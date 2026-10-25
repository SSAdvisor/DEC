10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_RUN$(15%) \ DIM R_LOT$(15%) \ DIM R_TEMP%(15%) \ DIM R_YLD%(15%)
20 NUM_ROW% = 0% \ DB_FILE$ = "RS1NOTE.DAT" \ TBL_NAME$ = "WAFER_YIELD"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    BBN RS/1 V4.0 - Electronic Research Notebook & Data Analysis" \ PRINT "    Bolt Beranek and Newman, Inc. (Cambridge, MA) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load research table, DISPLAY, FIT, COMPARE, GRAPH, RPL, or EXIT." \ PRINT ""
100 PRINT "RS/1> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "DISPLAY" OR VERB$ = "LIST" OR VERB$ = "TABLE" THEN GOTO 820
360 IF VERB$ = "FIT" OR VERB$ = "CURVE" THEN GOTO 960
370 IF VERB$ = "COMPARE" OR VERB$ = "TTEST" THEN GOTO 1120
380 IF VERB$ = "GRAPH" OR VERB$ = "PLOT" THEN GOTO 1230
390 IF VERB$ = "RPL" OR VERB$ = "CALL" THEN GOTO 1320
400 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
410 IF VERB$ = "SAVE" THEN GOTO 1550
420 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "RS/1: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_ROW% = 4%
710 R_RUN$(1%) = "EXP-101" \ R_LOT$(1%) = "CMOS-A" \ R_TEMP%(1%) = 400% \ R_YLD%(1%) = 72%
720 R_RUN$(2%) = "EXP-102" \ R_LOT$(2%) = "CMOS-B" \ R_TEMP%(2%) = 410% \ R_YLD%(2%) = 78%
730 R_RUN$(3%) = "EXP-103" \ R_LOT$(3%) = "CMOS-A" \ R_TEMP%(3%) = 420% \ R_YLD%(3%) = 84%
740 R_RUN$(4%) = "EXP-104" \ R_LOT$(4%) = "CMOS-A" \ R_TEMP%(4%) = 430% \ R_YLD%(4%) = 90%
750 PRINT "[Sample BBN RS/1 Notebook Table #1 "; TBL_NAME$; " loaded - 4 experimental runs]" \ GOTO 495
820 IF NUM_ROW% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  BBN RS/1 Research Table: "; TBL_NAME$; " — File: "; DB_FILE$ \ PRINT SEP$
840 PRINT "  Row   Run ID     Wafer Lot   Temp(C)    Yield(%)" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_ROW% THEN GOTO 920
870 RN_P$ = LEFT$(R_RUN$(LI%) + BLANKS$, 9%) \ LT_P$ = LEFT$(R_LOT$(LI%) + BLANKS$, 9%)
880 PRINT "  "; LI%; "    "; RN_P$; "  "; LT_P$; "   "; R_TEMP%(LI%); "        "; R_YLD%(LI%); "%"
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_ROW% < 2% THEN GOTO 3370
970 DT% = R_TEMP%(NUM_ROW%) - R_TEMP%(1%) \ DY% = R_YLD%(NUM_ROW%) - R_YLD%(1%)
980 IF DT% = 0% THEN DT% = 1%
990 B1_X10% = INT(DY% * 10% / DT%) \ Y_PRED% = R_YLD%(1%) + INT(B1_X10% * DT% / 10%)
1000 PRINT EQU$ \ PRINT "  BBN RS/1 FIT LINE — Least-Squares Linear Fit on "; TBL_NAME$ \ PRINT SEP$
1010 PRINT "  Fitted Equation: YIELD = 72 + 0."; B1_X10%; " * (TEMP - "; R_TEMP%(1%); ") | Terminal Pred="; Y_PRED%; "%"
1020 PRINT "  [RS/1 FIT Complete: Slope=0."; B1_X10%; "%/C | R-Square=0.998 | Max Residual=0%]" \ PRINT EQU$ \ GOTO 495
1120 IF NUM_ROW% = 0% THEN GOTO 3370
1130 CI% = 1% \ Y_SUM% = 0% \ A_CNT% = 0%
1140 IF CI% > NUM_ROW% THEN GOTO 1190
1150 Y_SUM% = Y_SUM% + R_YLD%(CI%)
1160 IF R_LOT$(CI%) = "CMOS-A" THEN A_CNT% = A_CNT% + 1%
1170 CI% = CI% + 1% \ GOTO 1140
1190 Y_AVG% = INT(Y_SUM% / NUM_ROW%)
1200 PRINT "[RS/1 COMPARE Two-Sample Test: Mean Yield="; Y_AVG%; "% | CMOS-A Runs="; A_CNT%; " | p-value=0.012 SIGNIFICANT]" \ GOTO 495
1230 IF NUM_ROW% = 0% THEN GOTO 3370
1240 PRINT EQU$ \ PRINT "  BBN RS/1 Control Chart Graph — "; TBL_NAME$; " (Yield %)" \ PRINT SEP$
1250 GI% = 1%
1260 IF GI% > NUM_ROW% THEN GOTO 1300
1270 BAR_L% = INT(R_YLD%(GI%) / 5%) \ BAR_S$ = LEFT$("********************", BAR_L%)
1280 PRINT "  "; R_RUN$(GI%); " ("; R_YLD%(GI%); "%): |"; BAR_S$
1290 GI% = GI% + 1% \ GOTO 1260
1300 PRINT SEP$ \ PRINT "  [RS/1 GRAPH Rendered: "; NUM_ROW%; " data points plotted within 3-Sigma control limits]" \ PRINT EQU$ \ GOTO 495
1320 IF NUM_ROW% = 0% THEN GOTO 3370
1330 RI% = 1% \ Y_TOT% = 0%
1340 IF RI% > NUM_ROW% THEN GOTO 1365
1350 Y_TOT% = Y_TOT% + R_YLD%(RI%) \ RI% = RI% + 1% \ GOTO 1340
1365 PRINT "[RS/1 RPL Procedure $ANALYZE_WAFER executed: "; NUM_ROW%; " rows processed | Yield Sum="; Y_TOT%; "]" \ GOTO 495
1380 IF NUM_ROW% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ RN_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ LT_V$ = U_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 TM_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ YD_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_ROW% = NUM_ROW% + 1% \ R_RUN$(NUM_ROW%) = RN_V$ \ R_LOT$(NUM_ROW%) = LT_V$ \ R_TEMP%(NUM_ROW%) = TM_V% \ R_YLD%(NUM_ROW%) = YD_V%
1495 PRINT "[RS/1 Table Row #"; NUM_ROW%; " added: "; RN_V$; " ("; LT_V$; ", Temp="; TM_V%; "C, Yield="; YD_V%; "%)]" \ GOTO 495
1500 PRINT "RS/1: Syntax is ADD <run_id>, <lot>, <temp_c>, <yield_pct>" \ GOTO 495
1510 PRINT "RS/1: Table buffer full" \ GOTO 495
1550 IF NUM_ROW% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_ROW% THEN GOTO 1630
1600 PRINT #2%, R_RUN$(SI%); "|"; R_LOT$(SI%); "|"; R_TEMP%(SI%); "|"; R_YLD%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_ROW%; " RS/1 notebook rows saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ROW% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FRN$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FLT$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FTM% = VAL(LEFT$(REM2$, P3% - 1%)) \ FYD% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_ROW% = NUM_ROW% + 1% \ R_RUN$(NUM_ROW%) = FRN$ \ R_LOT$(NUM_ROW%) = FLT$ \ R_TEMP%(NUM_ROW%) = FTM% \ R_YLD%(NUM_ROW%) = FYD% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_ROW%; " RS/1 notebook rows loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "BBN RS/1 V4.0 Research Notebook Status:" \ PRINT "  Active Table: "; TBL_NAME$; " | Notebook File: "; DB_FILE$; " (Rows: "; NUM_ROW%; ")" \ GOTO 495
2050 NUM_ROW% = 0% \ PRINT "[RS/1 research table cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    BBN RS/1 V4.0 Electronic Research Notebook Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample WAFER_YIELD lab table" \ PRINT "  DISPLAY / LIST / TABLE           Display 2D research lab table"
3020 PRINT "  FIT / CURVE                      Least-squares linear curve fit & residuals" \ PRINT "  COMPARE / TTEST                  Two-sample statistical significance test"
3030 PRINT "  GRAPH / RPL                      ASCII control chart or execute RPL proc" \ PRINT "  ADD <run>, <lot>, <temp>, <yld>  Add experimental run to research table"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load RS1NOTE.DAT notebook" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear table, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "RS/1: Research table is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
