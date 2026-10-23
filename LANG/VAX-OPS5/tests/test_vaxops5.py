#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX OPS5 V2.2-00 (vaxops5)
"""

import os
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXOPS5_BIN = os.path.join(ROOT_DIR, "compiler", "vaxops5")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXOPS5CompilerAndShell:
    def test_01_compile_and_link_xcon_demo_ops(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.OPS")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")

        r_comp = subprocess.run([VAXOPS5_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX OPS5 V2.2-00: Compiled DEMO.OPS -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(lst, "r") as f:
            lst_txt = f.read()
        assert "DEC VAX OPS5 V2.2-00" in lst_txt
        assert "RULE_ANNOUNCE-X" in lst_txt

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX OPS5 V2.2 — XCON VAX-11/780 CONFIGURATOR" in r_run.stdout
        assert "ORDER: CPU= VAX-11/780  MEMORY= 16 MB" in r_run.stdout
        assert "CONFIGURED: DW780-UBA ON SBI BUS" in r_run.stdout
        assert "VERIFIED MODULE: DW780-UBA  TOTAL SBI POWER= 500 WATTS" in r_run.stdout

    def test_02_counter_loop_modify_remove_and_compute(self, tmp_path):
        src = os.path.join(str(tmp_path), "COUNT.OPS")
        obj = os.path.join(str(tmp_path), "COUNT.OBJ")
        exe = os.path.join(str(tmp_path), "COUNT.EXE")

        with open(src, "w") as f:
            f.write(
                "(literalize counter ^val ^limit ^acc)\n"
                "(p step-counter\n"
                "   (counter ^val <v> ^limit <lim> > <v> ^acc <a>)\n"
                "   -->\n"
                "   (bind <nv> (compute <v> + 1))\n"
                "   (bind <na> (compute <a> + <nv>))\n"
                "   (modify 1 ^val <nv> ^acc <na>))\n"
                "(p finish-counter\n"
                "   (counter ^val <v> ^limit <v> ^acc <a>)\n"
                "   -->\n"
                "   (write |FINAL_ACC=| <a> (crlf))\n"
                "   (remove 1)\n"
                "   (halt))\n"
                "(make counter ^val 0 ^limit 5 ^acc 0)\n"
                "(run)\n"
            )

        assert subprocess.run([VAXOPS5_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "FINAL_ACC= 15" in r_run.stdout

    def test_03_negated_condition_elements_and_disjunctions(self, tmp_path):
        src = os.path.join(str(tmp_path), "ALARM.OPS")
        obj = os.path.join(str(tmp_path), "ALARM.OBJ")
        exe = os.path.join(str(tmp_path), "ALARM.EXE")

        with open(src, "w") as f:
            f.write(
                "(literalize sensor ^zone ^severity)\n"
                "(literalize ack ^zone)\n"
                "(p raise-unacknowledged-alarm\n"
                "   (sensor ^zone <z> ^severity << HIGH CRITICAL >>)\n"
                "   - (ack ^zone <z>)\n"
                "   -->\n"
                "   (write |ALERT ZONE:| <z> (crlf))\n"
                "   (make ack ^zone <z>))\n"
                "(make sensor ^zone REACTOR-1 ^severity CRITICAL)\n"
                "(make sensor ^zone COOLANT-2 ^severity LOW)\n"
                "(run)\n"
            )

        assert subprocess.run([VAXOPS5_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "ALERT ZONE: REACTOR-1" in r_run.stdout
        assert "COOLANT-2" not in r_run.stdout

    def test_04_interactive_ops5_shell(self, tmp_path):
        stdin_cmds = (
            "(literalize task ^name ^state)\n"
            "(p run-task (task ^name <n> ^state ready) --> (write |RUNNING| <n> (crlf)) (modify 1 ^state done))\n"
            "(make task ^name BACKUP ^state ready)\n"
            "(wm)\n"
            "(pm)\n"
            "(watch 1)\n"
            "(run 5)\n"
            "(exit)\n"
        )
        r = subprocess.run([VAXOPS5_BIN, "--interactive"], input=stdin_cmds, capture_output=True, text=True, cwd=str(tmp_path))
        assert r.returncode == 0
        assert "DEC VAX OPS5 V2.2-00 — Production System Environment" in r.stdout
        assert "OPS5>" in r.stdout
        assert "1: (TASK ^NAME BACKUP ^STATE READY)" in r.stdout
        assert "Rule RUN-TASK" in r.stdout
        assert "RUNNING BACKUP" in r.stdout
