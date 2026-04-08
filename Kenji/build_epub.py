#!/usr/bin/env python3
"""
Build Amazon KDP-ready EPUB from Kenji_story_book1.md
Usage: python build_epub.py
"""

import re
import os
from pathlib import Path
from ebooklib import epub

SCRIPT_DIR = Path(__file__).parent
SOURCE = SCRIPT_DIR / "Game init files" / "Kenji_story_book1.md"
OUTPUT = SCRIPT_DIR / "The_Sorcerer_Sword.epub"

BOOK_TITLE = "The Sorcerer-Sword"
BOOK_AUTHOR = "Hiro Protagonist"
BOOK_LANG = "en"
BOOK_ID = "kenji-sorcerer-sword-book1-2026"

CHAPTER_TITLES = {
    1: "A World Without Maps",
    2: "The Things We Carry Into the Dark",
    3: "What Walks Toward Us",
    4: "The Things That Wait",
    5: "What We Leave Behind",
    6: "The Bridge",
    7: "The Broken Antler",
    8: "The City That Knows",
    9: "The Old Man and the Ember",
    10: "What the Ember Sees",
    11: "What's Underneath",
    12: "The Crawl",
    13: "The Dramatic Little Bastard",
    14: "Two Combat Mages",
    15: "The Sword That Waited",
    16: "The Chair and the Voice",
    17: "Sing for Your Supper",
    18: "Come Back",
    19: "Both Halves",
    20: "The Reckoning",
    21: "Getting It Up",
    22: "Come Back",
    23: "The Gauntlet, Revisited",
    24: "The Things That Hunt You Back",
    25: "The Clock and the Door",
    26: "Tinder Boxes and Pressed Flowers",
    27: "New Management",
}

CSS = """\
@charset "UTF-8";
body {
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.5;
  text-align: justify;
  margin: 1em;
  orphans: 2;
  widows: 2;
}
h1.chapter-number {
  text-align: center;
  font-size: 1.1em;
  font-weight: normal;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-top: 3em;
  margin-bottom: 0.2em;
  page-break-before: always;
}
h2.chapter-title {
  text-align: center;
  font-size: 1.4em;
  font-style: italic;
  font-weight: normal;
  margin-top: 0;
  margin-bottom: 2em;
}
h3.section-header {
  text-align: left;
  font-size: 1.1em;
  font-weight: bold;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}
p {
  text-indent: 1.5em;
  margin: 0.3em 0;
}
p.first, p.after-break {
  text-indent: 0;
}
hr.scene-break {
  border: none;
  text-align: center;
  margin: 1.5em 0;
}
hr.scene-break::after {
  content: "\\2022  \\2022  \\2022";
  font-size: 0.8em;
  letter-spacing: 0.5em;
  color: #555;
}
div.stat-block {
  font-family: "Courier New", Courier, monospace;
  font-size: 0.85em;
  line-height: 1.3;
  border: 1px solid #888;
  padding: 1em;
  margin: 2em 0.5em;
  page-break-inside: avoid;
}
div.stat-block p {
  text-indent: 0;
  margin: 0.2em 0;
}
div.stat-block p.stat-header {
  font-weight: bold;
  font-size: 1.05em;
  margin-top: 0.8em;
  margin-bottom: 0.2em;
}
strong em, em strong {
  font-style: italic;
  font-weight: bold;
}
div.title-page {
  text-align: center;
  margin-top: 30%;
}
div.title-page h1 {
  font-size: 2em;
  font-weight: bold;
  margin-bottom: 0.3em;
}
div.title-page p.subtitle {
  font-size: 1.1em;
  font-style: italic;
  margin-bottom: 2em;
}
div.title-page p.author {
  font-size: 1.2em;
}
div.copyright {
  text-align: center;
  margin-top: 30%;
  font-size: 0.85em;
  line-height: 1.8;
}
div.copyright p { text-indent: 0; }
div.dedication {
  text-align: center;
  margin-top: 25%;
  font-style: italic;
  font-size: 1.1em;
}
div.dedication p { text-indent: 0; }
div.back-matter h2 {
  text-align: center;
  font-size: 1.3em;
  margin-bottom: 1.5em;
}
div.back-matter h3 {
  font-size: 1.1em;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}
div.back-matter p { text-indent: 0; margin: 0.5em 0; }
"""


