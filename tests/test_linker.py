import os
import subprocess

COMPILER_CMD = "source .venv/bin/activate && python compiler/basicc.py {input} -o {output}"
LINKER_CMD = "source .venv/bin/activate && python compiler/basiclink.py {input} -o {output}"

def test_linker_executable():
    bas_content = "10 PRINT 100\\n20 END\\n"
    bas_file = "tests/test_link.bas"
    bobj_file = "tests/test_link.bobj"
    exe_file = "tests/test_link_app"
    
    # 1. Write the source file
    with open(bas_file, "w") as f:
        f.write(bas_content)
        
    # 2. Compile to .bobj
    c_cmd = COMPILER_CMD.format(input=bas_file, output=bobj_file)
    subprocess.run(c_cmd, shell=True, check=True, executable='/bin/bash')
    
    # 3. Link to standalone executable
    l_cmd = LINKER_CMD.format(input=bobj_file, output=exe_file)
    subprocess.run(l_cmd, shell=True, check=True, executable='/bin/bash')
    
    # 4. Run the executable and verify output
    assert os.path.exists(exe_file)
    assert os.access(exe_file, os.X_OK)
    
    result = subprocess.run(f"./{exe_file}", shell=True, capture_output=True, text=True)
    
    assert result.returncode == 0
    # Output should contain the initialization and the printed value
    assert "PRINT: 100" in result.stdout
    assert "VM Halt" in result.stdout

def test_linker_rms_execution():
    bas_content = """10 OPEN "DATABASE" AS FILE #1, INDEXED, PRIMARY KEY K$
20 PUT #1
30 CLOSE #1
40 END
"""
    bas_file = "tests/test_link_rms.bas"
    bobj_file = "tests/test_link_rms.bobj"
    exe_file = "tests/test_link_rms_app"
    
    with open(bas_file, "w") as f:
        f.write(bas_content)
        
    subprocess.run(COMPILER_CMD.format(input=bas_file, output=bobj_file), shell=True, check=True, executable='/bin/bash')
    subprocess.run(LINKER_CMD.format(input=bobj_file, output=exe_file), shell=True, check=True, executable='/bin/bash')
    
    result = subprocess.run(f"./{exe_file}", shell=True, capture_output=True, text=True)
    
    assert result.returncode == 0
    assert "RMS OPEN (INDEXED) channel 1 with SQLite backend" in result.stdout
    assert "RMS PUT (INDEXED) channel 1 to SQLite" in result.stdout

def test_linker_odl_parsing():
    odl_content = """
.ROOT MAIN-O1
O1: .FCTR SUB1-SUB2
"""
    bas_content = "10 PRINT 1\n20 END\n"
    odl_file = "tests/test.odl"
    bas_file = "tests/test_odl.bas"
    bobj_file = "tests/test_odl.bobj"
    exe_file = "tests/test_odl_app"
    
    with open(odl_file, "w") as f:
        f.write(odl_content)
    with open(bas_file, "w") as f:
        f.write(bas_content)
        
    subprocess.run(COMPILER_CMD.format(input=bas_file, output=bobj_file), shell=True, check=True, executable='/bin/bash')
    
    # Run linker with odl file
    l_cmd = f"source .venv/bin/activate && python compiler/basiclink.py {bobj_file} {odl_file} -o {exe_file}"
    result = subprocess.run(l_cmd, shell=True, check=True, capture_output=True, text=True, executable='/bin/bash')
    
    # Verify that the linker output says it parsed the ODL file
    assert "Parsed ODL File" in result.stdout
    assert "'ROOT': 'MAIN-O1'" in result.stdout
    assert "'O1': 'SUB1-SUB2'" in result.stdout

