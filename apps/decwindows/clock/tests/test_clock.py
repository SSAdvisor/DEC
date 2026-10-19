import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_CLOCK = APP_DIR / "bin" / "clock"
BIN_DXCLOCK = APP_DIR / "bin" / "dxclock"


def run_clock(commands: str, binary: Path = BIN_CLOCK, cwd: Path = APP_DIR) -> str:
    proc = subprocess.run(
        [str(binary)],
        input=commands + "\n",
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )
    assert proc.returncode == 0, f"clock failed: {proc.stderr}"
    return proc.stdout


def test_01_banner_and_help():
    out = run_clock("HELP\nEXIT")
    assert "DECwindows Clock V3.0 (DECW$CLOCK / dxclock)" in out
    assert "--- DECwindows Clock V3.0 Commands ---" in out
    assert "ZONES / WORLD / ADDZONE" in out
    assert "DECwindows Clock V3.0 session terminated." in out


def test_02_sample_and_show_status():
    out = run_clock("SAMPLE; SHOW; EXIT")
    assert "[Loaded Sample DECwindows Clock: 14:30:00 on TUE 19-OCT-1993 (6 DEC World Sites)]" in out
    assert "Current Time   : 14:30:00 (24-Hour (Military))" in out
    assert "Current Date   : TUE 19-OCT-1993  |  Zone: EST (UTC-5 Maynard MLO / Nashua ZKO)" in out
    assert "Clock Face     : BOTH  |  Chime: ON (Hourly Bell)" in out
    assert "Alarm Status   : ON @ 15:00 - VAXcluster Quorum & Backup Window" in out


def test_03_settime_setdate_and_validation():
    out = run_clock("SETTIME 09:05:30; SETDATE WED 20-OCT-1993; SETTIME 25:00; SHOW; EXIT")
    assert "[Workstation Clock set to 09:05:30]" in out
    assert "[Workstation Date Banner: WED 20-OCT-1993]" in out
    assert "%CLOCK-E-INVTIME, Hour must be 0..23." in out
    assert "Current Time   : 09:05:30" in out


def test_04_format_12_and_24_hour():
    out = run_clock("SAMPLE; FORMAT 12; SETTIME 00:15:00; TIME; FORMAT 24; EXIT")
    assert "[Clock Digital Format set to 12-Hour -> 02:30:00 PM]" in out
    assert "Current Time: 12:15:00 AM" in out
    assert "[Clock Digital Format set to 24-Hour -> 00:15:00]" in out


def test_05_tick_chime_and_alarm_trigger():
    out = run_clock("SAMPLE; TICK 30; EXIT")
    assert "[CHIME! Hourly Bell Ring at 15:00]" in out
    assert "[ALARM! Bell Ring at 15:0 - VAXcluster Quorum & Backup Window]" in out
    assert "[Clock advanced 30 min(s) -> 15:00:00]" in out


def test_06_alarm_and_chime_configuration():
    out = run_clock("SAMPLE; ALARM 16:45|Alpha OSF/1 Build Freeze; CHIME OFF; ALARM OFF; SHOW; EXIT")
    assert "[Alarm Set for 16:45 (ENABLED) : Alpha OSF/1 Build Freeze]" in out
    assert "[Hourly Chime set to: OFF]" in out
    assert "[Alarm Bell DISABLED]" in out
    assert "Alarm Status   : OFF @ 16:45 - Alpha OSF/1 Build Freeze" in out


def test_07_face_mode_selection():
    out = run_clock("SAMPLE; FACE ANALOG; SHOW; FACE DIGITAL; SHOW; EXIT")
    assert "[Clock Face Mode set to: ANALOG]" in out
    assert "Clock Face     : ANALOG" in out
    assert "[Clock Face Mode set to: DIGITAL]" in out


def test_08_world_zones_and_addzone():
    out = run_clock("SAMPLE; ADDZONE SYD|Sydney Engineering Center|10; ZONES; EXIT")
    assert "[Added World Clock Site #7: SYD (Sydney Engineering Center, UTC 10)]" in out
    assert "MLO  | Maynard Mill, MA (HQ)        | UTC-5      | 14:30" in out
    assert "SRC  | Palo Alto Systems Research   | UTC-8      | 11:30" in out
    assert "REO  | Reading Engineering, UK      | UTC+0      | 19:30" in out
    assert "TKO  | Tokyo Engineering Center     | UTC+9      | 04:30" in out
    assert "SYD  | Sydney Engineering Center    | UTC+10     | 05:30" in out
    assert "Total world sites: 7" in out


def test_09_analog_dial_rendering():
    out = run_clock("SAMPLE; DIAL; EXIT")
    assert "Analog Hands : Hour->02  Min->30" in out
    assert "Digital Time : 14:30:00" in out
    assert "Date Banner  : TUE 19-OCT-1993" in out


def test_10_display_and_export_motif_window(tmp_path):
    win_file = tmp_path / "clock_win.txt"
    out = run_clock(f"SAMPLE; DISPLAY; EXPORT {win_file}; EXIT")
    assert "| [=] DECwindows Clock (dxclock) - TUE 19-OCT-1993 [BOTH]                   [v][^] |" in out
    assert "| File  Settings  Alarm  World-Zones  Help                                   |" in out
    assert f"[Clock window exported to {win_file}]" in out
    assert win_file.exists()
    content = win_file.read_text()
    assert "Digital Readout: 14:30:00 | Date: TUE 19-OCT-1993 | Alarm: 15:00" in content
    assert "Alarm Msg: VAXcluster Quorum & Backup Window" in content


def test_11_save_clear_and_load_persistence(tmp_path):
    cfg_file = tmp_path / "clock_cfg.clk"
    out = run_clock(f"SAMPLE; SAVE {cfg_file}; CLEAR; SHOW; LOAD {cfg_file}; SHOW; EXIT")
    assert f"[Saved DECwindows Clock configuration to {cfg_file}]" in out
    assert "[Clock reset to 00:00:00 and alarm cleared]" in out
    assert f"[Loaded DECwindows Clock configuration from {cfg_file} (Time: 14:30:00)]" in out
    assert "Alarm Status   : ON @ 15:00 - VAXcluster Quorum & Backup Window" in out


def test_12_command_line_batch_mode():
    proc = subprocess.run(
        [str(BIN_CLOCK), "SAMPLE; ZONES; EXIT"],
        text=True,
        capture_output=True,
        cwd=str(APP_DIR),
        timeout=10,
    )
    assert proc.returncode == 0
    assert "DEC Worldwide Engineering Timezones" in proc.stdout


def test_13_error_handling_invalid_command():
    out = run_clock("BADCMD; SETTIME 1200; ADDZONE BAD; EXIT")
    assert "%CLOCK-E-INVCMD, Unrecognized command: BADCMD" in out
    assert "%CLOCK-E-SYNTAX, Usage: SETTIME <HH:MM[:SS]>" in out
    assert "%CLOCK-E-SYNTAX, Usage: ADDZONE <site|location|utc_offset>" in out


def test_14_dxclock_symlink_execution():
    assert BIN_DXCLOCK.exists() and os.access(BIN_DXCLOCK, os.X_OK)
    out = run_clock("SAMPLE; DIAL; EXIT", binary=BIN_DXCLOCK)
    assert "DECwindows Clock V3.0" in out
    assert "Analog Hands : Hour->02  Min->30" in out
