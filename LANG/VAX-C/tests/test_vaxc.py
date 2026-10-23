#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX C V3.2 Compiler (vaxc)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXC_BIN = os.path.join(ROOT_DIR, "compiler", "vaxc")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXCCompiler:
    def test_01_compile_link_and_run_demo_c(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.C")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")
        map_f = os.path.join(str(tmp_path), "DEMO.MAP")

        r_comp = subprocess.run([VAXC_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX C V3.2-044: Compiled DEMO.C -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["creator"] == "DEC VAX C V3.2-044"
        assert obj_data["module"] == "VAXCDEMO"
        assert obj_data["ident"] == "V03-02"
        assert "MAIN" in obj_data["symbols"]

        with open(lst, "r") as f:
            lst_text = f.read()
        assert "DEC VAX C V3.2-044" in lst_text
        assert "Storage Allocation & Symbol Map:" in lst_text

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, "-m", map_f, "--full", obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX C V3.2-044 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "CLUSTER NODE      : VAX780::SYSMGR (ID=101)" in r_run.stdout
        assert "NODE ROLE         : PRIMARY VAXCLUSTER MASTER" in r_run.stdout
        assert "UPGRADED MIPS     : 1500" in r_run.stdout
        assert "WORKLOAD SUM(0..4): 2250" in r_run.stdout
        assert "VAXCLUSTER SCORE  : 13500" in r_run.stdout

    def test_02_do_while_while_break_continue_and_floats(self, tmp_path):
        src = os.path.join(str(tmp_path), "LOOPS.C")
        obj = os.path.join(str(tmp_path), "LOOPS.OBJ")
        exe = os.path.join(str(tmp_path), "LOOPS.EXE")

        with open(src, "w") as f:
            f.write(
                '#module LOOPS "V01-05"\n'
                "#include <stdio.h>\n"
                "int main() {\n"
                "    int k = 0, sum = 0;\n"
                "    while (k < 10) {\n"
                "        k++;\n"
                "        if (k == 3) continue;\n"
                "        if (k > 6) break;\n"
                "        sum += k;\n"
                "    }\n"
                "    int d = 1, prod = 1;\n"
                "    do {\n"
                "        prod *= d;\n"
                "        d++;\n"
                "    } while (d <= 5);\n"
                "    float ratio = 12.5;\n"
                "    printf(\"SUM=%d PROD=%d RATIO=%g\\n\", sum, prod, ratio);\n"
                "    return 0;\n"
                "}\n"
            )

        assert subprocess.run([VAXC_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        # k sums 1 + 2 + 4 + 5 + 6 = 18; prod = 5! = 120
        assert "SUM=18 PROD=120 RATIO=12.5" in r_run.stdout

    def test_03_string_functions_and_ternary_operator(self, tmp_path):
        src = os.path.join(str(tmp_path), "STRTEST.C")
        obj = os.path.join(str(tmp_path), "STRTEST.OBJ")
        exe = os.path.join(str(tmp_path), "STRTEST.EXE")

        with open(src, "w") as f:
            f.write(
                "#include <stdio.h>\n"
                "#include <string.h>\n"
                "int main() {\n"
                "    char buf[64];\n"
                "    strcpy(buf, \"OPEN\");\n"
                "    strcat(buf, \"VMS\");\n"
                "    int len = strlen(buf);\n"
                "    int eq = (strcmp(buf, \"OPENVMS\") == 0) ? 100 : 0;\n"
                "    puts(buf);\n"
                "    printf(\"LEN=%d EQ=%d\\n\", len, eq);\n"
                "    return 0;\n"
                "}\n"
            )

        assert subprocess.run([VAXC_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "OPENVMS" in r_run.stdout
        assert "LEN=7 EQ=100" in r_run.stdout

    def test_04_multi_module_c_and_bliss_interoperability(self, tmp_path):
        c_src = os.path.join(str(tmp_path), "MAINC.C")
        sub_src = os.path.join(str(tmp_path), "SUBC.C")
        c_obj = os.path.join(str(tmp_path), "MAINC.OBJ")
        sub_obj = os.path.join(str(tmp_path), "SUBC.OBJ")
        exe = os.path.join(str(tmp_path), "CAPP.EXE")

        with open(c_src, "w") as f:
            f.write(
                "#include <stdio.h>\n"
                "extern void SUBMOD();\n"
                "int main() {\n"
                "    printf(\"MAINC: CALLING SUBMOD\\n\");\n"
                "    SUBMOD();\n"
                "    printf(\"MAINC: DONE\\n\");\n"
                "    return 0;\n"
                "}\n"
            )
        with open(sub_src, "w") as f:
            f.write(
                '#pragma module SUBMOD "V01-00"\n'
                "#include <stdio.h>\n"
                "int main() {\n"
                "    printf(\"SUBMOD: EXECUTED FROM VAX C MODULE\\n\");\n"
                "    return 0;\n"
                "}\n"
            )

        assert subprocess.run([VAXC_BIN, c_src, "-o", c_obj], capture_output=True).returncode == 0
        assert subprocess.run([VAXC_BIN, sub_src, "-o", sub_obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, c_obj, sub_obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "MAINC: CALLING SUBMOD" in r_run.stdout
        assert "SUBMOD: EXECUTED FROM VAX C MODULE" in r_run.stdout
        assert "MAINC: DONE" in r_run.stdout
