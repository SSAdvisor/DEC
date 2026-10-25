# Nyplan, Inc. NYPLAN V4.1 Corporate Financial Modeling & Risk Analysis

**NYPLAN V4.1** is an authentic DEC BASIC-PLUS-2 recreation of the corporate financial modeling, budgeting, and risk simulation language authored by **Nyplan, Inc. (Kirkland, WA)** for DEC PDP-11 RSTS/E and VAX/VMS systems (1978–1988).

## Features
- **Corporate P&L & Budget Modeling (`NYPLAN.DAT`)**: Budget, Actual, Variance (`Actual - Budget`), and Multi-Year Forecast evaluation.
- **"What-If" Sensitivity Analysis (`WHATIF` / `SENSITIVITY`)**: Pro-forma P&L evaluation under simultaneous revenue growth and cost inflation assumptions.
- **Monte Carlo Variance & Risk Simulation (`MONTECARLO` / `RISK`)**: Pessimistic (`P10`), Expected (`Mean`), and Optimistic (`P90`) Net Operating Profit confidence intervals.
- **Multi-Division P&L Consolidation (`CONSOLIDATE`)**: Automated roll-up of subsidiary division statements into corporate consolidated P&L reports (`EXPORT`).

## Usage
```bash
./bin/nyplan "SAMPLE; MODEL; WHATIF 20, 5; MONTECARLO 250; CONSOLIDATE 25; EXIT"
```
