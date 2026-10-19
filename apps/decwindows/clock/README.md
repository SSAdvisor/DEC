# DECwindows Clock V3.0 (`DECW$CLOCK` / `dxclock`)

**DECwindows Clock V3.0** is a faithful native DEC BASIC-PLUS-2 implementation of the Digital Equipment Corporation DECwindows desktop clock (`DECW$CLOCK` on VAX/VMS and OpenVMS, `dxclock` on ULTRIX and DEC OSF/1, 1988–1995).

It provides an analog clock dial, 12/24-hour digital time readout, workstation date banner, hourly chime, programmable alarm bell, and a synchronized DEC Worldwide Engineering Timezone table.

---

## Features

- **Maynard / Nashua Workstation Clock Sample (`SAMPLE` / `DEMO`)**:
  - Initializes the workstation clock to `14:30:00` on `TUE 19-OCT-1993` (`EST (UTC-5 Maynard MLO / Nashua ZKO)`), enables the hourly chime and `15:00` alarm (`VAXcluster Quorum & Backup Window`), and loads 6 DEC Worldwide Engineering Sites (`MLO`, `ZKO`, `SRC`, `REO`, `VBO`, `TKO`).
- **Time & Date Management (`SETTIME`, `SETDATE`, `FORMAT 12|24`, `FACE ANALOG|DIGITAL|BOTH`)**:
  - Sets workstation time (`HH:MM[:SS]`) and date banner, switches between 12-hour (`AM`/`PM`) and 24-hour military readout, and configures the clock face presentation.
- **Time Advancement, Hourly Chime & Alarm Bell (`TICK [mins]`, `ALARM`, `CHIME`)**:
  - Advances the clock minute-by-minute (`TICK <mins>`), automatically ringing `[CHIME! Hourly Bell Ring at HH:00]` on the hour and `[ALARM! Bell Ring at HH:MM - <message>]` when reaching the programmed alarm time.
- **DEC Worldwide Engineering Timezones (`ZONES` / `WORLD`, `ADDZONE`)**:
  - Displays synchronized local times across DEC global engineering centers (`MLO` Maynard, `ZKO` Nashua, `SRC` Palo Alto, `REO` Reading UK, `VBO` Valbonne France, `TKO` Tokyo) and supports custom timezone additions.
- **ASCII Analog Dial & Motif / XUI Window Renderer (`DIAL`, `DISPLAY [ON <file>]`, `EXPORT <file>`)**:
  - Renders the ASCII analog clock face and the 78-column DECwindows Clock Motif/XUI window chrome.
- **Persistence (`SAVE <file>`, `LOAD <file>`)**:
  - Saves and restores workstation clock and alarm settings.

---

## Building and Testing

```bash
make -C apps/decwindows/clock build
pytest apps/decwindows/clock/tests/
```
