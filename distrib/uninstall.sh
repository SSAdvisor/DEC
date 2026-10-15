#!/bin/bash
# ==============================================================================
# DEC RSTS/E BASIC-PLUS-2 Modern Environment Uninstaller
# ==============================================================================
set -e

if [ "$(id -u)" -eq 0 ]; then
    DEFAULT_PREFIX="/usr/local/dec-basic2"
    DEFAULT_BIN_DIR="/usr/local/bin"
else
    DEFAULT_PREFIX="${HOME}/.local/dec-basic2"
    DEFAULT_BIN_DIR="${HOME}/.local/bin"
fi

PREFIX="${1:-${DEFAULT_PREFIX}}"
LINK_BIN="${DEFAULT_BIN_DIR}"

echo "================================================================================"
echo "    DEC RSTS/E BASIC-PLUS-2 Uninstaller"
echo "================================================================================"
echo "Target Prefix: ${PREFIX}"

# 1. Remove symlinks
echo "-> Removing symlinks from ${LINK_BIN}..."
for b in basicc basiclink dcl edt rsts_vm dec-printq; do
    if [ -L "${LINK_BIN}/${b}" ]; then
        TARGET="$(readlink "${LINK_BIN}/${b}" || true)"
        if [[ "${TARGET}" == *"${PREFIX}"* ]]; then
            rm -f "${LINK_BIN}/${b}"
            echo "   Removed symlink ${LINK_BIN}/${b}"
        fi
    fi
done

# 2. Remove installation prefix
if [ -d "${PREFIX}" ]; then
    echo "-> Removing installation directory ${PREFIX}..."
    rm -rf "${PREFIX}"
    echo "   Removed ${PREFIX}"
else
    echo "   Installation directory not found: ${PREFIX}"
fi

echo "================================================================================"
echo "Uninstallation complete."
echo "================================================================================"
