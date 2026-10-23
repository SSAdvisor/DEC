import os
import subprocess
import pytest

VMS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VMS_EMU = os.path.join(VMS_ROOT, "bin", "vms-emu")


def run_vms(cmd_or_args, stdin_text=None, tmp_root=None):
    args = [VMS_EMU]
    if tmp_root:
        args.extend(["--root", str(tmp_root)])
    if isinstance(cmd_or_args, str):
        args.extend(["-c", cmd_or_args])
    else:
        args.extend(cmd_or_args)
    env = os.environ.copy()
    env.pop("DISPLAY", None)  # Ensure deterministic CLI mode during automated tests
    res = subprocess.run(
        args,
        input=stdin_text,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return res


def run_vms_docker(cmd_or_args, stdin_text=None):
    args = ["docker", "run", "--rm", "-i", "dec-vms:latest"]
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


class TestVMSEmulationHost:
    def test_01_boot_and_show_system(self, tmp_path):
        res = run_vms(["--boot", "-c", "SHOW SYSTEM"], tmp_root=tmp_path)
        assert res.returncode == 0
        assert "VAXstation 4000 Model 90" in res.stdout
        assert "VAX/VMS Version V5.5-2" in res.stdout
        assert "DECW$SERVER_0" in res.stdout
        assert "SWAPPER" in res.stdout

    def test_02_interactive_login_and_authorize(self, tmp_path):
        # Verify default interactive mode prompts for Username:, LOGOUT/BYE returns to Username:
        # without terminating the OS, and privileged SHUTDOWN halts the system.
        stdin_data = (
            "SYSTEM\n"
            "MANAGER\n"
            "SHOW PROCESS\n"
            "AUTHORIZE ADD OPERATOR\n"
            "AUTHORIZE\n"
            "LOGOUT\n"
            "DECW\n"
            "MOTIF\n"
            "SHOW DEFAULT\n"
            "SHUTDOWN\n"
            "BYE\n"
            "SYSTEM\n"
            "MANAGER\n"
            "SHUTDOWN\n"
        )
        res = run_vms([], stdin_text=stdin_data, tmp_root=tmp_path)
        assert res.returncode == 0
        assert res.stdout.count("Username: ") >= 3
        assert "Welcome to VAX/VMS V5.5-2 on node VAX01" in res.stdout
        assert "User Identifier:    [1,4]" in res.stdout
        assert "OPERATOR [200,201] added to SYSUAF.DAT" in res.stdout
        assert "DKA0:[DECW]" in res.stdout
        assert "%SYSTEM-F-NOPRIV" in res.stdout
        assert "logged out at" in res.stdout
        assert "%OPCOM-S-SYSHUT, VAX/VMS V5.5-2 shutdown completed on node VAX01" in res.stdout

    def test_03_system_management_and_monitoring(self, tmp_path):
        cmds = (
            "SHOW DEVICES; "
            "SHOW MEMORY; "
            "SHOW CPU; "
            "SHOW USERS; "
            "SHOW QUOTA; "
            "SHOW DECWINDOWS; "
            "SHOW APPS; "
            "SHOW NETWORK; "
            "MONITOR; "
            "SYSMAN; "
            "ANALYZE/RMS_FILE SYS$LOGIN:WELCOME.TXT"
        )
        res = run_vms(cmds, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "VAX01$DKA0:" in res.stdout
        assert "VAX01$WSA0:" in res.stdout
        assert "Main Memory (128.00Mb)" in res.stdout
        assert "PAGEFILE.SYS" in res.stdout
        assert "DECwindows Workstation Display & OSF/Motif 1.1 Environment" in res.stdout
        assert "The analysis uncovered NO errors." in res.stdout

    def test_04_ods2_filesystem_versioning_and_purge(self, tmp_path):
        cmds = (
            "DIRECTORY SYS$LOGIN:; "
            "TYPE SYS$LOGIN:WELCOME.TXT;1; "
            "COPY SYS$LOGIN:WELCOME.TXT SYS$LOGIN:REPORT.TXT; "
            "COPY SYS$LOGIN:WELCOME.TXT SYS$LOGIN:REPORT.TXT; "
            "SEARCH SYS$LOGIN:REPORT.TXT VAX/VMS; "
            "DIFFERENCES SYS$LOGIN:WELCOME.TXT SYS$LOGIN:REPORT.TXT; "
            "PURGE SYS$LOGIN:; "
            "RENAME SYS$LOGIN:REPORT.TXT SYS$LOGIN:FINAL.TXT; "
            "DELETE SYS$LOGIN:FINAL.TXT;1"
        )
        res = run_vms(cmds, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "WELCOME.TXT;1" in res.stdout
        assert "%COPY-S-COPIED" in res.stdout
        assert "Number of difference sections found: 0" in res.stdout
        assert "%PURGE-I-FILPURG, DKA0:[SYSMGR]REPORT.TXT;1 deleted" in res.stdout
        assert "%RENAME-S-RENAMED" in res.stdout
        assert "%DELETE-I-FILDEL" in res.stdout

    def test_05_dcl_lexicals_logicals_and_procedures(self, tmp_path):
        cmds = (
            "WRITE SYS$OUTPUT F$GETSYI(\"VERSION\"); "
            "WRITE SYS$OUTPUT F$GETSYI(\"NODENAME\"); "
            "WRITE SYS$OUTPUT F$USER(); "
            "WRITE SYS$OUTPUT F$ENVIRONMENT(\"DEFAULT\"); "
            "DEFINE MY_WORK DKA0:[SYSMGR]; "
            "SET DISPLAY/CREATE/NODE=192.168.1.50; "
            "SHOW LOGICAL; "
            "DEASSIGN MY_WORK; "
            "@SYS$LOGIN:LOGIN.COM"
        )
        res = run_vms(cmds, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "V5.5-2" in res.stdout
        assert "VAX01" in res.stdout
        assert "[1,4]" in res.stdout
        assert "DKA0:[SYSMGR]" in res.stdout
        assert "192.168.1.50:0.0" in res.stdout
        assert "VAX/VMS V5.5-2 SYSTEM [1,4] Session Ready on Node VAX01" in res.stdout

    def test_06_basic_compile_link_run_edt_and_queues(self, tmp_path):
        res = run_vms(
            "BASIC SYS$LOGIN:HELLO.BAS; DIR; LINK SYS$LOGIN:HELLO.OBJ; RUN SYS$LOGIN:HELLO.EXE; DELETE SYS$LOGIN:HELLO.OBJ; PRINT SYS$LOGIN:WELCOME.TXT; SHOW QUEUE /ALL",
            tmp_root=tmp_path,
        )
        assert res.returncode == 0
        assert "HELLO.OBJ;1" in res.stdout
        assert "HELLO FROM DEC VAX/VMS V5.5-2 ON VAXSTATION 4000!" in res.stdout
        assert "SYS$PRINT" in res.stdout

        edt_res = run_vms("EDIT/EDT", stdin_text="WELCOME.TXT\nTYPE 1:3\nQUIT\n", tmp_root=tmp_path)
        assert edt_res.returncode == 0
        assert "Welcome to VAX/VMS V5.5-2" in edt_res.stdout

    def test_06b_vax_basic_v35_and_openvms_linker_opt_map(self, tmp_path):
        # Compile VAXDEMO.BAS with /LIST, link with VAXDEMO.OPT/OPT and /MAP/FULL, and run VAXDEMO.EXE
        cmds = (
            "BASIC/LIST SYS$LOGIN:VAXDEMO.BAS; "
            "LINK/MAP/FULL SYS$LOGIN:VAXDEMO.OBJ,SYS$LOGIN:VAXDEMO.OPT/OPT; "
            "RUN SYS$LOGIN:VAXDEMO.EXE; "
            "TYPE SYS$LOGIN:VAXDEMO.MAP"
        )
        res = run_vms(cmds, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "VAX BASIC V3.5-00: Compiled VAXDEMO.BAS -> VAXDEMO.OBJ (0 errors)" in res.stdout
        assert "DEC VAX BASIC V3.5 ON VAX/VMS V5.5-2" in res.stdout
        assert "EMPLOYEE:   DR. GORDON BELL" in res.stdout
        assert "DEPARTMENT: VAX ARCHITECTURE & VMS KERNEL" in res.stdout
        assert "TOTAL COMP: 97750" in res.stdout
        assert "OpenVMS VAX Linker V05-05 Image Map" in res.stdout
        assert "V03-05" in res.stdout

        # Also test interactive VAX BASIC V3.5 environment launched via DCL 'BASIC'
        repl_res = run_vms("BASIC", stdin_text="NEW REPLTEST\n10 PRINT \"VMS BASIC REPL READY\"\n20 END\nRUN\nEXIT\n", tmp_root=tmp_path)
        assert repl_res.returncode == 0
        assert "VAX BASIC V3.5-00" in repl_res.stdout
        assert "VMS BASIC REPL READY" in repl_res.stdout

    def test_07_vms_layered_applications(self, tmp_path):
        app_tests = [
            ("HAMURABI", "0\n0\n0\n0\n", "HAMURABI"),
            ("SORT", "EXIT\n", "SORT-11"),
            ("RMSUTILS", "HELP\nEXIT\n", "RMS"),
            ("ADE", "SAMPLE\nLIST\nEXIT\n", "ADE"),
            ("DATATRIEVE", "READY YACHTS\nPRINT FIRST 2\nEXIT\n", "ALBERG"),
            ("DECGRAPH", "SAMPLE\nPLOT\nEXIT\n", "DECGRAPH"),
            ("MAIL", "SAMPLE\nDIR\nEXIT\n", "DECMAIL"),
            ("DECWORD", "SAMPLE\nDIR\nEXIT\n", "DECWORD"),
            ("FMS", "SAMPLE\nDIR\nEXIT\n", "FMS-11"),
            ("MENU", "SAMPLE\nDIR\nEXIT\n", "MENU-11"),
            ("INDENT", "SAMPLE\nCHECK\nEXIT\n", "INDENT"),
        ]
        for verb, app_stdin, expected_marker in app_tests:
            res = run_vms(verb, stdin_text=app_stdin, tmp_root=tmp_path)
            assert res.returncode == 0, f"{verb} failed: {res.stdout} {res.stderr}"
            assert expected_marker.upper() in res.stdout.upper()

    def test_08_decwindows_workstation_suite_and_sys_images(self, tmp_path):
        # Verify DECwindows Session Manager & all 11 DECwindows apps run under VAX/VMS
        decw_tests = [
            ("RUN SYS$SYSTEM:DECW$SESSION --cli", "EXIT\n", "SESSION"),
            ("RUN SYS$SYSTEM:DECW$DECTERM --cli", "SAMPLE\nSHOW\nEXIT\n", "DECTERM"),
            ("RUN SYS$SYSTEM:DECW$BOOKREADER --cli", "SAMPLE\nDIR\nEXIT\n", "BOOKREADER"),
            ("RUN SYS$SYSTEM:DECW$CALENDAR --cli", "SAMPLE\nSHOW\nEXIT\n", "CALENDAR"),
            ("RUN SYS$SYSTEM:DECW$CARDFILER --cli", "SAMPLE\nDIR\nEXIT\n", "CARDFILER"),
            ("RUN SYS$SYSTEM:DECW$CDAVIEWER --cli", "SAMPLE\nSHOW\nEXIT\n", "CDA"),
            ("RUN SYS$SYSTEM:DECW$CALC --cli", "SAMPLE\nSHOW\nEXIT\n", "CALCULATOR"),
            ("RUN SYS$SYSTEM:DECW$CLOCK --cli", "SAMPLE\nSHOW\nEXIT\n", "CLOCK"),
            ("RUN SYS$SYSTEM:DECW$SOUND --cli", "SAMPLE\nDIR\nEXIT\n", "DECSOUND"),
            ("RUN SYS$SYSTEM:DECW$MAIL --cli", "SAMPLE\nDIR\nEXIT\n", "MAIL"),
            ("RUN SYS$SYSTEM:VUE$MASTER --cli", "SAMPLE\nDIR\nEXIT\n", "FILEVIEW"),
            ("RUN SYS$SYSTEM:DECW$NOTEPAD --cli", "SAMPLE\nSHOW\nEXIT\n", "NOTEPAD"),
        ]
        for cmd, app_stdin, marker in decw_tests:
            res = run_vms(cmd, stdin_text=app_stdin, tmp_root=tmp_path)
            assert res.returncode == 0, f"{cmd} failed: {res.stdout} {res.stderr}"
            assert marker.upper() in res.stdout.upper(), f"Missing {marker} in {cmd}"

    def test_09_rejects_unsupported_pdp11_dibs(self, tmp_path):
        for pdp11_only in ("DIBS", "DIBS11", "CTS500", "RUN SYS$SYSTEM:DIBS"):
            res = run_vms(pdp11_only, tmp_root=tmp_path)
            assert res.returncode != 0
            assert "%DCL-W-UNSUPOS" in res.stdout
            assert "16-bit PDP-11 RSTS/E" in res.stdout

    def test_09b_dcl_account_management_and_authorize_utility(self, tmp_path):
        # 1. Test DCL CREATE/ACCOUNT, SHOW ACCOUNT /FULL, MODIFY/ACCOUNT, SET PASSWORD
        r1 = run_vms(
            "CREATE/ACCOUNT ADAMS /UIC=[210,10] /PASSWORD=VAX9000 /QUOTA=80000 /PRIVILEGES=(SYSPRV,TMPMBX); SHOW ACCOUNT ADAMS /FULL",
            tmp_root=tmp_path,
        )
        assert r1.returncode == 0
        assert "%UAF-I-ADDMSG" in r1.stdout
        assert "ADAMS" in r1.stdout
        assert "[210,10]" in r1.stdout

        # 2. Verify persistence in SYSUAF.JSON and interactive UAF> prompt via RUN SYS$SYSTEM:AUTHORIZE
        uaf_stdin = (
            "SYSTEM\n"
            "MANAGER\n"
            "RUN SYS$SYSTEM:AUTHORIZE\n"
            "ADD MILLER /UIC=[210,20] /PASSWORD=ALPHA1 /ACCOUNT=ENGR /QUOTA=95000\n"
            "GRANT/IDENTIFIER=DECW$USERS MILLER\n"
            "MODIFY ADAMS /QUOTA=120000 /FLAGS=DISUSER\n"
            "SHOW MILLER /FULL\n"
            "EXIT\n"
            "SET PASSWORD MILLER /PASSWORD=NEWVMS1\n"
            "DELETE/ACCOUNT ADAMS\n"
            "LOGOUT\n"
        )
        r2 = subprocess.run(
            [VMS_EMU, "--root", str(tmp_path)],
            input=uaf_stdin,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert r2.returncode == 0
        assert "UAF>" in r2.stdout
        assert "%UAF-I-ADDMSG" in r2.stdout
        assert "%UAF-I-GRANTMSG" in r2.stdout
        assert "DECW$USERS" in r2.stdout
        assert "%SET-S-PASSCHG" in r2.stdout
        assert "%UAF-I-REMMSG" in r2.stdout

        # 3. Verify SYSTEM [1,4] cannot be removed
        r3 = run_vms("DELETE/ACCOUNT SYSTEM", tmp_root=tmp_path)
        assert r3.returncode != 0
        assert "cannot remove protected SYSTEM" in r3.stdout


class TestVMSDockerContainer:
    def test_10_docker_image_and_system_commands(self):
        res = run_vms_docker("SHOW SYSTEM; SHOW DEVICES; SHOW MEMORY; SHOW DECWINDOWS")
        assert res.returncode == 0
        assert "VAX/VMS V5.5-2 on node VAX01" in res.stdout
        assert "VAX01$DKA0:" in res.stdout
        assert "DECW$SERVER_0" in res.stdout

    def test_11_docker_compile_link_and_run_vax_basic(self):
        res = run_vms_docker(
            "BASIC SYS$LOGIN:HELLO.BAS; DIR; LINK SYS$LOGIN:HELLO.OBJ; RUN SYS$LOGIN:HELLO; DELETE SYS$LOGIN:HELLO.OBJ; "
            "BASIC/LIST SYS$LOGIN:VAXDEMO.BAS; LINK/MAP/FULL SYS$LOGIN:VAXDEMO.OBJ,SYS$LOGIN:VAXDEMO.OPT/OPT; RUN SYS$LOGIN:VAXDEMO.EXE"
        )
        assert res.returncode == 0
        assert "HELLO.OBJ;1" in res.stdout
        assert "HELLO FROM DEC VAX/VMS V5.5-2 ON VAXSTATION 4000!" in res.stdout
        assert "VAX BASIC V3.5-00: Compiled VAXDEMO.BAS -> VAXDEMO.OBJ (0 errors)" in res.stdout
        assert "EMPLOYEE:   DR. GORDON BELL" in res.stdout
        assert "TOTAL COMP: 97750" in res.stdout

    def test_12_docker_execute_decwindows_and_vms_apps_and_reject_dibs(self):
        res_clock = run_vms_docker("RUN SYS$SYSTEM:DECW$CLOCK --cli", stdin_text="SAMPLE\nSHOW\nEXIT\n")
        assert res_clock.returncode == 0
        assert "CLOCK" in res_clock.stdout.upper()

        res_dtr = run_vms_docker("DATATRIEVE", stdin_text="READY YACHTS\nPRINT FIRST 2\nEXIT\n")
        assert res_dtr.returncode == 0
        assert "ALBERG" in res_dtr.stdout.upper()

        res_unsup = run_vms_docker("DIBS")
        assert res_unsup.returncode != 0
        assert "%DCL-W-UNSUPOS" in res_unsup.stdout

    def test_13_multiuser_concurrent_sessions_and_network(self, tmp_path):
        # Launch Session 1 (OPA0: / PID 00000214) and run Session 2 concurrently (FTA1: / PID 00000215)
        p1 = subprocess.Popen(
            [VMS_EMU, "--root", str(tmp_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            p1.stdin.write("SYSTEM\nMANAGER\nSHOW SYSTEM\n")
            p1.stdin.flush()
            import time
            time.sleep(0.4)

            r2 = run_vms(
                [],
                stdin_text="DECW\nMOTIF\nSHOW USERS\nSHOW SYSTEM\nSHOW PROCESS\nSHOW NETWORK\nLOGOUT/DISCONNECT\n",
                tmp_root=tmp_path,
            )
            assert r2.returncode == 0
            assert "Total number of interactive users = 2" in r2.stdout
            assert "00000214" in r2.stdout and "OPA0:" in r2.stdout
            assert "00000215" in r2.stdout and "FTA1:" in r2.stdout
            assert "Multi-User Terminal Server: SSH on port" in r2.stdout
        finally:
            p1.stdin.write("SHUTDOWN\n")
            p1.stdin.flush()
            p1.communicate(timeout=5)

    def test_14_x11_web_workstation_png_and_bridge(self):
        import sys
        sys.path.insert(0, os.path.join(VMS_ROOT, "src"))
        import multiuser_service

        # Verify pure-Python BGRA -> RGBA PNG encoder used by /ws-x11
        raw_bgra = bytes([0x68, 0x53, 0x3B, 0x00] * (64 * 48))
        png = multiuser_service.encode_bgra_to_png(raw_bgra, 64, 48)
        assert png.startswith(b"\x89PNG\r\n\x1a\n")
        assert b"IHDR" in png and b"IDAT" in png and b"IEND" in png

        # Verify HTML template includes X11 canvas and /ws-x11 WebSocket support when enable_x11=True
        srv = multiuser_service.MultiUserTerminalServer(
            emu_cmd=[VMS_EMU],
            os_title="DEC VAX/VMS X11 Test",
            header_title="DEC VAXstation 4000 X11",
            https_port=18455,
            enable_x11=False,
        )
        assert b"x11-canvas" in srv.html_bytes
        assert b"/ws-x11" in srv.html_bytes
        assert b"DECW$STARTLOGIN" in srv.html_bytes

        # Verify unauthenticated sessions are blocked and wrong/blank passwords fail
        assert srv.get_session_auth_user("unauth_sid") is None
        ok_bad, _, err_bad = srv.verify_sysuaf_credentials("SYSTEM", "WRONGPASS")
        assert not ok_bad and "NOTVALID" in err_bad
        ok_blank, _, err_blank = srv.verify_sysuaf_credentials("SYSTEM", "")
        assert not ok_blank and "NOTVALID" in err_blank
        ok_nouser, _, err_nouser = srv.verify_sysuaf_credentials("NO_SUCH_USER_99", "PASS")
        assert not ok_nouser and "NOSUCHUSER" in err_nouser
