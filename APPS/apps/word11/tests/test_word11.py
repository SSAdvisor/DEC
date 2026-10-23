import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "word11.obj")
EXE_FILE = os.path.join(BIN_DIR, "word11")
W11_LINK = os.path.join(BIN_DIR, "w11")


def test_word11_build():
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0
    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\n{res_build.stdout}\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE)
    assert os.path.isfile(EXE_FILE)
    assert os.access(EXE_FILE, os.X_OK)
    assert os.path.islink(W11_LINK)


def test_word11_banner_and_help():
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, _ = proc.communicate(input="HELP\nEXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "WORD-11 V3.1 - Multi-User Word Processing System" in out
    assert "Data Processing Design, Inc. (DPD)" in out
    assert "W11>" in out
    assert "WORD-11 V3.1 Word & List Processing Commands" in out


def test_word11_sample_dir_and_read():
    res = subprocess.run([EXE_FILE, "SAMPLE; DIR; SELECT 2; READ; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "[Sample WORD-11 library loaded - 4 documents, 3 LP records, 5 dict terms]" in res.stdout
    assert "WORD-11 Document Index (W11DOC.DAT)" in res.stdout
    assert "DPD WORD-11 V3.1 RSTS/E Operations Guide" in res.stdout
    assert "WORD-11 Customer License Form Letter" in res.stdout
    assert "WORD-11 System Status:" in res.stdout


def test_word11_gold_keypad_spell_and_spool():
    res = subprocess.run(
        [EXE_FILE, "SAMPLE; GOLD; DICTADD RSTS11; SPELL; SPOOL 1; EXIT"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "WORD-11 VT100 PF1 (GOLD) Keypad Command Map" in res.stdout
    assert "Added 'RSTS11' to WORD-11 Spelling Dictionary" in res.stdout
    assert "WORD-11 Spelling Checker V3.1: Scanned Document #1" in res.stdout
    assert "WORD-11 Background Despooler: Queued Document #1 to LP0:" in res.stdout


def test_word11_edit_replace_merge_and_save_load(tmp_path):
    lib_file = str(tmp_path / "w11_test.dat")
    out_file = str(tmp_path / "w11_out.txt")
    cmd1 = (
        'SAMPLE; CREATE "DPD OEM Contract", "J.SMITH", "FINAL"; '
        'APPEND "Line Alpha~Line Beta"; REPLACE "Beta", "Gamma"; '
        'LPADD "Dr. Alan Kay", "Xerox PARC", "PDP-11/70"; MERGE 2; EXIT'
    )
    res1 = subprocess.run([W11_LINK, cmd1], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "[Document #5 created: DPD OEM Contract]" in res1.stdout
    assert "[Replaced 1 occurrence(s) in Document #5]" in res1.stdout
    assert "Dear Dr. Alan Kay," in res1.stdout
    assert "[List Processing complete: 4 merged documents generated]" in res1.stdout

    res_exp = subprocess.run([W11_LINK, f"SAMPLE; EXPORT {out_file}; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_exp.returncode == 0
    assert os.path.isfile(out_file)

    cmd2 = f"SAMPLE; SAVE {lib_file}; CLEAR; LOAD {lib_file}; DIR; EXIT"
    res2 = subprocess.run([W11_LINK, cmd2], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert os.path.isfile(lib_file)
    assert f"[4 documents loaded from {lib_file}]" in res2.stdout
