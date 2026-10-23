# DEC VAX PL/I V3.5 Compiler (`vaxpli`)

Native implementation of the **DEC VAX PL/I V3.5** compiler (`compiler/vaxpli` + `bootstrap/vaxpli.py`) for **DEC VAX/VMS V5.5-2**, emitting OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings linked via `vmslink` into standalone `vms_vm` executables.

## Features
- `<name>: PROCEDURE OPTIONS(MAIN); ... END [<name>];`
- `DECLARE` / `DCL` with `FIXED BINARY(31)` / `FIXED BIN(15)`, `FIXED DECIMAL(p,q)`, `FLOAT BINARY`, `CHARACTER(n) VARYING` / `CHAR(n) VAR`, `BIT(1)`, and `INITIAL(...)` / `INIT(...)`
- Hierarchical structures (`DCL 1 EMP, 2 NAME CHAR(32) VAR, 2 SALARY FIXED BIN(31);` with `EMP.NAME` access)
- Nested `PROCEDURE(...) [RETURNS(...)]` with `CALL` and `RETURN(...)`
- Control structures: `IF ... THEN ...; ELSE ...;`, `DO; ... END;`, `DO <v> = <start> TO <end> [BY <step>]; ... END;`, `DO WHILE(...); ... END;`, `DO UNTIL(...); ... END;`, `SELECT [(<expr>)]; WHEN (...) ...; OTHERWISE ...; END;`
- Stream I/O: `PUT SKIP LIST(...)`, `PUT LIST(...)`, `PUT SKIP EDIT(...)(...)`, `GET LIST(...)`

## Quick Start
```bash
make build
make demo
make test
```
