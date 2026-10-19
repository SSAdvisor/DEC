10 REM =================================================================
12 REM DECwindows Calculator V3.0 (DECW$CALC / dxcalc)
14 REM Digital Equipment Corporation VAX/VMS, ULTRIX & OSF/1 (1988-1995)
16 REM Sub-Project 6 of 11 in DECwindows Faithful BASIC-PLUS-2 Port
18 REM =================================================================
20 DIM TAPE_OP$(60%) \ DIM TAPE_RES%(60%)
22 ACC% = 0% \ MEM% = 0% \ NUM_TAPE% = 0%
24 CALC_MODE$ = "SCIENTIFIC" \ BASE_MODE$ = "DEC"
26 PIPE$ = "|" \ SEMI$ = ";" \ SP1$ = " " \ EQ$ = " = "
27 LBRK$ = "[" \ RBRK$ = "]" \ HASH$ = "#" \ HEX_PFX$ = "0x" \ OCT_PFX$ = "0o"
28 HEX_CHARS$ = "0123456789ABCDEF"
29 BLANKS$ = "                                                                                "
30 IS_BATCH% = 0% \ FORCE_CLI% = 0% \ S_IN$ = COMMAND$ \ GOSUB 500 \ CMD_INIT$ = S_OUT$
31 IF LEFT$(CMD_INIT$, 5%) = "--cli" THEN FORCE_CLI% = 1%
32 IF FORCE_CLI% = 1% THEN S_IN$ = MID$(CMD_INIT$, 6%, LEN(CMD_INIT$) - 5%)
33 IF FORCE_CLI% = 1% THEN GOSUB 500
34 IF FORCE_CLI% = 1% THEN CMD_INIT$ = S_OUT$
35 IF CMD_INIT$ = "--x11" OR CMD_INIT$ = "-gui" THEN CMD_INIT$ = "SAMPLE; X11; EXIT"
36 IF_X11% = 1% \ CHK_X11$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --check-gui"
37 IF CMD_INIT$ = "" AND FORCE_CLI% = 0% THEN IF_X11% = SYS(CHK_X11$)
38 IF IF_X11% = 0% THEN CMD_INIT$ = "SAMPLE; X11; EXIT"
39 IF CMD_INIT$ <> "" THEN IS_BATCH% = 1%
40 IF CMD_INIT$ <> "" THEN REM_CHAIN$ = CMD_INIT$
41 IF CMD_INIT$ <> "" THEN GOTO 54
42 PRINT "======================================================================" \ PRINT " DECwindows Calculator V3.0 (DECW$CALC / dxcalc)" \ PRINT " Digital Equipment Corporation - Scientific, Financial & Programmer" \ PRINT " Type HELP for commands, SAMPLE for engineering tape demo, EXIT." \ PRINT "======================================================================" \ PRINT "" \ REM_CHAIN$ = ""
44 IF REM_CHAIN$ <> "" THEN GOTO 54
45 IF IS_BATCH% = 1% THEN GOTO 990
46 PRINT "CALC> "; \ LINE INPUT RAW_IN$
47 IF LEN(RAW_IN$) = 0% THEN GOTO 990
48 IF ASCII(LEFT$(RAW_IN$, 1%)) = 26% THEN GOTO 990
49 IF ASCII(LEFT$(RAW_IN$, 1%)) = 0% THEN GOTO 990
52 REM_CHAIN$ = RAW_IN$
54 SC_POS% = INSTR(1%, REM_CHAIN$, SEMI$)
56 IF SC_POS% = 0% THEN CMD_LINE$ = REM_CHAIN$
58 IF SC_POS% = 0% THEN REM_CHAIN$ = ""
60 IF SC_POS% > 0% THEN CMD_LINE$ = LEFT$(REM_CHAIN$, SC_POS% - 1%)
62 IF SC_POS% > 0% THEN REM_CHAIN$ = MID$(REM_CHAIN$, SC_POS% + 1%, LEN(REM_CHAIN$) - SC_POS%)
64 S_IN$ = CMD_LINE$ \ GOSUB 500 \ CMD_LINE$ = S_OUT$
66 IF CMD_LINE$ = "" THEN GOTO 44
68 SP_POS% = INSTR(1%, CMD_LINE$, SP1$)
70 IF SP_POS% = 0% THEN VERB$ = CMD_LINE$
72 IF SP_POS% = 0% THEN ARG$ = ""
74 IF SP_POS% > 0% THEN VERB$ = LEFT$(CMD_LINE$, SP_POS% - 1%)
76 IF SP_POS% > 0% THEN ARG$ = MID$(CMD_LINE$, SP_POS% + 1%, LEN(CMD_LINE$) - SP_POS%)
78 S_IN$ = VERB$ \ GOSUB 520 \ VERB$ = S_OUT$
80 S_IN$ = ARG$ \ GOSUB 500 \ ARG$ = S_OUT$
82 IF VERB$ = "EXIT" THEN GOTO 990
84 IF VERB$ = "QUIT" THEN GOTO 990
86 IF VERB$ = "HELP" THEN GOTO 140
88 IF VERB$ = "SAMPLE" THEN GOTO 170
90 IF VERB$ = "DEMO" THEN GOTO 170
92 IF VERB$ = "SHOW" THEN GOTO 200
94 IF VERB$ = "STATUS" THEN GOTO 200
96 IF VERB$ = "SET" THEN GOTO 215
97 IF VERB$ = "ENTER" THEN GOTO 215
98 IF VERB$ = "ADD" THEN GOTO 225
99 IF VERB$ = "+" THEN GOTO 225
100 IF VERB$ = "SUB" THEN GOTO 235
101 IF VERB$ = "-" THEN GOTO 235
102 IF VERB$ = "MUL" THEN GOTO 245
103 IF VERB$ = "*" THEN GOTO 245
104 IF VERB$ = "DIV" THEN GOTO 255
105 IF VERB$ = "/" THEN GOTO 255
106 IF VERB$ = "MOD" THEN GOTO 270
108 IF VERB$ = "SQRT" THEN GOTO 285
110 IF VERB$ = "SQR" THEN GOTO 300
111 IF VERB$ = "SQUARE" THEN GOTO 300
112 IF VERB$ = "AND" THEN GOTO 310
114 IF VERB$ = "OR" THEN GOTO 318
116 IF VERB$ = "XOR" THEN GOTO 326
118 IF VERB$ = "STO" THEN GOTO 335
119 IF VERB$ = "MS" THEN GOTO 335
120 IF VERB$ = "RCL" THEN GOTO 342
121 IF VERB$ = "MR" THEN GOTO 342
122 IF VERB$ = "M+" THEN GOTO 350
123 IF VERB$ = "M-" THEN GOTO 356
124 IF VERB$ = "MC" THEN GOTO 362
126 IF VERB$ = "BASE" THEN GOTO 370
127 IF VERB$ = "RADIX" THEN GOTO 370
128 IF VERB$ = "MODE" THEN GOTO 385
130 IF VERB$ = "PMT" THEN GOTO 400
131 IF VERB$ = "LOAN" THEN GOTO 400
132 IF VERB$ = "TAPE" THEN GOTO 420
133 IF VERB$ = "HISTORY" THEN GOTO 420
134 IF VERB$ = "LIST" THEN GOTO 420
136 IF VERB$ = "DISPLAY" THEN GOTO 440
137 IF VERB$ = "SCREEN" THEN GOTO 440
138 IF VERB$ = "RENDER" THEN GOTO 440
140 IF VERB$ <> "HELP" THEN GOTO 154
141 PRINT "--- DECwindows Calculator V3.0 Commands ---"
142 PRINT "  SAMPLE / DEMO                        : Load DEC engineering calculation tape"
143 PRINT "  SET <n> / ADD <n> / SUB <n>          : Set, add, or subtract from accumulator"
144 PRINT "  MUL <n> / DIV <n> / MOD <n>          : Multiply, divide, or modulo accumulator"
145 PRINT "  SQRT / SQR                           : Integer square root or square"
146 PRINT "  AND <n> / OR <n> / XOR <n>           : Programmer bitwise logical operations"
147 PRINT "  STO (MS) / RCL (MR) / M+ / M- / MC   : Memory register operations"
148 PRINT "  BASE <DEC|HEX|OCT> / MODE <m>        : Switch radix or keypad mode"
149 PRINT "  PMT <principal|rate%|years>          : Financial loan payment calculation"
150 PRINT "  TAPE / LIST                          : Print calculation audit paper tape"
151 PRINT "  DISPLAY [ON <file>] / EXPORT <file>  : Render Motif/XUI Calculator window"
152 PRINT "  SHOW / SAVE <file> / LOAD <file>     : Status, save/load tape, CLEAR, EXIT"
153 GOTO 44
154 IF VERB$ = "EXPORT" THEN GOTO 440
156 IF VERB$ = "PRINT" THEN GOTO 440
158 IF VERB$ = "SAVE" THEN GOTO 455
160 IF VERB$ = "LOAD" THEN GOTO 472
162 IF VERB$ = "CLEAR" THEN GOTO 490
163 IF VERB$ = "C" THEN GOTO 490
164 IF VERB$ = "RESET" THEN GOTO 490
165 IF VERB$ = "X11" OR VERB$ = "GUI" OR VERB$ = "XDISPLAY" THEN GOTO 495
166 PRINT "%CALC-E-INVCMD, Unrecognized command: "; VERB$
168 GOTO 44
170 REM --- SAMPLE / DEMO ---
172 CALC_MODE$ = "SCIENTIFIC" \ BASE_MODE$ = "DEC" \ NUM_TAPE% = 6%
174 TAPE_OP$(1%) = "SET 1024" \ TAPE_RES%(1%) = 1024%
176 TAPE_OP$(2%) = "ADD 2048" \ TAPE_RES%(2%) = 3072%
178 TAPE_OP$(3%) = "MUL 4" \ TAPE_RES%(3%) = 12288%
180 TAPE_OP$(4%) = "DIV 3" \ TAPE_RES%(4%) = 4096%
182 TAPE_OP$(5%) = "STO (M=4096)" \ TAPE_RES%(5%) = 4096%
184 TAPE_OP$(6%) = "SUB 256" \ TAPE_RES%(6%) = 3840%
186 ACC% = 3840% \ MEM% = 4096%
188 PRINT "[Loaded Sample DECwindows Calculator Tape: 6 operations, ACC = "; ACC%; ", MEM = "; MEM%; "]"
190 GOTO 44
200 REM --- SHOW / STATUS ---
202 CNV_V% = ACC% \ GOSUB 550
204 PRINT "=== DECwindows Calculator Status ==="
206 PRINT "  Keypad Mode    : "; CALC_MODE$; "  |  Active Base: "; BASE_MODE$
208 PRINT "  Accumulator    : "; ACC%; " (DEC)  |  "; HEX_PFX$; HEX_OUT$; " (HEX)  |  "; OCT_PFX$; OCT_OUT$; " (OCT)"
210 PRINT "  Memory Reg (M) : "; MEM%
212 PRINT "  Tape Entries   : "; NUM_TAPE%; " operations"
214 GOTO 44
215 REM --- SET <n> / ENTER <n> ---
216 ACC% = VAL(ARG$) \ REC_OP$ = "SET " + ARG$ \ GOSUB 540
218 GOSUB 535 \ GOTO 44
225 REM --- ADD <n> / + <n> ---
226 OP_V% = VAL(ARG$) \ ACC% = ACC% + OP_V% \ REC_OP$ = "ADD " + ARG$ \ GOSUB 540
228 GOSUB 535 \ GOTO 44
235 REM --- SUB <n> / - <n> ---
236 OP_V% = VAL(ARG$) \ ACC% = ACC% - OP_V% \ REC_OP$ = "SUB " + ARG$ \ GOSUB 540
238 GOSUB 535 \ GOTO 44
245 REM --- MUL <n> / * <n> ---
246 OP_V% = VAL(ARG$) \ ACC% = ACC% * OP_V% \ REC_OP$ = "MUL " + ARG$ \ GOSUB 540
248 GOSUB 535 \ GOTO 44
255 REM --- DIV <n> / / <n> ---
256 OP_V% = VAL(ARG$)
258 IF OP_V% = 0% THEN PRINT "%CALC-E-DIVZERO, Division by zero error."
260 IF OP_V% = 0% THEN GOTO 44
262 ACC% = INT(ACC% / OP_V%) \ REC_OP$ = "DIV " + ARG$ \ GOSUB 540
264 GOSUB 535 \ GOTO 44
270 REM --- MOD <n> ---
272 OP_V% = VAL(ARG$)
274 IF OP_V% = 0% THEN PRINT "%CALC-E-DIVZERO, Modulo by zero error."
276 IF OP_V% = 0% THEN GOTO 44
278 Q_V% = INT(ACC% / OP_V%) \ P_V% = Q_V% * OP_V% \ ACC% = ACC% - P_V%
280 REC_OP$ = "MOD " + ARG$ \ GOSUB 540 \ GOSUB 535 \ GOTO 44
285 REM --- SQRT ---
286 IF ACC% < 0% THEN PRINT "%CALC-E-IMAGINARY, Square root of negative number."
287 IF ACC% < 0% THEN GOTO 44
288 SQ_R% = 0%
289 SQ_N% = SQ_R% + 1% \ SQ_P% = SQ_N% * SQ_N%
290 IF SQ_P% > ACC% THEN GOTO 294
292 SQ_R% = SQ_R% + 1% \ GOTO 289
294 ACC% = SQ_R% \ REC_OP$ = "SQRT" \ GOSUB 540 \ GOSUB 535 \ GOTO 44
300 REM --- SQR / SQUARE ---
302 ACC% = ACC% * ACC% \ REC_OP$ = "SQR" \ GOSUB 540 \ GOSUB 535 \ GOTO 44
310 REM --- AND <n> ---
312 OP_V% = VAL(ARG$) \ BW_MODE% = 1% \ GOSUB 580 \ REC_OP$ = "AND " + ARG$ \ GOSUB 540 \ GOSUB 535 \ GOTO 44
318 REM --- OR <n> ---
320 OP_V% = VAL(ARG$) \ BW_MODE% = 2% \ GOSUB 580 \ REC_OP$ = "OR " + ARG$ \ GOSUB 540 \ GOSUB 535 \ GOTO 44
326 REM --- XOR <n> ---
328 OP_V% = VAL(ARG$) \ BW_MODE% = 3% \ GOSUB 580 \ REC_OP$ = "XOR " + ARG$ \ GOSUB 540 \ GOSUB 535 \ GOTO 44
335 REM --- STO / MS ---
336 MEM% = ACC% \ S_IN$ = STR$(MEM%) \ GOSUB 500 \ REC_OP$ = "STO M=" + S_OUT$ \ GOSUB 540
338 PRINT "[Stored "; MEM%; " into Memory Register M]" \ GOTO 44
342 REM --- RCL / MR ---
344 ACC% = MEM% \ REC_OP$ = "RCL (M)" \ GOSUB 540 \ GOSUB 535 \ GOTO 44
350 REM --- M+ ---
352 MEM% = MEM% + ACC% \ PRINT "[Memory M+ : M = "; MEM%; "]" \ GOTO 44
356 REM --- M- ---
358 MEM% = MEM% - ACC% \ PRINT "[Memory M- : M = "; MEM%; "]" \ GOTO 44
362 REM --- MC ---
364 MEM% = 0% \ PRINT "[Memory Register M cleared]" \ GOTO 44
370 REM --- BASE <DEC|HEX|OCT> ---
372 S_IN$ = ARG$ \ GOSUB 520 \ B_REQ$ = S_OUT$
374 IF B_REQ$ = "DEC" THEN BASE_MODE$ = "DEC"
376 IF B_REQ$ = "HEX" THEN BASE_MODE$ = "HEX"
378 IF B_REQ$ = "OCT" THEN BASE_MODE$ = "OCT"
380 CNV_V% = ACC% \ GOSUB 550
382 PRINT "[Radix Base: "; BASE_MODE$; " | DEC="; ACC%; " HEX="; HEX_PFX$; HEX_OUT$; " OCT="; OCT_PFX$; OCT_OUT$; "]"
384 GOTO 44
385 REM --- MODE <SCIENTIFIC|FINANCIAL|PROGRAMMER> ---
386 S_IN$ = ARG$ \ GOSUB 520 \ M_REQ$ = S_OUT$
388 IF M_REQ$ <> "" THEN CALC_MODE$ = M_REQ$
390 PRINT "[Calculator Keypad Mode set to: "; CALC_MODE$; "]" \ GOTO 44
400 REM --- PMT <principal|rate%|years> / LOAN ---
401 P1% = INSTR(1%, ARG$, PIPE$)
402 IF P1% = 0% THEN PRINT "%CALC-E-SYNTAX, Usage: PMT <principal|rate_pct|years>"
403 IF P1% = 0% THEN GOTO 44
404 L_PR% = VAL(LEFT$(ARG$, P1% - 1%)) \ R1$ = MID$(ARG$, P1% + 1%, LEN(ARG$) - P1%)
405 P2% = INSTR(1%, R1$, PIPE$)
406 IF P2% = 0% THEN PRINT "%CALC-E-SYNTAX, Usage: PMT <principal|rate_pct|years>"
407 IF P2% = 0% THEN GOTO 44
408 L_RT% = VAL(LEFT$(R1$, P2% - 1%)) \ L_YR% = VAL(MID$(R1$, P2% + 1%, LEN(R1$) - P2%))
409 IF L_YR% < 1% THEN L_YR% = 1%
410 T_I1% = INT(L_PR% / 100%) \ TOT_INT% = T_I1% * L_RT% * L_YR% \ TOT_PAY% = L_PR% + TOT_INT%
412 ANN_PMT% = INT(TOT_PAY% / L_YR%) \ MON_PMT% = INT(ANN_PMT% / 12%)
414 ACC% = ANN_PMT% \ REC_OP$ = "PMT " + ARG$ \ GOSUB 540
416 PRINT "=== Financial Loan Analysis ==="
417 PRINT "  Principal: "; L_PR%; " | Rate: "; L_RT%; "% | Term: "; L_YR%; " yrs | Annual Pmt: "; ANN_PMT%; " (Monthly ~"; MON_PMT%; ")"
418 GOTO 44
420 REM --- TAPE / HISTORY / LIST ---
422 PRINT "=== DECwindows Calculator Paper Audit Tape ==="
424 PRINT "Step | Operation            | Decimal  | Hexadecimal | Octal"
426 PRINT "-----+----------------------+----------+-------------+----------"
428 I% = 1%
430 IF I% > NUM_TAPE% THEN GOTO 438
431 S_IN$ = STR$(I%) \ GOSUB 500 \ C_ST$ = LEFT$(S_OUT$ + BLANKS$, 4%)
432 C_OP$ = LEFT$(TAPE_OP$(I%) + BLANKS$, 20%)
433 CNV_V% = TAPE_RES%(I%) \ GOSUB 550
434 S_IN$ = STR$(TAPE_RES%(I%)) \ GOSUB 500 \ C_DC$ = LEFT$(S_OUT$ + BLANKS$, 8%)
435 C_HX$ = LEFT$(HEX_PFX$ + HEX_OUT$ + BLANKS$, 11%) \ C_OC$ = LEFT$(OCT_PFX$ + OCT_OUT$ + BLANKS$, 8%)
436 PRINT C_ST$; " | "; C_OP$; " | "; C_DC$; " | "; C_HX$; " | "; C_OC$
437 I% = I% + 1% \ GOTO 430
438 PRINT "Total tape entries: "; NUM_TAPE% \ GOTO 44
440 REM --- DISPLAY [ON <file>] / SCREEN / RENDER / EXPORT ---
441 OUT_FILE$ = "" \ S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
442 IF VERB$ = "EXPORT" THEN OUT_FILE$ = ARG$
443 IF LEFT$(UARG$, 3%) = "ON " THEN OUT_FILE$ = MID$(ARG$, 4%, LEN(ARG$) - 3%)
444 S_IN$ = OUT_FILE$ \ GOSUB 500 \ OUT_FILE$ = S_OUT$
446 GOSUB 600
448 IF OUT_FILE$ <> "" THEN PRINT "[Calculator window exported to "; OUT_FILE$; "]"
450 GOTO 44
455 REM --- SAVE <file> ---
456 IF ARG$ = "" THEN PRINT "%CALC-E-NOFILE, Specify filename for SAVE."
457 IF ARG$ = "" THEN GOTO 44
458 OPEN ARG$ FOR OUTPUT AS FILE #1%
459 S_IN$ = STR$(ACC%) \ GOSUB 500 \ AC_S$ = S_OUT$ \ S_IN$ = STR$(MEM%) \ GOSUB 500 \ MM_S$ = S_OUT$
460 S_REC$ = "STATE" + PIPE$ + CALC_MODE$ + PIPE$ + BASE_MODE$ + PIPE$ + AC_S$ + PIPE$ + MM_S$
461 PRINT #1%, S_REC$ \ I% = 1%
464 IF I% > NUM_TAPE% THEN GOTO 469
465 S_IN$ = STR$(TAPE_RES%(I%)) \ GOSUB 500 \ TR_S$ = S_OUT$
466 S_REC$ = "TAPE" + PIPE$ + TAPE_OP$(I%) + PIPE$ + TR_S$
467 PRINT #1%, S_REC$ \ I% = I% + 1% \ GOTO 464
469 CLOSE #1%
470 PRINT "[Saved "; NUM_TAPE%; " tape entries to "; ARG$; "]" \ GOTO 44
472 REM --- LOAD <file> ---
473 IF ARG$ = "" THEN PRINT "%CALC-E-NOFILE, Specify filename for LOAD."
474 IF ARG$ = "" THEN GOTO 44
475 OPEN ARG$ FOR INPUT AS FILE #1%
476 NUM_TAPE% = 0%
477 LINE INPUT #1%, L_REC$
478 IF LEN(L_REC$) = 0% THEN GOTO 487
479 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 487
480 S_IN$ = L_REC$ \ GOSUB 500 \ L_REC$ = S_OUT$
482 IF LEFT$(L_REC$, 6%) = "STATE|" THEN GOSUB 660
484 IF LEFT$(L_REC$, 5%) = "TAPE|" THEN GOSUB 680
485 GOTO 477
487 CLOSE #1%
488 PRINT "[Loaded "; NUM_TAPE%; " tape entries from "; ARG$; " (ACC="; ACC%; ", MEM="; MEM%; ")]" \ GOTO 44
490 REM --- CLEAR / C / RESET ---
492 ACC% = 0% \ MEM% = 0% \ NUM_TAPE% = 0%
494 PRINT "[Calculator accumulator, memory, and tape cleared]" \ GOTO 44
495 OUT_FILE$ = "/tmp/decw_calculator.txt" \ GOSUB 600
496 X_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app calculator --frame /tmp/decw_calculator.txt"
497 X_RC% = SYS(X_CMD$) \ GOTO 44
500 REM --- Subroutine: Trim leading/trailing spaces (S_IN$ -> S_OUT$) ---
502 S_OUT$ = S_IN$
504 IF LEN(S_OUT$) = 0% THEN GOTO 518
506 IF LEFT$(S_OUT$, 1%) = " " THEN S_OUT$ = MID$(S_OUT$, 2%, LEN(S_OUT$) - 1%)
508 IF LEFT$(S_OUT$, 1%) = " " THEN GOTO 504
510 IF LEN(S_OUT$) = 0% THEN GOTO 518
512 IF MID$(S_OUT$, LEN(S_OUT$), 1%) = " " THEN S_OUT$ = LEFT$(S_OUT$, LEN(S_OUT$) - 1%)
514 IF MID$(S_OUT$, LEN(S_OUT$), 1%) = " " THEN GOTO 510
518 RETURN
520 REM --- Subroutine: Uppercase string (S_IN$ -> S_OUT$) ---
522 S_OUT$ = "" \ U_I% = 1% \ U_L% = LEN(S_IN$)
524 IF U_I% > U_L% THEN GOTO 534
526 U_C$ = MID$(S_IN$, U_I%, 1%) \ U_A% = ASCII(U_C$)
528 IF U_A% >= 97% AND U_A% <= 122% THEN U_C$ = CHR$(U_A% - 32%)
530 S_OUT$ = S_OUT$ + U_C$ \ U_I% = U_I% + 1% \ GOTO 524
534 RETURN
535 REM --- Subroutine: Print active display readout ---
536 CNV_V% = ACC% \ GOSUB 550
537 PRINT "  Display ["; BASE_MODE$; "]: "; ACC%; " ("; HEX_PFX$; HEX_OUT$; " | "; OCT_PFX$; OCT_OUT$; ")  [M="; MEM%; "]"
538 RETURN
540 REM --- Subroutine: Append REC_OP$ and ACC% to paper tape ---
542 IF NUM_TAPE% < 60% THEN NUM_TAPE% = NUM_TAPE% + 1%
544 TAPE_OP$(NUM_TAPE%) = REC_OP$ \ TAPE_RES%(NUM_TAPE%) = ACC%
546 RETURN
550 REM --- Subroutine: Convert CNV_V% to HEX_OUT$ and OCT_OUT$ ---
551 W_V% = CNV_V%
552 IF W_V% < 0% THEN W_V% = 0% - W_V%
554 IF W_V% = 0% THEN HEX_OUT$ = "0"
555 IF W_V% = 0% THEN OCT_OUT$ = "0"
556 IF W_V% = 0% THEN GOTO 578
558 HEX_OUT$ = "" \ T_V% = W_V%
560 IF T_V% <= 0% THEN GOTO 566
562 Q_H% = INT(T_V% / 16%) \ P_H% = Q_H% * 16% \ R_H% = T_V% - P_H%
564 HEX_OUT$ = MID$(HEX_CHARS$, R_H% + 1%, 1%) + HEX_OUT$ \ T_V% = Q_H% \ GOTO 560
566 OCT_OUT$ = "" \ T_V% = W_V%
568 IF T_V% <= 0% THEN GOTO 578
570 Q_O% = INT(T_V% / 8%) \ P_O% = Q_O% * 8% \ R_O% = T_V% - P_O%
572 OCT_OUT$ = MID$(HEX_CHARS$, R_O% + 1%, 1%) + OCT_OUT$ \ T_V% = Q_O% \ GOTO 568
578 RETURN
580 REM --- Subroutine: Bitwise AND(1), OR(2), XOR(3) on ACC% and OP_V% ---
581 A_B% = ACC% \ B_B% = OP_V% \ RES_B% = 0% \ PWR_B% = 1% \ BIT_I% = 1%
582 IF A_B% < 0% THEN A_B% = 0% - A_B%
583 IF B_B% < 0% THEN B_B% = 0% - B_B%
584 IF BIT_I% > 15% THEN GOTO 598
586 QA% = INT(A_B% / 2%) \ PA% = QA% * 2% \ BA% = A_B% - PA% \ A_B% = QA%
588 QB% = INT(B_B% / 2%) \ PB% = QB% * 2% \ BB% = B_B% - PB% \ B_B% = QB%
590 B_OUT% = 0%
591 IF BW_MODE% = 1% THEN B_OUT% = BA% * BB%
592 IF BW_MODE% = 2% AND BA% + BB% > 0% THEN B_OUT% = 1%
594 IF BW_MODE% = 3% AND BA% <> BB% THEN B_OUT% = 1%
596 P_BIT% = B_OUT% * PWR_B% \ RES_B% = RES_B% + P_BIT% \ PWR_B% = PWR_B% * 2% \ BIT_I% = BIT_I% + 1% \ GOTO 584
598 ACC% = RES_B% \ RETURN
600 REM --- Subroutine: Render Motif/XUI Calculator Window ---
602 IF OUT_FILE$ <> "" THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #3%
603 B_L$ = "| " \ B_R$ = " |" \ W_BTN$ = " [v][^] |" \ W_M$ = " | M=" \ W_HX$ = " | HEX: " \ W_OC$ = " | OCT: " \ W_TP$ = " | Tape Entries: "
604 L1$ = "+----------------------------------------------------------------------------+"
606 W_T$ = LEFT$(CALC_MODE$ + SP1$ + LBRK$ + BASE_MODE$ + RBRK$ + BLANKS$, 36%)
608 L2$ = "| [=] DECwindows Calculator (dxcalc) - " + W_T$ + W_BTN$
610 L3$ = "| File  Edit  Mode  Base  Tape  Help                                         |"
612 CNV_V% = ACC% \ GOSUB 550
614 S_IN$ = STR$(ACC%) \ GOSUB 500 \ AC_S$ = S_OUT$ \ S_IN$ = STR$(MEM%) \ GOSUB 500 \ MM_S$ = S_OUT$
616 PAD_OUT$ = LEFT$("LCD: " + AC_S$ + W_HX$ + HEX_PFX$ + HEX_OUT$ + W_OC$ + OCT_PFX$ + OCT_OUT$ + W_M$ + MM_S$ + BLANKS$, 74%)
618 L4$ = B_L$ + PAD_OUT$ + B_R$
620 W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = L2$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
622 W_LN$ = L3$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = L4$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
624 W_LN$ = "|  [ MC ]  [ MR ]  [ M+ ]  [ M- ]  [ MS ]   |   [SQRT]  [SQR ]  [MOD ] [PMT] |" \ GOSUB 650
626 W_LN$ = "|  [ 7  ]  [ 8  ]  [ 9  ]  [ /  ]  [AND ]   |   [ 4  ]  [ 5  ]  [ 6  ] [ * ] |" \ GOSUB 650
628 W_LN$ = "|  [ 1  ]  [ 2  ]  [ 3  ]  [ -  ]  [ OR ]   |   [ 0  ]  [ =  ]  [ +  ] [XOR] |" \ GOSUB 650
630 W_LN$ = L1$ \ GOSUB 650
632 S_IN$ = STR$(NUM_TAPE%) \ GOSUB 500 \ NT_S$ = S_OUT$
634 PAD_OUT$ = LEFT$("Status: Ready | Mode: " + CALC_MODE$ + W_TP$ + NT_S$ + BLANKS$, 74%)
636 W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
638 IF OUT_FILE$ <> "" THEN CLOSE #3%
640 RETURN
650 IF OUT_FILE$ = "" THEN PRINT W_LN$
652 IF OUT_FILE$ <> "" THEN PRINT #3%, W_LN$
654 RETURN
660 REM --- Subroutine: Parse STATE|mode|base|acc|mem ---
662 H_R$ = MID$(L_REC$, 7%, LEN(L_REC$) - 6%) \ H1% = INSTR(1%, H_R$, PIPE$)
663 IF H1% = 0% THEN GOTO 674
664 CALC_MODE$ = LEFT$(H_R$, H1% - 1%) \ H_R$ = MID$(H_R$, H1% + 1%, LEN(H_R$) - H1%) \ H2% = INSTR(1%, H_R$, PIPE$)
666 IF H2% = 0% THEN GOTO 674
668 BASE_MODE$ = LEFT$(H_R$, H2% - 1%) \ H_R$ = MID$(H_R$, H2% + 1%, LEN(H_R$) - H2%) \ H3% = INSTR(1%, H_R$, PIPE$)
670 IF H3% = 0% THEN GOTO 674
672 ACC% = VAL(LEFT$(H_R$, H3% - 1%)) \ MEM% = VAL(MID$(H_R$, H3% + 1%, LEN(H_R$) - H3%))
674 RETURN
680 REM --- Subroutine: Parse TAPE|op|res ---
682 G_R$ = MID$(L_REC$, 6%, LEN(L_REC$) - 5%) \ G1% = INSTR(1%, G_R$, PIPE$)
683 IF G1% = 0% THEN GOTO 690
684 NUM_TAPE% = NUM_TAPE% + 1%
686 TAPE_OP$(NUM_TAPE%) = LEFT$(G_R$, G1% - 1%)
688 TAPE_RES%(NUM_TAPE%) = VAL(MID$(G_R$, G1% + 1%, LEN(G_R$) - G1%))
690 RETURN
990 PRINT "DECwindows Calculator V3.0 session terminated."
999 END
