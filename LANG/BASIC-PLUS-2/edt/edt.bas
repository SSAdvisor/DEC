10 ! ==============================================================================
20 ! DEC RSTS/E EDT Editor V3.0
30 ! Written in DEC BASIC-PLUS-2
40 !
50 ! A feature-rich implementation of the classic Digital Equipment Corporation
60 ! EDT text editor for RSTS/E, RSX-11M, and VMS systems.
70 !
80 ! Features:
90 !   - Authentic EDT Line Mode (* prompt)
100 !     Commands: TYPE (T), INSERT (I), DELETE (D), REPLACE (R),
110 !               FIND (F), SUBSTITUTE (S), RESEQ, SHOW, HELP,
120 !               WRITE (W), EXIT (EX), QUIT (QU), CHANGE (C)
130 !   - Full-Screen VT100 Keypad / Screen Mode (CHANGE mode)
140 !     Live buffer display, cursor navigation, interactive insertion,
150 !     deletion, status bar, and Ctrl-Z / Q return to line mode
160 !   - Robust file management: load, auto-create, save, write
170 ! ==============================================================================
180 DIM L$(500%)
182 DIM MACRO_NAME$(25%)
184 DIM MACRO_BODY$(25%)
186 DIM KEY_SPEC$(50%)
188 DIM KEY_DEF$(50%)
190 LET N% = 0%
200 LET CUR% = 0%
210 LET MODIFIED% = 0%
215 LET REPL_MODE% = 0%
216 LET NUM_MACROS% = 0%
217 LET NUM_KEYS% = 0%
218 LET QUEUED_CMD$ = ""
219 LET GOLD_ACTIVE% = 0%
220 LET F$ = ""
230 LET CMD$ = ""
240 LET ARG$ = ""
250 LET INP$ = ""
260 LET OP$ = ""
270 LET TOP% = 1%
280 LET BOT% = 1%
290 LET ST% = 0%
300 LET EN% = 0%
310 LET CNT% = 0%
320 LET POS% = 0%
330 LET K$ = ""
340 LET OLD$ = ""
350 LET NEW$ = ""
360 LET T1$ = ""
370 LET T2$ = ""
372 LET SUBTYPE$ = ""
374 LET REST$ = ""
376 LET KSPEC$ = ""
378 LET KCMD$ = ""
380 LET MNAME$ = ""
382 LET MCMD$ = ""
384 LET CFILE$ = ""
386 LET LOOKUP_KEY$ = ""
388 LET I% = 0%
390 LET J% = 0%
400 LET K% = 0%
402 LET M% = 0%

440 ! ------------------------------------------------------------------------------
450 ! Welcome Banner & File Load
460 ! ------------------------------------------------------------------------------
470 PRINT "DEC RSTS/E EDT Editor V3.0 (BASIC-PLUS-2)"
480 PRINT "Copyright (C) Digital Equipment Corporation / DEC-BASIC-PLUS-2"
490 PRINT ""
500 INPUT "File: "; F$
510 IF F$ = "" THEN LET F$ = "NONAME.TXT"
520 ON ERROR GOTO 620
530 OPEN F$ FOR INPUT AS FILE #1%
540 LINE INPUT #1%, INP$
550 LET N% = N% + 1%
560 LET L$(N%) = INP$
570 GOTO 540

580 ! File read finished or EOF hit
590 CLOSE #1%
600 ON ERROR GOTO 9900
610 GOTO 660

620 ! Error handler during file loading (EOF or File Not Found)
630 CLOSE #1%
640 ON ERROR GOTO 9900
650 IF N% = 0% THEN PRINT "[Input file does not exist: new file created]"

660 IF N% > 0% THEN PRINT "[File "; F$; ", "; N%; " lines read]"
670 IF N% > 0% THEN LET CUR% = 1% ELSE LET CUR% = 0%
680 LET MODIFIED% = 0%

