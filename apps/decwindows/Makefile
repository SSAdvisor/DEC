# DECwindows Suite Master Makefile
# Builds and tests all DECwindows sub-projects (decterm, bookreader, calendar,
# cardfiler, cdaviewer, calculator, clock, decsound, dxmail, fileview, notepad)

SUBPROJECTS := decterm bookreader calendar cardfiler cdaviewer calculator clock decsound dxmail fileview notepad
BIN_DIR := bin

.PHONY: all build test clean list

all: build

list:
	@echo "DECwindows Sub-Projects:"
	@for sub in $(SUBPROJECTS); do \
		if [ -f "$$sub/Makefile" ]; then \
			echo "  [x] $$sub (completed)"; \
		else \
			echo "  [ ] $$sub (pending)"; \
		fi \
	done

build:
	@mkdir -p $(BIN_DIR)
	@for sub in $(SUBPROJECTS); do \
		if [ -f "$$sub/Makefile" ]; then \
			echo "  -> Building DECwindows sub-project: $$sub"; \
			$(MAKE) -C "$$sub" build || exit 1; \
			cp -a "$$sub/bin"/* $(BIN_DIR)/; \
		fi \
	done
	@if [ -f "$(BIN_DIR)/decterm" ]; then \
		rm -f $(BIN_DIR)/decwindows && cp -f $(BIN_DIR)/decterm $(BIN_DIR)/decwindows; \
	fi

test: build
	@pytest

clean:
	@for sub in $(SUBPROJECTS); do \
		if [ -f "$$sub/Makefile" ]; then \
			$(MAKE) -C "$$sub" clean || true; \
		fi \
	done
	@rm -rf $(BIN_DIR) build
