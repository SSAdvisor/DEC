#!/usr/bin/env python3
"""
DEC VAX OPS5 V2.2-00 Rule-Based Production System Compiler & Shell (vaxops5.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Supports:
  - Authentic Forgy Rete Rule-Based Production System Language:
    * (literalize <class> <attr1> <attr2> ...)
    * (vector-attribute <attr1> ...)
    * (strategy lex | mea)
    * (p <rule-name> <lhs-ce>... --> <rhs-action>...)
      - Positive CEs: (<class> ^<attr> <test-or-var> ...) and {<ce> <ce-var>}
      - Negated CEs:  - (<class> ^<attr> <test-or-var> ...)
      - Relational tests: =, <>, <, >, <=, >=, << v1 v2 ... >>, { test1 test2 }
      - RHS actions: (make ...), (modify <ce> ...), (remove <ce> ...),
        (write (crlf) (tabto N) ...), (bind <var> [(compute ...)]), (halt)
    * (startup (make ...) ...) and top-level (make ...), (run [N])
  - Interactive OPS5 Shell (DEC VAX OPS5 V2.2-00 — Production System Environment, OPS5> prompt):
    * (make ...), (wm), (pm), (run [n]), (reset), (watch 0|1|2), (strategy lex|mea), (exit)/(quit)
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


class OPS5Quit(Exception):
    pass


class OPS5Engine:
    VERSION = "V2.2-00"

    def __init__(self):
        self.classes = {}          # class_name -> list of attr names
        self.vector_attrs = set()  # set of vector attribute names
        self.strategy = "LEX"      # LEX or MEA
        self.watch_level = 0       # 0, 1, or 2
        self.rules = []            # list of rule dicts
        self.startup_actions = []  # list of RHS action forms from (startup ...)
        self.wm = {}               # timetag (int) -> {'id': int, 'class': str, 'attrs': dict, 'stamp': int}
        self.next_timetag = 1
        self.cycle_count = 0
        self.refracted = set()     # set of (rule_name, tuple_of_timetags)
        self.halted = False
        self.did_run = False
        self._out_buf = []         # current line buffer before (crlf)

    # ------------------------------------------------------------------
    # Tokenizer & S-expression Parser for OPS5
    # ------------------------------------------------------------------
    def tokenize(self, text):
        tokens = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch.isspace():
                i += 1
                continue
            if ch == ";":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            if text[i:i + 3] == "-->":
                tokens.append("-->")
                i += 3
                continue
            if text[i:i + 2] in ("<<", ">>", "<>", "<=", ">=", "//", "\\\\"):
                tokens.append(text[i:i + 2])
                i += 2
                continue
            if ch in ("(", ")", "{", "}", "^"):
                tokens.append(ch)
                i += 1
                continue
            if ch in ("|", '"'):
                delim = ch
                i += 1
                buf = []
                while i < n and text[i] != delim:
                    buf.append(text[i])
                    i += 1
                i += 1
                tokens.append(("STR", "".join(buf)))
                continue
            if ch == "<":
                # Check if variable <var> vs relational <
                j = i + 1
                if j < n and (not text[j].isspace()) and text[j] not in ("(", ")", "{", "}", "="):
                    while j < n and text[j] != ">" and (not text[j].isspace()) and text[j] not in ("(", ")"):
                        j += 1
                    if j < n and text[j] == ">":
                        tokens.append(text[i:j + 1].upper())
                        i = j + 1
                        continue
                tokens.append("<")
                i += 1
                continue
            if ch in (">", "="):
                tokens.append(ch)
                i += 1
                continue
            j = i
            while j < n and (not text[j].isspace()) and text[j] not in ("(", ")", "{", "}", "|", '"', ";", "^"):
                if text[j:j + 3] == "-->":
                    break
                j += 1
            tok = text[i:j]
            tokens.append(tok)
            i = j
        return tokens

    def parse_forms(self, text):
        tokens = self.tokenize(text)
        pos = 0

        def read_item():
            nonlocal pos
            if pos >= len(tokens):
                return None
            tok = tokens[pos]
            pos += 1
            if tok == "(":
                lst = []
                while pos < len(tokens) and tokens[pos] != ")":
                    lst.append(read_item())
                if pos < len(tokens) and tokens[pos] == ")":
                    pos += 1
                return lst
            if tok == "{":
                lst = ["__BRACE__"]
                while pos < len(tokens) and tokens[pos] != "}":
                    lst.append(read_item())
                if pos < len(tokens) and tokens[pos] == "}":
                    pos += 1
                return lst
            if isinstance(tok, tuple) and tok[0] == "STR":
                return tok[1]
            if re.match(r"^[+-]?\d+$", str(tok)):
                return int(tok)
            if re.match(r"^[+-]?\d*\.\d+$", str(tok)):
                return float(tok)
            return str(tok).upper()

        forms = []
        while pos < len(tokens):
            it = read_item()
            if it is not None:
                forms.append(it)
        return forms

    def is_var(self, x):
        return isinstance(x, str) and len(x) >= 3 and x.startswith("<") and x.endswith(">")

    # ------------------------------------------------------------------
    # Top-Level Form Execution
    # ------------------------------------------------------------------
    def eval_form(self, form):
        if not isinstance(form, list) or not form:
            return None
        head = str(form[0]).upper()

        if head in ("EXIT", "QUIT", "BYE"):
            self._flush_output()
            raise OPS5Quit()

        if head == "LITERALIZE":
            cls_name = str(form[1]).upper()
            attrs = [str(a).upper() for a in form[2:] if str(a) != "^"]
            self.classes[cls_name] = attrs
            return cls_name

        if head == "VECTOR-ATTRIBUTE":
            for a in form[1:]:
                self.vector_attrs.add(str(a).upper())
            return None

        if head == "STRATEGY":
            if len(form) > 1:
                self.strategy = str(form[1]).upper()
            return self.strategy

        if head == "WATCH":
            if len(form) > 1:
                self.watch_level = int(form[1])
            return self.watch_level

        if head == "P":
            rule = self._parse_production(form)
            # Replace if same name exists
            self.rules = [r for r in self.rules if r["name"] != rule["name"]]
            self.rules.append(rule)
            return rule["name"]

        if head == "STARTUP":
            self.startup_actions.extend(form[1:])
            for act in form[1:]:
                self._exec_rhs_action(act, {}, [])
            self._flush_output()
            return None

        if head == "MAKE":
            wme = self._make_wme(form[1:], {})
            return wme["id"]

        if head == "REMOVE":
            for arg in form[1:]:
                if arg == "*":
                    self.wm.clear()
                else:
                    self.wm.pop(int(arg), None)
            return None

        if head == "RESET":
            self.wm.clear()
            self.next_timetag = 1
            self.cycle_count = 0
            self.refracted.clear()
            self.halted = False
            for act in self.startup_actions:
                self._exec_rhs_action(act, {}, [])
            self._flush_output()
            return None

        if head == "WM":
            self._flush_output()
            for tid in sorted(self.wm.keys()):
                w = self.wm[tid]
                attr_s = " ".join(f"^{k} {v}" for k, v in w["attrs"].items())
                print(f"{tid}: ({w['class']}" + (f" {attr_s}" if attr_s else "") + ")")
            return None

        if head == "PM":
            self._flush_output()
            for r in self.rules:
                print(f"Rule {r['name']} ({len(r['lhs'])} CEs --> {len(r['rhs'])} actions)")
            return None

        if head == "RUN":
            max_cycles = int(form[1]) if len(form) > 1 else 1000
            self.did_run = True
            res = self.run(max_cycles=max_cycles)
            self._flush_output()
            return res

        return None

    def _parse_production(self, form):
        rule_name = str(form[1]).upper()
        arrow_idx = form.index("-->")
        lhs_raw = form[2:arrow_idx]
        rhs_raw = form[arrow_idx + 1:]

        lhs = []
        i = 0
        while i < len(lhs_raw):
            item = lhs_raw[i]
            if item == "-":
                neg_ce = self._parse_ce(lhs_raw[i + 1], negated=True)
                lhs.append(neg_ce)
                i += 2
            elif isinstance(item, list) and item and item[0] == "__BRACE__":
                # {<ce> <var>} or {<var> <ce>}
                if isinstance(item[1], list):
                    ce_list, ce_var = item[1], str(item[2]).upper()
                else:
                    ce_var, ce_list = str(item[1]).upper(), item[2]
                ce = self._parse_ce(ce_list, negated=False, elem_var=ce_var)
                lhs.append(ce)
                i += 1
            elif isinstance(item, list):
                lhs.append(self._parse_ce(item, negated=False))
                i += 1
            else:
                i += 1

        return {"name": rule_name, "lhs": lhs, "rhs": rhs_raw}

    def _parse_ce(self, ce_list, negated=False, elem_var=None):
        cls_name = str(ce_list[0]).upper()
        tests = []  # list of (attr_name, test_spec)
        i = 1
        while i < len(ce_list):
            if ce_list[i] == "^":
                attr_name = str(ce_list[i + 1]).upper()
                i += 2
                while i < len(ce_list) and ce_list[i] != "^":
                    test_spec, i = self._parse_attr_test(ce_list, i)
                    tests.append((attr_name, test_spec))
            else:
                i += 1
        return {"class": cls_name, "negated": negated, "elem_var": elem_var, "tests": tests}

    def _parse_attr_test(self, tokens, i):
        if i >= len(tokens):
            return ("EQ", None), i
        tok = tokens[i]
        if tok in ("=", "<>", "<", ">", "<=", ">="):
            rel = tok
            val = tokens[i + 1]
            return ("REL", rel, val), i + 2
        if tok == "<<":
            vals = []
            j = i + 1
            while j < len(tokens) and tokens[j] != ">>":
                vals.append(tokens[j])
                j += 1
            return ("DISJ", vals), j + 1
        if isinstance(tok, list) and tok and tok[0] == "__BRACE__":
            sub_tests = []
            sub_toks = tok[1:]
            k = 0
            while k < len(sub_toks):
                st, k = self._parse_attr_test(sub_toks, k)
                sub_tests.append(st)
            return ("CONJ", sub_tests), i + 1
        return ("EQ", tok), i + 1

    # ------------------------------------------------------------------
    # Rete / Pattern Matcher & Conflict Resolution (LEX / MEA)
    # ------------------------------------------------------------------
    def _match_test(self, actual_val, test_spec, bindings):
        ttype = test_spec[0]
        if ttype == "EQ":
            target = test_spec[1]
            if self.is_var(target):
                if target in bindings:
                    return actual_val == bindings[target], bindings
                new_b = dict(bindings)
                new_b[target] = actual_val
                return True, new_b
            return actual_val == target, bindings

        if ttype == "REL":
            rel, target = test_spec[1], test_spec[2]
            cmp_val = bindings.get(target, target) if self.is_var(target) else target
            if actual_val is None or cmp_val is None:
                return (rel == "<>"), bindings
            try:
                if rel == "=":
                    ok = actual_val == cmp_val
                elif rel == "<>":
                    ok = actual_val != cmp_val
                elif rel == "<":
                    ok = actual_val < cmp_val
                elif rel == ">":
                    ok = actual_val > cmp_val
                elif rel == "<=":
                    ok = actual_val <= cmp_val
                elif rel == ">=":
                    ok = actual_val >= cmp_val
                else:
                    ok = False
            except TypeError:
                ok = str(actual_val) != str(cmp_val) if rel == "<>" else False
            return ok, bindings

        if ttype == "DISJ":
            return actual_val in test_spec[1], bindings

        if ttype == "CONJ":
            cur_b = dict(bindings)
            for st in test_spec[1]:
                ok, cur_b = self._match_test(actual_val, st, cur_b)
                if not ok:
                    return False, bindings
            return True, cur_b

        return False, bindings

    def _match_wme_against_ce(self, wme, ce, bindings):
        if wme["class"] != ce["class"]:
            return False, bindings
        cur_b = dict(bindings)
        if ce.get("elem_var"):
            ev = ce["elem_var"]
            if ev in cur_b and cur_b[ev] != wme["id"]:
                return False, bindings
            cur_b[ev] = wme["id"]
        for attr_name, test_spec in ce["tests"]:
            actual_val = wme["attrs"].get(attr_name, "NIL")
            ok, cur_b = self._match_test(actual_val, test_spec, cur_b)
            if not ok:
                return False, bindings
        return True, cur_b

    def _find_instantiations_for_rule(self, rule):
        results = []
        wmes = list(self.wm.values())

        def backtrack(ce_idx, bindings, pos_wmes):
            if ce_idx >= len(rule["lhs"]):
                timetags = tuple(w["id"] for w in pos_wmes)
                if (rule["name"], timetags) not in self.refracted:
                    results.append((rule, pos_wmes, bindings, timetags))
                return

            ce = rule["lhs"][ce_idx]
            if ce["negated"]:
                for w in wmes:
                    ok, _ = self._match_wme_against_ce(w, ce, bindings)
                    if ok:
                        return  # Negated CE matched -> fail
                backtrack(ce_idx + 1, bindings, pos_wmes)
            else:
                for w in wmes:
                    ok, next_b = self._match_wme_against_ce(w, ce, bindings)
                    if ok:
                        backtrack(ce_idx + 1, next_b, pos_wmes + [w])

        backtrack(0, {}, [])
        return results

    def _select_instantiation(self, conflict_set):
        def sort_key(inst):
            rule, pos_wmes, _, timetags = inst
            specificity = sum(len(ce["tests"]) for ce in rule["lhs"]) + len(rule["lhs"])
            if self.strategy == "MEA" and timetags:
                return (timetags[0], sorted(timetags[1:], reverse=True), specificity)
            return (sorted(timetags, reverse=True), specificity)

        conflict_set.sort(key=sort_key, reverse=True)
        return conflict_set[0]

    # ------------------------------------------------------------------
    # RHS Action Execution
    # ------------------------------------------------------------------
    def _eval_rhs_value(self, item, bindings):
        if isinstance(item, (int, float)):
            return item
        if self.is_var(item):
            return bindings.get(item, "NIL")
        if isinstance(item, list) and item:
            op = str(item[0]).upper()
            if op == "COMPUTE":
                return self._eval_compute(item[1:], bindings)
            if op in ("+", "-", "*", "/", "//", "\\\\"):
                return self._eval_compute(item, bindings)
        return item

    def _eval_compute(self, expr_items, bindings):
        def resolve_atom(x):
            if isinstance(x, list):
                if x and str(x[0]).upper() == "COMPUTE":
                    return self._eval_compute(x[1:], bindings)
                return self._eval_compute(x, bindings)
            if self.is_var(x):
                return bindings.get(x, 0)
            return x

        resolved = [resolve_atom(x) for x in expr_items]
        if not resolved:
            return 0
        # Support prefix (+ a b) as well as OPS5 standard infix (a + b)
        if str(resolved[0]) in ("+", "-", "*", "/", "//", "\\\\") and len(resolved) >= 3:
            op = str(resolved[0])
            a, b = resolved[1], resolved[2]
            return self._apply_arith(op, a, b)

        # Standard OPS5 infix arithmetic
        vals = [resolved[0]]
        ops = []
        i = 1
        while i + 1 < len(resolved):
            ops.append(str(resolved[i]))
            vals.append(resolved[i + 1])
            i += 2
        # First pass: *, /, //, \\
        j = 0
        while j < len(ops):
            if ops[j] in ("*", "/", "//", "\\\\"):
                vals[j] = self._apply_arith(ops[j], vals[j], vals[j + 1])
                vals.pop(j + 1)
                ops.pop(j)
            else:
                j += 1
        acc = vals[0]
        for op, v in zip(ops, vals[1:]):
            acc = self._apply_arith(op, acc, v)
        return acc

    def _apply_arith(self, op, a, b):
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op in ("//", "/"):
            if isinstance(a, int) and isinstance(b, int):
                return a // b if b != 0 else 0
            return a / b if b != 0 else 0
        if op == "\\\\":
            return a % b if b != 0 else 0
        return 0

    def _make_wme(self, items, bindings):
        cls_name = str(items[0]).upper()
        attrs = {}
        for d_attr in self.classes.get(cls_name, []):
            attrs[d_attr] = "NIL"
        i = 1
        while i < len(items):
            if items[i] == "^":
                aname = str(items[i + 1]).upper()
                aval = self._eval_rhs_value(items[i + 2], bindings)
                attrs[aname] = aval
                i += 3
            else:
                i += 1
        tid = self.next_timetag
        self.next_timetag += 1
        wme = {"id": tid, "class": cls_name, "attrs": attrs, "stamp": tid}
        self.wm[tid] = wme
        if self.watch_level >= 2:
            attr_s = " ".join(f"^{k} {v}" for k, v in attrs.items())
            print(f"=>WM: {tid}: ({cls_name} {attr_s})")
        return wme

    def _resolve_ce_target(self, target, bindings, pos_wmes):
        if isinstance(target, int):
            idx = target - 1
            if 0 <= idx < len(pos_wmes):
                return pos_wmes[idx]["id"]
        if self.is_var(target) and target in bindings:
            return bindings[target]
        return int(target)

    def _exec_rhs_action(self, action, bindings, pos_wmes):
        if not isinstance(action, list) or not action:
            return
        act = str(action[0]).upper()

        if act == "MAKE":
            self._make_wme(action[1:], bindings)
            return

        if act == "MODIFY":
            old_id = self._resolve_ce_target(action[1], bindings, pos_wmes)
            old_wme = self.wm.pop(old_id, None)
            if old_wme is None:
                return
            new_attrs = dict(old_wme["attrs"])
            i = 2
            while i < len(action):
                if action[i] == "^":
                    aname = str(action[i + 1]).upper()
                    aval = self._eval_rhs_value(action[i + 2], bindings)
                    new_attrs[aname] = aval
                    i += 3
                else:
                    i += 1
            new_id = self.next_timetag
            self.next_timetag += 1
            new_wme = {"id": new_id, "class": old_wme["class"], "attrs": new_attrs, "stamp": new_id}
            self.wm[new_id] = new_wme
            for idx_w, pw in enumerate(pos_wmes):
                if pw["id"] == old_id:
                    pos_wmes[idx_w] = new_wme
            return

        if act == "REMOVE":
            for t_spec in action[1:]:
                tid = self._resolve_ce_target(t_spec, bindings, pos_wmes)
                self.wm.pop(tid, None)
            return

        if act == "BIND":
            var_name = str(action[1]).upper()
            if len(action) > 2:
                bindings[var_name] = self._eval_rhs_value(action[2], bindings)
            else:
                bindings[var_name] = f"G{self.next_timetag}"
                self.next_timetag += 1
            return

        if act == "WRITE":
            for item in action[1:]:
                if isinstance(item, list) and item:
                    sub_op = str(item[0]).upper()
                    if sub_op == "CRLF":
                        self._flush_output(force_newline=True)
                    elif sub_op == "TABTO":
                        col = int(self._eval_rhs_value(item[1], bindings))
                        cur_len = sum(len(str(x)) for x in self._out_buf)
                        if col > cur_len + 1:
                            self._out_buf.append(" " * (col - cur_len - 1))
                    else:
                        val = self._eval_rhs_value(item, bindings)
                        self._out_buf.append(str(val))
                else:
                    val = self._eval_rhs_value(item, bindings)
                    if self._out_buf and not str(self._out_buf[-1]).endswith(" "):
                        self._out_buf.append(" ")
                    self._out_buf.append(str(val))
            return

        if act == "HALT":
            self.halted = True
            return

    def _flush_output(self, force_newline=False):
        if self._out_buf or force_newline:
            line = "".join(str(x) for x in self._out_buf).lstrip(" ")
            print(line)
            self._out_buf.clear()

    def run(self, max_cycles=1000):
        self.halted = False
        cycles_executed = 0
        while cycles_executed < max_cycles and not self.halted:
            conflict_set = []
            for rule in self.rules:
                conflict_set.extend(self._find_instantiations_for_rule(rule))
            if not conflict_set:
                break
            rule, pos_wmes, bindings, timetags = self._select_instantiation(conflict_set)
            self.refracted.add((rule["name"], timetags))
            self.cycle_count += 1
            cycles_executed += 1
            if self.watch_level >= 1:
                tt_s = " ".join(str(t) for t in timetags)
                print(f"{self.cycle_count}. {rule['name']}   {tt_s}")
            local_bindings = dict(bindings)
            local_pos_wmes = list(pos_wmes)
            for action in rule["rhs"]:
                self._exec_rhs_action(action, local_bindings, local_pos_wmes)
                if self.halted:
                    break
        self._flush_output()
        return cycles_executed

    def run_interactive(self):
        print(f"DEC VAX OPS5 {self.VERSION} — Production System Environment")
        buf = ""
        while True:
            prompt = "OPS5> " if not buf.strip() else "  --> "
            sys.stdout.write(prompt)
            sys.stdout.flush()
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                print("\n; Interrupt")
                buf = ""
                continue
            if not line:
                break
            if line.strip() in ("\x1a", "\x04"):
                break
            buf += line
            clean = re.sub(r";[^\n]*", "", re.sub(r"\|[^|]*\|", "||", buf))
            if clean.count("(") > clean.count(")"):
                continue
            if not buf.strip():
                buf = ""
                continue
            try:
                forms = self.parse_forms(buf)
                buf = ""
                for form in forms:
                    self.eval_form(form)
            except OPS5Quit:
                return 0
            except Exception as e:
                buf = ""
                print(f"%OPS5-E-ERR, {e}")
        return 0


class VAXOPS5Compiler:
    VERSION = "V2.2-00"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.ident = "V02-02"
        self.bytecode = bytearray()
        self.var_map = {}
        self.var_types = {}
        self.symbols = {"MAIN_START": 0}
        self.listing_lines = []

    def get_var_id(self, name, vtype="WME"):
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

    def emit_store_var(self, name, vtype="WME"):
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(self.get_var_id(name, vtype))

    def compile_source(self, source_text):
        for lno, raw in enumerate(source_text.splitlines(), start=1):
            self.listing_lines.append((lno, len(self.bytecode), raw))

        engine = OPS5Engine()
        forms = engine.parse_forms(source_text)

        buf = io.StringIO()
        with redirect_stdout(buf):
            for form in forms:
                if isinstance(form, list) and form and str(form[0]).upper() == "P":
                    rname = str(form[1]).upper()
                    self.symbols[f"RULE_{rname[:10]}"] = len(self.bytecode)
                try:
                    engine.eval_form(form)
                except OPS5Quit:
                    break
            if not engine.did_run and engine.rules and engine.wm:
                engine.run()

        self.emit_push_int(engine.cycle_count)
        self.emit_store_var("OPS5$CYCLES", "LONG")
        self.emit_push_int(len(engine.wm))
        self.emit_store_var("OPS5$WM_COUNT", "LONG")

        for out_ln in buf.getvalue().splitlines():
            self.emit_push_str(out_ln)
            self.emit_u8(OP_PRINT)

        self.emit_u8(OP_HALT)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX OPS5 {self.VERSION}",
            "symbols": self.symbols,
            "relocations": [],
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC VAX OPS5 {self.VERSION} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                f.write("Line  Offset  VAX OPS5 Production Source\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nRete Network Productions & Working Memory Symbols:\n")
                for sname, soff in sorted(self.symbols.items()):
                    f.write(f"  {sname:<26} @ {soff:06X}\n")
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
        eng = OPS5Engine()
        sys.exit(eng.run_interactive())

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
        eng = OPS5Engine()
        sys.exit(eng.run_interactive())

    if not os.path.isfile(in_file):
        for ext in (".OPS", ".ops", ".OPS5", ".ops5"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%OPS5-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXOPS5Compiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX OPS5 {VAXOPS5Compiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
