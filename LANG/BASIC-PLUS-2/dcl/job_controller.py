import os
import sys
import json
import time
import sqlite3
import shutil
import threading
from datetime import datetime

class JobController:
    def __init__(self, db_path=None, base_dir=None):
        if base_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".dcl"))
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.spool_dir = os.path.join(self.base_dir, "spool")
        os.makedirs(self.spool_dir, exist_ok=True)
        
        self.log_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.run_dir = os.path.join(self.base_dir, "run")
        os.makedirs(self.run_dir, exist_ok=True)
        self.pid_file = os.path.join(self.run_dir, "dec-printq.pid")
        
        if db_path is None:
            db_path = os.path.join(self.base_dir, "job_queue.db")
        self.db_path = db_path
        
        self.lock = threading.Lock()
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS queues (
                name TEXT PRIMARY KEY,
                type TEXT NOT NULL,       -- 'BATCH' or 'PRINT'
                status TEXT NOT NULL,     -- 'OPEN' or 'STOPPED'
                max_active INTEGER DEFAULT 1
            )
            """)
            
            c.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                queue_name TEXT NOT NULL,
                job_name TEXT NOT NULL,
                user_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,     -- 'PENDING', 'EXECUTING', 'COMPLETED', 'ABORTED', 'CANCELLED'
                submit_time TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                log_file TEXT,
                options_json TEXT,
                FOREIGN KEY(queue_name) REFERENCES queues(name)
            )
            """)
            
            # Default RSTS/E PBS Queues
            default_queues = [
                ("SYS$BATCH", "BATCH", "OPEN", 1),
                ("SYS$PRINT", "PRINT", "OPEN", 1),
                ("LP0:", "PRINT", "OPEN", 1),
                ("NETPRINT", "PRINT", "OPEN", 1),
                ("BATCH", "BATCH", "OPEN", 1),
                ("PRINT", "PRINT", "OPEN", 1)
            ]
            for q_name, q_type, q_status, q_max in default_queues:
                c.execute("""
                INSERT OR IGNORE INTO queues (name, type, status, max_active)
                VALUES (?, ?, ?, ?)
                """, (q_name, q_type, q_status, q_max))

            c.execute("""
            CREATE TABLE IF NOT EXISTS queue_config (
                queue_name TEXT PRIMARY KEY,
                dest_type TEXT DEFAULT 'SPOOL',    -- 'SPOOL', 'FILE', 'COMMAND', 'SOCKET'
                dest_path TEXT DEFAULT '',         -- file path, shell command, or host:port
                banner INTEGER DEFAULT 1,          -- 1 = burst/banner page, 0 = no banner
                form_type TEXT DEFAULT 'NORMAL',   -- 'NORMAL', 'WIDE132', etc.
                FOREIGN KEY(queue_name) REFERENCES queues(name)
            )
            """)

            default_configs = [
                ("SYS$PRINT", "SPOOL", "", 1, "NORMAL"),
                ("LP0:", "SPOOL", "", 1, "NORMAL"),
                ("NETPRINT", "SPOOL", "", 1, "NORMAL"),
                ("PRINT", "SPOOL", "", 1, "NORMAL")
            ]
            for qn, dtype, dpath, bnr, ftype in default_configs:
                c.execute("""
                INSERT OR IGNORE INTO queue_config (queue_name, dest_type, dest_path, banner, form_type)
                VALUES (?, ?, ?, ?, ?)
                """, (qn, dtype, dpath, bnr, ftype))

            c.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                ppn TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT DEFAULT '',
                quota INTEGER DEFAULT 10000,
                privs TEXT DEFAULT 'NOPRIV',
                flags TEXT DEFAULT 'NODISUSER',
                directory TEXT DEFAULT '',
                owner TEXT DEFAULT ''
            )
            """)

            default_accounts = [
                ("[1,1]", "LIBRARY", "LIB", 50000, "PRIV", "NODISUSER", "DK0:[1,1]", "System Library (LB:)"),
                ("[1,2]", "SYSTEM", "SYSTEM", 100000, "PRIV", "NODISUSER", "DK0:[1,2]", "System Manager (SY:)"),
                ("[1,3]", "PBS", "PBS", 25000, "PRIV", "NODISUSER", "DK0:[1,3]", "Print/Batch Services"),
                ("[100,100]", "DIBS", "DIBS", 20000, "NOPRIV", "NODISUSER", "DK0:[100,100]", "Commercial Accounting"),
                ("[200,200]", "GUEST", "", 10000, "NOPRIV", "NODISUSER", "DK0:[200,200]", "Timesharing Guest")
            ]
            for acc_ppn, acc_user, acc_pw, acc_q, acc_pr, acc_fl, acc_dir, acc_own in default_accounts:
                c.execute("""
                INSERT OR IGNORE INTO accounts (ppn, username, password, quota, privs, flags, directory, owner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (acc_ppn, acc_user, acc_pw, acc_q, acc_pr, acc_fl, acc_dir, acc_own))
                
            conn.commit()
            conn.close()

    def is_print_service_running(self):
        if not os.path.exists(self.pid_file):
            return False
        try:
            with open(self.pid_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return False
                pid = int(content)
            os.kill(pid, 0)
            return True
        except (ValueError, OSError):
            return False

    def get_queue_config(self, queue_name):
        q = self.normalize_queue_name(queue_name, "PRINT")
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM queue_config WHERE queue_name = ?", (q,))
            row = c.fetchone()
            conn.close()
            if row:
                return dict(row)
            return {
                "queue_name": q,
                "dest_type": "SPOOL",
                "dest_path": "",
                "banner": 1,
                "form_type": "NORMAL"
            }

    def set_queue_config(self, queue_name, dest_type="SPOOL", dest_path="", banner=1, form_type="NORMAL"):
        q = self.normalize_queue_name(queue_name, "PRINT")
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("""
            INSERT INTO queue_config (queue_name, dest_type, dest_path, banner, form_type)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(queue_name) DO UPDATE SET
                dest_type = excluded.dest_type,
                dest_path = excluded.dest_path,
                banner = excluded.banner,
                form_type = excluded.form_type
            """, (q, dest_type, dest_path, int(banner), form_type))
            conn.commit()
            conn.close()

    def normalize_queue_name(self, name, default_type="BATCH"):
        if not name:
            return "SYS$BATCH" if default_type == "BATCH" else "SYS$PRINT"
        name_upper = name.upper()
        if name_upper in ["SYS$BATCH", "BATCH"]:
            return "SYS$BATCH"
        if name_upper in ["SYS$PRINT", "PRINT", "LP0", "LP0:"]:
            if name_upper.startswith("LP0"):
                return "LP0:"
            return "SYS$PRINT"
        return name_upper

    def list_queues(self, queue_name=None):
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            if queue_name:
                q = self.normalize_queue_name(queue_name)
                c.execute("SELECT * FROM queues WHERE name = ? ORDER BY type, name", (q,))
            else:
                c.execute("SELECT * FROM queues ORDER BY type, name")
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            return rows

    def start_queue(self, queue_name):
        q = self.normalize_queue_name(queue_name)
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO queues (name, type, status, max_active) VALUES (?, 'PRINT', 'OPEN', 1)", (q,))
            c.execute("UPDATE queues SET status = 'OPEN' WHERE name = ?", (q,))
            changed = c.rowcount
            conn.commit()
            conn.close()
            return changed > 0

    def stop_queue(self, queue_name):
        q = self.normalize_queue_name(queue_name)
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("UPDATE queues SET status = 'STOPPED' WHERE name = ?", (q,))
            changed = c.rowcount
            conn.commit()
            conn.close()
            return changed > 0

    def submit_batch_job(self, file_path, queue_name="SYS$BATCH", job_name=None, user_name="SYSTEM", options=None):
        if not os.path.exists(file_path):
            base = os.path.basename(file_path)
            if os.path.exists(base):
                file_path = os.path.abspath(base)
            else:
                candidates = [file_path + ".COM", file_path + ".com", file_path + ".DCL", file_path + ".dcl"]
                found = False
                for cand in candidates:
                    if os.path.exists(cand):
                        file_path = os.path.abspath(cand)
                        found = True
                        break
                if not found:
                    raise FileNotFoundError(f"Command procedure {file_path} not found")
            
        queue_name = self.normalize_queue_name(queue_name, "BATCH")
        if not job_name:
            job_name = os.path.splitext(os.path.basename(file_path))[0].upper()
            
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        log_file = os.path.join(self.log_dir, f"{job_name}.LOG")
        options_str = json.dumps(options or {})
        
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO queues (name, type, status, max_active) VALUES (?, 'BATCH', 'OPEN', 1)", (queue_name,))
            c.execute("""
            INSERT INTO entries (queue_name, job_name, user_name, file_path, status, submit_time, log_file, options_json)
            VALUES (?, ?, ?, ?, 'PENDING', ?, ?, ?)
            """, (queue_name, job_name, user_name, os.path.abspath(file_path), now_str, log_file, options_str))
            entry_id = c.lastrowid
            conn.commit()
            conn.close()
            
        return entry_id, job_name, queue_name

    def submit_print_job(self, file_path, queue_name="SYS$PRINT", job_name=None, user_name="SYSTEM", copies=1, delete_after=False):
        if not os.path.exists(file_path):
            base = os.path.basename(file_path)
            if os.path.exists(base):
                file_path = os.path.abspath(base)
            else:
                d = os.path.dirname(file_path) or "."
                found = False
                if os.path.isdir(d):
                    for f in os.listdir(d):
                        if f.lower() == base.lower():
                            file_path = os.path.join(d, f)
                            found = True
                            break
                if not found:
                    raise FileNotFoundError(f"Print file {file_path} not found")
            
        queue_name = self.normalize_queue_name(queue_name, "PRINT")
        if not job_name:
            job_name = os.path.splitext(os.path.basename(file_path))[0].upper()
            
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        options = {
            "copies": int(copies),
            "delete_after": bool(delete_after)
        }
        
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO queues (name, type, status, max_active) VALUES (?, 'PRINT', 'OPEN', 1)", (queue_name,))
            c.execute("""
            INSERT INTO entries (queue_name, job_name, user_name, file_path, status, submit_time, options_json)
            VALUES (?, ?, ?, ?, 'PENDING', ?, ?)
            """, (queue_name, job_name, user_name, os.path.abspath(file_path), now_str, json.dumps(options)))
            entry_id = c.lastrowid
            conn.commit()
            conn.close()
            
        return entry_id, job_name, queue_name

    def list_entries(self, queue_name=None, all_entries=False):
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            query = "SELECT * FROM entries"
            params = []
            conditions = []
            
            if queue_name:
                q = self.normalize_queue_name(queue_name)
                conditions.append("queue_name = ?")
                params.append(q)
                
            if not all_entries:
                conditions.append("status IN ('PENDING', 'EXECUTING')")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY entry_id ASC"
            c.execute(query, params)
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            return rows

    def get_entry(self, entry_id):
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM entries WHERE entry_id = ?", (entry_id,))
            row = c.fetchone()
            conn.close()
            return dict(row) if row else None

    def delete_entry(self, entry_id):
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("SELECT status FROM entries WHERE entry_id = ?", (entry_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                return False, "Entry not found"
            
            curr_status = row['status']
            if curr_status == 'EXECUTING':
                # Cannot delete actively executing job without abort
                c.execute("UPDATE entries SET status = 'ABORTED' WHERE entry_id = ?", (entry_id,))
            else:
                c.execute("UPDATE entries SET status = 'CANCELLED' WHERE entry_id = ?", (entry_id,))
            conn.commit()
            conn.close()
            return True, "Cancelled"

    def process_next_batch_job(self, interpreter_runner=None):
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("""
            SELECT e.* FROM entries e
            JOIN queues q ON e.queue_name = q.name
            WHERE q.type = 'BATCH' AND q.status = 'OPEN' AND e.status = 'PENDING'
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

        # Execute outside lock so other queries can proceed
        success = True
        log_content = []
        log_content.append(f"Job {entry['job_name']} (entry {entry['entry_id']}) started at {start_time}")
        log_content.append(f"Executing procedure: {entry['file_path']}\n" + ("="*60))
        
        try:
            if interpreter_runner:
                exit_code, output = interpreter_runner(entry['file_path'])
                log_content.append(output)
                if exit_code != 0:
                    success = False
            else:
                log_content.append("No interpreter runner supplied.")
        except Exception as e:
            success = False
            log_content.append(f"Error executing job: {e}")
            
        end_time = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        log_content.append("="*60)
        log_content.append(f"Job {entry['job_name']} ended at {end_time} with status: {'COMPLETED' if success else 'ABORTED'}")
        
        final_log = "\n".join(log_content)
        if entry['log_file']:
            try:
                with open(entry['log_file'], 'w') as f:
                    f.write(final_log)
            except Exception as e:
                print(f"Warning: failed to write log file {entry['log_file']}: {e}")
                
        final_status = 'COMPLETED' if success else 'ABORTED'
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("UPDATE entries SET status = ?, end_time = ? WHERE entry_id = ?",
                      (final_status, end_time, entry['entry_id']))
            conn.commit()
            conn.close()
            
        entry['status'] = final_status
        return entry

    def process_next_print_job(self):
        with self.lock:
            conn = self._get_connection()
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

        opts = json.loads(entry['options_json'] or "{}")
        copies = opts.get("copies", 1)
        delete_after = opts.get("delete_after", False)
        
        # Spool destination: .dcl/spool/<queue_name>/<entry_id>_<job_name>.out
        q_dir = os.path.join(self.spool_dir, entry['queue_name'].replace(':', '_').replace('$', '_'))
        os.makedirs(q_dir, exist_ok=True)
        spool_target = os.path.join(q_dir, f"{entry['entry_id']:04d}_{entry['job_name']}.prt")
        
        try:
            with open(entry['file_path'], 'r', errors='ignore') as src, open(spool_target, 'w') as dst:
                header = f"--- DEC RSTS/E Print Spooler ---\nQueue: {entry['queue_name']} Entry: {entry['entry_id']} Job: {entry['job_name']}\nUser: {entry['user_name']} Date: {start_time} Copies: {copies}\n" + ("-"*60) + "\n"
                dst.write(header)
                content = src.read()
                for c_idx in range(copies):
                    if c_idx > 0:
                        dst.write("\n\f\n") # Form feed between copies
                    dst.write(content)
                dst.write("\n" + ("-"*60) + "\n--- End of Spool Output ---\n")
                
            if delete_after and os.path.exists(entry['file_path']):
                os.remove(entry['file_path'])
            success = True
        except Exception as e:
            print(f"Error spooling print job: {e}")
            success = False

        end_time = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        final_status = 'COMPLETED' if success else 'ABORTED'
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("UPDATE entries SET status = ?, end_time = ? WHERE entry_id = ?",
                      (final_status, end_time, entry['entry_id']))
            conn.commit()
            conn.close()
            
        entry['status'] = final_status
        return entry

    def process_all_pending(self, interpreter_runner=None):
        processed = 0
        while True:
            # First process any print jobs
            p_job = self.process_next_print_job()
            if p_job:
                processed += 1
                continue
            # Then process batch jobs
            b_job = self.process_next_batch_job(interpreter_runner)
            if b_job:
                processed += 1
                continue
            break
        return processed

    # ==========================================================================
    # DCL Account Management Subsystem ($ACCT.SYS / SYSUAF)
    # ==========================================================================
    def normalize_account_id(self, raw):
        if not raw:
            return None
        s = raw.strip().upper().strip('"').strip("'")
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1]
            if "," in inner:
                p1, p2 = [x.strip() for x in inner.split(",", 1)]
                if p1.isdigit() and p2.isdigit():
                    return f"[{int(p1)},{int(p2)}]"
            return s
        if "," in s:
            p1, p2 = [x.strip() for x in s.split(",", 1)]
            if p1.isdigit() and p2.isdigit():
                return f"[{int(p1)},{int(p2)}]"
        # Lookup by username
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("SELECT ppn FROM accounts WHERE UPPER(username) = ?", (s,))
            row = c.fetchone()
            conn.close()
            if row:
                return row["ppn"]
        return s

    def create_account(self, acct_spec, username=None, password="", quota=10000, privs="NOPRIV", flags="NODISUSER", directory=None, owner=""):
        s = acct_spec.strip().upper()
        if "," in s.strip("[]"):
            inner = s.strip("[]")
            p1, p2 = [x.strip() for x in inner.split(",", 1)]
            ppn = f"[{int(p1)},{int(p2)}]"
            uname = (username or f"U{int(p1)}_{int(p2)}").upper()
        else:
            uname = s.strip("[]")
            ppn = (username if username and "," in username else "[200,201]")
            if not ppn.startswith("["):
                ppn = f"[{ppn}]"
        if not directory:
            directory = f"DK0:{ppn}"
        if not owner:
            owner = f"Account {uname}"
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("""
            INSERT OR REPLACE INTO accounts (ppn, username, password, quota, privs, flags, directory, owner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ppn, uname, password, int(quota), privs.upper(), flags.upper(), directory, owner))
            conn.commit()
            conn.close()
        return ppn, uname

    def modify_account(self, acct_spec, username=None, password=None, quota=None, privs=None, flags=None, owner=None):
        ppn = self.normalize_account_id(acct_spec)
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM accounts WHERE ppn = ? OR UPPER(username) = ?", (ppn, acct_spec.strip().upper()))
            row = c.fetchone()
            if not row:
                conn.close()
                return False, f"Account {acct_spec} not found"
            curr = dict(row)
            new_user = username.upper() if username else curr["username"]
            new_pw = password if password is not None else curr["password"]
            new_quota = int(quota) if quota is not None else curr["quota"]
            new_privs = privs.upper() if privs else curr["privs"]
            new_flags = flags.upper() if flags else curr["flags"]
            new_owner = owner if owner is not None else curr["owner"]
            c.execute("""
            UPDATE accounts
            SET username = ?, password = ?, quota = ?, privs = ?, flags = ?, owner = ?
            WHERE ppn = ?
            """, (new_user, new_pw, new_quota, new_privs, new_flags, new_owner, curr["ppn"]))
            conn.commit()
            conn.close()
        return True, curr["ppn"]

    def delete_account(self, acct_spec):
        ppn = self.normalize_account_id(acct_spec)
        if ppn in ("[1,1]", "[1,2]", "[1,3]"):
            return False, f"Cannot delete system account {ppn}"
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM accounts WHERE ppn = ? OR UPPER(username) = ?", (ppn, acct_spec.strip().upper()))
            deleted = c.rowcount
            conn.commit()
            conn.close()
        if deleted == 0:
            return False, f"Account {acct_spec} not found"
        return True, ppn

    def list_accounts(self, acct_spec=None):
        with self.lock:
            conn = self._get_connection()
            c = conn.cursor()
            if acct_spec and acct_spec.strip() != "*":
                ppn = self.normalize_account_id(acct_spec)
                c.execute("SELECT * FROM accounts WHERE ppn = ? OR UPPER(username) = ? ORDER BY ppn", (ppn, acct_spec.strip().upper()))
            else:
                c.execute("SELECT * FROM accounts ORDER BY ppn")
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            return rows

    def handle_dcl_account_cmd(self, action, raw_rest=""):
        import shlex
        action = action.upper()
        tokens = []
        quals = {}
        for tok in shlex.split(raw_rest) if raw_rest else []:
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
                tokens.append(subparts[0])
                for part in subparts[1:]:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        quals[k.upper()] = v
                    else:
                        quals[part.upper()] = True
            else:
                if tok.upper() not in ("ACCOUNT", "ACCOUNTS", "PASSWORD"):
                    tokens.append(tok)

        if action == "CREATE":
            if not tokens:
                print("%DCL-E-PARAM, missing account PPN or username for CREATE/ACCOUNT")
                return 1
            spec = tokens[0]
            uname = quals.get("NAME") or quals.get("USER") or (tokens[1] if len(tokens) > 1 else None)
            pw = quals.get("PASSWORD", "")
            quota = int(quals.get("QUOTA", 10000))
            privs = "PRIV" if ("PRIVILEGES" in quals or "PRIV" in quals) else "NOPRIV"
            if isinstance(quals.get("PRIVILEGES"), str):
                privs = quals["PRIVILEGES"]
            flags = quals.get("FLAGS", "NODISUSER")
            owner = quals.get("OWNER", "")
            ppn, final_user = self.create_account(spec, username=uname, password=pw, quota=quota, privs=privs, flags=flags, owner=owner)
            print(f"%ACC-S-CREATED, account {ppn} ({final_user}) created [Quota={quota}, Priv={privs}]")
            return 0

        if action in ("MODIFY", "SET_ACCOUNT"):
            if not tokens:
                print("%DCL-E-PARAM, missing account PPN or username for MODIFY/ACCOUNT")
                return 1
            spec = tokens[0]
            uname = quals.get("NAME") or quals.get("USER")
            pw = quals.get("PASSWORD") if "PASSWORD" in quals else None
            quota = int(quals["QUOTA"]) if "QUOTA" in quals else None
            privs = None
            if "PRIVILEGES" in quals or "PRIV" in quals:
                privs = quals.get("PRIVILEGES") if isinstance(quals.get("PRIVILEGES"), str) else "PRIV"
            elif "NOPRIVILEGES" in quals or "NOPRIV" in quals:
                privs = "NOPRIV"
            flags = quals.get("FLAGS") if isinstance(quals.get("FLAGS"), str) else None
            if "DISUSER" in quals:
                flags = "DISUSER"
            elif "NODISUSER" in quals:
                flags = "NODISUSER"
            owner = quals.get("OWNER")
            ok, msg = self.modify_account(spec, username=uname, password=pw, quota=quota, privs=privs, flags=flags, owner=owner)
            if not ok:
                print(f"%ACC-E-NOTFND, {msg}")
                return 1
            print(f"%ACC-S-MODIFIED, account {msg} attributes updated")
            return 0

        if action == "DELETE":
            if not tokens:
                print("%DCL-E-PARAM, missing account PPN or username for DELETE/ACCOUNT")
                return 1
            ok, msg = self.delete_account(tokens[0])
            if not ok:
                print(f"%ACC-E-DELERR, cannot delete protected system account or {msg}")
                return 1
            print(f"%ACC-S-DELETED, account {msg} deleted from system account table")
            return 0

        if action == "SHOW":
            spec = tokens[0] if tokens else None
            full = "FULL" in quals
            rows = self.list_accounts(spec)
            if not rows:
                print(f"%ACC-W-NOACCT, account {spec} not found")
                return 1
            if full:
                for r in rows:
                    print(f"Account PPN:   {r['ppn']} ({r['username']})")
                    print(f"  Owner:       {r['owner']}")
                    print(f"  Directory:   {r['directory']}")
                    print(f"  Disk Quota:  {r['quota']} blocks")
                    print(f"  Privileges:  {r['privs']}")
                    print(f"  Login Flags: {r['flags']}")
                    print(f"  Password:    {'<set>' if r['password'] else '<none>'}")
                    print("")
            else:
                print("PPN        Username    Quota     Privs    Flags       Directory      Owner")
                print("---------  ----------  --------  -------  ----------  -------------  -------------------------")
                for r in rows:
                    print(f"{r['ppn']:<9}  {r['username']:<10}  {r['quota']:>8}  {r['privs']:<7}  {r['flags']:<10}  {r['directory']:<13}  {r['owner']}")
            return 0

        if action == "SET_PASSWORD":
            target = quals.get("ACCOUNT") or quals.get("USER") or (tokens[0] if len(tokens) > 1 else "[1,2]")
            if "GENERATE" in quals:
                new_pw = "DEC$9472"
            elif "PASSWORD" in quals and isinstance(quals["PASSWORD"], str):
                new_pw = quals["PASSWORD"]
            elif tokens:
                new_pw = tokens[-1]
            else:
                new_pw = "UPDATED"
            ok, msg = self.modify_account(target, password=new_pw)
            if not ok:
                print(f"%SET-E-PASSERR, {msg}")
                return 1
            print(f"%SET-S-PASSCHG, password updated for account {msg}")
            return 0

        return 1

def main():
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(description="DEC RSTS/E Job Control & Queue Subsystem CLI")
    parser.add_argument("--base-dir", default=None, help="Base directory for .dcl state")
    subparsers = parser.add_subparsers(dest="subcommand")
    
    # submit-print
    p_print = subparsers.add_parser("submit-print")
    p_print.add_argument("file")
    p_print.add_argument("--queue", default="SYS$PRINT")
    p_print.add_argument("--name", default=None)
    p_print.add_argument("--copies", type=int, default=1)
    p_print.add_argument("--delete", action="store_true")
    
    # submit-batch
    p_batch = subparsers.add_parser("submit-batch")
    p_batch.add_argument("file")
    p_batch.add_argument("--queue", default="SYS$BATCH")
    p_batch.add_argument("--name", default=None)
    p_batch.add_argument("--log", default=None)
    
    # show-queue
    p_sq = subparsers.add_parser("show-queue")
    p_sq.add_argument("queue", nargs="?", default=None)
    p_sq.add_argument("--all", action="store_true")
    p_sq.add_argument("--full", action="store_true")
    
    # show-jobs
    p_sj = subparsers.add_parser("show-jobs")
    p_sj.add_argument("--all", action="store_true")
    
    # show-entry
    p_se = subparsers.add_parser("show-entry")
    p_se.add_argument("entry", nargs="?", default=None)
    
    # delete-entry
    p_de = subparsers.add_parser("delete-entry")
    p_de.add_argument("entry", type=int)
    
    # start-queue
    p_st = subparsers.add_parser("start-queue")
    p_st.add_argument("queue")
    
    # stop-queue
    p_sp = subparsers.add_parser("stop-queue")
    p_sp.add_argument("queue")
    
    # process-pending
    subparsers.add_parser("process-pending")

    # dir
    p_dir = subparsers.add_parser("dir")
    p_dir.add_argument("pattern", nargs="?", default="*")

    # dcl-account
    p_acc = subparsers.add_parser("dcl-account")
    p_acc.add_argument("action")
    p_acc.add_argument("rest", nargs="?", default="")
    
    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(1)
        
    jc = JobController(base_dir=args.base_dir)
    
    if args.subcommand == "submit-print":
        try:
            entry_id, final_job_name, final_q_name = jc.submit_print_job(
                file_path=os.path.abspath(args.file),
                queue_name=args.queue,
                job_name=args.name,
                user_name="SYSTEM",
                copies=args.copies,
                delete_after=args.delete
            )
            print(f"Job {final_job_name} (entry {entry_id}) submitted to queue {final_q_name}")
            if not jc.is_print_service_running():
                jc.process_all_pending()
        except Exception as e:
            print(f"%DCL-E-PRINTERR, error submitting print job: {e}")
            sys.exit(2)
            
    elif args.subcommand == "submit-batch":
        try:
            opts = {"log_file": args.log} if args.log else {}
            entry_id, final_job_name, final_q_name = jc.submit_batch_job(
                file_path=os.path.abspath(args.file),
                queue_name=args.queue,
                job_name=args.name,
                user_name="SYSTEM",
                options=opts
            )
            print(f"Job {final_job_name} (entry {entry_id}) submitted to queue {final_q_name}")
            jc.process_all_pending()
        except Exception as e:
            print(f"%DCL-E-SUBMITERR, error submitting batch job: {e}")
            sys.exit(2)
            
    elif args.subcommand == "show-queue":
        all_entries = args.all or args.full
        queues = jc.list_queues(args.queue)
        if not queues:
            print(f"%DCL-W-NOQUEUE, queue {args.queue} not found")
            return
        out = []
        out.append("Terminal / Print / Batch Queue Status\n")
        for q in queues:
            q_name = q['name']
            q_type = q['type']
            q_status = q['status']
            entries = jc.list_entries(queue_name=q_name, all_entries=all_entries)
            out.append(f"Queue {q_name:<10} ({q_type}, status: {q_status}, Active: {len([e for e in entries if e['status']=='EXECUTING'])})")
            if entries:
                out.append("  Entry  Job Name         User         Status       Submitted")
                out.append("  -----  ---------------  -----------  -----------  --------------------")
                for e in entries:
                    out.append(f"  {e['entry_id']:>5}  {e['job_name']:<15}  {e['user_name']:<11}  {e['status']:<11}  {e['submit_time']}")
            else:
                out.append("  (No active entries)")
            out.append("")
        print("\n".join(out).strip())
        
    elif args.subcommand == "show-jobs":
        entries = jc.list_entries(all_entries=args.all)
        out = []
        out.append("System Job Table\n")
        out.append("Entry  Queue       Job Name         Status       File / Procedure")
        out.append("-----  ----------  ---------------  -----------  ------------------------------")
        for e in entries:
            file_short = os.path.basename(e['file_path'])
            out.append(f"{e['entry_id']:>5}  {e['queue_name']:<10}  {e['job_name']:<15}  {e['status']:<11}  {file_short}")
        if not entries:
            out.append("(No queue entries found)")
        print("\n".join(out))
        
    elif args.subcommand == "show-entry":
        if args.entry and args.entry.isdigit():
            entry_id = int(args.entry)
            e = jc.get_entry(entry_id)
            if not e:
                print(f"%DCL-W-NOENTRY, queue entry {entry_id} not found")
                sys.exit(1)
            file_short = os.path.basename(e['file_path'])
            out = [
                "Entry  Job Name         User         Status       Queue       Submitted",
                "-----  ---------------  -----------  -----------  ----------  --------------------",
                f"{e['entry_id']:>5}  {e['job_name']:<15}  {e['user_name']:<11}  {e['status']:<11}  {e['queue_name']:<10}  {e['submit_time']}",
                f"  File: {file_short}"
            ]
            print("\n".join(out))
        else:
            entries = jc.list_entries(all_entries=True)
            if not entries:
                print("(No queue entries found)")
                return
            out = []
            out.append("Entry  Job Name         User         Status       Queue       Submitted")
            out.append("-----  ---------------  -----------  -----------  ----------  --------------------")
            for e in entries:
                out.append(f"{e['entry_id']:>5}  {e['job_name']:<15}  {e['user_name']:<11}  {e['status']:<11}  {e['queue_name']:<10}  {e['submit_time']}")
            print("\n".join(out))
            
    elif args.subcommand == "delete-entry":
        success, msg = jc.delete_entry(args.entry)
        if success:
            print(f"Entry {args.entry} deleted from queue")
        else:
            print(f"%DCL-E-DELERR, error deleting entry {args.entry}: {msg}")
            sys.exit(1)
            
    elif args.subcommand == "start-queue":
        if jc.start_queue(args.queue):
            print(f"Queue {args.queue} started")
        else:
            print(f"%DCL-W-NOQUEUE, queue {args.queue} not found")
            sys.exit(1)
            
    elif args.subcommand == "stop-queue":
        if jc.stop_queue(args.queue):
            print(f"Queue {args.queue} stopped")
        else:
            print(f"%DCL-W-NOQUEUE, queue {args.queue} not found")
            sys.exit(1)
            
    elif args.subcommand == "process-pending":
        n = jc.process_all_pending()
        print(f"Processed {n} pending job(s).")

    elif args.subcommand == "dir":
        pattern = args.pattern or "*"
        if not os.path.isabs(pattern):
            pattern = os.path.join(os.getcwd(), pattern)
        files = glob.glob(pattern)
        out = [f"Directory {os.getcwd()}\n"]
        total_blocks = 0
        for f in sorted(files):
            basename = os.path.basename(f)
            stat = os.stat(f)
            size_kb = (stat.st_size + 511) // 512
            total_blocks += size_kb
            dt = datetime.fromtimestamp(stat.st_mtime).strftime("%d-%b-%Y %H:%M")
            out.append(f"{basename:<24} {size_kb:>6}  {dt}")
        out.append(f"\nTotal of {len(files)} files, {total_blocks} blocks.")
        print("\n".join(out))

    elif args.subcommand == "dcl-account":
        rc = jc.handle_dcl_account_cmd(args.action, args.rest)
        sys.exit(rc)

if __name__ == "__main__":
    main()
