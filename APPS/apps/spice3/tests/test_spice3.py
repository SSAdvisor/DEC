"""Test suite for VAX SPICE 3D1 / HSPICE Electronic Circuit Simulator."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "spice3"
ALIAS_SPICE = APP_DIR / "bin" / "spice"
ALIAS_HSPICE = APP_DIR / "bin" / "hspice"


def run_spice3(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_spice3_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_SPICE.exists() and os.access(ALIAS_SPICE, os.X_OK)
    assert ALIAS_HSPICE.exists() and os.access(ALIAS_HSPICE, os.X_OK)


def test_spice3_sample_op_tran_and_ac(tmp_path: Path):
    res = run_spice3("SAMPLE; NETLIST; OP; TRAN; AC; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample VAX SPICE 3D1 circuit deck loaded - 5 elements]" in out
    assert "[SPICE3 .OP DC Operating Point Converged: V(1)=5000mV V(2)=3400mV V(3)=2200mV]" in out
    assert "[SPICE3 .TRAN Transient Analysis Complete: Peak V(3)=3150mV at t=30ns]" in out
    assert "[SPICE3 .AC Bode Sweep Complete: Midband Gain=24dB | f_3dB=10MHz]" in out


def test_spice3_add_save_and_load(tmp_path: Path):
    res1 = run_spice3("SAMPLE; ADD M1, N3 -> N2 -> GND, NMOS_KP, 250; SAVE amp.cir; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_spice3("CLEAR; LOAD amp.cir; NETLIST; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[6 SPICE3 elements loaded from amp.cir]" in res2.stdout
    assert "M1" in res2.stdout
