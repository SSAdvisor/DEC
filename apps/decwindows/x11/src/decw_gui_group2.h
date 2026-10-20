#ifndef DECW_GUI_GROUP2_H
#define DECW_GUI_GROUP2_H

/* ============================================================================
 * 4. DECwindows Notepad (DECW$NOTEPAD / dxnotepad)
 *    Authentic OSF/Motif 1.1 Multi-Line XmText Editor, Clipboard & Search
 * ============================================================================ */

typedef struct {
    char lines[64][160];
    int num_lines;
    int cur_line;
    char clip_buf[160];
    int wrap_col;
    int read_only;
    int modified;
    int dialog_mode;   /* 0=none, 1=Find/Replace, 2=About */
    int focus_field;   /* 0=find, 1=replace */
    char find_str[64];
    char repl_str[64];
} DecwNotepadState;

static void np_load_state(DecwNotepadState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    st->wrap_col = 72;
    strcpy(st->find_str, "Motif");
    strcpy(st->repl_str, "OSF/Motif");
    strcpy(st->clip_buf, "(DECW$CLIPBOARD empty)");

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char buf[256];
        while (st->num_lines < 60 && fgets(buf, sizeof(buf), fp)) {
            buf[strcspn(buf, "\r\n")] = '\0';
            snprintf(st->lines[st->num_lines++], sizeof(st->lines[0]), "%.158s", buf);
        }
        fclose(fp);
    }
    if (st->num_lines == 0) {
        strcpy(st->lines[st->num_lines++], "DECwindows Motif 1.1 & Alpha AXP Workstation Notes (19-OCT-1991)");
        strcpy(st->lines[st->num_lines++], "----------------------------------------------------------------");
        strcpy(st->lines[st->num_lines++], "1. Verify DECW$NOTEPAD XmText widget cut/copy/paste via DECW$CLIPBOARD.");
        strcpy(st->lines[st->num_lines++], "2. Test compound string Latin-1 font rendering on HX/TX Framebuffer.");
        strcpy(st->lines[st->num_lines++], "3. Confirm VMS V5.5 and DEC OSF/1 V1.0 file interchange compatibility.");
        strcpy(st->lines[st->num_lines++], "4. Sign off ZKO Lab 3 workstation desktop integration checklist.");
    }
}

static void np_save_state(DecwNotepadState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    for (int i = 0; i < st->num_lines; i++) {
        fprintf(fp, "%s\n", st->lines[i]);
    }
    fclose(fp);
    st->modified = 0;
}

static int np_replace_all(DecwNotepadState* st, const char* old_s, const char* new_s) {
    if (!old_s || !old_s[0]) return 0;
    int count = 0;
    size_t olen = strlen(old_s);
    for (int i = 0; i < st->num_lines; i++) {
        char* pos = strstr(st->lines[i], old_s);
        if (pos) {
            char tmp[256];
            size_t pre = (size_t)(pos - st->lines[i]);
            snprintf(tmp, sizeof(tmp), "%.*s%s%s", (int)pre, st->lines[i], new_s, pos + olen);
            snprintf(st->lines[i], sizeof(st->lines[0]), "%.158s", tmp);
            count++;
            st->modified = 1;
        }
    }
    return count;
}

