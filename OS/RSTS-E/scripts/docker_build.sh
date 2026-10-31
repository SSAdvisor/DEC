#!/bin/bash
# ==============================================================================
# Build DEC RSTS/E V10.1-L Docker Image (dec-rsts-e:latest)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RSTS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

bash "${SCRIPT_DIR}/stage_runtime.sh"
docker network inspect dec-cluster-net >/dev/null 2>&1 || docker network create dec-cluster-net >/dev/null 2>&1 || true
echo "Building Docker image dec-rsts-e:latest and dec-rsts-e:10.1-l..."
docker build -t dec-rsts-e:latest -t dec-rsts-e:10.1-l "${RSTS_ROOT}"
echo "Docker image dec-rsts-e:latest (and dec-rsts-e:10.1-l) built successfully."
