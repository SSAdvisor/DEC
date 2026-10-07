#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "vm.h"
#include "rms.h"
#include "runtime.h"

int main(int argc, char **argv) {
    // Read the payload from the end of the executable
    FILE *f = fopen("/proc/self/exe", "rb");
    if (!f) {
        perror("fopen /proc/self/exe");
        return 1;
    }
    
    // Read the last 8 bytes to check magic and size
    fseek(f, -8, SEEK_END);
    char magic[4];
    uint32_t payload_size;
    
    if (fread(magic, 1, 4, f) != 4 || fread(&payload_size, 4, 1, f) != 1) {
        printf("Failed to read footer.\\n");
        return 1;
    }
    
    int has_header = 1;
    if (strncmp(magic, "RSTS", 4) != 0) {
        // Fallback for direct testing: if argv[1] is provided, try loading it
        if (argc >= 2) {
            fclose(f);
            f = fopen(argv[1], "rb");
            if (!f) return 1;
            fseek(f, 0, SEEK_END);
            payload_size = ftell(f);
            fseek(f, 0, SEEK_SET);
            has_header = 0;
        } else {
            printf("Error: No valid bytecode payload found in executable, and no input file provided.\\n");
            return 1;
        }
    } else {
        // We found the payload. Seek to the start of the payload.
        fseek(f, -((long)(8 + payload_size)), SEEK_END);
    }
    
    uint8_t *payload = malloc(payload_size);
    fread(payload, 1, payload_size, f);
    fclose(f);
    
    if (has_header) {
        g_num_segments = payload[0] | (payload[1] << 8);
        size_t header_size = 2 + (g_num_segments * 24);
        size_t data_offset = header_size;
        
        for (int i = 0; i < g_num_segments; i++) {
            size_t entry_offset = 2 + (i * 24);
            memcpy(g_segments[i].name, &payload[entry_offset], 16);
            g_segments[i].name[16] = '\0';
            g_segments[i].size = payload[entry_offset+16] | (payload[entry_offset+17] << 8) | (payload[entry_offset+18] << 16) | (payload[entry_offset+19] << 24);
            g_segments[i].vaddr = payload[entry_offset+20] | (payload[entry_offset+21] << 8) | (payload[entry_offset+22] << 16) | (payload[entry_offset+23] << 24);
            g_segments[i].bytecode = payload + data_offset;
            data_offset += g_segments[i].size;
        }
    } else {
        g_num_segments = 1;
        strcpy(g_segments[0].name, "MAIN");
        g_segments[0].size = payload_size;
        g_segments[0].vaddr = 0;
        g_segments[0].bytecode = payload;
    }

    printf("RSTS/E VM Init\\n");
    runtime_init();
    rms_init();
    vm_init();
    
    printf("--- Execution Start (Segments: %u) ---\\n", g_num_segments);
    vm_run(0); // Start MAIN
    printf("--- Execution End ---\\n");
    
    free(payload);
    return 0;
}
