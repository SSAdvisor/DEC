"""Test suite for Cincom Systems TOTAL V8.0 Network DBMS (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "total"
ALIAS_TOTDBM = APP_DIR / "bin" / "totdbm"


def run_total(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_total_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_TOTDBM.exists() and os.access(ALIAS_TOTDBM, os.X_OK)


def test_total_dbgen_sinon_and_sample(tmp_path: Path):
    res = run_total("DBGEN CORPDB; SINON UPDATE; SAMPLE; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "BEGIN-DATA-BASE-GENERATION: CORPDB" in out
    assert "[TOTAL DML SINON: Signed on to Database CORPDB in UPDATE mode — Status: ****]" in out
    assert "[Sample CINCOM TOTAL network database loaded - 3 CUSTM Master records, 4 ORDERV Chained records]" in out
    assert "CINCOM TOTAL V8.0 Nucleus Status:" in out


def test_total_readm_and_findx_chain_traversal(tmp_path: Path):
    res = run_total("SAMPLE; READM; FINDX C100; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "CINCOM TOTAL Master Data Set (CUSTM) — Direct Key Lookup" in out
    assert "Digital Equipment Corp" in out
    assert "[DML READM Status: **** (3 Master record(s) retrieved)]" in out
    assert "CINCOM TOTAL Variable Entry Data Set (ORDERV) — Linkage Path Traversal" in out
    assert "[DML FINDX/READV Status: **** (2 chained records, Total=$1830K)]" in out


def test_total_addm_and_addv_linkage(tmp_path: Path):
    res = run_total(
        "SAMPLE; ADDM C400, Raytheon Missile Sys, 6000; ADDV C400, ORD-401, VAX-11/780 Link, 920; FINDX C400; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[TOTAL DML ADDM: Master CUSTM record #4 added (Key=C400, Name=Raytheon Missile Sys, Credit=6000K) — Status: ****]" in out
    assert "[TOTAL DML ADDV: Variable ORDERV record #5 linked to Master C400 (ORD-401, $920K) — Status: ****]" in out
    assert "[DML FINDX/READV Status: **** (1 chained records, Total=$920K)]" in out


def test_total_export_save_and_load(tmp_path: Path):
    res1 = run_total(
        "SAMPLE; ADDM C500, Boeing Aerospace, 7500; EXPORT totrpt.txt; SAVE mytot.dat; EXIT",
        tmp_path,
    )
    assert res1.returncode == 0
    assert (tmp_path / "totrpt.txt").exists()
    assert "Boeing Aerospace" in (tmp_path / "totrpt.txt").read_text()

    res2 = run_total("CLEAR; LOAD mytot.dat; READM C500; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[TOTAL database loaded from mytot.dat (4 Master, 4 Variable records)]" in res2.stdout
    assert "Boeing Aerospace" in res2.stdout
