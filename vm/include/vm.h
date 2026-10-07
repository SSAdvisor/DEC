#ifndef VM_H
#define VM_H

#include <stdint.h>
#include <stddef.h>

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

#endif // VM_H
