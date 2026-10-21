#!/bin/bash
# ==============================================================================
# DEC RSTS/E V10.1-L Runtime Staging Script
# Stages the BASIC-PLUS-2 toolchain and RSTS/E-compatible applications from
# LANG/BASIC-PLUS-2 and APPS into OS/RSTS-E/system/ for host & Docker execution.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RSTS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEC_ROOT="$(cd "${RSTS_ROOT}/../.." && pwd)"
BP2_ROOT="${DEC_ROOT}/LANG/BASIC-PLUS-2"
APPS_ROOT="${DEC_ROOT}/APPS"
SYS_DIR="${RSTS_ROOT}/system"

mkdir -p "${SYS_DIR}/bin"
mkdir -p "${SYS_DIR}/lib/dcl"
mkdir -p "${SYS_DIR}/bootstrap"
mkdir -p "${SYS_DIR}/data"

echo "Staging DEC BASIC-PLUS-2 System Toolchain into ${SYS_DIR}..."

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

# 2. Stage the 12 RSTS/E-supported DEC-APPS (excluding VAX/VMS-only decwindows)
RSTS_APPS=(
    "hamurabi"
    "sort11"
    "rmsutils"
    "ade"
    "datatrieve11"
    "decgraph"
    "decmail"
    "decword"
    "dibs"
    "fms11"
    "menu11"
    "indent"
)

echo "Staging 12 RSTS/E-compatible applications from ${APPS_ROOT}..."
for app in "${RSTS_APPS[@]}"; do
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

# 3. Stage sample domains (YACHTS.sch, YACHTS.dat)
if [ -f "${APPS_ROOT}/YACHTS.sch" ]; then
    cp -f "${APPS_ROOT}/YACHTS.sch" "${SYS_DIR}/data/"
fi
if [ -f "${APPS_ROOT}/YACHTS.dat" ]; then
    cp -f "${APPS_ROOT}/YACHTS.dat" "${SYS_DIR}/data/"
fi

echo "RSTS/E V10.1-L runtime staging complete."