685 ! Check for EDTINI.EDT startup configuration file
690 ON ERROR GOTO 705
695 OPEN "EDTINI.EDT" FOR INPUT AS FILE #3%
700 LINE INPUT #3%, INP$
701 IF INP$ = "" THEN GOTO 700
702 IF QUEUED_CMD$ = "" THEN LET QUEUED_CMD$ = INP$ ELSE LET QUEUED_CMD$ = QUEUED_CMD$ + ";" + INP$
703 GOTO 700
704 CLOSE #3%
705 CLOSE #3%
706 ON ERROR GOTO 9900
710 IF QUEUED_CMD$ <> "" THEN PRINT "[Loaded configuration from EDTINI.EDT]"
715 PRINT "Type HELP for command list, or CHANGE for screen mode."
720 PRINT ""

730 ! ==============================================================================
735 ! Main Line Mode Command Loop (* prompt)
738 ! ==============================================================================
740 IF QUEUED_CMD$ <> "" THEN GOTO 746
742 PRINT "*";
744 INPUT CMD$
745 GOTO 757
746 LET POS% = INSTR(QUEUED_CMD$, ";")
748 IF POS% > 0% THEN GOTO 754
750 LET CMD$ = QUEUED_CMD$
752 LET QUEUED_CMD$ = ""
753 GOTO 757
754 LET CMD$ = LEFT$(QUEUED_CMD$, POS% - 1%)
756 LET QUEUED_CMD$ = RIGHT$(QUEUED_CMD$, POS% + 1%)
757 IF LEFT$(CMD$, 1%) <> " " THEN GOTO 760
758 LET CMD$ = RIGHT$(CMD$, 2%)
759 GOTO 757
760 IF CMD$ = "" THEN GOTO 740
761 IF LEN(CMD$) = 1% AND ASCII(CMD$) = 26% THEN GOTO 3020
762 IF CMD$ = "." THEN GOTO 770
764 IF CMD$ = "T ." THEN GOTO 770
766 IF CMD$ = "D ." THEN GOTO 770
767 IF RIGHT$(CMD$, LEN(CMD$)) <> "." THEN GOTO 770
768 IF INSTR(CMD$, "/") > 0% THEN GOTO 770
769 LET CMD$ = LEFT$(CMD$, LEN(CMD$) - 1%)

770 ! Parse command name and optional arguments
780 LET POS% = INSTR(CMD$, " ")
790 IF POS% = 0% THEN LET OP$ = CMD$ ELSE LET OP$ = LEFT$(CMD$, POS% - 1%)
800 IF POS% = 0% THEN LET ARG$ = "" ELSE LET ARG$ = RIGHT$(CMD$, POS% + 1%)

810 ! Dispatch commands
820 IF OP$ = "T" THEN GOTO 1100
830 IF OP$ = "TYPE" THEN GOTO 1100
840 IF OP$ = "I" THEN GOTO 1340
850 IF OP$ = "INSERT" THEN GOTO 1340
860 IF OP$ = "D" THEN GOTO 1580
870 IF OP$ = "DELETE" THEN GOTO 1580
880 IF OP$ = "R" THEN GOTO 1880
890 IF OP$ = "REPLACE" THEN GOTO 1880
900 IF OP$ = "F" THEN GOTO 1960
910 IF OP$ = "FIND" THEN GOTO 1960
920 IF OP$ = "S" THEN GOTO 2170
930 IF OP$ = "SUBSTITUTE" THEN GOTO 2170
940 IF OP$ = "RESEQ" THEN GOTO 2420
950 IF OP$ = "RESEQUENCE" THEN GOTO 2420
960 IF OP$ = "SHOW" THEN GOTO 2470
970 IF OP$ = "HELP" THEN GOTO 2580
980 IF OP$ = "W" THEN GOTO 2790
990 IF OP$ = "WRITE" THEN GOTO 2790
1000 IF OP$ = "EX" THEN GOTO 2910
1010 IF OP$ = "EXIT" THEN GOTO 2910
1020 IF OP$ = "QU" THEN GOTO 3020
1030 IF OP$ = "QUIT" THEN GOTO 3020
1040 IF OP$ = "C" THEN GOTO 4000
1050 IF OP$ = "CHANGE" THEN GOTO 4000
1052 IF OP$ = "DEF" THEN GOTO 3200
1054 IF OP$ = "DEFINE" THEN GOTO 3200
1056 IF LEFT$(OP$, 1%) = "@" THEN GOTO 3400

