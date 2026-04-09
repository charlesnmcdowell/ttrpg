"""Extract DM notes from Kenji_story_book2.md into dm_rules_tracking.md (Book 2 tracking section)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"C:\Users\charl\OneDrive\Documents\TTRPG\Kenji\Game init files")
STORY = Path(ROOT / "Kenji_story_book2.md")
DM_RULES = Path(ROOT / "dm_rules_tracking.md")
MARK_START = "<!-- AUTO_EXTRACT_BOOK2_TRACKING_START -->"
MARK_END = "<!-- AUTO_EXTRACT_BOOK2_TRACKING_END -->"


def main() -> None:
    text = STORY.read_text(encoding="utf-8")
    dm: list[str] = []

    def push(title: str, body: str) -> None:
        dm.append(f"\n---\n\n## {title}\n\n{body.strip()}\n")

    # 1) Book Two end: remove DING line; move KENJI sheet only (keep narrative paragraph)
    m = re.search(
        r"DING — END OF BOOK TWO: THE DESCENT — LEVEL 10 PENDING\n+"
        r"(The cycle turns\.[\s\S]*?)\n+"
        r"(KENJI\n[\s\S]*?End of Book Two: The Descent\.\n+)",
        text,
    )
    if not m:
        raise RuntimeError("Book Two DING + sheet not found")
    narrative, sheet = m.group(1), m.group(2)
    text = text[: m.start()] + narrative + "\n\n" + text[m.end() :]
    push("End of Book Two: The Descent — character sheet", sheet)

    # 2) All Sundered Gate DING checkpoints: DING ... End of The Sundered Gate — Chapter N.
    ding_re = re.compile(
        r"DING —[^\n]+\n+"
        r"(KENJI[\s\S]*?)\n*End of The Sundered Gate — Chapter [^\n]+\.\n+",
        re.MULTILINE,
    )
    while True:
        m = ding_re.search(text)
        if not m:
            break
        push("Sundered Gate — session checkpoint (DING)", m.group(0))
        text = text[: m.start()] + text[m.end() :]

    # 3) **CHAPTER N — STATE AT CLOSE** blocks
    for n in (9, 10):
        m = re.search(
            rf"\*\*CHAPTER {n} — STATE AT CLOSE\*\*\n+\n*(```[\s\S]*?```)\n+",
            text,
        )
        if m:
            push(f"Chapter {n} — state at close", m.group(0))
            text = text[: m.start()] + text[m.end() :]

    # 4) Chapter 12 DM appendices (Hour 13) up to Chapter Thirteen header
    m = re.search(
        r"\n*---\n*\n## STATE AT CHAPTER CLOSE\n*\n```\nDay 21, Hour 13:00[\s\S]*?\n```\n*"
        r"(?:\n*---\n*\n## CONSTRUCT ARMY[\s\S]*?)\n*"
        r"(?:\n*---\n*\n## NOBLE'S INTEREST[\s\S]*?)\n*"
        r"(?:\n*---\n*\n## EXP LOG[\s\S]*?)\n*"
        r"(?:\n*---\n*\n## TOURNAMENT BRACKET[\s\S]*?)\n*"
        r"(?:\n*---\n*\n## SENNA SCALING[\s\S]*?)\n*"
        r"(?:\n*---\n*\n## THREAT CLOCKS[\s\S]*?)\n*"
        r"(?:\n*---\n*\n## NPC STATUS[\s\S]*?)\n*```\n*",
        text,
    )
    if not m:
        raise RuntimeError("Chapter 12 appendices block not found")
    push("Chapter 12 — DM appendices", m.group(0))
    text = text[: m.start()] + "\n" + text[m.end() :]

    # 5) Chapter 13 DM appendices (Hour 15) through end of file
    m = re.search(
        r"\n*---\n*\n## STATE AT CHAPTER CLOSE\n*\n```\nDay 21, Hour 15:00[\s\S]*",
        text,
    )
    if not m:
        raise RuntimeError("Chapter 13 appendices block not found")
    push("Chapter 13 — DM appendices", m.group(0))
    text = text[: m.start()] + "\n" + text[m.end() :]

    # 6) Remove stray duplicate section header before Chapter Two (Sundered Gate)
    text = re.sub(
        r"\n# KENJI — THE SUNDERED GATE\n+\n*---\n+(?=\n*## Chapter Two)",
        "\n",
        text,
        count=1,
    )

    # 7) **Day ...** bold scene labels → ## Day ... (novel-style subheads)
    def repl_day(mm: re.Match[str]) -> str:
        inner = mm.group(1).strip()
        return f"\n\n## {inner}\n\n---\n"

    text = re.sub(r"\n\*\*(Day [^*]+)\*\*\n", repl_day, text)

    # 8) Fix misnumbered Pipeline chapters
    text = text.replace(
        "# The Sundered Gate — Chapter Ten: The Pipeline",
        "# The Sundered Gate — Chapter Eight: The Pipeline",
        1,
    )
    text = text.replace(
        "# The Sundered Gate — Chapter nine: The Pipeline",
        "# The Sundered Gate — Chapter Nine: The Pipeline",
        1,
    )

    # Cleanup: collapse extra blank lines
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    header = (
        "# Kenji — Book Two — DM Rules & Tracking\n\n"
        "*Extracted from `Kenji_story_book2.md` so the manuscript reads as a litRPG novel "
        "without session notes, clocks, or stat dumps between chapters.*\n"
    )
    extracted = header + "".join(dm)
    big = DM_RULES.read_text(encoding="utf-8")
    if MARK_START not in big or MARK_END not in big:
        raise RuntimeError(
            f"{DM_RULES.name} missing {MARK_START} / {MARK_END} — run _merge_dm_docs.py first."
        )
    pattern = re.compile(
        re.escape(MARK_START) + r"[\s\S]*?" + re.escape(MARK_END),
        re.MULTILINE,
    )
    new_big, n = pattern.subn(
        MARK_START + "\n\n" + extracted.strip() + "\n\n" + MARK_END,
        big,
        count=1,
    )
    if n != 1:
        raise RuntimeError("Could not replace Book 2 tracking block in dm_rules_tracking.md")
    DM_RULES.write_text(new_big, encoding="utf-8", newline="\n")
    STORY.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
    print("OK:", DM_RULES.name, STORY.name)


if __name__ == "__main__":
    main()
