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
    OP_DIM       = 0x15,
    OP_STORE_A   = 0x16,
    OP_LOAD_A    = 0x17,
    
    OP_ADD       = 0x20,
    OP_SUB       = 0x21,
    OP_MUL       = 0x22,
    OP_DIV       = 0x23,
    OP_EQ        = 0x24,
    OP_NEQ       = 0x25,
    OP_LT        = 0x26,
    OP_GT        = 0x27,
    
    OP_JMP       = 0x30,
    OP_JMP_Z     = 0x31,
    
    OP_CALL      = 0x40,
    OP_RET       = 0x41,
    OP_CALL_OVL  = 0x42, // Overlay cross-call
    
    OP_PRINT     = 0x50,
    OP_PRINT_NO_NL = 0x51,
    
    OP_RMS_OPEN  = 0x60,
    OP_RMS_GET   = 0x61,
    OP_RMS_PUT   = 0x62,
    OP_RMS_CLOS  = 0x63,
    
    OP_INPUT_I   = 0x70,
    OP_INPUT_S   = 0x71,
    OP_GETCH     = 0x72,
    OP_CHR       = 0x73
} Opcode;

#endif // OPCODES_H
