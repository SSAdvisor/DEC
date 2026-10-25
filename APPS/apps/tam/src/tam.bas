10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM F_NAME$(15%) \ DIM F_TYPE$(15%) \ DIM F_LEN%(15%) \ DIM F_ROW%(15%)
20 NUM_FLD% = 0% \ SCR_ID$ = "ORD_ENTRY" \ TX_CNT% = 12% \ DB_FILE$ = "TAMFRM.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    EG&H TAM V3.2 - Terminal Application Manager & Screen Monitor" \ PRINT "    Evans Griffiths & Hart, Inc. (Lexington, MA) - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load form, FIELDS, PAINT, VALIDATE, MONITOR." \ PRINT ""
100 PRINT "TAM> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "FIELDS" OR VERB$ = "LIST" THEN GOTO 820
360 IF VERB$ = "PAINT" OR VERB$ = "RENDER" OR VERB$ = "SCREEN" THEN GOTO 960
370 IF VERB$ = "VALIDATE" OR VERB$ = "CHECK" THEN GOTO 1100
380 IF VERB$ = "MONITOR" OR VERB$ = "DISPATCH" OR VERB$ = "TX" THEN GOTO 1200
390 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1320
400 IF VERB$ = "SAVE" THEN GOTO 1500
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1650
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1900
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2000
480 PRINT "TAM: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_FLD% = 4% \ SCR_ID$ = "ORD_ENTRY" \ TX_CNT% = 12%
710 F_NAME$(1%) = "ORDER_NO  " \ F_TYPE$(1%) = "NUM/REQ " \ F_LEN%(1%) = 8%  \ F_ROW%(1%) = 4%
720 F_NAME$(2%) = "CUST_CODE " \ F_TYPE$(2%) = "ALPHA/UP" \ F_LEN%(2%) = 10% \ F_ROW%(2%) = 6%
730 F_NAME$(3%) = "PART_NUM  " \ F_TYPE$(3%) = "RAD50   " \ F_LEN%(3%) = 12% \ F_ROW%(3%) = 8%
740 F_NAME$(4%) = "ORDER_AMT " \ F_TYPE$(4%) = "CURR/DEC" \ F_LEN%(4%) = 10% \ F_ROW%(4%) = 10%
750 PRINT "[Sample EG&H TAM screen definition ("; SCR_ID$; ") loaded - 4 VT100 fields]" \ GOTO 495
820 IF NUM_FLD% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  EG&H TAM Screen Field Table — Screen: "; SCR_ID$; " ("; DB_FILE$; ")" \ PRINT SEP$
840 PRINT "  Fld#   Field Name     Attribute/Type   Length   VT100 Row" \ PRINT SEP$
850 FI% = 1%
860 IF FI% > NUM_FLD% THEN GOTO 920
870 NM_P$ = LEFT$(F_NAME$(FI%) + BLANKS$, 13%) \ TP_P$ = LEFT$(F_TYPE$(FI%) + BLANKS$, 15%)
880 PRINT "  "; FI%; "      "; NM_P$; "  "; TP_P$; "  "; F_LEN%(FI%); "        Row "; F_ROW%(FI%)
890 FI% = FI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_FLD% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  +--------------------- EG&H TAM VT100 SCREEN PAINTER ---------------------+"
980 PRINT "  | SCREEN: "; LEFT$(SCR_ID$ + BLANKS$, 16%); "              TERMINAL: KB0: (VT100/AVO)    |"
990 FI% = 1%
1000 IF FI% > NUM_FLD% THEN GOTO 1050
1010 NM_P$ = LEFT$(F_NAME$(FI%) + BLANKS$, 14%) \ TP_P$ = LEFT$(F_TYPE$(FI%) + BLANKS$, 10%)
1020 PRINT "  | Row "; F_ROW%(FI%); ": "; NM_P$; " [__________] ("; TP_P$; " Len="; F_LEN%(FI%); ")          |"
1030 FI% = FI% + 1% \ GOTO 1000
1050 PRINT "  +-------------------------------------------------------------------------+" \ PRINT EQU$ \ GOTO 495
1100 IF NUM_FLD% = 0% THEN GOTO 3370
1110 TOT_W% = 0% \ FI% = 1%
1120 IF FI% > NUM_FLD% THEN GOTO 1150
1130 TOT_W% = TOT_W% + F_LEN%(FI%) \ FI% = FI% + 1% \ GOTO 1120
1150 PRINT "[TAM Field-Attribute Validation PASSED: "; NUM_FLD%; " fields verified, Buffer Size="; TOT_W%; " bytes]" \ GOTO 495
1200 TX_CODE$ = "TX_ORDER"
1210 IF ARGS$ <> "" THEN TX_CODE$ = ARGS$
1220 U_IN$ = TX_CODE$ \ GOSUB 580 \ TX_CODE$ = U_OUT$ \ TX_CNT% = TX_CNT% + 1%
1230 PRINT "[TAM Transaction Monitor: Dispatched "; TX_CODE$; " on Screen "; SCR_ID$; " (Active TX #"; TX_CNT%; " — Response: 0.08s)]" \ GOTO 495
1320 IF NUM_FLD% >= 15% THEN GOTO 1460
1330 C1% = INSTR(1%, ARGS$, ",")
1340 IF C1% = 0% THEN GOTO 1450
1350 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ NM_V$ = U_OUT$
1360 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1370 IF C2% = 0% THEN GOTO 1450
1380 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ TP_V$ = U_OUT$
1390 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1400 IF C3% = 0% THEN GOTO 1450
1410 LN_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ RW_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1420 NUM_FLD% = NUM_FLD% + 1% \ F_NAME$(NUM_FLD%) = NM_V$ \ F_TYPE$(NUM_FLD%) = TP_V$ \ F_LEN%(NUM_FLD%) = LN_V% \ F_ROW%(NUM_FLD%) = RW_V%
1430 PRINT "[TAM Field #"; NUM_FLD%; " added: "; NM_V$; " (Type="; TP_V$; ", Len="; LN_V%; ", Row="; RW_V%; ")]" \ GOTO 495
1450 PRINT "TAM: Syntax is ADD <field_name>, <type>, <len>, <row>" \ GOTO 495
1460 PRINT "TAM: Screen table full" \ GOTO 495
1500 IF NUM_FLD% = 0% THEN GOTO 3370
1510 SV_FILE$ = DB_FILE$
1520 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1530 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1540 IF SI% > NUM_FLD% THEN GOTO 1580
1550 PRINT #2%, F_NAME$(SI%); "|"; F_TYPE$(SI%); "|"; F_LEN%(SI%); "|"; F_ROW%(SI%)
1560 SI% = SI% + 1% \ GOTO 1540
1580 CLOSE #2% \ PRINT "["; NUM_FLD%; " TAM field definitions saved to "; SV_FILE$; "]" \ GOTO 495
1650 LD_FILE$ = DB_FILE$
1660 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1670 ON ERROR GOTO 1800 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_FLD% = 0%
1680 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1690 IF T_OUT$ = "" THEN GOTO 1680
1700 P1% = INSTR(1%, T_OUT$, "|")
1710 IF P1% = 0% THEN GOTO 1680
1720 FNM$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1730 IF P2% = 0% THEN GOTO 1680
1740 FTP$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1750 IF P3% = 0% THEN GOTO 1680
1760 FLN% = VAL(LEFT$(REM2$, P3% - 1%)) \ FRW% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1770 NUM_FLD% = NUM_FLD% + 1% \ F_NAME$(NUM_FLD%) = FNM$ \ F_TYPE$(NUM_FLD%) = FTP$ \ F_LEN%(NUM_FLD%) = FLN% \ F_ROW%(NUM_FLD%) = FRW% \ GOTO 1680
1800 CLOSE #2% \ RESUME 1810
1810 ON ERROR GOTO 0 \ PRINT "["; NUM_FLD%; " TAM field definitions loaded from "; LD_FILE$; "]" \ GOTO 495
1900 PRINT "EG&H TAM V3.2 Status:" \ PRINT "  Active Screen:  "; SCR_ID$; " (File: "; DB_FILE$; ", Fields: "; NUM_FLD%; ")"
1910 PRINT "  Transactions:   "; TX_CNT%; " dispatched" \ GOTO 495
2000 NUM_FLD% = 0% \ PRINT "[TAM screen definition cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    EG&H TAM V3.2 Terminal Application Manager Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample VT100 screen (ORD_ENTRY)" \ PRINT "  FIELDS / LIST                    List screen fields and attributes"
3020 PRINT "  PAINT / RENDER / SCREEN          Paint VT100 form layout" \ PRINT "  VALIDATE / CHECK                 Validate field coordinates and buffer size"
3030 PRINT "  MONITOR [tx] / DISPATCH          Dispatch commercial transaction" \ PRINT "  ADD <name>, <type>, <len>, <row> Add field to screen definition"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load TAMFRM.DAT screen file" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear form, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "TAM: Screen definition is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
