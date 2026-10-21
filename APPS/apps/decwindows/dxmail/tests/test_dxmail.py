import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_DXMAIL = APP_DIR / "bin" / "dxmail"
BIN_ALIAS = APP_DIR / "bin" / "decwinmail"


def run_dxmail(commands: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_DXMAIL), commands],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(APP_DIR),
    )


def test_dxmail_build():
    """1. Verify dxmail and decwinmail build cleanly."""
    res = subprocess.run(["make", "build"], cwd=str(APP_DIR), capture_output=True, text=True, timeout=15)
    assert res.returncode == 0, f"Build failed:\n{res.stdout}\n{res.stderr}"
    assert BIN_DXMAIL.is_file() and os.access(BIN_DXMAIL, os.X_OK)
    assert BIN_ALIAS.exists()


def test_dxmail_banner_repl():
    """2. Verify interactive REPL banner on stdin."""
    res = subprocess.run(
        [str(BIN_DXMAIL)],
        input="EXIT\n",
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(APP_DIR),
    )
    assert res.returncode == 0
    assert "DECwindows Mail V3.0 (DECW$MAIL - XUI/Motif Mail Cabinet & DDIF Viewer)" in res.stdout


def test_dxmail_help():
    """3. Verify HELP command output."""
    res = run_dxmail("HELP; EXIT")
    assert res.returncode == 0
    assert "--- DECwindows Mail V3.0 (DECW$MAIL) Commands ---" in res.stdout
    assert "CABINET / DRAWERS / FOLDERS" in res.stdout
    assert "SEND <to>|<subj>|<fmt>|<body>" in res.stdout


def test_dxmail_sample_and_show():
    """4. Verify SAMPLE cabinet loading and SHOW status."""
    res = run_dxmail("SAMPLE; SHOW; EXIT")
    assert res.returncode == 0
    assert "%DXMAIL-I-SAMPLE, loaded 6 messages into DECwindows Mail Cabinet" in res.stdout
    assert "Active Drawer : MAIN   Active Folder: INBOX" in res.stdout
    assert "Total Messages: 6 (Unread: 2, Wastebasket: 0)" in res.stdout


def test_dxmail_cabinet_hierarchy():
    """5. Verify CABINET / DRAWERS / FOLDERS hierarchy summary."""
    res = run_dxmail("SAMPLE; CABINET; EXIT")
    assert res.returncode == 0
    assert "=== DECwindows Mail Cabinet Hierarchy (SYS$LOGIN:DECW$MAIL.DAT) ===" in res.stdout
    assert "MAIN         INBOX           3      2      New & incoming electronic mail" in res.stdout
    assert "PROJECTS     ALPHA_OSF1      1      0      Alpha AXP & DEC OSF/1 engineering" in res.stdout


def test_dxmail_select_and_dir():
    """6. Verify SELECT folder switching and DIR header listing."""
    res = run_dxmail("SAMPLE; DIR; SELECT ALPHA_OSF1; DIR; EXIT")
    assert res.returncode == 0
    assert "MICA & Prism Kernel Review Notes" in res.stdout
    assert "[DDIF]  ZKO::CONKLIN" in res.stdout
    assert "%DXMAIL-I-SELECTED, opened drawer PROJECTS folder ALPHA_OSF1." in res.stdout
    assert "GEM Optimizing Backend PALcode Hooks" in res.stdout


def test_dxmail_read_next_prev_and_ddif():
    """7. Verify READ, DDIF stream detection, NEXT, and PREV navigation."""
    res = run_dxmail("SAMPLE; READ 1; NEXT; PREV; SHOW; EXIT")
    assert res.returncode == 0
    assert "Subject: MICA & Prism Kernel Review Notes" in res.stdout
    assert "[CDA Viewer Embedded Stream: DDIF Compound Document Segment]" in res.stdout
    assert "Alpha EV4 21064 booted multi-user OSF/1 in ZKO Lab 3." in res.stdout
    assert "Total Messages: 6 (Unread: 0, Wastebasket: 0)" in res.stdout


def test_dxmail_send_reply_forward():
    """8. Verify SEND (DDIF/TEXT), REPLY, and FORWARD operations."""
    res = run_dxmail(
        "SAMPLE; SEND ZKO::SUPNIK|NVAX Microcode Patch|DDIF|Patch v4.2 ready; "
        "REPLY 1|Benchmarks look solid; FORWARD 2|MLO::OLSEN|Great milestone!; SELECT SENT; DIR; EXIT"
    )
    assert res.returncode == 0
    assert "%DXMAIL-I-SENT, message #7 (DDIF) sent to ZKO::SUPNIK and filed in MAIN:SENT." in res.stdout
    assert "%DXMAIL-I-REPLIED, reply #8 sent to ZKO::CUTLER (RE: MICA & Prism Kernel Review Notes)." in res.stdout
    assert "%DXMAIL-I-FORWARDED, message #2 forwarded to MLO::OLSEN as #9." in res.stdout
    assert "NVAX Microcode Patch" in res.stdout
    assert "FWD: DEC OSF/1 V1.0 Alpha AXP Boot Milestone" in res.stdout


