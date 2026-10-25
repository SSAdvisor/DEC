10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_LBL$(10%) \ DIM C_BUD%(10%) \ DIM C_ACT%(10%) \ DIM C_VAR%(10%) \ DIM C_FCT%(10%) \ DIM R_RULE$(10%)
20 NUM_ROWS% = 0% \ GROWTH_PCT% = 10% \ DIV_CNT% = 1% \ MOD_FILE$ = "NYPLAN.DAT" \ MOD_TITLE$ = "NYPLAN Corporate P&L & Budget Model"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    NYPLAN V4.1 - Corporate Financial Modeling & Risk Analysis System" \ PRINT "    Nyplan, Inc. (Kirkland, WA) - DEC PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load P&L model, WHATIF or MONTECARLO to analyze." \ PRINT ""
100 PRINT "NYPLAN> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "MODEL" OR VERB$ = "GRID" OR VERB$ = "VIEW" OR VERB$ = "DISPLAY" OR VERB$ = "SHEET" THEN GOTO 850
360 IF VERB$ = "SET" OR VERB$ = "UPDATE" OR VERB$ = "CELL" THEN GOTO 1100
370 IF VERB$ = "LABEL" OR VERB$ = "ROW" THEN GOTO 1280
380 IF VERB$ = "RECALC" OR VERB$ = "CALC" THEN GOTO 1400
390 IF VERB$ = "WHATIF" OR VERB$ = "SENSITIVITY" THEN GOTO 1460
400 IF VERB$ = "MONTECARLO" OR VERB$ = "SIMULATE" OR VERB$ = "RISK" OR VERB$ = "VARIANCE" THEN GOTO 1700
410 IF VERB$ = "CONSOLIDATE" OR VERB$ = "MERGE" THEN GOTO 1950
420 IF VERB$ = "EXPORT" OR VERB$ = "REPORT" OR VERB$ = "PRINT" THEN GOTO 2120
430 IF VERB$ = "SAVE" THEN GOTO 2350
440 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 2500
450 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2800
460 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2900
480 PRINT "NYPLAN: Unknown command '"; VERB$; "'. Type HELP for commands."
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
645 IF NUM_ROWS% < 3% THEN GOTO 660
650 IF R_RULE$(3%) = "ROW1-ROW2" THEN C_BUD%(3%) = C_BUD%(1%) - C_BUD%(2%)
652 IF R_RULE$(3%) = "ROW1-ROW2" THEN C_ACT%(3%) = C_ACT%(1%) - C_ACT%(2%)
660 IF NUM_ROWS% < 6% THEN GOTO 675
662 IF R_RULE$(6%) = "ROW3-ROW4-ROW5" THEN C_BUD%(6%) = C_BUD%(3%) - C_BUD%(4%) - C_BUD%(5%)
664 IF R_RULE$(6%) = "ROW3-ROW4-ROW5" THEN C_ACT%(6%) = C_ACT%(3%) - C_ACT%(4%) - C_ACT%(5%)
675 RI% = 1%
680 IF RI% > NUM_ROWS% THEN GOTO 695
682 C_VAR%(RI%) = C_ACT%(RI%) - C_BUD%(RI%)
684 C_FCT%(RI%) = C_ACT%(RI%) + INT((C_ACT%(RI%) * GROWTH_PCT%) / 100%)
686 RI% = RI% + 1% \ GOTO 680
695 RETURN
700 NUM_ROWS% = 6% \ GROWTH_PCT% = 10% \ DIV_CNT% = 1% \ MOD_TITLE$ = "NYPLAN Corporate P&L & Budget Model"
710 R_LBL$(1%) = "Gross Sales Rev   " \ C_BUD%(1%) = 2000% \ C_ACT%(1%) = 2200% \ R_RULE$(1%) = "INPUT"
720 R_LBL$(2%) = "Cost of Goods Sold" \ C_BUD%(2%) = 800%  \ C_ACT%(2%) = 850%  \ R_RULE$(2%) = "INPUT"
730 R_LBL$(3%) = "Gross Margin      " \ C_BUD%(3%) = 0%    \ C_ACT%(3%) = 0%    \ R_RULE$(3%) = "ROW1-ROW2"
740 R_LBL$(4%) = "R&D Engineering   " \ C_BUD%(4%) = 300%  \ C_ACT%(4%) = 320%  \ R_RULE$(4%) = "INPUT"
750 R_LBL$(5%) = "SG&A Expense      " \ C_BUD%(5%) = 400%  \ C_ACT%(5%) = 410%  \ R_RULE$(5%) = "INPUT"
760 R_LBL$(6%) = "Net Operating Inc " \ C_BUD%(6%) = 0%    \ C_ACT%(6%) = 0%    \ R_RULE$(6%) = "ROW3-ROW4-ROW5"
770 GOSUB 640
780 PRINT "[Sample NYPLAN financial model loaded - 6 P&L accounts, Net Actual="; C_ACT%(6%); "K, Forecast="; C_FCT%(6%); "K]" \ GOTO 495
850 IF NUM_ROWS% = 0% THEN GOTO 3370
860 GOSUB 640
870 PRINT EQU$ \ PRINT "  "; MOD_TITLE$; " ("; MOD_FILE$; ")" \ PRINT SEP$
880 PRINT "Row  P&L Line Item           Budget($K)   Actual($K)   Variance     Forecast(+"; GROWTH_PCT%; "%)  Rule" \ PRINT SEP$
890 GI% = 1%
900 IF GI% > NUM_ROWS% THEN GOTO 1020
910 R_STR$ = STR$(GI%) \ T_IN$ = R_STR$ \ GOSUB 500 \ R_PAD$ = LEFT$(T_OUT$ + "   ", 4%)
920 L_PAD$ = LEFT$(R_LBL$(GI%) + BLANKS$, 22%)
930 B_STR$ = STR$(C_BUD%(GI%)) \ T_IN$ = B_STR$ \ GOSUB 500 \ B_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
940 A_STR$ = STR$(C_ACT%(GI%)) \ T_IN$ = A_STR$ \ GOSUB 500 \ A_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
950 V_STR$ = STR$(C_VAR%(GI%)) \ T_IN$ = V_STR$ \ GOSUB 500 \ V_PAD$ = LEFT$(T_OUT$ + BLANKS$, 12%)
960 F_STR$ = STR$(C_FCT%(GI%)) \ T_IN$ = F_STR$ \ GOSUB 500 \ F_PAD$ = LEFT$(T_OUT$ + BLANKS$, 14%)
970 PRINT R_PAD$; " "; L_PAD$; "  "; B_PAD$; " "; A_PAD$; " "; V_PAD$; " "; F_PAD$; " "; R_RULE$(GI%)
980 GI% = GI% + 1% \ GOTO 900
1020 PRINT SEP$ \ PRINT "  Divisions Consolidated: "; DIV_CNT%; " | Net Profit Variance: "; C_VAR%(6%); "K | Forecast Net: "; C_FCT%(6%); "K" \ PRINT EQU$ \ GOTO 495
1100 IF NUM_ROWS% = 0% THEN GOTO 3370
1110 C1% = INSTR(1%, ARGS$, ",")
1120 IF C1% = 0% THEN GOTO 1240
1130 R_IDX% = VAL(LEFT$(ARGS$, C1% - 1%)) \ REM_S$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_S$, ",")
1140 IF C2% = 0% THEN GOTO 1240
1150 IF R_IDX% < 1% THEN GOTO 1250
1160 IF R_IDX% > NUM_ROWS% THEN GOTO 1250
1170 V_BUD% = VAL(LEFT$(REM_S$, C2% - 1%)) \ V_ACT% = VAL(MID$(REM_S$, C2% + 1%, LEN(REM_S$) - C2%))
1180 C_BUD%(R_IDX%) = V_BUD% \ C_ACT%(R_IDX%) = V_ACT% \ GOSUB 640
1190 PRINT "[NYPLAN Row #"; R_IDX%; " updated: Budget="; V_BUD%; "K, Actual="; V_ACT%; "K, Var="; C_VAR%(R_IDX%); "K | Net Operating Inc="; C_ACT%(6%); "K]" \ GOTO 495
1240 PRINT "NYPLAN: Syntax is SET <row#>, <budget>, <actual>" \ GOTO 495
1250 PRINT "NYPLAN: Row number out of range (1 to "; NUM_ROWS%; ")" \ GOTO 495
1280 C1% = INSTR(1%, ARGS$, ",")
1290 IF C1% = 0% THEN GOTO 1370
1300 R_IDX% = VAL(LEFT$(ARGS$, C1% - 1%)) \ T_IN$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ GOSUB 500 \ L_TXT$ = T_OUT$
1310 IF R_IDX% < 1% THEN GOTO 1370
1320 IF R_IDX% > 8% THEN GOTO 1370
1330 IF R_IDX% > NUM_ROWS% THEN NUM_ROWS% = R_IDX%
1340 R_LBL$(R_IDX%) = L_TXT$
1350 IF R_RULE$(R_IDX%) = "" THEN R_RULE$(R_IDX%) = "INPUT"
1360 GOSUB 640 \ PRINT "[NYPLAN Row #"; R_IDX%; " label set to '"; L_TXT$; "']" \ GOTO 495
1370 PRINT "NYPLAN: Syntax is LABEL <row#>, <description>" \ GOTO 495
1400 IF NUM_ROWS% = 0% THEN GOTO 3370
1410 GOSUB 640 \ PRINT "[NYPLAN Model Recalculated: Gross Margin="; C_ACT%(3%); "K, Net Operating Inc="; C_ACT%(6%); "K, Forecast="; C_FCT%(6%); "K]" \ GOTO 495
1460 IF NUM_ROWS% = 0% THEN GOTO 3370
1470 W_REV_PCT% = 15% \ W_COST_PCT% = 5%
1480 IF ARGS$ = "" THEN GOTO 1550
1490 C1% = INSTR(1%, ARGS$, ",")
1500 IF C1% = 0% THEN GOTO 1540
1510 W_REV_PCT% = VAL(LEFT$(ARGS$, C1% - 1%)) \ W_COST_PCT% = VAL(MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%)) \ GOTO 1550
1540 W_REV_PCT% = VAL(ARGS$)
1550 GOSUB 640
1560 W_REV% = C_ACT%(1%) + INT((C_ACT%(1%) * W_REV_PCT%) / 100%)
1570 W_COGS% = C_ACT%(2%) + INT((C_ACT%(2%) * W_COST_PCT%) / 100%)
1580 W_GM% = W_REV% - W_COGS%
1590 W_OPEX% = C_ACT%(4%) + C_ACT%(5%) + INT(((C_ACT%(4%) + C_ACT%(5%)) * W_COST_PCT%) / 100%)
1600 W_NET% = W_GM% - W_OPEX% \ W_DELTA% = W_NET% - C_ACT%(6%)
1610 PRINT EQU$ \ PRINT "  NYPLAN 'What-If' Sensitivity Analysis (Rev +"; W_REV_PCT%; "%, Cost +"; W_COST_PCT%; "%)" \ PRINT SEP$
1620 PRINT "  Baseline Actuals:  Gross Rev="; C_ACT%(1%); "K | Gross Margin="; C_ACT%(3%); "K | Net Profit="; C_ACT%(6%); "K"
1630 PRINT "  What-If Scenario:  Gross Rev="; W_REV%; "K | Gross Margin="; W_GM%; "K | Net Profit="; W_NET%; "K"
1640 PRINT "  Net Profit Impact: "; W_DELTA%; "K (vs. Baseline "; C_ACT%(6%); "K)" \ PRINT EQU$ \ GOTO 495
1700 IF NUM_ROWS% = 0% THEN GOTO 3370
1710 GOSUB 640 \ MC_RUNS% = 100%
1720 IF ARGS$ <> "" THEN MC_RUNS% = VAL(ARGS$)
1730 IF MC_RUNS% < 10% THEN MC_RUNS% = 100%
1740 BASE_NET% = C_ACT%(6%)
1750 MC_LOW% = BASE_NET% - INT((C_ACT%(1%) * 12%) / 100%)
1760 MC_MEAN% = BASE_NET% + INT((BASE_NET% * 8%) / 100%)
1770 MC_HIGH% = BASE_NET% + INT((C_ACT%(1%) * 18%) / 100%)
1780 MC_STD% = INT((MC_HIGH% - MC_LOW%) / 4%)
1790 PRINT EQU$ \ PRINT "  NYPLAN Monte Carlo Risk & Variance Simulation ("; MC_RUNS%; " Trials)" \ PRINT SEP$
1800 PRINT "  Pessimistic (P10): $"; MC_LOW%; "K Net Operating Profit"
1810 PRINT "  Expected Mean:     $"; MC_MEAN%; "K Net Operating Profit"
1820 PRINT "  Optimistic (P90):  $"; MC_HIGH%; "K Net Operating Profit"
1830 PRINT "  Std Deviation:     $"; MC_STD%; "K | Confidence Interval (80%): $"; MC_LOW%; "K .. $"; MC_HIGH%; "K" \ PRINT EQU$ \ GOTO 495
1950 IF NUM_ROWS% = 0% THEN GOTO 3370
1960 ADD_PCT% = 25%
1970 IF ARGS$ <> "" THEN ADD_PCT% = VAL(ARGS$)
1980 CI% = 1%
1990 IF CI% > NUM_ROWS% THEN GOTO 2050
2000 IF R_RULE$(CI%) <> "INPUT" THEN GOTO 2040
2010 C_BUD%(CI%) = C_BUD%(CI%) + INT((C_BUD%(CI%) * ADD_PCT%) / 100%)
2020 C_ACT%(CI%) = C_ACT%(CI%) + INT((C_ACT%(CI%) * ADD_PCT%) / 100%)
2040 CI% = CI% + 1% \ GOTO 1990
2050 DIV_CNT% = DIV_CNT% + 1% \ GOSUB 640
2060 PRINT "[NYPLAN Multi-Division P&L Consolidation: Division #"; DIV_CNT%; " (+"; ADD_PCT%; "%) -> Consolidated Rev="; C_ACT%(1%); "K, Net Profit="; C_ACT%(6%); "K]" \ GOTO 495
2120 IF NUM_ROWS% = 0% THEN GOTO 3370
2130 GOSUB 640 \ OUT_FILE$ = "NYPRPT.TXT"
2140 IF ARGS$ <> "" THEN OUT_FILE$ = ARGS$
2150 OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2160 PRINT #2%, EQU$ \ PRINT #2%, "  "; MOD_TITLE$ \ PRINT #2%, SEP$
2170 EI% = 1%
2180 IF EI% > NUM_ROWS% THEN GOTO 2230
2190 PRINT #2%, R_LBL$(EI%); " | Budget="; C_BUD%(EI%); "K | Actual="; C_ACT%(EI%); "K | Var="; C_VAR%(EI%); "K | Forecast="; C_FCT%(EI%); "K"
2200 EI% = EI% + 1% \ GOTO 2180
2230 PRINT #2%, EQU$ \ CLOSE #2%
2240 PRINT "[NYPLAN Executive P&L Report exported to "; OUT_FILE$; "]" \ GOTO 495
2350 IF NUM_ROWS% = 0% THEN GOTO 3370
2360 GOSUB 640 \ SV_FILE$ = MOD_FILE$
2370 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
2380 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
2390 IF SI% > NUM_ROWS% THEN GOTO 2430
2400 PRINT #2%, R_LBL$(SI%); "|"; C_BUD%(SI%); "|"; C_ACT%(SI%); "|"; R_RULE$(SI%)
2410 SI% = SI% + 1% \ GOTO 2390
2430 CLOSE #2% \ PRINT "["; NUM_ROWS%; " NYPLAN model rows saved to "; SV_FILE$; "]" \ GOTO 495
2500 LD_FILE$ = MOD_FILE$
2510 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
2520 ON ERROR GOTO 2650 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ROWS% = 0%
2530 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
2540 IF T_OUT$ = "" THEN GOTO 2530
2550 P1% = INSTR(1%, T_OUT$, "|")
2560 IF P1% = 0% THEN GOTO 2530
2570 F_LBL$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
2580 IF P2% = 0% THEN GOTO 2530
2590 F_BUD% = VAL(LEFT$(REM1$, P2% - 1%)) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2600 IF P3% = 0% THEN GOTO 2530
2610 F_ACT% = VAL(LEFT$(REM2$, P3% - 1%)) \ F_RUL$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%)
2620 NUM_ROWS% = NUM_ROWS% + 1% \ R_LBL$(NUM_ROWS%) = F_LBL$ \ C_BUD%(NUM_ROWS%) = F_BUD% \ C_ACT%(NUM_ROWS%) = F_ACT% \ R_RULE$(NUM_ROWS%) = F_RUL$ \ GOTO 2530
2650 CLOSE #2% \ RESUME 2660
2660 ON ERROR GOTO 0 \ GOSUB 640 \ PRINT "["; NUM_ROWS%; " NYPLAN model rows loaded from "; LD_FILE$; "]" \ GOTO 495
2800 GOSUB 640 \ PRINT "NYPLAN V4.1 Financial Modeling Status:" \ PRINT "  Model File:     "; MOD_FILE$; " (Divisions Consolidated: "; DIV_CNT%; ")"
2810 PRINT "  Active Rows:    "; NUM_ROWS%; " | Actual Net Profit: "; C_ACT%(6%); "K | Forecast Net: "; C_FCT%(6%); "K" \ GOTO 495
2900 NUM_ROWS% = 0% \ DIV_CNT% = 1% \ PRINT "[NYPLAN financial model cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    NYPLAN V4.1 Corporate Financial Modeling Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample corporate P&L & budget model" \ PRINT "  MODEL / GRID / VIEW              Display Budget, Actual, Variance & Forecast"
3020 PRINT "  SET <row#>, <budget>, <actual>   Update P&L line item and recalculate model" \ PRINT "  LABEL <row#>, <title>            Set or add P&L line item description"
3030 PRINT "  WHATIF [rev_pct, cost_pct]       Run 'What-If' sensitivity analysis" \ PRINT "  MONTECARLO [trials] / RISK       Run Monte Carlo variance & risk simulation"
3040 PRINT "  CONSOLIDATE [pct] / MERGE        Consolidate subsidiary division P&L" \ PRINT "  EXPORT [file] / REPORT           Export formatted executive P&L report"
3050 PRINT "  SAVE [file] / LOAD [file]        Save or load NYPLAN.DAT financial model" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear model, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "NYPLAN: Financial model is empty. Use SAMPLE or LABEL." \ GOTO 495
3400 END
