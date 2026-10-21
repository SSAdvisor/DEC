# DEC RSTS/E DIGITAL Command Language (DCL) & Job Control (PBS) V10.1

An authentic, complete implementation of the classic Digital Equipment Corporation **DIGITAL Command Language (DCL)** and **Print/Batch Services (PBS)** subsystem, written entirely in **DEC BASIC-PLUS-2** (`dcl/dcl.bas`) and compiled directly to a native standalone executable (`dcl/dcl`) using `basicc.py` and `basiclink.py`.

---

## 1. Overview & Architecture

DCL was the standard command language across DEC operating systems (RSTS/E, RSX-11M/11M-PLUS, VAX/VMS). This subsystem provides a faithful recreation of the RSTS/E DCL user interface, interactive shell, command procedure interpreter, and job controller integration.

### Key Capabilities
- **Pure DEC BASIC-PLUS-2 Implementation**: The entire DCL interpreter, parser, symbol engine, and command dispatcher are implemented in `dcl/dcl.bas`.
- **Dual Execution Modes**:
  - **Interactive Shell**: Full-featured interactive terminal with prompt (`$ `), command history, variable assignments, and clean exit semantics.
  - **One-Shot Execution**: Direct execution of single commands passed on the command line (e.g. `./dcl/dcl SHOW SYSTEM`, `./dcl/dcl 'SHOW QUEUE LP0:'`).
  - **Command Procedures**: Interprets `.COM` and `.DCL` scripts (e.g. `./dcl/dcl @tests/office/salesrpt.dcl`), supporting labels (`LABEL:`), branching (`IF ... THEN GOTO`), comments (`!`), and symbol substitutions (`'NAME'`).
  - **Pipeline Support**: Supports standard I/O redirection and piping (e.g. `printf "SHOW TIME\nEXIT\n" | ./dcl/dcl`).
- **Print/Batch Services (PBS) Integration**:
  - Integrates with SQLite-backed queues for print and batch processing.
  - Transparent queue submission (`PRINT`, `SUBMIT`), status inspection (`SHOW QUEUE`, `SHOW JOBS`, `SHOW ENTRY`), and queue administration (`START/QUEUE`, `STOP/QUEUE`, `DELETE/ENTRY`).
  - Automatic spooling into `spool/<queue>/` with print banners and job log capture.
- **RSTS Virtual Machine Enhancements**:
  - `COMMAND$` (`OP_COMMAND_STR` 0x85): Inspects process command line arguments.
  - `TIME$` (`OP_TIME_STR` 0x86): Fetches system date/time in DEC format (`DD-Mon-YY HH:MM:SS`).
  - `SYS(cmd$)` (`OP_SYS` 0x84): Executes host-level operations with exit status return.
  - RMS sequential file I/O error trapping (`ON ERROR GOTO`) for script execution.

---

## 2. Directory Structure

```
dcl/
├── dcl.bas               # Pure DEC BASIC-PLUS-2 DCL interpreter source
├── dcl.obj               # Compiled BASIC object file (bytecode JSON)
├── dcl.bin               # Raw VM bytecode payload
├── dcl                   # Standalone native executable binary (VM + bytecode)
├── build.sh              # Automated build script
├── job_controller.py     # PBS queue manager and SQLite database interface
├── print_service.py      # Background queue spooling service
├── dcl_interpreter.py    # Python reference interpreter
├── dcl_parser.py         # Python reference command parser
├── dcl_shell.py          # Python reference CLI shell
└── README.md             # Subsystem documentation
```

Top-level wrapper:
- `dcl.py`: Top-level CLI launcher that invokes the native compiled binary `dcl/dcl` (with fallback to Python reference implementation).

---

## 3. Building and Running

### Build from Source
To compile `dcl.bas` and link the native executable:
```bash
./dcl/build.sh
```

Or manually using the compiler tools:
```bash
python3 compiler/basicc.py dcl/dcl.bas -o dcl/dcl.obj
python3 compiler/basiclink.py dcl/dcl.obj -o dcl/dcl
```

### Running DCL

#### 1. Interactive Shell
```bash
./dcl/dcl
# Or via the Python wrapper:
./dcl.py
```
Output:
```
DEC RSTS/E V10.1-L DCL (DIGITAL Command Language)
Print/Batch Services (PBS) Active. Type HELP for commands.

$ SHOW SYSTEM
DEC RSTS/E V10.1-L Environment
Host Platform: Linux Bytecode VM
System Time:   13-Oct-26 20:35:15
Compiler:      BASIC-PLUS-2 Python Frontend / C Runtime VM
Job Subsystem: Print/Batch Services (PBS) Active
Default Dir:   .
$ EXIT
%DCL-I-LOGOUT, session terminated
```

