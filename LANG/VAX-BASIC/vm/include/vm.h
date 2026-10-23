#ifndef VM_H
#define VM_H

#include <stdint.h>
#include <stddef.h>

#define MAX_VARS 256

typedef enum { VAL_INT, VAL_FLOAT, VAL_STR, VAL_ARR } ValType;
typedef struct Value {
    ValType type;
    union {
        int32_t i;
        float f;
        char s[1024];
        struct Value* arr;
    } v;
    int32_t size; // Used for arrays
} Value;

extern Value vars[MAX_VARS];


typedef struct {
    char name[17];
    uint32_t size;
    uint32_t vaddr;
    const uint8_t* bytecode;
} VmSegment;

extern VmSegment g_segments[256];
extern uint16_t g_num_segments;

// Initialize the virtual machine
void vm_init(void);

// Run the VM on a loaded bytecode payload
int vm_run(uint16_t seg_idx);

extern char g_command_line[1024];

#endif // VM_H
