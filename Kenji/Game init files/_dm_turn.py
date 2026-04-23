#!/usr/bin/env python3
"""Single state-mutation interface for the Kenji TTRPG.

Usage:
    python _dm_turn.py <command> [args...]

Commands:
    refresh                       Re-roll weather, sync tracker headers, write AI_CONTEXT.md, save.
    tick                          Advance 1 hour (tick_interaction), print alerts, save.
    tick <N>                      Advance N hours via repeated tick_interaction calls.
    rest                          Long rest (advance_day + full daily pipeline), save.
    eat                           Eat a meal from satchel, save.
    move <location>               Change location, save.
    dashboard                     Print dashboard (no save).
    brief                         Generate AI_CONTEXT.md + print brief (no save).
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
    validate                      Run consistency checks, print warnings.
    save                          Just save current engine state to JSON.
"""
import random
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR / "kenji_state.json"
TRACKER_FILE = SCRIPT_DIR / "character_tracker.md"

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


def load():
    return StoryEngine.load_json(str(STATE_FILE))


def save(eng):
    eng.save_json(str(STATE_FILE))
    warnings = eng.validate()
    if warnings:
        print("\n[!] VALIDATION WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    print(f"\n[OK] Saved -> {STATE_FILE.name} (v{eng._save_version})")


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


COMMANDS = {
    "refresh": cmd_refresh,
    "tick": cmd_tick,
    "rest": cmd_rest,
    "eat": cmd_eat,
    "move": cmd_move,
    "dashboard": cmd_dashboard,
    "brief": cmd_brief,
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
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        if len(sys.argv) >= 2:
            print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "receipt":
        cmd_receipt(None, args)
    else:
        eng = load()
        COMMANDS[cmd](eng, args)
