10 REM =========================================================================
20 REM DECwindows Notepad V3.0 (DECW$NOTEPAD / notepad / dxnotepad)
30 REM Workstation Desktop Text Editor, X11 Clipboard & Search/Replace Manager
40 REM Digital Equipment Corporation - VAX/VMS, ULTRIX & DEC OSF/1 (1988-1993)
50 REM =========================================================================
60 DIM NP_LINE$(80%) \ DIM CLIP_BUF$(40%) \ DIM TMP_BUF$(80%)
70 DIM CMD_Q$(30%) \ DIM FLD_P$(10%)
90 PIPE$ = "|" \ COLON$ = ":" \ LBRK$ = "[" \ RBRK$ = "]" \ SP1$ = " "
100 LINE_CNT% = 0% \ CUR_LN% = 0% \ CLIP_CNT% = 0% \ WRAP_COL% = 72%
110 MOD_FLAG% = 0% \ RO_FLAG% = 0% \ DOC_NAME$ = "SYS$LOGIN:UNTITLED.TXT"
120 PRT_CH% = 0% \ BANNER_SHOWN% = 0% \ CMD_LINE$ = COMMAND$
130 IF LEN(CMD_LINE$) > 0% THEN GOTO 240
150 PRINT "=============================================================================="
160 PRINT " DECwindows Notepad V3.0 (DECW$NOTEPAD - Motif Text & Clipboard Editor)"
170 PRINT " Digital Equipment Corporation - VAX/VMS & DEC OSF/1 Workstation Desktop"
180 PRINT "=============================================================================="
190 PRINT "Type HELP for commands, SAMPLE to load 1991 AXP engineering notes, EXIT to quit."
200 BANNER_SHOWN% = 1%
210 PRINT ""
220 LINE INPUT "Notepad> "; RAW_LINE$
230 IF LEN(RAW_LINE$) = 0% THEN GOTO 210
240 IF BANNER_SHOWN% = 0% THEN RAW_LINE$ = CMD_LINE$
250 GOSUB 3310 \ Q_IDX% = 1%
270 IF Q_IDX% > Q_CNT% THEN GOTO 320
280 ONE_CMD$ = CMD_Q$( Q_IDX% ) \ GOSUB 350 \ Q_IDX% = Q_IDX% + 1% \ GOTO 270
320 IF BANNER_SHOWN% = 0% THEN GOTO 4500
330 GOTO 210
350 C_STR$ = ONE_CMD$ \ GOSUB 3520
370 IF LEN(C_STR$) = 0% THEN GOTO 1040
380 SP_POS% = INSTR(1%, C_STR$, " ")
390 IF SP_POS% = 0% THEN VERB$ = C_STR$
400 IF SP_POS% = 0% THEN ARG$ = ""
410 IF SP_POS% > 0% THEN VERB$ = LEFT$(C_STR$, SP_POS% - 1%)
420 IF SP_POS% > 0% THEN ARG$ = MID$(C_STR$, SP_POS% + 1%, LEN(C_STR$))
430 U_IN$ = VERB$ \ GOSUB 3620 \ VERB$ = U_OUT$
440 C_STR$ = ARG$ \ GOSUB 3520 \ ARG$ = C_STR$
450 U_IN$ = ARG$ \ GOSUB 3620 \ UARG$ = U_OUT$
460 IF VERB$ = "EXIT" OR VERB$ = "QUIT" THEN GOTO 4500
470 IF VERB$ = "HELP" THEN GOTO 1050
480 IF VERB$ = "SAMPLE" THEN GOTO 1270
490 IF VERB$ = "SHOW" OR VERB$ = "STATUS" OR VERB$ = "STATS" THEN GOTO 1400
500 IF VERB$ = "LIST" OR VERB$ = "VIEW" OR VERB$ = "READ" OR VERB$ = "TYPE" THEN GOTO 1600
510 IF VERB$ = "APPEND" OR VERB$ = "ADD" THEN GOTO 1720
520 IF VERB$ = "INSERT" THEN GOTO 1820
530 IF VERB$ = "EDIT" OR VERB$ = "SETLINE" THEN GOTO 1980
540 IF VERB$ = "DELETE" OR VERB$ = "DELLINE" THEN GOTO 2100
550 IF VERB$ = "COPY" THEN GOTO 2280
560 IF VERB$ = "CUT" THEN GOTO 2440
570 IF VERB$ = "PASTE" THEN GOTO 2530
580 IF VERB$ = "CLIPBOARD" THEN GOTO 2710
590 IF VERB$ = "FIND" OR VERB$ = "SEARCH" THEN GOTO 2790
600 IF VERB$ = "REPLACE" OR VERB$ = "SUBSTITUTE" THEN GOTO 2920
610 IF VERB$ = "WRAP" THEN GOTO 3120
620 IF VERB$ = "READONLY" THEN GOTO 3240
630 IF VERB$ = "DISPLAY" OR VERB$ = "RENDER" THEN GOTO 4130
640 IF VERB$ = "EXPORT" THEN GOTO 4150
650 IF VERB$ = "PRINT" THEN GOTO 4120
660 IF VERB$ = "SAVE" THEN GOTO 4320
670 IF VERB$ = "LOAD" THEN GOTO 4400
680 IF VERB$ = "CLEAR" OR VERB$ = "NEW" THEN GOTO 1230
720 PRINT "%NOTEPAD-E-INVCMD, unrecognized command: "; VERB$
1040 RETURN
1050 PRINT "--- DECwindows Notepad V3.0 (DECW$NOTEPAD) Commands ---"
1070 PRINT "  SAMPLE                        Load 1991 Alpha AXP & Motif 1.1 release notes"
1080 PRINT "  LIST / VIEW / TYPE            Display all lines in document buffer"
1090 PRINT "  APPEND <text>                 Append a new line to end of document"
1100 PRINT "  INSERT <n>|<text>             Insert a new line before line #n"
1110 PRINT "  EDIT <n>|<text>               Replace text of line #n"
1120 PRINT "  DELETE <start> [end]          Delete line or inclusive range of lines"
1130 PRINT "  COPY <start> [end]            Copy line(s) to DECwindows Clipboard"
1140 PRINT "  CUT <start> [end]             Cut line(s) to DECwindows Clipboard"
1150 PRINT "  PASTE [after_line]            Paste Clipboard lines into document"
1160 PRINT "  CLIPBOARD                     Inspect DECwindows Clipboard (DECW$CLIPBOARD)"
1170 PRINT "  FIND <keyword>                Search document for keyword"
1180 PRINT "  REPLACE <old>|<new>           Global search and replace across document"
1190 PRINT "  WRAP <col|OFF>                Set word-wrap column and reflow lines"
1200 PRINT "  READONLY <ON|OFF>             Toggle Read-Only buffer protection"
1210 PRINT "  STATS / SHOW / STATUS         Count lines, words, characters, and settings"
1220 PRINT "  DISPLAY / PRINT ON <file>     Render Motif/XUI DECwindows Notepad window"
1222 PRINT "  SAVE <file> / LOAD <file>     Save or load text file"
1224 PRINT "  CLEAR / NEW / HELP / EXIT     Clear buffer, help, or quit"
1225 RETURN
1230 LINE_CNT% = 0% \ CUR_LN% = 0% \ MOD_FLAG% = 0% \ RO_FLAG% = 0% \ DOC_NAME$ = "SYS$LOGIN:UNTITLED.TXT"
1250 PRINT "%NOTEPAD-I-CLEARED, Notepad document buffer cleared."
1260 RETURN
1270 LINE_CNT% = 6% \ CUR_LN% = 1% \ MOD_FLAG% = 0% \ RO_FLAG% = 0%
1280 DOC_NAME$ = "SYS$LOGIN:AXP_NOTES.TXT"
1290 NP_LINE$( 1% ) = "DECwindows Motif 1.1 & Alpha AXP Workstation Notes (19-OCT-1991)"
1300 NP_LINE$( 2% ) = "----------------------------------------------------------------"
1310 NP_LINE$( 3% ) = "1. Verify DECW$NOTEPAD XmText widget cut/copy/paste via DECW$CLIPBOARD."
1320 NP_LINE$( 4% ) = "2. Test compound string Latin-1 font rendering on HX/TX Framebuffer."
1330 NP_LINE$( 5% ) = "3. Confirm VMS V5.5 and DEC OSF/1 V1.0 file interchange compatibility."
1340 NP_LINE$( 6% ) = "4. Sign off ZKO Lab 3 workstation desktop integration checklist."
1350 PRINT "%NOTEPAD-I-SAMPLE, loaded 6 lines into "; DOC_NAME$; "."
1360 RETURN
1400 REM --- STATS / SHOW / STATUS ---
1410 CHAR_CNT% = 0% \ WORD_CNT% = 0% \ SI% = 1%
1420 IF SI% > LINE_CNT% THEN GOTO 1520
1430 L_TXT$ = NP_LINE$( SI% ) \ CHAR_CNT% = CHAR_CNT% + LEN(L_TXT$)
1440 IN_W% = 0% \ CI% = 1%
1450 IF CI% > LEN(L_TXT$) THEN GOTO 1510
1460 CH_C$ = MID$(L_TXT$, CI%, 1%)
1470 IF CH_C$ = " " THEN IN_W% = 0%
1480 IF CH_C$ <> " " AND IN_W% = 0% THEN WORD_CNT% = WORD_CNT% + 1%
1490 IF CH_C$ <> " " THEN IN_W% = 1%
1500 CI% = CI% + 1% \ GOTO 1450
1510 SI% = SI% + 1% \ GOTO 1420
1520 MOD_S$ = "CLEAN"
1525 IF MOD_FLAG% = 1% THEN MOD_S$ = "MODIFIED"
1530 RO_S$ = "READ-WRITE"
1535 IF RO_FLAG% = 1% THEN RO_S$ = "READ-ONLY"
1540 PRINT "--- DECwindows Notepad Document Status ---"
1550 PRINT "  Document File : "; DOC_NAME$; " ("; MOD_S$; ", "; RO_S$; ")"
1560 PRINT "  Metrics       : "; LINE_CNT%; " lines, "; WORD_CNT%; " words, "; CHAR_CNT%; " characters"
1570 PRINT "  Cursor Line   : "; CUR_LN%; "   Word-Wrap Col: "; WRAP_COL%; "   Clipboard Lines: "; CLIP_CNT%
1580 RETURN
1600 REM --- LIST / VIEW / TYPE ---
1610 PRINT "=== DECwindows Notepad Buffer: "; DOC_NAME$; " ("; LINE_CNT%; " lines) ==="
1620 IF LINE_CNT% = 0% THEN PRINT "  (Buffer is empty)"
1630 LI% = 1%
1640 IF LI% > LINE_CNT% THEN GOTO 1700
1650 CUR_MK$ = "  "
1660 IF LI% = CUR_LN% THEN CUR_MK$ = "> "
1670 PRINT " "; CUR_MK$; LI%; ": "; NP_LINE$( LI% )
1680 LI% = LI% + 1% \ GOTO 1640
1700 PRINT "=============================================================================="
1710 RETURN
1720 REM --- APPEND <text> ---
1730 IF RO_FLAG% = 1% THEN PRINT "%NOTEPAD-E-READONLY, buffer is locked read-only."
1740 IF RO_FLAG% = 1% THEN GOTO 1810
1750 IF LINE_CNT% >= 80% THEN PRINT "%NOTEPAD-E-BUFFULL, document buffer is full."
1760 IF LINE_CNT% >= 80% THEN GOTO 1810
1770 LINE_CNT% = LINE_CNT% + 1% \ NP_LINE$( LINE_CNT% ) = ARG$
1780 CUR_LN% = LINE_CNT% \ MOD_FLAG% = 1%
1790 PRINT "%NOTEPAD-I-APPENDED, appended line #"; LINE_CNT%; "."
1810 RETURN
1820 REM --- INSERT <n>|<text> ---
1830 IF RO_FLAG% = 1% THEN PRINT "%NOTEPAD-E-READONLY, buffer is locked read-only."
1840 IF RO_FLAG% = 1% THEN GOTO 1970
1850 P_LINE$ = ARG$ \ GOSUB 3410
1860 IF P_CNT% < 2% THEN PRINT "%NOTEPAD-E-SYNTAX, usage: INSERT <n>|<text>"
1870 IF P_CNT% < 2% THEN GOTO 1970
1880 INS_N% = VAL(FLD_P$( 1% ))
1890 IF INS_N% < 1% OR INS_N% > LINE_CNT% + 1% THEN PRINT "%NOTEPAD-E-INVLINE, invalid line number."
1900 IF INS_N% < 1% OR INS_N% > LINE_CNT% + 1% THEN GOTO 1970
1910 II% = LINE_CNT%
1920 IF II% < INS_N% THEN GOTO 1950
1930 NX_I% = II% + 1% \ NP_LINE$( NX_I% ) = NP_LINE$( II% ) \ II% = II% - 1% \ GOTO 1920
1950 NP_LINE$( INS_N% ) = FLD_P$( 2% ) \ LINE_CNT% = LINE_CNT% + 1% \ CUR_LN% = INS_N% \ MOD_FLAG% = 1%
1960 PRINT "%NOTEPAD-I-INSERTED, inserted line #"; INS_N%; "."
1970 RETURN
1980 REM --- EDIT <n>|<text> ---
1990 IF RO_FLAG% = 1% THEN PRINT "%NOTEPAD-E-READONLY, buffer is locked read-only."
2000 IF RO_FLAG% = 1% THEN GOTO 2090
2010 P_LINE$ = ARG$ \ GOSUB 3410
2020 IF P_CNT% < 2% THEN PRINT "%NOTEPAD-E-SYNTAX, usage: EDIT <n>|<text>"
2030 IF P_CNT% < 2% THEN GOTO 2090
2040 ED_N% = VAL(FLD_P$( 1% ))
2050 IF ED_N% < 1% OR ED_N% > LINE_CNT% THEN PRINT "%NOTEPAD-E-INVLINE, invalid line number."
2060 IF ED_N% < 1% OR ED_N% > LINE_CNT% THEN GOTO 2090
2070 NP_LINE$( ED_N% ) = FLD_P$( 2% ) \ CUR_LN% = ED_N% \ MOD_FLAG% = 1%
2080 PRINT "%NOTEPAD-I-EDITED, updated line #"; ED_N%; "."
2090 RETURN
2100 REM --- DELETE <start> [end] ---
2110 IF RO_FLAG% = 1% THEN PRINT "%NOTEPAD-E-READONLY, buffer is locked read-only."
2120 IF RO_FLAG% = 1% THEN GOTO 2270
2130 GOSUB 3700
2140 IF R_ERR% = 1% THEN GOTO 2270
2150 DEL_CNT% = R_END% - R_ST% + 1% \ NEW_C% = 0% \ DI% = 1%
2160 IF DI% > LINE_CNT% THEN GOTO 2210
2170 IF DI% >= R_ST% AND DI% <= R_END% THEN GOTO 2200
2180 NEW_C% = NEW_C% + 1% \ NP_LINE$( NEW_C% ) = NP_LINE$( DI% )
2200 DI% = DI% + 1% \ GOTO 2160
2210 LINE_CNT% = NEW_C% \ MOD_FLAG% = 1%
2220 IF CUR_LN% > LINE_CNT% THEN CUR_LN% = LINE_CNT%
2230 PRINT "%NOTEPAD-I-DELETED, deleted "; DEL_CNT%; " line(s)."
2270 RETURN
2280 REM --- COPY <start> [end] ---
2290 GOSUB 3700
2300 IF R_ERR% = 1% THEN GOTO 2430
2310 CLIP_CNT% = 0% \ CI% = R_ST%
2320 IF CI% > R_END% THEN GOTO 2360
2330 CLIP_CNT% = CLIP_CNT% + 1% \ CLIP_BUF$( CLIP_CNT% ) = NP_LINE$( CI% )
2340 CI% = CI% + 1% \ GOTO 2320
2360 PRINT "%NOTEPAD-I-COPIED, copied "; CLIP_CNT%; " line(s) to DECW$CLIPBOARD."
2430 RETURN
2440 REM --- CUT <start> [end] ---
2450 IF RO_FLAG% = 1% THEN PRINT "%NOTEPAD-E-READONLY, buffer is locked read-only."
2460 IF RO_FLAG% = 1% THEN GOTO 2520
2470 GOSUB 3700
2480 IF R_ERR% = 1% THEN GOTO 2520
2490 GOSUB 2280
2500 GOSUB 2100
2510 PRINT "%NOTEPAD-I-CUT, cut "; CLIP_CNT%; " line(s) to DECW$CLIPBOARD."
2520 RETURN
2530 REM --- PASTE [after_line] ---
2540 IF RO_FLAG% = 1% THEN PRINT "%NOTEPAD-E-READONLY, buffer is locked read-only."
2550 IF RO_FLAG% = 1% THEN GOTO 2700
2560 IF CLIP_CNT% = 0% THEN PRINT "%NOTEPAD-W-CLIPEMPTY, DECW$CLIPBOARD is empty."
2570 IF CLIP_CNT% = 0% THEN GOTO 2700
2580 PST_AFT% = LINE_CNT%
2590 IF LEN(ARG$) > 0% THEN PST_AFT% = VAL(ARG$)
2600 IF PST_AFT% < 0% OR PST_AFT% > LINE_CNT% THEN PST_AFT% = LINE_CNT%
2610 T_CNT% = 0% \ PI% = 1%
2620 IF PI% > PST_AFT% THEN GOTO 2640
2630 T_CNT% = T_CNT% + 1% \ TMP_BUF$( T_CNT% ) = NP_LINE$( PI% ) \ PI% = PI% + 1% \ GOTO 2620
2640 CI% = 1%
2645 IF CI% > CLIP_CNT% THEN GOTO 2660
2650 T_CNT% = T_CNT% + 1% \ TMP_BUF$( T_CNT% ) = CLIP_BUF$( CI% ) \ CI% = CI% + 1% \ GOTO 2645
2660 PI% = PST_AFT% + 1%
2665 IF PI% > LINE_CNT% THEN GOTO 2680
2670 T_CNT% = T_CNT% + 1% \ TMP_BUF$( T_CNT% ) = NP_LINE$( PI% ) \ PI% = PI% + 1% \ GOTO 2665
2680 LINE_CNT% = T_CNT% \ PI% = 1%
2685 IF PI% > LINE_CNT% THEN GOTO 2695
2690 NP_LINE$( PI% ) = TMP_BUF$( PI% ) \ PI% = PI% + 1% \ GOTO 2685
2695 MOD_FLAG% = 1% \ PRINT "%NOTEPAD-I-PASTED, pasted "; CLIP_CNT%; " line(s) from DECW$CLIPBOARD."
2700 RETURN
2710 REM --- CLIPBOARD ---
2720 PRINT "=== DECwindows Clipboard (DECW$CLIPBOARD: "; CLIP_CNT%; " lines) ==="
2730 IF CLIP_CNT% = 0% THEN PRINT "  (Clipboard empty)"
2740 CI% = 1%
2750 IF CI% > CLIP_CNT% THEN GOTO 2780
2760 PRINT "  ["; CI%; "] "; CLIP_BUF$( CI% )
2770 CI% = CI% + 1% \ GOTO 2750
2780 RETURN
2790 REM --- FIND / SEARCH ---
2800 IF LEN(UARG$) = 0% THEN PRINT "%NOTEPAD-E-NOKWD, specify search string."
2810 IF LEN(UARG$) = 0% THEN GOTO 2910
2820 PRINT "--- DECwindows Notepad Search Results for '"; ARG$; "' ---"
2830 HITS% = 0% \ FI% = 1%
2840 IF FI% > LINE_CNT% THEN GOTO 2900
2850 U_IN$ = NP_LINE$( FI% ) \ GOSUB 3620
2860 COL_F% = INSTR(1%, U_OUT$, UARG$)
2870 IF COL_F% = 0% THEN GOTO 2890
2880 HITS% = HITS% + 1% \ CUR_LN% = FI%
2885 PRINT "  Line "; FI%; " (Col "; COL_F%; "): "; NP_LINE$( FI% )
2890 FI% = FI% + 1% \ GOTO 2840
2900 PRINT "Total matches found: "; HITS%
2910 RETURN
2920 REM --- REPLACE <old>|<new> ---
2930 IF RO_FLAG% = 1% THEN PRINT "%NOTEPAD-E-READONLY, buffer is locked read-only."
2940 IF RO_FLAG% = 1% THEN GOTO 3110
2950 P_LINE$ = ARG$ \ GOSUB 3410
2960 IF P_CNT% < 2% THEN PRINT "%NOTEPAD-E-SYNTAX, usage: REPLACE <old>|<new>"
2970 IF P_CNT% < 2% THEN GOTO 3110
2980 OLD_S$ = FLD_P$( 1% ) \ NEW_S$ = FLD_P$( 2% ) \ REP_CNT% = 0% \ RI% = 1%
2990 IF LEN(OLD_S$) = 0% THEN GOTO 3110
3000 IF RI% > LINE_CNT% THEN GOTO 3090
3010 SRC_L$ = NP_LINE$( RI% ) \ M_POS% = INSTR(1%, SRC_L$, OLD_S$)
3020 IF M_POS% = 0% THEN GOTO 3080
3030 L_PART$ = ""
3040 IF M_POS% > 1% THEN L_PART$ = LEFT$(SRC_L$, M_POS% - 1%)
3050 R_PART$ = MID$(SRC_L$, M_POS% + LEN(OLD_S$), LEN(SRC_L$))
3060 NP_LINE$( RI% ) = L_PART$ + NEW_S$ + R_PART$ \ REP_CNT% = REP_CNT% + 1% \ MOD_FLAG% = 1%
3080 RI% = RI% + 1% \ GOTO 3000
3090 PRINT "%NOTEPAD-I-REPLACED, replaced "; REP_CNT%; " occurrence(s) of '"; OLD_S$; "' with '"; NEW_S$; "'."
3110 RETURN
3120 REM --- WRAP <col|OFF> ---
3130 IF UARG$ = "OFF" OR UARG$ = "0" THEN WRAP_COL% = 0%
3140 IF UARG$ = "OFF" OR UARG$ = "0" THEN PRINT "%NOTEPAD-I-WRAP, word-wrap disabled."
3150 IF UARG$ = "OFF" OR UARG$ = "0" THEN GOTO 3230
3160 W_VAL% = VAL(ARG$)
3170 IF W_VAL% < 20% OR W_VAL% > 132% THEN PRINT "%NOTEPAD-E-INVWRAP, wrap column must be 20..132 or OFF."
3180 IF W_VAL% < 20% OR W_VAL% > 132% THEN GOTO 3230
3190 WRAP_COL% = W_VAL% \ GOSUB 3780
3200 PRINT "%NOTEPAD-I-WRAP, word-wrap margin set to column "; WRAP_COL%; " (Lines: "; LINE_CNT%; ")."
3230 RETURN
3240 REM --- READONLY <ON|OFF> ---
3250 IF UARG$ = "ON" OR UARG$ = "1" THEN RO_FLAG% = 1%
3260 IF UARG$ = "OFF" OR UARG$ = "0" THEN RO_FLAG% = 0%
3270 PRINT "%NOTEPAD-I-READONLY, Read-Only mode set to "; RO_FLAG%; "."
3280 RETURN
3310 Q_CNT% = 0% \ REM_CMD$ = RAW_LINE$
3330 IF LEN(REM_CMD$) = 0% THEN GOTO 3400
3340 SEMI_P% = INSTR(1%, REM_CMD$, ";") \ Q_CNT% = Q_CNT% + 1%
3360 IF SEMI_P% = 0% THEN CMD_Q$( Q_CNT% ) = REM_CMD$
3370 IF SEMI_P% = 0% THEN REM_CMD$ = ""
3380 IF SEMI_P% > 0% THEN CMD_Q$( Q_CNT% ) = LEFT$(REM_CMD$, SEMI_P% - 1%)
3390 IF SEMI_P% > 0% THEN REM_CMD$ = MID$(REM_CMD$, SEMI_P% + 1%, LEN(REM_CMD$))
3395 GOTO 3330
3400 RETURN
3410 P_CNT% = 0% \ REM_P$ = P_LINE$
3430 IF LEN(REM_P$) = 0% THEN GOTO 3510
3440 PP% = INSTR(1%, REM_P$, "|") \ P_CNT% = P_CNT% + 1%
3460 IF PP% = 0% THEN FLD_P$( P_CNT% ) = REM_P$
3470 IF PP% = 0% THEN REM_P$ = ""
3480 IF PP% > 0% THEN FLD_P$( P_CNT% ) = LEFT$(REM_P$, PP% - 1%)
3490 IF PP% > 0% THEN REM_P$ = MID$(REM_P$, PP% + 1%, LEN(REM_P$))
3500 GOTO 3430
3510 RETURN
3520 IF LEN(C_STR$) = 0% THEN GOTO 3610
3540 IF LEFT$(C_STR$, 1%) <> " " THEN GOTO 3570
3550 C_STR$ = MID$(C_STR$, 2%, LEN(C_STR$)) \ GOTO 3520
3570 IF LEN(C_STR$) = 0% THEN GOTO 3610
3580 IF RIGHT$(C_STR$, 1%) <> " " THEN GOTO 3610
3590 C_STR$ = LEFT$(C_STR$, LEN(C_STR$) - 1%) \ GOTO 3570
3610 RETURN
3620 U_OUT$ = "" \ UI% = 1%
3640 IF UI% > LEN(U_IN$) THEN GOTO 3695
3650 CH_A% = ASCII(MID$(U_IN$, UI%, 1%))
3660 IF CH_A% >= 97% AND CH_A% <= 122% THEN CH_A% = CH_A% - 32%
3670 U_OUT$ = U_OUT$ + CHR$(CH_A%) \ UI% = UI% + 1% \ GOTO 3640
3695 RETURN
3700 REM --- Parse <start> [end] range in ARG$ ---
3710 R_ERR% = 0% \ SP_R% = INSTR(1%, ARG$, " ")
3720 IF SP_R% = 0% THEN R_ST% = VAL(ARG$)
3730 IF SP_R% = 0% THEN R_END% = R_ST%
3740 IF SP_R% > 0% THEN R_ST% = VAL(LEFT$(ARG$, SP_R% - 1%))
3750 IF SP_R% > 0% THEN R_END% = VAL(MID$(ARG$, SP_R% + 1%, LEN(ARG$)))
3760 IF R_ST% < 1% OR R_END% < R_ST% OR R_END% > LINE_CNT% THEN PRINT "%NOTEPAD-E-INVRANGE, invalid line range."
3765 IF R_ST% < 1% OR R_END% < R_ST% OR R_END% > LINE_CNT% THEN R_ERR% = 1%
3770 RETURN
3780 REM --- Reflow lines exceeding WRAP_COL% ---
3790 T_CNT% = 0% \ WI% = 1%
3800 IF WI% > LINE_CNT% THEN GOTO 3880
3810 W_LN$ = NP_LINE$( WI% )
3820 IF LEN(W_LN$) <= WRAP_COL% THEN GOTO 3860
3830 CUT_P% = WRAP_COL%
3840 T_CNT% = T_CNT% + 1% \ TMP_BUF$( T_CNT% ) = LEFT$(W_LN$, CUT_P%)
3850 W_LN$ = MID$(W_LN$, CUT_P% + 1%, LEN(W_LN$)) \ GOTO 3820
3860 T_CNT% = T_CNT% + 1% \ TMP_BUF$( T_CNT% ) = W_LN$
3870 WI% = WI% + 1% \ GOTO 3800
3880 LINE_CNT% = T_CNT% \ WI% = 1%
3890 IF WI% > LINE_CNT% THEN GOTO 3910
3900 NP_LINE$( WI% ) = TMP_BUF$( WI% ) \ WI% = WI% + 1% \ GOTO 3890
3910 RETURN
4120 IF LEFT$(UARG$, 3%) = "ON " THEN ARG$ = MID$(ARG$, 4%, LEN(ARG$))
4124 C_STR$ = ARG$ \ GOSUB 3520 \ ARG$ = C_STR$
4126 IF LEN(ARG$) > 0% THEN GOTO 4150
4130 PRT_CH% = 0% \ GOSUB 4190
4145 RETURN
4150 IF LEN(ARG$) = 0% THEN PRINT "%NOTEPAD-E-NOFILE, specify output filename."
4155 IF LEN(ARG$) = 0% THEN GOTO 4185
4160 OPEN ARG$ FOR OUTPUT AS FILE #2% \ PRT_CH% = 2% \ GOSUB 4190 \ CLOSE #2% \ PRT_CH% = 0%
4180 PRINT "%NOTEPAD-I-EXPORTED, DECwindows Notepad window exported to "; ARG$
4185 RETURN
4190 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4200 PAD38$ = "                                      " \ T_S$ = DOC_NAME$ + PAD38$ \ W_TMP$ = LEFT$(T_S$, 37%)
4204 OUT_L$ = "| [X] DECwindows Notepad: " + W_TMP$
4206 OUT_L$ = OUT_L$ + " [_][#] |" \ GOSUB 4305
4208 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4210 OUT_L$ = "| File    Edit    Search    Format    Options                           Help |" \ GOSUB 4305
4215 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4218 OUT_L$ = "| [Cut]  [Copy]  [Paste]  [Find]  [Replace]  [Wrap:" + STR$(WRAP_COL%)
4220 OUT_L$ = OUT_L$ + "]  Lines:" + STR$(LINE_CNT%)
4222 OUT_L$ = OUT_L$ + " |" \ GOSUB 4305
4225 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4230 OUT_L$ = "| ....+....1....+....2....+....3....+....4....+....5....+....6....+....7.... |" \ GOSUB 4305
4235 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4240 DI% = 1%
4245 IF DI% > LINE_CNT% THEN GOTO 4270
4250 W_ROW$ = "| " + STR$(DI%) + COLON$ + SP1$ + NP_LINE$( DI% )
4255 OUT_L$ = W_ROW$ \ GOSUB 4305
4265 DI% = DI% + 1% \ GOTO 4245
4270 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4275 OUT_L$ = "| DECW$CLIPBOARD Buffer:" + STR$(CLIP_CNT%)
4278 OUT_L$ = OUT_L$ + " line(s)   Cursor Line:" + STR$(CUR_LN%)
4280 GOSUB 4305
4290 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4300 RETURN
4305 IF PRT_CH% = 0% THEN PRINT OUT_L$
4310 IF PRT_CH% = 2% THEN PRINT #2%, OUT_L$
4315 RETURN
4320 IF LEN(ARG$) = 0% THEN PRINT "%NOTEPAD-E-NOFILE, specify filename to save."
4330 IF LEN(ARG$) = 0% THEN GOTO 4395
4335 OPEN ARG$ FOR OUTPUT AS FILE #1% \ SVI% = 1%
4355 IF SVI% > LINE_CNT% THEN GOTO 4385
4360 S_REC$ = NP_LINE$( SVI% ) \ PRINT #1%, S_REC$ \ SVI% = SVI% + 1% \ GOTO 4355
4385 CLOSE #1% \ DOC_NAME$ = ARG$ \ MOD_FLAG% = 0%
4390 PRINT "%NOTEPAD-I-SAVED, saved "; LINE_CNT%; " lines to "; ARG$
4395 RETURN
4400 IF LEN(ARG$) = 0% THEN PRINT "%NOTEPAD-E-NOFILE, specify filename to load."
4410 IF LEN(ARG$) = 0% THEN GOTO 4495
4415 LINE_CNT% = 0% \ DOC_NAME$ = ARG$ \ MOD_FLAG% = 0%
4420 OPEN ARG$ FOR INPUT AS FILE #1%
4425 LINE INPUT #1%, L_REC$
4430 IF LEN(L_REC$) = 0% THEN GOTO 4485
4435 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 4485
4465 LINE_CNT% = LINE_CNT% + 1% \ NP_LINE$( LINE_CNT% ) = L_REC$
4480 GOTO 4425
4485 CLOSE #1% \ CUR_LN% = 1%
4490 PRINT "%NOTEPAD-I-LOADED, loaded "; LINE_CNT%; " lines from "; ARG$
4495 RETURN
4500 END
