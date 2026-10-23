# DEC MACRO-11 V05.05 Assembler (`LANG/MACRO-11`)

Authentic Digital Equipment Corporation PDP-11 **MACRO-11 V05.05** Relocatable Macro Assembler for **RSTS/E V10.1-L**.

## Architecture
- **Frontend (`compiler/macro11.bas` -> `compiler/macro11`)**: Written in pure DEC BASIC-PLUS-2 and compiled with `basicc` and `basiclink`. Supports both CLI assembly (`macro11 PROG.MAC -o PROG.OBJ -l PROG.LST`) and an interactive `MACRO>` workbench (`SAMPLE`, `LIST`, `SYMBOLS`, `ASSEMBLE`).
- **Assembler Core (`bootstrap/macro11.py`)**: Two-pass PDP-11 MACRO-11 assembler supporting registers `R0`-`R5`, `SP` (`R6`), `PC` (`R7`), condition codes (`N`, `Z`, `V`, `C`), addressing modes (`#imm`, `Rn`, `(Rn)`, `LAB(Rn)`), instructions (`MOV`, `CLR`, `INC`, `DEC`, `NEG`, `ADD`, `SUB`, `MUL`, `DIV`, `CMP`, `TST`, `BIT`, `BIS`, `BIC`, `ASL`, `ASR`, `BR`, `JMP`, `BEQ`, `BNE`, `BLT`, `BGE`, `BLE`, `BGT`, `SOB`, `JSR`, `RTS`, `HALT`, `.PRINT`, `.TTYOUT`, `.EXIT`), and directives (`.TITLE`, `.IDENT`, `.ASCIZ`, `.ASCII`, `.WORD`, `.BYTE`, `.BLKW`, `.END`).
- **Target Output**: Standard RSTS/E `.OBJ` relocatable object modules linked via `basiclink` (`LINK`) into standalone `.TSK` executables on `rsts_vm`.
