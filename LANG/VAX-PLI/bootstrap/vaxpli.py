#!/usr/bin/env python3
"""
DEC VAX PL/I V3.5 Compiler (vaxpli.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Compiles DEC VAX PL/I V3.5 source programs (.PLI) into OpenVMS relocatable
object modules (.OBJ) compatible with the OpenVMS Linker (vmslink) and image
activator (vms_vm), plus optional compiler listing files (.LST).
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
    OP_GE,
    OP_LE,
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


class VAXPLICompiler(VAXBasicCompiler):
    VERSION = "V3.5-00"
    CREATOR_NAME = "DEC VAX PL/I V3.5-00"

    def __init__(self, module_name="MAIN"):
        super().__init__(module_name=module_name)
        self.ident = "V03-05"
        self.line_offsets = {}
        self.cur_fn_stack = []

    def _strip_pli_comments(self, text):
        out = []
        i = 0
        n = len(text)
        in_str = None
        while i < n:
            ch = text[i]
            if in_str:
                out.append(ch)
                if ch == in_str:
                    if i + 1 < n and text[i + 1] == in_str:
                        out.append(in_str)
                        i += 2
                        continue
                    in_str = None
                i += 1
                continue
            if ch in ("'", '"'):
                in_str = ch
                out.append(ch)
                i += 1
                continue
            if ch == "/" and i + 1 < n and text[i + 1] == "*":
                i += 2
                while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
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
        cleaned = self._strip_pli_comments(text)
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
                s_val = "".join(buf)
                # Check '1'B or '0'B bit literal suffix
                if i < n and cleaned[i] in ("B", "b") and (i + 1 == n or not cleaned[i + 1].isalnum()):
                    i += 1
                    bit_v = 1 if "1" in s_val else 0
                    tokens.append(Tok("INT", bit_v, line))
                else:
                    tokens.append(Tok("STR", s_val, line))
                continue
            if cleaned[i:i + 2] in ("||", "<=", ">=", "<>", "^=", "~=", "!=", "¬="):
                op2 = cleaned[i:i + 2]
                if op2 in ("^=", "~=", "!=", "¬="):
                    op2 = "<>"
                tokens.append(Tok("SYM", op2, line))
                i += 2
                continue
            if ch in "+-*/=<>(),.;:&|^~¬":
                tokens.append(Tok("SYM", ch, line))
                i += 1
                continue
            if ch.isdigit():
                j = i
                has_dot = False
                while j < n and (cleaned[j].isdigit() or cleaned[j] == "."):
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
            if ch.isalpha() or ch in ("_", "$", "#"):
                j = i
                while j < n and (cleaned[j].isalnum() or cleaned[j] in ("_", "$", "#")):
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
            if t.kind == "STR":
                escaped = t.val.replace('"', '""')
                parts.append(f'"{escaped}"')
            elif t.kind in ("INT", "FLOAT"):
                parts.append(str(t.val))
            elif t.kind == "ID":
                if t.val == "MOD" and i + 1 < n and tok_list[i + 1].val == "(":
                    # MOD(a, b) -> (a MOD b)
                    i += 2
                    depth = 1
                    arg1 = []
                    arg2 = []
                    in_second = False
                    while i < n and depth > 0:
                        tk = tok_list[i]
                        if tk.kind == "SYM" and tk.val == "(":
                            depth += 1
                        elif tk.kind == "SYM" and tk.val == ")":
                            depth -= 1
                            if depth == 0:
                                break
                        elif tk.kind == "SYM" and tk.val == "," and depth == 1 and not in_second:
                            in_second = True
                            i += 1
                            continue
                        if in_second:
                            arg2.append(tk)
                        else:
                            arg1.append(tk)
                        i += 1
                    s1 = self._tokens_to_expr_str(arg1)
                    s2 = self._tokens_to_expr_str(arg2)
                    parts.append(f"(({s1}) MOD ({s2}))")
                elif t.val in ("SUBSTR", "MID"):
                    parts.append("MID$")
                elif t.val == "LENGTH":
                    parts.append("LEN")
                elif t.val == "INDEX":
                    parts.append("INSTR")
                elif t.val == "TRIM":
                    i += 1
                    continue
                else:
                    parts.append(t.val)
            elif t.kind == "SYM":
                if t.val == ".":
                    parts.append("::")
                elif t.val == "||":
                    parts.append(" + ")
                elif t.val == "&":
                    parts.append(" AND ")
                elif t.val == "|":
                    parts.append(" OR ")
                elif t.val in ("^", "~", "¬"):
                    parts.append(" NOT ")
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

        # Check top-level <label>: PROCEDURE OPTIONS(MAIN);
        if self._pk().kind == "ID" and self._pk(1).val == ":" and self._pk(2).val in ("PROCEDURE", "PROC"):
            pname = self._nx().val
            self._nx()  # :
            self._nx()  # PROCEDURE
            if self.module_name == "MAIN":
                self.module_name = pname[:16]
            while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ";"):
                self._nx()
            self._match("SYM", ";")

        while self._pk().kind != "EOF":
            if self._pk().kind == "ID" and self._pk().val == "END":
                self._nx()
                if self._pk().kind == "ID":
                    self._nx()
                self._match("SYM", ";")
                break
            self._parse_stmt()

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

    def _parse_dcl_item(self, parent_struct=None):
        # Optional structure level number (e.g. 1 EMP, 2 NAME CHAR(32) VAR)
        level = None
        if self._pk().kind == "INT":
            level = self._nx().val
        if self._pk().kind != "ID":
            return
        vnames = []
        if self._match("SYM", "("):
            while self._pk().kind == "ID":
                vnames.append(self._nx().val)
                if not self._match("SYM", ","):
                    break
            self._match("SYM", ")")
        else:
            vnames.append(self._nx().val)

        # Optional array bounds (n) or (lo:hi)
        arr_sz = None
        if self._match("SYM", "("):
            b_toks = self._collect_expr_tokens(stop_vals={")"})
            self._match("SYM", ")")
            ints = [tk.val for tk in b_toks if tk.kind == "INT"]
            if ints:
                arr_sz = max(ints) + 2

        vtype = "INT"
        init_toks = None
        while self._pk().kind != "EOF":
            t = self._pk()
            if t.kind == "SYM" and t.val in (",", ";"):
                break
            if t.kind == "ID":
                kw = self._nx().val
                if kw in ("CHARACTER", "CHAR"):
                    vtype = "STR"
                    if self._match("SYM", "("):
                        self._collect_expr_tokens(stop_vals={")"})
                        self._match("SYM", ")")
                elif kw in ("VARYING", "VAR"):
                    vtype = "STR"
                elif kw in ("FLOAT", "REAL", "DECIMAL", "DEC"):
                    if kw in ("FLOAT", "REAL"):
                        vtype = "FLOAT"
                    if self._match("SYM", "("):
                        p_toks = self._collect_expr_tokens(stop_vals={")"})
                        self._match("SYM", ")")
                        if any(tk.val == "," for tk in p_toks):
                            vtype = "FLOAT"
                elif kw in ("FIXED", "BINARY", "BIN", "BIT", "STATIC", "AUTOMATIC", "AUTO", "EXTERNAL", "ALIGNED", "UNALIGNED"):
                    if self._match("SYM", "("):
                        p_toks = self._collect_expr_tokens(stop_vals={")"})
                        self._match("SYM", ")")
                        if kw in ("FIXED",) and any(tk.val == "," for tk in p_toks):
                            vtype = "FLOAT"
                elif kw in ("INITIAL", "INIT"):
                    if self._match("SYM", "("):
                        init_toks = self._collect_expr_tokens(stop_vals={")"})
                        self._match("SYM", ")")
                else:
                    pass
            else:
                self._nx()

        is_struct_root = level == 1 and self._pk().val == "," and self._pk(1).kind == "INT" and self._pk(1).val > 1
        for vn in vnames:
            full_name = f"{parent_struct}.{vn}" if (parent_struct and level and level > 1) else vn
            if not is_struct_root:
                self.get_var_id(full_name, vtype)
                if arr_sz is not None:
                    self.emit_push_int(arr_sz)
                    self.emit_u8(OP_DIM_ARR)
                    self.emit_u16(self.get_var_id(full_name, vtype))
                if init_toks:
                    init_s = self._tokens_to_expr_str(init_toks)
                    self.compile_expr(init_s)
                    self.emit_store_var(full_name)

        if is_struct_root:
            root_name = vnames[0]
            while self._match("SYM", ","):
                if self._pk().kind == "INT" and self._pk().val > 1:
                    self._parse_dcl_item(parent_struct=root_name)
                else:
                    self._parse_dcl_item(parent_struct=None)
                    break

    def _parse_stmt(self):
        while self._match("SYM", ";"):
            pass
        t = self._pk()
        if t.kind == "EOF":
            return
        if t.kind == "ID" and t.val in ("END", "ELSE", "WHEN", "OTHERWISE"):
            return

        # Check label or nested PROCEDURE definition: <name>: PROCEDURE(...) [RETURNS(...)];
        if t.kind == "ID" and self._pk(1).val == ":":
            lbl_name = self._nx().val
            self._nx()  # :
            if self._pk().kind == "ID" and self._pk().val in ("PROCEDURE", "PROC"):
                self._nx()
                params = []
                if self._match("SYM", "("):
                    while self._pk().kind == "ID":
                        pn = self._nx().val
                        self.get_var_id(pn, "INT")
                        params.append(pn)
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ")")
                is_fn = False
                ret_vtype = "INT"
                while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ";"):
                    tk = self._nx()
                    if tk.kind == "ID" and tk.val == "RETURNS":
                        is_fn = True
                        if self._match("SYM", "("):
                            rtoks = self._collect_expr_tokens(stop_vals={")"})
                            self._match("SYM", ")")
                            if any(r.val in ("CHAR", "CHARACTER", "VARYING", "VAR") for r in rtoks):
                                ret_vtype = "STR"
                            elif any(r.val in ("FLOAT",) for r in rtoks):
                                ret_vtype = "FLOAT"
                self._match("SYM", ";")
                if is_fn:
                    self.get_var_id(lbl_name, ret_vtype)
                    self.fn_defs[lbl_name] = {
                        "label": f"__FN_{lbl_name}",
                        "ret_var": lbl_name,
                        "params": params,
                    }
                else:
                    self.sub_defs[lbl_name] = {
                        "label": f"__SUB_{lbl_name}",
                        "params": params,
                    }
                end_lbl = f"__ENDPROC_{lbl_name}"
                self.emit_jump(OP_JMP, end_lbl)
                self.labels[f"__FN_{lbl_name}" if is_fn else f"__SUB_{lbl_name}"] = len(self.bytecode)
                self.cur_fn_stack.append(lbl_name if is_fn else None)
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                    self._parse_stmt()
                self._match("ID", "END")
                if self._pk().kind == "ID":
                    self._nx()
                self._match("SYM", ";")
                self.cur_fn_stack.pop()
                self.emit_u8(OP_RET)
                self.labels[end_lbl] = len(self.bytecode)
                return

            self.labels[lbl_name] = len(self.bytecode)
            self._parse_stmt()
            return

        if t.kind == "ID":
            kw = t.val
            if kw in ("DECLARE", "DCL"):
                self._nx()
                while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ";"):
                    self._parse_dcl_item()
                    if not self._match("SYM", ","):
                        break
                self._match("SYM", ";")
                return

            if kw == "DO":
                self._nx()
                # Plain DO; ... END;
                if self._match("SYM", ";"):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                        self._parse_stmt()
                    self._match("ID", "END")
                    if self._pk().kind == "ID":
                        self._nx()
                    self._match("SYM", ";")
                    return

                # DO WHILE(...) or DO UNTIL(...)
                if self._pk().kind == "ID" and self._pk().val in ("WHILE", "UNTIL"):
                    mode = self._nx().val
                    self._match("SYM", "(")
                    cond_toks = self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                    self._match("SYM", ";")
                    self.loop_counter += 1
                    lid = self.loop_counter
                    top_lbl = f"__PLI_DW_TOP_{lid}"
                    end_lbl = f"__PLI_DW_END_{lid}"
                    if mode == "WHILE":
                        self.labels[top_lbl] = len(self.bytecode)
                        self.compile_expr(self._tokens_to_expr_str(cond_toks))
                        self.emit_jump(OP_JMP_FALSE, end_lbl)
                        while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                            self._parse_stmt()
                        self._match("ID", "END")
                        self._match("SYM", ";")
                        self.emit_jump(OP_JMP, top_lbl)
                        self.labels[end_lbl] = len(self.bytecode)
                    else:
                        self.labels[top_lbl] = len(self.bytecode)
                        while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                            self._parse_stmt()
                        self._match("ID", "END")
                        self._match("SYM", ";")
                        self.compile_expr(self._tokens_to_expr_str(cond_toks))
                        self.emit_jump(OP_JMP_FALSE, top_lbl)
                    return

                # DO <v> = <start> TO <end> [BY <step>]; ... END;
                vname = self._nx().val
                self._match("SYM", "=")
                start_toks = self._collect_expr_tokens(stop_ids={"TO"}, stop_vals={";"})
                self._match("ID", "TO")
                end_toks = self._collect_expr_tokens(stop_ids={"BY"}, stop_vals={";"})
                step_s = "1"
                if self._match("ID", "BY"):
                    step_toks = self._collect_expr_tokens(stop_vals={";"})
                    step_s = self._tokens_to_expr_str(step_toks)
                self._match("SYM", ";")
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__PLI_FOR_TOP_{lid}"
                end_lbl = f"__PLI_FOR_END_{lid}"
                self.compile_expr(self._tokens_to_expr_str(start_toks))
                self.emit_store_var(vname)
                self.labels[top_lbl] = len(self.bytecode)
                self.emit_load_var(vname)
                self.compile_expr(self._tokens_to_expr_str(end_toks))
                self.emit_u8(OP_GE if step_s.strip().startswith("-") else OP_LE)
                self.emit_jump(OP_JMP_FALSE, end_lbl)
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                    self._parse_stmt()
                self._match("ID", "END")
                self._match("SYM", ";")
                self.emit_load_var(vname)
                self.compile_expr(step_s)
                self.emit_u8(OP_ADD)
                self.emit_store_var(vname)
                self.emit_jump(OP_JMP, top_lbl)
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "IF":
                self._nx()
                cond_toks = self._collect_expr_tokens(stop_ids={"THEN"})
                self._match("ID", "THEN")
                self.loop_counter += 1
                if_id = self.loop_counter
                else_lbl = f"__PLI_ELSE_{if_id}"
                end_lbl = f"__PLI_ENDIF_{if_id}"
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

            if kw == "SELECT":
                self._nx()
                sel_var = None
                self.select_counter += 1
                sid = self.select_counter
                if self._match("SYM", "("):
                    sel_toks = self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                    sel_var = f"__PLI_SEL_{sid}"
                    if any(tk.kind == "STR" for tk in sel_toks) or any(
                        tk.kind == "ID" and self.is_str_var(tk.val) for tk in sel_toks
                    ):
                        self.get_var_id(sel_var, "STR")
                    self.compile_expr(self._tokens_to_expr_str(sel_toks))
                    self.emit_store_var(sel_var)
                self._match("SYM", ";")
                end_lbl = f"__PLI_SEL_END_{sid}"
                c_idx = 0
                while self._pk().kind != "EOF" and not (self._pk().kind == "ID" and self._pk().val == "END"):
                    if self._match("SYM", ";"):
                        continue
                    if self._pk().kind == "ID" and self._pk().val == "WHEN":
                        self._nx()
                        c_idx += 1
                        next_lbl = f"__PLI_SEL_{sid}_{c_idx}"
                        self._match("SYM", "(")
                        clauses = []
                        while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                            cl_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                            if cl_toks:
                                clauses.append(cl_toks)
                            if not self._match("SYM", ","):
                                break
                        self._match("SYM", ")")
                        for cl_i, cl in enumerate(clauses):
                            cl_s = self._tokens_to_expr_str(cl)
                            if sel_var:
                                self.emit_load_var(sel_var)
                                self.compile_expr(cl_s)
                                self.emit_u8(OP_EQ)
                            else:
                                self.compile_expr(cl_s)
                            if cl_i > 0:
                                self.emit_u8(OP_OR)
                        self.emit_jump(OP_JMP_FALSE, next_lbl)
                        self._parse_stmt()
                        self.emit_jump(OP_JMP, end_lbl)
                        self.labels[next_lbl] = len(self.bytecode)
                    elif self._pk().kind == "ID" and self._pk().val == "OTHERWISE":
                        self._nx()
                        self._parse_stmt()
                    else:
                        self._parse_stmt()
                self._match("ID", "END")
                self._match("SYM", ";")
                self.labels[end_lbl] = len(self.bytecode)
                return

            if kw == "PUT":
                self._nx()
                has_skip = False
                while self._pk().kind == "ID" and self._pk().val in ("SKIP", "LINE", "PAGE", "FILE"):
                    m_kw = self._nx().val
                    if m_kw == "SKIP":
                        has_skip = True
                    if self._match("SYM", "("):
                        self._collect_expr_tokens(stop_vals={")"})
                        self._match("SYM", ")")
                mode = "LIST"
                if self._pk().kind == "ID" and self._pk().val in ("LIST", "EDIT", "DATA"):
                    mode = self._nx().val
                args = []
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                        a_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                        if a_toks:
                            args.append(self._tokens_to_expr_str(a_toks))
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ")")
                if mode == "EDIT" and self._match("SYM", "("):
                    # Consume format specification list (A, F(8,2), X(2), etc.)
                    self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                self._match("SYM", ";")
                if not args:
                    self.emit_str("")
                    self.emit_u8(OP_PRINT_CH)
                    self.emit_u8(0)
                    self.emit_u8(1)
                else:
                    for idx, a_expr in enumerate(args):
                        is_last = idx == len(args) - 1
                        self.compile_expr(a_expr)
                        self.emit_u8(OP_PRINT_CH)
                        self.emit_u8(0)
                        self.emit_u8(1 if is_last else 0)
                return

            if kw == "GET":
                self._nx()
                while self._pk().kind == "ID" and self._pk().val in ("SKIP", "LIST", "EDIT", "FILE"):
                    self._nx()
                if self._match("SYM", "("):
                    while self._pk().kind != "EOF" and not (self._pk().kind == "SYM" and self._pk().val == ")"):
                        v_toks = self._collect_expr_tokens(stop_vals={",", ")"})
                        vname = self._tokens_to_expr_str(v_toks).replace("::", ".")
                        if vname:
                            vid = self.get_var_id(vname)
                            self.emit_u8(OP_INPUT_S if self.is_str_var(vname) else OP_INPUT_I)
                            self.emit_u16(vid)
                        if not self._match("SYM", ","):
                            break
                    self._match("SYM", ")")
                self._match("SYM", ";")
                return

            if kw == "CALL":
                self._nx()
                pname = self._nx().val
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
                if pname in self.sub_defs:
                    sub_info = self.sub_defs[pname]
                    for idx_a, a_expr in enumerate(args):
                        if idx_a < len(sub_info["params"]):
                            self.compile_expr(a_expr)
                            self.emit_store_var(sub_info["params"][idx_a])
                    self.emit_jump(OP_CALL, sub_info["label"])
                else:
                    self.emit_u8(OP_CALL_OVL)
                    rel_off = len(self.bytecode)
                    self.emit_u16(0)
                    self.relocations.append({"offset": rel_off, "type": "CALL_OVL", "target": pname})
                return

            if kw == "RETURN":
                self._nx()
                if self._match("SYM", "("):
                    ret_toks = self._collect_expr_tokens(stop_vals={")"})
                    self._match("SYM", ")")
                    fn_name = self.cur_fn_stack[-1] if self.cur_fn_stack else None
                    if fn_name:
                        self.compile_expr(self._tokens_to_expr_str(ret_toks))
                        self.emit_store_var(fn_name)
                self._match("SYM", ";")
                self.emit_u8(OP_RET)
                return

            if kw in ("GOTO", "GO"):
                self._nx()
                if kw == "GO":
                    self._match("ID", "TO")
                tgt = str(self._nx().val).upper()
                self._match("SYM", ";")
                self.emit_jump(OP_JMP, tgt)
                return

            if kw == "STOP":
                self._nx()
                self._match("SYM", ";")
                self.emit_u8(OP_HALT)
                return

            # Assignment: <lhs> = <rhs>;
            lhs_toks = [self._nx()]
            while self._pk().val in (".", "("):
                if self._pk().val == ".":
                    lhs_toks.append(self._nx())
                    lhs_toks.append(self._nx())
                elif self._pk().val == "(":
                    lhs_toks.append(self._nx())
                    lhs_toks.extend(self._collect_expr_tokens(stop_vals={")"}))
                    if self._pk().val == ")":
                        lhs_toks.append(self._nx())

            if self._match("SYM", "="):
                rhs_toks = self._collect_expr_tokens(stop_vals={";"})
                self._match("SYM", ";")
                rhs_s = self._tokens_to_expr_str(rhs_toks)
                lhs_s = self._tokens_to_expr_str(lhs_toks).replace("::", ".")
                m_arr = re.match(r"^([A-Za-z0-9_.$#]+)\s*\((.+)\)$", lhs_s)
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
                        vtype = self.var_types.get(vname, "FIXED BIN(31)")
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
        print("Usage: vaxpli <source.pli> [-o out.OBJ] [-l [out.LST]] [/OBJECT=...] [/LIST[=...]]")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".PLI", ".pli", ".PL1", ".pl1"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%PLI-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXPLICompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX PL/I {VAXPLICompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
