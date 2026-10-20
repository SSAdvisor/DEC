#ifndef DECW_GUI_GROUP1_H
#define DECW_GUI_GROUP1_H

/* ============================================================================
 * Shared OSF/Motif 1.1 Window Chrome, Menu Bar & Pull-Down Menu Toolkit
 * ============================================================================ */

typedef struct {
    const char* label;
    int action_id;
} DecwMenuItem;

typedef struct {
    const char* title;
    int x;
    int w;
    int right_align;
    const DecwMenuItem* items;
    int num_items;
} DecwMenuBarMenu;

static void draw_motif_chrome_and_menubar(
    Display* dpy, Drawable d, GC gc, const DecwColors* c,
    int win_w, int win_h, int font_asc, int font_h,
    const char* title, DecwMenuBarMenu* menus, int num_menus,
    int open_menu_idx, int* out_content_y)
{
    int title_h = font_h + 10;
    /* Outer 3D Motif Frame */
    draw_bevel_rect(dpy, d, gc, c, 0, 0, win_w, win_h, c->bg_gray, 0);

    /* Title Bar */
    draw_bevel_rect(dpy, d, gc, c, 6, 6, win_w - 12, title_h, c->title_bg, 0);
    draw_bevel_rect(dpy, d, gc, c, 9, 9, title_h - 6, title_h - 6, c->btn_bg, 0);
    XSetForeground(dpy, gc, c->canvas_fg);
    XDrawString(dpy, d, gc, 13, 8 + font_asc, "-", 1);

    XSetForeground(dpy, gc, c->title_fg);
    XDrawString(dpy, d, gc, 16 + title_h, 8 + font_asc, title, (int)strlen(title));

    /* Minimize & Maximize Motif buttons */
    draw_bevel_rect(dpy, d, gc, c, win_w - (title_h * 2 + 4), 9, title_h - 6, title_h - 6, c->btn_bg, 0);
    draw_bevel_rect(dpy, d, gc, c, win_w - (title_h), 9, title_h - 6, title_h - 6, c->btn_bg, 0);
    XSetForeground(dpy, gc, c->canvas_fg);
    XDrawString(dpy, d, gc, win_w - (title_h * 2 - 2), 8 + font_asc, ".", 1);
    XDrawRectangle(dpy, d, gc, win_w - title_h + 4, 13, (unsigned int)(title_h - 14), (unsigned int)(title_h - 14));

    /* Menu Bar */
    int mb_y = 6 + title_h + 2;
    int mb_h = font_h + 10;
    draw_bevel_rect(dpy, d, gc, c, 6, mb_y, win_w - 12, mb_h, c->btn_bg, 0);

    int cur_x = 12;
    int char_w = font_h / 2 + 2;
    for (int i = 0; i < num_menus; i++) {
        int mw = (int)strlen(menus[i].title) * char_w + 18;
        menus[i].w = mw;
        if (menus[i].right_align) {
            menus[i].x = win_w - mw - 12;
        } else {
            menus[i].x = cur_x;
            cur_x += mw + 4;
        }
        if (open_menu_idx == i) {
            draw_bevel_rect(dpy, d, gc, c, menus[i].x, mb_y + 2, mw, mb_h - 4, c->bg_gray, 1);
        }
        XSetForeground(dpy, gc, c->canvas_fg);
        XDrawString(dpy, d, gc, menus[i].x + 8, mb_y + font_asc + 3, menus[i].title, (int)strlen(menus[i].title));
        /* Underline mnemonic first character */
        XDrawLine(dpy, d, gc, menus[i].x + 8, mb_y + font_asc + 5, menus[i].x + 8 + char_w, mb_y + font_asc + 5);
    }

    if (out_content_y) {
        *out_content_y = mb_y + mb_h + 4;
    }
}

static void draw_motif_open_dropdown(
    Display* dpy, Drawable d, GC gc, const DecwColors* c,
    int win_w, int font_asc, int font_h,
    const DecwMenuBarMenu* menus, int num_menus, int open_menu_idx)
{
    if (open_menu_idx < 0 || open_menu_idx >= num_menus) return;
    const DecwMenuBarMenu* m = &menus[open_menu_idx];
    int title_h = font_h + 10;
    int mb_y = 6 + title_h + 2;
    int mb_h = font_h + 10;
    int drop_y = mb_y + mb_h;
    int item_h = font_h + 8;
    int char_w = font_h / 2 + 2;
    int max_len = 16;
    for (int i = 0; i < m->num_items; i++) {
        int l = (int)strlen(m->items[i].label);
        if (l > max_len) max_len = l;
    }
    int drop_w = max_len * char_w + 28;
    int drop_x = m->x;
    if (drop_x + drop_w > win_w - 8) drop_x = win_w - drop_w - 8;
    int drop_h = m->num_items * item_h + 8;

    draw_bevel_rect(dpy, d, gc, c, drop_x, drop_y, drop_w, drop_h, c->btn_bg, 0);
    for (int i = 0; i < m->num_items; i++) {
        int iy = drop_y + 4 + i * item_h;
        if (strcmp(m->items[i].label, "---") == 0) {
            XSetForeground(dpy, gc, c->bevel_dark);
            XDrawLine(dpy, d, gc, drop_x + 4, iy + item_h / 2, drop_x + drop_w - 4, iy + item_h / 2);
            XSetForeground(dpy, gc, c->bevel_light);
            XDrawLine(dpy, d, gc, drop_x + 4, iy + item_h / 2 + 1, drop_x + drop_w - 4, iy + item_h / 2 + 1);
        } else {
            XSetForeground(dpy, gc, c->canvas_fg);
            XDrawString(dpy, d, gc, drop_x + 12, iy + font_asc + 2, m->items[i].label, (int)strlen(m->items[i].label));
        }
    }
}

/* Returns:
 *  0 = not a menubar click
 * -1 = opened/closed a menu
 * >0 = selected action_id from open dropdown
 */
static int handle_motif_menubar_click(
    int mx, int my, int win_w, int font_h,
    const DecwMenuBarMenu* menus, int num_menus, int* open_menu_idx)
{
    int title_h = font_h + 10;
    int mb_y = 6 + title_h + 2;
    int mb_h = font_h + 10;

    if (*open_menu_idx >= 0 && *open_menu_idx < num_menus) {
        const DecwMenuBarMenu* m = &menus[*open_menu_idx];
        int drop_y = mb_y + mb_h;
        int item_h = font_h + 8;
        int char_w = font_h / 2 + 2;
        int max_len = 16;
        for (int i = 0; i < m->num_items; i++) {
            int l = (int)strlen(m->items[i].label);
            if (l > max_len) max_len = l;
        }
        int drop_w = max_len * char_w + 28;
        int drop_x = m->x;
        if (drop_x + drop_w > win_w - 8) drop_x = win_w - drop_w - 8;
        int drop_h = m->num_items * item_h + 8;

        if (mx >= drop_x && mx <= drop_x + drop_w && my >= drop_y && my <= drop_y + drop_h) {
            int idx = (my - (drop_y + 4)) / item_h;
            *open_menu_idx = -1;
            if (idx >= 0 && idx < m->num_items && m->items[idx].action_id > 0) {
                return m->items[idx].action_id;
            }
            return -1;
        }
    }

    if (my >= mb_y && my <= mb_y + mb_h) {
        for (int i = 0; i < num_menus; i++) {
            if (mx >= menus[i].x && mx <= menus[i].x + menus[i].w) {
                *open_menu_idx = (*open_menu_idx == i) ? -1 : i;
                return -1;
            }
        }
    }

    if (*open_menu_idx != -1) {
        *open_menu_idx = -1;
        return -1;
    }
    return 0;
}

static void draw_motif_status_bar(
    Display* dpy, Drawable d, GC gc, const DecwColors* c,
    int win_w, int win_h, int font_asc, int font_h, const char* status_msg)
{
    int st_h = font_h + 10;
    int st_y = win_h - st_h - 6;
    draw_bevel_rect(dpy, d, gc, c, 6, st_y, win_w - 12, st_h, c->bg_gray, 1);
    XSetForeground(dpy, gc, c->canvas_fg);
    XDrawString(dpy, d, gc, 14, st_y + font_asc + 3, status_msg, (int)strlen(status_msg));
}

static void draw_motif_about_dialog(
    Display* dpy, Drawable d, GC gc, const DecwColors* c,
    int win_w, int win_h, int font_asc, int font_h,
    const char* app_title, const char* line1, const char* line2, const char* line3,
    int* ok_x, int* ok_y, int* ok_w, int* ok_h)
{
    int dw = (win_w - 60 < 520) ? (win_w - 60) : 520;
    int dh = font_h * 8 + 64;
    int dx = (win_w - dw) / 2;
    int dy = (win_h - dh) / 2;

    draw_bevel_rect(dpy, d, gc, c, dx, dy, dw, dh, c->bg_gray, 0);
    draw_bevel_rect(dpy, d, gc, c, dx + 4, dy + 4, dw - 8, font_h + 8, c->title_bg, 0);
    XSetForeground(dpy, gc, c->title_fg);
    XDrawString(dpy, d, gc, dx + 12, dy + 6 + font_asc, app_title, (int)strlen(app_title));

    draw_bevel_rect(dpy, d, gc, c, dx + 10, dy + font_h + 18, dw - 20, dh - font_h * 2 - 42, c->canvas_bg, 1);
    XSetForeground(dpy, gc, c->canvas_fg);
    int ty = dy + font_h * 2 + 12 + font_asc;
    XDrawString(dpy, d, gc, dx + 20, ty, line1, (int)strlen(line1));
    ty += font_h + 6;
    XDrawString(dpy, d, gc, dx + 20, ty, line2, (int)strlen(line2));
    ty += font_h + 6;
    XDrawString(dpy, d, gc, dx + 20, ty, line3, (int)strlen(line3));

    *ok_w = 100;
    *ok_h = font_h + 12;
    *ok_x = dx + (dw - *ok_w) / 2;
    *ok_y = dy + dh - *ok_h - 10;
    draw_bevel_rect(dpy, d, gc, c, *ok_x, *ok_y, *ok_w, *ok_h, c->btn_bg, 0);
    XSetForeground(dpy, gc, c->canvas_fg);
    XDrawString(dpy, d, gc, *ok_x + 36, *ok_y + font_asc + 4, "OK", 2);
}

/* ============================================================================
 * 1. DECwindows Calculator (DECW$CALC / dxcalc)
 *    Authentic OSF/Motif 1.1 Scientific, Financial & Programmer Calculator
 * ============================================================================ */

typedef struct {
    char mode[24];     /* SCIENTIFIC, FINANCIAL, PROGRAMMER */
    char base[12];     /* DEC, HEX, OCT, BIN */
    long acc;
    long operand;
    long mem;
    char pending_op;   /* 0, '+', '-', '*', '/', '%', '&', '|', '^' */
    int entering_new;
    int show_tape;
    int dialog_mode;   /* 0=none, 1=About */
    char tape_op[64][64];
    long tape_res[64];
    int num_tape;
    /* Financial registers */
    long fin_pv;
    long fin_rate_bp;  /* basis points, e.g. 850 = 8.50% */
    long fin_years;
} DecwCalcState;

