# DEC VAX COBOL V4.3 (`vaxcobol`) — VAX/VMS V5.5-2

Authentic **DEC VAX COBOL V4.3** compiler (`compiler/vaxcobol` and `bootstrap/vaxcobol.py`) targeting the OpenVMS Linker (`vmslink`) and `vms_vm` runtime.

## Features
- Supports both VAX COBOL Terminal Free-Format and ANSI Fixed-Format
- `IDENTIFICATION DIVISION`, `PROGRAM-ID`, `ENVIRONMENT DIVISION`, `DATA DIVISION`, `WORKING-STORAGE SECTION`, level numbers `01`/`05`/`77`, `PIC 9(n)`, `PIC S9(n)V99`, `PIC X(n)`, `VALUE`, `INITIALIZE`
- `PROCEDURE DIVISION`, paragraphs/sections, `DISPLAY`, `ACCEPT`, `MOVE`, `COMPUTE`, `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`
- Structured COBOL: `IF / ELSE / END-IF`, `EVALUATE / WHEN / WHEN OTHER / END-EVALUATE`, `PERFORM <para> [THRU <para2>]`, inline `PERFORM <n> TIMES ... END-PERFORM`, `PERFORM UNTIL <cond> ... END-PERFORM`, `PERFORM VARYING ... END-PERFORM`, `STOP RUN`

## Build & Test
```bash
make build
make demo
make test
```
