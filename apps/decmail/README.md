# DECmail - Electronic Messaging & Mail Management System

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's **DECmail** (DECmail-11 / VMS MAIL), an electronic mail and messaging system originally distributed for **DEC PDP-11 (RSTS/E, RSX-11M)** and **VAX/VMS** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: DECmail V3.0 / DECmail-11
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (RSTS/E, RSX-11M, RSX-11M-PLUS), VAX-11 (VAX/VMS)
- **Historical Significance**: Electronic mail was one of Digital Equipment Corporation's most influential software contributions. First developed for PDP-11 and VAX systems, DECmail and VMS MAIL connected engineering laboratories, corporate offices, and university departments worldwide via DECnet. It later became the central messaging core of DEC's flagship **ALL-IN-1** integrated office system.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine runtime.

---

## 2. Architecture & Mailbox Management

DECmail organizes messages into standard folders and structured fields:

1. **Folder Architecture**:
   - `NEWMAIL`: Unread incoming messages (flagged with `*`).
   - `MAIL`: Read and archived messages.
   - `WASTEBASKET`: Messages marked for deletion (flagged with `D`).
   - `ALL`: Consolidated view of all messages across all folders.

2. **Message Properties**:
   - **From**: Originating user and DECnet node (e.g. `KEN.OLSEN@DEC`, `VMS.DEV@DEC`).
   - **To**: Intended recipient or distribution list (`ALL`, `OPERATOR`, `STAFF`).
   - **Date**: Standard DEC alphanumeric date stamp (e.g. `12-OCT-1981`).
   - **Subject**: One-line summary of message content.
   - **Status**: Read (`R`), Unread (`U` / `*`), or Deleted (`D`).
   - **Body**: Multi-line message content.

3. **Interchange File Format (`DECMAIL.DAT`)**:
   - Pipe-delimited flat file: `FROM|TO|DATE|SUBJECT|STATUS|FOLDER|BODY`
   - Compatible with DEC flat-file transfer utilities and external text extraction.

---

## 3. Directory Layout

```
apps/decmail/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── decmail         # Compiled native ELF binary
│   ├── mail            # Symlink alias -> decmail
│   └── decmail11       # Symlink alias -> decmail
├── build/
│   └── decmail.bobj    # Intermediate BASIC-PLUS-2 object
├── src/
│   └── decmail.bas     # Native DEC BASIC-PLUS-2 source code (< 470 lines)
└── tests/
    ├── __init__.py     # Test package marker
    └── test_decmail.py # Automated pytest test suite (14 test cases)
```

---

## 4. Command Reference & Syntax

### Interactive Mode (REPL)
Launch `decmail` (or aliases `mail` / `decmail11`) without arguments to enter interactive mode:

```
$ ./bin/decmail
================================================================================
    DECmail V3.0 - Electronic Messaging & Mail Management System
    Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11
================================================================================
Type HELP for commands, or EXIT to quit.

MAIL> SAMPLE
[Sample DECmail mailbox loaded - 4 messages]

MAIL> DIR
================================================================================
  DECmail Folder: ALL
================================================================================
#   St  From                 Date         Subject
--------------------------------------------------------------------------------
1      KEN.OLSEN@DEC        12-OCT-1981  Welcome to Digital Equipment Corporation
2   *  VMS.DEV@DEC          14-OCT-1981  VAX/VMS V3.0 Field Test Announcement
3   *  PDP11.SYS@DEC        15-OCT-1981  RSTS/E Nightly Backup Complete
4   D  ALL-IN-1@DEC         16-OCT-1981  ALL-IN-1 Office System Update
--------------------------------------------------------------------------------
  4 messages listed (* = Unread, D = Deleted)
================================================================================

MAIL> READ 1
================================================================================
Message 1 (12-OCT-1981) - Folder: MAIL
From:    KEN.OLSEN@DEC
To:      ALL
Subject: Welcome to Digital Equipment Corporation
--------------------------------------------------------------------------------
Welcome to Digital. Innovation, quality, and commitment
to our customers define our mission.
Ken Olsen
================================================================================

MAIL> REPLY "Thank you Ken."
[Reply sent to KEN.OLSEN@DEC]

MAIL> EXIT
```

### Batch Mode & Command Chaining
Pass commands on the command line or chain commands with semicolons (`;`):

```bash
# Check status and list unread messages:
./bin/decmail 'SAMPLE; SELECT NEWMAIL; DIR; EXIT'

# Compose a message in batch:
./bin/decmail 'SAMPLE; SEND "TEST@DEC", "Meeting Note", "See you tomorrow at 10am."; EXIT'

# Read message and extract to text file:
./bin/decmail 'SAMPLE; EXTRACT memo.txt 1; EXIT'
```

### Complete Command Summary

| Command | Aliases | Description |
|---|---|---|
| `DIR [folder]` | `DIRECTORY` | Lists message index, status, sender, date, and subject. Optional folder filter. |
| `READ [msg#]` | `VIEW`, `TYPE` | Displays full headers and body of message. Advances active message pointer. |
| `SEND <to>, <subj>, <body>` | `MAIL`, `POST` | Composes and sends a new message to the specified recipient. |
| `REPLY [text]` | `REP` | Replies to the current message (sets `To:` and `Subject: RE: ...`). |
| `FORWARD <to>` | `FWD` | Forwards the current message to another user with forwarding banner. |
| `DELETE [msg#]` | `DEL` | Marks message as deleted and moves it to the `WASTEBASKET` folder. |
| `PURGE` | - | Permanently removes all discarded messages from the mailbox. |
| `EXTRACT <file> [msg#]` | `EXPORT` | Extracts formatted message header and body to a text file. |
| `SELECT <folder>` | `FOLDER` | Sets the active working folder (`MAIL`, `NEWMAIL`, `WASTEBASKET`, `ALL`). |
| `SHOW [STATUS]` | `STATUS` | Displays active folder, current user, message pointer, and counts. |
| `SAMPLE` | `DEMO` | Loads historical DEC demonstration mailbox (Ken Olsen, VMS, RSTS, ALL-IN-1). |
| `SAVE [file]` | - | Saves active mailbox to disk in pipe-delimited interchange format. |
| `LOAD [file]` | `IMPORT` | Loads mailbox records from a disk file. |
| `CLEAR` | `RESET`, `NEW` | Clears all messages from memory. |
| `HELP` | `?` | Displays summary of all available DECmail commands. |
| `EXIT` | `QUIT`, `BYE` | Terminates the DECmail session. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/decmail clean build
```

Run test suite:
```bash
make -C apps/decmail test
# or directly:
pytest apps/decmail/tests/
```

Run interactive session:
```bash
make -C apps/decmail run
```
