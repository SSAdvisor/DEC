10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM C_ID$(12%) \ DIM C_NAME$(12%) \ DIM C_MOD$(12%) \ DIM C_AMT%(12%)
20 NUM_REC% = 0% \ DB_FILE$ = "CJBIZ.DAT" \ SUB_COUNT% = 4250%
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Collier-Jackson CJ/BUSINESS V5.4 - CJ/GL, CJ/PAYROLL & CJ/CIRC Suite" \ PRINT "    Collier-Jackson, Inc. (Tampa, FL) - DEC PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load suite, CJGL, CJPAY, CJCIRC, or EXIT." \ PRINT ""
100 PRINT "CJ/BUSINESS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "CJGL" OR VERB$ = "GL" OR VERB$ = "LIST" THEN GOTO 820
360 IF VERB$ = "CJPAY" OR VERB$ = "PAYROLL" THEN GOTO 1020
370 IF VERB$ = "CJCIRC" OR VERB$ = "CIRC" OR VERB$ = "ADBILL" THEN GOTO 1180
380 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1320
390 IF VERB$ = "SAVE" THEN GOTO 1500
400 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1650
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1900
420 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2000
480 PRINT "CJ/BUSINESS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ SUB_COUNT% = 4250%
710 C_ID$(1%) = "CJ-100" \ C_NAME$(1%) = "Display Ad Revenue    " \ C_MOD$(1%) = "CJ/AD  " \ C_AMT%(1%) = 1420%
720 C_ID$(2%) = "CJ-200" \ C_NAME$(2%) = "Subscriber Circulation" \ C_MOD$(2%) = "CJ/CIRC" \ C_AMT%(2%) = 850%
730 C_ID$(3%) = "CJ-300" \ C_NAME$(3%) = "Editorial & Pressroom " \ C_MOD$(3%) = "CJ/PAY " \ C_AMT%(3%) = 640%
740 C_ID$(4%) = "CJ-400" \ C_NAME$(4%) = "Newsprint & Distribution" \ C_MOD$(4%) = "CJ/GL  " \ C_AMT%(4%) = 510%
750 PRINT "[Sample Collier-Jackson CJ/BUSINESS suite loaded - 4 module ledgers]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Collier-Jackson CJ/GL — Enterprise General Ledger Summary ("; DB_FILE$; ")" \ PRINT SEP$
840 PRINT "  Entry ID   Account / Module Name     Subsystem   Amount($K)" \ PRINT SEP$
850 RI% = 1% \ TOT_CJ% = 0%
860 IF RI% > NUM_REC% THEN GOTO 930
870 TOT_CJ% = TOT_CJ% + C_AMT%(RI%)
880 ID_P$ = LEFT$(C_ID$(RI%) + BLANKS$, 9%) \ NM_P$ = LEFT$(C_NAME$(RI%) + BLANKS$, 24%) \ MD_P$ = LEFT$(C_MOD$(RI%) + BLANKS$, 10%)
890 PRINT "  "; ID_P$; "  "; NM_P$; "  "; MD_P$; "  "; C_AMT%(RI%)
900 RI% = RI% + 1% \ GOTO 860
930 PRINT SEP$ \ PRINT "  [CJ/GL Ledger Control Total = $"; TOT_CJ%; "K across "; NUM_REC%; " accounts]" \ PRINT EQU$ \ GOTO 495
1020 IF NUM_REC% = 0% THEN GOTO 3370
1030 GROSS_P% = C_AMT%(3%) \ FICA_P% = INT((GROSS_P% * 7%) / 100%) \ FED_P% = INT((GROSS_P% * 18%) / 100%) \ NET_P% = GROSS_P% - FICA_P% - FED_P%
1040 PRINT EQU$ \ PRINT "  Collier-Jackson CJ/PAYROLL — Personnel & Payroll Register" \ PRINT SEP$
1050 PRINT "  Gross Payroll:  $"; GROSS_P%; "K | FICA Tax: $"; FICA_P%; "K | Fed Withholding: $"; FED_P%; "K"
1060 PRINT "  Net Disbursed:  $"; NET_P%; "K — Direct Deposit & Check Register Verified" \ PRINT EQU$ \ GOTO 495
1180 IF NUM_REC% = 0% THEN GOTO 3370
1190 IF ARGS$ <> "" THEN SUB_COUNT% = VAL(ARGS$)
1200 AD_REV% = C_AMT%(1%) \ CIRC_REV% = C_AMT%(2%) \ TOT_PUB% = AD_REV% + CIRC_REV%
1210 PRINT EQU$ \ PRINT "  Collier-Jackson CJ/CIRC & CJ/AD — Circulation & Advertising Billing" \ PRINT SEP$
1220 PRINT "  Active Subscribers: "; SUB_COUNT%; "00 | Carrier Routes: 185 | Renewal Rate: 91%"
1230 PRINT "  Circulation Billing: $"; CIRC_REV%; "K | Display & Classified Ad Billing: $"; AD_REV%; "K"
1240 PRINT "  Total Publishing Revenue: $"; TOT_PUB%; "K" \ PRINT EQU$ \ GOTO 495
1320 IF NUM_REC% >= 12% THEN GOTO 1460
1330 C1% = INSTR(1%, ARGS$, ",")
1340 IF C1% = 0% THEN GOTO 1450
1350 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ ID_V$ = U_OUT$
1360 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1370 IF C2% = 0% THEN GOTO 1450
1380 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ NM_V$ = T_OUT$
1390 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1400 IF C3% = 0% THEN GOTO 1450
1410 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ MD_V$ = U_OUT$
1420 AM_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1430 NUM_REC% = NUM_REC% + 1% \ C_ID$(NUM_REC%) = ID_V$ \ C_NAME$(NUM_REC%) = NM_V$ \ C_MOD$(NUM_REC%) = MD_V$ \ C_AMT%(NUM_REC%) = AM_V%
1440 PRINT "[CJ/BUSINESS Entry #"; NUM_REC%; " added: "; ID_V$; " ("; NM_V$; ", Module="; MD_V$; ", Amt=$"; AM_V%; "K)]" \ GOTO 495
1450 PRINT "CJ/BUSINESS: Syntax is ADD <id>, <name>, <module>, <amount_k>" \ GOTO 495
1460 PRINT "CJ/BUSINESS: Table full" \ GOTO 495
1500 IF NUM_REC% = 0% THEN GOTO 3370
1510 SV_FILE$ = DB_FILE$
1520 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1530 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1540 IF SI% > NUM_REC% THEN GOTO 1580
1550 PRINT #2%, C_ID$(SI%); "|"; C_NAME$(SI%); "|"; C_MOD$(SI%); "|"; C_AMT%(SI%)
1560 SI% = SI% + 1% \ GOTO 1540
1580 CLOSE #2% \ PRINT "["; NUM_REC%; " CJ/BUSINESS records saved to "; SV_FILE$; "]" \ GOTO 495
1650 LD_FILE$ = DB_FILE$
1660 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1670 ON ERROR GOTO 1800 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1680 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1690 IF T_OUT$ = "" THEN GOTO 1680
1700 P1% = INSTR(1%, T_OUT$, "|")
1710 IF P1% = 0% THEN GOTO 1680
1720 FID$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1730 IF P2% = 0% THEN GOTO 1680
1740 FNM$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1750 IF P3% = 0% THEN GOTO 1680
1760 FMD$ = LEFT$(REM2$, P3% - 1%) \ FAM% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1770 NUM_REC% = NUM_REC% + 1% \ C_ID$(NUM_REC%) = FID$ \ C_NAME$(NUM_REC%) = FNM$ \ C_MOD$(NUM_REC%) = FMD$ \ C_AMT%(NUM_REC%) = FAM% \ GOTO 1680
1800 CLOSE #2% \ RESUME 1810
1810 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " CJ/BUSINESS records loaded from "; LD_FILE$; "]" \ GOTO 495
1900 PRINT "Collier-Jackson CJ/BUSINESS V5.4 Status:" \ PRINT "  Master File:    "; DB_FILE$; " (Accounts: "; NUM_REC%; ", Subscribers: "; SUB_COUNT%; "00)"
1910 PRINT "  Active Suite:   CJ/GL, CJ/PAYROLL, CJ/CIRC, CJ/AD" \ GOTO 495
2000 NUM_REC% = 0% \ PRINT "[CJ/BUSINESS records cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Collier-Jackson CJ/BUSINESS V5.4 Enterprise Suite Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample CJ/GL, CJ/PAY, and CJ/CIRC data" \ PRINT "  CJGL / GL / LIST                 Display Enterprise General Ledger"
3020 PRINT "  CJPAY / PAYROLL                  Run CJ/PAYROLL register and tax calculation" \ PRINT "  CJCIRC [subs] / CIRC             Display CJ/CIRC & CJ/AD publishing billing"
3030 PRINT "  ADD <id>, <name>, <mod>, <amt>   Add ledger/module entry" \ PRINT "  SAVE [file] / LOAD [file]        Save or load CJBIZ.DAT file"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear records, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "CJ/BUSINESS: No records loaded. Use SAMPLE or ADD." \ GOTO 495
3400 END
