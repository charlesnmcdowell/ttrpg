#!/usr/bin/env python3
"""Chapter-close pipeline for the Kenji TTRPG.

Run ONCE after finishing a chapter to batch-update all state tracking.
Supports TWO input modes:
  1. YAML/JSON receipt (new v2.0 pipeline) — structured chapter_receipt
  2. Chapter markdown file (legacy) — parses summary block from prose

Usage:
    python chapter_close.py <chapter_file_or_receipt>         # auto-detects format
    python chapter_close.py <file> --dry-run                  # show diff, don't save
    python chapter_close.py <file> --dry-run --json           # machine-readable diff
    python chapter_close.py <file> --character <name>         # use <name>_state.json

Examples:
    python chapter_close.py receipt_ch43.yaml                 # receipt mode (v2.0)
    python chapter_close.py receipt_ch43.json                 # receipt mode (JSON)
    python chapter_close.py "Book 4/Chapters/fraying_empire_chapter_16.md"  # legacy
"""

import json, re, sys, os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from copy import deepcopy

# Patch v2.0 methods onto StoryEngine for receipt processing
try:
    import engine_v2  # noqa: F401 — side-effect: monkey-patches StoryEngine
except ImportError:
    pass  # graceful: v2 features unavailable but legacy markdown mode still works

SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR / "kenji_state.json"
AI_CONTEXT_FILE = SCRIPT_DIR / "AI_CONTEXT.md"

sys.path.insert(0, str(SCRIPT_DIR))
from ttrpg_game_engine import StoryEngine

# ---------------------------------------------------------------------------
# Calendar helpers
# ---------------------------------------------------------------------------
# Ashmere starts at day 222 (month 8 of 12, 30 days each + offsets)
# The engine uses "day" as an absolute counter from campaign start.
# Mapping: Ashmere 1 = Day 223 (month 8 × 30 - 17 offset from Book 1 start)
# Derived from kenji_state.json: Ashmere 34 = Day 256 → offset = 256 - 34 = 222
ASHMERE_OFFSET = 222   # Ashmere N = Day (222 + N)
HOLLOWMERE_OFFSET = 252  # Hollowmere N = Day (252 + N)  [Ashmere has 30 days]

MONTH_OFFSETS = {
    "ashmere": ASHMERE_OFFSET,
    "hollowmere": HOLLOWMERE_OFFSET,
    "ironveil": 282,   # Hollowmere 30 = 282, Ironveil 1 = 283
    "lastmere": 312,
}

def parse_calendar_date(text: str) -> Optional[int]:
    """Parse 'Ashmere 31' or 'Day 253' into engine day number."""
    text = text.strip().lower()
    # Try "Day NNN" first
    m = re.search(r'day\s+(\d+)', text)
    if m:
        return int(m.group(1))
    # Try "Ashmere NN" etc.
    for month, offset in MONTH_OFFSETS.items():
        m = re.search(rf'{month}\s+(\d+)', text)
        if m:
            return offset + int(m.group(1))
    return None

def day_to_calendar(day: int) -> str:
    """Convert engine day to calendar string."""
    for month in reversed(sorted(MONTH_OFFSETS.items(), key=lambda x: x[1])):
        name, offset = month
        if day > offset:
            return f"{name.capitalize()} {day - offset}"
    return f"Day {day}"