STAT_BLOCK_HEADERS = {
    "KENJI", "CANTRIPS", "SPELLS", "ABILITIES", "INVENTORY", "QUEUED",
    "PENDING ACTIONS", "LOSSES THIS CHAPTER", "THREADS SEVERED THIS CHAPTER",
    "NEW ABILITIES", "NEW SPELLS", "LEVEL 1 SPELLS", "LEVEL 2 SPELLS",
    "LEVEL 3 SPELLS", "LEVEL 4 SPELLS", "PERK", "Gold:",
}


def is_stat_block_start(line: str) -> bool:
    """Detect where narrative ends and the stat/level-up block begins."""
    stripped = line.strip()
    if stripped.startswith("DING"):
        return True
    if re.match(r"^END OF CHAPTER", stripped):
        return True
    return False


def markdown_to_xhtml(text: str) -> str:
    """Convert inline markdown to XHTML, handling bold-italic, bold, italic."""
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Undo escaping inside tags we just created
    text = re.sub(r'&lt;(/?(?:strong|em))&gt;', r'<\1>', text)
    text = re.sub(r'&amp;(amp|lt|gt|quot|apos);', r'&\1;', text)
    return text


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def convert_narrative_to_xhtml(lines: list[str]) -> str:
    """Convert narrative markdown lines to XHTML paragraphs with scene breaks."""
    parts = []
    after_break = True

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped == "---":
            parts.append('<hr class="scene-break" />')
            after_break = True
            continue

        if stripped.startswith("### "):
            header_text = markdown_to_xhtml(stripped[4:])
            parts.append(f'<h3 class="section-header">{header_text}</h3>')
            after_break = True
            continue

        converted = markdown_to_xhtml(stripped)
        css_class = ' class="after-break"' if after_break else ''
        parts.append(f"<p{css_class}>{converted}</p>")
        after_break = False

    return "\n".join(parts)


def convert_stat_block_to_xhtml(lines: list[str]) -> str:
    """Convert stat block lines into a styled div."""
    parts = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        is_header = False
        for hdr in STAT_BLOCK_HEADERS:
            if stripped.startswith(hdr) or stripped.upper().startswith("PERK"):
                is_header = True
                break

        if re.match(r"^(DING|END OF CHAPTER|End of Chapter|End of Book)", stripped):
            is_header = True

        escaped = escape_xml(stripped)
        if is_header:
            parts.append(f'<p class="stat-header">{escaped}</p>')
        else:
            parts.append(f"<p>{escaped}</p>")

    if not parts:
        return ""
    return '<div class="stat-block">\n' + "\n".join(parts) + "\n</div>"


def parse_chapters(source_path: Path) -> list[dict]:
    """Parse the markdown source into chapter dicts."""
    text = source_path.read_text(encoding="utf-8")
    raw_blocks = re.split(r'^# KENJI\s*$', text, flags=re.MULTILINE)

    # First element is empty or preamble before the first # KENJI
    raw_blocks = [b for b in raw_blocks if b.strip()]

    chapters = []
    for idx, block in enumerate(raw_blocks, start=1):
        block_lines = block.split("\n")

        # Extract subtitle from first ## line
        subtitle = CHAPTER_TITLES.get(idx, f"Chapter {idx}")

        # Skip header lines (## lines)
        narrative_lines = []
        stat_lines = []
        in_stat = False

        for line in block_lines:
            stripped = line.strip()
            # Skip the ## subtitle/day header lines
            if stripped.startswith("## "):
                continue
            if not in_stat and is_stat_block_start(stripped):
                in_stat = True
            if in_stat:
                stat_lines.append(line)
            else:
                narrative_lines.append(line)

        chapters.append({
            "number": idx,
            "title": subtitle,
            "narrative": narrative_lines,
            "stat_block": stat_lines,
        })

    return chapters


def build_chapter_xhtml(ch: dict) -> str:
    """Build full XHTML content for a chapter."""
    num = ch["number"]
    title = ch["title"]

    narrative_html = convert_narrative_to_xhtml(ch["narrative"])
    stat_html = convert_stat_block_to_xhtml(ch["stat_block"])

    body = f"""\
<h1 class="chapter-number">Chapter {num}</h1>
<h2 class="chapter-title">{escape_xml(title)}</h2>
{narrative_html}
{stat_html}"""

    return body


