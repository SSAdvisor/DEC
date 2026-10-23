# DEC VAX C V3.2 Compiler

Authentic DEC VAX C V3.2 Compiler (`vaxc`) targeting OpenVMS VAX V5.5-2 and `vmslink` / `vms_vm`.

## Features
- **Preprocessor**: `#include <stdio.h>`, `#include <stdlib.h>`, `#include <string.h>`, `#include <descrip.h>`, `#define NAME VAL`, `#pragma module <name> "<ident>"` / `#module <name> "<ident>"`, `#ifdef` / `#ifndef` / `#else` / `#endif`, `$DESCRIPTOR(dsc, "str")`.
- **Types & Language Constructs**: `int`, `long`, `short`, `char`, `float`, `double`, `void`, `char *`, `globaldef`, `globalref`, `readonly`, arrays `int arr[10]`, `struct <tag> { ... };`, member access `.` and `->`, functions with parameters & `return`, `main()`, `if / else if / else`, `while (...)`, `for (init; cond; step)`, `do { ... } while (...);`, `switch / case / default / break`, `++`, `--`, `+=`, `-=`, `*=`, `printf(...)`, `puts(...)`, `strlen`, `strcpy`, `strcat`, `strcmp`, `LIB$PUT_OUTPUT(...)`.
