# DEC — Digital Equipment Corporation Operating Systems, Languages & Applications Ecosystem

A unified, authentic preservation and modernization ecosystem for classic **Digital Equipment Corporation (DEC)** operating systems (**RSTS/E** and **VAX/VMS**), compilers and runtime systems (**DEC BASIC-PLUS-2**, **RMS-11**, **DCL**, **EDT**), and layered enterprise/workstation applications (**DEC-APPS** and **DECwindows X11/Motif**).

---

## Repository Structure

```text
DEC/
├── Makefile                    # Unified build, Docker staging, and test runner
├── LICENSE                     # MIT License
├── OS/                         # DEC Operating System Emulations (Host + Docker)
│   ├── RSTS-E/                 # PDP-11/70 RSTS/E V10.1-L Monitor & CCL Environment
│   └── VMS/                    # VAXstation 4000-90 VAX/VMS V5.5-2 Executive & DCL
├── LANG/                       # DEC Languages, Compilers, Linkers & Run-Time Systems
│   └── BASIC-PLUS-2/           # Self-hosted BASIC-PLUS-2 Compiler, Linker, C VM, RMS, DCL & EDT
└── APPS/                       # DEC Layered Applications & Workstation Suites
    └── apps/                   # 13 Application Suites (HAMURABI, SORT-11, RMSUTILS, ADE,
                                # DATATRIEVE-11, DECgraph, DECmail, DECword/DP, DIBS-11,
                                # FMS-11, MENU-11, INDENT, and DECwindows X11/Motif)
```

---

## Project Divisions

### 1. Operating Systems (`OS/`)

| Emulation | Hardware / Architecture | Highlights | Docker Image |
| :--- | :--- | :--- | :--- |
| **[`OS/RSTS-E`](OS/RSTS-E)** | PDP-11/70 (`KB11-C`, 4096 KW, `DK0:` RA81) | `INIT.SYS` hardware bootstrap, PPN `[proj,prog]` accounts (`$ACCT.SYS`), 6.3 RAD-50 filesystem (`FILNAM.EXT`), switchable Keyboard Monitors (`DCL $`, `BASIC Ready`, `RSX >`), persistent DCL Account Management, and CCL dispatch for 12 PDP-11 applications (blocks 32-bit VAX-only `DECwindows`). | `dec-rsts-e:latest` |
| **[`OS/VMS`](OS/VMS)** | VAXstation 4000 Model 90 (Node `VAX01`, 128 MB, `VAX01$DKA0:`) | `VMB.EXE`/`SYSBOOT.EXE` bootstrap, `SYSUAF.DAT` UIC accounts & `UAF>` `AUTHORIZE` utility, ODS-2 filesystem with `;version` numbers and `PURGE`, DCL lexical functions (`F$TIME`, `F$GETSYI`, `F$USER`), and 12 VAX/VMS layered products including the full `DECwindows` X11/Motif workstation suite (blocks 16-bit PDP-11-only `DIBS-11`). | `dec-vms:latest` |

### 2. Languages & Run-Time Systems (`LANG/`)

* **[`LANG/BASIC-PLUS-2`](LANG/BASIC-PLUS-2)**:
  - **Native Compiler (`compiler/basicc.bas` $\rightarrow$ `basicc`)**: Written in pure DEC BASIC-PLUS-2; compiles `.BAS` sources to `.OBJ` / `.BIN` modules.
  - **Native Linker (`linker/basiclink.bas` $\rightarrow$ `basiclink`)**: Written in pure DEC BASIC-PLUS-2; resolves multi-module overlays (`.ODL`) and packages standalone executables.
  - **C Virtual Machine & RMS-11 Engine (`vm/build/rsts_vm`)**: Stack-based bytecode VM with SQLite-backed RMS sequential and indexed (`PRIMARY KEY` / `ALTERNATE KEY`) file I/O.
  - **DCL & Print/Batch Services (`dcl/dcl.bas` $\rightarrow$ `dcl`, `dec-printq`)**: Interactive DCL shell, `.COM` batch processor, `$ACCT.SYS` account management, and network print symbiont.
  - **DEC EDT Editor V3.0 (`edt/edt.bas` $\rightarrow$ `edt`)**: Line-mode (`*`) and VT100 full-screen keypad editor.

### 3. Layered Applications (`APPS/`)

* **[`APPS`](APPS)**:
  - **12 Terminal / RMS Applications**: `HAMURABI`, `SORT-11`, `RMSUTILS` (`RMSDES`, `RMSDEF`, `RMSIFL`, `RMSCNV`, `RMSBCK`, `RMSRST`, `RMSDSP`), `ADE`, `DATATRIEVE-11` (`DTR`), `DECgraph`, `DECmail`, `DECword/DP` (`WPS`), `DIBS-11` (`CTS-500`), `FMS-11`, `MENU-11`, and `INDENT`.
  - **DECwindows Workstation Suite (`APPS/apps/decwindows/`)**: Native C/Xlib OSF/Motif 1.1 interfacing library (`libdecw_x11.so`), Session Manager (`dxsession`), and 11 double-buffered X11 GUI applications (`DECterm`, `Bookreader`, `Calendar`, `Cardfiler`, `CDA Viewer`, `Calculator`, `Clock`, `DECsound`, `DECwindows Mail`, `FileView`, `Notepad`).

---

## Quick Start

### Build & Stage Everything
```bash
make all
```

### Build Docker Images for RSTS/E & VAX/VMS
```bash
make docker-build
```

### Launch Emulated Operating Systems
```bash
# Launch RSTS/E V10.1-L (Host or Docker)
make -C OS/RSTS-E run
make -C OS/RSTS-E docker-run

# Launch VAX/VMS V5.5-2 (Host or Docker with X11 forwarding)
make -C OS/VMS run
make -C OS/VMS docker-run
```

### Run Complete Verification Suite (433 Tests)
```bash
make test
```

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
