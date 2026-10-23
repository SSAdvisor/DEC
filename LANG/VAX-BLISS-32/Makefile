# ==============================================================================
# DEC VAX BLISS-32 V4.7 Systems Implementation Language Makefile
# ==============================================================================
VAXBASIC_BIN := $(abspath ../VAX-BASIC/compiler/vaxbasic)
VMSLINK_BIN  := $(abspath ../VAX-BASIC/linker/vmslink)

SRC := compiler/bliss32.bas
OBJ := compiler/bliss32.obj
EXE := compiler/bliss32

.PHONY: all build demo test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/bliss32.py
	@chmod +x bootstrap/bliss32.py
	$(VAXBASIC_BIN) $(SRC) -o $(OBJ)
	$(VMSLINK_BIN) -o $(EXE) $(OBJ)
	@rm -f $(OBJ)

demo: build
	$(EXE) samples/DEMO.B32 -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK_BIN) -o samples/DEMO.EXE -m samples/DEMO.MAP --full samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_bliss32.py

clean:
	rm -rf $(OBJ) samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .pytest_cache tests/__pycache__ .vms_bliss32_args.tmp
