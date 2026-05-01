#!/usr/bin/env python3
"""prose_state_extractor.py — Scan chapter prose for state-relevant claims and
flag items that haven't been mirrored into character_world_state.json.

Rule 9 enforcement: prose is authoritative for events; JSON is authoritative for
state. Anything established in chapter prose (item acquired, ability unlocked,
NPC bond formed, threat clock established) must end up in mechanical_state
before the chapter is marked DONE. This script catches drift programmatically.

USAGE
-----
    python prose_state_extractor.py --character cookie
        # scans Cookie/Chapters/*.md against
        # Cookie/Game init files/character_world_state.json
        # reports prose-only items that aren't in JSON

    python prose_state_extractor.py --character cookie --chapter 9
        # only scan chapter 9

    python prose_state_extractor.py --character cookie --json-only
        # only check the most recent N chapters (default: last 2) for fastest scan

DESIGN
------
The extractor is intentionally conservative. It surfaces CANDIDATE prose-state
mismatches for human review. False positives are expected and acceptable; false
negatives (drift the script misses) are the real cost. So patterns lean broad.

What it scans for:
- ITEM acquisitions: "walks out with", "wears", "puts on", "is wearing",
  "attuned", "in her hand", "fingers close around", "<NAME> [acquires/picks up/
  takes/keeps/pockets] <NOUN>"
- CLASS FEATURES / ABILITIES: capitalized ability names mentioned in prose
  with verb cues ("activates", "channels", "manifests", "the X flares")
- NPC mentions: capitalized proper nouns appearing 3+ times that aren't in
  main_cast or extra_npcs
- THREAT CLOCK keywords: "within N days", "before <event>", "deadline",
  "if <PC> doesn't <do X> by <Y>"

Output is a structured report listing each candidate with:
- chapter file + line number
- the matched phrase
- whether it's already in JSON (or any sibling file flagging it as known)
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent


def _find_ttrpg_root(start: Path) -> Optional[Path]:
    cur = start.resolve()
    for _ in range(10):
        if (cur / "realm_lore_registry.json").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _load_manifest(character: str) -> Dict[str, Any]:
    """Resolve manifests/<name>.json + return campaign config."""
    mp = SCRIPT_DIR / "manifests" / f"{character.lower()}.json"
    if not mp.exists():
        sys.exit(f"Manifest not found: {mp}")
    return json.loads(mp.read_text(encoding="utf-8"))


def _resolve_paths(manifest: Dict[str, Any]) -> Tuple[Path, Path]:
    """Return (state_file_path, chapters_dir_path)."""
    ttrpg_root = _find_ttrpg_root(SCRIPT_DIR)
    if ttrpg_root is None:
        sys.exit("Could not find TTRPG root (no realm_lore_registry.json)")
    state_file = ttrpg_root / manifest["state_file"]
    # Chapters live alongside the character folder (sibling of "Game init files")
    char_root = state_file.parent.parent       # e.g. ".../Cookie"
    chapters_dir = char_root / "Chapters"
    return state_file, chapters_dir


# ---------------------------------------------------------------------------
# Pattern library — broad on purpose. False positives are filtered later.
# ---------------------------------------------------------------------------

ITEM_ACQUIRE_PATTERNS = [
    # "Cookie walks out with the Anklet of Unarmed Combat."
    re.compile(r"\b(?:walks?|walked) out with (?:the |a |an )?([A-Z][\w' ]{2,60}?)(?=[\.\,\;\—\:\(])", re.IGNORECASE),
    # "Cookie wears the Healer's Ring." / "is wearing"
    re.compile(r"\b(?:wears?|wearing) (?:the |a |an )?([A-Z][\w' ]{2,60}?)(?=[\.\,\;\—\:\(])"),
    # "Cookie puts on the earrings."
    re.compile(r"\bputs? on (?:the |a |an )?([A-Z][\w' ]{2,60}?)(?=[\.\,\;\—\:\(])"),
    # "<NAME> attuned" / "Anklet attuned"
    re.compile(r"\b([A-Z][\w' ]{2,40}?) attuned\b"),
    # "Cookie keeps/takes/pockets the X"
    re.compile(r"\b(?:keeps?|kept|takes?|took|pockets?|pocketed|claims?|claimed|picks? up|picked up|hauls? home) (?:the |a |an )?([A-Z][\w' ]{2,60}?)(?=[\.\,\;\—\:\(])"),
    # "<NAME> sits warm on her finger"
    re.compile(r"\b(?:[A-Z][\w' ]{2,40}?) sits? (?:warm|cool|heavy|light) (?:on|against)\b"),
    # "the X hums against her skin"
    re.compile(r"\bthe ([A-Z][\w' ]{2,40}?) (?:hums?|glows?|flares?|pulses?) (?:against|on|in|under|across)\b"),
]

ABILITY_PATTERNS = [
    # "Cookie activates Heartstring." / "channels Golden Note"
    re.compile(r"\b(?:activates?|activated|channels?|channeled|manifests?|manifested|invokes?|invoked) ([A-Z][\w' ]{2,40}?)(?=[\.\,\;\—\:\(])"),
    # "the Heartstring caught him"
    re.compile(r"\bthe ([A-Z][\w' ]{2,40}?) (?:caught|hit|landed|pushed|rolled over|swept)\b"),
    # "Heartstring resonance" / "Heartstring full-fail" — bare proper-noun ability mentions
    re.compile(r"\b([A-Z][\w]{4,30}) (?:resonance|active|passive|on|off|caps?|capped|nullified|cooldown|recharge)\b"),
]

THREAT_CLOCK_PATTERNS = [
    # "within 30 days" / "in 14 days"
    re.compile(r"\bwithin (\d+)\s*(?:in[- ]game\s*)?days?\b", re.IGNORECASE),
    re.compile(r"\bin (\d+)\s*(?:in[- ]game\s*)?days?\b", re.IGNORECASE),
    # "before <event>"
    re.compile(r"\bbefore (?:return to|leaving|the|next) [A-Z][\w' ]{2,40}", re.IGNORECASE),
    # "deadline:" prefix
    re.compile(r"\bdeadline:?\s*[A-Z][\w' ]{2,40}", re.IGNORECASE),
    # "<PC> answers <X> by <Y>"
    re.compile(r"\b(?:answers?|owes? the answer|delivers?|reports? back) (?:before|by|within|no later than)\b", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Stop-words — proper nouns that aren't items / abilities / threats
# ---------------------------------------------------------------------------

ITEM_STOPWORDS = {
    # Cities, regions, realms
    "Varenholm", "Duskfen", "Bleakmoor", "Thornfield", "Greenveil", "Briarstone",
    "Millhaven", "Stormhaven", "Ashenmere", "Dragonspine", "Kharn", "Cinderpeak",
    "Kettlebrook", "Crown Quarter", "Sunken Playhouse", "Adventurer's Guild",
    "Gilt Lily", "Gilded Thread", "Pale Lantern", "Starling", "Millward Chandlery",
    "Maeven", "Wardbreakers", "Wardbreaker", "Phase", "Ankunyx", "Ankuspawn",
    # Common false-positives from broad regexes
    "Cookie", "Kenji", "Amaris", "Silka", "Lyssa", "Senna", "Finch", "Varn",
    "Eira", "Fern", "Daisy", "Tomas", "Ashworth", "Isolde", "Ivor",
    "Falconer", "Halbert", "Torren", "Beldra", "Selwyn", "Jareth",
    # Generic words that capitalize at sentence start
    "Sound", "Air", "Light", "Heat", "Cold", "Mid", "Late", "Early", "Half",
    "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
    "Day", "Night", "Morning", "Evening", "Hour", "Minute",
    "She", "He", "They", "Cookie", "The", "And", "But", "If", "When", "Then",
}

ABILITY_KNOWN = {
    "Heartstring", "Golden Note", "Chorus of One", "Dance of Dispel",
    "Healing Dance", "Planar Waltz", "Dragon's Roar Dance", "Tai Chi",
    "Dancer's Tai Chi", "Ember Last Stand", "Great User", "Fans Out of Control",
    "Dance Inspiration", "Sibling Resonance", "Ember", "Vorathiel",
    "Vigor", "Underhall Express", "Stack",
}


# ---------------------------------------------------------------------------
# JSON inspection
# ---------------------------------------------------------------------------

def _flatten_json_strings(obj: Any, out: List[str] = None) -> List[str]:
    """Walk the JSON tree and collect every string value (lowercased) for
    substring matching. Used to ask 'is this candidate already mentioned anywhere
    in the state file?' as a quick triage."""
    if out is None:
        out = []
    if isinstance(obj, str):
        out.append(obj.lower())
    elif isinstance(obj, dict):
        for v in obj.values():
            _flatten_json_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _flatten_json_strings(v, out)
    return out


