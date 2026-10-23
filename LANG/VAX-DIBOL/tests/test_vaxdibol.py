#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX DIBOL V4.1 Compiler (vaxdibol)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXDIBOL_BIN = os.path.join(ROOT_DIR, "compiler", "vaxdibol")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


def link_and_run(obj_path, tmp_path):
    exe_path = os.path.join(str(tmp_path), "PROG.EXE")
    r_link = subprocess.run([VMSLINK_BIN, "-o", exe_path, obj_path], capture_output=True, text=True)
    assert r_link.returncode == 0, r_link.stdout + r_link.stderr
    assert os.path.isfile(exe_path)
    return subprocess.run([exe_path], capture_output=True, text=True, cwd=str(tmp_path))


class TestVAXDibolCompiler:
    def test_01_compile_and_link_demo_dbl(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.DBL")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r_comp = subprocess.run([VAXDIBOL_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX DIBOL V4.1-00: Compiled DEMO.DBL -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["target"] == "VAX/VMS"

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC VAX DIBOL V4.1 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "CUSTOMER: DIGITAL EQUIPMENT CORP TIER: VAX-CLUSTER" in r_run.stdout
        assert "QTY=10 DISC=250 NET=2250" in r_run.stdout

    def test_02_while_do_until_and_if_begin_end_else(self, tmp_path):
        dbl_code = """\
.TITLE 'STRUCTDBL'
RECORD
    CNT_W,   I4, 1
    ACC_W,   I4, 0
    CNT_U,   I4, 0
    BADGE,   A12, 'INIT'
PROC
    WHILE (CNT_W .LE. 5) DO
    BEGIN
        ACC_W = ACC_W + CNT_W
        INCR CNT_W
    END

    DO
    BEGIN
        INCR CNT_U
    END
    UNTIL (CNT_U .EQ. 3)

    IF (ACC_W .EQ. 15) THEN
    BEGIN
        BADGE = 'VALID'
    END
    ELSE
    BEGIN
        BADGE = 'ERROR'
    END

    WRITES(1, 'ACC_W=', ACC_W, ' CNT_U=', CNT_U, ' BADGE=', BADGE)
    STOP
END
"""
        src = os.path.join(str(tmp_path), "STRUCTDBL.DBL")
        obj = os.path.join(str(tmp_path), "STRUCTDBL.OBJ")
        with open(src, "w") as f:
            f.write(dbl_code)

        r_comp = subprocess.run([VAXDIBOL_BIN, src, f"/OBJECT={obj}"], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "ACC_W=15 CNT_U=3 BADGE=VALID" in r_run.stdout

    def test_03_function_freturn_and_common(self, tmp_path):
        dbl_code = """\
COMMON
    BASE_VAL, D6, 40
RECORD
    RESULT_V, D6, 0
PROC
    RESULT_V = TRIPLE_VAL(14) + BASE_VAL
    DISPLAY(1, 'RESULT_V=', RESULT_V)
    STOP
END

FUNCTION TRIPLE_VAL (X_IN)
RECORD
    X_IN, D6
PROC
    FRETURN (X_IN * 3)
END
"""
        src = os.path.join(str(tmp_path), "FNTST.DBL")
        obj = os.path.join(str(tmp_path), "FNTST.OBJ")
        with open(src, "w") as f:
            f.write(dbl_code)

        r_comp = subprocess.run([VAXDIBOL_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "RESULT_V=82" in r_run.stdout

    def test_04_interactive_workbench(self, tmp_path):
        r = subprocess.run(
            [VAXDIBOL_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC VAX DIBOL V4.1-00 Compiler" in r.stdout
        assert "RECORD Section      : Verified" in r.stdout
        assert "0 errors, 0 warnings" in r.stdout
