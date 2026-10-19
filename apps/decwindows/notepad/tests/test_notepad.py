import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_NOTEPAD = APP_DIR / "bin" / "notepad"
BIN_ALIAS = APP_DIR / "bin" / "dxnotepad"


def run_notepad(commands: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_NOTEPAD), commands],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(APP_DIR),
    )


def test_notepad_build():
    """1. Verify notepad and dxnotepad build cleanly."""
    res = subprocess.run(["make", "build"], cwd=str(APP_DIR), capture_output=True, text=True, timeout=15)
    assert res.returncode == 0, f"Build failed:\n{res.stdout}\n{res.stderr}"
    assert BIN_NOTEPAD.is_file() and os.access(BIN_NOTEPAD, os.X_OK)
    assert BIN_ALIAS.exists()


def test_notepad_banner_repl():
    """2. Verify interactive REPL banner on stdin."""
    res = subprocess.run(
        [str(BIN_NOTEPAD)],
        input="EXIT\n",
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(APP_DIR),
    )
    assert res.returncode == 0
    assert "DECwindows Notepad V3.0 (DECW$NOTEPAD - Motif Text & Clipboard Editor)" in res.stdout


def test_notepad_help():
    """3. Verify HELP command output."""
    res = run_notepad("HELP; EXIT")
    assert res.returncode == 0
    assert "--- DECwindows Notepad V3.0 (DECW$NOTEPAD) Commands ---" in res.stdout
    assert "COPY <start> [end]" in res.stdout
    assert "REPLACE <old>|<new>" in res.stdout


def test_notepad_sample_and_stats():
    """4. Verify SAMPLE buffer loading and STATS/SHOW metrics."""
    res = run_notepad("SAMPLE; STATS; EXIT")
    assert res.returncode == 0
    assert "%NOTEPAD-I-SAMPLE, loaded 6 lines into SYS$LOGIN:AXP_NOTES.TXT." in res.stdout
    assert "Document File : SYS$LOGIN:AXP_NOTES.TXT (CLEAN, READ-WRITE)" in res.stdout
    assert "6 lines," in res.stdout


def test_notepad_list_and_append():
    """5. Verify LIST and APPEND operations."""
    res = run_notepad("SAMPLE; APPEND 5. Verify DECnet Phase V transport.; LIST; STATS; EXIT")
    assert res.returncode == 0
    assert "%NOTEPAD-I-APPENDED, appended line #7." in res.stdout
    assert "> 7: 5. Verify DECnet Phase V transport." in res.stdout
    assert "(MODIFIED, READ-WRITE)" in res.stdout


def test_notepad_insert_edit_delete():
    """6. Verify INSERT, EDIT, and DELETE line range operations."""
    res = run_notepad(
        "SAMPLE; INSERT 3|0. Check EV4 clock crystal.; EDIT 1|Updated Header Line; DELETE 2 3; LIST; EXIT"
    )
    assert res.returncode == 0
    assert "%NOTEPAD-I-INSERTED, inserted line #3." in res.stdout
    assert "%NOTEPAD-I-EDITED, updated line #1." in res.stdout
    assert "%NOTEPAD-I-DELETED, deleted 2 line(s)." in res.stdout
    assert "1: Updated Header Line" in res.stdout


def test_notepad_clipboard_copy_cut_paste():
    """7. Verify COPY, CUT, PASTE, and CLIPBOARD (DECW$CLIPBOARD) operations."""
    res = run_notepad("SAMPLE; COPY 3 4; CLIPBOARD; PASTE 6; CUT 1; LIST; EXIT")
    assert res.returncode == 0
    assert "%NOTEPAD-I-COPIED, copied 2 line(s) to DECW$CLIPBOARD." in res.stdout
    assert "=== DECwindows Clipboard (DECW$CLIPBOARD: 2 lines) ===" in res.stdout
    assert "%NOTEPAD-I-PASTED, pasted 2 line(s) from DECW$CLIPBOARD." in res.stdout
    assert "%NOTEPAD-I-CUT, cut 1 line(s) to DECW$CLIPBOARD." in res.stdout


