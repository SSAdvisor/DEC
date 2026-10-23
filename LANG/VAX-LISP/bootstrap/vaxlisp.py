#!/usr/bin/env python3
"""
DEC VAX LISP V3.1-00 Common Lisp Compiler & Interactive REPL (vaxlisp.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Supports:
  - Full S-expression reader (quotes ', comments ;, #| ... |#, #', strings, numbers, symbols)
  - Common Lisp special forms & macros:
    defun, defvar, defparameter, defconstant, setq, setf, let, let*, if, cond, when,
    unless, progn, dotimes, dolist, do, loop, lambda, function, quote, and, or
  - Common Lisp standard functions:
    format (t / nil, ~A, ~S, ~D, ~%), print, princ, prin1, terpri, write-line,
    car, first, cdr, rest, cadr, caddr, cons, list, length, append, reverse, nth,
    member, assoc, mapcar, apply, funcall, +, -, *, /, mod, rem, 1+, 1-, abs, max, min,
    =, /=, <, >, <=, >=, eq, eql, equal, not, null, atom, listp, consp, numberp, symbolp,
    stringp, string-upcase, string-downcase, concatenate, (exit) / (quit)
  - Emits OpenVMS .OBJ relocatable object modules and .LST listings for vmslink & vms_vm
  - Interactive VAX LISP V3.1 REPL (`VAX LISP V3.1 — Common Lisp for VAX/VMS`, `LISP>` prompt)
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
OP_LOAD_VAR = 0x14
OP_PUSH_I32 = 0x18
OP_PRINT = 0x50


class LispSymbol(str):
    def __new__(cls, name):
        return super().__new__(cls, name.upper())

    def __repr__(self):
        return str(self)


NIL = LispSymbol("NIL")
T = LispSymbol("T")


class LispQuit(Exception):
    pass


class LispReturn(Exception):
    def __init__(self, val=NIL):
        self.val = val


class LispFunction:
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env

    def __repr__(self):
        return f"#<FUNCTION {self.name}>"


class VAXLispEnv:
    VERSION = "V3.1-00"

    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}
        self.fns = {}
        if parent is None:
            self.vars["NIL"] = []
            self.vars["T"] = T

    def find_var_env(self, sym):
        key = str(sym).upper()
        if key in self.vars:
            return self
        if self.parent is not None:
            return self.parent.find_var_env(key)
        return None

    def get_var(self, sym):
        key = str(sym).upper()
        if key == "NIL":
            return []
        if key == "T":
            return T
        if key.startswith(":"):
            return LispSymbol(key)
        env = self.find_var_env(key)
        if env is not None:
            return env.vars[key]
        raise NameError(f"%LISP-E-UNBOUND, unbound variable {key}")

    def set_var(self, sym, val):
        key = str(sym).upper()
        env = self.find_var_env(key)
        if env is not None:
            env.vars[key] = val
        else:
            self.root().vars[key] = val
        return val

    def def_local(self, sym, val):
        self.vars[str(sym).upper()] = val

    def get_fn(self, sym):
        key = str(sym).upper()
        if key in self.fns:
            return self.fns[key]
        if self.parent is not None:
            return self.parent.get_fn(key)
        return None

    def set_fn(self, sym, fn):
        self.root().fns[str(sym).upper()] = fn

    def root(self):
        cur = self
        while cur.parent is not None:
            cur = cur.parent
        return cur


class VAXLispInterpreter:
    VERSION = "V3.1-00"

    def __init__(self):
        self.global_env = VAXLispEnv()

    # ------------------------------------------------------------------
    # S-Expression Reader
    # ------------------------------------------------------------------
    def tokenize(self, text):
        # Remove #| ... |# block comments
        text = re.sub(r"#\|.*?\|#", " ", text, flags=re.DOTALL)
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
            if text[i:i + 2] == "#'":
                tokens.append("#'")
                i += 2
                continue
            if ch in ("(", ")", "'", "`", ","):
                tokens.append(ch)
                i += 1
                continue
            if ch == '"':
                i += 1
                buf = []
                while i < n and text[i] != '"':
                    if text[i] == "\\" and i + 1 < n:
                        i += 1
                        buf.append(text[i])
                    else:
                        buf.append(text[i])
                    i += 1
                i += 1  # closing quote
                tokens.append(('STR', "".join(buf)))
                continue
            j = i
            while j < n and (not text[j].isspace()) and text[j] not in ("(", ")", "'", '"', ";"):
                j += 1
            tokens.append(text[i:j])
            i = j
        return tokens

    def parse_all(self, text):
        tokens = self.tokenize(text)
        pos = 0
        exprs = []

        def read_expr():
            nonlocal pos
            if pos >= len(tokens):
                return None
            tok = tokens[pos]
            pos += 1
            if tok == "(":
                lst = []
                while pos < len(tokens) and tokens[pos] != ")":
                    if tokens[pos] == ".":
                        pos += 1
                        cdr_val = read_expr()
                        if pos < len(tokens) and tokens[pos] == ")":
                            pos += 1
                        return (lst, cdr_val)
                    lst.append(read_expr())
                if pos < len(tokens) and tokens[pos] == ")":
                    pos += 1
                return lst
            if tok == ")":
                return []
            if tok == "'":
                return [LispSymbol("QUOTE"), read_expr()]
            if tok == "#'":
                return [LispSymbol("FUNCTION"), read_expr()]
            if isinstance(tok, tuple) and tok[0] == "STR":
                return tok[1]
            if re.match(r"^[+-]?\d+$", str(tok)):
                return int(tok)
            if re.match(r"^[+-]?\d*\.\d+(?:[eE][+-]?\d+)?$", str(tok)):
                return float(tok)
            up = str(tok).upper()
            if up == "NIL":
                return []
            if up == "T":
                return T
            return LispSymbol(up)

        while pos < len(tokens):
            e = read_expr()
            if e is not None:
                exprs.append(e)
        return exprs

    def is_true(self, val):
        if val is None:
            return False
        if isinstance(val, list) and len(val) == 0:
            return False
        if isinstance(val, LispSymbol) and str(val) == "NIL":
            return False
        if val is False:
            return False
        return True

    def format_lisp(self, val, readable=True):
        if val is None or (isinstance(val, list) and len(val) == 0):
            return "NIL"
        if isinstance(val, LispSymbol):
            return str(val)
        if isinstance(val, str):
            return f'"{val}"' if readable else val
        if isinstance(val, float):
            return f"{val:g}"
        if isinstance(val, int):
            return str(val)
        if isinstance(val, list):
            return "(" + " ".join(self.format_lisp(x, readable=readable) for x in val) + ")"
        if isinstance(val, tuple) and len(val) == 2:
            head_s = " ".join(self.format_lisp(x, readable=readable) for x in val[0])
            tail_s = self.format_lisp(val[1], readable=readable)
            return f"({head_s} . {tail_s})"
        return str(val)

    def _cl_format(self, fmt_str, args):
        out = []
        i = 0
        arg_idx = 0
        n = len(fmt_str)
        while i < n:
            if fmt_str[i] == "~" and i + 1 < n:
                d = fmt_str[i + 1].upper()
                if d == "%":
                    out.append("\n")
                    i += 2
                    continue
                if d == "~":
                    out.append("~")
                    i += 2
                    continue
                if d in ("A", "S", "D", "F", "G"):
                    val = args[arg_idx] if arg_idx < len(args) else []
                    arg_idx += 1
                    if d == "A":
                        out.append(self.format_lisp(val, readable=False))
                    elif d == "S":
                        out.append(self.format_lisp(val, readable=True))
                    else:
                        out.append(self.format_lisp(val, readable=False))
                    i += 2
                    continue
            out.append(fmt_str[i])
            i += 1
        return "".join(out)

    # ------------------------------------------------------------------
    # Evaluator
    # ------------------------------------------------------------------
    def eval_expr(self, expr, env=None):
        if env is None:
            env = self.global_env

        if isinstance(expr, (int, float, str)) and not isinstance(expr, LispSymbol):
            return expr
        if isinstance(expr, LispSymbol):
            return env.get_var(expr)
        if not isinstance(expr, list):
            return expr
        if len(expr) == 0:
            return []

        op = expr[0]
        args = expr[1:]

        if isinstance(op, list) and len(op) > 0 and str(op[0]).upper() == "LAMBDA":
            fn_obj = self.eval_expr(op, env)
            evaled_args = [self.eval_expr(a, env) for a in args]
            return self.call_fn(fn_obj, evaled_args, env)

        op_name = str(op).upper()

        if op_name in ("EXIT", "QUIT", "BYE"):
            raise LispQuit()

        if op_name == "QUOTE":
            return args[0] if args else []

        if op_name == "FUNCTION":
            target = args[0]
            if isinstance(target, list) and len(target) > 0 and str(target[0]).upper() == "LAMBDA":
                return LispFunction("LAMBDA", target[1], target[2:], env)
            fn = env.get_fn(target)
            if fn is not None:
                return fn
            return LispSymbol(str(target).upper())

        if op_name == "LAMBDA":
            params = args[0] if args else []
            body = args[1:]
            return LispFunction("LAMBDA", params, body, env)

        if op_name == "DEFUN":
            fn_name = str(args[0]).upper()
            params = args[1]
            body = args[2:]
            fn_obj = LispFunction(fn_name, params, body, env)
            env.set_fn(fn_name, fn_obj)
            return LispSymbol(fn_name)

        if op_name in ("DEFVAR", "DEFPARAMETER", "DEFCONSTANT"):
            var_name = str(args[0]).upper()
            val = self.eval_expr(args[1], env) if len(args) > 1 else []
            env.root().def_local(var_name, val)
            return LispSymbol(var_name)

        if op_name in ("SETQ", "SETF"):
            last_val = []
            for idx in range(0, len(args), 2):
                place = args[idx]
                val = self.eval_expr(args[idx + 1], env)
                if isinstance(place, LispSymbol):
                    env.set_var(place, val)
                elif isinstance(place, list) and len(place) >= 2:
                    acc_op = str(place[0]).upper()
                    target_list = self.eval_expr(place[1], env)
                    if acc_op in ("CAR", "FIRST") and isinstance(target_list, list) and target_list:
                        target_list[0] = val
                    elif acc_op == "NTH" and len(place) >= 3:
                        n_i = int(self.eval_expr(place[1], env))
                        t_l = self.eval_expr(place[2], env)
                        if isinstance(t_l, list) and 0 <= n_i < len(t_l):
                            t_l[n_i] = val
                last_val = val
            return last_val

        if op_name in ("LET", "LET*"):
            bindings = args[0]
            body = args[1:]
            new_env = VAXLispEnv(parent=env)
            if op_name == "LET":
                evaluated_pairs = []
                for b in bindings:
                    if isinstance(b, list):
                        vname = b[0]
                        vval = self.eval_expr(b[1], env) if len(b) > 1 else []
                    else:
                        vname, vval = b, []
                    evaluated_pairs.append((vname, vval))
                for vname, vval in evaluated_pairs:
                    new_env.def_local(vname, vval)
            else:
                for b in bindings:
                    if isinstance(b, list):
                        vname = b[0]
                        vval = self.eval_expr(b[1], new_env) if len(b) > 1 else []
                    else:
                        vname, vval = b, []
                    new_env.def_local(vname, vval)
            res = []
            for form in body:
                res = self.eval_expr(form, new_env)
            return res

        if op_name == "IF":
            cond_val = self.eval_expr(args[0], env)
            if self.is_true(cond_val):
                return self.eval_expr(args[1], env)
            if len(args) > 2:
                return self.eval_expr(args[2], env)
            return []

        if op_name == "COND":
            for clause in args:
                if not isinstance(clause, list) or not clause:
                    continue
                test_val = self.eval_expr(clause[0], env)
                if self.is_true(test_val):
                    if len(clause) == 1:
                        return test_val
                    res = []
                    for form in clause[1:]:
                        res = self.eval_expr(form, env)
                    return res
            return []

        if op_name == "WHEN":
            if self.is_true(self.eval_expr(args[0], env)):
                res = []
                for form in args[1:]:
                    res = self.eval_expr(form, env)
                return res
            return []

        if op_name == "UNLESS":
            if not self.is_true(self.eval_expr(args[0], env)):
                res = []
                for form in args[1:]:
                    res = self.eval_expr(form, env)
                return res
            return []

        if op_name == "PROGN":
            res = []
            for form in args:
                res = self.eval_expr(form, env)
            return res

        if op_name == "RETURN":
            val = self.eval_expr(args[0], env) if args else []
            raise LispReturn(val)

        if op_name == "DOTIMES":
            spec = args[0]
            var_sym = spec[0]
            count_val = int(self.eval_expr(spec[1], env))
            res_form = spec[2] if len(spec) > 2 else []
            loop_env = VAXLispEnv(parent=env)
            try:
                for i in range(count_val):
                    loop_env.def_local(var_sym, i)
                    for form in args[1:]:
                        self.eval_expr(form, loop_env)
            except LispReturn as lr:
                return lr.val
            loop_env.def_local(var_sym, count_val)
            return self.eval_expr(res_form, loop_env) if res_form != [] else []

        if op_name == "DOLIST":
            spec = args[0]
            var_sym = spec[0]
            items = self.eval_expr(spec[1], env)
            res_form = spec[2] if len(spec) > 2 else []
            loop_env = VAXLispEnv(parent=env)
            try:
                for it in (items if isinstance(items, list) else []):
                    loop_env.def_local(var_sym, it)
                    for form in args[1:]:
                        self.eval_expr(form, loop_env)
            except LispReturn as lr:
                return lr.val
            loop_env.def_local(var_sym, [])
            return self.eval_expr(res_form, loop_env) if res_form != [] else []

        if op_name in ("DO", "DO*"):
            var_specs = args[0]
            end_spec = args[1]
            body = args[2:]
            loop_env = VAXLispEnv(parent=env)
            steps = []
            for vs in var_specs:
                vname = vs[0]
                init_val = self.eval_expr(vs[1], loop_env if op_name == "DO*" else env) if len(vs) > 1 else []
                loop_env.def_local(vname, init_val)
                if len(vs) > 2:
                    steps.append((vname, vs[2]))
            try:
                while not self.is_true(self.eval_expr(end_spec[0], loop_env)):
                    for form in body:
                        self.eval_expr(form, loop_env)
                    if op_name == "DO":
                        next_vals = [(vn, self.eval_expr(st, loop_env)) for vn, st in steps]
                        for vn, nv in next_vals:
                            loop_env.def_local(vn, nv)
                    else:
                        for vn, st in steps:
                            loop_env.def_local(vn, self.eval_expr(st, loop_env))
            except LispReturn as lr:
                return lr.val
            res = []
            for form in end_spec[1:]:
                res = self.eval_expr(form, loop_env)
            return res

        if op_name == "LOOP":
            # Support both simple (loop (when ... (return ...)) ...) and extended (loop for i from a to b do/collect/sum ...)
            if args and isinstance(args[0], LispSymbol) and str(args[0]).upper() == "FOR":
                return self._eval_extended_loop(args, env)
            try:
                while True:
                    for form in args:
                        self.eval_expr(form, env)
            except LispReturn as lr:
                return lr.val

        if op_name == "AND":
            val = T
            for form in args:
                val = self.eval_expr(form, env)
                if not self.is_true(val):
                    return []
            return val

        if op_name == "OR":
            for form in args:
                val = self.eval_expr(form, env)
                if self.is_true(val):
                    return val
            return []

        # Evaluate arguments for standard function call
        evaled_args = [self.eval_expr(a, env) for a in args]
        return self.call_fn(op_name, evaled_args, env)

    def _eval_extended_loop(self, tokens, env):
        loop_env = VAXLispEnv(parent=env)
        var_sym = tokens[1]
        mode = str(tokens[2]).upper()
        if mode == "IN":
            seq = self.eval_expr(tokens[3], env)
            rest = tokens[4:]
            items = seq if isinstance(seq, list) else []
        else:
            lo = int(self.eval_expr(tokens[3], env))
            hi = int(self.eval_expr(tokens[5], env))
            rest = tokens[6:]
            items = list(range(lo, hi + 1))

        action = str(rest[0]).upper() if rest else "DO"
        body = rest[1:]
        collected = []
        total = 0
        try:
            for item in items:
                loop_env.def_local(var_sym, item)
                if action in ("COLLECT", "COLLECTING"):
                    collected.append(self.eval_expr(body[0], loop_env))
                elif action in ("SUM", "SUMMING"):
                    total += self.eval_expr(body[0], loop_env)
                else:
                    for form in body:
                        self.eval_expr(form, loop_env)
        except LispReturn as lr:
            return lr.val
        if action in ("COLLECT", "COLLECTING"):
            return collected
        if action in ("SUM", "SUMMING"):
            return total
        return []

    def call_fn(self, fn_or_name, evaled_args, env):
        if isinstance(fn_or_name, LispFunction):
            return self._invoke_user_fn(fn_or_name, evaled_args)

        name = str(fn_or_name).upper()
        user_fn = env.get_fn(name)
        if user_fn is not None:
            return self._invoke_user_fn(user_fn, evaled_args)

        # Built-in Common Lisp functions
        if name == "+":
            return sum(evaled_args)
        if name == "-":
            if not evaled_args:
                return 0
            if len(evaled_args) == 1:
                return -evaled_args[0]
            res = evaled_args[0]
            for x in evaled_args[1:]:
                res -= x
            return res
        if name == "*":
            prod = 1
            for x in evaled_args:
                prod *= x
            return prod
        if name == "/":
            if len(evaled_args) == 1:
                return 1 / evaled_args[0]
            res = evaled_args[0]
            for x in evaled_args[1:]:
                if isinstance(res, int) and isinstance(x, int) and res % x == 0:
                    res //= x
                else:
                    res /= x
            return res
        if name in ("MOD", "REM"):
            return evaled_args[0] % evaled_args[1]
        if name == "1+":
            return evaled_args[0] + 1
        if name == "1-":
            return evaled_args[0] - 1
        if name == "ABS":
            return abs(evaled_args[0])
        if name == "MAX":
            return max(evaled_args)
        if name == "MIN":
            return min(evaled_args)

        if name == "=":
            return T if evaled_args[0] == evaled_args[1] else []
        if name == "/=":
            return T if evaled_args[0] != evaled_args[1] else []
        if name == "<":
            return T if evaled_args[0] < evaled_args[1] else []
        if name == ">":
            return T if evaled_args[0] > evaled_args[1] else []
        if name == "<=":
            return T if evaled_args[0] <= evaled_args[1] else []
        if name == ">=":
            return T if evaled_args[0] >= evaled_args[1] else []
        if name in ("EQ", "EQL", "EQUAL"):
            return T if evaled_args[0] == evaled_args[1] else []

        if name in ("NOT", "NULL"):
            return T if not self.is_true(evaled_args[0]) else []
        if name == "ATOM":
            return T if not (isinstance(evaled_args[0], list) and len(evaled_args[0]) > 0) else []
        if name == "LISTP":
            return T if isinstance(evaled_args[0], list) else []
        if name == "CONSP":
            return T if isinstance(evaled_args[0], list) and len(evaled_args[0]) > 0 else []
        if name == "NUMBERP":
            return T if isinstance(evaled_args[0], (int, float)) else []
        if name == "SYMBOLP":
            v = evaled_args[0]
            return T if isinstance(v, LispSymbol) or (isinstance(v, list) and len(v) == 0) else []
        if name == "STRINGP":
            v = evaled_args[0]
            return T if isinstance(v, str) and not isinstance(v, LispSymbol) else []

        if name in ("CAR", "FIRST"):
            lst = evaled_args[0]
            return lst[0] if isinstance(lst, list) and lst else []
        if name in ("CDR", "REST"):
            lst = evaled_args[0]
            return lst[1:] if isinstance(lst, list) and lst else []
        if name in ("CADR", "SECOND"):
            lst = evaled_args[0]
            return lst[1] if isinstance(lst, list) and len(lst) > 1 else []
        if name in ("CADDR", "THIRD"):
            lst = evaled_args[0]
            return lst[2] if isinstance(lst, list) and len(lst) > 2 else []
        if name == "CONS":
            a, b = evaled_args[0], evaled_args[1]
            if isinstance(b, list):
                return [a] + b
            return [a, b]
        if name == "LIST":
            return list(evaled_args)
        if name == "LENGTH":
            return len(evaled_args[0]) if isinstance(evaled_args[0], (list, str)) else 0
        if name == "APPEND":
            out = []
            for lst in evaled_args:
                if isinstance(lst, list):
                    out.extend(lst)
            return out
        if name == "REVERSE":
            v = evaled_args[0]
            return list(reversed(v)) if isinstance(v, list) else v
        if name == "NTH":
            idx, lst = int(evaled_args[0]), evaled_args[1]
            return lst[idx] if isinstance(lst, list) and 0 <= idx < len(lst) else []
        if name == "MEMBER":
            item, lst = evaled_args[0], evaled_args[1]
            if isinstance(lst, list):
                for idx, x in enumerate(lst):
                    if x == item:
                        return lst[idx:]
            return []
        if name == "ASSOC":
            key, alist = evaled_args[0], evaled_args[1]
            if isinstance(alist, list):
                for pair in alist:
                    if isinstance(pair, list) and pair and pair[0] == key:
                        return pair
            return []

        if name == "MAPCAR":
            fn = evaled_args[0]
            lists = evaled_args[1:]
            return [self.call_fn(fn, list(items), env) for items in zip(*lists)]
        if name == "APPLY":
            fn = evaled_args[0]
            last = evaled_args[-1] if isinstance(evaled_args[-1], list) else [evaled_args[-1]]
            all_args = list(evaled_args[1:-1]) + list(last)
            return self.call_fn(fn, all_args, env)
        if name == "FUNCALL":
            fn = evaled_args[0]
            return self.call_fn(fn, evaled_args[1:], env)

        if name == "FORMAT":
            dest = evaled_args[0]
            fmt_str = str(evaled_args[1])
            rendered = self._cl_format(fmt_str, evaled_args[2:])
            if self.is_true(dest):
                sys.stdout.write(rendered)
                sys.stdout.flush()
                return []
            return rendered
        if name == "PRINT":
            val = evaled_args[0]
            print(self.format_lisp(val, readable=True))
            return val
        if name == "PRIN1":
            val = evaled_args[0]
            sys.stdout.write(self.format_lisp(val, readable=True))
            sys.stdout.flush()
            return val
        if name == "PRINC":
            val = evaled_args[0]
            sys.stdout.write(self.format_lisp(val, readable=False))
            sys.stdout.flush()
            return val
        if name == "WRITE-LINE":
            val = str(evaled_args[0])
            print(val)
            return val
        if name == "TERPRI":
            print()
            return []

        raise NameError(f"%LISP-E-UNDEFN, undefined function {name}")

    def _invoke_user_fn(self, fn_obj, evaled_args):
        local_env = VAXLispEnv(parent=fn_obj.env)
        p_idx = 0
        a_idx = 0
        params = fn_obj.params
        while p_idx < len(params):
            p = params[p_idx]
            p_str = str(p).upper()
            if p_str == "&REST":
                rest_sym = params[p_idx + 1]
                local_env.def_local(rest_sym, list(evaled_args[a_idx:]))
                break
            if p_str == "&OPTIONAL":
                p_idx += 1
                continue
            if isinstance(p, list):
                pname = p[0]
                val = evaled_args[a_idx] if a_idx < len(evaled_args) else self.eval_expr(p[1], local_env)
                local_env.def_local(pname, val)
            else:
                val = evaled_args[a_idx] if a_idx < len(evaled_args) else []
                local_env.def_local(p, val)
            p_idx += 1
            a_idx += 1

        res = []
        try:
            for form in fn_obj.body:
                res = self.eval_expr(form, local_env)
        except LispReturn as lr:
            return lr.val
        return res

    def run_interactive(self):
        print("VAX LISP V3.1 — Common Lisp for VAX/VMS")
        buf = ""
        while True:
            prompt = "LISP> " if not buf.strip() else "  --> "
            sys.stdout.write(prompt)
            sys.stdout.flush()
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                print("\n; Keyboard interrupt")
                buf = ""
                continue
            if not line:
                break
            if line.strip() in ("\x1a", "\x04"):
                break
            buf += line
            clean = re.sub(r';[^\n]*', '', re.sub(r'"(?:\\.|[^"\\])*"', '""', buf))
            if clean.count("(") > clean.count(")"):
                continue
            if not buf.strip():
                buf = ""
                continue
            try:
                exprs = self.parse_all(buf)
                buf = ""
                for expr in exprs:
                    val = self.eval_expr(expr)
                    print(self.format_lisp(val, readable=True))
            except LispQuit:
                return 0
            except Exception as e:
                buf = ""
                print(f"{e}")
        return 0


class VAXLispCompiler:
    VERSION = "V3.1-00"

    def __init__(self, module_name="MAIN"):
        self.module_name = module_name.upper()[:16]
        self.ident = "V03-01"
        self.bytecode = bytearray()
        self.var_map = {}
        self.var_types = {}
        self.symbols = {"MAIN_START": 0}
        self.listing_lines = []

    def get_var_id(self, name, vtype="SEXP"):
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

    def emit_store_var(self, name, vtype="SEXP"):
        self.emit_u8(OP_STORE_VAR)
        self.emit_u16(self.get_var_id(name, vtype))

    def compile_source(self, source_text):
        raw_lines = source_text.splitlines()
        for lno, raw in enumerate(raw_lines, start=1):
            self.listing_lines.append((lno, len(self.bytecode), raw))

        interp = VAXLispInterpreter()
        exprs = interp.parse_all(source_text)

        for expr in exprs:
            if isinstance(expr, list) and expr and str(expr[0]).upper() == "DEFUN":
                fn_name = str(expr[1]).upper()
                self.symbols[fn_name] = len(self.bytecode)

            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    interp.eval_expr(expr)
            except LispQuit:
                out_txt = buf.getvalue()
                for out_ln in out_txt.splitlines():
                    self.emit_push_str(out_ln)
                    self.emit_u8(OP_PRINT)
                break

            # Mirror global Lisp bindings into VM variable slots
            for k, v in interp.global_env.vars.items():
                if k in ("NIL", "T"):
                    continue
                if isinstance(v, int):
                    self.emit_push_int(v)
                    self.emit_store_var(k, "FIXNUM")
                else:
                    self.emit_push_str(interp.format_lisp(v, readable=True))
                    self.emit_store_var(k, "SEXP")

            out_txt = buf.getvalue()
            for out_ln in out_txt.splitlines():
                self.emit_push_str(out_ln)
                self.emit_u8(OP_PRINT)

        self.emit_u8(OP_HALT)

    def write_outputs(self, out_obj, out_lst=None):
        obj_data = {
            "module": self.module_name,
            "ident": self.ident,
            "creator": f"DEC VAX LISP {self.VERSION}",
            "symbols": self.symbols,
            "relocations": [],
            "bytecode": list(self.bytecode),
        }
        with open(out_obj, "w") as f:
            json.dump(obj_data, f, indent=2)

        if out_lst:
            now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
            with open(out_lst, "w") as f:
                f.write(f"DEC VAX LISP {self.VERSION} (VAX/VMS V5.5-2)  Module: {self.module_name}  Ident: {self.ident}  {now_str}\n")
                f.write("Line  Offset  VAX LISP Source Form\n")
                f.write("----  ------  ----------------------------------------------------------------\n")
                for lno, off, raw in self.listing_lines:
                    f.write(f"{lno:>4}  {off:06X}  {raw}\n")
                f.write("\nPackage USER Symbol & Function Table:\n")
                for sym_n, sym_off in sorted(self.symbols.items()):
                    f.write(f"  Function {sym_n:<22} @ {sym_off:06X}\n")
                for vname, vid in sorted(self.var_map.items(), key=lambda x: x[1]):
                    vtype = self.var_types.get(vname, "SEXP")
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
        interp = VAXLispInterpreter()
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
        interp = VAXLispInterpreter()
        sys.exit(interp.run_interactive())

    if not os.path.isfile(in_file):
        for ext in (".LSP", ".lsp", ".LISP", ".lisp", ".CL", ".cl"):
            if os.path.isfile(in_file + ext):
                in_file = in_file + ext
                break

    if not os.path.isfile(in_file):
        print(f"%LISP-E-OPENIN, error opening {in_file} as input")
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

    comp = VAXLispCompiler(module_name=mod_name)
    comp.compile_source(src_text)
    comp.write_outputs(out_obj, out_lst=out_lst)
    print(f"VAX LISP {VAXLispCompiler.VERSION}: Compiled {os.path.basename(in_file)} -> {os.path.basename(out_obj)} (0 errors)")


if __name__ == "__main__":
    main()
