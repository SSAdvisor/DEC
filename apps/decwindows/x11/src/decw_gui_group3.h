#ifndef DECW_GUI_GROUP3_H
#define DECW_GUI_GROUP3_H

/* ============================================================================
 * 7. DECwindows Bookreader (DECW$BOOKREADER / dxbook)
 *    Authentic OSF/Motif 1.1 Bookshelf Library, Navigation Tree & Topic Reader
 * ============================================================================ */

typedef struct {
    char code[24];
    char title[80];
} DecwBook;

typedef struct {
    char book_code[24];
    char sec[16];
    char title[80];
    char body[220];
    char xref[16];
} DecwTopic;

typedef struct {
    DecwBook books[8];
    int num_books;
    DecwTopic topics[24];
    int num_topics;
    int cur_topic;
    char bookmarks[16][80];
    int num_bm;
    int dialog_mode;   /* 0=none, 1=About */
} DecwBookState;

static void bk_add_book(DecwBookState* st, const char* code, const char* title) {
    if (st->num_books >= 8) return;
    snprintf(st->books[st->num_books].code, 24, "%s", code);
    snprintf(st->books[st->num_books].title, 80, "%s", title);
    st->num_books++;
}

static void bk_add_topic(DecwBookState* st, const char* bcode, const char* sec,
                         const char* title, const char* body, const char* xref) {
    if (st->num_topics >= 24) return;
    DecwTopic* t = &st->topics[st->num_topics++];
    snprintf(t->book_code, sizeof(t->book_code), "%s", bcode);
    snprintf(t->sec, sizeof(t->sec), "%s", sec);
    snprintf(t->title, sizeof(t->title), "%s", title);
    snprintf(t->body, sizeof(t->body), "%s", body);
    snprintf(t->xref, sizeof(t->xref), "%s", xref);
}

static void bk_load_state(DecwBookState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[360];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            if (strncmp(line, "B|", 2) == 0) {
                char c[24] = "", t[80] = "";
                if (sscanf(line + 2, "%23[^|]|%79[^\n]", c, t) == 2) bk_add_book(st, c, t);
            } else if (strncmp(line, "T|", 2) == 0) {
                char bc[24] = "", sc[16] = "", tl[80] = "", bd[220] = "", xr[16] = "";
                if (sscanf(line + 2, "%23[^|]|%15[^|]|%79[^|]|%219[^|]|%15[^\n]", bc, sc, tl, bd, xr) == 5) {
                    bk_add_topic(st, bc, sc, tl, bd, xr);
                }
            }
        }
        fclose(fp);
    }
    if (st->num_topics == 0) {
        bk_add_book(st, "VMS_DCL", "VAX/VMS DCL Dictionary (DECW$BOOK)");
        bk_add_book(st, "DECWIN_USER", "DECwindows Desktop User's Guide (DECW$BOOK)");
        bk_add_book(st, "BP2_REF", "PDP-11 & VAX BASIC-PLUS-2 Reference Manual");
        bk_add_topic(st, "VMS_DCL", "1.1", "Overview of Digital Command Language",
                     "DCL provides interactive and batch command control across VAX/VMS nodes.", "1.2");
        bk_add_topic(st, "VMS_DCL", "1.2", "SET TERMINAL Command Qualifiers",
                     "Use SET TERMINAL /INQUIRE /DEVICE=VT300 to configure DECterm sessions.", "2.1");
        bk_add_topic(st, "DECWIN_USER", "2.1", "Using the DECwindows Session Manager",
                     "Session Manager launches DECterm, Bookreader, FileView, and Mail.", "2.2");
        bk_add_topic(st, "DECWIN_USER", "2.2", "Navigating Hypertext Bookshelves",
                     "Double-click any book icon in LIBRARY.DECW$BOOKSHELF or click Hotspots.", "3.1");
        bk_add_topic(st, "BP2_REF", "3.1", "RMS Indexed and Sequential File I/O",
                     "OPEN file FOR INPUT or OUTPUT with MAP buffers and primary keys.", "3.2");
        bk_add_topic(st, "BP2_REF", "3.2", "Task-Builder and Overlay Compilation",
                     "Compile BASIC-PLUS-2 modules with basicc and link with basiclink.", "1.1");
    }
    snprintf(st->bookmarks[st->num_bm++], 80, "[1.1] Overview of Digital Command Language");
}

static void bk_follow_xref(DecwBookState* st) {
    if (st->cur_topic < 0 || st->cur_topic >= st->num_topics) return;
    const char* target = st->topics[st->cur_topic].xref;
    for (int i = 0; i < st->num_topics; i++) {
        if (strcasecmp(st->topics[i].sec, target) == 0) {
            st->cur_topic = i;
            return;
        }
    }
}

