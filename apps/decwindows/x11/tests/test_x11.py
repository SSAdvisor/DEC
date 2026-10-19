import ctypes
import os
import subprocess
from pathlib import Path
import pytest

X11_DIR = Path(__file__).resolve().parents[1]
DECW_DIR = X11_DIR.parent
LIB_SO = X11_DIR / "lib" / "libdecw_x11.so"
LIB_A = X11_DIR / "lib" / "libdecw_x11.a"
DECW_X11_BIN = X11_DIR / "bin" / "decw_x11"
DECWX11_BIN = X11_DIR / "bin" / "decwx11"
DXSESSION_BIN = X11_DIR / "bin" / "dxsession"

ALL_DECW_APPS = [
    ("decterm", "decterm"),
    ("bookreader", "bookreader"),
    ("calendar", "calendar"),
    ("cardfiler", "cardfiler"),
    ("cdaviewer", "cdaviewer"),
    ("calculator", "calculator"),
    ("clock", "clock"),
    ("decsound", "decsound"),
    ("dxmail", "dxmail"),
    ("fileview", "fileview"),
    ("notepad", "notepad"),
]

DECW_MAX_LINES = 128
DECW_LINE_LEN = 256


def get_x11_env(**extra):
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":10")
    path_dirs = [str(X11_DIR / "bin")]
    for app_dir, _ in ALL_DECW_APPS:
        path_dirs.append(str(DECW_DIR / app_dir / "bin"))
    env["PATH"] = ":".join(path_dirs) + ":" + env.get("PATH", "")
    env.update(extra)
    return env


def test_01_build_artifacts_exist():
    assert LIB_SO.exists(), "libdecw_x11.so shared library must exist"
    assert LIB_A.exists(), "libdecw_x11.a static archive must exist"
    assert DECW_X11_BIN.exists(), "decw_x11 executable must exist"
    assert DECWX11_BIN.exists(), "decwx11 BASIC-PLUS-2 Session Manager must exist"
    assert DXSESSION_BIN.is_symlink(), "dxsession must be a symlink to decwx11"


def test_02_ctypes_shared_library_api(tmp_path):
    lib = ctypes.CDLL(str(LIB_SO))
    lib.decw_x11_version.restype = ctypes.c_char_p
    ver = lib.decw_x11_version().decode("utf-8")
    assert "DECwindows X11/Motif 1.1 Interfacing Library V3.0" in ver

    # Test decw_x11_probe_display via ctypes
    lib.decw_x11_probe_display.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
    lib.decw_x11_probe_display.restype = ctypes.c_int
    info_buf = ctypes.create_string_buffer(256)
    dpy_name = os.environ.get("DISPLAY", ":10").encode("utf-8")
    rc_probe = lib.decw_x11_probe_display(dpy_name, info_buf, 256)
    assert rc_probe == 0
    assert b"X11 Display:" in info_buf.value

    # Test decw_x11_load_frame via ctypes
    frame_file = tmp_path / "sample_frame.txt"
    frame_file.write_text(
        "+----------------------------------------------------------------------------+\n"
        "| [X] DECwindows TestApp - WORK::TEST                       [_][#]           |\n"
        "+----------------------------------------------------------------------------+\n"
        "| File  Edit  View  Options                                             Help |\n"
        "+----------------------------------------------------------------------------+\n"
        "| [Sample] [Show] [Refresh]                                                  |\n"
        "+----------------------------------------------------------------------------+\n"
        "| Line 1: Hello from DECwindows X11 Interfacing Library                      |\n"
        "| Line 2: OSF/Motif 1.1 3D beveled frame parser test                         |\n"
        "+----------------------------------------------------------------------------+\n"
        "| Status: Ready                                                              |\n"
        "+----------------------------------------------------------------------------+\n"
    )

    LineArrayType = (ctypes.c_char * DECW_LINE_LEN) * DECW_MAX_LINES
    lines_buf = LineArrayType()
    lib.decw_x11_load_frame.argtypes = [ctypes.c_char_p, ctypes.POINTER(LineArrayType), ctypes.c_int]
    lib.decw_x11_load_frame.restype = ctypes.c_int
    line_cnt = lib.decw_x11_load_frame(str(frame_file).encode("utf-8"), ctypes.byref(lines_buf), DECW_MAX_LINES)
    assert line_cnt == 12
    assert b"DECwindows TestApp" in bytes(lines_buf[1])


