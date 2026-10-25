10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM D_DIV$(15%) \ DIM D_VAR$(15%) \ DIM D_PER$(15%) \ DIM D_ACT%(15%)
20 NUM_SLICE% = 0% \ VIEW_ORIENT$ = "DIV-BY-VAR" \ DB_FILE$ = "SYSWCUBE.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Comshare System W & Commander EIS V4.2 - Multidimensional OLAP DSS" \ PRINT "    Comshare, Inc. (Ann Arbor, MI) - DEC VAX/VMS & VAXstation" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load cube, CUBE, ROTATE, FXCONV, BRIEFING, or EXIT." \ PRINT ""
100 PRINT "SYSW> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "CUBE" OR VERB$ = "LIST" OR VERB$ = "SLICE" THEN GOTO 820
360 IF VERB$ = "ROTATE" OR VERB$ = "PIVOT" THEN GOTO 960
370 IF VERB$ = "FXCONV" OR VERB$ = "CURRENCY" THEN GOTO 1100
380 IF VERB$ = "BRIEFING" OR VERB$ = "EIS" THEN GOTO 1210
390 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
400 IF VERB$ = "SAVE" THEN GOTO 1550
410 IF VERB$ = "LOAD" OR VERB$ = "OPEN" THEN GOTO 1700
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "SYSW: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_SLICE% = 4% \ VIEW_ORIENT$ = "DIV-BY-VAR"
710 D_DIV$(1%) = "NORTH-AM" \ D_VAR$(1%) = "NET-SALES" \ D_PER$(1%) = "FY90-Q4" \ D_ACT%(1%) = 2400%
720 D_DIV$(2%) = "EUROPE  " \ D_VAR$(2%) = "NET-SALES" \ D_PER$(2%) = "FY90-Q4" \ D_ACT%(2%) = 1800%
730 D_DIV$(3%) = "PACIFIC " \ D_VAR$(3%) = "NET-SALES" \ D_PER$(3%) = "FY90-Q4" \ D_ACT%(3%) = 1200%
740 D_DIV$(4%) = "CORP-HQ " \ D_VAR$(4%) = "EBIT-RESERVE" \ D_PER$(4%) = "FY90-Q4" \ D_ACT%(4%) = 900%
750 PRINT "[Sample Comshare System W multidimensional hypercube loaded - 4 slices]" \ GOTO 495
820 IF NUM_SLICE% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Comshare System W Hypercube Slice (View: "; VIEW_ORIENT$; ") — File: "; DB_FILE$ \ PRINT SEP$
840 PRINT "  Division     Variable        Period     Actual($K)   Budget($K)" \ PRINT SEP$
850 LI% = 1% \ TOT_A% = 0%
860 IF LI% > NUM_SLICE% THEN GOTO 920
870 DV_P$ = LEFT$(D_DIV$(LI%) + BLANKS$, 11%) \ VR_P$ = LEFT$(D_VAR$(LI%) + BLANKS$, 14%) \ PR_P$ = LEFT$(D_PER$(LI%) + BLANKS$, 9%)
880 BDG_V% = INT((D_ACT%(LI%) * 95%) / 100%) \ TOT_A% = TOT_A% + D_ACT%(LI%)
890 PRINT "  "; DV_P$; "  "; VR_P$; "  "; PR_P$; "  "; D_ACT%(LI%); "         "; BDG_V%
900 LI% = LI% + 1% \ GOTO 860
920 PRINT SEP$ \ PRINT "  [Hypercube Consolidated Actual = $"; TOT_A%; "K across "; NUM_SLICE%; " slices]" \ PRINT EQU$ \ GOTO 495
960 IF NUM_SLICE% = 0% THEN GOTO 3370
970 VIEW_ORIENT$ = "TIME-BY-DIV"
980 IF ARGS$ <> "" THEN U_IN$ = ARGS$
990 IF ARGS$ <> "" THEN GOSUB 580
1000 IF ARGS$ <> "" THEN VIEW_ORIENT$ = U_OUT$
1010 PRINT EQU$ \ PRINT "  Comshare System W Dataman Cross-Dimensional Pivot — Axis: "; VIEW_ORIENT$ \ PRINT SEP$
1020 PRINT "  Pivoting Dimensions: [Time Periods] x [Divisions] x [Actual vs Budget Variance]..."
1030 PRINT "  [Hypercube ROTATE Complete: Active viewpoint switched to "; VIEW_ORIENT$; "]" \ PRINT EQU$ \ GOTO 495
1100 IF NUM_SLICE% = 0% THEN GOTO 3370
1110 SI% = 1% \ TOT_USD% = 0%
1120 IF SI% > NUM_SLICE% THEN GOTO 1150
1130 TOT_USD% = TOT_USD% + D_ACT%(SI%) \ SI% = SI% + 1% \ GOTO 1120
1150 TOT_DEM% = INT((TOT_USD% * 162%) / 100%) \ TOT_GBP% = INT((TOT_USD% * 54%) / 100%)
1160 PRINT EQU$ \ PRINT "  Comshare System W Multi-Currency FX Translation Table (Spot & Avg Rates)" \ PRINT SEP$
1170 PRINT "  Consolidated USD = $"; TOT_USD%; "K | Translated DEM = "; TOT_DEM%; "K DM | Translated GBP = "; TOT_GBP%; "K UKP"
1180 PRINT "  [FXCONV Translation Complete: USD=$"; TOT_USD%; "K, DEM="; TOT_DEM%; "K, GBP="; TOT_GBP%; "K]" \ PRINT EQU$ \ GOTO 495
1210 IF NUM_SLICE% = 0% THEN GOTO 3370
1220 SI% = 1% \ TOT_A% = 0%
1230 IF SI% > NUM_SLICE% THEN GOTO 1260
1240 TOT_A% = TOT_A% + D_ACT%(SI%) \ SI% = SI% + 1% \ GOTO 1230
1260 TOT_B% = INT((TOT_A% * 95%) / 100%) \ VAR_K% = TOT_A% - TOT_B%
1270 PRINT EQU$ \ PRINT "  Comshare Commander EIS — Executive Briefing Board (Exception Stoplights)" \ PRINT SEP$
1280 PRINT "  KPI #1 Consolidated Revenue : $"; TOT_A%; "K vs Budget $"; TOT_B%; "K (+"; VAR_K%; "K) [STATUS: GREEN]"
1290 PRINT "  KPI #2 Regional Drill-Down  : "; NUM_SLICE%; " Global Divisions ReportingOn-Time     [STATUS: GREEN]"
1300 PRINT "  [Commander EIS Briefing Complete: Favorable Variance +$"; VAR_K%; "K | All Stoplights GREEN]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_SLICE% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ DV_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ VR_V$ = U_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ PR_V$ = U_OUT$
1480 AC_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_SLICE% = NUM_SLICE% + 1% \ D_DIV$(NUM_SLICE%) = DV_V$ \ D_VAR$(NUM_SLICE%) = VR_V$ \ D_PER$(NUM_SLICE%) = PR_V$ \ D_ACT%(NUM_SLICE%) = AC_V%
1495 PRINT "[System W Slice #"; NUM_SLICE%; " added: "; DV_V$; " / "; VR_V$; " (Actual=$"; AC_V%; "K)]" \ GOTO 495
1500 PRINT "SYSW: Syntax is ADD <division>, <variable>, <period>, <actual_k>" \ GOTO 495
1510 PRINT "SYSW: Hypercube buffer full" \ GOTO 495
1550 IF NUM_SLICE% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_SLICE% THEN GOTO 1630
1600 PRINT #2%, D_DIV$(SI%); "|"; D_VAR$(SI%); "|"; D_PER$(SI%); "|"; D_ACT%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_SLICE%; " System W hypercube slices saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_SLICE% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FD$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FV$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FP$ = LEFT$(REM2$, P3% - 1%) \ FA% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_SLICE% = NUM_SLICE% + 1% \ D_DIV$(NUM_SLICE%) = FD$ \ D_VAR$(NUM_SLICE%) = FV$ \ D_PER$(NUM_SLICE%) = FP$ \ D_ACT%(NUM_SLICE%) = FA% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_SLICE%; " System W hypercube slices loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Comshare System W / Commander EIS Status:" \ PRINT "  Active Cube:    "; DB_FILE$; " (Slices: "; NUM_SLICE%; ", View: "; VIEW_ORIENT$; ")" \ GOTO 495
2050 NUM_SLICE% = 0% \ PRINT "[System W hypercube cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Comshare System W & Commander EIS Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample multidimensional OLAP cube" \ PRINT "  CUBE / LIST                      Display multidimensional hypercube slice"
3020 PRINT "  ROTATE [axis] / FXCONV           Pivot cube dimensions or run FX translation" \ PRINT "  BRIEFING / EIS                   Display Commander EIS Executive Board"
3030 PRINT "  ADD <div>, <var>, <per>, <act>   Add slice to hypercube" \ PRINT "  SAVE [file] / LOAD [file]        Save or load SYSWCUBE.DAT cube file"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear cube, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "SYSW: Hypercube is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
