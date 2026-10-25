"""Test suite for EG&H FSORT3 & VSELECT V3.5 (RSTS/E Sort & Selection)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "fsort3"
ALIAS_VSELECT = APP_DIR / "bin" / "vselect"


def run_fsort3(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_fsort3_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_VSELECT.exists() and os.access(ALIAS_VSELECT, os.X_OK)


def test_fsort3_sample_sort_and_vselect(tmp_path: Path):
    res = run_fsort3("SAMPLE; SORT ASC; SORT DESC; VSELECT 500; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample EG&H FSORT3 dataset loaded - 4 RMS records]" in out
    assert "[EG&H FSORT3 High-Speed Sort Complete: 4 records sorted ASC by Value (First=K-100:320K)]" in out
    assert "[EG&H FSORT3 High-Speed Sort Complete: 4 records sorted DESC by Value (First=K-400:980K)]" in out
    assert "[VSELECT Selected 3 of 4 records | Projected Sum = $2270K]" in out


def test_fsort3_add_save_and_load(tmp_path: Path):
    res1 = run_fsort3("SAMPLE; ADD K-500, Hudson Fab Plant, EAST, 1100; SAVE myfs.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_fsort3("CLEAR; LOAD myfs.dat; SORT DESC; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 FSORT3 records loaded from myfs.dat]" in res2.stdout
    assert "First=K-500:1100K" in res2.stdout
