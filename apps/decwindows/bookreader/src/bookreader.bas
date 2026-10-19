10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM BK_CODE$(10%) \ DIM BK_TITLE$(10%)
20 DIM TP_BOOK$(30%) \ DIM TP_SEC$(30%) \ DIM TP_TITLE$(30%) \ DIM TP_BODY$(30%) \ DIM TP_XREF$(30%)
30 DIM BM_TP%(20%) \ DIM BM_NOTE$(20%) \ DIM FLD$(10%)
40 NUM_BOOKS% = 0% \ NUM_TOPICS% = 0% \ NUM_BM% = 0% \ CUR_BOOK% = 0% \ CUR_TOPIC% = 0% \ SHELF_FILE$ = "LIBRARY.BKS"
50 BLANKS$ = "                                                                                " \ LBRK$ = "[" \ RBRK$ = "]" \ VBAR$ = "|" \ PIPE$ = "|"
60 SEP$    = "--------------------------------------------------------------------------------"
70 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
80 IF CMD_LINE$ = "" THEN GOTO 100
90 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 180
100 PRINT EQU$ \ PRINT "    DECwindows Bookreader V3.0 - XUI/Motif Online Documentation Viewer" \ PRINT "    Digital Equipment Corporation (DEC) VAX/VMS & ULTRIX Workstation Software" \ PRINT EQU$
110 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
120 PRINT "BOOKREADER> "; \ LINE INPUT RAW_INPUT$
130 IF LEN(RAW_INPUT$) = 0% THEN GOTO 3400
140 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 26% THEN GOTO 3400
150 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 0% THEN GOTO 3400
160 T_IN$ = RAW_INPUT$ \ GOSUB 500
170 IF T_OUT$ = "" THEN GOTO 120
175 SC_REM$ = T_OUT$
180 IF SC_REM$ = "" THEN GOTO 240
190 SC_P% = INSTR(1%, SC_REM$, ";")
200 IF SC_P% = 0% THEN GOTO 220
210 RAW_CMD$ = LEFT$(SC_REM$, SC_P% - 1%) \ SC_REM$ = MID$(SC_REM$, SC_P% + 1%, LEN(SC_REM$) - SC_P%) \ GOTO 230
220 RAW_CMD$ = SC_REM$ \ SC_REM$ = ""
230 GOSUB 260 \ GOTO 180
240 IF IS_BATCH% = 1% THEN GOTO 3400
250 GOTO 120
260 T_IN$ = RAW_CMD$ \ GOSUB 500 \ WORK_CMD$ = T_OUT$
270 IF WORK_CMD$ = "" THEN GOTO 495
280 SP% = INSTR(1%, WORK_CMD$, " ")
290 IF SP% = 0% THEN GOTO 310
300 VERB$ = LEFT$(WORK_CMD$, SP% - 1%) \ ARGS$ = MID$(WORK_CMD$, SP% + 1%, LEN(WORK_CMD$) - SP%) \ GOTO 320
310 VERB$ = WORK_CMD$ \ ARGS$ = ""
320 U_IN$ = VERB$ \ GOSUB 580 \ VERB$ = U_OUT$ \ T_IN$ = ARGS$ \ GOSUB 500 \ ARGS$ = T_OUT$
330 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "BYE" THEN GOTO 3400
340 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 3220
350 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 750
360 IF VERB$ = "SHELF" OR VERB$ = "BOOKS" OR VERB$ = "LIBRARY" THEN GOTO 960
370 IF VERB$ = "OPEN" OR VERB$ = "BOOK" OR VERB$ = "SELECT" THEN GOTO 1120
380 IF VERB$ = "TOC" OR VERB$ = "CONTENTS" OR VERB$ = "TOPICS" THEN GOTO 1280
390 IF VERB$ = "READ" OR VERB$ = "TOPIC" OR VERB$ = "VIEW" THEN GOTO 1460
400 IF VERB$ = "NEXT" THEN GOTO 1620
410 IF VERB$ = "PREV" OR VERB$ = "BACK" THEN GOTO 1700
420 IF VERB$ = "FOLLOW" OR VERB$ = "HOTSPOT" OR VERB$ = "XREF" OR VERB$ = "LINK" THEN GOTO 1780
430 IF VERB$ = "SEARCH" OR VERB$ = "FIND" THEN GOTO 1910
440 IF VERB$ = "BOOKMARK" OR VERB$ = "MARK" THEN GOTO 2070
450 IF VERB$ = "BOOKMARKS" OR VERB$ = "MARKS" THEN GOTO 2190
460 IF VERB$ = "ADDBOOK" THEN GOTO 2310
470 IF VERB$ = "ADDTOPIC" THEN GOTO 2420
475 IF VERB$ = "DELTOPIC" OR VERB$ = "DELETE" THEN GOTO 2540
480 IF VERB$ = "DISPLAY" OR VERB$ = "SCREEN" OR VERB$ = "RENDER" OR VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 2640
484 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2940
486 IF VERB$ = "SAVE" THEN GOTO 3040
488 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3120
490 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3200
494 PRINT "BOOKREADER: Unknown command '"; VERB$; "'. Type HELP for syntax."
495 RETURN
500 T_OUT$ = T_IN$
510 IF LEN(T_OUT$) = 0% THEN GOTO 570
520 IF LEFT$(T_OUT$, 1%) = " " THEN T_OUT$ = MID$(T_OUT$, 2%, LEN(T_OUT$) - 1%)
530 IF LEFT$(T_OUT$, 1%) = " " THEN GOTO 510
540 IF LEN(T_OUT$) = 0% THEN GOTO 570
550 IF MID$(T_OUT$, LEN(T_OUT$), 1%) = " " THEN T_OUT$ = LEFT$(T_OUT$, LEN(T_OUT$) - 1%)
560 IF MID$(T_OUT$, LEN(T_OUT$), 1%) = " " THEN GOTO 540
570 RETURN
580 U_OUT$ = "" \ UJ% = 1%
590 IF UJ% > LEN(U_IN$) THEN GOTO 630
600 UCH$ = MID$(U_IN$, UJ%, 1%) \ UA% = ASCII(UCH$)
610 IF UA% >= 97% AND UA% <= 122% THEN UCH$ = CHR$(UA% - 32%)
620 U_OUT$ = U_OUT$ + UCH$ \ UJ% = UJ% + 1% \ GOTO 590
630 RETURN
635 T_IN$ = Q_IN$ \ GOSUB 500 \ Q_OUT$ = T_OUT$ \ QCH$ = CHR$(34%) \ QL% = LEN(Q_OUT$)
638 IF QL% < 2% THEN GOTO 646
640 IF LEFT$(Q_OUT$, 1%) <> QCH$ THEN GOTO 646
642 IF MID$(Q_OUT$, QL%, 1%) = QCH$ THEN Q_OUT$ = MID$(Q_OUT$, 2%, QL% - 2%)
646 RETURN
650 NF% = 0% \ P_REM$ = P_IN$
655 IF NF% >= 9% THEN GOTO 690
660 PP% = INSTR(1%, P_REM$, PIPE$)
665 IF PP% = 0% THEN GOTO 680
670 NF% = NF% + 1% \ T_IN$ = LEFT$(P_REM$, PP% - 1%) \ GOSUB 500 \ FLD$(NF%) = T_OUT$
675 P_REM$ = MID$(P_REM$, PP% + 1%, LEN(P_REM$) - PP%) \ GOTO 655
680 NF% = NF% + 1% \ T_IN$ = P_REM$ \ GOSUB 500 \ FLD$(NF%) = T_OUT$
690 RETURN
750 NUM_BOOKS% = 3% \ NUM_TOPICS% = 6% \ NUM_BM% = 2% \ CUR_BOOK% = 1% \ CUR_TOPIC% = 1%
760 BK_CODE$(1%) = "VMS_DCL"     \ BK_TITLE$(1%) = "VAX/VMS DCL Dictionary (DECW$BOOK)"
770 BK_CODE$(2%) = "DECWIN_USER" \ BK_TITLE$(2%) = "DECwindows Desktop User's Guide (DECW$BOOK)"
780 BK_CODE$(3%) = "BP2_REF"     \ BK_TITLE$(3%) = "PDP-11 & VAX BASIC-PLUS-2 Reference Manual"
790 TP_BOOK$(1%) = "VMS_DCL" \ TP_SEC$(1%) = "1.1" \ TP_TITLE$(1%) = "Overview of Digital Command Language"
800 TP_BODY$(1%) = "DCL provides interactive and batch command control across VAX/VMS nodes." \ TP_XREF$(1%) = "1.2"
810 TP_BOOK$(2%) = "VMS_DCL" \ TP_SEC$(2%) = "1.2" \ TP_TITLE$(2%) = "SET TERMINAL Command Qualifiers"
820 TP_BODY$(2%) = "Use SET TERMINAL /INQUIRE /DEVICE=VT300 to configure DECterm sessions." \ TP_XREF$(2%) = "2.1"
830 TP_BOOK$(3%) = "DECWIN_USER" \ TP_SEC$(3%) = "2.1" \ TP_TITLE$(3%) = "Using the DECwindows Session Manager"
840 TP_BODY$(3%) = "Session Manager launches DECterm, Bookreader, FileView, and Mail." \ TP_XREF$(3%) = "2.2"
850 TP_BOOK$(4%) = "DECWIN_USER" \ TP_SEC$(4%) = "2.2" \ TP_TITLE$(4%) = "Navigating Hypertext Bookshelves"
860 TP_BODY$(4%) = "Double-click any book icon in LIBRARY.DECW$BOOKSHELF or click Hotspots." \ TP_XREF$(4%) = "3.1"
870 TP_BOOK$(5%) = "BP2_REF" \ TP_SEC$(5%) = "3.1" \ TP_TITLE$(5%) = "RMS Indexed and Sequential File I/O"
880 TP_BODY$(5%) = "OPEN file FOR INPUT or OUTPUT with MAP buffers and primary keys." \ TP_XREF$(5%) = "3.2"
890 TP_BOOK$(6%) = "BP2_REF" \ TP_SEC$(6%) = "3.2" \ TP_TITLE$(6%) = "Task-Builder and Overlay Compilation"
900 TP_BODY$(6%) = "Compile BASIC-PLUS-2 modules with basicc and link with basiclink." \ TP_XREF$(6%) = "1.1"
910 BM_TP%(1%) = 2% \ BM_NOTE$(1%) = "VT300 terminal setup reference"
920 BM_TP%(2%) = 5% \ BM_NOTE$(2%) = "RMS file organization syntax"
930 PRINT "[Sample DECwindows Bookshelf loaded: 3 books, 6 hypertext topics, 2 bookmarks]" \ GOTO 495
960 IF NUM_BOOKS% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  DECwindows Bookreader Library Bookshelf (LIBRARY.DECW$BOOKSHELF)" \ PRINT EQU$
980 PRINT "ID   Book Symbol    Topics   Book Title (.DECW$BOOK)" \ PRINT SEP$
990 BI% = 1%
1000 IF BI% > NUM_BOOKS% THEN GOTO 1100
1010 CNT_T% = 0% \ TI% = 1%
1020 IF TI% > NUM_TOPICS% THEN GOTO 1050
1030 IF TP_BOOK$(TI%) = BK_CODE$(BI%) THEN CNT_T% = CNT_T% + 1%
1040 TI% = TI% + 1% \ GOTO 1020
1050 B_S$ = STR$(BI%) \ T_IN$ = B_S$ \ GOSUB 500 \ B_P$ = LEFT$(T_OUT$ + BLANKS$, 5%)
1060 C_P$ = LEFT$(BK_CODE$(BI%) + BLANKS$, 15%)
1070 N_S$ = STR$(CNT_T%) \ T_IN$ = N_S$ \ GOSUB 500 \ N_P$ = LEFT$(T_OUT$ + BLANKS$, 9%)
1080 PRINT B_P$; C_P$; N_P$; BK_TITLE$(BI%)
1090 BI% = BI% + 1% \ GOTO 1000
1100 PRINT EQU$ \ GOTO 495
1120 IF NUM_BOOKS% = 0% THEN GOTO 3370
1130 IF ARGS$ = "" THEN GOTO 1260
1140 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ O_ARG$ = U_OUT$
1150 FOUND_B% = 0% \ BV% = VAL(O_ARG$)
1160 IF BV% >= 1% AND BV% <= NUM_BOOKS% THEN FOUND_B% = BV%
1170 IF FOUND_B% > 0% THEN GOTO 1210
1180 BI% = 1%
1190 IF BI% > NUM_BOOKS% THEN GOTO 1210
1200 IF BK_CODE$(BI%) = O_ARG$ THEN FOUND_B% = BI%
1205 BI% = BI% + 1% \ GOTO 1190
1210 IF FOUND_B% = 0% THEN GOTO 1270
1220 CUR_BOOK% = FOUND_B% \ FIRST_T% = 0% \ TI% = 1%
1230 IF TI% > NUM_TOPICS% THEN GOTO 1252
1240 IF TP_BOOK$(TI%) = BK_CODE$(CUR_BOOK%) AND FIRST_T% = 0% THEN FIRST_T% = TI%
1250 TI% = TI% + 1% \ GOTO 1230
1252 IF FIRST_T% > 0% THEN CUR_TOPIC% = FIRST_T%
1255 PRINT "[Opened Book #"; CUR_BOOK%; ": "; BK_TITLE$(CUR_BOOK%); " ("; BK_CODE$(CUR_BOOK%); ")]" \ GOTO 495
1260 PRINT "BOOKREADER: Syntax is OPEN <book_id_or_code>" \ GOTO 495
1270 PRINT "BOOKREADER: Book '"; O_ARG$; "' not found on bookshelf." \ GOTO 495
1280 IF NUM_TOPICS% = 0% THEN GOTO 3370
1290 U_IN$ = ARGS$ \ GOSUB 580 \ T_FLT$ = U_OUT$
1300 SHOW_ALL% = 0%
1310 IF T_FLT$ = "ALL" OR CUR_BOOK% = 0% THEN SHOW_ALL% = 1%
1320 PRINT EQU$
1330 IF SHOW_ALL% = 1% THEN PRINT "  DECwindows Bookreader Table of Contents - All Books"
1340 IF SHOW_ALL% = 0% THEN PRINT "  DECwindows Bookreader Table of Contents - "; BK_TITLE$(CUR_BOOK%)
1350 PRINT EQU$ \ PRINT "Top#  Book         Sec    Hotspot  Topic Title" \ PRINT SEP$
1360 TI% = 1%
1370 IF TI% > NUM_TOPICS% THEN GOTO 1440
1380 IF SHOW_ALL% = 0% AND TP_BOOK$(TI%) <> BK_CODE$(CUR_BOOK%) THEN GOTO 1430
1390 T_S$ = STR$(TI%) \ T_IN$ = T_S$ \ GOSUB 500 \ T_P$ = LEFT$(T_OUT$ + BLANKS$, 6%)
1400 B_P$ = LEFT$(TP_BOOK$(TI%) + BLANKS$, 13%) \ S_P$ = LEFT$(TP_SEC$(TI%) + BLANKS$, 7%)
1410 X_P$ = LEFT$(TP_XREF$(TI%) + BLANKS$, 9%)
1420 PRINT T_P$; B_P$; S_P$; X_P$; TP_TITLE$(TI%)
1430 TI% = TI% + 1% \ GOTO 1370
1440 PRINT EQU$ \ GOTO 495
1460 IF NUM_TOPICS% = 0% THEN GOTO 3370
1470 IF ARGS$ = "" THEN GOTO 1560
1480 Q_IN$ = ARGS$ \ GOSUB 635 \ R_ARG$ = Q_OUT$ \ FOUND_T% = 0% \ TV% = VAL(R_ARG$)
1490 IF INSTR(1%, R_ARG$, ".") > 0% THEN TV% = 0%
1500 IF TV% >= 1% AND TV% <= NUM_TOPICS% THEN FOUND_T% = TV%
1510 IF FOUND_T% > 0% THEN GOTO 1550
1520 TI% = 1%
1530 IF TI% > NUM_TOPICS% THEN GOTO 1550
1540 IF TP_SEC$(TI%) = R_ARG$ THEN FOUND_T% = TI%
1545 TI% = TI% + 1% \ GOTO 1530
1550 IF FOUND_T% = 0% THEN GOTO 1600
1555 CUR_TOPIC% = FOUND_T%
1560 IF CUR_TOPIC% < 1% OR CUR_TOPIC% > NUM_TOPICS% THEN GOTO 1600
1565 BI% = 1%
1570 IF BI% > NUM_BOOKS% THEN GOTO 1585
1575 IF BK_CODE$(BI%) = TP_BOOK$(CUR_TOPIC%) THEN CUR_BOOK% = BI%
1580 BI% = BI% + 1% \ GOTO 1570
1585 PRINT EQU$ \ PRINT "  [Topic #"; CUR_TOPIC%; " | "; TP_BOOK$(CUR_TOPIC%); " Sec "; TP_SEC$(CUR_TOPIC%); "] "; TP_TITLE$(CUR_TOPIC%) \ PRINT SEP$
1590 PRINT "  "; TP_BODY$(CUR_TOPIC%)
1595 PRINT "  [Hotspot Cross-Reference -> Section "; TP_XREF$(CUR_TOPIC%); "]" \ PRINT EQU$ \ GOTO 495
1600 PRINT "BOOKREADER: Topic '"; ARGS$; "' not found." \ GOTO 495
1620 IF NUM_TOPICS% = 0% THEN GOTO 3370
1630 IF CUR_TOPIC% >= NUM_TOPICS% THEN GOTO 1670
1640 CUR_TOPIC% = CUR_TOPIC% + 1% \ ARGS$ = "" \ GOTO 1560
1670 PRINT "BOOKREADER: Already at last topic (#"; NUM_TOPICS%; ")." \ GOTO 495
1700 IF NUM_TOPICS% = 0% THEN GOTO 3370
1710 IF CUR_TOPIC% <= 1% THEN GOTO 1750
1720 CUR_TOPIC% = CUR_TOPIC% - 1% \ ARGS$ = "" \ GOTO 1560
1750 PRINT "BOOKREADER: Already at first topic (#1)." \ GOTO 495
1780 IF NUM_TOPICS% = 0% THEN GOTO 3370
1790 IF CUR_TOPIC% < 1% OR CUR_TOPIC% > NUM_TOPICS% THEN GOTO 3370
1800 X_SEC$ = TP_XREF$(CUR_TOPIC%)
1810 IF X_SEC$ = "" OR X_SEC$ = "-" THEN GOTO 1880
1820 FOUND_X% = 0% \ TI% = 1%
1830 IF TI% > NUM_TOPICS% THEN GOTO 1860
1840 IF TP_SEC$(TI%) = X_SEC$ THEN FOUND_X% = TI%
1850 TI% = TI% + 1% \ GOTO 1830
1860 IF FOUND_X% = 0% THEN GOTO 1880
1870 CUR_TOPIC% = FOUND_X% \ PRINT "[Followed Hotspot Link -> Section "; X_SEC$; " (Topic #"; CUR_TOPIC%; ")]" \ ARGS$ = "" \ GOTO 1560
1880 PRINT "BOOKREADER: Hotspot target '"; X_SEC$; "' not found." \ GOTO 495
1910 IF NUM_TOPICS% = 0% THEN GOTO 3370
1920 IF ARGS$ = "" THEN GOTO 2050
1930 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ KW$ = U_OUT$
1940 PRINT EQU$ \ PRINT "  DECwindows Bookreader Full-Text Search Results for '"; Q_OUT$; "'" \ PRINT SEP$
1950 S_HIT% = 0% \ TI% = 1%
1960 IF TI% > NUM_TOPICS% THEN GOTO 2030
1970 U_IN$ = TP_TITLE$(TI%) + " " + TP_BODY$(TI%) \ GOSUB 580 \ HAY$ = U_OUT$
1980 IF INSTR(1%, HAY$, KW$) = 0% THEN GOTO 2020
1990 S_HIT% = S_HIT% + 1%
2000 PRINT "  [Match #"; S_HIT%; "] Topic #"; TI%; " ("; TP_BOOK$(TI%); " "; TP_SEC$(TI%); "): "; TP_TITLE$(TI%)
2020 TI% = TI% + 1% \ GOTO 1960
2030 PRINT SEP$ \ PRINT "  Total matching topics: "; S_HIT% \ PRINT EQU$ \ GOTO 495
2050 PRINT "BOOKREADER: Syntax is SEARCH <keyword>" \ GOTO 495
2070 IF NUM_TOPICS% = 0% THEN GOTO 3370
2080 IF NUM_BM% >= 20% THEN GOTO 2170
2090 NOTE_TXT$ = "Bookmark on Section " + TP_SEC$(CUR_TOPIC%)
2100 IF ARGS$ = "" THEN GOTO 2120
2110 Q_IN$ = ARGS$ \ GOSUB 635 \ NOTE_TXT$ = Q_OUT$
2120 NUM_BM% = NUM_BM% + 1% \ BM_TP%(NUM_BM%) = CUR_TOPIC% \ BM_NOTE$(NUM_BM%) = NOTE_TXT$
2130 PRINT "[Bookmark #"; NUM_BM%; " saved for Topic #"; CUR_TOPIC%; " ("; TP_SEC$(CUR_TOPIC%); "): "; NOTE_TXT$; "]" \ GOTO 495
2170 PRINT "BOOKREADER: Bookmark list full (maximum 20 bookmarks)." \ GOTO 495
2190 IF NUM_BM% = 0% THEN GOTO 2290
2200 PRINT EQU$ \ PRINT "  DECwindows Bookreader Saved Bookmarks ("; NUM_BM%; ")" \ PRINT EQU$
2210 PRINT "BM#   Topic#  Book         Sec     Bookmark Note" \ PRINT SEP$
2220 MI% = 1%
2230 IF MI% > NUM_BM% THEN GOTO 2280
2240 T_ID% = BM_TP%(MI%) \ M_S$ = STR$(MI%) \ T_IN$ = M_S$ \ GOSUB 500 \ M_P$ = LEFT$(T_OUT$ + BLANKS$, 6%)
2250 TP_S$ = STR$(T_ID%) \ T_IN$ = TP_S$ \ GOSUB 500 \ TP_P$ = LEFT$(T_OUT$ + BLANKS$, 8%)
2260 BK_P$ = LEFT$(TP_BOOK$(T_ID%) + BLANKS$, 13%) \ SC_P$ = LEFT$(TP_SEC$(T_ID%) + BLANKS$, 8%)
2270 PRINT M_P$; TP_P$; BK_P$; SC_P$; BM_NOTE$(MI%) \ MI% = MI% + 1% \ GOTO 2230
2280 PRINT EQU$ \ GOTO 495
2290 PRINT "BOOKREADER: No bookmarks saved." \ GOTO 495
2310 IF NUM_BOOKS% >= 10% THEN GOTO 2400
2320 P_IN$ = ARGS$ \ GOSUB 650
2330 IF NF% < 2% THEN GOTO 2390
2340 U_IN$ = FLD$(1%) \ GOSUB 580 \ NB_CODE$ = U_OUT$ \ NB_TITLE$ = FLD$(2%)
2350 NUM_BOOKS% = NUM_BOOKS% + 1% \ BK_CODE$(NUM_BOOKS%) = NB_CODE$ \ BK_TITLE$(NUM_BOOKS%) = NB_TITLE$ \ CUR_BOOK% = NUM_BOOKS%
2360 PRINT "[Added Book #"; NUM_BOOKS%; ": "; NB_CODE$; " - "; NB_TITLE$; "]" \ GOTO 495
2390 PRINT "BOOKREADER: Syntax is ADDBOOK <code|title>" \ GOTO 495
2400 PRINT "BOOKREADER: Bookshelf is full (maximum 10 books)." \ GOTO 495
2420 IF NUM_TOPICS% >= 30% THEN GOTO 2520
2430 IF CUR_BOOK% = 0% THEN GOTO 3370
2440 P_IN$ = ARGS$ \ GOSUB 650
2450 IF NF% < 3% THEN GOTO 2510
2460 NT_SEC$ = FLD$(1%) \ NT_TITLE$ = FLD$(2%) \ NT_BODY$ = FLD$(3%) \ NT_XREF$ = "-"
2470 IF NF% >= 4% THEN NT_XREF$ = FLD$(4%)
2480 NUM_TOPICS% = NUM_TOPICS% + 1% \ TP_BOOK$(NUM_TOPICS%) = BK_CODE$(CUR_BOOK%) \ TP_SEC$(NUM_TOPICS%) = NT_SEC$
2490 TP_TITLE$(NUM_TOPICS%) = NT_TITLE$ \ TP_BODY$(NUM_TOPICS%) = NT_BODY$ \ TP_XREF$(NUM_TOPICS%) = NT_XREF$ \ CUR_TOPIC% = NUM_TOPICS%
2500 PRINT "[Added Topic #"; NUM_TOPICS%; " ("; NT_SEC$; "): "; NT_TITLE$; "]" \ GOTO 495
2510 PRINT "BOOKREADER: Syntax is ADDTOPIC <sec|title|body|xref>" \ GOTO 495
2520 PRINT "BOOKREADER: Topic table full (maximum 30 topics)." \ GOTO 495
2540 IF NUM_TOPICS% = 0% THEN GOTO 3370
2550 D_ID% = VAL(ARGS$)
2560 IF D_ID% < 1% OR D_ID% > NUM_TOPICS% THEN GOTO 3380
2570 D_TIT$ = TP_TITLE$(D_ID%) \ DI% = D_ID%
2580 IF DI% >= NUM_TOPICS% THEN GOTO 2610
2590 TP_BOOK$(DI%) = TP_BOOK$(DI% + 1%) \ TP_SEC$(DI%) = TP_SEC$(DI% + 1%) \ TP_TITLE$(DI%) = TP_TITLE$(DI% + 1%)
2600 TP_BODY$(DI%) = TP_BODY$(DI% + 1%) \ TP_XREF$(DI%) = TP_XREF$(DI% + 1%) \ DI% = DI% + 1% \ GOTO 2580
2610 NUM_TOPICS% = NUM_TOPICS% - 1%
2620 IF CUR_TOPIC% > NUM_TOPICS% THEN CUR_TOPIC% = NUM_TOPICS%
2630 PRINT "[Deleted Topic #"; D_ID%; ": "; D_TIT$; "]" \ GOTO 495
2640 IF NUM_TOPICS% = 0% THEN GOTO 3370
2650 TO_FILE% = 0% \ OUT_FILE$ = ""
2660 IF ARGS$ = "" THEN GOTO 2720
2670 U_IN$ = ARGS$ \ GOSUB 580 \ U_ARGS$ = U_OUT$
2680 IF LEFT$(U_ARGS$, 3%) <> "ON " THEN GOTO 2710
2690 T_IN$ = MID$(ARGS$, 4%, LEN(ARGS$) - 3%) \ GOSUB 500 \ Q_IN$ = T_OUT$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1% \ GOTO 2720
2710 Q_IN$ = ARGS$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1%
2720 IF TO_FILE% = 1% THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2730 BDR$ = "+------------------------------------------------------------------------------+" \ SP1$ = " "
2740 T_BAR$ = VBAR$ + " [=] DECwindows Bookreader - " + BK_TITLE$(CUR_BOOK%) + BLANKS$
2750 T_BAR$ = LEFT$(T_BAR$, 72%) + " [v][^]" + VBAR$
2760 M_BAR$ = VBAR$ + "  File    View    Search    Bookmark    Link    Options    Help               " + VBAR$
2770 SEC_HDR$ = " Section " + TP_SEC$(CUR_TOPIC%)
2775 SEC_HDR$ = SEC_HDR$ + " - " + TP_TITLE$(CUR_TOPIC%)
2780 S_ROW$ = LEFT$(VBAR$ + SEC_HDR$ + BLANKS$, 79%) + VBAR$
2790 B_ROW$ = LEFT$(VBAR$ + "   " + TP_BODY$(CUR_TOPIC%) + BLANKS$, 79%) + VBAR$
2800 X_INF$ = " [Hotspot Link -> Section " + TP_XREF$(CUR_TOPIC%) + RBRK$
2810 X_ROW$ = LEFT$(VBAR$ + X_INF$ + BLANKS$, 79%) + VBAR$
2820 F_INF$ = " [<< Prev Topic]  [Next Topic >>]  [Book: " + BK_CODE$(CUR_BOOK%) + RBRK$
2830 F_ROW$ = LEFT$(VBAR$ + F_INF$ + BLANKS$, 79%) + VBAR$
2840 IF TO_FILE% = 1% THEN GOTO 2870
2850 PRINT BDR$ \ PRINT T_BAR$ \ PRINT BDR$ \ PRINT M_BAR$ \ PRINT BDR$
2860 PRINT S_ROW$ \ PRINT BDR$ \ PRINT B_ROW$ \ PRINT X_ROW$ \ PRINT BDR$ \ PRINT F_ROW$ \ PRINT BDR$ \ GOTO 2910
2870 PRINT #2%, BDR$ \ PRINT #2%, T_BAR$ \ PRINT #2%, BDR$ \ PRINT #2%, M_BAR$ \ PRINT #2%, BDR$
2880 PRINT #2%, S_ROW$ \ PRINT #2%, BDR$ \ PRINT #2%, B_ROW$ \ PRINT #2%, X_ROW$ \ PRINT #2%, BDR$ \ PRINT #2%, F_ROW$ \ PRINT #2%, BDR$ \ CLOSE #2%
2890 PRINT "[Bookreader topic window exported to "; OUT_FILE$; "]"
2910 GOTO 495
2940 PRINT EQU$ \ PRINT "  DECwindows Bookreader V3.0 - Library & Viewer Status" \ PRINT SEP$
2950 PRINT "  Active Bookshelf File:  "; SHELF_FILE$
2960 PRINT "  Total Books on Shelf:   "; NUM_BOOKS%
2970 PRINT "  Total Hypertext Topics: "; NUM_TOPICS%
2980 PRINT "  Saved Reader Bookmarks: "; NUM_BM%
2990 IF CUR_BOOK% > 0% THEN PRINT "  Current Open Book:      "; BK_CODE$(CUR_BOOK%); " ("; BK_TITLE$(CUR_BOOK%); ")"
3000 IF CUR_TOPIC% > 0% THEN PRINT "  Current Active Topic:   #"; CUR_TOPIC%; " ["; TP_SEC$(CUR_TOPIC%); "] "; TP_TITLE$(CUR_TOPIC%)
3010 PRINT EQU$ \ GOTO 495
3040 IF NUM_TOPICS% = 0% THEN GOTO 3370
3050 IF ARGS$ = "" THEN GOTO 3060
3055 Q_IN$ = ARGS$ \ GOSUB 635 \ SHELF_FILE$ = Q_OUT$
3060 OPEN SHELF_FILE$ FOR OUTPUT AS FILE #1%
3065 BI% = 1%
3070 IF BI% > NUM_BOOKS% THEN GOTO 3085
3075 B_REC$ = "B" + PIPE$ + BK_CODE$(BI%) + PIPE$ + BK_TITLE$(BI%) \ PRINT #1%, B_REC$
3080 BI% = BI% + 1% \ GOTO 3070
3085 TI% = 1%
3090 IF TI% > NUM_TOPICS% THEN GOTO 3110
3095 T_REC$ = "T" + PIPE$ + TP_BOOK$(TI%) + PIPE$ + TP_SEC$(TI%) + PIPE$ + TP_TITLE$(TI%) + PIPE$ + TP_BODY$(TI%) + PIPE$ + TP_XREF$(TI%)
3100 PRINT #1%, T_REC$ \ TI% = TI% + 1% \ GOTO 3090
3110 CLOSE #1% \ PRINT "[Saved "; NUM_BOOKS%; " book(s) and "; NUM_TOPICS%; " topic(s) to "; SHELF_FILE$; "]" \ GOTO 495
3120 IF ARGS$ = "" THEN GOTO 3190
3125 Q_IN$ = ARGS$ \ GOSUB 635 \ SHELF_FILE$ = Q_OUT$
3130 NUM_BOOKS% = 0% \ NUM_TOPICS% = 0% \ NUM_BM% = 0% \ OPEN SHELF_FILE$ FOR INPUT AS FILE #1%
3135 LINE INPUT #1%, IN_L$
3140 IF LEN(IN_L$) = 0% THEN GOTO 3180
3145 IF ASCII(LEFT$(IN_L$, 1%)) = 0% THEN GOTO 3180
3150 P_IN$ = IN_L$ \ GOSUB 650
3155 IF FLD$(1%) <> "B" THEN GOTO 3165
3160 NUM_BOOKS% = NUM_BOOKS% + 1% \ BK_CODE$(NUM_BOOKS%) = FLD$(2%) \ BK_TITLE$(NUM_BOOKS%) = FLD$(3%) \ GOTO 3135
3165 IF FLD$(1%) <> "T" THEN GOTO 3135
3170 NUM_TOPICS% = NUM_TOPICS% + 1% \ TP_BOOK$(NUM_TOPICS%) = FLD$(2%) \ TP_SEC$(NUM_TOPICS%) = FLD$(3%)
3175 TP_TITLE$(NUM_TOPICS%) = FLD$(4%) \ TP_BODY$(NUM_TOPICS%) = FLD$(5%) \ TP_XREF$(NUM_TOPICS%) = FLD$(6%) \ GOTO 3135
3180 CLOSE #1%
3182 IF NUM_BOOKS% > 0% THEN CUR_BOOK% = 1%
3184 IF NUM_TOPICS% > 0% THEN CUR_TOPIC% = 1%
3186 PRINT "[Loaded "; NUM_BOOKS%; " book(s) and "; NUM_TOPICS%; " topic(s) from "; SHELF_FILE$; "]" \ GOTO 495
3190 PRINT "BOOKREADER: Syntax is LOAD <filename>" \ GOTO 495
3200 NUM_BOOKS% = 0% \ NUM_TOPICS% = 0% \ NUM_BM% = 0% \ CUR_BOOK% = 0% \ CUR_TOPIC% = 0%
3210 PRINT "[Bookshelf, topics, and bookmarks cleared]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "  DECwindows Bookreader Online Documentation Commands" \ PRINT SEP$
3230 PRINT "  SAMPLE                   Load sample DECwindows Bookshelf & 3 manuals"
3240 PRINT "  SHELF / BOOKS            List all books on the active bookshelf"
3250 PRINT "  OPEN <id_or_code>        Open a book from the bookshelf"
3260 PRINT "  TOC [ALL]                Display Table of Contents for active or all books"
3270 PRINT "  READ <id_or_sec>         Display a specific documentation topic"
3280 PRINT "  NEXT / PREV              Navigate to next or previous hypertext topic"
3290 PRINT "  FOLLOW / HOTSPOT         Follow hypertext cross-reference link in topic"
3300 PRINT "  SEARCH <keyword>         Full-text search across all books and topics"
3310 PRINT "  BOOKMARK [note] / MARKS  Save a bookmark on current topic or list bookmarks"
3320 PRINT "  ADDBOOK <code|title>     Add a new book to the active bookshelf"
3330 PRINT "  ADDTOPIC <s|t|b|xref>    Add a new hypertext topic to the open book"
3340 PRINT "  DELTOPIC <id>            Delete topic #<id> from the library"
3350 PRINT "  DISPLAY [ON <file>]      Render Motif/XUI Bookreader window (or export)"
3360 PRINT "  SHOW / SAVE <f> / LOAD <f> / CLEAR / EXIT" \ PRINT EQU$ \ GOTO 495
3370 PRINT "BOOKREADER: Library is empty. Use SAMPLE, ADDBOOK, or LOAD first." \ GOTO 495
3380 PRINT "BOOKREADER: Invalid topic number." \ GOTO 495
3400 END
