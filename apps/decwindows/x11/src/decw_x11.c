#define _POSIX_C_SOURCE 200809L
#include "decw_x11.h"

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xatom.h>
#include <X11/keysym.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/select.h>
#include <sys/time.h>

typedef struct {
    unsigned long bg_gray;
    unsigned long bevel_light;
    unsigned long bevel_dark;
    unsigned long title_bg;
    unsigned long title_fg;
    unsigned long canvas_bg;
    unsigned long canvas_fg;
    unsigned long accent_green;
    unsigned long accent_amber;
    unsigned long btn_bg;
    unsigned long cmd_bg;
} DecwColors;

static unsigned long alloc_color(Display* dpy, int screen, const char* hex, unsigned long fallback) {
    Colormap cmap = DefaultColormap(dpy, screen);
    XColor col, exact;
    if (XAllocNamedColor(dpy, cmap, hex, &col, &exact)) {
        return col.pixel;
    }
    return fallback;
}

static void init_colors(Display* dpy, int screen, const char* app_id, DecwColors* c) {
    unsigned long white = WhitePixel(dpy, screen);
    unsigned long black = BlackPixel(dpy, screen);

    c->bg_gray      = alloc_color(dpy, screen, "#AEB2C3", white);
    c->bevel_light  = alloc_color(dpy, screen, "#E4E7F2", white);
    c->bevel_dark   = alloc_color(dpy, screen, "#525668", black);
    c->title_bg     = alloc_color(dpy, screen, "#3B5978", black);
    c->title_fg     = alloc_color(dpy, screen, "#FFFFFF", white);
    c->btn_bg       = alloc_color(dpy, screen, "#C5C9D8", white);
    c->cmd_bg       = alloc_color(dpy, screen, "#FFFFFF", white);
    c->accent_green = alloc_color(dpy, screen, "#28C840", black);
    c->accent_amber = alloc_color(dpy, screen, "#E5A000", black);

    (void)app_id;
    c->canvas_bg = alloc_color(dpy, screen, "#F6F5F0", white);
    c->canvas_fg = alloc_color(dpy, screen, "#141820", black);
}

static void draw_bevel_rect(Display* dpy, Window win, GC gc, const DecwColors* c,
                            int x, int y, int w, int h, unsigned long fill, int sunken) {
    unsigned long tl = sunken ? c->bevel_dark : c->bevel_light;
    unsigned long br = sunken ? c->bevel_light : c->bevel_dark;

    XSetForeground(dpy, gc, fill);
    XFillRectangle(dpy, win, gc, x, y, (unsigned int)w, (unsigned int)h);

    /* 2-pixel 3D OSF/Motif bevel border */
    XSetForeground(dpy, gc, tl);
    XDrawLine(dpy, win, gc, x, y, x + w - 1, y);
    XDrawLine(dpy, win, gc, x, y, x, y + h - 1);
    XDrawLine(dpy, win, gc, x + 1, y + 1, x + w - 2, y + 1);
    XDrawLine(dpy, win, gc, x + 1, y + 1, x + 1, y + h - 2);

    XSetForeground(dpy, gc, br);
    XDrawLine(dpy, win, gc, x, y + h - 1, x + w - 1, y + h - 1);
    XDrawLine(dpy, win, gc, x + w - 1, y, x + w - 1, y + h - 1);
    XDrawLine(dpy, win, gc, x + 1, y + h - 2, x + w - 2, y + h - 2);
    XDrawLine(dpy, win, gc, x + w - 2, y + 1, x + w - 2, y + h - 2);
}

const char* decw_x11_version(void) {
    return DECW_X11_VERSION;
}

int decw_x11_probe_display(const char* display_name, char* info_buf, size_t buf_len) {
    const char* dname = (display_name && display_name[0]) ? display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) {
        if (info_buf && buf_len > 0) {
            snprintf(info_buf, buf_len, "X11 Status: OFFLINE (unable to open display '%s')",
                     dname ? dname : "(unset)");
        }
        return -1;
    }

    int scr = DefaultScreen(dpy);
    int w = DisplayWidth(dpy, scr);
    int h = DisplayHeight(dpy, scr);
    int depth = DefaultDepth(dpy, scr);
    const char* vendor = ServerVendor(dpy);
    int rel = VendorRelease(dpy);

    if (info_buf && buf_len > 0) {
        snprintf(info_buf, buf_len,
                 "X11 Display: %s | Protocol: X%dR%d | Vendor: %s (%d) | Screen: %dx%d (%d-bit)",
                 DisplayString(dpy), ProtocolVersion(dpy), ProtocolRevision(dpy),
                 vendor ? vendor : "X11", rel, w, h, depth);
    }

    XCloseDisplay(dpy);
    return 0;
}

int decw_x11_load_frame(const char* frame_path, char lines[][DECW_LINE_LEN], int max_lines) {
    if (!frame_path || !frame_path[0] || max_lines <= 0) return 0;
    FILE* fp = fopen(frame_path, "r");
    if (!fp) return 0;

    int count = 0;
    char buf[512];
    while (count < max_lines && fgets(buf, sizeof(buf), fp)) {
        buf[strcspn(buf, "\r\n")] = '\0';
        snprintf(lines[count], DECW_LINE_LEN, "%.*s", DECW_LINE_LEN - 1, buf);
        count++;
    }
    fclose(fp);
    return count;
}

void decw_x11_resolve_defaults(DecwWindowConfig* cfg, const char* self_exe) {
    if (!cfg) return;
    if (!cfg->app_id[0]) strcpy(cfg->app_id, "decwindows");
    if (!cfg->export_verb[0]) strcpy(cfg->export_verb, "EXPORT");

    if (!cfg->frame_path[0]) {
        snprintf(cfg->frame_path, sizeof(cfg->frame_path), "/tmp/decw_%s.txt", cfg->app_id);
    }
    if (!cfg->state_path[0] &&
        strcasecmp(cfg->app_id, "clock") != 0 &&
        strcasecmp(cfg->app_id, "dxclock") != 0) {
        snprintf(cfg->state_path, sizeof(cfg->state_path), "/tmp/decw_%s.dat", cfg->app_id);
    }

    /* Default authentic DECwindows title per application */
    if (!cfg->title[0] || strcmp(cfg->title, "DECwindows Motif 1.1 Workstation Window") == 0) {
        if (strcasecmp(cfg->app_id, "decterm") == 0 || strcasecmp(cfg->app_id, "dxterm") == 0)
            strcpy(cfg->title, "DECterm - VAXcluster Node STAR:: (VT300)");
        else if (strcasecmp(cfg->app_id, "bookreader") == 0 || strcasecmp(cfg->app_id, "dxbook") == 0)
            strcpy(cfg->title, "DECwindows Bookreader - LIBRARY.DECW$BOOKSHELF");
        else if (strcasecmp(cfg->app_id, "calendar") == 0 || strcasecmp(cfg->app_id, "dxcalendar") == 0)
            strcpy(cfg->title, "DECwindows Calendar - October 1991 (STAR::SYSTEM)");
        else if (strcasecmp(cfg->app_id, "cardfiler") == 0 || strcasecmp(cfg->app_id, "dxcardfiler") == 0)
            strcpy(cfg->title, "DECwindows Cardfiler - DEC_SYSTEMS.CRD");
        else if (strcasecmp(cfg->app_id, "cdaviewer") == 0 || strcasecmp(cfg->app_id, "dxvdoc") == 0)
            strcpy(cfg->title, "DECwindows CDA Viewer - ALPHA_ARCH.DDIF");
        else if (strcasecmp(cfg->app_id, "calculator") == 0 || strcasecmp(cfg->app_id, "dxcalc") == 0)
            strcpy(cfg->title, "DECwindows Calculator - Scientific / Financial / Hex");
        else if (strcasecmp(cfg->app_id, "clock") == 0 || strcasecmp(cfg->app_id, "dxclock") == 0)
            strcpy(cfg->title, "DECwindows Clock - Maynard HQ (MLO) EST");
        else if (strcasecmp(cfg->app_id, "decsound") == 0 || strcasecmp(cfg->app_id, "dxsound") == 0)
            strcpy(cfg->title, "DECwindows DECsound - AMD Am79C30A 8kHz Mu-Law");
        else if (strcasecmp(cfg->app_id, "dxmail") == 0 || strcasecmp(cfg->app_id, "decwinmail") == 0)
            strcpy(cfg->title, "DECwindows Mail - Cabinet: MAIN [INBOX]");
        else if (strcasecmp(cfg->app_id, "fileview") == 0 || strcasecmp(cfg->app_id, "dxfileview") == 0)
            strcpy(cfg->title, "DECwindows FileView - DISK$VMS:[DECW.WORK]");
        else if (strcasecmp(cfg->app_id, "notepad") == 0 || strcasecmp(cfg->app_id, "dxnotepad") == 0)
            strcpy(cfg->title, "DECwindows Notepad - SYS$LOGIN:RELEASE_NOTES.TXT");
    }

    /* Automatically locate backing BASIC-PLUS-2 binary if not specified */
    if (!cfg->exec_bin[0] && strcmp(cfg->app_id, "decwindows") != 0) {
        char cand[512];
        if (self_exe && self_exe[0]) {
            const char* slash = strrchr(self_exe, '/');
            if (slash) {
                size_t dlen = (size_t)(slash - self_exe);
                if (dlen < 300) {
                    char dir[320];
                    memcpy(dir, self_exe, dlen);
                    dir[dlen] = '\0';
                    snprintf(cand, sizeof(cand), "%s/%s", dir, cfg->app_id);
                    if (access(cand, X_OK) == 0) {
                        snprintf(cfg->exec_bin, sizeof(cfg->exec_bin), "%.*s", (int)sizeof(cfg->exec_bin) - 1, cand);
                        return;
                    }
                    snprintf(cand, sizeof(cand), "%s/../../%s/bin/%s", dir, cfg->app_id, cfg->app_id);
                    if (access(cand, X_OK) == 0) {
                        snprintf(cfg->exec_bin, sizeof(cfg->exec_bin), "%.*s", (int)sizeof(cfg->exec_bin) - 1, cand);
                        return;
                    }
                }
            }
        }
        snprintf(cand, sizeof(cand), "./bin/%s", cfg->app_id);
        if (access(cand, X_OK) == 0) {
            snprintf(cfg->exec_bin, sizeof(cfg->exec_bin), "%.*s", (int)sizeof(cfg->exec_bin) - 1, cand);
            return;
        }
        snprintf(cand, sizeof(cand), "apps/decwindows/%s/bin/%s", cfg->app_id, cfg->app_id);
        if (access(cand, X_OK) == 0) {
            snprintf(cfg->exec_bin, sizeof(cfg->exec_bin), "%.*s", (int)sizeof(cfg->exec_bin) - 1, cand);
            return;
        }
        snprintf(cand, sizeof(cand), "../%s/bin/%s", cfg->app_id, cfg->app_id);
        if (access(cand, X_OK) == 0) {
            snprintf(cfg->exec_bin, sizeof(cfg->exec_bin), "%.*s", (int)sizeof(cfg->exec_bin) - 1, cand);
            return;
        }
    }
}

static void setup_app_buttons(const char* app_id, DecwButton* btns, int* num_btns) {
    *num_btns = 8;
    strcpy(btns[0].label, "Sample");
    strcpy(btns[0].command, "SAMPLE");

    strcpy(btns[1].label, "Refresh");
    strcpy(btns[1].command, "SHOW");

    strcpy(btns[2].label, "Action 1");
    strcpy(btns[2].command, "SHOW");

    strcpy(btns[3].label, "Action 2");
    strcpy(btns[3].command, "SHOW");

    strcpy(btns[4].label, "Clear");
    strcpy(btns[4].command, "CLEAR");

    strcpy(btns[5].label, "Font -");
    strcpy(btns[5].command, "__FONT_DEC__");

    strcpy(btns[6].label, "Font +");
    strcpy(btns[6].command, "__FONT_INC__");

    strcpy(btns[7].label, "Quit X11");
    strcpy(btns[7].command, "__QUIT__");

    if (!app_id) return;
    if (strcasecmp(app_id, "decterm") == 0 || strcasecmp(app_id, "dxterm") == 0) {
        strcpy(btns[1].label, "132 Col");
        strcpy(btns[1].command, "COLS 132");
        strcpy(btns[2].label, "80 Col");
        strcpy(btns[2].command, "COLS 80");
        strcpy(btns[3].label, "VT220 Mode");
        strcpy(btns[3].command, "MODE VT220");
    } else if (strcasecmp(app_id, "bookreader") == 0 || strcasecmp(app_id, "dxbook") == 0) {
        strcpy(btns[1].label, "Open VAX");
        strcpy(btns[1].command, "OPEN 1");
        strcpy(btns[2].label, "Next Topic");
        strcpy(btns[2].command, "NEXT");
        strcpy(btns[3].label, "Prev Topic");
        strcpy(btns[3].command, "PREV");
    } else if (strcasecmp(app_id, "calendar") == 0 || strcasecmp(app_id, "dxcalendar") == 0) {
        strcpy(btns[1].label, "Day 15");
        strcpy(btns[1].command, "DATE 15");
        strcpy(btns[2].label, "Day 16");
        strcpy(btns[2].command, "DATE 16");
        strcpy(btns[3].label, "Alarms");
        strcpy(btns[3].command, "ALARMS");
    } else if (strcasecmp(app_id, "cardfiler") == 0 || strcasecmp(app_id, "dxcardfiler") == 0) {
        strcpy(btns[1].label, "Next Card");
        strcpy(btns[1].command, "NEXT");
        strcpy(btns[2].label, "Prev Card");
        strcpy(btns[2].command, "PREV");
        strcpy(btns[3].label, "Sort Idx");
        strcpy(btns[3].command, "SORT INDEX");
    } else if (strcasecmp(app_id, "cdaviewer") == 0 || strcasecmp(app_id, "dxvdoc") == 0) {
        strcpy(btns[1].label, "Next Page");
        strcpy(btns[1].command, "NEXT");
        strcpy(btns[2].label, "Prev Page");
        strcpy(btns[2].command, "PREV");
        strcpy(btns[3].label, "Inspect");
        strcpy(btns[3].command, "CHECK");
    } else if (strcasecmp(app_id, "calculator") == 0 || strcasecmp(app_id, "dxcalc") == 0) {
        strcpy(btns[1].label, "Prog Mode");
        strcpy(btns[1].command, "MODE PROG");
        strcpy(btns[2].label, "Sci Mode");
        strcpy(btns[2].command, "MODE SCI");
        strcpy(btns[3].label, "PMT Loan");
        strcpy(btns[3].command, "PMT 100000 8.5 30");
    } else if (strcasecmp(app_id, "clock") == 0 || strcasecmp(app_id, "dxclock") == 0) {
        strcpy(btns[1].label, "+15 Min");
        strcpy(btns[1].command, "TICK 15");
        strcpy(btns[2].label, "12H Mode");
        strcpy(btns[2].command, "FORMAT 12");
        strcpy(btns[3].label, "24H Mode");
        strcpy(btns[3].command, "FORMAT 24");
    } else if (strcasecmp(app_id, "decsound") == 0 || strcasecmp(app_id, "dxsound") == 0) {
        strcpy(btns[1].label, "Play #1");
        strcpy(btns[1].command, "PLAY 1");
        strcpy(btns[2].label, "Play #2");
        strcpy(btns[2].command, "PLAY 2");
        strcpy(btns[3].label, "Spkr Out");
        strcpy(btns[3].command, "OUTPUT SPEAKER");
    } else if (strcasecmp(app_id, "dxmail") == 0 || strcasecmp(app_id, "decwinmail") == 0) {
        strcpy(btns[1].label, "Read #1");
        strcpy(btns[1].command, "READ 1");
        strcpy(btns[2].label, "Read #2");
        strcpy(btns[2].command, "READ 2");
        strcpy(btns[3].label, "Inbox");
        strcpy(btns[3].command, "SELECT INBOX");
    } else if (strcasecmp(app_id, "fileview") == 0 || strcasecmp(app_id, "dxfileview") == 0) {
        strcpy(btns[1].label, "Filter *.BAS");
        strcpy(btns[1].command, "FILTER *.BAS");
        strcpy(btns[2].label, "Show All");
        strcpy(btns[2].command, "FILTER *.*");
        strcpy(btns[3].label, "Purge Ver");
        strcpy(btns[3].command, "PURGE");
    } else if (strcasecmp(app_id, "notepad") == 0 || strcasecmp(app_id, "dxnotepad") == 0) {
        strcpy(btns[1].label, "Wrap 60");
        strcpy(btns[1].command, "WRAP 60");
        strcpy(btns[2].label, "Wrap 72");
        strcpy(btns[2].command, "WRAP 72");
        strcpy(btns[3].label, "Copy 1-3");
        strcpy(btns[3].command, "COPY 1 3");
    }
}

