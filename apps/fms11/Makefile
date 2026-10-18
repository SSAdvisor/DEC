APP := fms11
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
BOBJ := $(BUILD_DIR)/$(APP).bobj
EXE := $(BIN_DIR)/$(APP)
ALIAS_FMS := $(BIN_DIR)/fms
ALIAS_FED := $(BIN_DIR)/fed
ALIAS_FDV := $(BIN_DIR)/fdv

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(BOBJ)
	basiclink $(BOBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_FMS)
	@ln -sf $(APP) $(ALIAS_FED)
	@ln -sf $(APP) $(ALIAS_FDV)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
