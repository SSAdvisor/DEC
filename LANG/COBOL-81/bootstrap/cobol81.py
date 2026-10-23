#!/usr/bin/env python3
"""
DEC PDP-11 COBOL-81 V2.4 Compiler (cobol81.py)
Digital Equipment Corporation PDP-11 / RSTS/E V10.1-L

Compiles ANSI X3.23-1974 / DEC PDP-11 COBOL-81 source files (.CBL, .COB)
into RSTS/E relocatable object modules (.OBJ) compatible with basiclink
and rsts_vm, plus optional compiler listing files (.LST).
"""

import os
import re
import sys
import json
import struct


class Cobol81Compiler:
    VERSION = "V2.4"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name
        self.program_id = "COBPROG"
        self.bytecode = []
        self.relocations = []
        self.line_offsets = {}
        self.variables = {}
        self.var_types = {}       # var_name -> 'STR' | 'INT' | 'FLOAT'
        self.var_pics = {}        # var_name -> pic string
        self.var_init = {}        # var_name -> initial value
        self.file_selects = {}    # select_name -> filename
        self.fd_records = {}      # record_name -> select_name
        self.select_channels = {} # select_name -> int channel
        self.record_fields = {}   # record_name -> list of (field_name, length)
        self.listing_lines = []

    def get_var_index(self, name):
        up = name.upper().strip()
        if up not in self.variables:
            self.variables[up] = len(self.variables)
        return self.variables[up]

    # --- VM Bytecode Emitters ---
    def emit_u8(self, b):
        self.bytecode.append(b & 0xFF)

    def emit_u16(self, w):
        self.bytecode.append(w & 0xFF)
        self.bytecode.append((w >> 8) & 0xFF)

    def emit_push_i(self, val):
        self.emit_u8(0x10)
        self.emit_u16(int(val) & 0xFFFF)

    def emit_push_f(self, val):
        self.emit_u8(0x11)
        self.bytecode.extend(struct.pack("<f", float(val)))

    def emit_push_s(self, s):
        b = str(s).encode("utf-8")[:255]
        self.emit_u8(0x12)
        self.emit_u8(len(b))
        self.bytecode.extend(b)

    def emit_load_v(self, var_name):
        idx = self.get_var_index(var_name)
        self.emit_u8(0x14)
        self.emit_u16(idx)

    def emit_store_v(self, var_name):
        idx = self.get_var_index(var_name)
        self.emit_u8(0x13)
        self.emit_u16(idx)

    def emit_jmp(self, label):
        self.emit_u8(0x30)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": label.upper(),
        })
        self.emit_u16(0)

    def emit_jmp_z(self, label):
        self.emit_u8(0x31)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP_Z",
            "target_line": label.upper(),
        })
        self.emit_u16(0)

    def emit_call(self, label):
        self.emit_u8(0x40)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": label.upper(),
        })
        self.emit_u16(0)

    def push_atom(self, tok):
        s = tok.strip()
        if not s:
            self.emit_push_i(0)
            return
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            self.emit_push_s(s[1:-1])
            return
        up = s.upper()
        if up in ("ZERO", "ZEROS", "ZEROES"):
            self.emit_push_i(0)
            return
        if up in ("SPACE", "SPACES"):
            self.emit_push_s(" ")
            return
        if re.match(r"^[+-]?\d+\.\d+$", s):
            self.emit_push_f(float(s))
            return
        if re.match(r"^[+-]?\d+$", s):
            self.emit_push_i(int(s))
            return
        self.emit_load_v(up)

    def eval_arith_expr(self, expr_str):
        # Tokenize simple arithmetic expression (+, -, *, /) with parentheses
        tokens = re.findall(r'"[^"]*"|\'[^\']*\'|[A-Za-z0-9_-]+|[+\-*/()]', expr_str)
        prec = {"+": 1, "-": 1, "*": 2, "/": 2}
        output = []
        ops = []
        for t in tokens:
            if t == "(":
                ops.append(t)
            elif t == ")":
                while ops and ops[-1] != "(":
                    output.append(("OP", ops.pop()))
                if ops:
                    ops.pop()
            elif t in prec:
                while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                    output.append(("OP", ops.pop()))
                ops.append(t)
            else:
                output.append(("VAL", t))
        while ops:
            output.append(("OP", ops.pop()))

        for kind, val in output:
            if kind == "VAL":
                self.push_atom(val)
            else:
                if val == "+":
                    self.emit_u8(0x20)
                elif val == "-":
                    self.emit_u8(0x21)
                elif val == "*":
                    self.emit_u8(0x22)
                elif val == "/":
                    self.emit_u8(0x23)

    def eval_condition(self, cond_str):
        s = cond_str.strip()
        up = s.upper()
        for op_pat, op_code in [
            (" IS GREATER THAN OR EQUAL TO ", ">="),
            (" GREATER THAN OR EQUAL TO ", ">="),
            (" IS LESS THAN OR EQUAL TO ", "<="),
            (" LESS THAN OR EQUAL TO ", "<="),
            (" IS NOT EQUAL TO ", "<>"),
            (" NOT EQUAL TO ", "<>"),
            (" IS GREATER THAN ", ">"),
            (" GREATER THAN ", ">"),
            (" IS LESS THAN ", "<"),
            (" LESS THAN ", "<"),
            (" IS EQUAL TO ", "="),
            (" EQUAL TO ", "="),
            (" >= ", ">="),
            (" <= ", "<="),
            (" <> ", "<>"),
            (" != ", "<>"),
            (" > ", ">"),
            (" < ", "<"),
            (" = ", "="),
        ]:
            if op_pat in up:
                idx = up.index(op_pat)
                lhs = s[:idx].strip()
                rhs = s[idx + len(op_pat):].strip()
                self.eval_arith_expr(lhs)
                self.eval_arith_expr(rhs)
                if op_code == "=":
                    self.emit_u8(0x24)
                elif op_code == "<>":
                    self.emit_u8(0x25)
                elif op_code == "<":
                    self.emit_u8(0x26)
                elif op_code == ">":
                    self.emit_u8(0x27)
                elif op_code == "<=":
                    self.emit_u8(0x27)  # GT
                    self.emit_push_i(0)
                    self.emit_u8(0x24)  # EQ 0
                elif op_code == ">=":
                    self.emit_u8(0x26)  # LT
                    self.emit_push_i(0)
                    self.emit_u8(0x24)  # EQ 0
                return
        self.push_atom(s)

    def clean_cobol_line(self, raw):
        s = raw.rstrip("\r\n")
        if not s.strip():
            return ""
        # Check ANSI fixed-format sequence numbers in cols 1-6 + indicator in col 7
        if len(s) >= 7 and s[:6].isdigit():
            ind = s[6]
            if ind in ("*", "/"):
                return ""
            return s[7:]
        stripped = s.lstrip()
        if stripped.startswith("*"):
            return ""
        return stripped

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        cleaned_lines = []
        for idx, r in enumerate(raw_lines, start=1):
            c = self.clean_cobol_line(r)
            cleaned_lines.append((idx, c, r))

        # Split into divisions
        div = "IDENTIFICATION"
        proc_lines = []

        for lno, c, raw in cleaned_lines:
            up = c.strip().upper()
            if not up:
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue
            if "IDENTIFICATION DIVISION" in up or "ID DIVISION" in up:
                div = "IDENTIFICATION"
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue
            if "ENVIRONMENT DIVISION" in up:
                div = "ENVIRONMENT"
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue
            if "DATA DIVISION" in up:
                div = "DATA"
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue
            if "PROCEDURE DIVISION" in up:
                div = "PROCEDURE"
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue

            if div == "IDENTIFICATION":
                m = re.match(r"^PROGRAM-ID\.\s*([A-Z0-9_-]+)", up)
                if m:
                    self.program_id = m.group(1).rstrip(".")
                    if self.module_name == "MAIN":
                        self.module_name = self.program_id[:15]
                self.listing_lines.append((lno, len(self.bytecode), raw))
            elif div == "ENVIRONMENT":
                m = re.search(r"SELECT\s+([A-Z0-9_-]+)\s+ASSIGN\s+TO\s+([^\s.]+)", c, re.IGNORECASE)
                if m:
                    sel_name = m.group(1).upper()
                    fname = m.group(2).strip().rstrip(".").strip('"').strip("'")
                    self.file_selects[sel_name] = fname
                    if sel_name not in self.select_channels:
                        self.select_channels[sel_name] = len(self.select_channels) + 1
                self.listing_lines.append((lno, len(self.bytecode), raw))
            elif div == "DATA":
                self._parse_data_line(c)
                self.listing_lines.append((lno, len(self.bytecode), raw))
            elif div == "PROCEDURE":
                proc_lines.append((lno, c, raw))

        # Emit WORKING-STORAGE initializations
        for vname, vtype in self.var_types.items():
            init_v = self.var_init.get(vname)
            if vtype == "STR":
                self.emit_push_s(init_v if init_v is not None else "")
            elif vtype == "FLOAT":
                self.emit_push_f(init_v if init_v is not None else 0.0)
            else:
                self.emit_push_i(init_v if init_v is not None else 0)
            self.emit_store_v(vname)

        # Compile PROCEDURE DIVISION statements
        i = 0
        while i < len(proc_lines):
            lno, c, raw = proc_lines[i]
            pc_before = len(self.bytecode)
            s = c.strip()
            up = s.upper()

            # Check paragraph label: e.g. MAIN-LOGIC. or 100-CALC.
            m_para = re.match(r"^([A-Z0-9][A-Z0-9_-]*)\.\s*(.*)$", s, re.IGNORECASE)
            if m_para and m_para.group(1).upper() not in (
                "EXIT", "STOP", "DISPLAY", "MOVE", "ADD", "SUBTRACT",
                "MULTIPLY", "DIVIDE", "COMPUTE", "PERFORM", "IF", "ELSE",
                "END-IF", "GO", "GOTO", "ACCEPT", "OPEN", "CLOSE", "READ", "WRITE"
            ):
                para_name = m_para.group(1).upper()
                self.line_offsets[para_name] = len(self.bytecode)
                rem = m_para.group(2).strip()
                if rem:
                    self._compile_proc_stmt(rem)
                self.listing_lines.append((lno, pc_before, raw))
                i += 1
                continue

            self._compile_proc_stmt(s)
            self.listing_lines.append((lno, pc_before, raw))
            i += 1

        # Default trailing HALT + RET so paragraphs called via PERFORM return cleanly
        self.emit_u8(0x41)  # OP_RET (for trailing paragraph)
        self.emit_u8(0x00)  # OP_HALT

        # Resolve local jumps
        for rel in self.relocations:
            if rel["type"] in ("JMP", "JMP_Z"):
                tgt = rel["target_line"]
                if tgt in self.line_offsets:
                    off = self.line_offsets[tgt]
                    loc = rel["offset"]
                    self.bytecode[loc] = off & 0xFF
                    self.bytecode[loc + 1] = (off >> 8) & 0xFF

    def _parse_data_line(self, line):
        s = line.strip().rstrip(".")
        if not s:
            return
        up = s.upper()
        if up.startswith(("WORKING-STORAGE", "FILE SECTION", "FD ")):
            return
        m = re.match(r"^(\d+)\s+([A-Z0-9_-]+)(.*)$", s, re.IGNORECASE)
        if not m:
            return
        level = int(m.group(1))
        vname = m.group(2).upper()
        rest = m.group(3).strip()

        pic_m = re.search(r"PIC(?:TURE)?\s+(?:IS\s+)?([^\s.]+)", rest, re.IGNORECASE)
        val_m = re.search(r"VALUE\s+(?:IS\s+)?(.+)$", rest, re.IGNORECASE)

        vtype = "STR"
        if pic_m:
            pic = pic_m.group(1).upper()
            self.var_pics[vname] = pic
            if "X" in pic or "A" in pic:
                vtype = "STR"
            elif "V" in pic or "." in pic:
                vtype = "FLOAT"
            else:
                vtype = "INT"
        else:
            vtype = "STR"

        self.var_types[vname] = vtype
        self.get_var_index(vname)

        if val_m:
            raw_v = val_m.group(1).strip().rstrip(".")
            if (raw_v.startswith('"') and raw_v.endswith('"')) or (raw_v.startswith("'") and raw_v.endswith("'")):
                self.var_init[vname] = raw_v[1:-1]
            elif raw_v.upper() in ("ZERO", "ZEROS", "ZEROES"):
                self.var_init[vname] = 0 if vtype == "INT" else (0.0 if vtype == "FLOAT" else "0")
            elif raw_v.upper() in ("SPACE", "SPACES"):
                self.var_init[vname] = " "
            else:
                try:
                    self.var_init[vname] = float(raw_v) if vtype == "FLOAT" else int(float(raw_v))
                except ValueError:
                    self.var_init[vname] = raw_v

    def _compile_proc_stmt(self, stmt):
        s = stmt.strip().rstrip(".")
        if not s:
            return
        up = s.upper()

        if up in ("STOP RUN", "EXIT PROGRAM", "GOBACK"):
            self.emit_u8(0x00)  # OP_HALT
            return
        if up == "EXIT":
            self.emit_u8(0x41)  # OP_RET
            return
        if up.startswith("DISPLAY "):
            rest = s[8:].strip()
            no_adv = False
            if rest.upper().endswith("WITH NO ADVANCING"):
                no_adv = True
                rest = rest[:-17].strip()
            tokens = re.findall(r'"[^"]*"|\'[^\']*\'|[^\s,]+', rest)
            for idx, tok in enumerate(tokens):
                self.push_atom(tok)
                if idx < len(tokens) - 1 or no_adv:
                    self.emit_u8(0x51)  # OP_PRINT_NO_NL
                else:
                    self.emit_u8(0x50)  # OP_PRINT
            return
        if up.startswith("ACCEPT "):
            vname = s[7:].strip().split()[0].upper()
            idx = self.get_var_index(vname)
            if self.var_types.get(vname, "STR") == "STR":
                self.emit_u8(0x71)  # OP_INPUT_S
            else:
                self.emit_u8(0x70)  # OP_INPUT_I
            self.emit_u16(idx)
            return
        if up.startswith("MOVE "):
            m = re.match(r"^MOVE\s+(.+?)\s+TO\s+(.+)$", s, re.IGNORECASE)
            if m:
                src_expr = m.group(1).strip()
                targets = [t.strip().upper() for t in re.split(r"[\s,]+", m.group(2).strip()) if t.strip()]
                for tgt in targets:
                    self.push_atom(src_expr)
                    self.emit_store_v(tgt)
            return
        if up.startswith("COMPUTE "):
            m = re.match(r"^COMPUTE\s+([A-Z0-9_-]+)\s*=\s*(.+)$", s, re.IGNORECASE)
            if m:
                tgt = m.group(1).upper()
                expr = m.group(2).strip()
                self.eval_arith_expr(expr)
                if self.var_types.get(tgt) == "INT":
                    self.emit_u8(0x75)  # OP_INT
                self.emit_store_v(tgt)
            return
        if up.startswith("ADD "):
            m_giv = re.match(r"^ADD\s+(.+?)\s+TO\s+(.+?)\s+GIVING\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_giv:
                a, b, dst = m_giv.group(1), m_giv.group(2), m_giv.group(3).upper()
                self.push_atom(a)
                self.push_atom(b)
                self.emit_u8(0x20)
                self.emit_store_v(dst)
                return
            m_to = re.match(r"^ADD\s+(.+?)\s+TO\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_to:
                a, dst = m_to.group(1), m_to.group(2).upper()
                self.emit_load_v(dst)
                self.push_atom(a)
                self.emit_u8(0x20)
                self.emit_store_v(dst)
                return
        if up.startswith("SUBTRACT "):
            m_giv = re.match(r"^SUBTRACT\s+(.+?)\s+FROM\s+(.+?)\s+GIVING\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_giv:
                a, b, dst = m_giv.group(1), m_giv.group(2), m_giv.group(3).upper()
                self.push_atom(b)
                self.push_atom(a)
                self.emit_u8(0x21)
                self.emit_store_v(dst)
                return
            m_fr = re.match(r"^SUBTRACT\s+(.+?)\s+FROM\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_fr:
                a, dst = m_fr.group(1), m_fr.group(2).upper()
                self.emit_load_v(dst)
                self.push_atom(a)
                self.emit_u8(0x21)
                self.emit_store_v(dst)
                return
        if up.startswith("MULTIPLY "):
            m_giv = re.match(r"^MULTIPLY\s+(.+?)\s+BY\s+(.+?)\s+GIVING\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_giv:
                a, b, dst = m_giv.group(1), m_giv.group(2), m_giv.group(3).upper()
                self.push_atom(a)
                self.push_atom(b)
                self.emit_u8(0x22)
                self.emit_store_v(dst)
                return
            m_by = re.match(r"^MULTIPLY\s+(.+?)\s+BY\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_by:
                a, dst = m_by.group(1), m_by.group(2).upper()
                self.emit_load_v(dst)
                self.push_atom(a)
                self.emit_u8(0x22)
                self.emit_store_v(dst)
                return
        if up.startswith("DIVIDE "):
            m_into_giv = re.match(r"^DIVIDE\s+(.+?)\s+INTO\s+(.+?)\s+GIVING\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_into_giv:
                a, b, dst = m_into_giv.group(1), m_into_giv.group(2), m_into_giv.group(3).upper()
                self.push_atom(b)
                self.push_atom(a)
                self.emit_u8(0x23)
                if self.var_types.get(dst) == "INT":
                    self.emit_u8(0x75)
                self.emit_store_v(dst)
                return
            m_by_giv = re.match(r"^DIVIDE\s+(.+?)\s+BY\s+(.+?)\s+GIVING\s+([A-Z0-9_-]+)$", s, re.IGNORECASE)
            if m_by_giv:
                a, b, dst = m_by_giv.group(1), m_by_giv.group(2), m_by_giv.group(3).upper()
                self.push_atom(a)
                self.push_atom(b)
                self.emit_u8(0x23)
                if self.var_types.get(dst) == "INT":
                    self.emit_u8(0x75)
                self.emit_store_v(dst)
                return
        if up.startswith("PERFORM "):
            m_var = re.match(
                r"^PERFORM\s+([A-Z0-9_-]+)\s+VARYING\s+([A-Z0-9_-]+)\s+FROM\s+([^\s]+)\s+BY\s+([^\s]+)\s+UNTIL\s+(.+)$",
                s,
                re.IGNORECASE,
            )
            if m_var:
                para = m_var.group(1).upper()
                var = m_var.group(2).upper()
                from_v = m_var.group(3)
                by_v = m_var.group(4)
                cond = m_var.group(5)
                self.push_atom(from_v)
                self.emit_store_v(var)
                loop_lbl = f"__PERF_LP_{len(self.bytecode)}"
                exit_lbl = f"__PERF_EX_{len(self.bytecode)}"
                self.line_offsets[loop_lbl] = len(self.bytecode)
                self.eval_condition(cond)
                self.emit_push_i(0)
                self.emit_u8(0x24)  # EQ 0 (continue when cond is false)
                self.emit_jmp_z(exit_lbl)
                self.emit_call(para)
                self.emit_load_v(var)
                self.push_atom(by_v)
                self.emit_u8(0x20)
                self.emit_store_v(var)
                self.emit_jmp(loop_lbl)
                self.line_offsets[exit_lbl] = len(self.bytecode)
                return
            m_times = re.match(r"^PERFORM\s+([A-Z0-9_-]+)\s+(\d+)\s+TIMES$", s, re.IGNORECASE)
            if m_times:
                para = m_times.group(1).upper()
                cnt = int(m_times.group(2))
                for _ in range(cnt):
                    self.emit_call(para)
                return
            para = s[8:].strip().split()[0].upper()
            self.emit_call(para)
            return
        if up.startswith("GO TO ") or up.startswith("GOTO "):
            tgt = up.replace("GO TO ", "").replace("GOTO ", "").strip().split()[0]
            self.emit_jmp(tgt)
            return
        if up.startswith("IF "):
            # Single-line IF <cond> THEN <stmt> [ELSE <stmt2>]
            rest = s[3:].strip()
            if " THEN " in rest.upper():
                idx = rest.upper().index(" THEN ")
                cond = rest[:idx].strip()
                after_then = rest[idx + 6:].strip()
            else:
                # Split after comparison
                m_c = re.match(
                    r"^(.+?\s+(?:>=|<=|<>|=|>|<|EQUAL\s+TO\s+[^\s]+|GREATER\s+THAN\s+[^\s]+|LESS\s+THAN\s+[^\s]+))\s+(.+)$",
                    rest,
                    re.IGNORECASE,
                )
                if not m_c:
                    return
                cond = m_c.group(1).strip()
                after_then = m_c.group(2).strip()

            else_stmt = None
            if " ELSE " in after_then.upper():
                e_idx = after_then.upper().index(" ELSE ")
                then_stmt = after_then[:e_idx].strip()
                else_stmt = after_then[e_idx + 6:].strip()
            else:
                then_stmt = after_then

            else_lbl = f"__IF_ELSE_{len(self.bytecode)}"
            end_lbl = f"__IF_END_{len(self.bytecode)}"
            self.eval_condition(cond)
            self.emit_jmp_z(else_lbl)
            self._compile_proc_stmt(then_stmt)
            if else_stmt:
                self.emit_jmp(end_lbl)
            self.line_offsets[else_lbl] = len(self.bytecode)
            if else_stmt:
                self._compile_proc_stmt(else_stmt)
                self.line_offsets[end_lbl] = len(self.bytecode)
            return

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "version": 1,
            "module": "MAIN",
            "program_id": self.program_id,
            "compiler": f"DEC PDP-11 COBOL-81 {self.VERSION}",
            "symbols": [
                {"name": "MAIN_START", "type": "EXPORT", "offset": 0}
            ],
            "relocations": self.relocations,
            "strings": [],
            "bytecode": self.bytecode,
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            with open(out_lst, "w") as f:
                f.write(f"DEC PDP-11 COBOL-81 {self.VERSION} (RSTS/E V10.1-L)   PROGRAM-ID: {self.program_id}\n")
                f.write("Line  Offset  Source Statement\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06o}  {raw}\n")
                f.write("\nData Division Map:\n")
                for vname, vtype in sorted(self.var_types.items()):
                    pic = self.var_pics.get(vname, "X")
                    f.write(f"  {vname:<24} PIC {pic:<12} ({vtype})\n")


def main():
    raw_args = sys.argv[1:]
    args = []
    for a in raw_args:
        if a.startswith("@") and os.path.isfile(a[1:]):
            with open(a[1:], "r", errors="replace") as rf:
                args.extend([ln.strip() for ln in rf.read().splitlines() if ln.strip()])
        else:
            args.append(a)
    if not args:
        print("Usage: cobol <input.cbl> [-o output.obj] [-l listing.lst] [--module NAME]")
        sys.exit(1)

    in_file = None
    out_obj = None
    out_lst = None
    mod_name = "MAIN"

    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-o", "--output") and i + 1 < len(args):
            out_obj = args[i + 1]
            i += 2
        elif a in ("-l", "--list") and i + 1 < len(args):
            out_lst = args[i + 1]
            i += 2
        elif a == "--module" and i + 1 < len(args):
            mod_name = args[i + 1]
            i += 2
        elif not a.startswith("-") and in_file is None:
            in_file = a
            i += 1
        else:
            i += 1

    if not in_file:
        print("?COBOL-F-NOFILE, no input .CBL/.COB file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".CBL", ".cbl", ".COB", ".cob"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"?COBOL-F-FNF, cannot find COBOL source file {in_file}")
        sys.exit(1)

    if not out_obj:
        stem, _ = os.path.splitext(in_file)
        out_obj = stem + ".OBJ"

    with open(in_file, "r", errors="replace") as f:
        src_text = f.read()

    comp = Cobol81Compiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"COBOL-81 {Cobol81Compiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
