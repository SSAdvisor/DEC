# Makefile for DECwindows Notepad (notepad / dxnotepad)
BASICC := basicc
BASICLINK := basiclink

SRC_DIR := src
BUILD_DIR := build
BIN_DIR := bin

TARGET := $(BIN_DIR)/notepad
ALIAS := $(BIN_DIR)/dxnotepad
BOBJ := $(BUILD_DIR)/notepad.bobj
SRC := $(SRC_DIR)/notepad.bas

.PHONY: all build test clean

all: build

build: $(TARGET) $(ALIAS)

$(BOBJ): $(SRC)
	@mkdir -p $(BUILD_DIR)
	$(BASICC) $(SRC) -o $(BOBJ)

$(TARGET): $(BOBJ)
	@mkdir -p $(BIN_DIR)
	$(BASICLINK) $(BOBJ) -o $(TARGET)
	@chmod +x $(TARGET)

$(ALIAS): $(TARGET)
	@ln -sf notepad $(ALIAS)

test: build
	pytest

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
