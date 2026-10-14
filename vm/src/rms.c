#include "rms.h"
#include "vm.h"
#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <string.h>
#include <unistd.h>

#define MAX_CHANNELS 16

typedef struct {
    int active;
    uint8_t mode; // 0: SeqIn, 1: SeqOut, 2: Indexed Read, 3: Indexed Write/Recreate
    FILE* file;
    sqlite3* db;
    sqlite3_stmt* cursor_stmt;
    int pk_idx;
    uint8_t num_vars;
    int mapped_vars[256];
} RMSChannel;

static RMSChannel channels[MAX_CHANNELS];

void rms_init(void) {
    memset(channels, 0, sizeof(channels));
}

void rms_open(uint8_t channel, const char* filename, uint8_t mode, int key_var_idx, uint8_t num_vars, int* mapped_vars) {
    if (channel >= MAX_CHANNELS) return;
    
    char actual_file[256];
    if (filename && strlen(filename) > 0) {
        strncpy(actual_file, filename, sizeof(actual_file) - 1);
        actual_file[sizeof(actual_file) - 1] = '\0';
    } else {
        snprintf(actual_file, sizeof(actual_file), "chan%d.dat", channel);
    }
    
    channels[channel].active = 1;
    channels[channel].mode = mode;
    channels[channel].pk_idx = key_var_idx;
    channels[channel].num_vars = num_vars;
    channels[channel].cursor_stmt = NULL;
    if (num_vars > 0 && mapped_vars != NULL) {
        memcpy(channels[channel].mapped_vars, mapped_vars, num_vars * sizeof(int));
    }
    
    if (mode == 0) { // Seq In
        channels[channel].file = fopen(actual_file, "r");
    } else if (mode == 1) { // Seq Out
        channels[channel].file = fopen(actual_file, "w");
    } else if (mode == 2 || mode == 3) { // Indexed
        if (mode == 3) {
            // Recreate / truncate for fresh output
            unlink(actual_file);
        }
        if (sqlite3_open(actual_file, &channels[channel].db) != SQLITE_OK) {
            printf("Failed to open SQLite DB '%s' for channel %d\n", actual_file, channel);
        } else {
            const char* sql = "CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE, data BLOB);";
            sqlite3_exec(channels[channel].db, sql, 0, 0, 0);
        }
    }
}

void rms_put(uint8_t channel) {
    if (channel >= MAX_CHANNELS || !channels[channel].active) return;
    
    if (channels[channel].mode == 1) {
        if (channels[channel].file) {
            fprintf(channels[channel].file, "Record\n");
        }
    } else if (channels[channel].mode == 2 || channels[channel].mode == 3) {
        // Serialize mapped variables into a buffer
        int buf_size = 0;
        for (int i = 0; i < channels[channel].num_vars; i++) {
            int vidx = channels[channel].mapped_vars[i];
            buf_size += sizeof(ValType);
            if (vars[vidx].type == VAL_STR) {
                buf_size += strlen(vars[vidx].v.s) + 1;
            } else if (vars[vidx].type == VAL_INT) {
                buf_size += sizeof(int32_t);
            } else if (vars[vidx].type == VAL_FLOAT) {
                buf_size += sizeof(float);
            }
        }
        
        unsigned char* buf = malloc(buf_size);
        int ptr = 0;
        for (int i = 0; i < channels[channel].num_vars; i++) {
            int vidx = channels[channel].mapped_vars[i];
            memcpy(buf + ptr, &vars[vidx].type, sizeof(ValType));
            ptr += sizeof(ValType);
            if (vars[vidx].type == VAL_STR) {
                int len = strlen(vars[vidx].v.s) + 1;
                memcpy(buf + ptr, vars[vidx].v.s, len);
                ptr += len;
            } else if (vars[vidx].type == VAL_INT) {
                memcpy(buf + ptr, &vars[vidx].v.i, sizeof(int32_t));
                ptr += sizeof(int32_t);
            } else if (vars[vidx].type == VAL_FLOAT) {
                memcpy(buf + ptr, &vars[vidx].v.f, sizeof(float));
                ptr += sizeof(float);
            }
        }
        
        int pk_idx = channels[channel].pk_idx;
        char* key_str = "dummy_key";
        char pk_buf[256];
        if (pk_idx >= 0 && vars[pk_idx].type == VAL_STR) {
            key_str = vars[pk_idx].v.s;
        } else if (pk_idx >= 0 && vars[pk_idx].type == VAL_INT) {
            snprintf(pk_buf, sizeof(pk_buf), "%d", vars[pk_idx].v.i);
            key_str = pk_buf;
        }
        
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(channels[channel].db, "INSERT OR REPLACE INTO records (key, data) VALUES (?, ?);", -1, &stmt, 0) == SQLITE_OK) {
            sqlite3_bind_text(stmt, 1, key_str, -1, SQLITE_STATIC);
            sqlite3_bind_blob(stmt, 2, buf, buf_size, SQLITE_STATIC);
            sqlite3_step(stmt);
            sqlite3_finalize(stmt);
        }
        free(buf);
    }
}

