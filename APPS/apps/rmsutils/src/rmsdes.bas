10 ! ================================================================
20 ! RMSDES - DEC RMS-11 FILE DESIGN UTILITY
30 ! AUTHENTIC DIGITAL EQUIPMENT CORPORATION RMS-11 DESIGN FACILITY
40 ! REIMPLEMENTED IN BASIC-PLUS-2 FOR DEC-APPS
50 ! ================================================================
60 DES_FILE$ = ""
70 ORG$ = "INDEXED"
80 REC_SIZE% = 255%
90 KEY_POS% = 1%
100 KEY_LEN% = 16%
110 KEY_TYPE$ = "STRING"
120 BUCKET_SZ% = 1%
130 DUP_KEYS$ = "NO"
140 CMD$ = COMMAND$
150 IF CMD$ <> "" THEN GOSUB 300
160 IF DES_FILE$ = "" THEN GOSUB 400
170 IF DES_FILE$ = "" THEN GOTO 990
180 ! Ensure .DES extension if missing
190 IF INSTR(1%, DES_FILE$, ".") = 0% THEN DES_FILE$ = DES_FILE$ + ".DES"
200 ! --- WRITE SPECIFICATION FILE ---
210 ON ERROR GOTO 980
220 OPEN DES_FILE$ FOR OUTPUT AS FILE #1%
230 PRINT #1%, "! DEC RMS-11 FILE DESIGN SPECIFICATION"
240 PRINT #1%, "ORGANIZATION: "; ORG$
250 PRINT #1%, "RECORD_FORMAT: FIXED"
260 PRINT #1%, "RECORD_SIZE: "; REC_SIZE%
270 PRINT #1%, "KEY_POSITION: "; KEY_POS%
280 PRINT #1%, "KEY_LENGTH: "; KEY_LEN%
290 PRINT #1%, "KEY_TYPE: "; KEY_TYPE$
300 PRINT #1%, "DUPLICATES: "; DUP_KEYS$
310 PRINT #1%, "BUCKET_SIZE: "; BUCKET_SZ%
320 CLOSE #1%
330 ON ERROR GOTO 0
340 ! --- REPORT SUCCESS ---
350 PRINT "RMSDES V2.0 - DEC RMS-11 File Design Utility"
360 PRINT "================================================================"
370 PRINT "Design File:        "; DES_FILE$
380 PRINT "Organization:       "; ORG$
390 PRINT "Record Size:        "; REC_SIZE%; " bytes"
400 PRINT "Key Position:       "; KEY_POS%
410 PRINT "Key Length:         "; KEY_LEN%; " bytes"
420 PRINT "Key Type:           "; KEY_TYPE$
430 PRINT "Bucket Size:        "; BUCKET_SZ%
440 PRINT "Status:             SUCCESS"
450 PRINT "================================================================"
460 GOTO 999
470 ! --- PARSE COMMAND LINE ---
300 ! Check if positional arguments (contains space)
302 SP% = INSTR(1%, CMD$, " ")
304 IF SP% = 0% THEN GOTO 340
306 DES_FILE$ = LEFT$(CMD$, SP% - 1%)
308 REM$ = MID$(CMD$, SP% + 1%, LEN(CMD$) - SP%)
310 SP1% = INSTR(1%, REM$, " ")
311 IF SP1% = 0% THEN GOTO 315
312 A1$ = LEFT$(REM$, SP1% - 1%)
313 REM$ = MID$(REM$, SP1% + 1%, LEN(REM$) - SP1%)
314 GOTO 316
315 A1$ = REM$
316 IF A1$ = "INDEXED" OR A1$ = "indexed" THEN ORG$ = "INDEXED"
317 IF A1$ = "SEQUENTIAL" OR A1$ = "sequential" THEN ORG$ = "SEQUENTIAL"
318 IF A1$ = "RELATIVE" OR A1$ = "relative" THEN ORG$ = "RELATIVE"
319 IF SP1% = 0% THEN GOTO 390
320 SP2% = INSTR(1%, REM$, " ")
321 IF SP2% = 0% THEN GOTO 324
322 A2$ = LEFT$(REM$, SP2% - 1%)
323 REM$ = MID$(REM$, SP2% + 1%, LEN(REM$) - SP2%)
324 IF SP2% = 0% THEN A2$ = REM$
325 IF VAL(A2$) > 0% THEN REC_SIZE% = VAL(A2$)
326 IF SP2% = 0% THEN GOTO 390
327 SP3% = INSTR(1%, REM$, " ")
328 IF SP3% = 0% THEN GOTO 331
329 A3$ = LEFT$(REM$, SP3% - 1%)
330 REM$ = MID$(REM$, SP3% + 1%, LEN(REM$) - SP3%)
331 IF SP3% = 0% THEN A3$ = REM$
332 IF VAL(A3$) > 0% THEN KEY_POS% = VAL(A3$)
333 IF SP3% = 0% THEN GOTO 390
334 SP4% = INSTR(1%, REM$, " ")
335 IF SP4% = 0% THEN A4$ = REM$
336 IF SP4% > 0% THEN A4$ = LEFT$(REM$, SP4% - 1%)
337 IF VAL(A4$) > 0% THEN KEY_LEN% = VAL(A4$)
338 GOTO 390
340 ! Switch syntax parsing
342 SW_P% = 0%
344 P% = INSTR(1%, CMD$, "/IDX")
345 IF P% > 0% AND (SW_P% = 0% OR P% < SW_P%) THEN SW_P% = P%
346 P% = INSTR(1%, CMD$, "/SEQ")
347 IF P% > 0% AND (SW_P% = 0% OR P% < SW_P%) THEN SW_P% = P%
348 P% = INSTR(1%, CMD$, "/REL")
349 IF P% > 0% AND (SW_P% = 0% OR P% < SW_P%) THEN SW_P% = P%
350 P% = INSTR(1%, CMD$, "/SIZ")
351 IF P% > 0% AND (SW_P% = 0% OR P% < SW_P%) THEN SW_P% = P%
352 P% = INSTR(1%, CMD$, "/POS")
353 IF P% > 0% AND (SW_P% = 0% OR P% < SW_P%) THEN SW_P% = P%
354 P% = INSTR(1%, CMD$, "/LEN")
355 IF P% > 0% AND (SW_P% = 0% OR P% < SW_P%) THEN SW_P% = P%
356 P% = INSTR(1%, CMD$, "/BUCKET")
357 IF P% > 0% AND (SW_P% = 0% OR P% < SW_P%) THEN SW_P% = P%
358 IF SW_P% = 0% THEN GOTO 360 ELSE GOTO 362
360 DES_FILE$ = CMD$
361 GOTO 390
362 DES_FILE$ = LEFT$(CMD$, SW_P% - 1%)
363 SW$ = MID$(CMD$, SW_P%, LEN(CMD$) - SW_P% + 1%)
364 IF INSTR(1%, SW$, "/SEQ") > 0% THEN ORG$ = "SEQUENTIAL"
365 IF INSTR(1%, SW$, "/REL") > 0% THEN ORG$ = "RELATIVE"
366 IF INSTR(1%, SW$, "/IDX") > 0% THEN ORG$ = "INDEXED"
367 P_SIZ% = INSTR(1%, SW$, "/SIZ:")
368 IF P_SIZ% > 0% THEN REC_SIZE% = VAL(MID$(SW$, P_SIZ% + 5%, 4%))
369 P_POS% = INSTR(1%, SW$, "/POS:")
370 IF P_POS% > 0% THEN KEY_POS% = VAL(MID$(SW$, P_POS% + 5%, 4%))
371 P_LEN% = INSTR(1%, SW$, "/LEN:")
372 IF P_LEN% > 0% THEN KEY_LEN% = VAL(MID$(SW$, P_LEN% + 5%, 4%))
373 P_BKT% = INSTR(1%, SW$, "/BUCKET:")
374 IF P_BKT% > 0% THEN BUCKET_SZ% = VAL(MID$(SW$, P_BKT% + 8%, 3%))
390 RETURN
475 ! --- INTERACTIVE PROMPTS ---
400 PRINT "RMSDES V2.0 - DEC RMS-11 File Design Utility"
405 PRINT ""
410 INPUT "Design specification file: "; DES_FILE$
415 IF DES_FILE$ = "" THEN GOTO 500
420 PRINT "File organization (1=INDEXED, 2=SEQUENTIAL, 3=RELATIVE) [1]: ";
425 INPUT ORG_IN$
430 IF ORG_IN$ = "2" THEN ORG$ = "SEQUENTIAL"
435 IF ORG_IN$ = "3" THEN ORG$ = "RELATIVE"
440 PRINT "Record size in bytes [255]: ";
445 INPUT SIZ_IN$
450 IF SIZ_IN$ <> "" THEN REC_SIZE% = VAL(SIZ_IN$)
455 PRINT "Primary key position [1]: ";
460 INPUT POS_IN$
465 IF POS_IN$ <> "" THEN KEY_POS% = VAL(POS_IN$)
470 PRINT "Primary key length [16]: ";
475 INPUT LEN_IN$
480 IF LEN_IN$ <> "" THEN KEY_LEN% = VAL(LEN_IN$)
485 PRINT "Primary key type (C=Character, N=Numeric) [C]: ";
490 INPUT TYP_IN$
495 IF TYP_IN$ = "N" OR TYP_IN$ = "n" THEN KEY_TYPE$ = "INTEGER" ELSE KEY_TYPE$ = "STRING"
500 RETURN
980 PRINT "RMSDES: Error creating design file: "; DES_FILE$
985 GOTO 999
990 PRINT "RMSDES: Missing design specification file."
999 END
