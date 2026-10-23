# DEC PDP-11 APL-11 V2.1 Compiler & Workspace (`LANG/APL-11`)

Authentic Digital Equipment Corporation **PDP-11 APL-11 V2.1** Compiler and Interactive Workspace Environment for **RSTS/E V10.1-L**.

## Architecture
- **Frontend (`compiler/apl11.bas` -> `compiler/apl11` / `compiler/aplc`)**: Written in pure DEC BASIC-PLUS-2 and compiled with `basicc` and `basiclink`.
- **Dual Mode (`bootstrap/apl11.py`)**:
  1. **Compiler Mode**: Compiles `.APL` scripts into RSTS/E relocatable `.OBJ` modules linked via `basiclink` (`LINK`) into standalone `.TSK` executables on `rsts_vm`.
  2. **Interactive Workspace Mode**: Launches the classic 6-space indented APL-11 session supporting Unicode APL glyphs (`←`, `⍳`, `⍴`, `+/`, `×/`, `⌈/`, `⌊/`, `⌽`, `↑`, `↓`, `÷`, `×`, `∇`, `⍝`) and ASCII mnemonics (`<-`, `.IOTA`, `.RHO`, `+/`, `*/`, `.REV`, `.TAKE`, `.DROP`), user-defined `∇` functions, and system commands (`)WSID`, `)VARS`, `)FNS`, `)CLEAR`, `)SAVE`, `)LOAD`, `)ERASE`, `)OFF`).
