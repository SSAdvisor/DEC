# ==============================================================================
# DEC RSTS/E V10.1-L Emulation Makefile
# ==============================================================================
.PHONY: all stage build run login docker-build docker-run test clean

all: stage

stage:
	@bash scripts/stage_runtime.sh

build: stage

run: stage
	@./bin/rsts-emu

login: stage
	@./bin/rsts-emu --boot --login

docker-build:
	@bash scripts/docker_build.sh

docker-run:
	@bash scripts/docker_run.sh

test: stage
	@pytest -v

clean:
	rm -rf system fs .pytest_cache tests/__pycache__
