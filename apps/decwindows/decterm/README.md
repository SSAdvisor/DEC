# DECwindows DECterm (`decterm` / `dxterm`)

A native **DEC BASIC-PLUS-2** implementation of **DECterm** (`DECW$TERMINAL` / `dxterm`), the flagship XUI and OSF/Motif terminal emulator introduced with **DECwindows** on VAX/VMS V5.1 and ULTRIX Workstations in 1988.

---

## Historical Background

When Digital Equipment Corporation unveiled **DECwindows** in 1988 as one of the earliest commercial X11 Window System environments, **DECterm** provided full hardware-grade **VT300** (VT320/VT330/VT340), **VT220**, **VT100**, and **VT52** terminal emulation inside a windowed workstation session. Key capabilities included:
- **DECCOLM** 80/132-column switching and 24/36/48-row page geometry
- **DECUDK** User-Defined Keys (`F6`–`F20` and `PF1`–`PF4`) for custom DCL/command macros
- **ANSI/VT CSI & SGR** visual attributes (Bold `ESC[1m`, Underline `ESC[4m`, Reverse Video `ESC[7m`, Erase in Display `ESC[2J`)
- **Scrollback Transcript** and session logging (`DECTERM.LOG`)
- **DECSTR** Soft Terminal Reset

---

## Commands Reference

| Command | Description |
| :--- | :--- |
| `SAMPLE` / `DEMO` | Load sample VAX/VMS V5.5-2 `STAR::` VT300 terminal session |
| `SCREEN` / `DISPLAY` | Render the DECwindows XUI/Motif DECterm window and status bar |
| `SCREEN ON <file>` / `EXPORT <file>` | Export rendered DECterm window screen to a file |
| `HISTORY` / `SCROLLBACK` | Display numbered scrollback transcript with SGR attributes |
| `SEND <text>` / `EXEC <text>` | Transmit text or ANSI/VT CSI escape sequence to terminal buffer |
| `DELLINE <n>` | Delete line `#<n>` from the scrollback buffer |
| `MODE VT300\|VT220\|VT100\|VT52` | Switch terminal device emulation personality |
| `COLUMNS 80\|132` | Set terminal screen width (`DECCOLM`) |
| `ROWS 24\|36\|48` | Set terminal page length |
| `CURSOR BLOCK\|UNDERLINE` | Set terminal cursor style |
| `AUTOWRAP ON\|OFF` | Enable or disable auto-wrap (`DECCAWM`) |
| `TITLE <text>` | Set the DECwindows DECterm window title bar |
| `DEFKEY <key> <macro>` | Program a VT300 User-Defined Key (`DECUDK`) |
| `KEYS` / `SHOWKEYS` | Display all programmed UDK and PF key bindings |
| `PRESS <key>` | Trigger a programmed UDK key and transmit its macro |
| `INSPECT` / `ANALYZE` | Audit ANSI/VT CSI escape sequences and SGR attributes |
| `SHOW` / `STATUS` | Display DECterm setup parameters and session statistics |
| `SAVE <file>` / `LOAD <file>` | Save or restore terminal scrollback transcript |
| `CLEAR` / `RESET` | Perform `DECSTR` Soft Terminal Reset |
| `HELP` / `EXIT` | Show command summary or exit DECterm |
