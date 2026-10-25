"""Test suite for Compu-Share CAS V6.1 Accounting & Oil/Gas JIB (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "compushare"
ALIAS_CAS = APP_DIR / "bin" / "cas"


def run_compushare(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_compushare_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_CAS.exists() and os.access(ALIAS_CAS, os.X_OK)


def test_compushare_sample_jib_and_revdist(tmp_path: Path):
    res = run_compushare("SAMPLE; PARTNERS; JIB 400; REVDIST 1000; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Compu-Share CAS Division of Interest loaded - 4 owners on PERMIAN-UNIT-14]" in out
    assert "[Total Working Interest = 100% | Total Net Revenue Interest = 100%]" in out
    assert "[CAS JIB Complete: Total Billed to Working Interest Partners = $400K]" in out
    assert "[CAS Revenue Run Complete: Total Disbursed = $1000K]" in out


def test_compushare_add_save_and_load(tmp_path: Path):
    res1 = run_compushare("SAMPLE; ADD OR-50, Mesa Override Trust, 0, 5; SAVE mycas.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_compushare("CLEAR; LOAD mycas.dat; PARTNERS; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 CAS Division of Interest records loaded from mycas.dat]" in res2.stdout
    assert "Mesa Override Trust" in res2.stdout
