import subprocess
import os
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER_BIN = os.path.join(ROOT_DIR, "compiler", "basicc")
LINKER_BIN = os.path.join(ROOT_DIR, "linker", "basiclink")

def test_native_executables_exist():
    assert os.path.isfile(COMPILER_BIN), f"{COMPILER_BIN} not found"
    assert os.access(COMPILER_BIN, os.X_OK), f"{COMPILER_BIN} is not executable"
    assert os.path.isfile(LINKER_BIN), f"{LINKER_BIN} not found"
    assert os.access(LINKER_BIN, os.X_OK), f"{LINKER_BIN} is not executable"

def test_native_single_module_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        obj_path = os.path.join(tmpdir, "test.obj")
        exe_path = os.path.join(tmpdir, "test_exe")
        src_path = os.path.join(ROOT_DIR, "tests", "test_link.bas")

        # 1. Native Compile
        res_c = subprocess.run([COMPILER_BIN, src_path, "-o", obj_path],
                               capture_output=True, text=True)
        assert res_c.returncode == 0, f"Compilation failed: {res_c.stderr}\n{res_c.stdout}"
        assert os.path.isfile(obj_path), "obj file not created"

        # 2. Native Link
        res_l = subprocess.run([LINKER_BIN, obj_path, "-o", exe_path],
                               capture_output=True, text=True)
        assert res_l.returncode == 0, f"Linking failed: {res_l.stderr}\n{res_l.stdout}"
        assert os.path.isfile(exe_path), "executable not created"

        # 3. Native Run
        res_r = subprocess.run([exe_path], capture_output=True, text=True)
        assert res_r.returncode == 0, f"Execution failed: {res_r.stderr}\n{res_r.stdout}"
        assert "100" in res_r.stdout

def test_native_overlay_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        main_obj = os.path.join(tmpdir, "main.obj")
        f1_obj = os.path.join(tmpdir, "func1.obj")
        f2_obj = os.path.join(tmpdir, "func2.obj")
        exe_path = os.path.join(tmpdir, "overlay_exe")

        main_bas = os.path.join(ROOT_DIR, "tests", "main.bas")
        f1_bas = os.path.join(ROOT_DIR, "tests", "func1.bas")
        f2_bas = os.path.join(ROOT_DIR, "tests", "func2.bas")
        odl_path = os.path.join(ROOT_DIR, "tests", "test.odl")

        # 1. Native Compile Modules
        r1 = subprocess.run([COMPILER_BIN, main_bas, "-o", main_obj],
                            capture_output=True, text=True)
        assert r1.returncode == 0, f"Main compile failed: {r1.stderr}\n{r1.stdout}"

        r2 = subprocess.run([COMPILER_BIN, f1_bas, "-o", f1_obj, "--module", "FUNC1"],
                            capture_output=True, text=True)
        assert r2.returncode == 0, f"Func1 compile failed: {r2.stderr}\n{r2.stdout}"

        r3 = subprocess.run([COMPILER_BIN, f2_bas, "-o", f2_obj, "--module", "FUNC2"],
                            capture_output=True, text=True)
        assert r3.returncode == 0, f"Func2 compile failed: {r3.stderr}\n{r3.stdout}"

        # 2. Native Link
        res_l = subprocess.run([LINKER_BIN, main_obj, f1_obj, f2_obj, odl_path, "-o", exe_path],
                               capture_output=True, text=True)
        assert res_l.returncode == 0, f"Overlay link failed: {res_l.stderr}\n{res_l.stdout}"
        assert os.path.isfile(exe_path), "Overlay executable not created"

        # 3. Native Run
        res_r = subprocess.run([exe_path], capture_output=True, text=True)
        assert res_r.returncode == 0, f"Overlay run failed: {res_r.stderr}\n{res_r.stdout}"
        assert "1" in res_r.stdout
        assert "11" in res_r.stdout
        assert "22" in res_r.stdout

def test_native_data_and_strings():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "prog.bas")
        obj_path = os.path.join(tmpdir, "prog.obj")
        exe_path = os.path.join(tmpdir, "prog_exe")

        with open(src_path, "w") as f:
            f.write(
                '10 DATA 42, "PDP11"\n'
                '20 READ A%, B$\n'
                '30 PRINT "VAL="; A%; " STR="; B$; " LEN="; LEN(B$)\n'
                '40 END\n'
            )

        r_c = subprocess.run([COMPILER_BIN, src_path, "-o", obj_path],
                             capture_output=True, text=True)
        assert r_c.returncode == 0, f"Compile failed: {r_c.stderr}\n{r_c.stdout}"

        r_l = subprocess.run([LINKER_BIN, obj_path, "-o", exe_path],
                             capture_output=True, text=True)
        assert r_l.returncode == 0, f"Link failed: {r_l.stderr}\n{r_l.stdout}"

        r_r = subprocess.run([exe_path], capture_output=True, text=True)
        assert r_r.returncode == 0, f"Run failed: {r_r.stderr}\n{r_r.stdout}"
        assert "VAL=42 STR=PDP11 LEN=5" in r_r.stdout