# ---------------------------------------------------------------------------
# Chapter summary parser
# ---------------------------------------------------------------------------
def parse_chapter_summary(filepath: Path) -> Dict[str, Any]:
    """Extract structured data from a chapter markdown file.

    Reads:
    - Session span line (dates)
    - Summary block (Gameplay/Combat/Resources/Character/Intel/Ends)
    - Title
    """
    text = filepath.read_text(encoding="utf-8")
    result: Dict[str, Any] = {
        "file": str(filepath),
        "title": None,
        "start_date": None,
        "end_date": None,
        "end_day": None,
        "end_time": None,
        "end_location": None,
        "gold_spent": 0,
        "exp": None,
        "combat": False,
        "resources_notes": [],
        "vigor_events": [],
        "npc_updates": [],
    }

    # Title
    m = re.search(r'^#\s+.*?Chapter\s+\d+.*?:\s*\*(.+?)\*', text, re.MULTILINE)
    if m:
        result["title"] = m.group(1)

    # Session span
    m = re.search(r'\*\*Session span:\*\*\s*(.+)', text)
    if m:
        span = m.group(1)
        # Find end date — look for the last Ashmere/Hollowmere reference or Day reference
        dates = re.findall(r'(?:Ashmere|Hollowmere|Ironveil|Lastmere)\s+\d+', span, re.IGNORECASE)
        days = re.findall(r'Day\s+\d+', span, re.IGNORECASE)
        if dates:
            result["end_date"] = dates[-1]
            result["end_day"] = parse_calendar_date(dates[-1])
        if days:
            d = parse_calendar_date(days[-1])
            if d and (result["end_day"] is None or d > result["end_day"]):
                result["end_day"] = d
                result["end_date"] = days[-1]
        if len(dates) >= 2:
            result["start_date"] = dates[0]

    # Summary — Ends line
    m = re.search(r'\*\*Ends:\*\*\s*(.+?)(?:\n|$)', text)
    if m:
        ends = m.group(1)
        # Location
        loc_m = re.search(r'\*\*Kenji\*\*\s+(?:alone\s+)?(?:in|at)\s+\*\*(.+?)\*\*', ends)
        if loc_m:
            result["end_location"] = loc_m.group(1)
        # Time
        time_m = re.search(r'~?\*?\*?(\d{1,2}:\d{2}\s*(?:AM|PM)?)\*?\*?', ends)
        if time_m:
            result["end_time"] = time_m.group(1)
        # EXP
        exp_m = re.search(r'(\d[\d,]+)\s*/\s*(\d[\d,]+)', ends)
        if exp_m:
            result["exp"] = int(exp_m.group(1).replace(",", ""))
        # End day from Ends line (more reliable than session span sometimes)
        for date_str in re.findall(r'(?:Ashmere|Hollowmere)\s+\d+', ends, re.IGNORECASE):
            d = parse_calendar_date(date_str)
            if d:
                result["end_day"] = d
                result["end_date"] = date_str

    # Always scan summary bullets for later dates than what Session span or
    # Ends line found.  This handles chapters like Ch17 where the real end date
    # is embedded in a bullet like "Ashmere 33→34 close (canon)".

    # Handle "Ashmere 33→34" arrow style (pick the higher number)
    for arrow_m in re.finditer(
        r'(Ashmere|Hollowmere|Ironveil|Lastmere)\s+\d+\s*[→\->]+\s*(\d+)',
        text, re.IGNORECASE
    ):
        month_name = arrow_m.group(1).lower()
        day_num = int(arrow_m.group(2))
        d = MONTH_OFFSETS.get(month_name, 0) + day_num
        if result["end_day"] is None or d > result["end_day"]:
            result["end_day"] = d
            result["end_date"] = f"{month_name.capitalize()} {day_num}"

    # Also scan summary bullets for plain "Ashmere NN" references
    summary_block = re.search(
        r'^- \*\*Gameplay:\*\*.*?(?=\n\*\*Next|\n---|\Z)',
        text, re.MULTILINE | re.DOTALL
    )
    if summary_block:
        block = summary_block.group(0)
        all_dates = re.findall(
            r'(?:Ashmere|Hollowmere|Ironveil|Lastmere)\s+\d+',
            block, re.IGNORECASE
        )
        for date_str in all_dates:
            d = parse_calendar_date(date_str)
            if d and (result["end_day"] is None or d > result["end_day"]):
                result["end_day"] = d
                result["end_date"] = date_str

    # Resources line — gold
    m = re.search(r'\*\*Resources:\*\*\s*(.+?)(?:\n|$)', text)
    if m:
        res = m.group(1)
        result["resources_notes"].append(res)
        # Gold spent: look for −N GP or -N GP
        for gm in re.finditer(r'[−\-]\*?\*?(\d+)\s*GP\*?\*?', res):
            result["gold_spent"] += int(gm.group(1))

    # Also scan Gameplay line for GP amounts (some chapters log gold there)
    if result["gold_spent"] == 0:
        gp_m = re.search(r'\*\*Gameplay:\*\*\s*(.+?)(?:\n-|\n\*\*|\Z)', text, re.DOTALL)
        if gp_m:
            gameplay = gp_m.group(1)
            # Look for "−N GP" or "**N GP**" spending patterns
            for gm in re.finditer(r'[−\-]\*?\*?(\d+)\s*GP\*?\*?', gameplay):
                result["gold_spent"] += int(gm.group(1))
            # Also match "NNN GP" with spending context words nearby
            if result["gold_spent"] == 0:
                for gm in re.finditer(r'\*?\*?(\d+)\s*GP\*?\*?', gameplay):
                    amt = int(gm.group(1))
                    # Check surrounding context for spending words
                    start = max(0, gm.start() - 60)
                    context = gameplay[start:gm.end() + 20].lower()
                    if any(w in context for w in ['spent', 'paid', 'bought', 'cost',
                                                   'provender', 'inn', 'hire', 'bribe',
                                                   'purchase', 'luxury']):
                        result["gold_spent"] += amt

    # Combat line
    m = re.search(r'\*\*Combat:\*\*\s*(.+?)(?:\n|$)', text)
    if m:
        combat_text = m.group(1).strip().lower()
        result["combat"] = "none" not in combat_text

    return result


