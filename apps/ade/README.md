# ADE - DEC Application Development Environment

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's **ADE** (Application Development Environment), an integrated departmental relational data manager, 4GL reporting system, and interactive business analytics tool originally distributed for **DEC PDP-11 (RSTS/E)** and **VAX/VMS** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: DEC ADE (Application Development Environment), ADE/RSTS, ADE/VMS
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E), VAX-11 (VAX/VMS)
- **Historical Significance**: Introduced by DEC in the early 1980s as a friendly departmental 4GL and end-user computing environment. Designed for non-programmers, business analysts, and departmental managers to rapidly define data structures, enter records, run queries, generate formatted reports with column totals, and render ASCII graphics without writing traditional code.
- **Dialect & Toolchain**: DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine environment.

---

## 2. Architecture & Data Storage

DEC ADE organizes departmental databases into two companion files for each table:

1. **Schema Definition File (`<name>.sch`)**:
   - Line 1: Number of fields (`N`).
   - Lines 2 to `N+1`: Field definition records formatted as `NAME|TYPE|WIDTH`.
   - **Supported Data Types**:
     - `C`: Character string (alphanumeric text).
     - `N`: Numeric (real or integer values for mathematical operations, totals, and graphs).
     - `D`: Date (calendar dates, e.g. `YYYY-MM-DD` or `DD-MMM-YYYY`).

2. **Data Record File (`<name>.dat`)**:
   - Pipe-delimited records matching the active schema.
   - Preserved across sessions and auto-saved upon every modifying transaction (`ADD`, `CHANGE`, `DELETE`, `SORT`, `IMPORT`).

---

## 3. Directory Layout

```
apps/ade/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── src/
│   └── ade.bas         # Native DEC BASIC-PLUS-2 implementation
└── tests/
    ├── __init__.py
    └── test_ade.py     # Automated pytest test suite (16 test cases)
```

---

## 4. Command Reference & Syntax

### Interactive Mode (REPL)
Launch `ade` without arguments to enter the interactive shell:

```bash
$ ./bin/ade
================================================================================
    ADE V3.0 - Application Development Environment
    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E
================================================================================
Type HELP for commands, or EXIT to quit.

ADE> HELP
```

### Command Line & Chained Execution
Commands may be passed directly as arguments, and multiple commands can be chained using semicolons (`;`):

```bash
$ ./bin/ade "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); ADD 101,WIDGET,25,100; LIST"
```

### Complete Command Catalog

| Command | Arguments | Description |
|:---|:---|:---|
| `CREATE` / `DEFINE` | `<name> [(specs)]` | Creates a new database table. Optional `(NAME:TYPE:WIDTH,...)` specifies schema; defaults to `(ID:N:6,NAME:C:20,DEPT:C:12,SALARY:N:10,HIREDATE:D:10)`. |
| `USE` / `OPEN` | `<name>` | Opens an existing database table and loads its schema and records. |
| `ADD` / `ENTER` | `[val1,val2,...]` | Adds a new record. Accepts comma-separated values or prompts field-by-field interactively. |
| `LIST` / `BROWSE` | None | Displays all records in a formatted ASCII table with column headers and total count. |
| `FIND` / `SEARCH` | `<field> <val>` | Case-insensitive substring search matching records in the designated column. |
| `CHANGE` / `MODIFY` | `<rec_num>` | Modifies fields in the specified record interactively (press Enter to retain current value). |
| `DELETE` | `<rec_num>` | Deletes the specified record number and shifts subsequent records. |
| `SORT` | `<field> [ASC\|DESC]` | Sorts table records by the specified field alphabetically or numerically (default: `ASC`). |
| `STATS` / `TOTAL` | `<field>` | Calculates count, sum, average/mean, minimum, and maximum for numeric columns. |
| `REPORT` | `[title]` | Generates a formatted report with custom header, records, and automatic numeric column totals. |
| `GRAPH` / `CHART` | `<label_fld> <val_fld>` | Renders a horizontal ASCII bar chart (`*` bars) scaled to 50 columns. |
| `EXPORT` | `<filename>` | Exports table records to an external delimiter-separated text file. |
| `IMPORT` | `<filename>` | Imports records from an external text file and appends them to the active database. |
| `SHOW` | None | Displays active database status, file paths, field definitions, and record count. |
| `HELP` | None | Displays available commands and quick reference guide. |
| `EXIT` / `QUIT` / `BYE` | None | Exits the ADE environment. |

---

## 5. Examples

### Creating a Table and Entering Records
```
ADE> CREATE EMPLOYEES (ID:N:4,NAME:C:15,DEPT:C:10,SALARY:N:8)
Database 'EMPLOYEES' created successfully (Fields: 4).

ADE> ADD 101,ALICE,ENGINEERING,75000
Record 1 added.

ADE> ADD 102,BOB,MARKETING,62000
Record 2 added.

ADE> ADD 103,CHARLIE,ENGINEERING,81000
Record 3 added.
```

### Statistical Analysis & Reporting
```
ADE> STATS SALARY
================================================================================
    Statistical Analysis: SALARY (Database: EMPLOYEES)
--------------------------------------------------------------------------------
Records Analyzed:   3
Total / Sum:        218000
Average / Mean:     72666.7
Minimum Value:      62000
Maximum Value:      81000
================================================================================

ADE> REPORT Department Payroll Summary
================================================================================
    DEC ADE REPORT: Department Payroll Summary
    Database: EMPLOYEES          Records: 3
--------------------------------------------------------------------------------
REC#  ID   NAME            DEPT       SALARY   
--------------------------------------------------------------------------------
1     101  ALICE           ENGINEERING 75000    
2     102  BOB             MARKETING  62000    
3     103  CHARLIE         ENGINEERING 81000    
--------------------------------------------------------------------------------
TOTAL 306                             218000   
================================================================================
```

### ASCII Horizontal Bar Chart
```
ADE> GRAPH NAME SALARY
================================================================================
    DEC ADE Bar Chart: EMPLOYEES (NAME vs SALARY)
--------------------------------------------------------------------------------
ALICE           | ********************************************** (75000)
BOB             | ************************************** (62000)
CHARLIE         | ************************************************** (81000)
--------------------------------------------------------------------------------
Scale: 1 '*' = 1620 units
================================================================================
```

---

## 6. Build and Test Instructions

From within the `apps/ade/` sub-project directory:

```bash
# Build the application
make build

# Run the test suite
make test

# Launch the interactive application
make run

# Clean build artifacts
make clean
```
