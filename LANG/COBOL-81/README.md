# DEC PDP-11 COBOL-81 V2.4 Compiler (`LANG/COBOL-81`)

Authentic Digital Equipment Corporation **PDP-11 COBOL-81 V2.4** (ANSI X3.23-1974) Compiler for **RSTS/E V10.1-L**.

## Architecture
- **Frontend (`compiler/cobol81.bas` -> `compiler/cobol81`)**: Written in pure DEC BASIC-PLUS-2 and compiled with `basicc` and `basiclink`. Supports CLI compilation (`cobol81 PAYROL.CBL -o PAYROL.OBJ -l PAYROL.LST`) and an interactive `COBOL>` workbench (`SAMPLE`, `LIST`, `CHECK`, `COMPILE`).
- **Compiler Core (`bootstrap/cobol81.py`)**: Supports `IDENTIFICATION DIVISION`, `ENVIRONMENT DIVISION`, `DATA DIVISION` (`WORKING-STORAGE SECTION`, `PIC X/9/V`, `VALUE`), and `PROCEDURE DIVISION` (`DISPLAY`, `ACCEPT`, `MOVE`, `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `COMPUTE`, `PERFORM`, `PERFORM ... VARYING ... UNTIL`, `IF/THEN/ELSE`, `GO TO`, `STOP RUN`).
- **Target Output**: Standard RSTS/E `.OBJ` relocatable object modules linked via `basiclink` (`LINK`) into standalone `.TSK` executables on `rsts_vm`.
