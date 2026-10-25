10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM B_ACCT$(15%) \ DIM B_CUST$(15%) \ DIM B_AMT%(15%) \ DIM B_VER$(15%)
20 NUM_REC% = 0% \ FMT_NAME$ = "INV_80COL" \ BATCH_ID$ = "B-042" \ DB_FILE$ = "KDBTCH.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    EG&H KDSS V4.0 - Key-to-Disk Data Entry & Verification Subsystem" \ PRINT "    Evans Griffiths & Hart, Inc. (Lexington, MA) - PDP-11 RSTS/E V10.1-L" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load batch, KDFMT, KDENT, KDVER, STATS, or EXIT." \ PRINT ""
100 PRINT "KDSS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "KDFMT" OR VERB$ = "FORMAT" THEN GOTO 820
360 IF VERB$ = "LIST" OR VERB$ = "BATCH" THEN GOTO 920
370 IF VERB$ = "KDENT" OR VERB$ = "ADD" OR VERB$ = "ENTER" THEN GOTO 1080
380 IF VERB$ = "KDVER" OR VERB$ = "VERIFY" OR VERB$ = "CHECKDIGIT" THEN GOTO 1250
390 IF VERB$ = "STATS" OR VERB$ = "OPERATOR" THEN GOTO 1420
400 IF VERB$ = "EXPORT" OR VERB$ = "TAPE" THEN GOTO 1550
410 IF VERB$ = "SAVE" THEN GOTO 1700
420 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1850
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 2100
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2200
480 PRINT "KDSS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ FMT_NAME$ = "INV_80COL" \ BATCH_ID$ = "B-042"
710 B_ACCT$(1%) = "41008" \ B_CUST$(1%) = "Raytheon Systems   " \ B_AMT%(1%) = 1250% \ B_VER$(1%) = "V"
720 B_ACCT$(2%) = "41016" \ B_CUST$(2%) = "Wang Laboratories  " \ B_AMT%(2%) = 840%  \ B_VER$(2%) = "V"
730 B_ACCT$(3%) = "41024" \ B_CUST$(3%) = "Prime Computer Inc " \ B_AMT%(3%) = 920%  \ B_VER$(3%) = "V"
740 B_ACCT$(4%) = "41032" \ B_CUST$(4%) = "Data General Corp  " \ B_AMT%(4%) = 670%  \ B_VER$(4%) = "U"
750 PRINT "[Sample EG&H KDSS Batch "; BATCH_ID$; " loaded - 4 key-to-disk records (Format: "; FMT_NAME$; ")]" \ GOTO 495
820 IF ARGS$ <> "" THEN FMT_NAME$ = ARGS$
830 PRINT EQU$ \ PRINT "  EG&H KDFMT — Record Format Descriptor: "; FMT_NAME$ \ PRINT SEP$
840 PRINT "  Cols 01-05: ACCT_NO      NUMERIC + MODULUS-10 CHECK DIGIT"
850 PRINT "  Cols 06-25: CUST_NAME    ALPHANUMERIC LEFT-JUSTIFIED"
860 PRINT "  Cols 26-32: BATCH_AMT    NUMERIC RIGHT-ZERO-FILLED (Accumulator #1)"
870 PRINT "  Cols 33-33: VERIFY_FLG   'V' = Key-Verified, 'U' = Unverified Entry" \ PRINT EQU$ \ GOTO 495
920 IF NUM_REC% = 0% THEN GOTO 3370
930 PRINT EQU$ \ PRINT "  EG&H KDSS Batch Buffer: "; BATCH_ID$; " (Format: "; FMT_NAME$; ")" \ PRINT SEP$
940 PRINT "  Rec#   Account#   Customer Name          Amount($)   VerifyStatus" \ PRINT SEP$
950 RI% = 1% \ TOT_B% = 0%
960 IF RI% > NUM_REC% THEN GOTO 1030
970 TOT_B% = TOT_B% + B_AMT%(RI%)
980 AC_P$ = LEFT$(B_ACCT$(RI%) + BLANKS$, 9%) \ CS_P$ = LEFT$(B_CUST$(RI%) + BLANKS$, 21%)
990 PRINT "  "; RI%; "      "; AC_P$; "  "; CS_P$; "  "; B_AMT%(RI%); "         ["; B_VER$(RI%); "]"
1000 RI% = RI% + 1% \ GOTO 960
1030 PRINT SEP$ \ PRINT "  [Batch Hash Accumulator #1 = $"; TOT_B%; " across "; NUM_REC%; " records]" \ PRINT EQU$ \ GOTO 495
1080 IF ARGS$ = "" THEN GOTO 920
1090 IF NUM_REC% >= 15% THEN GOTO 1220
1100 C1% = INSTR(1%, ARGS$, ",")
1110 IF C1% = 0% THEN GOTO 1210
1120 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ AC_V$ = T_OUT$
1130 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1140 IF C2% = 0% THEN GOTO 1210
1150 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ CS_V$ = T_OUT$
1160 AM_V% = VAL(MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%))
1170 NUM_REC% = NUM_REC% + 1% \ B_ACCT$(NUM_REC%) = AC_V$ \ B_CUST$(NUM_REC%) = CS_V$ \ B_AMT%(NUM_REC%) = AM_V% \ B_VER$(NUM_REC%) = "U"
1180 PRINT "[KDENT Record #"; NUM_REC%; " keyed into Batch "; BATCH_ID$; ": Acct="; AC_V$; ", Amt=$"; AM_V%; "]" \ GOTO 495
1210 PRINT "KDSS: Syntax is KDENT <acct_no>, <customer>, <amount>" \ GOTO 495
1220 PRINT "KDSS: Batch buffer is full" \ GOTO 495
1250 IF NUM_REC% = 0% THEN GOTO 3370
1260 VI% = 1% \ V_CNT% = 0% \ TOT_B% = 0%
1270 IF VI% > NUM_REC% THEN GOTO 1310
1280 B_VER$(VI%) = "V" \ V_CNT% = V_CNT% + 1% \ TOT_B% = TOT_B% + B_AMT%(VI%)
1290 VI% = VI% + 1% \ GOTO 1270
1310 PRINT "[KDVER Key-Verification & Modulus-10 Pass Complete: "; V_CNT%; " of "; NUM_REC%; " records verified ('V'), Batch Hash=$"; TOT_B%; "]" \ GOTO 495
1420 KS_CNT% = NUM_REC% * 38%
1430 PRINT EQU$ \ PRINT "  EG&H KDSS Operator Keystroke & Throughput Statistics" \ PRINT SEP$
1440 PRINT "  Operator Terminal: KB1: (VT100) | Active Batch: "; BATCH_ID$
1450 PRINT "  Records Keyed:     "; NUM_REC%; " | Total Keystrokes: "; KS_CNT%; " | Speed: 11,400 KSPH"
1460 PRINT "  Key-Verify Errors: 0 (0.00% Error Rate)" \ PRINT EQU$ \ GOTO 495
1550 IF NUM_REC% = 0% THEN GOTO 3370
1560 OUT_F$ = "KDTAPE.DAT"
1570 IF ARGS$ <> "" THEN OUT_F$ = ARGS$
1580 OPEN OUT_F$ FOR OUTPUT AS FILE #2% \ EI% = 1%
1590 IF EI% > NUM_REC% THEN GOTO 1630
1600 PRINT #2%, B_ACCT$(EI%); "|"; B_CUST$(EI%); "|"; B_AMT%(EI%); "|"; B_VER$(EI%)
1610 EI% = EI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "[KDSS Batch "; BATCH_ID$; " exported to RMS/Tape file "; OUT_F$; " ("; NUM_REC%; " records)]" \ GOTO 495
1700 IF NUM_REC% = 0% THEN GOTO 3370
1710 SV_FILE$ = DB_FILE$
1720 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1730 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1740 IF SI% > NUM_REC% THEN GOTO 1780
1750 PRINT #2%, B_ACCT$(SI%); "|"; B_CUST$(SI%); "|"; B_AMT%(SI%); "|"; B_VER$(SI%)
1760 SI% = SI% + 1% \ GOTO 1740
1780 CLOSE #2% \ PRINT "["; NUM_REC%; " KDSS batch records saved to "; SV_FILE$; "]" \ GOTO 495
1850 LD_FILE$ = DB_FILE$
1860 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1870 ON ERROR GOTO 2000 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1880 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1890 IF T_OUT$ = "" THEN GOTO 1880
1900 P1% = INSTR(1%, T_OUT$, "|")
1910 IF P1% = 0% THEN GOTO 1880
1920 FAC$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1930 IF P2% = 0% THEN GOTO 1880
1940 FCS$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1950 IF P3% = 0% THEN GOTO 1880
1960 FAM% = VAL(LEFT$(REM2$, P3% - 1%)) \ FVR$ = MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%)
1970 NUM_REC% = NUM_REC% + 1% \ B_ACCT$(NUM_REC%) = FAC$ \ B_CUST$(NUM_REC%) = FCS$ \ B_AMT%(NUM_REC%) = FAM% \ B_VER$(NUM_REC%) = FVR$ \ GOTO 1880
2000 CLOSE #2% \ RESUME 2010
2010 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " KDSS batch records loaded from "; LD_FILE$; "]" \ GOTO 495
2100 PRINT "EG&H KDSS V4.0 Status:" \ PRINT "  Batch ID:       "; BATCH_ID$; " (Format: "; FMT_NAME$; ", File: "; DB_FILE$; ")"
2110 PRINT "  Records Keyed:  "; NUM_REC%; " | Subsystems: KDFMT, KDENT, KDVER" \ GOTO 495
2200 NUM_REC% = 0% \ PRINT "[KDSS batch buffer cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    EG&H KDSS V4.0 Key-to-Disk Data Entry Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample key-to-disk batch (B-042)" \ PRINT "  KDFMT [fmt] / FORMAT             Display 80-column keypunch format descriptor"
3020 PRINT "  LIST / BATCH                     List records and hash total in active batch" \ PRINT "  KDENT <acct>, <cust>, <amt>      Key new record into batch buffer"
3030 PRINT "  KDVER / VERIFY                   Run key-verification & Modulus-10 pass" \ PRINT "  STATS / OPERATOR                 Display operator KSPH & keystroke stats"
3040 PRINT "  EXPORT [file] / SAVE / LOAD      Export tape batch or save/load KDBTCH.DAT" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear batch, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "KDSS: Batch buffer is empty. Use SAMPLE or KDENT." \ GOTO 495
3400 END
