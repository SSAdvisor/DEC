import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(APP_DIR, "bin")
CARDFILER_BIN = os.path.join(BIN_DIR, "cardfiler")
DXCARDFILER_BIN = os.path.join(BIN_DIR, "dxcardfiler")


@pytest.fixture(scope="module", autouse=True)
def build_cardfiler():
    """Ensure cardfiler and its dxcardfiler alias are built before running tests."""
    res = subprocess.run(["make", "build"], cwd=APP_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"Build failed:\n{res.stdout}\n{res.stderr}"
    assert os.path.isfile(CARDFILER_BIN)
    assert os.path.exists(DXCARDFILER_BIN)


def run_cardfiler(commands, cwd=None):
    """Run cardfiler with semicolon-chained commands."""
    cmd_str = "; ".join(commands) if isinstance(commands, list) else commands
    res = subprocess.run(
        [CARDFILER_BIN, cmd_str],
        cwd=cwd or APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    return res.stdout


def test_help_and_commands():
    """Verify HELP displays Cardfiler command documentation."""
    out = run_cardfiler(["HELP", "EXIT"])
    assert "DECwindows Cardfiler Rotary Index Card Manager Commands" in out
    assert "SORT [INDEX|CATEGORY]" in out
    assert "DUP [id] / COPY [id]" in out


def test_sample_and_list():
    """Verify SAMPLE loads the 6 DEC directory cards and LIST displays them."""
    out = run_cardfiler(["SAMPLE", "LIST", "EXIT"])
    assert "[Sample DECwindows Cardfiler deck loaded: 6 index cards in DEC_DIRECTORY.CRD]" in out
    assert "Bell, Gordon" in out
    assert "Cutler, Dave" in out
    assert "Kronenberg, Nancy" in out
    assert "6 card(s) listed." in out


def test_list_filtered_by_category():
    """Verify LIST <category> filters cards by category."""
    out = run_cardfiler(["SAMPLE", "LIST VAX/VMS", "EXIT"])
    assert "Cutler, Dave" in out
    assert "1 card(s) listed." in out


def test_read_by_number_and_substring():
    """Verify READ locates cards both by numeric ID and by index header substring."""
    out = run_cardfiler(["SAMPLE", "READ 1", "READ Stewart", "EXIT"])
    assert "[Card #1 of 6] Index: Bell, Gordon" in out
    assert "[Card #4 of 6] Index: Stewart, Larry" in out
    assert "Cambridge Research Lab - Firefly Multiprocessor & DECstation 3100" in out


def test_next_and_prev_navigation():
    """Verify NEXT and PREV flip sequentially through the card deck."""
    out = run_cardfiler(["SAMPLE", "READ 2", "NEXT", "PREV", "EXIT"])
    assert "[Card #3 of 6] Index: Kronenberg, Nancy" in out
    assert "[Card #2 of 6] Index: Cutler, Dave" in out


def test_add_and_update_card():
    """Verify ADD creates a new index card and UPDATE modifies an existing card."""
    out = run_cardfiler([
        "SAMPLE",
        "ADD Sites, Dick|ALPHA_AXP|HLO::SITES (DTN 225-7000)|Alpha AXP Reference Architecture & Binary Translator",
        "READ 7",
        "UPDATE 7|Sites, Richard L.|ALPHA_AXP|HLO::SITES (DTN 225-7001)|Co-Architect of Alpha AXP & VEST Translator",
        "READ 7",
        "EXIT",
    ])
    assert "[Added Card #7: Sites, Dick (ALPHA_AXP)]" in out
    assert "[Updated Card #7: Sites, Richard L.]" in out
    assert "Co-Architect of Alpha AXP & VEST Translator" in out


def test_dup_and_delete_card():
    """Verify DUP duplicates a card and DELETE removes a card from the deck."""
    out = run_cardfiler(["SAMPLE", "DUP 1", "SHOW", "DELETE 7", "SHOW", "EXIT"])
    assert "[Duplicated Card #1 -> Card #7: Bell, Gordon (Copy)]" in out
    assert "Total Cards in Deck:    7 / 40 cards" in out
    assert "[Deleted Card #7: Bell, Gordon (Copy)]" in out
    assert "Total Cards in Deck:    6 / 40 cards" in out


def test_sort_by_index_and_category():
    """Verify SORT INDEX and SORT CATEGORY order the rotary deck."""
    out = run_cardfiler(["SAMPLE", "SORT CATEGORY", "READ 1", "SORT INDEX", "READ 1", "EXIT"])
    assert "[Sorted 6 index cards alphabetically by CATEGORY]" in out
    assert "[Card #1 of 6] Index: DECUS Program Library" in out
    assert "[Sorted 6 index cards alphabetically by INDEX]" in out
    assert "[Card #1 of 6] Index: Bell, Gordon" in out


def test_search_cards():
    """Verify SEARCH performs case-insensitive search across all card fields."""
    out = run_cardfiler(["SAMPLE", "SEARCH Firefly", "EXIT"])
    assert "DECwindows Cardfiler Search Results for 'Firefly'" in out
    assert "[Match #1] Card #4 [Stewart, Larry | ULTRIX] CRL::STEWART (DTN 226-8900)" in out
    assert "Total matching cards: 1" in out


def test_display_motif_window():
    """Verify DISPLAY renders the Motif/XUI Cardfiler window."""
    out = run_cardfiler(["SAMPLE", "READ 2", "DISPLAY", "EXIT"])
    assert "| [=] DECwindows Cardfiler - DEC_DIRECTORY.CRD" in out
    assert "|  File    Edit    Card    View    Search    Help" in out
    assert "| Index Tab: Cutler, Dave   [Card 2 of 6]" in out
    assert "| Category:  VAX/VMS   Node/Phone: ZKO::CUTLER (DTN 381-2001)" in out


def test_display_export_to_file(tmp_path):
    """Verify DISPLAY ON <file> exports the rendered Cardfiler window to disk."""
    out_file = tmp_path / "card_view.txt"
    out = run_cardfiler(["SAMPLE", f"DISPLAY ON {out_file}", "EXIT"], cwd=str(tmp_path))
    assert f"[Cardfiler window exported to {out_file}]" in out
    assert out_file.is_file()
    content = out_file.read_text()
    assert "DECwindows Cardfiler - DEC_DIRECTORY.CRD" in content
    assert "Index Tab: Bell, Gordon   [Card 1 of 6]" in content


def test_save_clear_and_load_deck(tmp_path):
    """Verify SAVE, CLEAR, and LOAD preserve all cards in .CRD format."""
    crd_file = tmp_path / "custom.crd"
    out = run_cardfiler([
        "SAMPLE",
        f"SAVE {crd_file}",
        "CLEAR",
        f"LOAD {crd_file}",
        "SHOW",
        "EXIT",
    ], cwd=str(tmp_path))
    assert f"[Saved 6 card(s) to {crd_file}]" in out
    assert "[Cardfiler deck cleared]" in out
    assert f"[Loaded 6 card(s) from {crd_file}]" in out
    assert "Total Cards in Deck:    6 / 40 cards" in out


def test_error_handling_empty_and_invalid_card():
    """Verify graceful error handling when deck is empty or card ID is invalid."""
    out = run_cardfiler(["CLEAR", "LIST", "SAMPLE", "DELETE 99", "EXIT"])
    assert "CARDFILER: Card deck is empty. Use SAMPLE, ADD, or LOAD first." in out
    assert "CARDFILER: Invalid card number." in out


def test_dxcardfiler_alias_execution():
    """Verify the dxcardfiler symlink alias executes Cardfiler."""
    res = subprocess.run(
        [DXCARDFILER_BIN, "SAMPLE; SHOW; EXIT"],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "DECwindows Cardfiler V3.0 - Rotary Deck & Card Status" in res.stdout
