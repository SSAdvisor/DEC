# DEC RSTS/E V10.1-L System Manager's & User's Reference Manual

## 1. System Architecture Overview

**RSTS/E** (*Resource-Sharing Timesharing System/Extended*) is Digital Equipment Corporation's multi-user timesharing operating system for the 16-bit PDP-11 family (PDP-11/70, PDP-11/44, PDP-11/84, PDP-11/93). RSTS/E V10.1-L represents the final major architectural evolution of the system, combining:
1. **Monitor & Executive (`INIT.SYS`)**: Manages PDP-11 22-bit physical memory (`2048 KW` / `4 MB`), job scheduling (`MAXJOB = 63`), terminal multiplexers (`KB0:`–`KB31:`), and RDS1.2 disk structures (`DK0:`).
2. **Keyboard Monitors (Run-Time Systems)**:
   - **DCL (`$`)**: Default DIGITAL Command Language environment introduced in RSTS/E V8/V9.
   - **BASIC-PLUS (`Ready`)**: Classic line-numbered interactive BASIC monitor (`SWITCH BASIC`).
   - **RSX (`>`)**: RSX-11M MCR/PIP/TKB emulation monitor (`SWITCH RSX`).
3. **Shared Run-Time Systems & Subsystems**:
   - **BASIC-PLUS-2 (`basicc` / `basiclink` / `rsts_vm`)**: Structured compiled BASIC-PLUS-2 with overlay support.
   - **RMS-11 (`RMSUTILS`, `SORT-11`)**: Record Management Services supporting sequential and SQLite-backed indexed `.IDX` files.
   - **Print/Batch Services (`PBS`)**: Background batch job processor and print spooler (`SYS$BATCH`, `SYS$PRINT`, `LP0:`).

---

## 2. Project-Programmer Numbers (PPNs) & Accounts

RSTS/E identifies user accounts and disk directories via a **PPN** (`[proj,prog]`), stored in `$ACCT.SYS`:

| PPN | Account Name | Privilege | Logical Device | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `[1,1]` | `LIBRARY` | `PRIV` | `LB:` | System Library executables, CCL tasks, and shared RTS |
| `[1,2]` | `SYSTEM` | `PRIV` | `SY:` (default) | System Manager / Operator account |
| `[1,3]` | `PBS` | `PRIV` | — | Print/Batch Services spooler account |
| `[100,100]` | `DIBS` | `NOPRIV` | — | Commercial CTS-500 / DIBS-11 Accounting account |
| `[200,200]` | `GUEST` | `NOPRIV` | — | General timesharing user account |

Use `HELLO <ppn>` (e.g., `HELLO 200,200` or `HELLO 1,2`) or `SET DEFAULT [proj,prog]` to switch accounts.

---

## 3. Logical Device Names

| Logical Device | Target | Description |
| :--- | :--- | :--- |
| `SY:` | `DK0:[curr_proj,curr_prog]` | Current user's logged-in PPN directory |
| `LB:` | `DK0:[1,1]` | System Library directory (`[1,1]`) and CCL task binaries |
| `DK0:` | `RA81 Disk Unit 0` | Primary RSTS/E structured system disk |
| `KB0:` / `KB:` / `TT:` | `/dev/tty` | Interactive controlling terminal |
| `LP0:` | `SYS$PRINT` | System line printer spooler |

---

## 4. Command Reference

### System Monitoring & Session Control
- `SHOW SYSTEM` — Display RSTS/E version, CPU model, current PPN, active monitor, and default directory.
- `SHOW DEVICES` — List Unibus/Q-bus peripheral devices (`DK0:`, `KB0:`, `LP0:`, `MT0:`, `XH0:`).
- `SHOW USERS` — List active interactive and detached jobs.
- `SHOW MEMORY` — Display PDP-11 physical memory map in Kilowords (`KW`).
- `SHOW LOGICALS` / `SHOW SYMBOLS` — Display logical device table or DCL symbols.
- `SHOW ACCOUNT [ppn] [/FULL]` (`SHOW ACCOUNTS`) — Display `$ACCT.SYS` PPN accounts, quotas, privileges, and login flags.
- `CREATE/ACCOUNT <ppn> [/NAME=user] [/PASSWORD=pw] [/QUOTA=n] [/PRIVILEGES]` — Create a persistent PPN account and directory on `DK0:`.
- `MODIFY/ACCOUNT <ppn> [/NAME=...] [/PASSWORD=...] [/QUOTA=...] [/PRIV | /NOPRIV] [/DISUSER]` (or `SET ACCOUNT`) — Update PPN account attributes.
- `DELETE/ACCOUNT <ppn>` — Delete a non-system PPN account from `$ACCT.SYS`.
- `SET PASSWORD [ppn] [/PASSWORD=new | /GENERATE]` — Update an account password.
- `SHOW CCL` / `SHOW APPS` — List all installed RSTS/E CCL applications.
- `SYSTAT` — Display classic RSTS/E full system status (Jobs, RTS, Disk structure, Free blocks).
- `SWITCH DCL` | `SWITCH BASIC` | `SWITCH RSX` — Switch active Keyboard Monitor.
- `HELLO <ppn>` / `BYE` / `LOGOUT` — Log into another PPN or terminate session.

### File Management & Legacy Utilities
- `DIRECTORY [spec]` (`DIR`) — List files in RSTS/E `Name .Typ Size Prot Date` format.
- `TYPE <file>` — Display file contents (`TYPE SY:WELCOME.TXT`).
- `COPY <src> <dst>` / `RENAME <old> <new>` / `DELETE <file>` — Standard file operations.
- `PIP [dst=src | /L]` — Peripheral Interchange Program.
- `FIT [spec]` — File Information Table display utility.
- `UTILITY CREATE <ppn> <name>` — Create a new PPN account on `DK0:`.

### Software Development & Job Control
- `BASIC <file.bas> [/OBJECT=file.obj]` — Compile a DEC BASIC-PLUS-2 program.
- `LINK <file.obj> [/OUTPUT=file]` — Link object module into executable task.
- `RUN <file>` — Execute a compiled binary or compile-and-run a `.BAS` source program.
- `EDT <file>` — Invoke DEC EDT V3.0 Text Editor.
- `SUBMIT <file.com>` / `PRINT <file>` / `SHOW QUEUE` / `SHOW JOBS` — Print/Batch Services (PBS).
