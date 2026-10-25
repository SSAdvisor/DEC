"""Test suite for Software House System 1032 VAX/VMS 4GL & Compressed Bitmap DBMS."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "s1032"
ALIAS_SYS1032 = APP_DIR / "bin" / "sys1032"


def run_s1032(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_s1032_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_SYS1032.exists() and os.access(ALIAS_SYS1032, os.X_OK)


def test_s1032_sample_list_find_and_stats(tmp_path: Path):
    res = run_s1032("SAMPLE; LIST; FIND AERO; FIND BIO; STATS; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample System 1032 dataset CLIENTS.DMS loaded - 4 records, Bitmap Index built]" in out
    assert "[System 1032 Bitmap Vector: [1101] -> 3 records selected (0 Disk Reads, Sum=2750)]" in out
    assert "[System 1032 Bitmap Vector: [0010] -> 1 records selected (0 Disk Reads, Sum=640)]" in out
    assert "Rating Summary       : Total=3390 | Mean=847 | Peak=980" in out


def test_s1032_add_save_and_load(tmp_path: Path):
    res1 = run_s1032("SAMPLE; ADD C-105, Biogen Inc, BIO, 890; SAVE mys1032.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    assert "added & Bitmap Index updated: C-105" in res1.stdout
    res2 = run_s1032("CLEAR; LOAD mys1032.dat; FIND BIO; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "System 1032 records loaded from mys1032.dat]" in res2.stdout
    assert "[00101]" in res2.stdout
