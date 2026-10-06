#include "rms.h"
#include <stdio.h>
#include <sqlite3.h>
#include <string.h>

#define MAX_CHANNELS 16

typedef struct {
    int active;
    uint8_t mode; // 0: SeqIn, 1: SeqOut, 2: Indexed
    FILE* file;
    sqlite3* db;
} RMSChannel;

static RMSChannel channels[MAX_CHANNELS];

void rms_init(void) {
    memset(channels, 0, sizeof(channels));
    printf("RMS initialized.\\n");
}

void rms_open(uint8_t channel, uint8_t mode, int key_var_idx) {
    if (channel >= MAX_CHANNELS) return;
    char filename[32];
    sprintf(filename, "chan%d.dat", channel);
    
    channels[channel].active = 1;
    channels[channel].mode = mode;
    
    if (mode == 0) { // Seq In
        channels[channel].file = fopen(filename, "r");
        printf("RMS OPEN (SEQ IN) channel %d\\n", channel);
    } else if (mode == 1) { // Seq Out
        channels[channel].file = fopen(filename, "w");
        printf("RMS OPEN (SEQ OUT) channel %d\\n", channel);
    } else if (mode == 2) { // Indexed
        sprintf(filename, "chan%d.db", channel);
        if (sqlite3_open(filename, &channels[channel].db) != SQLITE_OK) {
            printf("Failed to open SQLite DB for channel %d\\n", channel);
        } else {
            // Create a simple KV table for indexed access
            const char* sql = "CREATE TABLE IF NOT EXISTS records (key TEXT PRIMARY KEY, data TEXT);";
            sqlite3_exec(channels[channel].db, sql, 0, 0, 0);
            printf("RMS OPEN (INDEXED) channel %d with SQLite backend\\n", channel);
        }
    }
}

void rms_put(uint8_t channel) {
    if (channel >= MAX_CHANNELS || !channels[channel].active) return;
    
    if (channels[channel].mode == 1) {
        if (channels[channel].file) {
            fprintf(channels[channel].file, "Record\\n");
        }
        printf("RMS PUT (SEQ) channel %d\\n", channel);
    } else if (channels[channel].mode == 2) {
        // Insert into SQLite
        const char* sql = "INSERT OR REPLACE INTO records (key, data) VALUES ('dummy_key', 'dummy_data');";
        sqlite3_exec(channels[channel].db, sql, 0, 0, 0);
        printf("RMS PUT (INDEXED) channel %d to SQLite\\n", channel);
    }
}

void rms_get(uint8_t channel, uint8_t has_key, int key_var_idx) {
    if (channel >= MAX_CHANNELS || !channels[channel].active) return;
    
    if (channels[channel].mode == 0) {
        printf("RMS GET (SEQ) channel %d\\n", channel);
    } else if (channels[channel].mode == 2) {
        // Read from SQLite
        const char* sql = "SELECT data FROM records WHERE key = 'dummy_key';";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(channels[channel].db, sql, -1, &stmt, 0) == SQLITE_OK) {
            if (sqlite3_step(stmt) == SQLITE_ROW) {
                const unsigned char* text = sqlite3_column_text(stmt, 0);
                printf("RMS GET (INDEXED) channel %d: found '%s'\\n", channel, text);
            } else {
                printf("RMS GET (INDEXED) channel %d: not found\\n", channel);
            }
            sqlite3_finalize(stmt);
        }
    }
}

void rms_close(uint8_t channel) {
    if (channel >= MAX_CHANNELS || !channels[channel].active) return;
    
    if (channels[channel].mode == 0 || channels[channel].mode == 1) {
        if (channels[channel].file) fclose(channels[channel].file);
        printf("RMS CLOSE (SEQ) channel %d\\n", channel);
    } else if (channels[channel].mode == 2) {
        if (channels[channel].db) sqlite3_close(channels[channel].db);
        printf("RMS CLOSE (INDEXED) channel %d\\n", channel);
    }
    channels[channel].active = 0;
}
