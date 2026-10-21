# DEC-APPS Distribution System

A release packaging and deployment system for DEC-APPS applications, modeled on the Digital Equipment Corporation software distribution architecture used in the DEC BASIC-PLUS-2 environment.

---

## 1. Overview

The `distrib/` subsystem packages applications into both a **Unified Master Release Kit** and **Individual Standalone Kits**. Applications can be installed or uninstalled individually, in select subsets, or all at once.

### Key Capabilities
- **Master Release Kit (`DEC-APPS-V1.0-L-Linux-x86_64.tar.gz`)**: Contains all DEC applications with a unified installer capable of installing all or individual applications.
- **Individual Application Kits (`DEC-APPS-<app>-V1.0-L-Linux-x86_64.tar.gz`)**: Independent standalone release archives containing only the specified application and its dedicated installer.
- **Source Release Archive (`DEC-APPS-V1.0-Source.tar.gz`)**: Full clean source tree for building from scratch.
- **Manifests & Verification**: Every kit includes a DEC `KIT.INI` component descriptor and a `MANIFEST.TXT` SHA-256 integrity checksum file verified by `verify_kit.sh`.

---

## 2. Directory Layout

```
distrib/
├── build_kit.sh           # Master build and packaging script
├── install.sh             # Application installer (all or individual)
├── uninstall.sh           # Application uninstaller (all or individual)
├── verify_kit.sh          # Functional test & verification script
├── README.md              # This documentation
├── DEC-APPS-*.tar.gz      # Generated binary and source distribution kits (gitignored)
└── kit/                   # Staging area for kit builders (gitignored)
```

---

## 3. Building Distribution Kits

To build all application binaries and package all distribution archives:

```bash
./distrib/build_kit.sh
```
or via the root Makefile:
```bash
make dist
```

This automatically produces:
1. `distrib/DEC-APPS-V1.0-L-Linux-x86_64.tar.gz` (Master release archive)
2. `distrib/DEC-APPS-hamurabi-V1.0-L-Linux-x86_64.tar.gz` (Individual Hamurabi archive)
3. `distrib/DEC-APPS-sort11-V1.0-L-Linux-x86_64.tar.gz` (Individual SORT-11 archive)
4. `distrib/DEC-APPS-V1.0-Source.tar.gz` (Source archive)

---

## 4. Installation

### Install All Applications
```bash
./distrib/install.sh
```
Installs all available applications into `${HOME}/.local/dec-apps` (non-root) or `/usr/local/dec-apps` (root), creating global symlinks in `${HOME}/.local/bin` or `/usr/local/bin`.

### Install an Individual Application
```bash
# Install only SORT-11
./distrib/install.sh sort11

# Install only Hamurabi
./distrib/install.sh hamurabi

# Install multiple specific applications
./distrib/install.sh hamurabi sort11
```

### List Available Applications in Kit
```bash
./distrib/install.sh --list
```

### Custom Installation Paths & Options
```bash
./distrib/install.sh --prefix=/opt/dec-apps --symlink-dir=/usr/bin sort11
./distrib/install.sh --no-symlinks
./distrib/install.sh --no-verify
```

---

## 5. Uninstallation

### Uninstall an Individual Application
```bash
./distrib/uninstall.sh sort11
```
Removes the `sort11` binary, documentation, and symlink while leaving other installed DEC applications untouched.

### Uninstall All Applications
```bash
./distrib/uninstall.sh
# or
./distrib/uninstall.sh all
```

---

## 6. Verification

To verify that installed applications are present and pass functional self-tests:
```bash
./distrib/verify_kit.sh
# or for a specific application:
./distrib/verify_kit.sh sort11
```
