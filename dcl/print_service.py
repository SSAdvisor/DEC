#!/usr/bin/env python3
"""
DEC RSTS/E Print Queue Service & Symbiont Daemon (dec-printq)
Part of the DEC BASIC-PLUS-2 / RSTS/E PBS (Print/Batch Services) subsystem.

Features:
- Background continuous queue processing daemon
- Support for systemd service management (Type=simple)
- DEC Line Printer Burst/Banner page generation with ASCII block letters
- Multi-queue management (SYS$PRINT, LP0:, NETPRINT, custom queues)
- Configurable destinations: SPOOL (default), FILE/DEVICE, COMMAND/PIPE, TCP SOCKET
- Signal handling (SIGTERM, SIGINT, SIGHUP for reload)
- PID file management in .dcl/run/dec-printq.pid
- Full CLI for start, stop, restart, status, run, configure, and systemd-unit generation
"""

import os
import sys
import re
import time
import json
import signal
import socket
import logging
import argparse
import subprocess
import configparser
from datetime import datetime

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from dcl.job_controller import JobController

# 5x5 ASCII block font for authentic DEC banner/burst pages
BLOCK_FONT = {
    'A': [" AAA ", "A   A", "AAAAA", "A   A", "A   A"],
    'B': ["BBBB ", "B   B", "BBBB ", "B   B", "BBBB "],
    'C': [" CCCC", "C    ", "C    ", "C    ", " CCCC"],
    'D': ["DDDD ", "D   D", "D   D", "D   D", "DDDD "],
    'E': ["EEEEE", "E    ", "EEEE ", "E    ", "EEEEE"],
    'F': ["FFFFF", "F    ", "FFFF ", "F    ", "F    "],
    'G': [" GGGG", "G    ", "G  GG", "G   G", " GGGG"],
    'H': ["H   H", "H   H", "HHHHH", "H   H", "H   H"],
    'I': [" III ", "  I  ", "  I  ", "  I  ", " III "],
    'J': ["  JJJ", "    J", "    J", "J   J", " JJJ "],
    'K': ["K   K", "K  K ", "KKK  ", "K  K ", "K   K"],
    'L': ["L    ", "L    ", "L    ", "L    ", "LLLLL"],
    'M': ["M   M", "MM MM", "M M M", "M   M", "M   M"],
    'N': ["N   N", "NN  N", "N N N", "N  NN", "N   N"],
    'O': [" OOO ", "O   O", "O   O", "O   O", " OOO "],
    'P': ["PPPP ", "P   P", "PPPP ", "P    ", "P    "],
    'Q': [" QQQ ", "Q   Q", "Q   Q", "Q  Q ", " QQ Q"],
    'R': ["RRRR ", "R   R", "RRRR ", "R  R ", "R   R"],
    'S': [" SSSS", "S    ", " SSS ", "    S", "SSSS "],
    'T': ["TTTTT", "  T  ", "  T  ", "  T  ", "  T  "],
    'U': ["U   U", "U   U", "U   U", "U   U", " UUU "],
    'V': ["V   V", "V   V", "V   V", " V V ", "  V  "],
    'W': ["W   W", "W   W", "W W W", "WW WW", "W   W"],
    'X': ["X   X", " X X ", "  X  ", " X X ", "X   X"],
    'Y': ["Y   Y", " Y Y ", "  Y  ", "  Y  ", "  Y  "],
    'Z': ["ZZZZZ", "   Z ", "  Z  ", " Z   ", "ZZZZZ"],
    '0': [" 000 ", "0  00", "0 0 0", "00  0", " 000 "],
    '1': [" 11  ", "  1  ", "  1  ", "  1  ", " 111 "],
    '2': [" 222 ", "2   2", "   2 ", "  2  ", "22222"],
    '3': ["3333 ", "    3", " 333 ", "    3", "3333 "],
    '4': ["4  4 ", "4  4 ", "44444", "   4 ", "   4 "],
    '5': ["55555", "5    ", "5555 ", "    5", "5555 "],
    '6': [" 666 ", "6    ", "6666 ", "6   6", " 666 "],
    '7': ["77777", "    7", "   7 ", "  7  ", "  7  "],
    '8': [" 888 ", "8   8", " 888 ", "8   8", " 888 "],
    '9': [" 999 ", "9   9", " 9999", "    9", " 999 "],
    ' ': ["     ", "     ", "     ", "     ", "     "],
    '-': ["     ", "     ", " --- ", "     ", "     "],
    '_': ["     ", "     ", "     ", "     ", "_____"],
    '.': ["     ", "     ", "     ", "     ", "  .  "],
    ':': ["     ", "  :  ", "     ", "  :  ", "     "]
}

