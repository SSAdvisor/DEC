import os
import subprocess
import pytest

RSTS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RSTS_EMU = os.path.join(RSTS_ROOT, "bin", "rsts-emu")


def run_rsts(cmd_or_args, stdin_text=None, tmp_root=None):
    args = [RSTS_EMU]
    if tmp_root:
        args.extend(["--root", str(tmp_root)])
    if isinstance(cmd_or_args, str):
        args.extend(["-c", cmd_or_args])
    else:
        args.extend(cmd_or_args)
    res = subprocess.run(
        args,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return res


def run_rsts_docker(cmd_or_args, stdin_text=None):
    args = ["docker", "run", "--rm", "-i", "dec-rsts-e:latest"]
    if isinstance(cmd_or_args, str):
        args.extend(["-c", cmd_or_args])
    else:
        args.extend(cmd_or_args)
    res = subprocess.run(
        args,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return res


class TestRSTSEmulationHost:
    def test_01_boot_and_show_system(self, tmp_path):
        res = run_rsts(["--boot", "-c", "SHOW SYSTEM"], tmp_root=tmp_path)
        assert res.returncode == 0
        assert "INIT V10.1-0L  RSTS/E V10.1-L" in res.stdout
        assert "RSTS V10.1-L (PDP11)" in res.stdout
        assert "SYSTEM [1,2]" in res.stdout

    def test_02_interactive_ppn_login(self, tmp_path):
        stdin_data = "1,2\nSYSTEM\nSHOW SYSTEM\nHELLO 200,200\nSHOW DEFAULT\nBYE\n"
        res = run_rsts(["--login"], stdin_text=stdin_data, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "User: " in res.stdout
        assert "Job 1  User SYSTEM [1,2] on KB0:" in res.stdout
        assert "Switched session to User GUEST [200,200]" in res.stdout
        assert "logged off KB0:" in res.stdout

    def test_03_systat_devices_memory_users_accounts(self, tmp_path):
        res = run_rsts(
            "SYSTAT; SHOW DEVICES; SHOW MEMORY; SHOW USERS; SHOW ACCOUNTS; SHOW CCL",
            tmp_root=tmp_path,
        )
        assert res.returncode == 0
        assert "DK0:" in res.stdout
        assert "RA81" in res.stdout
        assert "PDP-11/70 Physical Memory Allocation" in res.stdout
        assert "[1,1]" in res.stdout
        assert "[1,2]" in res.stdout
        assert "DIBS" in res.stdout
        assert "DATATRIEVE11" in res.stdout

    def test_04_filesystem_ppn_pip_fit_utility(self, tmp_path):
        cmds = (
            "DIR SY:; "
            "TYPE SY:WELCOME.TXT; "
            "COPY SY:WELCOME.TXT SY:NOTE.TXT; "
            "RENAME SY:NOTE.TXT SY:MEMO.TXT; "
            "PIP SY:MEMO2.TXT=SY:MEMO.TXT; "
            "FIT SY:; "
            "DELETE SY:MEMO.TXT; "
            "DELETE SY:MEMO2.TXT; "
            "UTILITY CREATE 150,10 ENGR; "
            "SHOW ACCOUNTS"
        )
        res = run_rsts(cmds, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "Welcome to DEC RSTS/E V10.1-L" in res.stdout
        assert "%DCL-I-COPIED" in res.stdout
        assert "%DCL-I-RENAMED" in res.stdout
        assert "%DCL-I-DELETED" in res.stdout
        assert "[150,10]" in res.stdout
        assert "ENGR" in res.stdout

    def test_05_logicals_symbols_and_procedures(self, tmp_path):
        cmds = (
            "MYVAR = \"RSTS_OK\"; "
            "WRITE SYS$OUTPUT \"VAL='MYVAR'\"; "
            "ASSIGN DK0:[1,2] WORK:; "
            "SHOW LOGICALS; "
            "DEASSIGN WORK:; "
            "@SY:LOGIN.COM"
        )
        res = run_rsts(cmds, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "VAL=RSTS_OK" in res.stdout
        assert '"WORK:"' in res.stdout
        assert "RSTS/E V10.1-L System Manager [1,2] Session Initialized" in res.stdout

    def test_06_keyboard_monitors_basic_and_rsx(self, tmp_path):
        stdin_data = (
            "SWITCH BASIC\n"
            "NEW TESTP\n"
            "10 PRINT \"BASIC MONITOR COMPUTE:\"; 20% + 22%\n"
            "20 END\n"
            "LIST\n"
            "SAVE SY:TESTP.BAS\n"
            "RUN\n"
            "SWITCH RSX\n"
            "PIP SY:\n"
            "SWITCH DCL\n"
            "BYE\n"
        )
        res = run_rsts([], stdin_text=stdin_data, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "Switched to RSTS/E BASIC Keyboard Monitor" in res.stdout
        assert "BASIC MONITOR COMPUTE:42" in res.stdout
        assert "Switched to RSTS/E RSX Keyboard Monitor" in res.stdout
        assert "Switched to RSTS/E DCL Keyboard Monitor" in res.stdout

    def test_07_basic_plus_2_compile_link_run_and_edt_and_pbs(self, tmp_path):
        res = run_rsts(
            "BASIC SY:HELLO.BAS; DIR; LINK SY:HELLO.OBJ; RUN SY:HELLO.TSK; DELETE SY:HELLO.OBJ; PRINT SY:WELCOME.TXT; SHOW QUEUE /ALL",
            tmp_root=tmp_path,
        )
        assert res.returncode == 0
        assert "HELLO .OBJ" in res.stdout
        assert "HELLO FROM DEC RSTS/E V10.1-L ON PDP-11!" in res.stdout
        assert "HELLO.OBJ deleted" in res.stdout
        assert "SYS$PRINT" in res.stdout

        # Test EDT editor inside RSTS/E
        edt_res = run_rsts("EDT", stdin_text="WELCOME.TXT\nTYPE 1:3\nQUIT\n", tmp_root=tmp_path)
        assert edt_res.returncode == 0
        assert "Welcome to DEC RSTS/E V10.1-L" in edt_res.stdout

    def test_08_ccl_supported_applications(self, tmp_path):
        # Verify all 12 RSTS/E-supported DEC-APPS run cleanly under RSTS/E CCL
        app_tests = [
            ("HAMURABI", "0\n0\n0\n0\n", "HAMURABI"),
            ("SORT11", "EXIT\n", "SORT-11"),
            ("RMSUTILS", "HELP\nEXIT\n", "RMS"),
            ("ADE", "SAMPLE\nLIST\nEXIT\n", "ADE"),
            ("DATATRIEVE11", "READY YACHTS\nPRINT FIRST 2\nEXIT\n", "ALBERG"),
            ("DECGRAPH", "SAMPLE\nPLOT\nEXIT\n", "DECGRAPH"),
            ("DECMAIL", "SAMPLE\nDIR\nEXIT\n", "DECMAIL"),
            ("DECWORD", "SAMPLE\nDIR\nEXIT\n", "DECWORD"),
            ("DIBS", "SAMPLE\nTRIAL\nEXIT\n", "DIBS"),
            ("FMS11", "SAMPLE\nDIR\nEXIT\n", "FMS-11"),
            ("MENU11", "SAMPLE\nDIR\nEXIT\n", "MENU-11"),
            ("INDENT", "SAMPLE\nCHECK\nEXIT\n", "INDENT"),
        ]
        for ccl_verb, app_stdin, expected_marker in app_tests:
            res = run_rsts(ccl_verb, stdin_text=app_stdin, tmp_root=tmp_path)
            assert res.returncode == 0, f"{ccl_verb} failed with {res.stdout} {res.stderr}"
            assert expected_marker.upper() in res.stdout.upper(), f"Missing {expected_marker} in {ccl_verb}"

    def test_09_rejects_unsupported_vms_decwindows(self, tmp_path):
        for vms_only in ("DECWINDOWS", "DXSESSION", "DECTERM", "BOOKREADER", "CLOCK", "RUN LB:DECWINDOWS"):
            res = run_rsts(vms_only, tmp_root=tmp_path)
            assert res.returncode != 0
            assert "Unsupported OS facility" in res.stdout
            assert "DECwindows requires 32-bit VAX/VMS" in res.stdout

    def test_09b_dcl_account_management_and_persistence(self, tmp_path):
        # Create an account, verify persistence across invocations, modify, set password, and delete
        r1 = run_rsts(
            "CREATE/ACCOUNT [150,25] /NAME=PAYROLL /PASSWORD=SECRET1 /QUOTA=15000 /PRIVILEGES; SHOW ACCOUNT [150,25] /FULL",
            tmp_root=tmp_path,
        )
        assert r1.returncode == 0
        assert "%ACC-S-CREATED" in r1.stdout
        assert "PAYROLL" in r1.stdout
        assert "15000 blocks" in r1.stdout

        # Second invocation verifies persistence in DK0:[1,1]ACCT.JSON & login switching via HELLO
        r2 = run_rsts(
            "HELLO [150,25]; SHOW SYSTEM; MODIFY/ACCOUNT [150,25] /QUOTA=20000 /NOPRIVILEGES; SET PASSWORD [150,25] /PASSWORD=NEWPASS2; SHOW ACCOUNT [150,25] /FULL",
            tmp_root=tmp_path,
        )
        assert r2.returncode == 0
        assert "Switched session to User PAYROLL [150,25]" in r2.stdout
        assert "%ACC-S-MODIFIED" in r2.stdout
        assert "%SET-S-PASSCHG" in r2.stdout
        assert "20000 blocks" in r2.stdout

        # Delete non-system account and verify system account [1,2] is protected
        r3 = run_rsts("DELETE/ACCOUNT [150,25]", tmp_root=tmp_path)
        assert r3.returncode == 0
        assert "%ACC-S-DELETED" in r3.stdout

        r3_show = run_rsts("SHOW ACCOUNTS", tmp_root=tmp_path)
        assert "PAYROLL" not in r3_show.stdout

        r4 = run_rsts("DELETE/ACCOUNT [1,2]", tmp_root=tmp_path)
        assert r4.returncode != 0
        assert "cannot delete protected system account" in r4.stdout


class TestRSTSDockerContainer:
    def test_10_docker_image_and_system_commands(self):
        res = run_rsts_docker("SHOW SYSTEM; SYSTAT; SHOW DEVICES; SHOW CCL")
        assert res.returncode == 0
        assert "RSTS V10.1-L (PDP11)" in res.stdout
        assert "DK0:" in res.stdout
        assert "DIBS" in res.stdout

    def test_11_docker_compile_link_and_run_basic_plus_2(self):
        res = run_rsts_docker("BASIC SY:HELLO.BAS; DIR; LINK SY:HELLO.OBJ; RUN SY:HELLO; DELETE SY:HELLO.OBJ")
        assert res.returncode == 0
        assert "HELLO .OBJ" in res.stdout
        assert "HELLO FROM DEC RSTS/E V10.1-L ON PDP-11!" in res.stdout

    def test_12_docker_execute_rsts_applications_and_reject_decwindows(self):
        res_dibs = run_rsts_docker("DIBS", stdin_text="SAMPLE\nTRIAL\nEXIT\n")
        assert res_dibs.returncode == 0
        assert "TRIAL BALANCE" in res_dibs.stdout.upper()

        res_dtr = run_rsts_docker("DTR", stdin_text="READY YACHTS\nPRINT FIRST 2\nEXIT\n")
        assert res_dtr.returncode == 0
        assert "ALBERG" in res_dtr.stdout.upper()

        res_unsup = run_rsts_docker("DECWINDOWS")
        assert res_unsup.returncode != 0
        assert "Unsupported OS facility" in res_unsup.stdout
