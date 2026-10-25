"""Test suite for Lotus 1-2-3 for VAX/VMS V1.0 (Lotus Development Corp.)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "lotus123"
ALIAS_LOTUS = APP_DIR / "bin" / "lotus"
ALIAS_123 = APP_DIR / "bin" / "123"


def run_lotus123(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_lotus123_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_LOTUS.exists() and os.access(ALIAS_LOTUS, os.X_OK)
    assert ALIAS_123.exists() and os.access(ALIAS_123, os.X_OK)


def test_lotus123_sample_grid_summary_and_datatable(tmp_path: Path):
    res = run_lotus123("SAMPLE; GRID; SUMMARY; DATATABLE; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Lotus 1-2-3 3D worksheet loaded - 4 multi-sheet ranges]" in out
    assert "[3D @Function Summary Complete: @SUM=$4000K, @NPV=$3520K, @IRR=18%]" in out
    assert "[/Data Table Sensitivity Complete: Base=$4000K, Bull=$4600K]" in out


def test_lotus123_add_save_and_load(tmp_path: Path):
    res1 = run_lotus123("SAMPLE; ADD E:B2, Federal Gov Systems, +Q1..Q4_FED, 1000; SAVE my123.wk3; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_lotus123("CLEAR; LOAD my123.wk3; SUMMARY; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 Lotus 1-2-3 cells loaded from my123.wk3]" in res2.stdout
    assert "@SUM=$5000K" in res2.stdout
