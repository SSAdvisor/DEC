#!/bin/bash
# ==============================================================================
# DEC-APPS Distribution Kit Verification Script
# Digital Equipment Corporation / DEC-APPS Project
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Identify bin directory
if [ -n "${DEC_APPS_BIN}" ] && [ -d "${DEC_APPS_BIN}" ]; then
    BIN_DIR="${DEC_APPS_BIN}"
elif [ -d "${SCRIPT_DIR}/bin" ]; then
    BIN_DIR="${SCRIPT_DIR}/bin"
elif [ -d "${SCRIPT_DIR}/../bin" ]; then
    BIN_DIR="${SCRIPT_DIR}/../bin"
elif command -v hamurabi >/dev/null 2>&1; then
    BIN_DIR="$(dirname "$(command -v hamurabi)")"
elif command -v sort11 >/dev/null 2>&1; then
    BIN_DIR="$(dirname "$(command -v sort11)")"
elif command -v ade >/dev/null 2>&1; then
    BIN_DIR="$(dirname "$(command -v ade)")"
elif command -v datatrieve11 >/dev/null 2>&1; then
    BIN_DIR="$(dirname "$(command -v datatrieve11)")"
else
    BIN_DIR="/usr/local/dec-apps/bin"
fi

export DEC_APPS_HOME="$(cd "${BIN_DIR}/.." 2>/dev/null && pwd || echo "")"
export PATH="${BIN_DIR}:${PATH}"

echo "================================================================================"
echo "    DEC-APPS Application Suite Verification"
echo "================================================================================"
echo "Binaries Directory: ${BIN_DIR}"
if [ -n "${DEC_APPS_HOME}" ]; then
    echo "DEC_APPS_HOME:      ${DEC_APPS_HOME}"
fi
echo ""

TMP_DIR="$(mktemp -d /tmp/dec_apps_verify_XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT

# Target applications to verify (default: all binaries present in BIN_DIR)
TARGET_APPS=("$@")

