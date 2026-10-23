# DEC VAX Pascal V4.3 Compiler (`vaxpas`)

Native implementation of the **DEC VAX Pascal V4.3** compiler (`compiler/vaxpas` + `bootstrap/vaxpas.py`) for **DEC VAX/VMS V5.5-2**, emitting OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings linked via `vmslink` into standalone `vms_vm` executables.

## Features
- Module attributes (`[IDENT('V04-03')]`) and `PROGRAM <name>(INPUT, OUTPUT);`
- `CONST`, `TYPE` (`RECORD ... END`), and `VAR` (`INTEGER`, `REAL`, `DOUBLE`, `SINGLE`, `BOOLEAN`, `CHAR`, `VARYING [n] OF CHAR`, `STRING`, `ARRAY[lo..hi] OF ...`)
- Nested and top-level `PROCEDURE` and `FUNCTION` declarations
- Structured control flow: `BEGIN ... END`, `IF ... THEN ... ELSE`, `CASE ... OF ... OTHERWISE ... END`, `FOR ... TO/DOWNTO ... DO`, `WHILE ... DO`, `REPEAT ... UNTIL`
- Standard & VMS I/O: `WRITELN`, `WRITE`, `READLN`, `READ`
- Both `{ ... }` and `(* ... *)` comment styles

## Quick Start
```bash
make build
make demo
make test
```
