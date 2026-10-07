#include "vm.h"
#include "opcodes.h"
#include "rms.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STACK_SIZE 256
#define MAX_VARS 256

typedef enum { VAL_INT, VAL_STR } ValType;
typedef struct {
    ValType type;
    union {
        int32_t i;
        char s[256];
    } v;
} Value;

VmSegment g_segments[256];
uint16_t g_num_segments = 0;

#define VM_MEM_SIZE 65536
uint8_t virtual_memory[VM_MEM_SIZE];

void vm_init(void) {
    printf("VM Initialized.\n");
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
    static Value vars[MAX_VARS]; // Shared state across segments!
    
    size_t pc = 0;
    while (pc < size) {
        uint8_t op = bytecode[pc++];
        switch (op) {
            case OP_HALT:
                return 0;
            case OP_RET:
                return 0;
            case OP_CALL_OVL: {
                uint16_t target_idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                vm_run(target_idx);
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
                if (val.type == VAL_INT && val.v.i == 0) pc = target;
                break;
            }
            case OP_PUSH_I: {
                int32_t val = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                stack[sp].type = VAL_INT;
                stack[sp++].v.i = val;
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
            case OP_ADD: {
                Value b = stack[--sp];
                Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                stack[sp++].v.i = a.v.i + b.v.i;
                break;
            }
            case OP_SUB: {
                Value b = stack[--sp];
                Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                stack[sp++].v.i = a.v.i - b.v.i;
                break;
            }
            case OP_EQ: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                if (a.type == VAL_INT) stack[sp++].v.i = (a.v.i == b.v.i) ? 1 : 0;
                else stack[sp++].v.i = (strcmp(a.v.s, b.v.s) == 0) ? 1 : 0;
                break;
            }
            case OP_NEQ: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                if (a.type == VAL_INT) stack[sp++].v.i = (a.v.i != b.v.i) ? 1 : 0;
                else stack[sp++].v.i = (strcmp(a.v.s, b.v.s) != 0) ? 1 : 0;
                break;
            }
            case OP_LT: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                stack[sp++].v.i = (a.v.i < b.v.i) ? 1 : 0;
                break;
            }
            case OP_GT: {
                Value b = stack[--sp]; Value a = stack[--sp];
                stack[sp].type = VAL_INT;
                stack[sp++].v.i = (a.v.i > b.v.i) ? 1 : 0;
                break;
            }
            case OP_PRINT: {
                Value val = stack[--sp];
                if (val.type == VAL_INT) printf("%d\n", val.v.i);
                else printf("%s\n", val.v.s);
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
                    buf[strcspn(buf, "\n")] = 0;
                    vars[idx].type = VAL_STR;
                    strcpy(vars[idx].v.s, buf);
                }
                break;
            }
            case OP_RMS_OPEN: {
                uint8_t channel = bytecode[pc++];
                uint8_t mode = bytecode[pc++];
                int var_idx = -1;
                if (mode == 2) { var_idx = bytecode[pc] | (bytecode[pc+1] << 8); pc += 2; }
                rms_open(channel, mode, var_idx);
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
                rms_get(channel, has_key, var_idx);
                break;
            }
            case OP_RMS_CLOS: {
                uint8_t channel = bytecode[pc++];
                rms_close(channel);
                break;
            }
            default:
                printf("Unknown opcode: %02x at pc=%zu\n", op, pc-1);
                return 1;
        }
    }
    return 0;
}
