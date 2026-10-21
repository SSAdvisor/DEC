APP := dibs
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
OBJ := $(BUILD_DIR)/$(APP).obj
EXE := $(BIN_DIR)/$(APP)
ALIAS_DIBS11 := $(BIN_DIR)/dibs11
ALIAS_CTS500 := $(BIN_DIR)/cts500

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(OBJ)
	basiclink $(OBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_DIBS11)
	@ln -sf $(APP) $(ALIAS_CTS500)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
