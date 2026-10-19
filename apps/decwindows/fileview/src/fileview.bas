10 REM =========================================================================
20 REM DECwindows FileView V3.0 (VUE$MASTER / fileview / dxfileview)
30 REM Workstation Graphical File Manager, RMS Browser & DCL Verb Launcher
40 REM Digital Equipment Corporation - VAX/VMS, ULTRIX & DEC OSF/1 (1988-1993)
50 REM =========================================================================
60 DIM FV_DIR$(60%) \ DIM FV_NAME$(60%) \ DIM FV_VER%(60%) \ DIM FV_BLK%(60%)
70 DIM FV_ORG$(60%) \ DIM FV_PROT$(60%) \ DIM FV_DATE$(60%) \ DIM FV_BODY$(60%)
80 DIM CMD_Q$(30%) \ DIM FLD_P$(15%)
90 PIPE$ = "|" \ COLON$ = ":" \ SEMI$ = ";" \ LBRK$ = "[" \ RBRK$ = "]" \ SP1$ = " "
100 FILE_CNT% = 0% \ CUR_FILE% = 0% \ CUR_DIR$ = "SYS$SYSROOT:[SYSMGR]" \ CUR_FLT$ = "*.*"
110 PRT_CH% = 0% \ BANNER_SHOWN% = 0% \ CMD_LINE$ = COMMAND$
120 IF LEN(CMD_LINE$) > 0% THEN GOTO 240
150 PRINT "=============================================================================="
160 PRINT " DECwindows FileView V3.0 (VUE$MASTER - Workstation File & DCL Manager)"
170 PRINT " Digital Equipment Corporation - VAX/VMS & DEC OSF/1 Workstation Desktop"
180 PRINT "=============================================================================="
190 PRINT "Type HELP for commands, SAMPLE to load VMS workstation files, EXIT to quit."
200 BANNER_SHOWN% = 1%
210 PRINT ""
220 LINE INPUT "FileView> "; RAW_LINE$
230 IF LEN(RAW_LINE$) = 0% THEN GOTO 210
240 IF BANNER_SHOWN% = 0% THEN RAW_LINE$ = CMD_LINE$
250 GOSUB 3310 \ Q_IDX% = 1%
270 IF Q_IDX% > Q_CNT% THEN GOTO 320
280 ONE_CMD$ = CMD_Q$( Q_IDX% ) \ GOSUB 350 \ Q_IDX% = Q_IDX% + 1% \ GOTO 270
320 IF BANNER_SHOWN% = 0% THEN GOTO 4500
330 GOTO 210
350 C_STR$ = ONE_CMD$ \ GOSUB 3520
370 IF LEN(C_STR$) = 0% THEN GOTO 1040
380 SP_POS% = INSTR(1%, C_STR$, " ")
390 IF SP_POS% = 0% THEN VERB$ = C_STR$
400 IF SP_POS% = 0% THEN ARG$ = ""
410 IF SP_POS% > 0% THEN VERB$ = LEFT$(C_STR$, SP_POS% - 1%)
420 IF SP_POS% > 0% THEN ARG$ = MID$(C_STR$, SP_POS% + 1%, LEN(C_STR$))
430 U_IN$ = VERB$ \ GOSUB 3620 \ VERB$ = U_OUT$
440 C_STR$ = ARG$ \ GOSUB 3520 \ ARG$ = C_STR$
450 U_IN$ = ARG$ \ GOSUB 3620 \ UARG$ = U_OUT$
460 IF VERB$ = "EXIT" OR VERB$ = "QUIT" THEN GOTO 4500
470 IF VERB$ = "HELP" THEN GOTO 1050
480 IF VERB$ = "SAMPLE" THEN GOTO 1270
490 IF VERB$ = "SHOW" OR VERB$ = "STATUS" OR VERB$ = "PWD" THEN GOTO 1540
500 IF VERB$ = "CD" OR VERB$ = "SETDEF" THEN GOTO 1670
510 IF VERB$ = "FILTER" THEN GOTO 1740
520 IF VERB$ = "DIR" OR VERB$ = "LIST" OR VERB$ = "LS" THEN GOTO 1800
530 IF VERB$ = "TYPE" OR VERB$ = "VIEW" OR VERB$ = "READ" THEN GOTO 2040
540 IF VERB$ = "CREATE" OR VERB$ = "NEWFILE" THEN GOTO 2200
550 IF VERB$ = "COPY" THEN GOTO 2420
560 IF VERB$ = "RENAME" THEN GOTO 2600
570 IF VERB$ = "DELETE" THEN GOTO 2730
580 IF VERB$ = "PURGE" THEN GOTO 2860
590 IF VERB$ = "PROTECT" OR VERB$ = "SETPROT" THEN GOTO 3020
600 IF VERB$ = "RUN" OR VERB$ = "SUBMIT" OR VERB$ = "DCL" THEN GOTO 3150
610 IF VERB$ = "SEARCH" OR VERB$ = "FIND" THEN GOTO 3850
620 IF VERB$ = "DISPLAY" OR VERB$ = "RENDER" THEN GOTO 4130
630 IF VERB$ = "EXPORT" THEN GOTO 4150
640 IF VERB$ = "PRINT" THEN GOTO 4120
650 IF VERB$ = "SAVE" THEN GOTO 4320
660 IF VERB$ = "LOAD" THEN GOTO 4400
670 IF VERB$ = "CLEAR" THEN GOTO 1230
720 PRINT "%FILEVIEW-E-INVCMD, unrecognized command: "; VERB$
1040 RETURN
1050 PRINT "--- DECwindows FileView V3.0 (VUE$MASTER) Commands ---"
1070 PRINT "  SAMPLE                             Load 1991 VAX/VMS & Alpha AXP file catalog"
1080 PRINT "  SHOW / STATUS / PWD                Display active directory, filter, and stats"
1090 PRINT "  CD <dir> / SETDEF <dir>            Set default directory (or ALL)"
1100 PRINT "  FILTER <pattern>                   Set filename filter (*.*, *.COM, *.EXE)"
1110 PRINT "  DIR / LIST / LS                    List files in active directory"
1120 PRINT "  TYPE <n> / VIEW <n>                Inspect RMS attributes and contents of #n"
1130 PRINT "  CREATE <name>|<blk>|<org>|<body>   Create file (auto-increments VMS ;version)"
1140 PRINT "  COPY <n> <newname>                 Copy file #n to <newname>"
1150 PRINT "  RENAME <n> <newname>               Rename file #n"
1160 PRINT "  DELETE <n> / PURGE                 Delete file #n / Purge old VMS file versions"
1170 PRINT "  PROTECT <n> <prot>                 Set VMS UIC protection mask on file #n"
1180 PRINT "  RUN <n> / DCL <command>            Execute .COM/.EXE file #n or DCL command"
1190 PRINT "  SEARCH <keyword>                   Search filenames and file contents"
1200 PRINT "  DISPLAY / PRINT ON <file>          Render Motif/XUI FileView desktop window"
1210 PRINT "  SAVE <file> / LOAD <file>          Save or load FileView catalog (.fvw)"
1220 PRINT "  CLEAR / HELP / EXIT                Reset catalog, show help, or quit"
1225 RETURN
1230 FILE_CNT% = 0% \ CUR_FILE% = 0% \ CUR_DIR$ = "SYS$SYSROOT:[SYSMGR]" \ CUR_FLT$ = "*.*"
1250 PRINT "%FILEVIEW-I-CLEARED, FileView workspace catalog cleared."
1260 RETURN
1270 FILE_CNT% = 7% \ CUR_FILE% = 1% \ CUR_DIR$ = "SYS$SYSROOT:[SYSMGR]" \ CUR_FLT$ = "*.*"
1280 FV_DIR$( 1% ) = "SYS$SYSROOT:[SYSMGR]" \ FV_NAME$( 1% ) = "SYSTARTUP_V5.COM" \ FV_VER%( 1% ) = 4% \ FV_BLK%( 1% ) = 18%
1290 FV_ORG$( 1% ) = "SEQ/VAR" \ FV_PROT$( 1% ) = "(S:RWED,O:RWED,G:RE,W:)" \ FV_DATE$( 1% ) = "19-OCT-1991 07:00"
1300 FV_BODY$( 1% ) = "$! VAX/VMS V5.5 Site-Specific Startup -- Start DECnet & DECwindows XUI/Motif"
1310 FV_DIR$( 2% ) = "SYS$SYSROOT:[SYSMGR]" \ FV_NAME$( 2% ) = "LOGIN.COM" \ FV_VER%( 2% ) = 1% \ FV_BLK%( 2% ) = 4%
1320 FV_ORG$( 2% ) = "SEQ/VAR" \ FV_PROT$( 2% ) = "(S:RWED,O:RWED,G:,W:)" \ FV_DATE$( 2% ) = "14-OCT-1991 08:10"
1330 FV_BODY$( 2% ) = "$! Legacy operator login script (superseded by version ;2)"
1340 FV_DIR$( 3% ) = "SYS$SYSROOT:[SYSMGR]" \ FV_NAME$( 3% ) = "LOGIN.COM" \ FV_VER%( 3% ) = 2% \ FV_BLK%( 3% ) = 6%
1350 FV_ORG$( 3% ) = "SEQ/VAR" \ FV_PROT$( 3% ) = "(S:RWED,O:RWED,G:R,W:)" \ FV_DATE$( 3% ) = "19-OCT-1991 08:45"
1360 FV_BODY$( 3% ) = "$ SET TERMINAL/INQUIRE /DEC_CRT ! Launch VUE$MASTER FileView Session"
1370 FV_DIR$( 4% ) = "SYS$SYSROOT:[SYSMGR]" \ FV_NAME$( 4% ) = "SYLOGICALS.COM" \ FV_VER%( 4% ) = 3% \ FV_BLK%( 4% ) = 12%
1380 FV_ORG$( 4% ) = "SEQ/VAR" \ FV_PROT$( 4% ) = "(S:RWED,O:RWED,G:RE,W:R)" \ FV_DATE$( 4% ) = "18-OCT-1991 11:20"
1390 FV_BODY$( 4% ) = "$ DEFINE/SYSTEM DECW$BOOKSYSDIR DISK$DOC:[DECW$BOOK]"
1400 FV_DIR$( 5% ) = "SYS$COMMON:[SYSEXE]" \ FV_NAME$( 5% ) = "DECW$SERVER.EXE" \ FV_VER%( 5% ) = 1% \ FV_BLK%( 5% ) = 1420%
1410 FV_ORG$( 5% ) = "EXE/IMG" \ FV_PROT$( 5% ) = "(S:RWED,O:RWED,G:RE,W:E)" \ FV_DATE$( 5% ) = "15-OCT-1991 16:00"
1420 FV_BODY$( 5% ) = "[VAX/VMS Shareable Image: DECwindows X11R4 Display Server SPX/GPX]"
1430 FV_DIR$( 6% ) = "SYS$COMMON:[SYSEXE]" \ FV_NAME$( 6% ) = "RIGHTSLIST.DAT" \ FV_VER%( 6% ) = 1% \ FV_BLK%( 6% ) = 64%
1440 FV_ORG$( 6% ) = "IDX/KEY" \ FV_PROT$( 6% ) = "(S:RWED,O:RWED,G:,W:)" \ FV_DATE$( 6% ) = "12-OCT-1991 09:00"
1450 FV_BODY$( 6% ) = "[RMS Indexed File: System Rights Database - Key 0: Identifier]"
1460 FV_DIR$( 7% ) = "DISK$USER:[CONKLIN.AXP]" \ FV_NAME$( 7% ) = "EV4_PALCODE.MAR" \ FV_VER%( 7% ) = 5% \ FV_BLK%( 7% ) = 85%
1470 FV_ORG$( 7% ) = "SEQ/VAR" \ FV_PROT$( 7% ) = "(S:RWED,O:RWED,G:RE,W:)" \ FV_DATE$( 7% ) = "19-OCT-1991 10:30"
1480 FV_BODY$( 7% ) = ".TITLE EV4_PALCODE - Alpha 21064 Privileged Architecture Library"
1508 PRINT "%FILEVIEW-I-SAMPLE, loaded 7 VMS files across 3 directories into FileView."
1509 RETURN
1540 TOT_BLK% = 0% \ SI% = 1%
1550 IF SI% > FILE_CNT% THEN GOTO 1590
1560 TOT_BLK% = TOT_BLK% + FV_BLK%( SI% ) \ SI% = SI% + 1% \ GOTO 1550
1590 PRINT "--- DECwindows FileView Workspace Status ---"
1600 PRINT "  Default Dir  : "; CUR_DIR$
1610 PRINT "  File Filter  : "; CUR_FLT$
1620 PRINT "  Total Files  : "; FILE_CNT%; " (Total Disk Blocks: "; TOT_BLK%; ")"
1630 PRINT "  Selected File: #"; CUR_FILE%
1640 RETURN
1670 IF LEN(UARG$) = 0% THEN PRINT "%FILEVIEW-E-NODIR, specify directory specification (or ALL)."
1680 IF LEN(UARG$) = 0% THEN GOTO 1730
1690 CUR_DIR$ = UARG$
1700 PRINT "%FILEVIEW-I-SETDEF, default directory set to "; CUR_DIR$; "."
1730 RETURN
1740 IF LEN(UARG$) = 0% THEN CUR_FLT$ = "*.*"
1750 IF LEN(UARG$) > 0% THEN CUR_FLT$ = UARG$
1760 PRINT "%FILEVIEW-I-FILTER, file filter set to "; CUR_FLT$; "."
1770 RETURN
1800 TARGET_D$ = CUR_DIR$
1810 IF LEN(UARG$) > 0% THEN TARGET_D$ = UARG$
1820 PRINT "=== DECwindows FileView Directory: "; TARGET_D$; " (Filter: "; CUR_FLT$; ") ==="
1830 PRINT "  #   File;Ver                 Blocks  RMS Org   Revised Date       Protection"
1840 PRINT "  -----------------------------------------------------------------------------"
1850 FOUND_F% = 0% \ DIR_BLK% = 0% \ DI% = 1% \ PAD24$ = "                        "
1860 IF DI% > FILE_CNT% THEN GOTO 2000
1870 MATCH_D% = 0%
1880 IF TARGET_D$ = "ALL" THEN MATCH_D% = 1%
1890 IF FV_DIR$( DI% ) = TARGET_D$ THEN MATCH_D% = 1%
1900 IF MATCH_D% = 0% THEN GOTO 1990
1910 IF CUR_FLT$ = "*.*" THEN GOTO 1950
1920 EXT_S$ = CUR_FLT$
1930 IF LEFT$(EXT_S$, 1%) = "*" THEN EXT_S$ = MID$(EXT_S$, 2%, LEN(EXT_S$))
1940 IF INSTR(1%, FV_NAME$( DI% ), EXT_S$) = 0% THEN GOTO 1990
1950 FOUND_F% = FOUND_F% + 1% \ DIR_BLK% = DIR_BLK% + FV_BLK%( DI% )
1960 V_STR$ = STR$(FV_VER%( DI% )) \ C_STR$ = V_STR$ \ GOSUB 3520 \ V_STR$ = C_STR$
1970 FN_V$ = FV_NAME$( DI% ) + SEMI$ + V_STR$ \ T_S$ = FN_V$ + PAD24$ \ FN_COL$ = LEFT$(T_S$, 23%)
1975 B_STR$ = STR$(FV_BLK%( DI% )) + PAD24$ \ B_COL$ = LEFT$(B_STR$, 7%)
1980 PRINT " "; DI%; "  "; FN_COL$; " "; B_COL$; " "; FV_ORG$( DI% ); "   "; FV_DATE$( DI% ); "  "; FV_PROT$( DI% )
1990 DI% = DI% + 1% \ GOTO 1860
2000 IF FOUND_F% = 0% THEN PRINT "  %FILEVIEW-W-NOFILES, no files found matching filter."
2010 PRINT "  -----------------------------------------------------------------------------"
2020 PRINT "  Total of "; FOUND_F%; " file(s), "; DIR_BLK%; " block(s)."
2030 RETURN
2040 T_ID% = CUR_FILE%
2050 IF LEN(ARG$) > 0% THEN T_ID% = VAL(ARG$)
2060 IF T_ID% < 1% OR T_ID% > FILE_CNT% THEN PRINT "%FILEVIEW-E-INVFILE, file number out of range (1.."; FILE_CNT%; ")"
2070 IF T_ID% < 1% OR T_ID% > FILE_CNT% THEN GOTO 2190
2080 CUR_FILE% = T_ID%
2090 V_STR$ = STR$(FV_VER%( T_ID% )) \ C_STR$ = V_STR$ \ GOSUB 3520 \ V_STR$ = C_STR$
2100 PRINT "=============================================================================="
2110 PRINT " File #"; T_ID%; ": "; FV_DIR$( T_ID% ); FV_NAME$( T_ID% ); ";"; V_STR$
2120 PRINT " RMS Organization: "; FV_ORG$( T_ID% ); "   Size: "; FV_BLK%( T_ID% ); " blocks   Revised: "; FV_DATE$( T_ID% )
2130 PRINT " UIC Protection  : "; FV_PROT$( T_ID% )
2140 PRINT "------------------------------------------------------------------------------"
2150 PRINT " "; FV_BODY$( T_ID% )
2160 PRINT "=============================================================================="
2190 RETURN
2200 P_LINE$ = ARG$ \ GOSUB 3410
2210 IF P_CNT% < 4% THEN PRINT "%FILEVIEW-E-SYNTAX, usage: CREATE <name>|<blocks>|<org>|<content>"
2220 IF P_CNT% < 4% THEN GOTO 2410
2230 U_IN$ = FLD_P$( 1% ) \ GOSUB 3620 \ NEW_NM$ = U_OUT$
2240 MAX_V% = 0% \ VI% = 1%
2250 IF VI% > FILE_CNT% THEN GOTO 2300
2260 IF FV_DIR$( VI% ) = CUR_DIR$ AND FV_NAME$( VI% ) = NEW_NM$ AND FV_VER%( VI% ) > MAX_V% THEN MAX_V% = FV_VER%( VI% )
2280 VI% = VI% + 1% \ GOTO 2250
2300 FILE_CNT% = FILE_CNT% + 1% \ FV_DIR$( FILE_CNT% ) = CUR_DIR$ \ FV_NAME$( FILE_CNT% ) = NEW_NM$
2310 FV_VER%( FILE_CNT% ) = MAX_V% + 1% \ FV_BLK%( FILE_CNT% ) = VAL(FLD_P$( 2% ))
2320 IF FV_BLK%( FILE_CNT% ) < 1% THEN FV_BLK%( FILE_CNT% ) = 1%
2330 U_IN$ = FLD_P$( 3% ) \ GOSUB 3620 \ FV_ORG$( FILE_CNT% ) = U_OUT$
2340 FV_PROT$( FILE_CNT% ) = "(S:RWED,O:RWED,G:RE,W:)" \ FV_DATE$( FILE_CNT% ) = "19-OCT-1991 15:00"
2350 FV_BODY$( FILE_CNT% ) = FLD_P$( 4% ) \ CUR_FILE% = FILE_CNT%
2360 V_STR$ = STR$(FV_VER%( FILE_CNT% )) \ C_STR$ = V_STR$ \ GOSUB 3520 \ V_STR$ = C_STR$
2370 PRINT "%FILEVIEW-I-CREATED, created "; CUR_DIR$; NEW_NM$; ";"; V_STR$; " ("; FV_BLK%( FILE_CNT% ); " blocks)."
2410 RETURN
2420 SP_C% = INSTR(1%, UARG$, " ")
2430 IF SP_C% = 0% THEN PRINT "%FILEVIEW-E-SYNTAX, usage: COPY <n> <newname>"
2440 IF SP_C% = 0% THEN GOTO 2590
2450 CP_N% = VAL(LEFT$(UARG$, SP_C% - 1%)) \ CP_NM$ = MID$(UARG$, SP_C% + 1%, LEN(UARG$))
2460 C_STR$ = CP_NM$ \ GOSUB 3520 \ CP_NM$ = C_STR$
2470 IF CP_N% < 1% OR CP_N% > FILE_CNT% THEN PRINT "%FILEVIEW-E-INVFILE, invalid file number."
2480 IF CP_N% < 1% OR CP_N% > FILE_CNT% THEN GOTO 2590
2490 MAX_V% = 0% \ VI% = 1%
2500 IF VI% > FILE_CNT% THEN GOTO 2540
2510 IF FV_DIR$( VI% ) = FV_DIR$( CP_N% ) AND FV_NAME$( VI% ) = CP_NM$ AND FV_VER%( VI% ) > MAX_V% THEN MAX_V% = FV_VER%( VI% )
2520 VI% = VI% + 1% \ GOTO 2500
2540 FILE_CNT% = FILE_CNT% + 1% \ FV_DIR$( FILE_CNT% ) = FV_DIR$( CP_N% ) \ FV_NAME$( FILE_CNT% ) = CP_NM$
2550 FV_VER%( FILE_CNT% ) = MAX_V% + 1% \ FV_BLK%( FILE_CNT% ) = FV_BLK%( CP_N% ) \ FV_ORG$( FILE_CNT% ) = FV_ORG$( CP_N% )
2560 FV_PROT$( FILE_CNT% ) = FV_PROT$( CP_N% ) \ FV_DATE$( FILE_CNT% ) = "19-OCT-1991 15:10" \ FV_BODY$( FILE_CNT% ) = FV_BODY$( CP_N% )
2570 V_STR$ = STR$(FV_VER%( FILE_CNT% )) \ C_STR$ = V_STR$ \ GOSUB 3520 \ V_STR$ = C_STR$
2580 PRINT "%FILEVIEW-I-COPIED, copied #"; CP_N%; " to "; FV_DIR$( FILE_CNT% ); CP_NM$; ";"; V_STR$; "."
2590 RETURN
2600 SP_R% = INSTR(1%, UARG$, " ")
2610 IF SP_R% = 0% THEN PRINT "%FILEVIEW-E-SYNTAX, usage: RENAME <n> <newname>"
2620 IF SP_R% = 0% THEN GOTO 2720
2630 RN_N% = VAL(LEFT$(UARG$, SP_R% - 1%)) \ RN_NM$ = MID$(UARG$, SP_R% + 1%, LEN(UARG$))
2640 C_STR$ = RN_NM$ \ GOSUB 3520 \ RN_NM$ = C_STR$
2650 IF RN_N% < 1% OR RN_N% > FILE_CNT% THEN PRINT "%FILEVIEW-E-INVFILE, invalid file number."
2660 IF RN_N% < 1% OR RN_N% > FILE_CNT% THEN GOTO 2720
2670 OLD_NM$ = FV_NAME$( RN_N% ) \ FV_NAME$( RN_N% ) = RN_NM$
2680 PRINT "%FILEVIEW-I-RENAMED, renamed "; OLD_NM$; " to "; RN_NM$; ";"; FV_VER%( RN_N% ); "."
2720 RETURN
2730 DL_N% = VAL(ARG$)
2740 IF DL_N% < 1% OR DL_N% > FILE_CNT% THEN PRINT "%FILEVIEW-E-INVFILE, invalid file number."
2750 IF DL_N% < 1% OR DL_N% > FILE_CNT% THEN GOTO 2850
2760 DEL_NM$ = FV_NAME$( DL_N% ) \ DEL_V% = FV_VER%( DL_N% ) \ KI% = DL_N%
2770 IF KI% >= FILE_CNT% THEN GOTO 2820
2780 NX% = KI% + 1%
2790 FV_DIR$( KI% ) = FV_DIR$( NX% ) \ FV_NAME$( KI% ) = FV_NAME$( NX% ) \ FV_VER%( KI% ) = FV_VER%( NX% ) \ FV_BLK%( KI% ) = FV_BLK%( NX% )
2800 FV_ORG$( KI% ) = FV_ORG$( NX% ) \ FV_PROT$( KI% ) = FV_PROT$( NX% ) \ FV_DATE$( KI% ) = FV_DATE$( NX% ) \ FV_BODY$( KI% ) = FV_BODY$( NX% )
2810 KI% = KI% + 1% \ GOTO 2770
2820 FILE_CNT% = FILE_CNT% - 1%
2830 IF CUR_FILE% > FILE_CNT% THEN CUR_FILE% = FILE_CNT%
2840 PRINT "%FILEVIEW-I-DELETED, deleted "; DEL_NM$; ";"; DEL_V%; "."
2850 RETURN
2860 REM --- PURGE old versions ---
2870 PRG_CNT% = 0% \ NEW_C% = 0% \ PI% = 1%
2880 IF PI% > FILE_CNT% THEN GOTO 2990
2890 HAS_NEWER% = 0% \ PJ% = 1%
2900 IF PJ% > FILE_CNT% THEN GOTO 2940
2910 IF FV_DIR$( PJ% ) = FV_DIR$( PI% ) AND FV_NAME$( PJ% ) = FV_NAME$( PI% ) AND FV_VER%( PJ% ) > FV_VER%( PI% ) THEN HAS_NEWER% = 1%
2920 PJ% = PJ% + 1% \ GOTO 2900
2940 IF HAS_NEWER% = 1% THEN PRG_CNT% = PRG_CNT% + 1%
2950 IF HAS_NEWER% = 1% THEN GOTO 2980
2960 NEW_C% = NEW_C% + 1% \ FV_DIR$( NEW_C% ) = FV_DIR$( PI% ) \ FV_NAME$( NEW_C% ) = FV_NAME$( PI% ) \ FV_VER%( NEW_C% ) = FV_VER%( PI% )
2970 FV_BLK%( NEW_C% ) = FV_BLK%( PI% ) \ FV_ORG$( NEW_C% ) = FV_ORG$( PI% ) \ FV_PROT$( NEW_C% ) = FV_PROT$( PI% )
2975 FV_DATE$( NEW_C% ) = FV_DATE$( PI% ) \ FV_BODY$( NEW_C% ) = FV_BODY$( PI% )
2980 PI% = PI% + 1% \ GOTO 2880
2990 FILE_CNT% = NEW_C%
3000 PRINT "%FILEVIEW-I-PURGED, purged "; PRG_CNT%; " older file version(s)."
3010 RETURN
3020 SP_P% = INSTR(1%, UARG$, " ")
3030 IF SP_P% = 0% THEN PRINT "%FILEVIEW-E-SYNTAX, usage: PROTECT <n> <protection>"
3040 IF SP_P% = 0% THEN GOTO 3140
3050 PR_N% = VAL(LEFT$(UARG$, SP_P% - 1%)) \ PR_M$ = MID$(UARG$, SP_P% + 1%, LEN(UARG$))
3060 C_STR$ = PR_M$ \ GOSUB 3520 \ PR_M$ = C_STR$
3070 IF PR_N% < 1% OR PR_N% > FILE_CNT% THEN PRINT "%FILEVIEW-E-INVFILE, invalid file number."
3080 IF PR_N% < 1% OR PR_N% > FILE_CNT% THEN GOTO 3140
3090 FV_PROT$( PR_N% ) = PR_M$
3100 PRINT "%FILEVIEW-I-PROTSET, protection on "; FV_NAME$( PR_N% ); " set to "; PR_M$; "."
3140 RETURN
3150 IF VERB$ = "DCL" THEN GOTO 3240
3160 RN_ID% = VAL(ARG$)
3170 IF RN_ID% < 1% OR RN_ID% > FILE_CNT% THEN PRINT "%FILEVIEW-E-INVFILE, invalid file number."
3180 IF RN_ID% < 1% OR RN_ID% > FILE_CNT% THEN GOTO 3300
3190 PRINT "--- FileView DCL Subprocess: @"; FV_DIR$( RN_ID% ); FV_NAME$( RN_ID% ); " ---"
3200 PRINT "  "; FV_BODY$( RN_ID% )
3210 PRINT "%SYSTEM-S-NORMAL, normal successful completion (PID 204001A4)"
3220 GOTO 3300
3240 IF LEN(ARG$) = 0% THEN PRINT "%FILEVIEW-E-NODCL, specify DCL command string."
3250 IF LEN(ARG$) = 0% THEN GOTO 3300
3260 PRINT "--- FileView DCL Subprocess: $ "; ARG$; " ---"
3270 PRINT "%SYSTEM-S-NORMAL, DCL verb completed in VUE$MASTER subshell."
3300 RETURN
3310 Q_CNT% = 0% \ REM_CMD$ = RAW_LINE$
3330 IF LEN(REM_CMD$) = 0% THEN GOTO 3400
3340 SEMI_P% = INSTR(1%, REM_CMD$, ";") \ Q_CNT% = Q_CNT% + 1%
3360 IF SEMI_P% = 0% THEN CMD_Q$( Q_CNT% ) = REM_CMD$
3370 IF SEMI_P% = 0% THEN REM_CMD$ = ""
3380 IF SEMI_P% > 0% THEN CMD_Q$( Q_CNT% ) = LEFT$(REM_CMD$, SEMI_P% - 1%)
3390 IF SEMI_P% > 0% THEN REM_CMD$ = MID$(REM_CMD$, SEMI_P% + 1%, LEN(REM_CMD$))
3395 GOTO 3330
3400 RETURN
3410 P_CNT% = 0% \ REM_P$ = P_LINE$
3430 IF LEN(REM_P$) = 0% THEN GOTO 3510
3440 PP% = INSTR(1%, REM_P$, "|") \ P_CNT% = P_CNT% + 1%
3460 IF PP% = 0% THEN FLD_P$( P_CNT% ) = REM_P$
3470 IF PP% = 0% THEN REM_P$ = ""
3480 IF PP% > 0% THEN FLD_P$( P_CNT% ) = LEFT$(REM_P$, PP% - 1%)
3490 IF PP% > 0% THEN REM_P$ = MID$(REM_P$, PP% + 1%, LEN(REM_P$))
3500 GOTO 3430
3510 RETURN
3520 IF LEN(C_STR$) = 0% THEN GOTO 3610
3540 IF LEFT$(C_STR$, 1%) <> " " THEN GOTO 3570
3550 C_STR$ = MID$(C_STR$, 2%, LEN(C_STR$)) \ GOTO 3520
3570 IF LEN(C_STR$) = 0% THEN GOTO 3610
3580 IF RIGHT$(C_STR$, 1%) <> " " THEN GOTO 3610
3590 C_STR$ = LEFT$(C_STR$, LEN(C_STR$) - 1%) \ GOTO 3570
3610 RETURN
3620 U_OUT$ = "" \ UI% = 1%
3640 IF UI% > LEN(U_IN$) THEN GOTO 3695
3650 CH_A% = ASCII(MID$(U_IN$, UI%, 1%))
3660 IF CH_A% >= 97% AND CH_A% <= 122% THEN CH_A% = CH_A% - 32%
3670 U_OUT$ = U_OUT$ + CHR$(CH_A%) \ UI% = UI% + 1% \ GOTO 3640
3695 RETURN
3850 IF LEN(UARG$) = 0% THEN PRINT "%FILEVIEW-E-NOKWD, specify search keyword."
3870 IF LEN(UARG$) = 0% THEN GOTO 4000
3880 PRINT "--- DECwindows FileView Search Results for '"; ARG$; "' ---"
3890 HITS% = 0% \ KI% = 1%
3900 IF KI% > FILE_CNT% THEN GOTO 3980
3910 U_IN$ = FV_DIR$( KI% ) + SP1$ + FV_NAME$( KI% ) + SP1$ + FV_BODY$( KI% )
3920 GOSUB 3620
3930 IF INSTR(1%, U_OUT$, UARG$) = 0% THEN GOTO 3970
3940 HITS% = HITS% + 1%
3950 PRINT "  #"; KI%; " "; FV_DIR$( KI% ); FV_NAME$( KI% ); ";"; FV_VER%( KI% ); " ("; FV_BLK%( KI% ); " blk)"
3970 KI% = KI% + 1% \ GOTO 3900
3980 PRINT "Total matches found: "; HITS%
4000 RETURN
4120 IF LEFT$(UARG$, 3%) = "ON " THEN ARG$ = MID$(ARG$, 4%, LEN(ARG$))
4124 C_STR$ = ARG$ \ GOSUB 3520 \ ARG$ = C_STR$
4126 IF LEN(ARG$) > 0% THEN GOTO 4150
4130 PRT_CH% = 0% \ GOSUB 4190
4145 RETURN
4150 IF LEN(ARG$) = 0% THEN PRINT "%FILEVIEW-E-NOFILE, specify output filename."
4155 IF LEN(ARG$) = 0% THEN GOTO 4185
4160 OPEN ARG$ FOR OUTPUT AS FILE #2% \ PRT_CH% = 2% \ GOSUB 4190 \ CLOSE #2% \ PRT_CH% = 0%
4180 PRINT "%FILEVIEW-I-EXPORTED, DECwindows FileView window exported to "; ARG$
4185 RETURN
4190 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4200 PAD38$ = "                                      " \ T_S$ = CUR_DIR$ + PAD38$ \ W_TMP$ = LEFT$(T_S$, 36%)
4204 OUT_L$ = "| [X] DECwindows FileView: " + W_TMP$
4206 OUT_L$ = OUT_L$ + " [_][#] |" \ GOSUB 4305
4208 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4210 OUT_L$ = "| File   Commands   View   Options   Utilities   Work_in_Progress       Help |" \ GOSUB 4305
4215 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4218 OUT_L$ = "| Directory: " + CUR_DIR$
4220 OUT_L$ = OUT_L$ + "   Filter: " + CUR_FLT$
4222 OUT_L$ = OUT_L$ + "   Files:" + STR$(FILE_CNT%) \ GOSUB 4305
4225 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4230 OUT_L$ = "| [Type/View]  [Run/Submit]  [Copy]  [Rename]  [Delete]  [Purge]  [Protect]  |" \ GOSUB 4305
4235 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4240 WI% = 1%
4245 IF WI% > FILE_CNT% THEN GOTO 4270
4248 IF CUR_DIR$ <> "ALL" AND FV_DIR$( WI% ) <> CUR_DIR$ THEN GOTO 4265
4250 W_ROW$ = "| #" + STR$(WI%) + SP1$ + FV_NAME$( WI% ) + SEMI$ + STR$(FV_VER%( WI% )) + SP1$ + LBRK$ + FV_ORG$( WI% ) + RBRK$ + SP1$ + FV_PROT$( WI% )
4255 OUT_L$ = W_ROW$ \ GOSUB 4305
4265 WI% = WI% + 1% \ GOTO 4245
4270 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4272 IF CUR_FILE% < 1% OR CUR_FILE% > FILE_CNT% THEN GOTO 4290
4275 OUT_L$ = "| Preview #" + STR$(CUR_FILE%) + SP1$ + FV_NAME$( CUR_FILE% ) + COLON$ + SP1$ + FV_BODY$( CUR_FILE% ) \ GOSUB 4305
4290 OUT_L$ = "+----------------------------------------------------------------------------+" \ GOSUB 4305
4300 RETURN
4305 IF PRT_CH% = 0% THEN PRINT OUT_L$
4310 IF PRT_CH% = 2% THEN PRINT #2%, OUT_L$
4315 RETURN
4320 IF LEN(ARG$) = 0% THEN PRINT "%FILEVIEW-E-NOFILE, specify filename to save."
4330 IF LEN(ARG$) = 0% THEN GOTO 4395
4335 OPEN ARG$ FOR OUTPUT AS FILE #1%
4340 HDR_REC$ = "FILEVIEW" + PIPE$ + CUR_DIR$ + PIPE$ + CUR_FLT$ + PIPE$ + STR$(CUR_FILE%)
4345 PRINT #1%, HDR_REC$ \ SVI% = 1%
4355 IF SVI% > FILE_CNT% THEN GOTO 4385
4360 F_REC$ = "FIL" + PIPE$ + FV_DIR$( SVI% ) + PIPE$ + FV_NAME$( SVI% ) + PIPE$ + STR$(FV_VER%( SVI% )) + PIPE$ + STR$(FV_BLK%( SVI% ))
4365 F_REC$ = F_REC$ + PIPE$ + FV_ORG$( SVI% ) + PIPE$ + FV_PROT$( SVI% ) + PIPE$ + FV_DATE$( SVI% ) + PIPE$ + FV_BODY$( SVI% )
4370 PRINT #1%, F_REC$ \ SVI% = SVI% + 1% \ GOTO 4355
4385 CLOSE #1%
4390 PRINT "%FILEVIEW-I-SAVED, saved "; FILE_CNT%; " files to "; ARG$
4395 RETURN
4400 IF LEN(ARG$) = 0% THEN PRINT "%FILEVIEW-E-NOFILE, specify filename to load."
4410 IF LEN(ARG$) = 0% THEN GOTO 4495
4415 FILE_CNT% = 0%
4420 OPEN ARG$ FOR INPUT AS FILE #1%
4425 LINE INPUT #1%, L_REC$
4430 IF LEN(L_REC$) = 0% THEN GOTO 4485
4435 IF ASCII(LEFT$(L_REC$, 1%)) = 0% THEN GOTO 4485
4440 P_LINE$ = L_REC$ \ GOSUB 3410
4445 IF FLD_P$( 1% ) = "FILEVIEW" THEN CUR_DIR$ = FLD_P$( 2% )
4450 IF FLD_P$( 1% ) = "FILEVIEW" THEN CUR_FLT$ = FLD_P$( 3% )
4455 IF FLD_P$( 1% ) = "FILEVIEW" THEN CUR_FILE% = VAL(FLD_P$( 4% ))
4460 IF FLD_P$( 1% ) <> "FIL" THEN GOTO 4425
4465 FILE_CNT% = FILE_CNT% + 1% \ FV_DIR$( FILE_CNT% ) = FLD_P$( 2% ) \ FV_NAME$( FILE_CNT% ) = FLD_P$( 3% )
4470 FV_VER%( FILE_CNT% ) = VAL(FLD_P$( 4% )) \ FV_BLK%( FILE_CNT% ) = VAL(FLD_P$( 5% )) \ FV_ORG$( FILE_CNT% ) = FLD_P$( 6% )
4475 FV_PROT$( FILE_CNT% ) = FLD_P$( 7% ) \ FV_DATE$( FILE_CNT% ) = FLD_P$( 8% ) \ FV_BODY$( FILE_CNT% ) = FLD_P$( 9% )
4480 GOTO 4425
4485 CLOSE #1%
4490 PRINT "%FILEVIEW-I-LOADED, loaded "; FILE_CNT%; " files from "; ARG$
4495 RETURN
4500 END
