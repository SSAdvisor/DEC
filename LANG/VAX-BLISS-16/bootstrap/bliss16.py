#!/usr/bin/env python3
"""
DEC VAX BLISS-16 V4.2 16-Bit Compatibility Systems Language Compiler (bliss16.py)
Digital Equipment Corporation VAX/VMS V5.5-2 (PDP-11 / VAX Compatibility Mode)

Compiles DEC VAX BLISS-16 source files (.B16 / .BLI) into OpenVMS relocatable
object modules (.OBJ) compatible with vmslink and vms_vm, and generates optional
compiler listing files (.LST).
"""

import os
import sys

# Import shared BLISS compiler core from VAX-BLISS-32 or fallback path
_HERE = os.path.dirname(os.path.abspath(__file__))
_B32_DIRS = [
    os.path.abspath(os.path.join(_HERE, "..", "..", "VAX-BLISS-32", "bootstrap")),
    "/opt/dec-vms/system/lib/lang",
    "/home/ssadvisor/AGYprojects/DEC/LANG/VAX-BLISS-32/bootstrap",
]
for _d in _B32_DIRS:
    if os.path.isdir(_d) and _d not in sys.path:
        sys.path.insert(0, _d)

from bliss32 import BLISSCompiler, run_cli  # noqa: E402


class BLISS16Compiler(BLISSCompiler):
    COMPILER_NAME = "VAX BLISS-16"
    VERSION = "V4.2-00"
    CREATOR = "VAX BLISS-16 V4.2"
    WORD_BITS = 16


if __name__ == "__main__":
    run_cli(BLISS16Compiler, (".B16", ".b16", ".BLI", ".bli"), "BLISS16")
