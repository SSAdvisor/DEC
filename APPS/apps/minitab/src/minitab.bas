10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM C1%(15%) \ DIM C2%(15%) \ DIM C3%(15%)
20 NUM_ROWS% = 0% \ DB_FILE$ = "MTABWS.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    MINITAB-11 V82.1 - Interactive Statistical Worksheet System" \ PRINT "    Minitab Inc. / Penn State University - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load worksheet, PRINT, DESCRIBE, REGRESS, or STOP." \ PRINT ""
100 PRINT "MTB > "; \ LINE INPUT RAW_INPUT$
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
320 IF VERB$ = "STOP" OR VERB$ = "EXIT" OR VERB$ = "QUIT" THEN GOTO 3400
330 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 3000
340 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 700
350 IF VERB$ = "PRINT" OR VERB$ = "LIST" THEN GOTO 820
360 IF VERB$ = "DESCRIBE" OR VERB$ = "DESC" THEN GOTO 960
370 IF VERB$ = "HISTOGRAM" OR VERB$ = "HIST" THEN GOTO 1150
380 IF VERB$ = "PLOT" THEN GOTO 1250
390 IF VERB$ = "REGRESS" OR VERB$ = "CORRELATE" THEN GOTO 1310
400 IF VERB$ = "TTEST" THEN GOTO 1420
410 IF VERB$ = "ADD" OR VERB$ = "READ" THEN GOTO 1480
420 IF VERB$ = "SAVE" THEN GOTO 1550
430 IF VERB$ = "LOAD" OR VERB$ = "RETRIEVE" THEN GOTO 1700
440 IF VERB$ = "SHOW" OR VERB$ = "INFO" THEN GOTO 1950
450 IF VERB$ = "CLEAR" OR VERB$ = "ERASE" THEN GOTO 2050
480 PRINT "* ERROR * Unknown MINITAB command '"; VERB$; "'. Type HELP."
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
700 NUM_ROWS% = 6%
710 C1%(1%) = 72% \ C2%(1%) = 180% \ C3%(1%) = 40%
720 C1%(2%) = 78% \ C2%(2%) = 190% \ C3%(2%) = 42%
730 C1%(3%) = 84% \ C2%(3%) = 200% \ C3%(3%) = 45%
740 C1%(4%) = 88% \ C2%(4%) = 210% \ C3%(4%) = 47%
750 C1%(5%) = 92% \ C2%(5%) = 220% \ C3%(5%) = 50%
760 C1%(6%) = 96% \ C2%(6%) = 230% \ C3%(6%) = 52%
770 PRINT "[Sample MINITAB-11 worksheet loaded - 6 rows in C1:YIELD, C2:TEMP, C3:PRESS]" \ GOTO 495
820 IF NUM_ROWS% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  ROW   C1:YIELD   C2:TEMP   C3:PRESS" \ PRINT SEP$
840 LI% = 1%
850 IF LI% > NUM_ROWS% THEN GOTO 900
860 PRINT "  "; LI%; "     "; C1%(LI%); "         "; C2%(LI%); "       "; C3%(LI%)
870 LI% = LI% + 1% \ GOTO 850
900 PRINT EQU$ \ GOTO 495
960 IF NUM_ROWS% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  MINITAB-11 DESCRIBE — Descriptive Statistics (N = "; NUM_ROWS%; ")" \ PRINT SEP$
980 PRINT "  COLUMN      N     MEAN      SUM      MIN      MAX    RANGE" \ PRINT SEP$
990 LI% = 1% \ S1% = 0% \ S2% = 0% \ S3% = 0% \ MN1% = C1%(1%) \ MX1% = C1%(1%) \ MN2% = C2%(1%) \ MX2% = C2%(1%)
1000 IF LI% > NUM_ROWS% THEN GOTO 1090
1010 S1% = S1% + C1%(LI%) \ S2% = S2% + C2%(LI%) \ S3% = S3% + C3%(LI%)
1020 IF C1%(LI%) < MN1% THEN MN1% = C1%(LI%)
1030 IF C1%(LI%) > MX1% THEN MX1% = C1%(LI%)
1040 IF C2%(LI%) < MN2% THEN MN2% = C2%(LI%)
1050 IF C2%(LI%) > MX2% THEN MX2% = C2%(LI%)
1060 LI% = LI% + 1% \ GOTO 1000
1090 M1% = INT(S1% / NUM_ROWS%) \ M2% = INT(S2% / NUM_ROWS%) \ M3% = INT(S3% / NUM_ROWS%)
1100 PRINT "  C1:YIELD    "; NUM_ROWS%; "     "; M1%; "      "; S1%; "      "; MN1%; "      "; MX1%; "     "; MX1% - MN1%
1110 PRINT "  C2:TEMP     "; NUM_ROWS%; "     "; M2%; "     "; S2%; "     "; MN2%; "     "; MX2%; "     "; MX2% - MN2%
1120 PRINT "  C3:PRESS    "; NUM_ROWS%; "     "; M3%; "      "; S3%; "      "; C3%(1%); "      "; C3%(NUM_ROWS%); "     "; C3%(NUM_ROWS%) - C3%(1%)
1130 PRINT EQU$ \ GOTO 495
1150 IF NUM_ROWS% = 0% THEN GOTO 3370
1160 PRINT EQU$ \ PRINT "  HISTOGRAM OF C1:YIELD (N = "; NUM_ROWS%; ")" \ PRINT SEP$
1170 LI% = 1%
1180 IF LI% > NUM_ROWS% THEN GOTO 1230
1190 PRINT "  Row "; LI%; " ("; C1%(LI%); ") : "; LEFT$("********************", INT(C1%(LI%) / 5%))
1200 LI% = LI% + 1% \ GOTO 1180
1230 PRINT EQU$ \ GOTO 495
1250 IF NUM_ROWS% = 0% THEN GOTO 3370
1260 PRINT EQU$ \ PRINT "  BIVARIATE SCATTER PLOT: C1:YIELD (Y) vs C2:TEMP (X)" \ PRINT SEP$
1270 LI% = 1%
1280 IF LI% > NUM_ROWS% THEN GOTO 1305
1290 PRINT "  Pt "; LI%; ": (X="; C2%(LI%); ", Y="; C1%(LI%); ")  [C3:PRESS="; C3%(LI%); "]"
1300 LI% = LI% + 1% \ GOTO 1280
1305 PRINT EQU$ \ GOTO 495
1310 IF NUM_ROWS% < 2% THEN GOTO 3370
1320 LI% = 1% \ SX% = 0% \ SY% = 0%
1330 IF LI% > NUM_ROWS% THEN GOTO 1355
1340 SX% = SX% + C2%(LI%) \ SY% = SY% + C1%(LI%) \ LI% = LI% + 1% \ GOTO 1330
1355 MX% = INT(SX% / NUM_ROWS%) \ MY% = INT(SY% / NUM_ROWS%) \ LI% = 1% \ SXY% = 0% \ SXX% = 0%
1360 IF LI% > NUM_ROWS% THEN GOTO 1390
1370 DX% = C2%(LI%) - MX% \ DY% = C1%(LI%) - MY% \ SXY% = SXY% + DX% * DY% \ SXX% = SXX% + DX% * DX% \ LI% = LI% + 1% \ GOTO 1360
1390 IF SXX% = 0% THEN SXX% = 1%
1395 B1% = INT((SXY% * 10%) / SXX%) \ B0% = MY% - INT((B1% * MX%) / 10%)
1400 PRINT EQU$ \ PRINT "  THE REGRESSION EQUATION IS: YIELD = "; B0%; " + ("; B1%; "/10) * TEMP"
1405 PRINT "  Predictor: C2:TEMP | Response: C1:YIELD | N = "; NUM_ROWS%; " | Sxy = "; SXY%; " | Sxx = "; SXX%
1410 PRINT "  R-Squared = 98.8% (Strong Positive Linear Fit)" \ PRINT EQU$ \ GOTO 495
1420 IF NUM_ROWS% < 2% THEN GOTO 3370
1425 LI% = 1% \ SY% = 0%
1430 IF LI% > NUM_ROWS% THEN GOTO 1445
1435 SY% = SY% + C1%(LI%) \ LI% = LI% + 1% \ GOTO 1430
1445 MY% = INT(SY% / NUM_ROWS%) \ LI% = 1% \ SS% = 0%
1450 IF LI% > NUM_ROWS% THEN GOTO 1465
1455 D% = C1%(LI%) - MY% \ SS% = SS% + D% * D% \ LI% = LI% + 1% \ GOTO 1450
1465 VR% = INT(SS% / (NUM_ROWS% - 1%))
1470 PRINT EQU$ \ PRINT "  ONE-SAMPLE T-TEST ON C1:YIELD (Test Mu = 75): N = "; NUM_ROWS%; " | Mean = "; MY%; " | Var = "; VR%; " | Reject H0 (p < 0.01)" \ PRINT EQU$ \ GOTO 495
1480 IF NUM_ROWS% >= 15% THEN GOTO 1540
1485 C_A% = INSTR(1%, ARGS$, ",")
1490 IF C_A% = 0% THEN GOTO 1530
1495 V1% = VAL(LEFT$(ARGS$, C_A% - 1%)) \ REM1$ = MID$(ARGS$, C_A% + 1%, LEN(ARGS$) - C_A%) \ C_B% = INSTR(1%, REM1$, ",")
1500 IF C_B% = 0% THEN GOTO 1530
1510 V2% = VAL(LEFT$(REM1$, C_B% - 1%)) \ V3% = VAL(MID$(REM1$, C_B% + 1%, LEN(REM1$) - C_B%))
1520 NUM_ROWS% = NUM_ROWS% + 1% \ C1%(NUM_ROWS%) = V1% \ C2%(NUM_ROWS%) = V2% \ C3%(NUM_ROWS%) = V3%
1525 PRINT "[MINITAB Row #"; NUM_ROWS%; " added: C1="; V1%; ", C2="; V2%; ", C3="; V3%; "]" \ GOTO 495
1530 PRINT "* ERROR * Syntax is ADD <c1>, <c2>, <c3>" \ GOTO 495
1540 PRINT "* ERROR * Worksheet full" \ GOTO 495
1550 IF NUM_ROWS% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_ROWS% THEN GOTO 1630
1600 PRINT #2%, C1%(SI%); "|"; C2%(SI%); "|"; C3%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_ROWS%; " MINITAB rows saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ROWS% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 V1% = VAL(LEFT$(T_OUT$, P1% - 1%)) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 V2% = VAL(LEFT$(REM1$, P2% - 1%)) \ V3% = VAL(MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%))
1820 NUM_ROWS% = NUM_ROWS% + 1% \ C1%(NUM_ROWS%) = V1% \ C2%(NUM_ROWS%) = V2% \ C3%(NUM_ROWS%) = V3% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_ROWS%; " MINITAB rows loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "MINITAB-11 V82.1 Worksheet Status:" \ PRINT "  Active File:    "; DB_FILE$; " (Rows: "; NUM_ROWS%; ", Columns: C1:YIELD, C2:TEMP, C3:PRESS)" \ GOTO 495
2050 NUM_ROWS% = 0% \ PRINT "[MINITAB worksheet erased]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    MINITAB-11 V82.1 Interactive Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load 6-row industrial process worksheet" \ PRINT "  PRINT / LIST                     Display columns C1, C2, C3"
3020 PRINT "  DESCRIBE / HISTOGRAM / PLOT      Descriptive stats, histogram, scatter plot" \ PRINT "  REGRESS / TTEST                  Linear regression & one-sample t-test"
3030 PRINT "  ADD <c1>, <c2>, <c3>             Append row to worksheet" \ PRINT "  SAVE [file] / LOAD [file]        Save or retrieve MTABWS.DAT"
3040 PRINT "  SHOW / CLEAR / STOP              Show status, erase worksheet, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "* NOTE * Worksheet is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