static int run_notepad_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "notepad", &colors);

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
    int rec_w = 1040, rec_h = 700;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 480) ? cfg->width : (720 + font_scale * 110);
    int win_h = (cfg->height >= 360) ? cfg->height : (460 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 75, 75,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Notepad - SYS$LOGIN:RELEASE_NOTES.TXT";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$NOTEPAD");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwNotepadState st;
    np_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"New Document",      101},
        {"Open Sample Notes", 102},
        {"Save Document",     103},
        {"---",               0},
        {"Exit",              109}
    };
    static const DecwMenuItem edit_items[] = {
        {"Copy Current Line", 201},
        {"Cut Current Line",  202},
        {"Paste Below Line",  203},
        {"Insert New Line",   204},
        {"Delete Line",       205}
    };
    static const DecwMenuItem search_items[] = {
        {"Find / Replace...", 301}
    };
    static const DecwMenuItem fmt_items[] = {
        {"Wrap Column 60",    401},
        {"Wrap Column 72",    402},
        {"Wrap Column 80",    403},
        {"Toggle Read-Only",  404}
    };
    static const DecwMenuItem help_items[] = {
        {"About Notepad...",  501}
    };
    DecwMenuBarMenu menus[5] = {
        {"File",   0, 0, 0, file_items,   5},
        {"Edit",   0, 0, 0, edit_items,   5},
        {"Search", 0, 0, 0, search_items, 1},
        {"Format", 0, 0, 0, fmt_items,    4},
        {"Help",   0, 0, 1, help_items,   1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "Click any line and type directly to edit | Return=New Line, BackSpace=Delete");

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
    int tb_y = 82, tb_h = 34;
    int ed_x = 10, ed_y = 148, ed_w = 680, ed_h = 260;

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
                    int dw = (win_w - 60 < 520) ? (win_w - 60) : 520;
                    int dh = font_h * 8 + 64;
                    int dx = (win_w - dw) / 2;
                    int dy = (win_h - dh) / 2;
                    int fy0 = dy + font_h * 2 + 12;
                    int fh = font_h + 10;
                    if (my >= fy0 && my <= fy0 + fh) st.focus_field = 0;
                    else if (my >= fy0 + fh + 6 && my <= fy0 + (fh + 6) * 2) st.focus_field = 1;
                    else if (my >= dy + dh - fh - 12 && my <= dy + dh - 8) {
                        if (mx < dx + dw / 2) {
                            int rep = np_replace_all(&st, st.find_str, st.repl_str);
                            np_save_state(&st, cfg->state_path);
                            snprintf(status_msg, sizeof(status_msg), "Replaced '%s' -> '%s' on %d lines",
                                     st.find_str, st.repl_str, rep);
                        }
                        st.dialog_mode = 0;
                    }
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 5, &open_menu);
                if (mact != 0) {
                    if (mact == 101 && !st.read_only) {
                        st.num_lines = 1;
                        strcpy(st.lines[0], "");
                        st.cur_line = 0;
                        st.modified = 1;
                    } else if (mact == 102) {
                        np_load_state(&st, NULL);
                        np_save_state(&st, cfg->state_path);
                    } else if (mact == 103) {
                        np_save_state(&st, cfg->state_path);
                        snprintf(status_msg, sizeof(status_msg), "Saved %d lines to %.150s", st.num_lines, cfg->state_path);
                    } else if (mact == 109) running = 0;
                    else if (mact == 201 && st.num_lines > 0) {
                        strcpy(st.clip_buf, st.lines[st.cur_line]);
                        snprintf(status_msg, sizeof(status_msg), "Copied line #%d to DECW$CLIPBOARD", st.cur_line + 1);
                    } else if (mact == 202 && !st.read_only && st.num_lines > 0) {
                        strcpy(st.clip_buf, st.lines[st.cur_line]);
                        for (int i = st.cur_line; i < st.num_lines - 1; i++) strcpy(st.lines[i], st.lines[i + 1]);
                        if (st.num_lines > 1) st.num_lines--;
                        else strcpy(st.lines[0], "");
                        if (st.cur_line >= st.num_lines) st.cur_line = st.num_lines - 1;
                        st.modified = 1;
                    } else if (mact == 203 && !st.read_only && st.num_lines < 60) {
                        for (int i = st.num_lines; i > st.cur_line + 1; i--) strcpy(st.lines[i], st.lines[i - 1]);
                        strcpy(st.lines[st.cur_line + 1], st.clip_buf);
                        st.num_lines++;
                        st.cur_line++;
                        st.modified = 1;
                    } else if (mact == 204 && !st.read_only && st.num_lines < 60) {
                        for (int i = st.num_lines; i > st.cur_line + 1; i--) strcpy(st.lines[i], st.lines[i - 1]);
                        strcpy(st.lines[st.cur_line + 1], "");
                        st.num_lines++;
                        st.cur_line++;
                        st.modified = 1;
                    } else if (mact == 205 && !st.read_only && st.num_lines > 0) {
                        for (int i = st.cur_line; i < st.num_lines - 1; i++) strcpy(st.lines[i], st.lines[i + 1]);
                        if (st.num_lines > 1) st.num_lines--;
                        else strcpy(st.lines[0], "");
                        if (st.cur_line >= st.num_lines) st.cur_line = st.num_lines - 1;
                        st.modified = 1;
                    } else if (mact == 301) st.dialog_mode = 1;
                    else if (mact == 401) st.wrap_col = 60;
                    else if (mact == 402) st.wrap_col = 72;
                    else if (mact == 403) st.wrap_col = 80;
                    else if (mact == 404) st.read_only = !st.read_only;
                    else if (mact == 501) st.dialog_mode = 2;
                    continue;
                }

                /* Toolbar click */
                if (my >= tb_y && my <= tb_y + tb_h) {
                    int b_idx = (mx - 10) * 6 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b_idx == 0 && !st.read_only && st.num_lines < 60) {
                        strcpy(st.lines[st.num_lines], "5. Additional engineering review item appended.");
                        st.cur_line = st.num_lines++;
                        st.modified = 1;
                    } else if (b_idx == 1 && st.num_lines > 0) {
                        strcpy(st.clip_buf, st.lines[st.cur_line]);
                        snprintf(status_msg, sizeof(status_msg), "Copied line #%d to DECW$CLIPBOARD", st.cur_line + 1);
                    } else if (b_idx == 2 && !st.read_only && st.num_lines < 60) {
                        for (int i = st.num_lines; i > st.cur_line + 1; i--) strcpy(st.lines[i], st.lines[i - 1]);
                        strcpy(st.lines[st.cur_line + 1], st.clip_buf);
                        st.num_lines++;
                        st.cur_line++;
                        st.modified = 1;
                    } else if (b_idx == 3 && !st.read_only && st.num_lines > 0) {
                        for (int i = st.cur_line; i < st.num_lines - 1; i++) strcpy(st.lines[i], st.lines[i + 1]);
                        if (st.num_lines > 1) st.num_lines--;
                        else strcpy(st.lines[0], "");
                        if (st.cur_line >= st.num_lines) st.cur_line = st.num_lines - 1;
                        st.modified = 1;
                    } else if (b_idx == 4) {
                        st.dialog_mode = 1;
                    } else if (b_idx == 5) {
                        np_save_state(&st, cfg->state_path);
                        snprintf(status_msg, sizeof(status_msg), "Saved %d lines to %.150s", st.num_lines, cfg->state_path);
                    }
                    continue;
                }

                /* Editor canvas click */
                if (mx >= ed_x && mx < ed_x + ed_w && my >= ed_y + font_h + 12 && my < ed_y + ed_h) {
                    int row = (my - (ed_y + font_h + 12)) / (font_h + 6);
                    if (row >= 0 && row < st.num_lines) {
                        st.cur_line = row;
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                int n = XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                kbuf[n] = '\0';
                need_redraw = 1;

                if (st.dialog_mode == 1) {
                    char* fld = (st.focus_field == 0) ? st.find_str : st.repl_str;
                    if (ks == XK_Escape) st.dialog_mode = 0;
                    else if (ks == XK_Tab) st.focus_field = 1 - st.focus_field;
                    else if (ks == XK_Return || ks == XK_KP_Enter) {
                        np_replace_all(&st, st.find_str, st.repl_str);
                        st.dialog_mode = 0;
                    } else if (ks == XK_BackSpace && strlen(fld) > 0) fld[strlen(fld) - 1] = '\0';
                    else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127 && strlen(fld) + 1 < 60) {
                        size_t l = strlen(fld);
                        fld[l] = kbuf[0];
                        fld[l + 1] = '\0';
                    }
                } else {
                    if (ks == XK_Escape) {
                        if (st.dialog_mode != 0) st.dialog_mode = 0;
                        else running = 0;
                    } else if (ks == XK_Up && st.cur_line > 0) st.cur_line--;
                    else if (ks == XK_Down && st.cur_line + 1 < st.num_lines) st.cur_line++;
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
                    } else if (!st.read_only) {
                        if ((ks == XK_Return || ks == XK_KP_Enter) && st.num_lines < 60) {
                            for (int i = st.num_lines; i > st.cur_line + 1; i--) strcpy(st.lines[i], st.lines[i - 1]);
                            strcpy(st.lines[st.cur_line + 1], "");
                            st.num_lines++;
                            st.cur_line++;
                            st.modified = 1;
                        } else if (ks == XK_BackSpace || ks == XK_Delete) {
                            size_t l = strlen(st.lines[st.cur_line]);
                            if (l > 0) {
                                st.lines[st.cur_line][l - 1] = '\0';
                                st.modified = 1;
                            }
                        } else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127) {
                            size_t l = strlen(st.lines[st.cur_line]);
                            if (l + 1 < sizeof(st.lines[0])) {
                                st.lines[st.cur_line][l] = kbuf[0];
                                st.lines[st.cur_line][l + 1] = '\0';
                                st.modified = 1;
                            }
                        }
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
                                          title, menus, 5, open_menu, &cy);

            tb_y = cy;
            tb_h = font_h + 14;
            const char* tb_lbls[6] = {"+ Append Line", "Copy Line", "Paste Clip", "Delete Line", "Find/Replace", "Save Buffer"};
            int bw = (win_w - 20) / 6;
            for (int i = 0; i < 6; i++) {
                int bx = 10 + i * bw;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, tb_y, bw - 4, tb_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, tb_y + font_asc + 4, tb_lbls[i], (int)strlen(tb_lbls[i]));
            }

            /* Document Info Banner */
            int info_y = tb_y + tb_h + 4;
            int info_h = font_h + 10;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, info_y, win_w - 20, info_h, colors.bg_gray, 1);
            char ibuf[200];
            snprintf(ibuf, sizeof(ibuf), "Buffer: SYS$LOGIN:RELEASE_NOTES.TXT  |  Lines: %d  |  Line: %d  |  Wrap: %d  |  %s  |  %s",
                     st.num_lines, st.cur_line + 1, st.wrap_col,
                     st.read_only ? "[READ-ONLY]" : "[READ-WRITE]",
                     st.modified ? "[MODIFIED]" : "[SAVED]");
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 18, info_y + font_asc + 3, ibuf, (int)strlen(ibuf));

            /* Main XmText Multi-Line Editor Canvas */
            int st_h = font_h + 10;
            int clip_h = font_h + 12;
            ed_x = 10;
            ed_y = info_y + info_h + 4;
            ed_w = win_w - 20;
            ed_h = win_h - ed_y - clip_h - st_h - 16;
            draw_bevel_rect(dpy, back_buf, gc, &colors, ed_x, ed_y, ed_w, ed_h, colors.canvas_bg, 1);

            /* Column Ruler Header */
            draw_bevel_rect(dpy, back_buf, gc, &colors, ed_x + 2, ed_y + 2, ed_w - 4, font_h + 8, colors.btn_bg, 0);
            const char* ruler = "  Ln | 1....+....10....+....20....+....30....+....40....+....50....+....60....+....72";
            XSetForeground(dpy, gc, colors.bevel_dark);
            XDrawString(dpy, back_buf, gc, ed_x + 8, ed_y + font_asc + 3, ruler, (int)strlen(ruler));

            int line_h = font_h + 6;
            int ry = ed_y + font_h + 12;
            for (int i = 0; i < st.num_lines && ry + line_h < ed_y + ed_h - 4; i++) {
                int sel = (i == st.cur_line);
                if (sel) {
                    XSetForeground(dpy, gc, colors.bevel_light);
                    XFillRectangle(dpy, back_buf, gc, ed_x + 4, ry, (unsigned int)(ed_w - 8), (unsigned int)line_h);
                }
                char lbuf[220];
                snprintf(lbuf, sizeof(lbuf), "%s%2d | %s%s",
                         sel ? ">" : " ", i + 1, st.lines[i], (sel && !st.read_only) ? "_" : "");
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, ed_x + 8, ry + font_asc + 2, lbuf, (int)strlen(lbuf));
                ry += line_h;
            }

            /* DECW$CLIPBOARD Strip */
            int clip_y = ed_y + ed_h + 4;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, clip_y, win_w - 20, clip_h, colors.cmd_bg, 1);
            char cbuf[220];
            snprintf(cbuf, sizeof(cbuf), "DECW$CLIPBOARD: %s", st.clip_buf);
            XSetForeground(dpy, gc, colors.title_bg);
            XDrawString(dpy, back_buf, gc, 18, clip_y + font_asc + 3, cbuf, (int)strlen(cbuf));

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 5, open_menu);

            if (st.dialog_mode == 1) {
                int dw = (win_w - 60 < 520) ? (win_w - 60) : 520;
                int dh = font_h * 8 + 64;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, font_h + 8, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 6 + font_asc, "Notepad: Find & Replace Text", 28);

                int fy0 = dy + font_h * 2 + 12;
                int fh = font_h + 10;
                const char* flbls[2] = {"Find String:", "Replace With:"};
                const char* fvals[2] = {st.find_str, st.repl_str};
                for (int f = 0; f < 2; f++) {
                    int fy = fy0 + f * (fh + 6);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, dx + 14, fy + font_asc + 2, flbls[f], (int)strlen(flbls[f]));
                    draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 150, fy, dw - 166, fh, colors.cmd_bg, 1);
                    char vbuf[96];
                    snprintf(vbuf, sizeof(vbuf), "%s%s", fvals[f], (st.focus_field == f) ? "_" : "");
                    XDrawString(dpy, back_buf, gc, dx + 156, fy + font_asc + 2, vbuf, (int)strlen(vbuf));
                }
                int by = dy + dh - fh - 12;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 40, by, 150, fh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + dw - 190, by, 150, fh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 68, by + font_asc + 3, "Replace All", 11);
                XDrawString(dpy, back_buf, gc, dx + dw - 140, by + font_asc + 3, "Cancel", 6);
            } else if (st.dialog_mode == 2) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows Notepad: About",
                    "DECwindows Motif Notepad V3.0 (DECW$NOTEPAD / dxnotepad)",
                    "Workstation XmText Editor, Word-Wrap & DECW$CLIPBOARD Manager",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                if (st.num_lines > 1) st.cur_line = 1;
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
               title, cfg->app_id[0] ? cfg->app_id : "notepad", st.num_lines, 11, font_desc, info);
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
 * 5. DECwindows FileView (DECW$FILEVIEW / VUE$MASTER / dxfileview)
 *    Authentic OSF/Motif 1.1 VMS Directory Manager, Layout Dialog & DCL Panel
 * ============================================================================ */

