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
                    rmsdes|rmsdef|rmsifl|rmscnv|rmsbck|rmsrst|rmsdsp|dtr|dtr11|graph|decg|mail|decmail11|decworddp|wps|dibs11|cts500)
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
        if [ -d "$d" ] && [ -f "$d/src/$(basename "$d").bas" ]; then
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
    elif [ "${app}" = "dibs" ]; then
        COMPANIONS=("dibs11" "cts500")
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
