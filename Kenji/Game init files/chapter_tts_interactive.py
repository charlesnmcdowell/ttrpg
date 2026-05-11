#!/usr/bin/env python3
"""chapter_tts_interactive.py — interactive launcher for chapter_tts.

Asks the user to paste a chapter file path, then runs the full audiobook
pipeline. Designed to be launched by Run_Chapter_TTS.bat so users can
double-click an icon, paste a path, and get audio.

Handles Windows-Explorer paste quirks:
  - paths wrapped in double quotes (right-click > Copy as path)
  - leading / trailing whitespace
  - both forward and backward slashes

After the run, prints a clear success / failure summary and waits for
the user to press Enter (so the console window doesn't vanish if launched
by double-click).
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Ensure this folder is on sys.path so chapter_tts imports cleanly when
# launched from anywhere.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def clean_path_input(raw: str) -> str:
    """Strip quotes + whitespace from a user-pasted path."""
    s = raw.strip()
    # Strip matched outer quotes (Windows "Copy as path" wraps in ").
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1]
    return s.strip()


def prompt_for_chapter_path() -> Path:
    """Loop until the user gives us a valid chapter file."""
    print("=" * 64)
    print("  Chapter TTS — Audiobook Generator")
    print("=" * 64)
    print()
    print("Paste the full path to the chapter .md file.")
    print("  Tip: in Windows Explorer, hold Shift + right-click the file")
    print("       and choose 'Copy as path'. Then right-click here to paste.")
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
            print("  (empty input — try again)")
            continue
        if s.lower() in ("q", "quit", "exit"):
            print("Cancelled.")
            sys.exit(0)
        path = Path(s)
        if not path.exists():
            print(f"  Not found: {path}")
            print("  (check the path and try again)")
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


def main() -> int:
    # Step 1: get the chapter path interactively
    chapter_path = prompt_for_chapter_path()

    # Step 2: offer a dry-run first
    print()
    do_dry = prompt_yes_no(
        "Do a free dry-run first? (parses + validates voices, no ElevenLabs API)",
        default=True,
    )

    # Step 3: assemble argv and call chapter_tts.main()
    argv = [sys.argv[0], str(chapter_path)]
    if do_dry:
        argv.append("--dry-run")

    # Need to patch sys.argv because chapter_tts.main() uses argparse
    real_argv = sys.argv
    sys.argv = argv
    exit_code = 0
    try:
        import chapter_tts
        chapter_tts.main()
    except SystemExit as e:
        exit_code = int(e.code) if e.code is not None else 0
    except Exception as e:
        import traceback
        print()
        print("=" * 64)
        print(f"  UNEXPECTED ERROR: {type(e).__name__}: {e}")
        print("=" * 64)
        traceback.print_exc()
        exit_code = 99
    finally:
        sys.argv = real_argv

    # Step 4: if dry-run succeeded, offer to re-run for real
    if do_dry and exit_code == 0:
        print()
        if prompt_yes_no("Dry-run succeeded. Run for real (will cost ElevenLabs credits)?", default=False):
            argv = [sys.argv[0], str(chapter_path)]
            sys.argv = argv
            try:
                import importlib
                import chapter_tts
                importlib.reload(chapter_tts)
                chapter_tts.main()
            except SystemExit as e:
                exit_code = int(e.code) if e.code is not None else 0
            except Exception as e:
                import traceback
                print()
                print(f"  UNEXPECTED ERROR: {type(e).__name__}: {e}")
                traceback.print_exc()
                exit_code = 99
            finally:
                sys.argv = real_argv

    # Step 5: summary
    print()
    print("=" * 64)
    if exit_code == 0:
        print("  Done.")
    elif exit_code == 5:
        print("  Missing voice IDs - see list above. No credits spent.")
        print("  Edit tts_config.json to add the missing voices, then re-run.")
    else:
        print(f"  Exited with code {exit_code}.")
    print("=" * 64)
    return exit_code


if __name__ == "__main__":
    rc = main()
    # Pause so the user can read the output before the window closes.
    # The .bat does this too, but doing it here protects against being run
    # without the .bat (e.g. double-clicked .py).
    try:
        input("\nPress Enter to close...")
    except (EOFError, KeyboardInterrupt):
        pass
    sys.exit(rc)