static int run_bookreader_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "bookreader", &colors);

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
    int rec_w = 1080, rec_h = 720;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 500) ? cfg->width : (740 + font_scale * 110);
    int win_h = (cfg->height >= 380) ? cfg->height : (470 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 70, 70,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Bookreader - LIBRARY.DECW$BOOKSHELF";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$BOOKREADER");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwBookState st;
    bk_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Book 1: VAX/VMS DCL",      101},
        {"Book 2: DECwindows Guide", 102},
        {"Book 3: BASIC-PLUS-2 Ref", 103},
        {"---",                      0},
        {"Exit",                     109}
    };
    static const DecwMenuItem nav_items[] = {
        {"Previous Topic",           201},
        {"Next Topic",               202},
        {"Follow Hotspot XRef",      203}
    };
    static const DecwMenuItem bm_items[] = {
        {"Bookmark Current Topic",   301},
        {"Clear Bookmarks",          302}
    };
    static const DecwMenuItem help_items[] = {
        {"About Bookreader...",      401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File",      0, 0, 0, file_items, 5},
        {"Navigate",  0, 0, 0, nav_items,  3},
        {"Bookmarks", 0, 0, 0, bm_items,   2},
        {"Help",      0, 0, 1, help_items, 1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "Bookreader: %d books, %d topics | Click topic outline on left or Hotspot link",
             st.num_books, st.num_topics);

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
    int nav_x = 10, nav_y = 124, nav_w = 290, nav_h = 280;
    int hot_x = 0, hot_y = 0, hot_w = 0, hot_h = 0;

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
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) st.dialog_mode = 0;
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) st.cur_topic = 0;
                    else if (mact == 102 && st.num_topics >= 3) st.cur_topic = 2;
                    else if (mact == 103 && st.num_topics >= 5) st.cur_topic = 4;
                    else if (mact == 109) running = 0;
                    else if (mact == 201 && st.num_topics > 0) st.cur_topic = (st.cur_topic + st.num_topics - 1) % st.num_topics;
                    else if (mact == 202 && st.num_topics > 0) st.cur_topic = (st.cur_topic + 1) % st.num_topics;
                    else if (mact == 203) bk_follow_xref(&st);
                    else if (mact == 301 && st.num_bm < 16) {
                        char bm_tmp[80];
                        snprintf(bm_tmp, sizeof(bm_tmp), "[%s] %.60s",
                                 st.topics[st.cur_topic].sec, st.topics[st.cur_topic].title);
                        strcpy(st.bookmarks[st.num_bm++], bm_tmp);
                    } else if (mact == 302) st.num_bm = 0;
                    else if (mact == 401) st.dialog_mode = 1;
                    continue;
                }

                /* Toolbar click */
                if (my >= tb_y && my <= tb_y + tb_h) {
                    int b = (mx - 10) * 5 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b == 0 && st.num_topics > 0) st.cur_topic = (st.cur_topic + st.num_topics - 1) % st.num_topics;
                    else if (b == 1 && st.num_topics > 0) st.cur_topic = (st.cur_topic + 1) % st.num_topics;
                    else if (b == 2) bk_follow_xref(&st);
                    else if (b == 3 && st.num_bm < 16) {
                        char bm_tmp[80];
                        snprintf(bm_tmp, sizeof(bm_tmp), "[%s] %.60s",
                                 st.topics[st.cur_topic].sec, st.topics[st.cur_topic].title);
                        strcpy(st.bookmarks[st.num_bm++], bm_tmp);
                    } else if (b == 4) st.cur_topic = 0;
                    continue;
                }

                /* Hotspot button click */
                if (mx >= hot_x && mx <= hot_x + hot_w && my >= hot_y && my <= hot_y + hot_h) {
                    bk_follow_xref(&st);
                    snprintf(status_msg, sizeof(status_msg), "Followed Hypertext Hotspot -> Section %s: %s",
                             st.topics[st.cur_topic].sec, st.topics[st.cur_topic].title);
                    continue;
                }

                /* Left Outline Topic List click */
                if (mx >= nav_x && mx < nav_x + nav_w && my >= nav_y + font_h + 14 && my < nav_y + nav_h) {
                    int row = (my - (nav_y + font_h + 14)) / (font_h + 10);
                    if (row >= 0 && row < st.num_topics) {
                        st.cur_topic = row;
                        snprintf(status_msg, sizeof(status_msg), "Opened Topic %s: %s",
                                 st.topics[row].sec, st.topics[row].title);
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                need_redraw = 1;
                if (ks == XK_Escape) {
                    if (st.dialog_mode != 0) st.dialog_mode = 0;
                    else running = 0;
                } else if ((ks == XK_Down || ks == XK_Right) && st.num_topics > 0) st.cur_topic = (st.cur_topic + 1) % st.num_topics;
                else if ((ks == XK_Up || ks == XK_Left) && st.num_topics > 0) st.cur_topic = (st.cur_topic + st.num_topics - 1) % st.num_topics;
                else if (ks == XK_Return || ks == XK_KP_Enter) bk_follow_xref(&st);
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
            const char* tb_lbls[5] = {"< Prev Topic", "Next Topic >", "Follow Hotspot", "+ Bookmark", "First Topic"};
            int bw = (win_w - 20) / 5;
            for (int i = 0; i < 5; i++) {
                int bx = 10 + i * bw;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, tb_y, bw - 4, tb_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, tb_y + font_asc + 4, tb_lbls[i], (int)strlen(tb_lbls[i]));
            }

            int st_h = font_h + 10;
            nav_x = 10;
            nav_y = tb_y + tb_h + 6;
            nav_w = (win_w - 28) * 40 / 100;
            nav_h = win_h - nav_y - st_h - 14;

            /* Left Pane: Library & Navigation Window */
            draw_bevel_rect(dpy, back_buf, gc, &colors, nav_x, nav_y, nav_w, nav_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, nav_x + 2, nav_y + 2, nav_w - 4, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, nav_x + 10, nav_y + font_asc + 4, "Navigation Outline (Books & Topics)", 35);

            int row_h = font_h + 10;
            for (int i = 0; i < st.num_topics; i++) {
                int ry = nav_y + font_h + 16 + i * row_h;
                if (ry + row_h > nav_y + nav_h - 4) break;
                int sel = (i == st.cur_topic);
                draw_bevel_rect(dpy, back_buf, gc, &colors, nav_x + 4, ry, nav_w - 8, row_h - 2,
                                sel ? colors.title_bg : colors.btn_bg, sel);
                char tline[96];
                snprintf(tline, sizeof(tline), "[%s] %s - %s",
                         st.topics[i].book_code, st.topics[i].sec, st.topics[i].title);
                XSetForeground(dpy, gc, sel ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, nav_x + 10, ry + font_asc + 2, tline, (int)strlen(tline));
            }

            /* Right Pane: Topic Reading Window */
            int rx = nav_x + nav_w + 8;
            int rw = win_w - rx - 10;
            draw_bevel_rect(dpy, back_buf, gc, &colors, rx, nav_y, rw, nav_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, rx + 2, nav_y + 2, rw - 4, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, rx + 10, nav_y + font_asc + 4, "DECW$BOOK Topic Reader Window", 29);

            if (st.cur_topic >= 0 && st.cur_topic < st.num_topics) {
                const DecwTopic* tp = &st.topics[st.cur_topic];
                const char* btitle = tp->book_code;
                for (int b = 0; b < st.num_books; b++) {
                    if (strcasecmp(st.books[b].code, tp->book_code) == 0) btitle = st.books[b].title;
                }
                int ty = nav_y + font_h * 2 + 16;
                char bline[160], sline[160];
                snprintf(bline, sizeof(bline), "Manual : %s", btitle);
                snprintf(sline, sizeof(sline), "Section %s : %s", tp->sec, tp->title);

                XSetForeground(dpy, gc, colors.bevel_dark);
                XDrawString(dpy, back_buf, gc, rx + 16, ty, bline, (int)strlen(bline));
                ty += font_h + 10;
                XSetForeground(dpy, gc, colors.title_bg);
                XDrawString(dpy, back_buf, gc, rx + 16, ty, sline, (int)strlen(sline));
                XDrawLine(dpy, back_buf, gc, rx + 16, ty + 4, rx + rw - 16, ty + 4);
                ty += font_h + 18;

                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, rx + 16, ty, tp->body, (int)strlen(tp->body));
                ty += font_h * 2 + 12;

                /* Clickable Hypertext Hotspot Button */
                hot_x = rx + 16;
                hot_y = ty;
                hot_w = rw - 32;
                hot_h = font_h + 14;
                draw_bevel_rect(dpy, back_buf, gc, &colors, hot_x, hot_y, hot_w, hot_h, colors.btn_bg, 0);
                char hstr[128];
                snprintf(hstr, sizeof(hstr), "[Hotspot Cross-Reference] -> Click to Jump to Section %s", tp->xref);
                XSetForeground(dpy, gc, colors.title_bg);
                XDrawString(dpy, back_buf, gc, hot_x + 12, hot_y + font_asc + 4, hstr, (int)strlen(hstr));

                /* Saved Bookmarks Box */
                ty = hot_y + hot_h + 18;
                XSetForeground(dpy, gc, colors.bevel_dark);
                XDrawString(dpy, back_buf, gc, rx + 16, ty + font_asc, "Saved User Bookmarks:", 21);
                for (int b = 0; b < st.num_bm && b < 4; b++) {
                    ty += font_h + 6;
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, rx + 24, ty + font_asc, st.bookmarks[b], (int)strlen(st.bookmarks[b]));
                }
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows Bookreader: About",
                    "DECwindows Motif Bookreader V3.0 (DECW$BOOKREADER / dxbook)",
                    "Online Documentation Bookshelf, Topic Outline & Hypertext Viewer",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                bk_follow_xref(&st);
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
               title, cfg->app_id[0] ? cfg->app_id : "bookreader", st.num_topics, 9, font_desc, info);
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
 * 8. DECwindows CDA Viewer (DECW$CDAVIEWER / dxvdoc)
 *    Authentic OSF/Motif 1.1 Compound Document Page Canvas, Vector ISL & DTIF
 * ============================================================================ */

typedef struct {
    int page;
    char type[24];
    char desc[64];
    char body[192];
} DecwCdaSeg;

typedef struct {
    char doc_name[64];
    char doc_fmt[48];
    char doc_auth[64];
    int cur_page;
    int max_page;
    int all_pages;
    DecwCdaSeg segs[24];
    int num_segs;
    int dialog_mode;   /* 0=none, 1=Audit Report, 2=About */
} DecwCdaState;

static void cda_add_seg(DecwCdaState* st, int pg, const char* type, const char* desc, const char* body) {
    if (st->num_segs >= 24) return;
    DecwCdaSeg* s = &st->segs[st->num_segs++];
    s->page = pg;
    snprintf(s->type, sizeof(s->type), "%s", type);
    snprintf(s->desc, sizeof(s->desc), "%s", desc);
    snprintf(s->body, sizeof(s->body), "%s", body);
    if (pg > st->max_page) st->max_page = pg;
}

static void cda_load_state(DecwCdaState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    strcpy(st->doc_name, "ALPHA_SPEC.DDIF");
    strcpy(st->doc_fmt, "DDIF V1.2 (Compound Document)");
    strcpy(st->doc_auth, "DEC Alpha Architecture Group (MRO)");
    st->cur_page = 1;
    st->max_page = 3;

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[360];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            if (strncmp(line, "HDR|", 4) == 0) {
                sscanf(line + 4, "%63[^|]|%47[^|]|%63[^|]|%d", st->doc_name, st->doc_fmt, st->doc_auth, &st->max_page);
            } else if (strncmp(line, "SEG|", 4) == 0) {
                int pg = 1;
                char ty[24] = "", ds[64] = "", bd[192] = "";
                if (sscanf(line + 4, "%d|%23[^|]|%63[^|]|%191[^\n]", &pg, ty, ds, bd) == 4) {
                    cda_add_seg(st, pg, ty, ds, bd);
                }
            }
        }
        fclose(fp);
    }
    if (st->num_segs == 0) {
        cda_add_seg(st, 1, "HEADER", "DDIF$S_SEG_HDR (ISO-Latin-1)", "DEC ALPHA AXP 21064 ARCHITECTURE SPECIFICATION");
        cda_add_seg(st, 1, "TEXT", "DDIF$S_SEG_TXT (Galleys 1-2)", "64-bit RISC load/store architecture with 32 integer and 32 FP registers.");
        cda_add_seg(st, 1, "GRAPHIC", "DDIF$S_SEG_ISL (600x400 Sixel/ISL)", "[DIAGRAM: Superpipelined 7-Stage Dual-Issue Execution Pipeline]");
        cda_add_seg(st, 2, "TABLE", "DTIF$S_TBL_SPEC (4x3 Matrix)", "CHIP: 21064 (EV4) | CLOCK: 150-200 MHz | CACHE: 8KB I + 8KB D");
        cda_add_seg(st, 2, "TEXT", "DDIF$S_SEG_TXT (PALcode Layer)", "Privileged Architecture Library (PALcode) supports OpenVMS, OSF/1, and NT.");
        cda_add_seg(st, 3, "FOOTER", "DDIF$S_SEG_FTR (Document Control)", "DEC-AXP-ARCH-1992-REV1 | Digital Equipment Corporation, Maynard MA");
    }
}