1060 IF NUM_MACROS% <= 0% THEN GOTO 1090
1062 FOR M% = 1% TO NUM_MACROS%
1064     IF OP$ = MACRO_NAME$(M%) THEN GOTO 1080
1066 NEXT M%
1068 GOTO 1090
1080 IF QUEUED_CMD$ = "" THEN LET QUEUED_CMD$ = MACRO_BODY$(M%) ELSE LET QUEUED_CMD$ = MACRO_BODY$(M%) + ";" + QUEUED_CMD$
1085 GOTO 740

1090 PRINT "?Unrecognized command: "; OP$; " (type HELP for reference)"
1095 GOTO 740

1100 ! ==============================================================================
1110 ! TYPE Command (T [range])
1120 ! ==============================================================================
1130 IF N% > 0% THEN GOTO 1150
1135 PRINT "  (Buffer is empty)"
1140 GOTO 740
1150 LET ST% = CUR%
1155 LET EN% = CUR%
1160 IF ARG$ = "" THEN GOTO 1240
1170 IF ARG$ = "." THEN GOTO 1240
1180 IF ARG$ = "WHOLE" THEN GOTO 1195
1185 IF ARG$ = "*" THEN GOTO 1195
1190 GOTO 1200
1195 LET ST% = 1%
1196 LET EN% = N%
1197 GOTO 1240
1200 LET POS% = INSTR(ARG$, ":")
1205 IF POS% > 0% THEN GOTO 1220
1210 LET ST% = VAL(ARG$)
1212 LET EN% = ST%
1214 GOTO 1240
1220 LET ST% = VAL(LEFT$(ARG$, POS% - 1%))
1230 LET EN% = VAL(RIGHT$(ARG$, POS% + 1%))
1240 IF ST% < 1% THEN LET ST% = 1%
1250 IF EN% > N% THEN LET EN% = N%
1260 FOR I% = ST% TO EN%
1270     IF I% = CUR% THEN PRINT ">"; ELSE PRINT " ";
1280     PRINT USING "####  "; I%;
1290     PRINT L$(I%)
1300 NEXT I%
1310 LET CUR% = EN%
1320 GOTO 740

1340 ! ==============================================================================
1350 ! INSERT Command (I [line])
1360 ! ==============================================================================
1370 LET POS% = CUR%
1380 IF ARG$ <> "" THEN LET POS% = VAL(ARG$)
1390 IF POS% < 1% THEN LET POS% = 1%
1400 IF POS% > N% + 1% THEN LET POS% = N% + 1%
1410 PRINT "Entering Insert Mode. Enter text; end with '.' or Ctrl-Z on empty line."
1415 IF QUEUED_CMD$ <> "" THEN GOTO 1424
1420 PRINT "? ";
1430 INPUT INP$
1435 GOTO 1440
1424 LET M% = INSTR(QUEUED_CMD$, ";")
1425 IF M% > 0% THEN GOTO 1427
1426 LET INP$ = QUEUED_CMD$
14261 LET QUEUED_CMD$ = ""
14262 GOTO 1440
1427 LET INP$ = LEFT$(QUEUED_CMD$, M% - 1%)
1428 LET QUEUED_CMD$ = RIGHT$(QUEUED_CMD$, M% + 1%)
1429 GOTO 1440
1440 IF INP$ = "." THEN GOTO 1550
1450 IF INP$ = "^Z" THEN GOTO 1550
1460 IF LEN(INP$) = 1% AND ASCII(INP$) = 26% THEN GOTO 1550
1465 IF N% < 499% THEN GOTO 1480
1470 PRINT "?Buffer full"
1475 GOTO 1550
1480 IF N% < POS% THEN GOTO 1490
1481 LET J% = N%
1482 IF J% < POS% THEN GOTO 1490
1484 LET L$(J% + 1%) = L$(J%)
1485 LET J% = J% - 1%
1486 GOTO 1482
1490 LET L$(POS%) = INP$
1500 LET N% = N% + 1%
1510 LET CUR% = POS%
1520 LET POS% = POS% + 1%
1530 LET MODIFIED% = 1%
1540 GOTO 1415

1550 PRINT "[End of insertion]"
1560 GOTO 740

