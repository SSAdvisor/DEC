"""Test suite for Interleaf TPS 4.0 Technical Publishing Software (Interleaf, Inc.)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "interleaf"
ALIAS_TPS = APP_DIR / "bin" / "tps"


def run_interleaf(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_interleaf_binary_and_alias_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_TPS.exists() and os.access(ALIAS_TPS, os.X_OK)


def test_interleaf_sample_desktop_props_frame_paginate_and_lppost(tmp_path: Path):
    res = run_interleaf("SAMPLE; DESKTOP; PROPS; FRAME; PAGINATE; LPPOST; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample Interleaf TPS 4.0 book container loaded - 4 components]" in out
    assert "[Desktop Catalog: 4 documents in Book | Total Composed Pages: 66]" in out
    assert "[Property Sheet Verified for 4 active component tags]" in out
    assert "[Micro-Document Frame Check Complete: 2 vector graphics frames validated]" in out
    assert "[Book Pagination Complete: 4 chapters composed across 66 pages | TOC updated]" in out
    assert "[LPPOST Spooler Complete: 66 PostScript pages emitted to ILEAF_OUT.PS]" in out


def test_interleaf_add_save_and_load(tmp_path: Path):
    res1 = run_interleaf("SAMPLE; ADD CH-05, APPENDIX, VAXBI Bus Pinout Tables, 14; SAVE mybook.doc; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_interleaf("CLEAR; LOAD mybook.doc; PAGINATE; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 Interleaf TPS components loaded from mybook.doc]" in res2.stdout
    assert "[Book Pagination Complete: 5 chapters composed across 80 pages | TOC updated]" in res2.stdout
