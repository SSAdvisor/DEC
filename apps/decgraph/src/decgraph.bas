10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM D_LBL$(100%) \ DIM D_VAL(100%) \ NUM_PTS% = 0% \ G_TYPE$ = "BAR" \ G_WIDTH% = 50% \ G_HEIGHT% = 8%
20 G_TITLE$ = "DECgraph Presentation" \ G_SUB$ = "" \ G_XLABEL$ = "" \ G_YLABEL$ = "" \ DO_FILE% = 0% \ OUT_FILE$ = ""
30 BLANKS$ = "                                                                                "
40 STARS$  = "********************************************************************************"
50 BARS$   = "################################################################################"
60 SEP$    = "--------------------------------------------------------------------------------"
70 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
80 IF CMD_LINE$ = "" THEN GOTO 100
90 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 190
100 PRINT EQU$ \ PRINT "    DECgraph V3.0 - Business & Scientific Graphics Presentation System" \ PRINT "    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11" \ PRINT EQU$
110 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
120 PRINT "DECGRAPH> "; \ LINE INPUT RAW_INPUT$
130 IF LEN(RAW_INPUT$) = 0% THEN GOTO 2750
140 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 26% THEN GOTO 2750
150 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 0% THEN GOTO 2750
160 T_IN$ = RAW_INPUT$ \ GOSUB 520
170 IF T_OUT$ = "" THEN GOTO 120
180 SC_REM$ = T_OUT$
190 IF SC_REM$ = "" THEN GOTO 250
200 SC_P% = INSTR(1%, SC_REM$, ";")
210 IF SC_P% = 0% THEN GOTO 230
220 RAW_CMD$ = LEFT$(SC_REM$, SC_P% - 1%) \ SC_REM$ = MID$(SC_REM$, SC_P% + 1%, LEN(SC_REM$) - SC_P%) \ GOTO 240
230 RAW_CMD$ = SC_REM$ \ SC_REM$ = ""
240 GOSUB 270 \ GOTO 190
250 IF IS_BATCH% = 1% THEN GOTO 2750
260 GOTO 120
270 T_IN$ = RAW_CMD$ \ GOSUB 520 \ WORK_CMD$ = T_OUT$
280 IF WORK_CMD$ = "" THEN GOTO 510
290 SP% = INSTR(1%, WORK_CMD$, " ")
300 IF SP% = 0% THEN GOTO 320
310 VERB$ = LEFT$(WORK_CMD$, SP% - 1%) \ ARGS$ = MID$(WORK_CMD$, SP% + 1%, LEN(WORK_CMD$) - SP%) \ GOTO 330
320 VERB$ = WORK_CMD$ \ ARGS$ = ""
330 U_IN$ = VERB$ \ GOSUB 600 \ VERB$ = U_OUT$ \ T_IN$ = ARGS$ \ GOSUB 520 \ ARGS$ = T_OUT$
340 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "BYE" THEN GOTO 2750
350 IF VERB$ = "HELP" THEN GOTO 2680
360 IF VERB$ = "TYPE" OR VERB$ = "CHART" THEN GOTO 660
370 IF VERB$ = "DATA" OR VERB$ = "ADD" OR VERB$ = "POINT" THEN GOTO 860
380 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 970
390 IF VERB$ = "TITLE" THEN GOTO 1000
400 IF VERB$ = "SUBTITLE" OR VERB$ = "SUB" THEN GOTO 1050
410 IF VERB$ = "XLABEL" THEN GOTO 1100
420 IF VERB$ = "YLABEL" THEN GOTO 1110
430 IF VERB$ = "PLOT" OR VERB$ = "DRAW" OR VERB$ = "GRAPH" THEN GOTO 1520
440 IF VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 1450
450 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1120
460 IF VERB$ = "LIST" THEN GOTO 1190
470 IF VERB$ = "CLEAR" OR VERB$ = "RESET" OR VERB$ = "NEW" THEN GOTO 1250
480 IF VERB$ = "SAVE" THEN GOTO 1260
490 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1330
500 PRINT "DECgraph: Unknown command '"; VERB$; "'. Type HELP for syntax."
510 RETURN
520 T_OUT$ = T_IN$
530 IF LEN(T_OUT$) = 0% THEN GOTO 590
540 IF LEFT$(T_OUT$, 1%) = " " THEN T_OUT$ = MID$(T_OUT$, 2%, LEN(T_OUT$) - 1%)
550 IF LEFT$(T_OUT$, 1%) = " " THEN GOTO 530
560 IF LEN(T_OUT$) = 0% THEN GOTO 590
570 IF MID$(T_OUT$, LEN(T_OUT$), 1%) = " " THEN T_OUT$ = LEFT$(T_OUT$, LEN(T_OUT$) - 1%)
580 IF MID$(T_OUT$, LEN(T_OUT$), 1%) = " " THEN GOTO 560
590 RETURN
600 U_OUT$ = "" \ UJ% = 1%
610 IF UJ% > LEN(U_IN$) THEN GOTO 650
620 UCH$ = MID$(U_IN$, UJ%, 1%) \ UA% = ASCII(UCH$)
630 IF UA% >= 97% AND UA% <= 122% THEN UCH$ = CHR$(UA% - 32%)
640 U_OUT$ = U_OUT$ + UCH$ \ UJ% = UJ% + 1% \ GOTO 610
650 RETURN
660 IF ARGS$ = "" THEN GOTO 850
670 U_IN$ = ARGS$ \ GOSUB 600 \ T_REQ$ = U_OUT$
680 IF T_REQ$ = "BAR" THEN GOTO 790
690 IF T_REQ$ = "HBAR" THEN GOTO 790
700 IF T_REQ$ = "VBAR" THEN GOTO 800
710 IF T_REQ$ = "COLUMN" THEN GOTO 800
720 IF T_REQ$ = "LINE" THEN GOTO 810
730 IF T_REQ$ = "TREND" THEN GOTO 810
740 IF T_REQ$ = "PIE" THEN GOTO 820
750 IF T_REQ$ = "SHARE" THEN GOTO 820
760 IF T_REQ$ = "SCATTER" THEN GOTO 830
770 IF T_REQ$ = "XY" THEN GOTO 830
780 PRINT "DECgraph: Unsupported chart type '"; ARGS$; "'. Use BAR, VBAR, LINE, PIE, or SCATTER." \ GOTO 510
790 G_TYPE$ = "BAR" \ GOTO 840
800 G_TYPE$ = "VBAR" \ GOTO 840
810 G_TYPE$ = "LINE" \ GOTO 840
820 G_TYPE$ = "PIE" \ GOTO 840
830 G_TYPE$ = "SCATTER" \ GOTO 840
840 PRINT "[Chart type set to "; G_TYPE$; "]" \ GOTO 510
850 PRINT "Current chart type is "; G_TYPE$ \ GOTO 510
860 IF ARGS$ = "" THEN GOTO 960
870 CP% = INSTR(1%, ARGS$, ",")
880 IF CP% = 0% THEN CP% = INSTR(1%, ARGS$, " ")
890 IF CP% = 0% THEN GOTO 960
900 T_IN$ = LEFT$(ARGS$, CP% - 1%) \ GOSUB 520 \ LBL$ = T_OUT$ \ QCH$ = CHR$(34%) \ QL% = LEN(LBL$)
910 IF QL% < 2% THEN GOTO 940
920 IF LEFT$(LBL$, 1%) <> QCH$ THEN GOTO 940
930 IF RIGHT$(LBL$, QL%) = QCH$ THEN LBL$ = MID$(LBL$, 2%, QL% - 2%)
940 T_IN$ = MID$(ARGS$, CP% + 1%, LEN(ARGS$) - CP%) \ GOSUB 520 \ VAL_STR$ = T_OUT$ \ VAL_N = VAL(VAL_STR$) \ NUM_PTS% = NUM_PTS% + 1% \ D_LBL$(NUM_PTS%) = LBL$
950 D_VAL(NUM_PTS%) = VAL_N \ PRINT "[Point "; NUM_PTS%; " added: "; LBL$; " = "; VAL_N; "]" \ GOTO 510
960 PRINT "DECgraph: Syntax is DATA <label>, <value>" \ GOTO 510
970 NUM_PTS% = 4% \ D_LBL$(1%) = "Q1" \ D_VAL(1%) = 45 \ D_LBL$(2%) = "Q2" \ D_VAL(2%) = 78 \ D_LBL$(3%) = "Q3" \ D_VAL(3%) = 112 \ D_LBL$(4%) = "Q4" \ D_VAL(4%) = 95
980 G_TITLE$ = "Quarterly Revenue" \ G_SUB$ = "Digital Equipment Corporation" \ G_XLABEL$ = "Quarter" \ G_YLABEL$ = "Millions USD"
990 PRINT "[Sample dataset loaded - 4 quarterly points]" \ GOTO 510
1000 QCH$ = CHR$(34%) \ QL% = LEN(ARGS$)
1010 IF QL% < 2% THEN GOTO 1040
1020 IF LEFT$(ARGS$, 1%) <> QCH$ THEN GOTO 1040
1030 IF RIGHT$(ARGS$, QL%) = QCH$ THEN ARGS$ = MID$(ARGS$, 2%, QL% - 2%)
1040 G_TITLE$ = ARGS$ \ PRINT "[Title set to: "; G_TITLE$; "]" \ GOTO 510
1050 QCH$ = CHR$(34%) \ QL% = LEN(ARGS$)
1060 IF QL% < 2% THEN GOTO 1090
1070 IF LEFT$(ARGS$, 1%) <> QCH$ THEN GOTO 1090
1080 IF RIGHT$(ARGS$, QL%) = QCH$ THEN ARGS$ = MID$(ARGS$, 2%, QL% - 2%)
1090 G_SUB$ = ARGS$ \ PRINT "[Subtitle set to: "; G_SUB$; "]" \ GOTO 510
1100 G_XLABEL$ = ARGS$ \ PRINT "[X-axis label set to: "; G_XLABEL$; "]" \ GOTO 510
1110 G_YLABEL$ = ARGS$ \ PRINT "[Y-axis label set to: "; G_YLABEL$; "]" \ GOTO 510
1120 U_IN$ = ARGS$ \ GOSUB 600 \ S_ARG$ = U_OUT$
1130 IF S_ARG$ = "DATA" OR S_ARG$ = "POINTS" THEN GOTO 1190
1140 PRINT "DECgraph Configuration:" \ PRINT "  Chart Type:   "; G_TYPE$ \ PRINT "  Title:        "; G_TITLE$
1150 IF G_SUB$ <> "" THEN PRINT "  Subtitle:     "; G_SUB$
1160 IF G_XLABEL$ <> "" THEN PRINT "  X-Axis:       "; G_XLABEL$
1170 IF G_YLABEL$ <> "" THEN PRINT "  Y-Axis:       "; G_YLABEL$
1180 PRINT "  Data Points:  "; NUM_PTS% \ GOTO 510
1190 IF NUM_PTS% = 0% THEN GOTO 2670
1200 PRINT "DECgraph Data Points ("; NUM_PTS%; " total):" \ PRINT "Index  Label             Value" \ PRINT "------------------------------" \ LI% = 1%
1210 IF LI% > NUM_PTS% THEN GOTO 1240
1220 IDX_STR$ = STR$(LI%) \ T_IN$ = IDX_STR$ \ GOSUB 520 \ IDX_PAD$ = LEFT$(T_OUT$ + BLANKS$, 6%) \ LBL_PAD$ = LEFT$(D_LBL$(LI%) + BLANKS$, 16%)
1230 PRINT IDX_PAD$; " "; LBL_PAD$; "  "; D_VAL(LI%) \ LI% = LI% + 1% \ GOTO 1210
1240 PRINT "------------------------------" \ GOTO 510
1250 NUM_PTS% = 0% \ G_TITLE$ = "DECgraph Presentation" \ G_SUB$ = "" \ G_XLABEL$ = "" \ G_YLABEL$ = "" \ G_TYPE$ = "BAR" \ PRINT "[Dataset and settings cleared]" \ GOTO 510
1260 IF NUM_PTS% = 0% THEN GOTO 2670
1270 IF ARGS$ = "" THEN GOTO 1320
1280 OPEN ARGS$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1290 IF SI% > NUM_PTS% THEN GOTO 1310
1300 PRINT #2%, D_LBL$(SI%); "|"; D_VAL(SI%) \ SI% = SI% + 1% \ GOTO 1290
1310 CLOSE #2% \ PRINT "["; NUM_PTS%; " points saved to "; ARGS$; "]" \ GOTO 510
1320 PRINT "DECgraph: Specify save filename (SAVE <filename>)" \ GOTO 510
1330 IF ARGS$ = "" THEN GOTO 1440
1340 ON ERROR GOTO 1420 \ OPEN ARGS$ FOR INPUT AS FILE #2% \ NUM_PTS% = 0%
1350 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 520
1360 IF T_OUT$ = "" THEN GOTO 1350
1370 SEP_P% = INSTR(1%, T_OUT$, "|")
1380 IF SEP_P% = 0% THEN SEP_P% = INSTR(1%, T_OUT$, ",")
1390 IF SEP_P% = 0% THEN GOTO 1350
1400 LBL$ = LEFT$(T_OUT$, SEP_P% - 1%) \ VAL_STR$ = MID$(T_OUT$, SEP_P% + 1%, LEN(T_OUT$) - SEP_P%) \ NUM_PTS% = NUM_PTS% + 1% \ D_LBL$(NUM_PTS%) = LBL$
1410 D_VAL(NUM_PTS%) = VAL(VAL_STR$) \ GOTO 1350
1420 CLOSE #2% \ RESUME 1430
1430 ON ERROR GOTO 0 \ PRINT "["; NUM_PTS%; " points loaded from "; ARGS$; "]" \ GOTO 510
1440 PRINT "DECgraph: Specify load filename (LOAD <filename>)" \ GOTO 510
1450 U_IN$ = ARGS$ \ GOSUB 600 \ U_ARGS$ = U_OUT$ \ ON_P% = INSTR(1%, U_ARGS$, "ON ")
1460 IF ON_P% > 0% THEN OUT_FILE$ = MID$(ARGS$, ON_P% + 3%, LEN(ARGS$) - ON_P% - 2%)
1470 IF ON_P% = 0% THEN OUT_FILE$ = ARGS$
1480 T_IN$ = OUT_FILE$ \ GOSUB 520 \ OUT_FILE$ = T_OUT$
1490 IF OUT_FILE$ = "" THEN GOTO 1510
1500 DO_FILE% = 1% \ OPEN OUT_FILE$ FOR OUTPUT AS FILE #2% \ GOTO 1530
1510 PRINT "DECgraph: Specify output filename (PRINT ON <file> or EXPORT <file>)" \ GOTO 510
1520 DO_FILE% = 0%
1530 IF NUM_PTS% = 0% THEN GOTO 2670
1540 MIN_V = D_VAL(1%) \ MAX_V = MIN_V \ SUM_V = 0 \ CI% = 1%
1550 IF CI% > NUM_PTS% THEN GOTO 1600
1560 V = D_VAL(CI%) \ SUM_V = SUM_V + V
1570 IF V < MIN_V THEN MIN_V = V
1580 IF V > MAX_V THEN MAX_V = V
1590 CI% = CI% + 1% \ GOTO 1550
1600 IF MAX_V = MIN_V THEN MAX_V = MIN_V + 1
1610 BASE_V = 0
1620 IF MIN_V < 0 THEN BASE_V = MIN_V
1630 PRINT EQU$
1640 IF DO_FILE% = 1% THEN PRINT #2%, EQU$
1650 T_LINE$ = "  " + G_TITLE$ \ PRINT T_LINE$
1660 IF DO_FILE% = 1% THEN PRINT #2%, T_LINE$
1670 IF G_SUB$ = "" THEN GOTO 1700
1680 S_LINE$ = "  " + G_SUB$ \ PRINT S_LINE$
1690 IF DO_FILE% = 1% THEN PRINT #2%, S_LINE$
1700 PRINT EQU$
1710 IF DO_FILE% = 1% THEN PRINT #2%, EQU$
1720 IF G_TYPE$ = "BAR" THEN GOTO 1800
1730 IF G_TYPE$ = "HBAR" THEN GOTO 1800
1740 IF G_TYPE$ = "VBAR" THEN GOTO 1940
1750 IF G_TYPE$ = "COLUMN" THEN GOTO 1940
1760 IF G_TYPE$ = "LINE" THEN GOTO 2170
1770 IF G_TYPE$ = "PIE" THEN GOTO 2450
1780 IF G_TYPE$ = "SCATTER" THEN GOTO 2170
1790 GOTO 1800
1800 PI% = 1%
1810 IF PI% > NUM_PTS% THEN GOTO 1880
1820 LBL_PAD$ = LEFT$(D_LBL$(PI%) + BLANKS$, 12%) \ V = D_VAL(PI%) \ BAR_LEN% = INT(V * 40 / MAX_V)
1830 IF BAR_LEN% < 1% THEN BAR_LEN% = 1%
1840 IF BAR_LEN% > 40% THEN BAR_LEN% = 40%
1850 BAR_STR$ = LEFT$(STARS$, BAR_LEN%) \ VAL_STR$ = STR$(V) \ T_IN$ = VAL_STR$ \ GOSUB 520 \ VAL_TR$ = T_OUT$ \ PRINT LBL_PAD$; " | "; BAR_STR$; " ("; VAL_TR$; ")"
1860 IF DO_FILE% = 1% THEN PRINT #2%, LBL_PAD$; " | "; BAR_STR$; " ("; VAL_TR$; ")"
1870 PI% = PI% + 1% \ GOTO 1810
1880 PRINT SEP$
1890 IF DO_FILE% = 1% THEN PRINT #2%, SEP$
1900 IF G_XLABEL$ = "" THEN GOTO 2640
1910 PRINT "  Scale: "; G_XLABEL$
1920 IF DO_FILE% = 1% THEN PRINT #2%, "  Scale: "; G_XLABEL$
1930 GOTO 2640
1940 LV% = 8%
1950 IF LV% < 1% THEN GOTO 2060
1960 LEV_V = BASE_V + (MAX_V - BASE_V) * LV% / 8 \ LEV_INT% = INT(LEV_V) \ LEV_STR$ = STR$(LEV_INT%) \ T_IN$ = LEV_STR$ \ GOSUB 520
1970 Y_PAD% = 6% - LEN(T_OUT$) \ IF Y_PAD% < 0% THEN Y_PAD% = 0%
1980 ROW$ = LEFT$(BLANKS$, Y_PAD%) + T_OUT$ + " |" \ PI% = 1%
1990 IF PI% > NUM_PTS% THEN GOTO 2030
2000 IF D_VAL(PI%) >= LEV_V THEN ROW$ = ROW$ + "  ###   "
2010 IF D_VAL(PI%) < LEV_V THEN ROW$ = ROW$ + "        "
2020 PI% = PI% + 1% \ GOTO 1990
2030 PRINT ROW$
2040 IF DO_FILE% = 1% THEN PRINT #2%, ROW$
2050 LV% = LV% - 1% \ GOTO 1950
2060 AXIS$ = "       +" \ LBLS$ = "        " \ PI% = 1%
2070 IF PI% > NUM_PTS% THEN GOTO 2100
2080 AXIS$ = AXIS$ + "-------+" \ SHORT_L$ = LEFT$(D_LBL$(PI%) + BLANKS$, 4%) \ LBLS$ = LBLS$ + "  " \ LBLS$ = LBLS$ + SHORT_L$ \ LBLS$ = LBLS$ + "  "
2090 PI% = PI% + 1% \ GOTO 2070
2100 PRINT AXIS$ \ PRINT LBLS$
2110 IF DO_FILE% = 1% THEN PRINT #2%, AXIS$
2120 IF DO_FILE% = 1% THEN PRINT #2%, LBLS$
2130 IF G_XLABEL$ = "" THEN GOTO 2640
2140 PRINT "        ["; G_XLABEL$; "]"
2150 IF DO_FILE% = 1% THEN PRINT #2%, "        ["; G_XLABEL$; "]"
2160 GOTO 2640
2170 LV% = 8%
2180 IF LV% < 1% THEN GOTO 2340
2190 LEV_V = MIN_V + (MAX_V - MIN_V) * LV% / 8 \ LEV_P = MIN_V + (MAX_V - MIN_V) * (LV% - 1%) / 8 \ LEV_INT% = INT(LEV_V) \ LEV_STR$ = STR$(LEV_INT%) \ T_IN$ = LEV_STR$ \ GOSUB 520
2200 Y_PAD% = 6% - LEN(T_OUT$) \ IF Y_PAD% < 0% THEN Y_PAD% = 0%
2210 ROW$ = LEFT$(BLANKS$, Y_PAD%) + T_OUT$ + " |" \ PI% = 1%
2220 IF PI% > NUM_PTS% THEN GOTO 2310
2230 V = D_VAL(PI%) \ HIT% = 0%
2240 IF V <= LEV_P THEN GOTO 2260
2250 IF V <= LEV_V THEN HIT% = 1%
2260 IF LV% <> 1% THEN GOTO 2280
2270 IF V <= LEV_V THEN HIT% = 1%
2280 IF HIT% = 1% THEN ROW$ = ROW$ + "  (*)   "
2290 IF HIT% = 0% THEN ROW$ = ROW$ + "   .    "
2300 PI% = PI% + 1% \ GOTO 2220
2310 PRINT ROW$
2320 IF DO_FILE% = 1% THEN PRINT #2%, ROW$
2330 LV% = LV% - 1% \ GOTO 2180
2340 AXIS$ = "       +" \ LBLS$ = "        " \ PI% = 1%
2350 IF PI% > NUM_PTS% THEN GOTO 2380
2360 AXIS$ = AXIS$ + "-------+" \ SHORT_L$ = LEFT$(D_LBL$(PI%) + BLANKS$, 4%) \ LBLS$ = LBLS$ + "  " \ LBLS$ = LBLS$ + SHORT_L$ \ LBLS$ = LBLS$ + "  "
2370 PI% = PI% + 1% \ GOTO 2350
2380 PRINT AXIS$ \ PRINT LBLS$
2390 IF DO_FILE% = 1% THEN PRINT #2%, AXIS$
2400 IF DO_FILE% = 1% THEN PRINT #2%, LBLS$
2410 IF G_XLABEL$ = "" THEN GOTO 2640
2420 PRINT "        ["; G_XLABEL$; "]"
2430 IF DO_FILE% = 1% THEN PRINT #2%, "        ["; G_XLABEL$; "]"
2440 GOTO 2640
2450 HDR1$ = "Category        Value          Percent   Visual Share" \ PRINT HDR1$ \ PRINT SEP$
2460 IF DO_FILE% = 1% THEN PRINT #2%, HDR1$
2470 IF DO_FILE% = 1% THEN PRINT #2%, SEP$
2480 IF SUM_V <= 0 THEN SUM_V = 1
2490 PI% = 1%
2500 IF PI% > NUM_PTS% THEN GOTO 2600
2510 V = D_VAL(PI%) \ BAR_LEN% = INT(V * 35 / SUM_V)
2520 IF BAR_LEN% < 1% THEN BAR_LEN% = 1%
2530 IF BAR_LEN% > 35% THEN BAR_LEN% = 35%
2540 PAD_LEN% = 35% - BAR_LEN% \ PIE_BAR$ = LEFT$(STARS$, BAR_LEN%) \ PIE_PAD$ = LEFT$(BLANKS$, PAD_LEN%) \ LBL_PAD$ = LEFT$(D_LBL$(PI%) + BLANKS$, 14%)
2550 V_STR$ = STR$(V) \ T_IN$ = V_STR$ \ GOSUB 520 \ V_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%) \ PCT_T% = INT(V * 1000 / SUM_V) \ PCT_W% = INT(PCT_T% / 10%)
2560 PCT_F% = PCT_T% - PCT_W% * 10% \ P_STR$ = STR$(PCT_W%) + "." + STR$(PCT_F%) + "%" \ T_IN$ = P_STR$ \ GOSUB 520 \ P_PAD$ = LEFT$(T_OUT$ + BLANKS$, 8%)
2570 PRINT LBL_PAD$; "  "; V_PAD$; "  "; P_PAD$; "  ["; PIE_BAR$; PIE_PAD$; "]"
2580 IF DO_FILE% = 1% THEN PRINT #2%, LBL_PAD$; "  "; V_PAD$; "  "; P_PAD$; "  ["; PIE_BAR$; PIE_PAD$; "]"
2590 PI% = PI% + 1% \ GOTO 2500
2600 PRINT SEP$ \ PRINT "Total           "; SUM_V; "      100.0%"
2610 IF DO_FILE% = 1% THEN PRINT #2%, SEP$
2620 IF DO_FILE% = 1% THEN PRINT #2%, "Total           "; SUM_V; "      100.0%"
2630 GOTO 2640
2640 PRINT EQU$
2650 IF DO_FILE% = 0% THEN GOTO 510
2660 PRINT #2%, EQU$ \ CLOSE #2% \ DO_FILE% = 0% \ PRINT "[Chart written to "; OUT_FILE$; "]" \ GOTO 510
2670 PRINT "DECgraph: No data points loaded. Use DATA <lbl>,<val> or SAMPLE." \ GOTO 510
2680 PRINT EQU$ \ PRINT "    DECgraph Graphics & Charting Commands" \ PRINT EQU$ \ PRINT "  TYPE <BAR|VBAR|LINE|PIE|SCATTER> Set chart presentation format"
2690 PRINT "  DATA <label>, <value>            Add a labeled data point" \ PRINT "  SAMPLE / DEMO                    Load DEC quarterly revenue sample data"
2700 PRINT "  TITLE <text> / SUBTITLE <text>   Configure chart headings" \ PRINT "  XLABEL <text> / YLABEL <text>   Configure axis annotations"
2710 PRINT "  SHOW [DATA|STATUS] / LIST        Inspect data points and settings" \ PRINT "  PLOT / DRAW                      Render current chart to terminal"
2720 PRINT "  PRINT ON <file> / EXPORT <file>  Render chart to output file" \ PRINT "  SAVE <file> / LOAD <file>        File interchange (label|value format)"
2730 PRINT "  CLEAR / RESET                    Reset active dataset and configuration"
2740 PRINT "  EXIT / QUIT / BYE                Exit DECgraph session" \ PRINT EQU$ \ GOTO 510
2750 IF DO_FILE% = 1% THEN CLOSE #2%
2760 END
