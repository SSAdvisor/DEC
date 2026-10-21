import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "datatrieve11.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "datatrieve11.obj")
EXE_FILE = os.path.join(BIN_DIR, "datatrieve11")
DTR_LINK = os.path.join(BIN_DIR, "dtr")
DTR11_LINK = os.path.join(BIN_DIR, "dtr11")

def test_dtr_build():
    """Verify that datatrieve11.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE), f"Object file {OBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(DTR_LINK), f"Symlink {DTR_LINK} not found"
    assert os.path.islink(DTR11_LINK), f"Symlink {DTR11_LINK} not found"

def test_dtr_help():
    """Verify HELP command displays DATATRIEVE-11 commands."""
    res = subprocess.run([EXE_FILE, "HELP"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DATATRIEVE-11 Query & Data Management Commands" in res.stdout
    assert "READY" in res.stdout
    assert "FINISH" in res.stdout
    assert "FIND" in res.stdout
    assert "PRINT" in res.stdout
    assert "SELECT" in res.stdout
    assert "SORT" in res.stdout
    assert "STORE" in res.stdout
    assert "MODIFY" in res.stdout
    assert "ERASE" in res.stdout
    assert "TOTAL" in res.stdout
    assert "REPORT" in res.stdout
    assert "PLOT" in res.stdout
    assert "EXPORT" in res.stdout
    assert "IMPORT" in res.stdout
    assert "SHOW" in res.stdout

def test_dtr_banner_repl():
    """Verify interactive REPL displays DATATRIEVE-11 banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "DATATRIEVE-11 V3.0 - Query, Report & Data Management System" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / RSX-11M / RSTS/E" in out
    assert "DTR>" in out

