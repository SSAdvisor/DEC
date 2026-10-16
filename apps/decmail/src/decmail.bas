10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM M_FROM$(60%) \ DIM M_TO$(60%) \ DIM M_DATE$(60%) \ DIM M_SUBJ$(60%) \ DIM M_STAT$(60%) \ DIM M_FOLD$(60%) \ DIM M_BODY$(60%)
20 NUM_MSGS% = 0% \ CURR_MSG% = 1% \ CURR_USER$ = "OPERATOR" \ CURR_FOLD$ = "ALL" \ MAIL_FILE$ = "DECMAIL.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    DECmail V3.0 - Electronic Messaging & Mail Management System" \ PRINT "    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11" \ PRINT EQU$
90 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
100 PRINT "MAIL> "; \ LINE INPUT RAW_INPUT$
110 IF LEN(RAW_INPUT$) = 0% THEN GOTO 2700
120 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 26% THEN GOTO 2700
130 IF ASCII(LEFT$(RAW_INPUT$, 1%)) = 0% THEN GOTO 2700
140 T_IN$ = RAW_INPUT$ \ GOSUB 500
150 IF T_OUT$ = "" THEN GOTO 100
160 SC_REM$ = T_OUT$
170 IF SC_REM$ = "" THEN GOTO 230
180 SC_P% = INSTR(1%, SC_REM$, ";")
190 IF SC_P% = 0% THEN GOTO 210
200 RAW_CMD$ = LEFT$(SC_REM$, SC_P% - 1%) \ SC_REM$ = MID$(SC_REM$, SC_P% + 1%, LEN(SC_REM$) - SC_P%) \ GOTO 220
210 RAW_CMD$ = SC_REM$ \ SC_REM$ = ""
220 GOSUB 250 \ GOTO 170
230 IF IS_BATCH% = 1% THEN GOTO 2700
240 GOTO 100
250 T_IN$ = RAW_CMD$ \ GOSUB 500 \ WORK_CMD$ = T_OUT$
260 IF WORK_CMD$ = "" THEN GOTO 490
270 SP% = INSTR(1%, WORK_CMD$, " ")
280 IF SP% = 0% THEN GOTO 300
290 VERB$ = LEFT$(WORK_CMD$, SP% - 1%) \ ARGS$ = MID$(WORK_CMD$, SP% + 1%, LEN(WORK_CMD$) - SP%) \ GOTO 310
300 VERB$ = WORK_CMD$ \ ARGS$ = ""
310 U_IN$ = VERB$ \ GOSUB 580 \ VERB$ = U_OUT$ \ T_IN$ = ARGS$ \ GOSUB 500 \ ARGS$ = T_OUT$
320 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "BYE" THEN GOTO 2700
330 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 2590
340 IF VERB$ = "DIR" OR VERB$ = "DIRECTORY" THEN GOTO 740
350 IF VERB$ = "READ" OR VERB$ = "VIEW" OR VERB$ = "TYPE" THEN GOTO 920
360 IF VERB$ = "SEND" OR VERB$ = "MAIL" OR VERB$ = "POST" THEN GOTO 1110
370 IF VERB$ = "REPLY" OR VERB$ = "REP" THEN GOTO 1470
380 IF VERB$ = "FORWARD" OR VERB$ = "FWD" THEN GOTO 1660
390 IF VERB$ = "DELETE" OR VERB$ = "DEL" THEN GOTO 1800
400 IF VERB$ = "PURGE" THEN GOTO 1870
410 IF VERB$ = "EXTRACT" OR VERB$ = "EXPORT" THEN GOTO 2020
420 IF VERB$ = "SELECT" OR VERB$ = "FOLDER" THEN GOTO 2190
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2220
440 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 640
450 IF VERB$ = "CLEAR" OR VERB$ = "RESET" OR VERB$ = "NEW" THEN GOTO 2580
460 IF VERB$ = "SAVE" THEN GOTO 2290
470 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 2360
480 PRINT "DECmail: Unknown command '"; VERB$; "'. Type HELP for syntax."
490 RETURN
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
640 NUM_MSGS% = 4% \ CURR_MSG% = 1% \ CURR_FOLD$ = "ALL" \ M_FROM$(1%) = "KEN.OLSEN@DEC" \ M_TO$(1%) = "ALL" \ M_DATE$(1%) = "12-OCT-1981"
650 M_SUBJ$(1%) = "Welcome to Digital Equipment Corporation" \ M_STAT$(1%) = "R" \ M_FOLD$(1%) = "MAIL"
660 M_BODY$(1%) = "Welcome to Digital. Innovation, quality, and commitment~to our customers define our mission.~Ken Olsen"
670 M_FROM$(2%) = "VMS.DEV@DEC" \ M_TO$(2%) = "ALL" \ M_DATE$(2%) = "14-OCT-1981" \ M_SUBJ$(2%) = "VAX/VMS V3.0 Field Test Announcement" \ M_STAT$(2%) = "U" \ M_FOLD$(2%) = "NEWMAIL"
680 M_BODY$(2%) = "Field test for VAX/VMS V3.0 has begun. Report issues via~DECmail to VMS.DEV. Thank you."
690 M_FROM$(3%) = "PDP11.SYS@DEC" \ M_TO$(3%) = "OPERATOR" \ M_DATE$(3%) = "15-OCT-1981" \ M_SUBJ$(3%) = "RSTS/E Nightly Backup Complete" \ M_STAT$(3%) = "U" \ M_FOLD$(3%) = "NEWMAIL"
700 M_BODY$(3%) = "Nightly disk backup completed with zero errors on drive DB0:.~System online and healthy."
710 M_FROM$(4%) = "ALL-IN-1@DEC" \ M_TO$(4%) = "STAFF" \ M_DATE$(4%) = "16-OCT-1981" \ M_SUBJ$(4%) = "ALL-IN-1 Office System Update" \ M_STAT$(4%) = "D" \ M_FOLD$(4%) = "WASTEBASKET"
720 M_BODY$(4%) = "DECmail integration with ALL-IN-1 document processing and~calendar system is now active across all engineering sites."
730 PRINT "[Sample DECmail mailbox loaded - 4 messages]" \ GOTO 490
740 F_REQ$ = CURR_FOLD$
750 IF ARGS$ = "" THEN GOTO 770
760 U_IN$ = ARGS$ \ GOSUB 580 \ F_REQ$ = U_OUT$
770 PRINT EQU$ \ PRINT "  DECmail Folder: "; F_REQ$ \ PRINT EQU$ \ PRINT "#   St  From                 Date         Subject" \ PRINT SEP$
780 IF NUM_MSGS% = 0% THEN GOTO 900
790 DI% = 1% \ MATCH_CNT% = 0%
800 IF DI% > NUM_MSGS% THEN GOTO 910
810 IF F_REQ$ = "ALL" THEN GOTO 840
820 IF M_FOLD$(DI%) = F_REQ$ THEN GOTO 840
830 GOTO 890
840 MATCH_CNT% = MATCH_CNT% + 1% \ IDX_STR$ = STR$(DI%) \ T_IN$ = IDX_STR$ \ GOSUB 500 \ IDX_PAD$ = LEFT$(T_OUT$ + "    ", 4%) \ ST_CH$ = " "
850 IF M_STAT$(DI%) = "U" THEN ST_CH$ = "*"
860 IF M_STAT$(DI%) = "R" THEN ST_CH$ = " "
870 IF M_STAT$(DI%) = "D" THEN ST_CH$ = "D"
880 FROM_PAD$ = LEFT$(M_FROM$(DI%) + BLANKS$, 20%) \ DATE_PAD$ = LEFT$(M_DATE$(DI%) + BLANKS$, 12%) \ PRINT IDX_PAD$; ST_CH$; "  "; FROM_PAD$; " "; DATE_PAD$; " "; M_SUBJ$(DI%)
890 DI% = DI% + 1% \ GOTO 800
900 PRINT "    [No messages in mailbox]"
910 PRINT SEP$ \ PRINT "  "; MATCH_CNT%; " messages listed (* = Unread, D = Deleted)" \ PRINT EQU$ \ GOTO 490
920 IF NUM_MSGS% = 0% THEN GOTO 2670
930 IF ARGS$ <> "" THEN GOTO 970
940 REQ_M% = CURR_MSG% + 1%
950 IF REQ_M% > NUM_MSGS% THEN REQ_M% = 1%
960 GOTO 980
970 REQ_M% = VAL(ARGS$)
980 IF REQ_M% < 1% THEN GOTO 2680
990 IF REQ_M% > NUM_MSGS% THEN GOTO 2680
1000 CURR_MSG% = REQ_M%
1010 IF M_STAT$(REQ_M%) = "U" THEN M_STAT$(REQ_M%) = "R"
1020 IF M_FOLD$(REQ_M%) = "NEWMAIL" THEN M_FOLD$(REQ_M%) = "MAIL"
1030 PRINT EQU$ \ PRINT "Message "; REQ_M%; " ("; M_DATE$(REQ_M%); ") - Folder: "; M_FOLD$(REQ_M%) \ PRINT "From:    "; M_FROM$(REQ_M%) \ PRINT "To:      "; M_TO$(REQ_M%)
1040 PRINT "Subject: "; M_SUBJ$(REQ_M%) \ PRINT SEP$ \ B_REM$ = M_BODY$(REQ_M%)
1050 IF B_REM$ = "" THEN GOTO 1100
1060 T_P% = INSTR(1%, B_REM$, "~")
1070 IF T_P% = 0% THEN GOTO 1090
1080 B_LINE$ = LEFT$(B_REM$, T_P% - 1%) \ PRINT B_LINE$ \ B_REM$ = MID$(B_REM$, T_P% + 1%, LEN(B_REM$) - T_P%) \ GOTO 1050
1090 PRINT B_REM$
1100 PRINT EQU$ \ GOTO 490
1110 S_TO$ = "" \ S_SUBJ$ = "" \ S_BODY$ = ""
1120 IF ARGS$ = "" THEN GOTO 1240
1130 C1% = INSTR(1%, ARGS$, ",")
1140 IF C1% = 0% THEN GOTO 1190
1150 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ S_TO$ = T_OUT$ \ REM_A$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM_A$, ",")
1160 IF C2% = 0% THEN GOTO 1180
1170 T_IN$ = LEFT$(REM_A$, C2% - 1%) \ GOSUB 500 \ S_SUBJ$ = T_OUT$ \ T_IN$ = MID$(REM_A$, C2% + 1%, LEN(REM_A$) - C2%) \ GOSUB 500 \ S_BODY$ = T_OUT$ \ GOTO 1310
1180 T_IN$ = REM_A$ \ GOSUB 500 \ S_SUBJ$ = T_OUT$ \ S_BODY$ = "No message body provided." \ GOTO 1310
1190 SP% = INSTR(1%, ARGS$, " ")
1200 IF SP% = 0% THEN GOTO 1230
1210 T_IN$ = LEFT$(ARGS$, SP% - 1%) \ GOSUB 500 \ S_TO$ = T_OUT$ \ T_IN$ = MID$(ARGS$, SP% + 1%, LEN(ARGS$) - SP%) \ GOSUB 500 \ S_SUBJ$ = T_OUT$
1220 S_BODY$ = "No message body provided." \ GOTO 1310
1230 S_TO$ = ARGS$ \ S_SUBJ$ = "General Message" \ S_BODY$ = "No message body provided." \ GOTO 1310
1240 PRINT "To: "; \ LINE INPUT S_TO$ \ T_IN$ = S_TO$ \ GOSUB 500 \ S_TO$ = T_OUT$
1250 IF S_TO$ = "" THEN GOTO 490
1260 PRINT "Subject: "; \ LINE INPUT S_SUBJ$ \ T_IN$ = S_SUBJ$ \ GOSUB 500 \ S_SUBJ$ = T_OUT$ \ PRINT "Enter message text (end with . on a blank line):" \ S_BODY$ = ""
1270 LINE INPUT T_INP$
1280 IF T_INP$ = "." THEN GOTO 1310
1290 IF S_BODY$ <> "" THEN S_BODY$ = S_BODY$ + "~"
1300 S_BODY$ = S_BODY$ + T_INP$ \ GOTO 1270
1310 QCH$ = CHR$(34%) \ QL% = LEN(S_TO$)
1320 IF QL% < 2% THEN GOTO 1350
1330 IF LEFT$(S_TO$, 1%) <> QCH$ THEN GOTO 1350
1340 IF RIGHT$(S_TO$, QL%) = QCH$ THEN S_TO$ = MID$(S_TO$, 2%, QL% - 2%)
1350 QL% = LEN(S_SUBJ$)
1360 IF QL% < 2% THEN GOTO 1390
1370 IF LEFT$(S_SUBJ$, 1%) <> QCH$ THEN GOTO 1390
1380 IF RIGHT$(S_SUBJ$, QL%) = QCH$ THEN S_SUBJ$ = MID$(S_SUBJ$, 2%, QL% - 2%)
1390 QL% = LEN(S_BODY$)
1400 IF QL% < 2% THEN GOTO 1430
1410 IF LEFT$(S_BODY$, 1%) <> QCH$ THEN GOTO 1430
1420 IF RIGHT$(S_BODY$, QL%) = QCH$ THEN S_BODY$ = MID$(S_BODY$, 2%, QL% - 2%)
1430 IF NUM_MSGS% >= 50% THEN GOTO 2690
1440 NUM_MSGS% = NUM_MSGS% + 1% \ M_FROM$(NUM_MSGS%) = CURR_USER$ \ M_TO$(NUM_MSGS%)   = S_TO$ \ M_DATE$(NUM_MSGS%) = "16-OCT-1981" \ M_SUBJ$(NUM_MSGS%) = S_SUBJ$
1450 M_BODY$(NUM_MSGS%) = S_BODY$ \ M_STAT$(NUM_MSGS%) = "U" \ M_FOLD$(NUM_MSGS%) = "NEWMAIL" \ CURR_MSG% = NUM_MSGS% \ PRINT "[Message "; NUM_MSGS%; " sent to "; S_TO$; "]"
1460 GOTO 490
1470 IF NUM_MSGS% = 0% THEN GOTO 2670
1480 REQ_M% = CURR_MSG%
1490 IF REQ_M% < 1% THEN REQ_M% = 1%
1500 IF REQ_M% > NUM_MSGS% THEN REQ_M% = NUM_MSGS%
1510 S_TO$ = M_FROM$(REQ_M%) \ S_SUBJ$ = "RE: " + M_SUBJ$(REQ_M%)
1520 IF ARGS$ = "" THEN GOTO 1540
1530 S_BODY$ = ARGS$ \ GOTO 1590
1540 PRINT "Replying to "; S_TO$; " on: "; S_SUBJ$ \ PRINT "Enter reply text (end with . on a blank line):" \ S_BODY$ = ""
1550 LINE INPUT T_INP$
1560 IF T_INP$ = "." THEN GOTO 1590
1570 IF S_BODY$ <> "" THEN S_BODY$ = S_BODY$ + "~"
1580 S_BODY$ = S_BODY$ + T_INP$ \ GOTO 1550
1590 QCH$ = CHR$(34%) \ QL% = LEN(S_BODY$)
1600 IF QL% < 2% THEN GOTO 1630
1610 IF LEFT$(S_BODY$, 1%) <> QCH$ THEN GOTO 1630
1620 IF RIGHT$(S_BODY$, QL%) = QCH$ THEN S_BODY$ = MID$(S_BODY$, 2%, QL% - 2%)
1630 IF NUM_MSGS% >= 50% THEN GOTO 2690
1640 NUM_MSGS% = NUM_MSGS% + 1% \ M_FROM$(NUM_MSGS%) = CURR_USER$ \ M_TO$(NUM_MSGS%)   = S_TO$ \ M_DATE$(NUM_MSGS%) = "16-OCT-1981" \ M_SUBJ$(NUM_MSGS%) = S_SUBJ$
1650 M_BODY$(NUM_MSGS%) = S_BODY$ \ M_STAT$(NUM_MSGS%) = "U" \ M_FOLD$(NUM_MSGS%) = "NEWMAIL" \ CURR_MSG% = NUM_MSGS% \ PRINT "[Reply sent to "; S_TO$; "]" \ GOTO 490
1660 IF NUM_MSGS% = 0% THEN GOTO 2670
1670 IF ARGS$ = "" THEN GOTO 1790
1680 QCH$ = CHR$(34%) \ QL% = LEN(ARGS$)
1690 IF QL% < 2% THEN GOTO 1720
1700 IF LEFT$(ARGS$, 1%) <> QCH$ THEN GOTO 1720
1710 IF RIGHT$(ARGS$, QL%) = QCH$ THEN ARGS$ = MID$(ARGS$, 2%, QL% - 2%)
1720 REQ_M% = CURR_MSG%
1730 IF REQ_M% < 1% THEN REQ_M% = 1%
1740 IF REQ_M% > NUM_MSGS% THEN REQ_M% = NUM_MSGS%
1750 IF NUM_MSGS% >= 50% THEN GOTO 2690
1760 NUM_MSGS% = NUM_MSGS% + 1% \ M_FROM$(NUM_MSGS%) = CURR_USER$ \ M_TO$(NUM_MSGS%)   = ARGS$ \ M_DATE$(NUM_MSGS%) = "16-OCT-1981" \ M_SUBJ$(NUM_MSGS%) = "FWD: " + M_SUBJ$(REQ_M%)
1770 M_BODY$(NUM_MSGS%) = "--- Forwarded Message ---~" + M_BODY$(REQ_M%) \ M_STAT$(NUM_MSGS%) = "U" \ M_FOLD$(NUM_MSGS%) = "NEWMAIL" \ CURR_MSG% = NUM_MSGS%
1780 PRINT "[Message "; REQ_M%; " forwarded to "; ARGS$; "]" \ GOTO 490
1790 PRINT "DECmail: Specify recipient (FORWARD <user>)" \ GOTO 490
1800 IF NUM_MSGS% = 0% THEN GOTO 2670
1810 REQ_M% = CURR_MSG%
1820 IF ARGS$ = "" THEN GOTO 1840
1830 REQ_M% = VAL(ARGS$)
1840 IF REQ_M% < 1% THEN GOTO 2680
1850 IF REQ_M% > NUM_MSGS% THEN GOTO 2680
1860 M_STAT$(REQ_M%) = "D" \ M_FOLD$(REQ_M%) = "WASTEBASKET" \ PRINT "[Message "; REQ_M%; " marked deleted (moved to WASTEBASKET)]" \ GOTO 490
1870 IF NUM_MSGS% = 0% THEN GOTO 2670
1880 P_CNT% = 0% \ KEEP_CNT% = 0% \ PI% = 1%
1890 IF PI% > NUM_MSGS% THEN GOTO 1980
1900 IF M_STAT$(PI%) = "D" THEN GOTO 1960
1910 IF M_FOLD$(PI%) = "WASTEBASKET" THEN GOTO 1960
1920 KEEP_CNT% = KEEP_CNT% + 1%
1930 IF KEEP_CNT% = PI% THEN GOTO 1970
1940 M_FROM$(KEEP_CNT%) = M_FROM$(PI%) \ M_TO$(KEEP_CNT%)   = M_TO$(PI%) \ M_DATE$(KEEP_CNT%) = M_DATE$(PI%) \ M_SUBJ$(KEEP_CNT%) = M_SUBJ$(PI%) \ M_STAT$(KEEP_CNT%) = M_STAT$(PI%)
1950 M_FOLD$(KEEP_CNT%) = M_FOLD$(PI%) \ M_BODY$(KEEP_CNT%) = M_BODY$(PI%) \ GOTO 1970
1960 P_CNT% = P_CNT% + 1%
1970 PI% = PI% + 1% \ GOTO 1890
1980 NUM_MSGS% = KEEP_CNT%
1990 IF CURR_MSG% > NUM_MSGS% THEN CURR_MSG% = NUM_MSGS%
2000 IF CURR_MSG% < 1% THEN CURR_MSG% = 1%
2010 PRINT "[Mailbox purged - "; P_CNT%; " deleted messages removed]" \ GOTO 490
2020 IF NUM_MSGS% = 0% THEN GOTO 2670
2030 IF ARGS$ = "" THEN GOTO 2180
2040 SP% = INSTR(1%, ARGS$, " ")
2050 IF SP% = 0% THEN GOTO 2070
2060 EXT_FILE$ = LEFT$(ARGS$, SP% - 1%) \ REQ_M% = VAL(MID$(ARGS$, SP% + 1%, LEN(ARGS$) - SP%)) \ GOTO 2080
2070 EXT_FILE$ = ARGS$ \ REQ_M% = CURR_MSG%
2080 IF REQ_M% < 1% THEN GOTO 2680
2090 IF REQ_M% > NUM_MSGS% THEN GOTO 2680
2100 OPEN EXT_FILE$ FOR OUTPUT AS FILE #2% \ PRINT #2%, EQU$ \ PRINT #2%, "Message "; REQ_M%; " ("; M_DATE$(REQ_M%); ") - Folder: "; M_FOLD$(REQ_M%)
2110 PRINT #2%, "From:    "; M_FROM$(REQ_M%) \ PRINT #2%, "To:      "; M_TO$(REQ_M%) \ PRINT #2%, "Subject: "; M_SUBJ$(REQ_M%) \ PRINT #2%, SEP$ \ B_REM$ = M_BODY$(REQ_M%)
2120 IF B_REM$ = "" THEN GOTO 2170
2130 T_P% = INSTR(1%, B_REM$, "~")
2140 IF T_P% = 0% THEN GOTO 2160
2150 B_LINE$ = LEFT$(B_REM$, T_P% - 1%) \ PRINT #2%, B_LINE$ \ B_REM$ = MID$(B_REM$, T_P% + 1%, LEN(B_REM$) - T_P%) \ GOTO 2120
2160 PRINT #2%, B_REM$
2170 PRINT #2%, EQU$ \ CLOSE #2% \ PRINT "[Message "; REQ_M%; " extracted to "; EXT_FILE$; "]" \ GOTO 490
2180 PRINT "DECmail: Specify output filename (EXTRACT <file> [msg#])" \ GOTO 490
2190 IF ARGS$ = "" THEN GOTO 2210
2200 U_IN$ = ARGS$ \ GOSUB 580 \ CURR_FOLD$ = U_OUT$ \ PRINT "[Active folder set to "; CURR_FOLD$; "]" \ GOTO 490
2210 CURR_FOLD$ = "ALL" \ PRINT "[Active folder set to ALL]" \ GOTO 490
2220 U_IN$ = ARGS$ \ GOSUB 580 \ S_ARG$ = U_OUT$ \ UNREAD% = 0% \ DEL_CNT% = 0% \ SI% = 1%
2230 IF SI% > NUM_MSGS% THEN GOTO 2270
2240 IF M_STAT$(SI%) = "U" THEN UNREAD% = UNREAD% + 1%
2250 IF M_STAT$(SI%) = "D" THEN DEL_CNT% = DEL_CNT% + 1%
2260 SI% = SI% + 1% \ GOTO 2230
2270 PRINT "DECmail Status:" \ PRINT "  Active Folder:  "; CURR_FOLD$ \ PRINT "  Current User:   "; CURR_USER$ \ PRINT "  Current Msg:    "; CURR_MSG%
2280 PRINT "  Total Messages: "; NUM_MSGS% \ PRINT "  Unread:         "; UNREAD% \ PRINT "  Deleted:        "; DEL_CNT% \ GOTO 490
2290 IF NUM_MSGS% = 0% THEN GOTO 2670
2300 SV_FILE$ = MAIL_FILE$
2310 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
2320 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
2330 IF SI% > NUM_MSGS% THEN GOTO 2350
2340 PRINT #2%, M_FROM$(SI%); "|"; M_TO$(SI%); "|"; M_DATE$(SI%); "|"; M_SUBJ$(SI%); "|"; M_STAT$(SI%); "|"; M_FOLD$(SI%); "|"; M_BODY$(SI%) \ SI% = SI% + 1% \ GOTO 2330
2350 CLOSE #2% \ PRINT "["; NUM_MSGS%; " messages saved to "; SV_FILE$; "]" \ GOTO 490
2360 LD_FILE$ = MAIL_FILE$
2370 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
2380 ON ERROR GOTO 2560 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_MSGS% = 0%
2390 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
2400 IF T_OUT$ = "" THEN GOTO 2390
2410 IF NUM_MSGS% >= 50% THEN GOTO 2560
2420 P1% = INSTR(1%, T_OUT$, "|")
2430 IF P1% = 0% THEN GOTO 2390
2440 F_FROM$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
2450 IF P2% = 0% THEN GOTO 2390
2460 F_TO$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
2470 IF P3% = 0% THEN GOTO 2390
2480 F_DATE$ = LEFT$(REM2$, P3% - 1%) \ REM3$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ P4% = INSTR(1%, REM3$, "|")
2490 IF P4% = 0% THEN GOTO 2390
2500 F_SUBJ$ = LEFT$(REM3$, P4% - 1%) \ REM4$ = MID$(REM3$, P4% + 1%, LEN(REM3$) - P4%) \ P5% = INSTR(1%, REM4$, "|")
2510 IF P5% = 0% THEN GOTO 2390
2520 F_STAT$ = LEFT$(REM4$, P5% - 1%) \ REM5$ = MID$(REM4$, P5% + 1%, LEN(REM4$) - P5%) \ P6% = INSTR(1%, REM5$, "|")
2530 IF P6% = 0% THEN GOTO 2390
2540 F_FOLD$ = LEFT$(REM5$, P6% - 1%) \ F_BODY$ = MID$(REM5$, P6% + 1%, LEN(REM5$) - P6%) \ NUM_MSGS% = NUM_MSGS% + 1% \ M_FROM$(NUM_MSGS%) = F_FROM$ \ M_TO$(NUM_MSGS%)   = F_TO$
2550 M_DATE$(NUM_MSGS%) = F_DATE$ \ M_SUBJ$(NUM_MSGS%) = F_SUBJ$ \ M_STAT$(NUM_MSGS%) = F_STAT$ \ M_FOLD$(NUM_MSGS%) = F_FOLD$ \ M_BODY$(NUM_MSGS%) = F_BODY$ \ GOTO 2390
2560 CLOSE #2% \ RESUME 2570
2570 ON ERROR GOTO 0 \ CURR_MSG% = 1% \ PRINT "["; NUM_MSGS%; " messages loaded from "; LD_FILE$; "]" \ GOTO 490
2580 NUM_MSGS% = 0% \ CURR_MSG% = 1% \ CURR_FOLD$ = "ALL" \ PRINT "[Mailbox cleared]" \ GOTO 490
2590 PRINT EQU$ \ PRINT "    DECmail Electronic Messaging Commands" \ PRINT EQU$ \ PRINT "  DIR [folder]                     List message headers in folder"
2600 PRINT "  READ [msg#]                      Display message header and body" \ PRINT "  SEND <to>, <subj>, <body>        Compose and dispatch new message"
2610 PRINT "  REPLY [text]                     Reply to current message" \ PRINT "  FORWARD <to>                     Forward current message to another user"
2620 PRINT "  DELETE [msg#]                    Mark message as deleted (WASTEBASKET)" \ PRINT "  PURGE                            Permanently delete discarded messages"
2630 PRINT "  EXTRACT <file> [msg#]            Extract message to a disk file" \ PRINT "  SELECT <folder>                  Switch active folder (MAIL/NEWMAIL/ALL)"
2640 PRINT "  SHOW [STATUS]                    Display mailbox status summary" \ PRINT "  SAMPLE / DEMO                    Load DEC historical sample messages"
2650 PRINT "  SAVE [file] / LOAD [file]        Save or load mailbox data file" \ PRINT "  CLEAR / RESET                    Clear active messages from memory"
2660 PRINT "  EXIT / QUIT / BYE                Exit DECmail session" \ PRINT EQU$ \ GOTO 490
2670 PRINT "DECmail: No messages in mailbox. Use SAMPLE or SEND." \ GOTO 490
2680 PRINT "DECmail: Message number out of range (1 to "; NUM_MSGS%; ")" \ GOTO 490
2690 PRINT "DECmail: Mailbox is full (maximum 50 messages)" \ GOTO 490
2700 END
