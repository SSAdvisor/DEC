# DECwindows Calendar (`calendar` / `dxcalendar`)

A native **DEC BASIC-PLUS-2** implementation of **DECwindows Calendar** (`DECW$CALENDAR` / `dxcalendar`), Digital Equipment Corporation's workstation personal and group time management application introduced with DECwindows on VAX/VMS and ULTRIX.

---

## Historical Background

Included in the standard DECwindows desktop accessories alongside DECterm, Bookreader, and Cardfiler, **DECwindows Calendar** stored user schedules in `DECW$CALENDAR.DAT`, offering monthly calendar grids with visual markers on booked days, daily timeslot agendas, audio/popup reminder alarms, search, and timeslot conflict detection.

---

## Commands Reference

| Command | Description |
| :--- | :--- |
| `SAMPLE` / `DEMO` | Load sample October 1991 DEC Maynard Engineering (`ZKO`) schedule (6 appointments) |
| `MONTH` / `GRID` | Display 7-column monthly calendar grid with `*` markers on scheduled dates |
| `DATE <YYYY-MM-DD>` | Set the active calendar date |
| `DAY [YYYY-MM-DD]` / `AGENDA` | Display daily timeslot agenda for the active or specified date |
| `LIST` / `SCHEDULE` / `ALL` | List all appointments across all dates in the calendar |
| `ADD <date\|time\|dur\|alarm\|desc>` | Schedule a new appointment (`alarm` is `ON` or `OFF`) |
| `DELETE <id>` / `CANCEL <id>` | Cancel and remove appointment `#<id>` |
| `ALARM <id> ON\|OFF` | Toggle reminder alarm for appointment `#<id>` |
| `ALARMS` / `REMINDERS` | List all appointments with active alarms (`ON`) |
| `CHECK` / `CONFLICTS` | Audit schedule for overlapping double-booked date/time slots |
| `SEARCH <keyword>` / `FIND` | Search appointments by date, time, or description |
| `DISPLAY [ON <file>]` / `SCREEN` | Render the Motif/XUI Calendar window (or export to file) |
| `SHOW` / `STATUS` | Display calendar profile, active date, appointment count, and alarm count |
| `SAVE <file>` / `LOAD <file>` | Save or load schedule database |
| `CLEAR` / `EXIT` | Clear schedule or exit Calendar |
