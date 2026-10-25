10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM KB_LINE$(15%) \ DIM KB_USER$(15%) \ DIM KB_PROG$(15%) \ DIM KB_CMDS%(15%) \ DIM KB_RISK%(15%) \ DIM KB_LOCK%(15%)
20 NUM_KB% = 0% \ DB_FILE$ = "CAUDIT.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Clyde Digital Systems CONTRL / AUDIT / LOCK V4.1 - Security Monitor" \ PRINT "    Clyde Digital Systems (Provo, UT) - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load sessions, TERMINALS, OBSERVE, AUDIT, LOCK, or EXIT." \ PRINT ""
100 PRINT "CLYDE> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "TERMINALS" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "OBSERVE" OR VERB$ = "CONTRL" THEN GOTO 960
370 IF VERB$ = "AUDIT" OR VERB$ = "CAUDIT" THEN GOTO 1150
380 IF VERB$ = "LOCK" OR VERB$ = "INTRUDER" THEN GOTO 1280
390 IF VERB$ = "UNLOCK" THEN GOTO 1282
400 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
410 IF VERB$ = "SAVE" THEN GOTO 1550
420 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "CLYDE: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_KB% = 5%
710 KB_LINE$(1%) = "KB0:" \ KB_USER$(1%) = "[1,2] OPR  " \ KB_PROG$(1%) = "SYSTAT" \ KB_CMDS%(1%) = 42% \ KB_RISK%(1%) = 5% \ KB_LOCK%(1%) = 0%
720 KB_LINE$(2%) = "KB3:" \ KB_USER$(2%) = "[10,14] FIN" \ KB_PROG$(2%) = "MAPSGL" \ KB_CMDS%(2%) = 118% \ KB_RISK%(2%) = 10% \ KB_LOCK%(2%) = 0%
730 KB_LINE$(3%) = "KB7:" \ KB_USER$(3%) = "[20,55] DEV" \ KB_PROG$(3%) = "PIP   " \ KB_CMDS%(3%) = 64% \ KB_RISK%(3%) = 35% \ KB_LOCK%(3%) = 0%
740 KB_LINE$(4%) = "KB11:" \ KB_USER$(4%) = "[99,99] GST" \ KB_PROG$(4%) = "LOGIN " \ KB_CMDS%(4%) = 19% \ KB_RISK%(4%) = 85% \ KB_LOCK%(4%) = 0%
750 KB_LINE$(5%) = "KB14:" \ KB_USER$(5%) = "[1,4] BATCH" \ KB_PROG$(5%) = "FSORT3" \ KB_CMDS%(5%) = 310% \ KB_RISK%(5%) = 12% \ KB_LOCK%(5%) = 0%
760 PRINT "[Sample Clyde Security dataset loaded - 5 RSTS/E KB: sessions]" \ GOTO 495
820 IF NUM_KB% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Clyde Digital Systems — RSTS/E KB: Terminal Security Monitor" \ PRINT SEP$
840 LI% = 1%
860 IF LI% > NUM_KB% THEN GOTO 920
870 ST$ = "ACTIVE"
880 IF KB_RISK%(LI%) >= 75% THEN ST$ = "ALERT"
890 IF KB_LOCK%(LI%) = 1% THEN ST$ = "LOCKED"
900 PRINT "  "; KB_LINE$(LI%); "  "; KB_USER$(LI%); "  "; KB_PROG$(LI%); "  Cmds="; KB_CMDS%(LI%); "  Risk="; KB_RISK%(LI%); "%  ["; ST$; "]"
910 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_KB% = 0% THEN GOTO 3370
970 TGT$ = KB_LINE$(1%)
980 IF ARGS$ <> "" THEN U_IN$ = ARGS$
985 IF ARGS$ <> "" THEN GOSUB 580
990 IF ARGS$ <> "" THEN TGT$ = U_OUT$
1000 FI% = 0% \ LI% = 1%
1010 IF LI% > NUM_KB% THEN GOTO 1050
1020 IF KB_LINE$(LI%) = TGT$ THEN FI% = LI%
1030 LI% = LI% + 1% \ GOTO 1010
1050 IF FI% = 0% THEN GOTO 1130
1060 PRINT EQU$ \ PRINT "  Clyde CONTRL V4.1 - Live Terminal Mirror ["; KB_LINE$(FI%); "]" \ PRINT SEP$
1070 PRINT "  Account : "; KB_USER$(FI%); "   Program : "; KB_PROG$(FI%); "   Commands : "; KB_CMDS%(FI%); "   Risk : "; KB_RISK%(FI%); "%"
1080 PRINT "  Stream  : Ready > RUN $"; KB_PROG$(FI%); " [Keystroke stream mirrored to OPR]"
1090 IF KB_LOCK%(FI%) = 1% THEN PRINT "  Status  : TERMINAL FROZEN BY CLYDE INTRUDER LOCK"
1100 IF KB_LOCK%(FI%) = 0% THEN PRINT "  Status  : INTERACTIVE SESSION MONITORED"
1110 PRINT EQU$ \ GOTO 495
1130 PRINT "CLYDE: Terminal line not found: "; TGT$ \ GOTO 495
1150 IF NUM_KB% = 0% THEN GOTO 3370
1160 PRINT EQU$ \ PRINT "  Clyde CAUDIT V4.1 - RSTS/E Keystroke & Security Audit Trail" \ PRINT SEP$
1170 LI% = 1% \ TOT_C% = 0% \ HI_R% = 0% \ LK_C% = 0%
1180 IF LI% > NUM_KB% THEN GOTO 1250
1190 TOT_C% = TOT_C% + KB_CMDS%(LI%)
1200 IF KB_RISK%(LI%) >= 50% THEN HI_R% = HI_R% + 1%
1210 IF KB_LOCK%(LI%) = 1% THEN LK_C% = LK_C% + 1%
1220 PRINT "  [AUDIT] "; KB_LINE$(LI%); " "; KB_USER$(LI%); " Prog="; KB_PROG$(LI%); " Cmds="; KB_CMDS%(LI%); " Risk="; KB_RISK%(LI%); "%"
1230 LI% = LI% + 1% \ GOTO 1180
1250 PRINT SEP$ \ PRINT "  [CAUDIT Summary: Sessions="; NUM_KB%; " | Total Cmds="; TOT_C%; " | High-Risk="; HI_R%; " | Locked="; LK_C%; "]" \ PRINT EQU$ \ GOTO 495
1280 LK_VAL% = 1% \ GOTO 1285
1282 LK_VAL% = 0%
1285 IF NUM_KB% = 0% THEN GOTO 3370
1288 U_IN$ = ARGS$ \ GOSUB 580 \ TGT$ = U_OUT$ \ FI% = 0% \ LI% = 1%
1290 IF LI% > NUM_KB% THEN GOTO 1320
1300 IF KB_LINE$(LI%) = TGT$ THEN FI% = LI%
1310 LI% = LI% + 1% \ GOTO 1290
1320 IF FI% = 0% THEN GOTO 1130
1325 KB_LOCK%(FI%) = LK_VAL%
1330 IF LK_VAL% = 1% THEN PRINT "[Clyde LOCK: Terminal "; KB_LINE$(FI%); " FROZEN by Intruder Lock]"
1335 IF LK_VAL% = 0% THEN PRINT "[Clyde LOCK: Terminal "; KB_LINE$(FI%); " released]"
1338 GOTO 495
1380 IF NUM_KB% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ K_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_V$ = T_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ P_V$ = U_OUT$
1480 CM_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_KB% = NUM_KB% + 1% \ KB_LINE$(NUM_KB%) = K_V$ \ KB_USER$(NUM_KB%) = U_V$ \ KB_PROG$(NUM_KB%) = P_V$ \ KB_CMDS%(NUM_KB%) = CM_V% \ KB_RISK%(NUM_KB%) = 20% \ KB_LOCK%(NUM_KB%) = 0%
1495 PRINT "[Clyde Session #"; NUM_KB%; " added: "; K_V$; " ("; U_V$; ", Prog="; P_V$; ")]" \ GOTO 495
1500 PRINT "CLYDE: Syntax is ADD <kb>, <user>, <prog>, <cmds>" \ GOTO 495
1510 PRINT "CLYDE: Session table full" \ GOTO 495
1550 IF NUM_KB% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_KB% THEN GOTO 1630
1600 PRINT #2%, KB_LINE$(SI%); "|"; KB_USER$(SI%); "|"; KB_PROG$(SI%); "|"; KB_CMDS%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_KB%; " Clyde audit records saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_KB% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FK$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FU$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FP$ = LEFT$(REM2$, P3% - 1%) \ FC% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_KB% = NUM_KB% + 1% \ KB_LINE$(NUM_KB%) = FK$ \ KB_USER$(NUM_KB%) = FU$ \ KB_PROG$(NUM_KB%) = FP$ \ KB_CMDS%(NUM_KB%) = FC% \ KB_RISK%(NUM_KB%) = 20% \ KB_LOCK%(NUM_KB%) = 0% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_KB%; " Clyde audit records loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Clyde Digital Systems CONTRL / AUDIT / LOCK V4.1 Status:" \ PRINT "  Active File:    "; DB_FILE$; " (Sessions: "; NUM_KB%; ")" \ GOTO 495
2050 NUM_KB% = 0% \ PRINT "[Clyde session monitor cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Clyde Digital Systems CONTRL / AUDIT / LOCK V4.1 Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / TERMINALS               Load or list RSTS/E KB: sessions" \ PRINT "  OBSERVE [kb] / AUDIT             Mirror terminal or run CAUDIT report"
3020 PRINT "  LOCK <kb> / UNLOCK <kb>          Freeze or release KB: terminal line" \ PRINT "  ADD <kb>, <usr>, <prg>, <cmds>   Add monitored session"
3030 PRINT "  SAVE [file] / LOAD [file]        Save or load CAUDIT.DAT file" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear sessions, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "CLYDE: No sessions loaded. Use SAMPLE or ADD." \ GOTO 495
3400 END
