# ==============================================================================
# DEC PDP-11 FORTRAN-77 V5.0 Compiler Makefile (RSTS/E V10.1-L)
# ==============================================================================
BP2_BIN := $(abspath ../BASIC-PLUS-2/compiler/basicc)
BP2_LINK := $(abspath ../BASIC-PLUS-2/linker/basiclink)
BP2_VM := $(abspath ../BASIC-PLUS-2/vm/build/rsts_vm)

SRC := compiler/fortran77.bas
OBJ := compiler/fortran77.obj
EXE := compiler/fortran77

.PHONY: all build test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/fortran77.py
	@chmod +x bootstrap/fortran77.py
	$(BP2_BIN) $(SRC) -o $(OBJ)
	PATH="$(dir $(BP2_VM)):$$PATH" $(BP2_LINK) -o $(EXE) $(OBJ)
	@rm -f compiler/fortran77.bin

test: build
	pytest -v tests/

clean:
	rm -rf $(OBJ) $(EXE) compiler/fortran77.bin .pytest_cache tests/__pycache__