1580 ! ==============================================================================
1590 ! DELETE Command (D [range])
1600 ! ==============================================================================
1610 IF N% > 0% THEN GOTO 1620
1612 PRINT "?Buffer is empty"
1614 GOTO 740
1620 LET ST% = CUR%
1630 LET EN% = CUR%
1640 IF ARG$ = "" THEN GOTO 1730
1650 IF ARG$ = "." THEN GOTO 1730
1660 IF ARG$ = "WHOLE" THEN GOTO 1665
1662 GOTO 1670
1665 LET ST% = 1%
1666 LET EN% = N%
1667 GOTO 1730
1670 LET POS% = INSTR(ARG$, ":")
1675 IF POS% > 0% THEN GOTO 1690
1680 LET ST% = VAL(ARG$)
1682 LET EN% = ST%
1684 GOTO 1730
1690 LET ST% = VAL(LEFT$(ARG$, POS% - 1%))
1700 LET EN% = VAL(RIGHT$(ARG$, POS% + 1%))

1730 IF ST% < 1% THEN LET ST% = 1%
1740 IF EN% > N% THEN LET EN% = N%
1745 IF ST% <= EN% THEN GOTO 1760
1750 PRINT "?Invalid range"
1755 GOTO 740
1760 LET CNT% = EN% - ST% + 1%

1770 FOR J% = EN% + 1% TO N%
1780     LET L$(J% - CNT%) = L$(J%)
1790 NEXT J%
1800 LET N% = N% - CNT%
1810 IF CUR% > N% THEN LET CUR% = N%
1820 IF CUR% < 1% AND N% > 0% THEN LET CUR% = 1%
1830 LET MODIFIED% = 1%
1840 PRINT "["; CNT%; " line(s) deleted]"
1845 IF REPL_MODE% = 1% THEN GOTO 1860
1850 GOTO 740
1860 LET REPL_MODE% = 0%
1870 GOTO 1340

1880 ! ==============================================================================
1890 ! REPLACE Command (R [range])
1900 ! ==============================================================================
1910 IF N% = 0% THEN GOTO 1340
1920 LET REPL_MODE% = 1%
1930 GOTO 1610

1960 ! ==============================================================================
1970 ! FIND Command (F <target>)
1980 ! ==============================================================================
1990 IF N% > 0% THEN GOTO 2000
1992 PRINT "?Buffer is empty"
1994 GOTO 740
2000 IF ARG$ <> "" THEN GOTO 2010
2002 PRINT "?Target missing"
2004 GOTO 740
2010 LET ST% = VAL(ARG$)
2015 IF ST% <= 0% THEN GOTO 2030
2020 LET CUR% = ST%
2025 GOTO 1240

2030 LET CNT% = 0%
2040 FOR I% = CUR% TO N%
2045     IF INSTR(L$(I%), ARG$) > 0% THEN GOTO 2055
2050 NEXT I%
2052 GOTO 2070
2055 LET CUR% = I%
2056 LET CNT% = 1%
2058 GOTO 2110
2070 IF CUR% <= 1% THEN GOTO 2100
2072 FOR I% = 1% TO CUR% - 1%
2075     IF INSTR(L$(I%), ARG$) > 0% THEN GOTO 2085
2080 NEXT I%
2082 GOTO 2100
2085 LET CUR% = I%
2086 LET CNT% = 1%
2088 GOTO 2110
2100 PRINT "?String not found: "; ARG$
2105 GOTO 740
2110 PRINT ">";
2120 PRINT USING "####  "; CUR%;
2130 PRINT L$(CUR%)
2140 GOTO 740

