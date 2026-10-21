import os
import sys
import subprocess
import pytest

COMPILER_CMD = f"{sys.executable} compiler/basicc.py {{input}} -o {{output}} {{extra}}"
LINKER_CMD = f"{sys.executable} compiler/basiclink.py {{inputs}} {{odl}} -o {{output}}"

PREAMBLE = """1 C=C
2 N$=N$
3 A$=A$
4 T$=T$
5 B$=B$
6 U$=U$
7 C$=C$
8 V$=V$
9 P$=P$
10 W$=W$
11 Q$=Q$
12 X$=X$
13 R$=R$
14 Y$=Y$
15 E$=E$
16 Z$=Z$
17 F$=F$
18 S$=S$
19 G$=G$
20 D$=D$
21 I=I
"""

def write_bas(filename, content):
    with open(filename, "w") as f:
        # Shift line numbers in content to start after preamble
        lines = content.strip().split('\n')
        f.write(PREAMBLE)
        for line in lines:
            if line.strip():
                f.write(line + "\n")

def test_address_book_full():
    os.makedirs("tests/address_book", exist_ok=True)
    
    main_bas = """100 CALL "TUIDRAW"
110 INPUT C
120 IF C = 1 THEN GOTO 200
130 IF C = 2 THEN GOTO 300
140 IF C = 3 THEN GOTO 400
150 IF C = 4 THEN GOTO 500
160 IF C = 5 THEN GOTO 600
170 IF C = 6 THEN GOTO 700
180 GOTO 100
200 CALL "DBVIEW"
210 GOTO 100
300 CALL "EDITNAME"
310 GOTO 100
400 CALL "EDITADDR"
410 GOTO 100
500 CALL "EDITPHON"
510 GOTO 100
600 CALL "EDITEMAIL"
610 GOTO 100
700 PRINT "Exiting Address Book"
710 END
"""

    tui_bas = """100 PRINT "========================="
110 PRINT "   Address Book TUI      "
120 PRINT "========================="
130 PRINT "1: View Database"
140 PRINT "2: Edit Name"
150 PRINT "3: Edit Addresses"
160 PRINT "4: Edit Phones"
170 PRINT "5: Edit Emails"
180 PRINT "6: Exit"
190 PRINT "Choice?"
200 END
"""

    db_bas = """100 PRINT "--- DATABASE VIEW ---"
110 PRINT "Name:"
120 PRINT N$
130 PRINT "Addr 1:"
140 PRINT A$
150 PRINT T$
160 PRINT "Addr 2:"
170 PRINT B$
180 PRINT U$
190 PRINT "Addr 3:"
200 PRINT C$
210 PRINT V$
220 PRINT "Phone 1:"
230 PRINT P$
240 PRINT W$
250 PRINT "Phone 2:"
260 PRINT Q$
270 PRINT X$
280 PRINT "Phone 3:"
290 PRINT R$
300 PRINT Y$
310 PRINT "Email 1:"
320 PRINT E$
330 PRINT Z$
340 PRINT "Email 2:"
350 PRINT F$
360 PRINT S$
370 PRINT "Email 3:"
380 PRINT G$
390 PRINT D$
400 PRINT "---------------------"
410 END
"""

    edit_name_bas = """100 PRINT "Enter new Name:"
110 INPUT N$
120 PRINT "Name updated."
130 END
"""

    edit_addr_bas = """100 PRINT "Edit Address Index (1-3)?"
110 INPUT I
120 IF I = 1 THEN GOTO 200
130 IF I = 2 THEN GOTO 300
140 IF I = 3 THEN GOTO 400
150 GOTO 500
200 PRINT "Enter Addr 1:"
210 INPUT A$
220 PRINT "Enter Type 1:"
230 INPUT T$
240 GOTO 500
300 PRINT "Enter Addr 2:"
310 INPUT B$
320 PRINT "Enter Type 2:"
330 INPUT U$
340 GOTO 500
400 PRINT "Enter Addr 3:"
410 INPUT C$
420 PRINT "Enter Type 3:"
430 INPUT V$
500 PRINT "Address updated."
510 END
"""

    edit_phon_bas = """100 PRINT "Edit Phone Index (1-3)?"
110 INPUT I
120 IF I = 1 THEN GOTO 200
130 IF I = 2 THEN GOTO 300
140 IF I = 3 THEN GOTO 400
150 GOTO 500
200 PRINT "Enter Phone 1:"
210 INPUT P$
220 PRINT "Enter Type 1:"
230 INPUT W$
240 GOTO 500
300 PRINT "Enter Phone 2:"
310 INPUT Q$
320 PRINT "Enter Type 2:"
330 INPUT X$
340 GOTO 500
400 PRINT "Enter Phone 3:"
410 INPUT R$
420 PRINT "Enter Type 3:"
430 INPUT Y$
500 PRINT "Phone updated."
510 END
"""

    edit_email_bas = """100 PRINT "Edit Email Index (1-3)?"
110 INPUT I
120 IF I = 1 THEN GOTO 200
130 IF I = 2 THEN GOTO 300
140 IF I = 3 THEN GOTO 400
150 GOTO 500
200 PRINT "Enter Email 1:"
210 INPUT E$
220 PRINT "Enter Type 1:"
230 INPUT Z$
240 GOTO 500
300 PRINT "Enter Email 2:"
310 INPUT F$
320 PRINT "Enter Type 2:"
330 INPUT S$
340 GOTO 500
400 PRINT "Enter Email 3:"
410 INPUT G$
420 PRINT "Enter Type 3:"
430 INPUT D$
500 PRINT "Email updated."
510 END
"""

    write_bas("tests/address_book/main.bas", main_bas)
    write_bas("tests/address_book/tui.bas", tui_bas)
    write_bas("tests/address_book/db.bas", db_bas)
    write_bas("tests/address_book/edit_name.bas", edit_name_bas)
    write_bas("tests/address_book/edit_addr.bas", edit_addr_bas)
    write_bas("tests/address_book/edit_phon.bas", edit_phon_bas)
    write_bas("tests/address_book/edit_email.bas", edit_email_bas)

    odl_content = """
.ROOT MAIN-TUI_REG-DB_REG-OTHER_REG
TUI_REG: .FCTR TUIDRAW
DB_REG: .FCTR DBVIEW
OTHER_REG: .FCTR EDITNAME,EDITADDR,EDITPHON,EDITEMAIL
"""
    with open("tests/address_book/addr.odl", "w") as f:
        f.write(odl_content)

    bas_files = [
        ("tests/address_book/main.bas", "tests/address_book/main.obj", ""),
        ("tests/address_book/tui.bas", "tests/address_book/tui.obj", "--module TUIDRAW"),
        ("tests/address_book/db.bas", "tests/address_book/db.obj", "--module DBVIEW"),
        ("tests/address_book/edit_name.bas", "tests/address_book/edit_name.obj", "--module EDITNAME"),
        ("tests/address_book/edit_addr.bas", "tests/address_book/edit_addr.obj", "--module EDITADDR"),
        ("tests/address_book/edit_phon.bas", "tests/address_book/edit_phon.obj", "--module EDITPHON"),
        ("tests/address_book/edit_email.bas", "tests/address_book/edit_email.obj", "--module EDITEMAIL")
    ]
    
    for src, obj, extra in bas_files:
        cmd = COMPILER_CMD.format(input=src, output=obj, extra=extra)
        subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')
        
    objs = " ".join([obj for _, obj, _ in bas_files])
    
    l_cmd = LINKER_CMD.format(inputs=objs, odl="tests/address_book/addr.odl", output="tests/address_book/app")
    subprocess.run(l_cmd, shell=True, check=True, executable='/bin/bash')
    
    # Simulate:
    # 1: View DB
    # 2: Edit Name -> "Jane"
    # 3: Edit Addr -> 1 -> "123 New St" -> "Home"
    # 4: Edit Phone -> 2 -> "555-1234" -> "Work"
    # 5: Edit Email -> 3 -> "test@test.com" -> "Personal"
    # 1: View DB
    # 6: Exit
    simulated_input = "1\n2\nJane\n3\n1\n123 New St\nHome\n4\n2\n555-1234\nWork\n5\n3\ntest@test.com\nPersonal\n1\n6\n"
    
    result = subprocess.run("./tests/address_book/app", input=simulated_input, shell=True, capture_output=True, text=True)
    assert result.returncode == 0
    
    out = result.stdout
    assert "Address Book TUI" in out
    assert "DATABASE VIEW" in out
    assert "Name updated." in out
    assert "Address updated." in out
    assert "Phone updated." in out
    assert "Email updated." in out
    assert "Exiting Address Book" in out
    
    # Check that updated values made it to global state!
    assert "Jane" in out
    assert "123 New St" in out
    assert "Home" in out
    assert "555-1234" in out
    assert "Work" in out
    assert "test@test.com" in out
    assert "Personal" in out
