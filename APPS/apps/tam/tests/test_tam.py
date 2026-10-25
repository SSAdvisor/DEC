"""Test suite for EG&H TAM V3.2 Terminal Application Manager (RSTS/E)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "tam"


def run_tam(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_tam_binary_exists():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)


def test_tam_sample_paint_validate_and_monitor(tmp_path: Path):
    res = run_tam("SAMPLE; FIELDS; PAINT; VALIDATE; MONITOR TX_INVOICE; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample EG&H TAM screen definition (ORD_ENTRY) loaded - 4 VT100 fields]" in out
    assert "EG&H TAM VT100 SCREEN PAINTER" in out
    assert "[TAM Field-Attribute Validation PASSED: 4 fields verified, Buffer Size=40 bytes]" in out
    assert "[TAM Transaction Monitor: Dispatched TX_INVOICE on Screen ORD_ENTRY (Active TX #13" in out


def test_tam_add_save_and_load(tmp_path: Path):
    res1 = run_tam("SAMPLE; ADD SHIP_VIA, ALPHA, 8, 12; SAVE mytam.dat; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_tam("CLEAR; LOAD mytam.dat; VALIDATE; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 TAM field definitions loaded from mytam.dat]" in res2.stdout
    assert "Buffer Size=48 bytes" in res2.stdout