typedef struct {
    char dir[48];
    char name[48];
    int ver;
    int blocks;
    char fmt[16];
    char prot[32];
    char date[24];
    char content[128];
} DecwVmsFile;

typedef struct {
    char cur_dir[64];
    char filter[32];
    int sel_idx;
    DecwVmsFile files[32];
    int num_files;
    int show_blocks;
    int show_fmt;
    int show_prot;
    int show_date;
    int dialog_mode;   /* 0=none, 1=Layout Options, 2=About */
    char dcl_cmd[128];
    char dcl_out[160];
} DecwFileViewState;

static void fv_add_file(DecwFileViewState* st, const char* dir, const char* name, int ver,
                        int blks, const char* fmt, const char* prot, const char* dt, const char* body) {
    if (st->num_files >= 32) return;
    DecwVmsFile* f = &st->files[st->num_files++];
    snprintf(f->dir, sizeof(f->dir), "%s", dir);
    snprintf(f->name, sizeof(f->name), "%s", name);
    f->ver = ver;
    f->blocks = blks;
    snprintf(f->fmt, sizeof(f->fmt), "%s", fmt);
    snprintf(f->prot, sizeof(f->prot), "%s", prot);
    snprintf(f->date, sizeof(f->date), "%s", dt);
    snprintf(f->content, sizeof(f->content), "%s", body);
}

static void fv_load_state(DecwFileViewState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    strcpy(st->cur_dir, "SYS$SYSROOT:[SYSMGR]");
    strcpy(st->filter, "*.*");
    st->show_blocks = 1;
    st->show_fmt = 1;
    st->show_prot = 1;
    st->show_date = 1;
    strcpy(st->dcl_out, "$ SHOW DEFAULT -> SYS$SYSROOT:[SYSMGR] (Workstation VUE$MASTER Ready)");

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[320];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            if (strncmp(line, "FILEVIEW|", 9) == 0) {
                char d[64] = "", flt[32] = "";
                int s = 1;
                if (sscanf(line + 9, "%63[^|]|%31[^|]|%d", d, flt, &s) >= 2) {
                    snprintf(st->cur_dir, sizeof(st->cur_dir), "%s", d);
                    snprintf(st->filter, sizeof(st->filter), "%s", flt);
                }
            } else if (strncmp(line, "FIL|", 4) == 0) {
                char d[48] = "", n[48] = "", fmt[16] = "", prot[32] = "", dt[24] = "", body[128] = "";
                int ver = 1, blks = 1;
                if (sscanf(line + 4, "%47[^|]|%47[^|]|%d|%d|%15[^|]|%31[^|]|%23[^|]|%127[^\n]",
                           d, n, &ver, &blks, fmt, prot, dt, body) == 8) {
                    fv_add_file(st, d, n, ver, blks, fmt, prot, dt, body);
                }
            }
        }
        fclose(fp);
    }
    if (st->num_files == 0) {
        fv_add_file(st, "SYS$SYSROOT:[SYSMGR]", "SYSTARTUP_V5.COM", 4, 18, "SEQ/VAR", "(S:RWED,O:RWED,G:RE,W:)",
                    "19-OCT-1991 07:00", "$! VAX/VMS V5.5 Site-Specific Startup -- Start DECnet & DECwindows XUI/Motif");
        fv_add_file(st, "SYS$SYSROOT:[SYSMGR]", "LOGIN.COM", 1, 4, "SEQ/VAR", "(S:RWED,O:RWED,G:,W:)",
                    "14-OCT-1991 08:10", "$! Legacy operator login script (superseded by version ;2)");
        fv_add_file(st, "SYS$SYSROOT:[SYSMGR]", "LOGIN.COM", 2, 6, "SEQ/VAR", "(S:RWED,O:RWED,G:R,W:)",
                    "19-OCT-1991 08:45", "$ SET TERMINAL/INQUIRE /DEC_CRT ! Launch VUE$MASTER FileView Session");
        fv_add_file(st, "SYS$SYSROOT:[SYSMGR]", "SYLOGICALS.COM", 3, 12, "SEQ/VAR", "(S:RWED,O:RWED,G:RE,W:R)",
                    "18-OCT-1991 11:20", "$ DEFINE/SYSTEM DECW$BOOKSYSDIR DISK$DOC:[DECW$BOOK]");
        fv_add_file(st, "SYS$COMMON:[SYSEXE]", "DECW$SERVER.EXE", 1, 1420, "EXE/IMG", "(S:RWED,O:RWED,G:RE,W:E)",
                    "15-OCT-1991 16:00", "[VAX/VMS Shareable Image: DECwindows X11R4 Display Server SPX/GPX]");
        fv_add_file(st, "SYS$COMMON:[SYSEXE]", "RIGHTSLIST.DAT", 1, 64, "IDX/KEY", "(S:RWED,O:RWED,G:,W:)",
                    "12-OCT-1991 09:00", "[RMS Indexed File: System Rights Database - Key 0: Identifier]");
        fv_add_file(st, "DISK$USER:[CONKLIN.AXP]", "EV4_PALCODE.MAR", 5, 85, "SEQ/VAR", "(S:RWED,O:RWED,G:RE,W:)",
                    "19-OCT-1991 10:30", ".TITLE EV4_PALCODE - Alpha 21064 Privileged Architecture Library");
    }
}

