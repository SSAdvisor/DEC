#ifndef DECW_X11_H
#define DECW_X11_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DECW_X11_VERSION "DECwindows X11/Motif 1.1 Interfacing Library V3.0"
#define DECW_MAX_LINES   128
#define DECW_LINE_LEN    256
#define DECW_MAX_BUTTONS 8

typedef struct {
    char label[32];
    char command[128];
    int x;
    int y;
    int w;
    int h;
    int pressed;
} DecwButton;

typedef struct {
    char app_id[64];
    char title[128];
    char display_name[128];
    char frame_path[256];
    char state_path[256];
    char exec_bin[256];
    char export_verb[32];
    char font_spec[128];
    int font_scale;
    int width;
    int height;
    int autoclose_ms;
    int verify_only;
    int test_interact;
} DecwWindowConfig;

/* Return the library version banner string */
const char* decw_x11_version(void);

/* Probe an X11 display server and populate human-readable server info */
int decw_x11_probe_display(const char* display_name, char* info_buf, size_t buf_len);

/* Load a rendered text/Motif frame file into a 2D line buffer; returns line count */
int decw_x11_load_frame(const char* frame_path, char lines[][DECW_LINE_LEN], int max_lines);

/* Resolve default title, state path, and backing executable for a DECwindows app_id */
void decw_x11_resolve_defaults(DecwWindowConfig* cfg, const char* self_exe);

/* Execute a BASIC-PLUS-2 command against the backing application binary and refresh frame_path */
int decw_x11_exec_app_cmd(const DecwWindowConfig* cfg, const char* b2_cmd, char* status_out, size_t status_len);

/* Open and run the interactive X11 Motif/XUI window event loop for a DECwindows application */
int decw_x11_run_window(const DecwWindowConfig* cfg);

#ifdef __cplusplus
}
#endif

#endif /* DECW_X11_H */
