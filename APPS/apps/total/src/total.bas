10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM M_KEY$(10%) \ DIM M_NAME$(10%) \ DIM M_CRED%(10%) \ DIM V_MKEY$(20%) \ DIM V_OID$(20%) \ DIM V_ITEM$(20%) \ DIM V_AMT%(20%)
20 NUM_M% = 0% \ NUM_V% = 0% \ DB_NAME$ = "PRODDB" \ DB_MODE$ = "UPDATE" \ DB_OPEN% = 1% \ DB_FILE$ = "TOTMDB.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    CINCOM TOTAL V8.0 - Network Database Management System (PDP-11 RSTS/E)" \ PRINT "    Cincom Systems, Inc. (Cincinnati, OH) - Master & Variable Data Sets" \ PRINT EQU$
90 PRINT "Type HELP for DML/DDL commands, SAMPLE to load DB, DBGEN, READM, FINDX, or EXIT." \ PRINT ""
100 PRINT "TOTAL> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "DBGEN" OR VERB$ = "DDL" OR VERB$ = "SCHEMA" THEN GOTO 820
360 IF VERB$ = "SINON" OR VERB$ = "OPEN" THEN GOTO 960
370 IF VERB$ = "READM" OR VERB$ = "MASTER" OR VERB$ = "LISTM" THEN GOTO 1020
380 IF VERB$ = "FINDX" OR VERB$ = "READV" OR VERB$ = "CHAIN" OR VERB$ = "LISTV" THEN GOTO 1250
390 IF VERB$ = "ADDM" OR VERB$ = "INSERTM" THEN GOTO 1500
400 IF VERB$ = "ADDV" OR VERB$ = "INSERTV" THEN GOTO 1680
410 IF VERB$ = "EXPORT" OR VERB$ = "REPORT" OR VERB$ = "PRINT" THEN GOTO 1900
420 IF VERB$ = "SAVE" THEN GOTO 2150
430 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 2350
440 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2750
450 IF VERB$ = "CLEAR" OR VERB$ = "RESET" OR VERB$ = "SINOF" THEN GOTO 2850
480 PRINT "TOTAL: Unknown DML/DDL verb '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_M% = 3% \ NUM_V% = 4% \ DB_NAME$ = "PRODDB" \ DB_MODE$ = "UPDATE" \ DB_OPEN% = 1%
710 M_KEY$(1%) = "C100" \ M_NAME$(1%) = "Digital Equipment Corp" \ M_CRED%(1%) = 5000%
720 M_KEY$(2%) = "C200" \ M_NAME$(2%) = "First Bank Minneapolis" \ M_CRED%(2%) = 3500%
730 M_KEY$(3%) = "C300" \ M_NAME$(3%) = "General Dynamics Corp " \ M_CRED%(3%) = 4200%
740 V_MKEY$(1%) = "C100" \ V_OID$(1%) = "ORD-101" \ V_ITEM$(1%) = "PDP-11/70 System" \ V_AMT%(1%) = 1450%
750 V_MKEY$(2%) = "C100" \ V_OID$(2%) = "ORD-102" \ V_ITEM$(2%) = "RA81 Disk Drive " \ V_AMT%(2%) = 380%
760 V_MKEY$(3%) = "C200" \ V_OID$(3%) = "ORD-201" \ V_ITEM$(3%) = "VT100 Terminals " \ V_AMT%(3%) = 620%
770 V_MKEY$(4%) = "C300" \ V_OID$(4%) = "ORD-301" \ V_ITEM$(4%) = "TU16 Magtape Sub" \ V_AMT%(4%) = 510%
780 PRINT "[Sample CINCOM TOTAL network database loaded - 3 CUSTM Master records, 4 ORDERV Chained records]" \ GOTO 495
820 IF ARGS$ <> "" THEN DB_NAME$ = ARGS$
830 PRINT EQU$ \ PRINT "  CINCOM TOTAL V8.0 DDL Compiler (DBGEN) — Schema: "; DB_NAME$ \ PRINT SEP$
840 PRINT "  BEGIN-DATA-BASE-GENERATION: "; DB_NAME$
850 PRINT "    MASTER-DATA-SET: NAME=CUSTM, ACCESS=DIRECT-HASH, KEY=CUSTKEY(4)"
860 PRINT "      ELEMENTS: CUSTNAME(24), CREDIT-LIM(6), CUSTLK(8)"
870 PRINT "    VARIABLE-ENTRY-DATA-SET: NAME=ORDERV, LINKAGE-PATH=CUSTLK->CUSTM"
880 PRINT "      ELEMENTS: ORDID(8), ITEM-DESC(18), ORD-AMT(6)"
890 PRINT "  END-DATA-BASE-GENERATION — Status: **** (0 DDL Errors, DBMOD Compiled)" \ PRINT EQU$ \ GOTO 495
960 IF ARGS$ <> "" THEN DB_MODE$ = ARGS$
970 U_IN$ = DB_MODE$ \ GOSUB 580 \ DB_MODE$ = U_OUT$ \ DB_OPEN% = 1%
980 PRINT "[TOTAL DML SINON: Signed on to Database "; DB_NAME$; " in "; DB_MODE$; " mode — Status: ****]" \ GOTO 495
1020 IF NUM_M% = 0% THEN GOTO 3370
1030 REQ_K$ = ""
1040 IF ARGS$ <> "" THEN U_IN$ = ARGS$
1045 IF ARGS$ <> "" THEN GOSUB 580
1050 IF ARGS$ <> "" THEN REQ_K$ = U_OUT$
1060 PRINT EQU$ \ PRINT "  CINCOM TOTAL Master Data Set (CUSTM) — Direct Key Lookup" \ PRINT SEP$
1070 PRINT "  Key     Customer Name             Credit($K)   Chain Count   Chain Balance($K)" \ PRINT SEP$
1080 MI% = 1% \ M_FOUND% = 0%
1090 IF MI% > NUM_M% THEN GOTO 1210
1100 IF REQ_K$ = "" THEN GOTO 1130
1110 IF M_KEY$(MI%) = REQ_K$ THEN GOTO 1130
1120 GOTO 1200
1130 M_FOUND% = M_FOUND% + 1% \ CH_CNT% = 0% \ CH_SUM% = 0% \ VI% = 1%
1140 IF VI% > NUM_V% THEN GOTO 1180
1150 IF V_MKEY$(VI%) <> M_KEY$(MI%) THEN GOTO 1170
1160 CH_CNT% = CH_CNT% + 1% \ CH_SUM% = CH_SUM% + V_AMT%(VI%)
1170 VI% = VI% + 1% \ GOTO 1140
1180 K_PAD$ = LEFT$(M_KEY$(MI%) + BLANKS$, 6%) \ N_PAD$ = LEFT$(M_NAME$(MI%) + BLANKS$, 24%)
1190 PRINT "  "; K_PAD$; "  "; N_PAD$; "  "; M_CRED%(MI%); "          "; CH_CNT%; "             "; CH_SUM%
1200 MI% = MI% + 1% \ GOTO 1090
1210 PRINT SEP$ \ PRINT "  [DML READM Status: **** ("; M_FOUND%; " Master record(s) retrieved)]" \ PRINT EQU$ \ GOTO 495
1250 IF NUM_V% = 0% THEN GOTO 3370
1260 REQ_K$ = ""
1270 IF ARGS$ <> "" THEN U_IN$ = ARGS$
1275 IF ARGS$ <> "" THEN GOSUB 580
1280 IF ARGS$ <> "" THEN REQ_K$ = U_OUT$
1290 PRINT EQU$ \ PRINT "  CINCOM TOTAL Variable Entry Data Set (ORDERV) — Linkage Path Traversal" \ PRINT SEP$
1300 PRINT "  Link#   MasterKey   Order ID     Item Description       Amount($K)" \ PRINT SEP$
1310 VI% = 1% \ V_FOUND% = 0% \ V_TOT% = 0%
1320 IF VI% > NUM_V% THEN GOTO 1420
1330 IF REQ_K$ = "" THEN GOTO 1360
1340 IF V_MKEY$(VI%) = REQ_K$ THEN GOTO 1360
1350 GOTO 1410
1360 V_FOUND% = V_FOUND% + 1% \ V_TOT% = V_TOT% + V_AMT%(VI%)
1370 MK_PAD$ = LEFT$(V_MKEY$(VI%) + BLANKS$, 10%) \ OID_PAD$ = LEFT$(V_OID$(VI%) + BLANKS$, 11%)
1380 IT_PAD$ = LEFT$(V_ITEM$(VI%) + BLANKS$, 21%)
1390 PRINT "  "; VI%; "       "; MK_PAD$; "  "; OID_PAD$; "  "; IT_PAD$; "  "; V_AMT%(VI%)
1410 VI% = VI% + 1% \ GOTO 1320
1420 PRINT SEP$ \ PRINT "  [DML FINDX/READV Status: **** ("; V_FOUND%; " chained records, Total=$"; V_TOT%; "K)]" \ PRINT EQU$ \ GOTO 495
1500 IF NUM_M% >= 10% THEN GOTO 1650
1510 C1% = INSTR(1%, ARGS$, ",")
1520 IF C1% = 0% THEN GOTO 1640
1530 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ K_VAL$ = U_OUT$
1540 REM_M$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_M$, ",")
1550 IF C2% = 0% THEN GOTO 1640
1560 T_IN$ = LEFT$(REM_M$, C2% - 1%) \ GOSUB 500 \ N_VAL$ = T_OUT$
1570 CR_VAL% = VAL(MID$(REM_M$, C2% + 1%, LEN(REM_M$) - C2%))
1580 NUM_M% = NUM_M% + 1% \ M_KEY$(NUM_M%) = K_VAL$ \ M_NAME$(NUM_M%) = N_VAL$ \ M_CRED%(NUM_M%) = CR_VAL%
1590 PRINT "[TOTAL DML ADDM: Master CUSTM record #"; NUM_M%; " added (Key="; K_VAL$; ", Name="; N_VAL$; ", Credit="; CR_VAL%; "K) — Status: ****]" \ GOTO 495
1640 PRINT "TOTAL: Syntax is ADDM <key>, <customer_name>, <credit_k>" \ GOTO 495
1650 PRINT "TOTAL: Master Data Set CUSTM is full" \ GOTO 495
1680 IF NUM_V% >= 20% THEN GOTO 1850
1690 C1% = INSTR(1%, ARGS$, ",")
1700 IF C1% = 0% THEN GOTO 1840
1710 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ MK_VAL$ = U_OUT$
1720 REM_V1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_V1$, ",")
1730 IF C2% = 0% THEN GOTO 1840
1740 T_IN$ = LEFT$(REM_V1$, C2% - 1%) \ GOSUB 500 \ OID_VAL$ = T_OUT$
1750 REM_V2$ = MID$(REM_V1$, C2% + 1%, LEN(REM_V1$) - C2%) \ C3% = INSTR(1%, REM_V2$, ",")
1760 IF C3% = 0% THEN GOTO 1840
1770 T_IN$ = LEFT$(REM_V2$, C3% - 1%) \ GOSUB 500 \ IT_VAL$ = T_OUT$
1780 AM_VAL% = VAL(MID$(REM_V2$, C3% + 1%, LEN(REM_V2$) - C3%))
1790 NUM_V% = NUM_V% + 1% \ V_MKEY$(NUM_V%) = MK_VAL$ \ V_OID$(NUM_V%) = OID_VAL$ \ V_ITEM$(NUM_V%) = IT_VAL$ \ V_AMT%(NUM_V%) = AM_VAL%
1800 PRINT "[TOTAL DML ADDV: Variable ORDERV record #"; NUM_V%; " linked to Master "; MK_VAL$; " ("; OID_VAL$; ", $"; AM_VAL%; "K) — Status: ****]" \ GOTO 495
1840 PRINT "TOTAL: Syntax is ADDV <master_key>, <order_id>, <item>, <amount_k>" \ GOTO 495
1850 PRINT "TOTAL: Variable Entry Data Set ORDERV is full" \ GOTO 495
1900 IF NUM_M% = 0% THEN GOTO 3370
1910 OUT_FILE$ = "TOTRPT.TXT"
1920 IF ARGS$ <> "" THEN OUT_FILE$ = ARGS$
1930 OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
1940 PRINT #2%, EQU$ \ PRINT #2%, "  CINCOM TOTAL V8.0 Network Database Report — "; DB_NAME$ \ PRINT #2%, SEP$
1950 MI% = 1%
1960 IF MI% > NUM_M% THEN GOTO 1995
1970 PRINT #2%, "MASTER|"; M_KEY$(MI%); "|"; M_NAME$(MI%); "|CREDIT="; M_CRED%(MI%); "K"
1980 MI% = MI% + 1% \ GOTO 1960
1995 VI% = 1%
2000 IF VI% > NUM_V% THEN GOTO 2040
2010 PRINT #2%, "VARLINK|"; V_MKEY$(VI%); "|"; V_OID$(VI%); "|"; V_ITEM$(VI%); "|AMT="; V_AMT%(VI%); "K"
2020 VI% = VI% + 1% \ GOTO 2000
2040 PRINT #2%, EQU$ \ CLOSE #2%
2050 PRINT "[CINCOM TOTAL network database report exported to "; OUT_FILE$; "]" \ GOTO 495
2150 IF NUM_M% = 0% THEN GOTO 3370
2160 SV_FILE$ = DB_FILE$
2170 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
2180 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
2190 IF SI% > NUM_M% THEN GOTO 2230
2200 PRINT #2%, "M|"; M_KEY$(SI%); "|"; M_NAME$(SI%); "|"; M_CRED%(SI%)
2210 SI% = SI% + 1% \ GOTO 2190
2230 SI% = 1%
2240 IF SI% > NUM_V% THEN GOTO 2280
2250 PRINT #2%, "V|"; V_MKEY$(SI%); "|"; V_OID$(SI%); "|"; V_ITEM$(SI%); "|"; V_AMT%(SI%)
2260 SI% = SI% + 1% \ GOTO 2240
2280 CLOSE #2% \ PRINT "[TOTAL database saved to "; SV_FILE$; " ("; NUM_M%; " Master, "; NUM_V%; " Variable records)]" \ GOTO 495
2350 LD_FILE$ = DB_FILE$
2360 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
2370 ON ERROR GOTO 2600 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_M% = 0% \ NUM_V% = 0%
2380 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
2390 IF T_OUT$ = "" THEN GOTO 2380
2400 P1% = INSTR(1%, T_OUT$, "|")
2410 IF P1% = 0% THEN GOTO 2380
2420 R_TYP$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%)
2430 IF R_TYP$ = "V" THEN GOTO 2500
2440 P2% = INSTR(1%, REM1$, "|")
2450 IF P2% = 0% THEN GOTO 2380
2460 FK$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2470 IF P3% = 0% THEN GOTO 2380
2480 FN$ = LEFT$(REM2$, P3% - 1%) \ FC% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
2490 NUM_M% = NUM_M% + 1% \ M_KEY$(NUM_M%) = FK$ \ M_NAME$(NUM_M%) = FN$ \ M_CRED%(NUM_M%) = FC% \ GOTO 2380
2500 P2% = INSTR(1%, REM1$, "|")
2510 IF P2% = 0% THEN GOTO 2380
2520 FMK$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2530 IF P3% = 0% THEN GOTO 2380
2540 FOID$ = LEFT$(REM2$, P3% - 1%) \ REM3$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ P4% = INSTR(1%, REM3$, "|")
2550 IF P4% = 0% THEN GOTO 2380
2560 FIT$ = LEFT$(REM3$, P4% - 1%) \ FAM% = VAL(MID$(REM3$, P4% + 1%, LEN(REM3$) - P4%))
2570 NUM_V% = NUM_V% + 1% \ V_MKEY$(NUM_V%) = FMK$ \ V_OID$(NUM_V%) = FOID$ \ V_ITEM$(NUM_V%) = FIT$ \ V_AMT%(NUM_V%) = FAM% \ GOTO 2380
2600 CLOSE #2% \ RESUME 2610
2610 ON ERROR GOTO 0 \ PRINT "[TOTAL database loaded from "; LD_FILE$; " ("; NUM_M%; " Master, "; NUM_V%; " Variable records)]" \ GOTO 495
2750 PRINT "CINCOM TOTAL V8.0 Nucleus Status:" \ PRINT "  Active DBMOD:   "; DB_NAME$; " (Mode: "; DB_MODE$; ", File: "; DB_FILE$; ")"
2760 PRINT "  MasterCUSTM:    "; NUM_M%; " records | VariableORDERV: "; NUM_V%; " chained records" \ GOTO 495
2850 NUM_M% = 0% \ NUM_V% = 0% \ PRINT "[TOTAL DML SINOF: Database closed and memory buffers cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    CINCOM TOTAL V8.0 Network DBMS Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample Master (CUSTM) & Variable (ORDERV) sets" \ PRINT "  DBGEN [name] / DDL               Compile & display TOTAL DDL Network Schema"
3020 PRINT "  SINON [UPDATE|READ]              Sign on to TOTAL Database Nucleus" \ PRINT "  READM [key] / MASTER             Direct key lookup on Master Data Set (CUSTM)"
3030 PRINT "  FINDX [key] / READV / CHAIN      Traverse Variable Entry Data Set chain (ORDERV)" \ PRINT "  ADDM <key>, <name>, <credit>     Add record to Master Data Set (CUSTM)"
3040 PRINT "  ADDV <mkey>, <oid>, <item>, <amt>Link record into Variable Entry Data Set (ORDERV)" \ PRINT "  EXPORT [file] / REPORT           Export network linkage report"
3050 PRINT "  SAVE [file] / LOAD [file]        Save or load TOTMDB.DAT network database" \ PRINT "  SHOW / CLEAR / SINOF / EXIT      Status, sign-off, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "TOTAL: Database sets are empty. Use SAMPLE or ADDM." \ GOTO 495
3400 END
