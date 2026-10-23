# DEC VAX APL V3.1-00 Compiler & Workspace (`vaxapl`)

Authentic implementation of **DEC VAX APL V3.1-00** for OpenVMS VAX V5.5-2.

## Features
- Compiles `.APL` source programs into OpenVMS `.OBJ` relocatable object modules and `.LST` compiler listings for linking with `vmslink`.
- Supports both Unicode APL glyphs (`←`, `⍳`, `⍴`, `+/`, `×/`, `⌈/`, `⌊/`, `⌽`, `∇`, `⎕←`, `⍝`) and DEC ASCII mnemonics (`<-`, `.IOTA`, `.RHO`, `.SUM`, `.PROD`, `.MAX`, `.MIN`, `.REV`, `QUAD<-`, `REM`).
- Interactive VAX APL workspace environment (`DEC VAX APL V3.1-00 [VAX/VMS] — CLEAR WS`) with `)CLEAR`, `)VARS`, `)FNS`, `)WSID`, `)SAVE`, `)LOAD`, `)ERASE`, `)OFF`, `)EXIT`.
