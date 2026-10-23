# DEC VAX FORTRAN V5.5 (`vaxfor`) — VAX/VMS V5.5-2

Authentic **DEC VAX FORTRAN V5.5** compiler (`compiler/vaxfor` and `bootstrap/vaxfor.py`) targeting the OpenVMS Linker (`vmslink`) and `vms_vm` runtime.

## Features
- Both fixed-format and free-form VAX FORTRAN V5.5 syntax with `!` inline comments
- Data types: `BYTE`, `INTEGER*2`, `INTEGER*4`, `REAL*4`, `REAL*8`, `DOUBLE PRECISION`, `CHARACTER*n`, `LOGICAL`, `PARAMETER (...)`, `DIMENSION`, `DATA`
- Structured records: `STRUCTURE /name/ ... END STRUCTURE` and `RECORD /name/ var` with `var.field` access
- Structured control flow: `DO ... END DO`, `DO label var = start, end [, step]`, `DO WHILE (...)`, `IF (...) THEN / ELSE IF / ELSE / END IF`, `SELECT CASE / CASE / CASE DEFAULT / END SELECT`
- Subprograms & I/O: `SUBROUTINE`, `FUNCTION`, `CALL`, `RETURN`, `PRINT *`, `WRITE(*,*)`, `READ(*,*)`, `FORMAT`

## Build & Test
```bash
make build
make demo
make test
```
