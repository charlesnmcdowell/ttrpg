#!/usr/bin/env python3
"""Single state-mutation interface for the Kenji TTRPG.

Usage:
    python _dm_turn.py <command> [args...]
    python _dm_turn.py --character <name> <command> [args...]

Commands:
    refresh                       Re-roll weather, sync tracker headers, write AI_CONTEXT.md, save.
    tick                          Advance 1 hour (tick_interaction), print alerts, save.
    tick <N>                      Advance N hours via repeated tick_interaction calls.
    rest                          Long rest (advance_day + full daily pipeline), save.
    eat                           Eat a meal from satchel, save.
    move <location>               Change location, save.
    dashboard                     Print dashboard (no save).
    brief                         Generate AI_CONTEXT.md + print brief (no save).
    chapter_open [chapter_num]    Generate chapter-open report (goals, triggers, perks). No save.
    chapter_close_receipt <file>  Process a YAML chapter receipt file. Save.
    receipt                       One-line arc pointer stamp (RUN_ID + SHAs). No state change.
                                  Same as: python run_arc_pointer.py --stamp --no-log
    npc <name> <field> <value>    Update NPC field (location|activity|disposition), save.
    squad <name> <field> <value>  Update squad field (status|location|mission), save.
    rel <npc> <change> <reason>   Update relationship (+/-N and reason), save.
    clock <name> <delta>          Manually adjust a threat clock, save.
    gold <amount>                 Add (positive) or subtract (negative) gold, save.
    buff <name> <hours> <effects> Add a buff, save.
    debuff <name>                 Remove a named buff, save.
    slot <level> <+/-N>           Spend or restore spell slots (e.g. slot L2 -1), save.
    charge <name> <+/-N>          Spend or restore charges (e.g. charge Recall -1), save.
    quest <name> <status> [notes] Update quest status, save.
    event <name> <day> [notes]    Add a scheduled event, save.
    gamemode [action]              Full DM boot: brief + continuity + city registry +
                                  narrator + deadlines + dashboard. Writes GAMEMODE_REPORT.json.
                                  Pass player action text to include it in the report.
                                  Example: gamemode go back up team four against the spiders
    validate                      Run consistency checks, print warnings.
    save                          Just save current engine state to JSON.

Options:
    --character <name>            Load <name>_state.json instead of kenji_state.json.
"""
import random
import re
import subprocess
import sys
from pathlib import Path

# Patch v2.0 methods (goal audit, EXP, perks, economy, campaign rules) onto StoryEngine
try:
    import engine_v2  # noqa: F401 — side-effect: monkey-patches StoryEngine
except ImportError:
    pass  # graceful: v2 features unavailable but core commands still work

SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR / "kenji_state.json"  # default; overridden by --character
TRACKER_FILE = SCRIPT_DIR / "character_tracker.md"


def _find_ttrpg_root(start: Path) -> Path:
    """Walk up from start until we find realm_lore_registry.json (TTRPG root).
    Also checks sibling directories of each ancestor (handles flat mount layouts)."""
    cur = start
    for _ in range(10):
        if (cur / "realm_lore_registry.json").exists():
            return cur
        # Check sibling directories at this level
        if cur.parent.exists():
            try:
                for sibling in cur.parent.iterdir():
                    if sibling.is_dir() and (sibling / "realm_lore_registry.json").exists():
                        return sibling
            except PermissionError:
                pass
        cur = cur.parent
    return None


def resolve_state_file(character: str = None) -> Path:
    """Resolve state file path from --character flag.

    --character kenji   → kenji_state.json (default)
    --character cookie  → Cookie/Game init files/character_world_state.json
    --character <name>  → searches TTRPG root for <Name>/Game init files/
    """
    if not character or character.lower() == "kenji":
        return SCRIPT_DIR / "kenji_state.json"

    # Try local directory first
    local = SCRIPT_DIR / f"{character.lower()}_state.json"
    if local.exists():
        return local

    # Build a list of candidate roots to search
    search_roots = []

    # 1. Try TTRPG root (walk up from SCRIPT_DIR looking for realm_lore_registry.json)
    ttrpg_root = _find_ttrpg_root(SCRIPT_DIR)
    if ttrpg_root:
        search_roots.append(ttrpg_root)

    # 2. Try parent/grandparent of SCRIPT_DIR (original logic)
    search_roots.append(SCRIPT_DIR.parent)
    search_roots.append(SCRIPT_DIR.parent.parent)

    # Search each root for the character's campaign folder
    for root in search_roots:
        if not root or not root.exists():
            continue
        for subdir in root.iterdir():
            if subdir.is_dir() and subdir.name.lower() == character.lower():
                # Check <name>_state.json first, then character_world_state.json
                for fname in [f"{character.lower()}_state.json", "character_world_state.json"]:
                    candidate = subdir / "Game init files" / fname
                    if candidate.exists():
                        return candidate

    # Fallback — use the name directly
    return SCRIPT_DIR / f"{character.lower()}_state.json"

sys.path.insert(0, str(SCRIPT_DIR))
from ttrpg_game_engine import StoryEngine

# ---------------------------------------------------------------------------
# Calendar helpers (mirrors chapter_close.py constants)
# ---------------------------------------------------------------------------
MONTH_OFFSETS = {
    "ashmere": 222,
    "hollowmere": 252,
    "ironveil": 282,
    "lastmere": 312,
}

WEEKDAYS = ["Stillday", "Rootday", "Forgeday", "Windday", "Fieldday", "Crownday"]
# Anchor: Day 258 = Forgeday (index 2) → 258 mod 6 = 0 → offset 2
WEEKDAY_OFFSET = 2