2170 ! ==============================================================================
2180 ! SUBSTITUTE Command (S /old/new/)
2190 ! ==============================================================================
2200 IF N% > 0% THEN GOTO 2210
2202 PRINT "?Buffer is empty"
2204 GOTO 740
2210 IF LEN(ARG$) >= 3% THEN GOTO 2220
2212 PRINT "?Syntax: S /old/new/"
2214 GOTO 740
2220 LET T1$ = LEFT$(ARG$, 1%)
2230 LET POS% = INSTR(2%, ARG$, T1$)
2235 IF POS% > 0% THEN GOTO 2250
2240 PRINT "?Missing second delimiter"
2245 GOTO 740
2250 LET OLD$ = MID$(ARG$, 2%, POS% - 2%)
2260 LET T2$ = RIGHT$(ARG$, POS% + 1%)
2270 LET POS% = INSTR(T2$, T1$)
2275 IF POS% > 0% THEN GOTO 2280
2277 LET NEW$ = T2$
2278 GOTO 2290
2280 LET NEW$ = LEFT$(T2$, POS% - 1%)
2290 IF CUR% < 1% THEN LET CUR% = 1%
2300 LET POS% = INSTR(L$(CUR%), OLD$)
2305 IF POS% > 0% THEN GOTO 2320
2310 PRINT "?String not found in current line"
2315 GOTO 740

2320 LET T1$ = LEFT$(L$(CUR%), POS% - 1%)
2330 LET T2$ = RIGHT$(L$(CUR%), POS% + LEN(OLD$))
2340 LET L$(CUR%) = T1$ + NEW$ + T2$
2350 LET MODIFIED% = 1%
2360 PRINT ">";
2370 PRINT USING "####  "; CUR%;
2380 PRINT L$(CUR%)
2390 GOTO 740

2420 ! ==============================================================================
2430 ! RESEQUENCE Command
2440 ! ==============================================================================
2450 PRINT "[Buffer resequenced: 1 to "; N%; "]"
2460 GOTO 740

2470 ! ==============================================================================
2480 ! SHOW Command (SHOW, SHOW KEY, SHOW MACRO)
2490 ! ==============================================================================
2492 IF ARG$ = "KEY" THEN GOTO 2520
2494 IF ARG$ = "KEYS" THEN GOTO 2520
2496 IF ARG$ = "MACRO" THEN GOTO 2550
2498 IF ARG$ = "MACROS" THEN GOTO 2550
2500 PRINT "EDT Session Information:"
2502 PRINT "  Current File:    "; F$
2504 PRINT "  Total Lines:     "; N%
2506 PRINT "  Current Line:    "; CUR%
2508 PRINT "  Buffer Modified: ";
2510 IF MODIFIED% = 1% THEN PRINT "YES" ELSE PRINT "NO"
2512 PRINT "  Defined Keys:    "; NUM_KEYS%
2514 PRINT "  Defined Macros:  "; NUM_MACROS%
2516 PRINT "  Terminal Mode:   VT100 Video Terminal"
2518 GOTO 740

2520 ! SHOW KEY
2522 IF NUM_KEYS% > 0% THEN GOTO 2530
2525 PRINT "  (No user keys defined)"
2528 GOTO 740
2530 FOR I% = 1% TO NUM_KEYS%
2532     PRINT "  KEY "; KEY_SPEC$(I%); " AS '"; KEY_DEF$(I%); "'"
2535 NEXT I%
2540 GOTO 740

2550 ! SHOW MACRO
2552 IF NUM_MACROS% > 0% THEN GOTO 2560
2555 PRINT "  (No user macros defined)"
2558 GOTO 740
2560 FOR I% = 1% TO NUM_MACROS%
2562     PRINT "  MACRO "; MACRO_NAME$(I%); " AS '"; MACRO_BODY$(I%); "'"
2565 NEXT I%
2570 GOTO 740

2580 ! ==============================================================================
2590 ! HELP Command
2600 ! ==============================================================================
2610 PRINT "=================================================================="
2620 PRINT "                   DEC RSTS/E EDT COMMAND SUMMARY                 "
2630 PRINT "=================================================================="
2640 PRINT "Line Mode Commands (* prompt):"
2650 PRINT "  TYPE, T [range]       Display lines (e.g., T, T ., T 1:10, T WHOLE)"
2660 PRINT "  INSERT, I [line]      Insert text before line; exit with '.' or ^Z"
2670 PRINT "  DELETE, D [range]     Delete lines (e.g., D, D 5, D 1:10, D WHOLE)"
2680 PRINT "  REPLACE, R [range]    Delete lines and insert new text"
2690 PRINT "  FIND, F <arg>         Search text string or jump to line number"
2700 PRINT "  SUBSTITUTE, S /o/n/   Substitute 'o' with 'n' in current line"
2710 PRINT "  RESEQ                 Renumber line references"
2715 PRINT "  DEFINE KEY <k> AS 'cmd' Define keyboard shortcut/keypad macro"
2720 PRINT "  DEFINE MACRO <m> AS '..' Define named command sequence macro"
2725 PRINT "  SHOW [KEY|MACRO]      Display session, keys, or macro definitions"
2730 PRINT "  CHANGE, C             Enter full-screen VT100 keypad mode"
2735 PRINT "  @file                 Execute commands from command file"
2740 PRINT "  WRITE, W [file]       Write buffer contents to file without exit"
2750 PRINT "  EXIT, EX              Save buffer to file and exit"
2760 PRINT "  QUIT, QU              Exit immediately without saving"
2770 PRINT "=================================================================="
2780 GOTO 740

