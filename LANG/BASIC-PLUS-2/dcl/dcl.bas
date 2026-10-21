10 ! ==============================================================================
20 ! DEC RSTS/E DCL (DIGITAL Command Language) & PBS Job Controller
30 ! Written in pure DEC BASIC-PLUS-2
40 ! ==============================================================================
50 DIM PROC_L$(500%)
60 DIM LBL_N$(50%)
70 DIM LBL_PC%(50%)
80 DIM SYM_N$(100%)
90 DIM SYM_V$(100%)
100 DIM LOG_N$(20%)
110 DIM LOG_V$(20%)
120 DIM TOK$(20%)
130 LET NUM_SYM% = 0%
140 LET NUM_LOG% = 0%
150 LET NUM_L% = 0%
160 LET NUM_LBL% = 0%
170 LET NUM_TOK% = 0%
180 LET VERIFY% = 0%
190 LET EXIT_REQ% = 0%
200 LET STATUS_CODE% = 0%
210 LET DEF_DIR$ = "."
220 LET PROC_DIR$ = ""
230 LET INP$ = ""
240 LET CMD_LINE$ = ""
250 LET CUR_LINE$ = ""
260 LET VERB$ = ""
270 LET REST$ = ""
280 LET Q_QUEUE$ = ""
290 LET Q_NAME$ = ""
300 LET Q_COPIES$ = "1"
310 LET Q_DELETE% = 0%
320 LET Q_ENTRY$ = ""
330 LET Q_ALL% = 0%
340 LET Q_FULL% = 0%
350 LET Q_OBJ$ = ""
360 LET Q_MOD$ = ""
370 LET Q_OUT$ = ""
380 LET Q_LOG$ = ""
390 LET S_NAME$ = ""
400 LET S_VAL$ = ""
410 LET RET_VAL$ = ""
420 LET TXT$ = ""
430 LET T1$ = ""
440 LET T2$ = ""
450 LET T3$ = ""
460 LET COND_STR$ = ""
470 LET THEN_STMT$ = ""
480 LET COND_TRUE% = 0%
490 LET RC% = 0%
500 LET I% = 0%
510 LET J% = 0%
520 LET K% = 0%
530 LET P% = 0%
540 LET L% = 0%
550 LET PC% = 0%
560 LET ONE_SHOT% = 0%
570 LET RAW_ARGS$ = ""
580 LET RET_MODE% = 0%
600 ! Initialize default symbols
610 LET NUM_SYM% = 11%
620 LET SYM_N$(1%) = "$STATUS"
622 LET SYM_V$(1%) = "1"
630 LET SYM_N$(2%) = "$SEVERITY"
632 LET SYM_V$(2%) = "1"
640 LET SYM_N$(3%) = "SYS$SYSTEM"
642 LET SYM_V$(3%) = "."
650 LET SYM_N$(4%) = "P1"
652 LET SYM_V$(4%) = ""
660 LET SYM_N$(5%) = "P2"
662 LET SYM_V$(5%) = ""
670 LET SYM_N$(6%) = "P3"
672 LET SYM_V$(6%) = ""
680 LET SYM_N$(7%) = "P4"
682 LET SYM_V$(7%) = ""
690 LET SYM_N$(8%) = "P5"
691 LET SYM_V$(8%) = ""
692 LET SYM_N$(9%) = "P6"
693 LET SYM_V$(9%) = ""
694 LET SYM_N$(10%) = "P7"
695 LET SYM_V$(10%) = ""
696 LET SYM_N$(11%) = "P8"
697 LET SYM_V$(11%) = ""
700 ! Initialize default logicals
710 LET NUM_LOG% = 4%
720 LET LOG_N$(1%) = "SYS$OUTPUT"
722 LET LOG_V$(1%) = "TT:"
730 LET LOG_N$(2%) = "SYS$INPUT"
732 LET LOG_V$(2%) = "TT:"
740 LET LOG_N$(3%) = "SYS$ERROR"
742 LET LOG_V$(3%) = "TT:"
750 LET LOG_N$(4%) = "SYS$SYSTEM"
752 LET LOG_V$(4%) = "."
800 ! Check Command Line Arguments via COMMAND$
810 LET RAW_ARGS$ = COMMAND$
820 FOR I% = 1% TO 20%
830   IF LEFT$(RAW_ARGS$, 1%) = " " THEN LET RAW_ARGS$ = RIGHT$(RAW_ARGS$, 2%)
840   IF RIGHT$(RAW_ARGS$, LEN(RAW_ARGS$)) = " " THEN LET RAW_ARGS$ = LEFT$(RAW_ARGS$, LEN(RAW_ARGS$) - 1%)
850 NEXT I%
860 IF RAW_ARGS$ = "" THEN GOTO 1200
870 IF LEFT$(RAW_ARGS$, 1%) = "@" THEN GOTO 1450
880 LET L% = LEN(RAW_ARGS$)
890 IF L% < 4% THEN GOTO 930
900 IF RIGHT$(RAW_ARGS$, L% - 3%) = ".COM" THEN GOTO 1460
902 IF RIGHT$(RAW_ARGS$, L% - 3%) = ".com" THEN GOTO 1460
910 IF RIGHT$(RAW_ARGS$, L% - 3%) = ".DCL" THEN GOTO 1460
912 IF RIGHT$(RAW_ARGS$, L% - 3%) = ".dcl" THEN GOTO 1460
920 ! Single command one-shot execution
930 LET ONE_SHOT% = 1%
940 LET CMD_LINE$ = RAW_ARGS$
950 LET RET_MODE% = 2%
960 GOTO 3000
1200 ! ==============================================================================
1210 ! Interactive Shell Mode
1220 ! ==============================================================================
1230 PRINT "DEC RSTS/E V10.1-L DCL (DIGITAL Command Language)"
1240 PRINT "Print/Batch Services (PBS) Active. Type HELP for commands."
1250 PRINT ""
1270 IF EXIT_REQ% = 1% THEN GOTO 9990
1280 PRINT "$ ";
1290 LINE INPUT INP$
1300 IF INP$ = CHR$(26%) THEN GOTO 9990
1310 FOR I% = 1% TO 20%
1320   IF LEFT$(INP$, 1%) = " " THEN LET INP$ = RIGHT$(INP$, 2%)
1330   IF RIGHT$(INP$, LEN(INP$)) = " " THEN LET INP$ = LEFT$(INP$, LEN(INP$) - 1%)
1340 NEXT I%
1350 IF INP$ = "" THEN GOTO 1270
1360 IF LEFT$(INP$, 1%) = "!" THEN GOTO 1270
1370 LET CMD_LINE$ = INP$
1380 LET RET_MODE% = 0%
1390 GOTO 3000
1450 LET PROC_FILE$ = RIGHT$(RAW_ARGS$, 2%)
1452 LET ONE_SHOT% = 1%
1454 GOTO 1500
1460 LET PROC_FILE$ = RAW_ARGS$
1462 LET ONE_SHOT% = 1%
1464 GOTO 1500
1500 ! ==============================================================================
1510 ! Command Procedure Execution (@file or .com or .dcl)
1520 ! ==============================================================================
1530 FOR I% = 1% TO 20%
1540   IF LEFT$(PROC_FILE$, 1%) = " " THEN LET PROC_FILE$ = RIGHT$(PROC_FILE$, 2%)
1550   IF RIGHT$(PROC_FILE$, LEN(PROC_FILE$)) = " " THEN LET PROC_FILE$ = LEFT$(PROC_FILE$, LEN(PROC_FILE$) - 1%)
1560 NEXT I%
1580 ! Extract procedure directory
1590 LET PROC_DIR$ = ""
1600 LET P% = 0%
1610 FOR I% = 1% TO LEN(PROC_FILE$)
1620   IF MID$(PROC_FILE$, I%, 1%) = "/" THEN LET P% = I%
1630 NEXT I%
1640 IF P% > 0% THEN LET PROC_DIR$ = LEFT$(PROC_FILE$, P%)
1660 ! Open procedure file
1662 IF SYS("test -f " + PROC_FILE$) = 0% THEN GOTO 1680
1664 IF SYS("test -f " + PROC_FILE$ + ".COM") = 0% THEN LET PROC_FILE$ = PROC_FILE$ + ".COM"
1666 IF SYS("test -f " + PROC_FILE$) = 0% THEN GOTO 1680
1668 IF SYS("test -f " + PROC_FILE$ + ".com") = 0% THEN LET PROC_FILE$ = PROC_FILE$ + ".com"
1670 IF SYS("test -f " + PROC_FILE$) = 0% THEN GOTO 1680
1672 IF SYS("test -f " + PROC_FILE$ + ".DCL") = 0% THEN LET PROC_FILE$ = PROC_FILE$ + ".DCL"
1674 IF SYS("test -f " + PROC_FILE$) = 0% THEN GOTO 1680
1676 IF SYS("test -f " + PROC_FILE$ + ".dcl") = 0% THEN LET PROC_FILE$ = PROC_FILE$ + ".dcl"
1678 IF SYS("test -f " + PROC_FILE$) = 0% THEN GOTO 1680
1680 IF SYS("test -f " + PROC_FILE$) <> 0% THEN GOTO 1750
1685 OPEN PROC_FILE$ FOR INPUT AS FILE #1%
1690 GOTO 1760
1750 PRINT "%DCL-E-OPENIN, error opening "; PROC_FILE$; " as input"
1754 PRINT "-RMS-E-FNF, file not found"
1755 IF ONE_SHOT% = 1% THEN GOTO 9990
1758 GOTO 1270
1760 ! Read procedure lines into PROC_L$
1770 LET NUM_L% = 0%
1780 LET NUM_LBL% = 0%
1790 ON ERROR GOTO 1840
1810 LINE INPUT #1%, TXT$
1820 LET NUM_L% = NUM_L% + 1%
1830 LET PROC_L$(NUM_L%) = TXT$
1835 GOTO 1810
1840 CLOSE #1%
1860 ! Scan for labels (Pass 1)
1880 FOR I% = 1% TO NUM_L%
1890   LET T1$ = PROC_L$(I%)
1900   FOR J% = 1% TO 20%
1910     IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
1920     IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
1930   NEXT J%
1940   IF LEFT$(T1$, 1%) = "$" THEN LET T1$ = RIGHT$(T1$, 2%)
1950   FOR J% = 1% TO 20%
1960     IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
1970     IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
1980   NEXT J%
1990   LET P% = INSTR(T1$, ":")
2000   IF P% <= 1% THEN GOTO 2040
2010   LET T2$ = LEFT$(T1$, P% - 1%)
2020   IF INSTR(T2$, " ") > 0% OR INSTR(T2$, "/") > 0% THEN GOTO 2040
2030   LET NUM_LBL% = NUM_LBL% + 1%
2032   LET LBL_N$(NUM_LBL%) = T2$
2034   LET LBL_PC%(NUM_LBL%) = I%
2040 NEXT I%
2060 ! Execute procedure lines loop
2070 LET PC% = 1%
2080 IF PC% > NUM_L% THEN GOTO 2900
2085 IF EXIT_REQ% = 1% THEN GOTO 2900
2090 LET CUR_LINE$ = PROC_L$(PC%)
2100 LET PC% = PC% + 1%
2110 LET T1$ = CUR_LINE$
2120 FOR J% = 1% TO 20%
2130   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
2140   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
2150 NEXT J%
2160 IF T1$ = "" THEN GOTO 2080
2170 IF VERIFY% = 1% THEN IF LEFT$(T1$, 1%) <> "!" THEN PRINT "$ "; T1$
2180 IF LEFT$(T1$, 1%) = "$" THEN LET T1$ = RIGHT$(T1$, 2%)
2190 FOR J% = 1% TO 20%
2200   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
2210   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
2220 NEXT J%
2230 IF T1$ = "" OR LEFT$(T1$, 1%) = "!" THEN GOTO 2080
2250 ! Check if line starts with label: strip it
2260 LET P% = INSTR(T1$, ":")
2270 IF P% <= 1% THEN GOTO 2350
2280 LET T2$ = LEFT$(T1$, P% - 1%)
2290 IF INSTR(T2$, " ") > 0% OR INSTR(T2$, "/") > 0% THEN GOTO 2350
2300 LET T1$ = RIGHT$(T1$, P% + 1%)
2310 FOR J% = 1% TO 20%
2320   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
2330   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
2340 NEXT J%
2350 IF T1$ = "" OR LEFT$(T1$, 1%) = "!" THEN GOTO 2080
2370 ! Check for IF statement in procedure
2380 IF LEFT$(T1$, 3%) = "IF " OR LEFT$(T1$, 3%) = "if " THEN GOTO 7000
2400 ! Check for GOTO statement in procedure
2410 IF LEFT$(T1$, 5%) = "GOTO " THEN GOTO 2420
2412 IF LEFT$(T1$, 5%) = "goto " THEN GOTO 2420
2414 GOTO 2430
2420 LET T2$ = RIGHT$(T1$, 6%)
2425 GOTO 7500
2430 ! Check for EXIT or STOP
2440 IF T1$ = "EXIT" OR T1$ = "STOP" OR T1$ = "exit" OR T1$ = "stop" THEN GOTO 2900
2460 ! Dispatch normal line in procedure
2470 LET CMD_LINE$ = T1$
2480 LET RET_MODE% = 1%
2490 GOTO 3000
2900 IF ONE_SHOT% = 1% THEN GOTO 9990
2910 GOTO 1270
3000 ! ==============================================================================
3010 ! Command Line Parser & Dispatcher
3020 ! ==============================================================================
3030 FOR I% = 1% TO 20%
3040   IF LEFT$(CMD_LINE$, 1%) = " " THEN LET CMD_LINE$ = RIGHT$(CMD_LINE$, 2%)
3050   IF RIGHT$(CMD_LINE$, LEN(CMD_LINE$)) = " " THEN LET CMD_LINE$ = LEFT$(CMD_LINE$, LEN(CMD_LINE$) - 1%)
3060 NEXT I%
3070 IF CMD_LINE$ = "" THEN GOTO 3990
3080 IF LEFT$(CMD_LINE$, 1%) = "$" THEN LET CMD_LINE$ = RIGHT$(CMD_LINE$, 2%)
3090 FOR I% = 1% TO 20%
3100   IF LEFT$(CMD_LINE$, 1%) = " " THEN LET CMD_LINE$ = RIGHT$(CMD_LINE$, 2%)
3110   IF RIGHT$(CMD_LINE$, LEN(CMD_LINE$)) = " " THEN LET CMD_LINE$ = LEFT$(CMD_LINE$, LEN(CMD_LINE$) - 1%)
3120 NEXT I%
3130 IF CMD_LINE$ = "" OR LEFT$(CMD_LINE$, 1%) = "!" THEN GOTO 3990
3150 ! Check for nested procedure call: @file
3160 IF LEFT$(CMD_LINE$, 1%) <> "@" THEN GOTO 3180
3162 LET PROC_FILE$ = RIGHT$(CMD_LINE$, 2%)
3165 GOTO 1500
3180 ! Check for Symbol Assignment: VAR = VAL or VAR := VAL
3190 IF LEFT$(CMD_LINE$, 3%) = "IF " OR LEFT$(CMD_LINE$, 3%) = "if " THEN GOTO 3300
3200 LET P% = INSTR(CMD_LINE$, "=")
3210 IF P% <= 1% THEN GOTO 3300
3220 LET T1$ = LEFT$(CMD_LINE$, P% - 1%)
3230 IF INSTR(T1$, ":") > 0% THEN LET T1$ = LEFT$(T1$, INSTR(T1$, ":") - 1%)
3240 FOR J% = 1% TO 20%
3250   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
3260   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
3270 NEXT J%
3280 LET S_NAME$ = T1$
3290 IF INSTR(S_NAME$, " ") > 0% OR INSTR(S_NAME$, "/") > 0% THEN GOTO 3300
3295 LET T2$ = RIGHT$(CMD_LINE$, P% + 1%)
3296 FOR J% = 1% TO 20%
3297   IF LEFT$(T2$, 1%) = " " THEN LET T2$ = RIGHT$(T2$, 2%)
3298   IF RIGHT$(T2$, LEN(T2$)) = " " THEN LET T2$ = LEFT$(T2$, LEN(T2$) - 1%)
3299 NEXT J%
3302 IF LEFT$(T2$, 1%) = CHR$(34%) AND RIGHT$(T2$, LEN(T2$)) = CHR$(34%) THEN LET T2$ = MID$(T2$, 2%, LEN(T2$) - 2%)
3304 IF LEFT$(T2$, 1%) = CHR$(39%) AND RIGHT$(T2$, LEN(T2$)) = CHR$(39%) THEN LET T2$ = MID$(T2$, 2%, LEN(T2$) - 2%)
3306 LET S_VAL$ = T2$
3308 GOTO 8000
3300 ! Tokenize Verb and Qualifiers
3320 LET Q_QUEUE$ = ""
3330 LET Q_NAME$ = ""
3340 LET Q_COPIES$ = "1"
3350 LET Q_DELETE% = 0%
3360 LET Q_ENTRY$ = ""
3370 LET Q_ALL% = 0%
3380 LET Q_FULL% = 0%
3390 LET Q_OBJ$ = ""
3400 LET Q_MOD$ = ""
3410 LET Q_OUT$ = ""
3420 LET Q_LOG$ = ""
3425 LET Q_ACCT% = 0%
3430 LET NUM_TOK% = 0%
3450 ! Extract first word as candidate verb
3460 LET P% = INSTR(CMD_LINE$, " ")
3470 IF P% = 0% THEN LET VERB$ = CMD_LINE$
3472 IF P% = 0% THEN LET REST$ = ""
3474 IF P% > 0% THEN LET VERB$ = LEFT$(CMD_LINE$, P% - 1%)
3476 IF P% > 0% THEN LET REST$ = RIGHT$(CMD_LINE$, P% + 1%)
3478 LET RAW_REST$ = REST$
3490 ! Check attached qualifier on verb: VERB/QUAL=VAL
3500 LET P% = INSTR(VERB$, "/")
3502 IF P% <= 1% THEN GOTO 3530
3505 LET T1$ = RIGHT$(VERB$, P%)
3510 LET VERB$ = LEFT$(VERB$, P% - 1%)
3515 LET REST$ = T1$ + " " + REST$
3518 LET RAW_REST$ = REST$
3530 ! Uppercase VERB$
3540 FOR K% = 1% TO LEN(VERB$)
3550   LET P% = ASCII(MID$(VERB$, K%, 1%))
3560   IF P% >= 97% AND P% <= 122% THEN VERB$ = LEFT$(VERB$, K% - 1%) + CHR$(P% - 32%) + RIGHT$(VERB$, K% + 1%)
3570 NEXT K%
3590 ! Trim REST$
3600 FOR J% = 1% TO 20%
3610   IF LEFT$(REST$, 1%) = " " THEN LET REST$ = RIGHT$(REST$, 2%)
3620   IF RIGHT$(REST$, LEN(REST$)) = " " THEN LET REST$ = LEFT$(REST$, LEN(REST$) - 1%)
3630 NEXT J%
3650 ! Loop parsing arguments from REST$
3660 FOR J% = 1% TO 10%
3670   IF REST$ = "" THEN GOTO 3850
3680   LET P% = INSTR(REST$, " ")
3690   IF P% = 0% THEN LET T1$ = REST$
3692   IF P% = 0% THEN LET REST$ = ""
3694   IF P% > 0% THEN LET T1$ = LEFT$(REST$, P% - 1%)
3696   IF P% > 0% THEN LET REST$ = RIGHT$(REST$, P% + 1%)
3700   FOR K% = 1% TO 20%
3702     IF LEFT$(REST$, 1%) = " " THEN LET REST$ = RIGHT$(REST$, 2%)
3704     IF RIGHT$(REST$, LEN(REST$)) = " " THEN LET REST$ = LEFT$(REST$, LEN(REST$) - 1%)
3706   NEXT K%
3720   ! Check attached qualifier on argument: e.g. SALES.RPT/DELETE
3722   LET P% = INSTR(T1$, "/DELETE")
3724   IF P% <= 1% THEN LET P% = INSTR(T1$, "/delete")
3726   IF P% <= 1% THEN GOTO 3740
3728   LET Q_DELETE% = 1%
3730   LET T1$ = LEFT$(T1$, P% - 1%)
3740   IF LEFT$(T1$, 1%) = "/" THEN GOTO 3780
3750   IF T1$ = "" THEN GOTO 3840
3760   LET NUM_TOK% = NUM_TOK% + 1%
3765   LET TOK$(NUM_TOK%) = T1$
3770   GOTO 3840
3780   ! Parse qualifier in T1$
3800   LET T2$ = T1$
3802   FOR K% = 1% TO LEN(T2$)
3804     LET P% = ASCII(MID$(T2$, K%, 1%))
3806     IF P% >= 97% AND P% <= 122% THEN T2$ = LEFT$(T2$, K% - 1%) + CHR$(P% - 32%) + RIGHT$(T2$, K% + 1%)
3808   NEXT K%
3810   IF LEFT$(T2$, 7%) = "/QUEUE=" THEN LET Q_QUEUE$ = RIGHT$(T1$, 8%)
3812   IF LEFT$(T2$, 7%) = "/QUEUE:" THEN LET Q_QUEUE$ = RIGHT$(T1$, 8%)
3814   IF LEFT$(T2$, 6%) = "/NAME="  THEN LET Q_NAME$ = RIGHT$(T1$, 7%)
3816   IF LEFT$(T2$, 6%) = "/NAME:"  THEN LET Q_NAME$ = RIGHT$(T1$, 7%)
3818   IF LEFT$(T2$, 8%) = "/COPIES=" THEN LET Q_COPIES$ = RIGHT$(T1$, 9%)
3820   IF LEFT$(T2$, 8%) = "/COPIES:" THEN LET Q_COPIES$ = RIGHT$(T1$, 9%)
3822   IF T2$ = "/DELETE" THEN LET Q_DELETE% = 1%
3824   IF LEFT$(T2$, 7%) = "/ENTRY=" THEN LET Q_ENTRY$ = RIGHT$(T1$, 8%)
3826   IF LEFT$(T2$, 7%) = "/ENTRY:" THEN LET Q_ENTRY$ = RIGHT$(T1$, 8%)
3828   IF T2$ = "/ALL" THEN LET Q_ALL% = 1%
3830   IF T2$ = "/FULL" THEN LET Q_FULL% = 1%
3832   IF LEFT$(T2$, 8%) = "/OBJECT=" THEN LET Q_OBJ$ = RIGHT$(T1$, 9%)
3834   IF LEFT$(T2$, 8%) = "/MODULE=" THEN LET Q_MOD$ = RIGHT$(T1$, 9%)
3836   IF LEFT$(T2$, 8%) = "/OUTPUT=" THEN LET Q_OUT$ = RIGHT$(T1$, 9%)
3838   IF LEFT$(T2$, 5%) = "/LOG=" THEN LET Q_LOG$ = RIGHT$(T1$, 6%)
3839   IF T2$ = "/ACCOUNT" OR T2$ = "/ACCOUNTS" THEN LET Q_ACCT% = 1%
3840 NEXT J%
3850 ! Dispatch by VERB$
3855 IF VERB$ = "HELP" THEN GOTO 4000
3860 IF VERB$ = "SHOW" THEN GOTO 4200
3865 IF VERB$ = "PRINT" THEN GOTO 4500
3870 IF VERB$ = "SUBMIT" THEN GOTO 4600
3875 IF VERB$ = "DELETE" THEN GOTO 4700
3880 IF VERB$ = "START" THEN GOTO 4800
3885 IF VERB$ = "STOP" THEN GOTO 4900
3890 IF VERB$ = "BASIC" OR VERB$ = "COMPILE" THEN GOTO 5000
3895 IF VERB$ = "LINK" THEN GOTO 5100
3900 IF VERB$ = "RUN" THEN GOTO 5200
3905 IF VERB$ = "DIR" OR VERB$ = "DIRECTORY" THEN GOTO 5300
3910 IF VERB$ = "TYPE" THEN GOTO 5400
3915 IF VERB$ = "COPY" THEN GOTO 5500
3920 IF VERB$ = "RENAME" THEN GOTO 5600
3925 IF VERB$ = "SET" THEN GOTO 5700
3930 IF VERB$ = "WRITE" THEN GOTO 5800
3935 IF VERB$ = "WAIT" THEN GOTO 5920
3940 IF VERB$ = "ASSIGN" OR VERB$ = "DEFINE" THEN GOTO 6000
3945 IF VERB$ = "DEASSIGN" THEN GOTO 6100
3946 IF VERB$ = "CREATE" THEN GOTO 6200
3947 IF VERB$ = "MODIFY" THEN GOTO 6220
3948 IF VERB$ = "AUTHORIZE" THEN GOTO 6240
3950 IF VERB$ = "EXIT" THEN GOTO 3958
3952 IF VERB$ = "LOGOUT" THEN GOTO 3958
3954 IF VERB$ = "BYE" THEN GOTO 3958
3956 GOTO 3960
3958 LET EXIT_REQ% = 1%
3959 GOTO 3990
3960 PRINT "%DCL-W-IVVERB, unrecognized command verb '" + VERB$ + "' - check validity and spelling"
3965 GOTO 3990
3990 ! Return router based on RET_MODE%
3992 IF RET_MODE% = 0% THEN GOTO 1270
3994 IF RET_MODE% = 1% THEN GOTO 2080
3996 GOTO 9990
4000 ! ------------------------------------------------------------------------------
4010 ! HELP Command Handler
4020 ! ------------------------------------------------------------------------------
4030 IF NUM_TOK% > 0% THEN GOTO 4094
4040 PRINT "RSTS/E DIGITAL Command Language (DCL) & Job Control (PBS) Help"
4050 PRINT "Available Commands:"
4052 PRINT "  SUBMIT       - Submit a command procedure (.COM) to the batch queue"
4054 PRINT "  PRINT        - Submit a file to the print queue"
4056 PRINT "  SHOW QUEUE   - Display status of batch and print queues"
4058 PRINT "  SHOW JOBS    - Display queue entries and active processes"
4060 PRINT "  SHOW SYSTEM  - Display system and environment status"
4062 PRINT "  DELETE/ENTRY - Remove or cancel an entry from the queue"
4064 PRINT "  START/QUEUE  - Open or resume a queue"
4066 PRINT "  STOP/QUEUE   - Pause a queue"
4068 PRINT "  BASIC        - Compile a BASIC-PLUS-2 source file (.BAS)"
4070 PRINT "  LINK         - Link compiled BASIC object files (.OBJ) into executable"
4072 PRINT "  RUN          - Execute a compiled program"
4074 PRINT "  DIRECTORY    - List files in current or specified directory"
4076 PRINT "  TYPE         - Display contents of a file"
4078 PRINT "  COPY/RENAME  - Copy or rename files"
4080 PRINT "  SET DEFAULT  - Change default directory"
4082 PRINT "  WRITE        - Write output to SYS$OUTPUT"
4084 PRINT "  @file        - Execute DCL command procedure (.COM)"
4086 PRINT "  EXIT/LOGOUT  - End DCL session"
4088 PRINT "Type HELP <command> for additional information."
4090 GOTO 3990
4094 LET T1$ = TOK$(1%)
4096 FOR K% = 1% TO LEN(T1$)
4098   LET P% = ASCII(MID$(T1$, K%, 1%))
4100   IF P% >= 97% AND P% <= 122% THEN T1$ = LEFT$(T1$, K% - 1%) + CHR$(P% - 32%) + RIGHT$(T1$, K% + 1%)
4102 NEXT K%
4104 IF T1$ = "SUBMIT" THEN PRINT "SUBMIT <file.com> [/QUEUE=queue] [/NAME=job_name] [/LOG=log_file]"
4105 IF T1$ = "SUBMIT" THEN GOTO 3990
4106 IF T1$ = "PRINT" THEN PRINT "PRINT <file> [/QUEUE=queue] [/COPIES=n] [/NAME=job_name] [/DELETE]"
4107 IF T1$ = "PRINT" THEN GOTO 3990
4108 IF T1$ = "SHOW" THEN PRINT "SHOW QUEUE [name] [/ALL] [/FULL]"
4109 IF T1$ = "SHOW" THEN GOTO 3990
4110 IF T1$ = "BASIC" THEN PRINT "BASIC <file.bas> [/MODULE=name]"
4111 IF T1$ = "BASIC" THEN GOTO 3990
4112 IF T1$ = "LINK" THEN PRINT "LINK <file.obj> [/OUTPUT=target]"
4113 IF T1$ = "LINK" THEN GOTO 3990
4114 IF T1$ = "RUN" THEN PRINT "RUN <file>"
4115 IF T1$ = "RUN" THEN GOTO 3990
4116 PRINT "No specific help topic available for "; T1$
4118 GOTO 3990
4200 ! ------------------------------------------------------------------------------
4210 ! SHOW Command Handler
4220 ! ------------------------------------------------------------------------------
4230 IF NUM_TOK% > 0% THEN GOTO 4240
4232 PRINT "%DCL-E-PARAM, missing SHOW parameter"
4235 GOTO 3990
4240 LET T1$ = TOK$(1%)
4250 FOR K% = 1% TO LEN(T1$)
4260   LET P% = ASCII(MID$(T1$, K%, 1%))
4270   IF P% >= 97% AND P% <= 122% THEN T1$ = LEFT$(T1$, K% - 1%) + CHR$(P% - 32%) + RIGHT$(T1$, K% + 1%)
4280 NEXT K%
4300 IF T1$ <> "SYSTEM" THEN GOTO 4320
4305 PRINT "DEC RSTS/E V10.1-L Environment"
4310 PRINT "Host Platform: Linux Bytecode VM"
4312 PRINT "System Time:   "; DATE$(0%); " "; TIME$(0%)
4314 PRINT "Compiler:      DEC BASIC-PLUS-2 Native Toolchain / Bytecode VM"
4316 PRINT "Job Subsystem: Print/Batch Services (PBS) Active"
4318 PRINT "Default Dir:   "; DEF_DIR$
4319 GOTO 3990
4320 IF T1$ = "TIME" OR T1$ = "DATE" THEN PRINT DATE$(0%); " "; TIME$(0%)
4322 IF T1$ = "TIME" OR T1$ = "DATE" THEN GOTO 3990
4330 IF T1$ = "DEFAULT" THEN PRINT DEF_DIR$
4332 IF T1$ = "DEFAULT" THEN GOTO 3990
4340 IF T1$ <> "SYMBOL" AND T1$ <> "SYMBOLS" THEN GOTO 4360
4345 IF NUM_TOK% > 1% THEN LET S_NAME$ = TOK$(2%)
4347 IF NUM_TOK% > 1% THEN GOTO 8500
4350 PRINT "DCL Symbols:"
4352 FOR I% = 1% TO NUM_SYM%
4354   PRINT "  "; SYM_N$(I%); " = " + CHR$(34%) + SYM_V$(I%) + CHR$(34%)
4356 NEXT I%
4358 GOTO 3990
4360 IF T1$ <> "LOGICAL" AND T1$ <> "LOGICALS" AND T1$ <> "TRANSLATION" THEN GOTO 4380
4370 PRINT "Logical Names:"
4372 FOR I% = 1% TO NUM_LOG%
4374   PRINT "  " + CHR$(34%) + LOG_N$(I%) + CHR$(34%) + " = " + CHR$(34%) + LOG_V$(I%) + CHR$(34%)
4376 NEXT I%
4378 GOTO 3990
4380 IF T1$ <> "QUEUE" AND T1$ <> "QUEUES" THEN GOTO 4400
4390 LET T2$ = ""
4392 IF NUM_TOK% > 1% THEN LET T2$ = TOK$(2%)
4394 IF Q_ALL% = 1% OR Q_FULL% = 1% THEN LET T2$ = T2$ + " --all"
4396 LET RC% = SYS("python3 dcl/job_controller.py show-queue " + T2$)
4398 GOTO 3990
4400 IF T1$ <> "JOB" AND T1$ <> "JOBS" THEN GOTO 4420
4410 LET T2$ = ""
4412 IF Q_ALL% = 1% THEN LET T2$ = "--all"
4414 LET RC% = SYS("python3 dcl/job_controller.py show-jobs " + T2$)
4416 GOTO 3990
4420 IF T1$ <> "ENTRY" AND T1$ <> "ENTRIES" THEN GOTO 4438
4430 LET T2$ = ""
4432 IF NUM_TOK% > 1% THEN LET T2$ = TOK$(2%)
4434 LET RC% = SYS("python3 dcl/job_controller.py show-entry " + T2$)
4436 GOTO 3990
4438 IF T1$ = "ACCOUNT" OR T1$ = "ACCOUNTS" THEN LET RC% = SYS("python3 dcl/job_controller.py dcl-account SHOW " + CHR$(34%) + RAW_REST$ + CHR$(34%))
4439 IF T1$ = "ACCOUNT" OR T1$ = "ACCOUNTS" THEN GOTO 3990
4440 PRINT "%DCL-E-IVKEYW, unrecognized SHOW keyword '"; T1$; "'"
4450 GOTO 3990
4500 ! ------------------------------------------------------------------------------
4510 ! PRINT Command Handler
4520 ! ------------------------------------------------------------------------------
4525 IF NUM_TOK% > 0% THEN GOTO 4530
4527 PRINT "%DCL-E-NOFILE, missing filename to print"
4528 GOTO 3990
4530 LET T1$ = TOK$(1%)
4532 LET T3$ = T1$
4534 FOR K% = 1% TO LEN(T3$)
4536   LET P% = ASCII(MID$(T3$, K%, 1%))
4538   IF P% >= 65% AND P% <= 90% THEN T3$ = LEFT$(T3$, K% - 1%) + CHR$(P% + 32%) + RIGHT$(T3$, K% + 1%)
4540 NEXT K%
4542 IF SYS("test -f " + T1$) = 0% THEN GOTO 4555
4544 IF SYS("test -f " + T3$) = 0% THEN LET T1$ = T3$
4546 IF SYS("test -f " + T3$) = 0% THEN GOTO 4555
4548 IF PROC_DIR$ = "" THEN GOTO 4555
4550 IF SYS("test -f " + PROC_DIR$ + T1$) = 0% THEN LET T1$ = PROC_DIR$ + T1$
4552 IF SYS("test -f " + PROC_DIR$ + T1$) = 0% THEN GOTO 4555
4553 IF SYS("test -f " + PROC_DIR$ + T3$) = 0% THEN LET T1$ = PROC_DIR$ + T3$
4554 IF SYS("test -f " + PROC_DIR$ + T3$) = 0% THEN GOTO 4555
4555 LET T2$ = CHR$(34%) + T1$ + CHR$(34%)
4560 IF Q_QUEUE$ <> "" THEN LET T2$ = T2$ + " --queue " + Q_QUEUE$
4565 IF Q_NAME$ <> "" THEN LET T2$ = T2$ + " --name " + Q_NAME$
4570 IF Q_COPIES$ <> "1" THEN LET T2$ = T2$ + " --copies " + Q_COPIES$
4575 IF Q_DELETE% = 1% THEN LET T2$ = T2$ + " --delete"
4580 LET RC% = SYS("python3 dcl/job_controller.py submit-print " + T2$)
4585 GOTO 3990
4600 ! ------------------------------------------------------------------------------
4610 ! SUBMIT Command Handler
4620 ! ------------------------------------------------------------------------------
4625 IF NUM_TOK% > 0% THEN GOTO 4630
4627 PRINT "%DCL-E-NOFILE, missing command procedure filename"
4628 GOTO 3990
4630 LET T1$ = TOK$(1%)
4632 LET T3$ = T1$
4634 FOR K% = 1% TO LEN(T3$)
4636   LET P% = ASCII(MID$(T3$, K%, 1%))
4638   IF P% >= 65% AND P% <= 90% THEN T3$ = LEFT$(T3$, K% - 1%) + CHR$(P% + 32%) + RIGHT$(T3$, K% + 1%)
4640 NEXT K%
4642 IF SYS("test -f " + T1$) = 0% THEN GOTO 4655
4644 IF SYS("test -f " + T3$) = 0% THEN LET T1$ = T3$
4646 IF SYS("test -f " + T3$) = 0% THEN GOTO 4655
4648 IF PROC_DIR$ = "" THEN GOTO 4655
4650 IF SYS("test -f " + PROC_DIR$ + T1$) = 0% THEN LET T1$ = PROC_DIR$ + T1$
4652 IF SYS("test -f " + PROC_DIR$ + T1$) = 0% THEN GOTO 4655
4653 IF SYS("test -f " + PROC_DIR$ + T3$) = 0% THEN LET T1$ = PROC_DIR$ + T3$
4654 IF SYS("test -f " + PROC_DIR$ + T3$) = 0% THEN GOTO 4655
4655 LET T2$ = CHR$(34%) + T1$ + CHR$(34%)
4660 IF Q_QUEUE$ <> "" THEN LET T2$ = T2$ + " --queue " + Q_QUEUE$
4665 IF Q_NAME$ <> "" THEN LET T2$ = T2$ + " --name " + Q_NAME$
4670 IF Q_LOG$ <> "" THEN LET T2$ = T2$ + " --log " + Q_LOG$
4680 LET RC% = SYS("python3 dcl/job_controller.py submit-batch " + T2$)
4685 GOTO 3990
4700 ! ------------------------------------------------------------------------------
4710 ! DELETE Command Handler
4720 ! ------------------------------------------------------------------------------
4725 IF Q_ENTRY$ = "" THEN GOTO 4730
4727 LET RC% = SYS("python3 dcl/job_controller.py delete-entry " + Q_ENTRY$)
4729 GOTO 3990
4730 IF Q_ACCT% = 1% THEN LET RC% = SYS("python3 dcl/job_controller.py dcl-account DELETE " + CHR$(34%) + RAW_REST$ + CHR$(34%))
4731 IF Q_ACCT% = 1% THEN GOTO 3990
4732 IF NUM_TOK% > 0% THEN GOTO 4735
4733 PRINT "%DCL-E-PARAM, missing file or qualifier for DELETE"
4734 GOTO 3990
4735 LET T1$ = TOK$(1%)
4736 IF T1$ = "ACCOUNT" OR T1$ = "account" THEN LET RC% = SYS("python3 dcl/job_controller.py dcl-account DELETE " + CHR$(34%) + RAW_REST$ + CHR$(34%))
4737 IF T1$ = "ACCOUNT" OR T1$ = "account" THEN GOTO 3990
4740 LET RC% = SYS("rm -f " + T1$)
4745 PRINT "%DCL-I-DELETED, file "; T1$; " deleted"
4750 GOTO 3990
4800 ! ------------------------------------------------------------------------------
4810 ! START Command Handler
4820 ! ------------------------------------------------------------------------------
4825 IF NUM_TOK% > 0% THEN GOTO 4828
4826 PRINT "%DCL-E-PARAM, missing queue name"
4827 GOTO 3990
4828 LET RC% = SYS("python3 dcl/job_controller.py start-queue " + TOK$(1%))
4829 GOTO 3990
4900 ! ------------------------------------------------------------------------------
4910 ! STOP Command Handler
4920 ! ------------------------------------------------------------------------------
4925 IF NUM_TOK% > 0% THEN GOTO 4928
4926 PRINT "%DCL-E-PARAM, missing queue name"
4927 GOTO 3990
4928 LET RC% = SYS("python3 dcl/job_controller.py stop-queue " + TOK$(1%))
4929 GOTO 3990
5000 ! ------------------------------------------------------------------------------
5010 ! BASIC / COMPILE Command Handler
5020 ! ------------------------------------------------------------------------------
5025 IF NUM_TOK% > 0% THEN GOTO 5030
5026 PRINT "%DCL-E-NOFILE, missing BASIC source filename"
5027 GOTO 3990
5030 LET T1$ = TOK$(1%)
5032 LET T2$ = T1$
5034 IF Q_OBJ$ <> "" THEN GOTO 5040
5035 LET L% = LEN(T1$)
5036 IF L% > 4% THEN IF RIGHT$(T1$, L% - 3%) = ".bas" THEN LET Q_OBJ$ = LEFT$(T1$, L% - 4%) + ".OBJ"
5037 IF L% > 4% THEN IF RIGHT$(T1$, L% - 3%) = ".BAS" THEN LET Q_OBJ$ = LEFT$(T1$, L% - 4%) + ".OBJ"
5038 IF Q_OBJ$ = "" THEN LET Q_OBJ$ = T1$ + ".OBJ"
5040 IF Q_OBJ$ <> "" THEN LET T2$ = T2$ + " -o " + Q_OBJ$
5045 IF Q_MOD$ <> "" THEN LET T2$ = T2$ + " --module " + Q_MOD$
5050 LET RC% = SYS("python3 compiler/basicc.py " + T2$)
5055 GOTO 3990
5100 ! ------------------------------------------------------------------------------
5110 ! LINK Command Handler
5120 ! ------------------------------------------------------------------------------
5125 IF NUM_TOK% > 0% THEN GOTO 5130
5126 PRINT "%DCL-E-NOFILE, missing object filename to link"
5127 GOTO 3990
5130 LET T1$ = TOK$(1%)
5132 LET T3$ = T1$
5135 LET L% = LEN(T1$)
5136 IF L% >= 4% THEN IF RIGHT$(T3$, L% - 3%) = ".OBJ" OR RIGHT$(T3$, L% - 3%) = ".obj" THEN LET T3$ = LEFT$(T3$, L% - 4%)
5138 IF SYS("test -f " + T1$ + " && test ! -x " + T1$) = 0% THEN GOTO 5146
5139 IF SYS("test -f " + T3$ + ".OBJ") = 0% THEN LET T1$ = T3$ + ".OBJ"
5140 IF SYS("test -f " + T3$ + ".OBJ") = 0% THEN GOTO 5146
5141 IF SYS("test -f " + T3$ + ".obj") = 0% THEN LET T1$ = T3$ + ".obj"
5146 IF Q_OUT$ = "" THEN LET Q_OUT$ = T3$
5150 LET T2$ = "-o " + Q_OUT$ + " " + T1$
5160 FOR I% = 2% TO NUM_TOK%
5165   LET T2$ = T2$ + " " + TOK$(I%)
5170 NEXT I%
5175 LET RC% = SYS("python3 compiler/basiclink.py " + T2$)
5180 GOTO 3990
5200 ! ------------------------------------------------------------------------------
5210 ! RUN Command Handler
5220 ! ------------------------------------------------------------------------------
5225 IF NUM_TOK% > 0% THEN GOTO 5230
5226 PRINT "%DCL-E-NOFILE, missing program to run"
5227 GOTO 3990
5230 LET T1$ = TOK$(1%)
5232 LET T3$ = T1$
5234 FOR K% = 1% TO LEN(T3$)
5236   LET P% = ASCII(MID$(T3$, K%, 1%))
5238   IF P% >= 65% AND P% <= 90% THEN T3$ = LEFT$(T3$, K% - 1%) + CHR$(P% + 32%) + RIGHT$(T3$, K% + 1%)
5240 NEXT K%
5242 LET T2$ = T1$
5244 IF SYS("test -e " + T1$) = 0% THEN LET T2$ = T1$
5245 IF SYS("test -e " + T1$) = 0% THEN GOTO 5270
5246 IF SYS("test -e " + T3$) = 0% THEN LET T2$ = T3$
5247 IF SYS("test -e " + T3$) = 0% THEN GOTO 5270
5248 IF PROC_DIR$ = "" THEN GOTO 5270
5250 IF SYS("test -e " + PROC_DIR$ + T1$) = 0% THEN LET T2$ = PROC_DIR$ + T1$
5252 IF SYS("test -e " + PROC_DIR$ + T1$) = 0% THEN GOTO 5270
5254 IF SYS("test -e " + PROC_DIR$ + T3$) = 0% THEN LET T2$ = PROC_DIR$ + T3$
5256 IF SYS("test -e " + PROC_DIR$ + T3$) = 0% THEN GOTO 5270
5270 IF LEFT$(T2$, 1%) <> "/" AND LEFT$(T2$, 2%) <> "./" THEN LET T2$ = "./" + T2$
5275 LET RC% = SYS(T2$)
5280 GOTO 3990
5300 ! ------------------------------------------------------------------------------
5310 ! DIRECTORY / DIR Command Handler
5320 ! ------------------------------------------------------------------------------
5325 LET T1$ = "*"
5330 IF NUM_TOK% > 0% THEN LET T1$ = TOK$(1%)
5335 LET RC% = SYS("python3 dcl/job_controller.py dir " + CHR$(34%) + T1$ + CHR$(34%))
5340 GOTO 3990
5400 ! ------------------------------------------------------------------------------
5410 ! TYPE Command Handler
5420 ! ------------------------------------------------------------------------------
5425 IF NUM_TOK% > 0% THEN GOTO 5430
5426 PRINT "%DCL-E-NOFILE, missing file to display"
5427 GOTO 3990
5430 LET T1$ = TOK$(1%)
5432 LET T3$ = T1$
5434 FOR K% = 1% TO LEN(T3$)
5436   LET P% = ASCII(MID$(T3$, K%, 1%))
5438   IF P% >= 65% AND P% <= 90% THEN T3$ = LEFT$(T3$, K% - 1%) + CHR$(P% + 32%) + RIGHT$(T3$, K% + 1%)
5440 NEXT K%
5442 IF SYS("test -f " + T1$) = 0% THEN GOTO 5460
5444 IF SYS("test -f " + T3$) = 0% THEN LET T1$ = T3$
5446 IF SYS("test -f " + T3$) = 0% THEN GOTO 5460
5448 IF PROC_DIR$ = "" THEN GOTO 5460
5450 IF SYS("test -f " + PROC_DIR$ + T1$) = 0% THEN LET T1$ = PROC_DIR$ + T1$
5452 IF SYS("test -f " + PROC_DIR$ + T1$) = 0% THEN GOTO 5460
5453 IF SYS("test -f " + PROC_DIR$ + T3$) = 0% THEN LET T1$ = PROC_DIR$ + T3$
5454 IF SYS("test -f " + PROC_DIR$ + T3$) = 0% THEN GOTO 5460
5460 ON ERROR GOTO 5480
5462 OPEN T1$ FOR INPUT AS FILE #2%
5465 LINE INPUT #2%, TXT$
5470 PRINT TXT$
5475 GOTO 5465
5480 CLOSE #2%
5485 GOTO 3990
5500 ! ------------------------------------------------------------------------------
5510 ! COPY Command Handler
5520 ! ------------------------------------------------------------------------------
5525 IF NUM_TOK% >= 2% THEN GOTO 5530
5526 PRINT "%DCL-E-PARAM, missing source or destination"
5527 GOTO 3990
5530 LET RC% = SYS("cp " + TOK$(1%) + " " + TOK$(2%))
5535 PRINT "%DCL-I-COPIED, copied "; TOK$(1%); " to "; TOK$(2%)
5540 GOTO 3990
5600 ! ------------------------------------------------------------------------------
5610 ! RENAME Command Handler
5620 ! ------------------------------------------------------------------------------
5625 IF NUM_TOK% >= 2% THEN GOTO 5630
5626 PRINT "%DCL-E-PARAM, missing source or destination"
5627 GOTO 3990
5630 LET RC% = SYS("mv " + TOK$(1%) + " " + TOK$(2%))
5635 PRINT "%DCL-I-RENAMED, renamed "; TOK$(1%); " to "; TOK$(2%)
5640 GOTO 3990
5700 ! ------------------------------------------------------------------------------
5710 ! SET Command Handler
5720 ! ------------------------------------------------------------------------------
5725 IF NUM_TOK% > 0% THEN GOTO 5730
5726 PRINT "%DCL-E-PARAM, missing SET parameter"
5727 GOTO 3990
5730 LET T1$ = TOK$(1%)
5735 FOR K% = 1% TO LEN(T1$)
5740   LET P% = ASCII(MID$(T1$, K%, 1%))
5745   IF P% >= 97% AND P% <= 122% THEN T1$ = LEFT$(T1$, K% - 1%) + CHR$(P% - 32%) + RIGHT$(T1$, K% + 1%)
5750 NEXT K%
5755 IF T1$ <> "DEFAULT" AND T1$ <> "DEF" THEN GOTO 5775
5760 IF NUM_TOK% > 1% THEN GOTO 5765
5762 PRINT "%DCL-E-PARAM, missing directory path"
5764 GOTO 3990
5765 LET DEF_DIR$ = TOK$(2%)
5770 LET RC% = SYS("cd " + DEF_DIR$)
5772 GOTO 3990
5775 IF T1$ = "VERIFY" THEN LET VERIFY% = 1%
5777 IF T1$ = "VERIFY" THEN GOTO 3990
5780 IF T1$ = "NOVERIFY" THEN LET VERIFY% = 0%
5782 IF T1$ = "NOVERIFY" THEN GOTO 3990
5783 IF T1$ = "ACCOUNT" THEN LET RC% = SYS("python3 dcl/job_controller.py dcl-account SET_ACCOUNT " + CHR$(34%) + RAW_REST$ + CHR$(34%))
5784 IF T1$ = "ACCOUNT" THEN GOTO 3990
5785 IF T1$ = "PASSWORD" THEN LET RC% = SYS("python3 dcl/job_controller.py dcl-account SET_PASSWORD " + CHR$(34%) + RAW_REST$ + CHR$(34%))
5786 IF T1$ = "PASSWORD" THEN GOTO 3990
5788 PRINT "%DCL-W-IVKEYW, unrecognized SET option '"; T1$; "'"
5790 GOTO 3990
5800 ! ------------------------------------------------------------------------------
5810 ! WRITE Command Handler (WRITE SYS$OUTPUT "text")
5820 ! ------------------------------------------------------------------------------
5825 LET T1$ = RAW_REST$
5830 FOR J% = 1% TO 20%
5832   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
5834   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
5836 NEXT J%
5840 IF LEFT$(T1$, 10%) = "SYS$OUTPUT" OR LEFT$(T1$, 10%) = "sys$output" THEN LET T1$ = RIGHT$(T1$, 11%)
5845 FOR J% = 1% TO 20%
5847   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
5849   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
5851 NEXT J%
5855 IF LEFT$(T1$, 3%) = "TT:" OR LEFT$(T1$, 3%) = "tt:" THEN LET T1$ = RIGHT$(T1$, 4%)
5860 FOR J% = 1% TO 20%
5862   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
5864   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
5866 NEXT J%
5870 IF LEFT$(T1$, 1%) = CHR$(34%) AND RIGHT$(T1$, LEN(T1$)) = CHR$(34%) THEN LET T1$ = MID$(T1$, 2%, LEN(T1$) - 2%)
5880 ! Substitute symbols enclosed in single quotes 'SYM'
5882 LET P% = INSTR(T1$, "'")
5884 IF P% <= 0% THEN GOTO 5910
5886 LET L% = INSTR(RIGHT$(T1$, P% + 1%), "'")
5888 IF L% <= 0% THEN GOTO 5910
5890 LET L% = P% + L%
5892 LET S_NAME$ = MID$(T1$, P% + 1%, L% - P% - 1%)
5894 LET RET_VAL$ = ""
5895 FOR I% = 1% TO NUM_SYM%
5897   IF SYM_N$(I%) = S_NAME$ THEN LET RET_VAL$ = SYM_V$(I%)
5899 NEXT I%
5902 LET T1$ = LEFT$(T1$, P% - 1%) + RET_VAL$ + RIGHT$(T1$, L% + 1%)
5904 GOTO 5882
5910 PRINT T1$
5915 GOTO 3990
5920 ! ------------------------------------------------------------------------------
5925 ! WAIT Command Handler
5930 ! ------------------------------------------------------------------------------
5935 LET T1$ = "1"
5940 IF NUM_TOK% > 0% THEN LET T1$ = TOK$(1%)
5945 LET RC% = SYS("sleep " + T1$)
5950 GOTO 3990
6000 ! ------------------------------------------------------------------------------
6010 ! ASSIGN / DEFINE Command Handler
6020 ! ------------------------------------------------------------------------------
6025 IF NUM_TOK% >= 2% THEN GOTO 6030
6026 PRINT "%DCL-E-PARAM, missing value or logical name"
6027 GOTO 3990
6030 LET NUM_LOG% = NUM_LOG% + 1%
6035 LET LOG_N$(NUM_LOG%) = TOK$(2%)
6040 LET LOG_V$(NUM_LOG%) = TOK$(1%)
6045 GOTO 3990
6100 ! ------------------------------------------------------------------------------
6110 ! DEASSIGN Command Handler
6120 ! ------------------------------------------------------------------------------
6125 IF NUM_TOK% > 0% THEN GOTO 6130
6126 PRINT "%DCL-E-PARAM, missing logical name"
6127 GOTO 3990
6130 LET T1$ = TOK$(1%)
6135 FOR K% = 1% TO LEN(T1$)
6140   LET P% = ASCII(MID$(T1$, K%, 1%))
6145   IF P% >= 97% AND P% <= 122% THEN T1$ = LEFT$(T1$, K% - 1%) + CHR$(P% - 32%) + RIGHT$(T1$, K% + 1%)
6150 NEXT K%
6155 FOR I% = 1% TO NUM_LOG%
6160   IF LOG_N$(I%) = T1$ THEN LET LOG_N$(I%) = ""
6162   IF LOG_N$(I%) = T1$ THEN LET LOG_V$(I%) = ""
6165 NEXT I%
6170 GOTO 3990
6200 ! ------------------------------------------------------------------------------
6205 ! CREATE/ACCOUNT, MODIFY/ACCOUNT, AUTHORIZE Handlers
6210 ! ------------------------------------------------------------------------------
6212 LET RC% = SYS("python3 dcl/job_controller.py dcl-account CREATE " + CHR$(34%) + RAW_REST$ + CHR$(34%))
6215 GOTO 3990
6220 LET RC% = SYS("python3 dcl/job_controller.py dcl-account MODIFY " + CHR$(34%) + RAW_REST$ + CHR$(34%))
6225 GOTO 3990
6240 LET RC% = SYS("python3 dcl/job_controller.py dcl-account SHOW " + CHR$(34%) + RAW_REST$ + CHR$(34%))
6245 GOTO 3990
7000 ! ------------------------------------------------------------------------------
7010 ! IF Condition Evaluator in Procedure: IF <LHS> = <RHS> THEN <stmt>
7020 ! ------------------------------------------------------------------------------
7030 LET COND_TRUE% = 0%
7040 LET T2$ = RIGHT$(T1$, 4%)
7050 FOR J% = 1% TO 20%
7060   IF LEFT$(T2$, 1%) = " " THEN LET T2$ = RIGHT$(T2$, 2%)
7070   IF RIGHT$(T2$, LEN(T2$)) = " " THEN LET T2$ = LEFT$(T2$, LEN(T2$) - 1%)
7080 NEXT J%
7100 ! Find THEN keyword
7110 LET P% = INSTR(T2$, " THEN ")
7120 IF P% = 0% THEN LET P% = INSTR(T2$, " then ")
7130 IF P% = 0% THEN GOTO 2080
7150 LET COND_STR$ = LEFT$(T2$, P% - 1%)
7160 LET THEN_STMT$ = RIGHT$(T2$, P% + 6%)
7170 FOR J% = 1% TO 20%
7180   IF LEFT$(COND_STR$, 1%) = " " THEN LET COND_STR$ = RIGHT$(COND_STR$, 2%)
7190   IF RIGHT$(COND_STR$, LEN(COND_STR$)) = " " THEN LET COND_STR$ = LEFT$(COND_STR$, LEN(COND_STR$) - 1%)
7200   IF LEFT$(THEN_STMT$, 1%) = " " THEN LET THEN_STMT$ = RIGHT$(THEN_STMT$, 2%)
7210   IF RIGHT$(THEN_STMT$, LEN(THEN_STMT$)) = " " THEN LET THEN_STMT$ = LEFT$(THEN_STMT$, LEN(THEN_STMT$) - 1%)
7220 NEXT J%
7240 ! Parse operator in COND_STR$ (e.g. COUNT = 1)
7250 LET P% = INSTR(COND_STR$, "=")
7260 IF P% <= 1% THEN GOTO 7445
7270 LET T1$ = LEFT$(COND_STR$, P% - 1%)
7280 FOR J% = 1% TO 20%
7290   IF LEFT$(T1$, 1%) = " " THEN LET T1$ = RIGHT$(T1$, 2%)
7300   IF RIGHT$(T1$, LEN(T1$)) = " " THEN LET T1$ = LEFT$(T1$, LEN(T1$) - 1%)
7310 NEXT J%
7320 FOR I% = 1% TO NUM_SYM%
7330   IF SYM_N$(I%) = T1$ THEN LET T1$ = SYM_V$(I%)
7340 NEXT I%
7350 LET T2$ = RIGHT$(COND_STR$, P% + 1%)
7360 FOR J% = 1% TO 20%
7370   IF LEFT$(T2$, 1%) = " " THEN LET T2$ = RIGHT$(T2$, 2%)
7380   IF RIGHT$(T2$, LEN(T2$)) = " " THEN LET T2$ = LEFT$(T2$, LEN(T2$) - 1%)
7390 NEXT J%
7400 FOR I% = 1% TO NUM_SYM%
7410   IF SYM_N$(I%) = T2$ THEN LET T2$ = SYM_V$(I%)
7420 NEXT I%
7430 IF T1$ = T2$ THEN LET COND_TRUE% = 1%
7445 IF COND_TRUE% = 0% THEN GOTO 2080
7460 ! Condition was true: evaluate THEN_STMT$
7470 IF LEFT$(THEN_STMT$, 5%) = "GOTO " THEN GOTO 7474
7472 IF LEFT$(THEN_STMT$, 5%) = "goto " THEN GOTO 7474
7473 GOTO 7480
7474 LET T2$ = RIGHT$(THEN_STMT$, 6%)
7476 GOTO 7500
7480 IF THEN_STMT$ = "EXIT" THEN GOTO 2900
7482 IF THEN_STMT$ = "STOP" THEN GOTO 2900
7484 IF THEN_STMT$ = "exit" THEN GOTO 2900
7486 IF THEN_STMT$ = "stop" THEN GOTO 2900
7490 LET CMD_LINE$ = THEN_STMT$
7495 LET RET_MODE% = 1%
7498 GOTO 3000
7500 ! ------------------------------------------------------------------------------
7510 ! Jump to Label T2$ in Procedure
7520 ! ------------------------------------------------------------------------------
7530 FOR J% = 1% TO 20%
7540   IF LEFT$(T2$, 1%) = " " THEN LET T2$ = RIGHT$(T2$, 2%)
7550   IF RIGHT$(T2$, LEN(T2$)) = " " THEN LET T2$ = LEFT$(T2$, LEN(T2$) - 1%)
7560 NEXT J%
7570 FOR I% = 1% TO NUM_LBL%
7580   IF LBL_N$(I%) = T2$ THEN GOTO 7584
7582   GOTO 7590
7584   LET PC% = LBL_PC%(I%)
7586   GOTO 2080
7590 NEXT I%
7600 PRINT "%DCL-W-UNDLABEL, label "; T2$; " not found"
7610 LET STATUS_CODE% = 2%
7620 LET EXIT_REQ% = 1%
7630 GOTO 2900
8000 ! ------------------------------------------------------------------------------
8010 ! Set Symbol S_NAME$ = S_VAL$
8020 ! ------------------------------------------------------------------------------
8030 FOR I% = 1% TO NUM_SYM%
8040   IF SYM_N$(I%) = S_NAME$ THEN GOTO 8044
8042   GOTO 8050
8044   LET SYM_V$(I%) = S_VAL$
8046   GOTO 3990
8050 NEXT I%
8060 LET NUM_SYM% = NUM_SYM% + 1%
8070 LET SYM_N$(NUM_SYM%) = S_NAME$
8080 LET SYM_V$(NUM_SYM%) = S_VAL$
8090 GOTO 3990
8500 ! ------------------------------------------------------------------------------
8510 ! SHOW SYMBOL S_NAME$
8520 ! ------------------------------------------------------------------------------
8530 FOR I% = 1% TO NUM_SYM%
8540   IF SYM_N$(I%) = S_NAME$ THEN GOTO 8544
8542   GOTO 8550
8544   PRINT "  "; S_NAME$; " = " + CHR$(34%) + SYM_V$(I%) + CHR$(34%)
8546   GOTO 3990
8550 NEXT I%
8560 PRINT "%DCL-W-UNDSYM, undefined symbol '" + S_NAME$ + "'"
8570 GOTO 3990
9900 ! ------------------------------------------------------------------------------
9910 ! Global Error Handler
9920 ! ------------------------------------------------------------------------------
9925 RESUME 9990
9990 ! Exit program
9995 PRINT "%DCL-I-LOGOUT, session terminated"
9999 END
