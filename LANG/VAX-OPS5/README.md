# DEC VAX OPS5 V2.2-00 Rule-Based Production System (`vaxops5`)

Authentic implementation of **DEC VAX OPS5 V2.2-00** (Forgy Rete Production System Language) for OpenVMS VAX V5.5-2.

## Features
- Compiles `.OPS` production programs into OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings for linking with `vmslink`.
- Supports `(literalize ...)`, `(vector-attribute ...)`, `(strategy lex|mea)`, `(p <name> <lhs> --> <rhs>)`, positive and negated `-` condition elements, relational predicates (`=`, `<>`, `<`, `>`, `<=`, `>=`, `<< ... >>`), and RHS actions (`make`, `modify`, `remove`, `write`, `bind`, `compute`, `halt`).
- Interactive shell (`DEC VAX OPS5 V2.2-00 — Production System Environment`, `OPS5>` prompt) with `(make ...)`, `(wm)`, `(pm)`, `(run [n])`, `(reset)`, `(watch 0|1|2)`, `(exit)`.
