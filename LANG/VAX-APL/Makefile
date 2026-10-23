# ==============================================================================
# DEC VAX APL V3.1-00 Compiler & Interactive Workspace Makefile (VAX/VMS)
# ==============================================================================
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VAXBASIC := $(abspath $(ROOT_DIR)/../VAX-BASIC/compiler/vaxbasic)
VMSLINK  := $(abspath $(ROOT_DIR)/../VAX-BASIC/linker/vmslink)
COMP_BIN := $(ROOT_DIR)/compiler/vaxapl

.PHONY: all build demo test clean

all: build

build:
	chmod +x bootstrap/vaxapl.py
	$(VAXBASIC) compiler/vaxapl.bas -o compiler/vaxapl.obj
	$(VMSLINK) -o $(COMP_BIN) compiler/vaxapl.obj
	rm -f compiler/vaxapl.obj

demo: build
	$(COMP_BIN) samples/DEMO.APL -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK) -o samples/DEMO.EXE samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxapl.py

clean:
	rm -f compiler/*.obj samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .vms_apl_args.tmp
