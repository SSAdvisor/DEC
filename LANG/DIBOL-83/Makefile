# ==============================================================================
# DEC DIBOL-83 V5.3 Compiler Makefile (CTS-500 / RSTS/E V10.1-L)
# ==============================================================================
BP2_BIN := $(abspath ../BASIC-PLUS-2/compiler/basicc)
BP2_LINK := $(abspath ../BASIC-PLUS-2/linker/basiclink)
BP2_VM := $(abspath ../BASIC-PLUS-2/vm/build/rsts_vm)

SRC := compiler/dibol83.bas
OBJ := compiler/dibol83.obj
EXE := compiler/dibol83

.PHONY: all build test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/dibol83.py
	@chmod +x bootstrap/dibol83.py
	$(BP2_BIN) $(SRC) -o $(OBJ)
	PATH="$(dir $(BP2_VM)):$$PATH" $(BP2_LINK) -o $(EXE) $(OBJ)
	@rm -f compiler/dibol83.bin

test: build
	pytest -v tests/

clean:
	rm -rf $(OBJ) $(EXE) compiler/dibol83.bin .pytest_cache tests/__pycache__
