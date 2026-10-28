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
        # Verify default interactive mode prompts for User: login, BYE returns to User: prompt
        # without terminating the OS, and privileged SHUTDOWN halts the system.
        stdin_data = (
            "1,2\n"
            "SYSTEM\n"
            "SHOW SYSTEM\n"
            "BYE\n"
            "200,200\n"
            "SHOW DEFAULT\n"
            "SHUTDOWN\n"
            "BYE\n"
            "1,2\n"
            "SYSTEM\n"
            "SHUTDOWN\n"
        )
        res = run_rsts([], stdin_text=stdin_data, tmp_root=tmp_path)
        assert res.returncode == 0
        assert res.stdout.count("User: ") >= 3
        assert "Job 1  User SYSTEM [1,2] on KB0:" in res.stdout
        assert "User SYSTEM [1,2] logged off KB0:" in res.stdout
        assert "Job 1  User GUEST [200,200] on KB0:" in res.stdout
        assert "?Protection violation - SHUTDOWN requires privileged account" in res.stdout
        assert "SHUTUP V10.1-L  RSTS/E System Shutdown" in res.stdout
        assert "System halted at" in res.stdout

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
            "1,2\n"
            "SYSTEM\n"
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
            ("WORD11", "SAMPLE\nDIR\nEXIT\n", "WORD-11"),
            ("LEX11", "SAMPLE\nDIR\nEXIT\n", "LEX-11"),
            ("SATURNWP", "SAMPLE\nDIR\nEXIT\n", "SATURN-WP"),
            ("CALC2020", "SAMPLE\nGRID\nEXIT\n", "20/20"),
            ("SATURNCALC", "SAMPLE\nGRID\nEXIT\n", "SATURN-CALC"),
            ("NYPLAN", "SAMPLE\nMODEL\nEXIT\n", "NYPLAN"),
            ("TOTAL", "SAMPLE\nSCHEMA\nEXIT\n", "CINCOM TOTAL"),
            ("AMBASE", "SAMPLE\nSCHEMA\nEXIT\n", "AMBASE"),
            ("ACCENTR", "SAMPLE\nDSD\nEXIT\n", "ACCENT R"),
            ("SATURNBASE", "SAMPLE\nSCHEMA\nEXIT\n", "SATURN-BASE"),
            ("MCBA", "SAMPLE\nLIST\nEXIT\n", "MCBA"),
            ("MAPS", "SAMPLE\nLIST\nEXIT\n", "MAPS/GL"),
            ("TIMELINE", "SAMPLE\nLIST\nEXIT\n", "DIGI-GL"),
            ("COMPUSHARE", "SAMPLE\nLIST\nEXIT\n", "COMPU-SHARE"),
            ("CJBUSINESS", "SAMPLE\nLIST\nEXIT\n", "CJ/GL"),
            ("KDSS", "SAMPLE\nBATCH\nEXIT\n", "KDSS"),
            ("TAM", "SAMPLE\nLIST\nEXIT\n", "TAM"),
            ("FSORT3", "SAMPLE\nSORT ASC\nEXIT\n", "FSORT3"),
            ("CLYDE", "SAMPLE\nAUDIT\nEXIT\n", "CAUDIT"),
            ("MINITAB", "SAMPLE\nDESCRIBE\nSTOP\n", "MINITAB-11"),
            ("SPSS11", "SAMPLE\nFREQUENCIES\nFINISH\n", "SPSS-11"),
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

    def test_09c_rsts_e_six_language_compilers_and_apl_workspace(self, tmp_path):
        # Compile, link, and execute MACRO-11, COBOL-81, FORTRAN-77, DIBOL-83, RPG II, and APL-11
        res = run_rsts(
            "MACRO SY:HELLO.MAC; LINK SY:HELLO.OBJ; RUN SY:HELLO.TSK; "
            "COBOL SY:PAYROL.CBL; LINK SY:PAYROL.OBJ; RUN SY:PAYROL.TSK; "
            "FORTRAN SY:STATS.FOR; LINK SY:STATS.OBJ; RUN SY:STATS.TSK; "
            "DIBOL SY:INVOIC.DBL; LINK SY:INVOIC.OBJ; RUN SY:INVOIC.TSK; "
            "RPG SY:SLSRPT.RPG; LINK SY:SLSRPT.OBJ; RUN SY:SLSRPT.TSK; "
            "APL SY:VECTOR.APL; LINK SY:VECTOR.OBJ; RUN SY:VECTOR.TSK",
            tmp_root=tmp_path,
        )
        assert res.returncode == 0
        assert "HELLO FROM DEC MACRO-11 V05.05 ON RSTS-E!" in res.stdout
        assert "COBOL-81 PAYROLL: J. DEC ENGINEER GROSS=1200" in res.stdout
        assert "FORTRAN-77 SUM(1..10)=55" in res.stdout
        assert "DIBOL-83 CUSTOMER: DIGITAL EQUIPMENT CORP TOTAL=1800" in res.stdout
        assert "DEC RPG II V2.1 SALES REPORT" in res.stdout
        assert "RPG II TOTAL SALES=3000" in res.stdout
        assert "DEC APL-11 V2.1 VECTOR ENGINE" in res.stdout
        assert "120" in res.stdout

        # Test interactive APL-11 workspace via `APL` command
        apl_res = run_rsts(
            "APL",
            stdin_text="X <- .IOTA 6\n+/ X\n)VARS\n)OFF\n",
            tmp_root=tmp_path,
        )
        assert apl_res.returncode == 0
        assert "CLEAR WS" in apl_res.stdout
        assert "21" in apl_res.stdout
        assert "X" in apl_res.stdout


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

    def test_11b_docker_six_rsts_e_language_compilers(self):
        res = run_rsts_docker(
            "MACRO SY:HELLO.MAC; LINK SY:HELLO.OBJ; RUN SY:HELLO.TSK; "
            "COBOL SY:PAYROL.CBL; LINK SY:PAYROL.OBJ; RUN SY:PAYROL.TSK; "
            "FORTRAN SY:STATS.FOR; LINK SY:STATS.OBJ; RUN SY:STATS.TSK; "
            "DIBOL SY:INVOIC.DBL; LINK SY:INVOIC.OBJ; RUN SY:INVOIC.TSK; "
            "RPG SY:SLSRPT.RPG; LINK SY:SLSRPT.OBJ; RUN SY:SLSRPT.TSK; "
            "APL SY:VECTOR.APL; LINK SY:VECTOR.OBJ; RUN SY:VECTOR.TSK"
        )
        assert res.returncode == 0
        assert "HELLO FROM DEC MACRO-11 V05.05 ON RSTS-E!" in res.stdout
        assert "COBOL-81 PAYROLL: J. DEC ENGINEER GROSS=1200" in res.stdout
        assert "FORTRAN-77 SUM(1..10)=55" in res.stdout
        assert "DIBOL-83 CUSTOMER: DIGITAL EQUIPMENT CORP TOTAL=1800" in res.stdout
        assert "RPG II TOTAL SALES=3000" in res.stdout
        assert "DEC APL-11 V2.1 VECTOR ENGINE" in res.stdout

    def test_12_docker_execute_rsts_applications_and_reject_decwindows(self):
        res_dibs = run_rsts_docker("DIBS", stdin_text="SAMPLE\nTRIAL\nEXIT\n")
        assert res_dibs.returncode == 0
        assert "TRIAL BALANCE" in res_dibs.stdout.upper()

        res_dtr = run_rsts_docker("DTR", stdin_text="READY YACHTS\nPRINT FIRST 2\nEXIT\n")
        assert res_dtr.returncode == 0
        assert "ALBERG" in res_dtr.stdout.upper()

        for oa_cmd, oa_marker in (
            ("WORD11", "WORD-11"),
            ("LEX11", "LEX-11"),
            ("SATURNWP", "SATURN-WP"),
            ("2020", "20/20"),
            ("SATCALC", "SATURN-CALC"),
            ("NYPLAN", "NYPLAN"),
            ("TOTAL", "CINCOM TOTAL"),
            ("MCBA", "MCBA"),
            ("FSORT3", "FSORT3"),
            ("MINITAB", "MINITAB-11"),
            ("SPSS11", "SPSS-11"),
        ):
            res_oa = run_rsts_docker(oa_cmd, stdin_text="SAMPLE\nGRID\nDIR\nMODEL\nLIST\nDESCRIBE\nFREQUENCIES\nEXIT\nSTOP\nFINISH\n")
            assert res_oa.returncode == 0
            assert oa_marker in res_oa.stdout.upper()

        res_unsup = run_rsts_docker("DECWINDOWS")
        assert res_unsup.returncode != 0
        assert "Unsupported OS facility" in res_unsup.stdout

    def test_13_multiuser_concurrent_sessions_and_network(self, tmp_path):
        # Launch Session 1 (holding KB0: / Job 1) and run Session 2 concurrently (KB1: / Job 2)
        p1 = subprocess.Popen(
            [RSTS_EMU, "--root", str(tmp_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            p1.stdin.write("1,2\nSYSTEM\nSHOW SYSTEM\n")
            p1.stdin.flush()
            import time
            time.sleep(0.4)

            r2 = run_rsts(
                [],
                stdin_text="100,100\nDIBS\nSYSTAT\nSHOW USERS\nSHOW DEVICES\nSHOW NETWORK\nBYE/DISCONNECT\n",
                tmp_root=tmp_path,
            )
            assert r2.returncode == 0
            assert "Job 2  User DIBS [100,100] on KB1:" in r2.stdout
            assert "[1,2]" in r2.stdout and "KB0:" in r2.stdout
            assert "[100,100]" in r2.stdout and "KB1:" in r2.stdout
            assert "SSH Lines:" in r2.stdout and "HTTPS Lines:" in r2.stdout
        finally:
            p1.stdin.write("SHUTDOWN\n")
            p1.stdin.flush()
            p1.communicate(timeout=5)

    def test_14_subscriber_provisioning_username_login_and_disuser(self, tmp_path):
        import sys
        sys.path.insert(0, os.path.join(RSTS_ROOT, "src"))
        import rsts_os

        emu = rsts_os.RSTSEmulator(root_dir=str(tmp_path))
        ok, _ = emu.check_username_available("JSMITH")
        assert ok

        rec = emu.provision_subscriber_account(
            username="JSMITH",
            password="PDP11$OK",
            email="jsmith@example.com",
            plan="LCS_RSTS_10",
            clerk_user_id="user_clerk_101",
        )
        assert rec["ok"] is True
        assert rec["ppn"] == "[201,1]"
        assert rec["quota"] == 25000
        assert os.path.isfile(os.path.join(rec["dir_path"], "LOGIN.COM"))
        assert os.path.isfile(os.path.join(rec["dir_path"], "WELCOME.TXT"))
        assert os.path.isfile(os.path.join(rec["dir_path"], "HELLO.BAS"))

        ok_after, _ = emu.check_username_available("JSMITH")
        assert not ok_after

        # Verify interactive login by Username (JSMITH) and by PPN (201,1)
        login_res = run_rsts(
            [],
            stdin_text=(
                "JSMITH\n"
                "PDP11$OK\n"
                "@SY:LOGIN.COM\n"
                "RUN SY:HELLO.BAS\n"
                "BYE\n"
                "201,1\n"
                "PDP11$OK\n"
                "SHOW SYSTEM\n"
                "BYE/DISCONNECT\n"
            ),
            tmp_root=tmp_path,
        )
        assert login_res.returncode == 0
        assert "User JSMITH [201,1] on KB0:" in login_res.stdout
        assert "Welcome JSMITH ([201,1]) to Legacy Computing Systems PDP-11/70 RSTS/E" in login_res.stdout
        assert "HELLO JSMITH FROM LEGACY COMPUTING SYSTEMS PDP-11/70 RSTS/E!" in login_res.stdout

        # Suspend account (DISUSER) and verify login is blocked
        upd = emu.update_subscriber_account("user_clerk_101", status="DISUSER")
        assert upd["flags"] == "DISUSER"

        dis_res = run_rsts(
            [],
            stdin_text="JSMITH\n200,200\nBYE/DISCONNECT\n",
            tmp_root=tmp_path,
        )
        assert "?Account is disabled (DISUSER)" in dis_res.stdout

        # Reactivate account and verify login succeeds again
        upd_act = emu.update_subscriber_account("JSMITH", status="ACTIVE")
        assert upd_act["flags"] == "NODISUSER"

    def test_15_https_signup_portal_clerk_workos_webhooks_and_wss_login(self, tmp_path):
        import json
        import socket
        import ssl
        import time
        import urllib.request
        import base64

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]

        env = os.environ.copy()
        env["RSTS_FS_ROOT"] = str(tmp_path)
        srv_script = os.path.join(RSTS_ROOT, "src", "multiuser_service.py")
        proc = subprocess.Popen(
            [
                "python3",
                srv_script,
                "--serve-https",
                "--emu",
                RSTS_EMU,
                "--port",
                str(port),
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ssl_ctx = ssl._create_unverified_context()
        base_url = f"https://127.0.0.1:{port}"

        try:
            # Wait for HTTPS server to come up
            for _ in range(30):
                try:
                    with urllib.request.urlopen(f"{base_url}/api/v1/status", context=ssl_ctx, timeout=2) as r:
                        if r.status == 200:
                            break
                except Exception:
                    time.sleep(0.15)

            # 1. GET /signup portal
            with urllib.request.urlopen(f"{base_url}/signup", context=ssl_ctx, timeout=5) as r:
                html = r.read().decode("utf-8")
                assert r.status == 200
                assert "LEGACY COMPUTING SYSTEMS" in html
                assert "$10 / month" in html
                assert "WorkOS Enterprise" in html

            # 2. Check username availability
            with urllib.request.urlopen(f"{base_url}/api/v1/users/check?username=BELL11", context=ssl_ctx, timeout=5) as r:
                chk = json.loads(r.read().decode("utf-8"))
                assert chk["available"] is True

            # 2b. Create & validate 6-character alphanumeric + special char percentage discount coupons (100ths precision, never/days/months <= 1 yr)
            import urllib.error
            import urllib.parse
            def _is_alnum_special_6(code_str):
                return (
                    len(code_str) == 6
                    and any(c.isalpha() for c in code_str)
                    and any(c.isdigit() for c in code_str)
                    and any(not c.isalnum() for c in code_str)
                )

            cpn_never_req = urllib.request.Request(
                f"{base_url}/api/v1/coupons",
                data=json.dumps({"discount_percent": 33.33, "duration_unit": "never"}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(cpn_never_req, context=ssl_ctx, timeout=5) as r:
                assert r.status == 201
                cpn_never = json.loads(r.read().decode("utf-8"))["coupon"]
                assert _is_alnum_special_6(cpn_never["code"])
                assert cpn_never["discount_percent"] == 33.33
                assert cpn_never["never_expires"] is True
                assert cpn_never["expires_at"] is None
                coupon_code_6 = cpn_never["code"]

            cpn_days_req = urllib.request.Request(
                f"{base_url}/api/v1/coupons",
                data=json.dumps({"discount_percent": 12.75, "duration_unit": "days", "duration_value": 90}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(cpn_days_req, context=ssl_ctx, timeout=5) as r:
                cpn_days = json.loads(r.read().decode("utf-8"))["coupon"]
                assert _is_alnum_special_6(cpn_days["code"])
                assert cpn_days["discount_percent"] == 12.75
                assert cpn_days["duration_unit"] == "days" and cpn_days["duration_value"] == 90

            cpn_months_req = urllib.request.Request(
                f"{base_url}/api/v1/coupons",
                data=json.dumps({"discount_percent": 100.00, "duration_unit": "months", "duration_value": 12}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(cpn_months_req, context=ssl_ctx, timeout=5) as r:
                cpn_months = json.loads(r.read().decode("utf-8"))["coupon"]
                assert _is_alnum_special_6(cpn_months["code"])
                assert cpn_months["discount_percent"] == 100.0
                assert cpn_months["duration_unit"] == "months" and cpn_months["duration_value"] == 12

            # Reject > 1 year (366 days, 13 months) and > 100ths fractional place (12.345%)
            for bad_payload in (
                {"discount_percent": 25.0, "duration_unit": "days", "duration_value": 366},
                {"discount_percent": 25.0, "duration_unit": "months", "duration_value": 13},
                {"discount_percent": 12.345, "duration_unit": "never"},
            ):
                bad_req = urllib.request.Request(
                    f"{base_url}/api/v1/coupons",
                    data=json.dumps(bad_payload).encode("utf-8"),
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with pytest.raises(urllib.error.HTTPError) as exc_info:
                    urllib.request.urlopen(bad_req, context=ssl_ctx, timeout=5)
                assert exc_info.value.code == 400

            with urllib.request.urlopen(
                f"{base_url}/api/v1/coupons/validate?code={urllib.parse.quote(coupon_code_6, safe='')}&plan=LCS_RSTS_10",
                context=ssl_ctx,
                timeout=5,
            ) as r:
                val_res = json.loads(r.read().decode("utf-8"))
                assert val_res["ok"] is True
                assert val_res["valid"] is True
                assert val_res["discount_amount_usd"] == 3.33
                assert val_res["discounted_price_usd"] == 6.67

            # 3. POST /api/v1/signup ($10/mo RSTS/E subscriber with 33.33% 6-digit coupon)
            signup_payload = json.dumps({
                "username": "BELL11",
                "password": "DEC$1970",
                "email": "bell@dec.example.com",
                "plan": "LCS_RSTS_10",
                "clerk_user_id": "user_clerk_bell11",
                "coupon_code": coupon_code_6,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{base_url}/api/v1/signup",
                data=signup_payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=5) as r:
                assert r.status == 201
                created = json.loads(r.read().decode("utf-8"))
                assert created["ok"] is True
                assert created["ppn"] == "[201,1]"
                assert created["clerk_metadata"]["dec_username"] == "BELL11"
                assert created["coupon_applied"]["code"] == coupon_code_6
                assert created["discounted_price_usd"] == 6.67

            # 4. Clerk webhook: subscription.canceled -> DISUSER, then invoice.paid -> ACTIVE
            clerk_cancel = json.dumps({
                "type": "subscription.canceled",
                "data": {"id": "user_clerk_bell11", "public_metadata": {"dec_username": "BELL11"}},
            }).encode("utf-8")
            req_cc = urllib.request.Request(
                f"{base_url}/api/v1/webhooks/clerk",
                data=clerk_cancel,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req_cc, context=ssl_ctx, timeout=5) as r:
                cc_res = json.loads(r.read().decode("utf-8"))
                assert cc_res["action"] == "SUSPENDED"
                assert cc_res["account"]["status"] == "DISUSER"

            clerk_paid = json.dumps({
                "type": "invoice.paid",
                "data": {"id": "user_clerk_bell11", "status": "active", "public_metadata": {"dec_username": "BELL11"}},
            }).encode("utf-8")
            req_cp = urllib.request.Request(
                f"{base_url}/api/v1/webhooks/clerk",
                data=clerk_paid,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req_cp, context=ssl_ctx, timeout=5) as r:
                cp_res = json.loads(r.read().decode("utf-8"))
                assert cp_res["action"] == "REACTIVATED"
                assert cp_res["account"]["status"] == "ACTIVE"

            # 5. WorkOS SCIM webhook: dsync.user.created -> [300,1], dsync.user.deleted -> DISUSER
            wos_create = json.dumps({
                "event": "dsync.user.created",
                "data": {
                    "id": "dir_usr_01",
                    "organization_id": "org_mit_cs",
                    "username": "MITPROF",
                    "emails": [{"value": "prof@mit.edu"}],
                    "state": "active",
                },
            }).encode("utf-8")
            req_wc = urllib.request.Request(
                f"{base_url}/api/v1/webhooks/workos",
                data=wos_create,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req_wc, context=ssl_ctx, timeout=5) as r:
                wc_res = json.loads(r.read().decode("utf-8"))
                assert wc_res["action"] == "PROVISIONED"
                assert wc_res["account"]["ppn"] == "[300,1]"
                assert wc_res["account"]["quota"] == 100000
                assert wc_res["enterprise_billing"]["base_price_monthly"] == 199
                assert wc_res["enterprise_billing"]["included_active_seats"] == 15
                assert wc_res["enterprise_billing"]["additional_seat_price_monthly"] == 10
                assert wc_res["enterprise_billing"]["active_seats"] == 1
                assert wc_res["enterprise_billing"]["monthly_total_usd"] == 199

            # Verify GET /api/v1/enterprise/seats?org=org_mit_cs reports 1 active seat @ $199/mo
            with urllib.request.urlopen(f"{base_url}/api/v1/enterprise/seats?org=org_mit_cs", context=ssl_ctx, timeout=5) as r:
                sm = json.loads(r.read().decode("utf-8"))["seat_metering"]
                assert sm["active_seats"] == 1
                assert sm["remaining_included_seats"] == 14
                assert sm["monthly_total_usd"] == 199

            wos_del = json.dumps({
                "event": "dsync.user.deleted",
                "data": {"id": "dir_usr_01", "organization_id": "org_mit_cs", "username": "MITPROF"},
            }).encode("utf-8")
            req_wd = urllib.request.Request(
                f"{base_url}/api/v1/webhooks/workos",
                data=wos_del,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req_wd, context=ssl_ctx, timeout=5) as r:
                wd_res = json.loads(r.read().decode("utf-8"))
                assert wd_res["action"] == "SUSPENDED"
                assert wd_res["account"]["status"] == "DISUSER"
                assert wd_res["enterprise_billing"]["active_seats"] == 0
                assert wd_res["enterprise_billing"]["suspended_seats"] == 1

            # 6. Connect via live WSS (/ws) and log in with newly provisioned BELL11 account
            raw_sock = socket.create_connection(("127.0.0.1", port), timeout=5)
            tls_sock = ssl_ctx.wrap_socket(raw_sock, server_hostname="127.0.0.1")
            ws_key = base64.b64encode(os.urandom(16)).decode("ascii")
            handshake = (
                f"GET /ws HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{port}\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {ws_key}\r\n"
                "Sec-WebSocket-Version: 13\r\n\r\n"
            )
            tls_sock.sendall(handshake.encode("ascii"))
            resp_hdr = tls_sock.recv(1024).decode("latin-1", errors="replace")
            assert "101 Switching Protocols" in resp_hdr

            def send_masked_ws(text):
                payload = text.encode("utf-8")
                mask = b"\x12\x34\x56\x78"
                masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
                frame = bytearray([0x81, 0x80 | len(payload)]) + mask + masked
                tls_sock.sendall(bytes(frame))

            send_masked_ws("BELL11\n")
            time.sleep(0.2)
            send_masked_ws("DEC$1970\n")
            time.sleep(0.2)
            send_masked_ws("SHOW SYSTEM\nBYE/DISCONNECT\n")

            collected = b""
            tls_sock.settimeout(2.0)
            try:
                while True:
                    chunk = tls_sock.recv(4096)
                    if not chunk:
                        break
                    collected += chunk
            except Exception:
                pass
            tls_sock.close()
            decoded_out = collected.decode("latin-1", errors="replace")
            assert "BELL11 [201,1]" in decoded_out
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

    def test_16_live_container_clerk_cloud_provisioning_and_wss_terminal(self):
        import base64
        import json
        import socket
        import ssl
        import time
        import urllib.request

        ssl_ctx = ssl._create_unverified_context()
        base_url = "https://127.0.0.1:8411"

        try:
            with urllib.request.urlopen(f"{base_url}/api/v1/status", context=ssl_ctx, timeout=3) as r:
                status_data = json.loads(r.read().decode("utf-8"))
        except Exception as exc:
            pytest.skip(f"Live dec-rsts-e container not reachable on :8411 ({exc})")

        # 1. Verify live container status & Clerk Cloud Live configuration from .env
        assert status_data["ok"] is True
        assert status_data["primary_os"] == "RSTS"
        assert status_data["https_port"] == 8411
        assert status_data["auth_providers"]["clerk"]["configured"] is True
        assert status_data["auth_providers"]["clerk"]["mode"] == "cloud"

        # 2. Verify GET / (VT100 Web Terminal) and GET /signup (Clerk Cloud Live script tag)
        with urllib.request.urlopen(f"{base_url}/", context=ssl_ctx, timeout=5) as r:
            term_html = r.read().decode("utf-8")
            assert r.status == 200
            assert "SIGN UP ($10/MO)" in term_html

        with urllib.request.urlopen(f"{base_url}/signup", context=ssl_ctx, timeout=5) as r:
            signup_html = r.read().decode("utf-8")
            assert r.status == 200
            assert "Clerk Auth: Cloud Live" in signup_html
            assert "data-clerk-publishable-key=\"pk_test_" in signup_html

        # 3. Provision a live subscriber account (LIVE_RSTS) on the running dec-rsts-e container
        signup_payload = json.dumps({
            "username": "LIVE_RSTS",
            "password": "PDP11$LIVE",
            "email": "live_rsts@dec.example.com",
            "plan": "LCS_RSTS_10",
            "clerk_user_id": "user_clerk_live_rsts",
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/v1/signup",
            data=signup_payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=5) as r:
            assert r.status == 201
            created = json.loads(r.read().decode("utf-8"))
            assert created["ok"] is True
            assert created["username"] == "LIVE_RSTS"
            assert created["ppn"].startswith("[201,")
            assert created["quota"] == 25000
            assert created["clerk_metadata"]["dec_username"] == "LIVE_RSTS"
            assigned_ppn = created["ppn"]

        # 4. Verify account is listed in GET /api/v1/users on the running container
        with urllib.request.urlopen(f"{base_url}/api/v1/users", context=ssl_ctx, timeout=5) as r:
            users_data = json.loads(r.read().decode("utf-8"))
            assert users_data["ok"] is True
            names = {u.get("name") for u in users_data["users"].values()}
            assert "LIVE_RSTS" in names

        # 5. Exercise Clerk subscription lifecycle webhooks on the running container
        clerk_cancel = json.dumps({
            "type": "subscription.canceled",
            "data": {"id": "user_clerk_live_rsts", "public_metadata": {"dec_username": "LIVE_RSTS"}},
        }).encode("utf-8")
        req_cc = urllib.request.Request(
            f"{base_url}/api/v1/webhooks/clerk",
            data=clerk_cancel,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_cc, context=ssl_ctx, timeout=5) as r:
            cc_res = json.loads(r.read().decode("utf-8"))
            assert cc_res["action"] == "SUSPENDED"
            assert cc_res["account"]["status"] == "DISUSER"

        clerk_paid = json.dumps({
            "type": "invoice.paid",
            "data": {"id": "user_clerk_live_rsts", "status": "active", "public_metadata": {"dec_username": "LIVE_RSTS"}},
        }).encode("utf-8")
        req_cp = urllib.request.Request(
            f"{base_url}/api/v1/webhooks/clerk",
            data=clerk_paid,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_cp, context=ssl_ctx, timeout=5) as r:
            cp_res = json.loads(r.read().decode("utf-8"))
            assert cp_res["action"] == "REACTIVATED"
            assert cp_res["account"]["status"] == "ACTIVE"

        # 6. Connect via live WSS (wss://127.0.0.1:8411/ws) to the running container,
        #    log in with LIVE_RSTS, and execute HELLO.BAS inside the container
        raw_sock = socket.create_connection(("127.0.0.1", 8411), timeout=5)
        tls_sock = ssl_ctx.wrap_socket(raw_sock, server_hostname="127.0.0.1")
        ws_key = base64.b64encode(os.urandom(16)).decode("ascii")
        handshake = (
            "GET /ws HTTP/1.1\r\n"
            "Host: 127.0.0.1:8411\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {ws_key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        tls_sock.sendall(handshake.encode("ascii"))
        resp_hdr = tls_sock.recv(1024).decode("latin-1", errors="replace")
        assert "101 Switching Protocols" in resp_hdr

        def send_masked_ws(text):
            payload = text.encode("utf-8")
            mask = b"\x21\x43\x65\x87"
            masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            frame = bytearray([0x81, 0x80 | len(payload)]) + mask + masked
            tls_sock.sendall(bytes(frame))

        send_masked_ws("LIVE_RSTS\n")
        time.sleep(0.2)
        send_masked_ws("PDP11$LIVE\n")
        time.sleep(0.2)
        send_masked_ws("RUN HELLO.BAS\nSHOW SYSTEM\nBYE/DISCONNECT\n")

        collected = b""
        tls_sock.settimeout(2.5)
        try:
            while True:
                chunk = tls_sock.recv(4096)
                if not chunk:
                    break
                collected += chunk
        except Exception:
            pass
        tls_sock.close()
        decoded_out = collected.decode("latin-1", errors="replace")
        assert f"LIVE_RSTS {assigned_ppn}" in decoded_out
        assert "HELLO LIVE_RSTS FROM LEGACY COMPUTING SYSTEMS PDP-11/70 RSTS/E!" in decoded_out

