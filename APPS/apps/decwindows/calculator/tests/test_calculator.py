import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_CALC = APP_DIR / "bin" / "calculator"
BIN_DXCALC = APP_DIR / "bin" / "dxcalc"


def run_calc(commands: str, binary: Path = BIN_CALC, cwd: Path = APP_DIR) -> str:
    proc = subprocess.run(
        [str(binary)],
        input=commands + "\n",
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )
    assert proc.returncode == 0, f"calculator failed: {proc.stderr}"
    return proc.stdout


def test_01_banner_and_help():
    out = run_calc("HELP\nEXIT")
    assert "DECwindows Calculator V3.0 (DECW$CALC / dxcalc)" in out
    assert "--- DECwindows Calculator V3.0 Commands ---" in out
    assert "PMT <principal|rate%|years>" in out
    assert "DECwindows Calculator V3.0 session terminated." in out


def test_02_sample_and_show_status():
    out = run_calc("SAMPLE; SHOW; EXIT")
    assert "[Loaded Sample DECwindows Calculator Tape: 6 operations, ACC = 3840, MEM = 4096]" in out
    assert "Keypad Mode    : SCIENTIFIC  |  Active Base: DEC" in out
    assert "Accumulator    : 3840 (DEC)  |  0xF00 (HEX)  |  0o7400 (OCT)" in out
    assert "Memory Reg (M) : 4096" in out
    assert "Tape Entries   : 6 operations" in out


def test_03_basic_arithmetic_and_divzero():
    out = run_calc("SET 100; ADD 50; SUB 30; MUL 4; DIV 6; DIV 0; MOD 15; EXIT")
    assert "Display [DEC]: 150" in out
    assert "Display [DEC]: 120" in out
    assert "Display [DEC]: 480" in out
    assert "Display [DEC]: 80" in out
    assert "%CALC-E-DIVZERO, Division by zero error." in out
    assert "Display [DEC]: 5" in out


def test_04_scientific_sqrt_and_sqr():
    out = run_calc("SET 12; SQR; SQRT; EXIT")
    assert "Display [DEC]: 144 (0x90 | 0o220)" in out
    assert "Display [DEC]: 12 (0xC | 0o14)" in out


def test_05_programmer_bitwise_operations():
    out = run_calc("SET 240; AND 170; OR 15; XOR 255; EXIT")
    # 240 (0xF0) AND 170 (0xAA) = 160 (0xA0)
    assert "Display [DEC]: 160 (0xA0 | 0o240)" in out
    # 160 (0xA0) OR 15 (0x0F) = 175 (0xAF)
    assert "Display [DEC]: 175 (0xAF | 0o257)" in out
    # 175 (0xAF) XOR 255 (0xFF) = 80 (0x50)
    assert "Display [DEC]: 80 (0x50 | 0o120)" in out


def test_06_memory_register_operations():
    out = run_calc("SET 500; STO; M+; SET 100; M-; RCL; MC; SHOW; EXIT")
    assert "[Stored 500 into Memory Register M]" in out
    assert "[Memory M+ : M = 1000]" in out
    assert "[Memory M- : M = 900]" in out
    assert "Display [DEC]: 900" in out
    assert "[Memory Register M cleared]" in out
    assert "Memory Reg (M) : 0" in out


def test_07_radix_base_and_mode_switching():
    out = run_calc("SET 255; MODE PROGRAMMER; BASE HEX; BASE OCT; EXIT")
    assert "[Calculator Keypad Mode set to: PROGRAMMER]" in out
    assert "[Radix Base: HEX | DEC=255 HEX=0xFF OCT=0o377]" in out
    assert "[Radix Base: OCT | DEC=255 HEX=0xFF OCT=0o377]" in out


def test_08_financial_pmt_loan_calculation():
    out = run_calc("MODE FINANCIAL; PMT 12000|10|4; SHOW; EXIT")
    assert "=== Financial Loan Analysis ===" in out
    assert "Principal: 12000 | Rate: 10% | Term: 4 yrs | Annual Pmt: 4200 (Monthly ~350)" in out
    assert "Accumulator    : 4200 (DEC)" in out


def test_09_audit_paper_tape_listing():
    out = run_calc("SAMPLE; TAPE; EXIT")
    assert "=== DECwindows Calculator Paper Audit Tape ===" in out
    assert "SET 1024" in out
    assert "0x400" in out
    assert "0o2000" in out
    assert "Total tape entries: 6" in out


def test_10_display_and_export_motif_window(tmp_path):
    win_file = tmp_path / "calc_win.txt"
    out = run_calc(f"SAMPLE; DISPLAY; EXPORT {win_file}; EXIT")
    assert "| [=] DECwindows Calculator (dxcalc) - SCIENTIFIC [DEC]                     [v][^] |" in out
    assert "|  [ MC ]  [ MR ]  [ M+ ]  [ M- ]  [ MS ]   |   [SQRT]  [SQR ]  [MOD ] [PMT] |" in out
    assert f"[Calculator window exported to {win_file}]" in out
    assert win_file.exists()
    content = win_file.read_text()
    assert "LCD: 3840 | HEX: 0xF00 | OCT: 0o7400 | M=4096" in content


def test_11_save_clear_and_load_persistence(tmp_path):
    tape_file = tmp_path / "calc_state.tap"
    out = run_calc(f"SAMPLE; SAVE {tape_file}; CLEAR; SHOW; LOAD {tape_file}; SHOW; EXIT")
    assert f"[Saved 6 tape entries to {tape_file}]" in out
    assert "[Calculator accumulator, memory, and tape cleared]" in out
    assert f"[Loaded 6 tape entries from {tape_file} (ACC=3840, MEM=4096)]" in out
    assert "Tape Entries   : 6 operations" in out


def test_12_command_line_batch_mode():
    proc = subprocess.run(
        [str(BIN_CALC), "SAMPLE; SHOW; EXIT"],
        text=True,
        capture_output=True,
        cwd=str(APP_DIR),
        timeout=10,
    )
    assert proc.returncode == 0
    assert "Accumulator    : 3840 (DEC)" in proc.stdout


def test_13_error_handling_invalid_command():
    out = run_calc("FOOBAR; PMT 1000; EXIT")
    assert "%CALC-E-INVCMD, Unrecognized command: FOOBAR" in out
    assert "%CALC-E-SYNTAX, Usage: PMT <principal|rate_pct|years>" in out


def test_14_dxcalc_symlink_execution():
    assert BIN_DXCALC.exists() and os.access(BIN_DXCALC, os.X_OK)
    out = run_calc("SAMPLE; TAPE; EXIT", binary=BIN_DXCALC)
    assert "DECwindows Calculator V3.0" in out
    assert "Total tape entries: 6" in out
