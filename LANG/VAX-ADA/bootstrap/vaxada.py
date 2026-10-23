#!/usr/bin/env python3
"""
DEC VAX Ada V2.2 Compiler (vaxada.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Compiles DEC VAX Ada V2.2 (MIL-STD-1815A / Ada 83) source programs (.ADA) into
OpenVMS relocatable object modules (.OBJ) compatible with the OpenVMS Linker
(vmslink) and image activator (vms_vm), plus optional compiler listings (.LST).
"""

import os
import re
import sys
import json
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


class VAXAdaCompiler(VAXBasicCompiler):
    VERSION = "V2.2-00"
    CREATOR_NAME = "DEC VAX ADA V2.2-00"

    def __init__(self, module_name="MAIN"):
        super().__init__(module_name=module_name)
        self.ident = "V02-02"
        self.constants["TRUE"] = ("INT", 1)
        self.constants["FALSE"] = ("INT", 0)
        self.type_defs = {}
        self.line_offsets = {}
        self.cur_fn_stack = []
        self.loop_exit_stack = []

    def _strip_ada_comments(self, text):
        out = []
        i = 0
        n = len(text)
        in_str = False
        while i < n:
            ch = text[i]
            if in_str:
                out.append(ch)
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        out.append('"')
                        i += 2
                        continue
                    in_str = False
                i += 1
                continue
            if ch == '"':
                in_str = True
                out.append(ch)
                i += 1
                continue
            if ch == "-" and i + 1 < n and text[i + 1] == "-":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            out.append(ch)
            i += 1
        return "".join(out)

    def _lex(self, text):
        cleaned = self._strip_ada_comments(text)
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
            if ch == '"':
                i += 1
                buf = []
                while i < n:
                    if cleaned[i] == "\n":
                        line += 1
                    if cleaned[i] == '"':
                        if i + 1 < n and cleaned[i + 1] == '"':
                            buf.append('"')
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(cleaned[i])
                    i += 1
                tokens.append(Tok("STR", "".join(buf), line))
                continue
            if ch == "'" and i + 2 < n and cleaned[i + 2] == "'":
                tokens.append(Tok("STR", cleaned[i + 1], line))
                i += 3
                continue
            if cleaned[i:i + 2] in (":=", "=>", "..", "<=", ">=", "/=", "<>"):
                op2 = cleaned[i:i + 2]
                if op2 == "/=":
                    op2 = "<>"
                tokens.append(Tok("SYM", op2, line))
                i += 2
                continue
            if ch in "+-*/=<>(),.;:&|'":
                tokens.append(Tok("SYM", ch, line))
                i += 1
                continue
            if ch.isdigit():
                j = i
                has_dot = False
                while j < n and (
                    cleaned[j].isdigit()
                    or cleaned[j] == "_"
                    or (cleaned[j] == "." and j + 1 < n and cleaned[j + 1] != ".")
                ):
                    if cleaned[j] == ".":
                        has_dot = True
                    j += 1
                num_s = cleaned[i:j].replace("_", "")
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
        i = 0
        n = len(tok_list)
        while i < n:
            t = tok_list[i]
            # Handle Ada attribute <Type>'IMAGE(x) -> STR$(x)
            if (
                t.kind == "ID"
                and i + 2 < n
                and tok_list[i + 1].val == "'"
                and tok_list[i + 2].kind == "ID"
                and tok_list[i + 2].val == "IMAGE"
            ):
                parts.append("STR$")
                i += 3
                continue
            if t.kind == "STR":
                escaped = t.val.replace('"', '""')
                parts.append(f'"{escaped}"')
            elif t.kind in ("INT", "FLOAT"):
                parts.append(str(t.val))
            elif t.kind == "ID":
                if t.val in ("REM", "MOD"):
                    parts.append(" MOD ")
                elif t.val in ("AND", "OR", "XOR", "NOT"):
                    if t.val in ("AND", "OR") and i + 1 < n and tok_list[i + 1].kind == "ID" and tok_list[i + 1].val in ("THEN", "ELSE"):
                        i += 1
                    parts.append(f" {t.val} ")
                else:
                    parts.append(t.val)
            elif t.kind == "SYM":
                if t.val == ".":
                    parts.append("::")
                elif t.val == "&":
                    parts.append(" + ")
                elif t.val in ("<=", ">=", "<>", "=", "<", ">", "+", "-", "*", "/"):
                    parts.append(f" {t.val} ")
                else:
                    parts.append(t.val)
            i += 1
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
                    # Do not stop on 'THEN' or 'ELSE' if preceded by 'AND' or 'OR' (short-circuit 'and then' / 'or else')
                    if t.val in ("THEN", "ELSE") and collected and collected[-1].kind == "ID" and collected[-1].val in ("AND", "OR"):
                        collected.append(self._nx())
                        continue
                    break
            if t.kind == "SYM" and t.val == "(":
                depth += 1
            elif t.kind == "SYM" and t.val == ")":
                if depth == 0 and ")" in stop_vals:
                    break
                depth = max(0, depth - 1)
            collected.append(self._nx())
        return collected

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        self._toks = self._lex(source_text)
        self._tpos = 0

        # Consume context clauses: with ..., use ..., pragma ...
        while self._pk().kind == "ID" and self._pk().val in ("WITH", "USE", "PRAGMA"):
            kw = self._nx().val
            if kw == "PRAGMA" and self._pk().val == "IDENT":
                self._nx()
                if self._match("SYM", "("):
                    if self._pk().kind in ("STR", "ID"):
                        self.ident = str(self._nx().val)
                    self._match("SYM", ")")
            while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ";"):
                self._nx()
            self._match("SYM", ";")

        # Main procedure <Name> is ... begin ... end [<Name>];
        if self._pk().kind == "ID" and self._pk().val in ("PROCEDURE", "PACKAGE"):
            self._nx()
            if self._pk().kind == "ID" and self._pk().val == "BODY":
                self._nx()
            if self._pk().kind == "ID":
                pname = self._nx().val
                if self.module_name == "MAIN":
                    self.module_name = pname[:16]
            if self._match("SYM", "("):
                self._collect_expr_tokens(stop_vals={")"})
                self._match("SYM", ")")
            self._match("ID", "IS")
            self._parse_declarative_part()
            if self._match("ID", "BEGIN"):
                self._parse_seq_of_stmts(stop_ids={"END", "EXCEPTION"})
            if self._match("ID", "EXCEPTION"):
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                    self._nx()
            self._match("ID", "END")
            if self._pk().kind == "ID":
                self._nx()
            self._match("SYM", ";")

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

    def _parse_ada_type_def(self):
        t = self._pk()
        if t.kind == "ID" and t.val == "RECORD":
            self._nx()
            fields = []
            while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                if self._match("SYM", ";"):
                    continue
                if self._pk().kind == "ID" and self._pk().val == "NULL":
                    self._nx()
                    self._match("SYM", ";")
                    continue
                fnames = []
                while self._pk().kind == "ID":
                    fnames.append(self._nx().val)
                    if not self._match("SYM", ","):
                        break
                if self._match("SYM", ":"):
                    tspec = self._parse_ada_type_def()
                    fvtype = tspec[1] if tspec[0] == "SCALAR" else "INT"
                    for fn in fnames:
                        fields.append((fn, fvtype))
                    if self._match("SYM", ":="):
                        self._collect_expr_tokens(stop_vals={";"})
                self._match("SYM", ";")
            self._match("ID", "END")
            self._match("ID", "RECORD")
            return ("RECORD", fields)

        if t.kind == "ID" and t.val == "ARRAY":
            self._nx()
            hi_val = 64
            if self._match("SYM", "("):
                b_toks = self._collect_expr_tokens(stop_vals={")"})
                self._match("SYM", ")")
                ints = [tk.val for tk in b_toks if tk.kind == "INT"]
                if ints:
                    hi_val = max(ints) + 2
            self._match("ID", "OF")
            _, elem_t = self._parse_ada_type_def()
            return ("ARRAY", hi_val, elem_t)

        if t.kind == "ID":
            tname = self._nx().val
            if self._match("SYM", "("):
                self._collect_expr_tokens(stop_vals={")"})
                self._match("SYM", ")")
            if self._pk().kind == "ID" and self._pk().val == "RANGE":
                self._nx()
                self._collect_expr_tokens(stop_vals={";", ":="})
            if tname in self.type_defs:
                return self.type_defs[tname]
            if tname in ("STRING", "CHARACTER"):
                return ("SCALAR", "STR")
            if tname in ("FLOAT", "LONG_FLOAT", "SHORT_FLOAT", "DURATION"):
                return ("SCALAR", "FLOAT")
            return ("SCALAR", "INT")

        self._collect_expr_tokens(stop_vals={";", ":="})
        return ("SCALAR", "INT")

    def _register_ada_var(self, vname, tspec):
        kind = tspec[0]
        if kind == "RECORD":
            rec_key = f"__ADA_REC_{vname}"
            self.record_defs[rec_key] = tspec[1]
            self.record_vars[vname] = rec_key
            for fn, ft in tspec[1]:
                self.get_var_id(f"{vname}.{fn}", ft)
        elif kind == "ARRAY":
            _, sz, elem_t = tspec
            vid = self.get_var_id(vname, elem_t)
            self.emit_push_int(sz)
            self.emit_u8(OP_DIM_ARR)
            self.emit_u16(vid)
        else:
            self.get_var_id(vname, tspec[1])

    def _parse_declarative_part(self):
        while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val in ("BEGIN", "END")):
            if self._match("SYM", ";"):
                continue
            t = self._pk()
            if t.kind == "ID" and t.val in ("USE", "PRAGMA"):
                self._nx()
                if t.val == "PRAGMA" and self._pk().val == "IDENT":
                    self._nx()
                    if self._match("SYM", "("):
                        if self._pk().kind in ("STR", "ID"):
                            self.ident = str(self._nx().val)
                        self._match("SYM", ")")
                while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ";"):
                    self._nx()
                self._match("SYM", ";")
                continue

            if t.kind == "ID" and t.val in ("TYPE", "SUBTYPE"):
                self._nx()
                tname = self._nx().val
                self._match("ID", "IS")
                tspec = self._parse_ada_type_def()
                self.type_defs[tname] = tspec
                if tspec[0] == "RECORD":
                    self.record_defs[tname] = tspec[1]
                self._match("SYM", ";")
                continue

            if t.kind == "ID" and t.val in ("PROCEDURE", "FUNCTION"):
                is_fn = t.val == "FUNCTION"
                self._nx()
                sub_name = self._nx().val
                params = []
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                        pnames = []
                        while self._pk().kind == "ID":
                            pnames.append(self._nx().val)
                            if not self._match("SYM", ","):
                                break
                        if self._match("SYM", ":"):
                            while self._pk().kind == "ID" and self._pk().val in ("IN", "OUT"):
                                self._nx()
                            ptspec = self._parse_ada_type_def()
                            pvtype = ptspec[1] if ptspec[0] == "SCALAR" else "INT"
                            for pn in pnames:
                                self.get_var_id(pn, pvtype)
                                params.append(pn)
                        self._match("SYM", ";")
                    self._match("SYM", ")")
                ret_vtype = "INT"
                if is_fn and self._match("ID", "RETURN"):
                    rtspec = self._parse_ada_type_def()
                    ret_vtype = rtspec[1] if rtspec[0] == "SCALAR" else "INT"
                if self._match("SYM", ";"):
                    # Forward subprogram specification
                    continue
                self._match("ID", "IS")
                if is_fn:
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
                end_lbl = f"__ENDSUB_{sub_name}"
                self.emit_jump(OP_JMP, end_lbl)
                self.labels[f"__FN_{sub_name}" if is_fn else f"__SUB_{sub_name}"] = len(self.bytecode)
                self.cur_fn_stack.append(sub_name if is_fn else None)
                self._parse_declarative_part()
                if self._match("ID", "BEGIN"):
                    self._parse_seq_of_stmts(stop_ids={"END", "EXCEPTION"})
                if self._match("ID", "EXCEPTION"):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                        self._nx()
                self._match("ID", "END")
                if self._pk().kind == "ID":
                    self._nx()
                self._match("SYM", ";")
                self.cur_fn_stack.pop()
                self.emit_u8(OP_RET)
                self.labels[end_lbl] = len(self.bytecode)
                continue

            # Variable or constant declaration: <v1>, <v2> : [constant] [<Type>] [:= <expr>];
            vnames = []
            while self._pk().kind == "ID":
                vnames.append(self._nx().val)
                if not self._match("SYM", ","):
                    break
            if self._match("SYM", ":"):
                is_const = bool(self._match("ID", "CONSTANT"))
                tspec = ("SCALAR", "INT")
                if not (self._pk().kind == "SYM" and self._pk().val == ":="):
                    tspec = self._parse_ada_type_def()
                for vn in vnames:
                    self._register_ada_var(vn, tspec)
                if self._match("SYM", ":="):
                    init_toks = self._collect_expr_tokens(stop_vals={";"})
                    if is_const and len(init_toks) == 1 and init_toks[0].kind in ("INT", "FLOAT", "STR"):
                        for vn in vnames:
                            self.constants[vn] = (init_toks[0].kind, init_toks[0].val)
                    else:
                        init_s = self._tokens_to_expr_str(init_toks)
                        for vn in vnames:
                            if any(tk.kind == "STR" for tk in init_toks):
                                self.get_var_id(vn, "STR")
                            self.compile_expr(init_s)
                            self.emit_store_var(vn)
                self._match("SYM", ";")
            else:
                self._nx()

    def _parse_seq_of_stmts(self, stop_ids):
        while self._pk().kind != "EOF":
            while self._match("SYM", ";"):
                pass
            t = self._pk()
            if t.kind == "EOF":
                break
            if t.kind == "ID" and t.val in stop_ids:
                break
            self._parse_stmt()

    def _parse_stmt(self):
        t = self._pk()
        if t.kind == "EOF":
            return
        if t.kind == "ID":
            kw = t.val
            if kw == "NULL":
                self._nx()
                self._match("SYM", ";")
                return

            if kw in ("PUT_LINE", "PUT"):
                self._nx()
                has_nl = 1 if kw == "PUT_LINE" else 0
                args = []
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                        a_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                        if a_toks:
                            args.append(self._tokens_to_expr_str(a_toks))
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ")")
                self._match("SYM", ";")
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

            if kw == "NEW_LINE":
                self._nx()
                if self._match("SYM", "("):
                    self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                self._match("SYM", ";")
                self.emit_str("")
                self.emit_u8(OP_PRINT_CH)
                self.emit_u8(0)
                self.emit_u8(1)
                return

            if kw in ("GET_LINE", "GET"):
                self._nx()
                if self._match("SYM", "("):
                    v_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                    vname = self._tokens_to_expr_str(v_toks).replace("::", ".")
                    if vname:
                        vid = self.get_var_id(vname)
                        self.emit_u8(OP_INPUT_S if self.is_str_var(vname) else OP_INPUT_I)
                        self.emit_u16(vid)
                    self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                self._match("SYM", ";")
                return

            if kw == "IF":
                self._nx()
                cond_toks = self._collect_expr_tokens(stop_ids={"THEN"})
                self._match("ID", "THEN")
                self.loop_counter += 1
                if_id = self.loop_counter
                br_idx = 1
                next_lbl = f"__ADA_IF_{if_id}_{br_idx}"
                end_lbl = f"__ADA_ENDIF_{if_id}"
                self.compile_expr(self._tokens_to_expr_str(cond_toks))
                self.emit_jump(OP_JMP_FALSE, next_lbl)
                self._parse_seq_of_stmts(stop_ids={"ELSIF", "ELSE", "END"})
                while self._pk().kind == "ID" and self._pk().val == "ELSIF":
                    self._nx()
                    self.emit_jump(OP_JMP, end_lbl)
                    self.labels[next_lbl] = len(self.bytecode)
                    br_idx += 1
                    next_lbl = f"__ADA_IF_{if_id}_{br_idx}"
                    e_cond = self._collect_expr_tokens(stop_ids={"THEN"})
                    self._match("ID", "THEN")
                    self.compile_expr(self._tokens_to_expr_str(e_cond))
                    self.emit_jump(OP_JMP_FALSE, next_lbl)
                    self._parse_seq_of_stmts(stop_ids={"ELSIF", "ELSE", "END"})
                if self._pk().kind == "ID" and self._pk().val == "ELSE":
                    self._nx()
                    self.emit_jump(OP_JMP, end_lbl)
                    self.labels[next_lbl] = len(self.bytecode)
                    next_lbl = None
                    self._parse_seq_of_stmts(stop_ids={"END"})
                if next_lbl:
                    self.labels[next_lbl] = len(self.bytecode)
                self.labels[end_lbl] = len(self.bytecode)
                self._match("ID", "END")
                self._match("ID", "IF")
                self._match("SYM", ";")
                return

            if kw == "CASE":
                self._nx()
                sel_toks = self._collect_expr_tokens(stop_ids={"IS"})
                self._match("ID", "IS")
                self.select_counter += 1
                sid = self.select_counter
                sel_var = f"__ADA_CASE_{sid}"
                if any(tk.kind == "STR" for tk in sel_toks):
                    self.get_var_id(sel_var, "STR")
                self.compile_expr(self._tokens_to_expr_str(sel_toks))
                self.emit_store_var(sel_var)
                end_lbl = f"__ADA_CASE_END_{sid}"
                c_idx = 0
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                    if self._match("ID", "WHEN"):
                        if self._pk().kind == "ID" and self._pk().val == "OTHERS":
                            self._nx()
                            self._match("SYM", "=>")
                            self._parse_seq_of_stmts(stop_ids={"WHEN", "END"})
                            continue
                        c_idx += 1
                        next_lbl = f"__ADA_CASE_{sid}_{c_idx}"
                        choices = []
                        while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == "=>"):
                            ch_toks = self._collect_expr_tokens(stop_vals={"|", "=>"})
                            if ch_toks:
                                choices.append(ch_toks)
                            if not self._match("SYM", "|"):
                                break
                        self._match("SYM", "=>")
                        for ch_i, ch_t in enumerate(choices):
                            dots_idx = next((idx for idx, tk in enumerate(ch_t) if tk.val == ".."), -1)
                            if dots_idx != -1:
                                lo_s = self._tokens_to_expr_str(ch_t[:dots_idx])
                                hi_s = self._tokens_to_expr_str(ch_t[dots_idx + 1:])
                                self.emit_load_var(sel_var)
                                self.compile_expr(lo_s)
                                self.emit_u8(OP_GE)
                                self.emit_load_var(sel_var)
                                self.compile_expr(hi_s)
                                self.emit_u8(OP_LE)
                                self.emit_u8(OP_AND)
                            else:
                                self.emit_load_var(sel_var)
                                self.compile_expr(self._tokens_to_expr_str(ch_t))
                                self.emit_u8(OP_EQ)
                            if ch_i > 0:
                                self.emit_u8(OP_OR)
                        self.emit_jump(OP_JMP_FALSE, next_lbl)
                        self._parse_seq_of_stmts(stop_ids={"WHEN", "END"})
                        self.emit_jump(OP_JMP, end_lbl)
                        self.labels[next_lbl] = len(self.bytecode)
                    else:
                        self._nx()
                self._match("ID", "END")
                self._match("ID", "CASE")
                self._match("SYM", ";")
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "FOR":
                self._nx()
                vname = self._nx().val
                self._match("ID", "IN")
                is_rev = bool(self._match("ID", "REVERSE"))
                rng_toks = self._collect_expr_tokens(stop_ids={"LOOP"})
                self._match("ID", "LOOP")
                dots_idx = next((idx for idx, tk in enumerate(rng_toks) if tk.val == ".."), -1)
                lo_s = self._tokens_to_expr_str(rng_toks[:dots_idx]) if dots_idx != -1 else "1"
                hi_s = self._tokens_to_expr_str(rng_toks[dots_idx + 1:]) if dots_idx != -1 else "1"
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__ADA_FTOP_{lid}"
                end_lbl = f"__ADA_FEND_{lid}"
                self.compile_expr(hi_s if is_rev else lo_s)
                self.emit_store_var(vname)
                self.labels[top_lbl] = len(self.bytecode)
                self.emit_load_var(vname)
                self.compile_expr(lo_s if is_rev else hi_s)
                self.emit_u8(OP_GE if is_rev else OP_LE)
                self.emit_jump(OP_JMP_FALSE, end_lbl)
                self.loop_exit_stack.append(end_lbl)
                self._parse_seq_of_stmts(stop_ids={"END"})
                self.loop_exit_stack.pop()
                self._match("ID", "END")
                self._match("ID", "LOOP")
                self._match("SYM", ";")
                self.emit_load_var(vname)
                self.emit_push_int(1)
                self.emit_u8(OP_SUB if is_rev else OP_ADD)
                self.emit_store_var(vname)
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "WHILE":
                self._nx()
                cond_toks = self._collect_expr_tokens(stop_ids={"LOOP"})
                self._match("ID", "LOOP")
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__ADA_WTOP_{lid}"
                end_lbl = f"__ADA_WEND_{lid}"
                self.labels[top_lbl] = len(self.bytecode)
                self.compile_expr(self._tokens_to_expr_str(cond_toks))
                self.emit_jump(OP_JMP_FALSE, end_lbl)
                self.loop_exit_stack.append(end_lbl)
                self._parse_seq_of_stmts(stop_ids={"END"})
                self.loop_exit_stack.pop()
                self._match("ID", "END")
                self._match("ID", "LOOP")
                self._match("SYM", ";")
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "LOOP":
                self._nx()
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__ADA_LTOP_{lid}"
                end_lbl = f"__ADA_LEND_{lid}"
                self.labels[top_lbl] = len(self.bytecode)
                self.loop_exit_stack.append(end_lbl)
                self._parse_seq_of_stmts(stop_ids={"END"})
                self.loop_exit_stack.pop()
                self._match("ID", "END")
                self._match("ID", "LOOP")
                self._match("SYM", ";")
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "EXIT":
                self._nx()
                end_lbl = self.loop_exit_stack[-1] if self.loop_exit_stack else None
                if self._match("ID", "WHEN"):
                    cond_toks = self._collect_expr_tokens(stop_vals={";"})
                    self._match("SYM", ";")
                    if end_lbl:
                        self.loop_counter += 1
                        skip_lbl = f"__ADA_NOEXIT_{self.loop_counter}"
                        self.compile_expr(self._tokens_to_expr_str(cond_toks))
                        self.emit_jump(OP_JMP_FALSE, skip_lbl)
                        self.emit_jump(OP_JMP, end_lbl)
                        self.labels[skip_lbl] = len(self.bytecode)
                else:
                    self._match("SYM", ";")
                    if end_lbl:
                        self.emit_jump(OP_JMP, end_lbl)
                return

            if kw == "RETURN":
                self._nx()
                if not (self._pk().kind == "SYM" and self._pk().val == ";"):
                    ret_toks = self._collect_expr_tokens(stop_vals={";"})
                    fn_name = self.cur_fn_stack[-1] if self.cur_fn_stack else None
                    if fn_name:
                        self.compile_expr(self._tokens_to_expr_str(ret_toks))
                        self.emit_store_var(fn_name)
                self._match("SYM", ";")
                self.emit_u8(OP_RET)
                return

            # Assignment or Procedure call
            lhs_toks = [self._nx()]
            while self._pk().val in (".", "("):
                if self._pk().val == ".":
                    lhs_toks.append(self._nx())
                    lhs_toks.append(self._nx())
                elif self._pk().val == "(":
                    if lhs_toks[0].val in self.sub_defs or self._pk(1).val == ")":
                        break
                    # Check if followed by := after matching ')'
                    save_p = self._tpos
                    paren_toks = [self._nx()]
                    paren_toks.extend(self._collect_expr_tokens(stop_vals={")"}))
                    if self._pk().val == ")":
                        paren_toks.append(self._nx())
                    if self._pk().val == ":=":
                        lhs_toks.extend(paren_toks)
                    else:
                        self._tpos = save_p
                        break

            if self._match("SYM", ":="):
                rhs_toks = self._collect_expr_tokens(stop_vals={";"})
                self._match("SYM", ";")
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
                        tk.kind == "ID" and (tk.val == "IMAGE" or self.is_str_var(tk.val)) for tk in rhs_toks
                    ):
                        self.get_var_id(lhs_s, "STR")
                    self.compile_expr(rhs_s)
                    self.emit_store_var(lhs_s)
                return

            # Procedure call
            proc_name = lhs_toks[-1].val
            args = []
            if self._match("SYM", "("):
                while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                    a_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                    if a_toks:
                        args.append(self._tokens_to_expr_str(a_toks))
                    if not self._match("SYM", ","):
                        break
                self._match("SYM", ")")
            self._match("SYM", ";")
            if proc_name in ("PUT_LINE", "PUT"):
                has_nl = 1 if proc_name == "PUT_LINE" else 0
                for idx_a, a_expr in enumerate(args):
                    is_last = idx_a == len(args) - 1
                    self.compile_expr(a_expr)
                    self.emit_u8(OP_PRINT_CH)
                    self.emit_u8(0)
                    self.emit_u8(has_nl if is_last else 0)
            elif proc_name in self.sub_defs:
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

        self._nx()

    def write_outputs(self, out_obj, out_lst=None):
        super().write_outputs(out_obj, out_lst=None)
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
        print("Usage: vaxada <source.ada> [-o out.OBJ] [-l [out.LST]] [/OBJECT=...] [/LIST[=...]]")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".ADA", ".ada", ".ADB", ".adb", ".ADS", ".ads"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%ADA-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXAdaCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX ADA {VAXAdaCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