int decw_x11_exec_app_cmd(const DecwWindowConfig* cfg, const char* b2_cmd, char* status_out, size_t status_len) {
    if (!cfg || !cfg->exec_bin[0] || !b2_cmd || !b2_cmd[0]) {
        if (status_out && status_len > 0) {
            snprintf(status_out, status_len, "Ready (static frame view)");
        }
        return -1;
    }

    const char* exp_verb = (cfg->export_verb[0]) ? cfg->export_verb : "EXPORT";
    char chained[1024];
    if (cfg->state_path[0] && access(cfg->state_path, R_OK) == 0) {
        snprintf(chained, sizeof(chained),
                 "LOAD %s; %s; SAVE %s; %s %s; EXIT",
                 cfg->state_path, b2_cmd, cfg->state_path, exp_verb, cfg->frame_path);
    } else if (cfg->state_path[0]) {
        snprintf(chained, sizeof(chained),
                 "SAMPLE; %s; SAVE %s; %s %s; EXIT",
                 b2_cmd, cfg->state_path, exp_verb, cfg->frame_path);
    } else {
        snprintf(chained, sizeof(chained),
                 "SAMPLE; %s; %s %s; EXIT",
                 b2_cmd, exp_verb, cfg->frame_path);
    }

    char sys_cmd[1400];
    snprintf(sys_cmd, sizeof(sys_cmd), "DECW_FORCE_CLI=1 \"%s\" \"%s\" >/dev/null 2>&1", cfg->exec_bin, chained);
    int rc = system(sys_cmd);
    if (status_out && status_len > 0) {
        snprintf(status_out, status_len, "Executed X11 callback: %s (rc=%d)", b2_cmd, rc);
    }
    return rc;
}

static void draw_app_vector_widget(Display* dpy, Window win, GC gc, const DecwColors* c,
                                   const char* app_id, int x, int y, int w, int h, int font_h) {
    draw_bevel_rect(dpy, win, gc, c, x, y, w, h, c->bg_gray, 1);

    if (app_id && (strcasecmp(app_id, "clock") == 0 || strcasecmp(app_id, "dxclock") == 0)) {
        /* Native X11 Vector Analog Clock Dial */
        int cx = x + w / 2;
        int cy = y + h / 2;
        int r = (w < h ? w : h) / 2 - 4;
        if (r > 8) {
            XSetForeground(dpy, gc, c->canvas_bg);
            XFillArc(dpy, win, gc, cx - r, cy - r, (unsigned int)(r * 2), (unsigned int)(r * 2), 0, 360 * 64);
            XSetForeground(dpy, gc, c->bevel_dark);
            XDrawArc(dpy, win, gc, cx - r, cy - r, (unsigned int)(r * 2), (unsigned int)(r * 2), 0, 360 * 64);
            for (int tick = 0; tick < 12; tick++) {
                double ang = (tick * 30.0 - 90.0) * 3.14159265 / 180.0;
                int x1 = cx + (int)((r - 4) * cos(ang));
                int y1 = cy + (int)((r - 4) * sin(ang));
                int x2 = cx + (int)(r * cos(ang));
                int y2 = cy + (int)(r * sin(ang));
                XDrawLine(dpy, win, gc, x1, y1, x2, y2);
            }
            XSetForeground(dpy, gc, c->title_bg);
            XDrawLine(dpy, win, gc, cx, cy, cx - (int)(r * 0.5), cy - (int)(r * 0.3));
            XSetForeground(dpy, gc, c->canvas_fg);
            XDrawLine(dpy, win, gc, cx, cy, cx + (int)(r * 0.75), cy);
        }
    } else if (app_id && (strcasecmp(app_id, "decsound") == 0 || strcasecmp(app_id, "dxsound") == 0)) {
        /* Native X11 VU Meter Bars */
        XSetForeground(dpy, gc, c->canvas_fg);
        XDrawString(dpy, win, gc, x + 8, y + font_h, "X11 Am79C30A VU", 15);
        for (int b = 0; b < 8; b++) {
            unsigned long col = (b < 5) ? c->accent_green : c->accent_amber;
            XSetForeground(dpy, gc, col);
            XFillRectangle(dpy, win, gc, x + 10 + b * 14, y + font_h + 4, 10, h - font_h - 8 > 8 ? h - font_h - 8 : 8);
        }
    } else {
        /* X11 Motif Protocol Telemetry Badge */
        XSetForeground(dpy, gc, c->title_bg);
        XFillRectangle(dpy, win, gc, x + 4, y + 4, (unsigned int)(w - 8), (unsigned int)(h - 8));
        XSetForeground(dpy, gc, c->title_fg);
        XDrawString(dpy, win, gc, x + 10, y + (h + font_h) / 2 - 2, "X11/Motif 1.1", 13);
    }
}

static int parse_font_spec_to_scale(const char* spec, char* custom_xlfd, size_t xlfd_len) {
    if (!spec || !spec[0]) return 0;
    if (strcasecmp(spec, "small") == 0 || strcmp(spec, "1") == 0) return 1;
    if (strcasecmp(spec, "medium") == 0 || strcmp(spec, "2") == 0) return 2;
    if (strcasecmp(spec, "large") == 0 || strcmp(spec, "3") == 0) return 3;
    if (strcasecmp(spec, "xlarge") == 0 || strcmp(spec, "4") == 0) return 4;
    if (strcasecmp(spec, "xxlarge") == 0 || strcmp(spec, "5") == 0) return 5;
    if (strcasecmp(spec, "huge") == 0 || strcmp(spec, "6") == 0) return 6;

    int px = atoi(spec);
    if (px >= 12 && px <= 48) {
        if (px <= 16) return 1;
        if (px <= 21) return 2;
        if (px <= 25) return 3;
        if (px <= 29) return 4;
        if (px <= 33) return 5;
        return 6;
    }

    if (custom_xlfd && xlfd_len > 0) {
        strncpy(custom_xlfd, spec, xlfd_len - 1);
        custom_xlfd[xlfd_len - 1] = '\0';
    }
    return 0;
}

static XFontStruct* load_scaled_font(Display* dpy, int scale, const char* custom_xlfd,
                                     char* loaded_desc, size_t desc_len, int* rec_w, int* rec_h) {
    static const char* scale_fonts[7][3] = {
        { "12x24", "10x20", "9x15" },
        { "9x15", "8x13", "fixed" }, /* 1: Small (15px) */
        { "10x20", "-misc-fixed-medium-r-normal--20-140-100-100-c-100-iso8859-1", "9x15" }, /* 2: Medium (20px) */
        { "12x24", "-sony-fixed-medium-r-normal--24-170-100-100-c-120-iso8859-1", "10x20" }, /* 3: Large (24px, HiDPI Default) */
        { "-misc-fixed-bold-r-normal--28-0-100-100-c-0-iso8859-1", "12x24", "10x20" }, /* 4: XLarge (28px) */
        { "-sony-fixed-medium-r-normal--32-0-100-100-c-0-iso8859-1", "-misc-fixed-bold-r-normal--32-0-100-100-c-0-iso8859-1", "12x24" }, /* 5: XXLarge (32px) */
        { "-sony-fixed-medium-r-normal--36-0-100-100-c-0-iso8859-1", "-misc-fixed-bold-r-normal--36-0-100-100-c-0-iso8859-1", "12x24" }  /* 6: Huge (36px) */
    };
    static const int scale_dims[7][2] = {
        { 1220, 880 },
        { 780,  600 },
        { 980,  740 },
        { 1220, 880 },
        { 1420, 1000 },
        { 1620, 1120 },
        { 1840, 1240 }
    };
    static const char* scale_names[7] = {
        "Auto", "Small (15px)", "Medium (20px)", "Large (24px)", "XLarge (28px)", "XXLarge (32px)", "Huge (36px)"
    };

    if (scale < 1) scale = 1;
    if (scale > 6) scale = 6;

    if (rec_w) *rec_w = scale_dims[scale][0];
    if (rec_h) *rec_h = scale_dims[scale][1];

    XFontStruct* f = NULL;
    if (custom_xlfd && custom_xlfd[0]) {
        f = XLoadQueryFont(dpy, custom_xlfd);
        if (f && loaded_desc && desc_len > 0) {
            snprintf(loaded_desc, desc_len, "Custom (%s)", custom_xlfd);
        }
    }
    for (int i = 0; !f && i < 3; i++) {
        f = XLoadQueryFont(dpy, scale_fonts[scale][i]);
    }
    if (!f) f = XLoadQueryFont(dpy, "fixed");

    if (loaded_desc && desc_len > 0 && (!custom_xlfd || !custom_xlfd[0])) {
        snprintf(loaded_desc, desc_len, "%s [Scale %d/6]", scale_names[scale], scale);
    }
    return f;
}

/* =========================================================================
 * Authentic DECwindows Clock (DECW$CLOCK / dxclock) Native X11/Motif Engine
 * ========================================================================= */

typedef struct {
    int show_analog;
    int show_digital;
    int show_date;
    int show_menubar;
    int military_time;
    int show_seconds;
    int chime_on;

    int alarm_on;
    int alarm_repeat;
    int alarm_bell;
    int alarm_hr;
    int alarm_min;
    char alarm_msg[128];

    int alarm_triggered;
    int last_trig_min;
    int last_chime_hr;

    long time_offset_sec;
    int use_custom_date;
    char custom_date[64];

    /* Menu state: 0=none, 1=File, 2=Options, 3=Help, 4=Popup(MB3) */
    int active_menu;
    int popup_x;
    int popup_y;

    /* Dialog state: 0=none, 1=Display Options, 2=Alarm Options, 3=Help/About */
    int active_dialog;
    int help_mode; /* 0=Overview, 1=About */

    /* Draft state for Display Options Dialog (OK / Apply / Cancel) */
    int dlg_analog;
    int dlg_digital;
    int dlg_date;
    int dlg_menubar;
    int dlg_military;
    int dlg_seconds;
    int dlg_chime;

    /* Draft state for Alarm Options Dialog (OK / Apply / Cancel) */
    int dlg_alm_on;
    int dlg_alm_repeat;
    int dlg_alm_bell;
    int dlg_alm_hr;
    int dlg_alm_min;
    char dlg_alm_msg[128];
} DecwClockState;

static void clock_init_defaults(DecwClockState* st) {
    memset(st, 0, sizeof(*st));
    st->show_analog = 1;
    st->show_digital = 1;
    st->show_date = 1;
    st->show_menubar = 1;
    st->military_time = 0;
    st->show_seconds = 1;
    st->chime_on = 0;

    st->alarm_on = 0;
    st->alarm_repeat = 1;
    st->alarm_bell = 1;
    st->alarm_hr = 15;
    st->alarm_min = 0;
    strcpy(st->alarm_msg, "DECwindows Clock Reminder");

    st->last_trig_min = -1;
    st->last_chime_hr = -1;
}

