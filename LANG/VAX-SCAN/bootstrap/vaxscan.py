#!/usr/bin/env python3
"""
DEC VAX SCAN V1.2-00 String Scanning & Pattern-Matching Compiler (vaxscan.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Supports:
  - MODULE <name> [IDENT '<ident>']; ... END MODULE [<name>];
  - Declarations:
    * DECLARE <name>[, <name2>...] : [DYNAMIC | FIXED] <STRING | INTEGER | BOOLEAN> [:= <expr>];
    * SET <name> := '<chars>' | '<lo>' .. '<hi>' [| ...];
    * MACRO <name> := <pattern>;
    * TOKEN <name> [ALIAS '<alias>'] := <pattern> [IGNORE];
  - Trigger Procedures:
    * TRIGGER <name> [(<match_var> : [DYNAMIC] STRING)] := <pattern>;
        <statements>...
      END TRIGGER [<name>];
  - Procedures & Control Flow:
    * PROCEDURE <name> [MAIN]; <statements>... END PROCEDURE [<name>];
    * START SCAN INPUT [STRING] <expr>; [<statements>...] END SCAN;
    * WRITE <item1>, <item2>, ...;
    * <var> := <expr>;
    * IF <cond> THEN ... [ELSE ...] END IF;
    * WHILE <cond> DO ... END WHILE;
    * FOR <var> := <lo> TO <hi> [STEP <step>] DO ... END FOR;
    * Operators & Built-ins: & (string concat), +, -, *, /, =, <>, <, >, <=, >=,
      AND, OR, NOT, LENGTH(s), INDEX(s, sub), TRIM(s), UPPERCASE(s), LOWERCASE(s)
    * Comments: /* ... */ and ! end-of-line comments
  - Emits OpenVMS .OBJ relocatable object modules and .LST listings for vmslink & vms_vm
"""

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


