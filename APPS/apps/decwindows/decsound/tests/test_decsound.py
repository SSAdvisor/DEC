import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_DECSOUND = APP_DIR / "bin" / "decsound"
BIN_DXSOUND = APP_DIR / "bin" / "dxsound"


def run_decsound(commands: str, binary: Path = BIN_DECSOUND, cwd: Path = APP_DIR) -> str:
    proc = subprocess.run(
        [str(binary)],
        input=commands + "\n",
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )
    assert proc.returncode == 0, f"decsound failed: {proc.stderr}"
    return proc.stdout


def test_01_banner_and_help():
    out = run_decsound("HELP\nEXIT")
    assert "DECwindows DECsound V3.0 (DECW$SOUND / dxsound)" in out
    assert "--- DECwindows DECsound V3.0 Commands ---" in out
    assert "WAVEFORM [id] / VU / INSPECT" in out
    assert "DECwindows DECsound V3.0 session terminated." in out


def test_02_sample_and_show_status():
    out = run_decsound("SAMPLE; SHOW; EXIT")
    assert "[Loaded Sample DECsound Library: 6 audio clips (Active: VAX_BOOT_CHIME.AU)]" in out
    assert "Output Device  : SPEAKER (Internal BBA)  |  Volume : 80%" in out
    assert "Input Source   : MICROPHONE (DECaudio Handset)  |  Gain   : 75%" in out
    assert "Active Clip    : #1 (VAX_BOOT_CHIME.AU)" in out
    assert "Total Clips    : 6 audio clips in library" in out


def test_03_list_all_and_filtered_by_format():
    out = run_decsound("SAMPLE; LIST; LIST PCM16; EXIT")
    assert "VAX_BOOT_CHIME.AU" in out
    assert "ALPHA_INTRO.AU" in out
    assert "Total audio clips listed: 6" in out
    assert "Total audio clips listed: 2" in out


def test_04_play_by_id_and_by_name():
    out = run_decsound("SAMPLE; PLAY 3; PLAYCDA_VOICENOTE; PLAY CDA_VOICENOTE; EXIT")
    assert "[Playing Clip #3: ALPHA_INTRO.AU (PCM16-11KHZ, 18s) -> SPEAKER (Internal BBA) @ Vol 80%]" in out
    assert "Annotation : Ken Olsen & Bob Supnik Alpha AXP Launch Voice Note" in out
    assert "[Playing Clip #5: CDA_VOICENOTE.AU (MULAW-8KHZ, 12s)" in out


def test_05_record_new_clip():
    out = run_decsound(
        "SAMPLE; RECORD OSF1_NOTE.AU|MULAW-8KHZ|10|84|DEC OSF/1 Kernel Review Voice Memo; PLAY 7; EXIT"
    )
    assert "[Recorded Clip #7: OSF1_NOTE.AU (MULAW-8KHZ, 10s) from MICROPHONE (DECaudio Handset) @ Gain 75%]" in out
    assert "Annotation : DEC OSF/1 Kernel Review Voice Memo" in out


def test_06_delete_clip():
    out = run_decsound("SAMPLE; DELETE 2; LIST; EXIT")
    assert "[Deleted Audio Clip #2: NEWMAIL_BELL.AU]" in out
    assert "Total audio clips listed: 5" in out


def test_07_waveform_and_codec_inspector():
    out = run_decsound("SAMPLE; WAVEFORM 3; WAVEFORM 1; EXIT")
    assert "=== DECsound Waveform & Codec Inspector: ALPHA_INTRO.AU ===" in out
    assert "Encoding Codec : PCM16-11KHZ (22 KB/sec)" in out
    assert "Duration / Size: 18 sec  |  Buffer Size: 396 KB" in out
    assert "Signal Audit: CLEAN (No Digital Clipping Detected)" in out
    assert "=== DECsound Waveform & Codec Inspector: VAX_BOOT_CHIME.AU ===" in out
    assert "Duration / Size: 4 sec  |  Buffer Size: 32 KB" in out


def test_08_volume_gain_and_hardware_routing():
    out = run_decsound("SAMPLE; VOLUME 95; GAIN 60; OUTPUT HEADPHONE; INPUT LINE-IN; SHOW; EXIT")
    assert "[Playback Volume set to 95%]" in out
    assert "[Recording Gain set to 60%]" in out
    assert "[DECaudio Output routed to: HEADPHONE (Front Jack)]" in out
    assert "[DECaudio Input routed to: LINE-IN (Auxiliary)]" in out
    assert "Output Device  : HEADPHONE (Front Jack)  |  Volume : 95%" in out


def test_09_search_audio_clips():
    out = run_decsound("SAMPLE; SEARCH QUORUM; SEARCH PCM16; EXIT")
    assert "Clip #4 [CLUSTER_ALERT.AU | MULAW-8KHZ]: VAXcluster Quorum Transition Spoken Alert" in out
    assert "Total matching clips: 1" in out
    assert "Total matching clips: 2" in out


def test_10_display_and_export_motif_window(tmp_path):
    win_file = tmp_path / "decsound_win.txt"
    out = run_decsound(f"SAMPLE; DISPLAY; EXPORT {win_file}; EXIT")
    assert "| [=] DECwindows DECsound (dxsound) - VAX_BOOT_CHIME.AU [MULAW-8KHZ]         [v][^] |" in out
    assert "|   [ (o) REC ]    [ |> PLAY ]    [ || PAUSE ]    [ [] STOP ]    [ << ] [ >> ]|" in out
    assert f"[DECsound window exported to {win_file}]" in out
    assert win_file.exists()
    content = win_file.read_text()
    assert "Voice Note: VAXstation 4000 BBA Power-On Self-Test Chime" in content
    assert "Out: SPEAKER (Internal BBA) | Vol: 80% | Gain: 75%" in content


def test_11_save_clear_and_load_persistence(tmp_path):
    snd_file = tmp_path / "decsound_lib.snd"
    out = run_decsound(f"SAMPLE; SAVE {snd_file}; CLEAR; SHOW; LOAD {snd_file}; SHOW; EXIT")
    assert f"[Saved 6 audio clips to {snd_file}]" in out
    assert "[DECsound clip library cleared]" in out
    assert f"[Loaded 6 audio clips from {snd_file}]" in out
    assert "Total Clips    : 6 audio clips in library" in out


def test_12_command_line_batch_mode():
    proc = subprocess.run(
        [str(BIN_DECSOUND), "SAMPLE; WAVEFORM 1; EXIT"],
        text=True,
        capture_output=True,
        cwd=str(APP_DIR),
        timeout=10,
    )
    assert proc.returncode == 0
    assert "DECsound Waveform & Codec Inspector: VAX_BOOT_CHIME.AU" in proc.stdout


def test_13_error_handling_and_validation():
    out = run_decsound("SAMPLE; VOLUME 150; PLAY NO_SUCH_CLIP; DELETE 99; EXIT")
    assert "%DECSOUND-E-RANGE, Volume must be 0..100." in out
    assert "%DECSOUND-E-NOTFND, Audio clip not found: NO_SUCH_CLIP" in out
    assert "%DECSOUND-E-INVID, Invalid clip number." in out


def test_14_dxsound_symlink_execution():
    assert BIN_DXSOUND.exists() and os.access(BIN_DXSOUND, os.X_OK)
    out = run_decsound("SAMPLE; PLAY 1; EXIT", binary=BIN_DXSOUND)
    assert "DECwindows DECsound V3.0" in out
    assert "[Playing Clip #1: VAX_BOOT_CHIME.AU" in out
