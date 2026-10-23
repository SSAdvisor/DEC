import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "lex11.obj")
EXE_FILE = os.path.join(BIN_DIR, "lex11")
LEX_LINK = os.path.join(BIN_DIR, "lex")


def test_lex11_build():
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0
    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\n{res_build.stdout}\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE)
    assert os.path.isfile(EXE_FILE)
    assert os.access(EXE_FILE, os.X_OK)
    assert os.path.islink(LEX_LINK)


def test_lex11_banner_and_help():
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, _ = proc.communicate(input="HELP\nEXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "LEX-11 V2.4 - Word Processing & Office Automation System" in out
    assert "EEC Systems, Inc. (Millis, MA)" in out
    assert "LEX-11>" in out
    assert "LEX-11 V2.4 Word Processing & Office Automation Commands" in out


def test_lex11_sample_catalog_and_read():
    res = subprocess.run([EXE_FILE, "SAMPLE; DIR; SELECT 1; READ; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0
    assert "[Sample LEX-11 catalog loaded - 4 documents, 3 mail records, 3 glossary macros]" in res.stdout
    assert "LEX-11 Document Catalog (LEXDOC.DAT)" in res.stdout
    assert "EEC Systems LEX-11 V2.4 Executive Summary" in res.stdout
    assert "LEX-11 System Status:" in res.stdout


def test_lex11_desk_calculator_and_glossary_expand():
    res = subprocess.run(
        [EXE_FILE, 'SAMPLE; CALC 45*20; GLOSSARY; GLOSSADD "@DEPT", "Millis Systems Lab"; SELECT 1; EXPAND; READ 1; EXIT'],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "[LEX-11 Desk Calculator Register = 900" in res.stdout
    assert "LEX-11 Abbreviation Glossary" in res.stdout
    assert "[Glossary macro added: @DEPT]" in res.stdout
    assert "[Expanded glossary & calculator macros in Document #1" in res.stdout
    assert "EEC Systems, Inc. (Millis, MA)" in res.stdout
    assert "$900" in res.stdout


def test_lex11_mass_mailer_and_save_load(tmp_path):
    lib_file = str(tmp_path / "lex_test.dat")
    cmd1 = 'SAMPLE; CALC 1800; MAILADD "Mr. John Sculley", "Northeast Bottling", "PDP-11/70"; MERGE 2; EXIT'
    res1 = subprocess.run([LEX_LINK, cmd1], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "Dear Mr. John Sculley," in res1.stdout
    assert "$1800" in res1.stdout
    assert "[Mass-Mailer complete: 4 merged documents generated]" in res1.stdout

    cmd2 = f"SAMPLE; SAVE {lib_file}; CLEAR; LOAD {lib_file}; DIR; EXIT"
    res2 = subprocess.run([LEX_LINK, cmd2], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert os.path.isfile(lib_file)
    assert f"[4 documents loaded from {lib_file}]" in res2.stdout
