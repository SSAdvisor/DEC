# DEC VAX LISP V3.1-00 Common Lisp Compiler & REPL (`vaxlisp`)

Authentic implementation of **DEC VAX LISP V3.1-00** for OpenVMS VAX V5.5-2.

## Features
- Compiles `.LSP` / `.LISP` Common Lisp programs into OpenVMS `.OBJ` relocatable object modules and `.LST` listings for linking with `vmslink`.
- Supports `defun`, `defvar`, `defparameter`, `defconstant`, `setq`, `setf`, `let`, `let*`, `if`, `cond`, `when`, `unless`, `progn`, `dotimes`, `dolist`, `do`, `loop`, `format`, `mapcar`, `apply`, `funcall`, `lambda`, lexical closures, and list processing primitives.
- Interactive REPL (`VAX LISP V3.1 — Common Lisp for VAX/VMS` with `LISP>` prompt).
