10 REM =================================================================
12 REM DECwindows Clock V3.0 (DECW$CLOCK / dxclock)
14 REM Digital Equipment Corporation VAX/VMS, ULTRIX & OSF/1 (1988-1995)
16 REM Sub-Project 7 of 11 in DECwindows Faithful BASIC-PLUS-2 Port
18 REM =================================================================
20 DIM WZ_SITE$(12%) \ DIM WZ_LOC$(12%) \ DIM WZ_OFF%(12%)
22 CLK_HR% = 14% \ CLK_MN% = 30% \ CLK_SC% = 0%
24 CLK_DATE$ = "TUE 19-OCT-1993" \ CLK_TZ$ = "EST (UTC-5 Maynard MLO)"
25 FACE_MODE$ = "BOTH" \ MIL_MODE% = 1% \ CHIME_ON% = 1%
26 ALM_ON% = 0% \ ALM_HR% = 15% \ ALM_MN% = 0% \ ALM_MSG$ = "No Alarm Set"
27 PIPE$ = "|" \ SEMI$ = ";" \ COLON$ = ":" \ SP1$ = " " \ ZERO$ = "0"
28 LBRK$ = "[" \ RBRK$ = "]" \ PLUS$ = "+" \ MINUS$ = "-"
29 BLANKS$ = "                                                                                "
30 NUM_WZ% = 0% \ IS_BATCH% = 0% \ CMD_INIT$ = COMMAND$
31 IF CMD_INIT$ <> "" THEN IS_BATCH% = 1%
32 IF CMD_INIT$ <> "" THEN REM_CHAIN$ = CMD_INIT$
33 IF CMD_INIT$ <> "" THEN GOTO 54
34 PRINT "======================================================================"
35 PRINT " DECwindows Clock V3.0 (DECW$CLOCK / dxclock)"
36 PRINT " Digital Equipment Corporation - Desktop Analog/Digital Timekeeper"
37 PRINT " Type HELP for commands, SAMPLE for Maynard/Nashua clock demo, EXIT."
38 PRINT "======================================================================"
39 PRINT ""
40 REM --- Main Interactive REPL & Command Chain Loop ---
42 REM_CHAIN$ = ""
44 IF REM_CHAIN$ <> "" THEN GOTO 54
45 IF IS_BATCH% = 1% THEN GOTO 990
46 PRINT "CLOCK> "; \ LINE INPUT RAW_IN$
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
96 IF VERB$ = "SETTIME" THEN GOTO 225
98 IF VERB$ = "TIME" THEN GOTO 225
100 IF VERB$ = "SETDATE" THEN GOTO 250
102 IF VERB$ = "DATE" THEN GOTO 250
104 IF VERB$ = "TICK" THEN GOTO 260
106 IF VERB$ = "ADVANCE" THEN GOTO 260
108 IF VERB$ = "ALARM" THEN GOTO 290
110 IF VERB$ = "CHIME" THEN GOTO 325
112 IF VERB$ = "FORMAT" THEN GOTO 340
114 IF VERB$ = "FACE" THEN GOTO 355
116 IF VERB$ = "MODE" THEN GOTO 355
118 IF VERB$ = "ZONES" THEN GOTO 370
120 IF VERB$ = "WORLD" THEN GOTO 370
122 IF VERB$ = "SITES" THEN GOTO 370
124 IF VERB$ = "ADDZONE" THEN GOTO 400
126 IF VERB$ = "DIAL" THEN GOTO 425
128 IF VERB$ = "ANALOG" THEN GOTO 425
130 IF VERB$ = "DISPLAY" THEN GOTO 440
132 IF VERB$ = "SCREEN" THEN GOTO 440
134 IF VERB$ = "RENDER" THEN GOTO 440
140 IF VERB$ <> "HELP" THEN GOTO 154
141 PRINT "--- DECwindows Clock V3.0 Commands ---"
142 PRINT "  SAMPLE / DEMO                        : Load Maynard MLO clock & world zones"
143 PRINT "  SETTIME <HH:MM[:SS]> / TIME          : Set workstation clock time"
144 PRINT "  SETDATE <date> / DATE                : Set workstation date banner"
145 PRINT "  TICK [mins] / ADVANCE [mins]         : Advance clock and test alarm/chime"
146 PRINT "  ALARM <ON|OFF|HH:MM|message>         : Configure or toggle alarm bell"
147 PRINT "  CHIME <ON|OFF> / FORMAT <12|24>      : Toggle hourly chime or 12/24h mode"
148 PRINT "  FACE <ANALOG|DIGITAL|BOTH>           : Select clock face presentation"
149 PRINT "  ZONES / WORLD / ADDZONE <c|loc|off>  : View or add DEC world timezones"
150 PRINT "  DIAL / ANALOG                        : Render ASCII analog clock dial"
151 PRINT "  DISPLAY [ON <file>] / EXPORT <file>  : Render Motif/XUI Clock window"
152 PRINT "  SHOW / SAVE <file> / LOAD <file>     : Status, save/load settings, CLEAR, EXIT"
153 GOTO 44
154 IF VERB$ = "EXPORT" THEN GOTO 440
156 IF VERB$ = "PRINT" THEN GOTO 440
158 IF VERB$ = "SAVE" THEN GOTO 455
160 IF VERB$ = "LOAD" THEN GOTO 472
162 IF VERB$ = "CLEAR" THEN GOTO 490
164 IF VERB$ = "RESET" THEN GOTO 490
166 PRINT "%CLOCK-E-INVCMD, Unrecognized command: "; VERB$
168 GOTO 44
170 REM --- SAMPLE / DEMO ---
172 CLK_HR% = 14% \ CLK_MN% = 30% \ CLK_SC% = 0%
174 CLK_DATE$ = "TUE 19-OCT-1993" \ CLK_TZ$ = "EST (UTC-5 Maynard MLO / Nashua ZKO)"
176 FACE_MODE$ = "BOTH" \ MIL_MODE% = 1% \ CHIME_ON% = 1%
178 ALM_ON% = 1% \ ALM_HR% = 15% \ ALM_MN% = 0% \ ALM_MSG$ = "VAXcluster Quorum & Backup Window"
180 NUM_WZ% = 6%
181 WZ_SITE$(1%) = "MLO" \ WZ_LOC$(1%) = "Maynard Mill, MA (HQ)" \ WZ_OFF%(1%) = 0% - 5%
182 WZ_SITE$(2%) = "ZKO" \ WZ_LOC$(2%) = "Nashua Spit Brook, NH" \ WZ_OFF%(2%) = 0% - 5%
183 WZ_SITE$(3%) = "SRC" \ WZ_LOC$(3%) = "Palo Alto Systems Research" \ WZ_OFF%(3%) = 0% - 8%
184 WZ_SITE$(4%) = "REO" \ WZ_LOC$(4%) = "Reading Engineering, UK" \ WZ_OFF%(4%) = 0%
185 WZ_SITE$(5%) = "VBO" \ WZ_LOC$(5%) = "Valbonne Centre Technique" \ WZ_OFF%(5%) = 1%
186 WZ_SITE$(6%) = "TKO" \ WZ_LOC$(6%) = "Tokyo Engineering Center" \ WZ_OFF%(6%) = 9%
188 GOSUB 540
190 PRINT "[Loaded Sample DECwindows Clock: "; TIME_STR$; " on "; CLK_DATE$; " (6 DEC World Sites)]"
192 GOTO 44
200 REM --- SHOW / STATUS ---
202 GOSUB 540 \ GOSUB 560
204 CH_ST$ = "OFF"
205 IF CHIME_ON% = 1% THEN CH_ST$ = "ON (Hourly Bell)"
206 AL_ST$ = "OFF"
207 IF ALM_ON% = 1% THEN AL_ST$ = "ON"
208 FMT_ST$ = "12-Hour (AM/PM)"
209 IF MIL_MODE% = 1% THEN FMT_ST$ = "24-Hour (Military)"
210 PRINT "=== DECwindows Clock Status ==="
212 PRINT "  Current Time   : "; TIME_STR$; " ("; FMT_ST$; ")"
214 PRINT "  Current Date   : "; CLK_DATE$; "  |  Zone: "; CLK_TZ$
216 PRINT "  Clock Face     : "; FACE_MODE$; "  |  Chime: "; CH_ST$
218 PRINT "  Alarm Status   : "; AL_ST$; " @ "; ALM_STR$; " - "; ALM_MSG$
220 PRINT "  World Sites    : "; NUM_WZ%; " DEC engineering locations"
222 GOTO 44
225 REM --- SETTIME <HH:MM[:SS]> / TIME ---
226 IF ARG$ = "" THEN GOSUB 540
227 IF ARG$ = "" THEN PRINT "Current Time: "; TIME_STR$; " ("; CLK_DATE$; ")"
228 IF ARG$ = "" THEN GOTO 44
230 C1% = INSTR(1%, ARG$, COLON$)
232 IF C1% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: SETTIME <HH:MM[:SS]>"
233 IF C1% = 0% THEN GOTO 44
234 N_H% = VAL(LEFT$(ARG$, C1% - 1%)) \ R_T$ = MID$(ARG$, C1% + 1%, LEN(ARG$) - C1%)
236 C2% = INSTR(1%, R_T$, COLON$)
237 IF C2% = 0% THEN N_M% = VAL(R_T$)
238 IF C2% = 0% THEN N_S% = 0%
239 IF C2% > 0% THEN N_M% = VAL(LEFT$(R_T$, C2% - 1%))
240 IF C2% > 0% THEN N_S% = VAL(MID$(R_T$, C2% + 1%, LEN(R_T$) - C2%))
241 IF N_H% < 0% OR N_H% > 23% THEN PRINT "%CLOCK-E-INVTIME, Hour must be 0..23."
242 IF N_H% < 0% OR N_H% > 23% THEN GOTO 44
243 IF N_M% < 0% OR N_M% > 59% THEN PRINT "%CLOCK-E-INVTIME, Minute must be 0..59."
244 IF N_M% < 0% OR N_M% > 59% THEN GOTO 44
245 CLK_HR% = N_H% \ CLK_MN% = N_M% \ CLK_SC% = N_S% \ GOSUB 540
246 PRINT "[Workstation Clock set to "; TIME_STR$; "]" \ GOTO 44
250 REM --- SETDATE <date> / DATE ---
252 IF ARG$ <> "" THEN CLK_DATE$ = ARG$
254 PRINT "[Workstation Date Banner: "; CLK_DATE$; "]" \ GOTO 44
260 REM --- TICK [mins] / ADVANCE [mins] ---
262 ADV_M% = 1%
264 IF ARG$ <> "" THEN ADV_M% = VAL(ARG$)
266 IF ADV_M% < 1% THEN ADV_M% = 1%
268 STEP_I% = 1%
270 IF STEP_I% > ADV_M% THEN GOTO 284
272 CLK_MN% = CLK_MN% + 1%
274 IF CLK_MN% < 60% THEN GOTO 280
276 CLK_MN% = 0% \ CLK_HR% = CLK_HR% + 1%
277 IF CLK_HR% >= 24% THEN CLK_HR% = 0%
278 IF CHIME_ON% = 1% THEN PRINT "[CHIME! Hourly Bell Ring at "; CLK_HR%; ":00]"
280 IF ALM_ON% = 1% AND CLK_HR% = ALM_HR% AND CLK_MN% = ALM_MN% THEN PRINT "[ALARM! Bell Ring at "; ALM_HR%; ":"; ALM_MN%; " - "; ALM_MSG$; "]"
282 STEP_I% = STEP_I% + 1% \ GOTO 270
284 GOSUB 540 \ PRINT "[Clock advanced "; ADV_M%; " min(s) -> "; TIME_STR$; "]" \ GOTO 44
290 REM --- ALARM <ON|OFF|HH:MM|msg> ---
292 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
294 IF UARG$ = "ON" THEN ALM_ON% = 1%
295 IF UARG$ = "ON" THEN PRINT "[Alarm Bell ENABLED]"
296 IF UARG$ = "ON" THEN GOTO 44
298 IF UARG$ = "OFF" THEN ALM_ON% = 0%
299 IF UARG$ = "OFF" THEN PRINT "[Alarm Bell DISABLED]"
300 IF UARG$ = "OFF" THEN GOTO 44
302 P1% = INSTR(1%, ARG$, PIPE$)
304 IF P1% = 0% THEN T_PART$ = ARG$
305 IF P1% > 0% THEN T_PART$ = LEFT$(ARG$, P1% - 1%)
306 IF P1% > 0% THEN ALM_MSG$ = MID$(ARG$, P1% + 1%, LEN(ARG$) - P1%)
308 C1% = INSTR(1%, T_PART$, COLON$)
310 IF C1% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: ALARM <ON|OFF|HH:MM|message>"
311 IF C1% = 0% THEN GOTO 44
312 ALM_HR% = VAL(LEFT$(T_PART$, C1% - 1%)) \ ALM_MN% = VAL(MID$(T_PART$, C1% + 1%, LEN(T_PART$) - C1%))
314 ALM_ON% = 1% \ GOSUB 560
316 PRINT "[Alarm Set for "; ALM_STR$; " (ENABLED) : "; ALM_MSG$; "]" \ GOTO 44
325 REM --- CHIME <ON|OFF> ---
326 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
328 IF UARG$ = "ON" THEN CHIME_ON% = 1%
330 IF UARG$ = "OFF" THEN CHIME_ON% = 0%
332 PRINT "[Hourly Chime set to: "; UARG$; "]" \ GOTO 44
340 REM --- FORMAT <12|24> ---
342 IF ARG$ = "12" THEN MIL_MODE% = 0%
344 IF ARG$ = "24" THEN MIL_MODE% = 1%
346 GOSUB 540 \ PRINT "[Clock Digital Format set to "; ARG$; "-Hour -> "; TIME_STR$; "]" \ GOTO 44
355 REM --- FACE <ANALOG|DIGITAL|BOTH> / MODE ---
356 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
358 IF UARG$ <> "" THEN FACE_MODE$ = UARG$
360 PRINT "[Clock Face Mode set to: "; FACE_MODE$; "]" \ GOTO 44
370 REM --- ZONES / WORLD / SITES ---
372 PRINT "=== DEC Worldwide Engineering Timezones (Base: Maynard MLO UTC-5) ==="
374 PRINT "Site | Location                     | UTC Offset | Local Time"
376 PRINT "-----+------------------------------+------------+------------"
378 UTC_HR% = CLK_HR% + 5%
379 IF UTC_HR% >= 24% THEN UTC_HR% = UTC_HR% - 24%
380 I% = 1%
382 IF I% > NUM_WZ% THEN GOTO 396
384 Z_HR% = UTC_HR% + WZ_OFF%(I%)
385 IF Z_HR% < 0% THEN Z_HR% = Z_HR% + 24%
386 IF Z_HR% >= 24% THEN Z_HR% = Z_HR% - 24%
387 FMT_N% = Z_HR% \ GOSUB 535 \ Z_HS$ = FMT_S$ \ FMT_N% = CLK_MN% \ GOSUB 535 \ Z_MS$ = FMT_S$
388 S_IN$ = STR$(WZ_OFF%(I%)) \ GOSUB 500 \ OF_S$ = S_OUT$
389 IF WZ_OFF%(I%) >= 0% THEN OF_S$ = PLUS$ + OF_S$
390 C_ST$ = LEFT$(WZ_SITE$(I%) + BLANKS$, 4%) \ C_LC$ = LEFT$(WZ_LOC$(I%) + BLANKS$, 28%)
391 C_OF$ = LEFT$("UTC" + OF_S$ + BLANKS$, 10%)
392 PRINT C_ST$; " | "; C_LC$; " | "; C_OF$; " | "; Z_HS$; COLON$; Z_MS$
394 I% = I% + 1% \ GOTO 382
396 PRINT "Total world sites: "; NUM_WZ% \ GOTO 44
400 REM --- ADDZONE <site|location|utc_offset> ---
402 P1% = INSTR(1%, ARG$, PIPE$)
403 IF P1% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: ADDZONE <site|location|utc_offset>"
404 IF P1% = 0% THEN GOTO 44
406 Z_S$ = LEFT$(ARG$, P1% - 1%) \ R1$ = MID$(ARG$, P1% + 1%, LEN(ARG$) - P1%)
408 P2% = INSTR(1%, R1$, PIPE$)
409 IF P2% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: ADDZONE <site|location|utc_offset>"
410 IF P2% = 0% THEN GOTO 44
412 Z_L$ = LEFT$(R1$, P2% - 1%) \ Z_O% = VAL(MID$(R1$, P2% + 1%, LEN(R1$) - P2%))
414 NUM_WZ% = NUM_WZ% + 1% \ WZ_SITE$(NUM_WZ%) = Z_S$ \ WZ_LOC$(NUM_WZ%) = Z_L$ \ WZ_OFF%(NUM_WZ%) = Z_O%
416 PRINT "[Added World Clock Site #"; NUM_WZ%; ": "; Z_S$; " ("; Z_L$; ", UTC "; Z_O%; ")]" \ GOTO 44
425 REM --- DIAL / ANALOG ---
426 OUT_FILE$ = "" \ GOSUB 570 \ GOTO 44
440 REM --- DISPLAY [ON <file>] / SCREEN / RENDER / EXPORT ---
441 OUT_FILE$ = "" \ S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
442 IF VERB$ = "EXPORT" THEN OUT_FILE$ = ARG$
443 IF LEFT$(UARG$, 3%) = "ON " THEN OUT_FILE$ = MID$(ARG$, 4%, LEN(ARG$) - 3%)
444 S_IN$ = OUT_FILE$ \ GOSUB 500 \ OUT_FILE$ = S_OUT$
446 GOSUB 600
448 IF OUT_FILE$ <> "" THEN PRINT "[Clock window exported to "; OUT_FILE$; "]"
450 GOTO 44
455 REM --- SAVE <file> ---
456 IF ARG$ = "" THEN PRINT "%CLOCK-E-NOFILE, Specify filename for SAVE."
457 IF ARG$ = "" THEN GOTO 44
458 OPEN ARG$ FOR OUTPUT AS FILE #1%
459 S_IN$ = STR$(CLK_HR%) \ GOSUB 500 \ H_S$ = S_OUT$ \ S_IN$ = STR$(CLK_MN%) \ GOSUB 500 \ M_S$ = S_OUT$
460 S_REC$ = "CLK" + PIPE$ + H_S$ + PIPE$ + M_S$ + PIPE$ + CLK_DATE$ + PIPE$ + FACE_MODE$
461 PRINT #1%, S_REC$
462 S_IN$ = STR$(ALM_ON%) \ GOSUB 500 \ AO_S$ = S_OUT$ \ S_IN$ = STR$(ALM_HR%) \ GOSUB 500 \ AH_S$ = S_OUT$ \ S_IN$ = STR$(ALM_MN%) \ GOSUB 500 \ AM_S$ = S_OUT$
464 S_REC$ = "ALM" + PIPE$ + AO_S$ + PIPE$ + AH_S$ + PIPE$ + AM_S$ + PIPE$ + ALM_MSG$
466 PRINT #1%, S_REC$ \ CLOSE #1%
470 PRINT "[Saved DECwindows Clock configuration to "; ARG$; "]" \ GOTO 44
472 REM --- LOAD <file> ---
473 IF ARG$ = "" THEN PRINT "%CLOCK-E-NOFILE, Specify filename for LOAD."
474 IF ARG$ = "" THEN GOTO 44
475 OPEN ARG$ FOR INPUT AS FILE #1%
477 LINE INPUT #1%, L_REC$
478 IF LEN(L_REC$) = 0% THEN GOTO 487
479 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 487
480 S_IN$ = L_REC$ \ GOSUB 500 \ L_REC$ = S_OUT$
482 IF LEFT$(L_REC$, 4%) = "CLK|" THEN GOSUB 660
484 IF LEFT$(L_REC$, 4%) = "ALM|" THEN GOSUB 680
485 GOTO 477
487 CLOSE #1% \ GOSUB 540
488 PRINT "[Loaded DECwindows Clock configuration from "; ARG$; " (Time: "; TIME_STR$; ")]" \ GOTO 44
490 REM --- CLEAR / RESET ---
492 CLK_HR% = 0% \ CLK_MN% = 0% \ CLK_SC% = 0% \ ALM_ON% = 0%
494 PRINT "[Clock reset to 00:00:00 and alarm cleared]" \ GOTO 44
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
535 REM --- Subroutine: Format 2-digit integer (FMT_N% -> FMT_S$) ---
536 S_IN$ = STR$(FMT_N%) \ GOSUB 500 \ FMT_S$ = S_OUT$
537 IF FMT_N% < 10% THEN FMT_S$ = ZERO$ + FMT_S$
538 RETURN
540 REM --- Subroutine: Build TIME_STR$ according to MIL_MODE% ---
541 D_HR% = CLK_HR% \ AMPM$ = ""
542 IF MIL_MODE% = 0% AND CLK_HR% < 12% THEN AMPM$ = " AM"
543 IF MIL_MODE% = 0% AND CLK_HR% >= 12% THEN AMPM$ = " PM"
544 IF MIL_MODE% = 0% AND D_HR% > 12% THEN D_HR% = D_HR% - 12%
545 IF MIL_MODE% = 0% AND D_HR% = 0% THEN D_HR% = 12%
546 FMT_N% = D_HR% \ GOSUB 535 \ H_STR$ = FMT_S$
548 FMT_N% = CLK_MN% \ GOSUB 535 \ M_STR$ = FMT_S$
550 FMT_N% = CLK_SC% \ GOSUB 535 \ S_STR$ = FMT_S$
552 TIME_STR$ = H_STR$ + COLON$ + M_STR$ + COLON$ + S_STR$ + AMPM$
554 RETURN
560 REM --- Subroutine: Build ALM_STR$ ---
562 FMT_N% = ALM_HR% \ GOSUB 535 \ AH_STR$ = FMT_S$
564 FMT_N% = ALM_MN% \ GOSUB 535 \ AM_STR$ = FMT_S$
566 ALM_STR$ = AH_STR$ + COLON$ + AM_STR$
568 RETURN
570 REM --- Subroutine: Render Analog Dial Lines ---
572 GOSUB 540 \ H12% = CLK_HR%
574 IF H12% >= 12% THEN H12% = H12% - 12%
575 IF H12% = 0% THEN H12% = 12%
576 FMT_N% = H12% \ GOSUB 535 \ H12_S$ = FMT_S$
578 FMT_N% = CLK_MN% \ GOSUB 535 \ M60_S$ = FMT_S$
580 PRINT "        . - ~ ~ ~ - ."
582 PRINT "    . '      12       ' ."
584 PRINT "  .     11   |    1       ."
586 PRINT " .    10     |      2      ."
588 PRINT ".   9 -------O------- 3     .   Analog Hands : Hour->"; H12_S$; "  Min->"; M60_S$
590 PRINT " .     8     |      4      .    Digital Time : "; TIME_STR$
592 PRINT "  .      7   |    5       .     Date Banner  : "; CLK_DATE$
594 PRINT "    . .      6        . '"
596 PRINT "        ' - . _ . - '"
598 RETURN
600 REM --- Subroutine: Render Motif/XUI Clock Window ---
602 IF OUT_FILE$ <> "" THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #3%
603 B_L$ = "| " \ B_R$ = " |" \ W_BTN$ = " [v][^] |" \ W_DT$ = " | Date: " \ W_AL$ = " | Alarm: "
604 L1$ = "+----------------------------------------------------------------------------+"
606 W_T$ = LEFT$(CLK_DATE$ + SP1$ + LBRK$ + FACE_MODE$ + RBRK$ + BLANKS$, 40%)
608 L2$ = "| [=] DECwindows Clock (dxclock) - " + W_T$ + W_BTN$
610 L3$ = "| File  Settings  Alarm  World-Zones  Help                                   |"
612 GOSUB 540 \ GOSUB 560
614 W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = L2$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
616 W_LN$ = L3$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
618 W_LN$ = "|                     . - ~ ~ ~ - .                                          |" \ GOSUB 650
620 W_LN$ = "|                 . '      12       ' .                                      |" \ GOSUB 650
622 W_LN$ = "|               .     11   |    1       .                                    |" \ GOSUB 650
624 W_LN$ = "|              .    10     O------2      .                                   |" \ GOSUB 650
626 W_LN$ = "|              .   9               3     .                                   |" \ GOSUB 650
628 W_LN$ = "|               .     8          4      .                                    |" \ GOSUB 650
630 W_LN$ = "|                 . .      6        . '                                      |" \ GOSUB 650
632 W_LN$ = "|                     ' - . _ . - '                                          |" \ GOSUB 650
634 W_LN$ = L1$ \ GOSUB 650
636 PAD_OUT$ = LEFT$("Digital Readout: " + TIME_STR$ + W_DT$ + CLK_DATE$ + W_AL$ + ALM_STR$ + BLANKS$, 74%)
638 W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
640 PAD_OUT$ = LEFT$("Alarm Msg: " + ALM_MSG$ + SP1$ + PIPE$ + SP1$ + CLK_TZ$ + BLANKS$, 74%)
642 W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
644 IF OUT_FILE$ <> "" THEN CLOSE #3%
646 RETURN
650 IF OUT_FILE$ = "" THEN PRINT W_LN$
652 IF OUT_FILE$ <> "" THEN PRINT #3%, W_LN$
654 RETURN
660 REM --- Subroutine: Parse CLK|hr|mn|date|face ---
662 H_R$ = MID$(L_REC$, 5%, LEN(L_REC$) - 4%) \ H1% = INSTR(1%, H_R$, PIPE$)
663 IF H1% = 0% THEN GOTO 674
664 CLK_HR% = VAL(LEFT$(H_R$, H1% - 1%)) \ H_R$ = MID$(H_R$, H1% + 1%, LEN(H_R$) - H1%) \ H2% = INSTR(1%, H_R$, PIPE$)
666 IF H2% = 0% THEN GOTO 674
668 CLK_MN% = VAL(LEFT$(H_R$, H2% - 1%)) \ H_R$ = MID$(H_R$, H2% + 1%, LEN(H_R$) - H2%) \ H3% = INSTR(1%, H_R$, PIPE$)
670 IF H3% = 0% THEN GOTO 674
672 CLK_DATE$ = LEFT$(H_R$, H3% - 1%) \ FACE_MODE$ = MID$(H_R$, H3% + 1%, LEN(H_R$) - H3%)
674 RETURN
680 REM --- Subroutine: Parse ALM|on|hr|mn|msg ---
682 G_R$ = MID$(L_REC$, 5%, LEN(L_REC$) - 4%) \ G1% = INSTR(1%, G_R$, PIPE$)
683 IF G1% = 0% THEN GOTO 694
684 ALM_ON% = VAL(LEFT$(G_R$, G1% - 1%)) \ G_R$ = MID$(G_R$, G1% + 1%, LEN(G_R$) - G1%) \ G2% = INSTR(1%, G_R$, PIPE$)
686 IF G2% = 0% THEN GOTO 694
688 ALM_HR% = VAL(LEFT$(G_R$, G2% - 1%)) \ G_R$ = MID$(G_R$, G2% + 1%, LEN(G_R$) - G2%) \ G3% = INSTR(1%, G_R$, PIPE$)
690 IF G3% = 0% THEN GOTO 694
692 ALM_MN% = VAL(LEFT$(G_R$, G3% - 1%)) \ ALM_MSG$ = MID$(G_R$, G3% + 1%, LEN(G_R$) - G3%)
694 RETURN
990 PRINT "DECwindows Clock V3.0 session terminated."
999 END
