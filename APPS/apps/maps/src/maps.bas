10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM RC_CODE$(12%) \ DIM RC_NAME$(12%) \ DIM RC_BUD%(12%) \ DIM RC_ACT%(12%)
20 NUM_RC% = 0% \ DB_FILE$ = "MAPSGL.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Ross Systems MAPS V5.0 - Management Accounting & Planning System" \ PRINT "    Ross Systems, Inc. (Palo Alto, CA) - MAPS/GL, MAPS/MODEL, MAPS/AP, MAPS/AR" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load centers, CENTERS, VARIANCE, MODEL, or EXIT." \ PRINT ""
100 PRINT "MAPS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "CENTERS" OR VERB$ = "LIST" OR VERB$ = "GL" THEN GOTO 820
360 IF VERB$ = "VARIANCE" OR VERB$ = "VAR" THEN GOTO 1020
370 IF VERB$ = "MODEL" OR VERB$ = "PLAN" THEN GOTO 1180
380 IF VERB$ = "SUBLEDGER" OR VERB$ = "APAR" THEN GOTO 1350
390 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1500
400 IF VERB$ = "SAVE" THEN GOTO 1700
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1850
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2100
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2200
480 PRINT "MAPS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_RC% = 4%
710 RC_CODE$(1%) = "RC-100" \ RC_NAME$(1%) = "Corporate HQ & Admin  " \ RC_BUD%(1%) = 500% \ RC_ACT%(1%) = 480%
720 RC_CODE$(2%) = "RC-200" \ RC_NAME$(2%) = "Systems Engineering   " \ RC_BUD%(2%) = 850% \ RC_ACT%(2%) = 910%
730 RC_CODE$(3%) = "RC-300" \ RC_NAME$(3%) = "Manufacturing Ops     " \ RC_BUD%(3%) = 1200% \ RC_ACT%(3%) = 1150%
740 RC_CODE$(4%) = "RC-400" \ RC_NAME$(4%) = "North American Sales  " \ RC_BUD%(4%) = 650% \ RC_ACT%(4%) = 640%
750 PRINT "[Sample Ross Systems MAPS/GL hierarchy loaded - 4 Responsibility Centers]" \ GOTO 495
820 IF NUM_RC% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Ross Systems MAPS/GL — Hierarchical Responsibility Centers ("; DB_FILE$; ")" \ PRINT SEP$
840 PRINT "  Center   Responsibility Name      Budget($K)   Actual($K)   Var(Bud-Act)" \ PRINT SEP$
850 RI% = 1% \ TOT_B% = 0% \ TOT_A% = 0%
860 IF RI% > NUM_RC% THEN GOTO 940
870 V_RC% = RC_BUD%(RI%) - RC_ACT%(RI%) \ TOT_B% = TOT_B% + RC_BUD%(RI%) \ TOT_A% = TOT_A% + RC_ACT%(RI%)
880 C_PAD$ = LEFT$(RC_CODE$(RI%) + BLANKS$, 7%) \ N_PAD$ = LEFT$(RC_NAME$(RI%) + BLANKS$, 23%)
890 PRINT "  "; C_PAD$; "  "; N_PAD$; "  "; RC_BUD%(RI%); "          "; RC_ACT%(RI%); "          "; V_RC%
900 RI% = RI% + 1% \ GOTO 860
940 PRINT SEP$ \ PRINT "  [MAPS/GL Rollup: Total Budget=$"; TOT_B%; "K | Total Actual=$"; TOT_A%; "K | Net Favorable=$"; TOT_B% - TOT_A%; "K]" \ PRINT EQU$ \ GOTO 495
1020 IF NUM_RC% = 0% THEN GOTO 3370
1030 FAV_CNT% = 0% \ UNFAV_CNT% = 0% \ RI% = 1%
1040 IF RI% > NUM_RC% THEN GOTO 1100
1050 IF RC_ACT%(RI%) <= RC_BUD%(RI%) THEN FAV_CNT% = FAV_CNT% + 1%
1060 IF RC_ACT%(RI%) > RC_BUD%(RI%) THEN UNFAV_CNT% = UNFAV_CNT% + 1%
1070 RI% = RI% + 1% \ GOTO 1040
1100 PRINT "[MAPS/GL Variance Audit: "; FAV_CNT%; " Favorable Center(s), "; UNFAV_CNT%; " Unfavorable Center(s)]" \ GOTO 495
1180 IF NUM_RC% = 0% THEN GOTO 3370
1190 G_PCT% = 10%
1200 IF ARGS$ <> "" THEN G_PCT% = VAL(ARGS$)
1210 TOT_A% = 0% \ RI% = 1%
1220 IF RI% > NUM_RC% THEN GOTO 1250
1230 TOT_A% = TOT_A% + RC_ACT%(RI%) \ RI% = RI% + 1% \ GOTO 1220
1250 PROJ_B% = TOT_A% + INT((TOT_A% * G_PCT%) / 100%)
1260 PRINT "[MAPS/MODEL Executive Projection (+"; G_PCT%; "%): Current Actual=$"; TOT_A%; "K -> Next-Year Plan=$"; PROJ_B%; "K]" \ GOTO 495
1350 PRINT EQU$ \ PRINT "  Ross Systems MAPS/AP & MAPS/AR Subledger Integration" \ PRINT SEP$
1360 PRINT "  MAPS/AP Open Vouchers:   $420K (Current: $380K, Over 30: $40K)"
1370 PRINT "  MAPS/AR Open Invoices:   $960K (Current: $890K, Over 30: $70K)"
1380 PRINT "  Net Working Capital:     +$540K — Posted to MAPS/GL Control Accounts" \ PRINT EQU$ \ GOTO 495
1500 IF NUM_RC% >= 12% THEN GOTO 1640
1510 C1% = INSTR(1%, ARGS$, ",")
1520 IF C1% = 0% THEN GOTO 1630
1530 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ CD_V$ = U_OUT$
1540 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1550 IF C2% = 0% THEN GOTO 1630
1560 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ NM_V$ = T_OUT$
1570 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1580 IF C3% = 0% THEN GOTO 1630
1590 BD_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ AC_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1600 NUM_RC% = NUM_RC% + 1% \ RC_CODE$(NUM_RC%) = CD_V$ \ RC_NAME$(NUM_RC%) = NM_V$ \ RC_BUD%(NUM_RC%) = BD_V% \ RC_ACT%(NUM_RC%) = AC_V%
1610 PRINT "[MAPS/GL Center #"; NUM_RC%; " added: "; CD_V$; " ("; NM_V$; ", Budget=$"; BD_V%; "K, Actual=$"; AC_V%; "K)]" \ GOTO 495
1630 PRINT "MAPS: Syntax is ADD <rc_code>, <name>, <budget_k>, <actual_k>" \ GOTO 495
1640 PRINT "MAPS: Responsibility center table full" \ GOTO 495
1700 IF NUM_RC% = 0% THEN GOTO 3370
1710 SV_FILE$ = DB_FILE$
1720 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1730 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1740 IF SI% > NUM_RC% THEN GOTO 1780
1750 PRINT #2%, RC_CODE$(SI%); "|"; RC_NAME$(SI%); "|"; RC_BUD%(SI%); "|"; RC_ACT%(SI%)
1760 SI% = SI% + 1% \ GOTO 1740
1780 CLOSE #2% \ PRINT "["; NUM_RC%; " MAPS/GL Responsibility Centers saved to "; SV_FILE$; "]" \ GOTO 495
1850 LD_FILE$ = DB_FILE$
1860 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1870 ON ERROR GOTO 2000 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_RC% = 0%
1880 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1890 IF T_OUT$ = "" THEN GOTO 1880
1900 P1% = INSTR(1%, T_OUT$, "|")
1910 IF P1% = 0% THEN GOTO 1880
1920 FCD$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1930 IF P2% = 0% THEN GOTO 1880
1940 FNM$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1950 IF P3% = 0% THEN GOTO 1880
1960 FBD% = VAL(LEFT$(REM2$, P3% - 1%)) \ FAC% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1970 NUM_RC% = NUM_RC% + 1% \ RC_CODE$(NUM_RC%) = FCD$ \ RC_NAME$(NUM_RC%) = FNM$ \ RC_BUD%(NUM_RC%) = FBD% \ RC_ACT%(NUM_RC%) = FAC% \ GOTO 1880
2000 CLOSE #2% \ RESUME 2010
2010 ON ERROR GOTO 0 \ PRINT "["; NUM_RC%; " MAPS/GL Responsibility Centers loaded from "; LD_FILE$; "]" \ GOTO 495
2100 PRINT "Ross Systems MAPS V5.0 Status:" \ PRINT "  Master File:    "; DB_FILE$; " (Responsibility Centers: "; NUM_RC%; ")"
2110 PRINT "  Active Suite:   MAPS/GL, MAPS/MODEL, MAPS/AP, MAPS/AR" \ GOTO 495
2200 NUM_RC% = 0% \ PRINT "[MAPS/GL hierarchy cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Ross Systems MAPS V5.0 Accounting & Planning Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample Responsibility Centers" \ PRINT "  CENTERS / LIST / GL              Display hierarchical Responsibility Centers"
3020 PRINT "  VARIANCE / VAR                   Audit Favorable vs. Unfavorable centers" \ PRINT "  MODEL [growth_pct] / PLAN        Run MAPS/MODEL executive budget projection"
3030 PRINT "  SUBLEDGER / APAR                 Display MAPS/AP and MAPS/AR integration" \ PRINT "  ADD <code>, <name>, <bud>, <act> Add Responsibility Center"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load MAPSGL.DAT file" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear memory, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "MAPS: No Responsibility Centers loaded. Use SAMPLE or ADD." \ GOTO 495
3400 END
