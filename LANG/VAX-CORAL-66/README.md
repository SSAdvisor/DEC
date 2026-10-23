# DEC VAX CORAL 66 V2.1 Compiler (`vaxcoral`)

Native implementation of the **DEC VAX CORAL 66 V2.1** compiler (`compiler/vaxcoral` + `bootstrap/vaxcoral.py`) for **DEC VAX/VMS V5.5-2**, emitting OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings linked via `vmslink` into standalone `vms_vm` executables.

## Features
- Supports both **stropped** (`'PROGRAM'`, `'BEGIN'`, `'INTEGER'`, `'END'`, `'FINISH'`) and **unstropped** (`PROGRAM`, `BEGIN`, `INTEGER`, `END`, `FINISH`) DEC VAX CORAL 66 V2.1 syntax
- `INTEGER`, `FLOATING`, `FIXED(scale, frac)`, `ARRAY`, `TABLE`, `DEFINE`, and `COMMON` declarations
- `PROCEDURE` and typed `INTEGER PROCEDURE` subprograms with `ANSWER` / `RETURN`
- Control structures: `IF ... THEN ... ELSE`, `FOR <v> := <start> STEP <step> WHILE/UNTIL <cond> DO`, `WHILE <cond> DO`, `GOTO`, and `SWITCH`
- Comments: `COMMENT ... ;`, `'COMMENT' ... ;`, and `% ...`
- Output: `WRITE(...)`, `WRITE_TEXT(...)`, `PRINT_VALUE(...)`, `PRINT(...)`, `WRITELN(...)`, and `NEWLINE`

## Quick Start
```bash
make build
make demo
make test
```
