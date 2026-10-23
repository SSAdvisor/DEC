import os
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIBOL_BIN = os.path.join(ROOT_DIR, "compiler", "dibol83")
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


class TestDibol83Toolchain:
    def test_01_compile_and_link_invoic_sample(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "INVOIC.DBL")
        obj = os.path.join(str(tmp_path), "INVOIC.OBJ")
        lst = os.path.join(str(tmp_path), "INVOIC.LST")

        r_comp = subprocess.run([DIBOL_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "DIBOL-83 V5.3: Compiled INVOIC.DBL -> INVOIC.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DIBOL-83 CUSTOMER: DIGITAL EQUIPMENT CORP" in r_run.stdout
        assert "INVOICE NET TOTAL: 1700" in r_run.stdout

    def test_02_for_loop_incr_decr_and_if(self, tmp_path):
        dbl_code = """\
.TITLE 'LOOPTEST'
RECORD
    IDX,    D4, 0
    ACCUM,  D6, 0
PROC
    FOR IDX FROM 1 THRU 6 DO ACCUM = ACCUM + (IDX * 10)
    INCR ACCUM
    DECR ACCUM
    IF (ACCUM .EQ. 210) DISPLAY(1, 'DIBOL-FOR-OK:', ACCUM) ELSE DISPLAY(1, 'DIBOL-BAD')
    STOP
END
"""
        src = os.path.join(str(tmp_path), "LOOPTEST.DBL")
        obj = os.path.join(str(tmp_path), "LOOPTEST.OBJ")
        with open(src, "w") as f:
            f.write(dbl_code)

        r_comp = subprocess.run([DIBOL_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DIBOL-FOR-OK:210" in r_run.stdout

    def test_03_clear_and_xcall_outpt(self, tmp_path):
        dbl_code = """\
RECORD
    COUNT, D4, 99
PROC
    CLEAR COUNT
    INCR COUNT
    XCALL OUTPT(1, 1, 'OUTPT-BANNER-OK', 1)
    DISPLAY(1, 'COUNT=', COUNT)
    STOP
"""
        src = os.path.join(str(tmp_path), "CLRTST.DBL")
        obj = os.path.join(str(tmp_path), "CLRTST.OBJ")
        with open(src, "w") as f:
            f.write(dbl_code)

        r_comp = subprocess.run([DIBOL_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "OUTPT-BANNER-OK" in r_run.stdout
        assert "COUNT=1" in r_run.stdout

    def test_04_interactive_workbench_mode(self, tmp_path):
        r = subprocess.run(
            [DIBOL_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC DIBOL-83 V5.3 Compiler" in r.stdout
        assert "RECORD Section      : Verified" in r.stdout
        assert "0 errors, 0 warnings" in r.stdout
