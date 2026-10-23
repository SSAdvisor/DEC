#!/usr/bin/env python3
"""
Automated Pytest Suite for DEC VAX Ada V2.2 Compiler (vaxada)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXADA_BIN = os.path.join(ROOT_DIR, "compiler", "vaxada")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXAdaCompiler:
    def test_01_compile_demo_obj_and_lst(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.ADA")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r = subprocess.run([VAXADA_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r.returncode == 0
        assert "VAX ADA V2.2-00: Compiled DEMO.ADA -> DEMO.OBJ (0 errors)" in r.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "DEC VAX ADA V2.2-00"
        assert obj_data["ident"] == "V02-02"
        assert len(obj_data["bytecode"]) > 20

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "DEC VAX ADA V2.2-00 (VAX/VMS V5.5-2)" in lst_text
        assert "Storage Allocation & Symbol Map:" in lst_text

    def test_02_link_and_run_demo_exe(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.ADA")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        assert subprocess.run([VAXADA_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True).returncode == 0
        assert os.path.isfile(exe)
        assert os.path.isfile(map_f)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX ADA V2.2 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "EMPLOYEE:    DR. JEAN ICHBIAH" in r_run.stdout
        assert "BONUS:       17100" in r_run.stdout
        assert "TOTAL COMP:  112100" in r_run.stdout
        assert "AUDIT SCORE: 300 (MIL-STD-1815A GRADE A)" in r_run.stdout

    def test_03_loops_reverse_while_and_exit_when(self, tmp_path):
        src = os.path.join(str(tmp_path), "LOOPS.ADA")
        obj = os.path.join(str(tmp_path), "LOOPS.OBJ")
        exe = os.path.join(str(tmp_path), "LOOPS.EXE")

        with open(src, "w") as f:
            f.write(
                "-- Ada loop constructs test\n"
                "with TEXT_IO; use TEXT_IO;\n"
                "procedure LOOPS is\n"
                "    RSUM : Integer := 0;\n"
                "    WSUM : Integer := 0;\n"
                "    LSUM : Integer := 0;\n"
                "    K    : Integer := 1;\n"
                "begin\n"
                "    for I in reverse 1 .. 4 loop\n"
                "        RSUM := RSUM + I;\n"
                "    end loop;\n"
                "    while K <= 3 loop\n"
                "        WSUM := WSUM + (K * 10);\n"
                "        K := K + 1;\n"
                "    end loop;\n"
                "    K := 1;\n"
                "    loop\n"
                "        LSUM := LSUM + K;\n"
                "        K := K + 1;\n"
                "        exit when K > 5;\n"
                "    end loop;\n"
                "    Put_Line(\"RSUM=\" & Integer'Image(RSUM) & \" WSUM=\" & Integer'Image(WSUM) & \" LSUM=\" & Integer'Image(LSUM));\n"
                "end LOOPS;\n"
            )

        assert subprocess.run([VAXADA_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "RSUM=10 WSUM=60 LSUM=15" in r_run.stdout

    def test_04_if_elsif_else_and_arrays(self, tmp_path):
        src = os.path.join(str(tmp_path), "BRANCH.ADA")
        obj = os.path.join(str(tmp_path), "BRANCH.OBJ")
        lst = os.path.join(str(tmp_path), "BRANCH.LST")
        exe = os.path.join(str(tmp_path), "BRANCH.EXE")

        with open(src, "w") as f:
            f.write(
                "with TEXT_IO; use TEXT_IO;\n"
                "procedure BRANCH is\n"
                "    type Int_Vec is array (1 .. 4) of Integer;\n"
                "    V   : Int_Vec;\n"
                "    VAL : Integer := 75;\n"
                "    TAG : String(1 .. 10);\n"
                "begin\n"
                "    V(1) := 11;\n"
                "    V(2) := 22;\n"
                "    if VAL >= 90 then\n"
                "        TAG := \"A-TIER\";\n"
                "    elsif VAL >= 70 then\n"
                "        TAG := \"B-TIER\";\n"
                "    else\n"
                "        TAG := \"C-TIER\";\n"
                "    end if;\n"
                "    Put(\"VSUM=\" & Integer'Image(V(1) + V(2)));\n"
                "    Put_Line(\" TAG=\" & TAG);\n"
                "end BRANCH;\n"
            )

        assert subprocess.run([VAXADA_BIN, src, f"/OBJECT={obj}", f"/LIST={lst}"], capture_output=True).returncode == 0
        assert os.path.isfile(lst)
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "VSUM=33 TAG=B-TIER" in r_run.stdout