#### 2. One-Shot Command Execution
```bash
./dcl/dcl SHOW QUEUE
./dcl/dcl HELP PRINT
./dcl/dcl 'DIRECTORY *.bas'
```

#### 3. Command Procedure Execution
```bash
./dcl/dcl @tests/office/salesrpt.dcl
./dcl/dcl @tests/office/sales_batch.com
```

---

## 4. Supported DCL Commands

| Command | Qualifiers / Options | Description |
|:---|:---|:---|
| `SHOW SYSTEM` | | Displays RSTS/E environment, host OS, time, and PBS status |
| `SHOW QUEUE` | `[queue_name]` | Displays print and batch queue definitions and active counts |
| `SHOW JOBS` | | Displays active and completed jobs in PBS queues |
| `SHOW ENTRY` | `[entry_id]` | Displays detailed metadata for a specific queue entry |
| `SHOW SYMBOLS`| | Lists active symbol table variables (`$STATUS`, `P1`..`P8`, etc.) |
| `SHOW LOGICALS`| | Lists defined logical names (`SYS$OUTPUT`, `SYS$BATCH`, etc.) |
| `SHOW TIME` | | Displays current system date and time |
| `PRINT <file>`| `/QUEUE=q`, `/COPIES=n`, `/NAME=j`, `/DELETE` | Submits file to print queue (e.g. `LP0:`, `NETPRINT`) |
| `SUBMIT <proc>`| `/QUEUE=q`, `/NAME=j`, `/LOG` | Submits `.COM` command procedure to batch queue (`SYS$BATCH`) |
| `DELETE/ENTRY` | `=<entry_id>` | Cancels and removes an entry from the queue |
| `START/QUEUE` | `<queue_name>` | Resumes/opens a paused queue |
| `STOP/QUEUE` | `<queue_name>` | Pauses a queue to hold job processing |
| `BASIC <file>`| | Invokes `compiler/basicc.py` to compile BASIC-PLUS-2 source |
| `LINK <file>` | | Invokes `compiler/basiclink.py` to link compiled object files |
| `RUN <prog>` | | Executes a compiled program binary |
| `DIRECTORY` | `[file_spec]` | Lists directory contents with DEC block sizing |
| `TYPE <file>` | | Outputs text file contents to `SYS$OUTPUT` |
| `COPY <src> <dst>` | | Copies file to destination |
| `RENAME <src> <dst>` | | Renames/moves file |
| `SET DEFAULT` | `<directory>` | Changes current working directory |
| `WRITE` | `SYS$OUTPUT <text>` | Prints string with symbol interpolation (`'VAR'`) |
| `IF ... THEN` | `GOTO <label>` | Evaluates integer/string equality and jumps to label |
| `@<file>` | | Executes DCL command procedure file (`.COM` / `.DCL`) |
| `HELP` | `[command]` | Displays built-in help and topic documentation |
| `EXIT` / `LOGOUT` | | Terminates interactive session or script |

---

## 5. Command Procedure (.COM / .DCL) Syntax

Command procedures support authentic DEC command procedure conventions:
1. **Dollar Sign Prefix**: Lines starting with `$` or `$ ` are executed as commands.
2. **Comments**: Lines starting with `!` or `$ !` are ignored.
3. **Labels**: Identifiers followed by a colon (e.g. `START_LOOP:`) define jump targets.
4. **Symbol Substitution**: Single quotes evaluate symbols, e.g. `'COUNT'` or `'NAME'`.
5. **Control Flow**:
   ```dcl
   $ COUNT = 1
   $ LOOP:
   $ WRITE SYS$OUTPUT "Current count is 'COUNT'"
   $ IF COUNT = 5 THEN GOTO DONE
   $ GOTO LOOP
   $ DONE:
   $ EXIT
   ```

### Office Sales Batch Procedure Example (`tests/office/sales_batch.com`):
```dcl
$ ! SALES_BATCH.COM - Automatic batch report procedure
$ WRITE SYS$OUTPUT "Starting Sales Inventory Report Batch Job..."
$ BASIC tests/office/salesrpt.bas
$ LINK tests/office/salesrpt
$ RUN tests/office/salesrpt
$ PRINT tests/office/SALES.RPT /QUEUE=LP0: /NAME=SALES_NIGHTLY
$ SHOW QUEUE LP0:
$ WRITE SYS$OUTPUT "Sales Inventory Report Batch Job Finished Successfully."
$ EXIT
```

---

## 6. Testing & Verification

The subsystem is fully verified via automated Python `unittest` suites:
```bash
python3 -m unittest discover tests
```
Tests covering DCL and Job Controller include:
- `tests/test_dcl.py`: Tests command parsing, symbol evaluation, PBS job submission, batch execution, and subprocess execution of the compiled `dcl/dcl` binary.
- `tests/test_print_service.py`: Tests print daemon spooling, formatting, and banner generation.
