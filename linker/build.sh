#!/bin/bash
# ==============================================================================
# Build Script for DEC RSTS/E Linker (DEC BASIC-PLUS-2)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Building DEC RSTS/E Linker (basiclink) ==="
echo "Compiling linker/basiclink.bas with bootstrap compiler..."
python3 "${ROOT_DIR}/bootstrap/basicc.py" "${SCRIPT_DIR}/basiclink.bas" -o "${SCRIPT_DIR}/basiclink.obj"

echo "Linking linker/basiclink with bootstrap linker..."
python3 "${ROOT_DIR}/bootstrap/basiclink.py" "${SCRIPT_DIR}/basiclink.obj" -o "${SCRIPT_DIR}/basiclink"

echo "Build successful: ${SCRIPT_DIR}/basiclink"
