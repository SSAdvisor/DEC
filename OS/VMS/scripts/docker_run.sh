#!/bin/bash
# ==============================================================================
# Run DEC VAX/VMS V5.5-2 Docker Container (dec-vms:latest)
# Automatically forwards X11 socket if DISPLAY is set for DECwindows Motif GUIs
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! docker image inspect dec-vms:latest >/dev/null 2>&1; then
    bash "${SCRIPT_DIR}/docker_build.sh"
fi

X11_ARGS=()
if [ -n "${DISPLAY}" ] && [ -d "/tmp/.X11-unix" ]; then
    X11_ARGS=(-e "DISPLAY=${DISPLAY}" -v "/tmp/.X11-unix:/tmp/.X11-unix:rw")
fi

if [ -t 0 ] && [ $# -eq 0 ]; then
    exec docker run --rm -it "${X11_ARGS[@]}" dec-vms:latest
else
    exec docker run --rm -i "${X11_ARGS[@]}" dec-vms:latest "$@"
fi
