#ifndef OPCODES_H
#define OPCODES_H

#include <stdint.h>

// VM Opcodes
typedef enum {
    OP_HALT      = 0x00,
    OP_NOP       = 0x01,
    
    OP_PUSH_I    = 0x10,
    OP_PUSH_F    = 0x11,
    OP_PUSH_S    = 0x12,
    OP_STORE_V   = 0x13,
    OP_LOAD_V    = 0x14,
    
    OP_ADD       = 0x20,
    OP_SUB       = 0x21,
    OP_MUL       = 0x22,
    OP_DIV       = 0x23,
    
    OP_JMP       = 0x30,
    OP_JMP_Z     = 0x31,
    
    OP_CALL      = 0x40,
    OP_RET       = 0x41,
    OP_CALL_OVL  = 0x42, // Overlay cross-call
    
    OP_PRINT     = 0x50,
    
    OP_RMS_OPEN  = 0x60,
    OP_RMS_GET   = 0x61,
    OP_RMS_PUT   = 0x62,
    OP_RMS_CLOS  = 0x63
} Opcode;

#endif // OPCODES_H
