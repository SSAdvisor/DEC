# DECwindows (X11 / XUI / OSF/Motif 1.1 Workstation Application Suite)

A native **DEC BASIC-PLUS-2** and **X11 (`libX11` / `libdecw_x11.so`)** implementation of the classic **DECwindows** desktop and workstation application suite originally developed by Digital Equipment Corporation (DEC) for **VAX/VMS**, **ULTRIX**, and **DEC OSF/1 (Digital UNIX)** beginning in 1988–1991.

---

## Native X11 Protocol & OSF/Motif 1.1 Architecture (`x11/`)

All 11 DECwindows applications are integrated with the native **DECwindows X11 Interfacing Library** ([`x11/`](x11)):

- **Shared & Static C/Xlib Library (`lib/libdecw_x11.so`, `lib/libdecw_x11.a`, `include/decw_x11.h`)**:
  - Connects directly to the X11 server (`$DISPLAY`) using the X11 protocol (`XOpenDisplay`, `XCreateSimpleWindow`, `XSelectInput`, `XNextEvent`).
  - Renders authentic **DECwindows XUI / OSF/Motif 1.1** 3D beveled window borders, Steel Blue (`#3B5978`) title bars, P1 green phosphor CRT colors for `DECterm`, and Warm Ivory/Slate Motif palettes for desktop applications.
  - Draws live **X11 vector graphics widgets** (real-time analog clock dial with hour/minute/second hands for `clock`, stereo dB VU meter bars for `decsound`, and status telemetry badges).
  - Provides interactive **clickable 3D Motif `XmPushButton` toolbar buttons** and an interactive **`XmTextField` (`DECW Cmd>`) keyboard input bar** that execute real-time BASIC-PLUS-2 callbacks against the application's persistent state and immediately repaint the X11 window.
- **Invocation Modes (Supported by All 11 Applications)**:
  - **Auto-GUI Default**: Running any DECwindows binary with no arguments from an interactive terminal when `$DISPLAY` is reachable automatically opens the native X11 Motif window.
  - **Force X11 GUI**: Pass `--x11` or `-gui` (or set `DECW_FORCE_X11=1`), or type `X11` (`GUI` / `XDISPLAY`) inside any application's interactive prompt.
  - **Force CLI / Batch Mode**: Pass `--cli` (or set `DECW_FORCE_CLI=1`, or pipe `stdin`) to run in terminal REPL / batch mode.

---

## Sub-Projects Roadmap & Status

The `apps/decwindows/` suite contains the native X11 Interfacing Library & Session Manager plus all 11 DECwindows applications:

| # | Sub-Project | Directory | Executables / Libraries | Status | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | **X11 Library & Session Manager** | [`x11/`](x11) | `libdecw_x11.so`, `libdecw_x11.a`, `decw_x11`, `decwx11`, `dxsession` | **Completed** | Native C/Xlib X11 protocol engine, OSF/Motif 1.1 3D widget toolkit, and BASIC-PLUS-2 Session Manager |
| 1 | **DECterm** | [`decterm/`](decterm) | `decterm`, `dxterm` | **Completed** | VT300/VT220/VT100/VT52 terminal emulator, UDK programmable keys, ANSI/CSI parser, and X11 P1 phosphor window |
| 2 | **Bookreader** | [`bookreader/`](bookreader) | `bookreader`, `dxbook` | **Completed** | Online documentation library, bookshelf navigation, topic hierarchy, full-text search, and X11 hypertext viewer |
| 3 | **Calendar** | [`calendar/`](calendar) | `calendar`, `dxcalendar` | **Completed** | Personal & group time management, daily/monthly schedules, appointments, alarms, and X11 Motif planner |
| 4 | **Cardfiler** | [`cardfiler/`](cardfiler) | `cardfiler`, `dxcardfiler` | **Completed** | Index card database manager for contacts, reference notes, sorting, card decks, and X11 rotary card viewer |
| 5 | **CDA Viewer** | [`cdaviewer/`](cdaviewer) | `cdaviewer`, `dxvdoc` | **Completed** | Compound Document Architecture (DDIF/DTIF/DOTS) document inspector and X11 page renderer |
| 6 | **Calculator** | [`calculator/`](calculator) | `calculator`, `dxcalc` | **Completed** | Desktop scientific, financial, and programmer (DEC/HEX/OCT) calculator with memory tape and X11 keypad |
| 7 | **Clock** | [`clock/`](clock) | `clock`, `dxclock` | **Completed** | Analog/digital workstation clock, multi-timezone display, chime, alarm, and live X11 vector analog dial |
| 8 | **DECsound** | [`decsound/`](decsound) | `decsound`, `dxsound` | **Completed** | Workstation audio clip recorder/player, mu-law waveform analyzer, and X11 stereo VU meter |
| 9 | **DECwindows Mail** | [`dxmail/`](dxmail) | `dxmail`, `decwinmail` | **Completed** | XUI/Motif graphical mail cabinet, folder drawer, DDIF message viewer, and X11 mail window |
| 10 | **FileView** | [`fileview/`](fileview) | `fileview`, `dxfileview` | **Completed** | Workstation graphical file manager, RMS directory browser, DCL verb launcher, and X11 FileView window |
| 11 | **Notepad** | [`notepad/`](notepad) | `notepad`, `dxnotepad` | **Completed** | Desktop text editor with `DECW$CLIPBOARD` cut/copy/paste, search/replace, word-wrap, and X11 editor window |

---

## Building & Testing

Build the X11 library and all 11 DECwindows applications:
```bash
make -C apps/decwindows build
```

Run all DECwindows and X11 test suites (`171` tests):
```bash
make -C apps/decwindows test
```