def make_title_page() -> str:
    return f"""\
<div class="title-page">
<h1>{escape_xml(BOOK_TITLE)}</h1>
<p class="subtitle">Kenji &mdash; Book One</p>
<p class="author">{escape_xml(BOOK_AUTHOR)}</p>
</div>"""


def make_copyright_page() -> str:
    return """\
<div class="copyright">
<p>Copyright &copy; 2026 Hiro Protagonist</p>
<p>All rights reserved.</p>
<p>&nbsp;</p>
<p>This is a work of fiction. Names, characters, places, and incidents
either are the product of the author&rsquo;s imagination or are used
fictitiously. Any resemblance to actual persons, living or dead, events,
or locales is entirely coincidental.</p>
<p>&nbsp;</p>
<p>No part of this book may be reproduced in any form or by any
electronic or mechanical means, including information storage and
retrieval systems, without written permission from the author,
except for the use of brief quotations in a book review.</p>
<p>&nbsp;</p>
<p>First Edition</p>
</div>"""


def make_dedication_page() -> str:
    return """\
<div class="dedication">
<p>For everyone who woke up in the mud</p>
<p>and decided to keep walking.</p>
</div>"""


def make_appendix() -> str:
    return """\
<div class="back-matter">
<h2>Appendix &mdash; The World of Kenji</h2>

<h3>The Three Cosmic Forces</h3>

<p><strong>Creation &mdash; The Ember.</strong> The building force. Growth, life,
light. Ley lines carry it. The ancient architects used it. Kenji&rsquo;s ember
is creation energy housed in a mortal body. Visual signature: gold, white,
warm light. Things grow near it. Dead ground stirs.</p>

<p><strong>Entropy &mdash; Solveth.</strong> The recycling force. Death that feeds
life. The forest fire that clears space for new growth. Solveth is the god
of entropy&mdash;not evil, necessary. Visual signature: green-black, cold
light. Things wither but return to the soil. Creation heals entropy. The
two are partners in the natural cycle.</p>

<p><strong>Abyssal &mdash; The Abyss.</strong> Not part of the natural cycle. A wound
in the multiverse. A parasite that feeds on everything and gives nothing
back. The Abyss feeds on the gap the broken cycle left behind. Visual
signature: black glass, red veins. Not decay&mdash;dissolution. Matter
losing the will to exist. Creation burns abyssal energy on contact.</p>

<h3>Key Locations</h3>

<p><strong>Duskfen.</strong> A marsh village in the eastern wetlands. Home to the
Broken Antler inn (run by Pip and her father Aldric). The Duskfen Delve
lies beneath&mdash;ancient hexcrawler-infested tunnels hiding something
far older in their deepest passages.</p>

<p><strong>Varenholm.</strong> A major city three days&rsquo; ride west of Duskfen.
Home to the Varenholm Arcane Academy, the Mage Council, and the seat of
regional governance. The Academy tower dominates the skyline. The Gilt
Lens magic shop is run by Maren Holt.</p>

<p><strong>The Broken Antler Guild.</strong> Kenji&rsquo;s mercenary guild,
headquartered at the Broken Antler inn. Connected to both Varenholm and
Duskfen via Kenji&rsquo;s permanent portal network. Led by Brindle
(operations) with Kael as squad leader and Garrett as logistics.</p>

<h3>The Hollow Crown</h3>

<p>A blackened iron crown inscribed with crawling runes. Built by Chancellor
Marius Vael using fragments of ancient architecture, the Crown anchors a
siphon network that drained magical essence from 347 Academy graduates
over twelve years, feeding the stolen energy to Solveth to sustain
Vael&rsquo;s unnatural immortality. Kenji seized the Crown and became its
anchor, inheriting both the burden of 340 remaining threads and the bond
with Solveth. The Crown now resides in Kenji&rsquo;s Satchel of Holding.</p>

<h3>Emberfang</h3>

<p>A five-hundred-year-old longsword bonded to creation energy. Amber glow.
The blade woke when Kenji&rsquo;s ember reached sufficient strength,
recognizing a carrier of the same force that built it. Serves as a
channel for creation abilities including the Ember Lance (ranged
purification beam) and the Duality Aspect&rsquo;s creation mode. Found in
Aldric&rsquo;s smithy in Duskfen, where it had waited centuries for the
right hand.</p>
</div>"""


