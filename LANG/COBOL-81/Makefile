# ==============================================================================
# DEC PDP-11 COBOL-81 V2.4 Compiler Makefile (RSTS/E V10.1-L)
# ==============================================================================
BP2_BIN := $(abspath ../BASIC-PLUS-2/compiler/basicc)
BP2_LINK := $(abspath ../BASIC-PLUS-2/linker/basiclink)
BP2_VM := $(abspath ../BASIC-PLUS-2/vm/build/rsts_vm)

SRC := compiler/cobol81.bas
OBJ := compiler/cobol81.obj
EXE := compiler/cobol81

.PHONY: all build test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/cobol81.py
	@chmod +x bootstrap/cobol81.py
	$(BP2_BIN) $(SRC) -o $(OBJ)
	PATH="$(dir $(BP2_VM)):$$PATH" $(BP2_LINK) -o $(EXE) $(OBJ)
	@rm -f compiler/cobol81.bin

test: build
	pytest -v tests/

clean:
	rm -rf $(OBJ) $(EXE) compiler/cobol81.bin .pytest_cache tests/__pycache__
