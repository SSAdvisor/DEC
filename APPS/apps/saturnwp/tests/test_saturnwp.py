"""Test suite for Saturn Systems Saturn-WP V4.2 (RSTS/E Office Automation)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "saturnwp"
SWP_ALIAS = APP_DIR / "bin" / "swp"


def run_saturnwp(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_saturnwp_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert SWP_ALIAS.exists() and os.access(SWP_ALIAS, os.X_OK)


def test_saturnwp_sample_and_directory(tmp_path: Path):
    res = run_saturnwp("SAMPLE; DIR; STATS; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Saturn-WP library loaded - 4 documents, 3 Saturn-Base records, 3 Saturn-Calc rows]" in out
    assert "Saturn-WP Document Library (SATWP.DAT)" in out
    assert "Saturn Office Suite Executive Financial Report" in out
    assert "Saturn-Base Customer Renewal Letter" in out
    assert "Saturn-WP Document Statistics:" in out
    assert "Saturn-WP System Status:" in out


def test_saturnwp_calctable_calcset_and_embedcalc(tmp_path: Path):
    res = run_saturnwp(
        "SAMPLE; CALCTABLE; CALCSET 1, 200, 250; EMBEDCALC; READ 1; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "Saturn-Calc Live Worksheet Link (SCALC.WKS)" in out
    assert "[Saturn-Calc Row #1 updated: H1=200 H2=250]" in out
    assert "[Saturn-Calc table embedded into Document #1 (Total=1750K)]" in out
    assert "[SATURN-CALC EMBEDDED TABLE: H1=780K H2=970K TOTAL=1750K]" in out


def test_saturnwp_saturn_base_mail_merge(tmp_path: Path):
    res = run_saturnwp(
        "SAMPLE; BASEADD Jane Doe, Northstar Health, PDP-11/70 RSTS/E V9.6; BASELIST; SELECT 2; MERGE 2; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Saturn-Base Record #4 added: Jane Doe (Northstar Health)]" in out
    assert "[Saturn-Base Mail-Merge - Record #4 of 4]" in out
    assert "Dear Jane Doe," in out
    assert "[Saturn-Base Merge complete: 4 merged documents generated]" in out


def test_saturnwp_edit_format_save_and_load(tmp_path: Path):
    res1 = run_saturnwp(
        "SAMPLE; CREATE Q4 Forecast, R. Alan, FINANCE; APPEND Revenue up 22 percent.; EXPORT out.doc; SAVE mylib.dat; EXIT",
        tmp_path,
    )
    assert res1.returncode == 0
    assert (tmp_path / "out.doc").exists()
    assert "Revenue up 22 percent." in (tmp_path / "out.doc").read_text()

    res2 = run_saturnwp("CLEAR; LOAD mylib.dat; DIR FINANCE; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 documents loaded from mylib.dat]" in res2.stdout
    assert "Q4 Forecast" in res2.stdout
