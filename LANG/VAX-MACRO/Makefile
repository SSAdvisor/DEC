# ==============================================================================
# DEC VAX MACRO V05-00 Macro Assembler Makefile (VAX/VMS V5.5-2)
# ==============================================================================
VAXBASIC_BIN := $(abspath ../VAX-BASIC/compiler/vaxbasic)
VMSLINK_BIN  := $(abspath ../VAX-BASIC/linker/vmslink)

SRC := compiler/vaxmacro.bas
OBJ := compiler/vaxmacro.obj
EXE := compiler/vaxmacro

.PHONY: all build demo test clean

all: build

build: $(EXE)

$(EXE): $(SRC) bootstrap/vaxmacro.py
	@chmod +x bootstrap/vaxmacro.py
	$(VAXBASIC_BIN) $(SRC) -o $(OBJ)
	$(VMSLINK_BIN) -o $(EXE) $(OBJ)
	@rm -f $(OBJ)

demo: build
	$(EXE) samples/DEMO.MAR -o samples/DEMO.OBJ -l samples/DEMO.LST
	$(VMSLINK_BIN) -o samples/DEMO.EXE -m samples/DEMO.MAP --full samples/DEMO.OBJ
	./samples/DEMO.EXE

test: build
	pytest -v tests/test_vaxmacro.py

clean:
	rm -rf $(OBJ) samples/*.OBJ samples/*.LST samples/*.MAP samples/*.EXE .pytest_cache tests/__pycache__ .vms_macro_args.tmp
