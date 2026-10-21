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
        stdin_data = (
            "SYSTEM\n"
            "MANAGER\n"
            "SHOW PROCESS\n"
            "AUTHORIZE ADD OPERATOR\n"
            "AUTHORIZE\n"
            "LOGIN DECW\n"
            "SHOW DEFAULT\n"
            "LOGOUT\n"
        )
        res = run_vms(["--login"], stdin_text=stdin_data, tmp_root=tmp_path)
        assert res.returncode == 0
        assert "Username: " in res.stdout
        assert "Welcome to VAX/VMS V5.5-2 on node VAX01" in res.stdout
        assert "User Identifier:    [1,4]" in res.stdout
        assert "OPERATOR [200,201] added to SYSUAF.DAT" in res.stdout
        assert "DKA0:[DECW]" in res.stdout
        assert "logged out at" in res.stdout

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
        res = run_vms_docker("BASIC SYS$LOGIN:HELLO.BAS; DIR; LINK SYS$LOGIN:HELLO.OBJ; RUN SYS$LOGIN:HELLO; DELETE SYS$LOGIN:HELLO.OBJ")
        assert res.returncode == 0
        assert "HELLO.OBJ;1" in res.stdout
        assert "HELLO FROM DEC VAX/VMS V5.5-2 ON VAXSTATION 4000!" in res.stdout

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
