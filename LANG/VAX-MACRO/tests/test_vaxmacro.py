#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX MACRO V05-00 Assembler (vaxmacro)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXMACRO_BIN = os.path.join(ROOT_DIR, "compiler", "vaxmacro")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXMacroAssembler:
    def test_01_assemble_link_and_run_demo_mar(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.MAR")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        r_asm = subprocess.run([VAXMACRO_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_asm.returncode == 0
        assert "VAX MACRO V05-00: Assembled DEMO.MAR -> DEMO.OBJ (0 errors)" in r_asm.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "DEC VAX MACRO V05-00"
        assert obj_data["ident"] == "V05-00"
        assert "START" in obj_data["symbols"]

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "VAX MACRO V05-00" in lst_text
        assert "Program Section Synopsis:" in lst_text
        assert "$CODE" in lst_text
        assert "$DATA" in lst_text

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX MACRO V05-00 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "FACTORIAL(7) VIA SOBGTR   = 5040" in r_run.stdout
        assert "ARRAY SUM(0..4) VIA AOBLSS = 1800" in r_run.stdout
        assert "32-BIT ARITH (SUBL3/DIVL3) = 360" in r_run.stdout

    def test_02_branches_comparisons_and_bitwise_ops(self, tmp_path):
        src = os.path.join(str(tmp_path), "BRANCH.MAR")
        obj = os.path.join(str(tmp_path), "BRANCH.OBJ")
        exe = os.path.join(str(tmp_path), "BRANCH.EXE")

        with open(src, "w") as f:
            f.write(
                "        .TITLE  BRTEST\n"
                "        .IDENT  /V01-02/\n"
                "        .ENTRY  MAIN, ^M<R2,R3,R4>\n"
                "        MOVL    #^X00FF, R2\n"
                "        BISL2   #^X0F00, R2\n"
                "        XORL2   #^X000F, R2\n"
                "        CMPL    R2, #^X0FF0\n"
                "        BNEQ    FAIL\n"
                "        MNEGL   #42, R3\n"
                "        TSTL    R3\n"
                "        BGEQ    FAIL\n"
                "        .PRINT  /BRANCH & BITWISE OK/\n"
                "        PRTINT  /R2_DEC=/, R2\n"
                "        BRB     DONE\n"
                "FAIL:   .PRINT  /FAIL/\n"
                "DONE:   RET\n"
                "        .END    MAIN\n"
            )

        assert subprocess.run([VAXMACRO_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "BRANCH & BITWISE OK" in r_run.stdout
        assert "R2_DEC=4080" in r_run.stdout

    def test_03_user_macro_expansion_and_sobgeq_aobleq(self, tmp_path):
        src = os.path.join(str(tmp_path), "MACEXP.MAR")
        obj = os.path.join(str(tmp_path), "MACEXP.OBJ")
        lst = os.path.join(str(tmp_path), "MACEXP.LST")
        exe = os.path.join(str(tmp_path), "MACEXP.EXE")

        with open(src, "w") as f:
            f.write(
                "        .TITLE  MACEXP\n"
                "        .MACRO  ADD_TRIPLE A, B, DST\n"
                "        ADDL3   A, B, DST\n"
                "        MULL2   #3, DST\n"
                "        .ENDM\n"
                "        .ENTRY  START, 0\n"
                "        ADD_TRIPLE #10, #15, R0\n"
                "        PRTINT  /TRIPLE=/, R0\n"
                "        CLRL    R1\n"
                "        CLRL    R2\n"
                "LP:     ADDL2   R1, R2\n"
                "        AOBLEQ  #4, R1, LP\n"
                "        PRTINT  /AOBLEQ_SUM=/, R2\n"
                "        RET\n"
                "        .END    START\n"
            )

        assert subprocess.run([VAXMACRO_BIN, src, f"/OBJECT={obj}", f"/LIST={lst}"], capture_output=True).returncode == 0
        assert os.path.isfile(lst)
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "TRIPLE=75" in r_run.stdout
        assert "AOBLEQ_SUM=10" in r_run.stdout

    def test_04_multi_module_calls_linking(self, tmp_path):
        main_mar = os.path.join(str(tmp_path), "MAINM.MAR")
        sub_mar = os.path.join(str(tmp_path), "SUBM.MAR")
        main_obj = os.path.join(str(tmp_path), "MAINM.OBJ")
        sub_obj = os.path.join(str(tmp_path), "SUBM.OBJ")
        exe = os.path.join(str(tmp_path), "MULTI.EXE")

        with open(main_mar, "w") as f:
            f.write(
                "        .TITLE  MAINM\n"
                "        .ENTRY  START, 0\n"
                "        .PRINT  /MAIN MODULE ENTERED/\n"
                "        CALLS   #0, G^SUBM\n"
                "        .PRINT  /MAIN MODULE EXITING/\n"
                "        RET\n"
                "        .END    START\n"
            )
        with open(sub_mar, "w") as f:
            f.write(
                "        .TITLE  SUBM\n"
                "        .ENTRY  SUBM, 0\n"
                "        .PRINT  /EXTERNAL SUBM EXECUTED/\n"
                "        RET\n"
                "        .END\n"
            )

        assert subprocess.run([VAXMACRO_BIN, main_mar, "-o", main_obj], capture_output=True).returncode == 0
        assert subprocess.run([VAXMACRO_BIN, sub_mar, "-o", sub_obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, main_obj, sub_obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "MAIN MODULE ENTERED" in r_run.stdout
        assert "EXTERNAL SUBM EXECUTED" in r_run.stdout
        assert "MAIN MODULE EXITING" in r_run.stdout
