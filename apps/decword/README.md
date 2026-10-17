# DECword/DP - Word & Data Processing System

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's **DECword/DP** (DECword / WPS-11 / WPS-PLUS), an integrated multi-user word processing and data processing system originally distributed for **DEC PDP-11 (RSTS/E, RSX-11M)** and **VAX/VMS** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: DECword V3.0 & DECword/DP (Word & Data Processing)
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E, RSX-11M), VAX-11 (VAX/VMS)
- **Historical Significance**: Introduced in 1980–1982, **DECword** and **DECword/DP** brought DEC's dedicated WPS-8 / DECmate word processing capabilities to multi-user PDP-11 RSTS/E systems. **DECword/DP** specifically combined full-featured **Word Processing (WP)** (document libraries, WPS rulers, margins, centering, headers/footers) with **Data Processing (DP)** (list processing, database record integration, and automated mail-merge) on the same PDP-11 system, paving the way for DEC's **ALL-IN-1** office automation platform.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine runtime.

---

## 2. Architecture & Document Processing Features

1. **Document Library & Category Architecture**:
   - `LIBRARY`: Published and reference documents.
   - `FINAL`: Finalized documents and form letter templates.
   - `DRAFT`: Work-in-progress engineering memos and notes.
   - `WASTEBASKET`: Documents marked for deletion (`D`).
   - `ALL`: Consolidated view of all documents across all categories.

2. **WPS Ruler & Page Formatting Engine**:
   - Configurable **Left Margin (`LM`)**, **Right Margin (`RM`)**, **Line Spacing (`1` single / `2` double)**, and **Page Length (`PL`)**.
   - Visual DEC WPS ruler display (`....L....T....1....T....2....T....3....T....4....T....5....T....6....T.R`).
   - Inline `.CENTER <text>` directive for automatic centering between active margins.
   - Configurable running **Header (`HEADER`)** and **Footer (`FOOTER`)** with page numbering.

3. **Data Processing (DP) List Processing & Mail-Merge**:
   - Built-in DP record table storing structured `<NAME>`, `<COMPANY>`, and `<SYSTEM>` fields.
   - Automated `MERGE` (`LISTPROC`) engine that merges form documents containing `<NAME>`, `<COMPANY>`, and `<SYSTEM>` tokens across all DP records.

4. **Interchange File Format (`DECWORD.DAT`)**:
   - Pipe-delimited flat file: `TITLE|AUTHOR|DATE|CATEGORY|STATUS|BODY`

---

## 3. Directory Layout

```
apps/decword/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── decword         # Compiled native ELF binary
│   ├── decworddp       # Symlink alias -> decword
│   └── wps             # Symlink alias -> decword
├── build/
│   └── decword.bobj    # Intermediate BASIC-PLUS-2 object
├── src/
│   └── decword.bas     # Native DEC BASIC-PLUS-2 source code (< 470 lines)
└── tests/
    ├── __init__.py     # Test package marker
    └── test_decword.py # Automated pytest test suite (14 test cases)
```

---

## 4. Command Reference & Syntax

### Interactive Mode (REPL)
Launch `decword` (or aliases `decworddp` / `wps`) without arguments to enter interactive mode:

