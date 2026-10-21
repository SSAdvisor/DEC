#!/bin/bash
# ==============================================================================
# DEC RSTS/E BASIC-PLUS-2 Modern Environment Installer
# Version 10.1-L (Linux x86_64)
# Copyright (C) Digital Equipment Corporation / DEC-BASIC-PLUS-2 Project
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default installation prefix
if [ "$(id -u)" -eq 0 ]; then
    DEFAULT_PREFIX="/usr/local/dec-basic2"
    DEFAULT_BIN_DIR="/usr/local/bin"
else
    DEFAULT_PREFIX="${HOME}/.local/dec-basic2"
    DEFAULT_BIN_DIR="${HOME}/.local/bin"
fi

PREFIX="${DEFAULT_PREFIX}"
LINK_BIN="${DEFAULT_BIN_DIR}"
CREATE_SYMLINKS=true
RUN_VERIFY=true

# Parse command line flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix=*)
            PREFIX="${1#*=}"
            shift
            ;;
        --prefix|-p)
            PREFIX="$2"
            shift 2
            ;;
        --no-symlinks)
            CREATE_SYMLINKS=false
            shift
            ;;
        --symlink-dir=*)
            LINK_BIN="${1#*=}"
            shift
            ;;
        --no-verify)
            RUN_VERIFY=false
            shift
            ;;
        --help|-h)
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --prefix=<dir>, -p <dir>  Installation target directory (default: ${DEFAULT_PREFIX})"
            echo "  --symlink-dir=<dir>       Directory for global symlinks (default: ${DEFAULT_BIN_DIR})"
            echo "  --no-symlinks             Do not create symlinks in global bin directory"
            echo "  --no-verify               Skip post-installation verification tests"
            echo "  --help, -h                Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

echo "================================================================================"
echo "    DEC RSTS/E BASIC-PLUS-2 Modern Environment Installer V10.1-L"
echo "================================================================================"
echo "Installation Prefix:    ${PREFIX}"
echo "Global Symlinks:        $([ "${CREATE_SYMLINKS}" = true ] && echo "${LINK_BIN}" || echo "Disabled")"
echo "Run Verification:       ${RUN_VERIFY}"
echo "--------------------------------------------------------------------------------"

# 1. Create target directories
echo "-> Creating directories..."
mkdir -p "${PREFIX}/bin"
mkdir -p "${PREFIX}/docs"
mkdir -p "${PREFIX}/samples"
mkdir -p "${PREFIX}/bootstrap"

# 2. Copy binaries
echo "-> Installing executables..."
cp -a "${SCRIPT_DIR}/bin/"* "${PREFIX}/bin/"
chmod 755 "${PREFIX}/bin/"*

# 3. Copy documentation and license
echo "-> Installing documentation..."
cp -a "${SCRIPT_DIR}/docs/"* "${PREFIX}/docs/"
if [ -f "${SCRIPT_DIR}/LICENSE" ]; then
    cp -a "${SCRIPT_DIR}/LICENSE" "${PREFIX}/"
fi

# 4. Copy samples
echo "-> Installing sample applications..."
cp -a "${SCRIPT_DIR}/samples/"* "${PREFIX}/samples/"

# 5. Copy bootstrap toolchain
if [ -d "${SCRIPT_DIR}/bootstrap" ]; then
    echo "-> Installing bootstrapping toolchain..."
    cp -a "${SCRIPT_DIR}/bootstrap/"* "${PREFIX}/bootstrap/"
fi

# 6. Copy libraries and subsystems
if [ -d "${SCRIPT_DIR}/lib" ]; then
    echo "-> Installing libraries..."
    mkdir -p "${PREFIX}/lib"
    cp -a "${SCRIPT_DIR}/lib/"* "${PREFIX}/lib/"
fi

# 7. Generate basic_env.sh
echo "-> Generating environment profile snippet..."
cat << EOF > "${PREFIX}/bin/basic_env.sh"
# DEC RSTS/E BASIC-PLUS-2 Environment Settings
export DEC_BASIC_HOME="${PREFIX}"
export PATH="\${DEC_BASIC_HOME}/bin:\${PATH}"
EOF
chmod 644 "${PREFIX}/bin/basic_env.sh"

# 8. Create symlinks in global bin if enabled
if [ "${CREATE_SYMLINKS}" = true ]; then
    if [ "${PREFIX}/bin" = "${LINK_BIN}" ]; then
        echo "-> Binaries are directly installed in ${LINK_BIN}; skipping symlinks."
    else
        echo "-> Creating symlinks in ${LINK_BIN}..."
        mkdir -p "${LINK_BIN}"
        for b in basicc basiclink dcl edt rsts_vm dec-printq; do
            if [ -x "${PREFIX}/bin/${b}" ]; then
                ln -sf "${PREFIX}/bin/${b}" "${LINK_BIN}/${b}"
            fi
        done
    fi
fi

# 8. Run verification if requested
if [ "${RUN_VERIFY}" = true ]; then
    echo "--------------------------------------------------------------------------------"
    echo "-> Running post-installation verification tests..."
    if [ -f "${SCRIPT_DIR}/verify_kit.sh" ]; then
        DEC_BASIC_BIN="${PREFIX}/bin" bash "${SCRIPT_DIR}/verify_kit.sh"
    else
        echo "Verification script not found; skipping."
    fi
fi

echo "================================================================================"
echo "Installation complete!"
echo ""
echo "To use DEC BASIC-PLUS-2 in your current shell, run:"
echo "  source \"${PREFIX}/bin/basic_env.sh\""
echo ""
echo "Or add it to your ~/.bashrc:"
echo "  echo 'source \"${PREFIX}/bin/basic_env.sh\"' >> ~/.bashrc"
echo "================================================================================"
