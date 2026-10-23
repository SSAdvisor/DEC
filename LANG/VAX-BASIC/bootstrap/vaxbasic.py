#!/usr/bin/env python3
"""
DEC VAX BASIC V3.5 Compiler & Interactive Environment (vaxbasic.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Supports:
  - Full DEC VAX BASIC V3.5 structured language (line-numberless & line-numbered):
    * PROGRAM <name> ... END PROGRAM, %TITLE, %IDENT, OPTION TYPE = EXPLICIT
    * DECLARE LONG, WORD, BYTE, SINGLE, DOUBLE, GFLOAT, DECIMAL, STRING, CONSTANT
    * RECORD <Type> ... END RECORD and structured field access (REC::FIELD)
    * SELECT <expr> / CASE <val> / CASE <lo> TO <hi> / CASE ELSE / END SELECT
    * IF ... THEN ... ELSEIF ... ELSE ... END IF (multi-line & single-line)
    * FOR ... TO ... STEP ... NEXT, WHILE ... NEXT, UNTIL ... NEXT, EXIT, ITERATE
    * WHEN ERROR IN ... USE ... END WHEN structured exception blocks
    * SUB <name>(...) ... END SUB, FUNCTION <type> <name>(...) ... END FUNCTION,
      DEF <type> <name>(...) ... END DEF, and external CALL <module>
    * Full RMS File I/O (OPEN, CLOSE, GET, PUT, PRINT #, INPUT #, LINE INPUT #)
    * Emits OpenVMS .OBJ relocatable object modules and .LST compiler listings
  - Interactive VAX BASIC V3.5 Environment (Ready prompt: NEW, OLD, SAVE, LIST,
    SEQUENCE, COMPILE, RUN, HELP, EXIT)
"""

import os
import re
import sys
import json
import struct
import subprocess
import tempfile
from datetime import datetime

# Bytecode Opcodes (vms_vm & rsts_vm compatible)
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
OP_PRINT_CH = 0x52
OP_PRINT_USING = 0x53
OP_RMS_OPEN = 0x60
OP_RMS_GET = 0x61
OP_RMS_PUT = 0x62
OP_RMS_CLOSE = 0x63
OP_RMS_REST = 0x64
OP_INPUT_I = 0x70
OP_INPUT_S = 0x71
OP_INKEY = 0x72
OP_CHR = 0x73
OP_RND = 0x74
OP_INT = 0x75
OP_DATA_INIT = 0x76
OP_READ = 0x77
OP_ON_ERROR = 0x78
OP_RESUME = 0x79
OP_DATE_STR = 0x7A
OP_LINE_INPUT_CH = 0x7B
OP_LEN = 0x7C
OP_MID = 0x7D
OP_LEFT = 0x7E
OP_RIGHT = 0x7F
OP_INSTR = 0x80
OP_VAL = 0x81
OP_STR = 0x82
OP_ASCII = 0x83
OP_SYS = 0x84
OP_COMMAND_STR = 0x85
OP_TIME_STR = 0x86


