"""Test suite for Swanson Analysis ANSYS V4.4 Finite Element Analysis (FEA) Suite."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "ansys"


def run_ansys(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_ansys_binary_exists():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)


def test_ansys_sample_prep7_solve_and_post1(tmp_path: Path):
    res = run_ansys("SAMPLE; PREP7; SOLVE; POST1; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample ANSYS V4.4 FEA structural mesh loaded - 4 elements]" in out
    assert "[ANSYS /SOLU Frontal Matrix Solution Converged: 4 elements | 96 DOF]" in out
    assert "[ANSYS /POST1 Summary: Max Von Mises = 240 MPa at E-101 | Min SF = 3]" in out


def test_ansys_add_save_and_load(tmp_path: Path):
    res1 = run_ansys("SAMPLE; ADD E-105, STIF45 Flange Lug, TI64, 310; SAVE wing.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_ansys("CLEAR; LOAD wing.dat; POST1; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 ANSYS elements loaded from wing.dat]" in res2.stdout
    assert "Max Von Mises = 310 MPa at E-105" in res2.stdout