static void calc_add_tape(DecwCalcState* st, const char* op_desc, long res) {
    if (st->num_tape >= 60) {
        for (int i = 0; i < 59; i++) {
            strcpy(st->tape_op[i], st->tape_op[i + 1]);
            st->tape_res[i] = st->tape_res[i + 1];
        }
        st->num_tape = 59;
    }
    snprintf(st->tape_op[st->num_tape], sizeof(st->tape_op[0]), "%s", op_desc);
    st->tape_res[st->num_tape] = res;
    st->num_tape++;
}

static void calc_load_state(DecwCalcState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    strcpy(st->mode, "SCIENTIFIC");
    strcpy(st->base, "DEC");
    st->acc = 3840;
    st->mem = 4096;
    st->entering_new = 1;
    st->show_tape = 1;
    st->fin_pv = 100000;
    st->fin_rate_bp = 850;
    st->fin_years = 30;

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[256];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            if (strncmp(line, "STATE|", 6) == 0) {
                char m[32] = "", b[16] = "";
                long a = 0, mem = 0;
                if (sscanf(line + 6, "%31[^|]|%15[^|]|%ld|%ld", m, b, &a, &mem) == 4) {
                    snprintf(st->mode, sizeof(st->mode), "%s", m);
                    snprintf(st->base, sizeof(st->base), "%s", b);
                    st->acc = a;
                    st->mem = mem;
                }
            } else if (strncmp(line, "TAPE|", 5) == 0) {
                char op[64] = "";
                long r = 0;
                if (sscanf(line + 5, "%63[^|]|%ld", op, &r) == 2) {
                    calc_add_tape(st, op, r);
                }
            }
        }
        fclose(fp);
    }
    if (st->num_tape == 0) {
        calc_add_tape(st, "SET 1024", 1024);
        calc_add_tape(st, "ADD 2048", 3072);
        calc_add_tape(st, "MUL 4", 12288);
        calc_add_tape(st, "DIV 3", 4096);
        calc_add_tape(st, "STO (M=4096)", 4096);
        calc_add_tape(st, "SUB 256", 3840);
    }
}

static void calc_save_state(const DecwCalcState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    fprintf(fp, "STATE|%s|%s|%ld|%ld\n", st->mode, st->base, st->acc, st->mem);
    for (int i = 0; i < st->num_tape; i++) {
        fprintf(fp, "TAPE|%s|%ld\n", st->tape_op[i], st->tape_res[i]);
    }
    fclose(fp);
}

static void calc_format_bin16(long v, char* out, size_t len) {
    unsigned int u = (unsigned int)(v & 0xFFFF);
    char tmp[24];
    int p = 0;
    for (int b = 15; b >= 0; b--) {
        tmp[p++] = (u & (1u << b)) ? '1' : '0';
        if (b % 4 == 0 && b != 0) tmp[p++] = ' ';
    }
    tmp[p] = '\0';
    snprintf(out, len, "%s", tmp);
}

static void calc_format_primary(const DecwCalcState* st, char* out, size_t len) {
    if (strcasecmp(st->base, "HEX") == 0) {
        snprintf(out, len, "0x%lX", (unsigned long)(st->acc & 0xFFFFFFFFUL));
    } else if (strcasecmp(st->base, "OCT") == 0) {
        snprintf(out, len, "0o%lo", (unsigned long)(st->acc & 0xFFFFFFFFUL));
    } else if (strcasecmp(st->base, "BIN") == 0) {
        char bstr[32];
        calc_format_bin16(st->acc, bstr, sizeof(bstr));
        snprintf(out, len, "2#%s", bstr);
    } else {
        snprintf(out, len, "%ld", st->acc);
    }
}

static void calc_apply_pending(DecwCalcState* st) {
    if (!st->pending_op) return;
    long a = st->operand;
    long b = st->acc;
    long res = b;
    char desc[64];
    switch (st->pending_op) {
        case '+': res = a + b; snprintf(desc, sizeof(desc), "%ld + %ld", a, b); break;
        case '-': res = a - b; snprintf(desc, sizeof(desc), "%ld - %ld", a, b); break;
        case '*': res = a * b; snprintf(desc, sizeof(desc), "%ld * %ld", a, b); break;
        case '/': res = (b != 0) ? (a / b) : 0; snprintf(desc, sizeof(desc), "%ld / %ld", a, b); break;
        case '%': res = (b != 0) ? (a % b) : 0; snprintf(desc, sizeof(desc), "%ld MOD %ld", a, b); break;
        case '&': res = a & b; snprintf(desc, sizeof(desc), "%ld AND %ld", a, b); break;
        case '|': res = a | b; snprintf(desc, sizeof(desc), "%ld OR %ld", a, b); break;
        case '^': res = a ^ b; snprintf(desc, sizeof(desc), "%ld XOR %ld", a, b); break;
    }
    st->acc = res;
    st->pending_op = 0;
    st->entering_new = 1;
    calc_add_tape(st, desc, res);
}

static void calc_press_key(DecwCalcState* st, const char* key, const char* state_path, char* status_msg, size_t st_len) {
    if (strlen(key) == 1 && ((key[0] >= '0' && key[0] <= '9') || (key[0] >= 'A' && key[0] <= 'F'))) {
        int d = (key[0] <= '9') ? (key[0] - '0') : (key[0] - 'A' + 10);
        int radix = 10;
        if (strcasecmp(st->base, "HEX") == 0) radix = 16;
        else if (strcasecmp(st->base, "OCT") == 0) radix = 8;
        else if (strcasecmp(st->base, "BIN") == 0) radix = 2;
        if (d >= radix) {
            snprintf(status_msg, st_len, "Digit '%s' invalid in %s base", key, st->base);
            return;
        }
        if (st->entering_new) {
            st->acc = d;
            st->entering_new = 0;
        } else {
            st->acc = st->acc * radix + (st->acc < 0 ? -d : d);
        }
        snprintf(status_msg, st_len, "Accumulator: %ld", st->acc);
        return;
    }

    if (strcmp(key, "AC") == 0) {
        st->acc = 0;
        st->operand = 0;
        st->pending_op = 0;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "All Clear (Accumulator & Pending Op reset)");
    } else if (strcmp(key, "CE") == 0) {
        st->acc = 0;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Clear Entry (0)");
    } else if (strcmp(key, "+/-") == 0) {
        st->acc = -st->acc;
        snprintf(status_msg, st_len, "Negated accumulator -> %ld", st->acc);
    } else if (strcmp(key, "MC") == 0) {
        st->mem = 0;
        snprintf(status_msg, st_len, "Memory Cleared (M=0)");
    } else if (strcmp(key, "MR") == 0) {
        st->acc = st->mem;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Memory Recall -> %ld", st->acc);
    } else if (strcmp(key, "MS") == 0) {
        st->mem = st->acc;
        st->entering_new = 1;
        char d[64];
        snprintf(d, sizeof(d), "STO (M=%ld)", st->mem);
        calc_add_tape(st, d, st->acc);
        snprintf(status_msg, st_len, "Memory Stored (M=%ld)", st->mem);
    } else if (strcmp(key, "M+") == 0) {
        st->mem += st->acc;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Memory Add -> M=%ld", st->mem);
    } else if (strcmp(key, "M-") == 0) {
        st->mem -= st->acc;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Memory Subtract -> M=%ld", st->mem);
    } else if (strcmp(key, "+") == 0 || strcmp(key, "-") == 0 ||
               strcmp(key, "*") == 0 || strcmp(key, "/") == 0 ||
               strcmp(key, "MOD") == 0 || strcmp(key, "AND") == 0 ||
               strcmp(key, "OR") == 0 || strcmp(key, "XOR") == 0) {
        if (!st->entering_new && st->pending_op) {
            calc_apply_pending(st);
        }
        st->operand = st->acc;
        if (strcmp(key, "MOD") == 0) st->pending_op = '%';
        else if (strcmp(key, "AND") == 0) st->pending_op = '&';
        else if (strcmp(key, "OR") == 0) st->pending_op = '|';
        else if (strcmp(key, "XOR") == 0) st->pending_op = '^';
        else st->pending_op = key[0];
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Operator '%s' latched (Operand=%ld)", key, st->operand);
    } else if (strcmp(key, "=") == 0) {
        calc_apply_pending(st);
        snprintf(status_msg, st_len, "Result = %ld (0x%lX)", st->acc, (unsigned long)(st->acc & 0xFFFFFFFFUL));
    } else if (strcmp(key, "SQRT") == 0) {
        long old = st->acc;
        st->acc = (old > 0) ? (long)sqrt((double)old) : 0;
        st->entering_new = 1;
        char d[64];
        snprintf(d, sizeof(d), "SQRT(%ld)", old);
        calc_add_tape(st, d, st->acc);
        snprintf(status_msg, st_len, "SQRT(%ld) = %ld", old, st->acc);
    } else if (strcmp(key, "x^2") == 0) {
        long old = st->acc;
        st->acc = old * old;
        st->entering_new = 1;
        char d[64];
        snprintf(d, sizeof(d), "SQR(%ld)", old);
        calc_add_tape(st, d, st->acc);
        snprintf(status_msg, st_len, "SQR(%ld) = %ld", old, st->acc);
    } else if (strcmp(key, "NOT") == 0) {
        st->acc = (~st->acc) & 0xFFFF;
        st->entering_new = 1;
        calc_add_tape(st, "NOT16", st->acc);
        snprintf(status_msg, st_len, "16-bit NOT -> %ld (0x%lX)", st->acc, (unsigned long)st->acc);
    } else if (strcmp(key, "SHL") == 0) {
        st->acc = st->acc << 1;
        st->entering_new = 1;
        calc_add_tape(st, "SHL 1", st->acc);
        snprintf(status_msg, st_len, "Shift Left -> %ld", st->acc);
    } else if (strcmp(key, "SHR") == 0) {
        st->acc = st->acc >> 1;
        st->entering_new = 1;
        calc_add_tape(st, "SHR 1", st->acc);
        snprintf(status_msg, st_len, "Shift Right -> %ld", st->acc);
    } else if (strcmp(key, "SIN") == 0 || strcmp(key, "COS") == 0) {
        double rad = (double)st->acc * 3.14159265358979 / 180.0;
        double v = (strcmp(key, "SIN") == 0) ? sin(rad) : cos(rad);
        long old = st->acc;
        st->acc = (long)round(v * 1000.0);
        st->entering_new = 1;
        char d[64];
        snprintf(d, sizeof(d), "%s(%ld deg)*1000", key, old);
        calc_add_tape(st, d, st->acc);
        snprintf(status_msg, st_len, "%s(%ld deg) = %.3f (scaled x1000 = %ld)", key, old, v, st->acc);
    } else if (strcmp(key, "PV") == 0) {
        st->fin_pv = (st->acc > 0) ? st->acc : 100000;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Financial Principal PV set to $%ld", st->fin_pv);
    } else if (strcmp(key, "RATE") == 0) {
        st->fin_rate_bp = (st->acc > 0) ? (st->acc * 100) : 850;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Annual Interest Rate set to %.2f%%", st->fin_rate_bp / 100.0);
    } else if (strcmp(key, "N-YR") == 0) {
        st->fin_years = (st->acc > 0) ? st->acc : 30;
        st->entering_new = 1;
        snprintf(status_msg, st_len, "Loan Term set to %ld years", st->fin_years);
    } else if (strcmp(key, "PMT") == 0) {
        double r = (st->fin_rate_bp / 10000.0) / 12.0;
        int n = (int)(st->fin_years * 12);
        double pmt = 0.0;
        if (r > 0.0 && n > 0) {
            pmt = (double)st->fin_pv * (r * pow(1.0 + r, n)) / (pow(1.0 + r, n) - 1.0);
        } else if (n > 0) {
            pmt = (double)st->fin_pv / n;
        }
        st->acc = (long)round(pmt);
        st->entering_new = 1;
        char d[64];
        snprintf(d, sizeof(d), "PMT($%ld,%.1f%%,%ldy)", st->fin_pv, st->fin_rate_bp / 100.0, st->fin_years);
        calc_add_tape(st, d, st->acc);
        snprintf(status_msg, st_len, "Monthly Payment PMT = $%ld/mo (PV=$%ld, %.2f%%, %ld yrs)",
                 st->acc, st->fin_pv, st->fin_rate_bp / 100.0, st->fin_years);
    }
    calc_save_state(st, state_path);
}

