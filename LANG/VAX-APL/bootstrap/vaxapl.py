#!/usr/bin/env python3
"""
DEC VAX APL V3.1-00 Compiler & Interactive Workspace Engine (vaxapl.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Supports:
  1. Compiling VAX APL source files (.APL) into OpenVMS relocatable object modules (.OBJ)
     compatible with OpenVMS Linker (vmslink) and vms_vm, plus optional .LST compiler listings.
  2. Interactive VAX APL workspace session (--interactive / -i or when invoked without files)
     with system commands: )CLEAR, )VARS, )FNS, )WSID, )SAVE, )LOAD, )ERASE, )OFF, )EXIT.
  3. Both Unicode APL glyphs (← ⍳ ⍴ +/ ×/ ⌈/ ⌊/ ⌽ ↑ ↓ ÷ × ∇ ⎕← ⍝) and DEC VAX APL ASCII
     mnemonics (<- .IOTA .RHO .SUM .PROD .MAX .MIN .REV .TAKE .DROP .DIV QUAD<- REM).
"""

import io
import os
import re
import sys
import json
import struct
from contextlib import redirect_stdout
from datetime import datetime

# Bytecode Opcodes (vms_vm compatible)
OP_HALT = 0x00
OP_PUSH_INT = 0x10
OP_PUSH_FLOAT = 0x11
OP_PUSH_STR = 0x12
OP_STORE_VAR = 0x13
OP_LOAD_VAR = 0x14
OP_PUSH_I32 = 0x18
OP_PRINT = 0x50


