10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM D_TITLE$(30%) \ DIM D_AUTH$(30%) \ DIM D_DATE$(30%) \ DIM D_CAT$(30%) \ DIM D_STAT$(30%) \ DIM D_BODY$(30%) \ DIM L_TEXT$(100%)
20 DIM DP_NAME$(20%) \ DIM DP_COMP$(20%) \ DIM DP_SYS$(20%) \ NUM_DOCS% = 0% \ CURR_DOC% = 1% \ NUM_LINES% = 0% \ NUM_DP% = 0% \ CURR_CAT$ = "ALL" \ LIB_FILE$ = "DECWORD.DAT"
30 LM% = 5% \ RM% = 72% \ PL% = 55% \ SPACING% = 1% \ DOC_HDR$ = "DECword/DP Document Processing System" \ DOC_FTR$ = "Digital Equipment Corporation"
40 BLANKS$ = "                                                                                "
50 SEP$    = "--------------------------------------------------------------------------------"
60 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
70 IF CMD_LINE$ = "" THEN GOTO 90
80 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 180
90 PRINT EQU$ \ PRINT "    DECword/DP V3.0 - Word & Data Processing System" \ PRINT "    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11" \ PRINT EQU$
100 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
110 PRINT "WP> "; \ LINE INPUT RAW_INPUT$
120 IF LEN(RAW_INPUT$) = 0% THEN GOTO 3400
130 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 26% THEN GOTO 3400
140 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 0% THEN GOTO 3400
150 T_IN$ = RAW_INPUT$ \ GOSUB 500
160 IF T_OUT$ = "" THEN GOTO 110
170 SC_REM$ = T_OUT$
180 IF SC_REM$ = "" THEN GOTO 240
190 SC_P% = INSTR(1%, SC_REM$, ";")
200 IF SC_P% = 0% THEN GOTO 220
210 RAW_CMD$ = LEFT$(SC_REM$, SC_P% - 1%) \ SC_REM$ = MID$(SC_REM$, SC_P% + 1%, LEN(SC_REM$) - SC_P%) \ GOTO 230
220 RAW_CMD$ = SC_REM$ \ SC_REM$ = ""
230 GOSUB 260 \ GOTO 180
240 IF IS_BATCH% = 1% THEN GOTO 3400
250 GOTO 110
260 T_IN$ = RAW_CMD$ \ GOSUB 500 \ WORK_CMD$ = T_OUT$
270 IF WORK_CMD$ = "" THEN GOTO 495
280 SP% = INSTR(1%, WORK_CMD$, " ")
290 IF SP% = 0% THEN GOTO 310
300 VERB$ = LEFT$(WORK_CMD$, SP% - 1%) \ ARGS$ = MID$(WORK_CMD$, SP% + 1%, LEN(WORK_CMD$) - SP%) \ GOTO 320
310 VERB$ = WORK_CMD$ \ ARGS$ = ""
320 U_IN$ = VERB$ \ GOSUB 580 \ VERB$ = U_OUT$ \ T_IN$ = ARGS$ \ GOSUB 500 \ ARGS$ = T_OUT$
330 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "BYE" THEN GOTO 3400
340 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 3220
350 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 820
360 IF VERB$ = "DIR" OR VERB$ = "INDEX" OR VERB$ = "DIRECTORY" THEN GOTO 960
370 IF VERB$ = "SELECT" OR VERB$ = "EDIT" THEN GOTO 1130
380 IF VERB$ = "CREATE" OR VERB$ = "NEWDOC" THEN GOTO 1210
390 IF VERB$ = "READ" OR VERB$ = "VIEW" OR VERB$ = "LIST" OR VERB$ = "TYPE" THEN GOTO 1360
400 IF VERB$ = "APPEND" OR VERB$ = "ADD" THEN GOTO 1500
410 IF VERB$ = "DELLINE" THEN GOTO 1640
420 IF VERB$ = "REPLACE" OR VERB$ = "SUBSTITUTE" THEN GOTO 1740
430 IF VERB$ = "FIND" OR VERB$ = "SEARCH" THEN GOTO 1870
440 IF VERB$ = "RULER" OR VERB$ = "MARGIN" THEN GOTO 1990
450 IF VERB$ = "HEADER" THEN GOTO 2120
455 IF VERB$ = "FOOTER" THEN GOTO 2150
460 IF VERB$ = "FORMAT" OR VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 2180
465 IF VERB$ = "DPLIST" OR VERB$ = "RECORDS" THEN GOTO 2470
470 IF VERB$ = "DPADD" THEN GOTO 2560
475 IF VERB$ = "MERGE" OR VERB$ = "LISTPROC" THEN GOTO 2670
480 IF VERB$ = "STATS" OR VERB$ = "COUNT" THEN GOTO 2830
482 IF VERB$ = "COPY" THEN GOTO 2980
484 IF VERB$ = "DELETE" OR VERB$ = "DEL" THEN GOTO 3040
486 IF VERB$ = "PURGE" THEN GOTO 3100
488 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 3180
490 IF VERB$ = "SAVE" THEN GOTO 3290
491 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3330
492 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3210
494 PRINT "DECword/DP: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
640 NUM_LINES% = 0%
645 IF CURR_DOC% < 1% THEN GOTO 675
650 IF CURR_DOC% > NUM_DOCS% THEN GOTO 675
655 U_REM$ = D_BODY$(CURR_DOC%)
660 IF U_REM$ = "" THEN GOTO 675
662 UP% = INSTR(1%, U_REM$, "~")
664 IF UP% = 0% THEN GOTO 670
666 NUM_LINES% = NUM_LINES% + 1% \ L_TEXT$(NUM_LINES%) = LEFT$(U_REM$, UP% - 1%) \ U_REM$ = MID$(U_REM$, UP% + 1%, LEN(U_REM$) - UP%) \ GOTO 660
670 NUM_LINES% = NUM_LINES% + 1% \ L_TEXT$(NUM_LINES%) = U_REM$
675 RETURN
680 IF CURR_DOC% < 1% THEN GOTO 698
682 IF CURR_DOC% > NUM_DOCS% THEN GOTO 698
684 P_BODY$ = "" \ PK_I% = 1%
686 IF PK_I% > NUM_LINES% THEN GOTO 696
688 IF PK_I% > 1% THEN P_BODY$ = P_BODY$ + "~"
690 P_BODY$ = P_BODY$ + L_TEXT$(PK_I%) \ PK_I% = PK_I% + 1% \ GOTO 686
696 D_BODY$(CURR_DOC%) = P_BODY$
698 RETURN
700 REP_OUT$ = "" \ R_REM$ = REP_STR$ \ O_LEN% = LEN(REP_OLD$)
710 IF O_LEN% = 0% THEN GOTO 770
720 IF R_REM$ = "" THEN GOTO 780
730 RP% = INSTR(1%, R_REM$, REP_OLD$)
740 IF RP% = 0% THEN GOTO 760
750 REP_OUT$ = REP_OUT$ + LEFT$(R_REM$, RP% - 1%) + REP_NEW$ \ REP_CNT% = REP_CNT% + 1% \ R_REM$ = MID$(R_REM$, RP% + O_LEN%, LEN(R_REM$) - RP% - O_LEN% + 1%) \ GOTO 720
760 REP_OUT$ = REP_OUT$ + R_REM$ \ GOTO 780
770 REP_OUT$ = REP_STR$
780 RETURN
790 T_IN$ = Q_IN$ \ GOSUB 500 \ Q_OUT$ = T_OUT$ \ QCH$ = CHR$(34%) \ QL% = LEN(Q_OUT$)
795 IF QL% < 2% THEN GOTO 815
800 IF LEFT$(Q_OUT$, 1%) <> QCH$ THEN GOTO 815
805 IF MID$(Q_OUT$, QL%, 1%) = QCH$ THEN Q_OUT$ = MID$(Q_OUT$, 2%, QL% - 2%)
815 RETURN
820 NUM_DOCS% = 4% \ CURR_DOC% = 1% \ CURR_CAT$ = "ALL"
830 D_TITLE$(1%) = "PDP-11/70 RSTS/E V8.0 Product Overview" \ D_AUTH$(1%) = "KEN.OLSEN" \ D_DATE$(1%) = "18-OCT-1982" \ D_CAT$(1%) = "LIBRARY" \ D_STAT$(1%) = "A"
840 D_BODY$(1%) = ".CENTER DIGITAL EQUIPMENT CORPORATION~.CENTER PDP-11/70 RSTS/E V8.0 SPECIFICATION~"
845 D_BODY$(1%) = D_BODY$(1%) + "PDP-11/70 DECword/DP provides word and data~processing for 63 users on VT100 and LQP02."
850 D_TITLE$(2%) = "DECword/DP Customer Form Letter" \ D_AUTH$(2%) = "WPS.SALES" \ D_DATE$(2%) = "19-OCT-1982" \ D_CAT$(2%) = "FINAL" \ D_STAT$(2%) = "A"
860 D_BODY$(2%) = ".CENTER DIGITAL EQUIPMENT CORPORATION~Dear <NAME>,~Thank you for selecting the <SYSTEM> system for <COMPANY>.~Your DECword/DP kit has shipped from Maynard, MA.~Sincerely, DEC WPS Group"
870 D_TITLE$(3%) = "Maynard Mill Engineering Memo" \ D_AUTH$(3%) = "G.BELL" \ D_DATE$(3%) = "20-OCT-1982" \ D_CAT$(3%) = "DRAFT" \ D_STAT$(3%) = "A"
880 D_BODY$(3%) = "MEMORANDUM: VAX-11/780 & PDP-11 Interconnect~All engineering documents must be archived in DECword/DP format~prior to the quarterly architecture review in Building 12."
890 D_TITLE$(4%) = "Preliminary WPS-8 Obsolete Draft" \ D_AUTH$(4%) = "OPERATOR" \ D_DATE$(4%) = "10-OCT-1982" \ D_CAT$(4%) = "WASTEBASKET" \ D_STAT$(4%) = "D"
900 D_BODY$(4%) = "Superseded draft notes for early WPS-8 tape distribution."
910 NUM_DP% = 3% \ DP_NAME$(1%) = "Dr. Harlan Anderson" \ DP_COMP$(1%) = "MIT Lincoln Laboratory" \ DP_SYS$(1%) = "PDP-11/70"
920 DP_NAME$(2%) = "Dr. Dennis Ritchie" \ DP_COMP$(2%) = "Bell Telephone Laboratories" \ DP_SYS$(2%) = "VAX-11/780"
930 DP_NAME$(3%) = "Dr. Tim Berners-Lee" \ DP_COMP$(3%) = "CERN European Research" \ DP_SYS$(3%) = "PDP-11/45"
940 GOSUB 640 \ PRINT "[Sample DECword/DP library loaded - 4 documents, 3 DP records]" \ GOTO 495
960 C_REQ$ = CURR_CAT$
965 IF ARGS$ = "" THEN GOTO 980
970 U_IN$ = ARGS$ \ GOSUB 580 \ C_REQ$ = U_OUT$
980 PRINT EQU$ \ PRINT "  DECword/DP Document Library - Category: "; C_REQ$ \ PRINT EQU$ \ PRINT "#   St  Category     Author          Date         Title" \ PRINT SEP$
990 IF NUM_DOCS% = 0% THEN GOTO 1110
1000 DI% = 1% \ MATCH_CNT% = 0%
1010 IF DI% > NUM_DOCS% THEN GOTO 1120
1020 IF C_REQ$ = "ALL" THEN GOTO 1050
1030 IF D_CAT$(DI%) = C_REQ$ THEN GOTO 1050
1040 GOTO 1100
1050 MATCH_CNT% = MATCH_CNT% + 1% \ IDX_STR$ = STR$(DI%) \ T_IN$ = IDX_STR$ \ GOSUB 500 \ IDX_PAD$ = LEFT$(T_OUT$ + "    ", 4%) \ ST_CH$ = " "
1060 IF DI% = CURR_DOC% THEN ST_CH$ = "*"
1070 IF D_STAT$(DI%) = "D" THEN ST_CH$ = "D"
1080 CAT_PAD$ = LEFT$(D_CAT$(DI%) + BLANKS$, 12%) \ AUTH_PAD$ = LEFT$(D_AUTH$(DI%) + BLANKS$, 15%) \ DATE_PAD$ = LEFT$(D_DATE$(DI%) + BLANKS$, 12%)
1090 PRINT IDX_PAD$; ST_CH$; "  "; CAT_PAD$; " "; AUTH_PAD$; " "; DATE_PAD$; " "; D_TITLE$(DI%)
1100 DI% = DI% + 1% \ GOTO 1010
1110 PRINT "    [No documents in library]"
1120 PRINT SEP$ \ PRINT "  "; MATCH_CNT%; " documents listed (* = Active, D = Deleted)" \ PRINT EQU$ \ GOTO 495
1130 IF NUM_DOCS% = 0% THEN GOTO 3370
1140 IF ARGS$ = "" THEN GOTO 1190
1150 REQ_D% = VAL(ARGS$)
1160 IF REQ_D% < 1% THEN GOTO 3380
1170 IF REQ_D% > NUM_DOCS% THEN GOTO 3380
1180 CURR_DOC% = REQ_D% \ GOSUB 640 \ PRINT "[Active document set to #"; CURR_DOC%; ": "; D_TITLE$(CURR_DOC%); " ("; NUM_LINES%; " lines)]" \ GOTO 495
1190 GOSUB 640 \ PRINT "[Active document is #"; CURR_DOC%; ": "; D_TITLE$(CURR_DOC%); " ("; NUM_LINES%; " lines)]" \ GOTO 495
1210 IF NUM_DOCS% >= 25% THEN GOTO 3390
1220 C_TITLE$ = "Untitled Document" \ C_AUTH$ = "OPERATOR" \ C_CAT$ = "LIBRARY"
1230 IF ARGS$ = "" THEN GOTO 1320
1240 C1% = INSTR(1%, ARGS$, ",")
1250 IF C1% = 0% THEN GOTO 1310
1260 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 790 \ C_TITLE$ = Q_OUT$ \ REM_A$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_A$, ",")
1270 IF C2% = 0% THEN GOTO 1300
1280 Q_IN$ = LEFT$(REM_A$, C2% - 1%) \ GOSUB 790 \ C_AUTH$ = Q_OUT$ \ Q_IN$ = MID$(REM_A$, C2% + 1%, LEN(REM_A$) - C2%) \ GOSUB 790 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ C_CAT$ = U_OUT$ \ GOTO 1320
1300 Q_IN$ = REM_A$ \ GOSUB 790 \ C_AUTH$ = Q_OUT$ \ GOTO 1320
1310 Q_IN$ = ARGS$ \ GOSUB 790 \ C_TITLE$ = Q_OUT$
1320 NUM_DOCS% = NUM_DOCS% + 1% \ CURR_DOC% = NUM_DOCS% \ D_TITLE$(CURR_DOC%) = C_TITLE$ \ D_AUTH$(CURR_DOC%) = C_AUTH$
1330 D_DATE$(CURR_DOC%) = "21-OCT-1982" \ D_CAT$(CURR_DOC%) = C_CAT$ \ D_STAT$(CURR_DOC%) = "A" \ D_BODY$(CURR_DOC%) = "" \ NUM_LINES% = 0%
1340 PRINT "[Document #"; CURR_DOC%; " created: "; C_TITLE$; "]" \ GOTO 495
1360 IF NUM_DOCS% = 0% THEN GOTO 3370
1370 REQ_D% = CURR_DOC%
1380 IF ARGS$ <> "" THEN REQ_D% = VAL(ARGS$)
1390 IF REQ_D% < 1% THEN GOTO 3380
1400 IF REQ_D% > NUM_DOCS% THEN GOTO 3380
1410 CURR_DOC% = REQ_D% \ GOSUB 640
1420 PRINT EQU$ \ PRINT "Document #"; CURR_DOC%; ": "; D_TITLE$(CURR_DOC%) \ PRINT "Author:   "; D_AUTH$(CURR_DOC%); "    Date: "; D_DATE$(CURR_DOC%); "    Category: "; D_CAT$(CURR_DOC%) \ PRINT SEP$
1430 IF NUM_LINES% = 0% THEN GOTO 1480
1440 RI% = 1%
1450 IF RI% > NUM_LINES% THEN GOTO 1490
1460 L_STR$ = STR$(RI%) \ T_IN$ = L_STR$ \ GOSUB 500 \ L_PAD$ = LEFT$(T_OUT$ + "   ", 3%) \ PRINT L_PAD$; ": "; L_TEXT$(RI%) \ RI% = RI% + 1% \ GOTO 1450
1480 PRINT "  [Empty document]"
1490 PRINT EQU$ \ GOTO 495
1500 IF NUM_DOCS% = 0% THEN GOTO 3370
1510 GOSUB 640
1520 IF ARGS$ = "" THEN GOTO 1580
1530 Q_IN$ = ARGS$ \ GOSUB 790 \ A_REM$ = Q_OUT$
1540 IF A_REM$ = "" THEN GOTO 1620
1550 AP% = INSTR(1%, A_REM$, "~")
1560 IF AP% = 0% THEN GOTO 1575
1570 NUM_LINES% = NUM_LINES% + 1% \ L_TEXT$(NUM_LINES%) = LEFT$(A_REM$, AP% - 1%) \ A_REM$ = MID$(A_REM$, AP% + 1%, LEN(A_REM$) - AP%) \ GOTO 1540
1575 NUM_LINES% = NUM_LINES% + 1% \ L_TEXT$(NUM_LINES%) = A_REM$ \ GOTO 1620
1580 PRINT "Enter text lines for Document #"; CURR_DOC%; " (end with . on a blank line):"
1590 LINE INPUT A_INP$
1600 IF A_INP$ = "." THEN GOTO 1620
1610 NUM_LINES% = NUM_LINES% + 1% \ L_TEXT$(NUM_LINES%) = A_INP$ \ GOTO 1590
1620 GOSUB 680 \ PRINT "[Appended to Document #"; CURR_DOC%; " ("; NUM_LINES%; " lines)]" \ GOTO 495
1640 IF NUM_DOCS% = 0% THEN GOTO 3370
1650 GOSUB 640 \ DL% = VAL(ARGS$)
1660 IF DL% < 1% THEN GOTO 1720
1670 IF DL% > NUM_LINES% THEN GOTO 1720
1680 DI% = DL%
1690 IF DI% >= NUM_LINES% THEN GOTO 1710
1700 L_TEXT$(DI%) = L_TEXT$(DI% + 1%) \ DI% = DI% + 1% \ GOTO 1690
1710 NUM_LINES% = NUM_LINES% - 1% \ GOSUB 680 \ PRINT "[Line "; DL%; " deleted from Document #"; CURR_DOC%; "]" \ GOTO 495
1720 PRINT "DECword/DP: Line number out of range (1 to "; NUM_LINES%; ")" \ GOTO 495
1740 IF NUM_DOCS% = 0% THEN GOTO 3370
1750 C1% = INSTR(1%, ARGS$, ",")
1760 IF C1% = 0% THEN GOTO 1850
1770 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 790 \ REP_OLD$ = Q_OUT$ \ Q_IN$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ GOSUB 790 \ REP_NEW$ = Q_OUT$
1780 GOSUB 640 \ REP_CNT% = 0% \ RI% = 1%
1790 IF RI% > NUM_LINES% THEN GOTO 1830
1800 REP_STR$ = L_TEXT$(RI%) \ GOSUB 700 \ L_TEXT$(RI%) = REP_OUT$ \ RI% = RI% + 1% \ GOTO 1790
1830 GOSUB 680 \ PRINT "[Replaced "; REP_CNT%; " occurrence(s) in Document #"; CURR_DOC%; "]" \ GOTO 495
1850 PRINT "DECword/DP: Specify old and new text (REPLACE <old>, <new>)" \ GOTO 495
1870 IF NUM_DOCS% = 0% THEN GOTO 3370
1880 IF ARGS$ = "" THEN GOTO 1970
1890 Q_IN$ = ARGS$ \ GOSUB 790 \ F_PAT$ = Q_OUT$ \ GOSUB 640 \ F_CNT% = 0% \ FI% = 1%
1900 PRINT "Search results for '"; F_PAT$; "' in Document #"; CURR_DOC%; ":"
1910 IF FI% > NUM_LINES% THEN GOTO 1960
1920 FP% = INSTR(1%, L_TEXT$(FI%), F_PAT$)
1930 IF FP% = 0% THEN GOTO 1950
1940 F_CNT% = F_CNT% + 1% \ PRINT "  Line "; FI%; ": "; L_TEXT$(FI%)
1950 FI% = FI% + 1% \ GOTO 1910
1960 PRINT "[Found "; F_CNT%; " matching line(s)]" \ GOTO 495
1970 PRINT "DECword/DP: Specify search text (FIND <pattern>)" \ GOTO 495
1990 IF ARGS$ = "" THEN GOTO 2090
2000 R_ARGS$ = ARGS$ \ REP_STR$ = R_ARGS$ \ REP_OLD$ = "," \ REP_NEW$ = " " \ GOSUB 700 \ T_IN$ = REP_OUT$ \ GOSUB 500 \ R_ARGS$ = T_OUT$
2010 S1% = INSTR(1%, R_ARGS$, " ")
2020 IF S1% = 0% THEN GOTO 2070
2030 LM% = VAL(LEFT$(R_ARGS$, S1% - 1%)) \ T_IN$ = MID$(R_ARGS$, S1% + 1%, LEN(R_ARGS$) - S1%) \ GOSUB 500 \ R_REM2$ = T_OUT$ \ S2% = INSTR(1%, R_REM2$, " ")
2040 IF S2% = 0% THEN GOTO 2060
2050 RM% = VAL(LEFT$(R_REM2$, S2% - 1%)) \ SPACING% = VAL(MID$(R_REM2$, S2% + 1%, LEN(R_REM2$) - S2%)) \ GOTO 2080
2060 RM% = VAL(R_REM2$) \ GOTO 2080
2070 LM% = VAL(R_ARGS$)
2080 IF LM% < 1% THEN LM% = 1%
2082 IF RM% < 30% THEN RM% = 72%
2084 IF SPACING% < 1% THEN SPACING% = 1%
2086 IF SPACING% > 2% THEN SPACING% = 2%
2090 PRINT "DECword/DP Ruler Settings: LM="; LM%; " RM="; RM%; " Spacing="; SPACING%; " PageLen="; PL%
2100 PRINT "....L....T....1....T....2....T....3....T....4....T....5....T....6....T.R" \ GOTO 495
2120 Q_IN$ = ARGS$ \ GOSUB 790 \ DOC_HDR$ = Q_OUT$ \ PRINT "[Document header set to: "; DOC_HDR$; "]" \ GOTO 495
2150 Q_IN$ = ARGS$ \ GOSUB 790 \ DOC_FTR$ = Q_OUT$ \ PRINT "[Document footer set to: "; DOC_FTR$; "]" \ GOTO 495
2180 IF NUM_DOCS% = 0% THEN GOTO 3370
2190 TO_FILE% = 0% \ OUT_FILE$ = ""
2200 IF VERB$ = "EXPORT" THEN GOTO 2250
2210 IF ARGS$ = "" THEN GOTO 2280
2220 U_IN$ = ARGS$ \ GOSUB 580
2230 IF LEFT$(U_OUT$, 3%) = "ON " THEN GOTO 2260
2240 REQ_D% = VAL(ARGS$)
2242 IF REQ_D% < 1% THEN GOTO 2280
2244 IF REQ_D% > NUM_DOCS% THEN GOTO 2280
2246 CURR_DOC% = REQ_D% \ GOTO 2280
2250 IF ARGS$ = "" THEN GOTO 2450
2255 Q_IN$ = ARGS$ \ GOSUB 790 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1% \ GOTO 2280
2260 Q_IN$ = MID$(ARGS$, 4%, LEN(ARGS$) - 3%) \ GOSUB 790 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1%
2280 GOSUB 640 \ PAD_LM$ = LEFT$(BLANKS$, LM%) \ WIDTH% = RM% - LM%
2290 IF TO_FILE% = 1% THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2295 IF TO_FILE% = 1% THEN GOTO 2310
2300 PRINT EQU$ \ PRINT PAD_LM$; DOC_HDR$ \ PRINT SEP$ \ GOTO 2320
2310 PRINT #2%, EQU$ \ PRINT #2%, PAD_LM$; DOC_HDR$ \ PRINT #2%, SEP$
2320 FI% = 1%
2330 IF FI% > NUM_LINES% THEN GOTO 2420
2340 F_LINE$ = L_TEXT$(FI%)
2350 IF LEFT$(F_LINE$, 8%) = ".CENTER " THEN GOTO 2380
2360 OUT_L$ = PAD_LM$ + F_LINE$ \ GOTO 2390
2380 C_TXT$ = MID$(F_LINE$, 9%, LEN(F_LINE$) - 8%) \ C_PAD% = (WIDTH% - LEN(C_TXT$)) / 2%
2385 IF C_PAD% < 0% THEN C_PAD% = 0%
2388 OUT_L$ = PAD_LM$ + LEFT$(BLANKS$, C_PAD%) + C_TXT$
2390 IF TO_FILE% = 0% THEN PRINT OUT_L$
2395 IF TO_FILE% = 1% THEN PRINT #2%, OUT_L$
2400 IF SPACING% = 2% AND TO_FILE% = 0% THEN PRINT ""
2405 IF SPACING% = 2% AND TO_FILE% = 1% THEN PRINT #2%, ""
2410 FI% = FI% + 1% \ GOTO 2330
2420 IF TO_FILE% = 1% THEN GOTO 2430
2425 PRINT SEP$ \ PRINT PAD_LM$; DOC_FTR$; " - Page 1" \ PRINT EQU$ \ GOTO 2448
2430 PRINT #2%, SEP$ \ PRINT #2%, PAD_LM$; DOC_FTR$; " - Page 1" \ PRINT #2%, EQU$ \ CLOSE #2%
2445 PRINT "[Document #"; CURR_DOC%; " formatted to "; OUT_FILE$; "]"
2448 GOTO 495
2450 PRINT "DECword/DP: Specify output filename (EXPORT <file> or PRINT ON <file>)" \ GOTO 495
2470 PRINT EQU$ \ PRINT "  DECword/DP Data Processing (DP) List Records" \ PRINT EQU$ \ PRINT "#   <NAME>                   <COMPANY>                    <SYSTEM>" \ PRINT SEP$
2480 IF NUM_DP% = 0% THEN GOTO 2540
2490 DPI% = 1%
2500 IF DPI% > NUM_DP% THEN GOTO 2550
2510 IDX_STR$ = STR$(DPI%) \ T_IN$ = IDX_STR$ \ GOSUB 500 \ IDX_PAD$ = LEFT$(T_OUT$ + "    ", 4%)
2520 N_PAD$ = LEFT$(DP_NAME$(DPI%) + BLANKS$, 24%) \ C_PAD$ = LEFT$(DP_COMP$(DPI%) + BLANKS$, 28%)
2530 PRINT IDX_PAD$; N_PAD$; " "; C_PAD$; " "; DP_SYS$(DPI%) \ DPI% = DPI% + 1% \ GOTO 2500
2540 PRINT "    [No DP records loaded]"
2550 PRINT SEP$ \ PRINT "  "; NUM_DP%; " DP list record(s) available for MERGE" \ PRINT EQU$ \ GOTO 495
2560 IF NUM_DP% >= 20% THEN GOTO 2650
2570 C1% = INSTR(1%, ARGS$, ",")
2580 IF C1% = 0% THEN GOTO 2640
2590 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 790 \ N_VAL$ = Q_OUT$ \ REM_A$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_A$, ",")
2600 IF C2% = 0% THEN GOTO 2640
2610 Q_IN$ = LEFT$(REM_A$, C2% - 1%) \ GOSUB 790 \ C_VAL$ = Q_OUT$ \ Q_IN$ = MID$(REM_A$, C2% + 1%, LEN(REM_A$) - C2%) \ GOSUB 790 \ S_VAL$ = Q_OUT$
2620 NUM_DP% = NUM_DP% + 1% \ DP_NAME$(NUM_DP%) = N_VAL$ \ DP_COMP$(NUM_DP%) = C_VAL$ \ DP_SYS$(NUM_DP%) = S_VAL$
2630 PRINT "[DP Record #"; NUM_DP%; " added: "; N_VAL$; " ("; C_VAL$; ")]" \ GOTO 495
2640 PRINT "DECword/DP: Syntax is DPADD <name>, <company>, <system>" \ GOTO 495
2650 PRINT "DECword/DP: DP record table full" \ GOTO 495
2670 IF NUM_DOCS% = 0% THEN GOTO 3370
2680 IF NUM_DP% = 0% THEN GOTO 2810
2690 IF ARGS$ <> "" THEN CURR_DOC% = VAL(ARGS$)
2700 IF CURR_DOC% < 1% THEN CURR_DOC% = 1%
2710 IF CURR_DOC% > NUM_DOCS% THEN CURR_DOC% = NUM_DOCS%
2720 GOSUB 640 \ PAD_LM$ = LEFT$(BLANKS$, LM%) \ MI% = 1%
2730 IF MI% > NUM_DP% THEN GOTO 2800
2740 PRINT EQU$ \ PRINT "  [DECword/DP List Processing Merge - Record #"; MI%; " of "; NUM_DP%; "]" \ PRINT SEP$
2750 ML% = 1%
2760 IF ML% > NUM_LINES% THEN GOTO 2795
2770 M_LINE$ = L_TEXT$(ML%)
2775 IF LEFT$(M_LINE$, 8%) = ".CENTER " THEN M_LINE$ = MID$(M_LINE$, 9%, LEN(M_LINE$) - 8%)
2780 REP_STR$ = M_LINE$ \ REP_OLD$ = "<NAME>" \ REP_NEW$ = DP_NAME$(MI%) \ GOSUB 700
2785 REP_STR$ = REP_OUT$ \ REP_OLD$ = "<COMPANY>" \ REP_NEW$ = DP_COMP$(MI%) \ GOSUB 700
2790 REP_STR$ = REP_OUT$ \ REP_OLD$ = "<SYSTEM>" \ REP_NEW$ = DP_SYS$(MI%) \ GOSUB 700 \ PRINT PAD_LM$; REP_OUT$ \ ML% = ML% + 1% \ GOTO 2760
2795 MI% = MI% + 1% \ GOTO 2730
2800 PRINT EQU$ \ PRINT "[List Processing complete: "; NUM_DP%; " merged documents generated]" \ GOTO 495
2810 PRINT "DECword/DP: No DP records available. Use SAMPLE or DPADD." \ GOTO 495
2830 IF NUM_DOCS% = 0% THEN GOTO 3370
2840 GOSUB 640 \ W_CNT% = 0% \ CH_CNT% = 0% \ TOK_CNT% = 0% \ SI% = 1%
2850 IF SI% > NUM_LINES% THEN GOTO 2950
2860 S_LN$ = L_TEXT$(SI%) \ CH_CNT% = CH_CNT% + LEN(S_LN$)
2870 IF INSTR(1%, S_LN$, "<") > 0% THEN TOK_CNT% = TOK_CNT% + 1%
2880 T_IN$ = S_LN$ \ GOSUB 500 \ W_REM$ = T_OUT$
2890 IF W_REM$ = "" THEN GOTO 2940
2900 W_CNT% = W_CNT% + 1% \ WP% = INSTR(1%, W_REM$, " ")
2910 IF WP% = 0% THEN GOTO 2940
2920 T_IN$ = MID$(W_REM$, WP% + 1%, LEN(W_REM$) - WP%) \ GOSUB 500 \ W_REM$ = T_OUT$ \ GOTO 2900
2940 SI% = SI% + 1% \ GOTO 2850
2950 PG_EST% = 1%
2952 IF NUM_LINES% > PL% THEN PG_EST% = 2%
2960 PRINT "DECword/DP Document Statistics:" \ PRINT "  Document:       #"; CURR_DOC%; " ("; D_TITLE$(CURR_DOC%); ")"
2970 PRINT "  Lines:          "; NUM_LINES% \ PRINT "  Words:          "; W_CNT% \ PRINT "  Characters:     "; CH_CNT% \ PRINT "  Est. Pages:     "; PG_EST% \ PRINT "  DP Merge Lines: "; TOK_CNT% \ GOTO 495
2980 IF NUM_DOCS% = 0% THEN GOTO 3370
2990 IF NUM_DOCS% >= 25% THEN GOTO 3390
3000 SRC_D% = CURR_DOC%
3005 IF ARGS$ <> "" THEN SRC_D% = VAL(ARGS$)
3010 IF SRC_D% < 1% THEN GOTO 3380
3015 IF SRC_D% > NUM_DOCS% THEN GOTO 3380
3020 NUM_DOCS% = NUM_DOCS% + 1% \ D_TITLE$(NUM_DOCS%) = "Copy of " + D_TITLE$(SRC_D%) \ D_AUTH$(NUM_DOCS%) = D_AUTH$(SRC_D%) \ D_DATE$(NUM_DOCS%) = D_DATE$(SRC_D%)
3030 D_CAT$(NUM_DOCS%) = D_CAT$(SRC_D%) \ D_STAT$(NUM_DOCS%) = "A" \ D_BODY$(NUM_DOCS%) = D_BODY$(SRC_D%) \ PRINT "[Document #"; SRC_D%; " copied to Document #"; NUM_DOCS%; "]" \ GOTO 495
3040 IF NUM_DOCS% = 0% THEN GOTO 3370
3050 REQ_D% = CURR_DOC%
3055 IF ARGS$ <> "" THEN REQ_D% = VAL(ARGS$)
3060 IF REQ_D% < 1% THEN GOTO 3380
3065 IF REQ_D% > NUM_DOCS% THEN GOTO 3380
3070 D_STAT$(REQ_D%) = "D" \ D_CAT$(REQ_D%) = "WASTEBASKET" \ PRINT "[Document #"; REQ_D%; " marked deleted (moved to WASTEBASKET)]" \ GOTO 495
3100 IF NUM_DOCS% = 0% THEN GOTO 3370
3110 P_CNT% = 0% \ KEEP_CNT% = 0% \ PI% = 1%
3120 IF PI% > NUM_DOCS% THEN GOTO 3165
3130 IF D_STAT$(PI%) = "D" THEN GOTO 3155
3135 IF D_CAT$(PI%) = "WASTEBASKET" THEN GOTO 3155
3140 KEEP_CNT% = KEEP_CNT% + 1%
3145 IF KEEP_CNT% = PI% THEN GOTO 3160
3150 D_TITLE$(KEEP_CNT%) = D_TITLE$(PI%) \ D_AUTH$(KEEP_CNT%) = D_AUTH$(PI%) \ D_DATE$(KEEP_CNT%) = D_DATE$(PI%) \ D_CAT$(KEEP_CNT%) = D_CAT$(PI%) \ D_STAT$(KEEP_CNT%) = D_STAT$(PI%) \ D_BODY$(KEEP_CNT%) = D_BODY$(PI%) \ GOTO 3160
3155 P_CNT% = P_CNT% + 1%
3160 PI% = PI% + 1% \ GOTO 3120
3165 NUM_DOCS% = KEEP_CNT%
3168 IF CURR_DOC% > NUM_DOCS% THEN CURR_DOC% = NUM_DOCS%
3170 IF CURR_DOC% < 1% THEN CURR_DOC% = 1%
3175 GOSUB 640 \ PRINT "[Library purged - "; P_CNT%; " deleted documents removed]" \ GOTO 495
3180 GOSUB 640 \ DEL_CNT% = 0% \ SI% = 1%
3185 IF SI% > NUM_DOCS% THEN GOTO 3198
3190 IF D_STAT$(SI%) = "D" THEN DEL_CNT% = DEL_CNT% + 1%
3195 SI% = SI% + 1% \ GOTO 3185
3198 PRINT "DECword/DP System Status:" \ PRINT "  Active Document: #"; CURR_DOC%; " ("; NUM_LINES%; " lines)" \ PRINT "  Total Documents: "; NUM_DOCS%; " (Deleted: "; DEL_CNT%; ")"
3200 PRINT "  DP List Records: "; NUM_DP% \ PRINT "  Ruler Margins:   LM="; LM%; " RM="; RM%; " Spacing="; SPACING% \ GOTO 495
3210 NUM_DOCS% = 0% \ CURR_DOC% = 1% \ NUM_LINES% = 0% \ NUM_DP% = 0% \ PRINT "[DECword/DP library cleared]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "    DECword/DP Word & Data Processing Commands" \ PRINT EQU$ \ PRINT "  DIR [category]                   List documents in library"
3225 PRINT "  SELECT <doc#> / EDIT <doc#>      Select active document for editing" \ PRINT "  CREATE <title>, <auth>, <cat>    Create a new document in library"
3230 PRINT "  READ [doc#] / VIEW / LIST        Display document headers and numbered lines" \ PRINT "  APPEND [text] / DELLINE <line#>  Append text or delete a line"
3235 PRINT "  REPLACE <old>, <new>             Search and replace text across active doc" \ PRINT "  FIND <pattern>                   Search for text across active document"
3240 PRINT "  RULER [lm, rm, spacing]          Display or configure DECword WPS ruler" \ PRINT "  HEADER <text> / FOOTER <text>    Set document running header or footer"
3245 PRINT "  FORMAT / PRINT [ON <file>]       Format document with margins and headers" \ PRINT "  DPLIST / DPADD <n>, <c>, <s>     List or add Data Processing merge records"
3250 PRINT "  MERGE [doc#] / LISTPROC          Merge active form document with DP records" \ PRINT "  STATS / COUNT                    Display word, line, and character counts"
3255 PRINT "  COPY [doc#] / DELETE / PURGE     Copy, mark deleted, or purge documents" \ PRINT "  SAMPLE / SAVE [f] / LOAD [f]     Load demo library or save/load disk file"
3260 PRINT "  SHOW / CLEAR / EXIT              Show status, clear memory, or exit" \ PRINT EQU$ \ GOTO 495
3290 IF NUM_DOCS% = 0% THEN GOTO 3370
3295 SV_FILE$ = LIB_FILE$
3298 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
3300 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
3305 IF SI% > NUM_DOCS% THEN GOTO 3320
3310 PRINT #2%, D_TITLE$(SI%); "|"; D_AUTH$(SI%); "|"; D_DATE$(SI%); "|"; D_CAT$(SI%); "|"; D_STAT$(SI%); "|"; D_BODY$(SI%) \ SI% = SI% + 1% \ GOTO 3305
3320 CLOSE #2% \ PRINT "["; NUM_DOCS%; " documents saved to "; SV_FILE$; "]" \ GOTO 495
3330 LD_FILE$ = LIB_FILE$
3331 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
3332 ON ERROR GOTO 3362 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_DOCS% = 0%
3334 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
3336 IF T_OUT$ = "" THEN GOTO 3334
3338 P1% = INSTR(1%, T_OUT$, "|")
3339 IF P1% = 0% THEN GOTO 3334
3340 F_TIT$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
3341 IF P2% = 0% THEN GOTO 3334
3342 F_AUT$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
3343 IF P3% = 0% THEN GOTO 3334
3344 F_DAT$ = LEFT$(REM2$, P3% - 1%) \ REM3$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ P4% = INSTR(1%, REM3$, "|")
3345 IF P4% = 0% THEN GOTO 3334
3346 F_CAT$ = LEFT$(REM3$, P4% - 1%) \ REM4$ = MID$(REM3$, P4% + 1%, LEN(REM3$) - P4%) \ P5% = INSTR(1%, REM4$, "|")
3347 IF P5% = 0% THEN GOTO 3334
3348 F_STA$ = LEFT$(REM4$, P5% - 1%) \ F_BOD$ = MID$(REM4$, P5% + 1%, LEN(REM4$) - P5%) \ NUM_DOCS% = NUM_DOCS% + 1% \ D_TITLE$(NUM_DOCS%) = F_TIT$ \ D_AUTH$(NUM_DOCS%) = F_AUT$
3350 D_DATE$(NUM_DOCS%) = F_DAT$ \ D_CAT$(NUM_DOCS%) = F_CAT$ \ D_STAT$(NUM_DOCS%) = F_STA$ \ D_BODY$(NUM_DOCS%) = F_BOD$ \ GOTO 3334
3362 CLOSE #2% \ RESUME 3365
3365 ON ERROR GOTO 0 \ CURR_DOC% = 1% \ GOSUB 640 \ PRINT "["; NUM_DOCS%; " documents loaded from "; LD_FILE$; "]" \ GOTO 495
3370 PRINT "DECword/DP: No documents in library. Use SAMPLE or CREATE." \ GOTO 495
3380 PRINT "DECword/DP: Document number out of range (1 to "; NUM_DOCS%; ")" \ GOTO 495
3390 PRINT "DECword/DP: Document library is full" \ GOTO 495
3400 END
