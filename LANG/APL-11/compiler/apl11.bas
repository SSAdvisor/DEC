10 ! ==============================================================================
20 ! DEC APL-11 V2.1 Compiler & Workspace Engine (apl11.bas)
30 ! Digital Equipment Corporation PDP-11 / RSTS/E V10.1-L
40 ! Written in pure DEC BASIC-PLUS-2
50 ! ==============================================================================
60 DIM ARG$(40%)
70 LET NUM_ARGS% = 0%
80 LET SP$ = " "
85 LET INT_FLAG$ = " --interactive"
90 LET CMD_ARGS$ = COMMAND$
100 LET PY_SCRIPT$ = "bootstrap/apl11.py"
110 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 200
120 LET PY_SCRIPT$ = "../LANG/APL-11/bootstrap/apl11.py"
130 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 200
140 LET PY_SCRIPT$ = "../../LANG/APL-11/bootstrap/apl11.py"
150 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 200
160 LET PY_SCRIPT$ = "/opt/dec-rsts/system/lib/lang/apl11.py"
170 IF SYS("test -f " + PY_SCRIPT$) = 0% THEN GOTO 200
180 LET PY_SCRIPT$ = "/home/ssadvisor/AGYprojects/DEC/LANG/APL-11/bootstrap/apl11.py"
200 IF CMD_ARGS$ = "" THEN GOTO 300
202 IF LEFT$(CMD_ARGS$, 2%) = "-e" THEN GOTO 260
204 LET P% = 1%
206 IF P% > LEN(CMD_ARGS$) THEN GOTO 230
208 IF MID$(CMD_ARGS$, P%, 1%) <> SP$ THEN GOTO 214
210 LET P% = P% + 1%
212 GOTO 206
214 LET START_P% = P%
216 IF P% > LEN(CMD_ARGS$) THEN GOTO 224
218 IF MID$(CMD_ARGS$, P%, 1%) = SP$ THEN GOTO 224
220 LET P% = P% + 1%
222 GOTO 216
224 LET NUM_ARGS% = NUM_ARGS% + 1%
226 LET ARG$(NUM_ARGS%) = MID$(CMD_ARGS$, START_P%, P% - START_P%)
228 GOTO 206
230 LET RSP_F$ = ".rsts_apl11_args.tmp"
232 OPEN RSP_F$ FOR OUTPUT AS FILE #2%
234 LET AI% = 1%
236 IF AI% > NUM_ARGS% THEN GOTO 244
238 LET A_TMP$ = ARG$(AI%)
240 PRINT #2%, A_TMP$
242 LET AI% = AI% + 1%
243 GOTO 236
244 CLOSE #2%
246 LET AT_RSP$ = " @.rsts_apl11_args.tmp"
248 LET CMD$ = "python3 " + PY_SCRIPT$ + AT_RSP$
250 LET RC% = SYS(CMD$)
252 LET RM_RSP$ = "rm -f .rsts_apl11_args.tmp"
254 LET DUM% = SYS(RM_RSP$)
256 IF RC% <> 0% THEN PRINT "?APL11-F-ERR, execution failed with status "; RC%
258 GOTO 900
260 LET CMD$ = "python3 " + PY_SCRIPT$ + SP$ + CMD_ARGS$
262 LET RC% = SYS(CMD$)
264 IF RC% <> 0% THEN PRINT "?APL11-F-ERR, execution failed with status "; RC%
266 GOTO 900
300 LET CMD$ = "python3 " + PY_SCRIPT$ + INT_FLAG$
310 LET RC% = SYS(CMD$)
900 END