static int run_calculator_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "calculator", &colors);
    unsigned long lcd_bg = alloc_color(dpy, screen, "#18241C", BlackPixel(dpy, screen));
    unsigned long lcd_fg = alloc_color(dpy, screen, "#48FF88", WhitePixel(dpy, screen));
    unsigned long lcd_dim = alloc_color(dpy, screen, "#98D8B0", WhitePixel(dpy, screen));

    int font_scale = (disp_w >= 2560) ? 3 : 2;
    char custom_xlfd[128] = "";
    if (getenv("DECW_FONT_SIZE")) {
        int s = parse_font_spec_to_scale(getenv("DECW_FONT_SIZE"), custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (cfg->font_scale >= 1 && cfg->font_scale <= 6) font_scale = cfg->font_scale;
    if (cfg->font_spec[0]) {
        int s = parse_font_spec_to_scale(cfg->font_spec, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }

    char font_desc[96] = "";
    int rec_w = 880, rec_h = 680;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 420) ? cfg->width : (560 + font_scale * 90);
    int win_h = (cfg->height >= 360) ? cfg->height : (460 + font_scale * 70);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 90, 90,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Calculator";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$CALC");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwCalcState st;
    calc_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Load Sample Tape", 101},
        {"Clear All (AC)",   102},
        {"Save Tape State",  103},
        {"---",              0},
        {"Exit",             109}
    };
    static const DecwMenuItem mode_items[] = {
        {"Scientific Mode",  201},
        {"Financial Mode",   202},
        {"Programmer Mode",  203},
        {"---",              0},
        {"Toggle Paper Tape",204}
    };
    static const DecwMenuItem base_items[] = {
        {"Decimal (DEC)",    301},
        {"Hexadecimal (HEX)",302},
        {"Octal (OCT)",      303},
        {"Binary (BIN)",     304}
    };
    static const DecwMenuItem help_items[] = {
        {"About Calculator...", 401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File", 0, 0, 0, file_items, 5},
        {"Mode", 0, 0, 0, mode_items, 5},
        {"Base", 0, 0, 0, base_items, 4},
        {"Help", 0, 0, 1, help_items, 1}
    };

    static const char* key_labels[7][5] = {
        {"MC",   "MR",   "MS",   "M+",  "M-"},
        {"SQRT", "x^2",  "SIN",  "COS", "PMT"},
        {"AND",  "OR",   "XOR",  "NOT", "MOD"},
        {"7",    "8",    "9",    "/",   "AC"},
        {"4",    "5",    "6",    "*",   "CE"},
        {"1",    "2",    "3",    "-",   "SHL"},
        {"0",    "+/-",  "=",    "+",   "SHR"}
    };
    static const char* hex_row[6] = {"A", "B", "C", "D", "E", "F"};
    static const char* mode_bar[7] = {"DEC", "HEX", "OCT", "BIN", "SCI", "FIN", "PROG"};

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "DECwindows Calculator Ready | Mode: %s | Base: %s", st.mode, st.base);

    XMapWindow(dpy, win);
    XFlush(dpy);

    int autoclose_ms = cfg->autoclose_ms;
    const char* env_ac = getenv("DECW_X11_AUTOCLOSE_MS");
    if (autoclose_ms <= 0 && env_ac && env_ac[0]) autoclose_ms = atoi(env_ac);
    if (cfg->verify_only && autoclose_ms <= 0) autoclose_ms = 120;

    struct timeval start_tv;
    gettimeofday(&start_tv, NULL);
    int exposed_once = 0, need_redraw = 0, sent_synth = 0, running = 1;
    int open_menu = -1;
    int ok_x = 0, ok_y = 0, ok_w = 0, ok_h = 0;

    /* Button hit geometry cached during draw */
    int pad_x = 12, pad_y = 180, pad_w = 400, pad_h = 260;
    int hex_y = 145, hex_h = 28;
    int mbar_y = 112, mbar_h = 28;

    while (running) {
        while (XPending(dpy) > 0) {
            XEvent ev;
            XNextEvent(dpy, &ev);
            int font_h = (font ? (font->ascent + font->descent) : 18);
            if (font_h < 14) font_h = 14;

            if (ev.type == ConfigureNotify) {
                if (ev.xconfigure.width != win_w || ev.xconfigure.height != win_h) {
                    win_w = ev.xconfigure.width;
                    win_h = ev.xconfigure.height;
                    need_redraw = 1;
                }
            } else if (ev.type == Expose && ev.xexpose.count == 0) {
                exposed_once = 1;
                need_redraw = 1;
            } else if (ev.type == ButtonPress && ev.xbutton.button == Button1) {
                int mx = ev.xbutton.x, my = ev.xbutton.y;
                need_redraw = 1;

                if (st.dialog_mode != 0) {
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) {
                        st.dialog_mode = 0;
                    }
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) { calc_load_state(&st, NULL); calc_save_state(&st, cfg->state_path); snprintf(status_msg, sizeof(status_msg), "Loaded DEC engineering calculation tape"); }
                    else if (mact == 102) calc_press_key(&st, "AC", cfg->state_path, status_msg, sizeof(status_msg));
                    else if (mact == 103) { calc_save_state(&st, cfg->state_path); snprintf(status_msg, sizeof(status_msg), "Saved calculator state to %.160s", cfg->state_path); }
                    else if (mact == 109) running = 0;
                    else if (mact == 201) { strcpy(st.mode, "SCIENTIFIC"); calc_save_state(&st, cfg->state_path); }
                    else if (mact == 202) { strcpy(st.mode, "FINANCIAL"); calc_save_state(&st, cfg->state_path); }
                    else if (mact == 203) { strcpy(st.mode, "PROGRAMMER"); calc_save_state(&st, cfg->state_path); }
                    else if (mact == 204) { st.show_tape = !st.show_tape; }
                    else if (mact == 301) { strcpy(st.base, "DEC"); calc_save_state(&st, cfg->state_path); }
                    else if (mact == 302) { strcpy(st.base, "HEX"); calc_save_state(&st, cfg->state_path); }
                    else if (mact == 303) { strcpy(st.base, "OCT"); calc_save_state(&st, cfg->state_path); }
                    else if (mact == 304) { strcpy(st.base, "BIN"); calc_save_state(&st, cfg->state_path); }
                    else if (mact == 401) { st.dialog_mode = 1; }
                    continue;
                }

                /* Check mode/base quick toggle row */
                if (my >= mbar_y && my <= mbar_y + mbar_h && mx >= pad_x && mx <= pad_x + pad_w) {
                    int idx = (mx - pad_x) * 7 / (pad_w > 0 ? pad_w : 1);
                    if (idx >= 0 && idx < 4) {
                        strcpy(st.base, mode_bar[idx]);
                        snprintf(status_msg, sizeof(status_msg), "Switched number base to %s", st.base);
                    } else if (idx == 4) strcpy(st.mode, "SCIENTIFIC");
                    else if (idx == 5) strcpy(st.mode, "FINANCIAL");
                    else if (idx == 6) strcpy(st.mode, "PROGRAMMER");
                    calc_save_state(&st, cfg->state_path);
                    continue;
                }

                /* Check Hex A..F row */
                if (my >= hex_y && my <= hex_y + hex_h && mx >= pad_x && mx <= pad_x + pad_w) {
                    int idx = (mx - pad_x) * 6 / (pad_w > 0 ? pad_w : 1);
                    if (idx >= 0 && idx < 6) {
                        if (strcasecmp(st.base, "HEX") != 0) strcpy(st.base, "HEX");
                        calc_press_key(&st, hex_row[idx], cfg->state_path, status_msg, sizeof(status_msg));
                    }
                    continue;
                }

                /* Check 7x5 main keypad grid */
                if (mx >= pad_x && mx < pad_x + pad_w && my >= pad_y && my < pad_y + pad_h) {
                    int col = (mx - pad_x) * 5 / pad_w;
                    int row = (my - pad_y) * 7 / pad_h;
                    if (row >= 0 && row < 7 && col >= 0 && col < 5) {
                        const char* lbl = key_labels[row][col];
                        if (row == 1 && strcasecmp(st.mode, "FINANCIAL") == 0) {
                            const char* fin_row[5] = {"PV", "RATE", "N-YR", "PMT", "x^2"};
                            lbl = fin_row[col];
                        }
                        calc_press_key(&st, lbl, cfg->state_path, status_msg, sizeof(status_msg));
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                int n = XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                kbuf[n] = '\0';
                need_redraw = 1;
                if (ks == XK_Escape) {
                    if (st.dialog_mode != 0) st.dialog_mode = 0;
                    else running = 0;
                } else if (ks == XK_Return || ks == XK_KP_Enter) {
                    if (st.dialog_mode != 0) st.dialog_mode = 0;
                    else calc_press_key(&st, "=", cfg->state_path, status_msg, sizeof(status_msg));
                } else if (ks == XK_BackSpace || ks == XK_Delete) {
                    st.acc /= 10;
                } else if (ks == XK_F10 || ks == XK_Next) {
                    if (font_scale > 1) font_scale--;
                    if (font) XFreeFont(dpy, font);
                    font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                    if (font) XSetFont(dpy, gc, font->fid);
                } else if (ks == XK_F11 || ks == XK_Prior) {
                    if (font_scale < 6) font_scale++;
                    if (font) XFreeFont(dpy, font);
                    font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                    if (font) XSetFont(dpy, gc, font->fid);
                } else if (n > 0) {
                    char c = kbuf[0];
                    if (c >= 'a' && c <= 'f') c = (char)(c - 'a' + 'A');
                    if ((c >= '0' && c <= '9') || (c >= 'A' && c <= 'F')) {
                        char s[2] = {c, '\0'};
                        calc_press_key(&st, s, cfg->state_path, status_msg, sizeof(status_msg));
                    } else if (c == '+' || c == '-' || c == '*' || c == '/' || c == '=') {
                        char s[2] = {c, '\0'};
                        calc_press_key(&st, s, cfg->state_path, status_msg, sizeof(status_msg));
                    } else if (c == 'q' || c == 'Q') {
                        running = 0;
                    }
                }
            } else if (ev.type == ClientMessage && (Atom)ev.xclient.data.l[0] == wm_delete) {
                running = 0;
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
            int font_h = font ? (font->ascent + font->descent) : 18;
            if (font_h < 14) font_h = 14;
            int cy = 0;
            draw_motif_chrome_and_menubar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                                          title, menus, 4, open_menu, &cy);

            int st_h = font_h + 10;
            int avail_h = win_h - cy - st_h - 14;
            int tape_w = st.show_tape ? (win_w * 38 / 100) : 0;
            if (tape_w > 0 && tape_w < 210) tape_w = 210;
            pad_x = 10;
            pad_w = win_w - tape_w - 24;
            if (pad_w < 260) pad_w = 260;

            /* 1. Sunken LCD Accumulator Display */
            int lcd_h = font_h * 3 + 22;
            draw_bevel_rect(dpy, back_buf, gc, &colors, pad_x, cy, pad_w, lcd_h, lcd_bg, 1);

            char prim_str[64], bin_str[32], sec_line[160], mode_line[160];
            calc_format_primary(&st, prim_str, sizeof(prim_str));
            calc_format_bin16(st.acc, bin_str, sizeof(bin_str));
            snprintf(mode_line, sizeof(mode_line), "[%s]  Base: %s   %s   Op: %c",
                     st.mode, st.base,
                     st.mem != 0 ? "M" : " ",
                     st.pending_op ? st.pending_op : '-');
            snprintf(sec_line, sizeof(sec_line), "DEC: %ld  |  HEX: 0x%lX  |  OCT: 0o%lo  |  MEM: %ld",
                     st.acc, (unsigned long)(st.acc & 0xFFFF), (unsigned long)(st.acc & 0xFFFF), st.mem);

            XSetForeground(dpy, gc, lcd_dim);
            XDrawString(dpy, back_buf, gc, pad_x + 10, cy + font_asc + 4, mode_line, (int)strlen(mode_line));
            XSetForeground(dpy, gc, lcd_fg);
            XDrawString(dpy, back_buf, gc, pad_x + 14, cy + font_h + font_asc + 8, prim_str, (int)strlen(prim_str));
            XSetForeground(dpy, gc, lcd_dim);
            XDrawString(dpy, back_buf, gc, pad_x + 10, cy + font_h * 2 + font_asc + 12, sec_line, (int)strlen(sec_line));

            /* 2. Mode & Radix Selector Strip */
            mbar_y = cy + lcd_h + 6;
            mbar_h = font_h + 10;
            int mbw = pad_w / 7;
            for (int i = 0; i < 7; i++) {
                int bx = pad_x + i * mbw;
                int bw = (i == 6) ? (pad_w - i * mbw) : (mbw - 3);
                int active = (strcasecmp(st.base, mode_bar[i]) == 0) ||
                             (i == 4 && strncasecmp(st.mode, "SCI", 3) == 0) ||
                             (i == 5 && strncasecmp(st.mode, "FIN", 3) == 0) ||
                             (i == 6 && strncasecmp(st.mode, "PROG", 4) == 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, mbar_y, bw, mbar_h,
                                active ? colors.title_bg : colors.btn_bg, active);
                XSetForeground(dpy, gc, active ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 6, mbar_y + font_asc + 3, mode_bar[i], (int)strlen(mode_bar[i]));
            }

            /* 3. Hex Digit Row (A..F) */
            hex_y = mbar_y + mbar_h + 4;
            hex_h = font_h + 10;
            int hbw = pad_w / 6;
            for (int i = 0; i < 6; i++) {
                int bx = pad_x + i * hbw;
                int bw = (i == 5) ? (pad_w - i * hbw) : (hbw - 3);
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, hex_y, bw, hex_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + bw / 2 - 4, hex_y + font_asc + 3, hex_row[i], 1);
            }

            /* 4. Main 7x5 3D Motif PushButton Keypad */
            pad_y = hex_y + hex_h + 6;
            pad_h = avail_h - (pad_y - cy);
            if (pad_h < 180) pad_h = 180;
            int cell_w = pad_w / 5;
            int cell_h = pad_h / 7;
            for (int r = 0; r < 7; r++) {
                for (int c = 0; c < 5; c++) {
                    int bx = pad_x + c * cell_w;
                    int by = pad_y + r * cell_h;
                    int bw = (c == 4) ? (pad_w - c * cell_w) : (cell_w - 4);
                    int bh = (r == 6) ? (pad_h - r * cell_h) : (cell_h - 4);
                    const char* lbl = key_labels[r][c];
                    if (r == 1 && strcasecmp(st.mode, "FINANCIAL") == 0) {
                        const char* fin_row[5] = {"PV", "RATE", "N-YR", "PMT", "x^2"};
                        lbl = fin_row[c];
                    }
                    unsigned long fill = (strcmp(lbl, "=") == 0 || strcmp(lbl, "AC") == 0) ? colors.bg_gray : colors.btn_bg;
                    draw_bevel_rect(dpy, back_buf, gc, &colors, bx, by, bw, bh, fill, 0);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, bx + 10, by + (bh + font_asc) / 2 - 2, lbl, (int)strlen(lbl));
                }
            }

            /* 5. Paper Tape Audit Panel */
            if (st.show_tape && tape_w > 0) {
                int tx = pad_x + pad_w + 8;
                draw_bevel_rect(dpy, back_buf, gc, &colors, tx, cy, tape_w, avail_h, colors.canvas_bg, 1);
                draw_bevel_rect(dpy, back_buf, gc, &colors, tx + 2, cy + 2, tape_w - 4, font_h + 8, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, tx + 8, cy + font_asc + 4, "Audit Paper Tape", 16);

                XSetForeground(dpy, gc, colors.canvas_fg);
                int line_h = font_h + 4;
                int max_vis = (avail_h - font_h - 20) / line_h;
                int start_i = (st.num_tape > max_vis) ? (st.num_tape - max_vis) : 0;
                for (int i = start_i; i < st.num_tape; i++) {
                    char tline[128];
                    snprintf(tline, sizeof(tline), "%-15s = %ld", st.tape_op[i], st.tape_res[i]);
                    XDrawString(dpy, back_buf, gc, tx + 8, cy + font_h + 16 + font_asc + (i - start_i) * line_h,
                                tline, (int)strlen(tline));
                }
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows Calculator: About",
                    "DECwindows Motif Calculator V3.0 (DECW$CALC / dxcalc)",
                    "Scientific, Financial (PV/PMT) & Programmer (HEX/OCT/BIN)",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                calc_press_key(&st, "7", cfg->state_path, status_msg, sizeof(status_msg));
                need_redraw = 1;
            }
        }

        if (autoclose_ms > 0 && exposed_once) {
            struct timeval now_tv;
            gettimeofday(&now_tv, NULL);
            long elapsed = (now_tv.tv_sec - start_tv.tv_sec) * 1000L + (now_tv.tv_usec - start_tv.tv_usec) / 1000L;
            if (elapsed >= autoclose_ms) break;
        }

        if (running) {
            int xfd = ConnectionNumber(dpy);
            fd_set fds;
            FD_ZERO(&fds);
            FD_SET(xfd, &fds);
            struct timeval tv = {0, 30000};
            select(xfd + 1, &fds, NULL, NULL, &tv);
        }
    }

    {
        char info[256];
        decw_x11_probe_display(dname, info, sizeof(info));
        printf("[DECwindows X11 Engine] Window '%s' (%s) rendered (%d lines, %d Motif buttons, Font: %s) | %s\n",
               title, cfg->app_id[0] ? cfg->app_id : "calculator", st.num_tape, 35, font_desc, info);
        fflush(stdout);
    }

    XFreePixmap(dpy, back_buf);
    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}

