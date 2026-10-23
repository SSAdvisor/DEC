# ==============================================================================
# DEC PDP-11 RPG II V2.1 Compiler Makefile (RSTS/E V10.1-L)
# ==============================================================================
BP2_BIN := $(abspath ../BASIC-PLUS-2/compiler/basicc)
BP2_LINK := $(abspath ../BASIC-PLUS-2/linker/basiclink)
BP2_VM := $(abspath ../BASIC-PLUS-2/vm/build/rsts_vm)

SRC := compiler/rpgii.bas
OBJ := compiler/rpgii.obj
EXE := compiler/rpgii

.PHONY: all build test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/rpgii.py
	@chmod +x bootstrap/rpgii.py
	$(BP2_BIN) $(SRC) -o $(OBJ)
	PATH="$(dir $(BP2_VM)):$$PATH" $(BP2_LINK) -o $(EXE) $(OBJ)
	@rm -f compiler/rpgii.bin

test: build
	pytest -v tests/

clean:
	rm -rf $(OBJ) $(EXE) compiler/rpgii.bin .pytest_cache tests/__pycache__
