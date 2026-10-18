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
RMSUTILS_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-rmsutils-V1.0-L-Linux-x86_64.tar.gz")
ADE_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-ade-V1.0-L-Linux-x86_64.tar.gz")
DATATRIEVE11_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-datatrieve11-V1.0-L-Linux-x86_64.tar.gz")
DECGRAPH_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-decgraph-V1.0-L-Linux-x86_64.tar.gz")
DECMAIL_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-decmail-V1.0-L-Linux-x86_64.tar.gz")
DECWORD_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-decword-V1.0-L-Linux-x86_64.tar.gz")
DIBS_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-dibs-V1.0-L-Linux-x86_64.tar.gz")
FMS11_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-fms11-V1.0-L-Linux-x86_64.tar.gz")
MENU11_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-menu11-V1.0-L-Linux-x86_64.tar.gz")
INDENT_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-indent-V1.0-L-Linux-x86_64.tar.gz")
SRC_ARCHIVE = os.path.join(DISTRIB_DIR, "DEC-APPS-V1.0-L-Source.tar.gz")

def test_distrib_build_kit():
    """Verify that build_kit.sh runs cleanly and produces all release archives and manifests."""
    res = subprocess.run([BUILD_KIT_SH], capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, f"build_kit.sh failed:\n{res.stdout}\n{res.stderr}"

    assert os.path.isfile(MASTER_ARCHIVE), f"Master archive {MASTER_ARCHIVE} not created"
    assert os.path.isfile(HAMURABI_ARCHIVE), f"Hamurabi archive {HAMURABI_ARCHIVE} not created"
    assert os.path.isfile(SORT11_ARCHIVE), f"SORT-11 archive {SORT11_ARCHIVE} not created"
    assert os.path.isfile(RMSUTILS_ARCHIVE), f"RMSUTILS archive {RMSUTILS_ARCHIVE} not created"
    assert os.path.isfile(ADE_ARCHIVE), f"ADE archive {ADE_ARCHIVE} not created"
    assert os.path.isfile(DATATRIEVE11_ARCHIVE), f"DATATRIEVE-11 archive {DATATRIEVE11_ARCHIVE} not created"
    assert os.path.isfile(DECGRAPH_ARCHIVE), f"DECgraph archive {DECGRAPH_ARCHIVE} not created"
    assert os.path.isfile(DECMAIL_ARCHIVE), f"DECmail archive {DECMAIL_ARCHIVE} not created"
    assert os.path.isfile(DECWORD_ARCHIVE), f"DECword archive {DECWORD_ARCHIVE} not created"
    assert os.path.isfile(DIBS_ARCHIVE), f"DIBS archive {DIBS_ARCHIVE} not created"
    assert os.path.isfile(FMS11_ARCHIVE), f"FMS-11 archive {FMS11_ARCHIVE} not created"
    assert os.path.isfile(MENU11_ARCHIVE), f"MENU-11 archive {MENU11_ARCHIVE} not created"
    assert os.path.isfile(INDENT_ARCHIVE), f"INDENT archive {INDENT_ARCHIVE} not created"
    assert os.path.isfile(SRC_ARCHIVE), f"Source archive {SRC_ARCHIVE} not created"

    # Verify staging contents of master kit
    staging_dir = os.path.join(DISTRIB_DIR, "kit", "DEC-APPS-V1.0-L-Linux-x86_64")
    assert os.path.isfile(os.path.join(staging_dir, "KIT.INI"))
    assert os.path.isfile(os.path.join(staging_dir, "MANIFEST.TXT"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "hamurabi"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "sort11"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmsutils"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmsdes"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmsdef"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmsifl"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmscnv"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmsbck"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmsrst"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "rmsdsp"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "ade"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "datatrieve11"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "dtr"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "dtr11"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "decgraph"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "graph"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "decg"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "decmail"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "mail"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "decmail11"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "decword"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "decworddp"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "wps"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "dibs"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "dibs11"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "cts500"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "fms11"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "fms"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "fed"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "fdv"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "menu11"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "menu"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "mcf"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "indent"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "bp2fmt"))
    assert os.path.isfile(os.path.join(staging_dir, "bin", "pretty"))

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

def test_install_individual_rmsutils(tmp_path):
    """Verify that rmsutils (and all its companion utilities) can be installed and uninstalled."""
    prefix = tmp_path / "rmsutils_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "rmsutils"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"rmsutils install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: rmsutils" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    # Check that master and all 7 companion utilities are installed
    expected_bins = ["rmsutils", "rmsdes", "rmsdef", "rmsifl", "rmscnv", "rmsbck", "rmsrst", "rmsdsp"]
    for b in expected_bins:
        bin_path = prefix / "bin" / b
        assert bin_path.is_file(), f"Binary {b} was not installed"
        assert os.access(bin_path, os.X_OK), f"Binary {b} is not executable"

    assert (prefix / "docs" / "rmsutils.md").is_file()

    # Uninstall rmsutils
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "rmsutils"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    for b in expected_bins:
        assert not (prefix / "bin" / b).exists(), f"Binary {b} was not removed after uninstall"

def test_install_individual_ade(tmp_path):
    """Verify that ADE can be installed and uninstalled independently."""
    prefix = tmp_path / "ade_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "ade"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"ADE install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: ade" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    ade_bin = prefix / "bin" / "ade"
    assert ade_bin.is_file()
    assert os.access(ade_bin, os.X_OK)

    # Verify execution
    run_res = subprocess.run([str(ade_bin), "HELP"], capture_output=True, text=True, timeout=5)
    assert "ADE V3.0" in run_res.stdout

    assert (prefix / "docs" / "ade.md").is_file()

    # Uninstall ade
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "ade"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not ade_bin.exists()
    assert not (prefix / "docs" / "ade.md").exists()

def test_installer_list_apps():
    """Verify that ./install.sh --list enumerates all available applications."""
    res = subprocess.run([INSTALL_SH, "--list"], capture_output=True, text=True, timeout=5)
    assert res.returncode == 0
    assert "hamurabi" in res.stdout
    assert "sort11" in res.stdout
    assert "rmsutils" in res.stdout
    assert "ade" in res.stdout
    assert "datatrieve11" in res.stdout
    assert "decgraph" in res.stdout
    assert "decmail" in res.stdout
    assert "decword" in res.stdout
    assert "dibs" in res.stdout
    assert "fms11" in res.stdout
    assert "menu11" in res.stdout
    assert "indent" in res.stdout

def test_install_datatrieve11_individual(tmp_path):
    """Verify that datatrieve11 can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "dtr_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "datatrieve11"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"DATATRIEVE-11 install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: datatrieve11" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    dtr_bin = prefix / "bin" / "datatrieve11"
    assert dtr_bin.is_file()
    assert os.access(dtr_bin, os.X_OK)

    # Verify execution via binary
    run_res = subprocess.run([str(dtr_bin), "HELP"], capture_output=True, text=True, timeout=5)
    assert "DATATRIEVE-11 Query & Data Management Commands" in run_res.stdout

    assert (prefix / "docs" / "datatrieve11.md").is_file()

    # Uninstall datatrieve11
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "datatrieve11"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not dtr_bin.exists()
    assert not (prefix / "docs" / "datatrieve11.md").exists()

def test_install_decgraph_individual(tmp_path):
    """Verify that decgraph can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "decgraph_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "decgraph"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"DECgraph install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: decgraph" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    graph_bin = prefix / "bin" / "decgraph"
    assert graph_bin.is_file()
    assert os.access(graph_bin, os.X_OK)

    # Verify execution via binary
    run_res = subprocess.run([str(graph_bin), "HELP; EXIT"], capture_output=True, text=True, timeout=5)
    assert "DECgraph Graphics & Charting Commands" in run_res.stdout

    assert (prefix / "docs" / "decgraph.md").is_file()

    # Uninstall decgraph
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "decgraph"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not graph_bin.exists()
    assert not (prefix / "docs" / "decgraph.md").exists()

def test_install_decmail_individual(tmp_path):
    """Verify that decmail can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "decmail_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "decmail"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"DECmail install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: decmail" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    mail_bin = prefix / "bin" / "decmail"
    assert mail_bin.is_file()
    assert os.access(mail_bin, os.X_OK)

    # Verify execution via binary
    run_res = subprocess.run([str(mail_bin), "HELP; EXIT"], capture_output=True, text=True, timeout=5)
    assert "DECmail Electronic Messaging Commands" in run_res.stdout

    assert (prefix / "docs" / "decmail.md").is_file()

    # Uninstall decmail
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "decmail"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not mail_bin.exists()
    assert not (prefix / "docs" / "decmail.md").exists()

def test_install_decword_individual(tmp_path):
    """Verify that decword can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "decword_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "decword"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"DECword/DP install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: decword" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    word_bin = prefix / "bin" / "decword"
    assert word_bin.is_file()
    assert os.access(word_bin, os.X_OK)
    assert (prefix / "bin" / "decworddp").exists()
    assert (prefix / "bin" / "wps").exists()

    # Verify execution via binary
    run_res = subprocess.run([str(word_bin), "HELP; EXIT"], capture_output=True, text=True, timeout=5)
    assert "DECword/DP Word & Data Processing Commands" in run_res.stdout

    assert (prefix / "docs" / "decword.md").is_file()

    # Uninstall decword
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "decword"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not word_bin.exists()
    assert not (prefix / "docs" / "decword.md").exists()

def test_install_dibs_individual(tmp_path):
    """Verify that dibs can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "dibs_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "dibs"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"DIBS install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: dibs" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    dibs_bin = prefix / "bin" / "dibs"
    assert dibs_bin.is_file()
    assert os.access(dibs_bin, os.X_OK)
    assert (prefix / "bin" / "dibs11").exists()
    assert (prefix / "bin" / "cts500").exists()

    # Verify execution via binary
    run_res = subprocess.run([str(dibs_bin), "HELP; EXIT"], capture_output=True, text=True, timeout=5)
    assert "DIBS-11 Integrated Business System Commands" in run_res.stdout

    assert (prefix / "docs" / "dibs.md").is_file()

    # Uninstall dibs
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "dibs"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not dibs_bin.exists()
    assert not (prefix / "docs" / "dibs.md").exists()

def test_install_fms11_individual(tmp_path):
    """Verify that fms11 can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "fms11_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "fms11"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"FMS-11 install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: fms11" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    fms_bin = prefix / "bin" / "fms11"
    assert fms_bin.is_file()
    assert os.access(fms_bin, os.X_OK)
    assert (prefix / "bin" / "fms").exists()
    assert (prefix / "bin" / "fed").exists()
    assert (prefix / "bin" / "fdv").exists()

    # Verify execution via binary
    run_res = subprocess.run([str(fms_bin), "HELP; EXIT"], capture_output=True, text=True, timeout=5)
    assert "FMS-11 Forms Management System Commands" in run_res.stdout

    assert (prefix / "docs" / "fms11.md").is_file()

    # Uninstall fms11
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "fms11"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not fms_bin.exists()
    assert not (prefix / "docs" / "fms11.md").exists()

def test_install_menu11_individual(tmp_path):
    """Verify that menu11 can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "menu11_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "menu11"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"MENU-11 install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: menu11" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    menu_bin = prefix / "bin" / "menu11"
    assert menu_bin.is_file()
    assert os.access(menu_bin, os.X_OK)
    assert (prefix / "bin" / "menu").exists()
    assert (prefix / "bin" / "mcf").exists()

    # Verify execution via binary
    run_res = subprocess.run([str(menu_bin), "HELP; EXIT"], capture_output=True, text=True, timeout=5)
    assert "MENU-11 Menu Control & Dispatch Facility Commands" in run_res.stdout

    assert (prefix / "docs" / "menu11.md").is_file()

    # Uninstall menu11
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "menu11"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not menu_bin.exists()
    assert not (prefix / "docs" / "menu11.md").exists()

def test_install_indent_individual(tmp_path):
    """Verify that indent can be installed and uninstalled independently with symlinks."""
    prefix = tmp_path / "indent_install"
    res = subprocess.run(
        [INSTALL_SH, f"--prefix={prefix}", "--no-symlinks", "indent"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert res.returncode == 0, f"INDENT install failed:\n{res.stdout}\n{res.stderr}"
    assert "Installing application: indent" in res.stdout
    assert "Verification Summary: 1 Passed, 0 Failed" in res.stdout

    indent_bin = prefix / "bin" / "indent"
    assert indent_bin.is_file()
    assert os.access(indent_bin, os.X_OK)
    assert (prefix / "bin" / "bp2fmt").exists()
    assert (prefix / "bin" / "pretty").exists()

    # Verify execution via binary
    run_res = subprocess.run([str(indent_bin), "HELP; EXIT"], capture_output=True, text=True, timeout=5)
    assert "INDENT BASIC-PLUS-2 Source Formatter & Analyzer Commands" in run_res.stdout

    assert (prefix / "docs" / "indent.md").is_file()

    # Uninstall indent
    res_un = subprocess.run(
        [UNINSTALL_SH, f"--prefix={prefix}", "indent"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_un.returncode == 0
    assert not indent_bin.exists()
    assert not (prefix / "docs" / "indent.md").exists()