def test_dtr_ready_yachts_sample(tmp_path):
    """Verify READY YACHTS automatically initializes sample schema and 8 records."""
    res = subprocess.run([EXE_FILE, "READY YACHTS; FINISH; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Domain YACHTS readied - 8 records available]" in res.stdout
    assert "[Domain YACHTS finished]" in res.stdout

    sch_file = tmp_path / "YACHTS.sch"
    dat_file = tmp_path / "YACHTS.dat"
    assert sch_file.is_file()
    assert dat_file.is_file()

    lines = dat_file.read_text().splitlines()
    assert len(lines) == 8
    assert "ALBERG|37|SLOOP|37|10|36000" in lines[0]

def test_dtr_print_all(tmp_path):
    """Verify PRINT ALL produces tabular display with headers and record count."""
    res = subprocess.run([EXE_FILE, "READY YACHTS; PRINT ALL; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "MANUFACTURER    MODEL     RIG       LENGTH  BEAM    PRICE" in res.stdout
    assert "ALBERG" in res.stdout
    assert "CAPE DORY" in res.stdout
    assert "VALIANT" in res.stdout
    assert "SWAN" in res.stdout
    assert "[8 of 8 record(s) displayed]" in res.stdout

def test_dtr_print_first(tmp_path):
    """Verify PRINT FIRST n restricts displayed rows."""
    res = subprocess.run([EXE_FILE, "READY YACHTS; PRINT FIRST 3; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[3 of 8 record(s) displayed]" in res.stdout
    assert "ALBERG" in res.stdout
    assert "CAPE DORY" in res.stdout
    assert "PEARSON" in res.stdout

def test_dtr_find(tmp_path):
    """Verify FIND with relational conditions."""
    cmds = (
        "READY YACHTS; "
        "FIND WITH PRICE < 50000; "
        "PRINT ALL; "
        "FIND WITH RIG = SLOOP; "
        "PRINT ALL; "
        "FIND WITH MANUFACTURER CONTAINING DORY; "
        "PRINT ALL; "
        "EXIT"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[6 record(s) found in collection]" in res.stdout
    assert "[1 record(s) found in collection]" in res.stdout
    assert "CAPE DORY" in res.stdout

def test_dtr_select(tmp_path):
    """Verify SELECT individual record and view field breakdown."""
    res = subprocess.run([EXE_FILE, "READY YACHTS; SELECT 1; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Record 1 selected:" in res.stdout
    assert "MANUFACTURER  : ALBERG" in res.stdout
    assert "PRICE         : 36000" in res.stdout

def test_dtr_sort(tmp_path):
    """Verify SORT BY field ASC and DESC."""
    res_desc = subprocess.run([EXE_FILE, "READY YACHTS; SORT BY PRICE DESC; PRINT ALL; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res_desc.returncode == 0, f"Execution failed:\n{res_desc.stdout}\n{res_desc.stderr}"
    assert "[Collection sorted by PRICE (D)]" in res_desc.stdout

    # In descending order, Swan (165000) should appear before Cape Dory (24500)
    swan_pos = res_desc.stdout.find("SWAN")
    cape_pos = res_desc.stdout.find("CAPE DORY")
    assert swan_pos != -1 and cape_pos != -1 and swan_pos < cape_pos

    res_asc = subprocess.run([EXE_FILE, "READY YACHTS; SORT BY PRICE ASC; PRINT ALL; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res_asc.returncode == 0, f"Execution failed:\n{res_asc.stdout}\n{res_asc.stderr}"
    assert "[Collection sorted by PRICE (A)]" in res_asc.stdout

    swan_pos_asc = res_asc.stdout.find("SWAN")
    cape_pos_asc = res_asc.stdout.find("CAPE DORY")
    assert cape_pos_asc < swan_pos_asc

def test_dtr_total(tmp_path):
    """Verify TOTAL/STATS summary calculations."""
    res = subprocess.run([EXE_FILE, "READY YACHTS; TOTAL PRICE; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Statistics for YACHTS.PRICE (8 records):" in res.stdout
    assert "Count:    8" in res.stdout
    assert "Total:    464500" in res.stdout
    assert "Average:  58062.5" in res.stdout
    assert "Minimum:  24500" in res.stdout
    assert "Maximum:  165000" in res.stdout

def test_dtr_report(tmp_path):
    """Verify REPORT generation to screen and to file."""
    rep_file = tmp_path / "yacht_rep.txt"
    cmds = f"READY YACHTS; FIND WITH PRICE < 50000; REPORT ON {rep_file}; EXIT"
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DEC DATATRIEVE-11 REPORT: YACHTS" in res.stdout
    assert "[Report written to " in res.stdout
    assert rep_file.is_file()

    content = rep_file.read_text()
    assert "DEC DATATRIEVE-11 REPORT: YACHTS" in content
    assert "TOTALS:" in content
    assert "[6 Records Processed]" in content

def test_dtr_plot(tmp_path):
    """Verify PLOT produces horizontal ASCII bar charts."""
    res = subprocess.run([EXE_FILE, "READY YACHTS; PLOT LENGTH; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DATATRIEVE PLOT: LENGTH by MANUFACTURER" in res.stdout
    assert "ALBERG" in res.stdout
    assert "****" in res.stdout

def test_dtr_modify_and_erase(tmp_path):
    """Verify MODIFY field value and ERASE records."""
    cmds = (
        "READY YACHTS; "
        "FIND WITH MANUFACTURER = ALBERG; "
        "MODIFY PRICE = 99999; "
        "PRINT ALL; "
        "FIND WITH RIG = KETCH; "
        "ERASE; "
        "PRINT ALL; "
        "EXIT"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[1 record(s) modified in YACHTS]" in res.stdout
    assert "99999" in res.stdout
    assert "[1 record(s) erased from YACHTS]" in res.stdout

def test_dtr_export_import(tmp_path):
    """Verify EXPORT and IMPORT round trip."""
    exp_file = tmp_path / "export.dat"
    cmds = (
        f"READY YACHTS; "
        f"FIND WITH PRICE < 40000; "
        f"EXPORT {exp_file}; "
        f"DEFINE DOMAIN BACKUP; "
        f"IMPORT {exp_file}; "
        f"PRINT ALL; "
        f"EXIT"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[4 record(s) exported to {exp_file}]" in res.stdout
    assert "[Import complete - domain now has 4 records]" in res.stdout
    assert exp_file.is_file()

def test_dtr_show(tmp_path):
    """Verify SHOW DOMAINS, SHOW RECORDS, SHOW collections."""
    cmds = "READY YACHTS; SHOW DOMAINS; SHOW RECORDS; SHOW COLLECTIONS; EXIT"
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Available DATATRIEVE Domains:" in res.stdout
    assert "Record structure for domain YACHTS:" in res.stdout
    assert "MANUFACTURER    Char  14" in res.stdout
    assert "PRICE           Num   8" in res.stdout
    assert "Current collection contains 8 of 8 records in YACHTS" in res.stdout

def test_dtr_symlinks(tmp_path):
    """Verify dtr and dtr11 symlinks execute correctly."""
    res1 = subprocess.run([DTR_LINK, "READY YACHTS; PRINT FIRST 1; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "ALBERG" in res1.stdout

    res2 = subprocess.run([DTR11_LINK, "READY YACHTS; PRINT FIRST 1; EXIT"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "ALBERG" in res2.stdout
