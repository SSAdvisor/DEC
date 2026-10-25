"""Test suite for Information Builders FOCUS V6.5 4GL & DBMS for VAX/VMS."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "focus"


def run_focus(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_focus_binary_exists():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)


def test_focus_sample_master_table_define_and_graph(tmp_path: Path):
    res = run_focus("SAMPLE; MASTER; TABLE; TABLE EAST; DEFINE; GRAPH; SHOW; FIN", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample FOCUS Master File SALES.MAS & SALES.FOC loaded - 4 segments]" in out
    assert "FILE=SALES, SUFFIX=FOC" in out
    assert "TOTALS ( 4 SEGMENTS)" in out or "TOTALS (4 SEGMENTS)" in out
    assert "$ 2085K" in out or "$2085K" in out
    assert "$ 1260K" in out or "$1260K" in out
    assert "Total PROFIT_K = $ 521K]" in out or "Total PROFIT_K = $521K]" in out
    assert "FOCUS GRAPH FILE SALES SUM DOLLARS BY PROD_CODE" in out


def test_focus_add_save_and_load(tmp_path: Path):
    res1 = run_focus("SAMPLE; ADD VAX-6000, WEST, 10, 600; SAVE myfoc.dat; FIN", tmp_path)
    assert res1.returncode == 0
    assert "[MODIFY FILE SALES: Transactions=1 Accepted=1" in res1.stdout
    res2 = run_focus("CLEAR; LOAD myfoc.dat; TABLE; FIN", tmp_path)
    assert res2.returncode == 0
    assert "FOCUS segments loaded from myfoc.dat]" in res2.stdout
    assert "2685K" in res2.stdout
