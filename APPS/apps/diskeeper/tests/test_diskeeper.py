"""Test suite for Executive Software DISKEEPER V4.0 Online Disk Defragmenter."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "diskeeper"
ALIAS_DEFRAG = APP_DIR / "bin" / "defrag"


def run_diskeeper(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_diskeeper_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_DEFRAG.exists() and os.access(ALIAS_DEFRAG, os.X_OK)


def test_diskeeper_sample_analyze_defrag_and_map(tmp_path: Path):
    res = run_diskeeper("SAMPLE; ANALYZE; DEFRAG; MAP; ANALYZE; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample ODS-2 Volume VAX01$DKA0: scanned - 4 INDEXF.SYS file headers]" in out
    assert "[DISKEEPER ANALYZE: 4 fragmented files | Total Extents = 77]" in out
    assert "[DISKEEPER DEFRAG Complete: 73 excess extents eliminated | Volume=OPTIMIZED]" in out
    assert "[DISKEEPER MAP Rendered: Volume State = OPTIMIZED]" in out


def test_diskeeper_add_save_and_load(tmp_path: Path):
    res1 = run_diskeeper("SAMPLE; ADD FID-105, SWAPFILE.SYS, [SYS0], 19; SAVE dka0.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_diskeeper("CLEAR; LOAD dka0.dat; ANALYZE; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 DISKEEPER records loaded from dka0.dat]" in res2.stdout
    assert "SWAPFILE.SYS" in res2.stdout
    assert "Total Extents = 96" in res2.stdout
