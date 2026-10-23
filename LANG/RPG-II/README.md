# DEC PDP-11 RPG II V2.1 Compiler (`LANG/RPG-II`)

Authentic Digital Equipment Corporation **PDP-11 RPG II V2.1** (Report Program Generator II) Compiler for **RSTS/E V10.1-L**.

## Architecture
- **Frontend (`compiler/rpgii.bas` -> `compiler/rpgii`)**: Written in pure DEC BASIC-PLUS-2 and compiled with `basicc` and `basiclink`. Supports CLI compilation (`rpgii SLSRPT.RPG -o SLSRPT.OBJ -l SLSRPT.LST`) and an interactive `RPGII>` workbench (`SAMPLE`, `LIST`, `CHECK`, `COMPILE`).
- **Compiler Core (`bootstrap/rpgii.py`)**: Implements the RPG II fixed logic cycle (`1P` heading pass, calculation specification pass, detail/total `LR` output pass), indicators (`1P`, `LR`, `01`–`99`), Calculation (`C`) specs (`Z-ADD`, `Z-SUB`, `ADD`, `SUB`, `MULT`, `DIV`, `MOVE`, `MOVEL`, `COMP`, `SETON`, `SETOF`, `DO`/`END`, `EXSR`/`BEGSR`/`ENDSR`, `TAG`/`GOTO`, `DSPLY`), and Output (`O`) specs (`H`, `D`, `T`).
- **Target Output**: Standard RSTS/E `.OBJ` relocatable object modules linked via `basiclink` (`LINK`) into standalone `.TSK` executables on `rsts_vm`.
