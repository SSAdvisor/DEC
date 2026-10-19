#!/bin/bash
# ==============================================================================
# DEC-APPS Distribution Kit Builder
# Version 1.0-L (Linux x86_64)
# Digital Equipment Corporation / DEC-APPS Project
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

VERSION="1.0-L"
TARGET="Linux-x86_64"
KIT_NAME="DEC-APPS-V${VERSION}-${TARGET}"
STAGING_DIR="${SCRIPT_DIR}/kit/${KIT_NAME}"
MASTER_ARCHIVE="${SCRIPT_DIR}/${KIT_NAME}.tar.gz"
SRC_ARCHIVE="${SCRIPT_DIR}/DEC-APPS-V${VERSION}-Source.tar.gz"

echo "================================================================================"
echo "    Building DEC-APPS Distribution Kits: Version ${VERSION}"
echo "================================================================================"

# 1. Discover and build all applications
echo "-> Discovering applications in apps/..."
APP_LIST=()
for d in "${ROOT_DIR}/apps"/*; do
    if [ -d "$d" ] && [ -f "$d/Makefile" ]; then
        app_name="$(basename "$d")"
        APP_LIST+=("$app_name")
        echo "   [+] Found sub-project: ${app_name}"
        echo "       Compiling and linking ${app_name}..."
        make -C "$d" build >/dev/null
    fi
done

if [ ${#APP_LIST[@]} -eq 0 ]; then
    echo "Error: No applications found to package."
    exit 1
fi

# Clean kit staging root
mkdir -p "${SCRIPT_DIR}/kit"
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}/bin"
mkdir -p "${STAGING_DIR}/docs"

# 2. Stage Master Kit
echo "-> Staging Master Distribution Kit: ${STAGING_DIR}..."

for app in "${APP_LIST[@]}"; do
    if [ -d "${ROOT_DIR}/apps/${app}/bin" ]; then
        cp -a "${ROOT_DIR}/apps/${app}/bin"/* "${STAGING_DIR}/bin/"
        chmod 755 "${STAGING_DIR}/bin"/*
    fi
    if [ -d "${ROOT_DIR}/apps/${app}/lib" ]; then
        mkdir -p "${STAGING_DIR}/lib"
        cp -a "${ROOT_DIR}/apps/${app}/lib"/* "${STAGING_DIR}/lib/"
    fi
    if [ -d "${ROOT_DIR}/apps/${app}/include" ]; then
        mkdir -p "${STAGING_DIR}/include"
        cp -a "${ROOT_DIR}/apps/${app}/include"/* "${STAGING_DIR}/include/"
    fi

    DOC_SRC="${ROOT_DIR}/apps/${app}/README.md"
    if [ -f "${DOC_SRC}" ]; then
        cp -a "${DOC_SRC}" "${STAGING_DIR}/docs/${app}.md"
    fi
done

# Copy root documentation and license
if [ -f "${ROOT_DIR}/LICENSE" ]; then
    cp -a "${ROOT_DIR}/LICENSE" "${STAGING_DIR}/"
fi
if [ -f "${ROOT_DIR}/README.md" ]; then
    cp -a "${ROOT_DIR}/README.md" "${STAGING_DIR}/docs/DEC-APPS.md"
fi

# Copy management scripts
cp -a "${SCRIPT_DIR}/install.sh" "${STAGING_DIR}/"
cp -a "${SCRIPT_DIR}/uninstall.sh" "${STAGING_DIR}/"
cp -a "${SCRIPT_DIR}/verify_kit.sh" "${STAGING_DIR}/"
chmod 755 "${STAGING_DIR}/install.sh" "${STAGING_DIR}/uninstall.sh" "${STAGING_DIR}/verify_kit.sh"

# Create kit README
cat << EOF > "${STAGING_DIR}/README.md"
# DEC-APPS Master Distribution Kit
**Version**: ${VERSION}
**Architecture**: ${TARGET}
**Build Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Quick Installation
Install all DEC applications:
\`\`\`bash
./install.sh
\`\`\`

Install an individual application:
\`\`\`bash
./install.sh hamurabi
# or
./install.sh sort11
\`\`\`

List all available applications:
\`\`\`bash
./install.sh --list
\`\`\`

Uninstall applications:
\`\`\`bash
./uninstall.sh           # Uninstall all
./uninstall.sh sort11    # Uninstall only sort11
\`\`\`
EOF

# Generate KIT.INI for master kit
echo "-> Generating KIT.INI manifest..."
cat << EOF > "${STAGING_DIR}/KIT.INI"
[KIT]
Name=DEC-APPS
Version=${VERSION}
Architecture=${TARGET}
BuildDate=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
Vendor=Digital Equipment Corporation / DEC-APPS Project
Description=Classic Digital Equipment Corporation (DEC) Applications Collection for Linux

[APPLICATIONS]
EOF

for app in "${APP_LIST[@]}"; do
    echo "${app}=bin/${app}" >> "${STAGING_DIR}/KIT.INI"
done

# Generate MANIFEST.TXT (SHA-256)
echo "-> Generating MANIFEST.TXT (SHA-256)..."
(cd "${STAGING_DIR}" && find . -type f -not -name "MANIFEST.TXT" | sort | xargs sha256sum > "${STAGING_DIR}/MANIFEST.TXT")

# Verify staged master kit
echo "-> Verifying master kit integrity..."
bash "${STAGING_DIR}/verify_kit.sh"

# Compress Master Archive
echo "-> Compressing master binary release archive: ${MASTER_ARCHIVE}..."
(cd "${SCRIPT_DIR}/kit" && tar -czf "${MASTER_ARCHIVE}" "${KIT_NAME}")

# 3. Stage and Package Individual Application Kits
INDIVIDUAL_ARCHIVES=()
for app in "${APP_LIST[@]}"; do
    APP_KIT_NAME="DEC-APPS-${app}-V${VERSION}-${TARGET}"
    APP_STAGING="${SCRIPT_DIR}/kit/${APP_KIT_NAME}"
    APP_ARCHIVE="${SCRIPT_DIR}/${APP_KIT_NAME}.tar.gz"
    INDIVIDUAL_ARCHIVES+=("${APP_ARCHIVE}")

    echo "-> Staging individual application kit for ${app} (${APP_KIT_NAME})..."
    rm -rf "${APP_STAGING}"
    mkdir -p "${APP_STAGING}/bin"
    mkdir -p "${APP_STAGING}/docs"

    if [ -d "${ROOT_DIR}/apps/${app}/bin" ]; then
        cp -a "${ROOT_DIR}/apps/${app}/bin"/* "${APP_STAGING}/bin/"
        chmod 755 "${APP_STAGING}/bin"/*
    fi
    if [ -d "${ROOT_DIR}/apps/${app}/lib" ]; then
        mkdir -p "${APP_STAGING}/lib"
        cp -a "${ROOT_DIR}/apps/${app}/lib"/* "${APP_STAGING}/lib/"
    fi
    if [ -d "${ROOT_DIR}/apps/${app}/include" ]; then
        mkdir -p "${APP_STAGING}/include"
        cp -a "${ROOT_DIR}/apps/${app}/include"/* "${APP_STAGING}/include/"
    fi

    if [ -f "${ROOT_DIR}/apps/${app}/README.md" ]; then
        cp -a "${ROOT_DIR}/apps/${app}/README.md" "${APP_STAGING}/docs/${app}.md"
    fi
    if [ -f "${ROOT_DIR}/LICENSE" ]; then
        cp -a "${ROOT_DIR}/LICENSE" "${APP_STAGING}/"
    fi

    # Management scripts
    cp -a "${SCRIPT_DIR}/install.sh" "${APP_STAGING}/"
    cp -a "${SCRIPT_DIR}/uninstall.sh" "${APP_STAGING}/"
    cp -a "${SCRIPT_DIR}/verify_kit.sh" "${APP_STAGING}/"
    chmod 755 "${APP_STAGING}/install.sh" "${APP_STAGING}/uninstall.sh" "${APP_STAGING}/verify_kit.sh"

    # Per-application README
    cat << EOF > "${APP_STAGING}/README.md"
# DEC-APPS: ${app} Distribution Kit
**Version**: ${VERSION}
**Application**: ${app}
**Architecture**: ${TARGET}
**Build Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Installation
To install ${app}:
\`\`\`bash
./install.sh
\`\`\`

## Uninstallation
To uninstall ${app}:
\`\`\`bash
./uninstall.sh
\`\`\`
EOF

    # Per-application KIT.INI
    cat << EOF > "${APP_STAGING}/KIT.INI"
[KIT]
Name=DEC-APPS-${app}
Application=${app}
Version=${VERSION}
Architecture=${TARGET}
BuildDate=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
Vendor=Digital Equipment Corporation / DEC-APPS Project
Description=DEC Application: ${app}

[APPLICATIONS]
EOF
    for b in "${APP_STAGING}/bin"/*; do
        if [ -f "$b" ] && [ -x "$b" ]; then
            bname="$(basename "$b")"
            echo "${bname}=bin/${bname}" >> "${APP_STAGING}/KIT.INI"
        fi
    done

    # Per-application MANIFEST.TXT
    (cd "${APP_STAGING}" && find . -type f -not -name "MANIFEST.TXT" | sort | xargs sha256sum > "${APP_STAGING}/MANIFEST.TXT")

    # Verify individual kit
    bash "${APP_STAGING}/verify_kit.sh" "${app}" >/dev/null

    # Compress individual archive
    (cd "${SCRIPT_DIR}/kit" && tar -czf "${APP_ARCHIVE}" "${APP_KIT_NAME}")
done

# 4. Create Source Archive
echo "-> Compressing source release kit: ${SRC_ARCHIVE}..."
(cd "${ROOT_DIR}" && git archive --format=tar.gz --prefix="DEC-APPS-V${VERSION}-Source/" -o "${SRC_ARCHIVE}" HEAD 2>/dev/null || tar --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='distrib/kit' --exclude='distrib/*.tar.gz' -czf "${SRC_ARCHIVE}" -C "${ROOT_DIR}" .)

echo ""
echo "================================================================================"
echo "    DISTRIBUTION KITS GENERATION COMPLETE!"
echo "================================================================================"
echo "Master Archive:       ${MASTER_ARCHIVE} ($(du -h "${MASTER_ARCHIVE}" | cut -f1))"
echo "Individual Kits:"
for a in "${INDIVIDUAL_ARCHIVES[@]}"; do
    echo "  - $(basename "$a") ($(du -h "$a" | cut -f1))"
done
echo "Source Archive:       ${SRC_ARCHIVE} ($(du -h "${SRC_ARCHIVE}" | cut -f1))"
echo "================================================================================"
