#!/bin/bash
# ==============================================================================
# DEC-APPS Application Suite Installer
# Version 1.0-L (Linux x86_64)
# Digital Equipment Corporation / DEC-APPS Project
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Discover available applications in this kit
AVAILABLE_APPS=()
if [ -d "${SCRIPT_DIR}/bin" ]; then
    for f in "${SCRIPT_DIR}/bin"/*; do
        if [ -x "$f" ] && [ ! -d "$f" ]; then
            bname="$(basename "$f")"
            if [[ "$bname" != *.sh ]]; then
                case "$bname" in
                    rmsdes|rmsdef|rmsifl|rmscnv|rmsbck|rmsrst|rmsdsp|dtr|dtr11|graph|decg|mail|decmail11|decworddp|wps|w11|lex|swp|2020|sc20|satcalc|scalc|nyp|totdbm|amqry|amwriter|accent|accr|satbase|sbase|mcbamrp|mapsgl|digigl|cas|cjbiz|cjgl|kdfmt|kdent|vselect|contrl|caudit|mtab|spss|wordperfect|wp|tps|lotus|123|ifpsplus|sysw|eis|sqlplus|sqlforms|sqldba|iquel|isql|abf|phouse|quick|quiz|qtp|sys1032|askman|pathnet|sasvms|bbnrs1|spice|hspice|g90|defrag|robo|dibs11|cts500|fms|fed|fdv|menu|mcf|bp2fmt|pretty|decw_x11|decwx11|dxsession|decterm|dxterm|bookreader|dxbook|calendar|dxcalendar|cardfiler|dxcardfiler|cdaviewer|dxvdoc|calculator|dxcalc|clock|dxclock|decsound|dxsound|dxmail|decwinmail|fileview|dxfileview|notepad|dxnotepad)
                        ;;
                    *)
                        AVAILABLE_APPS+=("$bname")
                        ;;
                esac
            fi
        fi
    done
fi

# Fallback discovery if running directly from project root/distrib
if [ ${#AVAILABLE_APPS[@]} -eq 0 ] && [ -d "${SCRIPT_DIR}/../apps" ]; then
    for d in "${SCRIPT_DIR}/../apps"/*; do
        if [ -d "$d" ] && [ -f "$d/Makefile" ]; then
            AVAILABLE_APPS+=("$(basename "$d")")
        fi
    done
fi

# Default installation paths
if [ "$(id -u)" -eq 0 ]; then
    DEFAULT_PREFIX="/usr/local/dec-apps"
    DEFAULT_BIN_DIR="/usr/local/bin"
else
    DEFAULT_PREFIX="${HOME}/.local/dec-apps"
    DEFAULT_BIN_DIR="${HOME}/.local/bin"
fi

PREFIX="${DEFAULT_PREFIX}"
LINK_BIN="${DEFAULT_BIN_DIR}"
CREATE_SYMLINKS=true
RUN_VERIFY=true
SELECTED_APPS=()

# Function to display help
show_help() {
    cat << EOF
Usage: ./install.sh [OPTIONS] [APP...]

Install Digital Equipment Corporation (DEC) applications individually or all at once.

Arguments:
  APP                       Name of specific application(s) to install (e.g. 'sort11', 'hamurabi').
                            If omitted or set to 'all', all available applications will be installed.

Options:
  --prefix=<dir>, -p <dir>  Target installation directory (default: ${DEFAULT_PREFIX})
  --symlink-dir=<dir>       Directory for global symlinks (default: ${DEFAULT_BIN_DIR})
  --no-symlinks             Do not create symlinks in global bin directory
  --no-verify               Skip post-installation functional verification
  --list, -l                List all available applications in this kit
  --app=<name>              Specify an application to install (can be repeated)
  --help, -h                Show this help message

Available applications in this kit:
  ${AVAILABLE_APPS[*]:-None found}

Examples:
  ./install.sh                     # Install all applications
  ./install.sh sort11              # Install only SORT-11
  ./install.sh hamurabi sort11     # Install Hamurabi and SORT-11
  ./install.sh --prefix=/opt/dec   # Install all into custom prefix
EOF
    exit 0
}

# Function to list available applications
list_apps() {
    echo "Available DEC applications in this distribution kit:"
    echo "--------------------------------------------------------------------------------"
    printf "%-16s %-18s %s\n" "APPLICATION" "CATEGORY" "DESCRIPTION"
    echo "--------------------------------------------------------------------------------"
    for app in "${AVAILABLE_APPS[@]}"; do
        case "$app" in
            hamurabi)
                printf "%-16s %-18s %s\n" "hamurabi" "Simulation / Game" "Ancient Sumeria city-state economic simulation"
                ;;
            sort11)
                printf "%-16s %-18s %s\n" "sort11" "System Utility" "DEC RMS file sort and SQLite-backed index utility"
                ;;
            rmsutils)
                printf "%-16s %-18s %s\n" "rmsutils" "RMS Utilities" "DEC RMS-11 utilities suite (RMSDES, RMSDEF, RMSIFL, RMSCNV, RMSBCK, RMSRST, RMSDSP)"
                ;;
            ade)
                printf "%-16s %-18s %s\n" "ade" "4GL / Database" "Application Development Environment & 4GL data manager"
                ;;
            datatrieve11)
                printf "%-16s %-18s %s\n" "datatrieve11" "4GL Query & Report" "DEC DATATRIEVE-11 interactive query, report, and data management"
                ;;
            decgraph)
                printf "%-16s %-18s %s\n" "decgraph" "Business Graphics" "DECgraph presentation graphics and scientific charting system"
                ;;
            decmail)
                printf "%-16s %-18s %s\n" "decmail" "Office / Messaging" "DECmail electronic messaging and mailbox management system"
                ;;
            decword)
                printf "%-16s %-18s %s\n" "decword" "Word & Data Proc" "DECword/DP word processing, WPS ruler formatting, and mail-merge"
                ;;
            dibs)
                printf "%-16s %-18s %s\n" "dibs" "Business / ERP" "DIBS-11 DEC Integrated Business System (GL, AR, AP, Inventory)"
                ;;
            fms11)
                printf "%-16s %-18s %s\n" "fms11" "Forms Management" "FMS-11 DEC Forms Management System (FED, FLB, FUT, FDV)"
                ;;
            menu11)
                printf "%-16s %-18s %s\n" "menu11" "Menu Control" "MENU-11 DEC Menu Control & Application Dispatch Facility (MCF)"
                ;;
            indent)
                printf "%-16s %-18s %s\n" "indent" "Dev Utility" "INDENT DEC BASIC-PLUS-2 source code formatter & structure analyzer"
                ;;
            decwindows)
                printf "%-16s %-18s %s\n" "decwindows" "Workstation GUI" "DECwindows XUI/Motif desktop suite (DECterm, Bookreader, Calendar, etc.)"
                ;;
            word11)
                printf "%-16s %-18s %s\n" "word11" "Office / WP" "DPD WORD-11 V3.1 multi-user word processing & list processing (RSTS/E)"
                ;;
            lex11)
                printf "%-16s %-18s %s\n" "lex11" "Office / WP" "EEC Systems LEX-11 V2.4 word processing, desk calculator & mass-mailer"
                ;;
            saturnwp)
                printf "%-16s %-18s %s\n" "saturnwp" "Office / WP" "Saturn Systems Saturn-WP V4.2 integrated word processor & Saturn-Calc link"
                ;;
            calc2020)
                printf "%-16s %-18s %s\n" "calc2020" "Spreadsheet" "Access Technology 20/20 V2.3 (Supercomp-20) electronic spreadsheet"
                ;;
            saturncalc)
                printf "%-16s %-18s %s\n" "saturncalc" "Spreadsheet" "Saturn Systems Saturn-Calc V3.4 VT100 electronic worksheet"
                ;;
            nyplan)
                printf "%-16s %-18s %s\n" "nyplan" "Financial Model" "Nyplan Inc. NYPLAN V4.1 corporate financial modeling & risk simulation"
                ;;
            total)
                printf "%-16s %-18s %s\n" "total" "Network DBMS" "Cincom Systems TOTAL V8.0 network DBMS ( Master & Variable files )"
                ;;
            ambase)
                printf "%-16s %-18s %s\n" "ambase" "RSTS/E DBMS" "Amcor Computer Corp. AMBASE V4.2 DBMS, AMQRY & AMWRITER"
                ;;
            accentr)
                printf "%-16s %-18s %s\n" "accentr" "4GL & RDBMS" "National Information Systems ACCENT R V11.4 4GL & RDBMS"
                ;;
            saturnbase)
                printf "%-16s %-18s %s\n" "saturnbase" "Relational DBMS" "Saturn Systems Saturn-Base V3.2 relational data manager"
                ;;
            mcba)
                printf "%-16s %-18s %s\n" "mcba" "ERP / MRP" "MCBA V7.2 Accounting, Distribution & Manufacturing MRP Suite"
                ;;
            maps)
                printf "%-16s %-18s %s\n" "maps" "Financial / GL" "Ross Systems MAPS/GL & MAPS/MODEL V5.0 Financial Suite"
                ;;
            timeline)
                printf "%-16s %-18s %s\n" "timeline" "Accounting / GL" "Timeline Inc. DIGI-GL V4.3 General Ledger & Financial Statements"
                ;;
            compushare)
                printf "%-16s %-18s %s\n" "compushare" "Accounting / ERP" "Compu-Share CAS V6.1 Commercial Accounting System (GL/AP/AR/OE)"
                ;;
            cjbusiness)
                printf "%-16s %-18s %s\n" "cjbusiness" "Business / Payroll" "Collier-Jackson CJ/BUSINESS V5.4 Ledger & Payroll System"
                ;;
            kdss)
                printf "%-16s %-18s %s\n" "kdss" "Data Entry" "Evans Griffiths & Hart KDSS V4.0 Key-to-Disk Data Entry Subsystem"
                ;;
            tam)
                printf "%-16s %-18s %s\n" "tam" "Screen Manager" "Evans Griffiths & Hart TAM V3.2 Terminal Access Module"
                ;;
            fsort3)
                printf "%-16s %-18s %s\n" "fsort3" "Sort / Select" "Evans Griffiths & Hart FSORT3 & VSELECT V3.5 High-Speed Sort"
                ;;
            clyde)
                printf "%-16s %-18s %s\n" "clyde" "Security / Audit" "Clyde Digital Systems CONTRL / AUDIT / LOCK V4.1 Security Suite"
                ;;
            minitab)
                printf "%-16s %-18s %s\n" "minitab" "Statistics" "Minitab Inc. / Penn State MINITAB-11 V82.1 Statistical Worksheet"
                ;;
            spss11)
                printf "%-16s %-18s %s\n" "spss11" "Statistics" "SPSS Inc. SPSS-11 V9.0 Statistical Package for the Social Sciences"
                ;;
            wp51)
                printf "%-16s %-18s %s\n" "wp51" "VAX Office / WP" "WordPerfect 5.1 for VAX/VMS (Reveal Codes, Speller, Mail-Merge)"
                ;;
            interleaf)
                printf "%-16s %-18s %s\n" "interleaf" "VAX Publishing" "Interleaf TPS 4.0 Technical Publishing Software for VAXstation"
                ;;
            lotus123)
                printf "%-16s %-18s %s\n" "lotus123" "VAX Spreadsheet" "Lotus 1-2-3 for VAX/VMS V1.0 3D Multi-Sheet Spreadsheet (.WK3)"
                ;;
            ifps)
                printf "%-16s %-18s %s\n" "ifps" "VAX Financial" "Execucom IFPS/Plus V4.0 Interactive Financial Planning System"
                ;;
            systemw)
                printf "%-16s %-18s %s\n" "systemw" "VAX OLAP / EIS" "Comshare System W / Commander EIS Multidimensional DSS"
                ;;
            oracle)
                printf "%-16s %-18s %s\n" "oracle" "VAX RDBMS" "Oracle RDBMS V6.0 for VAX/VMS (SQL*Plus, SQL*Forms, SQL*DBA)"
                ;;
            ingres)
                printf "%-16s %-18s %s\n" "ingres" "VAX RDBMS" "RTI INGRES V6.2 for VAX/VMS (QUEL, SQL, VIFRED, ABF)"
                ;;
            focus)
                printf "%-16s %-18s %s\n" "focus" "VAX 4GL / DBMS" "Information Builders FOCUS V6.5 4GL & Reporting System"
                ;;
            powerhouse)
                printf "%-16s %-18s %s\n" "powerhouse" "VAX 4GL Suite" "Cognos PowerHouse 4GL V5.0 (PDL, QUICK, QUIZ, QTP)"
                ;;
            s1032)
                printf "%-16s %-18s %s\n" "s1032" "VAX Bitmap DBMS" "Software House System 1032 VAX/VMS 4GL & Compressed Bitmap DBMS"
                ;;
            manman)
                printf "%-16s %-18s %s\n" "manman" "VAX MRP II / ERP" "ASK MANMAN V7.0 Manufacturing Management MRP II Suite"
                ;;
            cerner)
                printf "%-16s %-18s %s\n" "cerner" "VAX Clinical LIS" "Cerner PathNet V3.0 Clinical Laboratory Information System"
                ;;
            sas)
                printf "%-16s %-18s %s\n" "sas" "VAX Statistics" "SAS System V6.06 for VAX/VMS (DATA Step & Statistical PROCs)"
                ;;
            rs1)
                printf "%-16s %-18s %s\n" "rs1" "VAX Lab Notebook" "BBN RS/1 V4.0 Electronic Research Notebook & Curve Fitting"
                ;;
            spice3)
                printf "%-16s %-18s %s\n" "spice3" "VAX CAD / IC Sim" "VAX SPICE 3D1 / HSPICE Electronic Circuit Simulator"
                ;;
            ansys)
                printf "%-16s %-18s %s\n" "ansys" "VAX CAE / FEA" "Swanson Analysis ANSYS V4.4 Finite Element Analysis Suite"
                ;;
            gaussian)
                printf "%-16s %-18s %s\n" "gaussian" "VAX Comp Chem" "Gaussian 90 Ab Initio Quantum Chemistry System"
                ;;
            diskeeper)
                printf "%-16s %-18s %s\n" "diskeeper" "VAX Disk Utility" "Executive Software DISKEEPER V4.0 Online ODS-2 Disk Defragmenter"
                ;;
            robomon)
                printf "%-16s %-18s %s\n" "robomon" "VAX Ops Monitor" "Heroix RoboMon V5.0 Rule-Based VAX/VMS Operations Manager"
                ;;
            coupon)
                printf "%-16s %-18s %s\n" "coupon" "LCS System Admin" "Legacy Computing Systems SYSTEM Discount Coupon Manager"
                ;;
            *)
                printf "%-16s %-18s %s\n" "$app" "Application" "DEC System Application ($app)"
                ;;
        esac
    done
    echo "--------------------------------------------------------------------------------"
    exit 0
}

# Parse command line flags and positional arguments
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
        --symlink-dir=*)
            LINK_BIN="${1#*=}"
            shift
            ;;
        --no-symlinks)
            CREATE_SYMLINKS=false
            shift
            ;;
        --no-verify)
            RUN_VERIFY=false
            shift
            ;;
        --list|-l|--list-apps)
            list_apps
            ;;
        --app=*)
            SELECTED_APPS+=("${1#*=}")
            shift
            ;;
        --help|-h)
            show_help
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
        *)
            if [ "$1" = "all" ] || [ "$1" = "ALL" ]; then
                SELECTED_APPS=("${AVAILABLE_APPS[@]}")
            else
                SELECTED_APPS+=("$1")
            fi
            shift
            ;;
    esac
done

# If no specific apps requested, install all available
if [ ${#SELECTED_APPS[@]} -eq 0 ]; then
    SELECTED_APPS=("${AVAILABLE_APPS[@]}")
fi

# Validate requested applications
VALID_APPS=()
for req in "${SELECTED_APPS[@]}"; do
    FOUND=false
    for avail in "${AVAILABLE_APPS[@]}"; do
        if [ "$req" = "$avail" ]; then
            FOUND=true
            VALID_APPS+=("$req")
            break
        fi
    done
    if [ "$FOUND" = false ]; then
        echo "Error: Requested application '$req' is not available in this kit."
        echo "Available applications: ${AVAILABLE_APPS[*]}"
        exit 1
    fi
done

echo "================================================================================"
echo "    DEC-APPS Application Suite Installer V1.0-L"
echo "================================================================================"
echo "Installation Prefix:    ${PREFIX}"
echo "Global Symlinks:        $([ "${CREATE_SYMLINKS}" = true ] && echo "${LINK_BIN}" || echo "Disabled")"
echo "Target Applications:    ${VALID_APPS[*]}"
echo "Run Verification:       ${RUN_VERIFY}"
echo "--------------------------------------------------------------------------------"

# 1. Create target directories
mkdir -p "${PREFIX}/bin"
mkdir -p "${PREFIX}/docs"
mkdir -p "${PREFIX}/share/dec-apps/installed"

# 2. Copy LICENSE and general docs if present
if [ -f "${SCRIPT_DIR}/LICENSE" ]; then
    cp -a "${SCRIPT_DIR}/LICENSE" "${PREFIX}/"
elif [ -f "${SCRIPT_DIR}/../LICENSE" ]; then
    cp -a "${SCRIPT_DIR}/../LICENSE" "${PREFIX}/"
fi

if [ -f "${SCRIPT_DIR}/README.md" ]; then
    cp -a "${SCRIPT_DIR}/README.md" "${PREFIX}/docs/DISTRIB_README.md"
fi

# 3. Install each requested application
for app in "${VALID_APPS[@]}"; do
    echo "-> Installing application: ${app}..."
    
    # Locate binary
    SRC_BIN=""
    if [ -f "${SCRIPT_DIR}/bin/${app}" ]; then
        SRC_BIN="${SCRIPT_DIR}/bin/${app}"
    elif [ -f "${SCRIPT_DIR}/../apps/${app}/bin/${app}" ]; then
        SRC_BIN="${SCRIPT_DIR}/../apps/${app}/bin/${app}"
    else
        echo "   Building application ${app} from source..."
        make -C "${SCRIPT_DIR}/../apps/${app}" build >/dev/null
        SRC_BIN="${SCRIPT_DIR}/../apps/${app}/bin/${app}"
    fi

    if [ ! -f "${SRC_BIN}" ]; then
        echo "Error: Binary for ${app} could not be located or built."
        exit 1
    fi

    # Copy binary
    cp -a "${SRC_BIN}" "${PREFIX}/bin/${app}"
    chmod 755 "${PREFIX}/bin/${app}"

    # Install documentation
    if [ -f "${SCRIPT_DIR}/docs/${app}.md" ]; then
        cp -a "${SCRIPT_DIR}/docs/${app}.md" "${PREFIX}/docs/"
    elif [ -f "${SCRIPT_DIR}/../apps/${app}/README.md" ]; then
        cp -a "${SCRIPT_DIR}/../apps/${app}/README.md" "${PREFIX}/docs/${app}.md"
    fi

    # Install companion utilities if applicable
    COMPANIONS=()
    if [ "${app}" = "rmsutils" ]; then
        COMPANIONS=("rmsdes" "rmsdef" "rmsifl" "rmscnv" "rmsbck" "rmsrst" "rmsdsp")
    elif [ "${app}" = "datatrieve11" ]; then
        COMPANIONS=("dtr" "dtr11")
    elif [ "${app}" = "decgraph" ]; then
        COMPANIONS=("graph" "decg")
    elif [ "${app}" = "decmail" ]; then
        COMPANIONS=("mail" "decmail11")
    elif [ "${app}" = "decword" ]; then
        COMPANIONS=("decworddp" "wps")
    elif [ "${app}" = "word11" ]; then
        COMPANIONS=("w11")
    elif [ "${app}" = "lex11" ]; then
        COMPANIONS=("lex")
    elif [ "${app}" = "saturnwp" ]; then
        COMPANIONS=("swp")
    elif [ "${app}" = "calc2020" ]; then
        COMPANIONS=("2020" "sc20")
    elif [ "${app}" = "saturncalc" ]; then
        COMPANIONS=("satcalc" "scalc")
    elif [ "${app}" = "nyplan" ]; then
        COMPANIONS=("nyp")
    elif [ "${app}" = "total" ]; then
        COMPANIONS=("totdbm")
    elif [ "${app}" = "ambase" ]; then
        COMPANIONS=("amqry" "amwriter")
    elif [ "${app}" = "accentr" ]; then
        COMPANIONS=("accent" "accr")
    elif [ "${app}" = "saturnbase" ]; then
        COMPANIONS=("satbase" "sbase")
    elif [ "${app}" = "mcba" ]; then
        COMPANIONS=("mcbamrp")
    elif [ "${app}" = "maps" ]; then
        COMPANIONS=("mapsgl")
    elif [ "${app}" = "timeline" ]; then
        COMPANIONS=("digigl")
    elif [ "${app}" = "compushare" ]; then
        COMPANIONS=("cas")
    elif [ "${app}" = "cjbusiness" ]; then
        COMPANIONS=("cjbiz" "cjgl")
    elif [ "${app}" = "kdss" ]; then
        COMPANIONS=("kdfmt" "kdent")
    elif [ "${app}" = "fsort3" ]; then
        COMPANIONS=("vselect")
    elif [ "${app}" = "clyde" ]; then
        COMPANIONS=("contrl" "caudit")
    elif [ "${app}" = "minitab" ]; then
        COMPANIONS=("mtab")
    elif [ "${app}" = "spss11" ]; then
        COMPANIONS=("spss")
    elif [ "${app}" = "wp51" ]; then
        COMPANIONS=("wordperfect" "wp")
    elif [ "${app}" = "interleaf" ]; then
        COMPANIONS=("tps")
    elif [ "${app}" = "lotus123" ]; then
        COMPANIONS=("lotus" "123")
    elif [ "${app}" = "ifps" ]; then
        COMPANIONS=("ifpsplus")
    elif [ "${app}" = "systemw" ]; then
        COMPANIONS=("sysw" "eis")
    elif [ "${app}" = "oracle" ]; then
        COMPANIONS=("sqlplus" "sqlforms" "sqldba")
    elif [ "${app}" = "ingres" ]; then
        COMPANIONS=("iquel" "isql" "abf")
    elif [ "${app}" = "powerhouse" ]; then
        COMPANIONS=("phouse" "quick" "quiz" "qtp")
    elif [ "${app}" = "s1032" ]; then
        COMPANIONS=("sys1032")
    elif [ "${app}" = "manman" ]; then
        COMPANIONS=("askman")
    elif [ "${app}" = "cerner" ]; then
        COMPANIONS=("pathnet")
    elif [ "${app}" = "sas" ]; then
        COMPANIONS=("sasvms")
    elif [ "${app}" = "rs1" ]; then
        COMPANIONS=("bbnrs1")
    elif [ "${app}" = "spice3" ]; then
        COMPANIONS=("spice" "hspice")
    elif [ "${app}" = "gaussian" ]; then
        COMPANIONS=("g90")
    elif [ "${app}" = "diskeeper" ]; then
        COMPANIONS=("defrag")
    elif [ "${app}" = "robomon" ]; then
        COMPANIONS=("robo")
    elif [ "${app}" = "dibs" ]; then
        COMPANIONS=("dibs11" "cts500")
    elif [ "${app}" = "fms11" ]; then
        COMPANIONS=("fms" "fed" "fdv")
    elif [ "${app}" = "menu11" ]; then
        COMPANIONS=("menu" "mcf")
    elif [ "${app}" = "indent" ]; then
        COMPANIONS=("bp2fmt" "pretty")
    elif [ "${app}" = "decwindows" ]; then
        COMPANIONS=("decw_x11" "decwx11" "dxsession" "decterm" "dxterm" "bookreader" "dxbook" "calendar" "dxcalendar" "cardfiler" "dxcardfiler" "cdaviewer" "dxvdoc" "calculator" "dxcalc" "clock" "dxclock" "decsound" "dxsound" "dxmail" "decwinmail" "fileview" "dxfileview" "notepad" "dxnotepad")
        mkdir -p "${PREFIX}/lib" "${PREFIX}/include"
        if [ -d "${SCRIPT_DIR}/lib" ]; then
            cp -a "${SCRIPT_DIR}/lib"/* "${PREFIX}/lib/" 2>/dev/null || true
        elif [ -d "${SCRIPT_DIR}/../apps/${app}/lib" ]; then
            cp -a "${SCRIPT_DIR}/../apps/${app}/lib"/* "${PREFIX}/lib/" 2>/dev/null || true
        fi
        if [ -d "${SCRIPT_DIR}/include" ]; then
            cp -a "${SCRIPT_DIR}/include"/* "${PREFIX}/include/" 2>/dev/null || true
        elif [ -d "${SCRIPT_DIR}/../apps/${app}/include" ]; then
            cp -a "${SCRIPT_DIR}/../apps/${app}/include"/* "${PREFIX}/include/" 2>/dev/null || true
        fi
    fi
    if [ ${#COMPANIONS[@]} -gt 0 ]; then
        for c in "${COMPANIONS[@]}"; do
            C_SRC=""
            if [ -f "${SCRIPT_DIR}/bin/${c}" ]; then
                C_SRC="${SCRIPT_DIR}/bin/${c}"
            elif [ -f "${SCRIPT_DIR}/../apps/${app}/bin/${c}" ]; then
                C_SRC="${SCRIPT_DIR}/../apps/${app}/bin/${c}"
            fi
            if [ -f "${C_SRC}" ]; then
                cp -a "${C_SRC}" "${PREFIX}/bin/${c}"
                chmod 755 "${PREFIX}/bin/${c}"
                if [ "${CREATE_SYMLINKS}" = true ] && [ "${PREFIX}/bin" != "${LINK_BIN}" ]; then
                    mkdir -p "${LINK_BIN}"
                    ln -sf "${PREFIX}/bin/${c}" "${LINK_BIN}/${c}"
                    echo "   Symlinked: ${LINK_BIN}/${c} -> ${PREFIX}/bin/${c}"
                fi
            fi
        done
    fi

    # Record installation receipt
    cat << EOF > "${PREFIX}/share/dec-apps/installed/${app}.txt"
Name=${app}
InstallDate=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
Binary=${PREFIX}/bin/${app}
Docs=${PREFIX}/docs/${app}.md
Companions=${COMPANIONS[*]}
EOF

    # Create global symlink
    if [ "${CREATE_SYMLINKS}" = true ]; then
        mkdir -p "${LINK_BIN}"
        if [ "${PREFIX}/bin" != "${LINK_BIN}" ]; then
            ln -sf "${PREFIX}/bin/${app}" "${LINK_BIN}/${app}"
            echo "   Symlinked: ${LINK_BIN}/${app} -> ${PREFIX}/bin/${app}"
        fi
    fi
done

# 4. Generate environment script dec_apps_env.sh
cat << EOF > "${PREFIX}/bin/dec_apps_env.sh"
# DEC-APPS Application Suite Environment Settings
export DEC_APPS_HOME="${PREFIX}"
export PATH="\${DEC_APPS_HOME}/bin:\${PATH}"
EOF
chmod 644 "${PREFIX}/bin/dec_apps_env.sh"

# 5. Run verification tests
if [ "${RUN_VERIFY}" = true ]; then
    echo "--------------------------------------------------------------------------------"
    echo "-> Running post-installation verification tests..."
    VERIFY_SCRIPT=""
    if [ -f "${SCRIPT_DIR}/verify_kit.sh" ]; then
        VERIFY_SCRIPT="${SCRIPT_DIR}/verify_kit.sh"
    elif [ -f "${SCRIPT_DIR}/../distrib/verify_kit.sh" ]; then
        VERIFY_SCRIPT="${SCRIPT_DIR}/../distrib/verify_kit.sh"
    fi

    if [ -n "${VERIFY_SCRIPT}" ]; then
        DEC_APPS_BIN="${PREFIX}/bin" bash "${VERIFY_SCRIPT}" "${VALID_APPS[@]}"
    else
        echo "Verification script not found; skipping."
    fi
fi

echo "================================================================================"
echo "Installation complete!"
echo ""
echo "Installed applications:"
for app in "${VALID_APPS[@]}"; do
    echo "  - ${PREFIX}/bin/${app}"
done
echo ""
echo "To use DEC-APPS in your current shell, run:"
echo "  source \"${PREFIX}/bin/dec_apps_env.sh\""
echo ""
echo "Or add it to your ~/.bashrc:"
echo "  echo 'source \"${PREFIX}/bin/dec_apps_env.sh\"' >> ~/.bashrc"
echo "================================================================================"
