"""Test suite for SAS System V6.06 for VAX/VMS (SAS Institute, Inc.)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "sas"
ALIAS_SASVMS = APP_DIR / "bin" / "sasvms"


def run_sas(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_sas_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_SASVMS.exists() and os.access(ALIAS_SASVMS, os.X_OK)


def test_sas_sample_print_means_freq_and_reg(tmp_path: Path):
    res = run_sas("SAMPLE; PRINT; MEANS; FREQ; REG; SHOW; ENDSAS", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "NOTE: The data set WORK.CLINICAL has 4 observations and 4 variables." in out
    assert "[SAS PROC MEANS: N=4 | RESPONSE Mean=75 | Min=45 | Max=105 | Sum=300]" in out
    assert "[SAS PROC FREQ TABLE GROUP: ACTIVE=3 (75%) | OTHER=1 (25%)]" in out
    assert "[SAS PROC REG Complete: RESPONSE = 25 + 2 * DOSE_MG | R-Square = 0.9950]" in out


def test_sas_add_save_and_load(tmp_path: Path):
    res1 = run_sas("SAMPLE; ADD SUBJ-05, ACTIVE, 50, 125; SAVE mysas.dat; ENDSAS", tmp_path)
    assert res1.returncode == 0
    res2 = run_sas("CLEAR; LOAD mysas.dat; MEANS; ENDSAS", tmp_path)
    assert res2.returncode == 0
    assert "[5 SAS observations loaded from library mysas.dat]" in res2.stdout
    assert "RESPONSE Mean=85" in res2.stdout
    assert "Sum=425" in res2.stdout
