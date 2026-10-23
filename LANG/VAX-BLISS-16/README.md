# DEC VAX BLISS-16 V4.2 16-Bit Compatibility Systems Language

Authentic 16-bit DEC VAX BLISS-16 V4.2 Compiler (`bliss16`) targeting OpenVMS VAX V5.5-2 and `vmslink` / `vms_vm`.

## Features
- **16-Bit Compatibility Mode**: `creator: "VAX BLISS-16 V4.2"`, 16-bit word wrapping on integer literals, and full compatibility with `.B16` and `.BLI` sources.
- **Constructs**: `MODULE ... = BEGIN ... END ELUDOM`, `.VAR` explicit dereference, `LOCAL`, `OWN`, `GLOBAL`, `BIND`, `LITERAL`, `VECTOR`, `ROUTINE`, `INCR`/`DECR`, `WHILE`/`UNTIL`, `IF/THEN/ELSE`, `SELECTONE`, `TTY_PUT_MSG`, `LIB$PUT_OUTPUT`, `PRINT`.