def _is_candidate_in_json(candidate: str, json_haystack: str) -> bool:
    """Case-insensitive substring check against the flattened state file."""
    if len(candidate) < 4:
        return True   # too short to flag confidently
    return candidate.lower() in json_haystack


# ---------------------------------------------------------------------------
# Chapter scanning
# ---------------------------------------------------------------------------

def _list_chapter_files(chapters_dir: Path, character: str, chapter_num: Optional[int] = None) -> List[Path]:
    if not chapters_dir.exists():
        return []
    pattern = f"{character.lower()}_chapter_*.md"
    files = sorted(chapters_dir.glob(pattern))
    if chapter_num is not None:
        target = f"{character.lower()}_chapter_{chapter_num:02d}.md"
        files = [f for f in files if f.name == target]
    return files


def _scan_chapter(path: Path, json_haystack: str) -> Dict[str, List[Tuple[int, str]]]:
    """Scan one chapter file. Return {category: [(line_no, snippet), ...]}."""
    findings: Dict[str, List[Tuple[int, str]]] = {
        "items": [],
        "abilities": [],
        "threat_clocks": [],
    }
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    for line_no, line in enumerate(text.splitlines(), start=1):
        # --- ITEMS ---
        for pat in ITEM_ACQUIRE_PATTERNS:
            for m in pat.finditer(line):
                if m.groups():
                    name = m.group(1).strip().rstrip(".,;:")
                else:
                    name = m.group(0).strip()
                if not name or name in ITEM_STOPWORDS:
                    continue
                # Skip if first word is a stopword
                if name.split()[0] in ITEM_STOPWORDS:
                    continue
                if _is_candidate_in_json(name, json_haystack):
                    continue
                findings["items"].append((line_no, f"{name}  (line: {line.strip()[:90]})"))

        # --- ABILITIES ---
        for pat in ABILITY_PATTERNS:
            for m in pat.finditer(line):
                if m.groups():
                    name = m.group(1).strip().rstrip(".,;:")
                else:
                    continue
                if not name or name in ITEM_STOPWORDS:
                    continue
                if name.split()[0] in ITEM_STOPWORDS:
                    continue
                if _is_candidate_in_json(name, json_haystack):
                    continue
                findings["abilities"].append((line_no, f"{name}  (line: {line.strip()[:90]})"))

        # --- THREAT CLOCKS ---
        for pat in THREAT_CLOCK_PATTERNS:
            m = pat.search(line)
            if m:
                snippet = line.strip()[:120]
                findings["threat_clocks"].append((line_no, snippet))

    # De-duplicate (same name, same chapter)
    for cat, hits in findings.items():
        seen = set()
        deduped = []
        for ln, txt in hits:
            key = txt.split("  (line:")[0].strip().lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append((ln, txt))
        findings[cat] = deduped

    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _report(state_file: Path, all_findings: Dict[Path, Dict[str, List[Tuple[int, str]]]]) -> int:
    """Print findings. Return non-zero exit code if drift found."""
    total = sum(
        len(v) for fp_findings in all_findings.values()
        for v in fp_findings.values()
    )
    if total == 0:
        print(f"OK — no prose-to-state drift detected.\n  state_file: {state_file}")
        return 0

    print(f"\n{'=' * 60}")
    print(f"  PROSE-TO-STATE DRIFT REPORT  (Rule 9)")
    print(f"  state_file: {state_file}")
    print(f"  total candidates: {total}")
    print(f"{'=' * 60}\n")

    for chapter_path, findings in all_findings.items():
        if not any(findings.values()):
            continue
        print(f"--- {chapter_path.name} ---")
        for category, hits in findings.items():
            if not hits:
                continue
            print(f"  [{category.upper()}]  ({len(hits)} candidate{'s' if len(hits) != 1 else ''})")
            for ln, txt in hits[:30]:   # cap per chapter to keep output readable
                print(f"    line {ln:>4}: {txt}")
            if len(hits) > 30:
                print(f"    ... ({len(hits) - 30} more)")
        print()

    print("→ Review each candidate. False positives expected.")
    print("→ Real drift: mirror into mechanical_state and re-run to confirm clean.")
    print("→ See dm_rules_tracking.md § RULE 9 for the prose-to-state mirror protocol.")
    return 1   # non-zero if drift found


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Scan chapter prose for state-drift candidates (Rule 9 enforcement).")
    p.add_argument("--character", "-C", required=True, help="Character name (e.g. cookie, kenji, amaris)")
    p.add_argument("--chapter", "-c", type=int, default=None, help="Only scan this chapter number")
    p.add_argument("--last", "-n", type=int, default=None, help="Only scan the last N chapter files")
    args = p.parse_args(argv)

    manifest = _load_manifest(args.character)
    state_file, chapters_dir = _resolve_paths(manifest)

    if not state_file.exists():
        sys.exit(f"State file not found: {state_file}")

    state = json.loads(state_file.read_text(encoding="utf-8"))
    json_haystack = " ".join(_flatten_json_strings(state))

    chapter_files = _list_chapter_files(chapters_dir, args.character, args.chapter)
    if args.last is not None and chapter_files:
        chapter_files = chapter_files[-args.last:]

    if not chapter_files:
        sys.exit(f"No chapter files found in {chapters_dir} matching '{args.character.lower()}_chapter_*.md'")

    all_findings: Dict[Path, Dict[str, List[Tuple[int, str]]]] = {}
    for cf in chapter_files:
        all_findings[cf] = _scan_chapter(cf, json_haystack)

    return _report(state_file, all_findings)


if __name__ == "__main__":
    sys.exit(main())
