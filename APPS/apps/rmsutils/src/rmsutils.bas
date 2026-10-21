10 ! ================================================================
20 ! RMSUTILS - DEC RMS-11 UTILITY SUITE MASTER LAUNCHER
30 ! AUTHENTIC DIGITAL EQUIPMENT CORPORATION RMS-11 SUITE
40 ! REIMPLEMENTED IN BASIC-PLUS-2 FOR DEC-APPS
50 ! ================================================================
60 EXE_PRE$ = ""
65 IF SYS("test -f apps/rmsutils/bin/rmsdes") = 0% THEN EXE_PRE$ = "apps/rmsutils/bin/"
70 IF SYS("test -f bin/rmsdes") = 0% THEN EXE_PRE$ = "bin/"
80 IF SYS("test -f ./rmsdes") = 0% THEN EXE_PRE$ = "./"
90 CMD$ = COMMAND$
95 IF CMD$ <> "" THEN GOTO 300
100 MENU_LOOP:
110 PRINT ""
120 PRINT "================================================================"
130 PRINT "    DEC RMS-11 Utilities Suite V2.0 (BASIC-PLUS-2)"
140 PRINT "================================================================"
150 PRINT "  1. RMSDES - File Design Utility (Create .DES specification)"
160 PRINT "  2. RMSDEF - File Definition Utility (Create empty RMS files)"
170 PRINT "  3. RMSIFL - Indexed File Load Utility (Fast sequential load)"
180 PRINT "  4. RMSCNV - File Convert Utility (Sequential <-> Indexed)"
190 PRINT "  5. RMSBCK - File Backup Utility (Create .BCK container)"
200 PRINT "  6. RMSRST - File Restore Utility (Rebuild from .BCK)"
210 PRINT "  7. RMSDSP - File Display Utility (Inspect RMS attributes)"
220 PRINT "  0. Exit"
230 PRINT "================================================================"
240 PRINT "Select utility [0-7]: ";
250 INPUT SEL$
260 IF SEL$ = "0" OR SEL$ = "exit" OR SEL$ = "EXIT" THEN GOTO 999
270 IF SEL$ = "1" THEN GOTO 510
275 IF SEL$ = "2" THEN GOTO 520
280 IF SEL$ = "3" THEN GOTO 530
285 IF SEL$ = "4" THEN GOTO 540
290 IF SEL$ = "5" THEN GOTO 550
295 IF SEL$ = "6" THEN GOTO 560
298 IF SEL$ = "7" THEN GOTO 570
299 PRINT "Invalid selection. Please choose 0 to 7."
302 GOTO MENU_LOOP
300 ! Dispatch command-line invocation
305 SP% = INSTR(1%, CMD$, " ")
310 IF SP% > 0% THEN GOTO 320
315 SUBCMD$ = CMD$
316 ARGS$ = ""
318 GOTO 330
320 SUBCMD$ = LEFT$(CMD$, SP% - 1%)
325 ARGS$ = MID$(CMD$, SP% + 1%, LEN(CMD$) - SP%)
330 IF SUBCMD$ = "rmsdes" OR SUBCMD$ = "RMSDES" THEN RC% = SYS(EXE_PRE$ + "rmsdes " + ARGS$)
332 IF SUBCMD$ = "rmsdes" OR SUBCMD$ = "RMSDES" THEN GOTO 999
335 IF SUBCMD$ = "rmsdef" OR SUBCMD$ = "RMSDEF" THEN RC% = SYS(EXE_PRE$ + "rmsdef " + ARGS$)
337 IF SUBCMD$ = "rmsdef" OR SUBCMD$ = "RMSDEF" THEN GOTO 999
340 IF SUBCMD$ = "rmsifl" OR SUBCMD$ = "RMSIFL" THEN RC% = SYS(EXE_PRE$ + "rmsifl " + ARGS$)
342 IF SUBCMD$ = "rmsifl" OR SUBCMD$ = "RMSIFL" THEN GOTO 999
345 IF SUBCMD$ = "rmscnv" OR SUBCMD$ = "RMSCNV" THEN RC% = SYS(EXE_PRE$ + "rmscnv " + ARGS$)
347 IF SUBCMD$ = "rmscnv" OR SUBCMD$ = "RMSCNV" THEN GOTO 999
350 IF SUBCMD$ = "rmsbck" OR SUBCMD$ = "RMSBCK" THEN RC% = SYS(EXE_PRE$ + "rmsbck " + ARGS$)
352 IF SUBCMD$ = "rmsbck" OR SUBCMD$ = "RMSBCK" THEN GOTO 999
355 IF SUBCMD$ = "rmsrst" OR SUBCMD$ = "RMSRST" THEN RC% = SYS(EXE_PRE$ + "rmsrst " + ARGS$)
357 IF SUBCMD$ = "rmsrst" OR SUBCMD$ = "RMSRST" THEN GOTO 999
360 IF SUBCMD$ = "rmsdsp" OR SUBCMD$ = "RMSDSP" THEN RC% = SYS(EXE_PRE$ + "rmsdsp " + ARGS$)
362 IF SUBCMD$ = "rmsdsp" OR SUBCMD$ = "RMSDSP" THEN GOTO 999
370 PRINT "RMSUTILS: Unknown utility '"; SUBCMD$; "'. Available: rmsdes, rmsdef, rmsifl, rmscnv, rmsbck, rmsrst, rmsdsp."
375 GOTO 999
510 RC% = SYS(EXE_PRE$ + "rmsdes")
515 GOTO MENU_LOOP
520 RC% = SYS(EXE_PRE$ + "rmsdef")
525 GOTO MENU_LOOP
530 RC% = SYS(EXE_PRE$ + "rmsifl")
535 GOTO MENU_LOOP
540 RC% = SYS(EXE_PRE$ + "rmscnv")
545 GOTO MENU_LOOP
550 RC% = SYS(EXE_PRE$ + "rmsbck")
555 GOTO MENU_LOOP
560 RC% = SYS(EXE_PRE$ + "rmsrst")
565 GOTO MENU_LOOP
570 RC% = SYS(EXE_PRE$ + "rmsdsp")
575 GOTO MENU_LOOP
999 END
