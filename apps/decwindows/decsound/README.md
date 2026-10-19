# DECwindows DECsound V3.0 (`DECW$SOUND` / `dxsound`)

**DECwindows DECsound V3.0** is a faithful native DEC BASIC-PLUS-2 implementation of the Digital Equipment Corporation DECwindows workstation audio clip recorder, player, waveform inspector, and voice annotation manager (`DECW$SOUND` on OpenVMS VAX/Alpha and `dxsound` on ULTRIX and DEC OSF/1 with DECaudio / BBA Baseband Audio, 1990–1995).

---

## Features

- **DECaudio Sample Library (`SAMPLE` / `DEMO`)**:
  - Loads 6 classic DEC workstation audio clips (`VAX_BOOT_CHIME.AU`, `NEWMAIL_BELL.AU`, `ALPHA_INTRO.AU`, `CLUSTER_ALERT.AU`, `CDA_VOICENOTE.AU`, and `DECUS_THEME.AU`) encoded in 8 kHz ITU-T G.711 mu-law (`MULAW-8KHZ`) and 11 kHz 16-bit PCM (`PCM16-11KHZ`).
- **Audio Clip Library & Format Filtering (`LIST [format]` / `CLIPS` / `DIR`)**:
  - Lists all audio clips or filters by encoding codec (`MULAW-8KHZ`, `PCM16-11KHZ`) showing Clip #, Filename, Codec, Duration (sec), Peak Amplitude (%), and Voice Annotation transcript.
- **Playback, Recording & Deletion (`PLAY [id|name]`, `RECORD <name|fmt|sec|peak|desc>`, `DELETE <id>`)**:
  - Plays clips through the selected DECaudio output device with an ASCII VU level meter, records new voice annotations from the active input source, and deletes clips.
- **Waveform & Codec Inspector (`WAVEFORM [id]` / `VU` / `INSPECT`)**:
  - Computes audio buffer size in KB (`8 KB/sec` for `MULAW-8KHZ`, `22 KB/sec` for `PCM16-11KHZ`), audits peak amplitude for digital clipping saturation, and renders a 40-column VU envelope bar.
- **DECaudio BBA Hardware Routing (`OUTPUT`, `INPUT`, `VOLUME`, `GAIN`)**:
  - Routes output between `SPEAKER (Internal BBA)`, `HEADPHONE (Front Jack)`, and `LINE-OUT (Rear RCA)`, and input between `MICROPHONE (DECaudio Handset)` and `LINE-IN (Auxiliary)`, with independent `0..100%` volume and gain controls.
- **Search & Motif / XUI Window Renderer (`SEARCH <kw>`, `DISPLAY [ON <file>]`, `EXPORT <file>`)**:
  - Searches across clip names, codecs, and annotations, and renders the 78-column DECwindows DECsound Motif/XUI window chrome with transport deck (`REC`, `PLAY`, `PAUSE`, `STOP`), VU meter, and voice annotation readout.
- **Persistence (`SAVE <file>`, `LOAD <file>`)**:
  - Saves and restores the DECsound hardware settings and audio clip library.

---

## Building and Testing

```bash
make -C apps/decwindows/decsound build
pytest apps/decwindows/decsound/tests/
```
