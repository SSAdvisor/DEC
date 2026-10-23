#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX BASIC V3.5 (vaxbasic) & OpenVMS Linker V05-05 (vmslink)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXBASIC_BIN = os.path.join(ROOT_DIR, "compiler", "vaxbasic")
VMSLINK_BIN = os.path.join(ROOT_DIR, "linker", "vmslink")


class TestVAXBasicAndOpenVMSLinker:
    def test_01_compile_and_link_vaxdemo_with_opt_and_map(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "VAXDEMO.BAS")
        opt = os.path.join(ROOT_DIR, "samples", "VAXDEMO.OPT")
        obj = os.path.join(str(tmp_path), "VAXDEMO.OBJ")
        lst = os.path.join(str(tmp_path), "VAXDEMO.LST")
        exe = os.path.join(str(tmp_path), "VAXDEMO.EXE")
        map_f = os.path.join(str(tmp_path), "VAXDEMO.MAP")

        r_comp = subprocess.run([VAXBASIC_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX BASIC V3.5-00: Compiled VAXDEMO.BAS -> VAXDEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj, opt], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)
        assert os.path.isfile(map_f)

        with open(map_f, "r") as f:
            map_text = f.read()
        assert "OpenVMS VAX Linker V05-05 Image Map" in map_text
        assert "VAXDEMO" in map_text
        assert "V03-05" in map_text
        assert "$CODE" in map_text

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "RSTS/E VM Init" not in r_run.stdout
        assert "DEC VAX BASIC V3.5 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "EMPLOYEE:   DR. GORDON BELL" in r_run.stdout
        assert "DEPARTMENT: VAX ARCHITECTURE & VMS KERNEL" in r_run.stdout
        assert "TOTAL COMP: 97750" in r_run.stdout

    def test_02_structured_loops_when_error_and_select_ranges(self, tmp_path):
        src_p = os.path.join(str(tmp_path), "FLOW.BAS")
        obj_p = os.path.join(str(tmp_path), "FLOW.OBJ")
        exe_p = os.path.join(str(tmp_path), "FLOW.EXE")

        with open(src_p, "w") as f:
            f.write(
                "PROGRAM FLOW\n"
                "    DECLARE LONG I, ACC, GRADE\n"
                "    DECLARE STRING RATING$\n"
                "    ACC = 0\n"
                "    I = 1\n"
                "    WHILE I <= 5\n"
                "        ACC = ACC + I\n"
                "        I = I + 1\n"
                "    NEXT\n"
                "    GRADE = 88\n"
                "    SELECT GRADE\n"
                "        CASE 90 TO 100\n"
                "            RATING$ = 'EXCELLENT'\n"
                "        CASE 80 TO 89\n"
                "            RATING$ = 'HONORS'\n"
                "        CASE ELSE\n"
                "            RATING$ = 'PASS'\n"
                "    END SELECT\n"
                "    PRINT 'WHILE_ACC='; ACC; ' RATING='; RATING$\n"
                "END PROGRAM\n"
            )

        assert subprocess.run([VAXBASIC_BIN, src_p, "-o", obj_p], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe_p, obj_p], capture_output=True).returncode == 0
        r_run = subprocess.run([exe_p], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "WHILE_ACC=15 RATING=HONORS" in r_run.stdout

    def test_03_openvms_linker_multi_module_and_olb_library(self, tmp_path):
        main_bas = os.path.join(str(tmp_path), "MAINMOD.BAS")
        sub_bas = os.path.join(str(tmp_path), "TAXMOD.BAS")
        main_obj = os.path.join(str(tmp_path), "MAINMOD.OBJ")
        sub_obj = os.path.join(str(tmp_path), "TAXMOD.OBJ")
        olb_file = os.path.join(str(tmp_path), "FINLIB.OLB")
        exe_file = os.path.join(str(tmp_path), "FINAPP.EXE")

        with open(main_bas, "w") as f:
            f.write(
                "PROGRAM MAINMOD\n"
                "    PRINT 'MAINMOD STARTING'\n"
                "    CALL TAXMOD\n"
                "    PRINT 'MAINMOD COMPLETE'\n"
                "END PROGRAM\n"
            )
        with open(sub_bas, "w") as f:
            f.write(
                "PROGRAM TAXMOD\n"
                "    PRINT 'TAXMOD EXECUTED FROM OLB LIBRARY'\n"
                "END PROGRAM\n"
            )

        assert subprocess.run([VAXBASIC_BIN, main_bas, "-o", main_obj], capture_output=True).returncode == 0
        assert subprocess.run([VAXBASIC_BIN, sub_bas, "-o", sub_obj], capture_output=True).returncode == 0

        with open(sub_obj, "r") as f:
            sub_mod_data = json.load(f)
        with open(olb_file, "w") as f:
            json.dump({"library": "FINLIB", "modules": {"TAXMOD": sub_mod_data}}, f, indent=2)

        # Link MAINMOD.OBJ against FINLIB.OLB/LIBRARY
        r_link = subprocess.run([VMSLINK_BIN, "-o", exe_file, f"{main_obj},{olb_file}/LIBRARY"], capture_output=True, text=True)
        assert r_link.returncode == 0
        r_run = subprocess.run([exe_file], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "MAINMOD STARTING" in r_run.stdout
        assert "TAXMOD EXECUTED FROM OLB LIBRARY" in r_run.stdout
        assert "MAINMOD COMPLETE" in r_run.stdout

    def test_04_interactive_vax_basic_repl(self, tmp_path):
        r_repl = subprocess.run(
            [VAXBASIC_BIN, "--interactive"],
            input='NEW TESTPROG\n10 PRINT "INTERACTIVE VAX BASIC OK"\n20 END\nLIST\nRUN\nEXIT\n',
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r_repl.returncode == 0
        assert "VAX BASIC V3.5-00" in r_repl.stdout
        assert "Ready" in r_repl.stdout
        assert "INTERACTIVE VAX BASIC OK" in r_repl.stdout
