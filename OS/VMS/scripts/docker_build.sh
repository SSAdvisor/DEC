#!/bin/bash
# ==============================================================================
# Build DEC VAX/VMS V5.5-2 Docker Image (dec-vms:latest)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VMS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

bash "${SCRIPT_DIR}/stage_runtime.sh"
echo "Building Docker image dec-vms:latest..."
docker build -t dec-vms:latest "${VMS_ROOT}"
echo "Docker image dec-vms:latest built successfully."
