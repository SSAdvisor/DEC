# Access Technology 20/20 V2.3 (Supercomp-20) Electronic Spreadsheet

**Access Technology 20/20 V2.3** (*Supercomp-20*) is an authentic DEC BASIC-PLUS-2 recreation of the industry-standard minicomputer electronic spreadsheet authored by **Access Technology, Inc. (South Natick, MA)** for DEC PDP-11 RSTS/E, RSX-11M, and VAX/VMS systems (1981–1992).

## Features
- **2D Worksheet Grid (`A1..D8`)**: Interactive and batch cell modeling with `/` slash command bar (`/W`, `/C`, `/F`, `/G`, `/M`, `/P`, `/S`, `/Q`).
- **Formula Engine**: `@SUM`, `@AVG`, `@IF`, `@NPV`, `@IRR`, and `@LOOKUP`.
- **Goal-Seeking (`/G` / `GOALSEEK`)**: Automated backward solver for target revenue/profit goals.
- **Multi-Sheet Consolidation (`/M` / `CONSOLIDATE`)**: Regional division consolidation into corporate master worksheets.
- **RMS / DATATRIEVE-11 Interchange (`SC20WS.DAT`)**: Pipe-delimited worksheet persistence and report generation (`EXPORT`).

## Usage
```bash
./bin/calc2020 "SAMPLE; GRID; FINANCE 10; GOALSEEK 2600; CONSOLIDATE 15; EXIT"
```
