# ==============================================================================
# DEC VAX SCAN V1.2-00 String Scanning & Pattern-Matching Makefile (VAX/VMS)
# ==============================================================================
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VAXBASIC := $(abspath $(ROOT_DIR)/../VAX-BASIC/compiler/vaxbasic)
VMSLINK  := $(abspath $(ROOT_DIR)/../VAX-BASIC/linker/vmslink)
COMP_BIN := $(ROOT_DIR)/compiler/vaxscan

.PHONY: all build demo test clean

all: build

build:
	chmod +x bootstrap/vaxscan.py
	$(VAXBASIC) compiler/vaxscan.bas -o compiler/vaxscan.obj
	$(VMSLINK) -o $(COMP_BIN) compiler/vaxscan.obj
	rm -f compiler/vaxscan.obj

demo: build
	$(COMP_BIN) samples/DEMO.SCN -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK) -o samples/DEMO.EXE samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxscan.py

clean:
	rm -f compiler/*.obj samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .vms_scan_args.tmp
