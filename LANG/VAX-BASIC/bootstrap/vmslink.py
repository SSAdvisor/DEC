#!/usr/bin/env python3
"""
DEC OpenVMS VAX Linker V05-05 (vmslink.py)
Digital Equipment Corporation VAX/VMS V5.5-2

Links one or more OpenVMS / VAX BASIC .OBJ object modules, .OLB object libraries,
and .OPT linker options files into a standalone native OpenVMS .EXE executable
image powered by vms_vm, and optionally generates an OpenVMS .MAP image map.
"""

import os
import sys
import json
import stat
import shutil
import struct
from datetime import datetime


class OpenVMSLinker:
    VERSION = "V05-05"
    VAX_P0_BASE = 0x00000200

    def __init__(self):
        self.obj_modules = []     # list of dicts: {module, ident, creator, file, bytecode, relocations, symbols}
        self.olb_modules = {}     # mod_name -> module dict
        self.opt_ident = "V01-00"
        self.opt_gsmatch = "LEQUAL,1,0"
        self.opt_clusters = []
        self.opt_psect_attrs = {}
        self.opt_universals = []
        self.opt_shareables = []
        self.odl_root = None

    def load_input(self, path, base_dir="."):
        up = path.upper()
        if up.endswith(("/LIBRARY", "/LIB")):
            clean = path.rsplit("/", 1)[0]
            self.load_olb(self._resolve(clean, base_dir))
            return
        if up.endswith(("/SHARE", "/SHAREABLE")):
            clean = path.rsplit("/", 1)[0]
            self.opt_shareables.append(clean)
            return
        if up.endswith(("/OPTIONS", "/OPT")):
            clean = path.rsplit("/", 1)[0]
            self.load_opt(self._resolve(clean, base_dir))
            return

        resolved = self._resolve(path, base_dir)
        ext = os.path.splitext(resolved)[1].upper()
        if ext == ".OPT":
            self.load_opt(resolved)
        elif ext == ".ODL":
            self.load_odl(resolved)
        elif ext == ".OLB":
            self.load_olb(resolved)
        else:
            self.load_obj(resolved)

    def _resolve(self, path, base_dir="."):
        if os.path.isfile(path):
            return os.path.abspath(path)
        cand = os.path.join(base_dir, path)
        if os.path.isfile(cand):
            return os.path.abspath(cand)
        for ext in (".OBJ", ".obj", ".OPT", ".opt", ".OLB", ".olb"):
            if os.path.isfile(path + ext):
                return os.path.abspath(path + ext)
            if os.path.isfile(cand + ext):
                return os.path.abspath(cand + ext)
        return os.path.abspath(path)

    def load_obj(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"%LINK-E-OPENIN, error opening {path} as input")
        with open(path, "r", errors="replace") as f:
            data = json.load(f)
        mod_dict = {
            "module": str(data.get("module", "MAIN")).upper()[:16],
            "ident": str(data.get("ident", "V01.00")),
            "creator": str(data.get("creator", "VAX BASIC V3.5")),
            "file": os.path.abspath(path),
            "bytecode": list(data.get("bytecode", [])),
            "relocations": list(data.get("relocations", [])),
            "symbols": dict(data.get("symbols", {})),
        }
        self.obj_modules.append(mod_dict)

    def load_olb(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"%LINK-E-OPENIN, error opening library {path} as input")
        with open(path, "r", errors="replace") as f:
            data = json.load(f)
        modules = data.get("modules", {})
        if isinstance(modules, dict):
            for mname, mdata in modules.items():
                self.olb_modules[mname.upper()] = {
                    "module": mname.upper()[:16],
                    "ident": str(mdata.get("ident", "V01.00")),
                    "creator": str(mdata.get("creator", "VAX/VMS LIBRARIAN")),
                    "file": f"{os.path.abspath(path)}({mname.upper()})",
                    "bytecode": list(mdata.get("bytecode", [])),
                    "relocations": list(mdata.get("relocations", [])),
                    "symbols": dict(mdata.get("symbols", {})),
                }

    def load_opt(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"%LINK-E-OPENIN, error opening options file {path} as input")
        opt_dir = os.path.dirname(os.path.abspath(path))
        with open(path, "r", errors="replace") as f:
            for raw in f:
                line = raw.split("!")[0].split(";")[0].strip()
                if not line:
                    continue
                up = line.upper()
                if up.startswith("IDENTIFICATION=") or up.startswith("IDENT="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    self.opt_ident = val
                elif up.startswith("GSMATCH="):
                    self.opt_gsmatch = line.split("=", 1)[1].strip()
                elif up.startswith("CLUSTER="):
                    self.opt_clusters.append(line.split("=", 1)[1].strip())
                elif up.startswith("PSECT_ATTR="):
                    parts = [p.strip() for p in line.split("=", 1)[1].split(",")]
                    if parts:
                        self.opt_psect_attrs[parts[0].upper()] = parts[1:]
                elif up.startswith("UNIVERSAL=") or up.startswith("SYMBOL_VECTOR="):
                    vals = [p.strip() for p in line.split("=", 1)[1].strip("()").split(",")]
                    self.opt_universals.extend(vals)
                elif up.endswith("/SHARE") or up.endswith("/SHAREABLE"):
                    self.opt_shareables.append(line.split("/")[0].strip())
                else:
                    # Treat as an object or library specification inside the .OPT file
                    for item in [x.strip() for x in line.split(",") if x.strip()]:
                        if item.upper().startswith("SYS$"):
                            self.opt_shareables.append(item)
                        else:
                            self.load_input(item, base_dir=opt_dir)

    def load_odl(self, path):
        if not os.path.isfile(path):
            return
        with open(path, "r", errors="replace") as f:
            for raw in f:
                line = raw.split(";")[0].strip()
                if ".ROOT" in line.upper():
                    self.odl_root = line.upper().split(".ROOT", 1)[1].strip()

    def _resolve_olb_dependencies(self, include_mods=None):
        if include_mods:
            for m in include_mods:
                m_up = m.upper()
                if m_up in self.olb_modules and not any(x["module"] == m_up for x in self.obj_modules):
                    self.obj_modules.append(self.olb_modules[m_up])

        # Automatically pull any CALL_OVL targets present in loaded .OLB libraries
        added = True
        while added:
            added = False
            known = {m["module"] for m in self.obj_modules}
            for mod in list(self.obj_modules):
                for rel in mod.get("relocations", []):
                    tgt = str(rel.get("target", "")).upper()
                    if tgt and tgt not in known and tgt in self.olb_modules:
                        self.obj_modules.append(self.olb_modules[tgt])
                        known.add(tgt)
                        added = True

    def _find_vm_binary(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vax_root = os.path.abspath(os.path.join(script_dir, ".."))
        dec_root = os.path.abspath(os.path.join(vax_root, "..", ".."))
        candidates = [
            os.path.join(vax_root, "vm", "build", "vms_vm"),
            "/opt/dec-vms/system/bin/vms_vm",
            os.path.join(dec_root, "OS", "VMS", "system", "bin", "vms_vm"),
            shutil.which("vms_vm") or "",
            os.path.join(dec_root, "LANG", "BASIC-PLUS-2", "vm", "build", "rsts_vm"),
            "/opt/dec-vms/system/bin/rsts_vm",
            shutil.which("rsts_vm") or "",
        ]
        for c in candidates:
            if c and os.path.isfile(c) and os.access(c, os.X_OK):
                return c
        raise RuntimeError("%LINK-F-NOVM, OpenVMS runtime image activator (vms_vm) not found")

    def link(self, out_exe, out_map=None, full_map=False, cross_ref=False, include_mods=None):
        self._resolve_olb_dependencies(include_mods=include_mods)
        if not self.obj_modules:
            raise ValueError("%LINK-E-NOINPUT, no input object modules specified")

        num_segs = len(self.obj_modules)
        mod_index = {m["module"]: idx for idx, m in enumerate(self.obj_modules)}

        # Global symbol table across modules: symbol_name -> (mod_idx, offset)
        global_symbols = {}
        for idx, mod in enumerate(self.obj_modules):
            for sym_name, sym_off in mod.get("symbols", {}).items():
                global_symbols[sym_name.upper()] = (idx, int(sym_off))

        # Assign segment virtual addresses
        seg_vaddrs = [0] * num_segs
        if self.odl_root:
            root_sz = 0
            for idx, mod in enumerate(self.obj_modules):
                if mod["module"] == "MAIN":
                    seg_vaddrs[idx] = 0
                    root_sz = len(mod["bytecode"])
            for idx, mod in enumerate(self.obj_modules):
                if mod["module"] != "MAIN":
                    seg_vaddrs[idx] = root_sz
        else:
            cur_v = 0
            for idx, mod in enumerate(self.obj_modules):
                seg_vaddrs[idx] = cur_v
                cur_v += len(mod["bytecode"])

        # Resolve relocations in each module's bytecode copy
        resolved_bytecodes = []
        xref_records = []  # (symbol_or_target, defining_mod, ref_mod, ref_offset)
        for idx, mod in enumerate(self.obj_modules):
            bc = list(mod["bytecode"])
            for rel in mod.get("relocations", []):
                rtype = str(rel.get("type", "CALL_OVL")).upper()
                off = int(rel.get("offset", 0))
                tgt = str(rel.get("target", "")).upper()
                if rtype == "CALL_OVL":
                    if tgt == "SAVEDB":
                        tgt_idx = 39320
                    elif tgt == "LOADDB":
                        tgt_idx = 39321
                    else:
                        tgt_idx = mod_index.get(tgt, 0)
                    if off + 1 < len(bc):
                        bc[off] = tgt_idx & 0xFF
                        bc[off + 1] = (tgt_idx >> 8) & 0xFF
                    xref_records.append((tgt, tgt, mod["module"], off))
                elif rtype in ("ABS16", "REL16", "EXT16"):
                    if tgt in mod.get("symbols", {}):
                        val = int(mod["symbols"][tgt])
                        def_mod = mod["module"]
                    elif tgt in global_symbols:
                        def_idx, sym_off = global_symbols[tgt]
                        val = seg_vaddrs[def_idx] + sym_off
                        def_mod = self.obj_modules[def_idx]["module"]
                    else:
                        val = 0
                        def_mod = "*UNDEF*"
                    if off + 1 < len(bc):
                        bc[off] = val & 0xFF
                        bc[off + 1] = (val >> 8) & 0xFF
                    xref_records.append((tgt, def_mod, mod["module"], off))
            resolved_bytecodes.append(bytes(bc))

        # Build binary payload:
        # 2-byte num_segments + N * 24-byte segment headers + concatenated bytecode + "VMSX" + 4-byte payload_size
        header_parts = [struct.pack("<H", num_segs)]
        for idx, mod in enumerate(self.obj_modules):
            name_bytes = mod["module"].encode("ascii", errors="replace")[:16].ljust(16, b"\x00")
            sz = len(resolved_bytecodes[idx])
            va = seg_vaddrs[idx]
            header_parts.append(struct.pack("<16sII", name_bytes, sz, va))

        payload = b"".join(header_parts) + b"".join(resolved_bytecodes)
        footer = b"VMSX" + struct.pack("<I", len(payload))

        vm_bin = self._find_vm_binary()
        out_dir = os.path.dirname(os.path.abspath(out_exe))
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        with open(vm_bin, "rb") as vf:
            vm_bytes = vf.read()

        with open(out_exe, "wb") as out_f:
            out_f.write(vm_bytes)
            out_f.write(payload)
            out_f.write(footer)

        st = os.stat(out_exe)
        os.chmod(out_exe, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        if out_map:
            self._write_map(out_map, out_exe, seg_vaddrs, resolved_bytecodes, global_symbols, xref_records, full_map, cross_ref)

        return len(payload)

    def _write_map(self, out_map, out_exe, seg_vaddrs, resolved_bytecodes, global_symbols, xref_records, full_map, cross_ref):
        now_str = datetime.now().strftime("%d-%b-%Y %H:%M")
        img_name = os.path.splitext(os.path.basename(out_exe))[0].upper()
        total_bytes = sum(len(b) for b in resolved_bytecodes)
        with open(out_map, "w") as f:
            f.write("================================================================================\n")
            f.write(f"                        OpenVMS VAX Linker {self.VERSION} Image Map\n")
            f.write(f"  Image Name: {img_name:<18}  Ident: {self.opt_ident:<10}  Date: {now_str}\n")
            f.write("================================================================================\n\n")

            f.write("+------------------------------------------------------------------------------+\n")
            f.write("|                           Object Module Synopsis                             |\n")
            f.write("+------------------+----------+----------+--------------------+----------------+\n")
            f.write("| Module Name      | Ident    |    Bytes | Language / Creator | File           |\n")
            f.write("+------------------+----------+----------+--------------------+----------------+\n")
            for idx, mod in enumerate(self.obj_modules):
                sz = len(resolved_bytecodes[idx])
                bname = os.path.basename(mod["file"])
                f.write(
                    f"| {mod['module']:<16} | {mod['ident']:<8} | {sz:>8} | {mod['creator'][:18]:<18} | {bname:<14} |\n"
                )
            f.write("+------------------+----------+----------+--------------------+----------------+\n\n")

            f.write("+------------------------------------------------------------------------------+\n")
            f.write("|                          Program Section Synopsis                            |\n")
            f.write("+------------------+----------+----------+----------+--------------------------+\n")
            f.write("| Psect Name       |     Base |      End |   Length | Attributes               |\n")
            f.write("+------------------+----------+----------+----------+--------------------------+\n")
            for idx, mod in enumerate(self.obj_modules):
                base_va = self.VAX_P0_BASE + seg_vaddrs[idx]
                sz = len(resolved_bytecodes[idx])
                end_va = base_va + max(0, sz - 1)
                psect = f"$CODE_{mod['module']}" if idx > 0 else "$CODE"
                attrs = "PIC,CON,REL,LCL,SHR,EXE,RD,NOWRT,LONG"
                if psect in self.opt_psect_attrs:
                    attrs = ",".join(self.opt_psect_attrs[psect])
                f.write(
                    f"| {psect:<16} | {base_va:08X} | {end_va:08X} | {sz:08X} | {attrs:<24} |\n"
                )
            f.write("+------------------+----------+----------+----------+--------------------------+\n\n")

            if global_symbols or cross_ref or full_map:
                f.write("+------------------------------------------------------------------------------+\n")
                f.write("|                         Symbol Cross-Reference Map                           |\n")
                f.write("+--------------------------+----------+------------------+---------------------+\n")
                f.write("| Symbol                   |    Value | Defined In       | Referenced By       |\n")
                f.write("+--------------------------+----------+------------------+---------------------+\n")
                for sym, (m_idx, s_off) in sorted(global_symbols.items()):
                    val = self.VAX_P0_BASE + seg_vaddrs[m_idx] + s_off
                    def_mod = self.obj_modules[m_idx]["module"]
                    refs = [r[2] for r in xref_records if r[0] == sym]
                    ref_str = ",".join(sorted(set(refs))) if refs else "(entry/label)"
                    f.write(f"| {sym:<24} | {val:08X} | {def_mod:<16} | {ref_str:<19} |\n")
                for sym, def_mod, ref_mod, ref_off in xref_records:
                    if sym not in global_symbols:
                        f.write(f"| {sym:<24} | CALL_OVL | {def_mod:<16} | {ref_mod:<19} |\n")
                f.write("+--------------------------+----------+------------------+---------------------+\n\n")

            if self.opt_shareables or self.opt_universals:
                f.write("Shareable Images & Universal Symbols:\n")
                for sh in self.opt_shareables:
                    f.write(f"  Shareable Image: {sh}\n")
                for uv in self.opt_universals:
                    f.write(f"  Universal Symbol: {uv}\n")
                f.write("\n")

            f.write("Link Run Statistics:\n")
            f.write(f"  Output Image File:       {os.path.abspath(out_exe)}\n")
            f.write(f"  Total Object Modules:    {len(self.obj_modules)}\n")
            f.write(f"  Total Image Bytes:       {total_bytes}\n")
            f.write(f"  Transfer Address:        {self.VAX_P0_BASE:08X}\n")
            f.write(f"  GSMATCH Criteria:        {self.opt_gsmatch}\n")


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
        print("Usage: vmslink [-o output.exe] [-m output.map] [--full] [--cross-reference] <input1.obj> [input2.obj ...] [options.opt] [library.olb]")
        sys.exit(1)

    out_exe = None
    out_map = None
    want_default_map = False
    full_map = False
    cross_ref = False
    ident_override = None
    include_mods = []
    inputs = []

    i = 0
    while i < len(args):
        a = args[i]
        up = a.upper()
        if a in ("-o", "--output", "--executable", "-e") and i + 1 < len(args):
            out_exe = args[i + 1]
            i += 2
        elif a in ("-m", "--map") and i + 1 < len(args) and not args[i + 1].startswith("-"):
            out_map = args[i + 1]
            i += 2
        elif a in ("-m", "--map"):
            want_default_map = True
            i += 1
        elif a == "--full":
            full_map = True
            want_default_map = True
            i += 1
        elif a in ("--cross-reference", "--cref"):
            cross_ref = True
            want_default_map = True
            i += 1
        elif a == "--ident" and i + 1 < len(args):
            ident_override = args[i + 1]
            i += 2
        elif a == "--include" and i + 1 < len(args):
            include_mods.extend([x.strip() for x in args[i + 1].split(",") if x.strip()])
            i += 2
        elif up.startswith("/EXECUTABLE=") or up.startswith("/EXE="):
            out_exe = a.split("=", 1)[1]
            i += 1
        elif up.startswith("/MAP="):
            out_map = a.split("=", 1)[1]
            i += 1
        elif up == "/MAP":
            want_default_map = True
            i += 1
        elif up == "/FULL":
            full_map = True
            want_default_map = True
            i += 1
        elif up in ("/CROSS_REFERENCE", "/CREF"):
            cross_ref = True
            want_default_map = True
            i += 1
        elif not a.startswith("-"):
            # Could be comma-separated list of inputs (e.g. MAIN.OBJ,SUB.OBJ,APP.OPT/OPT)
            for part in [p.strip() for p in a.split(",") if p.strip()]:
                inputs.append(part)
            i += 1
        else:
            i += 1

    if not inputs:
        print("%LINK-E-NOINPUT, no input files specified")
        sys.exit(1)

    linker = OpenVMSLinker()
    if ident_override:
        linker.opt_ident = ident_override

    try:
        for inp in inputs:
            linker.load_input(inp)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    if not linker.obj_modules and include_mods:
        linker._resolve_olb_dependencies(include_mods=include_mods)

    if not linker.obj_modules:
        print("%LINK-E-NOOBJ, no object modules loaded to link")
        sys.exit(1)

    first_obj_file = linker.obj_modules[0]["file"].split("(")[0]
    stem, _ = os.path.splitext(first_obj_file)
    if not out_exe:
        out_exe = stem + ".EXE"
    if want_default_map and not out_map:
        out_map = os.path.splitext(out_exe)[0] + ".MAP"

    try:
        linker.link(out_exe, out_map=out_map, full_map=full_map, cross_ref=cross_ref, include_mods=include_mods)
    except Exception as e:
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
