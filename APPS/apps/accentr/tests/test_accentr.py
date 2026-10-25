"""Test suite for NIS ACCENT R V11.4 4GL & RDBMS (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "accentr"
ALIAS_ACCENT = APP_DIR / "bin" / "accent"
ALIAS_ACCR = APP_DIR / "bin" / "accr"


def run_accentr(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_accentr_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_ACCENT.exists() and os.access(ALIAS_ACCENT, os.X_OK)
    assert ALIAS_ACCR.exists() and os.access(ALIAS_ACCR, os.X_OK)


def test_accentr_sample_dsd_and_extract(tmp_path: Path):
    res = run_accentr("SAMPLE; DSD; EXTRACT; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample ACCENT R Data Base Library (CORP_DBL) loaded - 4 records in Data Set INV_DS]" in out
    assert "DEFINE SD INV_SD" in out
    assert "[EXTRACT Complete: 4 records in INV_DS | Total Valuation = 5975]" in out


def test_accentr_add_pm_and_cm(tmp_path: Path):
    res = run_accentr(
        "SAMPLE; ADD TU16-M, TU16 9-Track Magtape, 8, 90; PM AUDIT_PM; CM DAILY_CM; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[ACCENT R Data Set INV_DS: Record #5 added (TU16-M, Qty=8, Unit=90)]" in out
    assert "ACCENT R Process Module (PM): AUDIT_PM Execution" in out
    assert "Records Processed: 5 | Reorder Alerts (<10 Qty): 2" in out
    assert "Computed Portfolio Valuation: $669500" in out
    assert "[ACCENT R Command Module (CM) DAILY_CM: Verified DBL CORP_DBL" in out


def test_accentr_export_save_and_load(tmp_path: Path):
    res1 = run_accentr("SAMPLE; ADD LP11-P, LP11 Line Printer, 5, 75; EXPORT out.txt; SAVE myacc.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    assert (tmp_path / "out.txt").exists()

    res2 = run_accentr("CLEAR; LOAD myacc.dat; EXTRACT; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 ACCENT R Data Set records loaded from myacc.dat]" in res2.stdout
    assert "LP11-P" in res2.stdout