def test_notepad_find_and_replace():
    """8. Verify FIND search and REPLACE global substitution."""
    res = run_notepad("SAMPLE; FIND Framebuffer; REPLACE V5.5|V5.5-2; LIST; EXIT")
    assert res.returncode == 0
    assert "Line 4 (Col 57): 2. Test compound string Latin-1 font rendering on HX/TX Framebuffer." in res.stdout
    assert "Total matches found: 1" in res.stdout
    assert "%NOTEPAD-I-REPLACED, replaced 1 occurrence(s) of 'V5.5' with 'V5.5-2'." in res.stdout
    assert "3. Confirm VMS V5.5-2 and DEC OSF/1 V1.0 file interchange compatibility." in res.stdout


def test_notepad_word_wrap():
    """9. Verify WRAP column reflowing and WRAP OFF."""
    res = run_notepad("SAMPLE; WRAP 40; STATS; WRAP OFF; EXIT")
    assert res.returncode == 0
    assert "%NOTEPAD-I-WRAP, word-wrap margin set to column 40 (Lines: 12)." in res.stdout
    assert "Word-Wrap Col: 40" in res.stdout
    assert "%NOTEPAD-I-WRAP, word-wrap disabled." in res.stdout


def test_notepad_readonly_protection():
    """10. Verify READONLY ON blocks modifications and READONLY OFF restores editing."""
    res = run_notepad("SAMPLE; READONLY ON; APPEND Should fail; DELETE 1; READONLY OFF; APPEND Should work; EXIT")
    assert res.returncode == 0
    assert "%NOTEPAD-I-READONLY, Read-Only mode set to 1." in res.stdout
    assert "%NOTEPAD-E-READONLY, buffer is locked read-only." in res.stdout
    assert "%NOTEPAD-I-APPENDED, appended line #7." in res.stdout


def test_notepad_display_and_export(tmp_path):
    """11. Verify Motif/XUI Notepad window DISPLAY and PRINT ON export."""
    win_file = tmp_path / "notepad_win.txt"
    res = run_notepad(f"SAMPLE; DISPLAY; PRINT ON {win_file}; EXIT")
    assert res.returncode == 0
    assert "[X] DECwindows Notepad:" in res.stdout
    assert "[Cut]  [Copy]  [Paste]  [Find]  [Replace]" in res.stdout
    assert win_file.is_file()
    assert "[X] DECwindows Notepad:" in win_file.read_text()


def test_notepad_save_and_load(tmp_path):
    """12. Verify SAVE and LOAD text file persistence."""
    doc_file = tmp_path / "saved_notes.txt"
    res1 = run_notepad(f"SAMPLE; APPEND Saved extra line; SAVE {doc_file}; EXIT")
    assert res1.returncode == 0
    assert "%NOTEPAD-I-SAVED, saved 7 lines" in res1.stdout
    assert doc_file.is_file()

    res2 = run_notepad(f"CLEAR; LOAD {doc_file}; LIST; EXIT")
    assert res2.returncode == 0
    assert "%NOTEPAD-I-LOADED, loaded 7 lines" in res2.stdout
    assert "7: Saved extra line" in res2.stdout


def test_notepad_clear_and_empty_clipboard():
    """13. Verify CLEAR and empty clipboard warning."""
    res = run_notepad("CLEAR; PASTE; LIST; EXIT")
    assert res.returncode == 0
    assert "%NOTEPAD-I-CLEARED, Notepad document buffer cleared." in res.stdout
    assert "%NOTEPAD-W-CLIPEMPTY, DECW$CLIPBOARD is empty." in res.stdout
    assert "(Buffer is empty)" in res.stdout


def test_notepad_symlink_and_errors():
    """14. Verify dxnotepad symlink execution and error handling."""
    res = subprocess.run(
        [str(BIN_ALIAS), "SAMPLE; EDIT 99|Bad; DELETE 9 2; BOGUS_CMD; EXIT"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(APP_DIR),
    )
    assert res.returncode == 0
    assert "%NOTEPAD-E-INVLINE" in res.stdout
    assert "%NOTEPAD-E-INVRANGE" in res.stdout
    assert "%NOTEPAD-E-INVCMD, unrecognized command: BOGUS_CMD" in res.stdout
