"""Test suite for Comshare System W / Commander EIS Multidimensional DSS."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "systemw"
ALIAS_SYSW = APP_DIR / "bin" / "sysw"
ALIAS_EIS = APP_DIR / "bin" / "eis"


def run_systemw(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_systemw_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_SYSW.exists() and os.access(ALIAS_SYSW, os.X_OK)
    assert ALIAS_EIS.exists() and os.access(ALIAS_EIS, os.X_OK)


def test_systemw_sample_cube_rotate_fxconv_and_briefing(tmp_path: Path):
    res = run_systemw("SAMPLE; CUBE; ROTATE VAR-BY-TIME; FXCONV; BRIEFING; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Comshare System W multidimensional hypercube loaded - 4 slices]" in out
    assert "[Hypercube Consolidated Actual = $6300K across 4 slices]" in out
    assert "[Hypercube ROTATE Complete: Active viewpoint switched to VAR-BY-TIME]" in out
    assert "[FXCONV Translation Complete: USD=$6300K, DEM=10206K, GBP=3402K]" in out
    assert "[Commander EIS Briefing Complete: Favorable Variance +$315K | All Stoplights GREEN]" in out


def test_systemw_add_save_and_load(tmp_path: Path):
    res1 = run_systemw("SAMPLE; ADD LATIN-AM, NET-SALES, FY90-Q4, 700; SAVE mycube.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_systemw("CLEAR; LOAD mycube.dat; CUBE; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 System W hypercube slices loaded from mycube.dat]" in res2.stdout
    assert "[Hypercube Consolidated Actual = $7000K across 5 slices]" in res2.stdout
