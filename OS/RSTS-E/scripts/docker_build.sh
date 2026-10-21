#!/bin/bash
# ==============================================================================
# Build DEC RSTS/E V10.1-L Docker Image (dec-rsts-e:latest)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RSTS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

bash "${SCRIPT_DIR}/stage_runtime.sh"
echo "Building Docker image dec-rsts-e:latest..."
docker build -t dec-rsts-e:latest "${RSTS_ROOT}"
echo "Docker image dec-rsts-e:latest built successfully."