2790 ! ==============================================================================
2800 ! WRITE / SAVE Command (W [file])
2810 ! ==============================================================================
2820 IF ARG$ <> "" THEN LET F$ = ARG$
2830 OPEN F$ FOR OUTPUT AS FILE #2%
2840 FOR I% = 1% TO N%
2850     PRINT #2%, L$(I%)
2860 NEXT I%
2870 CLOSE #2%
2880 LET MODIFIED% = 0%
2890 PRINT "["; N%; " lines written to file: "; F$; "]"
2900 GOTO 740

2910 ! ==============================================================================
2920 ! EXIT Command (Save and Exit)
2930 ! ==============================================================================
2940 OPEN F$ FOR OUTPUT AS FILE #2%
2950 FOR I% = 1% TO N%
2960     PRINT #2%, L$(I%)
2970 NEXT I%
2980 CLOSE #2%
2990 PRINT "[File "; F$; " written, "; N%; " lines]"
3000 PRINT "EDT session complete."
3010 END

3020 ! ==============================================================================
3030 ! QUIT Command (Exit without Save)
3040 ! ==============================================================================
3050 IF MODIFIED% = 1% THEN PRINT "[Warning: unsaved changes will be lost]"
3060 PRINT "EDT aborted."
3070 END

3200 ! ==============================================================================
3210 ! DEFINE Command (DEF / DEFINE KEY or DEFINE MACRO)
3220 ! ==============================================================================
3230 IF ARG$ = "" THEN GOTO 3240
3235 LET POS% = INSTR(ARG$, " ")
3238 IF POS% > 0% THEN GOTO 3250
3240 PRINT "?Syntax: DEFINE KEY <key> AS 'cmds' or DEFINE MACRO <name> AS 'cmds'"
3245 GOTO 740
3250 LET SUBTYPE$ = LEFT$(ARG$, POS% - 1%)
3255 LET REST$ = RIGHT$(ARG$, POS% + 1%)
3260 IF SUBTYPE$ = "KEY" THEN GOTO 3300
3265 IF SUBTYPE$ = "MACRO" THEN GOTO 3350
3270 PRINT "?Unknown definition type: "; SUBTYPE$; " (expected KEY or MACRO)"
3275 GOTO 740

3300 ! DEFINE KEY <spec> AS "<cmds>"
3305 LET POS% = INSTR(REST$, " AS ")
3310 IF POS% > 0% THEN GOTO 3320
3315 PRINT "?Missing AS clause in DEFINE KEY"
3318 GOTO 740
3320 LET KSPEC$ = LEFT$(REST$, POS% - 1%)
3322 LET KCMD$ = RIGHT$(REST$, POS% + 4%)
3323 IF LEFT$(KCMD$, 1%) = CHR$(34%) THEN LET KCMD$ = RIGHT$(KCMD$, 2%)
3324 IF LEFT$(KCMD$, 1%) = "'" THEN LET KCMD$ = RIGHT$(KCMD$, 2%)
3325 IF RIGHT$(KCMD$, LEN(KCMD$)) = CHR$(34%) THEN LET KCMD$ = LEFT$(KCMD$, LEN(KCMD$) - 1%)
3326 IF RIGHT$(KCMD$, LEN(KCMD$)) = "'" THEN LET KCMD$ = LEFT$(KCMD$, LEN(KCMD$) - 1%)
3330 IF NUM_KEYS% <= 0% THEN GOTO 3340
3332 FOR I% = 1% TO NUM_KEYS%
3334     IF KEY_SPEC$(I%) = KSPEC$ THEN GOTO 3338
3336 NEXT I%
3337 GOTO 3340
3338 LET KEY_DEF$(I%) = KCMD$
3339 GOTO 3345
3340 IF NUM_KEYS% < 50% THEN GOTO 3342
3341 PRINT "?Key table full"
33411 GOTO 740
3342 LET NUM_KEYS% = NUM_KEYS% + 1%
3343 LET KEY_SPEC$(NUM_KEYS%) = KSPEC$
3344 LET KEY_DEF$(NUM_KEYS%) = KCMD$
3345 PRINT "[Key '"; KSPEC$; "' defined]"
3348 GOTO 740

