APP := indent
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
OBJ := $(BUILD_DIR)/$(APP).obj
EXE := $(BIN_DIR)/$(APP)
ALIAS_BP2FMT := $(BIN_DIR)/bp2fmt
ALIAS_PRETTY := $(BIN_DIR)/pretty

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(OBJ)
	basiclink $(OBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_BP2FMT)
	@ln -sf $(APP) $(ALIAS_PRETTY)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
