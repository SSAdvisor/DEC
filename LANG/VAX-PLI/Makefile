# ==============================================================================
# DEC VAX PL/I V3.5 Compiler Makefile (OpenVMS VAX V5.5-2)
# ==============================================================================
ROOT_DIR     := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VAXBASIC_DIR := $(abspath $(ROOT_DIR)/../VAX-BASIC)
VAXBASIC_BIN := $(VAXBASIC_DIR)/compiler/vaxbasic
VMSLINK_BIN  := $(VAXBASIC_DIR)/linker/vmslink
COMP_BIN     := $(ROOT_DIR)/compiler/vaxpli

.PHONY: all build demo test clean

all: build

build:
	chmod +x bootstrap/vaxpli.py
	$(VAXBASIC_BIN) compiler/vaxpli.bas -o compiler/vaxpli.obj
	$(VMSLINK_BIN) -o $(COMP_BIN) compiler/vaxpli.obj
	rm -f compiler/vaxpli.obj

demo: build
	$(COMP_BIN) samples/DEMO.PLI -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK_BIN) -o samples/DEMO.EXE -m samples/DEMO.MAP --full samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxpli.py

clean:
	rm -f compiler/*.obj samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .vms_pli_args.tmp
