#!/usr/bin/env python3
"""
DEC PDP-11 RPG II V2.1 Compiler (rpgii.py)
Digital Equipment Corporation PDP-11 / RSTS/E V10.1-L (CTS-300 / RSTS/E RPG II)
Report Program Generator II

Compiles DEC RPG II specification programs (.RPG) containing Control (H),
File (F), Input (I), Calculation (C), and Output (O) specifications into
RSTS/E relocatable object modules (.OBJ) compatible with basiclink and
rsts_vm, plus optional compiler listing files (.LST).
"""

import os
import re
import sys
import json
import struct


class RPGIICompiler:
    VERSION = "V2.1"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name
        self.program_name = "RPGPROG"
        self.bytecode = []
        self.relocations = []
        self.line_offsets = {}
        self.variables = {}
        self.var_types = {}       # var_name -> 'INT' | 'FLOAT' | 'STR'
        self.c_specs = []         # list of parsed C-spec dicts
        self.o_specs = []         # list of parsed O-spec groups: {'type': 'H'|'D'|'T', 'ind': str, 'items': [...]}
        self.listing_lines = []

        # Pre-allocate RPG indicators *IN01..*IN99, *IN1P, *INLR
        for ind in ("IN1P", "INLR"):
            self.get_var_index(ind)
        for idx in range(1, 100):
            self.get_var_index(f"IN{idx:02d}")

    def get_var_index(self, name):
        up = name.upper().strip().lstrip("*")
        if up not in self.variables:
            self.variables[up] = len(self.variables)
        return self.variables[up]

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

    def push_factor(self, factor):
        s = factor.strip()
        if not s:
            self.emit_push_i(0)
            return
        if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
            self.emit_push_s(s[1:-1])
            return
        if re.match(r"^[+-]?\d+\.\d+$", s):
            self.emit_push_f(float(s))
            return
        if re.match(r"^[+-]?\d+$", s):
            self.emit_push_i(int(s))
            return
        self.emit_load_v(s.upper())

    def parse_spec_line(self, raw):
        s = raw.rstrip("\r\n")
        if not s.strip():
            return
        # Check comment: col 7 == '*' or line starts with '*' or '/*'
        stripped = s.lstrip()
        if stripped.startswith("*"):
            return
        if len(s) >= 7 and s[6] == "*":
            return

        # Determine form type (H, F, I, C, O)
        # Can be fixed-column (col 6) or token-delimited starting with H/F/I/C/O
        form = None
        if len(s) >= 6 and s[:5].strip().isdigit() and s[5].upper() in ("H", "F", "I", "C", "O"):
            form = s[5].upper()
            body = s[6:]
        elif stripped[0].upper() in ("H", "F", "I", "C", "O") and (len(stripped) == 1 or stripped[1] in (" ", "\t")):
            form = stripped[0].upper()
            body = stripped[1:].strip()
        elif len(s) >= 6 and s[5].upper() in ("H", "F", "I", "C", "O"):
            form = s[5].upper()
            body = s[6:]
        else:
            return

        if form == "H":
            tokens = body.split()
            if tokens:
                self.program_name = tokens[-1].upper()[:15]
        elif form == "C":
            self._parse_c_spec(body)
        elif form == "O":
            self._parse_o_spec(body)

    def _parse_c_spec(self, body):
        """
        Supports both token-oriented RPG II C-specs and fixed-column C-specs:
        Token form:
          C [N01|01] [Factor1] OPCODE [Factor2] [Result] [ResultInd]
        Opcodes: Z-ADD, Z-SUB, ADD, SUB, MULT, DIV, MOVE, MOVEL, COMP, SETON, SETOF,
                 TAG, GOTO, EXSR, BEGSR, ENDSR, DO, END, DSPLY
        """
        tokens = re.findall(r"'[^']*'|\"[^\"]*\"|[^\s]+", body.strip())
        if not tokens:
            return

        cond_ind = None
        if re.match(r"^N?(?:[0-9]{2}|LR|1P)$", tokens[0], re.IGNORECASE):
            cond_ind = tokens.pop(0).upper()
        if not tokens:
            return

        known_ops = {
            "Z-ADD", "Z-SUB", "ADD", "SUB", "MULT", "DIV", "MVR",
            "MOVE", "MOVEL", "COMP", "SETON", "SETOF",
            "TAG", "GOTO", "EXSR", "BEGSR", "ENDSR", "DO", "END", "DSPLY",
        }

        op_idx = -1
        for idx, tok in enumerate(tokens):
            if tok.upper() in known_ops:
                op_idx = idx
                break
        if op_idx == -1:
            return

        factor1 = tokens[0] if op_idx > 0 else ""
        opcode = tokens[op_idx].upper()
        after = tokens[op_idx + 1:]

        factor2 = ""
        result = ""
        res_ind = ""

        if opcode in ("SETON", "SETOF"):
            res_ind = after[0].upper() if after else ""
        elif opcode in ("TAG", "ENDSR", "END"):
            factor2 = after[0] if after else ""
        elif opcode in ("GOTO", "EXSR", "BEGSR"):
            factor2 = after[0] if after else factor1
        elif opcode in ("Z-ADD", "Z-SUB", "MOVE", "MOVEL"):
            if len(after) >= 2:
                factor2, result = after[0], after[1]
            elif len(after) == 1:
                result = after[0]
        elif opcode == "DSPLY":
            if len(after) >= 2:
                factor1 = after[0]
                factor2 = after[1]
            elif len(after) == 1:
                if factor1:
                    factor2 = after[0]
                else:
                    factor1 = after[0]
        elif opcode == "COMP":
            if len(after) >= 2:
                factor2 = after[0]
                res_ind = after[1].upper()
        else:
            # ADD, SUB, MULT, DIV, DO
            if len(after) >= 2:
                factor2, result = after[0], after[1]
                if len(after) >= 3:
                    res_ind = after[2].upper()
            elif len(after) == 1:
                factor2 = after[0]

        self.c_specs.append({
            "cond_ind": cond_ind,
            "factor1": factor1,
            "opcode": opcode,
            "factor2": factor2,
            "result": result,
            "res_ind": res_ind,
        })

    def _parse_o_spec(self, body):
        """
        O-spec lines:
          Record header line: O <FILENAME> <H|D|T|E> [Indicator: 1P, LR, 01..99]
          Field detail line:  O [FieldName] [EndPos] ['Literal']
        """
        tokens = re.findall(r"'[^']*'|\"[^\"]*\"|[^\s]+", body.strip())
        if not tokens:
            return

        if len(tokens) >= 2 and tokens[1].upper() in ("H", "D", "T", "E"):
            rec_type = tokens[1].upper()
            ind = tokens[2].upper() if len(tokens) >= 3 else ""
            self.o_specs.append({
                "type": rec_type,
                "ind": ind,
                "items": [],
            })
            return

        if not self.o_specs:
            self.o_specs.append({"type": "D", "ind": "", "items": []})

        # Field / constant line under current O-spec record
        for tok in tokens:
            if (tok.startswith("'") and tok.endswith("'")) or (tok.startswith('"') and tok.endswith('"')):
                self.o_specs[-1]["items"].append(("LIT", tok[1:-1]))
            elif tok.isdigit():
                # End position column specification (ignored in stream output or used for spacing)
                continue
            else:
                self.o_specs[-1]["items"].append(("VAR", tok.upper()))

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        for lno, raw in enumerate(raw_lines, start=1):
            self.parse_spec_line(raw)
            self.listing_lines.append((lno, len(self.bytecode), raw))

        # RPG II Fixed Logic Cycle Execution:
        # 1. Set 1P (First Page) indicator ON, print Heading ('H') O-specs conditioned on 1P or unconditional
        self.emit_push_i(1)
        self.emit_store_v("IN1P")

        for o_grp in self.o_specs:
            if o_grp["type"] == "H":
                self._emit_o_group(o_grp)

        self.emit_push_i(0)
        self.emit_store_v("IN1P")

        # 2. Execute Calculation (C) Specifications (main logic; stop before first BEGSR subroutine)
        in_subr = False
        do_stack = []
        for c in self.c_specs:
            op = c["opcode"]
            if op == "BEGSR":
                if not in_subr:
                    # Emit jump past subroutines to detail/total output phase
                    self.emit_jmp("__RPG_OUTPUT_PHASE")
                    in_subr = True
                sub_lbl = (c["factor1"] or c["factor2"]).upper()
                self.line_offsets[sub_lbl] = len(self.bytecode)
                continue
            if op == "ENDSR":
                self.emit_u8(0x41)  # OP_RET
                continue

            self._emit_c_spec(c, do_stack)

        self.line_offsets["__RPG_OUTPUT_PHASE"] = len(self.bytecode)

        # 3. Detail ('D') and Total ('T') Output Specifications
        for o_grp in self.o_specs:
            if o_grp["type"] in ("D", "T", "E"):
                self._emit_o_group(o_grp)

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

    def _emit_c_spec(self, c, do_stack):
        cond_ind = c["cond_ind"]
        skip_lbl = None
        if cond_ind:
            skip_lbl = f"__RPG_CSKIP_{len(self.bytecode)}"
            if cond_ind.startswith("N"):
                ind_name = f"IN{cond_ind[1:]}"
                self.emit_load_v(ind_name)
                self.emit_push_i(0)
                self.emit_u8(0x24)  # EQ 0
                self.emit_jmp_z(skip_lbl)
            else:
                ind_name = f"IN{cond_ind}"
                self.emit_load_v(ind_name)
                self.emit_jmp_z(skip_lbl)

        op = c["opcode"]
        f1 = c["factor1"]
        f2 = c["factor2"]
        res = c["result"].upper()
        rind = c["res_ind"]

        if op == "TAG":
            lbl = (f1 or f2).upper()
            self.line_offsets[lbl] = len(self.bytecode)
        elif op == "GOTO":
            self.emit_jmp((f2 or f1).upper())
        elif op == "EXSR":
            self.emit_call((f2 or f1).upper())
        elif op == "SETON":
            if rind:
                self.emit_push_i(1)
                self.emit_store_v(f"IN{rind}")
        elif op == "SETOF":
            if rind:
                self.emit_push_i(0)
                self.emit_store_v(f"IN{rind}")
        elif op == "Z-ADD":
            self.push_factor(f2)
            self.emit_store_v(res)
        elif op == "Z-SUB":
            self.emit_push_i(0)
            self.push_factor(f2)
            self.emit_u8(0x21)
            self.emit_store_v(res)
        elif op in ("MOVE", "MOVEL"):
            self.push_factor(f2)
            self.emit_store_v(res)
        elif op == "ADD":
            if f1:
                self.push_factor(f1)
            else:
                self.emit_load_v(res)
            self.push_factor(f2)
            self.emit_u8(0x20)
            self.emit_store_v(res)
        elif op == "SUB":
            if f1:
                self.push_factor(f1)
            else:
                self.emit_load_v(res)
            self.push_factor(f2)
            self.emit_u8(0x21)
            self.emit_store_v(res)
        elif op == "MULT":
            if f1:
                self.push_factor(f1)
            else:
                self.emit_load_v(res)
            self.push_factor(f2)
            self.emit_u8(0x22)
            self.emit_store_v(res)
        elif op == "DIV":
            if f1:
                self.push_factor(f1)
            else:
                self.emit_load_v(res)
            self.push_factor(f2)
            self.emit_u8(0x23)
            self.emit_u8(0x75)  # OP_INT
            self.emit_store_v(res)
        elif op == "COMP":
            # COMP Factor1 Factor2 -> sets indicator rind (EQ/HI/LO); here sets IN<rind> if Factor1 == Factor2 or >
            if rind:
                self.push_factor(f1)
                self.push_factor(f2)
                self.emit_u8(0x24)  # EQ
                self.emit_store_v(f"IN{rind}")
        elif op == "DSPLY":
            if f1:
                self.push_factor(f1)
                if f2:
                    self.emit_u8(0x51)
                    self.push_factor(f2)
                self.emit_u8(0x50)
            elif f2:
                self.push_factor(f2)
                self.emit_u8(0x50)
        elif op == "DO":
            # Factor1 DO Factor2 Result (loop var = Result, from Factor1 default 1 to Factor2)
            start_v = f1 if f1 else "1"
            end_v = f2 if f2 else "1"
            loop_var = res if res else "__RPG_DO_IDX"
            self.push_factor(start_v)
            self.emit_store_v(loop_var)
            lp_lbl = f"__RPG_DO_LP_{len(self.bytecode)}"
            ex_lbl = f"__RPG_DO_EX_{len(self.bytecode)}"
            self.line_offsets[lp_lbl] = len(self.bytecode)
            self.emit_load_v(loop_var)
            self.push_factor(end_v)
            self.emit_u8(0x27)  # GT
            self.emit_push_i(0)
            self.emit_u8(0x24)
            self.emit_jmp_z(ex_lbl)
            do_stack.append({"var": loop_var, "lp_lbl": lp_lbl, "ex_lbl": ex_lbl})
        elif op == "END":
            if do_stack:
                d = do_stack.pop()
                self.emit_load_v(d["var"])
                self.emit_push_i(1)
                self.emit_u8(0x20)
                self.emit_store_v(d["var"])
                self.emit_jmp(d["lp_lbl"])
                self.line_offsets[d["ex_lbl"]] = len(self.bytecode)

        if skip_lbl:
            self.line_offsets[skip_lbl] = len(self.bytecode)

    def _emit_o_group(self, o_grp):
        items = o_grp["items"]
        if not items:
            return
        ind = o_grp["ind"]
        skip_lbl = None
        if ind and ind not in ("1P",):
            skip_lbl = f"__RPG_OSKIP_{len(self.bytecode)}"
            self.emit_load_v(f"IN{ind}")
            self.emit_jmp_z(skip_lbl)

        for idx, (kind, val) in enumerate(items):
            if kind == "LIT":
                self.emit_push_s(val)
            else:
                self.emit_load_v(val)
            if idx < len(items) - 1:
                self.emit_u8(0x51)  # OP_PRINT_NO_NL
            else:
                self.emit_u8(0x50)  # OP_PRINT

        if skip_lbl:
            self.line_offsets[skip_lbl] = len(self.bytecode)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "version": 1,
            "module": "MAIN",
            "program": self.program_name,
            "compiler": f"DEC PDP-11 RPG II {self.VERSION}",
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
                f.write(f"DEC PDP-11 RPG II {self.VERSION} (RSTS/E V10.1-L)   PROGRAM: {self.program_name}\n")
                f.write("Line  Offset  Specification Statement\n")
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
        print("Usage: rpgii <input.rpg> [-o output.obj] [-l listing.lst] [--module NAME]")
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
        print("?RPGII-F-NOFILE, no input .RPG file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".RPG", ".rpg"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"?RPGII-F-FNF, cannot find RPG II source file {in_file}")
        sys.exit(1)

    if not out_obj:
        stem, _ = os.path.splitext(in_file)
        out_obj = stem + ".OBJ"

    with open(in_file, "r", errors="replace") as f:
        src_text = f.read()

    comp = RPGIICompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"RPG II {RPGIICompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
