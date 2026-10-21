APP_NAME := $(notdir $(CURDIR))
SRC := src/$(APP_NAME).bas
BUILD_DIR := build
BIN_DIR := bin
OBJ := $(BUILD_DIR)/$(APP_NAME).obj
EXE := $(BIN_DIR)/$(APP_NAME)

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(OBJ)
	basiclink $(OBJ) -o $(EXE)

test: build
	pytest tests/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