static int run_cdaviewer_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "cdaviewer", &colors);

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
    int rec_w = 1080, rec_h = 740;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 500) ? cfg->width : (750 + font_scale * 110);
    int win_h = (cfg->height >= 380) ? cfg->height : (480 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 75, 75,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows CDA Viewer - ALPHA_SPEC.DDIF";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$CDAVIEWER");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwCdaState st;
    cda_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Reload DDIF Document", 101},
        {"DDIF/DTIF Audit...",   102},
        {"---",                  0},
        {"Exit",                 109}
    };
    static const DecwMenuItem view_items[] = {
        {"Previous Page",        201},
        {"Next Page",            202},
        {"Toggle All-Pages View",203}
    };
    static const DecwMenuItem fmt_items[] = {
        {"Format: DDIF V1.2",    301},
        {"Format: DTIF Table",   302},
        {"Format: PostScript",   303}
    };
    static const DecwMenuItem help_items[] = {
        {"About CDA Viewer...",  401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File",   0, 0, 0, file_items, 4},
        {"View",   0, 0, 0, view_items, 3},
        {"Format", 0, 0, 0, fmt_items,  3},
        {"Help",   0, 0, 1, help_items, 1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "CDA Document: %s (%d pages, %d DDIF/DTIF segments)",
             st.doc_name, st.max_page, st.num_segs);

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
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) st.dialog_mode = 0;
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) cda_load_state(&st, NULL);
                    else if (mact == 102) st.dialog_mode = 1;
                    else if (mact == 109) running = 0;
                    else if (mact == 201 && st.cur_page > 1) { st.cur_page--; st.all_pages = 0; }
                    else if (mact == 202 && st.cur_page < st.max_page) { st.cur_page++; st.all_pages = 0; }
                    else if (mact == 203) st.all_pages = !st.all_pages;
                    else if (mact == 301) strcpy(st.doc_fmt, "DDIF V1.2 (Compound Document)");
                    else if (mact == 302) strcpy(st.doc_fmt, "DTIF V1.1 (Tabular Matrix)");
                    else if (mact == 303) strcpy(st.doc_fmt, "PostScript Level 2 Preview");
                    else if (mact == 401) st.dialog_mode = 2;
                    continue;
                }

                if (my >= tb_y && my <= tb_y + tb_h) {
                    int b = (mx - 10) * 5 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b == 0 && st.cur_page > 1) { st.cur_page--; st.all_pages = 0; }
                    else if (b == 1 && st.cur_page < st.max_page) { st.cur_page++; st.all_pages = 0; }
                    else if (b == 2) st.all_pages = !st.all_pages;
                    else if (b == 3) st.dialog_mode = 1;
                    else if (b == 4) { st.cur_page = 1; st.all_pages = 0; }
                    snprintf(status_msg, sizeof(status_msg), "Viewing %s | Page %d of %d (%s)",
                             st.doc_name, st.cur_page, st.max_page, st.doc_fmt);
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                need_redraw = 1;
                if (ks == XK_Escape) {
                    if (st.dialog_mode != 0) st.dialog_mode = 0;
                    else running = 0;
                } else if ((ks == XK_Right || ks == XK_Down) && st.cur_page < st.max_page) st.cur_page++;
                else if ((ks == XK_Left || ks == XK_Up) && st.cur_page > 1) st.cur_page--;
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
            const char* tb_lbls[5] = {"< Prev Page", "Next Page >", "All Pages Toggle", "Audit DDIF/DTIF", "Page 1"};
            int bw = (win_w - 20) / 5;
            for (int i = 0; i < 5; i++) {
                int bx = 10 + i * bw;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, tb_y, bw - 4, tb_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, tb_y + font_asc + 4, tb_lbls[i], (int)strlen(tb_lbls[i]));
            }

            /* Main Compound Document Backdrop & Drop-Shadowed Paper Sheet */
            int st_h = font_h + 10;
            int vp_x = 10, vp_y = tb_y + tb_h + 6;
            int vp_w = win_w - 20, vp_h = win_h - vp_y - st_h - 14;
            draw_bevel_rect(dpy, back_buf, gc, &colors, vp_x, vp_y, vp_w, vp_h, colors.bevel_dark, 1);

            int pg_x = vp_x + 22, pg_y = vp_y + 14;
            int pg_w = vp_w - 44, pg_h = vp_h - 28;
            XSetForeground(dpy, gc, BlackPixel(dpy, screen));
            XFillRectangle(dpy, back_buf, gc, pg_x + 6, pg_y + 6, (unsigned int)pg_w, (unsigned int)pg_h);
            draw_bevel_rect(dpy, back_buf, gc, &colors, pg_x, pg_y, pg_w, pg_h, colors.canvas_bg, 0);

            /* Document Running Header */
            char rhdr[256];
            snprintf(rhdr, sizeof(rhdr), "%.48s  |  %.36s  |  Author: %.48s  |  Page %d / %d",
                     st.doc_name, st.doc_fmt, st.doc_auth, st.cur_page, st.max_page);
            XSetForeground(dpy, gc, colors.title_bg);
            XDrawString(dpy, back_buf, gc, pg_x + 16, pg_y + font_asc + 8, rhdr, (int)strlen(rhdr));
            XDrawLine(dpy, back_buf, gc, pg_x + 12, pg_y + font_h + 12, pg_x + pg_w - 12, pg_y + font_h + 12);

            int sy = pg_y + font_h + 22;
            for (int i = 0; i < st.num_segs && sy + font_h * 2 < pg_y + pg_h - 12; i++) {
                const DecwCdaSeg* s = &st.segs[i];
                if (!st.all_pages && s->page != st.cur_page) continue;

                char tag[128];
                snprintf(tag, sizeof(tag), "[Page %d | %s] %s", s->page, s->type, s->desc);
                XSetForeground(dpy, gc, colors.bevel_dark);
                XDrawString(dpy, back_buf, gc, pg_x + 16, sy + font_asc, tag, (int)strlen(tag));
                sy += font_h + 6;

                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, pg_x + 24, sy + font_asc, s->body, (int)strlen(s->body));
                sy += font_h + 10;

                if (strcasecmp(s->type, "GRAPHIC") == 0 && sy + font_h * 3 + 20 < pg_y + pg_h) {
                    /* Render X11 Vector Alpha 21064 7-Stage Pipeline Diagram */
                    int gx = pg_x + 24, gw = pg_w - 48, gh = font_h * 2 + 20;
                    draw_bevel_rect(dpy, back_buf, gc, &colors, gx, sy, gw, gh, colors.cmd_bg, 1);
                    const char* stages[7] = {"S0:IF", "S1:ID", "S2:ISS", "S3:EX1", "S4:EX2", "S5:MEM", "S6:WB"};
                    int sw = (gw - 24) / 7;
                    for (int stg = 0; stg < 7; stg++) {
                        int bx = gx + 12 + stg * sw;
                        draw_bevel_rect(dpy, back_buf, gc, &colors, bx, sy + 6, sw - 8, gh - 12, colors.btn_bg, 0);
                        XSetForeground(dpy, gc, colors.title_bg);
                        XDrawString(dpy, back_buf, gc, bx + 6, sy + (gh + font_asc) / 2 - 2, stages[stg], (int)strlen(stages[stg]));
                    }
                    sy += gh + 8;
                } else if (strcasecmp(s->type, "TABLE") == 0 && sy + font_h * 3 + 16 < pg_y + pg_h) {
                    /* Render DTIF Matrix Table */
                    int tx = pg_x + 24, tw = pg_w - 48, th = font_h * 2 + 16;
                    draw_bevel_rect(dpy, back_buf, gc, &colors, tx, sy, tw, th, colors.btn_bg, 1);
                    const char* cols[3] = {"CHIP: DECchip 21064 (EV4)", "CLOCK: 150 - 200 MHz", "CACHE: 8KB I + 8KB D"};
                    int cw = tw / 3;
                    for (int c = 0; c < 3; c++) {
                        draw_bevel_rect(dpy, back_buf, gc, &colors, tx + c * cw + 2, sy + 2, cw - 4, th - 4, colors.cmd_bg, 0);
                        XSetForeground(dpy, gc, colors.canvas_fg);
                        XDrawString(dpy, back_buf, gc, tx + c * cw + 10, sy + (th + font_asc) / 2 - 2, cols[c], (int)strlen(cols[c]));
                    }
                    sy += th + 8;
                }
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "CDA Conformance Audit Report",
                    "Aggregate: DDIF V1.2 + DTIF V1.1 + DOTS Packed Object",
                    "Segments Verified: 6 (HEADER, TEXT, GRAPHIC ISL, TABLE, FOOTER)",
                    "Conformance Status: PASSED (Zero DDIF/DTIF descriptor errors)",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            } else if (st.dialog_mode == 2) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows CDA Viewer: About",
                    "DECwindows Motif CDA Viewer V3.0 (DECW$CDAVIEWER / dxvdoc)",
                    "Compound Document Architecture (DDIF/DTIF/DOTS/PostScript) Viewer",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                if (st.cur_page < st.max_page) st.cur_page++;
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
               title, cfg->app_id[0] ? cfg->app_id : "cdaviewer", st.num_segs, 9, font_desc, info);
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
 * 9. DECwindows DECterm (DECW$TERMINAL / dxterm)
 *    Authentic OSF/Motif 1.1 VT300 Terminal Emulator with Live DCL Prompt
 * ============================================================================ */

