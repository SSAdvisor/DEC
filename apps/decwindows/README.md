# DECwindows (XUI / Motif Workstation Application Suite)

A native **DEC BASIC-PLUS-2** implementation of the classic **DECwindows** desktop and workstation application suite originally developed by Digital Equipment Corporation (DEC) for **VAX/VMS**, **ULTRIX**, and **DEC OSF/1 (Digital UNIX)** beginning in 1988–1991.

---

## Sub-Projects Roadmap & Status

The `apps/decwindows/` sub-project contains 11 independent DECwindows application sub-projects:

| # | Sub-Project | Directory | Executables | Status | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **DECterm** | [`decterm/`](decterm) | `decterm`, `dxterm` | **Completed** | VT300/VT220/VT100/VT52 terminal emulator, UDK programmable keys, ANSI/CSI parser, and scrollback manager |
| 2 | **Bookreader** | `bookreader/` | `bookreader`, `dxbook` | Pending | Online documentation library, bookshelf navigation, topic hierarchy, and full-text search |
| 3 | **Calendar** | `calendar/` | `calendar`, `dxcalendar` | Pending | Personal & group time management, daily/monthly schedules, appointments, and alarms |
| 4 | **Cardfiler** | `cardfiler/` | `cardfiler`, `dxcardfiler` | Pending | Index card database manager for contacts, reference notes, sorting, and card decks |
| 5 | **CDA Viewer** | `cdaviewer/` | `cdaviewer`, `dxvdoc` | Pending | Compound Document Architecture (DDIF/DTIF/DOTS) document inspector and page renderer |
| 6 | **Calculator** | `calculator/` | `calculator`, `dxcalc` | Pending | Desktop scientific, financial, and programmer (DEC/HEX/OCT) calculator with memory tape |
| 7 | **Clock** | `clock/` | `clock`, `dxclock` | Pending | Analog/digital workstation clock, multi-timezone display, chime, and countdown timer/alarm |
| 8 | **DECsound** | `decsound/` | `decsound`, `dxsound` | Pending | Workstation audio clip recorder/player, mu-law waveform analyzer, and voice annotation manager |
| 9 | **DECwindows Mail** | `dxmail/` | `dxmail`, `decwinmail` | Pending | XUI/Motif graphical mail cabinet, folder drawer, message viewer, and composition window |
| 10 | **FileView** | `fileview/` | `fileview`, `dxfileview` | Pending | Workstation graphical file manager, directory browser, DCL verb launcher, and file inspector |
| 11 | **Notepad** | `notepad/` | `notepad`, `dxnotepad` | Pending | Desktop text editor with cut/copy/paste clipboard, search/replace, and line wrapping |

---

## Building & Testing

Build all completed DECwindows sub-projects:
```bash
make -C apps/decwindows build
```

Run all DECwindows test suites:
```bash
make -C apps/decwindows test
```
