10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM MN_NAME$(15%) \ DIM MN_TITLE$(15%) \ DIM MN_DATE$(15%) \ DIM MN_STAT$(15%)
20 DIM OP_MENU%(50%) \ DIM OP_KEY$(50%) \ DIM OP_DESC$(50%) \ DIM OP_TYPE$(50%) \ DIM OP_TARG$(50%) \ DIM OP_PRIV%(50%) \ DIM LG_MSG$(30%)
30 NUM_MENUS% = 0% \ CURR_MENU% = 1% \ PREV_MENU% = 1% \ NUM_OPTS% = 0% \ NUM_LOGS% = 0% \ USER_PPN$ = "[1,2]" \ USER_PRIV% = 100% \ MLB_FILE$ = "MENU11.MLB"
40 BLANKS$ = "                                                                                " \ LBRK$ = "[" \ RBRK$ = "]" \ LP$ = "(" \ RP$ = ")"
50 SEP$    = "--------------------------------------------------------------------------------"
60 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
70 IF CMD_LINE$ = "" THEN GOTO 90
80 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 180
90 PRINT EQU$ \ PRINT "    MENU-11 V2.0 - DEC Menu Control & Application Dispatch Facility (MCF)" \ PRINT "    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / RSX-11M / VAX" \ PRINT EQU$
100 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
110 PRINT "MENU> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 700
360 IF VERB$ = "DIR" OR VERB$ = "MENUS" OR VERB$ = "MLB" THEN GOTO 960
370 IF VERB$ = "SELECT" OR VERB$ = "MENU" THEN GOTO 1130
380 IF VERB$ = "BACK" OR VERB$ = "PARENT" OR VERB$ = "UP" THEN GOTO 1230
390 IF VERB$ = "CREATE" OR VERB$ = "NEWMENU" THEN GOTO 1260
400 IF VERB$ = "ADDOPT" OR VERB$ = "OPTION" THEN GOTO 1370
410 IF VERB$ = "OPTIONS" OR VERB$ = "DESCRIBE" OR VERB$ = "ITEMS" THEN GOTO 1540
420 IF VERB$ = "USER" OR VERB$ = "LOGIN" OR VERB$ = "SETPRIV" THEN GOTO 1700
430 IF VERB$ = "RUN" OR VERB$ = "EXEC" OR VERB$ = "PICK" OR VERB$ = "CHOOSE" THEN GOTO 1820
440 IF VERB$ = "LOG" OR VERB$ = "AUDIT" OR VERB$ = "HISTORY" THEN GOTO 2120
450 IF VERB$ = "DISPLAY" OR VERB$ = "RENDER" OR VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 2280
460 IF VERB$ = "DELETE" OR VERB$ = "DEL" THEN GOTO 2640
470 IF VERB$ = "PURGE" THEN GOTO 2710
480 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2880
484 IF VERB$ = "SAVE" THEN GOTO 2970
488 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3060
490 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3205
494 PRINT "MENU-11: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
650 O_CNT% = 0% \ CI% = 1%
655 IF CI% > NUM_OPTS% THEN GOTO 675
660 IF OP_MENU%(CI%) = CM_IDX% THEN O_CNT% = O_CNT% + 1%
665 CI% = CI% + 1% \ GOTO 655
675 RETURN
700 NUM_MENUS% = 4% \ CURR_MENU% = 1% \ PREV_MENU% = 1% \ NUM_OPTS% = 11% \ NUM_LOGS% = 1%
710 MN_NAME$(1%) = "MAIN_MENU" \ MN_TITLE$(1%) = "DEC RSTS/E V8.0 MASTER APPLICATION MENU" \ MN_DATE$(1%) = "26-OCT-1982" \ MN_STAT$(1%) = "A"
720 MN_NAME$(2%) = "ACCT_MENU" \ MN_TITLE$(2%) = "DIBS-11 COMMERCIAL ACCOUNTING & ERP MENU" \ MN_DATE$(2%) = "26-OCT-1982" \ MN_STAT$(2%) = "A"
730 MN_NAME$(3%) = "OFFICE_MENU" \ MN_TITLE$(3%) = "DEC ALL-IN-1 OFFICE & DECISION SUPPORT MENU" \ MN_DATE$(3%) = "27-OCT-1982" \ MN_STAT$(3%) = "A"
740 MN_NAME$(4%) = "OLD_BATCH" \ MN_TITLE$(4%) = "OBSOLETE CTS-300 CARD READER MENU" \ MN_DATE$(4%) = "01-OCT-1982" \ MN_STAT$(4%) = "D"
750 OP_MENU%(1%) = 1% \ OP_KEY$(1%) = "1" \ OP_DESC$(1%) = "Commercial Accounting & ERP" \ OP_TYPE$(1%) = "SUBMENU" \ OP_TARG$(1%) = "ACCT_MENU" \ OP_PRIV%(1%) = 10%
760 OP_MENU%(2%) = 1% \ OP_KEY$(2%) = "2" \ OP_DESC$(2%) = "Office & Decision Support" \ OP_TYPE$(2%) = "SUBMENU" \ OP_TARG$(2%) = "OFFICE_MENU" \ OP_PRIV%(2%) = 10%
770 OP_MENU%(3%) = 1% \ OP_KEY$(3%) = "3" \ OP_DESC$(3%) = "FMS-11 Screen Forms Driver" \ OP_TYPE$(3%) = "CHAIN" \ OP_TARG$(3%) = "SY:FMS11.TSK" \ OP_PRIV%(3%) = 20%
780 OP_MENU%(4%) = 1% \ OP_KEY$(4%) = "4" \ OP_DESC$(4%) = "RMS-11 File Utilities Suite" \ OP_TYPE$(4%) = "CHAIN" \ OP_TARG$(4%) = "SY:RMSUTILS.TSK" \ OP_PRIV%(4%) = 50%
790 OP_MENU%(5%) = 1% \ OP_KEY$(5%) = "9" \ OP_DESC$(5%) = "System Operator Console" \ OP_TYPE$(5%) = "CCL" \ OP_TARG$(5%) = "RUN $SYSTAT" \ OP_PRIV%(5%) = 100%
800 OP_MENU%(6%) = 2% \ OP_KEY$(6%) = "1" \ OP_DESC$(6%) = "DIBS-11 General Ledger & Trial Balance" \ OP_TYPE$(6%) = "CHAIN" \ OP_TARG$(6%) = "SY:DIBS11.TSK" \ OP_PRIV%(6%) = 20%
810 OP_MENU%(7%) = 2% \ OP_KEY$(7%) = "2" \ OP_DESC$(7%) = "SORT-11 Ledger Transaction Sort" \ OP_TYPE$(7%) = "CHAIN" \ OP_TARG$(7%) = "SY:SORT11.TSK" \ OP_PRIV%(7%) = 20%
820 OP_MENU%(8%) = 2% \ OP_KEY$(8%) = "M" \ OP_DESC$(8%) = "Return to Master Menu" \ OP_TYPE$(8%) = "SUBMENU" \ OP_TARG$(8%) = "MAIN_MENU" \ OP_PRIV%(8%) = 10%
830 OP_MENU%(9%) = 3% \ OP_KEY$(9%) = "1" \ OP_DESC$(9%) = "DECmail Electronic Messaging" \ OP_TYPE$(9%) = "CHAIN" \ OP_TARG$(9%) = "SY:DECMAIL.TSK" \ OP_PRIV%(9%) = 10%
840 OP_MENU%(10%) = 3% \ OP_KEY$(10%) = "2" \ OP_DESC$(10%) = "DECword/DP Word & List Processing" \ OP_TYPE$(10%) = "CHAIN" \ OP_TARG$(10%) = "SY:DECWORD.TSK" \ OP_PRIV%(10%) = 10%
850 OP_MENU%(11%) = 3% \ OP_KEY$(11%) = "3" \ OP_DESC$(11%) = "DATATRIEVE-11 & DECgraph Analytics" \ OP_TYPE$(11%) = "CHAIN" \ OP_TARG$(11%) = "SY:DTR11.TSK" \ OP_PRIV%(11%) = 10%
860 LG_MSG$(1%) = "MCF Session initialized for PPN [1,2] (Priv=100) on MAIN_MENU"
870 PRINT "[Sample MENU-11 Library loaded - 4 menus, 11 dispatch options]" \ GOTO 495
960 IF NUM_MENUS% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  MENU-11 Menu Control Library (MLB) - Library: "; MLB_FILE$ \ PRINT EQU$ \ PRINT "#   St  Menu Name        Options  Date          Menu Screen Title" \ PRINT SEP$
980 DI% = 1%
990 IF DI% > NUM_MENUS% THEN GOTO 1100
1000 CM_IDX% = DI% \ GOSUB 650 \ IDX_S$ = STR$(DI%) \ T_IN$ = IDX_S$ \ GOSUB 500 \ IPAD$ = LEFT$(T_OUT$ + "    ", 4%) \ ST_C$ = " "
1010 IF DI% = CURR_MENU% THEN ST_C$ = "*"
1020 IF MN_STAT$(DI%) = "D" THEN ST_C$ = "D"
1030 NM_P$ = LEFT$(MN_NAME$(DI%) + BLANKS$, 16%) \ OC_S$ = STR$(O_CNT%) \ T_IN$ = OC_S$ \ GOSUB 500 \ OC_P$ = LEFT$(T_OUT$ + BLANKS$, 8%) \ DT_P$ = LEFT$(MN_DATE$(DI%) + BLANKS$, 13%)
1040 PRINT IPAD$; ST_C$; "  "; NM_P$; " "; OC_P$; " "; DT_P$; " "; MN_TITLE$(DI%) \ DI% = DI% + 1% \ GOTO 990
1100 PRINT SEP$ \ PRINT "  "; NUM_MENUS%; " menu(s) in library (* = Active, D = Deleted)" \ PRINT EQU$ \ GOTO 495
1130 IF NUM_MENUS% = 0% THEN GOTO 3370
1140 IF ARGS$ = "" THEN GOTO 1220
1150 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ S_KEY$ = U_OUT$ \ REQ_M% = VAL(S_KEY$)
1160 IF REQ_M% >= 1% AND REQ_M% <= NUM_MENUS% THEN GOTO 1210
1170 REQ_M% = 0% \ SI% = 1%
1180 IF SI% > NUM_MENUS% THEN GOTO 1205
1190 IF MN_NAME$(SI%) = S_KEY$ THEN REQ_M% = SI%
1200 SI% = SI% + 1% \ GOTO 1180
1205 IF REQ_M% = 0% THEN GOTO 3380
1210 PREV_MENU% = CURR_MENU% \ CURR_MENU% = REQ_M% \ CM_IDX% = CURR_MENU% \ GOSUB 650
1220 PRINT "[Active menu set to #"; CURR_MENU%; ": "; MN_NAME$(CURR_MENU%); " - "; MN_TITLE$(CURR_MENU%); " ("; O_CNT%; " options)]" \ GOTO 495
1230 IF NUM_MENUS% = 0% THEN GOTO 3370
1240 CURR_MENU% = PREV_MENU% \ CM_IDX% = CURR_MENU% \ GOSUB 650
1250 PRINT "[Returned to parent menu #"; CURR_MENU%; ": "; MN_NAME$(CURR_MENU%); " ("; O_CNT%; " options)]" \ GOTO 495
1260 IF NUM_MENUS% >= 15% THEN GOTO 3390
1265 IF ARGS$ = "" THEN GOTO 1350
1270 C1% = INSTR(1%, ARGS$, ",")
1280 IF C1% = 0% THEN GOTO 1310
1290 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ N_MNM$ = U_OUT$ \ Q_IN$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ GOSUB 635 \ N_MTIT$ = Q_OUT$ \ GOTO 1320
1310 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ N_MNM$ = U_OUT$ \ N_MTIT$ = N_MNM$ + " APPLICATION MENU"
1320 PREV_MENU% = CURR_MENU% \ NUM_MENUS% = NUM_MENUS% + 1% \ CURR_MENU% = NUM_MENUS% \ MN_NAME$(CURR_MENU%) = N_MNM$ \ MN_TITLE$(CURR_MENU%) = N_MTIT$
1330 MN_DATE$(CURR_MENU%) = "28-OCT-1982" \ MN_STAT$(CURR_MENU%) = "A"
1340 PRINT "[Menu #"; CURR_MENU%; " created: "; N_MNM$; " ("; N_MTIT$; ")]" \ GOTO 495
1350 PRINT "MENU-11: Syntax is CREATE <menu_name>, <menu_title>" \ GOTO 495
1370 IF NUM_MENUS% = 0% THEN GOTO 3370
1380 IF NUM_OPTS% >= 50% THEN GOTO 3390
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1520
1410 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ O_KY$ = U_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1420 IF C2% = 0% THEN GOTO 1520
1430 Q_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 635 \ O_DS$ = Q_OUT$ \ REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1440 IF C3% = 0% THEN GOTO 1520
1450 Q_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ O_TP$ = U_OUT$ \ REM3$ = MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%) \ C4% = INSTR(1%, REM3$, ",")
1460 IF C4% = 0% THEN GOTO 1485
1470 Q_IN$ = LEFT$(REM3$, C4% - 1%) \ GOSUB 635 \ O_TG$ = Q_OUT$ \ O_PR% = VAL(MID$(REM3$, C4% + 1%, LEN(REM3$) - C4%)) \ GOTO 1495
1485 Q_IN$ = REM3$ \ GOSUB 635 \ O_TG$ = Q_OUT$ \ O_PR% = 10%
1495 IF O_PR% <= 0% THEN O_PR% = 10%
1500 NUM_OPTS% = NUM_OPTS% + 1% \ OP_MENU%(NUM_OPTS%) = CURR_MENU% \ OP_KEY$(NUM_OPTS%) = O_KY$ \ OP_DESC$(NUM_OPTS%) = O_DS$
1505 OP_TYPE$(NUM_OPTS%) = O_TP$ \ OP_TARG$(NUM_OPTS%) = O_TG$ \ OP_PRIV%(NUM_OPTS%) = O_PR%
1510 PRINT "[MCF: Option '"; O_KY$; "' added to "; MN_NAME$(CURR_MENU%); " ("; O_TP$; " -> "; O_TG$; ", Priv="; O_PR%; ")]" \ GOTO 495
1520 PRINT "MENU-11: Syntax is ADDOPT <key>, <desc>, <type>, <target> [, <priv>]" \ GOTO 495
1540 IF NUM_MENUS% = 0% THEN GOTO 3370
1550 PRINT EQU$ \ PRINT "  MENU-11 Option Dispatch Table - Menu: "; MN_NAME$(CURR_MENU%) \ PRINT "  Title: "; MN_TITLE$(CURR_MENU%) \ PRINT EQU$
1560 PRINT "Key   Action     Priv   Target Task / Menu    Option Description" \ PRINT SEP$
1570 OI% = 1% \ M_CNT% = 0%
1580 IF OI% > NUM_OPTS% THEN GOTO 1660
1590 IF OP_MENU%(OI%) <> CURR_MENU% THEN GOTO 1650
1600 M_CNT% = M_CNT% + 1% \ KY_P$ = LEFT$(OP_KEY$(OI%) + BLANKS$, 6%) \ TP_P$ = LEFT$(OP_TYPE$(OI%) + BLANKS$, 11%)
1610 P_S$ = STR$(OP_PRIV%(OI%)) \ T_IN$ = P_S$ \ GOSUB 500 \ PR_P$ = LEFT$(T_OUT$ + BLANKS$, 7%) \ TG_P$ = LEFT$(OP_TARG$(OI%) + BLANKS$, 22%)
1620 PRINT KY_P$; TP_P$; PR_P$; TG_P$; OP_DESC$(OI%)
1650 OI% = OI% + 1% \ GOTO 1580
1660 PRINT SEP$ \ PRINT "  "; M_CNT%; " option(s) defined in menu "; MN_NAME$(CURR_MENU%) \ PRINT EQU$ \ GOTO 495
1700 IF ARGS$ = "" THEN GOTO 1790
1705 RB% = INSTR(1%, ARGS$, "]") \ C_ST% = 1%
1708 IF RB% > 0% THEN C_ST% = RB% + 1%
1710 C1% = INSTR(C_ST%, ARGS$, ",")
1720 IF C1% = 0% THEN GOTO 1760
1730 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ USER_PPN$ = Q_OUT$ \ N_PR% = VAL(MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%))
1740 IF N_PR% > 0% THEN USER_PRIV% = N_PR%
1750 GOTO 1790
1760 N_PR% = VAL(ARGS$)
1770 IF N_PR% > 0% THEN USER_PRIV% = N_PR%
1775 IF N_PR% > 0% THEN GOTO 1790
1780 Q_IN$ = ARGS$ \ GOSUB 635 \ USER_PPN$ = Q_OUT$
1790 PRINT "[Operator context set: PPN="; USER_PPN$; ", Privilege Level="; USER_PRIV%; "]" \ GOTO 495
1820 IF NUM_MENUS% = 0% THEN GOTO 3370
1830 IF ARGS$ = "" THEN GOTO 2090
1840 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ R_KEY$ = U_OUT$ \ O_IDX% = 0% \ OI% = 1%
1850 IF OI% > NUM_OPTS% THEN GOTO 1890
1860 IF OP_MENU%(OI%) <> CURR_MENU% THEN GOTO 1880
1870 IF OP_KEY$(OI%) = R_KEY$ THEN O_IDX% = OI%
1880 OI% = OI% + 1% \ GOTO 1850
1890 IF O_IDX% = 0% THEN GOTO 2095
1900 REQ_P% = OP_PRIV%(O_IDX%)
1910 IF USER_PRIV% >= REQ_P% THEN GOTO 1960
1920 IF NUM_LOGS% < 30% THEN NUM_LOGS% = NUM_LOGS% + 1%
1922 S_L1$ = "SECURITY VIOLATION: PPN " + USER_PPN$
1924 S_L2$ = " denied option " + R_KEY$
1926 S_L3$ = " on " + MN_NAME$(CURR_MENU%)
1930 LG_MSG$(NUM_LOGS%) = S_L1$ + S_L2$ + S_L3$
1940 PRINT "[MENU-11 Security Violation: Option '"; R_KEY$; "' requires privilege level "; REQ_P%; " (current: "; USER_PRIV%; ")]" \ GOTO 495
1960 D_TP$ = OP_TYPE$(O_IDX%) \ D_TG$ = OP_TARG$(O_IDX%) \ D_DS$ = OP_DESC$(O_IDX%)
1970 IF NUM_LOGS% < 30% THEN NUM_LOGS% = NUM_LOGS% + 1%
1972 D_L1$ = "DISPATCH: PPN " + USER_PPN$
1974 D_L2$ = " executed " + D_TP$
1976 D_L3$ = " -> " + D_TG$
1980 LG_MSG$(NUM_LOGS%) = D_L1$ + D_L2$ + D_L3$
1990 IF D_TP$ <> "SUBMENU" THEN GOTO 2070
2000 U_IN$ = D_TG$ \ GOSUB 580 \ T_MNM$ = U_OUT$ \ REQ_M% = 0% \ SI% = 1%
2010 IF SI% > NUM_MENUS% THEN GOTO 2040
2020 IF MN_NAME$(SI%) = T_MNM$ THEN REQ_M% = SI%
2030 SI% = SI% + 1% \ GOTO 2010
2040 IF REQ_M% = 0% THEN GOTO 2070
2050 PREV_MENU% = CURR_MENU% \ CURR_MENU% = REQ_M% \ CM_IDX% = CURR_MENU% \ GOSUB 650
2060 PRINT "[MCF Dispatch: SUBMENU -> "; D_TG$; " (Active menu is now #"; CURR_MENU%; ": "; MN_NAME$(CURR_MENU%); ")]" \ GOTO 495
2070 PRINT "[MCF Dispatch: "; D_TP$; " -> "; D_TG$; " (Option "; R_KEY$; ": "; D_DS$; ")]" \ GOTO 495
2090 PRINT "MENU-11: Syntax is RUN <option_key>" \ GOTO 495
2095 PRINT "MENU-11: Option '"; R_KEY$; "' not found in active menu "; MN_NAME$(CURR_MENU%) \ GOTO 495
2120 PRINT EQU$ \ PRINT "  MENU-11 Security & Dispatch Audit Log (MCF)" \ PRINT EQU$
2130 IF NUM_LOGS% = 0% THEN PRINT "  (No audit events recorded)"
2140 LI% = 1%
2150 IF LI% > NUM_LOGS% THEN GOTO 2190
2160 L_S$ = STR$(LI%) \ T_IN$ = L_S$ \ GOSUB 500 \ L_P$ = LEFT$(T_OUT$ + "   ", 4%)
2170 PRINT "  "; L_P$; LG_MSG$(LI%) \ LI% = LI% + 1% \ GOTO 2150
2190 PRINT EQU$ \ GOTO 495
2280 IF NUM_MENUS% = 0% THEN GOTO 3370
2290 TO_FILE% = 0% \ OUT_FILE$ = ""
2300 IF VERB$ = "EXPORT" THEN GOTO 2350
2310 IF ARGS$ = "" THEN GOTO 2370
2320 U_IN$ = ARGS$ \ GOSUB 580
2330 IF LEFT$(U_OUT$, 3%) = "ON " THEN GOTO 2360
2340 REQ_M% = VAL(ARGS$)
2342 IF REQ_M% < 1% THEN GOTO 2370
2344 IF REQ_M% > NUM_MENUS% THEN GOTO 2370
2346 CURR_MENU% = REQ_M% \ GOTO 2370
2350 IF ARGS$ = "" THEN GOTO 2620
2355 Q_IN$ = ARGS$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1% \ GOTO 2370
2360 Q_IN$ = MID$(ARGS$, 4%, LEN(ARGS$) - 3%) \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1%
2370 IF TO_FILE% = 1% THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2380 C_TIT$ = MN_TITLE$(CURR_MENU%) \ C_PAD% = (68% - LEN(C_TIT$)) / 2%
2385 IF C_PAD% < 2% THEN C_PAD% = 2%
2390 PAD_C$ = LEFT$(BLANKS$, C_PAD%) \ PR_S$ = STR$(USER_PRIV%) \ T_IN$ = PR_S$ \ GOSUB 500 \ PR_TXT$ = T_OUT$
2400 IF TO_FILE% = 1% THEN GOTO 2420
2410 PRINT EQU$ \ PRINT PAD_C$; C_TIT$; "  "; LBRK$; MN_NAME$(CURR_MENU%); RBRK$ \ PRINT "  RSTS/E Account: "; USER_PPN$; "   Privilege: "; PR_TXT$; "   Date: "; MN_DATE$(CURR_MENU%) \ PRINT SEP$ \ GOTO 2430
2420 PRINT #2%, EQU$ \ PRINT #2%, PAD_C$; C_TIT$; "  "; LBRK$; MN_NAME$(CURR_MENU%); RBRK$ \ PRINT #2%, "  RSTS/E Account: "; USER_PPN$; "   Privilege: "; PR_TXT$; "   Date: "; MN_DATE$(CURR_MENU%) \ PRINT #2%, SEP$
2430 OI% = 1%
2440 IF OI% > NUM_OPTS% THEN GOTO 2560
2450 IF OP_MENU%(OI%) <> CURR_MENU% THEN GOTO 2550
2460 K_TAG$ = LBRK$ + OP_KEY$(OI%) + RBRK$ \ K_P$ = LEFT$(K_TAG$ + BLANKS$, 7%)
2470 D_P$ = LEFT$(OP_DESC$(OI%) + BLANKS$, 40%) \ T_TAG$ = LP$ + OP_TYPE$(OI%) + " -> " + OP_TARG$(OI%) + RP$
2530 IF TO_FILE% = 0% THEN PRINT "    "; K_P$; " "; D_P$; " "; T_TAG$
2540 IF TO_FILE% = 1% THEN PRINT #2%, "    "; K_P$; " "; D_P$; " "; T_TAG$
2550 OI% = OI% + 1% \ GOTO 2440
2560 IF TO_FILE% = 1% THEN GOTO 2590
2580 PRINT SEP$ \ PRINT "  Enter Selection Key (or BACK for Parent Menu, EXIT to Log Out):" \ PRINT EQU$ \ GOTO 495
2590 PRINT #2%, SEP$ \ PRINT #2%, "  Enter Selection Key (or BACK for Parent Menu, EXIT to Log Out):" \ PRINT #2%, EQU$ \ CLOSE #2%
2600 PRINT "[Menu "; MN_NAME$(CURR_MENU%); " rendered to "; OUT_FILE$; "]" \ GOTO 495
2620 PRINT "MENU-11: Specify output filename (EXPORT <file> or PRINT ON <file>)" \ GOTO 495
2640 IF NUM_MENUS% = 0% THEN GOTO 3370
2650 REQ_M% = CURR_MENU%
2660 IF ARGS$ <> "" THEN REQ_M% = VAL(ARGS$)
2670 IF REQ_M% < 1% THEN GOTO 3380
2680 IF REQ_M% > NUM_MENUS% THEN GOTO 3380
2690 MN_STAT$(REQ_M%) = "D" \ PRINT "[Menu #"; REQ_M%; " ("; MN_NAME$(REQ_M%); ") marked deleted]" \ GOTO 495
2710 IF NUM_MENUS% = 0% THEN GOTO 3370
2720 P_CNT% = 0% \ KEEP_M% = 0% \ PI% = 1%
2730 IF PI% > NUM_MENUS% THEN GOTO 2830
2740 IF MN_STAT$(PI%) = "D" THEN GOTO 2810
2750 KEEP_M% = KEEP_M% + 1%
2760 IF KEEP_M% = PI% THEN GOTO 2820
2770 MN_NAME$(KEEP_M%) = MN_NAME$(PI%) \ MN_TITLE$(KEEP_M%) = MN_TITLE$(PI%) \ MN_DATE$(KEEP_M%) = MN_DATE$(PI%) \ MN_STAT$(KEEP_M%) = MN_STAT$(PI%)
2780 OI% = 1%
2790 IF OI% > NUM_OPTS% THEN GOTO 2820
2800 IF OP_MENU%(OI%) = PI% THEN OP_MENU%(OI%) = KEEP_M%
2805 OI% = OI% + 1% \ GOTO 2790
2810 P_CNT% = P_CNT% + 1%
2820 PI% = PI% + 1% \ GOTO 2730
2830 NUM_MENUS% = KEEP_M%
2840 IF CURR_MENU% > NUM_MENUS% THEN CURR_MENU% = NUM_MENUS%
2850 IF CURR_MENU% < 1% THEN CURR_MENU% = 1%
2860 PRINT "[Menu library purged - "; P_CNT%; " deleted menu(s) removed]" \ GOTO 495
2880 CM_IDX% = CURR_MENU% \ GOSUB 650 \ DEL_CNT% = 0% \ SI% = 1%
2890 IF SI% > NUM_MENUS% THEN GOTO 2920
2900 IF MN_STAT$(SI%) = "D" THEN DEL_CNT% = DEL_CNT% + 1%
2910 SI% = SI% + 1% \ GOTO 2890
2920 PRINT "MENU-11 System Status:" \ PRINT "  Menu Library:    "; MLB_FILE$ \ PRINT "  Operator PPN:    "; USER_PPN$; " (Privilege:"; USER_PRIV%; ")"
2930 IF NUM_MENUS% > 0% THEN PRINT "  Active Menu:     #"; CURR_MENU%; " ("; MN_NAME$(CURR_MENU%); " - "; O_CNT%; " options)"
2940 IF NUM_MENUS% = 0% THEN PRINT "  Active Menu:     None"
2950 PRINT "  Total Menus:     "; NUM_MENUS%; " (Deleted: "; DEL_CNT%; ")" \ PRINT "  Total Options:   "; NUM_OPTS% \ GOTO 495
2970 IF NUM_MENUS% = 0% THEN GOTO 3370
2980 SV_FILE$ = MLB_FILE$
2990 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
3000 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
3010 IF SI% > NUM_MENUS% THEN GOTO 3040
3020 PRINT #2%, MN_NAME$(SI%); "|"; MN_TITLE$(SI%); "|"; MN_DATE$(SI%); "|"; MN_STAT$(SI%) \ SI% = SI% + 1% \ GOTO 3010
3040 CLOSE #2% \ PRINT "["; NUM_MENUS%; " menu(s) saved to library "; SV_FILE$; "]" \ GOTO 495
3060 LD_FILE$ = MLB_FILE$
3070 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
3080 ON ERROR GOTO 3180 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_MENUS% = 0%
3090 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
3100 IF T_OUT$ = "" THEN GOTO 3090
3110 P1% = INSTR(1%, T_OUT$, "|")
3120 IF P1% = 0% THEN GOTO 3090
3130 M_NM$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
3140 IF P2% = 0% THEN GOTO 3090
3150 M_TI$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
3160 IF P3% = 0% THEN GOTO 3090
3170 M_DT$ = LEFT$(REM2$, P3% - 1%) \ M_ST$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ NUM_MENUS% = NUM_MENUS% + 1%
3175 MN_NAME$(NUM_MENUS%) = M_NM$ \ MN_TITLE$(NUM_MENUS%) = M_TI$ \ MN_DATE$(NUM_MENUS%) = M_DT$ \ MN_STAT$(NUM_MENUS%) = M_ST$ \ GOTO 3090
3180 CLOSE #2% \ RESUME 3190
3190 ON ERROR GOTO 0 \ CURR_MENU% = 1% \ PREV_MENU% = 1% \ PRINT "["; NUM_MENUS%; " menu(s) loaded from library "; LD_FILE$; "]" \ GOTO 495
3205 NUM_MENUS% = 0% \ CURR_MENU% = 1% \ PREV_MENU% = 1% \ NUM_OPTS% = 0% \ NUM_LOGS% = 0% \ PRINT "[MENU-11 menu library cleared]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "    MENU-11 Menu Control & Dispatch Facility Commands" \ PRINT EQU$ \ PRINT "  DIR / MENUS / MLB                List menus in Menu Control Library"
3225 PRINT "  SELECT <name_or_#> / BACK        Select active menu or return to parent menu" \ PRINT "  CREATE <name>, <title>           Create new menu definition"
3230 PRINT "  ADDOPT <k>,<desc>,<t>,<trg>[,p]  Add dispatch option to active menu" \ PRINT "  OPTIONS / DESCRIBE / ITEMS       Display Option Dispatch Table"
3235 PRINT "  USER <ppn>, <priv>               Set operator PPN account and privilege level" \ PRINT "  RUN / EXEC / PICK <key>          Execute option (SUBMENU, CHAIN, CCL)"
3240 PRINT "  LOG / AUDIT / HISTORY            Display security & dispatch audit log" \ PRINT "  DISPLAY / RENDER / PRINT [ON f]  Render VT100 menu screen or export to file"
3245 PRINT "  DELETE [menu#] / PURGE           Mark menu deleted or purge library" \ PRINT "  SAMPLE / SAVE [f] / LOAD [f]     Load DEC demo menus or save/load MLB"
3250 PRINT "  SHOW / CLEAR / EXIT              Show status, clear memory, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "MENU-11: No menus in library. Use SAMPLE or CREATE." \ GOTO 495
3380 PRINT "MENU-11: Menu not found or out of range" \ GOTO 495
3390 PRINT "MENU-11: Menu or option table is full" \ GOTO 495
3400 END
