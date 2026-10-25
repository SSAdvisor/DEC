"""Test suite for Cerner PathNet V3.0 Clinical Laboratory Information System (VAX/VMS)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "cerner"
ALIAS_PATHNET = APP_DIR / "bin" / "pathnet"


def run_cerner(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_cerner_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_PATHNET.exists() and os.access(ALIAS_PATHNET, os.X_OK)


def test_cerner_sample_verify_panic_and_chart(tmp_path: Path):
    res = run_cerner("SAMPLE; ACCESSION; VERIFY; PANIC; CHART; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Cerner PathNet V3.0 LIS dataset loaded - 4 Clinical Specimen Accessions]" in out
    assert "[Cerner PathNet Analyzer Verification Complete: 2 Verified Normal | 2 Critical Panic Flagged]" in out
    assert "[PathNet Panic Summary: 2 Critical Panic Value Alerts requiring MD notification]" in out
    assert "[PathNet Cumulative Chart: 4 results charted | Aggregate Assay Index = 703]" in out


def test_cerner_order_save_and_load(tmp_path: Path):
    res1 = run_cerner("SAMPLE; ORDER AC-9005, ADAMS JOHN, CALCIUM, 62, 85, 105; VERIFY; SAVE mypath.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_cerner("CLEAR; LOAD mypath.dat; PANIC; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 PathNet records loaded from mypath.dat]" in res2.stdout
    assert "[PathNet Panic Summary: 3 Critical Panic Value Alerts requiring MD notification]" in res2.stdout
