import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "fms11.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "fms11.obj")
EXE_FILE = os.path.join(BIN_DIR, "fms11")
FMS_LINK = os.path.join(BIN_DIR, "fms")
FED_LINK = os.path.join(BIN_DIR, "fed")
FDV_LINK = os.path.join(BIN_DIR, "fdv")


def test_fms11_build():
    """Verify that fms11.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE), f"Object file {OBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(FMS_LINK), f"Symlink {FMS_LINK} not found"
    assert os.path.islink(FED_LINK), f"Symlink {FED_LINK} not found"
    assert os.path.islink(FDV_LINK), f"Symlink {FDV_LINK} not found"


def test_fms11_banner_repl():
    """Verify interactive REPL displays FMS-11 banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "FMS-11 V2.0 - DEC Forms Management System (FED / FLB / FUT / FDV)" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / RSX-11M / VAX" in out
    assert "FMS>" in out


def test_fms11_help():
    """Verify HELP command displays FMS-11 commands."""
    res = subprocess.run([EXE_FILE, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "FMS-11 Forms Management System Commands" in res.stdout
    assert "FLB" in res.stdout
    assert "SELECT" in res.stdout
    assert "CREATE" in res.stdout
    assert "ADDFIELD" in res.stdout
    assert "FIELDS" in res.stdout
    assert "PUT" in res.stdout
    assert "VALIDATE" in res.stdout
    assert "DISPLAY" in res.stdout


def test_fms11_sample_and_show():
    """Verify SAMPLE loads DEC sample form library and SHOW displays status."""
    res = subprocess.run([EXE_FILE, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Sample FMS-11 Form Library loaded - 4 forms, 10 field definitions]" in res.stdout
    assert "FMS-11 System Status:" in res.stdout
    assert "Form Library:    FMS.FLB" in res.stdout
    assert "Terminal Driver: VT100-FDV" in res.stdout
    assert "Active Form:     #1 (ORDER_ENTRY - 5 fields)" in res.stdout
    assert "Total Forms:     4 (Deleted: 1)" in res.stdout
    assert "Total Fields:    10" in res.stdout


def test_fms11_flb_dir_and_select():
    """Verify listing forms in FLB library and selecting forms by number and name."""
    cmd = "SAMPLE; FLB; SELECT 2; SELECT RSTS_LOGON; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "FMS-11 Form Library Directory (FLB)" in res.stdout
    assert "ORDER_ENTRY" in res.stdout
    assert "EMP_RECORD" in res.stdout
    assert "[Active form set to #2: EMP_RECORD - DEC PERSONNEL MASTER MAINTENANCE (3 fields)]" in res.stdout
    assert "[Active form set to #3: RSTS_LOGON - RSTS/E V8.0 TERMINAL LOGON FORM (2 fields)]" in res.stdout


def test_fms11_create_and_addfield_fed():
    """Verify FED Form Editor CREATE and ADDFIELD commands."""
    cmd = (
        'SAMPLE; CREATE "INV_LOOKUP", "DEC INVENTORY STOCK QUERY"; '
        'ADDFIELD "SKU_CODE", "Part SKU", 5, 10, "ALPHA", "VT100-AA"; '
        'ADDFIELD "WAREHOUSE", "Depot ID", 7, 6, "NUMERIC", "12"; '
        'FIELDS; DISPLAY; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Form #5 created: INV_LOOKUP (DEC INVENTORY STOCK QUERY)]" in res.stdout
    assert "[FED: Field 'SKU_CODE' added to form INV_LOOKUP (Row=5, Len=10, Type=ALPHA)]" in res.stdout
    assert "[FED: Field 'WAREHOUSE' added to form INV_LOOKUP (Row=7, Len=6, Type=NUMERIC)]" in res.stdout
    assert "2 field(s) defined in form INV_LOOKUP" in res.stdout
    assert "[VT100-AA__]" in res.stdout


def test_fms11_fut_fields_describe():
    """Verify FUT Form Utility field attribute table listing."""
    res = subprocess.run([EXE_FILE, "SAMPLE; FUT; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "FMS-11 Form Utility (FUT) Field Attribute Table - Form: ORDER_ENTRY" in res.stdout
    assert "ORDER_NO" in res.stdout
    assert "CUST_NAME" in res.stdout
    assert "MIT Lincoln Laboratory" in res.stdout
    assert "5 field(s) defined in form ORDER_ENTRY" in res.stdout


def test_fms11_fdv_put_get_and_protected():
    """Verify FDV Form Driver PUT, GET, and PROTECTED field guard."""
    cmd = (
        'SAMPLE; PUT "CUST_NAME", "Bell Telephone Labs"; '
        'GET "CUST_NAME"; PUT "STATUS", "CANCELLED"; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[FDV: Field 'CUST_NAME' set to 'Bell Telephone Labs']" in res.stdout
    assert 'FDV Field CUST_NAME (Customer Name) = "Bell Telephone Labs" [Type: ALPHA, Len: 24]' in res.stdout
    assert "FMS-11: Field 'STATUS' is PROTECTED (display-only)" in res.stdout


def test_fms11_fdv_clearform_and_validate():
    """Verify FDV CLEARFORM and VALIDATE (pass and fail checks)."""
    cmd = (
        'SAMPLE; VALIDATE; PUT "QUANTITY", "ABC"; VALIDATE; '
        'CLEARFORM; VALIDATE; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[FDV Validation PASSED: All 5 fields in ORDER_ENTRY are valid]" in res.stdout
    assert "[ERROR] Field 'QUANTITY' requires NUMERIC digits (got 'ABC')" in res.stdout
    assert "[FDV: Cleared 4 editable field(s) in form ORDER_ENTRY]" in res.stdout
    assert "[ERROR] Field 'ORDER_NO' is required (currently empty)" in res.stdout


def test_fms11_display_and_export_file(tmp_path):
    """Verify rendering VT100 form to screen and exporting to disk file."""
    out_file = str(tmp_path / "order_form.txt")
    cmd = f"SAMPLE; DISPLAY 1; PRINT ON {out_file}; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DEC COMMERCIAL ORDER ENTRY SCREEN  [ORDER_ENTRY]" in res.stdout
    assert "[10042___]" in res.stdout
    assert "<APPROVED>" in res.stdout
    assert f"[Form ORDER_ENTRY rendered to {out_file}]" in res.stdout

    assert os.path.isfile(out_file)
    with open(out_file) as f:
        content = f.read()
    assert "DEC COMMERCIAL ORDER ENTRY SCREEN  [ORDER_ENTRY]" in content
    assert "[MIT Lincoln Laboratory__]" in content


def test_fms11_delete_and_purge():
    """Verify deleting forms and purging the form library."""
    cmd = "SAMPLE; DELETE 3; SHOW; PURGE; SHOW; DIR; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Form #3 (RSTS_LOGON) marked deleted]" in res.stdout
    assert "[Form library purged - 2 deleted form(s) removed]" in res.stdout
    assert "Total Forms:     2 (Deleted: 0)" in res.stdout


def test_fms11_save_and_load(tmp_path):
    """Verify saving and loading the FMS-11 form library."""
    flb_path = str(tmp_path / "custom.flb")
    cmd = f"SAMPLE; SAVE {flb_path}; CLEAR; SHOW; LOAD {flb_path}; DIR; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[4 form(s) saved to library {flb_path}]" in res.stdout
    assert "[FMS-11 form library cleared]" in res.stdout
    assert f"[4 form(s) loaded from library {flb_path}]" in res.stdout
    assert "ORDER_ENTRY" in res.stdout
    assert "4 form(s) in library" in res.stdout


def test_fms11_symlinks():
    """Verify fms, fed, and fdv symlinks execute properly."""
    for link in [FMS_LINK, FED_LINK, FDV_LINK]:
        res = subprocess.run([link, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
        assert res.returncode == 0
        assert "FMS-11 System Status:" in res.stdout


def test_fms11_error_handling():
    """Verify error messages for empty library, missing forms/fields, and unknown commands."""
    res1 = subprocess.run([EXE_FILE, "CLEAR; DIR; EXIT"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "FMS-11: No forms in library" in res1.stdout

    res2 = subprocess.run([EXE_FILE, "SAMPLE; SELECT NO_SUCH_FORM; EXIT"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "FMS-11: Form not found or out of range" in res2.stdout

    res3 = subprocess.run([EXE_FILE, "UNKNOWN_CMD; EXIT"], capture_output=True, text=True, timeout=10)
    assert res3.returncode == 0
    assert "FMS-11: Unknown command 'UNKNOWN_CMD'" in res3.stdout
