"""Test suite for Gaussian 90 Ab Initio Quantum Chemistry System."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "gaussian"
ALIAS_G90 = APP_DIR / "bin" / "g90"


def run_gaussian(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_gaussian_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_G90.exists() and os.access(ALIAS_G90, os.X_OK)


def test_gaussian_sample_zmat_scf_pop_and_freq(tmp_path: Path):
    res = run_gaussian("SAMPLE; ZMAT; SCF; POP; FREQ; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Gaussian 90 Formaldehyde (H2CO) Z-Matrix loaded - 4 atoms]" in out
    assert "[SCF Done: E(RHF) = -113.866331 A.U. after 4 cycles | Basis= 36 GTFs]" in out or "[SCF Done: E(RHF) = -113.866331 A.U. after 4 cycles" in out
    assert "[Mulliken Population Complete: Net Charge =  0 me | Dipole = 2.67 Debye]" in out or "Dipole = 2.67 Debye" in out
    assert "[Gaussian 90 FREQ Complete: 0 Imaginary Freqs (Minimum) | ZPE = 18.42 kcal/mol]" in out


def test_gaussian_add_save_and_load(tmp_path: Path):
    res1 = run_gaussian("SAMPLE; ADD F5, C1 R=1.348 A, 6-31G*, -310; SAVE h2cof.g90; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_gaussian("CLEAR; LOAD h2cof.g90; ZMAT; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 Gaussian 90 atoms loaded from h2cof.g90]" in res2.stdout
    assert "F5" in res2.stdout
