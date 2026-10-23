# DEC VAX DSM V6.0-00 — Digital Standard MUMPS (`vaxdsm`)

Authentic implementation of **DEC VAX DSM V6.0-00** (Digital Standard MUMPS) for OpenVMS VAX V5.5-2.

## Features
- Compiles `.DSM` and `.M` MUMPS routines into OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings for linking with `vmslink`.
- Supports MUMPS commands (`SET`, `WRITE`, `NEW`, `KILL`, `IF`, `ELSE`, `FOR`, `DO`, `GOTO`, `QUIT`, `HALT`, `READ`) with single-letter abbreviations and `:cond` postconditionals.
- Supports hierarchical sparse local arrays and `^GLOBAL` B-tree arrays with `$DATA`, `$ORDER`, `$PIECE`, `$EXTRACT`, `$LENGTH`, `$FIND`, `$ASCII`, `$CHAR`.
- Interactive programmer prompt (`DEC VAX DSM V6.0-00 — Digital Standard MUMPS`, `DSM>` prompt).
