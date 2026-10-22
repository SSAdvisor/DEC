# DEC VAX/VMS V5.5-2 System Management & DCL Reference Manual

## 1. System Architecture Overview

**VAX/VMS** (*Virtual Address Extension / Virtual Memory System*) is Digital Equipment Corporation's 32-bit virtual memory operating system for VAX minicomputers and VAXstation workstations. This emulation models **VAX/VMS V5.5-2** running on a **VAXstation 4000 Model 90** (`KA49-A`, NVAX processor, `128 MB` RAM, Node `VAX01`).

Core architectural layers include:
1. **Executive & Bootstrap (`VMB.EXE` / `SYSBOOT.EXE`)**: Manages virtual memory paging (`PAGEFILE.SYS`, `SWAPFILE.SYS`), process scheduling (`SWAPPER`, `JOB_CONTROL`, `SYMBIONT_0001`, `DECW$SERVER_0`), and ODS-2 disk volumes (`VAX01$DKA0:`).
2. **DIGITAL Command Language (`DCL`)**: Case-insensitive command interpreter with lexical functions (`F$TIME()`, `F$GETSYI()`, `F$USER()`, `F$ENVIRONMENT()`, `F$TRNLNM()`), symbol substitution (`'SYM'`), and `.COM` command procedures.
3. **DECwindows XUI / OSF/Motif 1.1 Workstation Subsystem (`WSA0:`)**: Provides native C/Xlib 3D Motif graphical desktop applications (`SYS$LIBRARY:LIBDECW_X11.SO` and `SYS$SYSTEM:DECW$*.EXE`) alongside terminal/CLI operation.

---

## 2. Logical Name Tables (`LNM$SYSTEM_TABLE` & `LNM$PROCESS_TABLE`)

| Logical Name | Equivalence Specification | Purpose |
| :--- | :--- | :--- |
| `SYS$SYSDEVICE:` | `DKA0:` | Primary ODS-2 system disk volume (`VMS55_SYS`) |
| `SYS$SYSROOT:` | `DKA0:[SYS0.]` | System root directory hierarchy |
| `SYS$COMMON:` | `DKA0:[SYS0.SYSCOMMON.]` | Cluster-common system root |
| `SYS$SYSTEM:` | `DKA0:[SYS0.SYSCOMMON.SYSEXE]` | System executable images (`DECW$*.EXE`, `AUTHORIZE.EXE`) |
| `SYS$LIBRARY:` | `DKA0:[SYS0.SYSCOMMON.SYSLIB]` | Shared libraries (`libdecw_x11.so`, `DCLTABLES.EXE`) |
| `SYS$MANAGER:` | `DKA0:[SYS0.SYSMGR]` | System manager directory (`SYSTARTUP_V5.COM`, `LOGIN.COM`) |
| `SYS$LOGIN:` | `DKA0:[SYSMGR]` (for `SYSTEM`) | Logged-in user's home directory |
| `DECW$DISPLAY:` | `LOCAL:0.0` (or `$DISPLAY`) | Active X11 display routed via `SET DISPLAY` |

---

## 3. SYSUAF User Accounts & UICs

| Username | UIC | Default Directory | Default Privileges |
| :--- | :--- | :--- | :--- |
| `SYSTEM` | `[1,4]` | `DKA0:[SYSMGR]` | `CMKRNL, DETACH, OPER, SYSNAM, SYSPRV, BYPASS, SETPRV, WORLD` |
| `DECW` | `[100,1]` | `DKA0:[DECW]` | `TMPMBX, NETMBX, GRPNAM` |
| `GUEST` | `[200,200]` | `DKA0:[GUEST]` | `TMPMBX, NETMBX` |

Manage accounts via DCL (`CREATE/ACCOUNT`, `MODIFY/ACCOUNT`, `SET ACCOUNT`, `DELETE/ACCOUNT`, `SHOW ACCOUNT [/FULL]`, `SET PASSWORD`) or the interactive **Authorize Utility** (`RUN SYS$SYSTEM:AUTHORIZE` / `MCR AUTHORIZE` / `AUTHORIZE`) with its `UAF>` prompt (`ADD`, `MODIFY`, `REMOVE`, `SHOW [/FULL]`, `LIST`, `COPY`, `RENAME`, `GRANT/IDENTIFIER`, `REVOKE/IDENTIFIER`). Switch sessions with `LOGIN <username>`.

---

## 4. VAX/VMS DCL Command Reference

