import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "decword.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
BOBJ_FILE = os.path.join(BUILD_DIR, "decword.bobj")
EXE_FILE = os.path.join(BIN_DIR, "decword")
DECWORDDP_LINK = os.path.join(BIN_DIR, "decworddp")
WPS_LINK = os.path.join(BIN_DIR, "wps")


def test_decword_build():
    """Verify that decword.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(BOBJ_FILE), f"Object file {BOBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(DECWORDDP_LINK), f"Symlink {DECWORDDP_LINK} not found"
    assert os.path.islink(WPS_LINK), f"Symlink {WPS_LINK} not found"


def test_decword_banner_repl():
    """Verify interactive REPL displays DECword/DP banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "DECword/DP V3.0 - Word & Data Processing System" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11" in out
    assert "WP>" in out


def test_decword_help():
    """Verify HELP command displays DECword/DP commands."""
    res = subprocess.run([EXE_FILE, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DECword/DP Word & Data Processing Commands" in res.stdout
    assert "DIR" in res.stdout
    assert "SELECT" in res.stdout
    assert "CREATE" in res.stdout
    assert "APPEND" in res.stdout
    assert "REPLACE" in res.stdout
    assert "RULER" in res.stdout
    assert "FORMAT" in res.stdout
    assert "DPLIST" in res.stdout
    assert "MERGE" in res.stdout
    assert "STATS" in res.stdout


def test_decword_sample_and_show():
    """Verify SAMPLE loads DEC historical documents & DP records and SHOW displays status."""
    res = subprocess.run([EXE_FILE, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Sample DECword/DP library loaded - 4 documents, 3 DP records]" in res.stdout
    assert "DECword/DP System Status:" in res.stdout
    assert "Active Document: #1 (4 lines)" in res.stdout
    assert "Total Documents: 4 (Deleted: 1)" in res.stdout
    assert "DP List Records: 3" in res.stdout
    assert "Ruler Margins:   LM=5 RM=72 Spacing=1" in res.stdout


def test_decword_dir_and_categories():
    """Verify document library directory listing and category filtering."""
    cmd = "SAMPLE; DIR; DIR LIBRARY; DIR FINAL; DIR WASTEBASKET; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DECword/DP Document Library - Category: ALL" in res.stdout
    assert "PDP-11/70 RSTS/E V8.0 Product Overview" in res.stdout
    assert "DECword/DP Document Library - Category: LIBRARY" in res.stdout
    assert "DECword/DP Document Library - Category: FINAL" in res.stdout
    assert "DECword/DP Customer Form Letter" in res.stdout
    assert "DECword/DP Document Library - Category: WASTEBASKET" in res.stdout
    assert "Preliminary WPS-8 Obsolete Draft" in res.stdout


def test_decword_select_and_read():
    """Verify selecting and reading documents with numbered lines."""
    cmd = "SAMPLE; SELECT 3; READ; READ 1; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Active document set to #3: Maynard Mill Engineering Memo (3 lines)]" in res.stdout
    assert "Document #3: Maynard Mill Engineering Memo" in res.stdout
    assert "Author:   G.BELL" in res.stdout
    assert "MEMORANDUM: VAX-11/780 & PDP-11 Interconnect" in res.stdout
    assert "Document #1: PDP-11/70 RSTS/E V8.0 Product Overview" in res.stdout
    assert "processing for 63 users on VT100 and LQP02." in res.stdout


def test_decword_create_append_delline():
    """Verify creating a document, appending lines, and deleting a line."""
    cmd = (
        'SAMPLE; CREATE "VAX-11 Technical Note", "D.CUTLER", "DRAFT"; '
        'APPEND "Line One~Line Two~Line Three"; READ; DELLINE 2; READ; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Document #5 created: VAX-11 Technical Note]" in res.stdout
    assert "[Appended to Document #5 (3 lines)]" in res.stdout
    assert "[Line 2 deleted from Document #5]" in res.stdout
    assert "1  : Line One" in res.stdout
    assert "2  : Line Three" in res.stdout


def test_decword_replace_and_find():
    """Verify searching and replacing text within the active document."""
    cmd = (
        'SAMPLE; SELECT 1; FIND "PDP-11/70"; '
        'REPLACE "PDP-11/70", "PDP-11/70-MP"; READ 1; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Search results for 'PDP-11/70' in Document #1:" in res.stdout
    assert "[Found 2 matching line(s)]" in res.stdout
    assert "[Replaced 2 occurrence(s) in Document #1]" in res.stdout
    assert "PDP-11/70-MP RSTS/E V8.0 SPECIFICATION" in res.stdout


def test_decword_ruler_header_footer_format():
    """Verify RULER, HEADER, FOOTER, and FORMAT rendering."""
    cmd = (
        'SAMPLE; RULER 8, 70, 2; HEADER "DEC ENGINEERING STANDARD"; '
        'FOOTER "MAYNARD MILL ARCHIVE"; FORMAT 3; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DECword/DP Ruler Settings: LM=8 RM=70 Spacing=2 PageLen=55" in res.stdout
    assert "....L....T....1....T....2" in res.stdout
    assert "[Document header set to: DEC ENGINEERING STANDARD]" in res.stdout
    assert "[Document footer set to: MAYNARD MILL ARCHIVE]" in res.stdout
    assert "        DEC ENGINEERING STANDARD" in res.stdout
    assert "        MAYNARD MILL ARCHIVE - Page 1" in res.stdout


def test_decword_print_on_and_export_file(tmp_path):
    """Verify formatting documents to external files via PRINT ON and EXPORT."""
    f1 = str(tmp_path / "doc1_print.txt")
    f2 = str(tmp_path / "doc3_export.txt")
    cmd = f"SAMPLE; PRINT ON {f1}; SELECT 3; EXPORT {f2}; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[Document #1 formatted to {f1}]" in res.stdout
    assert f"[Document #3 formatted to {f2}]" in res.stdout

    assert os.path.isfile(f1)
    with open(f1) as fp:
        c1 = fp.read()
    assert "PDP-11/70 RSTS/E V8.0 SPECIFICATION" in c1
    assert "Digital Equipment Corporation - Page 1" in c1

    assert os.path.isfile(f2)
    with open(f2) as fp:
        c2 = fp.read()
    assert "MEMORANDUM: VAX-11/780 & PDP-11 Interconnect" in c2


def test_decword_dplist_dpadd_and_merge():
    """Verify Data Processing (DP) list management and Mail-Merge (LISTPROC / MERGE)."""
    cmd = (
        'SAMPLE; DPADD "Dr. Grace Hopper", "US Navy Dept", "DECSYSTEM-20"; '
        'DPLIST; MERGE 2; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[DP Record #4 added: Dr. Grace Hopper (US Navy Dept)]" in res.stdout
    assert "4 DP list record(s) available for MERGE" in res.stdout
    assert "[DECword/DP List Processing Merge - Record #1 of 4]" in res.stdout
    assert "Dear Dr. Harlan Anderson," in res.stdout
    assert "Thank you for selecting the PDP-11/70 system for MIT Lincoln Laboratory." in res.stdout
    assert "Dear Dr. Grace Hopper," in res.stdout
    assert "Thank you for selecting the DECSYSTEM-20 system for US Navy Dept." in res.stdout
    assert "[List Processing complete: 4 merged documents generated]" in res.stdout


def test_decword_stats_copy_delete_purge():
    """Verify STATS, COPY, DELETE, and PURGE operations."""
    cmd = "SAMPLE; SELECT 2; STATS; COPY 2; DELETE 1; PURGE; SHOW; DIR; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DECword/DP Document Statistics:" in res.stdout
    assert "Lines:          5" in res.stdout
    assert "DP Merge Lines: 2" in res.stdout
    assert "[Document #2 copied to Document #5]" in res.stdout
    assert "[Document #1 marked deleted (moved to WASTEBASKET)]" in res.stdout
    assert "[Library purged - 2 deleted documents removed]" in res.stdout
    assert "Total Documents: 3 (Deleted: 0)" in res.stdout
    assert "Copy of DECword/DP Customer Form Letter" in res.stdout


def test_decword_save_and_load(tmp_path):
    """Verify saving and loading the DECword/DP document library."""
    lib_file = str(tmp_path / "decword_lib.dat")
    cmd = f"SAMPLE; SAVE {lib_file}; CLEAR; SHOW; LOAD {lib_file}; DIR; READ 1; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[4 documents saved to {lib_file}]" in res.stdout
    assert "[DECword/DP library cleared]" in res.stdout
    assert f"[4 documents loaded from {lib_file}]" in res.stdout
    assert "PDP-11/70 RSTS/E V8.0 Product Overview" in res.stdout
    assert "processing for 63 users on VT100 and LQP02." in res.stdout


def test_decword_symlinks_and_errors():
    """Verify decworddp and wps symlinks and error handling."""
    res_dp = subprocess.run([DECWORDDP_LINK, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_dp.returncode == 0
    assert "Total Documents: 4" in res_dp.stdout

    res_wps = subprocess.run([WPS_LINK, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_wps.returncode == 0
    assert "DECword/DP Word & Data Processing Commands" in res_wps.stdout

    res_err1 = subprocess.run([EXE_FILE, "CLEAR; READ; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_err1.returncode == 0
    assert "DECword/DP: No documents in library" in res_err1.stdout

    res_err2 = subprocess.run([EXE_FILE, "SAMPLE; READ 99; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_err2.returncode == 0
    assert "DECword/DP: Document number out of range" in res_err2.stdout

    res_err3 = subprocess.run([EXE_FILE, "UNKNOWN_CMD; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_err3.returncode == 0
    assert "DECword/DP: Unknown command 'UNKNOWN_CMD'" in res_err3.stdout
