# DEC VAX RPG II V2.2 (`vaxrpg`) — VAX/VMS V5.5-2

Authentic **DEC VAX RPG II V2.2** compiler (`compiler/vaxrpg` and `bootstrap/vaxrpg.py`) targeting the OpenVMS Linker (`vmslink`) and `vms_vm` runtime.

## Features
- Supports VAX RPG II V2.2 Control (`H`), File (`F`), Input (`I`), Calculation (`C`), and Output (`O`) specification forms
- Opcodes: `ADD`, `SUB`, `MULT`, `DIV`, `MVR`, `Z-ADD`, `Z-SUB`, `MOVE`, `MOVEL`, `COMP`, `SETON`, `SETOF`, `EXSR`, `BEGSR`, `ENDSR`, `DO`, `END`, `GOTO`, `TAG`, `EXCPT`, `DSPLY`
- Indicators: `01`–`99`, `LR`, `1P`, `H1`–`H9` (including negated `N01`–`N99`, `NLR`, `N1P`, `NH1`–`NH9`)

## Build & Test
```bash
make build
make demo
make test
```