class VAXBasicCompiler:
    VERSION = "V3.5-00"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()
        self.ident = "V03-05"
        self.title = ""
        self.bytecode = bytearray()
        self.relocations = []
        self.var_map = {}          # var_name -> int index (0..255)
        self.var_types = {}        # var_name -> 'STR' | 'FLOAT' | 'INT'
        self.constants = {}        # const_name -> literal token
        self.record_defs = {}      # rec_type -> list of (field_name, field_type)
        self.record_vars = {}      # var_name -> rec_type
        self.labels = {}           # label_or_lineno -> bytecode offset
        self.fixups = []           # (offset, target_label, src_line)
        self.sub_defs = {}         # sub_name -> {label, params: [var_names]}
        self.fn_defs = {}          # fn_name -> {label, ret_var, params: [var_names], expr_inline}
        self.ctrl_stack = []       # stack of control structures
        self.listing_lines = []    # (lineno, offset, text)
        self.data_pool = []        # list of (dtype_str, val)
        self.select_counter = 0
        self.loop_counter = 0

    def get_var_id(self, name, vtype=None):
        u = name.strip().upper().replace("::", ".")
        if u not in self.var_map:
            idx = len(self.var_map)
            if idx >= 255:
                idx = 254
            self.var_map[u] = idx
            if vtype:
                self.var_types[u] = vtype
            elif u.endswith("$"):
                self.var_types[u] = "STR"
            elif u.endswith("%"):
                self.var_types[u] = "INT"
            else:
                self.var_types[u] = "INT"
        elif vtype:
            self.var_types[u] = vtype
        return self.var_map[u]

    def is_str_var(self, name):
        u = name.strip().upper().replace("::", ".")
        if u.endswith("$"):
            return True
        return self.var_types.get(u) == "STR"

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
        if -32768 <= iv <= 32767:
            self.emit_u8(OP_PUSH_INT)
            self.emit_i16(iv)
        else:
            self.emit_u8(OP_PUSH_I32)
            self.emit_i32(iv)

    def emit_load_var(self, name):
        self.emit_u8(OP_LOAD_VAR)
        self.emit_u16(self.get_var_id(name))

    def emit_store_var(self, name):
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(self.get_var_id(name))

    def emit_f32(self, val):
        self.bytecode.extend(struct.pack("<f", float(val)))

    def emit_str(self, s):
        b = s.encode("utf-8", errors="replace")[:254]
        self.emit_u8(OP_PUSH_STR)
        self.emit_u8(len(b))
        self.bytecode.extend(b)

    def emit_jump(self, op, target_label, src_line=0):
        self.emit_u8(op)
        fix_pos = len(self.bytecode)
        self.emit_u16(0)
        self.fixups.append((fix_pos, str(target_label).upper(), src_line))

    # --------------------------------------------------------------------------
    # Tokenizer & Expression Compiler
    # --------------------------------------------------------------------------
    def tokenize_expr(self, expr_str):
        tokens = []
        i = 0
        n = len(expr_str)
        while i < n:
            ch = expr_str[i]
            if ch in (" ", "\t"):
                i += 1
                continue
            if ch in ('"', "'"):
                q = ch
                i += 1
                buf = []
                while i < n:
                    if expr_str[i] == q:
                        if i + 1 < n and expr_str[i + 1] == q:
                            buf.append(q)
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(expr_str[i])
                    i += 1
                tokens.append(("STR", "".join(buf)))
                continue
            if expr_str[i:i + 2] in ("<=", ">=", "<>", "!=", "=="):
                op2 = expr_str[i:i + 2]
                if op2 == "!=":
                    op2 = "<>"
                elif op2 == "==":
                    op2 = "="
                tokens.append(("OP", op2))
                i += 2
                continue
            if ch in "+-*/^=<>(),;":
                tokens.append(("OP", ch))
                i += 1
                continue
            if ch.isdigit() or (ch == "." and i + 1 < n and expr_str[i + 1].isdigit()):
                j = i
                has_dot = False
                while j < n and (expr_str[j].isdigit() or expr_str[j] == "."):
                    if expr_str[j] == ".":
                        has_dot = True
                    j += 1
                num_s = expr_str[i:j]
                if j < n and expr_str[j] == "%":
                    j += 1
                if has_dot:
                    tokens.append(("FLOAT", float(num_s)))
                else:
                    tokens.append(("INT", int(num_s)))
                i = j
                continue
            if ch.isalpha() or ch in ("_", "$", "%"):
                j = i
                while j < n and (expr_str[j].isalnum() or expr_str[j] in ("_", "$", "%", ":")):
                    j += 1
                ident = expr_str[i:j].upper().replace("::", ".")
                i = j
                if ident in ("AND", "OR", "XOR", "NOT", "MOD"):
                    tokens.append(("OP", ident))
                elif ident in self.constants:
                    c_type, c_val = self.constants[ident]
                    tokens.append((c_type, c_val))
                else:
                    tokens.append(("IDENT", ident))
                continue
            i += 1
        return tokens

    def compile_expr(self, expr_str):
        tokens = self.tokenize_expr(expr_str)
        if not tokens:
            self.emit_push_int(0)
            return
        self._pos = 0
        self._tokens = tokens
        self._parse_or()

    def _peek(self):
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return (None, None)

    def _consume(self):
        t = self._peek()
        self._pos += 1
        return t

    def _parse_or(self):
        self._parse_and()
        while self._peek() in (("OP", "OR"), ("OP", "XOR")):
            _, op = self._consume()
            self._parse_and()
            self.emit_u8(OP_OR if op == "OR" else OP_XOR)

    def _parse_and(self):
        self._parse_not()
        while self._peek() == ("OP", "AND"):
            self._consume()
            self._parse_not()
            self.emit_u8(OP_AND)

    def _parse_not(self):
        if self._peek() == ("OP", "NOT"):
            self._consume()
            self._parse_not()
            self.emit_u8(OP_NOT)
        else:
            self._parse_cmp()

    def _parse_cmp(self):
        self._parse_add()
        while self._peek()[0] == "OP" and self._peek()[1] in ("=", "<>", "<", ">", "<=", ">="):
            _, op = self._consume()
            self._parse_add()
            op_map = {
                "=": OP_EQ,
                "<>": OP_NEQ,
                "<": OP_LT,
                ">": OP_GT,
                "<=": OP_LE,
                ">=": OP_GE,
            }
            self.emit_u8(op_map[op])

    def _parse_add(self):
        self._parse_mul()
        while self._peek()[0] == "OP" and self._peek()[1] in ("+", "-"):
            _, op = self._consume()
            self._parse_mul()
            self.emit_u8(OP_ADD if op == "+" else OP_SUB)

    def _parse_mul(self):
        self._parse_unary()
        while self._peek()[0] == "OP" and self._peek()[1] in ("*", "/", "MOD"):
            _, op = self._consume()
            self._parse_unary()
            if op == "*":
                self.emit_u8(OP_MUL)
            elif op == "/":
                self.emit_u8(OP_DIV)
            else:
                self.emit_u8(OP_MOD)

    def _parse_unary(self):
        if self._peek() == ("OP", "-"):
            self._consume()
            self.emit_push_int(0)
            self._parse_unary()
            self.emit_u8(OP_SUB)
            return
        if self._peek() == ("OP", "+"):
            self._consume()
            self._parse_unary()
            return
        self._parse_primary()

    def _parse_primary(self):
        ttype, tval = self._peek()
        if ttype == "INT":
            self._consume()
            self.emit_push_int(tval)
            return
        if ttype == "FLOAT":
            self._consume()
            self.emit_u8(OP_PUSH_FLOAT)
            self.emit_f32(tval)
            return
        if ttype == "STR":
            self._consume()
            self.emit_str(tval)
            return
        if ttype == "OP" and tval == "(":
            self._consume()
            self._parse_or()
            if self._peek() == ("OP", ")"):
                self._consume()
            return
        if ttype == "IDENT":
            self._consume()
            ident = tval
            if ident == "COMMAND$":
                self.emit_u8(OP_COMMAND_STR)
                return
            if ident == "DATE$":
                self.emit_str(datetime.now().strftime("%d-%b-%Y").upper())
                return
            if ident == "TIME$" and self._peek() != ("OP", "("):
                self.emit_push_int(0)
                self.emit_u8(OP_TIME_STR)
                return

            # Check function call or array access
            if self._peek() == ("OP", "("):
                self._consume()
                args = []
                if self._peek() != ("OP", ")"):
                    while True:
                        start_p = self._pos
                        depth = 0
                        while self._pos < len(self._tokens):
                            tk = self._tokens[self._pos]
                            if tk == ("OP", "("):
                                depth += 1
                            elif tk == ("OP", ")"):
                                if depth == 0:
                                    break
                                depth -= 1
                            elif tk == ("OP", ",") and depth == 0:
                                break
                            self._pos += 1
                        args.append(self._tokens[start_p:self._pos])
                        if self._peek() == ("OP", ","):
                            self._consume()
                        else:
                            break
                if self._peek() == ("OP", ")"):
                    self._consume()

                if self._emit_builtin_func(ident, args):
                    return

                # Check user-defined FUNCTION or DEF FN
                if ident in self.fn_defs:
                    fn_info = self.fn_defs[ident]
                    saved_tokens, saved_pos = self._tokens, self._pos
                    for p_idx, arg_toks in enumerate(args):
                        if p_idx < len(fn_info["params"]):
                            self._tokens = arg_toks
                            self._pos = 0
                            self._parse_or()
                            self.emit_store_var(fn_info["params"][p_idx])
                    self._tokens, self._pos = saved_tokens, saved_pos
                    self.emit_jump(OP_CALL, fn_info["label"])
                    self.emit_load_var(fn_info["ret_var"])
                    return

                # Array load
                saved_tokens, saved_pos = self._tokens, self._pos
                if args:
                    self._tokens = args[0]
                    self._pos = 0
                    self._parse_or()
                else:
                    self.emit_push_int(0)
                self._tokens, self._pos = saved_tokens, saved_pos
                self.emit_u8(OP_LOAD_ARR)
                self.emit_u16(self.get_var_id(ident))
                return

            # Plain variable
            self.emit_load_var(ident)
            return

        self._consume()
        self.emit_push_int(0)

    def _emit_arg_tokens(self, arg_toks):
        saved_tokens, saved_pos = self._tokens, self._pos
        self._tokens = arg_toks
        self._pos = 0
        self._parse_or()
        self._tokens, self._pos = saved_tokens, saved_pos

    def _emit_builtin_func(self, ident, args):
        one_arg_ops = {
            "INT": OP_INT,
            "LEN": OP_LEN,
            "CHR$": OP_CHR,
            "VAL": OP_VAL,
            "STR$": OP_STR,
            "ASCII": OP_ASCII,
            "SYS": OP_SYS,
            "RND": OP_RND,
            "TIME$": OP_TIME_STR,
            "INKEY$": OP_INKEY,
        }
        if ident in one_arg_ops:
            if args:
                self._emit_arg_tokens(args[0])
            else:
                self.emit_push_int(0)
            self.emit_u8(one_arg_ops[ident])
            return True
        if ident in ("LEFT$", "RIGHT$"):
            for a in args[:2]:
                self._emit_arg_tokens(a)
            self.emit_u8({"LEFT$": OP_LEFT, "RIGHT$": OP_RIGHT}[ident])
            return True
        if ident == "MID$":
            for a in args[:2]:
                self._emit_arg_tokens(a)
            if len(args) >= 3:
                self._emit_arg_tokens(args[2])
            else:
                self.emit_push_int(255)
            self.emit_u8(OP_MID)
            return True
        if ident == "SEG$":
            # VAX BASIC SEG$(s$, start, end) -> MID$(s$, start, end - start + 1)
            self._emit_arg_tokens(args[0])
            self._emit_arg_tokens(args[1])
            self._emit_arg_tokens(args[2])
            self._emit_arg_tokens(args[1])
            self.emit_u8(OP_SUB)
            self.emit_push_int(1)
            self.emit_u8(OP_ADD)
            self.emit_u8(OP_MID)
            return True
        if ident in ("INSTR", "POS"):
            if len(args) == 2:
                self.emit_push_int(1)
                self._emit_arg_tokens(args[0])
                self._emit_arg_tokens(args[1])
            else:
                for a in args[:3]:
                    self._emit_arg_tokens(a)
            self.emit_u8(OP_INSTR)
            return True
        return False

    # --------------------------------------------------------------------------
    # Two-Pass Source Preprocessing (SUB, FUNCTION, DEF, RECORD, Line Numbers)
    # --------------------------------------------------------------------------
    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()

        # Pass 1: Collect RECORD definitions, CONSTANT declarations, and SUB/FUNCTION signatures
        in_record = None
        i = 0
        while i < len(raw_lines):
            s = self._strip_comment(raw_lines[i]).strip()
            s = self._strip_lineno_and_label(s)[1]
            up = s.upper()
            if up.startswith("RECORD "):
                rec_name = up.split()[1].strip()
                in_record = rec_name
                self.record_defs[in_record] = []
                i += 1
                continue
            if up.startswith("END RECORD"):
                in_record = None
                i += 1
                continue
            if in_record is not None:
                self._parse_record_field(in_record, s)
                i += 1
                continue
            if up.startswith("SUB "):
                m = re.match(r"^SUB\s+([A-Za-z0-9_$%]+)\s*(?:\(([^)]*)\))?", s, re.IGNORECASE)
                if m:
                    sname = m.group(1).upper()
                    params = [self._extract_param_name(p) for p in (m.group(2) or "").split(",") if p.strip()]
                    self.sub_defs[sname] = {"label": f"__SUB_{sname}", "params": params}
            elif up.startswith("FUNCTION "):
                m = re.match(
                    r"^FUNCTION\s+(?:LONG|WORD|BYTE|INTEGER|SINGLE|DOUBLE|REAL|GFLOAT|DECIMAL|STRING)\s+([A-Za-z0-9_$%]+)\s*(?:\(([^)]*)\))?",
                    s,
                    re.IGNORECASE,
                )
                if not m:
                    m = re.match(r"^FUNCTION\s+([A-Za-z0-9_$%]+)\s*(?:\(([^)]*)\))?", s, re.IGNORECASE)
                if m:
                    fname = m.group(1).upper()
                    params = [self._extract_param_name(p) for p in (m.group(2) or "").split(",") if p.strip()]
                    if "STRING" in up.split("(")[0] or fname.endswith("$"):
                        self.get_var_id(fname, "STR")
                    self.fn_defs[fname] = {"label": f"__FN_{fname}", "ret_var": fname, "params": params}
            elif up.startswith("DEF "):
                m = re.match(
                    r"^DEF\s+(?:(?:LONG|WORD|BYTE|INTEGER|SINGLE|DOUBLE|REAL|STRING)\s+)?([A-Za-z0-9_$%]+)\s*(?:\(([^)]*)\))?\s*(?:=\s*(.+))?$",
                    s,
                    re.IGNORECASE,
                )
                if m:
                    fname = m.group(1).upper()
                    params = [self._extract_param_name(p) for p in (m.group(2) or "").split(",") if p.strip()]
                    if "STRING" in up.split("(")[0] or fname.endswith("$"):
                        self.get_var_id(fname, "STR")
                    self.fn_defs[fname] = {"label": f"__FN_{fname}", "ret_var": fname, "params": params}
            elif up.startswith("DATA "):
                items = [x.strip() for x in self._split_outside_quotes(s[5:].strip(), ",") if x.strip()]
                for it in items:
                    if (it.startswith('"') and it.endswith('"')) or (it.startswith("'") and it.endswith("'")):
                        self.data_pool.append(("STR", it[1:-1]))
                    elif "." in it:
                        self.data_pool.append(("FLOAT", float(it)))
                    else:
                        self.data_pool.append(("INT", int(it.rstrip("%"))))
            i += 1

        if self.data_pool:
            self._emit_init_data()

        # Pass 2: Emit bytecode for statements
        for idx, raw in enumerate(raw_lines, start=1):
            self.listing_lines.append((idx, len(self.bytecode), raw.rstrip("\r\n")))
            cleaned = self._strip_comment(raw).strip()
            if not cleaned:
                continue
            lbl, stmt = self._strip_lineno_and_label(cleaned)
            if lbl:
                self.labels[lbl.upper()] = len(self.bytecode)
            if not stmt:
                continue
            self._compile_stmt(stmt, idx)

        self.emit_u8(OP_HALT)

        # Resolve local jump fixups
        for fix_pos, target_lbl, src_line in self.fixups:
            if target_lbl in self.labels:
                addr = self.labels[target_lbl]
                self.bytecode[fix_pos] = addr & 0xFF
                self.bytecode[fix_pos + 1] = (addr >> 8) & 0xFF

    def _strip_comment(self, line):
        in_q = None
        for idx, ch in enumerate(line):
            if ch in ('"', "'"):
                if in_q is None:
                    in_q = ch
                elif in_q == ch:
                    in_q = None
            elif ch == "!" and in_q is None:
                return line[:idx]
        return line

    def _strip_lineno_and_label(self, s):
        lbl = None
        m_num = re.match(r"^(\d+)\s*(.*)$", s)
        if m_num:
            lbl = m_num.group(1)
            s = m_num.group(2).strip()
        m_lbl = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):(?!:)\s*(.*)$", s)
        if m_lbl and not s.upper().startswith(("HTTP:", "SYS$")):
            lbl = m_lbl.group(1).upper()
            s = m_lbl.group(2).strip()
        return lbl, s

    def _extract_param_name(self, param_spec):
        tokens = param_spec.strip().split()
        if not tokens:
            return ""
        name = tokens[-1].upper().rstrip("()")
        if any(t.upper() == "STRING" for t in tokens[:-1]):
            self.get_var_id(name, "STR")
        elif any(t.upper() in ("SINGLE", "DOUBLE", "REAL", "GFLOAT", "DECIMAL") for t in tokens[:-1]):
            self.get_var_id(name, "FLOAT")
        else:
            self.get_var_id(name, "INT")
        return name

    def _parse_record_field(self, rec_name, s):
        m = re.match(r"^(LONG|WORD|BYTE|INTEGER|SINGLE|DOUBLE|REAL|GFLOAT|DECIMAL|STRING)\s+([A-Za-z0-9_$%]+)", s, re.IGNORECASE)
        if m:
            ftype_kw = m.group(1).upper()
            fname = m.group(2).upper()
            vtype = "STR" if ftype_kw == "STRING" else ("FLOAT" if ftype_kw in ("SINGLE", "DOUBLE", "REAL", "GFLOAT", "DECIMAL") else "INT")
            self.record_defs[rec_name].append((fname, vtype))

    def _compile_stmt(self, stmt, lineno):
        stmt = stmt.strip()
        if not stmt:
            return

        # Support backslash multi-statement separator outside quotes
        parts = self._split_outside_quotes(stmt, "\\")
        if len(parts) > 1:
            for p in parts:
                self._compile_stmt(p, lineno)
            return

        up = stmt.upper()

        # Directives and non-executable declarations
        if up.startswith("REM ") or up == "REM":
            return
        if up.startswith("%IDENT"):
            m = re.search(r'["\']([^"\']+)["\']', stmt)
            if m:
                self.ident = m.group(1)
            return
        if up.startswith("%TITLE"):
            m = re.search(r'["\']([^"\']+)["\']', stmt)
            if m:
                self.title = m.group(1)
            return
        if up.startswith("OPTION "):
            return
        if up.startswith("PROGRAM "):
            pname = stmt.split(None, 1)[1].strip().upper()
            if self.module_name == "MAIN" and pname:
                self.module_name = pname[:16]
            return
        if up == "END PROGRAM" or up.startswith("END PROGRAM "):
            self.emit_u8(OP_HALT)
            return
        if up.startswith("RECORD "):
            self.ctrl_stack.append({"type": "RECORD"})
            return
        if up.startswith("END RECORD"):
            if self.ctrl_stack and self.ctrl_stack[-1]["type"] == "RECORD":
                self.ctrl_stack.pop()
            return
        if self.ctrl_stack and self.ctrl_stack[-1]["type"] == "RECORD":
            return
        if up.startswith("EXTERNAL "):
            return

        # DECLARE statements
        if up.startswith("DECLARE "):
            self._compile_declare(stmt[8:].strip())
            return

        # COMMON / MAP statements
        if up.startswith("COMMON ") or up.startswith("MAP "):
            self._compile_map_or_common(stmt)
            return

        # DIM statement
        if up.startswith("DIM "):
            self._compile_dim(stmt[4:].strip())
            return

        # SUB / END SUB / SUBEXIT
        if up.startswith("SUB "):
            m = re.match(r"^SUB\s+([A-Za-z0-9_$%]+)", stmt, re.IGNORECASE)
            if m:
                sname = m.group(1).upper()
                end_lbl = f"__ENDSUB_{sname}"
                self.emit_jump(OP_JMP, end_lbl, lineno)
                self.labels[f"__SUB_{sname}"] = len(self.bytecode)
                self.ctrl_stack.append({"type": "SUB", "name": sname, "end_lbl": end_lbl})
            return
        if up in ("SUBEXIT", "EXIT SUB"):
            self.emit_u8(OP_RET)
            return
        if up == "END SUB" or up.startswith("END SUB "):
            self.emit_u8(OP_RET)
            if self.ctrl_stack and self.ctrl_stack[-1]["type"] == "SUB":
                top = self.ctrl_stack.pop()
                self.labels[top["end_lbl"]] = len(self.bytecode)
            return

        # FUNCTION / DEF / END FUNCTION / END DEF
        if up.startswith("FUNCTION ") or up.startswith("DEF "):
            is_def = up.startswith("DEF ")
            m = re.match(
                r"^(?:FUNCTION|DEF)\s+(?:(?:LONG|WORD|BYTE|INTEGER|SINGLE|DOUBLE|REAL|GFLOAT|DECIMAL|STRING)\s+)?([A-Za-z0-9_$%]+)\s*(?:\(([^)]*)\))?\s*(?:=\s*(.+))?$",
                stmt,
                re.IGNORECASE,
            )
            if m:
                fname = m.group(1).upper()
                inline_expr = m.group(3)
                end_lbl = f"__ENDFN_{fname}"
                self.emit_jump(OP_JMP, end_lbl, lineno)
                self.labels[f"__FN_{fname}"] = len(self.bytecode)
                if inline_expr:
                    self.compile_expr(inline_expr)
                    self.emit_store_var(fname)
                    self.emit_u8(OP_RET)
                    self.labels[end_lbl] = len(self.bytecode)
                else:
                    self.ctrl_stack.append({"type": "FN", "name": fname, "end_lbl": end_lbl})
            return
        if up in ("FNEXIT", "EXIT FUNCTION", "EXIT DEF"):
            self.emit_u8(OP_RET)
            return
        if up in ("END FUNCTION", "END DEF", "FNEND") or up.startswith(("END FUNCTION ", "END DEF ")):
            self.emit_u8(OP_RET)
            if self.ctrl_stack and self.ctrl_stack[-1]["type"] == "FN":
                top = self.ctrl_stack.pop()
                self.labels[top["end_lbl"]] = len(self.bytecode)
            return

        # CALL statement
        if up.startswith("CALL "):
            rest_call = stmt[5:].strip()
            m = re.match(r"^([A-Za-z0-9_$%]+)\s*(?:\((.*)\))?$", rest_call)
            if m:
                cname = m.group(1).upper()
                arg_str = m.group(2) or ""
                args = [a.strip() for a in self._split_outside_quotes(arg_str, ",") if a.strip()]
                if cname in self.sub_defs:
                    sub_info = self.sub_defs[cname]
                    for idx_a, a_expr in enumerate(args):
                        if idx_a < len(sub_info["params"]):
                            self.compile_expr(a_expr)
                            self.emit_store_var(sub_info["params"][idx_a])
                    self.emit_jump(OP_CALL, sub_info["label"], lineno)
                else:
                    # External overlay / module call resolved by OpenVMS Linker (vmslink)
                    self.emit_u8(OP_CALL_OVL)
                    rel_off = len(self.bytecode)
                    self.emit_u16(0)
                    self.relocations.append({"offset": rel_off, "type": "CALL_OVL", "target": cname})
            return

        # SELECT / CASE / CASE ELSE / END SELECT
        if up.startswith("SELECT "):
            sel_expr = stmt[7:].strip()
            if sel_expr.upper().startswith("CASE "):
                sel_expr = sel_expr[5:].strip()
            self.select_counter += 1
            sid = self.select_counter
            sel_var = f"__SEL_VAL_{sid}"
            if any(q in sel_expr for q in ('"', "'", "$")):
                self.get_var_id(sel_var, "STR")
            self.compile_expr(sel_expr)
            self.emit_store_var(sel_var)
            self.ctrl_stack.append({
                "type": "SELECT",
                "id": sid,
                "var": sel_var,
                "case_idx": 0,
                "end_lbl": f"__SEL_END_{sid}",
                "next_case_lbl": None,
            })
            return

        if up.startswith("CASE "):
            sel_ctx = next((c for c in reversed(self.ctrl_stack) if c["type"] == "SELECT"), None)
            if not sel_ctx:
                return
            if sel_ctx["case_idx"] > 0:
                self.emit_jump(OP_JMP, sel_ctx["end_lbl"], lineno)
                if sel_ctx["next_case_lbl"]:
                    self.labels[sel_ctx["next_case_lbl"]] = len(self.bytecode)
            sel_ctx["case_idx"] += 1
            c_idx = sel_ctx["case_idx"]
            next_lbl = f"__SEL_{sel_ctx['id']}_CASE_{c_idx + 1}"
            sel_ctx["next_case_lbl"] = next_lbl

            case_body = stmt[5:].strip()
            if case_body.upper() == "ELSE":
                sel_ctx["next_case_lbl"] = None
                return

            clauses = [c.strip() for c in self._split_outside_quotes(case_body, ",") if c.strip()]
            for cl_i, clause in enumerate(clauses):
                m_to = re.match(r"^(.+?)\s+TO\s+(.+)$", clause, re.IGNORECASE)
                if m_to:
                    lo_e, hi_e = m_to.group(1).strip(), m_to.group(2).strip()
                    self.emit_load_var(sel_ctx["var"])
                    self.compile_expr(lo_e)
                    self.emit_u8(OP_GE)
                    self.emit_load_var(sel_ctx["var"])
                    self.compile_expr(hi_e)
                    self.emit_u8(OP_LE)
                    self.emit_u8(OP_AND)
                elif clause.upper().startswith(("=", "<>", "<=", ">=", "<", ">")):
                    for op_s, op_c in (("<=", OP_LE), (">=", OP_GE), ("<>", OP_NEQ), ("<", OP_LT), (">", OP_GT), ("=", OP_EQ)):
                        if clause.startswith(op_s):
                            rhs_e = clause[len(op_s):].strip()
                            self.emit_load_var(sel_ctx["var"])
                            self.compile_expr(rhs_e)
                            self.emit_u8(op_c)
                            break
                else:
                    self.emit_load_var(sel_ctx["var"])
                    self.compile_expr(clause)
                    self.emit_u8(OP_EQ)
                if cl_i > 0:
                    self.emit_u8(OP_OR)
            self.emit_jump(OP_JMP_FALSE, next_lbl, lineno)
            return

        if up.startswith("END SELECT"):
            if self.ctrl_stack and self.ctrl_stack[-1]["type"] == "SELECT":
                sel_ctx = self.ctrl_stack.pop()
                if sel_ctx["next_case_lbl"]:
                    self.labels[sel_ctx["next_case_lbl"]] = len(self.bytecode)
                self.labels[sel_ctx["end_lbl"]] = len(self.bytecode)
            return

        # WHEN ERROR IN ... USE ... END WHEN
        if up.startswith("WHEN ERROR IN"):
            self.loop_counter += 1
            wid = self.loop_counter
            use_lbl = f"__WHEN_USE_{wid}"
            end_lbl = f"__WHEN_END_{wid}"
            self.emit_jump(OP_ON_ERROR, use_lbl, lineno)
            self.emit_u16(self.get_var_id("ERR"))
            self.ctrl_stack.append({"type": "WHEN", "use_lbl": use_lbl, "end_lbl": end_lbl})
            return
        if up == "USE":
            when_ctx = next((c for c in reversed(self.ctrl_stack) if c["type"] == "WHEN"), None)
            if when_ctx:
                self.emit_u8(OP_ON_ERROR)
                self.emit_u16(0)
                self.emit_u16(0)
                self.emit_jump(OP_JMP, when_ctx["end_lbl"], lineno)
                self.labels[when_ctx["use_lbl"]] = len(self.bytecode)
            return
        if up.startswith("END WHEN"):
            if self.ctrl_stack and self.ctrl_stack[-1]["type"] == "WHEN":
                when_ctx = self.ctrl_stack.pop()
                self.emit_u8(OP_ON_ERROR)
                self.emit_u16(0)
                self.emit_u16(0)
                self.labels[when_ctx["end_lbl"]] = len(self.bytecode)
            return

        # ON ERROR GOTO / RESUME
        if up.startswith("ON ERROR GOTO "):
            tgt = stmt[14:].strip().upper()
            if tgt == "0":
                self.emit_u8(OP_ON_ERROR)
                self.emit_u16(0)
                self.emit_u16(0)
            else:
                self.emit_jump(OP_ON_ERROR, tgt, lineno)
                self.emit_u16(self.get_var_id("ERR"))
            return
        if up.startswith("RESUME"):
            rest_r = stmt[6:].strip()
            self.emit_u8(OP_RESUME)
            if rest_r:
                fix_p = len(self.bytecode)
                self.emit_u16(0)
                self.fixups.append((fix_p, rest_r.upper(), lineno))
            else:
                self.emit_u16(0)
            return

        # IF / ELSEIF / ELSE / END IF
        if up.startswith("IF "):
            m_then = re.search(r"\bTHEN\b", stmt, re.IGNORECASE)
            if not m_then:
                return
            cond_str = stmt[3:m_then.start()].strip()
            after_then = stmt[m_then.end():].strip()
            self.loop_counter += 1
            if_id = self.loop_counter
            if not after_then:
                next_branch = f"__IF_{if_id}_BR_1"
                end_if = f"__IF_{if_id}_END"
                self.compile_expr(cond_str)
                self.emit_jump(OP_JMP_FALSE, next_branch, lineno)
                self.ctrl_stack.append({
                    "type": "IF",
                    "id": if_id,
                    "br_idx": 1,
                    "next_lbl": next_branch,
                    "end_lbl": end_if,
                })
                return
            # Single-line IF ... THEN ... [ELSE ...]
            else_parts = self._split_keyword_outside_quotes(after_then, "ELSE")
            then_part = else_parts[0].strip()
            else_part = else_parts[1].strip() if len(else_parts) > 1 else None
            else_lbl = f"__SL_IF_ELSE_{if_id}"
            end_lbl = f"__SL_IF_END_{if_id}"
            self.compile_expr(cond_str)
            self.emit_jump(OP_JMP_FALSE, else_lbl if else_part else end_lbl, lineno)
            if then_part.isdigit():
                self.emit_jump(OP_JMP, then_part, lineno)
            else:
                self._compile_stmt(then_part, lineno)
            if else_part:
                self.emit_jump(OP_JMP, end_lbl, lineno)
                self.labels[else_lbl] = len(self.bytecode)
                if else_part.isdigit():
                    self.emit_jump(OP_JMP, else_part, lineno)
                else:
                    self._compile_stmt(else_part, lineno)
            self.labels[end_lbl] = len(self.bytecode)
            return

        if up.startswith("ELSEIF ") or up.startswith("ELSE IF "):
            if_ctx = next((c for c in reversed(self.ctrl_stack) if c["type"] == "IF"), None)
            if not if_ctx:
                return
            self.emit_jump(OP_JMP, if_ctx["end_lbl"], lineno)
            if if_ctx["next_lbl"]:
                self.labels[if_ctx["next_lbl"]] = len(self.bytecode)
            if_ctx["br_idx"] += 1
            next_branch = f"__IF_{if_ctx['id']}_BR_{if_ctx['br_idx']}"
            if_ctx["next_lbl"] = next_branch
            m_then = re.search(r"\bTHEN\b", stmt, re.IGNORECASE)
            cond_s = stmt.split(None, 1)[1]
            if cond_s.upper().startswith("IF "):
                cond_s = cond_s[3:]
            if m_then:
                cond_s = stmt[stmt.upper().find("IF") + 2:m_then.start()].strip()
            self.compile_expr(cond_s)
            self.emit_jump(OP_JMP_FALSE, next_branch, lineno)
            return

        if up == "ELSE":
            if_ctx = next((c for c in reversed(self.ctrl_stack) if c["type"] == "IF"), None)
            if not if_ctx:
                return
            self.emit_jump(OP_JMP, if_ctx["end_lbl"], lineno)
            if if_ctx["next_lbl"]:
                self.labels[if_ctx["next_lbl"]] = len(self.bytecode)
                if_ctx["next_lbl"] = None
            return

        if up in ("END IF", "ENDIF"):
            if self.ctrl_stack and self.ctrl_stack[-1]["type"] == "IF":
                if_ctx = self.ctrl_stack.pop()
                if if_ctx["next_lbl"]:
                    self.labels[if_ctx["next_lbl"]] = len(self.bytecode)
                self.labels[if_ctx["end_lbl"]] = len(self.bytecode)
            return

        # FOR / WHILE / UNTIL / NEXT / ITERATE / EXIT
        if up.startswith("FOR "):
            m = re.match(r"^FOR\s+([A-Za-z0-9_$%]+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$", stmt, re.IGNORECASE)
            if m:
                vname = m.group(1).upper()
                start_e, end_e, step_e = m.group(2), m.group(3), m.group(4) or "1"
                self.loop_counter += 1
                lid = self.loop_counter
                top_lbl = f"__FOR_TOP_{lid}"
                step_lbl = f"__FOR_STEP_{lid}"
                end_lbl = f"__FOR_END_{lid}"
                self.compile_expr(start_e)
                self.emit_store_var(vname)
                self.labels[top_lbl] = len(self.bytecode)
                self.emit_load_var(vname)
                self.compile_expr(end_e)
                if step_e.strip().startswith("-"):
                    self.emit_u8(OP_GE)
                else:
                    self.emit_u8(OP_LE)
                self.emit_jump(OP_JMP_FALSE, end_lbl, lineno)
                self.ctrl_stack.append({
                    "type": "FOR",
                    "var": vname,
                    "step": step_e,
                    "top_lbl": top_lbl,
                    "step_lbl": step_lbl,
                    "end_lbl": end_lbl,
                })
            return

        if up.startswith("WHILE "):
            cond_e = stmt[6:].strip()
            self.loop_counter += 1
            lid = self.loop_counter
            top_lbl = f"__WHILE_TOP_{lid}"
            end_lbl = f"__WHILE_END_{lid}"
            self.labels[top_lbl] = len(self.bytecode)
            self.compile_expr(cond_e)
            self.emit_jump(OP_JMP_FALSE, end_lbl, lineno)
            self.ctrl_stack.append({"type": "WHILE", "top_lbl": top_lbl, "step_lbl": top_lbl, "end_lbl": end_lbl})
            return

        if up.startswith("UNTIL "):
            cond_e = stmt[6:].strip()
            self.loop_counter += 1
            lid = self.loop_counter
            top_lbl = f"__UNTIL_TOP_{lid}"
            end_lbl = f"__UNTIL_END_{lid}"
            self.labels[top_lbl] = len(self.bytecode)
            self.compile_expr(cond_e)
            self.emit_jump(OP_JMP_FALSE, f"__UNTIL_BODY_{lid}", lineno)
            self.emit_jump(OP_JMP, end_lbl, lineno)
            self.labels[f"__UNTIL_BODY_{lid}"] = len(self.bytecode)
            self.ctrl_stack.append({"type": "UNTIL", "top_lbl": top_lbl, "step_lbl": top_lbl, "end_lbl": end_lbl})
            return

        if up == "ITERATE" or up.startswith("ITERATE "):
            loop_ctx = next((c for c in reversed(self.ctrl_stack) if c["type"] in ("FOR", "WHILE", "UNTIL")), None)
            if loop_ctx:
                self.emit_jump(OP_JMP, loop_ctx["step_lbl"], lineno)
            return

        if up.startswith("EXIT ") and up not in ("EXIT SUB", "EXIT FUNCTION", "EXIT DEF"):
            loop_ctx = next((c for c in reversed(self.ctrl_stack) if c["type"] in ("FOR", "WHILE", "UNTIL")), None)
            if loop_ctx:
                self.emit_jump(OP_JMP, loop_ctx["end_lbl"], lineno)
            return

        if up == "NEXT" or up.startswith("NEXT "):
            loop_ctx = next((c for c in reversed(self.ctrl_stack) if c["type"] in ("FOR", "WHILE", "UNTIL")), None)
            if not loop_ctx:
                return
            self.ctrl_stack.remove(loop_ctx)
            if loop_ctx["type"] == "FOR":
                self.labels[loop_ctx["step_lbl"]] = len(self.bytecode)
                self.emit_load_var(loop_ctx["var"])
                self.compile_expr(loop_ctx["step"])
                self.emit_u8(OP_ADD)
                self.emit_store_var(loop_ctx["var"])
            self.emit_jump(OP_JMP, loop_ctx["top_lbl"], lineno)
            self.labels[loop_ctx["end_lbl"]] = len(self.bytecode)
            return

        # GOTO / GOSUB / RETURN / STOP / END
        if up.startswith("GOTO ") or up.startswith("GO TO "):
            tgt = stmt.split()[-1].upper()
            self.emit_jump(OP_JMP, tgt, lineno)
            return
        if up.startswith("GOSUB "):
            tgt = stmt.split()[-1].upper()
            self.emit_jump(OP_CALL, tgt, lineno)
            return
        if up == "RETURN":
            self.emit_u8(OP_RET)
            return
        if up in ("STOP", "END"):
            self.emit_u8(OP_HALT)
            return
        if up.startswith("SLEEP "):
            return

        # File & RMS I/O: OPEN, CLOSE, GET, PUT, DELETE, FIND, UPDATE
        if up.startswith("OPEN "):
            self._compile_open(stmt[5:].strip())
            return
        if up.startswith("CLOSE"):
            self._compile_close(stmt[5:].strip())
            return
        if up.startswith(("GET ", "PUT ", "DELETE ", "FIND ", "UPDATE ")):
            self._compile_rms_op(stmt)
            return

        # DATA / READ / RESTORE
        if up.startswith("DATA "):
            return
        if up.startswith("READ "):
            for v in [x.strip() for x in stmt[5:].split(",") if x.strip()]:
                self.emit_u8(OP_READ)
                self.emit_u16(self.get_var_id(v))
            return
        if up.startswith("RESTORE"):
            self._emit_init_data()
            return

        # PRINT / PRINT USING / PRINT #ch
        if up == "PRINT" or up.startswith("PRINT ") or up.startswith("?"):
            body = stmt[1:].strip() if up.startswith("?") else stmt[5:].strip()
            self._compile_print(body)
            return

        # INPUT / LINE INPUT / LINPUT
        if up.startswith(("INPUT ", "LINE INPUT ", "LINPUT ")):
            self._compile_input(stmt)
            return

        # Assignment: [LET] var = expr or arr(idx) = expr
        assign_s = stmt[4:].strip() if up.startswith("LET ") else stmt
        if "=" in assign_s:
            eq_p = assign_s.find("=")
            lhs = assign_s[:eq_p].strip()
            rhs = assign_s[eq_p + 1:].strip()
            m_arr = re.match(r"^([A-Za-z0-9_$%:]+)\s*\((.+)\)$", lhs)
            if m_arr:
                aname = m_arr.group(1).upper().replace("::", ".")
                idx_e = m_arr.group(2)
                self.compile_expr(rhs)
                self.compile_expr(idx_e)
                self.emit_u8(OP_STORE_ARR)
                self.emit_u16(self.get_var_id(aname))
            else:
                vname = lhs.upper().replace("::", ".")
                if any(q in rhs for q in ('"', "'", "$")):
                    self.get_var_id(vname, "STR")
                self.compile_expr(rhs)
                self.emit_store_var(vname)

    def _compile_declare(self, body):
        up = body.upper()
        # Check DECLARE <type> CONSTANT <name> = <val>
        if "CONSTANT" in up:
            m = re.search(r"CONSTANT\s+(.+)$", body, re.IGNORECASE)
            if m:
                for item in self._split_outside_quotes(m.group(1), ","):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        k = k.strip().upper()
                        v = v.strip()
                        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                            self.constants[k] = ("STR", v[1:-1])
                        elif "." in v:
                            self.constants[k] = ("FLOAT", float(v))
                        else:
                            self.constants[k] = ("INT", int(v.rstrip("%")))
            return

        parts = body.split(None, 1)
        if len(parts) < 2:
            return
        type_kw = parts[0].upper()
        var_list = [v.strip() for v in self._split_outside_quotes(parts[1], ",") if v.strip()]
        if type_kw in self.record_defs:
            for v in var_list:
                v_clean = v.split("(")[0].strip().upper()
                self.record_vars[v_clean] = type_kw
                for fname, ftype in self.record_defs[type_kw]:
                    self.get_var_id(f"{v_clean}.{fname}", ftype)
            return

        vtype = "STR" if type_kw == "STRING" else ("FLOAT" if type_kw in ("SINGLE", "DOUBLE", "REAL", "GFLOAT", "HFLOAT", "DECIMAL") else "INT")
        for v in var_list:
            if "=" in v:
                vname, init_e = [x.strip() for x in v.split("=", 1)]
                self.get_var_id(vname, vtype)
                self.compile_expr(init_e)
                self.emit_store_var(vname)
            else:
                self.get_var_id(v, vtype)

    def _compile_map_or_common(self, stmt):
        m = re.match(r"^(?:MAP|COMMON)\s*\([^)]+\)\s*(.+)$", stmt, re.IGNORECASE)
        if not m:
            return
        items = self._split_outside_quotes(m.group(1), ",")
        for it in items:
            tokens = it.strip().split()
            if len(tokens) >= 2:
                tk_type = tokens[0].upper()
                vname = tokens[1].split("=")[0].strip().upper()
                vtype = "STR" if tk_type == "STRING" else "INT"
                self.get_var_id(vname, vtype)

    def _compile_dim(self, body):
        items = self._split_outside_quotes(body, ",")
        for it in items:
            m = re.match(r"^(?:(?:LONG|WORD|BYTE|INTEGER|SINGLE|DOUBLE|STRING)\s+)?([A-Za-z0-9_$%]+)\s*\((.+)\)$", it.strip(), re.IGNORECASE)
            if m:
                aname = m.group(1).upper()
                sz_e = m.group(2)
                self.compile_expr(sz_e)
                self.emit_u8(OP_DIM_ARR)
                self.emit_u16(self.get_var_id(aname))

    def _compile_print(self, body):
        ch_num = 0
        if body.startswith("#"):
            m_ch = re.match(r"^#(\d+)%?\s*[,;]\s*(.*)$", body)
            if m_ch:
                ch_num = int(m_ch.group(1))
                body = m_ch.group(2).strip()
            else:
                ch_num = int(re.sub(r"[^0-9]", "", body) or "0")
                body = ""

        if not body:
            self.emit_str("")
            self.emit_u8(OP_PRINT_CH)
            self.emit_u8(ch_num)
            self.emit_u8(1)
            return

        if body.upper().startswith("USING "):
            rest_u = body[6:].strip()
            semi_p = rest_u.find(";")
            if semi_p == -1:
                semi_p = rest_u.find(",")
            if semi_p != -1:
                fmt_e = rest_u[:semi_p].strip()
                items_s = rest_u[semi_p + 1:].strip()
                self.compile_expr(fmt_e)
                items = [x.strip() for x in self._split_outside_quotes(items_s, ",") if x.strip()]
                for it in items:
                    self.compile_expr(it)
                self.emit_u8(OP_PRINT_USING)
                self.emit_u8(ch_num)
                self.emit_u8(len(items))
                return

        has_nl = 1
        if body.endswith(";") or body.endswith(","):
            has_nl = 0
            body = body[:-1].strip()

        parts = self._split_print_items(body)
        if not parts:
            self.emit_str("")
            self.emit_u8(OP_PRINT_CH)
            self.emit_u8(ch_num)
            self.emit_u8(has_nl)
            return

        for idx_p, p in enumerate(parts):
            is_last = idx_p == len(parts) - 1
            self.compile_expr(p)
            self.emit_u8(OP_PRINT_CH)
            self.emit_u8(ch_num)
            self.emit_u8(has_nl if is_last else 0)

    def _compile_input(self, stmt):
        up = stmt.upper()
        is_line = up.startswith(("LINE INPUT", "LINPUT"))
        body = re.sub(r"^(?:LINE\s+INPUT|LINPUT|INPUT)\s+", "", stmt, flags=re.IGNORECASE).strip()
        ch_num = 0
        if body.startswith("#"):
            m_ch = re.match(r"^#(\d+)%?\s*[,;]\s*(.*)$", body)
            if m_ch:
                ch_num = int(m_ch.group(1))
                body = m_ch.group(2).strip()
        parts = [p.strip() for p in self._split_outside_quotes(body, ",") if p.strip()]
        if not parts:
            return
        if len(parts) > 1 and (parts[0].startswith('"') or parts[0].startswith("'")):
            prompt_s = parts[0]
            var_s = parts[-1].split(";")[-1].strip()
            if ch_num == 0:
                self.compile_expr(prompt_s)
                self.emit_u8(OP_PRINT_CH)
                self.emit_u8(0)
                self.emit_u8(0)
        elif ";" in parts[0] and (parts[0].startswith('"') or parts[0].startswith("'")):
            pr_part, var_s = parts[0].rsplit(";", 1)
            var_s = var_s.strip()
            if ch_num == 0:
                self.compile_expr(pr_part.strip())
                self.emit_u8(OP_PRINT_CH)
                self.emit_u8(0)
                self.emit_u8(0)
        else:
            var_s = parts[-1]

        vid = self.get_var_id(var_s)
        if ch_num > 0:
            self.emit_u8(OP_LINE_INPUT_CH)
            self.emit_u8(ch_num)
            self.emit_u16(vid)
        else:
            self.emit_u8(OP_INPUT_S if (is_line or self.is_str_var(var_s)) else OP_INPUT_I)
            self.emit_u16(vid)

    def _emit_init_data(self):
        self.emit_u8(OP_DATA_INIT)
        self.emit_u16(len(self.data_pool))
        for dtype, val in self.data_pool:
            if dtype == "INT":
                self.emit_u8(0)
                self.emit_i32(val)
            elif dtype == "FLOAT":
                self.emit_u8(1)
                self.emit_f32(val)
            else:
                b = str(val).encode("utf-8", errors="replace")[:254]
                self.emit_u8(2)
                self.emit_u8(len(b))
                self.bytecode.extend(b)

    def _compile_open(self, body):
        up = body.upper()
        m_ch = re.search(r"(?:AS\s+FILE|AS)\s+#?(\d+)%?", body, re.IGNORECASE)
        ch_num = int(m_ch.group(1)) if m_ch else 1
        fname_part = re.split(r"\s+(?:FOR|AS)\s+", body, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        mode = 0  # INPUT/DEFAULT
        if "FOR OUTPUT" in up:
            mode = 1
        self.compile_expr(fname_part)
        self.emit_u8(OP_RMS_OPEN)
        self.emit_u8(ch_num)
        self.emit_u8(mode)
        self.emit_u8(0)  # num_vars = 0

    def _compile_close(self, body):
        ch_num = int(re.sub(r"[^0-9]", "", body) or "1")
        self.emit_u8(OP_RMS_CLOSE)
        self.emit_u8(ch_num)

    def _compile_rms_op(self, stmt):
        up = stmt.upper()
        ch_m = re.search(r"#(\d+)%?", stmt)
        ch_num = int(ch_m.group(1)) if ch_m else 1
        if up.startswith("GET "):
            self.emit_u8(OP_RMS_GET)
            self.emit_u8(ch_num)
            self.emit_u8(0)
        elif up.startswith("PUT "):
            self.emit_u8(OP_RMS_PUT)
            self.emit_u8(ch_num)

    def _split_outside_quotes(self, s, sep):
        res = []
        cur = []
        in_q = None
        depth = 0
        i = 0
        while i < len(s):
            ch = s[i]
            if ch in ('"', "'"):
                if in_q is None:
                    in_q = ch
                elif in_q == ch:
                    in_q = None
                cur.append(ch)
            elif in_q is None:
                if ch == "(":
                    depth += 1
                    cur.append(ch)
                elif ch == ")":
                    depth = max(0, depth - 1)
                    cur.append(ch)
                elif depth == 0 and s[i:i + len(sep)] == sep:
                    res.append("".join(cur))
                    cur = []
                    i += len(sep)
                    continue
                else:
                    cur.append(ch)
            else:
                cur.append(ch)
            i += 1
        res.append("".join(cur))
        return res

    def _split_keyword_outside_quotes(self, s, kw):
        in_q = None
        depth = 0
        kw_u = kw.upper()
        for i in range(len(s)):
            ch = s[i]
            if ch in ('"', "'"):
                if in_q is None:
                    in_q = ch
                elif in_q == ch:
                    in_q = None
            elif in_q is None:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth = max(0, depth - 1)
                elif depth == 0 and s[i:i + len(kw) + 2].upper() == f" {kw_u} ":
                    return [s[:i], s[i + len(kw) + 2:]]
        return [s]

    def _split_print_items(self, s):
        res = []
        cur = []
        in_q = None
        depth = 0
        for ch in s:
            if ch in ('"', "'"):
                if in_q is None:
                    in_q = ch
                elif in_q == ch:
                    in_q = None
                cur.append(ch)
            elif in_q is None:
                if ch == "(":
                    depth += 1
                    cur.append(ch)
                elif ch == ")":
                    depth = max(0, depth - 1)
                    cur.append(ch)
                elif depth == 0 and ch in (";", ","):
                    item = "".join(cur).strip()
                    if item:
                        res.append(item)
                    cur = []
                else:
                    cur.append(ch)
            else:
                cur.append(ch)
        tail = "".join(cur).strip()
        if tail:
            res.append(tail)
        return res

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX BASIC {self.VERSION}",
            "symbols": {k: v for k, v in self.labels.items() if not k.startswith("__")},
            "relocations": self.relocations,
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC VAX BASIC {self.VERSION} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                if self.title:
                    f.write(f"Title: {self.title}\n")
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


class VAXBasicInteractiveEnv:
    def __init__(self):
        self.prog_name = "NONAME"
        self.lines = {}  # line_no -> text
        self.next_auto_line = 100

    def run_repl(self):
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
        print(f"\nVAX BASIC {VAXBasicCompiler.VERSION} — VAX/VMS V5.5-2 ({now_str})\n")
        print("Ready")
        while True:
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                print("\n^C\nReady")
                continue
            if not line:
                break
            s = line.rstrip("\r\n").strip()
            if not s:
                continue
            if s in ("\x1a", "EXIT", "QUIT", "BYE") or s.upper() in ("EXIT", "QUIT", "BYE"):
                break
            m_num = re.match(r"^(\d+)\s*(.*)$", s)
            if m_num:
                lno = int(m_num.group(1))
                body = m_num.group(2)
                if not body:
                    self.lines.pop(lno, None)
                else:
                    self.lines[lno] = s
                continue

            parts = s.split(None, 1)
            verb = parts[0].upper()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if verb == "HELP":
                print("VAX BASIC V3.5 Environment Commands:")
                print("  NEW [name]          Clear workspace and set program name")
                print("  OLD <file.bas>      Load VAX BASIC source file into workspace")
                print("  SAVE [file.bas]     Save workspace to disk")
                print("  REPLACE [file.bas]  Overwrite source file on disk")
                print("  LIST                Display current program buffer")
                print("  COMPILE [file.obj]  Compile workspace to OpenVMS .OBJ module")
                print("  RUN [file.bas]      Compile, link, and execute program")
                print("  EXIT                Return to OpenVMS DCL ($)")
                print("\nReady")
                continue
            if verb == "NEW":
                self.prog_name = arg.upper() if arg else "NONAME"
                self.lines.clear()
                print("\nReady")
                continue
            if verb == "LIST":
                print(f"\n{self.prog_name}  VAX BASIC {VAXBasicCompiler.VERSION}\n")
                for k in sorted(self.lines.keys()):
                    print(self.lines[k])
                print("\nReady")
                continue
            if verb in ("SAVE", "REPLACE"):
                fname = arg if arg else f"{self.prog_name}.BAS"
                if "." not in fname:
                    fname += ".BAS"
                with open(fname, "w") as f:
                    for k in sorted(self.lines.keys()):
                        f.write(self.lines[k] + "\n")
                print(f"\nReady")
                continue
            if verb == "OLD":
                fname = arg if "." in arg else arg + ".BAS"
                if not os.path.isfile(fname):
                    print(f"%BASIC-E-FNF, file '{fname}' not found\n\nReady")
                    continue
                self.lines.clear()
                self.prog_name = os.path.splitext(os.path.basename(fname))[0].upper()
                with open(fname, "r") as f:
                    for idx, ln in enumerate(f, start=1):
                        ln_s = ln.rstrip("\r\n")
                        if ln_s.strip():
                            m_l = re.match(r"^(\d+)", ln_s.strip())
                            key = int(m_l.group(1)) if m_l else idx * 10
                            self.lines[key] = ln_s
                print("\nReady")
                continue
            if verb == "COMPILE":
                obj_file = arg if arg else f"{self.prog_name}.OBJ"
                if "." not in obj_file:
                    obj_file += ".OBJ"
                src_text = "\n".join(self.lines[k] for k in sorted(self.lines.keys()))
                comp = VAXBasicCompiler(module_name=self.prog_name)
                comp.compile_source(src_text)
                comp.write_outputs(obj_file)
                print(f"VAX BASIC {VAXBasicCompiler.VERSION}: Compiled {self.prog_name} -> {obj_file} (0 errors)\n\nReady")
                continue
            if verb in ("RUN", "RUNNH"):
                if arg:
                    fname = arg if "." in arg else arg + ".BAS"
                    if os.path.isfile(fname):
                        with open(fname, "r") as f:
                            src_text = f.read()
                    else:
                        print(f"%BASIC-E-FNF, file '{fname}' not found\n\nReady")
                        continue
                else:
                    src_text = "\n".join(self.lines[k] for k in sorted(self.lines.keys()))
                self._compile_link_run_text(src_text)
                print("\nReady")
                continue

            # Otherwise treat as immediate or unnumbered program statement
            self.lines[self.next_auto_line] = s
            self.next_auto_line += 10
        return 0

    def _compile_link_run_text(self, src_text):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vmslink_py = os.path.join(script_dir, "vmslink.py")
        with tempfile.TemporaryDirectory() as tmpd:
            obj_p = os.path.join(tmpd, f"{self.prog_name}.OBJ")
            exe_p = os.path.join(tmpd, f"{self.prog_name}.EXE")
            comp = VAXBasicCompiler(module_name=self.prog_name)
            comp.compile_source(src_text)
            comp.write_outputs(obj_p)
            subprocess.run([sys.executable, vmslink_py, "-o", exe_p, obj_p], check=True)
            subprocess.run([exe_p], check=False)


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
        env = VAXBasicInteractiveEnv()
        sys.exit(env.run_repl())

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
        env = VAXBasicInteractiveEnv()
        sys.exit(env.run_repl())

    if not os.path.isfile(in_file):
        for ext in (".BAS", ".bas", ".B32", ".b32"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%BASIC-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXBasicCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX BASIC {VAXBasicCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