typedef struct {
    char lines[64][160];
    int num_lines;
    char input_line[128];
    char dev_mode[16];     /* VT300, VT220, VT100 */
    int cols;              /* 80 or 132 */
    int rows;              /* 24 or 36 */
    int block_cursor;      /* 1=Block, 0=Underline */
    int phosphor;          /* 0=Green, 1=Amber, 2=White Paper */
    int hold_screen;
    int dialog_mode;       /* 0=none, 1=About */
} DecwTermState;

static void term_append(DecwTermState* st, const char* s) {
    if (st->num_lines >= 60) {
        for (int i = 0; i < 59; i++) strcpy(st->lines[i], st->lines[i + 1]);
        st->num_lines = 59;
    }
    snprintf(st->lines[st->num_lines++], sizeof(st->lines[0]), "%s", s);
}

static void term_load_state(DecwTermState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    strcpy(st->dev_mode, "VT300");
    st->cols = 80;
    st->rows = 24;
    st->block_cursor = 1;
    st->phosphor = 0;

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char buf[256];
        while (st->num_lines < 60 && fgets(buf, sizeof(buf), fp)) {
            buf[strcspn(buf, "\r\n")] = '\0';
            if (strcmp(buf, "$ _ [Ready]") == 0) continue;
            term_append(st, buf);
        }
        fclose(fp);
    }
    if (st->num_lines == 0) {
        term_append(st, "ESC[1mWelcome to VAX/VMS V5.5-2 on node STAR::ESC[0m");
        term_append(st, "    Last interactive login on Friday, 18-OCT-1991 08:42");
        term_append(st, "$ SET TERMINAL /INQUIRE /DEVICE_TYPE=VT300");
        term_append(st, "ESC[7m DECwindows XUI/Motif Session Manager - DECW$TERMINAL V3.0 ESC[0m");
        term_append(st, "$ SHOW TERMINAL");
        term_append(st, "Terminal: _TWA12:   Device_Type: VT300_Series   Owner: SYSTEM");
        term_append(st, "   Width: 80        Page: 24 rows               DEC CRT1, CRT2, CRT3");
        term_append(st, "ESC[4mPID       Process Name    State  Pri      I/O       CPU       Page fltsESC[0m");
        term_append(st, "00000101  SWAPPER         HIB     16        0   0 00:00:01.42         0");
        term_append(st, "00000104  DECW$SERVER_0   LEF      8     4820   0 00:01:14.08      1420");
    }
}

static void term_save_state(const DecwTermState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    for (int i = 0; i < st->num_lines; i++) {
        fprintf(fp, "%s\n", st->lines[i]);
    }
    fprintf(fp, "$ _ [Ready]\n");
    fclose(fp);
}

static void term_exec_dcl(DecwTermState* st, const char* cmd, const char* state_path) {
    char echo_ln[160];
    snprintf(echo_ln, sizeof(echo_ln), "$ %s", cmd);
    term_append(st, echo_ln);

    if (strcasecmp(cmd, "CLEAR") == 0 || strcasecmp(cmd, "CLS") == 0) {
        st->num_lines = 0;
    } else if (strncasecmp(cmd, "SHOW TERM", 9) == 0) {
        char buf[160];
        snprintf(buf, sizeof(buf), "Terminal: _TWA12:  Device_Type: %s_Series  Width: %d  Page: %d rows",
                 st->dev_mode, st->cols, st->rows);
        term_append(st, buf);
    } else if (strncasecmp(cmd, "SHOW SYS", 8) == 0) {
        term_append(st, "OpenVMS V5.5-2 on node STAR::   19-OCT-1991 14:30:00   Uptime  14 06:12:44");
        term_append(st, "00000101 SWAPPER       HIB  16     00000104 DECW$SERVER_0  LEF   8");
        term_append(st, "00000108 DECW$WM       LEF   6     00000112 DECW$TERMINAL  CUR   4");
    } else if (strncasecmp(cmd, "SHOW CLUS", 9) == 0) {
        term_append(st, "View of Cluster from system ID 1025  node: STAR        19-OCT-1991");
        term_append(st, "  SYSTEM     |  MEMBERS  |  STAR (VAX 9000)  |  GALAXY (VAX 6000-440)");
    } else if (strncasecmp(cmd, "DIR", 3) == 0) {
        term_append(st, "Directory SYS$SYSROOT:[SYSMGR]");
        term_append(st, "LOGIN.COM;2        SYSTARTUP_V5.COM;4  SYLOGICALS.COM;3   DECW$PRIVATE.COM;1");
    } else if (strncasecmp(cmd, "HELP", 4) == 0) {
        term_append(st, "DCL Commands: SHOW TERMINAL, SHOW SYSTEM, SHOW CLUSTER, DIR, CLEAR, EXIT");
    } else if (cmd[0]) {
        char out[160];
        snprintf(out, sizeof(out), "%%DCL-I-EXEC, executed '%s' on node STAR:: (%s %dx%d)",
                 cmd, st->dev_mode, st->cols, st->rows);
        term_append(st, out);
    }
    term_save_state(st, state_path);
}

