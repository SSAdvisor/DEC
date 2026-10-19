10 REM =================================================================
12 REM DECwindows DECsound V3.0 (DECW$SOUND / dxsound)
14 REM Digital Equipment Corporation VAX/VMS, ULTRIX & OSF/1 (1990-1995)
16 REM Sub-Project 8 of 11 in DECwindows Faithful BASIC-PLUS-2 Port
18 REM =================================================================
20 DIM CLIP_NAME$(40%) \ DIM CLIP_FMT$(40%) \ DIM CLIP_SEC%(40%) \ DIM CLIP_PK%(40%) \ DIM CLIP_DESC$(40%)
22 NUM_CLIPS% = 0% \ CUR_CLIP% = 0%
24 OUT_DEV$ = "SPEAKER (Internal BBA)" \ IN_DEV$ = "MICROPHONE (DECaudio Handset)"
25 VOL_PCT% = 80% \ GAIN_PCT% = 75%
26 PIPE$ = "|" \ SEMI$ = ";" \ SP1$ = " " \ PCT$ = "%" \ SEC_S$ = "s"
27 LBRK$ = "[" \ RBRK$ = "]" \ HASH$ = "#" \ BAR_CH$ = "="
28 BLANKS$ = "                                                                                "
29 BARS$ = "=================================================="
30 IS_BATCH% = 0% \ CMD_INIT$ = COMMAND$
31 IF CMD_INIT$ <> "" THEN IS_BATCH% = 1%
32 IF CMD_INIT$ <> "" THEN REM_CHAIN$ = CMD_INIT$
33 IF CMD_INIT$ <> "" THEN GOTO 54
34 PRINT "======================================================================"
35 PRINT " DECwindows DECsound V3.0 (DECW$SOUND / dxsound)"
36 PRINT " Digital Equipment Corporation - Workstation Audio & Voice Annotations"
37 PRINT " Type HELP for commands, SAMPLE for DECaudio clip library, EXIT."
38 PRINT "======================================================================"
39 PRINT ""
40 REM --- Main Interactive REPL & Command Chain Loop ---
42 REM_CHAIN$ = ""
44 IF REM_CHAIN$ <> "" THEN GOTO 54
45 IF IS_BATCH% = 1% THEN GOTO 990
46 PRINT "DECSOUND> "; \ LINE INPUT RAW_IN$
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
96 IF VERB$ = "LIST" THEN GOTO 215
98 IF VERB$ = "CLIPS" THEN GOTO 215
100 IF VERB$ = "DIR" THEN GOTO 215
102 IF VERB$ = "PLAY" THEN GOTO 250
104 IF VERB$ = "SELECT" THEN GOTO 250
106 IF VERB$ = "RECORD" THEN GOTO 285
108 IF VERB$ = "ADD" THEN GOTO 285
110 IF VERB$ = "DELETE" THEN GOTO 320
112 IF VERB$ = "DEL" THEN GOTO 320
114 IF VERB$ = "WAVEFORM" THEN GOTO 340
116 IF VERB$ = "VU" THEN GOTO 340
118 IF VERB$ = "INSPECT" THEN GOTO 340
120 IF VERB$ = "VOLUME" THEN GOTO 375
122 IF VERB$ = "GAIN" THEN GOTO 385
124 IF VERB$ = "OUTPUT" THEN GOTO 395
126 IF VERB$ = "INPUT" THEN GOTO 405
128 IF VERB$ = "SEARCH" THEN GOTO 415
130 IF VERB$ = "FIND" THEN GOTO 415
132 IF VERB$ = "DISPLAY" THEN GOTO 440
134 IF VERB$ = "SCREEN" THEN GOTO 440
136 IF VERB$ = "RENDER" THEN GOTO 440
140 IF VERB$ <> "HELP" THEN GOTO 154
141 PRINT "--- DECwindows DECsound V3.0 Commands ---"
142 PRINT "  SAMPLE / DEMO                        : Load DECaudio & voice annotation clips"
143 PRINT "  LIST [format] / CLIPS / DIR          : List audio clips (optional format filter)"
144 PRINT "  PLAY [id|name] / SELECT [id|name]    : Play audio clip with VU meter readout"
145 PRINT "  RECORD <name|fmt|sec|peak|desc>      : Record/add new voice annotation clip"
146 PRINT "  DELETE <id> / DEL <id>               : Remove audio clip #<id> from library"
147 PRINT "  WAVEFORM [id] / VU / INSPECT         : Inspect clip mu-law/PCM waveform & dB"
148 PRINT "  VOLUME <0..100> / GAIN <0..100>      : Set playback volume or recording gain"
149 PRINT "  OUTPUT <SPEAKER|HEADPHONE|LINE-OUT>  : Route DECaudio BBA output device"
150 PRINT "  INPUT <MICROPHONE|LINE-IN>           : Route DECaudio BBA input source"
151 PRINT "  SEARCH <kw> / DISPLAY [ON <file>]    : Search clips or render Motif window"
152 PRINT "  SHOW / SAVE <file> / LOAD <file>     : Status, save/load library, CLEAR, EXIT"
153 GOTO 44
154 IF VERB$ = "EXPORT" THEN GOTO 440
156 IF VERB$ = "PRINT" THEN GOTO 440
158 IF VERB$ = "SAVE" THEN GOTO 455
160 IF VERB$ = "LOAD" THEN GOTO 472
162 IF VERB$ = "CLEAR" THEN GOTO 490
164 IF VERB$ = "RESET" THEN GOTO 490
166 PRINT "%DECSOUND-E-INVCMD, Unrecognized command: "; VERB$
168 GOTO 44
170 REM --- SAMPLE / DEMO ---
172 NUM_CLIPS% = 6% \ CUR_CLIP% = 1%
173 OUT_DEV$ = "SPEAKER (Internal BBA)" \ IN_DEV$ = "MICROPHONE (DECaudio Handset)"
174 VOL_PCT% = 80% \ GAIN_PCT% = 75%
176 CLIP_NAME$(1%) = "VAX_BOOT_CHIME.AU" \ CLIP_FMT$(1%) = "MULAW-8KHZ" \ CLIP_SEC%(1%) = 4% \ CLIP_PK%(1%) = 85%
177 CLIP_DESC$(1%) = "VAXstation 4000 BBA Power-On Self-Test Chime"
178 CLIP_NAME$(2%) = "NEWMAIL_BELL.AU" \ CLIP_FMT$(2%) = "MULAW-8KHZ" \ CLIP_SEC%(2%) = 2% \ CLIP_PK%(2%) = 90%
179 CLIP_DESC$(2%) = "DECwindows Mail New Message Arrival Bell"
180 CLIP_NAME$(3%) = "ALPHA_INTRO.AU" \ CLIP_FMT$(3%) = "PCM16-11KHZ" \ CLIP_SEC%(3%) = 18% \ CLIP_PK%(3%) = 92%
181 CLIP_DESC$(3%) = "Ken Olsen & Bob Supnik Alpha AXP Launch Voice Note"
182 CLIP_NAME$(4%) = "CLUSTER_ALERT.AU" \ CLIP_FMT$(4%) = "MULAW-8KHZ" \ CLIP_SEC%(4%) = 6% \ CLIP_PK%(4%) = 95%
183 CLIP_DESC$(4%) = "VAXcluster Quorum Transition Spoken Alert"
184 CLIP_NAME$(5%) = "CDA_VOICENOTE.AU" \ CLIP_FMT$(5%) = "MULAW-8KHZ" \ CLIP_SEC%(5%) = 12% \ CLIP_PK%(5%) = 78%
185 CLIP_DESC$(5%) = "DDIF Compound Document Embedded Voice Annotation"
186 CLIP_NAME$(6%) = "DECUS_THEME.AU" \ CLIP_FMT$(6%) = "PCM16-11KHZ" \ CLIP_SEC%(6%) = 25% \ CLIP_PK%(6%) = 88%
187 CLIP_DESC$(6%) = "DECUS Symposium Digital Audio Synthesis Demo"
188 PRINT "[Loaded Sample DECsound Library: 6 audio clips (Active: "; CLIP_NAME$(1%); ")]"
190 GOTO 44
200 REM --- SHOW / STATUS ---
202 ACT_N$ = "NONE"
203 IF CUR_CLIP% > 0% AND CUR_CLIP% <= NUM_CLIPS% THEN ACT_N$ = CLIP_NAME$(CUR_CLIP%)
204 PRINT "=== DECwindows DECsound Status ==="
206 PRINT "  Output Device  : "; OUT_DEV$; "  |  Volume : "; VOL_PCT%; "%"
208 PRINT "  Input Source   : "; IN_DEV$; "  |  Gain   : "; GAIN_PCT%; "%"
210 PRINT "  Active Clip    : #"; CUR_CLIP%; " ("; ACT_N$; ")"
212 PRINT "  Total Clips    : "; NUM_CLIPS%; " audio clips in library"
214 GOTO 44
215 REM --- LIST [format] / CLIPS / DIR ---
216 S_IN$ = ARG$ \ GOSUB 520 \ FILT_F$ = S_OUT$
218 IF FILT_F$ = "ALL" THEN FILT_F$ = ""
220 PRINT "=== DECsound Audio Clip Library ==="
222 PRINT "ID  | Clip Filename      | Format       | Dur | Peak | Voice Annotation / Description"
224 PRINT "----+--------------------+--------------+-----+------+----------------------------------------"
226 MATCH_CNT% = 0% \ I% = 1%
228 IF I% > NUM_CLIPS% THEN GOTO 244
230 S_IN$ = CLIP_FMT$(I%) \ GOSUB 520 \ UF$ = S_OUT$
231 IF FILT_F$ = "" THEN GOTO 234
232 IF INSTR(1%, UF$, FILT_F$) = 0% THEN GOTO 242
234 MATCH_CNT% = MATCH_CNT% + 1%
235 S_IN$ = STR$(I%) \ GOSUB 500 \ C_ID$ = LEFT$(S_OUT$ + BLANKS$, 3%)
236 C_NM$ = LEFT$(CLIP_NAME$(I%) + BLANKS$, 18%) \ C_FM$ = LEFT$(CLIP_FMT$(I%) + BLANKS$, 12%)
237 S_IN$ = STR$(CLIP_SEC%(I%)) \ GOSUB 500 \ C_SC$ = LEFT$(S_OUT$ + SEC_S$ + BLANKS$, 3%)
238 S_IN$ = STR$(CLIP_PK%(I%)) \ GOSUB 500 \ C_PK$ = LEFT$(S_OUT$ + PCT$ + BLANKS$, 4%)
239 C_DS$ = LEFT$(CLIP_DESC$(I%), 40%)
240 PRINT C_ID$; " | "; C_NM$; " | "; C_FM$; " | "; C_SC$; " | "; C_PK$; " | "; C_DS$
242 I% = I% + 1% \ GOTO 228
244 PRINT "Total audio clips listed: "; MATCH_CNT% \ GOTO 44
250 REM --- PLAY [id_or_name] / SELECT ---
252 IF NUM_CLIPS% = 0% THEN PRINT "%DECSOUND-W-EMPTY, No audio clips in library."
253 IF NUM_CLIPS% = 0% THEN GOTO 44
254 IF ARG$ = "" THEN GOTO 272
256 P_ID% = VAL(ARG$)
258 IF P_ID% >= 1% AND P_ID% <= NUM_CLIPS% THEN CUR_CLIP% = P_ID%
259 IF P_ID% >= 1% AND P_ID% <= NUM_CLIPS% THEN GOTO 272
260 S_IN$ = ARG$ \ GOSUB 520 \ U_T$ = S_OUT$ \ FOUND_C% = 0% \ I% = 1%
262 IF I% > NUM_CLIPS% THEN GOTO 268
264 S_IN$ = CLIP_NAME$(I%) \ GOSUB 520
265 IF INSTR(1%, S_OUT$, U_T$) > 0% AND FOUND_C% = 0% THEN FOUND_C% = I%
266 I% = I% + 1% \ GOTO 262
268 IF FOUND_C% = 0% THEN PRINT "%DECSOUND-E-NOTFND, Audio clip not found: "; ARG$
269 IF FOUND_C% = 0% THEN GOTO 44
270 CUR_CLIP% = FOUND_C%
272 VU_LEN% = INT(CLIP_PK%(CUR_CLIP%) * 30% / 100%)
274 VU_BAR$ = LEFT$(BARS$, VU_LEN%)
276 PRINT "[Playing Clip #"; CUR_CLIP%; ": "; CLIP_NAME$(CUR_CLIP%); " ("; CLIP_FMT$(CUR_CLIP%); ", "; CLIP_SEC%(CUR_CLIP%); "s) -> "; OUT_DEV$; " @ Vol "; VOL_PCT%; "%]"
278 PRINT "  Annotation : "; CLIP_DESC$(CUR_CLIP%)
280 PRINT "  VU Meter   : ["; VU_BAR$; "] (Peak "; CLIP_PK%(CUR_CLIP%); "%)"
282 GOTO 44
285 REM --- RECORD <name|fmt|sec|peak|desc> / ADD ---
286 P1% = INSTR(1%, ARG$, PIPE$)
288 IF P1% = 0% THEN PRINT "%DECSOUND-E-SYNTAX, Usage: RECORD <name|format|sec|peak|description>"
289 IF P1% = 0% THEN GOTO 44
290 N_NM$ = LEFT$(ARG$, P1% - 1%) \ R1$ = MID$(ARG$, P1% + 1%, LEN(ARG$) - P1%)
292 P2% = INSTR(1%, R1$, PIPE$)
293 IF P2% = 0% THEN PRINT "%DECSOUND-E-SYNTAX, Usage: RECORD <name|format|sec|peak|description>"
294 IF P2% = 0% THEN GOTO 44
296 N_FM$ = LEFT$(R1$, P2% - 1%) \ R2$ = MID$(R1$, P2% + 1%, LEN(R1$) - P2%)
298 P3% = INSTR(1%, R2$, PIPE$)
299 IF P3% = 0% THEN PRINT "%DECSOUND-E-SYNTAX, Usage: RECORD <name|format|sec|peak|description>"
300 IF P3% = 0% THEN GOTO 44
302 N_SC% = VAL(LEFT$(R2$, P3% - 1%)) \ R3$ = MID$(R2$, P3% + 1%, LEN(R2$) - P3%)
304 P4% = INSTR(1%, R3$, PIPE$)
305 IF P4% = 0% THEN N_PK% = 80%
306 IF P4% = 0% THEN N_DS$ = R3$
307 IF P4% > 0% THEN N_PK% = VAL(LEFT$(R3$, P4% - 1%))
308 IF P4% > 0% THEN N_DS$ = MID$(R3$, P4% + 1%, LEN(R3$) - P4%)
310 NUM_CLIPS% = NUM_CLIPS% + 1% \ CUR_CLIP% = NUM_CLIPS%
312 CLIP_NAME$(NUM_CLIPS%) = N_NM$ \ CLIP_FMT$(NUM_CLIPS%) = N_FM$ \ CLIP_SEC%(NUM_CLIPS%) = N_SC%
314 CLIP_PK%(NUM_CLIPS%) = N_PK% \ CLIP_DESC$(NUM_CLIPS%) = N_DS$
316 PRINT "[Recorded Clip #"; NUM_CLIPS%; ": "; N_NM$; " ("; N_FM$; ", "; N_SC%; "s) from "; IN_DEV$; " @ Gain "; GAIN_PCT%; "%]"
318 GOTO 44
320 REM --- DELETE <id> / DEL <id> ---
322 D_ID% = VAL(ARG$)
324 IF D_ID% < 1% OR D_ID% > NUM_CLIPS% THEN PRINT "%DECSOUND-E-INVID, Invalid clip number."
325 IF D_ID% < 1% OR D_ID% > NUM_CLIPS% THEN GOTO 44
326 D_NM$ = CLIP_NAME$(D_ID%) \ I% = D_ID%
328 IF I% >= NUM_CLIPS% THEN GOTO 334
330 CLIP_NAME$(I%) = CLIP_NAME$(I% + 1%) \ CLIP_FMT$(I%) = CLIP_FMT$(I% + 1%) \ CLIP_SEC%(I%) = CLIP_SEC%(I% + 1%)
332 CLIP_PK%(I%) = CLIP_PK%(I% + 1%) \ CLIP_DESC$(I%) = CLIP_DESC$(I% + 1%) \ I% = I% + 1% \ GOTO 328
334 NUM_CLIPS% = NUM_CLIPS% - 1%
335 IF CUR_CLIP% > NUM_CLIPS% THEN CUR_CLIP% = NUM_CLIPS%
336 PRINT "[Deleted Audio Clip #"; D_ID%; ": "; D_NM$; "]" \ GOTO 44
340 REM --- WAVEFORM [id] / VU / INSPECT ---
342 IF NUM_CLIPS% = 0% THEN PRINT "%DECSOUND-W-EMPTY, No audio clips in library."
343 IF NUM_CLIPS% = 0% THEN GOTO 44
344 IF ARG$ <> "" THEN W_REQ% = VAL(ARG$)
345 IF ARG$ <> "" AND W_REQ% >= 1% AND W_REQ% <= NUM_CLIPS% THEN CUR_CLIP% = W_REQ%
346 RATE_KB% = 8%
348 IF INSTR(1%, CLIP_FMT$(CUR_CLIP%), "PCM16") > 0% THEN RATE_KB% = 22%
350 SZ_KB% = CLIP_SEC%(CUR_CLIP%) * RATE_KB%
352 CL_ST$ = "CLEAN (No Digital Clipping Detected)"
354 IF CLIP_PK%(CUR_CLIP%) >= 98% THEN CL_ST$ = "WARNING (Peak Near 0 dBFS Saturation)"
356 VU_LEN% = INT(CLIP_PK%(CUR_CLIP%) * 40% / 100%) \ VU_BAR$ = LEFT$(BARS$, VU_LEN%)
358 PRINT "=== DECsound Waveform & Codec Inspector: "; CLIP_NAME$(CUR_CLIP%); " ==="
360 PRINT "  Encoding Codec : "; CLIP_FMT$(CUR_CLIP%); " ("; RATE_KB%; " KB/sec)"
362 PRINT "  Duration / Size: "; CLIP_SEC%(CUR_CLIP%); " sec  |  Buffer Size: "; SZ_KB%; " KB"
364 PRINT "  Peak Amplitude : "; CLIP_PK%(CUR_CLIP%); "%     |  Signal Audit: "; CL_ST$
366 PRINT "  Envelope (VU)  : |"; VU_BAR$; "|"
368 PRINT "  Annotation     : "; CLIP_DESC$(CUR_CLIP%)
370 GOTO 44
375 REM --- VOLUME <0..100> ---
376 V_REQ% = VAL(ARG$)
377 IF V_REQ% < 0% OR V_REQ% > 100% THEN PRINT "%DECSOUND-E-RANGE, Volume must be 0..100."
378 IF V_REQ% < 0% OR V_REQ% > 100% THEN GOTO 44
380 VOL_PCT% = V_REQ% \ PRINT "[Playback Volume set to "; VOL_PCT%; "%]" \ GOTO 44
385 REM --- GAIN <0..100> ---
386 G_REQ% = VAL(ARG$)
387 IF G_REQ% < 0% OR G_REQ% > 100% THEN PRINT "%DECSOUND-E-RANGE, Gain must be 0..100."
388 IF G_REQ% < 0% OR G_REQ% > 100% THEN GOTO 44
390 GAIN_PCT% = G_REQ% \ PRINT "[Recording Gain set to "; GAIN_PCT%; "%]" \ GOTO 44
395 REM --- OUTPUT <dev> ---
396 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
398 IF UARG$ = "SPEAKER" THEN OUT_DEV$ = "SPEAKER (Internal BBA)"
399 IF UARG$ = "HEADPHONE" THEN OUT_DEV$ = "HEADPHONE (Front Jack)"
400 IF UARG$ = "LINE-OUT" THEN OUT_DEV$ = "LINE-OUT (Rear RCA)"
402 PRINT "[DECaudio Output routed to: "; OUT_DEV$; "]" \ GOTO 44
405 REM --- INPUT <dev> ---
406 S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
408 IF UARG$ = "MICROPHONE" THEN IN_DEV$ = "MICROPHONE (DECaudio Handset)"
409 IF UARG$ = "LINE-IN" THEN IN_DEV$ = "LINE-IN (Auxiliary)"
412 PRINT "[DECaudio Input routed to: "; IN_DEV$; "]" \ GOTO 44
415 REM --- SEARCH <keyword> / FIND <keyword> ---
416 IF ARG$ = "" THEN PRINT "%DECSOUND-E-SYNTAX, Usage: SEARCH <keyword>"
417 IF ARG$ = "" THEN GOTO 44
418 S_IN$ = ARG$ \ GOSUB 520 \ KW$ = S_OUT$ \ FOUND% = 0%
420 PRINT "=== DECsound Search Results for '"; ARG$; "' ==="
422 I% = 1%
424 IF I% > NUM_CLIPS% THEN GOTO 436
426 S_IN$ = CLIP_NAME$(I%) + SP1$ + CLIP_FMT$(I%) + SP1$ + CLIP_DESC$(I%) \ GOSUB 520 \ HAY$ = S_OUT$
428 IF INSTR(1%, HAY$, KW$) = 0% THEN GOTO 434
430 FOUND% = FOUND% + 1%
432 PRINT "  Clip #"; I%; " ["; CLIP_NAME$(I%); " | "; CLIP_FMT$(I%); "]: "; CLIP_DESC$(I%)
434 I% = I% + 1% \ GOTO 424
436 PRINT "Total matching clips: "; FOUND% \ GOTO 44
440 REM --- DISPLAY [ON <file>] / SCREEN / RENDER / EXPORT ---
441 OUT_FILE$ = "" \ S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
442 IF VERB$ = "EXPORT" THEN OUT_FILE$ = ARG$
443 IF LEFT$(UARG$, 3%) = "ON " THEN OUT_FILE$ = MID$(ARG$, 4%, LEN(ARG$) - 3%)
444 S_IN$ = OUT_FILE$ \ GOSUB 500 \ OUT_FILE$ = S_OUT$
446 GOSUB 600
448 IF OUT_FILE$ <> "" THEN PRINT "[DECsound window exported to "; OUT_FILE$; "]"
450 GOTO 44
455 REM --- SAVE <file> ---
456 IF ARG$ = "" THEN PRINT "%DECSOUND-E-NOFILE, Specify filename for SAVE."
457 IF ARG$ = "" THEN GOTO 44
458 OPEN ARG$ FOR OUTPUT AS FILE #1%
459 S_IN$ = STR$(VOL_PCT%) \ GOSUB 500 \ V_S$ = S_OUT$ \ S_IN$ = STR$(GAIN_PCT%) \ GOSUB 500 \ G_S$ = S_OUT$
460 S_REC$ = "CFG" + PIPE$ + OUT_DEV$ + PIPE$ + IN_DEV$ + PIPE$ + V_S$ + PIPE$ + G_S$
461 PRINT #1%, S_REC$ \ I% = 1%
463 IF I% > NUM_CLIPS% THEN GOTO 469
464 S_IN$ = STR$(CLIP_SEC%(I%)) \ GOSUB 500 \ SC_S$ = S_OUT$ \ S_IN$ = STR$(CLIP_PK%(I%)) \ GOSUB 500 \ PK_S$ = S_OUT$
465 S_REC$ = "CLP" + PIPE$ + CLIP_NAME$(I%) + PIPE$ + CLIP_FMT$(I%) + PIPE$ + SC_S$ + PIPE$ + PK_S$ + PIPE$ + CLIP_DESC$(I%)
467 PRINT #1%, S_REC$ \ I% = I% + 1% \ GOTO 463
469 CLOSE #1%
470 PRINT "[Saved "; NUM_CLIPS%; " audio clips to "; ARG$; "]" \ GOTO 44
472 REM --- LOAD <file> ---
473 IF ARG$ = "" THEN PRINT "%DECSOUND-E-NOFILE, Specify filename for LOAD."
474 IF ARG$ = "" THEN GOTO 44
475 OPEN ARG$ FOR INPUT AS FILE #1%
476 NUM_CLIPS% = 0% \ CUR_CLIP% = 0%
477 LINE INPUT #1%, L_REC$
478 IF LEN(L_REC$) = 0% THEN GOTO 487
479 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 487
480 S_IN$ = L_REC$ \ GOSUB 500 \ L_REC$ = S_OUT$
482 IF LEFT$(L_REC$, 4%) = "CFG|" THEN GOSUB 660
484 IF LEFT$(L_REC$, 4%) = "CLP|" THEN GOSUB 680
485 GOTO 477
487 CLOSE #1%
488 IF NUM_CLIPS% > 0% THEN CUR_CLIP% = 1%
489 PRINT "[Loaded "; NUM_CLIPS%; " audio clips from "; ARG$; "]" \ GOTO 44
490 REM --- CLEAR / RESET ---
492 NUM_CLIPS% = 0% \ CUR_CLIP% = 0%
494 PRINT "[DECsound clip library cleared]" \ GOTO 44
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
600 REM --- Subroutine: Render Motif/XUI DECsound Window ---
602 IF OUT_FILE$ <> "" THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #3%
603 B_L$ = "| " \ B_R$ = " |" \ W_BTN$ = " [v][^] |" \ W_VL$ = " | Vol: " \ W_GN$ = "% | Gain: "
604 L1$ = "+----------------------------------------------------------------------------+"
605 ACT_N$ = "NONE" \ ACT_F$ = "IDLE" \ ACT_D$ = "No Clip Selected" \ ACT_P% = 0%
606 IF CUR_CLIP% > 0% AND CUR_CLIP% <= NUM_CLIPS% THEN ACT_N$ = CLIP_NAME$(CUR_CLIP%)
607 IF CUR_CLIP% > 0% AND CUR_CLIP% <= NUM_CLIPS% THEN ACT_F$ = CLIP_FMT$(CUR_CLIP%)
608 IF CUR_CLIP% > 0% AND CUR_CLIP% <= NUM_CLIPS% THEN ACT_D$ = CLIP_DESC$(CUR_CLIP%)
609 IF CUR_CLIP% > 0% AND CUR_CLIP% <= NUM_CLIPS% THEN ACT_P% = CLIP_PK%(CUR_CLIP%)
610 W_T$ = LEFT$(ACT_N$ + SP1$ + LBRK$ + ACT_F$ + RBRK$ + BLANKS$, 38%)
612 L2$ = "| [=] DECwindows DECsound (dxsound) - " + W_T$ + W_BTN$
614 L3$ = "| File  Edit  Settings  Clips  Waveform  Help                                |"
616 W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = L2$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
618 W_LN$ = L3$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
620 W_LN$ = "|   [ (o) REC ]    [ |> PLAY ]    [ || PAUSE ]    [ [] STOP ]    [ << ] [ >> ]|" \ GOSUB 650
622 W_LN$ = L1$ \ GOSUB 650
624 VU_LEN% = INT(ACT_P% * 40% / 100%) \ VU_BAR$ = LEFT$(BARS$, VU_LEN%)
626 S_IN$ = STR$(ACT_P%) \ GOSUB 500 \ PK_S$ = S_OUT$
628 PAD_OUT$ = LEFT$("VU Meter: [" + VU_BAR$ + RBRK$ + SP1$ + PK_S$ + PCT$ + BLANKS$, 74%)
630 W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650
632 PAD_OUT$ = LEFT$("Voice Note: " + ACT_D$ + BLANKS$, 74%)
634 W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
636 S_IN$ = STR$(VOL_PCT%) \ GOSUB 500 \ V_S$ = S_OUT$ \ S_IN$ = STR$(GAIN_PCT%) \ GOSUB 500 \ G_S$ = S_OUT$
638 PAD_OUT$ = LEFT$("Out: " + OUT_DEV$ + W_VL$ + V_S$ + W_GN$ + G_S$ + PCT$ + BLANKS$, 74%)
640 W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
642 IF OUT_FILE$ <> "" THEN CLOSE #3%
644 RETURN
650 IF OUT_FILE$ = "" THEN PRINT W_LN$
652 IF OUT_FILE$ <> "" THEN PRINT #3%, W_LN$
654 RETURN
660 REM --- Subroutine: Parse CFG|out|in|vol|gain ---
662 H_R$ = MID$(L_REC$, 5%, LEN(L_REC$) - 4%) \ H1% = INSTR(1%, H_R$, PIPE$)
663 IF H1% = 0% THEN GOTO 674
664 OUT_DEV$ = LEFT$(H_R$, H1% - 1%) \ H_R$ = MID$(H_R$, H1% + 1%, LEN(H_R$) - H1%) \ H2% = INSTR(1%, H_R$, PIPE$)
666 IF H2% = 0% THEN GOTO 674
668 IN_DEV$ = LEFT$(H_R$, H2% - 1%) \ H_R$ = MID$(H_R$, H2% + 1%, LEN(H_R$) - H2%) \ H3% = INSTR(1%, H_R$, PIPE$)
670 IF H3% = 0% THEN GOTO 674
672 VOL_PCT% = VAL(LEFT$(H_R$, H3% - 1%)) \ GAIN_PCT% = VAL(MID$(H_R$, H3% + 1%, LEN(H_R$) - H3%))
674 RETURN
680 REM --- Subroutine: Parse CLP|name|fmt|sec|pk|desc ---
682 G_R$ = MID$(L_REC$, 5%, LEN(L_REC$) - 4%) \ G1% = INSTR(1%, G_R$, PIPE$)
683 IF G1% = 0% THEN GOTO 699
684 C_N$ = LEFT$(G_R$, G1% - 1%) \ G_R$ = MID$(G_R$, G1% + 1%, LEN(G_R$) - G1%) \ G2% = INSTR(1%, G_R$, PIPE$)
686 IF G2% = 0% THEN GOTO 699
688 C_F$ = LEFT$(G_R$, G2% - 1%) \ G_R$ = MID$(G_R$, G2% + 1%, LEN(G_R$) - G2%) \ G3% = INSTR(1%, G_R$, PIPE$)
690 IF G3% = 0% THEN GOTO 699
692 C_S% = VAL(LEFT$(G_R$, G3% - 1%)) \ G_R$ = MID$(G_R$, G3% + 1%, LEN(G_R$) - G3%) \ G4% = INSTR(1%, G_R$, PIPE$)
694 IF G4% = 0% THEN GOTO 699
695 C_P% = VAL(LEFT$(G_R$, G4% - 1%)) \ C_D$ = MID$(G_R$, G4% + 1%, LEN(G_R$) - G4%)
696 NUM_CLIPS% = NUM_CLIPS% + 1% \ CLIP_NAME$(NUM_CLIPS%) = C_N$ \ CLIP_FMT$(NUM_CLIPS%) = C_F$
697 CLIP_SEC%(NUM_CLIPS%) = C_S% \ CLIP_PK%(NUM_CLIPS%) = C_P% \ CLIP_DESC$(NUM_CLIPS%) = C_D$
699 RETURN
990 PRINT "DECwindows DECsound V3.0 session terminated."
999 END
