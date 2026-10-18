#!/bin/bash
# ==============================================================================
# DEC-APPS Application Suite Uninstaller
# Digital Equipment Corporation / DEC-APPS Project
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$(id -u)" -eq 0 ]; then
    DEFAULT_PREFIX="/usr/local/dec-apps"
    DEFAULT_BIN_DIR="/usr/local/bin"
else
    DEFAULT_PREFIX="${HOME}/.local/dec-apps"
    DEFAULT_BIN_DIR="${HOME}/.local/bin"
fi

PREFIX="${DEFAULT_PREFIX}"
LINK_BIN="${DEFAULT_BIN_DIR}"
SELECTED_APPS=()

show_help() {
    cat << EOF
Usage: ./uninstall.sh [OPTIONS] [APP...]

Uninstall Digital Equipment Corporation (DEC) applications individually or all at once.

Arguments:
  APP                       Name of application(s) to uninstall (e.g. 'sort11', 'hamurabi').
                            If omitted or set to 'all', all installed DEC applications will be uninstalled.

Options:
  --prefix=<dir>, -p <dir>  Target installation directory (default: ${DEFAULT_PREFIX})
  --symlink-dir=<dir>       Directory for global symlinks (default: ${DEFAULT_BIN_DIR})
  --app=<name>              Specify an application to uninstall
  --help, -h                Show this help message
EOF
    exit 0
}

# Parse options
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
                SELECTED_APPS=()
            else
                SELECTED_APPS+=("$1")
            fi
            shift
            ;;
    esac
done

echo "================================================================================"
echo "    DEC-APPS Application Suite Uninstaller"
echo "================================================================================"
echo "Target Prefix: ${PREFIX}"

if [ ! -d "${PREFIX}" ]; then
    echo "Installation directory not found: ${PREFIX}"
    exit 0
fi