static void fv_save_state(const DecwFileViewState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    fprintf(fp, "FILEVIEW|%s|%s|%d\n", st->cur_dir, st->filter, st->sel_idx + 1);
    for (int i = 0; i < st->num_files; i++) {
        const DecwVmsFile* f = &st->files[i];
        fprintf(fp, "FIL|%s|%s|%d|%d|%s|%s|%s|%s\n",
                f->dir, f->name, f->ver, f->blocks, f->fmt, f->prot, f->date, f->content);
    }
    fclose(fp);
}

static int fv_match_filter(const DecwVmsFile* f, const char* flt) {
    if (!flt || !flt[0] || strcmp(flt, "*.*") == 0) return 1;
    if (flt[0] == '*' && flt[1] == '.') {
        const char* ext = strrchr(f->name, '.');
        if (ext && strcasecmp(ext + 1, flt + 2) == 0) return 1;
        return 0;
    }
    return strstr(f->name, flt) != NULL;
}

static void fv_purge_versions(DecwFileViewState* st) {
    for (int i = 0; i < st->num_files; i++) {
        for (int j = 0; j < st->num_files; j++) {
            if (i != j && strcasecmp(st->files[i].name, st->files[j].name) == 0 &&
                st->files[i].ver < st->files[j].ver) {
                for (int k = i; k < st->num_files - 1; k++) st->files[k] = st->files[k + 1];
                st->num_files--;
                i--;
                break;
            }
        }
    }
    if (st->sel_idx >= st->num_files) st->sel_idx = st->num_files - 1;
}

