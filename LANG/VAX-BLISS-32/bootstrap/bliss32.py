#!/usr/bin/env python3
"""
DEC VAX BLISS-32 V4.7 Systems Implementation Language Compiler (bliss32.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Compiles DEC VAX BLISS-32 source files (.B32 / .BLI) into OpenVMS relocatable
object modules (.OBJ) compatible with vmslink and vms_vm, and generates optional
compiler listing files (.LST).
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
OP_STR = 0x82


class BLISSCompiler:
    COMPILER_NAME = "VAX BLISS-32"
    VERSION = "V4.7-00"
    CREATOR = "VAX BLISS-32 V4.7"
    WORD_BITS = 32

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.ident = "V01-00"
        self.main_routine = None
        self.bytecode = bytearray()
        self.relocations = []
        self.var_map = {}
        self.var_types = {}
        self.literals = {
            "SS$_NORMAL": 1,
            "TRUE": 1,
            "FALSE": 0,
        }
        self.labels = {}
        self.fixups = []
        self.routines = {}         # rtn_name -> {label, ret_var, params}
        self.external_routines = set()
        self.vector_vars = set()
        self.listing_lines = []
        self.id_counter = 0
        self.current_rtn_ret_var = "__RET_MAIN"
        self.block_end_labels = {}  # block_label -> end_lbl
        self.loop_end_stack = []

    def new_id(self):
        self.id_counter += 1
        return self.id_counter

    def get_var_id(self, name, vtype="LONG"):
        u = name.strip().upper()
        if u not in self.var_map:
            idx = len(self.var_map)
            if idx >= 255:
                idx = 254
            self.var_map[u] = idx
            self.var_types[u] = vtype
        elif vtype != "LONG":
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

    def emit_push_int(self, val):
        iv = int(val)
        if self.WORD_BITS == 16:
            iv = iv & 0xFFFF
            if iv >= 0x8000:
                iv -= 0x10000
        else:
            if iv > 0x7FFFFFFF:
                iv -= 0x100000000
        if -32768 <= iv <= 32767:
            self.emit_u8(OP_PUSH_INT)
            self.emit_i16(iv)
        else:
            self.emit_u8(OP_PUSH_I32)
            self.emit_i32(iv)

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
    # Lexer
    # --------------------------------------------------------------------------
    def tokenize(self, source_text):
        tokens = []
        i = 0
        n = len(source_text)
        line_no = 1
        while i < n:
            ch = source_text[i]
            if ch == "\n":
                line_no += 1
                i += 1
                continue
            if ch in (" ", "\t", "\r"):
                i += 1
                continue
            # Line comment !
            if ch == "!":
                while i < n and source_text[i] != "\n":
                    i += 1
                continue
            # Block comment %( ... )%
            if source_text[i:i + 2] == "%(":
                i += 2
                while i < n and source_text[i:i + 2] != ")%":
                    if source_text[i] == "\n":
                        line_no += 1
                    i += 1
                i += 2
                continue
            # Lexical functions & radix literals starting with %
            if ch == "%":
                m_rad = re.match(r"^%([XOBD])\s*['\"]([^'\"]+)['\"]", source_text[i:], re.IGNORECASE)
                if m_rad:
                    base_ch = m_rad.group(1).upper()
                    digits = m_rad.group(2).strip()
                    base = {"X": 16, "O": 8, "B": 2, "D": 10}[base_ch]
                    tokens.append(("INT", int(digits, base), line_no))
                    i += m_rad.end()
                    continue
                m_str_fn = re.match(r"^%(?:ASCID|ASCIZ|ASCII|ASCIC|STRING)\b", source_text[i:], re.IGNORECASE)
                if m_str_fn:
                    i += m_str_fn.end()
                    continue
                m_char = re.match(r"^%CHAR\s*\(\s*(\d+)\s*\)", source_text[i:], re.IGNORECASE)
                if m_char:
                    tokens.append(("STR", chr(int(m_char.group(1))), line_no))
                    i += m_char.end()
                    continue
                i += 1
                continue
            # Quoted string '...' or "..."
            if ch in ("'", '"'):
                q = ch
                i += 1
                buf = []
                while i < n:
                    if source_text[i] == "\n":
                        line_no += 1
                    if source_text[i] == q:
                        if i + 1 < n and source_text[i + 1] == q:
                            buf.append(q)
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(source_text[i])
                    i += 1
                tokens.append(("STR", "".join(buf), line_no))
                continue
            # Two-char operators
            if source_text[i:i + 2] in ("<=", ">=", "<>", "!=", "=="):
                tokens.append(("SYM", source_text[i:i + 2], line_no))
                i += 2
                continue
            # Single-char punctuation/operators
            if ch in ".+-*/^=()[]{};,:<>":
                tokens.append(("SYM", ch, line_no))
                i += 1
                continue
            # Numbers
            if ch.isdigit():
                j = i
                while j < n and source_text[j].isdigit():
                    j += 1
                tokens.append(("INT", int(source_text[i:j]), line_no))
                i = j
                continue
            # Identifiers & keywords
            if ch.isalpha() or ch in ("_", "$"):
                j = i
                while j < n and (source_text[j].isalnum() or source_text[j] in ("_", "$")):
                    j += 1
                ident = source_text[i:j].upper()
                tokens.append(("ID", ident, line_no))
                i = j
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

    # --------------------------------------------------------------------------
    # Pass 1 & Pass 2 Compilation
    # --------------------------------------------------------------------------
    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        self._tokens = self.tokenize(source_text)

        # Pass 1: Pre-scan for ROUTINE definitions so forward calls work
        idx = 0
        ntok = len(self._tokens)
        while idx < ntok:
            tt, tv, _ = self._tokens[idx]
            if tt == "ID" and tv in ("FORWARD", "EXTERNAL"):
                while idx < ntok and not (self._tokens[idx][0] == "SYM" and self._tokens[idx][1] == ";"):
                    if tv == "EXTERNAL" and self._tokens[idx][0] == "ID" and self._tokens[idx][1] not in ("EXTERNAL", "ROUTINE", "LONG", "WORD", "BYTE", "NOVALUE"):
                        self.external_routines.add(self._tokens[idx][1])
                    idx += 1
                idx += 1
                continue
            if tt == "ID" and tv == "ROUTINE":
                if idx + 1 < ntok and self._tokens[idx + 1][0] == "ID":
                    rname = self._tokens[idx + 1][1]
                    p_idx = idx + 2
                    params = []
                    if p_idx < ntok and self._tokens[p_idx][0] == "SYM" and self._tokens[p_idx][1] == "(":
                        p_idx += 1
                        while p_idx < ntok and not (self._tokens[p_idx][0] == "SYM" and self._tokens[p_idx][1] == ")"):
                            if self._tokens[p_idx][0] == "ID":
                                pname = self._tokens[p_idx][1]
                                params.append(pname)
                                self.get_var_id(pname)
                                # Skip optional : attributes before , or )
                                p_idx += 1
                                while p_idx < ntok and not (self._tokens[p_idx][0] == "SYM" and self._tokens[p_idx][1] in (",", ")")):
                                    p_idx += 1
                            else:
                                p_idx += 1
                    ret_var = f"__RET_{rname}"
                    self.get_var_id(ret_var)
                    self.routines[rname] = {
                        "label": rname,
                        "ret_var": ret_var,
                        "params": params,
                    }
            idx += 1

        # Pass 2: Parse module and emit bytecode
        self._pos = 0
        line_offsets = {}

        if self._match_id("MODULE"):
            if self._peek()[0] == "ID":
                self.module_name = self._consume()[1][:16]
            if self._match_sym("("):
                depth = 1
                while self._peek()[0] != "EOF" and depth > 0:
                    tt, tv, _ = self._consume()
                    if tt == "SYM" and tv == "(":
                        depth += 1
                    elif tt == "SYM" and tv == ")":
                        depth -= 1
                    elif tt == "ID" and tv == "IDENT" and self._match_sym("="):
                        if self._peek()[0] in ("STR", "ID"):
                            self.ident = str(self._consume()[1])
                    elif tt == "ID" and tv == "MAIN" and self._match_sym("="):
                        if self._peek()[0] == "ID":
                            self.main_routine = self._consume()[1]
            self._match_sym("=")

        # Parse top-level BEGIN ... END or statements
        while self._peek()[0] != "EOF":
            lno = self._peek()[2]
            if lno and lno not in line_offsets:
                line_offsets[lno] = len(self.bytecode)
            if self._match_id("ELUDOM"):
                break
            self._parse_stmt(is_expr=False)
            self._match_sym(";")

        # Emit startup call to MAIN routine if present
        target_main = self.main_routine
        if not target_main:
            for cand in ("MAIN", "START"):
                if cand in self.routines:
                    target_main = cand
                    break
            if not target_main and self.routines:
                target_main = list(self.routines.keys())[-1]

        if target_main and target_main in self.routines:
            self.emit_jump(OP_CALL, self.routines[target_main]["label"])

        self.emit_u8(OP_HALT)

        # Resolve local jump fixups
        for fix_pos, target_lbl in self.fixups:
            if target_lbl in self.labels:
                addr = self.labels[target_lbl]
                self.bytecode[fix_pos] = addr & 0xFF
                self.bytecode[fix_pos + 1] = (addr >> 8) & 0xFF

        # Populate listing lines with offsets
        cur_off = 0
        for idx_l, raw in enumerate(raw_lines, start=1):
            if idx_l in line_offsets:
                cur_off = line_offsets[idx_l]
            self.listing_lines.append((idx_l, cur_off, raw.rstrip("\r\n")))

    # --------------------------------------------------------------------------
    # Statement & Declaration Parser
    # --------------------------------------------------------------------------
    def _parse_stmt(self, is_expr=False):
        tt, tv, _ = self._peek()
        if tt == "EOF":
            if is_expr:
                self.emit_push_int(0)
            return

        if tt == "SYM" and tv == ";":
            self._consume()
            if is_expr:
                self.emit_push_int(0)
            return

        # Labeled block: LABEL_NAME : BEGIN ... END
        if tt == "ID" and self._peek(1)[:2] == ("SYM", ":"):
            blk_label = self._consume()[1]
            self._consume()  # ':'
            end_lbl = f"__BLK_END_{blk_label}_{self.new_id()}"
            self.block_end_labels[blk_label] = end_lbl
            self._parse_stmt(is_expr=is_expr)
            self.labels[end_lbl] = len(self.bytecode)
            return

        # BEGIN ... END block
        if self._match_id("BEGIN"):
            self._parse_block_body("END", is_expr=is_expr)
            return

        # Declarations: LOCAL, OWN, GLOBAL, STACKLOCAL, REGISTER
        if tt == "ID" and tv in ("LOCAL", "OWN", "GLOBAL", "STACKLOCAL", "REGISTER"):
            if tv == "GLOBAL" and self._peek(1)[:2] == ("ID", "ROUTINE"):
                self._consume()  # GLOBAL
                self._parse_routine()
                if is_expr:
                    self.emit_push_int(1)
                return
            if tv == "GLOBAL" and self._peek(1)[:2] == ("ID", "BIND"):
                self._consume()
                self._parse_bind()
                if is_expr:
                    self.emit_push_int(1)
                return
            if tv == "GLOBAL" and self._peek(1)[:2] == ("ID", "LITERAL"):
                self._consume()
                self._parse_literal()
                if is_expr:
                    self.emit_push_int(1)
                return
            self._consume()
            self._parse_var_decl()
            if is_expr:
                self.emit_push_int(1)
            return

        if tt == "ID" and tv == "LITERAL":
            self._consume()
            self._parse_literal()
            if is_expr:
                self.emit_push_int(1)
            return

        if tt == "ID" and tv == "BIND":
            self._consume()
            self._parse_bind()
            if is_expr:
                self.emit_push_int(1)
            return

        if tt == "ID" and tv in ("FORWARD", "EXTERNAL", "SWITCHES", "LIBRARY", "REQUIRE"):
            while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == ";"):
                self._consume()
            if is_expr:
                self.emit_push_int(1)
            return

        if tt == "ID" and tv == "ROUTINE":
            self._parse_routine()
            if is_expr:
                self.emit_push_int(1)
            return

        # Control structures
        if self._match_id("IF"):
            self._parse_if(is_expr=is_expr)
            return

        if tt == "ID" and tv in ("INCR", "DECR"):
            is_decr = (self._consume()[1] == "DECR")
            self._parse_incr_decr(is_decr)
            if is_expr:
                self.emit_push_int(1)
            return

        if tt == "ID" and tv in ("WHILE", "UNTIL"):
            is_until = (self._consume()[1] == "UNTIL")
            self._parse_while_until(is_until)
            if is_expr:
                self.emit_push_int(1)
            return

        if self._match_id("DO"):
            self._parse_do_loop()
            if is_expr:
                self.emit_push_int(1)
            return

        if tt == "ID" and tv in ("SELECTONE", "SELECT", "SELECTU", "SELECTONEU"):
            self._consume()
            self._parse_select()
            if is_expr:
                self.emit_push_int(1)
            return

        if self._match_id("LEAVE"):
            if self._peek()[0] == "ID":
                lbl = self._consume()[1]
                if self._match_id("WITH"):
                    self._parse_expr()
                    self.emit_store_var(self.current_rtn_ret_var)
                if lbl in self.block_end_labels:
                    self.emit_jump(OP_JMP, self.block_end_labels[lbl])
                elif self.loop_end_stack:
                    self.emit_jump(OP_JMP, self.loop_end_stack[-1])
            elif self.loop_end_stack:
                self.emit_jump(OP_JMP, self.loop_end_stack[-1])
            if is_expr:
                self.emit_push_int(0)
            return

        if self._match_id("EXITLOOP"):
            if self._peek()[0] not in ("SYM", "EOF") and self._peek()[1] not in ("END", "TES", "ELSE"):
                self._parse_expr()
                self.emit_store_var(self.current_rtn_ret_var)
            if self.loop_end_stack:
                self.emit_jump(OP_JMP, self.loop_end_stack[-1])
            if is_expr:
                self.emit_push_int(0)
            return

        if self._match_id("RETURN"):
            if self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] in (";", ")")) and self._peek()[1] not in ("END", "TES", "ELSE", "ELUDOM"):
                self._parse_expr()
                self.emit_store_var(self.current_rtn_ret_var)
            self.emit_u8(OP_RET)
            if is_expr:
                self.emit_push_int(0)
            return

        # Assignment: IDENT = expr  OR  IDENT[idx] = expr
        if tt == "ID":
            # Look ahead for assignment `=` vs `[`
            if self._peek(1)[:2] == ("SYM", "="):
                vname = self._consume()[1]
                self._consume()  # '='
                self._parse_expr()
                self.emit_store_var(vname)
                if is_expr:
                    self.emit_load_var(vname)
                return
            if self._peek(1)[:2] == ("SYM", "["):
                # Scan past [...] to see if followed by '='
                scan = 2
                depth = 1
                while self._peek(scan)[0] != "EOF" and depth > 0:
                    s_tt, s_tv, _ = self._peek(scan)
                    if s_tt == "SYM" and s_tv == "[":
                        depth += 1
                    elif s_tt == "SYM" and s_tv == "]":
                        depth -= 1
                    scan += 1
                if self._peek(scan)[:2] == ("SYM", "="):
                    aname = self._consume()[1]
                    self._consume()  # '['
                    # Parse index expression later after value so stack order is (val, idx) for OP_STORE_ARR
                    idx_start = self._pos
                    depth = 1
                    while self._peek()[0] != "EOF" and depth > 0:
                        c_tt, c_tv, _ = self._consume()
                        if c_tt == "SYM" and c_tv == "[":
                            depth += 1
                        elif c_tt == "SYM" and c_tv == "]":
                            depth -= 1
                    idx_end = self._pos - 1
                    self._match_sym("=")
                    self._parse_expr()  # Pushes RHS value first
                    after_rhs = self._pos
                    self._pos = idx_start
                    self._parse_expr()  # Pushes index second
                    self._pos = after_rhs
                    self.emit_u8(OP_STORE_ARR)
                    self.emit_u16(self.get_var_id(aname))
                    if is_expr:
                        self.emit_push_int(1)
                    return

            # Standalone routine call: IDENT(...)
            if self._peek(1)[:2] == ("SYM", "(") and not is_expr:
                rname = self._consume()[1]
                self._emit_routine_call(rname, push_result=False)
                return

        # Otherwise parse as expression
        self._parse_expr()
        if not is_expr:
            # In BLISS, the value of the last expression in a routine body is its return value
            self.emit_store_var(self.current_rtn_ret_var)

    def _parse_block_body(self, end_kw="END", is_expr=False):
        stmts_count = 0
        while self._peek()[0] != "EOF":
            if self._match_id(end_kw):
                break
            if self._match_sym(";"):
                continue
            # Check if this is the final item before END
            self._parse_stmt(is_expr=False)
            stmts_count += 1
            self._match_sym(";")
        if is_expr:
            self.emit_load_var(self.current_rtn_ret_var)

    def _eval_const_expr(self):
        sign = 1
        if self._match_sym("-"):
            sign = -1
        elif self._match_sym("+"):
            sign = 1
        tt, tv, _ = self._peek()
        val = 0
        if tt == "INT":
            val = self._consume()[1] * sign
        elif tt == "ID" and tv in self.literals:
            val = self.literals[self._consume()[1]] * sign
        while self._peek()[0] == "SYM" and self._peek()[1] in ("+", "-", "*", "/"):
            op = self._consume()[1]
            rhs = self._eval_const_expr()
            if op == "+":
                val += rhs
            elif op == "-":
                val -= rhs
            elif op == "*":
                val *= rhs
            elif op == "/" and rhs != 0:
                val //= rhs
        return val

    def _parse_literal(self):
        while self._peek()[0] != "EOF":
            if self._peek()[0] == "SYM" and self._peek()[1] == ";":
                break
            if self._peek()[0] == "ID":
                cname = self._consume()[1]
                if self._match_sym("="):
                    cval = self._eval_const_expr()
                    self.literals[cname] = cval
            if not self._match_sym(","):
                break

    def _parse_bind(self):
        while self._peek()[0] != "EOF":
            if self._peek()[0] == "SYM" and self._peek()[1] == ";":
                break
            if self._peek()[0] == "ID":
                bname = self._consume()[1]
                # Skip optional : attributes before =
                if self._match_sym(":"):
                    while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == "="):
                        self._consume()
                if self._match_sym("="):
                    if self._match_id("UPLIT", "PLIT"):
                        self._match_sym("(")
                        elems = []
                        while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == ")"):
                            elems.append(self._eval_const_expr())
                            self._match_sym(",")
                        self._match_sym(")")
                        self.vector_vars.add(bname)
                        self.emit_push_int(max(1, len(elems)))
                        self.emit_u8(OP_DIM_ARR)
                        self.emit_u16(self.get_var_id(bname))
                        for idx_e, ev in enumerate(elems):
                            self.emit_push_int(ev)
                            self.emit_push_int(idx_e)
                            self.emit_u8(OP_STORE_ARR)
                            self.emit_u16(self.get_var_id(bname))
                    elif self._peek()[0] == "STR":
                        sval = self._consume()[1]
                        self.get_var_id(bname, "STR")
                        self.emit_push_str(sval)
                        self.emit_store_var(bname)
                    else:
                        self._parse_expr()
                        self.emit_store_var(bname)
            if not self._match_sym(","):
                break

    def _parse_var_decl(self):
        while self._peek()[0] != "EOF":
            if self._peek()[0] == "SYM" and self._peek()[1] == ";":
                break
            if self._peek()[0] != "ID":
                self._consume()
                continue
            vname = self._consume()[1]
            self.get_var_id(vname)
            is_vec = False
            vec_size = 0
            init_vals = None

            if self._match_sym(":"):
                # Parse BLISS allocation attributes: VECTOR[n], BLOCK[n,...], INITIAL(...), LONG, WORD, BYTE, etc.
                while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] in (",", ";", "=")):
                    att_t, att_v, _ = self._peek()
                    if att_t == "ID" and att_v in ("VECTOR", "BLOCK", "BITVECTOR"):
                        self._consume()
                        is_vec = True
                        if self._match_sym("["):
                            vec_size = self._eval_const_expr()
                            while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == "]"):
                                self._consume()
                            self._match_sym("]")
                    elif att_t == "ID" and att_v == "INITIAL":
                        self._consume()
                        if self._match_sym("("):
                            init_vals = []
                            while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == ")"):
                                if self._peek()[0] == "STR":
                                    init_vals.append(("STR", self._consume()[1]))
                                else:
                                    init_vals.append(("INT", self._eval_const_expr()))
                                self._match_sym(",")
                            self._match_sym(")")
                    else:
                        self._consume()

            if is_vec:
                self.vector_vars.add(vname)
                self.emit_push_int(max(1, vec_size))
                self.emit_u8(OP_DIM_ARR)
                self.emit_u16(self.get_var_id(vname))
                if init_vals:
                    for idx_i, (ityp, ival) in enumerate(init_vals):
                        if ityp == "STR":
                            self.emit_push_str(ival)
                        else:
                            self.emit_push_int(ival)
                        self.emit_push_int(idx_i)
                        self.emit_u8(OP_STORE_ARR)
                        self.emit_u16(self.get_var_id(vname))
            elif init_vals:
                ityp, ival = init_vals[0]
                if ityp == "STR":
                    self.get_var_id(vname, "STR")
                    self.emit_push_str(ival)
                else:
                    self.emit_push_int(ival)
                self.emit_store_var(vname)
            elif self._match_sym("="):
                self._parse_expr()
                self.emit_store_var(vname)
            else:
                # Default initialize scalar local/own to 0
                self.emit_push_int(0)
                self.emit_store_var(vname)

            if not self._match_sym(","):
                break

    def _parse_routine(self):
        self._match_id("ROUTINE")
        rname = self._consume()[1] if self._peek()[0] == "ID" else f"RTN_{self.new_id()}"
        if self._match_sym("("):
            while self._peek()[0] != "EOF" and not self._match_sym(")"):
                self._consume()
        # Optional : NOVALUE or attributes before =
        if self._match_sym(":"):
            while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == "="):
                self._consume()
        self._match_sym("=")

        end_rtn_lbl = f"__END_RTN_{rname}"
        self.emit_jump(OP_JMP, end_rtn_lbl)
        self.labels[rname] = len(self.bytecode)

        prev_ret = self.current_rtn_ret_var
        self.current_rtn_ret_var = f"__RET_{rname}"
        self.get_var_id(self.current_rtn_ret_var)

        self._parse_stmt(is_expr=False)

        self.emit_u8(OP_RET)
        self.labels[end_rtn_lbl] = len(self.bytecode)
        self.current_rtn_ret_var = prev_ret

    def _parse_if(self, is_expr=False):
        if_id = self.new_id()
        else_lbl = f"__IF_ELSE_{if_id}"
        end_lbl = f"__IF_END_{if_id}"

        self._parse_expr()
        self._match_id("THEN")
        self.emit_jump(OP_JMP_FALSE, else_lbl)
        self._parse_stmt(is_expr=is_expr)
        if self._match_id("ELSE"):
            self.emit_jump(OP_JMP, end_lbl)
            self.labels[else_lbl] = len(self.bytecode)
            self._parse_stmt(is_expr=is_expr)
            self.labels[end_lbl] = len(self.bytecode)
        else:
            if is_expr:
                self.emit_jump(OP_JMP, end_lbl)
                self.labels[else_lbl] = len(self.bytecode)
                self.emit_push_int(0)
                self.labels[end_lbl] = len(self.bytecode)
            else:
                self.labels[else_lbl] = len(self.bytecode)

    def _parse_incr_decr(self, is_decr=False):
        vname = self._consume()[1] if self._peek()[0] == "ID" else f"__IDX_{self.new_id()}"
        self.get_var_id(vname)

        if self._match_id("FROM"):
            self._parse_expr()
        else:
            self.emit_push_int(0)
        self.emit_store_var(vname)

        lid = self.new_id()
        top_lbl = f"__LOOP_TOP_{lid}"
        end_lbl = f"__LOOP_END_{lid}"
        hi_var = f"__LOOP_HI_{lid}"
        step_var = f"__LOOP_STEP_{lid}"

        if self._match_id("TO"):
            self._parse_expr()
        else:
            self.emit_push_int(0)
        self.emit_store_var(hi_var)

        if self._match_id("BY"):
            self._parse_expr()
        else:
            self.emit_push_int(1)
        self.emit_store_var(step_var)

        self._match_id("DO")

        self.labels[top_lbl] = len(self.bytecode)
        self.emit_load_var(vname)
        self.emit_load_var(hi_var)
        self.emit_u8(OP_GE if is_decr else OP_LE)
        self.emit_jump(OP_JMP_FALSE, end_lbl)

        self.loop_end_stack.append(end_lbl)
        self._parse_stmt(is_expr=False)
        self.loop_end_stack.pop()

        self.emit_load_var(vname)
        self.emit_load_var(step_var)
        self.emit_u8(OP_SUB if is_decr else OP_ADD)
        self.emit_store_var(vname)
        self.emit_jump(OP_JMP, top_lbl)
        self.labels[end_lbl] = len(self.bytecode)

    def _parse_while_until(self, is_until=False):
        lid = self.new_id()
        top_lbl = f"__WLOOP_TOP_{lid}"
        body_lbl = f"__WLOOP_BODY_{lid}"
        end_lbl = f"__WLOOP_END_{lid}"

        self.labels[top_lbl] = len(self.bytecode)
        self._parse_expr()
        if is_until:
            self.emit_jump(OP_JMP_FALSE, body_lbl)
            self.emit_jump(OP_JMP, end_lbl)
            self.labels[body_lbl] = len(self.bytecode)
        else:
            self.emit_jump(OP_JMP_FALSE, end_lbl)

        self._match_id("DO")
        self.loop_end_stack.append(end_lbl)
        self._parse_stmt(is_expr=False)
        self.loop_end_stack.pop()
        self.emit_jump(OP_JMP, top_lbl)
        self.labels[end_lbl] = len(self.bytecode)

    def _parse_do_loop(self):
        lid = self.new_id()
        top_lbl = f"__DOLOOP_TOP_{lid}"
        end_lbl = f"__DOLOOP_END_{lid}"

        self.labels[top_lbl] = len(self.bytecode)
        self.loop_end_stack.append(end_lbl)
        self._parse_stmt(is_expr=False)
        self.loop_end_stack.pop()

        if self._match_id("WHILE"):
            self._parse_expr()
            self.emit_jump(OP_JMP_FALSE, end_lbl)
            self.emit_jump(OP_JMP, top_lbl)
        elif self._match_id("UNTIL"):
            self._parse_expr()
            self.emit_jump(OP_JMP_FALSE, top_lbl)
        self.labels[end_lbl] = len(self.bytecode)

    def _parse_select(self):
        sid = self.new_id()
        sel_var = f"__SEL_VAL_{sid}"
        end_lbl = f"__SEL_END_{sid}"
        self._parse_expr()
        self.emit_store_var(sel_var)
        self._match_id("OF")
        self._match_id("SET")

        arm_idx = 0
        while self._peek()[0] != "EOF":
            if self._match_id("TES"):
                break
            if self._match_sym(";"):
                continue
            if self._match_sym("["):
                arm_idx += 1
                next_arm_lbl = f"__SEL_{sid}_ARM_{arm_idx}"
                if self._match_id("OTHERWISE", "ALWAYS"):
                    self._match_sym("]")
                    self._match_sym(":")
                    self._parse_stmt(is_expr=False)
                    self._match_sym(";")
                    self.emit_jump(OP_JMP, end_lbl)
                    self.labels[next_arm_lbl] = len(self.bytecode)
                    continue

                # Parse one or more values or ranges lo TO hi inside [...]
                cond_count = 0
                while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == "]"):
                    self.emit_load_var(sel_var)
                    self._parse_expr()
                    if self._match_id("TO"):
                        self.emit_u8(OP_GE)
                        self.emit_load_var(sel_var)
                        self._parse_expr()
                        self.emit_u8(OP_LE)
                        self.emit_u8(OP_AND)
                    else:
                        self.emit_u8(OP_EQ)
                    cond_count += 1
                    if cond_count > 1:
                        self.emit_u8(OP_OR)
                    self._match_sym(",")
                self._match_sym("]")
                self._match_sym(":")
                self.emit_jump(OP_JMP_FALSE, next_arm_lbl)
                self._parse_stmt(is_expr=False)
                self._match_sym(";")
                self.emit_jump(OP_JMP, end_lbl)
                self.labels[next_arm_lbl] = len(self.bytecode)
            else:
                self._consume()

        self.labels[end_lbl] = len(self.bytecode)

    # --------------------------------------------------------------------------
    # Expression Parser
    # --------------------------------------------------------------------------
    def _parse_expr(self):
        self._parse_or()

    def _parse_or(self):
        self._parse_and()
        while self._peek()[0] == "ID" and self._peek()[1] in ("OR", "XOR", "EQV"):
            op = self._consume()[1]
            self._parse_and()
            self.emit_u8(OP_OR if op == "OR" else OP_XOR)

    def _parse_and(self):
        self._parse_not()
        while self._peek()[:2] == ("ID", "AND"):
            self._consume()
            self._parse_not()
            self.emit_u8(OP_AND)

    def _parse_not(self):
        if self._peek()[:2] == ("ID", "NOT"):
            self._consume()
            self._parse_not()
            self.emit_u8(OP_NOT)
        else:
            self._parse_rel()

    def _parse_rel(self):
        self._parse_add()
        rel_id_map = {
            "EQL": OP_EQ, "EQLU": OP_EQ, "EQLA": OP_EQ,
            "NEQ": OP_NEQ, "NEQU": OP_NEQ, "NEQA": OP_NEQ,
            "LSS": OP_LT, "LSSU": OP_LT, "LSSA": OP_LT,
            "LEQ": OP_LE, "LEQU": OP_LE, "LEQA": OP_LE,
            "GTR": OP_GT, "GTRU": OP_GT, "GTRA": OP_GT,
            "GEQ": OP_GE, "GEQU": OP_GE, "GEQA": OP_GE,
        }
        rel_sym_map = {
            "==": OP_EQ, "=": OP_EQ,
            "!=": OP_NEQ, "<>": OP_NEQ,
            "<": OP_LT, "<=": OP_LE,
            ">": OP_GT, ">=": OP_GE,
        }
        while True:
            tt, tv, _ = self._peek()
            if tt == "ID" and tv in rel_id_map:
                self._consume()
                self._parse_add()
                self.emit_u8(rel_id_map[tv])
            elif tt == "SYM" and tv in rel_sym_map:
                self._consume()
                self._parse_add()
                self.emit_u8(rel_sym_map[tv])
            else:
                break

    def _parse_add(self):
        self._parse_mul()
        while self._peek()[0] == "SYM" and self._peek()[1] in ("+", "-"):
            op = self._consume()[1]
            self._parse_mul()
            self.emit_u8(OP_ADD if op == "+" else OP_SUB)

    def _parse_mul(self):
        self._parse_unary()
        while True:
            tt, tv, _ = self._peek()
            if tt == "SYM" and tv in ("*", "/"):
                self._consume()
                self._parse_unary()
                if tv == "*":
                    self.emit_u8(OP_MUL)
                else:
                    self.emit_u8(OP_DIV)
                    self.emit_u8(OP_INT)
            elif tt == "ID" and tv == "MOD":
                self._consume()
                self._parse_unary()
                self.emit_u8(OP_MOD)
            else:
                break

    def _parse_unary(self):
        # BLISS explicit dereference operator `.`
        if self._match_sym("."):
            self._parse_unary()
            return
        if self._match_sym("-"):
            self.emit_push_int(0)
            self._parse_unary()
            self.emit_u8(OP_SUB)
            return
        if self._match_sym("+"):
            self._parse_unary()
            return
        self._parse_primary()

    def _parse_primary(self):
        tt, tv, _ = self._peek()
        if tt == "INT":
            self._consume()
            self.emit_push_int(tv)
            return
        if tt == "STR":
            self._consume()
            self.emit_push_str(tv)
            return
        if tt == "SYM" and tv == "(":
            self._consume()
            # Could be parenthesized expression or compound expression (s1; s2; ...)
            if self._peek()[:2] == ("ID", "IF"):
                self._consume()
                self._parse_if(is_expr=True)
            else:
                self._parse_expr()
            self._match_sym(")")
            return
        if tt == "ID" and tv == "IF":
            self._consume()
            self._parse_if(is_expr=True)
            return
        if tt == "ID" and tv == "BEGIN":
            self._consume()
            self._parse_block_body("END", is_expr=True)
            return
        if tt == "ID":
            ident = self._consume()[1]
            if ident in self.literals:
                self.emit_push_int(self.literals[ident])
                return
            # Routine call in expression
            if self._peek()[:2] == ("SYM", "("):
                self._emit_routine_call(ident, push_result=True)
                return
            # Vector / array element access: VEC[idx]
            if self._peek()[:2] == ("SYM", "["):
                self._consume()  # '['
                self._parse_expr()
                self._match_sym("]")
                self.emit_u8(OP_LOAD_ARR)
                self.emit_u16(self.get_var_id(ident))
                return
            self.emit_load_var(ident)
            return

        self._consume()
        self.emit_push_int(0)

    def _emit_routine_call(self, rname, push_result=False):
        self._match_sym("(")
        # Built-in output routines: TTY_PUT_MSG, LIB$PUT_OUTPUT, PRINT, PUT_LINE
        if rname in ("TTY_PUT_MSG", "LIB$PUT_OUTPUT", "PRINT", "PUT_LINE", "PRTSTR", "PRTINT"):
            arg_positions = []
            while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == ")"):
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
                arg_positions.append((start_p, self._pos))
                self._match_sym(",")
            self._match_sym(")")

            saved_end = self._pos
            if not arg_positions:
                self.emit_push_str("")
                self.emit_u8(OP_PRINT)
            else:
                for idx_a, (ap_start, ap_end) in enumerate(arg_positions):
                    self._pos = ap_start
                    self._parse_expr()
                    is_last = (idx_a == len(arg_positions) - 1)
                    self.emit_u8(OP_PRINT if is_last else OP_PRINT_NO_NL)
            self._pos = saved_end
            if push_result:
                self.emit_push_int(1)  # SS$_NORMAL
            return

        # User-defined routine or external routine
        arg_positions = []
        while self._peek()[0] != "EOF" and not (self._peek()[0] == "SYM" and self._peek()[1] == ")"):
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
            arg_positions.append((start_p, self._pos))
            self._match_sym(",")
        self._match_sym(")")
        saved_end = self._pos

        if rname in self.routines:
            rinfo = self.routines[rname]
            for idx_a, (ap_start, ap_end) in enumerate(arg_positions):
                if idx_a < len(rinfo["params"]):
                    self._pos = ap_start
                    self._parse_expr()
                    self.emit_store_var(rinfo["params"][idx_a])
            self._pos = saved_end
            self.emit_jump(OP_CALL, rinfo["label"])
            if push_result:
                self.emit_load_var(rinfo["ret_var"])
        else:
            self._pos = saved_end
            self.emit_u8(OP_CALL_OVL)
            rel_off = len(self.bytecode)
            self.emit_u16(0)
            self.relocations.append({"offset": rel_off, "type": "CALL_OVL", "target": rname})
            if push_result:
                self.emit_push_int(1)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": self.CREATOR,
            "symbols": {k: v for k, v in self.labels.items() if not k.startswith("__")},
            "relocations": self.relocations,
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC {self.COMPILER_NAME} {self.VERSION} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                f.write("Line  Offset  Source Statement\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nPSECT & Symbol Storage Map:\n")
                for vname, vid in sorted(self.var_map.items(), key=lambda x: x[1]):
                    if not vname.startswith("__"):
                        vtype = "VECTOR" if vname in self.vector_vars else self.var_types.get(vname, "LONG")
                        f.write(f"  Slot {vid:>3} : {vname:<28} ({vtype})\n")
                f.write(f"\nCompilation Complete: 0 Diagnostics, {len(self.bytecode)} bytes generated.\n")


def run_cli(compiler_cls, default_exts, err_prefix):
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
        print(f"Usage: {sys.argv[0]} <input> [-o output.obj] [-l [listing.lst]] [/OBJECT=...] [/LIST[=...]]")
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
        print(f"%{err_prefix}-E-NOFILE, no input source file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in default_exts:
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%{err_prefix}-E-OPENIN, error opening {in_file} as input")
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

    comp = compiler_cls(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"{compiler_cls.COMPILER_NAME} {compiler_cls.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    run_cli(BLISSCompiler, (".B32", ".b32", ".BLI", ".bli"), "BLISS32")