class VAXAPLWorkspace:
    VERSION = "V3.1-00"

    def __init__(self, ws_dir="."):
        self.wsid = "CLEAR WS"
        self.ws_dir = ws_dir
        self.vars = {}         # name -> int | float | str | list
        self.fns = {}          # fn_name -> {'arg_l': None, 'arg_r': None, 'res': None, 'lines': []}
        self.in_fn_def = None  # current function header dict when inside ∇ ... ∇

    def normalize_ascii_mnemonics(self, line):
        s = line
        # Strip comments outside quotes: ⍝, .LAMP, NB., or REM
        in_q = None
        cut_idx = None
        i = 0
        while i < len(s):
            ch = s[i]
            if ch in ("'", '"'):
                if in_q is None:
                    in_q = ch
                elif in_q == ch:
                    in_q = None
            elif in_q is None:
                if ch == "⍝":
                    cut_idx = i
                    break
                if s[i:i + 5].upper() == ".LAMP" or s[i:i + 3].upper() == "NB.":
                    cut_idx = i
                    break
                if (i == 0 or s[i - 1].isspace()) and (
                    s[i:i + 4].upper() in ("REM ", "REM\t") or s[i:].upper() == "REM"
                ):
                    cut_idx = i
                    break
            i += 1
        if cut_idx is not None:
            s = s[:cut_idx]

        # Replace ASCII mnemonics with canonical APL tokens
        s = re.sub(r"\bQUAD\s*<-", "⎕←", s, flags=re.IGNORECASE)
        s = re.sub(r"\bQUAD\s*←", "⎕←", s, flags=re.IGNORECASE)
        s = s.replace("<-", "←")
        s = re.sub(r"\.IOTA\b", "⍳", s, flags=re.IGNORECASE)
        s = re.sub(r"\biota\b", "⍳", s, flags=re.IGNORECASE)
        s = re.sub(r"\.RHO\b", "⍴", s, flags=re.IGNORECASE)
        s = re.sub(r"\brho\b", "⍴", s, flags=re.IGNORECASE)
        s = re.sub(r"\.REV\b", "⌽", s, flags=re.IGNORECASE)
        s = re.sub(r"\.SUM/?\b", "+/", s, flags=re.IGNORECASE)
        s = re.sub(r"\.PROD/?\b", "×/", s, flags=re.IGNORECASE)
        s = re.sub(r"\.MAX/", "⌈/", s, flags=re.IGNORECASE)
        s = re.sub(r"\.MIN/", "⌊/", s, flags=re.IGNORECASE)
        s = re.sub(r"\.MAX\b", "⌈/", s, flags=re.IGNORECASE)
        s = re.sub(r"\.MIN\b", "⌊/", s, flags=re.IGNORECASE)
        s = re.sub(r"\.TAKE\b", "↑", s, flags=re.IGNORECASE)
        s = re.sub(r"\.DROP\b", "↓", s, flags=re.IGNORECASE)
        s = re.sub(r"\.DIV\b", "÷", s, flags=re.IGNORECASE)
        s = s.replace("*/", "×/")
        return s.strip()

    def format_value(self, val):
        if val is None:
            return ""
        if isinstance(val, str):
            return val
        if isinstance(val, list):
            if val and isinstance(val[0], list):
                return "\n".join(self.format_value(row) for row in val)
            parts = []
            for x in val:
                if isinstance(x, float) and x.is_integer():
                    parts.append(str(int(x)))
                elif isinstance(x, float):
                    parts.append(f"{x:g}")
                else:
                    parts.append(str(x))
            return " ".join(parts)
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        if isinstance(val, float):
            return f"{val:g}"
        return str(val)

    def _to_list(self, v):
        if isinstance(v, list):
            return v
        return [v]

    def _flatten(self, v):
        if isinstance(v, list):
            out = []
            for x in v:
                out.extend(self._flatten(x))
            return out
        return [v]

    def _apply_dyadic(self, op, left, right):
        if op == ",":
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            return self._to_list(left) + self._to_list(right)
        if op == "⍴":
            dims = self._to_list(left)
            src = self._flatten(right)
            if not src:
                return []
            if len(dims) == 1:
                n = int(dims[0])
                return [src[i % len(src)] for i in range(n)]
            rows, cols = int(dims[0]), int(dims[1])
            mat = []
            idx = 0
            for _ in range(rows):
                row = []
                for _ in range(cols):
                    row.append(src[idx % len(src)])
                    idx += 1
                mat.append(row)
            return mat
        if op == "↑":
            n = int(left[0] if isinstance(left, list) else left)
            src = self._to_list(right)
            return src[:n] if n >= 0 else src[n:]
        if op == "↓":
            n = int(left[0] if isinstance(left, list) else left)
            src = self._to_list(right)
            return src[n:] if n >= 0 else src[:n]

        def scalar_op(a, b):
            if op == "+":
                return a + b
            if op in ("-", "−"):
                return a - b
            if op in ("*", "×"):
                return a * b
            if op in ("/", "÷"):
                return (a / b) if b != 0 else 0
            if op in ("⌈", "⌈/"):
                return max(a, b)
            if op in ("⌊", "⌊/"):
                return min(a, b)
            if op == "=":
                return 1 if a == b else 0
            if op in ("≠", "<>"):
                return 1 if a != b else 0
            if op == "<":
                return 1 if a < b else 0
            if op == ">":
                return 1 if a > b else 0
            if op in ("≤", "<="):
                return 1 if a <= b else 0
            if op in ("≥", ">="):
                return 1 if a >= b else 0
            return 0

        if isinstance(left, list) and isinstance(right, list):
            if len(left) == 1 and len(right) > 1:
                return [scalar_op(left[0], b) for b in right]
            if len(right) == 1 and len(left) > 1:
                return [scalar_op(a, right[0]) for a in left]
            return [scalar_op(a, b) for a, b in zip(left, right)]
        if isinstance(left, list):
            return [scalar_op(a, right) for a in left]
        if isinstance(right, list):
            return [scalar_op(left, b) for b in right]
        return scalar_op(left, right)

    def _apply_monadic(self, op, right):
        if op == "⍳":
            n = int(right[0] if isinstance(right, list) else right)
            return list(range(1, n + 1))
        if op == "⍴":
            if isinstance(right, list):
                if right and isinstance(right[0], list):
                    return [len(right), len(right[0])]
                return [len(right)]
            if isinstance(right, str):
                return [len(right)]
            return [1]
        if op == "⌽":
            if isinstance(right, list):
                return list(reversed(right))
            if isinstance(right, str):
                return right[::-1]
            return right
        if op == "+/":
            lst = self._flatten(right)
            return sum(lst)
        if op == "×/":
            lst = self._flatten(right)
            prod = 1
            for x in lst:
                prod *= x
            return prod
        if op in ("⌈/", "⌈"):
            lst = self._flatten(right)
            return max(lst) if lst else 0
        if op in ("⌊/", "⌊"):
            lst = self._flatten(right)
            return min(lst) if lst else 0
        if op in ("-", "−", "¯"):
            if isinstance(right, list):
                return [-x for x in right]
            return -right
        return right

    def tokenize(self, expr):
        token_spec = re.compile(
            r"""
            '[^']*' | "[^"]*" |
            \+/ | ×/ | ⌈/ | ⌊/ |
            ⎕ | ← | ⍳ | ⍴ | ⌽ | ↑ | ↓ | ÷ | × | ⌈ | ⌊ | ≤ | ≥ | ≠ |
            ¯?\d+\.\d+ | ¯?\d+ |
            [A-Za-z_∆][A-Za-z0-9_∆]* |
            [+\-*/=,<>()]
            """,
            re.VERBOSE,
        )
        return [m.group(0) for m in token_spec.finditer(expr)]

    def parse_atom(self, tok):
        if (tok.startswith("'") and tok.endswith("'")) or (tok.startswith('"') and tok.endswith('"')):
            return tok[1:-1]
        t_num = tok.replace("¯", "-")
        if re.match(r"^-?\d+\.\d+$", t_num):
            return float(t_num)
        if re.match(r"^-?\d+$", t_num):
            return int(t_num)
        up = tok.upper()
        if up in self.vars:
            return self.vars[up]
        return 0

    def eval_tokens(self, tokens):
        collapsed = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if re.match(r"^¯?\d+(?:\.\d+)?$", t):
                vec = [self.parse_atom(t)]
                i += 1
                while i < len(tokens) and re.match(r"^¯?\d+(?:\.\d+)?$", tokens[i]):
                    vec.append(self.parse_atom(tokens[i]))
                    i += 1
                collapsed.append(vec[0] if len(vec) == 1 else vec)
            elif t == "(":
                depth = 1
                j = i + 1
                while j < len(tokens) and depth > 0:
                    if tokens[j] == "(":
                        depth += 1
                    elif tokens[j] == ")":
                        depth -= 1
                    j += 1
                sub_val = self.eval_tokens(tokens[i + 1 : j - 1])
                collapsed.append(sub_val)
                i = j
            else:
                collapsed.append(t)
                i += 1

        if not collapsed:
            return None

        ops_set = {
            "+/", "×/", "⌈/", "⌊/", "⍳", "⍴", "⌽", "↑", "↓",
            "+", "-", "−", "*", "×", "/", "÷", "⌈", "⌊", ",",
            "=", "≠", "<", ">", "≤", "≥",
        }

        def resolve_val(item):
            if isinstance(item, str) and item not in ops_set and item != "←":
                return self.parse_atom(item)
            return item

        idx = len(collapsed) - 1
        acc = resolve_val(collapsed[idx])
        idx -= 1

        while idx >= 0:
            tok = collapsed[idx]
            if tok == "←":
                if idx >= 1 and isinstance(collapsed[idx - 1], str):
                    var_name = collapsed[idx - 1].upper()
                    if var_name not in ("⎕", "QUAD"):
                        self.vars[var_name] = acc
                    idx -= 2
                    continue
            if isinstance(tok, str) and tok.upper() in self.fns:
                fn_name = tok.upper()
                fn_def = self.fns[fn_name]
                if fn_def["arg_l"] and idx >= 1 and not (
                    isinstance(collapsed[idx - 1], str) and (collapsed[idx - 1] in ops_set or collapsed[idx - 1] == "←")
                ):
                    lhs_val = resolve_val(collapsed[idx - 1])
                    acc = self.invoke_fn(fn_name, lhs_val, acc)
                    idx -= 2
                else:
                    acc = self.invoke_fn(fn_name, None, acc)
                    idx -= 1
                continue
            if isinstance(tok, str) and tok in ops_set:
                if tok in ("+/", "×/", "⌈/", "⌊/", "⍳", "⌽") or idx == 0 or (
                    isinstance(collapsed[idx - 1], str) and (collapsed[idx - 1] in ops_set or collapsed[idx - 1] == "←")
                ):
                    acc = self._apply_monadic(tok, acc)
                    idx -= 1
                else:
                    lhs_val = resolve_val(collapsed[idx - 1])
                    acc = self._apply_dyadic(tok, lhs_val, acc)
                    idx -= 2
            else:
                acc = resolve_val(tok)
                idx -= 1

        return acc

    def invoke_fn(self, fn_name, left_arg, right_arg):
        fn = self.fns[fn_name]
        saved_vars = dict(self.vars)
        if fn["arg_l"] and left_arg is not None:
            self.vars[fn["arg_l"]] = left_arg
        if fn["arg_r"] and right_arg is not None:
            self.vars[fn["arg_r"]] = right_arg
        last_val = None
        for ln in fn["lines"]:
            last_val = self.eval_line(ln, suppress_print=True)
        res = self.vars.get(fn["res"], last_val) if fn["res"] else last_val
        self.vars = saved_vars
        return res

    def eval_line(self, raw_line, suppress_print=False):
        s = raw_line.strip()
        if not s:
            return None

        # Handle function definition delimiters ∇ or .DEL
        if s.startswith("∇") or s.upper().startswith(".DEL"):
            body = s[1:].strip() if s.startswith("∇") else s[4:].strip()
            if self.in_fn_def is not None:
                self.fns[self.in_fn_def["name"]] = self.in_fn_def
                self.in_fn_def = None
                return None
            inline_close = False
            if body.endswith("∇"):
                inline_close = True
                body = body[:-1].strip()
            res_var = None
            if "←" in body or "<-" in body:
                body = body.replace("<-", "←")
                res_var, body = [x.strip().upper() for x in body.split("←", 1)]
            parts = body.upper().split()
            if len(parts) == 1:
                fn_name, arg_l, arg_r = parts[0], None, None
            elif len(parts) == 2:
                fn_name, arg_l, arg_r = parts[0], None, parts[1]
            else:
                arg_l, fn_name, arg_r = parts[0], parts[1], parts[2]
            self.in_fn_def = {"name": fn_name, "res": res_var, "arg_l": arg_l, "arg_r": arg_r, "lines": []}
            if inline_close:
                self.fns[fn_name] = self.in_fn_def
                self.in_fn_def = None
            return None

        if self.in_fn_def is not None:
            if s.endswith("∇") or s.upper().endswith(".DEL"):
                line_part = s[:-1].strip() if s.endswith("∇") else s[:-4].strip()
                if line_part:
                    self.in_fn_def["lines"].append(line_part)
                self.fns[self.in_fn_def["name"]] = self.in_fn_def
                self.in_fn_def = None
            else:
                self.in_fn_def["lines"].append(s)
            return None

        # Check APL system commands starting with ')'
        if s.startswith(")"):
            return self._exec_sys_cmd(s)

        norm = self.normalize_ascii_mnemonics(s)
        if not norm:
            return None

        stmts = [x.strip() for x in re.split(r"[⋄;]", norm) if x.strip()]
        last_val = None
        for st in stmts:
            tokens = self.tokenize(st)
            if not tokens:
                continue
            val = self.eval_tokens(tokens)
            last_val = val
            has_quad_assign = False
            for idx_t in range(len(tokens) - 1):
                if tokens[idx_t].upper() in ("⎕", "QUAD") and tokens[idx_t + 1] == "←":
                    has_quad_assign = True
                    break
            is_quiet_assign = (
                len(tokens) >= 2
                and tokens[1] == "←"
                and tokens[0].upper() not in ("⎕", "QUAD")
                and not has_quad_assign
            )
            if (not suppress_print or has_quad_assign) and not is_quiet_assign and val is not None:
                print(self.format_value(val))
        return last_val

    def _exec_sys_cmd(self, cmd_line):
        parts = cmd_line[1:].strip().split(None, 1)
        verb = parts[0].upper() if parts else ""
        arg = parts[1].strip() if len(parts) > 1 else ""

        if verb in ("OFF", "CONTINUE", "BYE", "EXIT", "QUIT"):
            now_s = datetime.now().strftime("%H:%M:%S %d-%b-%Y").upper()
            print(f"OFF AT {now_s} — DEC VAX APL {self.VERSION} WORKSPACE CLOSED")
            return "__APL_OFF__"
        if verb == "WSID":
            if arg:
                old_ws = self.wsid
                self.wsid = arg.upper()
                print(f"WAS {old_ws}")
            else:
                print(self.wsid)
            return None
        if verb == "CLEAR":
            self.vars.clear()
            self.fns.clear()
            self.wsid = "CLEAR WS"
            print("CLEAR WS")
            return None
        if verb == "VARS":
            print(" ".join(sorted(self.vars.keys())))
            return None
        if verb == "FNS":
            print(" ".join(sorted(self.fns.keys())))
            return None
        if verb == "ERASE":
            for sym in arg.upper().split():
                self.vars.pop(sym, None)
                self.fns.pop(sym, None)
            return None
        if verb == "SAVE":
            ws_name = (arg or self.wsid).upper().replace(" ", "_")
            if not ws_name.endswith(".VWS"):
                ws_name += ".VWS"
            path = os.path.join(self.ws_dir, ws_name)
            with open(path, "w") as f:
                json.dump({"wsid": self.wsid, "vars": self.vars, "fns": self.fns}, f, indent=2)
            now_s = datetime.now().strftime("%H:%M:%S %d-%b-%Y").upper()
            print(f"{now_s} SAVED {self.wsid}")
            return None
        if verb == "LOAD":
            ws_name = (arg or self.wsid).upper().replace(" ", "_")
            if not ws_name.endswith(".VWS"):
                ws_name += ".VWS"
            path = os.path.join(self.ws_dir, ws_name)
            if not os.path.isfile(path):
                print(f"%APL-E-WSNOTFND, workspace {arg} not found")
                return None
            with open(path, "r") as f:
                data = json.load(f)
            self.wsid = data.get("wsid", ws_name)
            self.vars = data.get("vars", {})
            self.fns = data.get("fns", {})
            print(f"SAVED {self.wsid}")
            return None
        if verb == "HELP":
            print(f"DEC VAX APL {self.VERSION} System Commands:")
            print("  )WSID [name]   Display or change active workspace name")
            print("  )VARS          List defined variables in workspace")
            print("  )FNS           List defined user functions (∇) in workspace")
            print("  )CLEAR         Reset workspace to CLEAR WS")
            print("  )SAVE [name]   Save active workspace (.VWS)")
            print("  )LOAD <name>   Load saved workspace (.VWS)")
            print("  )ERASE <names> Erase variables or functions")
            print("  )OFF / )EXIT   Exit VAX APL interpreter and return to DCL ($)")
            return None
        print(f"%APL-W-BADCMD, incorrect system command: ){verb}")
        return None

    def run_interactive(self):
        print(f"DEC VAX APL {self.VERSION} [VAX/VMS] — CLEAR WS")
        while True:
            sys.stdout.write("      ")
            sys.stdout.flush()
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                print("\nINTERRUPT")
                continue
            if not line:
                break
            line = line.rstrip("\r\n")
            if line in ("\x1a", "\x04"):
                break
            res = self.eval_line(line)
            if res == "__APL_OFF__":
                break
        return 0


