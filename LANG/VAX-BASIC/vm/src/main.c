#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "vm.h"
#include "rms.h"
#include "runtime.h"

char g_command_line[1024] = {0};

int main(int argc, char **argv) {
    FILE *f = fopen("/proc/self/exe", "rb");
    if (!f) {
        perror("fopen /proc/self/exe");
        return 1;
    }

    fseek(f, -8, SEEK_END);
    char magic[4];
    uint32_t payload_size;

    if (fread(magic, 1, 4, f) != 4 || fread(&payload_size, 4, 1, f) != 1) {
        fprintf(stderr, "%%IMGACT-F-BADHDR, image header read error\n");
        fclose(f);
        return 1;
    }

    int has_header = 1;
    if (strncmp(magic, "VMSX", 4) != 0 && strncmp(magic, "RSTS", 4) != 0) {
        if (argc >= 2) {
            fclose(f);
            f = fopen(argv[1], "rb");
            if (!f) return 1;
            fseek(f, 0, SEEK_END);
            payload_size = ftell(f);
            fseek(f, 0, SEEK_SET);
            has_header = 0;
        } else {
            fprintf(stderr, "%%IMGACT-F-NOTNATIVE, no OpenVMS image payload found in executable\n");
            fclose(f);
            return 1;
        }
    } else {
        fseek(f, -((long)(8 + payload_size)), SEEK_END);
    }

    uint8_t *payload = malloc(payload_size);
    if (!payload) {
        fclose(f);
        return 1;
    }
    if (fread(payload, 1, payload_size, f) != payload_size) {
        free(payload);
        fclose(f);
        return 1;
    }
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

    const char *trace_env = getenv("VMS_VM_TRACE");
    int trace = (trace_env && strcmp(trace_env, "1") == 0);
    if (trace) {
        printf("OpenVMS VAX Image Activator V5.5-2 (ISD Segments: %u)\n", g_num_segments);
    }

    runtime_init();
    rms_init();
    vm_init();

    int start_arg = has_header ? 1 : 2;
    g_command_line[0] = '\0';
    for (int i = start_arg; i < argc; i++) {
        if (i > start_arg) strncat(g_command_line, " ", sizeof(g_command_line) - strlen(g_command_line) - 1);
        strncat(g_command_line, argv[i], sizeof(g_command_line) - strlen(g_command_line) - 1);
    }

    int rc = vm_run(0);
    free(payload);
    return rc;
}
