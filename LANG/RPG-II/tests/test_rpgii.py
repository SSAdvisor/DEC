import os
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RPG_BIN = os.path.join(ROOT_DIR, "compiler", "rpgii")
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


class TestRPGIIToolchain:
    def test_01_compile_and_link_slsrpt_sample(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "SLSRPT.RPG")
        obj = os.path.join(str(tmp_path), "SLSRPT.OBJ")
        lst = os.path.join(str(tmp_path), "SLSRPT.LST")

        r_comp = subprocess.run([RPG_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "RPG II V2.1: Compiled SLSRPT.RPG -> SLSRPT.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC PDP-11 RPG II V2.1 SALES REPORT" in r_run.stdout
        assert "Q1 SALES: 1250" in r_run.stdout
        assert "Q2 SALES: 1750" in r_run.stdout
        assert "TOTAL H1 SALES: 3000" in r_run.stdout

    def test_02_do_loop_subroutine_exsr_and_indicators(self, tmp_path):
        rpg_code = """\
H LOOPRPG
C           Z-ADD 0        ACCUM
C   1       DO    5        IDX
C           EXSR  ADDSR
C           END
C   ACCUM   COMP  15       50
C   50      DSPLY 'RPG-DO-OK:' ACCUM
C           SETON          LR
C   ADDSR   BEGSR
C   ACCUM   ADD   IDX      ACCUM
C           ENDSR
"""
        src = os.path.join(str(tmp_path), "LOOPRPG.RPG")
        obj = os.path.join(str(tmp_path), "LOOPRPG.OBJ")
        with open(src, "w") as f:
            f.write(rpg_code)

        r_comp = subprocess.run([RPG_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "RPG-DO-OK:15" in r_run.stdout

    def test_03_mult_div_sub_and_move(self, tmp_path):
        rpg_code = """\
H ARITHRPG
C           Z-ADD 12       QTY
C           Z-ADD 20       PRICE
C   QTY     MULT  PRICE    GROSS
C   GROSS   SUB   40       NET
C   NET     DIV   4        QTR
C           MOVE  'PAID'   STATUS
O QPRINT  D
O                         'STATUS=' STATUS ' QTR=' QTR
"""
        src = os.path.join(str(tmp_path), "ARITHRPG.RPG")
        obj = os.path.join(str(tmp_path), "ARITHRPG.OBJ")
        with open(src, "w") as f:
            f.write(rpg_code)

        r_comp = subprocess.run([RPG_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "STATUS=PAID QTR=50" in r_run.stdout

    def test_04_interactive_workbench_mode(self, tmp_path):
        r = subprocess.run(
            [RPG_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC PDP-11 RPG II V2.1 Compiler" in r.stdout
        assert "H-Spec (Control)     : Verified" in r.stdout
        assert "O-Spec (Output)      : Verified" in r.stdout
