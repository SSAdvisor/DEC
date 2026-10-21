import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_FILEVIEW = APP_DIR / "bin" / "fileview"
BIN_ALIAS = APP_DIR / "bin" / "dxfileview"


def run_fileview(commands: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_FILEVIEW), commands],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(APP_DIR),
    )


def test_fileview_build():
    """1. Verify fileview and dxfileview build cleanly."""
    res = subprocess.run(["make", "build"], cwd=str(APP_DIR), capture_output=True, text=True, timeout=15)
    assert res.returncode == 0, f"Build failed:\n{res.stdout}\n{res.stderr}"
    assert BIN_FILEVIEW.is_file() and os.access(BIN_FILEVIEW, os.X_OK)
    assert BIN_ALIAS.exists()


def test_fileview_banner_repl():
    """2. Verify interactive REPL banner on stdin."""
    res = subprocess.run(
        [str(BIN_FILEVIEW)],
        input="EXIT\n",
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(APP_DIR),
    )
    assert res.returncode == 0
    assert "DECwindows FileView V3.0 (VUE$MASTER - Workstation File & DCL Manager)" in res.stdout


def test_fileview_help():
    """3. Verify HELP command output."""
    res = run_fileview("HELP; EXIT")
    assert res.returncode == 0
    assert "--- DECwindows FileView V3.0 (VUE$MASTER) Commands ---" in res.stdout
    assert "CREATE <name>|<blk>|<org>|<body>" in res.stdout
    assert "DELETE <n> / PURGE" in res.stdout


def test_fileview_sample_and_show():
    """4. Verify SAMPLE catalog loading and SHOW/PWD status."""
    res = run_fileview("SAMPLE; SHOW; EXIT")
    assert res.returncode == 0
    assert "%FILEVIEW-I-SAMPLE, loaded 7 VMS files across 3 directories into FileView." in res.stdout
    assert "Default Dir  : SYS$SYSROOT:[SYSMGR]" in res.stdout
    assert "Total Files  : 7 (Total Disk Blocks: 1609)" in res.stdout


def test_fileview_cd_filter_and_dir():
    """5. Verify CD, FILTER, and DIR directory listing."""
    res = run_fileview("SAMPLE; DIR; CD SYS$COMMON:[SYSEXE]; FILTER *.EXE; DIR; EXIT")
    assert res.returncode == 0
    assert "SYSTARTUP_V5.COM;4" in res.stdout
    assert "LOGIN.COM;1" in res.stdout
    assert "LOGIN.COM;2" in res.stdout
    assert "%FILEVIEW-I-SETDEF, default directory set to SYS$COMMON:[SYSEXE]." in res.stdout
    assert "%FILEVIEW-I-FILTER, file filter set to *.EXE." in res.stdout
    assert "DECW$SERVER.EXE;1" in res.stdout
    assert "Total of 1 file(s), 1420 block(s)." in res.stdout


def test_fileview_type_inspector():
    """6. Verify TYPE/VIEW file content and RMS attribute inspection."""
    res = run_fileview("SAMPLE; TYPE 7; EXIT")
    assert res.returncode == 0
    assert "File #7: DISK$USER:[CONKLIN.AXP]EV4_PALCODE.MAR;5" in res.stdout
    assert "RMS Organization: SEQ/VAR   Size: 85 blocks" in res.stdout
    assert ".TITLE EV4_PALCODE - Alpha 21064 Privileged Architecture Library" in res.stdout


def test_fileview_create_auto_versioning():
    """7. Verify CREATE auto-increments VMS file version numbers (;3)."""
    res = run_fileview(
        "SAMPLE; CREATE LOGIN.COM|8|SEQ/VAR|$ WRITE SYS$OUTPUT \"Login v3\"; TYPE 8; EXIT"
    )
    assert res.returncode == 0
    assert "%FILEVIEW-I-CREATED, created SYS$SYSROOT:[SYSMGR]LOGIN.COM;3 (8 blocks)." in res.stdout
    assert "File #8: SYS$SYSROOT:[SYSMGR]LOGIN.COM;3" in res.stdout