# ---------------------------------------------------------------------------
# Vigor expiry checker
# ---------------------------------------------------------------------------
def check_vigor_expiry(state: dict, current_day: int) -> List[str]:
    """Check dm_private.lovers_vigor_tracking for expired windows."""
    alerts = []
    dm = state.get("dm_private", {})
    vigor = dm.get("lovers_vigor_tracking", {})
    if isinstance(vigor, dict) and "note" in vigor:
        for name, entry in vigor.items():
            if name == "note" or not isinstance(entry, dict):
                continue
            status = entry.get("status", "")
            expires_str = entry.get("expires", "")
            expire_day = parse_calendar_date(expires_str)
            if expire_day is None:
                continue
            if current_day >= expire_day and "EXPIRED" not in status.upper() and "ACTIVE" in status.upper():
                alerts.append(f"VIGOR EXPIRED: {name} — was due {expires_str} (Day {expire_day}), current Day {current_day}")
            elif current_day < expire_day and "ACTIVE" in status.upper():
                remaining = expire_day - current_day
                alerts.append(f"VIGOR ACTIVE: {name} — {remaining} day(s) remaining (expires {expires_str})")
    return alerts


# ---------------------------------------------------------------------------
# Goal checker
# ---------------------------------------------------------------------------
def check_goals(state: dict, current_day: int) -> List[str]:
    """Check character_goals list for overdue/due-soon goals."""
    alerts = []
    goals = state.get("character_goals", [])
    for g in goals:
        if not isinstance(g, dict):
            continue
        st = (g.get("status") or "").strip().lower()
        if st in ("resolved", "mia", "closed", "complete", "completed", "superseded"):
            continue
        char = g.get("character", "?")
        gid = g.get("goal_id", "?")
        due = g.get("due_day")
        if due is None:
            continue
        try:
            due_i = int(due)
        except (TypeError, ValueError):
            continue
        if current_day > due_i:
            alerts.append(f"OVERDUE: {char} / {gid} — was due Day {due_i} ({day_to_calendar(due_i)}), now Day {current_day}")
        elif current_day == due_i:
            alerts.append(f"DUE TODAY: {char} / {gid} — deadline Day {due_i} ({day_to_calendar(due_i)})")
        elif current_day >= due_i - 2:
            alerts.append(f"DUE SOON: {char} / {gid} — deadline Day {due_i} ({day_to_calendar(due_i)}), {due_i - current_day} day(s) left")
    return alerts


