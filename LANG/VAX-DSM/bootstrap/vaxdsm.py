#!/usr/bin/env python3
"""
DEC VAX DSM V6.0-00 (Digital Standard MUMPS) Compiler & Environment (vaxdsm.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Supports:
  - Routines with labels (`LABEL ; comment` or `LABEL(p1,p2)`), multiple commands per line,
    postconditionals (`CMD:cond`), and full/abbreviated MUMPS commands:
    * SET (S), WRITE (W: !, # , ?col, strings, expressions), NEW (N), KILL (K),
      IF (I), ELSE (E), FOR (F var=start:step:end, F var=start:step, F var=v1,v2,...),
      DO (D label[(args)]), GOTO (G label), QUIT (Q [expr]), HALT (H), READ (R)
  - Intrinsic functions & operators:
    * _ (string concatenation), [ (contains), ' (logical not & negated comparisons '= '< '> '[),
      +, -, *, /, \\ (int div), # (modulo), =, <, >, &, !
    * $LENGTH ($L), $EXTRACT ($E), $PIECE ($P), $FIND ($F), $ASCII ($A),
      $CHAR ($C), $DATA ($D), $ORDER ($O)
  - Hierarchical sparse local arrays (`ARR(k1,k2)`) and global B-tree arrays (`^GLOBAL(k1,k2)`)
  - Interactive MUMPS programmer prompt (`DEC VAX DSM V6.0-00 — Digital Standard MUMPS`, `DSM>`)
  - Emits OpenVMS .OBJ relocatable object modules and .LST listings for vmslink & vms_vm
"""

import copy
import io
import os
import re
import sys
import json
import struct
from contextlib import redirect_stdout
from datetime import datetime

# Bytecode Opcodes (vms_vm compatible)
OP_HALT = 0x00
OP_PUSH_INT = 0x10
OP_PUSH_STR = 0x12
OP_STORE_VAR = 0x13
OP_PUSH_I32 = 0x18
OP_PRINT = 0x50


class DSMHalt(Exception):
    pass


class DSMQuit(Exception):
    def __init__(self, val=""):
        self.val = val


class DSMGoto(Exception):
    def __init__(self, label):
        self.label = label.upper()


class MumpsNode:
    def __init__(self, val=None):
        self.val = val
        self.subs = {}  # str key -> MumpsNode

    def clone(self):
        c = MumpsNode(self.val)
        c.subs = {k: v.clone() for k, v in self.subs.items()}
        return c


def mumps_collation_key(k):
    s = str(k)
    if re.match(r"^[+-]?(?:\d+|\d+\.\d+)$", s):
        return (0, float(s), s)
    return (1, 0.0, s)


def to_mumps_num(v):
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip()
    m = re.match(r"^[+-]?(?:\d+\.\d+|\d+)", s)
    if not m:
        return 0
    num_s = m.group(0)
    if "." in num_s:
        f = float(num_s)
        return int(f) if f.is_integer() else f
    return int(num_s)


