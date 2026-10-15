#!/bin/bash
# ==============================================================================
# Build Script for DEC RSTS/E BASIC-PLUS-2 Compiler (basicc)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Building DEC RSTS/E Compiler (basicc) ==="
echo "Compiling compiler/basicc.bas with bootstrap compiler..."
python3 "${ROOT_DIR}/bootstrap/basicc.py" "${SCRIPT_DIR}/basicc.bas" -o "${SCRIPT_DIR}/basicc.bobj"

echo "Linking compiler/basicc with linker..."
if [ -x "${ROOT_DIR}/linker/basiclink" ]; then
    "${ROOT_DIR}/linker/basiclink" "${SCRIPT_DIR}/basicc.bobj" -o "${SCRIPT_DIR}/basicc"
else
    python3 "${ROOT_DIR}/bootstrap/basiclink.py" "${SCRIPT_DIR}/basicc.bobj" -o "${SCRIPT_DIR}/basicc"
fi

echo "Build successful: ${SCRIPT_DIR}/basicc"
