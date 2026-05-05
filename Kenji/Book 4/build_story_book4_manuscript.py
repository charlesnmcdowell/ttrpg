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


# Word forms for chapter numbers — used to normalize Format B chapter
# headings ("Chapter 7:") to Format A style ("Chapter Seven:") in the
# consolidated manuscript.
_NUM_TO_WORD = {
    "1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five",
    "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine", "10": "Ten",
    "11": "Eleven", "12": "Twelve", "13": "Thirteen", "14": "Fourteen",
    "15": "Fifteen", "16": "Sixteen", "17": "Seventeen", "18": "Eighteen",
    "19": "Nineteen", "20": "Twenty", "21": "Twenty-One", "22": "Twenty-Two",
    "23": "Twenty-Three", "24": "Twenty-Four", "25": "Twenty-Five",
    "26": "Twenty-Six", "27": "Twenty-Seven", "28": "Twenty-Eight",
    "29": "Twenty-Nine", "30": "Thirty", "31": "Thirty-One",
    "32": "Thirty-Two", "33": "Thirty-Three", "34": "Thirty-Four",
    "35": "Thirty-Five", "36": "Thirty-Six", "37": "Thirty-Seven",
    "38": "Thirty-Eight", "39": "Thirty-Nine", "40": "Forty",
    "41": "Forty-One", "42": "Forty-Two",
}


def _strip_metadata_blocks(body: str) -> str:
    """Remove gameplay metadata that should NOT appear in the published
    manuscript:

      1. The opening "**Kenji dialogue note:** All Kenji spoken lines in this
         chapter are **player-declared** at the table..." paragraph that
         appears in many chapters (DM-tool annotation about player-declared
         dialogue rules — has no place in published prose).

      2. The closing "**Chapter X Summary:**" block + "**Next chapter hook:**"
         note at the end of each chapter (session log, mechanical resources,
         character notes, intel, EXP — gameplay tracking that breaks
         immersion for an Amazon reader).
    """
    # 1. Strip "Kenji dialogue note" paragraph — match the whole line and any
    #    immediate adjacent blank lines / "---" separator that frames it.
    body = re.sub(
        r"\*\*Kenji dialogue note:\*\*[^\n]*\n+(?:---\n+)?",
        "",
        body,
    )

    # 2. Strip from "**Chapter X Summary:**" through end of file. The summary
    #    block always sits at the chapter\'s tail and runs to EOF (sometimes
    #    with a "**Next chapter hook:**" line after it). Match the leading
    #    "---" separator if present so we don\'t leave an orphan rule.
    body = re.sub(
        r"\n+(?:---\s*\n+)?\*\*Chapter\s+[A-Za-z0-9 \-]+Summary:?\*\*[\s\S]*$",
        "",
        body,
    )

    # 3. Belt-and-suspenders: also strip standalone "**Next chapter hook:**"
    #    lines + their continuation in case any escape the Chapter Summary cut.
    body = re.sub(
        r"\n+\*\*Next chapter hook:\*\*[^\n]*(?:\n[^\n*]*)*",
        "",
        body,
    )

    return body.rstrip() + "\n"


def extract_manuscript_section(text: str) -> str:
    """Extract the body of one chapter file, returning a normalized
    "## Fraying Empire — Chapter X: *Title*" heading + body.

    Handles two source formats:
      A) Files starting with "# Fraying Empire — Chapter X: *Title*"
         (chapters 1-6, 14-18).
      B) Files starting with "# Book 4 — Fraying Empire" then a
         "## Chapter N: Title" line on the next non-blank line, optionally
         followed by **Date:** / **Location:** metadata lines (chapters
         7-13, 19-42).
    """
    lines = text.splitlines()
    if not lines:
        raise ValueError("empty chapter file")

    first = lines[0].strip()

    # ---- Format A — "# Fraying Empire — Chapter X: *Title*" ----
    if first.startswith("# Fraying Empire"):
        manuscript_title = "#" + lines[0]   # promote # → ##
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
        return manuscript_title + "\n\n" + _strip_metadata_blocks(body)

    # ---- Format B — "# Book 4 — Fraying Empire" + "## Chapter N: Title" ----
    if first.startswith("# Book 4 — Fraying Empire") or first.startswith("# Book 4 - Fraying Empire"):
        # Find the "## Chapter N: Title" line on a subsequent line
        i = 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i >= len(lines):
            raise ValueError("Format B: missing chapter heading line")
        ch_match = re.match(r"^##\s*Chapter\s+(\d+):\s*(.+?)\s*$", lines[i])
        if not ch_match:
            raise ValueError(f"Format B: expected '## Chapter N: Title', got: {lines[i]!r}")
        ch_num_digit = ch_match.group(1)
        ch_title = ch_match.group(2).strip().strip('*').strip()
        ch_word = _NUM_TO_WORD.get(ch_num_digit, ch_num_digit)
        manuscript_title = f"## Fraying Empire — Chapter {ch_word}: *{ch_title}*"
        i += 1
        # Skip metadata lines (**Date:**, **Location:**, blank, ---)
        while i < len(lines):
            stripped = lines[i].strip()
            if (stripped == ""
                or stripped == "---"
                or stripped.startswith("**Date:**")
                or stripped.startswith("**Location:**")
                or stripped.startswith("**Day")
                or stripped.startswith("**Time:**")):
                i += 1
                continue
            break
        body = "\n".join(lines[i:])
        return manuscript_title + "\n\n" + _strip_metadata_blocks(body)

    raise ValueError(f"unrecognized chapter header: {first!r}")


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
