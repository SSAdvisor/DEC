import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(APP_DIR, "src", "hamurabi.bas")
BUILD_DIR = os.path.join(APP_DIR, "build")
BIN_DIR = os.path.join(APP_DIR, "bin")
OBJ_FILE = os.path.join(BUILD_DIR, "hamurabi.obj")
EXE_FILE = os.path.join(BIN_DIR, "hamurabi")

def test_hamurabi_build():
    """Verify that hamurabi.bas compiles with basicc and links with basiclink cleanly."""
    res_clean = subprocess.run(["make", "-C", APP_DIR, "clean"], capture_output=True, text=True)
    assert res_clean.returncode == 0

    res_build = subprocess.run(["make", "-C", APP_DIR, "build"], capture_output=True, text=True)
    assert res_build.returncode == 0, f"Build failed:\nSTDOUT:\n{res_build.stdout}\nSTDERR:\n{res_build.stderr}"
    assert os.path.isfile(OBJ_FILE), f"Object file {OBJ_FILE} not found"
    assert os.path.isfile(EXE_FILE), f"Executable {EXE_FILE} not found"
    assert os.access(EXE_FILE, os.X_OK), f"Executable {EXE_FILE} is not executable"

def test_hamurabi_negative_input():
    """Verify handling of invalid negative steward inputs."""
    res = subprocess.run(
        [EXE_FILE],
        input="-1\n",
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res.returncode == 0
    assert "HAMURABI" in res.stdout
    assert "I CANNOT DO WHAT YOU WISH" in res.stdout
    assert "GET YOURSELF ANOTHER STEWARD" in res.stdout

def test_hamurabi_starvation_impeachment():
    """Verify starvation and impeachment logic when food ration is zero."""
    # Input vector:
    # Buy acres: 0
    # Sell acres: 0
    # Feed people: 0
    # Plant seed: 0
    input_data = "0\n0\n0\n0\n"
    res = subprocess.run(
        [EXE_FILE],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res.returncode == 0
    assert "YOU STARVED" in res.stdout
    assert "BEEN IMPEACHED AND THROWN OUT OF OFFICE" in res.stdout
    assert "NATIONAL FINK" in res.stdout
