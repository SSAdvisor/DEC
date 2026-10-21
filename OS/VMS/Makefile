# ==============================================================================
# DEC VAX/VMS V5.5-2 Emulation Makefile
# ==============================================================================
.PHONY: all stage build run login docker-build docker-run test clean

all: stage

stage:
	@bash scripts/stage_runtime.sh

build: stage

run: stage
	@./bin/vms-emu

login: stage
	@./bin/vms-emu --boot --login

docker-build:
	@bash scripts/docker_build.sh

docker-run:
	@bash scripts/docker_run.sh

test: stage
	@pytest -v

clean:
	rm -rf system fs .pytest_cache tests/__pycache__