3350 ! DEFINE MACRO <name> AS "<cmds>"
3355 LET POS% = INSTR(REST$, " AS ")
3360 IF POS% > 0% THEN GOTO 3370
3365 PRINT "?Missing AS clause in DEFINE MACRO"
3368 GOTO 740
3370 LET MNAME$ = LEFT$(REST$, POS% - 1%)
3372 LET MCMD$ = RIGHT$(REST$, POS% + 4%)
3373 IF LEFT$(MCMD$, 1%) = CHR$(34%) THEN LET MCMD$ = RIGHT$(MCMD$, 2%)
3374 IF LEFT$(MCMD$, 1%) = "'" THEN LET MCMD$ = RIGHT$(MCMD$, 2%)
3375 IF RIGHT$(MCMD$, LEN(MCMD$)) = CHR$(34%) THEN LET MCMD$ = LEFT$(MCMD$, LEN(MCMD$) - 1%)
3376 IF RIGHT$(MCMD$, LEN(MCMD$)) = "'" THEN LET MCMD$ = LEFT$(MCMD$, LEN(MCMD$) - 1%)
3380 IF NUM_MACROS% <= 0% THEN GOTO 3390
3382 FOR I% = 1% TO NUM_MACROS%
3384     IF MACRO_NAME$(I%) = MNAME$ THEN GOTO 3388
3386 NEXT I%
3387 GOTO 3390
3388 LET MACRO_BODY$(I%) = MCMD$
3389 GOTO 3395
3390 IF NUM_MACROS% < 25% THEN GOTO 3392
3391 PRINT "?Macro table full"
33911 GOTO 740
3392 LET NUM_MACROS% = NUM_MACROS% + 1%
3393 LET MACRO_NAME$(NUM_MACROS%) = MNAME$
3394 LET MACRO_BODY$(NUM_MACROS%) = MCMD$
3395 PRINT "[Macro '"; MNAME$; "' defined]"
3398 GOTO 740

3400 ! ==============================================================================
3410 ! @filename Command Procedure Execution
3420 ! ==============================================================================
3425 LET CFILE$ = RIGHT$(CMD$, 2%)
3430 IF CFILE$ <> "" THEN GOTO 3435
3432 PRINT "?File specification missing"
3434 GOTO 740
3435 ON ERROR GOTO 3460
3440 OPEN CFILE$ FOR INPUT AS FILE #3%
3445 LINE INPUT #3%, INP$
3448 IF INP$ = "" THEN GOTO 3445
3450 IF QUEUED_CMD$ = "" THEN LET QUEUED_CMD$ = INP$ ELSE LET QUEUED_CMD$ = QUEUED_CMD$ + ";" + INP$
3452 GOTO 3445
3455 CLOSE #3%
3458 GOTO 740
3460 CLOSE #3%
3462 ON ERROR GOTO 9900
3465 GOTO 740

4000 ! ==============================================================================
4010 ! Full-Screen VT100 Screen Mode (CHANGE / C)
4020 ! ==============================================================================
4030 PRINT "\033[2J\033[H";
4040 PRINT "\033[7m  DEC RSTS/E EDT SCREEN MODE (VT100) -- CHANGE MODE  \033[0m"
4050 PRINT ""

