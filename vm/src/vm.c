#include "vm.h"
#include "opcodes.h"
#include "rms.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <termios.h>
#include <unistd.h>

#define STACK_SIZE 256
#define MAX_VARS 256
#define MAX_DATA_POOL 1024

VmSegment g_segments[256];
uint16_t g_num_segments = 0;

#define VM_MEM_SIZE 65536
uint8_t virtual_memory[VM_MEM_SIZE];

Value vars[MAX_VARS]; // Global vars for save/load

static Value g_data_pool[MAX_DATA_POOL];
static int g_data_count = 0;
static int g_data_ptr = 0;

static int g_error_handler_pc = -1;
static int g_err_var_idx = -1;

void save_state(void) {
    FILE* f = fopen("db.bin", "wb"); 
    if (!f) return;
    for (int i = 0; i < MAX_VARS; i++) {
        fwrite(&vars[i].type, sizeof(ValType), 1, f);
        if (vars[i].type == VAL_ARR) {
            fwrite(&vars[i].size, sizeof(int32_t), 1, f);
            for (int j = 0; j < vars[i].size; j++) {
                fwrite(&vars[i].v.arr[j].type, sizeof(ValType), 1, f);
                if (vars[i].v.arr[j].type == VAL_INT) fwrite(&vars[i].v.arr[j].v.i, sizeof(int32_t), 1, f);
                else fwrite(vars[i].v.arr[j].v.s, 256, 1, f);
            }
        } else if (vars[i].type == VAL_INT) {
            fwrite(&vars[i].v.i, sizeof(int32_t), 1, f);
        } else if (vars[i].type == VAL_FLOAT) {
            fwrite(&vars[i].v.f, sizeof(float), 1, f);
        } else {
            fwrite(vars[i].v.s, 256, 1, f);
        }
    }
    fclose(f);
}

void load_state(void) {
    FILE* f = fopen("db.bin", "rb");
    if (!f) return;
    for (int i = 0; i < MAX_VARS; i++) {
        fread(&vars[i].type, sizeof(ValType), 1, f);
        if (vars[i].type == VAL_ARR) {
            fread(&vars[i].size, sizeof(int32_t), 1, f);
            vars[i].v.arr = (Value*)calloc(vars[i].size, sizeof(Value));
            for (int j = 0; j < vars[i].size; j++) {
                fread(&vars[i].v.arr[j].type, sizeof(ValType), 1, f);
                if (vars[i].v.arr[j].type == VAL_INT) fread(&vars[i].v.arr[j].v.i, sizeof(int32_t), 1, f);
                else fread(vars[i].v.arr[j].v.s, 256, 1, f);
            }
        } else if (vars[i].type == VAL_INT) {
            fread(&vars[i].v.i, sizeof(int32_t), 1, f);
        } else if (vars[i].type == VAL_FLOAT) {
            fread(&vars[i].v.f, sizeof(float), 1, f);
        } else {
            fread(vars[i].v.s, 256, 1, f);
        }
    }
    fclose(f);
}

