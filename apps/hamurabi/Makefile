APP_NAME := $(notdir $(CURDIR))
SRC := src/$(APP_NAME).bas
BUILD_DIR := build
BIN_DIR := bin
BOBJ := $(BUILD_DIR)/$(APP_NAME).bobj
EXE := $(BIN_DIR)/$(APP_NAME)

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(BOBJ)
	basiclink $(BOBJ) -o $(EXE)

test: build
	pytest tests/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
