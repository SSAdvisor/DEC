"""Test suite for Saturn Systems Saturn-Calc V3.4 (RSTS/E Electronic Spreadsheet)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "saturncalc"
ALIAS_SATCALC = APP_DIR / "bin" / "satcalc"
ALIAS_SCALC = APP_DIR / "bin" / "scalc"


def run_saturncalc(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_saturncalc_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_SATCALC.exists() and os.access(ALIAS_SATCALC, os.X_OK)
    assert ALIAS_SCALC.exists() and os.access(ALIAS_SCALC, os.X_OK)


def test_saturncalc_sample_grid_and_split_window(tmp_path: Path):
    res = run_saturncalc("SAMPLE; GRID; SPLIT 3; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Saturn-Calc worksheet loaded - 5 divisions, Total=3000K]" in out
    assert "Saturn-Calc V3.4 Virtual Worksheet (SCALC.DAT)" in out
    assert "[WINDOW 1 - TOP PANE: Rows 1 to 3 (Core Regional Divisions)]" in out
    assert "[WINDOW 2 - BOTTOM PANE: Rows 4 to 5 (Expansion & Export)]" in out
    assert "Saturn-Calc V3.4 Status:" in out


def test_saturncalc_depreciation_and_loan_amortization(tmp_path: Path):
    res = run_saturncalc(
        "SAMPLE; DEPREC 1200, 200, 5; LOAN 1000, 12, 5; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "Saturn-Calc Financial Depreciation Schedule (@SLN / @DDB / @SYD)" in out
    assert "@SLN = $200K / year" in out
    assert "@DDB (Year 1) = $480K" in out
    assert "@SYD (Year 1) = $333K" in out
    assert "Saturn-Calc Loan Amortization & @PMT Schedule" in out
    assert "@PMT = $272K / year" in out


def test_saturncalc_set_graph_and_exportwp(tmp_path: Path):
    res = run_saturncalc(
        "SAMPLE; SET 1, 500, 600; GRAPH; EXPORTWP; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Saturn-Calc Row #1 updated: H1=500K, H2=600K, Annual=1100K | Grand Total=3200K]" in out
    assert "Saturn-Graph V3.4 Handoff — Division Annual Revenue Chart ($K)" in out
    assert "[Saturn-Calc worksheet exported to Saturn-WP link file SCALC.WKS (Total=3200K)]" in out
    assert (tmp_path / "SCALC.WKS").exists()
    assert "GRAND TOTAL|H1=1430K|H2=1770K|TOTAL=3200K" in (tmp_path / "SCALC.WKS").read_text()


def test_saturncalc_save_and_load(tmp_path: Path):
    res1 = run_saturncalc(
        "SAMPLE; LABEL 6, Pacific Rim Div; SET 6, 150, 250; SAVE mycalc.dat; EXIT",
        tmp_path,
    )
    assert res1.returncode == 0
    assert (tmp_path / "mycalc.dat").exists()

    res2 = run_saturncalc("CLEAR; LOAD mycalc.dat; GRID; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[6 Saturn-Calc rows loaded from mycalc.dat]" in res2.stdout
    assert "Pacific Rim Div" in res2.stdout
    assert "3400" in res2.stdout
