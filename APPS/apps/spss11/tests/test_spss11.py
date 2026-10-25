import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "spss11"
SPSS_ALIAS = APP_DIR / "bin" / "spss"


def run_spss11(commands: list[str], cwd: Path) -> subprocess.CompletedProcess:
    input_text = "\n".join(commands) + "\n"
    return subprocess.run(
        [str(BIN_PATH)],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )


def test_spss11_binaries_exist():
    assert BIN_PATH.exists()
    assert SPSS_ALIAS.exists()


def test_spss11_statistical_procedures(tmp_path):
    res = run_spss11(
        [
            "SAMPLE",
            "DATALIST",
            "FREQUENCIES",
            "CONDESCRIPTIVE",
            "CROSSTABS",
            "ANOVA",
            "PEARSON",
            "FINISH",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample SPSS-11 system file loaded - 6 cases (CASE_ID, GRP, SCORE, INCOME)]" in out
    assert "TOTAL VALID CASES = 6 | MISSING = 0" in out
    assert "SCORE      76      456     62     90     28" in out
    assert "CHI-SQUARE = 6.00 (DF = 1, p < 0.02)" in out
    assert "Group CTRL Mean = 65 (N=3) | Group EXP Mean = 87 (N=3) | Effect = +22" in out
    assert "Pearson r = +0.9962" in out


def test_spss11_add_save_and_load(tmp_path):
    res = run_spss11(
        [
            "SAMPLE",
            "ADD S-107, EXP, 92, 50",
            "SAVE TESTSPSS.DAT",
            "CLEAR",
            "LOAD TESTSPSS.DAT",
            "SHOW",
            "FINISH",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[7 SPSS-11 cases saved to TESTSPSS.DAT]" in out
    assert "[7 SPSS-11 cases loaded from TESTSPSS.DAT]" in out
    assert "Cases: 7" in out
