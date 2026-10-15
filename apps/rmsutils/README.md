# RMSUTILS - DEC RMS-11 Utilities Suite

A native DEC **BASIC-PLUS-2** implementation of the official Digital Equipment Corporation **RMS-11 Utilities Suite**, providing comprehensive design, definition, high-speed loading, conversion, backup, restore, and inspection facilities for sequential and SQLite-backed **RMS (Record Management Services)** files.

---

## 1. Historical Background & Heritage

- **Original Suite**: DEC RMS-11 (Record Management Services for PDP-11)
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Operating Systems**: DEC PDP-11 (RSTS/E, RSX-11M, RSX-11M-PLUS), VAX-11 (VAX/VMS)
- **Included Utilities**:
  - `RMSDES`: RMS-11 File Design Utility
  - `RMSDEF`: RMS-11 File Definition / Creation Utility
  - `RMSIFL`: RMS-11 Indexed File Load Utility
  - `RMSCNV`: RMS-11 File Convert Utility
  - `RMSBCK`: RMS-11 File Backup Utility
  - `RMSRST`: RMS-11 File Restore Utility
  - `RMSDSP`: RMS-11 File Display Utility
  - `RMSUTILS`: Master Suite Launcher
- **Dialect**: DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E VM runtime.

---

## 2. Architecture & SQLite RMS Storage

In DEC BASIC-PLUS-2 on modern systems, RMS Indexed files are mapped to structured SQLite databases:

```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    data BLOB
);
```

- **MAP Buffer**: Uses `MAP (REC_BUF) STRING MAP_LINE$ = 255%` for zero-copy record transfer between BASIC buffers and SQLite records.
- **Indexed Access**: Handled via `OPEN ... ORGANIZATION INDEXED FIXED, PRIMARY KEY MAP_LINE$, MAP REC_BUF`, using `GET` and `PUT` statements.
- **Stream Sequential**: Sequential files are standard newline-delimited stream text files.
- **Portability**: All binaries operate standalone without external database engines.

---

## 3. Directory Layout

```
apps/rmsutils/
├── README.md               # This documentation
├── Makefile                # Sub-project build and test automation
├── bin/                    # Compiled native executables (8 binaries)
├── build/                  # Intermediate object files (.bobj)
├── src/
│   ├── rmsdes.bas          # RMSDES file design utility
│   ├── rmsdef.bas          # RMSDEF file definition utility
│   ├── rmsifl.bas          # RMSIFL indexed file load utility
│   ├── rmscnv.bas          # RMSCNV format convert utility
│   ├── rmsbck.bas          # RMSBCK backup container utility
│   ├── rmsrst.bas          # RMSRST restore utility
│   ├── rmsdsp.bas          # RMSDSP file display and inspection utility
│   └── rmsutils.bas        # Master launcher & dispatcher
└── tests/
    └── test_rmsutils.py    # Dedicated pytest test suite (10 test cases)
```

---

## 4. Utilities Reference

### 1. `RMSDES` - File Design Utility
Generates structured `.DES` design specification files defining file organization, record size, and key structures.

**Usage**:
```bash
./bin/rmsdes "spec.des INDEXED 255 1 4"
# Or using switches:
./bin/rmsdes "spec.des/IDX/SIZ:255/POS:1/LEN:4"
```

### 2. `RMSDEF` - File Definition Utility
Creates an empty RMS file (either indexed SQLite or sequential) based on a `.DES` specification or inline switches.

**Usage**:
```bash
./bin/rmsdef "output.idx=spec.des"
# Or inline:
./bin/rmsdef "output.idx/ORG:INDEXED/SIZ:255/KEY:(POS:1,SIZ:4)"
```

### 3. `RMSIFL` - Indexed File Load Utility
High-speed bulk loader that reads sequential records, sorts by primary key, rejects duplicate keys, and populates the target RMS indexed file.

**Usage**:
```bash
./bin/rmsifl "target.idx=source.txt"
```

### 4. `RMSCNV` - File Convert Utility
Converts files between RMS Indexed and sequential stream formats, reorganizing records and optionally writing an exceptions log.

**Usage**:
```bash
# Convert Indexed to Sequential:
./bin/rmscnv "report.txt=data.idx/SEQ"

# Convert Sequential to Indexed:
./bin/rmscnv "data.idx=raw.txt/IDX"
```

### 5. `RMSBCK` - File Backup Utility
Creates portable, verified `.BCK` container files containing file organization metadata, record counts, checksums, and record data.

**Usage**:
```bash
./bin/rmsbck "archive.bck=data.idx"
```

### 6. `RMSRST` - File Restore Utility
Restores RMS indexed or sequential files from a `.BCK` container, verifying record counts and data integrity.

**Usage**:
```bash
./bin/rmsrst "restored.idx=archive.bck"
```

### 7. `RMSDSP` - File Display Utility
Inspects and reports file organization, record sizes, total record counts, minimum and maximum key values, and sample records.

**Usage**:
```bash
./bin/rmsdsp "data.idx"
```

### 8. `RMSUTILS` - Master Launcher
Unified launcher providing both CLI dispatch and an interactive menu.

**CLI Usage**:
```bash
./bin/rmsutils rmsdsp data.idx
./bin/rmsutils rmsifl data.idx=records.txt
```

**Interactive Menu**:
```bash
./bin/rmsutils
```

---

## 5. End-to-End Pipeline Example

```bash
# 1. Design a new RMS indexed file specification:
./bin/rmsdes "emp.des INDEXED 255 1 4"

# 2. Define and create the empty indexed file:
./bin/rmsdef "emp.idx=emp.des"

# 3. Fast load employee records:
./bin/rmsifl "emp.idx=employees.txt"

# 4. Display file attributes and verify contents:
./bin/rmsdsp "emp.idx"

# 5. Create a verified backup container:
./bin/rmsbck "emp.bck=emp.idx"

# 6. Restore to a new indexed file:
./bin/rmsrst "emp_restored.idx=emp.bck"

# 7. Convert restored file to sequential text report:
./bin/rmscnv "emp_report.txt=emp_restored.idx/SEQ"
```

---

## 6. Building and Testing

### Build
Compile all 8 utilities with `basicc` and link with `basiclink`:
```bash
make -C apps/rmsutils build
```

### Test
Run the dedicated automated test suite:
```bash
make -C apps/rmsutils test
```

### Run
Launch the interactive RMS master menu:
```bash
make -C apps/rmsutils run
```
