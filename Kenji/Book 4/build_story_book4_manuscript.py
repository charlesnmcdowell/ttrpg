"""
Rebuild Game init files/Kenji_story_book4.md from Book 4/Chapters/fraying_empire_chapter_*.md

Run from anywhere: python build_story_book4_manuscript.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAPTERS = ROOT / "Chapters"
OUT = ROOT.parent / "Game init files" / "Kenji_story_book4.md"


def extract_manuscript_section(text: str) -> str:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# Fraying Empire"):
        raise ValueError("Expected # Fraying Empire header")
    manuscript_title = "#" + lines[0]
    i = 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].strip().startswith("*Book 4"):
        i += 1
    while i < len(lines) and lines[i].strip() in ("", "---"):
        i += 1
    if i < len(lines) and re.match(r"^## Chapter \w+:", lines[i]):
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    body = "\n".join(lines[i:])
    return manuscript_title + "\n\n" + body


def main() -> None:
    files = sorted(CHAPTERS.glob("fraying_empire_chapter_*.md"))
    if not files:
        raise SystemExit(f"No files matching fraying_empire_chapter_*.md in {CHAPTERS}")

    last = files[-1].stem  # fraying_empire_chapter_04
    num = last.split("_")[-1]

    header = f"""# KENJI — BOOK FOUR: *The Ronin*
## *Fraying Empire*

**Single manuscript — Book 4 (*Fraying Empire*):** The Ronin arc (Greymere → Greenveil → Thornfield → Millhaven → east road / Ashenveil border). Per-chapter source of truth: `Book 4/Chapters/` (`fraying_empire_chapter_01.md` … `fraying_empire_chapter_{num}.md`). Rebuild with `Book 4/build_story_book4_manuscript.py` after chapter edits. **Campaign bible (DM):** `fraying_empire_campaign.md` (*The Fraying Crown*).

---

*The Wizard King stepped away. The kingdom still runs on habit and competent people who are running out of duct tape. Kenji is somewhere smaller — a name he is not using, a village that needed a wall — until the world remembers where to knock.*

---

"""

    parts = [header]
    for f in files:
        section = extract_manuscript_section(f.read_text(encoding="utf-8"))
        parts.append(section.rstrip() + "\n\n---\n\n")

    text = "".join(parts).rstrip() + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT} ({len(files)} chapters)")


if __name__ == "__main__":
    main()
