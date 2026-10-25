10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM C_ID$(15%) \ DIM C_COMP$(15%) \ DIM C_REG$(15%) \ DIM C_REV%(15%)
20 NUM_REC% = 0% \ DB_FILE$ = "SBASE.DAT" \ TBL_NAME$ = "CUST_REVENUE"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Saturn-Base V3.2 - Interactive Relational Data Manager & Report System" \ PRINT "    Saturn Systems, Inc. (Minneapolis, MN) - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load DB, QUERY, EXPORTCALC, EXPORTWP, or EXIT." \ PRINT ""
100 PRINT "SATURN-BASE> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "SCHEMA" OR VERB$ = "TABLES" THEN GOTO 820
360 IF VERB$ = "QUERY" OR VERB$ = "SELECT" OR VERB$ = "LIST" THEN GOTO 920
370 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1150
380 IF VERB$ = "EXPORTCALC" OR VERB$ = "CALCLINK" THEN GOTO 1320
390 IF VERB$ = "EXPORTWP" OR VERB$ = "WPLINK" OR VERB$ = "EXPORT" THEN GOTO 1500
400 IF VERB$ = "SAVE" THEN GOTO 1700
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1850
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2150
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2250
480 PRINT "Saturn-Base: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ TBL_NAME$ = "CUST_REVENUE"
710 C_ID$(1%) = "SB-10" \ C_COMP$(1%) = "First Bank Minneapolis" \ C_REG$(1%) = "NORTH" \ C_REV%(1%) = 900%
720 C_ID$(2%) = "SB-20" \ C_COMP$(2%) = "Great Northern Grain  " \ C_REG$(2%) = "NORTH" \ C_REV%(2%) = 620%
730 C_ID$(3%) = "SB-30" \ C_COMP$(3%) = "Midwest Power & Light " \ C_REG$(3%) = "CENT " \ C_REV%(3%) = 700%
740 C_ID$(4%) = "SB-40" \ C_COMP$(4%) = "Pacific Timber Corp   " \ C_REG$(4%) = "WEST " \ C_REV%(4%) = 600%
750 PRINT "[Sample Saturn-Base relational table ("; TBL_NAME$; ") loaded - 4 records in SBASE.DAT]" \ GOTO 495
820 PRINT EQU$ \ PRINT "  Saturn-Base V3.2 Relational Schema — Table: "; TBL_NAME$ \ PRINT SEP$
830 PRINT "  Column 1: CUST_ID     CHAR(6)    Primary Key"
840 PRINT "  Column 2: COMPANY     CHAR(24)   Customer Organization"
850 PRINT "  Column 3: REGION      CHAR(6)    Territory (NORTH / CENT / WEST)"
860 PRINT "  Column 4: ANNUAL_REV  INTEGER    Annual Contract Revenue ($K)"
870 PRINT "  Links:    Saturn-Calc (SCALC.WKS) & Saturn-WP (SATWP.MRG)" \ PRINT EQU$ \ GOTO 495
920 IF NUM_REC% = 0% THEN GOTO 3370
930 F_REG$ = ""
940 IF ARGS$ <> "" THEN U_IN$ = ARGS$
945 IF ARGS$ <> "" THEN GOSUB 580
950 IF ARGS$ <> "" THEN F_REG$ = U_OUT$
960 PRINT EQU$ \ PRINT "  Saturn-Base Relational Query — Table: "; TBL_NAME$ \ PRINT SEP$
970 PRINT "  Cust ID   Company Name             Region   Annual Revenue ($K)" \ PRINT SEP$
980 QI% = 1% \ Q_CNT% = 0% \ Q_TOT% = 0%
990 IF QI% > NUM_REC% THEN GOTO 1090
1000 T_IN$ = C_REG$(QI%) \ GOSUB 500 \ R_CLN$ = T_OUT$
1010 IF F_REG$ = "" THEN GOTO 1040
1020 IF R_CLN$ = F_REG$ THEN GOTO 1040
1030 GOTO 1080
1040 Q_CNT% = Q_CNT% + 1% \ Q_TOT% = Q_TOT% + C_REV%(QI%)
1050 ID_P$ = LEFT$(C_ID$(QI%) + BLANKS$, 8%) \ CM_P$ = LEFT$(C_COMP$(QI%) + BLANKS$, 23%) \ RG_P$ = LEFT$(R_CLN$ + BLANKS$, 7%)
1060 PRINT "  "; ID_P$; "  "; CM_P$; "  "; RG_P$; "  "; C_REV%(QI%)
1080 QI% = QI% + 1% \ GOTO 990
1090 PRINT SEP$ \ PRINT "  [Saturn-Base Query: "; Q_CNT%; " record(s) matched | Total Revenue = $"; Q_TOT%; "K]" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_REC% >= 15% THEN GOTO 1290
1160 C1% = INSTR(1%, ARGS$, ",")
1170 IF C1% = 0% THEN GOTO 1280
1180 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ ID_V$ = U_OUT$
1190 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1200 IF C2% = 0% THEN GOTO 1280
1210 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ CM_V$ = T_OUT$
1220 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1230 IF C3% = 0% THEN GOTO 1280
1240 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ RG_V$ = U_OUT$
1250 RV_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1260 NUM_REC% = NUM_REC% + 1% \ C_ID$(NUM_REC%) = ID_V$ \ C_COMP$(NUM_REC%) = CM_V$ \ C_REG$(NUM_REC%) = RG_V$ \ C_REV%(NUM_REC%) = RV_V%
1270 PRINT "[Saturn-Base Record #"; NUM_REC%; " added: "; ID_V$; " ("; CM_V$; ", Region="; RG_V$; ", Rev=$"; RV_V%; "K)]" \ GOTO 495
1280 PRINT "Saturn-Base: Syntax is ADD <cust_id>, <company>, <region>, <rev_k>" \ GOTO 495
1290 PRINT "Saturn-Base: Table is full" \ GOTO 495
1320 IF NUM_REC% = 0% THEN GOTO 3370
1330 OUT_C$ = "SCALC.WKS"
1340 IF ARGS$ <> "" THEN OUT_C$ = ARGS$
1350 OPEN OUT_C$ FOR OUTPUT AS FILE #2% \ TOT_R% = 0% \ CI% = 1%
1360 IF CI% > NUM_REC% THEN GOTO 1400
1370 TOT_R% = TOT_R% + C_REV%(CI%)
1380 PRINT #2%, C_COMP$(CI%); "|"; C_REG$(CI%); "|"; C_REV%(CI%)
1390 CI% = CI% + 1% \ GOTO 1360
1400 CLOSE #2% \ PRINT "[Saturn-Base exported "; NUM_REC%; " records to Saturn-Calc worksheet "; OUT_C$; " (Total=$"; TOT_R%; "K)]" \ GOTO 495
1500 IF NUM_REC% = 0% THEN GOTO 3370
1510 OUT_W$ = "SATWP.MRG"
1520 IF ARGS$ <> "" THEN OUT_W$ = ARGS$
1530 OPEN OUT_W$ FOR OUTPUT AS FILE #2% \ WI% = 1%
1540 IF WI% > NUM_REC% THEN GOTO 1580
1550 PRINT #2%, "<ID>="; C_ID$(WI%); "|<COMPANY>="; C_COMP$(WI%); "|<REGION>="; C_REG$(WI%); "|<REV>="; C_REV%(WI%)
1560 WI% = WI% + 1% \ GOTO 1540
1580 CLOSE #2% \ PRINT "[Saturn-Base exported "; NUM_REC%; " mail-merge records to Saturn-WP file "; OUT_W$; "]" \ GOTO 495
1700 IF NUM_REC% = 0% THEN GOTO 3370
1710 SV_FILE$ = DB_FILE$
1720 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1730 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1740 IF SI% > NUM_REC% THEN GOTO 1780
1750 PRINT #2%, C_ID$(SI%); "|"; C_COMP$(SI%); "|"; C_REG$(SI%); "|"; C_REV%(SI%)
1760 SI% = SI% + 1% \ GOTO 1740
1780 CLOSE #2% \ PRINT "["; NUM_REC%; " Saturn-Base records saved to "; SV_FILE$; "]" \ GOTO 495
1850 LD_FILE$ = DB_FILE$
1860 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1870 ON ERROR GOTO 2000 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1880 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1890 IF T_OUT$ = "" THEN GOTO 1880
1900 P1% = INSTR(1%, T_OUT$, "|")
1910 IF P1% = 0% THEN GOTO 1880
1920 FID$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1930 IF P2% = 0% THEN GOTO 1880
1940 FCM$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1950 IF P3% = 0% THEN GOTO 1880
1960 FRG$ = LEFT$(REM2$, P3% - 1%) \ FRV% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1970 NUM_REC% = NUM_REC% + 1% \ C_ID$(NUM_REC%) = FID$ \ C_COMP$(NUM_REC%) = FCM$ \ C_REG$(NUM_REC%) = FRG$ \ C_REV%(NUM_REC%) = FRV% \ GOTO 1880
2000 CLOSE #2% \ RESUME 2010
2010 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " Saturn-Base records loaded from "; LD_FILE$; "]" \ GOTO 495
2150 PRINT "Saturn-Base V3.2 Status:" \ PRINT "  Active Table:   "; TBL_NAME$; " (File: "; DB_FILE$; ", Records: "; NUM_REC%; ")"
2160 PRINT "  Suite Links:    Saturn-Calc (EXPORTCALC) & Saturn-WP (EXPORTWP)" \ GOTO 495
2250 NUM_REC% = 0% \ PRINT "[Saturn-Base table cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Saturn-Base V3.2 Relational Data Manager Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample customer relational table" \ PRINT "  SCHEMA / TABLES                  Display table schema and Saturn suite links"
3020 PRINT "  QUERY [region] / SELECT / LIST   Query all records or filter by region" \ PRINT "  ADD <id>, <comp>, <reg>, <rev>   Insert new customer record"
3030 PRINT "  EXPORTCALC [file] / CALCLINK     Export table to Saturn-Calc (SCALC.WKS)" \ PRINT "  EXPORTWP [file] / WPLINK         Export mail-merge records to Saturn-WP"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load SBASE.DAT database" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear table, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "Saturn-Base: Table is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