```
$ ./bin/decword
================================================================================
    DECword/DP V3.0 - Word & Data Processing System
    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11
================================================================================
Type HELP for commands, or EXIT to quit.

WP> SAMPLE
[Sample DECword/DP library loaded - 4 documents, 3 DP records]

WP> DIR
================================================================================
  DECword/DP Document Library - Category: ALL
================================================================================
#   St  Category     Author          Date         Title
--------------------------------------------------------------------------------
1   *  LIBRARY      KEN.OLSEN       18-OCT-1982  PDP-11/70 RSTS/E V8.0 Product Overview
2      FINAL        WPS.SALES       19-OCT-1982  DECword/DP Customer Form Letter
3      DRAFT        G.BELL          20-OCT-1982  Maynard Mill Engineering Memo
4   D  WASTEBASKET  OPERATOR        10-OCT-1982  Preliminary WPS-8 Obsolete Draft
--------------------------------------------------------------------------------
  4 documents listed (* = Active, D = Deleted)
================================================================================

WP> FORMAT 1
================================================================================
     DECword/DP Document Processing System
--------------------------------------------------------------------------------
                        DIGITAL EQUIPMENT CORPORATION
                     PDP-11/70 RSTS/E V8.0 SPECIFICATION
     The PDP-11/70 running RSTS/E with DECword/DP delivers integrated
     word and data processing for up to 63 concurrent users.
     Supports VT100 terminals and LQP02 letter-quality printers.
--------------------------------------------------------------------------------
     Digital Equipment Corporation - Page 1
================================================================================

WP> MERGE 2
...
[List Processing complete: 3 merged documents generated]

WP> EXIT
```

### Complete Command Summary

| Command | Aliases | Description |
|---|---|---|
| `DIR [category]` | `INDEX`, `DIRECTORY` | Lists documents in the library (`ALL`, `LIBRARY`, `FINAL`, `DRAFT`, `WASTEBASKET`). |
| `SELECT <doc#>` | `EDIT` | Selects the active document for viewing, editing, or formatting. |
| `CREATE <title>, <auth>, <cat>` | `NEWDOC` | Creates a new document in the library and selects it. |
| `READ [doc#]` | `VIEW`, `LIST`, `TYPE` | Displays document metadata and numbered text lines. |
| `APPEND [text]` | `ADD` | Appends text line(s) (`~`-delimited in batch or interactive until `.`). |
| `DELLINE <line#>` | - | Deletes the specified line number from the active document. |
| `REPLACE <old>, <new>` | `SUBSTITUTE` | Searches and replaces `<old>` with `<new>` across the active document. |
| `FIND <pattern>` | `SEARCH` | Searches active document lines for `<pattern>` and displays matches. |
| `RULER [lm, rm, spacing]` | `MARGIN` | Displays the WPS ruler and configures Left Margin, Right Margin, and Spacing. |
| `HEADER <text>` | - | Sets the running page header text. |
| `FOOTER <text>` | - | Sets the running page footer text. |
| `FORMAT [doc#]` | `PRINT [ON <file>]`, `EXPORT <file>` | Formats and outputs the document to terminal or disk file. |
| `DPLIST` | `RECORDS` | Lists Data Processing (DP) records (`<NAME>`, `<COMPANY>`, `<SYSTEM>`). |
| `DPADD <name>, <comp>, <sys>` | - | Appends a new Data Processing record for List Processing / Mail-Merge. |
| `MERGE [doc#]` | `LISTPROC` | Merges the form document with all DP list records. |
| `STATS` | `COUNT` | Displays line, word, character, page, and merge token statistics. |
| `COPY [doc#]` | - | Duplicates a document into a new library slot. |
| `DELETE [doc#]` | `DEL` | Marks document as deleted and moves it to `WASTEBASKET`. |
| `PURGE` | - | Permanently removes all deleted (`WASTEBASKET`) documents. |
| `SAMPLE` | `DEMO` | Loads historical DECword/DP sample library and DP records. |
| `SAVE [file]` | - | Saves document library in pipe-delimited interchange format. |
| `LOAD [file]` | `IMPORT` | Loads document library from disk file. |
| `SHOW` | `STATUS` | Displays DECword/DP system status and active ruler configuration. |
| `CLEAR` | `RESET` | Clears all documents and DP records from memory. |
| `HELP` | `?` | Displays summary of all DECword/DP commands. |
| `EXIT` | `QUIT`, `BYE` | Exits the DECword/DP session. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/decword clean build
```

Run test suite:
```bash
make -C apps/decword test
# or directly:
pytest apps/decword/tests/
```

Run interactive session:
```bash
make -C apps/decword run
```
