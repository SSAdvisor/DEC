10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_KEY$(15%) \ DIM R_NAME$(15%) \ DIM R_REG$(15%) \ DIM R_VAL%(15%)
20 NUM_REC% = 0% \ SORT_ORD$ = "ASC" \ DB_FILE$ = "FSORT.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    EG&H FSORT3 & VSELECT V3.5 - High-Speed Sort & Record Selection" \ PRINT "    Evans Griffiths & Hart, Inc. (Lexington, MA) - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load records, SORT, VSELECT, LIST, or EXIT." \ PRINT ""
100 PRINT "FSORT3> "; \ LINE INPUT RAW_INPUT$
110 IF LEN(RAW_INPUT$) = 0% THEN GOTO 3400
120 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 26% THEN GOTO 3400
130 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 0% THEN GOTO 3400
140 T_IN$ = RAW_INPUT$ \ GOSUB 500
150 IF T_OUT$ = "" THEN GOTO 100
160 SC_REM$ = T_OUT$
170 IF SC_REM$ = "" THEN GOTO 230
180 SC_P% = INSTR(1%, SC_REM$, ";")
190 IF SC_P% = 0% THEN GOTO 210
200 RAW_CMD$ = LEFT$(SC_REM$, SC_P% - 1%) \ SC_REM$ = MID$(SC_REM$, SC_P% + 1%, LEN(SC_REM$) - SC_P%) \ GOTO 220
210 RAW_CMD$ = SC_REM$ \ SC_REM$ = ""
220 GOSUB 250 \ GOTO 170
230 IF IS_BATCH% = 1% THEN GOTO 3400
240 GOTO 100
250 T_IN$ = RAW_CMD$ \ GOSUB 500 \ WORK_CMD$ = T_OUT$
260 IF WORK_CMD$ = "" THEN GOTO 495
270 SP% = INSTR(1%, WORK_CMD$, " ")
280 IF SP% = 0% THEN GOTO 300
290 VERB$ = LEFT$(WORK_CMD$, SP% - 1%) \ ARGS$ = MID$(WORK_CMD$, SP% + 1%, LEN(WORK_CMD$) - SP%) \ GOTO 310
300 VERB$ = WORK_CMD$ \ ARGS$ = ""
310 U_IN$ = VERB$ \ GOSUB 580 \ VERB$ = U_OUT$ \ T_IN$ = ARGS$ \ GOSUB 500 \ ARGS$ = T_OUT$
320 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "BYE" THEN GOTO 3400
330 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 3000
340 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 700
350 IF VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "SORT" OR VERB$ = "FSORT3" THEN GOTO 960
370 IF VERB$ = "VSELECT" OR VERB$ = "SELECT" THEN GOTO 1200
380 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
390 IF VERB$ = "SAVE" THEN GOTO 1550
400 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
420 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "FSORT3: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ SORT_ORD$ = "UNSORTED"
710 R_KEY$(1%) = "K-300" \ R_NAME$(1%) = "Maynard Mill Ops   " \ R_REG$(1%) = "EAST" \ R_VAL%(1%) = 750%
720 R_KEY$(2%) = "K-100" \ R_NAME$(2%) = "Salem Assembly Plt " \ R_REG$(2%) = "EAST" \ R_VAL%(2%) = 320%
730 R_KEY$(3%) = "K-400" \ R_NAME$(3%) = "Colorado Springs   " \ R_REG$(3%) = "WEST" \ R_VAL%(3%) = 980%
740 R_KEY$(4%) = "K-200" \ R_NAME$(4%) = "Marlboro Cluster   " \ R_REG$(4%) = "EAST" \ R_VAL%(4%) = 540%
750 PRINT "[Sample EG&H FSORT3 dataset loaded - 4 RMS records]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  EG&H FSORT3 Buffer (Order: "; SORT_ORD$; ") — File: "; DB_FILE$ \ PRINT SEP$
840 PRINT "  Seq   Key     Facility Name          Region   Value($K)" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_REC% THEN GOTO 920
870 K_P$ = LEFT$(R_KEY$(LI%) + BLANKS$, 6%) \ N_P$ = LEFT$(R_NAME$(LI%) + BLANKS$, 21%) \ G_P$ = LEFT$(R_REG$(LI%) + BLANKS$, 7%)
880 PRINT "  "; LI%; "     "; K_P$; "  "; N_P$; "  "; G_P$; "  "; R_VAL%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_REC% = 0% THEN GOTO 3370
970 S_DIR$ = "ASC"
980 IF ARGS$ <> "" THEN U_IN$ = ARGS$
985 IF ARGS$ <> "" THEN GOSUB 580
990 IF ARGS$ <> "" THEN S_DIR$ = U_OUT$
1000 SI% = 1%
1010 IF SI% >= NUM_REC% THEN GOTO 1150
1020 SJ% = SI% + 1%
1030 IF SJ% > NUM_REC% THEN GOTO 1140
1040 DO_SWP% = 0%
1050 IF S_DIR$ = "DESC" AND R_VAL%(SJ%) > R_VAL%(SI%) THEN DO_SWP% = 1%
1060 IF S_DIR$ <> "DESC" AND R_VAL%(SJ%) < R_VAL%(SI%) THEN DO_SWP% = 1%
1070 IF DO_SWP% = 0% THEN GOTO 1130
1080 TK$ = R_KEY$(SI%) \ R_KEY$(SI%) = R_KEY$(SJ%) \ R_KEY$(SJ%) = TK$
1090 TN$ = R_NAME$(SI%) \ R_NAME$(SI%) = R_NAME$(SJ%) \ R_NAME$(SJ%) = TN$
1100 TR$ = R_REG$(SI%) \ R_REG$(SI%) = R_REG$(SJ%) \ R_REG$(SJ%) = TR$
1110 TV% = R_VAL%(SI%) \ R_VAL%(SI%) = R_VAL%(SJ%) \ R_VAL%(SJ%) = TV%
1130 SJ% = SJ% + 1% \ GOTO 1030
1140 SI% = SI% + 1% \ GOTO 1010
1150 SORT_ORD$ = S_DIR$
1160 PRINT "[EG&H FSORT3 High-Speed Sort Complete: "; NUM_REC%; " records sorted "; S_DIR$; " by Value (First="; R_KEY$(1%); ":"; R_VAL%(1%); "K)]" \ GOTO 495
1200 IF NUM_REC% = 0% THEN GOTO 3370
1210 MIN_V% = 500%
1220 IF ARGS$ <> "" THEN MIN_V% = VAL(ARGS$)
1230 PRINT EQU$ \ PRINT "  EG&H VSELECT — Boolean Record Selection (Criteria: VALUE >= "; MIN_V%; "K)" \ PRINT SEP$
1240 VI% = 1% \ V_CNT% = 0% \ V_SUM% = 0%
1250 IF VI% > NUM_REC% THEN GOTO 1320
1260 IF R_VAL%(VI%) < MIN_V% THEN GOTO 1310
1270 V_CNT% = V_CNT% + 1% \ V_SUM% = V_SUM% + R_VAL%(VI%)
1280 K_P$ = LEFT$(R_KEY$(VI%) + BLANKS$, 6%) \ N_P$ = LEFT$(R_NAME$(VI%) + BLANKS$, 21%)
1290 PRINT "  MATCH #"; V_CNT%; ": "; K_P$; "  "; N_P$; "  Region="; R_REG$(VI%); "  Val=$"; R_VAL%(VI%); "K"
1310 VI% = VI% + 1% \ GOTO 1250
1320 PRINT SEP$ \ PRINT "  [VSELECT Selected "; V_CNT%; " of "; NUM_REC%; " records | Projected Sum = $"; V_SUM%; "K]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_REC% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ K_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ N_V$ = T_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ G_V$ = U_OUT$
1480 VL_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_REC% = NUM_REC% + 1% \ R_KEY$(NUM_REC%) = K_V$ \ R_NAME$(NUM_REC%) = N_V$ \ R_REG$(NUM_REC%) = G_V$ \ R_VAL%(NUM_REC%) = VL_V%
1495 PRINT "[FSORT3 Record #"; NUM_REC%; " added: "; K_V$; " ("; N_V$; ", Val="; VL_V%; "K)]" \ GOTO 495
1500 PRINT "FSORT3: Syntax is ADD <key>, <name>, <region>, <val_k>" \ GOTO 495
1510 PRINT "FSORT3: Buffer full" \ GOTO 495
1550 IF NUM_REC% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_REC% THEN GOTO 1630
1600 PRINT #2%, R_KEY$(SI%); "|"; R_NAME$(SI%); "|"; R_REG$(SI%); "|"; R_VAL%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_REC%; " FSORT3 records saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FK$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FN$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FG$ = LEFT$(REM2$, P3% - 1%) \ FV% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_REC% = NUM_REC% + 1% \ R_KEY$(NUM_REC%) = FK$ \ R_NAME$(NUM_REC%) = FN$ \ R_REG$(NUM_REC%) = FG$ \ R_VAL%(NUM_REC%) = FV% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " FSORT3 records loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "EG&H FSORT3 & VSELECT V3.5 Status:" \ PRINT "  Active File:    "; DB_FILE$; " (Records: "; NUM_REC%; ", Order: "; SORT_ORD$; ")" \ GOTO 495
2050 NUM_REC% = 0% \ PRINT "[FSORT3 buffer cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    EG&H FSORT3 & VSELECT V3.5 Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample RMS records" \ PRINT "  LIST / DISPLAY                   Display records in current order"
3020 PRINT "  SORT [ASC|DESC] / FSORT3         High-speed multi-key sort" \ PRINT "  VSELECT [min_val] / SELECT       Boolean record selection & projection"
3030 PRINT "  ADD <key>, <name>, <reg>, <val>  Add record to buffer" \ PRINT "  SAVE [file] / LOAD [file]        Save or load FSORT.DAT file"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear buffer, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "FSORT3: Buffer is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
