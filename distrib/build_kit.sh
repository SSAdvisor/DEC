#!/bin/bash
# ==============================================================================
# DEC RSTS/E BASIC-PLUS-2 Distribution Kit Builder
# Version 10.1-L
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

VERSION="10.1-L"
TARGET="Linux-x86_64"
KIT_NAME="DEC-BASIC-PLUS-2-V${VERSION}-${TARGET}"
STAGING_DIR="${SCRIPT_DIR}/kit/${KIT_NAME}"
DIST_ARCHIVE="${SCRIPT_DIR}/${KIT_NAME}.tar.gz"
SRC_ARCHIVE="${SCRIPT_DIR}/DEC-BASIC-PLUS-2-V${VERSION}-Source.tar.gz"

echo "================================================================================"
echo "    Building Distribution Kit: ${KIT_NAME}"
echo "================================================================================"

# 1. Compile VM runtime
echo "-> Building C Runtime VM (vm/build/rsts_vm)..."
mkdir -p "${ROOT_DIR}/vm/build"
(cd "${ROOT_DIR}/vm/build" && cmake .. >/dev/null && make >/dev/null)

# 2. Rebuild native binaries
echo "-> Building native Linker (linker/basiclink)..."
bash "${ROOT_DIR}/linker/build.sh" >/dev/null

echo "-> Building native Compiler (compiler/basicc)..."
bash "${ROOT_DIR}/compiler/build.sh" >/dev/null

echo "-> Building native DCL processor (dcl/dcl)..."
bash "${ROOT_DIR}/dcl/build.sh" >/dev/null

echo "-> Building native EDT editor (edt/edt)..."
bash "${ROOT_DIR}/edt/build.sh" >/dev/null

# 3. Clean and prepare staging directory
echo "-> Preparing staging directory: ${STAGING_DIR}..."
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}/bin"
mkdir -p "${STAGING_DIR}/lib/dcl"
mkdir -p "${STAGING_DIR}/docs"
mkdir -p "${STAGING_DIR}/samples/hello"
mkdir -p "${STAGING_DIR}/samples/office"
mkdir -p "${STAGING_DIR}/samples/address_book"
mkdir -p "${STAGING_DIR}/samples/games"
mkdir -p "${STAGING_DIR}/bootstrap/grammar"

# 4. Copy Binaries
echo "-> Staging executables..."
cp "${ROOT_DIR}/compiler/basicc" "${STAGING_DIR}/bin/"
cp "${ROOT_DIR}/linker/basiclink" "${STAGING_DIR}/bin/"
cp "${ROOT_DIR}/dcl/dcl" "${STAGING_DIR}/bin/"
cp "${ROOT_DIR}/edt/edt" "${STAGING_DIR}/bin/"
cp "${ROOT_DIR}/vm/build/rsts_vm" "${STAGING_DIR}/bin/"

# Wrapper for dec-printq
cat << 'EOF' > "${STAGING_DIR}/bin/dec-printq"
#!/usr/bin/env bash
REAL_BIN="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "${REAL_BIN}")"
LIB_DIR="$(cd "${SCRIPT_DIR}/../lib/dcl" && pwd)"
export PYTHONPATH="${LIB_DIR}:${PYTHONPATH}"
exec python3 "${LIB_DIR}/print_service.py" "$@"
EOF
chmod 755 "${STAGING_DIR}/bin/dec-printq"

# 5. Copy Libraries and Subsystems
echo "-> Staging libraries and DCL services..."
cp "${ROOT_DIR}/dcl/job_controller.py" "${STAGING_DIR}/lib/dcl/"
cp "${ROOT_DIR}/dcl/print_service.py" "${STAGING_DIR}/lib/dcl/"
cp "${ROOT_DIR}/dec-printq.conf" "${STAGING_DIR}/lib/dcl/"

# 6. Copy Bootstrap Toolchain
echo "-> Staging bootstrap toolchain..."
cp "${ROOT_DIR}/bootstrap/basicc.py" "${STAGING_DIR}/bootstrap/"
cp "${ROOT_DIR}/bootstrap/basiclink.py" "${STAGING_DIR}/bootstrap/"
cp "${ROOT_DIR}/bootstrap/requirements.txt" "${STAGING_DIR}/bootstrap/"
cp "${ROOT_DIR}/bootstrap/README.md" "${STAGING_DIR}/bootstrap/"
cp -r "${ROOT_DIR}/bootstrap/grammar/"* "${STAGING_DIR}/bootstrap/grammar/"

# 7. Copy Samples
echo "-> Staging sample programs..."
cp -r "${ROOT_DIR}/samples/hello/"* "${STAGING_DIR}/samples/hello/"
cp -r "${ROOT_DIR}/samples/office/"* "${STAGING_DIR}/samples/office/"
cp -r "${ROOT_DIR}/samples/address_book/"* "${STAGING_DIR}/samples/address_book/"
cp -r "${ROOT_DIR}/samples/games/"* "${STAGING_DIR}/samples/games/"

