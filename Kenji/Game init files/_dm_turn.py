#!/usr/bin/env python3
"""Single state-mutation interface for the Kenji TTRPG.

Usage:
    python _dm_turn.py <command> [args...]

Commands:
    tick                          Advance 1 hour (tick_interaction), print alerts, save.
    tick <N>                      Advance N hours via repeated tick_interaction calls.
    rest                          Long rest (advance_day + full daily pipeline), save.
    eat                           Eat a meal from satchel, save.
    move <location>               Change location, save.
    dashboard                     Print dashboard (no save).
    brief                         Generate AI_CONTEXT.md + print brief (no save).
    npc <name> <field> <value>    Update NPC field (location|activity|disposition), save.
    squad <name> <field> <value>  Update squad field (status|location|mission), save.
    rel <npc> <change> <reason>   Update relationship (+/-N and reason), save.
    clock <name> <delta>          Manually adjust a threat clock, save.
    gold <amount>                 Add (positive) or subtract (negative) gold, save.
    buff <name> <hours> <effects> Add a buff, save.
    quest <name> <status> [notes] Update quest status, save.
    event <name> <day> [notes]    Add a scheduled event, save.
    validate                      Run consistency checks, print warnings.
    save                          Just save current engine state to JSON.
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR / "kenji_state.json"

sys.path.insert(0, str(SCRIPT_DIR))
from ttrpg_game_engine import StoryEngine


def load():
    return StoryEngine.load_json(str(STATE_FILE))


def save(eng):
    eng.save_json(str(STATE_FILE))
    warnings = eng.validate()
    if warnings:
        print("\n⚠️  VALIDATION WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    print(f"\n✅ Saved → {STATE_FILE.name}")


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
    print(f"\nDay {eng.day}, Hour {eng.hour:02d}:00 — {eng.time_of_day()}")
    print(f"Meal: {eng.meal_status()}")
    save(eng)


def cmd_rest(eng, args):
    print(f"Long rest: Day {eng.day} → Day {eng.day + 1}")
    results = eng.advance_day()
    if results:
        print("=== DAWN PROCESSING ===")
        for r in results:
            print(r)
    print(f"\nDay {eng.day}, Hour {eng.hour:02d}:00 — {eng.time_of_day()}")
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
    print(f"[Wrote {out}]")
    print(brief)


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


def cmd_validate(eng, args):
    warnings = eng.validate()
    if warnings:
        print("⚠️  VALIDATION WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✅ State is clean — no warnings.")


def cmd_save(eng, args):
    save(eng)


COMMANDS = {
    "tick": cmd_tick,
    "rest": cmd_rest,
    "eat": cmd_eat,
    "move": cmd_move,
    "dashboard": cmd_dashboard,
    "brief": cmd_brief,
    "npc": cmd_npc,
    "squad": cmd_squad,
    "rel": cmd_rel,
    "clock": cmd_clock,
    "gold": cmd_gold,
    "buff": cmd_buff,
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

    eng = load()
    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](eng, args)
