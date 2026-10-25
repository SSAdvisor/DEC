10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM I_PART$(15%) \ DIM I_DESC$(15%) \ DIM I_WC$(15%) \ DIM I_OH%(15%) \ DIM I_GROSS%(15%) \ DIM I_COST%(15%)
20 NUM_ITM% = 0% \ DB_FILE$ = "MANMAN.DAT" \ PLANT_ID$ = "PLT01-MAYNARD" \ BLANKS$ = "                                        "
30 SEP$ = "--------------------------------------------------------------------------------"
40 EQU$ = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    ASK MANMAN V7.0 - Manufacturing Management MRP II Suite" \ PRINT "    ASK Computer Systems, Inc. (Mountain View, CA) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
100 PRINT "MANMAN> "; \ LINE INPUT RAW_INPUT$
110 IF LEN(RAW_INPUT$) = 0% THEN GOTO 3400
120 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 26% OR ASCII(LEFT$(RAW_INPUT$, 1%)) = 0% THEN GOTO 3400
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
350 IF VERB$ = "OMAR" OR VERB$ = "LIST" OR VERB$ = "BOM" THEN GOTO 820
360 IF VERB$ = "MRP" OR VERB$ = "NET" THEN GOTO 960
370 IF VERB$ = "CRP" OR VERB$ = "ROUTING" THEN GOTO 1120
380 IF VERB$ = "OMAC" OR VERB$ = "ORDER" THEN GOTO 1250
390 IF VERB$ = "GL" OR VERB$ = "COST" THEN GOTO 1320
400 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
410 IF VERB$ = "SAVE" THEN GOTO 1550
420 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "MANMAN: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_ITM% = 4%
710 I_PART$(1%) = "VAX-CPU1" \ I_DESC$(1%) = "KA650 CPU Module  " \ I_WC$(1%) = "WC-SMT" \ I_OH%(1%) = 40% \ I_GROSS%(1%) = 100% \ I_COST%(1%) = 450%
720 I_PART$(2%) = "VAX-MEM8" \ I_DESC$(2%) = "MS650 8MB ECC RAM " \ I_WC$(2%) = "WC-SMT" \ I_OH%(2%) = 120% \ I_GROSS%(2%) = 90% \ I_COST%(2%) = 220%
730 I_PART$(3%) = "VAX-PSU2" \ I_DESC$(3%) = "H7868 Power Supply" \ I_WC$(3%) = "WC-ASM" \ I_OH%(3%) = 25% \ I_GROSS%(3%) = 75% \ I_COST%(3%) = 180%
740 I_PART$(4%) = "VAX-CAB4" \ I_DESC$(4%) = "BA213 Q-Bus Enclos" \ I_WC$(4%) = "WC-FAB" \ I_OH%(4%) = 15% \ I_GROSS%(4%) = 65% \ I_COST%(4%) = 310%
750 PRINT "[Sample ASK MANMAN V7.0 MRP II dataset loaded - 4 Item Master & BOM records]" \ GOTO 495
820 IF NUM_ITM% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  ASK MANMAN/OMAR Item Master & Multi-Level BOM — Plant: "; PLANT_ID$ \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_ITM% THEN GOTO 920
870 P_P$ = LEFT$(I_PART$(LI%) + BLANKS$, 10%) \ D_P$ = LEFT$(I_DESC$(LI%) + BLANKS$, 19%)
880 PRINT "  "; LI%; "  "; P_P$; "  "; D_P$; "  "; I_WC$(LI%); "  OH="; I_OH%(LI%); "  Gross="; I_GROSS%(LI%); "  $"; I_COST%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_ITM% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  ASK MANMAN/OMAR Time-Phased Gross-to-Net MRP Explosion" \ PRINT SEP$
980 MI% = 1% \ POR_CNT% = 0% \ POR_QTY% = 0%
990 IF MI% > NUM_ITM% THEN GOTO 1080
1000 NET_Q% = I_GROSS%(MI%) - I_OH%(MI%)
1010 IF NET_Q% < 0% THEN NET_Q% = 0%
1020 IF NET_Q% > 0% THEN POR_CNT% = POR_CNT% + 1%
1030 POR_QTY% = POR_QTY% + NET_Q%
1040 PRINT "  Part: "; I_PART$(MI%); " | Gross="; I_GROSS%(MI%); " | OnHand="; I_OH%(MI%); " | NetReq="; NET_Q%; " | POR="; NET_Q%
1050 MI% = MI% + 1% \ GOTO 990
1080 PRINT SEP$ \ PRINT "  [MANMAN MRP Complete: "; POR_CNT%; " Planned Order Releases | Total POR Qty = "; POR_QTY%; " units]" \ PRINT EQU$ \ GOTO 495
1120 IF NUM_ITM% = 0% THEN GOTO 3370
1140 CI% = 1% \ TOT_HRS% = 0%
1150 IF CI% > NUM_ITM% THEN GOTO 1210
1160 WC_HRS% = INT(I_GROSS%(CI%) * 2% / 5%) \ TOT_HRS% = TOT_HRS% + WC_HRS%
1180 PRINT "  WorkCtr: "; I_WC$(CI%); " | Part: "; I_PART$(CI%); " | StdRunHrs="; WC_HRS%; " hrs (Load: OK)"
1190 CI% = CI% + 1% \ GOTO 1150
1210 PRINT "  [MANMAN CRP Summary: Total Work Center Load = "; TOT_HRS%; " Std Hrs across "; NUM_ITM%; " routings]" \ GOTO 495
1250 IF NUM_ITM% = 0% THEN GOTO 3370
1260 OI% = 1% \ ORD_VAL% = 0%
1270 IF OI% > NUM_ITM% THEN GOTO 1300
1280 ORD_VAL% = ORD_VAL% + INT(I_GROSS%(OI%) * I_COST%(OI%) / 10%) \ OI% = OI% + 1% \ GOTO 1270
1300 PRINT "[ASK MANMAN/OMAC Customer Order Management: "; NUM_ITM%; " active lines | Backlog Invoice Total = $"; ORD_VAL%; "0]" \ GOTO 495
1320 IF NUM_ITM% = 0% THEN GOTO 3370
1330 GI% = 1% \ INV_VAL% = 0% \ STD_SUM% = 0%
1340 IF GI% > NUM_ITM% THEN GOTO 1370
1350 INV_VAL% = INV_VAL% + INT(I_OH%(GI%) * I_COST%(GI%) / 10%) \ STD_SUM% = STD_SUM% + I_COST%(GI%) \ GI% = GI% + 1% \ GOTO 1340
1370 PRINT "[ASK MANMAN/GL Standard Cost Rollup: Unit Cost Sum = $"; STD_SUM%; " | On-Hand Valuation = $"; INV_VAL%; "0]" \ GOTO 495
1380 IF NUM_ITM% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ P_V$ = T_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ D_V$ = T_OUT$ \ REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ W_V$ = T_OUT$ \ REM3$ = MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%) \ C4% = INSTR(1%, REM3$, ",")
1480 IF C4% = 0% THEN GOTO 1500
1482 OH_V% = VAL(LEFT$(REM3$, C4% - 1%)) \ REM4$ = MID$(REM3$, C4% + 1%, LEN(REM3$) - C4%) \ C5% = INSTR(1%, REM4$, ",")
1484 IF C5% = 0% THEN GOTO 1500
1486 GR_V% = VAL(LEFT$(REM4$, C5% - 1%)) \ CS_V% = VAL(MID$(REM4$, C5% + 1%, LEN(REM4$) - C5%))
1490 NUM_ITM% = NUM_ITM% + 1% \ I_PART$(NUM_ITM%) = P_V$ \ I_DESC$(NUM_ITM%) = D_V$ \ I_WC$(NUM_ITM%) = W_V$ \ I_OH%(NUM_ITM%) = OH_V% \ I_GROSS%(NUM_ITM%) = GR_V% \ I_COST%(NUM_ITM%) = CS_V%
1495 PRINT "[MANMAN Item #"; NUM_ITM%; " added: "; P_V$; " ("; D_V$; ", StdCost=$"; CS_V%; ")]" \ GOTO 495
1500 PRINT "MANMAN: Syntax is ADD <part>, <desc>, <wc>, <onhand>, <gross_req>, <std_cost>" \ GOTO 495
1510 PRINT "MANMAN: Item Master buffer full" \ GOTO 495
1550 IF NUM_ITM% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_ITM% THEN GOTO 1630
1600 PRINT #2%, I_PART$(SI%); "|"; I_DESC$(SI%); "|"; I_WC$(SI%); "|"; I_OH%(SI%); "|"; I_GROSS%(SI%); "|"; I_COST%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_ITM%; " MANMAN Item Master records saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ITM% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FP$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1790 FD$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1810 FW$ = LEFT$(REM2$, P3% - 1%) \ REM3$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ P4% = INSTR(1%, REM3$, "|")
1820 FOH% = VAL(LEFT$(REM3$, P4% - 1%)) \ REM4$ = MID$(REM3$, P4% + 1%, LEN(REM3$) - P4%) \ P5% = INSTR(1%, REM4$, "|")
1830 FGR% = VAL(LEFT$(REM4$, P5% - 1%)) \ FCS% = VAL(MID$(REM4$, P5% + 1%, LEN(REM4$) - P5%))
1840 NUM_ITM% = NUM_ITM% + 1% \ I_PART$(NUM_ITM%) = FP$ \ I_DESC$(NUM_ITM%) = FD$ \ I_WC$(NUM_ITM%) = FW$ \ I_OH%(NUM_ITM%) = FOH% \ I_GROSS%(NUM_ITM%) = FGR% \ I_COST%(NUM_ITM%) = FCS% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_ITM%; " MANMAN Item Master records loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "ASK MANMAN V7.0 MRP II Status: Plant="; PLANT_ID$; " | File="; DB_FILE$; " (Items: "; NUM_ITM%; ")" \ GOTO 495
2050 NUM_ITM% = 0% \ PRINT "[MANMAN Item Master cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    ASK MANMAN V7.0 MRP II Commands: SAMPLE, OMAR, MRP, CRP, OMAC, GL, ADD, SAVE, LOAD, SHOW, CLEAR, EXIT" \ PRINT EQU$ \ GOTO 495
3370 PRINT "MANMAN: Item Master is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