4060 LET TOP% = CUR% - 8%
4070 IF TOP% < 1% THEN LET TOP% = 1%
4080 LET BOT% = TOP% + 15%
4090 IF BOT% > N% THEN LET BOT% = N%

4100 FOR I% = TOP% TO BOT%
4110     IF I% = CUR% THEN PRINT "\033[7m"; ELSE PRINT "  ";
4120     PRINT USING "####  "; I%;
4130     PRINT L$(I%);
4140     IF I% = CUR% THEN PRINT "\033[0m" ELSE PRINT ""
4150 NEXT I%

4160 PRINT ""
4170 PRINT "\033[7m[EDT] File: "; F$; " | Line: "; CUR%; "/"; N%; " | [P]rev [N]ext [I]ns [D]el [Q/^Z]Exit\033[0m"

4180 LET K$ = INKEY$
4190 IF K$ = "" THEN GOTO 4180
4200 LET K% = ASCII(K$)

4210 IF K% = 26% THEN GOTO 4500
4220 IF K$ = "Q" OR K$ = "q" OR K% = 27% THEN GOTO 4500

4230 ! Check for GOLD key (G, g, or Ctrl-G (ascii 7))
4232 IF K$ = "G" OR K$ = "g" OR K% = 7% THEN GOTO 4240
4235 GOTO 4250
4240 LET GOLD_ACTIVE% = 1%
4242 PRINT "\033[7m[GOLD]\033[0m ";
4245 GOTO 4180

4250 ! Check if a key macro is defined for this key
4251 IF GOLD_ACTIVE% = 1% THEN GOTO 4254
4252 LET LOOKUP_KEY$ = K$
4253 GOTO 4256
4254 LET LOOKUP_KEY$ = "GOLD " + K$
4255 LET GOLD_ACTIVE% = 0%
4256 IF NUM_KEYS% <= 0% THEN GOTO 4260
4257 FOR I% = 1% TO NUM_KEYS%
4258     IF KEY_SPEC$(I%) = LOOKUP_KEY$ THEN GOTO 4450
4259 NEXT I%

4260 IF K$ = "N" OR K$ = "n" OR K$ = "J" OR K$ = "j" OR K% = 10% OR K% = 13% THEN GOTO 4300
4270 IF K$ = "P" OR K$ = "p" OR K$ = "K" OR K$ = "k" THEN GOTO 4330
4280 IF K$ = "D" OR K$ = "d" OR K% = 4% THEN GOTO 4360
4290 IF K$ = "I" OR K$ = "i" OR K$ = "A" OR K$ = "a" THEN GOTO 4410
4295 GOTO 4000

4300 IF CUR% < N% THEN LET CUR% = CUR% + 1%
4310 GOTO 4000

4330 IF CUR% > 1% THEN LET CUR% = CUR% - 1%
4340 GOTO 4000

4360 IF N% = 0% THEN GOTO 4000
4362 FOR J% = CUR% + 1% TO N%
4364     LET L$(J% - 1%) = L$(J%)
4366 NEXT J%
4368 LET N% = N% - 1%
4370 IF CUR% > N% THEN LET CUR% = N%
4372 LET MODIFIED% = 1%
4374 GOTO 4000

4410 PRINT ""
4412 INPUT "Insert text: "; INP$
4414 IF INP$ = "" THEN GOTO 4000
4416 IF N% >= 499% THEN GOTO 4000
4418 IF N% < CUR% THEN GOTO 4424
4419 LET J% = N%
4420 IF J% < CUR% THEN GOTO 4424
4421 LET L$(J% + 1%) = L$(J%)
4422 LET J% = J% - 1%
4423 GOTO 4420
4424 LET CUR% = CUR% + 1%
4426 LET L$(CUR%) = INP$
4428 LET N% = N% + 1%
4430 LET MODIFIED% = 1%
4432 GOTO 4000

4450 ! Execute Key Macro from Screen Mode
4452 LET QUEUED_CMD$ = KEY_DEF$(I%) + "; C"
4456 GOTO 4500

4500 PRINT "\033[2J\033[H";
4510 PRINT "[Exited screen mode, returned to line mode]"
4520 GOTO 740

9900 PRINT "?EDT-F-SYSFATAL, internal error code "; ERR
9910 RESUME 740
