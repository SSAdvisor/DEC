# DEC RSTS/E BASIC-PLUS-2 Environment for Linux

A faithful, modern reimplementation of the classic Digital Equipment Corporation (DEC) **RSTS/E BASIC-PLUS-2** programming and execution environment, running natively on 64-bit Linux.

---

## Highlights

- **Pure DEC BASIC-PLUS-2 Compiler (`compiler/basicc`)**: Written entirely in DEC BASIC-PLUS-2 (`compiler/basicc.bas`), featuring a multi-pass architecture, operator precedence expression stack, structured control flow, RMS file I/O, and alphanumeric/numeric label support.
- **Pure DEC BASIC-PLUS-2 Linker (`linker/basiclink`)**: Written in DEC BASIC-PLUS-2 (`linker/basiclink.bas`), supporting multi-module object linking, Overlay Description Language (`.odl`) tree layouts, and standalone Linux ELF binary packaging.
- **C Runtime Virtual Machine (`vm/`)**: High-performance stack-based virtual machine executing DEC RSTS/E bytecode.
- **RMS Indexed File Engine**: Embedded SQLite-backed Record Management Services supporting indexed files (`.IDX`), primary and secondary alternate keys, and `MAP` variable buffer binding.
- **DIGITAL Command Language (`dcl/dcl`)**: Native DCL processor and Print/Batch Services (PBS) shell supporting interactive commands, `.COM`/`.DCL` command procedures, and background job queues.
- **DEC EDT Editor V3.0 (`edt/edt`)**: Authentic line mode (`*`) and VT100 full-screen Change Mode text editor.
- **DEC Print Queue Service (`dec-printq`)**: Background daemon with authentic 5x5 ASCII block banner burst pages, spooling to CUPS and raw TCP socket network printers (JetDirect port 9100).
- **Distribution System (`distrib/`)**: Production-ready packaging generating standalone release kits (`.tar.gz`) with interactive/automated installers, verification suites, and SHA-256 integrity manifests.

---

## Directory Layout

```
DEC-BASIC-PLUS-2/
├── compiler/             # DEC BASIC-PLUS-2 Native Compiler (basicc.bas -> basicc)
├── linker/               # DEC BASIC-PLUS-2 Native Linker (basiclink.bas -> basiclink)
├── vm/                   # C Virtual Machine runtime and RMS SQLite engine
├── dcl/                  # DIGITAL Command Language shell and PBS job controller
├── edt/                  # DEC EDT Editor V3.0 (Line Mode & VT100 Screen Mode)
├── distrib/              # Distribution system, kit builder, installer, verification
├── bootstrap/            # Original Python/ANTLR reference toolchain for bootstrapping
├── docs/                 # Comprehensive documentation suite
│   ├── ARCHITECTURE.md   # Complete system architecture and opcode reference
│   ├── DEC_DOCUMENTATION_SUGGESTIONS.md  # Critical analysis and DEC manual suggestions
│   └── USER_GUIDE.md     # Quick start and developer guide
├── samples/              # Sample applications (Office RMS, Address Book, Games)
└── tests/                # Automated pytest test suites (53 tests, 100% pass)
```

---

## Documentation

- **[System Architecture & Opcode Specification](docs/ARCHITECTURE.md)**: Exhaustive manual detailing the compiler, linker, VM memory layout, opcode reference table, RMS SQLite engine, DCL, and EDT.
- **[Suggestions to Original DEC Documentation](docs/DEC_DOCUMENTATION_SUGGESTIONS.md)**: Scholarly analysis and proposal comparing historical DEC documentation against modern implementations, highlighting ambiguities (statement separators, substring indexing, negative loop steps) and proposing modern enhancements.
- **[User Guide & Quick Start](docs/USER_GUIDE.md)**: Practical tutorial for writing, compiling, linking, running, editing, and printing BASIC-PLUS-2 programs.

---

## Building the Distribution Kit

To generate the standalone distribution kit:
```bash
./distrib/build_kit.sh
```
This produces:
- `distrib/DEC-BASIC-PLUS-2-V10.1-L-Linux-x86_64.tar.gz` (Binary release kit)
- `distrib/DEC-BASIC-PLUS-2-V10.1-L-Source.tar.gz` (Source release kit)

To install:
```bash
tar -xzf distrib/DEC-BASIC-PLUS-2-V10.1-L-Linux-x86_64.tar.gz
cd DEC-BASIC-PLUS-2-V10.1-L-Linux-x86_64
./install.sh
```

---

## Running the Test Suite

```bash
pytest tests/
```
Output:
```
============================== 53 passed in 9.5s ==============================
```
