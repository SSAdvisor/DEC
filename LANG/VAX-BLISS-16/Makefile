# ==============================================================================
# DEC VAX BLISS-16 V4.2 16-Bit Compatibility Systems Language Makefile
# ==============================================================================
VAXBASIC_BIN := $(abspath ../VAX-BASIC/compiler/vaxbasic)
VMSLINK_BIN  := $(abspath ../VAX-BASIC/linker/vmslink)

SRC := compiler/bliss16.bas
OBJ := compiler/bliss16.obj
EXE := compiler/bliss16

.PHONY: all build demo test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/bliss16.py
	@chmod +x bootstrap/bliss16.py
	$(VAXBASIC_BIN) $(SRC) -o $(OBJ)
	$(VMSLINK_BIN) -o $(EXE) $(OBJ)
	@rm -f $(OBJ)

demo: build
	$(EXE) samples/DEMO.B16 -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK_BIN) -o samples/DEMO.EXE -m samples/DEMO.MAP --full samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_bliss16.py

clean:
	rm -rf $(OBJ) samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .pytest_cache tests/__pycache__ .vms_bliss16_args.tmp
