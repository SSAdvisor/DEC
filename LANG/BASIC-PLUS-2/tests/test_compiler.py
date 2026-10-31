import os
import sys
import json
import subprocess
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER_CMD = f"{sys.executable} compiler/basicc.py {{input}} -o {{output}}"


@pytest.fixture(autouse=True)
def _chdir_root(monkeypatch):
    monkeypatch.chdir(ROOT_DIR)


def compile_and_load(bas_content, test_name):
    bas_file = f"tests/{test_name}.bas"
    obj_file = f"tests/{test_name}.obj"
    
    with open(bas_file, "w") as f:
        f.write(bas_content)
        
    cmd = COMPILER_CMD.format(input=bas_file, output=obj_file)
    result = subprocess.run(cmd, shell=True, capture_output=True, executable='/bin/bash')
    
    if result.returncode != 0:
        print(result.stdout.decode())
        print(result.stderr.decode())
        raise Exception(f"Compiler failed for {test_name}")
        
    with open(obj_file, "r") as f:
        obj = json.load(f)
        
    return obj

def test_basic_math():
    bas = "10 LET A = 5 + 10\n20 PRINT A\n30 END\n"
    obj = compile_and_load(bas, "math")
    bc = obj["bytecode"]
    assert 0x20 in bc # OP_ADD
    assert 0x13 in bc # OP_STORE_V
    assert 0x52 in bc or 0x50 in bc # OP_PRINT_CH or OP_PRINT

def test_rms_sequential():
    bas = """10 OPEN "DATA.TXT" FOR OUTPUT AS FILE #1
20 PUT #1
30 CLOSE #1
"""
    obj = compile_and_load(bas, "rms_seq")
    bc = obj["bytecode"]
    assert 0x60 in bc # OP_RMS_OPEN
    assert 0x62 in bc # OP_RMS_PUT
    assert 0x63 in bc # OP_RMS_CLOS

def test_rms_indexed():
    bas = """10 OPEN "DATA.IDX" AS FILE #2, INDEXED, PRIMARY KEY K$
20 GET #2, KEY K$
30 PUT #2
40 CLOSE #2
"""
    obj = compile_and_load(bas, "rms_idx")
    bc = obj["bytecode"]
    assert 0x60 in bc # OP_RMS_OPEN
    assert 0x61 in bc # OP_RMS_GET
    assert 0x62 in bc # OP_RMS_PUT
    assert 0x63 in bc # OP_RMS_CLOS
    
def test_string_literals():
    bas = "10 PRINT \"HELLO WORLD\"\n"
    obj = compile_and_load(bas, "strings")
    bc = obj["bytecode"]
    assert 0x12 in bc # OP_PUSH_S
    assert b"HELLO WORLD" in bytes(bc)
