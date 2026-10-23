#!/usr/bin/env python3
"""
Automated Test Suite for DEC VAX FORTRAN V5.5 Compiler (vaxfor)
"""

import os
import json
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAXFOR_BIN = os.path.join(ROOT_DIR, "compiler", "vaxfor")
VMSLINK_BIN = os.path.abspath(os.path.join(ROOT_DIR, "..", "VAX-BASIC", "linker", "vmslink"))


def link_and_run(obj_path, tmp_path):
    exe_path = os.path.join(str(tmp_path), "PROG.EXE")
    r_link = subprocess.run([VMSLINK_BIN, "-o", exe_path, obj_path], capture_output=True, text=True)
    assert r_link.returncode == 0, r_link.stdout + r_link.stderr
    assert os.path.isfile(exe_path)
    return subprocess.run([exe_path], capture_output=True, text=True, cwd=str(tmp_path))


class TestVAXFortranCompiler:
    def test_01_compile_and_link_demo_for(self, tmp_path):
        src = os.path.join(ROOT_DIR, "samples", "DEMO.FOR")
        obj = os.path.join(str(tmp_path), "DEMO.OBJ")
        lst = os.path.join(str(tmp_path), "DEMO.LST")

        r_comp = subprocess.run([VAXFOR_BIN, src, "-o", obj, "-l", lst], capture_output=True, text=True)
        assert r_comp.returncode == 0
        assert "VAX FORTRAN V5.5-00: Compiled DEMO.FOR -> DEMO.OBJ (0 errors)" in r_comp.stdout
        assert os.path.isfile(obj)
        assert os.path.isfile(lst)

        with open(obj, "r") as f:
            obj_data = json.load(f)
        assert obj_data["target"] == "VAX/VMS"

        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "DEC VAX FORTRAN V5.5 ON VAX/VMS V5.5-2" in r_run.stdout
        assert "SENSOR: VAX-11/780 CORE ID=101" in r_run.stdout
        assert "ARRAY TOTAL=150 FACT(5)=120" in r_run.stdout
        assert "STATUS=NOMINAL" in r_run.stdout

    def test_02_structure_record_select_case_and_elseif(self, tmp_path):
        for_code = """\
      PROGRAM STRUCTTST
      IMPLICIT NONE
      STRUCTURE /EMP_REC/
          INTEGER*4 ID
          CHARACTER*24 NAME
          INTEGER*4 SALARY
      END STRUCTURE
      RECORD /EMP_REC/ EMP
      INTEGER*4 BONUS
      CHARACTER*16 BAND

      EMP.ID = 780
      EMP.NAME = 'DAVE CUTLER'
      EMP.SALARY = 92000

      IF (EMP.SALARY .GE. 90000) THEN
          BONUS = 8000
      ELSE IF (EMP.SALARY .GE. 70000) THEN
          BONUS = 5000
      ELSE
          BONUS = 2000
      END IF

      SELECT CASE (EMP.ID)
          CASE (700:799)
              BAND = 'VAX-ARCHITECT'
          CASE DEFAULT
              BAND = 'ENGINEER'
      END SELECT

      WRITE(*,*) 'EMP=', EMP.NAME, ' COMP=', EMP.SALARY + BONUS, ' BAND=', BAND
      STOP
      END
"""
        src = os.path.join(str(tmp_path), "STRUCTTST.FOR")
        obj = os.path.join(str(tmp_path), "STRUCTTST.OBJ")
        with open(src, "w") as f:
            f.write(for_code)

        r_comp = subprocess.run([VAXFOR_BIN, src, f"/OBJECT={obj}"], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "EMP=DAVE CUTLER COMP=100000 BAND=VAX-ARCHITECT" in r_run.stdout

    def test_03_user_function_data_and_labeled_do(self, tmp_path):
        for_code = """\
      PROGRAM FNTST
      INTEGER*4 X, Y, I, ACC, SQUARE_VAL
      DATA X / 12 /
      ACC = 0
      DO 100 I = 1, 4
          ACC = ACC + SQUARE_VAL(I)
 100  CONTINUE
      Y = SQUARE_VAL(X)
      PRINT *, 'ACC=', ACC, ' SQ12=', Y
      STOP
      END

      INTEGER*4 FUNCTION SQUARE_VAL(N)
      INTEGER*4 N
      SQUARE_VAL = N * N
      RETURN
      END
"""
        src = os.path.join(str(tmp_path), "FNTST.FOR")
        obj = os.path.join(str(tmp_path), "FNTST.OBJ")
        with open(src, "w") as f:
            f.write(for_code)

        r_comp = subprocess.run([VAXFOR_BIN, src, "-o", obj], capture_output=True, text=True)
        assert r_comp.returncode == 0
        r_run = link_and_run(obj, tmp_path)
        assert r_run.returncode == 0
        assert "ACC=30 SQ12=144" in r_run.stdout

    def test_04_interactive_workbench(self, tmp_path):
        r = subprocess.run(
            [VAXFOR_BIN],
            input="SAMPLE\nLIST\nCHECK\nEXIT\n",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert r.returncode == 0
        assert "DEC VAX FORTRAN V5.5-00 Compiler" in r.stdout
        assert "STRUCTURE / RECORD  : Verified" in r.stdout
        assert "0 errors, 0 warnings" in r.stdout
