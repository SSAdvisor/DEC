#!/usr/bin/env python3
"""
Automated Pytest Suite for DEC VAX Pascal V4.3 Compiler (vaxpas)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXPAS_BIN = os.path.join(ROOT_DIR, "compiler", "vaxpas")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXPascalCompiler:
    def test_01_compile_demo_obj_and_lst(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.PAS")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r = subprocess.run([VAXPAS_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r.returncode == 0
        assert "VAX PASCAL V4.3-00: Compiled DEMO.PAS -> DEMO.OBJ (0 errors)" in r.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "DEC VAX PASCAL V4.3-00"
        assert obj_data["ident"] == "V04-03"
        assert len(obj_data["bytecode"]) > 20

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "DEC VAX PASCAL V4.3-00 (VAX/VMS V5.5-2)" in lst_text
        assert "Storage Allocation & Symbol Map:" in lst_text

    def test_02_link_and_run_demo_exe(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.PAS")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        assert subprocess.run([VAXPAS_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True).returncode == 0
        assert os.path.isfile(exe)
        assert os.path.isfile(map_f)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX PASCAL V4.3 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "EMPLOYEE:    DR. NIKLAUS WIRTH" in r_run.stdout
        assert "BONUS:       12600" in r_run.stdout
        assert "TOTAL COMP:  96600" in r_run.stdout
        assert "SCORE SUM:   150 (OUTSTANDING)" in r_run.stdout

    def test_03_loops_while_repeat_downto_and_comments(self, tmp_path):
        src = os.path.join(str(tmp_path), "LOOPS.PAS")
        obj = os.path.join(str(tmp_path), "LOOPS.OBJ")
        exe = os.path.join(str(tmp_path), "LOOPS.EXE")

        with open(src, "w") as f:
            f.write(
                "(* VAX Pascal loop test *)\n"
                "[IDENT('V04-03')]\n"
                "PROGRAM LOOPTEST(INPUT, OUTPUT);\n"
                "VAR\n"
                "    I, WSUM, RSUM, DSUM : INTEGER;\n"
                "BEGIN\n"
                "    { Test WHILE loop }\n"
                "    I := 1; WSUM := 0;\n"
                "    WHILE I <= 4 DO\n"
                "    BEGIN\n"
                "        WSUM := WSUM + I;\n"
                "        I := I + 1;\n"
                "    END;\n"
                "    { Test REPEAT UNTIL loop }\n"
                "    I := 1; RSUM := 0;\n"
                "    REPEAT\n"
                "        RSUM := RSUM + (I * 2);\n"
                "        I := I + 1;\n"
                "    UNTIL I > 3;\n"
                "    { Test FOR DOWNTO loop }\n"
                "    DSUM := 0;\n"
                "    FOR I := 5 DOWNTO 1 DO\n"
                "        DSUM := DSUM + I;\n"
                "    WRITELN('WSUM=', WSUM, ' RSUM=', RSUM, ' DSUM=', DSUM);\n"
                "END.\n"
            )

        assert subprocess.run([VAXPAS_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "WSUM=10 RSUM=12 DSUM=15" in r_run.stdout

    def test_04_functions_procedures_and_case_otherwise(self, tmp_path):
        src = os.path.join(str(tmp_path), "FUNCS.PAS")
        obj = os.path.join(str(tmp_path), "FUNCS.OBJ")
        lst = os.path.join(str(tmp_path), "FUNCS.LST")
        exe = os.path.join(str(tmp_path), "FUNCS.EXE")

        with open(src, "w") as f:
            f.write(
                "PROGRAM FUNCTEST(OUTPUT);\n"
                "VAR\n"
                "    X, Y : INTEGER;\n"
                "    TAG  : STRING;\n"
                "FUNCTION SQUARE(N : INTEGER) : INTEGER;\n"
                "BEGIN\n"
                "    SQUARE := N * N;\n"
                "END;\n"
                "BEGIN\n"
                "    X := SQUARE(7);\n"
                "    Y := 999;\n"
                "    CASE Y OF\n"
                "        1, 2: TAG := 'LOW';\n"
                "        10..20: TAG := 'MID';\n"
                "        OTHERWISE TAG := 'HIGH';\n"
                "    END;\n"
                "    WRITE('SQ=', X, ' ');\n"
                "    WRITELN('TAG=', TAG);\n"
                "END.\n"
            )

        assert subprocess.run([VAXPAS_BIN, src, f"/OBJECT={obj}", f"/LIST={lst}"], capture_output=True).returncode == 0
        assert os.path.isfile(lst)
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "SQ=49 TAG=HIGH" in r_run.stdout
