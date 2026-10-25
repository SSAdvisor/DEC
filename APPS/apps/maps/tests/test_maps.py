"""Test suite for Ross Systems MAPS V5.0 Accounting & Planning (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "maps"
ALIAS_MAPSGL = APP_DIR / "bin" / "mapsgl"


def run_maps(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_maps_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_MAPSGL.exists() and os.access(ALIAS_MAPSGL, os.X_OK)


def test_maps_sample_centers_and_variance(tmp_path: Path):
    res = run_maps("SAMPLE; CENTERS; VARIANCE; SUBLEDGER; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Ross Systems MAPS/GL hierarchy loaded - 4 Responsibility Centers]" in out
    assert "[MAPS/GL Rollup: Total Budget=$3200K | Total Actual=$3180K | Net Favorable=$20K]" in out
    assert "[MAPS/GL Variance Audit: 3 Favorable Center(s), 1 Unfavorable Center(s)]" in out
    assert "Ross Systems MAPS/AP & MAPS/AR Subledger Integration" in out


def test_maps_model_add_save_and_load(tmp_path: Path):
    res1 = run_maps("SAMPLE; MODEL 10; ADD RC-500, European Operations, 400, 390; SAVE mymaps.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    assert "[MAPS/MODEL Executive Projection (+10%): Current Actual=$3180K -> Next-Year Plan=$3498K]" in res1.stdout

    res2 = run_maps("CLEAR; LOAD mymaps.dat; CENTERS; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 MAPS/GL Responsibility Centers loaded from mymaps.dat]" in res2.stdout
    assert "European Operations" in res2.stdout
