# DEC RSTS/E BASIC-PLUS-2 Compiler (`basicc`)

An authentic, standalone implementation of the **DEC RSTS/E BASIC-PLUS-2 Compiler**, written entirely in **pure DEC BASIC-PLUS-2** (`compiler/basicc.bas`) and compiled into a native Linux ELF executable (`compiler/basicc`).

## Overview

The compiler translates DEC BASIC-PLUS-2 source programs into RSTS/E VM bytecode modules (`.obj` and `.bin` files) with full support for language constructs, overlay relocations, RMS record I/O, MAP statements, error handling, and structured control flow.

### Key Capabilities

- **Pure BASIC-PLUS-2 Implementation**: The entire compiler (`compiler/basicc.bas`) is written in DEC BASIC-PLUS-2, using alphanumeric subroutine labels, recursive expression stacks, and table-driven symbol management.
- **Two-Pass Architecture**:
  - **Pass 1**: Scans and parses `DATA` statements to build constant data pools (`DATA_INT%`, `DATA_STR$`, `DATA_TYPE%`).
  - **Pass 2**: Compiles statements, evaluates expressions (with operator precedence: `OR`, `AND`, comparisons, `+`/`-`, `*`/`/`, unary `-`, function calls, array subscripting, and nested parentheses), emits bytecode, and records jump and symbol relocations.
  - **Relocation Resolution**: Resolves all numeric line targets and alphanumeric label targets to bytecode offsets.
- **Full Language Coverage**:
  - Statements: `PRINT`, `LET`, `IF...THEN...ELSE` (single-line and block `END IF`), `FOR...TO...STEP...NEXT`, `GOTO`, `GOSUB`/`RETURN`, `ON ERROR GOTO`, `RESUME`, `OPEN`, `CLOSE`, `GET`, `PUT`, `FIELD`, `MAP`, `DATA`/`READ`/`RESTORE`, `CALL` (overlay invocation), `DIM`, `SLEEP`, `END`, `STOP`.
  - Built-in functions: `CHR$`, `ASCII`, `STR$`, `VAL`, `LEN`, `MID$`, `LEFT$`, `RIGHT$`, `INSTR`, `TIME$`, `DATE$`, `INT`, `FIX`, `ABS`, `SGN`, `SQR`, `INKEY$`, `SYS`.
- **Overlay Support**:
  - Compiles main programs (`--module MAIN` or default) with `OP_HALT` (0x00).
  - Compiles overlay segments (`--module NAME`) with `OP_RET` (0x41) and generates `CALL_OVL` relocations for external segment calls.
- **Zero Python Runtime Dependency**: The native executable (`compiler/basicc`) runs directly via the RSTS/E VM runtime without Python or ANTLR installed.

## Usage

```bash
# Compile single-module program:
./compiler/basicc tests/test_link.bas -o tests/test_link.obj

# Compile overlay modules:
./compiler/basicc tests/func1.bas -o tests/func1.obj --module FUNC1
./compiler/basicc tests/func2.bas -o tests/func2.obj --module FUNC2
```

## Building from Source

To bootstrap or rebuild `compiler/basicc`:
```bash
./compiler/build.sh
```
This invokes `bootstrap/basicc.py` to compile `compiler/basicc.bas` into `compiler/basicc.obj` and links it via `linker/basiclink` into the standalone `compiler/basicc` binary.

## Compatibility Shim

`compiler/basicc.py` is maintained as a transparent CLI wrapper around `./compiler/basicc` (falling back to `bootstrap/basicc.py` if needed), ensuring seamless compatibility with existing test runners and scripts.
