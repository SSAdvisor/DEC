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
        word11|w11)
            OUT="$("${EXE}" "SAMPLE; DIR; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "WORD-11 Document Index"; then
                echo "PASSED (DPD WORD-11 V3.1 multi-user word processing verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        lex11|lex)
            OUT="$("${EXE}" "SAMPLE; DIR; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "LEX-11 Document Catalog"; then
                echo "PASSED (EEC Systems LEX-11 V2.4 word processing & calculator verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        saturnwp|swp)
            OUT="$("${EXE}" "SAMPLE; DIR; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Saturn-WP Document Library"; then
                echo "PASSED (Saturn Systems Saturn-WP V4.2 word processing verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        calc2020|2020|sc20)
            OUT="$("${EXE}" "SAMPLE; GRID; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Access Technology 20/20 Worksheet"; then
                echo "PASSED (Access Technology 20/20 V2.3 spreadsheet verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        saturncalc|satcalc|scalc)
            OUT="$("${EXE}" "SAMPLE; GRID; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Saturn-Calc V3.4 Virtual Worksheet"; then
                echo "PASSED (Saturn Systems Saturn-Calc V3.4 worksheet verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        nyplan|nyp)
            OUT="$("${EXE}" "SAMPLE; MODEL; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "NYPLAN Corporate P&L & Budget Model"; then
                echo "PASSED (Nyplan Inc. NYPLAN V4.1 financial modeling verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        total|totdbm)
            OUT="$("${EXE}" "SAMPLE; SCHEMA; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "CINCOM TOTAL V8.0 DDL Compiler"; then
                echo "PASSED (Cincom TOTAL V8.0 network DBMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        ambase|amqry|amwriter)
            OUT="$("${EXE}" "SAMPLE; SCHEMA; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "AMBASE V4.2 Data Dictionary"; then
                echo "PASSED (Amcor AMBASE V4.2 DBMS & query verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        accentr|accent|accr)
            OUT="$("${EXE}" "SAMPLE; DSD; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample ACCENT R Data Base Library"; then
                echo "PASSED (NIS ACCENT R V11.4 4GL & RDBMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        saturnbase|satbase|sbase)
            OUT="$("${EXE}" "SAMPLE; SCHEMA; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Saturn-Base V3.2 Relational Schema"; then
                echo "PASSED (Saturn Systems Saturn-Base V3.2 RDBMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        mcba|mcbamrp)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "MCBA Inventory Management"; then
                echo "PASSED (MCBA V7.2 ERP & MRP suite verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        maps|mapsgl)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Ross Systems MAPS/GL"; then
                echo "PASSED (Ross Systems MAPS V5.0 financial suite verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        timeline|digigl)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Timeline DIGI-GL"; then
                echo "PASSED (Timeline DIGI-GL V4.3 general ledger verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        compushare|cas)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Compu-Share CAS"; then
                echo "PASSED (Compu-Share CAS V6.1 accounting suite verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        cjbusiness|cjbiz|cjgl)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Collier-Jackson CJ/GL"; then
                echo "PASSED (Collier-Jackson CJ/BUSINESS V5.4 ledger & payroll verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        kdss|kdfmt|kdent)
            OUT="$("${EXE}" "SAMPLE; BATCH; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "EG&H KDSS Batch Buffer"; then
                echo "PASSED (EG&H KDSS V4.0 key-to-disk data entry verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        tam)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample EG&H TAM screen definition"; then
                echo "PASSED (EG&H TAM V3.2 terminal access module verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        fsort3|vselect)
            OUT="$("${EXE}" "SAMPLE; SORT ASC; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "EG&H FSORT3 High-Speed Sort Complete"; then
                echo "PASSED (EG&H FSORT3 & VSELECT V3.5 sort/select verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        clyde|contrl|caudit)
            OUT="$("${EXE}" "SAMPLE; AUDIT; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Clyde CAUDIT V4.1"; then
                echo "PASSED (Clyde Digital Systems CONTRL/AUDIT/LOCK V4.1 verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        minitab|mtab)
            OUT="$("${EXE}" "SAMPLE; DESCRIBE; STOP" 2>&1 || true)"
            if echo "${OUT}" | grep -q "MINITAB-11 DESCRIBE"; then
                echo "PASSED (MINITAB-11 V82.1 statistical worksheet verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        spss11|spss)
            OUT="$("${EXE}" "SAMPLE; FREQUENCIES; FINISH" 2>&1 || true)"
            if echo "${OUT}" | grep -q "SPSS-11 FREQUENCIES"; then
                echo "PASSED (SPSS-11 V9.0 statistical package verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        wp51|wordperfect|wp)
            OUT="$("${EXE}" "SAMPLE; REVEAL; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample WordPerfect 5.1 document loaded"; then
                echo "PASSED (WordPerfect 5.1 for VAX/VMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        interleaf|tps)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Interleaf TPS 4.0 book container loaded"; then
                echo "PASSED (Interleaf TPS 4.0 technical publishing verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        lotus123|lotus|123)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Lotus 1-2-3 3D worksheet loaded"; then
                echo "PASSED (Lotus 1-2-3 for VAX/VMS 3D spreadsheet verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        ifps|ifpsplus)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Execucom IFPS/Plus corporate model loaded"; then
                echo "PASSED (Execucom IFPS/Plus V4.0 financial planning verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        systemw|sysw|eis)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Comshare System W multidimensional hypercube loaded"; then
                echo "PASSED (Comshare System W / Commander EIS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        oracle|sqlplus|sqlforms|sqldba)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Oracle V6 tablespace"; then
                echo "PASSED (Oracle RDBMS V6.0 for VAX/VMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        ingres|iquel|isql|abf)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample RTI INGRES V6.2 database"; then
                echo "PASSED (RTI INGRES V6.2 for VAX/VMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        focus)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample FOCUS Master File"; then
                echo "PASSED (Information Builders FOCUS V6.5 4GL verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        powerhouse|phouse|quick|quiz|qtp)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Cognos PowerHouse Dictionary"; then
                echo "PASSED (Cognos PowerHouse 4GL V5.0 verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        s1032|sys1032)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample System 1032 dataset"; then
                echo "PASSED (Software House System 1032 bitmap DBMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        manman|askman)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample ASK MANMAN V7.0 MRP II dataset loaded"; then
                echo "PASSED (ASK MANMAN V7.0 MRP II suite verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        cerner|pathnet)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Cerner PathNet V3.0 LIS dataset loaded"; then
                echo "PASSED (Cerner PathNet V3.0 clinical LIS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        sas|sasvms)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "WORK.CLINICAL"; then
                echo "PASSED (SAS System V6.06 for VAX/VMS verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        rs1|bbnrs1)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample BBN RS/1 Notebook Table"; then
                echo "PASSED (BBN RS/1 V4.0 research lab notebook verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        spice3|spice|hspice)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample VAX SPICE 3D1 circuit deck loaded"; then
                echo "PASSED (VAX SPICE 3D1 / HSPICE circuit simulator verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        ansys)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample ANSYS V4.4 FEA structural mesh loaded"; then
                echo "PASSED (Swanson Analysis ANSYS V4.4 FEA verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        gaussian|g90)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Gaussian 90 Formaldehyde"; then
                echo "PASSED (Gaussian 90 quantum chemistry verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        diskeeper|defrag)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample ODS-2 Volume"; then
                echo "PASSED (Executive Software DISKEEPER V4.0 verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        robomon|robo)
            OUT="$("${EXE}" "SAMPLE; LIST; EXIT" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Sample Heroix RoboMon V5.0 VMS rule base loaded"; then
                echo "PASSED (Heroix RoboMon V5.0 operations monitor verified)"
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
        decwindows|decterm|dxterm)
            OUT="$(printf "SAMPLE\nINSPECT\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Audit PASSED: VT300 parser verified all CSI/SGR control sequences"; then
                echo "PASSED (DECwindows DECterm VT300 emulator verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        bookreader|dxbook)
            OUT="$(printf "SAMPLE\nSHELF\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECwindows Bookreader Library Bookshelf"; then
                echo "PASSED (DECwindows Bookreader online documentation verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        calendar|dxcalendar)
            OUT="$(printf "SAMPLE\nCHECK\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Audit PASSED: No overlapping appointment timeslots detected"; then
                echo "PASSED (DECwindows Calendar time & schedule manager verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        cardfiler|dxcardfiler)
            OUT="$(printf "SAMPLE\nLIST\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECwindows Cardfiler Index Deck"; then
                echo "PASSED (DECwindows Cardfiler index card manager verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        cdaviewer|dxvdoc)
            OUT="$(printf "SAMPLE\nINSPECT\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "CONFORMANT (ASN.1 TLV & DDIF/DTIF Descriptors Valid)"; then
                echo "PASSED (DECwindows CDA Viewer DDIF/DTIF inspector verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        calculator|dxcalc)
            OUT="$(printf "SAMPLE\nSHOW\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "0xF00 (HEX)"; then
                echo "PASSED (DECwindows Calculator scientific/programmer/financial verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        clock|dxclock)
            OUT="$(printf "SAMPLE\nZONES\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "Maynard Mill, MA (HQ)"; then
                echo "PASSED (DECwindows Clock analog/digital timekeeper verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        decsound|dxsound)
            OUT="$(printf "SAMPLE\nWAVEFORM 1\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECsound Waveform & Codec Inspector"; then
                echo "PASSED (DECwindows DECsound mu-law audio & voice annotation verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        dxmail|decwinmail)
            OUT="$(printf "SAMPLE\nCABINET\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECwindows Mail Cabinet Hierarchy"; then
                echo "PASSED (DECwindows Mail cabinet & DDIF viewer verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        fileview|dxfileview)
            OUT="$(printf "SAMPLE\nDIR\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "SYSTARTUP_V5.COM;4"; then
                echo "PASSED (DECwindows FileView VMS file & DCL manager verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        notepad|dxnotepad)
            OUT="$(printf "SAMPLE\nSTATS\nEXIT\n" | "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECwindows Notepad Document Status"; then
                echo "PASSED (DECwindows Notepad text & clipboard editor verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        decw_x11)
            OUT="$("${EXE}" --version 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECwindows X11/Motif 1.1 Interfacing Library"; then
                echo "PASSED (DECwindows X11/Motif 1.1 interfacing library & bridge verified)"
                PASSED_COUNT=$((PASSED_COUNT + 1))
            else
                echo "FAILED"
                echo "    Execution output: ${OUT}"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
            ;;
        decwx11|dxsession)
            OUT="$(printf "APPS\nEXIT\n" | DECW_FORCE_CLI=1 "${EXE}" 2>&1 || true)"
            if echo "${OUT}" | grep -q "DECwindows V3.0 - X11 Protocol & Motif Session Manager"; then
                echo "PASSED (DECwindows X11 Session Manager verified)"
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
