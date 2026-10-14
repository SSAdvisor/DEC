# DEC RSTS/E EDT Text Editor V3.0

An authentic, feature-rich implementation of the classic Digital Equipment Corporation **EDT** text editor, written entirely in **DEC BASIC-PLUS-2** (`edt/edt.bas`) and compiled directly to a native executable via `basicc.py` and `basiclink.py`.

---

## 1. Overview & Architecture

EDT was the primary text editor for DEC operating systems, including **RSTS/E**, **RSX-11M/11M-PLUS**, and **OpenVMS**. This implementation brings authentic DEC EDT functionality to modern environments powered by the DEC-BASIC-PLUS-2 compiler and RSTS virtual machine.

### Key Features
- **Authentic Dual-Mode Interface**:
  - **Line Editing Mode** (`*` prompt): Traditional command-line editing with line-range targeting (`1:10`, `WHOLE`, `.`), resequencing, text substitutions, and session inspections.
  - **Change / Screen Mode** (`CHANGE` or `C`): Full-screen VT100 video terminal interface featuring inverse video cursor highlight (`\033[7m`), status bar, single-keypress navigation, and live buffer editing.
- **Pure DEC BASIC-PLUS-2**: Built completely in BASIC-PLUS-2 with sequential channel I/O (`#1%`, `#2%`), dynamic string manipulation (`INSTR`, `MID$`, `LEFT$`, `RIGHT$`, `LEN`), and error handling (`ON ERROR GOTO`).
- **Dynamic File Management**: Opens existing text files, auto-creates new files when files do not exist, and writes changes back to disk with `EXIT` or `WRITE`.

---

## 2. Directory Structure

```
edt/
├── edt.bas           # Source code written in DEC BASIC-PLUS-2
├── edt.bobj          # Compiled BASIC object file (JSON bytecode format)
├── edt.bin           # Raw binary bytecode
├── edt               # Standalone executable binary (VM + bytecode payload)
├── build.sh          # Automated build script
├── sample.txt        # Sample text document for demonstration and testing
└── README.md         # Documentation and command reference
```

---

## 3. Building and Running

### Build from Source
To compile `edt.bas` and link the executable:
```bash
./edt/build.sh
```

Or manually using the compiler tools:
```bash
python3 compiler/basicc.py edt/edt.bas -o edt/edt.bobj
python3 compiler/basiclink.py edt/edt.bobj -o edt/edt
```

### Running EDT
```bash
./edt/edt
```
Upon startup, EDT prompts for the file name:
```
DEC RSTS/E EDT Editor V3.0 (BASIC-PLUS-2)
Copyright (C) Digital Equipment Corporation / DEC-BASIC-PLUS-2

File: sample.txt
[File sample.txt, 14 lines read]
Type HELP for command list, or CHANGE for screen mode.

*
```

---

## 4. Command Reference

### Line Mode Commands (`*` Prompt)

| Command | Shorthand | Syntax / Example | Description |
|---|---|---|---|
| `TYPE` | `T` | `T`, `T .`, `T 1:5`, `T WHOLE` | Display lines in the buffer with line numbers and current line indicator (`>`). |
| `INSERT` | `I` | `I`, `I 5` | Enter insert mode before the specified line. Terminate with `.` or `Ctrl-Z` on an empty line. |
| `DELETE` | `D` | `D`, `D 3`, `D 1:10`, `D WHOLE` | Delete one or more lines in the buffer and adjust line numbering. |
| `REPLACE` | `R` | `R`, `R 5`, `R 2:4` | Delete the specified range and immediately prompt for replacement text. |
| `FIND` | `F` | `F error`, `F 12` | Search forward (with wrap-around) for a substring, or jump directly to a line number. |
| `SUBSTITUTE` | `S` | `S /old/new/` | Substitute the first occurrence of `old` with `new` in the current line. |
| `RESEQ` | `RESEQ` | `RESEQ` | Resequence buffer line indices and reset current line pointer. |
| `DEFINE KEY` | `DEF KEY` | `DEFINE KEY 7 AS 'T WHOLE'` | Bind a key sequence or keypad number to an EDT command string. |
| `DEFINE MACRO` | `DEF MACRO` | `DEFINE MACRO SWAP AS 'F a;S /a/b/;T .'` | Define a named macro containing a sequence of commands separated by `;`. |
| `SHOW` | `SHOW` | `SHOW`, `SHOW KEY`, `SHOW MACRO` | Display active session info, defined keypad keys, or named macros. |
| `@file` | `@` | `@setup.edt` | Execute line-mode EDT commands from a command procedure file. |
| `CHANGE` | `C` | `CHANGE`, `C` | Enter VT100 full-screen screen editing mode. |
| `WRITE` | `W` | `W`, `W copy.txt` | Write the buffer contents to disk without exiting EDT. |
| `EXIT` | `EX` | `EXIT`, `EX` | Save the buffer contents to the file and exit to system prompt. |
| `QUIT` | `QU` | `QUIT`, `QU` | Exit EDT immediately without saving changes. |
| `HELP` | `HELP` | `HELP` | Display the EDT command summary and syntax guide. |

### Change Mode (VT100 Full-Screen Mode)

Enter with `CHANGE` or `C` from the `*` prompt. The screen clears and displays the buffer window with cursor highlight.

| Key | Action |
|---|---|
| `N` / `j` / `Enter` | Move down to next line |
| `P` / `k` | Move up to previous line |
| `I` / `a` | Prompt to insert text at current line |
| `D` | Delete the current line |
| `G` / `g` / `Ctrl-G` | **GOLD Key**: Activates GOLD modifier for the next keypress (e.g. `GOLD D`, `GOLD 7`) |
| *Custom Keys* | Any key defined with `DEFINE KEY <k>` or `DEFINE KEY GOLD <k>` executes the macro and returns to Screen Mode |
| `Q` / `Esc` / `Ctrl-Z` | Return cleanly to Line Mode (`*` prompt) |

---

## 5. Startup Configuration (`EDTINI.EDT`)

EDT automatically checks for an initialization file named `EDTINI.EDT` in the current working directory upon startup. If found, EDT automatically executes all commands defined within it (e.g., custom keypad bindings, user macros, and default editor settings) before presenting the command prompt.

---

## 6. Automated Verification

The test suite in `tests/test_edt.py` tests all core functionality using `pytest`:

```bash
pytest tests/test_edt.py -v
```

All 11 test cases verify file creation, loading, range typing, inserting, pattern searching, string substitutions, line deletions, resequencing, macro definitions and execution, keyboard shortcut bindings, command file `@file` execution, `EDTINI.EDT` auto-loading, and clean abort/exit semantics.