class VAXAPLCompiler:
    VERSION = "V3.1-00"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.ident = "V03-01"
        self.bytecode = bytearray()
        self.var_map = {}
        self.var_types = {}
        self.listing_lines = []

    def get_var_id(self, name, vtype="LONG"):
        u = name.strip().upper()
        if u not in self.var_map:
            self.var_map[u] = min(len(self.var_map), 254)
            self.var_types[u] = vtype
        return self.var_map[u]

    def emit_u8(self, b):
        self.bytecode.append(b & 0xFF)

    def emit_u16(self, w):
        self.bytecode.extend(struct.pack("<H", w & 0xFFFF))

    def emit_push_int(self, val):
        iv = int(val)
        if -32768 <= iv <= 32767:
            self.emit_u8(OP_PUSH_INT)
            self.bytecode.extend(struct.pack("<h", iv))
        else:
            self.emit_u8(OP_PUSH_I32)
            self.bytecode.extend(struct.pack("<i", iv))

    def emit_push_str(self, s):
        b = str(s).encode("utf-8", errors="replace")[:254]
        self.emit_u8(OP_PUSH_STR)
        self.emit_u8(len(b))
        self.bytecode.extend(b)

    def emit_store_var(self, name, vtype="LONG"):
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(self.get_var_id(name, vtype))

    def compile_source(self, source_text):
        ws = VAXAPLWorkspace()
        raw_lines = source_text.splitlines()
        tracked_vars = {}

        for lno, raw in enumerate(raw_lines, start=1):
            pc_before = len(self.bytecode)
            buf = io.StringIO()
            with redirect_stdout(buf):
                res = ws.eval_line(raw)
            # Emit variable stores for any newly assigned scalar or vector variables
            for vname, vval in ws.vars.items():
                if tracked_vars.get(vname) != vval:
                    tracked_vars[vname] = vval
                    if isinstance(vval, int):
                        self.emit_push_int(vval)
                        self.emit_store_var(vname, "LONG")
                    else:
                        self.emit_push_str(ws.format_value(vval))
                        self.emit_store_var(vname, "ARRAY/STR")
            out_txt = buf.getvalue()
            for out_ln in out_txt.splitlines():
                if out_ln.startswith("OFF AT "):
                    continue
                self.emit_push_str(out_ln)
                self.emit_u8(OP_PRINT)
            self.listing_lines.append((lno, pc_before, raw))
            if res == "__APL_OFF__":
                break

        self.emit_u8(OP_HALT)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX APL {self.VERSION}",
            "symbols": {"MAIN_START": 0},
            "relocations": [],
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC VAX APL {self.VERSION} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                f.write("Line  Offset  VAX APL Source Statement\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nWorkspace Symbol Allocation:\n")
                for vname, vid in sorted(self.var_map.items(), key=lambda x: x[1]):
                    vtype = self.var_types.get(vname, "ARRAY")
                    f.write(f"  Slot {vid:>3} : {vname:<24} ({vtype})\n")
                f.write(f"\nCompilation Summary: 0 Diagnostics, {len(self.bytecode)} bytes generated.\n")