# 8. Copy Documentation
echo "-> Staging documentation..."
cp "${ROOT_DIR}/docs/ARCHITECTURE.md" "${STAGING_DIR}/docs/"
cp "${ROOT_DIR}/docs/DEC_DOCUMENTATION_SUGGESTIONS.md" "${STAGING_DIR}/docs/"
cp "${ROOT_DIR}/docs/USER_GUIDE.md" "${STAGING_DIR}/docs/"
cp "${ROOT_DIR}/compiler/README.md" "${STAGING_DIR}/docs/compiler.md"
cp "${ROOT_DIR}/linker/README.md" "${STAGING_DIR}/docs/linker.md"
cp "${ROOT_DIR}/dcl/README.md" "${STAGING_DIR}/docs/dcl.md"
cp "${ROOT_DIR}/edt/README.md" "${STAGING_DIR}/docs/edt.md"

# Top-level README for the kit
cat << EOF > "${STAGING_DIR}/README.md"
# DEC RSTS/E BASIC-PLUS-2 Modern Environment
**Release Version**: ${VERSION}
**Target Platform**: ${TARGET}
**Build Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Quick Installation
To install DEC BASIC-PLUS-2:
\`\`\`bash
./install.sh
\`\`\`
For custom prefix:
\`\`\`bash
./install.sh --prefix=/opt/dec-basic2
\`\`\`

## Included Subsystems
- \`bin/basicc\`: Pure DEC BASIC-PLUS-2 Compiler
- \`bin/basiclink\`: Pure DEC BASIC-PLUS-2 Linker and Overlay Manager
- \`bin/rsts_vm\`: High-performance C Bytecode Runtime
- \`bin/dcl\`: DIGITAL Command Language (DCL) Processor & PBS Shell
- \`bin/edt\`: DEC EDT Editor V3.0 (Line Mode & VT100 Screen Mode)
- \`bin/dec-printq\`: Print/Batch Services Symbiont Daemon

See \`docs/USER_GUIDE.md\` and \`docs/ARCHITECTURE.md\` for complete instructions.
EOF

# 9. Copy installer, uninstaller, and verification scripts
cp "${SCRIPT_DIR}/install.sh" "${STAGING_DIR}/"
cp "${SCRIPT_DIR}/uninstall.sh" "${STAGING_DIR}/"
cp "${SCRIPT_DIR}/verify_kit.sh" "${STAGING_DIR}/"
chmod 755 "${STAGING_DIR}/install.sh" "${STAGING_DIR}/uninstall.sh" "${STAGING_DIR}/verify_kit.sh"

# 10. Generate KIT.INI Manifest
echo "-> Generating KIT.INI..."
cat << EOF > "${STAGING_DIR}/KIT.INI"
[KIT]
Name=DEC-BASIC-PLUS-2
Version=${VERSION}
Architecture=${TARGET}
BuildDate=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
Vendor=Digital Equipment Corporation / DEC-BASIC-PLUS-2 Project
Description=Authentic DEC BASIC-PLUS-2 Compiler, Linker, Runtime VM, DCL, and EDT Editor for Linux

[COMPONENTS]
Compiler=bin/basicc
Linker=bin/basiclink
Runtime=bin/rsts_vm
CommandLanguage=bin/dcl
Editor=bin/edt
PrintQueue=bin/dec-printq
Bootstrap=bootstrap/
Documentation=docs/
Samples=samples/
EOF

# 11. Generate MANIFEST.TXT with SHA256 checksums
echo "-> Generating MANIFEST.TXT (SHA-256)..."
(cd "${STAGING_DIR}" && find . -type f -not -name "MANIFEST.TXT" | sort | xargs sha256sum > "${STAGING_DIR}/MANIFEST.TXT")

# 12. Run verification on the staged kit
echo "-> Verifying staged kit integrity..."
bash "${STAGING_DIR}/verify_kit.sh"

# 13. Create Release Tarball Archives
echo "-> Compressing binary release kit: ${DIST_ARCHIVE}..."
(cd "${SCRIPT_DIR}/kit" && tar -czf "${DIST_ARCHIVE}" "${KIT_NAME}")

echo "-> Compressing source release kit: ${SRC_ARCHIVE}..."
(cd "${ROOT_DIR}" && git archive --format=tar.gz --prefix="DEC-BASIC-PLUS-2-V${VERSION}-Source/" -o "${SRC_ARCHIVE}" HEAD 2>/dev/null || tar --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='distrib/kit' -czf "${SRC_ARCHIVE}" -C "${ROOT_DIR}" .)

echo ""
echo "================================================================================"
echo "    DISTRIBUTION KIT GENERATION COMPLETE!"
echo "================================================================================"
echo "Staged Directory:  ${STAGING_DIR}"
echo "Binary Archive:    ${DIST_ARCHIVE} ($(du -h "${DIST_ARCHIVE}" | cut -f1))"
echo "Source Archive:    ${SRC_ARCHIVE} ($(du -h "${SRC_ARCHIVE}" | cut -f1))"
echo "================================================================================"
