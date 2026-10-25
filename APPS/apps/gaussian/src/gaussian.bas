10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_ATOM$(15%) \ DIM R_ZMAT$(15%) \ DIM R_BASIS$(15%) \ DIM R_CHG%(15%)
20 NUM_REC% = 0% \ QM_STATE$ = "ZMAT" \ DB_FILE$ = "GAUSS.G90"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    Gaussian 90 - Ab Initio Quantum Chemistry System (Rev. J)" \ PRINT "    Gaussian, Inc. (Pittsburgh, PA) - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load molecule, ZMAT, SCF, POP, FREQ, or EXIT." \ PRINT ""
100 PRINT "G90> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "ZMAT" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "SCF" OR VERB$ = "HF" THEN GOTO 960
370 IF VERB$ = "POP" OR VERB$ = "MULLIKEN" THEN GOTO 1120
380 IF VERB$ = "FREQ" OR VERB$ = "IR" THEN GOTO 1260
390 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
400 IF VERB$ = "SAVE" THEN GOTO 1550
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "G90: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 4% \ QM_STATE$ = "ZMAT"
710 R_ATOM$(1%) = "C1" \ R_ZMAT$(1%) = "Origin (0.00, 0.00)" \ R_BASIS$(1%) = "6-31G*" \ R_CHG%(1%) = 240%
720 R_ATOM$(2%) = "O2" \ R_ZMAT$(2%) = "C1  R=1.203 A      " \ R_BASIS$(2%) = "6-31G*" \ R_CHG%(2%) = -460%
730 R_ATOM$(3%) = "H3" \ R_ZMAT$(3%) = "C1  R=1.101 A=121.8" \ R_BASIS$(3%) = "6-31G*" \ R_CHG%(3%) = 110%
740 R_ATOM$(4%) = "H4" \ R_ZMAT$(4%) = "C1  R=1.101 D=180.0" \ R_BASIS$(4%) = "6-31G*" \ R_CHG%(4%) = 110%
750 PRINT "[Sample Gaussian 90 Formaldehyde (H2CO) Z-Matrix loaded - 4 atoms]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  Gaussian 90 Route: #P RHF/6-31G* OPT FREQ POP=FULL — File: "; DB_FILE$ \ PRINT SEP$
840 PRINT "  Center   Atom   Z-Matrix Internal Coordinates   Basis    Mulliken(m-e)" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_REC% THEN GOTO 920
870 A_P$ = LEFT$(R_ATOM$(LI%) + BLANKS$, 6%) \ Z_P$ = LEFT$(R_ZMAT$(LI%) + BLANKS$, 29%) \ B_P$ = LEFT$(R_BASIS$(LI%) + BLANKS$, 7%)
880 PRINT "  "; LI%; "        "; A_P$; " "; Z_P$; "   "; B_P$; "  "; R_CHG%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT EQU$ \ GOTO 495
960 IF NUM_REC% = 0% THEN GOTO 3370
970 QM_STATE$ = "SCF_DONE" \ N_BAS% = NUM_REC% * 9%
980 PRINT EQU$ \ PRINT "  LINK 502 — Restricted Hartree-Fock (RHF) SCF Iterative Convergence" \ PRINT SEP$
990 PRINT "  Cycle   Total Electronic Energy (Hartrees)     Delta-E          DIIS" \ PRINT SEP$
1000 PRINT "    1     -113.4102845                           0.0000000        Init"
1010 PRINT "    2     -113.8419201                          -0.4316356        DIIS"
1020 PRINT "    3     -113.8661904                          -0.0242703        DIIS"
1030 PRINT "    4     -113.8663312                          -0.0001408        Conv"
1040 PRINT SEP$ \ PRINT "  [SCF Done: E(RHF) = -113.866331 A.U. after 4 cycles | Basis="; N_BAS%; " GTFs]" \ PRINT EQU$ \ GOTO 495
1120 IF NUM_REC% = 0% THEN GOTO 3370
1130 QM_STATE$ = "POP_DONE" \ NET_Q% = 0% \ PI% = 1%
1140 PRINT EQU$ \ PRINT "  LINK 601 — Total Atomic Charges (Mulliken Population & Dipole)" \ PRINT SEP$
1150 IF PI% > NUM_REC% THEN GOTO 1210
1160 NET_Q% = NET_Q% + R_CHG%(PI%) \ A_P$ = LEFT$(R_ATOM$(PI%) + BLANKS$, 6%)
1170 PRINT "  Atom #"; PI%; " ("; A_P$; ")  Basis="; R_BASIS$(PI%); "   Charge = "; R_CHG%(PI%); " milli-e"
1180 PI% = PI% + 1% \ GOTO 1150
1210 PRINT SEP$ \ PRINT "  [Mulliken Population Complete: Net Charge = "; NET_Q%; " me | Dipole = 2.67 Debye]" \ PRINT EQU$ \ GOTO 495
1260 IF NUM_REC% = 0% THEN GOTO 3370
1270 QM_STATE$ = "FREQ_DONE"
1280 PRINT EQU$ \ PRINT "  LINK 716 — Harmonic Vibrational Frequencies & Zero-Point Energy (ZPE)" \ PRINT SEP$
1290 PRINT "  Mode   Symmetry   Frequency (cm-1)   IR Intensity (KM/Mole)   Assignment" \ PRINT SEP$
1300 PRINT "   1       B1           1335.4                 14.2             CH2 Wag"
1310 PRINT "   2       A1           1681.9                 38.5             CH2 Scissor"
1320 PRINT "   3       A1           1988.2                142.0             C=O Stretch"
1330 PRINT "   4       A1           3159.7                 64.8             C-H Sym Str"
1340 PRINT SEP$ \ PRINT "  [Gaussian 90 FREQ Complete: 0 Imaginary Freqs (Minimum) | ZPE = 18.42 kcal/mol]" \ PRINT EQU$ \ GOTO 495
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
1490 NUM_REC% = NUM_REC% + 1% \ R_ATOM$(NUM_REC%) = K_V$ \ R_ZMAT$(NUM_REC%) = N_V$ \ R_BASIS$(NUM_REC%) = G_V$ \ R_CHG%(NUM_REC%) = VL_V%
1495 PRINT "[Gaussian 90 Atom #"; NUM_REC%; " added: "; K_V$; " ("; N_V$; ", Charge="; VL_V%; " me)]" \ GOTO 495
1500 PRINT "G90: Syntax is ADD <atom>, <zmat_coords>, <basis>, <charge_me>" \ GOTO 495
1510 PRINT "G90: Z-Matrix buffer full" \ GOTO 495
1550 IF NUM_REC% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_REC% THEN GOTO 1630
1600 PRINT #2%, R_ATOM$(SI%); "|"; R_ZMAT$(SI%); "|"; R_BASIS$(SI%); "|"; R_CHG%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_REC%; " Gaussian 90 atoms saved to "; SV_FILE$; "]" \ GOTO 495
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
1820 NUM_REC% = NUM_REC% + 1% \ R_ATOM$(NUM_REC%) = FK$ \ R_ZMAT$(NUM_REC%) = FN$ \ R_BASIS$(NUM_REC%) = FG$ \ R_CHG%(NUM_REC%) = FV% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " Gaussian 90 atoms loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "Gaussian 90 Ab Initio System Status:" \ PRINT "  Active Input:   "; DB_FILE$; " (Atoms: "; NUM_REC%; ", Link State: "; QM_STATE$; ")" \ GOTO 495
2050 NUM_REC% = 0% \ QM_STATE$ = "ZMAT" \ PRINT "[Gaussian 90 Z-matrix cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    Gaussian 90 Ab Initio Quantum Chemistry Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load Formaldehyde (H2CO) Z-Matrix" \ PRINT "  ZMAT / LIST                      Display Z-matrix molecular geometry"
3020 PRINT "  SCF / HF                         Run Hartree-Fock SCF convergence" \ PRINT "  POP / MULLIKEN                   Display Mulliken charges & dipole"
3030 PRINT "  FREQ / IR                        Compute harmonic IR frequencies & ZPE" \ PRINT "  ADD <atom>, <zmat>, <bas>, <chg> Add atom center to Z-matrix"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load GAUSS.G90 input file" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear Z-matrix, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "G90: Z-matrix is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
