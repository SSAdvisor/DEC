#!/bin/bash
# ==============================================================================
# Build Script for DEC RSTS/E DCL & PBS Subsystem (DEC BASIC-PLUS-2)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Building DEC RSTS/E DCL Interpreter ==="
echo "Compiling dcl/dcl.bas with basicc.py..."
python3 "${ROOT_DIR}/compiler/basicc.py" "${SCRIPT_DIR}/dcl.bas" -o "${SCRIPT_DIR}/dcl.obj"

echo "Linking dcl/dcl with basiclink.py..."
python3 "${ROOT_DIR}/compiler/basiclink.py" "${SCRIPT_DIR}/dcl.obj" -o "${SCRIPT_DIR}/dcl"

echo "Build successful: ${SCRIPT_DIR}/dcl"