# Discover installed applications if none specified
if [ ${#SELECTED_APPS[@]} -eq 0 ]; then
    if [ -d "${PREFIX}/share/dec-apps/installed" ]; then
        for f in "${PREFIX}/share/dec-apps/installed"/*.txt; do
            if [ -f "$f" ]; then
                b="$(basename "$f" .txt)"
                SELECTED_APPS+=("$b")
            fi
        done
    fi

    # Fallback scan of bin directory
    if [ ${#SELECTED_APPS[@]} -eq 0 ] && [ -d "${PREFIX}/bin" ]; then
        for f in "${PREFIX}/bin"/*; do
            if [ -x "$f" ]; then
                bname="$(basename "$f")"
                if [[ "$bname" != *.sh ]]; then
                    SELECTED_APPS+=("$bname")
                fi
            fi
        done
    fi
fi

if [ ${#SELECTED_APPS[@]} -eq 0 ]; then
    echo "No installed DEC applications found to remove."
    exit 0
fi

echo "Removing application(s): ${SELECTED_APPS[*]}"
echo "--------------------------------------------------------------------------------"

for app in "${SELECTED_APPS[@]}"; do
    echo "-> Uninstalling ${app}..."
    
    # Check for companion utilities
    COMPANIONS=()
    if [ -f "${PREFIX}/share/dec-apps/installed/${app}.txt" ]; then
        COMP_LINE="$(grep '^Companions=' "${PREFIX}/share/dec-apps/installed/${app}.txt" || true)"
        if [ -n "${COMP_LINE}" ]; then
            COMPANIONS=(${COMP_LINE#Companions=})
        fi
    elif [ "$app" = "rmsutils" ]; then
        COMPANIONS=("rmsdes" "rmsdef" "rmsifl" "rmscnv" "rmsbck" "rmsrst" "rmsdsp")
    elif [ "$app" = "datatrieve11" ]; then
        COMPANIONS=("dtr" "dtr11")
    elif [ "$app" = "decgraph" ]; then
        COMPANIONS=("graph" "decg")
    elif [ "$app" = "decmail" ]; then
        COMPANIONS=("mail" "decmail11")
    elif [ "$app" = "decword" ]; then
        COMPANIONS=("decworddp" "wps")
    elif [ "$app" = "dibs" ]; then
        COMPANIONS=("dibs11" "cts500")
    elif [ "$app" = "fms11" ]; then
        COMPANIONS=("fms" "fed" "fdv")
    elif [ "$app" = "menu11" ]; then
        COMPANIONS=("menu" "mcf")
    fi

    # 1. Remove symlink
    if [ -L "${LINK_BIN}/${app}" ]; then
        TARGET="$(readlink "${LINK_BIN}/${app}" || true)"
        if [[ "${TARGET}" == *"${PREFIX}"* ]]; then
            rm -f "${LINK_BIN}/${app}"
            echo "   Removed symlink ${LINK_BIN}/${app}"
        fi
    fi

    # 2. Remove companion symlinks
    for c in "${COMPANIONS[@]}"; do
        if [ -L "${LINK_BIN}/${c}" ]; then
            TARGET="$(readlink "${LINK_BIN}/${c}" || true)"
            if [[ "${TARGET}" == *"${PREFIX}"* ]]; then
                rm -f "${LINK_BIN}/${c}"
                echo "   Removed companion symlink ${LINK_BIN}/${c}"
            fi
        fi
    done

    # 3. Remove binary
    if [ -f "${PREFIX}/bin/${app}" ] || [ -L "${PREFIX}/bin/${app}" ]; then
        rm -f "${PREFIX}/bin/${app}"
        echo "   Removed binary ${PREFIX}/bin/${app}"
    fi

    # 4. Remove companion binaries
    for c in "${COMPANIONS[@]}"; do
        if [ -f "${PREFIX}/bin/${c}" ] || [ -L "${PREFIX}/bin/${c}" ]; then
            rm -f "${PREFIX}/bin/${c}"
            echo "   Removed companion binary ${PREFIX}/bin/${c}"
        fi
    done

    # 5. Remove docs
    if [ -f "${PREFIX}/docs/${app}.md" ]; then
        rm -f "${PREFIX}/docs/${app}.md"
        echo "   Removed documentation ${PREFIX}/docs/${app}.md"
    fi

    # 6. Remove receipt
    if [ -f "${PREFIX}/share/dec-apps/installed/${app}.txt" ]; then
        rm -f "${PREFIX}/share/dec-apps/installed/${app}.txt"
    fi
done

# Check if any applications remain
REMAINING=0
if [ -d "${PREFIX}/share/dec-apps/installed" ]; then
    REMAINING=$(find "${PREFIX}/share/dec-apps/installed" -type f -name "*.txt" | wc -l)
fi

if [ "$REMAINING" -eq 0 ]; then
    echo "-> No remaining DEC applications in ${PREFIX}. Cleaning environment script..."
    rm -f "${PREFIX}/bin/dec_apps_env.sh"
    rm -f "${PREFIX}/LICENSE"
    rm -f "${PREFIX}/docs/DISTRIB_README.md"
    
    # Clean up empty directories
    rmdir "${PREFIX}/share/dec-apps/installed" 2>/dev/null || true
    rmdir "${PREFIX}/share/dec-apps" 2>/dev/null || true
    rmdir "${PREFIX}/share" 2>/dev/null || true
    rmdir "${PREFIX}/bin" 2>/dev/null || true
    rmdir "${PREFIX}/docs" 2>/dev/null || true

    if [ "${PREFIX}" != "${HOME}" ] && [ "${PREFIX}" != "${HOME}/.local" ] && [ "${PREFIX}" != "/usr" ] && [ "${PREFIX}" != "/usr/local" ]; then
        rmdir "${PREFIX}" 2>/dev/null || true
        echo "   Removed empty directory ${PREFIX}"
    fi
fi

echo "================================================================================"
echo "Uninstallation complete."
echo "================================================================================"
