#!/bin/bash
# ==============================================================================
# Run DEC RSTS/E V10.1-L Docker Container (dec-rsts-e:latest)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! docker image inspect dec-rsts-e:latest >/dev/null 2>&1; then
    bash "${SCRIPT_DIR}/docker_build.sh"
fi

if [ -t 0 ] && [ $# -eq 0 ]; then
    exec docker run --rm -it dec-rsts-e:latest
else
    exec docker run --rm -i dec-rsts-e:latest "$@"
fi
