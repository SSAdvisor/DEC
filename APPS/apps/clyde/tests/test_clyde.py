import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "clyde"
CONTRL_ALIAS = APP_DIR / "bin" / "contrl"
CAUDIT_ALIAS = APP_DIR / "bin" / "caudit"


def run_clyde(commands: list[str], cwd: Path) -> subprocess.CompletedProcess:
    input_text = "\n".join(commands) + "\n"
    return subprocess.run(
        [str(BIN_PATH)],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )


def test_clyde_binaries_exist():
    assert BIN_PATH.exists()
    assert CONTRL_ALIAS.exists()
    assert CAUDIT_ALIAS.exists()


def test_clyde_sample_observe_audit_and_lock(tmp_path):
    res = run_clyde(
        [
            "SAMPLE",
            "TERMINALS",
            "OBSERVE KB11:",
            "LOCK KB11:",
            "OBSERVE KB11:",
            "AUDIT",
            "UNLOCK KB11:",
            "EXIT",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Clyde Security dataset loaded - 5 RSTS/E KB: sessions]" in out
    assert "Clyde CONTRL V4.1 - Live Terminal Mirror [KB11:]" in out
    assert "TERMINAL FROZEN BY CLYDE INTRUDER LOCK" in out
    assert "[CAUDIT Summary: Sessions=5 | Total Cmds=553 | High-Risk=1 | Locked=1]" in out
    assert "[Clyde LOCK: Terminal KB11: released]" in out


def test_clyde_add_save_and_load(tmp_path):
    res = run_clyde(
        [
            "SAMPLE",
            "ADD KB15:, ENG-USR, TECO, 88",
            "SAVE TESTAUD.DAT",
            "CLEAR",
            "LOAD TESTAUD.DAT",
            "SHOW",
            "EXIT",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[6 Clyde audit records saved to TESTAUD.DAT]" in out
    assert "[6 Clyde audit records loaded from TESTAUD.DAT]" in out
    assert "Sessions: 6" in out
