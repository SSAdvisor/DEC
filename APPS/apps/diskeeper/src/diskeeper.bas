10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_FID$(15%) \ DIM R_FNAME$(15%) \ DIM R_DIR$(15%) \ DIM R_EXT%(15%)
20 NUM_REC% = 0% \ VOL_STAT$ = "FRAGMENTED" \ DB_FILE$ = "DISKEEP.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Executive Software DISKEEPER V4.0 - Online Disk Defragmenter" \ PRINT "    Executive Software, Inc. (Glendale, CA) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to scan volume, ANALYZE, DEFRAG, MAP, or EXIT." \ PRINT ""
100 PRINT "DISKEEPER> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "ANALYZE" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "DEFRAG" OR VERB$ = "CONSOLIDATE" THEN GOTO 980
370 IF VERB$ = "MAP" OR VERB$ = "BITMAP" THEN GOTO 1150
380 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
390 IF VERB$ = "SAVE" THEN GOTO 1550
400 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
420 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "DISKEEPER: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ VOL_STAT$ = "FRAGMENTED"
710 R_FID$(1%) = "FID-001" \ R_FNAME$(1%) = "INDEXF.SYS         " \ R_DIR$(1%) = "[000000]" \ R_EXT%(1%) = 14%
720 R_FID$(2%) = "FID-002" \ R_FNAME$(2%) = "BITMAP.SYS         " \ R_DIR$(2%) = "[000000]" \ R_EXT%(2%) = 4%
730 R_FID$(3%) = "FID-048" \ R_FNAME$(3%) = "ORADB_SYSTEM.DBF   " \ R_DIR$(3%) = "[ORACLE]" \ R_EXT%(3%) = 37%
740 R_FID$(4%) = "FID-092" \ R_FNAME$(4%) = "PAGEFILE.SYS       " \ R_DIR$(4%) = "[SYS0]  " \ R_EXT%(4%) = 22%
750 PRINT "[Sample ODS-2 Volume VAX01$DKA0: scanned - 4 INDEXF.SYS file headers]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 TOT_E% = 0% \ FRAG_C% = 0% \ LI% = 1%
840 PRINT EQU$ \ PRINT "  DISKEEPER V4.0 ODS-2 Volume Analysis — Volume: VAX01$DKA0: ("; VOL_STAT$; ")" \ PRINT SEP$
850 PRINT "  FID        File Specification     Directory   Extents   Status" \ PRINT SEP$
860 IF LI% > NUM_REC% THEN GOTO 940
870 TOT_E% = TOT_E% + R_EXT%(LI%) \ ST_S$ = "CONTIGUOUS"
880 IF R_EXT%(LI%) > 1% THEN ST_S$ = "EXCESSIVE "
890 IF R_EXT%(LI%) > 1% THEN FRAG_C% = FRAG_C% + 1%
900 F_P$ = LEFT$(R_FID$(LI%) + BLANKS$, 9%) \ N_P$ = LEFT$(R_FNAME$(LI%) + BLANKS$, 21%) \ D_P$ = LEFT$(R_DIR$(LI%) + BLANKS$, 9%)
910 PRINT "  "; F_P$; "  "; N_P$; "  "; D_P$; "   "; R_EXT%(LI%); "        "; ST_S$
920 LI% = LI% + 1% \ GOTO 860
940 PRINT SEP$ \ PRINT "  [DISKEEPER ANALYZE: "; FRAG_C%; " fragmented files | Total Extents = "; TOT_E%; "]" \ PRINT EQU$ \ GOTO 495
980 IF NUM_REC% = 0% THEN GOTO 3370
990 OLD_E% = 0% \ DI% = 1%
1000 IF DI% > NUM_REC% THEN GOTO 1040
1010 OLD_E% = OLD_E% + R_EXT%(DI%) \ R_EXT%(DI%) = 1%
1020 DI% = DI% + 1% \ GOTO 1000
1040 VOL_STAT$ = "OPTIMIZED" \ SAV_E% = OLD_E% - NUM_REC%
1050 PRINT EQU$ \ PRINT "  DISKEEPER V4.0 Online Extent Consolidation & Free-Space Compaction" \ PRINT SEP$
1060 PRINT "  Volume Target:        VAX01$DKA0: (RA90 1.2GB ODS-2 Volume)"
1070 PRINT "  Extents Before Run:   "; OLD_E%; " extents across "; NUM_REC%; " files"
1080 PRINT "  Extents After Run:    "; NUM_REC%; " contiguous extents (1 extent/file)"
1090 PRINT SEP$ \ PRINT "  [DISKEEPER DEFRAG Complete: "; SAV_E%; " excess extents eliminated | Volume=OPTIMIZED]" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_REC% = 0% THEN GOTO 3370
1160 PRINT EQU$ \ PRINT "  DISKEEPER V4.0 BITMAP.SYS LBN Allocation Map — VAX01$DKA0: ("; VOL_STAT$; ")" \ PRINT SEP$
1170 IF VOL_STAT$ = "OPTIMIZED" THEN GOTO 1210
1180 PRINT "  LBN 000000..049999: [IIII..BBBB...OOOO..PPPP...OOOO..IIII...PPPP..OOOO]"
1190 PRINT "  LBN 050000..099999: [..OOOO...PPPP..IIII....OOOO......PPPP...OOOO.....]"
1200 GOTO 1230
1210 PRINT "  LBN 000000..049999: [IIIIIIIIBBBBFFFFFFFFFFFFFFFFFFFFPPPPPPPPPPPPPPPPP]"
1220 PRINT "  LBN 050000..099999: [.................................................]"
1230 PRINT "  Legend: [I]=INDEXF.SYS  [B]=BITMAP.SYS  [O/F]=User Files  [P]=PAGEFILE  [.]=Free"
1240 PRINT SEP$ \ PRINT "  [DISKEEPER MAP Rendered: Volume State = "; VOL_STAT$; "]" \ PRINT EQU$ \ GOTO 495
1380 IF NUM_REC% >= 15% THEN GOTO 1510
1390 C1% = INSTR(1%, ARGS$, ",")
1400 IF C1% = 0% THEN GOTO 1500
1410 T_IN$ = LEFT$(ARGS$, C1% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ K_V$ = U_OUT$
1420 REM1$ = MID$(ARGS$, C1% + 1%, LEN(ARGS$) - C1%) \ C2% = INSTR(1%, REM1$, ",")
1430 IF C2% = 0% THEN GOTO 1500
1440 T_IN$ = LEFT$(REM1$, C2% - 1%) \ GOSUB 500 \ N_V$ = T_OUT$
1450 REM2$ = MID$(REM1$, C2% + 1%, LEN(REM1$) - C2%) \ C3% = INSTR(1%, REM2$, ",")
1460 IF C3% = 0% THEN GOTO 1500
1470 T_IN$ = LEFT$(REM2$, C3% - 1%) \ GOSUB 500 \ U_IN$ = T_OUT$ \ GOSUB 580 \ G_V$ = U_OUT$
1480 VL_V% = VAL(MID$(REM2$, C3% + 1%, LEN(REM2$) - C3%))
1490 NUM_REC% = NUM_REC% + 1% \ R_FID$(NUM_REC%) = K_V$ \ R_FNAME$(NUM_REC%) = N_V$ \ R_DIR$(NUM_REC%) = G_V$ \ R_EXT%(NUM_REC%) = VL_V%
1495 PRINT "[DISKEEPER File #"; NUM_REC%; " added: "; K_V$; " ("; N_V$; ", Extents="; VL_V%; ")]" \ GOTO 495
1500 PRINT "DISKEEPER: Syntax is ADD <fid>, <filename>, <dir>, <extents>" \ GOTO 495
1510 PRINT "DISKEEPER: File table full" \ GOTO 495
1550 IF NUM_REC% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_REC% THEN GOTO 1630
1600 PRINT #2%, R_FID$(SI%); "|"; R_FNAME$(SI%); "|"; R_DIR$(SI%); "|"; R_EXT%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_REC%; " DISKEEPER records saved to "; SV_FILE$; "]" \ GOTO 495
1700 LD_FILE$ = DB_FILE$
1710 IF ARGS$ <> "" THEN LD_FILE$ = ARGS$
1720 ON ERROR GOTO 1850 \ OPEN LD_FILE$ FOR INPUT AS FILE #2% \ NUM_REC% = 0%
1730 LINE INPUT #2%, T_LINE$ \ T_IN$ = T_LINE$ \ GOSUB 500
1740 IF T_OUT$ = "" THEN GOTO 1730
1750 P1% = INSTR(1%, T_OUT$, "|")
1760 IF P1% = 0% THEN GOTO 1730
1770 FK$ = LEFT$(T_OUT$, P1% - 1%) \ REM1$ = MID$(T_OUT$, P1% + 1%, LEN(T_OUT$) - P1%) \ P2% = INSTR(1%, REM1$, "|")
1780 IF P2% = 0% THEN GOTO 1730
1790 FN$ = LEFT$(REM1$, P2% - 1%) \ REM2$ = MID$(REM1$, P2% + 1%, LEN(REM1$) - P2%) \ P3% = INSTR(1%, REM2$, "|")
1800 IF P3% = 0% THEN GOTO 1730
1810 FG$ = LEFT$(REM2$, P3% - 1%) \ FV% = VAL(MID$(REM2$, P3% + 1%, LEN(REM2$) - P3%))
1820 NUM_REC% = NUM_REC% + 1% \ R_FID$(NUM_REC%) = FK$ \ R_FNAME$(NUM_REC%) = FN$ \ R_DIR$(NUM_REC%) = FG$ \ R_EXT%(NUM_REC%) = FV% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " DISKEEPER records loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Executive Software DISKEEPER V4.0 Status:" \ PRINT "  Volume / File:  VAX01$DKA0: / "; DB_FILE$; " (Files: "; NUM_REC%; ", State: "; VOL_STAT$; ")" \ GOTO 495
2050 NUM_REC% = 0% \ VOL_STAT$ = "FRAGMENTED" \ PRINT "[DISKEEPER volume table cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Executive Software DISKEEPER V4.0 Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Scan ODS-2 volume VAX01$DKA0: headers" \ PRINT "  ANALYZE / LIST                   Report file extent fragmentation"
3020 PRINT "  DEFRAG / CONSOLIDATE             Consolidate file extents online" \ PRINT "  MAP / BITMAP                     Display ASCII LBN volume allocation map"
3030 PRINT "  ADD <fid>, <name>, <dir>, <ext>  Add ODS-2 file entry to table" \ PRINT "  SAVE [file] / LOAD [file]        Save or load DISKEEP.DAT file"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear table, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "DISKEEPER: Volume table is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
