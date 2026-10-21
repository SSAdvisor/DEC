import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_CDAVIEWER = APP_DIR / "bin" / "cdaviewer"
BIN_DXVDOC = APP_DIR / "bin" / "dxvdoc"


def run_cdaviewer(commands: str, binary: Path = BIN_CDAVIEWER, cwd: Path = APP_DIR) -> str:
    proc = subprocess.run(
        [str(binary)],
        input=commands + "\n",
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )
    assert proc.returncode == 0, f"cdaviewer failed: {proc.stderr}"
    return proc.stdout


def test_01_banner_and_help():
    out = run_cdaviewer("HELP\nEXIT")
    assert "DECwindows CDA Viewer V3.0 (DECW$CDAVIEWER / dxvdoc)" in out
    assert "--- DECwindows CDA Viewer V3.0 Commands ---" in out
    assert "INSPECT / ANALYZE / CHECK" in out
    assert "DECwindows CDA Viewer V3.0 session terminated." in out


def test_02_sample_and_show_status():
    out = run_cdaviewer("SAMPLE; SHOW; EXIT")
    assert "[Loaded Sample CDA Document: ALPHA_SPEC.DDIF (6 segments, 3 pages)]" in out
    assert "Document Name  : ALPHA_SPEC.DDIF" in out
    assert "CDA Format     : DDIF V1.2 (Compound Document)" in out
    assert "Author / Dept  : DEC Alpha Architecture Group (MRO)" in out
    assert "Current Page   : Page 1 of 3" in out
    assert "Total Segments : 6 compound segments" in out


def test_03_elements_list_all_and_filtered():
    out = run_cdaviewer("SAMPLE; ELEMENTS; ELEMENTS TEXT; EXIT")
    assert "DDIF$S_SEG_HDR (ISO-Latin-1)" in out
    assert "DTIF$S_TBL_SPEC (4x3 Matrix)" in out
    assert "DDIF$S_SEG_ISL (600x400 Sixel/ISL)" in out
    assert "Total segments listed: 6" in out
    assert "Total segments listed: 2" in out


def test_04_page_render_and_frames():
    out = run_cdaviewer("SAMPLE; PAGE 1; PAGE 2; EXIT")
    assert "=== CDA Page 1 of 3 : ALPHA_SPEC.DDIF (DDIF V1.2 (Compound Document)) ===" in out
    assert "[Seg #1 | HEADER | DDIF$S_SEG_HDR (ISO-Latin-1)]" in out
    assert "+--- [ISL/Sixel Image Frame] ------------------------------------+" in out
    assert "=== CDA Page 2 of 3 : ALPHA_SPEC.DDIF (DDIF V1.2 (Compound Document)) ===" in out
    assert "CHIP: 21064 (EV4) | CLOCK: 150-200 MHz | CACHE: 8KB I + 8KB D" in out


def test_05_next_and_prev_navigation():
    out = run_cdaviewer("SAMPLE; NEXT; NEXT; PREV; SHOW; EXIT")
    assert "=== CDA Page 3 of 3 : ALPHA_SPEC.DDIF (DDIF V1.2 (Compound Document)) ===" in out
    assert "DEC-AXP-ARCH-1992-REV1 | Digital Equipment Corporation, Maynard MA" in out
    assert "Current Page   : Page 2 of 3" in out


def test_06_pages_render_full_document():
    out = run_cdaviewer("SAMPLE; PAGES; EXIT")
    assert "=== CDA Page 1 of 3" in out
    assert "=== CDA Page 2 of 3" in out
    assert "=== CDA Page 3 of 3" in out


def test_07_addseg_new_segment_and_page_expansion():
    out = run_cdaviewer(
        "SAMPLE; ADDSEG 4|GRAPHIC|DDIF$S_SEG_ISL (Die Photo)|[IMAGE: 21064 CMOS-4 1.68M Transistors]; PAGE 4; EXIT"
    )
    assert "[Added CDA Segment #7 on Page 4: GRAPHIC (DDIF$S_SEG_ISL (Die Photo))]" in out
    assert "=== CDA Page 4 of 4 : ALPHA_SPEC.DDIF" in out
    assert "[IMAGE: 21064 CMOS-4 1.68M Transistors]" in out


def test_08_delseg_segment_removal():
    out = run_cdaviewer("SAMPLE; DELSEG 3; ELEMENTS; EXIT")
    assert "[Deleted CDA Segment #3: GRAPHIC (DDIF$S_SEG_ISL (600x400 Sixel/ISL))]" in out
    assert "Total segments listed: 5" in out


def test_09_inspect_conformance_audit():
    out = run_cdaviewer("SAMPLE; INSPECT; EXIT")
    assert "=== CDA Compound Document Conformance Audit ===" in out
    assert "Total Pages    : 3  |  Total Segments: 6" in out
    assert "DDIF Text Segs : 2  |  Header/Footer : 2" in out
    assert "DTIF Tables    : 1  |  ISL Graphics  : 1" in out
    assert "Audit Result   : CONFORMANT (ASN.1 TLV & DDIF/DTIF Descriptors Valid)" in out


def test_10_search_segments():
    out = run_cdaviewer("SAMPLE; SEARCH PALCODE; SEARCH DTIF; EXIT")
    assert "Seg #5 (Page 2) [TEXT | DDIF$S_SEG_TXT (PALcode Layer)]" in out
    assert "Seg #4 (Page 2) [TABLE | DTIF$S_TBL_SPEC (4x3 Matrix)]" in out
    assert "Total matching segments: 1" in out


def test_11_format_setting():
    out = run_cdaviewer("SAMPLE; FORMAT DTIF V1.1 (Tabular Interchange); SHOW; EXIT")
    assert "[CDA Presentation Format set to: DTIF V1.1 (Tabular Interchange)]" in out
    assert "CDA Format     : DTIF V1.1 (Tabular Interchange)" in out


def test_12_display_and_export_motif_window(tmp_path):
    win_file = tmp_path / "cdaviewer_win.txt"
    out = run_cdaviewer(f"SAMPLE; DISPLAY; EXPORT {win_file}; EXIT")
    assert "| [=] DECwindows CDA Viewer - ALPHA_SPEC.DDIF [DDIF V1.2 (Compound Doc [v][^] |" in out
    assert "| File  View  Navigate  Inspect  Options  Help                               |" in out
    assert f"[CDA Viewer window exported to {win_file}]" in out
    assert win_file.exists()
    content = win_file.read_text()
    assert "[HEADER #1] DDIF$S_SEG_HDR (ISO-Latin-1)" in content
    assert "Status: DDIF/DTIF Conformant" in content


def test_13_save_clear_and_load_persistence(tmp_path):
    cda_file = tmp_path / "alpha_doc.cda"
    out = run_cdaviewer(f"SAMPLE; SAVE {cda_file}; CLEAR; SHOW; LOAD {cda_file}; SHOW; EXIT")
    assert f"[Saved 6 CDA segments to {cda_file}]" in out
    assert "[CDA document cleared]" in out
    assert f"[Loaded 6 CDA segments from {cda_file} (ALPHA_SPEC.DDIF)]" in out
    assert "Total Segments : 6 compound segments" in out


def test_14_dxvdoc_symlink_execution():
    assert BIN_DXVDOC.exists() and os.access(BIN_DXVDOC, os.X_OK)
    out = run_cdaviewer("SAMPLE; INSPECT; EXIT", binary=BIN_DXVDOC)
    assert "DECwindows CDA Viewer V3.0" in out
    assert "CONFORMANT (ASN.1 TLV & DDIF/DTIF Descriptors Valid)" in out
