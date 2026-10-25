"""Test suite for WordPerfect 5.1 for VAX/VMS (WordPerfect Corp.)."""
import os
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "wp51"
ALIAS_WP = APP_DIR / "bin" / "wp"
ALIAS_WORDPERFECT = APP_DIR / "bin" / "wordperfect"


def run_wp51(commands: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN_PATH), commands],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_wp51_binary_and_aliases_exist():
    assert BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK)
    assert ALIAS_WP.exists() and os.access(ALIAS_WP, os.X_OK)
    assert ALIAS_WORDPERFECT.exists() and os.access(ALIAS_WORDPERFECT, os.X_OK)


def test_wp51_sample_reveal_spell_thesaurus_and_merge(tmp_path: Path):
    res = run_wp51("SAMPLE; LIST; REVEAL; SPELL; THESAURUS CLUSTER; MERGE; SHOW; EXIT", tmp_path)
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample WordPerfect 5.1 document loaded - 4 paragraphs]" in out
    assert "[Bold:On]" in out and "[SRt][HRt]" in out
    assert "[Speller Complete: 280 words verified, 0 misspellings, 2 technical acronyms skipped]" in out
    assert "[Thesaurus Lookup Complete: 8 synonyms and 1 antonym found for CLUSTER]" in out
    assert "[WP51 Mail-Merge Complete: 3 customized documents generated (4 paragraphs each)]" in out


def test_wp51_add_save_and_load(tmp_path: Path):
    res1 = run_wp51("SAMPLE; ADD P-05, APPENDIX, VAXstation 4000 DECwindows font table., 60; SAVE mydoc.wpd; EXIT", tmp_path)
    assert res1.returncode == 0
    res2 = run_wp51("CLEAR; LOAD mydoc.wpd; SPELL; EXIT", tmp_path)
    assert res2.returncode == 0
    assert "[5 WP51 paragraphs loaded from mydoc.wpd]" in res2.stdout
    assert "[Speller Complete: 340 words verified" in res2.stdout
