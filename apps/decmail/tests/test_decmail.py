import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "decmail.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
BOBJ_FILE = os.path.join(BUILD_DIR, "decmail.bobj")
EXE_FILE = os.path.join(BIN_DIR, "decmail")
MAIL_LINK = os.path.join(BIN_DIR, "mail")
DECMAIL11_LINK = os.path.join(BIN_DIR, "decmail11")


def test_decmail_build():
    """Verify that decmail.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(BOBJ_FILE), f"Object file {BOBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"
    assert os.path.islink(MAIL_LINK), f"Symlink {MAIL_LINK} not found"
    assert os.path.islink(DECMAIL11_LINK), f"Symlink {DECMAIL11_LINK} not found"


def test_decmail_banner_repl():
    """Verify interactive REPL displays DECmail banner on empty command line."""
    proc = subprocess.Popen([EXE_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input="EXIT\n", timeout=10)
    assert proc.returncode == 0
    assert "DECmail V3.0 - Electronic Messaging & Mail Management System" in out
    assert "Digital Equipment Corporation (DEC) PDP-11 / RSTS/E / VAX-11" in out
    assert "MAIL>" in out


def test_decmail_help():
    """Verify HELP command displays DECmail commands."""
    res = subprocess.run([EXE_FILE, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DECmail Electronic Messaging Commands" in res.stdout
    assert "DIR" in res.stdout
    assert "READ" in res.stdout
    assert "SEND" in res.stdout
    assert "REPLY" in res.stdout
    assert "FORWARD" in res.stdout
    assert "DELETE" in res.stdout
    assert "PURGE" in res.stdout
    assert "EXTRACT" in res.stdout
    assert "SELECT" in res.stdout
    assert "SHOW" in res.stdout


def test_decmail_sample_and_show():
    """Verify SAMPLE loads DEC historical sample messages and SHOW displays status."""
    res = subprocess.run([EXE_FILE, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Sample DECmail mailbox loaded - 4 messages]" in res.stdout
    assert "DECmail Status:" in res.stdout
    assert "Active Folder:  ALL" in res.stdout
    assert "Current User:   OPERATOR" in res.stdout
    assert "Total Messages: 4" in res.stdout
    assert "Unread:         2" in res.stdout
    assert "Deleted:        1" in res.stdout


def test_decmail_dir_all_and_folders():
    """Verify directory listing and folder filtering."""
    cmd = "SAMPLE; DIR; SELECT NEWMAIL; DIR; SELECT WASTEBASKET; DIR; EXIT"
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "DECmail Folder: ALL" in res.stdout
    assert "KEN.OLSEN@DEC" in res.stdout
    assert "VMS.DEV@DEC" in res.stdout
    assert "DECmail Folder: NEWMAIL" in res.stdout
    assert "DECmail Folder: WASTEBASKET" in res.stdout
    assert "ALL-IN-1 Office System Update" in res.stdout


def test_decmail_read_message():
    """Verify reading messages and status update."""
    res = subprocess.run([EXE_FILE, "SAMPLE; READ 1; READ 2; EXIT"], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "Message 1 (12-OCT-1981) - Folder: MAIL" in res.stdout
    assert "From:    KEN.OLSEN@DEC" in res.stdout
    assert "Subject: Welcome to Digital Equipment Corporation" in res.stdout
    assert "Welcome to Digital. Innovation, quality, and commitment" in res.stdout

    assert "Message 2 (14-OCT-1981) - Folder: MAIL" in res.stdout
    assert "From:    VMS.DEV@DEC" in res.stdout
    assert "Field test for VAX/VMS V3.0 has begun" in res.stdout


def test_decmail_send_message():
    """Verify composing and sending messages."""
    cmd = 'SAMPLE; SEND "TECH.LEAD@DEC", "Architecture Review", "Please review the DECmail draft."; DIR; READ 5; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Message 5 sent to TECH.LEAD@DEC]" in res.stdout
    assert "Message 5 (16-OCT-1981) - Folder: MAIL" in res.stdout
    assert "To:      TECH.LEAD@DEC" in res.stdout
    assert "Subject: Architecture Review" in res.stdout
    assert "Please review the DECmail draft." in res.stdout


def test_decmail_reply():
    """Verify replying to current message."""
    cmd = 'SAMPLE; READ 1; REPLY "Thanks for the welcome Ken."; READ 5; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Reply sent to KEN.OLSEN@DEC]" in res.stdout
    assert "Message 5 (16-OCT-1981) - Folder: MAIL" in res.stdout
    assert "To:      KEN.OLSEN@DEC" in res.stdout
    assert "Subject: RE: Welcome to Digital Equipment Corporation" in res.stdout
    assert "Thanks for the welcome Ken." in res.stdout


def test_decmail_forward():
    """Verify forwarding messages."""
    cmd = 'SAMPLE; READ 1; FORWARD "ARCHIVE@DEC"; READ 5; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Message 1 forwarded to ARCHIVE@DEC]" in res.stdout
    assert "Message 5 (16-OCT-1981) - Folder: MAIL" in res.stdout
    assert "To:      ARCHIVE@DEC" in res.stdout
    assert "Subject: FWD: Welcome to Digital Equipment Corporation" in res.stdout
    assert "--- Forwarded Message ---" in res.stdout


def test_decmail_delete_and_purge():
    """Verify deleting messages and purging mailbox."""
    cmd = 'SAMPLE; DELETE 1; SHOW; PURGE; SHOW; DIR; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert "[Message 1 marked deleted (moved to WASTEBASKET)]" in res.stdout
    assert "[Mailbox purged - 2 deleted messages removed]" in res.stdout
    assert "Total Messages: 2" in res.stdout


def test_decmail_extract_file(tmp_path):
    """Verify extracting message to external text file."""
    msg_file = str(tmp_path / "extracted_msg.txt")
    cmd = f'SAMPLE; EXTRACT {msg_file} 1; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[Message 1 extracted to {msg_file}]" in res.stdout

    assert os.path.isfile(msg_file)
    with open(msg_file) as f:
        content = f.read()
    assert "Message 1 (12-OCT-1981) - Folder: MAIL" in content
    assert "From:    KEN.OLSEN@DEC" in content
    assert "Ken Olsen" in content


def test_decmail_save_load(tmp_path):
    """Verify saving and loading mailbox data files."""
    box_file = str(tmp_path / "mailbox.dat")
    cmd = f'SAMPLE; SAVE {box_file}; CLEAR; SHOW; LOAD {box_file}; DIR; EXIT'
    res = subprocess.run([EXE_FILE, cmd], capture_output=True, text=True, timeout=10)
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    assert f"[4 messages saved to {box_file}]" in res.stdout
    assert "[Mailbox cleared]" in res.stdout
    assert f"[4 messages loaded from {box_file}]" in res.stdout
    assert "KEN.OLSEN@DEC" in res.stdout
    assert "4 messages listed" in res.stdout


def test_decmail_symlinks():
    """Verify mail and decmail11 symlinks execute properly."""
    res_mail = subprocess.run([MAIL_LINK, "SAMPLE; SHOW; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_mail.returncode == 0
    assert "Total Messages: 4" in res_mail.stdout

    res_decmail11 = subprocess.run([DECMAIL11_LINK, "HELP; EXIT"], capture_output=True, text=True, timeout=10)
    assert res_decmail11.returncode == 0
    assert "DECmail Electronic Messaging Commands" in res_decmail11.stdout


def test_decmail_error_handling():
    """Verify error messages for empty mailbox or invalid numbers."""
    res1 = subprocess.run([EXE_FILE, "CLEAR; READ; EXIT"], capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0
    assert "DECmail: No messages in mailbox" in res1.stdout

    res2 = subprocess.run([EXE_FILE, "SAMPLE; READ 99; EXIT"], capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert "DECmail: Message number out of range" in res2.stdout

    res3 = subprocess.run([EXE_FILE, "UNKNOWN_CMD; EXIT"], capture_output=True, text=True, timeout=10)
    assert res3.returncode == 0
    assert "DECmail: Unknown command 'UNKNOWN_CMD'" in res3.stdout