static int run_fileview_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "fileview", &colors);

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
    int rec_w = 1100, rec_h = 740;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 520) ? cfg->width : (760 + font_scale * 115);
    int win_h = (cfg->height >= 380) ? cfg->height : (490 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 70, 70,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows FileView - SYS$SYSROOT:[SYSMGR]";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$FILEVIEW");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwFileViewState st;
    fv_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Reload VMS Sample", 101},
        {"Save Directory",    102},
        {"Purge Old Versions",103},
        {"Delete Selected",   104},
        {"---",               0},
        {"Exit",              109}
    };
    static const DecwMenuItem view_items[] = {
        {"Filter *.* (All)",  201},
        {"Filter *.COM",      202},
        {"Filter *.EXE",      203},
        {"Filter *.MAR",      204}
    };
    static const DecwMenuItem cmd_items[] = {
        {"DCL: SHOW DEFAULT", 301},
        {"DCL: DIR /FULL",    302},
        {"DCL: PURGE /LOG",   303}
    };
    static const DecwMenuItem opt_items[] = {
        {"Layout Columns...", 401}
    };
    static const DecwMenuItem help_items[] = {
        {"About FileView...", 501}
    };
    DecwMenuBarMenu menus[5] = {
        {"File",     0, 0, 0, file_items, 6},
        {"View",     0, 0, 0, view_items, 4},
        {"Commands", 0, 0, 0, cmd_items,  3},
        {"Options",  0, 0, 0, opt_items,  1},
        {"Help",     0, 0, 1, help_items, 1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "FileView Ready | %d VMS files | Click file row or Action buttons on right", st.num_files);

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
    int flt_y = 82, flt_h = 34;
    int list_x = 10, list_y = 124, list_w = 500, list_h = 220;
    int act_x = 520, act_w = 180;

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
                    int dh = font_h * 9 + 64;
                    int dy = (win_h - dh) / 2;
                    int fy0 = dy + font_h * 2 + 12;
                    int fh = font_h + 10;
                    if (my >= fy0 && my < fy0 + fh) st.show_blocks = !st.show_blocks;
                    else if (my >= fy0 + fh + 4 && my < fy0 + (fh + 4) * 2) st.show_fmt = !st.show_fmt;
                    else if (my >= fy0 + (fh + 4) * 2 && my < fy0 + (fh + 4) * 3) st.show_prot = !st.show_prot;
                    else if (my >= fy0 + (fh + 4) * 3 && my < fy0 + (fh + 4) * 4) st.show_date = !st.show_date;
                    else if (my >= dy + dh - fh - 12) st.dialog_mode = 0;
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 5, &open_menu);
                if (mact != 0) {
                    if (mact == 101) { fv_load_state(&st, NULL); fv_save_state(&st, cfg->state_path); }
                    else if (mact == 102) fv_save_state(&st, cfg->state_path);
                    else if (mact == 103 || mact == 303) {
                        fv_purge_versions(&st);
                        fv_save_state(&st, cfg->state_path);
                        strcpy(st.dcl_out, "$ PURGE /LOG -> Purged superseded file versions (;1)");
                    } else if (mact == 104 && st.num_files > 1) {
                        for (int i = st.sel_idx; i < st.num_files - 1; i++) st.files[i] = st.files[i + 1];
                        st.num_files--;
                        if (st.sel_idx >= st.num_files) st.sel_idx = st.num_files - 1;
                        fv_save_state(&st, cfg->state_path);
                    } else if (mact == 109) running = 0;
                    else if (mact == 201) strcpy(st.filter, "*.*");
                    else if (mact == 202) strcpy(st.filter, "*.COM");
                    else if (mact == 203) strcpy(st.filter, "*.EXE");
                    else if (mact == 204) strcpy(st.filter, "*.MAR");
                    else if (mact == 301) snprintf(st.dcl_out, sizeof(st.dcl_out), "$ SHOW DEFAULT -> %s", st.cur_dir);
                    else if (mact == 302 && st.sel_idx >= 0 && st.sel_idx < st.num_files) {
                        const DecwVmsFile* f = &st.files[st.sel_idx];
                        snprintf(st.dcl_out, sizeof(st.dcl_out), "$ DIR/FULL %s;%d -> %d blks, %s, %s",
                                 f->name, f->ver, f->blocks, f->fmt, f->prot);
                    } else if (mact == 401) st.dialog_mode = 1;
                    else if (mact == 501) st.dialog_mode = 2;
                    continue;
                }

                /* Quick Filter Buttons on Top Bar */
                if (my >= flt_y && my <= flt_y + flt_h && mx >= win_w - 300) {
                    int b = (mx - (win_w - 300)) * 4 / 290;
                    if (b == 0) strcpy(st.filter, "*.*");
                    else if (b == 1) strcpy(st.filter, "*.COM");
                    else if (b == 2) strcpy(st.filter, "*.EXE");
                    else if (b == 3) strcpy(st.filter, "*.MAR");
                    continue;
                }

                /* File List Selection */
                if (mx >= list_x && mx < list_x + list_w && my >= list_y + font_h + 14 && my < list_y + list_h) {
                    int target_row = (my - (list_y + font_h + 14)) / (font_h + 8);
                    int vis_idx = 0;
                    for (int i = 0; i < st.num_files; i++) {
                        if (fv_match_filter(&st.files[i], st.filter)) {
                            if (vis_idx == target_row) {
                                st.sel_idx = i;
                                snprintf(st.cur_dir, sizeof(st.cur_dir), "%s", st.files[i].dir);
                                snprintf(status_msg, sizeof(status_msg), "Selected %s;%d (%d blocks, %s)",
                                         st.files[i].name, st.files[i].ver, st.files[i].blocks, st.files[i].fmt);
                                break;
                            }
                            vis_idx++;
                        }
                    }
                    continue;
                }

                /* Right Column Action PushButtons */
                if (mx >= act_x && mx <= act_x + act_w && my >= list_y && my <= list_y + list_h) {
                    int b_h = (list_h - 4) / 6;
                    int b = (my - list_y) / (b_h > 0 ? b_h : 1);
                    if (b == 0 && st.sel_idx >= 0 && st.sel_idx < st.num_files) {
                        const DecwVmsFile* f = &st.files[st.sel_idx];
                        snprintf(st.dcl_out, sizeof(st.dcl_out), "$ TYPE %s;%d -> %s", f->name, f->ver, f->content);
                    } else if (b == 1 && st.sel_idx >= 0 && st.sel_idx < st.num_files && st.num_files < 31) {
                        DecwVmsFile c = st.files[st.sel_idx];
                        c.ver++;
                        st.files[st.num_files++] = c;
                        st.sel_idx = st.num_files - 1;
                        fv_save_state(&st, cfg->state_path);
                        snprintf(st.dcl_out, sizeof(st.dcl_out), "$ COPY %s -> Created new version ;%d", c.name, c.ver);
                    } else if (b == 2) {
                        fv_purge_versions(&st);
                        fv_save_state(&st, cfg->state_path);
                        strcpy(st.dcl_out, "$ PURGE /LOG -> Removed older file versions");
                    } else if (b == 3 && st.num_files > 1) {
                        for (int i = st.sel_idx; i < st.num_files - 1; i++) st.files[i] = st.files[i + 1];
                        st.num_files--;
                        if (st.sel_idx >= st.num_files) st.sel_idx = st.num_files - 1;
                        fv_save_state(&st, cfg->state_path);
                    } else if (b == 4) {
                        st.dialog_mode = 1;
                    } else if (b == 5) {
                        fv_load_state(&st, NULL);
                        fv_save_state(&st, cfg->state_path);
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
                } else if (ks == XK_Up && st.sel_idx > 0) st.sel_idx--;
                else if (ks == XK_Down && st.sel_idx + 1 < st.num_files) st.sel_idx++;
                else if (ks == XK_Return || ks == XK_KP_Enter) {
                    if (st.dcl_cmd[0]) {
                        if (strncasecmp(st.dcl_cmd, "PURGE", 5) == 0) fv_purge_versions(&st);
                        snprintf(st.dcl_out, sizeof(st.dcl_out), "$ %s -> %s (%d files)", st.dcl_cmd, st.cur_dir, st.num_files);
                        st.dcl_cmd[0] = '\0';
                    }
                } else if (ks == XK_BackSpace && strlen(st.dcl_cmd) > 0) {
                    st.dcl_cmd[strlen(st.dcl_cmd) - 1] = '\0';
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
                } else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127 && strlen(st.dcl_cmd) + 1 < sizeof(st.dcl_cmd)) {
                    size_t l = strlen(st.dcl_cmd);
                    st.dcl_cmd[l] = kbuf[0];
                    st.dcl_cmd[l + 1] = '\0';
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
                                          title, menus, 5, open_menu, &cy);

            /* Top Directory & Filter Bar */
            flt_y = cy;
            flt_h = font_h + 12;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, flt_y, win_w - 314, flt_h, colors.cmd_bg, 1);
            char dfbuf[160];
            snprintf(dfbuf, sizeof(dfbuf), "Directory: %s    |    Filter: %s", st.cur_dir, st.filter);
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 18, flt_y + font_asc + 3, dfbuf, (int)strlen(dfbuf));

            const char* flt_btns[4] = {"*.*", "*.COM", "*.EXE", "*.MAR"};
            for (int i = 0; i < 4; i++) {
                int bx = win_w - 298 + i * 72;
                int act = (strcasecmp(st.filter, flt_btns[i]) == 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, flt_y, 68, flt_h,
                                act ? colors.title_bg : colors.btn_bg, act);
                XSetForeground(dpy, gc, act ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, flt_y + font_asc + 3, flt_btns[i], (int)strlen(flt_btns[i]));
            }

            /* Middle File List + Action Button Column */
            int st_h = font_h + 10;
            int prev_h = font_h * 4 + 26;
            list_x = 10;
            list_y = flt_y + flt_h + 6;
            act_w = 175;
            list_w = win_w - act_w - 28;
            list_h = win_h - list_y - prev_h - st_h - 16;
            act_x = list_x + list_w + 8;

            draw_bevel_rect(dpy, back_buf, gc, &colors, list_x, list_y, list_w, list_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, list_x + 2, list_y + 2, list_w - 4, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, list_x + 10, list_y + font_asc + 4,
                        "VMS Filename;Ver        Blks   Fmt      Protection               Modified Date", 78);

            int row_h = font_h + 8;
            int ry = list_y + font_h + 14;
            for (int i = 0; i < st.num_files && ry + row_h < list_y + list_h - 4; i++) {
                const DecwVmsFile* f = &st.files[i];
                if (!fv_match_filter(f, st.filter)) continue;
                int sel = (i == st.sel_idx);
                if (sel) {
                    draw_bevel_rect(dpy, back_buf, gc, &colors, list_x + 4, ry, list_w - 8, row_h - 1, colors.title_bg, 1);
                }
                char nv[64], rbuf[220];
                snprintf(nv, sizeof(nv), "%s;%d", f->name, f->ver);
                snprintf(rbuf, sizeof(rbuf), "%-22s %5s  %-8s %-24s %s",
                         nv,
                         st.show_blocks ? (snprintf(nv + 32, 16, "%d", f->blocks), nv + 32) : "",
                         st.show_fmt ? f->fmt : "",
                         st.show_prot ? f->prot : "",
                         st.show_date ? f->date : "");
                XSetForeground(dpy, gc, sel ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, list_x + 10, ry + font_asc + 2, rbuf, (int)strlen(rbuf));
                ry += row_h;
            }

            /* Action PushButton Column */
            const char* act_lbls[6] = {"Read / Type", "Copy New ;Ver", "Purge Old ;*", "Delete File", "Layout Cols...", "Reload Sample"};
            int bh = (list_h - 4) / 6;
            for (int i = 0; i < 6; i++) {
                int by = list_y + i * bh;
                draw_bevel_rect(dpy, back_buf, gc, &colors, act_x, by, act_w, bh - 4, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, act_x + 12, by + (bh + font_asc) / 2 - 3, act_lbls[i], (int)strlen(act_lbls[i]));
            }

            /* Bottom File Preview & DCL Subwindow */
            int py = list_y + list_h + 6;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, py, win_w - 20, prev_h, colors.canvas_bg, 1);
            if (st.sel_idx >= 0 && st.sel_idx < st.num_files) {
                const DecwVmsFile* f = &st.files[st.sel_idx];
                char p1[200], p2[200];
                snprintf(p1, sizeof(p1), "Selected: %s%s;%d  |  %d Blocks  |  RMS: %s  |  Prot: %s",
                         f->dir, f->name, f->ver, f->blocks, f->fmt, f->prot);
                snprintf(p2, sizeof(p2), "Content : %s", f->content);
                XSetForeground(dpy, gc, colors.title_bg);
                XDrawString(dpy, back_buf, gc, 18, py + font_asc + 4, p1, (int)strlen(p1));
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, 18, py + font_h + font_asc + 8, p2, (int)strlen(p2));
            }
            XSetForeground(dpy, gc, colors.bevel_dark);
            XDrawString(dpy, back_buf, gc, 18, py + font_h * 2 + font_asc + 12, st.dcl_out, (int)strlen(st.dcl_out));

            char dcl_in[180];
            snprintf(dcl_in, sizeof(dcl_in), "DCL Command> %s_", st.dcl_cmd);
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 18, py + font_h * 3 + font_asc + 16, dcl_in, (int)strlen(dcl_in));

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 5, open_menu);

            if (st.dialog_mode == 1) {
                int dw = (win_w - 60 < 480) ? (win_w - 60) : 480;
                int dh = font_h * 9 + 64;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, font_h + 8, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 6 + font_asc, "FileView: Layout Options", 24);

                int fy0 = dy + font_h * 2 + 12;
                int fh = font_h + 10;
                int flags[4] = {st.show_blocks, st.show_fmt, st.show_prot, st.show_date};
                const char* flbls[4] = {"Show File Size (Blocks)", "Show RMS Record Format", "Show UIC Protection Mask", "Show Modification Date"};
                for (int f = 0; f < 4; f++) {
                    int fy = fy0 + f * (fh + 4);
                    draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 20, fy, dw - 40, fh, colors.btn_bg, flags[f]);
                    char cstr[80];
                    snprintf(cstr, sizeof(cstr), "[%c] %s", flags[f] ? 'X' : ' ', flbls[f]);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, dx + 32, fy + font_asc + 2, cstr, (int)strlen(cstr));
                }
                int by = dy + dh - fh - 12;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + (dw - 120) / 2, by, 120, fh, colors.btn_bg, 0);
                XDrawString(dpy, back_buf, gc, dx + (dw - 120) / 2 + 46, by + font_asc + 3, "OK", 2);
            } else if (st.dialog_mode == 2) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows FileView: About",
                    "DECwindows Motif FileView V3.0 (DECW$FILEVIEW / VUE$MASTER)",
                    "OpenVMS RMS Directory Browser, Layout Customizer & DCL Shell",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                if (st.num_files > 1) st.sel_idx = 1;
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
               title, cfg->app_id[0] ? cfg->app_id : "fileview", st.num_files, 10, font_desc, info);
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
 * 6. DECwindows Mail (DECW$MAIL / dxmail)
 *    Authentic OSF/Motif 1.1 Three-Pane Mail Cabinet, Drawer/Folder & Reader
 * ============================================================================ */

