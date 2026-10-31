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
VAXBASIC_ROOT="${DEC_ROOT}/LANG/VAX-BASIC"
APPS_ROOT="${DEC_ROOT}/APPS"
SYS_DIR="${VMS_ROOT}/system"

mkdir -p "${SYS_DIR}/bin"
mkdir -p "${SYS_DIR}/lib/dcl"
mkdir -p "${SYS_DIR}/lib/lang"
mkdir -p "${SYS_DIR}/include"
mkdir -p "${SYS_DIR}/data"

echo "Staging DEC VAX BASIC V3.5, OpenVMS Linker V05-05, and BASIC-PLUS-2 Toolchain into ${SYS_DIR}..."

# 1a. Build and stage VAX BASIC V3.5, OpenVMS VAX Linker V05-05 & 17 VAX Language Compilers
if [ -d "${VAXBASIC_ROOT}" ]; then
    make -C "${VAXBASIC_ROOT}" build >/dev/null
    cp -f "${VAXBASIC_ROOT}/compiler/vaxbasic" "${SYS_DIR}/bin/vaxbasic"
    cp -f "${VAXBASIC_ROOT}/linker/vmslink" "${SYS_DIR}/bin/vmslink"
    cp -f "${VAXBASIC_ROOT}/vm/build/vms_vm" "${SYS_DIR}/bin/vms_vm"
    chmod 755 "${SYS_DIR}/bin/vaxbasic" "${SYS_DIR}/bin/vmslink" "${SYS_DIR}/bin/vms_vm"
    cp -f "${VAXBASIC_ROOT}/bootstrap/vaxbasic.py" "${SYS_DIR}/lib/lang/vaxbasic.py"
    cp -f "${VAXBASIC_ROOT}/bootstrap/vmslink.py" "${SYS_DIR}/lib/lang/vmslink.py"
    chmod 755 "${SYS_DIR}/lib/lang/vaxbasic.py" "${SYS_DIR}/lib/lang/vmslink.py"
fi

VAX_LANG_SPECS=(
    "VAX-MACRO:vaxmacro:DEMO.MAR"
    "VAX-FORTRAN:vaxfor:DEMO.FOR"
    "VAX-COBOL:vaxcobol:DEMO.COB"
    "VAX-C:vaxc:DEMO.C"
    "VAX-PASCAL:vaxpas:DEMO.PAS"
    "VAX-PLI:vaxpli:DEMO.PLI"
    "VAX-ADA:vaxada:DEMO.ADA"
    "VAX-DIBOL:vaxdibol:DEMO.DBL"
    "VAX-BLISS-32:bliss32:DEMO.B32"
    "VAX-BLISS-16:bliss16:DEMO.B16"
    "VAX-RPG-II:vaxrpg:DEMO.RPG"
    "VAX-APL:vaxapl:DEMO.APL"
    "VAX-LISP:vaxlisp:DEMO.LSP"
    "VAX-OPS5:vaxops5:DEMO.OPS"
    "VAX-DSM:vaxdsm:DEMO.DSM"
    "VAX-SCAN:vaxscan:DEMO.SCN"
    "VAX-CORAL-66:vaxcoral:DEMO.COR"
)

mkdir -p "${SYS_DIR}/data/samples"
echo "Staging 17 VAX/VMS language compilers into ${SYS_DIR}..."
for spec in "${VAX_LANG_SPECS[@]}"; do
    IFS=":" read -r lang_dir bin_name demo_file <<< "${spec}"
    LANG_PATH="${DEC_ROOT}/LANG/${lang_dir}"
    if [ -d "${LANG_PATH}" ]; then
        if [ ! -f "${LANG_PATH}/compiler/${bin_name}" ]; then
            make -C "${LANG_PATH}" build >/dev/null
        fi
        cp -f "${LANG_PATH}/compiler/${bin_name}" "${SYS_DIR}/bin/${bin_name}"
        chmod 755 "${SYS_DIR}/bin/${bin_name}"
        cp -f "${LANG_PATH}/bootstrap/${bin_name}.py" "${SYS_DIR}/lib/lang/${bin_name}.py"
        chmod 755 "${SYS_DIR}/lib/lang/${bin_name}.py"
        if [ -f "${LANG_PATH}/samples/${demo_file}" ]; then
            cp -f "${LANG_PATH}/samples/${demo_file}" "${SYS_DIR}/data/samples/${demo_file}"
        fi
    fi
done

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

# 2. Stage the 52 VAX/VMS-supported DEC-APPS (including decwindows; excluding PDP-11-only dibs)
VMS_APPS=(
    "hamurabi"
    "sort11"
    "rmsutils"
    "ade"
    "datatrieve11"
    "decgraph"
    "decmail"
    "decword"
    "word11"
    "lex11"
    "saturnwp"
    "wp51"
    "interleaf"
    "calc2020"
    "saturncalc"
    "nyplan"
    "lotus123"
    "ifps"
    "systemw"
    "total"
    "ambase"
    "accentr"
    "saturnbase"
    "oracle"
    "ingres"
    "focus"
    "powerhouse"
    "s1032"
    "mcba"
    "maps"
    "timeline"
    "compushare"
    "cjbusiness"
    "manman"
    "cerner"
    "kdss"
    "tam"
    "fsort3"
    "clyde"
    "minitab"
    "spss11"
    "sas"
    "rs1"
    "spice3"
    "ansys"
    "gaussian"
    "diskeeper"
    "robomon"
    "fms11"
    "menu11"
    "indent"
    "coupon"
    "decwindows"
)

echo "Staging 53 VAX/VMS-compatible applications (including DECwindows X11/Motif) from ${APPS_ROOT}..."
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
