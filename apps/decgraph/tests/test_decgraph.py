import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "decgraph.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
BOBJ_FILE = os.path.join(BUILD_DIR, "decgraph.bobj")
EXE_FILE = os.path.join(BIN_DIR, "decgraph")
GRAPH_LINK = os.path.join(BIN_DIR, "graph")
DECG_LINK = os.path.join(BIN_DIR, "decg")


def test_decgraph_build():
    """Verify that decgraph.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(BOBJ_FILE), f"Object file {BOBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(GRAPH_LINK), f"Symlink {GRAPH_LINK} not found"
    assert os.path.islink(DECG_LINK), f"Symlink {DECG_LINK} not found"


def test_decgraph_banner_repl():
    """Verify interactive REPL displays DECgraph banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "DECgraph V3.0 - Business & Scientific Graphics Presentation System" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11" in out
    assert "DECGRAPH>" in out


def test_decgraph_help():
    """Verify HELP command displays DECgraph commands."""
    res = subprocess.run([EXE_FILE, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DECgraph Graphics & Charting Commands" in res.stdout
    assert "TYPE" in res.stdout
    assert "DATA" in res.stdout
    assert "SAMPLE" in res.stdout
    assert "TITLE" in res.stdout
    assert "PLOT" in res.stdout
    assert "PRINT ON" in res.stdout
    assert "SAVE" in res.stdout
    assert "LOAD" in res.stdout


def test_decgraph_sample_and_show():
    """Verify SAMPLE command loads DEC sample revenue data and SHOW displays settings."""
    res = subprocess.run([EXE_FILE, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Sample dataset loaded - 4 quarterly points]" in res.stdout
    assert "DECgraph Configuration:" in res.stdout
    assert "Chart Type:   BAR" in res.stdout
    assert "Title:        Quarterly Revenue" in res.stdout
    assert "Subtitle:     Digital Equipment Corporation" in res.stdout
    assert "X-Axis:       Quarter" in res.stdout
    assert "Y-Axis:       Millions USD" in res.stdout
    assert "Data Points:  4" in res.stdout


def test_decgraph_chart_types_and_aliases():
    """Verify TYPE changes chart types and handles aliases and validation."""
    cmd = "TYPE VBAR; TYPE COLUMN; TYPE LINE; TYPE TREND; TYPE PIE; TYPE SHARE; TYPE SCATTER; TYPE XY; TYPE HBAR; TYPE BAR; TYPE FOOBAR; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Chart type set to VBAR]" in res.stdout
    assert "[Chart type set to LINE]" in res.stdout
    assert "[Chart type set to PIE]" in res.stdout
    assert "[Chart type set to SCATTER]" in res.stdout
    assert "[Chart type set to BAR]" in res.stdout
    assert "DECgraph: Unsupported chart type 'FOOBAR'" in res.stdout


def test_decgraph_plot_bar():
    """Verify horizontal BAR chart rendering."""
    res = subprocess.run([EXE_FILE, "SAMPLE; TYPE BAR; PLOT; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Quarterly Revenue" in res.stdout
    assert "Digital Equipment Corporation" in res.stdout
    assert "Q1           | **************** (45)" in res.stdout
    assert "Q2           | *************************** (78)" in res.stdout
    assert "Q3           | **************************************** (112)" in res.stdout
    assert "Q4           | ********************************* (95)" in res.stdout
    assert "Scale: Quarter" in res.stdout


def test_decgraph_plot_vbar():
    """Verify vertical column (VBAR) chart rendering."""
    res = subprocess.run([EXE_FILE, "SAMPLE; TYPE VBAR; PLOT; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Quarterly Revenue" in res.stdout
    assert "+-------+-------+-------+-------+" in res.stdout
    assert "Q1" in res.stdout and "Q2" in res.stdout and "Q3" in res.stdout and "Q4" in res.stdout
    assert "[Quarter]" in res.stdout
    assert "###" in res.stdout


def test_decgraph_plot_line():
    """Verify LINE chart rendering."""
    res = subprocess.run([EXE_FILE, "SAMPLE; TYPE LINE; PLOT; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Quarterly Revenue" in res.stdout
    assert "(*)" in res.stdout
    assert "+-------+-------+-------+-------+" in res.stdout
    assert "Q1" in res.stdout and "Q4" in res.stdout


def test_decgraph_plot_pie():
    """Verify PIE share chart rendering with percentages."""
    res = subprocess.run([EXE_FILE, "SAMPLE; TYPE PIE; PLOT; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Category        Value          Percent   Visual Share" in res.stdout
    assert "13.6%" in res.stdout
    assert "23.6%" in res.stdout
    assert "33.9%" in res.stdout
    assert "28.7%" in res.stdout
    assert "Total           330      100.0%" in res.stdout


def test_decgraph_custom_data_and_titles():
    """Verify custom titles, subtitles, axis labels, adding points, and listing."""
    cmd = (
        'CLEAR; TITLE "PDP-11 vs VAX"; SUBTITLE "Performance Benchmark"; '
        'XLABEL "Architecture"; YLABEL "MIPS"; '
        'DATA "PDP-11/70", 1.2; DATA "VAX-11/780", 1.0; DATA "MicroVAX-II", 0.9; '
        'SHOW; LIST; PLOT; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Title set to: PDP-11 vs VAX]" in res.stdout
    assert "[Subtitle set to: Performance Benchmark]" in res.stdout
    assert "[Point 1 added: PDP-11/70 = 1.2]" in res.stdout
    assert "[Point 2 added: VAX-11/780 = 1]" in res.stdout
    assert "Data Points:  3" in res.stdout
    assert "PDP-11/70" in res.stdout
    assert "VAX-11/780" in res.stdout
    assert "MicroVAX-II" in res.stdout


def test_decgraph_save_load(tmp_path):
    """Verify SAVE and LOAD file interchange."""
    data_file = str(tmp_path / "graph_data.dat")
    cmd = f'SAMPLE; SAVE {data_file}; CLEAR; SHOW; LOAD {data_file}; LIST; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[4 points saved to {data_file}]" in res.stdout
    assert "[Dataset and settings cleared]" in res.stdout
    assert f"[4 points loaded from {data_file}]" in res.stdout
    assert "Q1" in res.stdout and "Q4" in res.stdout

    # Verify content on disk
    with open(data_file) as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 4
    assert "Q1|45" in lines[0]


def test_decgraph_print_on_export(tmp_path):
    """Verify PRINT ON and EXPORT write charts to files."""
    export_file1 = str(tmp_path / "chart1.txt")
    export_file2 = str(tmp_path / "chart2.txt")
    cmd = (
        f'SAMPLE; TYPE VBAR; PRINT ON {export_file1}; '
        f'TYPE PIE; EXPORT {export_file2}; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[Chart written to {export_file1}]" in res.stdout
    assert f"[Chart written to {export_file2}]" in res.stdout

    assert os.path.isfile(export_file1)
    with open(export_file1) as f:
        c1 = f.read()
    assert "Quarterly Revenue" in c1
    assert "+-------+-------+-------+-------+" in c1

    assert os.path.isfile(export_file2)
    with open(export_file2) as f:
        c2 = f.read()
    assert "Category        Value          Percent   Visual Share" in c2
    assert "Total           330      100.0%" in c2


def test_decgraph_symlinks():
    """Verify graph and decg symlinks run correctly."""
    res_graph = subprocess.run([GRAPH_LINK, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_graph.returncode == 0
    assert "[Sample dataset loaded - 4 quarterly points]" in res_graph.stdout

    res_decg = subprocess.run([DECG_LINK, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_decg.returncode == 0
    assert "DECgraph Graphics & Charting Commands" in res_decg.stdout


def test_decgraph_error_handling():
    """Verify error messages for missing data or invalid syntax."""
    res1 = subprocess.run([EXE_FILE, "CLEAR; PLOT; EXIT"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "DECgraph: No data points loaded" in res1.stdout

    res2 = subprocess.run([EXE_FILE, "DATA; EXIT"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "DECgraph: Syntax is DATA <label>, <value>" in res2.stdout

    res3 = subprocess.run([EXE_FILE, "UNKNOWN_CMD; EXIT"], capture_output=True, text=True, timeout=10)
    assert res3.returncode == 0
    assert "DECgraph: Unknown command 'UNKNOWN_CMD'" in res3.stdout