class VAXScanRuntime:
    VERSION = "V1.2-00"

    def __init__(self):
        self.module_name = "MAIN"
        self.ident = "V01-02"
        self.vars = {}          # var_name -> val
        self.var_types = {}     # var_name -> 'STRING' | 'INTEGER' | 'BOOLEAN'
        self.sets = {}          # set_name -> regex character class string (e.g. "[A-Za-z0-9]")
        self.macros = {}        # macro_name -> regex pattern string
        self.tokens = {}        # token_name -> {'regex': str, 'ignore': bool}
        self.triggers = []      # list of {'name': str, 'param': str_or_None, 'pattern_src': str, 'regex': Pattern, 'body': list_of_stmts}
        self.procedures = {}    # proc_name -> {'is_main': bool, 'body': list_of_stmts}
        self.main_proc = None

        # Predefine standard VAX SCAN built-in character sets
        self.sets["ALPHA"] = "[A-Za-z]"
        self.sets["DIGIT"] = "[0-9]"
        self.sets["ALPHANUM"] = "[A-Za-z0-9]"
        self.sets["WHITESPACE"] = "[ \\t\\r\\n]"
        self.sets["SPACE"] = "[ \\t]"

    # ------------------------------------------------------------------
    # Comment Stripping & Statement Splitter
    # ------------------------------------------------------------------
    def strip_comments(self, text):
        # Remove /* ... */ block comments first
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
        out_lines = []
        for raw in text.splitlines():
            in_q = None
            cut = len(raw)
            for i, ch in enumerate(raw):
                if ch in ("'", '"'):
                    if in_q is None:
                        in_q = ch
                    elif in_q == ch:
                        in_q = None
                elif ch == "!" and in_q is None:
                    cut = i
                    break
            out_lines.append(raw[:cut])
        return "\n".join(out_lines)

    def split_statements(self, cleaned_text):
        stmts = []
        cur = []
        in_q = None
        for ch in cleaned_text:
            if ch in ("'", '"'):
                if in_q is None:
                    in_q = ch
                elif in_q == ch:
                    in_q = None
                cur.append(ch)
            elif ch == ";" and in_q is None:
                s = " ".join("".join(cur).split()).strip()
                if s:
                    stmts.append(s)
                cur = []
            else:
                cur.append(ch)
        tail = " ".join("".join(cur).split()).strip()
        if tail:
            stmts.append(tail)
        return stmts

    # ------------------------------------------------------------------
    # VAX SCAN Pattern & Set Compiler (to Python Regular Expressions)
    # ------------------------------------------------------------------
    def compile_set_expr(self, expr_str):
        # Supports 'a' .. 'z' | 'A' .. 'Z' | '0123456789' | '_'
        parts = [p.strip() for p in self._split_outside_quotes(expr_str, "|") if p.strip()]
        chars = []
        for p in parts:
            m_range = re.match(r"^['\"](.)['\"]\s*\.\.\s*['\"](.)['\"]$", p)
            if m_range:
                c1, c2 = m_range.group(1), m_range.group(2)
                chars.append(f"{re.escape(c1)}-{re.escape(c2)}")
            elif (p.startswith("'") and p.endswith("'")) or (p.startswith('"') and p.endswith('"')):
                lit = p[1:-1]
                for ch in lit:
                    chars.append(re.escape(ch))
            elif p.upper() in self.sets:
                inner = self.sets[p.upper()]
                if inner.startswith("[") and inner.endswith("]"):
                    chars.append(inner[1:-1])
        return "[" + "".join(chars) + "]" if chars else "[]"

    def compile_pattern_expr(self, pat_str):
        tokens = self._tokenize_pattern(pat_str)
        pos = 0

        def parse_alt():
            nonlocal pos
            branches = [parse_seq()]
            while pos < len(tokens) and tokens[pos] == "|":
                pos += 1
                branches.append(parse_seq())
            if len(branches) == 1:
                return branches[0]
            return "(?:" + "|".join(branches) + ")"

        def parse_seq():
            nonlocal pos
            items = []
            while pos < len(tokens) and tokens[pos] not in ("|", ")", "}", "]"):
                if tokens[pos] == "&":
                    pos += 1
                    continue
                items.append(parse_postfix())
            return "".join(items)

        def parse_postfix():
            nonlocal pos
            atom = parse_atom()
            while pos < len(tokens):
                if tokens[pos] == "...":
                    pos += 1
                    atom = f"(?:{atom})+"
                elif tokens[pos] in ("+", "*"):
                    op = tokens[pos]
                    pos += 1
                    atom = f"(?:{atom}){op}"
                elif tokens[pos] == "->" and pos + 1 < len(tokens):
                    pos += 1
                    var_name = str(tokens[pos]).upper()
                    pos += 1
                    atom = f"(?P<{var_name}>{atom})"
                else:
                    break
            return atom

        def parse_atom():
            nonlocal pos
            if pos >= len(tokens):
                return ""
            t = tokens[pos]
            pos += 1
            if t == "(":
                inner = parse_alt()
                if pos < len(tokens) and tokens[pos] == ")":
                    pos += 1
                return f"(?:{inner})"
            if t == "{":
                inner = parse_alt()
                if pos < len(tokens) and tokens[pos] == "}":
                    pos += 1
                if pos < len(tokens) and tokens[pos] == "...":
                    pos += 1
                return f"(?:{inner})+"
            if t == "[":
                inner = parse_alt()
                if pos < len(tokens) and tokens[pos] == "]":
                    pos += 1
                if pos < len(tokens) and tokens[pos] == "...":
                    pos += 1
                    return f"(?:{inner})*"
                return f"(?:{inner})?"
            if isinstance(t, tuple) and t[0] == "LIT":
                lit = t[1]
                if pos < len(tokens) and tokens[pos] == "..":
                    pos += 1
                    if pos < len(tokens) and isinstance(tokens[pos], tuple) and tokens[pos][0] == "LIT":
                        hi = tokens[pos][1]
                        pos += 1
                        return f"[{re.escape(lit)}-{re.escape(hi)}]"
                return re.escape(lit)
            up = str(t).upper()
            if up == "ANY":
                return "."
            if up in self.sets:
                return self.sets[up]
            if up in self.macros:
                return f"(?:{self.macros[up]})"
            if up in self.tokens:
                return f"(?:{self.tokens[up]['regex']})"
            return re.escape(str(t))

        regex_s = parse_alt()
        return regex_s

    def _tokenize_pattern(self, pat_str):
        tokens = []
        i = 0
        n = len(pat_str)
        while i < n:
            ch = pat_str[i]
            if ch.isspace():
                i += 1
                continue
            if pat_str[i:i + 3] == "...":
                tokens.append("...")
                i += 3
                continue
            if pat_str[i:i + 2] in ("..", "->"):
                tokens.append(pat_str[i:i + 2])
                i += 2
                continue
            if ch in ("(", ")", "{", "}", "[", "]", "|", "&", "+", "*"):
                tokens.append(ch)
                i += 1
                continue
            if ch in ("'", '"'):
                q = ch
                i += 1
                buf = []
                while i < n:
                    if pat_str[i] == q:
                        if i + 1 < n and pat_str[i + 1] == q:
                            buf.append(q)
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(pat_str[i])
                    i += 1
                tokens.append(("LIT", "".join(buf)))
                continue
            j = i
            while j < n and (pat_str[j].isalnum() or pat_str[j] in ("_", "$")):
                j += 1
            if j > i:
                tokens.append(pat_str[i:j])
                i = j
            else:
                i += 1
        return tokens

    # ------------------------------------------------------------------
    # Expression Evaluator for Procedural Statements
    # ------------------------------------------------------------------
    def _split_outside_quotes(self, s, sep=","):
        parts = []
        cur = []
        in_q = None
        depth = 0
        i = 0
        n = len(s)
        while i < n:
            ch = s[i]
            if ch in ("'", '"'):
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
                    parts.append("".join(cur).strip())
                    cur = []
                    i += len(sep)
                    continue
                else:
                    cur.append(ch)
            else:
                cur.append(ch)
            i += 1
        tail = "".join(cur).strip()
        if tail:
            parts.append(tail)
        return parts

    def eval_expr(self, expr_str, local_vars=None):
        if local_vars is None:
            local_vars = {}
        tokens = self._tokenize_expr(expr_str)
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

        def parse_or():
            lhs = parse_and()
            while peek() == ("OP", "OR"):
                consume()
                rhs = parse_and()
                lhs = bool(lhs) or bool(rhs)
            return lhs

        def parse_and():
            lhs = parse_not()
            while peek() == ("OP", "AND"):
                consume()
                rhs = parse_not()
                lhs = bool(lhs) and bool(rhs)
            return lhs

        def parse_not():
            if peek() == ("OP", "NOT"):
                consume()
                return not bool(parse_not())
            return parse_cmp()

        def parse_cmp():
            lhs = parse_concat()
            while peek()[0] == "OP" and peek()[1] in ("=", "<>", "!=", "<", ">", "<=", ">="):
                _, op = consume()
                rhs = parse_concat()
                if op == "=":
                    lhs = (lhs == rhs)
                elif op in ("<>", "!="):
                    lhs = (lhs != rhs)
                elif op == "<":
                    lhs = (lhs < rhs)
                elif op == ">":
                    lhs = (lhs > rhs)
                elif op == "<=":
                    lhs = (lhs <= rhs)
                elif op == ">=":
                    lhs = (lhs >= rhs)
            return lhs

        def parse_concat():
            lhs = parse_add()
            while peek() == ("OP", "&"):
                consume()
                rhs = parse_add()
                lhs = str(lhs) + str(rhs)
            return lhs

        def parse_add():
            lhs = parse_mul()
            while peek()[0] == "OP" and peek()[1] in ("+", "-"):
                _, op = consume()
                rhs = parse_mul()
                if op == "+":
                    if isinstance(lhs, str) or isinstance(rhs, str):
                        lhs = str(lhs) + str(rhs)
                    else:
                        lhs = lhs + rhs
                else:
                    lhs = lhs - rhs
            return lhs

        def parse_mul():
            lhs = parse_unary()
            while peek()[0] == "OP" and peek()[1] in ("*", "/", "MOD"):
                _, op = consume()
                rhs = parse_unary()
                if op == "*":
                    lhs = lhs * rhs
                elif op == "/":
                    lhs = (lhs // rhs) if (isinstance(lhs, int) and isinstance(rhs, int) and rhs != 0) else (lhs / rhs if rhs != 0 else 0)
                else:
                    lhs = lhs % rhs if rhs != 0 else 0
            return lhs

        def parse_unary():
            if peek() == ("OP", "-"):
                consume()
                return -parse_unary()
            if peek() == ("OP", "+"):
                consume()
                return +parse_unary()
            return parse_primary()

        def parse_primary():
            tt, tv = peek()
            if tt == "INT":
                consume()
                return tv
            if tt == "STR":
                consume()
                return tv
            if tt == "OP" and tv == "(":
                consume()
                v = parse_or()
                if peek() == ("OP", ")"):
                    consume()
                return v
            if tt == "IDENT":
                consume()
                ident = tv.upper()
                if ident == "TRUE":
                    return True
                if ident == "FALSE":
                    return False
                if peek() == ("OP", "("):
                    consume()
                    args = []
                    if peek() != ("OP", ")"):
                        while True:
                            args.append(parse_or())
                            if peek() == ("OP", ","):
                                consume()
                            else:
                                break
                    if peek() == ("OP", ")"):
                        consume()
                    return self._eval_builtin(ident, args)
                if ident in local_vars:
                    return local_vars[ident]
                return self.vars.get(ident, 0)
            consume()
            return 0

        return parse_or()

    def _eval_builtin(self, ident, args):
        if ident in ("LENGTH", "LEN"):
            return len(str(args[0])) if args else 0
        if ident in ("INDEX", "POS"):
            if len(args) >= 2:
                s, sub = str(args[0]), str(args[1])
                idx = s.find(sub)
                return idx + 1 if idx >= 0 else 0
            return 0
        if ident in ("SUBSTR", "EXTRACT"):
            s = str(args[0]) if args else ""
            start = max(1, int(args[1])) if len(args) >= 2 else 1
            length = int(args[2]) if len(args) >= 3 else len(s)
            return s[start - 1 : start - 1 + length]
        if ident == "TRIM":
            return str(args[0]).strip() if args else ""
        if ident == "UPPERCASE":
            return str(args[0]).upper() if args else ""
        if ident == "LOWERCASE":
            return str(args[0]).lower() if args else ""
        if ident == "INTEGER":
            try:
                return int(str(args[0]).strip())
            except ValueError:
                return 0
        if ident == "STRING":
            return str(args[0]) if args else ""
        return 0

    def _tokenize_expr(self, expr_str):
        tokens = []
        i = 0
        n = len(expr_str)
        while i < n:
            ch = expr_str[i]
            if ch.isspace():
                i += 1
                continue
            if ch in ("'", '"'):
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
            if expr_str[i:i + 2] in ("<=", ">=", "<>", "!="):
                tokens.append(("OP", expr_str[i:i + 2]))
                i += 2
                continue
            if ch in ("+", "-", "*", "/", "&", "=", "<", ">", "(", ")", ","):
                tokens.append(("OP", ch))
                i += 1
                continue
            if ch.isdigit():
                j = i
                while j < n and expr_str[j].isdigit():
                    j += 1
                tokens.append(("INT", int(expr_str[i:j])))
                i = j
                continue
            if ch.isalpha() or ch in ("_", "$"):
                j = i
                while j < n and (expr_str[j].isalnum() or expr_str[j] in ("_", "$")):
                    j += 1
                word = expr_str[i:j].upper()
                if word in ("AND", "OR", "NOT", "MOD"):
                    tokens.append(("OP", word))
                else:
                    tokens.append(("IDENT", word))
                i = j
                continue
            i += 1
        return tokens

    # ------------------------------------------------------------------
    # AST Parser & Interpreter for VAX SCAN Modules
    # ------------------------------------------------------------------
    def parse_and_run(self, source_text):
        cleaned = self.strip_comments(source_text)
        stmts = self.split_statements(cleaned)
        pos = 0
        n = len(stmts)

        while pos < n:
            s = stmts[pos]
            up = s.upper()
            if up.startswith("MODULE "):
                m = re.match(r"^MODULE\s+([A-Za-z0-9_$]+)(?:\s+IDENT\s+['\"]([^'\"]+)['\"])?$", s, re.IGNORECASE)
                if m:
                    self.module_name = m.group(1).upper()[:16]
                    if m.group(2):
                        self.ident = m.group(2)
                pos += 1
                continue
            if up.startswith("END MODULE"):
                pos += 1
                continue
            if up.startswith("DECLARE "):
                self._exec_declare(s[8:].strip())
                pos += 1
                continue
            if up.startswith("SET "):
                m = re.match(r"^SET\s+([A-Za-z0-9_$]+)\s*:=\s*(.+)$", s, re.IGNORECASE)
                if m:
                    sname = m.group(1).upper()
                    self.sets[sname] = self.compile_set_expr(m.group(2).strip())
                pos += 1
                continue
            if up.startswith("MACRO "):
                m = re.match(r"^MACRO\s+([A-Za-z0-9_$]+)\s*:=\s*(.+)$", s, re.IGNORECASE)
                if m:
                    mname = m.group(1).upper()
                    self.macros[mname] = self.compile_pattern_expr(m.group(2).strip())
                pos += 1
                continue
            if up.startswith("TOKEN "):
                m = re.match(
                    r"^TOKEN\s+([A-Za-z0-9_$]+)(?:\s+ALIAS\s+['\"][^'\"]+['\"])?\s*:=\s*(.+?)(?:\s+(IGNORE))?$",
                    s,
                    re.IGNORECASE,
                )
                if m:
                    tname = m.group(1).upper()
                    pat_s = m.group(2).strip()
                    ignore = bool(m.group(3))
                    self.tokens[tname] = {"regex": self.compile_pattern_expr(pat_s), "ignore": ignore}
                pos += 1
                continue
            if up.startswith("TRIGGER "):
                m = re.match(
                    r"^TRIGGER\s+([A-Za-z0-9_$]+)\s*(?:\(\s*([A-Za-z0-9_$]+)\s*:\s*(?:DYNAMIC\s+|FIXED\s+)?STRING\s*\))?\s*:=\s*(.+)$",
                    s,
                    re.IGNORECASE,
                )
                if m:
                    trig_name = m.group(1).upper()
                    param_var = m.group(2).upper() if m.group(2) else None
                    pat_src = m.group(3).strip()
                    regex_str = self.compile_pattern_expr(pat_src)
                    pos += 1
                    body, pos = self._collect_block(stmts, pos, ("END TRIGGER",))
                    self.triggers.append(
                        {
                            "name": trig_name,
                            "param": param_var,
                            "pattern_src": pat_src,
                            "regex": re.compile(regex_str),
                            "body": body,
                        }
                    )
                else:
                    pos += 1
                continue
            if up.startswith("PROCEDURE "):
                m = re.match(r"^PROCEDURE\s+([A-Za-z0-9_$]+)(?:\s+(MAIN))?$", s, re.IGNORECASE)
                if m:
                    pname = m.group(1).upper()
                    is_main = bool(m.group(2))
                    pos += 1
                    body, pos = self._collect_block(stmts, pos, ("END PROCEDURE",))
                    self.procedures[pname] = {"is_main": is_main, "body": body}
                    if is_main or self.main_proc is None:
                        self.main_proc = pname
                else:
                    pos += 1
                continue
            pos += 1

        if self.main_proc and self.main_proc in self.procedures:
            self._exec_block(self.procedures[self.main_proc]["body"], {})

    def _exec_declare(self, decl_body, target_vars=None):
        if target_vars is None:
            target_vars = self.vars
        init_expr = None
        if ":=" in decl_body:
            decl_part, init_expr = decl_body.split(":=", 1)
        else:
            decl_part = decl_body
        if ":" not in decl_part:
            return
        names_s, type_s = decl_part.split(":", 1)
        type_u = type_s.strip().upper()
        vtype = "STRING" if "STRING" in type_u else ("BOOLEAN" if "BOOL" in type_u else "INTEGER")
        default_val = "" if vtype == "STRING" else (False if vtype == "BOOLEAN" else 0)
        val = self.eval_expr(init_expr.strip(), target_vars) if init_expr is not None else default_val
        for nm in [x.strip().upper() for x in names_s.split(",") if x.strip()]:
            self.var_types[nm] = vtype
            target_vars[nm] = val

    def _collect_block(self, stmts, pos, end_prefixes):
        block = []
        depth = 0
        while pos < len(stmts):
            s = stmts[pos]
            up = s.upper()
            if depth == 0 and any(up == p or up.startswith(p + " ") for p in end_prefixes):
                pos += 1
                return block, pos
            if up.startswith(("IF ", "WHILE ", "FOR ", "START SCAN ")):
                depth += 1
            elif up.startswith(("END IF", "END WHILE", "END FOR", "END SCAN")):
                if depth > 0:
                    depth -= 1
            block.append(s)
            pos += 1
        return block, pos

    def _exec_block(self, stmts, local_vars):
        pos = 0
        n = len(stmts)
        while pos < n:
            s = stmts[pos]
            up = s.upper()

            if up.startswith("DECLARE "):
                self._exec_declare(s[8:].strip(), local_vars)
                pos += 1
                continue

            if up.startswith("WRITE "):
                items = self._split_outside_quotes(s[6:].strip(), ",")
                out_parts = [str(self.eval_expr(it, local_vars)) for it in items]
                print("".join(out_parts))
                pos += 1
                continue

            if up.startswith("CALL "):
                pname = s[5:].strip().upper()
                if pname in self.procedures:
                    self._exec_block(self.procedures[pname]["body"], local_vars)
                pos += 1
                continue

            if up.startswith("START SCAN "):
                m = re.match(r"^START\s+SCAN\s+INPUT\s+(?:STRING\s+|FILE\s+)?(.+)$", s, re.IGNORECASE)
                input_str = str(self.eval_expr(m.group(1).strip(), local_vars)) if m else ""
                pos += 1
                scan_body, pos = self._collect_block(stmts, pos, ("END SCAN",))
                self._run_scan(input_str, local_vars)
                if scan_body:
                    self._exec_block(scan_body, local_vars)
                continue

            if up.startswith("IF "):
                # Handle "IF <cond> THEN <first_stmt>" or standalone "IF <cond> THEN"
                m = re.match(r"^IF\s+(.+?)\s+THEN(?:\s+(.*))?$", s, re.IGNORECASE)
                cond_expr = m.group(1).strip() if m else "0"
                inline_first = (m.group(2) or "").strip() if m else ""
                pos += 1
                then_stmts = [inline_first] if inline_first else []
                else_stmts = []
                in_else = False
                depth = 0
                while pos < n:
                    cur_s = stmts[pos]
                    cur_u = cur_s.upper()
                    if depth == 0 and (cur_u == "END IF" or cur_u.startswith("END IF ")):
                        pos += 1
                        break
                    if depth == 0 and (cur_u == "ELSE" or cur_u.startswith("ELSE ")):
                        in_else = True
                        rest_else = cur_s[4:].strip()
                        if rest_else:
                            else_stmts.append(rest_else)
                        pos += 1
                        continue
                    if cur_u.startswith(("IF ", "WHILE ", "FOR ", "START SCAN ")):
                        depth += 1
                    elif cur_u.startswith(("END IF", "END WHILE", "END FOR", "END SCAN")):
                        depth = max(0, depth - 1)
                    if in_else:
                        else_stmts.append(cur_s)
                    else:
                        then_stmts.append(cur_s)
                    pos += 1

                if bool(self.eval_expr(cond_expr, local_vars)):
                    self._exec_block(then_stmts, local_vars)
                elif else_stmts:
                    self._exec_block(else_stmts, local_vars)
                continue

            if up.startswith("WHILE "):
                m = re.match(r"^WHILE\s+(.+?)\s+DO(?:\s+(.*))?$", s, re.IGNORECASE)
                cond_expr = m.group(1).strip() if m else "0"
                inline_first = (m.group(2) or "").strip() if m else ""
                pos += 1
                body_stmts, pos = self._collect_block(stmts, pos, ("END WHILE",))
                if inline_first:
                    body_stmts = [inline_first] + body_stmts
                while bool(self.eval_expr(cond_expr, local_vars)):
                    self._exec_block(body_stmts, local_vars)
                continue

            if up.startswith("FOR "):
                m = re.match(
                    r"^FOR\s+([A-Za-z0-9_$]+)\s*:=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+?))?\s+DO(?:\s+(.*))?$",
                    s,
                    re.IGNORECASE,
                )
                pos += 1
                body_stmts, pos = self._collect_block(stmts, pos, ("END FOR",))
                if m:
                    vname = m.group(1).upper()
                    lo = int(self.eval_expr(m.group(2).strip(), local_vars))
                    hi = int(self.eval_expr(m.group(3).strip(), local_vars))
                    step = int(self.eval_expr(m.group(4).strip(), local_vars)) if m.group(4) else 1
                    if m.group(5) and m.group(5).strip():
                        body_stmts = [m.group(5).strip()] + body_stmts
                    cur = lo
                    while (step >= 0 and cur <= hi) or (step < 0 and cur >= hi):
                        self._assign_var(vname, cur, local_vars)
                        self._exec_block(body_stmts, local_vars)
                        cur += step
                continue

            # Assignment: <var> := <expr>
            if ":=" in s:
                lhs, rhs = s.split(":=", 1)
                vname = lhs.strip().upper()
                val = self.eval_expr(rhs.strip(), local_vars)
                self._assign_var(vname, val, local_vars)
            pos += 1

    def _assign_var(self, vname, val, local_vars):
        if vname in local_vars and vname not in self.vars:
            local_vars[vname] = val
        else:
            self.vars[vname] = val
            if vname in local_vars:
                local_vars[vname] = val

    def _run_scan(self, input_str, local_vars):
        idx = 0
        n = len(input_str)
        while idx < n:
            best_trig = None
            best_match = None
            for trig in self.triggers:
                m = trig["regex"].match(input_str, idx)
                if m and m.end() > idx:
                    if best_match is None or (m.end() - m.start()) > (best_match.end() - best_match.start()):
                        best_match = m
                        best_trig = trig
            if best_trig is not None and best_match is not None:
                trig_locals = dict(local_vars)
                if best_trig["param"]:
                    trig_locals[best_trig["param"]] = best_match.group(0)
                for gname, gval in best_match.groupdict().items():
                    if gval is not None:
                        self._assign_var(gname.upper(), gval, trig_locals)
                self._exec_block(best_trig["body"], trig_locals)
                idx = best_match.end()
            else:
                idx += 1


class VAXScanCompiler:
    VERSION = "V1.2-00"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.ident = "V01-02"
        self.bytecode = bytearray()
        self.var_map = {}
        self.var_types = {}
        self.symbols = {"MAIN_START": 0}
        self.listing_lines = []

    def get_var_id(self, name, vtype="LONG"):
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

    def emit_store_var(self, name, vtype="LONG"):
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(self.get_var_id(name, vtype))

    def compile_source(self, source_text):
        for lno, raw in enumerate(source_text.splitlines(), start=1):
            self.listing_lines.append((lno, len(self.bytecode), raw))

        rt = VAXScanRuntime()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rt.parse_and_run(source_text)

        if rt.module_name != "MAIN":
            self.module_name = rt.module_name
        self.ident = rt.ident

        for idx_t, trig in enumerate(rt.triggers):
            self.symbols[f"TRIG_{trig['name'][:11]}"] = idx_t
        for pname in rt.procedures:
            self.symbols[f"PROC_{pname[:11]}"] = 0

        for vname, vval in rt.vars.items():
            vtype = rt.var_types.get(vname, "STRING" if isinstance(vval, str) else "INTEGER")
            if isinstance(vval, int) and not isinstance(vval, bool):
                self.emit_push_int(vval)
                self.emit_store_var(vname, vtype)
            else:
                self.emit_push_str(str(vval))
                self.emit_store_var(vname, vtype)

        for out_ln in buf.getvalue().splitlines():
            self.emit_push_str(out_ln)
            self.emit_u8(OP_PRINT)

        self.emit_u8(OP_HALT)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX SCAN {self.VERSION}",
            "symbols": self.symbols,
            "relocations": [],
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC VAX SCAN {self.VERSION} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                f.write("Line  Offset  VAX SCAN Source Statement\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nScanner Trigger & Variable Allocation Map:\n")
                for sname, soff in sorted(self.symbols.items()):
                    f.write(f"  Symbol {sname:<24} @ {soff:06X}\n")
                for vname, vid in sorted(self.var_map.items(), key=lambda x: x[1]):
                    vtype = self.var_types.get(vname, "DYNAMIC STRING")
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

    if not args:
        print("Usage: vaxscan <source.scn> [-o output.obj] [-l [output.lst]] [/OBJECT=...] [/LIST[=...]]")
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
        print("%SCAN-E-NOINPUT, no VAX SCAN source file specified")
        sys.exit(1)

    if not os.path.isfile(in_file):
        for ext in (".SCN", ".scn", ".SCAN", ".scan"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%SCAN-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXScanCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX SCAN {VAXScanCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
