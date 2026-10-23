#!/usr/bin/env python3
"""
DEC VAX C V3.2 Compiler (vaxc.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Compiles DEC VAX C source files (.C) into OpenVMS relocatable object modules
(.OBJ) compatible with vmslink and vms_vm, and generates optional compiler
listing files (.LST).
"""

import os
import re
import sys
import json
import struct
from datetime import datetime

# Bytecode Opcodes (vms_vm compatible)
OP_HALT = 0x00
OP_NOP = 0x01
OP_PUSH_INT = 0x10
OP_PUSH_FLOAT = 0x11
OP_PUSH_STR = 0x12
OP_STORE_VAR = 0x13
OP_LOAD_VAR = 0x14
OP_DIM_ARR = 0x15
OP_STORE_ARR = 0x16
OP_LOAD_ARR = 0x17
OP_PUSH_I32 = 0x18
OP_ADD = 0x20
OP_SUB = 0x21
OP_MUL = 0x22
OP_DIV = 0x23
OP_EQ = 0x24
OP_NEQ = 0x25
OP_LT = 0x26
OP_GT = 0x27
OP_AND = 0x28
OP_OR = 0x29
OP_LE = 0x2A
OP_GE = 0x2B
OP_NOT = 0x2C
OP_MOD = 0x2D
OP_XOR = 0x2E
OP_JMP = 0x30
OP_JMP_FALSE = 0x31
OP_CALL = 0x40
OP_RET = 0x41
OP_CALL_OVL = 0x42
OP_PRINT = 0x50
OP_PRINT_NO_NL = 0x51
OP_CHR = 0x73
OP_INT = 0x75
OP_LEN = 0x7C
OP_VAL = 0x81
OP_STR = 0x82

C_TYPE_KEYWORDS = {
    "INT", "LONG", "SHORT", "CHAR", "FLOAT", "DOUBLE", "VOID",
    "UNSIGNED", "SIGNED", "CONST", "VOLATILE", "STATIC", "EXTERN",
    "REGISTER", "AUTO", "GLOBALDEF", "GLOBALREF", "GLOBALVALUE",
    "READONLY", "NOSHARE", "TYPEDEF",
}


