# DEC PDP-11 FORTRAN-77 V5.0 Compiler (`LANG/FORTRAN-77`)

Authentic Digital Equipment Corporation **PDP-11 FORTRAN-77 V5.0** (ANSI X3.9-1978 / FORTRAN IV-PLUS) Compiler for **RSTS/E V10.1-L**.

## Architecture
- **Frontend (`compiler/fortran77.bas` -> `compiler/fortran77`)**: Written in pure DEC BASIC-PLUS-2 and compiled with `basicc` and `basiclink`. Supports CLI compilation (`fortran77 STATS.FOR -o STATS.OBJ -l STATS.LST`) and an interactive `FORTRAN>` workbench (`SAMPLE`, `LIST`, `CHECK`, `COMPILE`).
- **Compiler Core (`bootstrap/fortran77.py`)**: Supports `PROGRAM`, `INTEGER`, `REAL`, `CHARACTER`, `DIMENSION`, `DATA`, `DO <label> I = start, end [, step]` / `CONTINUE` / `ENDDO`, block `IF (...) THEN ... ELSE ... ENDIF`, single-line `IF (...) stmt`, relational operators (`.EQ.`, `.NE.`, `.LT.`, `.LE.`, `.GT.`, `.GE.`, `.AND.`, `.OR.`), `GOTO`, `CALL` / `SUBROUTINE` / `RETURN`, `WRITE(6,*)` / `PRINT *`, `READ`, `FORMAT`, `STOP`, and `END`.
- **Target Output**: Standard RSTS/E `.OBJ` relocatable object modules linked via `basiclink` (`LINK`) into standalone `.TSK` executables on `rsts_vm`.
