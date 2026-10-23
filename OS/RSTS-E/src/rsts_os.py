#!/usr/bin/env python3
"""
DEC RSTS/E V10.1-L Operating System Emulation Monitor
Digital Equipment Corporation PDP-11 Resource-Sharing Timesharing System/Extended

Provides:
  - Authentic PDP-11/70 & RSTS/E V10.1-L Boot Loader (INIT.SYS) and Login Monitor
  - Project-Programmer Number (PPN) Account & Privilege Architecture ([1,1], [1,2], [1,3], [100,100], [200,200])
  - Logical Device Mapping (SY:, LB:, DK0:, KB0:, TT:, LP0:, MT0:)
  - Multiple Keyboard Monitors: DCL ($), BASIC-PLUS (Ready), and RSX (>)
  - Concise Command Language (CCL) dispatching all 12 RSTS/E-supported DEC-APPS
  - Native DEC BASIC-PLUS-2 Toolchain integration (BASIC, LINK, RUN, EDT, PBS Queues)
  - OS compatibility enforcement (rejects 32-bit VAX/VMS-only DECwindows X11 suite)
"""

import os
import sys
import glob
import json
import shlex
import shutil
import subprocess
from datetime import datetime


class RSTSEmulator:
    VERSION = "V10.1-L"
    NODE_NAME = "PDP11"
    CPU_MODEL = "PDP-11/70 (KB11-C / FP11-C, 22-bit Addressing, 4096 KW)"

    # Standard RSTS/E PPN Accounts ($ACCT.SYS)
    DEFAULT_ACCOUNTS = {
        "1,1": {
            "ppn": "[1,1]",
            "name": "LIBRARY",
            "password": "LIB",
            "priv": True,
            "quota": 50000,
            "desc": "System Library Account (LB:)",
            "dir_name": "001_001",
        },
        "1,2": {
            "ppn": "[1,2]",
            "name": "SYSTEM",
            "password": "SYSTEM",
            "priv": True,
            "quota": 100000,
            "desc": "System Manager / Operator Account (SY:)",
            "dir_name": "001_002",
        },
        "1,3": {
            "ppn": "[1,3]",
            "name": "PBS",
            "password": "PBS",
            "priv": True,
            "quota": 25000,
            "desc": "Print/Batch Services Spooler Account",
            "dir_name": "001_003",
        },
        "100,100": {
            "ppn": "[100,100]",
            "name": "DIBS",
            "password": "DIBS",
            "priv": False,
            "quota": 20000,
            "desc": "CTS-500 / DIBS-11 Commercial Accounting Account",
            "dir_name": "100_100",
        },
        "200,200": {
            "ppn": "[200,200]",
            "name": "GUEST",
            "password": "",
            "priv": False,
            "quota": 10000,
            "desc": "General Timesharing User Account",
            "dir_name": "200_200",
        },
    }

    # Applications historically supported on 16-bit PDP-11 RSTS/E
    SUPPORTED_CCL_APPS = {
        "HAMURABI": ("hamurabi", "Ancient Sumeria Economic Simulation (DEC 1973)"),
        "SORT11": ("sort11", "DEC RMS-11 File Sort & Index Utility"),
        "SORT": ("sort11", "DEC RMS-11 File Sort & Index Utility"),
        "RMSUTILS": ("rmsutils", "DEC RMS-11 Utilities Suite"),
        "RMSDES": ("rmsdes", "RMS-11 File Design Utility"),
        "RMSDEF": ("rmsdef", "RMS-11 File Definition Utility"),
        "RMSIFL": ("rmsifl", "RMS-11 Indexed File Load Utility"),
        "RMSCNV": ("rmscnv", "RMS-11 File Conversion Utility"),
        "RMSBCK": ("rmsbck", "RMS-11 File Backup Utility"),
        "RMSRST": ("rmsrst", "RMS-11 File Restore Utility"),
        "RMSDSP": ("rmsdsp", "RMS-11 File Display Utility"),
        "ADE": ("ade", "Application Development Environment V3.0 (4GL)"),
        "DATATRIEVE11": ("datatrieve11", "DEC DATATRIEVE-11 V3.0 Query & Report System"),
        "DATATRIEVE": ("datatrieve11", "DEC DATATRIEVE-11 V3.0 Query & Report System"),
        "DTR11": ("datatrieve11", "DEC DATATRIEVE-11 V3.0 Query & Report System"),
        "DTR": ("datatrieve11", "DEC DATATRIEVE-11 V3.0 Query & Report System"),
        "DECGRAPH": ("decgraph", "DECgraph V3.0 Presentation Graphics System"),
        "GRAPH": ("decgraph", "DECgraph V3.0 Presentation Graphics System"),
        "DECG": ("decgraph", "DECgraph V3.0 Presentation Graphics System"),
        "DECMAIL": ("decmail", "DECmail-11 V3.0 Electronic Messaging System"),
        "DECMAIL11": ("decmail", "DECmail-11 V3.0 Electronic Messaging System"),
        "MAIL": ("decmail", "DECmail-11 V3.0 Electronic Messaging System"),
        "DECWORD": ("decword", "DECword/DP V3.0 Word & Data Processing System"),
        "DECWORDDP": ("decword", "DECword/DP V3.0 Word & Data Processing System"),
        "WPS": ("decword", "DECword/DP V3.0 WPS-PLUS System"),
        "DIBS": ("dibs", "DIBS-11 V3.0 (DEC Integrated Business System / CTS-500)"),
        "DIBS11": ("dibs", "DIBS-11 V3.0 (DEC Integrated Business System / CTS-500)"),
        "CTS500": ("dibs", "CTS-500 / DIBS-11 Commercial Transaction System"),
        "FMS11": ("fms11", "FMS-11 V2.0 Forms Management System"),
        "FMS": ("fms11", "FMS-11 V2.0 Forms Management System"),
        "FED": ("fms11", "FMS-11 Form Editor"),
        "FDV": ("fms11", "FMS-11 Form Driver"),
        "MENU11": ("menu11", "MENU-11 V2.0 Menu Control & Dispatch Facility"),
        "MENU": ("menu11", "MENU-11 V2.0 Menu Control & Dispatch Facility"),
        "MCF": ("menu11", "MENU-11 V2.0 Menu Control Facility"),
        "INDENT": ("indent", "INDENT V2.0 BASIC-PLUS-2 Source Formatter"),
        "BP2FMT": ("indent", "INDENT V2.0 BASIC-PLUS-2 Source Formatter"),
        "PRETTY": ("indent", "INDENT V2.0 BASIC-PLUS-2 Pretty-Printer"),
        "EDT": ("edt", "DEC EDT Interactive Text Editor V3.0"),
        "EDIT": ("edt", "DEC EDT Interactive Text Editor V3.0"),
        "MACRO": ("macro11", "DEC PDP-11 MACRO-11 V05.05 Relocatable Macro Assembler"),
        "MACRO11": ("macro11", "DEC PDP-11 MACRO-11 V05.05 Relocatable Macro Assembler"),
        "COBOL": ("cobol81", "DEC PDP-11 COBOL-81 V2.4 (ANSI-74) Compiler"),
        "COBOL81": ("cobol81", "DEC PDP-11 COBOL-81 V2.4 (ANSI-74) Compiler"),
        "FORTRAN": ("fortran77", "DEC PDP-11 FORTRAN-77 V5.0 Compiler"),
        "FORTRAN77": ("fortran77", "DEC PDP-11 FORTRAN-77 V5.0 Compiler"),
        "F77": ("fortran77", "DEC PDP-11 FORTRAN-77 V5.0 Compiler"),
        "DIBOL": ("dibol83", "DEC CTS-500 / RSTS/E DIBOL-83 V5.3 Compiler"),
        "DIBOL83": ("dibol83", "DEC CTS-500 / RSTS/E DIBOL-83 V5.3 Compiler"),
        "RPG": ("rpgii", "DEC PDP-11 RPG II V2.1 Report Program Generator"),
        "RPGII": ("rpgii", "DEC PDP-11 RPG II V2.1 Report Program Generator"),
        "APL": ("apl11", "DEC PDP-11 APL-11 V2.1 Compiler & Interactive Workspace"),
        "APL11": ("apl11", "DEC PDP-11 APL-11 V2.1 Compiler & Interactive Workspace"),
    }

    # Applications strictly requiring 32-bit VAX/VMS or ULTRIX (NOT supported on PDP-11 RSTS/E)
    UNSUPPORTED_VMS_APPS = {
        "DECWINDOWS",
        "DECW_X11",
        "DECWX11",
        "DXSESSION",
        "DECW$SESSION",
        "DECTERM",
        "DXTERM",
        "DECW$DECTERM",
        "BOOKREADER",
        "DXBOOK",
        "DECW$BOOKREADER",
        "CALENDAR",
        "DXCALENDAR",
        "DECW$CALENDAR",
        "CARDFILER",
        "DXCARDFILER",
        "DECW$CARDFILER",
        "CDAVIEWER",
        "DXVDOC",
        "DECW$CDAVIEWER",
        "CALCULATOR",
        "DXCALC",
        "DECW$CALC",
        "CLOCK",
        "DXCLOCK",
        "DECW$CLOCK",
        "DECSOUND",
        "DXSOUND",
        "DECW$SOUND",
        "DXMAIL",
        "DECWINMAIL",
        "DECW$MAIL",
        "FILEVIEW",
        "DXFILEVIEW",
        "VUE$MASTER",
        "NOTEPAD",
        "DXNOTEPAD",
        "DECW$NOTEPAD",
    }

    def __init__(self, root_dir=None, current_ppn="1,2"):
        self.os_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.dec_root = os.path.abspath(os.path.join(self.os_dir, "..", ".."))
        self.sys_bin = self._locate_sys_bin()
        self.job_controller = self._locate_job_controller()

        if root_dir is None:
            root_dir = os.environ.get("RSTS_FS_ROOT", os.path.join(self.os_dir, "fs"))
        self.fs_root = os.path.abspath(root_dir)
        self.dk0_root = os.path.join(self.fs_root, "dk0")

        self.accounts = {k: dict(v) for k, v in self.DEFAULT_ACCOUNTS.items()}
        self.current_ppn = self.normalize_ppn(current_ppn) or "1,2"
        self.monitor_mode = "DCL"  # 'DCL', 'BASIC', or 'RSX'
        self.verify = False
        self.exit_requested = False
        self.logout_requested = False
        self._in_interactive_loop = False
        self.boot_time = datetime.now()
        self.pid = os.getpid()
        self.session_source = os.environ.get("DEC_SESSION_SOURCE", "SSH" if os.environ.get("SSH_CONNECTION") else "CONSOLE")
        self.ssh_port = int(os.environ.get("RSTS_SSH_PORT", "2211"))
        self.https_port = int(os.environ.get("RSTS_HTTPS_PORT", "8411"))
        self.sessions_path = os.path.join(self.fs_root, ".rsts_sessions.json")
        self.job_id = 1
        self.kb_line = "KB0:"

        # BASIC-PLUS Keyboard Monitor in-memory program buffer
        self.basic_prog_name = "NONAME"
        self.basic_lines = {}

        # Initialize filesystem and logicals
        self._init_filesystem()
        self._allocate_terminal_line()
        self.symbols = {
            "$STATUS": "1",
            "$SEVERITY": "1",
            "$PPN": self.accounts[self.current_ppn]["ppn"],
            "$USER": self.accounts[self.current_ppn]["name"],
            "SYS$SYSTEM": "LB:",
        }
        self.logicals = {
            "SY:": self.get_ppn_dir(self.current_ppn),
            "LB:": self.get_ppn_dir("1,1"),
            "DK0:": self.dk0_root,
            "KB:": "/dev/tty",
            self.kb_line: "/dev/tty",
            "TT:": "/dev/tty",
            "LP0:": "SYS$PRINT",
            "SYS$OUTPUT": self.kb_line,
            "SYS$INPUT": self.kb_line,
            "SYS$ERROR": self.kb_line,
            "SYS$SYSTEM": self.get_ppn_dir("1,1"),
        }
        self.ccl_table = dict(self.SUPPORTED_CCL_APPS)
        self.default_dir = self.get_ppn_dir(self.current_ppn)

    def _locate_sys_bin(self):
        candidates = [
            os.path.join(self.os_dir, "system", "bin"),
            "/opt/dec-rsts/system/bin",
            os.path.expanduser("~/.local/dec-basic2/bin"),
        ]
        for c in candidates:
            if os.path.isdir(c) and os.path.exists(os.path.join(c, "basicc")):
                return c
        return os.path.join(self.os_dir, "system", "bin")

    def _locate_job_controller(self):
        candidates = [
            os.path.join(self.os_dir, "system", "lib", "dcl", "job_controller.py"),
            "/opt/dec-rsts/system/lib/dcl/job_controller.py",
            os.path.join(self.dec_root, "LANG", "BASIC-PLUS-2", "dcl", "job_controller.py"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return candidates[0]

    def normalize_ppn(self, raw):
        if not raw:
            return None
        s = raw.strip().upper().strip("[]")
        if s in self.accounts:
            return s
        for ppn_key, acct in self.accounts.items():
            if acct["name"].upper() == s:
                return ppn_key
        if "," in s:
            parts = [p.strip() for p in s.split(",", 1)]
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                norm = f"{int(parts[0])},{int(parts[1])}"
                return norm
        return None

    def get_ppn_dir(self, ppn_key):
        if ppn_key in self.accounts:
            dname = self.accounts[ppn_key]["dir_name"]
        else:
            p1, p2 = ppn_key.split(",", 1)
            dname = f"{int(p1):03d}_{int(p2):03d}"
        path = os.path.join(self.dk0_root, dname)
        os.makedirs(path, exist_ok=True)
        return path

    def _reload_accounts(self):
        lib_dir = self.get_ppn_dir("1,1")
        acct_json = os.path.join(lib_dir, "ACCT.JSON")
        if os.path.exists(acct_json):
            try:
                with open(acct_json, "r") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.accounts.update(loaded)
            except Exception:
                pass

    def _load_live_sessions(self):
        sessions = {}
        if os.path.exists(self.sessions_path):
            try:
                with open(self.sessions_path, "r") as f:
                    raw = json.load(f)
                if isinstance(raw, dict):
                    for pid_str, info in raw.items():
                        try:
                            pid_val = int(pid_str)
                            if pid_val == self.pid:
                                sessions[pid_str] = info
                            else:
                                os.kill(pid_val, 0)
                                sessions[pid_str] = info
                        except Exception:
                            pass
            except Exception:
                pass
        return sessions

    def _save_sessions(self, sessions):
        try:
            tmp_p = self.sessions_path + f".{self.pid}.tmp"
            with open(tmp_p, "w") as f:
                json.dump(sessions, f, indent=2)
            os.replace(tmp_p, self.sessions_path)
        except Exception:
            pass

    def _allocate_terminal_line(self):
        sessions = self._load_live_sessions()
        pid_key = str(self.pid)
        if pid_key in sessions:
            self.job_id = sessions[pid_key].get("job_id", 1)
            self.kb_line = sessions[pid_key].get("kb_line", "KB0:")
            return
        used_jobs = {int(s.get("job_id", 0)) for s in sessions.values()}
        used_lines = {s.get("kb_line", "") for s in sessions.values()}

        if self.pid == 1 and "KB0:" not in used_lines:
            self.kb_line = "KB0:"
        else:
            for idx in range(0, 32):
                cand = f"KB{idx}:"
                if cand not in used_lines:
                    self.kb_line = cand
                    break

        j = 1
        while j in used_jobs:
            j += 1
        self.job_id = j

    def _register_session(self, logged_in=True, what=None):
        sessions = self._load_live_sessions()
        acct = self.accounts.get(self.current_ppn, self.DEFAULT_ACCOUNTS["1,2"])
        sessions[str(self.pid)] = {
            "pid": self.pid,
            "job_id": self.job_id,
            "kb_line": self.kb_line,
            "ppn_key": self.current_ppn,
            "ppn": acct["ppn"],
            "user": acct["name"],
            "priv": bool(acct.get("priv", False)),
            "monitor": self.monitor_mode,
            "what": what or self.monitor_mode,
            "logged_in": bool(logged_in),
            "source": self.session_source,
            "login_time": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
        }
        self._save_sessions(sessions)

    def _unregister_session(self):
        sessions = self._load_live_sessions()
        if str(self.pid) in sessions:
            sessions.pop(str(self.pid), None)
            self._save_sessions(sessions)

    def _save_accounts(self):
        lib_dir = self.get_ppn_dir("1,1")
        acct_json = os.path.join(lib_dir, "ACCT.JSON")
        with open(acct_json, "w") as f:
            json.dump(self.accounts, f, indent=2)
        acct_sys = os.path.join(lib_dir, "ACCT.SYS")
        with open(acct_sys, "w") as f:
            for k, v in self.accounts.items():
                f.write(f"{v['ppn']}:{v['name']}:{v['quota']}:{'PRIV' if v['priv'] else 'NOPRIV'}:{v['desc']}\n")

    def _init_filesystem(self):
        os.makedirs(self.dk0_root, exist_ok=True)
        for ppn_key in self.accounts:
            self.get_ppn_dir(ppn_key)

        # Load or populate [1,1] System Library account database ($ACCT.SYS)
        lib_dir = self.get_ppn_dir("1,1")
        acct_json = os.path.join(lib_dir, "ACCT.JSON")
        if os.path.exists(acct_json):
            try:
                with open(acct_json, "r") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.accounts.update(loaded)
                    for ppn_key in self.accounts:
                        self.get_ppn_dir(ppn_key)
            except Exception:
                pass
        self._save_accounts()

        # Populate [1,2] System Manager directory with classic RSTS/E welcome & sample files
        sys_dir = self.get_ppn_dir("1,2")
        welcome_path = os.path.join(sys_dir, "WELCOME.TXT")
        if not os.path.exists(welcome_path):
            with open(welcome_path, "w") as f:
                f.write(
                    "========================================================================\n"
                    "  Welcome to DEC RSTS/E V10.1-L (Resource-Sharing Timesharing System)\n"
                    "  Digital Equipment Corporation PDP-11 Series Emulation\n"
                    "========================================================================\n"
                    "  Logical Devices: SY: ([1,2]), LB: ([1,1]), DK0:, KB0:, LP0:\n"
                    "  Monitors:        DCL ($), BASIC-PLUS (SWITCH BASIC), RSX (SWITCH RSX)\n"
                    "  Type HELP or SHOW APPS for available DEC utilities and packages.\n"
                )

        login_com = os.path.join(sys_dir, "LOGIN.COM")
        if not os.path.exists(login_com):
            with open(login_com, "w") as f:
                f.write(
                    "$ ! RSTS/E V10.1-L System Manager Login Procedure [1,2]LOGIN.COM\n"
                    "$ WRITE SYS$OUTPUT \"RSTS/E V10.1-L System Manager [1,2] Session Initialized\"\n"
                )

        hello_bas = os.path.join(sys_dir, "HELLO.BAS")
        if not os.path.exists(hello_bas):
            with open(hello_bas, "w") as f:
                f.write(
                    "10 ! RSTS/E V10.1-L BASIC-PLUS-2 Sample Program\n"
                    "20 PRINT \"HELLO FROM DEC RSTS/E V10.1-L ON PDP-11!\"\n"
                    "30 END\n"
                )

        hello_mac = os.path.join(sys_dir, "HELLO.MAC")
        if not os.path.exists(hello_mac):
            with open(hello_mac, "w") as f:
                f.write(
                    "        .TITLE  HELLO - DEC PDP-11 RSTS/E MACRO-11 SAMPLE\n"
                    "        .IDENT  /V05.05/\n"
                    "        .MCALL  .PRINT,.EXIT\n"
                    "START:  MOV     #10.,R0\n"
                    "        MOV     #32.,R1\n"
                    "        ADD     R0,R1\n"
                    "        .PRINT  #MSG1\n"
                    "        .PRINT  R1\n"
                    "        .EXIT\n"
                    "MSG1:   .ASCIZ  /HELLO FROM DEC MACRO-11 V05.05 ON RSTS-E!/\n"
                    "        .END    START\n"
                )

        payrol_cbl = os.path.join(sys_dir, "PAYROL.CBL")
        if not os.path.exists(payrol_cbl):
            with open(payrol_cbl, "w") as f:
                f.write(
                    "       IDENTIFICATION DIVISION.\n"
                    "       PROGRAM-ID. PAYROL.\n"
                    "       ENVIRONMENT DIVISION.\n"
                    "       DATA DIVISION.\n"
                    "       WORKING-STORAGE SECTION.\n"
                    "       01  EMP-NAME       PIC X(20) VALUE \"J. DEC ENGINEER\".\n"
                    "       01  HOURS-WORKED   PIC 9(4)  VALUE 40.\n"
                    "       01  HOURLY-RATE    PIC 9(4)  VALUE 25.\n"
                    "       01  GROSS-PAY      PIC 9(6)  VALUE 0.\n"
                    "       PROCEDURE DIVISION.\n"
                    "       MAIN-LOGIC.\n"
                    "           MULTIPLY HOURS-WORKED BY HOURLY-RATE GIVING GROSS-PAY.\n"
                    "           ADD 200 TO GROSS-PAY.\n"
                    "           DISPLAY \"COBOL-81 PAYROLL: \" EMP-NAME \" GROSS=\" GROSS-PAY.\n"
                    "           STOP RUN.\n"
                )

        stats_for = os.path.join(sys_dir, "STATS.FOR")
        if not os.path.exists(stats_for):
            with open(stats_for, "w") as f:
                f.write(
                    "C     DEC PDP-11 FORTRAN-77 V5.0 SAMPLE\n"
                    "      PROGRAM STATS\n"
                    "      INTEGER I, ISUM\n"
                    "      ISUM = 0\n"
                    "      DO 100 I = 1, 10\n"
                    "         ISUM = ISUM + I\n"
                    " 100  CONTINUE\n"
                    "      WRITE(6,*) 'FORTRAN-77 SUM(1..10)=', ISUM\n"
                    "      STOP\n"
                    "      END\n"
                )

        invoic_dbl = os.path.join(sys_dir, "INVOIC.DBL")
        if not os.path.exists(invoic_dbl):
            with open(invoic_dbl, "w") as f:
                f.write(
                    ".TITLE 'INVOIC - DEC DIBOL-83 SAMPLE'\n"
                    "RECORD\n"
                    "    CUST,   A24, 'DIGITAL EQUIPMENT CORP'\n"
                    "    QTY,    D4,  12\n"
                    "    PRICE,  D6,  150\n"
                    "    TOTAL,  D8,  0\n"
                    "PROC\n"
                    "    TOTAL = QTY * PRICE\n"
                    "    DISPLAY(1, 'DIBOL-83 CUSTOMER: ', CUST, ' TOTAL=', TOTAL)\n"
                    "    STOP\n"
                    "END\n"
                )

        slsrpt_rpg = os.path.join(sys_dir, "SLSRPT.RPG")
        if not os.path.exists(slsrpt_rpg):
            with open(slsrpt_rpg, "w") as f:
                f.write(
                    "* DEC PDP-11 RPG II V2.1 SAMPLE\n"
                    "H SLSRPT\n"
                    "F QPRINT  O   F  132     PRINTER\n"
                    "C           Z-ADD 1250     Q1SLS\n"
                    "C           Z-ADD 1750     Q2SLS\n"
                    "C   Q1SLS   ADD   Q2SLS    TOTSLS\n"
                    "C           SETON          LR\n"
                    "O QPRINT  H  1P\n"
                    "O                         'DEC RPG II V2.1 SALES REPORT'\n"
                    "O QPRINT  T  LR\n"
                    "O                         'RPG II TOTAL SALES=' TOTSLS\n"
                )

        vector_apl = os.path.join(sys_dir, "VECTOR.APL")
        if not os.path.exists(vector_apl):
            with open(vector_apl, "w") as f:
                f.write(
                    "'DEC APL-11 V2.1 VECTOR ENGINE'\n"
                    "V <- .IOTA 10\n"
                    "+/ V\n"
                    "*/ .IOTA 5\n"
                    ")OFF\n"
                )

    def resolve_path(self, rsts_spec):
        """Translate a RSTS/E file specification (e.g. SY:HELLO.BAS, LB:SORT11, [1,2]FILE.TXT) to host path."""
        if not rsts_spec:
            return self.default_dir
        spec = rsts_spec.strip().strip('"').strip("'")

        # Check explicit device prefix: SY:, LB:, DK0:
        upper = spec.upper()
        if upper.startswith("SY:"):
            rest = spec[3:]
            return self._resolve_in_dir(self.get_ppn_dir(self.current_ppn), rest)
        if upper.startswith("LB:"):
            rest = spec[3:]
            cand = self._resolve_in_dir(self.get_ppn_dir("1,1"), rest)
            if os.path.exists(cand):
                return cand
            bin_cand = os.path.join(self.sys_bin, rest.lower())
            if os.path.exists(bin_cand):
                return bin_cand
            return cand
        if upper.startswith("DK0:"):
            rest = spec[4:]
            if rest.startswith("[") and "]" in rest:
                idx = rest.index("]")
                ppn_str = rest[1:idx]
                fname = rest[idx + 1:]
                norm = self.normalize_ppn(ppn_str)
                if norm:
                    return self._resolve_in_dir(self.get_ppn_dir(norm), fname)
            return self._resolve_in_dir(self.default_dir, rest)

        # Check [proj,prog]FILENAME
        if spec.startswith("[") and "]" in spec:
            idx = spec.index("]")
            ppn_str = spec[1:idx]
            fname = spec[idx + 1:]
            norm = self.normalize_ppn(ppn_str)
            if norm:
                return self._resolve_in_dir(self.get_ppn_dir(norm), fname)

        # Check user-defined logicals
        for log_name, log_target in self.logicals.items():
            if upper.startswith(log_name.upper()) and log_name.endswith(":"):
                rest = spec[len(log_name):]
                if os.path.isdir(log_target):
                    return self._resolve_in_dir(log_target, rest)

        if os.path.isabs(spec) or os.path.exists(spec):
            return os.path.abspath(spec)

        return self._resolve_in_dir(self.default_dir, spec)

    def _rad50_parts(self, filename):
        """Return RSTS/E RAD-50 (6.3) uppercase (stem, ext) for a filename."""
        bname = os.path.basename(filename)
        if "." in bname:
            stem, ext = bname.rsplit(".", 1)
        else:
            stem, ext = bname, ""
        return stem.upper()[:6], ext.upper()[:3]

    def _resolve_in_dir(self, base_dir, rel_name):
        if not rel_name:
            return base_dir
        exact = os.path.join(base_dir, rel_name)
        if os.path.exists(exact):
            return exact
        if os.path.isdir(base_dir):
            # 1. Exact case-insensitive match
            for entry in os.listdir(base_dir):
                if entry.lower() == rel_name.lower():
                    return os.path.join(base_dir, entry)
            # 2. RAD-50 6.3 match (so displayed 6.3 names in DIR always match on TYPE/COPY/DELETE/RUN)
            if "*" not in rel_name and "?" not in rel_name:
                target_rad50 = self._rad50_parts(rel_name)
                for entry in sorted(os.listdir(base_dir)):
                    if self._rad50_parts(entry) == target_rad50:
                        return os.path.join(base_dir, entry)
        return exact

    def find_executable(self, name):
        """Find a binary in staged system/bin, LANG/*/compiler, or PATH."""
        clean = name.strip().lower()
        if clean.startswith("$"):
            clean = clean[1:]
        cand = os.path.join(self.sys_bin, clean)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
        for lang_dir in ("BASIC-PLUS-2", "MACRO-11", "COBOL-81", "FORTRAN-77", "DIBOL-83", "RPG-II", "APL-11"):
            lang_cand = os.path.join(self.dec_root, "LANG", lang_dir, "compiler", clean)
            if os.path.isfile(lang_cand) and os.access(lang_cand, os.X_OK):
                return lang_cand
        which_res = shutil.which(clean)
        if which_res:
            return which_res
        return None

    def print_boot_sequence(self):
        now_str = datetime.now().strftime("%d-%b-%Y  %I:%M %p")
        print("BOOTING RSTS/E ON PDP-11/70 (DK0:[1,1]INIT.SYS)...")
        print("INIT V10.1-0L  RSTS/E V10.1-L")
        print("Command File Name? <CR> for DEFAULT")
        print("Memory allocation:")
        print("  0K -  111K : RSTS/E Monitor & Executive")
        print("112K -  159K : Basic-Plus-2 / RMS-11 Shared Run-Time System")
        print("160K - 2047K : User Job Area (MAXJOB = 63)")
        print("Devices configured: DK0: (RA81), KB0:-KB31: (DHV11), LP0: (LP11), MT0: (TU16)")
        print(f"RSTS {self.VERSION}  {now_str}  System Initialized.\n")

    def interactive_login(self, in_stream=None):
        stream = in_stream or sys.stdin
        self._register_session(logged_in=False, what="LOGIN")
        now_str = datetime.now().strftime("%d-%b-%Y  %I:%M %p")
        print(f"\nRSTS {self.VERSION}  {now_str}\n")
        while True:
            sys.stdout.write("User: ")
            sys.stdout.flush()
            try:
                user_in = stream.readline()
            except KeyboardInterrupt:
                print("^C")
                continue
            if not user_in:
                self._unregister_session()
                return False
            if "\x03" in user_in:
                print("^C")
                continue
            user_in = user_in.strip()
            if not user_in:
                now_str = datetime.now().strftime("%d-%b-%Y  %I:%M %p")
                print(f"\nRSTS {self.VERSION}  {now_str}\n")
                continue
            if user_in.upper() in ("EXIT", "QUIT", "BYE", "LOGOUT", "\x04", "\x1a") and self.pid != 1:
                self._unregister_session()
                return False
            self._reload_accounts()
            ppn = self.normalize_ppn(user_in)
            if not ppn or ppn not in self.accounts:
                print("?Invalid user account - use PPN (e.g. 1,2 or 200,200) or account name (SYSTEM, GUEST)")
                continue
            acct = self.accounts[ppn]
            if acct["password"]:
                sys.stdout.write("Password: ")
                sys.stdout.flush()
                try:
                    pw_in = stream.readline()
                except KeyboardInterrupt:
                    print("^C")
                    continue
                if not pw_in:
                    self._unregister_session()
                    return False
                if "\x03" in pw_in:
                    print("^C")
                    continue
                pw_in = pw_in.strip()
                if pw_in.upper() != acct["password"].upper():
                    print("?Invalid login attempt")
                    continue
            self.monitor_mode = "DCL"
            self.basic_prog_name = "NONAME"
            self.basic_lines.clear()
            self._switch_account(ppn)
            self._register_session(logged_in=True, what=self.monitor_mode)
            print(f"Last interactive login on {datetime.now().strftime('%A, %d-%b-%Y %I:%M %p')} at {self.kb_line}")
            print(f"Job {self.job_id}  User {acct['name']} {acct['ppn']} on {self.kb_line} ({self.monitor_mode} Monitor)\n")
            return True

    def _switch_account(self, ppn_key):
        self.current_ppn = ppn_key
        acct = self.accounts[ppn_key]
        self.default_dir = self.get_ppn_dir(ppn_key)
        self.logicals["SY:"] = self.default_dir
        self.symbols["$PPN"] = acct["ppn"]
        self.symbols["$USER"] = acct["name"]
        if self._in_interactive_loop:
            self._register_session(logged_in=True, what=self.monitor_mode)

    def get_prompt(self):
        if self.monitor_mode == "BASIC":
            return "\nReady\n\n"
        elif self.monitor_mode == "RSX":
            return "> "
        return "$ "

    def run_interactive(self, require_login=True, show_boot=False):
        if show_boot:
            self.print_boot_sequence()

        self._in_interactive_loop = True
        need_login = require_login
        try:
            while not self.exit_requested:
                if need_login:
                    if not self.interactive_login():
                        break
                else:
                    self._register_session(logged_in=True, what=self.monitor_mode)
                    now_str = datetime.now().strftime("%d-%b-%Y  %I:%M %p")
                    acct = self.accounts[self.current_ppn]
                    print(f"RSTS {self.VERSION}  {now_str}")
                    print(f"Job {self.job_id}  User {acct['name']} {acct['ppn']} on {self.kb_line}  ({self.monitor_mode} Monitor)")
                    print("Print/Batch Services (PBS) Active. Type HELP or SHOW APPS for commands.\n")

                self.logout_requested = False
                while not self.exit_requested and not self.logout_requested:
                    sys.stdout.write(self.get_prompt())
                    sys.stdout.flush()
                    try:
                        line = sys.stdin.readline()
                    except KeyboardInterrupt:
                        print("^C")
                        continue
                    if not line:
                        self.exit_requested = True
                        break
                    if "\x03" in line:
                        print("^C")
                        continue
                    line = line.rstrip("\r\n")
                    if line == "\x1a":  # Ctrl-Z
                        break
                    try:
                        self.execute_line(line)
                    except KeyboardInterrupt:
                        print("\n^C")

                # After BYE / LOGOUT, return terminal line to the RSTS/E User: login prompt
                need_login = True
        finally:
            self._unregister_session()
            self._in_interactive_loop = False
        return 0

    def execute_script(self, script_path):
        resolved = self.resolve_path(script_path)
        if not os.path.isfile(resolved):
            for ext in (".COM", ".com", ".DCL", ".dcl"):
                if os.path.isfile(resolved + ext):
                    resolved = resolved + ext
                    break
        if not os.path.isfile(resolved):
            print(f"%DCL-E-OPENIN, error opening {script_path} as input")
            print("-RMS-E-FNF, file not found")
            return 1
        with open(resolved, "r", errors="replace") as f:
            lines = [ln.rstrip("\r\n") for ln in f]
        return self._execute_procedure_lines(lines)

    def _execute_procedure_lines(self, lines):
        labels = {}
        for idx, raw in enumerate(lines):
            s = raw.strip()
            if s.startswith("$"):
                s = s[1:].strip()
            if ":" in s:
                lbl_cand = s.split(":", 1)[0].strip()
                if lbl_cand and " " not in lbl_cand and "/" not in lbl_cand:
                    labels[lbl_cand.upper()] = idx

        pc = 0
        while pc < len(lines) and not self.exit_requested and not self.logout_requested:
            raw = lines[pc].strip()
            pc += 1
            if not raw:
                continue
            if self.verify and not raw.startswith("!"):
                print(f"$ {raw}")
            if raw.startswith("$"):
                raw = raw[1:].strip()
            if not raw or raw.startswith("!"):
                continue
            if ":" in raw:
                lbl_cand, rest = raw.split(":", 1)
                if lbl_cand.strip() and " " not in lbl_cand.strip() and "/" not in lbl_cand.strip():
                    raw = rest.strip()
            if not raw or raw.startswith("!"):
                continue
            if raw.upper() == "EXIT" or raw.upper().startswith("EXIT "):
                break
            if raw.upper().startswith("GOTO "):
                target = raw[5:].strip().upper()
                if target in labels:
                    pc = labels[target]
                    continue
            self.execute_line(raw)
        return 0

    def execute_line(self, line):
        s = line.strip()
        if not s:
            return 0
        if s.startswith("$"):
            s = s[1:].strip()
        if not s or s.startswith("!"):
            return 0

        # Substitute 'SYMBOL' in command line
        for sym_k, sym_v in self.symbols.items():
            token = f"'{sym_k}'"
            if token in s:
                s = s.replace(token, sym_v)

        if self.monitor_mode == "BASIC":
            return self._execute_basic_monitor(s)
        elif self.monitor_mode == "RSX":
            return self._execute_rsx_monitor(s)
        return self._execute_dcl_monitor(s)

    # ==========================================================================
    # BASIC-PLUS Keyboard Monitor (Ready prompt)
    # ==========================================================================
    def _execute_basic_monitor(self, s):
        # If line begins with a line number, store it in memory buffer
        parts = s.split(None, 1)
        if parts[0].isdigit():
            lnum = int(parts[0])
            if len(parts) == 1:
                self.basic_lines.pop(lnum, None)
            else:
                self.basic_lines[lnum] = s
            return 0

        verb = parts[0].upper()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if verb == "SWITCH":
            target = (arg.upper() or "DCL").split()[0]
            if target in ("DCL", "BASIC", "RSX"):
                self.monitor_mode = target
                print(f"Switched to RSTS/E {target} Keyboard Monitor")
                return 0
        if verb == "DCL":
            self.monitor_mode = "DCL"
            print("Switched to RSTS/E DCL Keyboard Monitor")
            return 0
        if verb == "NEW":
            self.basic_prog_name = arg.upper() if arg else "NONAME"
            self.basic_lines.clear()
            return 0
        if verb == "LIST":
            print(f"{self.basic_prog_name}  RSTS {self.VERSION} BASIC-PLUS")
            for k in sorted(self.basic_lines.keys()):
                print(self.basic_lines[k])
            return 0
        if verb in ("CAT", "CATALOG", "DIR"):
            return self._cmd_dir(arg)
        if verb in ("SAVE", "REPLACE"):
            fname = arg if arg else f"{self.basic_prog_name}.BAS"
            if "." not in fname:
                fname += ".BAS"
            target = self.resolve_path(fname)
            with open(target, "w") as f:
                for k in sorted(self.basic_lines.keys()):
                    f.write(self.basic_lines[k] + "\n")
            print(f"Saved {os.path.basename(target)}")
            return 0
        if verb == "OLD":
            if not arg:
                print("?File name required")
                return 1
            fname = arg if "." in arg else arg + ".BAS"
            target = self.resolve_path(fname)
            if not os.path.isfile(target):
                print(f"?Can't find file or account - {arg}")
                return 1
            self.basic_lines.clear()
            self.basic_prog_name = os.path.splitext(os.path.basename(target))[0].upper()
            with open(target, "r") as f:
                for idx, ln in enumerate(f, start=1):
                    ln_s = ln.rstrip("\r\n")
                    if ln_s.strip():
                        tok = ln_s.split(None, 1)[0]
                        key = int(tok) if tok.isdigit() else idx * 10
                        self.basic_lines[key] = ln_s
            return 0
        if verb in ("RUN", "RUNNH"):
            if arg:
                return self._cmd_run(arg)
            if not self.basic_lines:
                print("?No program in memory")
                return 1
            tmp_bas = os.path.join(self.default_dir, f"{self.basic_prog_name}.BAS")
            with open(tmp_bas, "w") as f:
                for k in sorted(self.basic_lines.keys()):
                    f.write(self.basic_lines[k] + "\n")
            return self._compile_and_run_bas(tmp_bas, show_header=(verb == "RUN"))
        if verb in ("BYE", "LOGOUT", "LOGOFF"):
            print(f"Job {self.job_id}  User {self.accounts[self.current_ppn]['name']} {self.accounts[self.current_ppn]['ppn']} logged off {self.kb_line} at {datetime.now().strftime('%I:%M %p')}")
            self.monitor_mode = "DCL"
            self.basic_prog_name = "NONAME"
            self.basic_lines.clear()
            if "/DISCONNECT" in rest.upper() and self.pid != 1:
                self.exit_requested = True
            elif self._in_interactive_loop:
                self._register_session(logged_in=False, what="LOGIN")
                self.logout_requested = True
            else:
                self.exit_requested = True
            return 0
        if verb == "SYSTAT":
            return self._cmd_systat()
        if verb == "HELLO":
            return self._cmd_hello(arg)
        # Fallback to DCL / CCL command
        return self._execute_dcl_monitor(s)

    # ==========================================================================
    # RSX Keyboard Monitor (> prompt)
    # ==========================================================================
    def _execute_rsx_monitor(self, s):
        parts = s.split(None, 1)
        verb = parts[0].upper()
        arg = parts[1].strip() if len(parts) > 1 else ""
        if verb == "SWITCH":
            target = arg.upper() or "DCL"
            if target in ("DCL", "BASIC", "RSX"):
                self.monitor_mode = target
                print(f"Switched to RSTS/E {target} Keyboard Monitor")
                return 0
        if verb == "MCR":
            return self._execute_dcl_monitor(arg)
        if verb == "PIP":
            return self._cmd_pip(arg)
        if verb in ("TKB", "LINK"):
            return self._cmd_link(arg)
        if verb in ("MAC", "MACRO", "MACRO11"):
            return self._cmd_lang_compiler("macro11", "MACRO-11", (".MAC", ".mac", ".ASM", ".asm"), arg)
        if verb in ("F77", "FOR", "FORTRAN", "FORTRAN77"):
            return self._cmd_lang_compiler("fortran77", "FORTRAN-77", (".FOR", ".for", ".FTN", ".ftn", ".F77", ".f77"), arg)
        if verb in ("COB", "COBOL", "COBOL81"):
            return self._cmd_lang_compiler("cobol81", "COBOL-81", (".CBL", ".cbl", ".COB", ".cob"), arg)
        if verb in ("DBL", "DIBOL", "DIBOL83"):
            return self._cmd_lang_compiler("dibol83", "DIBOL-83", (".DBL", ".dbl", ".DIB", ".dib"), arg)
        if verb in ("RPG", "RPGII"):
            return self._cmd_lang_compiler("rpgii", "RPG II", (".RPG", ".rpg"), arg)
        if verb in ("APL", "APL11"):
            return self._cmd_apl(verb, arg)
        return self._execute_dcl_monitor(s)

    # ==========================================================================
    # DCL Keyboard Monitor ($ prompt)
    # ==========================================================================
    def _execute_dcl_monitor(self, s):
        if s.startswith("@"):
            return self.execute_script(s[1:].strip())

        # Check IF <cond> THEN <stmt>
        if s.upper().startswith("IF ") and " THEN " in s.upper():
            idx = s.upper().index(" THEN ")
            cond = s[3:idx].strip()
            then_stmt = s[idx + 6:].strip()
            if self._eval_dcl_cond(cond):
                return self.execute_line(then_stmt)
            return 0

        # Check symbol assignment: VAR = VAL or VAR := VAL
        if "=" in s and not s.split("=", 1)[0].strip().startswith("/"):
            lhs = s.split("=", 1)[0].rstrip(":").strip()
            if lhs and " " not in lhs and "/" not in lhs:
                rhs = s.split("=", 1)[1].strip().strip('"').strip("'")
                self.symbols[lhs.upper()] = rhs
                return 0

        # Extract verb and qualifiers
        first_word = s.split(None, 1)[0]
        rest = s.split(None, 1)[1].strip() if len(s.split(None, 1)) > 1 else ""
        if "/" in first_word:
            v_part, q_part = first_word.split("/", 1)
            verb = v_part.upper()
            rest = f"/{q_part} {rest}".strip()
        else:
            verb = first_word.upper()

        # Check if user attempted to invoke a VAX/VMS-only DECwindows facility
        if verb in self.UNSUPPORTED_VMS_APPS:
            print(
                f"?Unsupported OS facility '{verb}' - DECwindows requires 32-bit VAX/VMS or ULTRIX "
                f"(not supported on 16-bit PDP-11 RSTS/E {self.VERSION})"
            )
            self.symbols["$STATUS"] = "2"
            return 2

        if verb in ("HELP", "MAN"):
            return self._cmd_help(rest)
        if verb == "SHOW":
            return self._cmd_show(rest)
        if verb == "SYSTAT":
            return self._cmd_systat()
        if verb in ("HELLO", "LOGIN"):
            return self._cmd_hello(rest)
        if verb in ("BYE", "LOGOUT", "LOGOFF"):
            print(f"Job {self.job_id}  User {self.accounts[self.current_ppn]['name']} {self.accounts[self.current_ppn]['ppn']} logged off {self.kb_line} at {datetime.now().strftime('%I:%M %p')}")
            self.monitor_mode = "DCL"
            self.basic_prog_name = "NONAME"
            self.basic_lines.clear()
            if "/DISCONNECT" in rest.upper() and self.pid != 1:
                self.exit_requested = True
            elif self._in_interactive_loop:
                self._register_session(logged_in=False, what="LOGIN")
                self.logout_requested = True
            else:
                self.exit_requested = True
            return 0
        if verb in ("SHUTDOWN", "SHUTUP", "HALT"):
            if not self.accounts[self.current_ppn].get("priv", False):
                print("?Protection violation - SHUTDOWN requires privileged account [1,2]")
                self.symbols["$STATUS"] = "2"
                return 1
            now_str = datetime.now().strftime("%I:%M %p")
            print(f"SHUTUP {self.VERSION}  RSTS/E System Shutdown")
            print(f"%SHUTUP-I-SHUT, RSTS/E {self.VERSION} shutting down on DK0:")
            print("%SHUTUP-I-KILL, terminating active jobs and PBS queues...")
            print("%SHUTUP-I-DISM, dismounting system disk DK0: (RA81)")
            print(f"System halted at {now_str}")
            self.exit_requested = True
            return 0
        if verb == "EXIT":
            return 0
        if verb == "QUIT":
            print("%DCL-I-LOGOUT, use BYE or LOGOUT to log off terminal session, or SHUTDOWN to halt system")
            return 0
        if verb == "SWITCH":
            target = (rest.strip().upper() or "DCL").split()[0]
            if target in ("DCL", "BASIC", "RSX"):
                self.monitor_mode = target
                print(f"Switched to RSTS/E {target} Keyboard Monitor")
                return 0
            print(f"?Invalid monitor '{target}' - specify DCL, BASIC, or RSX")
            return 1
        if verb in ("DIR", "DIRECT", "DIRECTORY"):
            return self._cmd_dir(rest)
        if verb == "TYPE":
            return self._cmd_type(rest)
        if verb == "COPY":
            return self._cmd_copy(rest)
        if verb == "RENAME":
            return self._cmd_rename(rest)
        if verb == "DELETE":
            return self._cmd_delete(rest)
        if verb == "CREATE":
            return self._cmd_create(rest)
        if verb == "MODIFY":
            return self._cmd_modify(rest)
        if verb == "PIP":
            return self._cmd_pip(rest)
        if verb == "FIT":
            return self._cmd_fit(rest)
        if verb in ("UTILITY", "AUTHORIZE", "REACT"):
            return self._cmd_utility(rest)
        if verb == "SET":
            return self._cmd_set(rest)
        if verb in ("ASSIGN", "DEFINE"):
            return self._cmd_assign(verb, rest)
        if verb == "DEASSIGN":
            return self._cmd_deassign(rest)
        if verb in ("WRITE", "ECHO"):
            return self._cmd_write(rest)
        if verb in ("BASIC", "COMPILE", "BP2"):
            return self._cmd_basic(rest)
        if verb in ("MACRO", "MACRO11", "MAC"):
            return self._cmd_lang_compiler("macro11", "MACRO-11", (".MAC", ".mac", ".ASM", ".asm"), rest)
        if verb in ("COBOL", "COBOL81", "COB"):
            return self._cmd_lang_compiler("cobol81", "COBOL-81", (".CBL", ".cbl", ".COB", ".cob"), rest)
        if verb in ("FORTRAN", "FORTRAN77", "F77", "FOR"):
            return self._cmd_lang_compiler("fortran77", "FORTRAN-77", (".FOR", ".for", ".FTN", ".ftn", ".F77", ".f77"), rest)
        if verb in ("DIBOL", "DIBOL83", "DBL"):
            return self._cmd_lang_compiler("dibol83", "DIBOL-83", (".DBL", ".dbl", ".DIB", ".dib"), rest)
        if verb in ("RPG", "RPGII"):
            return self._cmd_lang_compiler("rpgii", "RPG II", (".RPG", ".rpg"), rest)
        if verb in ("APL", "APL11", "APLC"):
            return self._cmd_apl(verb, rest)
        if verb in ("LINK", "TKB"):
            return self._cmd_link(rest)
        if verb == "RUN":
            return self._cmd_run(rest)
        if verb == "PRINT":
            return self._cmd_print(rest)
        if verb == "SUBMIT":
            return self._cmd_submit(rest)
        if verb == "START":
            return self._cmd_queue_ctl("start-queue", rest)
        if verb == "STOP":
            if not rest:
                return 0
            return self._cmd_queue_ctl("stop-queue", rest)

        # Check CCL (Concise Command Language) table for supported RSTS/E applications
        if verb in self.ccl_table:
            bin_name, _ = self.ccl_table[verb]
            return self._invoke_app(bin_name, rest)

        # Check if verb matches a binary in system/bin or default_dir
        exe = self.find_executable(verb)
        if exe:
            return self._invoke_app(verb.lower(), rest)

        print(f"%DCL-W-IVVERB, unrecognized command verb '{verb}' - check validity and spelling")
        self.symbols["$STATUS"] = "2"
        return 1

    def _eval_dcl_cond(self, cond):
        for op in (".EQS.", ".EQ.", "==", "="):
            if op in cond.upper():
                idx = cond.upper().index(op)
                lhs = cond[:idx].strip().strip('"').strip("'")
                rhs = cond[idx + len(op):].strip().strip('"').strip("'")
                lhs_val = self.symbols.get(lhs.upper(), lhs)
                rhs_val = self.symbols.get(rhs.upper(), rhs)
                return lhs_val.upper() == rhs_val.upper()
        for op in (".NES.", ".NE.", "<>", "!="):
            if op in cond.upper():
                idx = cond.upper().index(op)
                lhs = cond[:idx].strip().strip('"').strip("'")
                rhs = cond[idx + len(op):].strip().strip('"').strip("'")
                lhs_val = self.symbols.get(lhs.upper(), lhs)
                rhs_val = self.symbols.get(rhs.upper(), rhs)
                return lhs_val.upper() != rhs_val.upper()
        return False

    # ==========================================================================
    # RSTS/E System & File Commands
    # ==========================================================================
    def _cmd_help(self, rest):
        topic = rest.strip().upper()
        if not topic:
            print(
                "==============================================================================\n"
                f"  DEC RSTS/E {self.VERSION} Operating System Monitor & DCL Help\n"
                "==============================================================================\n"
                "  System & Session Commands:\n"
                "    HELLO <ppn>        Switch PPN account (e.g. HELLO 1,2 or HELLO 200,200)\n"
                "    BYE / LOGOUT       Log off current user session and return to KB0: User: prompt\n"
                "    SHUTDOWN / HALT    Privileged RSTS/E SHUTUP system shutdown (halts OS/container)\n"
                "    SYSTAT             Display RSTS/E system jobs, PPNs, RTS, and disk status\n"
                "    SWITCH <monitor>   Switch Keyboard Monitor (DCL, BASIC, RSX)\n"
                "    SHOW SYSTEM        Display RSTS/E monitor, CPU, memory, and PBS status\n"
                "    SHOW DEVICES       Display PDP-11 Unibus/Q-bus hardware device table\n"
                "    SHOW USERS         List logged-in PPN accounts and terminal lines\n"
                "    SHOW ACCOUNT       Display $ACCT.SYS PPN accounts (supports /FULL)\n"
                "    CREATE/ACCOUNT     Create PPN account (/NAME=, /PASSWORD=, /QUOTA=, /PRIV)\n"
                "    MODIFY/ACCOUNT     Modify PPN account attributes (or SET ACCOUNT)\n"
                "    DELETE/ACCOUNT     Remove non-system PPN account from $ACCT.SYS\n"
                "    SET PASSWORD       Change account password (/PASSWORD=, /GENERATE)\n"
                "    SHOW MEMORY        Display PDP-11 physical memory layout (KW)\n"
                "    SHOW LOGICALS      Display system and user logical device names\n"
                "    SHOW CCL / APPS    List installed RSTS/E CCL applications & utilities\n"
                "    SHOW QUEUE / JOBS  Display Print/Batch Services (PBS) queues and jobs\n"
                "\n"
                "  File & Directory Management:\n"
                "    DIRECTORY [spec]   List files in PPN directory (SY:, LB:, [1,2])\n"
                "    TYPE <file>        Display contents of a file\n"
                "    COPY <src> <dst>   Copy file between PPN directories or devices\n"
                "    RENAME <old> <new> Rename file\n"
                "    DELETE <file>      Delete file or queue entry (/ENTRY=n)\n"
                "    PIP / FIT          Peripheral Interchange Program / File Info Table\n"
                "    SET DEFAULT <ppn>  Change current working PPN or directory\n"
                "    ASSIGN <dev> <log> Assign logical device name\n"
                "\n"
                "  Programming & Applications (CCL):\n"
                "    BASIC <file.bas>   Compile DEC BASIC-PLUS-2 program (.BAS -> .OBJ)\n"
                "    MACRO <file.mac>   Assemble DEC PDP-11 MACRO-11 program (.MAC -> .OBJ)\n"
                "    COBOL <file.cbl>   Compile DEC PDP-11 COBOL-81 program (.CBL -> .OBJ)\n"
                "    FORTRAN <file.for> Compile DEC PDP-11 FORTRAN-77 program (.FOR -> .OBJ)\n"
                "    DIBOL <file.dbl>   Compile DEC CTS-500 DIBOL-83 program (.DBL -> .OBJ)\n"
                "    RPG <file.rpg>     Compile DEC PDP-11 RPG II program (.RPG -> .OBJ)\n"
                "    APL [file.apl]     Interactive APL-11 workspace or compile .APL -> .OBJ\n"
                "    LINK <file.obj>    Link RSTS/E object module (.OBJ -> .TSK executable)\n"
                "    RUN <prog>         Execute compiled .TSK program or source file\n"
                "    EDT <file>         Invoke DEC EDT V3.0 Text Editor\n"
                "    SUBMIT / PRINT     Submit batch job (.COM) or print job to PBS spooler\n"
                "    HAMURABI, SORT11, RMSUTILS, ADE, DATATRIEVE11 (DTR), DECGRAPH,\n"
                "    DECMAIL (MAIL), DECWORD (WPS), DIBS (CTS500), FMS11, MENU11, INDENT\n"
            )
            return 0
        if topic in self.ccl_table:
            bname, desc = self.ccl_table[topic]
            print(f"{topic} — {desc} (RSTS/E CCL command -> LB:{bname.upper()}.TSK)")
            return 0
        print(f"RSTS/E Help Topic '{topic}': Use HELP for full command summary.")
        return 0

    def _cmd_show(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        quals = [t.upper() for t in rest.split() if t.startswith("/")]
        if not tokens:
            print("%DCL-E-PARAM, missing SHOW parameter")
            return 1
        sub = tokens[0].upper()
        acct = self.accounts[self.current_ppn]
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        if sub in ("SYSTEM", "SYS"):
            print(f"RSTS {self.VERSION} ({self.NODE_NAME}) — {self.CPU_MODEL}")
            print(f"System Time:   {now_str}")
            print(f"Current User:  {acct['name']} {acct['ppn']} ({'Privileged' if acct['priv'] else 'Non-Privileged'})")
            print(f"Terminal Line: {self.kb_line} (Job {self.job_id}, Source: {self.session_source})")
            print(f"KB Monitor:    {self.monitor_mode} (Auxiliary RTS: BASIC2, RMS11, EDT)")
            print(f"System Disk:   DK0: (RA81 Structured Disk, Mounted)")
            print(f"Job Subsystem: Print/Batch Services (PBS) Active")
            print(f"Multi-User:    SSH (port {self.ssh_port}) & HTTPS Web VT100 (port {self.https_port})")
            print(f"Default Dir:   {self.default_dir}")
            return 0
        if sub in ("NETWORK", "NET", "MULTIUSER"):
            print(f"RSTS/E {self.VERSION} Multi-User Terminal Concentrator (DHV11 / DECserver):")
            print(f"  Console Line:  KB0: (Operator Console)")
            print(f"  SSH Lines:     KB1:-KB31: via OpenSSH on port {self.ssh_port} (user: dec)")
            print(f"  HTTPS Lines:   KB1:-KB31: via HTTPS/WSS Web VT100 on port {self.https_port}")
            return 0
        if sub in ("DEVICES", "DEV", "DEVICE"):
            sessions = self._load_live_sessions()
            line_owners = {s["kb_line"]: s["ppn"] for s in sessions.values() if s.get("logged_in")}
            line_owners[self.kb_line] = acct["ppn"]
            print("Device  Type    Status          Owner   Description")
            print("------  ------  --------------  ------  ------------------------------------")
            print("DK0:    RA81    Mounted/Public  [1,1]   Primary RSTS/E System Disk (SY:/LB:)")
            for idx in range(0, 4):
                kbl = f"KB{idx}:"
                desc = "Console Interactive Terminal" if idx == 0 else f"Timesharing Terminal Line {idx} (SSH/HTTPS)"
                if kbl in line_owners:
                    print(f"{kbl:<6}  DHV11   Allocated       {line_owners[kbl]:<6}  {desc}")
                else:
                    print(f"{kbl:<6}  DHV11   Available       None    {desc}")
            print("LP0:    LP11    Spooling (PBS)  [1,3]   System Line Printer (SYS$PRINT)")
            print("MT0:    TU16    Online/Free     None    9-Track Magnetic Tape Transport")
            print("XH0:    DEQNA   Online          [1,2]   Q-bus Ethernet Interface (SSH/HTTPS)")
            return 0
        if sub in ("USERS", "USER"):
            sessions = self._load_live_sessions()
            active = [s for s in sessions.values() if s.get("logged_in")]
            if not any(s.get("pid") == self.pid for s in active):
                active.append({
                    "job_id": self.job_id,
                    "user": acct["name"],
                    "ppn": acct["ppn"],
                    "kb_line": self.kb_line,
                    "monitor": self.monitor_mode,
                    "priv": acct["priv"],
                })
            active.sort(key=lambda x: x.get("job_id", 1))
            print("Job  User      PPN        Line   RTS      State   Priv")
            print("---  --------  ---------  -----  -------  ------  ----")
            max_j = 1
            for s in active:
                jid = s.get("job_id", 1)
                if jid > max_j:
                    max_j = jid
                print(
                    f"{jid:>3}  {s['user']:<8}  {s['ppn']:<9}  {s['kb_line']:<5}  {s.get('monitor', 'DCL'):<7}  RN      {'Yes' if s.get('priv') else 'No'}"
                )
            print(f"{max_j + 1:>3}  PBS       [1,3]      Det    PBS...   SL      Yes")
            print(f"{max_j + 2:>3}  ERRCPY    [1,2]      Det    RTS...   SL      Yes")
            return 0
        if sub in ("MEMORY", "MEM"):
            print("PDP-11/70 Physical Memory Allocation (Total: 2048 KW / 4096 KB)")
            print("  Area                   Address Range (KW)   Size (KW)")
            print("  ---------------------  -------------------  ---------")
            print("  RSTS/E Monitor         0000 - 0111            112 KW")
            print("  Shared Run-Time (RTS)  0112 - 0255            144 KW")
            print("  Disk Cache & Buffers   0256 - 0383            128 KW")
            print("  User Job Space (Free)  0384 - 2047           1664 KW")
            return 0
        if sub in ("TIME", "DATE"):
            print(now_str)
            return 0
        if sub in ("DEFAULT", "DEF"):
            print(f"Current PPN: {acct['ppn']} ({acct['name']}) -> {self.default_dir}")
            return 0
        if sub in ("LOGICAL", "LOGICALS", "TRANSLATION"):
            print("RSTS/E Logical Device Assignments:")
            for k, v in self.logicals.items():
                print(f'  "{k}" = "{v}"')
            return 0
        if sub in ("SYMBOL", "SYMBOLS"):
            print("DCL Symbols:")
            for k, v in self.symbols.items():
                print(f'  {k} = "{v}"')
            return 0
        if sub in ("CCL", "APPS", "APPLICATIONS", "UTILITIES"):
            print(f"RSTS/E {self.VERSION} Installed CCL Applications & System Utilities (LB:[1,1]):")
            print("----------------------------------------------------------------------------")
            seen = set()
            for cmd, (bname, desc) in sorted(self.ccl_table.items()):
                if bname not in seen:
                    seen.add(bname)
                    print(f"  {cmd:<14} (LB:{bname.upper():<12}) - {desc}")
            print("----------------------------------------------------------------------------")
            print("Note: VAX/VMS 32-bit DECwindows X11 applications are excluded on PDP-11 RSTS/E.")
            return 0
        if sub in ("ACCOUNTS", "ACCOUNT", "PPN"):
            self._reload_accounts()
            target_spec = tokens[1] if len(tokens) > 1 else None
            full = ("/FULL" in quals) or ("/ALL" in quals)
            items = list(self.accounts.items())
            if target_spec and target_spec != "*":
                norm = self.normalize_ppn(target_spec)
                if not norm or norm not in self.accounts:
                    print(f"%ACC-W-NOACCT, account {target_spec} not found")
                    return 1
                items = [(norm, self.accounts[norm])]
            if full:
                for k, v in items:
                    print(f"Account PPN:   {v['ppn']} ({v['name']})")
                    print(f"  Description: {v['desc']}")
                    print(f"  Directory:   DK0:{v['ppn']} ({self.get_ppn_dir(k)})")
                    print(f"  Disk Quota:  {v['quota']} blocks")
                    print(f"  Privileges:  {'PRIV' if v['priv'] else 'NOPRIV'}")
                    print(f"  Login Flags: {v.get('flags', 'NODISUSER')}")
                    print(f"  Password:    {'<set>' if v.get('password') else '<none>'}")
                    print("")
            else:
                print("PPN        Account   Quota     Privileges  Flags       Description")
                print("---------  --------  --------  ----------  ----------  --------------------------------------")
                for k, v in items:
                    flags = v.get("flags", "NODISUSER")
                    print(f"{v['ppn']:<9}  {v['name']:<8}  {v['quota']:>8}  {'PRIV' if v['priv'] else 'NOPRIV':<10}  {flags:<10}  {v['desc']}")
            return 0
        if sub in ("QUEUE", "QUEUES"):
            q_arg = tokens[1] if len(tokens) > 1 else None
            cmd = [sys.executable, self.job_controller, "show-queue"]
            if q_arg:
                cmd.append(q_arg)
            if "/ALL" in quals or "/FULL" in quals:
                cmd.append("--all")
            return subprocess.call(cmd)
        if sub in ("JOB", "JOBS"):
            cmd = [sys.executable, self.job_controller, "show-jobs"]
            if "/ALL" in quals or "/FULL" in quals:
                cmd.append("--all")
            return subprocess.call(cmd)
        if sub in ("ENTRY", "ENTRIES"):
            cmd = [sys.executable, self.job_controller, "show-entry"]
            if len(tokens) > 1:
                cmd.append(tokens[1])
            return subprocess.call(cmd)
        if sub in ("TERMINAL", "TERM"):
            print(f"Terminal {self.kb_line} Type=VT100, Width=80, Page=24, Baud=9600, Scope, Eightbit ({self.session_source})")
            return 0

        print(f"%DCL-E-IVKEYW, unrecognized SHOW keyword '{sub}'")
        return 1

    def _cmd_systat(self):
        acct = self.accounts[self.current_ppn]
        now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
        sessions = self._load_live_sessions()
        active = [s for s in sessions.values() if s.get("logged_in")]
        if not any(s.get("pid") == self.pid for s in active):
            active.append({
                "job_id": self.job_id,
                "ppn": acct["ppn"],
                "kb_line": self.kb_line,
                "what": "SYSTAT",
                "monitor": self.monitor_mode,
            })
        active.sort(key=lambda x: x.get("job_id", 1))
        print(f"RSTS {self.VERSION} ({self.NODE_NAME}) Status at {now_str}   Up: 00:42:15")
        print("Job    Who    Where    What     Size    State     Run-Time   Pri/RB   RTS")
        print("---  -------  -----  --------  ------  -------  -----------  ------  ------")
        max_j = 1
        for s in active:
            jid = s.get("job_id", 1)
            if jid > max_j:
                max_j = jid
            what_str = "SYSTAT" if s.get("pid") == self.pid else s.get("what", s.get("monitor", "DCL"))
            print(f"{jid:>2}   {s['ppn']:<7}  {s['kb_line']:<5}  {what_str:<8}  16/32K  RN           00:01.2   -8/6   {s.get('monitor', 'DCL')}")
        print(f"{max_j + 1:>2}   [1,3]    Det    PBS        12/32K  SL           00:00.4    0/6   DCL")
        print(f"{max_j + 2:>2}   [1,2]    Det    ERRCPY      8/32K  SL           00:00.1    0/6   RTS")
        total_jobs = len(active) + 2
        print("\nBusy Devices: None")
        print("Disk Structure:")
        print("Dsk  Open     Free     Clu   Err   Name      Level    Comments")
        print(f"DK0  {total_jobs:>3}     84210      4     0    RSTS10    1.2      Pub, DLU, Mounted")
        print("Small   Large   Jobs    Hung TTY's   Errors")
        print(f" 412     1664K  {total_jobs:>2}/63       0           0")
        return 0

    def _cmd_hello(self, rest):
        if not rest:
            print(f"Currently logged in as {self.accounts[self.current_ppn]['name']} {self.accounts[self.current_ppn]['ppn']} on {self.kb_line}")
            return 0
        self._reload_accounts()
        token = rest.split()[0]
        ppn = self.normalize_ppn(token)
        if not ppn or ppn not in self.accounts:
            print(f"?Invalid PPN or account '{token}'")
            return 1
        self._switch_account(ppn)
        acct = self.accounts[ppn]
        print(f"Switched session to User {acct['name']} {acct['ppn']} on {self.kb_line}")
        return 0

    def _cmd_dir(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        spec = tokens[0] if tokens else "SY:*"
        target = self.resolve_path(spec)
        if os.path.isdir(target):
            pattern = os.path.join(target, "*")
            disp_dir = target
        else:
            pattern = target if ("*" in target or "?" in target) else target
            disp_dir = os.path.dirname(target) or self.default_dir

        acct = self.accounts[self.current_ppn]
        print(f" Name .Typ    Size    Prot     Date       SY:{acct['ppn']} ({disp_dir})")
        print("----------------------------------------------------------------------")
        files = sorted(glob.glob(pattern))
        total_blocks = 0
        count = 0
        for f in files:
            if os.path.isdir(f):
                continue
            r_stem, r_ext = self._rad50_parts(f)
            st = os.stat(f)
            blocks = max(1, (st.st_size + 511) // 512)
            total_blocks += blocks
            count += 1
            dt = datetime.fromtimestamp(st.st_mtime).strftime("%d-%b-%y")
            print(f"{r_stem:<6}.{r_ext:<3} {blocks:>6}   < 60>   {dt}")
        print(f"\nTotal of {total_blocks} blocks in {count} files in {acct['ppn']}")
        return 0

    def _cmd_type(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if not tokens:
            print("%DCL-E-NOFILE, missing file to display")
            return 1
        target = self.resolve_path(tokens[0])
        if not os.path.isfile(target):
            print(f"?Can't find file or account - {tokens[0]}")
            return 1
        with open(target, "r", errors="replace") as f:
            sys.stdout.write(f.read())
        return 0

    def _cmd_copy(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing source or destination")
            return 1
        src = self.resolve_path(tokens[0])
        dst = self.resolve_path(tokens[1])
        if not os.path.isfile(src):
            print(f"?Can't find file - {tokens[0]}")
            return 1
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        shutil.copy2(src, dst)
        print(f"%DCL-I-COPIED, copied {os.path.basename(src)} to {os.path.basename(dst)}")
        return 0

    def _cmd_rename(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing source or destination")
            return 1
        src = self.resolve_path(tokens[0])
        dst = self.resolve_path(tokens[1])
        if not os.path.exists(src):
            print(f"?Can't find file - {tokens[0]}")
            return 1
        shutil.move(src, dst)
        print(f"%DCL-I-RENAMED, renamed {os.path.basename(src)} to {os.path.basename(dst)}")
        return 0

    def _parse_dcl_tokens_and_quals(self, rest):
        tokens = []
        quals = {}
        for tok in shlex.split(rest) if rest else []:
            if tok.startswith("/"):
                for part in tok.lstrip("/").split("/"):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        quals[k.upper()] = v
                    elif ":" in part:
                        k, v = part.split(":", 1)
                        quals[k.upper()] = v
                    else:
                        quals[part.upper()] = True
            elif "/" in tok and not os.path.exists(tok):
                subparts = tok.split("/")
                if subparts[0]:
                    tokens.append(subparts[0])
                for part in subparts[1:]:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        quals[k.upper()] = v
                    elif ":" in part:
                        k, v = part.split(":", 1)
                        quals[k.upper()] = v
                    else:
                        quals[part.upper()] = True
            else:
                tokens.append(tok)
        return tokens, quals

    def _cmd_create(self, rest):
        tokens, quals = self._parse_dcl_tokens_and_quals(rest)
        if "ACCOUNT" in quals or "ACCOUNTS" in quals or (tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS")):
            if tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS"):
                tokens = tokens[1:]
            return self._create_account_dcl(tokens, quals)
        if "DIRECTORY" in quals or "DIR" in quals:
            if not tokens:
                print("%DCL-E-PARAM, missing directory specification")
                return 1
            return self._create_account_dcl(tokens, quals)
        if not tokens:
            print("%DCL-E-PARAM, missing file or /ACCOUNT qualifier for CREATE")
            return 1
        # If first token looks like a PPN [proj,prog], treat as CREATE/ACCOUNT
        if tokens[0].startswith("[") and "," in tokens[0]:
            return self._create_account_dcl(tokens, quals)
        target = self.resolve_path(tokens[0])
        with open(target, "w") as f:
            f.write("")
        print(f"%DCL-I-CREATED, created {os.path.basename(target)}")
        return 0

    def _create_account_dcl(self, tokens, quals):
        if not tokens:
            print("%DCL-E-PARAM, missing PPN [proj,prog] for CREATE/ACCOUNT")
            return 1
        raw_spec = tokens[0].strip("[]")
        if "," in raw_spec:
            p1, p2 = [x.strip() for x in raw_spec.split(",", 1)]
            if not (p1.isdigit() and p2.isdigit()):
                print(f"?Invalid PPN '{tokens[0]}'")
                return 1
            ppn_key = f"{int(p1)},{int(p2)}"
            default_name = f"U{int(p1)}_{int(p2)}"
        else:
            default_name = raw_spec.upper()
            ppn_key = quals.get("PPN", "200,201").strip("[]")
            p1, p2 = [x.strip() for x in ppn_key.split(",", 1)]
            ppn_key = f"{int(p1)},{int(p2)}"

        name = (quals.get("NAME") or quals.get("USER") or (tokens[1] if len(tokens) > 1 else default_name)).upper()
        password = quals.get("PASSWORD", "")
        if password is True:
            password = ""
        quota = int(quals.get("QUOTA", 10000))
        priv = bool("PRIVILEGES" in quals or "PRIV" in quals)
        if "NOPRIVILEGES" in quals or "NOPRIV" in quals:
            priv = False
        flags = "DISUSER" if "DISUSER" in quals else "NODISUSER"
        desc = quals.get("OWNER") or quals.get("DESC") or f"User Account {name}"

        p1, p2 = ppn_key.split(",", 1)
        self.accounts[ppn_key] = {
            "ppn": f"[{ppn_key}]",
            "name": name,
            "password": str(password),
            "priv": priv,
            "quota": quota,
            "flags": flags,
            "desc": str(desc),
            "dir_name": f"{int(p1):03d}_{int(p2):03d}",
        }
        self.get_ppn_dir(ppn_key)
        self._save_accounts()
        print(f"%ACC-S-CREATED, account [{ppn_key}] ({name}) created on DK0: [Quota={quota}, {'PRIV' if priv else 'NOPRIV'}]")
        return 0

    def _cmd_modify(self, rest):
        tokens, quals = self._parse_dcl_tokens_and_quals(rest)
        if tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS"):
            tokens = tokens[1:]
        return self._modify_account_dcl(tokens, quals)

    def _modify_account_dcl(self, tokens, quals):
        if not tokens:
            print("%DCL-E-PARAM, missing PPN or account name for MODIFY/ACCOUNT")
            return 1
        ppn_key = self.normalize_ppn(tokens[0])
        if not ppn_key or ppn_key not in self.accounts:
            print(f"%ACC-E-NOTFND, account {tokens[0]} not found")
            return 1
        acct = self.accounts[ppn_key]
        if "NAME" in quals and isinstance(quals["NAME"], str):
            acct["name"] = quals["NAME"].upper()
        if "USER" in quals and isinstance(quals["USER"], str):
            acct["name"] = quals["USER"].upper()
        if "PASSWORD" in quals:
            acct["password"] = "" if quals["PASSWORD"] is True else str(quals["PASSWORD"])
        if "NOPASSWORD" in quals:
            acct["password"] = ""
        if "QUOTA" in quals and str(quals["QUOTA"]).isdigit():
            acct["quota"] = int(quals["QUOTA"])
        if "PRIVILEGES" in quals or "PRIV" in quals:
            acct["priv"] = True
        if "NOPRIVILEGES" in quals or "NOPRIV" in quals:
            acct["priv"] = False
        if "DISUSER" in quals:
            acct["flags"] = "DISUSER"
        if "NODISUSER" in quals:
            acct["flags"] = "NODISUSER"
        if "OWNER" in quals and isinstance(quals["OWNER"], str):
            acct["desc"] = quals["OWNER"]
        if "DESC" in quals and isinstance(quals["DESC"], str):
            acct["desc"] = quals["DESC"]
        self._save_accounts()
        print(f"%ACC-S-MODIFIED, account {acct['ppn']} ({acct['name']}) updated [Quota={acct['quota']}, {'PRIV' if acct['priv'] else 'NOPRIV'}]")
        return 0

    def _cmd_delete(self, rest):
        tokens, quals = self._parse_dcl_tokens_and_quals(rest)
        if "ENTRY" in quals:
            eid = str(quals["ENTRY"])
            return subprocess.call([sys.executable, self.job_controller, "delete-entry", eid])
        if "ACCOUNT" in quals or "ACCOUNTS" in quals or (tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS")):
            if tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS"):
                tokens = tokens[1:]
            if not tokens:
                print("%DCL-E-PARAM, missing PPN or account name for DELETE/ACCOUNT")
                return 1
            ppn_key = self.normalize_ppn(tokens[0])
            if not ppn_key or ppn_key not in self.accounts:
                print(f"%ACC-E-NOTFND, account {tokens[0]} not found")
                return 1
            if ppn_key in ("1,1", "1,2", "1,3"):
                print(f"%ACC-E-DELERR, cannot delete protected system account [{ppn_key}]")
                return 1
            removed = self.accounts.pop(ppn_key)
            self._save_accounts()
            print(f"%ACC-S-DELETED, account {removed['ppn']} ({removed['name']}) deleted from $ACCT.SYS")
            return 0
        if not tokens:
            print("%DCL-E-PARAM, missing file or qualifier for DELETE")
            return 1
        target = self.resolve_path(tokens[0])
        if os.path.isfile(target):
            os.remove(target)
            print(f"%DCL-I-DELETED, file {os.path.basename(target)} deleted")
            return 0
        print(f"?Can't find file - {tokens[0]}")
        return 1

    def _cmd_pip(self, rest):
        """RSTS/E Peripheral Interchange Program (PIP): supports DST=SRC or /L directory."""
        s = rest.strip()
        if not s or "/L" in s.upper() or "/DI" in s.upper():
            spec = s.split("/")[0].strip() or "SY:*"
            return self._cmd_dir(spec)
        if "/DE" in s.upper():
            spec = s.split("/")[0].strip()
            return self._cmd_delete(spec)
        if "=" in s:
            dst_s, src_s = s.split("=", 1)
            return self._cmd_copy(f"{src_s.strip()} {dst_s.strip()}")
        return self._cmd_dir(s)

    def _cmd_fit(self, rest):
        """RSTS/E File Information Table (FIT) utility."""
        print(f"FIT V10.1-L — RSTS/E File Information Table Utility ({self.accounts[self.current_ppn]['ppn']})")
        return self._cmd_dir(rest)

    def _cmd_utility(self, rest):
        """RSTS/E System Manager Account Utility (UTILITY / REACT)."""
        tokens, quals = self._parse_dcl_tokens_and_quals(rest)
        if tokens and tokens[0].upper() in ("ADD", "CREATE"):
            sub_tokens = tokens[1:]
            if len(sub_tokens) >= 2 and "NAME" not in quals:
                quals["NAME"] = sub_tokens[1]
            return self._create_account_dcl(sub_tokens, quals)
        if tokens and tokens[0].upper() in ("MODIFY", "SET"):
            return self._modify_account_dcl(tokens[1:], quals)
        if tokens and tokens[0].upper() in ("DELETE", "REMOVE"):
            return self._cmd_delete("/ACCOUNT " + " ".join(tokens[1:]))
        return self._cmd_show("ACCOUNTS " + rest)

    def _cmd_set(self, rest):
        tokens, quals = self._parse_dcl_tokens_and_quals(rest)
        if not tokens:
            print("%DCL-E-PARAM, missing SET parameter")
            return 1
        opt = tokens[0].upper()
        if opt in ("ACCOUNT", "ACCOUNTS"):
            return self._modify_account_dcl(tokens[1:], quals)
        if opt == "PASSWORD":
            target_spec = quals.get("ACCOUNT") or quals.get("USER") or (tokens[1] if len(tokens) > 1 else self.current_ppn)
            ppn_key = self.normalize_ppn(str(target_spec))
            if not ppn_key or ppn_key not in self.accounts:
                print(f"%SET-E-NOTFND, account {target_spec} not found")
                return 1
            if "GENERATE" in quals:
                new_pw = "PDP11$99"
            elif "PASSWORD" in quals and isinstance(quals["PASSWORD"], str):
                new_pw = quals["PASSWORD"]
            elif "NEW" in quals and isinstance(quals["NEW"], str):
                new_pw = quals["NEW"]
            elif len(tokens) > 2:
                new_pw = tokens[2]
            elif len(tokens) > 1 and self.normalize_ppn(tokens[1]) is None:
                new_pw = tokens[1]
            else:
                new_pw = "UPDATED"
            self.accounts[ppn_key]["password"] = str(new_pw)
            self._save_accounts()
            print(f"%SET-S-PASSCHG, password updated for account {self.accounts[ppn_key]['ppn']} ({self.accounts[ppn_key]['name']})")
            return 0
        if opt in ("DEFAULT", "DEF"):
            if len(tokens) < 2:
                print("%DCL-E-PARAM, missing directory or PPN")
                return 1
            arg = tokens[1]
            ppn = self.normalize_ppn(arg)
            if ppn and ppn in self.accounts:
                self._switch_account(ppn)
                print(f"Default PPN set to {self.accounts[ppn]['ppn']} ({self.default_dir})")
                return 0
            resolved = self.resolve_path(arg)
            if os.path.isdir(resolved):
                self.default_dir = resolved
                self.logicals["SY:"] = resolved
                return 0
            print(f"?Can't find directory or account - {arg}")
            return 1
        if opt == "VERIFY":
            self.verify = True
            return 0
        if opt == "NOVERIFY":
            self.verify = False
            return 0
        print(f"%DCL-W-IVKEYW, unrecognized SET option '{opt}'")
        return 0

    def _cmd_assign(self, verb, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing value or logical name")
            return 1
        if verb == "DEFINE":
            log_name, target = tokens[0].upper(), tokens[1]
        else:
            target, log_name = tokens[0], tokens[1].upper()
        if not log_name.endswith(":"):
            log_name_colon = log_name + ":"
        else:
            log_name_colon = log_name
        self.logicals[log_name] = target
        self.logicals[log_name_colon] = target
        return 0

    def _cmd_deassign(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if not tokens:
            return 1
        name = tokens[0].upper()
        self.logicals.pop(name, None)
        self.logicals.pop(name.rstrip(":"), None)
        self.logicals.pop(name.rstrip(":") + ":", None)
        return 0

    def _cmd_write(self, rest):
        s = rest.strip()
        for prefix in ("SYS$OUTPUT", "KB0:", "KB:", "TT:"):
            if s.upper().startswith(prefix):
                s = s[len(prefix):].strip()
                break
        if s.startswith('"') and s.endswith('"') and len(s) >= 2:
            s = s[1:-1]
        print(s)
        return 0

    def _is_dcl_qualifier(self, token):
        if not token.startswith("/"):
            return False
        if os.path.exists(token) or token.count("/") > 1:
            return False
        return True

    # ==========================================================================
    # BASIC-PLUS-2 Compiler, Linker, Runtime & Application Execution
    # ==========================================================================
    def _cmd_basic(self, rest):
        tokens = []
        obj_out = None
        for t in rest.split():
            if t.upper().startswith("/OBJECT=") or t.upper().startswith("/OBJ="):
                obj_out = self.resolve_path(t.split("=", 1)[1])
            elif not self._is_dcl_qualifier(t):
                tokens.append(t)
        if not tokens:
            print("%DCL-E-NOFILE, missing BASIC source filename")
            return 1
        src = self.resolve_path(tokens[0])
        if not os.path.isfile(src) and os.path.isfile(src + ".BAS"):
            src = src + ".BAS"
        elif not os.path.isfile(src) and os.path.isfile(src + ".bas"):
            src = src + ".bas"
        if not os.path.isfile(src):
            print(f"?Can't find BASIC source file - {tokens[0]}")
            return 1
        if not obj_out:
            src_dir = os.path.dirname(src) or self.default_dir
            r_stem, _ = self._rad50_parts(src)
            obj_out = os.path.join(src_dir, f"{r_stem}.OBJ")

        basicc_bin = self.find_executable("basicc")
        if not basicc_bin:
            print("%BP2-F-NOCOMP, native basicc compiler not found")
            return 1
        rc = subprocess.call([basicc_bin, src, "-o", obj_out], cwd=self.default_dir)
        # Remove intermediate raw bytecode .bin artifact so only authentic .OBJ remains in PPN dir
        stem_out, _ = os.path.splitext(obj_out)
        for bin_cand in (stem_out + ".bin", obj_out + ".bin"):
            if os.path.isfile(bin_cand):
                try:
                    os.remove(bin_cand)
                except OSError:
                    pass
        return rc

    def _rel_to_cwd(self, path):
        if not path:
            return path
        try:
            rel = os.path.relpath(path, self.default_dir)
            if len(rel) < len(path):
                return rel
        except ValueError:
            pass
        return path

    def _cmd_lang_compiler(self, bin_name, lang_label, default_exts, rest):
        if not rest or not rest.strip():
            return self._invoke_app(bin_name, "")
        tokens = []
        obj_out = None
        lst_out = None
        want_default_lst = False
        for t in rest.split():
            up = t.upper()
            if up.startswith("/OBJECT=") or up.startswith("/OBJ="):
                obj_out = self.resolve_path(t.split("=", 1)[1])
            elif up.startswith("/LIST=") or up.startswith("/LST="):
                lst_out = self.resolve_path(t.split("=", 1)[1])
            elif up in ("/LIST", "/LST"):
                want_default_lst = True
            elif not self._is_dcl_qualifier(t):
                tokens.append(t)

        if not tokens:
            print(f"%DCL-E-NOFILE, missing {lang_label} source filename")
            return 1

        raw_spec = tokens[0]
        if "=" in raw_spec and not raw_spec.startswith("/"):
            lhs, rhs = raw_spec.split("=", 1)
            src_token = rhs.strip()
            if "," in lhs:
                o_part, l_part = lhs.split(",", 1)
                if o_part.strip():
                    obj_out = self.resolve_path(o_part.strip())
                if l_part.strip():
                    lst_out = self.resolve_path(l_part.strip())
            elif lhs.strip():
                obj_out = self.resolve_path(lhs.strip())
        else:
            src_token = raw_spec

        src = self.resolve_path(src_token)
        if not os.path.isfile(src):
            for ext_cand in default_exts:
                if os.path.isfile(src + ext_cand):
                    src = src + ext_cand
                    break
        if not os.path.isfile(src):
            print(f"?Can't find {lang_label} source file - {src_token}")
            return 1

        src_dir = os.path.dirname(src) or self.default_dir
        r_stem, _ = self._rad50_parts(src)
        if not obj_out:
            obj_out = os.path.join(src_dir, f"{r_stem}.OBJ")
        if want_default_lst and not lst_out:
            lst_out = os.path.join(src_dir, f"{r_stem}.LST")

        comp_bin = self.find_executable(bin_name)
        if not comp_bin:
            print(f"%{bin_name.upper()}-F-NOCOMP, native {lang_label} compiler not found")
            return 1

        env = os.environ.copy()
        env["PATH"] = f"{self.sys_bin}:{env.get('PATH', '')}"
        cmd = [comp_bin, self._rel_to_cwd(src), "-o", self._rel_to_cwd(obj_out)]
        if lst_out:
            cmd.extend(["-l", self._rel_to_cwd(lst_out)])
        return subprocess.call(cmd, cwd=self.default_dir, env=env)

    def _cmd_apl(self, verb, rest):
        apl_bin = self.find_executable("apl11")
        if not apl_bin:
            print("%APL11-F-NOCOMP, native APL-11 compiler/interpreter not found")
            return 1
        env = os.environ.copy()
        env["PATH"] = f"{self.sys_bin}:{env.get('PATH', '')}"

        if not rest or not rest.strip():
            if verb.upper() == "APLC":
                print("%DCL-E-NOFILE, missing APL-11 source filename")
                return 1
            return subprocess.call([apl_bin, "--interactive"], cwd=self.default_dir, env=env)

        tokens = []
        obj_out = None
        lst_out = None
        want_default_lst = False
        interactive_mode = False
        run_script_mode = False
        for t in rest.split():
            up = t.upper()
            if up.startswith("/OBJECT=") or up.startswith("/OBJ="):
                obj_out = self.resolve_path(t.split("=", 1)[1])
            elif up.startswith("/LIST=") or up.startswith("/LST="):
                lst_out = self.resolve_path(t.split("=", 1)[1])
            elif up in ("/LIST", "/LST"):
                want_default_lst = True
            elif up in ("/INTERACTIVE", "/WS"):
                interactive_mode = True
            elif up in ("/RUN", "/EXEC"):
                run_script_mode = True
            elif not self._is_dcl_qualifier(t):
                tokens.append(t)

        if interactive_mode and not tokens:
            return subprocess.call([apl_bin, "--interactive"], cwd=self.default_dir, env=env)

        if not tokens:
            print("%DCL-E-NOFILE, missing APL-11 source filename")
            return 1

        raw_spec = tokens[0]
        if "=" in raw_spec and not raw_spec.startswith("/"):
            lhs, rhs = raw_spec.split("=", 1)
            src_token = rhs.strip()
            if "," in lhs:
                o_part, l_part = lhs.split(",", 1)
                if o_part.strip():
                    obj_out = self.resolve_path(o_part.strip())
                if l_part.strip():
                    lst_out = self.resolve_path(l_part.strip())
            elif lhs.strip():
                obj_out = self.resolve_path(lhs.strip())
        else:
            src_token = raw_spec

        src = self.resolve_path(src_token)
        if not os.path.isfile(src):
            for ext_cand in (".APL", ".apl", ".AWS", ".aws"):
                if os.path.isfile(src + ext_cand):
                    src = src + ext_cand
                    break
        if not os.path.isfile(src):
            print(f"?Can't find APL-11 source file - {src_token}")
            return 1

        if run_script_mode:
            return subprocess.call([apl_bin, "--run", self._rel_to_cwd(src)], cwd=self.default_dir, env=env)

        src_dir = os.path.dirname(src) or self.default_dir
        r_stem, _ = self._rad50_parts(src)
        if not obj_out:
            obj_out = os.path.join(src_dir, f"{r_stem}.OBJ")
        if want_default_lst and not lst_out:
            lst_out = os.path.join(src_dir, f"{r_stem}.LST")

        cmd = [apl_bin, self._rel_to_cwd(src), "-o", self._rel_to_cwd(obj_out)]
        if lst_out:
            cmd.extend(["-l", self._rel_to_cwd(lst_out)])
        return subprocess.call(cmd, cwd=self.default_dir, env=env)

    def _cmd_link(self, rest):
        tokens = []
        bin_out = None
        for t in rest.split():
            if t.upper().startswith("/OUTPUT=") or t.upper().startswith("/OUT="):
                bin_out = self.resolve_path(t.split("=", 1)[1])
            elif not self._is_dcl_qualifier(t):
                tokens.append(t)
        if not tokens:
            print("%DCL-E-NOFILE, missing object filename to link")
            return 1
        obj = self.resolve_path(tokens[0])
        if not os.path.isfile(obj):
            for ext_cand in (".OBJ", ".obj"):
                if os.path.isfile(obj + ext_cand):
                    obj = obj + ext_cand
                    break
        if not os.path.isfile(obj):
            print(f"?Can't find object module - {tokens[0]}")
            return 1
        if not bin_out:
            obj_dir = os.path.dirname(obj) or self.default_dir
            r_stem, _ = self._rad50_parts(obj)
            bin_out = os.path.join(obj_dir, f"{r_stem}.TSK")

        basiclink_bin = self.find_executable("basiclink")
        if not basiclink_bin:
            print("%BP2-F-NOLINK, native basiclink linker not found")
            return 1

        # Ensure rsts_vm is accessible in cwd or PATH for basiclink
        vm_bin = self.find_executable("rsts_vm")
        env = os.environ.copy()
        env["PATH"] = f"{self.sys_bin}:{env.get('PATH', '')}"
        vm_link = os.path.join(self.default_dir, "rsts_vm")
        created_vm_link = False
        if vm_bin and not os.path.exists(vm_link):
            try:
                os.symlink(vm_bin, vm_link)
                created_vm_link = True
            except OSError:
                pass
        try:
            rc = subprocess.call([basiclink_bin, "-o", bin_out, obj], cwd=self.default_dir, env=env)
        finally:
            if created_vm_link and os.path.islink(vm_link):
                os.unlink(vm_link)
        return rc

    def _compile_and_run_bas(self, bas_path, show_header=True):
        r_stem, _ = self._rad50_parts(bas_path)
        if show_header:
            now_str = datetime.now().strftime("%d-%b-%y %I:%M %p")
            print(f"{r_stem}   {now_str}")
        bas_dir = os.path.dirname(bas_path) or self.default_dir
        obj_path = os.path.join(bas_dir, f"{r_stem}.OBJ")
        bin_path = os.path.join(bas_dir, f"{r_stem}.TSK")
        rc = self._cmd_basic(f"{bas_path} /OBJECT={obj_path}")
        if rc != 0:
            return rc
        rc = self._cmd_link(f"{obj_path} /OUTPUT={bin_path}")
        if rc != 0:
            return rc
        return subprocess.call([bin_path], cwd=self.default_dir)

    def _compile_and_run_lang(self, src_path, bin_name, lang_label, default_exts):
        r_stem, _ = self._rad50_parts(src_path)
        src_dir = os.path.dirname(src_path) or self.default_dir
        obj_path = os.path.join(src_dir, f"{r_stem}.OBJ")
        tsk_path = os.path.join(src_dir, f"{r_stem}.TSK")
        rc = self._cmd_lang_compiler(bin_name, lang_label, default_exts, f"{src_path} /OBJECT={obj_path}")
        if rc != 0:
            return rc
        rc = self._cmd_link(f"{obj_path} /OUTPUT={tsk_path}")
        if rc != 0:
            return rc
        return subprocess.call([tsk_path], cwd=self.default_dir)

    def _cmd_run(self, rest):
        if not rest:
            print("%DCL-E-NOFILE, missing program to run")
            return 1
        parts = rest.split(None, 1)
        prog = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""

        # Check if user tried to RUN a VAX/VMS-only DECwindows image
        clean_upper = prog.upper()
        for prefix in ("SY:", "LB:", "SYS$SYSTEM:", "$"):
            if clean_upper.startswith(prefix):
                clean_upper = clean_upper[len(prefix):]
        clean_upper = os.path.splitext(clean_upper)[0]
        if clean_upper in self.UNSUPPORTED_VMS_APPS:
            print(
                f"?Unsupported OS facility '{clean_upper}' - DECwindows requires 32-bit VAX/VMS or ULTRIX "
                f"(not supported on 16-bit PDP-11 RSTS/E {self.VERSION})"
            )
            return 2

        # Check if it's a CCL app name (e.g. RUN LB:HAMURABI or RUN $SORT11)
        if clean_upper in self.ccl_table and "." not in prog:
            bname, _ = self.ccl_table[clean_upper]
            return self._invoke_app(bname, args_str)

        target = self.resolve_path(prog)
        if not os.path.isfile(target):
            for ext_cand in (
                ".TSK", ".tsk", ".BAC", ".bac", ".EXE", ".exe",
                ".BAS", ".bas", ".MAC", ".mac", ".CBL", ".cbl",
                ".FOR", ".for", ".DBL", ".dbl", ".RPG", ".rpg",
                ".APL", ".apl",
            ):
                cand = self.resolve_path(prog + ext_cand)
                if os.path.isfile(cand):
                    target = cand
                    break
        if os.path.isfile(target):
            up_t = target.upper()
            if up_t.endswith(".BAS"):
                return self._compile_and_run_bas(target)
            if up_t.endswith((".MAC", ".ASM")):
                return self._compile_and_run_lang(target, "macro11", "MACRO-11", (".MAC", ".mac"))
            if up_t.endswith((".CBL", ".COB")):
                return self._compile_and_run_lang(target, "cobol81", "COBOL-81", (".CBL", ".cbl"))
            if up_t.endswith((".FOR", ".FTN", ".F77")):
                return self._compile_and_run_lang(target, "fortran77", "FORTRAN-77", (".FOR", ".for"))
            if up_t.endswith((".DBL", ".DIB")):
                return self._compile_and_run_lang(target, "dibol83", "DIBOL-83", (".DBL", ".dbl"))
            if up_t.endswith(".RPG"):
                return self._compile_and_run_lang(target, "rpgii", "RPG II", (".RPG", ".rpg"))
            if up_t.endswith((".APL", ".AWS")):
                return self._compile_and_run_lang(target, "apl11", "APL-11", (".APL", ".apl"))
            if os.access(target, os.X_OK):
                cmd = [target] + (shlex.split(args_str) if args_str else [])
                return subprocess.call(cmd, cwd=self.default_dir)

        exe = self.find_executable(clean_upper.lower())
        if exe:
            return self._invoke_app(clean_upper.lower(), args_str)

        print(f"?Can't find runnable program - {prog}")
        return 1

    def _invoke_app(self, bin_name, args_str=""):
        exe = self.find_executable(bin_name)
        if not exe:
            print(f"?System library program LB:{bin_name.upper()}.TSK not found")
            return 1
        env = os.environ.copy()
        env["PATH"] = f"{self.sys_bin}:{env.get('PATH', '')}"
        cmd = [exe]
        if args_str:
            for tok in shlex.split(args_str):
                up = tok.upper()
                if up.startswith(("SY:", "LB:", "DK0:", "[")):
                    resolved = self.resolve_path(tok)
                    if os.path.dirname(resolved) == self.default_dir:
                        cmd.append(os.path.basename(resolved))
                    else:
                        cmd.append(resolved)
                else:
                    cmd.append(tok)
        return subprocess.call(cmd, cwd=self.default_dir, env=env)

    def _cmd_print(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if not tokens:
            print("%DCL-E-NOFILE, missing filename to print")
            return 1
        target = self.resolve_path(tokens[0])
        cmd = [sys.executable, self.job_controller, "submit-print", target]
        for t in rest.split():
            up = t.upper()
            if up.startswith("/QUEUE="):
                cmd.extend(["--queue", t.split("=", 1)[1]])
            elif up.startswith("/NAME="):
                cmd.extend(["--name", t.split("=", 1)[1]])
            elif up.startswith("/COPIES="):
                cmd.extend(["--copies", t.split("=", 1)[1]])
            elif up == "/DELETE":
                cmd.append("--delete")
        return subprocess.call(cmd)

    def _cmd_submit(self, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if not tokens:
            print("%DCL-E-NOFILE, missing command procedure filename")
            return 1
        target = self.resolve_path(tokens[0])
        cmd = [sys.executable, self.job_controller, "submit-batch", target]
        for t in rest.split():
            up = t.upper()
            if up.startswith("/QUEUE="):
                cmd.extend(["--queue", t.split("=", 1)[1]])
            elif up.startswith("/NAME="):
                cmd.extend(["--name", t.split("=", 1)[1]])
            elif up.startswith("/LOG="):
                cmd.extend(["--log", t.split("=", 1)[1]])
        return subprocess.call(cmd)

    def _cmd_queue_ctl(self, action, rest):
        tokens = [t for t in rest.split() if not t.startswith("/")]
        if not tokens:
            print("%DCL-E-PARAM, missing queue name")
            return 1
        return subprocess.call([sys.executable, self.job_controller, action, tokens[0]])


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="DEC RSTS/E V10.1-L Operating System Emulation Monitor"
    )
    parser.add_argument("-c", "--command", help="Execute RSTS/E command(s) (semicolon-separated) and exit")
    parser.add_argument("-u", "--user", default="1,2", help="Initial PPN or username for -c / --no-login (default: 1,2 / SYSTEM)")
    parser.add_argument("--login", action="store_true", default=True, help="Prompt for interactive PPN User/Password login (default)")
    parser.add_argument("--no-login", action="store_true", help="Skip login prompt and start directly in --user account")
    parser.add_argument("--boot", action="store_true", help="Display PDP-11/70 INIT.SYS bootstrap sequence")
    parser.add_argument("--multiuser", action="store_true", help="Start multi-user SSH and HTTPS VT100 terminal daemons")
    parser.add_argument("--root", default=None, help="Virtual disk root directory (DK0:)")
    parser.add_argument("script", nargs="?", default=None, help="Optional DCL command procedure (.COM) to execute")

    args = parser.parse_args()
    emu = RSTSEmulator(root_dir=args.root, current_ppn=args.user)

    if args.boot and args.command:
        emu.print_boot_sequence()

    if args.command:
        rc = 0
        for subcmd in args.command.split(";"):
            subcmd = subcmd.strip()
            if subcmd:
                rc = emu.execute_line(subcmd)
                if emu.exit_requested:
                    break
        sys.exit(rc)

    if args.script:
        script_arg = args.script[1:] if args.script.startswith("@") else args.script
        sys.exit(emu.execute_script(script_arg))

    if os.getpid() == 1 or args.multiuser or os.environ.get("RSTS_MULTIUSER") == "1":
        try:
            import multiuser_service
            emu_bin = os.path.join(emu.os_dir, "bin", "rsts-emu")
            multiuser_service.start_background_daemons(
                emu_bin_path=emu_bin,
                os_title="DEC RSTS/E V10.1-L — VT100 Web Terminal",
                header_title="DEC PDP-11/70 — RSTS/E V10.1-L Timesharing (KB1:-KB31:)",
                ssh_port=emu.ssh_port,
                https_port=emu.https_port,
            )
        except Exception:
            pass

    sys.exit(emu.run_interactive(require_login=not args.no_login, show_boot=args.boot))


if __name__ == "__main__":
    main()
