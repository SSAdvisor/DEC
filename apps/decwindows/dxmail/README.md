# DECwindows Mail V3.0 (`dxmail` / `decwinmail`)

A native **DEC BASIC-PLUS-2** implementation of **DECwindows Mail** (`DECW$MAIL` / `dxmail`), the XUI and OSF/Motif graphical electronic mail cabinet, drawer/folder organizer, and Compound Document Architecture (`DDIF`) message viewer for VAX/VMS, ULTRIX, and DEC OSF/1 workstations (1988–1993).

---

## Overview & Workstation Heritage

Unlike character-cell `VMS MAIL`, **DECwindows Mail** (`dxmail`) organized electronic correspondence using a multi-level **Filing Cabinet** metaphor:
- **Drawers & Folders:** Top-level drawers (`MAIN`, `PROJECTS`) containing specialized folders (`INBOX`, `READ`, `SENT`, `DRAFTS`, `WASTEBASKET`, `ALPHA_OSF1`).
- **CDA / DDIF Compound Messages:** Alongside standard ASCII `TEXT` messages, DECwindows Mail natively sent, received, and rendered **Compound Document Architecture (`DDIF`)** multimedia and structured messages.
- **Three-Pane Motif Interface:** Combined a Drawer/Folder hierarchy view, a scrollable Message Header summary list, a push-button action bar (`[Read]`, `[Send/New]`, `[Reply]`, `[Forward]`, `[Move]`, `[Delete]`, `[Next]`, `[Prev]`, `[Search]`), and an integrated Read Pane.

---

## Command Reference

| Command | Description |
| :--- | :--- |
| `SAMPLE` | Load the 1991 ZKO Engineering Mail Cabinet (`MAIN` & `PROJECTS` drawers, 6 messages in `TEXT` and `DDIF`) |
| `CABINET` / `DRAWERS` / `FOLDERS` | Display the hierarchical Mail Cabinet tree with total and unread message counts per drawer/folder |
| `SELECT <folder>` / `FOLDER` / `OPEN` | Open a specific folder (`INBOX`, `READ`, `SENT`, `DRAFTS`, `WASTEBASKET`, `ALPHA_OSF1`, or `ALL`) |
| `DIR [folder]` / `LIST` / `HEADERS` | List message headers in the active or specified folder with status (`*` Unread, `M` Marked, `D` Deleted) and format (`[TEXT]`, `[DDIF]`) |
| `READ <n>` / `VIEW <n>` | Read message `#n` in full (marks `UNREAD` messages as `READ` and identifies `DDIF` compound streams) |
| `NEXT` / `PREV` | Step forward or backward through messages in the cabinet |
| `SEND <to>\|<subj>\|<fmt>\|<body>` | Compose and transmit a new `TEXT` or `DDIF` message and file a copy in `MAIN:SENT` |
| `REPLY <n>\|<body>` | Send a reply (`RE: <subject>`) to the sender of message `#n` |
| `FORWARD <n>\|<to>\|<note>` | Forward message `#n` (`FWD: <subject>`) with an introductory note to `<to>` |
| `MOVE <n> [drawer:]<folder>` / `FILE` | File message `#n` into another drawer and folder |
| `MARK <n>` / `UNMARK <n>` | Flag message `#n` as `MARKED` or clear the flag back to `READ` |
| `DELETE <n>` | Move message `#n` to `MAIN:WASTEBASKET` with status `DELETED` |
| `PURGE` / `EMPTY` | Permanently empty all deleted messages from `WASTEBASKET` |
| `SEARCH <keyword>` / `FIND` / `PICK` | Case-insensitive full-text search across From, To, Subject, and Body |
| `EXTRACT <n> <file>` | Export message `#n` headers and body to an external text file |
| `DISPLAY` / `RENDER` / `PRINT ON <file>` | Render the 78-column Motif/XUI DECwindows Mail cabinet window to terminal or file |
| `SAVE <file>` / `LOAD <file>` | Save or load the complete Mail Cabinet state (`.dxm`) |
| `SHOW` / `CLEAR` / `HELP` / `EXIT` | Display cabinet status, reset cabinet, view command help, or exit |
