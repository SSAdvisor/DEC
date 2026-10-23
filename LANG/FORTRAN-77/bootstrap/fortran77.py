#!/usr/bin/env python3
"""
DEC PDP-11 FORTRAN-77 V5.0 Compiler (fortran77.py)
Digital Equipment Corporation PDP-11 / RSTS/E V10.1-L (FORTRAN-77 / FORTRAN IV-PLUS)

Compiles ANSI X3.9-1978 / DEC PDP-11 FORTRAN-77 source files (.FOR, .FTN, .F77)
into RSTS/E relocatable object modules (.OBJ) compatible with basiclink and
rsts_vm, plus optional compiler listing files (.LST).
"""

import os
import re
import sys
import json
import struct


class Fortran77Compiler:
    VERSION = "V5.0"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name
        self.program_name = "MAIN"
        self.bytecode = []
        self.relocations = []
        self.line_offsets = {}
        self.variables = {}
        self.var_types = {}       # var_name -> 'INT' | 'FLOAT' | 'STR' | 'ARR'
        self.arrays = {}          # var_name -> size
        self.data_inits = []      # (var_name, val)
        self.do_stack = []        # list of dicts for active DO loops
        self.if_stack = []        # list of dicts for block IF..THEN..ELSE..ENDIF
        self.formats = {}         # stmt_label -> format string
        self.listing_lines = []

    def get_var_index(self, name):
        up = name.upper().strip()
        if up not in self.variables:
            self.variables[up] = len(self.variables)
        return self.variables[up]

    def get_var_type(self, name):
        up = name.upper().strip()
        if up in self.var_types:
            return self.var_types[up]
        # Implicit FORTRAN typing: I-N are INTEGER, A-H and O-Z are REAL
        if up and up[0] in "IJKLMN":
            return "INT"
        return "FLOAT"

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

    def emit_dim(self, var_name, size):
        self.emit_push_i(size)
        idx = self.get_var_index(var_name)
        self.emit_u8(0x15)
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

    def eval_expr(self, expr_str):
        s = expr_str.strip()
        if not s:
            self.emit_push_i(0)
            return

        # Replace FORTRAN relational operators with canonical tokens
        s_norm = re.sub(r"\.EQ\.", " == ", s, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.NE\.", " != ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.LE\.", " <= ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.GE\.", " >= ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.LT\.", " < ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.GT\.", " > ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.AND\.", " & ", s_norm, flags=re.IGNORECASE)
        s_norm = re.sub(r"\.OR\.", " | ", s_norm, flags=re.IGNORECASE)

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

        # Check intrinsic functions or array access NAME(ARG)
        m_fn = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((.+)\)$", s)
        if m_fn:
            fname = m_fn.group(1).upper()
            arg_s = m_fn.group(2).strip()
            if fname in ("INT", "IFIX"):
                self.eval_expr(arg_s)
                self.emit_u8(0x75)  # OP_INT
                return
            if fname == "MOD":
                a_p, b_p = [x.strip() for x in arg_s.split(",", 1)]
                # a - INT(a / b) * b
                self.eval_expr(a_p)
                self.eval_expr(a_p)
                self.eval_expr(b_p)
                self.emit_u8(0x23)
                self.emit_u8(0x75)
                self.eval_expr(b_p)
                self.emit_u8(0x22)
                self.emit_u8(0x21)
                return
            if fname in self.arrays:
                self.eval_expr(arg_s)
                idx = self.get_var_index(fname)
                self.emit_u8(0x17)  # OP_LOAD_A
                self.emit_u16(idx)
                return

        # Tokenize arithmetic expression
        tokens = re.findall(r"'[^']*'|\"[^\"]*\"|[A-Za-z_][A-Za-z0-9_]*\([^)]*\)|[A-Za-z_][A-Za-z0-9_]*|\d+\.\d*|\d+|[+\-*/()]", s)
        prec = {"+": 1, "-": 1, "*": 2, "/": 2}
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
                # Handle unary minus
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
                elif "(" in val and val.endswith(")"):
                    self.eval_expr(val)
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

    def parse_fortran_line(self, raw):
        s = raw.rstrip("\r\n")
        if not s.strip():
            return None, ""
        if s[0] in ("C", "c", "*", "!"):
            return None, ""
        # Check if standard fixed-form columns 1-5 label + col 7 statement, or free-form
        m_lbl = re.match(r"^\s*(\d+)\s+(.*)$", s)
        if m_lbl:
            return m_lbl.group(1), m_lbl.group(2).strip()
        return None, s.strip()

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        parsed = []
        for idx, r in enumerate(raw_lines, start=1):
            lbl, stmt = self.parse_fortran_line(r)
            parsed.append((idx, lbl, stmt, r))

        # Pass 1: Collect PROGRAM, INTEGER, REAL, CHARACTER, DIMENSION, DATA, FORMAT
        for lno, lbl, stmt, raw in parsed:
            if not stmt:
                continue
            up = stmt.upper()
            if up.startswith("PROGRAM "):
                self.program_name = stmt[8:].strip().split()[0].upper()
                if self.module_name == "MAIN":
                    self.module_name = self.program_name[:15]
            elif up.startswith("FORMAT"):
                if lbl:
                    self.formats[lbl] = stmt[6:].strip()
            elif up.startswith(("INTEGER", "REAL", "CHARACTER", "DIMENSION")):
                self._parse_declaration(stmt)
            elif up.startswith("DATA "):
                self._parse_data_stmt(stmt)

        # Emit array dimensions and DATA initializations
        for arr_name, sz in self.arrays.items():
            self.emit_dim(arr_name, sz)
        for vname, val in self.data_inits:
            if isinstance(val, str):
                self.emit_push_s(val)
            elif isinstance(val, float):
                self.emit_push_f(val)
            else:
                self.emit_push_i(val)
            self.emit_store_v(vname)

        # Pass 2: Compile executable statements
        for lno, lbl, stmt, raw in parsed:
            pc_before = len(self.bytecode)
            if lbl:
                self.line_offsets[str(lbl)] = len(self.bytecode)
            if stmt:
                self._compile_stmt(stmt)
            if lbl:
                # Check if any active DO loops terminate at this label
                while self.do_stack and self.do_stack[-1]["end_label"] == str(lbl):
                    do_info = self.do_stack.pop()
                    self._close_do_loop(do_info)
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

    def _parse_declaration(self, stmt):
        up = stmt.upper()
        base_type = "INT"
        rest = stmt
        if up.startswith("INTEGER"):
            base_type = "INT"
            rest = re.sub(r"^INTEGER(?:\*\d+)?\s*", "", stmt, flags=re.IGNORECASE)
        elif up.startswith("REAL"):
            base_type = "FLOAT"
            rest = re.sub(r"^REAL(?:\*\d+)?\s*", "", stmt, flags=re.IGNORECASE)
        elif up.startswith("CHARACTER"):
            base_type = "STR"
            rest = re.sub(r"^CHARACTER(?:\*\d+)?\s*", "", stmt, flags=re.IGNORECASE)
        elif up.startswith("DIMENSION"):
            rest = stmt[9:].strip()

        items = re.findall(r"[A-Za-z_][A-Za-z0-9_]*(?:\(\d+\))?", rest)
        for it in items:
            if "(" in it:
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((\d+)\)$", it)
                if m:
                    aname, asz = m.group(1).upper(), int(m.group(2))
                    self.arrays[aname] = asz
                    self.var_types[aname] = base_type
                    self.get_var_index(aname)
            else:
                vname = it.upper()
                self.var_types[vname] = base_type
                self.get_var_index(vname)

    def _parse_data_stmt(self, stmt):
        # DATA A, B / 10, 20 /  or  DATA A/10/, B/20/
        rest = stmt[5:].strip()
        pairs = re.findall(r"([A-Za-z0-9_,\s]+?)/([^/]+)/", rest)
        for v_part, val_part in pairs:
            vnames = [x.strip().upper() for x in v_part.split(",") if x.strip()]
            vals = [x.strip() for x in val_part.split(",") if x.strip()]
            for vn, vv in zip(vnames, vals):
                if (vv.startswith("'") and vv.endswith("'")) or (vv.startswith('"') and vv.endswith('"')):
                    self.data_inits.append((vn, vv[1:-1]))
                elif "." in vv:
                    self.data_inits.append((vn, float(vv)))
                else:
                    self.data_inits.append((vn, int(vv)))

    def _close_do_loop(self, do_info):
        var = do_info["var"]
        self.emit_load_v(var)
        self.eval_expr(do_info["step"])
        self.emit_u8(0x20)  # OP_ADD
        self.emit_store_v(var)
        self.emit_jmp(do_info["loop_lbl"])
        self.line_offsets[do_info["exit_lbl"]] = len(self.bytecode)

    def _split_write_items(self, s):
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

    def _compile_stmt(self, stmt):
        s = stmt.strip()
        up = s.upper()

        if up.startswith(("PROGRAM ", "INTEGER", "REAL", "CHARACTER", "DIMENSION", "DATA ", "FORMAT", "IMPLICIT")):
            return
        if up == "CONTINUE":
            return
        if up in ("STOP", "END") or up.startswith("STOP "):
            self.emit_u8(0x00)  # OP_HALT
            return
        if up == "RETURN":
            self.emit_u8(0x41)  # OP_RET
            return
        if up.startswith("SUBROUTINE "):
            m = re.match(r"^SUBROUTINE\s+([A-Za-z_][A-Za-z0-9_]*)", s, re.IGNORECASE)
            if m:
                self.line_offsets[m.group(1).upper()] = len(self.bytecode)
            return
        if up.startswith("CALL "):
            m = re.match(r"^CALL\s+([A-Za-z_][A-Za-z0-9_]*)", s, re.IGNORECASE)
            if m:
                self.emit_call(m.group(1).upper())
            return
        if up.startswith("GOTO ") or up.startswith("GO TO "):
            tgt = re.sub(r"^GO\s*TO\s+", "", s, flags=re.IGNORECASE).strip()
            self.emit_jmp(tgt)
            return
        if up.startswith("DO "):
            # DO 100 I = 1, 10 [, 2]  or  DO I = 1, 10
            m = re.match(r"^DO\s+(\d+)?\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", s, re.IGNORECASE)
            if m:
                end_lbl = m.group(1) or "ENDDO"
                var = m.group(2).upper()
                bounds = [x.strip() for x in m.group(3).split(",")]
                from_e = bounds[0]
                to_e = bounds[1] if len(bounds) > 1 else "1"
                step_e = bounds[2] if len(bounds) > 2 else "1"

                self.eval_expr(from_e)
                self.emit_store_v(var)
                loop_lbl = f"__DO_LP_{len(self.bytecode)}"
                exit_lbl = f"__DO_EX_{len(self.bytecode)}"
                self.line_offsets[loop_lbl] = len(self.bytecode)
                self.emit_load_v(var)
                self.eval_expr(to_e)
                self.emit_u8(0x27)  # GT
                self.emit_push_i(0)
                self.emit_u8(0x24)  # EQ 0 (var <= to_e)
                self.emit_jmp_z(exit_lbl)
                self.do_stack.append({
                    "end_label": str(end_lbl),
                    "var": var,
                    "step": step_e,
                    "loop_lbl": loop_lbl,
                    "exit_lbl": exit_lbl,
                })
            return
        if up in ("ENDDO", "END DO"):
            if self.do_stack:
                do_info = self.do_stack.pop()
                self._close_do_loop(do_info)
            return
        if up.startswith("WRITE") or up.startswith("PRINT"):
            items_str = ""
            if up.startswith("WRITE"):
                m = re.match(r"^WRITE\s*\([^)]*\)\s*(.*)$", s, re.IGNORECASE)
                if m:
                    items_str = m.group(1).strip()
            else:
                m = re.match(r"^PRINT\s*(?:\*|\d+)\s*,?\s*(.*)$", s, re.IGNORECASE)
                if m:
                    items_str = m.group(1).strip()
            items = self._split_write_items(items_str)
            if not items:
                self.emit_push_s("")
                self.emit_u8(0x50)
                return
            for idx, it in enumerate(items):
                self.eval_expr(it)
                if idx < len(items) - 1:
                    self.emit_u8(0x51)  # OP_PRINT_NO_NL
                else:
                    self.emit_u8(0x50)  # OP_PRINT
            return
        if up.startswith("READ"):
            m = re.match(r"^READ\s*(?:\([^)]*\)|\*)\s*,?\s*(.+)$", s, re.IGNORECASE)
            if m:
                vname = m.group(1).strip().split(",")[0].strip().upper()
                idx = self.get_var_index(vname)
                if self.get_var_type(vname) == "STR":
                    self.emit_u8(0x71)
                else:
                    self.emit_u8(0x70)
                self.emit_u16(idx)
            return
        if up.startswith("IF"):
            m_blk = re.match(r"^IF\s*\((.+)\)\s*THEN$", s, re.IGNORECASE)
            if m_blk:
                cond = m_blk.group(1)
                else_lbl = f"__F77_ELSE_{len(self.bytecode)}"
                end_lbl = f"__F77_END_{len(self.bytecode)}"
                self.eval_expr(cond)
                self.emit_jmp_z(else_lbl)
                self.if_stack.append({"else_lbl": else_lbl, "end_lbl": end_lbl, "has_else": False})
                return
            m_single = re.match(r"^IF\s*\((.+?)\)\s*(.+)$", s, re.IGNORECASE)
            if m_single:
                cond = m_single.group(1)
                action = m_single.group(2).strip()
                skip_lbl = f"__F77_SKIP_{len(self.bytecode)}"
                self.eval_expr(cond)
                self.emit_jmp_z(skip_lbl)
                self._compile_stmt(action)
                self.line_offsets[skip_lbl] = len(self.bytecode)
                return
        if up == "ELSE":
            if self.if_stack:
                top = self.if_stack[-1]
                self.emit_jmp(top["end_lbl"])
                self.line_offsets[top["else_lbl"]] = len(self.bytecode)
                top["has_else"] = True
            return
        if up in ("ENDIF", "END IF"):
            if self.if_stack:
                top = self.if_stack.pop()
                if not top["has_else"]:
                    self.line_offsets[top["else_lbl"]] = len(self.bytecode)
                self.line_offsets[top["end_lbl"]] = len(self.bytecode)
            return

        # Assignment: VAR = EXPR or ARR(IDX) = EXPR
        if "=" in s:
            lhs, rhs = s.split("=", 1)
            lhs = lhs.strip().upper()
            rhs = rhs.strip()
            if "(" in lhs and lhs.endswith(")"):
                m = re.match(r"^([A-Z_][A-Z0-9_]*)\((.+)\)$", lhs)
                if m:
                    aname, idx_e = m.group(1), m.group(2)
                    self.eval_expr(rhs)
                    self.eval_expr(idx_e)
                    idx = self.get_var_index(aname)
                    self.emit_u8(0x16)  # OP_STORE_A
                    self.emit_u16(idx)
                    return
            self.eval_expr(rhs)
            if self.get_var_type(lhs) == "INT":
                self.emit_u8(0x75)  # OP_INT
            self.emit_store_v(lhs)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "version": 1,
            "module": "MAIN",
            "program": self.program_name,
            "compiler": f"DEC PDP-11 FORTRAN-77 {self.VERSION}",
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
                f.write(f"DEC PDP-11 FORTRAN-77 {self.VERSION} (RSTS/E V10.1-L)   PROGRAM: {self.program_name}\n")
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
        print("Usage: fortran <input.for> [-o output.obj] [-l listing.lst] [--module NAME]")
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
        print("?FORTRAN-F-NOFILE, no input .FOR/.FTN file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".FOR", ".for", ".FTN", ".ftn", ".F77", ".f77"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"?FORTRAN-F-FNF, cannot find FORTRAN source file {in_file}")
        sys.exit(1)

    if not out_obj:
        stem, _ = os.path.splitext(in_file)
        out_obj = stem + ".OBJ"

    with open(in_file, "r", errors="replace") as f:
        src_text = f.read()

    comp = Fortran77Compiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"FORTRAN-77 {Fortran77Compiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