def test_dxmail_move_mark_unmark():
    """9. Verify MOVE across drawers/folders and MARK / UNMARK flags."""
    res = run_dxmail("SAMPLE; MARK 1; MOVE 1 PROJECTS:ALPHA_OSF1; SELECT ALPHA_OSF1; DIR; UNMARK 1; READ 1; EXIT")
    assert res.returncode == 0
    assert "%DXMAIL-I-MARKED, message #1 flagged as MARKED." in res.stdout
    assert "%DXMAIL-I-MOVED, message #1 filed into PROJECTS:ALPHA_OSF1." in res.stdout
    assert "%DXMAIL-I-UNMARKED, message #1 flag cleared (READ)." in res.stdout


def test_dxmail_delete_and_purge():
    """10. Verify DELETE to WASTEBASKET and PURGE permanent removal."""
    res = run_dxmail("SAMPLE; DELETE 1; DELETE 4; SELECT WASTEBASKET; DIR; PURGE; SHOW; EXIT")
    assert res.returncode == 0
    assert "%DXMAIL-I-DELETED, message #1 moved to MAIN:WASTEBASKET." in res.stdout
    assert "%DXMAIL-I-PURGED, permanently removed 2 message(s) from WASTEBASKET." in res.stdout
    assert "Total Messages: 4 (Unread: 1, Wastebasket: 0)" in res.stdout


def test_dxmail_search_and_extract(tmp_path):
    """11. Verify SEARCH full-text query and EXTRACT message to file."""
    ext_file = tmp_path / "msg3_paxos.txt"
    res = run_dxmail(f"SAMPLE; SEARCH Paxos; EXTRACT 3 {ext_file}; EXIT")
    assert res.returncode == 0
    assert "#3 [MAIN:INBOX] From: SRC::LAMPORT | Subj: Part-Time Parliament Consensus Draft" in res.stdout
    assert "Total matches found: 1" in res.stdout
    assert ext_file.is_file()
    content = ext_file.read_text()
    assert "From: SRC::LAMPORT" in content
    assert "Format: DDIF" in content
    assert "Paxos synod fault-tolerant protocol proof" in content


def test_dxmail_display_and_export(tmp_path):
    """12. Verify Motif/XUI window DISPLAY and PRINT ON file export."""
    win_file = tmp_path / "dxmail_win.txt"
    res = run_dxmail(f"SAMPLE; DISPLAY; PRINT ON {win_file}; EXIT")
    assert res.returncode == 0
    assert "[X] DECwindows Mail:" in res.stdout
    assert "[Read] [Send/New] [Reply] [Forward] [Move] [Delete] [Next] [Prev] [Search]" in res.stdout
    assert win_file.is_file()
    assert "[X] DECwindows Mail:" in win_file.read_text()


def test_dxmail_save_and_load(tmp_path):
    """13. Verify SAVE and LOAD cabinet persistence."""
    cab_file = tmp_path / "cabinet.dxm"
    res1 = run_dxmail(f"SAMPLE; SEND ZKO::TEST|Save Test|TEXT|Saved body; SAVE {cab_file}; EXIT")
    assert res1.returncode == 0
    assert "%DXMAIL-I-SAVED, saved 7 messages" in res1.stdout
    assert cab_file.is_file()

    res2 = run_dxmail(f"CLEAR; LOAD {cab_file}; READ 7; EXIT")
    assert res2.returncode == 0
    assert "%DXMAIL-I-LOADED, loaded 7 messages" in res2.stdout
    assert "Subject: Save Test" in res2.stdout
    assert "Saved body" in res2.stdout


def test_dxmail_symlink_and_errors():
    """14. Verify decwinmail symlink execution and error handling."""
    res = subprocess.run(
        [str(BIN_ALIAS), "SAMPLE; READ 99; BOGUS_CMD; EXIT"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(APP_DIR),
    )
    assert res.returncode == 0
    assert "%DXMAIL-E-INVMSG" in res.stdout
    assert "%DXMAIL-E-INVCMD, unrecognized command: BOGUS_CMD" in res.stdout
