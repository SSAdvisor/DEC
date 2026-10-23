#!/usr/bin/env python3
"""
Automated Pytest Suite for DEC VAX PL/I V3.5 Compiler (vaxpli)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXPLI_BIN = os.path.join(ROOT_DIR, "compiler", "vaxpli")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXPLICompiler:
    def test_01_compile_demo_obj_and_lst(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.PLI")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r = subprocess.run([VAXPLI_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r.returncode == 0
        assert "VAX PL/I V3.5-00: Compiled DEMO.PLI -> DEMO.OBJ (0 errors)" in r.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "DEC VAX PL/I V3.5-00"
        assert obj_data["ident"] == "V03-05"
        assert len(obj_data["bytecode"]) > 20

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "DEC VAX PL/I V3.5-00 (VAX/VMS V5.5-2)" in lst_text
        assert "Storage Allocation & Symbol Map:" in lst_text

    def test_02_link_and_run_demo_exe(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.PLI")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        assert subprocess.run([VAXPLI_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True).returncode == 0
        assert os.path.isfile(exe)
        assert os.path.isfile(map_f)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX PL/I V3.5 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "EMPLOYEE:    DR. FERNANDO CORBATO" in r_run.stdout
        assert "BONUS:       18400" in r_run.stdout
        assert "TOTAL COMP:  110400" in r_run.stdout
        assert "QTR INDEX:   250 [DISTINGUISHED]" in r_run.stdout

    def test_03_do_while_until_and_concat(self, tmp_path):
        src = os.path.join(str(tmp_path), "LOOPS.PLI")
        obj = os.path.join(str(tmp_path), "LOOPS.OBJ")
        exe = os.path.join(str(tmp_path), "LOOPS.EXE")

        with open(src, "w") as f:
            f.write(
                "/* PL/I DO WHILE and DO UNTIL test */\n"
                "LOOPMOD: PROCEDURE OPTIONS(MAIN);\n"
                "    DCL I FIXED BIN(31) INIT(1);\n"
                "    DCL WACC FIXED BIN(31) INIT(0);\n"
                "    DCL UACC FIXED BIN(31) INIT(0);\n"
                "    DCL MSG CHAR(32) VAR INIT('VAX');\n"
                "    DO WHILE(I <= 4);\n"
                "        WACC = WACC + I;\n"
                "        I = I + 1;\n"
                "    END;\n"
                "    I = 1;\n"
                "    DO UNTIL(I > 3);\n"
                "        UACC = UACC + (I * 10);\n"
                "        I = I + 1;\n"
                "    END;\n"
                "    MSG = MSG || '-PLI';\n"
                "    PUT SKIP LIST('WACC=', WACC, ' UACC=', UACC, ' MSG=', MSG);\n"
                "END LOOPMOD;\n"
            )

        assert subprocess.run([VAXPLI_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "WACC=10 UACC=60 MSG=VAX-PLI" in r_run.stdout

    def test_04_select_when_otherwise_and_arrays(self, tmp_path):
        src = os.path.join(str(tmp_path), "ARRSEL.PLI")
        obj = os.path.join(str(tmp_path), "ARRSEL.OBJ")
        lst = os.path.join(str(tmp_path), "ARRSEL.LST")
        exe = os.path.join(str(tmp_path), "ARRSEL.EXE")

        with open(src, "w") as f:
            f.write(
                "ARRSEL: PROCEDURE OPTIONS(MAIN);\n"
                "    DCL VEC(5) FIXED BIN(31);\n"
                "    DCL K FIXED BIN(15);\n"
                "    DCL TOT FIXED BIN(31) INIT(0);\n"
                "    DCL STATUS CHAR(16) VAR;\n"
                "    DO K = 1 TO 3;\n"
                "        VEC(K) = K * 5;\n"
                "        TOT = TOT + VEC(K);\n"
                "    END;\n"
                "    SELECT (TOT);\n"
                "        WHEN (10) STATUS = 'TEN';\n"
                "        WHEN (30) STATUS = 'THIRTY';\n"
                "        OTHERWISE STATUS = 'OTHER';\n"
                "    END;\n"
                "    PUT SKIP LIST('TOT=', TOT, ' STATUS=', STATUS);\n"
                "END ARRSEL;\n"
            )

        assert subprocess.run([VAXPLI_BIN, src, f"/OBJECT={obj}", f"/LIST={lst}"], capture_output=True).returncode == 0
        assert os.path.isfile(lst)
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "TOT=30 STATUS=THIRTY" in r_run.stdout
