#!/usr/bin/env python3
"""
DEC VAX/VMS V5.5-2 Operating System Emulation Executive & DCL Environment
Digital Equipment Corporation 32-bit VAX Virtual Memory System

Provides:
  - Authentic VAXstation 4000 Model 90 / VAX-11/780 VMB.EXE & SYSBOOT.EXE bootstrap
  - SYSUAF User Identification Code (UIC) Accounts ([1,4] SYSTEM, [100,1] DECW, [200,200] GUEST)
  - Hierarchical ODS-2 Virtual Filesystem (DKA0:[SYSMGR], SYS$SYSTEM:, SYS$LIBRARY:, SYS$LOGIN:)
  - VMS File Versioning (;1, ;2, ...) and PURGE support
  - DCL Lexical Functions (F$TIME, F$USER, F$GETSYI, F$ENVIRONMENT, F$TRNLNM)
  - Full integration with DEC BASIC-PLUS-2 / VAX BASIC, EDT, PBS Queues, and 12 VMS-supported DEC-APPS
  - Native DECwindows XUI / OSF/Motif 1.1 Workstation Suite (all 11 X11 GUI apps + Session Manager)
  - OS compatibility enforcement (rejects 16-bit PDP-11 RSTS/E-only DIBS-11 / CTS-500 suite)
"""

import os
import re
import sys
import glob
import json
import shlex
import shutil
import subprocess
from datetime import datetime


