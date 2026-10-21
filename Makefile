# ==============================================================================
# DEC (Digital Equipment Corporation) Unified Ecosystem Master Makefile
# ==============================================================================
# Divisions:
#   - LANG/BASIC-PLUS-2 : Native DEC BASIC-PLUS-2 Compiler, Linker, VM, DCL & EDT
#   - APPS              : 13 Classic DEC Applications & DECwindows Motif X11 Suite
#   - OS/RSTS-E         : DEC RSTS/E V10.1-L PDP-11/70 Operating System Emulation
#   - OS/VMS            : DEC VAX/VMS V5.5-2 VAXstation 4000-90 OS Emulation
# ==============================================================================

.PHONY: all build stage docker-build test test-lang test-apps test-os clean

all: build stage

build:
	@echo "=== Building LANG/BASIC-PLUS-2 Distribution Kit ==="
	bash LANG/BASIC-PLUS-2/distrib/build_kit.sh
	@echo "=== Building APPS Suite ==="
	$(MAKE) -C APPS build

stage:
	@echo "=== Staging OS/RSTS-E and OS/VMS Runtimes ==="
	$(MAKE) -C OS/RSTS-E stage
	$(MAKE) -C OS/VMS stage

docker-build:
	@echo "=== Building OS/RSTS-E and OS/VMS Docker Images ==="
	$(MAKE) -C OS/RSTS-E docker-build
	$(MAKE) -C OS/VMS docker-build

test: test-lang test-apps test-os

test-lang:
	@echo "=== Testing LANG/BASIC-PLUS-2 (55 tests) ==="
	cd LANG/BASIC-PLUS-2 && pytest -v tests/

test-apps:
	@echo "=== Testing APPS (352 tests) ==="
	cd APPS && pytest -v

test-os:
	@echo "=== Testing OS/RSTS-E & OS/VMS (26 tests) ==="
	pytest -v OS/RSTS-E/tests/test_rsts_e.py OS/VMS/tests/test_vms.py

clean:
	$(MAKE) -C APPS clean
	$(MAKE) -C OS/RSTS-E clean
	$(MAKE) -C OS/VMS clean
