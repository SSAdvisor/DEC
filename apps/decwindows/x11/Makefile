# ==============================================================================
# DECwindows X11 / Motif 1.1 Interfacing Library & Session Manager Makefile
# ==============================================================================

CC        = gcc
CFLAGS    = -O2 -Wall -Wextra -fPIC -Iinclude
LDFLAGS   = -lX11 -lm
BASICC    = basicc
BASICLINK = basiclink

SRC_DIR   = src
INC_DIR   = include
BUILD_DIR = build
LIB_DIR   = lib
BIN_DIR   = bin

SHARED_LIB = $(LIB_DIR)/libdecw_x11.so
STATIC_LIB = $(LIB_DIR)/libdecw_x11.a
BRIDGE_BIN = $(BIN_DIR)/decw_x11

BAS_SRC    = $(SRC_DIR)/decwx11.bas
BOBJ       = $(BUILD_DIR)/decwx11.bobj
BAS_BIN    = $(BIN_DIR)/decwx11
ALIAS_BIN  = $(BIN_DIR)/dxsession

.PHONY: all build test run clean

all: build

build: $(SHARED_LIB) $(STATIC_LIB) $(BRIDGE_BIN) $(BAS_BIN) $(ALIAS_BIN)

$(BUILD_DIR)/decw_x11.o: $(SRC_DIR)/decw_x11.c $(INC_DIR)/decw_x11.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(SRC_DIR)/decw_x11.c -o $(BUILD_DIR)/decw_x11.o

$(SHARED_LIB): $(BUILD_DIR)/decw_x11.o
	@mkdir -p $(LIB_DIR)
	$(CC) -shared -o $(SHARED_LIB) $(BUILD_DIR)/decw_x11.o $(LDFLAGS)

$(STATIC_LIB): $(BUILD_DIR)/decw_x11.o
	@mkdir -p $(LIB_DIR)
	ar rcs $(STATIC_LIB) $(BUILD_DIR)/decw_x11.o

$(BRIDGE_BIN): $(SRC_DIR)/decw_x11_main.c $(SHARED_LIB)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/decw_x11_main.c -L$(LIB_DIR) -ldecw_x11 -Wl,-rpath,'$$ORIGIN/../lib' $(LDFLAGS) -o $(BRIDGE_BIN)

$(BOBJ): $(BAS_SRC)
	@mkdir -p $(BUILD_DIR)
	$(BASICC) $(BAS_SRC) -o $(BOBJ)

$(BAS_BIN): $(BOBJ)
	@mkdir -p $(BIN_DIR)
	$(BASICLINK) -o $(BAS_BIN) $(BOBJ)

$(ALIAS_BIN): $(BAS_BIN)
	ln -sf decwx11 $(ALIAS_BIN)

test: build
	pytest -v tests/

run: build
	./$(BAS_BIN)

clean:
	rm -rf $(BUILD_DIR) $(LIB_DIR) $(BIN_DIR) *.tmp_hex
