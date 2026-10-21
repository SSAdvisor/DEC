import os
import sys
import unittest
import tempfile
import shutil
import subprocess

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from dcl.dcl_parser import DCLParsedCommand
from dcl.job_controller import JobController
from dcl.dcl_interpreter import DCLInterpreter

class TestDCLParser(unittest.TestCase):
    def test_comment_and_blank(self):
        c1 = DCLParsedCommand("! This is a comment")
        self.assertTrue(c1.is_comment)
        c2 = DCLParsedCommand("$ ! Comment with dollar")
        self.assertTrue(c2.is_comment)
        c3 = DCLParsedCommand("   ")
        self.assertTrue(c3.is_comment)

    def test_label_and_command(self):
        c = DCLParsedCommand("START_LOOP: WRITE SYS$OUTPUT \"Processing...\"")
        self.assertEqual(c.label, "START_LOOP")
        self.assertEqual(c.verb, "WRITE")
        self.assertEqual(c.args, ["SYS$OUTPUT", "Processing..."])

    def test_qualifiers(self):
        c = DCLParsedCommand("PRINT tests/office/SALES.RPT /QUEUE=LP0: /COPIES=3 /DELETE")
        self.assertEqual(c.verb, "PRINT")
        self.assertEqual(c.args, ["tests/office/SALES.RPT"])
        self.assertEqual(c.qualifiers.get("QUEUE"), "LP0:")
        self.assertEqual(c.qualifiers.get("COPIES"), "3")
        self.assertTrue(c.qualifiers.get("DELETE"))

    def test_assignment(self):
        c = DCLParsedCommand("COUNT = 42")
        self.assertTrue(c.is_assignment)
        self.assertEqual(c.assign_var, "COUNT")
        self.assertEqual(c.assign_val, "42")

    def test_attached_qualifiers(self):
        c = DCLParsedCommand("PRINT/QUEUE=NETPRINT SALES.RPT/DELETE")
        self.assertEqual(c.verb, "PRINT")
        self.assertEqual(c.args, ["SALES.RPT"])
        self.assertEqual(c.qualifiers.get("QUEUE"), "NETPRINT")
        self.assertTrue(c.qualifiers.get("DELETE"))

        c2 = DCLParsedCommand("DELETE/ENTRY=42")
        self.assertEqual(c2.verb, "DELETE")
        self.assertEqual(c2.qualifiers.get("ENTRY"), "42")

