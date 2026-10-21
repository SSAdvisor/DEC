import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "indent.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "indent.obj")
EXE_FILE = os.path.join(BIN_DIR, "indent")
BP2FMT_LINK = os.path.join(BIN_DIR, "bp2fmt")
PRETTY_LINK = os.path.join(BIN_DIR, "pretty")


def test_indent_build():
    """Verify that indent.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE), f"Object file {OBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(BP2FMT_LINK), f"Symlink {BP2FMT_LINK} not found"
    assert os.path.islink(PRETTY_LINK), f"Symlink {PRETTY_LINK} not found"


def test_indent_banner_repl():
    """Verify interactive REPL displays INDENT banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "INDENT V2.0 - DEC BASIC-PLUS-2 Source Formatter & Structure Analyzer" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / RSX-11M / VAX" in out
    assert "INDENT>" in out


def test_indent_help():
    """Verify HELP command displays INDENT commands."""
    res = subprocess.run([EXE_FILE, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "INDENT BASIC-PLUS-2 Source Formatter & Analyzer Commands" in res.stdout
    assert "SAMPLE" in res.stdout
    assert "FORMAT" in res.stdout
    assert "CHECK" in res.stdout
    assert "XREF" in res.stdout
    assert "STEP" in res.stdout
    assert "MARGIN" in res.stdout
    assert "CASE" in res.stdout


def test_indent_sample_and_show():
    """Verify SAMPLE loads DEC sample program and SHOW displays status."""
    res = subprocess.run([EXE_FILE, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Sample BASIC-PLUS-2 program PAYROLL.BAS loaded - 15 source lines]" in res.stdout
    assert "INDENT System Status:" in res.stdout
    assert "Active File:     PAYROLL.BAS" in res.stdout
    assert "Buffer Lines:    15" in res.stdout
    assert "Indent Step:     4 spaces" in res.stdout
    assert "Base Margin:     2 spaces" in res.stdout
    assert "Case Mode:       UPPER" in res.stdout


def test_indent_raw_addline_delline():
    """Verify RAW listing, ADDLINE, and DELLINE buffer editing."""
    cmd = 'SAMPLE; ADDLINE "160 END"; RAW; DELLINE 16; SHOW; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Line #16 added to source buffer: 160 END]" in res.stdout
    assert "16  : 160 END" in res.stdout
    assert "[Deleted buffer line #16: 160 END]" in res.stdout
    assert "Buffer Lines:    15" in res.stdout


def test_indent_format_and_case_modes():
    """Verify FORMAT pretty-printing in UPPER and ASIS case modes and custom STEP/MARGIN."""
    cmd = "SAMPLE; FORMAT; STEP 2; MARGIN 1; CASE ASIS; FORMAT; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "40          FOR I% = 1% TO EMP_CNT%" in res.stdout
    assert "70                  RATE = 18.50" in res.stdout
    assert "[Indentation step width set to 2 spaces per nesting level]" in res.stdout
    assert "[Base left margin set to 1 spaces]" in res.stdout
    assert "[Keyword/statement casing mode set to ASIS]" in res.stdout
    assert "40       for i% = 1% to emp_cnt%" in res.stdout


def test_indent_check_balanced_and_unbalanced():
    """Verify CHECK structural audit passes on balanced code and detects unclosed blocks."""
    cmd = 'SAMPLE; CHECK; ADDLINE "160 FOR K% = 1% TO 5%"; CHECK; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Audit PASSED: All BASIC-PLUS-2 block structures are balanced]" in res.stdout
    assert "Maximum Nesting Depth:  3" in res.stdout
    assert "[ERROR] 1 unclosed block structure(s) at end of file" in res.stdout
    assert "[Audit FAILED: 1 structural nesting error(s) detected]" in res.stdout


def test_indent_check_unmatched_closer():
    """Verify CHECK detects unmatched NEXT/END SUB closer."""
    cmd = 'CLEAR; ADDLINE "10 NEXT I%"; CHECK; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[ERROR] Unmatched block closer on line 10: NEXT I%" in res.stdout
    assert "[Audit FAILED: 1 structural nesting error(s) detected]" in res.stdout


def test_indent_xref_table():
    """Verify XREF control-flow and nesting cross-reference table."""
    res = subprocess.run([EXE_FILE, "SAMPLE; XREF; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "INDENT Control-Flow & Nesting Cross-Reference - File: PAYROLL.BAS" in res.stdout
    assert "SUB-OPEN" in res.stdout
    assert "LOOP-OPEN" in res.stdout
    assert "SEL-OPEN" in res.stdout
    assert "SEL-CASE" in res.stdout
    assert "BRANCH" in res.stdout
    assert "150" in res.stdout
    assert "15 line(s) analyzed in PAYROLL.BAS" in res.stdout


def test_indent_export_formatted_file(tmp_path):
    """Verify exporting formatted BASIC-PLUS-2 code via PRINT ON / EXPORT."""
    out_file = str(tmp_path / "formatted.bas")
    cmd = f"SAMPLE; PRINT ON {out_file}; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[Formatted BASIC-PLUS-2 source written to {out_file} (15 lines)]" in res.stdout

    assert os.path.isfile(out_file)
    with open(out_file) as f:
        content = f.read()
    assert "20      SUB CALC_PAYROLL(EMP_CNT%, TOT_PAY)" in content
    assert "70                  RATE = 18.50" in content
    assert "140     END SUB" in content


def test_indent_save_and_load(tmp_path):
    """Verify saving and loading raw .BAS source files."""
    bas_path = str(tmp_path / "test_prog.bas")
    cmd = f"SAMPLE; SAVE {bas_path}; CLEAR; SHOW; LOAD {bas_path}; CHECK; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[15 raw source line(s) saved to {bas_path}]" in res.stdout
    assert "[INDENT source buffer cleared]" in res.stdout
    assert f"[15 source line(s) loaded from {bas_path}]" in res.stdout
    assert "[Audit PASSED: All BASIC-PLUS-2 block structures are balanced]" in res.stdout


def test_indent_symlinks():
    """Verify bp2fmt and pretty symlinks execute properly."""
    for link in [BP2FMT_LINK, PRETTY_LINK]:
        res = subprocess.run([link, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
        assert res.returncode == 0
        assert "INDENT System Status:" in res.stdout


def test_indent_parameter_validation():
    """Verify validation errors for out-of-range STEP, MARGIN, and CASE arguments."""
    cmd = "STEP 99; MARGIN 50; CASE INVALID; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "INDENT: Step width must be between 1 and 8 spaces" in res.stdout
    assert "INDENT: Base margin must be between 0 and 12 spaces" in res.stdout
    assert "INDENT: Syntax is CASE UPPER or CASE ASIS" in res.stdout


def test_indent_error_handling():
    """Verify error messages for empty buffer, out-of-range line deletion, and unknown commands."""
    res1 = subprocess.run([EXE_FILE, "CLEAR; FORMAT; EXIT"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "INDENT: Source buffer is empty" in res1.stdout

    res2 = subprocess.run([EXE_FILE, "SAMPLE; DELLINE 99; EXIT"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "INDENT: Buffer line number out of range" in res2.stdout

    res3 = subprocess.run([EXE_FILE, "UNKNOWN_CMD; EXIT"], capture_output=True, text=True, timeout=10)
    assert res3.returncode == 0
    assert "INDENT: Unknown command 'UNKNOWN_CMD'" in res3.stdout
