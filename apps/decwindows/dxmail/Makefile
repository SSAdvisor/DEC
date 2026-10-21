# Makefile for DECwindows Mail (dxmail / decwinmail)
BASICC := basicc
BASICLINK := basiclink

SRC_DIR := src
BUILD_DIR := build
BIN_DIR := bin

TARGET := $(BIN_DIR)/dxmail
ALIAS := $(BIN_DIR)/decwinmail
OBJ := $(BUILD_DIR)/dxmail.obj
SRC := $(SRC_DIR)/dxmail.bas

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
	@ln -sf dxmail $(ALIAS)

test: build
	pytest

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
