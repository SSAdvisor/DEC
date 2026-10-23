#!/usr/bin/env python3
"""
DEC VAX MACRO V05-00 Macro Assembler (vaxmacro.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Assembles 32-bit VAX MACRO source files (.MAR) into OpenVMS relocatable object
modules (.OBJ) compatible with vmslink and vms_vm, and generates optional
VAX MACRO listing files (.LST) with hexadecimal offset/byte columns, PSECT
synopses, and symbol tables.
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
OP_STR = 0x82


class VAXMacroCompiler:
    VERSION = "V05-00"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.title = self.module_name
        self.subtitle = ""
        self.ident = "V01-00"
        self.bytecode = bytearray()
        self.relocations = []
        self.labels = {}           # label -> bytecode offset
        self.fixups = []           # (offset, target_label, src_line)
        self.variables = {}        # var_name -> uint16 index
        self.asciz_labels = {}     # label -> string value
        self.data_labels = {}      # label -> list of 32-bit int values
        self.equ_symbols = {       # symbol -> int
            "SS$_NORMAL": 1,
            "STS$M_INHIB_MSG": 0x10000000,
        }
        self.psects = {
            "$CODE": "PIC,CON,REL,LCL,SHR,EXE,RD,NOWRT,LONG",
            "$DATA": "PIC,CON,REL,LCL,NOSHR,NOEXE,RD,WRT,LONG",
        }
        self.entry_points = []
        self.end_transfer = None
        self.listing_lines = []
        self.macros = {}           # macro_name -> (params, body_lines)
        self.macro_exp_counter = 0

        # Pre-allocate VAX 32-bit general registers R0..R11, AP (R12), FP (R13), SP (R14), PC (R15)
        for reg in (
            "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7",
            "R8", "R9", "R10", "R11", "AP", "FP", "SP", "PC",
            "CC_Z", "CC_N", "CC_C", "CC_V", "TMP1", "TMP2", "__LAST_PUSHED"
        ):
            self.get_var_index(reg)
        self.variables["R12"] = self.variables["AP"]
        self.variables["R13"] = self.variables["FP"]
        self.variables["R14"] = self.variables["SP"]
        self.variables["R15"] = self.variables["PC"]

    def get_var_index(self, name):
        up = name.upper().strip()
        alias = {"R12": "AP", "R13": "FP", "R14": "SP", "R15": "PC"}
        up = alias.get(up, up)
        if up not in self.variables:
            idx = len(self.variables)
            if idx >= 255:
                idx = 254
            self.variables[up] = idx
        return self.variables[up]

    # --- Low-level VM Bytecode Emitters ---
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
        # Wrap unsigned 32-bit hex literals into signed 32-bit range
        if iv > 0x7FFFFFFF:
            iv = iv - 0x100000000
        if -32768 <= iv <= 32767:
            self.emit_u8(OP_PUSH_INT)
            self.emit_i16(iv)
        else:
            self.emit_u8(OP_PUSH_I32)
            self.emit_i32(iv)

    def emit_push_s(self, s):
        b = s.encode("utf-8", errors="replace")[:254]
        self.emit_u8(OP_PUSH_STR)
        self.emit_u8(len(b))
        self.bytecode.extend(b)

    def emit_load_v(self, var_name):
        idx = self.get_var_index(var_name)
        self.emit_u8(OP_LOAD_VAR)
        self.emit_u16(idx)

    def emit_store_v(self, var_name):
        idx = self.get_var_index(var_name)
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(idx)

    def emit_dim(self, var_name, size):
        self.emit_push_int(size)
        idx = self.get_var_index(var_name)
        self.emit_u8(OP_DIM_ARR)
        self.emit_u16(idx)

    def emit_store_a(self, var_name, idx_val):
        self.emit_push_int(idx_val)
        idx = self.get_var_index(var_name)
        self.emit_u8(OP_STORE_ARR)
        self.emit_u16(idx)

    def emit_jmp(self, label, src_line=0):
        self.emit_u8(OP_JMP)
        fix_pos = len(self.bytecode)
        self.emit_u16(0)
        self.fixups.append((fix_pos, label.upper().strip(), src_line))

    def emit_jmp_z(self, label, src_line=0):
        self.emit_u8(OP_JMP_FALSE)
        fix_pos = len(self.bytecode)
        self.emit_u16(0)
        self.fixups.append((fix_pos, label.upper().strip(), src_line))

    def emit_call(self, label, src_line=0):
        self.emit_u8(OP_CALL)
        fix_pos = len(self.bytecode)
        self.emit_u16(0)
        self.fixups.append((fix_pos, label.upper().strip(), src_line))

    def update_cc_from_var(self, var_name):
        # CC_Z = (var == 0)
        self.emit_load_v(var_name)
        self.emit_push_int(0)
        self.emit_u8(OP_EQ)
        self.emit_store_v("CC_Z")
        # CC_N = (var < 0)
        self.emit_load_v(var_name)
        self.emit_push_int(0)
        self.emit_u8(OP_LT)
        self.emit_store_v("CC_N")

    def clean_operand_prefix(self, tok):
        s = tok.strip()
        # Strip VAX addressing mode prefixes: G^, W^, B^, L^, S^, I^
        m = re.match(r"^[GWBLSI]\^(.*)$", s, re.IGNORECASE)
        if m:
            s = m.group(1).strip()
        return s

    def parse_int(self, tok):
        s = self.clean_operand_prefix(tok)
        if s.startswith("#"):
            s = self.clean_operand_prefix(s[1:])
        if s.endswith("."):
            s = s[:-1]
        up = s.upper()
        if up.startswith("^M<") and up.endswith(">"):
            # Register save mask e.g. ^M<R2,R3,R4>
            inner = up[3:-1]
            mask = 0
            for r in inner.split(","):
                r = r.strip()
                if r.startswith("R") and r[1:].isdigit():
                    mask |= (1 << int(r[1:]))
            return mask
        if up.startswith("^D"):
            return int(s[2:], 10)
        if up.startswith("^O"):
            return int(s[2:], 8)
        if up.startswith("^X"):
            return int(s[2:], 16)
        if up.startswith("^B"):
            return int(s[2:], 2)
        if up.startswith("^A") and len(s) >= 4:
            delim = s[2]
            body = s[3:]
            end_p = body.find(delim)
            chars = body[:end_p] if end_p != -1 else body
            val = 0
            for idx_c, ch in enumerate(chars[:4]):
                val |= (ord(ch) & 0xFF) << (8 * idx_c)
            return val
        if up in self.equ_symbols:
            return self.equ_symbols[up]
        # Simple +/- expression in constant
        if "+" in up and not up.startswith("+"):
            parts = up.split("+", 1)
            return self.parse_int(parts[0]) + self.parse_int(parts[1])
        if "-" in up and not up.startswith("-"):
            parts = up.split("-", 1)
            return self.parse_int(parts[0]) - self.parse_int(parts[1])
        try:
            return int(s, 10)
        except ValueError:
            return 0

    def push_operand(self, op_str):
        s = self.clean_operand_prefix(op_str)
        if s.startswith("#"):
            lit = self.clean_operand_prefix(s[1:])
            up_lit = lit.upper()
            if up_lit in self.asciz_labels:
                self.emit_push_s(self.asciz_labels[up_lit])
            elif up_lit in self.equ_symbols:
                self.emit_push_int(self.equ_symbols[up_lit])
            else:
                self.emit_push_int(self.parse_int(lit))
            return

        up = s.upper()
        if up in self.equ_symbols:
            self.emit_push_int(self.equ_symbols[up])
            return
        if up in self.asciz_labels:
            self.emit_push_s(self.asciz_labels[up])
            return

        # Autoincrement / autodecrement (Rn)+ or -(Rn)
        m_auto = re.match(r"^(?:-\(([A-Z0-9]+)\)|\(([A-Z0-9]+)\)\+)$", up)
        if m_auto:
            reg = m_auto.group(1) or m_auto.group(2)
            if reg in ("SP", "R14"):
                self.emit_load_v("__LAST_PUSHED")
            else:
                self.emit_load_v(reg)
            return

        # Indexed or indirect: e.g. LAB(R1) or LAB[R1] or (R0)
        m_idx = re.match(r"^([A-Z0-9_$]*)(?:\(([A-Z0-9]+)\)|\[([A-Z0-9]+)\])$", up)
        if m_idx:
            arr_name = m_idx.group(1)
            reg_name = m_idx.group(2) or m_idx.group(3)
            if arr_name:
                self.emit_load_v(reg_name)
                idx = self.get_var_index(arr_name)
                self.emit_u8(OP_LOAD_ARR)
                self.emit_u16(idx)
                return
            else:
                self.emit_load_v(reg_name)
                return

        if up in self.data_labels and len(self.data_labels[up]) > 1:
            self.emit_push_int(0)
            idx = self.get_var_index(up)
            self.emit_u8(OP_LOAD_ARR)
            self.emit_u16(idx)
            return

        self.emit_load_v(up)

    def store_operand(self, op_str):
        s = self.clean_operand_prefix(op_str)
        up = s.upper()
        if up in ("-(SP)", "-(R14)"):
            self.emit_store_v("__LAST_PUSHED")
            return
        m_idx = re.match(r"^([A-Z0-9_$]*)(?:\(([A-Z0-9]+)\)|\[([A-Z0-9]+)\])$", up)
        if m_idx:
            arr_name = m_idx.group(1)
            reg_name = m_idx.group(2) or m_idx.group(3)
            if arr_name:
                self.emit_load_v(reg_name)
                idx = self.get_var_index(arr_name)
                self.emit_u8(OP_STORE_ARR)
                self.emit_u16(idx)
                return
        self.emit_store_v(up)
        self.update_cc_from_var(up)

    def strip_comment(self, line):
        in_delim = None
        for i, ch in enumerate(line):
            if in_delim:
                if ch == in_delim:
                    in_delim = None
            else:
                if ch in ('"', "'", "/"):
                    in_delim = ch
                elif ch == ";":
                    return line[:i]
        return line

    def extract_delimited_string(self, rest):
        s = rest.strip()
        if not s:
            return ""
        if s.upper().startswith("^A") and len(s) > 2:
            s = s[2:].strip()
        delim = s[0]
        if delim in ("/", '"', "'", "<"):
            end_delim = ">" if delim == "<" else delim
            idx = s.rfind(end_delim)
            if idx > 0:
                return s[1:idx]
            return s[1:]
        return s

    def _split_operands(self, arg):
        res = []
        cur = []
        in_delim = None
        depth = 0
        for ch in arg:
            if in_delim:
                if ch == in_delim:
                    in_delim = None
                cur.append(ch)
            else:
                if ch in ('"', "'", "/"):
                    in_delim = ch
                    cur.append(ch)
                elif ch in ("<", "(", "["):
                    depth += 1
                    cur.append(ch)
                elif ch in (">", ")", "]"):
                    depth = max(0, depth - 1)
                    cur.append(ch)
                elif ch == "," and depth == 0:
                    res.append("".join(cur).strip())
                    cur = []
                else:
                    cur.append(ch)
        tail = "".join(cur).strip()
        if tail:
            res.append(tail)
        return res

    def _preprocess_macros(self, raw_lines):
        expanded = []
        i = 0
        while i < len(raw_lines):
            raw = raw_lines[i]
            clean = self.strip_comment(raw).strip()
            parts = clean.split(None, 1)
            op = parts[0].upper() if parts else ""
            if op == ".MACRO":
                rest = parts[1].strip() if len(parts) > 1 else ""
                m_parts = re.split(r"[\s,]+", rest)
                mname = m_parts[0].upper() if m_parts else "ANON"
                mparams = [p.upper().lstrip("?") for p in m_parts[1:] if p.strip()]
                body = []
                i += 1
                while i < len(raw_lines):
                    c2 = self.strip_comment(raw_lines[i]).strip()
                    if c2.upper().startswith(".ENDM"):
                        break
                    body.append(raw_lines[i])
                    i += 1
                self.macros[mname] = (mparams, body)
                i += 1
                continue
            if op in self.macros:
                mparams, body = self.macros[op]
                arg_str = parts[1].strip() if len(parts) > 1 else ""
                actuals = self._split_operands(arg_str) if arg_str else []
                self.macro_exp_counter += 1
                for bline in body:
                    sub_line = bline
                    for pidx, pname in enumerate(mparams):
                        pval = actuals[pidx] if pidx < len(actuals) else ""
                        sub_line = re.sub(rf"\b{re.escape(pname)}\b", pval, sub_line, flags=re.IGNORECASE)
                    expanded.append(sub_line)
                i += 1
                continue
            expanded.append(raw)
            i += 1
        return expanded

    def compile_source(self, source_text):
        raw_lines = self._preprocess_macros(source_text.splitlines())

        # Pass 1: Collect .TITLE, .IDENT, .PSECT, .ENTRY, symbol assignments (SYM = VAL), .ASCIZ/.ASCID/.ASCII, .LONG/.WORD/.BYTE, .BLKL/.BLKW/.BLKB
        for raw in raw_lines:
            clean = self.strip_comment(raw).strip()
            if not clean:
                continue
            if "=" in clean and not clean.startswith("."):
                # Could be SYM = VAL or SYM == VAL
                m_eq = re.match(r"^([A-Za-z_$][A-Za-z0-9_$.]*)\s*==?\s*(.+)$", clean)
                if m_eq:
                    lhs = m_eq.group(1).strip().upper()
                    rhs = m_eq.group(2).strip()
                    self.equ_symbols[lhs] = self.parse_int(rhs)
                    continue

            label = None
            stmt = clean
            while ":" in stmt:
                cand_lbl, after = stmt.split(":", 1)
                cand_clean = cand_lbl.strip().rstrip(":")
                if re.match(r"^[A-Za-z0-9_$.]+$", cand_clean):
                    label = cand_clean.upper()
                    stmt = after.strip()
                else:
                    break

            if not stmt:
                continue
            parts = stmt.split(None, 1)
            op = parts[0].upper()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if op == ".TITLE" and arg:
                t_parts = arg.split(None, 1)
                self.title = t_parts[0].upper()
                if len(t_parts) > 1:
                    self.subtitle = t_parts[1].strip()
                if self.module_name == "MAIN":
                    self.module_name = self.title[:16]
            elif op in (".SUBTITLE", ".SBTTL") and arg:
                self.subtitle = arg
            elif op == ".IDENT" and arg:
                self.ident = self.extract_delimited_string(arg)
            elif op == ".PSECT" and arg:
                ps_parts = self._split_operands(arg)
                if ps_parts:
                    ps_name = ps_parts[0].upper()
                    ps_attrs = ",".join(p.upper() for p in ps_parts[1:]) if len(ps_parts) > 1 else "PIC,CON,REL,LCL,SHR,EXE,RD,NOWRT,LONG"
                    self.psects[ps_name] = ps_attrs
            elif op == ".ENTRY" and arg:
                e_parts = self._split_operands(arg)
                if e_parts:
                    ename = e_parts[0].upper()
                    if ename not in self.entry_points:
                        self.entry_points.append(ename)
            elif op == ".END" and arg:
                self.end_transfer = arg.split()[0].upper()
            elif op in (".ASCIZ", ".ASCII", ".ASCID", ".ASCIC"):
                s_val = self.extract_delimited_string(arg)
                if label:
                    self.asciz_labels[label] = s_val
            elif op in (".LONG", ".WORD", ".BYTE", ".ADDRESS"):
                ops = self._split_operands(arg)
                vals = []
                for x in ops:
                    if x.upper() in self.asciz_labels:
                        # .ADDRESS or descriptor pointing to a string label
                        self.asciz_labels[label] = self.asciz_labels[x.upper()]
                    else:
                        vals.append(self.parse_int(x))
                if label and vals and label not in self.asciz_labels:
                    self.data_labels[label] = vals
            elif op in (".BLKL", ".BLKW", ".BLKB", ".BLKQ"):
                cnt = self.parse_int(arg) if arg else 1
                if label:
                    self.data_labels[label] = [0] * max(1, cnt)

        # Emit startup initialization for .ASCIZ/.ASCID and .LONG/.WORD/.BYTE variables
        for lbl, sval in self.asciz_labels.items():
            self.emit_push_s(sval)
            self.emit_store_v(lbl)
        for lbl, lvals in self.data_labels.items():
            if len(lvals) == 1:
                self.emit_push_int(lvals[0])
                self.emit_store_v(lbl)
            else:
                self.emit_dim(lbl, len(lvals))
                for idx_i, v in enumerate(lvals):
                    self.emit_push_int(v)
                    self.emit_store_a(lbl, idx_i)

        # Jump to main transfer entry point if specified (.END <entry> or first .ENTRY)
        start_target = self.end_transfer or (self.entry_points[0] if self.entry_points else None)
        if start_target:
            self.emit_jmp(start_target, 0)

        # Pass 2: Assemble executable VAX instructions
        line_no = 0
        for raw in raw_lines:
            line_no += 1
            pc_before = len(self.bytecode)
            clean = self.strip_comment(raw).strip()
            if not clean:
                self.listing_lines.append((line_no, pc_before, [], raw))
                continue
            if "=" in clean and not clean.startswith(".") and re.match(r"^[A-Za-z_$][A-Za-z0-9_$.]*\s*==?", clean):
                self.listing_lines.append((line_no, pc_before, [], raw))
                continue

            while ":" in clean:
                cand_lbl, after = clean.split(":", 1)
                cand_clean = cand_lbl.strip().rstrip(":")
                if re.match(r"^[A-Za-z0-9_$.]+$", cand_clean):
                    lbl_up = cand_clean.upper()
                    self.labels[lbl_up] = len(self.bytecode)
                    clean = after.strip()
                else:
                    break

            if not clean:
                self.listing_lines.append((line_no, pc_before, [], raw))
                continue

            parts = clean.split(None, 1)
            op = parts[0].upper()
            arg = parts[1].strip() if len(parts) > 1 else ""

            self._assemble_instruction(op, arg, line_no)
            emitted = list(self.bytecode[pc_before:])
            self.listing_lines.append((line_no, pc_before, emitted[:8], raw))

        # Ensure trailing HALT
        self.emit_u8(OP_HALT)

        # Resolve local branch/call fixups
        for fix_pos, target_lbl, src_line in self.fixups:
            if target_lbl in self.labels:
                addr = self.labels[target_lbl]
                self.bytecode[fix_pos] = addr & 0xFF
                self.bytecode[fix_pos + 1] = (addr >> 8) & 0xFF

    def _assemble_instruction(self, op, arg, line_no=0):
        if op in (
            ".TITLE", ".SUBTITLE", ".SBTTL", ".IDENT", ".PSECT", ".GLOBAL", ".GLOBL",
            ".EXTERNAL", ".EXTRN", ".WEAK", ".ALIGN", ".EVEN", ".ODD", ".DSABL", ".ENABL",
            ".NOSHOW", ".SHOW", ".PAGE", ".LIBRARY", ".LINK",
            ".ASCIZ", ".ASCII", ".ASCID", ".ASCIC",
            ".LONG", ".WORD", ".BYTE", ".QUAD", ".ADDRESS",
            ".BLKL", ".BLKW", ".BLKB", ".BLKQ"
        ):
            return

        if op == ".ENTRY":
            ops = self._split_operands(arg)
            if ops:
                ename = ops[0].upper()
                self.labels[ename] = len(self.bytecode)
            return

        if op in (".END", "$EXIT_S", "HALT", "BPT"):
            self.emit_u8(OP_HALT)
            return

        if op == "NOP":
            return

        # Convenience & VMS RTL output macros
        if op in (".PRINT", "PRINT", "PRTSTR", "$PUTMSG_S"):
            if not arg:
                self.emit_push_s("")
            elif arg[0] in ("/", '"', "'", "<"):
                self.emit_push_s(self.extract_delimited_string(arg))
            else:
                ops = self._split_operands(arg)
                first_op = self.clean_operand_prefix(ops[0]).lstrip("#").upper()
                if first_op in self.asciz_labels:
                    self.emit_push_s(self.asciz_labels[first_op])
                else:
                    self.push_operand(ops[0])
            self.emit_u8(OP_PRINT)
            return

        if op == "PRTINT":
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                # PRTINT prefix_label_or_str, reg_or_var
                p0 = ops[0].strip()
                if p0[0] in ("/", '"', "'", "<"):
                    self.emit_push_s(self.extract_delimited_string(p0))
                else:
                    self.push_operand(p0)
                self.emit_u8(OP_PRINT_NO_NL)
                self.push_operand(ops[1])
                self.emit_u8(OP_PRINT)
            elif ops:
                self.push_operand(ops[0])
                self.emit_u8(OP_PRINT)
            return

        # Stack push/pop instructions (used before CALLS #n, G^LIB$PUT_OUTPUT or subroutines)
        if op in ("PUSHAL", "PUSHAB", "PUSHAW", "PUSHAQ", "PUSHL"):
            ops = self._split_operands(arg)
            if ops:
                self.push_operand(ops[0])
                self.emit_store_v("__LAST_PUSHED")
            return

        if op == "POPL":
            ops = self._split_operands(arg)
            if ops:
                self.emit_load_v("__LAST_PUSHED")
                self.store_operand(ops[0])
            return

        # Data movement instructions
        if op in ("MOVL", "MOVW", "MOVB", "MOVZBL", "MOVZWL", "MOVZBW", "MOVAL", "MOVAB", "MOVAW", "MOVAQ"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[0])
                self.store_operand(ops[1])
            return

        if op in ("MNEGL", "MNEGW", "MNEGB"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.emit_push_int(0)
                self.push_operand(ops[0])
                self.emit_u8(OP_SUB)
                self.store_operand(ops[1])
            return

        if op in ("MCOML", "MCOMW", "MCOMB"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.emit_push_int(-1)
                self.push_operand(ops[0])
                self.emit_u8(OP_SUB)
                self.store_operand(ops[1])
            return

        if op in ("CLRL", "CLRW", "CLRB", "CLRQ"):
            self.emit_push_int(0)
            self.store_operand(arg)
            return

        if op in ("INCL", "INCW", "INCB"):
            self.push_operand(arg)
            self.emit_push_int(1)
            self.emit_u8(OP_ADD)
            self.store_operand(arg)
            return

        if op in ("DECL", "DECW", "DECB"):
            self.push_operand(arg)
            self.emit_push_int(1)
            self.emit_u8(OP_SUB)
            self.store_operand(arg)
            return

        # 2-operand and 3-operand VAX arithmetic
        if op in ("ADDL2", "ADDW2", "ADDB2"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_ADD)
                self.store_operand(ops[1])
            return

        if op in ("ADDL3", "ADDW3", "ADDB3"):
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                self.push_operand(ops[0])
                self.push_operand(ops[1])
                self.emit_u8(OP_ADD)
                self.store_operand(ops[2])
            return

        if op in ("SUBL2", "SUBW2", "SUBB2"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_SUB)
                self.store_operand(ops[1])
            return

        if op in ("SUBL3", "SUBW3", "SUBB3"):
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                # VAX SUBL3 sub, min, dif -> dif = min - sub
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_SUB)
                self.store_operand(ops[2])
            return

        if op in ("MULL2", "MULW2", "MULB2"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_MUL)
                self.store_operand(ops[1])
            return

        if op in ("MULL3", "MULW3", "MULB3"):
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                self.push_operand(ops[0])
                self.push_operand(ops[1])
                self.emit_u8(OP_MUL)
                self.store_operand(ops[2])
            return

        if op in ("DIVL2", "DIVW2", "DIVB2"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_DIV)
                self.emit_u8(OP_INT)
                self.store_operand(ops[1])
            return

        if op in ("DIVL3", "DIVW3", "DIVB3"):
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                # VAX DIVL3 divr, divd, quo -> quo = int(divd / divr)
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_DIV)
                self.emit_u8(OP_INT)
                self.store_operand(ops[2])
            return

        # Bitwise instructions
        if op in ("BICL2", "BICW2", "BICB2"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_SUB)
                self.store_operand(ops[1])
            return

        if op in ("BICL3", "BICW3", "BICB3"):
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_SUB)
                self.store_operand(ops[2])
            return

        if op in ("BISL2", "BISW2", "BISB2"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_OR)
                self.store_operand(ops[1])
            return

        if op in ("BISL3", "BISW3", "BISB3"):
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_OR)
                self.store_operand(ops[2])
            return

        if op in ("XORL2", "XORW2", "XORB2"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_XOR)
                self.store_operand(ops[1])
            return

        if op in ("XORL3", "XORW3", "XORB3"):
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                self.push_operand(ops[1])
                self.push_operand(ops[0])
                self.emit_u8(OP_XOR)
                self.store_operand(ops[2])
            return

        # Compare and test instructions
        if op in ("CMPL", "CMPW", "CMPB"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[0])
                self.push_operand(ops[1])
                self.emit_u8(OP_SUB)
                self.emit_store_v("TMP1")
                self.update_cc_from_var("TMP1")
            return

        if op in ("TSTL", "TSTW", "TSTB"):
            self.push_operand(arg)
            self.emit_store_v("TMP1")
            self.update_cc_from_var("TMP1")
            return

        if op in ("BITL", "BITW", "BITB"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[0])
                self.push_operand(ops[1])
                self.emit_u8(OP_AND)
                self.emit_store_v("TMP1")
                self.update_cc_from_var("TMP1")
            return

        # Unconditional & conditional branches
        if op in ("JMP", "BRB", "BRW"):
            self.emit_jmp(self.clean_operand_prefix(arg), line_no)
            return

        if op in ("BEQL", "BEQLU", "BEQ"):
            self.emit_load_v("CC_Z")
            self.emit_push_int(0)
            self.emit_u8(OP_EQ)
            self.emit_jmp_z(self.clean_operand_prefix(arg), line_no)
            return

        if op in ("BNEQ", "BNEQU", "BNE"):
            self.emit_load_v("CC_Z")
            self.emit_jmp_z(self.clean_operand_prefix(arg), line_no)
            return

        if op in ("BLSS", "BLSSU", "BLT"):
            self.emit_load_v("CC_N")
            self.emit_push_int(0)
            self.emit_u8(OP_EQ)
            self.emit_jmp_z(self.clean_operand_prefix(arg), line_no)
            return

        if op in ("BGEQ", "BGEQU", "BGE", "BCC"):
            self.emit_load_v("CC_N")
            self.emit_jmp_z(self.clean_operand_prefix(arg), line_no)
            return

        if op in ("BLEQ", "BLEQU", "BLE"):
            self.emit_load_v("CC_Z")
            self.emit_load_v("CC_N")
            self.emit_u8(OP_OR)
            self.emit_push_int(0)
            self.emit_u8(OP_EQ)
            self.emit_jmp_z(self.clean_operand_prefix(arg), line_no)
            return

        if op in ("BGTR", "BGTRU", "BGT"):
            self.emit_load_v("CC_Z")
            self.emit_load_v("CC_N")
            self.emit_u8(OP_OR)
            self.emit_jmp_z(self.clean_operand_prefix(arg), line_no)
            return

        if op == "BLBS":
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[0])
                self.emit_push_int(2)
                self.emit_u8(OP_MOD)
                self.emit_push_int(0)
                self.emit_u8(OP_EQ)
                self.emit_jmp_z(self.clean_operand_prefix(ops[1]), line_no)
            return

        if op == "BLBC":
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                self.push_operand(ops[0])
                self.emit_push_int(2)
                self.emit_u8(OP_MOD)
                self.emit_jmp_z(self.clean_operand_prefix(ops[1]), line_no)
            return

        # VAX Loop instructions: SOBGTR, SOBGEQ, AOBLSS, AOBLEQ
        if op == "SOBGTR":
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                reg, lbl = ops[0], self.clean_operand_prefix(ops[1])
                self.push_operand(reg)
                self.emit_push_int(1)
                self.emit_u8(OP_SUB)
                self.store_operand(reg)
                # Branch if reg > 0 (i.e. NOT (reg <= 0))
                self.push_operand(reg)
                self.emit_push_int(0)
                self.emit_u8(OP_LE)
                self.emit_jmp_z(lbl, line_no)
            return

        if op == "SOBGEQ":
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                reg, lbl = ops[0], self.clean_operand_prefix(ops[1])
                self.push_operand(reg)
                self.emit_push_int(1)
                self.emit_u8(OP_SUB)
                self.store_operand(reg)
                # Branch if reg >= 0 (i.e. NOT (reg < 0))
                self.push_operand(reg)
                self.emit_push_int(0)
                self.emit_u8(OP_LT)
                self.emit_jmp_z(lbl, line_no)
            return

        if op == "AOBLSS":
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                limit, reg, lbl = ops[0], ops[1], self.clean_operand_prefix(ops[2])
                self.push_operand(reg)
                self.emit_push_int(1)
                self.emit_u8(OP_ADD)
                self.store_operand(reg)
                # Branch if reg < limit (i.e. NOT (reg >= limit))
                self.push_operand(reg)
                self.push_operand(limit)
                self.emit_u8(OP_GE)
                self.emit_jmp_z(lbl, line_no)
            return

        if op == "AOBLEQ":
            ops = self._split_operands(arg)
            if len(ops) >= 3:
                limit, reg, lbl = ops[0], ops[1], self.clean_operand_prefix(ops[2])
                self.push_operand(reg)
                self.emit_push_int(1)
                self.emit_u8(OP_ADD)
                self.store_operand(reg)
                # Branch if reg <= limit (i.e. NOT (reg > limit))
                self.push_operand(reg)
                self.push_operand(limit)
                self.emit_u8(OP_GT)
                self.emit_jmp_z(lbl, line_no)
            return

        # Subroutines & Procedure Calls
        if op in ("JSB", "BSBB", "BSBW"):
            tgt = self.clean_operand_prefix(arg)
            self.emit_call(tgt, line_no)
            return

        if op in ("RSB", "RET"):
            self.emit_u8(OP_RET)
            return

        if op in ("CALLS", "CALLG"):
            ops = self._split_operands(arg)
            if len(ops) >= 2:
                tgt = self.clean_operand_prefix(ops[1]).upper()
                if tgt in ("LIB$PUT_OUTPUT", "SYS$OUTPUT", "PRTSTR", "PRTINT"):
                    self.emit_load_v("__LAST_PUSHED")
                    self.emit_u8(OP_PRINT)
                    self.emit_push_int(1)
                    self.emit_store_v("R0")
                elif tgt in ("SYS$EXIT", "$EXIT_S"):
                    self.emit_u8(OP_HALT)
                elif tgt in self.entry_points or tgt in self.labels:
                    self.emit_call(tgt, line_no)
                else:
                    # External procedure call resolved by OpenVMS Linker (vmslink)
                    self.emit_u8(OP_CALL_OVL)
                    rel_off = len(self.bytecode)
                    self.emit_u16(0)
                    self.relocations.append({"offset": rel_off, "type": "CALL_OVL", "target": tgt})
            return

        if op == "LIB$PUT_OUTPUT":
            self.push_operand(arg)
            self.emit_u8(OP_PRINT)
            self.emit_push_int(1)
            self.emit_store_v("R0")
            return

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX MACRO {self.VERSION}",
            "symbols": {k: v for k, v in self.labels.items() if not k.startswith("__")},
            "relocations": self.relocations,
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"{self.title:<16} VAX MACRO {self.VERSION} (VAX/VMS V5.5-2)  Ident: {self.ident}  {now_str}\n")
                if self.subtitle:
                    f.write(f"Subtitle: {self.subtitle}\n")
                f.write("Line   Offset   Hex Bytes                 Source Statement\n")
                f.write("----  --------  ------------------------  ------------------------------------------------\n")
                for lno, addr, b_slice, raw in self.listing_lines:
                    hex_addr = f"{addr:08X}"
                    hex_bytes = " ".join(f"{b:02X}" for b in b_slice[:8])
                    f.write(f"{lno:>4}  {hex_addr}  {hex_bytes:<24}  {raw}\n")
                f.write("\nProgram Section Synopsis:\n")
                for ps_name, ps_attrs in self.psects.items():
                    f.write(f"  {ps_name:<16}  {ps_attrs}\n")
                f.write("\nSymbol Table:\n")
                for sym, off in sorted(self.labels.items()):
                    f.write(f"  {sym:<20} = {off:08X} R\n")
                for sym, val in sorted(self.equ_symbols.items()):
                    f.write(f"  {sym:<20} = {val & 0xFFFFFFFF:08X}\n")
                f.write(f"\nAssembly Complete: 0 Errors, {len(self.bytecode)} bytes generated.\n")


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
        print("Usage: vaxmacro <input.mar> [-o output.obj] [-l [listing.lst]] [/OBJECT=...] [/LIST[=...]]")
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
        print("%MACRO-E-NOFILE, no input .MAR file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".MAR", ".mar", ".MAC", ".mac", ".ASM", ".asm"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%MACRO-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXMacroCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX MACRO {VAXMacroCompiler.VERSION}: Assembled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