typedef struct {
    int id;
    char drawer[24];
    char folder[24];
    char from[32];
    char to[32];
    char date[24];
    char subject[64];
    char fmt[12];
    char status[16];
    char body[192];
} DecwMailMsg;

typedef struct {
    char cur_drawer[24];
    char cur_folder[24];
    int sel_msg_idx;
    DecwMailMsg msgs[32];
    int num_msgs;
    int dialog_mode;   /* 0=none, 1=Compose/Reply, 2=About */
    int focus_field;   /* 0=to, 1=subj, 2=body */
    char c_to[48];
    char c_subj[64];
    char c_body[160];
} DecwMailState;

static void mail_add_msg(DecwMailState* st, const char* drw, const char* fld,
                         const char* from, const char* to, const char* dt,
                         const char* subj, const char* fmt, const char* status, const char* body) {
    if (st->num_msgs >= 32) return;
    DecwMailMsg* m = &st->msgs[st->num_msgs++];
    m->id = st->num_msgs;
    snprintf(m->drawer, sizeof(m->drawer), "%s", drw);
    snprintf(m->folder, sizeof(m->folder), "%s", fld);
    snprintf(m->from, sizeof(m->from), "%s", from);
    snprintf(m->to, sizeof(m->to), "%s", to);
    snprintf(m->date, sizeof(m->date), "%s", dt);
    snprintf(m->subject, sizeof(m->subject), "%s", subj);
    snprintf(m->fmt, sizeof(m->fmt), "%s", fmt);
    snprintf(m->status, sizeof(m->status), "%s", status);
    snprintf(m->body, sizeof(m->body), "%s", body);
}

static void mail_load_state(DecwMailState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    strcpy(st->cur_drawer, "MAIN");
    strcpy(st->cur_folder, "ALL");

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[380];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            if (strncmp(line, "MSG|", 4) == 0) {
                int id = 0;
                char drw[24] = "", fld[24] = "", fr[32] = "", to[32] = "", dt[24] = "";
                char subj[64] = "", fmt[12] = "", sts[16] = "", body[192] = "";
                if (sscanf(line + 4, "%d|%23[^|]|%23[^|]|%31[^|]|%31[^|]|%23[^|]|%63[^|]|%11[^|]|%15[^|]|%191[^\n]",
                           &id, drw, fld, fr, to, dt, subj, fmt, sts, body) == 10) {
                    mail_add_msg(st, drw, fld, fr, to, dt, subj, fmt, sts, body);
                }
            }
        }
        fclose(fp);
    }
    if (st->num_msgs == 0) {
        mail_add_msg(st, "MAIN", "INBOX", "ZKO::CUTLER", "ZKO::SYSTEM", "19-OCT-1991 08:30",
                     "MICA & Prism Kernel Review Notes", "TEXT", "UNREAD",
                     "Please review the scheduler spinlock latency benchmarks before 14:00.");
        mail_add_msg(st, "MAIN", "INBOX", "ZKO::CONKLIN", "ZKO::ALL_ENG", "19-OCT-1991 09:15",
                     "DEC OSF/1 V1.0 Alpha AXP Boot Milestone", "DDIF", "UNREAD",
                     "[CDA/DDIF V1.2] Alpha EV4 21064 booted multi-user OSF/1 in ZKO Lab 3.");
        mail_add_msg(st, "MAIN", "INBOX", "SRC::LAMPORT", "ZKO::SYSTEM", "19-OCT-1991 10:05",
                     "Part-Time Parliament Consensus Draft", "DDIF", "MARKED",
                     "[CDA/DDIF V1.2] Attached is the Paxos synod fault-tolerant protocol proof.");
        mail_add_msg(st, "MAIN", "READ", "MLO::OLSEN", "ALL::DEC", "18-OCT-1991 16:00",
                     "DECworld 92 Boston Planning", "TEXT", "READ",
                     "All workstation groups will demonstrate DECwindows Motif 1.1 live.");
        mail_add_msg(st, "MAIN", "SENT", "ZKO::SYSTEM", "ZKO::CUTLER", "18-OCT-1991 17:20",
                     "RE: Lab 3 VAX 9000 Cluster Allocation", "TEXT", "READ",
                     "CI star coupler channels 2 and 3 are reserved for overnight stress tests.");
        mail_add_msg(st, "PROJECTS", "ALPHA_OSF1", "REO::WULF", "ZKO::CONKLIN", "17-OCT-1991 11:45",
                     "GEM Optimizing Backend PALcode Hooks", "TEXT", "READ",
                     "Unaligned quadword trap handlers verified on EV4 simulator.");
    }
}

static void mail_save_state(const DecwMailState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    fprintf(fp, "DXMAIL|%s|%s|%d\n", st->cur_drawer, st->cur_folder, st->sel_msg_idx + 1);
    for (int i = 0; i < st->num_msgs; i++) {
        const DecwMailMsg* m = &st->msgs[i];
        fprintf(fp, "MSG|%d|%s|%s|%s|%s|%s|%s|%s|%s|%s\n",
                i + 1, m->drawer, m->folder, m->from, m->to, m->date, m->subject, m->fmt, m->status, m->body);
    }
    fclose(fp);
}

static int mail_folder_count(const DecwMailState* st, const char* fld) {
    if (strcmp(fld, "ALL") == 0) return st->num_msgs;
    int c = 0;
    for (int i = 0; i < st->num_msgs; i++) {
        if (strcasecmp(st->msgs[i].folder, fld) == 0) c++;
    }
    return c;
}

