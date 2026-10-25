"""Test suite for RTI INGRES V6.2 for VAX/VMS (QUEL, SQL, VIFRED & ABF)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "ingres"
ALIAS_IQUEL = APP_DIR / "bin" / "iquel"
ALIAS_ISQL = APP_DIR / "bin" / "isql"
ALIAS_ABF = APP_DIR / "bin" / "abf"


def run_ingres(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_ingres_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_IQUEL.exists() and os.access(ALIAS_IQUEL, os.X_OK)
    assert ALIAS_ISQL.exists() and os.access(ALIAS_ISQL, os.X_OK)
    assert ALIAS_ABF.exists() and os.access(ALIAS_ABF, os.X_OK)


def test_ingres_sample_quel_isql_vifred_and_abf(tmp_path: Path):
    res = run_ingres("SAMPLE; RETRIEVE; RETRIEVE ENG; ISQL; VIFRED; ABF; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample RTI INGRES V6.2 database VAXINGDB loaded - 4 tuples in relation EMP]" in out
    assert "[QUEL RETRIEVE: (4 tuples) | SUM(E.SALARY BY E.ALL) = $17400]" in out
    assert "[QUEL RETRIEVE: (2 tuples) | SUM(E.SALARY BY E.ALL) = $8100]" in out
    assert "COUNT = 4 | SUM = $17400 | AVG = $4350 | MAX = $4800" in out
    assert "[VIFRED Form EMP_VIF compiled to INGRES System Catalogs (II_FORMS)]" in out
    assert "[ABF 4GL Frame PAYROLL_AUDIT_FRM executed across 4 tuples — 0 errors]" in out


def test_ingres_add_save_and_load(tmp_path: Path):
    res1 = run_ingres("SAMPLE; ADD I105, Rowe Lawrence, ARCH, 4600; SAVE mying.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    assert "[QUEL APPEND TO EMP: (1 tuple) ID=I105" in res1.stdout
    res2 = run_ingres("CLEAR; LOAD mying.dat; ISQL; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 INGRES tuples loaded from mying.dat]" in res2.stdout
    assert "SUM = $22000" in res2.stdout
