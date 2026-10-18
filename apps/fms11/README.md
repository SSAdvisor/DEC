# FMS-11 - DEC Forms Management System (FED / FLB / FUT / FDV)

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's **FMS-11** (**Forms Management System**), an interactive video terminal screen forms editor, library manager, and runtime form driver originally distributed for **DEC PDP-11 (RSTS/E, RSX-11M, RT-11)** and **VAX/VMS** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: FMS-11 V2.0 / VAX FMS (Forms Management System)
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E, RSX-11M, RT-11), VAX-11 (VAX/VMS)
- **Historical Significance**: Introduced in 1979 for VT52 and VT100 video terminals, **FMS-11** separated user-interface screen layout and field validation from application logic in BASIC-PLUS-2, COBOL-11, DIBOL, and FORTRAN programs. It introduced four classic components:
  - **FED (Form Editor)**: Interactive definition of screen layouts and field attributes.
  - **FLB (Form Library Utility)**: Packaging and indexing multiple forms in `.FLB` form libraries.
  - **FUT (Form Utility)**: Inspecting and documenting field attribute tables.
  - **FDV (Form Driver)**: Runtime rendering, data binding (`PUT`/`GET`), protected-field enforcement, and input validation.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine runtime.

---

## 2. Architecture & Subsystems

1. **Form Library Utility (`FLB` / `DIR` / `FORMS`)**:
   - Manages named screen forms (`ORDER_ENTRY`, `EMP_RECORD`, `RSTS_LOGON`) in `FMS.FLB`.
   - Tracks form status (`A` active, `D` deleted), field counts, creation dates, and screen titles.

2. **Form Editor (`FED`: `CREATE` / `ADDFIELD`)**:
   - Creates new forms and attaches structured fields with:
     - **Field Name** (`ORDER_NO`, `CUST_NAME`, `PART_SKU`)
     - **Prompt Label** (`Order Number`, `Customer Name`)
     - **Row & Length** (VT100 row coordinate and character width)
     - **Data Type** (`ALPHA`, `NUMERIC`, `DATE`, `PROTECTED`)

3. **Form Utility (`FUT`: `FIELDS` / `DESCRIBE`)**:
   - Prints complete Field Attribute Tables for any form in the library.

4. **Form Driver Runtime (`FDV`: `PUT`, `GET`, `CLEARFORM`, `VALIDATE`, `DISPLAY`)**:
   - Renders VT100-style forms with underlined input boxes `[10042___]` for editable fields and `<APPROVED>` brackets for display-only `PROTECTED` fields.
   - Enforces `PROTECTED` field write-protection and validates required fields, max lengths, and `NUMERIC` constraints.

---

## 3. Directory Layout

```
apps/fms11/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── fms11           # Compiled native ELF binary
│   ├── fms             # Symlink alias -> fms11
│   ├── fed             # Symlink alias -> fms11
│   └── fdv             # Symlink alias -> fms11
├── build/
│   └── fms11.bobj      # Intermediate BASIC-PLUS-2 object
├── src/
│   └── fms11.bas       # Native DEC BASIC-PLUS-2 source code (< 470 lines)
└── tests/
    ├── __init__.py     # Test package marker
    └── test_fms11.py   # Automated pytest test suite (14 test cases)
```

---

## 4. Command Reference & Syntax

| Command | Aliases | Description |
|---|---|---|
| `DIR` | `FLB`, `FORMS` | Lists all forms in the active Form Library (`FMS.FLB`). |
| `SELECT <name_or_#>` | `FORM` | Selects the active form by name or index number. |
| `CREATE <name>, <title>` | `NEWFORM` | Creates a new form definition in the library (FED). |
| `ADDFIELD <n>,<lbl>,<r>,<l>,<t>[,<v>]` | `FIELD` | Adds a field definition to the active form (FED). |
| `FIELDS` | `DESCRIBE`, `FUT` | Displays the Field Attribute Table for the active form (FUT). |
| `PUT <field>, <value>` | `SET`, `FILL` | Sets a field value in the active form; guards `PROTECTED` fields (FDV). |
| `GET <field>` | - | Displays the current value and attributes of a field (FDV). |
| `CLEARFORM` | `RESETFORM` | Clears all editable (non-protected) fields in the active form (FDV). |
| `VALIDATE` | `CHECK` | Validates required, length, and numeric rules across all fields (FDV). |
| `DISPLAY [form#]` | `RENDER`, `PRINT [ON <f>]`, `EXPORT <f>` | Renders the VT100 screen form to terminal or disk file. |
| `DELETE [form#]` | `DEL` | Marks a form as deleted in the Form Library. |
| `PURGE` | - | Permanently removes deleted forms from the Form Library. |
| `SAMPLE` | `DEMO` | Loads historical DEC FMS-11 forms (`ORDER_ENTRY`, `EMP_RECORD`, `RSTS_LOGON`). |
| `SAVE [file]` | - | Saves the Form Library directory to disk (`FMS.FLB`). |
| `LOAD [file]` | `IMPORT` | Loads Form Library definitions from disk. |
| `SHOW` | `STATUS` | Displays FMS-11 system status and form/field counts. |
| `CLEAR` | `RESET` | Clears all forms and fields from memory. |
| `HELP` | `?` | Displays summary of all available FMS-11 commands. |
| `EXIT` | `QUIT`, `BYE` | Exits the FMS-11 session. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/fms11 clean build
```

Run test suite:
```bash
make -C apps/fms11 test
# or directly:
pytest apps/fms11/tests/
```

Run interactive session:
```bash
make -C apps/fms11 run
```
