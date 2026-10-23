#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX RPG II V2.2 Compiler (vaxrpg)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXRPG_BIN = os.path.join(ROOT_DIR, "compiler", "vaxrpg")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


def link_and_run(obj_path, tmp_path):
    exe_path = os.path.join(str(tmp_path), "PROG.EXE")
    r_link = subprocess.run([VMSLINK_BIN, "-o", exe_path, obj_path], capture_output=True, text=True)
    assert r_link.returncode == 0, r_link.stdout + r_link.stderr
    assert os.path.isfile(exe_path)
    return subprocess.run([exe_path], capture_output=True, text=True, cwd=str(tmp_path))


class TestVAXRPGIICompiler:
    def test_01_compile_and_link_demo_rpg(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.RPG")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r_comp = subprocess.run([VAXRPG_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX RPG II V2.2-00: Compiled DEMO.RPG -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["target"] == "VAX/VMS"

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC VAX RPG II V2.2 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "EXCPT AUDIT DEPT=VAX-SYS BONUS=1250" in r_run.stdout
        assert "Q1=1200 Q2=1800 SUBTOT=3000" in r_run.stdout
        assert "TOTAL VAX REVENUE=4250" in r_run.stdout

    def test_02_goto_tag_indicators_and_z_sub(self, tmp_path):
        rpg_code = """\
H GOTORPG
C           Z-ADD 50       VALA
C           Z-SUB 10       NEGV
C           SETON          H1
C           SETOF          05
C   N05     GOTO  SKIP1
C           Z-ADD 999      VALA
C   SKIP1   TAG
C   H1      VALA  ADD   NEGV     FINALV
O QPRINT  D  H1
O                         'FINALV=' FINALV
"""
        src = os.path.join(str(tmp_path), "GOTORPG.RPG")
        obj = os.path.join(str(tmp_path), "GOTORPG.OBJ")
        with open(src, "w") as f:
            f.write(rpg_code)

        r_comp = subprocess.run([VAXRPG_BIN, src, f"/OBJECT={obj}"], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "FINALV=40" in r_run.stdout

    def test_03_div_mvr_movel_and_comp_hi_lo_eq(self, tmp_path):
        rpg_code = """\
H DIVRPG
C           Z-ADD 47       NUMER
C           Z-ADD 5        DENOM
C   NUMER   DIV   DENOM    QUOT
C           MVR            REMDR
C   QUOT    COMP  9        21 22 23
C   23      MOVEL 'EXACT9' STATUS
O QPRINT  D  23
O                         'QUOT=' QUOT ' REM=' REMDR ' STATUS=' STATUS
"""
        src = os.path.join(str(tmp_path), "DIVRPG.RPG")
        obj = os.path.join(str(tmp_path), "DIVRPG.OBJ")
        with open(src, "w") as f:
            f.write(rpg_code)

        r_comp = subprocess.run([VAXRPG_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "QUOT=9 REM=2 STATUS=EXACT9" in r_run.stdout

    def test_04_interactive_workbench(self, tmp_path):
        r = subprocess.run(
            [VAXRPG_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC VAX RPG II V2.2-00 Compiler" in r.stdout
        assert "H-Spec (Control)     : Verified" in r.stdout
        assert "O-Spec (Output)      : Verified" in r.stdout