def make_about_author() -> str:
    return """\
<div class="back-matter">
<h2>About the Author</h2>
<p>Hiro Protagonist writes LitRPG fantasy with sharp dialogue, tactical
combat, and characters who treat mortal peril as a recreational activity.
<em>The Sorcerer-Sword</em> is the first book in the Kenji series.</p>
<p>For updates and new releases, visit [your website or social media here].</p>
</div>"""


def wrap_xhtml(body: str, title: str) -> str:
    """Wrap body content in a full XHTML document."""
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<title>{escape_xml(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
{body}
</body>
</html>"""


def build_epub():
    print(f"Reading source: {SOURCE}")
    chapters = parse_chapters(SOURCE)
    print(f"Parsed {len(chapters)} chapters")

    book = epub.EpubBook()
    book.set_identifier(BOOK_ID)
    book.set_title(BOOK_TITLE)
    book.set_language(BOOK_LANG)
    book.add_author(BOOK_AUTHOR)
    book.add_metadata("DC", "subject", "LitRPG")
    book.add_metadata("DC", "subject", "Fantasy")
    book.add_metadata("DC", "subject", "Gamelit")
    book.add_metadata(None, "meta", "", {"name": "calibre:series", "content": "Kenji"})
    book.add_metadata(None, "meta", "", {"name": "calibre:series_index", "content": "1"})

    style = epub.EpubItem(
        uid="style",
        file_name="style.css",
        media_type="text/css",
        content=CSS.encode("utf-8"),
    )
    book.add_item(style)

    spine_items = ["nav"]
    toc_items = []

    # --- Front Matter ---
    title_page = epub.EpubHtml(title="Title Page", file_name="title.xhtml", lang="en")
    title_page.set_content(wrap_xhtml(make_title_page(), BOOK_TITLE).encode("utf-8"))
    title_page.add_item(style)
    book.add_item(title_page)
    spine_items.append(title_page)

    copyright_page = epub.EpubHtml(title="Copyright", file_name="copyright.xhtml", lang="en")
    copyright_page.set_content(wrap_xhtml(make_copyright_page(), "Copyright").encode("utf-8"))
    copyright_page.add_item(style)
    book.add_item(copyright_page)
    spine_items.append(copyright_page)

    dedication_page = epub.EpubHtml(title="Dedication", file_name="dedication.xhtml", lang="en")
    dedication_page.set_content(wrap_xhtml(make_dedication_page(), "Dedication").encode("utf-8"))
    dedication_page.add_item(style)
    book.add_item(dedication_page)
    spine_items.append(dedication_page)

    # --- Chapters ---
    for ch in chapters:
        ch_num = ch["number"]
        ch_title = f"Chapter {ch_num}: {ch['title']}"
        filename = f"ch{ch_num:02d}.xhtml"

        body = build_chapter_xhtml(ch)
        content = wrap_xhtml(body, ch_title)

        epub_ch = epub.EpubHtml(title=ch_title, file_name=filename, lang="en")
        epub_ch.set_content(content.encode("utf-8"))
        epub_ch.add_item(style)
        book.add_item(epub_ch)

        spine_items.append(epub_ch)
        toc_items.append(epub_ch)
        print(f"  Chapter {ch_num}: {ch['title']} ({len(ch['narrative'])} narrative lines, {len(ch['stat_block'])} stat lines)")

    # --- Back Matter ---
    appendix_page = epub.EpubHtml(title="Appendix", file_name="appendix.xhtml", lang="en")
    appendix_page.set_content(wrap_xhtml(make_appendix(), "Appendix").encode("utf-8"))
    appendix_page.add_item(style)
    book.add_item(appendix_page)
    spine_items.append(appendix_page)
    toc_items.append(appendix_page)

    author_page = epub.EpubHtml(title="About the Author", file_name="author.xhtml", lang="en")
    author_page.set_content(wrap_xhtml(make_about_author(), "About the Author").encode("utf-8"))
    author_page.add_item(style)
    book.add_item(author_page)
    spine_items.append(author_page)
    toc_items.append(author_page)

    # --- Navigation ---
    book.toc = toc_items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine_items

    # --- Write ---
    print(f"\nWriting EPUB to: {OUTPUT}")
    epub.write_epub(str(OUTPUT), book, {})
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Done! File size: {size_kb:.0f} KB")


if __name__ == "__main__":
    build_epub()
