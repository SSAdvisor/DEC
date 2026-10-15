import os
import subprocess
import sqlite3
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(APP_DIR, "src")
BIN_DIR = os.path.join(APP_DIR, "bin")
BUILD_DIR = os.path.join(APP_DIR, "build")

RMSDES_EXE = os.path.join(BIN_DIR, "rmsdes")
RMSDEF_EXE = os.path.join(BIN_DIR, "rmsdef")
RMSIFL_EXE = os.path.join(BIN_DIR, "rmsifl")
RMSCNV_EXE = os.path.join(BIN_DIR, "rmscnv")
RMSBCK_EXE = os.path.join(BIN_DIR, "rmsbck")
RMSRST_EXE = os.path.join(BIN_DIR, "rmsrst")
RMSDSP_EXE = os.path.join(BIN_DIR, "rmsdsp")
RMSUTILS_EXE = os.path.join(BIN_DIR, "rmsutils")

ALL_EXES = [
    RMSDES_EXE,
    RMSDEF_EXE,
    RMSIFL_EXE,
    RMSCNV_EXE,
    RMSBCK_EXE,
    RMSRST_EXE,
    RMSDSP_EXE,
    RMSUTILS_EXE,
]

SAMPLE_RECORDS = [
    "1001 Adams, Abigail       ENGINEERING  75000",
    "1002 Smith, John          MARKETING    62000",
    "1003 Williams, Roger      OPERATIONS   58000",
    "1004 Davis, Clara         FINANCE      81000",
    "1005 Miller, Ethan        RESEARCH     92000",
]

