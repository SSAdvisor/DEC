import os
import sys
import time
import shutil
import tempfile
import unittest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from dcl.job_controller import JobController
from dcl.print_service import (
    DECPrintService,
    render_banner_text,
    generate_dec_burst_page,
    discover_network_printers,
    generate_config_from_discovery,
    find_default_config_file
)

class TestPrintService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.jc = JobController(base_dir=self.temp_dir)
        self.service = DECPrintService(job_controller=self.jc, poll_interval=0.1)

    def tearDown(self):
        self.service.stop_daemon()
        shutil.rmtree(self.temp_dir)

    def test_banner_generation(self):
        banner_sales = render_banner_text("SALES")
        self.assertIn("S", banner_sales)
        self.assertIn("A", banner_sales)
        lines = banner_sales.split("\n")
        self.assertEqual(len(lines), 5)

        entry = {
            "entry_id": 1,
            "job_name": "TESTJOB",
            "user_name": "USER1",
            "queue_name": "LP0:",
            "submit_time": "12-OCT-2026 12:00:00",
            "file_path": "/tmp/test.txt",
            "options_json": "{\"copies\": 1}"
        }
        cfg = {"dest_type": "SPOOL", "form_type": "NORMAL"}
        burst = generate_dec_burst_page(entry, cfg, "12-OCT-2026 12:00:01")
        self.assertIn("DEC RSTS/E V10.1", burst)
        self.assertIn("TESTJOB", burst)
        self.assertIn("USER1", burst)
        self.assertIn("\f", burst)

    def test_queue_configuration(self):
        self.jc.set_queue_config("LP0:", dest_type="FILE", dest_path=os.path.join(self.temp_dir, "lp0.out"), banner=0)
        cfg = self.jc.get_queue_config("LP0:")
        self.assertEqual(cfg["dest_type"], "FILE")
        self.assertEqual(cfg["dest_path"], os.path.join(self.temp_dir, "lp0.out"))
        self.assertEqual(cfg["banner"], 0)

    def test_process_job_spool_with_banner(self):
        test_file = os.path.join(self.temp_dir, "sample.txt")
        with open(test_file, "w") as f:
            f.write("SAMPLE REPORT DATA\nLINE 2\n")

        entry_id, job_name, q_name = self.jc.submit_print_job(
            file_path=test_file,
            queue_name="NETPRINT",
            job_name="RPT1",
            copies=1,
            delete_after=True
        )

        entry = self.service.process_one_print_job()
        self.assertIsNotNone(entry)
        self.assertEqual(entry["entry_id"], entry_id)
        self.assertEqual(entry["status"], "COMPLETED")

        # Source file should be deleted (/DELETE flag)
        self.assertFalse(os.path.exists(test_file))

        # Spool file should exist with banner
        spool_file = os.path.join(self.temp_dir, "spool", "NETPRINT", f"{entry_id:04d}_{job_name}.prt")
        self.assertTrue(os.path.exists(spool_file))
        with open(spool_file, "r") as f:
            content = f.read()
            self.assertIn("DEC RSTS/E V10.1", content)
            self.assertIn("SAMPLE REPORT DATA", content)

    def test_process_job_file_destination_no_banner(self):
        target_out = os.path.join(self.temp_dir, "printer_dest.out")
        self.jc.set_queue_config("SYS$PRINT", dest_type="FILE", dest_path=target_out, banner=0)

        test_file = os.path.join(self.temp_dir, "raw.txt")
        with open(test_file, "w") as f:
            f.write("DIRECT TO FILE CONTENT\n")

        entry_id, _, _ = self.jc.submit_print_job(
            file_path=test_file,
            queue_name="SYS$PRINT",
            job_name="DIRECT1",
            copies=1
        )

        entry = self.service.process_one_print_job()
        self.assertIsNotNone(entry)
        self.assertEqual(entry["status"], "COMPLETED")

        self.assertTrue(os.path.exists(target_out))
        with open(target_out, "r") as f:
            content = f.read()
            self.assertIn("DIRECT TO FILE CONTENT", content)
            self.assertNotIn("DEC RSTS/E V10.1", content)  # Banner was disabled

    def test_systemd_unit_generation(self):
        unit = self.service.generate_systemd_unit(user="myuser")
        self.assertIn("Description=DEC RSTS/E Print Queue Service", unit)
        self.assertIn("User=myuser", unit)
        self.assertIn("ExecStart=", unit)
        self.assertIn("Restart=always", unit)

    def test_daemon_lifecycle(self):
        self.assertFalse(self.jc.is_print_service_running())
        code, msg = self.service.start_daemon()
        self.assertEqual(code, 0)
        self.assertTrue(self.jc.is_print_service_running())

        # Test submit while daemon is running
        test_file = os.path.join(self.temp_dir, "async.txt")
        with open(test_file, "w") as f:
            f.write("ASYNC JOB CONTENT\n")

        entry_id, _, _ = self.jc.submit_print_job(
            file_path=test_file,
            queue_name="NETPRINT",
            job_name="ASYNC1"
        )

        # Wait for daemon to process
        for _ in range(30):
            time.sleep(0.1)
            e = self.jc.get_entry(entry_id)
            if e and e["status"] == "COMPLETED":
                break

        e = self.jc.get_entry(entry_id)
        self.assertEqual(e["status"], "COMPLETED")

        # Stop daemon
        code, msg = self.service.stop_daemon()
        self.assertEqual(code, 0)
        self.assertFalse(self.jc.is_print_service_running())

    def test_load_config_file(self):
        conf_path = os.path.join(self.temp_dir, "test-printq.conf")
        with open(conf_path, "w") as f:
            f.write("""
[SERVICE]
poll_interval = 0.25

[QUEUE:TESTNET]
status = OPEN
dest_type = SOCKET
dest_path = 192.168.1.50:9100
banner = 0
form_type = WIDE132

[QUEUE:TESTLP]
status = OPEN
dest_type = FILE
dest_path = /tmp/testlp.out
banner = 1
form_type = NORMAL
""")
        applied = self.service.load_config_file(conf_path)
        self.assertEqual(len(applied), 2)
        self.assertEqual(self.service.poll_interval, 0.25)

        net_cfg = self.jc.get_queue_config("TESTNET")
        self.assertEqual(net_cfg["dest_type"], "SOCKET")
        self.assertEqual(net_cfg["dest_path"], "192.168.1.50:9100")
        self.assertEqual(net_cfg["banner"], 0)
        self.assertEqual(net_cfg["form_type"], "WIDE132")

        lp_cfg = self.jc.get_queue_config("TESTLP")
        self.assertEqual(lp_cfg["dest_type"], "FILE")
        self.assertEqual(lp_cfg["dest_path"], "/tmp/testlp.out")
        self.assertEqual(lp_cfg["banner"], 1)

    def test_generate_config_from_discovery(self):
        mock_printers = [{
            "model": "HP LaserJet M209dw",
            "hostname": "NPI0ED18B.local",
            "ip": "192.168.40.203",
            "jetdirect_port": 9100,
            "cups_queue": "HP_LaserJet_M209dw_0ED18B"
        }]
        out_file = os.path.join(self.temp_dir, "gen.conf")
        text = generate_config_from_discovery(mock_printers, out_file)
        self.assertTrue(os.path.exists(out_file))
        self.assertIn("[QUEUE:NETPRINT]", text)
        self.assertIn("192.168.40.203:9100", text)
        self.assertIn("[QUEUE:HPLASER]", text)
        self.assertIn("lp -d HP_LaserJet_M209dw_0ED18B", text)

    def test_discover_network_printers(self):
        # Should return a list without crashing
        printers = discover_network_printers()
        self.assertIsInstance(printers, list)

if __name__ == "__main__":
    unittest.main()
