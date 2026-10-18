APP := menu11
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
BOBJ := $(BUILD_DIR)/$(APP).bobj
EXE := $(BIN_DIR)/$(APP)
ALIAS_MENU := $(BIN_DIR)/menu
ALIAS_MCF := $(BIN_DIR)/mcf

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(BOBJ)
	basiclink $(BOBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_MENU)
	@ln -sf $(APP) $(ALIAS_MCF)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
