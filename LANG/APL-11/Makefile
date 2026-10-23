# ==============================================================================
# DEC PDP-11 APL-11 V2.1 Compiler & Workspace Makefile (RSTS/E V10.1-L)
# ==============================================================================
BP2_BIN := $(abspath ../BASIC-PLUS-2/compiler/basicc)
BP2_LINK := $(abspath ../BASIC-PLUS-2/linker/basiclink)
BP2_VM := $(abspath ../BASIC-PLUS-2/vm/build/rsts_vm)

SRC := compiler/apl11.bas
OBJ := compiler/apl11.obj
EXE := compiler/apl11

.PHONY: all build test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/apl11.py
	@chmod +x bootstrap/apl11.py
	$(BP2_BIN) $(SRC) -o $(OBJ)
	PATH="$(dir $(BP2_VM)):$$PATH" $(BP2_LINK) -o $(EXE) $(OBJ)
	@ln -sf apl11 compiler/aplc
	@rm -f compiler/apl11.bin

test: build
	pytest -v tests/

clean:
	rm -rf $(OBJ) $(EXE) compiler/aplc compiler/apl11.bin .pytest_cache tests/__pycache__