/* ============================================================================
 * 2. DECwindows Calendar (DECW$CALENDAR / dxcalendar)
 *    Authentic OSF/Motif 1.1 Monthly Calendar Grid & Day-Planner Time Slots
 * ============================================================================ */

typedef struct {
    char date[16];     /* YYYY-MM-DD */
    char time[12];     /* HH:MM */
    int duration;
    int alarm_on;
    char desc[128];
} DecwCalAppt;

typedef struct {
    DecwCalAppt appts[48];
    int num_appts;
    int cur_day;       /* 1..31 in Oct 1991 */
    int sel_appt;      /* index in appts[] */
    int view_mode;     /* 0=Day+Month Split, 1=All Schedule, 2=Alarms/Conflicts */
    int dialog_mode;   /* 0=none, 1=New Appt Dialog, 2=About */
    int focus_field;   /* 0=time, 1=dur, 2=desc */
    char edit_time[12];
    char edit_dur[12];
    char edit_desc[96];
    int edit_alarm;
} DecwCalState;

static void cal_add_appt(DecwCalState* st, const char* dt, const char* tm, int dur, int alm, const char* desc) {
    if (st->num_appts >= 48) return;
    DecwCalAppt* a = &st->appts[st->num_appts++];
    snprintf(a->date, sizeof(a->date), "%s", dt);
    snprintf(a->time, sizeof(a->time), "%s", tm);
    a->duration = dur;
    a->alarm_on = alm;
    snprintf(a->desc, sizeof(a->desc), "%s", desc);
}

static void cal_load_state(DecwCalState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    st->cur_day = 18;
    st->sel_appt = 0;
    strcpy(st->edit_time, "15:30");
    strcpy(st->edit_dur, "60");
    strcpy(st->edit_desc, "DECwindows Motif Engineering Review");
    st->edit_alarm = 1;

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[256];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            char dt[16] = "", tm[12] = "", alm_s[8] = "", desc[128] = "";
            int dur = 0;
            if (sscanf(line, "%15[^|]|%11[^|]|%d|%7[^|]|%127[^\n]", dt, tm, &dur, alm_s, desc) == 5) {
                cal_add_appt(st, dt, tm, dur, strcasecmp(alm_s, "ON") == 0 ? 1 : 0, desc);
            }
        }
        fclose(fp);
    }
    if (st->num_appts == 0) {
        cal_add_appt(st, "1991-10-18", "09:00", 60, 1, "VAX/VMS V5.5 Release Engineering Sign-off (ZKO2-3/Q18)");
        cal_add_appt(st, "1991-10-18", "11:00", 45, 1, "DECwindows XUI to OSF/Motif Toolkit Porting Review");
        cal_add_appt(st, "1991-10-18", "14:30", 90, 0, "Alpha AXP 64-Bit Architecture Briefing with Hudson Team");
        cal_add_appt(st, "1991-10-21", "10:00", 60, 1, "DECUS Fall Symposium Keynote Preparation (Anaheim)");
        cal_add_appt(st, "1991-10-24", "13:00", 30, 0, "ULTRIX Workstation Field Service Diagnostics Sync");
        cal_add_appt(st, "1991-10-28", "16:00", 120, 1, "VAXcluster CI780 Star Coupler Maintenance Window");
    }
}