static void clock_load_state_file(DecwClockState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "r");
    if (!fp) return;
    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        line[strcspn(line, "\r\n")] = '\0';
        if (strncmp(line, "CLK|", 4) == 0) {
            char* p = line + 4;
            char* s1 = strchr(p, '|');
            if (s1) {
                *s1 = '\0';
                char* s2 = strchr(s1 + 1, '|');
                if (s2) {
                    *s2 = '\0';
                    char* s3 = strchr(s2 + 1, '|');
                    if (s3) {
                        *s3 = '\0';
                        const char* face = s3 + 1;
                        if (strcasecmp(face, "ANALOG") == 0) {
                            st->show_analog = 1;
                            st->show_digital = 0;
                        } else if (strcasecmp(face, "DIGITAL") == 0) {
                            st->show_analog = 0;
                            st->show_digital = 1;
                        } else if (strcasecmp(face, "BOTH") == 0) {
                            st->show_analog = 1;
                            st->show_digital = 1;
                        }
                    }
                }
            }
        } else if (strncmp(line, "ALM|", 4) == 0) {
            char* p = line + 4;
            char* s1 = strchr(p, '|');
            if (s1) {
                *s1 = '\0';
                st->alarm_on = atoi(p) ? 1 : 0;
                char* s2 = strchr(s1 + 1, '|');
                if (s2) {
                    *s2 = '\0';
                    st->alarm_hr = atoi(s1 + 1) % 24;
                    char* s3 = strchr(s2 + 1, '|');
                    if (s3) {
                        *s3 = '\0';
                        st->alarm_min = atoi(s2 + 1) % 60;
                        strncpy(st->alarm_msg, s3 + 1, sizeof(st->alarm_msg) - 1);
                        st->alarm_msg[sizeof(st->alarm_msg) - 1] = '\0';
                    }
                }
            }
        } else if (strncmp(line, "OPT|", 4) == 0) {
            int a = 1, dg = 1, dt = 1, mb = 1, mil = 0, rpt = 1;
            if (sscanf(line + 4, "%d|%d|%d|%d|%d|%d", &a, &dg, &dt, &mb, &mil, &rpt) >= 5) {
                st->show_analog = a ? 1 : 0;
                st->show_digital = dg ? 1 : 0;
                st->show_date = dt ? 1 : 0;
                st->show_menubar = mb ? 1 : 0;
                st->military_time = mil ? 1 : 0;
                st->alarm_repeat = rpt ? 1 : 0;
                if (!st->show_analog && !st->show_digital && !st->show_date) {
                    st->show_analog = 1;
                }
            }
        }
    }
    fclose(fp);
}

static void clock_save_state_file(const DecwClockState* st, const char* path, int cur_hr, int cur_min, const char* date_str) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    const char* face = (st->show_analog && st->show_digital) ? "BOTH" : (st->show_analog ? "ANALOG" : "DIGITAL");
    fprintf(fp, "CLK|%d|%d|%s|%s\n", cur_hr, cur_min, date_str, face);
    fprintf(fp, "ALM|%d|%d|%d|%s\n", st->alarm_on, st->alarm_hr, st->alarm_min, st->alarm_msg);
    fprintf(fp, "OPT|%d|%d|%d|%d|%d|%d\n",
            st->show_analog, st->show_digital, st->show_date,
            st->show_menubar, st->military_time, st->alarm_repeat);
    fclose(fp);
}

static void draw_motif_checkbox(Display* dpy, Window win, GC gc, const DecwColors* c,
                                int x, int y, int box_sz, int checked, const char* label, int font_asc) {
    /* Sunken when checked, raised when unchecked (authentic OSF/Motif XmToggleButton indicator) */
    unsigned long fill = checked ? c->accent_amber : c->bg_gray;
    draw_bevel_rect(dpy, win, gc, c, x, y, box_sz, box_sz, fill, checked ? 1 : 0);
    if (checked) {
        XSetForeground(dpy, gc, c->canvas_fg);
        XDrawLine(dpy, win, gc, x + 3, y + box_sz / 2, x + box_sz / 2 - 1, y + box_sz - 4);
        XDrawLine(dpy, win, gc, x + box_sz / 2 - 1, y + box_sz - 4, x + box_sz - 3, y + 3);
        XDrawLine(dpy, win, gc, x + 3, y + box_sz / 2 + 1, x + box_sz / 2 - 1, y + box_sz - 3);
        XDrawLine(dpy, win, gc, x + box_sz / 2 - 1, y + box_sz - 3, x + box_sz - 3, y + 4);
    }
    if (label && label[0]) {
        XSetForeground(dpy, gc, c->canvas_fg);
        XDrawString(dpy, win, gc, x + box_sz + 10, y + (box_sz + font_asc) / 2 - 2, label, (int)strlen(label));
    }
}

static void draw_bell_icon(Display* dpy, Window win, GC gc, const DecwColors* c, int cx, int cy, int r) {
    /* Classic DECwindows Alarm Bell Vector Icon */
    XSetForeground(dpy, gc, c->accent_amber);
    XFillArc(dpy, win, gc, cx - r, cy - r, (unsigned int)(r * 2), (unsigned int)(r * 2), 0, 180 * 64);
    XPoint trap[4];
    trap[0].x = (short)(cx - r);         trap[0].y = (short)cy;
    trap[1].x = (short)(cx + r);         trap[1].y = (short)cy;
    trap[2].x = (short)(cx + r + r / 3); trap[2].y = (short)(cy + r - 2);
    trap[3].x = (short)(cx - r - r / 3); trap[3].y = (short)(cy + r - 2);
    XFillPolygon(dpy, win, gc, trap, 4, Convex, CoordModeOrigin);

    XSetForeground(dpy, gc, c->canvas_fg);
    XDrawArc(dpy, win, gc, cx - r, cy - r, (unsigned int)(r * 2), (unsigned int)(r * 2), 0, 180 * 64);
    XDrawLine(dpy, win, gc, trap[0].x, trap[0].y, trap[3].x, trap[3].y);
    XDrawLine(dpy, win, gc, trap[1].x, trap[1].y, trap[2].x, trap[2].y);
    XDrawLine(dpy, win, gc, trap[3].x, trap[3].y, trap[2].x, trap[2].y);
    /* Clapper */
    XFillArc(dpy, win, gc, cx - 3, cy + r - 3, 6, 6, 0, 360 * 64);
}

static void draw_clock_hand_polygon(Display* dpy, Window win, GC gc,
                                    int cx, int cy, double angle_rad,
                                    double len, double tail_len, double half_width,
                                    unsigned long fill_col, unsigned long outline_col) {
    double dx = cos(angle_rad);
    double dy = sin(angle_rad);
    double px = -dy;
    double py = dx;

    XPoint pts[5];
    /* Back tail point */
    pts[0].x = (short)(cx - dx * tail_len);
    pts[0].y = (short)(cy - dy * tail_len);
    /* Left shoulder */
    pts[1].x = (short)(cx + dx * (len * 0.18) + px * half_width);
    pts[1].y = (short)(cy + dy * (len * 0.18) + py * half_width);
    /* Tip */
    pts[2].x = (short)(cx + dx * len);
    pts[2].y = (short)(cy + dy * len);
    /* Right shoulder */
    pts[3].x = (short)(cx + dx * (len * 0.18) - px * half_width);
    pts[3].y = (short)(cy + dy * (len * 0.18) - py * half_width);
    pts[4] = pts[0];

    XSetForeground(dpy, gc, fill_col);
    XFillPolygon(dpy, win, gc, pts, 4, Convex, CoordModeOrigin);
    XSetForeground(dpy, gc, outline_col);
    XDrawLines(dpy, win, gc, pts, 5, CoordModeOrigin);
}

static void clock_get_current_tm(const DecwClockState* st, struct tm* out_tm,
                                 char* date_buf, size_t date_len,
                                 char* time_buf, size_t time_len,
                                 char* alm_buf, size_t alm_len) {
    time_t now = time(NULL) + st->time_offset_sec;
    struct tm* lt = localtime(&now);
    if (lt) {
        *out_tm = *lt;
    } else {
        memset(out_tm, 0, sizeof(*out_tm));
        out_tm->tm_hour = 12;
        out_tm->tm_mday = 20;
        out_tm->tm_mon = 9;
        out_tm->tm_year = 126;
    }

    static const char* wdays[7] = { "SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT" };
    static const char* mons[12] = { "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" };

    if (st->use_custom_date && st->custom_date[0]) {
        snprintf(date_buf, date_len, "%s", st->custom_date);
    } else {
        int wd = (out_tm->tm_wday >= 0 && out_tm->tm_wday < 7) ? out_tm->tm_wday : 0;
        int mo = (out_tm->tm_mon >= 0 && out_tm->tm_mon < 12) ? out_tm->tm_mon : 0;
        snprintf(date_buf, date_len, "%s %02d-%s-%04d",
                 wdays[wd], out_tm->tm_mday, mons[mo], out_tm->tm_year + 1900);
    }

    if (st->military_time) {
        if (st->show_seconds) {
            snprintf(time_buf, time_len, "%02d:%02d:%02d", out_tm->tm_hour, out_tm->tm_min, out_tm->tm_sec);
        } else {
            snprintf(time_buf, time_len, "%02d:%02d", out_tm->tm_hour, out_tm->tm_min);
        }
        snprintf(alm_buf, alm_len, "%02d:%02d", st->alarm_hr, st->alarm_min);
    } else {
        const char* ampm = (out_tm->tm_hour >= 12) ? "PM" : "AM";
        int h12 = out_tm->tm_hour % 12;
        if (h12 == 0) h12 = 12;
        if (st->show_seconds) {
            snprintf(time_buf, time_len, "%2d:%02d:%02d %s", h12, out_tm->tm_min, out_tm->tm_sec, ampm);
        } else {
            snprintf(time_buf, time_len, "%2d:%02d %s", h12, out_tm->tm_min, ampm);
        }
        const char* a_ampm = (st->alarm_hr >= 12) ? "PM" : "AM";
        int ah12 = st->alarm_hr % 12;
        if (ah12 == 0) ah12 = 12;
        snprintf(alm_buf, alm_len, "%d:%02d %s", ah12, st->alarm_min, a_ampm);
    }
}

static void clock_open_display_dialog(DecwClockState* st) {
    st->dlg_analog = st->show_analog;
    st->dlg_digital = st->show_digital;
    st->dlg_date = st->show_date;
    st->dlg_menubar = st->show_menubar;
    st->dlg_military = st->military_time;
    st->dlg_seconds = st->show_seconds;
    st->dlg_chime = st->chime_on;
    st->active_dialog = 1;
    st->active_menu = 0;
}

static void clock_apply_display_dialog(DecwClockState* st) {
    st->show_analog = st->dlg_analog;
    st->show_digital = st->dlg_digital;
    st->show_date = st->dlg_date;
    st->show_menubar = st->dlg_menubar;
    st->military_time = st->dlg_military;
    st->show_seconds = st->dlg_seconds;
    st->chime_on = st->dlg_chime;
    if (!st->show_analog && !st->show_digital && !st->show_date) {
        st->show_analog = 1;
        st->dlg_analog = 1;
    }
}

static void clock_open_alarm_dialog(DecwClockState* st) {
    st->dlg_alm_on = st->alarm_on;
    st->dlg_alm_repeat = st->alarm_repeat;
    st->dlg_alm_bell = st->alarm_bell;
    st->dlg_alm_hr = st->alarm_hr;
    st->dlg_alm_min = st->alarm_min;
    strncpy(st->dlg_alm_msg, st->alarm_msg, sizeof(st->dlg_alm_msg) - 1);
    st->dlg_alm_msg[sizeof(st->dlg_alm_msg) - 1] = '\0';
    st->active_dialog = 2;
    st->active_menu = 0;
}

static void clock_apply_alarm_dialog(DecwClockState* st) {
    st->alarm_on = st->dlg_alm_on;
    st->alarm_repeat = st->dlg_alm_repeat;
    st->alarm_bell = st->dlg_alm_bell;
    st->alarm_hr = (st->dlg_alm_hr + 24) % 24;
    st->alarm_min = (st->dlg_alm_min + 60) % 60;
    strncpy(st->alarm_msg, st->dlg_alm_msg, sizeof(st->alarm_msg) - 1);
    st->alarm_msg[sizeof(st->alarm_msg) - 1] = '\0';
    st->last_trig_min = -1;
}

static void clock_recommended_size(int scale, int show_analog, int* out_w, int* out_h) {
    static const int clk_dims[7][2] = {
        { 460, 580 },
        { 320, 410 }, /* 1: Small */
        { 390, 490 }, /* 2: Medium */
        { 470, 590 }, /* 3: Large (HiDPI default) */
        { 550, 680 }, /* 4: XLarge */
        { 630, 770 }, /* 5: XXLarge */
        { 710, 860 }  /* 6: Huge */
    };
    if (scale < 1) scale = 1;
    if (scale > 6) scale = 6;
    if (out_w) *out_w = clk_dims[scale][0];
    if (out_h) {
        *out_h = show_analog ? clk_dims[scale][1] : (clk_dims[scale][0] / 2 + 40);
    }
}

