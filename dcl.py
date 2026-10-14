#!/usr/bin/env python3
import sys
import os
import subprocess

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    dcl_bin = os.path.join(repo_root, "dcl", "dcl")
    if os.path.exists(dcl_bin) and os.access(dcl_bin, os.X_OK):
        # Forward directly to compiled DEC BASIC-PLUS-2 DCL binary
        res = subprocess.run([dcl_bin] + sys.argv[1:])
        sys.exit(res.returncode)
    else:
        # Fallback to Python reference shell
        from dcl.dcl_shell import main as shell_main
        shell_main()

if __name__ == "__main__":
    main()
