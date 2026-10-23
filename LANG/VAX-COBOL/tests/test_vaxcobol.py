#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX COBOL V4.3 Compiler (vaxcobol)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXCOBOL_BIN = os.path.join(ROOT_DIR, "compiler", "vaxcobol")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


def link_and_run(obj_path, tmp_path):
    exe_path = os.path.join(str(tmp_path), "PROG.EXE")
    r_link = subprocess.run([VMSLINK_BIN, "-o", exe_path, obj_path], capture_output=True, text=True)
    assert r_link.returncode == 0, r_link.stdout + r_link.stderr
    assert os.path.isfile(exe_path)
    return subprocess.run([exe_path], capture_output=True, text=True, cwd=str(tmp_path))


class TestVAXCobolCompiler:
    def test_01_compile_and_link_demo_cob(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.COB")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r_comp = subprocess.run([VAXCOBOL_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX COBOL V4.3-00: Compiled DEMO.COB -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["target"] == "VAX/VMS"

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC VAX COBOL V4.3 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "EMPLOYEE: KEN OLSEN TIER: VAX-SYSTEMS" in r_run.stdout
        assert "BASE=1400 BONUS=500 GROSS=1900" in r_run.stdout

    def test_02_block_if_else_end_if_and_evaluate(self, tmp_path):
        cob_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. EVALTST.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       77  SCORE-VAL        PIC 9(4) VALUE 85.
       77  GRADE-STR        PIC X(12) VALUE SPACES.
       77  STATUS-STR       PIC X(12) VALUE SPACES.
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           IF SCORE-VAL >= 60
               MOVE "PASSED" TO STATUS-STR
           ELSE
               MOVE "FAILED" TO STATUS-STR
           END-IF.
           EVALUATE SCORE-VAL
               WHEN 90 THRU 100
                   MOVE "GRADE-A" TO GRADE-STR
               WHEN 80 THRU 89
                   MOVE "GRADE-B" TO GRADE-STR
               WHEN OTHER
                   MOVE "GRADE-C" TO GRADE-STR
           END-EVALUATE.
           DISPLAY "STATUS=" STATUS-STR " GRADE=" GRADE-STR.
           STOP RUN.
"""
        src = os.path.join(str(tmp_path), "EVALTST.COB")
        obj = os.path.join(str(tmp_path), "EVALTST.OBJ")
        with open(src, "w") as f:
            f.write(cob_code)

        r_comp = subprocess.run([VAXCOBOL_BIN, src, f"/OBJECT={obj}"], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "STATUS=PASSED GRADE=GRADE-B" in r_run.stdout

    def test_03_inline_perform_times_until_and_initialize(self, tmp_path):
        cob_code = """\
IDENTIFICATION DIVISION.
PROGRAM-ID. PERFTST.
DATA DIVISION.
WORKING-STORAGE SECTION.
01  CNT-A          PIC 9(4) VALUE 99.
01  CNT-B          PIC 9(4) VALUE 0.
01  QUOT-V         PIC 9(4) VALUE 0.
PROCEDURE DIVISION.
START-PARA.
    INITIALIZE CNT-A.
    PERFORM 3 TIMES
        ADD 10 TO CNT-A
    END-PERFORM.
    PERFORM UNTIL CNT-B >= 4
        ADD 1 TO CNT-B
    END-PERFORM.
    DIVIDE CNT-B INTO CNT-A GIVING QUOT-V.
    DISPLAY "CNT-A=" CNT-A " CNT-B=" CNT-B " QUOT=" QUOT-V.
    STOP RUN.
"""
        src = os.path.join(str(tmp_path), "PERFTST.COB")
        obj = os.path.join(str(tmp_path), "PERFTST.OBJ")
        with open(src, "w") as f:
            f.write(cob_code)

        r_comp = subprocess.run([VAXCOBOL_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "CNT-A=30 CNT-B=4 QUOT=7" in r_run.stdout

    def test_04_interactive_workbench(self, tmp_path):
        r = subprocess.run(
            [VAXCOBOL_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC VAX COBOL V4.3-00 Compiler" in r.stdout
        assert "IDENTIFICATION DIVISION : Verified" in r.stdout
        assert "0 syntax errors" in r.stdout
