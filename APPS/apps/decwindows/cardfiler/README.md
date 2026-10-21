# DECwindows Cardfiler (`cardfiler` / `dxcardfiler`)

A native **DEC BASIC-PLUS-2** implementation of **DECwindows Cardfiler** (`DECW$CARDFILER` / `dxcardfiler`), Digital Equipment Corporation's graphical rotary index card database manager for VAX/VMS and ULTRIX workstations.

---

## Historical Background

Part of the original 1988 DECwindows desktop accessories suite, **Cardfiler** emulated a desktop rotary file of 3x5 index cards stored in `.CRD` deck files. Each card had an **Index Header** line (used for alphabetical tab sorting and quick lookup) and a free-form card body for telephone numbers, DECnet node addresses (`NODE::USER`), and reference notes.

---

## Commands Reference

| Command | Description |
| :--- | :--- |
| `SAMPLE` / `DEMO` | Load sample `DEC_DIRECTORY.CRD` engineering & node directory (6 cards) |
| `LIST [category]` / `DECK` | List all cards in the deck, optionally filtered by category |
| `READ <id_or_index>` / `CARD` | Display a full 3x5 index card by card number or index header substring |
| `NEXT` / `PREV` | Flip sequentially forward or backward through the rotary card deck |
| `ADD <index\|cat\|node\|body>` | Create and add a new index card to the deck |
| `UPDATE <id\|index\|cat\|node\|body>` | Modify an existing index card |
| `DUP [id]` / `COPY [id]` | Duplicate an index card onto a new `(Copy)` card |
| `DELETE <id>` / `DEL <id>` | Remove card `#<id>` from the deck |
| `SORT [INDEX\|CATEGORY]` | Sort the rotary card deck alphabetically by Index Header or Category |
| `SEARCH <keyword>` / `FIND` | Search across all card fields (index, category, node, body) |
| `DISPLAY [ON <file>]` / `SCREEN` | Render the Motif/XUI Cardfiler window (or export to file) |
| `SHOW` / `STATUS` | Display active `.CRD` deck file, card count, and selected card |
| `SAVE <file>` / `LOAD <file>` | Save or load `.CRD` card deck files |
| `CLEAR` / `EXIT` | Clear card deck or exit Cardfiler |
