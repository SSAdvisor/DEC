10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM CD_INDEX$(40%) \ DIM CD_CAT$(40%) \ DIM CD_NODE$(40%) \ DIM CD_BODY$(40%)
20 DIM FLD$(10%)
30 NUM_CARDS% = 0% \ CUR_CARD% = 0% \ DECK_TITLE$ = "DEC Engineering & Node Directory" \ DECK_FILE$ = "DEC_DIRECTORY.CRD"
40 BLANKS$ = "                                                                                " \ LBRK$ = "[" \ RBRK$ = "]" \ VBAR$ = "|" \ PIPE$ = "|"
50 SEP$    = "--------------------------------------------------------------------------------"
60 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ FORCE_CLI% = 0%
61 T_IN$ = COMMAND$ \ GOSUB 500 \ CMD_LINE$ = T_OUT$
62 IF LEFT$(CMD_LINE$, 5%) = "--cli" THEN FORCE_CLI% = 1%
63 IF FORCE_CLI% = 1% THEN T_IN$ = MID$(CMD_LINE$, 6%, LEN(CMD_LINE$) - 5%)
64 IF FORCE_CLI% = 1% THEN GOSUB 500
65 IF FORCE_CLI% = 1% THEN CMD_LINE$ = T_OUT$
66 IF CMD_LINE$ = "--x11" OR CMD_LINE$ = "-gui" THEN CMD_LINE$ = "SAMPLE; X11; EXIT"
67 IF_X11% = 1% \ CHK_X11$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --check-gui"
68 IF CMD_LINE$ = "" AND FORCE_CLI% = 0% THEN IF_X11% = SYS(CHK_X11$)
69 IF IF_X11% = 0% THEN CMD_LINE$ = "SAMPLE; X11; EXIT"
70 IF CMD_LINE$ = "" THEN GOTO 100
80 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 180
100 PRINT EQU$ \ PRINT "    DECwindows Cardfiler V3.0 - XUI/Motif Rotary Index Card Manager" \ PRINT "    Digital Equipment Corporation (DEC) VAX/VMS & ULTRIX Workstation Software" \ PRINT EQU$
110 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
120 PRINT "CARDFILER> "; \ LINE INPUT RAW_INPUT$
130 IF LEN(RAW_INPUT$) = 0% THEN GOTO 3400
140 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 26% THEN GOTO 3400
150 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 0% THEN GOTO 3400
160 T_IN$ = RAW_INPUT$ \ GOSUB 500
170 IF T_OUT$ = "" THEN GOTO 120
175 SC_REM$ = T_OUT$
180 IF SC_REM$ = "" THEN GOTO 240
190 SC_P% = INSTR(1%, SC_REM$, ";")
200 IF SC_P% = 0% THEN GOTO 220
210 RAW_CMD$ = LEFT$(SC_REM$, SC_P% - 1%) \ SC_REM$ = MID$(SC_REM$, SC_P% + 1%, LEN(SC_REM$) - SC_P%) \ GOTO 230
220 RAW_CMD$ = SC_REM$ \ SC_REM$ = ""
230 GOSUB 260 \ GOTO 180
240 IF IS_BATCH% = 1% THEN GOTO 3400
250 GOTO 120
260 T_IN$ = RAW_CMD$ \ GOSUB 500 \ WORK_CMD$ = T_OUT$
270 IF WORK_CMD$ = "" THEN GOTO 495
280 SP% = INSTR(1%, WORK_CMD$, " ")
290 IF SP% = 0% THEN GOTO 310
300 VERB$ = LEFT$(WORK_CMD$, SP% - 1%) \ ARGS$ = MID$(WORK_CMD$, SP% + 1%, LEN(WORK_CMD$) - SP%) \ GOTO 320
310 VERB$ = WORK_CMD$ \ ARGS$ = ""
320 U_IN$ = VERB$ \ GOSUB 580 \ VERB$ = U_OUT$ \ T_IN$ = ARGS$ \ GOSUB 500 \ ARGS$ = T_OUT$
330 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "BYE" THEN GOTO 3400
340 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 3220
350 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 750
360 IF VERB$ = "LIST" OR VERB$ = "DECK" OR VERB$ = "INDEX" OR VERB$ = "CARDS" THEN GOTO 940
370 IF VERB$ = "READ" OR VERB$ = "CARD" OR VERB$ = "SELECT" OR VERB$ = "VIEW" THEN GOTO 1150
380 IF VERB$ = "NEXT" THEN GOTO 1330
390 IF VERB$ = "PREV" OR VERB$ = "BACK" THEN GOTO 1400
400 IF VERB$ = "ADD" OR VERB$ = "NEWCARD" OR VERB$ = "CREATE" THEN GOTO 1470
410 IF VERB$ = "UPDATE" OR VERB$ = "EDIT" OR VERB$ = "MODIFY" THEN GOTO 1600
420 IF VERB$ = "DUP" OR VERB$ = "COPY" THEN GOTO 1740
430 IF VERB$ = "DELETE" OR VERB$ = "DEL" OR VERB$ = "REMOVE" THEN GOTO 1860
440 IF VERB$ = "SORT" THEN GOTO 1980
450 IF VERB$ = "SEARCH" OR VERB$ = "FIND" THEN GOTO 2200
460 IF VERB$ = "DISPLAY" OR VERB$ = "SCREEN" OR VERB$ = "RENDER" OR VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 2380
484 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2780
486 IF VERB$ = "SAVE" THEN GOTO 2900
488 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3010
490 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3180
492 IF VERB$ = "X11" OR VERB$ = "GUI" OR VERB$ = "XDISPLAY" THEN GOTO 3392
494 PRINT "CARDFILER: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
635 T_IN$ = Q_IN$ \ GOSUB 500 \ Q_OUT$ = T_OUT$ \ QCH$ = CHR$(34%) \ QL% = LEN(Q_OUT$)
638 IF QL% < 2% THEN GOTO 646
640 IF LEFT$(Q_OUT$, 1%) <> QCH$ THEN GOTO 646
642 IF MID$(Q_OUT$, QL%, 1%) = QCH$ THEN Q_OUT$ = MID$(Q_OUT$, 2%, QL% - 2%)
646 RETURN
650 NF% = 0% \ P_REM$ = P_IN$
655 IF NF% >= 9% THEN GOTO 690
660 PP% = INSTR(1%, P_REM$, PIPE$)
665 IF PP% = 0% THEN GOTO 680
670 NF% = NF% + 1% \ T_IN$ = LEFT$(P_REM$, PP% - 1%) \ GOSUB 500 \ FLD$(NF%) = T_OUT$
675 P_REM$ = MID$(P_REM$, PP% + 1%, LEN(P_REM$) - PP%) \ GOTO 655
680 NF% = NF% + 1% \ T_IN$ = P_REM$ \ GOSUB 500 \ FLD$(NF%) = T_OUT$
690 RETURN
750 NUM_CARDS% = 6% \ CUR_CARD% = 1% \ DECK_TITLE$ = "DEC Engineering & Node Directory"
760 CD_INDEX$(1%) = "Bell, Gordon"           \ CD_CAT$(1%) = "ENGINEERING" \ CD_NODE$(1%) = "MLO::BELL (DTN 223-4100)"
770 CD_BODY$(1%)  = "VP of Engineering - PDP-11, VAX-11/780 Architecture, Maynard Mill MLO"
780 CD_INDEX$(2%) = "Cutler, Dave"           \ CD_CAT$(2%) = "VAX/VMS"     \ CD_NODE$(2%) = "ZKO::CUTLER (DTN 381-2001)"
790 CD_BODY$(2%)  = "RSX-11M, VAX/VMS, MicroVAX I/II, VAXeln & DECwest Bellevue Lab"
800 CD_INDEX$(3%) = "Kronenberg, Nancy"      \ CD_CAT$(3%) = "VAXCLUSTER"  \ CD_NODE$(3%) = "MRO::NANCY (DTN 297-5120)"
810 CD_BODY$(3%)  = "Computer Interconnect (CI780), SCA Protocol, HSC50 Storage Controller"
820 CD_INDEX$(4%) = "Stewart, Larry"         \ CD_CAT$(4%) = "ULTRIX"      \ CD_NODE$(4%) = "CRL::STEWART (DTN 226-8900)"
830 CD_BODY$(4%)  = "Cambridge Research Lab - Firefly Multiprocessor & DECstation 3100"
840 CD_INDEX$(5%) = "Customer Response Ctr"  \ CD_CAT$(5%) = "SUPPORT"     \ CD_NODE$(5%) = "CSC::HELP (1-800-332-8000)"
850 CD_BODY$(5%)  = "Colorado Springs Field Service & Software Patch Distribution Center"
860 CD_INDEX$(6%) = "DECUS Program Library"  \ CD_CAT$(6%) = "DECUS"       \ CD_NODE$(6%) = "MR1::DECUS (DTN 231-6500)"
870 CD_BODY$(6%)  = "Digital Equipment Computer Users Society Symposia & SIG Tape Catalog"
880 PRINT "[Sample DECwindows Cardfiler deck loaded: 6 index cards in "; DECK_FILE$; "]" \ GOTO 495
940 IF NUM_CARDS% = 0% THEN GOTO 3370
950 U_IN$ = ARGS$ \ GOSUB 580 \ C_FLT$ = U_OUT$
960 PRINT EQU$ \ PRINT "  DECwindows Cardfiler Index Deck: "; DECK_TITLE$; " ("; NUM_CARDS%; " cards)" \ PRINT EQU$
970 PRINT "Card#  Index Header             Category      DECnet Node / Phone" \ PRINT SEP$
980 SH_CNT% = 0% \ CI% = 1%
990 IF CI% > NUM_CARDS% THEN GOTO 1090
1000 U_IN$ = CD_CAT$(CI%) \ GOSUB 580 \ U_CAT$ = U_OUT$
1010 IF C_FLT$ <> "" AND U_CAT$ <> C_FLT$ THEN GOTO 1080
1020 SH_CNT% = SH_CNT% + 1%
1030 C_S$ = STR$(CI%) \ T_IN$ = C_S$ \ GOSUB 500 \ C_P$ = LEFT$(T_OUT$ + BLANKS$, 7%)
1040 IX_P$ = LEFT$(CD_INDEX$(CI%) + BLANKS$, 25%)
1050 CT_P$ = LEFT$(CD_CAT$(CI%) + BLANKS$, 14%)
1060 PRINT C_P$; IX_P$; CT_P$; CD_NODE$(CI%)
1080 CI% = CI% + 1% \ GOTO 990
1090 PRINT SEP$ \ PRINT "  "; SH_CNT%; " card(s) listed." \ PRINT EQU$ \ GOTO 495
1150 IF NUM_CARDS% = 0% THEN GOTO 3370
1160 IF ARGS$ = "" THEN GOTO 1260
1170 Q_IN$ = ARGS$ \ GOSUB 635 \ R_ARG$ = Q_OUT$ \ FOUND_C% = 0% \ CV% = VAL(R_ARG$)
1180 IF CV% >= 1% AND CV% <= NUM_CARDS% THEN FOUND_C% = CV%
1190 IF FOUND_C% > 0% THEN GOTO 1250
1200 U_IN$ = R_ARG$ \ GOSUB 580 \ U_TARG$ = U_OUT$ \ CI% = 1%
1210 IF CI% > NUM_CARDS% THEN GOTO 1250
1220 U_IN$ = CD_INDEX$(CI%) \ GOSUB 580
1230 IF INSTR(1%, U_OUT$, U_TARG$) > 0% AND FOUND_C% = 0% THEN FOUND_C% = CI%
1240 CI% = CI% + 1% \ GOTO 1210
1250 IF FOUND_C% = 0% THEN GOTO 1310
1255 CUR_CARD% = FOUND_C%
1260 IF CUR_CARD% < 1% OR CUR_CARD% > NUM_CARDS% THEN GOTO 1310
1270 PRINT EQU$ \ PRINT "  [Card #"; CUR_CARD%; " of "; NUM_CARDS%; "] Index: "; CD_INDEX$(CUR_CARD%) \ PRINT SEP$
1280 PRINT "  Category:     "; CD_CAT$(CUR_CARD%)
1290 PRINT "  DECnet/Phone: "; CD_NODE$(CUR_CARD%)
1300 PRINT "  Notes:        "; CD_BODY$(CUR_CARD%) \ PRINT EQU$ \ GOTO 495
1310 PRINT "CARDFILER: Card '"; ARGS$; "' not found in deck." \ GOTO 495
1330 IF NUM_CARDS% = 0% THEN GOTO 3370
1340 IF CUR_CARD% >= NUM_CARDS% THEN GOTO 1380
1350 CUR_CARD% = CUR_CARD% + 1% \ ARGS$ = "" \ GOTO 1260
1380 PRINT "CARDFILER: Already at end of card deck (#"; NUM_CARDS%; ")." \ GOTO 495
1400 IF NUM_CARDS% = 0% THEN GOTO 3370
1410 IF CUR_CARD% <= 1% THEN GOTO 1450
1420 CUR_CARD% = CUR_CARD% - 1% \ ARGS$ = "" \ GOTO 1260
1450 PRINT "CARDFILER: Already at top of card deck (#1)." \ GOTO 495
1470 IF NUM_CARDS% >= 40% THEN GOTO 1580
1480 P_IN$ = ARGS$ \ GOSUB 650
1490 IF NF% < 4% THEN GOTO 1570
1500 N_IX$ = FLD$(1%) \ U_IN$ = FLD$(2%) \ GOSUB 580 \ N_CT$ = U_OUT$
1510 N_ND$ = FLD$(3%) \ N_BD$ = FLD$(4%)
1520 NUM_CARDS% = NUM_CARDS% + 1% \ CD_INDEX$(NUM_CARDS%) = N_IX$ \ CD_CAT$(NUM_CARDS%) = N_CT$
1530 CD_NODE$(NUM_CARDS%) = N_ND$ \ CD_BODY$(NUM_CARDS%) = N_BD$ \ CUR_CARD% = NUM_CARDS%
1540 PRINT "[Added Card #"; NUM_CARDS%; ": "; N_IX$; " ("; N_CT$; ")]" \ GOTO 495
1570 PRINT "CARDFILER: Syntax is ADD <index_header|category|node_or_phone|body_notes>" \ GOTO 495
1580 PRINT "CARDFILER: Card deck is full (maximum 40 cards)." \ GOTO 495
1600 IF NUM_CARDS% = 0% THEN GOTO 3370
1610 P_IN$ = ARGS$ \ GOSUB 650
1620 IF NF% < 5% THEN GOTO 1710
1630 U_ID% = VAL(FLD$(1%))
1640 IF U_ID% < 1% OR U_ID% > NUM_CARDS% THEN GOTO 3380
1650 CD_INDEX$(U_ID%) = FLD$(2%) \ U_IN$ = FLD$(3%) \ GOSUB 580 \ CD_CAT$(U_ID%) = U_OUT$
1660 CD_NODE$(U_ID%) = FLD$(4%) \ CD_BODY$(U_ID%) = FLD$(5%) \ CUR_CARD% = U_ID%
1670 PRINT "[Updated Card #"; U_ID%; ": "; CD_INDEX$(U_ID%); "]" \ GOTO 495
1710 PRINT "CARDFILER: Syntax is UPDATE <id|index_header|category|node_or_phone|body_notes>" \ GOTO 495
1740 IF NUM_CARDS% = 0% THEN GOTO 3370
1750 IF NUM_CARDS% >= 40% THEN GOTO 1580
1760 CP_ID% = CUR_CARD%
1770 IF ARGS$ <> "" THEN CP_ID% = VAL(ARGS$)
1780 IF CP_ID% < 1% OR CP_ID% > NUM_CARDS% THEN GOTO 3380
1790 NUM_CARDS% = NUM_CARDS% + 1% \ CD_INDEX$(NUM_CARDS%) = CD_INDEX$(CP_ID%) + " (Copy)"
1800 CD_CAT$(NUM_CARDS%) = CD_CAT$(CP_ID%) \ CD_NODE$(NUM_CARDS%) = CD_NODE$(CP_ID%)
1810 CD_BODY$(NUM_CARDS%) = CD_BODY$(CP_ID%) \ CUR_CARD% = NUM_CARDS%
1820 PRINT "[Duplicated Card #"; CP_ID%; " -> Card #"; NUM_CARDS%; ": "; CD_INDEX$(NUM_CARDS%); "]" \ GOTO 495
1860 IF NUM_CARDS% = 0% THEN GOTO 3370
1870 D_ID% = VAL(ARGS$)
1880 IF D_ID% < 1% OR D_ID% > NUM_CARDS% THEN GOTO 3380
1890 D_IX$ = CD_INDEX$(D_ID%) \ DI% = D_ID%
1900 IF DI% >= NUM_CARDS% THEN GOTO 1940
1910 CD_INDEX$(DI%) = CD_INDEX$(DI% + 1%) \ CD_CAT$(DI%) = CD_CAT$(DI% + 1%)
1920 CD_NODE$(DI%) = CD_NODE$(DI% + 1%) \ CD_BODY$(DI%) = CD_BODY$(DI% + 1%) \ DI% = DI% + 1% \ GOTO 1900
1940 NUM_CARDS% = NUM_CARDS% - 1%
1950 IF CUR_CARD% > NUM_CARDS% THEN CUR_CARD% = NUM_CARDS%
1960 PRINT "[Deleted Card #"; D_ID%; ": "; D_IX$; "]" \ GOTO 495
1980 IF NUM_CARDS% = 0% THEN GOTO 3370
1990 U_IN$ = ARGS$ \ GOSUB 580 \ S_BY$ = U_OUT$
2000 IF S_BY$ = "" THEN S_BY$ = "INDEX"
2010 IF S_BY$ <> "INDEX" AND S_BY$ <> "CATEGORY" THEN GOTO 2170
2020 SI% = 1%
2030 IF SI% >= NUM_CARDS% THEN GOTO 2150
2040 SJ% = SI% + 1%
2050 IF SJ% > NUM_CARDS% THEN GOTO 2130
2060 K1$ = CD_INDEX$(SI%) \ K2$ = CD_INDEX$(SJ%)
2070 IF S_BY$ = "CATEGORY" THEN K1$ = CD_CAT$(SI%)
2075 IF S_BY$ = "CATEGORY" THEN K2$ = CD_CAT$(SJ%)
2080 IF K1$ <= K2$ THEN GOTO 2120
2090 T_IX$ = CD_INDEX$(SI%) \ CD_INDEX$(SI%) = CD_INDEX$(SJ%) \ CD_INDEX$(SJ%) = T_IX$
2100 T_CT$ = CD_CAT$(SI%) \ CD_CAT$(SI%) = CD_CAT$(SJ%) \ CD_CAT$(SJ%) = T_CT$
2110 T_ND$ = CD_NODE$(SI%) \ CD_NODE$(SI%) = CD_NODE$(SJ%) \ CD_NODE$(SJ%) = T_ND$
2115 T_BD$ = CD_BODY$(SI%) \ CD_BODY$(SI%) = CD_BODY$(SJ%) \ CD_BODY$(SJ%) = T_BD$
2120 SJ% = SJ% + 1% \ GOTO 2050
2130 SI% = SI% + 1% \ GOTO 2030
2150 CUR_CARD% = 1% \ PRINT "[Sorted "; NUM_CARDS%; " index cards alphabetically by "; S_BY$; "]" \ GOTO 495
2170 PRINT "CARDFILER: Syntax is SORT INDEX or SORT CATEGORY" \ GOTO 495
2200 IF NUM_CARDS% = 0% THEN GOTO 3370
2210 IF ARGS$ = "" THEN GOTO 2340
2220 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ KW$ = U_OUT$
2230 PRINT EQU$ \ PRINT "  DECwindows Cardfiler Search Results for '"; Q_OUT$; "'" \ PRINT SEP$
2240 S_HIT% = 0% \ CI% = 1%
2250 IF CI% > NUM_CARDS% THEN GOTO 2320
2260 H1$ = CD_INDEX$(CI%) + " " + CD_CAT$(CI%)
2265 H2$ = H1$ + " " + CD_NODE$(CI%)
2270 U_IN$ = H2$ + " " + CD_BODY$(CI%) \ GOSUB 580 \ HAY$ = U_OUT$
2280 IF INSTR(1%, HAY$, KW$) = 0% THEN GOTO 2310
2290 S_HIT% = S_HIT% + 1%
2300 PRINT "  [Match #"; S_HIT%; "] Card #"; CI%; " ["; CD_INDEX$(CI%); " | "; CD_CAT$(CI%); "] "; CD_NODE$(CI%)
2310 CI% = CI% + 1% \ GOTO 2250
2320 PRINT SEP$ \ PRINT "  Total matching cards: "; S_HIT% \ PRINT EQU$ \ GOTO 495
2340 PRINT "CARDFILER: Syntax is SEARCH <keyword>" \ GOTO 495
2380 IF NUM_CARDS% = 0% THEN GOTO 3370
2390 TO_FILE% = 0% \ OUT_FILE$ = ""
2400 IF ARGS$ = "" THEN GOTO 2460
2410 U_IN$ = ARGS$ \ GOSUB 580 \ U_ARGS$ = U_OUT$
2420 IF LEFT$(U_ARGS$, 3%) <> "ON " THEN GOTO 2450
2430 T_IN$ = MID$(ARGS$, 4%, LEN(ARGS$) - 3%) \ GOSUB 500 \ Q_IN$ = T_OUT$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1% \ GOTO 2460
2450 Q_IN$ = ARGS$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1%
2460 IF TO_FILE% = 1% THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2470 BDR$ = "+------------------------------------------------------------------------------+" \ SP1$ = " "
2480 T_BAR$ = VBAR$ + " [=] DECwindows Cardfiler - " + DECK_FILE$ + BLANKS$
2490 T_BAR$ = LEFT$(T_BAR$, 72%) + " [v][^]" + VBAR$
2500 M_BAR$ = VBAR$ + "  File    Edit    Card    View    Search    Help                              " + VBAR$
2510 C_S$ = STR$(CUR_CARD%) \ T_IN$ = C_S$ \ GOSUB 500 \ C_STR$ = T_OUT$
2520 N_S$ = STR$(NUM_CARDS%) \ T_IN$ = N_S$ \ GOSUB 500 \ N_STR$ = T_OUT$
2530 IX_LN$ = " Index Tab: " + CD_INDEX$(CUR_CARD%)
2535 IX_LN$ = IX_LN$ + "   [Card " + C_STR$
2540 IX_LN$ = IX_LN$ + " of " + N_STR$ + RBRK$
2550 IX_ROW$ = LEFT$(VBAR$ + IX_LN$ + BLANKS$, 79%) + VBAR$
2560 CT_LN$ = " Category:  " + CD_CAT$(CUR_CARD%)
2565 CT_LN$ = CT_LN$ + "   Node/Phone: " + CD_NODE$(CUR_CARD%)
2570 CT_ROW$ = LEFT$(VBAR$ + CT_LN$ + BLANKS$, 79%) + VBAR$
2580 BD_ROW$ = LEFT$(VBAR$ + "   " + CD_BODY$(CUR_CARD%) + BLANKS$, 79%) + VBAR$
2590 F_INF$ = " [<< Prev Card]  [Next Card >>]  [Deck: " + DECK_TITLE$ + RBRK$
2600 F_ROW$ = LEFT$(VBAR$ + F_INF$ + BLANKS$, 79%) + VBAR$
2610 IF TO_FILE% = 1% THEN GOTO 2650
2620 PRINT BDR$ \ PRINT T_BAR$ \ PRINT BDR$ \ PRINT M_BAR$ \ PRINT BDR$
2630 PRINT IX_ROW$ \ PRINT BDR$ \ PRINT CT_ROW$ \ PRINT BD_ROW$ \ PRINT BDR$ \ PRINT F_ROW$ \ PRINT BDR$ \ GOTO 2700
2650 PRINT #2%, BDR$ \ PRINT #2%, T_BAR$ \ PRINT #2%, BDR$ \ PRINT #2%, M_BAR$ \ PRINT #2%, BDR$
2660 PRINT #2%, IX_ROW$ \ PRINT #2%, BDR$ \ PRINT #2%, CT_ROW$ \ PRINT #2%, BD_ROW$ \ PRINT #2%, BDR$ \ PRINT #2%, F_ROW$ \ PRINT #2%, BDR$ \ CLOSE #2%
2670 PRINT "[Cardfiler window exported to "; OUT_FILE$; "]"
2700 GOTO 495
2780 PRINT EQU$ \ PRINT "  DECwindows Cardfiler V3.0 - Rotary Deck & Card Status" \ PRINT SEP$
2790 PRINT "  Deck Title:             "; DECK_TITLE$
2800 PRINT "  Card File (.CRD):       "; DECK_FILE$
2810 PRINT "  Total Cards in Deck:    "; NUM_CARDS%; " / 40 cards"
2820 IF CUR_CARD% > 0% THEN PRINT "  Active Selected Card:   #"; CUR_CARD%; " - "; CD_INDEX$(CUR_CARD%); " ("; CD_CAT$(CUR_CARD%); ")"
2830 PRINT EQU$ \ GOTO 495
2900 IF NUM_CARDS% = 0% THEN GOTO 3370
2910 IF ARGS$ = "" THEN GOTO 2920
2915 Q_IN$ = ARGS$ \ GOSUB 635 \ DECK_FILE$ = Q_OUT$
2920 OPEN DECK_FILE$ FOR OUTPUT AS FILE #1%
2930 CI% = 1%
2940 IF CI% > NUM_CARDS% THEN GOTO 2980
2950 C_REC$ = CD_INDEX$(CI%) + PIPE$ + CD_CAT$(CI%) + PIPE$ + CD_NODE$(CI%) + PIPE$ + CD_BODY$(CI%)
2960 PRINT #1%, C_REC$ \ CI% = CI% + 1% \ GOTO 2940
2980 CLOSE #1% \ PRINT "[Saved "; NUM_CARDS%; " card(s) to "; DECK_FILE$; "]" \ GOTO 495
3010 IF ARGS$ = "" THEN GOTO 3140
3020 Q_IN$ = ARGS$ \ GOSUB 635 \ DECK_FILE$ = Q_OUT$
3030 NUM_CARDS% = 0% \ OPEN DECK_FILE$ FOR INPUT AS FILE #1%
3040 IF NUM_CARDS% >= 40% THEN GOTO 3110
3050 LINE INPUT #1%, IN_L$
3060 IF LEN(IN_L$) = 0% THEN GOTO 3110
3065 IF ASCII(LEFT$(IN_L$, 1%)) = 0% THEN GOTO 3110
3070 P_IN$ = IN_L$ \ GOSUB 650
3075 IF NF% < 4% THEN GOTO 3110
3080 NUM_CARDS% = NUM_CARDS% + 1% \ CD_INDEX$(NUM_CARDS%) = FLD$(1%) \ CD_CAT$(NUM_CARDS%) = FLD$(2%)
3090 CD_NODE$(NUM_CARDS%) = FLD$(3%) \ CD_BODY$(NUM_CARDS%) = FLD$(4%) \ GOTO 3040
3110 CLOSE #1%
3120 IF NUM_CARDS% > 0% THEN CUR_CARD% = 1%
3130 PRINT "[Loaded "; NUM_CARDS%; " card(s) from "; DECK_FILE$; "]" \ GOTO 495
3140 PRINT "CARDFILER: Syntax is LOAD <filename>" \ GOTO 495
3180 NUM_CARDS% = 0% \ CUR_CARD% = 0%
3190 PRINT "[Cardfiler deck cleared]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "  DECwindows Cardfiler Rotary Index Card Manager Commands" \ PRINT SEP$
3230 PRINT "  SAMPLE                   Load sample DEC Engineering & Node Directory deck"
3240 PRINT "  LIST [category]          List all index cards in deck (or filter by category)"
3250 PRINT "  READ <id_or_index>       Display full 3x5 index card by # or header"
3260 PRINT "  NEXT / PREV              Flip forward or backward through rotary deck"
3270 PRINT "  ADD <idx|cat|node|body>  Add a new index card to the deck"
3280 PRINT "  UPDATE <id|idx|cat|n|b>  Modify an existing index card"
3290 PRINT "  DUP [id] / COPY [id]     Duplicate an index card"
3300 PRINT "  DELETE <id>              Remove card #<id> from the deck"
3310 PRINT "  SORT [INDEX|CATEGORY]    Sort card deck alphabetically by index or category"
3320 PRINT "  SEARCH <keyword>         Full-text search across all card fields"
3330 PRINT "  DISPLAY [ON <file>]      Render Motif/XUI Cardfiler window (or export)"
3340 PRINT "  SHOW / SAVE <f> / LOAD <f> / CLEAR / EXIT" \ PRINT EQU$ \ GOTO 495
3370 PRINT "CARDFILER: Card deck is empty. Use SAMPLE, ADD, or LOAD first." \ GOTO 495
3380 PRINT "CARDFILER: Invalid card number." \ GOTO 495
3392 IF NUM_CARDS% = 0% THEN GOSUB 750
3393 ARGS$ = "/tmp/decw_cardfiler.dat" \ GOSUB 2900
3394 VERB$ = "EXPORT" \ ARGS$ = "/tmp/decw_cardfiler.txt" \ GOSUB 2380
3395 X_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app cardfiler --frame /tmp/decw_cardfiler.txt"
3396 X_RC% = SYS(X_CMD$) \ GOTO 495
3400 END
