"""Test suite for Nyplan Inc. NYPLAN V4.1 (RSTS/E Corporate Financial Modeling)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "nyplan"
ALIAS_NYP = APP_DIR / "bin" / "nyp"


def run_nyplan(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_nyplan_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_NYP.exists() and os.access(ALIAS_NYP, os.X_OK)


def test_nyplan_sample_and_model_display(tmp_path: Path):
    res = run_nyplan("SAMPLE; MODEL; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample NYPLAN financial model loaded - 6 P&L accounts, Net Actual=620K, Forecast=682K]" in out
    assert "NYPLAN Corporate P&L & Budget Model (NYPLAN.DAT)" in out
    assert "Divisions Consolidated: 1 | Net Profit Variance: 120K | Forecast Net: 682K" in out
    assert "NYPLAN V4.1 Financial Modeling Status:" in out


def test_nyplan_whatif_and_montecarlo(tmp_path: Path):
    res = run_nyplan(
        "SAMPLE; WHATIF 20, 10; MONTECARLO 500; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "NYPLAN 'What-If' Sensitivity Analysis (Rev +20%, Cost +10%)" in out
    assert "What-If Scenario:  Gross Rev=2640K | Gross Margin=1705K | Net Profit=902K" in out
    assert "Net Profit Impact: 282K (vs. Baseline 620K)" in out
    assert "NYPLAN Monte Carlo Risk & Variance Simulation (500 Trials)" in out
    assert "Pessimistic (P10): $356K Net Operating Profit" in out
    assert "Expected Mean:     $669K Net Operating Profit" in out
    assert "Optimistic (P90):  $1016K Net Operating Profit" in out


def test_nyplan_set_and_consolidate(tmp_path: Path):
    res = run_nyplan(
        "SAMPLE; SET 1, 2100, 2400; CONSOLIDATE 25; EXIT",
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[NYPLAN Row #1 updated: Budget=2100K, Actual=2400K, Var=300K | Net Operating Inc=820K]" in out
    assert "[NYPLAN Multi-Division P&L Consolidation: Division #2 (+25%) -> Consolidated Rev=3000K, Net Profit=1026K]" in out


def test_nyplan_export_save_and_load(tmp_path: Path):
    res1 = run_nyplan(
        "SAMPLE; LABEL 7, Capital CapEx; SET 7, 150, 180; EXPORT pnl.txt; SAVE mynyp.dat; EXIT",
        tmp_path,
    )
    assert res1.returncode == 0
    assert (tmp_path / "pnl.txt").exists()
    assert "Capital CapEx" in (tmp_path / "pnl.txt").read_text()

    res2 = run_nyplan("CLEAR; LOAD mynyp.dat; MODEL; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[7 NYPLAN model rows loaded from mynyp.dat]" in res2.stdout
    assert "Capital CapEx" in res2.stdout
