# ==============================================================================
# DEC VAX FORTRAN V5.5 Compiler Makefile (VAX/VMS V5.5-2)
# ==============================================================================
ROOT_DIR     := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VAXBASIC_BIN := $(abspath $(ROOT_DIR)/../VAX-BASIC/compiler/vaxbasic)
VMSLINK_BIN  := $(abspath $(ROOT_DIR)/../VAX-BASIC/linker/vmslink)

SRC := compiler/vaxfor.bas
OBJ := compiler/vaxfor.obj
EXE := compiler/vaxfor

.PHONY: all build demo test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/vaxfor.py
	chmod +x bootstrap/vaxfor.py
	$(VAXBASIC_BIN) $(SRC) -o $(OBJ)
	$(VMSLINK_BIN) -o $(EXE) $(OBJ)
	@rm -f $(OBJ)

demo: build
	$(EXE) samples/DEMO.FOR -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK_BIN) -o samples/DEMO.EXE samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxfor.py

clean:
	rm -rf $(OBJ) samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .pytest_cache tests/__pycache__ .vms_for_args.tmp
