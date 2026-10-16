APP := decgraph
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
BOBJ := $(BUILD_DIR)/$(APP).bobj
EXE := $(BIN_DIR)/$(APP)
ALIAS_GRAPH := $(BIN_DIR)/graph
ALIAS_DECG := $(BIN_DIR)/decg

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(BOBJ)
	basiclink $(BOBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_GRAPH)
	@ln -sf $(APP) $(ALIAS_DECG)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
