10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM G_NUM$(25%) \ DIM G_NAME$(25%) \ DIM G_TYPE$(25%) \ DIM G_BAL%(25%) \ DIM J_DR$(30%) \ DIM J_CR$(30%) \ DIM J_AMT%(30%) \ DIM J_MEMO$(30%)
20 DIM AR_ID$(20%) \ DIM AR_NAME$(20%) \ DIM AR_BAL%(20%) \ DIM AP_ID$(20%) \ DIM AP_NAME$(20%) \ DIM AP_BAL%(20%) \ DIM I_SKU$(20%) \ DIM I_DESC$(20%) \ DIM I_QTY%(20%) \ DIM I_COST%(20%)
30 NUM_GL% = 0% \ NUM_JRN% = 0% \ NUM_AR% = 0% \ NUM_AP% = 0% \ NUM_INV% = 0% \ COMP_NAME$ = "DIGITAL EQUIPMENT CORP - COMMERCIAL DIV" \ PERIOD$ = "FY1982-Q4" \ DIBS_FILE$ = "DIBS.DAT"
40 BLANKS$ = "                                                                                "
50 SEP$    = "--------------------------------------------------------------------------------"
60 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
70 IF CMD_LINE$ = "" THEN GOTO 90
80 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 180
90 PRINT EQU$ \ PRINT "    DIBS V3.0 - DEC Integrated Business & Accounting System (DIBS-11)" \ PRINT "    Digital Equipment Corporation (DEC) PDP-11 / CTS-300 / RSTS/E" \ PRINT EQU$
100 PRINT "Type HELP for commands, or EXIT to quit." \ PRINT ""
110 PRINT "DIBS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" THEN GOTO 750
360 IF VERB$ = "COA" OR VERB$ = "GL" OR VERB$ = "ACCOUNTS" THEN GOTO 960
370 IF VERB$ = "ADDACCT" THEN GOTO 1090
380 IF VERB$ = "POST" OR VERB$ = "JOURNAL" THEN GOTO 1220
390 IF VERB$ = "JRNLIST" OR VERB$ = "REGISTER" THEN GOTO 1360
400 IF VERB$ = "TRIAL" OR VERB$ = "TB" THEN GOTO 1460
410 IF VERB$ = "INCOME" OR VERB$ = "PL" THEN GOTO 1640
420 IF VERB$ = "BALANCE" OR VERB$ = "BS" THEN GOTO 1810
430 IF VERB$ = "AR" OR VERB$ = "ARLIST" THEN GOTO 2020
440 IF VERB$ = "INVOICE" THEN GOTO 2120
450 IF VERB$ = "RECEIVE" OR VERB$ = "CASH" THEN GOTO 2270
455 IF VERB$ = "AP" OR VERB$ = "APLIST" THEN GOTO 2400
460 IF VERB$ = "VOUCHER" THEN GOTO 2500
465 IF VERB$ = "PAY" THEN GOTO 2650
470 IF VERB$ = "INV" OR VERB$ = "INVLIST" THEN GOTO 2780
475 IF VERB$ = "ADDITEM" THEN GOTO 2900
480 IF VERB$ = "REPORT" OR VERB$ = "EXPORT" THEN GOTO 3020
484 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 3170
486 IF VERB$ = "SAVE" THEN GOTO 3290
488 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 3330
490 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 3205
494 PRINT "DIBS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
650 DR_IDX% = 0% \ CR_IDX% = 0% \ GI% = 1%
655 IF GI% > NUM_GL% THEN GOTO 680
660 IF G_NUM$(GI%) = P_DR$ THEN DR_IDX% = GI%
665 IF G_NUM$(GI%) = P_CR$ THEN CR_IDX% = GI%
670 GI% = GI% + 1% \ GOTO 655
680 IF DR_IDX% = 0% THEN GOTO 725
685 IF CR_IDX% = 0% THEN GOTO 725
690 DT$ = G_TYPE$(DR_IDX%)
692 IF DT$ = "ASSET" OR DT$ = "EXP" THEN GOTO 698
694 G_BAL%(DR_IDX%) = G_BAL%(DR_IDX%) - P_AMT% \ GOTO 700
698 G_BAL%(DR_IDX%) = G_BAL%(DR_IDX%) + P_AMT%
700 CT$ = G_TYPE$(CR_IDX%)
702 IF CT$ = "LIAB" OR CT$ = "EQUITY" OR CT$ = "REV" THEN GOTO 708
704 G_BAL%(CR_IDX%) = G_BAL%(CR_IDX%) - P_AMT% \ GOTO 710
708 G_BAL%(CR_IDX%) = G_BAL%(CR_IDX%) + P_AMT%
710 IF NUM_JRN% >= 30% THEN GOTO 720
715 NUM_JRN% = NUM_JRN% + 1% \ J_DR$(NUM_JRN%) = P_DR$ \ J_CR$(NUM_JRN%) = P_CR$ \ J_AMT%(NUM_JRN%) = P_AMT% \ J_MEMO$(NUM_JRN%) = P_MEMO$
720 P_OK% = 1% \ RETURN
725 P_OK% = 0% \ RETURN
750 NUM_GL% = 8% \ G_NUM$(1%) = "1010" \ G_NAME$(1%) = "Cash in Bank" \ G_TYPE$(1%) = "ASSET" \ G_BAL%(1%) = 8500%
760 G_NUM$(2%) = "1100" \ G_NAME$(2%) = "Accounts Receivable" \ G_TYPE$(2%) = "ASSET" \ G_BAL%(2%) = 4500%
770 G_NUM$(3%) = "1200" \ G_NAME$(3%) = "Inventory - DEC Systems" \ G_TYPE$(3%) = "ASSET" \ G_BAL%(3%) = 6000%
780 G_NUM$(4%) = "2010" \ G_NAME$(4%) = "Accounts Payable" \ G_TYPE$(4%) = "LIAB" \ G_BAL%(4%) = 3000%
790 G_NUM$(5%) = "3010" \ G_NAME$(5%) = "Retained Earnings" \ G_TYPE$(5%) = "EQUITY" \ G_BAL%(5%) = 9500%
800 G_NUM$(6%) = "4010" \ G_NAME$(6%) = "Hardware Sales Revenue" \ G_TYPE$(6%) = "REV" \ G_BAL%(6%) = 14000%
810 G_NUM$(7%) = "5010" \ G_NAME$(7%) = "Cost of Goods Sold" \ G_TYPE$(7%) = "EXP" \ G_BAL%(7%) = 5000%
820 G_NUM$(8%) = "5100" \ G_NAME$(8%) = "Engineering & Payroll" \ G_TYPE$(8%) = "EXP" \ G_BAL%(8%) = 2500%
830 NUM_AR% = 3% \ AR_ID$(1%) = "C100" \ AR_NAME$(1%) = "MIT Lincoln Lab" \ AR_BAL%(1%) = 2000%
840 AR_ID$(2%) = "C200" \ AR_NAME$(2%) = "Bell Laboratories" \ AR_BAL%(2%) = 1500% \ AR_ID$(3%) = "C300" \ AR_NAME$(3%) = "Boston University" \ AR_BAL%(3%) = 1000%
850 NUM_AP% = 3% \ AP_ID$(1%) = "V100" \ AP_NAME$(1%) = "Maynard Components" \ AP_BAL%(1%) = 1200%
860 AP_ID$(2%) = "V200" \ AP_NAME$(2%) = "Intel Memory Corp" \ AP_BAL%(2%) = 1000% \ AP_ID$(3%) = "V300" \ AP_NAME$(3%) = "Tektronix Displays" \ AP_BAL%(3%) = 800%
870 NUM_INV% = 3% \ I_SKU$(1%) = "PDP1170" \ I_DESC$(1%) = "PDP-11/70 CPU System" \ I_QTY%(1%) = 2% \ I_COST%(1%) = 1500%
880 I_SKU$(2%) = "VAX11780" \ I_DESC$(2%) = "VAX-11/780 Cabinet" \ I_QTY%(2%) = 1% \ I_COST%(2%) = 2000%
890 I_SKU$(3%) = "VT100" \ I_DESC$(3%) = "VT100 Video Terminal" \ I_QTY%(3%) = 10% \ I_COST%(3%) = 100%
900 NUM_JRN% = 2% \ J_DR$(1%) = "1100" \ J_CR$(1%) = "4010" \ J_AMT%(1%) = 2000% \ J_MEMO$(1%) = "Opening PDP-11/70 Shipment"
910 J_DR$(2%) = "5010" \ J_CR$(2%) = "2010" \ J_AMT%(2%) = 1200% \ J_MEMO$(2%) = "Maynard Components Supply"
920 PRINT "[Sample DIBS-11 business dataset loaded - 8 GL accounts, 3 AR, 3 AP, 3 INV]" \ GOTO 495
960 IF NUM_GL% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  DIBS-11 General Ledger Chart of Accounts - "; COMP_NAME$ \ PRINT EQU$ \ PRINT "Acct#   Account Name                  Type      Normal Side      Balance ($)" \ PRINT SEP$
980 CI% = 1%
990 IF CI% > NUM_GL% THEN GOTO 1070
1000 AC_PAD$ = LEFT$(G_NUM$(CI%) + BLANKS$, 8%) \ NM_PAD$ = LEFT$(G_NAME$(CI%) + BLANKS$, 30%) \ TP_PAD$ = LEFT$(G_TYPE$(CI%) + BLANKS$, 10%) \ SIDE$ = "CREDIT (CR)"
1010 IF G_TYPE$(CI%) = "ASSET" OR G_TYPE$(CI%) = "EXP" THEN SIDE$ = "DEBIT  (DR)"
1020 SD_PAD$ = LEFT$(SIDE$ + BLANKS$, 16%) \ PRINT AC_PAD$; NM_PAD$; TP_PAD$; SD_PAD$; " "; G_BAL%(CI%) \ CI% = CI% + 1% \ GOTO 990
1070 PRINT SEP$ \ PRINT "  "; NUM_GL%; " General Ledger accounts listed" \ PRINT EQU$ \ GOTO 495
1090 IF NUM_GL% >= 25% THEN GOTO 3390
1100 C1% = INSTR(1%, ARGS$, ",")
1110 IF C1% = 0% THEN GOTO 1200
1120 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ A_NUM$ = Q_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1130 IF C2% = 0% THEN GOTO 1200
1140 Q_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 635 \ A_NAM$ = Q_OUT$ \ REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1150 IF C3% = 0% THEN GOTO 1175
1160 Q_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ A_TYP$ = U_OUT$ \ A_BAL% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%)) \ GOTO 1180
1175 Q_IN$ = REM2$ \ GOSUB 635 \ U_IN$ = Q_OUT$ \ GOSUB 580 \ A_TYP$ = U_OUT$ \ A_BAL% = 0%
1180 NUM_GL% = NUM_GL% + 1% \ G_NUM$(NUM_GL%) = A_NUM$ \ G_NAME$(NUM_GL%) = A_NAM$ \ G_TYPE$(NUM_GL%) = A_TYP$ \ G_BAL%(NUM_GL%) = A_BAL%
1190 PRINT "[GL Account "; A_NUM$; " ("; A_NAM$; ") added - Type: "; A_TYP$; ", Balance: $"; A_BAL%; "]" \ GOTO 495
1200 PRINT "DIBS: Syntax is ADDACCT <acct#>, <name>, <type> [, <opening_bal>]" \ GOTO 495
1220 IF NUM_GL% = 0% THEN GOTO 3370
1230 C1% = INSTR(1%, ARGS$, ",")
1240 IF C1% = 0% THEN GOTO 1340
1250 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ P_DR$ = Q_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1260 IF C2% = 0% THEN GOTO 1340
1270 Q_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 635 \ P_CR$ = Q_OUT$ \ REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1280 IF C3% = 0% THEN GOTO 1300
1290 P_AMT% = VAL(LEFT$(REM2$, C3% - 1%)) \ Q_IN$ = MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%) \ GOSUB 635 \ P_MEMO$ = Q_OUT$ \ GOTO 1310
1300 P_AMT% = VAL(REM2$) \ P_MEMO$ = "GL Journal Entry"
1310 GOSUB 650
1320 IF P_OK% = 0% THEN GOTO 1345
1330 PRINT "[Journal Entry #"; NUM_JRN%; " posted: DR "; P_DR$; " / CR "; P_CR$; " for $"; P_AMT%; " ("; P_MEMO$; ")]" \ GOTO 495
1340 PRINT "DIBS: Syntax is POST <dr_acct>, <cr_acct>, <amount> [, <memo>]" \ GOTO 495
1345 PRINT "DIBS: Invalid GL account number in POST (verify with COA)" \ GOTO 495
1360 PRINT EQU$ \ PRINT "  DIBS-11 General Ledger Journal Register - Period: "; PERIOD$ \ PRINT EQU$ \ PRINT "#    Debit    Credit   Amount ($)    Memo / Description" \ PRINT SEP$
1370 IF NUM_JRN% = 0% THEN GOTO 1430
1380 JI% = 1%
1390 IF JI% > NUM_JRN% THEN GOTO 1440
1400 IDX_S$ = STR$(JI%) \ T_IN$ = IDX_S$ \ GOSUB 500 \ IPAD$ = LEFT$(T_OUT$ + "     ", 5%) \ DR_P$ = LEFT$(J_DR$(JI%) + BLANKS$, 9%) \ CR_P$ = LEFT$(J_CR$(JI%) + BLANKS$, 9%)
1410 AM_S$ = STR$(J_AMT%(JI%)) \ T_IN$ = AM_S$ \ GOSUB 500 \ AM_P$ = LEFT$(T_OUT$ + BLANKS$, 13%) \ PRINT IPAD$; DR_P$; CR_P$; AM_P$; " "; J_MEMO$(JI%) \ JI% = JI% + 1% \ GOTO 1390
1430 PRINT "    [No journal entries recorded]"
1440 PRINT SEP$ \ PRINT "  "; NUM_JRN%; " journal entry(s) in register" \ PRINT EQU$ \ GOTO 495
1460 IF NUM_GL% = 0% THEN GOTO 3370
1470 PRINT EQU$ \ PRINT "  DIBS-11 GENERAL LEDGER TRIAL BALANCE - "; PERIOD$ \ PRINT EQU$ \ PRINT "Acct#   Account Name                  Type         Debit ($)      Credit ($)" \ PRINT SEP$
1480 TOT_DR% = 0% \ TOT_CR% = 0% \ TI% = 1%
1490 IF TI% > NUM_GL% THEN GOTO 1580
1500 AC_P$ = LEFT$(G_NUM$(TI%) + BLANKS$, 8%) \ NM_P$ = LEFT$(G_NAME$(TI%) + BLANKS$, 30%) \ TP_P$ = LEFT$(G_TYPE$(TI%) + BLANKS$, 12%)
1510 IF G_TYPE$(TI%) = "ASSET" OR G_TYPE$(TI%) = "EXP" THEN GOTO 1540
1520 TOT_CR% = TOT_CR% + G_BAL%(TI%) \ PRINT AC_P$; NM_P$; TP_P$; "             0          "; G_BAL%(TI%) \ GOTO 1560
1540 TOT_DR% = TOT_DR% + G_BAL%(TI%) \ B_STR$ = STR$(G_BAL%(TI%)) \ T_IN$ = B_STR$ \ GOSUB 500 \ B_PAD$ = LEFT$(T_OUT$ + BLANKS$, 14%) \ PRINT AC_P$; NM_P$; TP_P$; " "; B_PAD$; "          0"
1560 TI% = TI% + 1% \ GOTO 1490
1580 PRINT SEP$ \ PRINT "TOTAL DEBITS:  $"; TOT_DR%; "      TOTAL CREDITS: $"; TOT_CR%
1590 IF TOT_DR% = TOT_CR% THEN PRINT "*** TRIAL BALANCE IS IN BALANCE (DR = CR) ***"
1600 IF TOT_DR% <> TOT_CR% THEN PRINT "*** WARNING: TRIAL BALANCE OUT OF BALANCE ***"
1610 PRINT EQU$ \ GOTO 495
1640 IF NUM_GL% = 0% THEN GOTO 3370
1650 PRINT EQU$ \ PRINT "  DIBS-11 INCOME STATEMENT (PROFIT & LOSS) - "; PERIOD$ \ PRINT EQU$ \ PRINT "REVENUE ACCOUNTS:"
1660 TOT_REV% = 0% \ TOT_EXP% = 0% \ II% = 1%
1670 IF II% > NUM_GL% THEN GOTO 1710
1680 IF G_TYPE$(II%) <> "REV" THEN GOTO 1700
1690 TOT_REV% = TOT_REV% + G_BAL%(II%) \ NM_P$ = LEFT$(G_NAME$(II%) + BLANKS$, 32%) \ PRINT "  "; G_NUM$(II%); "  "; NM_P$; " $"; G_BAL%(II%)
1700 II% = II% + 1% \ GOTO 1670
1710 PRINT "  Total Revenue:                           $"; TOT_REV% \ PRINT SEP$ \ PRINT "EXPENSE ACCOUNTS:" \ II% = 1%
1720 IF II% > NUM_GL% THEN GOTO 1760
1730 IF G_TYPE$(II%) <> "EXP" THEN GOTO 1750
1740 TOT_EXP% = TOT_EXP% + G_BAL%(II%) \ NM_P$ = LEFT$(G_NAME$(II%) + BLANKS$, 32%) \ PRINT "  "; G_NUM$(II%); "  "; NM_P$; " $"; G_BAL%(II%)
1750 II% = II% + 1% \ GOTO 1720
1760 NET_INC% = TOT_REV% - TOT_EXP% \ PRINT "  Total Expenses:                          $"; TOT_EXP% \ PRINT SEP$ \ PRINT "NET INCOME (PROFIT / LOSS):                $"; NET_INC% \ PRINT EQU$ \ GOTO 495
1810 IF NUM_GL% = 0% THEN GOTO 3370
1820 TOT_AST% = 0% \ TOT_LIB% = 0% \ TOT_EQ% = 0% \ TOT_REV% = 0% \ TOT_EXP% = 0% \ BI% = 1%
1830 IF BI% > NUM_GL% THEN GOTO 1890
1840 IF G_TYPE$(BI%) = "ASSET" THEN TOT_AST% = TOT_AST% + G_BAL%(BI%)
1850 IF G_TYPE$(BI%) = "LIAB" THEN TOT_LIB% = TOT_LIB% + G_BAL%(BI%)
1860 IF G_TYPE$(BI%) = "EQUITY" THEN TOT_EQ% = TOT_EQ% + G_BAL%(BI%)
1870 IF G_TYPE$(BI%) = "REV" THEN TOT_REV% = TOT_REV% + G_BAL%(BI%)
1880 IF G_TYPE$(BI%) = "EXP" THEN TOT_EXP% = TOT_EXP% + G_BAL%(BI%)
1885 BI% = BI% + 1% \ GOTO 1830
1890 NET_INC% = TOT_REV% - TOT_EXP% \ TOT_EQ_ALL% = TOT_EQ% + NET_INC% \ TOT_LE% = TOT_LIB% + TOT_EQ_ALL%
1900 PRINT EQU$ \ PRINT "  DIBS-11 BALANCE SHEET - "; COMP_NAME$ \ PRINT EQU$ \ PRINT "ASSETS:" \ BI% = 1%
1910 IF BI% > NUM_GL% THEN GOTO 1945
1920 IF G_TYPE$(BI%) <> "ASSET" THEN GOTO 1940
1930 NM_P$ = LEFT$(G_NAME$(BI%) + BLANKS$, 32%) \ PRINT "  "; G_NUM$(BI%); "  "; NM_P$; " $"; G_BAL%(BI%)
1940 BI% = BI% + 1% \ GOTO 1910
1945 PRINT "  Total Assets:                            $"; TOT_AST% \ PRINT SEP$ \ PRINT "LIABILITIES & EQUITY:" \ BI% = 1%
1950 IF BI% > NUM_GL% THEN GOTO 1985
1960 IF G_TYPE$(BI%) = "LIAB" OR G_TYPE$(BI%) = "EQUITY" THEN GOTO 1970
1965 GOTO 1980
1970 NM_P$ = LEFT$(G_NAME$(BI%) + BLANKS$, 32%) \ PRINT "  "; G_NUM$(BI%); "  "; NM_P$; " $"; G_BAL%(BI%)
1980 BI% = BI% + 1% \ GOTO 1950
1985 PRINT "  ----  Current Period Net Income          $"; NET_INC% \ PRINT SEP$ \ PRINT "  Total Liabilities:                       $"; TOT_LIB%
1990 PRINT "  Total Equity (incl. Net Income):         $"; TOT_EQ_ALL% \ PRINT "  Total Liabilities & Equity:              $"; TOT_LE% \ PRINT EQU$ \ GOTO 495
2020 PRINT EQU$ \ PRINT "  DIBS-11 Accounts Receivable (AR) Customer Subledger" \ PRINT EQU$ \ PRINT "CustID   Customer Name                   Balance ($)" \ PRINT SEP$
2030 TOT_AR% = 0% \ AI% = 1%
2040 IF AI% > NUM_AR% THEN GOTO 2090
2050 TOT_AR% = TOT_AR% + AR_BAL%(AI%) \ ID_P$ = LEFT$(AR_ID$(AI%) + BLANKS$, 9%) \ NM_P$ = LEFT$(AR_NAME$(AI%) + BLANKS$, 31%) \ PRINT ID_P$; NM_P$; " $"; AR_BAL%(AI%) \ AI% = AI% + 1% \ GOTO 2040
2090 PRINT SEP$ \ PRINT "  Total Accounts Receivable ("; NUM_AR%; " customers): $"; TOT_AR% \ PRINT EQU$ \ GOTO 495
2120 IF NUM_GL% = 0% THEN GOTO 3370
2130 C1% = INSTR(1%, ARGS$, ",")
2140 IF C1% = 0% THEN GOTO 2250
2150 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ C_ID$ = Q_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
2160 IF C2% = 0% THEN GOTO 2250
2170 Q_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 635 \ C_NM$ = Q_OUT$ \ C_AMT% = VAL(MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%)) \ F_IDX% = 0% \ AI% = 1%
2180 IF AI% > NUM_AR% THEN GOTO 2210
2190 IF AR_ID$(AI%) = C_ID$ THEN F_IDX% = AI%
2200 AI% = AI% + 1% \ GOTO 2180
2210 IF F_IDX% > 0% THEN GOTO 2230
2220 NUM_AR% = NUM_AR% + 1% \ F_IDX% = NUM_AR% \ AR_ID$(F_IDX%) = C_ID$ \ AR_NAME$(F_IDX%) = C_NM$ \ AR_BAL%(F_IDX%) = 0%
2230 AR_BAL%(F_IDX%) = AR_BAL%(F_IDX%) + C_AMT% \ P_DR$ = "1100" \ P_CR$ = "4010" \ P_AMT% = C_AMT% \ P_MEMO$ = "AR Invoice " + C_ID$ \ GOSUB 650
2240 PRINT "[AR Invoice billed to "; C_ID$; " ("; AR_NAME$(F_IDX%); ") for $"; C_AMT%; " - Posted DR 1100 / CR 4010]" \ GOTO 495
2250 PRINT "DIBS: Syntax is INVOICE <cust_id>, <name>, <amount>" \ GOTO 495
2270 IF NUM_AR% = 0% THEN GOTO 3370
2280 C1% = INSTR(1%, ARGS$, ",")
2290 IF C1% = 0% THEN GOTO 2380
2300 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ C_ID$ = Q_OUT$ \ C_AMT% = VAL(MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%)) \ F_IDX% = 0% \ AI% = 1%
2310 IF AI% > NUM_AR% THEN GOTO 2340
2320 IF AR_ID$(AI%) = C_ID$ THEN F_IDX% = AI%
2330 AI% = AI% + 1% \ GOTO 2310
2340 IF F_IDX% = 0% THEN GOTO 2385
2350 AR_BAL%(F_IDX%) = AR_BAL%(F_IDX%) - C_AMT% \ P_DR$ = "1010" \ P_CR$ = "1100" \ P_AMT% = C_AMT% \ P_MEMO$ = "AR Cash Receipt " + C_ID$ \ GOSUB 650
2360 PRINT "[AR Payment of $"; C_AMT%; " received from "; C_ID$; " - Posted DR 1010 / CR 1100]" \ GOTO 495
2380 PRINT "DIBS: Syntax is RECEIVE <cust_id>, <amount>" \ GOTO 495
2385 PRINT "DIBS: Customer ID '"; C_ID$; "' not found in AR subledger" \ GOTO 495
2400 PRINT EQU$ \ PRINT "  DIBS-11 Accounts Payable (AP) Vendor Subledger" \ PRINT EQU$ \ PRINT "VendID   Vendor Name                     Balance ($)" \ PRINT SEP$
2410 TOT_AP% = 0% \ VI% = 1%
2420 IF VI% > NUM_AP% THEN GOTO 2470
2430 TOT_AP% = TOT_AP% + AP_BAL%(VI%) \ ID_P$ = LEFT$(AP_ID$(VI%) + BLANKS$, 9%) \ NM_P$ = LEFT$(AP_NAME$(VI%) + BLANKS$, 31%) \ PRINT ID_P$; NM_P$; " $"; AP_BAL%(VI%) \ VI% = VI% + 1% \ GOTO 2420
2470 PRINT SEP$ \ PRINT "  Total Accounts Payable ("; NUM_AP%; " vendors): $"; TOT_AP% \ PRINT EQU$ \ GOTO 495
2500 IF NUM_GL% = 0% THEN GOTO 3370
2510 C1% = INSTR(1%, ARGS$, ",")
2520 IF C1% = 0% THEN GOTO 2630
2530 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ V_ID$ = Q_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
2540 IF C2% = 0% THEN GOTO 2630
2550 Q_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 635 \ V_NM$ = Q_OUT$ \ V_AMT% = VAL(MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%)) \ F_IDX% = 0% \ VI% = 1%
2560 IF VI% > NUM_AP% THEN GOTO 2590
2570 IF AP_ID$(VI%) = V_ID$ THEN F_IDX% = VI%
2580 VI% = VI% + 1% \ GOTO 2560
2590 IF F_IDX% > 0% THEN GOTO 2610
2600 NUM_AP% = NUM_AP% + 1% \ F_IDX% = NUM_AP% \ AP_ID$(F_IDX%) = V_ID$ \ AP_NAME$(F_IDX%) = V_NM$ \ AP_BAL%(F_IDX%) = 0%
2610 AP_BAL%(F_IDX%) = AP_BAL%(F_IDX%) + V_AMT% \ P_DR$ = "5010" \ P_CR$ = "2010" \ P_AMT% = V_AMT% \ P_MEMO$ = "AP Voucher " + V_ID$ \ GOSUB 650
2620 PRINT "[AP Voucher recorded for "; V_ID$; " ("; AP_NAME$(F_IDX%); ") for $"; V_AMT%; " - Posted DR 5010 / CR 2010]" \ GOTO 495
2630 PRINT "DIBS: Syntax is VOUCHER <vend_id>, <name>, <amount>" \ GOTO 495
2650 IF NUM_AP% = 0% THEN GOTO 3370
2660 C1% = INSTR(1%, ARGS$, ",")
2670 IF C1% = 0% THEN GOTO 2760
2680 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ V_ID$ = Q_OUT$ \ V_AMT% = VAL(MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%)) \ F_IDX% = 0% \ VI% = 1%
2690 IF VI% > NUM_AP% THEN GOTO 2720
2700 IF AP_ID$(VI%) = V_ID$ THEN F_IDX% = VI%
2710 VI% = VI% + 1% \ GOTO 2690
2720 IF F_IDX% = 0% THEN GOTO 2765
2730 AP_BAL%(F_IDX%) = AP_BAL%(F_IDX%) - V_AMT% \ P_DR$ = "2010" \ P_CR$ = "1010" \ P_AMT% = V_AMT% \ P_MEMO$ = "AP Check Payment " + V_ID$ \ GOSUB 650
2740 PRINT "[AP Check of $"; V_AMT%; " paid to "; V_ID$; " - Posted DR 2010 / CR 1010]" \ GOTO 495
2760 PRINT "DIBS: Syntax is PAY <vend_id>, <amount>" \ GOTO 495
2765 PRINT "DIBS: Vendor ID '"; V_ID$; "' not found in AP subledger" \ GOTO 495
2780 PRINT EQU$ \ PRINT "  DIBS-11 Inventory Control (IC) Item Master" \ PRINT EQU$ \ PRINT "SKU        Description                     Qty     Unit Cost ($)   Ext Value ($)" \ PRINT SEP$
2790 TOT_IV% = 0% \ XI% = 1%
2800 IF XI% > NUM_INV% THEN GOTO 2870
2810 EXT_V% = I_QTY%(XI%) * I_COST%(XI%) \ TOT_IV% = TOT_IV% + EXT_V% \ SK_P$ = LEFT$(I_SKU$(XI%) + BLANKS$, 11%) \ DS_P$ = LEFT$(I_DESC$(XI%) + BLANKS$, 32%)
2820 Q_S$ = STR$(I_QTY%(XI%)) \ T_IN$ = Q_S$ \ GOSUB 500 \ Q_P$ = LEFT$(T_OUT$ + BLANKS$, 8%) \ C_S$ = STR$(I_COST%(XI%)) \ T_IN$ = C_S$ \ GOSUB 500 \ C_P$ = LEFT$(T_OUT$ + BLANKS$, 15%)
2830 PRINT SK_P$; DS_P$; Q_P$; C_P$; " $"; EXT_V% \ XI% = XI% + 1% \ GOTO 2800
2870 PRINT SEP$ \ PRINT "  Total Inventory Valuation ("; NUM_INV%; " items): $"; TOT_IV% \ PRINT EQU$ \ GOTO 495
2900 IF NUM_INV% >= 20% THEN GOTO 3390
2910 C1% = INSTR(1%, ARGS$, ",")
2920 IF C1% = 0% THEN GOTO 3000
2930 Q_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 635 \ N_SKU$ = Q_OUT$ \ REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
2940 IF C2% = 0% THEN GOTO 3000
2950 Q_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 635 \ N_DSC$ = Q_OUT$ \ REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
2960 IF C3% = 0% THEN GOTO 3000
2970 N_QTY% = VAL(LEFT$(REM2$, C3% - 1%)) \ N_CST% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%)) \ NUM_INV% = NUM_INV% + 1%
2980 I_SKU$(NUM_INV%) = N_SKU$ \ I_DESC$(NUM_INV%) = N_DSC$ \ I_QTY%(NUM_INV%) = N_QTY% \ I_COST%(NUM_INV%) = N_CST%
2990 PRINT "[Inventory Item "; N_SKU$; " ("; N_DSC$; ") added: Qty="; N_QTY%; ", Cost=$"; N_CST%; "]" \ GOTO 495
3000 PRINT "DIBS: Syntax is ADDITEM <sku>, <desc>, <qty>, <cost>" \ GOTO 495
3020 IF NUM_GL% = 0% THEN GOTO 3370
3030 R_FILE$ = ARGS$
3040 IF R_FILE$ = "" THEN GOTO 3160
3050 U_IN$ = R_FILE$ \ GOSUB 580
3060 IF LEFT$(U_OUT$, 3%) = "ON " THEN R_FILE$ = MID$(R_FILE$, 4%, LEN(R_FILE$) - 3%)
3065 Q_IN$ = R_FILE$ \ GOSUB 635 \ R_FILE$ = Q_OUT$
3070 OPEN R_FILE$ FOR OUTPUT AS FILE #2% \ PRINT #2%, EQU$ \ PRINT #2%, "  DIBS-11 EXECUTIVE FINANCIAL REPORT - "; COMP_NAME$ \ PRINT #2%, "  Fiscal Period: "; PERIOD$ \ PRINT #2%, EQU$
3080 RI% = 1% \ TOT_R% = 0% \ TOT_E% = 0%
3090 IF RI% > NUM_GL% THEN GOTO 3130
3100 NM_P$ = LEFT$(G_NAME$(RI%) + BLANKS$, 30%) \ TP_P$ = LEFT$(G_TYPE$(RI%) + BLANKS$, 8%) \ PRINT #2%, G_NUM$(RI%); "  "; NM_P$; "  "; TP_P$; "  $"; G_BAL%(RI%)
3110 IF G_TYPE$(RI%) = "REV" THEN TOT_R% = TOT_R% + G_BAL%(RI%)
3115 IF G_TYPE$(RI%) = "EXP" THEN TOT_E% = TOT_E% + G_BAL%(RI%)
3120 RI% = RI% + 1% \ GOTO 3090
3130 NET_R% = TOT_R% - TOT_E% \ PRINT #2%, SEP$ \ PRINT #2%, "Total Revenue: $"; TOT_R%; "   Total Expenses: $"; TOT_E%; "   Net Income: $"; NET_R% \ PRINT #2%, EQU$ \ CLOSE #2%
3140 PRINT "[DIBS-11 Financial Report exported to "; R_FILE$; "]" \ GOTO 495
3160 GOTO 1460
3170 PRINT "DIBS-11 System Status:" \ PRINT "  Company:         "; COMP_NAME$ \ PRINT "  Fiscal Period:   "; PERIOD$
3180 PRINT "  GL Accounts:     "; NUM_GL% \ PRINT "  Journal Entries: "; NUM_JRN% \ PRINT "  AR Customers:    "; NUM_AR%
3190 PRINT "  AP Vendors:      "; NUM_AP% \ PRINT "  Inventory Items: "; NUM_INV% \ GOTO 495
3205 NUM_GL% = 0% \ NUM_JRN% = 0% \ NUM_AR% = 0% \ NUM_AP% = 0% \ NUM_INV% = 0% \ PRINT "[All DIBS-11 ledgers and subledgers cleared]" \ GOTO 495
3220 PRINT EQU$ \ PRINT "    DIBS-11 Integrated Business System Commands" \ PRINT EQU$ \ PRINT "  COA / GL / ACCOUNTS              List General Ledger Chart of Accounts"
3225 PRINT "  ADDACCT <num>, <name>, <t>, <b > Add General Ledger account" \ PRINT "  POST <dr>, <cr>, <amt>, <memo>   Post double-entry GL journal transaction"
3230 PRINT "  JRNLIST / REGISTER               Display GL Journal Entry Register" \ PRINT "  TRIAL / TB                       Generate General Ledger Trial Balance"
3235 PRINT "  INCOME / PL                      Generate Income Statement (Profit & Loss)" \ PRINT "  BALANCE / BS                     Generate Balance Sheet"
3240 PRINT "  AR / INVOICE / RECEIVE           List AR, bill customer, or receive cash" \ PRINT "  AP / VOUCHER / PAY               List AP, record voucher, or pay vendor"
3245 PRINT "  INV / ADDITEM                    List Inventory valuation or add SKU item" \ PRINT "  REPORT [ON <f>] / EXPORT <f>     Display or export financial report"
3250 PRINT "  SAMPLE / SAVE [f] / LOAD [f]     Load DEC business dataset or save/load GL" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear ledgers, or exit" \ PRINT EQU$ \ GOTO 495
3290 IF NUM_GL% = 0% THEN GOTO 3370
3295 SV_FILE$ = DIBS_FILE$
3298 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
3300 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
3305 IF SI% > NUM_GL% THEN GOTO 3320
3310 PRINT #2%, G_NUM$(SI%); "|"; G_NAME$(SI%); "|"; G_TYPE$(SI%); "|"; G_BAL%(SI%) \ SI% = SI% + 1% \ GOTO 3305
3320 CLOSE #2% \ PRINT "["; NUM_GL%; " GL accounts saved to "; SV_FILE$; "]" \ GOTO 495
3330 LD_FILE$ = DIBS_FILE$
3332 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
3334 ON ERROR GOTO 3362 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_GL% = 0%
3336 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
3338 IF T_OUT$ = "" THEN GOTO 3336
3340 P1% = INSTR(1%, T_OUT$, "|")
3342 IF P1% = 0% THEN GOTO 3336
3344 F_NUM$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
3346 IF P2% = 0% THEN GOTO 3336
3348 F_NAM$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
3350 IF P3% = 0% THEN GOTO 3336
3352 F_TYP$ = LEFT$(REM2$, P3% - 1%) \ F_BAL% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%)) \ NUM_GL% = NUM_GL% + 1%
3354 G_NUM$(NUM_GL%) = F_NUM$ \ G_NAME$(NUM_GL%) = F_NAM$ \ G_TYPE$(NUM_GL%) = F_TYP$ \ G_BAL%(NUM_GL%) = F_BAL% \ GOTO 3336
3362 CLOSE #2% \ RESUME 3365
3365 ON ERROR GOTO 0 \ PRINT "["; NUM_GL%; " GL accounts loaded from "; LD_FILE$; "]" \ GOTO 495
3370 PRINT "DIBS: No accounting data loaded. Use SAMPLE or ADDACCT." \ GOTO 495
3390 PRINT "DIBS: Table capacity reached" \ GOTO 495
3400 END
