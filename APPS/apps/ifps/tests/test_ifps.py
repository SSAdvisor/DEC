"""Test suite for Execucom IFPS/Plus V4.0 Interactive Financial Planning System."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "ifps"
ALIAS_IFPSPLUS = APP_DIR / "bin" / "ifpsplus"


def run_ifps(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_ifps_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_IFPSPLUS.exists() and os.access(ALIAS_IFPSPLUS, os.X_OK)


def test_ifps_sample_model_solve_whatif_goalseek_and_montecarlo(tmp_path: Path):
    res = run_ifps("SAMPLE; MODEL; SOLVE; WHATIF 20; GOALSEEK 3000; MONTECARLO; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Execucom IFPS/Plus corporate model loaded - 4 equations]" in out
    assert "[IFPS SOLVE Complete: 4 simultaneous equations solved | YR3 Net=$2248K]" in out
    assert "[WHAT IF Solution: Adjusted REVENUE=$6000K | Adjusted NET_INCOME=$2040K]" in out
    assert "[GOAL SEEK Converged in 4 iterations: Required REVENUE = $8820K for Target $3000K]" in out
    assert "[MONTE CARLO Complete: Mean=$1700K, P10=$1394K, P90=$2108K]" in out


def test_ifps_add_save_and_load(tmp_path: Path):
    res1 = run_ifps("SAMPLE; ADD 50, AFTER_TAX_NET, NET_INCOME * 0.66, 1122; SAVE myifps.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_ifps("CLEAR; LOAD myifps.dat; SOLVE; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 IFPS equations loaded from myifps.dat]" in res2.stdout
    assert "[IFPS SOLVE Complete: 5 simultaneous equations solved" in res2.stdout