class VAXCCompiler:
    VERSION = "V3.2-044"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.ident = "V01-00"
        self.bytecode = bytearray()
        self.relocations = []
        self.var_map = {}
        self.var_types = {}
        self.macros = {
            "SS$_NORMAL": "1",
            "EXIT_SUCCESS": "0",
            "EXIT_FAILURE": "1",
            "NULL": "0",
            "TRUE": "1",
            "FALSE": "0",
        }
        self.struct_defs = {}      # tag_upper -> list of (field_name_upper, vtype)
        self.struct_vars = {}      # var_upper -> tag_upper
        self.ptr_targets = {}      # ptr_var_upper -> target_var_upper
        self.array_vars = set()
        self.functions = {}        # fn_upper -> {label, ret_var, params, is_defined}
        self.labels = {}
        self.fixups = []
        self.listing_lines = []
        self.id_counter = 0
        self.current_fn_ret_var = "__RET_MAIN"
        self.break_stack = []
        self.continue_stack = []

    def new_id(self):
        self.id_counter += 1
        return self.id_counter

    def get_var_id(self, name, vtype=None):
        u = name.strip().upper()
        if u not in self.var_map:
            idx = len(self.var_map)
            if idx >= 255:
                idx = 254
            self.var_map[u] = idx
            self.var_types[u] = vtype or "LONG"
        elif vtype:
            self.var_types[u] = vtype
        return self.var_map[u]

    def emit_u8(self, b):
        self.bytecode.append(b & 0xFF)

    def emit_u16(self, w):
        self.bytecode.extend(struct.pack("<H", w & 0xFFFF))

    def emit_i16(self, val):
        self.bytecode.extend(struct.pack("<h", int(val)))

    def emit_i32(self, val):
        self.bytecode.extend(struct.pack("<i", int(val)))

    def emit_f32(self, val):
        self.bytecode.extend(struct.pack("<f", float(val)))

    def emit_push_int(self, val):
        iv = int(val)
        if iv > 0x7FFFFFFF:
            iv -= 0x100000000
        if -32768 <= iv <= 32767:
            self.emit_u8(OP_PUSH_INT)
            self.emit_i16(iv)
        else:
            self.emit_u8(OP_PUSH_I32)
            self.emit_i32(iv)

    def emit_push_float(self, val):
        self.emit_u8(OP_PUSH_FLOAT)
        self.emit_f32(val)

    def emit_push_str(self, s):
        b = s.encode("utf-8", errors="replace")[:254]
        self.emit_u8(OP_PUSH_STR)
        self.emit_u8(len(b))
        self.bytecode.extend(b)

    def emit_load_var(self, name):
        self.emit_u8(OP_LOAD_VAR)
        self.emit_u16(self.get_var_id(name))

    def emit_store_var(self, name):
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(self.get_var_id(name))

    def emit_jump(self, op, target_label):
        self.emit_u8(op)
        fix_pos = len(self.bytecode)
        self.emit_u16(0)
        self.fixups.append((fix_pos, str(target_label).upper()))

    # --------------------------------------------------------------------------
    # Preprocessor & Lexer
    # --------------------------------------------------------------------------
    def preprocess(self, source_text):
        out_lines = []
        raw_lines = source_text.splitlines()
        skip_stack = []

        for raw in raw_lines:
            stripped = raw.strip()
            if stripped.startswith("#"):
                directive_body = stripped[1:].strip()
                parts = directive_body.split(None, 1)
                kw = parts[0].lower() if parts else ""
                rest = parts[1].strip() if len(parts) > 1 else ""
                # Strip /* ... */ or // comment from directive
                rest = re.sub(r"/\*.*?\*/", "", rest).split("//")[0].strip()

                if kw == "ifdef":
                    cond = rest.upper() in self.macros
                    skip_stack.append(not cond)
                    out_lines.append("")
                    continue
                if kw == "ifndef":
                    cond = rest.upper() not in self.macros
                    skip_stack.append(not cond)
                    out_lines.append("")
                    continue
                if kw == "else":
                    if skip_stack:
                        skip_stack[-1] = not skip_stack[-1]
                    out_lines.append("")
                    continue
                if kw == "endif":
                    if skip_stack:
                        skip_stack.pop()
                    out_lines.append("")
                    continue
                if any(skip_stack):
                    out_lines.append("")
                    continue

                if kw == "include":
                    out_lines.append("")
                    continue
                if kw == "module" or (kw == "pragma" and rest.lower().startswith("module")):
                    if kw == "pragma":
                        rest = rest[6:].strip()
                    m_mod = re.match(r'^([A-Za-z0-9_$]+)\s*(?:["\']([^"\']+)["\']|([A-Za-z0-9_$.-]+))?', rest)
                    if m_mod:
                        self.module_name = m_mod.group(1).upper()[:16]
                        ident_v = m_mod.group(2) or m_mod.group(3)
                        if ident_v:
                            self.ident = ident_v
                    out_lines.append("")
                    continue
                if kw == "define":
                    m_def = re.match(r"^([A-Za-z_][A-Za-z0-9_$]*)\s*(.*)$", rest)
                    if m_def:
                        mname = m_def.group(1)
                        mval = m_def.group(2).strip() or "1"
                        self.macros[mname] = mval
                    out_lines.append("")
                    continue
                out_lines.append("")
                continue

            if any(skip_stack):
                out_lines.append("")
                continue

            # Expand $DESCRIPTOR(name, "string") macro from <descrip.h>
            m_dsc = re.search(r"\$DESCRIPTOR\s*\(\s*([A-Za-z0-9_$]+)\s*,\s*(\"[^\"]*\")\s*\)", raw)
            if m_dsc:
                d_name, d_str = m_dsc.group(1), m_dsc.group(2)
                raw = f'char *{d_name} = {d_str};'

            out_lines.append(raw)

        return "\n".join(out_lines)

    def _decode_c_escapes(self, s):
        out = []
        i = 0
        while i < len(s):
            if s[i] == "\\" and i + 1 < len(s):
                nxt = s[i + 1]
                esc_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "0": ""}
                out.append(esc_map.get(nxt, nxt))
                i += 2
            else:
                out.append(s[i])
                i += 1
        return "".join(out)

    def tokenize(self, text):
        tokens = []
        i = 0
        n = len(text)
        line_no = 1
        while i < n:
            ch = text[i]
            if ch == "\n":
                line_no += 1
                i += 1
                continue
            if ch in (" ", "\t", "\r"):
                i += 1
                continue
            # Comments /* ... */ and //
            if text[i:i + 2] == "/*":
                i += 2
                while i < n and text[i:i + 2] != "*/":
                    if text[i] == "\n":
                        line_no += 1
                    i += 1
                i += 2
                continue
            if text[i:i + 2] == "//":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            # String literal
            if ch == '"':
                i += 1
                buf = []
                while i < n and text[i] != '"':
                    if text[i] == "\\" and i + 1 < n:
                        buf.append(text[i:i + 2])
                        i += 2
                        continue
                    if text[i] == "\n":
                        line_no += 1
                    buf.append(text[i])
                    i += 1
                i += 1
                tokens.append(("STR", self._decode_c_escapes("".join(buf)), line_no))
                continue
            # Char literal
            if ch == "'":
                i += 1
                buf = []
                while i < n and text[i] != "'":
                    if text[i] == "\\" and i + 1 < n:
                        buf.append(text[i:i + 2])
                        i += 2
                        continue
                    buf.append(text[i])
                    i += 1
                i += 1
                dec = self._decode_c_escapes("".join(buf))
                cval = ord(dec[0]) if dec else 0
                tokens.append(("INT", cval, line_no))
                continue
            # Multi-char operators
            if text[i:i + 2] in ("->", "++", "--", "+=", "-=", "*=", "/=", "%=", "==", "!=", "<=", ">=", "&&", "||", "<<", ">>", "&=", "|=", "^="):
                tokens.append(("SYM", text[i:i + 2], line_no))
                i += 2
                continue
            # Single-char punctuation/operators
            if ch in "+-*/%&|^~!=<>?:.,;()[]{}":
                tokens.append(("SYM", ch, line_no))
                i += 1
                continue
            # Numbers (hex 0x..., octal 0..., float, decimal)
            if ch.isdigit():
                if text[i:i + 2].lower() == "0x":
                    j = i + 2
                    while j < n and text[j] in "0123456789abcdefABCDEF":
                        j += 1
                    val = int(text[i + 2:j] or "0", 16)
                    while j < n and text[j].lower() in ("u", "l"):
                        j += 1
                    tokens.append(("INT", val, line_no))
                    i = j
                    continue
                j = i
                has_dot = False
                while j < n and (text[j].isdigit() or text[j] == "."):
                    if text[j] == ".":
                        has_dot = True
                    j += 1
                num_s = text[i:j]
                while j < n and text[j].lower() in ("u", "l", "f"):
                    j += 1
                if has_dot:
                    tokens.append(("FLOAT", float(num_s), line_no))
                elif num_s.startswith("0") and len(num_s) > 1 and all(c in "01234567" for c in num_s):
                    tokens.append(("INT", int(num_s, 8), line_no))
                else:
                    tokens.append(("INT", int(num_s), line_no))
                i = j
                continue
            # Identifiers & macro expansion
            if ch.isalpha() or ch in ("_", "$"):
                j = i
                while j < n and (text[j].isalnum() or text[j] in ("_", "$")):
                    j += 1
                ident = text[i:j]
                i = j
                if ident in self.macros:
                    m_toks = self.tokenize(self.macros[ident])
                    for mt, mv, _ in m_toks:
                        tokens.append((mt, mv, line_no))
                    continue
                if ident.upper() in self.macros:
                    m_toks = self.tokenize(self.macros[ident.upper()])
                    for mt, mv, _ in m_toks:
                        tokens.append((mt, mv, line_no))
                    continue
                tokens.append(("ID", ident.upper(), line_no))
                continue
            i += 1
        return tokens

    # --------------------------------------------------------------------------
    # Parser Helpers
    # --------------------------------------------------------------------------
    def _peek(self, offset=0):
        idx = self._pos + offset
        if idx < len(self._tokens):
            return self._tokens[idx]
        return ("EOF", None, 0)

    def _consume(self):
        t = self._peek()
        self._pos += 1
        return t

    def _match_id(self, *names):
        tt, tv, _ = self._peek()
        if tt == "ID" and tv in names:
            self._consume()
            return tv
        return None

    def _match_sym(self, *syms):
        tt, tv, _ = self._peek()
        if tt == "SYM" and tv in syms:
            self._consume()
            return tv
        return None

    def _is_type_start(self, offset=0):
        tt, tv, _ = self._peek(offset)
        if tt == "ID" and (tv in C_TYPE_KEYWORDS or tv == "STRUCT"):
            return True
        return False

    def _parse_type_spec(self):
        is_float = False
        is_char = False
        is_ptr = False
        struct_tag = None

        while self._peek()[0] != "EOF":
            tt, tv, _ = self._peek()
            if tt == "ID" and tv in C_TYPE_KEYWORDS:
                self._consume()
                if tv in ("FLOAT", "DOUBLE"):
                    is_float = True
                elif tv == "CHAR":
                    is_char = True
            elif tt == "ID" and tv == "STRUCT":
                self._consume()
                if self._peek()[0] == "ID":
                    struct_tag = self._consume()[1]
                if self._match_sym("{"):
                    fields = []
                    while self._peek()[0] != "EOF" and not self._match_sym("}"):
                        f_vtype, _ = self._parse_type_spec()
                        while self._peek()[0] != "EOF":
                            if self._match_sym("*"):
                                f_vtype = "STR" if f_vtype == "CHAR" else f_vtype
                            if self._peek()[0] == "ID":
                                fname = self._consume()[1]
                                if self._match_sym("["):
                                    while self._peek()[0] != "EOF" and not self._match_sym("]"):
                                        self._consume()
                                    if f_vtype == "CHAR":
                                        f_vtype = "STR"
                                fields.append((fname, "STR" if f_vtype == "CHAR" else f_vtype))
                            if not self._match_sym(","):
                                break
                        self._match_sym(";")
                    if struct_tag:
                        self.struct_defs[struct_tag] = fields
            elif tt == "SYM" and tv == "*":
                self._consume()
                is_ptr = True
            else:
                break

        if struct_tag:
            return ("STRUCT", struct_tag)
        if is_char and is_ptr:
            return ("STR", None)
        if is_float:
            return ("FLOAT", None)
        if is_char:
            return ("CHAR", None)
        return ("LONG", None)

    # --------------------------------------------------------------------------
    # Compilation Entry Point
    # --------------------------------------------------------------------------
    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        preprocessed = self.preprocess(source_text)
        self._tokens = self.tokenize(preprocessed)

        # Pass 1: Pre-scan top-level function definitions and prototypes
        self._prescan_functions()

        # Pass 2: Parse top-level declarations and functions
        self._pos = 0
        line_offsets = {}

        while self._peek()[0] != "EOF":
            lno = self._peek()[2]
            if lno and lno not in line_offsets:
                line_offsets[lno] = len(self.bytecode)
            if self._match_sym(";"):
                continue
            self._parse_top_level()

        # Call MAIN at end of startup initialization
        if "MAIN" in self.functions and self.functions["MAIN"]["is_defined"]:
            self.emit_jump(OP_CALL, self.functions["MAIN"]["label"])

        self.emit_u8(OP_HALT)

        # Resolve jump fixups
        for fix_pos, target_lbl in self.fixups:
            if target_lbl in self.labels:
                addr = self.labels[target_lbl]
                self.bytecode[fix_pos] = addr & 0xFF
                self.bytecode[fix_pos + 1] = (addr >> 8) & 0xFF

        cur_off = 0
        for idx_l, raw in enumerate(raw_lines, start=1):
            if idx_l in line_offsets:
                cur_off = line_offsets[idx_l]
            self.listing_lines.append((idx_l, cur_off, raw.rstrip("\r\n")))

    def _prescan_functions(self):
        idx = 0
        ntok = len(self._tokens)
        brace_depth = 0
        while idx < ntok:
            tt, tv, _ = self._tokens[idx]
            if tt == "SYM" and tv == "{":
                brace_depth += 1
                idx += 1
                continue
            if tt == "SYM" and tv == "}":
                brace_depth = max(0, brace_depth - 1)
                idx += 1
                continue
            if brace_depth == 0 and tt == "ID" and tv not in C_TYPE_KEYWORDS and tv != "STRUCT":
                if idx + 1 < ntok and self._tokens[idx + 1][:2] == ("SYM", "("):
                    fname = tv
                    p_idx = idx + 2
                    params = []
                    p_depth = 1
                    cur_param_ids = []
                    while p_idx < ntok and p_depth > 0:
                        pt, pv, _ = self._tokens[p_idx]
                        if pt == "SYM" and pv == "(":
                            p_depth += 1
                        elif pt == "SYM" and pv == ")":
                            p_depth -= 1
                            if p_depth == 0:
                                if cur_param_ids:
                                    params.append(cur_param_ids[-1])
                                break
                        elif pt == "SYM" and pv == "," and p_depth == 1:
                            if cur_param_ids:
                                params.append(cur_param_ids[-1])
                            cur_param_ids = []
                        elif pt == "ID" and pv not in C_TYPE_KEYWORDS and pv != "STRUCT":
                            cur_param_ids.append(pv)
                        p_idx += 1
                    after_p = p_idx + 1
                    is_def = (after_p < ntok and self._tokens[after_p][:2] == ("SYM", "{"))
                    for pn in params:
                        self.get_var_id(pn)
                    ret_var = f"__RET_{fname}"
                    self.get_var_id(ret_var)
                    if fname not in self.functions or is_def:
                        self.functions[fname] = {
                            "label": fname,
                            "ret_var": ret_var,
                            "params": params,
                            "is_defined": is_def or self.functions.get(fname, {}).get("is_defined", False),
                        }
                    idx = after_p
                    continue
            idx += 1

    def _parse_top_level(self):
        # Could start with type specifier or directly `main()`
        if self._is_type_start():
            vtype, struct_tag = self._parse_type_spec()
            if self._match_sym(";"):
                # Standalone `struct tag { ... };`
                return
        else:
            vtype, struct_tag = ("LONG", None)

        while self._match_sym("*"):
            if vtype == "CHAR":
                vtype = "STR"

        if self._peek()[0] != "ID":
            self._consume()
            return

        name = self._consume()[1]

        # Check if function declaration or definition: name(...)
        if self._match_sym("("):
            params = []
            while self._peek()[0] != "EOF" and not self._match_sym(")"):
                p_vtype, p_stag = self._parse_type_spec()
                while self._match_sym("*"):
                    if p_vtype == "CHAR":
                        p_vtype = "STR"
                if self._peek()[0] == "ID":
                    pname = self._consume()[1]
                    if self._match_sym("["):
                        while self._peek()[0] != "EOF" and not self._match_sym("]"):
                            self._consume()
                        if p_vtype == "CHAR":
                            p_vtype = "STR"
                    self.get_var_id(pname, p_vtype)
                    params.append(pname)
                self._match_sym(",")

            if self._match_sym(";"):
                # Prototype only
                return

            # Function body `{ ... }`
            end_fn_lbl = f"__END_FN_{name}"
            self.emit_jump(OP_JMP, end_fn_lbl)
            self.labels[name] = len(self.bytecode)

            prev_ret = self.current_fn_ret_var
            self.current_fn_ret_var = f"__RET_{name}"
            self.get_var_id(self.current_fn_ret_var, vtype if vtype in ("STR", "FLOAT") else "LONG")

            self._parse_stmt()

            self.emit_u8(OP_RET)
            self.labels[end_fn_lbl] = len(self.bytecode)
            self.current_fn_ret_var = prev_ret
            return

        # Global variable declaration (possibly comma-separated)
        self._parse_var_declarator_rest(name, vtype, struct_tag)
        while self._match_sym(","):
            cur_vt = vtype
            while self._match_sym("*"):
                if cur_vt == "CHAR":
                    cur_vt = "STR"
            if self._peek()[0] == "ID":
                next_name = self._consume()[1]
                self._parse_var_declarator_rest(next_name, cur_vt, struct_tag)
        self._match_sym(";")

    def _parse_var_declarator_rest(self, vname, vtype, struct_tag):
        # Array declaration: vname[size]
        if self._match_sym("["):
            arr_sz = 64
            if not self._match_sym("]"):
                if self._peek()[0] == "INT":
                    arr_sz = self._consume()[1]
                while self._peek()[0] != "EOF" and not self._match_sym("]"):
                    self._consume()
            if vtype == "CHAR":
                # char buf[N] -> string variable
                self.get_var_id(vname, "STR")
                if self._match_sym("="):
                    self._parse_expr()
                    self.emit_store_var(vname)
                else:
                    self.emit_push_str("")
                    self.emit_store_var(vname)
                return

            self.array_vars.add(vname)
            self.emit_push_int(max(1, arr_sz))
            self.emit_u8(OP_DIM_ARR)
            self.emit_u16(self.get_var_id(vname, "ARRAY"))
            if self._match_sym("="):
                if self._match_sym("{"):
                    idx_e = 0
                    while self._peek()[0] != "EOF" and not self._match_sym("}"):
                        self._parse_assignment_expr()
                        self.emit_push_int(idx_e)
                        self.emit_u8(OP_STORE_ARR)
                        self.emit_u16(self.get_var_id(vname))
                        idx_e += 1
                        self._match_sym(",")
            return

        # Struct variable or pointer to struct
        if vtype == "STRUCT" and struct_tag:
            self.struct_vars[vname] = struct_tag
            fields = self.struct_defs.get(struct_tag, [])
            for fname, fvt in fields:
                self.get_var_id(f"{vname}.{fname}", fvt)
            if self._match_sym("="):
                if self._match_sym("{"):
                    f_idx = 0
                    while self._peek()[0] != "EOF" and not self._match_sym("}"):
                        self._parse_assignment_expr()
                        if f_idx < len(fields):
                            fname, _ = fields[f_idx]
                            self.emit_store_var(f"{vname}.{fname}")
                        else:
                            self.emit_store_var("__DUMMY")
                        f_idx += 1
                        self._match_sym(",")
                elif self._match_sym("&"):
                    if self._peek()[0] == "ID":
                        tgt_struct = self._consume()[1]
                        self.ptr_targets[vname] = tgt_struct
                else:
                    self._parse_assignment_expr()
                    self.emit_store_var(vname)
            return

        # Scalar variable
        actual_vt = "STR" if vtype == "STR" else ("FLOAT" if vtype == "FLOAT" else "LONG")
        self.get_var_id(vname, actual_vt)
        if self._match_sym("="):
            if self._peek()[:2] == ("SYM", "&") and self._peek(1)[0] == "ID":
                self._consume()  # '&'
                tgt = self._consume()[1]
                self.ptr_targets[vname] = tgt
                self.emit_load_var(tgt)
                self.emit_store_var(vname)
            else:
                self._parse_assignment_expr()
                self.emit_store_var(vname)
        else:
            if actual_vt == "STR":
                self.emit_push_str("")
            elif actual_vt == "FLOAT":
                self.emit_push_float(0.0)
            else:
                self.emit_push_int(0)
            self.emit_store_var(vname)

    # --------------------------------------------------------------------------
    # Statement Parser
    # --------------------------------------------------------------------------
    def _parse_stmt(self):
        tt, tv, _ = self._peek()
        if tt == "EOF":
            return

        if self._match_sym(";"):
            return

        # Block `{ ... }`
        if self._match_sym("{"):
            while self._peek()[0] != "EOF" and not self._match_sym("}"):
                self._parse_stmt()
            return

        # Local variable declaration
        if self._is_type_start():
            vtype, struct_tag = self._parse_type_spec()
            if self._match_sym(";"):
                return
            while True:
                cur_vt = vtype
                while self._match_sym("*"):
                    if cur_vt == "CHAR":
                        cur_vt = "STR"
                if self._peek()[0] == "ID":
                    vname = self._consume()[1]
                    self._parse_var_declarator_rest(vname, cur_vt, struct_tag)
                if not self._match_sym(","):
                    break
            self._match_sym(";")
            return

        # if (...) ... [else ...]
        if self._match_id("IF"):
            if_id = self.new_id()
            else_lbl = f"__CIF_ELSE_{if_id}"
            end_lbl = f"__CIF_END_{if_id}"
            self._match_sym("(")
            self._parse_expr()
            self._match_sym(")")
            self.emit_jump(OP_JMP_FALSE, else_lbl)
            self._parse_stmt()
            if self._match_id("ELSE"):
                self.emit_jump(OP_JMP, end_lbl)
                self.labels[else_lbl] = len(self.bytecode)
                self._parse_stmt()
                self.labels[end_lbl] = len(self.bytecode)
            else:
                self.labels[else_lbl] = len(self.bytecode)
            return

        # while (...) ...
        if self._match_id("WHILE"):
            lid = self.new_id()
            top_lbl = f"__CWHILE_TOP_{lid}"
            end_lbl = f"__CWHILE_END_{lid}"
            self.labels[top_lbl] = len(self.bytecode)
            self._match_sym("(")
            self._parse_expr()
            self._match_sym(")")
            self.emit_jump(OP_JMP_FALSE, end_lbl)
            self.break_stack.append(end_lbl)
            self.continue_stack.append(top_lbl)
            self._parse_stmt()
            self.break_stack.pop()
            self.continue_stack.pop()
            self.emit_jump(OP_JMP, top_lbl)
            self.labels[end_lbl] = len(self.bytecode)
            return

        # do ... while (...);
        if self._match_id("DO"):
            lid = self.new_id()
            top_lbl = f"__CDO_TOP_{lid}"
            cond_lbl = f"__CDO_COND_{lid}"
            end_lbl = f"__CDO_END_{lid}"
            self.labels[top_lbl] = len(self.bytecode)
            self.break_stack.append(end_lbl)
            self.continue_stack.append(cond_lbl)
            self._parse_stmt()
            self.break_stack.pop()
            self.continue_stack.pop()
            self.labels[cond_lbl] = len(self.bytecode)
            self._match_id("WHILE")
            self._match_sym("(")
            self._parse_expr()
            self._match_sym(")")
            self._match_sym(";")
            self.emit_jump(OP_JMP_FALSE, end_lbl)
            self.emit_jump(OP_JMP, top_lbl)
            self.labels[end_lbl] = len(self.bytecode)
            return

        # for (init; cond; step) ...
        if self._match_id("FOR"):
            lid = self.new_id()
            top_lbl = f"__CFOR_TOP_{lid}"
            step_lbl = f"__CFOR_STEP_{lid}"
            end_lbl = f"__CFOR_END_{lid}"
            self._match_sym("(")
            # 1. init
            if not self._match_sym(";"):
                if self._is_type_start():
                    vtype, struct_tag = self._parse_type_spec()
                    while True:
                        cur_vt = vtype
                        while self._match_sym("*"):
                            if cur_vt == "CHAR":
                                cur_vt = "STR"
                        if self._peek()[0] == "ID":
                            vname = self._consume()[1]
                            self._parse_var_declarator_rest(vname, cur_vt, struct_tag)
                        if not self._match_sym(","):
                            break
                else:
                    self._parse_expr(discard_result=True)
                self._match_sym(";")
            # 2. cond
            self.labels[top_lbl] = len(self.bytecode)
            if not self._match_sym(";"):
                self._parse_expr()
                self.emit_jump(OP_JMP_FALSE, end_lbl)
                self._match_sym(";")
            # 3. step (save tokens to emit after body)
            step_start = self._pos
            p_depth = 1
            while self._peek()[0] != "EOF" and p_depth > 0:
                ct, cv, _ = self._consume()
                if ct == "SYM" and cv == "(":
                    p_depth += 1
                elif ct == "SYM" and cv == ")":
                    p_depth -= 1
            step_end = self._pos - 1

            self.break_stack.append(end_lbl)
            self.continue_stack.append(step_lbl)
            self._parse_stmt()
            self.break_stack.pop()
            self.continue_stack.pop()

            self.labels[step_lbl] = len(self.bytecode)
            after_body_pos = self._pos
            if step_start < step_end:
                self._pos = step_start
                self._parse_expr(discard_result=True)
            self._pos = after_body_pos
            self.emit_jump(OP_JMP, top_lbl)
            self.labels[end_lbl] = len(self.bytecode)
            return

        # switch (expr) { case ...: default: }
        if self._match_id("SWITCH"):
            self._parse_switch()
            return

        if self._match_id("BREAK"):
            self._match_sym(";")
            if self.break_stack:
                self.emit_jump(OP_JMP, self.break_stack[-1])
            return

        if self._match_id("CONTINUE"):
            self._match_sym(";")
            if self.continue_stack:
                self.emit_jump(OP_JMP, self.continue_stack[-1])
            return

        if self._match_id("RETURN"):
            if not self._match_sym(";"):
                self._parse_expr()
                self.emit_store_var(self.current_fn_ret_var)
                self._match_sym(";")
            self.emit_u8(OP_RET)
            return

        # Expression statement
        self._parse_expr(discard_result=True)
        self._match_sym(";")

    def _parse_switch(self):
        sid = self.new_id()
        sw_var = f"__CSW_VAL_{sid}"
        end_lbl = f"__CSW_END_{sid}"
        self._match_sym("(")
        self._parse_expr()
        self._match_sym(")")
        self.emit_store_var(sw_var)
        self._match_sym("{")

        self.break_stack.append(end_lbl)
        arm_idx = 0
        while self._peek()[0] != "EOF" and not self._match_sym("}"):
            if self._match_id("CASE"):
                arm_idx += 1
                next_arm_lbl = f"__CSW_{sid}_ARM_{arm_idx}"
                # Support stacked `case V1: case V2:`
                case_count = 0
                while True:
                    self.emit_load_var(sw_var)
                    self._parse_expr()
                    self.emit_u8(OP_EQ)
                    case_count += 1
                    if case_count > 1:
                        self.emit_u8(OP_OR)
                    self._match_sym(":")
                    if not self._match_id("CASE"):
                        break
                self.emit_jump(OP_JMP_FALSE, next_arm_lbl)
                while self._peek()[0] != "EOF" and not (self._peek()[0] == "ID" and self._peek()[1] in ("CASE", "DEFAULT")) and not (self._peek()[:2] == ("SYM", "}")):
                    self._parse_stmt()
                self.labels[next_arm_lbl] = len(self.bytecode)
            elif self._match_id("DEFAULT"):
                self._match_sym(":")
                while self._peek()[0] != "EOF" and not (self._peek()[0] == "ID" and self._peek()[1] in ("CASE", "DEFAULT")) and not (self._peek()[:2] == ("SYM", "}")):
                    self._parse_stmt()
            else:
                self._parse_stmt()

        self.break_stack.pop()
        self.labels[end_lbl] = len(self.bytecode)

    # --------------------------------------------------------------------------
    # Expression Parser (with C assignment, ++, --, +=, -=, *=, /=, struct ., ->)
    # --------------------------------------------------------------------------
    def _resolve_lvalue_name(self):
        """
        Parses an identifier with optional `.field` or `->field` chain and returns
        (resolved_var_name, is_array, idx_token_range).
        """
        base = self._consume()[1]
        while self._peek()[0] == "SYM" and self._peek()[1] in (".", "->"):
            op = self._consume()[1]
            if self._peek()[0] == "ID":
                fld = self._consume()[1]
                real_base = self.ptr_targets.get(base, base)
                base = f"{real_base}.{fld}"
        if self._peek()[:2] == ("SYM", "["):
            self._consume()  # '['
            idx_start = self._pos
            depth = 1
            while self._peek()[0] != "EOF" and depth > 0:
                ct, cv, _ = self._consume()
                if ct == "SYM" and cv == "[":
                    depth += 1
                elif ct == "SYM" and cv == "]":
                    depth -= 1
            idx_end = self._pos - 1
            return (base, True, (idx_start, idx_end))
        return (base, False, None)

    def _parse_expr(self, discard_result=False):
        self._parse_assignment_expr(discard_result=discard_result)
        while self._match_sym(","):
            self._parse_assignment_expr(discard_result=discard_result)

    def _parse_assignment_expr(self, discard_result=False):
        # Check if starts with lvalue followed by =, +=, -=, *=, /=, %=
        saved_pos = self._pos
        if self._peek()[0] == "ID" and self._peek(1)[:2] != ("SYM", "("):
            vname, is_arr, idx_range = self._resolve_lvalue_name()
            tt, tv, _ = self._peek()
            if tt == "SYM" and tv in ("=", "+=", "-=", "*=", "/=", "%=", "|=", "^="):
                self._consume()  # assignment op
                if is_arr:
                    idx_s, idx_e = idx_range
                    if tv == "=":
                        self._parse_assignment_expr()
                    else:
                        # Load current arr[idx]
                        after_op_pos = self._pos
                        self._pos = idx_s
                        self._parse_expr()
                        self._pos = after_op_pos
                        self.emit_u8(OP_LOAD_ARR)
                        self.emit_u16(self.get_var_id(vname))
                        self._parse_assignment_expr()
                        self._emit_compound_op(tv)
                    # Store into arr[idx]
                    after_rhs = self._pos
                    self._pos = idx_s
                    self._parse_expr()
                    self._pos = after_rhs
                    self.emit_u8(OP_STORE_ARR)
                    self.emit_u16(self.get_var_id(vname))
                    if not discard_result:
                        self._pos = idx_s
                        self._parse_expr()
                        self._pos = after_rhs
                        self.emit_u8(OP_LOAD_ARR)
                        self.emit_u16(self.get_var_id(vname))
                    return
                else:
                    if tv == "=" and self._peek()[:2] == ("SYM", "&") and self._peek(1)[0] == "ID":
                        self._consume()  # '&'
                        tgt = self._consume()[1]
                        self.ptr_targets[vname] = tgt
                        self.emit_load_var(tgt)
                        self.emit_store_var(vname)
                    elif tv == "=":
                        self._parse_assignment_expr()
                        self.emit_store_var(vname)
                    else:
                        self.emit_load_var(vname)
                        self._parse_assignment_expr()
                        self._emit_compound_op(tv)
                        self.emit_store_var(vname)
                    if not discard_result:
                        self.emit_load_var(vname)
                    return
        self._pos = saved_pos

        # Check standalone void function call when discard_result=True
        if discard_result and self._peek()[0] == "ID" and self._peek(1)[:2] == ("SYM", "("):
            fname = self._consume()[1]
            self._emit_function_call(fname, push_result=False)
            return

        self._parse_ternary()
        if discard_result:
            self.emit_store_var("__DISCARD")

    def _emit_compound_op(self, tv):
        if tv == "+=":
            self.emit_u8(OP_ADD)
        elif tv == "-=":
            self.emit_u8(OP_SUB)
        elif tv == "*=":
            self.emit_u8(OP_MUL)
        elif tv == "/=":
            self.emit_u8(OP_DIV)
            self.emit_u8(OP_INT)
        elif tv == "%=":
            self.emit_u8(OP_MOD)
        elif tv == "|=":
            self.emit_u8(OP_OR)
        elif tv == "^=":
            self.emit_u8(OP_XOR)

    def _parse_ternary(self):
        self._parse_logical_or()
        if self._match_sym("?"):
            tid = self.new_id()
            false_lbl = f"__CTERN_F_{tid}"
            end_lbl = f"__CTERN_E_{tid}"
            self.emit_jump(OP_JMP_FALSE, false_lbl)
            self._parse_expr()
            self.emit_jump(OP_JMP, end_lbl)
            self.labels[false_lbl] = len(self.bytecode)
            self._match_sym(":")
            self._parse_ternary()
            self.labels[end_lbl] = len(self.bytecode)

    def _parse_logical_or(self):
        self._parse_logical_and()
        while self._match_sym("||", "|", "^"):
            op = self._tokens[self._pos - 1][1]
            self._parse_logical_and()
            self.emit_u8(OP_XOR if op == "^" else OP_OR)

    def _parse_logical_and(self):
        self._parse_equality()
        while self._match_sym("&&", "&"):
            self._parse_equality()
            self.emit_u8(OP_AND)

    def _parse_equality(self):
        self._parse_relational()
        while self._peek()[0] == "SYM" and self._peek()[1] in ("==", "!="):
            op = self._consume()[1]
            self._parse_relational()
            self.emit_u8(OP_EQ if op == "==" else OP_NEQ)

    def _parse_relational(self):
        self._parse_additive()
        rel_map = {"<": OP_LT, "<=": OP_LE, ">": OP_GT, ">=": OP_GE}
        while self._peek()[0] == "SYM" and self._peek()[1] in rel_map:
            op = self._consume()[1]
            self._parse_additive()
            self.emit_u8(rel_map[op])

    def _parse_additive(self):
        self._parse_multiplicative()
        while self._peek()[0] == "SYM" and self._peek()[1] in ("+", "-"):
            op = self._consume()[1]
            self._parse_multiplicative()
            self.emit_u8(OP_ADD if op == "+" else OP_SUB)

    def _parse_multiplicative(self):
        self._parse_unary()
        while self._peek()[0] == "SYM" and self._peek()[1] in ("*", "/", "%"):
            op = self._consume()[1]
            self._parse_unary()
            if op == "*":
                self.emit_u8(OP_MUL)
            elif op == "/":
                self.emit_u8(OP_DIV)
                if self._last_was_int:
                    self.emit_u8(OP_INT)
            else:
                self.emit_u8(OP_MOD)

    def _parse_unary(self):
        self._last_was_int = True
        # Pre-increment / pre-decrement: ++x, --x
        if self._peek()[0] == "SYM" and self._peek()[1] in ("++", "--"):
            op = self._consume()[1]
            if self._peek()[0] == "ID":
                vname, is_arr, _ = self._resolve_lvalue_name()
                self.emit_load_var(vname)
                self.emit_push_int(1)
                self.emit_u8(OP_ADD if op == "++" else OP_SUB)
                self.emit_store_var(vname)
                self.emit_load_var(vname)
                return
        if self._match_sym("-"):
            self.emit_push_int(0)
            self._parse_unary()
            self.emit_u8(OP_SUB)
            return
        if self._match_sym("+"):
            self._parse_unary()
            return
        if self._match_sym("!"):
            self._parse_unary()
            self.emit_u8(OP_NOT)
            return
        # Address-of `&x` or dereference `*p`
        if self._match_sym("&", "*"):
            self._parse_unary()
            return
        if self._match_id("SIZEOF"):
            self._match_sym("(")
            depth = 1
            while self._peek()[0] != "EOF" and depth > 0:
                ct, cv, _ = self._consume()
                if ct == "SYM" and cv == "(":
                    depth += 1
                elif ct == "SYM" and cv == ")":
                    depth -= 1
            self.emit_push_int(4)
            return
        self._parse_primary()

    def _parse_primary(self):
        tt, tv, _ = self._peek()
        if tt == "INT":
            self._consume()
            self.emit_push_int(tv)
            return
        if tt == "FLOAT":
            self._consume()
            self._last_was_int = False
            self.emit_push_float(tv)
            return
        if tt == "STR":
            self._consume()
            # Concatenate adjacent string literals "a" "b"
            buf = [tv]
            while self._peek()[0] == "STR":
                buf.append(self._consume()[1])
            self.emit_push_str("".join(buf))
            return
        if tt == "SYM" and tv == "(":
            self._consume()
            # Check C type cast `(int)`, `(float)`, `(char *)`, etc.
            if self._is_type_start():
                cast_vt, _ = self._parse_type_spec()
                while self._match_sym("*"):
                    pass
                self._match_sym(")")
                self._parse_unary()
                if cast_vt == "LONG":
                    self.emit_u8(OP_INT)
                return
            self._parse_expr()
            self._match_sym(")")
            return
        if tt == "ID":
            # Function call: fname(...)
            if self._peek(1)[:2] == ("SYM", "("):
                fname = self._consume()[1]
                self._emit_function_call(fname, push_result=True)
                return

            vname, is_arr, idx_range = self._resolve_lvalue_name()
            if is_arr:
                idx_s, idx_e = idx_range
                saved_end = self._pos
                self._pos = idx_s
                self._parse_expr()
                self._pos = saved_end
                self.emit_u8(OP_LOAD_ARR)
                self.emit_u16(self.get_var_id(vname))
                return

            if self.var_types.get(vname) == "FLOAT":
                self._last_was_int = False

            # Check post-increment / post-decrement `x++`, `x--`
            if self._peek()[0] == "SYM" and self._peek()[1] in ("++", "--"):
                op = self._consume()[1]
                self.emit_load_var(vname)  # push original value
                self.emit_load_var(vname)
                self.emit_push_int(1)
                self.emit_u8(OP_ADD if op == "++" else OP_SUB)
                self.emit_store_var(vname)
                return

            self.emit_load_var(vname)
            return

        self._consume()
        self.emit_push_int(0)

    # --------------------------------------------------------------------------
    # Built-in C RTL (`printf`, `puts`, `strlen`, `strcpy`, `strcat`, `strcmp`) & Function Calls
    # --------------------------------------------------------------------------
    def _collect_call_args(self):
        self._match_sym("(")
        arg_ranges = []
        while self._peek()[0] != "EOF" and not (self._peek()[:2] == ("SYM", ")")):
            start_p = self._pos
            depth = 0
            while self._peek()[0] != "EOF":
                ct, cv, _ = self._peek()
                if ct == "SYM" and cv in ("(", "["):
                    depth += 1
                elif ct == "SYM" and cv in (")", "]"):
                    if depth == 0:
                        break
                    depth -= 1
                elif ct == "SYM" and cv == "," and depth == 0:
                    break
                self._consume()
            arg_ranges.append((start_p, self._pos))
            self._match_sym(",")
        self._match_sym(")")
        return arg_ranges, self._pos

    def _emit_literal_text(self, text):
        parts = text.split("\n")
        for idx_p, part in enumerate(parts):
            if idx_p > 0:
                self.emit_push_str("")
                self.emit_u8(OP_PRINT)
            if part:
                self.emit_push_str(part)
                self.emit_u8(OP_PRINT_NO_NL)

    def _emit_printf(self, arg_ranges, saved_end):
        if not arg_ranges:
            self._pos = saved_end
            return
        fmt_start, fmt_end = arg_ranges[0]
        if self._tokens[fmt_start][0] == "STR":
            # Combine adjacent string literal tokens in format
            fmt_parts = []
            p = fmt_start
            while p < fmt_end and self._tokens[p][0] == "STR":
                fmt_parts.append(self._tokens[p][1])
                p += 1
            fmt_str = "".join(fmt_parts)
            val_args = arg_ranges[1:]
            arg_idx = 0

            # Parse format specifiers: %% or %[-+0 #]*[0-9]*(\.[0-9]+)?[hlL]?[diouxXDOUeEfFgGcsp]
            spec_re = re.compile(r"%(%|[-+0 #]*\d*(?:\.\d+)?(?:[hlL])?[diouxXDOUeEfFgGcsp])")
            last_end = 0
            for m in spec_re.finditer(fmt_str):
                if m.start() > last_end:
                    self._emit_literal_text(fmt_str[last_end:m.start()])
                spec = m.group(1)
                if spec == "%":
                    self._emit_literal_text("%")
                else:
                    if arg_idx < len(val_args):
                        a_s, a_e = val_args[arg_idx]
                        arg_idx += 1
                        self._pos = a_s
                        self._parse_assignment_expr()
                        if spec.endswith("c"):
                            self.emit_u8(OP_CHR)
                        self.emit_u8(OP_PRINT_NO_NL)
                last_end = m.end()
            if last_end < len(fmt_str):
                self._emit_literal_text(fmt_str[last_end:])
        else:
            self._pos = fmt_start
            self._parse_assignment_expr()
            self.emit_u8(OP_PRINT_NO_NL)
        self._pos = saved_end

    def _emit_function_call(self, fname, push_result=False):
        arg_ranges, saved_end = self._collect_call_args()

        if fname in ("PRINTF", "FPRINTF"):
            if fname == "FPRINTF" and len(arg_ranges) >= 2:
                arg_ranges = arg_ranges[1:]
            self._emit_printf(arg_ranges, saved_end)
            if push_result:
                self.emit_push_int(1)
            return

        if fname in ("PUTS", "LIB$PUT_OUTPUT", "SYS$PUTMSG"):
            if arg_ranges:
                self._pos = arg_ranges[0][0]
                self._parse_assignment_expr()
                self._pos = saved_end
            else:
                self.emit_push_str("")
            self.emit_u8(OP_PRINT)
            if push_result:
                self.emit_push_int(1)
            return

        if fname == "STRLEN":
            if arg_ranges:
                self._pos = arg_ranges[0][0]
                self._parse_assignment_expr()
                self._pos = saved_end
                self.emit_u8(OP_LEN)
            elif push_result:
                self.emit_push_int(0)
            return

        if fname == "STRCPY":
            if len(arg_ranges) >= 2:
                dst_tok = self._tokens[arg_ranges[0][0]][1]
                self._pos = arg_ranges[1][0]
                self._parse_assignment_expr()
                self._pos = saved_end
                self.emit_store_var(dst_tok)
                if push_result:
                    self.emit_load_var(dst_tok)
            return

        if fname == "STRCAT":
            if len(arg_ranges) >= 2:
                dst_tok = self._tokens[arg_ranges[0][0]][1]
                self.emit_load_var(dst_tok)
                self._pos = arg_ranges[1][0]
                self._parse_assignment_expr()
                self._pos = saved_end
                self.emit_u8(OP_ADD)
                self.emit_store_var(dst_tok)
                if push_result:
                    self.emit_load_var(dst_tok)
            return

        if fname == "STRCMP":
            if len(arg_ranges) >= 2:
                self._pos = arg_ranges[0][0]
                self._parse_assignment_expr()
                self._pos = arg_ranges[1][0]
                self._parse_assignment_expr()
                self._pos = saved_end
                self.emit_u8(OP_NEQ)
            elif push_result:
                self.emit_push_int(0)
            return

        if fname in ("ATOI", "ATOL"):
            if arg_ranges:
                self._pos = arg_ranges[0][0]
                self._parse_assignment_expr()
                self._pos = saved_end
                self.emit_u8(OP_VAL)
                self.emit_u8(OP_INT)
            elif push_result:
                self.emit_push_int(0)
            return

        if fname in ("EXIT", "SYS$EXIT", "_EXIT", "ABORT"):
            self.emit_u8(OP_HALT)
            if push_result:
                self.emit_push_int(0)
            return

        # User-defined function in this module
        if fname in self.functions and self.functions[fname]["is_defined"]:
            finfo = self.functions[fname]
            for idx_a, (a_s, a_e) in enumerate(arg_ranges):
                if idx_a < len(finfo["params"]):
                    self._pos = a_s
                    self._parse_assignment_expr()
                    self.emit_store_var(finfo["params"][idx_a])
            self._pos = saved_end
            self.emit_jump(OP_CALL, finfo["label"])
            if push_result:
                self.emit_load_var(finfo["ret_var"])
            return

        # External module call resolved by OpenVMS Linker (vmslink)
        self._pos = saved_end
        self.emit_u8(OP_CALL_OVL)
        rel_off = len(self.bytecode)
        self.emit_u16(0)
        self.relocations.append({"offset": rel_off, "type": "CALL_OVL", "target": fname})
        if push_result:
            self.emit_push_int(1)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX C {self.VERSION}",
            "symbols": {k: v for k, v in self.labels.items() if not k.startswith("__")},
            "relocations": self.relocations,
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC VAX C {self.VERSION} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                f.write("Line  Offset  Source Statement\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nStorage Allocation & Symbol Map:\n")
                for vname, vid in sorted(self.var_map.items(), key=lambda x: x[1]):
                    if not vname.startswith("__"):
                        vtype = self.var_types.get(vname, "LONG")
                        f.write(f"  Slot {vid:>3} : {vname:<28} ({vtype})\n")
                f.write(f"\nCompilation Summary: 0 Diagnostics, {len(self.bytecode)} bytes generated.\n")


def main():
    args = list(sys.argv[1:])
    expanded = True
    while expanded:
        expanded = False
        new_args = []
        for a in args:
            if a.startswith("@") and os.path.isfile(a[1:]):
                with open(a[1:], "r", errors="replace") as rf:
                    new_args.extend([ln.strip() for ln in rf.read().splitlines() if ln.strip()])
                expanded = True
            else:
                new_args.append(a)
        args = new_args

    if not args:
        print("Usage: vaxc <input.c> [-o output.obj] [-l [listing.lst]] [/OBJECT=...] [/LIST[=...]]")
        sys.exit(1)

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
        print("%CC-E-NOFILE, no input .C file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".C", ".c"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%CC-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXCCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX C {VAXCCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
