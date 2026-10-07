#include "vm.h"
#include "opcodes.h"
#include "rms.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STACK_SIZE 256
#define MAX_VARS 256

VmSegment g_segments[256];
uint16_t g_num_segments = 0;

#define OVERLAY_SIZE 4096
uint8_t overlay_area[OVERLAY_SIZE];

void vm_init(void) {
    printf("VM Initialized.\\n");
}

int vm_run(uint16_t seg_idx) {
    if (seg_idx >= g_num_segments) {
        printf("Error: invalid segment index %d\\n", seg_idx);
        return 1;
    }
    
    const uint8_t* bytecode;
    size_t size;
    
    if (seg_idx == 0) {
        bytecode = g_segments[0].bytecode;
        size = g_segments[0].size;
    } else {
        printf("Loading overlay segment %d (%s) into overlay region at %p.\\n", seg_idx, g_segments[seg_idx].name, overlay_area);
        size = g_segments[seg_idx].size;
        if (size > OVERLAY_SIZE) size = OVERLAY_SIZE;
        memcpy(overlay_area, g_segments[seg_idx].bytecode, size);
        bytecode = overlay_area;
    }

    int32_t stack[STACK_SIZE];
    int sp = 0;
    static int32_t vars[MAX_VARS] = {0}; // Shared state across segments!
    
    size_t pc = 0;
    while (pc < size) {
        uint8_t op = bytecode[pc++];
        switch (op) {
            case OP_HALT:
                printf("VM Halt.\\n");
                return 0;
            case OP_RET:
                return 0;
            case OP_CALL_OVL: {
                uint16_t target_idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                vm_run(target_idx);
                break;
            }
            case OP_PUSH_I: {
                int32_t val = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                stack[sp++] = val;
                break;
            }
            case OP_PUSH_S: {
                int32_t idx = bytecode[pc] | (bytecode[pc+1] << 8);
                pc += 2;
                stack[sp++] = idx; // Pushing string index for now
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
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = a + b;
                break;
            }
            case OP_PRINT: {
                int32_t val = stack[--sp];
                printf("PRINT: %d\\n", val);
                break;
            }
            case OP_RMS_OPEN: {
                uint8_t channel = bytecode[pc++];
                uint8_t mode = bytecode[pc++];
                int var_idx = -1;
                if (mode == 2) { // Indexed
                    var_idx = bytecode[pc] | (bytecode[pc+1] << 8);
                    pc += 2;
                }
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
                if (has_key) {
                    var_idx = bytecode[pc] | (bytecode[pc+1] << 8);
                    pc += 2;
                }
                rms_get(channel, has_key, var_idx);
                break;
            }
            case OP_RMS_CLOS: {
                uint8_t channel = bytecode[pc++];
                rms_close(channel);
                break;
            }
            default:
                printf("Unknown opcode: %02x at pc=%zu\\n", op, pc-1);
                return 1;
        }
    }
    return 0;
}
