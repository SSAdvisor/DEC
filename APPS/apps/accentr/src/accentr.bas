10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM P_NO$(15%) \ DIM P_DESC$(15%) \ DIM P_QTY%(15%) \ DIM P_PRC%(15%)
20 NUM_REC% = 0% \ DBL_NAME$ = "CORP_DBL" \ SD_NAME$ = "INV_SD" \ DS_NAME$ = "INV_DS" \ DB_FILE$ = "ACCRDB.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    ACCENT R V11.4 - Fourth-Generation Language (4GL) & Relational DBMS" \ PRINT "    National Information Systems (NIS, Cupertino, CA) - PDP-11 RSTS/E" \ PRINT EQU$
90 PRINT "Type HELP for 4GL commands, SAMPLE to load DBL, DSD, EXTRACT, PM, CM, or EXIT." \ PRINT ""
100 PRINT "ACCENT-R> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "DSD" OR VERB$ = "SCHEMA" OR VERB$ = "SD" THEN GOTO 820
360 IF VERB$ = "EXTRACT" OR VERB$ = "LIST" OR VERB$ = "DS" OR VERB$ = "SELECT" THEN GOTO 920
370 IF VERB$ = "ADD" OR VERB$ = "ENTER" OR VERB$ = "INSERT" THEN GOTO 1120
380 IF VERB$ = "PM" OR VERB$ = "PROCESS" OR VERB$ = "RUNPM" THEN GOTO 1300
390 IF VERB$ = "CM" OR VERB$ = "COMMAND" OR VERB$ = "RUNCM" THEN GOTO 1500
400 IF VERB$ = "EXPORT" OR VERB$ = "REPORT" THEN GOTO 1650
410 IF VERB$ = "SAVE" THEN GOTO 1820
420 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1950
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2200
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2300
480 PRINT "ACCENT R: Unknown 4GL command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ DBL_NAME$ = "CORP_DBL" \ SD_NAME$ = "INV_SD" \ DS_NAME$ = "INV_DS"
710 P_NO$(1%) = "DEC-70" \ P_DESC$(1%) = "PDP-11/70 CPU Cabinet" \ P_QTY%(1%) = 6%  \ P_PRC%(1%) = 450%
720 P_NO$(2%) = "RA81-A" \ P_DESC$(2%) = "RA81 456MB Disk Drive" \ P_QTY%(2%) = 14% \ P_PRC%(2%) = 120%
730 P_NO$(3%) = "DHV-11" \ P_DESC$(3%) = "DHV11 8-Line Async Mux" \ P_QTY%(3%) = 25% \ P_PRC%(3%) = 35%
740 P_NO$(4%) = "VT100A" \ P_DESC$(4%) = "VT100 Video Terminal  " \ P_QTY%(4%) = 40% \ P_PRC%(4%) = 18%
750 PRINT "[Sample ACCENT R Data Base Library ("; DBL_NAME$; ") loaded - 4 records in Data Set "; DS_NAME$; "]" \ GOTO 495
820 PRINT EQU$ \ PRINT "  ACCENT R V11.4 Schema Definition (DSD): "; SD_NAME$; " in DBL "; DBL_NAME$ \ PRINT SEP$
830 PRINT "  DEFINE SD "; SD_NAME$
840 PRINT "    PART_NO      , CHAR      , 6   , KEY"
850 PRINT "    PART_DESC    , CHAR      , 22"
860 PRINT "    QTY_ON_HAND  , INT       , 5"
870 PRINT "    UNIT_COST    , INT       , 6"
880 PRINT "  END — Data Index (DI): PART_IDX Linked to Data Set (DS): "; DS_NAME$ \ PRINT EQU$ \ GOTO 495
920 IF NUM_REC% = 0% THEN GOTO 3370
930 PRINT EQU$ \ PRINT "  ACCENT R Data Set (DS): "; DS_NAME$; " — EXTRACT Listing" \ PRINT SEP$
940 PRINT "  Part No   Description              Qty On Hand   Unit($100)   Ext Value($100)" \ PRINT SEP$
950 EI% = 1% \ TOT_EXT% = 0%
960 IF EI% > NUM_REC% THEN GOTO 1030
970 EXT_V% = P_QTY%(EI%) * P_PRC%(EI%) \ TOT_EXT% = TOT_EXT% + EXT_V%
980 PN_P$ = LEFT$(P_NO$(EI%) + BLANKS$, 8%) \ PD_P$ = LEFT$(P_DESC$(EI%) + BLANKS$, 23%)
990 PRINT "  "; PN_P$; "  "; PD_P$; "  "; P_QTY%(EI%); "            "; P_PRC%(EI%); "          "; EXT_V%
1000 EI% = EI% + 1% \ GOTO 960
1030 PRINT SEP$ \ PRINT "  [EXTRACT Complete: "; NUM_REC%; " records in "; DS_NAME$; " | Total Valuation = "; TOT_EXT%; "]" \ PRINT EQU$ \ GOTO 495
1120 IF NUM_REC% >= 15% THEN GOTO 1260
1130 C1% = INSTR(1%, ARGS$, ",")
1140 IF C1% = 0% THEN GOTO 1250
1150 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ PN_V$ = U_OUT$
1160 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1170 IF C2% = 0% THEN GOTO 1250
1180 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ PD_V$ = T_OUT$
1190 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1200 IF C3% = 0% THEN GOTO 1250
1210 QT_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ PR_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1220 NUM_REC% = NUM_REC% + 1% \ P_NO$(NUM_REC%) = PN_V$ \ P_DESC$(NUM_REC%) = PD_V$ \ P_QTY%(NUM_REC%) = QT_V% \ P_PRC%(NUM_REC%) = PR_V%
1230 PRINT "[ACCENT R Data Set "; DS_NAME$; ": Record #"; NUM_REC%; " added ("; PN_V$; ", Qty="; QT_V%; ", Unit="; PR_V%; ")]" \ GOTO 495
1250 PRINT "ACCENT R: Syntax is ADD <part_no>, <description>, <qty>, <unit_cost>" \ GOTO 495
1260 PRINT "ACCENT R: Data Set is full" \ GOTO 495
1300 IF NUM_REC% = 0% THEN GOTO 3370
1310 PM_NAME$ = "VALUATE_PM"
1320 IF ARGS$ <> "" THEN PM_NAME$ = ARGS$
1330 U_IN$ = PM_NAME$ \ GOSUB 580 \ PM_NAME$ = U_OUT$
1340 TOT_VAL% = 0% \ LOW_STK% = 0% \ PI% = 1%
1350 IF PI% > NUM_REC% THEN GOTO 1400
1360 TOT_VAL% = TOT_VAL% + (P_QTY%(PI%) * P_PRC%(PI%))
1370 IF P_QTY%(PI%) < 10% THEN LOW_STK% = LOW_STK% + 1%
1380 PI% = PI% + 1% \ GOTO 1350
1400 PRINT EQU$ \ PRINT "  ACCENT R Process Module (PM): "; PM_NAME$; " Execution" \ PRINT SEP$
1410 PRINT "  RELATE DS "; DS_NAME$; " VIA DI PART_IDX"
1420 PRINT "  Records Processed: "; NUM_REC%; " | Reorder Alerts (<10 Qty): "; LOW_STK%
1430 PRINT "  Computed Portfolio Valuation: $"; TOT_VAL%; "00"
1440 PRINT "  [PM "; PM_NAME$; " completed with 0 runtime errors]" \ PRINT EQU$ \ GOTO 495
1500 CM_NAME$ = "NIGHTLY_CM"
1510 IF ARGS$ <> "" THEN CM_NAME$ = ARGS$
1520 U_IN$ = CM_NAME$ \ GOSUB 580 \ CM_NAME$ = U_OUT$
1530 PRINT "[ACCENT R Command Module (CM) "; CM_NAME$; ": Verified DBL "; DBL_NAME$; ", SD "; SD_NAME$; ", and DS "; DS_NAME$; " ("; NUM_REC%; " records)]" \ GOTO 495
1650 IF NUM_REC% = 0% THEN GOTO 3370
1660 OUT_F$ = "ACCRRPT.TXT"
1670 IF ARGS$ <> "" THEN OUT_F$ = ARGS$
1680 OPEN OUT_F$ FOR OUTPUT AS FILE #2%
1690 PRINT #2%, "ACCENT R V11.4 4GL REPORT — DBL "; DBL_NAME$; " / DS "; DS_NAME$
1700 RI% = 1%
1710 IF RI% > NUM_REC% THEN GOTO 1750
1720 PRINT #2%, P_NO$(RI%); "|"; P_DESC$(RI%); "|QTY="; P_QTY%(RI%); "|COST="; P_PRC%(RI%)
1730 RI% = RI% + 1% \ GOTO 1710
1750 CLOSE #2% \ PRINT "[ACCENT R 4GL report exported to "; OUT_F$; "]" \ GOTO 495
1820 IF NUM_REC% = 0% THEN GOTO 3370
1830 SV_FILE$ = DB_FILE$
1840 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1850 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1860 IF SI% > NUM_REC% THEN GOTO 1900
1870 PRINT #2%, P_NO$(SI%); "|"; P_DESC$(SI%); "|"; P_QTY%(SI%); "|"; P_PRC%(SI%)
1880 SI% = SI% + 1% \ GOTO 1860
1900 CLOSE #2% \ PRINT "["; NUM_REC%; " ACCENT R Data Set records saved to "; SV_FILE$; "]" \ GOTO 495
1950 LD_FILE$ = DB_FILE$
1960 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1970 ON ERROR GOTO 2100 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1980 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1990 IF T_OUT$ = "" THEN GOTO 1980
2000 P1% = INSTR(1%, T_OUT$, "|")
2010 IF P1% = 0% THEN GOTO 1980
2020 FPN$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
2030 IF P2% = 0% THEN GOTO 1980
2040 FPD$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2050 IF P3% = 0% THEN GOTO 1980
2060 FQT% = VAL(LEFT$(REM2$, P3% - 1%)) \ FPR% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
2070 NUM_REC% = NUM_REC% + 1% \ P_NO$(NUM_REC%) = FPN$ \ P_DESC$(NUM_REC%) = FPD$ \ P_QTY%(NUM_REC%) = FQT% \ P_PRC%(NUM_REC%) = FPR% \ GOTO 1980
2100 CLOSE #2% \ RESUME 2110
2110 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " ACCENT R Data Set records loaded from "; LD_FILE$; "]" \ GOTO 495
2200 PRINT "ACCENT R V11.4 4GL Environment Status:" \ PRINT "  Active DBL:     "; DBL_NAME$; " (File: "; DB_FILE$; ")"
2210 PRINT "  Schema (SD):    "; SD_NAME$; " | Data Set (DS): "; DS_NAME$; " ("; NUM_REC%; " records)" \ GOTO 495
2300 NUM_REC% = 0% \ PRINT "[ACCENT R Data Set cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    NIS ACCENT R V11.4 4GL & Relational DBMS Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample DBL, Schema (SD), and Data Set (DS)" \ PRINT "  DSD / SCHEMA / SD                Display Schema Definition (DSD) and Data Index (DI)"
3020 PRINT "  EXTRACT / LIST / DS              Extract and display records from Data Set" \ PRINT "  ADD <part>, <desc>, <qty>, <prc> Enter new record into Data Set"
3030 PRINT "  PM [name] / PROCESS              Execute 4GL Process Module (PM) valuation" \ PRINT "  CM [name] / COMMAND              Execute 4GL Command Module (CM) verification"
3040 PRINT "  EXPORT [file] / SAVE / LOAD      Export report or save/load ACCRDB.DAT" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear Data Set, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "ACCENT R: Data Set is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