def test_fileview_copy_and_rename():
    """8. Verify COPY and RENAME operations."""
    res = run_fileview("SAMPLE; COPY 1 SYSTARTUP_BAK.COM; RENAME 8 SYSTARTUP_OLD.COM; DIR; EXIT")
    assert res.returncode == 0
    assert "%FILEVIEW-I-COPIED, copied #1 to SYS$SYSROOT:[SYSMGR]SYSTARTUP_BAK.COM;1." in res.stdout
    assert "%FILEVIEW-I-RENAMED, renamed SYSTARTUP_BAK.COM to SYSTARTUP_OLD.COM;1." in res.stdout
    assert "SYSTARTUP_OLD.COM;1" in res.stdout


def test_fileview_delete_and_purge():
    """9. Verify PURGE removes superseded versions (;1) and DELETE removes specific file."""
    res = run_fileview("SAMPLE; PURGE; DIR; DELETE 1; SHOW; EXIT")
    assert res.returncode == 0
    assert "%FILEVIEW-I-PURGED, purged 1 older file version(s)." in res.stdout
    assert "LOGIN.COM;2" in res.stdout
    assert "LOGIN.COM;1" not in res.stdout
    assert "%FILEVIEW-I-DELETED, deleted SYSTARTUP_V5.COM;4." in res.stdout
    assert "Total Files  : 5" in res.stdout


def test_fileview_protect_and_run_dcl():
    """10. Verify PROTECT UIC mask update and RUN / DCL subprocess execution."""
    res = run_fileview(
        "SAMPLE; PROTECT 1 (S:RWED,O:RWED,G:,W:); TYPE 1; RUN 1; DCL SHOW SYSTEM/CLUSTER; EXIT"
    )
    assert res.returncode == 0
    assert "%FILEVIEW-I-PROTSET, protection on SYSTARTUP_V5.COM set to (S:RWED,O:RWED,G:,W:)." in res.stdout
    assert "--- FileView DCL Subprocess: @SYS$SYSROOT:[SYSMGR]SYSTARTUP_V5.COM ---" in res.stdout
    assert "%SYSTEM-S-NORMAL, normal successful completion (PID 204001A4)" in res.stdout
    assert "--- FileView DCL Subprocess: $ SHOW SYSTEM/CLUSTER ---" in res.stdout


def test_fileview_search():
    """11. Verify SEARCH across filenames and file contents."""
    res = run_fileview("SAMPLE; SEARCH 21064; EXIT")
    assert res.returncode == 0
    assert "#7 DISK$USER:[CONKLIN.AXP]EV4_PALCODE.MAR;5 (85 blk)" in res.stdout
    assert "Total matches found: 1" in res.stdout


def test_fileview_display_and_export(tmp_path):
    """12. Verify Motif/XUI FileView window DISPLAY and PRINT ON export."""
    win_file = tmp_path / "fileview_win.txt"
    res = run_fileview(f"SAMPLE; DISPLAY; PRINT ON {win_file}; EXIT")
    assert res.returncode == 0
    assert "[X] DECwindows FileView:" in res.stdout
    assert "[Type/View]  [Run/Submit]  [Copy]  [Rename]  [Delete]  [Purge]  [Protect]" in res.stdout
    assert win_file.is_file()
    assert "[X] DECwindows FileView:" in win_file.read_text()


def test_fileview_save_and_load(tmp_path):
    """13. Verify SAVE and LOAD catalog persistence."""
    fvw_file = tmp_path / "catalog.fvw"
    res1 = run_fileview(f"SAMPLE; CREATE TEST.COM|5|SEQ/VAR|$ EXIT; SAVE {fvw_file}; EXIT")
    assert res1.returncode == 0
    assert "%FILEVIEW-I-SAVED, saved 8 files" in res1.stdout
    assert fvw_file.is_file()

    res2 = run_fileview(f"CLEAR; LOAD {fvw_file}; TYPE 8; EXIT")
    assert res2.returncode == 0
    assert "%FILEVIEW-I-LOADED, loaded 8 files" in res2.stdout
    assert "File #8: SYS$SYSROOT:[SYSMGR]TEST.COM;1" in res2.stdout
    assert "$ EXIT" in res2.stdout


def test_fileview_symlink_and_errors():
    """14. Verify dxfileview symlink execution and error handling."""
    res = subprocess.run(
        [str(BIN_ALIAS), "SAMPLE; TYPE 99; BOGUS_CMD; EXIT"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(APP_DIR),
    )
    assert res.returncode == 0
    assert "%FILEVIEW-E-INVFILE" in res.stdout
    assert "%FILEVIEW-E-INVCMD, unrecognized command: BOGUS_CMD" in res.stdout
