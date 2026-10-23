# DEC VAX BLISS-32 V4.7 Systems Implementation Language

Authentic 32-bit DEC VAX BLISS-32 V4.7 Compiler (`bliss32`) targeting OpenVMS VAX V5.5-2 and `vmslink` / `vms_vm`.

## Features
- **Module & Declarations**: `MODULE <name> (IDENT = '...', MAIN = <routine>) = BEGIN ... END ELUDOM`, `LOCAL`, `GLOBAL`, `OWN`, `BIND`, `LITERAL`, `VECTOR[...]`, `INITIAL(...)`, `UPLIT(...)`.
- **Explicit Dereference & Operators**: Authentic BLISS `.VAR` fetch operator on RHS expressions (`X = .X + 1`), relational operators (`EQL`, `NEQ`, `LSS`, `LEQ`, `GTR`, `GEQ` and `==`, `!=`, `<`, `<=`, `>`, `>=`), logical (`AND`, `OR`, `XOR`, `EQV`, `NOT`).
- **Control Structures & Routines**: `ROUTINE <name>(...) = BEGIN ... END`, `GLOBAL ROUTINE`, `IF ... THEN ... ELSE ...`, `INCR <v> FROM <lo> TO <hi> [BY <s>] DO ...`, `DECR <v> FROM <hi> TO <lo> [BY <s>] DO ...`, `WHILE <cond> DO ...`, `UNTIL <cond> DO ...`, `SELECTONE <expr> OF SET [<val>]: ...; [OTHERWISE]: ...; TES`, `LEAVE`, `EXITLOOP`, `RETURN`, `TTY_PUT_MSG`, `LIB$PUT_OUTPUT`, `PRINT`.
