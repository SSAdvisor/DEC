10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM O_NO$(15%) \ DIM O_CUST$(15%) \ DIM O_BR$(15%) \ DIM O_AMT%(15%)
20 NUM_REC% = 0% \ PHD_NM$ = "CORP_PHD" \ QK_SCR$ = "ORD_QUICK" \ DB_FILE$ = "PHDICT.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Cognos PowerHouse 4GL V5.0 - PDL, QUICK, QUIZ & QTP Suite" \ PRINT "    Cognos Incorporated (Ottawa, Ontario) - DEC VAX/VMS Commercial 4GL" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load PHD, PDL, QUICK, QUIZ, QTP, or EXIT." \ PRINT ""
100 PRINT "PHOUSE> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "PDL" OR VERB$ = "SCHEMA" OR VERB$ = "DICT" THEN GOTO 820
360 IF VERB$ = "QUICK" OR VERB$ = "SCREEN" THEN GOTO 920
370 IF VERB$ = "QUIZ" OR VERB$ = "LIST" OR VERB$ = "REPORT" THEN GOTO 1060
380 IF VERB$ = "QTP" OR VERB$ = "BATCH" THEN GOTO 1280
390 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1450
400 IF VERB$ = "SAVE" THEN GOTO 1650
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1800
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2050
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2150
480 PRINT "*E* PowerHouse: Unknown 4GL command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ PHD_NM$ = "CORP_PHD" \ QK_SCR$ = "ORD_QUICK"
710 O_NO$(1%) = "P-1001" \ O_CUST$(1%) = "Northern Telecom  " \ O_BR$(1%) = "OTTAWA" \ O_AMT%(1%) = 640%
720 O_NO$(2%) = "P-1002" \ O_CUST$(2%) = "Royal Bank Canada " \ O_BR$(2%) = "TORONT" \ O_AMT%(2%) = 920%
730 O_NO$(3%) = "P-1003" \ O_CUST$(3%) = "Bell Canada Ent   " \ O_BR$(3%) = "OTTAWA" \ O_AMT%(3%) = 480%
740 O_NO$(4%) = "P-1004" \ O_CUST$(4%) = "Hydro-Quebec Corp " \ O_BR$(4%) = "MONTRL" \ O_AMT%(4%) = 760%
750 PRINT "[Sample Cognos PowerHouse Dictionary "; PHD_NM$; " loaded - 4 RMS records in ORDERS]" \ GOTO 495
820 PRINT EQU$ \ PRINT "  Cognos PowerHouse PDL V5.0 Dictionary Definition: "; PHD_NM$; ".PHD" \ PRINT SEP$
830 PRINT "  RECORD ORDERS ORGANIZATION INDEXED FILE 'ORDERS.RMS'"
840 PRINT "  ITEMS: ORDER-NO(CHAR 6 KEY), CUST-NAME(CHAR 18), BRANCH-CODE(CHAR 6), ORDER-AMT(INT 4)" \ PRINT EQU$ \ GOTO 495
920 IF ARGS$ <> "" THEN QK_SCR$ = ARGS$
930 U_IN$ = QK_SCR$ \ GOSUB 580 \ QK_SCR$ = U_OUT$
940 PRINT EQU$ \ PRINT "  Cognos QUICK V5.0 VT220 Interactive Screen Design — Screen: "; QK_SCR$; ".QKC" \ PRINT SEP$
950 PRINT "  | COGNOS QUICK V5.0 SCREEN: "; QK_SCR$; "  01 ORDER-NO:[______] 02 BRANCH:[______] |"
960 PRINT "  | 03 CUST-NAME:[__________________] 04 ORDER-AMT:[______]($K) ACTION:[UR] |"
970 PRINT "  [QUICK Screen "; QK_SCR$; ".QKC compiled against PHD "; PHD_NM$; " — 4 fields validated]" \ PRINT EQU$ \ GOTO 495
1060 IF NUM_REC% = 0% THEN GOTO 3370
1070 F_BR$ = ""
1080 IF ARGS$ <> "" THEN U_IN$ = ARGS$
1085 IF ARGS$ <> "" THEN GOSUB 580
1090 IF ARGS$ <> "" THEN F_BR$ = U_OUT$
1100 PRINT EQU$ \ PRINT "  Cognos QUIZ V5.0 Report Writer: ACCESS ORDERS \ SORT ON BRANCH-CODE \ REPORT ALL" \ PRINT SEP$
1110 PRINT "  ORDER-NO   CUST-NAME             BRANCH-CODE   ORDER-AMT($K)" \ PRINT SEP$
1120 QI% = 1% \ Q_CNT% = 0% \ Q_SUM% = 0%
1130 IF QI% > NUM_REC% THEN GOTO 1230
1140 T_IN$ = O_BR$(QI%) \ GOSUB 500 \ B_CLEAN$ = T_OUT$
1150 IF F_BR$ = "" THEN GOTO 1180
1160 IF B_CLEAN$ = F_BR$ THEN GOTO 1180
1170 GOTO 1220
1180 Q_CNT% = Q_CNT% + 1% \ Q_SUM% = Q_SUM% + O_AMT%(QI%)
1190 ON_P$ = LEFT$(O_NO$(QI%) + BLANKS$, 8%) \ CS_P$ = LEFT$(O_CUST$(QI%) + BLANKS$, 20%) \ BR_P$ = LEFT$(B_CLEAN$ + BLANKS$, 11%)
1200 PRINT "  "; ON_P$; "   "; CS_P$; "  "; BR_P$; "   $"; O_AMT%(QI%); "K"
1220 QI% = QI% + 1% \ GOTO 1130
1230 PRINT SEP$ \ PRINT "  FINAL FOOTING — Records Read/Sorted: "; Q_CNT%; " | SUBTOTAL ORDER-AMT = $"; Q_SUM%; "K" \ PRINT EQU$ \ GOTO 495
1280 IF NUM_REC% = 0% THEN GOTO 3370
1290 TOT_A% = 0% \ TAX_A% = 0% \ BI% = 1%
1300 IF BI% > NUM_REC% THEN GOTO 1350
1310 TOT_A% = TOT_A% + O_AMT%(BI%) \ TAX_A% = TAX_A% + INT((O_AMT%(BI%) * 7%) / 100%)
1320 BI% = BI% + 1% \ GOTO 1300
1350 PRINT EQU$ \ PRINT "  Cognos QTP V5.0 High-Volume Batch Transaction Processor" \ PRINT SEP$
1360 PRINT "  RUN ORDER_POST_RUN | Records: "; NUM_REC%; " | Gross=$"; TOT_A%; "K | Tax=$"; TAX_A%; "K"
1370 PRINT "  [QTP Batch Run Completed: "; NUM_REC%; " subfile records written to GL_POST.SF]" \ PRINT EQU$ \ GOTO 495
1450 IF NUM_REC% >= 15% THEN GOTO 1610
1460 C1% = INSTR(1%, ARGS$, ",")
1470 IF C1% = 0% THEN GOTO 1600
1480 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ ON_V$ = U_OUT$
1490 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1500 IF C2% = 0% THEN GOTO 1600
1510 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ CS_V$ = T_OUT$
1520 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1530 IF C3% = 0% THEN GOTO 1600
1540 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ BR_V$ = U_OUT$
1550 AM_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1560 NUM_REC% = NUM_REC% + 1% \ O_NO$(NUM_REC%) = ON_V$ \ O_CUST$(NUM_REC%) = CS_V$ \ O_BR$(NUM_REC%) = BR_V$ \ O_AMT%(NUM_REC%) = AM_V%
1570 PRINT "[QUICK Transaction Entry: Record #"; NUM_REC%; " added ("; ON_V$; ", "; CS_V$; ", "; BR_V$; ", $"; AM_V%; "K)]" \ GOTO 495
1600 PRINT "PowerHouse: Syntax is ADD <order_no>, <customer>, <branch>, <amt_k>" \ GOTO 495
1610 PRINT "PowerHouse: RMS file ORDERS is full" \ GOTO 495
1650 IF NUM_REC% = 0% THEN GOTO 3370
1660 SV_FILE$ = DB_FILE$
1670 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1680 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1690 IF SI% > NUM_REC% THEN GOTO 1730
1700 PRINT #2%, O_NO$(SI%); "|"; O_CUST$(SI%); "|"; O_BR$(SI%); "|"; O_AMT%(SI%)
1710 SI% = SI% + 1% \ GOTO 1690
1730 CLOSE #2% \ PRINT "["; NUM_REC%; " PowerHouse records saved to "; SV_FILE$; "]" \ GOTO 495
1800 LD_FILE$ = DB_FILE$
1810 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1820 ON ERROR GOTO 1950 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1830 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1840 IF T_OUT$ = "" THEN GOTO 1830
1850 P1% = INSTR(1%, T_OUT$, "|")
1860 IF P1% = 0% THEN GOTO 1830
1870 FON$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1880 IF P2% = 0% THEN GOTO 1830
1890 FCS$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1900 IF P3% = 0% THEN GOTO 1830
1910 FBR$ = LEFT$(REM2$, P3% - 1%) \ FAM% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1920 NUM_REC% = NUM_REC% + 1% \ O_NO$(NUM_REC%) = FON$ \ O_CUST$(NUM_REC%) = FCS$ \ O_BR$(NUM_REC%) = FBR$ \ O_AMT%(NUM_REC%) = FAM% \ GOTO 1830
1950 CLOSE #2% \ RESUME 1960
1960 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " PowerHouse records loaded from "; LD_FILE$; "]" \ GOTO 495
2050 PRINT "Cognos PowerHouse V5.0 Status: PHD="; PHD_NM$; " | Screen="; QK_SCR$; " | File="; DB_FILE$; " (Records: "; NUM_REC%; ")" \ GOTO 495
2150 NUM_REC% = 0% \ PRINT "[PowerHouse ORDERS buffer cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Cognos PowerHouse 4GL V5.0 (PDL / QUICK / QUIZ / QTP) Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / PDL / QUICK [scr] / QUIZ [branch] / QTP"
3020 PRINT "  ADD <ord>, <cust>, <br>, <amt> / SAVE [f] / LOAD [f] / SHOW / CLEAR / EXIT" \ PRINT EQU$ \ GOTO 495
3370 PRINT "*E* PowerHouse: ORDERS file is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
