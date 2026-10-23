#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX APL V3.1-00 (vaxapl)
"""

import os
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXAPL_BIN = os.path.join(ROOT_DIR, "compiler", "vaxapl")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXAPLCompilerAndWorkspace:
    def test_01_compile_and_link_demo_apl(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.APL")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")

        r_comp = subprocess.run([VAXAPL_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX APL V3.1-00: Compiled DEMO.APL -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(lst, "r") as f:
            lst_txt = f.read()
        assert "DEC VAX APL V3.1-00" in lst_txt
        assert "Compilation Summary: 0 Diagnostics" in lst_txt

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX APL V3.1-00 — VAX/VMS VECTOR ANALYTICS" in r_run.stdout
        assert "1 2 3 4 5 6 7 8 9 10" in r_run.stdout
        assert "55" in r_run.stdout
        assert "120" in r_run.stdout
        assert "92" in r_run.stdout
        assert "14" in r_run.stdout
        assert "5 4 3 2 1" in r_run.stdout
        assert "30" in r_run.stdout

    def test_02_ascii_mnemonics_and_dcl_qualifiers(self, tmp_path):
        src = os.path.join(str(tmp_path), "ASCII.APL")
        obj = os.path.join(str(tmp_path), "ASCII.OBJ")
        lst = os.path.join(str(tmp_path), "ASCII.LST")
        exe = os.path.join(str(tmp_path), "ASCII.EXE")

        with open(src, "w") as f:
            f.write(
                "REM VAX APL ASCII MNEMONIC TEST\n"
                "V <- .IOTA 6\n"
                "QUAD<- .SUM V\n"
                "QUAD<- .PROD .IOTA 4\n"
                "QUAD<- .MAX 12 45 9 33\n"
                "QUAD<- .MIN 12 45 9 33\n"
                "QUAD<- .REV .IOTA 4\n"
                "QUAD<- .RHO V\n"
            )

        r_comp = subprocess.run([VAXAPL_BIN, src, f"/OBJECT={obj}", f"/LIST={lst}"], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        lines = [ln.strip() for ln in r_run.stdout.strip().splitlines()]
        assert lines == ["21", "24", "45", "9", "4 3 2 1", "6"]

    def test_03_interactive_repl_workspace_commands(self, tmp_path):
        stdin_cmds = (
            ")WSID VAXCALC\n"
            "A ← ⍳ 5\n"
            "B ← 10 × A\n"
            "+/ B\n"
            ")VARS\n"
            ")SAVE\n"
            ")CLEAR\n"
            ")LOAD VAXCALC\n"
            "B\n"
            ")EXIT\n"
        )
        r = subprocess.run([VAXAPL_BIN, "--interactive"], input=stdin_cmds, capture_output=True, text=True, cwd=str(tmp_path))
        assert r.returncode == 0
        assert "DEC VAX APL V3.1-00 [VAX/VMS] — CLEAR WS" in r.stdout
        assert "WAS CLEAR WS" in r.stdout
        assert "150" in r.stdout
        assert "A B" in r.stdout
        assert "10 20 30 40 50" in r.stdout

    def test_04_user_defined_del_functions_in_repl(self, tmp_path):
        stdin_cmds = (
            "∇ R ← X HYPOT Y\n"
            "R ← (X × X) + (Y × Y)\n"
            "∇\n"
            ")FNS\n"
            "3 HYPOT 4\n"
            ")OFF\n"
        )
        r = subprocess.run([VAXAPL_BIN], input=stdin_cmds, capture_output=True, text=True, cwd=str(tmp_path))
        assert r.returncode == 0
        assert "HYPOT" in r.stdout
        assert "25" in r.stdout
