import os
import subprocess
import pytest

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISTRIB_DIR = os.path.join(REPO_DIR, "distrib")
BUILD_KIT_SH = os.path.join(DISTRIB_DIR, "build_kit.sh")
INSTALL_SH = os.path.join(DISTRIB_DIR, "install.sh")
UNINSTALL_SH = os.path.join(DISTRIB_DIR, "uninstall.sh")
VERIFY_KIT_SH = os.path.join(DISTRIB_DIR, "verify_kit.sh")

MASTER_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-V1.0-L-Linux-x86_64.tar.gz")
HAMURABI_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-hamurabi-V1.0-L-Linux-x86_64.tar.gz")
SORT11_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-sort11-V1.0-L-Linux-x86_64.tar.gz")
SRC_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-V1.0-L-Source.tar.gz")

def test_distrib_build_kit():
    """Verify that build_kit.sh runs cleanly and produces all release archives and manifests."""
    res = subprocess.run([BUILD_KIT_SH], capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, f"build_kit.sh failed:\n{res.stdout}\n{res.stderr}"

    assert os.path.isfile(MASTER_ARCHIVE), f"Master archive {MASTER_ARCHIVE} not created"
    assert os.path.isfile(HAMURABI_ARCHIVE), f"Hamurabi archive {HAMURABI_ARCHIVE} not created"
    assert os.path.isfile(SORT11_ARCHIVE), f"SORT-11 archive {SORT11_ARCHIVE} not created"
    assert os.path.isfile(SRC_ARCHIVE), f"Source archive {SRC_ARCHIVE} not created"

    # Verify staging contents of master kit
    staging_dir = os.path.join(DISTRIB_DIR, "kit", "DEC-APPS-V1.0-L-Linux-x86_64")
    assert os.path.isfile(os.path.join(staging_dir, "KIT.INI"))
    assert os.path.isfile(os.path.join(staging_dir, "MANIFEST.TXT"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "hamurabi"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "sort11"))

def test_install_individual_app(tmp_path):
    """Verify that an individual application can be installed independently."""
    prefix = tmp_path / "individual_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "sort11"],
        capture_output=True,
        text=True,
        timeout=20
    )
    assert res.returncode == 0, f"Individual install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: sort11" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    sort11_bin = prefix / "bin" / "sort11"
    hamurabi_bin = prefix / "bin" / "hamurabi"
    assert sort11_bin.is_file()
    assert os.access(sort11_bin, os.X_OK)
    assert not hamurabi_bin.exists(), "hamurabi binary should NOT be installed"

    assert (prefix / "docs" / "sort11.md").is_file()
    assert (prefix / "bin" / "dec_apps_env.sh").is_file()

def test_uninstall_individual_app(tmp_path):
    """Verify that uninstalling one application does not affect others in the same prefix."""
    prefix = tmp_path / "mixed_install"

    # 1. Install both applications
    res_in = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "all"],
        capture_output=True,
        text=True,
        timeout=20
    )
    assert res_in.returncode == 0
    assert (prefix / "bin" / "sort11").is_file()
    assert (prefix / "bin" / "hamurabi").is_file()

    # 2. Uninstall sort11 only
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "sort11"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert "Uninstalling sort11..." in res_un.stdout

    # 3. Check status: sort11 removed, hamurabi preserved
    assert not (prefix / "bin" / "sort11").exists()
    assert not (prefix / "docs" / "sort11.md").exists()
    assert (prefix / "bin" / "hamurabi").is_file()
    assert (prefix / "docs" / "hamurabi.md").is_file()

def test_install_and_uninstall_all(tmp_path):
    """Verify installing all applications at once and full uninstallation."""
    prefix = tmp_path / "bulk_install"

    # 1. Install all
    res_in = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks"],
        capture_output=True,
        text=True,
        timeout=20
    )
    assert res_in.returncode == 0
    assert (prefix / "bin" / "sort11").is_file()
    assert (prefix / "bin" / "hamurabi").is_file()
    assert (prefix / "bin" / "dec_apps_env.sh").is_file()

    # 2. Uninstall all
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "all"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not prefix.exists() or not any(prefix.iterdir()), "Target prefix should be removed or empty"

def test_installer_list_apps():
    """Verify that ./install.sh --list enumerates all available applications."""
    res = subprocess.run([INSTALL_SH, "--list"], capture_output=True, text=True, timeout=5)
    assert res.returncode == 0
    assert "hamurabi" in res.stdout
    assert "sort11" in res.stdout
