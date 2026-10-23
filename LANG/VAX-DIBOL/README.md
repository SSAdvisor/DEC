# DEC VAX DIBOL V4.1 (`vaxdibol`) — VAX/VMS V5.5-2

Authentic **DEC VAX DIBOL V4.1** compiler (`compiler/vaxdibol` and `bootstrap/vaxdibol.py`) targeting the OpenVMS Linker (`vmslink`) and `vms_vm` runtime.

## Features
- Supports VAX DIBOL V4.1 `RECORD`, named records, `A`/`D`/`I` fields (`A<n>`, `D<n>`, `D<n>.<p>`, `I1`/`I2`/`I4`), `COMMON`, `EXTERNAL`, `SUBROUTINE`, `FUNCTION`, `PROC`
- Subprograms & I/O: `XCALL`, `CALL`, `RETURN`, `FRETURN`, `OPEN`, `WRITES`, `DISPLAY`, `READS`, `CLOSE`, `INCR`, `DECR`, `CLEAR`
- Structured control flow: `IF / THEN / BEGIN / END / ELSE`, `FOR / FROM / THRU / BY / DO`, `WHILE / DO`, `DO / UNTIL`, `USING / SELECT / ENDUSING`, `STOP`, `END`

## Build & Test
```bash
make build
make demo
make test
```
