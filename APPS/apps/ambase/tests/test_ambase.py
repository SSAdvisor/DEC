"""Test suite for Amcor AMBASE / AMWRITER / AMQUERY V4.2 (RSTS/E DBMS)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "ambase"
ALIAS_AMQRY = APP_DIR / "bin" / "amqry"
ALIAS_AMWRITER = APP_DIR / "bin" / "amwriter"


def run_ambase(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_ambase_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_AMQRY.exists() and os.access(ALIAS_AMQRY, os.X_OK)
    assert ALIAS_AMWRITER.exists() and os.access(ALIAS_AMWRITER, os.X_OK)


def test_ambase_sample_schema_and_amquery(tmp_path: Path):
    res = run_ambase("SAMPLE; SCHEMA; AMQUERY; AMQUERY ENGR; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample AMBASE database loaded - 4 indexed records in AMBASE.DAT]" in out
    assert "AMBASE V4.2 Data Dictionary & B-Tree Index Schema" in out
    assert "[AMQUERY: 4 record(s) selected | Total Budget = 3290]" in out
    assert "[AMQUERY: 2 record(s) selected | Total Budget = 1720]" in out


def test_ambase_add_amwriter_and_amgen(tmp_path: Path):
    res = run_ambase(
        "SAMPLE; ADD E105, Dick Hustvedt, ENGR, 810; AMWRITER rpt.txt; AMGEN PAY_FORM; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[AMBASE Record #5 inserted: Key=E105 (Dick Hustvedt, Dept=ENGR, Budget=810)]" in out
    assert "Records Processed: 5 | Total Budget: 4100 | Mean Budget: 820" in out
    assert "[AMGEN compiled screen PAY_FORM.SCR — 4 bound AMBASE fields verified]" in out
    assert (tmp_path / "rpt.txt").exists()


def test_ambase_save_and_load(tmp_path: Path):
    res1 = run_ambase("SAMPLE; ADD E106, Nancy Kronenberg, ENGR, 790; SAVE mydb.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_ambase("CLEAR; LOAD mydb.dat; AMQUERY ENGR; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 AMBASE records loaded from mydb.dat]" in res2.stdout
    assert "Nancy Kronenberg" in res2.stdout
