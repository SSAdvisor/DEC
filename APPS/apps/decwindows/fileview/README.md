# DECwindows FileView V3.0 (`fileview` / `dxfileview`)

A native **DEC BASIC-PLUS-2** implementation of **DECwindows FileView** (`VUE$MASTER` / `fileview` / `dxfileview`), the workstation graphical file manager, VAX/VMS RMS directory browser, file version controller, and DCL verb launcher for VAX/VMS, ULTRIX, and DEC OSF/1 workstations (1988–1993).

---

## Overview & Workstation Heritage

In DECwindows XUI and Motif (`VUE$MASTER`), **FileView** served as the primary user desktop shell and file management utility:
- **VMS RMS File & Version Management:** Displays full VAX/VMS file specifications (`DISK:[DIR]FILENAME.EXT;VER`), size in 512-byte blocks, RMS organization (`SEQ/VAR`, `IDX/KEY`, `EXE/IMG`), revision timestamps, and VMS UIC protection masks (`(S:RWED,O:RWED,G:RE,W:)`).
- **Automatic File Versioning & `PURGE`:** Creating or copying a file automatically increments its VMS version number (`;1`, `;2`, `;3`), while `PURGE` removes superseded lower-numbered file versions.
- **DCL Verb & Subprocess Launcher:** Launches `.COM` DCL command procedures, `.EXE` images, and interactive `$ DCL` verbs directly from the FileView work area.

---

## Command Reference

| Command | Description |
| :--- | :--- |
| `SAMPLE` | Load the 1991 VAX/VMS V5.5 & Alpha AXP file catalog across `SYS$SYSROOT:[SYSMGR]`, `SYS$COMMON:[SYSEXE]`, and `DISK$USER:[CONKLIN.AXP]` |
| `SHOW` / `STATUS` / `PWD` | Display active default directory, wildcard filter, total files, and disk block usage |
| `CD <dir>` / `SETDEF <dir>` | Change active default directory (`SYS$SYSROOT:[SYSMGR]`, `SYS$COMMON:[SYSEXE]`, `DISK$USER:[CONKLIN.AXP]`, or `ALL`) |
| `FILTER <pattern>` | Set file wildcard filter (`*.*`, `*.COM`, `*.EXE`, `*.MAR`) |
| `DIR [dir]` / `LIST` / `LS` | List files in the active directory matching the current filter with block counts and RMS attributes |
| `TYPE <n>` / `VIEW <n>` | Inspect full RMS attributes, UIC protection mask, and contents of file `#n` |
| `CREATE <name>\|<blk>\|<org>\|<body>` | Create a new file in the active directory (automatically increments `;version` if `<name>` exists) |
| `COPY <n> <newname>` | Copy file `#n` to `<newname>` with automatic VMS version numbering |
| `RENAME <n> <newname>` | Rename file `#n` to `<newname>` |
| `DELETE <n>` | Delete file `#n` from the workspace catalog |
| `PURGE` | Remove superseded older VMS versions (`;1`, etc.) while preserving the highest version of each file |
| `PROTECT <n> <prot>` / `SETPROT` | Update the VMS UIC protection mask on file `#n` |
| `RUN <n>` / `SUBMIT <n>` / `DCL <cmd>` | Execute a `.COM`/`.EXE` file `#n` or run a `$ DCL` verb in the FileView subprocess |
| `SEARCH <keyword>` / `FIND` | Case-insensitive search across directory names, filenames, and file contents |
| `DISPLAY` / `RENDER` / `PRINT ON <file>` | Render the 78-column Motif/XUI FileView desktop window to terminal or file |
| `SAVE <file>` / `LOAD <file>` | Save or load the FileView catalog (`.fvw`) |
| `CLEAR` / `HELP` / `EXIT` | Reset catalog, display help, or exit |
