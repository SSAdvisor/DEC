10 ! ==============================================================================
12 ! DECwindows V3.0 - X11 Protocol & Motif Session Manager (DECW$SESSION / decwx11)
14 ! Native DEC BASIC-PLUS-2 Interfacing Controller for libdecw_x11 / decw_x11
16 ! ==============================================================================
20 DIM APP_ID$(15%)
22 DIM APP_NAME$(15%)
24 DIM APP_DESC$(15%)
30 LET NUM_APPS% = 0%
32 LET CUR_DISPLAY$ = ":10"
34 LET WM_THEME$ = "MOTIF_1.1_STEEL_BLUE"
36 LET FONT_NAME$ = "-dec-terminal-medium-r-normal--14-140-75-75-c-80-iso8859-1"
38 LET FORCE_CLI% = 0%
40 LET OUT_CH% = 0%
42 LET RBRK$ = "]"
44 LET SP$ = " "
45 GOSUB 1000
50 LET IN_LINE$ = COMMAND$
52 GOSUB 3300
54 LET RAW_CMD$ = TR_OUT$
56 IF LEFT$(RAW_CMD$, 5%) = "--cli" THEN
58   LET FORCE_CLI% = 1%
60   LET IN_LINE$ = MID$(RAW_CMD$, 6%, LEN(RAW_CMD$) - 5%)
62   GOSUB 3300
64   LET RAW_CMD$ = TR_OUT$
66 END IF
68 IF RAW_CMD$ = "--x11" OR RAW_CMD$ = "-gui" THEN LET RAW_CMD$ = "X11; EXIT"
70 IF RAW_CMD$ <> "" THEN GOTO 250
72 IF FORCE_CLI% = 1% THEN GOTO 85
74 LET CHK_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --check-gui"
76 IF SYS(CHK_CMD$) = 0% THEN
78   GOSUB 1900
80   END
82 END IF
85 PRINT "=================================================================="
90 PRINT " DECwindows V3.0 - X11 Protocol & Motif Session Manager (decwx11)"
95 PRINT " Native Xlib Library (libdecw_x11.so) & BASIC-PLUS-2 Bridge"
100 PRINT "=================================================================="
105 PRINT "Type HELP for X11 session commands, APPS to list, or EXIT to quit."
110 PRINT ""
120 ! Interactive REPL Loop
130 PRINT "DECWX11> ";
140 LINE INPUT IN_LINE$
150 IF ASCII(IN_LINE$) = 26% THEN GOTO 900
160 GOSUB 3300
165 LET IN_LINE$ = TR_OUT$
170 IF IN_LINE$ = "" THEN GOTO 130
180 LET RAW_CMD$ = IN_LINE$
190 GOSUB 300
200 IF QUIT_FLAG% = 1% THEN GOTO 900
210 IF COMMAND$ = "" THEN GOTO 130
220 GOTO 900
250 ! Batch Mode Entry
260 GOSUB 300
270 GOTO 900
300 ! Process semicolon-separated commands in RAW_CMD$
310 LET REM_CMD$ = RAW_CMD$
320 IF REM_CMD$ = "" THEN GOTO 395
330 LET SEMI_P% = INSTR(1%, REM_CMD$, ";")
340 IF SEMI_P% = 0% THEN
342   LET ONE_CMD$ = REM_CMD$
344   LET REM_CMD$ = ""
346 ELSE
348   LET ONE_CMD$ = LEFT$(REM_CMD$, SEMI_P% - 1%)
350   LET REM_CMD$ = MID$(REM_CMD$, SEMI_P% + 1%, LEN(REM_CMD$) - SEMI_P%)
352 END IF
360 LET IN_LINE$ = ONE_CMD$
365 GOSUB 3300
370 LET ONE_CMD$ = TR_OUT$
375 IF ONE_CMD$ <> "" THEN GOSUB 400
380 IF QUIT_FLAG% = 1% THEN GOTO 395
390 GOTO 320
395 RETURN
400 ! Single Command Dispatcher
410 LET SP_P% = INSTR(1%, ONE_CMD$, " ")
420 IF SP_P% = 0% THEN
422   LET VERB$ = ONE_CMD$
424   LET ARG_STR$ = ""
426 ELSE
428   LET VERB$ = LEFT$(ONE_CMD$, SP_P% - 1%)
430   LET IN_LINE$ = MID$(ONE_CMD$, SP_P% + 1%, LEN(ONE_CMD$) - SP_P%)
432   GOSUB 3300
434   LET ARG_STR$ = TR_OUT$
436 END IF
440 LET IN_STR$ = VERB$
442 GOSUB 3400
444 LET VERB$ = UP_OUT$
450 IF VERB$ = "EXIT" OR VERB$ = "QUIT" THEN
452   LET QUIT_FLAG% = 1%
454   GOTO 590
456 END IF
460 IF VERB$ = "HELP" THEN GOTO 500
462 IF VERB$ = "SAMPLE" THEN GOTO 505
464 IF VERB$ = "PROBE" OR VERB$ = "XPROBE" THEN GOTO 510
466 IF VERB$ = "APPS" OR VERB$ = "LIST" THEN GOTO 515
468 IF VERB$ = "LAUNCH" OR VERB$ = "RUN" THEN GOTO 520
470 IF VERB$ = "DISPLAY" OR VERB$ = "RENDER" THEN GOTO 525
472 IF VERB$ = "EXPORT" THEN GOTO 530
474 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 535
476 IF VERB$ = "X11" OR VERB$ = "GUI" OR VERB$ = "XDISPLAY" THEN GOTO 540
485 PRINT "%DECWX11-E-INVCMD, unrecognized command: " + VERB$
490 GOTO 590
500 GOSUB 600
502 GOTO 590
505 GOSUB 1000
507 PRINT "[DECwindows X11 Session Manager initialized - 11 X11/Motif applications registered]"
508 GOTO 590
510 GOSUB 1200
512 GOTO 590
515 GOSUB 1300
517 GOTO 590
520 GOSUB 1400
522 GOTO 590
525 LET OUT_CH% = 0%
526 GOSUB 2200
527 GOTO 590
530 GOSUB 2500
532 GOTO 590
535 GOSUB 2600
537 GOTO 590
540 GOSUB 1900
542 GOTO 590
590 RETURN
600 ! HELP Command
610 PRINT "DECwindows X11 Protocol & Motif 1.1 Session Manager Commands:"
615 PRINT "  PROBE                 - Probe active X11 display server via libdecw_x11"
620 PRINT "  APPS                  - List all 11 registered DECwindows X11 applications"
625 PRINT "  LAUNCH <app>          - Launch a DECwindows application in X11 GUI mode"
630 PRINT "  X11                   - Open the DECwindows Session Manager X11 window"
635 PRINT "  DISPLAY               - Render the Session Manager window to terminal"
640 PRINT "  EXPORT <file>         - Export the Session Manager frame to a file"
645 PRINT "  SHOW                  - Display X11 library version, theme, and server status"
650 PRINT "  SAMPLE                - Reload the 11 DECwindows suite definitions"
655 PRINT "  HELP                  - Display this command reference"
660 PRINT "  EXIT                  - Exit DECwindows X11 Session Manager"
665 RETURN
1000 ! Initialize 11 DECwindows Suite Applications
1010 LET NUM_APPS% = 11%
1015 LET APP_ID$( 1% ) = "decterm" \ LET APP_NAME$( 1% ) = "DECterm" \ LET APP_DESC$( 1% ) = "VT300/VT220/VT100/VT52 X11 Terminal Emulator"
1020 LET APP_ID$( 2% ) = "bookreader" \ LET APP_NAME$( 2% ) = "Bookreader" \ LET APP_DESC$( 2% ) = "Online Hypertext Documentation Reader"
1025 LET APP_ID$( 3% ) = "calendar" \ LET APP_NAME$( 3% ) = "Calendar" \ LET APP_DESC$( 3% ) = "Personal & Group Appointment Scheduler"
1030 LET APP_ID$( 4% ) = "cardfiler" \ LET APP_NAME$( 4% ) = "Cardfiler" \ LET APP_DESC$( 4% ) = "Rotary Index Card Database Manager"
1035 LET APP_ID$( 5% ) = "cdaviewer" \ LET APP_NAME$( 5% ) = "CDA Viewer" \ LET APP_DESC$( 5% ) = "DDIF/DTIF Compound Document Inspector"
1040 LET APP_ID$( 6% ) = "calculator" \ LET APP_NAME$( 6% ) = "Calculator" \ LET APP_DESC$( 6% ) = "Scientific, Financial & Hex/Oct Calculator"
1045 LET APP_ID$( 7% ) = "clock" \ LET APP_NAME$( 7% ) = "Clock" \ LET APP_DESC$( 7% ) = "Analog Dial & Digital Workstation Clock"
1050 LET APP_ID$( 8% ) = "decsound" \ LET APP_NAME$( 8% ) = "DECsound" \ LET APP_DESC$( 8% ) = "Workstation Audio Clip Recorder & Player"
1055 LET APP_ID$( 9% ) = "dxmail" \ LET APP_NAME$( 9% ) = "DECwindows Mail" \ LET APP_DESC$( 9% ) = "Hierarchical Mail Cabinet & Folder Client"
1060 LET APP_ID$( 10% ) = "fileview" \ LET APP_NAME$( 10% ) = "FileView" \ LET APP_DESC$( 10% ) = "Workstation File Manager & DCL Launcher"
1065 LET APP_ID$( 11% ) = "notepad" \ LET APP_NAME$( 11% ) = "Notepad" \ LET APP_DESC$( 11% ) = "XUI/Motif Text Editor & X11 Clipboard"
1070 RETURN
1200 ! PROBE X11 Server
1210 LET PRB_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --probe"
1220 LET RC% = SYS(PRB_CMD$)
1230 IF RC% <> 0% THEN PRINT "%DECWX11-W-NOXSERVER, X11 display probe returned status" + STR$(RC%)
1240 RETURN
1300 ! APPS / LIST
1310 PRINT "Registered DECwindows X11 / Motif 1.1 Applications:"
1315 PRINT "----------------------------------------------------------------------------"
1320 PRINT " #   App ID       Application Name    Description"
1325 PRINT "----------------------------------------------------------------------------"
1330 LET IDX% = 1%
1335 IF IDX% > NUM_APPS% THEN GOTO 1380
1340 LET PAD$ = "                       "
1345 LET T_S$ = APP_ID$( IDX% ) + PAD$ \ LET C_ID$ = LEFT$(T_S$, 12%)
1350 LET T_S$ = APP_NAME$( IDX% ) + PAD$ \ LET C_NM$ = LEFT$(T_S$, 19%)
1355 PRINT " " + STR$(IDX%) + SP$ + SP$ + C_ID$ + SP$ + C_NM$ + SP$ + APP_DESC$( IDX% )
1360 LET IDX% = IDX% + 1%
1365 GOTO 1335
1380 PRINT "----------------------------------------------------------------------------"
1385 RETURN
1400 ! LAUNCH <app>
1410 IF ARG_STR$ = "" THEN
1412   PRINT "%DECWX11-E-NOAPP, usage: LAUNCH <app_id>"
1414   GOTO 1480
1416 END IF
1420 LET L_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --verify --app " + ARG_STR$
1430 LET RC% = SYS(L_CMD$)
1440 IF RC% = 0% THEN PRINT "[X11 Session Manager launched application: " + ARG_STR$ + RBRK$
1450 IF RC% <> 0% THEN PRINT "%DECWX11-E-LAUNCHERR, failed to launch X11 window for " + ARG_STR$
1480 RETURN
1900 ! X11 / GUI Session Manager Window
1910 LET EXP_SAV$ = ARG_STR$
1915 LET ARG_STR$ = "/tmp/decw_decwindows.txt"
1920 GOSUB 2500
1925 LET ARG_STR$ = EXP_SAV$
1930 LET X_CMD$ = "PATH=./bin:../x11/bin:apps/decwindows/x11/bin:$PATH decw_x11 --app decwindows --frame /tmp/decw_decwindows.txt"
1940 LET RC% = SYS(X_CMD$)
1950 RETURN
2200 ! DISPLAY / RENDER Session Manager Window
2210 LET BDR$ = "+----------------------------------------------------------------------------+"
2212 LET VBAR$ = "|"
2214 LET L1$ = BDR$ \ GOSUB 3200
2215 LET T_S$ = "| [=] DECwindows Session Manager - X11 / Motif 1.1 Desktop"
2217 LET PAD$ = "                                                           "
2219 LET T_P$ = T_S$ + PAD$
2221 LET L1$ = LEFT$(T_P$, 71%) + "[_][O] |" \ GOSUB 3200
2223 LET L1$ = BDR$ \ GOSUB 3200
2225 LET L1$ = "|  Session    Applications    Customize    Window    Security    Help        |" \ GOSUB 3200
2227 LET L1$ = BDR$ \ GOSUB 3200
2230 LET T_S$ = "| Theme: " + WM_THEME$
2232 LET T_P$ = T_S$ + PAD$
2234 LET L1$ = LEFT$(T_P$, 77%) + VBAR$ \ GOSUB 3200
2236 LET L1$ = "|----------------------------------------------------------------------------|" \ GOSUB 3200
2238 LET L1$ = "|  #  Application       X11 Binary   Description                             |" \ GOSUB 3200
2240 LET L1$ = "|----------------------------------------------------------------------------|" \ GOSUB 3200
2245 LET IDX% = 1%
2250 IF IDX% > NUM_APPS% THEN GOTO 2285
2255 LET T_S$ = APP_NAME$( IDX% ) + PAD$ \ LET C_NM$ = LEFT$(T_S$, 17%)
2260 LET T_S$ = APP_ID$( IDX% ) + PAD$ \ LET C_ID$ = LEFT$(T_S$, 12%)
2265 LET T_S$ = APP_DESC$( IDX% ) + PAD$ \ LET C_DS$ = LEFT$(T_S$, 39%)
2270 LET ROW$ = "| " + STR$(IDX%) + SP$ + SP$ + C_NM$ + SP$ + C_ID$ + SP$ + C_DS$
2272 LET T_P$ = ROW$ + PAD$
2274 LET L1$ = LEFT$(T_P$, 77%) + VBAR$ \ GOSUB 3200
2276 LET IDX% = IDX% + 1%
2278 GOTO 2250
2285 LET L1$ = BDR$ \ GOSUB 3200
2288 LET L1$ = "| [Status: X11 READY]  [Apps: 11]  [Toolkit: OSF/Motif 1.1]  [Lib: Xlib]     |" \ GOSUB 3200
2290 LET L1$ = BDR$ \ GOSUB 3200
2295 RETURN
2500 ! EXPORT Frame
2510 IF ARG_STR$ = "" THEN
2512   PRINT "%DECWX11-E-NOFILE, usage: EXPORT <filename>"
2514   GOTO 2550
2516 END IF
2520 OPEN ARG_STR$ FOR OUTPUT AS FILE #2%
2525 LET OUT_CH% = 2%
2530 GOSUB 2200
2535 CLOSE #2%
2540 LET OUT_CH% = 0%
2545 PRINT "[DECwindows X11 Session Manager exported to " + ARG_STR$ + RBRK$
2550 RETURN
2600 ! SHOW Status
2610 PRINT "DECwindows X11 Interfacing Library & Session Manager Status:"
2615 PRINT "  Library Engine   : DECwindows X11/Motif 1.1 Interfacing Library V3.0 (libdecw_x11.so)"
2620 PRINT "  Bridge Binary    : decw_x11 (Xlib Event Loop, 3D Motif Bevel & Callback Engine)"
2625 PRINT "  Window Theme     : " + WM_THEME$
2630 PRINT "  Default Font     : " + FONT_NAME$
2635 PRINT "  Registered Apps  :" + STR$(NUM_APPS%)
2640 GOSUB 1200
2645 RETURN
3200 ! Output Helper
3210 IF OUT_CH% = 0% THEN PRINT L1$
3220 IF OUT_CH% > 0% THEN PRINT #2%, L1$
3230 RETURN
3300 ! Trim IN_LINE$ -> TR_OUT$
3310 LET TR_OUT$ = IN_LINE$
3315 IF TR_OUT$ = "" THEN GOTO 3360
3320 IF LEFT$(TR_OUT$, 1%) <> " " THEN GOTO 3335
3325 LET TR_OUT$ = MID$(TR_OUT$, 2%, LEN(TR_OUT$) - 1%)
3330 GOTO 3315
3335 IF TR_OUT$ = "" THEN GOTO 3360
3340 IF RIGHT$(TR_OUT$, LEN(TR_OUT$)) <> " " THEN GOTO 3360
3345 LET TR_OUT$ = LEFT$(TR_OUT$, LEN(TR_OUT$) - 1%)
3350 GOTO 3335
3360 RETURN
3400 ! Uppercase IN_STR$ -> UP_OUT$
3410 LET UP_OUT$ = ""
3415 LET U_I% = 1%
3420 LET U_L% = LEN(IN_STR$)
3425 IF U_I% > U_L% THEN GOTO 3460
3430 LET U_C$ = MID$(IN_STR$, U_I%, 1%)
3435 LET U_A% = ASCII(U_C$)
3440 IF U_A% >= 97% AND U_A% <= 122% THEN LET U_C$ = CHR$(U_A% - 32%)
3445 LET UP_OUT$ = UP_OUT$ + U_C$
3450 LET U_I% = U_I% + 1%
3455 GOTO 3425
3460 RETURN
900 ! Exit
910 END
