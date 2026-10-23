import os
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MACRO11_BIN = os.path.join(ROOT_DIR, "compiler", "macro11")
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


class TestMacro11Toolchain:
    def test_01_compile_and_link_sample_hello_mac(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "HELLO.MAC")
        obj = os.path.join(str(tmp_path), "HELLO.OBJ")
        lst = os.path.join(str(tmp_path), "HELLO.LST")

        r_asm = subprocess.run([MACRO11_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_asm.returncode == 0
        assert "MACRO-11 V05.05: Assembled HELLO.MAC -> HELLO.OBJ (0 errors)" in r_asm.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(lst, "r") as f:
            lst_txt = f.read()
        assert "MACRO V05.05" in lst_txt
        assert "Symbol Table:" in lst_txt
        assert "START" in lst_txt

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "HELLO FROM DEC MACRO-11 V05.05 ON RSTS-E!" in r_run.stdout
        assert "PDP-11 REGISTER R1 RESULT:" in r_run.stdout
        assert "42" in r_run.stdout

    def test_02_registers_arithmetic_and_branches(self, tmp_path):
        mac_code = """\
        .TITLE  ARITH
        .IDENT  /V01.00/
START:  CLR     R0
        MOV     #5.,R1
        MOV     #1.,R2
FACT:   MOV     R2,R3
        MUL     R1,R3
        MOV     R3,R2
        SOB     R1,FACT
        .PRINT  #OUTMSG
        .PRINT  R2
        .EXIT
OUTMSG: .ASCIZ  /FACTORIAL5=/
        .END    START
"""
        src = os.path.join(str(tmp_path), "ARITH.MAC")
        obj = os.path.join(str(tmp_path), "ARITH.OBJ")
        with open(src, "w") as f:
            f.write(mac_code)

        r_asm = subprocess.run([MACRO11_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_asm.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "FACTORIAL5=" in r_run.stdout
        assert "120" in r_run.stdout

    def test_03_cmp_branches_and_word_directives(self, tmp_path):
        mac_code = """\
        .TITLE  CMPBR
START:  MOV     VALA,R0
        MOV     VALB,R1
        CMP     R0,R1
        BLT     LESS
        .PRINT  #M_GE
        BR      DONE
LESS:   .PRINT  #M_LT
DONE:   .EXIT
VALA:   .WORD   15.
VALB:   .WORD   25.
M_LT:   .ASCIZ  /VALA IS LESS THAN VALB/
M_GE:   .ASCIZ  /VALA IS GE VALB/
        .END    START
"""
        src = os.path.join(str(tmp_path), "CMPBR.MAC")
        obj = os.path.join(str(tmp_path), "CMPBR.OBJ")
        with open(src, "w") as f:
            f.write(mac_code)

        r_asm = subprocess.run([MACRO11_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_asm.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "VALA IS LESS THAN VALB" in r_run.stdout

    def test_04_interactive_workbench_mode(self, tmp_path):
        r = subprocess.run(
            [MACRO11_BIN],
            input="SAMPLE\nLIST\nSYMBOLS\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC MACRO-11 V05.05" in r.stdout
        assert "Symbol Table & Audit" in r.stdout
        assert "START" in r.stdout
        assert "Errors: 0" in r.stdout