def day_to_calendar(day: int) -> str:
    """Engine day → 'Ashmere 36'."""
    for name, offset in sorted(MONTH_OFFSETS.items(), key=lambda x: -x[1]):
        if day > offset:
            return f"{name.capitalize()} {day - offset}"
    return f"Day {day}"


def day_to_weekday(day: int) -> str:
    """Engine day → weekday name."""
    return WEEKDAYS[(day + WEEKDAY_OFFSET) % 6]


def season_for_month(month_name: str) -> str:
    """Month name → season string."""
    m = month_name.lower()
    if m in ("ashmere",):
        return "Season of Fall"
    elif m in ("hollowmere",):
        return "Season of Dark"
    elif m in ("ironveil",):
        return "Season of Iron"
    elif m in ("lastmere",):
        return "Season of Ending"
    return "Unknown Season"


def _is_nested_state_file(path: Path) -> bool:
    """Check if a JSON file uses the nested character_world_state format."""
    import json
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return isinstance(data, dict) and "_story_engine_state" in data
    except Exception:
        return False


def load():
    return StoryEngine.load_json(str(STATE_FILE))


def save(eng):
    """Save engine state. For nested character_world_state.json files,
    writes back into _story_engine_state without clobbering the outer keys."""
    import json
    if _is_nested_state_file(STATE_FILE):
        full_data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        full_data["_story_engine_state"] = eng.to_dict()
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(full_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(STATE_FILE)
        print(f"\n[OK] Saved _story_engine_state -> {STATE_FILE.name}")
    else:
        eng.save_json(str(STATE_FILE))
        print(f"\n[OK] Saved -> {STATE_FILE.name} (v{eng._save_version})")
    warnings = eng.validate()
    if warnings:
        print("\n[!] VALIDATION WARNINGS:")
        for w in warnings:
            print(f"  - {w}")


def _build_charge_str(eng) -> str:
    """Build compact charge summary like 'Wind Step 3/5; Smoke-Invis-Clone 2/3; Iaido 0/1'."""
    parts = []
    # Preferred display order + short names
    short = {
        "Wind Step": "Wind Step",
        "Smoke-Invis-Clone Combo": "Smoke-Invis-Clone",
        "Phantom Double": "Phantom Double",
        "Iaido Draw-Strike (guaranteed crit)": "Iaido",
    }
    for full_name, display in short.items():
        if full_name in eng.charges:
            cur, mx = eng.charges[full_name][0], eng.charges[full_name][1]
            parts.append(f"**{display}** **{cur}/{mx}**")
    # Any remaining charges not in the short map
    for name, val in eng.charges.items():
        if name not in short:
            parts.append(f"**{name}** **{val[0]}/{val[1]}**")
    return "; ".join(parts)


def _refresh_weather(eng):
    """Re-roll weather for current location from profiles."""
    # Extract base location name (strip markdown bold)
    loc_clean = re.sub(r'\*+', '', eng.location).strip()
    # Try exact match first, then partial
    matched = None
    for profile_loc in eng.weather_profiles:
        if profile_loc.lower() in loc_clean.lower() or loc_clean.lower() in profile_loc.lower():
            matched = profile_loc
            break
    if matched:
        eng.weather = random.choice(eng.weather_profiles[matched])
        print(f"[WEATHER] {matched} → {eng.weather}")
    else:
        print(f"[WEATHER] No profile for '{loc_clean}' — keeping: {eng.weather}")
        print(f"  Available profiles: {', '.join(eng.weather_profiles.keys())}")
        print(f"  Tip: add '{loc_clean}' to weather_profiles in kenji_state.json")


def _sync_tracker_header(eng):
    """Overwrite the first 5 content lines of character_tracker.md with fresh engine state."""
    if not TRACKER_FILE.exists():
        print(f"[TRACKER] {TRACKER_FILE.name} not found — skipping header sync")
        return

    text = TRACKER_FILE.read_text(encoding="utf-8")
    lines = text.split("\n")

    cal = day_to_calendar(eng.day)
    weekday = day_to_weekday(eng.day)
    month_name = cal.split()[0] if " " in cal else "Unknown"
    season = season_for_month(month_name)
    hr = int(eng.hour) if isinstance(eng.hour, (int, float)) else eng.hour
    time_str = f"{hr:02d}:00" if isinstance(hr, int) else str(hr)

    # Build charge string
    charge_str = _build_charge_str(eng)

    # Build relationship snippet for Mursha (most active)
    mursha_rel = eng.relationships.get("Mursha", {})
    rel_str = f"**relationships.Mursha** **{mursha_rel.get('score', '?')}**" if mursha_rel else ""

    # Active arc info
    aa = eng.extra_json.get("active_arc", {})
    arc_slug = aa.get("slug", "") if isinstance(aa, dict) else str(aa)
    arc_path = aa.get("relative_path", "") if isinstance(aa, dict) else ""

    # Chapter status from narrative_notes or story_beat
    ch_status = ""
    nn = eng.extra_json.get("narrative_notes", [])
    for note in reversed(nn) if isinstance(nn, list) else []:
        if isinstance(note, str) and ("COMPLETE" in note or "OPEN" in note):
            ch_status = note.strip()
            break
    if not ch_status:
        ch_status = eng.story_beat.strip()[:120] if eng.story_beat else ""

    # Weather snippet
    weather_note = eng.weather if eng.weather else "clear"

    # --- Build new header lines ---
    new_lines = [
        f"# Character Tracker — Kenji TTRPG",
        f"",
        f"**Current In-Game Date:** {cal}, 1247 AR — **{weekday}** — **Day** **{eng.day}** **~{time_str}** — **{season}** (**{weather_note}**; see `kenji_state.json` `weather`)",
        f"**Current Location:** {eng.location}. **Kenji** **~{eng.gold} GP, {eng.silver} SP**. {charge_str}. {rel_str}.",
        f"**BOOK 4 — {ch_status}** — `arcs/{arc_path}`. **Pallid March** **shelf** **`pallid_march_south_push_arc.md`**." if arc_path else f"**BOOK 4** — {ch_status}",
        f"**Active Book:** Book 4 — Fraying Empire (The Ronin Arc)",
    ]

    # Find where the old header ends (line starting with "> **Cross-references:**")
    crossref_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("> **Cross-references:**"):
            crossref_idx = i
            break

    if crossref_idx is not None:
        # Replace everything before the cross-references line
        result = new_lines + [""] + lines[crossref_idx:]
    else:
        # Fallback: replace first 6 lines
        result = new_lines + [""] + lines[7:]

    TRACKER_FILE.write_text("\n".join(result), encoding="utf-8")
    print(f"[TRACKER] Header synced — {cal} Day {eng.day} ~{time_str} {weekday}")

    # --- Also update Kenji's Location line and Gold line ---
    text2 = TRACKER_FILE.read_text(encoding="utf-8")
    # Update Kenji Location line
    text2 = re.sub(
        r'(\*\*Location:\*\*) .*?(?=\n)',
        f'\\1 **{eng.location.replace("**", "")}** — **{cal}** **{weekday}** **~{time_str}** **Day** **{eng.day}**. **HP {eng.hp}/{eng.max_hp}**; {charge_str}. **Oathbreaker** **BoH**. **Purse** **~{eng.gold} GP, {eng.silver} SP** (`kenji_state.json`).',
        text2,
        count=1
    )
    # Update Gold line
    text2 = re.sub(
        r'\*\*Gold:\*\* ~[\d,.]+ (?:GP|gp).*?(?=\n)',
        f'**Gold:** ~{eng.gold} GP / {eng.silver} SP (synced `kenji_state.json` Day {eng.day})',
        text2,
        count=1
    )
    # Update Last Updated line for Kenji
    text2 = re.sub(
        r'(\*\*Last Updated:\*\*) .*?(?=\n)',
        f'\\1 {cal} / Day {eng.day} — engine refresh',
        text2,
        count=1
    )

    TRACKER_FILE.write_text(text2, encoding="utf-8")
    print(f"[TRACKER] Kenji block updated — gold {eng.gold} GP / {eng.silver} SP")


def cmd_refresh(eng, args):
    """Re-roll weather, sync tracker headers + Kenji block, write AI_CONTEXT.md, save."""
    print("=" * 50)
    print("ENGINE REFRESH")
    print("=" * 50)

    # 1. Weather
    _refresh_weather(eng)

    # 2. Save state (so weather persists before tracker reads it)
    save(eng)

    # 3. Sync tracker header + Kenji block
    _sync_tracker_header(eng)

    # 4. Write AI_CONTEXT.md
    brief = eng.ai_brief_markdown()
    out = SCRIPT_DIR / "AI_CONTEXT.md"
    out.write_text(brief, encoding="utf-8")
    print(f"[BRIEF] Wrote {out.name} ({len(brief)} chars)")

    # 5. Validate
    warnings = eng.validate()
    if warnings:
        print("\n[!] VALIDATION WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    # Summary
    cal = day_to_calendar(eng.day)
    weekday = day_to_weekday(eng.day)
    hr = int(eng.hour) if isinstance(eng.hour, (int, float)) else eng.hour
    print(f"\n{'=' * 50}")
    print(f"Day {eng.day} ({cal}, {weekday}) ~{hr:02d}:00")
    print(f"Location: {eng.location}")
    print(f"Weather:  {eng.weather}")
    print(f"Gold:     {eng.gold} GP / {eng.silver} SP")
    print(f"HP:       {eng.hp}/{eng.max_hp}")
    charges_display = _build_charge_str(eng).replace("**", "")
    print(f"Charges:  {charges_display}")
    print(f"{'=' * 50}")


def cmd_tick(eng, args):
    hours = int(args[0]) if args else 1
    all_alerts = []
    for _ in range(hours):
        alerts = eng.tick_interaction()
        all_alerts.extend(alerts)
    if all_alerts:
        print("=== ALERTS ===")
        for a in all_alerts:
            print(a)
    save(eng)
    print(f"\nDay {eng.day}, {eng.clock_display()} — {eng.time_of_day()}")
    print(f"Meal: {eng.meal_status()}")


def cmd_rest(eng, args):
    print(f"Long rest: Day {eng.day} → Day {eng.day + 1}")
    results = eng.advance_day()
    if results:
        print("=== DAWN PROCESSING ===")
        for r in results:
            print(r)
    print(f"\nDay {eng.day}, {eng.clock_display()} — {eng.time_of_day()}")
    save(eng)


def cmd_eat(eng, args):
    eng.eat_meal()
    print(f"Ate a meal. Meals remaining: {eng.meals}. {eng.meal_status()}")
    save(eng)


def cmd_move(eng, args):
    if not args:
        print("Usage: move <location>"); return
    loc = " ".join(args)
    eng.set_location(loc)
    print(f"Location → {eng.location} (Weather: {eng.weather})")
    save(eng)


def cmd_dashboard(eng, args):
    print(eng.dashboard())


def cmd_brief(eng, args):
    brief = eng.ai_brief_markdown()
    out = SCRIPT_DIR / "AI_CONTEXT.md"
    out.write_text(brief, encoding="utf-8")
    print(f"[Wrote {out}] ({len(brief)} chars)")


def cmd_receipt(eng, args):
    """Print KENJI_ARC_POINTER_STAMP from run_arc_pointer.py (no log file, no JSON mutation)."""
    script = SCRIPT_DIR / "run_arc_pointer.py"
    cmd = [
        sys.executable,
        str(script),
        "--state",
        str(STATE_FILE),
        "--stamp",
        "--no-log",
    ]
    r = subprocess.run(cmd, cwd=str(SCRIPT_DIR), capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    if r.returncode != 0 and not out:
        print(f"[receipt] exit {r.returncode}", file=sys.stderr)


def cmd_npc(eng, args):
    if len(args) < 3:
        print("Usage: npc <name> <location|activity|disposition> <value>"); return
    name, field = args[0], args[1]
    value = " ".join(args[2:])
    eng.update_npc(name, **{field: value})
    print(f"NPC {name}.{field} → {value}")
    save(eng)


def cmd_squad(eng, args):
    if len(args) < 3:
        print("Usage: squad <name> <status|location|mission> <value>"); return
    name, field = args[0], args[1]
    value = " ".join(args[2:])
    eng.update_squad(name, **{field: value})
    print(f"Squad {name}.{field} → {value}")
    save(eng)


def cmd_rel(eng, args):
    if len(args) < 3:
        print("Usage: rel <npc> <+/-N> <reason>"); return
    npc = args[0]
    change = int(args[1])
    reason = " ".join(args[2:])
    eng.update_relationship(npc, change, reason)
    r = eng.relationships.get(npc, {})
    print(f"{npc}: {r.get('score', 0):+d} ({r.get('tier', '?')}) — {reason}")
    save(eng)


def cmd_clock(eng, args):
    if len(args) < 2:
        print("Usage: clock <name> <+/-N>"); return
    name = args[0]
    delta = int(args[1])
    eng.advance_threat(name, delta)
    clock = eng.threat_clocks.get(name, {})
    print(f"{name}: {clock.get('progress', 0)}% (rate {clock.get('rate', 0)}/day)")
    save(eng)


def cmd_gold(eng, args):
    if not args:
        print("Usage: gold <+/-amount>"); return
    amount = int(args[0])
    if amount >= 0:
        eng.gold += amount
        print(f"+{amount} GP → {eng.gold} GP total")
    else:
        eng.spend_gold(gp=abs(amount))
        print(f"{amount} GP → {eng.gold} GP total")
    save(eng)


def cmd_buff(eng, args):
    if len(args) < 3:
        print("Usage: buff <name> <hours> <effects>"); return
    name = args[0]
    hours = int(args[1])
    effects = " ".join(args[2:])
    eng.add_buff(name, hours, effects)
    print(f"Buff: {name} ({hours}hr) — {effects}")
    save(eng)


def cmd_quest(eng, args):
    if len(args) < 2:
        print("Usage: quest <name> <status> [notes]"); return
    name = args[0]
    status = args[1]
    notes = " ".join(args[2:]) if len(args) > 2 else None
    for q in eng.quests:
        if q["name"].lower().startswith(name.lower()):
            q["status"] = status
            if notes:
                q["notes"] = notes
            print(f"Quest '{q['name']}' → {status}")
            save(eng)
            return
    print(f"Quest not found: {name}")


def cmd_event(eng, args):
    if len(args) < 2:
        print("Usage: event <name> <day> [notes]"); return
    name = args[0]
    day = int(args[1])
    notes = " ".join(args[2:]) if len(args) > 2 else ""
    eng.add_event(name, day, notes=notes)
    print(f"Event added: {name} on Day {day}")
    save(eng)


def cmd_slot(eng, args):
    if len(args) < 2:
        print("Usage: slot <level> <+/-N>  (e.g. slot L2 -1)"); return
    level = args[0]
    delta = int(args[1])
    if level not in eng.spell_slots:
        print(f"Unknown slot level: {level}"); return
    cur, mx = eng.spell_slots[level]
    if delta < 0:
        ok = eng.spend_slot(level, abs(delta))
        if not ok:
            print(f"Not enough L{level} slots ({cur}/{mx})"); return
    else:
        eng.restore_slot(level, delta)
    new_cur = eng.spell_slots[level][0]
    print(f"{level}: {new_cur}/{mx}")
    save(eng)


def cmd_charge(eng, args):
    if len(args) < 2:
        print("Usage: charge <name> <+/-N>  (e.g. charge Recall -1)"); return
    name = args[0]
    delta = int(args[1])
    if name not in eng.charges:
        print(f"Unknown charge: {name}. Available: {', '.join(eng.charges.keys())}"); return
    cur, mx = eng.charges[name]
    if delta < 0:
        ok = eng.spend_charge(name, abs(delta))
        if not ok:
            print(f"Not enough {name} charges ({cur}/{mx})"); return
    else:
        eng.restore_charge(name, delta)
    new_cur = eng.charges[name][0]
    print(f"{name}: {new_cur}/{mx}")
    save(eng)


def cmd_debuff(eng, args):
    if not args:
        print("Usage: debuff <name>  (e.g. debuff Haste)"); return
    name = " ".join(args)
    if eng.remove_buff(name):
        print(f"Removed buff: {name}")
    else:
        print(f"Buff not found: {name}. Active: {', '.join(eng.buffs.keys()) or 'none'}")
    save(eng)


def cmd_chapter_open(eng, args):
    """Generate the mandatory chapter-open report. No state changes."""
    chapter = int(args[0]) if args else eng.extra_json.get("current_chapter", 0)
    if chapter <= 0:
        print("[!] No chapter number provided and none found in state.")
        print("    Usage: chapter_open <chapter_number>")
        print("    Or set current_chapter in kenji_state.json")
        return

    # Determine active PC from engine's char_name
    active_pc = eng.char_name

    report = eng.generate_chapter_open_report(chapter, active_pc)
    print(report)

    # Also write to file for AI consumption
    out = SCRIPT_DIR / "CHAPTER_OPEN_REPORT.md"
    out.write_text(f"<!-- Auto-generated by _dm_turn.py chapter_open -->\n\n{report}\n",
                   encoding="utf-8")
    print(f"\n[Wrote {out.name}] ({len(report)} chars)")


def cmd_chapter_close_receipt(eng, args):
    """Process a YAML chapter receipt to update all trackers."""
    if not args:
        print("Usage: chapter_close_receipt <receipt_file.yaml>")
        return

    receipt_path = Path(args[0])
    if not receipt_path.is_absolute():
        receipt_path = SCRIPT_DIR / receipt_path

    if not receipt_path.exists():
        print(f"ERROR: Receipt file not found: {receipt_path}")
        return

    # Parse YAML receipt
    try:
        import yaml
    except ImportError:
        # Fallback: try to parse as simplified YAML using basic parser
        print("[!] PyYAML not installed. Attempting basic parse...")
        _process_receipt_basic(eng, receipt_path)
        return

    text = receipt_path.read_text(encoding="utf-8")
    receipt = yaml.safe_load(text)
    if isinstance(receipt, dict) and "chapter_receipt" in receipt:
        receipt = receipt["chapter_receipt"]

    _apply_receipt(eng, receipt)
    save(eng)

    # Regenerate AI_CONTEXT.md
    brief = eng.ai_brief_markdown()
    out = SCRIPT_DIR / "AI_CONTEXT.md"
    out.write_text(brief, encoding="utf-8")
    print(f"[SAVED] AI_CONTEXT.md ({len(brief)} chars)")


def _process_receipt_basic(eng, receipt_path: Path):
    """Basic YAML-like parser for receipt files when PyYAML is not available."""
    import json as _json
    text = receipt_path.read_text(encoding="utf-8")

    # Try JSON format first (receipt could be JSON)
    try:
        receipt = _json.loads(text)
        if isinstance(receipt, dict) and "chapter_receipt" in receipt:
            receipt = receipt["chapter_receipt"]
        _apply_receipt(eng, receipt)
        save(eng)
        return
    except _json.JSONDecodeError:
        pass

    print("ERROR: Could not parse receipt file. Use JSON format or install PyYAML.")
    print("  pip install pyyaml --break-system-packages")


def _apply_receipt(eng, receipt: dict):
    """Apply a parsed chapter receipt to engine state."""
    from datetime import datetime

    print(f"{'=' * 60}")
    print(f"CHAPTER CLOSE (from receipt)")
    print(f"{'=' * 60}")

    ch_num = receipt.get("chapter_number", "?")
    print(f"\nChapter: {ch_num}")

    # --- Day/Time ---
    end_day = receipt.get("day_end")
    if end_day and end_day != eng.day:
        old_day = eng.day
        eng.day = int(end_day)
        print(f"[DAY] {old_day} → {eng.day}")

    hours = receipt.get("hours_elapsed")
    if hours:
        eng.hour = (eng.hour + int(hours)) % 24

    # --- Location ---
    loc = receipt.get("location_end")
    if loc and loc != eng.location:
        eng.location = loc
        print(f"[LOCATION] → {loc}")

    # --- EXP ---
    exp_block = receipt.get("exp_earned", {})
    if exp_block:
        combat_exp = int(exp_block.get("combat", 0))
        roleplay_exp = int(exp_block.get("roleplay", 0))
        discovery_exp = int(exp_block.get("discovery", 0))
        total = int(exp_block.get("total", combat_exp + roleplay_exp + discovery_exp))
        justification = exp_block.get("justification", "")

        # Validate total
        calc_total = combat_exp + roleplay_exp + discovery_exp
        if total != calc_total:
            print(f"[!] EXP total mismatch: stated {total}, calculated {calc_total}. Using calculated.")
            total = calc_total

        result = eng.update_exp(int(ch_num) if str(ch_num).isdigit() else 0,
                                combat_exp, roleplay_exp, discovery_exp, justification)
        print(f"[EXP] +{total} ({result['old_exp']:,} → {result['new_exp']:,})")
        if result.get("level_up"):
            print(f"[!!] LEVEL UP available!")
        if result.get("zero_streak_warning"):
            print(f"[!] {result['warning']}")
    else:
        print("[!] WARNING: No exp_earned block in receipt. EXP tracking is mandatory.")

    # --- Gold ---
    gold_block = receipt.get("gold_changes", {})
    if gold_block:
        gained = int(gold_block.get("gained", 0))
        spent = int(gold_block.get("spent", 0))
        notes = gold_block.get("notes", "")

        econ = eng.validate_economy(gained, spent, notes)
        if econ["warnings"]:
            for w in econ["warnings"]:
                print(f"[!] ECONOMY: {w}")

        eng.gold += gained - spent
        print(f"[GOLD] +{gained} / -{spent} = {eng.gold} GP")

    # --- HP ---
    hp_block = receipt.get("hp_changes", {})
    if hp_block:
        if "current_hp" in hp_block:
            eng.hp = int(hp_block["current_hp"])
            print(f"[HP] → {eng.hp}/{eng.max_hp}")

    # --- Goals progressed ---
    for gp in receipt.get("goals_progressed", []):
        gid = gp.get("goal_id", "")
        new_status = gp.get("new_status", "")
        note = gp.get("progress_note", "")
        for g in eng.character_goals:
            if isinstance(g, dict) and g.get("goal_id") == gid:
                if new_status:
                    g["status"] = new_status
                if ch_num and str(ch_num).isdigit():
                    g["last_updated_chapter"] = int(ch_num)
                print(f"[GOAL] {gid} → {new_status or 'updated'}: {note}")
                break

    # --- New goals ---
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
        print(f"[GOAL+] {gn.get('goal_id', '?')}: {gn.get('description', '')}")

    # --- Items ---
    for item in receipt.get("items_gained", []):
        if item not in eng.satchel and item not in eng.key_items:
            eng.key_items.append(item)
            print(f"[ITEM+] {item}")
    for item in receipt.get("items_lost", []):
        if item in eng.satchel:
            eng.satchel.remove(item)
            print(f"[ITEM-] {item}")
        elif item in eng.key_items:
            eng.key_items.remove(item)
            print(f"[ITEM-] {item}")

    # --- Perks triggered ---
    for pt in receipt.get("perks_triggered", []):
        perk_id = pt.get("perk_id", "")
        occurred = pt.get("occurred", False)
        desc = pt.get("description", "")
        if occurred:
            print(f"[PERK] {perk_id}: {desc}")

    # --- NPCs ---
    for nc in receipt.get("npcs_changed", []):
        name = nc.get("name", "")
        change = nc.get("change", "")
        if name:
            print(f"[NPC] {name}: {change}")

    # --- Update chapter counter ---
    if str(ch_num).isdigit():
        eng.extra_json["current_chapter"] = int(ch_num)

    # --- Cover status ---
    cover = receipt.get("cover_status")
    if cover:
        eng.extra_json["cover_status"] = cover

    # --- Notes ---
    notes = receipt.get("notes", "")
    if notes:
        print(f"\n[NOTES] {notes}")

    print(f"\n{'=' * 60}")
    print(f"Chapter {ch_num} receipt applied successfully.")
    print(f"{'=' * 60}")


def cmd_validate(eng, args):
    warnings = eng.validate()
    if warnings:
        print("[!] VALIDATION WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("[OK] State is clean -- no warnings.")


def cmd_save(eng, args):
    save(eng)


# ---------------------------------------------------------------------------
# GAMEMODE — Full DM boot sequence (deterministic, no AI guessing)
# ---------------------------------------------------------------------------

def _load_city_registry(location: str) -> dict:
    """Parse shared_world_continuity.md City Location Registry.
    Returns {city_name: [list of location dicts]} for the city matching `location`."""
    import re
    ttrpg_root = _find_ttrpg_root(SCRIPT_DIR)
    if not ttrpg_root:
        # Try sibling/parent paths
        for candidate in [SCRIPT_DIR.parent.parent, SCRIPT_DIR.parent]:
            swc = candidate / "shared_world_continuity.md"
            if swc.exists():
                ttrpg_root = candidate
                break
    if not ttrpg_root:
        return {"error": "Cannot find TTRPG root (no realm_lore_registry.json)"}

    swc = ttrpg_root / "shared_world_continuity.md"
    if not swc.exists():
        return {"error": f"shared_world_continuity.md not found in {ttrpg_root}"}

    text = swc.read_text(encoding="utf-8")

    # Find City Location Registry section
    registry_start = text.find("## City Location Registry")
    if registry_start == -1:
        return {"error": "No City Location Registry section found"}

    registry_text = text[registry_start:]

    # Parse city sections (### City Name (description))
    city_pattern = re.compile(r'^### (.+?)(?:\n|$)', re.MULTILINE)
    cities = {}
    for m in city_pattern.finditer(registry_text):
        city_header = m.group(1).strip()
        city_name = city_header.split("(")[0].strip()
        # Extract table rows for this city (lines starting with | **)
        start = m.end()
        next_city = city_pattern.search(registry_text, start)
        end = next_city.start() if next_city else len(registry_text)
        section = registry_text[start:end]

        locations = []
        for line in section.split("\n"):
            line = line.strip()
            if line.startswith("| **"):
                # Parse table row: | **Name** | Type | Origin | Owner | Status | Lore |
                cells = [c.strip() for c in line.split("|")[1:-1]]  # skip empty first/last
                if len(cells) >= 6:
                    loc_name = cells[0].replace("**", "").strip()
                    locations.append({
                        "name": loc_name,
                        "type": cells[1].strip(),
                        "origin": cells[2].strip(),
                        "owner": cells[3].strip(),
                        "status_25yr": cells[4].strip(),
                        "lore": cells[5].strip() if len(cells) > 5 else "",
                    })
        if locations:
            cities[city_name] = locations

    # Match current location to a city
    loc_lower = location.lower()
    matched_city = None
    for city_name in cities:
        if city_name.lower() in loc_lower or loc_lower in city_name.lower():
            matched_city = city_name
            break
    # Also check if any location name matches
    if not matched_city:
        for city_name, locs in cities.items():
            for loc in locs:
                if loc["name"].lower() in loc_lower:
                    matched_city = city_name
                    break
            if matched_city:
                break

    if matched_city:
        return {
            "city": matched_city,
            "locations": cities[matched_city],
            "location_count": len(cities[matched_city]),
        }
    else:
        return {
            "city": None,
            "locations": [],
            "note": f"No city registry match for '{location}'. May be wilderness/ruin.",
        }


def _check_deadlines(eng, full_data: dict = None) -> list:
    """Check all scheduled events and quests for due/overdue items."""
    alerts = []
    current_day = eng.day
    current_hour = eng.hour if isinstance(eng.hour, (int, float)) else 0

    # Check engine events
    for ev in eng.events:
        ev_day = ev.get("day", 999)
        ev_name = ev.get("name", "unnamed")
        if ev_day < current_day:
            alerts.append({"name": ev_name, "day": ev_day, "status": "OVERDUE"})
        elif ev_day == current_day:
            alerts.append({"name": ev_name, "day": ev_day, "status": "DUE_TODAY"})
        elif ev_day == current_day + 1:
            alerts.append({"name": ev_name, "day": ev_day, "status": "TOMORROW"})

    # Check quests
    for q in eng.quests:
        q_status = q.get("status", "").lower()
        if q_status in ("complete", "done", "resolved", "failed"):
            continue
        q_name = q.get("name", "unnamed")
        q_due = q.get("due_day", q.get("deadline", None))
        if q_due is not None:
            if isinstance(q_due, (int, float)):
                if q_due < current_day:
                    alerts.append({"name": q_name, "day": int(q_due), "status": "OVERDUE", "type": "quest"})
                elif q_due == current_day:
                    alerts.append({"name": q_name, "day": int(q_due), "status": "DUE_TODAY", "type": "quest"})

    # Also check full_data scheduled_events if available (nested state format)
    if full_data:
        sched = full_data.get("scheduled_events", full_data.get("_story_engine_state", {}).get("events", []))
        if isinstance(sched, list):
            for ev in sched:
                if isinstance(ev, dict):
                    ev_day = ev.get("day", 999)
                    ev_name = ev.get("name", ev.get("event", "unnamed"))
                    if ev_day < current_day:
                        alerts.append({"name": ev_name, "day": ev_day, "status": "OVERDUE"})
                    elif ev_day == current_day:
                        alerts.append({"name": ev_name, "day": ev_day, "status": "DUE_TODAY"})

    # Deduplicate by name
    seen = set()
    unique = []
    for a in alerts:
        if a["name"] not in seen:
            seen.add(a["name"])
            unique.append(a)
    return unique


def _read_narrator_style(full_data: dict) -> str:
    """Extract narrator_style from character_world_state.json."""
    pi = full_data.get("player_input", {})
    style = pi.get("narrator_style", "")
    if not style:
        style = "Aleron Kong (irreverent, funny, mechanics-in-prose)"
    return style


def cmd_gamemode(eng, args):
    """Full DM boot sequence. Deterministic — runs all systems, returns structured report.

    Usage: gamemode [player action text]
    Example: gamemode go back up team four against the spiders
    """
    import json as _json

    player_action = " ".join(args) if args else ""

    report = {
        "command": "gamemode",
        "status": "OK",
        "errors": [],
        "warnings": [],
    }

    # ── 1. LOAD & BRIEF ──────────────────────────────────────────────────
    print("=" * 60)
    print("GAMEMODE — DM BOOT SEQUENCE")
    print("=" * 60)

    # Write fresh AI_CONTEXT.md
    try:
        brief_text = eng.ai_brief_markdown()
        out = SCRIPT_DIR / "AI_CONTEXT.md"
        out.write_text(brief_text, encoding="utf-8")
        report["brief"] = "OK"
        print(f"[1/6] BRIEF — wrote AI_CONTEXT.md ({len(brief_text)} chars)")
    except Exception as e:
        report["brief"] = f"FAILED: {e}"
        report["errors"].append(f"Brief failed: {e}")
        print(f"[1/6] BRIEF — FAILED: {e}")

    # ── 2. CHARACTER STATE ────────────────────────────────────────────────
    # Load full data for nested state files (Cookie etc.)
    full_data = {}
    try:
        full_data = _json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass

    cal = day_to_calendar(eng.day)
    weekday = day_to_weekday(eng.day)
    hr = int(eng.hour) if isinstance(eng.hour, (int, float)) else eng.hour
    time_str = f"{hr:02d}:00" if isinstance(hr, int) else str(hr)

    state_summary = {
        "character": eng.char_name,
        "level": eng.level,
        "exp": getattr(eng, "exp", 0),
        "exp_to_next": getattr(eng, "exp_to_next_level", 0),
        "day": eng.day,
        "hour": hr,
        "calendar": f"{weekday}, {cal} 1247 AR",
        "location": eng.location,
        "weather": eng.weather,
        "hp": eng.hp,
        "max_hp": eng.max_hp,
        "ac": getattr(eng, "ac", 0),
        "gold": eng.gold,
        "silver": eng.silver,
        "copper": getattr(eng, "copper", 0),
        "spell_slots": dict(eng.spell_slots) if eng.spell_slots else {},
        "charges": {k: {"current": v[0], "max": v[1]} for k, v in eng.charges.items()} if eng.charges else {},
        "buffs": list(eng.buffs.keys()) if eng.buffs else [],
        "meals": eng.meals,
        "hours_since_meal": eng.hours_since_meal,
    }

    # Chapter info from full_data
    chapter = full_data.get("_chapter", 0)
    chapter_status = full_data.get("_chapter_status", "")
    chapter_title = full_data.get("_chapter_title", "")
    state_summary["chapter"] = chapter
    state_summary["chapter_status"] = chapter_status
    state_summary["chapter_title"] = chapter_title

    report["state"] = state_summary
    print(f"[2/6] STATE — {eng.char_name} L{eng.level} | Day {eng.day} {time_str} | {eng.location}")

    # ── 3. CONTINUITY ENGINE ──────────────────────────────────────────────
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        import continuity_engine as ce
        load_msg = ce.load_campaign(eng.char_name.lower())
        report["continuity_load"] = load_msg

        # Build state dict for check_engine
        ce_state = {
            "hour": eng.hour,
            "day": eng.day,
            "location": eng.location,
            "hp": eng.hp,
            "max_hp": eng.max_hp,
            "exp": getattr(eng, "exp", 0),
            "meals": eng.meals,
            "hours_since_meal": eng.hours_since_meal,
            "weather": eng.weather,
            "npcs_in_scene": [],
            "threat_id": "",
            "aura_targets": [],
            "active_buffs": list(eng.buffs.keys()) if eng.buffs else [],
            "charges": {k: v[0] for k, v in eng.charges.items()} if eng.charges else {},
        }
        ce_report = ce.check_engine(ce_state)
        report["continuity_check"] = ce_report
        # Count issues
        issue_count = ce_report.count("!!") + ce_report.count("MISSING") + ce_report.count("BROKEN")
        if issue_count > 0:
            report["warnings"].append(f"Continuity: {issue_count} issue(s) flagged")
        print(f"[3/6] CONTINUITY — loaded {eng.char_name}, {issue_count} issue(s)")
    except Exception as e:
        report["continuity_load"] = f"FAILED: {e}"
        report["continuity_check"] = ""
        report["errors"].append(f"Continuity engine failed: {e}")
        print(f"[3/6] CONTINUITY — FAILED: {e}")

    # ── 4. CITY LOCATION REGISTRY ─────────────────────────────────────────
    city_data = _load_city_registry(eng.location)
    report["city_registry"] = city_data
    city_name = city_data.get("city", "none")
    loc_count = city_data.get("location_count", 0)
    print(f"[4/6] CITY REGISTRY — {city_name or 'no match'} ({loc_count} locations)")

    # ── 5. NARRATOR STYLE ─────────────────────────────────────────────────
    narrator = _read_narrator_style(full_data)
    report["narrator_style"] = narrator
    print(f"[5/6] NARRATOR — {narrator[:60]}")

    # ── 6. DEADLINE CHECK ─────────────────────────────────────────────────
    deadlines = _check_deadlines(eng, full_data)
    report["deadlines"] = deadlines
    overdue = [d for d in deadlines if d["status"] == "OVERDUE"]
    due_today = [d for d in deadlines if d["status"] == "DUE_TODAY"]
    if overdue:
        report["warnings"].extend([f"OVERDUE: {d['name']} (Day {d['day']})" for d in overdue])
    print(f"[6/6] DEADLINES — {len(overdue)} overdue, {len(due_today)} due today, {len(deadlines)} total")

    # ── PLAYER ACTION ─────────────────────────────────────────────────────
    if player_action:
        report["player_action"] = player_action
        print(f"\n[ACTION] \"{player_action}\"")

    # ── DASHBOARD ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("DASHBOARD")
    print(f"{'=' * 60}")

    # Build compact dashboard
    slots_str = " | ".join(f"L{k}: {v[0]}/{v[1]}" for k, v in sorted(eng.spell_slots.items())) if eng.spell_slots else "none"
    charges_str = _build_charge_str(eng).replace("**", "") if eng.charges else "none"

    print(f"  {eng.char_name} — Day {eng.day} | {time_str} | {eng.location}")
    print(f"  HP {eng.hp}/{eng.max_hp} | AC {getattr(eng, 'ac', '?')} | Level {eng.level} ({getattr(eng, 'exp', 0):,}/{getattr(eng, 'exp', 0) + getattr(eng, 'exp_to_next_level', 0):,})")
    print(f"  GP {eng.gold} | SP {eng.silver} | CP {getattr(eng, 'copper', 0)}")
    print(f"  Slots: {slots_str}")
    if eng.charges:
        print(f"  Charges: {charges_str}")
    if eng.buffs:
        print(f"  Buffs: {', '.join(eng.buffs.keys())}")
    print(f"  Weather: {eng.weather}")
    print(f"  Meals: {eng.meals} | Hours since meal: {eng.hours_since_meal}")
    if deadlines:
        print(f"  Deadlines:")
        for d in deadlines:
            print(f"    [{d['status']}] {d['name']} — Day {d['day']}")

    print(f"\n{'=' * 60}")
    if report["errors"]:
        print(f"ERRORS: {len(report['errors'])}")
        for e in report["errors"]:
            print(f"  !! {e}")
    if report["warnings"]:
        print(f"WARNINGS: {len(report['warnings'])}")
        for w in report["warnings"]:
            print(f"  ! {w}")
    if not report["errors"] and not report["warnings"]:
        print("ALL SYSTEMS GREEN")
    print(f"{'=' * 60}")

    # ── JSON OUTPUT (for AI consumption) ──────────────────────────────────
    # Write to file so AI can read it even if stdout is truncated
    report_path = SCRIPT_DIR / "GAMEMODE_REPORT.json"
    report_path.write_text(_json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"\n[REPORT] Wrote GAMEMODE_REPORT.json")


COMMANDS = {
    "refresh": cmd_refresh,
    "tick": cmd_tick,
    "rest": cmd_rest,
    "eat": cmd_eat,
    "move": cmd_move,
    "dashboard": cmd_dashboard,
    "brief": cmd_brief,
    "chapter_open": cmd_chapter_open,
    "chapter_close_receipt": cmd_chapter_close_receipt,
    "receipt": cmd_receipt,
    "npc": cmd_npc,
    "squad": cmd_squad,
    "rel": cmd_rel,
    "clock": cmd_clock,
    "gold": cmd_gold,
    "buff": cmd_buff,
    "debuff": cmd_debuff,
    "slot": cmd_slot,
    "charge": cmd_charge,
    "quest": cmd_quest,
    "event": cmd_event,
    "validate": cmd_validate,
    "save": cmd_save,
    "gamemode": cmd_gamemode,
}

if __name__ == "__main__":
    # Parse --character flag
    argv = list(sys.argv[1:])
    character_override = None
    if "--character" in argv:
        idx = argv.index("--character")
        if idx + 1 < len(argv):
            character_override = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2:]
        else:
            print("ERROR: --character requires a name argument")
            sys.exit(1)


    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        if argv:
            print(f"Unknown command: {argv[0]}")
        sys.exit(1)

    cmd = argv[0]
    args = argv[1:]

    # Resolve state file from --character flag
    if character_override:
        STATE_FILE = resolve_state_file(character_override)
        print(f"[CHARACTER] Loading: {STATE_FILE.name}")

    if cmd == "receipt":
        cmd_receipt(None, args)
    else:
        eng = load()
        COMMANDS[cmd](eng, args)
