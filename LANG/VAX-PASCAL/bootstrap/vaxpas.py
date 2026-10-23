#!/usr/bin/env python3
"""
DEC VAX Pascal V4.3 Compiler (vaxpas.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Compiles VAX Pascal V4.3 source programs (.PAS) into OpenVMS relocatable object
modules (.OBJ) compatible with the OpenVMS Linker (vmslink) and image activator
(vms_vm), plus optional compiler listing files (.LST).
"""

import os
import re
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAX_BASIC_BOOTSTRAP = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "VAX-BASIC", "bootstrap"))
if os.path.isdir(VAX_BASIC_BOOTSTRAP) and VAX_BASIC_BOOTSTRAP not in sys.path:
    sys.path.insert(0, VAX_BASIC_BOOTSTRAP)
elif os.path.isdir("/opt/dec-vms/system/lib/lang") and "/opt/dec-vms/system/lib/lang" not in sys.path:
    sys.path.insert(0, "/opt/dec-vms/system/lib/lang")

from vaxbasic import (  # noqa: E402
    VAXBasicCompiler,
    OP_HALT,
    OP_ADD,
    OP_SUB,
    OP_EQ,
    OP_GE,
    OP_LE,
    OP_AND,
    OP_OR,
    OP_JMP,
    OP_JMP_FALSE,
    OP_CALL,
    OP_RET,
    OP_CALL_OVL,
    OP_PRINT_CH,
    OP_DIM_ARR,
    OP_STORE_ARR,
    OP_INPUT_I,
    OP_INPUT_S,
)


class Tok:
    __slots__ = ("kind", "val", "line")

    def __init__(self, kind, val, line):
        self.kind = kind
        self.val = val
        self.line = line

    def __repr__(self):
        return f"Tok({self.kind}, {self.val!r}, L{self.line})"


