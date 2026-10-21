import os
import sys
import glob
import subprocess
import shutil
import time
import re
from datetime import datetime
from dcl.dcl_parser import DCLParsedCommand
from dcl.job_controller import JobController

class DCLInterpreter:
    def __init__(self, repo_root=None, job_controller=None):
        if repo_root is None:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.repo_root = repo_root
        self.current_dir = os.getcwd()
        self.job_controller = job_controller or JobController(base_dir=os.path.join(self.repo_root, ".dcl"))
        
        self.symbols = {
            "$STATUS": "1",
            "$SEVERITY": "1",
            "SYS$SYSTEM": self.repo_root,
        }
        self.logicals = {
            "SYS$OUTPUT": "TT:",
            "SYS$INPUT": "TT:",
            "SYS$ERROR": "TT:",
            "SYS$SYSTEM": self.repo_root
        }
        self.verify = False
        self.exit_requested = False

    def execute_line(self, line):
        cmd = DCLParsedCommand(line)
        if cmd.is_comment:
            return 0, ""

        if cmd.is_assignment:
            self.symbols[cmd.assign_var] = cmd.assign_val
            return 0, ""

        if not cmd.verb:
            return 0, ""

        return self.dispatch(cmd)

    def resolve_path(self, path):
        if not path:
            return path
        candidates = []
        if os.path.isabs(path):
            candidates.append(path)
        else:
            candidates.append(os.path.join(self.current_dir, path))
            proc_dir = getattr(self, 'current_proc_dir', None)
            if proc_dir:
                candidates.append(os.path.join(proc_dir, path))

        for cand in candidates:
            if os.path.exists(cand):
                return cand
            d, f = os.path.split(cand)
            if not d:
                d = "."
            if os.path.isdir(d):
                f_lower = f.lower()
                for item in os.listdir(d):
                    if item.lower() == f_lower:
                        return os.path.join(d, item)

        if not os.path.isabs(path):
            return os.path.join(self.current_dir, path)
        return path

    def execute_procedure(self, filepath, parameters=None):
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.current_dir, filepath)
            
        if not os.path.exists(filepath):
            # Try appending .COM or .DCL
            if os.path.exists(filepath + ".COM") or os.path.exists(filepath + ".com"):
                filepath = filepath + ".COM" if os.path.exists(filepath + ".COM") else filepath + ".com"
            elif os.path.exists(filepath + ".DCL") or os.path.exists(filepath + ".dcl"):
                filepath = filepath + ".DCL" if os.path.exists(filepath + ".DCL") else filepath + ".dcl"
            else:
                return 1, f"%DCL-E-OPENIN, error opening {filepath} as input\n-RMS-E-FNF, file not found"

        prev_proc_dir = getattr(self, 'current_proc_dir', None)
        self.current_proc_dir = os.path.dirname(os.path.abspath(filepath))

        with open(filepath, 'r', errors='ignore') as f:
            lines = [line.rstrip('\r\n') for line in f]

        # Scan labels
        labels = {}
        for idx, line in enumerate(lines):
            cmd = DCLParsedCommand(line)
            if cmd.label:
                labels[cmd.label] = idx

        # Set up P1..P8 parameters
        old_params = {}
        for i in range(1, 9):
            param_key = f"P{i}"
            old_params[param_key] = self.symbols.get(param_key)
            if parameters and i <= len(parameters):
                self.symbols[param_key] = str(parameters[i - 1])
            else:
                self.symbols[param_key] = ""

        output_lines = []
        pc = 0
        status_code = 0

        while pc < len(lines):
            raw_line = lines[pc]
            pc += 1

            if self.verify and raw_line.strip() and not raw_line.strip().startswith('!'):
                output_lines.append(f"$ {raw_line.strip()}")

            cmd = DCLParsedCommand(raw_line)
            if cmd.is_comment and not cmd.label:
                continue

            if cmd.is_assignment:
                self.symbols[cmd.assign_var] = cmd.assign_val
                continue

            if not cmd.verb:
                continue

            # Special IF flow control in procedure
            if cmd.verb == "IF":
                cond_true, then_stmt = self.evaluate_if(raw_line)
                if cond_true:
                    then_cmd = DCLParsedCommand(then_stmt)
                    if then_cmd.verb == "GOTO" and then_cmd.args:
                        target_label = then_cmd.args[0].upper()
                        if target_label in labels:
                            pc = labels[target_label] + 1
                            continue
                        else:
                            output_lines.append(f"%DCL-W-UNDLABEL, label {target_label} not found")
                            status_code = 2
                            break
                    elif then_cmd.verb in ["EXIT", "STOP"] and not ('QUEUE' in then_cmd.qualifiers):
                        break
                    else:
                        code, out = self.dispatch(then_cmd)
                        if out:
                            output_lines.append(out)
                        self.symbols["$STATUS"] = str(code)
                        if code != 0:
                            status_code = code
                continue

            # Special GOTO flow control
            if cmd.verb == "GOTO":
                if cmd.args:
                    target_label = cmd.args[0].upper()
                    if target_label in labels:
                        pc = labels[target_label] + 1
                        continue
                    else:
                        out = f"%DCL-W-UNDLABEL, label {target_label} not found"
                        output_lines.append(out)
                        status_code = 2
                        break
                continue

            # EXIT / STOP
            if cmd.verb in ["EXIT", "STOP"] and not ('QUEUE' in cmd.qualifiers):
                break

            code, out = self.dispatch(cmd)
            if out:
                output_lines.append(out)
            self.symbols["$STATUS"] = str(code)
            if code != 0:
                status_code = code

        # Restore parameters
        for k, v in old_params.items():
            if v is not None:
                self.symbols[k] = v
            else:
                self.symbols.pop(k, None)

        self.current_proc_dir = prev_proc_dir
        return status_code, "\n".join(output_lines)

    def dispatch(self, cmd: DCLParsedCommand):
        verb = cmd.verb
        
        # Check procedure call (@file)
        if verb.startswith('@'):
            proc_file = verb[1:] if len(verb) > 1 else (cmd.args[0] if cmd.args else "")
            return self.execute_procedure(proc_file, cmd.args[1:] if len(verb) == 1 else cmd.args)

        # Dispatch table
        methods = {
            "HELP": self.cmd_help,
            "SHOW": self.cmd_show,
            "SUBMIT": self.cmd_submit,
            "PRINT": self.cmd_print,
            "DELETE": self.cmd_delete,
            "STOP": self.cmd_stop,
            "START": self.cmd_start,
            "BASIC": self.cmd_basic,
            "COMPILE": self.cmd_basic,
            "LINK": self.cmd_link,
            "RUN": self.cmd_run,
            "DIR": self.cmd_directory,
            "DIRECTORY": self.cmd_directory,
            "TYPE": self.cmd_type,
            "COPY": self.cmd_copy,
            "RENAME": self.cmd_rename,
            "SET": self.cmd_set,
            "WRITE": self.cmd_write,
            "WAIT": self.cmd_wait,
            "IF": self.cmd_if,
            "ASSIGN": self.cmd_assign,
            "DEFINE": self.cmd_assign,
            "DEASSIGN": self.cmd_deassign,
            "CREATE": self.cmd_create,
            "MODIFY": self.cmd_modify,
            "AUTHORIZE": self.cmd_authorize,
            "EXIT": self.cmd_exit,
            "LOGOUT": self.cmd_exit,
            "BYE": self.cmd_exit
        }

        handler = methods.get(verb)
        if handler:
            return handler(cmd)
        else:
            return 1, f"%DCL-W-IVVERB, unrecognized command verb '{verb}' - check validity and spelling"

    def cmd_help(self, cmd):
        topic = cmd.args[0].upper() if cmd.args else ""
        if not topic:
            return 0, """RSTS/E DIGITAL Command Language (DCL) & Job Control (PBS) Help

Available Commands:
  SUBMIT       - Submit a command procedure (.COM) to the batch queue
  PRINT        - Submit a file to the print queue
  SHOW QUEUE   - Display status of batch and print queues
  SHOW JOBS    - Display queue entries and active processes
  SHOW SYSTEM  - Display system and environment status
  DELETE/ENTRY - Remove or cancel an entry from the queue
  START/QUEUE  - Open or resume a queue
  STOP/QUEUE   - Pause a queue
  BASIC        - Compile a BASIC-PLUS-2 source file (.BAS)
  LINK         - Link compiled BASIC object files (.OBJ) into executable
  RUN          - Execute a compiled program
  DIRECTORY    - List files in current or specified directory
  TYPE         - Display contents of a file
  COPY/RENAME  - Copy or rename files
  SET DEFAULT  - Change default directory
  WRITE        - Write output to SYS$OUTPUT
  @file        - Execute DCL command procedure (.COM)
  EXIT/LOGOUT  - End DCL session

Type HELP <command> for additional information."""
        
        help_topics = {
            "SUBMIT": "SUBMIT <file.com> [/QUEUE=queue] [/NAME=job_name] [/LOG=log_file]\nSubmits a command procedure to the batch queue (default: SYS$BATCH).",
            "PRINT": "PRINT <file> [/QUEUE=queue] [/COPIES=n] [/NAME=job_name] [/DELETE]\nSubmits a file to the print queue (default: SYS$PRINT).",
            "SHOW": "SHOW QUEUE [name] [/ALL] [/FULL]\nSHOW JOBS\nSHOW SYSTEM\nSHOW TIME\nSHOW SYMBOL <name>",
            "BASIC": "BASIC <file.bas> [/MODULE=name]\nCompiles DEC BASIC-PLUS-2 source file into bytecode object (.OBJ).",
            "LINK": "LINK <file.obj> [/OUTPUT=target]\nLinks .OBJ modules into a runnable binary.",
            "RUN": "RUN <file>\nExecutes a compiled BASIC-PLUS-2 executable."
        }
        return 0, help_topics.get(topic, f"No specific help topic available for {topic}")

    def cmd_submit(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-NOFILE, missing command procedure filename"
            
        file_path = self.resolve_path(cmd.args[0])
        if not os.path.exists(file_path):
            cand = self.resolve_path(cmd.args[0] + ".com")
            if os.path.exists(cand):
                file_path = cand
            else:
                cand_dcl = self.resolve_path(cmd.args[0] + ".dcl")
                if os.path.exists(cand_dcl):
                    file_path = cand_dcl

        queue_name = cmd.qualifiers.get("QUEUE", "SYS$BATCH")
        job_name = cmd.qualifiers.get("NAME")
        log_file = cmd.qualifiers.get("LOG")
        
        opts = {}
        if log_file:
            opts["log_file"] = log_file

        try:
            entry_id, final_job_name, final_q_name = self.job_controller.submit_batch_job(
                file_path=file_path,
                queue_name=queue_name,
                job_name=job_name,
                user_name="SYSTEM",
                options=opts
            )
            msg = f"Job {final_job_name} (entry {entry_id}) submitted to queue {final_q_name}"
            
            # Immediately process in background or synchronously if queue is open
            self.job_controller.process_all_pending(interpreter_runner=self.execute_procedure)
            return 0, msg
        except Exception as e:
            return 2, f"%DCL-E-SUBMITERR, error submitting batch job: {e}"

    def cmd_print(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-NOFILE, missing filename to print"
            
        file_path = self.resolve_path(cmd.args[0])
            
        queue_name = cmd.qualifiers.get("QUEUE", "SYS$PRINT")
        job_name = cmd.qualifiers.get("NAME")
        copies = int(cmd.qualifiers.get("COPIES", 1))
        delete_after = "DELETE" in cmd.qualifiers
        
        try:
            entry_id, final_job_name, final_q_name = self.job_controller.submit_print_job(
                file_path=file_path,
                queue_name=queue_name,
                job_name=job_name,
                user_name="SYSTEM",
                copies=copies,
                delete_after=delete_after
            )
            msg = f"Job {final_job_name} (entry {entry_id}) submitted to queue {final_q_name}"
            if not self.job_controller.is_print_service_running():
                self.job_controller.process_all_pending(interpreter_runner=self.execute_procedure)
            return 0, msg
        except Exception as e:
            return 2, f"%DCL-E-PRINTERR, error submitting print job: {e}"

    def cmd_show(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-PARAM, missing SHOW parameter (QUEUE, JOBS, SYSTEM, TIME, SYMBOL, LOGICAL)"
            
        sub = cmd.args[0].upper()
        if sub in ["QUEUE", "QUEUES"]:
            target_q = cmd.args[1] if len(cmd.args) > 1 else None
            all_entries = ("ALL" in cmd.qualifiers) or ("FULL" in cmd.qualifiers)
            queues = self.job_controller.list_queues(target_q)
            if not queues:
                return 0, f"%DCL-W-NOQUEUE, queue {target_q} not found"
                
            out = []
            out.append("Terminal / Print / Batch Queue Status\n")
            for q in queues:
                q_name = q['name']
                q_type = q['type']
                q_status = q['status']
                entries = self.job_controller.list_entries(queue_name=q_name, all_entries=all_entries)
                
                out.append(f"Queue {q_name:<10} ({q_type}, status: {q_status}, Active: {len([e for e in entries if e['status']=='EXECUTING'])})")
                if entries:
                    out.append("  Entry  Job Name         User         Status       Submitted")
                    out.append("  -----  ---------------  -----------  -----------  --------------------")
                    for e in entries:
                        out.append(f"  {e['entry_id']:>5}  {e['job_name']:<15}  {e['user_name']:<11}  {e['status']:<11}  {e['submit_time']}")
                else:
                    out.append("  (No active entries)")
                out.append("")
            return 0, "\n".join(out).strip()

        elif sub in ["JOB", "JOBS"]:
            all_entries = "ALL" in cmd.qualifiers
            entries = self.job_controller.list_entries(all_entries=all_entries)
            out = []
            out.append("System Job Table\n")
            out.append("Entry  Queue       Job Name         Status       File / Procedure")
            out.append("-----  ----------  ---------------  -----------  ------------------------------")
            for e in entries:
                file_short = os.path.basename(e['file_path'])
                out.append(f"{e['entry_id']:>5}  {e['queue_name']:<10}  {e['job_name']:<15}  {e['status']:<11}  {file_short}")
            if not entries:
                out.append("(No queue entries found)")
            return 0, "\n".join(out)

        elif sub in ["ENTRY", "ENTRIES"]:
            if len(cmd.args) > 1 and cmd.args[1].isdigit():
                entry_id = int(cmd.args[1])
                e = self.job_controller.get_entry(entry_id)
                if not e:
                    return 1, f"%DCL-W-NOENTRY, queue entry {entry_id} not found"
                file_short = os.path.basename(e['file_path'])
                out = [
                    "Entry  Job Name         User         Status       Queue       Submitted",
                    "-----  ---------------  -----------  -----------  ----------  --------------------",
                    f"{e['entry_id']:>5}  {e['job_name']:<15}  {e['user_name']:<11}  {e['status']:<11}  {e['queue_name']:<10}  {e['submit_time']}",
                    f"  File: {file_short}"
                ]
                return 0, "\n".join(out)
            else:
                entries = self.job_controller.list_entries(all_entries=True)
                if not entries:
                    return 0, "(No queue entries found)"
                out = []
                out.append("Entry  Job Name         User         Status       Queue       Submitted")
                out.append("-----  ---------------  -----------  -----------  ----------  --------------------")
                for e in entries:
                    out.append(f"{e['entry_id']:>5}  {e['job_name']:<15}  {e['user_name']:<11}  {e['status']:<11}  {e['queue_name']:<10}  {e['submit_time']}")
                return 0, "\n".join(out)

        elif sub == "SYSTEM":
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
            return 0, f"""DEC RSTS/E V10.1-L Environment
Host Platform: Linux Bytecode VM
System Time:   {now_str}
Compiler:      BASIC-PLUS-2 Python Frontend / C Runtime VM
Job Subsystem: Print/Batch Services (PBS) Active
Default Dir:   {self.current_dir}"""

        elif sub in ["TIME", "DATE"]:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
            return 0, now_str

        elif sub == "DEFAULT":
            return 0, self.current_dir

        elif sub in ["SYMBOL", "SYMBOLS"]:
            if len(cmd.args) > 1:
                sym = cmd.args[1].upper()
                if sym in self.symbols:
                    return 0, f"  {sym} = \"{self.symbols[sym]}\""
                return 1, f"%DCL-W-UNDSYM, undefined symbol '{sym}'"
            out = ["DCL Symbols:"]
            for k, v in sorted(self.symbols.items()):
                out.append(f"  {k} = \"{v}\"")
            return 0, "\n".join(out)

        elif sub in ["LOGICAL", "LOGICALS", "TRANSLATION"]:
            out = ["Logical Names:"]
            for k, v in sorted(self.logicals.items()):
                out.append(f"  \"{k}\" = \"{v}\"")
            return 0, "\n".join(out)

        elif sub in ["ACCOUNT", "ACCOUNTS"]:
            return self._exec_account_action("SHOW", cmd)

        return 1, f"%DCL-E-IVKEYW, unrecognized SHOW keyword '{sub}'"

    def _exec_account_action(self, action, cmd):
        import io
        from contextlib import redirect_stdout
        raw = cmd.raw_line.strip().lstrip("$").strip()
        parts = raw.split(None, 1)
        rest = parts[1] if len(parts) > 1 else ""
        if "/" in parts[0]:
            rest = "/" + parts[0].split("/", 1)[1] + " " + rest
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = self.job_controller.handle_dcl_account_cmd(action, rest.strip())
        return rc, buf.getvalue().rstrip()

    def cmd_create(self, cmd):
        return self._exec_account_action("CREATE", cmd)

    def cmd_modify(self, cmd):
        return self._exec_account_action("MODIFY", cmd)

    def cmd_authorize(self, cmd):
        return self._exec_account_action("SHOW", cmd)

    def cmd_delete(self, cmd):
        if "ENTRY" in cmd.qualifiers:
            entry_id = int(cmd.qualifiers["ENTRY"])
            success, msg = self.job_controller.delete_entry(entry_id)
            if success:
                return 0, f"Entry {entry_id} deleted from queue"
            return 1, f"%DCL-E-DELERR, error deleting entry {entry_id}: {msg}"

        if "ACCOUNT" in cmd.qualifiers or (cmd.args and cmd.args[0].upper() == "ACCOUNT"):
            return self._exec_account_action("DELETE", cmd)
            
        if not cmd.args:
            return 1, "%DCL-E-PARAM, missing file or qualifier for DELETE"
            
        target_file = cmd.args[0]
        if not os.path.isabs(target_file):
            target_file = os.path.join(self.current_dir, target_file)
        if os.path.exists(target_file):
            os.remove(target_file)
            return 0, f"%DCL-I-DELETED, file {target_file} deleted"
        return 1, f"%DCL-W-FILNOTFND, file {target_file} not found"

    def cmd_start(self, cmd):
        if "QUEUE" in cmd.qualifiers or (cmd.args and cmd.args[0].upper() == "QUEUE"):
            q_name = cmd.qualifiers.get("QUEUE")
            if not q_name and len(cmd.args) > 1:
                q_name = cmd.args[1]
            if not q_name:
                return 1, "%DCL-E-PARAM, missing queue name"
            if self.job_controller.start_queue(q_name):
                return 0, f"Queue {q_name} started"
            return 1, f"%DCL-W-NOQUEUE, queue {q_name} not found"
        return 1, "%DCL-E-PARAM, unrecognized START option"

    def cmd_stop(self, cmd):
        if "QUEUE" in cmd.qualifiers or (cmd.args and cmd.args[0].upper() == "QUEUE"):
            q_name = cmd.qualifiers.get("QUEUE")
            if not q_name and len(cmd.args) > 1:
                q_name = cmd.args[1]
            if not q_name:
                return 1, "%DCL-E-PARAM, missing queue name"
            if self.job_controller.stop_queue(q_name):
                return 0, f"Queue {q_name} stopped"
            return 1, f"%DCL-W-NOQUEUE, queue {q_name} not found"
        return 0, ""

    def cmd_basic(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-NOFILE, missing BASIC source filename"
        raw_src = cmd.args[0]
        if not raw_src.lower().endswith(".bas"):
            cand = self.resolve_path(raw_src + ".bas")
            if os.path.exists(cand):
                src_file = cand
            else:
                src_file = self.resolve_path(raw_src)
        else:
            src_file = self.resolve_path(raw_src)

        basicc_py = os.path.join(self.repo_root, "compiler", "basicc.py")
        default_obj = os.path.splitext(src_file)[0] + ".OBJ"
        out_obj = cmd.qualifiers.get("OBJECT", default_obj)
        
        c_args = [sys.executable, basicc_py, src_file, "-o", out_obj]
        if "MODULE" in cmd.qualifiers:
            c_args.extend(["--module", cmd.qualifiers["MODULE"]])

        res = subprocess.run(c_args, cwd=self.current_dir, capture_output=True, text=True)
        out = (res.stdout + "\n" + res.stderr).strip()
        return res.returncode, out

    def cmd_link(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-NOFILE, missing object filename to link"
        raw_obj = cmd.args[0]
        obj_file = self.resolve_path(raw_obj)
        if not os.path.exists(obj_file) or (os.path.isfile(obj_file) and os.access(obj_file, os.X_OK)):
            stem_q, _ = os.path.splitext(raw_obj)
            for ext_cand in (".OBJ", ".obj"):
                cand = self.resolve_path(stem_q + ext_cand)
                if os.path.exists(cand):
                    obj_file = cand
                    break

        output_file = cmd.qualifiers.get("OUTPUT", os.path.splitext(obj_file)[0])
        basiclink_py = os.path.join(self.repo_root, "compiler", "basiclink.py")
        
        link_args = [sys.executable, basiclink_py, "-o", output_file, obj_file]
        for extra in cmd.args[1:]:
            link_args.append(extra)

        res = subprocess.run(link_args, cwd=self.current_dir, capture_output=True, text=True)
        out = (res.stdout + "\n" + res.stderr).strip()
        return res.returncode, out

    def cmd_run(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-NOFILE, missing program to run"
        prog_arg = cmd.args[0]
        prog = self.resolve_path(prog_arg)
        run_cwd = os.path.dirname(prog) if os.path.dirname(prog) and os.path.exists(prog) else self.current_dir
            
        if os.path.exists(prog) and os.access(prog, os.X_OK):
            res = subprocess.run([prog], cwd=run_cwd, capture_output=True, text=True)
            out = (res.stdout + "\n" + res.stderr).strip()
            return res.returncode, out
            
        bin_cand = self.resolve_path(prog_arg + ".bin")
        if not os.path.exists(bin_cand):
            bin_cand = self.resolve_path(prog + ".bin")
        if os.path.exists(bin_cand):
            bin_cwd = os.path.dirname(bin_cand) if os.path.dirname(bin_cand) else self.current_dir
            vm_exe = os.path.join(self.repo_root, "vm", "build", "rsts_vm")
            res = subprocess.run([vm_exe, bin_cand], cwd=bin_cwd, capture_output=True, text=True)
            out = (res.stdout + "\n" + res.stderr).strip()
            return res.returncode, out
        return 1, f"%DCL-E-FILNOTFND, executable {prog_arg} not found"

    def cmd_directory(self, cmd):
        pattern = cmd.args[0] if cmd.args else "*"
        if not os.path.isabs(pattern):
            pattern = os.path.join(self.current_dir, pattern)
        files = glob.glob(pattern)
        out = []
        out.append(f"Directory {self.current_dir}\n")
        total_blocks = 0
        for f in sorted(files):
            basename = os.path.basename(f)
            stat = os.stat(f)
            size_kb = (stat.st_size + 511) // 512
            total_blocks += size_kb
            dt = datetime.fromtimestamp(stat.st_mtime).strftime("%d-%b-%Y %H:%M")
            out.append(f"{basename:<24} {size_kb:>6}  {dt}")
        out.append(f"\nTotal of {len(files)} files, {total_blocks} blocks.")
        return 0, "\n".join(out)

    def cmd_type(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-NOFILE, missing file to display"
        fpath = self.resolve_path(cmd.args[0])
        if not os.path.exists(fpath):
            return 1, f"%DCL-W-FILNOTFND, file {fpath} not found"
        with open(fpath, 'r', errors='ignore') as f:
            return 0, f.read().rstrip()

    def cmd_copy(self, cmd):
        if len(cmd.args) < 2:
            return 1, "%DCL-E-PARAM, missing source or destination"
        src, dst = cmd.args[0], cmd.args[1]
        if not os.path.isabs(src): src = os.path.join(self.current_dir, src)
        if not os.path.isabs(dst): dst = os.path.join(self.current_dir, dst)
        shutil.copy2(src, dst)
        return 0, f"%DCL-I-COPIED, copied {src} to {dst}"

    def cmd_rename(self, cmd):
        if len(cmd.args) < 2:
            return 1, "%DCL-E-PARAM, missing source or destination"
        src, dst = cmd.args[0], cmd.args[1]
        if not os.path.isabs(src): src = os.path.join(self.current_dir, src)
        if not os.path.isabs(dst): dst = os.path.join(self.current_dir, dst)
        os.rename(src, dst)
        return 0, f"%DCL-I-RENAMED, renamed {src} to {dst}"

    def cmd_set(self, cmd):
        if not cmd.args:
            return 1, "%DCL-E-PARAM, missing SET parameter"
        sub = cmd.args[0].upper()
        if sub in ["DEFAULT", "DEF"]:
            if len(cmd.args) < 2:
                return 1, "%DCL-E-PARAM, missing directory path"
            new_dir = cmd.args[1]
            if not os.path.isabs(new_dir):
                new_dir = os.path.abspath(os.path.join(self.current_dir, new_dir))
            if os.path.isdir(new_dir):
                self.current_dir = new_dir
                return 0, ""
            return 1, f"%DCL-W-DIRNOTFND, directory {new_dir} not found"
        elif sub == "VERIFY":
            self.verify = True
            return 0, ""
        elif sub == "NOVERIFY":
            self.verify = False
            return 0, ""
        elif sub == "ACCOUNT":
            return self._exec_account_action("SET_ACCOUNT", cmd)
        elif sub == "PASSWORD":
            return self._exec_account_action("SET_PASSWORD", cmd)
        return 1, f"%DCL-W-IVKEYW, unrecognized SET option '{sub}'"

    def cmd_write(self, cmd):
        # Format: WRITE SYS$OUTPUT "text" or symbols
        args = list(cmd.args)
        if args and args[0].upper() in ["SYS$OUTPUT", "TT:", "TT"]:
            args.pop(0)
        text = " ".join(args)
        # Symbol substitution if text starts with ' and ends with '
        for sym_name, sym_val in self.symbols.items():
            text = text.replace(f"'{sym_name}'", sym_val)
        return 0, text

    def cmd_wait(self, cmd):
        duration = 1.0
        if cmd.args:
            val = cmd.args[0]
            if ':' in val:
                parts = val.split(':')
                duration = int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
            else:
                try:
                    duration = float(val)
                except ValueError:
                    duration = 1.0
        time.sleep(duration)
        return 0, ""

    def evaluate_if(self, raw_line):
        raw = raw_line.strip()
        if raw.startswith('$'):
            raw = raw[1:].strip()
        if not raw.upper().startswith("IF "):
            return False, ""
        
        idx = raw.upper().find(" THEN ")
        if idx == -1:
            idx = raw.upper().find(" THEN")
            if idx == -1:
                return False, ""
            then_len = 5
        else:
            then_len = 6
            
        cond_str = raw[3:idx].strip()
        then_stmt = raw[idx+then_len:].strip()
        
        for s_name, s_val in self.symbols.items():
            pattern = r'\b' + re.escape(s_name) + r'\b'
            rep = repr(s_val) if isinstance(s_val, str) and not s_val.isdigit() else str(s_val)
            cond_str = re.sub(pattern, rep, cond_str)
            
        cond_val = False
        try:
            c_py = cond_str.replace('.EQ.', '==').replace('.NE.', '!=').replace('.GT.', '>').replace('.LT.', '<')
            if '==' not in c_py and '!=' not in c_py and '<=' not in c_py and '>=' not in c_py and '=' in c_py:
                c_py = c_py.replace('=', '==')
            cond_val = bool(eval(c_py))
        except Exception:
            cond_val = False
            
        return cond_val, then_stmt

    def cmd_if(self, cmd):
        cond_val, then_stmt = self.evaluate_if(cmd.raw_line)
        if cond_val:
            return self.execute_line(then_stmt)
        return 0, ""

    def cmd_assign(self, cmd):
        if len(cmd.args) >= 2:
            target, name = cmd.args[0], cmd.args[1].upper()
            self.logicals[name] = target
            return 0, ""
        return 1, "%DCL-E-PARAM, missing value or logical name"

    def cmd_deassign(self, cmd):
        if cmd.args:
            name = cmd.args[0].upper()
            self.logicals.pop(name, None)
            return 0, ""
        return 1, "%DCL-E-PARAM, missing logical name"

    def cmd_exit(self, cmd):
        self.exit_requested = True
        return 0, "%DCL-I-LOGOUT, session terminated"
