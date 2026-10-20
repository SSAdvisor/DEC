10 REM =================================================================
12 REM DECwindows Clock V3.0 (DECW$CLOCK / dxclock)
14 REM Digital Equipment Corporation VAX/VMS, ULTRIX & OSF/1 (1988-1995)
16 REM Sub-Project 7 of 11 in DECwindows Faithful BASIC-PLUS-2 Port
18 REM =================================================================
20 DIM WZ_SITE$(12%) \ DIM WZ_LOC$(12%) \ DIM WZ_OFF%(12%)
22 CLK_HR% = 14% \ CLK_MN% = 30% \ CLK_SC% = 0%
24 CLK_DATE$ = "TUE 19-OCT-1993" \ CLK_TZ$ = "EST (UTC-5 Maynard MLO)"
25 FACE_MODE$ = "BOTH" \ MIL_MODE% = 1% \ CHIME_ON% = 1%
26 ANALOG_ON% = 1% \ DIGITAL_ON% = 1% \ DATE_ON% = 1% \ MENUBAR_ON% = 1%
27 ALM_ON% = 0% \ ALM_RPT% = 1% \ ALM_BELL% = 1%
28 ALM_HR% = 15% \ ALM_MN% = 0% \ ALM_MSG$ = "No Alarm Set"
29 PIPE$ = "|" \ SEMI$ = ";" \ COLON$ = ":" \ SP1$ = " " \ ZERO$ = "0"
30 LBRK$ = "[" \ RBRK$ = "]" \ PLUS$ = "+" \ MINUS$ = "-" \ CTR_O$ = "O"
31 BLANKS$ = "                                                                                "
32 NUM_WZ% = 0% \ IS_BATCH% = 0% \ FORCE_CLI% = 0% \ HAS_STATE% = 0%
33 S_IN$ = COMMAND$ \ GOSUB 500 \ CMD_INIT$ = S_OUT$
34 IF LEFT$(CMD_INIT$, 5%) = "--cli" THEN FORCE_CLI% = 1%
35 IF FORCE_CLI% = 1% THEN S_IN$ = MID$(CMD_INIT$, 6%, LEN(CMD_INIT$) - 5%)
36 IF FORCE_CLI% = 1% THEN GOSUB 500
37 IF FORCE_CLI% = 1% THEN CMD_INIT$ = S_OUT$
38 IF CMD_INIT$ = "--x11" OR CMD_INIT$ = "-gui" THEN CMD_INIT$ = "X11; EXIT"
39 IF_X11% = 1% \ CHK_X11$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --check-gui"
40 IF CMD_INIT$ = "" AND FORCE_CLI% = 0% THEN IF_X11% = SYS(CHK_X11$)
41 IF IF_X11% = 0% THEN CMD_INIT$ = "X11; EXIT"
42 IF CMD_INIT$ <> "" THEN IS_BATCH% = 1%
43 IF CMD_INIT$ <> "" THEN REM_CHAIN$ = CMD_INIT$
44 IF CMD_INIT$ <> "" THEN GOTO 54
45 PRINT "======================================================================" \ PRINT " DECwindows Clock V3.0 (DECW$CLOCK / dxclock)" \ PRINT " Digital Equipment Corporation - Desktop Analog/Digital Timekeeper" \ PRINT " Type HELP for commands, SAMPLE for Maynard/Nashua clock demo, EXIT." \ PRINT "" \ REM_CHAIN$ = ""
46 IF REM_CHAIN$ <> "" THEN GOTO 54
47 IF IS_BATCH% = 1% THEN GOTO 990
48 PRINT "CLOCK> "; \ LINE INPUT RAW_IN$
49 IF LEN(RAW_IN$) = 0% THEN GOTO 990
50 IF ASCII(LEFT$(RAW_IN$, 1%)) = 26% THEN GOTO 990
51 IF ASCII(LEFT$(RAW_IN$, 1%)) = 0% THEN GOTO 990
52 REM_CHAIN$ = RAW_IN$
54 SC_POS% = INSTR(1%, REM_CHAIN$, SEMI$)
56 IF SC_POS% = 0% THEN CMD_LINE$ = REM_CHAIN$
58 IF SC_POS% = 0% THEN REM_CHAIN$ = ""
60 IF SC_POS% > 0% THEN CMD_LINE$ = LEFT$(REM_CHAIN$, SC_POS% - 1%)
62 IF SC_POS% > 0% THEN REM_CHAIN$ = MID$(REM_CHAIN$, SC_POS% + 1%, LEN(REM_CHAIN$) - SC_POS%)
64 S_IN$ = CMD_LINE$ \ GOSUB 500 \ CMD_LINE$ = S_OUT$
66 IF CMD_LINE$ = "" THEN GOTO 46
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
110 IF VERB$ = "CHIME" THEN GOTO 320
111 IF VERB$ = "BELL" THEN GOTO 327
112 IF VERB$ = "REPEAT" THEN GOTO 333
113 IF VERB$ = "FORMAT" THEN GOTO 340
114 IF VERB$ = "MILITARY" THEN GOTO 340
115 IF VERB$ = "FACE" THEN GOTO 350
116 IF VERB$ = "MODE" THEN GOTO 350
117 IF VERB$ = "DIGITAL" THEN GOTO 360
118 IF VERB$ = "DATEPART" THEN GOTO 360
119 IF VERB$ = "MENUBAR" THEN GOTO 360
120 IF VERB$ = "ZONES" THEN GOTO 376
121 IF VERB$ = "WORLD" THEN GOTO 376
122 IF VERB$ = "SITES" THEN GOTO 376
124 IF VERB$ = "ADDZONE" THEN GOTO 400
126 IF VERB$ = "DIAL" THEN GOTO 428
128 IF VERB$ = "ANALOG" THEN GOTO 420
130 IF VERB$ = "DISPLAY" THEN GOTO 441
132 IF VERB$ = "SCREEN" THEN GOTO 441
134 IF VERB$ = "RENDER" THEN GOTO 441
136 IF VERB$ = "OPTIONS" THEN GOTO 432
138 IF VERB$ = "DIALOG" THEN GOTO 432
140 IF VERB$ <> "HELP" THEN GOTO 157
141 PRINT "--- DECwindows Clock V3.0 Commands ---"
142 PRINT "  SAMPLE / DEMO                        : Load Maynard MLO clock & world zones"
143 PRINT "  SETTIME <HH:MM[:SS]> / TIME          : Set workstation clock time"
144 PRINT "  SETDATE <date> / DATE                : Set workstation date banner"
145 PRINT "  TICK [mins] / ADVANCE [mins]         : Advance clock and test alarm/chime"
146 PRINT "  ALARM <ON|OFF|HH:MM|message>         : Configure Options -> Alarm... settings"
147 PRINT "  REPEAT <ON|OFF> / BELL <ON|OFF>      : Toggle alarm daily repeat & bell"
148 PRINT "  ANALOG <ON|OFF> / DIGITAL <ON|OFF>   : Toggle Display... Analog & Digital parts"
149 PRINT "  DATEPART <ON|OFF> / MENUBAR <ON|OFF> : Toggle Display... Date part & Menubar"
150 PRINT "  MILITARY <ON|OFF> / FORMAT <12|24>   : Toggle 12-hour AM/PM vs 24-hour time"
151 PRINT "  FACE <ANALOG|DIGITAL|BOTH>           : Select clock face presentation preset"
152 PRINT "  OPTIONS [DISPLAY|ALARM] / RESTORE    : Show Display/Alarm dialog or defaults"
153 PRINT "  ZONES / WORLD / ADDZONE <c|loc|off>  : View or add DEC world timezones"
154 PRINT "  DIAL / DISPLAY [ON <f>] / EXPORT <f> : Render dial or Motif Clock window"
155 PRINT "  SHOW / SAVE <f> / LOAD <f> / X11     : Status, save/load options, launch X11"
156 GOTO 46
157 IF VERB$ = "EXPORT" THEN GOTO 441
158 IF VERB$ = "PRINT" THEN GOTO 441
159 IF VERB$ = "SAVE" THEN GOTO 458
160 IF VERB$ = "LOAD" THEN GOTO 472
161 IF VERB$ = "CLEAR" THEN GOTO 490
162 IF VERB$ = "RESET" THEN GOTO 490
163 IF VERB$ = "RESTORE" THEN GOTO 488
165 IF VERB$ = "X11" OR VERB$ = "GUI" OR VERB$ = "XDISPLAY" THEN GOTO 495
166 PRINT "%CLOCK-E-INVCMD, Unrecognized command: "; VERB$
168 GOTO 46
170 REM --- SAMPLE / DEMO ---
172 CLK_HR% = 14% \ CLK_MN% = 30% \ CLK_SC% = 0% \ HAS_STATE% = 1%
174 CLK_DATE$ = "TUE 19-OCT-1993" \ CLK_TZ$ = "EST (UTC-5 Maynard MLO / Nashua ZKO)"
176 FACE_MODE$ = "BOTH" \ MIL_MODE% = 1% \ CHIME_ON% = 1%
177 ANALOG_ON% = 1% \ DIGITAL_ON% = 1% \ DATE_ON% = 1% \ MENUBAR_ON% = 1%
178 ALM_ON% = 1% \ ALM_RPT% = 1% \ ALM_BELL% = 1%
179 ALM_HR% = 15% \ ALM_MN% = 0% \ ALM_MSG$ = "VAXcluster Quorum & Backup Window"
180 NUM_WZ% = 6%
181 WZ_SITE$(1%) = "MLO" \ WZ_LOC$(1%) = "Maynard Mill, MA (HQ)" \ WZ_OFF%(1%) = 0% - 5%
182 WZ_SITE$(2%) = "ZKO" \ WZ_LOC$(2%) = "Nashua Spit Brook, NH" \ WZ_OFF%(2%) = 0% - 5%
183 WZ_SITE$(3%) = "SRC" \ WZ_LOC$(3%) = "Palo Alto Systems Research" \ WZ_OFF%(3%) = 0% - 8%
184 WZ_SITE$(4%) = "REO" \ WZ_LOC$(4%) = "Reading Engineering, UK" \ WZ_OFF%(4%) = 0%
185 WZ_SITE$(5%) = "VBO" \ WZ_LOC$(5%) = "Valbonne Centre Technique" \ WZ_OFF%(5%) = 1%
186 WZ_SITE$(6%) = "TKO" \ WZ_LOC$(6%) = "Tokyo Engineering Center" \ WZ_OFF%(6%) = 9%
188 GOSUB 540
190 PRINT "[Loaded Sample DECwindows Clock: "; TIME_STR$; " on "; CLK_DATE$; " (6 DEC World Sites)]"
192 GOTO 46
200 REM --- SHOW / STATUS ---
202 GOSUB 540 \ GOSUB 560 \ GOSUB 565
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
217 PRINT "  Display Parts  : Analog="; AN_S$; " Digital="; DG_S$; " Date="; DT_S$; " Menubar="; MB_S$
218 PRINT "  Alarm Status   : "; AL_ST$; " @ "; ALM_STR$; " - "; ALM_MSG$; " (Repeat="; RP_S$; " Bell="; BL_S$; ")"
220 PRINT "  World Sites    : "; NUM_WZ%; " DEC engineering locations"
222 GOTO 46
225 REM --- SETTIME <HH:MM[:SS]> / TIME ---
226 IF ARG$ = "" THEN GOSUB 540
227 IF ARG$ = "" THEN PRINT "Current Time: "; TIME_STR$; " ("; CLK_DATE$; ")"
228 IF ARG$ = "" THEN GOTO 46
230 C1% = INSTR(1%, ARG$, COLON$)
232 IF C1% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: SETTIME <HH:MM[:SS]>"
233 IF C1% = 0% THEN GOTO 46
234 N_H% = VAL(LEFT$(ARG$, C1% - 1%)) \ R_T$ = MID$(ARG$, C1% + 1%, LEN(ARG$) - C1%)
236 C2% = INSTR(1%, R_T$, COLON$)
237 IF C2% = 0% THEN N_M% = VAL(R_T$)
238 IF C2% = 0% THEN N_S% = 0%
239 IF C2% > 0% THEN N_M% = VAL(LEFT$(R_T$, C2% - 1%))
240 IF C2% > 0% THEN N_S% = VAL(MID$(R_T$, C2% + 1%, LEN(R_T$) - C2%))
241 IF N_H% < 0% OR N_H% > 23% THEN PRINT "%CLOCK-E-INVTIME, Hour must be 0..23."
242 IF N_H% < 0% OR N_H% > 23% THEN GOTO 46
243 IF N_M% < 0% OR N_M% > 59% THEN PRINT "%CLOCK-E-INVTIME, Minute must be 0..59."
244 IF N_M% < 0% OR N_M% > 59% THEN GOTO 46
245 CLK_HR% = N_H% \ CLK_MN% = N_M% \ CLK_SC% = N_S% \ HAS_STATE% = 1% \ GOSUB 540
246 PRINT "[Workstation Clock set to "; TIME_STR$; "]" \ GOTO 46
250 REM --- SETDATE <date> / DATE ---
252 IF ARG$ <> "" THEN CLK_DATE$ = ARG$
253 IF ARG$ <> "" THEN HAS_STATE% = 1%
254 PRINT "[Workstation Date Banner: "; CLK_DATE$; "]" \ GOTO 46
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
281 IF ALM_ON% = 1% AND CLK_HR% = ALM_HR% AND CLK_MN% = ALM_MN% AND ALM_RPT% = 0% THEN ALM_ON% = 0%
282 STEP_I% = STEP_I% + 1% \ GOTO 270
284 HAS_STATE% = 1% \ GOSUB 540 \ PRINT "[Clock advanced "; ADV_M%; " min(s) -> "; TIME_STR$; "]" \ GOTO 46
290 REM --- ALARM <ON|OFF|HH:MM|msg> ---
292 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$ \ HAS_STATE% = 1%
294 IF UARG$ = "ON" THEN ALM_ON% = 1%
295 IF UARG$ = "ON" THEN PRINT "[Alarm Bell ENABLED]"
296 IF UARG$ = "ON" THEN GOTO 46
298 IF UARG$ = "OFF" THEN ALM_ON% = 0%
299 IF UARG$ = "OFF" THEN PRINT "[Alarm Bell DISABLED]"
300 IF UARG$ = "OFF" THEN GOTO 46
302 P1% = INSTR(1%, ARG$, PIPE$)
304 IF P1% = 0% THEN T_PART$ = ARG$
305 IF P1% > 0% THEN T_PART$ = LEFT$(ARG$, P1% - 1%)
306 IF P1% > 0% THEN ALM_MSG$ = MID$(ARG$, P1% + 1%, LEN(ARG$) - P1%)
308 C1% = INSTR(1%, T_PART$, COLON$)
310 IF C1% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: ALARM <ON|OFF|HH:MM|message>"
311 IF C1% = 0% THEN GOTO 46
312 ALM_HR% = VAL(LEFT$(T_PART$, C1% - 1%)) \ ALM_MN% = VAL(MID$(T_PART$, C1% + 1%, LEN(T_PART$) - C1%))
314 ALM_ON% = 1% \ GOSUB 560
316 PRINT "[Alarm Set for "; ALM_STR$; " (ENABLED) : "; ALM_MSG$; "]" \ GOTO 46
320 REM --- CHIME <ON|OFF> ---
321 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$ \ HAS_STATE% = 1%
322 IF UARG$ = "ON" THEN CHIME_ON% = 1%
323 IF UARG$ = "OFF" THEN CHIME_ON% = 0%
325 PRINT "[Hourly Chime set to: "; UARG$; "]" \ GOTO 46
327 REM --- BELL <ON|OFF> ---
328 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$ \ HAS_STATE% = 1%
329 IF UARG$ = "ON" THEN ALM_BELL% = 1%
330 IF UARG$ = "OFF" THEN ALM_BELL% = 0%
331 PRINT "[Alarm Bell set to: "; UARG$; "]" \ GOTO 46
333 REM --- REPEAT <ON|OFF> ---
334 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$ \ HAS_STATE% = 1%
335 IF UARG$ = "ON" THEN ALM_RPT% = 1%
336 IF UARG$ = "OFF" THEN ALM_RPT% = 0%
337 PRINT "[Alarm Repeat set to: "; UARG$; "]" \ GOTO 46
340 REM --- FORMAT <12|24> / MILITARY <ON|OFF> ---
341 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$ \ HAS_STATE% = 1% \ F_LBL$ = ARG$
342 IF UARG$ = "12" OR UARG$ = "OFF" THEN MIL_MODE% = 0%
343 IF UARG$ = "12" OR UARG$ = "OFF" THEN F_LBL$ = "12"
344 IF UARG$ = "24" OR UARG$ = "ON" THEN MIL_MODE% = 1%
345 IF UARG$ = "24" OR UARG$ = "ON" THEN F_LBL$ = "24"
346 GOSUB 540 \ PRINT "[Clock Digital Format set to "; F_LBL$; "-Hour -> "; TIME_STR$; "]" \ GOTO 46
350 REM --- FACE <ANALOG|DIGITAL|BOTH> / MODE ---
351 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$ \ HAS_STATE% = 1%
352 IF UARG$ <> "" THEN FACE_MODE$ = UARG$
353 IF FACE_MODE$ = "ANALOG" THEN ANALOG_ON% = 1%
354 IF FACE_MODE$ = "ANALOG" THEN DIGITAL_ON% = 0%
355 IF FACE_MODE$ = "DIGITAL" THEN ANALOG_ON% = 0%
356 IF FACE_MODE$ = "DIGITAL" THEN DIGITAL_ON% = 1%
357 IF FACE_MODE$ = "BOTH" THEN ANALOG_ON% = 1%
358 IF FACE_MODE$ = "BOTH" THEN DIGITAL_ON% = 1%
359 PRINT "[Clock Face Mode set to: "; FACE_MODE$; "]" \ GOTO 46
360 REM --- DIGITAL / DATEPART / MENUBAR <ON|OFF> ---
361 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$ \ HAS_STATE% = 1%
362 IF VERB$ = "DIGITAL" AND UARG$ = "ON" THEN DIGITAL_ON% = 1%
363 IF VERB$ = "DIGITAL" AND UARG$ = "OFF" THEN DIGITAL_ON% = 0%
364 IF VERB$ = "DIGITAL" THEN GOSUB 565
365 IF VERB$ = "DIGITAL" THEN PRINT "[Display Options: Digital Part set to "; DG_S$; "]"
366 IF VERB$ = "DIGITAL" THEN GOTO 46
367 IF VERB$ = "DATEPART" AND UARG$ = "ON" THEN DATE_ON% = 1%
368 IF VERB$ = "DATEPART" AND UARG$ = "OFF" THEN DATE_ON% = 0%
369 IF VERB$ = "DATEPART" THEN GOSUB 565
370 IF VERB$ = "DATEPART" THEN PRINT "[Display Options: Date Part set to "; DT_S$; "]"
371 IF VERB$ = "DATEPART" THEN GOTO 46
373 IF UARG$ = "ON" THEN MENUBAR_ON% = 1%
374 IF UARG$ = "OFF" THEN MENUBAR_ON% = 0%
375 GOSUB 565 \ PRINT "[Display Options: Menubar set to "; MB_S$; "]" \ GOTO 46
376 PRINT "=== DEC Worldwide Engineering Timezones (Base: Maynard MLO UTC-5) ==="
377 PRINT "Site | Location                     | UTC Offset | Local Time"
378 PRINT "-----+------------------------------+------------+------------"
379 UTC_HR% = CLK_HR% + 5%
380 IF UTC_HR% >= 24% THEN UTC_HR% = UTC_HR% - 24%
381 I% = 1%
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
396 PRINT "Total world sites: "; NUM_WZ% \ GOTO 46
400 REM --- ADDZONE <site|location|utc_offset> ---
402 P1% = INSTR(1%, ARG$, PIPE$)
403 IF P1% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: ADDZONE <site|location|utc_offset>"
404 IF P1% = 0% THEN GOTO 46
406 Z_S$ = LEFT$(ARG$, P1% - 1%) \ R1$ = MID$(ARG$, P1% + 1%, LEN(ARG$) - P1%)
408 P2% = INSTR(1%, R1$, PIPE$)
409 IF P2% = 0% THEN PRINT "%CLOCK-E-SYNTAX, Usage: ADDZONE <site|location|utc_offset>"
410 IF P2% = 0% THEN GOTO 46
412 Z_L$ = LEFT$(R1$, P2% - 1%) \ Z_O% = VAL(MID$(R1$, P2% + 1%, LEN(R1$) - P2%))
414 NUM_WZ% = NUM_WZ% + 1% \ WZ_SITE$(NUM_WZ%) = Z_S$ \ WZ_LOC$(NUM_WZ%) = Z_L$ \ WZ_OFF%(NUM_WZ%) = Z_O%
416 PRINT "[Added World Clock Site #"; NUM_WZ%; ": "; Z_S$; " ("; Z_L$; ", UTC "; Z_O%; ")]" \ GOTO 46
420 REM --- ANALOG [ON|OFF] ---
421 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
422 IF UARG$ = "ON" THEN ANALOG_ON% = 1%
423 IF UARG$ = "OFF" THEN ANALOG_ON% = 0%
424 IF UARG$ = "ON" OR UARG$ = "OFF" THEN HAS_STATE% = 1%
425 IF UARG$ = "ON" OR UARG$ = "OFF" THEN GOSUB 565
426 IF UARG$ = "ON" OR UARG$ = "OFF" THEN PRINT "[Display Options: Analog Part set to "; AN_S$; "]"
427 IF UARG$ = "ON" OR UARG$ = "OFF" THEN GOTO 46
428 OUT_FILE$ = "" \ GOSUB 583 \ GOTO 46
432 REM --- OPTIONS / DIALOG [DISPLAY|ALARM] ---
433 S_IN$ = ARG$ \ GOSUB 520 \ DLG_MODE$ = S_OUT$
434 IF DLG_MODE$ = "" THEN DLG_MODE$ = "DISPLAY"
435 GOSUB 540 \ GOSUB 560 \ GOSUB 565
436 PRINT "+----------------------------------------------------------+"
437 IF DLG_MODE$ = "ALARM" THEN PRINT "| [=] Clock: Alarm Options Dialog                          |"
438 IF DLG_MODE$ <> "ALARM" THEN PRINT "| [=] Clock: Display Options Dialog                        |"
439 PRINT "+----------------------------------------------------------+"
440 GOTO 451
441 OUT_FILE$ = "" \ S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
442 IF VERB$ = "EXPORT" THEN OUT_FILE$ = ARG$
443 IF LEFT$(UARG$, 3%) = "ON " THEN OUT_FILE$ = MID$(ARG$, 4%, LEN(ARG$) - 3%)
444 S_IN$ = OUT_FILE$ \ GOSUB 500 \ OUT_FILE$ = S_OUT$
446 GOSUB 609
448 IF OUT_FILE$ <> "" THEN PRINT "[Clock window exported to "; OUT_FILE$; "]"
450 GOTO 46
451 IF DLG_MODE$ <> "ALARM" THEN PRINT "|  ["; AN_X$; "] Analog Part      ["; MB_X$; "] Menubar                    |"
452 IF DLG_MODE$ <> "ALARM" THEN PRINT "|  ["; DG_X$; "] Digital Part     ["; ML_X$; "] Military Time (24-Hour)    |"
453 IF DLG_MODE$ <> "ALARM" THEN PRINT "|  ["; DT_X$; "] Date Part                                       |"
454 IF DLG_MODE$ = "ALARM" THEN PRINT "|  ["; AL_X$; "] Alarm On   ["; RP_X$; "] Repeat   ["; BL_X$; "] Bell             |"
455 DLG_M$ = LEFT$(ALM_MSG$ + BLANKS$, 24%)
456 IF DLG_MODE$ = "ALARM" THEN PRINT "|  Alarm Time: "; ALM_STR$; "  Message: "; DLG_M$; " |"
457 PRINT "|            [ OK ]       [ Apply ]       [ Cancel ]       |" \ PRINT "+----------------------------------------------------------+" \ GOTO 46
458 IF ARG$ = "" THEN PRINT "%CLOCK-E-NOFILE, Specify filename for SAVE."
459 IF ARG$ = "" THEN GOTO 46
460 SAVE_PATH$ = ARG$ \ GOSUB 700
462 PRINT "[Saved DECwindows Clock configuration to "; ARG$; "]" \ GOTO 46
472 REM --- LOAD <file> ---
473 IF ARG$ = "" THEN PRINT "%CLOCK-E-NOFILE, Specify filename for LOAD."
474 IF ARG$ = "" THEN GOTO 46
475 OPEN ARG$ FOR INPUT AS FILE #1%
477 LINE INPUT #1%, L_REC$
478 IF LEN(L_REC$) = 0% THEN GOTO 486
479 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 486
480 S_IN$ = L_REC$ \ GOSUB 500 \ L_REC$ = S_OUT$
482 IF LEFT$(L_REC$, 4%) = "CLK|" THEN GOSUB 660
483 IF LEFT$(L_REC$, 4%) = "ALM|" THEN GOSUB 680
484 IF LEFT$(L_REC$, 4%) = "OPT|" THEN GOSUB 720
485 GOTO 477
486 CLOSE #1% \ HAS_STATE% = 1% \ GOSUB 540
487 PRINT "[Loaded DECwindows Clock configuration from "; ARG$; " (Time: "; TIME_STR$; ")]" \ GOTO 46
488 REM --- RESTORE (Restore System Options) ---
489 ANALOG_ON% = 1% \ DIGITAL_ON% = 1% \ DATE_ON% = 1% \ MENUBAR_ON% = 1% \ MIL_MODE% = 0% \ FACE_MODE$ = "BOTH" \ ALM_ON% = 0% \ GOSUB 540 \ PRINT "[Restored DECwindows Clock System Options (Analog+Digital+Date, 12-Hour)]" \ GOTO 46
490 REM --- CLEAR / RESET ---
492 CLK_HR% = 0% \ CLK_MN% = 0% \ CLK_SC% = 0% \ ALM_ON% = 0%
494 PRINT "[Clock reset to 00:00:00 and alarm cleared]" \ GOTO 46
495 OUT_FILE$ = "/tmp/decw_clock.txt" \ GOSUB 609 \ SAVE_PATH$ = "/tmp/decw_clock.dat"
496 IF HAS_STATE% = 1% THEN GOSUB 700
497 X_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app clock --frame /tmp/decw_clock.txt"
498 IF HAS_STATE% = 1% THEN X_CMD$ = X_CMD$ + " --state /tmp/decw_clock.dat"
499 X_RC% = SYS(X_CMD$) \ GOTO 46
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
561 FMT_N% = ALM_HR% \ GOSUB 535 \ AH_STR$ = FMT_S$
562 FMT_N% = ALM_MN% \ GOSUB 535 \ AM_STR$ = FMT_S$
563 ALM_STR$ = AH_STR$ + COLON$ + AM_STR$
564 RETURN
565 REM --- Subroutine: Build Display & Alarm Option Status Strings ---
566 AN_S$ = "OFF" \ AN_X$ = " " \ DG_S$ = "OFF" \ DG_X$ = " " \ DT_S$ = "OFF" \ DT_X$ = " " \ MB_S$ = "OFF" \ MB_X$ = " "
567 IF ANALOG_ON% = 1% THEN AN_S$ = "ON"
568 IF ANALOG_ON% = 1% THEN AN_X$ = "X"
569 IF DIGITAL_ON% = 1% THEN DG_S$ = "ON"
570 IF DIGITAL_ON% = 1% THEN DG_X$ = "X"
571 IF DATE_ON% = 1% THEN DT_S$ = "ON"
572 IF DATE_ON% = 1% THEN DT_X$ = "X"
573 IF MENUBAR_ON% = 1% THEN MB_S$ = "ON"
574 IF MENUBAR_ON% = 1% THEN MB_X$ = "X"
575 ML_X$ = " " \ AL_X$ = " " \ RP_S$ = "OFF" \ RP_X$ = " " \ BL_S$ = "OFF" \ BL_X$ = " "
576 IF MIL_MODE% = 1% THEN ML_X$ = "X"
577 IF ALM_ON% = 1% THEN AL_X$ = "X"
578 IF ALM_RPT% = 1% THEN RP_S$ = "ON"
579 IF ALM_RPT% = 1% THEN RP_X$ = "X"
580 IF ALM_BELL% = 1% THEN BL_S$ = "ON"
581 IF ALM_BELL% = 1% THEN BL_X$ = "X"
582 RETURN
583 REM --- Subroutine: Render Standalone Analog Dial ---
584 GOSUB 540 \ GOSUB 592
585 PRINT "        . - ~ ~ ~ - ."
586 PRINT "    . '      12       ' ."
587 PRINT "  .     11 "; R_NW$; " "; R_N$; " "; R_NE$; " 1       ."
588 PRINT " .    10   "; R_NW$; " "; R_N$; " "; R_NE$; "   2      ."
589 PRINT ".   9  "; R_W$; "O"; R_E$; "  3     .   Analog Hands : Hour->"; H12_S$; "  Min->"; M60_S$
590 PRINT " .     8   "; R_SW$; " "; R_S$; " "; R_SE$; "   4      .    Digital Time : "; TIME_STR$
591 PRINT "  .      7 "; R_SW$; " "; R_S$; " "; R_SE$; " 5       .     Date Banner  : "; CLK_DATE$ \ PRINT "    . .      6        . '" \ PRINT "        ' - . _ . - '" \ RETURN
592 REM --- Subroutine: Compute Dynamic Analog Dial Hand Vectors ---
593 H12% = CLK_HR%
594 IF H12% >= 12% THEN H12% = H12% - 12%
595 IF H12% = 0% THEN H12% = 12%
596 FMT_N% = H12% \ GOSUB 535 \ H12_S$ = FMT_S$ \ FMT_N% = CLK_MN% \ GOSUB 535 \ M60_S$ = FMT_S$
597 M_SEC% = INT((CLK_MN% + 2%) / 5%)
598 IF M_SEC% = 0% THEN M_SEC% = 12%
599 R_N$ = " " \ R_NE$ = " " \ R_E$ = "      " \ R_SE$ = " " \ R_S$ = " " \ R_SW$ = " " \ R_W$ = "      " \ R_NW$ = " "
600 IF M_SEC% = 12% OR H12% = 12% THEN R_N$ = "|"
601 IF M_SEC% = 1% OR M_SEC% = 2% OR H12% = 1% OR H12% = 2% THEN R_NE$ = "/"
602 IF M_SEC% = 3% OR H12% = 3% THEN R_E$ = "------"
603 IF M_SEC% = 4% OR M_SEC% = 5% OR H12% = 4% OR H12% = 5% THEN R_SE$ = "\"
604 IF M_SEC% = 6% OR H12% = 6% THEN R_S$ = "|"
605 IF M_SEC% = 7% OR M_SEC% = 8% OR H12% = 7% OR H12% = 8% THEN R_SW$ = "/"
606 IF M_SEC% = 9% OR H12% = 9% THEN R_W$ = "------"
607 IF M_SEC% = 10% OR M_SEC% = 11% OR H12% = 10% OR H12% = 11% THEN R_NW$ = "\"
608 RETURN
609 REM --- Subroutine: Render Motif/XUI Clock Window ---
610 IF OUT_FILE$ <> "" THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #3%
611 B_L$ = "| " \ B_R$ = " |" \ W_BTN$ = " [v][^] |" \ W_DT$ = " | Date: " \ W_AL$ = " | Alarm: "
612 L1$ = "+----------------------------------------------------------------------------+"
613 W_T$ = LEFT$(CLK_DATE$ + SP1$ + LBRK$ + FACE_MODE$ + RBRK$ + BLANKS$, 40%)
614 L2$ = "| [=] DECwindows Clock (dxclock) - " + W_T$ + W_BTN$
615 L3$ = "| File  Options                                                         Help |"
616 GOSUB 540 \ GOSUB 560 \ GOSUB 592
617 W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = L2$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
618 IF MENUBAR_ON% = 1% THEN W_LN$ = L3$
619 IF MENUBAR_ON% = 1% THEN GOSUB 650
620 IF MENUBAR_ON% = 1% THEN W_LN$ = L1$
621 IF MENUBAR_ON% = 1% THEN GOSUB 650
622 IF DATE_ON% = 1% THEN PAD_OUT$ = LEFT$("Date Part: " + CLK_DATE$ + W_DT$ + CLK_TZ$ + BLANKS$, 74%)
623 IF DATE_ON% = 1% THEN W_LN$ = B_L$ + PAD_OUT$ + B_R$
624 IF DATE_ON% = 1% THEN GOSUB 650
625 IF DATE_ON% = 1% THEN W_LN$ = L1$
626 IF DATE_ON% = 1% THEN GOSUB 650
627 IF ANALOG_ON% = 0% THEN GOTO 640
628 W_LN$ = "|                     . - ~ ~ ~ - .                                          |" \ GOSUB 650
629 W_LN$ = "|                 . '      12       ' .                                      |" \ GOSUB 650
630 P_R1$ = "1       ." \ P_R2$ = "  2      ." \ P_R3$ = "  3     ." \ P_R4$ = "  4      ."
631 A_L1$ = "|               .     11 " + R_NW$ + SP1$ + R_N$ + SP1$ + R_NE$ + SP1$ + P_R1$
632 PAD_OUT$ = LEFT$(A_L1$ + BLANKS$, 77%) + PIPE$ \ W_LN$ = PAD_OUT$ \ GOSUB 650
633 A_L2$ = "|              .    10   " + R_NW$ + SP1$ + R_N$ + SP1$ + R_NE$ + SP1$ + P_R2$
634 PAD_OUT$ = LEFT$(A_L2$ + BLANKS$, 77%) + PIPE$ \ W_LN$ = PAD_OUT$ \ GOSUB 650
635 A_L3$ = "|              .   9  " + R_W$ + CTR_O$ + R_E$ + P_R3$
636 PAD_OUT$ = LEFT$(A_L3$ + BLANKS$, 77%) + PIPE$ \ W_LN$ = PAD_OUT$ \ GOSUB 650
637 A_L4$ = "|               .     8   " + R_SW$ + SP1$ + R_S$ + SP1$ + R_SE$ + SP1$ + P_R4$
638 PAD_OUT$ = LEFT$(A_L4$ + BLANKS$, 77%) + PIPE$ \ W_LN$ = PAD_OUT$ \ GOSUB 650
639 W_LN$ = "|                 . .      6        . '                                      |" \ GOSUB 650 \ W_LN$ = "|                     ' - . _ . - '                                          |" \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
640 IF DIGITAL_ON% = 1% THEN PAD_OUT$ = LEFT$("Digital Readout: " + TIME_STR$ + W_DT$ + CLK_DATE$ + W_AL$ + ALM_STR$ + BLANKS$, 74%)
641 IF DIGITAL_ON% = 1% THEN W_LN$ = B_L$ + PAD_OUT$ + B_R$
642 IF DIGITAL_ON% = 1% THEN GOSUB 650
643 IF DIGITAL_ON% = 1% THEN W_LN$ = L1$
644 IF DIGITAL_ON% = 1% THEN GOSUB 650
645 PAD_OUT$ = LEFT$("Alarm Msg: " + ALM_MSG$ + SP1$ + PIPE$ + SP1$ + CLK_TZ$ + BLANKS$, 74%)
646 W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
647 IF OUT_FILE$ <> "" THEN CLOSE #3%
648 RETURN
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
700 REM --- Subroutine: Save State to SAVE_PATH$ ---
702 OPEN SAVE_PATH$ FOR OUTPUT AS FILE #1%
704 S_IN$ = STR$(CLK_HR%) \ GOSUB 500 \ H_S$ = S_OUT$ \ S_IN$ = STR$(CLK_MN%) \ GOSUB 500 \ M_S$ = S_OUT$
706 S_REC$ = "CLK" + PIPE$ + H_S$ + PIPE$ + M_S$ + PIPE$ + CLK_DATE$ + PIPE$ + FACE_MODE$
708 PRINT #1%, S_REC$
710 S_IN$ = STR$(ALM_ON%) \ GOSUB 500 \ AO_S$ = S_OUT$ \ S_IN$ = STR$(ALM_HR%) \ GOSUB 500 \ AH_S$ = S_OUT$ \ S_IN$ = STR$(ALM_MN%) \ GOSUB 500 \ AM_S$ = S_OUT$
712 S_REC$ = "ALM" + PIPE$ + AO_S$ + PIPE$ + AH_S$ + PIPE$ + AM_S$ + PIPE$ + ALM_MSG$
714 PRINT #1%, S_REC$
715 S_IN$ = STR$(ANALOG_ON%) \ GOSUB 500 \ O1$ = S_OUT$ \ S_IN$ = STR$(DIGITAL_ON%) \ GOSUB 500 \ O2$ = S_OUT$ \ S_IN$ = STR$(DATE_ON%) \ GOSUB 500 \ O3$ = S_OUT$
716 S_IN$ = STR$(MENUBAR_ON%) \ GOSUB 500 \ O4$ = S_OUT$ \ S_IN$ = STR$(MIL_MODE%) \ GOSUB 500 \ O5$ = S_OUT$ \ S_IN$ = STR$(ALM_RPT%) \ GOSUB 500 \ O6$ = S_OUT$
717 S_REC$ = "OPT" + PIPE$ + O1$ + PIPE$ + O2$ + PIPE$ + O3$ + PIPE$ + O4$ + PIPE$ + O5$ + PIPE$ + O6$
718 PRINT #1%, S_REC$ \ CLOSE #1%
719 RETURN
720 REM --- Subroutine: Parse OPT|analog|digital|date|menubar|mil|rpt ---
722 O_R$ = MID$(L_REC$, 5%, LEN(L_REC$) - 4%)
724 ANALOG_ON% = VAL(LEFT$(O_R$, 1%)) \ DIGITAL_ON% = VAL(MID$(O_R$, 3%, 1%)) \ DATE_ON% = VAL(MID$(O_R$, 5%, 1%))
726 MENUBAR_ON% = VAL(MID$(O_R$, 7%, 1%)) \ MIL_MODE% = VAL(MID$(O_R$, 9%, 1%)) \ ALM_RPT% = VAL(MID$(O_R$, 11%, 1%))
728 RETURN
990 PRINT "DECwindows Clock V3.0 session terminated."
999 END
