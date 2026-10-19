import os
import subprocess
import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(APP_DIR, "bin")
CALENDAR_BIN = os.path.join(BIN_DIR, "calendar")
DXCALENDAR_BIN = os.path.join(BIN_DIR, "dxcalendar")


@pytest.fixture(scope="module", autouse=True)
def build_calendar():
    """Ensure calendar and its dxcalendar alias are built before running tests."""
    res = subprocess.run(["make", "build"], cwd=APP_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"Build failed:\n{res.stdout}\n{res.stderr}"
    assert os.path.isfile(CALENDAR_BIN)
    assert os.path.exists(DXCALENDAR_BIN)


def run_calendar(commands, cwd=None):
    """Run calendar with semicolon-chained commands."""
    cmd_str = "; ".join(commands) if isinstance(commands, list) else commands
    res = subprocess.run(
        [CALENDAR_BIN, cmd_str],
        cwd=cwd or APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0, f"Execution failed:\n{res.stdout}\n{res.stderr}"
    return res.stdout


def test_help_and_commands():
    """Verify HELP displays Calendar command documentation."""
    out = run_calendar(["HELP", "EXIT"])
    assert "DECwindows Calendar Time & Schedule Manager Commands" in out
    assert "MONTH / GRID" in out
    assert "CHECK / CONFLICTS" in out


def test_sample_and_list():
    """Verify SAMPLE loads the 6 October 1991 appointments and LIST displays them."""
    out = run_calendar(["SAMPLE", "LIST", "EXIT"])
    assert "[Sample DECwindows Calendar loaded: 6 appointments for October 1991]" in out
    assert "DECwindows Calendar Full Schedule (6 appointments)" in out
    assert "VAX/VMS V5.5 Release Engineering Sign-off" in out
    assert "Alpha AXP 64-Bit Architecture Briefing" in out


def test_month_grid_markers():
    """Verify MONTH renders the calendar grid with * markers on booked dates."""
    out = run_calendar(["SAMPLE", "MONTH", "EXIT"])
    assert "DECwindows Calendar Monthly View - 1991-10 (Maynard Engineering (ZKO))" in out
    assert "18*" in out
    assert "21*" in out
    assert "24*" in out
    assert "28*" in out


def test_date_and_day_agenda():
    """Verify DATE selection and DAY agenda filtering."""
    out = run_calendar(["SAMPLE", "DATE 1991-10-21", "DAY", "EXIT"])
    assert "[Active calendar date set to 1991-10-21]" in out
    assert "DECwindows Calendar Daily Agenda for 1991-10-21" in out
    assert "DECUS Fall Symposium Keynote Preparation (Anaheim)" in out
    assert "1 appointment(s) scheduled on 1991-10-21" in out


def test_add_appointment():
    """Verify ADD schedules a new appointment with time, duration, and alarm."""
    out = run_calendar([
        "SAMPLE",
        "ADD 1991-10-18|16:30|45|ON|DECnet Phase V Architecture Review",
        "DAY 1991-10-18",
        "EXIT",
    ])
    assert "[Added Appointment #7 on 1991-10-18 at 16:30 (45m, Alarm:ON): DECnet Phase V Architecture Review]" in out
    assert "4 appointment(s) scheduled on 1991-10-18" in out


def test_delete_appointment():
    """Verify DELETE cancels and removes an appointment."""
    out = run_calendar(["SAMPLE", "DELETE 2", "SHOW", "EXIT"])
    assert "[Cancelled Appointment #2: DECwindows XUI to OSF/Motif Toolkit Porting Review]" in out
    assert "Total Appointments:     5 / 40 entries" in out


def test_alarm_toggle_and_alarms_list():
    """Verify ALARM ON|OFF toggles reminders and ALARMS lists active alarms."""
    out = run_calendar(["SAMPLE", "ALARM 3 ON", "ALARM 1 OFF", "ALARMS", "EXIT"])
    assert "[Appointment #3 alarm set to ON" in out
    assert "[Appointment #1 alarm set to OFF" in out
    assert "Total active alarms: 4" in out


def test_check_conflicts_clean_and_overlapping():
    """Verify CHECK detects double-booked timeslot conflicts."""
    out_clean = run_calendar(["SAMPLE", "CHECK", "EXIT"])
    assert "[Audit PASSED: No overlapping appointment timeslots detected]" in out_clean

    out_conf = run_calendar([
        "SAMPLE",
        "ADD 1991-10-18|09:00|30|ON|Overlapping Staff Sync",
        "CHECK",
        "EXIT",
    ])
    assert "[CONFLICT] 1991-10-18 09:00: Appt #1 overlaps Appt #7" in out_conf
    assert "[Audit WARNING: 1 double-booked timeslot conflict(s) detected]" in out_conf


def test_search_appointments():
    """Verify SEARCH finds appointments by keyword across date, time, and description."""
    out = run_calendar(["SAMPLE", "SEARCH VAXcluster", "EXIT"])
    assert "DECwindows Calendar Search Results for 'VAXcluster'" in out
    assert "[Match #1] #6 1991-10-28 16:00 - VAXcluster CI780 Star Coupler Maintenance Window" in out
    assert "Total matching appointments: 1" in out


def test_display_motif_window():
    """Verify DISPLAY renders the Motif/XUI Calendar window."""
    out = run_calendar(["SAMPLE", "DISPLAY", "EXIT"])
    assert "| [=] DECwindows Calendar - Maynard Engineering (ZKO)" in out
    assert "|  File    Edit    View    Entry    Customize    Help" in out
    assert "| Selected Day: 1991-10-18   [<< Prev Day] [Today] [Next Day >>]" in out
    assert "| 09:00 | [ON] VAX/VMS V5.5 Release Engineering Sign-off (ZKO2-3/Q18)" in out


def test_display_export_to_file(tmp_path):
    """Verify DISPLAY ON <file> exports the rendered Calendar window to a file."""
    out_file = tmp_path / "calendar_view.txt"
    out = run_calendar(["SAMPLE", f"DISPLAY ON {out_file}", "EXIT"], cwd=str(tmp_path))
    assert f"[Calendar window exported to {out_file}]" in out
    assert out_file.is_file()
    content = out_file.read_text()
    assert "DECwindows Calendar - Maynard Engineering (ZKO)" in content
    assert "[Date: 1991-10-18] [Total Entries: 6]" in content


def test_save_clear_and_load_calendar(tmp_path):
    """Verify SAVE, CLEAR, and LOAD preserve all appointments."""
    cal_file = tmp_path / "schedule.dat"
    out = run_calendar([
        "SAMPLE",
        f"SAVE {cal_file}",
        "CLEAR",
        f"LOAD {cal_file}",
        "SHOW",
        "EXIT",
    ], cwd=str(tmp_path))
    assert f"[Saved 6 appointment(s) to {cal_file}]" in out
    assert "[Calendar appointments cleared]" in out
    assert f"[Loaded 6 appointment(s) from {cal_file}]" in out
    assert "Total Appointments:     6 / 40 entries" in out


def test_error_handling_empty_and_invalid_id():
    """Verify graceful error handling when calendar is empty or ID is invalid."""
    out = run_calendar(["CLEAR", "LIST", "SAMPLE", "DELETE 99", "EXIT"])
    assert "CALENDAR: No appointments scheduled. Use SAMPLE, ADD, or LOAD first." in out
    assert "CALENDAR: Invalid appointment ID." in out


def test_dxcalendar_alias_execution():
    """Verify the dxcalendar symlink alias executes Calendar."""
    res = subprocess.run(
        [DXCALENDAR_BIN, "SAMPLE; SHOW; EXIT"],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "DECwindows Calendar V3.0 - Schedule & Time Manager Status" in res.stdout