static void format_using(FILE* out, const char* fmt, int num_args, Value* args) {
    int arg_idx = 0;
    int len = strlen(fmt);
    int i = 0;
    while (i < len) {
        if (fmt[i] == '\\') {
            // String field with backslashes
            int j = i + 1;
            while (j < len && fmt[j] != '\\') j++;
            if (j < len && fmt[j] == '\\') {
                int field_width = j - i + 1;
                const char* s_val = "";
                if (arg_idx < num_args) {
                    s_val = (args[arg_idx].type == VAL_STR) ? args[arg_idx].v.s : "";
                    arg_idx++;
                }
                int s_len = strlen(s_val);
                for (int k = 0; k < field_width; k++) {
                    if (k < s_len) fputc(s_val[k], out);
                    else fputc(' ', out);
                }
                i = j + 1;
                continue;
            }
        }
        if (fmt[i] == '$' && i + 1 < len && fmt[i+1] == '$') {
            // Floating dollar field: $$#####.##
            int j = i;
            while (j < len && (fmt[j] == '$' || fmt[j] == '#' || fmt[j] == ',')) j++;
            int decimals = 0;
            if (j < len && fmt[j] == '.') {
                j++;
                while (j < len && fmt[j] == '#') { decimals++; j++; }
            }
            int field_width = j - i;
            double val = 0.0;
            if (arg_idx < num_args) {
                if (args[arg_idx].type == VAL_FLOAT) val = args[arg_idx].v.f;
                else if (args[arg_idx].type == VAL_INT) val = args[arg_idx].v.i;
                arg_idx++;
            }
            char num_buf[64];
            snprintf(num_buf, sizeof(num_buf), "$%.*f", decimals, val);
            int num_len = strlen(num_buf);
            for (int k = 0; k < field_width - num_len; k++) fputc(' ', out);
            fputs(num_buf, out);
            i = j;
            continue;
        }
        if (fmt[i] == '#') {
            // Numeric field: #### or ####.##
            int j = i;
            while (j < len && (fmt[j] == '#' || fmt[j] == ',')) j++;
            int decimals = -1;
            if (j < len && fmt[j] == '.') {
                decimals = 0;
                j++;
                while (j < len && fmt[j] == '#') { decimals++; j++; }
            }
            int field_width = j - i;
            double val = 0.0;
            if (arg_idx < num_args) {
                if (args[arg_idx].type == VAL_FLOAT) val = args[arg_idx].v.f;
                else if (args[arg_idx].type == VAL_INT) val = args[arg_idx].v.i;
                arg_idx++;
            }
            char num_buf[64];
            if (decimals >= 0) snprintf(num_buf, sizeof(num_buf), "%.*f", decimals, val);
            else snprintf(num_buf, sizeof(num_buf), "%ld", (long)round(val));
            int num_len = strlen(num_buf);
            for (int k = 0; k < field_width - num_len; k++) fputc(' ', out);
            fputs(num_buf, out);
            i = j;
            continue;
        }
        fputc(fmt[i], out);
        i++;
    }
    fputc('\n', out);
    fflush(out);
}

void vm_init(void) {
    g_data_ptr = 0;
    g_data_count = 0;
    g_error_handler_pc = -1;
    g_err_var_idx = -1;
    memset(vars, 0, sizeof(vars));
}

