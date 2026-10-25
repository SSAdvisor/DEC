10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM L_ACC$(15%) \ DIM L_PAT$(15%) \ DIM L_TEST$(15%) \ DIM L_VAL%(15%) \ DIM L_LOW%(15%) \ DIM L_HIGH%(15%) \ DIM L_STAT$(15%)
20 NUM_LAB% = 0% \ DB_FILE$ = "PATHNET.DAT" \ HOSP_ID$ = "MGH-VAXCLUSTER" \ BLANKS$ = "                                        "
30 SEP$ = "--------------------------------------------------------------------------------"
40 EQU$ = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Cerner PathNet V3.0 - Clinical Laboratory Information System (HNA)" \ PRINT "    Cerner Corporation (Kansas City, MO) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
100 PRINT "PATHNET> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "ACCESSION" OR VERB$ = "LIST" OR VERB$ = "LOG" THEN GOTO 820
360 IF VERB$ = "VERIFY" OR VERB$ = "AUTO" THEN GOTO 960
370 IF VERB$ = "PANIC" OR VERB$ = "CRITICAL" THEN GOTO 1120
380 IF VERB$ = "CHART" OR VERB$ = "CUMULATIVE" THEN GOTO 1250
390 IF VERB$ = "ADD" OR VERB$ = "ORDER" THEN GOTO 1380
400 IF VERB$ = "SAVE" THEN GOTO 1550
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "PATHNET: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_LAB% = 4%
710 L_ACC$(1%) = "AC-9001" \ L_PAT$(1%) = "MORRISON, ELEANOR " \ L_TEST$(1%) = "GLUCOSE" \ L_VAL%(1%) = 420% \ L_LOW%(1%) = 70% \ L_HIGH%(1%) = 110% \ L_STAT$(1%) = "PENDING"
720 L_ACC$(2%) = "AC-9002" \ L_PAT$(2%) = "KOWALSKI, STANLEY " \ L_TEST$(2%) = "SODIUM " \ L_VAL%(2%) = 140% \ L_LOW%(2%) = 135% \ L_HIGH%(2%) = 145% \ L_STAT$(2%) = "PENDING"
730 L_ACC$(3%) = "AC-9003" \ L_PAT$(3%) = "CHEN, RAYMOND     " \ L_TEST$(3%) = "POTASSX" \ L_VAL%(3%) = 68% \ L_LOW%(3%) = 35% \ L_HIGH%(3%) = 52% \ L_STAT$(3%) = "PENDING"
740 L_ACC$(4%) = "AC-9004" \ L_PAT$(4%) = "MORRISON, ELEANOR " \ L_TEST$(4%) = "WBC-CNT" \ L_VAL%(4%) = 75% \ L_LOW%(4%) = 45% \ L_HIGH%(4%) = 110% \ L_STAT$(4%) = "PENDING"
750 PRINT "[Sample Cerner PathNet V3.0 LIS dataset loaded - 4 Clinical Specimen Accessions]" \ GOTO 495
820 IF NUM_LAB% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Cerner PathNet Specimen Barcode Accession Log — Site: "; HOSP_ID$ \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_LAB% THEN GOTO 920
870 P_P$ = LEFT$(L_PAT$(LI%) + BLANKS$, 19%)
880 PRINT "  "; LI%; "  "; L_ACC$(LI%); "  "; P_P$; "  "; L_TEST$(LI%); "  "; L_VAL%(LI%); " ("; L_LOW%(LI%); "-"; L_HIGH%(LI%); ") "; L_STAT$(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_LAB% = 0% THEN GOTO 3370
970 VI% = 1% \ NORM_C% = 0% \ CRIT_C% = 0%
980 IF VI% > NUM_LAB% THEN GOTO 1060
990 L_STAT$(VI%) = "VERIFIED"
1000 IF L_VAL%(VI%) < L_LOW%(VI%) THEN L_STAT$(VI%) = "PANIC-LO"
1010 IF L_VAL%(VI%) > L_HIGH%(VI%) THEN L_STAT$(VI%) = "PANIC-HI"
1020 IF L_STAT$(VI%) = "VERIFIED" THEN NORM_C% = NORM_C% + 1%
1030 IF L_STAT$(VI%) <> "VERIFIED" THEN CRIT_C% = CRIT_C% + 1%
1040 VI% = VI% + 1% \ GOTO 980
1060 PRINT "[Cerner PathNet Analyzer Verification Complete: "; NORM_C%; " Verified Normal | "; CRIT_C%; " Critical Panic Flagged]" \ GOTO 495
1120 IF NUM_LAB% = 0% THEN GOTO 3370
1140 PI% = 1% \ P_CNT% = 0%
1150 IF PI% > NUM_LAB% THEN GOTO 1220
1160 IF L_VAL%(PI%) >= L_LOW%(PI%) AND L_VAL%(PI%) <= L_HIGH%(PI%) THEN GOTO 1210
1170 P_CNT% = P_CNT% + 1%
1180 PRINT "  **PANIC ALERT** "; L_ACC$(PI%); " | "; L_PAT$(PI%); " | "; L_TEST$(PI%); " = "; L_VAL%(PI%); " (Ref: "; L_LOW%(PI%); "-"; L_HIGH%(PI%); ")"
1210 PI% = PI% + 1% \ GOTO 1150
1220 PRINT "  [PathNet Panic Summary: "; P_CNT%; " Critical Panic Value Alerts requiring MD notification]" \ GOTO 495
1250 IF NUM_LAB% = 0% THEN GOTO 3370
1270 CI% = 1% \ C_SUM% = 0%
1280 IF CI% > NUM_LAB% THEN GOTO 1330
1290 C_SUM% = C_SUM% + L_VAL%(CI%)
1300 PRINT "  Patient: "; L_PAT$(CI%); " | Assay: "; L_TEST$(CI%); " | Val="; L_VAL%(CI%); " | Status="; L_STAT$(CI%)
1310 CI% = CI% + 1% \ GOTO 1280
1330 PRINT "  [PathNet Cumulative Chart: "; NUM_LAB%; " results charted | Aggregate Assay Index = "; C_SUM%; "]" \ GOTO 495
1380 IF NUM_LAB% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ A_V$ = T_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ P_V$ = T_OUT$ \ REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ T_V$ = T_OUT$ \ REM3$ = MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%) \ C4% = INSTR(1%, REM3$, ",")
1480 IF C4% = 0% THEN GOTO 1500
1482 VL_V% = VAL(LEFT$(REM3$, C4% - 1%)) \ REM4$ = MID$(REM3$, C4% + 1%, LEN(REM3$) - C4%) \ C5% = INSTR(1%, REM4$, ",")
1484 IF C5% = 0% THEN GOTO 1500
1486 LO_V% = VAL(LEFT$(REM4$, C5% - 1%)) \ HI_V% = VAL(MID$(REM4$, C5% + 1%, LEN(REM4$) - C5%))
1490 NUM_LAB% = NUM_LAB% + 1% \ L_ACC$(NUM_LAB%) = A_V$ \ L_PAT$(NUM_LAB%) = P_V$ \ L_TEST$(NUM_LAB%) = T_V$ \ L_VAL%(NUM_LAB%) = VL_V% \ L_LOW%(NUM_LAB%) = LO_V% \ L_HIGH%(NUM_LAB%) = HI_V% \ L_STAT$(NUM_LAB%) = "PENDING"
1495 PRINT "[PathNet Specimen #"; NUM_LAB%; " accessioned: "; A_V$; " ("; P_V$; ", "; T_V$; "="; VL_V%; ")]" \ GOTO 495
1500 PRINT "PATHNET: Syntax is ADD <acc>, <patient>, <test>, <val>, <low>, <high>" \ GOTO 495
1510 PRINT "PATHNET: Accession buffer full" \ GOTO 495
1550 IF NUM_LAB% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_LAB% THEN GOTO 1630
1600 PRINT #2%, L_ACC$(SI%); "|"; L_PAT$(SI%); "|"; L_TEST$(SI%); "|"; L_VAL%(SI%); "|"; L_LOW%(SI%); "|"; L_HIGH%(SI%); "|"; L_STAT$(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_LAB%; " PathNet records saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_LAB% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FA$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1790 FP$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1810 FT$ = LEFT$(REM2$, P3% - 1%) \ REM3$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ P4% = INSTR(1%, REM3$, "|")
1820 FVL% = VAL(LEFT$(REM3$, P4% - 1%)) \ REM4$ = MID$(REM3$, P4% + 1%, LEN(REM3$) - P4%) \ P5% = INSTR(1%, REM4$, "|")
1830 FLO% = VAL(LEFT$(REM4$, P5% - 1%)) \ REM5$ = MID$(REM4$, P5% + 1%, LEN(REM4$) - P5%) \ P6% = INSTR(1%, REM5$, "|")
1840 FHI% = VAL(LEFT$(REM5$, P6% - 1%)) \ FST$ = MID$(REM5$, P6% + 1%, LEN(REM5$) - P6%)
1845 NUM_LAB% = NUM_LAB% + 1% \ L_ACC$(NUM_LAB%) = FA$ \ L_PAT$(NUM_LAB%) = FP$ \ L_TEST$(NUM_LAB%) = FT$ \ L_VAL%(NUM_LAB%) = FVL% \ L_LOW%(NUM_LAB%) = FLO% \ L_HIGH%(NUM_LAB%) = FHI% \ L_STAT$(NUM_LAB%) = FST$ \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_LAB%; " PathNet records loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Cerner PathNet V3.0 Clinical LIS Status: Cluster="; HOSP_ID$; " | File="; DB_FILE$; " (Specimens: "; NUM_LAB%; ")" \ GOTO 495
2050 NUM_LAB% = 0% \ PRINT "[PathNet accession log cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Cerner PathNet V3.0 Commands: SAMPLE, ACCESSION, VERIFY, PANIC, CHART, ORDER/ADD, SAVE, LOAD, SHOW, CLEAR, EXIT" \ PRINT EQU$ \ GOTO 495
3370 PRINT "PATHNET: Accession log is empty. Use SAMPLE or ORDER/ADD." \ GOTO 495
3400 END
