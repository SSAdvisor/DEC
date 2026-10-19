10 REM =================================================================
12 REM DECwindows CDA Viewer V3.0 (Compound Document Architecture)
14 REM Digital Equipment Corporation VAX/VMS, ULTRIX & OSF/1 (1988-1995)
16 REM Sub-Project 5 of 11 in DECwindows Faithful BASIC-PLUS-2 Port
18 REM =================================================================
20 DIM SEG_PG%(60%) \ DIM SEG_TYPE$(60%) \ DIM SEG_DESC$(60%) \ DIM SEG_BODY$(60%)
24 NUM_SEGS% = 0% \ CUR_PG% = 1% \ MAX_PG% = 1%
25 DOC_NAME$ = "UNTITLED.DDIF" \ DOC_FMT$ = "DDIF V1.2 (Compound Document)"
26 DOC_AUTH$ = "DEC Workstation Group" \ DOC_DOTS$ = "PACKED (External Links Resolved)"
27 PIPE$ = "|" \ SEMI$ = ";" \ COLON$ = ":" \ SP1$ = " "
28 LBRK$ = "[" \ RBRK$ = "]" \ HASH$ = "#" \ SLASH$ = "/"
29 BLANKS$ = "                                                                                "
30 IS_BATCH% = 0% \ CMD_INIT$ = COMMAND$
31 IF CMD_INIT$ <> "" THEN IS_BATCH% = 1%
32 IF CMD_INIT$ <> "" THEN REM_CHAIN$ = CMD_INIT$
33 IF CMD_INIT$ <> "" THEN GOTO 54
34 PRINT "======================================================================"
35 PRINT " DECwindows CDA Viewer V3.0 (DECW$CDAVIEWER / dxvdoc)"
36 PRINT " Digital Equipment Corporation - DDIF / DTIF / DOTS Document Viewer"
37 PRINT " Type HELP for commands, SAMPLE for Alpha AXP DDIF document, EXIT."
38 PRINT "======================================================================"
39 PRINT ""
40 REM --- Main Interactive REPL & Command Chain Loop ---
42 REM_CHAIN$ = ""
44 IF REM_CHAIN$ <> "" THEN GOTO 54
45 IF IS_BATCH% = 1% THEN GOTO 990
46 PRINT "CDA> "; \ LINE INPUT RAW_IN$
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
96 IF VERB$ = "INFO" THEN GOTO 200
98 IF VERB$ = "ELEMENTS" THEN GOTO 215
100 IF VERB$ = "SEGMENTS" THEN GOTO 215
102 IF VERB$ = "LIST" THEN GOTO 215
104 IF VERB$ = "DIR" THEN GOTO 215
106 IF VERB$ = "PAGE" THEN GOTO 250
108 IF VERB$ = "READ" THEN GOTO 250
110 IF VERB$ = "VIEW" THEN GOTO 250
112 IF VERB$ = "NEXT" THEN GOTO 280
114 IF VERB$ = "PREV" THEN GOTO 290
116 IF VERB$ = "PAGES" THEN GOTO 300
118 IF VERB$ = "DOCUMENT" THEN GOTO 300
120 IF VERB$ = "ALL" THEN GOTO 300
122 IF VERB$ = "ADDSEG" THEN GOTO 315
124 IF VERB$ = "ADD" THEN GOTO 315
126 IF VERB$ = "DELSEG" THEN GOTO 345
128 IF VERB$ = "DELETE" THEN GOTO 345
130 IF VERB$ = "INSPECT" THEN GOTO 365
132 IF VERB$ = "ANALYZE" THEN GOTO 365
133 IF VERB$ = "CHECK" THEN GOTO 365
134 IF VERB$ = "SEARCH" THEN GOTO 405
135 IF VERB$ = "FIND" THEN GOTO 405
136 IF VERB$ = "FORMAT" THEN GOTO 430
137 IF VERB$ = "DISPLAY" THEN GOTO 440
138 IF VERB$ = "SCREEN" THEN GOTO 440
139 IF VERB$ = "RENDER" THEN GOTO 440
140 IF VERB$ <> "HELP" THEN GOTO 154
141 PRINT "--- DECwindows CDA Viewer V3.0 Commands ---"
142 PRINT "  SAMPLE / DEMO                        : Load Alpha AXP DDIF compound document"
143 PRINT "  ELEMENTS [type] / SEGMENTS / LIST    : List CDA segments (optional type filter)"
144 PRINT "  PAGE <n> / READ <n> / NEXT / PREV    : Render compound segments on page <n>"
145 PRINT "  PAGES / DOCUMENT / ALL               : Render all pages of compound document"
146 PRINT "  ADDSEG <pg|type|desc|body> / DELSEG  : Add or delete a CDA document segment"
147 PRINT "  INSPECT / ANALYZE / CHECK            : Run DDIF/DTIF/DOTS conformance audit"
148 PRINT "  SEARCH <kw> / FIND <kw>              : Search segment descriptors and content"
149 PRINT "  FORMAT <fmt>                         : Set CDA presentation format (DDIF/DTIF/PS)"
150 PRINT "  DISPLAY [ON <file>] / EXPORT <file>  : Render Motif/XUI CDA Viewer window"
151 PRINT "  SHOW / SAVE <file> / LOAD <file>     : View status or save/load .cda document"
152 PRINT "  CLEAR / HELP / EXIT                  : Reset document, show help, or quit"
153 GOTO 44
154 IF VERB$ = "EXPORT" THEN GOTO 440
156 IF VERB$ = "PRINT" THEN GOTO 440
158 IF VERB$ = "SAVE" THEN GOTO 455
160 IF VERB$ = "LOAD" THEN GOTO 472
162 IF VERB$ = "CLEAR" THEN GOTO 490
164 IF VERB$ = "RESET" THEN GOTO 490
166 PRINT "%CDAVIEWER-E-INVCMD, Unrecognized command: "; VERB$
168 GOTO 44
170 REM --- SAMPLE / DEMO: Load Alpha AXP Compound Document ---
172 DOC_NAME$ = "ALPHA_SPEC.DDIF" \ DOC_FMT$ = "DDIF V1.2 (Compound Document)"
174 DOC_AUTH$ = "DEC Alpha Architecture Group (MRO)"
176 DOC_DOTS$ = "PACKED (External Links Resolved)"
178 NUM_SEGS% = 6% \ CUR_PG% = 1% \ MAX_PG% = 3%
180 SEG_PG%(1%) = 1% \ SEG_TYPE$(1%) = "HEADER" \ SEG_DESC$(1%) = "DDIF$S_SEG_HDR (ISO-Latin-1)"
181 SEG_BODY$(1%) = "DEC ALPHA AXP 21064 ARCHITECTURE SPECIFICATION"
182 SEG_PG%(2%) = 1% \ SEG_TYPE$(2%) = "TEXT" \ SEG_DESC$(2%) = "DDIF$S_SEG_TXT (Galleys 1-2)"
183 SEG_BODY$(2%) = "64-bit RISC load/store architecture with 32 integer and 32 FP registers."
184 SEG_PG%(3%) = 1% \ SEG_TYPE$(3%) = "GRAPHIC" \ SEG_DESC$(3%) = "DDIF$S_SEG_ISL (600x400 Sixel/ISL)"
185 SEG_BODY$(3%) = "[DIAGRAM: Superpipelined 7-Stage Dual-Issue Execution Pipeline]"
186 SEG_PG%(4%) = 2% \ SEG_TYPE$(4%) = "TABLE" \ SEG_DESC$(4%) = "DTIF$S_TBL_SPEC (4x3 Matrix)"
187 SEG_BODY$(4%) = "CHIP: 21064 (EV4) | CLOCK: 150-200 MHz | CACHE: 8KB I + 8KB D"
188 SEG_PG%(5%) = 2% \ SEG_TYPE$(5%) = "TEXT" \ SEG_DESC$(5%) = "DDIF$S_SEG_TXT (PALcode Layer)"
189 SEG_BODY$(5%) = "Privileged Architecture Library (PALcode) supports OpenVMS, OSF/1, and NT."
190 SEG_PG%(6%) = 3% \ SEG_TYPE$(6%) = "FOOTER" \ SEG_DESC$(6%) = "DDIF$S_SEG_FTR (Document Control)"
191 SEG_BODY$(6%) = "DEC-AXP-ARCH-1992-REV1 | Digital Equipment Corporation, Maynard MA"
194 PRINT "[Loaded Sample CDA Document: "; DOC_NAME$; " ("; NUM_SEGS%; " segments, "; MAX_PG%; " pages)]"
196 GOTO 44
200 REM --- SHOW / STATUS / INFO ---
202 PRINT "=== DECwindows CDA Viewer Status ==="
204 PRINT "  Document Name  : "; DOC_NAME$
206 PRINT "  CDA Format     : "; DOC_FMT$
208 PRINT "  Author / Dept  : "; DOC_AUTH$
210 PRINT "  DOTS Transport : "; DOC_DOTS$
212 PRINT "  Current Page   : Page "; CUR_PG%; " of "; MAX_PG%
213 PRINT "  Total Segments : "; NUM_SEGS%; " compound segments"
214 GOTO 44
215 REM --- ELEMENTS [type] / SEGMENTS / LIST / DIR ---
216 S_IN$ = ARG$ \ GOSUB 520 \ FILT_T$ = S_OUT$
218 IF FILT_T$ = "ALL" THEN FILT_T$ = ""
220 PRINT "=== CDA Document Segments ("; DOC_NAME$; ") ==="
222 PRINT "Seg# | Pg | Type     | DDIF/DTIF Aggregate Descriptor   | Content"
224 PRINT "-----+----+----------+----------------------------------+----------------------------------"
226 MATCH_CNT% = 0% \ I% = 1%
228 IF I% > NUM_SEGS% THEN GOTO 244
230 S_IN$ = SEG_TYPE$(I%) \ GOSUB 520 \ UT$ = S_OUT$
231 IF FILT_T$ = "" THEN GOTO 234
232 IF UT$ <> FILT_T$ THEN GOTO 242
234 MATCH_CNT% = MATCH_CNT% + 1%
236 S_IN$ = STR$(I%) \ GOSUB 500 \ C_ID$ = LEFT$(S_OUT$ + BLANKS$, 4%)
237 S_IN$ = STR$(SEG_PG%(I%)) \ GOSUB 500 \ C_PG$ = LEFT$(S_OUT$ + BLANKS$, 2%)
238 C_TY$ = LEFT$(SEG_TYPE$(I%) + BLANKS$, 8%)
239 C_DS$ = LEFT$(SEG_DESC$(I%) + BLANKS$, 34%)
240 B_PRV$ = LEFT$(SEG_BODY$(I%), 36%)
241 PRINT C_ID$; " | "; C_PG$; " | "; C_TY$; " | "; C_DS$; " | "; B_PRV$
242 I% = I% + 1% \ GOTO 228
244 PRINT "Total segments listed: "; MATCH_CNT%
246 GOTO 44
250 REM --- PAGE <n> / READ <n> / VIEW <n> ---
252 IF NUM_SEGS% = 0% THEN PRINT "%CDAVIEWER-W-EMPTY, No CDA document loaded."
254 IF NUM_SEGS% = 0% THEN GOTO 44
256 PG_REQ% = CUR_PG%
258 IF ARG$ <> "" THEN PG_REQ% = VAL(ARG$)
260 IF PG_REQ% < 1% THEN GOTO 266
262 IF PG_REQ% > MAX_PG% THEN GOTO 266
264 GOTO 270
266 PRINT "%CDAVIEWER-E-INVPG, Page number out of range (1.."; MAX_PG%; ")."
268 GOTO 44
270 CUR_PG% = PG_REQ%
272 GOSUB 560
274 GOTO 44
280 REM --- NEXT ---
282 IF NUM_SEGS% = 0% THEN PRINT "%CDAVIEWER-W-EMPTY, No CDA document loaded."
283 IF NUM_SEGS% = 0% THEN GOTO 44
284 IF CUR_PG% < MAX_PG% THEN CUR_PG% = CUR_PG% + 1%
286 GOSUB 560
288 GOTO 44
290 REM --- PREV ---
292 IF NUM_SEGS% = 0% THEN PRINT "%CDAVIEWER-W-EMPTY, No CDA document loaded."
293 IF NUM_SEGS% = 0% THEN GOTO 44
294 IF CUR_PG% > 1% THEN CUR_PG% = CUR_PG% - 1%
296 GOSUB 560
298 GOTO 44
300 REM --- PAGES / DOCUMENT / ALL ---
302 IF NUM_SEGS% = 0% THEN PRINT "%CDAVIEWER-W-EMPTY, No CDA document loaded."
304 IF NUM_SEGS% = 0% THEN GOTO 44
306 SAV_PG% = CUR_PG% \ CUR_PG% = 1%
308 IF CUR_PG% > MAX_PG% THEN GOTO 312
310 GOSUB 560 \ CUR_PG% = CUR_PG% + 1% \ GOTO 308
312 CUR_PG% = SAV_PG% \ GOTO 44
315 REM --- ADDSEG <pg|type|desc|body> / ADD ---
316 P1% = INSTR(1%, ARG$, PIPE$)
318 IF P1% = 0% THEN PRINT "%CDAVIEWER-E-SYNTAX, Usage: ADDSEG <page|type|descriptor|content>"
320 IF P1% = 0% THEN GOTO 44
322 S_PG$ = LEFT$(ARG$, P1% - 1%) \ R1$ = MID$(ARG$, P1% + 1%, LEN(ARG$) - P1%)
324 P2% = INSTR(1%, R1$, PIPE$)
326 IF P2% = 0% THEN PRINT "%CDAVIEWER-E-SYNTAX, Usage: ADDSEG <page|type|descriptor|content>"
328 IF P2% = 0% THEN GOTO 44
330 S_TY$ = LEFT$(R1$, P2% - 1%) \ R2$ = MID$(R1$, P2% + 1%, LEN(R1$) - P2%)
332 P3% = INSTR(1%, R2$, PIPE$)
334 IF P3% = 0% THEN S_DS$ = "DDIF$S_SEG_USER"
335 IF P3% = 0% THEN S_BD$ = R2$
336 IF P3% > 0% THEN S_DS$ = LEFT$(R2$, P3% - 1%)
337 IF P3% > 0% THEN S_BD$ = MID$(R2$, P3% + 1%, LEN(R2$) - P3%)
338 S_IN$ = S_PG$ \ GOSUB 500 \ N_PG% = VAL(S_OUT$)
339 IF N_PG% < 1% THEN N_PG% = 1%
340 S_IN$ = S_TY$ \ GOSUB 500 \ S_IN$ = S_OUT$ \ GOSUB 520 \ S_TY$ = S_OUT$ \ S_IN$ = S_DS$ \ GOSUB 500 \ S_DS$ = S_OUT$ \ S_IN$ = S_BD$ \ GOSUB 500 \ S_BD$ = S_OUT$
341 NUM_SEGS% = NUM_SEGS% + 1% \ SEG_PG%(NUM_SEGS%) = N_PG% \ SEG_TYPE$(NUM_SEGS%) = S_TY$
342 SEG_DESC$(NUM_SEGS%) = S_DS$ \ SEG_BODY$(NUM_SEGS%) = S_BD$
343 IF N_PG% > MAX_PG% THEN MAX_PG% = N_PG%
344 PRINT "[Added CDA Segment #"; NUM_SEGS%; " on Page "; N_PG%; ": "; S_TY$; " ("; S_DS$; ")]" \ GOTO 44
345 REM --- DELSEG <seg#> / DELETE <seg#> ---
346 D_ID% = VAL(ARG$)
347 IF D_ID% < 1% THEN GOTO 350
348 IF D_ID% > NUM_SEGS% THEN GOTO 350
349 GOTO 352
350 PRINT "%CDAVIEWER-E-INVSEG, Invalid segment number." \ GOTO 44
352 D_TY$ = SEG_TYPE$(D_ID%) \ D_DS$ = SEG_DESC$(D_ID%) \ I% = D_ID%
354 IF I% >= NUM_SEGS% THEN GOTO 360
356 SEG_PG%(I%) = SEG_PG%(I% + 1%) \ SEG_TYPE$(I%) = SEG_TYPE$(I% + 1%)
357 SEG_DESC$(I%) = SEG_DESC$(I% + 1%) \ SEG_BODY$(I%) = SEG_BODY$(I% + 1%)
358 I% = I% + 1% \ GOTO 354
360 NUM_SEGS% = NUM_SEGS% - 1%
362 PRINT "[Deleted CDA Segment #"; D_ID%; ": "; D_TY$; " ("; D_DS$; ")]"
364 GOTO 44
365 REM --- INSPECT / ANALYZE / CHECK ---
366 C_TXT% = 0% \ C_TBL% = 0% \ C_GFX% = 0% \ C_HDR% = 0% \ I% = 1%
368 IF I% > NUM_SEGS% THEN GOTO 382
370 UT$ = SEG_TYPE$(I%)
372 IF UT$ = "TEXT" THEN C_TXT% = C_TXT% + 1%
374 IF UT$ = "TABLE" THEN C_TBL% = C_TBL% + 1%
376 IF UT$ = "GRAPHIC" THEN C_GFX% = C_GFX% + 1%
378 IF UT$ = "HEADER" THEN C_HDR% = C_HDR% + 1%
379 IF UT$ = "FOOTER" THEN C_HDR% = C_HDR% + 1%
380 I% = I% + 1% \ GOTO 368
382 PRINT "=== CDA Compound Document Conformance Audit ==="
384 PRINT "  Document       : "; DOC_NAME$; " ("; DOC_FMT$; ")"
386 PRINT "  DOTS Packaging : "; DOC_DOTS$
388 PRINT "  Total Pages    : "; MAX_PG%; "  |  Total Segments: "; NUM_SEGS%
390 PRINT "  DDIF Text Segs : "; C_TXT%; "  |  Header/Footer : "; C_HDR%
392 PRINT "  DTIF Tables    : "; C_TBL%; "  |  ISL Graphics  : "; C_GFX%
394 CONF_ST$ = "CONFORMANT (ASN.1 TLV & DDIF/DTIF Descriptors Valid)"
396 IF NUM_SEGS% = 0% THEN CONF_ST$ = "EMPTY DOCUMENT"
398 PRINT "  Audit Result   : "; CONF_ST$
400 GOTO 44
405 REM --- SEARCH <keyword> / FIND <keyword> ---
406 IF ARG$ = "" THEN PRINT "%CDAVIEWER-E-SYNTAX, Usage: SEARCH <keyword>"
407 IF ARG$ = "" THEN GOTO 44
408 S_IN$ = ARG$ \ GOSUB 520 \ KW$ = S_OUT$ \ FOUND% = 0%
410 PRINT "=== CDA Search Results for '"; ARG$; "' ==="
412 I% = 1%
414 IF I% > NUM_SEGS% THEN GOTO 426
416 S_IN$ = SEG_TYPE$(I%) + SP1$ + SEG_DESC$(I%) + SP1$ + SEG_BODY$(I%) \ GOSUB 520 \ HAY$ = S_OUT$
418 IF INSTR(1%, HAY$, KW$) = 0% THEN GOTO 424
420 FOUND% = FOUND% + 1%
422 PRINT "  Seg #"; I%; " (Page "; SEG_PG%(I%); ") ["; SEG_TYPE$(I%); " | "; SEG_DESC$(I%); "]: "; SEG_BODY$(I%)
424 I% = I% + 1% \ GOTO 414
426 PRINT "Total matching segments: "; FOUND%
428 GOTO 44
430 REM --- FORMAT <fmt> ---
431 IF ARG$ = "" THEN PRINT "Current CDA Format: "; DOC_FMT$
432 IF ARG$ = "" THEN GOTO 44
434 DOC_FMT$ = ARG$
436 PRINT "[CDA Presentation Format set to: "; DOC_FMT$; "]"
438 GOTO 44
440 REM --- DISPLAY [ON <file>] / SCREEN / RENDER / EXPORT ---
441 OUT_FILE$ = "" \ S_IN$ = ARG$ \ GOSUB 520 \ UARG$ = S_OUT$
442 IF VERB$ = "EXPORT" THEN OUT_FILE$ = ARG$
443 IF LEFT$(UARG$, 3%) = "ON " THEN OUT_FILE$ = MID$(ARG$, 4%, LEN(ARG$) - 3%)
444 S_IN$ = OUT_FILE$ \ GOSUB 500 \ OUT_FILE$ = S_OUT$
446 GOSUB 600
448 IF OUT_FILE$ <> "" THEN PRINT "[CDA Viewer window exported to "; OUT_FILE$; "]"
450 GOTO 44
455 REM --- SAVE <file> ---
456 IF ARG$ = "" THEN PRINT "%CDAVIEWER-E-NOFILE, Specify filename for SAVE."
457 IF ARG$ = "" THEN GOTO 44
458 OPEN ARG$ FOR OUTPUT AS FILE #1%
459 S_IN$ = STR$(MAX_PG%) \ GOSUB 500 \ MP_S$ = S_OUT$
460 S_REC$ = "HDR" + PIPE$ + DOC_NAME$ + PIPE$ + DOC_FMT$ + PIPE$ + DOC_AUTH$ + PIPE$ + MP_S$
461 PRINT #1%, S_REC$ \ I% = 1%
464 IF I% > NUM_SEGS% THEN GOTO 469
465 S_IN$ = STR$(SEG_PG%(I%)) \ GOSUB 500 \ PG_S$ = S_OUT$
466 S_REC$ = "SEG" + PIPE$ + PG_S$ + PIPE$ + SEG_TYPE$(I%) + PIPE$ + SEG_DESC$(I%) + PIPE$ + SEG_BODY$(I%)
467 PRINT #1%, S_REC$ \ I% = I% + 1% \ GOTO 464
469 CLOSE #1%
470 PRINT "[Saved "; NUM_SEGS%; " CDA segments to "; ARG$; "]" \ GOTO 44
472 REM --- LOAD <file> ---
473 IF ARG$ = "" THEN PRINT "%CDAVIEWER-E-NOFILE, Specify filename for LOAD."
474 IF ARG$ = "" THEN GOTO 44
475 OPEN ARG$ FOR INPUT AS FILE #1%
476 NUM_SEGS% = 0% \ CUR_PG% = 1% \ MAX_PG% = 1%
477 LINE INPUT #1%, L_REC$
478 IF LEN(L_REC$) = 0% THEN GOTO 487
479 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 487
480 S_IN$ = L_REC$ \ GOSUB 500 \ L_REC$ = S_OUT$
482 IF LEFT$(L_REC$, 4%) = "HDR|" THEN GOSUB 660
484 IF LEFT$(L_REC$, 4%) = "SEG|" THEN GOSUB 680
485 GOTO 477
487 CLOSE #1%
488 PRINT "[Loaded "; NUM_SEGS%; " CDA segments from "; ARG$; " ("; DOC_NAME$; ")]" \ GOTO 44
490 REM --- CLEAR / RESET ---
492 NUM_SEGS% = 0% \ CUR_PG% = 1% \ MAX_PG% = 1% \ DOC_NAME$ = "UNTITLED.DDIF"
494 PRINT "[CDA document cleared]" \ GOTO 44
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
560 REM --- Subroutine: Render Page CUR_PG% to stdout ---
562 PRINT "=== CDA Page "; CUR_PG%; " of "; MAX_PG%; " : "; DOC_NAME$; " ("; DOC_FMT$; ") ==="
564 PG_CNT% = 0% \ P_I% = 1%
566 IF P_I% > NUM_SEGS% THEN GOTO 592
568 IF SEG_PG%(P_I%) <> CUR_PG% THEN GOTO 590
570 PG_CNT% = PG_CNT% + 1%
572 PRINT "  [Seg #"; P_I%; " | "; SEG_TYPE$(P_I%); " | "; SEG_DESC$(P_I%); "]"
574 IF SEG_TYPE$(P_I%) = "TABLE" THEN PRINT "  +----------------------------------------------------------------+"
576 IF SEG_TYPE$(P_I%) = "GRAPHIC" THEN PRINT "  +--- [ISL/Sixel Image Frame] ------------------------------------+"
578 PRINT "    "; SEG_BODY$(P_I%)
580 IF SEG_TYPE$(P_I%) = "TABLE" THEN PRINT "  +----------------------------------------------------------------+"
582 IF SEG_TYPE$(P_I%) = "GRAPHIC" THEN PRINT "  +----------------------------------------------------------------+"
590 P_I% = P_I% + 1% \ GOTO 566
592 IF PG_CNT% = 0% THEN PRINT "  (No compound segments on Page "; CUR_PG%; ")"
594 PRINT "======================================================================"
596 RETURN
600 REM --- Subroutine: Render Motif/XUI CDA Viewer Window ---
602 IF OUT_FILE$ <> "" THEN OPEN OUT_FILE$ FOR OUTPUT AS FILE #3%
603 B_L$ = "| " \ B_R$ = " |" \ W_BTN$ = " [v][^] |" \ W_DOT$ = " | DOTS: " \ W_SEG$ = " | Segs: "
604 L1$ = "+----------------------------------------------------------------------------+"
606 W_T$ = LEFT$(DOC_NAME$ + SP1$ + LBRK$ + DOC_FMT$ + RBRK$ + BLANKS$, 40%)
608 L2$ = "| [=] DECwindows CDA Viewer - " + W_T$ + W_BTN$
610 L3$ = "| File  View  Navigate  Inspect  Options  Help                               |"
612 S_IN$ = STR$(CUR_PG%) \ GOSUB 500 \ C_S$ = S_OUT$ \ S_IN$ = STR$(MAX_PG%) \ GOSUB 500 \ M_S$ = S_OUT$
616 PAD_OUT$ = LEFT$("Page: " + C_S$ + SLASH$ + M_S$ + W_DOT$ + DOC_DOTS$ + BLANKS$, 74%) \ L4$ = B_L$ + PAD_OUT$ + B_R$
618 W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = L2$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
620 W_LN$ = L3$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = L4$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
622 W_I% = 1%
624 IF W_I% > NUM_SEGS% THEN GOTO 638
626 IF SEG_PG%(W_I%) <> CUR_PG% THEN GOTO 636
628 S_IN$ = STR$(W_I%) \ GOSUB 500 \ SI_S$ = S_OUT$
630 PAD_OUT$ = LEFT$(LBRK$ + SEG_TYPE$(W_I%) + SP1$ + HASH$ + SI_S$ + RBRK$ + SP1$ + SEG_DESC$(W_I%) + BLANKS$, 74%) \ W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650
632 PAD_OUT$ = LEFT$(SP1$ + SP1$ + SEG_BODY$(W_I%) + BLANKS$, 74%) \ W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650
636 W_I% = W_I% + 1% \ GOTO 624
638 S_IN$ = STR$(NUM_SEGS%) \ GOSUB 500 \ NS_S$ = S_OUT$
640 PAD_OUT$ = LEFT$("Status: DDIF/DTIF Conformant | Author: " + DOC_AUTH$ + W_SEG$ + NS_S$ + BLANKS$, 74%)
642 W_LN$ = L1$ \ GOSUB 650 \ W_LN$ = B_L$ + PAD_OUT$ + B_R$ \ GOSUB 650 \ W_LN$ = L1$ \ GOSUB 650
644 IF OUT_FILE$ <> "" THEN CLOSE #3%
646 RETURN
650 IF OUT_FILE$ = "" THEN PRINT W_LN$
652 IF OUT_FILE$ <> "" THEN PRINT #3%, W_LN$
654 RETURN
660 REM --- Subroutine: Parse HDR|name|fmt|auth|maxpg ---
662 H_R$ = MID$(L_REC$, 5%, LEN(L_REC$) - 4%) \ H1% = INSTR(1%, H_R$, PIPE$)
663 IF H1% = 0% THEN GOTO 674
664 DOC_NAME$ = LEFT$(H_R$, H1% - 1%) \ H_R$ = MID$(H_R$, H1% + 1%, LEN(H_R$) - H1%) \ H2% = INSTR(1%, H_R$, PIPE$)
666 IF H2% = 0% THEN GOTO 674
668 DOC_FMT$ = LEFT$(H_R$, H2% - 1%) \ H_R$ = MID$(H_R$, H2% + 1%, LEN(H_R$) - H2%) \ H3% = INSTR(1%, H_R$, PIPE$)
670 IF H3% = 0% THEN GOTO 674
672 DOC_AUTH$ = LEFT$(H_R$, H3% - 1%) \ MAX_PG% = VAL(MID$(H_R$, H3% + 1%, LEN(H_R$) - H3%))
674 RETURN
680 REM --- Subroutine: Parse SEG|pg|type|desc|body ---
682 G_R$ = MID$(L_REC$, 5%, LEN(L_REC$) - 4%) \ G1% = INSTR(1%, G_R$, PIPE$)
683 IF G1% = 0% THEN GOTO 699
684 G_PG% = VAL(LEFT$(G_R$, G1% - 1%)) \ G_R$ = MID$(G_R$, G1% + 1%, LEN(G_R$) - G1%) \ G2% = INSTR(1%, G_R$, PIPE$)
686 IF G2% = 0% THEN GOTO 699
688 G_TY$ = LEFT$(G_R$, G2% - 1%) \ G_R$ = MID$(G_R$, G2% + 1%, LEN(G_R$) - G2%) \ G3% = INSTR(1%, G_R$, PIPE$)
690 IF G3% = 0% THEN GOTO 699
692 G_DS$ = LEFT$(G_R$, G3% - 1%) \ G_BD$ = MID$(G_R$, G3% + 1%, LEN(G_R$) - G3%)
694 NUM_SEGS% = NUM_SEGS% + 1% \ SEG_PG%(NUM_SEGS%) = G_PG% \ SEG_TYPE$(NUM_SEGS%) = G_TY$
696 SEG_DESC$(NUM_SEGS%) = G_DS$ \ SEG_BODY$(NUM_SEGS%) = G_BD$
698 IF G_PG% > MAX_PG% THEN MAX_PG% = G_PG%
699 RETURN
990 PRINT "DECwindows CDA Viewer V3.0 session terminated."
999 END
