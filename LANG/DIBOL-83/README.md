# DEC DIBOL-83 V5.3 Compiler (`LANG/DIBOL-83`)

Authentic Digital Equipment Corporation **DIBOL-83 V5.3** (Digital Business Oriented Language / CTS-300 / CTS-500) Compiler for **RSTS/E V10.1-L**.

## Architecture
- **Frontend (`compiler/dibol83.bas` -> `compiler/dibol83`)**: Written in pure DEC BASIC-PLUS-2 and compiled with `basicc` and `basiclink`. Supports CLI compilation (`dibol83 INVOIC.DBL -o INVOIC.OBJ -l INVOIC.LST`) and an interactive `DIBOL>` workbench (`SAMPLE`, `LIST`, `CHECK`, `COMPILE`).
- **Compiler Core (`bootstrap/dibol83.py`)**: Supports `RECORD` division (`A` alpha and `D` decimal fields with initializers) and `PROC` division (`XCALL FLAGS`, `XCALL OUTPT`, `OPEN`, `CLOSE`, `DISPLAY`, `ACCEPT`, `READ`, `INCR`, `DECR`, `CLEAR`, `FOR ... FROM ... THRU ... DO`, `IF (...) ... ELSE ...`, `CALL`, `RETURN`, `GOTO`, `STOP`, `END`).
- **Target Output**: Standard RSTS/E `.OBJ` relocatable object modules linked via `basiclink` (`LINK`) into standalone `.TSK` executables on `rsts_vm`.
