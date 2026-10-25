# SPSS-11 (V9.0)

Statistical Package for the Social Sciences for DEC PDP-11 RSTS/E (`spss11`, `spss`).

## Commands
- `SAMPLE` — Load 6-case study dataset (`CASE_ID`, `GRP`, `SCORE`, `INCOME`)
- `DATALIST` / `LIST` — Display active cases in system file
- `FREQUENCIES` — Generate categorical frequency & cumulative percentage table for `GRP`
- `CONDESCRIPTIVE` — Compute `MEAN`, `SUM`, `MIN`, `MAX`, `RANGE` for `SCORE` and `INCOME`
- `CROSSTABS` — Generate 2x2 contingency table (`GRP` by `SCORE_TIER`) with Chi-Square
- `ANOVA` / `ONEWAY` — Perform One-Way ANOVA of `SCORE` by `GRP`
- `PEARSON` / `CORR` — Compute Pearson correlation between `SCORE` and `INCOME`
- `ADD`, `SAVE [file]`, `LOAD [file]`, `SHOW` / `VARLABELS`, `CLEAR`, `HELP`, `FINISH` / `EXIT`
