10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM A_SEG$(12%) \ DIM A_DESC$(12%) \ DIM A_DR%(12%) \ DIM A_CR%(12%)
20 NUM_ACT% = 0% \ DB_FILE$ = "DIGIGL.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Timeline DIGI-GL V4.3 - Multi-Segmented General Ledger & Report Writer" \ PRINT "    Timeline, Inc. (Bellevue, WA) - 36-Character Segmented COA Engine" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load ledger, COA, TRIAL, POST, FINRPT, or EXIT." \ PRINT ""
100 PRINT "TIMELINE> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "COA" OR VERB$ = "LIST" OR VERB$ = "TRIAL" OR VERB$ = "BALANCE" THEN GOTO 820
360 IF VERB$ = "POST" OR VERB$ = "ADD" THEN GOTO 1050
370 IF VERB$ = "FINRPT" OR VERB$ = "REPORT" OR VERB$ = "EXPORT" THEN GOTO 1250
380 IF VERB$ = "SAVE" THEN GOTO 1450
390 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1600
400 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1850
410 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 1950
480 PRINT "TIMELINE: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_ACT% = 4%
710 A_SEG$(1%) = "01-100-000-1010-000" \ A_DESC$(1%) = "Operating Cash - Fund 01" \ A_DR%(1%) = 1850% \ A_CR%(1%) = 0%
720 A_SEG$(2%) = "01-200-110-1200-001" \ A_DESC$(2%) = "Trade Receivables NW    " \ A_DR%(2%) = 950%  \ A_CR%(2%) = 0%
730 A_SEG$(3%) = "01-100-000-2010-000" \ A_DESC$(3%) = "Vouchers Payable        " \ A_DR%(3%) = 0%    \ A_CR%(3%) = 600%
740 A_SEG$(4%) = "01-200-110-4000-001" \ A_DESC$(4%) = "System Sales Revenue NW " \ A_DR%(4%) = 0%    \ A_CR%(4%) = 2200%
750 PRINT "[Sample Timeline DIGI-GL multi-segmented ledger loaded - 4 segmented accounts]" \ GOTO 495
820 IF NUM_ACT% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Timeline DIGI-GL — Multi-Segmented Chart of Accounts & Trial Balance" \ PRINT "  Segment Mask: [FUND(2)-DIV(3)-DEPT(3)-NAT(4)-SUB(3)]" \ PRINT SEP$
840 PRINT "  Segmented Account      Account Description        Debit($K)    Credit($K)" \ PRINT SEP$
850 AI% = 1% \ TOT_DR% = 0% \ TOT_CR% = 0%
860 IF AI% > NUM_ACT% THEN GOTO 940
870 TOT_DR% = TOT_DR% + A_DR%(AI%) \ TOT_CR% = TOT_CR% + A_CR%(AI%)
880 S_PAD$ = LEFT$(A_SEG$(AI%) + BLANKS$, 21%) \ D_PAD$ = LEFT$(A_DESC$(AI%) + BLANKS$, 25%)
890 PRINT "  "; S_PAD$; "  "; D_PAD$; "  "; A_DR%(AI%); "           "; A_CR%(AI%)
900 AI% = AI% + 1% \ GOTO 860
940 BAL_ST$ = "IN BALANCE"
950 IF TOT_DR% <> TOT_CR% THEN BAL_ST$ = "OUT OF BALANCE"
960 PRINT SEP$ \ PRINT "  [DIGI-GL Trial Balance: Total Debits=$"; TOT_DR%; "K | Total Credits=$"; TOT_CR%; "K — "; BAL_ST$; "]" \ PRINT EQU$ \ GOTO 495
1050 IF NUM_ACT% >= 12% THEN GOTO 1210
1060 C1% = INSTR(1%, ARGS$, ",")
1070 IF C1% = 0% THEN GOTO 1200
1080 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ SG_V$ = T_OUT$
1090 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1100 IF C2% = 0% THEN GOTO 1200
1110 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ DS_V$ = T_OUT$
1120 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1130 IF C3% = 0% THEN GOTO 1200
1140 DR_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ CR_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1150 NUM_ACT% = NUM_ACT% + 1% \ A_SEG$(NUM_ACT%) = SG_V$ \ A_DESC$(NUM_ACT%) = DS_V$ \ A_DR%(NUM_ACT%) = DR_V% \ A_CR%(NUM_ACT%) = CR_V%
1160 PRINT "[DIGI-GL Account #"; NUM_ACT%; " posted: "; SG_V$; " (Dr=$"; DR_V%; "K, Cr=$"; CR_V%; "K)]" \ GOTO 495
1200 PRINT "TIMELINE: Syntax is POST <seg_acct>, <desc>, <debit_k>, <credit_k>" \ GOTO 495
1210 PRINT "TIMELINE: Ledger table full" \ GOTO 495
1250 IF NUM_ACT% = 0% THEN GOTO 3370
1260 OUT_F$ = "DIGIRPT.TXT"
1270 IF ARGS$ <> "" THEN OUT_F$ = ARGS$
1280 OPEN OUT_F$ FOR OUTPUT AS FILE #2%
1290 PRINT #2%, "TIMELINE DIGI-GL FINANCIAL REPORT WRITER"
1300 AI% = 1%
1310 IF AI% > NUM_ACT% THEN GOTO 1350
1320 PRINT #2%, A_SEG$(AI%); "|"; A_DESC$(AI%); "|DR="; A_DR%(AI%); "|CR="; A_CR%(AI%)
1330 AI% = AI% + 1% \ GOTO 1310
1350 CLOSE #2% \ PRINT "[Timeline DIGI-GL Financial Report written to "; OUT_F$; "]" \ GOTO 495
1450 IF NUM_ACT% = 0% THEN GOTO 3370
1460 SV_FILE$ = DB_FILE$
1470 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1480 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1490 IF SI% > NUM_ACT% THEN GOTO 1530
1500 PRINT #2%, A_SEG$(SI%); "|"; A_DESC$(SI%); "|"; A_DR%(SI%); "|"; A_CR%(SI%)
1510 SI% = SI% + 1% \ GOTO 1490
1530 CLOSE #2% \ PRINT "["; NUM_ACT%; " DIGI-GL segmented accounts saved to "; SV_FILE$; "]" \ GOTO 495
1600 LD_FILE$ = DB_FILE$
1610 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1620 ON ERROR GOTO 1750 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ACT% = 0%
1630 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1640 IF T_OUT$ = "" THEN GOTO 1630
1650 P1% = INSTR(1%, T_OUT$, "|")
1660 IF P1% = 0% THEN GOTO 1630
1670 FSG$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1680 IF P2% = 0% THEN GOTO 1630
1690 FDS$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1700 IF P3% = 0% THEN GOTO 1630
1710 FDR% = VAL(LEFT$(REM2$, P3% - 1%)) \ FCR% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1720 NUM_ACT% = NUM_ACT% + 1% \ A_SEG$(NUM_ACT%) = FSG$ \ A_DESC$(NUM_ACT%) = FDS$ \ A_DR%(NUM_ACT%) = FDR% \ A_CR%(NUM_ACT%) = FCR% \ GOTO 1630
1750 CLOSE #2% \ RESUME 1760
1760 ON ERROR GOTO 0 \ PRINT "["; NUM_ACT%; " DIGI-GL segmented accounts loaded from "; LD_FILE$; "]" \ GOTO 495
1850 PRINT "Timeline DIGI-GL V4.3 Status:" \ PRINT "  Ledger File:    "; DB_FILE$; " (Segmented Accounts: "; NUM_ACT%; ")"
1860 PRINT "  Segment Format: FUND-DIV-DEPT-NAT-SUB (Up to 36 chars)" \ GOTO 495
1950 NUM_ACT% = 0% \ PRINT "[DIGI-GL ledger cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Timeline DIGI-GL V4.3 Multi-Segmented Ledger Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample 5-segment Chart of Accounts" \ PRINT "  COA / TRIAL / BALANCE            Display segmented accounts & Trial Balance"
3020 PRINT "  POST <seg>, <desc>, <dr>, <cr>   Post segmented account entry" \ PRINT "  FINRPT [file] / REPORT           Generate custom financial report"
3030 PRINT "  SAVE [file] / LOAD [file]        Save or load DIGIGL.DAT ledger" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear ledger, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "TIMELINE: Ledger is empty. Use SAMPLE or POST." \ GOTO 495
3400 END