def render_banner_text(text: str) -> str:
    """Renders text in 5-line DEC block letters."""
    clean = text.upper()
    lines = ["", "", "", "", ""]
    for ch in clean:
        glyph = BLOCK_FONT.get(ch, BLOCK_FONT[' '])
        for row in range(5):
            lines[row] += glyph[row] + "  "
    return "\n".join(line.rstrip() for line in lines)

def generate_dec_burst_page(entry: dict, queue_config: dict, print_time: str) -> str:
    """Generates an authentic DEC RSTS/E PBS Line Printer Burst/Banner Page."""
    q_name = entry.get('queue_name', 'SYS$PRINT')
    job_name = entry.get('job_name', 'JOB')
    user_name = entry.get('user_name', 'SYSTEM')
    entry_id = entry.get('entry_id', 0)
    submit_time = entry.get('submit_time', '')
    opts = json.loads(entry.get('options_json') or "{}")
    copies = opts.get('copies', 1)
    file_short = os.path.basename(entry.get('file_path', ''))
    form_type = queue_config.get('form_type', 'NORMAL')

    border = "=" * 80
    sub_border = "-" * 80
    job_block = render_banner_text(job_name[:10])

    burst = [
        border,
        "                                DEC RSTS/E V10.1",
        "                         PRINT SERVICES (PBS) SYMBIONT",
        border,
        "",
        job_block,
        "",
        sub_border,
        "JOB IDENTIFICATION:",
        f"  Job Name:       {job_name:<16}  Entry Number:  {entry_id}",
        f"  User Name:      {user_name:<16}  Queue:         {q_name}",
        f"  Submitted:      {submit_time:<16}  Printed:       {print_time}",
        f"  Copies:         {copies:<16}  Form Type:     {form_type}",
        f"  Input File:     {file_short}",
        border,
        "\f"  # Form feed separating banner from job body
    ]
    return "\n".join(burst)


def find_default_config_file(base_dir=None) -> str | None:
    """Finds default dec-printq.conf control file if present."""
    candidates = []
    if base_dir:
        candidates.append(os.path.join(base_dir, "dec-printq.conf"))
    candidates.extend([
        os.path.join(os.getcwd(), "dec-printq.conf"),
        os.path.join(repo_root, "dec-printq.conf"),
        os.path.join(repo_root, ".dcl", "dec-printq.conf"),
        "/etc/dec-printq.conf"
    ])
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None


