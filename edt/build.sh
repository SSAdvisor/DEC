#!/bin/bash
# ==============================================================================
# Build Script for DEC RSTS/E EDT Editor V3.0 (DEC BASIC-PLUS-2)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Building DEC EDT Text Editor ==="
echo "Compiling edt/edt.bas with basicc.py..."
python3 "${ROOT_DIR}/compiler/basicc.py" "${SCRIPT_DIR}/edt.bas" -o "${SCRIPT_DIR}/edt.bobj"

echo "Linking edt/edt with basiclink.py..."
python3 "${ROOT_DIR}/compiler/basiclink.py" "${SCRIPT_DIR}/edt.bobj" -o "${SCRIPT_DIR}/edt"

echo "Build successful: ${SCRIPT_DIR}/edt"
