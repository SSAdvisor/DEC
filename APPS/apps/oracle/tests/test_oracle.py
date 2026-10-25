"""Test suite for Oracle RDBMS V6.0 for VAX/VMS (SQL*Plus, SQL*Forms & SQL*DBA)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "oracle"
ALIAS_SQLPLUS = APP_DIR / "bin" / "sqlplus"
ALIAS_SQLFORMS = APP_DIR / "bin" / "sqlforms"
ALIAS_SQLDBA = APP_DIR / "bin" / "sqldba"


def run_oracle(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_oracle_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_SQLPLUS.exists() and os.access(ALIAS_SQLPLUS, os.X_OK)
    assert ALIAS_SQLFORMS.exists() and os.access(ALIAS_SQLFORMS, os.X_OK)
    assert ALIAS_SQLDBA.exists() and os.access(ALIAS_SQLDBA, os.X_OK)


def test_oracle_sample_describe_select_forms_and_dba(tmp_path: Path):
    res = run_oracle("SAMPLE; DESCRIBE; SELECT; SELECT RESEARCH; SQLFORMS; SQLDBA; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Oracle V6 tablespace SYSTEM.DBF (ORA_SID=VAXPROD) loaded - 4 rows in SCOTT.EMP]" in out
    assert "SQL*Plus V3.0 DESCRIBE SCOTT.EMP" in out
    assert "[4 rows selected | SUM(SAL) = $14670 | AVG(SAL) = $3667]" in out
    assert "[2 rows selected | SUM(SAL) = $6250 | AVG(SAL) = $3125]" in out
    assert "[SQL*Forms INP Trigger Validation Passed for 4 rows in EMPFORM.INP]" in out
    assert "Background Processes Active  : ORA_VAXPROD_DBWR, LGWR, SMON, PMON, ARCH [RUNNING]" in out


def test_oracle_add_save_and_load(tmp_path: Path):
    res1 = run_oracle("SAMPLE; ADD 7902, FORD JAMES, RESEARCH, 3000; SAVE myora.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    assert "[1 row created in SCOTT.EMP: EMPNO=7902" in res1.stdout
    res2 = run_oracle("CLEAR; LOAD myora.dat; SELECT; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[ 5 Oracle rows loaded from myora.dat]" in res2.stdout or "[5 Oracle rows loaded from myora.dat]" in res2.stdout
    assert "7902" in res2.stdout
