import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(APP_DIR, "bin")
BOOKREADER_BIN = os.path.join(BIN_DIR, "bookreader")
DXBOOK_BIN = os.path.join(BIN_DIR, "dxbook")


@pytest.fixture(scope="module", autouse=True)
def build_bookreader():
    """Ensure bookreader and its dxbook alias are built before running tests."""
    res = subprocess.run(["make", "build"], cwd=APP_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"Build failed:\n{res.stdout}\n{res.stderr}"
    assert os.path.isfile(BOOKREADER_BIN)
    assert os.path.exists(DXBOOK_BIN)


def run_bookreader(commands, cwd=None):
    """Run bookreader with semicolon-chained commands."""
    cmd_str = "; ".join(commands) if isinstance(commands, list) else commands
    res = subprocess.run(
        [BOOKREADER_BIN, cmd_str],
        cwd=cwd or APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    return res.stdout


def test_help_and_commands():
    """Verify HELP displays Bookreader command documentation."""
    out = run_bookreader(["HELP", "EXIT"])
    assert "DECwindows Bookreader Online Documentation Commands" in out
    assert "SHELF / BOOKS" in out
    assert "FOLLOW / HOTSPOT" in out


def test_sample_and_shelf():
    """Verify SAMPLE loads the 3 DECwindows manuals and SHELF lists them."""
    out = run_bookreader(["SAMPLE", "SHELF", "EXIT"])
    assert "[Sample DECwindows Bookshelf loaded: 3 books, 6 hypertext topics, 2 bookmarks]" in out
    assert "VMS_DCL" in out
    assert "DECWIN_USER" in out
    assert "BP2_REF" in out


def test_open_book_and_toc():
    """Verify OPEN selects a specific book and TOC lists its topics."""
    out = run_bookreader(["SAMPLE", "OPEN DECWIN_USER", "TOC", "EXIT"])
    assert "[Opened Book #2: DECwindows Desktop User's Guide (DECW$BOOK) (DECWIN_USER)]" in out
    assert "Using the DECwindows Session Manager" in out
    assert "Navigating Hypertext Bookshelves" in out
    assert "Overview of Digital Command Language" not in out


def test_toc_all():
    """Verify TOC ALL lists topics across all manuals on the bookshelf."""
    out = run_bookreader(["SAMPLE", "TOC ALL", "EXIT"])
    assert "DECwindows Bookreader Table of Contents - All Books" in out
    assert "Overview of Digital Command Language" in out
    assert "Task-Builder and Overlay Compilation" in out


def test_read_by_id_and_section():
    """Verify READ by topic number and by section number (e.g. 3.1)."""
    out = run_bookreader(["SAMPLE", "READ 3.1", "EXIT"])
    assert "[Topic #5 | BP2_REF Sec 3.1] RMS Indexed and Sequential File I/O" in out
    assert "OPEN file FOR INPUT or OUTPUT with MAP buffers and primary keys." in out


def test_next_and_prev_navigation():
    """Verify NEXT and PREV step sequentially through hypertext topics."""
    out = run_bookreader(["SAMPLE", "READ 1", "NEXT", "PREV", "EXIT"])
    assert "[Topic #2 | VMS_DCL Sec 1.2] SET TERMINAL Command Qualifiers" in out
    assert "[Topic #1 | VMS_DCL Sec 1.1] Overview of Digital Command Language" in out


def test_follow_hotspot_cross_reference():
    """Verify FOLLOW jumps to the cross-referenced Hotspot section."""
    out = run_bookreader(["SAMPLE", "READ 2", "FOLLOW", "EXIT"])
    assert "[Followed Hotspot Link -> Section 2.1 (Topic #3)]" in out
    assert "[Topic #3 | DECWIN_USER Sec 2.1] Using the DECwindows Session Manager" in out


def test_full_text_search():
    """Verify SEARCH performs case-insensitive search across titles and bodies."""
    out = run_bookreader(["SAMPLE", "SEARCH basiclink", "EXIT"])
    assert "DECwindows Bookreader Full-Text Search Results for 'basiclink'" in out
    assert "[Match #1] Topic #6 (BP2_REF 3.2): Task-Builder and Overlay Compilation" in out
    assert "Total matching topics: 1" in out


def test_bookmark_and_bookmarks_list():
    """Verify BOOKMARK adds a reader bookmark and MARKS lists all bookmarks."""
    out = run_bookreader([
        "SAMPLE",
        "READ 3",
        "BOOKMARK \"Session Manager startup notes\"",
        "MARKS",
        "EXIT",
    ])
    assert "[Bookmark #3 saved for Topic #3 (2.1): Session Manager startup notes]" in out
    assert "DECwindows Bookreader Saved Bookmarks (3)" in out
    assert "Session Manager startup notes" in out


def test_addbook_addtopic_and_deltopic():
    """Verify ADDBOOK, ADDTOPIC, and DELTOPIC manage custom documentation."""
    out = run_bookreader([
        "SAMPLE",
        "ADDBOOK ULTRIX_MAN|ULTRIX-32 System Management Guide",
        "ADDTOPIC 4.1|Disk Partitioning|Use chpt to configure RZ25 disk partitions.|1.1",
        "READ 7",
        "DELTOPIC 7",
        "SHOW",
        "EXIT",
    ])
    assert "[Added Book #4: ULTRIX_MAN - ULTRIX-32 System Management Guide]" in out
    assert "[Added Topic #7 (4.1): Disk Partitioning]" in out
    assert "Use chpt to configure RZ25 disk partitions." in out
    assert "[Deleted Topic #7: Disk Partitioning]" in out
    assert "Total Hypertext Topics: 6" in out


def test_display_motif_window():
    """Verify DISPLAY renders the Motif/XUI Bookreader topic window."""
    out = run_bookreader(["SAMPLE", "READ 1", "DISPLAY", "EXIT"])
    assert "| [=] DECwindows Bookreader - VAX/VMS DCL Dictionary (DECW$BOOK)" in out
    assert "|  File    View    Search    Bookmark    Link    Options    Help" in out
    assert "| Section 1.1 - Overview of Digital Command Language" in out
    assert "| [<< Prev Topic]  [Next Topic >>]  [Book: VMS_DCL]" in out


def test_display_export_to_file(tmp_path):
    """Verify DISPLAY ON <file> exports the rendered Bookreader window to disk."""
    out_file = tmp_path / "book_topic.txt"
    out = run_bookreader(["SAMPLE", f"DISPLAY ON {out_file}", "EXIT"], cwd=str(tmp_path))
    assert f"[Bookreader topic window exported to {out_file}]" in out
    assert out_file.is_file()
    content = out_file.read_text()
    assert "DECwindows Bookreader - VAX/VMS DCL Dictionary" in content
    assert "[Hotspot Link -> Section 1.2]" in content


def test_save_clear_and_load_bookshelf(tmp_path):
    """Verify SAVE, CLEAR, and LOAD preserve books and hypertext topics."""
    bks_file = tmp_path / "custom.bks"
    out = run_bookreader([
        "SAMPLE",
        f"SAVE {bks_file}",
        "CLEAR",
        f"LOAD {bks_file}",
        "SHOW",
        "EXIT",
    ], cwd=str(tmp_path))
    assert f"[Saved 3 book(s) and 6 topic(s) to {bks_file}]" in out
    assert "[Bookshelf, topics, and bookmarks cleared]" in out
    assert f"[Loaded 3 book(s) and 6 topic(s) from {bks_file}]" in out
    assert "Total Books on Shelf:   3" in out
    assert "Total Hypertext Topics: 6" in out


def test_dxbook_alias_execution():
    """Verify the dxbook symlink alias executes Bookreader."""
    res = subprocess.run(
        [DXBOOK_BIN, "SAMPLE; SHOW; EXIT"],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "DECwindows Bookreader V3.0 - Library & Viewer Status" in res.stdout
