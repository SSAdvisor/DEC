import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(APP_DIR, "bin")
DECTERM_BIN = os.path.join(BIN_DIR, "decterm")
DXTERM_BIN = os.path.join(BIN_DIR, "dxterm")


@pytest.fixture(scope="module", autouse=True)
def build_decterm():
    """Ensure decterm and its dxterm alias are built before running tests."""
    res = subprocess.run(["make", "build"], cwd=APP_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"Build failed:\n{res.stdout}\n{res.stderr}"
    assert os.path.isfile(DECTERM_BIN)
    assert os.path.exists(DXTERM_BIN)


def run_decterm(commands, cwd=None):
    """Run decterm with a semicolon-chained command string or stdin lines."""
    cmd_str = "; ".join(commands) if isinstance(commands, list) else commands
    res = subprocess.run(
        [DECTERM_BIN, cmd_str],
        cwd=cwd or APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    return res.stdout


def test_help_and_banner():
    """Verify HELP command output and DECterm command reference."""
    out = run_decterm(["HELP", "EXIT"])
    assert "DECwindows DECterm Terminal Emulator Commands" in out
    assert "MODE VT300|VT220|VT100|VT52" in out
    assert "DEFKEY <key> <macro>" in out


def test_sample_and_history():
    """Verify SAMPLE loads the VAX/VMS VT300 session and HISTORY lists SGR attributes."""
    out = run_decterm(["SAMPLE", "HISTORY", "EXIT"])
    assert "[Sample DECterm VT300 session loaded - 10 screen lines, 4 UDK bindings]" in out
    assert "Welcome to VAX/VMS V5.5-2 on node STAR::" in out
    assert "BOLD" in out
    assert "REV" in out
    assert "UNDL" in out


def test_screen_rendering():
    """Verify SCREEN renders the Motif/XUI DECterm window with menu bar and status bar."""
    out = run_decterm(["SAMPLE", "SCREEN", "EXIT"])
    assert "| [=] DECterm - VAXcluster Node STAR:: (VT300)" in out
    assert "|  Commands    Setup    Edit    Customize    Window    Help" in out
    assert "[Online] [VT300] [80x24] [Cursor:BLOCK] [Wrap:ON]" in out


def test_send_and_escape_sequence_attributes():
    """Verify SEND parses ANSI/VT CSI SGR sequences (BOLD, UNDL, REV, NORM)."""
    out = run_decterm([
        "SEND \"ESC[1mSystem Alert: Disk Quota ExceededESC[0m\"",
        "SEND \"ESC[4mDirectory DUA0:[SYSMGR]ESC[0m\"",
        "SEND \"ESC[7m Operator Message ESC[0m\"",
        "SEND \"$ DIRECTORY /SIZE\"",
        "HISTORY",
        "EXIT",
    ])
    assert "[DECterm line #1 (BOLD):" in out
    assert "[DECterm line #2 (UNDL):" in out
    assert "[DECterm line #3 (REV):" in out
    assert "[DECterm line #4 (NORM):" in out


def test_send_clear_screen_csi():
    """Verify ESC[2J Erase in Display clears previous scrollback lines."""
    out = run_decterm([
        "SAMPLE",
        "SEND \"ESC[2J$ SHOW TIME\"",
        "HISTORY",
        "EXIT",
    ])
    assert "DECterm Scrollback & Attribute Transcript (1 lines)" in out
    assert "$ SHOW TIME" in out


def test_delline():
    """Verify DELLINE removes a specific line from the scrollback buffer."""
    out = run_decterm(["SAMPLE", "DELLINE 2", "SHOW", "EXIT"])
    assert "[Deleted scrollback line #2:" in out
    assert "Scrollback Transcript:  9 / 500 lines" in out


def test_terminal_emulation_modes():
    """Verify MODE switches between VT300, VT220, VT100, and VT52."""
    out = run_decterm(["MODE VT220", "MODE VT100", "MODE VT52", "SHOW", "EXIT"])
    assert "[Terminal emulation mode set to VT220]" in out
    assert "[Terminal emulation mode set to VT100]" in out
    assert "[Terminal emulation mode set to VT52]" in out
    assert "Terminal Emulation:     VT52" in out


def test_columns_and_rows_geometry():
    """Verify COLUMNS (80/132) and ROWS (24/36/48) setup options."""
    out = run_decterm(["COLUMNS 132", "ROWS 48", "SAMPLE", "SCREEN", "EXIT"])
    assert "[Terminal display width set to 132 columns]" in out
    assert "[Terminal page length set to 48 rows]" in out
    assert "[Online] [VT300] [132x48]" in out


def test_cursor_autowrap_and_title():
    """Verify CURSOR, AUTOWRAP, and TITLE customization."""
    out = run_decterm([
        "CURSOR UNDERLINE",
        "AUTOWRAP OFF",
        "TITLE \"DECterm - ULTRIX V4.2 Session\"",
        "SAMPLE",
        "TITLE \"DECterm - ULTRIX V4.2 Session\"",
        "SCREEN",
        "EXIT",
    ])
    assert "[Terminal cursor style set to UNDERLINE]" in out
    assert "[DECCAWM Auto-Wrap mode set to OFF]" in out
    assert "| [=] DECterm - ULTRIX V4.2 Session" in out
    assert "[Cursor:UNDERLINE] [Wrap:OFF]" in out


def test_udk_defkey_keys_and_press():
    """Verify programming and triggering VT300 User-Defined Keys (DECUDK)."""
    out = run_decterm([
        "SAMPLE",
        "DEFKEY F7 \"SHOW MEMORY /PHYSICAL\"",
        "KEYS",
        "PRESS F7",
        "HISTORY",
        "EXIT",
    ])
    assert "[UDK key F7 programmed -> SHOW MEMORY /PHYSICAL]" in out
    assert "F7      SHOW MEMORY /PHYSICAL" in out
    assert "[Key F7 transmitted: $ SHOW MEMORY /PHYSICAL]" in out
    assert "$ SHOW MEMORY /PHYSICAL" in out


def test_inspect_conformance_audit():
    """Verify INSPECT reports ANSI/VT escape sequence and SGR attribute counts."""
    out = run_decterm(["SAMPLE", "INSPECT", "EXIT"])
    assert "DECterm ANSI/VT Escape Sequence & Attribute Conformance Audit" in out
    assert "Total Buffer Lines:     10" in out
    assert "ANSI/CSI Escape Lines:  3" in out
    assert "Bold Lines (SGR 1):     1" in out
    assert "Underline Lines (SGR 4):1" in out
    assert "Reverse Video (SGR 7):  1" in out
    assert "[Audit PASSED: VT300 parser verified all CSI/SGR control sequences]" in out


def test_screen_export_to_file(tmp_path):
    """Verify SCREEN ON <file> exports the rendered DECterm window to disk."""
    export_file = tmp_path / "decterm_screen.txt"
    out = run_decterm(["SAMPLE", f"SCREEN ON {export_file}", "EXIT"], cwd=str(tmp_path))
    assert f"[DECterm window screen exported to {export_file}]" in out
    assert export_file.is_file()
    content = export_file.read_text()
    assert "DECterm - VAXcluster Node STAR:: (VT300)" in content
    assert "[Online] [VT300] [80x24]" in content


def test_save_clear_and_load_session(tmp_path):
    """Verify SAVE, CLEAR (DECSTR reset), and LOAD restore session lines."""
    sess_file = tmp_path / "session.log"
    out = run_decterm([
        "SAMPLE",
        f"SAVE {sess_file}",
        "CLEAR",
        f"LOAD {sess_file}",
        "INSPECT",
        "EXIT",
    ], cwd=str(tmp_path))
    assert f"[Saved 10 terminal line(s) to {sess_file}]" in out
    assert "[DECSTR Soft Terminal Reset complete - screen and settings restored]" in out
    assert f"[Loaded 10 terminal line(s) from {sess_file}]" in out
    assert "Total Buffer Lines:     10" in out


def test_dxterm_alias_execution():
    """Verify that the dxterm symlink alias launches DECterm properly."""
    res = subprocess.run(
        [DXTERM_BIN, "SAMPLE; SHOW; EXIT"],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "DECwindows DECterm V3.0 - Terminal Setup & Session Status" in res.stdout
