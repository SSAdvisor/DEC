# DEC-APPS Root Makefile
# Discovers all sub-projects in apps/ and provides project-wide targets.

APPS_DIR := apps
SUBDIRS := $(wildcard $(APPS_DIR)/*)

.PHONY: all build test clean help $(SUBDIRS)

all: build

help:
	@echo "DEC-APPS Master Build System"
	@echo "----------------------------"
	@echo "Available targets:"
	@echo "  make build  - Compile and link all sub-projects"
	@echo "  make test   - Run test suites for all sub-projects (via pytest)"
	@echo "  make clean  - Clean build artifacts across all sub-projects"
	@echo "  make list   - List all registered sub-projects"

list:
	@echo "Registered sub-projects:"
	@for dir in $(SUBDIRS); do \
		if [ -d "$$dir" ]; then \
			echo "  - $$(basename $$dir)"; \
		fi \
	done

build:
	@for dir in $(SUBDIRS); do \
		if [ -f "$$dir/Makefile" ]; then \
			echo "=== Building $$dir ==="; \
			$(MAKE) -C "$$dir" build || exit 1; \
		fi \
	done

test:
	@pytest

clean:
	@for dir in $(SUBDIRS); do \
		if [ -f "$$dir/Makefile" ]; then \
			echo "=== Cleaning $$dir ==="; \
			$(MAKE) -C "$$dir" clean || true; \
		fi \
	done
