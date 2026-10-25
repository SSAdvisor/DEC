"""Test suite for Heroix RoboMon V5.0 Rule-Based VAX/VMS Operations Manager."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "robomon"
ALIAS_ROBO = APP_DIR / "bin" / "robo"


def run_robomon(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_robomon_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_ROBO.exists() and os.access(ALIAS_ROBO, os.X_OK)


def test_robomon_sample_rules_evaluate_and_autocorrect(tmp_path: Path):
    res = run_robomon("SAMPLE; RULES; EVALUATE 85; AUTOCORRECT; EVALUATE 85; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Heroix RoboMon V5.0 VMS rule base loaded - 4 operational rules]" in out
    assert "[RoboMon EVALUATE Complete:  3 of  4 rules triggered OPCOM alerts]" in out or "3 of  4 rules triggered OPCOM alerts" in out or "3 of 4 rules triggered OPCOM alerts" in out
    assert "State=NOMINAL]" in out
    assert "0 of  4 rules triggered OPCOM alerts" in out or "0 of 4 rules triggered OPCOM alerts" in out


def test_robomon_add_save_and_load(tmp_path: Path):
    res1 = run_robomon("SAMPLE; ADD RL-SEC05, Failed Logins/min, LOCK_TERM, 110; SAVE rules.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_robomon("CLEAR; LOAD rules.dat; RULES; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 RoboMon rules loaded from rules.dat]" in res2.stdout
    assert "RL-SEC05" in res2.stdout
