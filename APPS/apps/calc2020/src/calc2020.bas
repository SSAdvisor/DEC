10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_LBL$(10%) \ DIM C_A%(10%) \ DIM C_B%(10%) \ DIM C_C%(10%) \ DIM C_D%(10%) \ DIM R_FML$(10%)
20 NUM_ROWS% = 0% \ CURR_ROW% = 1% \ WS_TITLE$ = "20/20 Corporate Financial Model" \ WS_FILE$ = "SC20WS.DAT" \ DISC_RATE% = 10% \ CONSOL_CNT% = 1%
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Access Technology 20/20 V2.3 (Supercomp-20) Electronic Spreadsheet" \ PRINT "    Access Technology, Inc. (South Natick, MA) - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load model, GRID to view, or EXIT to quit." \ PRINT ""
100 PRINT "20/20> "; \ LINE INPUT RAW_INPUT$
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
320 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "BYE" OR VERB$ = "/Q" THEN GOTO 3400
330 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 3000
340 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 700
350 IF VERB$ = "GRID" OR VERB$ = "SHEET" OR VERB$ = "VIEW" OR VERB$ = "DISPLAY" OR VERB$ = "/W" THEN GOTO 900
360 IF VERB$ = "RECALC" OR VERB$ = "CALC" OR VERB$ = "/C" THEN GOTO 1150
370 IF VERB$ = "SET" OR VERB$ = "LET" OR VERB$ = "PUT" THEN GOTO 1200
380 IF VERB$ = "LABEL" OR VERB$ = "ROW" THEN GOTO 1500
390 IF VERB$ = "FORMULAS" OR VERB$ = "FORMULA" OR VERB$ = "/F" THEN GOTO 1620
400 IF VERB$ = "FINANCE" OR VERB$ = "NPV" OR VERB$ = "IRR" THEN GOTO 1760
410 IF VERB$ = "GOALSEEK" OR VERB$ = "GOAL" OR VERB$ = "/G" THEN GOTO 1920
420 IF VERB$ = "CONSOLIDATE" OR VERB$ = "MERGE" OR VERB$ = "/M" THEN GOTO 2100
430 IF VERB$ = "EXPORT" OR VERB$ = "PRINT" OR VERB$ = "/P" THEN GOTO 2250
440 IF VERB$ = "SAVE" OR VERB$ = "/S" THEN GOTO 2500
450 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 2650
460 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2850
470 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2950
480 PRINT "20/20: Unknown command '"; VERB$; "'. Type HELP for commands."
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
640 IF NUM_ROWS% = 0% THEN GOTO 695
645 RI% = 1%
650 IF RI% > NUM_ROWS% THEN GOTO 670
655 IF R_FML$(RI%) = "@SUM(A..C)" THEN C_D%(RI%) = C_A%(RI%) + C_B%(RI%) + C_C%(RI%)
660 IF R_FML$(RI%) = "@AVG(A..C)" THEN C_D%(RI%) = INT((C_A%(RI%) + C_B%(RI%) + C_C%(RI%)) / 3%)
665 RI% = RI% + 1% \ GOTO 650
670 IF NUM_ROWS% < 4% THEN GOTO 695
672 IF R_FML$(4%) <> "@SUM(1..3)" THEN GOTO 682
674 C_A%(4%) = C_A%(1%) + C_A%(2%) + C_A%(3%) \ C_B%(4%) = C_B%(1%) + C_B%(2%) + C_B%(3%)
676 C_C%(4%) = C_C%(1%) + C_C%(2%) + C_C%(3%) \ C_D%(4%) = C_A%(4%) + C_B%(4%) + C_C%(4%)
682 IF NUM_ROWS% < 6% THEN GOTO 695
684 IF R_FML$(6%) <> "@IF(4-5)" THEN GOTO 695
686 C_A%(6%) = C_A%(4%) - C_A%(5%) \ C_B%(6%) = C_B%(4%) - C_B%(5%)
688 C_C%(6%) = C_C%(4%) - C_C%(5%) \ C_D%(6%) = C_A%(6%) + C_B%(6%) + C_C%(6%)
695 RETURN
700 NUM_ROWS% = 6% \ CURR_ROW% = 1% \ DISC_RATE% = 10% \ CONSOL_CNT% = 1% \ WS_TITLE$ = "20/20 Corporate Financial Model"
710 R_LBL$(1%) = "Hardware Sales    " \ C_A%(1%) = 400% \ C_B%(1%) = 450% \ C_C%(1%) = 500% \ R_FML$(1%) = "@SUM(A..C)"
720 R_LBL$(2%) = "Software Licenses " \ C_A%(2%) = 200% \ C_B%(2%) = 240% \ C_C%(2%) = 280% \ R_FML$(2%) = "@SUM(A..C)"
730 R_LBL$(3%) = "Support & Maint   " \ C_A%(3%) = 100% \ C_B%(3%) = 110% \ C_C%(3%) = 120% \ R_FML$(3%) = "@SUM(A..C)"
740 R_LBL$(4%) = "Total Revenue     " \ C_A%(4%) = 0%   \ C_B%(4%) = 0%   \ C_C%(4%) = 0%   \ R_FML$(4%) = "@SUM(1..3)"
750 R_LBL$(5%) = "Operating Expense " \ C_A%(5%) = 420% \ C_B%(5%) = 460% \ C_C%(5%) = 490% \ R_FML$(5%) = "@SUM(A..C)"
760 R_LBL$(6%) = "Net Operating Inc " \ C_A%(6%) = 0%   \ C_B%(6%) = 0%   \ C_C%(6%) = 0%   \ R_FML$(6%) = "@IF(4-5)"
770 GOSUB 640
780 PRINT "[Sample 20/20 worksheet loaded - 6 rows x 4 columns (A1..D6), formulas evaluated]" \ GOTO 495
900 IF NUM_ROWS% = 0% THEN GOTO 3370
910 GOSUB 640
920 PRINT EQU$ \ PRINT "  Access Technology 20/20 Worksheet: "; WS_TITLE$; " ("; WS_FILE$; ")" \ PRINT SEP$
930 PRINT "Row  Description             Col A (Q1)   Col B (Q2)   Col C (Q3)   Col D (Total)  Formula" \ PRINT SEP$
940 GI% = 1%
950 IF GI% > NUM_ROWS% THEN GOTO 1120
960 R_STR$ = STR$(GI%) \ T_IN$ = R_STR$ \ GOSUB 500 \ R_PAD$ = LEFT$(T_OUT$ + "   ", 4%)
970 L_PAD$ = LEFT$(R_LBL$(GI%) + BLANKS$, 22%)
980 A_STR$ = STR$(C_A%(GI%)) \ T_IN$ = A_STR$ \ GOSUB 500 \ A_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
990 B_STR$ = STR$(C_B%(GI%)) \ T_IN$ = B_STR$ \ GOSUB 500 \ B_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
1000 C_STR$ = STR$(C_C%(GI%)) \ T_IN$ = C_STR$ \ GOSUB 500 \ C_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
1010 D_STR$ = STR$(C_D%(GI%)) \ T_IN$ = D_STR$ \ GOSUB 500 \ D_PAD$ = LEFT$(T_OUT$ + BLANKS$, 14%)
1020 PRINT R_PAD$; " "; L_PAD$; "  "; A_PAD$; " "; B_PAD$; " "; C_PAD$; " "; D_PAD$; " "; R_FML$(GI%)
1030 GI% = GI% + 1% \ GOTO 950
1120 PRINT SEP$ \ PRINT "  Command Bar: /W Worksheet  /C Recalc  /F Formulas  /G GoalSeek  /P Print  /S Save" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_ROWS% = 0% THEN GOTO 3370
1160 GOSUB 640 \ PRINT "[20/20 Recalculation complete: Row 4 Total Revenue="; C_D%(4%); " Row 6 Net Income="; C_D%(6%); "]" \ GOTO 495
1200 IF NUM_ROWS% = 0% THEN GOTO 3370
1210 C1% = INSTR(1%, ARGS$, ",")
1220 IF C1% = 0% THEN GOTO 1470
1230 CELL_REF$ = LEFT$(ARGS$, C1% - 1%) \ VAL_RAW$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%)
1240 T_IN$ = CELL_REF$ \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ CELL_REF$ = U_OUT$
1250 T_IN$ = VAL_RAW$ \ GOSUB 500 \ VAL_STR$ = T_OUT$
1260 IF LEN(CELL_REF$) < 2% THEN GOTO 1470
1270 COL_CH$ = LEFT$(CELL_REF$, 1%) \ ROW_IDX% = VAL(MID$(CELL_REF$, 2%, LEN(CELL_REF$) - 1%))
1280 IF ROW_IDX% < 1% THEN GOTO 1480
1290 IF ROW_IDX% > NUM_ROWS% THEN GOTO 1480
1300 IF LEFT$(VAL_STR$, 1%) = "@" THEN GOTO 1420
1310 NEW_V% = VAL(VAL_STR$)
1320 IF COL_CH$ = "A" THEN C_A%(ROW_IDX%) = NEW_V%
1330 IF COL_CH$ = "B" THEN C_B%(ROW_IDX%) = NEW_V%
1340 IF COL_CH$ = "C" THEN C_C%(ROW_IDX%) = NEW_V%
1350 IF COL_CH$ = "D" THEN C_D%(ROW_IDX%) = NEW_V%
1360 GOSUB 640 \ PRINT "[Cell "; CELL_REF$; " set to "; NEW_V%; " | Row "; ROW_IDX%; " Total (D"; ROW_IDX%; ")="; C_D%(ROW_IDX%); "]" \ GOTO 495
1420 U_IN$ = VAL_STR$ \ GOSUB 580 \ R_FML$(ROW_IDX%) = U_OUT$ \ GOSUB 640
1430 PRINT "[Row "; ROW_IDX%; " formula set to "; R_FML$(ROW_IDX%); " | D"; ROW_IDX%; "="; C_D%(ROW_IDX%); "]" \ GOTO 495
1470 PRINT "20/20: Syntax is SET <Cell>, <Value_or_@Formula> (e.g. SET A1, 500)" \ GOTO 495
1480 PRINT "20/20: Row index out of range (1 to "; NUM_ROWS%; ")" \ GOTO 495
1500 C1% = INSTR(1%, ARGS$, ",")
1510 IF C1% = 0% THEN GOTO 1590
1520 R_IDX% = VAL(LEFT$(ARGS$, C1% - 1%)) \ T_IN$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ GOSUB 500 \ L_TXT$ = T_OUT$
1530 IF R_IDX% < 1% THEN GOTO 1590
1540 IF R_IDX% > 8% THEN GOTO 1590
1550 IF R_IDX% > NUM_ROWS% THEN NUM_ROWS% = R_IDX%
1560 R_LBL$(R_IDX%) = L_TXT$
1570 IF R_FML$(R_IDX%) = "" THEN R_FML$(R_IDX%) = "@SUM(A..C)"
1580 GOSUB 640 \ PRINT "[Row "; R_IDX%; " label set to '"; L_TXT$; "']" \ GOTO 495
1590 PRINT "20/20: Syntax is LABEL <row#>, <description>" \ GOTO 495
1620 IF NUM_ROWS% = 0% THEN GOTO 3370
1630 PRINT EQU$ \ PRINT "  20/20 Worksheet Formula Audit (/F)" \ PRINT SEP$
1640 FI% = 1%
1650 IF FI% > NUM_ROWS% THEN GOTO 1720
1660 L_PAD$ = LEFT$(R_LBL$(FI%) + BLANKS$, 22%)
1670 PRINT "  Row "; FI%; " ("; L_PAD$; "): D"; FI%; " = "; R_FML$(FI%); " -> "; C_D%(FI%)
1680 FI% = FI% + 1% \ GOTO 1650
1720 PRINT SEP$ \ PRINT "  Built-in Functions: @SUM, @AVG, @MIN, @MAX, @NPV, @IRR, @IF, @LOOKUP" \ PRINT EQU$ \ GOTO 495
1760 IF NUM_ROWS% = 0% THEN GOTO 3370
1770 GOSUB 640
1780 IF ARGS$ <> "" THEN DISC_RATE% = VAL(ARGS$)
1790 IF DISC_RATE% < 1% THEN DISC_RATE% = 10%
1800 CF1% = C_A%(6%) \ CF2% = C_B%(6%) \ CF3% = C_C%(6%)
1810 PV1% = CF1% - INT((CF1% * DISC_RATE%) / (100% + DISC_RATE%))
1820 PV2% = CF2% - INT((CF2% * DISC_RATE% * 2%) / (100% + DISC_RATE% * 2%))
1830 PV3% = CF3% - INT((CF3% * DISC_RATE% * 3%) / (100% + DISC_RATE% * 3%))
1840 NPV_VAL% = PV1% + PV2% + PV3% \ IRR_EST% = 18% + INT(C_D%(6%) / 100%)
1850 PRINT EQU$ \ PRINT "  20/20 Financial Analysis (@NPV / @IRR / @LOOKUP)" \ PRINT SEP$
1860 PRINT "  Discount Rate:         "; DISC_RATE%; "%"
1870 PRINT "  Cash Flows (Row 6):    Q1="; CF1%; "  Q2="; CF2%; "  Q3="; CF3%; "  Total="; C_D%(6%)
1880 PRINT "  Net Present Value:     @NPV("; DISC_RATE%; "%, A6..C6) = "; NPV_VAL%
1890 PRINT "  Internal Rate Return:  @IRR(A6..C6)       = "; IRR_EST%; "%" \ PRINT EQU$ \ GOTO 495
1920 IF NUM_ROWS% = 0% THEN GOTO 3370
1930 GOSUB 640 \ GOAL_VAL% = 2400%
1940 IF ARGS$ <> "" THEN GOAL_VAL% = VAL(ARGS$)
1950 CURR_REV% = C_D%(4%) \ DIFF_REV% = GOAL_VAL% - CURR_REV%
1960 C_A%(1%) = C_A%(1%) + DIFF_REV% \ GOSUB 640
1970 PRINT "[20/20 Goal-Seek (/G): Target Total Revenue (D4) = "; GOAL_VAL%; " -> Solved A1 (Hardware Q1) = "; C_A%(1%); ", New D4 = "; C_D%(4%); "]" \ GOTO 495
2100 IF NUM_ROWS% = 0% THEN GOTO 3370
2110 ADD_PCT% = 20%
2120 IF ARGS$ <> "" THEN ADD_PCT% = VAL(ARGS$)
2130 CI% = 1%
2140 IF CI% > 3% THEN GOTO 2190
2150 C_A%(CI%) = C_A%(CI%) + INT((C_A%(CI%) * ADD_PCT%) / 100%)
2160 C_B%(CI%) = C_B%(CI%) + INT((C_B%(CI%) * ADD_PCT%) / 100%)
2170 C_C%(CI%) = C_C%(CI%) + INT((C_C%(CI%) * ADD_PCT%) / 100%)
2180 CI% = CI% + 1% \ GOTO 2140
2190 CONSOL_CNT% = CONSOL_CNT% + 1% \ GOSUB 640
2200 PRINT "[20/20 Multi-Sheet Consolidation (/M): Merged Division #"; CONSOL_CNT%; " (+"; ADD_PCT%; "%) -> Total Revenue D4="; C_D%(4%); ", Net Income D6="; C_D%(6%); "]" \ GOTO 495
2250 IF NUM_ROWS% = 0% THEN GOTO 3370
2260 GOSUB 640 \ OUT_FILE$ = "SC20RPT.TXT"
2270 IF ARGS$ <> "" THEN OUT_FILE$ = ARGS$
2280 OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2290 PRINT #2%, EQU$ \ PRINT #2%, "  Access Technology 20/20 Report: "; WS_TITLE$ \ PRINT #2%, SEP$
2300 EI% = 1%
2310 IF EI% > NUM_ROWS% THEN GOTO 2360
2320 PRINT #2%, R_LBL$(EI%); " | Q1="; C_A%(EI%); " | Q2="; C_B%(EI%); " | Q3="; C_C%(EI%); " | Total="; C_D%(EI%)
2330 EI% = EI% + 1% \ GOTO 2310
2360 PRINT #2%, EQU$ \ CLOSE #2%
2370 PRINT "[20/20 Worksheet report exported to "; OUT_FILE$; "]" \ GOTO 495
2500 IF NUM_ROWS% = 0% THEN GOTO 3370
2510 GOSUB 640 \ SV_FILE$ = WS_FILE$
2520 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
2530 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
2540 IF SI% > NUM_ROWS% THEN GOTO 2580
2550 PRINT #2%, R_LBL$(SI%); "|"; C_A%(SI%); "|"; C_B%(SI%); "|"; C_C%(SI%); "|"; C_D%(SI%); "|"; R_FML$(SI%)
2560 SI% = SI% + 1% \ GOTO 2540
2580 CLOSE #2% \ PRINT "["; NUM_ROWS%; " worksheet rows saved to "; SV_FILE$; "]" \ GOTO 495
2650 LD_FILE$ = WS_FILE$
2660 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
2670 ON ERROR GOTO 2790 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ROWS% = 0%
2680 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
2690 IF T_OUT$ = "" THEN GOTO 2680
2700 P1% = INSTR(1%, T_OUT$, "|")
2710 IF P1% = 0% THEN GOTO 2680
2720 F_LBL$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
2730 IF P2% = 0% THEN GOTO 2680
2740 F_A% = VAL(LEFT$(REM1$, P2% - 1%)) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2750 IF P3% = 0% THEN GOTO 2680
2760 F_B% = VAL(LEFT$(REM2$, P3% - 1%)) \ REM3$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ P4% = INSTR(1%, REM3$, "|")
2770 IF P4% = 0% THEN GOTO 2680
2775 F_C% = VAL(LEFT$(REM3$, P4% - 1%)) \ REM4$ = MID$(REM3$, P4% + 1%, LEN(REM3$) - P4%) \ P5% = INSTR(1%, REM4$, "|")
2780 IF P5% = 0% THEN GOTO 2680
2782 F_D% = VAL(LEFT$(REM4$, P5% - 1%)) \ F_FML$ = MID$(REM4$, P5% + 1%, LEN(REM4$) - P5%)
2784 NUM_ROWS% = NUM_ROWS% + 1% \ R_LBL$(NUM_ROWS%) = F_LBL$ \ C_A%(NUM_ROWS%) = F_A% \ C_B%(NUM_ROWS%) = F_B% \ C_C%(NUM_ROWS%) = F_C% \ C_D%(NUM_ROWS%) = F_D% \ R_FML$(NUM_ROWS%) = F_FML$ \ GOTO 2680
2790 CLOSE #2% \ RESUME 2800
2800 ON ERROR GOTO 0 \ GOSUB 640 \ PRINT "["; NUM_ROWS%; " worksheet rows loaded from "; LD_FILE$; "]" \ GOTO 495
2850 GOSUB 640 \ PRINT "20/20 Electronic Spreadsheet Status:" \ PRINT "  Model Title:   "; WS_TITLE$; " ("; WS_FILE$; ")"
2860 PRINT "  Active Rows:   "; NUM_ROWS%; " (Columns A..D) | Consolidated Sheets: "; CONSOL_CNT% \ PRINT "  Discount Rate: "; DISC_RATE%; "% | Total Revenue: "; C_D%(4%); " | Net Income: "; C_D%(6%) \ GOTO 495
2950 NUM_ROWS% = 0% \ CONSOL_CNT% = 1% \ PRINT "[20/20 worksheet cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Access Technology 20/20 V2.3 (Supercomp-20) Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample corporate financial model" \ PRINT "  GRID / SHEET / VIEW / /W         Display 2D worksheet grid (A1..D6)"
3020 PRINT "  SET <cell>, <val_or_formula>     Set cell value or formula (e.g. SET A1, 500)" \ PRINT "  LABEL <row#>, <title>            Set or add row description"
3030 PRINT "  RECALC / CALC / /C               Recalculate all worksheet formulas" \ PRINT "  FORMULAS / /F                    Audit active worksheet formulas"
3040 PRINT "  FINANCE [rate] / NPV / IRR       Compute @NPV and @IRR on cash flows" \ PRINT "  GOALSEEK [target] / /G           Solve Q1 input for target Total Revenue"
3050 PRINT "  CONSOLIDATE [pct] / /M           Multi-sheet consolidation into model" \ PRINT "  EXPORT [file] / /P               Export formatted report to disk"
3060 PRINT "  SAVE [file] / LOAD [file] / /S   Save or load SC20WS.DAT model" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear grid, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "20/20: Worksheet is empty. Use SAMPLE or LABEL to initialize." \ GOTO 495
3400 END
