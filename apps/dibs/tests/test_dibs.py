import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "dibs.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
BOBJ_FILE = os.path.join(BUILD_DIR, "dibs.bobj")
EXE_FILE = os.path.join(BIN_DIR, "dibs")
DIBS11_LINK = os.path.join(BIN_DIR, "dibs11")
CTS500_LINK = os.path.join(BIN_DIR, "cts500")


def test_dibs_build():
    """Verify that dibs.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(BOBJ_FILE), f"Object file {BOBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(DIBS11_LINK), f"Symlink {DIBS11_LINK} not found"
    assert os.path.islink(CTS500_LINK), f"Symlink {CTS500_LINK} not found"


def test_dibs_banner_repl():
    """Verify interactive REPL displays DIBS-11 banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "DIBS V3.0 - DEC Integrated Business & Accounting System (DIBS-11)" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / CTS-300 / RSTS/E" in out
    assert "DIBS>" in out


def test_dibs_help():
    """Verify HELP command displays DIBS-11 commands."""
    res = subprocess.run([EXE_FILE, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DIBS-11 Integrated Business System Commands" in res.stdout
    assert "COA" in res.stdout
    assert "POST" in res.stdout
    assert "TRIAL" in res.stdout
    assert "INCOME" in res.stdout
    assert "BALANCE" in res.stdout
    assert "INVOICE" in res.stdout
    assert "VOUCHER" in res.stdout
    assert "INV" in res.stdout


def test_dibs_sample_and_show():
    """Verify SAMPLE loads DEC commercial dataset and SHOW displays system status."""
    res = subprocess.run([EXE_FILE, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Sample DIBS-11 business dataset loaded - 8 GL accounts, 3 AR, 3 AP, 3 INV]" in res.stdout
    assert "DIBS-11 System Status:" in res.stdout
    assert "GL Accounts:     8" in res.stdout
    assert "Journal Entries: 2" in res.stdout
    assert "AR Customers:    3" in res.stdout
    assert "AP Vendors:      3" in res.stdout
    assert "Inventory Items: 3" in res.stdout


def test_dibs_coa_and_addacct():
    """Verify listing Chart of Accounts and adding a new GL account."""
    cmd = 'SAMPLE; ADDACCT "5200", "DECnet Field Service", "EXP", 0; COA; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[GL Account 5200 (DECnet Field Service) added - Type: EXP, Balance: $0]" in res.stdout
    assert "1010    Cash in Bank" in res.stdout
    assert "5200    DECnet Field Service" in res.stdout
    assert "9 General Ledger accounts listed" in res.stdout


def test_dibs_post_and_jrnlist():
    """Verify double-entry journal posting and Journal Register audit trail."""
    cmd = 'SAMPLE; POST 5100, 1010, 500, "Biweekly Engineering Payroll"; JRNLIST; TRIAL; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Journal Entry #3 posted: DR 5100 / CR 1010 for $500 (Biweekly Engineering Payroll)]" in res.stdout
    assert "Biweekly Engineering Payroll" in res.stdout
    assert "3 journal entry(s) in register" in res.stdout
    assert "*** TRIAL BALANCE IS IN BALANCE (DR = CR) ***" in res.stdout


def test_dibs_trial_income_balance():
    """Verify Trial Balance, Income Statement (P&L), and Balance Sheet reconciliation."""
    cmd = "SAMPLE; TRIAL; INCOME; BALANCE; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "TOTAL DEBITS:  $26500      TOTAL CREDITS: $26500" in res.stdout
    assert "*** TRIAL BALANCE IS IN BALANCE (DR = CR) ***" in res.stdout
    assert "Total Revenue:                           $14000" in res.stdout
    assert "Total Expenses:                          $7500" in res.stdout
    assert "NET INCOME (PROFIT / LOSS):                $6500" in res.stdout
    assert "Total Assets:                            $19000" in res.stdout
    assert "Total Liabilities & Equity:              $19000" in res.stdout


def test_dibs_ar_invoice_and_receive():
    """Verify Accounts Receivable billing (INVOICE) and cash receipt (RECEIVE) with GL integration."""
    cmd = (
        'SAMPLE; INVOICE "C400", "Carnegie Mellon Univ", 1000; '
        'RECEIVE "C100", 500; AR; TRIAL; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[AR Invoice billed to C400 (Carnegie Mellon Univ) for $1000 - Posted DR 1100 / CR 4010]" in res.stdout
    assert "[AR Payment of $500 received from C100 - Posted DR 1010 / CR 1100]" in res.stdout
    assert "Total Accounts Receivable (4 customers): $5000" in res.stdout
    assert "*** TRIAL BALANCE IS IN BALANCE (DR = CR) ***" in res.stdout


def test_dibs_ap_voucher_and_pay():
    """Verify Accounts Payable voucher entry (VOUCHER) and check disbursement (PAY) with GL integration."""
    cmd = (
        'SAMPLE; VOUCHER "V400", "Fairchild Semiconductor", 600; '
        'PAY "V100", 400; AP; TRIAL; EXIT'
    )
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[AP Voucher recorded for V400 (Fairchild Semiconductor) for $600 - Posted DR 5010 / CR 2010]" in res.stdout
    assert "[AP Check of $400 paid to V100 - Posted DR 2010 / CR 1010]" in res.stdout
    assert "Total Accounts Payable (4 vendors): $3200" in res.stdout
    assert "*** TRIAL BALANCE IS IN BALANCE (DR = CR) ***" in res.stdout


def test_dibs_inventory_and_additem():
    """Verify Inventory Control listing, item addition, and valuation."""
    cmd = 'SAMPLE; ADDITEM "LA120", "DECwriter III Terminal", 5, 200; INV; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Inventory Item LA120 (DECwriter III Terminal) added: Qty=5, Cost=$200]" in res.stdout
    assert "PDP1170    PDP-11/70 CPU System" in res.stdout
    assert "LA120      DECwriter III Terminal" in res.stdout
    assert "Total Inventory Valuation (4 items): $7000" in res.stdout


def test_dibs_report_export(tmp_path):
    """Verify exporting executive financial report to disk file."""
    rpt_file = str(tmp_path / "dibs_report.txt")
    cmd = f"SAMPLE; REPORT ON {rpt_file}; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[DIBS-11 Financial Report exported to {rpt_file}]" in res.stdout
    assert os.path.isfile(rpt_file)
    with open(rpt_file) as f:
        content = f.read()
    assert "DIBS-11 EXECUTIVE FINANCIAL REPORT" in content
    assert "Total Revenue: $14000   Total Expenses: $7500   Net Income: $6500" in content


def test_dibs_save_and_load(tmp_path):
    """Verify saving and loading the General Ledger chart of accounts."""
    gl_file = str(tmp_path / "dibs_gl.dat")
    cmd = f"SAMPLE; SAVE {gl_file}; CLEAR; SHOW; LOAD {gl_file}; COA; TRIAL; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[8 GL accounts saved to {gl_file}]" in res.stdout
    assert "[All DIBS-11 ledgers and subledgers cleared]" in res.stdout
    assert f"[8 GL accounts loaded from {gl_file}]" in res.stdout
    assert "*** TRIAL BALANCE IS IN BALANCE (DR = CR) ***" in res.stdout


def test_dibs_symlinks():
    """Verify dibs11 and cts500 symlinks execute properly."""
    res1 = subprocess.run([DIBS11_LINK, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "GL Accounts:     8" in res1.stdout

    res2 = subprocess.run([CTS500_LINK, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "DIBS-11 Integrated Business System Commands" in res2.stdout


def test_dibs_error_handling():
    """Verify error messages for empty ledgers, invalid accounts, and unknown commands."""
    res1 = subprocess.run([EXE_FILE, "CLEAR; TRIAL; EXIT"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "DIBS: No accounting data loaded" in res1.stdout

    res2 = subprocess.run([EXE_FILE, "SAMPLE; POST 9999, 1010, 100; EXIT"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "DIBS: Invalid GL account number in POST" in res2.stdout

    res3 = subprocess.run([EXE_FILE, "UNKNOWN_CMD; EXIT"], capture_output=True, text=True, timeout=10)
    assert res3.returncode == 0
    assert "DIBS: Unknown command 'UNKNOWN_CMD'" in res3.stdout
