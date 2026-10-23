# DEC VAX SCAN V1.2-00 String Scanning & Pattern-Matching Compiler (`vaxscan`)

Authentic implementation of **DEC VAX SCAN V1.2-00** for OpenVMS VAX V5.5-2.

## Features
- Compiles `.SCN` string scanning modules into OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings for linking with `vmslink`.
- Supports `MODULE ... IDENT ... END MODULE`, `SET`, `MACRO`, `TOKEN`, `DECLARE`, `TRIGGER (<var> : STRING) := <pattern> ... END TRIGGER`, `PROCEDURE ... MAIN ... END PROCEDURE`, and `START SCAN INPUT STRING <expr> ... END SCAN`.
- Full procedural statements (`IF ... THEN ... ELSE ... END IF`, `WHILE ... DO ... END WHILE`, `FOR ... DO ... END FOR`, `WRITE`, `:=`) and string intrinsics (`LENGTH`, `INDEX`, `&`).
