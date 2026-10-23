# ==============================================================================
# DEC VAX C V3.2 Compiler Makefile (VAX/VMS V5.5-2)
# ==============================================================================
VAXBASIC_BIN := $(abspath ../VAX-BASIC/compiler/vaxbasic)
VMSLINK_BIN  := $(abspath ../VAX-BASIC/linker/vmslink)

SRC := compiler/vaxc.bas
OBJ := compiler/vaxc.obj
EXE := compiler/vaxc

.PHONY: all build demo test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/vaxc.py
	@chmod +x bootstrap/vaxc.py
	$(VAXBASIC_BIN) $(SRC) -o $(OBJ)
	$(VMSLINK_BIN) -o $(EXE) $(OBJ)
	@rm -f $(OBJ)

demo: build
	$(EXE) samples/DEMO.C -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK_BIN) -o samples/DEMO.EXE -m samples/DEMO.MAP --full samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxc.py

clean:
	rm -rf $(OBJ) samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .pytest_cache tests/__pycache__ .vms_vaxc_args.tmp
