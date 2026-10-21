import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "menu11.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "menu11.obj")
EXE_FILE = os.path.join(BIN_DIR, "menu11")
MENU_LINK = os.path.join(BIN_DIR, "menu")
MCF_LINK = os.path.join(BIN_DIR, "mcf")


def test_menu11_build():
    """Verify that menu11.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE), f"Object file {OBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(MENU_LINK), f"Symlink {MENU_LINK} not found"
    assert os.path.islink(MCF_LINK), f"Symlink {MCF_LINK} not found"


def test_menu11_banner_repl():
    """Verify interactive REPL displays MENU-11 banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "MENU-11 V2.0 - DEC Menu Control & Application Dispatch Facility (MCF)" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / RSX-11M / VAX" in out
    assert "MENU>" in out


def test_menu11_help():
    """Verify HELP command displays MENU-11 commands."""
    res = subprocess.run([EXE_FILE, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "MENU-11 Menu Control & Dispatch Facility Commands" in res.stdout
    assert "MLB" in res.stdout
    assert "SELECT" in res.stdout
    assert "CREATE" in res.stdout
    assert "ADDOPT" in res.stdout
    assert "OPTIONS" in res.stdout
    assert "USER" in res.stdout
    assert "RUN" in res.stdout
    assert "LOG" in res.stdout
    assert "DISPLAY" in res.stdout


def test_menu11_sample_and_show():
    """Verify SAMPLE loads DEC sample menu library and SHOW displays status."""
    res = subprocess.run([EXE_FILE, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Sample MENU-11 Library loaded - 4 menus, 11 dispatch options]" in res.stdout
    assert "MENU-11 System Status:" in res.stdout
    assert "Menu Library:    MENU11.MLB" in res.stdout
    assert "Operator PPN:    [1,2] (Privilege:100)" in res.stdout
    assert "Active Menu:     #1 (MAIN_MENU - 5 options)" in res.stdout
    assert "Total Menus:     4 (Deleted: 1)" in res.stdout
    assert "Total Options:   11" in res.stdout


def test_menu11_mlb_dir_select_and_back():
    """Verify listing menus in MLB library, selecting menus, and returning via BACK."""
    cmd = "SAMPLE; MLB; SELECT 2; SELECT OFFICE_MENU; BACK; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "MENU-11 Menu Control Library (MLB)" in res.stdout
    assert "MAIN_MENU" in res.stdout
    assert "ACCT_MENU" in res.stdout
    assert "[Active menu set to #2: ACCT_MENU - DIBS-11 COMMERCIAL ACCOUNTING & ERP MENU (3 options)]" in res.stdout
    assert "[Active menu set to #3: OFFICE_MENU - DEC ALL-IN-1 OFFICE & DECISION SUPPORT MENU (3 options)]" in res.stdout
    assert "[Returned to parent menu #2: ACCT_MENU (3 options)]" in res.stdout


def test_menu11_create_and_addopt():
    """Verify CREATE and ADDOPT commands for defining custom menus and options."""
    cmd = (
        'SAMPLE; CREATE "ENG_MENU", "VAX ENGINEERING TOOLS MENU"; '
        'ADDOPT "1", "BASIC-PLUS-2 Compiler", "CHAIN", "SY:BASICC.TSK", 20; '
        'ADDOPT "2", "Return to Master", "SUBMENU", "MAIN_MENU", 10; '
        'OPTIONS; DISPLAY; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Menu #5 created: ENG_MENU (VAX ENGINEERING TOOLS MENU)]" in res.stdout
    assert "[MCF: Option '1' added to ENG_MENU (CHAIN -> SY:BASICC.TSK, Priv=20)]" in res.stdout
    assert "[MCF: Option '2' added to ENG_MENU (SUBMENU -> MAIN_MENU, Priv=10)]" in res.stdout
    assert "2 option(s) defined in menu ENG_MENU" in res.stdout
    assert "(CHAIN -> SY:BASICC.TSK)" in res.stdout


def test_menu11_options_describe():
    """Verify OPTIONS / DESCRIBE table listing."""
    res = subprocess.run([EXE_FILE, "SAMPLE; OPTIONS; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "MENU-11 Option Dispatch Table - Menu: MAIN_MENU" in res.stdout
    assert "ACCT_MENU" in res.stdout
    assert "SY:FMS11.TSK" in res.stdout
    assert "RUN $SYSTAT" in res.stdout
    assert "5 option(s) defined in menu MAIN_MENU" in res.stdout


def test_menu11_dispatch_submenu_and_chain():
    """Verify RUN/EXEC option dispatching for SUBMENU navigation and CHAIN task execution."""
    cmd = "SAMPLE; RUN 1; SHOW; RUN 1; RUN M; SHOW; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[MCF Dispatch: SUBMENU -> ACCT_MENU (Active menu is now #2: ACCT_MENU)]" in res.stdout
    assert "Active Menu:     #2 (ACCT_MENU - 3 options)" in res.stdout
    assert "[MCF Dispatch: CHAIN -> SY:DIBS11.TSK (Option 1: DIBS-11 General Ledger & Trial Balance)]" in res.stdout
    assert "[MCF Dispatch: SUBMENU -> MAIN_MENU (Active menu is now #1: MAIN_MENU)]" in res.stdout


def test_menu11_security_privilege_and_audit_log():
    """Verify USER operator PPN/privilege enforcement and MCF security audit log."""
    cmd = (
        "SAMPLE; USER [100,10], 10; RUN 9; RUN 4; "
        "USER [1,2], 100; RUN 9; LOG; EXIT"
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Operator context set: PPN=[100,10], Privilege Level=10]" in res.stdout
    assert "[MENU-11 Security Violation: Option '9' requires privilege level 100 (current: 10)]" in res.stdout
    assert "[MENU-11 Security Violation: Option '4' requires privilege level 50 (current: 10)]" in res.stdout
    assert "[MCF Dispatch: CCL -> RUN $SYSTAT (Option 9: System Operator Console)]" in res.stdout
    assert "SECURITY VIOLATION: PPN [100,10] denied option 9 on MAIN_MENU" in res.stdout
    assert "DISPATCH: PPN [1,2] executed CCL -> RUN $SYSTAT" in res.stdout


def test_menu11_display_and_export_file(tmp_path):
    """Verify rendering VT100 menu screen to terminal and exporting to disk file."""
    out_file = str(tmp_path / "main_menu.txt")
    cmd = f"SAMPLE; DISPLAY 1; PRINT ON {out_file}; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DEC RSTS/E V8.0 MASTER APPLICATION MENU  [MAIN_MENU]" in res.stdout
    assert "(SUBMENU -> ACCT_MENU)" in res.stdout
    assert f"[Menu MAIN_MENU rendered to {out_file}]" in res.stdout

    assert os.path.isfile(out_file)
    with open(out_file) as f:
        content = f.read()
    assert "DEC RSTS/E V8.0 MASTER APPLICATION MENU  [MAIN_MENU]" in content
    assert "FMS-11 Screen Forms Driver" in content


def test_menu11_delete_and_purge():
    """Verify deleting menus and purging the menu control library."""
    cmd = "SAMPLE; DELETE 3; SHOW; PURGE; SHOW; DIR; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Menu #3 (OFFICE_MENU) marked deleted]" in res.stdout
    assert "[Menu library purged - 2 deleted menu(s) removed]" in res.stdout
    assert "Total Menus:     2 (Deleted: 0)" in res.stdout


def test_menu11_save_and_load(tmp_path):
    """Verify saving and loading the MENU-11 menu library."""
    mlb_path = str(tmp_path / "custom.mlb")
    cmd = f"SAMPLE; SAVE {mlb_path}; CLEAR; SHOW; LOAD {mlb_path}; DIR; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[4 menu(s) saved to library {mlb_path}]" in res.stdout
    assert "[MENU-11 menu library cleared]" in res.stdout
    assert f"[4 menu(s) loaded from library {mlb_path}]" in res.stdout
    assert "MAIN_MENU" in res.stdout
    assert "4 menu(s) in library" in res.stdout


def test_menu11_symlinks():
    """Verify menu and mcf symlinks execute properly."""
    for link in [MENU_LINK, MCF_LINK]:
        res = subprocess.run([link, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
        assert res.returncode == 0
        assert "MENU-11 System Status:" in res.stdout


def test_menu11_error_handling():
    """Verify error messages for empty library, missing menus/options, and unknown commands."""
    res1 = subprocess.run([EXE_FILE, "CLEAR; DIR; EXIT"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "MENU-11: No menus in library" in res1.stdout

    res2 = subprocess.run([EXE_FILE, "SAMPLE; SELECT NO_SUCH_MENU; EXIT"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "MENU-11: Menu not found or out of range" in res2.stdout

    res3 = subprocess.run([EXE_FILE, "SAMPLE; RUN Z; EXIT"], capture_output=True, text=True, timeout=10)
    assert res3.returncode == 0
    assert "MENU-11: Option 'Z' not found in active menu MAIN_MENU" in res3.stdout

    res4 = subprocess.run([EXE_FILE, "UNKNOWN_CMD; EXIT"], capture_output=True, text=True, timeout=10)
    assert res4.returncode == 0
    assert "MENU-11: Unknown command 'UNKNOWN_CMD'" in res4.stdout
