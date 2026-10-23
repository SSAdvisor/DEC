10 ! ==============================================================================
20 ! DEC OpenVMS VAX Linker V05-05 (vmslink.bas)
30 ! Digital Equipment Corporation VAX/VMS V5.5-2
40 ! Written in pure DEC VAX BASIC / BASIC-PLUS-2
50 ! ==============================================================================
60 DIM ARG$(40%)
70 LET NUM_ARGS% = 0%
80 LET SP$ = " "
90 LET CMD_ARGS$ = COMMAND$
100 IF CMD_ARGS$ = "" THEN GOTO 300
110 LET P% = 1%
120 IF P% > LEN(CMD_ARGS$) THEN GOTO 200
130 IF MID$(CMD_ARGS$, P%, 1%) <> SP$ THEN GOTO 150
140 LET P% = P% + 1%
145 GOTO 120
150 LET START_P% = P%
160 IF P% > LEN(CMD_ARGS$) THEN GOTO 180
170 IF MID$(CMD_ARGS$, P%, 1%) = SP$ THEN GOTO 180
175 LET P% = P% + 1%
178 GOTO 160
180 LET NUM_ARGS% = NUM_ARGS% + 1%
185 LET ARG$(NUM_ARGS%) = MID$(CMD_ARGS$, START_P%, P% - START_P%)
190 GOTO 120
200 LET PY_SCRIPT$ = "bootstrap/vmslink.py"
205 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 240
210 LET PY_SCRIPT$ = "../LANG/VAX-BASIC/bootstrap/vmslink.py"
215 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 240
220 LET PY_SCRIPT$ = "../../LANG/VAX-BASIC/bootstrap/vmslink.py"
225 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 240
230 LET PY_SCRIPT$ = "/opt/dec-vms/system/lib/lang/vmslink.py"
235 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 240
238 LET PY_SCRIPT$ = "/home/ssadvisor/AGYprojects/DEC/LANG/VAX-BASIC/bootstrap/vmslink.py"
240 LET RSP_F$ = ".vms_link_args.tmp"
245 OPEN RSP_F$ FOR OUTPUT AS FILE #2%
250 LET AI% = 1%
255 IF AI% > NUM_ARGS% THEN GOTO 270
260 LET A_TMP$ = ARG$(AI%)
262 PRINT #2%, A_TMP$
265 LET AI% = AI% + 1%
268 GOTO 255
270 CLOSE #2%
272 LET AT_RSP$ = " @.vms_link_args.tmp"
275 LET CMD$ = "python3 " + PY_SCRIPT$ + AT_RSP$
280 LET RC% = SYS(CMD$)
282 LET RM_RSP$ = "rm -f .vms_link_args.tmp"
285 LET DUM% = SYS(RM_RSP$)
290 GOTO 900
300 PRINT "Usage: vmslink [-o output.exe] [-m output.map] [--full] [--cross-reference] <input1.obj> [options.opt] [lib.olb]"
900 END
