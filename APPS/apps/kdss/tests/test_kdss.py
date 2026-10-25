"""Test suite for EG&H KDSS V4.0 Key-to-Disk Subsystem (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "kdss"
ALIAS_KDFMT = APP_DIR / "bin" / "kdfmt"
ALIAS_KDENT = APP_DIR / "bin" / "kdent"


def run_kdss(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_kdss_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_KDFMT.exists() and os.access(ALIAS_KDFMT, os.X_OK)
    assert ALIAS_KDENT.exists() and os.access(ALIAS_KDENT, os.X_OK)


def test_kdss_sample_kdfmt_kdver_and_stats(tmp_path: Path):
    res = run_kdss("SAMPLE; KDFMT; LIST; KDVER; STATS; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample EG&H KDSS Batch B-042 loaded - 4 key-to-disk records (Format: INV_80COL)]" in out
    assert "[Batch Hash Accumulator #1 = $3680 across 4 records]" in out
    assert "[KDVER Key-Verification & Modulus-10 Pass Complete: 4 of 4 records verified ('V'), Batch Hash=$3680]" in out
    assert "EG&H KDSS Operator Keystroke & Throughput Statistics" in out


def test_kdss_kdent_export_save_and_load(tmp_path: Path):
    res1 = run_kdss("SAMPLE; KDENT 41040, Apollo Computer, 520; KDVER; EXPORT tape.dat; SAVE mykd.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    assert (tmp_path / "tape.dat").exists()

    res2 = run_kdss("CLEAR; LOAD mykd.dat; LIST; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 KDSS batch records loaded from mykd.dat]" in res2.stdout
    assert "Apollo Computer" in res2.stdout