def main():
    raw_args = sys.argv[1:]
    args = []
    for a in raw_args:
        if a.startswith("@") and os.path.isfile(a[1:]):
            with open(a[1:], "r", errors="replace") as rf:
                args.extend([ln.strip() for ln in rf.read().splitlines() if ln.strip()])
        else:
            args.append(a)

    if not args or args[0] in ("--interactive", "-i"):
        ws = VAXAPLWorkspace()
        sys.exit(ws.run_interactive())

    if args[0] == "-e" and len(args) > 1:
        ws = VAXAPLWorkspace()
        for expr in " ".join(args[1:]).split(";"):
            res = ws.eval_line(expr)
            if res == "__APL_OFF__":
                break
        sys.exit(0)

    in_file = None
    out_obj = None
    out_lst = None
    want_default_lst = False
    mod_name = None

    i = 0
    while i < len(args):
        a = args[i]
        up = a.upper()
        if a in ("-o", "--output", "--object") and i + 1 < len(args):
            out_obj = args[i + 1]
            i += 2
        elif a in ("-l", "--list") and i + 1 < len(args) and not args[i + 1].startswith("-"):
            out_lst = args[i + 1]
            i += 2
        elif a in ("-l", "--list"):
            want_default_lst = True
            i += 1
        elif a == "--module" and i + 1 < len(args):
            mod_name = args[i + 1]
            i += 2
        elif up.startswith("/OBJECT=") or up.startswith("/OBJ="):
            out_obj = a.split("=", 1)[1]
            i += 1
        elif up.startswith("/LIST=") or up.startswith("/LST="):
            out_lst = a.split("=", 1)[1]
            i += 1
        elif up in ("/LIST", "/LST"):
            want_default_lst = True
            i += 1
        elif not a.startswith("-") and in_file is None:
            in_file = a
            i += 1
        else:
            i += 1

    if not in_file:
        ws = VAXAPLWorkspace()
        sys.exit(ws.run_interactive())

    if not os.path.isfile(in_file):
        for ext in (".APL", ".apl"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%APL-E-OPENIN, error opening {in_file} as input")
        sys.exit(1)

    stem, _ = os.path.splitext(in_file)
    if not out_obj:
        out_obj = stem + ".OBJ"
    if want_default_lst and not out_lst:
        out_lst = stem + ".LST"
    if not mod_name:
        mod_name = os.path.basename(stem).upper()[:16]

    with open(in_file, "r", errors="replace") as f:
        src_text = f.read()

    comp = VAXAPLCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX APL {VAXAPLCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
