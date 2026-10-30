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

    def test_06c_vax_17_language_compilers_and_interactive_repls(self, tmp_path):
        # Verify all 17 VAX language compilers compile DEMO.<EXT> -> .OBJ, link via LINK, and run via RUN
        lang_cases = [
            ("MACRO", "DEMO.MAR", "M_DEMO", "VAX MACRO V05-00"),
            ("FORTRAN", "DEMO.FOR", "F_DEMO", "VAX FORTRAN V5.5"),
            ("COBOL", "DEMO.COB", "COB_DEMO", "VAX COBOL V4.3"),
            ("CC", "DEMO.C", "C_DEMO", "VAX C V3.2"),
            ("PASCAL", "DEMO.PAS", "PAS_DEMO", "VAX PASCAL V4.3"),
            ("PLI", "DEMO.PLI", "PLI_DEMO", "VAX PL/I V3.5"),
            ("ADA", "DEMO.ADA", "ADA_DEMO", "VAX ADA V2.2"),
            ("DIBOL", "DEMO.DBL", "DBL_DEMO", "VAX DIBOL V4.1"),
            ("BLISS32", "DEMO.B32", "B32_DEMO", "VAX BLISS-32 V4.7"),
            ("BLISS16", "DEMO.B16", "B16_DEMO", "VAX BLISS-16 V4.2"),
            ("RPG", "DEMO.RPG", "RPG_DEMO", "VAX RPG II V2.2"),
            ("APL", "DEMO.APL", "APL_DEMO", "VAX APL V3.1"),
            ("LISP", "DEMO.LSP", "LSP_DEMO", "VAX LISP V3.1"),
            ("OPS5", "DEMO.OPS", "OPS_DEMO", "VAX OPS5 V2.2"),
            ("DSM", "DEMO.DSM", "DSM_DEMO", "VAX DSM V6.0"),
            ("SCAN", "DEMO.SCN", "SCN_DEMO", "VAX SCAN V1.2"),
            ("CORAL", "DEMO.COR", "COR_DEMO", "VAX CORAL 66 V2.1"),
        ]
        for verb, demo_src, out_stem, expected in lang_cases:
            cmds = (
                f"{verb}/LIST={out_stem}.LST/OBJECT={out_stem}.OBJ SYS$LOGIN:{demo_src}; "
                f"LINK/EXECUTABLE={out_stem}.EXE {out_stem}.OBJ; "
                f"RUN {out_stem}.EXE"
            )
            res = run_vms(cmds, tmp_root=tmp_path)
            assert res.returncode == 0, f"{verb} failed: {res.stdout} {res.stderr}"
            assert expected.upper() in res.stdout.upper(), f"Missing '{expected}' in {verb}: {res.stdout}"

        # Verify interactive REPL modes for APL, LISP, OPS5, and DSM from DCL
        apl_res = run_vms("APL", stdin_text="+/ \u2373 10\n)OFF\n", tmp_root=tmp_path)
        assert apl_res.returncode == 0
        assert "55" in apl_res.stdout

        lisp_res = run_vms("LISP", stdin_text="(+ 20 22)\n(EXIT)\n", tmp_root=tmp_path)
        assert lisp_res.returncode == 0
        assert "42" in lisp_res.stdout

        dsm_res = run_vms("DSM", stdin_text="SET X=7*8 WRITE \"DSM=\",X,!\nHALT\n", tmp_root=tmp_path)
        assert dsm_res.returncode == 0
        assert "DSM=56" in dsm_res.stdout

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
            ("WP51", "SAMPLE\nREVEAL\nEXIT\n", "WORDPERFECT"),
            ("INTERLEAF", "SAMPLE\nLIST\nEXIT\n", "INTERLEAF"),
            ("LOTUS123", "SAMPLE\nLIST\nEXIT\n", "LOTUS 1-2-3"),
            ("IFPS", "SAMPLE\nLIST\nEXIT\n", "IFPS"),
            ("SYSTEMW", "SAMPLE\nLIST\nEXIT\n", "SYSTEM W"),
            ("ORACLE", "SAMPLE\nLIST\nEXIT\n", "ORACLE"),
            ("INGRES", "SAMPLE\nLIST\nEXIT\n", "INGRES"),
            ("FOCUS", "SAMPLE\nLIST\nEXIT\n", "FOCUS"),
            ("POWERHOUSE", "SAMPLE\nLIST\nEXIT\n", "POWERHOUSE"),
            ("S1032", "SAMPLE\nLIST\nEXIT\n", "SYSTEM 1032"),
            ("MANMAN", "SAMPLE\nLIST\nEXIT\n", "MANMAN"),
            ("CERNER", "SAMPLE\nLIST\nEXIT\n", "PATHNET"),
            ("SAS", "SAMPLE\nLIST\nEXIT\n", "WORK.CLINICAL"),
            ("RS1", "SAMPLE\nLIST\nEXIT\n", "RS/1"),
            ("SPICE3", "SAMPLE\nLIST\nEXIT\n", "SPICE"),
            ("ANSYS", "SAMPLE\nLIST\nEXIT\n", "ANSYS"),
            ("GAUSSIAN", "SAMPLE\nLIST\nEXIT\n", "GAUSSIAN"),
            ("DISKEEPER", "SAMPLE\nLIST\nEXIT\n", "INDEXF.SYS"),
            ("ROBOMON", "SAMPLE\nLIST\nEXIT\n", "ROBOMON"),
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

    def test_11b_docker_compile_link_and_run_17_vax_languages(self):
        cmds = (
            "MACRO/OBJECT=M.OBJ SYS$LOGIN:DEMO.MAR; LINK/EXE=M.EXE M.OBJ; RUN M.EXE; "
            "FORTRAN/OBJECT=F.OBJ SYS$LOGIN:DEMO.FOR; LINK/EXE=F.EXE F.OBJ; RUN F.EXE; "
            "COBOL/OBJECT=COB.OBJ SYS$LOGIN:DEMO.COB; LINK/EXE=COB.EXE COB.OBJ; RUN COB.EXE; "
            "CC/OBJECT=C.OBJ SYS$LOGIN:DEMO.C; LINK/EXE=C.EXE C.OBJ; RUN C.EXE; "
            "PASCAL/OBJECT=PAS.OBJ SYS$LOGIN:DEMO.PAS; LINK/EXE=PAS.EXE PAS.OBJ; RUN PAS.EXE; "
            "PLI/OBJECT=PLI.OBJ SYS$LOGIN:DEMO.PLI; LINK/EXE=PLI.EXE PLI.OBJ; RUN PLI.EXE; "
            "ADA/OBJECT=ADA.OBJ SYS$LOGIN:DEMO.ADA; LINK/EXE=ADA.EXE ADA.OBJ; RUN ADA.EXE; "
            "DIBOL/OBJECT=DBL.OBJ SYS$LOGIN:DEMO.DBL; LINK/EXE=DBL.EXE DBL.OBJ; RUN DBL.EXE; "
            "BLISS32/OBJECT=B32.OBJ SYS$LOGIN:DEMO.B32; LINK/EXE=B32.EXE B32.OBJ; RUN B32.EXE; "
            "BLISS16/OBJECT=B16.OBJ SYS$LOGIN:DEMO.B16; LINK/EXE=B16.EXE B16.OBJ; RUN B16.EXE; "
            "RPG/OBJECT=RPG.OBJ SYS$LOGIN:DEMO.RPG; LINK/EXE=RPG.EXE RPG.OBJ; RUN RPG.EXE; "
            "APL/OBJECT=APL.OBJ SYS$LOGIN:DEMO.APL; LINK/EXE=APL.EXE APL.OBJ; RUN APL.EXE; "
            "LISP/OBJECT=LSP.OBJ SYS$LOGIN:DEMO.LSP; LINK/EXE=LSP.EXE LSP.OBJ; RUN LSP.EXE; "
            "OPS5/OBJECT=OPS.OBJ SYS$LOGIN:DEMO.OPS; LINK/EXE=OPS.EXE OPS.OBJ; RUN OPS.EXE; "
            "DSM/OBJECT=DSM.OBJ SYS$LOGIN:DEMO.DSM; LINK/EXE=DSM.EXE DSM.OBJ; RUN DSM.EXE; "
            "SCAN/OBJECT=SCN.OBJ SYS$LOGIN:DEMO.SCN; LINK/EXE=SCN.EXE SCN.OBJ; RUN SCN.EXE; "
            "CORAL/OBJECT=COR.OBJ SYS$LOGIN:DEMO.COR; LINK/EXE=COR.EXE COR.OBJ; RUN COR.EXE"
        )
        res = run_vms_docker(cmds)
        assert res.returncode == 0, f"Docker 17-lang test failed: {res.stdout} {res.stderr}"
        for marker in (
            "VAX MACRO V05-00",
            "VAX FORTRAN V5.5",
            "VAX COBOL V4.3",
            "VAX C V3.2",
            "VAX PASCAL V4.3",
            "VAX PL/I V3.5",
            "VAX ADA V2.2",
            "VAX DIBOL V4.1",
            "VAX BLISS-32 V4.7",
            "VAX BLISS-16 V4.2",
            "VAX RPG II V2.2",
            "VAX APL V3.1",
            "VAX LISP V3.1",
            "VAX OPS5 V2.2",
            "VAX DSM V6.0",
            "VAX SCAN V1.2",
            "VAX CORAL 66 V2.1",
        ):
            assert marker in res.stdout.upper(), f"Missing '{marker}' in Docker output"

    def test_12_docker_execute_decwindows_and_vms_apps_and_reject_dibs(self):
        res_clock = run_vms_docker("RUN SYS$SYSTEM:DECW$CLOCK --cli", stdin_text="SAMPLE\nSHOW\nEXIT\n")
        assert res_clock.returncode == 0
        assert "CLOCK" in res_clock.stdout.upper()

        res_dtr = run_vms_docker("DATATRIEVE", stdin_text="READY YACHTS\nPRINT FIRST 2\nEXIT\n")
        assert res_dtr.returncode == 0
        assert "ALBERG" in res_dtr.stdout.upper()

        for vms_cmd, vms_marker in (
            ("WP51", "WORDPERFECT"),
            ("LOTUS123", "LOTUS 1-2-3"),
            ("ORACLE", "ORACLE"),
            ("MANMAN", "MANMAN"),
            ("SAS", "WORK.CLINICAL"),
            ("SPICE3", "SPICE"),
            ("DISKEEPER", "INDEXF.SYS"),
        ):
            res_tp = run_vms_docker(vms_cmd, stdin_text="SAMPLE\nLIST\nEXIT\n")
            assert res_tp.returncode == 0
            assert vms_marker in res_tp.stdout.upper()

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

    def test_15_subscriber_provisioning_sysuaf_and_disuser(self, tmp_path):
        import sys
        sys.path.insert(0, os.path.join(VMS_ROOT, "src"))
        import vms_os
        import multiuser_service

        emu = vms_os.VMSEmulator(root_dir=str(tmp_path))
        ok, _ = emu.check_username_available("CUTLER")
        assert ok

        rec = emu.provision_subscriber_account(
            username="CUTLER",
            password="VMS$V55",
            email="cutler@dec.example.com",
            plan="LCS_VMS_10",
            clerk_user_id="user_clerk_202",
        )
        assert rec["ok"] is True
        assert rec["uic"] == "[200,201]"
        assert rec["quota"] == 50000
        assert "DECW$USERS" in rec["identifiers"]
        assert os.path.isfile(os.path.join(rec["dir_path"], "LOGIN.COM;1"))
        assert os.path.isfile(os.path.join(rec["dir_path"], "WELCOME.TXT;1"))
        assert os.path.isfile(os.path.join(rec["dir_path"], "HELLO.BAS;1"))

        ok_after, _ = emu.check_username_available("CUTLER")
        assert not ok_after

        # Verify interactive login at Username: prompt and execution of LOGIN.COM and HELLO.BAS
        login_res = run_vms(
            [],
            stdin_text=(
                "CUTLER\n"
                "VMS$V55\n"
                "@SYS$LOGIN:LOGIN.COM\n"
                "RUN SYS$LOGIN:HELLO.BAS\n"
                "LOGOUT/DISCONNECT\n"
            ),
            tmp_root=tmp_path,
        )
        assert login_res.returncode == 0
        assert "Welcome CUTLER ([200,201]) to Legacy Computing Systems VAX/VMS" in login_res.stdout
        assert "HELLO CUTLER FROM LEGACY COMPUTING SYSTEMS VAX/VMS V5.5-2!" in login_res.stdout

        # Suspend account (DISUSER) and verify VT220 and DECwindows X11 login are blocked
        upd = emu.update_subscriber_account("user_clerk_202", status="DISUSER")
        assert upd["flags"] == "DISUSER"

        dis_res = run_vms(
            [],
            stdin_text="CUTLER\nGUEST\nLOGOUT/DISCONNECT\n",
            tmp_root=tmp_path,
        )
        assert "%LOGIN-F-DISUSER, account is disabled" in dis_res.stdout

        env_prev = os.environ.get("VMS_FS_ROOT")
        os.environ["VMS_FS_ROOT"] = str(tmp_path)
        try:
            srv = multiuser_service.MultiUserTerminalServer(
                emu_cmd=[VMS_EMU],
                os_title="DEC VAX/VMS X11 Auth Test",
                header_title="DEC VAXstation 4000",
                https_port=18456,
                enable_x11=False,
            )
            ok_x11, _, err_x11 = srv.verify_sysuaf_credentials("CUTLER", "VMS$V55")
            assert not ok_x11 and "DISUSER" in err_x11
        finally:
            if env_prev is None:
                os.environ.pop("VMS_FS_ROOT", None)
            else:
                os.environ["VMS_FS_ROOT"] = env_prev

    def test_16_https_signup_portal_clerk_workos_webhooks_and_wss_login(self, tmp_path):
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
        env["VMS_FS_ROOT"] = str(tmp_path)
        srv_script = os.path.join(VMS_ROOT, "src", "multiuser_service.py")
        proc = subprocess.Popen(
            [
                "python3",
                srv_script,
                "--serve-https",
                "--emu",
                VMS_EMU,
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
                assert "VAX/VMS &amp; DECwindows" in html
                assert "$10 / month" in html

            # 2. Check username availability
            with urllib.request.urlopen(f"{base_url}/api/v1/users/check?username=VAXUSER1", context=ssl_ctx, timeout=5) as r:
                chk = json.loads(r.read().decode("utf-8"))
                assert chk["available"] is True

            # 2b. Create & validate 6-character alphanumeric + special char percentage discount coupons (100ths precision, never/days/months <= 1 yr)
            import urllib.error
            cpn_req = urllib.request.Request(
                f"{base_url}/api/v1/coupons",
                data=json.dumps({"discount_percent": 12.75, "duration_unit": "months", "duration_value": 6}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(cpn_req, context=ssl_ctx, timeout=5) as r:
                assert r.status == 201
                cpn = json.loads(r.read().decode("utf-8"))["coupon"]
                assert (
                    len(cpn["code"]) == 6
                    and any(c.isalpha() for c in cpn["code"])
                    and any(c.isdigit() for c in cpn["code"])
                    and any(not c.isalnum() for c in cpn["code"])
                )
                assert cpn["discount_percent"] == 12.75
                assert cpn["duration_unit"] == "months" and cpn["duration_value"] == 6
                vms_coupon_code = cpn["code"]

            # Reject > 1 year (366 days, 13 months)
            for bad_payload in (
                {"discount_percent": 50.0, "duration_unit": "days", "duration_value": 366},
                {"discount_percent": 50.0, "duration_unit": "months", "duration_value": 13},
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

            # 3. POST /api/v1/signup ($10/mo VAX/VMS subscriber with 12.75% 6-digit coupon -> $8.72)
            signup_payload = json.dumps({
                "username": "VAXUSER1",
                "password": "VAX$1991",
                "email": "vaxuser1@dec.example.com",
                "plan": "LCS_VMS_10",
                "clerk_user_id": "user_clerk_vax1",
                "coupon_code": vms_coupon_code,
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
                assert created["uic"] == "[200,201]"
                assert created["clerk_metadata"]["dec_username"] == "VAXUSER1"
                assert created["coupon_applied"]["code"] == vms_coupon_code
                assert created["discounted_price_usd"] == 8.72

            # 3c. Verify /admin Web Admin page, SYSTEM user authentication, and BASIC-PLUS-2 COUPON CLI integration
            with urllib.request.urlopen(f"{base_url}/admin", context=ssl_ctx, timeout=5) as r:
                admin_html = r.read().decode("utf-8")
                assert r.status == 200
                assert "LEGACY COMPUTING SYSTEMS — SYSTEM ADMIN" in admin_html
                assert "COUPON.BAS" in admin_html

            req_sys = urllib.request.Request(
                f"{base_url}/api/v1/admin/login",
                data=json.dumps({"username": "SYSTEM", "password": "MANAGER"}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req_sys, context=ssl_ctx, timeout=5) as r:
                auth_data = json.loads(r.read().decode("utf-8"))
                assert auth_data["ok"] is True
                assert auth_data["authenticated"] is True
                admin_token = auth_data["admin_token"]

            req_bp2 = urllib.request.Request(
                f"{base_url}/api/v1/admin/coupon-cli",
                data=json.dumps({"command": "CREATE V9$k!2, 50.00, MONTHS, 6, VMS BP2 Admin Promo; LIST"}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json", "X-LCS-Admin-Token": admin_token},
            )
            with urllib.request.urlopen(req_bp2, context=ssl_ctx, timeout=5) as r:
                bp2_res = json.loads(r.read().decode("utf-8"))
                assert bp2_res["ok"] is True
                assert "[Coupon Created: V9$k!2 | 50.00% OFF" in bp2_res["output"]
                assert "V9$k!2" in bp2_res["coupons"]
                assert bp2_res["coupons"]["V9$k!2"]["discount_percent"] == 50.0

            # Also verify VAX/VMS DCL privilege check on COUPON (blocked for GUEST)
            res_guest = run_vms(["-u", "GUEST", "-c", "COUPON"], tmp_root=tmp_path)
            assert res_guest.returncode != 0
            assert "%CLI-E-NOPRIV" in res_guest.stdout

            # 4. Clerk webhook: subscription.canceled -> DISUSER, then invoice.paid -> ACTIVE
            clerk_cancel = json.dumps({
                "type": "subscription.canceled",
                "data": {"id": "user_clerk_vax1", "public_metadata": {"dec_username": "VAXUSER1"}},
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
                "data": {"id": "user_clerk_vax1", "status": "active", "public_metadata": {"dec_username": "VAXUSER1"}},
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

            # 5. WorkOS SCIM webhook: dsync.user.created -> [300,1], dsync.user.suspended -> DISUSER
            wos_create = json.dumps({
                "event": "dsync.user.created",
                "data": {
                    "id": "wos_vms_01",
                    "organization_id": "org_cern_lab",
                    "username": "CERNENG",
                    "emails": [{"value": "eng@cern.ch"}],
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
                assert wc_res["account"]["uic"] == "[300,1]"
                assert wc_res["account"]["quota"] == 100000
                assert wc_res["enterprise_billing"]["base_price_monthly"] == 199
                assert wc_res["enterprise_billing"]["included_active_seats"] == 15
                assert wc_res["enterprise_billing"]["additional_seat_price_monthly"] == 10
                assert wc_res["enterprise_billing"]["active_seats"] >= 1
                assert wc_res["enterprise_billing"]["monthly_total_usd"] == 199

            # Verify GET /api/v1/enterprise/seats?org=org_cern_lab reports active seat metering
            with urllib.request.urlopen(f"{base_url}/api/v1/enterprise/seats?org=org_cern_lab", context=ssl_ctx, timeout=5) as r:
                sm = json.loads(r.read().decode("utf-8"))["seat_metering"]
                assert sm["active_seats"] >= 1
                assert sm["base_price_monthly"] == 199
                assert sm["included_active_seats"] == 15

            wos_susp = json.dumps({
                "event": "dsync.user.suspended",
                "data": {"id": "wos_vms_01", "organization_id": "org_cern_lab", "username": "CERNENG"},
            }).encode("utf-8")
            req_ws = urllib.request.Request(
                f"{base_url}/api/v1/webhooks/workos",
                data=wos_susp,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req_ws, context=ssl_ctx, timeout=5) as r:
                ws_res = json.loads(r.read().decode("utf-8"))
                assert ws_res["action"] == "SUSPENDED"
                assert ws_res["account"]["status"] == "DISUSER"
                assert ws_res["enterprise_billing"]["suspended_seats"] >= 1

            # 6. Connect via live WSS (/ws?sid=test_vaxuser1), verify SYSTEM ADMIN menu option is hidden by default,
            #    and verify terminal login as SYSTEM ([1,4]) automatically authenticates /api/v1/admin/session?sid=test_vaxuser1
            with urllib.request.urlopen(f"{base_url}/", context=ssl_ctx, timeout=5) as r_root:
                root_html = r_root.read().decode("utf-8")
                assert 'id="btn-sys-admin"' in root_html
                assert 'style="display:none;' in root_html

            raw_sock = socket.create_connection(("127.0.0.1", port), timeout=5)
            tls_sock = ssl_ctx.wrap_socket(raw_sock, server_hostname="127.0.0.1")
            ws_key = base64.b64encode(os.urandom(16)).decode("ascii")
            handshake = (
                f"GET /ws?sid=test_vaxuser1 HTTP/1.1\r\n"
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

            time.sleep(0.25)
            with pytest.raises(urllib.error.HTTPError) as exc_unauth:
                urllib.request.urlopen(f"{base_url}/api/v1/admin/session?sid=test_vaxuser1", context=ssl_ctx, timeout=5)
            assert exc_unauth.value.code == 401

            send_masked_ws("VAXUSER1\n")
            time.sleep(0.2)
            send_masked_ws("VAX$1991\n")
            time.sleep(0.25)
            with pytest.raises(urllib.error.HTTPError) as exc_vaxuser:
                urllib.request.urlopen(f"{base_url}/api/v1/admin/session?sid=test_vaxuser1", context=ssl_ctx, timeout=5)
            assert exc_vaxuser.value.code == 401

            send_masked_ws("SHOW PROCESS\nLOGOUT\n")
            time.sleep(0.25)
            send_masked_ws("SYSTEM\n")
            time.sleep(0.2)
            send_masked_ws("MANAGER\n")
            time.sleep(0.3)
            with urllib.request.urlopen(f"{base_url}/api/v1/admin/session?sid=test_vaxuser1", context=ssl_ctx, timeout=5) as r_sys_sess:
                assert r_sys_sess.status == 200
                sess_json = json.loads(r_sys_sess.read().decode("utf-8"))
                assert sess_json["authenticated"] is True
                assert sess_json["terminal_authenticated"] is True
                assert sess_json["username"] == "SYSTEM"

            send_masked_ws("LOGOUT\n")
            time.sleep(0.3)
            with pytest.raises(urllib.error.HTTPError) as exc_after_logout:
                urllib.request.urlopen(f"{base_url}/api/v1/admin/session?sid=test_vaxuser1", context=ssl_ctx, timeout=5)
            assert exc_after_logout.value.code == 401
            send_masked_ws("LOGOUT/DISCONNECT\n")

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
            assert "[200,201]" in decoded_out
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

    def test_17_live_container_clerk_cloud_dual_bundle_and_x11_workstation(self):
        import base64
        import json
        import socket
        import ssl
        import time
        import urllib.request

        ssl_ctx = ssl._create_unverified_context()
        base_url = "https://127.0.0.1:8455"

        try:
            with urllib.request.urlopen(f"{base_url}/api/v1/status", context=ssl_ctx, timeout=3) as r:
                status_data = json.loads(r.read().decode("utf-8"))
        except Exception as exc:
            pytest.skip(f"Live dec-vms container not reachable on :8455 ({exc})")

        # 1. Verify live container status & Clerk Cloud Live configuration from .env
        assert status_data["ok"] is True
        assert status_data["primary_os"] == "VMS"
        assert status_data["https_port"] == 8455
        assert status_data["auth_providers"]["clerk"]["configured"] is True
        assert status_data["auth_providers"]["clerk"]["mode"] == "cloud"

        # 2. Verify GET / (VT220 & DECwindows X11 Workstation) and GET /signup (Clerk Cloud Live script tag)
        with urllib.request.urlopen(f"{base_url}/", context=ssl_ctx, timeout=5) as r:
            term_html = r.read().decode("utf-8")
            assert r.status == 200
            assert "SIGN UP ($10/MO)" in term_html
            assert "x11-canvas" in term_html

        with urllib.request.urlopen(f"{base_url}/signup", context=ssl_ctx, timeout=5) as r:
            signup_html = r.read().decode("utf-8")
            assert r.status == 200
            assert "Clerk Auth: Cloud Live" in signup_html
            assert "data-clerk-publishable-key=\"pk_test_" in signup_html

        # 3. Provision a $15/mo DEC Dual-System Cluster Pass (LCS_BUNDLE_15 -> BOTH RSTS/E & VAX/VMS)
        #    against the live dec-vms container (:8455) and verify cross-container provisioning to dec-rsts-e (:8411)
        signup_payload = json.dumps({
            "username": "LIVE_BNDL",
            "password": "VAX$BUNDLE15",
            "email": "live_bndl@dec.example.com",
            "plan": "LCS_BUNDLE_15",
            "target_os": "BOTH",
            "clerk_user_id": "user_clerk_live_bndl",
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/v1/signup",
            data=signup_payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=8) as r:
            assert r.status == 201
            created = json.loads(r.read().decode("utf-8"))
            assert created["ok"] is True
            assert created["username"] == "LIVE_BNDL"
            assert created["uic"].startswith("[200,")
            assert created["ppn"].startswith("[201,")
            assert created["quota"] == 100000
            assert "RSTS_E" in created["clerk_metadata"]["subscribed_os"]
            assert "VAX_VMS" in created["clerk_metadata"]["subscribed_os"]
            assigned_uic = created["uic"]

        # 4. Verify LIVE_BNDL exists in both dec-vms (:8455) and dec-rsts-e (:8411)
        with urllib.request.urlopen(f"{base_url}/api/v1/users", context=ssl_ctx, timeout=5) as r:
            vms_users = json.loads(r.read().decode("utf-8"))["users"]
            assert "LIVE_BNDL" in vms_users

        with urllib.request.urlopen("https://127.0.0.1:8411/api/v1/users", context=ssl_ctx, timeout=5) as r:
            rsts_users = json.loads(r.read().decode("utf-8"))["users"]
            rsts_names = {u.get("name") for u in rsts_users.values()}
            assert "LIVE_BNDL" in rsts_names

        # 5. Exercise Clerk subscription lifecycle webhooks on the running VAX/VMS container
        clerk_cancel = json.dumps({
            "type": "subscription.canceled",
            "data": {"id": "user_clerk_live_bndl", "public_metadata": {"dec_username": "LIVE_BNDL"}},
        }).encode("utf-8")
        req_cc = urllib.request.Request(
            f"{base_url}/api/v1/webhooks/clerk",
            data=clerk_cancel,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_cc, context=ssl_ctx, timeout=8) as r:
            cc_res = json.loads(r.read().decode("utf-8"))
            assert cc_res["action"] == "SUSPENDED"
            assert cc_res["account"]["status"] == "DISUSER"

        clerk_paid = json.dumps({
            "type": "invoice.paid",
            "data": {"id": "user_clerk_live_bndl", "status": "active", "public_metadata": {"dec_username": "LIVE_BNDL"}},
        }).encode("utf-8")
        req_cp = urllib.request.Request(
            f"{base_url}/api/v1/webhooks/clerk",
            data=clerk_paid,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_cp, context=ssl_ctx, timeout=8) as r:
            cp_res = json.loads(r.read().decode("utf-8"))
            assert cp_res["action"] == "REACTIVATED"
            assert cp_res["account"]["status"] == "ACTIVE"

        # 6. Connect via live WSS (wss://127.0.0.1:8455/ws) to the running container,
        #    log in with LIVE_BNDL, and run LOGIN.COM + HELLO.BAS
        raw_sock = socket.create_connection(("127.0.0.1", 8455), timeout=5)
        tls_sock = ssl_ctx.wrap_socket(raw_sock, server_hostname="127.0.0.1")
        ws_key = base64.b64encode(os.urandom(16)).decode("ascii")
        handshake = (
            "GET /ws?sid=live_bndl_sid HTTP/1.1\r\n"
            "Host: 127.0.0.1:8455\r\n"
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

        send_masked_ws("LIVE_BNDL\n")
        time.sleep(0.2)
        send_masked_ws("VAX$BUNDLE15\n")
        time.sleep(0.2)
        send_masked_ws("@SYS$LOGIN:LOGIN.COM\nRUN SYS$LOGIN:HELLO.BAS\nSHOW PROCESS\nLOGOUT/DISCONNECT\n")

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
        assert assigned_uic in decoded_out
        assert "HELLO LIVE_BNDL FROM LEGACY COMPUTING SYSTEMS VAX/VMS V5.5-2!" in decoded_out

