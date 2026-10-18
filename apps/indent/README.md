# INDENT - DEC BASIC-PLUS-2 Source Formatter & Structure Analyzer

A native DEC **BASIC-PLUS-2** implementation of **INDENT** (**Source Code Pretty-Printer, Formatter & Structure Analyzer**), an interactive and batch source code indentation, case-normalization, and block-structure verification utility originally distributed for **DEC PDP-11 (RSTS/E, RSX-11M)** and **VAX/VMS** systems via DEC and the DECUS (Digital Equipment Computer Users Society) software library.

---

## 1. Historical Background & Heritage

- **Original Utility**: `INDENT.BAS` / `BP2FMT` / `PRETTY` (RSTS/E & DECUS PDP-11 BASIC-PLUS / BASIC-PLUS-2 Source Formatter)
- **Manufacturer / Origin**: Digital Equipment Corporation & DECUS PDP-11 Program Library (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E, RSX-11M), VAX-11 (VAX/VMS)
- **Historical Significance**: As BASIC-PLUS and BASIC-PLUS-2 evolved from unstructured line-numbered BASIC into block-structured languages supporting `SUB ... END SUB`, `FUNCTION ... END FUNCTION`, `FOR ... NEXT`, `WHILE ... NEXT`, `UNTIL ... NEXT`, and `SELECT ... CASE ... END SELECT`, **INDENT** became an essential programmer's workbench utility on RSTS/E and VAX/VMS. It aligned line numbers into uniform columns, indented nested blocks according to configurable step widths, normalized lowercase/mixed-case keywords into standard DEC uppercase conventions, audited block nesting balance, and generated control-flow cross-reference listings.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine runtime.

---

## 2. Architecture & Subsystems

1. **Source Buffer & File Manager (`SAMPLE`, `RAW` / `LIST`, `ADDLINE`, `DELLINE`, `SAVE`, `LOAD`)**:
   - Manages `.BAS` source files in an interactive editing buffer (`PROGRAM.BAS` or `PAYROLL.BAS`).
   - Supports loading existing `.BAS` files from disk, appending or deleting statements, and saving raw source buffers.

2. **Block-Structure Pretty-Printer (`FORMAT` / `INDENT` / `PRETTY`, `PRINT ON` / `EXPORT`, `STEP`, `MARGIN`, `CASE`)**:
   - Separates leading BASIC line numbers from statement bodies and formats line numbers in a fixed 6-character left column.
   - Automatically computes hierarchical indentation across `SUB`/`FUNCTION`/`DEF`, `FOR`/`WHILE`/`UNTIL`, and `SELECT`/`CASE`/`END SELECT` blocks.
   - Supports configurable indentation step width (`1`..`8` spaces), base margin (`0`..`12` spaces), and casing mode (`UPPER` vs `ASIS`).

3. **Structural Nesting Auditor (`CHECK` / `ANALYZE` / `VERIFY`)**:
   - Verifies that all block openers (`SUB`, `FOR`, `WHILE`, `UNTIL`, `SELECT`) and block closers (`END SUB`, `NEXT`, `END SELECT`) are balanced.
   - Reports total lines, comment lines (`REM` / `!`), branch statements (`GOTO` / `GOSUB`), maximum nesting depth, and any unclosed or unmatched block errors.

4. **Control-Flow & Nesting Cross-Reference (`XREF` / `LINES` / `TABLE`)**:
   - Produces a line-by-line structural table showing Buffer #, BASIC Line #, Nesting Level (`L0`..`Ln`), Construct Classification (`SUB-OPEN`, `LOOP-OPEN`, `SEL-CASE`, `BRANCH`, `COMMENT`, `STMT`), and `GOTO`/`GOSUB` branch target line numbers.

---

## 3. Directory Layout

```
apps/indent/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── indent          # Compiled native ELF binary
│   ├── bp2fmt          # Symlink alias -> indent
│   └── pretty          # Symlink alias -> indent
├── build/
│   └── indent.bobj     # Intermediate BASIC-PLUS-2 object
├── src/
│   └── indent.bas      # Native DEC BASIC-PLUS-2 source code (< 470 lines)
└── tests/
    ├── __init__.py     # Test package marker
    └── test_indent.py  # Automated pytest test suite (14 test cases)
```

---

## 4. Command Reference & Syntax

| Command | Aliases | Description |
|---|---|---|
| `SAMPLE` | `DEMO` | Loads the sample DEC BASIC-PLUS-2 payroll calculation module (`PAYROLL.BAS`). |
| `RAW` | `LIST`, `SOURCE` | Displays the unformatted raw source buffer. |
| `FORMAT` | `INDENT`, `PRETTY` | Pretty-prints the structured BASIC-PLUS-2 source listing to the terminal. |
| `PRINT ON <file>` | `EXPORT <file>` | Writes the formatted and indented BASIC-PLUS-2 source to a disk file. |
| `CHECK` | `ANALYZE`, `VERIFY` | Audits block structure balance and reports nesting metrics and errors. |
| `XREF` | `LINES`, `TABLE` | Displays the line-by-line nesting level and branch target cross-reference table. |
| `STEP <1..8>` | `WIDTH` | Sets the indentation step width in spaces per nesting level (default: `4`). |
| `MARGIN <0..12>` | - | Sets the base left margin after the line number column (default: `2`). |
| `CASE <UPPER\|ASIS>` | - | Sets statement casing normalization (`UPPER` or `ASIS`). |
| `ADDLINE <stmt>` | `ADD` | Appends a BASIC-PLUS-2 source line to the buffer. |
| `DELLINE <#>` | `DELETE`, `DEL` | Deletes a line from the source buffer by buffer index. |
| `SAVE [file]` | - | Saves the raw source buffer to disk. |
| `LOAD [file]` | `IMPORT` | Loads a `.BAS` source file from disk into the buffer. |
| `SHOW` | `STATUS` | Displays current INDENT configuration and buffer status. |
| `CLEAR` | `RESET` | Clears the source buffer. |
| `HELP` | `?` | Displays summary of all available INDENT commands. |
| `EXIT` | `QUIT`, `BYE` | Exits the INDENT session. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/indent clean build
```

Run test suite:
```bash
make -C apps/indent test
# or directly:
pytest apps/indent/tests/
```

Run interactive session:
```bash
make -C apps/indent run
```
