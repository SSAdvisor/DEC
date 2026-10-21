# HAMURABI - The Ancient Game of Sumeria

A faithful DEC **BASIC-PLUS-2** implementation of the classic strategy simulation *HAMURABI*, one of the most famous computer games in computing history.

---

## 1. Historical Background & Heritage

- **Original Authors**: Richard Merrill (1968, written in FOCAL as `KING` / `SUMER` at Digital Equipment Corporation in Maynard, MA)
- **BASIC Translation**: David H. Ahl (1973, translated to DEC BASIC-PLUS for RSTS-11 and published by DEC in *101 BASIC Computer Games*)
- **Target Platform**: DEC PDP-11 (RSTS/E), DECsystem-10/20, VAX/VMS
- **Dialect**: DEC BASIC-PLUS-2
- **Compilation Toolchain**: `basicc` (native compiler) and `basiclink` (native linker)

---

## 2. Gameplay

You govern the ancient city-state of Sumeria for a ten-year term of office. Each year, you must decide:
1. **Land Purchases / Sales**: Buy or sell acres of land using your store of grain (land prices fluctuate dynamically between 17 and 26 bushels per acre).
2. **Food Allocation**: Feed your citizens (each citizen requires 20 bushels to survive).
3. **Agriculture**: Plant acres with seed (1 bushel of grain plants 2 acres; each citizen can cultivate up to 10 acres).

Watch out for unpredictable events such as plagues, varying crop yields (1 to 5 bushels/acre), and grain loss due to rats. If you starve too many citizens in a single year, you will be promptly impeached and declared a **National Fink**!

---

## 3. Directory Layout

```
apps/hamurabi/
├── README.md           # This documentation
├── Makefile            # Sub-project build and test automation
├── src/
│   └── hamurabi.bas    # DEC BASIC-PLUS-2 source code
└── tests/
    ├── __init__.py
    └── test_hamurabi.py # Dedicated pytest test suite
```

---

## 4. Building and Running

### Build
To compile and link the application:
```bash
make build
```
This produces the bytecode object in `build/hamurabi.obj` and the standalone native binary in `bin/hamurabi`.

### Run
To play the game interactively:
```bash
make run
```
or directly:
```bash
./bin/hamurabi
```

### Test
To run the dedicated sub-project test suite:
```bash
make test
```
