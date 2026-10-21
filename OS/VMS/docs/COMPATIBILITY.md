# Historical OS Compatibility Matrix (VAX/VMS vs. PDP-11 RSTS/E)

| Project / Application | Category | VAX/VMS (`OS/VMS`) | PDP-11 RSTS/E (`OS/RSTS-E`) | Historical Provenance & Notes |
| :--- | :--- | :---: | :---: | :--- |
| **`BASIC-PLUS-2` / VAX BASIC** (`basicc`, `basiclink`) | Language / Compiler | **Yes** | **Yes** | DEC BASIC-PLUS-2 was engineered by DEC for source and RMS compatibility across VAX/VMS, RSTS/E, and RSX-11M. |
| **`EDT`** (`edt`) | Text Editor | **Yes** | **Yes** | Standard VAX/VMS interactive line & VT100/VT220 keypad text editor. |
| **`DCL` & Queue Manager** (`dcl`, `dec-printq`) | Command Language & Spooler | **Yes** | **Yes** | Native VAX/VMS DIGITAL Command Language and Batch/Print Job Controller. |
| **`decwindows`** (X11/Motif Suite + 11 GUI Apps) | Workstation GUI | **Yes** | **No** | **Native to VAX/VMS**: DECwindows XUI / OSF/Motif 1.1 (`DECW$SESSION`, `DECterm`, `Bookreader`, `Calendar`, `Cardfiler`, `CDA Viewer`, `Calculator`, `Clock`, `DECsound`, `DECwindows Mail`, `FileView` / `VUE$MASTER`, `Notepad`) was built for 32-bit VAX/VMS workstations. |
| **`datatrieve11`** (`DATATRIEVE` / `DTR`) | 4GL Query & Report | **Yes** | **Yes** | VAX DATATRIEVE & DATATRIEVE-11 with the classic DEC `YACHTS` demonstration domain. |
| **`ade`** | 4GL Database | **Yes** | **Yes** | DEC Application Development Environment supported on VAX/VMS and RSTS/E. |
| **`decgraph`** | Business Graphics | **Yes** | **Yes** | VAX DECgraph presentation graphics system. |
| **`decmail`** (`MAIL`) | Electronic Mail | **Yes** | **Yes** | VAX/VMS Personal Mail Utility (`MAIL`) and DECmail-11. |
| **`decword`** (`WPS`) | Word Processing | **Yes** | **Yes** | WPS-PLUS / DECword for VAX/VMS and RSTS/E. |
| **`fms11`** (`FMS`) | Forms Management | **Yes** | **Yes** | VAX FMS / FMS-11 Forms Management System (`FED`, `FDV`, `FLB`, `FUT`). |
| **`menu11`** (`MENU`) | Menu Control (MCF) | **Yes** | **Yes** | VAX/VMS and PDP-11 Menu Control Facility. |
| **`sort11`** (`SORT`) | System Utility | **Yes** | **Yes** | VAX/VMS `SORT/MERGE` and RMS-11 Sort utility. |
| **`rmsutils`** | RMS Utilities | **Yes** | **Yes** | DEC RMS file design, definition, conversion, backup, restore, and display utilities. |
| **`indent`** | Developer Utility | **Yes** | **Yes** | DECUS BASIC-PLUS-2 / VAX BASIC source code formatter and structure analyzer. |
| **`hamurabi`** | Simulation / Game | **Yes** | **Yes** | Classic DEC BASIC Sumerian economic simulation included on DECUS VAX & PDP-11 tapes. |
| **`dibs`** (`DIBS-11` / `CTS-500`) | ERP / Accounting | **No** | **Yes** | **Strictly 16-bit PDP-11 RSTS/E**: DIBS-11 (`CTS-300`/`CTS-500`) was a PDP-11 commercial RSTS/E package and is rejected under 32-bit VAX/VMS. |
