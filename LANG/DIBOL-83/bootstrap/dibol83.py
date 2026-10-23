#!/usr/bin/env python3
"""
DEC DIBOL-83 V5.3 Compiler (dibol83.py)
Digital Equipment Corporation PDP-11 / RSTS/E V10.1-L (CTS-300 / CTS-500)
Digital Business Oriented Language (ANSI X3.165-1988 / DIBOL-83)

Compiles DIBOL-83 source files (.DBL, .DIB) into RSTS/E relocatable object
modules (.OBJ) compatible with basiclink and rsts_vm, plus optional compiler
listing files (.LST).
"""

import os
import re
import sys
import json
import struct


class Dibol83Compiler:
    VERSION = "V5.3"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name
        self.title = "DIBOL83"
        self.bytecode = []
        self.relocations = []
        self.line_offsets = {}
        self.variables = {}
        self.var_types = {}       # var_name -> 'STR' (A) | 'INT' (D) | 'FLOAT' (D.p)
        self.var_init = {}        # var_name -> initial literal
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
            "target_line": str(label).upper(),
        })
        self.emit_u16(0)

    def emit_jmp_z(self, label):
        self.emit_u8(0x31)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP_Z",
            "target_line": str(label).upper(),
        })
        self.emit_u16(0)

    def emit_call(self, label):
        self.emit_u8(0x40)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": str(label).upper(),
        })
        self.emit_u16(0)

    def strip_comment(self, line):
        in_q = None
        for i, ch in enumerate(line):
            if in_q:
                if ch == in_q:
                    in_q = None
            else:
                if ch in ("'", '"'):
                    in_q = ch
                elif ch == ";":
                    return line[:i]
        return line

    def eval_expr(self, expr_str):
        s = expr_str.strip()
        if not s:
            self.emit_push_i(0)
            return

        # Normalize DIBOL relational operators (.EQ., .NE., .LT., .LE., .GT., .GE.)
        s_norm = re.sub(r"\.EQ\.", " == ", s, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.NE\.", " != ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.LE\.", " <= ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.GE\.", " >= ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.LT\.", " < ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.GT\.", " > ", s_norm, flags=re.IGNORECASE)

        for rel_op in ("==", "!=", "<=", ">=", "<", ">"):
            if f" {rel_op} " in s_norm:
                lhs, rhs = s_norm.split(f" {rel_op} ", 1)
                self.eval_expr(lhs)
                self.eval_expr(rhs)
                if rel_op == "==":
                    self.emit_u8(0x24)
                elif rel_op == "!=":
                    self.emit_u8(0x25)
                elif rel_op == "<":
                    self.emit_u8(0x26)
                elif rel_op == ">":
                    self.emit_u8(0x27)
                elif rel_op == "<=":
                    self.emit_u8(0x27)
                    self.emit_push_i(0)
                    self.emit_u8(0x24)
                elif rel_op == ">=":
                    self.emit_u8(0x26)
                    self.emit_push_i(0)
                    self.emit_u8(0x24)
                return

        if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
            self.emit_push_s(s[1:-1])
            return

        tokens = re.findall(r"'[^']*'|\"[^\"]*\"|[A-Za-z_$][A-Za-z0-9_$]*|\d+\.\d*|\d+|[+\-*/()#]", s)
        prec = {"+": 1, "-": 1, "*": 2, "/": 2, "#": 2}
        output = []
        ops = []
        for idx_t, t in enumerate(tokens):
            if t == "(":
                ops.append(t)
            elif t == ")":
                while ops and ops[-1] != "(":
                    output.append(("OP", ops.pop()))
                if ops:
                    ops.pop()
            elif t in prec:
                if t == "-" and (idx_t == 0 or tokens[idx_t - 1] in ("(", "+", "-", "*", "/")):
                    output.append(("VAL", "0"))
                while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                    output.append(("OP", ops.pop()))
                ops.append(t)
            else:
                output.append(("VAL", t))
        while ops:
            output.append(("OP", ops.pop()))

        for kind, val in output:
            if kind == "VAL":
                if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
                    self.emit_push_s(val[1:-1])
                elif re.match(r"^\d+\.\d*$", val):
                    self.emit_push_f(float(val))
                elif re.match(r"^\d+$", val):
                    self.emit_push_i(int(val))
                else:
                    self.emit_load_v(val.upper())
            else:
                if val == "+":
                    self.emit_u8(0x20)
                elif val == "-":
                    self.emit_u8(0x21)
                elif val == "*":
                    self.emit_u8(0x22)
                elif val == "/":
                    self.emit_u8(0x23)
                elif val == "#":
                    # DIBOL rounded division operator #
                    self.emit_u8(0x23)
                    self.emit_u8(0x75)

    def _split_top_level_commas(self, s):
        items = []
        cur = []
        in_q = None
        depth = 0
        for ch in s:
            if in_q:
                cur.append(ch)
                if ch == in_q:
                    in_q = None
            else:
                if ch in ("'", '"'):
                    in_q = ch
                    cur.append(ch)
                elif ch == "(":
                    depth += 1
                    cur.append(ch)
                elif ch == ")":
                    depth = max(0, depth - 1)
                    cur.append(ch)
                elif ch == "," and depth == 0:
                    items.append("".join(cur).strip())
                    cur = []
                else:
                    cur.append(ch)
        if cur:
            items.append("".join(cur).strip())
        return [x for x in items if x]

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        in_record = True
        proc_lines = []

        for lno, raw in enumerate(raw_lines, start=1):
            clean = self.strip_comment(raw).strip()
            if not clean:
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue
            up = clean.upper()
            if up.startswith(".TITLE"):
                parts = clean.split(None, 1)
                if len(parts) > 1:
                    self.title = parts[1].strip().strip("'").strip('"')[:15]
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue
            if up == "RECORD" or up.startswith("RECORD "):
                in_record = True
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue
            if up == "PROC" or up.startswith("PROC "):
                in_record = False
                self.listing_lines.append((lno, len(self.bytecode), raw))
                continue

            if in_record:
                self._parse_record_field(clean)
                self.listing_lines.append((lno, len(self.bytecode), raw))
            else:
                proc_lines.append((lno, clean, raw))

        # Emit RECORD field initializations
        for vname, vtype in self.var_types.items():
            init_v = self.var_init.get(vname)
            if vtype == "STR":
                self.emit_push_s(init_v if init_v is not None else "")
            elif vtype == "FLOAT":
                self.emit_push_f(init_v if init_v is not None else 0.0)
            else:
                self.emit_push_i(init_v if init_v is not None else 0)
            self.emit_store_v(vname)

        # Compile PROC section
        for lno, clean, raw in proc_lines:
            pc_before = len(self.bytecode)
            stmt = clean
            # Check for label: LABEL, statement  or  LABEL: statement
            m_lbl = re.match(r"^([A-Za-z_$][A-Za-z0-9_$]*)\s*[,:]\s*(.*)$", stmt)
            if m_lbl and m_lbl.group(1).upper() not in (
                "XCALL", "OPEN", "CLOSE", "DISPLAY", "ACCEPT", "READ", "WRITE",
                "STORE", "INCR", "DECR", "CLEAR", "IF", "ELSE", "GOTO", "CALL",
                "RETURN", "STOP", "END", "FOR", "BEGIN"
            ):
                lbl_name = m_lbl.group(1).upper()
                self.line_offsets[lbl_name] = len(self.bytecode)
                stmt = m_lbl.group(2).strip()
            if stmt:
                self._compile_proc_stmt(stmt)
            self.listing_lines.append((lno, pc_before, raw))

        self.emit_u8(0x00)  # OP_HALT

        # Resolve local relocations
        for rel in self.relocations:
            if rel["type"] in ("JMP", "JMP_Z"):
                tgt = str(rel["target_line"]).upper()
                if tgt in self.line_offsets:
                    off = self.line_offsets[tgt]
                    loc = rel["offset"]
                    self.bytecode[loc] = off & 0xFF
                    self.bytecode[loc + 1] = (off >> 8) & 0xFF

    def _parse_record_field(self, clean):
        # Format: FIELD_NAME, A20 [, 'INIT']  or  AMOUNT, D8.2, 125.50  or  COUNT, D4, 10
        parts = self._split_top_level_commas(clean)
        if len(parts) < 2:
            return
        vname = parts[0].strip().upper()
        spec = parts[1].strip().upper()
        init_raw = parts[2].strip() if len(parts) >= 3 else None

        if spec.startswith("A"):
            vtype = "STR"
        elif "." in spec:
            vtype = "FLOAT"
        else:
            vtype = "INT"

        self.var_types[vname] = vtype
        self.get_var_index(vname)

        if init_raw is not None:
            if (init_raw.startswith("'") and init_raw.endswith("'")) or (init_raw.startswith('"') and init_raw.endswith('"')):
                self.var_init[vname] = init_raw[1:-1]
            elif vtype == "FLOAT":
                try:
                    self.var_init[vname] = float(init_raw)
                except ValueError:
                    self.var_init[vname] = 0.0
            elif vtype == "INT":
                try:
                    self.var_init[vname] = int(float(init_raw))
                except ValueError:
                    self.var_init[vname] = 0
            else:
                self.var_init[vname] = init_raw

    def _compile_proc_stmt(self, stmt):
        s = stmt.strip()
        up = s.upper()

        if up in ("STOP", "END", "FINI") or up.startswith("STOP "):
            self.emit_u8(0x00)  # OP_HALT
            return
        if up in ("BEGIN", "END"):
            return
        if up == "RETURN":
            self.emit_u8(0x41)  # OP_RET
            return
        if up.startswith("XCALL "):
            # e.g. XCALL FLAGS(7000000, 1) or XCALL OUTPT(...)
            m_out = re.match(r"^XCALL\s+OUTPT\s*\((.+)\)$", s, re.IGNORECASE)
            if m_out:
                args = self._split_top_level_commas(m_out.group(1))
                if len(args) >= 3:
                    self.eval_expr(args[2])
                    self.emit_u8(0x50)
            return
        if up.startswith("OPEN") or up.startswith("CLOSE"):
            # Terminal channel open/close in DIBOL (e.g. OPEN(1, O, 'TT:')) is handled natively by stdout/stdin
            return
        if up.startswith("DISPLAY") or up.startswith("FORMS"):
            # DISPLAY(ch, item1, item2, ...)
            m = re.match(r"^(?:DISPLAY|FORMS)\s*\((.+)\)$", s, re.IGNORECASE)
            if m:
                args = self._split_top_level_commas(m.group(1))
                # First arg is channel number (e.g. 1 or TTCH); print remaining items
                items = args[1:] if len(args) > 1 else args
                for idx, it in enumerate(items):
                    self.eval_expr(it)
                    if idx < len(items) - 1:
                        self.emit_u8(0x51)  # OP_PRINT_NO_NL
                    else:
                        self.emit_u8(0x50)  # OP_PRINT
            return
        if up.startswith("ACCEPT") or up.startswith("READ"):
            m = re.match(r"^(?:ACCEPT|READ)\s*\((.+)\)$", s, re.IGNORECASE)
            if m:
                args = self._split_top_level_commas(m.group(1))
                if len(args) >= 2:
                    vname = args[1].strip().upper()
                    idx = self.get_var_index(vname)
                    if self.var_types.get(vname, "STR") == "STR":
                        self.emit_u8(0x71)
                    else:
                        self.emit_u8(0x70)
                    self.emit_u16(idx)
            return
        if up.startswith("INCR "):
            vname = s[5:].strip().upper()
            self.emit_load_v(vname)
            self.emit_push_i(1)
            self.emit_u8(0x20)
            self.emit_store_v(vname)
            return
        if up.startswith("DECR "):
            vname = s[5:].strip().upper()
            self.emit_load_v(vname)
            self.emit_push_i(1)
            self.emit_u8(0x21)
            self.emit_store_v(vname)
            return
        if up.startswith("CLEAR "):
            for v in self._split_top_level_commas(s[6:]):
                vname = v.upper()
                if self.var_types.get(vname) == "STR":
                    self.emit_push_s("")
                else:
                    self.emit_push_i(0)
                self.emit_store_v(vname)
            return
        if up.startswith("CALL "):
            lbl = s[5:].strip().upper()
            self.emit_call(lbl)
            return
        if up.startswith("GOTO ") or up.startswith("GO TO "):
            lbl = re.sub(r"^GO\s*TO\s+", "", s, flags=re.IGNORECASE).strip().upper()
            self.emit_jmp(lbl)
            return
        if up.startswith("FOR "):
            # FOR var FROM start THRU end [BY step] DO stmt
            m = re.match(
                r"^FOR\s+([A-Za-z_$][A-Za-z0-9_$]*)\s+FROM\s+(.+?)\s+THRU\s+(.+?)(?:\s+BY\s+(.+?))?\s+DO\s+(.+)$",
                s,
                re.IGNORECASE,
            )
            if m:
                var = m.group(1).upper()
                from_e = m.group(2).strip()
                thru_e = m.group(3).strip()
                step_e = (m.group(4) or "1").strip()
                body_s = m.group(5).strip()

                self.eval_expr(from_e)
                self.emit_store_v(var)
                loop_lbl = f"__DBL_FOR_LP_{len(self.bytecode)}"
                exit_lbl = f"__DBL_FOR_EX_{len(self.bytecode)}"
                self.line_offsets[loop_lbl] = len(self.bytecode)
                self.emit_load_v(var)
                self.eval_expr(thru_e)
                self.emit_u8(0x27)  # GT
                self.emit_push_i(0)
                self.emit_u8(0x24)  # EQ 0
                self.emit_jmp_z(exit_lbl)
                self._compile_proc_stmt(body_s)
                self.emit_load_v(var)
                self.eval_expr(step_e)
                self.emit_u8(0x20)
                self.emit_store_v(var)
                self.emit_jmp(loop_lbl)
                self.line_offsets[exit_lbl] = len(self.bytecode)
            return
        if up.startswith("IF "):
            # IF (cond) stmt [ELSE stmt2]
            m = re.match(r"^IF\s*\((.+?)\)\s*(.+)$", s, re.IGNORECASE)
            if m:
                cond = m.group(1).strip()
                rest = m.group(2).strip()
                else_stmt = None
                if " ELSE " in rest.upper():
                    e_idx = rest.upper().index(" ELSE ")
                    then_stmt = rest[:e_idx].strip()
                    else_stmt = rest[e_idx + 6:].strip()
                else:
                    then_stmt = rest
                else_lbl = f"__DBL_ELSE_{len(self.bytecode)}"
                end_lbl = f"__DBL_END_{len(self.bytecode)}"
                self.eval_expr(cond)
                self.emit_jmp_z(else_lbl)
                self._compile_proc_stmt(then_stmt)
                if else_stmt:
                    self.emit_jmp(end_lbl)
                self.line_offsets[else_lbl] = len(self.bytecode)
                if else_stmt:
                    self._compile_proc_stmt(else_stmt)
                    self.line_offsets[end_lbl] = len(self.bytecode)
            return

        # Assignment: VAR = EXPR
        if "=" in s:
            lhs, rhs = s.split("=", 1)
            vname = lhs.strip().upper()
            self.eval_expr(rhs.strip())
            if self.var_types.get(vname) == "INT":
                self.emit_u8(0x75)  # OP_INT
            self.emit_store_v(vname)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "version": 1,
            "module": "MAIN",
            "title": self.title,
            "compiler": f"DEC DIBOL-83 {self.VERSION}",
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
                f.write(f"DEC PDP-11 DIBOL-83 {self.VERSION} (CTS-500 / RSTS/E V10.1-L)   TITLE: {self.title}\n")
                f.write("Line  Offset  Source Statement\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06o}  {raw}\n")


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
        print("Usage: dibol <input.dbl> [-o output.obj] [-l listing.lst] [--module NAME]")
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
        print("?DIBOL-F-NOFILE, no input .DBL/.DIB file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".DBL", ".dbl", ".DIB", ".dib"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"?DIBOL-F-FNF, cannot find DIBOL source file {in_file}")
        sys.exit(1)

    if not out_obj:
        stem, _ = os.path.splitext(in_file)
        out_obj = stem + ".OBJ"

    with open(in_file, "r", errors="replace") as f:
        src_text = f.read()

    comp = Dibol83Compiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"DIBOL-83 {Dibol83Compiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
