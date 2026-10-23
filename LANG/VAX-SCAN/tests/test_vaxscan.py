#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX SCAN V1.2-00 (vaxscan)
"""

import os
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXSCAN_BIN = os.path.join(ROOT_DIR, "compiler", "vaxscan")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXScanCompiler:
    def test_01_compile_and_link_demo_scn(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.SCN")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")

        r_comp = subprocess.run([VAXSCAN_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX SCAN V1.2-00: Compiled DEMO.SCN -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(lst, "r") as f:
            lst_txt = f.read()
        assert "DEC VAX SCAN V1.2-00" in lst_txt
        assert "Module: AUDIT_SCANNER" in lst_txt
        assert "TRIG_ON_DEC_NODE" in lst_txt

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX SCAN V1.2-00 — OPENVMS AUDIT LOG SCANNER" in r_run.stdout
        assert "NODE DETECTED: VAX780 (RAW=VAX780::)" in r_run.stdout
        assert "SECURITY EVENT #1 CODE=12" in r_run.stdout
        assert "NODE DETECTED: VAX8600 (RAW=VAX8600::)" in r_run.stdout
        assert "SECURITY EVENT #2 CODE=30" in r_run.stdout
        assert "SUMMARY: NODES=2 EVENTS=2 ERR_SUM=42" in r_run.stdout

    def test_02_sets_macros_tokens_and_dcl_qualifiers(self, tmp_path):
        src = os.path.join(str(tmp_path), "LEXER.SCN")
        obj = os.path.join(str(tmp_path), "LEXER.OBJ")
        lst = os.path.join(str(tmp_path), "LEXER.LST")
        exe = os.path.join(str(tmp_path), "LEXER.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE LEXER IDENT 'V01-00';\n"
                "    SET HEX := '0' .. '9' | 'A' .. 'F';\n"
                "    MACRO HEX_BYTE := '$' & { HEX }...;\n"
                "    DECLARE COUNT : INTEGER := 0;\n"
                "    TRIGGER GOT_HEX (H : STRING) := HEX_BYTE;\n"
                "        COUNT := COUNT + 1;\n"
                "        WRITE 'HEX[', COUNT, ']=', H;\n"
                "    END TRIGGER GOT_HEX;\n"
                "    PROCEDURE MAIN_ENTRY MAIN;\n"
                "        START SCAN INPUT STRING 'ADDR $1F AND $FF00 END';\n"
                "        END SCAN;\n"
                "    END PROCEDURE MAIN_ENTRY;\n"
                "END MODULE LEXER;\n"
            )

        r_comp = subprocess.run([VAXSCAN_BIN, src, f"/OBJECT={obj}", f"/LIST={lst}"], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "HEX[1]=$1F" in r_run.stdout
        assert "HEX[2]=$FF00" in r_run.stdout

    def test_03_control_flow_if_while_for_and_string_builtins(self, tmp_path):
        src = os.path.join(str(tmp_path), "FLOW.SCN")
        obj = os.path.join(str(tmp_path), "FLOW.OBJ")
        exe = os.path.join(str(tmp_path), "FLOW.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE FLOW IDENT 'V01-02';\n"
                "    DECLARE S : DYNAMIC STRING := 'OPEN' & 'VMS';\n"
                "    DECLARE I : INTEGER := 0;\n"
                "    DECLARE ACC : INTEGER := 0;\n"
                "    PROCEDURE TEST_FLOW MAIN;\n"
                "        FOR I := 1 TO 4 DO\n"
                "            ACC := ACC + I;\n"
                "        END FOR;\n"
                "        WHILE I > 1 DO\n"
                "            I := I - 1;\n"
                "        END WHILE;\n"
                "        IF INDEX(S, 'VMS') = 5 THEN\n"
                "            WRITE 'STR=', S, ' LEN=', LENGTH(S), ' ACC=', ACC, ' I=', I;\n"
                "        ELSE\n"
                "            WRITE 'FAIL';\n"
                "        END IF;\n"
                "    END PROCEDURE TEST_FLOW;\n"
                "END MODULE FLOW;\n"
            )

        assert subprocess.run([VAXSCAN_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "STR=OPENVMS LEN=7 ACC=10 I=1" in r_run.stdout

    def test_04_Alternation_and_optional_patterns(self, tmp_path):
        src = os.path.join(str(tmp_path), "PAT.SCN")
        obj = os.path.join(str(tmp_path), "PAT.OBJ")
        exe = os.path.join(str(tmp_path), "PAT.EXE")

        with open(src, "w") as f:
            f.write(
                "MODULE PAT IDENT 'V01-02';\n"
                "    SET DIG := '0' .. '9';\n"
                "    TOKEN QUAL := '/' & ('FULL' | 'BRIEF') & [ '=' & { DIG }... ];\n"
                "    TRIGGER ON_QUAL (Q : STRING) := QUAL;\n"
                "        WRITE 'QUALIFIER=', Q;\n"
                "    END TRIGGER ON_QUAL;\n"
                "    PROCEDURE RUN_PAT MAIN;\n"
                "        START SCAN INPUT STRING 'LINK /BRIEF /FULL=42';\n"
                "        END SCAN;\n"
                "    END PROCEDURE RUN_PAT;\n"
                "END MODULE PAT;\n"
            )

        assert subprocess.run([VAXSCAN_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "QUALIFIER=/BRIEF" in r_run.stdout
        assert "QUALIFIER=/FULL=42" in r_run.stdout
