# ==============================================================================
# DEC VAX OPS5 V2.2-00 Rule-Based Production System Makefile (VAX/VMS)
# ==============================================================================
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VAXBASIC := $(abspath $(ROOT_DIR)/../VAX-BASIC/compiler/vaxbasic)
VMSLINK  := $(abspath $(ROOT_DIR)/../VAX-BASIC/linker/vmslink)
COMP_BIN := $(ROOT_DIR)/compiler/vaxops5

.PHONY: all build demo test clean

all: build

build:
	chmod +x bootstrap/vaxops5.py
	$(VAXBASIC) compiler/vaxops5.bas -o compiler/vaxops5.obj
	$(VMSLINK) -o $(COMP_BIN) compiler/vaxops5.obj
	rm -f compiler/vaxops5.obj

demo: build
	$(COMP_BIN) samples/DEMO.OPS -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK) -o samples/DEMO.EXE samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxops5.py

clean:
	rm -f compiler/*.obj samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .vms_ops5_args.tmp
