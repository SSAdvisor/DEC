#!/bin/bash
# ==============================================================================
# DEC VAX/VMS V5.5-2 Runtime Staging Script
# Stages the BASIC-PLUS-2 / VAX BASIC toolchain and VAX/VMS-compatible
# applications (including DECwindows X11/Motif suite) into OS/VMS/system/
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VMS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEC_ROOT="$(cd "${VMS_ROOT}/../.." && pwd)"
BP2_ROOT="${DEC_ROOT}/LANG/BASIC-PLUS-2"
APPS_ROOT="${DEC_ROOT}/APPS"
SYS_DIR="${VMS_ROOT}/system"

mkdir -p "${SYS_DIR}/bin"
mkdir -p "${SYS_DIR}/lib/dcl"
mkdir -p "${SYS_DIR}/include"
mkdir -p "${SYS_DIR}/data"

echo "Staging DEC BASIC-PLUS-2 / VAX BASIC Toolchain into ${SYS_DIR}..."

# 1. Stage BASIC-PLUS-2 binaries
for bin_name in basicc basiclink dcl edt rsts_vm dec-printq; do
    if [ -f "${BP2_ROOT}/distrib/kit/DEC-BASIC-PLUS-2-V10.1-L-Linux-x86_64/bin/${bin_name}" ]; then
        cp -f "${BP2_ROOT}/distrib/kit/DEC-BASIC-PLUS-2-V10.1-L-Linux-x86_64/bin/${bin_name}" "${SYS_DIR}/bin/${bin_name}"
        chmod 755 "${SYS_DIR}/bin/${bin_name}"
    elif [ -f "${BP2_ROOT}/${bin_name}/${bin_name}" ]; then
        cp -f "${BP2_ROOT}/${bin_name}/${bin_name}" "${SYS_DIR}/bin/${bin_name}"
        chmod 755 "${SYS_DIR}/bin/${bin_name}"
    fi
done

if [ -f "${BP2_ROOT}/compiler/basicc" ]; then
    cp -f "${BP2_ROOT}/compiler/basicc" "${SYS_DIR}/bin/basicc"
    chmod 755 "${SYS_DIR}/bin/basicc"
fi
if [ -f "${BP2_ROOT}/linker/basiclink" ]; then
    cp -f "${BP2_ROOT}/linker/basiclink" "${SYS_DIR}/bin/basiclink"
    chmod 755 "${SYS_DIR}/bin/basiclink"
fi
if [ -f "${BP2_ROOT}/dcl/job_controller.py" ]; then
    cp -f "${BP2_ROOT}/dcl/job_controller.py" "${SYS_DIR}/lib/dcl/job_controller.py"
fi
if [ -f "${BP2_ROOT}/dec-printq.py" ]; then
    cp -f "${BP2_ROOT}/dec-printq.py" "${SYS_DIR}/lib/dcl/dec-printq.py"
fi
if [ -f "${BP2_ROOT}/dec-printq.conf" ]; then
    cp -f "${BP2_ROOT}/dec-printq.conf" "${SYS_DIR}/lib/dcl/dec-printq.conf"
fi

# 2. Stage the 12 VAX/VMS-supported DEC-APPS (including decwindows; excluding PDP-11-only dibs)
VMS_APPS=(
    "hamurabi"
    "sort11"
    "rmsutils"
    "ade"
    "datatrieve11"
    "decgraph"
    "decmail"
    "decword"
    "fms11"
    "menu11"
    "indent"
    "decwindows"
)

echo "Staging 12 VAX/VMS-compatible applications (including DECwindows X11/Motif) from ${APPS_ROOT}..."
for app in "${VMS_APPS[@]}"; do
    APP_BIN_DIR="${APPS_ROOT}/apps/${app}/bin"
    if [ ! -d "${APP_BIN_DIR}" ]; then
        make -C "${APPS_ROOT}/apps/${app}" build >/dev/null
    fi
    for f in "${APP_BIN_DIR}"/*; do
        if [ -e "$f" ]; then
            cp -af "$f" "${SYS_DIR}/bin/"
        fi
    done
done

# 3. Stage DECwindows X11 shared/static libraries and headers
if [ -d "${APPS_ROOT}/apps/decwindows/lib" ]; then
    cp -af "${APPS_ROOT}/apps/decwindows/lib"/* "${SYS_DIR}/lib/" 2>/dev/null || true
fi
if [ -d "${APPS_ROOT}/apps/decwindows/include" ]; then
    cp -af "${APPS_ROOT}/apps/decwindows/include"/* "${SYS_DIR}/include/" 2>/dev/null || true
fi

# 4. Stage sample domains (YACHTS.sch, YACHTS.dat)
if [ -f "${APPS_ROOT}/YACHTS.sch" ]; then
    cp -f "${APPS_ROOT}/YACHTS.sch" "${SYS_DIR}/data/"
fi
if [ -f "${APPS_ROOT}/YACHTS.dat" ]; then
    cp -f "${APPS_ROOT}/YACHTS.dat" "${SYS_DIR}/data/"
fi

echo "VAX/VMS V5.5-2 runtime staging complete."
