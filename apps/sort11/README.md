# SORT-11 - DEC RMS File Sort & Re-Indexing Utility

A native DEC **BASIC-PLUS-2** implementation of the classic Digital Equipment Corporation **SORT-11** utility, featuring support for sequential stream files and SQLite-backed **RMS (Record Management Services)** indexed files.

---

## 1. Historical Background & Heritage

- **Original Utility**: SORT-11 / RMS-11 Sort Utility
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E, RSX-11M, RSX-11M-PLUS), VAX-11 (VAX/VMS)
- **Primary Purpose**: High-performance sorting, record selection, and index generation for RMS-11 file organizations (Sequential, Relative, and Indexed).
- **Current Dialect**: DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` under the RSTS/E virtual machine runtime.

---

## 2. RMS Architecture & SQLite Storage

In DEC BASIC-PLUS-2 and the RSTS/E VM environment, RMS Indexed files are mapped to SQLite-backed storage databases:

```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    data BLOB
);
```

- **MAP Buffer**: `MAP (REC_BUF) STRING MAP_LINE$ = 255%` maps record buffers directly to SQLite table records.
- **Sequential Input / Output**: Stream-based ASCII text records separated by standard newlines.
- **Indexed Input / Output**: SQLite storage accessed via `OPEN ... ORGANIZATION INDEXED FIXED, PRIMARY KEY MAP_LINE$, MAP REC_BUF`, using `GET #n%` for sequential retrieval and `PUT #n%` for record insertion.
- **Auto-Detection**: Input and output files ending in `.IDX` or `.idx` are automatically identified as RMS Indexed databases.

---

## 3. Directory Layout

```
apps/sort11/
├── README.md           # This documentation
├── Makefile            # Sub-project build and test automation
├── src/
│   └── sort11.bas      # DEC BASIC-PLUS-2 source code
└── tests/
    └── test_sort11.py  # Dedicated pytest test suite (9 test cases)
```

---

## 4. Command Line & Interactive Usage

### DEC Command String Syntax
The primary interface follows DEC PDP-11 / RSTS/E CLI conventions:

```bash
./bin/sort11 "OUTFILE=INFILE/KEY:(POS:start,SIZ:length,order,type)[/RMS]"
```

- **`POS:start`**: 1-indexed starting character position of the sort key (default: `1`).
- **`SIZ:length`**: Number of characters in the sort key (default: `10`).
- **`ASC` | `DESC`**: Sort order (Ascending or Descending; default: `ASC`).
- **`NUM` | `CH`**: Comparison type (`NUM` for numeric values, `CH` for alphanumeric character order; default: `CH`).
- **`/RMS`**: Forces output format to SQLite-backed RMS Indexed file (or auto-detected via `.IDX` file extension).

### Positional Syntax
Simple positional arguments are also supported:

```bash
./bin/sort11 "INFILE OUTFILE"
```

### Interactive Prompt Wizard
When invoked without arguments, SORT-11 launches an interactive configuration wizard:

```
SORT-11 V3.0 - DEC RMS Sort Utility

Input file: input.txt
Output file: sorted.txt
Input format (1=Sequential, 2=RMS Indexed) [1]: 1
Output format (1=Sequential, 2=RMS Indexed) [1]: 1
Key start position [1]: 1
Key length [10]: 4
Sort order (A=Ascending, D=Descending) [A]: A
Key type (C=Character, N=Numeric) [C]: N
```

---

## 5. Examples

### 1. Numeric Sort (Ascending)
Sort sequential file by 4-digit ID at position 1:
```bash
./bin/sort11 "sorted.txt=input.txt/KEY:(POS:1,SIZ:4,ASC,NUM)"
```

### 2. Character Sort (Descending)
Sort sequential file by surname starting at column 10:
```bash
./bin/sort11 "sorted.txt=input.txt/KEY:(POS:10,SIZ:15,DESC,CH)"
```

### 3. Sequential to RMS Indexed Conversion
Sort raw text records and populate an SQLite RMS indexed database:
```bash
./bin/sort11 "records.idx=raw_data.txt/KEY:(POS:1,SIZ:6,ASC,CH)/RMS"
```

### 4. RMS Indexed to Sequential Export
Read from an RMS SQLite database and generate a sorted text report:
```bash
./bin/sort11 "report.txt=records.idx/KEY:(POS:1,SIZ:6,DESC,NUM)"
```

---

## 6. Building and Testing

### Build
Compile `sort11.bas` and link into standalone binary:
```bash
make build
```

### Test
Run the dedicated test suite verifying builds, sequential sorting, RMS SQLite indexing, conversions, and interactive wizard:
```bash
make test
```

### Run
Launch SORT-11 interactively:
```bash
make run
```
