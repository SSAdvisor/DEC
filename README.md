# DEC-APPS

A curated repository of classic applications distributed by Digital Equipment Corporation (DEC) or written by third parties for DEC systems (such as PDP-11, VAX, and DECsystem-10/20), reimplemented and preserved using the native **BASIC-PLUS-2** dialect.

All applications in this repository are compiled and linked using the native Linux DEC BASIC-PLUS-2 toolchain:
- **`basicc`**: Native DEC BASIC-PLUS-2 compiler (generates `.bobj` bytecode modules)
- **`basiclink`**: Native DEC BASIC-PLUS-2 linker (links modules into native Linux executables)

---

## Repository Structure

Every application in this project is maintained as an independent sub-project under the `apps/` directory, complete with its own source code, build scripts, documentation, and dedicated test suite.

```
DEC-APPS/
├── Makefile                    # Root Makefile to build/test all sub-projects
├── pytest.ini                  # Root pytest configuration for test discovery
├── .gitignore                  # Git ignore rules for build and runtime artifacts
├── README.md                   # This file
└── apps/                       # Sub-project applications
    └── <app-name>/
        ├── README.md           # Application history, DEC heritage, and usage
        ├── Makefile            # Sub-project build, test, run, and clean targets
        ├── src/                # BASIC-PLUS-2 source code (*.bas, *.odl)
        │   └── <app-name>.bas
        └── tests/              # Sub-project test suite
            ├── __init__.py
            └── test_<app-name>.py
```

---

## Sub-Project Standards

Each sub-project must adhere to the following standards:

1. **Sub-Project Directory**: Placed inside `apps/<app-name>/`.
2. **BASIC-PLUS-2 Source**: Placed in `apps/<app-name>/src/`. Line numbers or structured labels conforming to DEC BASIC-PLUS-2 syntax.
3. **Build Target**: A standard `Makefile` providing:
   - `make build` (or `make all`): Compiles with `basicc` to `build/<app>.bobj` and links with `basiclink` to `bin/<app>`.
   - `make test`: Runs the sub-project's dedicated test suite.
   - `make run`: Runs the compiled executable.
   - `make clean`: Removes intermediate and binary artifacts.
4. **Dedicated Test Suite**: Placed in `apps/<app-name>/tests/`, containing automated tests (using `pytest` or standalone test scripts) that verify:
   - Source code compiles with `basicc` without errors.
   - Object files link cleanly with `basiclink`.
   - Executable runs as expected, testing key input/output scenarios.
5. **Documentation**: A `README.md` in the sub-project directory documenting:
   - Historical background and provenance (e.g. DECUS tape ID, DEC Software Distribution Center, David Ahl's *101 BASIC Computer Games*, RSTS/E release version).
   - Instructions for building, running, and playing/using the application.

---

## Quick Start

### Prerequisites
Ensure `basicc` and `basiclink` are installed and available on your `PATH`:
```bash
which basicc basiclink
```

### Building All Applications
To compile and link all sub-projects across the repository:
```bash
make build
```

### Running All Tests
To execute all test suites across all sub-projects:
```bash
make test
```

### Building Distribution Kits
To build release packages (both a unified master kit and individual per-application kits):
```bash
make dist
```
This produces ready-to-deploy `.tar.gz` archives in `distrib/`.

### Installing Applications
Install all applications into `${HOME}/.local/dec-apps` (with symlinks in `~/.local/bin`):
```bash
make install
```
Or install an individual application:
```bash
make install APP=sort11
# or
make install APP=hamurabi
```

### Uninstalling Applications
Uninstall all applications:
```bash
make uninstall
```
Or uninstall an individual application:
```bash
make uninstall APP=sort11
```

### Cleaning Build Artifacts
```bash
make clean
```

---

## Applications Catalog

| Application | Category | Description | Heritage |
| :--- | :--- | :--- | :--- |
| [`hamurabi`](apps/hamurabi) | Simulation / Game | Ancient Sumeria city-state economic and governance simulation | Richard Merrill (1968), David Ahl (*101 BASIC Computer Games*, DEC, 1973) |
| [`sort11`](apps/sort11) | System Utility | RMS file sort and index utility supporting sequential and SQLite-backed indexed files | Digital Equipment Corporation PDP-11 / RSTS/E / RSX-11M RMS-11 facility |
