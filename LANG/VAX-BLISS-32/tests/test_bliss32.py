#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX BLISS-32 V4.7 Compiler (bliss32)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLISS32_BIN = os.path.join(ROOT_DIR, "compiler", "bliss32")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXBliss32Compiler:
    def test_01_compile_link_and_run_demo_b32(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.B32")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        r_comp = subprocess.run([BLISS32_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX BLISS-32 V4.7-00: Compiled DEMO.B32 -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "VAX BLISS-32 V4.7"
        assert obj_data["ident"] == "V04-07"
        assert "START_KERNEL" in obj_data["symbols"]

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "DEC VAX BLISS-32 V4.7-00" in lst_text
        assert "PSECT & Symbol Storage Map:" in lst_text

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX BLISS-32 V4.7 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "PAGE_TABLE VECTOR SUM (0..4) = 1500" in r_run.stdout
        assert "KERNEL CHECKSUM              = 5524" in r_run.stdout
        assert "SCHEDULER CLASS              = ELEVATED VAX SYSTEM PRIORITY" in r_run.stdout
        assert "GLOBAL_TICKS (.OWN)          = 4096" in r_run.stdout

    def test_02_decr_while_until_and_leave_blocks(self, tmp_path):
        src = os.path.join(str(tmp_path), "FLOW.B32")
        obj = os.path.join(str(tmp_path), "FLOW.OBJ")
        exe = os.path.join(str(tmp_path), "FLOW.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE FLOW (IDENT = 'V01-00', MAIN = MAIN) =\n"
                "BEGIN\n"
                "GLOBAL ROUTINE MAIN : NOVALUE =\n"
                "BEGIN\n"
                "    LOCAL K, ACC, W;\n"
                "    ACC = 0;\n"
                "    DECR K FROM 10 TO 2 BY 2 DO\n"
                "        ACC = .ACC + .K;\n"
                "    W = 1;\n"
                "    SEARCH_BLK : BEGIN\n"
                "        WHILE .W LSS 100 DO\n"
                "        BEGIN\n"
                "            W = .W * 2;\n"
                "            IF .W GEQ 32 THEN LEAVE SEARCH_BLK;\n"
                "        END;\n"
                "    END;\n"
                "    TTY_PUT_MSG('DECR_ACC=', .ACC, ' LEAVE_W=', .W);\n"
                "END;\n"
                "END ELUDOM\n"
            )

        assert subprocess.run([BLISS32_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DECR_ACC=30 LEAVE_W=32" in r_run.stdout

    def test_03_radix_literals_uplit_and_if_expressions(self, tmp_path):
        src = os.path.join(str(tmp_path), "EXPR.BLI")
        obj = os.path.join(str(tmp_path), "EXPR.OBJ")
        exe = os.path.join(str(tmp_path), "EXPR.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE EXPR (MAIN = RUN_EXPR) =\n"
                "BEGIN\n"
                "BIND TBL = UPLIT(11, 22, 33, 44);\n"
                "ROUTINE MAX_VAL (A, B) = (IF .A GTR .B THEN .A ELSE .B);\n"
                "GLOBAL ROUTINE RUN_EXPR : NOVALUE =\n"
                "BEGIN\n"
                "    LOCAL HEX_V, OCT_V, M;\n"
                "    HEX_V = %X'0020';\n"
                "    OCT_V = %O'0010';\n"
                "    M = MAX_VAL(.TBL[2], .HEX_V + .OCT_V);\n"
                "    PRINT('MAX_VAL=', .M, ' TBL3=', .TBL[3]);\n"
                "END;\n"
                "END ELUDOM\n"
            )

        assert subprocess.run([BLISS32_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "MAX_VAL=40 TBL3=44" in r_run.stdout

    def test_04_multi_module_bliss32_linking(self, tmp_path):
        m1_src = os.path.join(str(tmp_path), "KERNEL.B32")
        m2_src = os.path.join(str(tmp_path), "DRIVER.B32")
        m1_obj = os.path.join(str(tmp_path), "KERNEL.OBJ")
        m2_obj = os.path.join(str(tmp_path), "DRIVER.OBJ")
        exe = os.path.join(str(tmp_path), "SYSIMG.EXE")

        with open(m1_src, "w") as f:
            f.write(
                "MODULE KERNEL (MAIN = INIT_SYS) =\n"
                "BEGIN\n"
                "EXTERNAL ROUTINE DRIVER;\n"
                "GLOBAL ROUTINE INIT_SYS : NOVALUE =\n"
                "BEGIN\n"
                "    LIB$PUT_OUTPUT('KERNEL: DISPATCHING TO DRIVER');\n"
                "    DRIVER();\n"
                "    LIB$PUT_OUTPUT('KERNEL: DRIVER RETURNED OK');\n"
                "END;\n"
                "END ELUDOM\n"
            )
        with open(m2_src, "w") as f:
            f.write(
                "MODULE DRIVER (MAIN = DRV_ENTRY) =\n"
                "BEGIN\n"
                "GLOBAL ROUTINE DRV_ENTRY : NOVALUE =\n"
                "BEGIN\n"
                "    LIB$PUT_OUTPUT('DRIVER: INITIALIZED UDA50 CONTROLLER');\n"
                "END;\n"
                "END ELUDOM\n"
            )

        assert subprocess.run([BLISS32_BIN, m1_src, "-o", m1_obj], capture_output=True).returncode == 0
        assert subprocess.run([BLISS32_BIN, m2_src, "-o", m2_obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, m1_obj, m2_obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "KERNEL: DISPATCHING TO DRIVER" in r_run.stdout
        assert "DRIVER: INITIALIZED UDA50 CONTROLLER" in r_run.stdout
        assert "KERNEL: DRIVER RETURNED OK" in r_run.stdout