# ---------------------------------------------------------------------------
# Diff reporter
# ---------------------------------------------------------------------------
def compute_diff(old: dict, new: dict, chapter_data: dict) -> Dict[str, Any]:
    """Compare old and new state, produce a human-readable diff."""
    diff = {
        "chapter": chapter_data.get("title", "?"),
        "file": chapter_data.get("file", "?"),
        "changes": [],
        "vigor_alerts": [],
        "goal_alerts": [],
    }

    # Day/Calendar
    if old.get("day") != new.get("day"):
        diff["changes"].append(f"Day: {old.get('day')} → {new.get('day')} ({day_to_calendar(new['day'])})")
    if old.get("hour") != new.get("hour"):
        diff["changes"].append(f"Hour: {old.get('hour')} → {new.get('hour')}")

    # Location
    old_loc = old.get("location", "")
    new_loc = new.get("location", "")
    if old_loc != new_loc:
        # Truncate for display
        diff["changes"].append(f"Location: ...{old_loc[:50]}... → ...{new_loc[:50]}...")

    # Gold
    if old.get("gold") != new.get("gold"):
        delta = new["gold"] - old["gold"]
        diff["changes"].append(f"Gold: {old['gold']} → {new['gold']} ({delta:+d} GP)")

    # EXP
    if old.get("exp") != new.get("exp"):
        diff["changes"].append(f"EXP: {old.get('exp')} → {new.get('exp')}")

    # Calendar string
    if old.get("calendar_date") != new.get("calendar_date"):
        diff["changes"].append(f"Calendar: {old.get('calendar_date', '?')} → {new.get('calendar_date', '?')}")

    # Canon pointer
    if old.get("canon_pointer") != new.get("canon_pointer"):
        diff["changes"].append(f"Canon pointer updated")

    return diff


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def chapter_close(chapter_path: str, dry_run: bool = False, json_output: bool = False):
    """Main chapter-close pipeline."""
    chapter_file = Path(chapter_path)
    if not chapter_file.is_absolute():
        chapter_file = SCRIPT_DIR / chapter_file
    if not chapter_file.exists():
        print(f"ERROR: Chapter file not found: {chapter_file}")
        sys.exit(1)

    # Load current state
    state_text = STATE_FILE.read_text(encoding="utf-8")
    old_state = json.loads(state_text)
    old_snapshot = deepcopy(old_state)

    # Parse chapter
    chapter_data = parse_chapter_summary(chapter_file)

    print(f"{'=' * 60}")
    print(f"CHAPTER CLOSE: {chapter_data.get('title', '?')}")
    print(f"File: {chapter_file.name}")
    print(f"{'=' * 60}")
    print()

    # --- Load engine ---
    eng = StoryEngine.load_json(str(STATE_FILE))

    # --- 1. Calendar advancement ---
    end_day = chapter_data.get("end_day")
    stale_chapter = False  # True if this chapter predates current engine state

    if end_day and end_day < eng.day:
        stale_chapter = True
        print(f"[CALENDAR] WARNING: Chapter end day ({end_day} = {day_to_calendar(end_day)}) "
              f"is BEFORE current engine day ({eng.day} = {day_to_calendar(eng.day)}).")
        print(f"           This chapter appears already processed. Skipping all state mutations.")
        print()
    elif end_day and end_day > eng.day:
        old_day = eng.day
        # Advance day-by-day
        days_to_advance = end_day - eng.day
        for _ in range(days_to_advance):
            eng.day += 1
        # Set hour based on end time
        if chapter_data.get("end_time"):
            t = chapter_data["end_time"]
            hour_m = re.match(r'(\d+):(\d+)', t)
            if hour_m:
                h = int(hour_m.group(1))
                m = int(hour_m.group(2))
                eng.hour = h + m / 60.0
        else:
            eng.hour = 6.5  # default post-LR
        print(f"[CALENDAR] Day {old_day} → Day {end_day} ({day_to_calendar(end_day)})")
        # Update calendar_date string
        cal_str = f"{day_to_calendar(end_day)}, 1247 AR"
        if chapter_data.get("end_time"):
            cal_str += f" (~{chapter_data['end_time']})"
        eng.extra_json["calendar_date"] = cal_str
        eng.extra_json.setdefault("calendar", {})["current_date"] = f"{day_to_calendar(end_day)}, 1247 AR"
        eng.extra_json.setdefault("calendar", {})["day_count"] = end_day
    elif end_day:
        print(f"[CALENDAR] Day already at {end_day} ({day_to_calendar(end_day)}) — no change")
    else:
        print(f"[CALENDAR] Could not parse end date from chapter summary")

    if stale_chapter:
        # Still run read-only checks (Vigor, goals, validation) for informational purposes
        print("[VIGOR] Status (read-only — no mutations):")
        vigor_alerts = check_vigor_expiry(eng.to_dict(), end_day or eng.day)
        for a in vigor_alerts:
            print(f"  {a}")
        print()
        warnings = eng.validate()
        if warnings:
            print("[VALIDATE] Warnings:")
            for w in warnings:
                print(f"  ⚠ {w}")
        # Build a minimal diff
        diff = {"stale": True, "chapter_end_day": end_day, "engine_day": eng.day}
        diff["vigor_alerts"] = vigor_alerts
        diff["goal_alerts"] = []
    else:
        # --- 2. Location ---
        if chapter_data.get("end_location"):
            loc = chapter_data["end_location"]
            old_loc = eng.location
            eng.location = loc
            print(f"[LOCATION] → {loc}")

        # --- 3. Gold ---
        if chapter_data.get("gold_spent", 0) > 0:
            spent = chapter_data["gold_spent"]
            eng.gold -= spent
            print(f"[GOLD] −{spent} GP → {eng.gold} GP remaining")

        # --- 4. EXP ---
        if chapter_data.get("exp") and chapter_data["exp"] != eng.exp:
            old_exp = eng.exp
            eng.exp = chapter_data["exp"]
            print(f"[EXP] {old_exp:,} → {eng.exp:,}")

        # --- 5. Canon pointer ---
        ch_title = chapter_data.get("title", "?")
        ch_num_m = re.search(r'chapter[_ ]?(\d+)', str(chapter_file).lower())
        ch_num = ch_num_m.group(1) if ch_num_m else "?"
        end_cal = day_to_calendar(end_day) if end_day else "?"
        eng.canon_pointer = (
            f"Book 4, Chapter {ch_num} COMPLETE ({chapter_file.name}). "
            f"Ends {end_cal}, Day {end_day or '?'}."
        )
        print(f"[CANON] → Ch{ch_num} complete")

        # --- 6. Process character goals ---
        print()
        goal_alerts = eng.process_character_goals()
        if goal_alerts:
            print("[GOALS] Engine alerts:")
            for a in goal_alerts:
                print(f"  {a}")

        # Also run our own check for overdue/due-soon
        extra_goal_alerts = check_goals(eng.to_dict(), eng.day)
        if extra_goal_alerts:
            print("[GOALS] Status check:")
            for a in extra_goal_alerts:
                print(f"  {a}")

        # --- 7. Vigor expiry check ---
        print()
        vigor_alerts = check_vigor_expiry(eng.to_dict(), eng.day)
        if vigor_alerts:
            print("[VIGOR] Status:")
            for a in vigor_alerts:
                print(f"  {a}")
        else:
            print("[VIGOR] No active Vigor windows or all already marked expired")

        # --- 8. Validation ---
        print()
        warnings = eng.validate()
        if warnings:
            print("[VALIDATE] Warnings:")
            for w in warnings:
                print(f"  ⚠ {w}")
        else:
            print("[VALIDATE] State clean")

    # --- 9. Compute diff ---
    if stale_chapter:
        # Already built minimal diff above
        print()
        print(f"{'=' * 60}")
        print("STALE CHAPTER — no state mutations applied")
        print(f"Engine is at Day {eng.day} ({day_to_calendar(eng.day)}), "
              f"chapter ends at Day {end_day} ({day_to_calendar(end_day)}).")
        print(f"{'=' * 60}")
        if json_output:
            print(json.dumps(diff, indent=2, ensure_ascii=False))
        return

    new_state = eng.to_dict()
    diff = compute_diff(old_snapshot, new_state, chapter_data)
    diff["vigor_alerts"] = vigor_alerts
    diff["goal_alerts"] = extra_goal_alerts

    # --- 10. Save or dry-run ---
    print()
    print(f"{'=' * 60}")
    if dry_run:
        print("DRY RUN — no files modified")
        print(f"{'=' * 60}")
        if json_output:
            print(json.dumps(diff, indent=2, ensure_ascii=False))
        else:
            print("\nChanges that WOULD be applied:")
            for c in diff["changes"]:
                print(f"  → {c}")
    else:
        # Save state
        eng.save_json(str(STATE_FILE))
        print(f"[SAVED] {STATE_FILE.name} (v{eng._save_version})")

        # Regenerate AI_CONTEXT.md
        brief = eng.ai_brief_markdown()
        AI_CONTEXT_FILE.write_text(brief, encoding="utf-8")
        print(f"[SAVED] AI_CONTEXT.md ({len(brief)} chars)")
        sep = "=" * 60
        print(sep)
        print("\nApplied changes:")
        for c in diff["changes"]:
            print(f"  -> {c}")

        # Write receipt
        receipt_dir = SCRIPT_DIR / "logs"
        receipt_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ch_label = f"chapter_close_{ch_num}_{ts}.txt"
        receipt_file = receipt_dir / ch_label
        r_lines = []
        r_lines.append("CHAPTER_CLOSE_RECEIPT")
        r_lines.append(f"chapter: {ch_num}")
        r_lines.append(f"file: {chapter_file.name}")
        r_lines.append(f"executed: {datetime.now().isoformat(timespec='seconds')}")
        r_lines.append(f"engine_day: {eng.day}")
        r_lines.append(f"calendar: {day_to_calendar(eng.day)}")
        r_lines.append(f"save_version: {eng._save_version}")
        r_lines.append("---")
        for c in diff["changes"]:
            r_lines.append(f"  {c}")
        if vigor_alerts:
            r_lines.append("--- VIGOR ---")
            for a in vigor_alerts:
                r_lines.append(f"  {a}")
        if extra_goal_alerts:
            r_lines.append("--- GOALS ---")
            for a in extra_goal_alerts:
                r_lines.append(f"  {a}")
        if warnings:
            r_lines.append("--- WARNINGS ---")
            for w in warnings:
                r_lines.append(f"  {w}")
        receipt_file.write_text("\n".join(r_lines), encoding="utf-8")
        print(f"[RECEIPT] {receipt_file}")

    print()
    return diff


