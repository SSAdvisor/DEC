# MENU-11 - DEC Menu Control & Application Dispatch Facility (MCF)

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's **MENU-11** (**Menu Control & Application Dispatch Facility**), an interactive hierarchical menu manager, PPN privilege security controller, and turnkey application dispatcher originally distributed for **DEC PDP-11 (RSTS/E, RSX-11M, CTS-300, CTS-500)** and **VAX/VMS** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: MENU-11 V2.0 / RSTS/E Menu Control Facility (MCF)
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E, RSX-11M, CTS-300, CTS-500), VAX-11 (VAX/VMS)
- **Historical Significance**: On commercial PDP-11 turnkey installations running RSTS/E and CTS-300/500, **MENU-11** served as the top-level captive login shell and application dispatcher. It allowed system managers (`[1,2]`) to organize departmental applications (**DIBS-11**, **FMS-11**, **DECmail**, **DECword/DP**, **DATATRIEVE-11**, **DECgraph**, **SORT-11**, **RMSUTILS**) into hierarchical VT100 menus, enforce RSTS/E Project-Programmer Number (`[proj,prog]`) privilege levels (`10`..`100`), chain to compiled `.TSK` tasks or CCL commands, and record an operator security audit trail.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine runtime.

---

## 2. Architecture & Subsystems

1. **Menu Control Library (`MLB` / `DIR` / `MENUS`)**:
   - Manages named application menus (`MAIN_MENU`, `ACCT_MENU`, `OFFICE_MENU`) stored in `MENU11.MLB`.
   - Tracks menu status (`A` active, `D` deleted), option counts, creation dates, and screen titles.

2. **Menu Definition Editor (`CREATE` / `ADDOPT` / `OPTIONS`)**:
   - Creates menus and defines dispatch options with:
     - **Selection Key** (`1`, `2`, `3`, `9`, `M`)
     - **Option Description** (`Commercial Accounting & ERP`, `FMS-11 Screen Forms Driver`)
     - **Dispatch Action Type** (`SUBMENU`, `CHAIN`, `CCL`)
     - **Target Task or Menu** (`ACCT_MENU`, `SY:DIBS11.TSK`, `RUN $SYSTAT`)
     - **Minimum Privilege Level** (`10` = General User, `20` = Accounting, `50` = Systems, `100` = `[1,2]` Operator)

3. **Security & Application Dispatcher (`USER`, `RUN` / `EXEC` / `PICK`, `BACK`, `LOG`)**:
   - Evaluates the current operator's RSTS/E PPN (`[1,2]`, `[100,10]`) and privilege level before dispatching any menu selection.
   - Navigates hierarchically across submenus (`SUBMENU`) and parent menus (`BACK` / `PARENT`), chains to tasks (`CHAIN` / `CCL`), and logs all dispatches and security violations in the MCF Audit Log (`LOG`).

4. **VT100 Menu Screen Renderer (`DISPLAY` / `RENDER` / `PRINT ON` / `EXPORT`)**:
   - Renders formatted VT100 application menus with centered headers, RSTS/E PPN & privilege status bar, selection keys, and dispatch targets to the terminal or an output file.

---

## 3. Directory Layout

```
apps/menu11/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── menu11          # Compiled native ELF binary
│   ├── menu            # Symlink alias -> menu11
│   └── mcf             # Symlink alias -> menu11
├── build/
│   └── menu11.obj     # Intermediate BASIC-PLUS-2 object
├── src/
│   └── menu11.bas      # Native DEC BASIC-PLUS-2 source code (< 470 lines)
└── tests/
    ├── __init__.py     # Test package marker
    └── test_menu11.py  # Automated pytest test suite (14 test cases)
```

---

## 4. Command Reference & Syntax

| Command | Aliases | Description |
|---|---|---|
| `DIR` | `MENUS`, `MLB` | Lists all menus in the active Menu Control Library (`MENU11.MLB`). |
| `SELECT <name_or_#>` | `MENU` | Selects the active menu by name or index number. |
| `BACK` | `PARENT`, `UP` | Returns to the previous/parent menu in the navigation hierarchy. |
| `CREATE <name>, <title>` | `NEWMENU` | Creates a new menu definition in the library. |
| `ADDOPT <k>,<desc>,<t>,<trg>[,<p>]` | `OPTION` | Adds a dispatch option to the active menu. |
| `OPTIONS` | `DESCRIBE`, `ITEMS` | Displays the Option Dispatch Table for the active menu. |
| `USER <ppn>, <priv>` | `LOGIN`, `SETPRIV` | Sets the active operator RSTS/E PPN account and privilege level. |
| `RUN <key>` | `EXEC`, `PICK`, `CHOOSE` | Dispatches an option by key (enforces privilege level and navigates submenus). |
| `LOG` | `AUDIT`, `HISTORY` | Displays the MCF Security & Dispatch Audit Log. |
| `DISPLAY [menu#]` | `RENDER`, `PRINT [ON <f>]`, `EXPORT <f>` | Renders the VT100 menu screen to terminal or disk file. |
| `DELETE [menu#]` | `DEL` | Marks a menu as deleted in the Menu Control Library. |
| `PURGE` | - | Permanently removes deleted menus from the Menu Control Library. |
| `SAMPLE` | `DEMO` | Loads historical DEC RSTS/E V8.0 turnkey menus (`MAIN_MENU`, `ACCT_MENU`, `OFFICE_MENU`). |
| `SAVE [file]` | - | Saves the Menu Control Library directory to disk (`MENU11.MLB`). |
| `LOAD [file]` | `IMPORT` | Loads Menu Control Library definitions from disk. |
| `SHOW` | `STATUS` | Displays MENU-11 system status, operator PPN/privilege, and menu/option counts. |
| `CLEAR` | `RESET` | Clears all menus, options, and audit logs from memory. |
| `HELP` | `?` | Displays summary of all available MENU-11 commands. |
| `EXIT` | `QUIT`, `BYE` | Exits the MENU-11 session. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/menu11 clean build
```

Run test suite:
```bash
make -C apps/menu11 test
# or directly:
pytest apps/menu11/tests/
```

Run interactive session:
```bash
make -C apps/menu11 run
```
