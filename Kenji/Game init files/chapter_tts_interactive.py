#!/usr/bin/env python3
"""chapter_tts_interactive.py — interactive launcher for chapter_tts.

Asks the user to paste a chapter file path, runs a pre-flight parse +
voice-coverage check, prompts for any missing speakers (paste a voice ID
or use the narrator), then hands the parsed segments to chapter_tts so
the user only pays Claude once.

Designed to be launched by Run_Chapter_TTS.bat. Handles Windows-Explorer
paste quirks: paths wrapped in double quotes, leading/trailing whitespace.

All stdout/stderr is tee'd into voice_audio/tts_runs.log with a timestamped
header per run, so errors stay readable even if the console window closes.
"""
from __future__ import annotations
import datetime
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

KENJI_DIR = SCRIPT_DIR.parent
LOG_DIR   = KENJI_DIR / "voice_audio"
LOG_PATH  = LOG_DIR / "tts_runs.log"
MAX_LOG_BYTES = 5 * 1024 * 1024


# ---------------------------------------------------------------------------
# Tee logging
# ---------------------------------------------------------------------------

class _Tee:
    def __init__(self, *streams):
        self.streams = [s for s in streams if s is not None]
    def write(self, data):
        for s in self.streams:
            try: s.write(data)
            except Exception: pass
    def flush(self):
        for s in self.streams:
            try: s.flush()
            except Exception: pass
    def isatty(self):
        first = self.streams[0] if self.streams else None
        return bool(getattr(first, "isatty", lambda: False)())


def setup_logging():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        return None
    try:
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > MAX_LOG_BYTES:
            prev = LOG_PATH.with_suffix(".prev.log")
            if prev.exists():
                prev.unlink()
            LOG_PATH.rename(prev)
    except Exception:
        pass
    try:
        log_file = open(LOG_PATH, "a", encoding="utf-8", buffering=1)
    except Exception:
        return None
    sep = "=" * 72
    ts = datetime.datetime.now().isoformat(" ", "seconds")
    log_file.write(f"\n{sep}\n")
    log_file.write(f"  Chapter TTS run started: {ts}\n")
    log_file.write(f"{sep}\n\n")
    log_file.flush()
    sys.stdout = _Tee(sys.stdout, log_file)
    sys.stderr = _Tee(sys.stderr, log_file)
    return log_file


def teardown_logging(log_file, exit_code, chapter_path=""):
    if log_file is None:
        return
    try:
        sys.stdout.flush(); sys.stderr.flush()
    except Exception:
        pass
    sep = "-" * 72
    ts = datetime.datetime.now().isoformat(" ", "seconds")
    try:
        log_file.write(f"\n{sep}\n")
        if chapter_path:
            log_file.write(f"  Chapter:     {chapter_path}\n")
        log_file.write(f"  Exit code:   {exit_code}")
        log_file.write("  (success)\n" if exit_code == 0 else "  (FAILED)\n")
        log_file.write(f"  Finished at: {ts}\n")
        log_file.write(f"{sep}\n")
        log_file.flush()
        log_file.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# User input helpers
# ---------------------------------------------------------------------------

def clean_path_input(raw: str) -> str:
    """Strip quotes + whitespace from a user-pasted path."""
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1]
    return s.strip()


def looks_like_voice_id(s: str) -> bool:
    """ElevenLabs voice IDs are 19-20 alphanumeric chars. Loose check
    (15-40 chars, alphanumeric + underscore allowed)."""
    return 15 <= len(s) <= 40 and all(c.isalnum() or c == "_" for c in s)


