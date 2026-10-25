APP := oracle
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
OBJ := $(BUILD_DIR)/$(APP).obj
EXE := $(BIN_DIR)/$(APP)
ALIAS_SQLPLUS := $(BIN_DIR)/sqlplus
ALIAS_SQLFORMS := $(BIN_DIR)/sqlforms
ALIAS_SQLDBA := $(BIN_DIR)/sqldba

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(OBJ)
	basiclink $(OBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_SQLPLUS)
	@ln -sf $(APP) $(ALIAS_SQLFORMS)
	@ln -sf $(APP) $(ALIAS_SQLDBA)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
