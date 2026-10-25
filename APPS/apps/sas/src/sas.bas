10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM S_ID$(15%) \ DIM S_GRP$(15%) \ DIM S_DOSE%(15%) \ DIM S_RESP%(15%)
20 NUM_OBS% = 0% \ DB_FILE$ = "SASLIB.DAT" \ DS_NAME$ = "WORK.CLINICAL"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    SAS System V6.06 for VAX/VMS - DATA Step & Statistical PROCs" \ PRINT "    SAS Institute, Inc. (Cary, NC) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load SAS dataset, PRINT, MEANS, FREQ, REG, or ENDSAS." \ PRINT ""
100 PRINT "SAS> "; \ LINE INPUT RAW_INPUT$
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
320 IF VERB$ = "EXIT" OR VERB$ = "QUIT" OR VERB$ = "ENDSAS" OR VERB$ = "BYE" THEN GOTO 3400
330 IF VERB$ = "HELP" OR VERB$ = "?" THEN GOTO 3000
340 IF VERB$ = "SAMPLE" OR VERB$ = "DEMO" OR VERB$ = "DATA" THEN GOTO 700
350 IF VERB$ = "PRINT" OR VERB$ = "LIST" THEN GOTO 820
360 IF VERB$ = "MEANS" OR VERB$ = "SUMMARY" THEN GOTO 960
370 IF VERB$ = "FREQ" OR VERB$ = "TABLES" THEN GOTO 1120
380 IF VERB$ = "REG" OR VERB$ = "GLM" THEN GOTO 1250
390 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
400 IF VERB$ = "SAVE" THEN GOTO 1550
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" OR VERB$ = "CONTENTS" THEN GOTO 1950
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "SAS: ERROR 180-322: Statement '"; VERB$; "' is not valid. Type HELP."
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
700 NUM_OBS% = 4%
710 S_ID$(1%) = "SUBJ-01" \ S_GRP$(1%) = "ACTIVE" \ S_DOSE%(1%) = 10% \ S_RESP%(1%) = 45%
720 S_ID$(2%) = "SUBJ-02" \ S_GRP$(2%) = "PLACEB" \ S_DOSE%(2%) = 20% \ S_RESP%(2%) = 65%
730 S_ID$(3%) = "SUBJ-03" \ S_GRP$(3%) = "ACTIVE" \ S_DOSE%(3%) = 30% \ S_RESP%(3%) = 85%
740 S_ID$(4%) = "SUBJ-04" \ S_GRP$(4%) = "ACTIVE" \ S_DOSE%(4%) = 40% \ S_RESP%(4%) = 105%
750 PRINT "NOTE: The data set WORK.CLINICAL has 4 observations and 4 variables." \ GOTO 495
820 IF NUM_OBS% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  The SAS System — PROC PRINT DATA="; DS_NAME$ \ PRINT SEP$
840 PRINT "  OBS    ID         GROUP     DOSE_MG    RESPONSE" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_OBS% THEN GOTO 920
870 I_P$ = LEFT$(S_ID$(LI%) + BLANKS$, 9%) \ G_P$ = LEFT$(S_GRP$(LI%) + BLANKS$, 8%)
880 PRINT "  "; LI%; "     "; I_P$; "  "; G_P$; "  "; S_DOSE%(LI%); "         "; S_RESP%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_OBS% = 0% THEN GOTO 3370
970 MI% = 1% \ D_SUM% = 0% \ R_SUM% = 0% \ R_MIN% = S_RESP%(1%) \ R_MAX% = S_RESP%(1%)
980 IF MI% > NUM_OBS% THEN GOTO 1050
990 D_SUM% = D_SUM% + S_DOSE%(MI%) \ R_SUM% = R_SUM% + S_RESP%(MI%)
1000 IF S_RESP%(MI%) < R_MIN% THEN R_MIN% = S_RESP%(MI%)
1010 IF S_RESP%(MI%) > R_MAX% THEN R_MAX% = S_RESP%(MI%)
1020 MI% = MI% + 1% \ GOTO 980
1050 D_MEAN% = INT(D_SUM% / NUM_OBS%) \ R_MEAN% = INT(R_SUM% / NUM_OBS%)
1060 PRINT EQU$ \ PRINT "  The SAS System — PROC MEANS DATA="; DS_NAME$ \ PRINT SEP$
1070 PRINT "  Variable   N          Mean           Min           Max           Sum" \ PRINT SEP$
1080 PRINT "  DOSE_MG    "; NUM_OBS%; "          "; D_MEAN%; "             "; S_DOSE%(1%); "            "; S_DOSE%(NUM_OBS%); "            "; D_SUM%
1090 PRINT "  RESPONSE   "; NUM_OBS%; "          "; R_MEAN%; "             "; R_MIN%; "            "; R_MAX%; "           "; R_SUM%
1100 PRINT SEP$ \ PRINT "  [SAS PROC MEANS: N="; NUM_OBS%; " | RESPONSE Mean="; R_MEAN%; " | Min="; R_MIN%; " | Max="; R_MAX%; " | Sum="; R_SUM%; "]" \ PRINT EQU$ \ GOTO 495
1120 IF NUM_OBS% = 0% THEN GOTO 3370
1130 FI% = 1% \ ACT_C% = 0% \ PLC_C% = 0%
1140 IF FI% > NUM_OBS% THEN GOTO 1190
1150 IF S_GRP$(FI%) = "ACTIVE" THEN ACT_C% = ACT_C% + 1%
1160 IF S_GRP$(FI%) <> "ACTIVE" THEN PLC_C% = PLC_C% + 1%
1170 FI% = FI% + 1% \ GOTO 1140
1190 ACT_PCT% = INT(ACT_C% * 100% / NUM_OBS%) \ PLC_PCT% = 100% - ACT_PCT%
1200 PRINT "[SAS PROC FREQ TABLE GROUP: ACTIVE="; ACT_C%; " ("; ACT_PCT%; "%) | OTHER="; PLC_C%; " ("; PLC_PCT%; "%)]" \ GOTO 495
1250 IF NUM_OBS% < 2% THEN GOTO 3370
1260 DX% = S_DOSE%(NUM_OBS%) - S_DOSE%(1%) \ DY% = S_RESP%(NUM_OBS%) - S_RESP%(1%)
1270 IF DX% = 0% THEN DX% = 1%
1280 SLOPE% = INT(DY% / DX%) \ INTER% = S_RESP%(1%) - SLOPE% * S_DOSE%(1%)
1290 PRINT EQU$ \ PRINT "  The SAS System — PROC REG DATA="; DS_NAME$; " (MODEL RESPONSE = DOSE_MG)" \ PRINT SEP$
1300 PRINT "  Parameter     DF     Estimate     F-Value    Prob>F     R-Square" \ PRINT SEP$
1310 PRINT "  INTERCEPT     1      "; INTER%; "           99.80      0.0001     0.9950"
1320 PRINT "  DOSE_MG       1      "; SLOPE%; "            99.80      0.0001     0.9950"
1330 PRINT SEP$ \ PRINT "  [SAS PROC REG Complete: RESPONSE = "; INTER%; " + "; SLOPE%; " * DOSE_MG | R-Square = 0.9950]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_OBS% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ I_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ G_V$ = U_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 DS_V% = VAL(LEFT$(REM2$, C3% - 1%)) \ RS_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_OBS% = NUM_OBS% + 1% \ S_ID$(NUM_OBS%) = I_V$ \ S_GRP$(NUM_OBS%) = G_V$ \ S_DOSE%(NUM_OBS%) = DS_V% \ S_RESP%(NUM_OBS%) = RS_V%
1495 PRINT "[SAS DATA Step Observation #"; NUM_OBS%; " added: "; I_V$; " ("; G_V$; ", DOSE="; DS_V%; ", RESP="; RS_V%; ")]" \ GOTO 495
1500 PRINT "SAS: Syntax is ADD <subj_id>, <group>, <dose_mg>, <response>" \ GOTO 495
1510 PRINT "SAS: WORK.CLINICAL buffer full" \ GOTO 495
1550 IF NUM_OBS% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_OBS% THEN GOTO 1630
1600 PRINT #2%, S_ID$(SI%); "|"; S_GRP$(SI%); "|"; S_DOSE%(SI%); "|"; S_RESP%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_OBS%; " SAS observations saved to library "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_OBS% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FI$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FG$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FDS% = VAL(LEFT$(REM2$, P3% - 1%)) \ FRS% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_OBS% = NUM_OBS% + 1% \ S_ID$(NUM_OBS%) = FI$ \ S_GRP$(NUM_OBS%) = FG$ \ S_DOSE%(NUM_OBS%) = FDS% \ S_RESP%(NUM_OBS%) = FRS% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_OBS%; " SAS observations loaded from library "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "SAS System V6.06 for VAX/VMS Status:" \ PRINT "  Active Dataset: "; DS_NAME$; " | Library File: "; DB_FILE$; " (Obs: "; NUM_OBS%; ")" \ GOTO 495
2050 NUM_OBS% = 0% \ PRINT "[SAS dataset WORK.CLINICAL cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    SAS System V6.06 for VAX/VMS Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO / DATA             Load sample WORK.CLINICAL SAS dataset" \ PRINT "  PRINT / LIST                     Run PROC PRINT on active dataset"
3020 PRINT "  MEANS / SUMMARY                  Run PROC MEANS (N, Mean, Min, Max, Sum)" \ PRINT "  FREQ / TABLES                    Run PROC FREQ categorical distribution"
3030 PRINT "  REG / GLM                        Run PROC REG linear regression & ANOVA" \ PRINT "  ADD <id>, <grp>, <dose>, <resp>  Add observation to WORK.CLINICAL"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load SASLIB.DAT library" \ PRINT "  SHOW / CLEAR / ENDSAS            Show status, clear dataset, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "SAS: Dataset WORK.CLINICAL is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
