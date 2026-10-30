10 MAP (REC_BUF) STRING MAP_LINE$ = 255%
15 DIM CP_CODE$(30%) \ DIM CP_PCT$(30%) \ DIM CP_BP%(30%) \ DIM CP_UNIT$(30%) \ DIM CP_VAL%(30%) \ DIM CP_STAT$(30%) \ DIM CP_DESC$(30%)
20 NUM_CP% = 0% \ DB_FILE$ = "COUPON.DAT" \ PIPE$ = "|" \ RNG_SEED% = 137%
25 LET_POOL$ = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
30 DIG_POOL$ = "0123456789" \ SPC_POOL$ = "!@#$%*-_+=~?"
35 SEP$ = "--------------------------------------------------------------------------------"
40 EQU$ = "================================================================================"
45 IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
46 ON ERROR GOTO 65 \ OPEN DB_FILE$ FOR INPUT AS FILE #2%
48 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
50 IF T_OUT$ = "" THEN GOTO 48
52 P1% = INSTR(1%, T_OUT$, PIPE$)
53 IF P1% = 0% THEN GOTO 48
54 FC$ = LEFT$(T_OUT$, P1% - 1%) \ R1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, R1$, PIPE$)
55 IF P2% = 0% THEN GOTO 48
56 FP$ = LEFT$(R1$, P2% - 1%) \ R2$ = MID$(R1$, P2% + 1%, LEN(R1$) - P2%) \ P3% = INSTR(1%, R2$, PIPE$)
57 IF P3% = 0% THEN GOTO 48
58 FU$ = LEFT$(R2$, P3% - 1%) \ R3$ = MID$(R2$, P3% + 1%, LEN(R2$) - P3%) \ P4% = INSTR(1%, R3$, PIPE$)
59 IF P4% = 0% THEN GOTO 48
60 FV% = VAL(LEFT$(R3$, P4% - 1%)) \ R4$ = MID$(R3$, P4% + 1%, LEN(R3$) - P4%) \ P5% = INSTR(1%, R4$, PIPE$)
61 IF P5% = 0% THEN GOTO 48
62 FS$ = LEFT$(R4$, P5% - 1%) \ FD$ = MID$(R4$, P5% + 1%, LEN(R4$) - P5%) \ PCT_IN$ = FP$ \ GOSUB 682
63 NUM_CP% = NUM_CP% + 1% \ CP_CODE$(NUM_CP%) = FC$ \ CP_PCT$(NUM_CP%) = FP$ \ CP_BP%(NUM_CP%) = BP_OUT% \ CP_UNIT$(NUM_CP%) = FU$ \ CP_VAL%(NUM_CP%) = FV% \ CP_STAT$(NUM_CP%) = FS$ \ CP_DESC$(NUM_CP%) = FD$ \ GOTO 48
65 CLOSE #2% \ RESUME 68
68 ON ERROR GOTO 0
70 IF CMD_LINE$ = "" THEN GOTO 80
75 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Legacy Computing Systems - SYSTEM Discount Coupon Manager V1.0"
85 PRINT "    Authorized Account: SYSTEM ([1,2] RSTS/E | [1,4] VAX/VMS) - BASIC-PLUS-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE, LIST, CREATE, GENERATE, VALIDATE, DISABLE, or EXIT." \ PRINT ""
100 PRINT "COUPON> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "LIST" OR VERB$ = "DISPLAY" OR VERB$ = "COUPONS" THEN GOTO 820
360 IF VERB$ = "CREATE" OR VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1000
370 IF VERB$ = "GENERATE" OR VERB$ = "GEN" THEN GOTO 980
380 IF VERB$ = "VALIDATE" OR VERB$ = "APPLY" OR VERB$ = "CHECK" THEN GOTO 1250
390 IF VERB$ = "DISABLE" OR VERB$ = "SUSPEND" THEN GOTO 1400
400 IF VERB$ = "ENABLE" OR VERB$ = "ACTIVATE" THEN GOTO 1405
410 IF VERB$ = "DELETE" OR VERB$ = "REMOVE" THEN GOTO 1460
420 IF VERB$ = "SAVE" THEN GOTO 1550
430 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
440 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
450 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "COUPON: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
640 RNG_SEED% = RNG_SEED% + 37% + NUM_CP% * 13%
645 P1_I% = RNG_SEED% - INT(RNG_SEED% / 49%) * 49% + 1%
650 P2_I% = RNG_SEED% - INT(RNG_SEED% / 10%) * 10% + 1%
655 P3_I% = RNG_SEED% - INT(RNG_SEED% / 12%) * 12% + 1%
660 P4_I% = (RNG_SEED% + 19%) - INT((RNG_SEED% + 19%) / 49%) * 49% + 1%
665 P5_I% = (RNG_SEED% + 7%) - INT((RNG_SEED% + 7%) / 12%) * 12% + 1%
670 P6_I% = (RNG_SEED% + 5%) - INT((RNG_SEED% + 5%) / 10%) * 10% + 1%
675 GEN_CODE$ = MID$(LET_POOL$, P1_I%, 1%) + MID$(DIG_POOL$, P2_I%, 1%) + MID$(SPC_POOL$, P3_I%, 1%) + MID$(LET_POOL$, P4_I%, 1%) + MID$(SPC_POOL$, P5_I%, 1%) + MID$(DIG_POOL$, P6_I%, 1%)
680 RETURN
682 DP% = INSTR(1%, PCT_IN$, ".")
684 IF DP% = 0% THEN GOTO 694
686 PW% = VAL(LEFT$(PCT_IN$, DP% - 1%)) \ PF_S$ = MID$(PCT_IN$, DP% + 1%, LEN(PCT_IN$) - DP%)
688 IF LEN(PF_S$) = 1% THEN PF_S$ = PF_S$ + "0"
690 PF% = VAL(LEFT$(PF_S$, 2%)) \ BP_OUT% = PW% * 100% + PF% \ GOTO 696
694 PW% = VAL(PCT_IN$) \ BP_OUT% = PW% * 100%
696 RETURN
697 OPEN DB_FILE$ FOR OUTPUT AS FILE #2% \ ASI% = 1%
698 IF ASI% > NUM_CP% THEN GOTO 704
699 PRINT #2%, CP_CODE$(ASI%); "|"; CP_PCT$(ASI%); "|"; CP_UNIT$(ASI%); "|"; CP_VAL%(ASI%); "|"; CP_STAT$(ASI%); "|"; CP_DESC$(ASI%)
702 ASI% = ASI% + 1% \ GOTO 698
704 CLOSE #2% \ RETURN
700 NUM_CP% = 3%
710 CP_CODE$(1%) = "K9$m#2" \ CP_PCT$(1%) = "25.50" \ CP_BP%(1%) = 2550% \ CP_UNIT$(1%) = "DAYS" \ CP_VAL%(1%) = 30% \ CP_STAT$(1%) = "ACTIVE" \ CP_DESC$(1%) = "Spring 25.50% Promo"
720 CP_CODE$(2%) = "V7!p@4" \ CP_PCT$(2%) = "50.00" \ CP_BP%(2%) = 5000% \ CP_UNIT$(2%) = "MONTHS" \ CP_VAL%(2%) = 6% \ CP_STAT$(2%) = "ACTIVE" \ CP_DESC$(2%) = "6-Month Half-Price Pass"
730 CP_CODE$(3%) = "Z3*q~8" \ CP_PCT$(3%) = "100.00" \ CP_BP%(3%) = 10000% \ CP_UNIT$(3%) = "NEVER" \ CP_VAL%(3%) = 0% \ CP_STAT$(3%) = "ACTIVE" \ CP_DESC$(3%) = "DEC Museum Lifetime Grant"
740 GOSUB 697 \ PRINT "[Sample SYSTEM Coupon dataset loaded - 3 promotional codes]" \ GOTO 495
820 IF NUM_CP% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Legacy Computing Systems - Active & Registered Discount Coupons (SYSTEM)" \ PRINT SEP$
840 LI% = 1%
850 IF LI% > NUM_CP% THEN GOTO 920
860 IF CP_UNIT$(LI%) = "NEVER" THEN PRINT "  Code: "; CP_CODE$(LI%); " | "; CP_PCT$(LI%); "% OFF | NEVER EXPIRES | ["; CP_STAT$(LI%); "] | "; CP_DESC$(LI%)
870 IF CP_UNIT$(LI%) = "DAYS" THEN PRINT "  Code: "; CP_CODE$(LI%); " | "; CP_PCT$(LI%); "% OFF | DAYS: "; CP_VAL%(LI%); " | ["; CP_STAT$(LI%); "] | "; CP_DESC$(LI%)
880 IF CP_UNIT$(LI%) = "MONTHS" THEN PRINT "  Code: "; CP_CODE$(LI%); " | "; CP_PCT$(LI%); "% OFF | MONTHS: "; CP_VAL%(LI%); " | ["; CP_STAT$(LI%); "] | "; CP_DESC$(LI%)
900 LI% = LI% + 1% \ GOTO 850
920 PRINT SEP$ \ PRINT "  [Total Coupons: "; NUM_CP%; " | Database: "; DB_FILE$; "]" \ PRINT EQU$ \ GOTO 495
980 ARGS$ = "AUTO, " + ARGS$
1000 IF NUM_CP% >= 30% THEN GOTO 1230
1010 C1% = INSTR(1%, ARGS$, ",")
1020 IF C1% = 0% THEN GOTO 1210
1030 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ IN_CODE$ = T_OUT$
1040 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%)
1050 U_IN$ = IN_CODE$ \ GOSUB 580 \ UP_CODE$ = U_OUT$
1060 IF UP_CODE$ = "AUTO" OR UP_CODE$ = "RANDOM" THEN GOSUB 640
1065 IF UP_CODE$ = "AUTO" OR UP_CODE$ = "RANDOM" THEN IN_CODE$ = GEN_CODE$
1070 IF LEN(IN_CODE$) <> 6% THEN GOTO 1215
1080 C2% = INSTR(1%, REM1$, ",")
1090 IF C2% = 0% THEN GOTO 1210
1100 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ IN_PCT$ = T_OUT$
1110 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%)
1115 PCT_IN$ = IN_PCT$ \ GOSUB 682 \ IN_BP% = BP_OUT%
1120 IF IN_BP% <= 0% OR IN_BP% > 10000% THEN GOTO 1220
1125 C3% = INSTR(1%, REM2$, ",")
1130 IF C3% = 0% THEN GOTO 1150
1135 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ IN_UNIT$ = U_OUT$
1140 REM3$ = MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%) \ GOTO 1155
1150 T_IN$ = REM2$ \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ IN_UNIT$ = U_OUT$ \ REM3$ = "0, Promotional Discount"
1155 C4% = INSTR(1%, REM3$, ",")
1160 IF C4% = 0% THEN GOTO 1175
1165 IN_VAL% = VAL(LEFT$(REM3$, C4% - 1%)) \ T_IN$ = MID$(REM3$, C4% + 1%, LEN(REM3$) - C4%) \ GOSUB 500 \ IN_DESC$ = T_OUT$ \ GOTO 1180
1175 IN_VAL% = VAL(REM3$) \ IN_DESC$ = "LCS Promotional Discount"
1180 IF IN_UNIT$ = "NEVER" THEN IN_VAL% = 0%
1182 IF IN_UNIT$ = "NEVER" THEN GOTO 1196
1184 IF IN_UNIT$ = "DAYS" THEN GOTO 1190
1186 IF IN_UNIT$ = "MONTHS" THEN GOTO 1193
1188 GOTO 1225
1190 IF IN_VAL% < 1% OR IN_VAL% > 365% THEN GOTO 1222
1192 GOTO 1196
1193 IF IN_VAL% < 1% OR IN_VAL% > 12% THEN GOTO 1224
1196 NUM_CP% = NUM_CP% + 1% \ CP_CODE$(NUM_CP%) = IN_CODE$ \ CP_PCT$(NUM_CP%) = IN_PCT$ \ CP_BP%(NUM_CP%) = IN_BP% \ CP_UNIT$(NUM_CP%) = IN_UNIT$ \ CP_VAL%(NUM_CP%) = IN_VAL% \ CP_STAT$(NUM_CP%) = "ACTIVE" \ CP_DESC$(NUM_CP%) = IN_DESC$
1200 GOSUB 697 \ PRINT "[Coupon Created: "; IN_CODE$; " | "; IN_PCT$; "% OFF | Duration="; IN_UNIT$; " ("; IN_VAL%; ") | Status=ACTIVE]" \ GOTO 495
1210 PRINT "COUPON: Syntax is CREATE <code|AUTO>, <pct>, <NEVER|DAYS|MONTHS>, <val>, <desc>" \ GOTO 495
1215 PRINT "COUPON: Error - Coupon code must be 6 characters (alphanumeric + special chars)" \ GOTO 495
1220 PRINT "COUPON: Error - Discount percent must be > 0.00 and <= 100.00" \ GOTO 495
1222 PRINT "COUPON: Error - DAYS duration must be between 1 and 365 (max 1 year)" \ GOTO 495
1224 PRINT "COUPON: Error - MONTHS duration must be between 1 and 12 (max 1 year)" \ GOTO 495
1225 PRINT "COUPON: Error - Duration unit must be NEVER, DAYS, or MONTHS" \ GOTO 495
1230 PRINT "COUPON: Coupon table full (max 30)" \ GOTO 495
1250 IF NUM_CP% = 0% THEN GOTO 3370
1255 C1% = INSTR(1%, ARGS$, ",") \ BASE_PR% = 10%
1260 IF C1% = 0% THEN GOTO 1275
1265 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ V_CODE$ = T_OUT$
1270 BASE_PR% = VAL(MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%)) \ GOTO 1280
1275 T_IN$ = ARGS$ \ GOSUB 500 \ V_CODE$ = T_OUT$
1280 IF BASE_PR% <= 0% THEN BASE_PR% = 10%
1285 FI% = 0% \ LI% = 1%
1290 IF LI% > NUM_CP% THEN GOTO 1320
1300 IF CP_CODE$(LI%) = V_CODE$ THEN FI% = LI%
1310 LI% = LI% + 1% \ GOTO 1290
1320 IF FI% = 0% THEN GOTO 1380
1330 IF CP_STAT$(FI%) <> "ACTIVE" THEN GOTO 1385
1340 ORIG_C% = BASE_PR% * 100% \ DISC_C% = INT((BASE_PR% * CP_BP%(FI%) + 50%) / 100%) \ FIN_C% = ORIG_C% - DISC_C%
1345 IF FIN_C% < 0% THEN FIN_C% = 0%
1350 DD% = INT(DISC_C% / 100%) \ DC% = DISC_C% - DD% * 100% \ FD% = INT(FIN_C% / 100%) \ FC% = FIN_C% - FD% * 100%
1360 PRINT EQU$ \ PRINT "  [COUPON VALIDATED] Code: "; CP_CODE$(FI%); " ("; CP_PCT$(FI%); "% OFF - "; CP_DESC$(FI%); ")"
1365 PRINT "  Original Price: $"; BASE_PR%; ".00 | Discount: -$"; DD%; "."; DC%; " | Final Price: $"; FD%; "."; FC%; " / month"
1370 PRINT EQU$ \ GOTO 495
1380 PRINT "COUPON: Code not found: "; V_CODE$ \ GOTO 495
1385 PRINT "COUPON: Code "; V_CODE$; " is currently "; CP_STAT$(FI%) \ GOTO 495
1400 NEW_ST$ = "DISABLED" \ GOTO 1410
1405 NEW_ST$ = "ACTIVE"
1410 IF NUM_CP% = 0% THEN GOTO 3370
1415 T_IN$ = ARGS$ \ GOSUB 500 \ TGT_C$ = T_OUT$ \ FI% = 0% \ LI% = 1%
1420 IF LI% > NUM_CP% THEN GOTO 1440
1425 IF CP_CODE$(LI%) = TGT_C$ THEN FI% = LI%
1430 LI% = LI% + 1% \ GOTO 1420
1440 IF FI% = 0% THEN GOTO 1380
1445 CP_STAT$(FI%) = NEW_ST$ \ GOSUB 697 \ PRINT "[Coupon "; CP_CODE$(FI%); " status set to "; NEW_ST$; "]" \ GOTO 495
1460 IF NUM_CP% = 0% THEN GOTO 3370
1465 T_IN$ = ARGS$ \ GOSUB 500 \ TGT_C$ = T_OUT$ \ FI% = 0% \ LI% = 1%
1470 IF LI% > NUM_CP% THEN GOTO 1490
1475 IF CP_CODE$(LI%) = TGT_C$ THEN FI% = LI%
1480 LI% = LI% + 1% \ GOTO 1470
1490 IF FI% = 0% THEN GOTO 1380
1495 SI% = FI%
1500 IF SI% >= NUM_CP% THEN GOTO 1525
1505 CP_CODE$(SI%) = CP_CODE$(SI% + 1%) \ CP_PCT$(SI%) = CP_PCT$(SI% + 1%) \ CP_BP%(SI%) = CP_BP%(SI% + 1%) \ CP_UNIT$(SI%) = CP_UNIT$(SI% + 1%)
1510 CP_VAL%(SI%) = CP_VAL%(SI% + 1%) \ CP_STAT$(SI%) = CP_STAT$(SI% + 1%) \ CP_DESC$(SI%) = CP_DESC$(SI% + 1%)
1515 SI% = SI% + 1% \ GOTO 1500
1525 NUM_CP% = NUM_CP% - 1% \ GOSUB 697 \ PRINT "[Coupon "; TGT_C$; " deleted]" \ GOTO 495
1550 SV_FILE$ = DB_FILE$
1560 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1570 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1580 IF SI% > NUM_CP% THEN GOTO 1620
1590 PRINT #2%, CP_CODE$(SI%); "|"; CP_PCT$(SI%); "|"; CP_UNIT$(SI%); "|"; CP_VAL%(SI%); "|"; CP_STAT$(SI%); "|"; CP_DESC$(SI%)
1610 SI% = SI% + 1% \ GOTO 1580
1620 CLOSE #2% \ PRINT "["; NUM_CP%; " coupon records saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_CP% = 0%
1735 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1735
1745 P1% = INSTR(1%, T_OUT$, PIPE$)
1750 IF P1% = 0% THEN GOTO 1735
1755 FC$ = LEFT$(T_OUT$, P1% - 1%) \ R1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, R1$, PIPE$)
1760 IF P2% = 0% THEN GOTO 1735
1765 FP$ = LEFT$(R1$, P2% - 1%) \ R2$ = MID$(R1$, P2% + 1%, LEN(R1$) - P2%) \ P3% = INSTR(1%, R2$, PIPE$)
1770 IF P3% = 0% THEN GOTO 1735
1775 FU$ = LEFT$(R2$, P3% - 1%) \ R3$ = MID$(R2$, P3% + 1%, LEN(R2$) - P3%) \ P4% = INSTR(1%, R3$, PIPE$)
1780 IF P4% = 0% THEN GOTO 1735
1785 FV% = VAL(LEFT$(R3$, P4% - 1%)) \ R4$ = MID$(R3$, P4% + 1%, LEN(R3$) - P4%) \ P5% = INSTR(1%, R4$, PIPE$)
1790 IF P5% = 0% THEN GOTO 1735
1795 FS$ = LEFT$(R4$, P5% - 1%) \ FD$ = MID$(R4$, P5% + 1%, LEN(R4$) - P5%)
1798 PCT_IN$ = FP$ \ GOSUB 682
1800 NUM_CP% = NUM_CP% + 1% \ CP_CODE$(NUM_CP%) = FC$ \ CP_PCT$(NUM_CP%) = FP$ \ CP_BP%(NUM_CP%) = BP_OUT% \ CP_UNIT$(NUM_CP%) = FU$ \ CP_VAL%(NUM_CP%) = FV% \ CP_STAT$(NUM_CP%) = FS$ \ CP_DESC$(NUM_CP%) = FD$ \ GOTO 1735
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_CP%; " coupon records loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Legacy Computing Systems - SYSTEM Coupon Manager V1.0 Status:"
1960 PRINT "  Authorized Account: SYSTEM ([1,2] RSTS/E | [1,4] VAX/VMS)"
1970 PRINT "  Active Database:    "; DB_FILE$; " (Coupons: "; NUM_CP%; ")" \ GOTO 495
2050 NUM_CP% = 0% \ PRINT "[Coupon table cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Legacy Computing Systems - SYSTEM Coupon Manager V1.0 Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / LIST                        Load sample coupons or list all coupons"
3020 PRINT "  CREATE <code|AUTO>,<pct>,<unit>,<v>,<d> Create 6-char coupon (NEVER|DAYS|MONTHS)"
3030 PRINT "  GENERATE <pct>,<unit>,<val>,<desc>   Auto-generate 6-char random coupon"
3040 PRINT "  VALIDATE <code> [, <price>]          Validate coupon & compute discounted price"
3050 PRINT "  DISABLE <code> / ENABLE <code>       Suspend or reactivate a coupon code"
3060 PRINT "  DELETE <code> / CLEAR                Delete a coupon code or clear table"
3070 PRINT "  SAVE [file] / LOAD [file] / STATUS   Save/load COUPON.DAT or show status" \ PRINT EQU$ \ GOTO 495
3370 PRINT "COUPON: No coupons in table. Use SAMPLE, CREATE, GENERATE, or LOAD." \ GOTO 495
3400 END