static int run_clock_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) {
        fprintf(stderr, "%%DECW-E-NOX11, unable to open X11 display '%s'\n", dname ? dname : "(null)");
        return 1;
    }

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, cfg->app_id, &colors);
    unsigned long crimson_col = alloc_color(dpy, screen, "#C82828", colors.canvas_fg);
    unsigned long navy_hand   = alloc_color(dpy, screen, "#1E2F46", colors.canvas_fg);
    unsigned long dial_rim    = alloc_color(dpy, screen, "#D6DAE6", colors.bg_gray);

    int font_scale = (disp_w >= 2560) ? 3 : 2;
    char custom_xlfd[128] = "";

    const char* env_fsize = getenv("DECW_FONT_SIZE");
    const char* env_fx11 = getenv("DECW_X11_FONT");
    const char* env_scale = getenv("DECW_SCALE");

    if (env_scale && env_scale[0]) {
        int s = parse_font_spec_to_scale(env_scale, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (env_fsize && env_fsize[0]) {
        int s = parse_font_spec_to_scale(env_fsize, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (env_fx11 && env_fx11[0]) {
        int s = parse_font_spec_to_scale(env_fx11, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (cfg->font_scale >= 1 && cfg->font_scale <= 6) {
        font_scale = cfg->font_scale;
    }
    if (cfg->font_spec[0]) {
        int s = parse_font_spec_to_scale(cfg->font_spec, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }

    DecwClockState st;
    clock_init_defaults(&st);
    const char* save_target = cfg->state_path[0] ? cfg->state_path : "/tmp/decw_clock_saved.dat";
    if (cfg->state_path[0] && access(cfg->state_path, R_OK) == 0) {
        clock_load_state_file(&st, cfg->state_path);
    } else if (access("/tmp/decw_clock_saved.dat", R_OK) == 0) {
        clock_load_state_file(&st, "/tmp/decw_clock_saved.dat");
    }

    char font_desc[96] = "";
    int dummy_w = 0, dummy_h = 0;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &dummy_w, &dummy_h);

    int rec_w = 470, rec_h = 590;
    clock_recommended_size(font_scale, st.show_analog, &rec_w, &rec_h);

    int win_w = (cfg->width >= 240) ? cfg->width : rec_w;
    int win_h = (cfg->height >= 180) ? cfg->height : rec_h;
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window root = RootWindow(dpy, screen);
    Window win = XCreateSimpleWindow(dpy, root, 100, 80, (unsigned int)win_w, (unsigned int)win_h,
                                     2, colors.bevel_dark, colors.bg_gray);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Clock";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$CLOCK");

    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);

    Atom decw_atom = XInternAtom(dpy, "_DECW_MOTIF_APP_ID", False);
    XChangeProperty(dpy, win, decw_atom, XA_STRING, 8, PropModeReplace,
                    (const unsigned char*)"clock", 5);

    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) {
        XSetFont(dpy, gc, font->fid);
    }

    /* Disable X server automatic background erase on Expose/Configure to prevent any flicker */
    XSetWindowBackgroundPixmap(dpy, win, None);

    int depth = DefaultDepth(dpy, screen);
    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w;
    int buf_h = win_h;

    XMapWindow(dpy, win);
    XFlush(dpy);

    int autoclose_ms = cfg->autoclose_ms;
    const char* env_ac = getenv("DECW_X11_AUTOCLOSE_MS");
    if (autoclose_ms <= 0 && env_ac && env_ac[0]) {
        autoclose_ms = atoi(env_ac);
    }
    if (cfg->verify_only && autoclose_ms <= 0) {
        autoclose_ms = 120;
    }

    struct timeval start_tv;
    gettimeofday(&start_tv, NULL);
    int exposed_once = 0;
    int sent_synth = 0;
    int running = 1;
    int last_drawn_sec = -1;

    while (running) {
        int need_redraw = 0;
        struct tm cur_tm;
        char date_str[64], time_str[64], alm_str[32];
        clock_get_current_tm(&st, &cur_tm, date_str, sizeof(date_str),
                             time_str, sizeof(time_str), alm_str, sizeof(alm_str));

        /* Check hourly chime */
        if (st.chime_on && cur_tm.tm_min == 0 && cur_tm.tm_sec == 0 && st.last_chime_hr != cur_tm.tm_hour) {
            st.last_chime_hr = cur_tm.tm_hour;
            XBell(dpy, 80);
        }

        /* Check alarm trigger */
        if (st.alarm_on && cur_tm.tm_hour == st.alarm_hr && cur_tm.tm_min == st.alarm_min &&
            st.last_trig_min != (cur_tm.tm_hour * 60 + cur_tm.tm_min)) {
            st.last_trig_min = cur_tm.tm_hour * 60 + cur_tm.tm_min;
            st.alarm_triggered = 1;
            if (st.alarm_bell) {
                XBell(dpy, 100);
            }
            need_redraw = 1;
        }

        /* Redraw every second for live ticking hands & digital clock (double-buffered, zero flicker) */
        if (exposed_once && cur_tm.tm_sec != last_drawn_sec) {
            last_drawn_sec = cur_tm.tm_sec;
            need_redraw = 1;
        }

        int font_asc = font ? font->ascent : 14;
        int font_desc_px = font ? font->descent : 4;
        int font_h = font_asc + font_desc_px;
        if (font_h < 14) font_h = 14;
        int char_w = (font && font->max_bounds.width > 6) ? font->max_bounds.width : (font_h / 2 + 2);
        int mb_h = st.show_menubar ? (font_h + 14) : 0;

        while (XPending(dpy) > 0) {
            XEvent ev;
            XNextEvent(dpy, &ev);

            font_asc = font ? font->ascent : 14;
            font_desc_px = font ? font->descent : 4;
            font_h = font_asc + font_desc_px;
            if (font_h < 14) font_h = 14;
            char_w = (font && font->max_bounds.width > 6) ? font->max_bounds.width : (font_h / 2 + 2);
            mb_h = st.show_menubar ? (font_h + 14) : 0;

            if (ev.type == ConfigureNotify) {
                if (ev.xconfigure.width != win_w || ev.xconfigure.height != win_h) {
                    win_w = ev.xconfigure.width;
                    win_h = ev.xconfigure.height;
                    need_redraw = 1;
                }
            } else if (ev.type == Expose && ev.xexpose.count == 0) {
                exposed_once = 1;
                need_redraw = 1;
            } else if (ev.type == ButtonPress) {
                int mx = ev.xbutton.x;
                int my = ev.xbutton.y;
                unsigned int btn = ev.xbutton.button;

                /* 1. If Alarm Notification popup is active, check OK button */
                if (st.alarm_triggered) {
                    int dh = font_h * 7 + 56;
                    int dy = (win_h - dh) / 2;
                    int bh = font_h + 12;
                    int by = dy + dh - bh - 10;
                    if (my >= by - 10 && my <= by + bh + 10) {
                        st.alarm_triggered = 0;
                        if (!st.alarm_repeat) {
                            st.alarm_on = 0;
                        }
                        need_redraw = 1;
                    }
                    continue;
                }

                /* 2. Right-click (Button 3) or Middle-click (Button 2) opens Popup Menu */
                if (btn == Button3 || btn == Button2) {
                    st.active_menu = 4;
                    st.popup_x = mx;
                    st.popup_y = my;
                    need_redraw = 1;
                    continue;
                }

                /* 3. Handle clicks inside an open Pull-down or Popup Menu */
                if (st.active_menu != 0) {
                    int handled_menu = 0;
                    if (st.active_menu == 1) {
                        int m_x = 12, m_y = 6 + mb_h;
                        int m_w = char_w * 14 + 24, m_h = font_h + 18;
                        if (mx >= m_x && mx <= m_x + m_w && my >= m_y && my <= m_y + m_h) {
                            running = 0;
                            handled_menu = 1;
                        }
                    } else if (st.active_menu == 2) {
                        int file_w = char_w * 4 + 20;
                        int m_x = 12 + file_w + 8;
                        int m_y = 6 + mb_h;
                        int row_h = font_h + 10;
                        int m_w = char_w * 24 + 28;
                        int m_h = row_h * 5 + 16;
                        if (m_x + m_w > win_w - 6) m_x = win_w - m_w - 6;
                        if (mx >= m_x && mx <= m_x + m_w && my >= m_y && my <= m_y + m_h) {
                            int idx = (my - m_y - 4) / row_h;
                            if (idx == 0) {
                                clock_open_display_dialog(&st);
                            } else if (idx == 1) {
                                clock_open_alarm_dialog(&st);
                            } else if (idx == 2) {
                                st.time_offset_sec = 0;
                                st.use_custom_date = 0;
                                st.active_menu = 0;
                            } else if (idx == 3) {
                                clock_save_state_file(&st, save_target, cur_tm.tm_hour, cur_tm.tm_min, date_str);
                                st.active_menu = 0;
                            } else if (idx >= 4) {
                                unlink("/tmp/decw_clock_saved.dat");
                                clock_init_defaults(&st);
                            }
                            handled_menu = 1;
                        }
                    } else if (st.active_menu == 3) {
                        int m_w = char_w * 18 + 24;
                        int m_x = win_w - m_w - 12;
                        int m_y = 6 + mb_h;
                        int row_h = font_h + 10;
                        int m_h = row_h * 2 + 12;
                        if (mx >= m_x && mx <= m_x + m_w && my >= m_y && my <= m_y + m_h) {
                            int idx = (my - m_y - 4) / row_h;
                            st.help_mode = (idx >= 1) ? 1 : 0;
                            st.active_dialog = 3;
                            st.active_menu = 0;
                            handled_menu = 1;
                        }
                    } else if (st.active_menu == 4) {
                        int row_h = font_h + 9;
                        int m_w = char_w * 23 + 32;
                        int m_h = row_h * 9 + 14;
                        int m_x = st.popup_x;
                        int m_y = st.popup_y;
                        if (m_x + m_w > win_w - 8) m_x = win_w - m_w - 8;
                        if (m_y + m_h > win_h - 8) m_y = win_h - m_h - 8;
                        if (m_x < 8) m_x = 8;
                        if (m_y < 8) m_y = 8;
                        if (mx >= m_x && mx <= m_x + m_w && my >= m_y && my <= m_y + m_h) {
                            int idx = (my - m_y - 4) / row_h;
                            st.active_menu = 0;
                            if (idx == 0) clock_open_display_dialog(&st);
                            else if (idx == 1) clock_open_alarm_dialog(&st);
                            else if (idx == 2) {
                                st.show_analog = !st.show_analog;
                                if (!st.show_analog && !st.show_digital && !st.show_date) st.show_digital = 1;
                            } else if (idx == 3) {
                                st.show_digital = !st.show_digital;
                                if (!st.show_analog && !st.show_digital && !st.show_date) st.show_analog = 1;
                            } else if (idx == 4) {
                                st.show_date = !st.show_date;
                                if (!st.show_analog && !st.show_digital && !st.show_date) st.show_analog = 1;
                            } else if (idx == 5) {
                                st.show_menubar = !st.show_menubar;
                            } else if (idx == 6) {
                                st.military_time = !st.military_time;
                            } else if (idx == 7) {
                                clock_save_state_file(&st, save_target, cur_tm.tm_hour, cur_tm.tm_min, date_str);
                            } else if (idx >= 8) {
                                running = 0;
                            }
                            handled_menu = 1;
                        }
                    }

                    if (!handled_menu) {
                        st.active_menu = 0;
                        need_redraw = 1;
                    } else {
                        need_redraw = 1;
                        continue;
                    }
                }

                /* 4. Handle clicks inside an open Dialog Box */
                if (st.active_dialog == 1) {
                    int dw = win_w - 32;
                    int dh = font_h * 12 + 76;
                    if (dw < 280) dw = win_w - 12;
                    if (dh > win_h - 16) dh = win_h - 16;
                    int dx = (win_w - dw) / 2;
                    int dy = (win_h - dh) / 2;
                    int th = font_h + 10;
                    int r_step = (dh - th - (font_h + 26)) / 7;
                    if (r_step < font_h + 4) r_step = font_h + 4;
                    int ry = dy + th + 10;

                    int bw = (dw - 48) / 3;
                    int bh = font_h + 12;
                    int by = dy + dh - bh - 10;

                    if (my >= by && my <= by + bh) {
                        if (mx >= dx + 12 && mx <= dx + 12 + bw) {
                            /* OK */
                            clock_apply_display_dialog(&st);
                            st.active_dialog = 0;
                        } else if (mx >= dx + 24 + bw && mx <= dx + 24 + bw * 2) {
                            /* Apply */
                            clock_apply_display_dialog(&st);
                        } else if (mx >= dx + 36 + bw * 2 && mx <= dx + 36 + bw * 3) {
                            /* Cancel */
                            st.active_dialog = 0;
                        }
                    } else if (mx >= dx + 12 && mx <= dx + dw - 12 && my >= ry && my < ry + r_step * 7) {
                        int idx = (my - ry) / r_step;
                        if (idx == 0) st.dlg_analog = !st.dlg_analog;
                        else if (idx == 1) st.dlg_digital = !st.dlg_digital;
                        else if (idx == 2) st.dlg_date = !st.dlg_date;
                        else if (idx == 3) st.dlg_menubar = !st.dlg_menubar;
                        else if (idx == 4) st.dlg_military = !st.dlg_military;
                        else if (idx == 5) st.dlg_seconds = !st.dlg_seconds;
                        else if (idx == 6) st.dlg_chime = !st.dlg_chime;
                    }
                    need_redraw = 1;
                    continue;
                } else if (st.active_dialog == 2) {
                    int dw = win_w - 24;
                    int dh = font_h * 12 + 80;
                    if (dw < 290) dw = win_w - 10;
                    if (dh > win_h - 16) dh = win_h - 16;
                    int dx = (win_w - dw) / 2;
                    int dy = (win_h - dh) / 2;
                    int th = font_h + 10;
                    int r_step = (dh - th - (font_h + 26)) / 7;
                    if (r_step < font_h + 4) r_step = font_h + 4;
                    int ry = dy + th + 10;

                    int bw = (dw - 48) / 3;
                    int bh = font_h + 12;
                    int by = dy + dh - bh - 10;

                    int btn_s = font_h + 8;
                    int hx = dx + 16 + char_w * 7;
                    int hplus_x = hx + btn_s + char_w * 4 + 20;
                    int test_x = hplus_x + btn_s + 12;
                    int hy = ry + r_step * 3;
                    int my_row = ry + r_step * 4;

                    if (my >= by && my <= by + bh) {
                        if (mx >= dx + 12 && mx <= dx + 12 + bw) {
                            clock_apply_alarm_dialog(&st);
                            st.active_dialog = 0;
                        } else if (mx >= dx + 24 + bw && mx <= dx + 24 + bw * 2) {
                            clock_apply_alarm_dialog(&st);
                        } else if (mx >= dx + 36 + bw * 2 && mx <= dx + 36 + bw * 3) {
                            st.active_dialog = 0;
                        }
                    } else if (my >= ry && my < ry + r_step * 3 && mx >= dx + 12 && mx <= dx + dw - 12) {
                        int idx = (my - ry) / r_step;
                        if (idx == 0) st.dlg_alm_on = !st.dlg_alm_on;
                        else if (idx == 1) st.dlg_alm_repeat = !st.dlg_alm_repeat;
                        else if (idx == 2) st.dlg_alm_bell = !st.dlg_alm_bell;
                    } else if (my >= hy && my <= hy + btn_s) {
                        if (mx >= hx && mx <= hx + btn_s) {
                            st.dlg_alm_hr = (st.dlg_alm_hr + 23) % 24;
                        } else if (mx >= hplus_x && mx <= hplus_x + btn_s) {
                            st.dlg_alm_hr = (st.dlg_alm_hr + 1) % 24;
                        } else if (mx >= test_x && mx <= dx + dw - 12) {
                            clock_apply_alarm_dialog(&st);
                            st.active_dialog = 0;
                            st.alarm_triggered = 1;
                            if (st.alarm_bell) XBell(dpy, 100);
                        }
                    } else if (my >= my_row && my <= my_row + btn_s) {
                        if (mx >= hx && mx <= hx + btn_s) {
                            st.dlg_alm_min = (st.dlg_alm_min + 59) % 60;
                        } else if (mx >= hplus_x && mx <= hplus_x + btn_s) {
                            st.dlg_alm_min = (st.dlg_alm_min + 1) % 60;
                        }
                    }
                    need_redraw = 1;
                    continue;
                } else if (st.active_dialog == 3) {
                    st.active_dialog = 0;
                    need_redraw = 1;
                    continue;
                }

                /* 5. Handle clicks on the Menubar (or hidden-menubar corner button) */
                if (st.show_menubar && my >= 6 && my <= 6 + mb_h) {
                    int file_x = 12;
                    int file_w = char_w * 4 + 20;
                    int opt_x  = file_x + file_w + 8;
                    int opt_w  = char_w * 7 + 20;
                    int help_w = char_w * 4 + 20;
                    int help_x = win_w - help_w - 12;

                    if (mx >= file_x && mx <= file_x + file_w) {
                        st.active_menu = (st.active_menu == 1) ? 0 : 1;
                    } else if (mx >= opt_x && mx <= opt_x + opt_w) {
                        st.active_menu = (st.active_menu == 2) ? 0 : 2;
                    } else if (mx >= help_x && mx <= help_x + help_w) {
                        st.active_menu = (st.active_menu == 3) ? 0 : 3;
                    } else {
                        st.active_menu = 0;
                    }
                    need_redraw = 1;
                } else if (!st.show_menubar) {
                    int h_sz = font_h + 4;
                    if (mx >= win_w - h_sz - 14 && my <= h_sz + 14) {
                        st.active_menu = 4;
                        st.popup_x = mx;
                        st.popup_y = my;
                        need_redraw = 1;
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                int n = XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                kbuf[n] = '\0';

                if (ks == XK_Escape) {
                    if (st.alarm_triggered) {
                        st.alarm_triggered = 0;
                    } else if (st.active_menu != 0) {
                        st.active_menu = 0;
                    } else if (st.active_dialog != 0) {
                        st.active_dialog = 0;
                    } else {
                        running = 0;
                    }
                    need_redraw = 1;
                } else if (st.active_dialog == 2) {
                    /* Typing in Alarm Options Dialog Message Box */
                    if (ks == XK_Return || ks == XK_KP_Enter) {
                        clock_apply_alarm_dialog(&st);
                        st.active_dialog = 0;
                        need_redraw = 1;
                    } else if (ks == XK_BackSpace || ks == XK_Delete) {
                        size_t len = strlen(st.dlg_alm_msg);
                        if (len > 0) {
                            st.dlg_alm_msg[len - 1] = '\0';
                            need_redraw = 1;
                        }
                    } else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127) {
                        size_t len = strlen(st.dlg_alm_msg);
                        if (len + 1 < sizeof(st.dlg_alm_msg)) {
                            st.dlg_alm_msg[len] = kbuf[0];
                            st.dlg_alm_msg[len + 1] = '\0';
                            need_redraw = 1;
                        }
                    }
                } else if (ks == XK_F10 || ks == XK_Next || ((ev.xkey.state & ControlMask) && (ks == XK_minus || ks == XK_underscore))) {
                    if (font_scale > 1) font_scale--;
                    custom_xlfd[0] = '\0';
                    if (font) XFreeFont(dpy, font);
                    font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &dummy_w, &dummy_h);
                    if (font) XSetFont(dpy, gc, font->fid);
                    clock_recommended_size(font_scale, st.show_analog, &rec_w, &rec_h);
                    win_w = (rec_w > disp_w - 80) ? disp_w - 80 : rec_w;
                    win_h = (rec_h > disp_h - 80) ? disp_h - 80 : rec_h;
                    XResizeWindow(dpy, win, (unsigned int)win_w, (unsigned int)win_h);
                    need_redraw = 1;
                } else if (ks == XK_F11 || ks == XK_Prior || ((ev.xkey.state & ControlMask) && (ks == XK_equal || ks == XK_plus))) {
                    if (font_scale < 6) font_scale++;
                    custom_xlfd[0] = '\0';
                    if (font) XFreeFont(dpy, font);
                    font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &dummy_w, &dummy_h);
                    if (font) XSetFont(dpy, gc, font->fid);
                    clock_recommended_size(font_scale, st.show_analog, &rec_w, &rec_h);
                    win_w = (rec_w > disp_w - 80) ? disp_w - 80 : rec_w;
                    win_h = (rec_h > disp_h - 80) ? disp_h - 80 : rec_h;
                    XResizeWindow(dpy, win, (unsigned int)win_w, (unsigned int)win_h);
                    need_redraw = 1;
                } else if (ks == XK_F1) {
                    st.help_mode = 0;
                    st.active_dialog = 3;
                    need_redraw = 1;
                } else if ((ev.xkey.state & ControlMask) && (ks == XK_q || ks == XK_Q)) {
                    running = 0;
                } else if ((ev.xkey.state & ControlMask) && (ks == XK_d || ks == XK_D)) {
                    clock_open_display_dialog(&st);
                    need_redraw = 1;
                } else if ((ev.xkey.state & ControlMask) && (ks == XK_a || ks == XK_A)) {
                    clock_open_alarm_dialog(&st);
                    need_redraw = 1;
                } else if ((ev.xkey.state & ControlMask) && (ks == XK_m || ks == XK_M)) {
                    st.show_menubar = !st.show_menubar;
                    need_redraw = 1;
                } else if ((ev.xkey.state & ControlMask) && (ks == XK_s || ks == XK_S)) {
                    clock_save_state_file(&st, save_target, cur_tm.tm_hour, cur_tm.tm_min, date_str);
                }
            } else if (ev.type == ClientMessage) {
                if ((Atom)ev.xclient.data.l[0] == wm_delete) {
                    running = 0;
                }
            }
        }

        if (need_redraw && running) {
            last_drawn_sec = cur_tm.tm_sec;
            if (win_w != buf_w || win_h != buf_h) {
                XFreePixmap(dpy, back_buf);
                back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
                buf_w = win_w;
                buf_h = win_h;
            }

            font_asc = font ? font->ascent : 14;
            font_desc_px = font ? font->descent : 4;
            font_h = font_asc + font_desc_px;
            if (font_h < 14) font_h = 14;
            char_w = (font && font->max_bounds.width > 6) ? font->max_bounds.width : (font_h / 2 + 2);
            mb_h = st.show_menubar ? (font_h + 14) : 0;

            /* 1. Outer 3D OSF/Motif Window Frame (drawn onto off-screen back_buf) */
            draw_bevel_rect(dpy, back_buf, gc, &colors, 0, 0, win_w, win_h, colors.bg_gray, 0);

            int cur_y = 6;

            /* 2. Authentic DECwindows Clock Menubar (File, Options, Help) */
            if (st.show_menubar) {
                draw_bevel_rect(dpy, back_buf, gc, &colors, 6, cur_y, win_w - 12, mb_h, colors.bg_gray, 0);

                int file_x = 12;
                int file_w = char_w * 4 + 20;
                int opt_x  = file_x + file_w + 8;
                int opt_w  = char_w * 7 + 20;
                int help_w = char_w * 4 + 20;
                int help_x = win_w - help_w - 12;

                if (st.active_menu == 1) {
                    draw_bevel_rect(dpy, back_buf, gc, &colors, file_x, cur_y + 2, file_w, mb_h - 4, colors.btn_bg, 0);
                }
                if (st.active_menu == 2) {
                    draw_bevel_rect(dpy, back_buf, gc, &colors, opt_x, cur_y + 2, opt_w, mb_h - 4, colors.btn_bg, 0);
                }
                if (st.active_menu == 3) {
                    draw_bevel_rect(dpy, back_buf, gc, &colors, help_x, cur_y + 2, help_w, mb_h - 4, colors.btn_bg, 0);
                }

                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, file_x + 10, cur_y + font_asc + 4, "File", 4);
                XDrawLine(dpy, back_buf, gc, file_x + 10, cur_y + font_asc + 6, file_x + 10 + char_w, cur_y + font_asc + 6);

                XDrawString(dpy, back_buf, gc, opt_x + 10, cur_y + font_asc + 4, "Options", 7);
                XDrawLine(dpy, back_buf, gc, opt_x + 10, cur_y + font_asc + 6, opt_x + 10 + char_w, cur_y + font_asc + 6);

                XDrawString(dpy, back_buf, gc, help_x + 10, cur_y + font_asc + 4, "Help", 4);
                XDrawLine(dpy, back_buf, gc, help_x + 10, cur_y + font_asc + 6, help_x + 10 + char_w, cur_y + font_asc + 6);

                cur_y += mb_h + 4;
            }

            /* 3. Compute heights of active Clock Parts (Date Part, Digital Part, Analog Part) */
            int avail_h = win_h - cur_y - 8;
            if (avail_h < 60) avail_h = 60;

            int date_h = 0, dig_h = 0, ana_h = 0;
            if (st.show_analog) {
                if (st.show_date) date_h = font_h + 16;
                if (st.show_digital) dig_h = font_h + 20;
                ana_h = avail_h - date_h - dig_h - (st.show_date ? 4 : 0) - (st.show_digital ? 4 : 0);
                if (ana_h < 80) ana_h = 80;
            } else {
                if (st.show_date && st.show_digital) {
                    date_h = avail_h / 2 - 2;
                    dig_h = avail_h - date_h - 4;
                } else if (st.show_date) {
                    date_h = avail_h;
                } else {
                    dig_h = avail_h;
                }
            }

            /* 3a. Render Date Part */
            if (st.show_date && date_h > 0) {
                draw_bevel_rect(dpy, back_buf, gc, &colors, 8, cur_y, win_w - 16, date_h, colors.canvas_bg, 1);
                int tw = font ? XTextWidth(font, date_str, (int)strlen(date_str)) : ((int)strlen(date_str) * char_w);
                int tx = (win_w - tw) / 2;
                int ty = cur_y + (date_h + font_asc - font_desc_px) / 2;
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, tx, ty, date_str, (int)strlen(date_str));
                cur_y += date_h + 4;
            }

            /* 3b. Render Digital Part */
            if (st.show_digital && dig_h > 0) {
                draw_bevel_rect(dpy, back_buf, gc, &colors, 8, cur_y, win_w - 16, dig_h, colors.canvas_bg, 1);
                int tw = font ? XTextWidth(font, time_str, (int)strlen(time_str)) : ((int)strlen(time_str) * char_w);
                int tx = (win_w - tw) / 2;
                int ty = cur_y + (dig_h + font_asc - font_desc_px) / 2;
                XSetForeground(dpy, gc, colors.title_bg);
                XDrawString(dpy, back_buf, gc, tx, ty, time_str, (int)strlen(time_str));
                XDrawString(dpy, back_buf, gc, tx + 1, ty, time_str, (int)strlen(time_str));

                if (st.alarm_on) {
                    int bell_r = font_h / 3 + 2;
                    int bx = win_w - 28 - (font ? XTextWidth(font, alm_str, (int)strlen(alm_str)) : (int)strlen(alm_str) * char_w);
                    if (bx > tx + tw + 16) {
                        draw_bell_icon(dpy, back_buf, gc, &colors, bx - bell_r - 4, cur_y + dig_h / 2 - 2, bell_r);
                        XSetForeground(dpy, gc, colors.canvas_fg);
                        XDrawString(dpy, back_buf, gc, bx, ty, alm_str, (int)strlen(alm_str));
                    }
                }
                cur_y += dig_h + 4;
            }

            /* 3c. Render Analog Part */
            if (st.show_analog && ana_h > 0) {
                int ax = 8, ay = cur_y, aw = win_w - 16, ah = ana_h;
                draw_bevel_rect(dpy, back_buf, gc, &colors, ax, ay, aw, ah, colors.canvas_bg, 1);

                int cx = ax + aw / 2;
                int cy = ay + ah / 2;
                int r = ((aw < ah) ? aw : ah) / 2 - 14;
                if (r < 24) r = 24;

                /* Outer 3D Circular Bezel */
                XSetForeground(dpy, gc, dial_rim);
                XFillArc(dpy, back_buf, gc, cx - r - 6, cy - r - 6,
                         (unsigned int)((r + 6) * 2), (unsigned int)((r + 6) * 2), 0, 360 * 64);
                XSetForeground(dpy, gc, colors.bevel_dark);
                XDrawArc(dpy, back_buf, gc, cx - r - 6, cy - r - 6,
                         (unsigned int)((r + 6) * 2), (unsigned int)((r + 6) * 2), 45 * 64, 180 * 64);
                XSetForeground(dpy, gc, colors.bevel_light);
                XDrawArc(dpy, back_buf, gc, cx - r - 6, cy - r - 6,
                         (unsigned int)((r + 6) * 2), (unsigned int)((r + 6) * 2), 225 * 64, 180 * 64);

                /* Inner Clock Face */
                XSetForeground(dpy, gc, colors.canvas_bg);
                XFillArc(dpy, back_buf, gc, cx - r, cy - r, (unsigned int)(r * 2), (unsigned int)(r * 2), 0, 360 * 64);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawArc(dpy, back_buf, gc, cx - r, cy - r, (unsigned int)(r * 2), (unsigned int)(r * 2), 0, 360 * 64);

                /* 60 Minute Ticks & 12 Major Hour Marks + Numerals */
                for (int m = 0; m < 60; m++) {
                    double ang = (m * 6.0 - 90.0) * 3.14159265358979323846 / 180.0;
                    double ca = cos(ang);
                    double sa = sin(ang);
                    if (m % 5 == 0) {
                        int hr_num = (m / 5 == 0) ? 12 : (m / 5);
                        int tick_len = (m % 15 == 0) ? (r / 10 + 5) : (r / 14 + 4);
                        int x1 = cx + (int)((r - tick_len) * ca);
                        int y1 = cy + (int)((r - tick_len) * sa);
                        int x2 = cx + (int)((r - 2) * ca);
                        int y2 = cy + (int)((r - 2) * sa);
                        XSetForeground(dpy, gc, colors.canvas_fg);
                        XDrawLine(dpy, back_buf, gc, x1, y1, x2, y2);
                        XDrawLine(dpy, back_buf, gc, x1 + 1, y1, x2 + 1, y2);
                        XDrawLine(dpy, back_buf, gc, x1, y1 + 1, x2, y2 + 1);

                        if (r >= 65) {
                            char num_s[8];
                            snprintf(num_s, sizeof(num_s), "%d", hr_num);
                            int nw = font ? XTextWidth(font, num_s, (int)strlen(num_s)) : ((int)strlen(num_s) * char_w);
                            double nr = r - tick_len - (font_h * 0.65) - 2;
                            int nx = cx + (int)(nr * ca) - nw / 2;
                            int ny = cy + (int)(nr * sa) + (font_asc - font_desc_px) / 2;
                            XDrawString(dpy, back_buf, gc, nx, ny, num_s, (int)strlen(num_s));
                        }
                    } else if (r >= 50) {
                        int x1 = cx + (int)((r - 5) * ca);
                        int y1 = cy + (int)((r - 5) * sa);
                        int x2 = cx + (int)((r - 2) * ca);
                        int y2 = cy + (int)((r - 2) * sa);
                        XSetForeground(dpy, gc, colors.bevel_dark);
                        XDrawLine(dpy, back_buf, gc, x1, y1, x2, y2);
                    }
                }

                /* Alarm Bell Indicator in Top-Left of Analog Canvas + Alarm Hand Marker */
                if (st.alarm_on) {
                    int br = font_h / 3 + 3;
                    draw_bell_icon(dpy, back_buf, gc, &colors, ax + 16 + br, ay + 14 + br, br);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, ax + 24 + br * 2, ay + 14 + br + font_asc / 2,
                                alm_str, (int)strlen(alm_str));

                    /* Dashed/Amber Alarm Pointer on Dial */
                    double alm_ang = (((st.alarm_hr % 12) + st.alarm_min / 60.0) * 30.0 - 90.0) * 3.14159265358979323846 / 180.0;
                    int ax2 = cx + (int)((r * 0.68) * cos(alm_ang));
                    int ay2 = cy + (int)((r * 0.68) * sin(alm_ang));
                    XSetForeground(dpy, gc, colors.accent_amber);
                    XDrawLine(dpy, back_buf, gc, cx, cy, ax2, ay2);
                }

                /* Hour Hand Polygon */
                double hr_ang = (((cur_tm.tm_hour % 12) + cur_tm.tm_min / 60.0 + cur_tm.tm_sec / 3600.0) * 30.0 - 90.0) * 3.14159265358979323846 / 180.0;
                double hr_w = (r * 0.065 > 4.0) ? (r * 0.065) : 4.0;
                draw_clock_hand_polygon(dpy, back_buf, gc, cx, cy, hr_ang, r * 0.52, r * 0.12, hr_w,
                                        navy_hand, colors.canvas_fg);

                /* Minute Hand Polygon */
                double mn_ang = ((cur_tm.tm_min + cur_tm.tm_sec / 60.0) * 6.0 - 90.0) * 3.14159265358979323846 / 180.0;
                double mn_w = (r * 0.045 > 3.0) ? (r * 0.045) : 3.0;
                draw_clock_hand_polygon(dpy, back_buf, gc, cx, cy, mn_ang, r * 0.76, r * 0.15, mn_w,
                                        colors.title_bg, colors.canvas_fg);

                /* Second Hand Sweep Needle */
                if (st.show_seconds) {
                    double sc_ang = (cur_tm.tm_sec * 6.0 - 90.0) * 3.14159265358979323846 / 180.0;
                    int sx1 = cx - (int)((r * 0.18) * cos(sc_ang));
                    int sy1 = cy - (int)((r * 0.18) * sin(sc_ang));
                    int sx2 = cx + (int)((r * 0.82) * cos(sc_ang));
                    int sy2 = cy + (int)((r * 0.82) * sin(sc_ang));
                    XSetForeground(dpy, gc, crimson_col);
                    XDrawLine(dpy, back_buf, gc, sx1, sy1, sx2, sy2);
                    XDrawLine(dpy, back_buf, gc, sx1 + 1, sy1, sx2 + 1, sy2);
                }

                /* Center Pivot Cap */
                int cap_r = (r / 18 > 4) ? (r / 18) : 4;
                XSetForeground(dpy, gc, colors.btn_bg);
                XFillArc(dpy, back_buf, gc, cx - cap_r, cy - cap_r,
                         (unsigned int)(cap_r * 2), (unsigned int)(cap_r * 2), 0, 360 * 64);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawArc(dpy, back_buf, gc, cx - cap_r, cy - cap_r,
                         (unsigned int)(cap_r * 2), (unsigned int)(cap_r * 2), 0, 360 * 64);
            }

            /* Subtle [=] menu hotspot in top-right when Menubar is hidden */
            if (!st.show_menubar) {
                int h_sz = font_h + 4;
                draw_bevel_rect(dpy, back_buf, gc, &colors, win_w - h_sz - 10, 10, h_sz, h_sz, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, win_w - h_sz - 6, 10 + font_asc, "=", 1);
            }

            /* 4. Render Active Pull-down Menu or MB3 Pop-up Menu */
            if (st.active_menu == 1) {
                int mx = 12, my = 6 + mb_h;
                int mw = char_w * 14 + 24;
                int mh = font_h + 18;
                draw_bevel_rect(dpy, back_buf, gc, &colors, mx, my, mw, mh, colors.bg_gray, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, mx + 12, my + font_asc + 6, "Exit     Ctrl+Q", 15);
            } else if (st.active_menu == 2) {
                int file_w = char_w * 4 + 20;
                int mx = 12 + file_w + 8;
                int my = 6 + mb_h;
                int row_h = font_h + 10;
                int mw = char_w * 24 + 28;
                int mh = row_h * 5 + 16;
                if (mx + mw > win_w - 6) mx = win_w - mw - 6;
                draw_bevel_rect(dpy, back_buf, gc, &colors, mx, my, mw, mh, colors.bg_gray, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, mx + 12, my + font_asc + 6,             "Display...          Ctrl+D", 26);
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h + font_asc + 6,     "Alarm...            Ctrl+A", 26);
                XDrawLine(dpy, back_buf, gc, mx + 6, my + row_h * 2 + 4, mx + mw - 6, my + row_h * 2 + 4);
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 2 + font_asc + 8, "Sync System Time    Ctrl+T", 26);
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 3 + font_asc + 8, "Save Options        Ctrl+S", 26);
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 4 + font_asc + 8, "Restore System Options", 22);
            } else if (st.active_menu == 3) {
                int mw = char_w * 18 + 24;
                int mx = win_w - mw - 12;
                int my = 6 + mb_h;
                int row_h = font_h + 10;
                int mh = row_h * 2 + 12;
                draw_bevel_rect(dpy, back_buf, gc, &colors, mx, my, mw, mh, colors.bg_gray, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, mx + 12, my + font_asc + 6,         "Overview...     F1", 18);
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h + font_asc + 6, "About Clock...", 14);
            } else if (st.active_menu == 4) {
                int row_h = font_h + 9;
                int mw = char_w * 23 + 32;
                int mh = row_h * 9 + 14;
                int mx = st.popup_x;
                int my = st.popup_y;
                if (mx + mw > win_w - 8) mx = win_w - mw - 8;
                if (my + mh > win_h - 8) my = win_h - mh - 8;
                if (mx < 8) mx = 8;
                if (my < 8) my = 8;
                draw_bevel_rect(dpy, back_buf, gc, &colors, mx, my, mw, mh, colors.bg_gray, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                char buf[64];
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 0 + font_asc + 5, "Display...", 10);
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 1 + font_asc + 5, "Alarm...", 8);
                snprintf(buf, sizeof(buf), "[%c] Analog Part", st.show_analog ? 'X' : ' ');
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 2 + font_asc + 5, buf, (int)strlen(buf));
                snprintf(buf, sizeof(buf), "[%c] Digital Part", st.show_digital ? 'X' : ' ');
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 3 + font_asc + 5, buf, (int)strlen(buf));
                snprintf(buf, sizeof(buf), "[%c] Date Part", st.show_date ? 'X' : ' ');
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 4 + font_asc + 5, buf, (int)strlen(buf));
                snprintf(buf, sizeof(buf), "[%c] Menubar", st.show_menubar ? 'X' : ' ');
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 5 + font_asc + 5, buf, (int)strlen(buf));
                snprintf(buf, sizeof(buf), "[%c] Military Time", st.military_time ? 'X' : ' ');
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 6 + font_asc + 5, buf, (int)strlen(buf));
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 7 + font_asc + 5, "Save Options", 12);
                XDrawString(dpy, back_buf, gc, mx + 12, my + row_h * 8 + font_asc + 5, "Exit", 4);
            }

            /* 5. Render Modal/Modeless OSF/Motif Dialog Boxes */
            if (st.active_dialog == 1) {
                int dw = win_w - 32;
                int dh = font_h * 12 + 76;
                if (dw < 280) dw = win_w - 12;
                if (dh > win_h - 16) dh = win_h - 16;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;

                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                int th = font_h + 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, th, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 4 + font_asc + 2, "Clock: Display Options", 22);

                int box_sz = font_h;
                int r_step = (dh - th - (font_h + 26)) / 7;
                if (r_step < font_h + 4) r_step = font_h + 4;
                int ry = dy + th + 10;

                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 0, box_sz, st.dlg_analog,   "Analog Part", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 1, box_sz, st.dlg_digital,  "Digital Part", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 2, box_sz, st.dlg_date,     "Date Part", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 3, box_sz, st.dlg_menubar,  "Menubar", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 4, box_sz, st.dlg_military, "Military Time (24-Hr)", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 5, box_sz, st.dlg_seconds,  "Second Hand", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 6, box_sz, st.dlg_chime,    "Hourly Chime", font_asc);

                int bw = (dw - 48) / 3;
                int bh = font_h + 12;
                int by = dy + dh - bh - 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 12,            by, bw, bh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 24 + bw,       by, bw, bh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 36 + bw * 2,   by, bw, bh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 12 + (bw - char_w * 2) / 2,          by + font_asc + 4, "OK", 2);
                XDrawString(dpy, back_buf, gc, dx + 24 + bw + (bw - char_w * 5) / 2,     by + font_asc + 4, "Apply", 5);
                XDrawString(dpy, back_buf, gc, dx + 36 + bw * 2 + (bw - char_w * 6) / 2, by + font_asc + 4, "Cancel", 6);
            } else if (st.active_dialog == 2) {
                int dw = win_w - 24;
                int dh = font_h * 12 + 80;
                if (dw < 290) dw = win_w - 10;
                if (dh > win_h - 16) dh = win_h - 16;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;

                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                int th = font_h + 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, th, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 4 + font_asc + 2, "Clock: Alarm Options", 20);

                int box_sz = font_h;
                int r_step = (dh - th - (font_h + 26)) / 7;
                if (r_step < font_h + 4) r_step = font_h + 4;
                int ry = dy + th + 10;

                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 0, box_sz, st.dlg_alm_on,     "Alarm On", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 1, box_sz, st.dlg_alm_repeat, "Repeat Daily", font_asc);
                draw_motif_checkbox(dpy, back_buf, gc, &colors, dx + 16, ry + r_step * 2, box_sz, st.dlg_alm_bell,   "Keyboard Bell", font_asc);

                int hy = ry + r_step * 3;
                int btn_s = font_h + 8;
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 16, hy + font_asc + 2, "Hour:", 5);
                int hx = dx + 16 + char_w * 7;
                draw_bevel_rect(dpy, back_buf, gc, &colors, hx, hy, btn_s, btn_s, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, hx + 6, hy + font_asc + 2, "-", 1);

                draw_bevel_rect(dpy, back_buf, gc, &colors, hx + btn_s + 4, hy, char_w * 4 + 12, btn_s, colors.cmd_bg, 1);
                char hbuf[16];
                snprintf(hbuf, sizeof(hbuf), "%02d", st.dlg_alm_hr);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, hx + btn_s + 12, hy + font_asc + 2, hbuf, (int)strlen(hbuf));

                int hplus_x = hx + btn_s + char_w * 4 + 20;
                draw_bevel_rect(dpy, back_buf, gc, &colors, hplus_x, hy, btn_s, btn_s, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, hplus_x + 6, hy + font_asc + 2, "+", 1);

                int test_x = hplus_x + btn_s + 12;
                int test_w = dw - (test_x - dx) - 12;
                if (test_w >= char_w * 4 + 12) {
                    draw_bevel_rect(dpy, back_buf, gc, &colors, test_x, hy, test_w, btn_s, colors.btn_bg, 0);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, test_x + 8, hy + font_asc + 2, "Test", 4);
                }

                int my_row = ry + r_step * 4;
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 16, my_row + font_asc + 2, "Min :", 5);
                draw_bevel_rect(dpy, back_buf, gc, &colors, hx, my_row, btn_s, btn_s, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, hx + 6, my_row + font_asc + 2, "-", 1);

                draw_bevel_rect(dpy, back_buf, gc, &colors, hx + btn_s + 4, my_row, char_w * 4 + 12, btn_s, colors.cmd_bg, 1);
                char mbuf[16];
                snprintf(mbuf, sizeof(mbuf), "%02d", st.dlg_alm_min);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, hx + btn_s + 12, my_row + font_asc + 2, mbuf, (int)strlen(mbuf));

                draw_bevel_rect(dpy, back_buf, gc, &colors, hplus_x, my_row, btn_s, btn_s, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, hplus_x + 6, my_row + font_asc + 2, "+", 1);

                int msg_lbl_y = ry + r_step * 5;
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 16, msg_lbl_y + font_asc, "Alarm Message (type to edit):", 29);

                int msg_box_y = ry + r_step * 6 - 2;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 14, msg_box_y, dw - 28, font_h + 10, colors.cmd_bg, 1);
                char msg_disp[140];
                snprintf(msg_disp, sizeof(msg_disp), "%s_", st.dlg_alm_msg);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 20, msg_box_y + font_asc + 2, msg_disp, (int)strlen(msg_disp));

                int bw = (dw - 48) / 3;
                int bh = font_h + 12;
                int by = dy + dh - bh - 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 12,            by, bw, bh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 24 + bw,       by, bw, bh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 36 + bw * 2,   by, bw, bh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 12 + (bw - char_w * 2) / 2,          by + font_asc + 4, "OK", 2);
                XDrawString(dpy, back_buf, gc, dx + 24 + bw + (bw - char_w * 5) / 2,     by + font_asc + 4, "Apply", 5);
                XDrawString(dpy, back_buf, gc, dx + 36 + bw * 2 + (bw - char_w * 6) / 2, by + font_asc + 4, "Cancel", 6);
            } else if (st.active_dialog == 3) {
                int dw = win_w - 28;
                int dh = font_h * 9 + 60;
                if (dh > win_h - 20) dh = win_h - 20;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;

                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                int th = font_h + 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, th, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                const char* htitle = st.help_mode ? "About DECwindows Clock" : "DECwindows Clock Overview";
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 4 + font_asc + 2, htitle, (int)strlen(htitle));

                XSetForeground(dpy, gc, colors.canvas_fg);
                int ty = dy + th + font_asc + 12;
                int lh = font_h + 4;
                if (st.help_mode) {
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 0, "DECwindows Clock (DECW$CLOCK / dxclock)", 39);
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 1, "Version 3.0 - OSF/Motif 1.1 Desktop Suite", 41);
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 2, "Digital Equipment Corporation", 29);
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 3, "VAX/VMS, ULTRIX & DEC OSF/1", 27);
                } else {
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 0, "- Options -> Display: Toggle Analog,", 36);
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 1, "  Digital, Date, Menubar, Military.", 35);
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 2, "- Options -> Alarm: Set Alarm & Msg.", 36);
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 3, "- Right-Click (MB3): Pop-up Menu.", 33);
                    XDrawString(dpy, back_buf, gc, dx + 16, ty + lh * 4, "- Keys: F10/F11 Resize, Ctrl+D/A.", 33);
                }

                int bw = char_w * 8 + 20;
                int bh = font_h + 12;
                int bx = dx + (dw - bw) / 2;
                int by = dy + dh - bh - 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, by, bw, bh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + (bw - char_w * 2) / 2, by + font_asc + 4, "OK", 2);
            }

            /* 6. Render Alarm Triggered Notification Dialog Overlay */
            if (st.alarm_triggered) {
                int dw = win_w - 28;
                int dh = font_h * 7 + 56;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;

                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                int th = font_h + 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, th, crimson_col, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 4 + font_asc + 2, "DECwindows Clock: Alarm!", 24);

                int br = font_h / 2 + 4;
                draw_bell_icon(dpy, back_buf, gc, &colors, dx + 24 + br, dy + th + 20 + br, br);

                XSetForeground(dpy, gc, colors.canvas_fg);
                char atime_line[96];
                snprintf(atime_line, sizeof(atime_line), "Alarm Time: %s", alm_str);
                XDrawString(dpy, back_buf, gc, dx + 36 + br * 2, dy + th + font_asc + 14, atime_line, (int)strlen(atime_line));
                XDrawString(dpy, back_buf, gc, dx + 18, dy + th + font_h * 2 + 24, st.alarm_msg, (int)strlen(st.alarm_msg));

                int bw = char_w * 10 + 24;
                int bh = font_h + 12;
                int bx = dx + (dw - bw) / 2;
                int by = dy + dh - bh - 10;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, by, bw, bh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + (bw - char_w * 2) / 2, by + font_asc + 4, "OK", 2);
            }

            /* Atomic blit of off-screen double-buffer Pixmap to live Window */
            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                XEvent bev;
                memset(&bev, 0, sizeof(bev));
                bev.xbutton.type = ButtonPress;
                bev.xbutton.display = dpy;
                bev.xbutton.window = win;
                bev.xbutton.x = 20;
                bev.xbutton.y = 14;
                bev.xbutton.button = Button1;
                XSendEvent(dpy, win, False, ButtonPressMask, &bev);
                XFlush(dpy);
            }
        }

        if (autoclose_ms > 0 && exposed_once) {
            struct timeval now_tv;
            gettimeofday(&now_tv, NULL);
            long elapsed_ms = (now_tv.tv_sec - start_tv.tv_sec) * 1000L +
                              (now_tv.tv_usec - start_tv.tv_usec) / 1000L;
            if (elapsed_ms >= autoclose_ms) {
                running = 0;
                break;
            }
        }

        if (running) {
            int xfd = ConnectionNumber(dpy);
            fd_set fds;
            FD_ZERO(&fds);
            FD_SET(xfd, &fds);
            struct timeval tv;
            tv.tv_sec = 0;
            tv.tv_usec = 100000; /* 100ms tick check */
            select(xfd + 1, &fds, NULL, NULL, &tv);
        }
    }

    {
        char info[256];
        decw_x11_probe_display(dname, info, sizeof(info));
        int active_parts = st.show_analog + st.show_digital + st.show_date;
        printf("[DECwindows X11 Engine] Window '%s' (%s) rendered (%d parts, 3 Motif buttons, Font: %s) | %s\n",
               title, cfg->app_id[0] ? cfg->app_id : "clock", active_parts, font_desc, info);
        fflush(stdout);
    }

    XFreePixmap(dpy, back_buf);
    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}