class VAXPascalCompiler(VAXBasicCompiler):
    VERSION = "V4.3-00"
    CREATOR_NAME = "DEC VAX PASCAL V4.3-00"

    def __init__(self, module_name="MAIN"):
        super().__init__(module_name=module_name)
        self.ident = "V04-03"
        self.constants["TRUE"] = ("INT", 1)
        self.constants["FALSE"] = ("INT", 0)
        self.constants["MAXINT"] = ("INT", 2147483647)
        self.type_defs = {}  # type_name -> ('RECORD', [(fname, vtype)]) | ('ARRAY', size, elem_vtype) | ('SCALAR', vtype)
        self.array_vars = {}  # var_name -> (size, elem_vtype)
        self.line_offsets = {}

    def _strip_pascal_comments(self, text):
        out = []
        i = 0
        n = len(text)
        in_str = False
        while i < n:
            ch = text[i]
            if in_str:
                out.append(ch)
                if ch == "'":
                    if i + 1 < n and text[i + 1] == "'":
                        out.append("'")
                        i += 2
                        continue
                    in_str = False
                i += 1
                continue
            if ch == "'":
                in_str = True
                out.append(ch)
                i += 1
                continue
            if ch == "{":
                i += 1
                while i < n and text[i] != "}":
                    if text[i] == "\n":
                        out.append("\n")
                    i += 1
                if i < n and text[i] == "}":
                    i += 1
                continue
            if ch == "(" and i + 1 < n and text[i + 1] == "*":
                i += 2
                while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == ")"):
                    if text[i] == "\n":
                        out.append("\n")
                    i += 1
                if i + 1 < n:
                    i += 2
                continue
            out.append(ch)
            i += 1
        return "".join(out)

    def _lex(self, text):
        cleaned = self._strip_pascal_comments(text)
        tokens = []
        i = 0
        n = len(cleaned)
        line = 1
        while i < n:
            ch = cleaned[i]
            if ch == "\n":
                line += 1
                i += 1
                continue
            if ch in (" ", "\t", "\r"):
                i += 1
                continue
            if ch in ("'", '"'):
                q = ch
                i += 1
                buf = []
                while i < n:
                    if cleaned[i] == "\n":
                        line += 1
                    if cleaned[i] == q:
                        if i + 1 < n and cleaned[i + 1] == q:
                            buf.append(q)
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(cleaned[i])
                    i += 1
                tokens.append(Tok("STR", "".join(buf), line))
                continue
            if cleaned[i:i + 2] in (":=", "<=", ">=", "<>", ".."):
                tokens.append(Tok("SYM", cleaned[i:i + 2], line))
                i += 2
                continue
            if ch in "+-*/=<>(),.;:[]^":
                tokens.append(Tok("SYM", ch, line))
                i += 1
                continue
            if ch.isdigit():
                j = i
                has_dot = False
                while j < n and (cleaned[j].isdigit() or (cleaned[j] == "." and j + 1 < n and cleaned[j + 1] != ".")):
                    if cleaned[j] == ".":
                        has_dot = True
                    j += 1
                num_s = cleaned[i:j]
                if has_dot:
                    tokens.append(Tok("FLOAT", float(num_s), line))
                else:
                    tokens.append(Tok("INT", int(num_s), line))
                i = j
                continue
            if ch.isalpha() or ch in ("_", "$"):
                j = i
                while j < n and (cleaned[j].isalnum() or cleaned[j] in ("_", "$")):
                    j += 1
                tokens.append(Tok("ID", cleaned[i:j].upper(), line))
                i = j
                continue
            i += 1
        return tokens

    def _normalize_pascal_expr(self, expr_str):
        # Convert Pascal array brackets arr[idx] to arr(idx), DIV to /, etc.
        out = []
        in_q = None
        i = 0
        n = len(expr_str)
        while i < n:
            ch = expr_str[i]
            if ch in ("'", '"'):
                if in_q is None:
                    in_q = ch
                elif in_q == ch:
                    in_q = None
                out.append(ch)
                i += 1
                continue
            if in_q is None:
                if ch == "[":
                    out.append("(")
                    i += 1
                    continue
                if ch == "]":
                    out.append(")")
                    i += 1
                    continue
                if expr_str[i:i + 5].upper() == " DIV " or (i > 0 and expr_str[i - 1] in " )" and expr_str[i:i + 4].upper() == "DIV "):
                    out.append(" / ")
                    i += 4
                    continue
            out.append(ch)
            i += 1
        s = "".join(out)
        s = re.sub(r"\bDIV\b", "/", s, flags=re.IGNORECASE)
        return s

    def compile_expr(self, expr_str):
        super().compile_expr(self._normalize_pascal_expr(expr_str))

    def _mark_line(self, line):
        if line not in self.line_offsets:
            self.line_offsets[line] = len(self.bytecode)

    def _pk(self, offset=0):
        idx = self._tpos + offset
        if 0 <= idx < len(self._toks):
            t = self._toks[idx]
            self._mark_line(t.line)
            return t
        return Tok("EOF", "", self._toks[-1].line if self._toks else 1)

    def _nx(self):
        t = self._pk()
        self._tpos += 1
        return t

    def _match(self, kind, val=None):
        t = self._pk()
        if t.kind == kind and (val is None or t.val == val):
            self._tpos += 1
            return t
        return None

    def _tokens_to_expr_str(self, tok_list):
        parts = []
        for idx, t in enumerate(tok_list):
            if t.kind == "STR":
                escaped = t.val.replace('"', '""')
                parts.append(f'"{escaped}"')
            elif t.kind in ("INT", "FLOAT"):
                parts.append(str(t.val))
            elif t.kind == "ID":
                if t.val == "DIV":
                    parts.append(" / ")
                elif t.val in ("AND", "OR", "NOT", "MOD", "XOR"):
                    parts.append(f" {t.val} ")
                elif idx + 1 < len(tok_list) and tok_list[idx + 1].val == ".":
                    parts.append(t.val)
                elif idx > 0 and tok_list[idx - 1].val == ".":
                    parts.append(t.val)
                else:
                    parts.append(t.val)
            elif t.kind == "SYM":
                if t.val == "[":
                    parts.append("(")
                elif t.val == "]":
                    parts.append(")")
                elif t.val == ".":
                    parts.append("::")
                elif t.val in ("<=", ">=", "<>", "=", "<", ">", "+", "-", "*", "/"):
                    parts.append(f" {t.val} ")
                else:
                    parts.append(t.val)
        return "".join(parts).strip()

    def _collect_expr_tokens(self, stop_vals=None, stop_ids=None):
        stop_vals = set(stop_vals or ())
        stop_ids = set(stop_ids or ())
        collected = []
        depth = 0
        while self._pk().kind != "EOF":
            t = self._pk()
            if depth == 0:
                if t.kind == "SYM" and t.val in stop_vals:
                    break
                if t.kind == "ID" and t.val in stop_ids:
                    break
            if t.kind == "SYM" and t.val in ("(", "["):
                depth += 1
            elif t.kind == "SYM" and t.val in (")", "]"):
                if depth == 0 and t.val in stop_vals:
                    break
                depth = max(0, depth - 1)
            collected.append(self._nx())
        return collected

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        self._toks = self._lex(source_text)
        self._tpos = 0

        # Parse optional [IDENT('...')] module attributes
        while self._pk().val == "[":
            self._nx()
            while self._pk().kind != "EOF" and self._pk().val != "]":
                t = self._nx()
                if t.kind == "ID" and t.val == "IDENT":
                    if self._match("SYM", "("):
                        st = self._nx()
                        if st.kind == "STR":
                            self.ident = st.val
                        self._match("SYM", ")")
            self._match("SYM", "]")

        # Parse PROGRAM <name>(...) ; or MODULE <name> ;
        if self._pk().kind == "ID" and self._pk().val in ("PROGRAM", "MODULE"):
            self._nx()
            if self._pk().kind == "ID":
                pname = self._nx().val
                if self.module_name == "MAIN":
                    self.module_name = pname[:16]
            if self._match("SYM", "("):
                while self._pk().kind != "EOF" and self._pk().val != ")":
                    self._nx()
                self._match("SYM", ")")
            self._match("SYM", ";")

        self._parse_block(is_main=True)
        self.emit_u8(OP_HALT)

        for fix_pos, target_lbl, src_line in self.fixups:
            if target_lbl in self.labels:
                addr = self.labels[target_lbl]
                self.bytecode[fix_pos] = addr & 0xFF
                self.bytecode[fix_pos + 1] = (addr >> 8) & 0xFF

        last_off = 0
        for idx, raw in enumerate(raw_lines, start=1):
            off = self.line_offsets.get(idx, last_off)
            last_off = off
            self.listing_lines.append((idx, off, raw.rstrip("\r\n")))

    def _parse_type_spec(self):
        t = self._pk()
        if t.kind == "ID" and t.val == "VARYING":
            self._nx()
            if self._match("SYM", "["):
                while self._pk().kind != "EOF" and self._pk().val != "]":
                    self._nx()
                self._match("SYM", "]")
            self._match("ID", "OF")
            if self._pk().kind == "ID":
                self._nx()
            return ("SCALAR", "STR")
        if t.kind == "ID" and t.val == "PACKED":
            self._nx()
            return self._parse_type_spec()
        if t.kind == "ID" and t.val == "ARRAY":
            self._nx()
            hi_val = 64
            if self._match("SYM", "["):
                b_toks = self._collect_expr_tokens(stop_vals={"]"})
                self._match("SYM", "]")
                ints = [tk.val for tk in b_toks if tk.kind == "INT"]
                if ints:
                    hi_val = max(ints) + 2
            self._match("ID", "OF")
            _, elem_vtype = self._parse_type_spec()
            return ("ARRAY", hi_val, elem_vtype)
        if t.kind == "ID" and t.val == "RECORD":
            self._nx()
            fields = []
            while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                if self._match("SYM", ";"):
                    continue
                fnames = []
                while self._pk().kind == "ID":
                    fnames.append(self._nx().val)
                    if not self._match("SYM", ","):
                        break
                if self._match("SYM", ":"):
                    tspec = self._parse_type_spec()
                    fvtype = tspec[1] if tspec[0] == "SCALAR" else "INT"
                    for fn in fnames:
                        fields.append((fn, fvtype))
                else:
                    self._nx()
                self._match("SYM", ";")
            self._match("ID", "END")
            return ("RECORD", fields)
        if t.kind == "ID":
            tname = self._nx().val
            if tname in self.type_defs:
                return self.type_defs[tname]
            if tname in ("STRING", "CHAR", "TEXT"):
                return ("SCALAR", "STR")
            if tname in ("REAL", "SINGLE", "DOUBLE", "G_FLOAT", "D_FLOAT"):
                return ("SCALAR", "FLOAT")
            return ("SCALAR", "INT")
        # Subrange lo..hi
        self._collect_expr_tokens(stop_vals={";", ")"})
        return ("SCALAR", "INT")

    def _register_var(self, vname, tspec):
        kind = tspec[0]
        if kind == "RECORD":
            rec_key = f"__ANON_REC_{vname}"
            self.record_defs[rec_key] = tspec[1]
            self.record_vars[vname] = rec_key
            for fn, ft in tspec[1]:
                self.get_var_id(f"{vname}.{fn}", ft)
        elif kind == "ARRAY":
            _, sz, elem_t = tspec
            self.array_vars[vname] = (sz, elem_t)
            vid = self.get_var_id(vname, elem_t)
            self.emit_push_int(sz)
            self.emit_u8(OP_DIM_ARR)
            self.emit_u16(vid)
        else:
            self.get_var_id(vname, tspec[1])

    def _parse_block(self, is_main=False):
        while self._pk().kind == "ID" and self._pk().val in ("CONST", "TYPE", "VAR", "PROCEDURE", "FUNCTION", "LABEL"):
            kw = self._nx().val
            if kw == "LABEL":
                while self._pk().kind != "EOF" and self._pk().val != ";":
                    self._nx()
                self._match("SYM", ";")
            elif kw == "CONST":
                while self._pk().kind == "ID" and self._pk().val not in (
                    "TYPE", "VAR", "PROCEDURE", "FUNCTION", "BEGIN", "CONST"
                ):
                    cname = self._nx().val
                    if self._match("SYM", "="):
                        etoks = self._collect_expr_tokens(stop_vals={";"})
                        if len(etoks) == 1 and etoks[0].kind in ("STR", "INT", "FLOAT"):
                            self.constants[cname] = (etoks[0].kind, etoks[0].val)
                        elif len(etoks) == 2 and etoks[0].val == "-" and etoks[1].kind in ("INT", "FLOAT"):
                            self.constants[cname] = (etoks[1].kind, -etoks[1].val)
                        else:
                            expr_s = self._tokens_to_expr_str(etoks)
                            self.compile_expr(expr_s)
                            self.emit_store_var(cname)
                    self._match("SYM", ";")
            elif kw == "TYPE":
                while self._pk().kind == "ID" and self._pk().val not in (
                    "CONST", "VAR", "PROCEDURE", "FUNCTION", "BEGIN", "TYPE"
                ):
                    tname = self._nx().val
                    if self._match("SYM", "="):
                        tspec = self._parse_type_spec()
                        self.type_defs[tname] = tspec
                        if tspec[0] == "RECORD":
                            self.record_defs[tname] = tspec[1]
                    self._match("SYM", ";")
            elif kw == "VAR":
                while self._pk().kind == "ID" and self._pk().val not in (
                    "CONST", "TYPE", "PROCEDURE", "FUNCTION", "BEGIN", "VAR"
                ):
                    vnames = []
                    while self._pk().kind == "ID":
                        vnames.append(self._nx().val)
                        if not self._match("SYM", ","):
                            break
                    if self._match("SYM", ":"):
                        tspec = self._parse_type_spec()
                        for vn in vnames:
                            self._register_var(vn, tspec)
                        if self._match("SYM", ":="):
                            init_toks = self._collect_expr_tokens(stop_vals={";"})
                            init_s = self._tokens_to_expr_str(init_toks)
                            for vn in vnames:
                                self.compile_expr(init_s)
                                self.emit_store_var(vn)
                    self._match("SYM", ";")
            elif kw in ("PROCEDURE", "FUNCTION"):
                is_fn = kw == "FUNCTION"
                sub_name = self._nx().val
                params = []
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and self._pk().val != ")":
                        if self._pk().kind == "ID" and self._pk().val in ("VAR", "VALUE"):
                            self._nx()
                        pnames = []
                        while self._pk().kind == "ID":
                            pnames.append(self._nx().val)
                            if not self._match("SYM", ","):
                                break
                        if self._match("SYM", ":"):
                            ptspec = self._parse_type_spec()
                            pvtype = ptspec[1] if ptspec[0] == "SCALAR" else "INT"
                            for pn in pnames:
                                self.get_var_id(pn, pvtype)
                                params.append(pn)
                        self._match("SYM", ";")
                    self._match("SYM", ")")
                if is_fn:
                    ret_vtype = "INT"
                    if self._match("SYM", ":"):
                        rtspec = self._parse_type_spec()
                        ret_vtype = rtspec[1] if rtspec[0] == "SCALAR" else "INT"
                    self.get_var_id(sub_name, ret_vtype)
                    self.fn_defs[sub_name] = {
                        "label": f"__FN_{sub_name}",
                        "ret_var": sub_name,
                        "params": params,
                    }
                else:
                    self.sub_defs[sub_name] = {
                        "label": f"__SUB_{sub_name}",
                        "params": params,
                    }
                self._match("SYM", ";")
                if self._pk().kind == "ID" and self._pk().val in ("EXTERNAL", "FORWARD"):
                    self._nx()
                    self._match("SYM", ";")
                    continue
                end_lbl = f"__ENDSUB_{sub_name}"
                self.emit_jump(OP_JMP, end_lbl)
                lbl_key = f"__FN_{sub_name}" if is_fn else f"__SUB_{sub_name}"
                self.labels[lbl_key] = len(self.bytecode)
                self._parse_block(is_main=False)
                self._match("SYM", ";")
                self.emit_u8(OP_RET)
                self.labels[end_lbl] = len(self.bytecode)

        if self._match("ID", "BEGIN"):
            while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                if self._match("SYM", ";"):
                    continue
                self._parse_stmt()
                self._match("SYM", ";")
            self._match("ID", "END")
            if is_main:
                self._match("SYM", ".")

    def _parse_stmt(self):
        t = self._pk()
        if t.kind == "EOF" or t.val in (";", "END", "ELSE", "UNTIL", "OTHERWISE"):
            return

        if t.kind in ("INT", "ID") and self._pk(1).val == ":":
            lbl = str(self._nx().val).upper()
            self._nx()
            self.labels[lbl] = len(self.bytecode)
            self._parse_stmt()
            return

        if t.kind == "ID":
            kw = t.val
            if kw == "BEGIN":
                self._nx()
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                    if self._match("SYM", ";"):
                        continue
                    self._parse_stmt()
                    self._match("SYM", ";")
                self._match("ID", "END")
                return

            if kw in ("WRITELN", "WRITE"):
                self._nx()
                has_nl = 1 if kw == "WRITELN" else 0
                args = []
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                        arg_toks = self._collect_expr_tokens(stop_vals={",", ")", ":"})
                        while self._match("SYM", ":"):
                            self._collect_expr_tokens(stop_vals={",", ")", ":"})
                        if arg_toks:
                            args.append(self._tokens_to_expr_str(arg_toks))
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ")")
                if not args:
                    self.emit_str("")
                    self.emit_u8(OP_PRINT_CH)
                    self.emit_u8(0)
                    self.emit_u8(has_nl)
                else:
                    for idx, a_expr in enumerate(args):
                        is_last = idx == len(args) - 1
                        self.compile_expr(a_expr)
                        self.emit_u8(OP_PRINT_CH)
                        self.emit_u8(0)
                        self.emit_u8(has_nl if is_last else 0)
                return

            if kw in ("READLN", "READ"):
                self._nx()
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and self._pk().val != ")":
                        v_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                        vname = self._tokens_to_expr_str(v_toks)
                        if vname:
                            vid = self.get_var_id(vname)
                            self.emit_u8(OP_INPUT_S if self.is_str_var(vname) else OP_INPUT_I)
                            self.emit_u16(vid)
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ")")
                return

            if kw == "IF":
                self._nx()
                cond_toks = self._collect_expr_tokens(stop_ids={"THEN"})
                self._match("ID", "THEN")
                self.loop_counter += 1
                if_id = self.loop_counter
                else_lbl = f"__PAS_ELSE_{if_id}"
                end_lbl = f"__PAS_ENDIF_{if_id}"
                self.compile_expr(self._tokens_to_expr_str(cond_toks))
                self.emit_jump(OP_JMP_FALSE, else_lbl)
                self._parse_stmt()
                if self._pk().kind == "ID" and self._pk().val == "ELSE":
                    self._nx()
                    self.emit_jump(OP_JMP, end_lbl)
                    self.labels[else_lbl] = len(self.bytecode)
                    self._parse_stmt()
                    self.labels[end_lbl] = len(self.bytecode)
                else:
                    self.labels[else_lbl] = len(self.bytecode)
                return

            if kw == "WHILE":
                self._nx()
                cond_toks = self._collect_expr_tokens(stop_ids={"DO"})
                self._match("ID", "DO")
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__PAS_WTOP_{lid}"
                end_lbl = f"__PAS_WEND_{lid}"
                self.labels[top_lbl] = len(self.bytecode)
                self.compile_expr(self._tokens_to_expr_str(cond_toks))
                self.emit_jump(OP_JMP_FALSE, end_lbl)
                self._parse_stmt()
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "REPEAT":
                self._nx()
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__PAS_RTOP_{lid}"
                self.labels[top_lbl] = len(self.bytecode)
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "UNTIL"):
                    if self._match("SYM", ";"):
                        continue
                    self._parse_stmt()
                    self._match("SYM", ";")
                self._match("ID", "UNTIL")
                cond_toks = self._collect_expr_tokens(stop_vals={";"}, stop_ids={"END", "ELSE", "UNTIL"})
                self.compile_expr(self._tokens_to_expr_str(cond_toks))
                self.emit_jump(OP_JMP_FALSE, top_lbl)
                return

            if kw == "FOR":
                self._nx()
                vname = self._nx().val
                self._match("SYM", ":=")
                lo_toks = self._collect_expr_tokens(stop_ids={"TO", "DOWNTO"})
                dir_kw = self._nx().val if self._pk().kind == "ID" else "TO"
                hi_toks = self._collect_expr_tokens(stop_ids={"DO"})
                self._match("ID", "DO")
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__PAS_FTOP_{lid}"
                end_lbl = f"__PAS_FEND_{lid}"
                self.compile_expr(self._tokens_to_expr_str(lo_toks))
                self.emit_store_var(vname)
                self.labels[top_lbl] = len(self.bytecode)
                self.emit_load_var(vname)
                self.compile_expr(self._tokens_to_expr_str(hi_toks))
                self.emit_u8(OP_GE if dir_kw == "DOWNTO" else OP_LE)
                self.emit_jump(OP_JMP_FALSE, end_lbl)
                self._parse_stmt()
                self.emit_load_var(vname)
                self.emit_push_int(1)
                self.emit_u8(OP_SUB if dir_kw == "DOWNTO" else OP_ADD)
                self.emit_store_var(vname)
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "CASE":
                self._nx()
                sel_toks = self._collect_expr_tokens(stop_ids={"OF"})
                self._match("ID", "OF")
                self.select_counter += 1
                sid = self.select_counter
                sel_var = f"__PAS_CASE_{sid}"
                sel_expr_s = self._tokens_to_expr_str(sel_toks)
                if any(tk.kind == "STR" for tk in sel_toks):
                    self.get_var_id(sel_var, "STR")
                self.compile_expr(sel_expr_s)
                self.emit_store_var(sel_var)
                end_lbl = f"__PAS_CASE_END_{sid}"
                c_idx = 0
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                    if self._match("SYM", ";"):
                        continue
                    if self._pk().kind == "ID" and self._pk().val in ("OTHERWISE", "ELSE"):
                        self._nx()
                        self._match("SYM", ":")
                        while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                            if self._match("SYM", ";"):
                                continue
                            self._parse_stmt()
                            self._match("SYM", ";")
                        break
                    c_idx += 1
                    next_lbl = f"__PAS_CASE_{sid}_{c_idx}"
                    clauses = []
                    while self._pk().kind != "EOF" and self._pk().val != ":":
                        cl_toks = self._collect_expr_tokens(stop_vals={",", ":"})
                        if cl_toks:
                            clauses.append(cl_toks)
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ":")
                    for cl_i, cl in enumerate(clauses):
                        dots_idx = next((idx for idx, tk in enumerate(cl) if tk.val == ".."), -1)
                        if dots_idx != -1:
                            lo_s = self._tokens_to_expr_str(cl[:dots_idx])
                            hi_s = self._tokens_to_expr_str(cl[dots_idx + 1:])
                            self.emit_load_var(sel_var)
                            self.compile_expr(lo_s)
                            self.emit_u8(OP_GE)
                            self.emit_load_var(sel_var)
                            self.compile_expr(hi_s)
                            self.emit_u8(OP_LE)
                            self.emit_u8(OP_AND)
                        else:
                            val_s = self._tokens_to_expr_str(cl)
                            self.emit_load_var(sel_var)
                            self.compile_expr(val_s)
                            self.emit_u8(OP_EQ)
                        if cl_i > 0:
                            self.emit_u8(OP_OR)
                    self.emit_jump(OP_JMP_FALSE, next_lbl)
                    self._parse_stmt()
                    self.emit_jump(OP_JMP, end_lbl)
                    self.labels[next_lbl] = len(self.bytecode)
                    self._match("SYM", ";")
                self._match("ID", "END")
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "GOTO":
                self._nx()
                tgt = str(self._nx().val).upper()
                self.emit_jump(OP_JMP, tgt)
                return

            # Procedure call or Assignment
            lhs_toks = [self._nx()]
            while self._pk().val in (".", "["):
                if self._pk().val == ".":
                    lhs_toks.append(self._nx())
                    lhs_toks.append(self._nx())
                elif self._pk().val == "[":
                    lhs_toks.append(self._nx())
                    lhs_toks.extend(self._collect_expr_tokens(stop_vals={"]"}))
                    if self._pk().val == "]":
                        lhs_toks.append(self._nx())

            if self._match("SYM", ":="):
                rhs_toks = self._collect_expr_tokens(
                    stop_vals={";"}, stop_ids={"END", "ELSE", "UNTIL", "OTHERWISE"}
                )
                rhs_s = self._tokens_to_expr_str(rhs_toks)
                lhs_s = self._tokens_to_expr_str(lhs_toks).replace("::", ".")
                m_arr = re.match(r"^([A-Za-z0-9_.$]+)\s*\((.+)\)$", lhs_s)
                if m_arr:
                    aname = m_arr.group(1).upper()
                    idx_e = m_arr.group(2)
                    self.compile_expr(rhs_s)
                    self.compile_expr(idx_e)
                    self.emit_u8(OP_STORE_ARR)
                    self.emit_u16(self.get_var_id(aname))
                else:
                    if any(tk.kind == "STR" for tk in rhs_toks) or any(
                        tk.kind == "ID" and self.is_str_var(tk.val) for tk in rhs_toks
                    ):
                        self.get_var_id(lhs_s, "STR")
                    self.compile_expr(rhs_s)
                    self.emit_store_var(lhs_s)
                return

            # Procedure call
            proc_name = lhs_toks[0].val
            args = []
            if self._match("SYM", "("):
                while self._pk().kind != "EOF" and self._pk().val != ")":
                    a_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                    if a_toks:
                        args.append(self._tokens_to_expr_str(a_toks))
                    if not self._match("SYM", ","):
                        break
                self._match("SYM", ")")
            if proc_name in self.sub_defs:
                sub_info = self.sub_defs[proc_name]
                for idx_a, a_expr in enumerate(args):
                    if idx_a < len(sub_info["params"]):
                        self.compile_expr(a_expr)
                        self.emit_store_var(sub_info["params"][idx_a])
                self.emit_jump(OP_CALL, sub_info["label"])
            else:
                self.emit_u8(OP_CALL_OVL)
                rel_off = len(self.bytecode)
                self.emit_u16(0)
                self.relocations.append({"offset": rel_off, "type": "CALL_OVL", "target": proc_name})
            return

        # Fallback: advance token
        self._nx()

    def write_outputs(self, out_obj, out_lst=None):
        super().write_outputs(out_obj, out_lst=None)
        import json
        with open(out_obj, "r") as f:
            obj_data = json.load(f)
        obj_data["creator"] = self.CREATOR_NAME
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(
                    f"{self.CREATOR_NAME} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n"
                )
                f.write("Line  Offset  Source Statement\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nStorage Allocation & Symbol Map:\n")
                for vname, vid in sorted(self.var_map.items(), key=lambda x: x[1]):
                    if not vname.startswith("__"):
                        vtype = self.var_types.get(vname, "INTEGER")
                        f.write(f"  Slot {vid:>3} : {vname:<28} ({vtype})\n")
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
        print("Usage: vaxpas <source.pas> [-o out.OBJ] [-l [out.LST]] [/OBJECT=...] [/LIST[=...]]")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".PAS", ".pas"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%PASCAL-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXPascalCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX PASCAL {VAXPascalCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
