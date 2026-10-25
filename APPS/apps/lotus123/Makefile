APP := lotus123
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
OBJ := $(BUILD_DIR)/$(APP).obj
EXE := $(BIN_DIR)/$(APP)
ALIAS_LOTUS := $(BIN_DIR)/lotus
ALIAS_123 := $(BIN_DIR)/123

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(OBJ)
	basiclink $(OBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_LOTUS)
	@ln -sf $(APP) $(ALIAS_123)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
