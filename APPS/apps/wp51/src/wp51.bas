10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM P_ID$(15%) \ DIM P_STY$(15%) \ DIM P_TXT$(15%) \ DIM P_WRD%(15%)
20 NUM_PAR% = 0% \ DOC_REV$ = "5.1-VMS" \ DB_FILE$ = "WP51DOC.WPD"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    WordPerfect 5.1 for VAX/VMS - Multi-User Document Processing System" \ PRINT "    WordPerfect Corporation (Orem, UT) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load doc, REVEAL, SPELL, THESAURUS, MERGE, or EXIT." \ PRINT ""
100 PRINT "WP51> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "LIST" OR VERB$ = "DIR" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "REVEAL" OR VERB$ = "CODES" THEN GOTO 960
370 IF VERB$ = "SPELL" OR VERB$ = "SPELLER" THEN GOTO 1120
380 IF VERB$ = "THESAURUS" OR VERB$ = "THES" THEN GOTO 1220
390 IF VERB$ = "MERGE" OR VERB$ = "MAILMERGE" THEN GOTO 1300
400 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
410 IF VERB$ = "SAVE" THEN GOTO 1550
420 IF VERB$ = "LOAD" OR VERB$ = "RETRIEVE" THEN GOTO 1700
430 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
440 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "WP51: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_PAR% = 4%
710 P_ID$(1%) = "P-01" \ P_STY$(1%) = "HEADING" \ P_TXT$(1%) = "DEC VAXcluster Operations Executive Memo" \ P_WRD%(1%) = 42%
720 P_ID$(2%) = "P-02" \ P_STY$(2%) = "BODY" \ P_TXT$(2%) = "Quarterly RMS journaling and shadow set status." \ P_WRD%(2%) = 118%
730 P_ID$(3%) = "P-03" \ P_STY$(3%) = "TABLE" \ P_TXT$(3%) = "Node VAX8800 SLA uptime exceeded 99.94 percent." \ P_WRD%(3%) = 85%
740 P_ID$(4%) = "P-04" \ P_STY$(4%) = "FOOTER" \ P_TXT$(4%) = "Approved for LN03 PostScript distribution." \ P_WRD%(4%) = 35%
750 PRINT "[Sample WordPerfect 5.1 document loaded - 4 paragraphs]" \ GOTO 495
820 IF NUM_PAR% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  WordPerfect 5.1 Document 1 — File: "; DB_FILE$; " (Format: "; DOC_REV$; ")" \ PRINT SEP$
840 PRINT "  Para   Style     Words   Document Text Excerpt" \ PRINT SEP$
850 LI% = 1% \ TOT_W% = 0%
860 IF LI% > NUM_PAR% THEN GOTO 920
870 I_P$ = LEFT$(P_ID$(LI%) + BLANKS$, 5%) \ S_P$ = LEFT$(P_STY$(LI%) + BLANKS$, 8%) \ TOT_W% = TOT_W% + P_WRD%(LI%)
880 PRINT "  "; I_P$; "  "; S_P$; "  "; P_WRD%(LI%); "     "; P_TXT$(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT SEP$ \ PRINT "  Doc 1 Pg 1 Ln 1.0"; CHR$(34%); " Pos 1.0"; CHR$(34%); " | Total Paragraphs: "; NUM_PAR%; " | Total Words: "; TOT_W% \ PRINT EQU$ \ GOTO 495
960 IF NUM_PAR% = 0% THEN GOTO 3370
970 PRINT EQU$ \ PRINT "  WordPerfect 5.1 Reveal Codes (Alt-F3) — [Margin Set:10,70][Just:Full][HZone:10%,4%]" \ PRINT SEP$
980 RI% = 1%
990 IF RI% > NUM_PAR% THEN GOTO 1050
1000 PRINT "  "; P_ID$(RI%); ": [Style On:"; P_STY$(RI%); "][Bold:On]"; P_TXT$(RI%); "[Bold:Off][SRt][HRt]"
1010 RI% = RI% + 1% \ GOTO 990
1050 PRINT SEP$ \ PRINT "  [Reveal Codes Active: "; NUM_PAR%; " blocks inspected | Press Alt-F3 to restore window]" \ PRINT EQU$ \ GOTO 495
1120 IF NUM_PAR% = 0% THEN GOTO 3370
1130 SI% = 1% \ TOT_W% = 0%
1140 IF SI% > NUM_PAR% THEN GOTO 1170
1150 TOT_W% = TOT_W% + P_WRD%(SI%) \ SI% = SI% + 1% \ GOTO 1140
1170 PRINT EQU$ \ PRINT "  WordPerfect 5.1 Speller (Ctrl-F2) — Dictionary: WP{WP}US.LEX (115,000 words)" \ PRINT SEP$
1180 PRINT "  Scanning "; NUM_PAR%; " paragraphs ("; TOT_W%; " total words) + Supplemental VMS Technical Lexicon..."
1190 PRINT "  [Speller Complete: "; TOT_W%; " words verified, 0 misspellings, 2 technical acronyms skipped]" \ PRINT EQU$ \ GOTO 495
1220 Q_WRD$ = "SYSTEM"
1230 IF ARGS$ <> "" THEN U_IN$ = ARGS$
1240 IF ARGS$ <> "" THEN GOSUB 580
1250 IF ARGS$ <> "" THEN Q_WRD$ = U_OUT$
1260 PRINT EQU$ \ PRINT "  WordPerfect 5.1 Thesaurus (Alt-F1) — Headword Lookup: "; Q_WRD$ \ PRINT SEP$
1270 PRINT "  (n)  1. architecture, complex, configuration, network, VAXcluster"
1280 PRINT "  (n)  2. methodology, organization, procedure, regimen [Ant: chaos]"
1290 PRINT "  [Thesaurus Lookup Complete: 8 synonyms and 1 antonym found for "; Q_WRD$; "]" \ PRINT EQU$ \ GOTO 495
1300 IF NUM_PAR% = 0% THEN GOTO 3370
1310 PRINT EQU$ \ PRINT "  WordPerfect 5.1 Mail-Merge (Shift-F9) — Primary: "; DB_FILE$; " + Secondary: VMSNODES.SFD" \ PRINT SEP$
1320 PRINT "  Merging Record #1 (^F1^=Maynard HQ, ^F2^=VAX 9000)... [Page Break ^E]"
1330 PRINT "  Merging Record #2 (^F1^=Salem Plant, ^F2^=VAX 6000)... [Page Break ^E]"
1340 PRINT "  Merging Record #3 (^F1^=Marlboro Lab, ^F2^=VAXstation 3100)... [EOF]"
1350 PRINT "  [WP51 Mail-Merge Complete: 3 customized documents generated ("; NUM_PAR%; " paragraphs each)]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_PAR% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ K_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ S_V$ = U_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ TX_V$ = T_OUT$
1480 WD_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_PAR% = NUM_PAR% + 1% \ P_ID$(NUM_PAR%) = K_V$ \ P_STY$(NUM_PAR%) = S_V$ \ P_TXT$(NUM_PAR%) = TX_V$ \ P_WRD%(NUM_PAR%) = WD_V%
1495 PRINT "[WP51 Paragraph #"; NUM_PAR%; " added: "; K_V$; " ("; S_V$; ", Words="; WD_V%; ")]" \ GOTO 495
1500 PRINT "WP51: Syntax is ADD <id>, <style>, <text>, <words>" \ GOTO 495
1510 PRINT "WP51: Document buffer full" \ GOTO 495
1550 IF NUM_PAR% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_PAR% THEN GOTO 1630
1600 PRINT #2%, P_ID$(SI%); "|"; P_STY$(SI%); "|"; P_TXT$(SI%); "|"; P_WRD%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_PAR%; " WP51 paragraphs saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_PAR% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FK$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FS$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FT$ = LEFT$(REM2$, P3% - 1%) \ FW% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_PAR% = NUM_PAR% + 1% \ P_ID$(NUM_PAR%) = FK$ \ P_STY$(NUM_PAR%) = FS$ \ P_TXT$(NUM_PAR%) = FT$ \ P_WRD%(NUM_PAR%) = FW% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_PAR%; " WP51 paragraphs loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "WordPerfect 5.1 for VAX/VMS Status:" \ PRINT "  Active File:    "; DB_FILE$; " (Paragraphs: "; NUM_PAR%; ", Format: "; DOC_REV$; ")" \ GOTO 495
2050 NUM_PAR% = 0% \ PRINT "[WP51 document buffer cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    WordPerfect 5.1 for VAX/VMS Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample WP51 document" \ PRINT "  LIST / DIR                       Display document paragraphs & word count"
3020 PRINT "  REVEAL / CODES                   Show WordPerfect Reveal Codes (Alt-F3)" \ PRINT "  SPELL / THESAURUS [word]         Run 115,000-word Speller or Thesaurus"
3030 PRINT "  MERGE                            Execute Primary/Secondary Mail-Merge" \ PRINT "  ADD <id>, <style>, <txt>, <wds>  Append paragraph to document"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or retrieve WP51DOC.WPD file" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear doc, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "WP51: Document buffer is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
