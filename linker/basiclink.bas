10 ! ==============================================================================
20 ! DEC RSTS/E BASIC-PLUS-2 Linker (basiclink)
30 ! Written in pure DEC BASIC-PLUS-2
40 ! ==============================================================================
50 DIM ARG$(50%)
60 DIM BOBJ_FILES$(20%)
70 DIM MOD_NAME$(20%)
80 DIM SEG_LEN%(20%)
90 DIM SEG_VADDR%(20%)
100 DIM SEG_START%(20%)
110 DIM ALL_BC%(32000%)
120 DIM REL_SEG%(200%)
130 DIM REL_OFF%(200%)
140 DIM REL_TYPE$(200%)
150 DIM REL_TGT$(200%)
160 DIM ODL_NAME$(20%)
170 DIM ODL_FCTR$(20%)
180 LET HEX_CHARS$ = "0123456789ABCDEF"
185 LET Q$ = CHR$(34%)
190 LET NUM_ARGS% = 0%
200 LET NUM_BOBJ% = 0%
210 LET NUM_REL% = 0%
220 LET NUM_ODL% = 0%
230 LET ODL_ROOT$ = ""
240 LET ODL_FILE$ = ""
250 LET OUT_FILE$ = "a.out"
260 LET TOTAL_BC% = 0%
270 LET PAYLOAD_SZ% = 0%
280 LET RC% = 0%
290 LET I% = 0%
300 LET J% = 0%
310 LET S% = 0%
320 LET R% = 0%
330 LET P% = 0%
340 LET B% = 0%
350 LET L$ = ""
360 LET SECTION$ = ""
370 LET TMP_HEX$ = ""
380 LET CMD_ARGS$ = COMMAND$
400 LET P% = 1%
410 IF P% > LEN(CMD_ARGS$) THEN GOTO 500
420 IF MID$(CMD_ARGS$, P%, 1%) <> " " THEN GOTO 430
425 LET P% = P% + 1%
428 GOTO 410
430 LET START_P% = P%
440 IF P% > LEN(CMD_ARGS$) THEN GOTO 450
442 IF MID$(CMD_ARGS$, P%, 1%) = " " THEN GOTO 450
444 LET P% = P% + 1%
446 GOTO 440
450 LET NUM_ARGS% = NUM_ARGS% + 1%
460 LET ARG$(NUM_ARGS%) = MID$(CMD_ARGS$, START_P%, P% - START_P%)
470 GOTO 410
500 ! Check arguments
510 IF NUM_ARGS% < 1% THEN
520   PRINT "Usage: basiclink [-o output] <input1.obj> [input2.obj ...] [file.odl]"
530   END
540 END IF
550 LET I% = 1%
560 IF I% > NUM_ARGS% THEN GOTO 650
570 IF ARG$(I%) = "-o" THEN
580   IF I% < NUM_ARGS% THEN LET OUT_FILE$ = ARG$(I% + 1%)
590   LET I% = I% + 2%
600   GOTO 560
610 END IF
620 IF INSTR(1%, ARG$(I%), ".odl") > 0% OR INSTR(1%, ARG$(I%), ".ODL") > 0% THEN
622   LET ODL_FILE$ = ARG$(I%)
624   LET I% = I% + 1%
626   GOTO 560
628 END IF
630 IF INSTR(1%, ARG$(I%), ".obj") > 0% OR INSTR(1%, ARG$(I%), ".OBJ") > 0% THEN
632   LET NUM_BOBJ% = NUM_BOBJ% + 1%
634   LET BOBJ_FILES$(NUM_BOBJ%) = ARG$(I%)
636 END IF
640 LET I% = I% + 1%
645 GOTO 560
650 IF NUM_BOBJ% < 1% THEN
660   PRINT "Error: No input .obj files specified"
670   END
680 END IF
700 ! Parse ODL file if present
710 IF ODL_FILE$ = "" THEN GOTO 800
720 ON ERROR GOTO 790
730 OPEN ODL_FILE$ FOR INPUT AS FILE #1%
740 LINE INPUT #1%, L$
745 IF L$ = "" THEN GOTO 740
750 IF LEFT$(L$, 1%) = ";" THEN GOTO 740
755 IF INSTR(1%, L$, ".ROOT") > 0% THEN
760   LET P% = INSTR(1%, L$, ".ROOT") + 6%
762   LET ODL_ROOT$ = MID$(L$, P%, LEN(L$) - P% + 1%)
764   GOTO 740
766 END IF
770 IF INSTR(1%, L$, ".FCTR") > 0% THEN
772   LET P1% = INSTR(1%, L$, ":")
774   LET P2% = INSTR(1%, L$, ".FCTR") + 6%
776   LET NUM_ODL% = NUM_ODL% + 1%
778   LET ODL_NAME$(NUM_ODL%) = LEFT$(L$, P1% - 1%)
780   LET ODL_FCTR$(NUM_ODL%) = MID$(L$, P2%, LEN(L$) - P2% + 1%)
782 END IF
785 GOTO 740
790 CLOSE #1%
795 ON ERROR GOTO 0
800 ! Read and parse each .obj file
805 LET S% = 1%
810 IF S% > NUM_BOBJ% THEN GOTO 1200
820 LET SEG_START%(S%) = TOTAL_BC%
830 LET SEG_LEN%(S%) = 0%
840 LET MOD_NAME$(S%) = "MOD" + STR$(S%)
850 LET SECTION$ = ""
860 ON ERROR GOTO 1150
870 OPEN BOBJ_FILES$(S%) FOR INPUT AS FILE #1%
880 LINE INPUT #1%, L$
890 IF INSTR(1%, L$, Q$ + "module" + Q$ + ":") > 0% THEN
900   LET P1% = INSTR(1%, L$, Q$ + "module" + Q$ + ":")
910   LET P2% = INSTR(P1% + 9%, L$, Q$)
920   LET P3% = INSTR(P2% + 1%, L$, Q$)
930   LET MOD_NAME$(S%) = MID$(L$, P2% + 1%, P3% - P2% - 1%)
940   GOTO 880
950 END IF
960 IF INSTR(1%, L$, Q$ + "relocations" + Q$ + ":") > 0% THEN
962   LET SECTION$ = "RELOC"
964   GOTO 880
966 END IF
970 IF INSTR(1%, L$, Q$ + "bytecode" + Q$ + ":") > 0% THEN
972   LET SECTION$ = "BC"
974   GOTO 880
976 END IF
980 IF SECTION$ = "RELOC" THEN
982   IF INSTR(1%, L$, "]") > 0% THEN
984     LET SECTION$ = ""
986     GOTO 880
988   END IF
990   IF INSTR(1%, L$, Q$ + "offset" + Q$ + ":") > 0% THEN
995     LET NUM_REL% = NUM_REL% + 1%
1000    LET REL_SEG%(NUM_REL%) = S%
1002    LET P% = INSTR(1%, L$, Q$ + "offset" + Q$ + ":") + 9%
1004    LET REL_OFF%(NUM_REL%) = VAL(MID$(L$, P%, LEN(L$) - P% + 1%))
1006  END IF
1010  IF INSTR(1%, L$, Q$ + "type" + Q$ + ":") > 0% THEN
1012    LET P1% = INSTR(1%, L$, Q$ + "type" + Q$ + ":") + 7%
1014    LET P2% = INSTR(P1%, L$, Q$)
1016    LET P3% = INSTR(P2% + 1%, L$, Q$)
1018    LET REL_TYPE$(NUM_REL%) = MID$(L$, P2% + 1%, P3% - P2% - 1%)
1020  END IF
1022  IF INSTR(1%, L$, Q$ + "target" + Q$ + ":") > 0% THEN
1024    LET P1% = INSTR(1%, L$, Q$ + "target" + Q$ + ":") + 9%
1026    LET P2% = INSTR(P1%, L$, Q$)
1028    LET P3% = INSTR(P2% + 1%, L$, Q$)
1030    LET REL_TGT$(NUM_REL%) = MID$(L$, P2% + 1%, P3% - P2% - 1%)
1032  END IF
1034  GOTO 880
1036 END IF
1040 IF SECTION$ = "BC" THEN
1042  IF INSTR(1%, L$, "]") > 0% THEN
1043    LET SECTION$ = ""
1044    GOTO 880
1045  END IF
1046  LET CP% = 1%
1047  IF CP% > LEN(L$) THEN GOTO 880
1048  LET CH$ = MID$(L$, CP%, 1%)
1049  IF CH$ < "0" OR CH$ > "9" THEN
1050    LET CP% = CP% + 1%
1051    GOTO 1047
1052  END IF
1053  LET NUM_START% = CP%
1054  IF CP% > LEN(L$) THEN GOTO 1060
1055  IF MID$(L$, CP%, 1%) < "0" OR MID$(L$, CP%, 1%) > "9" THEN GOTO 1060
1056  LET CP% = CP% + 1%
1057  GOTO 1054
1060  LET VAL% = VAL(MID$(L$, NUM_START%, CP% - NUM_START%))
1062  LET ALL_BC%(SEG_START%(S%) + SEG_LEN%(S%)) = VAL%
1064  LET SEG_LEN%(S%) = SEG_LEN%(S%) + 1%
1066  GOTO 1047
1070 END IF
1080 GOTO 880
1150 CLOSE #1%
1155 ON ERROR GOTO 0
1160 LET TOTAL_BC% = TOTAL_BC% + SEG_LEN%(S%)
1170 LET S% = S% + 1%
1180 GOTO 810
1200 ! Resolve Relocations
1210 FOR R% = 1% TO NUM_REL%
1220   IF REL_TYPE$(R%) = "CALL_OVL" THEN
1230     LET S% = REL_SEG%(R%)
1240     LET TGT$ = REL_TGT$(R%)
1250     LET TGT_IDX% = 0%
1260     IF TGT$ = "SAVEDB" THEN LET TGT_IDX% = 39320%
1270     IF TGT$ = "LOADDB" THEN LET TGT_IDX% = 39321%
1280     IF TGT$ <> "SAVEDB" AND TGT$ <> "LOADDB" THEN
1290       FOR M% = 1% TO NUM_BOBJ%
1300         IF MOD_NAME$(M%) = TGT$ THEN LET TGT_IDX% = M% - 1%
1310       NEXT M%
1320     END IF
1330     LET OFF% = SEG_START%(S%) + REL_OFF%(R%)
1340     LET ALL_BC%(OFF%) = TGT_IDX% AND 255%
1350     LET ALL_BC%(OFF% + 1%) = INT(TGT_IDX% / 256%) AND 255%
1360   END IF
1370 NEXT R%
1400 ! Assign Virtual Addresses
1410 IF ODL_ROOT$ <> "" THEN
1420   ! ODL present: ROOT-O1 overlay handling
1430   LET ROOT_SZ% = 0%
1440   FOR S% = 1% TO NUM_BOBJ%
1450     IF MOD_NAME$(S%) = "MAIN" THEN
1460       LET SEG_VADDR%(S%) = 0%
1470       LET ROOT_SZ% = SEG_LEN%(S%)
1480     END IF
1490   NEXT S%
1500   FOR S% = 1% TO NUM_BOBJ%
1510     IF MOD_NAME$(S%) <> "MAIN" THEN
1520       LET SEG_VADDR%(S%) = ROOT_SZ%
1530     END IF
1540   NEXT S%
1550 ELSE
1560   ! Sequential VADDR
1570   LET CUR_V% = 0%
1580   FOR S% = 1% TO NUM_BOBJ%
1590     LET SEG_VADDR%(S%) = CUR_V%
1600     LET CUR_V% = CUR_V% + SEG_LEN%(S%)
1610   NEXT S%
1620 END IF
1700 ! Check VM executable existence
1705 LET VM_EXE$ = "vm/build/rsts_vm"
1710 IF SYS("test -f " + VM_EXE$) = 0% THEN GOTO 1760
1715 LET VM_EXE$ = "${DEC_BASIC_HOME}/bin/rsts_vm"
1720 IF SYS("test -f " + VM_EXE$) = 0% THEN GOTO 1760
1725 LET VM_EXE$ = "$(which rsts_vm 2>/dev/null)"
1730 IF SYS("test -n " + Q$ + VM_EXE$ + Q$ + " && test -f " + VM_EXE$) = 0% THEN GOTO 1760
1735 LET VM_EXE$ = "/usr/local/dec-basic2/bin/rsts_vm"
1740 IF SYS("test -f " + VM_EXE$) = 0% THEN GOTO 1760
1745 LET VM_EXE$ = "${HOME}/.local/dec-basic2/bin/rsts_vm"
1750 IF SYS("test -f " + VM_EXE$) = 0% THEN GOTO 1760
1752 PRINT "Error: VM executable rsts_vm not found. Please set DEC_BASIC_HOME or add rsts_vm to PATH."
1754 END
1760 ! Found VM executable
1800 ! Create hex payload
1810 LET TMP_HEX$ = OUT_FILE$ + ".tmp_hex"
1820 OPEN TMP_HEX$ FOR OUTPUT AS FILE #2%
1830 ! 1. Num segments (2 bytes)
1840 LET B% = NUM_BOBJ% AND 255%
1850 PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
1860 LET B% = INT(NUM_BOBJ% / 256%) AND 255%
1870 PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
1880 ! 2. Segment headers: name (16), size (4), vaddr (4)
1890 FOR S% = 1% TO NUM_BOBJ%
1900   LET SNAME$ = MOD_NAME$(S%)
1910   FOR I% = 1% TO 16%
1920     IF I% <= LEN(SNAME$) THEN LET B% = ASCII(MID$(SNAME$, I%, 1%)) ELSE LET B% = 0%
1930     PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
1940   NEXT I%
1950   ! Size (4 bytes)
1960   LET SZ% = SEG_LEN%(S%)
1970   LET B% = SZ% AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
1980   LET B% = INT(SZ% / 256%) AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
1990   LET B% = INT(SZ% / 65536%) AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2000   PRINT #2%, "00";
2010   ! Vaddr (4 bytes)
2020   LET VA% = SEG_VADDR%(S%)
2030   LET B% = VA% AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2040   LET B% = INT(VA% / 256%) AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2050   LET B% = INT(VA% / 65536%) AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2060   PRINT #2%, "00";
2070 NEXT S%
2100 ! 3. Bytecode pool
2110 FOR S% = 1% TO NUM_BOBJ%
2120   FOR J% = 0% TO SEG_LEN%(S%) - 1%
2130     LET B% = ALL_BC%(SEG_START%(S%) + J%)
2140     PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2150   NEXT J%
2160 NEXT S%
2200 ! 4. Footer: Magic "RSTS" + Payload size (4 bytes)
2210 PRINT #2%, "52535453";
2220 LET PAYLOAD_SZ% = 2% + (NUM_BOBJ% * 24%) + TOTAL_BC%
2230 LET B% = PAYLOAD_SZ% AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2240 LET B% = INT(PAYLOAD_SZ% / 256%) AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2250 LET B% = INT(PAYLOAD_SZ% / 65536%) AND 255% \ PRINT #2%, MID$(HEX_CHARS$, INT(B% / 16%) + 1%, 1%) + MID$(HEX_CHARS$, (B% AND 15%) + 1%, 1%);
2260 PRINT #2%, "00";
2270 CLOSE #2%
2300 ! Package executable
2310 LET RC% = SYS("cp " + VM_EXE$ + " " + OUT_FILE$)
2315 LET CMD$ = "xxd -r -p " + TMP_HEX$ + " >> " + OUT_FILE$
2320 LET RC% = SYS(CMD$)
2330 LET RC% = SYS("chmod 755 " + OUT_FILE$)
2340 LET RC% = SYS("rm -f " + TMP_HEX$)
2350 PRINT "Successfully linked "; NUM_BOBJ%; " segments into "; OUT_FILE$
2360 END
