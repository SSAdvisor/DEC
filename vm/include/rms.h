#ifndef RMS_H
#define RMS_H

#include <stdint.h>

// RMS emulation layer for Sequential, Relative, and Indexed files.
void rms_init(void);
void rms_open(uint8_t channel, uint8_t mode, int key_var_idx);
void rms_put(uint8_t channel);
void rms_get(uint8_t channel, uint8_t has_key, int key_var_idx);
void rms_close(uint8_t channel);

#endif // RMS_H
