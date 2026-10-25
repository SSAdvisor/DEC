"""Test suite for Cognos PowerHouse 4GL V5.0 (PDL / QUICK / QUIZ / QTP) for VAX/VMS."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "powerhouse"
ALIAS_PHOUSE = APP_DIR / "bin" / "phouse"
ALIAS_QUICK = APP_DIR / "bin" / "quick"
ALIAS_QUIZ = APP_DIR / "bin" / "quiz"
ALIAS_QTP = APP_DIR / "bin" / "qtp"


def run_powerhouse(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_powerhouse_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_PHOUSE.exists() and os.access(ALIAS_PHOUSE, os.X_OK)
    assert ALIAS_QUICK.exists() and os.access(ALIAS_QUICK, os.X_OK)
    assert ALIAS_QUIZ.exists() and os.access(ALIAS_QUIZ, os.X_OK)
    assert ALIAS_QTP.exists() and os.access(ALIAS_QTP, os.X_OK)


def test_powerhouse_sample_pdl_quick_quiz_and_qtp(tmp_path: Path):
    res = run_powerhouse("SAMPLE; PDL; QUICK; QUIZ; QUIZ OTTAWA; QTP; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Cognos PowerHouse Dictionary CORP_PHD loaded - 4 RMS records in ORDERS]" in out
    assert "RECORD ORDERS ORGANIZATION INDEXED FILE 'ORDERS.RMS'" in out
    assert "[QUICK Screen ORD_QUICK.QKC compiled against PHD CORP_PHD" in out
    assert "SUBTOTAL ORDER-AMT = $ 2800K" in out or "SUBTOTAL ORDER-AMT = $2800K" in out
    assert "SUBTOTAL ORDER-AMT = $ 1120K" in out or "SUBTOTAL ORDER-AMT = $1120K" in out
    assert "[QTP Batch Run Completed:  4 subfile records written to GL_POST.SF]" in out or "subfile records written to GL_POST.SF" in out


def test_powerhouse_add_save_and_load(tmp_path: Path):
    res1 = run_powerhouse("SAMPLE; ADD P-1005, Corel Corp, OTTAWA, 500; SAVE myph.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    assert "[QUICK Transaction Entry: Record #" in res1.stdout
    res2 = run_powerhouse("CLEAR; LOAD myph.dat; QUIZ; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "PowerHouse records loaded from myph.dat]" in res2.stdout
    assert "3300K" in res2.stdout