static int run_dxmail_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "dxmail", &colors);

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
    int rec_w = 1120, rec_h = 760;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 540) ? cfg->width : (780 + font_scale * 115);
    int win_h = (cfg->height >= 400) ? cfg->height : (500 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 65, 65,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Mail - Cabinet: MAIN [INBOX]";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$MAIL");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwMailState st;
    mail_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Load Sample Cabinet", 101},
        {"Save Mail Cabinet",   102},
        {"---",                 0},
        {"Exit",                109}
    };
    static const DecwMenuItem view_items[] = {
        {"All Folders",         201},
        {"MAIN : INBOX",        202},
        {"MAIN : READ",         203},
        {"MAIN : SENT",         204},
        {"PROJECTS : ALPHA_OSF1", 205}
    };
    static const DecwMenuItem msg_items[] = {
        {"Compose / Send...",   301},
        {"Reply to Sender...",  302},
        {"Mark / Flag Message", 303},
        {"Move to READ Folder", 304},
        {"Delete Message",      305}
    };
    static const DecwMenuItem help_items[] = {
        {"About DECwindows Mail...", 401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File",    0, 0, 0, file_items, 4},
        {"View",    0, 0, 0, view_items, 5},
        {"Message", 0, 0, 0, msg_items,  5},
        {"Help",    0, 0, 1, help_items, 1}
    };

    static const char* folder_names[5] = {"ALL", "INBOX", "READ", "SENT", "ALPHA_OSF1"};
    static const char* folder_labels[5] = {
        "ALL FOLDERS",
        "MAIN -> INBOX",
        "MAIN -> READ",
        "MAIN -> SENT",
        "PROJECTS -> ALPHA_OSF1"
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "Cabinet: MAIN | %d messages | Click folder on left or message header on right", st.num_msgs);

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
    int tb_y = 82, tb_h = 34;
    int cab_x = 10, cab_y = 124, cab_w = 240, cab_h = 200;
    int hdr_x = 258, hdr_w = 500;

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
                    int dh = font_h * 9 + 68;
                    int dx = (win_w - dw) / 2;
                    int dy = (win_h - dh) / 2;
                    int fy0 = dy + font_h * 2 + 12;
                    int fh = font_h + 10;
                    for (int f = 0; f < 3; f++) {
                        if (my >= fy0 + f * (fh + 6) && my <= fy0 + (f + 1) * (fh + 6)) st.focus_field = f;
                    }
                    if (my >= dy + dh - fh - 12 && my <= dy + dh - 8) {
                        if (mx < dx + dw / 2) {
                            mail_add_msg(&st, "MAIN", "SENT", "ZKO::SYSTEM",
                                         st.c_to[0] ? st.c_to : "ZKO::CUTLER",
                                         "20-OCT-1991 12:00",
                                         st.c_subj[0] ? st.c_subj : "DECwindows Motif Update",
                                         "TEXT", "READ",
                                         st.c_body[0] ? st.c_body : "Message transmitted via DECwindows Mail.");
                            st.sel_msg_idx = st.num_msgs - 1;
                            mail_save_state(&st, cfg->state_path);
                            snprintf(status_msg, sizeof(status_msg), "Sent message #%d to %s", st.num_msgs, st.c_to);
                        }
                        st.dialog_mode = 0;
                    }
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) { mail_load_state(&st, NULL); mail_save_state(&st, cfg->state_path); }
                    else if (mact == 102) mail_save_state(&st, cfg->state_path);
                    else if (mact == 109) running = 0;
                    else if (mact >= 201 && mact <= 205) strcpy(st.cur_folder, folder_names[mact - 201]);
                    else if (mact == 301) {
                        strcpy(st.c_to, "ZKO::CUTLER");
                        strcpy(st.c_subj, "DECwindows Motif Status");
                        strcpy(st.c_body, "All 11 DECwindows Motif X11 applications verified.");
                        st.dialog_mode = 1;
                    } else if (mact == 302 && st.sel_msg_idx >= 0 && st.sel_msg_idx < st.num_msgs) {
                        strcpy(st.c_to, st.msgs[st.sel_msg_idx].from);
                        snprintf(st.c_subj, sizeof(st.c_subj), "RE: %.54s", st.msgs[st.sel_msg_idx].subject);
                        strcpy(st.c_body, "Acknowledged. Reviewed and signed off.");
                        st.dialog_mode = 1;
                    } else if (mact == 303 && st.sel_msg_idx >= 0 && st.sel_msg_idx < st.num_msgs) {
                        strcpy(st.msgs[st.sel_msg_idx].status,
                               strcmp(st.msgs[st.sel_msg_idx].status, "MARKED") == 0 ? "READ" : "MARKED");
                        mail_save_state(&st, cfg->state_path);
                    } else if (mact == 304 && st.sel_msg_idx >= 0 && st.sel_msg_idx < st.num_msgs) {
                        strcpy(st.msgs[st.sel_msg_idx].folder, "READ");
                        strcpy(st.msgs[st.sel_msg_idx].status, "READ");
                        mail_save_state(&st, cfg->state_path);
                    } else if (mact == 305 && st.num_msgs > 1) {
                        for (int i = st.sel_msg_idx; i < st.num_msgs - 1; i++) st.msgs[i] = st.msgs[i + 1];
                        st.num_msgs--;
                        if (st.sel_msg_idx >= st.num_msgs) st.sel_msg_idx = st.num_msgs - 1;
                        mail_save_state(&st, cfg->state_path);
                    } else if (mact == 401) st.dialog_mode = 2;
                    continue;
                }

                /* Toolbar click */
                if (my >= tb_y && my <= tb_y + tb_h) {
                    int b = (mx - 10) * 6 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b == 0) {
                        strcpy(st.c_to, "ZKO::CUTLER");
                        strcpy(st.c_subj, "DECwindows Motif Status");
                        strcpy(st.c_body, "All 11 DECwindows Motif X11 applications verified.");
                        st.dialog_mode = 1;
                    } else if (b == 1 && st.sel_msg_idx >= 0 && st.sel_msg_idx < st.num_msgs) {
                        strcpy(st.c_to, st.msgs[st.sel_msg_idx].from);
                        snprintf(st.c_subj, sizeof(st.c_subj), "RE: %.54s", st.msgs[st.sel_msg_idx].subject);
                        strcpy(st.c_body, "Acknowledged. Reviewed and signed off.");
                        st.dialog_mode = 1;
                    } else if (b == 2 && st.sel_msg_idx >= 0 && st.sel_msg_idx < st.num_msgs) {
                        strcpy(st.msgs[st.sel_msg_idx].status,
                               strcmp(st.msgs[st.sel_msg_idx].status, "MARKED") == 0 ? "READ" : "MARKED");
                        mail_save_state(&st, cfg->state_path);
                    } else if (b == 3 && st.sel_msg_idx >= 0 && st.sel_msg_idx < st.num_msgs) {
                        strcpy(st.msgs[st.sel_msg_idx].folder, "READ");
                        strcpy(st.msgs[st.sel_msg_idx].status, "READ");
                        mail_save_state(&st, cfg->state_path);
                    } else if (b == 4 && st.num_msgs > 1) {
                        for (int i = st.sel_msg_idx; i < st.num_msgs - 1; i++) st.msgs[i] = st.msgs[i + 1];
                        st.num_msgs--;
                        if (st.sel_msg_idx >= st.num_msgs) st.sel_msg_idx = st.num_msgs - 1;
                        mail_save_state(&st, cfg->state_path);
                    } else if (b == 5 && st.num_msgs > 0) {
                        st.sel_msg_idx = (st.sel_msg_idx + 1) % st.num_msgs;
                    }
                    continue;
                }

                /* Left Cabinet Folder Tree click */
                if (mx >= cab_x && mx < cab_x + cab_w && my >= cab_y + font_h + 14 && my < cab_y + cab_h) {
                    int row = (my - (cab_y + font_h + 14)) / (font_h + 10);
                    if (row >= 0 && row < 5) {
                        strcpy(st.cur_folder, folder_names[row]);
                        for (int i = 0; i < st.num_msgs; i++) {
                            if (strcmp(st.cur_folder, "ALL") == 0 ||
                                strcasecmp(st.msgs[i].folder, st.cur_folder) == 0) {
                                st.sel_msg_idx = i;
                                break;
                            }
                        }
                    }
                    continue;
                }

                /* Upper-Right Message Header List click */
                if (mx >= hdr_x && mx < hdr_x + hdr_w && my >= cab_y + font_h + 14 && my < cab_y + cab_h) {
                    int target_row = (my - (cab_y + font_h + 14)) / (font_h + 8);
                    int vis = 0;
                    for (int i = 0; i < st.num_msgs; i++) {
                        if (strcmp(st.cur_folder, "ALL") == 0 ||
                            strcasecmp(st.msgs[i].folder, st.cur_folder) == 0) {
                            if (vis == target_row) {
                                st.sel_msg_idx = i;
                                if (strcmp(st.msgs[i].status, "UNREAD") == 0) {
                                    strcpy(st.msgs[i].status, "READ");
                                    mail_save_state(&st, cfg->state_path);
                                }
                                break;
                            }
                            vis++;
                        }
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                int n = XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                kbuf[n] = '\0';
                need_redraw = 1;
                if (st.dialog_mode == 1) {
                    char* fld = (st.focus_field == 0) ? st.c_to : (st.focus_field == 1 ? st.c_subj : st.c_body);
                    size_t maxl = (st.focus_field == 0) ? 44 : (st.focus_field == 1 ? 60 : 150);
                    if (ks == XK_Escape) st.dialog_mode = 0;
                    else if (ks == XK_Tab) st.focus_field = (st.focus_field + 1) % 3;
                    else if (ks == XK_BackSpace && strlen(fld) > 0) fld[strlen(fld) - 1] = '\0';
                    else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127 && strlen(fld) + 1 < maxl) {
                        size_t l = strlen(fld);
                        fld[l] = kbuf[0];
                        fld[l + 1] = '\0';
                    }
                } else {
                    if (ks == XK_Escape) running = 0;
                    else if (ks == XK_Up && st.sel_msg_idx > 0) st.sel_msg_idx--;
                    else if (ks == XK_Down && st.sel_msg_idx + 1 < st.num_msgs) st.sel_msg_idx++;
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
            const char* tb_lbls[6] = {"Compose...", "Reply...", "Mark/Flag", "Move->READ", "Delete Msg", "Next Msg >"};
            int bw = (win_w - 20) / 6;
            for (int i = 0; i < 6; i++) {
                int bx = 10 + i * bw;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, tb_y, bw - 4, tb_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, tb_y + font_asc + 4, tb_lbls[i], (int)strlen(tb_lbls[i]));
            }

            int st_h = font_h + 10;
            int avail_h = win_h - (tb_y + tb_h + 6) - st_h - 14;
            cab_x = 10;
            cab_y = tb_y + tb_h + 6;
            cab_w = (win_w - 28) * 32 / 100;
            cab_h = avail_h * 52 / 100;
            hdr_x = cab_x + cab_w + 8;
            hdr_w = win_w - hdr_x - 10;

            /* 1. Upper-Left: Mail Cabinet & Drawers Tree */
            draw_bevel_rect(dpy, back_buf, gc, &colors, cab_x, cab_y, cab_w, cab_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, cab_x + 2, cab_y + 2, cab_w - 4, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, cab_x + 8, cab_y + font_asc + 4, "Mail Cabinet / Drawers", 22);

            for (int f = 0; f < 5; f++) {
                int fy = cab_y + font_h + 16 + f * (font_h + 10);
                if (fy + font_h + 8 > cab_y + cab_h) break;
                int act = (strcasecmp(st.cur_folder, folder_names[f]) == 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, cab_x + 4, fy, cab_w - 8, font_h + 8,
                                act ? colors.title_bg : colors.btn_bg, act);
                char fline[80];
                snprintf(fline, sizeof(fline), "%s (%d)", folder_labels[f], mail_folder_count(&st, folder_names[f]));
                XSetForeground(dpy, gc, act ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, cab_x + 10, fy + font_asc + 2, fline, (int)strlen(fline));
            }

            /* 2. Upper-Right: Message Header List */
            draw_bevel_rect(dpy, back_buf, gc, &colors, hdr_x, cab_y, hdr_w, cab_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, hdr_x + 2, cab_y + 2, hdr_w - 4, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, hdr_x + 10, cab_y + font_asc + 4,
                        "#   State    Fmt   From           Subject", 41);

            int ry = cab_y + font_h + 14;
            int row_h = font_h + 8;
            for (int i = 0; i < st.num_msgs && ry + row_h < cab_y + cab_h - 4; i++) {
                const DecwMailMsg* m = &st.msgs[i];
                if (strcmp(st.cur_folder, "ALL") != 0 && strcasecmp(m->folder, st.cur_folder) != 0) continue;
                int sel = (i == st.sel_msg_idx);
                if (sel) {
                    draw_bevel_rect(dpy, back_buf, gc, &colors, hdr_x + 4, ry, hdr_w - 8, row_h - 1, colors.title_bg, 1);
                }
                char mline[200];
                snprintf(mline, sizeof(mline), "%-2d  %-7s  %-4s  %-13s  %s",
                         i + 1, m->status, m->fmt, m->from, m->subject);
                XSetForeground(dpy, gc, sel ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, hdr_x + 10, ry + font_asc + 2, mline, (int)strlen(mline));
                ry += row_h;
            }

            /* 3. Lower Pane: Message Content Reader */
            int rdr_y = cab_y + cab_h + 6;
            int rdr_h = avail_h - cab_h - 6;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, rdr_y, win_w - 20, rdr_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, 12, rdr_y + 2, win_w - 24, font_h + 10, colors.btn_bg, 0);

            if (st.sel_msg_idx >= 0 && st.sel_msg_idx < st.num_msgs) {
                const DecwMailMsg* m = &st.msgs[st.sel_msg_idx];
                char h1[200], h2[200];
                snprintf(h1, sizeof(h1), "Message #%d  |  Drawer: %s -> %s  |  Format: %s  |  Status: [%s]",
                         st.sel_msg_idx + 1, m->drawer, m->folder, m->fmt, m->status);
                snprintf(h2, sizeof(h2), "From: %-16s   To: %-16s   Date: %s", m->from, m->to, m->date);
                char h3[200];
                snprintf(h3, sizeof(h3), "Subject: %s", m->subject);

                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, 20, rdr_y + font_asc + 4, h1, (int)strlen(h1));
                int ty = rdr_y + font_h + 16 + font_asc;
                XSetForeground(dpy, gc, colors.title_bg);
                XDrawString(dpy, back_buf, gc, 20, ty, h2, (int)strlen(h2));
                ty += font_h + 6;
                XDrawString(dpy, back_buf, gc, 20, ty, h3, (int)strlen(h3));
                ty += font_h + 10;
                XSetForeground(dpy, gc, colors.bevel_dark);
                XDrawLine(dpy, back_buf, gc, 18, ty - font_asc, win_w - 28, ty - font_asc);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, 20, ty + 4, m->body, (int)strlen(m->body));
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                int dw = (win_w - 60 < 560) ? (win_w - 60) : 560;
                int dh = font_h * 9 + 68;
                int dx = (win_w - dw) / 2;
                int dy = (win_h - dh) / 2;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx, dy, dw, dh, colors.bg_gray, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 4, dy + 4, dw - 8, font_h + 8, colors.title_bg, 0);
                XSetForeground(dpy, gc, colors.title_fg);
                XDrawString(dpy, back_buf, gc, dx + 12, dy + 6 + font_asc, "DECwindows Mail: Compose / Send Message", 39);

                int fy0 = dy + font_h * 2 + 12;
                int fh = font_h + 10;
                const char* flbls[3] = {"To (DECnet):", "Subject:", "Body Text:"};
                const char* fvals[3] = {st.c_to, st.c_subj, st.c_body};
                for (int f = 0; f < 3; f++) {
                    int fy = fy0 + f * (fh + 6);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, dx + 14, fy + font_asc + 2, flbls[f], (int)strlen(flbls[f]));
                    draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 145, fy, dw - 161, fh, colors.cmd_bg, 1);
                    char vbuf[168];
                    snprintf(vbuf, sizeof(vbuf), "%s%s", fvals[f], (st.focus_field == f) ? "_" : "");
                    XDrawString(dpy, back_buf, gc, dx + 152, fy + font_asc + 2, vbuf, (int)strlen(vbuf));
                }
                int by = dy + dh - fh - 12;
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + 40, by, 140, fh, colors.btn_bg, 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, dx + dw - 180, by, 140, fh, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, dx + 68, by + font_asc + 3, "Send Mail", 9);
                XDrawString(dpy, back_buf, gc, dx + dw - 140, by + font_asc + 3, "Cancel", 6);
            } else if (st.dialog_mode == 2) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows Mail: About",
                    "DECwindows Motif Mail V3.0 (DECW$MAIL / dxmail)",
                    "Hierarchical Mail Cabinet, Drawers, Folders & CDA/DDIF Reader",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                if (st.num_msgs > 1) st.sel_msg_idx = 1;
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
               title, cfg->app_id[0] ? cfg->app_id : "dxmail", st.num_msgs, 10, font_desc, info);
        fflush(stdout);
    }

    XFreePixmap(dpy, back_buf);
    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}

#endif /* DECW_GUI_GROUP2_H */