int rms_get(uint8_t channel, uint8_t has_key, int key_var_idx) {
    if (channel >= MAX_CHANNELS || !channels[channel].active) return -1;
    
    if (channels[channel].mode == 0) {
        return 0;
    } else if (channels[channel].mode == 2 || channels[channel].mode == 3) {
        if (!has_key) {
            // Sequential read
            if (!channels[channel].cursor_stmt) {
                const char* sql = "SELECT data FROM records ORDER BY id ASC;";
                if (sqlite3_prepare_v2(channels[channel].db, sql, -1, &channels[channel].cursor_stmt, 0) != SQLITE_OK) {
                    return 11; // Error / EOF
                }
            }
            int rc = sqlite3_step(channels[channel].cursor_stmt);
            if (rc == SQLITE_ROW) {
                const void* buf = sqlite3_column_blob(channels[channel].cursor_stmt, 0);
                int bytes = sqlite3_column_bytes(channels[channel].cursor_stmt, 0);
                
                int ptr = 0;
                for (int i = 0; i < channels[channel].num_vars && ptr < bytes; i++) {
                    int vidx = channels[channel].mapped_vars[i];
                    ValType t;
                    memcpy(&t, (const char*)buf + ptr, sizeof(ValType));
                    ptr += sizeof(ValType);
                    vars[vidx].type = t;
                    if (t == VAL_STR) {
                        strcpy(vars[vidx].v.s, (const char*)buf + ptr);
                        ptr += strlen(vars[vidx].v.s) + 1;
                    } else if (t == VAL_INT) {
                        memcpy(&vars[vidx].v.i, (const char*)buf + ptr, sizeof(int32_t));
                        ptr += sizeof(int32_t);
                    } else if (t == VAL_FLOAT) {
                        memcpy(&vars[vidx].v.f, (const char*)buf + ptr, sizeof(float));
                        ptr += sizeof(float);
                    }
                }
                return 0; // Success
            } else {
                // EOF reached
                sqlite3_finalize(channels[channel].cursor_stmt);
                channels[channel].cursor_stmt = NULL;
                return 11; // BASIC-PLUS-2 End of File error
            }
        } else {
            // Key search
            char* search_key = "dummy_key";
            char pk_buf[256];
            if (key_var_idx >= 0) {
                if (vars[key_var_idx].type == VAL_STR) search_key = vars[key_var_idx].v.s;
                else if (vars[key_var_idx].type == VAL_INT) {
                    snprintf(pk_buf, sizeof(pk_buf), "%d", vars[key_var_idx].v.i);
                    search_key = pk_buf;
                }
            }
            
            sqlite3_stmt* stmt;
            if (sqlite3_prepare_v2(channels[channel].db, "SELECT data FROM records ORDER BY id ASC;", -1, &stmt, 0) == SQLITE_OK) {
                int found = 0;
                while (sqlite3_step(stmt) == SQLITE_ROW) {
                    const void* buf = sqlite3_column_blob(stmt, 0);
                    int bytes = sqlite3_column_bytes(stmt, 0);
                    
                    int ptr = 0;
                    int matches = 0;
                    for (int i = 0; i < channels[channel].num_vars && ptr < bytes; i++) {
                        ValType t;
                        memcpy(&t, (const char*)buf + ptr, sizeof(ValType));
                        ptr += sizeof(ValType);
                        if (t == VAL_STR) {
                            const char* str_val = (const char*)buf + ptr;
                            if (strcmp(str_val, search_key) == 0) matches = 1;
                            ptr += strlen(str_val) + 1;
                        } else if (t == VAL_INT) {
                            int32_t i_val;
                            memcpy(&i_val, (const char*)buf + ptr, sizeof(int32_t));
                            char i_buf[256];
                            snprintf(i_buf, sizeof(i_buf), "%d", i_val);
                            if (strcmp(i_buf, search_key) == 0) matches = 1;
                            ptr += sizeof(int32_t);
                        } else if (t == VAL_FLOAT) {
                            ptr += sizeof(float);
                        }
                    }
                    
                    if (matches) {
                        found = 1;
                        ptr = 0;
                        for (int i = 0; i < channels[channel].num_vars && ptr < bytes; i++) {
                            int vidx = channels[channel].mapped_vars[i];
                            ValType t;
                            memcpy(&t, (const char*)buf + ptr, sizeof(ValType));
                            ptr += sizeof(ValType);
                            vars[vidx].type = t;
                            if (t == VAL_STR) {
                                strcpy(vars[vidx].v.s, (const char*)buf + ptr);
                                ptr += strlen(vars[vidx].v.s) + 1;
                            } else if (t == VAL_INT) {
                                memcpy(&vars[vidx].v.i, (const char*)buf + ptr, sizeof(int32_t));
                                ptr += sizeof(int32_t);
                            } else if (t == VAL_FLOAT) {
                                memcpy(&vars[vidx].v.f, (const char*)buf + ptr, sizeof(float));
                                ptr += sizeof(float);
                            }
                        }
                        break;
                    }
                }
                sqlite3_finalize(stmt);
                if (found) return 0;
                return 155; // Record Not Found error in BASIC-PLUS-2
            }
        }
    }
    return -1;
}

void rms_restore(uint8_t channel, int key_idx) {
    if (channel >= MAX_CHANNELS || !channels[channel].active) return;
    if (channels[channel].cursor_stmt) {
        sqlite3_finalize(channels[channel].cursor_stmt);
        channels[channel].cursor_stmt = NULL;
    }
}

void rms_close(uint8_t channel) {
    if (channel >= MAX_CHANNELS || !channels[channel].active) return;
    
    if (channels[channel].cursor_stmt) {
        sqlite3_finalize(channels[channel].cursor_stmt);
        channels[channel].cursor_stmt = NULL;
    }
    if (channels[channel].file) {
        fclose(channels[channel].file);
        channels[channel].file = NULL;
    }
    if (channels[channel].db) {
        sqlite3_close(channels[channel].db);
        channels[channel].db = NULL;
    }
    channels[channel].active = 0;
}

FILE* rms_get_channel_file(uint8_t channel) {
    if (channel > 0 && channel < MAX_CHANNELS && channels[channel].active && channels[channel].file) {
        return channels[channel].file;
    }
    return stdout;
}
