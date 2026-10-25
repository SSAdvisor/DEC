10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_ID$(15%) \ DIM R_NAME$(15%) \ DIM R_DIV$(15%) \ DIM R_SCORE%(15%)
20 NUM_REC% = 0% \ DS_NM$ = "CLIENTS.DMS" \ LAST_HITS% = 0% \ DB_FILE$ = "S1032.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Software House System 1032 VAX/VMS - 4GL & Compressed Bitmap DBMS" \ PRINT "    Software House, Inc. (Cambridge, MA) - VAX/VMS Inverted Bitmap Engine" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load DMS, LIST, FIND, STATS, ADD, or EXIT." \ PRINT ""
100 PRINT "*1032> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "LIST" OR VERB$ = "PRINT" OR VERB$ = "TYPE" THEN GOTO 820
360 IF VERB$ = "FIND" OR VERB$ = "SEARCH" THEN GOTO 960
370 IF VERB$ = "STATS" OR VERB$ = "BITMAP" OR VERB$ = "DENSITY" THEN GOTO 1220
380 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1400
390 IF VERB$ = "SAVE" THEN GOTO 1600
400 IF VERB$ = "LOAD" OR VERB$ = "OPEN" THEN GOTO 1750
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2000
420 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2100
480 PRINT "%S1032-E-INVCMD, unrecognized System 1032 command '"; VERB$; "'. Type HELP."
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
700 NUM_REC% = 4% \ DS_NM$ = "CLIENTS.DMS" \ LAST_HITS% = 4%
710 R_ID$(1%) = "C-101" \ R_NAME$(1%) = "Raytheon Defense  " \ R_DIV$(1%) = "AERO" \ R_SCORE%(1%) = 920%
720 R_ID$(2%) = "C-102" \ R_NAME$(2%) = "Draper Laboratory " \ R_DIV$(2%) = "AERO" \ R_SCORE%(2%) = 850%
730 R_ID$(3%) = "C-103" \ R_NAME$(3%) = "Genetics Inst     " \ R_DIV$(3%) = "BIO " \ R_SCORE%(3%) = 640%
740 R_ID$(4%) = "C-104" \ R_NAME$(4%) = "MIT Lincoln Lab   " \ R_DIV$(4%) = "AERO" \ R_SCORE%(4%) = 980%
750 PRINT "[Sample System 1032 dataset "; DS_NM$; " loaded - 4 records, Bitmap Index built]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  System 1032 Dataset: "; DS_NM$; " — Record Listing" \ PRINT SEP$
840 PRINT "  Rec#   Client ID   Organization Name      Division   Rating" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_REC% THEN GOTO 920
870 ID_P$ = LEFT$(R_ID$(LI%) + BLANKS$, 9%) \ NM_P$ = LEFT$(R_NAME$(LI%) + BLANKS$, 21%) \ DV_P$ = LEFT$(R_DIV$(LI%) + BLANKS$, 8%)
880 PRINT "  "; LI%; "      "; ID_P$; "   "; NM_P$; "  "; DV_P$; "   "; R_SCORE%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_REC% = 0% THEN GOTO 3370
970 F_DIV$ = "AERO"
980 IF ARGS$ <> "" THEN U_IN$ = ARGS$
985 IF ARGS$ <> "" THEN GOSUB 580
990 IF ARGS$ <> "" THEN F_DIV$ = U_OUT$
1000 PRINT EQU$ \ PRINT "  System 1032 Compressed Bitmap FIND — Criteria: DIVISION EQ '"; F_DIV$; "'" \ PRINT SEP$
1010 FI% = 1% \ LAST_HITS% = 0% \ B_VEC$ = "" \ H_SUM% = 0%
1020 IF FI% > NUM_REC% THEN GOTO 1130
1030 T_IN$ = R_DIV$(FI%) \ GOSUB 500 \ D_CLEAN$ = T_OUT$
1040 IF D_CLEAN$ = F_DIV$ THEN GOTO 1070
1050 B_VEC$ = B_VEC$ + "0" \ GOTO 1120
1070 B_VEC$ = B_VEC$ + "1" \ LAST_HITS% = LAST_HITS% + 1% \ H_SUM% = H_SUM% + R_SCORE%(FI%)
1080 ID_P$ = LEFT$(R_ID$(FI%) + BLANKS$, 8%) \ NM_P$ = LEFT$(R_NAME$(FI%) + BLANKS$, 20%)
1090 PRINT "  HIT #"; LAST_HITS%; " [Rec "; FI%; "]: "; ID_P$; "  "; NM_P$; "  Div="; D_CLEAN$; "  Score="; R_SCORE%(FI%)
1120 FI% = FI% + 1% \ GOTO 1020
1130 PRINT SEP$ \ PRINT "  [System 1032 Bitmap Vector: ["; B_VEC$; "] -> "; LAST_HITS%; " records selected (0 Disk Reads, Sum="; H_SUM%; ")]" \ PRINT EQU$ \ GOTO 495
1220 IF NUM_REC% = 0% THEN GOTO 3370
1230 TOT_SC% = 0% \ MAX_SC% = 0% \ SI% = 1%
1240 IF SI% > NUM_REC% THEN GOTO 1290
1250 TOT_SC% = TOT_SC% + R_SCORE%(SI%)
1260 IF R_SCORE%(SI%) > MAX_SC% THEN MAX_SC% = R_SCORE%(SI%)
1270 SI% = SI% + 1% \ GOTO 1240
1290 AVG_SC% = INT(TOT_SC% / NUM_REC%) \ BM_BYTES% = NUM_REC% * 4%
1300 PRINT EQU$ \ PRINT "  System 1032 Compressed Bitmap Index Density & Dataset Statistics" \ PRINT SEP$
1310 PRINT "  Active Dataset       : "; DS_NM$; " (Total Records: "; NUM_REC%; ", Last FIND Selection: "; LAST_HITS%; ")"
1320 PRINT "  Inverted Bitmap Size : "; BM_BYTES%; " bytes (Run-Length Encoded Bit-Vectors on DIV, ID)"
1330 PRINT "  Rating Summary       : Total="; TOT_SC%; " | Mean="; AVG_SC%; " | Peak="; MAX_SC% \ PRINT EQU$ \ GOTO 495
1400 IF NUM_REC% >= 15% THEN GOTO 1560
1410 C1% = INSTR(1%, ARGS$, ",")
1420 IF C1% = 0% THEN GOTO 1550
1430 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ ID_V$ = U_OUT$
1440 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1450 IF C2% = 0% THEN GOTO 1550
1460 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ NM_V$ = T_OUT$
1470 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1480 IF C3% = 0% THEN GOTO 1550
1490 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ DV_V$ = U_OUT$
1500 SC_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1510 NUM_REC% = NUM_REC% + 1% \ R_ID$(NUM_REC%) = ID_V$ \ R_NAME$(NUM_REC%) = NM_V$ \ R_DIV$(NUM_REC%) = DV_V$ \ R_SCORE%(NUM_REC%) = SC_V%
1520 LAST_HITS% = NUM_REC%
1530 PRINT "[System 1032 Record #"; NUM_REC%; " added & Bitmap Index updated: "; ID_V$; " ("; NM_V$; ", "; DV_V$; ", "; SC_V%; ")]" \ GOTO 495
1550 PRINT "System 1032: Syntax is ADD <id>, <name>, <division>, <score>" \ GOTO 495
1560 PRINT "System 1032: Dataset "; DS_NM$; " is full" \ GOTO 495
1600 IF NUM_REC% = 0% THEN GOTO 3370
1610 SV_FILE$ = DB_FILE$
1620 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1630 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1640 IF SI% > NUM_REC% THEN GOTO 1680
1650 PRINT #2%, R_ID$(SI%); "|"; R_NAME$(SI%); "|"; R_DIV$(SI%); "|"; R_SCORE%(SI%)
1660 SI% = SI% + 1% \ GOTO 1640
1680 CLOSE #2% \ PRINT "["; NUM_REC%; " System 1032 records saved to "; SV_FILE$; "]" \ GOTO 495
1750 LD_FILE$ = DB_FILE$
1760 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1770 ON ERROR GOTO 1900 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1780 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1790 IF T_OUT$ = "" THEN GOTO 1780
1800 P1% = INSTR(1%, T_OUT$, "|")
1810 IF P1% = 0% THEN GOTO 1780
1820 FID$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1830 IF P2% = 0% THEN GOTO 1780
1840 FNM$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1850 IF P3% = 0% THEN GOTO 1780
1860 FDV$ = LEFT$(REM2$, P3% - 1%) \ FSC% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1870 NUM_REC% = NUM_REC% + 1% \ R_ID$(NUM_REC%) = FID$ \ R_NAME$(NUM_REC%) = FNM$ \ R_DIV$(NUM_REC%) = FDV$ \ R_SCORE%(NUM_REC%) = FSC% \ GOTO 1780
1900 CLOSE #2% \ RESUME 1910
1910 ON ERROR GOTO 0 \ LAST_HITS% = NUM_REC% \ PRINT "["; NUM_REC%; " System 1032 records loaded from "; LD_FILE$; "]" \ GOTO 495
2000 PRINT "Software House System 1032 Status:" \ PRINT "  Dataset: "; DS_NM$; " | File: "; DB_FILE$; " (Records: "; NUM_REC%; ", Active Selection: "; LAST_HITS%; ")" \ GOTO 495
2100 NUM_REC% = 0% \ LAST_HITS% = 0% \ PRINT "[System 1032 dataset cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Software House System 1032 VAX/VMS Bitmap DBMS Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample CLIENTS.DMS & build bitmaps" \ PRINT "  LIST / PRINT                     Display records in dataset"
3020 PRINT "  FIND [division] / SEARCH         Compressed bitmap inverted-index selection" \ PRINT "  STATS / BITMAP                   Display bitmap index density & statistics"
3030 PRINT "  ADD <id>, <name>, <div>, <score> Add record & update bitmap index" \ PRINT "  SAVE [file] / LOAD [file]        Save or load S1032.DAT dataset"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear dataset, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "%S1032-W-EMPTY, dataset is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