def chapter_close_receipt(receipt_path: str, dry_run: bool = False,
                         json_output: bool = False, character: str = None):
    """Chapter-close pipeline from a structured YAML/JSON receipt (v2.0).

    The receipt is the standardized output from the AI at chapter end.
    """
    rpath = Path(receipt_path)
    if not rpath.is_absolute():
        rpath = SCRIPT_DIR / rpath
    if not rpath.exists():
        print(f"ERROR: Receipt not found: {rpath}")
        sys.exit(1)

    text = rpath.read_text(encoding="utf-8")

    # Try JSON first, then YAML
    receipt = None
    try:
        receipt = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
            receipt = yaml.safe_load(text)
        except ImportError:
            print("ERROR: Receipt is not JSON and PyYAML is not installed.")
            print("  pip install pyyaml --break-system-packages")
            sys.exit(1)

    if isinstance(receipt, dict) and "chapter_receipt" in receipt:
        receipt = receipt["chapter_receipt"]
    if not isinstance(receipt, dict):
        print("ERROR: Receipt did not parse to a dict.")
        sys.exit(1)

    # Resolve state file
    state_file = STATE_FILE
    if character:
        # Import the resolver from _dm_turn
        sys.path.insert(0, str(SCRIPT_DIR))
        try:
            from _dm_turn import resolve_state_file
            state_file = resolve_state_file(character)
        except ImportError:
            state_file = SCRIPT_DIR / f"{character.lower()}_state.json"

    # Load engine
    eng = StoryEngine.load_json(str(state_file))
    old_snapshot = deepcopy(eng.to_dict())

    ch_num = receipt.get("chapter_number", "?")
    print(f"{'=' * 60}")
    print(f"CHAPTER CLOSE (receipt): Chapter {ch_num}")
    print(f"Receipt: {rpath.name}")
    print(f"{'=' * 60}")

    # --- Apply receipt fields ---
    changes = []

    # Day
    end_day = receipt.get("day_end")
    if end_day and int(end_day) != eng.day:
        old_day = eng.day
        eng.day = int(end_day)
        changes.append(f"Day: {old_day} → {eng.day} ({day_to_calendar(eng.day)})")

    # Location
    loc = receipt.get("location_end")
    if loc and loc != eng.location:
        old_loc = eng.location
        eng.location = loc
        changes.append(f"Location: {old_loc} → {loc}")

    # EXP (mandatory)
    exp_block = receipt.get("exp_earned")
    if not exp_block:
        print("[!!] REJECTED: No exp_earned block in receipt. EXP tracking is mandatory.")
        print("     Even zero-EXP chapters must include the block with total: 0.")
        if not dry_run:
            sys.exit(1)
    else:
        combat_exp = int(exp_block.get("combat", 0))
        roleplay_exp = int(exp_block.get("roleplay", 0))
        discovery_exp = int(exp_block.get("discovery", 0))
        stated_total = int(exp_block.get("total", 0))
        calc_total = combat_exp + roleplay_exp + discovery_exp
        if stated_total != calc_total:
            print(f"[!] EXP total mismatch: stated {stated_total}, calculated {calc_total}. Using calculated.")
        justification = exp_block.get("justification", "")
        result = eng.update_exp(
            int(ch_num) if str(ch_num).isdigit() else 0,
            combat_exp, roleplay_exp, discovery_exp, justification
        )
        changes.append(f"EXP: {result['old_exp']:,} → {result['new_exp']:,} (+{calc_total})")
        if result.get("level_up"):
            changes.append("LEVEL UP available!")
        if result.get("zero_streak_warning"):
            changes.append(result["warning"])

    # Gold
    gold_block = receipt.get("gold_changes", {})
    if gold_block:
        gained = int(gold_block.get("gained", 0))
        spent = int(gold_block.get("spent", 0))
        notes = gold_block.get("notes", "")
        econ = eng.validate_economy(gained, spent, notes)
        for w in econ["warnings"]:
            changes.append(f"ECONOMY WARNING: {w}")
        old_gold = eng.gold
        eng.gold += gained - spent
        changes.append(f"Gold: {old_gold} → {eng.gold} ({gained - spent:+d} GP)")

    # HP
    hp_block = receipt.get("hp_changes", {})
    if hp_block and "current_hp" in hp_block:
        old_hp = eng.hp
        eng.hp = int(hp_block["current_hp"])
        if old_hp != eng.hp:
            changes.append(f"HP: {old_hp} → {eng.hp}/{eng.max_hp}")

    # Goals progressed
    for gp in receipt.get("goals_progressed", []):
        gid = gp.get("goal_id", "")
        new_status = gp.get("new_status", "")
        note = gp.get("progress_note", "")
        for g in eng.character_goals:
            if isinstance(g, dict) and g.get("goal_id") == gid:
                if new_status:
                    g["status"] = new_status
                if str(ch_num).isdigit():
                    g["last_updated_chapter"] = int(ch_num)
                changes.append(f"Goal {gid} → {new_status or 'updated'}: {note}")
                break

    # New goals
    for gn in receipt.get("goals_new", []):
        eng.character_goals.append({
            "goal_id": gn.get("goal_id", ""),
            "description": gn.get("description", ""),
            "status": "active",
            "due_chapter": gn.get("due_chapter"),
            "due_day": gn.get("due_day"),
            "trigger_condition": gn.get("trigger_condition"),
            "attached_npc": gn.get("attached_npc"),
            "created_chapter": int(ch_num) if str(ch_num).isdigit() else None,
            "last_updated_chapter": int(ch_num) if str(ch_num).isdigit() else None,
            "escalation_tier": 0,
        })
        changes.append(f"Goal NEW: {gn.get('goal_id', '?')}")

    # Items
    for item in receipt.get("items_gained", []):
        if item not in eng.key_items:
            eng.key_items.append(item)
            changes.append(f"Item gained: {item}")
    for item in receipt.get("items_lost", []):
        if item in eng.satchel:
            eng.satchel.remove(item)
            changes.append(f"Item lost: {item}")
        elif item in eng.key_items:
            eng.key_items.remove(item)
            changes.append(f"Item lost: {item}")

    # Cover status
    cover = receipt.get("cover_status")
    if cover:
        eng.extra_json["cover_status"] = cover
        changes.append(f"Cover: → {cover}")

    # Chapter counter
    if str(ch_num).isdigit():
        eng.extra_json["current_chapter"] = int(ch_num)

    # Canon pointer
    end_cal = day_to_calendar(eng.day) if eng.day else "?"
    eng.canon_pointer = f"Chapter {ch_num} COMPLETE. Ends {end_cal}, Day {eng.day}."

    # --- Run goal audit + escalation ---
    chapter_int = int(ch_num) if str(ch_num).isdigit() else 0
    if chapter_int > 0:
        esc_msgs = eng.escalate_goals(chapter_int)
        for msg in esc_msgs:
            changes.append(f"ESCALATION: {msg.splitlines()[0]}")

    # --- Vigor check ---
    vigor_alerts = check_vigor_expiry(eng.to_dict(), eng.day)
    goal_alerts = check_goals(eng.to_dict(), eng.day)

    # --- Validation ---
    warnings = eng.validate()

    # --- Output ---
    print()
    if dry_run:
        print("DRY RUN — no files modified")
        print(f"{'=' * 60}")
        print("\nChanges that WOULD be applied:")
        for c in changes:
            print(f"  → {c}")
        if json_output:
            print(json.dumps({
                "changes": changes,
                "vigor_alerts": vigor_alerts,
                "goal_alerts": goal_alerts,
                "warnings": warnings,
            }, indent=2))
    else:
        eng.save_json(str(state_file))
        print(f"[SAVED] {state_file.name} (v{eng._save_version})")

        brief = eng.ai_brief_markdown()
        AI_CONTEXT_FILE.write_text(brief, encoding="utf-8")
        print(f"[SAVED] AI_CONTEXT.md ({len(brief)} chars)")

        print(f"{'=' * 60}")
        print("\nApplied changes:")
        for c in changes:
            print(f"  → {c}")

        # Write receipt log
        receipt_dir = SCRIPT_DIR / "logs"
        receipt_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        receipt_file = receipt_dir / f"chapter_close_{ch_num}_{ts}.txt"
        r_lines = [
            "CHAPTER_CLOSE_RECEIPT (v2.0)",
            f"chapter: {ch_num}",
            f"receipt_file: {rpath.name}",
            f"executed: {datetime.now().isoformat(timespec='seconds')}",
            f"engine_day: {eng.day}",
            f"calendar: {day_to_calendar(eng.day)}",
            f"save_version: {eng._save_version}",
            "---",
        ]
        for c in changes:
            r_lines.append(f"  {c}")
        if vigor_alerts:
            r_lines.append("--- VIGOR ---")
            r_lines.extend(f"  {a}" for a in vigor_alerts)
        if goal_alerts:
            r_lines.append("--- GOALS ---")
            r_lines.extend(f"  {a}" for a in goal_alerts)
        if warnings:
            r_lines.append("--- WARNINGS ---")
            r_lines.extend(f"  {w}" for w in warnings)
        receipt_file.write_text("\n".join(r_lines), encoding="utf-8")
        print(f"[RECEIPT] {receipt_file}")

    if vigor_alerts:
        print("\n[VIGOR]")
        for a in vigor_alerts:
            print(f"  {a}")
    if goal_alerts:
        print("\n[GOALS]")
        for a in goal_alerts:
            print(f"  {a}")
    if warnings:
        print("\n[WARNINGS]")
        for w in warnings:
            print(f"  {w}")


def _detect_format(filepath: Path) -> str:
    """Detect if a file is a receipt (JSON/YAML) or a chapter markdown."""
    suffix = filepath.suffix.lower()
    if suffix in (".yaml", ".yml", ".json"):
        return "receipt"
    if suffix in (".md", ".markdown"):
        return "markdown"
    # Try to detect by content
    text = filepath.read_text(encoding="utf-8")[:500]
    if "chapter_receipt:" in text or '"chapter_receipt"' in text or '"chapter_number"' in text:
        return "receipt"
    return "markdown"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Chapter close pipeline (v2.0)")
    ap.add_argument("chapter", help="Path to chapter file (.md) or receipt (.yaml/.json)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--character", default=None, help="Character name (loads <name>_state.json)")
    args = ap.parse_args()

    chapter_file = Path(args.chapter)
    if not chapter_file.is_absolute():
        chapter_file = SCRIPT_DIR / chapter_file

    fmt = _detect_format(chapter_file)
    if fmt == "receipt":
        chapter_close_receipt(str(chapter_file), dry_run=args.dry_run,
                              json_output=args.json, character=args.character)
    else:
        chapter_close(str(chapter_file), dry_run=args.dry_run, json_output=args.json)
