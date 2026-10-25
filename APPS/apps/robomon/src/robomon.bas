10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_RULE$(15%) \ DIM R_METRIC$(15%) \ DIM R_ACT$(15%) \ DIM R_VAL%(15%)
20 NUM_REC% = 0% \ MON_STATE$ = "ARMED" \ DB_FILE$ = "ROBOMON.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Heroix RoboMon V5.0 - Rule-Based VAX/VMS Operations Manager" \ PRINT "    Heroix Corporation (Newton, MA) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load rules, RULES, EVALUATE, AUTOCORRECT, EXIT." \ PRINT ""
100 PRINT "ROBOMON> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "RULES" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "EVALUATE" OR VERB$ = "ALERTS" THEN GOTO 960
370 IF VERB$ = "AUTOCORRECT" OR VERB$ = "FIX" THEN GOTO 1150
380 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
390 IF VERB$ = "SAVE" THEN GOTO 1550
400 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
420 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "ROBOMON: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ MON_STATE$ = "ARMED"
710 R_RULE$(1%) = "RL-MEM01" \ R_METRIC$(1%) = "Hard Page Faults/s " \ R_ACT$(1%) = "SET WS_EXT" \ R_VAL%(1%) = 145%
720 R_RULE$(2%) = "RL-DSK02" \ R_METRIC$(2%) = "DKA0: Used Pct (%) " \ R_ACT$(2%) = "PURGE_LOGS" \ R_VAL%(2%) = 94%
730 R_RULE$(3%) = "RL-QUE03" \ R_METRIC$(3%) = "SYS$BATCH Stalled  " \ R_ACT$(3%) = "START_QUE " \ R_VAL%(3%) = 120%
740 R_RULE$(4%) = "RL-CPU04" \ R_METRIC$(4%) = "COM Compute Queue  " \ R_ACT$(4%) = "NO_ACTION " \ R_VAL%(4%) = 42%
750 PRINT "[Sample Heroix RoboMon V5.0 VMS rule base loaded - 4 operational rules]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Heroix RoboMon V5.0 Knowledge Base (State: "; MON_STATE$; ") — File: "; DB_FILE$ \ PRINT SEP$
840 PRINT "  Seq   RuleID     Monitored VMS Metric   DCL Action   Level(%)" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_REC% THEN GOTO 920
870 K_P$ = LEFT$(R_RULE$(LI%) + BLANKS$, 9%) \ M_P$ = LEFT$(R_METRIC$(LI%) + BLANKS$, 21%) \ A_P$ = LEFT$(R_ACT$(LI%) + BLANKS$, 11%)
880 PRINT "  "; LI%; "     "; K_P$; "  "; M_P$; "  "; A_P$; "  "; R_VAL%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_REC% = 0% THEN GOTO 3370
970 THR% = 85%
980 IF ARGS$ <> "" THEN THR% = VAL(ARGS$)
990 PRINT EQU$ \ PRINT "  Heroix RoboMon Rule Engine — Evaluating VMS Thresholds (Limit > "; THR%; "%)" \ PRINT SEP$
1000 EI% = 1% \ AL_CNT% = 0%
1010 IF EI% > NUM_REC% THEN GOTO 1090
1020 IF R_VAL%(EI%) <= THR% THEN GOTO 1070
1030 AL_CNT% = AL_CNT% + 1%
1040 K_P$ = LEFT$(R_RULE$(EI%) + BLANKS$, 9%) \ M_P$ = LEFT$(R_METRIC$(EI%) + BLANKS$, 21%)
1050 PRINT "  %ROBOMON-W-ALERT, "; K_P$; " ("; M_P$; ") = "; R_VAL%(EI%); "% -> Trigger: "; R_ACT$(EI%)
1070 EI% = EI% + 1% \ GOTO 1010
1090 IF AL_CNT% > 0% THEN MON_STATE$ = "ALERT"
1100 IF AL_CNT% = 0% THEN MON_STATE$ = "NOMINAL"
1110 PRINT SEP$ \ PRINT "  [RoboMon EVALUATE Complete: "; AL_CNT%; " of "; NUM_REC%; " rules triggered OPCOM alerts]" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_REC% = 0% THEN GOTO 3370
1160 PRINT EQU$ \ PRINT "  Heroix RoboMon Automated DCL Corrective Action Dispatcher" \ PRINT SEP$
1170 FI% = 1% \ FX_CNT% = 0%
1180 IF FI% > NUM_REC% THEN GOTO 1270
1190 IF R_VAL%(FI%) <= 85% THEN GOTO 1250
1200 FX_CNT% = FX_CNT% + 1% \ OLD_V% = R_VAL%(FI%) \ R_VAL%(FI%) = 50%
1210 PRINT "  $ ! Executing DCL Rule "; R_RULE$(FI%); " Action: "; R_ACT$(FI%); " (Was "; OLD_V%; "% -> Now 50%)"
1250 FI% = FI% + 1% \ GOTO 1180
1270 MON_STATE$ = "NOMINAL"
1280 PRINT SEP$ \ PRINT "  [RoboMon AUTOCORRECT Complete: "; FX_CNT%; " DCL corrective actions executed | State=NOMINAL]" \ PRINT EQU$ \ GOTO 495
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
1490 NUM_REC% = NUM_REC% + 1% \ R_RULE$(NUM_REC%) = K_V$ \ R_METRIC$(NUM_REC%) = N_V$ \ R_ACT$(NUM_REC%) = G_V$ \ R_VAL%(NUM_REC%) = VL_V%
1495 PRINT "[RoboMon Rule #"; NUM_REC%; " added: "; K_V$; " ("; N_V$; ", Level="; VL_V%; "%)]" \ GOTO 495
1500 PRINT "ROBOMON: Syntax is ADD <rule_id>, <metric>, <dcl_action>, <level_pct>" \ GOTO 495
1510 PRINT "ROBOMON: Rule table full" \ GOTO 495
1550 IF NUM_REC% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_REC% THEN GOTO 1630
1600 PRINT #2%, R_RULE$(SI%); "|"; R_METRIC$(SI%); "|"; R_ACT$(SI%); "|"; R_VAL%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_REC%; " RoboMon rules saved to "; SV_FILE$; "]" \ GOTO 495
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
1820 NUM_REC% = NUM_REC% + 1% \ R_RULE$(NUM_REC%) = FK$ \ R_METRIC$(NUM_REC%) = FN$ \ R_ACT$(NUM_REC%) = FG$ \ R_VAL%(NUM_REC%) = FV% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " RoboMon rules loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Heroix RoboMon V5.0 Operations Status:" \ PRINT "  Active RuleDB:  "; DB_FILE$; " (Rules: "; NUM_REC%; ", Monitor State: "; MON_STATE$; ")" \ GOTO 495
2050 NUM_REC% = 0% \ MON_STATE$ = "ARMED" \ PRINT "[RoboMon rule base cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Heroix RoboMon V5.0 Rule-Based Operations Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample VAX/VMS operational rules" \ PRINT "  RULES / LIST                     Display monitored system rules"
3020 PRINT "  EVALUATE [limit] / ALERTS        Evaluate rules & flag OPCOM violations" \ PRINT "  AUTOCORRECT / FIX                Execute automated DCL corrective actions"
3030 PRINT "  ADD <id>, <metric>, <act>, <val> Add operational rule to knowledge base" \ PRINT "  SAVE [file] / LOAD [file]        Save or load ROBOMON.DAT rule base"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear rules, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "ROBOMON: Rule base is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
