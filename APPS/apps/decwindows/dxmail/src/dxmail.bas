10 REM =========================================================================
20 REM DECwindows Mail V3.0 (DECW$MAIL / dxmail / decwinmail)
30 REM XUI / Motif Graphical Mail Cabinet, Drawer/Folder Manager & DDIF Viewer
40 REM Digital Equipment Corporation - VAX/VMS, ULTRIX & DEC OSF/1 (1988-1993)
50 REM =========================================================================
60 DIM MSG_ID%(60%) \ DIM MSG_DRW$(60%) \ DIM MSG_FLD$(60%) \ DIM MSG_FROM$(60%)
70 DIM MSG_TO$(60%) \ DIM MSG_DATE$(60%) \ DIM MSG_SUBJ$(60%) \ DIM MSG_FMT$(60%)
80 DIM MSG_STAT$(60%) \ DIM MSG_BODY$(60%) \ DIM CMD_Q$(30%) \ DIM FLD_P$(15%)
90 PIPE$ = "|" \ COLON$ = ":" \ LBRK$ = "[" \ RBRK$ = "]" \ SP1$ = " " \ STAR$ = "*"
100 MSG_CNT% = 0% \ CUR_MSG% = 0% \ CUR_DRW$ = "MAIN" \ CUR_FLD$ = "INBOX"
110 CAB_NAME$ = "SYS$LOGIN:DECW$MAIL.DAT" \ USER_ADDR$ = "ZKO::SYSTEM"
120 PRT_CH% = 0% \ BANNER_SHOWN% = 0% \ FORCE_CLI% = 0%
122 C_STR$ = COMMAND$ \ GOSUB 3520 \ CMD_LINE$ = C_STR$
124 IF LEFT$(CMD_LINE$, 5%) = "--cli" THEN FORCE_CLI% = 1%
126 IF FORCE_CLI% = 1% THEN C_STR$ = MID$(CMD_LINE$, 6%, LEN(CMD_LINE$) - 5%)
128 IF FORCE_CLI% = 1% THEN GOSUB 3520
130 IF FORCE_CLI% = 1% THEN CMD_LINE$ = C_STR$
132 IF CMD_LINE$ = "--x11" OR CMD_LINE$ = "-gui" THEN CMD_LINE$ = "SAMPLE; X11; EXIT"
134 IF_X11% = 1% \ CHK_X11$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --check-gui"
136 IF CMD_LINE$ = "" AND FORCE_CLI% = 0% THEN IF_X11% = SYS(CHK_X11$)
138 IF IF_X11% = 0% THEN CMD_LINE$ = "SAMPLE; X11; EXIT"
140 IF LEN(CMD_LINE$) > 0% THEN GOTO 240
150 PRINT "=============================================================================="
160 PRINT " DECwindows Mail V3.0 (DECW$MAIL - XUI/Motif Mail Cabinet & DDIF Viewer)"
170 PRINT " Digital Equipment Corporation - VAX/VMS & DEC OSF/1 Workstation Desktop"
180 PRINT "=============================================================================="
190 PRINT "Type HELP for commands, SAMPLE to load 1991 ZKO mail cabinet, EXIT to quit."
200 BANNER_SHOWN% = 1%
210 PRINT ""
220 LINE INPUT "DXmail> "; RAW_LINE$
230 IF LEN(RAW_LINE$) = 0% THEN GOTO 210
240 IF BANNER_SHOWN% = 0% THEN RAW_LINE$ = CMD_LINE$
250 GOSUB 3310 \ Q_IDX% = 1%
270 IF Q_IDX% > Q_CNT% THEN GOTO 320
280 ONE_CMD$ = CMD_Q$( Q_IDX% ) \ GOSUB 350 \ Q_IDX% = Q_IDX% + 1% \ GOTO 270
320 IF BANNER_SHOWN% = 0% THEN GOTO 4500
330 GOTO 210
350 C_STR$ = ONE_CMD$ \ GOSUB 3520
370 IF LEN(C_STR$) = 0% THEN GOTO 1040
380 SP_POS% = INSTR(1%, C_STR$, " ")
390 IF SP_POS% = 0% THEN VERB$ = C_STR$
400 IF SP_POS% = 0% THEN ARG$ = ""
410 IF SP_POS% > 0% THEN VERB$ = LEFT$(C_STR$, SP_POS% - 1%)
420 IF SP_POS% > 0% THEN ARG$ = MID$(C_STR$, SP_POS% + 1%, LEN(C_STR$))
430 U_IN$ = VERB$ \ GOSUB 3620 \ VERB$ = U_OUT$
440 C_STR$ = ARG$ \ GOSUB 3520 \ ARG$ = C_STR$
450 U_IN$ = ARG$ \ GOSUB 3620 \ UARG$ = U_OUT$
460 IF VERB$ = "EXIT" OR VERB$ = "QUIT" THEN GOTO 4500
470 IF VERB$ = "HELP" THEN GOTO 1050
480 IF VERB$ = "SAMPLE" THEN GOTO 1270
490 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1510
500 IF VERB$ = "CABINET" OR VERB$ = "DRAWERS" OR VERB$ = "FOLDERS" THEN GOTO 1640
510 IF VERB$ = "SELECT" OR VERB$ = "FOLDER" OR VERB$ = "OPEN" THEN GOTO 1820
520 IF VERB$ = "DIR" OR VERB$ = "LIST" OR VERB$ = "HEADERS" THEN GOTO 1970
530 IF VERB$ = "READ" OR VERB$ = "VIEW" THEN GOTO 2170
540 IF VERB$ = "NEXT" THEN GOTO 2340
550 IF VERB$ = "PREV" THEN GOTO 2400
560 IF VERB$ = "SEND" OR VERB$ = "COMPOSE" THEN GOTO 2460
570 IF VERB$ = "REPLY" THEN GOTO 2640
580 IF VERB$ = "FORWARD" THEN GOTO 2790
590 IF VERB$ = "MOVE" OR VERB$ = "FILE" THEN GOTO 2950
600 IF VERB$ = "MARK" THEN GOTO 3100
610 IF VERB$ = "UNMARK" THEN GOTO 3170
620 IF VERB$ = "DELETE" THEN GOTO 3240
630 IF VERB$ = "PURGE" OR VERB$ = "EMPTY" THEN GOTO 3700
640 IF VERB$ = "SEARCH" OR VERB$ = "FIND" OR VERB$ = "PICK" THEN GOTO 3850
650 IF VERB$ = "EXTRACT" THEN GOTO 4010
660 IF VERB$ = "DISPLAY" OR VERB$ = "RENDER" THEN GOTO 4130
670 IF VERB$ = "EXPORT" THEN GOTO 4150
680 IF VERB$ = "PRINT" THEN GOTO 4120
690 IF VERB$ = "SAVE" THEN GOTO 4320
700 IF VERB$ = "LOAD" THEN GOTO 4400
710 IF VERB$ = "CLEAR" THEN GOTO 1230
715 IF VERB$ = "X11" OR VERB$ = "GUI" OR VERB$ = "XDISPLAY" THEN GOTO 4496
720 PRINT "%DXMAIL-E-INVCMD, unrecognized command: "; VERB$
1040 RETURN
1050 PRINT "--- DECwindows Mail V3.0 (DECW$MAIL) Commands ---"
1070 PRINT "  SAMPLE                        Load 1991 ZKO Mail Cabinet (MAIN & PROJECTS drawers)"
1080 PRINT "  CABINET / DRAWERS / FOLDERS   Show hierarchical Mail Cabinet drawer/folder counts"
1090 PRINT "  SELECT <folder>               Open folder (INBOX, READ, SENT, ALPHA_OSF1, ALL)"
1100 PRINT "  DIR / LIST / HEADERS          List message headers in active folder"
1110 PRINT "  READ <n> / NEXT / PREV        Read message #n (supports TEXT & DDIF formats)"
1120 PRINT "  SEND <to>|<subj>|<fmt>|<body> Compose & send message (FMT: TEXT or DDIF)"
1130 PRINT "  REPLY <n>|<body>              Reply to message #n (RE: <subject>)"
1140 PRINT "  FORWARD <n>|<to>|<note>       Forward message #n to recipient"
1150 PRINT "  MOVE <n> [drawer:]<folder>    File message #n into target drawer/folder"
1160 PRINT "  MARK <n> / UNMARK <n>         Flag or unflag message #n"
1170 PRINT "  DELETE <n> / PURGE            Move #n to WASTEBASKET / Empty WASTEBASKET"
1180 PRINT "  SEARCH <keyword>              Search From, To, Subject, and Body"
1190 PRINT "  EXTRACT <n> <file>            Export message #n to text file"
1200 PRINT "  DISPLAY / PRINT ON <file>     Render Motif/XUI DECwindows Mail cabinet window"
1210 PRINT "  SAVE <file> / LOAD <file>     Save or load Mail Cabinet (.dxm)"
1220 PRINT "  SHOW / CLEAR / HELP / EXIT    Cabinet status, reset, help, quit"
1225 RETURN
1230 MSG_CNT% = 0% \ CUR_MSG% = 0% \ CUR_DRW$ = "MAIN" \ CUR_FLD$ = "INBOX"
1250 PRINT "%DXMAIL-I-CLEARED, Mail cabinet cleared."
1260 RETURN
1270 MSG_CNT% = 6% \ CUR_MSG% = 1% \ CUR_DRW$ = "MAIN" \ CUR_FLD$ = "INBOX"
1290 CAB_NAME$ = "SYS$LOGIN:DECW$MAIL.DAT"
1300 MSG_ID%(1%) = 1% \ MSG_DRW$(1%) = "MAIN" \ MSG_FLD$(1%) = "INBOX"
1310 MSG_FROM$(1%) = "ZKO::CUTLER" \ MSG_TO$(1%) = "ZKO::SYSTEM" \ MSG_DATE$(1%) = "19-OCT-1991 08:30"
1320 MSG_SUBJ$(1%) = "MICA & Prism Kernel Review Notes" \ MSG_FMT$(1%) = "TEXT" \ MSG_STAT$(1%) = "UNREAD"
1330 MSG_BODY$(1%) = "Please review the scheduler spinlock latency benchmarks before 14:00."
1340 MSG_ID%(2%) = 2% \ MSG_DRW$(2%) = "MAIN" \ MSG_FLD$(2%) = "INBOX"
1350 MSG_FROM$(2%) = "ZKO::CONKLIN" \ MSG_TO$(2%) = "ZKO::ALL_ENG" \ MSG_DATE$(2%) = "19-OCT-1991 09:15"
1360 MSG_SUBJ$(2%) = "DEC OSF/1 V1.0 Alpha AXP Boot Milestone" \ MSG_FMT$(2%) = "DDIF" \ MSG_STAT$(2%) = "UNREAD"
1370 MSG_BODY$(2%) = "[CDA/DDIF V1.2] Alpha EV4 21064 booted multi-user OSF/1 in ZKO Lab 3."
1380 MSG_ID%(3%) = 3% \ MSG_DRW$(3%) = "MAIN" \ MSG_FLD$(3%) = "INBOX"
1390 MSG_FROM$(3%) = "SRC::LAMPORT" \ MSG_TO$(3%) = "ZKO::SYSTEM" \ MSG_DATE$(3%) = "19-OCT-1991 10:05"
1400 MSG_SUBJ$(3%) = "Part-Time Parliament Consensus Draft" \ MSG_FMT$(3%) = "DDIF" \ MSG_STAT$(3%) = "MARKED"
1410 MSG_BODY$(3%) = "[CDA/DDIF V1.2] Attached is the Paxos synod fault-tolerant protocol proof."
1420 MSG_ID%(4%) = 4% \ MSG_DRW$(4%) = "MAIN" \ MSG_FLD$(4%) = "READ"
1430 MSG_FROM$(4%) = "MLO::OLSEN" \ MSG_TO$(4%) = "ALL::DEC" \ MSG_DATE$(4%) = "18-OCT-1991 16:00"
1440 MSG_SUBJ$(4%) = "DECworld 92 Boston Planning" \ MSG_FMT$(4%) = "TEXT" \ MSG_STAT$(4%) = "READ"
1450 MSG_BODY$(4%) = "All workstation groups will demonstrate DECwindows Motif 1.1 live."
1460 MSG_ID%(5%) = 5% \ MSG_DRW$(5%) = "MAIN" \ MSG_FLD$(5%) = "SENT"
1470 MSG_FROM$(5%) = "ZKO::SYSTEM" \ MSG_TO$(5%) = "ZKO::CUTLER" \ MSG_DATE$(5%) = "18-OCT-1991 17:20"
1480 MSG_SUBJ$(5%) = "RE: Lab 3 VAX 9000 Cluster Allocation" \ MSG_FMT$(5%) = "TEXT" \ MSG_STAT$(5%) = "READ"
1490 MSG_BODY$(5%) = "CI star coupler channels 2 and 3 are reserved for overnight stress tests."
1500 MSG_ID%(6%) = 6% \ MSG_DRW$(6%) = "PROJECTS" \ MSG_FLD$(6%) = "ALPHA_OSF1"
1502 MSG_FROM$(6%) = "REO::WULF" \ MSG_TO$(6%) = "ZKO::CONKLIN" \ MSG_DATE$(6%) = "17-OCT-1991 11:45"
1504 MSG_SUBJ$(6%) = "GEM Optimizing Backend PALcode Hooks" \ MSG_FMT$(6%) = "TEXT" \ MSG_STAT$(6%) = "READ"
1506 MSG_BODY$(6%) = "Unaligned quadword trap handlers verified on EV4 simulator."
1508 PRINT "%DXMAIL-I-SAMPLE, loaded 6 messages into DECwindows Mail Cabinet (MAIN & PROJECTS)."
1509 RETURN
1510 UNR_CNT% = 0% \ DEL_CNT% = 0% \ SI% = 1%
1530 IF SI% > MSG_CNT% THEN GOTO 1580
1540 IF MSG_STAT$(SI%) = "UNREAD" THEN UNR_CNT% = UNR_CNT% + 1%
1550 IF MSG_FLD$(SI%) = "WASTEBASKET" THEN DEL_CNT% = DEL_CNT% + 1%
1560 SI% = SI% + 1% \ GOTO 1530
1580 PRINT "--- DECwindows Mail Cabinet Status ---"
1590 PRINT "  Cabinet File  : "; CAB_NAME$; "   User Address: "; USER_ADDR$
1600 PRINT "  Active Drawer : "; CUR_DRW$; "   Active Folder: "; CUR_FLD$
1610 PRINT "  Total Messages: "; MSG_CNT%; " (Unread: "; UNR_CNT%; ", Wastebasket: "; DEL_CNT%; ")"
1620 PRINT "  Current Msg # : "; CUR_MSG%
1630 RETURN
1640 PRINT "=== DECwindows Mail Cabinet Hierarchy ("; CAB_NAME$; ") ==="
1660 PRINT "  Drawer       Folder          Total   Unread   Description"
1670 PRINT "  ----------------------------------------------------------------------"
1680 CHK_D$ = "MAIN" \ CHK_F$ = "INBOX" \ CHK_DESC$ = "New & incoming electronic mail" \ GOSUB 1760
1690 CHK_D$ = "MAIN" \ CHK_F$ = "READ" \ CHK_DESC$ = "Reviewed correspondence archive" \ GOSUB 1760
1700 CHK_D$ = "MAIN" \ CHK_F$ = "SENT" \ CHK_DESC$ = "Outbound transmitted messages" \ GOSUB 1760
1710 CHK_D$ = "MAIN" \ CHK_F$ = "DRAFTS" \ CHK_DESC$ = "Unfinished composition drafts" \ GOSUB 1760
1720 CHK_D$ = "MAIN" \ CHK_F$ = "WASTEBASKET" \ CHK_DESC$ = "Deleted messages pending purge" \ GOSUB 1760
1730 CHK_D$ = "PROJECTS" \ CHK_F$ = "ALPHA_OSF1" \ CHK_DESC$ = "Alpha AXP & DEC OSF/1 engineering" \ GOSUB 1760
1740 PRINT "  ----------------------------------------------------------------------"
1750 RETURN
1760 FC_TOT% = 0% \ FC_UNR% = 0% \ FI% = 1%
1770 IF FI% > MSG_CNT% THEN GOTO 1810
1780 IF MSG_DRW$(FI%) = CHK_D$ AND MSG_FLD$(FI%) = CHK_F$ THEN FC_TOT% = FC_TOT% + 1%
1790 IF MSG_DRW$(FI%) = CHK_D$ AND MSG_FLD$(FI%) = CHK_F$ AND MSG_STAT$(FI%) = "UNREAD" THEN FC_UNR% = FC_UNR% + 1%
1800 FI% = FI% + 1% \ GOTO 1770
1810 PAD15$ = "               " \ T_S$ = CHK_D$ + PAD15$ \ D_COL$ = LEFT$(T_S$, 12%) \ T_S$ = CHK_F$ + PAD15$ \ F_COL$ = LEFT$(T_S$, 15%)
1812 PRINT "  "; D_COL$; " "; F_COL$; " "; FC_TOT%; "      "; FC_UNR%; "      "; CHK_DESC$
1815 RETURN
1820 IF LEN(UARG$) = 0% THEN PRINT "%DXMAIL-E-NOFLD, specify folder (INBOX, READ, SENT, ALPHA_OSF1, WASTEBASKET, ALL)"
1840 IF LEN(UARG$) = 0% THEN GOTO 1960
1850 COL_P% = INSTR(1%, UARG$, ":")
1860 IF COL_P% > 0% THEN CUR_DRW$ = LEFT$(UARG$, COL_P% - 1%)
1870 IF COL_P% > 0% THEN CUR_FLD$ = MID$(UARG$, COL_P% + 1%, LEN(UARG$))
1880 IF COL_P% = 0% THEN CUR_FLD$ = UARG$
1890 IF CUR_FLD$ = "ALPHA_OSF1" THEN CUR_DRW$ = "PROJECTS"
1900 IF CUR_FLD$ = "INBOX" OR CUR_FLD$ = "READ" OR CUR_FLD$ = "SENT" THEN CUR_DRW$ = "MAIN"
1910 IF CUR_FLD$ = "DRAFTS" OR CUR_FLD$ = "WASTEBASKET" OR CUR_FLD$ = "ALL" THEN CUR_DRW$ = "MAIN"
1920 PRINT "%DXMAIL-I-SELECTED, opened drawer "; CUR_DRW$; " folder "; CUR_FLD$; "."
1960 RETURN
1970 TARGET_FLD$ = CUR_FLD$
1990 IF LEN(UARG$) > 0% THEN TARGET_FLD$ = UARG$
2000 PRINT "=== DECwindows Mail Index [Drawer: "; CUR_DRW$; " | Folder: "; TARGET_FLD$; "] ==="
2010 PRINT "  #   St  Fmt     From            Date               Subject"
2020 PRINT "  --------------------------------------------------------------------------"
2030 FOUND_M% = 0% \ DI% = 1% \ PAD18$ = "                  "
2040 IF DI% > MSG_CNT% THEN GOTO 2140
2050 SHOW_IT% = 0%
2060 IF TARGET_FLD$ = "ALL" THEN SHOW_IT% = 1%
2070 IF MSG_FLD$(DI%) = TARGET_FLD$ THEN SHOW_IT% = 1%
2080 IF SHOW_IT% = 0% THEN GOTO 2130
2090 FOUND_M% = FOUND_M% + 1% \ ST_MK$ = "  "
2100 IF MSG_STAT$(DI%) = "UNREAD" THEN ST_MK$ = "* "
2110 IF MSG_STAT$(DI%) = "MARKED" THEN ST_MK$ = "M "
2115 IF MSG_STAT$(DI%) = "DELETED" THEN ST_MK$ = "D "
2116 T_S$ = MSG_FMT$(DI%) + PAD18$ \ FM_C$ = LEFT$(T_S$, 4%) \ T_S$ = MSG_FROM$(DI%) + PAD18$ \ FR_C$ = LEFT$(T_S$, 15%)
2118 T_S$ = MSG_DATE$(DI%) + PAD18$ \ DT_C$ = LEFT$(T_S$, 18%)
2120 PRINT " "; MSG_ID%(DI%); " "; ST_MK$; " ["; FM_C$; "]  "; FR_C$; " "; DT_C$; " "; MSG_SUBJ$(DI%)
2130 DI% = DI% + 1% \ GOTO 2040
2140 IF FOUND_M% = 0% THEN PRINT "  (No messages in folder "; TARGET_FLD$; ")"
2150 PRINT "  --------------------------------------------------------------------------"
2160 RETURN
2170 R_ID% = CUR_MSG%
2190 IF LEN(ARG$) > 0% THEN R_ID% = VAL(ARG$)
2200 IF R_ID% < 1% OR R_ID% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, message number out of range (1.."; MSG_CNT%; ")"
2210 IF R_ID% < 1% OR R_ID% > MSG_CNT% THEN GOTO 2330
2220 CUR_MSG% = R_ID%
2230 IF MSG_STAT$(R_ID%) = "UNREAD" THEN MSG_STAT$(R_ID%) = "READ"
2240 PRINT "=============================================================================="
2250 PRINT " Message #"; MSG_ID%(R_ID%); "  ["; MSG_DRW$(R_ID%); ":"; MSG_FLD$(R_ID%); "]   Status: "; MSG_STAT$(R_ID%); "   Format: "; MSG_FMT$(R_ID%)
2260 PRINT " From   : "; MSG_FROM$(R_ID%); "   To: "; MSG_TO$(R_ID%)
2270 PRINT " Date   : "; MSG_DATE$(R_ID%)
2280 PRINT " Subject: "; MSG_SUBJ$(R_ID%)
2290 PRINT "------------------------------------------------------------------------------"
2300 IF MSG_FMT$(R_ID%) = "DDIF" THEN PRINT " [CDA Viewer Embedded Stream: DDIF Compound Document Segment]"
2310 PRINT " "; MSG_BODY$(R_ID%)
2320 PRINT "=============================================================================="
2330 RETURN
2340 IF CUR_MSG% >= MSG_CNT% THEN PRINT "%DXMAIL-W-NOMORE, already at last message."
2360 IF CUR_MSG% >= MSG_CNT% THEN GOTO 2390
2370 CUR_MSG% = CUR_MSG% + 1% \ ARG$ = STR$(CUR_MSG%) \ GOSUB 2170
2390 RETURN
2400 IF CUR_MSG% <= 1% THEN PRINT "%DXMAIL-W-FIRSTMSG, already at first message."
2420 IF CUR_MSG% <= 1% THEN GOTO 2450
2430 CUR_MSG% = CUR_MSG% - 1% \ ARG$ = STR$(CUR_MSG%) \ GOSUB 2170
2450 RETURN
2460 P_LINE$ = ARG$ \ GOSUB 3410
2480 IF P_CNT% < 4% THEN PRINT "%DXMAIL-E-SYNTAX, usage: SEND <to>|<subj>|<fmt>|<body>"
2490 IF P_CNT% < 4% THEN GOTO 2630
2500 IF MSG_CNT% >= 60% THEN PRINT "%DXMAIL-E-CABFULL, cabinet full."
2510 IF MSG_CNT% >= 60% THEN GOTO 2630
2520 MSG_CNT% = MSG_CNT% + 1% \ MSG_ID%(MSG_CNT%) = MSG_CNT%
2530 MSG_DRW$(MSG_CNT%) = "MAIN" \ MSG_FLD$(MSG_CNT%) = "SENT"
2540 MSG_FROM$(MSG_CNT%) = USER_ADDR$ \ MSG_TO$(MSG_CNT%) = FLD_P$(1%)
2550 MSG_DATE$(MSG_CNT%) = "19-OCT-1991 14:30" \ MSG_SUBJ$(MSG_CNT%) = FLD_P$(2%)
2560 U_IN$ = FLD_P$(3%) \ GOSUB 3620 \ S_FMT$ = U_OUT$
2570 IF S_FMT$ <> "DDIF" AND S_FMT$ <> "PS" THEN S_FMT$ = "TEXT"
2580 MSG_FMT$(MSG_CNT%) = S_FMT$ \ MSG_STAT$(MSG_CNT%) = "READ"
2590 MSG_BODY$(MSG_CNT%) = FLD_P$(4%) \ CUR_MSG% = MSG_CNT%
2600 PRINT "%DXMAIL-I-SENT, message #"; MSG_CNT%; " ("; S_FMT$; ") sent to "; FLD_P$(1%); " and filed in MAIN:SENT."
2630 RETURN
2640 P_LINE$ = ARG$ \ GOSUB 3410
2660 IF P_CNT% < 2% THEN PRINT "%DXMAIL-E-SYNTAX, usage: REPLY <n>|<body>"
2670 IF P_CNT% < 2% THEN GOTO 2780
2680 REP_N% = VAL(FLD_P$(1%))
2690 IF REP_N% < 1% OR REP_N% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, invalid message number."
2700 IF REP_N% < 1% OR REP_N% > MSG_CNT% THEN GOTO 2780
2710 MSG_CNT% = MSG_CNT% + 1% \ MSG_ID%(MSG_CNT%) = MSG_CNT%
2720 MSG_DRW$(MSG_CNT%) = "MAIN" \ MSG_FLD$(MSG_CNT%) = "SENT"
2730 MSG_FROM$(MSG_CNT%) = USER_ADDR$ \ MSG_TO$(MSG_CNT%) = MSG_FROM$(REP_N%)
2740 MSG_DATE$(MSG_CNT%) = "19-OCT-1991 14:35" \ MSG_SUBJ$(MSG_CNT%) = "RE: " + MSG_SUBJ$(REP_N%)
2750 MSG_FMT$(MSG_CNT%) = "TEXT" \ MSG_STAT$(MSG_CNT%) = "READ"
2760 MSG_BODY$(MSG_CNT%) = FLD_P$(2%) \ CUR_MSG% = MSG_CNT%
2770 PRINT "%DXMAIL-I-REPLIED, reply #"; MSG_CNT%; " sent to "; MSG_TO$(MSG_CNT%); " ("; MSG_SUBJ$(MSG_CNT%); ")."
2780 RETURN
2790 P_LINE$ = ARG$ \ GOSUB 3410
2810 IF P_CNT% < 3% THEN PRINT "%DXMAIL-E-SYNTAX, usage: FORWARD <n>|<to>|<note>"
2820 IF P_CNT% < 3% THEN GOTO 2940
2830 FWD_N% = VAL(FLD_P$(1%))
2840 IF FWD_N% < 1% OR FWD_N% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, invalid message number."
2850 IF FWD_N% < 1% OR FWD_N% > MSG_CNT% THEN GOTO 2940
2860 MSG_CNT% = MSG_CNT% + 1% \ MSG_ID%(MSG_CNT%) = MSG_CNT%
2870 MSG_DRW$(MSG_CNT%) = "MAIN" \ MSG_FLD$(MSG_CNT%) = "SENT"
2880 MSG_FROM$(MSG_CNT%) = USER_ADDR$ \ MSG_TO$(MSG_CNT%) = FLD_P$(2%)
2890 MSG_DATE$(MSG_CNT%) = "19-OCT-1991 14:40" \ MSG_SUBJ$(MSG_CNT%) = "FWD: " + MSG_SUBJ$(FWD_N%)
2900 MSG_FMT$(MSG_CNT%) = MSG_FMT$(FWD_N%) \ MSG_STAT$(MSG_CNT%) = "READ"
2910 F_SEP$ = " // Orig: " \ MSG_BODY$(MSG_CNT%) = FLD_P$(3%) + F_SEP$ + MSG_BODY$(FWD_N%) \ CUR_MSG% = MSG_CNT%
2930 PRINT "%DXMAIL-I-FORWARDED, message #"; FWD_N%; " forwarded to "; FLD_P$(2%); " as #"; MSG_CNT%; "."
2940 RETURN
2950 SP_M% = INSTR(1%, UARG$, " ")
2970 IF SP_M% = 0% THEN PRINT "%DXMAIL-E-SYNTAX, usage: MOVE <n> [drawer:]<folder>"
2980 IF SP_M% = 0% THEN GOTO 3090
2990 MV_N% = VAL(LEFT$(UARG$, SP_M% - 1%))
3000 MV_DEST$ = MID$(UARG$, SP_M% + 1%, LEN(UARG$)) \ C_STR$ = MV_DEST$ \ GOSUB 3520 \ MV_DEST$ = C_STR$
3020 IF MV_N% < 1% OR MV_N% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, invalid message number."
3030 IF MV_N% < 1% OR MV_N% > MSG_CNT% THEN GOTO 3090
3040 C_POS% = INSTR(1%, MV_DEST$, ":")
3050 IF C_POS% > 0% THEN MSG_DRW$(MV_N%) = LEFT$(MV_DEST$, C_POS% - 1%)
3060 IF C_POS% > 0% THEN MSG_FLD$(MV_N%) = MID$(MV_DEST$, C_POS% + 1%, LEN(MV_DEST$))
3070 IF C_POS% = 0% THEN MSG_FLD$(MV_N%) = MV_DEST$
3075 IF MSG_FLD$(MV_N%) = "ALPHA_OSF1" AND C_POS% = 0% THEN MSG_DRW$(MV_N%) = "PROJECTS"
3080 PRINT "%DXMAIL-I-MOVED, message #"; MV_N%; " filed into "; MSG_DRW$(MV_N%); ":"; MSG_FLD$(MV_N%); "."
3090 RETURN
3100 MK_N% = VAL(ARG$)
3120 IF MK_N% < 1% OR MK_N% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, invalid message number."
3130 IF MK_N% < 1% OR MK_N% > MSG_CNT% THEN GOTO 3160
3140 MSG_STAT$(MK_N%) = "MARKED" \ PRINT "%DXMAIL-I-MARKED, message #"; MK_N%; " flagged as MARKED."
3160 RETURN
3170 UM_N% = VAL(ARG$)
3190 IF UM_N% < 1% OR UM_N% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, invalid message number."
3200 IF UM_N% < 1% OR UM_N% > MSG_CNT% THEN GOTO 3230
3210 MSG_STAT$(UM_N%) = "READ" \ PRINT "%DXMAIL-I-UNMARKED, message #"; UM_N%; " flag cleared (READ)."
3230 RETURN
3240 DL_N% = VAL(ARG$)
3260 IF DL_N% < 1% OR DL_N% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, invalid message number."
3270 IF DL_N% < 1% OR DL_N% > MSG_CNT% THEN GOTO 3300
3280 MSG_DRW$(DL_N%) = "MAIN" \ MSG_FLD$(DL_N%) = "WASTEBASKET" \ MSG_STAT$(DL_N%) = "DELETED"
3290 PRINT "%DXMAIL-I-DELETED, message #"; DL_N%; " moved to MAIN:WASTEBASKET."
3300 RETURN
3310 Q_CNT% = 0% \ REM_CMD$ = RAW_LINE$
3330 IF LEN(REM_CMD$) = 0% THEN GOTO 3400
3340 SEMI_P% = INSTR(1%, REM_CMD$, ";") \ Q_CNT% = Q_CNT% + 1%
3360 IF SEMI_P% = 0% THEN CMD_Q$(Q_CNT%) = REM_CMD$
3370 IF SEMI_P% = 0% THEN REM_CMD$ = ""
3380 IF SEMI_P% > 0% THEN CMD_Q$(Q_CNT%) = LEFT$(REM_CMD$, SEMI_P% - 1%)
3390 IF SEMI_P% > 0% THEN REM_CMD$ = MID$(REM_CMD$, SEMI_P% + 1%, LEN(REM_CMD$))
3395 GOTO 3330
3400 RETURN
3410 P_CNT% = 0% \ REM_P$ = P_LINE$
3430 IF LEN(REM_P$) = 0% THEN GOTO 3510
3440 PP% = INSTR(1%, REM_P$, "|") \ P_CNT% = P_CNT% + 1%
3460 IF PP% = 0% THEN FLD_P$(P_CNT%) = REM_P$
3470 IF PP% = 0% THEN REM_P$ = ""
3480 IF PP% > 0% THEN FLD_P$(P_CNT%) = LEFT$(REM_P$, PP% - 1%)
3490 IF PP% > 0% THEN REM_P$ = MID$(REM_P$, PP% + 1%, LEN(REM_P$))
3500 GOTO 3430
3510 RETURN
3520 IF LEN(C_STR$) = 0% THEN GOTO 3610
3540 IF LEFT$(C_STR$, 1%) <> " " THEN GOTO 3570
3550 C_STR$ = MID$(C_STR$, 2%, LEN(C_STR$)) \ GOTO 3520
3570 IF LEN(C_STR$) = 0% THEN GOTO 3610
3580 IF RIGHT$(C_STR$, 1%) <> " " THEN GOTO 3610
3590 C_STR$ = LEFT$(C_STR$, LEN(C_STR$) - 1%) \ GOTO 3570
3610 RETURN
3620 U_OUT$ = "" \ UI% = 1%
3640 IF UI% > LEN(U_IN$) THEN GOTO 3695
3650 CH_A% = ASCII(MID$(U_IN$, UI%, 1%))
3660 IF CH_A% >= 97% AND CH_A% <= 122% THEN CH_A% = CH_A% - 32%
3670 U_OUT$ = U_OUT$ + CHR$(CH_A%) \ UI% = UI% + 1% \ GOTO 3640
3695 RETURN
3700 NEW_CNT% = 0% \ REMOVED% = 0% \ PI% = 1%
3720 IF PI% > MSG_CNT% THEN GOTO 3810
3730 IF MSG_FLD$(PI%) = "WASTEBASKET" THEN REMOVED% = REMOVED% + 1%
3740 IF MSG_FLD$(PI%) = "WASTEBASKET" THEN GOTO 3800
3750 NEW_CNT% = NEW_CNT% + 1%
3760 MSG_ID%(NEW_CNT%) = NEW_CNT% \ MSG_DRW$(NEW_CNT%) = MSG_DRW$(PI%) \ MSG_FLD$(NEW_CNT%) = MSG_FLD$(PI%)
3770 MSG_FROM$(NEW_CNT%) = MSG_FROM$(PI%) \ MSG_TO$(NEW_CNT%) = MSG_TO$(PI%) \ MSG_DATE$(NEW_CNT%) = MSG_DATE$(PI%)
3780 MSG_SUBJ$(NEW_CNT%) = MSG_SUBJ$(PI%) \ MSG_FMT$(NEW_CNT%) = MSG_FMT$(PI%) \ MSG_STAT$(NEW_CNT%) = MSG_STAT$(PI%)
3790 MSG_BODY$(NEW_CNT%) = MSG_BODY$(PI%)
3800 PI% = PI% + 1% \ GOTO 3720
3810 MSG_CNT% = NEW_CNT%
3820 IF CUR_MSG% > MSG_CNT% THEN CUR_MSG% = MSG_CNT%
3830 PRINT "%DXMAIL-I-PURGED, permanently removed "; REMOVED%; " message(s) from WASTEBASKET."
3840 RETURN
3850 IF LEN(UARG$) = 0% THEN PRINT "%DXMAIL-E-NOKWD, specify search keyword."
3870 IF LEN(UARG$) = 0% THEN GOTO 4000
3880 PRINT "--- DECwindows Mail Search Results for '"; ARG$; "' ---"
3890 HITS% = 0% \ KI% = 1%
3900 IF KI% > MSG_CNT% THEN GOTO 3980
3910 U_IN$ = MSG_FROM$(KI%) + SP1$ + MSG_TO$(KI%) + SP1$ + MSG_SUBJ$(KI%) + SP1$ + MSG_BODY$(KI%)
3920 GOSUB 3620
3930 IF INSTR(1%, U_OUT$, UARG$) = 0% THEN GOTO 3970
3940 HITS% = HITS% + 1%
3950 PRINT "  #"; MSG_ID%(KI%); " ["; MSG_DRW$(KI%); ":"; MSG_FLD$(KI%); "] From: "; MSG_FROM$(KI%); " | Subj: "; MSG_SUBJ$(KI%)
3970 KI% = KI% + 1% \ GOTO 3900
3980 PRINT "Total matches found: "; HITS%
4000 RETURN
4010 SP_E% = INSTR(1%, ARG$, " ")
4030 IF SP_E% = 0% THEN PRINT "%DXMAIL-E-SYNTAX, usage: EXTRACT <n> <file>"
4040 IF SP_E% = 0% THEN GOTO 4115
4050 EX_N% = VAL(LEFT$(ARG$, SP_E% - 1%))
4060 EX_F$ = MID$(ARG$, SP_E% + 1%, LEN(ARG$)) \ C_STR$ = EX_F$ \ GOSUB 3520 \ EX_F$ = C_STR$
4080 IF EX_N% < 1% OR EX_N% > MSG_CNT% THEN PRINT "%DXMAIL-E-INVMSG, invalid message number."
4090 IF EX_N% < 1% OR EX_N% > MSG_CNT% THEN GOTO 4115
4100 OPEN EX_F$ FOR OUTPUT AS FILE #2%
4101 EX_L$ = "From: " + MSG_FROM$(EX_N%) \ PRINT #2%, EX_L$ \ EX_L$ = "To: " + MSG_TO$(EX_N%) \ PRINT #2%, EX_L$
4103 EX_L$ = "Date: " + MSG_DATE$(EX_N%) \ PRINT #2%, EX_L$ \ EX_L$ = "Subject: " + MSG_SUBJ$(EX_N%) \ PRINT #2%, EX_L$
4105 EX_L$ = "Format: " + MSG_FMT$(EX_N%) \ PRINT #2%, EX_L$ \ EX_L$ = "" \ PRINT #2%, EX_L$ \ EX_L$ = MSG_BODY$(EX_N%) \ PRINT #2%, EX_L$
4108 CLOSE #2%
4110 PRINT "%DXMAIL-I-EXTRACTED, message #"; EX_N%; " exported to "; EX_F$; "."
4115 RETURN
4120 IF LEFT$(UARG$, 3%) = "ON " THEN ARG$ = MID$(ARG$, 4%, LEN(ARG$))
4124 C_STR$ = ARG$ \ GOSUB 3520 \ ARG$ = C_STR$
4126 IF LEN(ARG$) > 0% THEN GOTO 4150
4130 PRT_CH% = 0% \ GOSUB 4190
4145 RETURN
4150 IF LEN(ARG$) = 0% THEN PRINT "%DXMAIL-E-NOFILE, specify output filename."
4155 IF LEN(ARG$) = 0% THEN GOTO 4185
4160 OPEN ARG$ FOR OUTPUT AS FILE #2% \ PRT_CH% = 2% \ GOSUB 4190 \ CLOSE #2% \ PRT_CH% = 0%
4180 PRINT "%DXMAIL-I-EXPORTED, DECwindows Mail window exported to "; ARG$
4185 RETURN
4190 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4200 PAD38$ = "                                      " \ T_S$ = CAB_NAME$ + PAD38$ \ W_TMP$ = LEFT$(T_S$, 38%)
4204 OUT_L$ = "| [X] DECwindows Mail: " + W_TMP$
4206 OUT_L$ = OUT_L$ + " [_][#] |" \ GOSUB 4305
4208 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4210 OUT_L$ = "| File   Edit   View   Folder   Message   Send   Customize              Help |" \ GOSUB 4305
4215 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4218 OUT_L$ = "| Active Drawer: " + CUR_DRW$
4220 OUT_L$ = OUT_L$ + "  Active Folder: " + CUR_FLD$
4222 OUT_L$ = OUT_L$ + "  Total Msgs:" + STR$(MSG_CNT%) \ GOSUB 4305
4225 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4230 OUT_L$ = "| [Read] [Send/New] [Reply] [Forward] [Move] [Delete] [Next] [Prev] [Search] |" \ GOSUB 4305
4235 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4240 WI% = 1%
4245 IF WI% > MSG_CNT% THEN GOTO 4270
4248 IF CUR_FLD$ <> "ALL" AND MSG_FLD$(WI%) <> CUR_FLD$ THEN GOTO 4265
4250 W_ROW$ = "| #" + STR$(MSG_ID%(WI%)) + SP1$ + MSG_STAT$(WI%) + SP1$ + LBRK$ + MSG_FMT$(WI%) + RBRK$ + SP1$ + MSG_FROM$(WI%) + SP1$ + MSG_SUBJ$(WI%)
4255 OUT_L$ = W_ROW$ \ GOSUB 4305
4265 WI% = WI% + 1% \ GOTO 4245
4270 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4272 IF CUR_MSG% < 1% OR CUR_MSG% > MSG_CNT% THEN GOTO 4290
4275 OUT_L$ = "| Read Pane #" + STR$(CUR_MSG%) + SP1$ + MSG_FROM$(CUR_MSG%) + COLON$ + SP1$ + MSG_SUBJ$(CUR_MSG%) \ GOSUB 4305
4280 OUT_L$ = "| " + MSG_BODY$(CUR_MSG%) \ GOSUB 4305
4290 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4300 RETURN
4305 IF PRT_CH% = 0% THEN PRINT OUT_L$
4310 IF PRT_CH% = 2% THEN PRINT #2%, OUT_L$
4315 RETURN
4320 IF LEN(ARG$) = 0% THEN PRINT "%DXMAIL-E-NOFILE, specify filename to save."
4330 IF LEN(ARG$) = 0% THEN GOTO 4395
4335 OPEN ARG$ FOR OUTPUT AS FILE #1%
4340 HDR_REC$ = "DXMAIL" + PIPE$ + CUR_DRW$ + PIPE$ + CUR_FLD$ + PIPE$ + STR$(CUR_MSG%)
4345 PRINT #1%, HDR_REC$ \ SVI% = 1%
4355 IF SVI% > MSG_CNT% THEN GOTO 4385
4360 M_REC$ = "MSG" + PIPE$ + STR$(MSG_ID%(SVI%)) + PIPE$ + MSG_DRW$(SVI%) + PIPE$ + MSG_FLD$(SVI%) + PIPE$ + MSG_FROM$(SVI%) + PIPE$ + MSG_TO$(SVI%)
4365 M_REC$ = M_REC$ + PIPE$ + MSG_DATE$(SVI%) + PIPE$ + MSG_SUBJ$(SVI%) + PIPE$ + MSG_FMT$(SVI%) + PIPE$ + MSG_STAT$(SVI%) + PIPE$ + MSG_BODY$(SVI%)
4370 PRINT #1%, M_REC$ \ SVI% = SVI% + 1% \ GOTO 4355
4385 CLOSE #1%
4390 PRINT "%DXMAIL-I-SAVED, saved "; MSG_CNT%; " messages to "; ARG$
4395 RETURN
4400 IF LEN(ARG$) = 0% THEN PRINT "%DXMAIL-E-NOFILE, specify filename to load."
4410 IF LEN(ARG$) = 0% THEN GOTO 4495
4415 MSG_CNT% = 0% \ CAB_NAME$ = ARG$
4420 OPEN ARG$ FOR INPUT AS FILE #1%
4425 LINE INPUT #1%, L_REC$
4430 IF LEN(L_REC$) = 0% THEN GOTO 4485
4435 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 4485
4440 P_LINE$ = L_REC$ \ GOSUB 3410
4445 IF FLD_P$(1%) = "DXMAIL" THEN CUR_DRW$ = FLD_P$(2%)
4450 IF FLD_P$(1%) = "DXMAIL" THEN CUR_FLD$ = FLD_P$(3%)
4455 IF FLD_P$(1%) = "DXMAIL" THEN CUR_MSG% = VAL(FLD_P$(4%))
4460 IF FLD_P$(1%) <> "MSG" THEN GOTO 4425
4465 MSG_CNT% = MSG_CNT% + 1% \ MSG_ID%(MSG_CNT%) = VAL(FLD_P$(2%)) \ MSG_DRW$(MSG_CNT%) = FLD_P$(3%) \ MSG_FLD$(MSG_CNT%) = FLD_P$(4%)
4470 MSG_FROM$(MSG_CNT%) = FLD_P$(5%) \ MSG_TO$(MSG_CNT%) = FLD_P$(6%) \ MSG_DATE$(MSG_CNT%) = FLD_P$(7%) \ MSG_SUBJ$(MSG_CNT%) = FLD_P$(8%)
4475 MSG_FMT$(MSG_CNT%) = FLD_P$(9%) \ MSG_STAT$(MSG_CNT%) = FLD_P$(10%) \ MSG_BODY$(MSG_CNT%) = FLD_P$(11%)
4480 GOTO 4425
4485 CLOSE #1%
4490 PRINT "%DXMAIL-I-LOADED, loaded "; MSG_CNT%; " messages from "; ARG$
4495 RETURN
4496 IF MSG_CNT% = 0% THEN GOSUB 1270
4497 ARG$ = "/tmp/decw_dxmail.dat" \ GOSUB 4320 \ ARG$ = "/tmp/decw_dxmail.txt" \ GOSUB 4150
4498 X_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app dxmail --frame /tmp/decw_dxmail.txt"
4499 X_RC% = SYS(X_CMD$) \ RETURN
4500 END