def test_03_decw_x11_cli_probe_and_check_gui():
    env = get_x11_env()
    res_ver = subprocess.run([str(DECW_X11_BIN), "--version"], env=env, capture_output=True, text=True, check=True)
    assert "DECwindows X11/Motif 1.1 Interfacing Library V3.0" in res_ver.stdout

    res_probe = subprocess.run([str(DECW_X11_BIN), "--probe"], env=env, capture_output=True, text=True)
    assert res_probe.returncode == 0
    assert "X11 Display:" in res_probe.stdout

    # Check --check-gui respects DECW_FORCE_CLI and DECW_FORCE_X11
    env_cli = get_x11_env(DECW_FORCE_CLI="1")
    res_cli = subprocess.run([str(DECW_X11_BIN), "--check-gui"], env=env_cli, capture_output=True, text=True)
    assert res_cli.returncode == 1

    env_x11 = get_x11_env(DECW_FORCE_X11="1")
    res_x11 = subprocess.run([str(DECW_X11_BIN), "--check-gui"], env=env_x11, capture_output=True, text=True)
    assert res_x11.returncode == 0


def test_04_decw_x11_window_render_and_synthetic_button_callback():
    env = get_x11_env(DECW_X11_AUTOCLOSE_MS="150")
    res = subprocess.run(
        [
            str(DECW_X11_BIN),
            "--app",
            "calculator",
            "--autoclose",
            "150",
            "--test-interact",
            "--verify",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "[DECwindows X11 Engine] Window 'DECwindows Calculator" in res.stdout
    assert "Motif buttons" in res.stdout


def test_05_decwx11_session_manager_commands(tmp_path):
    export_file = tmp_path / "session_frame.txt"
    env = get_x11_env(DECW_FORCE_CLI="1", DECW_X11_AUTOCLOSE_MS="80")
    cmds = "\n".join(
        [
            "HELP",
            "SHOW",
            "APPS",
            "PROBE",
            "DISPLAY",
            f"EXPORT {export_file}",
            "EXIT",
        ]
    ) + "\n"
    res = subprocess.run(
        [str(DECWX11_BIN)],
        input=cmds,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "DECwindows V3.0 - X11 Protocol & Motif Session Manager" in res.stdout
    assert "DECterm" in res.stdout
    assert "Notepad" in res.stdout
    assert "X11 Display:" in res.stdout
    assert export_file.exists()
    assert "DECwindows Session Manager" in export_file.read_text()


def test_06_dxsession_symlink_and_x11_launch():
    env = get_x11_env(DECW_X11_AUTOCLOSE_MS="80")
    res = subprocess.run(
        [str(DXSESSION_BIN), "LAUNCH clock"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "[DECwindows X11 Engine] Window 'DECwindows Clock" in res.stdout


@pytest.mark.parametrize("app_dir,app_bin", ALL_DECW_APPS)
def test_07_all_11_apps_autolaunch_x11_and_cli_override(app_dir, app_bin):
    bin_path = DECW_DIR / app_dir / "bin" / app_bin
    assert bin_path.exists(), f"Binary {bin_path} must exist"

    # 1. Default auto-launch when DECW_FORCE_X11=1 (simulating interactive TTY + DISPLAY)
    env_auto = get_x11_env(DECW_FORCE_X11="1", DECW_X11_AUTOCLOSE_MS="60")
    res_auto = subprocess.run(
        [str(bin_path)],
        env=env_auto,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res_auto.returncode == 0
    assert "[DECwindows X11 Engine] Window" in res_auto.stdout

    # 2. --cli flag overrides X11 auto-launch and enters standard CLI/REPL mode
    res_cli = subprocess.run(
        [str(bin_path), "--cli"],
        input="HELP\nEXIT\n",
        env=env_auto,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res_cli.returncode == 0
    assert "[DECwindows X11 Engine] Window" not in res_cli.stdout
    assert "Commands" in res_cli.stdout or "HELP" in res_cli.stdout

    # 3. Interactive X11 REPL command launches X11 window on demand
    env_repl = get_x11_env(DECW_FORCE_CLI="1", DECW_X11_AUTOCLOSE_MS="60")
    res_repl = subprocess.run(
        [str(bin_path)],
        input="SAMPLE\nX11\nEXIT\n",
        env=env_repl,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res_repl.returncode == 0
    assert "[DECwindows X11 Engine] Window" in res_repl.stdout
