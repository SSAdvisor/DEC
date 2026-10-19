# Makefile for DECwindows Mail (dxmail / decwinmail)
BASICC := basicc
BASICLINK := basiclink

SRC_DIR := src
BUILD_DIR := build
BIN_DIR := bin

TARGET := $(BIN_DIR)/dxmail
ALIAS := $(BIN_DIR)/decwinmail
BOBJ := $(BUILD_DIR)/dxmail.bobj
SRC := $(SRC_DIR)/dxmail.bas

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
	@ln -sf dxmail $(ALIAS)

test: build
	pytest

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