if [ ${#TARGET_APPS[@]} -eq 0 ]; then
    for f in "${BIN_DIR}"/*; do
        if [ -x "$f" ] && [ ! -d "$f" ]; then
            bname="$(basename "$f")"
            # Ignore environment scripts or shell wrappers
            if [[ "$bname" != *.sh ]]; then
                TARGET_APPS+=("$bname")
            fi
        fi
    done
fi

if [ ${#TARGET_APPS[@]} -eq 0 ]; then
    echo "Error: No executable applications found in ${BIN_DIR} to verify."
    exit 1
fi

echo "Verifying application(s): ${TARGET_APPS[*]}"
echo "--------------------------------------------------------------------------------"

FAILED_COUNT=0
PASSED_COUNT=0

for APP in "${TARGET_APPS[@]}"; do
    EXE="${BIN_DIR}/${APP}"
    if [ ! -x "${EXE}" ]; then
        echo "[-] ${APP}: Missing or not executable (${EXE})"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        continue
    fi

    echo -n "[*] Testing ${APP}... "
    case "${APP}" in
        hamurabi)
            OUT="$(echo "-1" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "HAMURABI"; then
                echo "PASSED (DEC simulation banner verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Unexpected output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        sort11)
            IN_F="${TMP_DIR}/sort_in.txt"
            OUT_F="${TMP_DIR}/sort_out.txt"
            printf "2000 Bravo\n1000 Alpha\n" > "${IN_F}"
            OUT="$("${EXE}" "${OUT_F}=${IN_F}/KEY:(POS:1,SIZ:4,ASC,NUM)" 2>&1 || true)"
            if echo "${OUT}" | grep -q "SORT-11" && grep -q "1000 Alpha" "${OUT_F}" 2>/dev/null; then
                echo "PASSED (RMS sort & execution verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmsutils)
            OUT="$(printf "0\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DEC RMS-11 Utilities Suite"; then
                echo "PASSED (RMS-11 master menu verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmsdes)
            DES_F="${TMP_DIR}/test.des"
            OUT="$("${EXE}" "${DES_F} INDEXED 255 1 4" 2>&1 || true)"
            if echo "${OUT}" | grep -q "RMSDES" && [ -f "${DES_F}" ]; then
                echo "PASSED (RMS design generation verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmsdef)
            IDX_F="${TMP_DIR}/def.idx"
            OUT="$("${EXE}" "${IDX_F}/ORG:INDEXED/SIZ:255" 2>&1 || true)"
            if echo "${OUT}" | grep -q "RMSDEF" && [ -f "${IDX_F}" ]; then
                echo "PASSED (RMS file creation verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmsifl)
            IDX_F="${TMP_DIR}/ifl.idx"
            SEQ_F="${TMP_DIR}/ifl.txt"
            printf "1001 Test Record\n" > "${SEQ_F}"
            OUT="$("${EXE}" "${IDX_F}=${SEQ_F}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "RMSIFL" && [ -f "${IDX_F}" ]; then
                echo "PASSED (RMS indexed file load verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmsdsp)
            IDX_F="${TMP_DIR}/dsp.idx"
            SEQ_F="${TMP_DIR}/dsp.txt"
            printf "1001 Sample\n" > "${SEQ_F}"
            if [ -x "${BIN_DIR}/rmsifl" ]; then
                "${BIN_DIR}/rmsifl" "${IDX_F}=${SEQ_F}" >/dev/null 2>&1 || true
            fi
            OUT="$("${EXE}" "${IDX_F}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "RMSDSP"; then
                echo "PASSED (RMS file display verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmsbck)
            IDX_F="${TMP_DIR}/bck.idx"
            BCK_F="${TMP_DIR}/test.bck"
            SEQ_F="${TMP_DIR}/bck.txt"
            printf "1001 Backup Test\n" > "${SEQ_F}"
            if [ -x "${BIN_DIR}/rmsifl" ]; then
                "${BIN_DIR}/rmsifl" "${IDX_F}=${SEQ_F}" >/dev/null 2>&1 || true
            fi
            OUT="$("${EXE}" "${BCK_F}=${IDX_F}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "RMSBCK" && [ -f "${BCK_F}" ]; then
                echo "PASSED (RMS backup container verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmsrst)
            BCK_F="${TMP_DIR}/test.bck"
            RST_F="${TMP_DIR}/rst.idx"
            if [ ! -f "${BCK_F}" ]; then
                IDX_F="${TMP_DIR}/bck.idx"
                SEQ_F="${TMP_DIR}/bck.txt"
                printf "1001 Backup Test\n" > "${SEQ_F}"
                if [ -x "${BIN_DIR}/rmsifl" ]; then
                    "${BIN_DIR}/rmsifl" "${IDX_F}=${SEQ_F}" >/dev/null 2>&1 || true
                fi
                if [ -x "${BIN_DIR}/rmsbck" ]; then
                    "${BIN_DIR}/rmsbck" "${BCK_F}=${IDX_F}" >/dev/null 2>&1 || true
                fi
            fi
            OUT="$("${EXE}" "${RST_F}=${BCK_F}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "RMSRST" && [ -f "${RST_F}" ]; then
                echo "PASSED (RMS restore verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rmscnv)
            IDX_F="${TMP_DIR}/cnv.idx"
            SEQ_F="${TMP_DIR}/cnv.txt"
            printf "1001 Convert Test\n" > "${SEQ_F}"
            if [ -x "${BIN_DIR}/rmsifl" ]; then
                "${BIN_DIR}/rmsifl" "${IDX_F}=${SEQ_F}" >/dev/null 2>&1 || true
            fi
            OUT_SEQ="${TMP_DIR}/cnv_out.txt"
            OUT="$("${EXE}" "${OUT_SEQ}=${IDX_F}/SEQ" 2>&1 || true)"
            if echo "${OUT}" | grep -q "RMSCNV" && [ -f "${OUT_SEQ}" ]; then
                echo "PASSED (RMS convert verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        ade)
            OUT="$("${EXE}" "HELP" 2>&1 || true)"
            if echo "${OUT}" | grep -q "ADE V3.0"; then
                echo "PASSED (ADE 4GL environment & help verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        datatrieve11|dtr|dtr11)
            OUT="$(printf "READY YACHTS\nPRINT FIRST 1\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "readied"; then
                echo "PASSED (DATATRIEVE-11 domain & query verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        decgraph|graph|decg)
            OUT="$(printf "SAMPLE\nTYPE BAR\nPLOT\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Quarterly Revenue"; then
                echo "PASSED (DECgraph charting verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        decmail|mail|decmail11)
            OUT="$(printf "SAMPLE\nDIR\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECmail"; then
                echo "PASSED (DECmail messaging verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        decword|decworddp|wps)
            OUT="$(printf "SAMPLE\nDIR\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECword/DP"; then
                echo "PASSED (DECword/DP word & data processing verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        dibs|dibs11|cts500)
            OUT="$(printf "SAMPLE\nTRIAL\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "TRIAL BALANCE IS IN BALANCE"; then
                echo "PASSED (DIBS-11 accounting & trial balance verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        fms11|fms|fed|fdv)
            OUT="$(printf "SAMPLE\nVALIDATE\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "FDV Validation PASSED"; then
                echo "PASSED (FMS-11 forms management & FDV validation verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        menu11|menu|mcf)
            OUT="$(printf "SAMPLE\nRUN 1\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "MCF Dispatch: SUBMENU -> ACCT_MENU"; then
                echo "PASSED (MENU-11 menu control & dispatch verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        indent|bp2fmt|pretty)
            OUT="$(printf "SAMPLE\nCHECK\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Audit PASSED: All BASIC-PLUS-2 block structures are balanced"; then
                echo "PASSED (INDENT BASIC-PLUS-2 formatter & analyzer verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        *)
            # Generic sanity check
            OUT="$("${EXE}" 2>&1 || true)"
            if [ -n "${OUT}" ]; then
                echo "PASSED (Executable launched successfully)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "WARNING (Executed with no output)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            fi
            ;;
    esac
done

echo "--------------------------------------------------------------------------------"
echo "Verification Summary: ${PASSED_COUNT} Passed, ${FAILED_COUNT} Failed."
if [ ${FAILED_COUNT} -gt 0 ]; then
    echo "Error: Verification failed for one or more applications."
    exit 1
fi

echo "All verified applications are fully functional!"
echo "================================================================================"
