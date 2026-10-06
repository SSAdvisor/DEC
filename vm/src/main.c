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
    
    uint8_t *bytecode;
    uint32_t first_seg_size;
    uint16_t num_segments = 1;

    if (has_header) {
        // Now extract the root segment bytecode from the payload
        // Payload Format: [NUM_SEGMENTS (2)] | [NAME (16)] [SIZE (4)] ... | [DATA]
        num_segments = payload[0] | (payload[1] << 8);
        size_t header_size = 2 + (num_segments * 20);
        first_seg_size = payload[2+16] | (payload[2+16+1] << 8) | (payload[2+16+2] << 16) | (payload[2+16+3] << 24);
        bytecode = payload + header_size;
    } else {
        bytecode = payload;
        first_seg_size = payload_size;
    }

    printf("RSTS/E VM Init\\n");
    runtime_init();
    rms_init();
    vm_init();
    
    printf("--- Execution Start (Seg Size: %u, Segments: %u) ---\\n", first_seg_size, num_segments);
    vm_run(bytecode, first_seg_size);
    printf("--- Execution End ---\\n");
    
    free(payload);
    return 0;
}
