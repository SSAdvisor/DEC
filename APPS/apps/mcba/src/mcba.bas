10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM I_PART$(12%) \ DIM I_DESC$(12%) \ DIM I_OH%(12%) \ DIM I_ALC%(12%) \ DIM I_COST%(12%) \ DIM I_BOM%(12%)
20 NUM_ITEMS% = 0% \ COP_ORDERS% = 3% \ SFC_WO% = 100% \ DB_FILE$ = "MCBAIM.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    MCBA V7.2 - Modular Accounting, Distribution & Manufacturing (MRP) Suite" \ PRINT "    Mini-Computer Business Applications, Inc. (MCBA) - PDP-11 RSTS/E" \ PRINT EQU$
90 PRINT "Type HELP for modules, SAMPLE to load ERP, IM, BOMP, COP, MRP, GL, or EXIT." \ PRINT ""
100 PRINT "MCBA> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "IM" OR VERB$ = "INVENTORY" OR VERB$ = "LIST" THEN GOTO 820
360 IF VERB$ = "BOMP" OR VERB$ = "BOM" THEN GOTO 1020
370 IF VERB$ = "COP" OR VERB$ = "ORDER" THEN GOTO 1180
380 IF VERB$ = "MRP" OR VERB$ = "PLAN" OR VERB$ = "SFC" THEN GOTO 1320
390 IF VERB$ = "GL" OR VERB$ = "FINANCE" OR VERB$ = "LEDGER" THEN GOTO 1550
400 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1700
410 IF VERB$ = "SAVE" THEN GOTO 1880
420 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 2020
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2250
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2350
480 PRINT "MCBA: Unknown module/command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_ITEMS% = 4% \ COP_ORDERS% = 3% \ SFC_WO% = 101%
710 I_PART$(1%) = "KB11-C" \ I_DESC$(1%) = "PDP-11/70 Processor Bd" \ I_OH%(1%) = 10% \ I_ALC%(1%) = 2% \ I_COST%(1%) = 180% \ I_BOM%(1%) = 1%
720 I_PART$(2%) = "MS11-M" \ I_DESC$(2%) = "MOS Memory Array 256KB" \ I_OH%(2%) = 24% \ I_ALC%(2%) = 8% \ I_COST%(2%) = 45%  \ I_BOM%(2%) = 4%
730 I_PART$(3%) = "RH70-B" \ I_DESC$(3%) = "Massbus Disk Ctlr     " \ I_OH%(3%) = 12% \ I_ALC%(3%) = 4% \ I_COST%(3%) = 60%  \ I_BOM%(3%) = 2%
740 I_PART$(4%) = "H960-C" \ I_DESC$(4%) = "DEC 19-Inch Cabinet   " \ I_OH%(4%) = 8%  \ I_ALC%(4%) = 2% \ I_COST%(4%) = 30%  \ I_BOM%(4%) = 1%
750 PRINT "[Sample MCBA ERP & Manufacturing database loaded - 4 I/M items, BOMP assembly PDP11-SYS]" \ GOTO 495
820 IF NUM_ITEMS% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  MCBA Inventory Management (I/M) — Item Master ("; DB_FILE$; ")" \ PRINT SEP$
840 PRINT "  Part No   Description              On-Hand   Alloc   Avail   Unit($100)  Value($100)" \ PRINT SEP$
850 II% = 1% \ TOT_INV% = 0%
860 IF II% > NUM_ITEMS% THEN GOTO 950
870 AVAIL% = I_OH%(II%) - I_ALC%(II%) \ VAL_I% = I_OH%(II%) * I_COST%(II%) \ TOT_INV% = TOT_INV% + VAL_I%
880 P_PAD$ = LEFT$(I_PART$(II%) + BLANKS$, 8%) \ D_PAD$ = LEFT$(I_DESC$(II%) + BLANKS$, 23%)
890 PRINT "  "; P_PAD$; "  "; D_PAD$; "  "; I_OH%(II%); "        "; I_ALC%(II%); "       "; AVAIL%; "       "; I_COST%(II%); "         "; VAL_I%
900 II% = II% + 1% \ GOTO 860
950 PRINT SEP$ \ PRINT "  [MCBA I/M Summary: "; NUM_ITEMS%; " items | Total Inventory Value = $"; TOT_INV%; "00]" \ PRINT EQU$ \ GOTO 495
1020 IF NUM_ITEMS% = 0% THEN GOTO 3370
1030 PRINT EQU$ \ PRINT "  MCBA Bill of Material Processor (BOMP) — Parent Assembly: PDP11-SYS" \ PRINT SEP$
1040 PRINT "  Seq  Component   Description              Qty/Assy   Unit($100)   Assy Cost($100)" \ PRINT SEP$
1050 BI% = 1% \ STD_COST% = 0%
1060 IF BI% > NUM_ITEMS% THEN GOTO 1130
1070 EXT_C% = I_BOM%(BI%) * I_COST%(BI%) \ STD_COST% = STD_COST% + EXT_C%
1080 P_PAD$ = LEFT$(I_PART$(BI%) + BLANKS$, 10%) \ D_PAD$ = LEFT$(I_DESC$(BI%) + BLANKS$, 23%)
1090 PRINT "  "; BI%; "    "; P_PAD$; "  "; D_PAD$; "  "; I_BOM%(BI%); "          "; I_COST%(BI%); "           "; EXT_C%
1100 BI% = BI% + 1% \ GOTO 1060
1130 PRINT SEP$ \ PRINT "  [BOMP Standard Assembly Cost for 1x PDP11-SYS = $"; STD_COST%; "00]" \ PRINT EQU$ \ GOTO 495
1180 IF NUM_ITEMS% = 0% THEN GOTO 3370
1190 ORD_QTY% = 2%
1200 IF ARGS$ <> "" THEN ORD_QTY% = VAL(ARGS$)
1210 IF ORD_QTY% < 1% THEN ORD_QTY% = 1%
1220 CI% = 1%
1230 IF CI% > NUM_ITEMS% THEN GOTO 1270
1240 I_ALC%(CI%) = I_ALC%(CI%) + (ORD_QTY% * I_BOM%(CI%))
1250 CI% = CI% + 1% \ GOTO 1230
1270 COP_ORDERS% = COP_ORDERS% + 1%
1280 PRINT "[MCBA Customer Order Processing (COP): Booked Order #"; COP_ORDERS%; " for "; ORD_QTY%; "x PDP11-SYS — Component allocations updated]" \ GOTO 495
1320 IF NUM_ITEMS% = 0% THEN GOTO 3370
1330 MASTER_DEM% = 10%
1340 IF ARGS$ <> "" THEN MASTER_DEM% = VAL(ARGS$)
1350 IF MASTER_DEM% < 1% THEN MASTER_DEM% = 10%
1360 PRINT EQU$ \ PRINT "  MCBA Material Requirements Planning (MRP) & Shop Floor Control (SFC)" \ PRINT "  Master Production Schedule (MPS): "; MASTER_DEM%; " units of PDP11-SYS" \ PRINT SEP$
1370 PRINT "  Part No   Gross Req   Avail(OH-Alc)   Net Req   Planned Work Order" \ PRINT SEP$
1380 MI% = 1% \ WO_CNT% = 0%
1390 IF MI% > NUM_ITEMS% THEN GOTO 1510
1400 GROSS_R% = MASTER_DEM% * I_BOM%(MI%) \ AVAIL_R% = I_OH%(MI%) - I_ALC%(MI%)
1410 NET_R% = GROSS_R% - AVAIL_R%
1420 IF NET_R% < 0% THEN NET_R% = 0%
1430 WO_STR$ = "NONE (Sufficient)"
1440 IF NET_R% <= 0% THEN GOTO 1470
1450 SFC_WO% = SFC_WO% + 1% \ WO_CNT% = WO_CNT% + 1% \ WO_STR$ = "WO-" + STR$(SFC_WO%) + " (Release)"
1470 P_PAD$ = LEFT$(I_PART$(MI%) + BLANKS$, 8%)
1480 PRINT "  "; P_PAD$; "  "; GROSS_R%; "          "; AVAIL_R%; "               "; NET_R%; "         "; WO_STR$
1490 MI% = MI% + 1% \ GOTO 1390
1510 PRINT SEP$ \ PRINT "  [MCBA MRP Explosion Complete: "; WO_CNT%; " Shop Floor Control (SFC) Work Orders released]" \ PRINT EQU$ \ GOTO 495
1550 IF NUM_ITEMS% = 0% THEN GOTO 3370
1560 TOT_INV% = 0% \ GI% = 1%
1570 IF GI% > NUM_ITEMS% THEN GOTO 1600
1580 TOT_INV% = TOT_INV% + (I_OH%(GI%) * I_COST%(GI%)) \ GI% = GI% + 1% \ GOTO 1570
1600 AR_BAL% = COP_ORDERS% * 950% \ AP_BAL% = 1420%
1610 PRINT EQU$ \ PRINT "  MCBA Financial Integration — G/L, A/R, A/P & Payroll Summary" \ PRINT SEP$
1620 PRINT "  Acct 1200 - Accounts Receivable (COP):  $"; AR_BAL%; "00 ("; COP_ORDERS%; " Active Orders)"
1630 PRINT "  Acct 1400 - Inventory Asset (I/M):      $"; TOT_INV%; "00"
1640 PRINT "  Acct 2100 - Accounts Payable (P/O):     $"; AP_BAL%; "00"
1650 PRINT "  Acct 5200 - Direct Shop Payroll (SFC):  $84000" \ PRINT EQU$ \ GOTO 495
1700 IF NUM_ITEMS% >= 12% THEN GOTO 1840
1710 C1% = INSTR(1%, ARGS$, ",")
1720 IF C1% = 0% THEN GOTO 1830
1730 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ P_V$ = U_OUT$
1740 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1750 IF C2% = 0% THEN GOTO 1830
1760 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ D_V$ = T_OUT$
1770 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1780 IF C3% = 0% THEN GOTO 1830
1790 OH_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ CS_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1800 NUM_ITEMS% = NUM_ITEMS% + 1% \ I_PART$(NUM_ITEMS%) = P_V$ \ I_DESC$(NUM_ITEMS%) = D_V$
1810 I_OH%(NUM_ITEMS%) = OH_V% \ I_ALC%(NUM_ITEMS%) = 0% \ I_COST%(NUM_ITEMS%) = CS_V% \ I_BOM%(NUM_ITEMS%) = 1%
1820 PRINT "[MCBA I/M Item #"; NUM_ITEMS%; " added: "; P_V$; " (On-Hand="; OH_V%; ", Cost=$"; CS_V%; "00)]" \ GOTO 495
1830 PRINT "MCBA: Syntax is ADD <part_no>, <description>, <on_hand>, <unit_cost>" \ GOTO 495
1840 PRINT "MCBA: Item master full" \ GOTO 495
1880 IF NUM_ITEMS% = 0% THEN GOTO 3370
1890 SV_FILE$ = DB_FILE$
1900 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1910 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1920 IF SI% > NUM_ITEMS% THEN GOTO 1960
1930 PRINT #2%, I_PART$(SI%); "|"; I_DESC$(SI%); "|"; I_OH%(SI%); "|"; I_ALC%(SI%); "|"; I_COST%(SI%); "|"; I_BOM%(SI%)
1940 SI% = SI% + 1% \ GOTO 1920
1960 CLOSE #2% \ PRINT "["; NUM_ITEMS%; " MCBA Item Master records saved to "; SV_FILE$; "]" \ GOTO 495
2020 LD_FILE$ = DB_FILE$
2030 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
2040 ON ERROR GOTO 2190 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_ITEMS% = 0%
2050 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
2060 IF T_OUT$ = "" THEN GOTO 2050
2070 P1% = INSTR(1%, T_OUT$, "|")
2080 IF P1% = 0% THEN GOTO 2050
2090 FP$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
2100 IF P2% = 0% THEN GOTO 2050
2110 FD$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2120 IF P3% = 0% THEN GOTO 2050
2130 FOH% = VAL(LEFT$(REM2$, P3% - 1%)) \ REM3$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ P4% = INSTR(1%, REM3$, "|")
2140 IF P4% = 0% THEN GOTO 2050
2150 FAL% = VAL(LEFT$(REM3$, P4% - 1%)) \ REM4$ = MID$(REM3$, P4% + 1%, LEN(REM3$) - P4%) \ P5% = INSTR(1%, REM4$, "|")
2160 IF P5% = 0% THEN GOTO 2050
2170 FCS% = VAL(LEFT$(REM4$, P5% - 1%)) \ FBM% = VAL(MID$(REM4$, P5% + 1%, LEN(REM4$) - P5%))
2180 NUM_ITEMS% = NUM_ITEMS% + 1% \ I_PART$(NUM_ITEMS%) = FP$ \ I_DESC$(NUM_ITEMS%) = FD$ \ I_OH%(NUM_ITEMS%) = FOH% \ I_ALC%(NUM_ITEMS%) = FAL% \ I_COST%(NUM_ITEMS%) = FCS% \ I_BOM%(NUM_ITEMS%) = FBM% \ GOTO 2050
2190 CLOSE #2% \ RESUME 2200
2200 ON ERROR GOTO 0 \ PRINT "["; NUM_ITEMS%; " MCBA Item Master records loaded from "; LD_FILE$; "]" \ GOTO 495
2250 PRINT "MCBA V7.2 ERP & Manufacturing Status:" \ PRINT "  Master File:    "; DB_FILE$; " (Items: "; NUM_ITEMS%; ", Active COP Orders: "; COP_ORDERS%; ")"
2260 PRINT "  Active Modules: COP, I/M, BOMP, MRP, SFC, G/L, A/R, A/P, PR" \ GOTO 495
2350 NUM_ITEMS% = 0% \ PRINT "[MCBA database cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    MCBA V7.2 ERP, Distribution & Manufacturing (MRP) Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample I/M, BOMP, and COP dataset" \ PRINT "  IM / INVENTORY / LIST            Display Inventory Management (I/M) status"
3020 PRINT "  BOMP / BOM                       Bill of Material Processor cost roll-up" \ PRINT "  COP [qty] / ORDER                Customer Order Processing & stock allocation"
3030 PRINT "  MRP [mps_qty] / PLAN / SFC       Run MRP net explosion & SFC work orders" \ PRINT "  GL / FINANCE / LEDGER            Display G/L, A/R, A/P, and Payroll summary"
3040 PRINT "  ADD <part>, <desc>, <oh>, <cost> Add part to Inventory Master" \ PRINT "  SAVE [file] / LOAD [file]        Save or load MCBAIM.DAT master file"
3050 PRINT "  SHOW / CLEAR / EXIT              Show status, clear database, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "MCBA: Inventory master is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
