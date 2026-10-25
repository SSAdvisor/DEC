10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM W_ADDR$(15%) \ DIM W_LBL$(15%) \ DIM W_FML$(15%) \ DIM W_VAL%(15%)
20 NUM_CELL% = 0% \ SHEET_MODE$ = "3D-GROUP" \ DB_FILE$ = "LOTUS.WK3"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Lotus 1-2-3 for VAX/VMS Release 3.0 (V1.0) - 3D Enterprise Spreadsheet" \ PRINT "    Lotus Development Corporation (Cambridge, MA) - DEC ALL-IN-1 / VAX/VMS" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load .WK3, GRID, SUMMARY, DATATABLE, or EXIT." \ PRINT ""
100 PRINT "123> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "GRID" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "SUMMARY" OR VERB$ = "CALC" THEN GOTO 960
370 IF VERB$ = "DATATABLE" OR VERB$ = "TABLE" THEN GOTO 1150
380 IF VERB$ = "ADD" OR VERB$ = "SET" THEN GOTO 1380
390 IF VERB$ = "SAVE" THEN GOTO 1550
400 IF VERB$ = "LOAD" OR VERB$ = "RETRIEVE" THEN GOTO 1700
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
420 IF VERB$ = "CLEAR" OR VERB$ = "ERASE" THEN GOTO 2050
480 PRINT "123: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_CELL% = 4%
710 W_ADDR$(1%) = "A:B2" \ W_LBL$(1%) = "North America Hardware" \ W_FML$(1%) = "+Q1..Q4_NA" \ W_VAL%(1%) = 1400%
720 W_ADDR$(2%) = "B:B2" \ W_LBL$(2%) = "European VAX Division " \ W_FML$(2%) = "+Q1..Q4_EU" \ W_VAL%(2%) = 1100%
730 W_ADDR$(3%) = "C:B2" \ W_LBL$(3%) = "Pacific Rim Operations" \ W_FML$(3%) = "+Q1..Q4_AP" \ W_VAL%(3%) = 900%
740 W_ADDR$(4%) = "D:B4" \ W_LBL$(4%) = "Corp R&D Allocation   " \ W_FML$(4%) = "@SUM(A:B4..C:B4)" \ W_VAL%(4%) = 600%
750 PRINT "[Sample Lotus 1-2-3 3D worksheet loaded - 4 multi-sheet ranges]" \ GOTO 495
820 IF NUM_CELL% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Lotus 1-2-3 3D Worksheet (Mode: "; SHEET_MODE$; ") — File: "; DB_FILE$; " [READY]" \ PRINT SEP$
840 PRINT "  3D Cell   Line Item Label          Formula / Definition    Value($K)" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_CELL% THEN GOTO 920
870 A_P$ = LEFT$(W_ADDR$(LI%) + BLANKS$, 8%) \ L_P$ = LEFT$(W_LBL$(LI%) + BLANKS$, 23%) \ F_P$ = LEFT$(W_FML$(LI%) + BLANKS$, 22%)
880 PRINT "  "; A_P$; "  "; L_P$; "  "; F_P$; "  "; W_VAL%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_CELL% = 0% THEN GOTO 3370
970 SI% = 1% \ TOT_S% = 0% \ MAX_V% = 0%
980 IF SI% > NUM_CELL% THEN GOTO 1030
990 TOT_S% = TOT_S% + W_VAL%(SI%)
1000 IF W_VAL%(SI%) > MAX_V% THEN MAX_V% = W_VAL%(SI%)
1010 SI% = SI% + 1% \ GOTO 980
1030 AVG_V% = INT(TOT_S% / NUM_CELL%) \ NPV_V% = INT((TOT_S% * 88%) / 100%) \ IRR_V% = 18% \ STD_V% = INT(AVG_V% / 5%)
1040 PRINT EQU$ \ PRINT "  Lotus 1-2-3 3D Consolidation & @Function Financial Summary" \ PRINT SEP$
1050 PRINT "  @SUM(A:B2..D:B4) = $"; TOT_S%; "K   | @AVG(A:B2..D:B4) = $"; AVG_V%; "K"
1060 PRINT "  @NPV(0.10,A..D)  = $"; NPV_V%; "K   | @IRR(Guess,A..D) = "; IRR_V%; "%   | @STD = $"; STD_V%; "K"
1070 PRINT "  [3D @Function Summary Complete: @SUM=$"; TOT_S%; "K, @NPV=$"; NPV_V%; "K, @IRR="; IRR_V%; "%]" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_CELL% = 0% THEN GOTO 3370
1160 SI% = 1% \ TOT_S% = 0%
1170 IF SI% > NUM_CELL% THEN GOTO 1200
1180 TOT_S% = TOT_S% + W_VAL%(SI%) \ SI% = SI% + 1% \ GOTO 1170
1200 DT_LOW% = INT((TOT_S% * 90%) / 100%) \ DT_BASE% = TOT_S% \ DT_HIGH% = INT((TOT_S% * 115%) / 100%)
1210 PRINT EQU$ \ PRINT "  Lotus 1-2-3 /Data Table 2 Sensitivity Matrix (Growth Rate vs FX Rate)" \ PRINT SEP$
1220 PRINT "  Scenario -10% Bear Case  : Projected 3D Total = $"; DT_LOW%; "K"
1230 PRINT "  Scenario   0% Base Case  : Projected 3D Total = $"; DT_BASE%; "K"
1240 PRINT "  Scenario +15% Bull Case  : Projected 3D Total = $"; DT_HIGH%; "K"
1250 PRINT "  [/Data Table Sensitivity Complete: Base=$"; DT_BASE%; "K, Bull=$"; DT_HIGH%; "K]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_CELL% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ A_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ L_V$ = T_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ F_V$ = T_OUT$
1480 VL_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_CELL% = NUM_CELL% + 1% \ W_ADDR$(NUM_CELL%) = A_V$ \ W_LBL$(NUM_CELL%) = L_V$ \ W_FML$(NUM_CELL%) = F_V$ \ W_VAL%(NUM_CELL%) = VL_V%
1495 PRINT "[Lotus 1-2-3 Cell #"; NUM_CELL%; " set: "; A_V$; " ("; L_V$; " = $"; VL_V%; "K)]" \ GOTO 495
1500 PRINT "123: Syntax is ADD <sheet:cell>, <label>, <formula>, <val_k>" \ GOTO 495
1510 PRINT "123: Worksheet memory full" \ GOTO 495
1550 IF NUM_CELL% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_CELL% THEN GOTO 1630
1600 PRINT #2%, W_ADDR$(SI%); "|"; W_LBL$(SI%); "|"; W_FML$(SI%); "|"; W_VAL%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_CELL%; " Lotus 1-2-3 cells saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_CELL% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FA$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FL$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FF$ = LEFT$(REM2$, P3% - 1%) \ FV% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_CELL% = NUM_CELL% + 1% \ W_ADDR$(NUM_CELL%) = FA$ \ W_LBL$(NUM_CELL%) = FL$ \ W_FML$(NUM_CELL%) = FF$ \ W_VAL%(NUM_CELL%) = FV% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_CELL%; " Lotus 1-2-3 cells loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Lotus 1-2-3 for VAX/VMS V1.0 Status:" \ PRINT "  Active File:    "; DB_FILE$; " (Cells: "; NUM_CELL%; ", Mode: "; SHEET_MODE$; ")" \ GOTO 495
2050 NUM_CELL% = 0% \ PRINT "[Lotus 1-2-3 worksheet erased]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Lotus 1-2-3 for VAX/VMS Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample 3D .WK3 worksheet" \ PRINT "  GRID / LIST                      Display 3D multi-sheet cells (A:A1..D:B4)"
3020 PRINT "  SUMMARY / CALC                   Evaluate @SUM, @NPV, @IRR, and @STD" \ PRINT "  DATATABLE / TABLE                Run 1-way/2-way /Data Table sensitivity"
3030 PRINT "  ADD <addr>, <lbl>, <fml>, <val>  Set 3D worksheet cell" \ PRINT "  SAVE [file] / LOAD [file]        Save or retrieve LOTUS.WK3 file"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, erase worksheet, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "123: Worksheet is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
