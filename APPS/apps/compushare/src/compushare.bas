10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM P_ID$(12%) \ DIM P_NAME$(12%) \ DIM P_WI%(12%) \ DIM P_NRI%(12%)
20 NUM_P% = 0% \ WELL_NAME$ = "PERMIAN-UNIT-14" \ DB_FILE$ = "CASJIB.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Compu-Share CAS V6.1 - RMS-11 Accounting & Oil/Gas JIB/Revenue Suite" \ PRINT "    Compu-Share, Inc. (Lubbock, TX) - DEC PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load lease, PARTNERS, JIB, REVDIST, or EXIT." \ PRINT ""
100 PRINT "CAS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "PARTNERS" OR VERB$ = "LIST" OR VERB$ = "OWNERS" THEN GOTO 820
360 IF VERB$ = "JIB" OR VERB$ = "BILLING" THEN GOTO 980
370 IF VERB$ = "REVDIST" OR VERB$ = "REVENUE" THEN GOTO 1150
380 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1320
390 IF VERB$ = "SAVE" THEN GOTO 1500
400 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1650
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1900
420 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2000
480 PRINT "CAS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_P% = 4% \ WELL_NAME$ = "PERMIAN-UNIT-14"
710 P_ID$(1%) = "OP-10" \ P_NAME$(1%) = "West Texas Operating  " \ P_WI%(1%) = 50% \ P_NRI%(1%) = 40%
720 P_ID$(2%) = "WI-20" \ P_NAME$(2%) = "High Plains Energy LP " \ P_WI%(2%) = 30% \ P_NRI%(2%) = 24%
730 P_ID$(3%) = "WI-30" \ P_NAME$(3%) = "Panhandle Drilling Co " \ P_WI%(3%) = 20% \ P_NRI%(3%) = 16%
740 P_ID$(4%) = "RY-99" \ P_NAME$(4%) = "Landowner Royalty Trst" \ P_WI%(4%) = 0%  \ P_NRI%(4%) = 20%
750 PRINT "[Sample Compu-Share CAS Division of Interest loaded - 4 owners on "; WELL_NAME$; "]" \ GOTO 495
820 IF NUM_P% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Compu-Share CAS — Division of Interest (Well: "; WELL_NAME$; ")" \ PRINT SEP$
840 PRINT "  Owner ID   Partner / Royalty Name    Working Int(WI%)   Net Rev Int(NRI%)" \ PRINT SEP$
850 PI% = 1% \ TOT_WI% = 0% \ TOT_NRI% = 0%
860 IF PI% > NUM_P% THEN GOTO 930
870 TOT_WI% = TOT_WI% + P_WI%(PI%) \ TOT_NRI% = TOT_NRI% + P_NRI%(PI%)
880 ID_P$ = LEFT$(P_ID$(PI%) + BLANKS$, 9%) \ NM_P$ = LEFT$(P_NAME$(PI%) + BLANKS$, 24%)
890 PRINT "  "; ID_P$; "  "; NM_P$; "  "; P_WI%(PI%); "%                "; P_NRI%(PI%); "%"
900 PI% = PI% + 1% \ GOTO 860
930 PRINT SEP$ \ PRINT "  [Total Working Interest = "; TOT_WI%; "% | Total Net Revenue Interest = "; TOT_NRI%; "%]" \ PRINT EQU$ \ GOTO 495
980 IF NUM_P% = 0% THEN GOTO 3370
990 AFE_COST% = 400%
1000 IF ARGS$ <> "" THEN AFE_COST% = VAL(ARGS$)
1010 PRINT EQU$ \ PRINT "  Compu-Share CAS — Joint-Interest Billing (JIB) Run (Well Cost: $"; AFE_COST%; "K)" \ PRINT SEP$
1020 PI% = 1% \ TOT_BILL% = 0%
1030 IF PI% > NUM_P% THEN GOTO 1090
1040 SHARE_C% = INT((AFE_COST% * P_WI%(PI%)) / 100%) \ TOT_BILL% = TOT_BILL% + SHARE_C%
1050 NM_P$ = LEFT$(P_NAME$(PI%) + BLANKS$, 24%)
1060 PRINT "  "; P_ID$(PI%); "  "; NM_P$; " (WI="; P_WI%(PI%); "%) -> JIB Invoice: $"; SHARE_C%; "K"
1070 PI% = PI% + 1% \ GOTO 1030
1090 PRINT SEP$ \ PRINT "  [CAS JIB Complete: Total Billed to Working Interest Partners = $"; TOT_BILL%; "K]" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_P% = 0% THEN GOTO 3370
1160 GROSS_R% = 1000%
1170 IF ARGS$ <> "" THEN GROSS_R% = VAL(ARGS$)
1180 PRINT EQU$ \ PRINT "  Compu-Share CAS — Oil & Gas Revenue Distribution (Gross: $"; GROSS_R%; "K)" \ PRINT SEP$
1190 PI% = 1% \ TOT_DIST% = 0%
1200 IF PI% > NUM_P% THEN GOTO 1260
1210 SHARE_R% = INT((GROSS_R% * P_NRI%(PI%)) / 100%) \ TOT_DIST% = TOT_DIST% + SHARE_R%
1220 NM_P$ = LEFT$(P_NAME$(PI%) + BLANKS$, 24%)
1230 PRINT "  "; P_ID$(PI%); "  "; NM_P$; " (NRI="; P_NRI%(PI%); "%) -> Net Check: $"; SHARE_R%; "K"
1240 PI% = PI% + 1% \ GOTO 1200
1260 PRINT SEP$ \ PRINT "  [CAS Revenue Run Complete: Total Disbursed = $"; TOT_DIST%; "K]" \ PRINT EQU$ \ GOTO 495
1320 IF NUM_P% >= 12% THEN GOTO 1460
1330 C1% = INSTR(1%, ARGS$, ",")
1340 IF C1% = 0% THEN GOTO 1450
1350 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ ID_V$ = U_OUT$
1360 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1370 IF C2% = 0% THEN GOTO 1450
1380 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ NM_V$ = T_OUT$
1390 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1400 IF C3% = 0% THEN GOTO 1450
1410 WI_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ NR_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1420 NUM_P% = NUM_P% + 1% \ P_ID$(NUM_P%) = ID_V$ \ P_NAME$(NUM_P%) = NM_V$ \ P_WI%(NUM_P%) = WI_V% \ P_NRI%(NUM_P%) = NR_V%
1430 PRINT "[CAS Owner #"; NUM_P%; " added: "; ID_V$; " ("; NM_V$; ", WI="; WI_V%; "%, NRI="; NR_V%; "%)]" \ GOTO 495
1450 PRINT "CAS: Syntax is ADD <id>, <name>, <wi_pct>, <nri_pct>" \ GOTO 495
1460 PRINT "CAS: Owner table full" \ GOTO 495
1500 IF NUM_P% = 0% THEN GOTO 3370
1510 SV_FILE$ = DB_FILE$
1520 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1530 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1540 IF SI% > NUM_P% THEN GOTO 1580
1550 PRINT #2%, P_ID$(SI%); "|"; P_NAME$(SI%); "|"; P_WI%(SI%); "|"; P_NRI%(SI%)
1560 SI% = SI% + 1% \ GOTO 1540
1580 CLOSE #2% \ PRINT "["; NUM_P%; " CAS Division of Interest records saved to "; SV_FILE$; "]" \ GOTO 495
1650 LD_FILE$ = DB_FILE$
1660 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1670 ON ERROR GOTO 1800 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_P% = 0%
1680 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1690 IF T_OUT$ = "" THEN GOTO 1680
1700 P1% = INSTR(1%, T_OUT$, "|")
1710 IF P1% = 0% THEN GOTO 1680
1720 FID$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1730 IF P2% = 0% THEN GOTO 1680
1740 FNM$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1750 IF P3% = 0% THEN GOTO 1680
1760 FWI% = VAL(LEFT$(REM2$, P3% - 1%)) \ FNR% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1770 NUM_P% = NUM_P% + 1% \ P_ID$(NUM_P%) = FID$ \ P_NAME$(NUM_P%) = FNM$ \ P_WI%(NUM_P%) = FWI% \ P_NRI%(NUM_P%) = FNR% \ GOTO 1680
1800 CLOSE #2% \ RESUME 1810
1810 ON ERROR GOTO 0 \ PRINT "["; NUM_P%; " CAS Division of Interest records loaded from "; LD_FILE$; "]" \ GOTO 495
1900 PRINT "Compu-Share CAS V6.1 Status:" \ PRINT "  Active Lease:   "; WELL_NAME$; " (File: "; DB_FILE$; ", Owners: "; NUM_P%; ")"
1910 PRINT "  Active Modules: CAS/GL, CAS/AP, CAS/AR, CAS/JIB, CAS/REVDIST" \ GOTO 495
2000 NUM_P% = 0% \ PRINT "[CAS Division of Interest cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Compu-Share CAS V6.1 Accounting & Oil/Gas JIB Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample Lease Division of Interest" \ PRINT "  PARTNERS / LIST                  Display Working Interest & Net Revenue owners"
3020 PRINT "  JIB [cost_k] / BILLING           Run Joint-Interest Billing (WI% allocation)" \ PRINT "  REVDIST [gross_k] / REVENUE      Run Oil & Gas Revenue Distribution (NRI%)"
3030 PRINT "  ADD <id>, <name>, <wi>, <nri>    Add partner or royalty interest owner" \ PRINT "  SAVE [file] / LOAD [file]        Save or load CASJIB.DAT file"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear records, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "CAS: No owners loaded. Use SAMPLE or ADD." \ GOTO 495
3400 END
