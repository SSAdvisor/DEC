10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_ELEM$(15%) \ DIM R_DESC$(15%) \ DIM R_MAT$(15%) \ DIM R_LOAD%(15%)
20 NUM_REC% = 0% \ FEA_STATE$ = "PREP7" \ DB_FILE$ = "ANSYS.DAT"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Swanson Analysis Systems ANSYS V4.4 - Finite Element Analysis (FEA)" \ PRINT "    Swanson Analysis Systems, Inc. (Houston, PA) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load mesh, PREP7, SOLVE, POST1, or EXIT." \ PRINT ""
100 PRINT "ANSYS> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "PREP7" OR VERB$ = "/PREP7" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "SOLU" OR VERB$ = "/SOLU" OR VERB$ = "SOLVE" THEN GOTO 960
370 IF VERB$ = "POST1" OR VERB$ = "/POST1" THEN GOTO 1150
380 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
390 IF VERB$ = "SAVE" THEN GOTO 1550
400 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
410 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
420 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "ANSYS: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ FEA_STATE$ = "PREP7"
710 R_ELEM$(1%) = "E-101" \ R_DESC$(1%) = "STIF45 Root Anchor " \ R_MAT$(1%) = "TI64" \ R_LOAD%(1%) = 240%
720 R_ELEM$(2%) = "E-102" \ R_DESC$(2%) = "STIF45 Web Spar    " \ R_MAT$(2%) = "TI64" \ R_LOAD%(2%) = 195%
730 R_ELEM$(3%) = "E-103" \ R_DESC$(3%) = "STIF63 Wing Skin   " \ R_MAT$(3%) = "AL70" \ R_LOAD%(3%) = 160%
740 R_ELEM$(4%) = "E-104" \ R_DESC$(4%) = "STIF4 Beam Tip     " \ R_MAT$(4%) = "AL70" \ R_LOAD%(4%) = 110%
750 PRINT "[Sample ANSYS V4.4 FEA structural mesh loaded - 4 elements]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 FEA_STATE$ = "PREP7"
840 PRINT EQU$ \ PRINT "  ANSYS V4.4 /PREP7 — Finite Element Mesh Definition (File: "; DB_FILE$; ")" \ PRINT SEP$
850 PRINT "  Seq   ElemID   Element Type & Zone    Material   Stress(MPa)" \ PRINT SEP$
860 LI% = 1%
870 IF LI% > NUM_REC% THEN GOTO 920
880 E_P$ = LEFT$(R_ELEM$(LI%) + BLANKS$, 7%) \ D_P$ = LEFT$(R_DESC$(LI%) + BLANKS$, 21%) \ M_P$ = LEFT$(R_MAT$(LI%) + BLANKS$, 8%)
890 PRINT "  "; LI%; "     "; E_P$; "  "; D_P$; "  "; M_P$; "   "; R_LOAD%(LI%)
900 LI% = LI% + 1% \ GOTO 870
920 PRINT EQU$ \ GOTO 495
960 IF NUM_REC% = 0% THEN GOTO 3370
970 FEA_STATE$ = "SOLVED" \ DOF% = NUM_REC% * 24% \ WAVE% = 18%
980 PRINT EQU$ \ PRINT "  ANSYS V4.4 /SOLU — Frontal Direct Stiffness Matrix Solver" \ PRINT SEP$
990 PRINT "  Active Degrees of Freedom (DOF):  "; DOF%; " (UX, UY, UZ, ROTX, ROTY, ROTZ)"
1000 PRINT "  RMS Wavefront Size:               "; WAVE%; " Equations (In-Core VAX Virtual Memory)"
1010 PRINT "  Boundary Conditions:              Root Nodes Fixed (UX=UY=UZ=0)"
1020 PRINT SEP$ \ PRINT "  [ANSYS /SOLU Frontal Matrix Solution Converged: "; NUM_REC%; " elements | "; DOF%; " DOF]" \ PRINT EQU$ \ GOTO 495
1150 IF NUM_REC% = 0% THEN GOTO 3370
1160 FEA_STATE$ = "POST1" \ MAX_S% = 0% \ SUM_S% = 0% \ MAX_E$ = "" \ PI% = 1%
1170 PRINT EQU$ \ PRINT "  ANSYS V4.4 /POST1 — Von Mises Equivalent Stress & Nodal Displacement" \ PRINT SEP$
1180 PRINT "  ElemID   Material   VonMises(MPa)   Deflect(0.1mm)   SafetyFactor" \ PRINT SEP$
1190 IF PI% > NUM_REC% THEN GOTO 1280
1200 S_VAL% = R_LOAD%(PI%) \ SUM_S% = SUM_S% + S_VAL%
1210 IF S_VAL% > MAX_S% THEN MAX_S% = S_VAL%
1220 IF S_VAL% = MAX_S% THEN MAX_E$ = R_ELEM$(PI%)
1230 DEF_V% = INT(S_VAL% / 12%) \ SF_V% = INT(800% / S_VAL%)
1240 E_P$ = LEFT$(R_ELEM$(PI%) + BLANKS$, 7%) \ M_P$ = LEFT$(R_MAT$(PI%) + BLANKS$, 8%)
1250 PRINT "  "; E_P$; "  "; M_P$; "   "; S_VAL%; "             "; DEF_V%; "               "; SF_V%
1260 PI% = PI% + 1% \ GOTO 1190
1280 PRINT SEP$ \ PRINT "  [ANSYS /POST1 Summary: Max Von Mises = "; MAX_S%; " MPa at "; MAX_E$; " | Min SF = "; INT(800% / MAX_S%); "]" \ PRINT EQU$ \ GOTO 495
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
1490 NUM_REC% = NUM_REC% + 1% \ R_ELEM$(NUM_REC%) = K_V$ \ R_DESC$(NUM_REC%) = N_V$ \ R_MAT$(NUM_REC%) = G_V$ \ R_LOAD%(NUM_REC%) = VL_V%
1495 PRINT "[ANSYS Element #"; NUM_REC%; " added: "; K_V$; " ("; N_V$; ", Stress="; VL_V%; " MPa)]" \ GOTO 495
1500 PRINT "ANSYS: Syntax is ADD <elem_id>, <desc>, <material>, <stress_mpa>" \ GOTO 495
1510 PRINT "ANSYS: Element table full" \ GOTO 495
1550 IF NUM_REC% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_REC% THEN GOTO 1630
1600 PRINT #2%, R_ELEM$(SI%); "|"; R_DESC$(SI%); "|"; R_MAT$(SI%); "|"; R_LOAD%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_REC%; " ANSYS elements saved to "; SV_FILE$; "]" \ GOTO 495
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
1820 NUM_REC% = NUM_REC% + 1% \ R_ELEM$(NUM_REC%) = FK$ \ R_DESC$(NUM_REC%) = FN$ \ R_MAT$(NUM_REC%) = FG$ \ R_LOAD%(NUM_REC%) = FV% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " ANSYS elements loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Swanson Analysis ANSYS V4.4 Status:" \ PRINT "  Database File:  "; DB_FILE$; " (Elements: "; NUM_REC%; ", Processor: /"; FEA_STATE$; ")" \ GOTO 495
2050 NUM_REC% = 0% \ FEA_STATE$ = "PREP7" \ PRINT "[ANSYS finite element database cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Swanson Analysis ANSYS V4.4 Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample aerospace structural mesh" \ PRINT "  PREP7 / /PREP7 / LIST            Display /PREP7 finite element mesh"
3020 PRINT "  SOLU / /SOLU / SOLVE             Run frontal stiffness matrix solver" \ PRINT "  POST1 / /POST1                   Display Von Mises stress & safety factor"
3030 PRINT "  ADD <id>, <desc>, <mat>, <mpa>   Add finite element to mesh" \ PRINT "  SAVE [file] / LOAD [file]        Save or load ANSYS.DAT database"
3040 PRINT "  SHOW / CLEAR / EXIT              Show status, clear mesh, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "ANSYS: Mesh database is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
