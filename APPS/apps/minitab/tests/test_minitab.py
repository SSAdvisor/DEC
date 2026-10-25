import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "minitab"
MTAB_ALIAS = APP_DIR / "bin" / "mtab"


def run_minitab(commands: list[str], cwd: Path) -> subprocess.CompletedProcess:
    input_text = "\n".join(commands) + "\n"
    return subprocess.run(
        [str(BIN_PATH)],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )


def test_minitab_binaries_exist():
    assert BIN_PATH.exists()
    assert MTAB_ALIAS.exists()


def test_minitab_sample_describe_regress_and_ttest(tmp_path):
    res = run_minitab(
        [
            "SAMPLE",
            "PRINT",
            "DESCRIBE",
            "HISTOGRAM",
            "PLOT",
            "REGRESS",
            "TTEST",
            "STOP",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample MINITAB-11 worksheet loaded - 6 rows in C1:YIELD, C2:TEMP, C3:PRESS]" in out
    assert "C1:YIELD    6     85      510      72      96     24" in out
    assert "THE REGRESSION EQUATION IS: YIELD = 3 + (4/10) * TEMP" in out
    assert "ONE-SAMPLE T-TEST ON C1:YIELD (Test Mu = 75): N = 6 | Mean = 85 | Var = 79" in out


def test_minitab_add_save_and_load(tmp_path):
    res = run_minitab(
        [
            "SAMPLE",
            "ADD 99, 240, 55",
            "SAVE TESTMTAB.DAT",
            "CLEAR",
            "LOAD TESTMTAB.DAT",
            "SHOW",
            "STOP",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[7 MINITAB rows saved to TESTMTAB.DAT]" in out
    assert "[7 MINITAB rows loaded from TESTMTAB.DAT]" in out
    assert "Rows: 7" in out
