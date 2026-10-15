UTILS := rmsdes rmsdef rmsifl rmscnv rmsbck rmsrst rmsdsp rmsutils

BUILD_DIR := build
BIN_DIR := bin

EXES := $(patsubst %,$(BIN_DIR)/%,$(UTILS))

.PHONY: all build test run clean

all: build

build: $(EXES)

$(BIN_DIR)/%: src/%.bas
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $< -o $(BUILD_DIR)/$*.bobj
	basiclink $(BUILD_DIR)/$*.bobj -o $@

test: build
	pytest tests/

run: build
	./$(BIN_DIR)/rmsutils

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
