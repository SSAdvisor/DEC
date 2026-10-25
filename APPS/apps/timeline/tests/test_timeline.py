"""Test suite for Timeline DIGI-GL V4.3 Multi-Segmented Ledger (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "timeline"
ALIAS_DIGIGL = APP_DIR / "bin" / "digigl"


def run_timeline(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_timeline_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_DIGIGL.exists() and os.access(ALIAS_DIGIGL, os.X_OK)


def test_timeline_sample_coa_and_trial_balance(tmp_path: Path):
    res = run_timeline("SAMPLE; COA; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Timeline DIGI-GL multi-segmented ledger loaded - 4 segmented accounts]" in out
    assert "[DIGI-GL Trial Balance: Total Debits=$2800K | Total Credits=$2800K — IN BALANCE]" in out


def test_timeline_post_finrpt_save_and_load(tmp_path: Path):
    res1 = run_timeline(
        "SAMPLE; POST 02-100-310-5100-001, Engineering Payroll, 300, 0; POST 02-100-000-2100-000, Accrued Payroll, 0, 300; FINRPT rpt.txt; SAVE mygl.dat; EXIT",
        tmp_path,
    )
    assert res1.returncode == 0
    assert (tmp_path / "rpt.txt").exists()

    res2 = run_timeline("CLEAR; LOAD mygl.dat; TRIAL; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[6 DIGI-GL segmented accounts loaded from mygl.dat]" in res2.stdout
    assert "[DIGI-GL Trial Balance: Total Debits=$3100K | Total Credits=$3100K — IN BALANCE]" in res2.stdout
