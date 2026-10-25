APP := powerhouse
BUILD_DIR := build
BIN_DIR := bin
SRC_DIR := src
TESTS_DIR := tests

SRC := $(SRC_DIR)/$(APP).bas
OBJ := $(BUILD_DIR)/$(APP).obj
EXE := $(BIN_DIR)/$(APP)
ALIAS_PHOUSE := $(BIN_DIR)/phouse
ALIAS_QUICK := $(BIN_DIR)/quick
ALIAS_QUIZ := $(BIN_DIR)/quiz
ALIAS_QTP := $(BIN_DIR)/qtp

.PHONY: all build test run clean

all: build

build: $(EXE)

$(EXE): $(SRC)
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)
	basicc $(SRC) -o $(OBJ)
	basiclink $(OBJ) -o $(EXE)
	@ln -sf $(APP) $(ALIAS_PHOUSE)
	@ln -sf $(APP) $(ALIAS_QUICK)
	@ln -sf $(APP) $(ALIAS_QUIZ)
	@ln -sf $(APP) $(ALIAS_QTP)

test: build
	pytest $(TESTS_DIR)/

run: build
	./$(EXE)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