def prompt_for_chapter_path() -> Path:
    print("=" * 64)
    print("  Chapter TTS - Audiobook Generator")
    print("=" * 64)
    print()
    print("Paste the full path to the chapter .md file.")
    print("  Tip: in Windows Explorer, hold Shift + right-click the file")
    print("       and choose 'Copy as path'. Then right-click here to paste.")
    print()
    print(f"  Run log: {LOG_PATH}")
    print()
    print("  Type 'q' or press Ctrl+C to quit.")
    print()
    while True:
        try:
            raw = input("Chapter file path:  ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)
        s = clean_path_input(raw)
        if not s:
            print("  (empty input - try again)")
            continue
        if s.lower() in ("q", "quit", "exit"):
            print("Cancelled.")
            sys.exit(0)
        path = Path(s)
        if not path.exists():
            print(f"  Not found: {path}")
            continue
        if not path.is_file():
            print(f"  Not a file: {path}")
            continue
        if path.suffix.lower() not in (".md", ".markdown", ".txt"):
            print(f"  Warning: {path.suffix} is not a typical markdown extension.")
            cont = input("  Use it anyway? (y/n):  ").strip().lower()
            if not cont.startswith("y"):
                continue
        return path


def prompt_yes_no(question: str, default: bool = False) -> bool:
    suffix = " (Y/n): " if default else " (y/N): "
    try:
        ans = input(question + suffix).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    if not ans:
        return default
    return ans.startswith("y")


# ---------------------------------------------------------------------------
# Voice config writer (atomic via tmp+rename to avoid OneDrive truncation)
# ---------------------------------------------------------------------------

def save_voice_slot(speaker: str, voice_id: str) -> bool:
    """Add or update a slot in tts_config.json -> character_voices.
    Atomic via temp file. Returns True on success, False on any failure."""
    cfg_path = SCRIPT_DIR / "tts_config.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ERROR reading tts_config.json: {e}")
        return False
    cfg.setdefault("character_voices", {})[speaker] = voice_id
    payload = json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"
    try:
        # Write via tmp file in same directory, then atomic os.replace.
        # This sidesteps OneDrive's mid-write truncation.
        tmp = cfg_path.with_suffix(".json.tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, cfg_path)
    except Exception as e:
        print(f"  ERROR writing tts_config.json: {e}")
        return False
    return True


# ---------------------------------------------------------------------------
# Interactive missing-voice resolver
# ---------------------------------------------------------------------------

def resolve_missing_voices(missing: List[str], narrator_voice: str) -> bool:
    """For each missing speaker, prompt for a voice ID. Save to config as
    we go. Returns True if all resolved, False if user aborted."""
    print()
    print("=" * 64)
    print(f"  {len(missing)} character(s) need voice IDs:")
    for n in missing:
        print(f"    - {n}")
    print("=" * 64)
    print()
    print("For each, paste an ElevenLabs voice ID, OR type:")
    print("  n - use the Narrator's voice (good for minor characters)")
    print("  s - skip this character (aborts the run)")
    print("  q - quit without saving any more")
    print()
    print("Find voice IDs at https://elevenlabs.io/app/voice-library")
    print("  (URL ends with the voice ID, or use the Share dialog)")
    print()

    for i, name in enumerate(missing, start=1):
        while True:
            try:
                raw = input(f"  [{i}/{len(missing)}] Voice ID for '{name}':  ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Aborted.")
                return False
            if not raw:
                print("  (empty input - try again, or 'q' to quit)")
                continue
            lower = raw.lower()
            if lower in ("q", "quit", "exit"):
                print("  Quit. Voice IDs entered so far were saved.")
                return False
            if lower in ("s", "skip"):
                print(f"  Skipping {name}. Aborting run before any audio is generated.")
                return False
            if lower in ("n", "narrator"):
                if not narrator_voice:
                    print("  ERROR: no Narrator voice ID configured.")
                    print("  Add one to tts_config.json under 'Narrator', then re-run.")
                    return False
                voice_id = narrator_voice
                print(f"  -> using Narrator's voice ({voice_id[:12]}...)")
            else:
                voice_id = raw.strip('"\'')  # strip quotes if pasted with them
                if not looks_like_voice_id(voice_id):
                    print(f"  '{voice_id}' doesn't look like a voice ID")
                    print(f"  (expected 15-40 alphanumeric chars; got {len(voice_id)})")
                    confirm = input("    Use it anyway? (y/n):  ").strip().lower()
                    if not confirm.startswith("y"):
                        continue
            if save_voice_slot(name, voice_id):
                print(f"  Saved: {name} -> {voice_id[:12]}{'...' if len(voice_id) > 12 else ''}")
                break
            else:
                print("  (save failed - try again, or 'q' to quit)")
    print()
    print("All voice IDs assigned. Continuing...")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import chapter_tts

    chapter_path = prompt_for_chapter_path()

    # Load Claude key up front so we fail fast.
    print()
    print("Pre-flight: parsing chapter for speakers...")
    anthropic_key = chapter_tts.load_anthropic_key()
    if not anthropic_key:
        print("ERROR: No ANTHROPIC_API_KEY env var or ttrpg_key.txt.")
        print("Cannot call Claude for speaker parsing.")
        return 2

    try:
        chapter_text = chapter_tts.load_chapter(chapter_path)
    except Exception as e:
        print(f"ERROR loading chapter: {e}")
        return 2
    print(f"  {len(chapter_text):,} chars in chapter")

    try:
        segments = chapter_tts.parse_speakers_via_claude(chapter_text, anthropic_key)
    except Exception as e:
        print(f"ERROR parsing speakers: {e}")
        return 3
    print(f"  {len(segments)} segments parsed")

    # Validate in a loop — prompt for missing voices until all are resolved.
    while True:
        try:
            config = chapter_tts.load_voice_config()
        except Exception as e:
            print(f"ERROR loading tts_config.json: {e}")
            return 4
        ok, missing, voice_map = chapter_tts.validate_voice_coverage(segments, config)
        if ok:
            print(f"  All {len(voice_map)} speakers have voice IDs. Good to go.")
            break
        narrator_voice = chapter_tts.voice_id_for("Narrator", config) or ""
        if not resolve_missing_voices(missing, narrator_voice):
            return 5
        # Loop: re-validate with the updated config

    # Cache segments to a temp file so chapter_tts.main() skips the Claude
    # parse step (saves money + ensures it uses the exact same segments
    # the user just resolved voices for).
    segs_temp = Path(tempfile.gettempdir()) / f"chapter_tts_segs_{os.getpid()}.json"
    segs_temp.write_text(json.dumps(segments, ensure_ascii=False), encoding="utf-8")

    # Offer dry-run first
    print()
    do_dry = prompt_yes_no(
        "Do a dry-run first? (cost preview only - no ElevenLabs credits)",
        default=True,
    )

    argv_base = [sys.argv[0], str(chapter_path), "--load-segments", str(segs_temp)]
    argv = list(argv_base)
    if do_dry:
        argv.append("--dry-run")

    real_argv = sys.argv
    sys.argv = argv
    exit_code = 0
    try:
        chapter_tts.main()
    except SystemExit as e:
        exit_code = int(e.code) if e.code is not None else 0
    except Exception as e:
        import traceback
        print(f"\nUNEXPECTED ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        exit_code = 99
    finally:
        sys.argv = real_argv

    # If dry-run, offer real run
    if do_dry and exit_code == 0:
        print()
        if prompt_yes_no("Dry-run succeeded. Run for real (will cost ElevenLabs credits)?", default=False):
            sys.argv = list(argv_base)  # no --dry-run this time
            try:
                import importlib
                importlib.reload(chapter_tts)
                chapter_tts.main()
            except SystemExit as e:
                exit_code = int(e.code) if e.code is not None else 0
            except Exception as e:
                import traceback
                print(f"\nUNEXPECTED ERROR: {type(e).__name__}: {e}")
                traceback.print_exc()
                exit_code = 99
            finally:
                sys.argv = real_argv

    # Cleanup temp file
    try:
        segs_temp.unlink()
    except Exception:
        pass

    # Final summary
    print()
    print("=" * 64)
    if exit_code == 0:
        print("  Done.")
    elif exit_code == 5:
        print("  User aborted at voice-resolution step. No credits spent.")
    else:
        print(f"  Exited with code {exit_code}.")
    print(f"  Full log: {LOG_PATH}")
    print("=" * 64)
    return exit_code


if __name__ == "__main__":
    log_file = setup_logging()
    rc = 1
    try:
        rc = main()
    except SystemExit as e:
        rc = int(e.code) if e.code is not None else 0
    except Exception as e:
        import traceback
        print()
        print("=" * 64)
        print(f"  FATAL: {type(e).__name__}: {e}")
        print("=" * 64)
        traceback.print_exc()
        rc = 99
    finally:
        teardown_logging(log_file, rc)

    try:
        input("\nPress Enter to close...")
    except (EOFError, KeyboardInterrupt):
        pass
    sys.exit(rc)
