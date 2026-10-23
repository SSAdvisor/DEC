#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX DSM V6.0-00 (vaxdsm)
"""

import os
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXDSM_BIN = os.path.join(ROOT_DIR, "compiler", "vaxdsm")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXDSMCompilerAndEnvironment:
    def test_01_compile_and_link_demo_dsm(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.DSM")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")

        r_comp = subprocess.run([VAXDSM_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX DSM V6.0-00: Compiled DEMO.DSM -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(lst, "r") as f:
            lst_txt = f.read()
        assert "DEC VAX DSM V6.0-00" in lst_txt
        assert "Tag REPORT" in lst_txt

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX DSM V6.0-00 — DIGITAL STANDARD MUMPS" in r_run.stdout
        assert "ID=101 NAME=BELL,GORDON" in r_run.stdout
        assert "DEPT=CARDIOLOGY [ADM]" in r_run.stdout
        assert "ID=102 NAME=CUTLER,DAVE" in r_run.stdout
        assert "TOTAL PATIENTS=2 DATA(101)=11" in r_run.stdout

    def test_02_mumps_intrinsics_and_operators(self, tmp_path):
        src = os.path.join(str(tmp_path), "INTRIN.M")
        obj = os.path.join(str(tmp_path), "INTRIN.OBJ")
        exe = os.path.join(str(tmp_path), "INTRIN.EXE")

        with open(src, "w") as f:
            f.write(
                "INTRIN ; Test MUMPS intrinsics\n"
                ' S S="VAX/VMS/DSM"\n'
                ' W "LEN=",$L(S)," PIECES=",$L(S,"/")," P2=",$P(S,"/",2),!\n'
                ' W "FIND=",$F(S,"VMS")," ASC=",$A("A")," CHR=",$C(68,69,67),!\n'
                ' I S["VMS" W "CONTAINS=YES",!\n'
                " H\n"
            )

        assert subprocess.run([VAXDSM_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "LEN=11 PIECES=3 P2=VMS" in r_run.stdout
        assert "FIND=8 ASC=65 CHR=DEC" in r_run.stdout
        assert "CONTAINS=YES" in r_run.stdout

    def test_03_for_loops_postconditionals_and_new_scoping(self, tmp_path):
        src = os.path.join(str(tmp_path), "SCOPE.DSM")
        obj = os.path.join(str(tmp_path), "SCOPE.OBJ")
        exe = os.path.join(str(tmp_path), "SCOPE.EXE")

        with open(src, "w") as f:
            f.write(
                "MAIN ; Test FOR, NEW, and postconditionals\n"
                " S X=99,SUM=0\n"
                " F I=1:1:5 S:I'=3 SUM=SUM+I\n"
                " D SUB\n"
                ' W "OUTER_X=",X," SUM=",SUM,!\n'
                " H\n"
                "SUB ; Local scope test\n"
                " N X\n"
                " S X=42\n"
                ' W "INNER_X=",X,!\n'
                " Q\n"
            )

        assert subprocess.run([VAXDSM_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "INNER_X=42" in r_run.stdout
        assert "OUTER_X=99 SUM=12" in r_run.stdout

    def test_04_interactive_dsm_programmer_mode(self, tmp_path):
        stdin_cmds = (
            'S ^INV(1)="DISK",^INV(2)="TAPE"\n'
            'W $O(^INV(1)),"=",^INV(2),!\n'
            "H\n"
        )
        r = subprocess.run([VAXDSM_BIN, "--interactive"], input=stdin_cmds, capture_output=True, text=True, cwd=str(tmp_path))
        assert r.returncode == 0
        assert "DEC VAX DSM V6.0-00 — Digital Standard MUMPS" in r.stdout
        assert "DSM>" in r.stdout
        assert "2=TAPE" in r.stdout
