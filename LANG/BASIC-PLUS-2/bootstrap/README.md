# DEC BASIC-PLUS-2 Bootstrap Toolchain

This directory contains the original Python and ANTLR4 reference implementation of the **DEC BASIC-PLUS-2** compiler and linker. It serves as the bootstrap toolchain used to build the native compiler (`compiler/basicc.bas`) and linker (`linker/basiclink.bas`).

## Contents

- `basicc.py`: Bootstrap compiler using ANTLR4 parser generator
- `basiclink.py`: Bootstrap linker and executable packager
- `grammar/`: ANTLR4 grammar (`RSTSBasic.g4`) and generated Python visitor/lexer
- `requirements.txt`: Python package requirements (`antlr4-python3-runtime`)

## Usage

### Bootstrap Compilation
```bash
python3 bootstrap/basicc.py <input.bas> -o <output.obj> [--module NAME]
```

### Bootstrap Linking
```bash
python3 bootstrap/basiclink.py [-o <output_executable>] <module1.obj> [module2.obj ...] [file.odl]
```

## Self-Hosting Workflow

1. Use `bootstrap/basicc.py` and `bootstrap/basiclink.py` to compile and link `compiler/basicc.bas` into `compiler/basicc`.
2. Use `bootstrap/basicc.py` and `bootstrap/basiclink.py` to compile and link `linker/basiclink.bas` into `linker/basiclink`.
3. Once bootstrapped, `compiler/basicc` and `linker/basiclink` can compile and link DEC BASIC-PLUS-2 programs natively without requiring Python or ANTLR.
