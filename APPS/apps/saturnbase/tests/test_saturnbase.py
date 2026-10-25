"""Test suite for Saturn Systems Saturn-Base V3.2 (RSTS/E Relational DBMS)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "saturnbase"
ALIAS_SATBASE = APP_DIR / "bin" / "satbase"
ALIAS_SBASE = APP_DIR / "bin" / "sbase"


def run_saturnbase(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_saturnbase_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_SATBASE.exists() and os.access(ALIAS_SATBASE, os.X_OK)
    assert ALIAS_SBASE.exists() and os.access(ALIAS_SBASE, os.X_OK)


def test_saturnbase_sample_schema_and_query(tmp_path: Path):
    res = run_saturnbase("SAMPLE; SCHEMA; QUERY; QUERY NORTH; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Saturn-Base relational table (CUST_REVENUE) loaded - 4 records in SBASE.DAT]" in out
    assert "[Saturn-Base Query: 4 record(s) matched | Total Revenue = $2820K]" in out
    assert "[Saturn-Base Query: 2 record(s) matched | Total Revenue = $1520K]" in out


def test_saturnbase_add_exportcalc_and_exportwp(tmp_path: Path):
    res = run_saturnbase(
        "SAMPLE; ADD SB-50, Mayo Medical Labs, NORTH, 480; EXPORTCALC; EXPORTWP; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Saturn-Base Record #5 added: SB-50 (Mayo Medical Labs, Region=NORTH, Rev=$480K)]" in out
    assert "[Saturn-Base exported 5 records to Saturn-Calc worksheet SCALC.WKS (Total=$3300K)]" in out
    assert "[Saturn-Base exported 5 mail-merge records to Saturn-WP file SATWP.MRG]" in out
    assert (tmp_path / "SCALC.WKS").exists()
    assert (tmp_path / "SATWP.MRG").exists()


def test_saturnbase_save_and_load(tmp_path: Path):
    res1 = run_saturnbase("SAMPLE; ADD SB-60, Cargill Grain Div, CENT, 850; SAVE mysb.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_saturnbase("CLEAR; LOAD mysb.dat; QUERY CENT; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 Saturn-Base records loaded from mysb.dat]" in res2.stdout
    assert "Cargill Grain Div" in res2.stdout
