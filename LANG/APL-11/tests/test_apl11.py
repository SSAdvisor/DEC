import os
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APL_BIN = os.path.join(ROOT_DIR, "compiler", "apl11")
BASICLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "BASIC-PLUS-2", "linker", "basiclink"))
VM_DIR = os.path.abspath(os.path.join(ROOT_DIR, "..", "BASIC-PLUS-2", "vm", "build"))


def link_and_run(obj_path, tmp_path):
    tsk_path = os.path.join(str(tmp_path), "PROG.TSK")
    env = os.environ.copy()
    env["PATH"] = f"{VM_DIR}:{env.get('PATH', '')}"
    r_link = subprocess.run([BASICLINK_BIN, "-o", tsk_path, obj_path], capture_output=True, text=True, env=env)
    assert r_link.returncode == 0, r_link.stdout + r_link.stderr
    r_run = subprocess.run([tsk_path], capture_output=True, text=True, cwd=str(tmp_path))
    return r_run


class TestAPL11Toolchain:
    def test_01_compile_and_link_vectors_sample(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "VECTORS.APL")
        obj = os.path.join(str(tmp_path), "VECTORS.OBJ")
        lst = os.path.join(str(tmp_path), "VECTORS.LST")

        r_comp = subprocess.run([APL_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "APL-11 V2.1: Compiled VECTORS.APL -> VECTORS.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC PDP-11 APL-11 V2.1 VECTOR ENGINE" in r_run.stdout
        assert "1 2 3 4 5 6 7 8 9 10" in r_run.stdout
        assert "55" in r_run.stdout
        assert "120" in r_run.stdout
        assert "100 81 64 49 36 25 16 9 4 1" in r_run.stdout

    def test_02_interactive_apl_workspace_and_ascii_mnemonics(self, tmp_path):
        stdin_cmds = (
            ")WSID MYCALC\n"
            "X <- .IOTA 6\n"
            "+/ X\n"
            "*/ .IOTA 4\n"
            ".RHO X\n"
            ")VARS\n"
            ")SAVE\n"
            ")CLEAR\n"
            ")LOAD MYCALC\n"
            "X\n"
            ")OFF\n"
        )
        r = subprocess.run([APL_BIN], input=stdin_cmds, capture_output=True, text=True, cwd=str(tmp_path))
        assert r.returncode == 0
        assert "DEC PDP-11 APL-11 V2.1" in r.stdout
        assert "21" in r.stdout
        assert "24" in r.stdout
        assert "1 2 3 4 5 6" in r.stdout
        assert "OFF AT" in r.stdout

    def test_03_user_defined_del_functions(self, tmp_path):
        stdin_cmds = (
            "∇ Z ← AVG V\n"
            "Z ← (+/ V) ÷ (⍴ V)\n"
            "∇\n"
            ")FNS\n"
            "AVG 10 20 30 40\n"
            ")OFF\n"
        )
        r = subprocess.run([APL_BIN], input=stdin_cmds, capture_output=True, text=True, cwd=str(tmp_path))
        assert r.returncode == 0
        assert "AVG" in r.stdout
        assert "25" in r.stdout
