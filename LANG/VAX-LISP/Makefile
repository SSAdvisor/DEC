# ==============================================================================
# DEC VAX LISP V3.1-00 Common Lisp Compiler & REPL Makefile (VAX/VMS)
# ==============================================================================
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VAXBASIC := $(abspath $(ROOT_DIR)/../VAX-BASIC/compiler/vaxbasic)
VMSLINK  := $(abspath $(ROOT_DIR)/../VAX-BASIC/linker/vmslink)
COMP_BIN := $(ROOT_DIR)/compiler/vaxlisp

.PHONY: all build demo test clean

all: build

build:
	chmod +x bootstrap/vaxlisp.py
	$(VAXBASIC) compiler/vaxlisp.bas -o compiler/vaxlisp.obj
	$(VMSLINK) -o $(COMP_BIN) compiler/vaxlisp.obj
	rm -f compiler/vaxlisp.obj

demo: build
	$(COMP_BIN) samples/DEMO.LSP -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK) -o samples/DEMO.EXE samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxlisp.py

clean:
	rm -f compiler/*.obj samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .vms_lisp_args.tmp
