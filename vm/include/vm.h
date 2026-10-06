#ifndef VM_H
#define VM_H

#include <stdint.h>
#include <stddef.h>

// Initialize the virtual machine
void vm_init(void);

// Run the VM on a loaded bytecode payload
int vm_run(const uint8_t* bytecode, size_t size);

#endif // VM_H
