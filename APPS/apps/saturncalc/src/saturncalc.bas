10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_LBL$(10%) \ DIM C_H1%(10%) \ DIM C_H2%(10%) \ DIM C_TOT%(10%) \ DIM C_VAR%(10%)
20 NUM_ROWS% = 0% \ SPLIT_ROW% = 3% \ WS_FILE$ = "SCALC.DAT" \ WP_FILE$ = "SCALC.WKS" \ ASSET_COST% = 1200% \ ASSET_SALV% = 200% \ ASSET_LIFE% = 5%
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Saturn-Calc V3.4 - Virtual-Array VT100 Electronic Worksheet" \ PRINT "    Saturn Systems, Inc. (Minneapolis, MN) - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load worksheet, SPLIT for dual view, or EXIT." \ PRINT ""
100 PRINT "SATURN-CALC> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "GRID" OR VERB$ = "SHEET" OR VERB$ = "VIEW" OR VERB$ = "DISPLAY" THEN GOTO 850
360 IF VERB$ = "SPLIT" OR VERB$ = "WINDOW" THEN GOTO 1050
370 IF VERB$ = "SET" OR VERB$ = "CELL" OR VERB$ = "UPDATE" THEN GOTO 1250
380 IF VERB$ = "LABEL" OR VERB$ = "ROW" THEN GOTO 1420
390 IF VERB$ = "RECALC" OR VERB$ = "CALC" THEN GOTO 1540
400 IF VERB$ = "DEPREC" OR VERB$ = "SLN" OR VERB$ = "DDB" OR VERB$ = "SYD" THEN GOTO 1600
410 IF VERB$ = "LOAN" OR VERB$ = "PMT" OR VERB$ = "AMORT" THEN GOTO 1820
420 IF VERB$ = "GRAPH" OR VERB$ = "SATGRAPH" OR VERB$ = "PLOT" THEN GOTO 2020
430 IF VERB$ = "EXPORTWP" OR VERB$ = "HANDOFF" OR VERB$ = "WP" OR VERB$ = "EXPORT" THEN GOTO 2200
440 IF VERB$ = "SAVE" THEN GOTO 2400
450 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 2550
460 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2800
470 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2900
480 PRINT "Saturn-Calc: Unknown command '"; VERB$; "'. Type HELP for commands."
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
640 TOT_H1% = 0% \ TOT_H2% = 0% \ TOT_ALL% = 0%
645 IF NUM_ROWS% = 0% THEN GOTO 695
650 RI% = 1%
655 IF RI% > NUM_ROWS% THEN GOTO 695
660 C_TOT%(RI%) = C_H1%(RI%) + C_H2%(RI%) \ C_VAR%(RI%) = C_H2%(RI%) - C_H1%(RI%)
665 TOT_H1% = TOT_H1% + C_H1%(RI%) \ TOT_H2% = TOT_H2% + C_H2%(RI%) \ TOT_ALL% = TOT_ALL% + C_TOT%(RI%)
670 RI% = RI% + 1% \ GOTO 655
695 RETURN
700 NUM_ROWS% = 5% \ SPLIT_ROW% = 3% \ ASSET_COST% = 1200% \ ASSET_SALV% = 200% \ ASSET_LIFE% = 5%
710 R_LBL$(1%) = "Northern Division " \ C_H1%(1%) = 420% \ C_H2%(1%) = 480%
720 R_LBL$(2%) = "Central Division  " \ C_H1%(2%) = 310% \ C_H2%(2%) = 390%
730 R_LBL$(3%) = "Western Division  " \ C_H1%(3%) = 270% \ C_H2%(3%) = 330%
740 R_LBL$(4%) = "Southern Division " \ C_H1%(4%) = 190% \ C_H2%(4%) = 250%
750 R_LBL$(5%) = "Export Operations " \ C_H1%(5%) = 160% \ C_H2%(5%) = 200%
760 GOSUB 640
770 PRINT "[Sample Saturn-Calc worksheet loaded - 5 divisions, Total="; TOT_ALL%; "K]" \ GOTO 495
850 IF NUM_ROWS% = 0% THEN GOTO 3370
860 GOSUB 640
870 PRINT EQU$ \ PRINT "  Saturn-Calc V3.4 Virtual Worksheet ("; WS_FILE$; ")" \ PRINT SEP$
880 PRINT "Row  Division / Account       H1 ($K)      H2 ($K)      Annual ($K)  H2-H1 Var" \ PRINT SEP$
890 GI% = 1%
900 IF GI% > NUM_ROWS% THEN GOTO 980
910 R_STR$ = STR$(GI%) \ T_IN$ = R_STR$ \ GOSUB 500 \ R_PAD$ = LEFT$(T_OUT$ + "   ", 4%)
920 L_PAD$ = LEFT$(R_LBL$(GI%) + BLANKS$, 22%)
930 H1_STR$ = STR$(C_H1%(GI%)) \ T_IN$ = H1_STR$ \ GOSUB 500 \ H1_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
940 H2_STR$ = STR$(C_H2%(GI%)) \ T_IN$ = H2_STR$ \ GOSUB 500 \ H2_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
950 TT_STR$ = STR$(C_TOT%(GI%)) \ T_IN$ = TT_STR$ \ GOSUB 500 \ TT_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
960 PRINT R_PAD$; " "; L_PAD$; "  "; H1_PAD$; " "; H2_PAD$; " "; TT_PAD$; " "; C_VAR%(GI%)
970 GI% = GI% + 1% \ GOTO 900
980 PRINT SEP$ \ PRINT "TOT  Worksheet Grand Total    "; TOT_H1%; "         "; TOT_H2%; "         "; TOT_ALL%; "         "; TOT_H2% - TOT_H1% \ PRINT EQU$ \ GOTO 495
1050 IF NUM_ROWS% = 0% THEN GOTO 3370
1060 IF ARGS$ <> "" THEN SPLIT_ROW% = VAL(ARGS$)
1070 IF SPLIT_ROW% < 1% THEN SPLIT_ROW% = 1%
1080 IF SPLIT_ROW% >= NUM_ROWS% THEN SPLIT_ROW% = NUM_ROWS% - 1%
1090 GOSUB 640
1100 PRINT EQU$ \ PRINT "  [WINDOW 1 - TOP PANE: Rows 1 to "; SPLIT_ROW%; " (Core Regional Divisions)]" \ PRINT SEP$
1110 WI% = 1%
1120 IF WI% > SPLIT_ROW% THEN GOTO 1160
1130 L_PAD$ = LEFT$(R_LBL$(WI%) + BLANKS$, 22%)
1140 PRINT "  Row "; WI%; ": "; L_PAD$; " | H1="; C_H1%(WI%); "K | H2="; C_H2%(WI%); "K | Total="; C_TOT%(WI%); "K"
1150 WI% = WI% + 1% \ GOTO 1120
1160 PRINT SEP$ \ PRINT "  [WINDOW 2 - BOTTOM PANE: Rows "; SPLIT_ROW% + 1%; " to "; NUM_ROWS%; " (Expansion & Export)]" \ PRINT SEP$
1170 WI% = SPLIT_ROW% + 1%
1180 IF WI% > NUM_ROWS% THEN GOTO 1220
1190 L_PAD$ = LEFT$(R_LBL$(WI%) + BLANKS$, 22%)
1200 PRINT "  Row "; WI%; ": "; L_PAD$; " | H1="; C_H1%(WI%); "K | H2="; C_H2%(WI%); "K | Total="; C_TOT%(WI%); "K"
1210 WI% = WI% + 1% \ GOTO 1180
1220 PRINT EQU$ \ GOTO 495
1250 IF NUM_ROWS% = 0% THEN GOTO 3370
1260 C1% = INSTR(1%, ARGS$, ",")
1270 IF C1% = 0% THEN GOTO 1390
1280 R_IDX% = VAL(LEFT$(ARGS$, C1% - 1%)) \ REM_S$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_S$, ",")
1290 IF C2% = 0% THEN GOTO 1390
1300 IF R_IDX% < 1% THEN GOTO 1400
1310 IF R_IDX% > NUM_ROWS% THEN GOTO 1400
1320 V_H1% = VAL(LEFT$(REM_S$, C2% - 1%)) \ V_H2% = VAL(MID$(REM_S$, C2% + 1%, LEN(REM_S$) - C2%))
1330 C_H1%(R_IDX%) = V_H1% \ C_H2%(R_IDX%) = V_H2% \ GOSUB 640
1340 PRINT "[Saturn-Calc Row #"; R_IDX%; " updated: H1="; V_H1%; "K, H2="; V_H2%; "K, Annual="; C_TOT%(R_IDX%); "K | Grand Total="; TOT_ALL%; "K]" \ GOTO 495
1390 PRINT "Saturn-Calc: Syntax is SET <row#>, <h1_val>, <h2_val>" \ GOTO 495
1400 PRINT "Saturn-Calc: Row number out of range (1 to "; NUM_ROWS%; ")" \ GOTO 495
1420 C1% = INSTR(1%, ARGS$, ",")
1430 IF C1% = 0% THEN GOTO 1510
1440 R_IDX% = VAL(LEFT$(ARGS$, C1% - 1%)) \ T_IN$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ GOSUB 500 \ L_TXT$ = T_OUT$
1450 IF R_IDX% < 1% THEN GOTO 1510
1460 IF R_IDX% > 8% THEN GOTO 1510
1470 IF R_IDX% > NUM_ROWS% THEN NUM_ROWS% = R_IDX%
1480 R_LBL$(R_IDX%) = L_TXT$ \ GOSUB 640
1490 PRINT "[Saturn-Calc Row #"; R_IDX%; " label set to '"; L_TXT$; "']" \ GOTO 495
1510 PRINT "Saturn-Calc: Syntax is LABEL <row#>, <description>" \ GOTO 495
1540 IF NUM_ROWS% = 0% THEN GOTO 3370
1550 GOSUB 640 \ PRINT "[Saturn-Calc Recalculation complete: H1="; TOT_H1%; "K, H2="; TOT_H2%; "K, Annual Total="; TOT_ALL%; "K]" \ GOTO 495
1600 IF ARGS$ = "" THEN GOTO 1690
1610 C1% = INSTR(1%, ARGS$, ",")
1620 IF C1% = 0% THEN GOTO 1690
1630 ASSET_COST% = VAL(LEFT$(ARGS$, C1% - 1%)) \ REM_D$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_D$, ",")
1640 IF C2% = 0% THEN GOTO 1690
1650 ASSET_SALV% = VAL(LEFT$(REM_D$, C2% - 1%)) \ ASSET_LIFE% = VAL(MID$(REM_D$, C2% + 1%, LEN(REM_D$) - C2%))
1690 IF ASSET_LIFE% < 1% THEN ASSET_LIFE% = 5%
1700 DEP_BASE% = ASSET_COST% - ASSET_SALV%
1710 SLN_YR% = INT(DEP_BASE% / ASSET_LIFE%)
1720 DDB_YR1% = INT((ASSET_COST% * 2%) / ASSET_LIFE%)
1730 SYD_SUM% = INT((ASSET_LIFE% * (ASSET_LIFE% + 1%)) / 2%)
1740 SYD_YR1% = INT((DEP_BASE% * ASSET_LIFE%) / SYD_SUM%)
1750 PRINT EQU$ \ PRINT "  Saturn-Calc Financial Depreciation Schedule (@SLN / @DDB / @SYD)" \ PRINT SEP$
1760 PRINT "  Asset Cost:      $"; ASSET_COST%; "K   Salvage Value: $"; ASSET_SALV%; "K   Useful Life: "; ASSET_LIFE%; " Years"
1770 PRINT "  Straight-Line:   @SLN = $"; SLN_YR%; "K / year"
1780 PRINT "  Double-Declining:@DDB (Year 1) = $"; DDB_YR1%; "K"
1790 PRINT "  Sum-Years-Digits:@SYD (Year 1) = $"; SYD_YR1%; "K (Denominator="; SYD_SUM%; ")" \ PRINT EQU$ \ GOTO 495
1820 LOAN_P% = 1000% \ LOAN_R% = 12% \ LOAN_Y% = 5%
1830 IF ARGS$ = "" THEN GOTO 1910
1840 C1% = INSTR(1%, ARGS$, ",")
1850 IF C1% = 0% THEN GOTO 1910
1860 LOAN_P% = VAL(LEFT$(ARGS$, C1% - 1%)) \ REM_L$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_L$, ",")
1870 IF C2% = 0% THEN GOTO 1910
1880 LOAN_R% = VAL(LEFT$(REM_L$, C2% - 1%)) \ LOAN_Y% = VAL(MID$(REM_L$, C2% + 1%, LEN(REM_L$) - C2%))
1910 IF LOAN_Y% < 1% THEN LOAN_Y% = 5%
1920 PRIN_YR% = INT(LOAN_P% / LOAN_Y%) \ INT_YR1% = INT((LOAN_P% * LOAN_R%) / 100%)
1930 PMT_YR% = PRIN_YR% + INT((INT_YR1% * 60%) / 100%) \ TOT_PAID% = PMT_YR% * LOAN_Y%
1940 PRINT EQU$ \ PRINT "  Saturn-Calc Loan Amortization & @PMT Schedule" \ PRINT SEP$
1950 PRINT "  Principal:       $"; LOAN_P%; "K   Interest Rate: "; LOAN_R%; "%   Term: "; LOAN_Y%; " Years"
1960 PRINT "  Annual Payment:  @PMT = $"; PMT_YR%; "K / year (Year 1 Interest: $"; INT_YR1%; "K)"
1970 PRINT "  Total Repayment: $"; TOT_PAID%; "K (Total Interest: $"; TOT_PAID% - LOAN_P%; "K)" \ PRINT EQU$ \ GOTO 495
2020 IF NUM_ROWS% = 0% THEN GOTO 3370
2030 GOSUB 640
2040 PRINT EQU$ \ PRINT "  Saturn-Graph V3.4 Handoff — Division Annual Revenue Chart ($K)" \ PRINT SEP$
2050 GI% = 1%
2060 IF GI% > NUM_ROWS% THEN GOTO 2150
2070 L_PAD$ = LEFT$(R_LBL$(GI%) + BLANKS$, 18%) \ B_LEN% = INT(C_TOT%(GI%) / 25%)
2080 IF B_LEN% < 1% THEN B_LEN% = 1%
2090 IF B_LEN% > 40% THEN B_LEN% = 40%
2100 BAR_S$ = "" \ BI% = 1%
2110 IF BI% > B_LEN% THEN GOTO 2130
2120 BAR_S$ = BAR_S$ + "#" \ BI% = BI% + 1% \ GOTO 2110
2130 PRINT "  "; L_PAD$; " | "; BAR_S$; " ("; C_TOT%(GI%); "K)"
2140 GI% = GI% + 1% \ GOTO 2060
2150 PRINT SEP$ \ PRINT "  [Saturn-Graph Plot Complete — Grand Total: "; TOT_ALL%; "K]" \ PRINT EQU$ \ GOTO 495
2200 IF NUM_ROWS% = 0% THEN GOTO 3370
2210 GOSUB 640 \ OUT_WP$ = WP_FILE$
2220 IF ARGS$ <> "" THEN OUT_WP$ = ARGS$
2230 OPEN OUT_WP$ FOR OUTPUT AS FILE #2%
2240 PRINT #2%, "SATURN-CALC WORKSHEET HANDOFF ("; OUT_WP$; ")"
2250 WI% = 1%
2260 IF WI% > NUM_ROWS% THEN GOTO 2300
2270 PRINT #2%, R_LBL$(WI%); "|H1="; C_H1%(WI%); "K|H2="; C_H2%(WI%); "K|TOTAL="; C_TOT%(WI%); "K"
2280 WI% = WI% + 1% \ GOTO 2260
2300 PRINT #2%, "GRAND TOTAL|H1="; TOT_H1%; "K|H2="; TOT_H2%; "K|TOTAL="; TOT_ALL%; "K"
2310 CLOSE #2% \ PRINT "[Saturn-Calc worksheet exported to Saturn-WP link file "; OUT_WP$; " (Total="; TOT_ALL%; "K)]" \ GOTO 495
2400 IF NUM_ROWS% = 0% THEN GOTO 3370
2410 GOSUB 640 \ SV_FILE$ = WS_FILE$
2420 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
2430 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
2440 IF SI% > NUM_ROWS% THEN GOTO 2480
2450 PRINT #2%, R_LBL$(SI%); "|"; C_H1%(SI%); "|"; C_H2%(SI%)
2460 SI% = SI% + 1% \ GOTO 2440
2480 CLOSE #2% \ PRINT "["; NUM_ROWS%; " Saturn-Calc rows saved to "; SV_FILE$; "]" \ GOTO 495
2550 LD_FILE$ = WS_FILE$
2560 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
2570 ON ERROR GOTO 2680 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ROWS% = 0%
2580 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
2590 IF T_OUT$ = "" THEN GOTO 2580
2600 P1% = INSTR(1%, T_OUT$, "|")
2610 IF P1% = 0% THEN GOTO 2580
2620 F_LBL$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
2630 IF P2% = 0% THEN GOTO 2580
2640 F_H1% = VAL(LEFT$(REM1$, P2% - 1%)) \ F_H2% = VAL(MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%))
2650 NUM_ROWS% = NUM_ROWS% + 1% \ R_LBL$(NUM_ROWS%) = F_LBL$ \ C_H1%(NUM_ROWS%) = F_H1% \ C_H2%(NUM_ROWS%) = F_H2% \ GOTO 2580
2680 CLOSE #2% \ RESUME 2690
2690 ON ERROR GOTO 0 \ GOSUB 640 \ PRINT "["; NUM_ROWS%; " Saturn-Calc rows loaded from "; LD_FILE$; "]" \ GOTO 495
2800 GOSUB 640 \ PRINT "Saturn-Calc V3.4 Status:" \ PRINT "  Worksheet File: "; WS_FILE$; " (Saturn-WP Link: "; WP_FILE$; ")"
2810 PRINT "  Active Rows:    "; NUM_ROWS%; " (Split Row: "; SPLIT_ROW%; ") | Grand Total: "; TOT_ALL%; "K" \ GOTO 495
2900 NUM_ROWS% = 0% \ TOT_H1% = 0% \ TOT_H2% = 0% \ TOT_ALL% = 0% \ PRINT "[Saturn-Calc worksheet cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Saturn-Calc V3.4 Electronic Worksheet Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample 5-division financial worksheet" \ PRINT "  GRID / SHEET / VIEW              Display full worksheet and totals"
3020 PRINT "  SPLIT [row#] / WINDOW            Display split-window dual pane view" \ PRINT "  SET <row#>, <h1>, <h2>           Update row H1/H2 values and recalculate"
3030 PRINT "  LABEL <row#>, <title>            Set or add row description" \ PRINT "  DEPREC [cost,salv,life]          Calculate @SLN, @DDB, @SYD depreciation"
3040 PRINT "  LOAN [prin,rate,yrs] / PMT       Calculate loan amortization & @PMT" \ PRINT "  GRAPH / SATGRAPH / PLOT          Render Saturn-Graph division bar chart"
3050 PRINT "  EXPORTWP [file] / WP             Handoff worksheet range to Saturn-WP" \ PRINT "  SAVE [file] / LOAD [file]        Save or load SCALC.DAT worksheet"
3060 PRINT "  SHOW / CLEAR / EXIT              Show status, clear worksheet, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "Saturn-Calc: Worksheet is empty. Use SAMPLE or LABEL." \ GOTO 495
3400 END