def discover_network_printers() -> list[dict]:
    """Discovers network and local printers using CUPS, IPP, mDNS/Avahi, and port probing."""
    discovered = {}

    # 1. mDNS / Avahi discovery
    try:
        res = subprocess.run(["avahi-browse", "-rt", "_ipp._tcp"], capture_output=True, text=True, timeout=4)
        current = {}
        for line in res.stdout.splitlines():
            sline = line.strip()
            if sline.startswith("=") and "Internet Printer" in sline:
                current = {"protocol": "IPP"}
            elif "hostname = [" in sline:
                m = re.search(r"\[(.*?)\]", sline)
                if m:
                    current["hostname"] = m.group(1).rstrip(".")
            elif "address = [" in sline:
                m = re.search(r"\[(.*?)\]", sline)
                if m:
                    current["ip"] = m.group(1)
            elif "port = [" in sline:
                m = re.search(r"\[(.*?)\]", sline)
                if m:
                    current["port"] = int(m.group(1))
            elif "txt = [" in sline:
                m = re.search(r"product=\((.*?)\)", sline) or re.search(r"\"ty=(.*?)(?:\"|\s)", sline) or re.search(r"\"usb_MDL=(.*?)(?:\"|\s)", sline)
                if m:
                    current["model"] = m.group(1).strip('"()')
                key = current.get("ip") or current.get("hostname")
                if key and key not in discovered:
                    discovered[key] = dict(current)
    except Exception:
        pass

    # 2. ippfind
    try:
        res = subprocess.run(["ippfind"], capture_output=True, text=True, timeout=4)
        for line in res.stdout.splitlines():
            uri = line.strip()
            if uri and uri.startswith("ipp://"):
                host_part = uri.split("ipp://", 1)[1].split("/", 1)[0]
                host = host_part.split(":")[0]
                key = host
                if key not in discovered:
                    discovered[key] = {"hostname": host, "ipp_uri": uri, "protocol": "IPP"}
                else:
                    discovered[key]["ipp_uri"] = uri
    except Exception:
        pass

    # 3. Resolve hostnames and test JetDirect port 9100
    for key, data in list(discovered.items()):
        host = data.get("hostname") or data.get("ip")
        ip = data.get("ip")
        if not ip and host:
            try:
                ip = socket.gethostbyname(host)
                data["ip"] = ip
            except Exception:
                pass

        probe_target = ip or host
        if probe_target:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.0)
                    if s.connect_ex((probe_target, 9100)) == 0:
                        data["jetdirect_port"] = 9100
            except Exception:
                pass

    # 4. CUPS discovery via lpstat
    try:
        res = subprocess.run(["lpstat", "-p", "-v"], capture_output=True, text=True, timeout=4)
        cups_printers = {}
        for line in res.stdout.splitlines():
            if line.startswith("printer "):
                parts = line.split()
                pname = parts[1]
                cups_printers[pname] = {"cups_queue": pname}
            elif line.startswith("device for "):
                parts = line[11:].split(":", 1)
                pname = parts[0].strip()
                uri = parts[1].strip() if len(parts) > 1 else ""
                if pname in cups_printers:
                    cups_printers[pname]["uri"] = uri

        for pname, cdata in cups_printers.items():
            matched = False
            for k, pdata in discovered.items():
                h = pdata.get("hostname", "")
                ip = pdata.get("ip", "")
                h_short = h.split(".")[0] if h else ""
                pname_clean = pname.split("@")[0].lower()
                if (h_short and (h_short.lower() in pname.lower() or pname_clean in h_short.lower())) or \
                   (ip and ip in cdata.get("uri", "")) or \
                   (pdata.get("model") and any(w.lower() in pname.lower() for w in pdata["model"].split() if len(w) > 3)):
                    if not pdata.get("cups_queue") or "@" in pdata.get("cups_queue", ""):
                        pdata["cups_queue"] = pname.split("@")[0]
                    matched = True
                    break
            if not matched and not pname.endswith(".local") and "@" not in pname:
                discovered[f"cups_{pname}"] = {
                    "model": pname.replace("_", " "),
                    "cups_queue": pname,
                    "protocol": "CUPS",
                    "uri": cdata.get("uri", "")
                }
    except Exception:
        pass

    # Consolidate duplicate records that share IP or hostname
    consolidated = {}
    for k, data in discovered.items():
        ip = data.get("ip")
        key = ip if ip else data.get("hostname", k)
        if key in consolidated:
            target = consolidated[key]
            for f in ["model", "hostname", "ip", "port", "jetdirect_port", "cups_queue", "ipp_uri"]:
                if not target.get(f) and data.get(f):
                    target[f] = data[f]
                elif f == "model" and target.get("model") and len(data.get("model", "")) > len(target.get("model", "")):
                    target["model"] = data["model"]
        else:
            consolidated[key] = dict(data)

    return list(consolidated.values())