class VMSEmulator:
    VERSION = "V5.5-2"
    NODE_NAME = "VAX01"
    HW_MODEL = "VAXstation 4000 Model 90 (KA49-A, NVAX CPU, 128 MB RAM)"

    DEFAULT_USERS = {
        "SYSTEM": {
            "username": "SYSTEM",
            "owner": "SYSTEM MANAGER",
            "account": "SYSTEM",
            "uic": "[1,4]",
            "password": "MANAGER",
            "privs": "CMKRNL,DETACH,OPER,SYSNAM,SYSPRV,BYPASS,SETPRV,WORLD,TMPMBX,NETMBX",
            "flags": "NODISUSER",
            "identifiers": ["SYSTEM", "OPER"],
            "dir_spec": "DKA0:[SYSMGR]",
            "dir_rel": "sys0/sysmgr",
            "quota": 250000,
        },
        "DECW": {
            "username": "DECW",
            "owner": "DECWINDOWS WORKSTATION",
            "account": "DECW",
            "uic": "[100,1]",
            "password": "MOTIF",
            "privs": "TMPMBX,NETMBX,GRPNAM",
            "flags": "NODISUSER",
            "identifiers": ["DECW$USERS"],
            "dir_spec": "DKA0:[DECW]",
            "dir_rel": "decw",
            "quota": 100000,
        },
        "GUEST": {
            "username": "GUEST",
            "owner": "TIMESHARING GUEST",
            "account": "USER",
            "uic": "[200,200]",
            "password": "",
            "privs": "TMPMBX,NETMBX",
            "flags": "NODISUSER",
            "identifiers": [],
            "dir_spec": "DKA0:[GUEST]",
            "dir_rel": "guest",
            "quota": 25000,
        },
    }

    # SYS$SYSTEM:DECW$* and VMS System Image Mapping
    VMS_SYSTEM_IMAGES = {
        "DECW$SESSION": "decwx11",
        "DECW$STARTLOGIN": "decwx11",
        "DECW$TERMINAL": "decterm",
        "DECW$DECTERM": "decterm",
        "DECW$BOOKREADER": "bookreader",
        "DECW$CALENDAR": "calendar",
        "DECW$CARDFILER": "cardfiler",
        "DECW$CDAVIEWER": "cdaviewer",
        "DECW$CALC": "calculator",
        "DECW$CALCULATOR": "calculator",
        "DECW$CLOCK": "clock",
        "DECW$SOUND": "decsound",
        "DECW$DECSOUND": "decsound",
        "DECW$MAIL": "dxmail",
        "VUE$MASTER": "fileview",
        "DECW$FILEVIEW": "fileview",
        "DECW$NOTEPAD": "notepad",
        "DTR32": "datatrieve11",
        "SORTMERGE": "sort11",
        "MAIL": "decmail",
        "EDT": "edt",
    }

    # Supported VAX/VMS DCL & Foreign Commands (12 DEC-APPS + Toolchain)
    SUPPORTED_VMS_APPS = {
        "HAMURABI": ("hamurabi", "Ancient Sumeria Economic Simulation (DECUS VAX BASIC)"),
        "SORT": ("sort11", "VAX/VMS SORT/MERGE Utility"),
        "SORT11": ("sort11", "DEC RMS File Sort & Index Utility"),
        "RMSUTILS": ("rmsutils", "DEC RMS File Utilities Suite"),
        "RMSDES": ("rmsdes", "RMS File Design Utility"),
        "RMSDEF": ("rmsdef", "RMS File Definition Utility"),
        "RMSIFL": ("rmsifl", "RMS Indexed File Load Utility"),
        "RMSCNV": ("rmscnv", "RMS File Conversion Utility"),
        "RMSBCK": ("rmsbck", "RMS File Backup Utility"),
        "RMSRST": ("rmsrst", "RMS File Restore Utility"),
        "RMSDSP": ("rmsdsp", "RMS File Display Utility"),
        "ADE": ("ade", "VAX Application Development Environment V3.0 (4GL)"),
        "DATATRIEVE": ("datatrieve11", "VAX DATATRIEVE V3.0 Query & Report System"),
        "DATATRIEVE11": ("datatrieve11", "DEC DATATRIEVE V3.0 Query & Report System"),
        "DTR": ("datatrieve11", "VAX DATATRIEVE V3.0 Query & Report System"),
        "DTR11": ("datatrieve11", "DEC DATATRIEVE V3.0 Query & Report System"),
        "DECGRAPH": ("decgraph", "VAX DECgraph V3.0 Presentation Graphics System"),
        "GRAPH": ("decgraph", "VAX DECgraph V3.0 Presentation Graphics System"),
        "DECG": ("decgraph", "VAX DECgraph V3.0 Presentation Graphics System"),
        "MAIL": ("decmail", "VAX/VMS Personal Mail Utility V3.0"),
        "DECMAIL": ("decmail", "VAX/VMS Personal Mail Utility V3.0"),
        "DECWORD": ("decword", "WPS-PLUS / DECword V3.0 Word Processing System"),
        "WPS": ("decword", "WPS-PLUS / DECword V3.0 Word Processing System"),
        "FMS": ("fms11", "VAX FMS V2.0 Forms Management System"),
        "FMS11": ("fms11", "DEC Forms Management System V2.0"),
        "FED": ("fms11", "VAX FMS Form Editor"),
        "FDV": ("fms11", "VAX FMS Form Driver"),
        "MENU": ("menu11", "VAX/VMS Menu Control & Dispatch Facility"),
        "MENU11": ("menu11", "DEC Menu Control Facility V2.0"),
        "MCF": ("menu11", "DEC Menu Control Facility V2.0"),
        "INDENT": ("indent", "VAX BASIC / BASIC-PLUS-2 Source Formatter"),
        "BP2FMT": ("indent", "VAX BASIC / BASIC-PLUS-2 Source Formatter"),
        "PRETTY": ("indent", "VAX BASIC / BASIC-PLUS-2 Pretty-Printer"),
        "EDT": ("edt", "VAX/VMS EDT Interactive Text Editor V3.0"),
        # DECwindows Workstation Suite (Native to VAX/VMS)
        "DECWINDOWS": ("decwindows", "VAX/VMS DECwindows Motif Workstation Suite"),
        "DECWX11": ("decwx11", "DECwindows XUI / OSF/Motif 1.1 Session Manager"),
        "DXSESSION": ("dxsession", "DECwindows XUI / OSF/Motif 1.1 Session Manager"),
        "DECW_X11": ("decw_x11", "DECwindows Native X11 Protocol Engine"),
        "DECTERM": ("decterm", "DECwindows DECterm VT300 Terminal Emulator"),
        "DXTERM": ("dxterm", "DECwindows DECterm VT300 Terminal Emulator"),
        "BOOKREADER": ("bookreader", "DECwindows Bookreader Hypertext Online Documentation"),
        "DXBOOK": ("dxbook", "DECwindows Bookreader Hypertext Online Documentation"),
        "CALENDAR": ("calendar", "DECwindows Calendar & Engineering Time Manager"),
        "DXCALENDAR": ("dxcalendar", "DECwindows Calendar & Engineering Time Manager"),
        "CARDFILER": ("cardfiler", "DECwindows Cardfiler Index Card Manager"),
        "DXCARDFILER": ("dxcardfiler", "DECwindows Cardfiler Index Card Manager"),
        "CDAVIEWER": ("cdaviewer", "DECwindows CDA DDIF/DTIF Compound Document Viewer"),
        "DXVDOC": ("dxvdoc", "DECwindows CDA DDIF/DTIF Compound Document Viewer"),
        "CALCULATOR": ("calculator", "DECwindows Scientific/Financial/Hex Calculator"),
        "DXCALC": ("dxcalc", "DECwindows Scientific/Financial/Hex Calculator"),
        "CLOCK": ("clock", "DECwindows Workstation Analog/Digital Clock"),
        "DXCLOCK": ("dxclock", "DECwindows Workstation Analog/Digital Clock"),
        "DECSOUND": ("decsound", "DECwindows VAXstation Audio Recorder/Player"),
        "DXSOUND": ("dxsound", "DECwindows VAXstation Audio Recorder/Player"),
        "DXMAIL": ("dxmail", "DECwindows Motif Three-Pane Mail Cabinet"),
        "DECWINMAIL": ("decwinmail", "DECwindows Motif Three-Pane Mail Cabinet"),
        "FILEVIEW": ("fileview", "DECwindows FileView Graphical File Manager (VUE$MASTER)"),
        "DXFILEVIEW": ("dxfileview", "DECwindows FileView Graphical File Manager"),
        "NOTEPAD": ("notepad", "DECwindows Notepad Motif Text Editor"),
        "DXNOTEPAD": ("dxnotepad", "DECwindows Notepad Motif Text Editor"),
    }

    # Applications strictly built for 16-bit PDP-11 CTS-300/CTS-500 RSTS/E (NOT supported on VAX/VMS)
    UNSUPPORTED_PDP11_APPS = {
        "DIBS",
        "DIBS11",
        "DIBS-11",
        "CTS300",
        "CTS500",
    }

    def __init__(self, root_dir=None, username="SYSTEM"):
        self.os_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.dec_root = os.path.abspath(os.path.join(self.os_dir, "..", ".."))
        self.sys_bin = self._locate_sys_bin()
        self.sys_lib = self._locate_sys_lib()
        self.job_controller = self._locate_job_controller()

        if root_dir is None:
            root_dir = os.environ.get("VMS_FS_ROOT", os.path.join(self.os_dir, "fs"))
        self.fs_root = os.path.abspath(root_dir)
        self.dka0_root = os.path.join(self.fs_root, "dka0")

        self.users = {k: dict(v) for k, v in self.DEFAULT_USERS.items()}
        self.current_user = self.normalize_user(username) or "SYSTEM"
        self.prompt = "$ "
        self.verify = False
        self.exit_requested = False
        self.logout_requested = False
        self._in_interactive_loop = False
        self.display_node = os.environ.get("DISPLAY", "LOCAL:0.0")
        self.pid = os.getpid()
        self.session_source = os.environ.get("DEC_SESSION_SOURCE", "SSH" if os.environ.get("SSH_CONNECTION") else "CONSOLE")
        self.ssh_port = int(os.environ.get("VMS_SSH_PORT", "2255"))
        self.https_port = int(os.environ.get("VMS_HTTPS_PORT", "8455"))
        self.sessions_path = os.path.join(self.fs_root, ".vms_sessions.json")
        self.vms_pid = "00000214"
        self.term_device = "OPA0:"

        self._init_filesystem()
        self._allocate_terminal_device()
        user_info = self.users[self.current_user]
        self.default_dir = self.get_user_dir(self.current_user)
        self.default_vms_spec = user_info["dir_spec"]

        self.symbols = {
            "$STATUS": "%X00000001",
            "$SEVERITY": "1",
            "SYS$NODE": f"{self.NODE_NAME}::",
            "P1": "",
            "P2": "",
            "P3": "",
            "P4": "",
        }
        self.logicals = {
            "SYS$SYSDEVICE": "DKA0:",
            "SYS$SYSROOT": os.path.join(self.dka0_root, "sys0"),
            "SYS$COMMON": os.path.join(self.dka0_root, "sys0", "syscommon"),
            "SYS$SYSTEM": os.path.join(self.dka0_root, "sys0", "syscommon", "sysexe"),
            "SYS$LIBRARY": os.path.join(self.dka0_root, "sys0", "syscommon", "syslib"),
            "SYS$MANAGER": os.path.join(self.dka0_root, "sys0", "sysmgr"),
            "SYS$HELP": os.path.join(self.dka0_root, "sys0", "syscommon", "syshlp"),
            "SYS$LOGIN": self.default_dir,
            "SYS$SCRATCH": self.default_dir,
            "SYS$DISK": "DKA0:",
            "SYS$INPUT": self.term_device,
            "SYS$OUTPUT": self.term_device,
            "SYS$ERROR": self.term_device,
            "DECW$DISPLAY": self.display_node,
        }

    def _locate_sys_bin(self):
        candidates = [
            os.path.join(self.os_dir, "system", "bin"),
            "/opt/dec-vms/system/bin",
            os.path.expanduser("~/.local/dec-basic2/bin"),
        ]
        for c in candidates:
            if os.path.isdir(c) and os.path.exists(os.path.join(c, "basicc")):
                return c
        return os.path.join(self.os_dir, "system", "bin")

    def _locate_sys_lib(self):
        candidates = [
            os.path.join(self.os_dir, "system", "lib"),
            "/opt/dec-vms/system/lib",
            os.path.join(self.dec_root, "APPS", "apps", "decwindows", "lib"),
        ]
        for c in candidates:
            if os.path.isdir(c):
                return c
        return os.path.join(self.os_dir, "system", "lib")

    def _locate_job_controller(self):
        candidates = [
            os.path.join(self.os_dir, "system", "lib", "dcl", "job_controller.py"),
            "/opt/dec-vms/system/lib/dcl/job_controller.py",
            os.path.join(self.dec_root, "LANG", "BASIC-PLUS-2", "dcl", "job_controller.py"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return candidates[0]

    def normalize_user(self, raw):
        if not raw:
            return None
        s = raw.strip().upper()
        if s in self.users:
            return s
        for uname, uinfo in self.users.items():
            if uinfo["uic"] == s or uinfo["uic"].strip("[]") == s.strip("[]"):
                return uname
        return None

    def get_user_dir(self, uname):
        u = self.users[uname]
        p = os.path.join(self.dka0_root, u["dir_rel"])
        os.makedirs(p, exist_ok=True)
        return p

    def _reload_sysuaf(self):
        sysexe_dir = os.path.join(self.dka0_root, "sys0", "syscommon", "sysexe")
        uaf_json = os.path.join(sysexe_dir, "SYSUAF.JSON")
        if os.path.exists(uaf_json):
            try:
                with open(uaf_json, "r") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.users.update(loaded)
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

    def _allocate_terminal_device(self):
        sessions = self._load_live_sessions()
        pid_key = str(self.pid)
        if pid_key in sessions:
            self.vms_pid = sessions[pid_key].get("vms_pid", "00000214")
            self.term_device = sessions[pid_key].get("term_device", "OPA0:")
            return
        used_pids = {s.get("vms_pid", "") for s in sessions.values()}
        used_terms = {s.get("term_device", "") for s in sessions.values()}

        if "OPA0:" not in used_terms:
            self.term_device = "OPA0:"
        else:
            for idx in range(1, 65):
                cand = f"FTA{idx}:"
                if cand not in used_terms:
                    self.term_device = cand
                    break

        num = 0x214
        while f"{num:08X}" in used_pids:
            num += 1
        self.vms_pid = f"{num:08X}"

    def _register_session(self, logged_in=True):
        sessions = self._load_live_sessions()
        uinfo = self.users.get(self.current_user, self.DEFAULT_USERS["SYSTEM"])
        sessions[str(self.pid)] = {
            "pid": self.pid,
            "vms_pid": self.vms_pid,
            "term_device": self.term_device,
            "username": self.current_user,
            "uic": uinfo["uic"],
            "logged_in": bool(logged_in),
            "source": self.session_source,
            "login_time": datetime.now().strftime("%d-%b-%Y %H:%M:%S.00"),
        }
        self._save_sessions(sessions)

    def _unregister_session(self):
        sessions = self._load_live_sessions()
        if str(self.pid) in sessions:
            sessions.pop(str(self.pid), None)
            self._save_sessions(sessions)

    def _save_sysuaf(self):
        sysexe_dir = os.path.join(self.dka0_root, "sys0", "syscommon", "sysexe")
        os.makedirs(sysexe_dir, exist_ok=True)
        uaf_json = os.path.join(sysexe_dir, "SYSUAF.JSON")
        with open(uaf_json, "w") as f:
            json.dump(self.users, f, indent=2)
        uaf_dat = os.path.join(sysexe_dir, "SYSUAF.DAT")
        with open(uaf_dat, "w") as f:
            for k, v in self.users.items():
                f.write(f"{v['username']}:{v['uic']}:{v.get('account','USER')}:{v['quota']}:{v['privs']}:{v['dir_spec']}\n")

    def _init_filesystem(self):
        for sub in (
            "sys0/syscommon/sysexe",
            "sys0/syscommon/syslib",
            "sys0/syscommon/syshlp",
            "sys0/sysmgr",
            "decw",
            "guest",
        ):
            os.makedirs(os.path.join(self.dka0_root, sub), exist_ok=True)

        sysexe_dir = os.path.join(self.dka0_root, "sys0", "syscommon", "sysexe")
        uaf_json = os.path.join(sysexe_dir, "SYSUAF.JSON")
        if os.path.exists(uaf_json):
            try:
                with open(uaf_json, "r") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.users.update(loaded)
                    for uname in self.users:
                        self.get_user_dir(uname)
            except Exception:
                pass
        self._save_sysuaf()

        sysmgr_dir = os.path.join(self.dka0_root, "sys0", "sysmgr")
        welcome_txt = os.path.join(sysmgr_dir, "WELCOME.TXT")
        if not os.path.exists(welcome_txt):
            with open(welcome_txt, "w") as f:
                f.write(
                    "========================================================================\n"
                    f"  Welcome to VAX/VMS {self.VERSION} on node {self.NODE_NAME}\n"
                    f"  Hardware: {self.HW_MODEL}\n"
                    "========================================================================\n"
                    "  System Logicals: SYS$SYSTEM:, SYS$LIBRARY:, SYS$MANAGER:, SYS$LOGIN:\n"
                    "  Workstation UI:  DECwindows XUI / OSF/Motif 1.1 (DXSESSION, DECTERM,\n"
                    "                   BOOKREADER, CALENDAR, CARDFILER, CDAVIEWER, CLOCK,\n"
                    "                   CALCULATOR, DECSOUND, DXMAIL, FILEVIEW, NOTEPAD)\n"
                )

        login_com = os.path.join(sysmgr_dir, "LOGIN.COM")
        if not os.path.exists(login_com):
            with open(login_com, "w") as f:
                f.write(
                    "$ ! VAX/VMS V5.5-2 System Manager Login Procedure DKA0:[SYSMGR]LOGIN.COM;1\n"
                    "$ WRITE SYS$OUTPUT \"VAX/VMS V5.5-2 SYSTEM [1,4] Session Ready on Node VAX01\"\n"
                )

        hello_bas = os.path.join(sysmgr_dir, "HELLO.BAS")
        if not os.path.exists(hello_bas):
            with open(hello_bas, "w") as f:
                f.write(
                    "10 ! VAX/VMS V5.5-2 VAX BASIC / BASIC-PLUS-2 Sample Program\n"
                    "20 PRINT \"HELLO FROM DEC VAX/VMS V5.5-2 ON VAXSTATION 4000!\"\n"
                    "30 END\n"
                )

        shutdown_com = os.path.join(sysexe_dir, "SHUTDOWN.COM")
        if not os.path.exists(shutdown_com):
            with open(shutdown_com, "w") as f:
                f.write(
                    "$ ! VAX/VMS V5.5-2 System Shutdown Procedure SYS$SYSTEM:SHUTDOWN.COM;1\n"
                    "$ SHUTDOWN\n"
                )

    def resolve_path(self, vms_spec):
        """Translate a VMS file specification (e.g. SYS$LOGIN:HELLO.BAS;1, DKA0:[SYSMGR]FILE.TXT) to host path."""
        if not vms_spec:
            return self.default_dir
        spec = vms_spec.strip().strip('"').strip("'")

        # Strip trailing VMS version number ;1, ;2 if present unless exact versioned file exists
        version_suffix = ""
        if ";" in spec:
            base_spec, ver_part = spec.rsplit(";", 1)
            if ver_part.isdigit() or ver_part in ("*", "0", "-1"):
                version_suffix = f";{ver_part}"
                spec = base_spec

        upper = spec.upper()

        # Check logical name prefixes: SYS$LOGIN:, SYS$SYSTEM:, SYS$MANAGER:, SYS$LIBRARY:
        for log_k, log_v in self.logicals.items():
            prefix = log_k.upper().rstrip(":") + ":"
            if upper.startswith(prefix):
                rest = spec[len(prefix):]
                if os.path.isdir(log_v):
                    return self._resolve_in_dir(log_v, rest, version_suffix)

        # Check DKA0:[DIR.SUBDIR]FILENAME.EXT or [DIR]FILENAME.EXT
        m = re.match(r"^(?:[A-Za-z0-9$_]+:)?\[([^\]]+)\](.*)$", spec)
        if m:
            dir_part, file_part = m.group(1), m.group(2)
            mapped_dir = self._map_vms_bracket_dir(dir_part)
            return self._resolve_in_dir(mapped_dir, file_part, version_suffix)

        if upper.startswith("DKA0:"):
            rest = spec[5:]
            return self._resolve_in_dir(self.default_dir, rest, version_suffix)

        if os.path.isabs(spec) or os.path.exists(spec):
            return os.path.abspath(spec)

        return self._resolve_in_dir(self.default_dir, spec, version_suffix)

    def _map_vms_bracket_dir(self, bracket_str):
        b = bracket_str.strip().upper()
        if b in ("SYSMGR", "SYS0.SYSMGR", "1,4", "001,004"):
            return os.path.join(self.dka0_root, "sys0", "sysmgr")
        if b in ("SYSEXE", "SYS0.SYSCOMMON.SYSEXE"):
            return os.path.join(self.dka0_root, "sys0", "syscommon", "sysexe")
        if b in ("SYSLIB", "SYS0.SYSCOMMON.SYSLIB"):
            return os.path.join(self.dka0_root, "sys0", "syscommon", "syslib")
        if b in ("DECW", "100,1"):
            return os.path.join(self.dka0_root, "decw")
        if b in ("GUEST", "200,200"):
            return os.path.join(self.dka0_root, "guest")
        rel = b.lower().replace(".", "/")
        p = os.path.join(self.dka0_root, rel)
        os.makedirs(p, exist_ok=True)
        return p

    def _resolve_in_dir(self, base_dir, rel_name, version_suffix=""):
        if not rel_name:
            return base_dir
        if version_suffix and os.path.exists(os.path.join(base_dir, rel_name + version_suffix)):
            return os.path.join(base_dir, rel_name + version_suffix)
        exact = os.path.join(base_dir, rel_name)
        if os.path.exists(exact):
            return exact
        if os.path.isdir(base_dir):
            for entry in os.listdir(base_dir):
                if entry.lower() == rel_name.lower():
                    return os.path.join(base_dir, entry)
        return exact

    def find_executable(self, name):
        clean = name.strip().lower()
        if clean.startswith("$"):
            clean = clean[1:]
        cand = os.path.join(self.sys_bin, clean)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
        which_res = shutil.which(clean)
        if which_res:
            return which_res
        return None

    def print_boot_sequence(self):
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S.%f")[:-4]
        print("KA49-A V1.2-342-V4.0   VAXstation 4000 Model 90")
        print(">>> BOOT DKA0")
        print("Initializing VMB.EXE / SYSBOOT.EXE from DKA0:[SYS0.SYSCOMMON.SYSEXE]...")
        print("")
        print(f"   VAX/VMS Version {self.VERSION}   Major version id = 1 Minor version id = 0")
        print("")
        print("%DECnet-I-LOADED, network executive loaded, node VAX01 (1.10)")
        print("%DECW-I-STARTED, DECwindows XUI / OSF/Motif V1.1 workstation server initialized")
        print(f"%SET-I-INTSET, login interactive limit = 64, current interactive value = 1")
        print(f"  SYSTEM       job terminated at {now_str} (Startup Completed)\n")

    def interactive_login(self, in_stream=None):
        stream = in_stream or sys.stdin
        self._register_session(logged_in=False)
        print(f"\n    Welcome to VAX/VMS {self.VERSION} on node {self.NODE_NAME}\n")
        while True:
            sys.stdout.write("Username: ")
            sys.stdout.flush()
            try:
                u_in = stream.readline()
            except KeyboardInterrupt:
                print("^C")
                continue
            if not u_in:
                self._unregister_session()
                return False
            if "\x03" in u_in:
                print("^C")
                continue
            u_in = u_in.strip()
            if not u_in:
                print(f"\n    Welcome to VAX/VMS {self.VERSION} on node {self.NODE_NAME}\n")
                continue
            if u_in.upper() in ("EXIT", "QUIT", "BYE", "LOGOUT", "\x04", "\x1a") and self.pid != 1:
                self._unregister_session()
                return False
            self._reload_sysuaf()
            uname = self.normalize_user(u_in)
            if not uname:
                print("%LOGIN-F-NOSUCHUSER, no such user")
                continue
            uinfo = self.users[uname]
            flags_list = [fl.strip().upper() for fl in uinfo.get("flags", "").split(",") if fl.strip()]
            if "DISUSER" in flags_list and "NODISUSER" not in flags_list:
                print("%LOGIN-F-DISUSER, account is disabled")
                continue
            if uinfo["password"]:
                sys.stdout.write("Password: ")
                sys.stdout.flush()
                try:
                    p_in = stream.readline()
                except KeyboardInterrupt:
                    print("^C")
                    continue
                if not p_in:
                    self._unregister_session()
                    return False
                if "\x03" in p_in:
                    print("^C")
                    continue
                p_in = p_in.strip()
                if p_in and p_in.upper() != uinfo["password"].upper():
                    print("%LOGIN-F-NOTVALID, user authorization failure")
                    continue
            self._switch_user(uname)
            self._register_session(logged_in=True)
            print(f"\n    Welcome to VAX/VMS {self.VERSION} on node {self.NODE_NAME}")
            print(f"    Last interactive login on {datetime.now().strftime('%A, %d-%b-%Y %H:%M')} at {self.term_device}")
            return True

    def _switch_user(self, uname):
        self.current_user = uname
        uinfo = self.users[uname]
        self.default_dir = self.get_user_dir(uname)
        self.default_vms_spec = uinfo["dir_spec"]
        self.logicals["SYS$LOGIN"] = self.default_dir
        self.logicals["SYS$SCRATCH"] = self.default_dir
        if self._in_interactive_loop:
            self._register_session(logged_in=True)

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
                    self._register_session(logged_in=True)
                    print(f"    Welcome to VAX/VMS {self.VERSION} on node {self.NODE_NAME}")
                    print(f"    Interactive session for {self.current_user} {self.users[self.current_user]['uic']} on {self.term_device} ({self.default_vms_spec})\n")

                self.logout_requested = False
                while not self.exit_requested and not self.logout_requested:
                    sys.stdout.write(self.prompt)
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
                    if line == "\x1a":
                        break
                    try:
                        self.execute_line(line)
                    except KeyboardInterrupt:
                        print("\n^C")

                # After LOGOUT / BYE, return terminal to the VAX/VMS Username: login prompt
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

    def _expand_lexicals(self, text):
        """Evaluate VMS DCL lexical functions like F$TIME(), F$USER(), F$GETSYI(), F$ENVIRONMENT(), F$TRNLNM()."""
        out = text
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S.00")
        out = re.sub(r"F\$TIME\(\s*\)", f'"{now_str}"', out, flags=re.IGNORECASE)
        out = re.sub(r"F\$USER\(\s*\)", f'"{self.users[self.current_user]["uic"]}"', out, flags=re.IGNORECASE)
        out = re.sub(r"F\$PROCESS\(\s*\)", f'"{self.current_user}"', out, flags=re.IGNORECASE)

        def repl_getsyi(m):
            arg = m.group(1).strip().strip('"').strip("'").upper()
            mapping = {
                "VERSION": self.VERSION,
                "NODENAME": self.NODE_NAME,
                "ARCH_NAME": "VAX",
                "HW_NAME": self.HW_MODEL,
            }
            return f'"{mapping.get(arg, self.VERSION)}"'

        out = re.sub(r"F\$GETSYI\(([^)]+)\)", repl_getsyi, out, flags=re.IGNORECASE)

        def repl_env(m):
            arg = m.group(1).strip().strip('"').strip("'").upper()
            if arg == "DEFAULT":
                return f'"{self.default_vms_spec}"'
            return f'"{self.VERSION}"'

        out = re.sub(r"F\$ENVIRONMENT\(([^)]+)\)", repl_env, out, flags=re.IGNORECASE)

        def repl_trnlnm(m):
            arg = m.group(1).strip().strip('"').strip("'").upper().rstrip(":")
            val = self.logicals.get(arg, self.logicals.get(arg + ":", ""))
            return f'"{val}"'

        out = re.sub(r"F\$TRNLNM\(([^)]+)\)", repl_trnlnm, out, flags=re.IGNORECASE)
        return out

    def execute_line(self, line):
        s = line.strip()
        if not s:
            return 0
        if s.startswith("$"):
            s = s[1:].strip()
        if not s or s.startswith("!"):
            return 0

        s = self._expand_lexicals(s)

        for sym_k, sym_v in self.symbols.items():
            token = f"'{sym_k}'"
            if token in s:
                s = s.replace(token, sym_v)

        if s.startswith("@"):
            return self.execute_script(s[1:].strip())

        if s.upper().startswith("IF ") and " THEN " in s.upper():
            idx = s.upper().index(" THEN ")
            cond = s[3:idx].strip()
            then_stmt = s[idx + 6:].strip()
            if self._eval_dcl_cond(cond):
                return self.execute_line(then_stmt)
            return 0

        # Symbol assignment: VAR = VAL or VAR := VAL
        if "=" in s and not s.split("=", 1)[0].strip().startswith("/"):
            lhs = s.split("=", 1)[0].rstrip(":").strip()
            if lhs and " " not in lhs and "/" not in lhs:
                rhs = s.split("=", 1)[1].strip().strip('"').strip("'")
                self.symbols[lhs.upper()] = rhs
                return 0

        first_word = s.split(None, 1)[0]
        rest = s.split(None, 1)[1].strip() if len(s.split(None, 1)) > 1 else ""
        if "/" in first_word:
            v_part, q_part = first_word.split("/", 1)
            verb = v_part.upper()
            rest = f"/{q_part} {rest}".strip()
        else:
            verb = first_word.upper()

        # Check if user attempted to invoke PDP-11 RSTS/E-only DIBS-11 / CTS-500
        if verb in self.UNSUPPORTED_PDP11_APPS:
            print(
                f"%DCL-W-UNSUPOS, '{verb}' (DIBS-11 / CTS-300/CTS-500) is a 16-bit PDP-11 RSTS/E commercial package "
                f"not supported under 32-bit VAX/VMS {self.VERSION}"
            )
            self.symbols["$STATUS"] = "%X00038090"
            return 2

        if verb in ("HELP", "MAN"):
            return self._cmd_help(rest)
        if verb == "SHOW":
            return self._cmd_show(rest)
        if verb == "SET":
            return self._cmd_set(rest)
        if verb in ("LOGIN", "HELLO"):
            return self._cmd_login(rest)
        if verb in ("LOGOUT", "BYE", "LOGOFF"):
            print(f"  {self.current_user:<12} logged out at {datetime.now().strftime('%d-%b-%Y %H:%M:%S.00')}")
            if "/DISCONNECT" in rest.upper() and self.pid != 1:
                self.exit_requested = True
            elif self._in_interactive_loop:
                self._register_session(logged_in=False)
                self.logout_requested = True
            else:
                self.exit_requested = True
            return 0
        if verb in ("SHUTDOWN", "HALT", "OPCCRASH"):
            u_privs = self.users[self.current_user].get("privs", "").upper()
            if not any(p in u_privs for p in ("SYSPRV", "OPER", "SETPRV", "CMKRNL")) and self.current_user != "SYSTEM":
                print("%SYSTEM-F-NOPRIV, insufficient privilege or object protection violation")
                self.symbols["$STATUS"] = "%X00000024"
                return 1
            print("%SHUTDOWN-I-BOOTCHECK, performing reboot consistency check...")
            print("%SHUTDOWN-I-OPERATOR, this terminal is now an operator's console")
            print(f"%SHUTDOWN-I-DISMOUNT, dismounting {self.NODE_NAME}$DKA0:")
            print(f"%OPCOM-S-SYSHUT, VAX/VMS {self.VERSION} shutdown completed on node {self.NODE_NAME}")
            print("SYSTEM SHUTDOWN COMPLETE - USE CONSOLE TO HALT SYSTEM")
            print(">>> HALT")
            self.exit_requested = True
            return 0
        if verb == "EXIT":
            return 0
        if verb == "QUIT":
            print("%DCL-I-LOGOUT, use LOGOUT or BYE to end terminal session, or SHUTDOWN to halt system")
            return 0
        if verb in ("DIR", "DIRECTORY"):
            return self._cmd_dir(rest)
        if verb == "TYPE":
            return self._cmd_type(rest)
        if verb == "COPY":
            return self._cmd_copy(rest)
        if verb == "RENAME":
            return self._cmd_rename(rest)
        if verb == "DELETE":
            return self._cmd_delete(rest)
        if verb == "PURGE":
            return self._cmd_purge(rest)
        if verb == "CREATE":
            return self._cmd_create(rest)
        if verb == "MODIFY":
            return self._cmd_modify(rest)
        if verb == "SEARCH":
            return self._cmd_search(rest)
        if verb in ("DIFF", "DIFFERENCES"):
            return self._cmd_diff(rest)
        if verb == "ANALYZE":
            return self._cmd_analyze(rest)
        if verb == "CONVERT":
            return self._invoke_app("rmscnv", rest)
        if verb in ("AUTHORIZE", "UAF"):
            return self._cmd_authorize(rest, interactive_uaf=(verb == "UAF"))
        if verb == "MCR":
            if rest.strip().upper().startswith("AUTHORIZE"):
                sub_rest = rest.strip()[9:].strip()
                return self._cmd_authorize(sub_rest, interactive_uaf=not bool(sub_rest))
            return self.execute_line(rest)
        if verb == "MONITOR":
            return self._cmd_monitor(rest)
        if verb == "SYSMAN":
            return self._cmd_sysman(rest)
        if verb in ("DEFINE", "ASSIGN"):
            return self._cmd_define(verb, rest)
        if verb == "DEASSIGN":
            return self._cmd_deassign(rest)
        if verb in ("WRITE", "ECHO"):
            return self._cmd_write(rest)
        if verb in ("BASIC", "COMPILE"):
            return self._cmd_basic(rest)
        if verb == "LINK":
            return self._cmd_link(rest)
        if verb == "RUN":
            return self._cmd_run(rest)
        if verb == "EDIT":
            return self._cmd_edit(rest)
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

        if verb in self.SUPPORTED_VMS_APPS:
            bin_name, _ = self.SUPPORTED_VMS_APPS[verb]
            return self._invoke_app(bin_name, rest)

        exe = self.find_executable(verb)
        if exe:
            return self._invoke_app(verb.lower(), rest)

        print(f"%DCL-W-IVVERB, unrecognized command verb - check validity and spelling\n \\{verb}\\")
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

    def _is_dcl_qualifier(self, token):
        if not token.startswith("/"):
            return False
        if os.path.exists(token) or token.count("/") > 1:
            return False
        return True

    # ==========================================================================
    # VAX/VMS System & File Commands
    # ==========================================================================
    def _cmd_help(self, rest):
        topic = rest.strip().upper()
        if not topic:
            print(
                "==============================================================================\n"
                f"  DEC VAX/VMS {self.VERSION} DIGITAL Command Language (DCL) Help Library\n"
                "==============================================================================\n"
                "  System Management & Information:\n"
                "    LOGIN / HELLO      Switch interactive SYSUAF user session\n"
                "    LOGOUT / BYE       Log off current user session and return to OPA0: Username: prompt\n"
                "    SHUTDOWN / HALT    Privileged VAX/VMS system shutdown (halts OS/container)\n"
                "    SHOW SYSTEM        Display active VMS processes, PIDs, states, and pages\n"
                "    SHOW DEVICES       Display DKA0:, MKA0:, OPA0:, FTA0:, WSA0: device table\n"
                "    SHOW MEMORY        Display VAX physical memory, pagefile, and swapfile\n"
                "    SHOW CPU           Display VAXstation 4000 Model 90 processor status\n"
                "    SHOW PROCESS       Display current process UIC, privileges, and quotas\n"
                "    SHOW LOGICAL       Display LNM$SYSTEM_TABLE and process logical names\n"
                "    SHOW DECWINDOWS    Display DECwindows Motif X11 server & 11 GUI apps\n"
                "    SHOW APPS          Display all installed VAX/VMS layered products\n"
                "    SHOW ACCOUNT       Display SYSUAF user accounts (supports /FULL)\n"
                "    AUTHORIZE          VMS Authorize Utility (UAF>: ADD, MODIFY, REMOVE, SHOW, GRANT)\n"
                "    CREATE/ACCOUNT     Create SYSUAF user account (/UIC=, /PASSWORD=, /PRIV=, /QUOTA=)\n"
                "    MODIFY/ACCOUNT     Modify SYSUAF user account (or SET ACCOUNT)\n"
                "    DELETE/ACCOUNT     Remove non-system user account from SYSUAF.DAT\n"
                "    SET PASSWORD       Change SYSUAF account password (/PASSWORD=, /GENERATE)\n"
                "    MONITOR / SYSMAN   VMS System Performance Monitor & System Management\n"
                "\n"
                "  ODS-2 Filesystem & Version Management:\n"
                "    DIRECTORY [spec]   List files with VMS version numbers (;1, ;2)\n"
                "    PURGE [spec]       Delete older file versions, keeping highest version\n"
                "    TYPE / COPY / RENAME / DELETE / CREATE / SEARCH / DIFFERENCES\n"
                "    SET DEFAULT <dir>  Change default device/directory (e.g. DKA0:[SYSMGR])\n"
                "    DEFINE <log> <val> Define logical name\n"
                "\n"
                "  Compilers, Layered Products & DECwindows Workstation Suite:\n"
                "    BASIC / LINK / RUN / EDIT (EDT) / SUBMIT / PRINT / ANALYZE/RMS_FILE\n"
                "    SORT, RMSUTILS, ADE, DATATRIEVE (DTR), DECGRAPH, MAIL (DECMAIL),\n"
                "    DECWORD (WPS), FMS, MENU, INDENT, HAMURABI\n"
                "    DECWINDOWS, DXSESSION, DECTERM, BOOKREADER, CALENDAR, CARDFILER,\n"
                "    CDAVIEWER, CALCULATOR, CLOCK, DECSOUND, DXMAIL, FILEVIEW, NOTEPAD\n"
                "    RUN SYS$SYSTEM:DECW$CLOCK (and all SYS$SYSTEM:DECW$* images)\n"
            )
            return 0
        if topic in self.SUPPORTED_VMS_APPS:
            bname, desc = self.SUPPORTED_VMS_APPS[topic]
            print(f"{topic} — {desc} (SYS$SYSTEM:{bname.upper()}.EXE)")
            return 0
        print(f"VAX/VMS Help Topic '{topic}': Type HELP for full DCL Dictionary summary.")
        return 0

    def _cmd_show(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        quals = [t.upper() for t in rest.split() if self._is_dcl_qualifier(t)]
        if not tokens:
            print("%DCL-E-PARAM, missing SHOW parameter")
            return 1
        sub = tokens[0].upper()
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S.00")
        uinfo = self.users[self.current_user]

        if sub in ("SYSTEM", "SYS"):
            sessions = self._load_live_sessions()
            active = [s for s in sessions.values() if s.get("logged_in")]
            if not any(s.get("pid") == self.pid for s in active):
                active.append({
                    "vms_pid": self.vms_pid,
                    "username": self.current_user,
                    "term_device": self.term_device,
                })
            active.sort(key=lambda x: x.get("vms_pid", "00000214"))
            print(f"VAX/VMS {self.VERSION} on node {self.NODE_NAME}   {now_str}   Uptime  0 02:15:40")
            print("  Pid    Process Name    State  Pri      I/O       CPU       Page flts Ph.Mem")
            print("00000201 SWAPPER         HIB     16        0   0 00:00:00.12         0      0")
            print("00000204JOB_CONTROL     HIB     10      142   0 00:00:00.45       180    320")
            print("00000206SYMBIONT_0001   HIB      6       88   0 00:00:00.21       110    240")
            print("00000208 DECW$SERVER_0   LEF      8     1420   0 00:00:03.80       950   2480")
            for s in active:
                st = "CUR" if s.get("pid") == self.pid else "LEF"
                print(f"{s['vms_pid']} {s['username']:<15} {st}      4      310   0 00:00:01.05       412    640")
            return 0
        if sub in ("DEVICES", "DEV", "DEVICE"):
            print(f"Device                  Device           Error    Volume         Free  Trans Mnt")
            print(f" Name                   Status           Count     Label        Blocks Count Cnt")
            print(f"VAX01$DKA0:             Mounted              0  VMS55_SYS       418920    14   1")
            print(f"VAX01$MKA500:           Online               0")
            print(f"VAX01$OPA0:             Online               0  (Operator Console)")
            print(f"VAX01$FTA1:             Online               0  (Multi-User SSH/HTTPS Pseudo-Terminal)")
            print(f"VAX01$WSA0:             Online               0  (DECwindows X11 Display {self.display_node})")
            return 0
        if sub in ("MEMORY", "MEM"):
            print(f"              System Memory Resources on {now_str}")
            print("Physical Memory Usage (pages):     Total        Free      In Use    Modified")
            print("  Main Memory (128.00Mb)          262144      218400       42144        1600")
            print("Paging File Usage (blocks):         Free  Reservable       Total")
            print("  DISK$VMS55:[SYS0.SYSEXE]SWAPFILE.SYS")
            print("                                   32000       32000       36000")
            print("  DISK$VMS55:[SYS0.SYSEXE]PAGEFILE.SYS")
            print("                                  110000      110000      128000")
            return 0
        if sub == "CPU":
            print(f"VAX01, a {self.HW_MODEL}")
            print("Multiprocessing is DISABLED. Uniprocessor System.")
            print("PRIMARY CPU = 00")
            print("Active CPUs:      00")
            print("Configured CPUs:  00")
            return 0
        if sub in ("USERS", "USER"):
            sessions = self._load_live_sessions()
            active = [s for s in sessions.values() if s.get("logged_in")]
            if not any(s.get("pid") == self.pid for s in active):
                active.append({
                    "vms_pid": self.vms_pid,
                    "username": self.current_user,
                    "term_device": self.term_device,
                    "source": self.session_source,
                })
            active.sort(key=lambda x: x.get("vms_pid", "00000214"))
            print(f"      VAX/VMS Interactive Users on {now_str}")
            print(f"    Total number of interactive users = {len(active)}")
            print(" Username     Process Name      PID     Terminal")
            for s in active:
                print(f" {s['username']:<12} {s['username']:<17} {s['vms_pid']}  {s['term_device']} ({s.get('source', 'WSA0:')})")
            return 0
        if sub in ("PROCESS", "PROC"):
            print(f"{now_str}   User: {self.current_user:<12}   Process ID:   {self.vms_pid}")
            print(f"                          Node: {self.NODE_NAME:<12}   Process name: \"{self.current_user}\"")
            print(f"Terminal:           {self.term_device} ({self.session_source} / DECwindows WSA0:)")
            print(f"User Identifier:    {uinfo['uic']}")
            print(f"Base priority:      4")
            print(f"Default file spec:  {self.default_vms_spec} ({self.default_dir})")
            print(f"Process privileges: {uinfo['privs']}")
            return 0
        if sub in ("TIME", "DATE"):
            print(f"  {now_str}")
            return 0
        if sub in ("DEFAULT", "DEF"):
            print(f"  {self.default_vms_spec}   ({self.default_dir})")
            return 0
        if sub in ("QUOTA", "QUOTAS"):
            print(f"User {uinfo['uic']} ({self.current_user}) has 1240 blocks used, {uinfo['quota']} available,")
            print(f"of {uinfo['quota']} authorized and permitted overdraft of 1000 blocks on DKA0:")
            return 0
        if sub in ("LOGICAL", "LOGICALS", "TRANSLATION"):
            print("(LNM$PROCESS_TABLE & LNM$SYSTEM_TABLE)")
            for k, v in self.logicals.items():
                print(f'  "{k}" = "{v}"')
            return 0
        if sub in ("SYMBOL", "SYMBOLS"):
            for k, v in self.symbols.items():
                print(f'  {k} = "{v}"')
            return 0
        if sub in ("DISPLAY", "DECWINDOWS", "MOTIF"):
            print("DECwindows Workstation Display & OSF/Motif 1.1 Environment:")
            print(f"  Device:        WSA0: -> {self.display_node}")
            print(f"  Library:       SYS$LIBRARY:LIBDECW_X11.SO ({self.sys_lib})")
            print("  Applications:  DECW$SESSION (dxsession), DECW$DECTERM (decterm),")
            print("                 DECW$BOOKREADER (bookreader), DECW$CALENDAR (calendar),")
            print("                 DECW$CARDFILER (cardfiler), DECW$CDAVIEWER (cdaviewer),")
            print("                 DECW$CALC (calculator), DECW$CLOCK (clock),")
            print("                 DECW$SOUND (decsound), DECW$MAIL (dxmail),")
            print("                 VUE$MASTER (fileview), DECW$NOTEPAD (notepad)")
            return 0
        if sub in ("APPS", "APPLICATIONS", "PRODUCTS", "UTILITIES"):
            print(f"VAX/VMS {self.VERSION} Installed Layered Products & Utilities (SYS$SYSTEM:):")
            print("----------------------------------------------------------------------------")
            seen = set()
            for cmd, (bname, desc) in sorted(self.SUPPORTED_VMS_APPS.items()):
                if bname not in seen:
                    seen.add(bname)
                    print(f"  {cmd:<14} (SYS$SYSTEM:{bname.upper():<12}.EXE) - {desc}")
            print("----------------------------------------------------------------------------")
            print("Note: PDP-11 RSTS/E-only DIBS-11 (CTS-500) is excluded under 32-bit VAX/VMS.")
            return 0
        if sub in ("NETWORK", "NET", "CLUSTER", "MULTIUSER"):
            print(f"DECnet Phase IV Status for Node {self.NODE_NAME} (1.10): State = ON, Routing = Area")
            print(f"Multi-User Terminal Server: SSH on port {self.ssh_port} (FTA1:-FTA64:), HTTPS Web VT220 on port {self.https_port}")
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
        if sub in ("ACCOUNT", "ACCOUNTS", "UAF"):
            target = tokens[1] if len(tokens) > 1 else "*"
            full_q = "/FULL" if ("/FULL" in quals or "/ALL" in quals) else "/BRIEF"
            return self._uaf_show(target, full=("/FULL" in full_q))

        print(f"%DCL-W-IVKEYW, unrecognized keyword - check validity and spelling\n \\{sub}\\")
        return 1

    def _cmd_set(self, rest):
        expanded = []
        for raw_tok in rest.split():
            if "/" in raw_tok and not raw_tok.startswith("/") and not os.path.exists(raw_tok):
                parts = raw_tok.split("/")
                expanded.append(parts[0])
                for p in parts[1:]:
                    expanded.append("/" + p)
            elif raw_tok.startswith("/") and raw_tok.count("/") > 1 and not os.path.exists(raw_tok):
                for p in raw_tok.lstrip("/").split("/"):
                    expanded.append("/" + p)
            else:
                expanded.append(raw_tok)
        tokens = [t for t in expanded if not self._is_dcl_qualifier(t)]
        quals = [t for t in expanded if self._is_dcl_qualifier(t)]
        if not tokens:
            print("%DCL-E-PARAM, missing SET parameter")
            return 1
        opt = tokens[0].upper()
        if opt in ("DEFAULT", "DEF"):
            if len(tokens) < 2:
                print("%DCL-E-PARAM, missing directory specification")
                return 1
            spec = tokens[1]
            resolved = self.resolve_path(spec)
            if os.path.isdir(resolved):
                self.default_dir = resolved
                self.default_vms_spec = spec.upper() if "[" in spec else f"DKA0:[{ os.path.basename(resolved).upper() }]"
                self.logicals["SYS$LOGIN"] = resolved
                return 0
            print(f"%SET-E-DIRNOTFND, directory {spec} not found")
            return 1
        if opt == "PROMPT":
            for q in quals:
                if "=" in q:
                    self.prompt = q.split("=", 1)[1].strip('"').strip("'")
            if len(tokens) > 1:
                self.prompt = tokens[1].strip('"').strip("'")
            return 0
        if opt == "PROCESS":
            for q in quals:
                if q.upper().startswith("/NAME="):
                    print(f"%SET-I-PROCNAME, process name set to {q.split('=', 1)[1]}")
            return 0
        if opt == "DISPLAY":
            for q in quals:
                if q.upper().startswith("/NODE="):
                    node = q.split("=", 1)[1].strip('"')
                    self.display_node = f"{node}:0.0" if ":" not in node else node
                    self.logicals["DECW$DISPLAY"] = self.display_node
            print(f"%DECW-I-DISSET, DECwindows display WSA0: routed to {self.display_node}")
            return 0
        if opt == "VERIFY":
            self.verify = True
            return 0
        if opt == "NOVERIFY":
            self.verify = False
            return 0
        if opt in ("ACCOUNT", "ACCOUNTS"):
            sub_rest = " ".join(tokens[1:] + quals)
            return self._uaf_modify(sub_rest)
        if opt == "PASSWORD":
            target_u = self.current_user
            new_pw = "VMS$PASS99"
            for q in quals:
                qu = q.upper()
                if qu.startswith("/USER=") or qu.startswith("/ACCOUNT="):
                    target_u = q.split("=", 1)[1].strip('"').upper()
                elif qu.startswith("/PASSWORD=") or qu.startswith("/NEW="):
                    new_pw = q.split("=", 1)[1].strip('"')
                elif qu == "/GENERATE":
                    new_pw = "VAX$8492"
            if len(tokens) > 1:
                cand_u = self.normalize_user(tokens[1])
                if cand_u:
                    target_u = cand_u
                    if len(tokens) > 2:
                        new_pw = tokens[2]
                else:
                    new_pw = tokens[1]
            uname = self.normalize_user(target_u)
            if not uname:
                print(f"%SET-E-NOSUCHUSER, user {target_u} not found in SYSUAF.DAT")
                return 1
            self.users[uname]["password"] = str(new_pw)
            self._save_sysuaf()
            print(f"%SET-S-PASSCHG, password updated for SYSUAF user {uname} ({self.users[uname]['uic']})")
            return 0
        return 0

    def _cmd_login(self, rest):
        if not rest:
            print(f"Currently logged in as {self.current_user} {self.users[self.current_user]['uic']}")
            return 0
        uname = self.normalize_user(rest.split()[0])
        if not uname:
            print(f"%LOGIN-F-NOSUCHUSER, no such user '{rest}'")
            return 1
        self._switch_user(uname)
        print(f"%LOGIN-S-LOGGEDIN, switched session to {uname} {self.users[uname]['uic']} ({self.default_vms_spec})")
        return 0

    def _cmd_dir(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        spec = tokens[0] if tokens else self.default_dir
        target = self.resolve_path(spec)
        if os.path.isdir(target):
            pattern = os.path.join(target, "*")
        else:
            pattern = target if ("*" in target or "?" in target) else target

        print(f"\nDirectory {self.default_vms_spec}\n")
        files = sorted(glob.glob(pattern))
        total_blocks = 0
        count = 0
        for f in files:
            if os.path.isdir(f):
                continue
            bname = os.path.basename(f)
            vms_name = bname.upper() if ";" in bname else f"{bname.upper()};1"
            st = os.stat(f)
            blocks = max(1, (st.st_size + 511) // 512)
            total_blocks += blocks
            count += 1
            dt = datetime.fromtimestamp(st.st_mtime).strftime("%d-%b-%Y %H:%M")
            print(f"{vms_name:<28} {blocks:>6}  {dt}")
        print(f"\nTotal of {count} files, {total_blocks} blocks.")
        return 0

    def _cmd_type(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if not tokens:
            print("%DCL-E-NOFILE, missing file to display")
            return 1
        target = self.resolve_path(tokens[0])
        if not os.path.isfile(target):
            print(f"%TYPE-W-SEARCHFAIL, error searching for {tokens[0]}\n-RMS-E-FNF, file not found")
            return 1
        with open(target, "r", errors="replace") as f:
            sys.stdout.write(f.read())
        return 0

    def _cmd_copy(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing source or destination")
            return 1
        src = self.resolve_path(tokens[0])
        dst = self.resolve_path(tokens[1])
        if not os.path.isfile(src):
            print(f"%COPY-E-OPENIN, error opening {tokens[0]} as input\n-RMS-E-FNF, file not found")
            return 1
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        # If destination already exists and has no explicit version, create a ;2 version backup
        if os.path.isfile(dst) and ";" not in os.path.basename(dst):
            ver1 = dst + ";1"
            if not os.path.exists(ver1):
                shutil.copy2(dst, ver1)
        shutil.copy2(src, dst)
        print(f"%COPY-S-COPIED, {os.path.basename(src)} copied to {os.path.basename(dst)} (1 block)")
        return 0

    def _cmd_rename(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing source or destination")
            return 1
        src = self.resolve_path(tokens[0])
        dst = self.resolve_path(tokens[1])
        if not os.path.exists(src):
            print(f"%RENAME-E-FNF, file {tokens[0]} not found")
            return 1
        shutil.move(src, dst)
        print(f"%RENAME-S-RENAMED, {os.path.basename(src)} renamed to {os.path.basename(dst)}")
        return 0

    def _cmd_delete(self, rest):
        for tok in rest.split():
            if tok.upper().startswith("/ENTRY=") or tok.upper().startswith("/ENTRY:"):
                eid = tok.split("=", 1)[-1].split(":", 1)[-1]
                return subprocess.call([sys.executable, self.job_controller, "delete-entry", eid])
        up_quals = [t.upper() for t in rest.split() if self._is_dcl_qualifier(t)]
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if "/ACCOUNT" in up_quals or "/ACCOUNTS" in up_quals or (tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS")):
            if tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS"):
                tokens = tokens[1:]
            return self._uaf_remove(" ".join(tokens))
        if not tokens:
            print("%DCL-E-PARAM, missing file specification")
            return 1
        target = self.resolve_path(tokens[0])
        if os.path.isfile(target):
            os.remove(target)
            print(f"%DELETE-I-FILDEL, {os.path.basename(target)};1 deleted (1 block)")
            return 0
        print(f"%DELETE-W-SEARCHFAIL, error searching for {tokens[0]}\n-RMS-E-FNF, file not found")
        return 1

    def _cmd_purge(self, rest):
        """VAX/VMS PURGE command: removes older file versions (;1, ;2, ...) keeping latest."""
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        target_dir = self.resolve_path(tokens[0]) if tokens else self.default_dir
        if os.path.isfile(target_dir):
            target_dir = os.path.dirname(target_dir)
        purged = 0
        if os.path.isdir(target_dir):
            for entry in sorted(os.listdir(target_dir)):
                if ";" in entry:
                    full_p = os.path.join(target_dir, entry)
                    if os.path.isfile(full_p):
                        os.remove(full_p)
                        purged += 1
                        print(f"%PURGE-I-FILPURG, {self.default_vms_spec}{entry.upper()} deleted (1 block)")
        if purged == 0:
            print("%PURGE-I-FILPURG, no old file versions found to purge")
        else:
            print(f"%PURGE-S-TOTAL, {purged} file(s) purged")
        return 0

    def _cmd_create(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        quals = [t.upper() for t in rest.split() if self._is_dcl_qualifier(t)]
        if any(q.startswith("/ACCOUNT") for q in quals) or (tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS")):
            if tokens and tokens[0].upper() in ("ACCOUNT", "ACCOUNTS"):
                tokens = tokens[1:]
            clean_rest = " ".join([t for t in rest.split() if not t.upper().startswith("/ACCOUNT") and t.upper() not in ("ACCOUNT", "ACCOUNTS")])
            return self._uaf_add(clean_rest)
        if not tokens:
            print("%DCL-E-PARAM, missing file or directory specification")
            return 1
        target = self.resolve_path(tokens[0])
        if any(q.startswith("/DIR") for q in quals):
            os.makedirs(target, exist_ok=True)
            print(f"%CREATE-I-CREATED, directory {tokens[0]} created")
            return 0
        with open(target, "w") as f:
            f.write("")
        print(f"%CREATE-I-CREATED, {os.path.basename(target)};1 created")
        return 0

    def _cmd_modify(self, rest):
        clean_rest = " ".join([t for t in rest.split() if not t.upper().startswith("/ACCOUNT") and t.upper() not in ("ACCOUNT", "ACCOUNTS")])
        return self._uaf_modify(clean_rest)

    def _cmd_search(self, rest):
        tokens = [t for t in shlex.split(rest) if not self._is_dcl_qualifier(t)]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing file or search string")
            return 1
        target = self.resolve_path(tokens[0])
        pattern = tokens[1]
        if not os.path.isfile(target):
            print(f"%SEARCH-E-OPENIN, error opening {tokens[0]}")
            return 1
        matches = 0
        with open(target, "r", errors="replace") as f:
            for ln in f:
                if pattern.upper() in ln.upper():
                    sys.stdout.write(ln)
                    matches += 1
        if matches == 0:
            print("%SEARCH-I-NOMATCHES, no strings matched")
        return 0

    def _cmd_diff(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing comparison files")
            return 1
        f1 = self.resolve_path(tokens[0])
        f2 = self.resolve_path(tokens[1])
        if not os.path.isfile(f1) or not os.path.isfile(f2):
            print("%DIFF-E-OPENIN, error opening input file")
            return 1
        with open(f1, "r", errors="replace") as a, open(f2, "r", errors="replace") as b:
            if a.read() == b.read():
                print("Number of difference sections found: 0\nNumber of difference records found: 0")
            else:
                print("Number of difference sections found: 1")
        return 0

    def _cmd_analyze(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        fname = tokens[0] if tokens else "WELCOME.TXT"
        target = self.resolve_path(fname)
        print(f"Check RMS File Integrity — VAX/VMS ANALYZE/RMS_FILE V5.5-2")
        print(f"File Spec: {target}")
        print("The analysis uncovered NO errors.")
        return 0

    def _parse_uaf_quals(self, s):
        tokens = []
        quals = {}
        for tok in shlex.split(s) if s else []:
            if tok.startswith("/"):
                for part in tok.lstrip("/").split("/"):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        quals[k.upper()] = v.strip("()")
                    elif ":" in part:
                        k, v = part.split(":", 1)
                        quals[k.upper()] = v.strip("()")
                    else:
                        quals[part.upper()] = True
            elif "/" in tok and not os.path.exists(tok):
                subparts = tok.split("/")
                if subparts[0]:
                    tokens.append(subparts[0])
                for part in subparts[1:]:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        quals[k.upper()] = v.strip("()")
                    elif ":" in part:
                        k, v = part.split(":", 1)
                        quals[k.upper()] = v.strip("()")
                    else:
                        quals[part.upper()] = True
            else:
                tokens.append(tok)
        return tokens, quals

    def _uaf_add(self, rest):
        tokens, quals = self._parse_uaf_quals(rest)
        if not tokens:
            print("%UAF-E-ADDERR, missing username for ADD/CREATE")
            return 1
        raw_id = tokens[0].upper()
        if raw_id.startswith("[") and "," in raw_id:
            uic = raw_id
            uname = (quals.get("NAME") or quals.get("USER") or f"U{raw_id.strip('[]').replace(',', '_')}").upper()
        else:
            uname = raw_id
            uic = quals.get("UIC", "[200,201]")
            if not uic.startswith("["):
                uic = f"[{uic}]"
        password = str(quals.get("PASSWORD", "")) if quals.get("PASSWORD") is not True else ""
        owner = str(quals.get("OWNER", f"USER {uname}"))
        account = str(quals.get("ACCOUNT", "USER")).upper()
        dir_spec = str(quals.get("DIRECTORY", quals.get("DIR", f"DKA0:[{uname}]"))).upper()
        if not dir_spec.startswith("DKA0:"):
            dir_spec = f"DKA0:{dir_spec}" if dir_spec.startswith("[") else f"DKA0:[{dir_spec}]"
        dir_rel = dir_spec.split("[", 1)[-1].rstrip("]").lower().replace(".", "/")
        quota = int(quals.get("PGFLQUOTA", quals.get("QUOTA", 50000)))
        privs = str(quals.get("PRIVILEGES", quals.get("PRIV", "TMPMBX,NETMBX"))).upper()
        if privs == "TRUE":
            privs = "SYSPRV,TMPMBX,NETMBX"
        flags = str(quals.get("FLAGS", "NODISUSER")).upper()
        if "DISUSER" in quals:
            flags = "DISUSER"
        self.users[uname] = {
            "username": uname,
            "owner": owner,
            "account": account,
            "uic": uic,
            "password": password,
            "privs": privs,
            "flags": flags,
            "identifiers": [],
            "dir_spec": dir_spec,
            "dir_rel": dir_rel,
            "quota": quota,
        }
        self.get_user_dir(uname)
        self._save_sysuaf()
        print(f"%UAF-I-ADDMSG, user record(s) updated — {uname} {uic} added to SYSUAF.DAT")
        return 0

    def _uaf_modify(self, rest):
        tokens, quals = self._parse_uaf_quals(rest)
        if not tokens:
            print("%UAF-E-MODERR, missing username for MODIFY")
            return 1
        uname = self.normalize_user(tokens[0])
        if not uname:
            print(f"%UAF-E-MODERR, user {tokens[0]} not found in SYSUAF.DAT")
            return 1
        u = self.users[uname]
        if "PASSWORD" in quals:
            u["password"] = "" if quals["PASSWORD"] is True else str(quals["PASSWORD"])
        if "NOPASSWORD" in quals:
            u["password"] = ""
        if "UIC" in quals and isinstance(quals["UIC"], str):
            uic_v = quals["UIC"]
            u["uic"] = uic_v if uic_v.startswith("[") else f"[{uic_v}]"
        if "OWNER" in quals and isinstance(quals["OWNER"], str):
            u["owner"] = quals["OWNER"]
        if "ACCOUNT" in quals and isinstance(quals["ACCOUNT"], str):
            u["account"] = quals["ACCOUNT"].upper()
        if "PRIVILEGES" in quals or "PRIV" in quals:
            pv = quals.get("PRIVILEGES", quals.get("PRIV"))
            u["privs"] = pv.upper() if isinstance(pv, str) else "SYSPRV,TMPMBX,NETMBX"
        if "NOPRIVILEGES" in quals or "NOPRIV" in quals:
            u["privs"] = "TMPMBX,NETMBX"
        if "QUOTA" in quals or "PGFLQUOTA" in quals:
            qv = quals.get("QUOTA", quals.get("PGFLQUOTA"))
            if str(qv).isdigit():
                u["quota"] = int(qv)
        if "FLAGS" in quals and isinstance(quals["FLAGS"], str):
            u["flags"] = quals["FLAGS"].upper()
        if "DISUSER" in quals:
            u["flags"] = "DISUSER"
        if "NODISUSER" in quals:
            u["flags"] = "NODISUSER"
        self._save_sysuaf()
        print(f"%UAF-I-MODMSG, user record(s) updated — {uname} {u['uic']} modified in SYSUAF.DAT")
        return 0

    def _uaf_remove(self, rest):
        tokens, _ = self._parse_uaf_quals(rest)
        if not tokens:
            print("%UAF-E-REMERR, missing username to remove")
            return 1
        uname = self.normalize_user(tokens[0])
        if not uname:
            print(f"%UAF-E-REMERR, user {tokens[0]} not found in SYSUAF.DAT")
            return 1
        if uname == "SYSTEM":
            print("%UAF-E-REMERR, cannot remove protected SYSTEM [1,4] account")
            return 1
        u = self.users.pop(uname)
        self._save_sysuaf()
        print(f"%UAF-I-REMMSG, user record {uname} {u['uic']} removed from SYSUAF.DAT")
        return 0

    def _uaf_show(self, target="*", full=False):
        items = list(self.users.values())
        if target and target != "*":
            uname = self.normalize_user(target)
            if not uname:
                print(f"%UAF-W-BADSPC, no user matches specification '{target}'")
                return 1
            items = [self.users[uname]]
        if full:
            for u in items:
                print(f"Username: {u['username']:<16} Owner:  {u.get('owner', u['username'])}")
                print(f"Account:  {u.get('account', 'USER'):<16} UIC:    {u['uic']:<12} ([{u['username']}])")
                print(f"CLI:      DCL              Tables: DCLTABLES")
                print(f"Default:  {u['dir_spec']}")
                print(f"Flags:    {u.get('flags', 'NODISUSER')}")
                print(f"Primary days:   Mon Tue Wed Thu Fri")
                print(f"Secondary days: Sat Sun")
                print(f"Pgflquo:  {u['quota']:<16} Prclm:  8            Bio/Diolm: 18")
                print(f"Privileges:")
                print(f"  {u['privs']}")
                ids = u.get("identifiers", [])
                if ids:
                    print(f"Identifiers Held: {', '.join(ids)}")
                print("")
        else:
            print("VAX/VMS Authorize Utility (SYSUAF.DAT):")
            print("Username      UIC         Account   Flags       Default Directory   Privileges")
            print("------------  ----------  --------  ----------  ------------------  ----------------------------------")
            for u in items:
                flags = u.get("flags", "NODISUSER")
                acct = u.get("account", "USER")
                print(f"{u['username']:<12}  {u['uic']:<10}  {acct:<8}  {flags:<10}  {u['dir_spec']:<18}  {u['privs'][:34]}")
        return 0

    def _execute_uaf_line(self, line):
        s = line.strip()
        if not s or s.startswith("!"):
            return 0
        first = s.split(None, 1)[0]
        rest = s.split(None, 1)[1].strip() if len(s.split(None, 1)) > 1 else ""
        if "/" in first:
            v_part, q_part = first.split("/", 1)
            verb = v_part.upper()
            rest = f"/{q_part} {rest}".strip()
        else:
            verb = first.upper()

        if verb in ("ADD", "CREATE"):
            return self._uaf_add(rest)
        if verb in ("MODIFY", "SET"):
            return self._uaf_modify(rest)
        if verb in ("REMOVE", "DELETE"):
            return self._uaf_remove(rest)
        if verb in ("SHOW", "LIST"):
            tokens, quals = self._parse_uaf_quals(rest)
            target = tokens[0] if tokens else "*"
            full = ("FULL" in quals) and (verb != "LIST")
            return self._uaf_show(target, full=full)
        if verb == "COPY":
            tokens, quals = self._parse_uaf_quals(rest)
            if len(tokens) < 2:
                print("%UAF-E-CPYERR, missing source or destination username")
                return 1
            src = self.normalize_user(tokens[0])
            dst = tokens[1].upper()
            if not src:
                print(f"%UAF-E-CPYERR, source user {tokens[0]} not found")
                return 1
            new_u = dict(self.users[src])
            new_u["username"] = dst
            new_u["dir_spec"] = f"DKA0:[{dst}]"
            new_u["dir_rel"] = dst.lower()
            if "UIC" in quals and isinstance(quals["UIC"], str):
                uv = quals["UIC"]
                new_u["uic"] = uv if uv.startswith("[") else f"[{uv}]"
            self.users[dst] = new_u
            self.get_user_dir(dst)
            self._save_sysuaf()
            print(f"%UAF-I-COPMSG, user record copied from {src} to {dst} {new_u['uic']}")
            return 0
        if verb == "RENAME":
            tokens, _ = self._parse_uaf_quals(rest)
            if len(tokens) < 2:
                print("%UAF-E-RENERR, missing old or new username")
                return 1
            old_u = self.normalize_user(tokens[0])
            new_name = tokens[1].upper()
            if not old_u:
                print(f"%UAF-E-RENERR, user {tokens[0]} not found")
                return 1
            rec = self.users.pop(old_u)
            rec["username"] = new_name
            self.users[new_name] = rec
            self._save_sysuaf()
            print(f"%UAF-I-RENMSG, user record {old_u} renamed to {new_name}")
            return 0
        if verb == "GRANT":
            tokens, quals = self._parse_uaf_quals(rest)
            ident = quals.get("IDENTIFIER", tokens[0] if tokens else "DECW$USERS")
            target_u = tokens[-1] if tokens else self.current_user
            uname = self.normalize_user(target_u)
            if not uname:
                print(f"%UAF-E-GRTERR, user {target_u} not found")
                return 1
            ids = self.users[uname].setdefault("identifiers", [])
            if str(ident).upper() not in ids:
                ids.append(str(ident).upper())
            self._save_sysuaf()
            print(f"%UAF-I-GRANTMSG, identifier {str(ident).upper()} granted to {uname}")
            return 0
        if verb == "REVOKE":
            tokens, quals = self._parse_uaf_quals(rest)
            ident = quals.get("IDENTIFIER", tokens[0] if tokens else "DECW$USERS")
            target_u = tokens[-1] if tokens else self.current_user
            uname = self.normalize_user(target_u)
            if not uname:
                print(f"%UAF-E-REVERR, user {target_u} not found")
                return 1
            ids = self.users[uname].setdefault("identifiers", [])
            if str(ident).upper() in ids:
                ids.remove(str(ident).upper())
            self._save_sysuaf()
            print(f"%UAF-I-REVOKEMSG, identifier {str(ident).upper()} revoked from {uname}")
            return 0
        if verb == "HELP":
            print(
                "VAX/VMS Authorize Utility (UAF>) Commands:\n"
                "  ADD <user> [/PASSWORD=p] [/UIC=[g,m]] [/OWNER=o] [/ACCOUNT=a] [/PRIVILEGES=(...)] [/QUOTA=n]\n"
                "  MODIFY <user> [/PASSWORD=p] [/PRIVILEGES=(...)] [/QUOTA=n] [/FLAGS=DISUSER]\n"
                "  REMOVE <user>              Remove user account from SYSUAF.DAT\n"
                "  SHOW [user|*] [/FULL]      Display SYSUAF user record(s)\n"
                "  LIST [user|*]              List brief summary of SYSUAF accounts\n"
                "  COPY <src> <dst> [/UIC=..] Duplicate existing user template\n"
                "  RENAME <old> <new>         Rename user account\n"
                "  GRANT/IDENTIFIER=<id> <u>  Grant rightslist identifier to user\n"
                "  REVOKE/IDENTIFIER=<id> <u> Revoke rightslist identifier from user\n"
                "  EXIT                       Return to DCL ($)"
            )
            return 0
        return self._uaf_show(s)

    def _cmd_authorize(self, rest, interactive_uaf=False):
        s = rest.strip()
        if s:
            return self._execute_uaf_line(s)
        if interactive_uaf and getattr(self, "_in_interactive_loop", False):
            while True:
                sys.stdout.write("UAF> ")
                sys.stdout.flush()
                try:
                    ln = sys.stdin.readline()
                except KeyboardInterrupt:
                    print("^C")
                    continue
                if not ln:
                    break
                if "\x03" in ln:
                    print("^C")
                    continue
                ln_s = ln.strip()
                if ln_s.upper() in ("EXIT", "QUIT", "\x1a"):
                    break
                self._execute_uaf_line(ln_s)
            return 0
        return self._uaf_show("*", full=False)

    def _cmd_monitor(self, rest):
        print(f"VAX/VMS V5.5-2 Performance Monitor on Node {self.NODE_NAME}")
        print("  Interrupt Stack:   0%   Kernel Mode:   4%   Executive Mode:   2%")
        print("  Supervisor Mode:   1%   User Mode:    12%   Idle Time:       81%")
        return 0

    def _cmd_sysman(self, rest):
        print(f"SYSMAN> Node {self.NODE_NAME} VAX/VMS {self.VERSION} System Management Environment Active.")
        return 0

    def _cmd_define(self, verb, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if len(tokens) < 2:
            print("%DCL-E-PARAM, missing logical name or equivalence string")
            return 1
        if verb == "DEFINE":
            log_name, target = tokens[0].upper().rstrip(":"), tokens[1]
        else:
            target, log_name = tokens[0], tokens[1].upper().rstrip(":")
        self.logicals[log_name] = target
        return 0

    def _cmd_deassign(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if not tokens:
            return 1
        name = tokens[0].upper().rstrip(":")
        self.logicals.pop(name, None)
        return 0

    def _cmd_write(self, rest):
        s = rest.strip()
        for prefix in ("SYS$OUTPUT", "OPA0:", "TT:"):
            if s.upper().startswith(prefix):
                s = s[len(prefix):].strip()
                break
        if s.startswith('"') and s.endswith('"') and len(s) >= 2:
            s = s[1:-1]
        print(s)
        return 0

    # ==========================================================================
    # Compilers, Linker, DECwindows & Layered Applications
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
            print("%DCL-E-NOFILE, missing VAX BASIC / BASIC-PLUS-2 source filename")
            return 1
        src = self.resolve_path(tokens[0])
        if not os.path.isfile(src) and os.path.isfile(src + ".BAS"):
            src = src + ".BAS"
        elif not os.path.isfile(src) and os.path.isfile(src + ".bas"):
            src = src + ".bas"
        if not os.path.isfile(src):
            print(f"%BASIC-E-OPENIN, error opening {tokens[0]} as input")
            return 1
        if not obj_out:
            stem, _ = os.path.splitext(src)
            obj_out = stem + ".OBJ"

        basicc_bin = self.find_executable("basicc")
        if not basicc_bin:
            print("%BASIC-F-NOCOMP, basicc compiler not found")
            return 1
        rc = subprocess.call([basicc_bin, src, "-o", obj_out], cwd=self.default_dir)
        stem_out, _ = os.path.splitext(obj_out)
        for bin_cand in (stem_out + ".bin", obj_out + ".bin"):
            if os.path.isfile(bin_cand):
                try:
                    os.remove(bin_cand)
                except OSError:
                    pass
        return rc

    def _cmd_link(self, rest):
        tokens = []
        bin_out = None
        for t in rest.split():
            if t.upper().startswith("/EXECUTABLE=") or t.upper().startswith("/EXE=") or t.upper().startswith("/OUTPUT="):
                bin_out = self.resolve_path(t.split("=", 1)[1])
            elif not self._is_dcl_qualifier(t):
                tokens.append(t)
        if not tokens:
            print("%DCL-E-NOFILE, missing object module to link")
            return 1
        obj = self.resolve_path(tokens[0])
        if not os.path.isfile(obj):
            stem_q, ext_q = os.path.splitext(obj)
            if ext_q.upper() == ".OBJ":
                for alt_ext in (".OBJ", ".obj"):
                    if os.path.isfile(stem_q + alt_ext):
                        obj = stem_q + alt_ext
                        break
            else:
                for ext_cand in (".OBJ", ".obj"):
                    if os.path.isfile(obj + ext_cand):
                        obj = obj + ext_cand
                        break
        if not os.path.isfile(obj):
            print(f"%LINK-E-OPENIN, error opening {tokens[0]} as input")
            return 1
        if not bin_out:
            stem, _ = os.path.splitext(obj)
            bin_out = stem + ".EXE"

        basiclink_bin = self.find_executable("basiclink")
        if not basiclink_bin:
            print("%LINK-F-NOLINK, basiclink linker not found")
            return 1

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

    def _cmd_edit(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        arg = tokens[0] if tokens else ""
        return self._invoke_app("edt", arg)

    def _cmd_run(self, rest):
        if not rest:
            print("%DCL-E-NOFILE, missing image specification to run")
            return 1
        parts = rest.split(None, 1)
        prog = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""

        clean_upper = prog.upper()
        if ";" in clean_upper:
            clean_upper = clean_upper.rsplit(";", 1)[0]
        for prefix in ("SYS$SYSTEM:", "SYS$LIBRARY:", "DKA0:[SYSEXE]", "$"):
            if clean_upper.startswith(prefix):
                clean_upper = clean_upper[len(prefix):]
        clean_upper = os.path.splitext(clean_upper)[0]

        if clean_upper in self.UNSUPPORTED_PDP11_APPS:
            print(
                f"%DCL-W-UNSUPOS, '{clean_upper}' (DIBS-11 / CTS-300/CTS-500) is a 16-bit PDP-11 RSTS/E application "
                f"not supported under 32-bit VAX/VMS {self.VERSION}"
            )
            return 2

        if clean_upper == "AUTHORIZE":
            return self._cmd_authorize(args_str, interactive_uaf=not bool(args_str.strip()))

        if clean_upper in self.VMS_SYSTEM_IMAGES:
            return self._invoke_app(self.VMS_SYSTEM_IMAGES[clean_upper], args_str)

        if clean_upper in self.SUPPORTED_VMS_APPS:
            bname, _ = self.SUPPORTED_VMS_APPS[clean_upper]
            return self._invoke_app(bname, args_str)

        target = self.resolve_path(prog)
        if not os.path.isfile(target):
            for ext_cand in (".EXE", ".exe", ".TSK", ".tsk"):
                cand = self.resolve_path(prog + ext_cand)
                if os.path.isfile(cand):
                    target = cand
                    break
        if os.path.isfile(target) and os.access(target, os.X_OK):
            cmd = [target] + (shlex.split(args_str) if args_str else [])
            return subprocess.call(cmd, cwd=self.default_dir)

        exe = self.find_executable(clean_upper.lower())
        if exe:
            return self._invoke_app(clean_upper.lower(), args_str)

        print(f"%DCL-W-ACTIMAGE, error activating image {prog}\n-RMS-E-FNF, file not found")
        return 1

    def _invoke_app(self, bin_name, args_str=""):
        exe = self.find_executable(bin_name)
        if not exe:
            print(f"%DCL-W-ACTIMAGE, error activating SYS$SYSTEM:{bin_name.upper()}.EXE")
            return 1
        env = os.environ.copy()
        env["PATH"] = f"{self.sys_bin}:{env.get('PATH', '')}"
        env["LD_LIBRARY_PATH"] = f"{self.sys_lib}:{env.get('LD_LIBRARY_PATH', '')}"
        cmd = [exe]
        if args_str:
            for tok in shlex.split(args_str):
                up = tok.upper()
                if up.startswith(("SYS$", "DKA0:", "[")) or ";" in tok:
                    resolved = self.resolve_path(tok)
                    if os.path.dirname(resolved) == self.default_dir:
                        cmd.append(os.path.basename(resolved))
                    else:
                        cmd.append(resolved)
                else:
                    cmd.append(tok)
        return subprocess.call(cmd, cwd=self.default_dir, env=env)

    def _cmd_print(self, rest):
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if not tokens:
            print("%DCL-E-NOFILE, missing file specification to print")
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
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if not tokens:
            print("%DCL-E-NOFILE, missing command procedure to submit")
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
        tokens = [t for t in rest.split() if not self._is_dcl_qualifier(t)]
        if not tokens:
            print("%DCL-E-PARAM, missing queue name")
            return 1
        return subprocess.call([sys.executable, self.job_controller, action, tokens[0]])


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="DEC VAX/VMS V5.5-2 Operating System Emulation Executive & DCL"
    )
    parser.add_argument("-c", "--command", help="Execute VAX/VMS DCL command(s) (semicolon-separated) and exit")
    parser.add_argument("-u", "--user", default="SYSTEM", help="Initial SYSUAF username or UIC for -c / --no-login (default: SYSTEM)")
    parser.add_argument("--login", action="store_true", default=True, help="Prompt for interactive VMS Username/Password login (default)")
    parser.add_argument("--no-login", action="store_true", help="Skip login prompt and start directly in --user account")
    parser.add_argument("--boot", action="store_true", help="Display VAXstation 4000 VMB.EXE / SYSBOOT.EXE bootstrap")
    parser.add_argument("--multiuser", action="store_true", help="Start multi-user SSH and HTTPS VT220 terminal daemons")
    parser.add_argument("--root", default=None, help="Virtual ODS-2 disk root directory (DKA0:)")
    parser.add_argument("script", nargs="?", default=None, help="Optional DCL command procedure (.COM) to execute")

    args = parser.parse_args()
    emu = VMSEmulator(root_dir=args.root, username=args.user)

    if args.boot and args.command:
        emu.print_boot_sequence()

    if args.command:
        rc = 0
        for subcmd in re.split(r";(?![0-9]+\b)", args.command):
            subcmd = subcmd.strip()
            if subcmd:
                rc = emu.execute_line(subcmd)
                if emu.exit_requested:
                    break
        sys.exit(rc)

    if args.script:
        script_arg = args.script[1:] if args.script.startswith("@") else args.script
        sys.exit(emu.execute_script(script_arg))

    if os.getpid() == 1 or args.multiuser or os.environ.get("VMS_MULTIUSER") == "1":
        try:
            import multiuser_service
            emu_bin = os.path.join(emu.os_dir, "bin", "vms-emu")
            multiuser_service.start_background_daemons(
                emu_bin_path=emu_bin,
                os_title="DEC VAX/VMS V5.5-2 — VT220 Web Terminal",
                header_title="DEC VAXstation 4000 — VAX/VMS V5.5-2 Timesharing (Node VAX01)",
                ssh_port=emu.ssh_port,
                https_port=emu.https_port,
            )
        except Exception:
            pass

    sys.exit(emu.run_interactive(require_login=not args.no_login, show_boot=args.boot))


if __name__ == "__main__":
    main()
