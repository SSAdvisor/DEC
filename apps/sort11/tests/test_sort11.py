import os
import subprocess
import sqlite3
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "sort11.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "sort11.obj")
EXE_FILE = os.path.join(BIN_DIR, "sort11")

SAMPLE_RECS = [
    "3000 Delta",
    "1000 Alpha",
    "4000 Echo",
    "2000 Charlie",
    "5000 Bravo",
]

def test_sort11_build():
    """Verify that sort11.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE), f"Object file {OBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"

def test_sequential_numeric_sort_asc(tmp_path):
    """Test sequential sort with numeric key in ascending order."""
    in_file = tmp_path / "num_in.txt"
    out_file = tmp_path / "num_out_asc.txt"
    in_file.write_text("\n".join(SAMPLE_RECS) + "\n")

    cmd = f"{out_file}={in_file}/KEY:(POS:1,SIZ:4,ASC,NUM)"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Status:             SUCCESS" in res.stdout
    assert "Records Processed:  5" in res.stdout

    lines = [line.strip() for line in out_file.read_text().splitlines() if line.strip()]
    expected = [
        "1000 Alpha",
        "2000 Charlie",
        "3000 Delta",
        "4000 Echo",
        "5000 Bravo",
    ]
    assert lines == expected

def test_sequential_numeric_sort_desc(tmp_path):
    """Test sequential sort with numeric key in descending order."""
    in_file = tmp_path / "num_in.txt"
    out_file = tmp_path / "num_out_desc.txt"
    in_file.write_text("\n".join(SAMPLE_RECS) + "\n")

    cmd = f"{out_file}={in_file}/KEY:(POS:1,SIZ:4,DESC,NUM)"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "Status:             SUCCESS" in res.stdout

    lines = [line.strip() for line in out_file.read_text().splitlines() if line.strip()]
    expected = [
        "5000 Bravo",
        "4000 Echo",
        "3000 Delta",
        "2000 Charlie",
        "1000 Alpha",
    ]
    assert lines == expected

def test_sequential_char_sort(tmp_path):
    """Test sequential sort with character key (name field)."""
    in_file = tmp_path / "char_in.txt"
    out_asc = tmp_path / "char_out_asc.txt"
    out_desc = tmp_path / "char_out_desc.txt"
    in_file.write_text("\n".join(SAMPLE_RECS) + "\n")

    # Character Ascending
    cmd_asc = f"{out_asc}={in_file}/KEY:(POS:6,SIZ:10,ASC,CH)"
    res_asc = subprocess.run([EXE_FILE, cmd_asc], capture_output=True, text=True, timeout=10)
    assert res_asc.returncode == 0

    lines_asc = [line.strip() for line in out_asc.read_text().splitlines() if line.strip()]
    expected_asc = [
        "1000 Alpha",
        "5000 Bravo",
        "2000 Charlie",
        "3000 Delta",
        "4000 Echo",
    ]
    assert lines_asc == expected_asc

    # Character Descending
    cmd_desc = f"{out_desc}={in_file}/KEY:(POS:6,SIZ:10,DESC,CH)"
    res_desc = subprocess.run([EXE_FILE, cmd_desc], capture_output=True, text=True, timeout=10)
    assert res_desc.returncode == 0

    lines_desc = [line.strip() for line in out_desc.read_text().splitlines() if line.strip()]
    expected_desc = [
        "4000 Echo",
        "3000 Delta",
        "2000 Charlie",
        "5000 Bravo",
        "1000 Alpha",
    ]
    assert lines_desc == expected_desc

def test_seq_to_rms_indexed_conversion(tmp_path):
    """Test sorting sequential file into an SQLite-backed RMS indexed file (.IDX)."""
    in_file = tmp_path / "seq_in.txt"
    out_idx = tmp_path / "output.idx"
    in_file.write_text("\n".join(SAMPLE_RECS) + "\n")

    cmd = f"{out_idx}={in_file}/KEY:(POS:1,SIZ:4,ASC,NUM)/RMS"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "Output File:        " + str(out_idx) + " (RMS)" in res.stdout
    assert os.path.isfile(out_idx)

    # Verify SQLite schema and contents
    conn = sqlite3.connect(str(out_idx))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records';")
    assert cursor.fetchone() is not None, "RMS table 'records' not found in SQLite database"

    cursor.execute("SELECT key FROM records ORDER BY id ASC;")
    rows = [r[0].strip() for r in cursor.fetchall()]
    conn.close()

    expected = [
        "1000 Alpha",
        "2000 Charlie",
        "3000 Delta",
        "4000 Echo",
        "5000 Bravo",
    ]
    assert rows == expected

def test_rms_indexed_to_seq_conversion(tmp_path):
    """Test reading from an SQLite RMS indexed file and sorting into a sequential text file."""
    # First create an RMS indexed file
    in_file = tmp_path / "initial.txt"
    rms_file = tmp_path / "data.idx"
    out_seq = tmp_path / "sorted_from_rms.txt"
    in_file.write_text("\n".join(SAMPLE_RECS) + "\n")

    cmd1 = f"{rms_file}={in_file}/RMS"
    res1 = subprocess.run([EXE_FILE, cmd1], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0

    # Read from RMS indexed file and sort descending by character key
    cmd2 = f"{out_seq}={rms_file}/KEY:(POS:6,SIZ:10,DESC,CH)"
    res2 = subprocess.run([EXE_FILE, cmd2], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "Input File:         " + str(rms_file) + " (RMS)" in res2.stdout
    assert "Output File:        " + str(out_seq) + " (SEQ)" in res2.stdout

    lines = [line.strip() for line in out_seq.read_text().splitlines() if line.strip()]
    expected = [
        "4000 Echo",
        "3000 Delta",
        "2000 Charlie",
        "5000 Bravo",
        "1000 Alpha",
    ]
    assert lines == expected

def test_rms_to_rms_sort(tmp_path):
    """Test reading from an RMS indexed file and writing into a new RMS indexed file."""
    in_file = tmp_path / "init.txt"
    rms1 = tmp_path / "rms1.idx"
    rms2 = tmp_path / "rms2.idx"
    in_file.write_text("\n".join(SAMPLE_RECS) + "\n")

    # Step 1: Sequential to RMS
    subprocess.run([EXE_FILE, f"{rms1}={in_file}/RMS"], check=True, timeout=10)

    # Step 2: RMS to RMS (descending numeric)
    cmd = f"{rms2}={rms1}/KEY:(POS:1,SIZ:4,DESC,NUM)/RMS"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "Input File:         " + str(rms1) + " (RMS)" in res.stdout
    assert "Output File:        " + str(rms2) + " (RMS)" in res.stdout

    conn = sqlite3.connect(str(rms2))
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM records ORDER BY id ASC;")
    rows = [r[0].strip() for r in cursor.fetchall()]
    conn.close()

    expected = [
        "5000 Bravo",
        "4000 Echo",
        "3000 Delta",
        "2000 Charlie",
        "1000 Alpha",
    ]
    assert rows == expected

def test_positional_syntax(tmp_path):
    """Test positional CLI syntax: sort11 input output."""
    in_file = tmp_path / "pos_in.txt"
    out_file = tmp_path / "pos_out.txt"
    in_file.write_text("3000 Charlie\n1000 Bravo\n2000 Alpha\n")

    cmd = f"{in_file} {out_file}"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "Status:             SUCCESS" in res.stdout

    lines = [line.strip() for line in out_file.read_text().splitlines() if line.strip()]
    expected = [
        "1000 Bravo",
        "2000 Alpha",
        "3000 Charlie",
    ]
    assert lines == expected

def test_interactive_wizard(tmp_path):
    """Test interactive prompt wizard when invoked without arguments."""
    in_file = tmp_path / "wiz_in.txt"
    out_file = tmp_path / "wiz_out.txt"
    in_file.write_text("500 Beta\n100 Delta\n300 Gamma\n")

    # Input sequence:
    # Input file: in_file
    # Output file: out_file
    # Input format: 1 (Sequential)
    # Output format: 1 (Sequential)
    # Key position: 1
    # Key length: 3
    # Sort order: A (Ascending)
    # Key type: N (Numeric)
    input_str = f"{in_file}\n{out_file}\n1\n1\n1\n3\nA\nN\n"
    res = subprocess.run([EXE_FILE], input=input_str, capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "SORT-11 V3.0 - DEC RMS Sort Utility" in res.stdout
    assert "Status:             SUCCESS" in res.stdout

    lines = [line.strip() for line in out_file.read_text().splitlines() if line.strip()]
    expected = [
        "100 Delta",
        "300 Gamma",
        "500 Beta",
    ]
    assert lines == expected
