#!/bin/bash
# ==============================================================================
# Build DEC VAX/VMS V5.5-2 Docker Image (dec-vms:latest)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VMS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

bash "${SCRIPT_DIR}/stage_runtime.sh"
docker network inspect dec-cluster-net >/dev/null 2>&1 || docker network create dec-cluster-net >/dev/null 2>&1 || true
echo "Building Docker image dec-vms:latest and dec-vms:5.5-2..."
docker build -t dec-vms:latest -t dec-vms:5.5-2 "${VMS_ROOT}"
echo "Docker image dec-vms:latest (and dec-vms:5.5-2) built successfully."