def test_rmsutils_build():
    """Verify clean build and linking of all 8 RMS utility binaries."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"

    for exe in ALL_EXES:
        assert os.path.isfile(exe), f"Binary {exe} not found after build"
        assert os.access(exe, os.X_OK), f"Binary {exe} is not executable"

def test_rmsdes_design_file(tmp_path):
    """Verify RMSDES generates a valid DEC RMS design (.DES) specification."""
    des_file = tmp_path / "employee.des"
    cmd = f"{des_file} INDEXED 255 1 4"
    res = subprocess.run([RMSDES_EXE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"RMSDES failed:\n{res.stdout}\n{res.stderr}"
    assert "Status:             SUCCESS" in res.stdout
    assert os.path.isfile(des_file)

    content = des_file.read_text()
    assert "ORGANIZATION: INDEXED" in content
    assert "RECORD_SIZE: 255" in content
    assert "KEY_POSITION: 1" in content
    assert "KEY_LENGTH: 4" in content

def test_rmsdef_create_indexed_from_des(tmp_path):
    """Verify RMSDEF creates an SQLite indexed RMS file from a .DES design file."""
    des_file = tmp_path / "test.des"
    des_file.write_text(
        "! DEC RMS-11 DESIGN SPECIFICATION\n"
        "FILE_NAME: test.idx\n"
        "ORGANIZATION: INDEXED\n"
        "RECORD_FORMAT: FIXED\n"
        "MAX_RECORD_SIZE: 255\n"
        "KEY_POS: 1\n"
        "KEY_SIZE: 4\n"
        "KEY_TYPE: STRING\n"
        "DUPLICATES: NO\n"
    )
    idx_file = tmp_path / "test.idx"
    cmd = f"{idx_file}={des_file}"
    res = subprocess.run([RMSDEF_EXE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"RMSDEF failed:\n{res.stdout}\n{res.stderr}"
    assert "Status:             SUCCESS" in res.stdout
    assert os.path.isfile(idx_file)

    conn = sqlite3.connect(str(idx_file))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records';")
    assert cur.fetchone() is not None, "Table 'records' not found in created .IDX file"
    conn.close()

def test_rmsdef_create_from_switches(tmp_path):
    """Verify RMSDEF creates files using inline command switches."""
    idx_file = tmp_path / "switches.idx"
    cmd = f"{idx_file}/ORG:INDEXED/SIZE:255/KEY:(POS:1,SIZ:4)"
    res = subprocess.run([RMSDEF_EXE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"RMSDEF switch mode failed:\n{res.stdout}\n{res.stderr}"
    assert "Status:             SUCCESS" in res.stdout
    assert os.path.isfile(idx_file)

def test_rmsifl_load_indexed(tmp_path):
    """Verify RMSIFL loads sequential data into an RMS indexed file."""
    idx_file = tmp_path / "loaded.idx"
    seq_file = tmp_path / "records.txt"
    seq_file.write_text("\n".join(SAMPLE_RECORDS) + "\n")

    cmd = f"{idx_file}={seq_file}"
    res = subprocess.run([RMSIFL_EXE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"RMSIFL failed:\n{res.stdout}\n{res.stderr}"
    assert "Status:             SUCCESS" in res.stdout
    assert "Records Loaded:     5" in res.stdout
    assert "Duplicate Keys:     0" in res.stdout

    conn = sqlite3.connect(str(idx_file))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM records;")
    cnt = cur.fetchone()[0]
    assert cnt == 5

    cur.execute("SELECT key FROM records ORDER BY id ASC;")
    rows = [r[0].strip() for r in cur.fetchall()]
    conn.close()
    assert rows[0].startswith("1001 Adams")
    assert rows[4].startswith("1005 Miller")

def test_rmsdsp_display_indexed(tmp_path):
    """Verify RMSDSP inspects RMS file metadata, statistics, and record keys."""
    idx_file = tmp_path / "disp.idx"
    seq_file = tmp_path / "records.txt"
    seq_file.write_text("\n".join(SAMPLE_RECORDS) + "\n")
    subprocess.run([RMSIFL_EXE, f"{idx_file}={seq_file}"], check=True, timeout=10)

    res = subprocess.run([RMSDSP_EXE, str(idx_file)], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"RMSDSP failed:\n{res.stdout}\n{res.stderr}"
    assert "RMSDSP V2.0 - DEC RMS-11 File Display Utility" in res.stdout
    assert "File Organization:  INDEXED" in res.stdout
    assert "Total Records:      5" in res.stdout
    assert "First Key Seen:     1001 Adams, Abigail" in res.stdout
    assert "Last Key Seen:      1005 Miller, Ethan" in res.stdout
    assert "Integrity Status:   VALID RMS STRUCTURE" in res.stdout

def test_rmsbck_and_rmsrst_roundtrip(tmp_path):
    """Verify RMSBCK backs up an indexed file and RMSRST restores it with exact integrity."""
    idx_orig = tmp_path / "original.idx"
    bck_file = tmp_path / "backup.bck"
    idx_rest = tmp_path / "restored.idx"
    seq_file = tmp_path / "records.txt"
    seq_file.write_text("\n".join(SAMPLE_RECORDS) + "\n")

    # Load original
    subprocess.run([RMSIFL_EXE, f"{idx_orig}={seq_file}"], check=True, timeout=10)

    # Backup
    res_bck = subprocess.run([RMSBCK_EXE, f"{bck_file}={idx_orig}"], capture_output=True, text=True, timeout=10)
    assert res_bck.returncode == 0, f"RMSBCK failed:\n{res_bck.stdout}\n{res_bck.stderr}"
    assert "Records Backed Up:  5" in res_bck.stdout
    assert "Status:             SUCCESS" in res_bck.stdout
    assert os.path.isfile(bck_file)

    # Restore
    res_rst = subprocess.run([RMSRST_EXE, f"{idx_rest}={bck_file}"], capture_output=True, text=True, timeout=10)
    assert res_rst.returncode == 0, f"RMSRST failed:\n{res_rst.stdout}\n{res_rst.stderr}"
    assert "Records Expected:   5" in res_rst.stdout
    assert "Records Restored:   5" in res_rst.stdout
    assert "Integrity Check:    VERIFIED (OK)" in res_rst.stdout
    assert "Status:             SUCCESS" in res_rst.stdout

    # Verify restored records match original
    conn = sqlite3.connect(str(idx_rest))
    cur = conn.cursor()
    cur.execute("SELECT key FROM records ORDER BY id ASC;")
    rows = [r[0].strip() for r in cur.fetchall()]
    conn.close()
    assert rows == SAMPLE_RECORDS

def test_rmscnv_conversion(tmp_path):
    """Verify RMSCNV converts between RMS indexed and sequential files."""
    idx_file = tmp_path / "data.idx"
    seq_out = tmp_path / "converted.txt"
    reidx_file = tmp_path / "reindexed.idx"
    seq_in = tmp_path / "in.txt"
    seq_in.write_text("\n".join(SAMPLE_RECORDS) + "\n")

    # 1. Create indexed source
    subprocess.run([RMSIFL_EXE, f"{idx_file}={seq_in}"], check=True, timeout=10)

    # 2. Convert Indexed -> Sequential
    res1 = subprocess.run([RMSCNV_EXE, f"{seq_out}={idx_file}/SEQ"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0, f"RMSCNV Indexed->Seq failed:\n{res1.stdout}\n{res1.stderr}"
    assert "Records Converted:  5" in res1.stdout
    assert seq_out.read_text().splitlines() == SAMPLE_RECORDS

    # 3. Convert Sequential -> Indexed
    res2 = subprocess.run([RMSCNV_EXE, f"{reidx_file}={seq_out}/IDX"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0, f"RMSCNV Seq->Indexed failed:\n{res2.stdout}\n{res2.stderr}"
    assert "Records Converted:  5" in res2.stdout

    conn = sqlite3.connect(str(reidx_file))
    cur = conn.cursor()
    cur.execute("SELECT key FROM records ORDER BY id ASC;")
    rows = [r[0].strip() for r in cur.fetchall()]
    conn.close()
    assert rows == SAMPLE_RECORDS

def test_rmsutils_dispatcher_cli(tmp_path):
    """Verify master RMSUTILS dispatcher executes sub-utilities via CLI."""
    idx_file = tmp_path / "disp_test.idx"
    seq_file = tmp_path / "disp_seq.txt"
    seq_file.write_text("\n".join(SAMPLE_RECORDS[:3]) + "\n")

    # Load via dispatcher
    cmd = f"rmsifl {idx_file}={seq_file}"
    res = subprocess.run([RMSUTILS_EXE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"RMSUTILS dispatcher failed:\n{res.stdout}\n{res.stderr}"
    assert "RMSIFL V2.0" in res.stdout
    assert "Records Loaded:     3" in res.stdout

    # Display via dispatcher
    cmd2 = f"rmsdsp {idx_file}"
    res2 = subprocess.run([RMSUTILS_EXE, cmd2], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "RMSDSP V2.0" in res2.stdout
    assert "Total Records:      3" in res2.stdout

def test_rmsutils_dispatcher_menu_exit():
    """Verify interactive menu responds and exits cleanly on option 0."""
    res = subprocess.run([RMSUTILS_EXE], input="0\n", capture_output=True, text=True, timeout=5)
    assert res.returncode == 0
    assert "DEC RMS-11 Utilities Suite V2.0" in res.stdout
    assert "Select utility [0-7]:" in res.stdout