static void cal_save_state(const DecwCalState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    for (int i = 0; i < st->num_appts; i++) {
        fprintf(fp, "%s|%s|%d|%s|%s\n",
                st->appts[i].date, st->appts[i].time, st->appts[i].duration,
                st->appts[i].alarm_on ? "ON" : "OFF", st->appts[i].desc);
    }
    fclose(fp);
}

static int cal_day_has_appt(const DecwCalState* st, int day) {
    char target[16];
    snprintf(target, sizeof(target), "1991-10-%02d", day);
    int cnt = 0;
    for (int i = 0; i < st->num_appts; i++) {
        if (strcmp(st->appts[i].date, target) == 0) cnt++;
    }
    return cnt;
}

static int run_calendar_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "calendar", &colors);

    int font_scale = (disp_w >= 2560) ? 3 : 2;
    char custom_xlfd[128] = "";
    if (getenv("DECW_FONT_SIZE")) {
        int s = parse_font_spec_to_scale(getenv("DECW_FONT_SIZE"), custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (cfg->font_scale >= 1 && cfg->font_scale <= 6) font_scale = cfg->font_scale;
    if (cfg->font_spec[0]) {
        int s = parse_font_spec_to_scale(cfg->font_spec, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }

    char font_desc[96] = "";
    int rec_w = 1040, rec_h = 720;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 480) ? cfg->width : (720 + font_scale * 110);
    int win_h = (cfg->height >= 360) ? cfg->height : (480 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 80, 80,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Calendar - October 1991";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$CALENDAR");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwCalState st;
    cal_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Open Sample Schedule", 101},
        {"Save Schedule",        102},
        {"---",                  0},
        {"Exit",                 109}
    };
    static const DecwMenuItem edit_items[] = {
        {"New Appointment...",   201},
        {"Toggle Selected Alarm",202},
        {"Delete Selected Entry",203}
    };
    static const DecwMenuItem view_items[] = {
        {"Day + Month View",     301},
        {"All Scheduled Entries",302},
        {"Alarms & Conflicts",   303},
        {"---",                  0},
        {"Jump to Oct 18, 1991", 304}
    };
    static const DecwMenuItem help_items[] = {
        {"About Calendar...",    401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File", 0, 0, 0, file_items, 4},
        {"Edit", 0, 0, 0, edit_items, 3},
        {"View", 0, 0, 0, view_items, 5},
        {"Help", 0, 0, 1, help_items, 1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "Date: 1991-10-%02d | %d appointments scheduled | Click any day on calendar grid",
             st.cur_day, st.num_appts);

    XMapWindow(dpy, win);
    XFlush(dpy);

    int autoclose_ms = cfg->autoclose_ms;
    const char* env_ac = getenv("DECW_X11_AUTOCLOSE_MS");
    if (autoclose_ms <= 0 && env_ac && env_ac[0]) autoclose_ms = atoi(env_ac);
    if (cfg->verify_only && autoclose_ms <= 0) autoclose_ms = 120;

    struct timeval start_tv;
    gettimeofday(&start_tv, NULL);
    int exposed_once = 0, need_redraw = 0, sent_synth = 0, running = 1;
    int open_menu = -1;
    int ok_x = 0, ok_y = 0, ok_w = 0, ok_h = 0;
    int grid_x = 12, grid_y = 140, grid_w = 340, grid_h = 280;
    int list_x = 365, list_y = 140, list_w = 400, list_h = 280;
    int tb_y = 85, tb_h = 34;

    while (running) {
        while (XPending(dpy) > 0) {
            XEvent ev;
            XNextEvent(dpy, &ev);
            int font_h = (font ? (font->ascent + font->descent) : 18);
            if (font_h < 14) font_h = 14;

            if (ev.type == ConfigureNotify) {
                if (ev.xconfigure.width != win_w || ev.xconfigure.height != win_h) {
                    win_w = ev.xconfigure.width;
                    win_h = ev.xconfigure.height;
                    need_redraw = 1;
                }
            } else if (ev.type == Expose && ev.xexpose.count == 0) {
                exposed_once = 1;
                need_redraw = 1;
            } else if (ev.type == ButtonPress && ev.xbutton.button == Button1) {
                int mx = ev.xbutton.x, my = ev.xbutton.y;
                need_redraw = 1;

                if (st.dialog_mode == 2) {
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) st.dialog_mode = 0;
                    continue;
                } else if (st.dialog_mode == 1) {
                    int dw = (win_w - 60 < 540) ? (win_w - 60) : 540;
                    int dh = font_h * 10 + 70;
                    int dx = (win_w - dw) / 2;
                    int dy = (win_h - dh) / 2;
                    int fy0 = dy + font_h * 2 + 12;
                    int fh = font_h + 10;
                    if (my >= fy0 && my <= fy0 + fh) st.focus_field = 0;
                    else if (my >= fy0 + fh + 6 && my <= fy0 + (fh + 6) * 2) st.focus_field = 1;
                    else if (my >= fy0 + (fh + 6) * 2 && my <= fy0 + (fh + 6) * 3) st.focus_field = 2;
                    else if (my >= fy0 + (fh + 6) * 3 && my <= fy0 + (fh + 6) * 4) st.edit_alarm = !st.edit_alarm;
                    else if (my >= dy + dh - fh - 12 && my <= dy + dh - 8) {
                        if (mx < dx + dw / 2) {
                            char dt[16];
                            snprintf(dt, sizeof(dt), "1991-10-%02d", st.cur_day);
                            int dur = atoi(st.edit_dur);
                            if (dur <= 0) dur = 30;
                            cal_add_appt(&st, dt, st.edit_time[0] ? st.edit_time : "10:00",
                                         dur, st.edit_alarm, st.edit_desc[0] ? st.edit_desc : "Meeting");
                            cal_save_state(&st, cfg->state_path);
                            snprintf(status_msg, sizeof(status_msg), "Added appointment on %s at %s", dt, st.edit_time);
                        }
                        st.dialog_mode = 0;
                    }
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) { cal_load_state(&st, NULL); cal_save_state(&st, cfg->state_path); }
                    else if (mact == 102) { cal_save_state(&st, cfg->state_path); snprintf(status_msg, sizeof(status_msg), "Saved schedule to %.160s", cfg->state_path); }
                    else if (mact == 109) running = 0;
                    else if (mact == 201) st.dialog_mode = 1;
                    else if (mact == 202 && st.sel_appt >= 0 && st.sel_appt < st.num_appts) {
                        st.appts[st.sel_appt].alarm_on = !st.appts[st.sel_appt].alarm_on;
                        cal_save_state(&st, cfg->state_path);
                    } else if (mact == 203 && st.sel_appt >= 0 && st.sel_appt < st.num_appts) {
                        for (int i = st.sel_appt; i < st.num_appts - 1; i++) st.appts[i] = st.appts[i + 1];
                        if (st.num_appts > 0) st.num_appts--;
                        if (st.sel_appt >= st.num_appts) st.sel_appt = st.num_appts - 1;
                        cal_save_state(&st, cfg->state_path);
                    } else if (mact == 301) st.view_mode = 0;
                    else if (mact == 302) st.view_mode = 1;
                    else if (mact == 303) st.view_mode = 2;
                    else if (mact == 304) st.cur_day = 18;
                    else if (mact == 401) st.dialog_mode = 2;
                    continue;
                }

                /* Toolbar buttons */
                if (my >= tb_y && my <= tb_y + tb_h) {
                    int b_idx = (mx - 10) * 6 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b_idx == 0 && st.cur_day > 1) st.cur_day--;
                    else if (b_idx == 1) st.cur_day = 18;
                    else if (b_idx == 2 && st.cur_day < 31) st.cur_day++;
                    else if (b_idx == 3) st.dialog_mode = 1;
                    else if (b_idx == 4 && st.sel_appt >= 0 && st.sel_appt < st.num_appts) {
                        st.appts[st.sel_appt].alarm_on = !st.appts[st.sel_appt].alarm_on;
                        cal_save_state(&st, cfg->state_path);
                    } else if (b_idx == 5) {
                        st.view_mode = (st.view_mode + 1) % 3;
                    }
                    snprintf(status_msg, sizeof(status_msg), "Selected Date: 1991-10-%02d (%d appointments on day)",
                             st.cur_day, cal_day_has_appt(&st, st.cur_day));
                    continue;
                }

                /* Monthly calendar grid click (Oct 1991 starts on Tuesday = col 2) */
                int cells_y = grid_y + (font_h + 12) * 2;
                int cells_h = grid_h - (font_h + 12) * 2;
                if (mx >= grid_x && mx < grid_x + grid_w && my >= cells_y && my < cells_y + cells_h) {
                    int col = (mx - grid_x) * 7 / grid_w;
                    int row = (my - cells_y) * 5 / cells_h;
                    int d = row * 7 + col - 2 + 1; /* Oct 1, 1991 is Tuesday (col 2) */
                    if (d >= 1 && d <= 31) {
                        st.cur_day = d;
                        snprintf(status_msg, sizeof(status_msg), "Selected Oct %d, 1991 (%d scheduled entries)",
                                 d, cal_day_has_appt(&st, d));
                    }
                    continue;
                }

                /* Appointment list click */
                if (mx >= list_x && mx < list_x + list_w && my >= list_y + font_h + 14 && my < list_y + list_h) {
                    int row = (my - (list_y + font_h + 14)) / ((font_h + 6) * 2);
                    if (row >= 0 && row < st.num_appts) {
                        st.sel_appt = row;
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                int n = XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                kbuf[n] = '\0';
                need_redraw = 1;
                if (st.dialog_mode == 1) {
                    char* fld = (st.focus_field == 0) ? st.edit_time : (st.focus_field == 1 ? st.edit_dur : st.edit_desc);
                    size_t maxl = (st.focus_field == 0) ? 10 : (st.focus_field == 1 ? 8 : 90);
                    if (ks == XK_Escape) st.dialog_mode = 0;
                    else if (ks == XK_Tab) st.focus_field = (st.focus_field + 1) % 3;
                    else if (ks == XK_Return || ks == XK_KP_Enter) {
                        char dt[16];
                        snprintf(dt, sizeof(dt), "1991-10-%02d", st.cur_day);
                        cal_add_appt(&st, dt, st.edit_time, atoi(st.edit_dur) > 0 ? atoi(st.edit_dur) : 30, st.edit_alarm, st.edit_desc);
                        cal_save_state(&st, cfg->state_path);
                        st.dialog_mode = 0;
                    } else if (ks == XK_BackSpace && strlen(fld) > 0) {
                        fld[strlen(fld) - 1] = '\0';
                    } else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127 && strlen(fld) + 1 < maxl) {
                        size_t l = strlen(fld);
                        fld[l] = kbuf[0];
                        fld[l + 1] = '\0';
                    }
                } else {
                    if (ks == XK_Escape) {
                        if (st.dialog_mode != 0) st.dialog_mode = 0;
                        else running = 0;
                    } else if (ks == XK_Left && st.cur_day > 1) st.cur_day--;
                    else if (ks == XK_Right && st.cur_day < 31) st.cur_day++;
                    else if (ks == XK_F10 || ks == XK_Next) {
                        if (font_scale > 1) font_scale--;
                        if (font) XFreeFont(dpy, font);
                        font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                        if (font) XSetFont(dpy, gc, font->fid);
                    } else if (ks == XK_F11 || ks == XK_Prior) {
                        if (font_scale < 6) font_scale++;
                        if (font) XFreeFont(dpy, font);
                        font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                        if (font) XSetFont(dpy, gc, font->fid);
                    }
                }
            } else if (ev.type == ClientMessage && (Atom)ev.xclient.data.l[0] == wm_delete) {
                running = 0;
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
            int font_h = font ? (font->ascent + font->descent) : 18;
            if (font_h < 14) font_h = 14;
            int cy = 0;
            draw_motif_chrome_and_menubar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                                          title, menus, 4, open_menu, &cy);

            /* Top Navigation & Action Toolbar */
            tb_y = cy;
            tb_h = font_h + 14;
            const char* tb_lbls[6] = {"< Prev Day", "Oct 18 Today", "Next Day >", "+ New Appt...", "Toggle Alarm", "Switch View"};
            int bw = (win_w - 20) / 6;
            for (int i = 0; i < 6; i++) {
                int bx = 10 + i * bw;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, tb_y, bw - 4, tb_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, tb_y + font_asc + 4, tb_lbls[i], (int)strlen(tb_lbls[i]));
            }

            int st_h = font_h + 10;
            grid_y = tb_y + tb_h + 6;
            grid_h = win_h - grid_y - st_h - 14;
            grid_x = 10;
            grid_w = (win_w - 28) * 44 / 100;
            list_x = grid_x + grid_w + 8;
            list_y = grid_y;
            list_w = win_w - list_x - 10;
            list_h = grid_h;

            /* Left Pane: Monthly Calendar Grid (October 1991) */
            draw_bevel_rect(dpy, back_buf, gc, &colors, grid_x, grid_y, grid_w, grid_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, grid_x + 2, grid_y + 2, grid_w - 4, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, grid_x + 12, grid_y + font_asc + 5, "OCTOBER 1991  (Click Day)", 25);

            const char* dow[7] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
            int cw = (grid_w - 8) / 7;
            int dow_y = grid_y + font_h + 14;
            for (int c = 0; c < 7; c++) {
                draw_bevel_rect(dpy, back_buf, gc, &colors, grid_x + 4 + c * cw, dow_y, cw - 2, font_h + 8, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, grid_x + 8 + c * cw, dow_y + font_asc + 2, dow[c], 3);
            }

            int cells_y = dow_y + font_h + 10;
            int ch = (grid_h - (cells_y - grid_y) - 6) / 5;
            for (int r = 0; r < 5; r++) {
                for (int c = 0; c < 7; c++) {
                    int d = r * 7 + c - 2 + 1;
                    int cx = grid_x + 4 + c * cw;
                    int ry = cells_y + r * ch;
                    if (d >= 1 && d <= 31) {
                        int has_a = cal_day_has_appt(&st, d);
                        int is_sel = (d == st.cur_day);
                        unsigned long fill = is_sel ? colors.title_bg : (has_a ? colors.btn_bg : colors.canvas_bg);
                        draw_bevel_rect(dpy, back_buf, gc, &colors, cx, ry, cw - 2, ch - 2, fill, is_sel);
                        char dstr[16];
                        snprintf(dstr, sizeof(dstr), "%2d%s", d, has_a ? "*" : "");
                        XSetForeground(dpy, gc, is_sel ? colors.title_fg : colors.canvas_fg);
                        XDrawString(dpy, back_buf, gc, cx + 6, ry + font_asc + 4, dstr, (int)strlen(dstr));
                    } else {
                        draw_bevel_rect(dpy, back_buf, gc, &colors, cx, ry, cw - 2, ch - 2, colors.bg_gray, 1);
                    }
                }
            }

            /* Right Pane: Day-Planner Schedule & Time-Slot Entries */
            draw_bevel_rect(dpy, back_buf, gc, &colors, list_x, list_y, list_w, list_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, list_x + 2, list_y + 2, list_w - 4, font_h + 10, colors.title_bg, 0);
            char hdr_buf[128];
            snprintf(hdr_buf, sizeof(hdr_buf), "Day-Planner: 1991-10-%02d & Upcoming Schedule", st.cur_day);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, list_x + 10, list_y + font_asc + 5, hdr_buf, (int)strlen(hdr_buf));

            char sel_dt[16];
            snprintf(sel_dt, sizeof(sel_dt), "1991-10-%02d", st.cur_day);
            int row_h = (font_h + 6) * 2;
            int ry = list_y + font_h + 16;
            for (int i = 0; i < st.num_appts && ry + row_h < list_y + list_h - 4; i++) {
                int match_day = (strcmp(st.appts[i].date, sel_dt) == 0);
                int is_sel = (i == st.sel_appt);
                unsigned long rfill = is_sel ? colors.btn_bg : (match_day ? colors.bevel_light : colors.canvas_bg);
                draw_bevel_rect(dpy, back_buf, gc, &colors, list_x + 6, ry, list_w - 12, row_h - 4, rfill, is_sel);

                char l1[160], l2[160];
                snprintf(l1, sizeof(l1), "[#%d] %s  %s (%d min)  %s %s",
                         i + 1, st.appts[i].date, st.appts[i].time, st.appts[i].duration,
                         st.appts[i].alarm_on ? "[BELL:ON]" : "[BELL:OFF]",
                         match_day ? "<-- SELECTED DAY" : "");
                snprintf(l2, sizeof(l2), "     %s", st.appts[i].desc);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, list_x + 12, ry + font_asc + 2, l1, (int)strlen(l1));
                XDrawString(dpy, back_buf, gc, list_x + 12, ry + font_h + font_asc + 4, l2, (int)strlen(l2));
                ry += row_h;
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                int dw = (win_w - 60 < 540) ? (win_w - 60) : 540;
                int dh = font_h * 10 + 70;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, font_h + 8, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 6 + font_asc, "Calendar: Schedule New Appointment", 34);

                int fy0 = dy + font_h * 2 + 12;
                int fh = font_h + 10;
                const char* flbls[3] = {"Time (HH:MM):", "Duration (m):", "Description:"};
                const char* fvals[3] = {st.edit_time, st.edit_dur, st.edit_desc};
                for (int f = 0; f < 3; f++) {
                    int fy = fy0 + f * (fh + 6);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, dx + 14, fy + font_asc + 2, flbls[f], (int)strlen(flbls[f]));
                    draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 160, fy, dw - 176, fh, colors.cmd_bg, 1);
                    char vbuf[110];
                    snprintf(vbuf, sizeof(vbuf), "%s%s", fvals[f], (st.focus_field == f) ? "_" : "");
                    XDrawString(dpy, back_buf, gc, dx + 166, fy + font_asc + 2, vbuf, (int)strlen(vbuf));
                }
                int ay = fy0 + 3 * (fh + 6);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 160, ay, dw - 176, fh, colors.btn_bg, st.edit_alarm);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 168, ay + font_asc + 2,
                            st.edit_alarm ? "[X] Reminder Alarm Bell ON" : "[ ] Reminder Alarm Bell OFF", 27);

                int by = dy + dh - fh - 12;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 40, by, 140, fh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + dw - 180, by, 140, fh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 68, by + font_asc + 3, "Add Entry", 9);
                XDrawString(dpy, back_buf, gc, dx + dw - 140, by + font_asc + 3, "Cancel", 6);
            } else if (st.dialog_mode == 2) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows Calendar: About",
                    "DECwindows Motif Calendar V3.0 (DECW$CALENDAR / dxcalendar)",
                    "Personal & Workgroup Time-Slot Planner, Alarms & Conflict Audit",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                st.cur_day = 21;
                need_redraw = 1;
            }
        }

        if (autoclose_ms > 0 && exposed_once) {
            struct timeval now_tv;
            gettimeofday(&now_tv, NULL);
            long elapsed = (now_tv.tv_sec - start_tv.tv_sec) * 1000L + (now_tv.tv_usec - start_tv.tv_usec) / 1000L;
            if (elapsed >= autoclose_ms) break;
        }

        if (running) {
            int xfd = ConnectionNumber(dpy);
            fd_set fds;
            FD_ZERO(&fds);
            FD_SET(xfd, &fds);
            struct timeval tv = {0, 30000};
            select(xfd + 1, &fds, NULL, NULL, &tv);
        }
    }

    {
        char info[256];
        decw_x11_probe_display(dname, info, sizeof(info));
        printf("[DECwindows X11 Engine] Window '%s' (%s) rendered (%d lines, %d Motif buttons, Font: %s) | %s\n",
               title, cfg->app_id[0] ? cfg->app_id : "calendar", st.num_appts, 12, font_desc, info);
        fflush(stdout);
    }

    XFreePixmap(dpy, back_buf);
    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}