#include "decw_gui_group1.h"
#include "decw_gui_group2.h"
#include "decw_gui_group3.h"

int decw_x11_run_window(const DecwWindowConfig* cfg) {
    if (!cfg) return -1;

    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");

    /* Determine whether to detach from the active terminal (default: detach unless
     * running with --foreground / DECW_X11_FOREGROUND=1 or automated test flags). */
    int autoclose_ms = cfg->autoclose_ms;
    const char* env_ac = getenv("DECW_X11_AUTOCLOSE_MS");
    if (autoclose_ms <= 0 && env_ac && env_ac[0]) {
        autoclose_ms = atoi(env_ac);
    }
    const char* env_fg = getenv("DECW_X11_FOREGROUND");
    int force_fg = (env_fg && env_fg[0] && strcmp(env_fg, "0") != 0);
    const char* env_detach = getenv("DECW_X11_FORCE_DETACH");
    int force_detach = (env_detach && env_detach[0] && strcmp(env_detach, "0") != 0);

    int should_detach = force_detach || (!force_fg && autoclose_ms <= 0 && !cfg->verify_only && !cfg->test_interact);
    if (should_detach) {
        char info[256];
        if (decw_x11_probe_display(dname, info, sizeof(info)) != 0) {
            fprintf(stderr, "%%DECW-E-NOX11, unable to open X11 display '%s'\n", dname ? dname : "(null)");
            return 1;
        }
        fflush(NULL);
        pid_t pid = fork();
        if (pid > 0) {
            const char* title = cfg->title[0] ? cfg->title : "DECwindows Motif Application";
            printf("[DECwindows X11 Engine] Window '%s' (%s) detached from terminal (PID %d) | %s\n",
                   title, cfg->app_id[0] ? cfg->app_id : "decw", (int)pid, info);
            fflush(stdout);
            return 0;
        } else if (pid == 0) {
            setsid();
            int devnull = open("/dev/null", O_RDWR);
            if (devnull >= 0) {
                dup2(devnull, STDIN_FILENO);
                dup2(devnull, STDOUT_FILENO);
                dup2(devnull, STDERR_FILENO);
                if (devnull > STDERR_FILENO) {
                    close(devnull);
                }
            }
        }
    }

    if (strcasecmp(cfg->app_id, "clock") == 0 || strcasecmp(cfg->app_id, "dxclock") == 0) {
        return run_clock_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "calculator") == 0 || strcasecmp(cfg->app_id, "dxcalc") == 0) {
        return run_calculator_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "calendar") == 0 || strcasecmp(cfg->app_id, "dxcalendar") == 0) {
        return run_calendar_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "cardfiler") == 0 || strcasecmp(cfg->app_id, "dxcardfiler") == 0) {
        return run_cardfiler_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "notepad") == 0 || strcasecmp(cfg->app_id, "dxnotepad") == 0) {
        return run_notepad_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "fileview") == 0 || strcasecmp(cfg->app_id, "dxfileview") == 0) {
        return run_fileview_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "dxmail") == 0 || strcasecmp(cfg->app_id, "decwinmail") == 0 || strcasecmp(cfg->app_id, "mail") == 0) {
        return run_dxmail_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "bookreader") == 0 || strcasecmp(cfg->app_id, "dxbook") == 0) {
        return run_bookreader_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "cdaviewer") == 0 || strcasecmp(cfg->app_id, "dxvdoc") == 0) {
        return run_cdaviewer_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "decterm") == 0 || strcasecmp(cfg->app_id, "dxterm") == 0) {
        return run_decterm_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "decsound") == 0 || strcasecmp(cfg->app_id, "dxsound") == 0) {
        return run_decsound_window(cfg);
    }
    if (strcasecmp(cfg->app_id, "decwindows") == 0 || strcasecmp(cfg->app_id, "dxsession") == 0 || strcasecmp(cfg->app_id, "decwx11") == 0) {
        return run_session_window(cfg);
    }

    Display* dpy = XOpenDisplay(dname);
    if (!dpy) {
        fprintf(stderr, "%%DECW-E-NOX11, unable to open X11 display '%s'\n", dname ? dname : "(null)");
        return 1;
    }

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, cfg->app_id, &colors);

    /* Determine initial font scale: default to 3 (24px Large) on HiDPI >=2560px displays, or 2 (20px) otherwise */
    int font_scale = (disp_w >= 2560) ? 3 : 2;
    char custom_xlfd[128] = "";

    const char* env_fsize = getenv("DECW_FONT_SIZE");
    const char* env_fx11 = getenv("DECW_X11_FONT");
    const char* env_scale = getenv("DECW_SCALE");

    if (env_scale && env_scale[0]) {
        int s = parse_font_spec_to_scale(env_scale, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (env_fsize && env_fsize[0]) {
        int s = parse_font_spec_to_scale(env_fsize, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (env_fx11 && env_fx11[0]) {
        int s = parse_font_spec_to_scale(env_fx11, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (cfg->font_scale >= 1 && cfg->font_scale <= 6) {
        font_scale = cfg->font_scale;
    }
    if (cfg->font_spec[0]) {
        int s = parse_font_spec_to_scale(cfg->font_spec, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }

    char font_desc[96] = "";
    int rec_w = 1220, rec_h = 880;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);

    int win_w = (cfg->width >= 400) ? cfg->width : rec_w;
    int win_h = (cfg->height >= 300) ? cfg->height : rec_h;
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window root = RootWindow(dpy, screen);
    int depth = DefaultDepth(dpy, screen);
    Window win = XCreateSimpleWindow(dpy, root, 60, 60, (unsigned int)win_w, (unsigned int)win_h,
                                     2, colors.bevel_dark, colors.bg_gray);
    /* Disable X server automatic background erase on Expose/Configure to eliminate flicker */
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Motif Application";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, cfg->app_id[0] ? cfg->app_id : "decwindows");

    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);

    Atom decw_atom = XInternAtom(dpy, "_DECW_MOTIF_APP_ID", False);
    if (cfg->app_id[0]) {
        XChangeProperty(dpy, win, decw_atom, XA_STRING, 8, PropModeReplace,
                        (const unsigned char*)cfg->app_id, (int)strlen(cfg->app_id));
    }

    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) {
        XSetFont(dpy, gc, font->fid);
    }

    int buf_w = win_w;
    int buf_h = win_h;
    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)buf_w, (unsigned int)buf_h, (unsigned int)depth);

    char lines[DECW_MAX_LINES][DECW_LINE_LEN];
    int line_count = decw_x11_load_frame(cfg->frame_path, lines, DECW_MAX_LINES);
    if (line_count == 0 && cfg->exec_bin[0]) {
        char st[128];
        decw_x11_exec_app_cmd(cfg, "SHOW", st, sizeof(st));
        line_count = decw_x11_load_frame(cfg->frame_path, lines, DECW_MAX_LINES);
    }

    DecwButton buttons[DECW_MAX_BUTTONS];
    int num_buttons = 0;
    setup_app_buttons(cfg->app_id, buttons, &num_buttons);

    char cmd_input[192] = "";
    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg),
             "Font: %s | Click [Font -] / [Font +] or press F10/F11 (PageDown/PageUp) to resize",
             font_desc);

    XMapWindow(dpy, win);
    XFlush(dpy);

    if (cfg->verify_only && autoclose_ms <= 0) {
        autoclose_ms = 120;
    }

    struct timeval start_tv;
    gettimeofday(&start_tv, NULL);
    int exposed_once = 0;
    int need_redraw = 0;
    int sent_synth = 0;
    int running = 1;

    while (running) {
        while (XPending(dpy) > 0) {
            XEvent ev;
            XNextEvent(dpy, &ev);

            if (ev.type == ConfigureNotify) {
                if (ev.xconfigure.width != win_w || ev.xconfigure.height != win_h) {
                    win_w = ev.xconfigure.width;
                    win_h = ev.xconfigure.height;
                    need_redraw = 1;
                }
            } else if (ev.type == Expose && ev.xexpose.count == 0) {
                exposed_once = 1;
                need_redraw = 1;
            } else if (ev.type == ButtonPress) {
                int mx = ev.xbutton.x;
                int my = ev.xbutton.y;
                for (int b = 0; b < num_buttons; b++) {
                    if (mx >= buttons[b].x && mx <= buttons[b].x + buttons[b].w &&
                        my >= buttons[b].y && my <= buttons[b].y + buttons[b].h) {
                        buttons[b].pressed = 1;
                        need_redraw = 1;
                    }
                }
            } else if (ev.type == ButtonRelease) {
                int mx = ev.xbutton.x;
                int my = ev.xbutton.y;
                for (int b = 0; b < num_buttons; b++) {
                    int was_pressed = buttons[b].pressed;
                    buttons[b].pressed = 0;
                    if (was_pressed) need_redraw = 1;
                    if (was_pressed &&
                        mx >= buttons[b].x && mx <= buttons[b].x + buttons[b].w &&
                        my >= buttons[b].y && my <= buttons[b].y + buttons[b].h) {
                        if (strcmp(buttons[b].command, "__QUIT__") == 0) {
                            running = 0;
                        } else if (strcmp(buttons[b].command, "__FONT_DEC__") == 0 ||
                                   strcmp(buttons[b].command, "__FONT_INC__") == 0) {
                            if (strcmp(buttons[b].command, "__FONT_DEC__") == 0 && font_scale > 1) font_scale--;
                            if (strcmp(buttons[b].command, "__FONT_INC__") == 0 && font_scale < 6) font_scale++;
                            custom_xlfd[0] = '\0';
                            if (font) XFreeFont(dpy, font);
                            font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                            if (font) XSetFont(dpy, gc, font->fid);
                            win_w = (rec_w > disp_w - 80) ? disp_w - 80 : rec_w;
                            win_h = (rec_h > disp_h - 80) ? disp_h - 80 : rec_h;
                            XResizeWindow(dpy, win, (unsigned int)win_w, (unsigned int)win_h);
                            snprintf(status_msg, sizeof(status_msg), "Resized X11 font to %s (%dx%d)", font_desc, win_w, win_h);
                            need_redraw = 1;
                        } else {
                            decw_x11_exec_app_cmd(cfg, buttons[b].command, status_msg, sizeof(status_msg));
                            line_count = decw_x11_load_frame(cfg->frame_path, lines, DECW_MAX_LINES);
                            need_redraw = 1;
                        }
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                int n = XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                kbuf[n] = '\0';

                if (ks == XK_Escape) {
                    running = 0;
                } else if (ks == XK_F10 || ks == XK_Next || ((ev.xkey.state & ControlMask) && (ks == XK_minus || ks == XK_underscore))) {
                    if (font_scale > 1) font_scale--;
                    custom_xlfd[0] = '\0';
                    if (font) XFreeFont(dpy, font);
                    font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                    if (font) XSetFont(dpy, gc, font->fid);
                    win_w = (rec_w > disp_w - 80) ? disp_w - 80 : rec_w;
                    win_h = (rec_h > disp_h - 80) ? disp_h - 80 : rec_h;
                    XResizeWindow(dpy, win, (unsigned int)win_w, (unsigned int)win_h);
                    snprintf(status_msg, sizeof(status_msg), "Resized X11 font to %s (%dx%d)", font_desc, win_w, win_h);
                    need_redraw = 1;
                } else if (ks == XK_F11 || ks == XK_Prior || ((ev.xkey.state & ControlMask) && (ks == XK_equal || ks == XK_plus))) {
                    if (font_scale < 6) font_scale++;
                    custom_xlfd[0] = '\0';
                    if (font) XFreeFont(dpy, font);
                    font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                    if (font) XSetFont(dpy, gc, font->fid);
                    win_w = (rec_w > disp_w - 80) ? disp_w - 80 : rec_w;
                    win_h = (rec_h > disp_h - 80) ? disp_h - 80 : rec_h;
                    XResizeWindow(dpy, win, (unsigned int)win_w, (unsigned int)win_h);
                    snprintf(status_msg, sizeof(status_msg), "Resized X11 font to %s (%dx%d)", font_desc, win_w, win_h);
                    need_redraw = 1;
                } else if (ks == XK_Return || ks == XK_KP_Enter) {
                    if (strcasecmp(cmd_input, "EXIT") == 0 || strcasecmp(cmd_input, "QUIT") == 0) {
                        running = 0;
                    } else if (strncasecmp(cmd_input, "FONT ", 5) == 0 || strncasecmp(cmd_input, "SCALE ", 6) == 0) {
                        const char* arg = strchr(cmd_input, ' ');
                        while (arg && *arg == ' ') arg++;
                        if (arg && (strcmp(arg, "+") == 0 || strcasecmp(arg, "UP") == 0)) {
                            if (font_scale < 6) font_scale++;
                            custom_xlfd[0] = '\0';
                        } else if (arg && (strcmp(arg, "-") == 0 || strcasecmp(arg, "DOWN") == 0)) {
                            if (font_scale > 1) font_scale--;
                            custom_xlfd[0] = '\0';
                        } else if (arg && *arg) {
                            int s = parse_font_spec_to_scale(arg, custom_xlfd, sizeof(custom_xlfd));
                            if (s > 0) {
                                font_scale = s;
                                custom_xlfd[0] = '\0';
                            }
                        }
                        if (font) XFreeFont(dpy, font);
                        font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                        if (font) XSetFont(dpy, gc, font->fid);
                        win_w = (rec_w > disp_w - 80) ? disp_w - 80 : rec_w;
                        win_h = (rec_h > disp_h - 80) ? disp_h - 80 : rec_h;
                        XResizeWindow(dpy, win, (unsigned int)win_w, (unsigned int)win_h);
                        snprintf(status_msg, sizeof(status_msg), "Resized X11 font to %s (%dx%d)", font_desc, win_w, win_h);
                        cmd_input[0] = '\0';
                        need_redraw = 1;
                    } else if (cmd_input[0]) {
                        decw_x11_exec_app_cmd(cfg, cmd_input, status_msg, sizeof(status_msg));
                        line_count = decw_x11_load_frame(cfg->frame_path, lines, DECW_MAX_LINES);
                        cmd_input[0] = '\0';
                        need_redraw = 1;
                    }
                } else if (ks == XK_BackSpace || ks == XK_Delete) {
                    size_t clen = strlen(cmd_input);
                    if (clen > 0) {
                        cmd_input[clen - 1] = '\0';
                        need_redraw = 1;
                    }
                } else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127) {
                    size_t clen = strlen(cmd_input);
                    if (clen + 1 < sizeof(cmd_input)) {
                        cmd_input[clen] = kbuf[0];
                        cmd_input[clen + 1] = '\0';
                        need_redraw = 1;
                    }
                }
            } else if (ev.type == ClientMessage) {
                if ((Atom)ev.xclient.data.l[0] == wm_delete) {
                    running = 0;
                }
            }
        }

        if (running && exposed_once && need_redraw) {
            need_redraw = 0;
            if (win_w != buf_w || win_h != buf_h) {
                XFreePixmap(dpy, back_buf);
                buf_w = (win_w > 1) ? win_w : 1;
                buf_h = (win_h > 1) ? win_h : 1;
                back_buf = XCreatePixmap(dpy, win, (unsigned int)buf_w, (unsigned int)buf_h, (unsigned int)depth);
            }

            int font_asc = font ? font->ascent : 14;
            int font_desc_px = font ? font->descent : 4;
            int font_h = font_asc + font_desc_px;
            if (font_h < 14) font_h = 14;
            int char_w = (font && font->max_bounds.width > 6) ? font->max_bounds.width : (font_h / 2 + 2);

            int title_h = font_h + 14;
            int tb_y = title_h + 12;
            int btn_h = font_h + 14;
            int btn_w = char_w * 10 + 14;
            if (btn_w * num_buttons + 60 > win_w) {
                btn_w = (win_w - 64) / num_buttons - 6;
                if (btn_w < 64) btn_w = 64;
            }

            /* 1. Outer 3D Motif Frame */
            draw_bevel_rect(dpy, back_buf, gc, &colors, 0, 0, win_w, win_h, colors.bg_gray, 0);

            /* 2. DECwindows Title Bar */
            draw_bevel_rect(dpy, back_buf, gc, &colors, 6, 6, win_w - 12, title_h, colors.title_bg, 0);
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, 9, title_h - 4, title_h - 6, colors.btn_bg, 0);
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 15, 9 + font_asc + 2, "=", 1);

            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, 18 + title_h, 9 + font_asc + 2, title, (int)strlen(title));

            /* Minimize & Maximize Motif buttons */
            draw_bevel_rect(dpy, back_buf, gc, &colors, win_w - (title_h * 2 + 6), 9, title_h - 6, title_h - 6, colors.btn_bg, 0);
            draw_bevel_rect(dpy, back_buf, gc, &colors, win_w - (title_h + 2), 9, title_h - 6, title_h - 6, colors.btn_bg, 0);
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, win_w - (title_h * 2 - 2), 9 + font_asc + 2, "_", 1);
            XDrawString(dpy, back_buf, gc, win_w - (title_h - 6), 9 + font_asc + 2, "O", 1);

            /* 3. Interactive Motif 3D PushButton Toolbar + X11 Vector Telemetry Widget */
            for (int b = 0; b < num_buttons; b++) {
                buttons[b].x = 8 + b * (btn_w + 6);
                buttons[b].y = tb_y;
                buttons[b].w = btn_w;
                buttons[b].h = btn_h;
                draw_bevel_rect(dpy, back_buf, gc, &colors,
                                buttons[b].x, buttons[b].y, buttons[b].w, buttons[b].h,
                                colors.btn_bg, buttons[b].pressed);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc,
                            buttons[b].x + 8, buttons[b].y + font_asc + 5,
                            buttons[b].label, (int)strlen(buttons[b].label));
            }

            int vec_x = 8 + num_buttons * (btn_w + 6) + 4;
            int vec_w = win_w - vec_x - 8;
            if (vec_w >= 110) {
                draw_app_vector_widget(dpy, back_buf, gc, &colors, cfg->app_id, vec_x, tb_y, vec_w, btn_h, font_asc);
            }

            /* 4. Main Sunken 3D Application Viewport Canvas */
            int cmd_box_h = font_h + 14;
            int st_box_h = font_h + 12;
            int canvas_y = tb_y + btn_h + 8;
            int canvas_h = win_h - canvas_y - cmd_box_h - st_box_h - 22;
            if (canvas_h < 120) canvas_h = 120;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 8, canvas_y, win_w - 16, canvas_h, colors.canvas_bg, 1);

            XSetForeground(dpy, gc, colors.canvas_fg);
            int line_h = font_h + 3;
            int max_vis = (canvas_h - 14) / line_h;
            for (int i = 0; i < line_count && i < max_vis; i++) {
                XDrawString(dpy, back_buf, gc, 18, canvas_y + font_asc + 8 + i * line_h,
                            lines[i], (int)strlen(lines[i]));
            }

            /* 5. Sunken Motif XmTextField Command Entry Box */
            int cmd_y = canvas_y + canvas_h + 6;
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 10, cmd_y + font_asc + 5, "DECW Cmd>", 9);

            int box_x = 16 + char_w * 10;
            int box_w = win_w - box_x - 10;
            draw_bevel_rect(dpy, back_buf, gc, &colors, box_x, cmd_y, box_w, cmd_box_h, colors.cmd_bg, 1);
            char prompt_disp[220];
            snprintf(prompt_disp, sizeof(prompt_disp), "%s_", cmd_input);
            XSetForeground(dpy, gc, BlackPixel(dpy, screen));
            XDrawString(dpy, back_buf, gc, box_x + 8, cmd_y + font_asc + 5, prompt_disp, (int)strlen(prompt_disp));

            /* 6. Bottom Status Bar */
            int st_y = cmd_y + cmd_box_h + 6;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 8, st_y, win_w - 16, st_box_h, colors.bg_gray, 1);
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 16, st_y + font_asc + 4, status_msg, (int)strlen(status_msg));

            /* Atomic double-buffer blit to live window */
            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth && num_buttons >= 2) {
                sent_synth = 1;
                XEvent bev;
                memset(&bev, 0, sizeof(bev));
                bev.xbutton.type = ButtonPress;
                bev.xbutton.display = dpy;
                bev.xbutton.window = win;
                bev.xbutton.x = buttons[1].x + 10;
                bev.xbutton.y = buttons[1].y + 10;
                bev.xbutton.button = Button1;
                XSendEvent(dpy, win, False, ButtonPressMask, &bev);
                bev.xbutton.type = ButtonRelease;
                XSendEvent(dpy, win, False, ButtonReleaseMask, &bev);
                XFlush(dpy);
            }
        }

        if (autoclose_ms > 0 && exposed_once) {
            struct timeval now_tv;
            gettimeofday(&now_tv, NULL);
            long elapsed_ms = (now_tv.tv_sec - start_tv.tv_sec) * 1000L +
                              (now_tv.tv_usec - start_tv.tv_usec) / 1000L;
            if (elapsed_ms >= autoclose_ms) {
                running = 0;
                break;
            }
        }

        if (running) {
            int xfd = ConnectionNumber(dpy);
            fd_set fds;
            FD_ZERO(&fds);
            FD_SET(xfd, &fds);
            struct timeval tv;
            tv.tv_sec = 0;
            tv.tv_usec = 30000; /* 30ms poll slice */
            select(xfd + 1, &fds, NULL, NULL, &tv);
        }
    }

    {
        char info[256];
        decw_x11_probe_display(dname, info, sizeof(info));
        printf("[DECwindows X11 Engine] Window '%s' (%s) rendered (%d lines, %d Motif buttons, Font: %s) | %s\n",
               title, cfg->app_id[0] ? cfg->app_id : "decw", line_count, num_buttons, font_desc, info);
        fflush(stdout);
    }

    XFreePixmap(dpy, back_buf);
    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}
