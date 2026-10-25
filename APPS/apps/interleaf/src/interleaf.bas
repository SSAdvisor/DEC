10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM C_ID$(15%) \ DIM C_TAG$(15%) \ DIM C_TITLE$(15%) \ DIM C_PGS%(15%)
20 NUM_CMP% = 0% \ BOOK_NAME$ = "VAX_TECH_MANUAL.BOOK" \ DB_FILE$ = "ILEAF.DOC"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Interleaf TPS 4.0 - Technical Publishing Software for VAXstation" \ PRINT "    Interleaf, Inc. (Cambridge, MA) - DEC VAX/VMS & DECwindows" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load book, DESKTOP, PROPS, FRAME, PAGINATE, LPPOST, or EXIT." \ PRINT ""
100 PRINT "TPS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "DESKTOP" OR VERB$ = "LIST" OR VERB$ = "CATALOG" THEN GOTO 820
360 IF VERB$ = "PROPS" OR VERB$ = "PROPERTIES" THEN GOTO 960
370 IF VERB$ = "FRAME" OR VERB$ = "DIAGRAM" THEN GOTO 1100
380 IF VERB$ = "PAGINATE" OR VERB$ = "COMPOSE" THEN GOTO 1210
390 IF VERB$ = "LPPOST" OR VERB$ = "POSTSCRIPT" THEN GOTO 1310
400 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
410 IF VERB$ = "SAVE" THEN GOTO 1550
420 IF VERB$ = "LOAD" OR VERB$ = "OPEN" THEN GOTO 1700
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "TPS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_CMP% = 4%
710 C_ID$(1%) = "CH-01" \ C_TAG$(1%) = "CHAPTER" \ C_TITLE$(1%) = "VAX 9000 System Architecture Overview" \ C_PGS%(1%) = 24%
720 C_ID$(2%) = "CH-02" \ C_TAG$(2%) = "DIAGRAM" \ C_TITLE$(2%) = "XMI Bus & Vector Processor Timing Frame" \ C_PGS%(2%) = 16%
730 C_ID$(3%) = "CH-03" \ C_TAG$(3%) = "SPEC-TBL" \ C_TITLE$(3%) = "Multi-Chip Unit Thermal Specifications" \ C_PGS%(3%) = 18%
740 C_ID$(4%) = "CH-04" \ C_TAG$(4%) = "INDEX" \ C_TITLE$(4%) = "Master Cross-Reference & Autonumber Index" \ C_PGS%(4%) = 8%
750 PRINT "[Sample Interleaf TPS 4.0 book container loaded - 4 components]" \ GOTO 495
820 IF NUM_CMP% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Interleaf TPS 4.0 Desktop — Book: "; BOOK_NAME$; " ("; DB_FILE$; ")" \ PRINT SEP$
840 PRINT "  ID      Component Tag   Pages   Document / Sub-Container Title" \ PRINT SEP$
850 LI% = 1% \ TOT_P% = 0%
860 IF LI% > NUM_CMP% THEN GOTO 920
870 I_P$ = LEFT$(C_ID$(LI%) + BLANKS$, 6%) \ T_P$ = LEFT$(C_TAG$(LI%) + BLANKS$, 14%) \ TOT_P% = TOT_P% + C_PGS%(LI%)
880 PRINT "  "; I_P$; "  "; T_P$; "  "; C_PGS%(LI%); "      "; C_TITLE$(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT SEP$ \ PRINT "  [Desktop Catalog: "; NUM_CMP%; " documents in Book | Total Composed Pages: "; TOT_P%; "]" \ PRINT EQU$ \ GOTO 495
960 IF NUM_CMP% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  Interleaf TPS Component Property Sheet — Master Style Catalog" \ PRINT SEP$
980 PRINT "  Font Family:   Bitstream Charter / Helvetica 10pt (Leading: 12pt)"
990 PRINT "  Page Grid:     8.5 x 11.0 in | 2-Column Technical Layout | Bleed: 0.25 in"
1000 PRINT "  Autonumber:    Stream <SecNum>.<FigNum> | Hyphenation: Knuth-Liang Active"
1010 PRINT "  [Property Sheet Verified for "; NUM_CMP%; " active component tags]" \ PRINT EQU$ \ GOTO 495
1100 IF NUM_CMP% = 0% THEN GOTO 3370
1110 PRINT EQU$ \ PRINT "  Interleaf TPS Anchored Micro-Document Frame Inspector" \ PRINT SEP$
1120 PRINT "  Frame #1 [Anchored to CH-02]: Vector Bezier Bus Timing (48 primitives, grouped)"
1130 PRINT "  Frame #2 [Anchored to CH-03]: Isometric MCU Heatsink CAD Callout (EPS import)"
1140 PRINT "  [Micro-Document Frame Check Complete: 2 vector graphics frames validated]" \ PRINT EQU$ \ GOTO 495
1210 IF NUM_CMP% = 0% THEN GOTO 3370
1220 PI% = 1% \ TOT_P% = 0%
1230 IF PI% > NUM_CMP% THEN GOTO 1260
1240 TOT_P% = TOT_P% + C_PGS%(PI%) \ PI% = PI% + 1% \ GOTO 1230
1260 PRINT EQU$ \ PRINT "  Interleaf TPS Book Pagination, Cross-Numbering & TOC Engine" \ PRINT SEP$
1270 PRINT "  Resolving autonumber streams, figure callouts, and widow/orphan constraints..."
1280 PRINT "  [Book Pagination Complete: "; NUM_CMP%; " chapters composed across "; TOT_P%; " pages | TOC updated]" \ PRINT EQU$ \ GOTO 495
1310 IF NUM_CMP% = 0% THEN GOTO 3370
1320 PI% = 1% \ TOT_P% = 0%
1330 IF PI% > NUM_CMP% THEN GOTO 1360
1340 TOT_P% = TOT_P% + C_PGS%(PI%) \ PI% = PI% + 1% \ GOTO 1330
1360 PRINT EQU$ \ PRINT "  Interleaf LPPOST PostScript Level 1 Driver — Target: DEC PrintServer 40" \ PRINT SEP$
1370 PRINT "  [LPPOST Spooler Complete: "; TOT_P%; " PostScript pages emitted to ILEAF_OUT.PS]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_CMP% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ K_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ TG_V$ = U_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ TI_V$ = T_OUT$
1480 PG_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_CMP% = NUM_CMP% + 1% \ C_ID$(NUM_CMP%) = K_V$ \ C_TAG$(NUM_CMP%) = TG_V$ \ C_TITLE$(NUM_CMP%) = TI_V$ \ C_PGS%(NUM_CMP%) = PG_V%
1495 PRINT "[Interleaf Component #"; NUM_CMP%; " added: "; K_V$; " ("; TG_V$; ", Pages="; PG_V%; ")]" \ GOTO 495
1500 PRINT "TPS: Syntax is ADD <id>, <tag>, <title>, <pages>" \ GOTO 495
1510 PRINT "TPS: Book container full" \ GOTO 495
1550 IF NUM_CMP% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_CMP% THEN GOTO 1630
1600 PRINT #2%, C_ID$(SI%); "|"; C_TAG$(SI%); "|"; C_TITLE$(SI%); "|"; C_PGS%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_CMP%; " Interleaf TPS components saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_CMP% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FK$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FTG$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FTI$ = LEFT$(REM2$, P3% - 1%) \ FPG% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_CMP% = NUM_CMP% + 1% \ C_ID$(NUM_CMP%) = FK$ \ C_TAG$(NUM_CMP%) = FTG$ \ C_TITLE$(NUM_CMP%) = FTI$ \ C_PGS%(NUM_CMP%) = FPG% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_CMP%; " Interleaf TPS components loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Interleaf TPS 4.0 Technical Publishing Status:" \ PRINT "  Active Book:    "; BOOK_NAME$; " (File: "; DB_FILE$; ", Components: "; NUM_CMP%; ")" \ GOTO 495
2050 NUM_CMP% = 0% \ PRINT "[Interleaf TPS book container cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Interleaf TPS 4.0 Technical Publishing Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample technical manual book" \ PRINT "  DESKTOP / LIST                   Display Desktop/Book/Document catalog"
3020 PRINT "  PROPS / FRAME                    Inspect component properties or vector frames" \ PRINT "  PAGINATE / LPPOST                Run cross-numbering/TOC or PostScript output"
3030 PRINT "  ADD <id>, <tag>, <title>, <pgs>  Add document component to book" \ PRINT "  SAVE [file] / LOAD [file]        Save or load ILEAF.DOC container"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear desktop, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "TPS: Desktop book container is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
