import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "ade.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
BOBJ_FILE = os.path.join(BUILD_DIR, "ade.bobj")
EXE_FILE = os.path.join(BIN_DIR, "ade")

def test_ade_build():
    """Verify that ade.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(BOBJ_FILE), f"Object file {BOBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"

def test_ade_help():
    """Verify HELP command displays ADE banner and all documented commands."""
    res = subprocess.run([EXE_FILE, "HELP"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "ADE V3.0 - Application Development Environment" in res.stdout
    assert "CREATE" in res.stdout
    assert "USE" in res.stdout
    assert "ADD" in res.stdout
    assert "LIST" in res.stdout
    assert "FIND" in res.stdout
    assert "CHANGE" in res.stdout
    assert "DELETE" in res.stdout
    assert "SORT" in res.stdout
    assert "STATS" in res.stdout
    assert "REPORT" in res.stdout
    assert "GRAPH" in res.stdout
    assert "EXPORT" in res.stdout
    assert "IMPORT" in res.stdout
    assert "SHOW" in res.stdout
    assert "EXIT" in res.stdout

def test_ade_create_default_schema(tmp_path):
    """Test CREATE table with DEC ADE default schema (ID, NAME, DEPT, SALARY, HIREDATE)."""
    res = subprocess.run([EXE_FILE, "CREATE EMPLOYEES"], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Database 'EMPLOYEES' created successfully (Fields: 5)." in res.stdout

    sch_file = tmp_path / "EMPLOYEES.sch"
    dat_file = tmp_path / "EMPLOYEES.dat"
    assert sch_file.is_file()
    assert dat_file.is_file()

    sch_content = sch_file.read_text().splitlines()
    assert sch_content[0].strip() == "5"
    assert "ID|N|6" in sch_content[1]
    assert "NAME|C|20" in sch_content[2]
    assert "DEPT|C|12" in sch_content[3]
    assert "SALARY|N|10" in sch_content[4]
    assert "HIREDATE|D|10" in sch_content[5]

def test_ade_create_custom_schema(tmp_path):
    """Test CREATE table with custom field specifications."""
    cmd = "CREATE ITEMS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4)"
    res = subprocess.run([EXE_FILE, cmd], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Database 'ITEMS' created successfully (Fields: 4)." in res.stdout

    sch_file = tmp_path / "ITEMS.sch"
    sch_content = sch_file.read_text().splitlines()
    assert sch_content[0].strip() == "4"
    assert "SKU|N|6" in sch_content[1]
    assert "NAME|C|15" in sch_content[2]
    assert "PRICE|N|8" in sch_content[3]
    assert "QTY|N|4" in sch_content[4]

def test_ade_add_and_list(tmp_path):
    """Test ADD records and LIST formatted table."""
    cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,45,50; "
        "ADD 1003,GIZMO,15,200; "
        "LIST"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Record 1 added." in res.stdout
    assert "Record 2 added." in res.stdout
    assert "Record 3 added." in res.stdout
    assert "Database: PRODS (Total Records: 3)" in res.stdout
    assert "REC#  SKU    NAME            PRICE    QTY" in res.stdout
    assert "1     1001   WIDGET          25       100" in res.stdout
    assert "2     1002   GADGET          45       50" in res.stdout
    assert "3     1003   GIZMO           15       200" in res.stdout
    assert "3 record(s) listed." in res.stdout

def test_ade_find(tmp_path):
    """Test FIND command searching for substring values in specific fields."""
    cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,45,50; "
        "ADD 1003,GIZMO,15,200; "
        "FIND NAME GAD"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Search matches for NAME containing 'GAD':" in res.stdout
    assert "[Rec 2] 1002|GADGET|45|50" in res.stdout
    assert "1 matching record(s) found." in res.stdout

def test_ade_change(tmp_path):
    """Test CHANGE command modifying record fields."""
    setup_cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100"
    )
    res_setup = subprocess.run([EXE_FILE, setup_cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res_setup.returncode == 0

    # Piped input: keep SKU (empty), change NAME to MEGAWIDGET, change PRICE to 35, keep QTY (empty)
    change_input = "\nMEGAWIDGET\n35\n\n"
    res_change = subprocess.run(
        [EXE_FILE, "USE PRODS; CHANGE 1; LIST"],
        input=change_input,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_change.returncode == 0, f"Execution failed:\n{res_change.stdout}\n{res_change.stderr}"
    assert "Record 1 updated." in res_change.stdout
    assert "MEGAWIDGET" in res_change.stdout
    assert "35" in res_change.stdout

def test_ade_delete(tmp_path):
    """Test DELETE command removing records and shifting subsequent records."""
    cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,45,50; "
        "ADD 1003,GIZMO,15,200; "
        "DELETE 2; "
        "LIST"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Record 2 deleted. Remaining: 2." in res.stdout
    assert "1     1001   WIDGET" in res.stdout
    assert "2     1003   GIZMO" in res.stdout
    assert "GADGET" not in res.stdout

def test_ade_sort_numeric_asc_desc(tmp_path):
    """Test SORT command with numeric fields ascending and descending."""
    cmds_asc = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,45,50; "
        "ADD 1003,GIZMO,15,200; "
        "SORT PRICE ASC; "
        "LIST"
    )
    res_asc = subprocess.run([EXE_FILE, cmds_asc], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res_asc.returncode == 0, f"Ascending sort failed:\n{res_asc.stdout}\n{res_asc.stderr}"
    assert "Sorted 3 records by PRICE (ASC)." in res_asc.stdout
    # Expect order: GIZMO (15), WIDGET (25), GADGET (45)
    lines_asc = res_asc.stdout.splitlines()
    gizmo_idx = next(i for i, line in enumerate(lines_asc) if "GIZMO" in line)
    widget_idx = next(i for i, line in enumerate(lines_asc) if "WIDGET" in line)
    gadget_idx = next(i for i, line in enumerate(lines_asc) if "GADGET" in line)
    assert gizmo_idx < widget_idx < gadget_idx

    cmds_desc = "USE PRODS; SORT PRICE DESC; LIST"
    res_desc = subprocess.run([EXE_FILE, cmds_desc], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res_desc.returncode == 0, f"Descending sort failed:\n{res_desc.stdout}\n{res_desc.stderr}"
    assert "Sorted 3 records by PRICE (DESC)." in res_desc.stdout
    # Expect order: GADGET (45), WIDGET (25), GIZMO (15)
    lines_desc = res_desc.stdout.splitlines()
    gadget_idx = next(i for i, line in enumerate(lines_desc) if "GADGET" in line)
    widget_idx = next(i for i, line in enumerate(lines_desc) if "WIDGET" in line)
    gizmo_idx = next(i for i, line in enumerate(lines_desc) if "GIZMO" in line)
    assert gadget_idx < widget_idx < gizmo_idx

def test_ade_stats(tmp_path):
    """Test STATS / TOTAL calculation for numeric fields."""
    cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,45,50; "
        "ADD 1003,GIZMO,15,200; "
        "STATS PRICE"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Statistical Analysis: PRICE (Database: PRODS)" in res.stdout
    assert "Records Analyzed:   3" in res.stdout
    assert "Total / Sum:        85" in res.stdout
    assert "Average / Mean:     28.3333" in res.stdout
    assert "Minimum Value:      15" in res.stdout
    assert "Maximum Value:      45" in res.stdout

def test_ade_report(tmp_path):
    """Test REPORT command generating tabular report with column totals."""
    cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,45,50; "
        "ADD 1003,GIZMO,15,200; "
        "REPORT Product Inventory Report"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DEC ADE REPORT: Product Inventory Report" in res.stdout
    assert "Database: PRODS          Records: 3" in res.stdout
    assert "1     1001   WIDGET          25       100" in res.stdout
    assert "2     1002   GADGET          45       50" in res.stdout
    assert "3     1003   GIZMO           15       200" in res.stdout
    # Column totals line: TOTAL followed by sum of SKU, PRICE (85), QTY (350)
    assert "TOTAL" in res.stdout
    assert "85" in res.stdout
    assert "350" in res.stdout

def test_ade_graph(tmp_path):
    """Test GRAPH command rendering ASCII horizontal bar chart."""
    cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,50,50; "
        "ADD 1003,GIZMO,10,200; "
        "GRAPH NAME PRICE"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DEC ADE Bar Chart: PRODS (NAME vs PRICE)" in res.stdout
    assert "GADGET          | ************************************************** (50)" in res.stdout
    assert "WIDGET          | ************************* (25)" in res.stdout
    assert "GIZMO           | ********** (10)" in res.stdout
    assert "Scale: 1 '*' = 1 units" in res.stdout

def test_ade_export_import(tmp_path):
    """Test EXPORT to raw text file and IMPORT into a newly created table."""
    exp_file = tmp_path / "prods_export.txt"
    cmds_export = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "ADD 1002,GADGET,45,50; "
        f"EXPORT {exp_file}"
    )
    res_export = subprocess.run([EXE_FILE, cmds_export], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res_export.returncode == 0, f"Export failed:\n{res_export.stdout}\n{res_export.stderr}"
    assert exp_file.is_file()
    exp_lines = [l.strip() for l in exp_file.read_text().splitlines() if l.strip()]
    assert exp_lines == ["1001|WIDGET|25|100", "1002|GADGET|45|50"]

    cmds_import = (
        "CREATE PRODS2 (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        f"IMPORT {exp_file}; "
        "LIST"
    )
    res_import = subprocess.run([EXE_FILE, cmds_import], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res_import.returncode == 0, f"Import failed:\n{res_import.stdout}\n{res_import.stderr}"
    assert "Imported 2 records from" in res_import.stdout
    assert "Database: PRODS2 (Total Records: 2)" in res_import.stdout
    assert "1     1001   WIDGET" in res_import.stdout
    assert "2     1002   GADGET" in res_import.stdout

def test_ade_show(tmp_path):
    """Test SHOW command displaying database status and field definitions."""
    cmds = (
        "CREATE PRODS (SKU:N:6,NAME:C:15,PRICE:N:8,QTY:N:4); "
        "ADD 1001,WIDGET,25,100; "
        "SHOW"
    )
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DEC ADE Environment Status" in res.stdout
    assert "Active Database:    PRODS" in res.stdout
    assert "Schema File:        PRODS.sch" in res.stdout
    assert "Data File:          PRODS.dat" in res.stdout
    assert "Field Count:        4" in res.stdout
    assert "Record Count:       1" in res.stdout
    assert "[1] SKU (Type: N, Width: 6)" in res.stdout
    assert "[2] NAME (Type: C, Width: 15)" in res.stdout

def test_ade_command_chaining(tmp_path):
    """Test executing multiple commands chained with semicolons in CLI."""
    cmds = "SHOW; HELP; SHOW"
    res = subprocess.run([EXE_FILE, cmds], cwd=str(tmp_path), capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert res.stdout.count("DEC ADE Environment Status") == 2
    assert "ADE V3.0 - Application Development Environment" in res.stdout

def test_ade_interactive_repl():
    """Test interactive REPL prompt and clean exit on EXIT."""
    res = subprocess.run(
        [EXE_FILE],
        input="SHOW\nHELP\nEXIT\n",
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res.returncode == 0, f"Interactive REPL failed:\n{res.stdout}\n{res.stderr}"
    assert "Type HELP for commands, or EXIT to quit." in res.stdout
    assert res.stdout.count("ADE> ") >= 3
    assert "DEC ADE Environment Status" in res.stdout
    assert "Available Commands:" in res.stdout
