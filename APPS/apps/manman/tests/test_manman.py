"""Test suite for ASK MANMAN V7.0 Manufacturing Management MRP II Suite (VAX/VMS)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "manman"
ALIAS_ASKMAN = APP_DIR / "bin" / "askman"


def run_manman(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_manman_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_ASKMAN.exists() and os.access(ALIAS_ASKMAN, os.X_OK)


def test_manman_sample_mrp_crp_omac_and_gl(tmp_path: Path):
    res = run_manman("SAMPLE; OMAR; MRP; CRP; OMAC; GL; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample ASK MANMAN V7.0 MRP II dataset loaded - 4 Item Master & BOM records]" in out
    assert "[MANMAN MRP Complete: 3 Planned Order Releases | Total POR Qty = 160 units]" in out
    assert "[MANMAN CRP Summary: Total Work Center Load = 132 Std Hrs across 4 routings]" in out
    assert "[ASK MANMAN/OMAC Customer Order Management: 4 active lines | Backlog Invoice Total = $98450]" in out
    assert "[ASK MANMAN/GL Standard Cost Rollup: Unit Cost Sum = $1160 | On-Hand Valuation = $53550]" in out


def test_manman_add_save_and_load(tmp_path: Path):
    res1 = run_manman("SAMPLE; ADD VAX-DSK9, RA90 SDI Disk, WC-ASM, 10, 50, 600; SAVE myman.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_manman("CLEAR; LOAD myman.dat; MRP; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 MANMAN Item Master records loaded from myman.dat]" in res2.stdout
    assert "[MANMAN MRP Complete: 4 Planned Order Releases | Total POR Qty = 200 units]" in res2.stdout
