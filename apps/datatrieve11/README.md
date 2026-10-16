# DATATRIEVE-11 - DEC Query, Report & Data Management System

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's famous **DATATRIEVE-11** (DTR-11), an interactive 4GL query language, report writer, and data management system originally distributed for **DEC PDP-11 (RSX-11M, RSX-11M-PLUS, RSTS/E)** and **VAX/VMS** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: DEC DATATRIEVE-11 (DTR-11) / VAX DATATRIEVE
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSX-11M, RSX-11M-PLUS, RSTS/E), VAX-11 (VAX/VMS)
- **Historical Significance**: First released by DEC in the late 1970s and 1980s, DATATRIEVE was DEC's premier Fourth Generation Language (4GL). It became an industry standard query and reporting tool across thousands of PDP-11 and VAX installations. The famous sample domain **YACHTS** (containing classic sailboats: Alberg, Cape Dory, Pearson, Tartan, Valiant, Coronado, Swan, Morgan) was used in all DEC DATATRIEVE user manuals, training courses, and trade show demonstrations.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine environment.

---

## 2. Architecture & Data Storage

DATATRIEVE-11 organizes data into **Domains** and **Records**:

1. **Domain Schema File (`<DOMAIN>.sch`)**:
   - Line 1: Number of fields (`N`).
   - Lines 2 to `N+1`: Field specifications formatted as `NAME|TYPE|WIDTH`.
   - **Supported Data Types**:
     - `C`: Character string (alphanumeric text).
     - `N`: Numeric (real or integer values for mathematical operations, sorting, and ASCII plotting).

2. **Domain Data File (`<DOMAIN>.dat`)**:
   - Pipe-delimited records matching the active schema.
   - When the classic DEC domain `YACHTS` is readied for the first time (`READY YACHTS`), DATATRIEVE-11 automatically initializes `YACHTS.sch` and `YACHTS.dat` with the 8 historical DEC demonstration yachts.

3. **Collections & Queries**:
   - Queries with `FIND` construct a dynamic **Collection** (subset of records matching criteria).
   - Subsequent verbs (`PRINT`, `SELECT`, `SORT`, `MODIFY`, `ERASE`, `TOTAL`, `REPORT`, `PLOT`) operate on the active collection.

---

## 3. Directory Layout

```
apps/datatrieve11/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── datatrieve11    # Compiled binary
│   ├── dtr             # Symlink -> datatrieve11
│   └── dtr11           # Symlink -> datatrieve11
├── build/
│   └── datatrieve11.bobj # Intermediate BASIC-PLUS-2 object
├── src/
│   └── datatrieve11.bas  # Native DEC BASIC-PLUS-2 source (< 470 lines)
└── tests/
    └── test_datatrieve11.py # Automated pytest test suite (16 test cases)
```

---

## 4. Command Reference & Syntax

### Interactive Mode (REPL)
Launch `datatrieve11` (or `dtr` / `dtr11`) without arguments to enter the interactive shell:

```bash
$ ./bin/datatrieve11
================================================================================
    DATATRIEVE-11 V3.0 - Query, Report & Data Management System
    Digital Equipment Corporation (DEC) PDP-11 / RSX-11M / RSTS/E
================================================================================
Type HELP for commands, or EXIT to quit.

DTR> READY YACHTS
[Domain YACHTS readied - 8 records available]

DTR> PRINT ALL
MANUFACTURER    MODEL     RIG       LENGTH  BEAM    PRICE     
--------------------------------------------------------------
ALBERG          37        SLOOP         37      10     36000  
CAPE DORY       28        SLOOP         28       9     24500  
PEARSON         30        SLOOP         30      10     29000  
TARTAN          34        SLOOP         34      10     45000  
VALIANT         40        CUTTER        40      12     85000  
CORONADO        35        KETCH         35      10     38000  
SWAN            48        SLOOP         48      13    165000  
MORGAN          38        SLOOP         38      11     42000  
--------------------------------------------------------------
[8 of 8 record(s) displayed]

DTR> EXIT
```

### Command-Line & Chained Batch Execution
Commands can be chained using semicolons (`;`) in CLI mode:

```bash
$ ./bin/dtr "READY YACHTS; FIND WITH PRICE < 50000; PRINT ALL; EXIT"
```

### Complete Command Catalog

| Command | Arguments | Description |
|:---|:---|:---|
| `READY` / `OPEN` | `[<domain>]` | Opens and loads a domain (defaults to sample domain `YACHTS`). |
| `FINISH` / `CLOSE` | None | Flushes all modifications to disk and closes the active domain. |
| `SHOW` | `DOMAINS` \| `RECORDS` \| `COLLECTIONS` \| `ALL` | Displays domain list, record layout, collection status, or general state. |
| `DEFINE DOMAIN` | `<name>` | Defines a new domain with default or custom schema. |
| `FIND` / `SEARCH` | `[ALL] [WITH <field> <op> <val>] [SORTED BY <field>]` | Queries records into the active collection. Operators: `=`, `<>`, `!=`, `>`, `<`, `>=`, `<=`, `CONTAINING`. |
| `PRINT` / `LIST` | `[ALL]` \| `[FIRST <n>]` | Displays records in active collection in a formatted ASCII table. |
| `SELECT` | `[<rec#>]` | Selects and inspects individual record fields. |
| `SORT` | `[BY] <field> [ASC\|DESC]` | Sorts collection ascending (default) or descending by field. |
| `STORE` / `ADD` | None | Interactively prompts for fields and adds a new record. |
| `MODIFY` / `CHANGE` | `<field> = <val>` | Updates field value across all records in current collection. |
| `ERASE` / `DELETE` | `[ALL]` | Deletes collection records from the active domain. |
| `TOTAL` / `STATS` | `[<numeric_field>]` | Computes Count, Total, Average, Minimum, and Maximum for numeric field. |
| `REPORT` | `[ON <file>]` | Produces formatted tabular report with column headers and total count. |
| `PLOT` / `GRAPH` | `[<lbl_fld>] [<val_fld>]` | Renders ASCII horizontal bar chart scaled to maximum value. |
| `EXPORT` / `EXTRACT`| `<file>` | Exports current collection to pipe-delimited text file. |
| `IMPORT` | `<file>` | Imports external pipe-delimited text file into active domain. |
| `HELP` | None | Displays quick command summary. |
| `EXIT` / `QUIT` / `BYE` | None | Saves domain and exits. |

---

## 5. Building & Testing

```bash
# Build binary and symlinks
make -C apps/datatrieve11 build

# Run automated test suite
pytest apps/datatrieve11/tests/test_datatrieve11.py -v
```