def generate_config_from_discovery(printers: list[dict], output_file: str = None) -> str:
    """Generates a complete dec-printq.conf control file from discovered printers."""
    lines = [
        "# ==============================================================================",
        "# DEC RSTS/E Print Queue Service (dec-printq) Control File",
        "# Auto-generated by dec-printq discovery",
        "# ==============================================================================",
        "",
        "[SERVICE]",
        "poll_interval = 0.5",
        "banner_default = 1",
        "",
        "# ==============================================================================",
        "# Configured Queues",
        "# ==============================================================================",
        ""
    ]

    has_netprint = False
    for p in printers:
        ip = p.get("ip") or p.get("hostname")
        model = p.get("model", "Network Printer")
        jd_port = p.get("jetdirect_port")
        cups_q = p.get("cups_queue")

        if jd_port and ip and not has_netprint:
            lines.extend([
                f"# Network Printer: {model} (Direct TCP AppSocket Port {jd_port})",
                "[QUEUE:NETPRINT]",
                f"description = {model} via Direct TCP AppSocket",
                "status = OPEN",
                "dest_type = SOCKET",
                f"dest_path = {ip}:{jd_port}",
                "banner = 1",
                "form_type = NORMAL",
                ""
            ])
            has_netprint = True

        if cups_q:
            q_label = "HPLASER" if "hp" in cups_q.lower() else "CUPSPRINT"
            lines.extend([
                f"# Network Printer: {model} via CUPS Native Filter",
                f"[QUEUE:{q_label}]",
                f"description = {model} via CUPS Host Filter",
                "status = OPEN",
                "dest_type = COMMAND",
                f"dest_path = lp -d {cups_q}",
                "banner = 1",
                "form_type = NORMAL",
                ""
            ])

    if not has_netprint:
        lines.extend([
            "# Network Printer (Fallback placeholder)",
            "[QUEUE:NETPRINT]",
            "description = Network Printer via TCP Socket",
            "status = OPEN",
            "dest_type = SOCKET",
            "dest_path = 127.0.0.1:9100",
            "banner = 1",
            "form_type = NORMAL",
            ""
        ])

    lines.extend([
        "# Default DEC System Spooler",
        "[QUEUE:SYS$PRINT]",
        "description = Default System Print Spooler",
        "status = OPEN",
        "dest_type = SPOOL",
        "dest_path = ",
        "banner = 1",
        "form_type = NORMAL",
        "",
        "# Simulated / Physical Line Printer 0",
        "[QUEUE:LP0:]",
        "description = DEC Line Printer 0",
        "status = OPEN",
        "dest_type = FILE",
        "dest_path = .dcl/spool/lp0_simulated.prt",
        "banner = 1",
        "form_type = NORMAL",
        ""
    ])

    text = "\n".join(lines)
    if output_file:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(text)
    return text