class TestJobController(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.jc = JobController(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_queues_and_print_spool(self):
        # Create a test report file
        test_file = os.path.join(self.temp_dir, "test.rpt")
        with open(test_file, "w") as f:
            f.write("SAMPLE REPORT DATA\nLINE 2")

        entry_id, job_name, q_name = self.jc.submit_print_job(
            file_path=test_file,
            queue_name="LP0:",
            job_name="TEST_RPT",
            copies=2
        )
        self.assertEqual(q_name, "LP0:")
        
        # Verify job is PENDING
        e = self.jc.get_entry(entry_id)
        self.assertEqual(e['status'], 'PENDING')

        # Process print queue
        processed = self.jc.process_all_pending()
        self.assertEqual(processed, 1)

        # Verify job is COMPLETED
        e = self.jc.get_entry(entry_id)
        self.assertEqual(e['status'], 'COMPLETED')

        # Check spool file exists
        spool_path = os.path.join(self.temp_dir, "spool", "LP0_", f"{entry_id:04d}_{job_name}.prt")
        self.assertTrue(os.path.exists(spool_path))
        with open(spool_path, 'r') as f:
            content = f.read()
            self.assertIn("SAMPLE REPORT DATA", content)
            self.assertIn("Copies: 2", content)

    def test_batch_job_execution(self):
        # Create a test .com procedure
        com_file = os.path.join(self.temp_dir, "test.com")
        with open(com_file, "w") as f:
            f.write("$ WRITE SYS$OUTPUT \"HELLO FROM BATCH\"\n$ EXIT\n")

        entry_id, job_name, q_name = self.jc.submit_batch_job(
            file_path=com_file,
            queue_name="SYS$BATCH"
        )
        
        def dummy_runner(fpath):
            return 0, "HELLO FROM BATCH"

        self.jc.process_all_pending(interpreter_runner=dummy_runner)
        e = self.jc.get_entry(entry_id)
        self.assertEqual(e['status'], 'COMPLETED')
        
        # Check log file
        self.assertTrue(os.path.exists(e['log_file']))
        with open(e['log_file'], 'r') as f:
            log_txt = f.read()
            self.assertIn("HELLO FROM BATCH", log_txt)

class TestDCLInterpreter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.jc = JobController(base_dir=self.temp_dir)
        self.interp = DCLInterpreter(repo_root=repo_root, job_controller=self.jc)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_system_and_show(self):
        code, out = self.interp.execute_line("SHOW SYSTEM")
        self.assertEqual(code, 0)
        self.assertIn("RSTS/E", out)

        code, out = self.interp.execute_line("SHOW QUEUE")
        self.assertEqual(code, 0)
        self.assertIn("SYS$BATCH", out)

    def test_symbol_assignment_and_write(self):
        self.interp.execute_line("NAME = \"DEC-BASIC\"")
        code, out = self.interp.execute_line("WRITE SYS$OUTPUT Welcome to 'NAME'")
        self.assertEqual(code, 0)
        self.assertEqual(out, "Welcome to DEC-BASIC")

    def test_command_procedure_execution(self):
        com_file = os.path.join(self.temp_dir, "calc.com")
        with open(com_file, "w") as f:
            f.write("""$ ! Test procedure with IF and GOTO
$ COUNT = 1
$ LOOP:
$ WRITE SYS$OUTPUT "Iteration 'COUNT'"
$ IF COUNT = 1 THEN GOTO SKIP
$ WRITE SYS$OUTPUT "Should not appear"
$ SKIP:
$ WRITE SYS$OUTPUT "Done"
$ EXIT
""")
        code, out = self.interp.execute_procedure(com_file)
        self.assertEqual(code, 0)
        self.assertIn("Iteration 1", out)
        self.assertIn("Done", out)
        self.assertNotIn("Should not appear", out)

    def test_show_entry(self):
        test_file = os.path.join(self.temp_dir, "report.txt")
        with open(test_file, "w") as f:
            f.write("SAMPLE DATA")
        self.interp.execute_line(f"PRINT/QUEUE=NETPRINT {test_file}")
        code, out = self.interp.execute_line("SHOW ENTRY")
        self.assertEqual(code, 0)
        self.assertIn("NETPRINT", out)
        self.assertIn("COMPLETED", out)

        code, out = self.interp.execute_line("SHOW ENTRY 1")
        self.assertEqual(code, 0)
        self.assertIn("NETPRINT", out)
        self.assertIn("report.txt", out)

    def test_salesrpt_dcl_execution(self):
        sales_dcl = os.path.join(repo_root, "tests", "office", "salesrpt.dcl")
        code, out = self.interp.execute_procedure(sales_dcl)
        self.assertEqual(code, 0)
        self.assertIn("NETPRINT", out)
        self.assertIn("COMPLETED", out)

    def test_account_management_lifecycle(self):
        code, out = self.interp.execute_line("SHOW ACCOUNT")
        self.assertEqual(code, 0)
        self.assertIn("[1,2]", out)
        self.assertIn("SYSTEM", out)

        code, out = self.interp.execute_line("CREATE/ACCOUNT [150,10] /NAME=ENGR /PASSWORD=VAX11 /QUOTA=8000 /PRIVILEGES")
        self.assertEqual(code, 0)
        self.assertIn("created", out)

        code, out = self.interp.execute_line("SHOW ACCOUNT [150,10] /FULL")
        self.assertEqual(code, 0)
        self.assertIn("ENGR", out)
        self.assertIn("8000", out)
        self.assertIn("PRIV", out)

        code, out = self.interp.execute_line("MODIFY/ACCOUNT [150,10] /QUOTA=12000 /NOPRIVILEGES")
        self.assertEqual(code, 0)
        self.assertIn("updated", out)

        code, out = self.interp.execute_line("SET PASSWORD [150,10] /PASSWORD=NEWPASS99")
        self.assertEqual(code, 0)
        self.assertIn("password updated", out)

        code, out = self.interp.execute_line("DELETE/ACCOUNT [150,10]")
        self.assertEqual(code, 0)
        self.assertIn("deleted", out)

        code, out = self.interp.execute_line("DELETE/ACCOUNT [1,2]")
        self.assertNotEqual(code, 0)
        self.assertIn("cannot delete protected system account", out)

class TestCompiledDCL(unittest.TestCase):
    def setUp(self):
        self.dcl_bin = os.path.join(repo_root, "dcl", "dcl")
        if not (os.path.exists(self.dcl_bin) and os.access(self.dcl_bin, os.X_OK)):
            self.skipTest("Compiled DCL binary not found at " + self.dcl_bin)

    def test_show_system(self):
        res = subprocess.run([self.dcl_bin, "SHOW", "SYSTEM"], capture_output=True, text=True, cwd=repo_root)
        self.assertEqual(res.returncode, 0)
        self.assertIn("RSTS/E", res.stdout)
        self.assertIn("Host Platform", res.stdout)
        self.assertIn("Print/Batch Services (PBS) Active", res.stdout)

    def test_show_queue(self):
        res = subprocess.run([self.dcl_bin, "SHOW", "QUEUE"], capture_output=True, text=True, cwd=repo_root)
        self.assertEqual(res.returncode, 0)
        self.assertIn("SYS$BATCH", res.stdout)
        self.assertIn("LP0:", res.stdout)

    def test_help(self):
        res = subprocess.run([self.dcl_bin, "HELP"], capture_output=True, text=True, cwd=repo_root)
        self.assertEqual(res.returncode, 0)
        self.assertIn("DIGITAL Command Language", res.stdout)
        self.assertIn("SUBMIT", res.stdout)
        self.assertIn("PRINT", res.stdout)

    def test_command_procedure(self):
        bas_file = os.path.join(repo_root, "tests", "office", "salesrpt.bas")
        obj_file = os.path.join(repo_root, "tests", "office", "salesrpt.obj")
        exe_file = os.path.join(repo_root, "tests", "office", "salesrpt")
        if not os.path.exists(exe_file):
            subprocess.run([sys.executable, os.path.join(repo_root, "compiler", "basicc.py"), bas_file, "-o", obj_file], check=True, cwd=repo_root)
            subprocess.run([sys.executable, os.path.join(repo_root, "compiler", "basiclink.py"), obj_file, "-o", exe_file], check=True, cwd=repo_root)

        proc = os.path.join(repo_root, "tests", "office", "salesrpt.dcl")
        res = subprocess.run([self.dcl_bin, f"@{proc}"], capture_output=True, text=True, cwd=repo_root)
        self.assertEqual(res.returncode, 0)
        self.assertIn("submitted to queue NETPRINT", res.stdout)

    def test_sales_batch_procedure(self):
        batch_com = os.path.join(repo_root, "tests", "office", "sales_batch.com")
        res = subprocess.run([self.dcl_bin, f"@{batch_com}"], capture_output=True, text=True, cwd=repo_root)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Sales Inventory Report Batch Job Finished Successfully", res.stdout)

    def test_interactive_session_pipe(self):
        res = subprocess.run(
            [self.dcl_bin],
            input='WRITE SYS$OUTPUT "HELLO COMPILED DCL"\nEXIT\n',
            capture_output=True,
            text=True,
            cwd=repo_root
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("HELLO COMPILED DCL", res.stdout)

    def test_dcl_py_wrapper(self):
        py_dcl = os.path.join(repo_root, "dcl.py")
        res = subprocess.run([sys.executable, py_dcl, "SHOW", "SYSTEM"], capture_output=True, text=True, cwd=repo_root)
        self.assertEqual(res.returncode, 0)
        self.assertIn("RSTS/E", res.stdout)

    def test_compiled_dcl_account_commands(self):
        res = subprocess.run(
            [self.dcl_bin],
            input=(
                "CREATE/ACCOUNT [160,5] /NAME=FINANCE /QUOTA=6000 /PASSWORD=LEDGER1\n"
                "SHOW ACCOUNT [160,5] /FULL\n"
                "SET ACCOUNT [160,5] /QUOTA=9000\n"
                "DELETE/ACCOUNT [160,5]\n"
                "EXIT\n"
            ),
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("FINANCE", res.stdout)
        self.assertIn("created", res.stdout)
        self.assertIn("updated", res.stdout)
        self.assertIn("deleted", res.stdout)

if __name__ == "__main__":
    unittest.main()
