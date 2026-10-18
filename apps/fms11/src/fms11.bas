10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM FM_NAME$(15%) \ DIM FM_TITLE$(15%) \ DIM FM_DATE$(15%) \ DIM FM_STAT$(15%)
20 DIM FL_FORM%(40%) \ DIM FL_NAME$(40%) \ DIM FL_LABEL$(40%) \ DIM FL_ROW%(40%) \ DIM FL_LEN%(40%) \ DIM FL_TYPE$(40%) \ DIM FL_VAL$(40%)
30 NUM_FORMS% = 0% \ CURR_FORM% = 1% \ NUM_FLDS% = 0% \ TERM_MODE$ = "VT100-FDV" \ FLB_FILE$ = "FMS.FLB"
40 BLANKS$ = "                                                                                " \ USCORE$ = "________________________________________"
50 SEP$    = "--------------------------------------------------------------------------------"
60 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
70 IF CMD_LINE$ = "" THEN GOTO 90
80 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 180
90 PRINT EQU$ \ PRINT "    FMS-11 V2.0 - DEC Forms Management System (FED / FLB / FUT / FDV)" \ PRINT "    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / RSX-11M / VAX" \ PRINT EQU$
100 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
110 PRINT "FMS> "; \ LINE INPUT RAW_INPUT$
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
360 IF VERB$ = "DIR" OR VERB$ = "FLB" OR VERB$ = "FORMS" THEN GOTO 960
370 IF VERB$ = "SELECT" OR VERB$ = "FORM" THEN GOTO 1130
380 IF VERB$ = "CREATE" OR VERB$ = "NEWFORM" THEN GOTO 1250
390 IF VERB$ = "ADDFIELD" OR VERB$ = "FIELD" THEN GOTO 1370
400 IF VERB$ = "FIELDS" OR VERB$ = "DESCRIBE" OR VERB$ = "FUT" THEN GOTO 1540
410 IF VERB$ = "PUT" OR VERB$ = "SET" OR VERB$ = "FILL" THEN GOTO 1700
420 IF VERB$ = "GET" THEN GOTO 1860
430 IF VERB$ = "CLEARFORM" OR VERB$ = "RESETFORM" THEN GOTO 1980
440 IF VERB$ = "VALIDATE" OR VERB$ = "CHECK" THEN GOTO 2070
450 IF VERB$ = "DISPLAY" OR VERB$ = "RENDER" OR VERB$ = "PRINT" OR VERB$ = "EXPORT" THEN GOTO 2280
460 IF VERB$ = "DELETE" OR VERB$ = "DEL" THEN GOTO 2640
470 IF VERB$ = "PURGE" THEN GOTO 2710
480 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2880
484 IF VERB$ = "SAVE" THEN GOTO 2970
488 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3060
490 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3205
494 PRINT "FMS-11: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
650 F_CNT% = 0% \ CI% = 1%
655 IF CI% > NUM_FLDS% THEN GOTO 675
660 IF FL_FORM%(CI%) = CF_IDX% THEN F_CNT% = F_CNT% + 1%
665 CI% = CI% + 1% \ GOTO 655
675 RETURN
700 NUM_FORMS% = 4% \ CURR_FORM% = 1% \ NUM_FLDS% = 10%
710 FM_NAME$(1%) = "ORDER_ENTRY" \ FM_TITLE$(1%) = "DEC COMMERCIAL ORDER ENTRY SCREEN" \ FM_DATE$(1%) = "22-OCT-1982" \ FM_STAT$(1%) = "A"
720 FM_NAME$(2%) = "EMP_RECORD" \ FM_TITLE$(2%) = "DEC PERSONNEL MASTER MAINTENANCE" \ FM_DATE$(2%) = "23-OCT-1982" \ FM_STAT$(2%) = "A"
730 FM_NAME$(3%) = "RSTS_LOGON" \ FM_TITLE$(3%) = "RSTS/E V8.0 TERMINAL LOGON FORM" \ FM_DATE$(3%) = "24-OCT-1982" \ FM_STAT$(3%) = "A"
740 FM_NAME$(4%) = "OLD_INVOICE" \ FM_TITLE$(4%) = "OBSOLETE VT52 INVOICE FORM" \ FM_DATE$(4%) = "10-OCT-1982" \ FM_STAT$(4%) = "D"
750 FL_FORM%(1%) = 1% \ FL_NAME$(1%) = "ORDER_NO" \ FL_LABEL$(1%) = "Order Number" \ FL_ROW%(1%) = 4% \ FL_LEN%(1%) = 8% \ FL_TYPE$(1%) = "NUMERIC" \ FL_VAL$(1%) = "10042"
760 FL_FORM%(2%) = 1% \ FL_NAME$(2%) = "CUST_NAME" \ FL_LABEL$(2%) = "Customer Name" \ FL_ROW%(2%) = 6% \ FL_LEN%(2%) = 24% \ FL_TYPE$(2%) = "ALPHA" \ FL_VAL$(2%) = "MIT Lincoln Laboratory"
770 FL_FORM%(3%) = 1% \ FL_NAME$(3%) = "PART_SKU" \ FL_LABEL$(3%) = "DEC System SKU" \ FL_ROW%(3%) = 8% \ FL_LEN%(3%) = 12% \ FL_TYPE$(3%) = "ALPHA" \ FL_VAL$(3%) = "PDP-11/70"
780 FL_FORM%(4%) = 1% \ FL_NAME$(4%) = "QUANTITY" \ FL_LABEL$(4%) = "Order Quantity" \ FL_ROW%(4%) = 10% \ FL_LEN%(4%) = 6% \ FL_TYPE$(4%) = "NUMERIC" \ FL_VAL$(4%) = "2"
790 FL_FORM%(5%) = 1% \ FL_NAME$(5%) = "STATUS" \ FL_LABEL$(5%) = "Order Status" \ FL_ROW%(5%) = 12% \ FL_LEN%(5%) = 12% \ FL_TYPE$(5%) = "PROTECTED" \ FL_VAL$(5%) = "APPROVED"
800 FL_FORM%(6%) = 2% \ FL_NAME$(6%) = "EMP_ID" \ FL_LABEL$(6%) = "Badge Number" \ FL_ROW%(6%) = 4% \ FL_LEN%(6%) = 6% \ FL_TYPE$(6%) = "NUMERIC" \ FL_VAL$(6%) = "4821"
810 FL_FORM%(7%) = 2% \ FL_NAME$(7%) = "FULL_NAME" \ FL_LABEL$(7%) = "Employee Name" \ FL_ROW%(7%) = 6% \ FL_LEN%(7%) = 24% \ FL_TYPE$(7%) = "ALPHA" \ FL_VAL$(7%) = "Gordon Bell"
820 FL_FORM%(8%) = 2% \ FL_NAME$(8%) = "DEPT_CODE" \ FL_LABEL$(8%) = "Department" \ FL_ROW%(8%) = 8% \ FL_LEN%(8%) = 16% \ FL_TYPE$(8%) = "ALPHA" \ FL_VAL$(8%) = "VAX Engineering"
830 FL_FORM%(9%) = 3% \ FL_NAME$(9%) = "ACCOUNT" \ FL_LABEL$(9%) = "PPN Account" \ FL_ROW%(9%) = 5% \ FL_LEN%(9%) = 10% \ FL_TYPE$(9%) = "ALPHA" \ FL_VAL$(9%) = "[1,2]"
840 FL_FORM%(10%) = 3% \ FL_NAME$(10%) = "TERMINAL" \ FL_LABEL$(10%) = "Terminal Line" \ FL_ROW%(10%) = 7% \ FL_LEN%(10%) = 10% \ FL_TYPE$(10%) = "PROTECTED" \ FL_VAL$(10%) = "KB0:VT100"
850 PRINT "[Sample FMS-11 Form Library loaded - 4 forms, 10 field definitions]" \ GOTO 495
960 IF NUM_FORMS% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  FMS-11 Form Library Directory (FLB) - Library: "; FLB_FILE$ \ PRINT EQU$ \ PRINT "#   St  Form Name        Fields   Date          Screen Title" \ PRINT SEP$
980 DI% = 1%
990 IF DI% > NUM_FORMS% THEN GOTO 1100
1000 CF_IDX% = DI% \ GOSUB 650 \ IDX_S$ = STR$(DI%) \ T_IN$ = IDX_S$ \ GOSUB 500 \ IPAD$ = LEFT$(T_OUT$ + "    ", 4%) \ ST_C$ = " "
1010 IF DI% = CURR_FORM% THEN ST_C$ = "*"
1020 IF FM_STAT$(DI%) = "D" THEN ST_C$ = "D"
1030 NM_P$ = LEFT$(FM_NAME$(DI%) + BLANKS$, 16%) \ FC_S$ = STR$(F_CNT%) \ T_IN$ = FC_S$ \ GOSUB 500 \ FC_P$ = LEFT$(T_OUT$ + BLANKS$, 8%) \ DT_P$ = LEFT$(FM_DATE$(DI%) + BLANKS$, 13%)
1040 PRINT IPAD$; ST_C$; "  "; NM_P$; " "; FC_P$; " "; DT_P$; " "; FM_TITLE$(DI%) \ DI% = DI% + 1% \ GOTO 990
1100 PRINT SEP$ \ PRINT "  "; NUM_FORMS%; " form(s) in library (* = Active, D = Deleted)" \ PRINT EQU$ \ GOTO 495
1130 IF NUM_FORMS% = 0% THEN GOTO 3370
1140 IF ARGS$ = "" THEN GOTO 1220
1150 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ S_KEY$ = U_OUT$ \ REQ_F% = VAL(S_KEY$)
1160 IF REQ_F% >= 1% AND REQ_F% <= NUM_FORMS% THEN GOTO 1210
1170 REQ_F% = 0% \ SI% = 1%
1180 IF SI% > NUM_FORMS% THEN GOTO 1205
1190 IF FM_NAME$(SI%) = S_KEY$ THEN REQ_F% = SI%
1200 SI% = SI% + 1% \ GOTO 1180
1205 IF REQ_F% = 0% THEN GOTO 3380
1210 CURR_FORM% = REQ_F% \ CF_IDX% = CURR_FORM% \ GOSUB 650
1220 PRINT "[Active form set to #"; CURR_FORM%; ": "; FM_NAME$(CURR_FORM%); " - "; FM_TITLE$(CURR_FORM%); " ("; F_CNT%; " fields)]" \ GOTO 495
1250 IF NUM_FORMS% >= 15% THEN GOTO 3390
1260 IF ARGS$ = "" THEN GOTO 1350
1270 C1% = INSTR(1%, ARGS$, ",")
1280 IF C1% = 0% THEN GOTO 1310
1290 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ N_FNM$ = U_OUT$ \ Q_IN$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ GOSUB 635 \ N_FTIT$ = Q_OUT$ \ GOTO 1320
1310 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ N_FNM$ = U_OUT$ \ N_FTIT$ = N_FNM$ + " SCREEN FORM"
1320 NUM_FORMS% = NUM_FORMS% + 1% \ CURR_FORM% = NUM_FORMS% \ FM_NAME$(CURR_FORM%) = N_FNM$ \ FM_TITLE$(CURR_FORM%) = N_FTIT$
1330 FM_DATE$(CURR_FORM%) = "25-OCT-1982" \ FM_STAT$(CURR_FORM%) = "A"
1340 PRINT "[Form #"; CURR_FORM%; " created: "; N_FNM$; " ("; N_FTIT$; ")]" \ GOTO 495
1350 PRINT "FMS-11: Syntax is CREATE <form_name>, <screen_title>" \ GOTO 495
1370 IF NUM_FORMS% = 0% THEN GOTO 3370
1380 IF NUM_FLDS% >= 40% THEN GOTO 3390
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1520
1410 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ F_NM$ = U_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1420 IF C2% = 0% THEN GOTO 1520
1430 Q_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 635 \ F_LB$ = Q_OUT$ \ REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1440 IF C3% = 0% THEN GOTO 1520
1450 F_RW% = VAL(LEFT$(REM2$, C3% - 1%)) \ REM3$ = MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%) \ C4% = INSTR(1%, REM3$, ",")
1460 IF C4% = 0% THEN GOTO 1520
1470 F_LN% = VAL(LEFT$(REM3$, C4% - 1%)) \ REM4$ = MID$(REM3$, C4% + 1%, LEN(REM3$) - C4%) \ C5% = INSTR(1%, REM4$, ",")
1480 IF C5% = 0% THEN GOTO 1495
1485 Q_IN$ = LEFT$(REM4$, C5% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ F_TP$ = U_OUT$ \ Q_IN$ = MID$(REM4$, C5% + 1%, LEN(REM4$) - C5%) \ GOSUB 635 \ F_VL$ = Q_OUT$ \ GOTO 1500
1495 Q_IN$ = REM4$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ F_TP$ = U_OUT$ \ F_VL$ = ""
1500 NUM_FLDS% = NUM_FLDS% + 1% \ FL_FORM%(NUM_FLDS%) = CURR_FORM% \ FL_NAME$(NUM_FLDS%) = F_NM$ \ FL_LABEL$(NUM_FLDS%) = F_LB$
1505 FL_ROW%(NUM_FLDS%) = F_RW% \ FL_LEN%(NUM_FLDS%) = F_LN% \ FL_TYPE$(NUM_FLDS%) = F_TP$ \ FL_VAL$(NUM_FLDS%) = F_VL$
1510 PRINT "[FED: Field '"; F_NM$; "' added to form "; FM_NAME$(CURR_FORM%); " (Row="; F_RW%; ", Len="; F_LN%; ", Type="; F_TP$; ")]" \ GOTO 495
1520 PRINT "FMS-11: Syntax is ADDFIELD <name>, <label>, <row>, <len>, <type> [, <default>]" \ GOTO 495
1540 IF NUM_FORMS% = 0% THEN GOTO 3370
1550 PRINT EQU$ \ PRINT "  FMS-11 Form Utility (FUT) Field Attribute Table - Form: "; FM_NAME$(CURR_FORM%) \ PRINT "  Title: "; FM_TITLE$(CURR_FORM%) \ PRINT EQU$
1560 PRINT "Field Name      Row   Len   Type        Prompt Label          Current Value" \ PRINT SEP$
1570 FI% = 1% \ M_CNT% = 0%
1580 IF FI% > NUM_FLDS% THEN GOTO 1660
1590 IF FL_FORM%(FI%) <> CURR_FORM% THEN GOTO 1650
1600 M_CNT% = M_CNT% + 1% \ NM_P$ = LEFT$(FL_NAME$(FI%) + BLANKS$, 16%) \ R_S$ = STR$(FL_ROW%(FI%)) \ T_IN$ = R_S$ \ GOSUB 500 \ R_P$ = LEFT$(T_OUT$ + BLANKS$, 6%)
1610 L_S$ = STR$(FL_LEN%(FI%)) \ T_IN$ = L_S$ \ GOSUB 500 \ L_P$ = LEFT$(T_OUT$ + BLANKS$, 6%) \ TP_P$ = LEFT$(FL_TYPE$(FI%) + BLANKS$, 12%) \ LB_P$ = LEFT$(FL_LABEL$(FI%) + BLANKS$, 22%)
1620 PRINT NM_P$; R_P$; L_P$; TP_P$; LB_P$; FL_VAL$(FI%)
1650 FI% = FI% + 1% \ GOTO 1580
1660 PRINT SEP$ \ PRINT "  "; M_CNT%; " field(s) defined in form "; FM_NAME$(CURR_FORM%) \ PRINT EQU$ \ GOTO 495
1700 IF NUM_FORMS% = 0% THEN GOTO 3370
1710 C1% = INSTR(1%, ARGS$, ",")
1720 IF C1% = 0% THEN GOTO 1840
1730 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ P_FNM$ = U_OUT$ \ Q_IN$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ GOSUB 635 \ P_FVL$ = Q_OUT$
1740 F_IDX% = 0% \ FI% = 1%
1750 IF FI% > NUM_FLDS% THEN GOTO 1790
1760 IF FL_FORM%(FI%) <> CURR_FORM% THEN GOTO 1780
1770 IF FL_NAME$(FI%) = P_FNM$ THEN F_IDX% = FI%
1780 FI% = FI% + 1% \ GOTO 1750
1790 IF F_IDX% = 0% THEN GOTO 1845
1800 IF FL_TYPE$(F_IDX%) = "PROTECTED" THEN GOTO 1850
1810 FL_VAL$(F_IDX%) = P_FVL$ \ PRINT "[FDV: Field '"; P_FNM$; "' set to '"; P_FVL$; "']" \ GOTO 495
1840 PRINT "FMS-11: Syntax is PUT <field_name>, <value>" \ GOTO 495
1845 PRINT "FMS-11: Field '"; P_FNM$; "' not found in active form "; FM_NAME$(CURR_FORM%) \ GOTO 495
1850 PRINT "FMS-11: Field '"; P_FNM$; "' is PROTECTED (display-only)" \ GOTO 495
1860 IF NUM_FORMS% = 0% THEN GOTO 3370
1870 IF ARGS$ = "" THEN GOTO 1960
1880 Q_IN$ = ARGS$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ G_FNM$ = U_OUT$ \ F_IDX% = 0% \ FI% = 1%
1890 IF FI% > NUM_FLDS% THEN GOTO 1930
1900 IF FL_FORM%(FI%) <> CURR_FORM% THEN GOTO 1920
1910 IF FL_NAME$(FI%) = G_FNM$ THEN F_IDX% = FI%
1920 FI% = FI% + 1% \ GOTO 1890
1930 IF F_IDX% = 0% THEN GOTO 1965
1940 PRINT "FDV Field "; G_FNM$; " ("; FL_LABEL$(F_IDX%); ") = "; CHR$(34%); FL_VAL$(F_IDX%); CHR$(34%); " [Type: "; FL_TYPE$(F_IDX%); ", Len: "; FL_LEN%(F_IDX%); "]" \ GOTO 495
1960 PRINT "FMS-11: Syntax is GET <field_name>" \ GOTO 495
1965 PRINT "FMS-11: Field '"; G_FNM$; "' not found in active form "; FM_NAME$(CURR_FORM%) \ GOTO 495
1980 IF NUM_FORMS% = 0% THEN GOTO 3370
1990 CL_CNT% = 0% \ FI% = 1%
2000 IF FI% > NUM_FLDS% THEN GOTO 2050
2010 IF FL_FORM%(FI%) <> CURR_FORM% THEN GOTO 2040
2020 IF FL_TYPE$(FI%) = "PROTECTED" THEN GOTO 2040
2030 FL_VAL$(FI%) = "" \ CL_CNT% = CL_CNT% + 1%
2040 FI% = FI% + 1% \ GOTO 2000
2050 PRINT "[FDV: Cleared "; CL_CNT%; " editable field(s) in form "; FM_NAME$(CURR_FORM%); "]" \ GOTO 495
2070 IF NUM_FORMS% = 0% THEN GOTO 3370
2080 V_ERR% = 0% \ V_TOT% = 0% \ FI% = 1%
2090 IF FI% > NUM_FLDS% THEN GOTO 2230
2100 IF FL_FORM%(FI%) <> CURR_FORM% THEN GOTO 2220
2110 V_TOT% = V_TOT% + 1% \ V_VAL$ = FL_VAL$(FI%) \ V_LEN% = LEN(V_VAL$)
2120 IF V_LEN% > 0% THEN GOTO 2150
2130 PRINT "  [ERROR] Field '"; FL_NAME$(FI%); "' is required (currently empty)" \ V_ERR% = V_ERR% + 1% \ GOTO 2220
2150 IF V_LEN% <= FL_LEN%(FI%) THEN GOTO 2180
2160 PRINT "  [ERROR] Field '"; FL_NAME$(FI%); "' exceeds max length ("; FL_LEN%(FI%); ")" \ V_ERR% = V_ERR% + 1% \ GOTO 2220
2180 IF FL_TYPE$(FI%) <> "NUMERIC" THEN GOTO 2220
2190 CH1% = ASCII(LEFT$(V_VAL$, 1%))
2200 IF CH1% >= 48% AND CH1% <= 57% THEN GOTO 2220
2210 PRINT "  [ERROR] Field '"; FL_NAME$(FI%); "' requires NUMERIC digits (got '"; V_VAL$; "')" \ V_ERR% = V_ERR% + 1%
2220 FI% = FI% + 1% \ GOTO 2090
2230 IF V_ERR% > 0% THEN GOTO 2250
2240 PRINT "[FDV Validation PASSED: All "; V_TOT%; " fields in "; FM_NAME$(CURR_FORM%); " are valid]" \ GOTO 495
2250 PRINT "[FDV Validation FAILED: "; V_ERR%; " error(s) found in "; FM_NAME$(CURR_FORM%); "]" \ GOTO 495
2280 IF NUM_FORMS% = 0% THEN GOTO 3370
2290 TO_FILE% = 0% \ OUT_FILE$ = ""
2300 IF VERB$ = "EXPORT" THEN GOTO 2350
2310 IF ARGS$ = "" THEN GOTO 2370
2320 U_IN$ = ARGS$ \ GOSUB 580
2330 IF LEFT$(U_OUT$, 3%) = "ON " THEN GOTO 2360
2340 REQ_F% = VAL(ARGS$)
2342 IF REQ_F% < 1% THEN GOTO 2370
2344 IF REQ_F% > NUM_FORMS% THEN GOTO 2370
2346 CURR_FORM% = REQ_F% \ GOTO 2370
2350 IF ARGS$ = "" THEN GOTO 2620
2355 Q_IN$ = ARGS$ \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1% \ GOTO 2370
2360 Q_IN$ = MID$(ARGS$, 4%, LEN(ARGS$) - 3%) \ GOSUB 635 \ OUT_FILE$ = Q_OUT$ \ TO_FILE% = 1%
2370 IF TO_FILE% = 1% THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #2%
2380 C_TIT$ = FM_TITLE$(CURR_FORM%) \ C_PAD% = (70% - LEN(C_TIT$)) / 2%
2385 IF C_PAD% < 2% THEN C_PAD% = 2%
2390 PAD_C$ = LEFT$(BLANKS$, C_PAD%) \ LBRK$ = "[" \ RBRK$ = "]" \ LANG$ = "<" \ RANG$ = ">"
2400 IF TO_FILE% = 1% THEN GOTO 2420
2410 PRINT EQU$ \ PRINT PAD_C$; C_TIT$; "  ["; FM_NAME$(CURR_FORM%); "]" \ PRINT SEP$ \ GOTO 2430
2420 PRINT #2%, EQU$ \ PRINT #2%, PAD_C$; C_TIT$; "  ["; FM_NAME$(CURR_FORM%); "]" \ PRINT #2%, SEP$
2430 FI% = 1%
2440 IF FI% > NUM_FLDS% THEN GOTO 2560
2450 IF FL_FORM%(FI%) <> CURR_FORM% THEN GOTO 2550
2460 R_S$ = STR$(FL_ROW%(FI%)) \ T_IN$ = R_S$ \ GOSUB 500 \ R_TMP$ = "R" + T_OUT$ \ R_P$ = LEFT$(R_TMP$ + BLANKS$, 5%)
2465 LB_TMP$ = FL_LABEL$(FI%) + ":" \ LB_P$ = LEFT$(LB_TMP$ + BLANKS$, 22%)
2470 V_TXT$ = FL_VAL$(FI%) \ F_W% = FL_LEN%(FI%)
2480 IF LEN(V_TXT$) >= F_W% THEN BOX_IN$ = LEFT$(V_TXT$, F_W%)
2490 IF LEN(V_TXT$) < F_W% THEN BOX_IN$ = V_TXT$ + LEFT$(USCORE$, F_W% - LEN(V_TXT$))
2500 BOX_S$ = LBRK$ + BOX_IN$ + RBRK$
2510 IF FL_TYPE$(FI%) = "PROTECTED" THEN BOX_S$ = LANG$ + V_TXT$ + RANG$
2530 IF TO_FILE% = 0% THEN PRINT "  "; R_P$; "  "; LB_P$; " "; BOX_S$; "   ("; FL_NAME$(FI%); ")"
2540 IF TO_FILE% = 1% THEN PRINT #2%, "  "; R_P$; "  "; LB_P$; " "; BOX_S$; "   ("; FL_NAME$(FI%); ")"
2550 FI% = FI% + 1% \ GOTO 2440
2560 IF TO_FILE% = 1% THEN GOTO 2590
2580 PRINT SEP$ \ PRINT "  [FDV Mode: "; TERM_MODE$; " | Enter=Next Field | Gold+F=Exit Form]" \ PRINT EQU$ \ GOTO 495
2590 PRINT #2%, SEP$ \ PRINT #2%, "  [FDV Mode: "; TERM_MODE$; " | Enter=Next Field | Gold+F=Exit Form]" \ PRINT #2%, EQU$ \ CLOSE #2%
2600 PRINT "[Form "; FM_NAME$(CURR_FORM%); " rendered to "; OUT_FILE$; "]" \ GOTO 495
2620 PRINT "FMS-11: Specify output filename (EXPORT <file> or PRINT ON <file>)" \ GOTO 495
2640 IF NUM_FORMS% = 0% THEN GOTO 3370
2650 REQ_F% = CURR_FORM%
2660 IF ARGS$ <> "" THEN REQ_F% = VAL(ARGS$)
2670 IF REQ_F% < 1% THEN GOTO 3380
2680 IF REQ_F% > NUM_FORMS% THEN GOTO 3380
2690 FM_STAT$(REQ_F%) = "D" \ PRINT "[Form #"; REQ_F%; " ("; FM_NAME$(REQ_F%); ") marked deleted]" \ GOTO 495
2710 IF NUM_FORMS% = 0% THEN GOTO 3370
2720 P_CNT% = 0% \ KEEP_F% = 0% \ PI% = 1%
2730 IF PI% > NUM_FORMS% THEN GOTO 2830
2740 IF FM_STAT$(PI%) = "D" THEN GOTO 2810
2750 KEEP_F% = KEEP_F% + 1%
2760 IF KEEP_F% = PI% THEN GOTO 2820
2770 FM_NAME$(KEEP_F%) = FM_NAME$(PI%) \ FM_TITLE$(KEEP_F%) = FM_TITLE$(PI%) \ FM_DATE$(KEEP_F%) = FM_DATE$(PI%) \ FM_STAT$(KEEP_F%) = FM_STAT$(PI%)
2780 FI% = 1%
2790 IF FI% > NUM_FLDS% THEN GOTO 2820
2800 IF FL_FORM%(FI%) = PI% THEN FL_FORM%(FI%) = KEEP_F%
2805 FI% = FI% + 1% \ GOTO 2790
2810 P_CNT% = P_CNT% + 1%
2820 PI% = PI% + 1% \ GOTO 2730
2830 NUM_FORMS% = KEEP_F%
2840 IF CURR_FORM% > NUM_FORMS% THEN CURR_FORM% = NUM_FORMS%
2850 IF CURR_FORM% < 1% THEN CURR_FORM% = 1%
2860 PRINT "[Form library purged - "; P_CNT%; " deleted form(s) removed]" \ GOTO 495
2880 CF_IDX% = CURR_FORM% \ GOSUB 650 \ DEL_CNT% = 0% \ SI% = 1%
2890 IF SI% > NUM_FORMS% THEN GOTO 2920
2900 IF FM_STAT$(SI%) = "D" THEN DEL_CNT% = DEL_CNT% + 1%
2910 SI% = SI% + 1% \ GOTO 2890
2920 PRINT "FMS-11 System Status:" \ PRINT "  Form Library:    "; FLB_FILE$ \ PRINT "  Terminal Driver: "; TERM_MODE$
2930 IF NUM_FORMS% > 0% THEN PRINT "  Active Form:     #"; CURR_FORM%; " ("; FM_NAME$(CURR_FORM%); " - "; F_CNT%; " fields)"
2940 IF NUM_FORMS% = 0% THEN PRINT "  Active Form:     None"
2950 PRINT "  Total Forms:     "; NUM_FORMS%; " (Deleted: "; DEL_CNT%; ")" \ PRINT "  Total Fields:    "; NUM_FLDS% \ GOTO 495
2970 IF NUM_FORMS% = 0% THEN GOTO 3370
2980 SV_FILE$ = FLB_FILE$
2990 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
3000 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
3010 IF SI% > NUM_FORMS% THEN GOTO 3040
3020 PRINT #2%, FM_NAME$(SI%); "|"; FM_TITLE$(SI%); "|"; FM_DATE$(SI%); "|"; FM_STAT$(SI%) \ SI% = SI% + 1% \ GOTO 3010
3040 CLOSE #2% \ PRINT "["; NUM_FORMS%; " form(s) saved to library "; SV_FILE$; "]" \ GOTO 495
3060 LD_FILE$ = FLB_FILE$
3070 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
3080 ON ERROR GOTO 3180 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_FORMS% = 0%
3090 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
3100 IF T_OUT$ = "" THEN GOTO 3090
3110 P1% = INSTR(1%, T_OUT$, "|")
3120 IF P1% = 0% THEN GOTO 3090
3130 F_NM$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
3140 IF P2% = 0% THEN GOTO 3090
3150 F_TI$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
3160 IF P3% = 0% THEN GOTO 3090
3170 F_DT$ = LEFT$(REM2$, P3% - 1%) \ F_ST$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%) \ NUM_FORMS% = NUM_FORMS% + 1%
3175 FM_NAME$(NUM_FORMS%) = F_NM$ \ FM_TITLE$(NUM_FORMS%) = F_TI$ \ FM_DATE$(NUM_FORMS%) = F_DT$ \ FM_STAT$(NUM_FORMS%) = F_ST$ \ GOTO 3090
3180 CLOSE #2% \ RESUME 3190
3190 ON ERROR GOTO 0 \ CURR_FORM% = 1% \ PRINT "["; NUM_FORMS%; " form(s) loaded from library "; LD_FILE$; "]" \ GOTO 495
3205 NUM_FORMS% = 0% \ CURR_FORM% = 1% \ NUM_FLDS% = 0% \ PRINT "[FMS-11 form library cleared]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "    FMS-11 Forms Management System Commands" \ PRINT EQU$ \ PRINT "  DIR / FLB / FORMS                List forms in Form Library"
3225 PRINT "  SELECT <name_or_#>               Select active form by name or number" \ PRINT "  CREATE <name>, <title>           Create new form definition (FED)"
3230 PRINT "  ADDFIELD <n>,<lbl>,<r>,<l>,<t>   Add field definition to active form (FED)" \ PRINT "  FIELDS / DESCRIBE / FUT          Display Field Attribute Table (FUT)"
3235 PRINT "  PUT <field>, <value>             Set field value in active form (FDV)" \ PRINT "  GET <field>                      Retrieve field value and attributes (FDV)"
3240 PRINT "  CLEARFORM / RESETFORM            Clear editable field values in active form" \ PRINT "  VALIDATE / CHECK                 Validate required & numeric fields (FDV)"
3245 PRINT "  DISPLAY / RENDER / PRINT [ON f]  Render VT100 form to screen or file" \ PRINT "  DELETE [form#] / PURGE           Mark form deleted or purge library"
3250 PRINT "  SAMPLE / SAVE [f] / LOAD [f]     Load DEC demo forms or save/load FLB" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear memory, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "FMS-11: No forms in library. Use SAMPLE or CREATE." \ GOTO 495
3380 PRINT "FMS-11: Form not found or out of range" \ GOTO 495
3390 PRINT "FMS-11: Form or field table is full" \ GOTO 495
3400 END