static int run_decterm_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "decterm", &colors);
    unsigned long crt_bg = alloc_color(dpy, screen, "#10161C", BlackPixel(dpy, screen));
    unsigned long phos_green = alloc_color(dpy, screen, "#33FF66", WhitePixel(dpy, screen));
    unsigned long phos_amber = alloc_color(dpy, screen, "#FFB000", WhitePixel(dpy, screen));

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
    int win_w = (cfg->width >= 500) ? cfg->width : (760 + font_scale * 115);
    int win_h = (cfg->height >= 380) ? cfg->height : (480 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 60, 60,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECterm - VAXcluster Node STAR:: (VT300)";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$TERMINAL");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwTermState st;
    term_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Reset VT300 Session", 101},
        {"Clear Screen",        102},
        {"Save Transcript",     103},
        {"---",                 0},
        {"Exit DECterm",        109}
    };
    static const DecwMenuItem cmd_items[] = {
        {"DCL: SHOW TERMINAL",  201},
        {"DCL: SHOW SYSTEM",    202},
        {"DCL: SHOW CLUSTER",   203},
        {"DCL: DIRECTORY",      204},
        {"DCL: HELP",           205}
    };
    static const DecwMenuItem cust_items[] = {
        {"80 Columns (DECCOLM)", 301},
        {"132 Columns (DECCOLM)",302},
        {"VT300 Mode",           303},
        {"VT220 Mode",           304},
        {"Toggle Cursor Style",  305},
        {"Green Phosphor CRT",   306},
        {"Amber Phosphor CRT",   307},
        {"White Paper CRT",      308}
    };
    static const DecwMenuItem help_items[] = {
        {"About DECterm...",     401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File",      0, 0, 0, file_items, 5},
        {"Commands",  0, 0, 0, cmd_items,  5},
        {"Customize", 0, 0, 0, cust_items, 8},
        {"Help",      0, 0, 1, help_items, 1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "Type DCL commands directly on the VT300 screen and press Return | F10/F11 scales font");

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
    int udk_y = 0, udk_h = 34;

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
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) st.dialog_mode = 0;
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) { term_load_state(&st, NULL); term_save_state(&st, cfg->state_path); }
                    else if (mact == 102) st.num_lines = 0;
                    else if (mact == 103) term_save_state(&st, cfg->state_path);
                    else if (mact == 109) running = 0;
                    else if (mact == 201) term_exec_dcl(&st, "SHOW TERMINAL", cfg->state_path);
                    else if (mact == 202) term_exec_dcl(&st, "SHOW SYSTEM", cfg->state_path);
                    else if (mact == 203) term_exec_dcl(&st, "SHOW CLUSTER", cfg->state_path);
                    else if (mact == 204) term_exec_dcl(&st, "DIRECTORY", cfg->state_path);
                    else if (mact == 205) term_exec_dcl(&st, "HELP", cfg->state_path);
                    else if (mact == 301) st.cols = 80;
                    else if (mact == 302) st.cols = 132;
                    else if (mact == 303) strcpy(st.dev_mode, "VT300");
                    else if (mact == 304) strcpy(st.dev_mode, "VT220");
                    else if (mact == 305) st.block_cursor = !st.block_cursor;
                    else if (mact == 306) st.phosphor = 0;
                    else if (mact == 307) st.phosphor = 1;
                    else if (mact == 308) st.phosphor = 2;
                    else if (mact == 401) st.dialog_mode = 1;
                    continue;
                }

                /* Bottom DECUDK Function Key Bar */
                if (my >= udk_y && my <= udk_y + udk_h) {
                    int b = (mx - 10) * 6 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b == 0) term_exec_dcl(&st, "SHOW TERMINAL", cfg->state_path);
                    else if (b == 1) term_exec_dcl(&st, "SHOW SYSTEM", cfg->state_path);
                    else if (b == 2) term_exec_dcl(&st, "SHOW CLUSTER", cfg->state_path);
                    else if (b == 3) term_exec_dcl(&st, "DIRECTORY", cfg->state_path);
                    else if (b == 4) st.phosphor = (st.phosphor + 1) % 3;
                    else if (b == 5) st.num_lines = 0;
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
                    term_exec_dcl(&st, st.input_line, cfg->state_path);
                    st.input_line[0] = '\0';
                } else if (ks == XK_BackSpace || ks == XK_Delete) {
                    size_t l = strlen(st.input_line);
                    if (l > 0) st.input_line[l - 1] = '\0';
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
                } else if (n > 0 && kbuf[0] >= 32 && kbuf[0] < 127 && strlen(st.input_line) + 1 < sizeof(st.input_line)) {
                    size_t l = strlen(st.input_line);
                    st.input_line[l] = kbuf[0];
                    st.input_line[l + 1] = '\0';
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

            /* Hardware VT300 Status LED Bar */
            int led_h = font_h + 10;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, cy, win_w - 20, led_h, colors.bg_gray, 1);
            char lstr[200];
            snprintf(lstr, sizeof(lstr), "Device: %s_Series  |  Geometry: %dx%d  |  Cursor: %s  |  LEDs: [o]Online [ ]Hold [ ]Wait",
                     st.dev_mode, st.cols, st.rows, st.block_cursor ? "BLOCK" : "UNDERLINE");
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 18, cy + font_asc + 3, lstr, (int)strlen(lstr));

            /* Main VT300 CRT Screen */
            int st_h = font_h + 10;
            udk_h = font_h + 14;
            int crt_y = cy + led_h + 4;
            int crt_h = win_h - crt_y - udk_h - st_h - 16;
            udk_y = crt_y + crt_h + 4;

            unsigned long bg_col = (st.phosphor == 2) ? colors.cmd_bg : crt_bg;
            unsigned long fg_col = (st.phosphor == 0) ? phos_green : (st.phosphor == 1 ? phos_amber : BlackPixel(dpy, screen));
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, crt_y, win_w - 20, crt_h, bg_col, 1);

            int line_h = font_h + 4;
            int max_vis = (crt_h - 16) / line_h - 1;
            if (max_vis < 4) max_vis = 4;
            int start_i = (st.num_lines > max_vis) ? (st.num_lines - max_vis) : 0;
            int ry = crt_y + 8;

            for (int i = start_i; i < st.num_lines; i++) {
                const char* raw = st.lines[i];
                char clean[160];
                int rev = (strstr(raw, "ESC[7m") != NULL);
                int und = (strstr(raw, "ESC[4m") != NULL);
                /* Strip ESC[...] tags for clean visual rendering */
                int p = 0;
                for (int k = 0; raw[k] && p < 155; ) {
                    if (strncmp(&raw[k], "ESC[", 4) == 0) {
                        while (raw[k] && raw[k] != 'm') k++;
                        if (raw[k] == 'm') k++;
                    } else {
                        clean[p++] = raw[k++];
                    }
                }
                clean[p] = '\0';

                if (rev) {
                    XSetForeground(dpy, gc, fg_col);
                    XFillRectangle(dpy, back_buf, gc, 18, ry, (unsigned int)(win_w - 36), (unsigned int)line_h);
                    XSetForeground(dpy, gc, bg_col);
                    XDrawString(dpy, back_buf, gc, 22, ry + font_asc + 1, clean, (int)strlen(clean));
                } else {
                    XSetForeground(dpy, gc, fg_col);
                    XDrawString(dpy, back_buf, gc, 18, ry + font_asc + 1, clean, (int)strlen(clean));
                    if (und) {
                        XDrawLine(dpy, back_buf, gc, 18, ry + font_asc + 3, 18 + p * (font_h / 2 + 1), ry + font_asc + 3);
                    }
                }
                ry += line_h;
            }

            /* Live interactive DCL prompt line */
            char prompt_ln[160];
            snprintf(prompt_ln, sizeof(prompt_ln), "$ %s%s", st.input_line, st.block_cursor ? "[]" : "_");
            XSetForeground(dpy, gc, fg_col);
            XDrawString(dpy, back_buf, gc, 18, ry + font_asc + 2, prompt_ln, (int)strlen(prompt_ln));

            /* Bottom VT300 Programmable Function Key Bar (DECUDK) */
            const char* udk_lbls[6] = {"F17 ShTerm", "F18 ShSys", "F19 Cluster", "F20 Dir", "Phosphor CRT", "Clear Screen"};
            int bw = (win_w - 20) / 6;
            for (int i = 0; i < 6; i++) {
                int bx = 10 + i * bw;
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, udk_y, bw - 4, udk_h, colors.btn_bg, 0);
                XSetForeground(dpy, gc, colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 8, udk_y + font_asc + 4, udk_lbls[i], (int)strlen(udk_lbls[i]));
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows DECterm: About",
                    "DECwindows Motif DECterm V3.0 (DECW$TERMINAL / dxterm)",
                    "VT300 / VT220 / VT100 Video Terminal & DCL Session Emulator",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                term_exec_dcl(&st, "SHOW TERMINAL", cfg->state_path);
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
               title, cfg->app_id[0] ? cfg->app_id : "decterm", st.num_lines, 10, font_desc, info);
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
 * 10. DECwindows DECsound (DECW$SOUND / dxsound)
 *     Authentic OSF/Motif 1.1 Audio Transport Deck, Waveform Scope & VU Meter
 * ============================================================================ */

typedef struct {
    char name[48];
    char fmt[24];
    int sec;
    int peak;
    char desc[96];
} DecwAudioClip;

typedef struct {
    char out_dev[48];
    char in_dev[48];
    int vol_pct;
    int gain_pct;
    int cur_clip;
    int transport_state;   /* 0=STOPPED, 1=PLAYING, 2=PAUSED, 3=RECORDING */
    DecwAudioClip clips[16];
    int num_clips;
    int dialog_mode;       /* 0=none, 1=About */
} DecwSoundState;

static void snd_add_clip(DecwSoundState* st, const char* name, const char* fmt, int sec, int pk, const char* desc) {
    if (st->num_clips >= 16) return;
    DecwAudioClip* c = &st->clips[st->num_clips++];
    snprintf(c->name, sizeof(c->name), "%s", name);
    snprintf(c->fmt, sizeof(c->fmt), "%s", fmt);
    c->sec = sec;
    c->peak = pk;
    snprintf(c->desc, sizeof(c->desc), "%s", desc);
}

