10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_ID$(15%) \ DIM R_NAME$(15%) \ DIM R_DEPT$(15%) \ DIM R_SAL%(15%)
20 NUM_REC% = 0% \ DB_FILE$ = "AMBASE.DAT" \ SCR_NAME$ = "EMP_MAINT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    AMBASE V4.2 - Relational DBMS, AMQUERY, AMWRITER & AMGEN Suite" \ PRINT "    Amcor Computer Corp. (Louisville, KY) - DEC PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load DB, AMQUERY, AMWRITER, AMGEN, or EXIT." \ PRINT ""
100 PRINT "AMBASE> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "SCHEMA" OR VERB$ = "DICT" THEN GOTO 820
360 IF VERB$ = "AMQUERY" OR VERB$ = "QUERY" OR VERB$ = "SELECT" OR VERB$ = "LIST" THEN GOTO 920
370 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1150
380 IF VERB$ = "AMWRITER" OR VERB$ = "REPORT" OR VERB$ = "EXPORT" THEN GOTO 1320
390 IF VERB$ = "AMGEN" OR VERB$ = "SCREEN" THEN GOTO 1600
400 IF VERB$ = "SAVE" THEN GOTO 1800
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1950
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2200
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2300
480 PRINT "AMBASE: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ SCR_NAME$ = "EMP_MAINT"
710 R_ID$(1%) = "E101" \ R_NAME$(1%) = "Kenneth Olsen    " \ R_DEPT$(1%) = "EXEC" \ R_SAL%(1%) = 950%
720 R_ID$(2%) = "E102" \ R_NAME$(2%) = "Gordon Bell      " \ R_DEPT$(2%) = "ENGR" \ R_SAL%(2%) = 880%
730 R_ID$(3%) = "E103" \ R_NAME$(3%) = "Dave Cutler      " \ R_DEPT$(3%) = "ENGR" \ R_SAL%(3%) = 840%
740 R_ID$(4%) = "E104" \ R_NAME$(4%) = "desc. Finance Mgr" \ R_DEPT$(4%) = "FIN " \ R_SAL%(4%) = 620%
750 R_NAME$(4%) = "leanor Vance     " \ R_NAME$(4%) = "Eleanor Vance    "
760 PRINT "[Sample AMBASE database loaded - 4 indexed records in AMBASE.DAT]" \ GOTO 495
820 PRINT EQU$ \ PRINT "  AMBASE V4.2 Data Dictionary & B-Tree Index Schema ("; DB_FILE$; ")" \ PRINT SEP$
830 PRINT "  Relation: PERSONNEL_MASTER   Organization: ISAM / B-Tree Primary Key"
840 PRINT "  Field 1: EMP_ID     CHAR(4)    PRIMARY KEY (Unique)"
850 PRINT "  Field 2: EMP_NAME   CHAR(20)   ATTRIBUTE"
860 PRINT "  Field 3: DEPT_CODE  CHAR(6)    SECONDARY INDEX"
870 PRINT "  Field 4: ANNUAL_BUD INTEGER    NUMERIC($100s)" \ PRINT EQU$ \ GOTO 495
920 IF NUM_REC% = 0% THEN GOTO 3370
930 F_DEPT$ = ""
940 IF ARGS$ <> "" THEN U_IN$ = ARGS$
945 IF ARGS$ <> "" THEN GOSUB 580
950 IF ARGS$ <> "" THEN F_DEPT$ = U_OUT$
960 PRINT EQU$ \ PRINT "  AMQUERY V4.2 Interactive Query Results" \ PRINT SEP$
970 PRINT "  Key     Employee Name          Department   Budget($100s)" \ PRINT SEP$
980 QI% = 1% \ Q_CNT% = 0% \ Q_SUM% = 0%
990 IF QI% > NUM_REC% THEN GOTO 1090
1000 T_IN$ = R_DEPT$(QI%) \ GOSUB 500 \ D_CLEAN$ = T_OUT$
1010 IF F_DEPT$ = "" THEN GOTO 1040
1020 IF D_CLEAN$ = F_DEPT$ THEN GOTO 1040
1030 GOTO 1080
1040 Q_CNT% = Q_CNT% + 1% \ Q_SUM% = Q_SUM% + R_SAL%(QI%)
1050 ID_P$ = LEFT$(R_ID$(QI%) + BLANKS$, 6%) \ NM_P$ = LEFT$(R_NAME$(QI%) + BLANKS$, 21%) \ DP_P$ = LEFT$(D_CLEAN$ + BLANKS$, 11%)
1060 PRINT "  "; ID_P$; "  "; NM_P$; "  "; DP_P$; "  "; R_SAL%(QI%)
1080 QI% = QI% + 1% \ GOTO 990
1090 PRINT SEP$ \ PRINT "  [AMQUERY: "; Q_CNT%; " record(s) selected | Total Budget = "; Q_SUM%; "]" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_REC% >= 15% THEN GOTO 1290
1160 C1% = INSTR(1%, ARGS$, ",")
1170 IF C1% = 0% THEN GOTO 1280
1180 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ ID_V$ = U_OUT$
1190 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1200 IF C2% = 0% THEN GOTO 1280
1210 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ NM_V$ = T_OUT$
1220 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1230 IF C3% = 0% THEN GOTO 1280
1240 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ DP_V$ = U_OUT$
1250 SL_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1260 NUM_REC% = NUM_REC% + 1% \ R_ID$(NUM_REC%) = ID_V$ \ R_NAME$(NUM_REC%) = NM_V$ \ R_DEPT$(NUM_REC%) = DP_V$ \ R_SAL%(NUM_REC%) = SL_V%
1270 PRINT "[AMBASE Record #"; NUM_REC%; " inserted: Key="; ID_V$; " ("; NM_V$; ", Dept="; DP_V$; ", Budget="; SL_V%; ")]" \ GOTO 495
1280 PRINT "AMBASE: Syntax is ADD <id>, <name>, <dept>, <budget>" \ GOTO 495
1290 PRINT "AMBASE: Relation table is full" \ GOTO 495
1320 IF NUM_REC% = 0% THEN GOTO 3370
1330 TO_F% = 0% \ OUT_F$ = "AMWRPT.TXT"
1340 IF ARGS$ <> "" THEN OUT_F$ = ARGS$
1345 IF ARGS$ <> "" THEN TO_F% = 1%
1350 TOT_S% = 0% \ RI% = 1%
1360 IF RI% > NUM_REC% THEN GOTO 1390
1370 TOT_S% = TOT_S% + R_SAL%(RI%) \ RI% = RI% + 1% \ GOTO 1360
1390 AVG_S% = INT(TOT_S% / NUM_REC%)
1400 PRINT EQU$ \ PRINT "  AMWRITER V4.2 Executive Summary Report — PERSONNEL_MASTER" \ PRINT SEP$
1410 PRINT "  Records Processed: "; NUM_REC%; " | Total Budget: "; TOT_S%; " | Mean Budget: "; AVG_S% \ PRINT EQU$
1420 IF TO_F% = 0% THEN GOTO 495
1430 OPEN OUT_F$ FOR OUTPUT AS FILE #2%
1440 PRINT #2%, "AMWRITER V4.2 REPORT — PERSONNEL_MASTER"
1450 RI% = 1%
1460 IF RI% > NUM_REC% THEN GOTO 1500
1470 PRINT #2%, R_ID$(RI%); "|"; R_NAME$(RI%); "|"; R_DEPT$(RI%); "|"; R_SAL%(RI%)
1480 RI% = RI% + 1% \ GOTO 1460
1500 PRINT #2%, "TOTAL_RECORDS="; NUM_REC%; "|TOTAL_BUDGET="; TOT_S% \ CLOSE #2%
1510 PRINT "[AMWRITER report written to "; OUT_F$; "]" \ GOTO 495
1600 IF ARGS$ <> "" THEN SCR_NAME$ = ARGS$
1610 U_IN$ = SCR_NAME$ \ GOSUB 580 \ SCR_NAME$ = U_OUT$
1620 PRINT EQU$ \ PRINT "  AMGEN V4.2 VT100 Screen Application Builder — Form: "; SCR_NAME$ \ PRINT SEP$
1630 PRINT "  +--------------------------------------------------------------+"
1640 PRINT "  | AMCOR SCREEN FORM: "; LEFT$(SCR_NAME$ + BLANKS$, 16%); "  MODE: [ADD/INQ/CHG/DEL] |"
1650 PRINT "  |   EMPLOYEE ID:   [____]          DEPARTMENT: [______]        |"
1660 PRINT "  |   EMPLOYEE NAME: [____________________]                      |"
1670 PRINT "  |   ANNUAL BUDGET: [______]        <PF1>=SAVE  <PF4>=EXIT      |"
1680 PRINT "  +--------------------------------------------------------------+"
1690 PRINT "  [AMGEN compiled screen "; SCR_NAME$; ".SCR — 4 bound AMBASE fields verified]" \ PRINT EQU$ \ GOTO 495
1800 IF NUM_REC% = 0% THEN GOTO 3370
1810 SV_FILE$ = DB_FILE$
1820 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1830 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1840 IF SI% > NUM_REC% THEN GOTO 1880
1850 PRINT #2%, R_ID$(SI%); "|"; R_NAME$(SI%); "|"; R_DEPT$(SI%); "|"; R_SAL%(SI%)
1860 SI% = SI% + 1% \ GOTO 1840
1880 CLOSE #2% \ PRINT "["; NUM_REC%; " AMBASE records saved to "; SV_FILE$; "]" \ GOTO 495
1950 LD_FILE$ = DB_FILE$
1960 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1970 ON ERROR GOTO 2100 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1980 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1990 IF T_OUT$ = "" THEN GOTO 1980
2000 P1% = INSTR(1%, T_OUT$, "|")
2010 IF P1% = 0% THEN GOTO 1980
2020 FID$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
2030 IF P2% = 0% THEN GOTO 1980
2040 FNM$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2050 IF P3% = 0% THEN GOTO 1980
2060 FDP$ = LEFT$(REM2$, P3% - 1%) \ FSL% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
2070 NUM_REC% = NUM_REC% + 1% \ R_ID$(NUM_REC%) = FID$ \ R_NAME$(NUM_REC%) = FNM$ \ R_DEPT$(NUM_REC%) = FDP$ \ R_SAL%(NUM_REC%) = FSL% \ GOTO 1980
2100 CLOSE #2% \ RESUME 2110
2110 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " AMBASE records loaded from "; LD_FILE$; "]" \ GOTO 495
2200 PRINT "AMBASE V4.2 Database Status:" \ PRINT "  Database File:  "; DB_FILE$; " (Indexed Records: "; NUM_REC%; ")"
2210 PRINT "  Active Screen:  "; SCR_NAME$; ".SCR | Subsystems: AMQUERY, AMWRITER, AMGEN" \ GOTO 495
2300 NUM_REC% = 0% \ PRINT "[AMBASE database cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Amcor AMBASE V4.2 DBMS, AMQUERY, AMWRITER & AMGEN Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample indexed database (AMBASE.DAT)" \ PRINT "  SCHEMA / DICT                    Display Data Dictionary & B-Tree keys"
3020 PRINT "  AMQUERY [dept] / QUERY / LIST    Query all records or filter by department" \ PRINT "  ADD <id>, <name>, <dept>, <bud>  Insert indexed record into AMBASE"
3030 PRINT "  AMWRITER [file] / REPORT         Generate ad-hoc summary report" \ PRINT "  AMGEN [form] / SCREEN            Compile & preview VT100 data entry screen"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load AMBASE.DAT database" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear memory, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "AMBASE: Database is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
