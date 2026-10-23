# ==============================================================================
# DEC VAX DSM V6.0-00 (Digital Standard MUMPS) Makefile (VAX/VMS)
# ==============================================================================
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VAXBASIC := $(abspath $(ROOT_DIR)/../VAX-BASIC/compiler/vaxbasic)
VMSLINK  := $(abspath $(ROOT_DIR)/../VAX-BASIC/linker/vmslink)
COMP_BIN := $(ROOT_DIR)/compiler/vaxdsm

.PHONY: all build demo test clean

all: build

build:
	chmod +x bootstrap/vaxdsm.py
	$(VAXBASIC) compiler/vaxdsm.bas -o compiler/vaxdsm.obj
	$(VMSLINK) -o $(COMP_BIN) compiler/vaxdsm.obj
	rm -f compiler/vaxdsm.obj

demo: build
	$(COMP_BIN) samples/DEMO.DSM -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK) -o samples/DEMO.EXE samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxdsm.py

clean:
	rm -f compiler/*.obj samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .vms_dsm_args.tmp