static void snd_load_state(DecwSoundState* st, const char* path) {
    memset(st, 0, sizeof(*st));
    strcpy(st->out_dev, "SPEAKER (Internal BBA)");
    strcpy(st->in_dev, "MICROPHONE (DECaudio Handset)");
    st->vol_pct = 80;
    st->gain_pct = 75;
    st->transport_state = 1;

    FILE* fp = (path && path[0]) ? fopen(path, "r") : NULL;
    if (fp) {
        char line[320];
        while (fgets(line, sizeof(line), fp)) {
            line[strcspn(line, "\r\n")] = '\0';
            if (strncmp(line, "CFG|", 4) == 0) {
                sscanf(line + 4, "%47[^|]|%47[^|]|%d|%d", st->out_dev, st->in_dev, &st->vol_pct, &st->gain_pct);
            } else if (strncmp(line, "CLP|", 4) == 0) {
                char nm[48] = "", fm[24] = "", ds[96] = "";
                int sc = 1, pk = 80;
                if (sscanf(line + 4, "%47[^|]|%23[^|]|%d|%d|%95[^\n]", nm, fm, &sc, &pk, ds) == 5) {
                    snd_add_clip(st, nm, fm, sc, pk, ds);
                }
            }
        }
        fclose(fp);
    }
    if (st->num_clips == 0) {
        snd_add_clip(st, "VAX_BOOT_CHIME.AU", "MULAW-8KHZ", 4, 85, "VAXstation 4000 BBA Power-On Self-Test Chime");
        snd_add_clip(st, "NEWMAIL_BELL.AU", "MULAW-8KHZ", 2, 90, "DECwindows Mail New Message Arrival Bell");
        snd_add_clip(st, "ALPHA_INTRO.AU", "PCM16-11KHZ", 18, 92, "Ken Olsen & Bob Supnik Alpha AXP Launch Voice Note");
        snd_add_clip(st, "CLUSTER_ALERT.AU", "MULAW-8KHZ", 6, 95, "VAXcluster Quorum Transition Spoken Alert");
        snd_add_clip(st, "CDA_VOICENOTE.AU", "MULAW-8KHZ", 12, 78, "DDIF Compound Document Embedded Voice Annotation");
        snd_add_clip(st, "DECUS_THEME.AU", "PCM16-11KHZ", 25, 88, "DECUS Symposium Digital Audio Synthesis Demo");
    }
}

static void snd_save_state(const DecwSoundState* st, const char* path) {
    if (!path || !path[0]) return;
    FILE* fp = fopen(path, "w");
    if (!fp) return;
    fprintf(fp, "CFG|%s|%s|%d|%d\n", st->out_dev, st->in_dev, st->vol_pct, st->gain_pct);
    for (int i = 0; i < st->num_clips; i++) {
        fprintf(fp, "CLP|%s|%s|%d|%d|%s\n",
                st->clips[i].name, st->clips[i].fmt, st->clips[i].sec, st->clips[i].peak, st->clips[i].desc);
    }
    fclose(fp);
}

