import subprocess
import os
import tarfile
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(ROOT_DIR, "distrib")
KIT_ARCHIVE = os.path.join(DIST_DIR, "DEC-BASIC-PLUS-2-V10.1-L-Linux-x86_64.tar.gz")
SRC_ARCHIVE = os.path.join(DIST_DIR, "DEC-BASIC-PLUS-2-V10.1-L-Source.tar.gz")

def test_distribution_archives_exist():
    assert os.path.isfile(KIT_ARCHIVE), f"Binary kit archive not found at {KIT_ARCHIVE}"
    assert os.path.getsize(KIT_ARCHIVE) > 500000, "Binary kit archive suspiciously small"
    assert os.path.isfile(SRC_ARCHIVE), f"Source kit archive not found at {SRC_ARCHIVE}"
    assert os.path.getsize(SRC_ARCHIVE) > 500000, "Source kit archive suspiciously small"

def test_kit_installation_and_verification():
    with tempfile.TemporaryDirectory() as tmpdir:
        unpack_dir = os.path.join(tmpdir, "unpack")
        install_prefix = os.path.join(tmpdir, "prefix")
        os.makedirs(unpack_dir)

        # 1. Extract tarball
        with tarfile.open(KIT_ARCHIVE, "r:gz") as tar:
            tar.extractall(path=unpack_dir, filter="data")

        kit_root = os.path.join(unpack_dir, "DEC-BASIC-PLUS-2-V10.1-L-Linux-x86_64")
        assert os.path.isdir(kit_root), f"Expected kit root {kit_root} not found"

        # 2. Run installer
        install_script = os.path.join(kit_root, "install.sh")
        res_inst = subprocess.run(
            [install_script, f"--prefix={install_prefix}", "--no-symlinks"],
            capture_output=True,
            text=True,
        )
        assert res_inst.returncode == 0, f"Install failed: {res_inst.stderr}\n{res_inst.stdout}"
        assert "ALL 7 VERIFICATION CHECKS PASSED SUCCESSFULLY!" in res_inst.stdout

        # 3. Check installed layout
        bin_dir = os.path.join(install_prefix, "bin")
        for b in ["basicc", "basiclink", "dcl", "edt", "rsts_vm", "dec-printq", "basic_env.sh"]:
            assert os.path.exists(os.path.join(bin_dir, b)), f"Installed file missing: {b}"

        docs_dir = os.path.join(install_prefix, "docs")
        for d in ["ARCHITECTURE.md", "DEC_DOCUMENTATION_SUGGESTIONS.md", "USER_GUIDE.md"]:
            assert os.path.exists(os.path.join(docs_dir, d)), f"Installed doc missing: {d}"

        # 4. Compile and link a test program using the installed binaries
        test_bas = os.path.join(tmpdir, "test.bas")
        test_obj = os.path.join(tmpdir, "test.obj")
        test_exe = os.path.join(tmpdir, "test_exe")

        with open(test_bas, "w") as f:
            f.write(
                '10 PRINT "INSTALL_TEST_OK: "; 12 * 12\n'
                '20 END\n'
            )

        basicc = os.path.join(bin_dir, "basicc")
        basiclink = os.path.join(bin_dir, "basiclink")

        env = dict(os.environ)
        env["DEC_BASIC_HOME"] = install_prefix
        env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"

        r_comp = subprocess.run([basicc, test_bas, "-o", test_obj], capture_output=True, text=True, env=env)
        assert r_comp.returncode == 0, f"Installed basicc failed: {r_comp.stderr}\n{r_comp.stdout}"

        r_link = subprocess.run([basiclink, test_obj, "-o", test_exe], capture_output=True, text=True, env=env)
        assert r_link.returncode == 0, f"Installed basiclink failed: {r_link.stderr}\n{r_link.stdout}"

        r_run = subprocess.run([test_exe], capture_output=True, text=True)
        assert r_run.returncode == 0, f"Test executable failed: {r_run.stderr}\n{r_run.stdout}"
        assert "INSTALL_TEST_OK: 144" in r_run.stdout

        # 5. Test uninstaller
        uninstall_script = os.path.join(kit_root, "uninstall.sh")
        res_uninst = subprocess.run(
            [uninstall_script, install_prefix],
            capture_output=True,
            text=True,
        )
        assert res_uninst.returncode == 0, f"Uninstall failed: {res_uninst.stderr}\n{res_uninst.stdout}"
        assert not os.path.exists(install_prefix), "Install prefix was not removed by uninstall.sh"
