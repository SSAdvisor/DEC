import subprocess
import os
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDT_BIN = os.path.join(ROOT_DIR, "edt", "edt")
SAMPLE_TXT = os.path.join(ROOT_DIR, "edt", "sample.txt")


def run_edt(inputs):
    input_str = "\n".join(inputs) + "\n"
    res = subprocess.run(
        [EDT_BIN],
        input=input_str,
        capture_output=True,
        text=True,
        cwd=ROOT_DIR,
        timeout=10,
    )
    return res.stdout, res.stderr, res.returncode


def test_edt_help():
    stdout, _, code = run_edt(["NONAME.TXT", "HELP", "QUIT"])
    assert code == 0
    assert "DEC RSTS/E EDT Editor" in stdout
    assert "DEC RSTS/E EDT COMMAND SUMMARY" in stdout
    assert "TYPE, T" in stdout
    assert "INSERT, I" in stdout
    assert "DELETE, D" in stdout
    assert "SUBSTITUTE, S" in stdout
    assert "EDT aborted." in stdout


def test_edt_load_existing_file():
    stdout, _, code = run_edt([SAMPLE_TXT, "T 1:3", "SHOW", "QUIT"])
    assert code == 0
    assert f"File {SAMPLE_TXT}" in stdout
    assert "DIGITAL EQUIPMENT CORPORATION" in stdout
    assert "Current File:" in stdout
    assert "Terminal Mode:   VT100 Video Terminal" in stdout


def test_edt_create_insert_and_exit(tmp_path):
    test_file = str(tmp_path / "test_doc.txt")
    inputs = [
        test_file,
        "I",
        "Line Alpha",
        "Line Beta",
        "Line Gamma",
        ".",
        "T WHOLE",
        "EXIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "Line Alpha" in stdout
    assert "Line Beta" in stdout
    assert "Line Gamma" in stdout
    assert "EDT session complete." in stdout

    # Verify file was written to disk
    assert os.path.exists(test_file)
    with open(test_file, "r") as f:
        content = f.read().splitlines()
    assert content == ["Line Alpha", "Line Beta", "Line Gamma"]


def test_edt_find_and_substitute(tmp_path):
    test_file = str(tmp_path / "subst_test.txt")
    # First create file
    with open(test_file, "w") as f:
        f.write("System online\nStatus: FAIL\nAll clear\n")

    inputs = [
        test_file,
        "F FAIL",
        "S /FAIL/PASS/",
        "T WHOLE",
        "EXIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "Status: FAIL" in stdout
    assert "Status: PASS" in stdout

    # Verify updated file on disk
    with open(test_file, "r") as f:
        lines = f.read().splitlines()
    assert lines == ["System online", "Status: PASS", "All clear"]


def test_edt_delete_lines(tmp_path):
    test_file = str(tmp_path / "delete_test.txt")
    with open(test_file, "w") as f:
        f.write("Line 10\nLine 20 to delete\nLine 30\n")

    inputs = [
        test_file,
        "D 2",
        "T WHOLE",
        "EXIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "[1 line(s) deleted]" in stdout

    with open(test_file, "r") as f:
        lines = f.read().splitlines()
    assert lines == ["Line 10", "Line 30"]


def test_edt_resequence_and_write(tmp_path):
    test_file = str(tmp_path / "write_test.txt")
    other_file = str(tmp_path / "saved_copy.txt")
    with open(test_file, "w") as f:
        f.write("Header\nEntry 1\nEntry 2\n")

    inputs = [
        test_file,
        "RESEQ",
        f"W {other_file}",
        "QUIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "[Buffer resequenced: 1 to 3]" in stdout
    assert f"3 lines written to file: {other_file}" in stdout

    with open(other_file, "r") as f:
        lines = f.read().splitlines()
    assert lines == ["Header", "Entry 1", "Entry 2"]


def test_edt_quit_aborts_without_saving(tmp_path):
    test_file = str(tmp_path / "abort_test.txt")
    original = "Original unmodified content\n"
    with open(test_file, "w") as f:
        f.write(original)

    inputs = [
        test_file,
        "D 1",
        "QUIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "EDT aborted." in stdout

    with open(test_file, "r") as f:
        content = f.read()
    assert content == original


def test_edt_define_key_and_show_key():
    inputs = [
        "NONAME.TXT",
        "DEFINE KEY 7 AS 'T WHOLE'",
        "DEFINE KEY GOLD D AS 'D .'",
        "SHOW KEY",
        "SHOW",
        "QUIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "[Key '7' defined]" in stdout
    assert "[Key 'GOLD D' defined]" in stdout
    assert "KEY 7 AS 'T WHOLE'" in stdout
    assert "KEY GOLD D AS 'D .'" in stdout
    assert "Defined Keys:    2" in stdout


def test_edt_define_and_execute_macro(tmp_path):
    test_file = str(tmp_path / "macro_test.txt")
    with open(test_file, "w") as f:
        f.write("Alpha item\nBeta item\nGamma item\n")

    inputs = [
        test_file,
        "DEFINE MACRO SWAP AS 'F Beta;S /Beta/BETA/;T .'",
        "SHOW MACRO",
        "SHOW",
        "SWAP",
        "EXIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "[Macro 'SWAP' defined]" in stdout
    assert "MACRO SWAP AS 'F Beta;S /Beta/BETA/;T .'" in stdout
    assert "Defined Macros:  1" in stdout
    assert "BETA item" in stdout

    with open(test_file, "r") as f:
        lines = f.read().splitlines()
    assert lines == ["Alpha item", "BETA item", "Gamma item"]


def test_edt_command_file_procedure(tmp_path):
    test_file = str(tmp_path / "cmd_target.txt")
    with open(test_file, "w") as f:
        f.write("Line 1\nLine 2\n")

    cmd_file = str(tmp_path / "script.edt")
    with open(cmd_file, "w") as f:
        f.write("I\nLine 0\n.\n")
        f.write("T WHOLE\n")

    inputs = [
        test_file,
        f"@{cmd_file}",
        "EXIT",
    ]
    stdout, _, code = run_edt(inputs)
    assert code == 0
    assert "Line 0" in stdout

    with open(test_file, "r") as f:
        lines = f.read().splitlines()
    assert lines == ["Line 0", "Line 1", "Line 2"]


def test_edt_edtini_autoload(tmp_path):
    ini_path = os.path.join(ROOT_DIR, "EDTINI.EDT")
    try:
        with open(ini_path, "w") as f:
            f.write("DEFINE KEY 5 AS 'T .'\n")
            f.write("DEFINE MACRO LISTALL AS 'T WHOLE'\n")

        inputs = [
            SAMPLE_TXT,
            "SHOW KEY",
            "SHOW MACRO",
            "QUIT",
        ]
        stdout, _, code = run_edt(inputs)
        assert code == 0
        assert "[Loaded configuration from EDTINI.EDT]" in stdout
        assert "KEY 5 AS 'T .'" in stdout
        assert "MACRO LISTALL AS 'T WHOLE'" in stdout
    finally:
        if os.path.exists(ini_path):
            os.remove(ini_path)

