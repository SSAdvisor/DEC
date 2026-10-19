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
#include <unistd.h>
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

    if (app_id && (strcasecmp(app_id, "decterm") == 0 || strcasecmp(app_id, "dxterm") == 0)) {
        c->canvas_bg = alloc_color(dpy, screen, "#121820", black);
        c->canvas_fg = alloc_color(dpy, screen, "#33FF66", white);
    } else {
        c->canvas_bg = alloc_color(dpy, screen, "#F6F5F0", white);
        c->canvas_fg = alloc_color(dpy, screen, "#141820", black);
    }
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
    if (!cfg->state_path[0]) {
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

int decw_x11_run_window(const DecwWindowConfig* cfg) {
    if (!cfg) return -1;

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
    Window win = XCreateSimpleWindow(dpy, root, 60, 60, (unsigned int)win_w, (unsigned int)win_h,
                                     2, colors.bevel_dark, colors.bg_gray);

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

    while (running) {
        while (XPending(dpy) > 0) {
            XEvent ev;
            XNextEvent(dpy, &ev);

            if (ev.type == ConfigureNotify) {
                win_w = ev.xconfigure.width;
                win_h = ev.xconfigure.height;
            } else if (ev.type == Expose && ev.xexpose.count == 0) {
                exposed_once = 1;
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
                draw_bevel_rect(dpy, win, gc, &colors, 0, 0, win_w, win_h, colors.bg_gray, 0);

                /* 2. DECwindows Title Bar */
                draw_bevel_rect(dpy, win, gc, &colors, 6, 6, win_w - 12, title_h, colors.title_bg, 0);
                draw_bevel_rect(dpy, win, gc, &colors, 10, 9, title_h - 4, title_h - 6, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, win, gc, 15, 9 + font_asc + 2, "=", 1);

                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, win, gc, 18 + title_h, 9 + font_asc + 2, title, (int)strlen(title));

                /* Minimize & Maximize Motif buttons */
                draw_bevel_rect(dpy, win, gc, &colors, win_w - (title_h * 2 + 6), 9, title_h - 6, title_h - 6, colors.btn_bg, 0);
                draw_bevel_rect(dpy, win, gc, &colors, win_w - (title_h + 2), 9, title_h - 6, title_h - 6, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, win, gc, win_w - (title_h * 2 - 2), 9 + font_asc + 2, "_", 1);
                XDrawString(dpy, win, gc, win_w - (title_h - 6), 9 + font_asc + 2, "O", 1);

                /* 3. Interactive Motif 3D PushButton Toolbar + X11 Vector Telemetry Widget */
                for (int b = 0; b < num_buttons; b++) {
                    buttons[b].x = 8 + b * (btn_w + 6);
                    buttons[b].y = tb_y;
                    buttons[b].w = btn_w;
                    buttons[b].h = btn_h;
                    draw_bevel_rect(dpy, win, gc, &colors,
                                    buttons[b].x, buttons[b].y, buttons[b].w, buttons[b].h,
                                    colors.btn_bg, buttons[b].pressed);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, win, gc,
                                buttons[b].x + 8, buttons[b].y + font_asc + 5,
                                buttons[b].label, (int)strlen(buttons[b].label));
                }

                int vec_x = 8 + num_buttons * (btn_w + 6) + 4;
                int vec_w = win_w - vec_x - 8;
                if (vec_w >= 110) {
                    draw_app_vector_widget(dpy, win, gc, &colors, cfg->app_id, vec_x, tb_y, vec_w, btn_h, font_asc);
                }

                /* 4. Main Sunken 3D Application Viewport Canvas */
                int cmd_box_h = font_h + 14;
                int st_box_h = font_h + 12;
                int canvas_y = tb_y + btn_h + 8;
                int canvas_h = win_h - canvas_y - cmd_box_h - st_box_h - 22;
                if (canvas_h < 120) canvas_h = 120;
                draw_bevel_rect(dpy, win, gc, &colors, 8, canvas_y, win_w - 16, canvas_h, colors.canvas_bg, 1);

                XSetForeground(dpy, gc, colors.canvas_fg);
                int line_h = font_h + 3;
                int max_vis = (canvas_h - 14) / line_h;
                for (int i = 0; i < line_count && i < max_vis; i++) {
                    XDrawString(dpy, win, gc, 18, canvas_y + font_asc + 8 + i * line_h,
                                lines[i], (int)strlen(lines[i]));
                }

                /* 5. Sunken Motif XmTextField Command Entry Box */
                int cmd_y = canvas_y + canvas_h + 6;
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, win, gc, 10, cmd_y + font_asc + 5, "DECW Cmd>", 9);

                int box_x = 16 + char_w * 10;
                int box_w = win_w - box_x - 10;
                draw_bevel_rect(dpy, win, gc, &colors, box_x, cmd_y, box_w, cmd_box_h, colors.cmd_bg, 1);
                char prompt_disp[220];
                snprintf(prompt_disp, sizeof(prompt_disp), "%s_", cmd_input);
                XSetForeground(dpy, gc, BlackPixel(dpy, screen));
                XDrawString(dpy, win, gc, box_x + 8, cmd_y + font_asc + 5, prompt_disp, (int)strlen(prompt_disp));

                /* 6. Bottom Status Bar */
                int st_y = cmd_y + cmd_box_h + 6;
                draw_bevel_rect(dpy, win, gc, &colors, 8, st_y, win_w - 16, st_box_h, colors.bg_gray, 1);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, win, gc, 16, st_y + font_asc + 4, status_msg, (int)strlen(status_msg));

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
            } else if (ev.type == ButtonPress) {
                int mx = ev.xbutton.x;
                int my = ev.xbutton.y;
                for (int b = 0; b < num_buttons; b++) {
                    if (mx >= buttons[b].x && mx <= buttons[b].x + buttons[b].w &&
                        my >= buttons[b].y && my <= buttons[b].y + buttons[b].h) {
                        buttons[b].pressed = 1;
                        XClearArea(dpy, win, 0, 0, 0, 0, True);
                    }
                }
            } else if (ev.type == ButtonRelease) {
                int mx = ev.xbutton.x;
                int my = ev.xbutton.y;
                for (int b = 0; b < num_buttons; b++) {
                    int was_pressed = buttons[b].pressed;
                    buttons[b].pressed = 0;
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
                            XClearArea(dpy, win, 0, 0, 0, 0, True);
                        } else {
                            decw_x11_exec_app_cmd(cfg, buttons[b].command, status_msg, sizeof(status_msg));
                            line_count = decw_x11_load_frame(cfg->frame_path, lines, DECW_MAX_LINES);
                            XClearArea(dpy, win, 0, 0, 0, 0, True);
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
                    XClearArea(dpy, win, 0, 0, 0, 0, True);
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
                    XClearArea(dpy, win, 0, 0, 0, 0, True);
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
                        XClearArea(dpy, win, 0, 0, 0, 0, True);
                    } else if (cmd_input[0]) {
                        decw_x11_exec_app_cmd(cfg, cmd_input, status_msg, sizeof(status_msg));
                        line_count = decw_x11_load_frame(cfg->frame_path, lines, DECW_MAX_LINES);
                        cmd_input[0] = '\0';
                        XClearArea(dpy, win, 0, 0, 0, 0, True);
                    }
                } else if (ks == XK_BackSpace || ks == XK_Delete) {
                    size_t clen = strlen(cmd_input);
                    if (clen > 0) {
                        cmd_input[clen - 1] = '\0';
                        XClearArea(dpy, win, 0, 0, 0, 0, True);
                    }
                } else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127) {
                    size_t clen = strlen(cmd_input);
                    if (clen + 1 < sizeof(cmd_input)) {
                        cmd_input[clen] = kbuf[0];
                        cmd_input[clen + 1] = '\0';
                        XClearArea(dpy, win, 0, 0, 0, 0, True);
                    }
                }
            } else if (ev.type == ClientMessage) {
                if ((Atom)ev.xclient.data.l[0] == wm_delete) {
                    running = 0;
                }
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

    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}
