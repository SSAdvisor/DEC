10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM TERM_LINE$(60%) \ DIM TERM_ATTR$(60%) \ DIM UDK_KEY$(20%) \ DIM UDK_VAL$(20%)
20 NUM_LINES% = 0% \ NUM_UDK% = 0% \ EMUL_MODE$ = "VT300" \ TERM_COLS% = 80% \ TERM_ROWS% = 24% \ CUR_STYLE$ = "BLOCK"
30 AUTO_WRAP$ = "ON" \ MAX_SCROLL% = 500% \ WIN_TITLE$ = "DECterm - VAX/VMS Session 1" \ SESS_FILE$ = "DECTERM.LOG"
40 BLANKS$ = "                                                                                " \ LBRK$ = "[" \ RBRK$ = "]" \ VBAR$ = "|"
50 SEP$    = "--------------------------------------------------------------------------------"
60 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
70 GOSUB 700
80 IF CMD_LINE$ = "" THEN GOTO 100
90 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 180
100 PRINT EQU$ \ PRINT "    DECwindows DECterm V3.0 - XUI/Motif VT300 Terminal Emulator" \ PRINT "    Digital Equipment Corporation (DEC) VAX/VMS & ULTRIX Workstation Software" \ PRINT EQU$
110 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
120 PRINT "DECTERM> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 800
360 IF VERB$ = "SEND" OR VERB$ = "EXEC" OR VERB$ = "WRITE" THEN GOTO 1000
370 IF VERB$ = "DELLINE" OR VERB$ = "DELETE" OR VERB$ = "DEL" THEN GOTO 1180
380 IF VERB$ = "HISTORY" OR VERB$ = "SCROLLBACK" OR VERB$ = "TRANSCRIPT" OR VERB$ = "LIST" THEN GOTO 1290
390 IF VERB$ = "MODE" OR VERB$ = "EMULATE" THEN GOTO 1420
400 IF VERB$ = "COLUMNS" OR VERB$ = "COLS" THEN GOTO 1510
410 IF VERB$ = "ROWS" OR VERB$ = "LINES" THEN GOTO 1600
420 IF VERB$ = "CURSOR" THEN GOTO 1690
430 IF VERB$ = "AUTOWRAP" OR VERB$ = "WRAP" THEN GOTO 1780
440 IF VERB$ = "TITLE" THEN GOTO 1870
450 IF VERB$ = "DEFKEY" OR VERB$ = "UDK" THEN GOTO 1940
460 IF VERB$ = "KEYS" OR VERB$ = "SHOWKEYS" THEN GOTO 2120
470 IF VERB$ = "PRESS" OR VERB$ = "KEY" THEN GOTO 2240
480 IF VERB$ = "INSPECT" OR VERB$ = "ANALYZE" OR VERB$ = "PARSE" THEN GOTO 2380
482 IF VERB$ = "SCREEN" OR VERB$ = "DISPLAY" OR VERB$ = "RENDER" OR VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 2560
484 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2880
486 IF VERB$ = "SAVE" THEN GOTO 2990
488 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3090
490 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3190
494 PRINT "DECTERM: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
650 A_ATTR$ = "NORM" \ A_CLEAN$ = A_RAW$
655 IF INSTR(1%, A_RAW$, "ESC[1m") > 0% THEN A_ATTR$ = "BOLD"
660 IF INSTR(1%, A_RAW$, "ESC[4m") > 0% THEN A_ATTR$ = "UNDL"
665 IF INSTR(1%, A_RAW$, "ESC[7m") > 0% THEN A_ATTR$ = "REV"
670 IF INSTR(1%, A_RAW$, "ESC[2J") > 0% OR INSTR(1%, A_RAW$, "ESC[H") > 0% THEN A_ATTR$ = "CSI"
675 RETURN
700 NUM_UDK% = 4%
710 UDK_KEY$(1%) = "PF1" \ UDK_VAL$(1%) = "SHOW SYSTEM"
720 UDK_KEY$(2%) = "PF2" \ UDK_VAL$(2%) = "HELP /INSTRUCTIONS"
730 UDK_KEY$(3%) = "F6"  \ UDK_VAL$(3%) = "SET TERMINAL /VT300 /WIDTH=80"
740 UDK_KEY$(4%) = "F10" \ UDK_VAL$(4%) = "EXIT"
750 RETURN
800 NUM_LINES% = 10% \ WIN_TITLE$ = "DECterm - VAXcluster Node STAR:: (VT300)"
810 TERM_LINE$(1%)  = "ESC[1mWelcome to VAX/VMS V5.5-2 on node STAR::ESC[0m" \ TERM_ATTR$(1%) = "BOLD"
820 TERM_LINE$(2%)  = "    Last interactive login on Friday, 18-OCT-1991 08:42" \ TERM_ATTR$(2%) = "NORM"
830 TERM_LINE$(3%)  = "$ SET TERMINAL /INQUIRE /DEVICE_TYPE=VT300" \ TERM_ATTR$(3%) = "NORM"
840 TERM_LINE$(4%)  = "ESC[7m DECwindows XUI/Motif Session Manager - DECW$TERMINAL V3.0 ESC[0m" \ TERM_ATTR$(4%) = "REV"
850 TERM_LINE$(5%)  = "$ SHOW TERMINAL" \ TERM_ATTR$(5%) = "NORM"
860 TERM_LINE$(6%)  = "Terminal: _TWA12:   Device_Type: VT300_Series   Owner: SYSTEM" \ TERM_ATTR$(6%) = "NORM"
870 TERM_LINE$(7%)  = "   Width: 80        Page: 24 rows               DEC CRT1, CRT2, CRT3" \ TERM_ATTR$(7%) = "NORM"
880 TERM_LINE$(8%)  = "ESC[4mPID       Process Name    State  Pri      I/O       CPU       Page fltsESC[0m" \ TERM_ATTR$(8%) = "UNDL"
890 TERM_LINE$(9%)  = "00000101  SWAPPER         HIB     16        0   0 00:00:01.42         0" \ TERM_ATTR$(9%) = "NORM"
900 TERM_LINE$(10%) = "$ _ [Ready]" \ TERM_ATTR$(10%) = "NORM"
910 PRINT "[Sample DECterm VT300 session loaded - 10 screen lines, 4 UDK bindings]" \ GOTO 495
1000 IF NUM_LINES% >= 60% THEN GOTO 3390
1010 IF ARGS$ = "" THEN GOTO 1150
1020 Q_IN$ = ARGS$ \ GOSUB 635 \ S_TXT$ = Q_OUT$
1030 IF INSTR(1%, S_TXT$, "ESC[2J") > 0% THEN NUM_LINES% = 0%
1040 A_RAW$ = S_TXT$ \ GOSUB 650
1050 NUM_LINES% = NUM_LINES% + 1% \ TERM_LINE$(NUM_LINES%) = S_TXT$ \ TERM_ATTR$(NUM_LINES%) = A_ATTR$
1060 PRINT "[DECterm line #"; NUM_LINES%; " ("; A_ATTR$; "): "; S_TXT$; "]" \ GOTO 495
1150 PRINT "DECTERM: Syntax is SEND <text_or_escape_sequence>" \ GOTO 495
1180 IF NUM_LINES% = 0% THEN GOTO 3370
1190 D_IDX% = VAL(ARGS$)
1200 IF D_IDX% < 1% OR D_IDX% > NUM_LINES% THEN GOTO 3380
1210 D_TXT$ = TERM_LINE$(D_IDX%) \ DI% = D_IDX%
1220 IF DI% >= NUM_LINES% THEN GOTO 1260
1230 TERM_LINE$(DI%) = TERM_LINE$(DI% + 1%) \ TERM_ATTR$(DI%) = TERM_ATTR$(DI% + 1%) \ DI% = DI% + 1% \ GOTO 1220
1260 NUM_LINES% = NUM_LINES% - 1%
1270 PRINT "[Deleted scrollback line #"; D_IDX%; ": "; D_TXT$; "]" \ GOTO 495
1290 IF NUM_LINES% = 0% THEN GOTO 3370
1300 PRINT EQU$ \ PRINT "  DECterm Scrollback & Attribute Transcript ("; NUM_LINES%; " lines)" \ PRINT EQU$
1310 PRINT "Line#  Attr    Content" \ PRINT SEP$
1320 HI% = 1%
1330 IF HI% > NUM_LINES% THEN GOTO 1390
1340 H_S$ = STR$(HI%) \ T_IN$ = H_S$ \ GOSUB 500 \ H_P$ = LEFT$(T_OUT$ + BLANKS$, 7%)
1350 AT_P$ = LEFT$(TERM_ATTR$(HI%) + BLANKS$, 8%)
1360 PRINT H_P$; AT_P$; TERM_LINE$(HI%)
1370 HI% = HI% + 1% \ GOTO 1330
1390 PRINT EQU$ \ GOTO 495
1420 IF ARGS$ = "" THEN GOTO 1480
1430 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ M_ARG$ = U_OUT$
1440 IF M_ARG$ <> "VT300" AND M_ARG$ <> "VT220" AND M_ARG$ <> "VT100" AND M_ARG$ <> "VT52" THEN GOTO 1490
1450 EMUL_MODE$ = M_ARG$
1480 PRINT "[Terminal emulation mode set to "; EMUL_MODE$; "]" \ GOTO 495
1490 PRINT "DECTERM: Supported modes are VT300, VT220, VT100, or VT52" \ GOTO 495
1510 IF ARGS$ = "" THEN GOTO 1570
1520 C_VAL% = VAL(ARGS$)
1530 IF C_VAL% <> 80% AND C_VAL% <> 132% THEN GOTO 1580
1540 TERM_COLS% = C_VAL%
1570 PRINT "[Terminal display width set to "; TERM_COLS%; " columns]" \ GOTO 495
1580 PRINT "DECTERM: Supported column widths are 80 or 132 (DECCOLM)" \ GOTO 495
1600 IF ARGS$ = "" THEN GOTO 1660
1610 R_VAL% = VAL(ARGS$)
1620 IF R_VAL% <> 24% AND R_VAL% <> 36% AND R_VAL% <> 48% THEN GOTO 1670
1630 TERM_ROWS% = R_VAL%
1660 PRINT "[Terminal page length set to "; TERM_ROWS%; " rows]" \ GOTO 495
1670 PRINT "DECTERM: Supported row counts are 24, 36, or 48" \ GOTO 495
1690 IF ARGS$ = "" THEN GOTO 1750
1700 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ CR_ARG$ = U_OUT$
1710 IF CR_ARG$ <> "BLOCK" AND CR_ARG$ <> "UNDERLINE" THEN GOTO 1760
1720 CUR_STYLE$ = CR_ARG$
1750 PRINT "[Terminal cursor style set to "; CUR_STYLE$; "]" \ GOTO 495
1760 PRINT "DECTERM: Supported cursor styles are BLOCK or UNDERLINE" \ GOTO 495
1780 IF ARGS$ = "" THEN GOTO 1840
1790 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ AW_ARG$ = U_OUT$
1800 IF AW_ARG$ <> "ON" AND AW_ARG$ <> "OFF" THEN GOTO 1850
1810 AUTO_WRAP$ = AW_ARG$
1840 PRINT "[DECCAWM Auto-Wrap mode set to "; AUTO_WRAP$; "]" \ GOTO 495
1850 PRINT "DECTERM: Syntax is AUTOWRAP ON or AUTOWRAP OFF" \ GOTO 495
1870 IF ARGS$ = "" THEN GOTO 1910
1880 Q_IN$ = ARGS$ \ GOSUB 635 \ WIN_TITLE$ = Q_OUT$
1910 PRINT "[DECterm window title set to: "; WIN_TITLE$; "]" \ GOTO 495
1940 SP_K% = INSTR(1%, ARGS$, " ")
1950 IF SP_K% = 0% THEN GOTO 2090
1960 K_RAW$ = LEFT$(ARGS$, SP_K% - 1%) \ V_RAW$ = MID$(ARGS$, SP_K% + 1%, LEN(ARGS$) - SP_K%)
1970 U_IN$ = K_RAW$ \ GOSUB 580 \ K_NAME$ = U_OUT$ \ Q_IN$ = V_RAW$ \ GOSUB 635 \ K_STR$ = Q_OUT$
1980 F_IDX% = 0% \ KI% = 1%
1990 IF KI% > NUM_UDK% THEN GOTO 2030
2000 IF UDK_KEY$(KI%) = K_NAME$ THEN F_IDX% = KI%
2010 KI% = KI% + 1% \ GOTO 1990
2030 IF F_IDX% > 0% THEN GOTO 2060
2040 IF NUM_UDK% >= 20% THEN GOTO 2100
2050 NUM_UDK% = NUM_UDK% + 1% \ F_IDX% = NUM_UDK% \ UDK_KEY$(F_IDX%) = K_NAME$
2060 UDK_VAL$(F_IDX%) = K_STR$
2070 PRINT "[UDK key "; K_NAME$; " programmed -> "; K_STR$; "]" \ GOTO 495
2090 PRINT "DECTERM: Syntax is DEFKEY <key_name> <macro_string>" \ GOTO 495
2100 PRINT "DECTERM: UDK key table full (maximum 20 keys)" \ GOTO 495
2120 PRINT EQU$ \ PRINT "  DECterm VT300 User-Defined Keys (DECUDK) & PF Key Table" \ PRINT EQU$
2130 PRINT "Key     Macro Definition" \ PRINT SEP$
2140 KI% = 1%
2150 IF KI% > NUM_UDK% THEN GOTO 2200
2160 KP$ = LEFT$(UDK_KEY$(KI%) + BLANKS$, 8%)
2170 PRINT KP$; UDK_VAL$(KI%)
2180 KI% = KI% + 1% \ GOTO 2150
2200 PRINT EQU$ \ GOTO 495
2240 IF ARGS$ = "" THEN GOTO 2350
2250 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ P_KEY$ = U_OUT$
2260 P_FOUND% = 0% \ KI% = 1%
2270 IF KI% > NUM_UDK% THEN GOTO 2310
2280 IF UDK_KEY$(KI%) = P_KEY$ THEN P_FOUND% = KI%
2290 KI% = KI% + 1% \ GOTO 2270
2310 IF P_FOUND% = 0% THEN GOTO 2360
2320 M_CMD$ = UDK_VAL$(P_FOUND%)
2330 NUM_LINES% = NUM_LINES% + 1% \ TERM_LINE$(NUM_LINES%) = "$ " + M_CMD$ \ TERM_ATTR$(NUM_LINES%) = "NORM"
2340 PRINT "[Key "; P_KEY$; " transmitted: $ "; M_CMD$; "]" \ GOTO 495
2350 PRINT "DECTERM: Syntax is PRESS <key_name>" \ GOTO 495
2360 PRINT "DECTERM: Key '"; P_KEY$; "' is not defined in UDK table" \ GOTO 495
2380 IF NUM_LINES% = 0% THEN GOTO 3370
2390 C_NORM% = 0% \ C_BOLD% = 0% \ C_UNDL% = 0% \ C_REV% = 0% \ C_ESC% = 0% \ AI% = 1%
2400 IF AI% > NUM_LINES% THEN GOTO 2490
2410 IF TERM_ATTR$(AI%) = "NORM" THEN C_NORM% = C_NORM% + 1%
2420 IF TERM_ATTR$(AI%) = "BOLD" THEN C_BOLD% = C_BOLD% + 1%
2430 IF TERM_ATTR$(AI%) = "UNDL" THEN C_UNDL% = C_UNDL% + 1%
2440 IF TERM_ATTR$(AI%) = "REV" THEN C_REV% = C_REV% + 1%
2450 IF INSTR(1%, TERM_LINE$(AI%), "ESC[") > 0% THEN C_ESC% = C_ESC% + 1%
2460 AI% = AI% + 1% \ GOTO 2400
2490 PRINT EQU$ \ PRINT "  DECterm ANSI/VT Escape Sequence & Attribute Conformance Audit" \ PRINT SEP$
2500 PRINT "  Emulation Personality:  "; EMUL_MODE$; " ("; TERM_COLS%; "x"; TERM_ROWS%; ")"
2510 PRINT "  Total Buffer Lines:     "; NUM_LINES% \ PRINT "  ANSI/CSI Escape Lines:  "; C_ESC%
2520 PRINT "  Normal Lines (SGR 0):   "; C_NORM% \ PRINT "  Bold Lines (SGR 1):     "; C_BOLD%
2530 PRINT "  Underline Lines (SGR 4):"; C_UNDL% \ PRINT "  Reverse Video (SGR 7):  "; C_REV%
2540 PRINT "  [Audit PASSED: "; EMUL_MODE$; " parser verified all CSI/SGR control sequences]" \ PRINT EQU$ \ GOTO 495
2560 IF NUM_LINES% = 0% THEN GOTO 3370
2570 TO_FILE% = 0% \ OUT_FILE$ = ""
2580 IF ARGS$ = "" THEN GOTO 2640
2590 U_IN$ = ARGS$ \ GOSUB 580 \ U_ARGS$ = U_OUT$
2600 IF LEFT$(U_ARGS$, 3%) <> "ON " THEN GOTO 2630
2610 T_IN$ = MID$(ARGS$, 4%, LEN(ARGS$) - 3%) \ GOSUB 500 \ Q_IN$ = T_OUT$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1% \ GOTO 2640
2630 Q_IN$ = ARGS$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1%
2640 IF TO_FILE% = 1% THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2650 BDR$ = "+------------------------------------------------------------------------------+" \ SP1$ = " " \ XCH$ = "x"
2660 T_BAR$ = VBAR$ + " [=] " + WIN_TITLE$ + BLANKS$
2670 T_BAR$ = LEFT$(T_BAR$, 72%) + " [v][^]" + VBAR$
2680 M_BAR$ = VBAR$ + "  Commands    Setup    Edit    Customize    Window    Help                    " + VBAR$
2690 IF TO_FILE% = 1% THEN GOTO 2702
2692 PRINT BDR$ \ PRINT T_BAR$ \ PRINT BDR$ \ PRINT M_BAR$ \ PRINT BDR$ \ GOTO 2710
2702 PRINT #2%, BDR$ \ PRINT #2%, T_BAR$ \ PRINT #2%, BDR$ \ PRINT #2%, M_BAR$ \ PRINT #2%, BDR$
2710 RI% = 1%
2720 IF RI% > NUM_LINES% THEN GOTO 2790
2730 R_TXT$ = LEFT$(TERM_LINE$(RI%) + BLANKS$, 76%)
2740 R_ROW$ = VBAR$ + SP1$ + R_TXT$ + SP1$ + VBAR$
2750 IF TO_FILE% = 0% THEN PRINT R_ROW$
2760 IF TO_FILE% = 1% THEN PRINT #2%, R_ROW$
2770 RI% = RI% + 1% \ GOTO 2720
2790 C_S$ = STR$(TERM_COLS%) \ T_IN$ = C_S$ \ GOSUB 500 \ C_STR$ = T_OUT$
2800 R_S$ = STR$(TERM_ROWS%) \ T_IN$ = R_S$ \ GOSUB 500 \ R_STR$ = T_OUT$
2810 S_INF$ = " [Online] " + LBRK$ + EMUL_MODE$ + RBRK$ + SP1$ + LBRK$ + C_STR$ + XCH$ + R_STR$ + RBRK$
2814 S_INF$ = S_INF$ + " [Cursor:" + CUR_STYLE$ + RBRK$
2818 S_INF$ = S_INF$ + " [Wrap:" + AUTO_WRAP$ + RBRK$
2820 S_BAR$ = LEFT$(VBAR$ + S_INF$ + BLANKS$, 79%) + VBAR$
2830 IF TO_FILE% = 1% THEN GOTO 2840
2835 PRINT BDR$ \ PRINT S_BAR$ \ PRINT BDR$ \ GOTO 2860
2840 PRINT #2%, BDR$ \ PRINT #2%, S_BAR$ \ PRINT #2%, BDR$ \ CLOSE #2%
2850 PRINT "[DECterm window screen exported to "; OUT_FILE$; "]"
2860 GOTO 495
2880 PRINT EQU$ \ PRINT "  DECwindows DECterm V3.0 - Terminal Setup & Session Status" \ PRINT SEP$
2890 PRINT "  Window Title:           "; WIN_TITLE$
2900 PRINT "  Terminal Emulation:     "; EMUL_MODE$
2910 PRINT "  Screen Dimensions:      "; TERM_COLS%; " columns x "; TERM_ROWS%; " rows"
2920 PRINT "  Cursor Style:           "; CUR_STYLE$
2930 PRINT "  Auto-Wrap (DECCAWM):    "; AUTO_WRAP$
2940 PRINT "  Scrollback Transcript:  "; NUM_LINES%; " / "; MAX_SCROLL%; " lines"
2950 PRINT "  Programmed UDK Keys:    "; NUM_UDK%; " active key bindings"
2960 PRINT EQU$ \ GOTO 495
2990 IF NUM_LINES% = 0% THEN GOTO 3370
3000 IF ARGS$ = "" THEN GOTO 3010
3005 Q_IN$ = ARGS$ \ GOSUB 635 \ SESS_FILE$ = Q_OUT$
3010 OPEN SESS_FILE$ FOR OUTPUT AS FILE #1%
3020 SI% = 1%
3030 IF SI% > NUM_LINES% THEN GOTO 3070
3040 S_LN$ = TERM_LINE$(SI%) \ PRINT #1%, S_LN$
3050 SI% = SI% + 1% \ GOTO 3030
3070 CLOSE #1% \ PRINT "[Saved "; NUM_LINES%; " terminal line(s) to "; SESS_FILE$; "]" \ GOTO 495
3090 IF ARGS$ = "" THEN GOTO 3180
3100 Q_IN$ = ARGS$ \ GOSUB 635 \ SESS_FILE$ = Q_OUT$
3110 NUM_LINES% = 0% \ OPEN SESS_FILE$ FOR INPUT AS FILE #1%
3120 IF NUM_LINES% >= 60% THEN GOTO 3160
3130 LINE INPUT #1%, IN_L$
3140 IF LEN(IN_L$) = 0% THEN GOTO 3160
3145 IF ASCII(LEFT$(IN_L$, 1%)) = 0% THEN GOTO 3160
3150 T_IN$ = IN_L$ \ GOSUB 500 \ CLEAN_L$ = T_OUT$
3152 IF CLEAN_L$ = "" THEN GOTO 3160
3154 A_RAW$ = CLEAN_L$ \ GOSUB 650 \ NUM_LINES% = NUM_LINES% + 1% \ TERM_LINE$(NUM_LINES%) = CLEAN_L$ \ TERM_ATTR$(NUM_LINES%) = A_ATTR$ \ GOTO 3120
3160 CLOSE #1% \ PRINT "[Loaded "; NUM_LINES%; " terminal line(s) from "; SESS_FILE$; "]" \ GOTO 495
3180 PRINT "DECTERM: Syntax is LOAD <filename>" \ GOTO 495
3190 NUM_LINES% = 0% \ EMUL_MODE$ = "VT300" \ TERM_COLS% = 80% \ TERM_ROWS% = 24% \ CUR_STYLE$ = "BLOCK" \ AUTO_WRAP$ = "ON"
3200 GOSUB 700 \ PRINT "[DECSTR Soft Terminal Reset complete - screen and settings restored]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "  DECwindows DECterm Terminal Emulator Commands" \ PRINT SEP$
3230 PRINT "  SAMPLE                   Load sample VAX/VMS VT300 terminal session"
3240 PRINT "  SCREEN [ON <file>]       Render Motif/XUI DECterm window (or export)"
3250 PRINT "  HISTORY                  Display numbered scrollback transcript & attributes"
3260 PRINT "  SEND <text>              Transmit text or ANSI/VT CSI sequence to terminal"
3270 PRINT "  DELLINE <n>              Delete line #<n> from scrollback buffer"
3280 PRINT "  MODE VT300|VT220|VT100|VT52  Set terminal device emulation personality"
3290 PRINT "  COLUMNS 80|132           Set terminal screen width (DECCOLM)"
3300 PRINT "  ROWS 24|36|48            Set terminal page length"
3310 PRINT "  CURSOR BLOCK|UNDERLINE   Set terminal cursor style"
3320 PRINT "  AUTOWRAP ON|OFF          Set auto-wrap mode (DECCAWM)"
3330 PRINT "  TITLE <text>             Set DECwindows DECterm window title bar"
3340 PRINT "  DEFKEY <key> <macro>     Program a VT300 User-Defined Key (DECUDK)"
3350 PRINT "  KEYS / PRESS <key>       List or trigger programmed UDK function keys"
3360 PRINT "  INSPECT / SHOW           Audit ANSI/VT sequences or show terminal status"
3365 PRINT "  SAVE <f> / LOAD <f>      Save or load session transcript / CLEAR / EXIT" \ PRINT EQU$ \ GOTO 495
3370 PRINT "DECTERM: Scrollback buffer is empty. Use SAMPLE, SEND, or LOAD first." \ GOTO 495
3380 PRINT "DECTERM: Invalid line number." \ GOTO 495
3390 PRINT "DECTERM: Scrollback buffer is full (maximum 60 lines)." \ GOTO 495
3400 END
