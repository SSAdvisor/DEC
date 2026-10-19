# DECwindows X11 / Motif 1.1 Interfacing Library (`apps/decwindows/x11/`)

## Heritage & Architecture

Historically, DECwindows applications on VAX/VMS, ULTRIX, and DEC OSF/1 were built atop the **X11 Window System Protocol** (X11R3 through X11R6), `Xlib` (`DECW$XLIBSHR`), the X Toolkit Intrinsics (`Xt`), and Digital's **XUI** and **OSF/Motif 1.1** widget toolkits (`DECW$XMLIBSHR`).

The `apps/decwindows/x11/` sub-project provides the native **C / Xlib Interfacing Library (`libdecw_x11.so` / `libdecw_x11.a`)**, the **X11 Motif Window & Event Loop Bridge (`decw_x11`)**, and the **BASIC-PLUS-2 X11 Session Manager (`decwx11` / `dxsession`)** that connect all 11 DEC BASIC-PLUS-2 DECwindows applications to live X11 display servers.

---

## Components

1. **`lib/libdecw_x11.so` & `lib/libdecw_x11.a`** (`src/decw_x11.c`, `include/decw_x11.h`):
   - Native C shared and static libraries linked against `-lX11` and `-lm`.
   - Connects to any X11 display server (`$DISPLAY` or `--display`) using `XOpenDisplay`.
   - Implements the authentic **DECwindows XUI / OSF/Motif 1.1 3D color palette** (Steel Blue `#3B5978` title bar, `#AEB2C3` Slate Gray 3D raised/sunken bevels, `#121820` / `#33FF66` P1 green phosphor for `DECterm`, and `#F6F5F0` workstation ivory for desktop applications).
   - Renders 3D beveled Motif title bars, clickable 3D Motif `XmPushButton` toolbars, native X11 vector telemetry widgets (such as a vector `XDrawArc`/`XDrawLine` analog clock dial for `clock` and `XFillRectangle` stereo/mono VU bars for `decsound`), sunken application viewport canvases, and an interactive `XmTextField` command entry box (`DECW Cmd>`).
   - Processes `Expose`, `ConfigureNotify`, `ButtonPress`, `ButtonRelease`, `KeyPress`, and `WM_DELETE_WINDOW` (`ClientMessage`) X11 events, executing interactive callbacks back into the backing BASIC-PLUS-2 application binary and refreshing the X11 window in real time.

2. **`bin/decw_x11`** (`src/decw_x11_main.c`):
   - Native X11 window engine and BASIC-PLUS-2 IPC bridge executable.
   - Supports `--probe`, `--check-gui` (detects interactive TTY + reachable `$DISPLAY` for automatic X11 startup), `--app <id>`, `--frame <path>`, `--state <path>`, `--exec <binary>`, `--geometry <WxH>`, `--autoclose <ms>`, `--verify`, and `--test-interact`.

3. **`bin/decwx11` & `bin/dxsession`** (`src/decwx11.bas`):
   - Native DEC BASIC-PLUS-2 **DECwindows X11 Session Manager** compiled with `basicc` and `basiclink`.
   - Commands: `PROBE`, `APPS` / `LIST`, `LAUNCH <app>`, `X11` / `GUI`, `DISPLAY`, `EXPORT <file>`, `SHOW`, `SAMPLE`, `HELP`, `EXIT`.

---

## Auto-Launch & Dual-Mode Operation Across All 11 DECwindows Applications

Every DECwindows application (`decterm`, `bookreader`, `calendar`, `cardfiler`, `cdaviewer`, `calculator`, `clock`, `decsound`, `dxmail`, `fileview`, `notepad`, and `decwx11`) supports:

- **Automatic X11 GUI Launch**: When launched interactively from a terminal (`isatty(0)`) with `$DISPLAY` set (or when `DECW_FORCE_X11=1` or `--x11` / `-gui` is passed), the application automatically opens its X11 Motif 1.1 GUI window via `decw_x11`.
- **CLI / REPL Fallback**: When `--cli` is passed, `DECW_FORCE_CLI=1` is set, stdin is piped, or `$DISPLAY` is unavailable, the application runs in interactive or batch CLI/REPL mode.
- **`X11` / `GUI` / `XDISPLAY` REPL Command**: Type `X11` or `GUI` at any application's interactive prompt to open its live state in an X11 Motif window on `$DISPLAY`.
