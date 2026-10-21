# Historical OS Compatibility Matrix (RSTS/E vs. VAX/VMS)

This document records the historical operating system support for every language subsystem and application in the unified DEC workspace, governing which applications are enabled in **RSTS/E (`OS/RSTS-E`)** versus **VAX/VMS (`OS/VMS`)**.

| Project / Application | Category | PDP-11 RSTS/E (`OS/RSTS-E`) | VAX/VMS (`OS/VMS`) | Historical Provenance & Notes |
| :--- | :--- | :---: | :---: | :--- |
| **`BASIC-PLUS-2`** (`basicc`, `basiclink`) | Language / Compiler | **Yes** | **Yes** | DEC BASIC-PLUS-2 was specifically designed by DEC for cross-system compatibility across RSTS/E, RSX-11M, and VAX/VMS. |
| **`EDT`** (`edt`) | Text Editor | **Yes** | **Yes** | Standard interactive line & VT100 keypad text editor across RSTS/E V8–V10 and VAX/VMS. |
| **`DCL` & `PBS`** (`dcl`, `dec-printq`) | Command Language & Spooler | **Yes** | **Yes** | DIGITAL Command Language and Print/Batch Queue subsystem across RSTS/E V9/V10 and VAX/VMS. |
| **`hamurabi`** | Simulation / Game | **Yes** | **Yes** | Originated on DEC PDP-8/PDP-11 RSTS-11 (*101 BASIC Computer Games*, David Ahl, DEC, 1973) and distributed on DECUS VAX tapes. |
| **`sort11`** | System Utility | **Yes** (`SORT11`) | **Yes** (`SORT`) | RMS-11 Sort/Merge utility on PDP-11 RSTS/E (`SORT11`) and VAX/VMS (`SORT`). |
| **`rmsutils`** | RMS-11 Utilities | **Yes** | **Yes** | DEC RMS-11 utilities (`RMSDES`, `RMSDEF`, `RMSIFL`, `RMSCNV`, `RMSBCK`, `RMSRST`, `RMSDSP`) across PDP-11 RSTS/E and VAX/VMS. |
| **`ade`** | 4GL Database | **Yes** | **Yes** | DEC Application Development Environment (1979–1985) supported on both PDP-11 RSTS/E and VAX/VMS. |
| **`datatrieve11`** | 4GL Query & Report | **Yes** (`DTR11`) | **Yes** (`DTR`) | DEC DATATRIEVE-11 on PDP-11 RSTS/E/RSX-11M and VAX DATATRIEVE on VAX/VMS (with classic `YACHTS` domain). |
| **`decgraph`** | Business Graphics | **Yes** | **Yes** | DECgraph presentation charting package supported on PDP-11 RSTS/E and VAX/VMS. |
| **`decmail`** | Electronic Mail | **Yes** (`DECMAIL11`) | **Yes** (`MAIL`) | DECmail-11 on PDP-11 RSTS/E and VMS Mail Utility (`MAIL`) on VAX/VMS. |
| **`decword`** | Word Processing | **Yes** (`DECWORDDP`) | **Yes** (`WPS`) | DECword/DP (PDP-11 RSTS/E turnkey & layered word processing) and WPS-PLUS on VAX/VMS. |
| **`dibs`** (`DIBS-11` / `CTS-500`) | ERP / Accounting | **Yes** | **No** | **Strictly PDP-11 RSTS/E**: DIBS-11 (DEC Integrated Business System) was built for PDP-11 CTS-300/CTS-500 commercial RSTS/E systems. |
| **`fms11`** | Forms Management | **Yes** (`FMS11`) | **Yes** (`FMS`) | DEC Forms Management System (`FED`, `FDV`, `FLB`, `FUT`) on PDP-11 RSTS/E and VAX FMS on VAX/VMS. |
| **`menu11`** | Menu Control (MCF) | **Yes** (`MENU11`) | **Yes** (`MENU`) | DEC Menu Control Facility across PDP-11 RSTS/E (CTS-500) and VAX/VMS. |
| **`indent`** | Developer Utility | **Yes** | **Yes** | DECUS BASIC-PLUS-2 source code pretty-printer and structure analyzer for RSTS/E and VAX/VMS. |
| **`decwindows`** (X11/Motif Suite + 11 GUI Apps) | Workstation GUI | **No** | **Yes** | **Strictly VAX/VMS (and ULTRIX/OSF/1)**: DECwindows XUI/Motif (`DECterm`, `Bookreader`, `Calendar`, `Cardfiler`, `CDA Viewer`, `Calculator`, `Clock`, `DECsound`, `DECwindows Mail`, `FileView`, `Notepad`) required 32-bit VAXstation/VMS architecture and was never supported on 16-bit PDP-11 RSTS/E. |
