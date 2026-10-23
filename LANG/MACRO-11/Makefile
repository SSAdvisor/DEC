# ==============================================================================
# DEC MACRO-11 V05.05 Assembler Makefile (PDP-11 / RSTS/E V10.1-L)
# ==============================================================================
BP2_BIN := $(abspath ../BASIC-PLUS-2/compiler/basicc)
BP2_LINK := $(abspath ../BASIC-PLUS-2/linker/basiclink)
BP2_VM := $(abspath ../BASIC-PLUS-2/vm/build/rsts_vm)

SRC := compiler/macro11.bas
OBJ := compiler/macro11.obj
EXE := compiler/macro11

.PHONY: all build test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/macro11.py
	@chmod +x bootstrap/macro11.py
	$(BP2_BIN) $(SRC) -o $(OBJ)
	PATH="$(dir $(BP2_VM)):$$PATH" $(BP2_LINK) -o $(EXE) $(OBJ)
	@rm -f compiler/macro11.bin

test: build
	pytest -v tests/

clean:
	rm -rf $(OBJ) $(EXE) compiler/macro11.bin .pytest_cache tests/__pycache__
