# DECwindows Bookreader (`bookreader` / `dxbook`)

A native **DEC BASIC-PLUS-2** implementation of **DECwindows Bookreader** (`DECW$BOOKREADER` / `dxbook`), Digital Equipment Corporation's online hypertext documentation viewer introduced with DECwindows on VAX/VMS and ULTRIX workstations.

---

## Historical Background

Distributed alongside VAX/VMS Consolidated Online Documentation (OLD) CD-ROMs beginning in 1989, **Bookreader** organized manuals into `.DECW$BOOKSHELF` libraries containing `.DECW$BOOK` hypertext books. Users could browse hierarchical Tables of Contents, follow interactive **Hotspot** cross-reference links between sections and manuals, search full text across manuals, and save personal reader bookmarks.

---

## Commands Reference

| Command | Description |
| :--- | :--- |
| `SAMPLE` / `DEMO` | Load sample `LIBRARY.DECW$BOOKSHELF` with 3 DEC manuals, 6 topics, and 2 bookmarks |
| `SHELF` / `BOOKS` / `LIBRARY` | List all books on the active bookshelf with topic counts |
| `OPEN <id_or_code>` | Open a book by numeric ID or symbol code (e.g. `VMS_DCL`, `DECWIN_USER`, `BP2_REF`) |
| `TOC [ALL]` | Display Table of Contents for the active book or all books (`TOC ALL`) |
| `READ <id_or_sec>` | Read a topic by topic number or section number (e.g. `READ 1.2`) |
| `NEXT` / `PREV` | Navigate sequentially to the next or previous topic |
| `FOLLOW` / `HOTSPOT` / `LINK` | Follow the hypertext Hotspot cross-reference link in the current topic |
| `SEARCH <keyword>` / `FIND <kw>` | Perform a case-insensitive full-text search across all books and topics |
| `BOOKMARK [note]` / `MARK` | Save a bookmark on the currently open topic |
| `BOOKMARKS` / `MARKS` | List all saved bookmarks |
| `ADDBOOK <code\|title>` | Add a new `.DECW$BOOK` manual to the bookshelf |
| `ADDTOPIC <sec\|title\|body\|xref>` | Add a new hypertext topic section to the open book |
| `DELTOPIC <id>` | Delete topic `#<id>` from the library |
| `DISPLAY [ON <file>]` / `SCREEN` | Render the Motif/XUI Bookreader Topic Window (or export to file) |
| `SHOW` / `STATUS` | Display active bookshelf, open book, current topic, and counts |
| `SAVE <file>` / `LOAD <file>` | Save or load the bookshelf and topic database |
| `CLEAR` / `EXIT` | Clear library state or exit Bookreader |
