# DEC RSTS/E V10.1-L Operating System Emulation

An authentic operating system emulation of **Digital Equipment Corporation's RSTS/E V10.1-L** (*Resource-Sharing Timesharing System/Extended*) for the PDP-11 family, integrating the native **DEC BASIC-PLUS-2** compiler/linker/VM toolchain and the 12 RSTS/E-supported applications from **DEC-APPS**, executable both directly on the Linux host and inside a self-contained **Docker** container (`dec-rsts-e:latest`).

---

## Key Features

- **PDP-11/70 Hardware & `INIT.SYS` Bootstrap Emulation**: Simulates the 22-bit PDP-11/70 CPU (`KB11-C`), `RA81` system disk (`DK0:`), `DHV11` terminal multiplexers (`KB0:`–`KB31:`), `LP11` line printer (`LP0:`), and `TU16` magnetic tape (`MT0:`).
- **Project-Programmer Number (`[proj,prog]`) Account Architecture**:
  - `[1,1]` (`LIBRARY`) — System Library (`LB:`)
  - `[1,2]` (`SYSTEM`) — System Manager (`SY:`, privileged)
  - `[1,3]` (`PBS`) — Print/Batch Services Spooler (`PRIV`)
  - `[100,100]` (`DIBS`) — Commercial CTS-500 / DIBS-11 Accounting User
  - `[200,200]` (`GUEST`) — General Timesharing User (`NOPRIV`)
- **Multiple Keyboard Monitors**:
  - **DCL (`$`)**: Default RSTS/E V9/V10 DIGITAL Command Language interface.
  - **BASIC-PLUS (`Ready`)**: Classic interactive line-numbered BASIC Keyboard Monitor (`SWITCH BASIC`).
  - **RSX (`>`)**: RSX-11M Monitor emulation (`SWITCH RSX`, `MCR`, `PIP`, `TKB`).
- **Concise Command Language (CCL) & Native Language Compilers**:
  - Direct execution of **7 PDP-11 / RSTS/E Language Compilers** emitting native `.OBJ` object modules that link via `LINK` (`TKB`) into standalone `.TSK` executables on `rsts_vm`:
    - `BASIC` (`BP2`, `COMPILE`) — DEC BASIC-PLUS-2 V2.7 (`SY:HELLO.BAS`)
    - `MACRO` (`MACRO11`, `MAC`) — DEC PDP-11 MACRO-11 V05.05 Relocatable Macro Assembler (`SY:HELLO.MAC`)
    - `COBOL` (`COBOL81`, `COB`) — DEC PDP-11 COBOL-81 V2.4 (ANSI-74) Compiler (`SY:PAYROL.CBL`)
    - `FORTRAN` (`FORTRAN77`, `F77`, `FOR`) — DEC PDP-11 FORTRAN-77 V5.0 Compiler (`SY:STATS.FOR`)
    - `DIBOL` (`DIBOL83`, `DBL`) — DEC CTS-500 / RSTS/E DIBOL-83 V5.3 Compiler (`SY:INVOIC.DBL`)
    - `RPG` (`RPGII`) — DEC PDP-11 RPG II V2.1 Report Program Generator (`SY:SLSRPT.RPG`)
    - `APL` (`APL11`, `APLC`) — DEC PDP-11 APL-11 V2.1 Compiler & Interactive Workspace (`SY:VECTOR.APL` or interactive `APL`)
  - Direct execution of `LINK`, `RUN`, `EDT`, `SUBMIT`, `PRINT`, `SYSTAT`, `PIP`, `FIT`, `UTILITY`.
  - Pre-configured CCL verbs for all **12 RSTS/E-supported DEC-APPS**: `HAMURABI`, `SORT11` (`SORT`), `RMSUTILS` (`RMSDES`, `RMSDEF`, `RMSIFL`, `RMSCNV`, `RMSBCK`, `RMSRST`, `RMSDSP`), `ADE`, `DATATRIEVE11` (`DTR`), `DECGRAPH` (`GRAPH`), `DECMAIL` (`MAIL`), `DECWORD` (`WPS`), `DIBS` (`CTS500`), `FMS11` (`FMS`), `MENU11` (`MENU`), and `INDENT` (`BP2FMT`).
  - Enforces historical OS boundaries: 32-bit VAX/VMS-only `DECwindows` X11 applications are excluded and rejected with an authentic RSTS/E diagnostic.

---

## Quick Start

### 1. Stage Runtime & Run on Host
```bash
make stage
./bin/rsts-emu
```
Or boot with the full PDP-11/70 `INIT.SYS` bootstrap and interactive `User: 1,2` login prompt:
```bash
make login
```
Execute a one-shot command or `.COM` command procedure:
```bash
./bin/rsts-emu -c "SHOW SYSTEM; SYSTAT"
./bin/rsts-emu @SY:LOGIN.COM
```

### 2. Build & Run with Docker
Build the `dec-rsts-e:latest` Docker image:
```bash
make docker-build
```
Launch an interactive RSTS/E V10.1-L session inside Docker:
```bash
make docker-run
```
Or run one-shot RSTS/E commands inside Docker:
```bash
./scripts/docker_run.sh -c "SHOW SYSTEM; SYSTAT; DIR SY:"
```

### 3. Run the Test Suite (Host + Docker)
```bash
make test
```

---

## Documentation

- [RSTS/E System Manager's & User's Manual](docs/RSTS_E_MANUAL.md)
- [Historical OS Application Compatibility Matrix](docs/COMPATIBILITY.md)
