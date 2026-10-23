10 ! ==============================================================================
20 ! DEC VAX SCAN V1.2-00 String Scanning & Pattern-Matching Compiler (vaxscan.bas)
30 ! Digital Equipment Corporation VAX/VMS V5.5-2
40 ! Written in pure DEC VAX BASIC
50 ! ==============================================================================
60 DIM ARG$(40%)
70 LET NUM_ARGS% = 0%
80 LET SP$ = " "
90 LET CMD_ARGS$ = COMMAND$
100 LET PY_SCRIPT$ = "bootstrap/vaxscan.py"
105 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 150
110 LET PY_SCRIPT$ = "../LANG/VAX-SCAN/bootstrap/vaxscan.py"
115 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 150
120 LET PY_SCRIPT$ = "../../LANG/VAX-SCAN/bootstrap/vaxscan.py"
125 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 150
130 LET PY_SCRIPT$ = "/opt/dec-vms/system/lib/lang/vaxscan.py"
135 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 150
140 LET PY_SCRIPT$ = "/home/ssadvisor/AGYprojects/DEC/LANG/VAX-SCAN/bootstrap/vaxscan.py"
150 IF CMD_ARGS$ = "" THEN GOTO 300
155 LET P% = 1%
160 IF P% > LEN(CMD_ARGS$) THEN GOTO 220
165 IF MID$(CMD_ARGS$, P%, 1%) <> SP$ THEN GOTO 180
170 LET P% = P% + 1%
175 GOTO 160
180 LET START_P% = P%
185 IF P% > LEN(CMD_ARGS$) THEN GOTO 205
190 IF MID$(CMD_ARGS$, P%, 1%) = SP$ THEN GOTO 205
195 LET P% = P% + 1%
200 GOTO 185
205 LET NUM_ARGS% = NUM_ARGS% + 1%
210 LET ARG$(NUM_ARGS%) = MID$(CMD_ARGS$, START_P%, P% - START_P%)
215 GOTO 160
220 LET RSP_F$ = ".vms_scan_args.tmp"
225 OPEN RSP_F$ FOR OUTPUT AS FILE #2%
230 LET AI% = 1%
235 IF AI% > NUM_ARGS% THEN GOTO 255
240 LET A_TMP$ = ARG$(AI%)
245 PRINT #2%, A_TMP$
250 LET AI% = AI% + 1%
252 GOTO 235
255 CLOSE #2%
260 LET AT_RSP$ = " @.vms_scan_args.tmp"
265 LET CMD$ = "python3 " + PY_SCRIPT$ + AT_RSP$
270 LET RC% = SYS(CMD$)
275 LET RM_RSP$ = "rm -f .vms_scan_args.tmp"
280 LET DUM% = SYS(RM_RSP$)
285 GOTO 900
300 LET CMD$ = "python3 " + PY_SCRIPT$
310 LET RC% = SYS(CMD$)
900 END
