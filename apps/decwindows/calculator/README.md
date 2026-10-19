# DECwindows Calculator V3.0 (`DECW$CALC` / `dxcalc`)

**DECwindows Calculator V3.0** is a faithful native DEC BASIC-PLUS-2 implementation of the Digital Equipment Corporation DECwindows desktop calculator (`DECW$CALC` on VAX/VMS and OpenVMS, `dxcalc` on ULTRIX and DEC OSF/1, 1988–1995).

It provides scientific, financial, and programmer (Decimal / Hexadecimal / Octal) calculation modes, a memory register (`M`), and a printable audit paper tape.

---

## Features

- **Engineering Sample Tape (`SAMPLE` / `DEMO`)**:
  - Loads a 6-step DEC engineering calculation tape (`SET 1024`, `ADD 2048`, `MUL 4`, `DIV 3`, `STO`, `SUB 256`), setting `ACC = 3840` (`0xF00` / `0o7400`) and `MEM = 4096` (`0x1000` / `0o10000`).
- **Arithmetic & Scientific Operations (`SET`, `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `SQRT`, `SQR`)**:
  - Full accumulator arithmetic with division-by-zero protection (`%CALC-E-DIVZERO`) and integer square root / square functions.
- **Programmer Bitwise Logic & Multi-Radix (`AND`, `OR`, `XOR`, `BASE DEC|HEX|OCT`)**:
  - 16-bit bitwise logical operations and simultaneous Decimal, Hexadecimal (`0x...`), and Octal (`0o...`) display conversion.
- **Memory Register (`STO` / `MS`, `RCL` / `MR`, `M+`, `M-`, `MC`)**:
  - Standard DECwindows Calculator memory storage, recall, accumulation, and clear operations.
- **Financial Loan Analysis (`PMT <principal|rate%|years>` / `LOAN`)**:
  - Calculates annual and estimated monthly loan repayment amounts and records the result on the audit tape.
- **Audit Paper Tape (`TAPE` / `HISTORY` / `LIST`)**:
  - Displays every recorded operation step with its Decimal, Hexadecimal, and Octal result.
- **Motif / XUI Window Renderer (`DISPLAY [ON <file>]`, `EXPORT <file>`)**:
  - Renders the 78-column DECwindows Calculator Motif/XUI window with LCD multi-radix display, memory readout, visual keypad buttons, and status bar.
- **Persistence (`SAVE <file>`, `LOAD <file>`)**:
  - Saves and restores calculator state and paper tape history.

---

## Building and Testing

```bash
make -C apps/decwindows/calculator build
pytest apps/decwindows/calculator/tests/
```
