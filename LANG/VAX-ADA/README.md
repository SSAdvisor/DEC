# DEC VAX Ada V2.2 Compiler (`vaxada`)

Native implementation of the **DEC VAX Ada V2.2** compiler (`compiler/vaxada` + `bootstrap/vaxada.py`) for **DEC VAX/VMS V5.5-2**, emitting OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings linked via `vmslink` into standalone `vms_vm` executables.

## Features
- `with TEXT_IO; use TEXT_IO;` context clauses and `pragma IDENT("...");`
- `procedure <Name> is ... begin ... end [<Name>];`
- `type <Name> is record ... end record;`, `type <Name> is array (...) of ...;`, and `subtype` declarations
- Standard types (`Integer`, `Natural`, `Positive`, `Float`, `Boolean`, `String`) and `constant` declarations
- Nested `function` and `procedure` subprograms with `return`
- Control structures: `if ... then ... elsif ... then ... else ... end if;`, `case ... is when ... => ... when others => ... end case;`, `for <v> in [reverse] <lo> .. <hi> loop ... end loop;`, `while <cond> loop ... end loop;`, `loop ... exit when <cond>; ... end loop;`
- `Put_Line(...)`, `Put(...)`, `New_Line`, `Integer'Image(...)`, and `&` string concatenation

## Quick Start
```bash
make build
make demo
make test
```
