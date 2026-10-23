#!/usr/bin/env python3
"""
DEC MACRO-11 V05.05 Assembler (macro11.py)
Digital Equipment Corporation PDP-11 / RSTS/E V10.1-L

Assembles PDP-11 MACRO-11 source files (.MAC) into RSTS/E relocatable object
modules (.OBJ) and raw bytecode (.bin) compatible with basiclink and rsts_vm,
plus optional assembler listing files (.LST) with octal address/word columns
and symbol tables.
"""

import os
import re
import sys
import json
import struct


class Macro11Compiler:
    VERSION = "V05.05"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name
        self.title = "MAIN"
        self.ident = "V01.00"
        self.bytecode = []
        self.relocations = []
        self.line_offsets = {}
        self.variables = {}
        self.asciz_labels = {}      # label -> string value
        self.word_labels = {}       # label -> list of int values
        self.equ_symbols = {}       # symbol -> int
        self.listing_lines = []

        # Pre-allocate PDP-11 general registers R0..R5, SP (R6), PC (R7), and condition codes
        for reg in ("R0", "R1", "R2", "R3", "R4", "R5", "SP", "PC", "CC_Z", "CC_N", "CC_C", "CC_V", "TMP1", "TMP2"):
            self.get_var_index(reg)
        self.variables["R6"] = self.variables["SP"]
        self.variables["R7"] = self.variables["PC"]

    def get_var_index(self, name):
        up = name.upper().strip()
        if up == "R6":
            up = "SP"
        elif up == "R7":
            up = "PC"
        if up not in self.variables:
            self.variables[up] = len(self.variables)
        return self.variables[up]

    # --- Low-level VM Bytecode Emitters ---
    def emit_u8(self, b):
        self.bytecode.append(b & 0xFF)

    def emit_u16(self, w):
        self.bytecode.append(w & 0xFF)
        self.bytecode.append((w >> 8) & 0xFF)

    def emit_push_i(self, val):
        self.emit_u8(0x10)
        self.emit_u16(val & 0xFFFF)

    def emit_push_s(self, s):
        b = s.encode("utf-8")[:255]
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

    def emit_store_a(self, var_name, idx_val):
        self.emit_push_i(idx_val)
        idx = self.get_var_index(var_name)
        self.emit_u8(0x16)
        self.emit_u16(idx)

    def emit_jmp(self, label):
        self.emit_u8(0x30)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": label.upper(),
        })
        self.emit_u16(0)

    def emit_jmp_z(self, label):
        self.emit_u8(0x31)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP_Z",
            "target_line": label.upper(),
        })
        self.emit_u16(0)

    def emit_call(self, label):
        self.emit_u8(0x40)
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": label.upper(),
        })
        self.emit_u16(0)

    def update_cc_from_var(self, var_name):
        # CC_Z = (var == 0)
        self.emit_load_v(var_name)
        self.emit_push_i(0)
        self.emit_u8(0x24)  # OP_EQ
        self.emit_store_v("CC_Z")
        # CC_N = (var < 0)
        self.emit_load_v(var_name)
        self.emit_push_i(0)
        self.emit_u8(0x26)  # OP_LT
        self.emit_store_v("CC_N")

    def parse_int(self, tok):
        s = tok.strip()
        if s.startswith("#"):
            s = s[1:].strip()
        if s.endswith("."):
            return int(s[:-1], 10)
        if s.upper().startswith("^D"):
            return int(s[2:], 10)
        if s.upper().startswith("^O"):
            return int(s[2:], 8)
        if s.upper().startswith("^X"):
            return int(s[2:], 16)
        if s.upper() in self.equ_symbols:
            return self.equ_symbols[s.upper()]
        try:
            # In MACRO-11, numbers without a trailing '.' are octal if all digits 0-7, else decimal
            if s.lstrip("-+").isdigit():
                if all(c in "01234567" for c in s.lstrip("-+")) and len(s.lstrip("-+")) > 1 and s.lstrip("-+").startswith("0"):
                    return int(s, 8)
                return int(s, 10)
        except ValueError:
            pass
        return 0

    def push_operand(self, op_str):
        s = op_str.strip()
        if s.startswith("#"):
            lit = s[1:].strip()
            if lit.upper() in self.asciz_labels:
                self.emit_push_s(self.asciz_labels[lit.upper()])
            elif lit.upper() in self.equ_symbols:
                self.emit_push_i(self.equ_symbols[lit.upper()])
            else:
                self.emit_push_i(self.parse_int(lit))
            return
        up = s.upper()
        if up in self.equ_symbols:
            self.emit_push_i(self.equ_symbols[up])
            return
        if "(" in up and up.endswith(")"):
            # Indexed or indirect: e.g. (R0) or LAB(R1)
            m = re.match(r"^([A-Z0-9_$]*)\(([A-Z0-9]+)\)$", up)
            if m:
                arr_name, reg_name = m.group(1), m.group(2)
                if arr_name:
                    self.emit_load_v(reg_name)
                    idx = self.get_var_index(arr_name)
                    self.emit_u8(0x17)  # OP_LOAD_A
                    self.emit_u16(idx)
                    return
                else:
                    self.emit_load_v(reg_name)
                    return
        self.emit_load_v(up)

    def store_operand(self, op_str):
        s = op_str.strip()
        up = s.upper()
        if "(" in up and up.endswith(")"):
            m = re.match(r"^([A-Z0-9_$]*)\(([A-Z0-9]+)\)$", up)
            if m:
                arr_name, reg_name = m.group(1), m.group(2)
                if arr_name:
                    self.emit_load_v(reg_name)
                    idx = self.get_var_index(arr_name)
                    self.emit_u8(0x16)  # OP_STORE_A
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
        delim = s[0]
        if delim in ('/', '"', "'", '<'):
            end_delim = '>' if delim == '<' else delim
            idx = s.find(end_delim, 1)
            if idx != -1:
                return s[1:idx]
            return s[1:]
        return s

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()

        # Pass 1: Collect .TITLE, .IDENT, symbol assignments (SYM = VAL), .ASCIZ, .ASCII, .WORD, .BLKW
        for raw in raw_lines:
            clean = self.strip_comment(raw).strip()
            if not clean:
                continue
            if "=" in clean and not clean.startswith("."):
                parts = clean.split("=", 1)
                lhs = parts[0].strip().upper()
                rhs = parts[1].strip()
                if re.match(r"^[A-Z_$][A-Z0-9_$.]*$", lhs):
                    self.equ_symbols[lhs] = self.parse_int(rhs)
                    continue

            label = None
            stmt = clean
            if ":" in stmt:
                cand_lbl, after = stmt.split(":", 1)
                if re.match(r"^[A-Za-z_$][A-Za-z0-9_$.]*$", cand_lbl.strip()):
                    label = cand_lbl.strip().upper()
                    stmt = after.strip()

            if not stmt:
                continue
            parts = stmt.split(None, 1)
            op = parts[0].upper()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if op == ".TITLE" and arg:
                self.title = arg.split()[0].upper()
                if self.module_name == "MAIN":
                    self.module_name = self.title[:15]
            elif op == ".IDENT" and arg:
                self.ident = self.extract_delimited_string(arg)
            elif op in (".ASCIZ", ".ASCII", ".PRINT"):
                s_val = self.extract_delimited_string(arg)
                if label:
                    self.asciz_labels[label] = s_val
            elif op in (".WORD", ".BYTE"):
                vals = [self.parse_int(x) for x in arg.split(",") if x.strip()]
                if label:
                    self.word_labels[label] = vals
            elif op in (".BLKW", ".BLKB"):
                cnt = self.parse_int(arg) if arg else 1
                if label:
                    self.word_labels[label] = [0] * max(1, cnt)

        # Emit startup initialization for .ASCIZ and .WORD variables
        for lbl, sval in self.asciz_labels.items():
            self.emit_push_s(sval)
            self.emit_store_v(lbl)
        for lbl, wvals in self.word_labels.items():
            if len(wvals) == 1:
                self.emit_push_i(wvals[0])
                self.emit_store_v(lbl)
            else:
                self.emit_dim(lbl, len(wvals))
                for idx_i, v in enumerate(wvals):
                    self.emit_push_i(v)
                    self.emit_store_a(lbl, idx_i)
                # Also store first word in scalar variable for direct MOV LAB,Rn
                self.emit_push_i(wvals[0])
                self.emit_store_v(lbl)

        # Pass 2: Assemble executable instructions
        line_no = 0
        for raw in raw_lines:
            line_no += 1
            pc_before = len(self.bytecode)
            clean = self.strip_comment(raw).strip()
            if not clean:
                self.listing_lines.append((line_no, pc_before, [], raw))
                continue
            if "=" in clean and not clean.startswith("."):
                self.listing_lines.append((line_no, pc_before, [], raw))
                continue

            while ":" in clean:
                cand_lbl, after = clean.split(":", 1)
                if re.match(r"^[A-Za-z_$][A-Za-z0-9_$.]*$", cand_lbl.strip()):
                    lbl_up = cand_lbl.strip().upper()
                    self.line_offsets[lbl_up] = len(self.bytecode)
                    clean = after.strip()
                else:
                    break

            if not clean:
                self.listing_lines.append((line_no, pc_before, [], raw))
                continue

            parts = clean.split(None, 1)
            op = parts[0].upper()
            arg = parts[1].strip() if len(parts) > 1 else ""

            self._assemble_instruction(op, arg)
            emitted = self.bytecode[pc_before:]
            self.listing_lines.append((line_no, pc_before, emitted[:6], raw))

        # Ensure trailing HALT
        self.emit_u8(0x00)

        # Resolve local relocations
        for rel in self.relocations:
            if rel["type"] in ("JMP", "JMP_Z"):
                tgt = rel["target_line"]
                if tgt in self.line_offsets:
                    off = self.line_offsets[tgt]
                    loc = rel["offset"]
                    self.bytecode[loc] = off & 0xFF
                    self.bytecode[loc + 1] = (off >> 8) & 0xFF

    def _split_two_ops(self, arg):
        parts = [p.strip() for p in arg.split(",", 1)]
        if len(parts) == 2:
            return parts[0], parts[1]
        return arg.strip(), ""

    def _assemble_instruction(self, op, arg):
        if op in (".TITLE", ".IDENT", ".MCALL", ".CSECT", ".PSECT", ".GLOBL", ".EVEN", ".ODD", ".ASCIZ", ".ASCII", ".WORD", ".BYTE", ".BLKW", ".BLKB"):
            return
        if op in (".END", ".EXIT", "HALT", "IOT", "BPT"):
            self.emit_u8(0x00)  # OP_HALT
            return
        if op == "NOP":
            return
        if op in (".TTYOUT", "TTYOUT"):
            src = arg.strip() if arg else "R0"
            self.push_operand(src)
            self.emit_u8(0x73)  # OP_CHR
            self.emit_u8(0x51)  # OP_PRINT_NO_NL
            return
        if op in (".PRINT", "PRINT"):
            if not arg:
                self.emit_push_s("")
            elif arg[0] in ('/', '"', "'", '<'):
                self.emit_push_s(self.extract_delimited_string(arg))
            else:
                tok = arg.strip().lstrip("#").upper()
                if tok in self.asciz_labels:
                    self.emit_push_s(self.asciz_labels[tok])
                else:
                    self.push_operand(arg)
            self.emit_u8(0x50)  # OP_PRINT
            return
        if op in ("MOV", "MOVB"):
            src, dst = self._split_two_ops(arg)
            self.push_operand(src)
            self.store_operand(dst)
            return
        if op in ("CLR", "CLRB"):
            self.emit_push_i(0)
            self.store_operand(arg)
            return
        if op in ("INC", "INCB"):
            self.push_operand(arg)
            self.emit_push_i(1)
            self.emit_u8(0x20)  # OP_ADD
            self.store_operand(arg)
            return
        if op in ("DEC", "DECB"):
            self.push_operand(arg)
            self.emit_push_i(1)
            self.emit_u8(0x21)  # OP_SUB
            self.store_operand(arg)
            return
        if op in ("NEG", "NEGB"):
            self.emit_push_i(0)
            self.push_operand(arg)
            self.emit_u8(0x21)  # OP_SUB
            self.store_operand(arg)
            return
        if op == "ADD":
            src, dst = self._split_two_ops(arg)
            self.push_operand(dst)
            self.push_operand(src)
            self.emit_u8(0x20)  # OP_ADD
            self.store_operand(dst)
            return
        if op == "SUB":
            src, dst = self._split_two_ops(arg)
            self.push_operand(dst)
            self.push_operand(src)
            self.emit_u8(0x21)  # OP_SUB
            self.store_operand(dst)
            return
        if op == "MUL":
            src, dst = self._split_two_ops(arg)
            self.push_operand(dst)
            self.push_operand(src)
            self.emit_u8(0x22)  # OP_MUL
            self.store_operand(dst)
            return
        if op == "DIV":
            src, dst = self._split_two_ops(arg)
            self.push_operand(dst)
            self.push_operand(src)
            self.emit_u8(0x23)  # OP_DIV
            self.emit_u8(0x75)  # OP_INT
            self.store_operand(dst)
            return
        if op in ("BIC", "BICB"):
            # Bit Clear: dst = dst & ~src (approximated or supported via helper)
            src, dst = self._split_two_ops(arg)
            self.push_operand(dst)
            self.push_operand(src)
            self.emit_u8(0x21)
            self.store_operand(dst)
            return
        if op in ("BIS", "BISB"):
            src, dst = self._split_two_ops(arg)
            self.push_operand(dst)
            self.push_operand(src)
            self.emit_u8(0x29)  # OP_OR
            self.store_operand(dst)
            return
        if op in ("BIT", "BITB"):
            src, dst = self._split_two_ops(arg)
            self.push_operand(dst)
            self.push_operand(src)
            self.emit_u8(0x28)  # OP_AND
            self.emit_store_v("TMP1")
            self.update_cc_from_var("TMP1")
            return
        if op in ("ASL", "ASLB"):
            self.push_operand(arg)
            self.emit_push_i(2)
            self.emit_u8(0x22)
            self.store_operand(arg)
            return
        if op in ("ASR", "ASRB"):
            self.push_operand(arg)
            self.emit_push_i(2)
            self.emit_u8(0x23)
            self.emit_u8(0x75)
            self.store_operand(arg)
            return
        if op in ("CMP", "CMPB"):
            src, dst = self._split_two_ops(arg)
            self.push_operand(src)
            self.push_operand(dst)
            self.emit_u8(0x21)  # src - dst
            self.emit_store_v("TMP1")
            self.update_cc_from_var("TMP1")
            return
        if op in ("TST", "TSTB"):
            self.push_operand(arg)
            self.emit_store_v("TMP1")
            self.update_cc_from_var("TMP1")
            return
        if op in ("BR", "JMP"):
            self.emit_jmp(arg.strip())
            return
        if op == "BEQ":
            # Jump if CC_Z == 1 (i.e. NOT CC_Z == 0)
            self.emit_load_v("CC_Z")
            self.emit_push_i(0)
            self.emit_u8(0x24)  # EQ 0 -> 1 when CC_Z==0
            self.emit_jmp_z(arg.strip())
            return
        if op == "BNE":
            # Jump if CC_Z == 0
            self.emit_load_v("CC_Z")
            self.emit_jmp_z(arg.strip())
            return
        if op in ("BLT", "BMI"):
            # Jump if CC_N == 1
            self.emit_load_v("CC_N")
            self.emit_push_i(0)
            self.emit_u8(0x24)
            self.emit_jmp_z(arg.strip())
            return
        if op in ("BGE", "BPL"):
            # Jump if CC_N == 0
            self.emit_load_v("CC_N")
            self.emit_jmp_z(arg.strip())
            return
        if op == "BLE":
            # Jump if CC_Z == 1 or CC_N == 1
            self.emit_load_v("CC_Z")
            self.emit_load_v("CC_N")
            self.emit_u8(0x29)  # OR
            self.emit_push_i(0)
            self.emit_u8(0x24)
            self.emit_jmp_z(arg.strip())
            return
        if op == "BGT":
            # Jump if CC_Z == 0 and CC_N == 0
            self.emit_load_v("CC_Z")
            self.emit_load_v("CC_N")
            self.emit_u8(0x29)  # OR
            self.emit_jmp_z(arg.strip())
            return
        if op == "SOB":
            # SOB Rn,label -> dec Rn; if Rn != 0 goto label
            reg, lbl = self._split_two_ops(arg)
            self.push_operand(reg)
            self.emit_push_i(1)
            self.emit_u8(0x21)
            self.store_operand(reg)
            self.emit_load_v("CC_Z")
            self.emit_jmp_z(lbl)
            return
        if op == "JSR":
            # JSR PC,subr or JSR Rn,subr
            if "," in arg:
                _, tgt = self._split_two_ops(arg)
            else:
                tgt = arg.strip()
            self.emit_call(tgt)
            return
        if op in ("RTS", "RETURN"):
            self.emit_u8(0x41)  # OP_RET
            return
        if op in ("EMT", "TRAP"):
            # RSTS/E EMT / RSX directive simulation: print R0 if string/number or no-op
            code = self.parse_int(arg) if arg else 0
            if code in (351, 0o351, 1):
                self.emit_load_v("R0")
                self.emit_u8(0x50)
            return

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "version": 1,
            "module": "MAIN",
            "title": self.title,
            "ident": self.ident,
            "assembler": f"DEC MACRO-11 {self.VERSION}",
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
                f.write(f"{self.title:<12} MACRO {self.VERSION}  RSTS/E V10.1-L Assembler Listing   Ident: {self.ident}\n")
                f.write("Line   Octal   Bytes               Source Statement\n")
                f.write("----  ------  ------------------  ------------------------------------------------\n")
                for lno, addr, b_slice, raw in self.listing_lines:
                    oct_addr = f"{addr:06o}"
                    oct_bytes = " ".join(f"{b:03o}" for b in b_slice[:4])
                    f.write(f"{lno:>4}  {oct_addr}  {oct_bytes:<18}  {raw}\n")
                f.write("\nSymbol Table:\n")
                for sym, off in sorted(self.line_offsets.items()):
                    f.write(f"  {sym:<16} = {off:06o}R\n")
                for sym, val in sorted(self.equ_symbols.items()):
                    f.write(f"  {sym:<16} = {val & 0xFFFF:06o}\n")


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
        print("Usage: macro11 <input.mac> [-o output.obj] [-l listing.lst] [--module NAME]")
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
        print("?MACRO-F-NOFILE, no input .MAC file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".MAC", ".mac", ".ASM", ".asm"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"?MACRO-F-FNF, cannot find source file {in_file}")
        sys.exit(1)

    if not out_obj:
        stem, _ = os.path.splitext(in_file)
        out_obj = stem + ".OBJ"

    with open(in_file, "r", errors="replace") as f:
        src_text = f.read()

    comp = Macro11Compiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"MACRO-11 {Macro11Compiler.VERSION}: Assembled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
