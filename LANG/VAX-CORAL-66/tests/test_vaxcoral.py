#!/usr/bin/env python3
"""
Automated Pytest Suite for DEC VAX CORAL 66 V2.1 Compiler (vaxcoral)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXCORAL_BIN = os.path.join(ROOT_DIR, "compiler", "vaxcoral")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXCoral66Compiler:
    def test_01_compile_demo_obj_and_lst(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.COR")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r = subprocess.run([VAXCORAL_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r.returncode == 0
        assert "VAX CORAL 66 V2.1-00: Compiled DEMO.COR -> DEMO.OBJ (0 errors)" in r.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "DEC VAX CORAL 66 V2.1-00"
        assert obj_data["ident"] == "V02-01"
        assert len(obj_data["bytecode"]) > 20

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "DEC VAX CORAL 66 V2.1-00 (VAX/VMS V5.5-2)" in lst_text
        assert "Storage Allocation & Symbol Map:" in lst_text

    def test_02_link_and_run_demo_exe(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.COR")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        assert subprocess.run([VAXCORAL_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True).returncode == 0
        assert os.path.isfile(exe)
        assert os.path.isfile(map_f)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX CORAL 66 V2.1 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "EMPLOYEE:    SIR IAN CURRIE (RRE MALVERN)" in r_run.stdout
        assert "ALLOWANCE:   10200" in r_run.stdout
        assert "TOTAL COMP:  95200" in r_run.stdout
        assert "TELEMETRY:   450" in r_run.stdout

    def test_03_unstropped_coral66_and_for_until(self, tmp_path):
        src = os.path.join(str(tmp_path), "UNSTROP.COR")
        obj = os.path.join(str(tmp_path), "UNSTROP.OBJ")
        exe = os.path.join(str(tmp_path), "UNSTROP.EXE")

        with open(src, "w") as f:
            f.write(
                "COMMENT Unstropped CORAL 66 test program ;\n"
                "% Single-line comment test\n"
                "PROGRAM UNSTROP;\n"
                "BEGIN\n"
                "    INTEGER I, USUM, WSUM;\n"
                "    USUM := 0;\n"
                "    FOR I := 1 STEP 1 UNTIL I > 4 DO\n"
                "        USUM := USUM + (I * 5);\n"
                "    I := 1; WSUM := 0;\n"
                "    WHILE I <= 3 DO\n"
                "    BEGIN\n"
                "        WSUM := WSUM + I;\n"
                "        I := I + 1;\n"
                "    END;\n"
                "    WRITE_TEXT(\"USUM=\"); PRINT_VALUE(USUM);\n"
                "    WRITE_TEXT(\" WSUM=\"); PRINT_VALUE(WSUM); NEWLINE;\n"
                "END\n"
                "FINISH\n"
            )

        assert subprocess.run([VAXCORAL_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "USUM=50 WSUM=6" in r_run.stdout

    def test_04_switch_goto_and_left_arrow_assign(self, tmp_path):
        src = os.path.join(str(tmp_path), "SWITCHT.COR")
        obj = os.path.join(str(tmp_path), "SWITCHT.OBJ")
        lst = os.path.join(str(tmp_path), "SWITCHT.LST")
        exe = os.path.join(str(tmp_path), "SWITCHT.EXE")

        with open(src, "w") as f:
            f.write(
                "'PROGRAM' SWITCHTEST;\n"
                "'BEGIN'\n"
                "    'INTEGER' MODE, CODE;\n"
                "    'SWITCH' JUMP_TBL := LBL_ONE, LBL_TWO, LBL_THREE;\n"
                "    MODE ← 2;\n"
                "    'GOTO' JUMP_TBL[MODE];\n"
                "LBL_ONE:\n"
                "    CODE ← 111;\n"
                "    'GOTO' DONE;\n"
                "LBL_TWO:\n"
                "    CODE ← 222;\n"
                "    'GOTO' DONE;\n"
                "LBL_THREE:\n"
                "    CODE ← 333;\n"
                "DONE:\n"
                "    WRITE_TEXT(\"SWITCH_CODE=\"); PRINT_VALUE(CODE); NEWLINE;\n"
                "'END'\n"
                "'FINISH'\n"
            )

        assert subprocess.run([VAXCORAL_BIN, src, f"/OBJECT={obj}", f"/LIST={lst}"], capture_output=True).returncode == 0
        assert os.path.isfile(lst)
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "SWITCH_CODE=222" in r_run.stdout
