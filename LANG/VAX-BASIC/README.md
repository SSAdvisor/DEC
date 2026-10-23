# DEC VAX BASIC V3.5 & OpenVMS VAX Linker V05-05

A native implementation of **DEC VAX BASIC V3.5** (`vaxbasic`) and the **OpenVMS VAX Linker V05-05** (`vmslink`) for **DEC VAX/VMS V5.5-2** (`OS/VMS/`), backed by a dedicated OpenVMS Image Activator VM (`vms_vm`).

## Architecture
- **VAX BASIC V3.5 Compiler (`compiler/vaxbasic` + `bootstrap/vaxbasic.py`)**:
  - Line-numberless and line-numbered structured programs (`PROGRAM <name>` ... `END PROGRAM`, `%TITLE`, `%IDENT`, `OPTION TYPE = EXPLICIT`)
  - Structured `RECORD <Type>` ... `END RECORD` types with `REC::FIELD` access
  - `DECLARE LONG`, `WORD`, `BYTE`, `SINGLE`, `DOUBLE`, `GFLOAT`, `DECIMAL`, `STRING`, and `CONSTANT`
  - `SELECT` / `CASE` (values, lists, `low TO high` ranges, relational `CASE`, `CASE ELSE`) / `END SELECT`
  - `IF` / `THEN` / `ELSEIF` / `ELSE` / `END IF`, `FOR` / `NEXT`, `WHILE` / `NEXT`, `UNTIL` / `NEXT`, `EXIT`, `ITERATE`
  - `WHEN ERROR IN` ... `USE` ... `END WHEN` exception blocks
  - `SUB` / `END SUB`, `FUNCTION` / `END FUNCTION`, `DEF` / `END DEF`, and multi-module `CALL`
  - Interactive VAX BASIC V3.5 environment (`Ready` prompt: `NEW`, `OLD`, `SAVE`, `LIST`, `COMPILE`, `RUN`, `HELP`, `EXIT`)
- **OpenVMS VAX Linker V05-05 (`linker/vmslink` + `bootstrap/vmslink.py`)**:
  - Links `.OBJ` object modules, `.OLB` object libraries (`/LIBRARY`, `/INCLUDE`), and `.OPT` linker options files (`IDENTIFICATION=`, `GSMATCH=`, `CLUSTER=`, `PSECT_ATTR=`, `UNIVERSAL=`, `/SHARE`)
  - Generates OpenVMS `.MAP` Image Map files (`/MAP`, `/FULL`, `/CROSS_REFERENCE`) with `Object Module Synopsis`, `Program Section Synopsis` (`$CODE` at P0 base `00000200`), `Symbol Cross-Reference Map`, and `Link Run Statistics`
  - Produces standalone OpenVMS `.EXE` images powered by `vms_vm`

## Quick Start
```bash
make build
make test
```
