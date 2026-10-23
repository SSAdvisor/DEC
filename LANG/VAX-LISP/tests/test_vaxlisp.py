#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX LISP V3.1-00 (vaxlisp)
"""

import os
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXLISP_BIN = os.path.join(ROOT_DIR, "compiler", "vaxlisp")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


class TestVAXLispCompilerAndREPL:
    def test_01_compile_and_link_demo_lsp(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.LSP")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")
        exe = os.path.join(str(tmp_path), "DEMO.EXE")

        r_comp = subprocess.run([VAXLISP_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX LISP V3.1-00: Compiled DEMO.LSP -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(lst, "r") as f:
            lst_txt = f.read()
        assert "DEC VAX LISP V3.1-00" in lst_txt
        assert "Function FACTORIAL" in lst_txt

        r_link = subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True, text=True)
        assert r_link.returncode == 0
        assert os.path.isfile(exe)

        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "DEC VAX LISP V3.1 — SYMBOLIC PROCESSING ENGINE" in r_run.stdout
        assert "FACTORIAL(6) = 720" in r_run.stdout
        assert "FIBONACCI(8) = 21" in r_run.stdout
        assert "REVERSED     = (5 4 3 2 1)" in r_run.stdout
        assert "SUM-SQUARES  = 55" in r_run.stdout

    def test_02_loops_macros_and_list_primitives(self, tmp_path):
        src = os.path.join(str(tmp_path), "LISTOPS.LSP")
        obj = os.path.join(str(tmp_path), "LISTOPS.OBJ")
        exe = os.path.join(str(tmp_path), "LISTOPS.EXE")

        with open(src, "w") as f:
            f.write(
                "(defvar *acc* 0)\n"
                "(dotimes (i 5)\n"
                "  (setq *acc* (+ *acc* (1+ i))))\n"
                "(dolist (x '(10 20 30))\n"
                "  (setq *acc* (+ *acc* x)))\n"
                "(format t \"ACC=~D LEN=~D NTH=~A~%\" *acc* (length '(a b c d)) (nth 2 '(alpha beta gamma delta)))\n"
            )

        assert subprocess.run([VAXLISP_BIN, src, f"/OBJECT={obj}"], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "ACC=75 LEN=4 NTH=GAMMA" in r_run.stdout

    def test_03_higher_order_functions_do_and_predicates(self, tmp_path):
        src = os.path.join(str(tmp_path), "HIGHER.LSP")
        obj = os.path.join(str(tmp_path), "HIGHER.OBJ")
        exe = os.path.join(str(tmp_path), "HIGHER.EXE")

        with open(src, "w") as f:
            f.write(
                "(defun make-adder (k)\n"
                "  (lambda (x) (+ x k)))\n"
                "(setq add10 (make-adder 10))\n"
                "(setq mapped (mapcar add10 '(1 2 3)))\n"
                "(setq pcheck (list (null nil) (atom 'foo) (listp mapped) (numberp 42) (symbolp 'bar)))\n"
                "(format t \"MAPPED=~S PCHECK=~S~%\" mapped pcheck)\n"
            )

        assert subprocess.run([VAXLISP_BIN, src, "-o", obj], capture_output=True).returncode == 0
        assert subprocess.run([VMSLINK_BIN, "-o", exe, obj], capture_output=True).returncode == 0
        r_run = subprocess.run([exe], capture_output=True, text=True)
        assert r_run.returncode == 0
        assert "MAPPED=(11 12 13) PCHECK=(T T T T T)" in r_run.stdout

    def test_04_interactive_vax_lisp_repl(self, tmp_path):
        stdin_cmds = (
            "(defun cube (x) (* x x x))\n"
            "(cube 4)\n"
            "(cons 'vax '(lisp v3-1))\n"
            "(exit)\n"
        )
        r = subprocess.run([VAXLISP_BIN, "--interactive"], input=stdin_cmds, capture_output=True, text=True, cwd=str(tmp_path))
        assert r.returncode == 0
        assert "VAX LISP V3.1 — Common Lisp for VAX/VMS" in r.stdout
        assert "LISP>" in r.stdout
        assert "CUBE" in r.stdout
        assert "64" in r.stdout
        assert "(VAX LISP V3-1)" in r.stdout
