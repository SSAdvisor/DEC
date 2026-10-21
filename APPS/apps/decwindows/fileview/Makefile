# Makefile for DECwindows FileView (fileview / dxfileview)
BASICC := basicc
BASICLINK := basiclink

SRC_DIR := src
BUILD_DIR := build
BIN_DIR := bin

TARGET := $(BIN_DIR)/fileview
ALIAS := $(BIN_DIR)/dxfileview
OBJ := $(BUILD_DIR)/fileview.obj
SRC := $(SRC_DIR)/fileview.bas

.PHONY: all build test clean

all: build

build: $(TARGET) $(ALIAS)

$(OBJ): $(SRC)
	@mkdir -p $(BUILD_DIR)
	$(BASICC) $(SRC) -o $(OBJ)

$(TARGET): $(OBJ)
	@mkdir -p $(BIN_DIR)
	$(BASICLINK) $(OBJ) -o $(TARGET)
	@chmod +x $(TARGET)

$(ALIAS): $(TARGET)
	@ln -sf fileview $(ALIAS)

test: build
	pytest

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
