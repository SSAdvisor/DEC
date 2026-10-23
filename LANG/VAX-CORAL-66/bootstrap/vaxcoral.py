#!/usr/bin/env python3
"""
DEC VAX CORAL 66 V2.1 Compiler (vaxcoral.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Compiles DEC VAX CORAL 66 V2.1 real-time defense/industrial control programs
(.COR) — supporting both stropped ('BEGIN', 'INTEGER', 'END', 'FINISH') and
unstropped (BEGIN, INTEGER, END, FINISH) syntax — into OpenVMS relocatable
object modules (.OBJ) compatible with vmslink and vms_vm, plus optional .LST
compiler listings.
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
    OP_EQ,
    OP_LE,
    OP_JMP,
    OP_JMP_FALSE,
    OP_CALL,
    OP_RET,
    OP_CALL_OVL,
    OP_PRINT_CH,
    OP_DIM_ARR,
    OP_STORE_ARR,
)


CORAL_KEYWORDS = {
    "PROGRAM",
    "BEGIN",
    "END",
    "FINISH",
    "INTEGER",
    "FLOATING",
    "FIXED",
    "STRING",
    "BYTE",
    "ARRAY",
    "TABLE",
    "DEFINE",
    "COMMON",
    "LIBRARY",
    "EXTERNAL",
    "ABSOLUTE",
    "PROCEDURE",
    "RECURSIVE",
    "VALUE",
    "LOCATION",
    "IF",
    "THEN",
    "ELSE",
    "FOR",
    "STEP",
    "WHILE",
    "UNTIL",
    "TO",
    "DO",
    "GOTO",
    "GO",
    "SWITCH",
    "ANSWER",
    "RETURN",
    "COMMENT",
    "AND",
    "OR",
    "XOR",
    "NOT",
    "MOD",
    "DIV",
    "TRUE",
    "FALSE",
    "WRITE",
    "WRITE_TEXT",
    "WRITELN",
    "PRINT",
    "PRINT_VALUE",
    "NEWLINE",
}


class Tok:
    __slots__ = ("kind", "val", "line")

    def __init__(self, kind, val, line):
        self.kind = kind
        self.val = val
        self.line = line

    def __repr__(self):
        return f"Tok({self.kind}, {self.val!r}, L{self.line})"


class VAXCoral66Compiler(VAXBasicCompiler):
    VERSION = "V2.1-00"
    CREATOR_NAME = "DEC VAX CORAL 66 V2.1-00"

    def __init__(self, module_name="MAIN"):
        super().__init__(module_name=module_name)
        self.ident = "V02-01"
        self.constants["TRUE"] = ("INT", 1)
        self.constants["FALSE"] = ("INT", 0)
        self.switches = {}       # sw_name -> [lbl1, lbl2, ...]
        self.table_fields = {}   # field_name -> vtype
        self.line_offsets = {}
        self.cur_fn_stack = []

    def _lex(self, text):
        tokens = []
        i = 0
        n = len(text)
        line = 1
        while i < n:
            ch = text[i]
            if ch == "\n":
                line += 1
                i += 1
                continue
            if ch in (" ", "\t", "\r"):
                i += 1
                continue
            # % single-line comment
            if ch == "%":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            # /* ... */ comment
            if ch == "/" and i + 1 < n and text[i + 1] == "*":
                i += 2
                while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
                    if text[i] == "\n":
                        line += 1
                    i += 1
                if i + 1 < n:
                    i += 2
                continue
            # Double-quoted string literal
            if ch == '"':
                i += 1
                buf = []
                while i < n:
                    if text[i] == "\n":
                        line += 1
                    if text[i] == '"':
                        if i + 1 < n and text[i + 1] == '"':
                            buf.append('"')
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(text[i])
                    i += 1
                tokens.append(Tok("STR", "".join(buf), line))
                continue
            # Single-quoted stropped keyword ('BEGIN', 'INTEGER', 'COMMENT', etc.) or string literal
            if ch == "'":
                i += 1
                buf = []
                while i < n and text[i] != "'":
                    if text[i] == "\n":
                        line += 1
                    buf.append(text[i])
                    i += 1
                if i < n and text[i] == "'":
                    i += 1
                word = "".join(buf)
                word_up = word.strip().upper()
                if word_up == "COMMENT":
                    while i < n and text[i] != ";":
                        if text[i] == "\n":
                            line += 1
                        i += 1
                    if i < n and text[i] == ";":
                        i += 1
                    continue
                if word_up in CORAL_KEYWORDS:
                    tokens.append(Tok("ID", word_up, line))
                else:
                    tokens.append(Tok("STR", word, line))
                continue
            # Left arrow assignment ←
            if ch == "←":
                tokens.append(Tok("SYM", ":=", line))
                i += 1
                continue
            if text[i:i + 2] in (":=", "<=", ">=", "<>", "!="):
                op2 = text[i:i + 2]
                if op2 == "!=":
                    op2 = "<>"
                tokens.append(Tok("SYM", op2, line))
                i += 2
                continue
            if ch in "+-*/=<>(),.;:[]":
                tokens.append(Tok("SYM", ch, line))
                i += 1
                continue
            if ch.isdigit():
                j = i
                has_dot = False
                while j < n and (text[j].isdigit() or text[j] == "."):
                    if text[j] == ".":
                        has_dot = True
                    j += 1
                num_s = text[i:j]
                if has_dot:
                    tokens.append(Tok("FLOAT", float(num_s), line))
                else:
                    tokens.append(Tok("INT", int(num_s), line))
                i = j
                continue
            if ch.isalpha() or ch in ("_", "$"):
                j = i
                while j < n and (text[j].isalnum() or text[j] in ("_", "$")):
                    j += 1
                ident = text[i:j].upper()
                i = j
                if ident == "COMMENT":
                    while i < n and text[i] != ";":
                        if text[i] == "\n":
                            line += 1
                        i += 1
                    if i < n and text[i] == ";":
                        i += 1
                    continue
                tokens.append(Tok("ID", ident, line))
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
        for t in tok_list:
            if t.kind == "STR":
                escaped = t.val.replace('"', '""')
                parts.append(f'"{escaped}"')
            elif t.kind in ("INT", "FLOAT"):
                parts.append(str(t.val))
            elif t.kind == "ID":
                if t.val == "DIV":
                    parts.append(" / ")
                elif t.val in ("AND", "OR", "XOR", "NOT", "MOD"):
                    parts.append(f" {t.val} ")
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

        if self._pk().kind == "ID" and self._pk().val == "PROGRAM":
            self._nx()
            if self._pk().kind == "ID":
                pname = self._nx().val
                if self.module_name == "MAIN":
                    self.module_name = pname[:16]
            self._match("SYM", ";")

        while self._pk().kind != "EOF":
            if self._pk().kind == "ID" and self._pk().val == "FINISH":
                self._nx()
                self._match("SYM", ";")
                break
            self._parse_stmt()
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

    def _parse_decl_list(self, vtype):
        if self._pk().kind == "ID" and self._pk().val == "ARRAY":
            self._nx()
            while self._pk().kind == "ID":
                aname = self._nx().val
                hi_val = 64
                if self._match("SYM", "[") or self._match("SYM", "("):
                    b_toks = self._collect_expr_tokens(stop_vals={"]", ")"})
                    self._nx()
                    ints = [tk.val for tk in b_toks if tk.kind == "INT"]
                    if ints:
                        hi_val = max(ints) + 2
                vid = self.get_var_id(aname, vtype)
                self.emit_push_int(hi_val)
                self.emit_u8(OP_DIM_ARR)
                self.emit_u16(vid)
                if not self._match("SYM", ","):
                    break
            return

        while self._pk().kind == "ID":
            vname = self._nx().val
            if self._match("SYM", "[") or self._match("SYM", "("):
                b_toks = self._collect_expr_tokens(stop_vals={"]", ")"})
                self._nx()
                ints = [tk.val for tk in b_toks if tk.kind == "INT"]
                sz = (max(ints) + 2) if ints else 64
                vid = self.get_var_id(vname, vtype)
                self.emit_push_int(sz)
                self.emit_u8(OP_DIM_ARR)
                self.emit_u16(vid)
            else:
                self.get_var_id(vname, vtype)
                if self._match("SYM", ":=") or self._match("SYM", "="):
                    init_toks = self._collect_expr_tokens(stop_vals={",", ";"})
                    self.compile_expr(self._tokens_to_expr_str(init_toks))
                    self.emit_store_var(vname)
            if not self._match("SYM", ","):
                break

    def _parse_procedure(self, ret_vtype=None):
        self._match("ID", "PROCEDURE")
        if self._pk().kind == "ID" and self._pk().val == "RECURSIVE":
            self._nx()
        pname = self._nx().val
        params = []
        if self._match("SYM", "("):
            while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                pvtype = "INT"
                while self._pk().kind == "ID" and self._pk().val in (
                    "VALUE", "LOCATION", "INTEGER", "FLOATING", "FIXED", "STRING", "BYTE"
                ):
                    kw_p = self._nx().val
                    if kw_p == "STRING":
                        pvtype = "STR"
                    elif kw_p in ("FLOATING", "FIXED"):
                        pvtype = "FLOAT"
                    if kw_p == "FIXED" and self._match("SYM", "("):
                        self._collect_expr_tokens(stop_vals={")"})
                        self._match("SYM", ")")
                while self._pk().kind == "ID":
                    pn = self._nx().val
                    self.get_var_id(pn, pvtype)
                    params.append(pn)
                    if not self._match("SYM", ","):
                        break
                self._match("SYM", ";")
            self._match("SYM", ")")
        self._match("SYM", ";")
        is_fn = ret_vtype is not None
        if is_fn:
            self.get_var_id(pname, ret_vtype)
            self.fn_defs[pname] = {
                "label": f"__FN_{pname}",
                "ret_var": pname,
                "params": params,
            }
        else:
            self.sub_defs[pname] = {
                "label": f"__SUB_{pname}",
                "params": params,
            }
        end_lbl = f"__ENDPROC_{pname}"
        self.emit_jump(OP_JMP, end_lbl)
        self.labels[f"__FN_{pname}" if is_fn else f"__SUB_{pname}"] = len(self.bytecode)
        self.cur_fn_stack.append(pname if is_fn else None)
        self._parse_stmt()
        self.cur_fn_stack.pop()
        self.emit_u8(OP_RET)
        self.labels[end_lbl] = len(self.bytecode)

    def _parse_stmt(self):
        t = self._pk()
        if t.kind == "EOF" or (t.kind == "SYM" and t.val == ";"):
            return
        if t.kind == "ID" and t.val in ("END", "ELSE", "FINISH"):
            return

        # Statement label <id>:
        if t.kind == "ID" and self._pk(1).val == ":":
            lbl = self._nx().val
            self._nx()  # :
            self.labels[lbl] = len(self.bytecode)
            self._parse_stmt()
            return

        if t.kind == "ID":
            kw = t.val
            if kw == "BEGIN":
                self._nx()
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val in ("END", "FINISH")):
                    if self._match("SYM", ";"):
                        continue
                    self._parse_stmt()
                    self._match("SYM", ";")
                self._match("ID", "END")
                return

            if kw == "DEFINE":
                self._nx()
                while self._pk().kind == "ID":
                    cname = self._nx().val
                    self._match("SYM", "=")
                    etoks = self._collect_expr_tokens(stop_vals={",", ";"})
                    if len(etoks) == 1 and etoks[0].kind in ("INT", "FLOAT", "STR"):
                        self.constants[cname] = (etoks[0].kind, etoks[0].val)
                    else:
                        expr_s = self._tokens_to_expr_str(etoks)
                        self.compile_expr(expr_s)
                        self.emit_store_var(cname)
                    if not self._match("SYM", ","):
                        break
                return

            if kw == "COMMON":
                self._nx()
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                        self._parse_stmt()
                        self._match("SYM", ";")
                    self._match("SYM", ")")
                return

            if kw in ("INTEGER", "FLOATING", "FIXED", "STRING", "BYTE"):
                self._nx()
                vtype = "STR" if kw == "STRING" else ("FLOAT" if kw == "FLOATING" else "INT")
                if kw == "FIXED" and self._match("SYM", "("):
                    p_toks = self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                    ints = [tk.val for tk in p_toks if tk.kind == "INT"]
                    if len(ints) >= 2 and ints[1] > 0:
                        vtype = "FLOAT"
                if self._pk().kind == "ID" and self._pk().val == "PROCEDURE":
                    self._parse_procedure(ret_vtype=vtype)
                    return
                self._parse_decl_list(vtype)
                return

            if kw == "ARRAY":
                self._parse_decl_list("INT")
                return

            if kw == "TABLE":
                self._nx()
                tname = self._nx().val
                num_entries = 32
                if self._match("SYM", "[") or self._match("SYM", "("):
                    b_toks = self._collect_expr_tokens(stop_vals={"]", ")"})
                    self._nx()
                    ints = [tk.val for tk in b_toks if tk.kind == "INT"]
                    if ints:
                        num_entries = max(ints) + 2
                if self._match("SYM", "[") or self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val in ("]", ")")):
                        if self._match("SYM", ";") or self._match("SYM", ","):
                            continue
                        if self._pk().kind == "ID":
                            fname = self._nx().val
                            fvtype = "INT"
                            while self._pk().kind != "EOF" and not (
                                self._pk().kind == "SYM" and self._pk().val in (";", ",", "]", ")")
                            ):
                                tk = self._nx()
                                if tk.kind == "ID" and tk.val == "STRING":
                                    fvtype = "STR"
                                elif tk.kind == "ID" and tk.val == "FLOATING":
                                    fvtype = "FLOAT"
                            self.get_var_id(f"{tname}.{fname}", fvtype)
                            vid = self.get_var_id(fname, fvtype)
                            self.emit_push_int(num_entries)
                            self.emit_u8(OP_DIM_ARR)
                            self.emit_u16(vid)
                        else:
                            self._nx()
                    self._nx()
                return

            if kw == "PROCEDURE":
                self._parse_procedure(ret_vtype=None)
                return

            if kw == "SWITCH":
                self._nx()
                sw_name = self._nx().val
                self._match("SYM", ":=")
                lbls = []
                while self._pk().kind == "ID":
                    lbls.append(self._nx().val)
                    if not self._match("SYM", ","):
                        break
                self.switches[sw_name] = lbls
                return

            if kw in ("ANSWER", "RETURN"):
                self._nx()
                if not (self._pk().kind == "SYM" and self._pk().val == ";"):
                    ret_toks = self._collect_expr_tokens(stop_vals={";"}, stop_ids={"END", "ELSE"})
                    fn_name = self.cur_fn_stack[-1] if self.cur_fn_stack else None
                    if fn_name and ret_toks:
                        self.compile_expr(self._tokens_to_expr_str(ret_toks))
                        self.emit_store_var(fn_name)
                self.emit_u8(OP_RET)
                return

            if kw == "IF":
                self._nx()
                cond_toks = self._collect_expr_tokens(stop_ids={"THEN"})
                self._match("ID", "THEN")
                self.loop_counter += 1
                if_id = self.loop_counter
                else_lbl = f"__COR_ELSE_{if_id}"
                end_lbl = f"__COR_ENDIF_{if_id}"
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
                top_lbl = f"__COR_WTOP_{lid}"
                end_lbl = f"__COR_WEND_{lid}"
                self.labels[top_lbl] = len(self.bytecode)
                self.compile_expr(self._tokens_to_expr_str(cond_toks))
                self.emit_jump(OP_JMP_FALSE, end_lbl)
                self._parse_stmt()
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "FOR":
                self._nx()
                vname = self._nx().val
                if not self._match("SYM", ":="):
                    self._match("SYM", "=")
                start_toks = self._collect_expr_tokens(stop_ids={"STEP", "TO", "DO"})
                start_s = self._tokens_to_expr_str(start_toks)
                step_s = "1"
                mode = "WHILE"
                cond_s = "1"
                if self._match("ID", "STEP"):
                    step_toks = self._collect_expr_tokens(stop_ids={"WHILE", "UNTIL", "DO"})
                    step_s = self._tokens_to_expr_str(step_toks)
                    if self._pk().kind == "ID" and self._pk().val in ("WHILE", "UNTIL"):
                        mode = self._nx().val
                        cond_toks = self._collect_expr_tokens(stop_ids={"DO"})
                        cond_s = self._tokens_to_expr_str(cond_toks)
                elif self._match("ID", "TO"):
                    hi_toks = self._collect_expr_tokens(stop_ids={"DO"})
                    hi_s = self._tokens_to_expr_str(hi_toks)
                    mode = "TO"
                    cond_s = hi_s
                self._match("ID", "DO")

                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__COR_FTOP_{lid}"
                body_lbl = f"__COR_FBODY_{lid}"
                end_lbl = f"__COR_FEND_{lid}"
                self.compile_expr(start_s)
                self.emit_store_var(vname)
                self.labels[top_lbl] = len(self.bytecode)
                if mode == "WHILE":
                    self.compile_expr(cond_s)
                    self.emit_jump(OP_JMP_FALSE, end_lbl)
                elif mode == "UNTIL":
                    # In CORAL 66, STEP s UNTIL cond DO stmt executes while cond is FALSE (or until v > limit)
                    self.compile_expr(cond_s)
                    self.emit_jump(OP_JMP_FALSE, body_lbl)
                    self.emit_jump(OP_JMP, end_lbl)
                    self.labels[body_lbl] = len(self.bytecode)
                elif mode == "TO":
                    self.emit_load_var(vname)
                    self.compile_expr(cond_s)
                    self.emit_u8(OP_LE)
                    self.emit_jump(OP_JMP_FALSE, end_lbl)

                self._parse_stmt()
                self.emit_load_var(vname)
                self.compile_expr(step_s)
                self.emit_u8(OP_ADD)
                self.emit_store_var(vname)
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw in ("GOTO", "GO"):
                self._nx()
                if kw == "GO":
                    self._match("ID", "TO")
                tgt = self._nx().val
                if self._match("SYM", "[") or self._match("SYM", "("):
                    idx_toks = self._collect_expr_tokens(stop_vals={"]", ")"})
                    self._nx()
                    idx_s = self._tokens_to_expr_str(idx_toks)
                    for i_sw, sw_lbl in enumerate(self.switches.get(tgt, []), start=1):
                        self.loop_counter += 1
                        skip_lbl = f"__COR_SW_{self.loop_counter}"
                        self.compile_expr(idx_s)
                        self.emit_push_int(i_sw)
                        self.emit_u8(OP_EQ)
                        self.emit_jump(OP_JMP_FALSE, skip_lbl)
                        self.emit_jump(OP_JMP, sw_lbl)
                        self.labels[skip_lbl] = len(self.bytecode)
                else:
                    self.emit_jump(OP_JMP, tgt)
                return

            if kw == "NEWLINE":
                self._nx()
                if self._match("SYM", "("):
                    self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                self.emit_str("")
                self.emit_u8(OP_PRINT_CH)
                self.emit_u8(0)
                self.emit_u8(1)
                return

            if kw in ("WRITE", "WRITE_TEXT", "WRITELN", "PRINT", "PRINT_VALUE"):
                self._nx()
                has_nl = 1 if kw in ("WRITELN", "PRINT") else 0
                args = []
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                        a_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                        if a_toks:
                            args.append(self._tokens_to_expr_str(a_toks))
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ")")
                if not args:
                    self.emit_str("")
                    self.emit_u8(OP_PRINT_CH)
                    self.emit_u8(0)
                    self.emit_u8(has_nl)
                else:
                    for idx_a, a_expr in enumerate(args):
                        is_last = idx_a == len(args) - 1
                        self.compile_expr(a_expr)
                        self.emit_u8(OP_PRINT_CH)
                        self.emit_u8(0)
                        self.emit_u8(has_nl if is_last else 0)
                return

            # Assignment or Procedure call
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

            if self._match("SYM", ":=") or self._match("SYM", "="):
                rhs_toks = self._collect_expr_tokens(stop_vals={";"}, stop_ids={"END", "ELSE", "FINISH"})
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
                while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
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
            elif proc_name in self.fn_defs:
                fn_info = self.fn_defs[proc_name]
                for idx_a, a_expr in enumerate(args):
                    if idx_a < len(fn_info["params"]):
                        self.compile_expr(a_expr)
                        self.emit_store_var(fn_info["params"][idx_a])
                self.emit_jump(OP_CALL, fn_info["label"])
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
        print("Usage: vaxcoral <source.cor> [-o out.OBJ] [-l [out.LST]] [/OBJECT=...] [/LIST[=...]]")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".COR", ".cor", ".C66", ".c66"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%CORAL-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXCoral66Compiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX CORAL 66 {VAXCoral66Compiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
