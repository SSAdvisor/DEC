# Saturn Systems Saturn-Calc V3.4 Electronic Worksheet

**Saturn-Calc V3.4** is an authentic DEC BASIC-PLUS-2 recreation of the virtual-array VT100 electronic spreadsheet authored by **Saturn Systems, Inc. (Minneapolis, MN)** for DEC PDP-11 RSTS/E systems (1982–1990).

## Features
- **Virtual-Array VT100 Worksheet (`SCALC.DAT`)**: Multi-division H1, H2, Annual Total, and Variance grid.
- **Split-Window Dual Pane View (`SPLIT` / `WINDOW`)**: Simultaneous inspection of core divisions and expansion/export operations.
- **Financial Depreciation & Amortization**: `@SLN`, `@DDB`, and `@SYD` asset depreciation (`DEPREC`) plus `@PMT` loan amortization (`LOAN`).
- **Saturn-Graph & Saturn-WP Handoff**: Direct VT100 bar charting (`GRAPH`) and `SCALC.WKS` export (`EXPORTWP`) for `Saturn-WP`.

## Usage
```bash
./bin/saturncalc "SAMPLE; GRID; SPLIT 3; DEPREC 1200, 200, 5; LOAN 1000, 12, 5; GRAPH; EXIT"
```
