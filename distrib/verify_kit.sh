#!/bin/bash
# ==============================================================================
# DEC RSTS/E BASIC-PLUS-2 Kit Verification Script
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Identify bin directory
if [ -n "${DEC_BASIC_BIN}" ] && [ -d "${DEC_BASIC_BIN}" ]; then
    BIN_DIR="${DEC_BASIC_BIN}"
elif [ -d "${SCRIPT_DIR}/bin" ]; then
    BIN_DIR="${SCRIPT_DIR}/bin"
elif command -v basicc >/dev/null 2>&1; then
    BIN_DIR="$(dirname "$(command -v basicc)")"
else
    BIN_DIR="/usr/local/dec-basic2/bin"
fi

export DEC_BASIC_HOME="$(cd "${BIN_DIR}/.." && pwd)"
export PATH="${BIN_DIR}:${PATH}"

echo "================================================================================"
echo "    DEC RSTS/E BASIC-PLUS-2 Subsystem Verification"
echo "================================================================================"
echo "Using Binaries in: ${BIN_DIR}"
echo "DEC_BASIC_HOME:    ${DEC_BASIC_HOME}"
echo ""

TMP_DIR="$(mktemp -d /tmp/dec_verify_XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT

# Check 1: Check required executables exist
echo -n "Checking binary presence... "
for b in basicc basiclink dcl edt rsts_vm; do
    if [ ! -x "${BIN_DIR}/${b}" ]; then
        echo "FAILED"
        echo "Error: Required binary ${BIN_DIR}/${b} is missing or not executable."
        exit 1
    fi
done
echo "OK"

# Check 2: Native Compiler test
echo -n "Testing DEC BASIC-PLUS-2 Compiler (basicc)... "
cat << 'EOF' > "${TMP_DIR}/test_prog.bas"
10 ! ==============================================
20 ! Test program for kit verification
30 ! ==============================================
40 DATA 100, 200, "VERIFY_OK"
50 READ A%, B%, MSG$
60 PRINT "RESULT="; A% + B%; " "; MSG$; " DATE="; DATE$(0%)
70 END
EOF

"${BIN_DIR}/basicc" "${TMP_DIR}/test_prog.bas" -o "${TMP_DIR}/test_prog.bobj" >/dev/null 2>&1
if [ ! -f "${TMP_DIR}/test_prog.bobj" ]; then
    echo "FAILED"
    echo "Error: Compiler failed to produce test_prog.bobj."
    exit 1
fi
echo "PASSED"

# Check 3: Native Linker test
echo -n "Testing DEC BASIC-PLUS-2 Linker (basiclink)... "
"${BIN_DIR}/basiclink" "${TMP_DIR}/test_prog.bobj" -o "${TMP_DIR}/test_prog_exe" >/dev/null 2>&1
if [ ! -x "${TMP_DIR}/test_prog_exe" ]; then
    echo "FAILED"
    echo "Error: Linker failed to produce executable binary."
    exit 1
fi
echo "PASSED"

# Check 4: Native Runtime Execution
echo -n "Testing standalone executable execution (rsts_vm)... "
OUT="$("${TMP_DIR}/test_prog_exe" 2>&1)"
if [[ "${OUT}" != *"RESULT=300 VERIFY_OK"* ]]; then
    echo "FAILED"
    echo "Unexpected execution output: ${OUT}"
    exit 1
fi
echo "PASSED"

# Check 5: DIGITAL Command Language (DCL)
echo -n "Testing DIGITAL Command Language (dcl)... "
DCL_OUT="$("${BIN_DIR}/dcl" "SHOW SYSTEM" 2>&1)"
if [[ "${DCL_OUT}" != *"RSTS/E"* ]] || [[ "${DCL_OUT}" != *"Host Platform"* ]]; then
    echo "FAILED"
    echo "Unexpected DCL output: ${DCL_OUT}"
    exit 1
fi
echo "PASSED"

# Check 6: DEC EDT Editor V3.0
echo -n "Testing DEC EDT Editor V3.0 (edt)... "
touch "${TMP_DIR}/test_doc.txt"
EDT_OUT="$(printf "%s\n" "${TMP_DIR}/test_doc.txt" "T WHOLE" "QUIT" | "${BIN_DIR}/edt" 2>&1)"
if [[ "${EDT_OUT}" != *"EDT"* ]]; then
    echo "FAILED"
    echo "Unexpected EDT output: ${EDT_OUT}"
    exit 1
fi
echo "PASSED"

echo ""
echo "================================================================================"
echo "    ALL 6 VERIFICATION CHECKS PASSED SUCCESSFULLY!"
echo "================================================================================"
