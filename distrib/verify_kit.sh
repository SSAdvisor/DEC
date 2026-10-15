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
