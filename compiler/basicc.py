#!/usr/bin/env python3
import os
import sys

# Forwarding shim to bootstrap implementation
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bootstrap_dir = os.path.join(repo_root, "bootstrap")
if bootstrap_dir not in sys.path:
    sys.path.insert(0, bootstrap_dir)

import basicc

if __name__ == '__main__':
    basicc.main()