static int run_decsound_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "decsound", &colors);
    unsigned long scope_bg = alloc_color(dpy, screen, "#101A18", BlackPixel(dpy, screen));
    unsigned long wave_col = alloc_color(dpy, screen, "#38FF90", WhitePixel(dpy, screen));
    unsigned long vu_red   = alloc_color(dpy, screen, "#E03030", BlackPixel(dpy, screen));

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
    int win_h = (cfg->height >= 380) ? cfg->height : (480 + font_scale * 75);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 80, 80,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows DECsound - AMD Am79C30A 8kHz Mu-Law";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$SOUND");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    DecwSoundState st;
    snd_load_state(&st, cfg->state_path);

    static const DecwMenuItem file_items[] = {
        {"Load Sample Clips",   101},
        {"Save Clip Library",   102},
        {"---",                 0},
        {"Exit",                109}
    };
    static const DecwMenuItem edit_items[] = {
        {"Record New Voice Clip", 201},
        {"Delete Selected Clip",  202}
    };
    static const DecwMenuItem opt_items[] = {
        {"Output: Internal Speaker", 301},
        {"Output: Headphone Jack",   302},
        {"Output: Line-Out",         303},
        {"---",                      0},
        {"Input: Handset Mic",       304},
        {"Input: Line-In",           305}
    };
    static const DecwMenuItem help_items[] = {
        {"About DECsound...",   401}
    };
    DecwMenuBarMenu menus[4] = {
        {"File",    0, 0, 0, file_items, 4},
        {"Edit",    0, 0, 0, edit_items, 2},
        {"Options", 0, 0, 0, opt_items,  6},
        {"Help",    0, 0, 1, help_items, 1}
    };

    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "DECsound BBA Ready | Playing: %s | Click transport deck, sliders, or clip list",
             st.clips[0].name);

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
    int tr_y = 82, tr_h = 38;
    int sld_y = 240, sld_h = 32;
    int tbl_y = 280, tbl_h = 160;

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
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) st.dialog_mode = 0;
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 4, &open_menu);
                if (mact != 0) {
                    if (mact == 101) { snd_load_state(&st, NULL); snd_save_state(&st, cfg->state_path); }
                    else if (mact == 102) snd_save_state(&st, cfg->state_path);
                    else if (mact == 109) running = 0;
                    else if (mact == 201) {
                        snd_add_clip(&st, "VOICE_MEMO.AU", "MULAW-8KHZ", 8, 91, "Recorded Workstation Voice Annotation");
                        st.cur_clip = st.num_clips - 1;
                        st.transport_state = 3;
                        snd_save_state(&st, cfg->state_path);
                    } else if (mact == 202 && st.num_clips > 1) {
                        for (int i = st.cur_clip; i < st.num_clips - 1; i++) st.clips[i] = st.clips[i + 1];
                        st.num_clips--;
                        if (st.cur_clip >= st.num_clips) st.cur_clip = st.num_clips - 1;
                        snd_save_state(&st, cfg->state_path);
                    } else if (mact == 301) strcpy(st.out_dev, "SPEAKER (Internal BBA)");
                    else if (mact == 302) strcpy(st.out_dev, "HEADPHONE (Front Jack)");
                    else if (mact == 303) strcpy(st.out_dev, "LINE-OUT (Rear BNC)");
                    else if (mact == 304) strcpy(st.in_dev, "MICROPHONE (DECaudio Handset)");
                    else if (mact == 305) strcpy(st.in_dev, "LINE-IN (Auxiliary)");
                    else if (mact == 401) st.dialog_mode = 1;
                    continue;
                }

                /* Transport Deck Buttons */
                if (my >= tr_y && my <= tr_y + tr_h) {
                    int b = (mx - 10) * 6 / (win_w - 20 > 0 ? win_w - 20 : 1);
                    if (b == 0) {
                        snd_add_clip(&st, "VOICE_MEMO.AU", "MULAW-8KHZ", 8, 91, "Recorded Workstation Voice Annotation");
                        st.cur_clip = st.num_clips - 1;
                        st.transport_state = 3;
                        snd_save_state(&st, cfg->state_path);
                    } else if (b == 1) st.transport_state = 1;
                    else if (b == 2) st.transport_state = 2;
                    else if (b == 3) st.transport_state = 0;
                    else if (b == 4 && st.num_clips > 0) st.cur_clip = (st.cur_clip + st.num_clips - 1) % st.num_clips;
                    else if (b == 5 && st.num_clips > 0) st.cur_clip = (st.cur_clip + 1) % st.num_clips;
                    continue;
                }

                /* Volume & Gain Sliders click */
                if (my >= sld_y && my <= sld_y + sld_h) {
                    int half = win_w / 2;
                    if (mx < half) {
                        int pct = (mx - 20) * 100 / (half - 40 > 0 ? half - 40 : 1);
                        if (pct < 0) pct = 0;
                        if (pct > 100) pct = 100;
                        st.vol_pct = pct;
                    } else {
                        int pct = (mx - (half + 10)) * 100 / (half - 40 > 0 ? half - 40 : 1);
                        if (pct < 0) pct = 0;
                        if (pct > 100) pct = 100;
                        st.gain_pct = pct;
                    }
                    snd_save_state(&st, cfg->state_path);
                    continue;
                }

                /* Clip Table click */
                if (my >= tbl_y + font_h + 12 && my <= tbl_y + tbl_h) {
                    int row = (my - (tbl_y + font_h + 12)) / (font_h + 8);
                    if (row >= 0 && row < st.num_clips) {
                        st.cur_clip = row;
                        st.transport_state = 1;
                        snprintf(status_msg, sizeof(status_msg), "Playing Clip #%d: %s (%s, %ds, Peak %d%%)",
                                 row + 1, st.clips[row].name, st.clips[row].fmt, st.clips[row].sec, st.clips[row].peak);
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                need_redraw = 1;
                if (ks == XK_Escape) {
                    if (st.dialog_mode != 0) st.dialog_mode = 0;
                    else running = 0;
                } else if (ks == XK_Up && st.cur_clip > 0) st.cur_clip--;
                else if (ks == XK_Down && st.cur_clip + 1 < st.num_clips) st.cur_clip++;
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

            /* 1. Audio Transport Deck Buttons */
            tr_y = cy;
            tr_h = font_h + 16;
            const char* tr_lbls[6] = {"(o) Record", "|> Play", "|| Pause", "[] Stop", "|<< Prev", "Next >>|"};
            int bw = (win_w - 20) / 6;
            for (int i = 0; i < 6; i++) {
                int bx = 10 + i * bw;
                int act = (i == 0 && st.transport_state == 3) ||
                          (i == 1 && st.transport_state == 1) ||
                          (i == 2 && st.transport_state == 2) ||
                          (i == 3 && st.transport_state == 0);
                draw_bevel_rect(dpy, back_buf, gc, &colors, bx, tr_y, bw - 4, tr_h,
                                act ? colors.title_bg : colors.btn_bg, act);
                XSetForeground(dpy, gc, act ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, bx + 10, tr_y + font_asc + 5, tr_lbls[i], (int)strlen(tr_lbls[i]));
            }

            /* 2. Oscilloscope Waveform & Multi-Segment LED Peak VU Meter */
            int sc_y = tr_y + tr_h + 6;
            int sc_h = font_h * 4 + 28;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, sc_y, win_w - 20, sc_h, scope_bg, 1);

            const DecwAudioClip* clp = (st.cur_clip >= 0 && st.cur_clip < st.num_clips) ? &st.clips[st.cur_clip] : NULL;
            int peak = clp ? clp->peak : 80;
            const char* st_names[4] = {"STOPPED", "PLAYING", "PAUSED", "RECORDING"};
            char sc_hdr[200];
            snprintf(sc_hdr, sizeof(sc_hdr), "[%s]  Clip: %s (%s, %ds)  |  Out: %s",
                     st_names[st.transport_state],
                     clp ? clp->name : "NONE", clp ? clp->fmt : "-", clp ? clp->sec : 0, st.out_dev);
            XSetForeground(dpy, gc, wave_col);
            XDrawString(dpy, back_buf, gc, 20, sc_y + font_asc + 4, sc_hdr, (int)strlen(sc_hdr));

            /* Draw Oscilloscope Waveform Trace */
            int mid_y = sc_y + font_h + (sc_h - font_h * 2 - 12) / 2 + 4;
            int amp_max = (sc_h - font_h * 2 - 20) / 2;
            if (amp_max < 8) amp_max = 8;
            XSetForeground(dpy, gc, colors.bevel_dark);
            XDrawLine(dpy, back_buf, gc, 20, mid_y, win_w - 30, mid_y);
            XSetForeground(dpy, gc, wave_col);
            int prev_x = 20, prev_y = mid_y;
            for (int x = 20; x < win_w - 30; x += 6) {
                double t = (double)(x - 20 + st.cur_clip * 19) * 0.18;
                double env = (st.transport_state == 0) ? 0.1 : ((double)peak / 100.0);
                int dy = (int)(sin(t) * cos(t * 0.37) * amp_max * env);
                XDrawLine(dpy, back_buf, gc, prev_x, prev_y, x, mid_y + dy);
                prev_x = x;
                prev_y = mid_y + dy;
            }

            /* Segmented LED VU Bar at bottom of scope */
            int vu_y = sc_y + sc_h - font_h - 8;
            XSetForeground(dpy, gc, WhitePixel(dpy, screen));
            XDrawString(dpy, back_buf, gc, 20, vu_y + font_asc, "VU Peak:", 8);
            int num_segs = 24;
            int active_segs = (st.transport_state == 0) ? 1 : (peak * num_segs / 100);
            int seg_x0 = 110;
            int seg_w = (win_w - seg_x0 - 100) / num_segs;
            if (seg_w < 6) seg_w = 6;
            for (int s = 0; s < num_segs; s++) {
                unsigned long scol = (s < 15) ? colors.accent_green : (s < 20 ? colors.accent_amber : vu_red);
                if (s >= active_segs) scol = colors.bevel_dark;
                XSetForeground(dpy, gc, scol);
                XFillRectangle(dpy, back_buf, gc, seg_x0 + s * seg_w, vu_y + 2, (unsigned int)(seg_w - 3), (unsigned int)(font_h - 2));
            }
            char pk_str[32];
            snprintf(pk_str, sizeof(pk_str), "%d%%", peak);
            XSetForeground(dpy, gc, wave_col);
            XDrawString(dpy, back_buf, gc, seg_x0 + num_segs * seg_w + 8, vu_y + font_asc, pk_str, (int)strlen(pk_str));

            /* 3. Interactive Volume & Gain Motif Sliders */
            sld_y = sc_y + sc_h + 6;
            sld_h = font_h + 16;
            int hw = (win_w - 28) / 2;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, sld_y, hw, sld_h, colors.bg_gray, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, 18 + hw, sld_y, hw, sld_h, colors.bg_gray, 1);

            int vw_fill = (hw - 16) * st.vol_pct / 100;
            int gw_fill = (hw - 16) * st.gain_pct / 100;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 14, sld_y + 4, vw_fill > 8 ? vw_fill : 8, sld_h - 8, colors.title_bg, 0);
            draw_bevel_rect(dpy, back_buf, gc, &colors, 22 + hw, sld_y + 4, gw_fill > 8 ? gw_fill : 8, sld_h - 8, colors.title_bg, 0);

            char vstr[64], gstr[64];
            snprintf(vstr, sizeof(vstr), "Playback Volume: %d%% (Click to adjust)", st.vol_pct);
            snprintf(gstr, sizeof(gstr), "Recording Gain: %d%% (Click to adjust)", st.gain_pct);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, 22, sld_y + font_asc + 4, vstr, (int)strlen(vstr));
            XDrawString(dpy, back_buf, gc, 30 + hw, sld_y + font_asc + 4, gstr, (int)strlen(gstr));

            /* 4. Bottom Audio Clip Library Table */
            int st_h = font_h + 10;
            tbl_y = sld_y + sld_h + 6;
            tbl_h = win_h - tbl_y - st_h - 14;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, tbl_y, win_w - 20, tbl_h, colors.canvas_bg, 1);
            draw_bevel_rect(dpy, back_buf, gc, &colors, 12, tbl_y + 2, win_w - 24, font_h + 10, colors.title_bg, 0);
            XSetForeground(dpy, gc, colors.title_fg);
            XDrawString(dpy, back_buf, gc, 20, tbl_y + font_asc + 4,
                        "#   Clip Filename         Format        Sec  Peak   Voice Annotation Description", 80);

            int row_h = font_h + 8;
            int ry = tbl_y + font_h + 14;
            for (int i = 0; i < st.num_clips && ry + row_h < tbl_y + tbl_h - 4; i++) {
                int sel = (i == st.cur_clip);
                if (sel) {
                    draw_bevel_rect(dpy, back_buf, gc, &colors, 14, ry, win_w - 28, row_h - 1, colors.title_bg, 1);
                }
                char cline[200];
                snprintf(cline, sizeof(cline), "%-2d  %-20s  %-12s  %2ds  %3d%%   %s",
                         i + 1, st.clips[i].name, st.clips[i].fmt, st.clips[i].sec, st.clips[i].peak, st.clips[i].desc);
                XSetForeground(dpy, gc, sel ? colors.title_fg : colors.canvas_fg);
                XDrawString(dpy, back_buf, gc, 20, ry + font_asc + 2, cline, (int)strlen(cline));
                ry += row_h;
            }

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 4, open_menu);

            if (st.dialog_mode == 1) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows DECsound: About",
                    "DECwindows Motif DECsound V3.0 (DECW$SOUND / dxsound)",
                    "Baseboard Audio (AMD Am79C30A) 8kHz Mu-Law & PCM16 Voice Tool",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
                if (st.num_clips > 1) st.cur_clip = 1;
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
               title, cfg->app_id[0] ? cfg->app_id : "decsound", st.num_clips, 10, font_desc, info);
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
 * 11. DECwindows Session Manager (DECW$SESSION / decwx11 / dxsession)
 *     Authentic OSF/Motif 1.1 Workstation Control Panel & Application Launcher
 * ============================================================================ */

