# ==============================================================================
# DEC VAX BASIC V3.5 & OpenVMS VAX Linker V05-05 Makefile
# ==============================================================================
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VM_BUILD := $(ROOT_DIR)/vm/build
VMS_VM   := $(VM_BUILD)/vms_vm
COMP_BIN := $(ROOT_DIR)/compiler/vaxbasic
LINK_BIN := $(ROOT_DIR)/linker/vmslink

.PHONY: all vm build demo test clean

all: build

vm:
	mkdir -p $(VM_BUILD)
	cd $(VM_BUILD) && cmake .. && $(MAKE) -j4

build: vm
	chmod +x bootstrap/vaxbasic.py bootstrap/vmslink.py
	python3 bootstrap/vaxbasic.py compiler/vaxbasic.bas -o compiler/vaxbasic.obj
	python3 bootstrap/vmslink.py -o $(COMP_BIN) compiler/vaxbasic.obj
	python3 bootstrap/vaxbasic.py linker/vmslink.bas -o linker/vmslink.obj
	python3 bootstrap/vmslink.py -o $(LINK_BIN) linker/vmslink.obj

demo: build
	$(COMP_BIN) samples/VAXDEMO.BAS -o samples/VAXDEMO.OBJ -l samples/VAXDEMO.LST
	$(LINK_BIN) -o samples/VAXDEMO.EXE -m samples/VAXDEMO.MAP --full samples/VAXDEMO.OBJ samples/VAXDEMO.OPT
	./samples/VAXDEMO.EXE

test: build
	pytest -v tests/test_vaxbasic_and_vmslink.py

clean:
	rm -f compiler/vaxbasic compiler/*.obj linker/vmslink linker/*.obj samples/*.OBJ samples/*.EXE samples/*.LST samples/*.MAP
