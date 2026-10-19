# DECwindows Notepad V3.0 (`notepad` / `dxnotepad`)

A native **DEC BASIC-PLUS-2** implementation of **DECwindows Notepad** (`DECW$NOTEPAD` / `notepad` / `dxnotepad`), the XUI and OSF/Motif desktop text editor, `DECW$CLIPBOARD` cut/copy/paste manager, and search/replace utility for VAX/VMS, ULTRIX, and DEC OSF/1 workstations (1988–1993).

---

## Overview & Workstation Heritage

In DECwindows XUI and Motif (`DECW$NOTEPAD`), **Notepad** provided a fast, visual multi-line `XmText` editor integrated with the workstation clipboard:
- **X11 / Motif Clipboard (`DECW$CLIPBOARD`) Integration:** Supports multi-line `COPY`, `CUT`, `PASTE`, and `CLIPBOARD` inspection for moving blocks of text within or across documents.
- **Global Search & Replace:** Case-insensitive `FIND` (`SEARCH`) with line and column reporting, plus global `REPLACE <old>|<new>` across the buffer.
- **Word-Wrap Reflow & Read-Only Protection:** Configurable `WRAP <col|OFF>` column reflowing and `READONLY <ON|OFF>` buffer lock protection.

---

## Command Reference

| Command | Description |
| :--- | :--- |
| `SAMPLE` | Load the 1991 DECwindows Motif 1.1 & Alpha AXP engineering scratchpad (`SYS$LOGIN:AXP_NOTES.TXT`) |
| `LIST` / `VIEW` / `TYPE` / `READ` | Display all lines in the document buffer with line numbers and cursor marker (`>`) |
| `APPEND <text>` / `ADD <text>` | Append a new line to the end of the document buffer |
| `INSERT <n>\|<text>` | Insert a new line before line `#n` |
| `EDIT <n>\|<text>` / `SETLINE` | Replace the contents of line `#n` |
| `DELETE <start> [end]` / `DELLINE` | Delete a single line or inclusive range of lines |
| `COPY <start> [end]` | Copy line(s) into the DECwindows Clipboard (`DECW$CLIPBOARD`) |
| `CUT <start> [end]` | Copy line(s) into `DECW$CLIPBOARD` and remove them from the document buffer |
| `PASTE [after_line]` | Insert `DECW$CLIPBOARD` lines after `[after_line]` (or at the end of the buffer) |
| `CLIPBOARD` | Display the current contents of `DECW$CLIPBOARD` |
| `FIND <keyword>` / `SEARCH` | Case-insensitive search across all lines, reporting line and column numbers |
| `REPLACE <old>\|<new>` | Replace occurrences of `<old>` with `<new>` across the document buffer |
| `WRAP <col\|OFF>` | Set word-wrap column (`20..132` or `OFF`) and reflow lines |
| `READONLY <ON\|OFF>` | Enable or disable Read-Only buffer protection |
| `STATS` / `SHOW` / `STATUS` | Display document filename, modified/read-only state, line/word/character counts, and wrap column |
| `DISPLAY` / `RENDER` / `PRINT ON <file>` | Render the 78-column Motif/XUI DECwindows Notepad window to terminal or file |
| `SAVE <file>` / `LOAD <file>` | Save or load document text files |
| `CLEAR` / `NEW` / `HELP` / `EXIT` | Clear document buffer, display help, or exit |
