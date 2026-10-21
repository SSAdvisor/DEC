10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM AP_DATE$(40%) \ DIM AP_TIME$(40%) \ DIM AP_DUR%(40%)
20 DIM AP_ALARM$(40%) \ DIM AP_DESC$(40%) \ DIM FLD$(10%) \ DIM DAY_MARK$(31%)
30 NUM_APPT% = 0% \ CUR_DATE$ = "1991-10-18" \ CAL_TITLE$ = "Maynard Engineering (ZKO)" \ CAL_FILE$ = "DECWCAL.DAT"
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
100 PRINT EQU$ \ PRINT "    DECwindows Calendar V3.0 - XUI/Motif Time & Schedule Manager" \ PRINT "    Digital Equipment Corporation (DEC) VAX/VMS & ULTRIX Workstation Software" \ PRINT EQU$
110 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
120 PRINT "CALENDAR> "; \ LINE INPUT RAW_INPUT$
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
360 IF VERB$ = "DATE" OR VERB$ = "GOTO" OR VERB$ = "SELECT" THEN GOTO 920
370 IF VERB$ = "MONTH" OR VERB$ = "GRID" THEN GOTO 990
380 IF VERB$ = "DAY" OR VERB$ = "AGENDA" THEN GOTO 1210
390 IF VERB$ = "LIST" OR VERB$ = "SCHEDULE" OR VERB$ = "ALL" THEN GOTO 1400
400 IF VERB$ = "ADD" OR VERB$ = "APPT" OR VERB$ = "BOOK" THEN GOTO 1540
410 IF VERB$ = "DELETE" OR VERB$ = "CANCEL" OR VERB$ = "DEL" THEN GOTO 1690
420 IF VERB$ = "ALARM" THEN GOTO 1810
430 IF VERB$ = "ALARMS" OR VERB$ = "REMINDERS" THEN GOTO 1950
440 IF VERB$ = "CHECK" OR VERB$ = "CONFLICTS" OR VERB$ = "AUDIT" THEN GOTO 2090
450 IF VERB$ = "SEARCH" OR VERB$ = "FIND" THEN GOTO 2290
460 IF VERB$ = "DISPLAY" OR VERB$ = "SCREEN" OR VERB$ = "RENDER" OR VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 2450
484 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2840
486 IF VERB$ = "SAVE" THEN GOTO 2950
488 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3060
490 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3190
492 IF VERB$ = "X11" OR VERB$ = "GUI" OR VERB$ = "XDISPLAY" THEN GOTO 3392
494 PRINT "CALENDAR: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
750 NUM_APPT% = 6% \ CUR_DATE$ = "1991-10-18" \ CAL_TITLE$ = "Maynard Engineering (ZKO)"
760 AP_DATE$(1%) = "1991-10-18" \ AP_TIME$(1%) = "09:00" \ AP_DUR%(1%) = 60% \ AP_ALARM$(1%) = "ON"
770 AP_DESC$(1%) = "VAX/VMS V5.5 Release Engineering Sign-off (ZKO2-3/Q18)"
780 AP_DATE$(2%) = "1991-10-18" \ AP_TIME$(2%) = "11:00" \ AP_DUR%(2%) = 45% \ AP_ALARM$(2%) = "ON"
790 AP_DESC$(2%) = "DECwindows XUI to OSF/Motif Toolkit Porting Review"
800 AP_DATE$(3%) = "1991-10-18" \ AP_TIME$(3%) = "14:30" \ AP_DUR%(3%) = 90% \ AP_ALARM$(3%) = "OFF"
810 AP_DESC$(3%) = "Alpha AXP 64-Bit Architecture Briefing with Hudson Team"
820 AP_DATE$(4%) = "1991-10-21" \ AP_TIME$(4%) = "10:00" \ AP_DUR%(4%) = 60% \ AP_ALARM$(4%) = "ON"
830 AP_DESC$(4%) = "DECUS Fall Symposium Keynote Preparation (Anaheim)"
840 AP_DATE$(5%) = "1991-10-24" \ AP_TIME$(5%) = "13:00" \ AP_DUR%(5%) = 30% \ AP_ALARM$(5%) = "OFF"
850 AP_DESC$(5%) = "ULTRIX Workstation Field Service Diagnostics Sync"
860 AP_DATE$(6%) = "1991-10-28" \ AP_TIME$(6%) = "16:00" \ AP_DUR%(6%) = 120% \ AP_ALARM$(6%) = "ON"
870 AP_DESC$(6%) = "VAXcluster CI780 Star Coupler Maintenance Window"
880 PRINT "[Sample DECwindows Calendar loaded: 6 appointments for October 1991]" \ GOTO 495
920 IF ARGS$ = "" THEN GOTO 960
930 Q_IN$ = ARGS$ \ GOSUB 635 \ CUR_DATE$ = Q_OUT$
960 PRINT "[Active calendar date set to "; CUR_DATE$; "]" \ GOTO 495
990 M_PFX$ = LEFT$(CUR_DATE$, 8%)
1000 DI% = 1%
1010 IF DI% > 31% THEN GOTO 1040
1020 DAY_MARK$(DI%) = " " \ DI% = DI% + 1% \ GOTO 1010
1040 AI% = 1%
1050 IF AI% > NUM_APPT% THEN GOTO 1100
1060 IF LEFT$(AP_DATE$(AI%), 8%) <> M_PFX$ THEN GOTO 1090
1070 D_NUM% = VAL(MID$(AP_DATE$(AI%), 9%, 2%))
1080 IF D_NUM% >= 1% AND D_NUM% <= 31% THEN DAY_MARK$(D_NUM%) = "*"
1090 AI% = AI% + 1% \ GOTO 1050
1100 M_HDR$ = LEFT$(CUR_DATE$, 7%) \ PRINT EQU$ \ PRINT "  DECwindows Calendar Monthly View - "; M_HDR$; " ("; CAL_TITLE$; ")" \ PRINT SEP$
1110 PRINT "  Su    Mo    Tu    We    Th    Fr    Sa    (* = Scheduled Appointments)" \ PRINT SEP$
1120 PRINT "              01"; DAY_MARK$(1%); "   02"; DAY_MARK$(2%); "   03"; DAY_MARK$(3%); "   04"; DAY_MARK$(4%); "   05"; DAY_MARK$(5%)
1130 PRINT "  06"; DAY_MARK$(6%); "   07"; DAY_MARK$(7%); "   08"; DAY_MARK$(8%); "   09"; DAY_MARK$(9%); "   10"; DAY_MARK$(10%); "   11"; DAY_MARK$(11%); "   12"; DAY_MARK$(12%)
1140 PRINT "  13"; DAY_MARK$(13%); "   14"; DAY_MARK$(14%); "   15"; DAY_MARK$(15%); "   16"; DAY_MARK$(16%); "   17"; DAY_MARK$(17%); "   18"; DAY_MARK$(18%); "   19"; DAY_MARK$(19%)
1150 PRINT "  20"; DAY_MARK$(20%); "   21"; DAY_MARK$(21%); "   22"; DAY_MARK$(22%); "   23"; DAY_MARK$(23%); "   24"; DAY_MARK$(24%); "   25"; DAY_MARK$(25%); "   26"; DAY_MARK$(26%)
1160 PRINT "  27"; DAY_MARK$(27%); "   28"; DAY_MARK$(28%); "   29"; DAY_MARK$(29%); "   30"; DAY_MARK$(30%); "   31"; DAY_MARK$(31%)
1170 PRINT EQU$ \ GOTO 495
1210 IF NUM_APPT% = 0% THEN GOTO 3370
1220 D_TARG$ = CUR_DATE$
1230 IF ARGS$ = "" THEN GOTO 1250
1240 Q_IN$ = ARGS$ \ GOSUB 635 \ D_TARG$ = Q_OUT$ \ CUR_DATE$ = D_TARG$
1250 PRINT EQU$ \ PRINT "  DECwindows Calendar Daily Agenda for "; D_TARG$ \ PRINT EQU$
1260 PRINT "ID    Time    Dur(m)  Alarm   Appointment Description" \ PRINT SEP$
1270 D_CNT% = 0% \ AI% = 1%
1280 IF AI% > NUM_APPT% THEN GOTO 1360
1290 IF AP_DATE$(AI%) <> D_TARG$ THEN GOTO 1350
1300 D_CNT% = D_CNT% + 1%
1310 I_S$ = STR$(AI%) \ T_IN$ = I_S$ \ GOSUB 500 \ I_P$ = LEFT$(T_OUT$ + BLANKS$, 6%)
1320 TM_P$ = LEFT$(AP_TIME$(AI%) + BLANKS$, 8%)
1330 DU_S$ = STR$(AP_DUR%(AI%)) \ T_IN$ = DU_S$ \ GOSUB 500 \ DU_P$ = LEFT$(T_OUT$ + BLANKS$, 8%)
1340 AL_P$ = LEFT$(AP_ALARM$(AI%) + BLANKS$, 8%)
1345 PRINT I_P$; TM_P$; DU_P$; AL_P$; AP_DESC$(AI%)
1350 AI% = AI% + 1% \ GOTO 1280
1360 PRINT SEP$ \ PRINT "  "; D_CNT%; " appointment(s) scheduled on "; D_TARG$ \ PRINT EQU$ \ GOTO 495
1400 IF NUM_APPT% = 0% THEN GOTO 3370
1410 PRINT EQU$ \ PRINT "  DECwindows Calendar Full Schedule ("; NUM_APPT%; " appointments)" \ PRINT EQU$
1420 PRINT "ID   Date         Time    Dur(m)  Alarm  Description" \ PRINT SEP$
1430 AI% = 1%
1440 IF AI% > NUM_APPT% THEN GOTO 1510
1450 I_S$ = STR$(AI%) \ T_IN$ = I_S$ \ GOSUB 500 \ I_P$ = LEFT$(T_OUT$ + BLANKS$, 5%)
1460 DT_P$ = LEFT$(AP_DATE$(AI%) + BLANKS$, 13%) \ TM_P$ = LEFT$(AP_TIME$(AI%) + BLANKS$, 8%)
1470 DU_S$ = STR$(AP_DUR%(AI%)) \ T_IN$ = DU_S$ \ GOSUB 500 \ DU_P$ = LEFT$(T_OUT$ + BLANKS$, 8%)
1480 AL_P$ = LEFT$(AP_ALARM$(AI%) + BLANKS$, 7%)
1490 PRINT I_P$; DT_P$; TM_P$; DU_P$; AL_P$; AP_DESC$(AI%)
1500 AI% = AI% + 1% \ GOTO 1440
1510 PRINT EQU$ \ GOTO 495
1540 IF NUM_APPT% >= 40% THEN GOTO 1670
1550 P_IN$ = ARGS$ \ GOSUB 650
1560 IF NF% < 5% THEN GOTO 1660
1570 N_DT$ = FLD$(1%) \ N_TM$ = FLD$(2%) \ N_DU% = VAL(FLD$(3%))
1580 U_IN$ = FLD$(4%) \ GOSUB 580 \ N_AL$ = U_OUT$ \ N_DS$ = FLD$(5%)
1590 IF N_DU% <= 0% THEN N_DU% = 30%
1600 IF N_AL$ <> "ON" AND N_AL$ <> "OFF" THEN N_AL$ = "ON"
1610 NUM_APPT% = NUM_APPT% + 1% \ AP_DATE$(NUM_APPT%) = N_DT$ \ AP_TIME$(NUM_APPT%) = N_TM$
1620 AP_DUR%(NUM_APPT%) = N_DU% \ AP_ALARM$(NUM_APPT%) = N_AL$ \ AP_DESC$(NUM_APPT%) = N_DS$
1630 PRINT "[Added Appointment #"; NUM_APPT%; " on "; N_DT$; " at "; N_TM$; " ("; N_DU%; "m, Alarm:"; N_AL$; "): "; N_DS$; "]" \ GOTO 495
1660 PRINT "CALENDAR: Syntax is ADD <date|time|dur_min|alarm_ON_OFF|description>" \ GOTO 495
1670 PRINT "CALENDAR: Schedule database full (maximum 40 appointments)." \ GOTO 495
1690 IF NUM_APPT% = 0% THEN GOTO 3370
1700 D_ID% = VAL(ARGS$)
1710 IF D_ID% < 1% OR D_ID% > NUM_APPT% THEN GOTO 3380
1720 D_DS$ = AP_DESC$(D_ID%) \ DI% = D_ID%
1730 IF DI% >= NUM_APPT% THEN GOTO 1770
1740 AP_DATE$(DI%) = AP_DATE$(DI% + 1%) \ AP_TIME$(DI%) = AP_TIME$(DI% + 1%) \ AP_DUR%(DI%) = AP_DUR%(DI% + 1%)
1750 AP_ALARM$(DI%) = AP_ALARM$(DI% + 1%) \ AP_DESC$(DI%) = AP_DESC$(DI% + 1%) \ DI% = DI% + 1% \ GOTO 1730
1770 NUM_APPT% = NUM_APPT% - 1%
1780 PRINT "[Cancelled Appointment #"; D_ID%; ": "; D_DS$; "]" \ GOTO 495
1810 IF NUM_APPT% = 0% THEN GOTO 3370
1820 SP_A% = INSTR(1%, ARGS$, " ")
1830 IF SP_A% = 0% THEN GOTO 1920
1840 A_ID% = VAL(LEFT$(ARGS$, SP_A% - 1%))
1850 IF A_ID% < 1% OR A_ID% > NUM_APPT% THEN GOTO 3380
1860 T_IN$ = MID$(ARGS$, SP_A% + 1%, LEN(ARGS$) - SP_A%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ A_ST$ = U_OUT$
1870 IF A_ST$ <> "ON" AND A_ST$ <> "OFF" THEN GOTO 1920
1880 AP_ALARM$(A_ID%) = A_ST$
1890 PRINT "[Appointment #"; A_ID%; " alarm set to "; A_ST$; " ("; AP_DESC$(A_ID%); ")]" \ GOTO 495
1920 PRINT "CALENDAR: Syntax is ALARM <id> ON|OFF" \ GOTO 495
1950 IF NUM_APPT% = 0% THEN GOTO 3370
1960 PRINT EQU$ \ PRINT "  DECwindows Calendar Active Reminder Alarms" \ PRINT EQU$
1970 PRINT "ID   Date         Time    Dur(m)  Description" \ PRINT SEP$
1980 A_CNT% = 0% \ AI% = 1%
1990 IF AI% > NUM_APPT% THEN GOTO 2060
2000 IF AP_ALARM$(AI%) <> "ON" THEN GOTO 2050
2010 A_CNT% = A_CNT% + 1%
2020 I_S$ = STR$(AI%) \ T_IN$ = I_S$ \ GOSUB 500 \ I_P$ = LEFT$(T_OUT$ + BLANKS$, 5%)
2030 DT_P$ = LEFT$(AP_DATE$(AI%) + BLANKS$, 13%) \ TM_P$ = LEFT$(AP_TIME$(AI%) + BLANKS$, 8%)
2040 DU_S$ = STR$(AP_DUR%(AI%)) \ T_IN$ = DU_S$ \ GOSUB 500 \ DU_P$ = LEFT$(T_OUT$ + BLANKS$, 8%)
2045 PRINT I_P$; DT_P$; TM_P$; DU_P$; AP_DESC$(AI%)
2050 AI% = AI% + 1% \ GOTO 1990
2060 PRINT SEP$ \ PRINT "  Total active alarms: "; A_CNT% \ PRINT EQU$ \ GOTO 495
2090 IF NUM_APPT% = 0% THEN GOTO 3370
2100 PRINT EQU$ \ PRINT "  DECwindows Calendar Timeslot Conflict & Double-Booking Audit" \ PRINT SEP$
2110 C_ERR% = 0% \ I1% = 1%
2120 IF I1% >= NUM_APPT% THEN GOTO 2220
2130 I2% = I1% + 1%
2140 IF I2% > NUM_APPT% THEN GOTO 2200
2150 IF AP_DATE$(I1%) <> AP_DATE$(I2%) THEN GOTO 2190
2160 IF AP_TIME$(I1%) <> AP_TIME$(I2%) THEN GOTO 2190
2170 C_ERR% = C_ERR% + 1%
2180 PRINT "  [CONFLICT] "; AP_DATE$(I1%); " "; AP_TIME$(I1%); ": Appt #"; I1%; " overlaps Appt #"; I2%
2190 I2% = I2% + 1% \ GOTO 2140
2200 I1% = I1% + 1% \ GOTO 2120
2220 PRINT "  Total Appointments Checked: "; NUM_APPT%
2230 PRINT "  Timeslot Conflicts Found:   "; C_ERR%
2240 IF C_ERR% = 0% THEN PRINT "  [Audit PASSED: No overlapping appointment timeslots detected]"
2250 IF C_ERR% > 0% THEN PRINT "  [Audit WARNING: "; C_ERR%; " double-booked timeslot conflict(s) detected]"
2260 PRINT EQU$ \ GOTO 495
2290 IF NUM_APPT% = 0% THEN GOTO 3370
2300 IF ARGS$ = "" THEN GOTO 2420
2310 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ KW$ = U_OUT$
2320 PRINT EQU$ \ PRINT "  DECwindows Calendar Search Results for '"; Q_OUT$; "'" \ PRINT SEP$
2330 S_HIT% = 0% \ AI% = 1%
2340 IF AI% > NUM_APPT% THEN GOTO 2400
2350 H_TMP$ = AP_DATE$(AI%) + " " + AP_TIME$(AI%)
2352 U_IN$ = H_TMP$ + " " + AP_DESC$(AI%) \ GOSUB 580 \ HAY$ = U_OUT$
2360 IF INSTR(1%, HAY$, KW$) = 0% THEN GOTO 2390
2370 S_HIT% = S_HIT% + 1%
2380 PRINT "  [Match #"; S_HIT%; "] #"; AI%; " "; AP_DATE$(AI%); " "; AP_TIME$(AI%); " - "; AP_DESC$(AI%)
2390 AI% = AI% + 1% \ GOTO 2340
2400 PRINT SEP$ \ PRINT "  Total matching appointments: "; S_HIT% \ PRINT EQU$ \ GOTO 495
2420 PRINT "CALENDAR: Syntax is SEARCH <keyword>" \ GOTO 495
2450 IF NUM_APPT% = 0% THEN GOTO 3370
2460 TO_FILE% = 0% \ OUT_FILE$ = ""
2470 IF ARGS$ = "" THEN GOTO 2530
2480 U_IN$ = ARGS$ \ GOSUB 580 \ U_ARGS$ = U_OUT$
2490 IF LEFT$(U_ARGS$, 3%) <> "ON " THEN GOTO 2520
2500 T_IN$ = MID$(ARGS$, 4%, LEN(ARGS$) - 3%) \ GOSUB 500 \ Q_IN$ = T_OUT$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1% \ GOTO 2530
2520 Q_IN$ = ARGS$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1%
2530 IF TO_FILE% = 1% THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2540 BDR$ = "+------------------------------------------------------------------------------+" \ SP1$ = " " \ COL_SEP$ = " | "
2550 T_BAR$ = VBAR$ + " [=] DECwindows Calendar - " + CAL_TITLE$ + BLANKS$
2560 T_BAR$ = LEFT$(T_BAR$, 72%) + " [v][^]" + VBAR$
2570 M_BAR$ = VBAR$ + "  File    Edit    View    Entry    Customize    Help                          " + VBAR$
2580 D_HDR$ = " Selected Day: " + CUR_DATE$
2585 D_HDR$ = D_HDR$ + "   [<< Prev Day] [Today] [Next Day >>]"
2590 D_ROW$ = LEFT$(VBAR$ + D_HDR$ + BLANKS$, 79%) + VBAR$
2600 IF TO_FILE% = 1% THEN GOTO 2625
2610 PRINT BDR$ \ PRINT T_BAR$ \ PRINT BDR$ \ PRINT M_BAR$ \ PRINT BDR$ \ PRINT D_ROW$ \ PRINT BDR$ \ GOTO 2640
2625 PRINT #2%, BDR$ \ PRINT #2%, T_BAR$ \ PRINT #2%, BDR$ \ PRINT #2%, M_BAR$ \ PRINT #2%, BDR$ \ PRINT #2%, D_ROW$ \ PRINT #2%, BDR$
2640 AI% = 1% \ SHOWN% = 0%
2650 IF AI% > NUM_APPT% THEN GOTO 2740
2660 IF AP_DATE$(AI%) <> CUR_DATE$ THEN GOTO 2730
2670 SHOWN% = SHOWN% + 1%
2680 R_LN$ = " " + AP_TIME$(AI%) + COL_SEP$ + LBRK$ + AP_ALARM$(AI%) + RBRK$ + SP1$ + AP_DESC$(AI%)
2690 R_ROW$ = LEFT$(VBAR$ + R_LN$ + BLANKS$, 79%) + VBAR$
2700 IF TO_FILE% = 0% THEN PRINT R_ROW$
2710 IF TO_FILE% = 1% THEN PRINT #2%, R_ROW$
2730 AI% = AI% + 1% \ GOTO 2650
2740 T_S$ = STR$(NUM_APPT%) \ T_IN$ = T_S$ \ GOSUB 500 \ T_STR$ = T_OUT$
2750 S_INF$ = " [Calendar: " + CAL_FILE$ + RBRK$
2755 S_INF$ = S_INF$ + " [Date: " + CUR_DATE$ + RBRK$
2760 S_INF$ = S_INF$ + " [Total Entries: " + T_STR$ + RBRK$
2770 S_ROW$ = LEFT$(VBAR$ + S_INF$ + BLANKS$, 79%) + VBAR$
2780 IF TO_FILE% = 1% THEN GOTO 2800
2790 PRINT BDR$ \ PRINT S_ROW$ \ PRINT BDR$ \ GOTO 2820
2800 PRINT #2%, BDR$ \ PRINT #2%, S_ROW$ \ PRINT #2%, BDR$ \ CLOSE #2%
2810 PRINT "[Calendar window exported to "; OUT_FILE$; "]"
2820 GOTO 495
2840 PRINT EQU$ \ PRINT "  DECwindows Calendar V3.0 - Schedule & Time Manager Status" \ PRINT SEP$
2850 PRINT "  Calendar Profile:       "; CAL_TITLE$
2860 PRINT "  Database File:          "; CAL_FILE$
2870 PRINT "  Selected Active Date:   "; CUR_DATE$
2880 PRINT "  Total Appointments:     "; NUM_APPT%; " / 40 entries"
2890 A_CNT% = 0% \ AI% = 1%
2900 IF AI% > NUM_APPT% THEN GOTO 2925
2910 IF AP_ALARM$(AI%) = "ON" THEN A_CNT% = A_CNT% + 1%
2920 AI% = AI% + 1% \ GOTO 2900
2925 PRINT "  Active Reminder Alarms: "; A_CNT%
2930 PRINT EQU$ \ GOTO 495
2950 IF NUM_APPT% = 0% THEN GOTO 3370
2960 IF ARGS$ = "" THEN GOTO 2970
2965 Q_IN$ = ARGS$ \ GOSUB 635 \ CAL_FILE$ = Q_OUT$
2970 OPEN CAL_FILE$ FOR OUTPUT AS FILE #1%
2980 AI% = 1%
2990 IF AI% > NUM_APPT% THEN GOTO 3040
3000 DU_S$ = STR$(AP_DUR%(AI%)) \ T_IN$ = DU_S$ \ GOSUB 500 \ DU_STR$ = T_OUT$
3010 C_REC$ = AP_DATE$(AI%) + PIPE$ + AP_TIME$(AI%) + PIPE$ + DU_STR$ + PIPE$ + AP_ALARM$(AI%) + PIPE$ + AP_DESC$(AI%)
3020 PRINT #1%, C_REC$ \ AI% = AI% + 1% \ GOTO 2990
3040 CLOSE #1% \ PRINT "[Saved "; NUM_APPT%; " appointment(s) to "; CAL_FILE$; "]" \ GOTO 495
3060 IF ARGS$ = "" THEN GOTO 3170
3070 Q_IN$ = ARGS$ \ GOSUB 635 \ CAL_FILE$ = Q_OUT$
3080 NUM_APPT% = 0% \ OPEN CAL_FILE$ FOR INPUT AS FILE #1%
3090 IF NUM_APPT% >= 40% THEN GOTO 3150
3100 LINE INPUT #1%, IN_L$
3110 IF LEN(IN_L$) = 0% THEN GOTO 3150
3115 IF ASCII(LEFT$(IN_L$, 1%)) = 0% THEN GOTO 3150
3120 P_IN$ = IN_L$ \ GOSUB 650
3125 IF NF% < 5% THEN GOTO 3150
3130 NUM_APPT% = NUM_APPT% + 1% \ AP_DATE$(NUM_APPT%) = FLD$(1%) \ AP_TIME$(NUM_APPT%) = FLD$(2%)
3140 AP_DUR%(NUM_APPT%) = VAL(FLD$(3%)) \ AP_ALARM$(NUM_APPT%) = FLD$(4%) \ AP_DESC$(NUM_APPT%) = FLD$(5%) \ GOTO 3090
3150 CLOSE #1%
3155 IF NUM_APPT% > 0% THEN CUR_DATE$ = AP_DATE$(1%)
3160 PRINT "[Loaded "; NUM_APPT%; " appointment(s) from "; CAL_FILE$; "]" \ GOTO 495
3170 PRINT "CALENDAR: Syntax is LOAD <filename>" \ GOTO 495
3190 NUM_APPT% = 0% \ CUR_DATE$ = "1991-10-18"
3200 PRINT "[Calendar appointments cleared]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "  DECwindows Calendar Time & Schedule Manager Commands" \ PRINT SEP$
3230 PRINT "  SAMPLE                   Load sample October 1991 DEC Engineering schedule"
3240 PRINT "  MONTH / GRID             Display monthly calendar grid with [*] markers"
3250 PRINT "  DATE <YYYY-MM-DD>        Select active calendar date"
3260 PRINT "  DAY [YYYY-MM-DD]         Display daily appointment agenda for a date"
3270 PRINT "  LIST / SCHEDULE          List all scheduled appointments across all dates"
3280 PRINT "  ADD <dt|tm|dur|alm|desc> Schedule a new appointment"
3290 PRINT "  DELETE <id>              Cancel and remove appointment #<id>"
3300 PRINT "  ALARM <id> ON|OFF        Toggle reminder alarm for appointment #<id>"
3310 PRINT "  ALARMS                   List all appointments with active alarms"
3320 PRINT "  CHECK / CONFLICTS        Audit schedule for double-booked timeslots"
3330 PRINT "  SEARCH <keyword>         Search appointments by date, time, or description"
3340 PRINT "  DISPLAY [ON <file>]      Render Motif/XUI Calendar window (or export)"
3350 PRINT "  SHOW / SAVE <f> / LOAD <f> / CLEAR / EXIT" \ PRINT EQU$ \ GOTO 495
3370 PRINT "CALENDAR: No appointments scheduled. Use SAMPLE, ADD, or LOAD first." \ GOTO 495
3380 PRINT "CALENDAR: Invalid appointment ID." \ GOTO 495
3392 IF NUM_APPT% = 0% THEN GOSUB 750
3393 ARGS$ = "/tmp/decw_calendar.dat" \ GOSUB 2950
3394 VERB$ = "EXPORT" \ ARGS$ = "/tmp/decw_calendar.txt" \ GOSUB 2450
3395 X_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app calendar --frame /tmp/decw_calendar.txt"
3396 X_RC% = SYS(X_CMD$) \ GOTO 495
3400 END