/* ============================================================================
 * 3. DECwindows Cardfiler (DECW$CARDFILER / dxcardfiler)
 *    Authentic OSF/Motif 1.1 Rotary Index Deck & 3x5 Electronic Index Card
 * ============================================================================ */

typedef struct {
    char index[64];
    char category[32];
    char node[64];
    char body[192];
} DecwCard;

typedef struct {
    DecwCard cards[48];
    int num_cards;
    int cur_card;
    int dialog_mode;   /* 0=none, 1=Add/Edit Card, 2=About */
    int edit_is_new;
    int focus_field;   /* 0=index, 1=category, 2=node, 3=body */
    char f_index[64];
    char f_cat[32];
    char f_node[64];
    char f_body[160];
} DecwCardState;

static void card_add(DecwCardState* st, const char* idx, const char* cat, const char* node, const char* body) {
    if (st->num_cards >= 48) return;
    DecwCard* c = &st->cards[st->num_cards++];
    snprintf(c->index, sizeof(c->index), "%s", idx);
    snprintf(c->category, sizeof(c->category), "%s", cat);
    snprintf(c->node, sizeof(c->node), "%s", node);
    snprintf(c->body, sizeof(c->body), "%s", body);
}

static void card_load_state(DecwCardState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[320];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            char idx[64] = "", cat[32] = "", node[64] = "", body[192] = "";
            if (sscanf(line, "%63[^|]|%31[^|]|%63[^|]|%191[^\n]", idx, cat, node, body) == 4) {
                card_add(st, idx, cat, node, body);
            }
        }
        fclose(fp);
    }
    if (st->num_cards == 0) {
        card_add(st, "Bell, Gordon", "ENGINEERING", "MLO::BELL (DTN 223-4100)",
                 "VP of Engineering - PDP-11, VAX-11/780 Architecture, Maynard Mill MLO");
        card_add(st, "Cutler, Dave", "VAX/VMS", "ZKO::CUTLER (DTN 381-2001)",
                 "RSX-11M, VAX/VMS, MicroVAX I/II, VAXeln & DECwest Bellevue Lab");
        card_add(st, "Kronenberg, Nancy", "VAXCLUSTER", "MRO::NANCY (DTN 297-5120)",
                 "Computer Interconnect (CI780), SCA Protocol, HSC50 Storage Controller");
        card_add(st, "Stewart, Larry", "ULTRIX", "CRL::STEWART (DTN 226-8900)",
                 "Cambridge Research Lab - Firefly Multiprocessor & DECstation 3100");
        card_add(st, "Customer Response Ctr", "SUPPORT", "CSC::HELP (1-800-332-8000)",
                 "Colorado Springs Field Service & Software Patch Distribution Center");
        card_add(st, "DECUS Program Library", "DECUS", "MR1::DECUS (DTN 231-6500)",
                 "Digital Equipment Computer Users Society Symposia & SIG Tape Catalog");
    }
}