static int run_session_window(const DecwWindowConfig* cfg) {
    const char* dname = cfg->display_name[0] ? cfg->display_name : getenv("DISPLAY");
    Display* dpy = XOpenDisplay(dname);
    if (!dpy) return 1;

    int screen = DefaultScreen(dpy);
    int disp_w = DisplayWidth(dpy, screen);
    int disp_h = DisplayHeight(dpy, screen);
    int depth = DefaultDepth(dpy, screen);

    DecwColors colors;
    init_colors(dpy, screen, "decwindows", &colors);

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
    int rec_w = 1040, rec_h = 680;
    XFontStruct* font = load_scaled_font(dpy, font_scale, custom_xlfd, font_desc, sizeof(font_desc), &rec_w, &rec_h);
    int win_w = (cfg->width >= 480) ? cfg->width : (720 + font_scale * 105);
    int win_h = (cfg->height >= 360) ? cfg->height : (440 + font_scale * 70);
    if (win_w > disp_w - 80) win_w = disp_w - 80;
    if (win_h > disp_h - 80) win_h = disp_h - 80;

    Window win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen), 50, 50,
                                     (unsigned int)win_w, (unsigned int)win_h, 2, colors.bevel_dark, colors.bg_gray);
    XSetWindowBackgroundPixmap(dpy, win, None);

    const char* title = cfg->title[0] ? cfg->title : "DECwindows Session Manager - VAXcluster Node STAR::";
    XStoreName(dpy, win, title);
    XSetIconName(dpy, win, "DECW$SESSION");
    Atom wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | StructureNotifyMask);

    GC gc = XCreateGC(dpy, win, 0, NULL);
    if (font) XSetFont(dpy, gc, font->fid);

    Pixmap back_buf = XCreatePixmap(dpy, win, (unsigned int)win_w, (unsigned int)win_h, (unsigned int)depth);
    int buf_w = win_w, buf_h = win_h;

    static const char* app_ids[11] = {
        "decterm", "fileview", "dxmail", "clock",
        "calculator", "calendar", "cardfiler", "notepad",
        "bookreader", "cdaviewer", "decsound"
    };
    static const char* app_titles[11] = {
        "DECterm (VT300)",     "FileView (DCL)",    "DECwindows Mail",    "DECwindows Clock",
        "Calculator (dxcalc)", "Calendar Planner",  "Cardfiler (3x5)",    "Notepad Editor",
        "Bookreader Manual",   "CDA Viewer (DDIF)", "DECsound Audio"
    };

    static const DecwMenuItem sess_items[] = {
        {"End Session / Exit", 109}
    };
    static const DecwMenuItem app_items[] = {
        {"Launch DECterm",     200},
        {"Launch FileView",    201},
        {"Launch Mail",        202},
        {"Launch Clock",       203},
        {"Launch Calculator",  204},
        {"Launch Calendar",    205},
        {"Launch Cardfiler",   206},
        {"Launch Notepad",     207},
        {"Launch Bookreader",  208},
        {"Launch CDA Viewer",  209},
        {"Launch DECsound",    210}
    };
    static const DecwMenuItem help_items[] = {
        {"About Session Manager...", 401}
    };
    DecwMenuBarMenu menus[3] = {
        {"Session",      0, 0, 0, sess_items, 1},
        {"Applications", 0, 0, 0, app_items,  11},
        {"Help",         0, 0, 1, help_items, 1}
    };

    char dpy_info[256] = "";
    decw_x11_probe_display(dname, dpy_info, sizeof(dpy_info));
    char status_msg[220];
    snprintf(status_msg, sizeof(status_msg), "DECW$SESSION Active | Click any application tile to launch it on %s",
             dname ? dname : ":0");

    XMapWindow(dpy, win);
    XFlush(dpy);

    int autoclose_ms = cfg->autoclose_ms;
    const char* env_ac = getenv("DECW_X11_AUTOCLOSE_MS");
    if (autoclose_ms <= 0 && env_ac && env_ac[0]) autoclose_ms = atoi(env_ac);
    if (cfg->verify_only && autoclose_ms <= 0) autoclose_ms = 120;

    struct timeval start_tv;
    gettimeofday(&start_tv, NULL);
    int exposed_once = 0, need_redraw = 0, sent_synth = 0, running = 1;
    int open_menu = -1, dialog_mode = 0;
    int ok_x = 0, ok_y = 0, ok_w = 0, ok_h = 0;
    int grid_x = 12, grid_y = 90, grid_w = 680, grid_h = 220;

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

                if (dialog_mode != 0) {
                    if (mx >= ok_x && mx <= ok_x + ok_w && my >= ok_y && my <= ok_y + ok_h) dialog_mode = 0;
                    continue;
                }

                int mact = handle_motif_menubar_click(mx, my, win_w, font_h, menus, 3, &open_menu);
                if (mact != 0) {
                    if (mact == 109) running = 0;
                    else if (mact >= 200 && mact <= 210) {
                        int idx = mact - 200;
                        char cmd[256];
                        snprintf(cmd, sizeof(cmd), "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app %s --detach >/dev/null 2>&1", app_ids[idx]);
                        int rc = system(cmd);
                        (void)rc;
                        snprintf(status_msg, sizeof(status_msg), "Launched %s (%s) in detached X11 window", app_titles[idx], app_ids[idx]);
                    } else if (mact == 401) dialog_mode = 1;
                    continue;
                }

                if (mx >= grid_x && mx < grid_x + grid_w && my >= grid_y && my < grid_y + grid_h) {
                    int col = (mx - grid_x) * 4 / grid_w;
                    int row = (my - grid_y) * 3 / grid_h;
                    int idx = row * 4 + col;
                    if (idx >= 0 && idx < 11) {
                        char cmd[256];
                        snprintf(cmd, sizeof(cmd), "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app %s --detach >/dev/null 2>&1", app_ids[idx]);
                        int rc = system(cmd);
                        (void)rc;
                        snprintf(status_msg, sizeof(status_msg), "Launched %s (%s) in detached X11 window", app_titles[idx], app_ids[idx]);
                    } else if (idx == 11) {
                        running = 0;
                    }
                }
            } else if (ev.type == KeyPress) {
                KeySym ks = NoSymbol;
                char kbuf[16];
                XLookupString(&ev.xkey, kbuf, sizeof(kbuf) - 1, &ks, NULL);
                need_redraw = 1;
                if (ks == XK_Escape) running = 0;
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
                                          title, menus, 3, open_menu, &cy);

            int st_h = font_h + 10;
            int log_h = font_h * 4 + 20;
            grid_x = 10;
            grid_y = cy + 4;
            grid_w = win_w - 20;
            grid_h = win_h - grid_y - log_h - st_h - 16;

            int cw = grid_w / 4;
            int ch = grid_h / 3;
            for (int r = 0; r < 3; r++) {
                for (int c = 0; c < 4; c++) {
                    int idx = r * 4 + c;
                    int bx = grid_x + c * cw;
                    int by = grid_y + r * ch;
                    const char* lbl = (idx < 11) ? app_titles[idx] : "End Session [Quit]";
                    draw_bevel_rect(dpy, back_buf, gc, &colors, bx + 3, by + 3, cw - 6, ch - 6,
                                    (idx == 11) ? colors.bg_gray : colors.btn_bg, 0);
                    XSetForeground(dpy, gc, colors.canvas_fg);
                    XDrawString(dpy, back_buf, gc, bx + 14, by + (ch + font_asc) / 2 - 2, lbl, (int)strlen(lbl));
                }
            }

            int ly = grid_y + grid_h + 6;
            draw_bevel_rect(dpy, back_buf, gc, &colors, 10, ly, win_w - 20, log_h, colors.canvas_bg, 1);
            XSetForeground(dpy, gc, colors.title_bg);
            XDrawString(dpy, back_buf, gc, 18, ly + font_asc + 4,
                        "DECwindows Motif 1.1 Workstation Session Control (DECW$SESSION)", 63);
            XSetForeground(dpy, gc, colors.canvas_fg);
            XDrawString(dpy, back_buf, gc, 18, ly + font_h + font_asc + 8, dpy_info, (int)strlen(dpy_info));
            XDrawString(dpy, back_buf, gc, 18, ly + font_h * 2 + font_asc + 12,
                        "Click any application push-button above to launch its native X11 window.", 72);

            draw_motif_status_bar(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h, status_msg);
            draw_motif_open_dropdown(dpy, back_buf, gc, &colors, win_w, font_asc, font_h, menus, 3, open_menu);

            if (dialog_mode == 1) {
                draw_motif_about_dialog(dpy, back_buf, gc, &colors, win_w, win_h, font_asc, font_h,
                    "DECwindows Session Manager: About",
                    "DECwindows Motif Session Manager V3.0 (DECW$SESSION / dxsession)",
                    "Workstation Application Launcher & X11 Display Server Controller",
                    "Copyright (c) Digital Equipment Corporation, 1988-1993.",
                    &ok_x, &ok_y, &ok_w, &ok_h);
            }

            XCopyArea(dpy, back_buf, win, gc, 0, 0, (unsigned int)win_w, (unsigned int)win_h, 0, 0);
            XFlush(dpy);

            if (cfg->test_interact && !sent_synth) {
                sent_synth = 1;
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
               title, cfg->app_id[0] ? cfg->app_id : "decwindows", 11, 12, font_desc, info);
        fflush(stdout);
    }

    XFreePixmap(dpy, back_buf);
    if (font) XFreeFont(dpy, font);
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}

#endif /* DECW_GUI_GROUP3_H */
