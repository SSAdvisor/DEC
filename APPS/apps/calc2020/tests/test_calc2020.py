"""Test suite for Access Technology 20/20 V2.3 (Supercomp-20) Electronic Spreadsheet."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "calc2020"
ALIAS_2020 = APP_DIR / "bin" / "2020"
ALIAS_SC20 = APP_DIR / "bin" / "sc20"


def run_calc2020(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_calc2020_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_2020.exists() and os.access(ALIAS_2020, os.X_OK)
    assert ALIAS_SC20.exists() and os.access(ALIAS_SC20, os.X_OK)


def test_calc2020_sample_grid_and_formulas(tmp_path: Path):
    res = run_calc2020("SAMPLE; GRID; FORMULAS; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample 20/20 worksheet loaded - 6 rows x 4 columns (A1..D6), formulas evaluated]" in out
    assert "Access Technology 20/20 Worksheet: 20/20 Corporate Financial Model" in out
    assert "20/20 Worksheet Formula Audit (/F)" in out
    assert "Row 4 (Total Revenue         ): D4 = @SUM(1..3) -> 2400" in out
    assert "Row 6 (Net Operating Inc     ): D6 = @IF(4-5) -> 1030" in out


def test_calc2020_set_cell_recalc_and_goalseek(tmp_path: Path):
    res = run_calc2020(
        "SAMPLE; SET A1, 500; RECALC; GOALSEEK 2800; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Cell A1 set to 500 | Row 1 Total (D1)=1450]" in out
    assert "Row 4 Total Revenue=2500" in out
    assert "[20/20 Goal-Seek (/G): Target Total Revenue (D4) = 2800 -> Solved A1 (Hardware Q1) = 800, New D4 = 2800]" in out


def test_calc2020_finance_and_consolidate(tmp_path: Path):
    res = run_calc2020(
        "SAMPLE; FINANCE 10; CONSOLIDATE 20; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "20/20 Financial Analysis (@NPV / @IRR / @LOOKUP)" in out
    assert "@NPV(10%, A6..C6) = 855" in out
    assert "@IRR(A6..C6)       = 28%" in out
    assert "[20/20 Multi-Sheet Consolidation (/M): Merged Division #2 (+20%) -> Total Revenue D4=2880, Net Income D6=1510]" in out


def test_calc2020_export_save_and_load(tmp_path: Path):
    res1 = run_calc2020(
        "SAMPLE; LABEL 7, R&D Investment; SET A7, 50; SET B7, 60; SET C7, 70; EXPORT report.txt; SAVE mymodel.dat; EXIT",
        tmp_path,
    )
    assert res1.returncode == 0
    assert (tmp_path / "report.txt").exists()
    assert "R&D Investment" in (tmp_path / "report.txt").read_text()

    res2 = run_calc2020("CLEAR; LOAD mymodel.dat; GRID; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[7 worksheet rows loaded from mymodel.dat]" in res2.stdout
    assert "R&D Investment" in res2.stdout
