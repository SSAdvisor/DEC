10 MAP (REC_BUF) STRING MAP_LINE$ = 255% \ DIM R_DEV$(15%) \ DIM R_NODES$(15%) \ DIM R_TYPE$(15%) \ DIM R_VAL%(15%)
20 NUM_REC% = 0% \ SIM_MODE$ = "IDLE" \ DB_FILE$ = "SPICE.CIR"
30 BLANKS$ = "                                                                                "
40 SEP$    = "--------------------------------------------------------------------------------"
50 EQU$    = "================================================================================" \ IS_BATCH% = 0% \ CMD_LINE$ = COMMAND$
60 IF CMD_LINE$ = "" THEN GOTO 80
70 IS_BATCH% = 1% \ SC_REM$ = CMD_LINE$ \ GOTO 170
80 PRINT EQU$ \ PRINT "    VAX SPICE 3D1 / HSPICE - Electronic Circuit Simulator" \ PRINT "    UC Berkeley CAD Group / Meta-Software - DEC VAX/VMS V5.5-2" \ PRINT EQU$
90 PRINT "Type HELP for commands, SAMPLE to load deck, NETLIST, OP, TRAN, AC, or EXIT." \ PRINT ""
100 PRINT "SPICE3> "; \ LINE INPUT RAW_INPUT$
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
350 IF VERB$ = "NETLIST" OR VERB$ = "LIST" OR VERB$ = "DISPLAY" THEN GOTO 820
360 IF VERB$ = "OP" OR VERB$ = ".OP" THEN GOTO 960
370 IF VERB$ = "TRAN" OR VERB$ = ".TRAN" THEN GOTO 1120
380 IF VERB$ = "AC" OR VERB$ = ".AC" THEN GOTO 1250
390 IF VERB$ = "ADD" OR VERB$ = "INSERT" THEN GOTO 1380
400 IF VERB$ = "SAVE" THEN GOTO 1550
410 IF VERB$ = "LOAD" OR VERB$ = "IMPORT" THEN GOTO 1700
420 IF VERB$ = "SHOW" OR VERB$ = "STATUS" THEN GOTO 1950
430 IF VERB$ = "CLEAR" OR VERB$ = "RESET" THEN GOTO 2050
480 PRINT "SPICE3: Unknown command '"; VERB$; "'. Type HELP for syntax."
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
700 NUM_REC% = 5% \ SIM_MODE$ = "LOADED"
710 R_DEV$(1%) = "V1" \ R_NODES$(1%) = "N1 -> GND          " \ R_TYPE$(1%) = "DC_MV " \ R_VAL%(1%) = 5000%
720 R_DEV$(2%) = "R1" \ R_NODES$(2%) = "N1 -> N2           " \ R_TYPE$(2%) = "OHM   " \ R_VAL%(2%) = 1000%
730 R_DEV$(3%) = "R2" \ R_NODES$(3%) = "N2 -> N3           " \ R_TYPE$(3%) = "OHM   " \ R_VAL%(3%) = 2200%
740 R_DEV$(4%) = "C1" \ R_NODES$(4%) = "N3 -> GND          " \ R_TYPE$(4%) = "PF    " \ R_VAL%(4%) = 100%
750 R_DEV$(5%) = "Q1" \ R_NODES$(5%) = "N3 -> N2 -> GND    " \ R_TYPE$(5%) = "BJT_B " \ R_VAL%(5%) = 150%
760 PRINT "[Sample VAX SPICE 3D1 circuit deck loaded - 5 elements]" \ GOTO 495
820 IF NUM_REC% = 0% THEN GOTO 3370
830 PRINT EQU$ \ PRINT "  .TITLE VAX SPICE 3D1 CIRCUIT DECK — File: "; DB_FILE$ \ PRINT SEP$
840 PRINT "  Idx   Element   Node Connections       Model/Unit   ParamVal" \ PRINT SEP$
850 LI% = 1%
860 IF LI% > NUM_REC% THEN GOTO 920
870 D_P$ = LEFT$(R_DEV$(LI%) + BLANKS$, 8%) \ N_P$ = LEFT$(R_NODES$(LI%) + BLANKS$, 21%) \ T_P$ = LEFT$(R_TYPE$(LI%) + BLANKS$, 10%)
880 PRINT "  "; LI%; "     "; D_P$; "  "; N_P$; "  "; T_P$; "   "; R_VAL%(LI%)
890 LI% = LI% + 1% \ GOTO 860
920 PRINT "  .END" \ PRINT EQU$ \ GOTO 495
960 IF NUM_REC% = 0% THEN GOTO 3370
970 V_IN% = R_VAL%(1%) \ V_N2% = INT((V_IN% * 68%) / 100%) \ V_N3% = INT((V_IN% * 44%) / 100%) \ I_BR% = INT(V_IN% / 3%)
980 SIM_MODE$ = "DC_OP"
990 PRINT EQU$ \ PRINT "  SPICE 3D1 SMALL-SIGNAL BIAS SOLUTION (.OP)   TEMP = 27.0 DEG C" \ PRINT SEP$
1000 PRINT "  NODE     VOLTAGE (mV)      BRANCH     CURRENT (uA)     POWER (uW)" \ PRINT SEP$
1010 PRINT "  V(N1)    "; V_IN%; "             I(V1)      -"; I_BR%; "            "; INT((V_IN% * I_BR%) / 1000%)
1020 PRINT "  V(N2)    "; V_N2%; "             I(R1)       "; I_BR%; "            "; INT(((V_IN% - V_N2%) * I_BR%) / 1000%)
1030 PRINT "  V(N3)    "; V_N3%; "             Ic(Q1)      "; INT((I_BR% * 98%) / 100%); "            "; INT((V_N3% * I_BR%) / 1000%)
1040 PRINT SEP$ \ PRINT "  [SPICE3 .OP DC Operating Point Converged: V(1)="; V_IN%; "mV V(2)="; V_N2%; "mV V(3)="; V_N3%; "mV]" \ PRINT EQU$ \ GOTO 495
1120 IF NUM_REC% = 0% THEN GOTO 3370
1130 SIM_MODE$ = "TRAN"
1140 PRINT EQU$ \ PRINT "  SPICE 3D1 TRANSIENT ANALYSIS (.TRAN 10NS 50NS) — Output Node V(N3)" \ PRINT SEP$
1150 PRINT "  Time(ns)   V(N3) mV   ASCII Oscilloscope Trace" \ PRINT SEP$
1160 PRINT "   0.0 ns      2200     |***********"
1170 PRINT "  10.0 ns      2750     |**************"
1180 PRINT "  20.0 ns      3080     |****************"
1190 PRINT "  30.0 ns      3150     |*****************"
1200 PRINT "  40.0 ns      2640     |*************"
1210 PRINT "  50.0 ns      2210     |***********"
1220 PRINT SEP$ \ PRINT "  [SPICE3 .TRAN Transient Analysis Complete: Peak V(3)=3150mV at t=30ns]" \ PRINT EQU$ \ GOTO 495
1250 IF NUM_REC% = 0% THEN GOTO 3370
1260 SIM_MODE$ = "AC_BODE"
1270 PRINT EQU$ \ PRINT "  SPICE 3D1 AC SMALL-SIGNAL BODE RESPONSE (.AC DEC 10 1KHZ 100MHZ)" \ PRINT SEP$
1280 PRINT "  Freq (Hz)       Gain (dB)    Phase (Deg)    Response Band" \ PRINT SEP$
1290 PRINT "  1.000E+03         24.0         -2.1         Passband Flat"
1300 PRINT "  1.000E+05         23.9        -14.5         Passband"
1310 PRINT "  1.000E+07         21.0        -45.0         -3dB Corner (f_3dB)"
1320 PRINT "  1.000E+08          4.0        -84.2         Roll-Off (-20dB/dec)"
1330 PRINT SEP$ \ PRINT "  [SPICE3 .AC Bode Sweep Complete: Midband Gain=24dB | f_3dB=10MHz]" \ PRINT EQU$ \ GOTO 495
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
1490 NUM_REC% = NUM_REC% + 1% \ R_DEV$(NUM_REC%) = K_V$ \ R_NODES$(NUM_REC%) = N_V$ \ R_TYPE$(NUM_REC%) = G_V$ \ R_VAL%(NUM_REC%) = VL_V%
1495 PRINT "[SPICE3 Element #"; NUM_REC%; " added: "; K_V$; " ("; N_V$; ", Val="; VL_V%; ")]" \ GOTO 495
1500 PRINT "SPICE3: Syntax is ADD <dev>, <nodes>, <type>, <val>" \ GOTO 495
1510 PRINT "SPICE3: Circuit deck buffer full" \ GOTO 495
1550 IF NUM_REC% = 0% THEN GOTO 3370
1560 SV_FILE$ = DB_FILE$
1570 IF ARGS$ <> "" THEN SV_FILE$ = ARGS$
1580 OPEN SV_FILE$ FOR OUTPUT AS FILE #2% \ SI% = 1%
1590 IF SI% > NUM_REC% THEN GOTO 1630
1600 PRINT #2%, R_DEV$(SI%); "|"; R_NODES$(SI%); "|"; R_TYPE$(SI%); "|"; R_VAL%(SI%)
1610 SI% = SI% + 1% \ GOTO 1590
1630 CLOSE #2% \ PRINT "["; NUM_REC%; " SPICE3 elements saved to "; SV_FILE$; "]" \ GOTO 495
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
1820 NUM_REC% = NUM_REC% + 1% \ R_DEV$(NUM_REC%) = FK$ \ R_NODES$(NUM_REC%) = FN$ \ R_TYPE$(NUM_REC%) = FG$ \ R_VAL%(NUM_REC%) = FV% \ GOTO 1730
1850 CLOSE #2% \ RESUME 1860
1860 ON ERROR GOTO 0 \ PRINT "["; NUM_REC%; " SPICE3 elements loaded from "; LD_FILE$; "]" \ GOTO 495
1950 PRINT "VAX SPICE 3D1 / HSPICE Status:" \ PRINT "  Deck File:      "; DB_FILE$; " (Elements: "; NUM_REC%; ", SimMode: "; SIM_MODE$; ")" \ GOTO 495
2050 NUM_REC% = 0% \ SIM_MODE$ = "IDLE" \ PRINT "[SPICE3 circuit deck cleared]" \ GOTO 495
3000 PRINT EQU$ \ PRINT "    VAX SPICE 3D1 / HSPICE Commands" \ PRINT EQU$
3010 PRINT "  SAMPLE / DEMO                    Load sample BJT amplifier circuit deck" \ PRINT "  NETLIST / LIST                   Display SPICE circuit deck components"
3020 PRINT "  OP / .OP                         Run DC operating point node analysis" \ PRINT "  TRAN / .TRAN                     Run transient time-domain simulation"
3030 PRINT "  AC / .AC                         Run AC small-signal Bode sweep" \ PRINT "  ADD <dev>, <nodes>, <type>, <v>  Add circuit component to deck"
3040 PRINT "  SAVE [file] / LOAD [file]        Save or load SPICE.CIR deck" \ PRINT "  SHOW / CLEAR / EXIT              Show status, clear deck, or exit" \ PRINT EQU$ \ GOTO 495
3370 PRINT "SPICE3: Circuit deck is empty. Use SAMPLE or ADD." \ GOTO 495
3400 END
