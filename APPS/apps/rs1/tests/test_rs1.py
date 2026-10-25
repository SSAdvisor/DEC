"""Test suite for BBN RS/1 V4.0 Electronic Research Notebook (VAX/VMS)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "rs1"
ALIAS_BBNRS1 = APP_DIR / "bin" / "bbnrs1"


def run_rs1(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_rs1_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_BBNRS1.exists() and os.access(ALIAS_BBNRS1, os.X_OK)


def test_rs1_sample_display_fit_compare_graph_and_rpl(tmp_path: Path):
    res = run_rs1("SAMPLE; DISPLAY; FIT; COMPARE; GRAPH; RPL; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample BBN RS/1 Notebook Table #1 WAFER_YIELD loaded - 4 experimental runs]" in out
    assert "[RS/1 FIT Complete: Slope=0.6%/C | R-Square=0.998 | Max Residual=0%]" in out
    assert "[RS/1 COMPARE Two-Sample Test: Mean Yield=81% | CMOS-A Runs=3 | p-value=0.012 SIGNIFICANT]" in out
    assert "[RS/1 GRAPH Rendered: 4 data points plotted within 3-Sigma control limits]" in out
    assert "[RS/1 RPL Procedure $ANALYZE_WAFER executed: 4 rows processed | Yield Sum=324]" in out


def test_rs1_add_save_and_load(tmp_path: Path):
    res1 = run_rs1("SAMPLE; ADD EXP-105, CMOS-B, 440, 96; SAVE myrs1.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_rs1("CLEAR; LOAD myrs1.dat; RPL; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 RS/1 notebook rows loaded from myrs1.dat]" in res2.stdout
    assert "Yield Sum=420" in res2.stdout
