# DECgraph - Business & Scientific Graphics Presentation System

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's **DECgraph**, an interactive charting and presentation graphics system originally distributed for **DEC PDP-11 (RSTS/E, RSX-11M)** and **VAX/VMS** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: DECgraph V3.0
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E, RSX-11M, RSX-11M-PLUS), VAX-11 (VAX/VMS)
- **Historical Significance**: Originally developed by DEC as part of the DEC Office and Information Systems family (often paired with ADE - Application Development Environment and DATATRIEVE-11), DECgraph enabled business analysts, researchers, and engineers to transform tabular data into clear visual presentations on VT-series terminals and hardcopy plotters.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine runtime.

---

## 2. Supported Chart Presentations

DECgraph supports multiple distinct chart presentation formats suited for business, financial, and scientific applications:

1. **Horizontal Bar Chart (`BAR` / `HBAR`)**:
   - Produces clear, scaled horizontal bars using ASCII glyphs (`*`).
   - Automatically computes scale bounds and attaches exact value annotations `(val)`.
   - Displays category labels aligned on the left axis with axis scale annotations below.

2. **Vertical Column Chart (`VBAR` / `COLUMN`)**:
   - Multi-tier vertical bar presentation using block characters (`###`).
   - Vertical y-axis numerical intervals scaled across 8 visual tiers.
   - Horizontal category tick marks and centered column labels (`+-------+-------+`).

3. **Line Trend Chart (`LINE` / `TREND`)**:
   - High-contrast point tracking plots using `(*)` markers with background grid references (`.`).
   - Visualizes trends and variations across sequential time or observation points.

4. **Pie / Share Analysis Report (`PIE` / `SHARE`)**:
   - Proportional distribution report displaying category labels, absolute values, computed percentage shares (to 0.1% precision), and proportional visual share bars.
   - Includes summary totals and 100% balance validation.

5. **Scatter Plot (`SCATTER` / `XY`)**:
   - Coordinate tracking graph for experimental and statistical point distributions.

---

## 3. Directory Layout

```
apps/decgraph/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── decgraph        # Compiled native ELF binary
│   ├── graph           # Symlink alias -> decgraph
│   └── decg            # Symlink alias -> decgraph
├── build/
│   └── decgraph.bobj   # Intermediate BASIC-PLUS-2 object
├── src/
│   └── decgraph.bas    # Native DEC BASIC-PLUS-2 source code (< 470 lines)
└── tests/
    ├── __init__.py     # Test package marker
    └── test_decgraph.py # Automated pytest test suite (14 test cases)
```

---

## 4. Command Reference & Syntax

### Interactive Mode (REPL)
Launch `decgraph` (or aliases `graph` / `decg`) without arguments to enter interactive mode:

```
$ ./bin/decgraph
================================================================================
    DECgraph V3.0 - Business & Scientific Graphics Presentation System
    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11
================================================================================
Type HELP for commands, or EXIT to quit.

DECGRAPH> SAMPLE
[Sample dataset loaded - 4 quarterly points]

DECGRAPH> TYPE VBAR
[Chart type set to VBAR]

DECGRAPH> PLOT
================================================================================
  Quarterly Revenue
  Digital Equipment Corporation
================================================================================
   112 |                  ###           
    98 |                  ###           
    84 |                  ###     ###   
    70 |          ###     ###     ###   
    56 |          ###     ###     ###   
    42 |  ###     ###     ###     ###   
    28 |  ###     ###     ###     ###   
    14 |  ###     ###     ###     ###   
       +-------+-------+-------+-------+
          Q1      Q2      Q3      Q4    
        [Quarter]
================================================================================
DECGRAPH> EXIT
```

### Batch Mode & Command Chaining
Pass commands on the command line or chain commands with semicolons (`;`):

```bash
# Render DEC quarterly revenue sample as horizontal bar chart:
./bin/decgraph 'SAMPLE; TYPE BAR; PLOT; EXIT'

# Export vertical column chart to a text file:
./bin/decgraph 'SAMPLE; TYPE VBAR; PRINT ON revenue_chart.txt; EXIT'

# Custom dataset definition:
./bin/decgraph 'TITLE "Q1 Regional Sales"; DATA North, 150; DATA South, 210; DATA West, 185; TYPE PIE; PLOT; EXIT'
```

### Complete Command Summary

| Command | Aliases | Description |
|---|---|---|
| `TYPE <fmt>` | `CHART` | Sets chart format: `BAR`, `VBAR` (`COLUMN`), `LINE` (`TREND`), `PIE` (`SHARE`), `SCATTER` (`XY`). |
| `DATA <lbl>, <val>` | `ADD`, `POINT` | Adds a labeled numeric data point. Supports quoted strings (`DATA "Project A", 45`). |
| `SAMPLE` | `DEMO` | Loads DEC quarterly revenue demonstration dataset (Q1: 45, Q2: 78, Q3: 112, Q4: 95). |
| `TITLE <text>` | - | Sets chart primary header title. Quotes are automatically stripped. |
| `SUBTITLE <text>` | `SUB` | Sets chart secondary heading. Quotes are automatically stripped. |
| `XLABEL <text>` | - | Sets horizontal axis / scale annotation. |
| `YLABEL <text>` | - | Sets vertical axis annotation. |
| `SHOW [DATA\|STATUS]` | `STATUS` | Displays current chart settings, headings, and loaded point count. |
| `LIST` | - | Displays tabular list of all loaded data points with index, label, and value. |
| `PLOT` | `DRAW`, `GRAPH` | Renders the active chart presentation to the terminal. |
| `PRINT ON <file>` | `EXPORT <file>` | Renders the active chart presentation directly into an output file. |
| `SAVE <file>` | - | Saves the current dataset to disk in standard interchange format (`label\|value`). |
| `LOAD <file>` | `IMPORT <file>` | Loads data points from a file (`label\|value` or CSV format). |
| `CLEAR` | `RESET`, `NEW` | Resets all data points, titles, and settings back to defaults. |
| `HELP` | - | Displays summary of all available DECgraph commands. |
| `EXIT` | `QUIT`, `BYE` | Terminates the DECgraph session. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/decgraph clean build
```

Run test suite:
```bash
make -C apps/decgraph test
# or directly:
pytest apps/decgraph/tests/
```

Run interactive session:
```bash
make -C apps/decgraph run
```