int vm_run(uint16_t seg_idx) {
    if (seg_idx >= g_num_segments) {
        printf("Error: invalid segment index %d\n", seg_idx);
        return 1;
    }
    
    uint32_t vaddr = g_segments[seg_idx].vaddr;
    size_t size = g_segments[seg_idx].size;
    
    if (vaddr + size > VM_MEM_SIZE) {
        printf("Error: Segment %s exceeds virtual memory!\n", g_segments[seg_idx].name);
        return 1;
    }
    
    memcpy(&virtual_memory[vaddr], g_segments[seg_idx].bytecode, size);
    const uint8_t* bytecode = &virtual_memory[vaddr];

    Value stack[STACK_SIZE];
    int sp = 0;
    size_t call_stack[256];
    int call_sp = 0;
    
    size_t pc = 0;
    while (pc < size) {
        uint8_t op = bytecode[pc++];
        switch (op) {
            case OP_HALT:
                return 0;
            case OP_CALL: {
                uint16_t target = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                if (call_sp < 256) {
                    call_stack[call_sp++] = pc;
                }
                pc = target;
                break;
            }
            case OP_RET: {
                if (call_sp > 0) {
                    pc = call_stack[--call_sp];
                } else {
                    return 0;
                }
                break;
            }
            case OP_CALL_OVL: {
                uint16_t target_idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                if (target_idx == 0x9998) {
                    save_state();
                } else if (target_idx == 0x9999) {
                    load_state();
                } else {
                    vm_run(target_idx);
                }
                break;
            }
            case OP_JMP: {
                uint16_t target = bytecode[pc] | (bytecode[pc+1] << 8);
                pc = target;
                break;
            }
            case OP_JMP_Z: {
                uint16_t target = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                Value val = stack[--sp];
                if ((val.type == VAL_INT && val.v.i == 0) || (val.type == VAL_FLOAT && val.v.f == 0.0f)) {
                    pc = target;
                }
                break;
            }
            case OP_PUSH_I: {
                int16_t val = (int16_t)(bytecode[pc] | (bytecode[pc+1] << 8));
                pc += 2;
                stack[sp].type = VAL_INT;
                stack[sp++].v.i = val;
                break;
            }
            case OP_PUSH_F: {
                float val;
                memcpy(&val, &bytecode[pc], sizeof(float));
                pc += sizeof(float);
                stack[sp].type = VAL_FLOAT;
                stack[sp++].v.f = val;
                break;
            }
            case OP_PUSH_S: {
                uint8_t len = bytecode[pc++];
                stack[sp].type = VAL_STR;
                memcpy(stack[sp].v.s, &bytecode[pc], len);
                stack[sp].v.s[len] = '\0';
                pc += len;
                sp++;
                break;
            }
            case OP_STORE_V: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                vars[idx] = stack[--sp];
                break;
            }
            case OP_LOAD_V: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                stack[sp++] = vars[idx];
                break;
            }
            case OP_DIM: { 
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                Value size_val = stack[--sp];
                int32_t arr_sz = (size_val.type == VAL_INT ? size_val.v.i : (int32_t)size_val.v.f) + 1;
                vars[idx].type = VAL_ARR;
                vars[idx].size = arr_sz;
                vars[idx].v.arr = (Value*)calloc(arr_sz, sizeof(Value));
                for(int i = 0; i < arr_sz; i++) {
                    vars[idx].v.arr[i].type = VAL_INT;
                    vars[idx].v.arr[i].v.i = 0;
                }
                break;
            }
            case OP_STORE_A: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                Value arr_idx = stack[--sp];
                Value val = stack[--sp];
                int32_t a_idx = (arr_idx.type == VAL_INT ? arr_idx.v.i : (int32_t)arr_idx.v.f);
                if (vars[idx].type == VAL_ARR && a_idx >= 0 && a_idx < vars[idx].size) {
                    vars[idx].v.arr[a_idx] = val;
                }
                break;
            }
            case OP_LOAD_A: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                Value arr_idx = stack[--sp];
                int32_t a_idx = (arr_idx.type == VAL_INT ? arr_idx.v.i : (int32_t)arr_idx.v.f);
                if (vars[idx].type == VAL_ARR && a_idx >= 0 && a_idx < vars[idx].size) {
                    stack[sp++] = vars[idx].v.arr[a_idx];
                } else {
                    stack[sp].type = VAL_INT;
                    stack[sp++].v.i = 0;
                }
                break;
            }
            case OP_ADD: {
                Value b = stack[--sp];
                Value a = stack[--sp];
                if (a.type == VAL_STR || b.type == VAL_STR) {
                    char str_a[256];
                    char str_b[256];
                    if (a.type == VAL_STR) strncpy(str_a, a.v.s, 255);
                    else if (a.type == VAL_INT) snprintf(str_a, sizeof(str_a), "%d", a.v.i);
                    else snprintf(str_a, sizeof(str_a), "%g", a.v.f);
                    str_a[255] = '\0';

                    if (b.type == VAL_STR) strncpy(str_b, b.v.s, 255);
                    else if (b.type == VAL_INT) snprintf(str_b, sizeof(str_b), "%d", b.v.i);
                    else snprintf(str_b, sizeof(str_b), "%g", b.v.f);
                    str_b[255] = '\0';

                    stack[sp].type = VAL_STR;
                    snprintf(stack[sp].v.s, sizeof(stack[sp].v.s), "%s%s", str_a, str_b);
                    sp++;
                } else if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                    float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                    stack[sp].type = VAL_FLOAT;
                    stack[sp++].v.f = fa + fb;
                } else {
                    stack[sp].type = VAL_INT;
                    stack[sp++].v.i = a.v.i + b.v.i;
                }
                break;
            }
            case OP_SUB: {
                Value b = stack[--sp];
                Value a = stack[--sp];
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                    float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                    stack[sp].type = VAL_FLOAT;
                    stack[sp++].v.f = fa - fb;
                } else {
                    stack[sp].type = VAL_INT;
                    stack[sp++].v.i = a.v.i - b.v.i;
                }
                break;
            }
            case OP_MUL: { 
                Value b = stack[--sp];
                Value a = stack[--sp];
                float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    stack[sp].type = VAL_FLOAT;
                    stack[sp++].v.f = fa * fb;
                } else {
                    stack[sp].type = VAL_INT;
                    stack[sp++].v.i = a.v.i * b.v.i;
                }
                break;
            }
            case OP_DIV: {
                Value b = stack[--sp];
                Value a = stack[--sp];
                float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                stack[sp].type = VAL_FLOAT;
                stack[sp++].v.f = (fb != 0.0f) ? (fa / fb) : 0.0f;
                break;
            }
            case OP_RND: { 
                stack[sp].type = VAL_FLOAT;
                stack[sp++].v.f = (float)rand() / (float)RAND_MAX;
                break;
            }
            case OP_INT: { 
                Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                stack[sp++].v.i = (int32_t)((a.type == VAL_FLOAT) ? floorf(a.v.f) : a.v.i);
                break;
            }
            case OP_EQ: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                    float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                    stack[sp++].v.i = (fa == fb) ? 1 : 0;
                } else if (a.type == VAL_INT && b.type == VAL_INT) {
                    stack[sp++].v.i = (a.v.i == b.v.i) ? 1 : 0;
                } else {
                    stack[sp++].v.i = (strcmp(a.v.s, b.v.s) == 0) ? 1 : 0;
                }
                break;
            }
            case OP_NEQ: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                    float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                    stack[sp++].v.i = (fa != fb) ? 1 : 0;
                } else if (a.type == VAL_INT && b.type == VAL_INT) {
                    stack[sp++].v.i = (a.v.i != b.v.i) ? 1 : 0;
                } else {
                    stack[sp++].v.i = (strcmp(a.v.s, b.v.s) != 0) ? 1 : 0;
                }
                break;
            }
            case OP_LT: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                    float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                    stack[sp++].v.i = (fa < fb) ? 1 : 0;
                } else if (a.type == VAL_INT && b.type == VAL_INT) {
                    stack[sp++].v.i = (a.v.i < b.v.i) ? 1 : 0;
                } else {
                    stack[sp++].v.i = (strcmp(a.v.s, b.v.s) < 0) ? 1 : 0;
                }
                break;
            }
            case OP_GT: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    float fa = (a.type == VAL_FLOAT) ? a.v.f : a.v.i;
                    float fb = (b.type == VAL_FLOAT) ? b.v.f : b.v.i;
                    stack[sp++].v.i = (fa > fb) ? 1 : 0;
                } else if (a.type == VAL_INT && b.type == VAL_INT) {
                    stack[sp++].v.i = (a.v.i > b.v.i) ? 1 : 0;
                } else {
                    stack[sp++].v.i = (strcmp(a.v.s, b.v.s) > 0) ? 1 : 0;
                }
                break;
            }
            case OP_AND: {
                Value b = stack[--sp]; Value a = stack[--sp];
                int ia = (a.type == VAL_INT) ? a.v.i : (a.type == VAL_FLOAT ? (int)a.v.f : (strlen(a.v.s) > 0));
                int ib = (b.type == VAL_INT) ? b.v.i : (b.type == VAL_FLOAT ? (int)b.v.f : (strlen(b.v.s) > 0));
                stack[sp].type = VAL_INT;
                if (a.type == VAL_INT && b.type == VAL_INT) {
                    stack[sp++].v.i = (ia & ib);
                } else {
                    stack[sp++].v.i = (ia && ib) ? 1 : 0;
                }
                break;
            }
            case OP_OR: {
                Value b = stack[--sp]; Value a = stack[--sp];
                int ia = (a.type == VAL_INT) ? a.v.i : (a.type == VAL_FLOAT ? (int)a.v.f : (strlen(a.v.s) > 0));
                int ib = (b.type == VAL_INT) ? b.v.i : (b.type == VAL_FLOAT ? (int)b.v.f : (strlen(b.v.s) > 0));
                stack[sp].type = VAL_INT;
                if (a.type == VAL_INT && b.type == VAL_INT) {
                    stack[sp++].v.i = (ia | ib);
                } else {
                    stack[sp++].v.i = (ia || ib) ? 1 : 0;
                }
                break;
            }
            case OP_PRINT: {
                Value val = stack[--sp];
                if (val.type == VAL_INT) printf("%d\n", val.v.i);
                else if (val.type == VAL_FLOAT) printf("%g\n", val.v.f);
                else printf("%s\n", val.v.s);
                fflush(stdout);
                break;
            }
            case OP_PRINT_NO_NL: {
                Value val = stack[--sp];
                if (val.type == VAL_INT) printf("%d", val.v.i);
                else if (val.type == VAL_FLOAT) printf("%g", val.v.f);
                else printf("%s", val.v.s);
                fflush(stdout);
                break;
            }
            case OP_PRINT_CH: {
                uint8_t ch = bytecode[pc++];
                uint8_t nl = bytecode[pc++];
                FILE* out = rms_get_channel_file(ch);
                Value val = stack[--sp];
                if (val.type == VAL_INT) fprintf(out, "%d", val.v.i);
                else if (val.type == VAL_FLOAT) fprintf(out, "%g", val.v.f);
                else fprintf(out, "%s", val.v.s);
                if (nl) fprintf(out, "\n");
                fflush(out);
                break;
            }
            case OP_PRINT_USING: {
                uint8_t ch = bytecode[pc++];
                uint8_t num_args = bytecode[pc++];
                FILE* out = rms_get_channel_file(ch);
                Value args[32];
                for (int a = num_args - 1; a >= 0; a--) {
                    args[a] = stack[--sp];
                }
                Value fmt_val = stack[--sp];
                const char* fmt = (fmt_val.type == VAL_STR) ? fmt_val.v.s : "";
                format_using(out, fmt, num_args, args);
                break;
            }
            case OP_INPUT_I: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                int temp;
                if (scanf("%d", &temp) != 1) temp = 0;
                while(getchar() != '\n');
                vars[idx].type = VAL_INT;
                vars[idx].v.i = temp;
                break;
            }
            case OP_INPUT_S: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                char buf[256];
                if (fgets(buf, 256, stdin)) {
                    buf[strcspn(buf, "\r\n")] = 0;
                    vars[idx].type = VAL_STR;
                    strncpy(vars[idx].v.s, buf, 255);
                    vars[idx].v.s[255] = '\0';
                } else {
                    vars[idx].type = VAL_STR;
                    if (feof(stdin)) {
                        vars[idx].v.s[0] = 26; // Ctrl-Z on EOF
                        vars[idx].v.s[1] = '\0';
                    } else {
                        vars[idx].v.s[0] = '\0';
                    }
                }
                break;
            }
            case OP_RMS_OPEN: {
                uint8_t channel = bytecode[pc++];
                uint8_t mode = bytecode[pc++];
                int pk_idx = -1;
                if (mode == 2 || mode == 3) {
                    pk_idx = bytecode[pc] | (bytecode[pc+1] << 8);
                    pc += 2;
                }
                
                uint8_t num_vars = bytecode[pc++];
                int mapped_vars[256];
                for(int i = 0; i < num_vars; i++) {
                    mapped_vars[i] = bytecode[pc] | (bytecode[pc+1] << 8);
                    pc += 2;
                }
                
                Value filename_val = stack[--sp];
                const char* filename = (filename_val.type == VAL_STR) ? filename_val.v.s : "";
                rms_open(channel, filename, mode, pk_idx, num_vars, mapped_vars);
                if (mode == 0 && rms_get_channel_file(channel) == NULL) {
                    if (g_error_handler_pc >= 0) {
                        if (g_err_var_idx >= 0) {
                            vars[g_err_var_idx].type = VAL_INT;
                            vars[g_err_var_idx].v.i = 5; // File Not Found
                        }
                        pc = g_error_handler_pc;
                    }
                }
                break;
            }
            case OP_RMS_PUT: {
                uint8_t channel = bytecode[pc++];
                rms_put(channel);
                break;
            }
            case OP_RMS_GET: {
                uint8_t channel = bytecode[pc++];
                uint8_t has_key = bytecode[pc++];
                int var_idx = -1;
                if (has_key) { var_idx = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2; }
                int rc = rms_get(channel, has_key, var_idx);
                if (rc != 0) {
                    if (g_error_handler_pc >= 0) {
                        if (g_err_var_idx >= 0) {
                            vars[g_err_var_idx].type = VAL_INT;
                            vars[g_err_var_idx].v.i = rc;
                        }
                        pc = g_error_handler_pc;
                    } else {
                        printf("Unhandled RMS error %d\n", rc);
                        return rc;
                    }
                }
                break;
            }
            case OP_RMS_CLOS: {
                uint8_t channel = bytecode[pc++];
                rms_close(channel);
                break;
            }
            case OP_RMS_REST: {
                uint8_t channel = bytecode[pc++];
                uint8_t key_idx = bytecode[pc++];
                rms_restore(channel, key_idx);
                break;
            }
            case OP_GETCH: {
                struct termios oldt, newt;
                tcgetattr(STDIN_FILENO, &oldt);
                newt = oldt;
                newt.c_lflag &= ~(ICANON | ECHO);
                tcsetattr(STDIN_FILENO, TCSANOW, &newt);
                
                char ch;
                if (read(STDIN_FILENO, &ch, 1) != 1) {
                    ch = 0;
                }
                tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
                
                stack[sp].type = VAL_STR;
                if (ch != 0) {
                    stack[sp].v.s[0] = ch;
                    stack[sp].v.s[1] = '\0';
                } else {
                    stack[sp].v.s[0] = '\0';
                }
                sp++;
                break;
            }
            case OP_CHR: {
                Value val = stack[--sp];
                stack[sp].type = VAL_STR;
                stack[sp].v.s[0] = (char)(val.v.i & 0xFF);
                stack[sp].v.s[1] = '\0';
                sp++;
                break;
            }
            case OP_INIT_DATA: {
                uint16_t count = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                g_data_count = count;
                g_data_ptr = 0;
                for (int d = 0; d < count; d++) {
                    uint8_t dtype = bytecode[pc++];
                    if (dtype == 0) { // INT
                        int32_t ival;
                        memcpy(&ival, &bytecode[pc], 4); pc += 4;
                        g_data_pool[d].type = VAL_INT;
                        g_data_pool[d].v.i = ival;
                    } else if (dtype == 1) { // FLOAT
                        float fval;
                        memcpy(&fval, &bytecode[pc], 4); pc += 4;
                        g_data_pool[d].type = VAL_FLOAT;
                        g_data_pool[d].v.f = fval;
                    } else if (dtype == 2) { // STR
                        uint8_t slen = bytecode[pc++];
                        g_data_pool[d].type = VAL_STR;
                        memcpy(g_data_pool[d].v.s, &bytecode[pc], slen);
                        g_data_pool[d].v.s[slen] = '\0';
                        pc += slen;
                    }
                }
                break;
            }
            case OP_READ: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                if (g_data_ptr < g_data_count) {
                    vars[idx] = g_data_pool[g_data_ptr++];
                }
                break;
            }
            case OP_ON_ERROR: {
                uint16_t target = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                uint16_t err_idx = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                g_error_handler_pc = (target == 0) ? -1 : target;
                g_err_var_idx = err_idx;
                break;
            }
            case OP_RESUME: {
                uint16_t target = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                pc = target;
                break;
            }
            case OP_DATE_STR: {
                Value arg = stack[--sp];
                (void)arg;
                time_t t = time(NULL);
                struct tm *tm = localtime(&t);
                char dstr[32];
                strftime(dstr, sizeof(dstr), "%d-%b-%y", tm);
                stack[sp].type = VAL_STR;
                strncpy(stack[sp].v.s, dstr, 255);
                stack[sp].v.s[255] = '\0';
                sp++;
                break;
            }
            case OP_INPUT_LINE_CH: {
                uint8_t ch = bytecode[pc++];
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2;
                FILE* in = rms_get_channel_file(ch);
                char buf[1024];
                if (in && fgets(buf, sizeof(buf), in)) {
                    buf[strcspn(buf, "\r\n")] = 0;
                    vars[idx].type = VAL_STR;
                    strncpy(vars[idx].v.s, buf, 255);
                    vars[idx].v.s[255] = '\0';
                } else {
                    vars[idx].type = VAL_STR;
                    vars[idx].v.s[0] = '\0';
                    if (g_error_handler_pc >= 0) {
                        if (g_err_var_idx >= 0) {
                            vars[g_err_var_idx].type = VAL_INT;
                            vars[g_err_var_idx].v.i = 11; // EOF
                        }
                        pc = g_error_handler_pc;
                    }
                }
                break;
            }
            case OP_LEN: {
                Value val = stack[--sp];
                int len = (val.type == VAL_STR) ? (int)strlen(val.v.s) : 0;
                stack[sp].type = VAL_INT;
                stack[sp].v.i = len;
                sp++;
                break;
            }
            case OP_MID: {
                Value len_v = stack[--sp];
                Value start_v = stack[--sp];
                Value str_v = stack[--sp];
                int start = (start_v.type == VAL_INT) ? start_v.v.i : (int)start_v.v.f;
                int len = (len_v.type == VAL_INT) ? len_v.v.i : (int)len_v.v.f;
                const char* s = (str_v.type == VAL_STR) ? str_v.v.s : "";
                int slen = (int)strlen(s);
                char res[256] = "";
                if (start >= 1 && start <= slen && len > 0) {
                    int copy_len = len;
                    if (start - 1 + copy_len > slen) copy_len = slen - (start - 1);
                    if (copy_len > 255) copy_len = 255;
                    strncpy(res, s + start - 1, copy_len);
                    res[copy_len] = '\0';
                }
                stack[sp].type = VAL_STR;
                strncpy(stack[sp].v.s, res, 255);
                stack[sp].v.s[255] = '\0';
                sp++;
                break;
            }
            case OP_LEFT: {
                Value len_v = stack[--sp];
                Value str_v = stack[--sp];
                int len = (len_v.type == VAL_INT) ? len_v.v.i : (int)len_v.v.f;
                const char* s = (str_v.type == VAL_STR) ? str_v.v.s : "";
                int slen = (int)strlen(s);
                char res[256] = "";
                if (len > 0) {
                    if (len > slen) len = slen;
                    if (len > 255) len = 255;
                    strncpy(res, s, len);
                    res[len] = '\0';
                }
                stack[sp].type = VAL_STR;
                strncpy(stack[sp].v.s, res, 255);
                stack[sp].v.s[255] = '\0';
                sp++;
                break;
            }
            case OP_RIGHT: {
                Value pos_v = stack[--sp];
                Value str_v = stack[--sp];
                int pos = (pos_v.type == VAL_INT) ? pos_v.v.i : (int)pos_v.v.f;
                const char* s = (str_v.type == VAL_STR) ? str_v.v.s : "";
                int slen = (int)strlen(s);
                char res[256] = "";
                if (pos >= 1 && pos <= slen) {
                    strncpy(res, s + pos - 1, 255);
                    res[255] = '\0';
                }
                stack[sp].type = VAL_STR;
                strncpy(stack[sp].v.s, res, 255);
                stack[sp].v.s[255] = '\0';
                sp++;
                break;
            }
            case OP_INSTR: {
                Value target_v = stack[--sp];
                Value str_v = stack[--sp];
                Value start_v = stack[--sp];
                int start = (start_v.type == VAL_INT) ? start_v.v.i : (int)start_v.v.f;
                const char* s = (str_v.type == VAL_STR) ? str_v.v.s : "";
                const char* t = (target_v.type == VAL_STR) ? target_v.v.s : "";
                int slen = (int)strlen(s);
                int found_idx = 0;
                if (start >= 1 && start <= slen && strlen(t) > 0) {
                    const char* p = strstr(s + start - 1, t);
                    if (p) {
                        found_idx = (int)(p - s) + 1;
                    }
                }
                stack[sp].type = VAL_INT;
                stack[sp].v.i = found_idx;
                sp++;
                break;
            }
            case OP_VAL: {
                Value str_v = stack[--sp];
                const char* s = (str_v.type == VAL_STR) ? str_v.v.s : "";
                float val = (float)atof(s);
                if (strchr(s, '.') == NULL) {
                    stack[sp].type = VAL_INT;
                    stack[sp].v.i = (int)val;
                } else {
                    stack[sp].type = VAL_FLOAT;
                    stack[sp].v.f = val;
                }
                sp++;
                break;
            }
            case OP_STR: {
                Value val = stack[--sp];
                char res[64];
                if (val.type == VAL_INT) snprintf(res, sizeof(res), "%d", val.v.i);
                else if (val.type == VAL_FLOAT) snprintf(res, sizeof(res), "%g", val.v.f);
                else strncpy(res, val.v.s, 63);
                stack[sp].type = VAL_STR;
                strncpy(stack[sp].v.s, res, 255);
                stack[sp].v.s[255] = '\0';
                sp++;
                break;
            }
            case OP_ASCII: {
                Value str_v = stack[--sp];
                const char* s = (str_v.type == VAL_STR) ? str_v.v.s : "";
                int code = (s[0] != '\0') ? (unsigned char)s[0] : 0;
                stack[sp].type = VAL_INT;
                stack[sp].v.i = code;
                sp++;
                break;
            }
            case OP_SYS: {
                Value cmd_v = stack[--sp];
                const char* cmd = (cmd_v.type == VAL_STR) ? cmd_v.v.s : "";
                int rc = 0;
                if (strncasecmp(cmd, "cd ", 3) == 0) {
                    const char* dir = cmd + 3;
                    while (*dir == ' ') dir++;
                    rc = chdir(dir);
                } else {
                    rc = system(cmd);
                }
                stack[sp].type = VAL_INT;
                stack[sp].v.i = (rc == 0) ? 0 : ((rc >> 8) & 0xFF);
                sp++;
                break;
            }
            case OP_COMMAND_STR: {
                stack[sp].type = VAL_STR;
                strncpy(stack[sp].v.s, g_command_line, 255);
                stack[sp].v.s[255] = '\0';
                sp++;
                break;
            }
            case OP_TIME_STR: {
                Value arg = stack[--sp];
                (void)arg;
                time_t t = time(NULL);
                struct tm *tm = localtime(&t);
                char tstr[32];
                strftime(tstr, sizeof(tstr), "%H:%M:%S", tm);
                stack[sp].type = VAL_STR;
                strncpy(stack[sp].v.s, tstr, 255);
                stack[sp].v.s[255] = '\0';
                sp++;
                break;
            }
            default:
                printf("Unknown opcode: %02x at pc=%zu\n", op, pc-1);
                return 1;
        }
    }
    return 0;
}
