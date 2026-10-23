#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX BLISS-16 V4.2 Compiler (bliss16)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLISS16_BIN = os.path.join(ROOT_DIR, "compiler", "bliss16")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXBliss16Compiler:
    def test_01_compile_link_and_run_demo_b16(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.B16")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        r_comp = subprocess.run([BLISS16_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX BLISS-16 V4.2-00: Compiled DEMO.B16 -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "VAX BLISS-16 V4.2"
        assert obj_data["ident"] == "V04-02"
        assert "B16_MAIN" in obj_data["symbols"]

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "DEC VAX BLISS-16 V4.2-00" in lst_text

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX BLISS-16 V4.2 ON VAX/VMS V5.5-2 (16-BIT)" in r_run.stdout
        assert "UNIBUS RX_RING TOTAL BYTES = 640" in r_run.stdout
        assert "16-BIT PACKET CRC          = 1408" in r_run.stdout
        assert "DEVICE CSR STATUS          = CSR_READY (ONLINE)" in r_run.stdout

    def test_02_16bit_word_literals_and_decr_loops(self, tmp_path):
        src = os.path.join(str(tmp_path), "WORD16.B16")
        obj = os.path.join(str(tmp_path), "WORD16.OBJ")
        exe = os.path.join(str(tmp_path), "WORD16.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE WORD16 (MAIN = START16) =\n"
                "BEGIN\n"
                "GLOBAL ROUTINE START16 : NOVALUE =\n"
                "BEGIN\n"
                "    LOCAL N, PROD, NEG16;\n"
                "    PROD = 1;\n"
                "    DECR N FROM 5 TO 1 DO\n"
                "        PROD = .PROD * .N;\n"
                "    NEG16 = %X'FFFF';\n"
                "    TTY_PUT_MSG('FACT5=', .PROD, ' FFFF_16=', .NEG16);\n"
                "END;\n"
                "END ELUDOM\n"
            )

        assert subprocess.run([BLISS16_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "FACT5=120 FFFF_16=-1" in r_run.stdout

    def test_03_selectone_and_routines_b16(self, tmp_path):
        src = os.path.join(str(tmp_path), "SEL16.BLI")
        obj = os.path.join(str(tmp_path), "SEL16.OBJ")
        exe = os.path.join(str(tmp_path), "SEL16.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE SEL16 (MAIN = MAIN) =\n"
                "BEGIN\n"
                "ROUTINE SCALE16 (X) = (.X * 16);\n"
                "GLOBAL ROUTINE MAIN : NOVALUE =\n"
                "BEGIN\n"
                "    LOCAL V, MSG;\n"
                "    V = SCALE16(4);\n"
                "    SELECTONE .V OF\n"
                "    SET\n"
                "        [16, 32]: MSG = 'LOW';\n"
                "        [64]:     MSG = 'EXACT_64';\n"
                "        [OTHERWISE]: MSG = 'OTHER';\n"
                "    TES;\n"
                "    PRINT('V=', .V, ' MSG=', .MSG);\n"
                "END;\n"
                "END ELUDOM\n"
            )

        assert subprocess.run([BLISS16_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "V=64 MSG=EXACT_64" in r_run.stdout

    def test_04_response_file_and_default_listing(self, tmp_path):
        src = os.path.join(str(tmp_path), "RSP16.B16")
        rsp = os.path.join(str(tmp_path), "BUILD.RSP")
        obj = os.path.join(str(tmp_path), "RSP16.OBJ")
        lst = os.path.join(str(tmp_path), "RSP16.LST")
        exe = os.path.join(str(tmp_path), "RSP16.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE RSP16 (MAIN = M) =\n"
                "BEGIN\n"
                "GLOBAL ROUTINE M : NOVALUE = LIB$PUT_OUTPUT('BLISS-16 RSP OK');\n"
                "END ELUDOM\n"
            )
        with open(rsp, "w") as f:
            f.write(f"{src}\n/OBJECT={obj}\n/LIST={lst}\n")

        assert subprocess.run([BLISS16_BIN, f"@{rsp}"], capture_output=True).returncode == 0
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "BLISS-16 RSP OK" in r_run.stdout
