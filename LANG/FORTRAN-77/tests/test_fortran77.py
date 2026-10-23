import os
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
F77_BIN = os.path.join(ROOT_DIR, "compiler", "fortran77")
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


class TestFortran77Toolchain:
    def test_01_compile_and_link_stats_sample(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "STATS.FOR")
        obj = os.path.join(str(tmp_path), "STATS.OBJ")
        lst = os.path.join(str(tmp_path), "STATS.LST")

        r_comp = subprocess.run([F77_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "FORTRAN-77 V5.0: Compiled STATS.FOR -> STATS.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC PDP-11 FORTRAN-77 V5.0 RESULTS:" in r_run.stdout
        assert "SUM(1..10) = 55" in r_run.stdout
        assert "SUMSQ(1..10) = 385" in r_run.stdout

    def test_02_block_if_else_and_arrays(self, tmp_path):
        for_code = """\
C     FORTRAN-77 ARRAYS AND BLOCK IF
      PROGRAM ARRTST
      INTEGER A(5), I, ITOT
      ITOT = 0
      DO 10 I = 1, 5
         A(I) = I * 10
         ITOT = ITOT + A(I)
 10   CONTINUE
      IF (ITOT .EQ. 150) THEN
         WRITE(6,*) 'ARRAY-TOTAL-OK:', ITOT
      ELSE
         WRITE(6,*) 'ARRAY-TOTAL-BAD'
      ENDIF
      STOP
      END
"""
        src = os.path.join(str(tmp_path), "ARRTST.FOR")
        obj = os.path.join(str(tmp_path), "ARRTST.OBJ")
        with open(src, "w") as f:
            f.write(for_code)

        r_comp = subprocess.run([F77_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "ARRAY-TOTAL-OK:150" in r_run.stdout

    def test_03_subroutine_call_and_data_stmt(self, tmp_path):
        for_code = """\
      PROGRAM SUBTST
      INTEGER X, Y
      DATA X / 21 /
      CALL DOUBLE_IT
      WRITE(6,*) 'Y=', Y
      STOP
      SUBROUTINE DOUBLE_IT
      Y = X * 2
      RETURN
      END
"""
        src = os.path.join(str(tmp_path), "SUBTST.FOR")
        obj = os.path.join(str(tmp_path), "SUBTST.OBJ")
        with open(src, "w") as f:
            f.write(for_code)

        r_comp = subprocess.run([F77_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "Y=42" in r_run.stdout

    def test_04_interactive_workbench_mode(self, tmp_path):
        r = subprocess.run(
            [F77_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC PDP-11 FORTRAN-77 V5.0 Compiler" in r.stdout
        assert "DO Loop Labels      : Balanced" in r.stdout
        assert "0 errors, 0 warnings" in r.stdout
