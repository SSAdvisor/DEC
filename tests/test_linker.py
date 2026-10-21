import os
import sys
import subprocess

COMPILER_CMD = f"{sys.executable} compiler/basicc.py {{input}} -o {{output}}"
LINKER_CMD = f"{sys.executable} compiler/basiclink.py {{input}} -o {{output}}"

def test_linker_executable():
    bas_content = "10 PRINT 100\n20 END\n"
    bas_file = "tests/test_link.bas"
    obj_file = "tests/test_link.obj"
    exe_file = "tests/test_link_app"
    
    # 1. Write the source file
    with open(bas_file, "w") as f:
        f.write(bas_content)
        
    # 2. Compile to .obj
    c_cmd = COMPILER_CMD.format(input=bas_file, output=obj_file)
    subprocess.run(c_cmd, shell=True, check=True, executable='/bin/bash')
    
    # 3. Link to standalone executable
    l_cmd = LINKER_CMD.format(input=obj_file, output=exe_file)
    subprocess.run(l_cmd, shell=True, check=True, executable='/bin/bash')
    
    # 4. Run the executable and verify output
    assert os.path.exists(exe_file)
    assert os.access(exe_file, os.X_OK)
    
    result = subprocess.run(f"./{exe_file}", shell=True, capture_output=True, text=True)
    
    assert result.returncode == 0
    # Output should contain the initialization and the printed value
    assert "100" in result.stdout

def test_linker_rms_execution():
    bas_content = """10 OPEN "DATABASE" AS FILE #1, INDEXED, PRIMARY KEY K$
20 PUT #1
30 CLOSE #1
40 END
"""
    bas_file = "tests/test_link_rms.bas"
    obj_file = "tests/test_link_rms.obj"
    exe_file = "tests/test_link_rms_app"
    
    with open(bas_file, "w") as f:
        f.write(bas_content)
        
    subprocess.run(COMPILER_CMD.format(input=bas_file, output=obj_file), shell=True, check=True, executable='/bin/bash')
    subprocess.run(LINKER_CMD.format(input=obj_file, output=exe_file), shell=True, check=True, executable='/bin/bash')
    
    result = subprocess.run(f"./{exe_file}", shell=True, capture_output=True, text=True)
    
    assert result.returncode == 0

def test_linker_overlays():
    odl_content = """
.ROOT MAIN-O1
O1: .FCTR FUNC1,FUNC2
"""
    main_bas = '10 PRINT 1\n20 CALL "FUNC1"\n30 CALL "FUNC2"\n40 END\n'
    func1_bas = '10 PRINT 11\n20 END\n'
    func2_bas = '10 PRINT 22\n20 END\n'
    
    with open("tests/main.bas", "w") as f: f.write(main_bas)
    with open("tests/func1.bas", "w") as f: f.write(func1_bas)
    with open("tests/func2.bas", "w") as f: f.write(func2_bas)
    with open("tests/test.odl", "w") as f: f.write(odl_content)
    
    # Compile
    subprocess.run(f"{sys.executable} compiler/basicc.py tests/main.bas -o tests/main.obj", shell=True, check=True, executable='/bin/bash')
    subprocess.run(f"{sys.executable} compiler/basicc.py tests/func1.bas -o tests/func1.obj --module FUNC1", shell=True, check=True, executable='/bin/bash')
    subprocess.run(f"{sys.executable} compiler/basicc.py tests/func2.bas -o tests/func2.obj --module FUNC2", shell=True, check=True, executable='/bin/bash')
    
    # Link
    l_cmd = f"{sys.executable} compiler/basiclink.py tests/main.obj tests/func1.obj tests/func2.obj tests/test.odl -o tests/overlay_app"
    subprocess.run(l_cmd, shell=True, check=True, executable='/bin/bash')
    
    # Run
    result = subprocess.run("./tests/overlay_app", shell=True, capture_output=True, text=True)
    assert result.returncode == 0
    
    assert "1" in result.stdout
    assert "11" in result.stdout
    assert "22" in result.stdout

