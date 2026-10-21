# DEC RSTS/E BASIC-PLUS-2 Linker (`basiclink`)

An authentic, standalone implementation of the **DEC RSTS/E Linker and Overlay Manager**, written entirely in **DEC BASIC-PLUS-2** (`linker/basiclink.bas`) and compiled into a native executable (`linker/basiclink`).

## Overview

The linker links one or more compiled object modules (`.obj` files) and optional Overlay Description Language (`.odl`) configuration files into native, standalone Linux executables.

### Key Capabilities

- **Multi-Module Linking**: Resolves module names and cross-segment `CALL_OVL` relocations.
- **RMS/Database Interception**: Built-in support for `SAVEDB` and `LOADDB` database runtime handlers.
- **ODL Overlay Trees**: Parses `.ROOT` and `.FCTR` definitions to lay out segment virtual addresses (`vaddr`).
- **Binary Executable Packaging**: Appends the compiled RSTS/E payload (segment table, data pool, and `"RSTS"` magic footer) to `vm/build/rsts_vm` and marks it executable (`chmod 755`).
- **Zero Python Dependency**: Runs natively under the RSTS/E bytecode VM.

## Usage

```bash
# Link single module into standalone executable:
./linker/basiclink tests/test_link.obj -o test_link_app

# Link multiple modules with ODL overlay file:
./linker/basiclink tests/main.obj tests/func1.obj tests/func2.obj tests/test.odl -o overlay_app
```

## Building from Source

To bootstrap `linker/basiclink`:
```bash
./linker/build.sh
```
This invokes `bootstrap/basicc.py` and `bootstrap/basiclink.py` to compile `linker/basiclink.bas` into `linker/basiclink`.
