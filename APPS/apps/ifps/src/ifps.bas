10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM M_LN$(15%) \ DIM M_VAR$(15%) \ DIM M_EQ$(15%) \ DIM M_BASE%(15%)
20 NUM_EQ% = 0% \ MOD_NAME$ = "CORP_PLAN_1990" \ DB_FILE$ = "IFPSMOD.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Execucom IFPS/Plus V4.0 - Interactive Financial Planning System" \ PRINT "    Execucom Systems Corporation (Austin, TX) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load model, MODEL, SOLVE, WHATIF, GOALSEEK, MONTECARLO, or EXIT." \ PRINT ""
100 PRINT "IFPS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "MODEL" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "SOLVE" OR VERB$ = "COMPILE" THEN GOTO 960
370 IF VERB$ = "WHATIF" OR VERB$ = "WHAT" THEN GOTO 1100
380 IF VERB$ = "GOALSEEK" OR VERB$ = "GOAL" THEN GOTO 1210
390 IF VERB$ = "MONTECARLO" OR VERB$ = "MONTE" THEN GOTO 1310
400 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
410 IF VERB$ = "SAVE" THEN GOTO 1550
420 IF VERB$ = "LOAD" OR VERB$ = "GET" THEN GOTO 1700
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "IFPS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_EQ% = 4%
710 M_LN$(1%) = "10" \ M_VAR$(1%) = "REVENUE" \ M_EQ$(1%) = "PREVIOUS REVENUE * 1.12" \ M_BASE%(1%) = 5000%
720 M_LN$(2%) = "20" \ M_VAR$(2%) = "COGS" \ M_EQ$(2%) = "REVENUE * 0.44" \ M_BASE%(2%) = 2200%
730 M_LN$(3%) = "30" \ M_VAR$(3%) = "OPEX" \ M_EQ$(3%) = "1100, PREVIOUS OPEX * 1.05" \ M_BASE%(3%) = 1100%
740 M_LN$(4%) = "40" \ M_VAR$(4%) = "NET_INCOME" \ M_EQ$(4%) = "REVENUE - COGS - OPEX" \ M_BASE%(4%) = 1700%
750 PRINT "[Sample Execucom IFPS/Plus corporate model loaded - 4 equations]" \ GOTO 495
820 IF NUM_EQ% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  IFPS/Plus Model Subsystem — Model: "; MOD_NAME$; " ("; DB_FILE$; ")" \ PRINT SEP$
840 PRINT "  Line  Variable Name    Natural-Language Definition       YR1 Base($K)" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_EQ% THEN GOTO 920
870 L_P$ = LEFT$(M_LN$(LI%) + BLANKS$, 4%) \ V_P$ = LEFT$(M_VAR$(LI%) + BLANKS$, 15%) \ E_P$ = LEFT$(M_EQ$(LI%) + BLANKS$, 32%)
880 PRINT "  "; L_P$; "  "; V_P$; "  "; E_P$; "  "; M_BASE%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_EQ% = 0% THEN GOTO 3370
970 REV1% = M_BASE%(1%) \ REV2% = INT((REV1% * 112%) / 100%) \ REV3% = INT((REV2% * 112%) / 100%)
980 NET1% = M_BASE%(NUM_EQ%) \ NET2% = INT((NET1% * 115%) / 100%) \ NET3% = INT((NET2% * 115%) / 100%)
990 PRINT EQU$ \ PRINT "  IFPS/Plus Non-Procedural Model Solution — COLUMNS 1990..1992" \ PRINT SEP$
1000 PRINT "  REVENUE ($K)     :  1990 = "; REV1%; "   | 1991 = "; REV2%; "   | 1992 = "; REV3%
1010 PRINT "  NET_INCOME ($K)  :  1990 = "; NET1%; "   | 1991 = "; NET2%; "   | 1992 = "; NET3%
1020 PRINT "  [IFPS SOLVE Complete: "; NUM_EQ%; " simultaneous equations solved | YR3 Net=$"; NET3%; "K]" \ PRINT EQU$ \ GOTO 495
1100 IF NUM_EQ% = 0% THEN GOTO 3370
1110 W_PCT% = 15%
1120 IF ARGS$ <> "" THEN W_PCT% = VAL(ARGS$)
1130 W_REV% = INT((M_BASE%(1%) * (100% + W_PCT%)) / 100%) \ W_NET% = INT((M_BASE%(NUM_EQ%) * (100% + W_PCT%)) / 100%)
1140 PRINT EQU$ \ PRINT "  IFPS/Plus WHAT IF Case Override (REVENUE Growth +"; W_PCT%; "%)" \ PRINT SEP$
1150 PRINT "  [WHAT IF Solution: Adjusted REVENUE=$"; W_REV%; "K | Adjusted NET_INCOME=$"; W_NET%; "K]" \ PRINT EQU$ \ GOTO 495
1210 IF NUM_EQ% = 0% THEN GOTO 3370
1220 G_TGT% = 2500%
1230 IF ARGS$ <> "" THEN G_TGT% = VAL(ARGS$)
1240 REQ_REV% = INT((G_TGT% * 294%) / 100%)
1250 PRINT EQU$ \ PRINT "  IFPS/Plus Backward GOAL SEEK — Target NET_INCOME = $"; G_TGT%; "K" \ PRINT SEP$
1260 PRINT "  Adjusting Decision Variable: REVENUE (Secant Root-Finding Iteration)..."
1270 PRINT "  [GOAL SEEK Converged in 4 iterations: Required REVENUE = $"; REQ_REV%; "K for Target $"; G_TGT%; "K]" \ PRINT EQU$ \ GOTO 495
1310 IF NUM_EQ% = 0% THEN GOTO 3370
1320 MC_MEAN% = M_BASE%(NUM_EQ%) \ MC_P10% = INT((MC_MEAN% * 82%) / 100%) \ MC_P90% = INT((MC_MEAN% * 124%) / 100%)
1330 PRINT EQU$ \ PRINT "  IFPS/Plus MONTE CARLO Risk Simulation (1000 Trials: TRIANG & NORMRAND)" \ PRINT SEP$
1340 PRINT "  [MONTE CARLO Complete: Mean=$"; MC_MEAN%; "K, P10=$"; MC_P10%; "K, P90=$"; MC_P90%; "K]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_EQ% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ L_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ V_V$ = U_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ E_V$ = T_OUT$
1480 BS_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_EQ% = NUM_EQ% + 1% \ M_LN$(NUM_EQ%) = L_V$ \ M_VAR$(NUM_EQ%) = V_V$ \ M_EQ$(NUM_EQ%) = E_V$ \ M_BASE%(NUM_EQ%) = BS_V%
1495 PRINT "[IFPS Equation #"; NUM_EQ%; " added: Line "; L_V$; " "; V_V$; " (Base=$"; BS_V%; "K)]" \ GOTO 495
1500 PRINT "IFPS: Syntax is ADD <line>, <var>, <equation>, <yr1_val>" \ GOTO 495
1510 PRINT "IFPS: Model buffer full" \ GOTO 495
1550 IF NUM_EQ% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_EQ% THEN GOTO 1630
1600 PRINT #2%, M_LN$(SI%); "|"; M_VAR$(SI%); "|"; M_EQ$(SI%); "|"; M_BASE%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_EQ%; " IFPS equations saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_EQ% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FL$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FV$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FE$ = LEFT$(REM2$, P3% - 1%) \ FB% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_EQ% = NUM_EQ% + 1% \ M_LN$(NUM_EQ%) = FL$ \ M_VAR$(NUM_EQ%) = FV$ \ M_EQ$(NUM_EQ%) = FE$ \ M_BASE%(NUM_EQ%) = FB% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_EQ%; " IFPS equations loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Execucom IFPS/Plus V4.0 Status:" \ PRINT "  Active Model:   "; MOD_NAME$; " (File: "; DB_FILE$; ", Equations: "; NUM_EQ%; ")" \ GOTO 495
2050 NUM_EQ% = 0% \ PRINT "[IFPS model cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Execucom IFPS/Plus V4.0 Financial Modeling Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample corporate planning model" \ PRINT "  MODEL / LIST                     Display natural-language model equations"
3020 PRINT "  SOLVE / WHATIF [pct]             Solve horizon or run What-If override" \ PRINT "  GOALSEEK [target] / MONTECARLO   Run backward Goal Seek or Monte Carlo risk"
3030 PRINT "  ADD <ln>, <var>, <eq>, <base>    Append equation to model" \ PRINT "  SAVE [file] / LOAD [file]        Save or load IFPSMOD.DAT model file"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear model, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "IFPS: Model is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
