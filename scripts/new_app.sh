#!/usr/bin/env bash
# Helper script to scaffold a new DEC application sub-project
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <app-name>"
    exit 1
fi

APP_NAME="$1"
APP_DIR="apps/${APP_NAME}"

if [ -d "$APP_DIR" ]; then
    echo "Error: Directory ${APP_DIR} already exists."
    exit 1
fi

echo "Scaffolding sub-project ${APP_NAME} in ${APP_DIR}..."

mkdir -p "${APP_DIR}/src"
mkdir -p "${APP_DIR}/tests"

# 1. Makefile
cat << 'EOF' > "${APP_DIR}/Makefile"
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
EOF

# 2. Sample BASIC source
cat << EOF > "${APP_DIR}/src/${APP_NAME}.bas"
10 ! ${APP_NAME}.BAS - DEC System Application
20 PRINT "${APP_NAME} - DEC BASIC-PLUS-2"
30 END
EOF

# 3. Dedicated pytest test suite
cat << EOF > "${APP_DIR}/tests/test_${APP_NAME}.py"
import os
import subprocess

CUR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(CUR_DIR, "src", "${APP_NAME}.bas")
BIN_FILE = os.path.join(CUR_DIR, "bin", "${APP_NAME}")

def test_build():
    res = subprocess.run(["make", "-C", CUR_DIR, "build"], capture_output=True, text=True)
    assert res.returncode == 0, f"Build failed: {res.stderr}\n{res.stdout}"
    assert os.path.isfile(BIN_FILE), f"Binary {BIN_FILE} was not produced"
    assert os.access(BIN_FILE, os.X_OK), f"Binary {BIN_FILE} is not executable"

def test_run():
    res = subprocess.run([BIN_FILE], capture_output=True, text=True)
    assert res.returncode == 0, f"Execution failed: {res.stderr}\n{res.stdout}"
    assert "${APP_NAME}" in res.stdout
EOF

touch "${APP_DIR}/tests/__init__.py"

# 4. README.md
cat << EOF > "${APP_DIR}/README.md"
# ${APP_NAME}

## Origin & DEC Heritage
- **System**: DEC PDP-11 / RSTS/E
- **Dialect**: BASIC-PLUS-2

## Building & Running
To compile and link:
\`\`\`bash
make build
\`\`\`

To run:
\`\`\`bash
make run
\`\`\`

To test:
\`\`\`bash
make test
\`\`\`
EOF

echo "Created sub-project ${APP_NAME} successfully!"