### System Monitoring & Administration
- `SHOW SYSTEM` — Display active VMS processes, PIDs, priority, I/O, CPU time, and page faults.
- `SHOW DEVICES` — Display `VAX01$DKA0:`, `VAX01$MKA500:`, `VAX01$OPA0:`, `VAX01$WSA0:` status.
- `SHOW MEMORY` — Display physical memory pages (`128 MB`) and `PAGEFILE.SYS` / `SWAPFILE.SYS` blocks.
- `SHOW CPU` / `SHOW PROCESS` / `SHOW USERS` / `SHOW QUOTA` / `SHOW NETWORK`.
- `SHOW LOGICAL` / `SHOW SYMBOL` / `SHOW DEFAULT` / `SHOW TIME`.
- `SHOW DECWINDOWS` / `SHOW APPS` — Display DECwindows X11 workstation suite and layered products.
- `SHOW ACCOUNT [user] [/FULL]` — Display SYSUAF user account records.
- `CREATE/ACCOUNT <user> [/UIC=[g,m]] [/PASSWORD=p] [/QUOTA=n] [/PRIVILEGES=(...)]` — Create a persistent SYSUAF user account and home directory.
- `MODIFY/ACCOUNT <user> [...]` (or `SET ACCOUNT`) — Modify SYSUAF user account attributes, quotas, or flags (`/FLAGS=DISUSER`).
- `DELETE/ACCOUNT <user>` — Remove a non-system user account from `SYSUAF.DAT`.
- `SET PASSWORD [user] [/PASSWORD=new | /GENERATE]` — Change user password in `SYSUAF.DAT`.
- `AUTHORIZE` / `RUN SYS$SYSTEM:AUTHORIZE` / `MCR AUTHORIZE` — VAX/VMS Authorize Utility (`UAF>` interactive and command-line modes).
- `MONITOR`, `SYSMAN`, `ANALYZE/RMS_FILE`, `CONVERT`.

### ODS-2 File & Version Management
- `DIRECTORY [spec]` — List files with VMS `;version` numbers, block sizes, and timestamps.
- `COPY <src> <dst>` — Copy files (automatically preserves previous version as `;1` when overwriting).
- `PURGE [spec]` — Delete older file versions (`;1`), retaining the current version.
- `TYPE`, `RENAME`, `DELETE`, `CREATE`, `CREATE/DIRECTORY`, `SEARCH`, `DIFFERENCES`.

### DECwindows Workstation Applications
Invoke directly by verb or via `RUN SYS$SYSTEM:<IMAGE>`:
- `DXSESSION` / `RUN SYS$SYSTEM:DECW$SESSION`
- `DECTERM` / `RUN SYS$SYSTEM:DECW$DECTERM`
- `BOOKREADER` / `RUN SYS$SYSTEM:DECW$BOOKREADER`
- `CALENDAR` / `RUN SYS$SYSTEM:DECW$CALENDAR`
- `CARDFILER` / `RUN SYS$SYSTEM:DECW$CARDFILER`
- `CDAVIEWER` / `RUN SYS$SYSTEM:DECW$CDAVIEWER`
- `CALCULATOR` / `RUN SYS$SYSTEM:DECW$CALC`
- `CLOCK` / `RUN SYS$SYSTEM:DECW$CLOCK`
- `DECSOUND` / `RUN SYS$SYSTEM:DECW$SOUND`
- `DXMAIL` / `RUN SYS$SYSTEM:DECW$MAIL`
- `FILEVIEW` / `RUN SYS$SYSTEM:VUE$MASTER`
- `NOTEPAD` / `RUN SYS$SYSTEM:DECW$NOTEPAD`

### Browser-Based DECwindows X11 Emulation (HTTPS / WSS `/ws-x11`)
When connected via the HTTPS Web Terminal (`https://localhost:8455/` or Tailscale Funnel `:8443`):
- An internal X11 framebuffer (`Xvfb :99` at `1024x720x24`) and `libX11`/`libXtst` WebSocket bridge (`/ws-x11`) stream live PNG frames of the `:99` display to an interactive HTML5 `<canvas>`.
- Running any DECwindows application at the `$` prompt (e.g., `$ DECWINDOWS`, `$ CLOCK`, `$ CALCULATOR`) automatically opens the **SPLIT (VT220 + X11)** workstation view.
- You can also switch between **VT220**, **SPLIT (VT220 + X11)**, and **DECWINDOWS X11 (WSA0:)** modes or launch applications directly from the X11 toolbar.