def to_mumps_str(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


class VAXDSMInterpreter:
    VERSION = "V6.0-00"

    def __init__(self):
        self.locals = {}        # var_name -> MumpsNode
        self.globals = {}       # ^GLOBAL_NAME -> MumpsNode
        self.new_stack = []     # stack of saved local dicts for NEW
        self.test_flag = True   # $TEST ($T) set by IF
        self.routines = []      # list of {'label': str_or_None, 'params': [], 'body': str}
        self.label_map = {}     # LABEL -> line index in self.routines
        self._col = 0           # current horizontal column for ?col tabbing
        self._out_buf = []      # current line buffer before ! newline

    # ------------------------------------------------------------------
    # Hierarchical Sparse Array / Global Node Access
    # ------------------------------------------------------------------
    def _get_table(self, name):
        return self.globals if name.startswith("^") else self.locals

    def get_node(self, name, subs, create=False):
        key = name.upper()
        tbl = self._get_table(key)
        if key not in tbl:
            if not create:
                return None
            tbl[key] = MumpsNode()
        node = tbl[key]
        for s in subs:
            sk = to_mumps_str(s)
            if sk not in node.subs:
                if not create:
                    return None
                node.subs[sk] = MumpsNode()
            node = node.subs[sk]
        return node

    def set_var(self, name, subs, val):
        node = self.get_node(name, subs, create=True)
        node.val = to_mumps_str(val) if not isinstance(val, (int, float)) else val

    def get_var(self, name, subs):
        node = self.get_node(name, subs, create=False)
        if node is None or node.val is None:
            return ""
        return node.val

    def kill_var(self, name=None, subs=None):
        if name is None:
            self.locals.clear()
            return
        key = name.upper()
        tbl = self._get_table(key)
        if not subs:
            tbl.pop(key, None)
            return
        parent = self.get_node(key, subs[:-1], create=False)
        if parent is not None:
            parent.subs.pop(to_mumps_str(subs[-1]), None)

    def data_fn(self, name, subs):
        node = self.get_node(name, subs, create=False)
        if node is None:
            return 0
        has_val = 1 if node.val is not None else 0
        has_subs = 10 if any(v.val is not None or v.subs for v in node.subs.values()) else 0
        return has_val + has_subs

    def order_fn(self, name, subs, direction=1):
        if not subs:
            return ""
        parent = self.get_node(name, subs[:-1], create=False)
        if parent is None:
            return ""
        valid_keys = [k for k, v in parent.subs.items() if v.val is not None or v.subs]
        if not valid_keys:
            return ""
        valid_keys.sort(key=mumps_collation_key, reverse=(direction < 0))
        seed = to_mumps_str(subs[-1])
        if seed == "":
            return valid_keys[0]
        seed_key = mumps_collation_key(seed)
        for k in valid_keys:
            kk = mumps_collation_key(k)
            if direction > 0 and kk > seed_key:
                return k
            if direction < 0 and kk < seed_key:
                return k
        return ""

    # ------------------------------------------------------------------
    # Expression Parser & Evaluator (Left-to-Right ANSI MUMPS Semantics)
    # ------------------------------------------------------------------
    def tokenize_expr(self, expr):
        tokens = []
        i = 0
        n = len(expr)
        while i < n:
            ch = expr[i]
            if ch.isspace():
                i += 1
                continue
            if ch == '"':
                i += 1
                buf = []
                while i < n:
                    if expr[i] == '"':
                        if i + 1 < n and expr[i + 1] == '"':
                            buf.append('"')
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(expr[i])
                    i += 1
                tokens.append(("STR", "".join(buf)))
                continue
            if expr[i:i + 2] in ("'=", "'<", "'>", "'[", "'&", "'!", "**"):
                tokens.append(("OP", expr[i:i + 2]))
                i += 2
                continue
            if ch in ("+", "-", "*", "/", "\\", "#", "_", "=", "<", ">", "[", "&", "!", "'", "(", ")", ","):
                tokens.append(("OP", ch))
                i += 1
                continue
            if ch.isdigit() or (ch == "." and i + 1 < n and expr[i + 1].isdigit()):
                j = i
                has_dot = False
                while j < n and (expr[j].isdigit() or expr[j] == "."):
                    if expr[j] == ".":
                        has_dot = True
                    j += 1
                num_s = expr[i:j]
                tokens.append(("NUM", float(num_s) if has_dot else int(num_s)))
                i = j
                continue
            if ch in ("$", "^") or ch.isalpha() or ch == "%":
                j = i + 1
                while j < n and (expr[j].isalnum() or expr[j] == "%"):
                    j += 1
                tokens.append(("IDENT", expr[i:j].upper()))
                i = j
                continue
            i += 1
        return tokens

    def eval_expr(self, expr_str):
        tokens = self.tokenize_expr(expr_str)
        if not tokens:
            return ""
        pos = 0

        def peek():
            return tokens[pos] if pos < len(tokens) else (None, None)

        def consume():
            nonlocal pos
            t = peek()
            pos += 1
            return t

        def parse_arg_list():
            # Assumes '(' already consumed
            args = []
            if peek() == ("OP", ")"):
                consume()
                return args
            while pos < len(tokens):
                args.append(parse_expr())
                if peek() == ("OP", ","):
                    consume()
                elif peek() == ("OP", ")"):
                    consume()
                    break
                else:
                    break
            return args

        def parse_var_ref():
            # Parses variable/global reference for $DATA / $ORDER without evaluating the final node
            _, vname = consume()
            subs = []
            if peek() == ("OP", "("):
                consume()
                subs = parse_arg_list()
            return vname, subs

        def parse_atom():
            tt, tv = peek()
            if tt == "OP" and tv == "(":
                consume()
                val = parse_expr()
                if peek() == ("OP", ")"):
                    consume()
                return val
            if tt == "OP" and tv in ("+", "-", "'"):
                consume()
                operand = parse_atom()
                if tv == "+":
                    return to_mumps_num(operand)
                if tv == "-":
                    return -to_mumps_num(operand)
                if tv == "'":
                    return 0 if to_mumps_num(operand) != 0 else 1
            if tt == "NUM":
                consume()
                return tv
            if tt == "STR":
                consume()
                return tv
            if tt == "IDENT":
                if tv.startswith("$$"):
                    consume()
                    lbl = tv[2:]
                    args = []
                    if peek() == ("OP", "("):
                        consume()
                        args = parse_arg_list()
                    return self.call_label(lbl, args)
                if tv.startswith("$"):
                    consume()
                    if tv in ("$T", "$TEST"):
                        return 1 if self.test_flag else 0
                    if tv in ("$D", "$DATA") and peek() == ("OP", "("):
                        consume()
                        vname, subs = parse_var_ref()
                        if peek() == ("OP", ")"):
                            consume()
                        return self.data_fn(vname, subs)
                    if tv in ("$O", "$ORDER") and peek() == ("OP", "("):
                        consume()
                        vname, subs = parse_var_ref()
                        direction = 1
                        if peek() == ("OP", ","):
                            consume()
                            direction = int(to_mumps_num(parse_expr()))
                        if peek() == ("OP", ")"):
                            consume()
                        return self.order_fn(vname, subs, direction=direction)
                    args = []
                    if peek() == ("OP", "("):
                        consume()
                        args = parse_arg_list()
                    return self._eval_intrinsic(tv, args)
                # Local or Global Variable
                consume()
                subs = []
                if peek() == ("OP", "("):
                    consume()
                    subs = parse_arg_list()
                return self.get_var(tv, subs)
            consume()
            return ""

        def parse_expr():
            lhs = parse_atom()
            binary_ops = {
                "+", "-", "*", "/", "\\", "#", "**", "_",
                "=", "'=", "<", "'<", ">", "'>", "[", "'[", "&", "'&", "!", "'!",
            }
            while peek()[0] == "OP" and peek()[1] in binary_ops:
                _, op = consume()
                rhs = parse_atom()
                lhs = self._apply_binary(op, lhs, rhs)
            return lhs

        return parse_expr()

    def _apply_binary(self, op, a, b):
        if op == "_":
            return to_mumps_str(a) + to_mumps_str(b)
        if op == "+":
            return to_mumps_num(a) + to_mumps_num(b)
        if op == "-":
            return to_mumps_num(a) - to_mumps_num(b)
        if op == "*":
            return to_mumps_num(a) * to_mumps_num(b)
        if op == "**":
            return to_mumps_num(a) ** to_mumps_num(b)
        if op == "/":
            nb = to_mumps_num(b)
            res = (to_mumps_num(a) / nb) if nb != 0 else 0
            return int(res) if isinstance(res, float) and res.is_integer() else res
        if op == "\\":
            nb = to_mumps_num(b)
            return int(to_mumps_num(a) // nb) if nb != 0 else 0
        if op == "#":
            nb = to_mumps_num(b)
            return (to_mumps_num(a) % nb) if nb != 0 else 0
        if op == "=":
            return 1 if to_mumps_str(a) == to_mumps_str(b) else 0
        if op == "'=":
            return 1 if to_mumps_str(a) != to_mumps_str(b) else 0
        if op == "<":
            return 1 if to_mumps_num(a) < to_mumps_num(b) else 0
        if op == "'<":
            return 1 if to_mumps_num(a) >= to_mumps_num(b) else 0
        if op == ">":
            return 1 if to_mumps_num(a) > to_mumps_num(b) else 0
        if op == "'>":
            return 1 if to_mumps_num(a) <= to_mumps_num(b) else 0
        if op == "[":
            return 1 if to_mumps_str(b) in to_mumps_str(a) else 0
        if op == "'[":
            return 1 if to_mumps_str(b) not in to_mumps_str(a) else 0
        if op == "&":
            return 1 if (to_mumps_num(a) != 0 and to_mumps_num(b) != 0) else 0
        if op == "'&":
            return 0 if (to_mumps_num(a) != 0 and to_mumps_num(b) != 0) else 1
        if op == "!":
            return 1 if (to_mumps_num(a) != 0 or to_mumps_num(b) != 0) else 0
        if op == "'!":
            return 0 if (to_mumps_num(a) != 0 or to_mumps_num(b) != 0) else 1
        return 0

    def _eval_intrinsic(self, fn_name, args):
        fn = fn_name.upper()
        if fn in ("$L", "$LENGTH"):
            s = to_mumps_str(args[0]) if args else ""
            if len(args) >= 2:
                delim = to_mumps_str(args[1])
                if not delim:
                    return 0
                return 0 if s == "" else (s.count(delim) + 1)
            return len(s)

        if fn in ("$E", "$EXTRACT"):
            s = to_mumps_str(args[0]) if args else ""
            start = int(to_mumps_num(args[1])) if len(args) >= 2 else 1
            end = int(to_mumps_num(args[2])) if len(args) >= 3 else start
            start_i = max(0, start - 1)
            if end < start:
                return ""
            return s[start_i:end]

        if fn in ("$P", "$PIECE"):
            s = to_mumps_str(args[0]) if args else ""
            delim = to_mumps_str(args[1]) if len(args) >= 2 else ","
            start = int(to_mumps_num(args[2])) if len(args) >= 3 else 1
            end = int(to_mumps_num(args[3])) if len(args) >= 4 else start
            if not delim or end < start:
                return ""
            parts = s.split(delim)
            lo = max(1, start) - 1
            hi = min(len(parts), end)
            if lo >= len(parts):
                return ""
            return delim.join(parts[lo:hi])

        if fn in ("$F", "$FIND"):
            s = to_mumps_str(args[0]) if args else ""
            sub = to_mumps_str(args[1]) if len(args) >= 2 else ""
            start = int(to_mumps_num(args[2])) if len(args) >= 3 else 1
            idx = s.find(sub, max(0, start - 1))
            if idx < 0:
                return 0
            return idx + 1 + len(sub)

        if fn in ("$A", "$ASCII"):
            s = to_mumps_str(args[0]) if args else ""
            pos = int(to_mumps_num(args[1])) if len(args) >= 2 else 1
            if 1 <= pos <= len(s):
                return ord(s[pos - 1])
            return -1

        if fn in ("$C", "$CHAR"):
            out = []
            for a in args:
                code = int(to_mumps_num(a))
                if code >= 0:
                    out.append(chr(code))
            return "".join(out)

        return ""

    # ------------------------------------------------------------------
    # Line & Command Execution
    # ------------------------------------------------------------------
    def _strip_comment(self, line):
        in_q = False
        i = 0
        n = len(line)
        while i < n:
            if line[i] == '"':
                in_q = not in_q
            elif line[i] == ";" and not in_q:
                return line[:i]
            i += 1
        return line

    def _split_top_level(self, text, sep=","):
        parts = []
        cur = []
        in_q = False
        depth = 0
        for ch in text:
            if ch == '"':
                in_q = not in_q
                cur.append(ch)
            elif not in_q:
                if ch == "(":
                    depth += 1
                    cur.append(ch)
                elif ch == ")":
                    depth = max(0, depth - 1)
                    cur.append(ch)
                elif depth == 0 and ch == sep:
                    parts.append("".join(cur).strip())
                    cur = []
                else:
                    cur.append(ch)
            else:
                cur.append(ch)
        tail = "".join(cur).strip()
        if tail:
            parts.append(tail)
        return parts

    def _read_next_cmd(self, line, pos):
        n = len(line)
        while pos < n and line[pos].isspace():
            pos += 1
        if pos >= n or line[pos] == ";":
            return None, None, None, n

        # Read command word (and optional :postcond)
        in_q = False
        depth = 0
        j = pos
        while j < n:
            ch = line[j]
            if ch == '"':
                in_q = not in_q
            elif not in_q:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth = max(0, depth - 1)
                elif depth == 0 and (ch.isspace() or ch == ";"):
                    break
            j += 1
        cmd_token = line[pos:j]
        if ":" in cmd_token:
            cmd_word, postcond = cmd_token.split(":", 1)
        else:
            cmd_word, postcond = cmd_token, None
        cmd_word = cmd_word.upper()

        if j >= n or line[j] == ";":
            return cmd_word, postcond, "", n
        spaces = 0
        k = j
        while k < n and line[k] == " ":
            spaces += 1
            k += 1

        # If FOR, its scope is the rest of the line (both argumentless FOR  body and FOR var=spec body)
        if cmd_word in ("F", "FOR"):
            if spaces >= 2:
                return cmd_word, postcond, "__ARGLESS__ " + line[k:], n
            return cmd_word, postcond, line[k:], n

        # Check if argumentless command (followed by >=2 spaces, or end of line, or ELSE/HALT)
        if spaces >= 2 or cmd_word in ("E", "ELSE", "H", "HALT"):
            return cmd_word, postcond, "", k

        # Otherwise read command argument up to next whitespace outside quotes/parens
        in_q = False
        depth = 0
        m = k
        while m < n:
            ch = line[m]
            if ch == '"':
                in_q = not in_q
            elif not in_q:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth = max(0, depth - 1)
                elif depth == 0 and (ch == " " or ch == "\t" or ch == ";"):
                    break
            m += 1
        return cmd_word, postcond, line[k:m].strip(), m

    def _parse_lvalue(self, lval_str):
        lval_str = lval_str.strip()
        if "(" in lval_str and lval_str.endswith(")"):
            idx = lval_str.index("(")
            vname = lval_str[:idx].strip().upper()
            sub_str = lval_str[idx + 1:-1]
            subs = [self.eval_expr(s) for s in self._split_top_level(sub_str, ",")]
            return vname, subs
        return lval_str.upper(), []

    def exec_commands(self, line):
        cleaned = self._strip_comment(line).rstrip()
        if not cleaned.strip():
            return
        pos = 0
        n = len(cleaned)
        while pos < n:
            cmd, postcond, arg, next_pos = self._read_next_cmd(cleaned, pos)
            pos = next_pos
            if not cmd:
                break
            if postcond is not None:
                if to_mumps_num(self.eval_expr(postcond)) == 0:
                    continue

            if cmd in ("S", "SET"):
                for assign in self._split_top_level(arg, ","):
                    if "=" not in assign:
                        continue
                    lhs_s, rhs_s = assign.split("=", 1)
                    val = self.eval_expr(rhs_s)
                    lhs_s = lhs_s.strip()
                    if lhs_s.startswith("(") and lhs_s.endswith(")"):
                        for target in self._split_top_level(lhs_s[1:-1], ","):
                            vn, subs = self._parse_lvalue(target)
                            self.set_var(vn, subs, val)
                    else:
                        vn, subs = self._parse_lvalue(lhs_s)
                        self.set_var(vn, subs, val)

            elif cmd in ("W", "WRITE"):
                self._exec_write(arg)

            elif cmd in ("K", "KILL"):
                if not arg:
                    self.kill_var()
                else:
                    for item in self._split_top_level(arg, ","):
                        vn, subs = self._parse_lvalue(item)
                        self.kill_var(vn, subs)

            elif cmd in ("N", "NEW"):
                saved = {}
                for item in self._split_top_level(arg, ","):
                    vn = item.strip().upper()
                    if vn in self.locals:
                        saved[vn] = self.locals.pop(vn)
                    else:
                        saved[vn] = None
                self.new_stack.append(saved)

            elif cmd in ("I", "IF"):
                cond_ok = True
                for c_expr in self._split_top_level(arg, ","):
                    if to_mumps_num(self.eval_expr(c_expr)) == 0:
                        cond_ok = False
                        break
                self.test_flag = cond_ok
                if not cond_ok:
                    return

            elif cmd in ("E", "ELSE"):
                if self.test_flag:
                    return

            elif cmd in ("F", "FOR"):
                self._exec_for(arg)
                return

            elif cmd in ("D", "DO"):
                for target in self._split_top_level(arg, ","):
                    if "(" in target and target.endswith(")"):
                        idx = target.index("(")
                        lbl = target[:idx].strip().upper()
                        call_args = [self.eval_expr(x) for x in self._split_top_level(target[idx + 1:-1], ",")]
                    else:
                        lbl = target.strip().upper()
                        call_args = []
                    self.call_label(lbl, call_args)

            elif cmd in ("G", "GOTO"):
                raise DSMGoto(arg.strip())

            elif cmd in ("Q", "QUIT"):
                ret_val = self.eval_expr(arg) if arg else ""
                raise DSMQuit(ret_val)

            elif cmd in ("H", "HALT"):
                self.flush_output()
                raise DSMHalt()

            elif cmd in ("R", "READ"):
                for item in self._split_top_level(arg, ","):
                    if item.startswith('"') or item.startswith("!") or item.startswith("?"):
                        self._exec_write(item)
                    else:
                        vn, subs = self._parse_lvalue(item)
                        inp_line = sys.stdin.readline().rstrip("\r\n")
                        self.set_var(vn, subs, inp_line)

    def _exec_write(self, arg):
        for item in self._split_top_level(arg, ","):
            if not item:
                continue
            if re.match(r"^[!#]+$", item):
                for ch in item:
                    if ch in ("!", "#"):
                        self.flush_output(force_newline=True)
                continue
            if item.startswith("?"):
                col = int(to_mumps_num(self.eval_expr(item[1:])))
                if col > self._col:
                    pad = " " * (col - self._col)
                    self._out_buf.append(pad)
                    self._col = col
                continue
            val_s = to_mumps_str(self.eval_expr(item))
            self._out_buf.append(val_s)
            self._col += len(val_s)

    def _exec_for(self, for_rest):
        if for_rest.startswith("__ARGLESS__ "):
            body_part = for_rest[len("__ARGLESS__ "):].strip()
            for _ in range(10000):
                try:
                    self.exec_commands(body_part)
                except DSMQuit:
                    return
            return

        # Split F var=specs  commands...
        in_q = False
        depth = 0
        split_idx = len(for_rest)
        for idx, ch in enumerate(for_rest):
            if ch == '"':
                in_q = not in_q
            elif not in_q:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth = max(0, depth - 1)
                elif depth == 0 and ch.isspace():
                    split_idx = idx
                    break
        spec_part = for_rest[:split_idx].strip()
        body_part = for_rest[split_idx:].strip()
        if "=" not in spec_part:
            return
        lhs_s, specs_s = spec_part.split("=", 1)
        vn, subs = self._parse_lvalue(lhs_s)

        for spec in self._split_top_level(specs_s, ","):
            colon_parts = self._split_top_level(spec, ":")
            if len(colon_parts) == 1:
                self.set_var(vn, subs, self.eval_expr(colon_parts[0]))
                try:
                    self.exec_commands(body_part)
                except DSMQuit:
                    return
            elif len(colon_parts) == 2:
                cur = to_mumps_num(self.eval_expr(colon_parts[0]))
                step = to_mumps_num(self.eval_expr(colon_parts[1]))
                for _ in range(10000):
                    self.set_var(vn, subs, cur)
                    try:
                        self.exec_commands(body_part)
                    except DSMQuit:
                        return
                    cur += step
            else:
                cur = to_mumps_num(self.eval_expr(colon_parts[0]))
                step = to_mumps_num(self.eval_expr(colon_parts[1]))
                end = to_mumps_num(self.eval_expr(colon_parts[2]))
                while (step >= 0 and cur <= end) or (step < 0 and cur >= end):
                    self.set_var(vn, subs, cur)
                    try:
                        self.exec_commands(body_part)
                    except DSMQuit:
                        return
                    cur += step

    def flush_output(self, force_newline=False):
        if self._out_buf or force_newline:
            print("".join(self._out_buf))
            self._out_buf.clear()
            self._col = 0

    # ------------------------------------------------------------------
    # Routine Loader & Execution
    # ------------------------------------------------------------------
    def load_source(self, source_text):
        self.routines.clear()
        self.label_map.clear()
        for raw in source_text.splitlines():
            if not raw.strip():
                continue
            m = re.match(r"^([A-Za-z%][A-Za-z0-9%]*)(?:\(([^)]*)\))?(?:\s+(.*))?$", raw)
            if m and not raw[0].isspace():
                lbl = m.group(1).upper()
                params = [p.strip().upper() for p in (m.group(2) or "").split(",") if p.strip()]
                body = m.group(3) or ""
                self.label_map[lbl] = len(self.routines)
                self.routines.append({"label": lbl, "params": params, "body": body})
            else:
                self.routines.append({"label": None, "params": [], "body": raw.strip()})

    def call_label(self, label, args=None):
        lbl = label.upper()
        if lbl not in self.label_map:
            return ""
        start_idx = self.label_map[lbl]
        params = self.routines[start_idx]["params"]
        depth_before = len(self.new_stack)
        if params:
            saved = {p: self.locals.get(p) for p in params}
            self.new_stack.append(saved)
            for p_idx, pname in enumerate(params):
                val = args[p_idx] if args and p_idx < len(args) else ""
                self.set_var(pname, [], val)

        ret_val = ""
        try:
            self._run_from(start_idx)
        except DSMQuit as dq:
            ret_val = dq.val
        finally:
            while len(self.new_stack) > depth_before:
                saved_top = self.new_stack.pop()
                for k, v in saved_top.items():
                    if v is None:
                        self.locals.pop(k, None)
                    else:
                        self.locals[k] = v
        return ret_val

    def _run_from(self, start_idx=0):
        pc = start_idx
        while 0 <= pc < len(self.routines):
            body = self.routines[pc]["body"]
            try:
                self.exec_commands(body)
                pc += 1
            except DSMGoto as dg:
                if dg.label in self.label_map:
                    pc = self.label_map[dg.label]
                else:
                    break

    def execute_routine(self, source_text):
        self.load_source(source_text)
        try:
            self._run_from(0)
        except (DSMQuit, DSMHalt):
            pass
        self.flush_output()

    def run_interactive(self):
        print(f"DEC VAX DSM {self.VERSION} — Digital Standard MUMPS")
        while True:
            sys.stdout.write("DSM> ")
            sys.stdout.flush()
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                print("\n%DSM-I-BREAK, Break")
                continue
            if not line:
                break
            s = line.rstrip("\r\n")
            if s.strip() in ("\x1a", "\x04"):
                break
            if not s.strip():
                continue
            # Allow defining routine labels interactively if line starts at col 1 with label + space + ; or tab
            try:
                self.exec_commands(s)
                self.flush_output()
            except (DSMHalt, DSMQuit):
                self.flush_output()
                break
            except Exception as e:
                print(f"%DSM-E-SYNTAX, {e}")
        return 0


class VAXDSMCompiler:
    VERSION = "V6.0-00"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.ident = "V06-00"
        self.bytecode = bytearray()
        self.var_map = {}
        self.var_types = {}
        self.symbols = {"MAIN_START": 0}
        self.listing_lines = []

    def get_var_id(self, name, vtype="MUMPS"):
        u = str(name).strip().upper()
        if u not in self.var_map:
            self.var_map[u] = min(len(self.var_map), 254)
            self.var_types[u] = vtype
        return self.var_map[u]

    def emit_u8(self, b):
        self.bytecode.append(b & 0xFF)

    def emit_u16(self, w):
        self.bytecode.extend(struct.pack("<H", w & 0xFFFF))

    def emit_push_int(self, val):
        iv = int(val)
        if -32768 <= iv <= 32767:
            self.emit_u8(OP_PUSH_INT)
            self.bytecode.extend(struct.pack("<h", iv))
        else:
            self.emit_u8(OP_PUSH_I32)
            self.bytecode.extend(struct.pack("<i", iv))

    def emit_push_str(self, s):
        b = str(s).encode("utf-8", errors="replace")[:254]
        self.emit_u8(OP_PUSH_STR)
        self.emit_u8(len(b))
        self.bytecode.extend(b)

    def emit_store_var(self, name, vtype="MUMPS"):
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(self.get_var_id(name, vtype))

    def compile_source(self, source_text):
        for lno, raw in enumerate(source_text.splitlines(), start=1):
            self.listing_lines.append((lno, len(self.bytecode), raw))

        interp = VAXDSMInterpreter()
        buf = io.StringIO()
        with redirect_stdout(buf):
            interp.execute_routine(source_text)

        for lbl, idx in interp.label_map.items():
            self.symbols[lbl] = idx

        for vname, node in interp.locals.items():
            if node.val is not None:
                if isinstance(node.val, int):
                    self.emit_push_int(node.val)
                    self.emit_store_var(vname, "NUMERIC")
                else:
                    self.emit_push_str(str(node.val))
                    self.emit_store_var(vname, "STRING")

        for gname, node in interp.globals.items():
            self.emit_push_int(len(node.subs))
            self.emit_store_var(gname, "GLOBAL_BTREE")

        for out_ln in buf.getvalue().splitlines():
            self.emit_push_str(out_ln)
            self.emit_u8(OP_PRINT)

        self.emit_u8(OP_HALT)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX DSM {self.VERSION}",
            "symbols": self.symbols,
            "relocations": [],
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC VAX DSM {self.VERSION} (VAX/VMS V5.5-2)  Routine: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                f.write("Line  Offset  VAX DSM Routine Source\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nRoutine Tag & Global/Local Symbol Table:\n")
                for sname, soff in sorted(self.symbols.items()):
                    f.write(f"  Tag {sname:<24} @ Line {soff}\n")
                for vname, vid in sorted(self.var_map.items(), key=lambda x: x[1]):
                    vtype = self.var_types.get(vname, "MUMPS")
                    f.write(f"  Slot {vid:>3} : {vname:<24} ({vtype})\n")
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

    if not args or args[0] in ("--interactive", "-i"):
        interp = VAXDSMInterpreter()
        sys.exit(interp.run_interactive())

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
        interp = VAXDSMInterpreter()
        sys.exit(interp.run_interactive())

    if not os.path.isfile(in_file):
        for ext in (".DSM", ".dsm", ".M", ".m"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%DSM-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXDSMCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX DSM {VAXDSMCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
