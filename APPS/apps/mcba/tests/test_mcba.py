"""Test suite for MCBA V7.2 ERP & Manufacturing Suite (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "mcba"
ALIAS_MCBAMRP = APP_DIR / "bin" / "mcbamrp"


def run_mcba(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_mcba_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_MCBAMRP.exists() and os.access(ALIAS_MCBAMRP, os.X_OK)


def test_mcba_sample_im_and_bomp(tmp_path: Path):
    res = run_mcba("SAMPLE; IM; BOMP; GL; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample MCBA ERP & Manufacturing database loaded - 4 I/M items, BOMP assembly PDP11-SYS]" in out
    assert "[MCBA I/M Summary: 4 items | Total Inventory Value = $384000]" in out
    assert "[BOMP Standard Assembly Cost for 1x PDP11-SYS = $51000]" in out
    assert "MCBA Financial Integration — G/L, A/R, A/P & Payroll Summary" in out


def test_mcba_cop_and_mrp_explosion(tmp_path: Path):
    res = run_mcba("SAMPLE; COP 2; MRP 10; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[MCBA Customer Order Processing (COP): Booked Order #4 for 2x PDP11-SYS — Component allocations updated]" in out
    assert "[MCBA MRP Explosion Complete: 4 Shop Floor Control (SFC) Work Orders released]" in out


def test_mcba_add_save_and_load(tmp_path: Path):
    res1 = run_mcba("SAMPLE; ADD FP11-C, Floating Point Proc, 15, 95; SAVE mymcba.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_mcba("CLEAR; LOAD mymcba.dat; IM; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 MCBA Item Master records loaded from mymcba.dat]" in res2.stdout
    assert "FP11-C" in res2.stdout
