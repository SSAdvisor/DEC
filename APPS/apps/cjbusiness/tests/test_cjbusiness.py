"""Test suite for Collier-Jackson CJ/BUSINESS V5.4 (RSTS/E ERP)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "cjbusiness"
ALIAS_CJBIZ = APP_DIR / "bin" / "cjbiz"
ALIAS_CJGL = APP_DIR / "bin" / "cjgl"


def run_cjbusiness(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_cjbusiness_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_CJBIZ.exists() and os.access(ALIAS_CJBIZ, os.X_OK)
    assert ALIAS_CJGL.exists() and os.access(ALIAS_CJGL, os.X_OK)


def test_cjbusiness_sample_cjgl_cjpay_and_cjcirc(tmp_path: Path):
    res = run_cjbusiness("SAMPLE; CJGL; CJPAY; CJCIRC; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Collier-Jackson CJ/BUSINESS suite loaded - 4 module ledgers]" in out
    assert "[CJ/GL Ledger Control Total = $3420K across 4 accounts]" in out
    assert "Gross Payroll:  $640K | FICA Tax: $44K | Fed Withholding: $115K" in out
    assert "Total Publishing Revenue: $2270K" in out


def test_cjbusiness_add_save_and_load(tmp_path: Path):
    res1 = run_cjbusiness("SAMPLE; ADD CJ-500, Sunday Classifieds, CJ/AD, 380; SAVE mycj.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_cjbusiness("CLEAR; LOAD mycj.dat; CJGL; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 CJ/BUSINESS records loaded from mycj.dat]" in res2.stdout
    assert "Sunday Classifieds" in res2.stdout