class DECPrintService:
    def __init__(self, job_controller=None, poll_interval=0.5, config_file=None):
        self.job_controller = job_controller or JobController()
        self.poll_interval = poll_interval
        self.config_file = config_file or find_default_config_file(self.job_controller.base_dir if self.job_controller else None)
        self.running = False
        
        self.log_file = os.path.join(self.job_controller.log_dir, "dec-printq.log")
        self.pid_file = self.job_controller.pid_file
        
        self.logger = logging.getLogger("DECPrintService")
        self._setup_logging()

    def load_config_file(self, config_path: str = None) -> list[str]:
        """Loads queue definitions and service settings from an INI-style control file."""
        target = config_path or self.config_file
        if not target:
            target = find_default_config_file(self.job_controller.base_dir if self.job_controller else None)

        if not target or not os.path.isfile(target):
            return []

        self.config_file = os.path.abspath(target)
        cfg = configparser.ConfigParser()
        cfg.read(self.config_file)

        applied = []
        if "SERVICE" in cfg:
            s_sec = cfg["SERVICE"]
            if "poll_interval" in s_sec:
                try:
                    self.poll_interval = float(s_sec["poll_interval"])
                except ValueError:
                    pass

        for section in cfg.sections():
            if section.startswith("QUEUE:"):
                q_name = section[6:].strip()
                sec = cfg[section]
                status = sec.get("status", "OPEN").upper()
                dest_type = sec.get("dest_type", "SPOOL").upper()
                dest_path = sec.get("dest_path", "").strip()
                banner = int(sec.get("banner", "1"))
                form_type = sec.get("form_type", "NORMAL").strip()

                if status == "OPEN":
                    self.job_controller.start_queue(q_name)
                else:
                    self.job_controller.stop_queue(q_name)

                self.job_controller.set_queue_config(
                    queue_name=q_name,
                    dest_type=dest_type,
                    dest_path=dest_path,
                    banner=banner,
                    form_type=form_type
                )
                applied.append(f"Queue {q_name} -> {dest_type} ({dest_path or 'spool dir'}, status={status})")

        if hasattr(self, "logger"):
            self.logger.info(f"Loaded control file {self.config_file} ({len(applied)} queues updated)")
        return applied

    def _setup_logging(self, foreground=False):
        self.logger.setLevel(logging.INFO)
        for h in list(self.logger.handlers):
            h.close()
        self.logger.handlers.clear()
        
        formatter = logging.Formatter("[%(asctime)s] [PBS-SYMBIONT] %(levelname)s: %(message)s",
                                      datefmt="%d-%b-%Y %H:%M:%S")
        
        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        if foreground:
            sh = logging.StreamHandler(sys.stdout)
            sh.setFormatter(formatter)
            self.logger.addHandler(sh)

    def write_pid(self):
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def clear_pid(self):
        if os.path.exists(self.pid_file):
            try:
                os.remove(self.pid_file)
            except OSError:
                pass

    def dispatch_output(self, queue_name: str, entry: dict, content: str, q_config: dict) -> bool:
        """Dispatches spooled text according to destination configuration."""
        dest_type = q_config.get("dest_type", "SPOOL").upper()
        dest_path = q_config.get("dest_path", "").strip()
        
        entry_id = entry['entry_id']
        job_name = entry['job_name']
        
        # 1. Standard SPOOL destination: .dcl/spool/<QUEUE>/<entry_id>_<job>.prt
        if dest_type == "SPOOL" or not dest_path:
            q_dir = os.path.join(self.job_controller.spool_dir, queue_name.replace(':', '_').replace('$', '_'))
            os.makedirs(q_dir, exist_ok=True)
            target = os.path.join(q_dir, f"{entry_id:04d}_{job_name}.prt")
            with open(target, 'w') as f:
                f.write(content)
            self.logger.info(f"Entry {entry_id} spooled to file: {target}")
            return True

        # 2. FILE / DEVICE destination (e.g. /dev/lp0 or a simulated printer file)
        elif dest_type in ["FILE", "DEVICE"]:
            dest_dir = os.path.dirname(dest_path)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            with open(dest_path, 'a') as f:
                f.write(content)
            self.logger.info(f"Entry {entry_id} sent to device/file: {dest_path}")
            return True

        # 3. COMMAND / PIPE destination (e.g. lpr -P queue)
        elif dest_type in ["COMMAND", "PIPE"]:
            res = subprocess.run(dest_path, input=content, shell=True, text=True, capture_output=True)
            if res.returncode == 0:
                self.logger.info(f"Entry {entry_id} piped to command: {dest_path}")
                return True
            else:
                self.logger.error(f"Entry {entry_id} pipe failed: {res.stderr.strip()}")
                return False

        # 4. TCP SOCKET (RAW 9100 network printing)
        elif dest_type in ["SOCKET", "TCP", "NET"]:
            parts = dest_path.split(':')
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 9100
            with socket.create_connection((host, port), timeout=10) as s:
                s.sendall(content.encode('utf-8', errors='replace'))
            self.logger.info(f"Entry {entry_id} transmitted via TCP to {host}:{port}")
            return True

        else:
            self.logger.error(f"Unknown destination type '{dest_type}' for queue {queue_name}")
            return False

    def process_one_print_job(self) -> dict:
        """Finds the next pending job in an open print queue and processes it."""
        with self.job_controller.lock:
            conn = self.job_controller._get_connection()
            c = conn.cursor()
            c.execute("""
            SELECT e.* FROM entries e
            JOIN queues q ON e.queue_name = q.name
            WHERE q.type = 'PRINT' AND q.status = 'OPEN' AND e.status = 'PENDING'
            ORDER BY e.entry_id ASC LIMIT 1
            """)
            row = c.fetchone()
            if not row:
                conn.close()
                return None
            
            entry = dict(row)
            start_time = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
            c.execute("UPDATE entries SET status = 'EXECUTING', start_time = ? WHERE entry_id = ?",
                      (start_time, entry['entry_id']))
            conn.commit()
            conn.close()

        entry_id = entry['entry_id']
        job_name = entry['job_name']
        q_name = entry['queue_name']
        file_path = entry['file_path']
        
        self.logger.info(f"Processing Entry {entry_id} [{job_name}] for queue {q_name}")
        
        opts = json.loads(entry['options_json'] or "{}")
        copies = int(opts.get("copies", 1))
        delete_after = bool(opts.get("delete_after", False))
        
        q_config = self.job_controller.get_queue_config(q_name)
        banner_enabled = bool(q_config.get("banner", 1))
        
        success = False
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file {file_path} not found")
                
            with open(file_path, 'r', errors='ignore') as f:
                body_content = f.read()

            output_chunks = []
            
            # 1. Burst / Banner page
            if banner_enabled:
                burst_page = generate_dec_burst_page(entry, q_config, start_time)
                output_chunks.append(burst_page)

            # 2. Job body (repeated per copy with form feeds)
            for c_idx in range(copies):
                if c_idx > 0:
                    output_chunks.append("\n\f\n")
                output_chunks.append(body_content)
                
            output_chunks.append("\n" + ("-" * 60) + "\n--- End of Spool Output ---\n")
            full_spool_text = "".join(output_chunks)
            
            # 3. Dispatch
            dispatch_ok = self.dispatch_output(q_name, entry, full_spool_text, q_config)
            if dispatch_ok:
                if delete_after and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        self.logger.info(f"Deleted source file {file_path} (/DELETE flag)")
                    except OSError as e:
                        self.logger.warning(f"Failed to delete source file: {e}")
                success = True

        except Exception as e:
            self.logger.error(f"Error processing entry {entry_id}: {e}")
            success = False

        end_time = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        final_status = 'COMPLETED' if success else 'ABORTED'
        
        with self.job_controller.lock:
            conn = self.job_controller._get_connection()
            c = conn.cursor()
            c.execute("UPDATE entries SET status = ?, end_time = ? WHERE entry_id = ?",
                      (final_status, end_time, entry_id))
            conn.commit()
            conn.close()

        entry['status'] = final_status
        entry['end_time'] = end_time
        self.logger.info(f"Entry {entry_id} finished with status: {final_status}")
        return entry

    def run_foreground(self):
        """Runs the queue service in foreground mode (for systemd or interactive testing)."""
        self._setup_logging(foreground=True)
        self.running = True
        
        # Load control file if present
        if self.config_file:
            self.load_config_file(self.config_file)

        def handle_signal(sig, frame):
            sig_name = signal.Signals(sig).name
            self.logger.info(f"Received signal {sig_name}, initiating graceful shutdown...")
            self.running = False

        def handle_hup(sig, frame):
            self.logger.info("SIGHUP received: reloading control file and refreshing queues...")
            if self.config_file:
                self.load_config_file(self.config_file)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, handle_hup)

        self.write_pid()
        self.logger.info(f"DEC RSTS/E Print Queue Service (PBS Symbiont) started (PID {os.getpid()})")
        if self.config_file:
            self.logger.info(f"Active control file: {self.config_file}")
        
        queues = self.job_controller.list_queues()
        print_queues = [q['name'] for q in queues if q['type'] == 'PRINT' and q['status'] == 'OPEN']
        self.logger.info(f"Monitored active print queues: {', '.join(print_queues)}")

        try:
            while self.running:
                processed = self.process_one_print_job()
                if not processed:
                    time.sleep(self.poll_interval)
        finally:
            self.clear_pid()
            self.logger.info("DEC RSTS/E Print Queue Service shutdown complete.")

    def start_daemon(self) -> tuple[int, str]:
        """Starts the print queue service as a detached background daemon."""
        if self.job_controller.is_print_service_running():
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
            return 0, f"DEC Print Queue Service is already running (PID {pid})."

        script_path = os.path.abspath(__file__)
        cmd = [sys.executable, script_path, "run"]
        if self.job_controller.base_dir:
            cmd.extend(["--base-dir", self.job_controller.base_dir])
        if self.config_file:
            cmd.extend(["--config", self.config_file])

        proc = subprocess.Popen(
            cmd,
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

        # Wait up to 2 seconds for PID file creation
        for _ in range(20):
            time.sleep(0.1)
            if self.job_controller.is_print_service_running():
                return 0, f"DEC Print Queue Service started successfully (PID {proc.pid})."

        return 1, "%PBS-E-STARTERR, failed to confirm print service startup."

    def stop_daemon(self) -> tuple[int, str]:
        """Stops the running daemon gracefully."""
        if not os.path.exists(self.pid_file):
            return 0, "DEC Print Queue Service is not running."

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
        except (ValueError, OSError):
            self.clear_pid()
            return 0, "Stale PID file cleared; service was not running."

        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            self.clear_pid()
            return 0, "Process already terminated; cleared PID file."
        except PermissionError as e:
            return 1, f"%PBS-E-PERM, cannot send signal to PID {pid}: {e}"

        # Wait up to 5 seconds for clean exit
        for _ in range(50):
            time.sleep(0.1)
            try:
                os.kill(pid, 0)
            except OSError:
                self.clear_pid()
                return 0, f"DEC Print Queue Service (PID {pid}) stopped successfully."

        # If still running, force kill
        try:
            os.kill(pid, signal.SIGKILL)
            self.clear_pid()
            return 0, f"DEC Print Queue Service (PID {pid}) forcibly terminated."
        except OSError:
            self.clear_pid()
            return 0, f"DEC Print Queue Service (PID {pid}) stopped."

    def get_status_text(self) -> str:
        """Returns human-readable status of the print queue service."""
        is_running = self.job_controller.is_print_service_running()
        out = []
        out.append("DEC RSTS/E Print Queue Service (PBS Symbiont) Status")
        out.append("====================================================")
        
        if is_running:
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
            out.append(f"Service State:  ACTIVE / RUNNING (PID {pid})")
        else:
            out.append("Service State:  INACTIVE / STOPPED")
            
        out.append(f"Control File:   {self.config_file or '(none)'}")
        out.append(f"Log File:       {self.log_file}")
        out.append(f"Spool Dir:      {self.job_controller.spool_dir}")
        out.append("")
        
        out.append("Configured Print Queues:")
        out.append("Queue       Status    Dest Type  Destination           Banner  Form")
        out.append("----------  --------  ---------  --------------------  ------  -------")
        queues = self.job_controller.list_queues()
        for q in queues:
            if q['type'] == 'PRINT':
                q_name = q['name']
                q_status = q['status']
                cfg = self.job_controller.get_queue_config(q_name)
                dtype = cfg.get('dest_type', 'SPOOL')
                dpath = cfg.get('dest_path', '') or '(spool dir)'
                bnr = "YES" if cfg.get('banner', 1) else "NO"
                form = cfg.get('form_type', 'NORMAL')
                out.append(f"{q_name:<10}  {q_status:<8}  {dtype:<9}  {dpath:<20}  {bnr:<6}  {form}")

        # Recent entries
        entries = self.job_controller.list_entries(all_entries=True)
        print_entries = [e for e in entries if e['queue_name'] in [q['name'] for q in queues if q['type'] == 'PRINT']]
        out.append("")
        out.append(f"Recent Print Queue Entries (Total: {len(print_entries)}):")
        if print_entries:
            out.append("Entry  Job Name         User         Status       Queue       Submitted")
            out.append("-----  ---------------  -----------  -----------  ----------  --------------------")
            for e in print_entries[-8:]:
                out.append(f"{e['entry_id']:>5}  {e['job_name']:<15}  {e['user_name']:<11}  {e['status']:<11}  {e['queue_name']:<10}  {e['submit_time']}")
        else:
            out.append("  (No print entries recorded)")

        return "\n".join(out)

    def generate_systemd_unit(self, user=None) -> str:
        """Generates a complete systemd unit file."""
        if not user:
            user = os.environ.get("USER", "root")
            
        script_path = os.path.abspath(__file__)
        py_bin = sys.executable

        unit = f"""[Unit]
Description=DEC RSTS/E Print Queue Service (PBS Symbiont Daemon)
Documentation=https://github.com/dec-basic/pbs
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={repo_root}
ExecStart={py_bin} {script_path} run
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3s
StandardOutput=journal
StandardError=journal
KillMode=process

[Install]
WantedBy=multi-user.target
"""
        return unit


def main():
    parser = argparse.ArgumentParser(description="DEC RSTS/E Print Queue Service & Symbiont Manager")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "run", "systemd-unit", "configure", "apply-config", "discover"],
                        help="Action to perform")
    parser.add_argument("--config", "-c", help="Path to dec-printq.conf control file")
    parser.add_argument("--queue", help="Queue name for configure command")
    parser.add_argument("--dest-type", choices=["SPOOL", "FILE", "DEVICE", "COMMAND", "SOCKET"],
                        help="Destination type for queue")
    parser.add_argument("--dest-path", help="Destination path / command / host:port")
    parser.add_argument("--banner", type=int, choices=[0, 1], help="Enable (1) or disable (0) DEC burst banner")
    parser.add_argument("--form-type", default="NORMAL", help="Form type name")
    parser.add_argument("--base-dir", default=None, help="Base directory for database, spool, and logs")
    parser.add_argument("--install", action="store_true", help="Install systemd unit to user or system directory")
    parser.add_argument("--user", help="User to run systemd unit as")
    parser.add_argument("--generate-config", nargs="?", const="dec-printq.conf",
                        help="Generate control file from discovered network printers (filename optional, defaults to dec-printq.conf)")

    args = parser.parse_args()
    jc = JobController(base_dir=args.base_dir) if args.base_dir else None
    service = DECPrintService(job_controller=jc, config_file=args.config)

    if args.command == "run":
        service.run_foreground()

    elif args.command == "start":
        code, msg = service.start_daemon()
        print(msg)
        sys.exit(code)

    elif args.command == "stop":
        code, msg = service.stop_daemon()
        print(msg)
        sys.exit(code)

    elif args.command == "restart":
        service.stop_daemon()
        time.sleep(0.5)
        code, msg = service.start_daemon()
        print(msg)
        sys.exit(code)

    elif args.command == "status":
        print(service.get_status_text())

    elif args.command == "apply-config":
        applied = service.load_config_file(args.config)
        if applied:
            print(f"Successfully applied control file: {service.config_file}")
            for item in applied:
                print(f"  * {item}")
        else:
            print(f"Warning: No queues configured or control file not found ({args.config or service.config_file or 'dec-printq.conf'}).")

    elif args.command == "discover":
        print("Discovering printers on the network...")
        printers = discover_network_printers()
        if not printers:
            print("No network or CUPS printers detected.")
        else:
            print(f"Found {len(printers)} printer(s):\n")
            print(f"{'Model / Host':<28} {'IP Address':<16} {'JetDirect':<12} {'IPP':<8} {'CUPS Queue'}")
            print(f"{'-'*28} {'-'*16} {'-'*12} {'-'*8} {'-'*28}")
            for p in printers:
                model_host = p.get('model') or p.get('hostname') or 'Unknown'
                ip = p.get('ip') or '(resolving)'
                jd = f"Port {p['jetdirect_port']}" if p.get('jetdirect_port') else "No"
                ipp = f"Port {p['port']}" if p.get('port') else ("Yes" if p.get('ipp_uri') else "No")
                cups = p.get('cups_queue') or '-'
                print(f"{model_host[:28]:<28} {ip:<16} {jd:<12} {ipp:<8} {cups}")
            print("")

        if args.generate_config:
            target_file = args.generate_config
            generate_config_from_discovery(printers, target_file)
            print(f"Control file generated at: {target_file}")
            print(f"You can apply it anytime with: ./dec-printq.py apply-config --config {target_file}")

    elif args.command == "configure":
        if not args.queue:
            print("Error: --queue required for configure command")
            sys.exit(1)
        dtype = args.dest_type or "SPOOL"
        dpath = args.dest_path or ""
        bnr = 1 if args.banner is None else args.banner
        ftype = args.form_type or "NORMAL"
        service.job_controller.set_queue_config(args.queue, dest_type=dtype, dest_path=dpath, banner=bnr, form_type=ftype)
        print(f"Queue {args.queue} configured: dest_type={dtype}, dest_path={dpath}, banner={bnr}, form_type={ftype}")

    elif args.command == "systemd-unit":
        unit_text = service.generate_systemd_unit(user=args.user)
        if args.install:
            # Install to user systemd unit dir
            user_unit_dir = os.path.expanduser("~/.config/systemd/user")
            os.makedirs(user_unit_dir, exist_ok=True)
            unit_file = os.path.join(user_unit_dir, "dec-printq.service")
            with open(unit_file, "w") as f:
                f.write(unit_text)
            print(f"Systemd service installed to: {unit_file}")
            print("To enable and start:")
            print("  systemctl --user daemon-reload")
            print("  systemctl --user enable --now dec-printq.service")
        else:
            print(unit_text)

if __name__ == "__main__":
    main()
