# DEC VAX/VMS V5.5-2 Operating System Emulation

An authentic 32-bit **Digital Equipment Corporation VAX/VMS V5.5-2** (*Virtual Memory System*) emulation on a **VAXstation 4000 Model 90** (`Node VAX01`), integrating the **VAX BASIC / BASIC-PLUS-2** compiler/linker/runtime, the **DECwindows XUI / OSF/Motif 1.1** workstation suite (all 11 X11 GUI applications + Session Manager), and the VAX/VMS-compatible applications from **DEC-APPS**, executable both directly on the Linux host and inside a **Docker** container (`dec-vms:latest`).

---

## Key Features

- **VAXstation 4000 Model 90 Bootstrap (`VMB.EXE` / `SYSBOOT.EXE`) & Login Executive**:
  - Simulates `KA49-A` NVAX processor, `128 MB` physical memory, `PAGEFILE.SYS` / `SWAPFILE.SYS`, `VAX01$DKA0:` system disk, `OPA0:` console, and `WSA0:` DECwindows X11 workstation display.
- **SYSUAF User Identification Code (`[group,member]`) Accounts**:
  - `SYSTEM` (`[1,4]`, `DKA0:[SYSMGR]`, full `SETPRV, OPER, SYSPRV, BYPASS, WORLD`)
  - `DECW` (`[100,1]`, `DKA0:[DECW]`, DECwindows Workstation User)
  - `GUEST` (`[200,200]`, `DKA0:[GUEST]`, unprivileged user)
- **ODS-2 Hierarchical Filesystem, Logical Names & File Versioning**:
  - System logicals: `SYS$SYSTEM:`, `SYS$LIBRARY:`, `SYS$MANAGER:`, `SYS$LOGIN:`, `SYS$SYSROOT:`, `SYS$COMMON:`, `SYS$DISK:`, `DECW$DISPLAY:`.
  - Tracks file versions (`;1`, `;2`) on `COPY` and cleans up older versions via `PURGE`.
- **Full VAX/VMS DCL & Lexical Functions**:
  - Built-in lexical functions: `F$TIME()`, `F$USER()`, `F$PROCESS()`, `F$GETSYI()`, `F$ENVIRONMENT()`, `F$TRNLNM()`.
  - System utilities: `SHOW SYSTEM`, `SHOW DEVICES`, `SHOW MEMORY`, `SHOW CPU`, `SHOW PROCESS`, `SHOW QUOTA`, `SHOW DECWINDOWS`, `AUTHORIZE`, `MONITOR`, `SYSMAN`, `ANALYZE/RMS_FILE`, `CONVERT`, `SEARCH`, `DIFFERENCES`, `CREATE`, `PURGE`.
- **Complete DECwindows Motif Workstation & Layered Products**:
  - Supports all **12 VAX/VMS-compatible DEC-APPS**: `DECWINDOWS` (`dxsession`, `decterm`, `bookreader`, `calendar`, `cardfiler`, `cdaviewer`, `calculator`, `clock`, `decsound`, `dxmail`, `fileview`, `notepad` — plus `RUN SYS$SYSTEM:DECW$*` system images), `DATATRIEVE` (`DTR`), `ADE`, `DECGRAPH`, `MAIL` (`DECMAIL`), `DECWORD` (`WPS`), `FMS` (`FMS11`), `MENU` (`MENU11`), `SORT` (`SORT11`), `RMSUTILS`, `INDENT`, and `HAMURABI`.
  - Enforces historical OS boundaries: 16-bit PDP-11 RSTS/E-only `DIBS-11` (`CTS-500`) is excluded and rejected with an authentic VMS `%DCL-W-UNSUPOS` diagnostic.

---

## Quick Start

### 1. Stage Runtime & Run on Host
```bash
make stage
./bin/vms-emu
```
Or boot with the full VAXstation 4000 `VMB.EXE` bootstrap and interactive `Username: SYSTEM` login prompt:
```bash
make login
```
Execute a one-shot DCL command or `.COM` procedure:
```bash
./bin/vms-emu -c "SHOW SYSTEM; SHOW MEMORY; SHOW DECWINDOWS"
./bin/vms-emu @SYS$LOGIN:LOGIN.COM
```

### 2. Build & Run with Docker (including X11 Forwarding for DECwindows)
Build the `dec-vms:latest` Docker image:
```bash
make docker-build
```
Launch an interactive VAX/VMS V5.5-2 session inside Docker (automatically forwards `DISPLAY` and `/tmp/.X11-unix` when available):
```bash
make docker-run
```
Or run one-shot VMS DCL commands inside Docker:
```bash
./scripts/docker_run.sh -c "SHOW SYSTEM; SHOW DEVICES; DIRECTORY SYS\$LOGIN:"
```

### 3. Run the Test Suite (Host + Docker)
```bash
# Run all 15 host + Docker + multi-user + X11 Web Workstation tests
make test
```

### Multi-User SSH, HTTPS VT220 Web Terminal & JavaScript DECwindows X11 Workstation
- **SSH Timesharing (`FTA1:`–`FTA64:`)**: `ssh -p 2255 dec@localhost` (configurable via `VMS_SSH_PORT` in `docker-compose.yml`).
- **HTTPS VT220 + DECwindows X11 Browser Workstation (`WSA0: :99.0`)**: `https://localhost:8455` (configurable via `VMS_HTTPS_PORT` in `docker-compose.yml`).
  - Supports **VT220**, **SPLIT (VT220 + X11)**, and **DECWINDOWS X11 (`WSA0:`)** display modes.
  - Typing any DECwindows command at the DCL `$` prompt (`DECWINDOWS`, `DXSESSION`, `CLOCK`, `CALCULATOR`, `CALENDAR`, `CARDFILER`, `BOOKREADER`, `CDAVIEWER`, `DECSOUND`, `DXMAIL`, `FILEVIEW`, `NOTEPAD`, `DECTERM`) or clicking **LAUNCH DECWINDOWS** / **OPEN APP** renders the live X11 OSF/Motif 1.1 GUI directly onto the HTML5 `<canvas>` over WebSocket (`/ws-x11`) with full mouse (Left/Right click + window title-bar drag) and keyboard interaction.

---

## Documentation

- [VAX/VMS System Management & DCL Reference Manual](docs/VMS_MANUAL.md)
- [Historical OS Application Compatibility Matrix](docs/COMPATIBILITY.md)
