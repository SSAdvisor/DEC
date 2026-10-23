import os
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COBOL_BIN = os.path.join(ROOT_DIR, "compiler", "cobol81")
BASICLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "BASIC-PLUS-2", "linker", "basiclink"))
VM_DIR = os.path.abspath(os.path.join(ROOT_DIR, "..", "BASIC-PLUS-2", "vm", "build"))


def link_and_run(obj_path, tmp_path):
    tsk_path = os.path.join(str(tmp_path), "PROG.TSK")
    env = os.environ.copy()
    env["PATH"] = f"{VM_DIR}:{env.get('PATH', '')}"
    r_link = subprocess.run([BASICLINK_BIN, "-o", tsk_path, obj_path], capture_output=True, text=True, env=env)
    assert r_link.returncode == 0, r_link.stdout + r_link.stderr
    r_run = subprocess.run([tsk_path], capture_output=True, text=True, cwd=str(tmp_path))
    return r_run


class TestCobol81Toolchain:
    def test_01_compile_and_link_payroll_sample(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "PAYROL.CBL")
        obj = os.path.join(str(tmp_path), "PAYROL.OBJ")
        lst = os.path.join(str(tmp_path), "PAYROL.LST")

        r_comp = subprocess.run([COBOL_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "COBOL-81 V2.4: Compiled PAYROL.CBL -> PAYROL.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC PDP-11 COBOL-81 V2.4 PAYROLL SYSTEM" in r_run.stdout
        assert "EMPLOYEE:  J. DEC ENGINEER" in r_run.stdout
        assert "GROSS PAY: 1200" in r_run.stdout

    def test_02_compute_perform_varying_and_if(self, tmp_path):
        cbl_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SUMTEST.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  IDX-N          PIC 9(4) VALUE 1.
       01  ACC-SUM        PIC 9(6) VALUE 0.
       PROCEDURE DIVISION.
       MAIN-PARA.
           PERFORM ADD-STEP VARYING IDX-N FROM 1 BY 1 UNTIL IDX-N > 5.
           IF ACC-SUM = 15 THEN DISPLAY "SUM-OK: " ACC-SUM ELSE DISPLAY "SUM-BAD".
           STOP RUN.
       ADD-STEP.
           COMPUTE ACC-SUM = ACC-SUM + IDX-N.
           EXIT.
"""
        src = os.path.join(str(tmp_path), "SUMTEST.CBL")
        obj = os.path.join(str(tmp_path), "SUMTEST.OBJ")
        with open(src, "w") as f:
            f.write(cbl_code)

        r_comp = subprocess.run([COBOL_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "SUM-OK: 15" in r_run.stdout

    def test_03_subtract_divide_and_move(self, tmp_path):
        cbl_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ARITHCBL.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  A-VAL          PIC 9(4) VALUE 100.
       01  B-VAL          PIC 9(4) VALUE 28.
       01  DIFF-VAL       PIC 9(4) VALUE 0.
       01  QUOT-VAL       PIC 9(4) VALUE 0.
       PROCEDURE DIVISION.
       START-PARA.
           SUBTRACT B-VAL FROM A-VAL GIVING DIFF-VAL.
           DIVIDE 8 INTO DIFF-VAL GIVING QUOT-VAL.
           DISPLAY "QUOTIENT=" QUOT-VAL.
           STOP RUN.
"""
        src = os.path.join(str(tmp_path), "ARITHCBL.CBL")
        obj = os.path.join(str(tmp_path), "ARITHCBL.OBJ")
        with open(src, "w") as f:
            f.write(cbl_code)

        r_comp = subprocess.run([COBOL_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "QUOTIENT=9" in r_run.stdout

    def test_04_interactive_workbench_mode(self, tmp_path):
        r = subprocess.run(
            [COBOL_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC PDP-11 COBOL-81 V2.4 Compiler" in r.stdout
        assert "IDENTIFICATION DIVISION : Verified" in r.stdout
        assert "0 syntax errors" in r.stdout