static void card_save_state(const DecwCardState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    for (int i = 0; i < st->num_cards; i++) {
        fprintf(fp, "%s|%s|%s|%s\n",
                st->cards[i].index, st->cards[i].category, st->cards[i].node, st->cards[i].body);
    }
    fclose(fp);
}

static void card_sort(DecwCardState* st, int by_cat) {
    for (int i = 0; i < st->num_cards - 1; i++) {
        for (int j = i + 1; j < st->num_cards; j++) {
            const char* a = by_cat ? st->cards[i].category : st->cards[i].index;
            const char* b = by_cat ? st->cards[j].category : st->cards[j].index;
            if (strcasecmp(a, b) > 0) {
                DecwCard tmp = st->cards[i];
                st->cards[i] = st->cards[j];
                st->cards[j] = tmp;
            }
        }
    }
}

static int run_cardfiler_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "cardfiler", &colors);
    unsigned long crimson = alloc_color(dpy, screen, "#B82028", BlackPixel(dpy, screen));
    unsigned long rule_blue = alloc_color(dpy, screen, "#98B8D8", BlackPixel(dpy, screen));

    int font_scale = (disp_w >= 2560) ? 3 : 2;
    char custom_xlfd[128] = "";
    if (getenv("DECW_FONT_SIZE")) {
        int s = parse_font_spec_to_scale(getenv("DECW_FONT_SIZE"), custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }
    if (cfg->font_scale >= 1 && cfg->font_scale <= 6) font_scale = cfg->font_scale;
    if (cfg->font_spec[0]) {
        int s = parse_font_spec_to_scale(cfg->font_spec, custom_xlfd, sizeof(custom_xlfd));
        if (s > 0) font_scale = s;
    }

    char font_desc[96] = "";
    int rec_w = 1020, rec_h = 680;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 480) ? cfg->width : (700 + font_scale * 105);
    int win_h = (cfg->height >= 360) ? cfg->height : (450 + font_scale * 70);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 85, 85,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Cardfiler - DEC_SYSTEMS.CRD";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$CARDFILER");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwCardState st;
    card_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Open Sample Deck", 101},
        {"Save Card Deck",   102},
        {"---",              0},
        {"Exit",             109}
    };
    static const DecwMenuItem card_items[] = {
        {"Add New Card...",  201},
        {"Edit Current...",  202},
        {"Duplicate Card",   203},
        {"Delete Card",      204}
    };
    static const DecwMenuItem view_items[] = {
        {"Next Card",        301},
        {"Previous Card",    302},
        {"---",              0},
        {"Sort by Index",    303},
        {"Sort by Category", 304}
    };
    static const DecwMenuItem help_items[] = {
        {"About Cardfiler...", 401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File", 0, 0, 0, file_items, 4},
        {"Card", 0, 0, 0, card_items, 4},
        {"View", 0, 0, 0, view_items, 5},
        {"Help", 0, 0, 1, help_items, 1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "Card 1 of %d: %s | Click index list or navigation buttons",
             st.num_cards, st.cards[0].index);

    XMapWindow(dpy, win);
    XFlush(dpy);

    int autoclose_ms = cfg->autoclose_ms;
    const char* env_ac = getenv("DECW_X11_AUTOCLOSE_MS");
    if (autoclose_ms <= 0 && env_ac && env_ac[0]) autoclose_ms = atoi(env_ac);
    if (cfg->verify_only && autoclose_ms <= 0) autoclose_ms = 120;

    struct timeval start_tv;
    gettimeofday(&start_tv, NULL);
    int exposed_once = 0, need_redraw = 0, sent_synth = 0, running = 1;
    int open_menu = -1;
    int ok_x = 0, ok_y = 0, ok_w = 0, ok_h = 0;
    int idx_x = 10, idx_y = 120, idx_w = 280, idx_h = 260;
    int tb_y = 82, tb_h = 34;

    while (running) {
        while (XPending(dpy) > 0) {
            XEvent ev;
            XNextEvent(dpy, &ev);
            int font_h = (font ? (font->ascent + font->descent) : 18);
            if (font_h < 14) font_h = 14;

            if (ev.type == ConfigureNotify) {
                if (ev.xconfigure.width != win_w || ev.xconfigure.height != win_h) {
                    win_w = ev.xconfigure.width;
                    win_h = ev.xconfigure.height;
                    need_redraw = 1;
                }
            } else if (ev.type == Expose && ev.xexpose.count == 0) {
                exposed_once = 1;
                need_redraw = 1;
            } else if (ev.type == ButtonPress && ev.xbutton.button == Button1) {
                int mx = ev.xbutton.x, my = ev.xbutton.y;
                need_redraw = 1;

                if (st.dialog_mode == 2) {
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) st.dialog_mode = 0;
                    continue;
                } else if (st.dialog_mode == 1) {
                    int dw = (win_w - 60 < 560) ? (win_w - 60) : 560;
                    int dh = font_h * 10 + 70;
                    int dx = (win_w - dw) / 2;
                    int dy = (win_h - dh) / 2;
                    int fy0 = dy + font_h * 2 + 12;
                    int fh = font_h + 10;
                    for (int f = 0; f < 4; f++) {
                        if (my >= fy0 + f * (fh + 6) && my <= fy0 + (f + 1) * (fh + 6)) st.focus_field = f;
                    }
                    if (my >= dy + dh - fh - 12 && my <= dy + dh - 8) {
                        if (mx < dx + dw / 2) {
                            if (st.edit_is_new) {
                                card_add(&st, st.f_index[0] ? st.f_index : "New Entry",
                                         st.f_cat[0] ? st.f_cat : "GENERAL",
                                         st.f_node[0] ? st.f_node : "NODE::USER",
                                         st.f_body[0] ? st.f_body : "Index card notes.");
                                st.cur_card = st.num_cards - 1;
                            } else if (st.cur_card >= 0 && st.cur_card < st.num_cards) {
                                snprintf(st.cards[st.cur_card].index, 64, "%s", st.f_index);
                                snprintf(st.cards[st.cur_card].category, 32, "%s", st.f_cat);
                                snprintf(st.cards[st.cur_card].node, 64, "%s", st.f_node);
                                snprintf(st.cards[st.cur_card].body, 192, "%s", st.f_body);
                            }
                            card_save_state(&st, cfg->state_path);
                        }
                        st.dialog_mode = 0;
                    }
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) { card_load_state(&st, NULL); card_save_state(&st, cfg->state_path); }
                    else if (mact == 102) { card_save_state(&st, cfg->state_path); }
                    else if (mact == 109) running = 0;
                    else if (mact == 201) {
                        st.edit_is_new = 1;
                        strcpy(st.f_index, "Supnik, Bob");
                        strcpy(st.f_cat, "ALPHA");
                        strcpy(st.f_node, "ZKO::SUPNIK");
                        strcpy(st.f_body, "NVAX, Alpha EV4/EV5 Microprocessor & SIMH Simulator Architect");
                        st.dialog_mode = 1;
                    } else if (mact == 202 && st.num_cards > 0) {
                        st.edit_is_new = 0;
                        strcpy(st.f_index, st.cards[st.cur_card].index);
                        strcpy(st.f_cat, st.cards[st.cur_card].category);
                        strcpy(st.f_node, st.cards[st.cur_card].node);
                        strcpy(st.f_body, st.cards[st.cur_card].body);
                        st.dialog_mode = 1;
                    } else if (mact == 203 && st.num_cards > 0) {
                        DecwCard c = st.cards[st.cur_card];
                        card_add(&st, c.index, c.category, c.node, c.body);
                        st.cur_card = st.num_cards - 1;
                        card_save_state(&st, cfg->state_path);
                    } else if (mact == 204 && st.num_cards > 1) {
                        for (int i = st.cur_card; i < st.num_cards - 1; i++) st.cards[i] = st.cards[i + 1];
                        st.num_cards--;
                        if (st.cur_card >= st.num_cards) st.cur_card = st.num_cards - 1;
                        card_save_state(&st, cfg->state_path);
                    } else if (mact == 301 && st.num_cards > 0) st.cur_card = (st.cur_card + 1) % st.num_cards;
                    else if (mact == 302 && st.num_cards > 0) st.cur_card = (st.cur_card + st.num_cards - 1) % st.num_cards;
                    else if (mact == 303) { card_sort(&st, 0); card_save_state(&st, cfg->state_path); }
                    else if (mact == 304) { card_sort(&st, 1); card_save_state(&st, cfg->state_path); }
                    else if (mact == 401) st.dialog_mode = 2;
                    continue;
                }

                /* Toolbar click */
                if (my >= tb_y && my <= tb_y + tb_h) {
                    int b_idx = (mx - 10) * 6 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b_idx == 0 && st.num_cards > 0) st.cur_card = (st.cur_card + st.num_cards - 1) % st.num_cards;
                    else if (b_idx == 1 && st.num_cards > 0) st.cur_card = (st.cur_card + 1) % st.num_cards;
                    else if (b_idx == 2) {
                        st.edit_is_new = 1;
                        strcpy(st.f_index, "Supnik, Bob");
                        strcpy(st.f_cat, "ALPHA");
                        strcpy(st.f_node, "ZKO::SUPNIK");
                        strcpy(st.f_body, "NVAX, Alpha EV4/EV5 Microprocessor & SIMH Simulator Architect");
                        st.dialog_mode = 1;
                    } else if (b_idx == 3 && st.num_cards > 0) {
                        st.edit_is_new = 0;
                        strcpy(st.f_index, st.cards[st.cur_card].index);
                        strcpy(st.f_cat, st.cards[st.cur_card].category);
                        strcpy(st.f_node, st.cards[st.cur_card].node);
                        strcpy(st.f_body, st.cards[st.cur_card].body);
                        st.dialog_mode = 1;
                    } else if (b_idx == 4) { card_sort(&st, 0); card_save_state(&st, cfg->state_path); }
                    else if (b_idx == 5) { card_sort(&st, 1); card_save_state(&st, cfg->state_path); }
                    if (st.num_cards > 0) {
                        snprintf(status_msg, sizeof(status_msg), "Card %d of %d: %s [%s]",
                                 st.cur_card + 1, st.num_cards, st.cards[st.cur_card].index, st.cards[st.cur_card].category);
                    }
                    continue;
                }

                /* Rotary Index List click */
                if (mx >= idx_x && mx < idx_x + idx_w && my >= idx_y + font_h + 14 && my < idx_y + idx_h) {
                    int row = (my - (idx_y + font_h + 14)) / (font_h + 10);
                    if (row >= 0 && row < st.num_cards) {
                        st.cur_card = row;
                        snprintf(status_msg, sizeof(status_msg), "Flipped to Card #%d: %s", row + 1, st.cards[row].index);
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                int n = XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                kbuf[n] = '\0';
                need_redraw = 1;
                if (st.dialog_mode == 1) {
                    char* fld = (st.focus_field == 0) ? st.f_index :
                                (st.focus_field == 1 ? st.f_cat : (st.focus_field == 2 ? st.f_node : st.f_body));
                    size_t maxl = (st.focus_field == 1) ? 28 : (st.focus_field == 3 ? 150 : 60);
                    if (ks == XK_Escape) st.dialog_mode = 0;
                    else if (ks == XK_Tab) st.focus_field = (st.focus_field + 1) % 4;
                    else if (ks == XK_BackSpace && strlen(fld) > 0) fld[strlen(fld) - 1] = '\0';
                    else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127 && strlen(fld) + 1 < maxl) {
                        size_t l = strlen(fld);
                        fld[l] = kbuf[0];
                        fld[l + 1] = '\0';
                    }
                } else {
                    if (ks == XK_Escape) running = 0;
                    else if ((ks == XK_Down || ks == XK_Right) && st.num_cards > 0) st.cur_card = (st.cur_card + 1) % st.num_cards;
                    else if ((ks == XK_Up || ks == XK_Left) && st.num_cards > 0) st.cur_card = (st.cur_card + st.num_cards - 1) % st.num_cards;
                    else if (ks == XK_F10 || ks == XK_Next) {
                        if (font_scale > 1) font_scale--;
                        if (font) XFreeFont(dpy, font);
                        font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                        if (font) XSetFont(dpy, gc, font->fid);
                    } else if (ks == XK_F11 || ks == XK_Prior) {
                        if (font_scale < 6) font_scale++;
                        if (font) XFreeFont(dpy, font);
                        font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
                        if (font) XSetFont(dpy, gc, font->fid);
                    }
                }
            } else if (ev.type == ClientMessage && (Atom)ev.xclient.data.l[0] == wm_delete) {
                running = 0;
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
            int font_h = font ? (font->ascent + font->descent) : 18;
            if (font_h < 14) font_h = 14;
            int cy = 0;
            draw_motif_chrome_and_menubar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                                          title, menus, 4, open_menu, &cy);

            tb_y = cy;
            tb_h = font_h + 14;
            const char* tb_lbls[6] = {"< Prev Card", "Next Card >", "+ Add Card...", "Edit Card...", "Sort Index", "Sort Category"};
            int bw = (win_w - 20) / 6;
            for (int i = 0; i < 6; i++) {
                int bx = 10 + i * bw;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, tb_y, bw - 4, tb_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, tb_y + font_asc + 4, tb_lbls[i], (int)strlen(tb_lbls[i]));
            }

            int st_h = font_h + 10;
            idx_x = 10;
            idx_y = tb_y + tb_h + 6;
            idx_w = (win_w - 28) * 38 / 100;
            idx_h = win_h - idx_y - st_h - 14;

            /* Left Pane: Rotary Index List */
            draw_bevel_rect(dpy, back_buf, gc, &colors, idx_x, idx_y, idx_w, idx_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, idx_x + 2, idx_y + 2, idx_w - 4, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, idx_x + 10, idx_y + font_asc + 5, "Rotary Card Index List", 22);

            int row_h = font_h + 10;
            for (int i = 0; i < st.num_cards; i++) {
                int ry = idx_y + font_h + 16 + i * row_h;
                if (ry + row_h > idx_y + idx_h - 4) break;
                int sel = (i == st.cur_card);
                draw_bevel_rect(dpy, back_buf, gc, &colors, idx_x + 4, ry, idx_w - 8, row_h - 2,
                                sel ? colors.title_bg : colors.btn_bg, sel);
                char rstr[96];
                snprintf(rstr, sizeof(rstr), "%s  [%s]", st.cards[i].index, st.cards[i].category);
                XSetForeground(dpy, gc, sel ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, idx_x + 10, ry + font_asc + 2, rstr, (int)strlen(rstr));
            }

            /* Right Pane: 3x5 Electronic Index Card */
            int cx = idx_x + idx_w + 8;
            int cw = win_w - cx - 10;
            draw_bevel_rect(dpy, back_buf, gc, &colors, cx, idx_y, cw, idx_h, colors.bg_gray, 1);

            /* Stacked 3x5 Card Effect with Drop Shadow */
            int card_x = cx + 16, card_y = idx_y + 16;
            int card_w = cw - 32, card_h = idx_h - 32;
            XSetForeground(dpy, gc, colors.bevel_dark);
            XFillRectangle(dpy, back_buf, gc, card_x + 6, card_y + 6, (unsigned int)card_w, (unsigned int)card_h);
            draw_bevel_rect(dpy, back_buf, gc, &colors, card_x, card_y, card_w, card_h, colors.canvas_bg, 0);

            if (st.num_cards > 0 && st.cur_card >= 0 && st.cur_card < st.num_cards) {
                const DecwCard* c = &st.cards[st.cur_card];
                /* Index Header above double crimson rule line */
                char hdr[128];
                snprintf(hdr, sizeof(hdr), "INDEX: %s", c->index);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, card_x + 16, card_y + font_asc + 10, hdr, (int)strlen(hdr));

                char badge[64];
                snprintf(badge, sizeof(badge), "[%s]  Card %d/%d", c->category, st.cur_card + 1, st.num_cards);
                XSetForeground(dpy, gc, colors.title_bg);
                XDrawString(dpy, back_buf, gc, card_x + card_w - (int)strlen(badge) * (font_h / 2 + 2) - 16,
                            card_y + font_asc + 10, badge, (int)strlen(badge));

                /* Double Crimson Red Index Rule Line */
                int rule_y = card_y + font_h + 18;
                XSetForeground(dpy, gc, crimson);
                XDrawLine(dpy, back_buf, gc, card_x + 6, rule_y, card_x + card_w - 6, rule_y);
                XDrawLine(dpy, back_buf, gc, card_x + 6, rule_y + 3, card_x + card_w - 6, rule_y + 3);

                /* Faint Blue Horizontal Index Card Ruled Lines */
                int line_step = font_h + 10;
                for (int ly = rule_y + line_step; ly < card_y + card_h - 12; ly += line_step) {
                    XSetForeground(dpy, gc, rule_blue);
                    XDrawLine(dpy, back_buf, gc, card_x + 10, ly, card_x + card_w - 10, ly);
                }

                XSetForeground(dpy, gc, colors.canvas_fg);
                char nline[128];
                snprintf(nline, sizeof(nline), "DECnet / Phone : %s", c->node);
                XDrawString(dpy, back_buf, gc, card_x + 16, rule_y + line_step - 4, nline, (int)strlen(nline));

                char categ_line[128];
                snprintf(categ_line, sizeof(categ_line), "Filing Category: %s", c->category);
                XDrawString(dpy, back_buf, gc, card_x + 16, rule_y + line_step * 2 - 4, categ_line, (int)strlen(categ_line));

                /* Word-wrap body text onto index card lines */
                const char* p = c->body;
                int row_idx = 3;
                while (*p && rule_y + line_step * row_idx < card_y + card_h - 10) {
                    char chunk[64];
                    snprintf(chunk, sizeof(chunk), "%.*s", 54, p);
                    XDrawString(dpy, back_buf, gc, card_x + 16, rule_y + line_step * row_idx - 4, chunk, (int)strlen(chunk));
                    size_t adv = strlen(chunk);
                    p += adv;
                    row_idx++;
                }
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                int dw = (win_w - 60 < 560) ? (win_w - 60) : 560;
                int dh = font_h * 10 + 70;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, font_h + 8, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 6 + font_asc,
                            st.edit_is_new ? "Cardfiler: Add New 3x5 Index Card" : "Cardfiler: Edit 3x5 Index Card", 30);

                int fy0 = dy + font_h * 2 + 12;
                int fh = font_h + 10;
                const char* flbls[4] = {"Index Header:", "Category:", "DECnet/Phone:", "Card Body:"};
                const char* fvals[4] = {st.f_index, st.f_cat, st.f_node, st.f_body};
                for (int f = 0; f < 4; f++) {
                    int fy = fy0 + f * (fh + 6);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, dx + 14, fy + font_asc + 2, flbls[f], (int)strlen(flbls[f]));
                    draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 150, fy, dw - 166, fh, colors.cmd_bg, 1);
                    char vbuf[168];
                    snprintf(vbuf, sizeof(vbuf), "%s%s", fvals[f], (st.focus_field == f) ? "_" : "");
                    XDrawString(dpy, back_buf, gc, dx + 156, fy + font_asc + 2, vbuf, (int)strlen(vbuf));
                }
                int by = dy + dh - fh - 12;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 40, by, 140, fh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + dw - 180, by, 140, fh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 74, by + font_asc + 3, "Save Card", 9);
                XDrawString(dpy, back_buf, gc, dx + dw - 140, by + font_asc + 3, "Cancel", 6);
            } else if (st.dialog_mode == 2) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows Cardfiler: About",
                    "DECwindows Motif Cardfiler V3.0 (DECW$CARDFILER / dxcardfiler)",
                    "Electronic 3x5 Rotary Index Card Filing & Search System",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                if (st.num_cards > 1) st.cur_card = 1;
                need_redraw = 1;
            }
        }

        if (autoclose_ms > 0 && exposed_once) {
            struct timeval now_tv;
            gettimeofday(&now_tv, NULL);
            long elapsed = (now_tv.tv_sec - start_tv.tv_sec) * 1000L + (now_tv.tv_usec - start_tv.tv_usec) / 1000L;
            if (elapsed >= autoclose_ms) break;
        }

        if (running) {
            int xfd = ConnectionNumber(dpy);
            fd_set fds;
            FD_ZERO(&fds);
            FD_SET(xfd, &fds);
            struct timeval tv = {0, 30000};
            select(xfd + 1, &fds, NULL, NULL, &tv);
        }
    }

    {
        char info[256];
        decw_x11_probe_display(dname, info, sizeof(info));
        printf("[DECwindows X11 Engine] Window '%s' (%s) rendered (%d lines, %d Motif buttons, Font: %s) | %s\n",
               title, cfg->app_id[0] ? cfg->app_id : "cardfiler", st.num_cards, 10, font_desc, info);
        fflush(stdout);
    }

    XFreePixmap(dpy, back_buf);
    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}

#endif /* DECW_GUI_GROUP1_H */
