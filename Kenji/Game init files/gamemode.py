#!/usr/bin/env python3
"""GAMEMODE — Full DM boot sequence + Combat engine.

Deterministic pre-flight that runs ALL game systems before the AI narrates.
No prose, no guessing — code does the work.

Usage:
    python gamemode.py [--character <name>] [player action text...]

Examples:
    python gamemode.py --character cookie help with spiders
    python gamemode.py --character cookie engage spiders with tai chi
    python gamemode.py                          # defaults to kenji
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Import game engine components
# ---------------------------------------------------------------------------
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from _dm_turn import (
        resolve_state_file, load, save, _build_charge_str,
        day_to_calendar, day_to_weekday, _find_ttrpg_root,
        STATE_FILE as _DEFAULT_STATE,
    )
    import _dm_turn
except ImportError as e:
    print(f"FATAL: Cannot import _dm_turn: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from ttrpg_game_engine import (
        StoryEngine, Combat, Combatant, load_combatant, load_ability,
        d20, roll_dice, Status,
    )
except ImportError as e:
    print(f"FATAL: Cannot import ttrpg_game_engine: {e}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Truncation-safe JSON loader
# ---------------------------------------------------------------------------

def _extract_story_engine_state(raw: str) -> dict:
    idx = raw.find('"_story_engine_state"')
    if idx < 0:
        return None
    brace_start = raw.find('{', idx)
    if brace_start < 0:
        return None
    depth = 0
    for i in range(brace_start, len(raw)):
        if raw[i] == '{':
            depth += 1
        elif raw[i] == '}':
            depth -= 1
            if depth == 0:
                block = raw[brace_start:i + 1]
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    return None
    return None


def _extract_top_level_fields(raw: str) -> dict:
    result = {}
    for field in ("_chapter", "_chapter_status", "_chapter_title"):
        pattern = rf'"{field}"\s*:\s*("(?:[^"\\]|\\.)*?"|\d+|true|false|null)'
        m = re.search(pattern, raw)
        if m:
            val = m.group(1)
            if val.startswith('"'):
                result[field] = val.strip('"')
            elif val.isdigit():
                result[field] = int(val)
            else:
                result[field] = val
    ns_match = re.search(r'"narrator_style"\s*:\s*"([^"]*)"', raw)
    if ns_match:
        result["narrator_style"] = ns_match.group(1)
    return result


def _extract_full_sections(raw: str) -> dict:
    """Try to extract full JSON sections even from truncated files."""
    result = {}
    for section_name in ("mechanical_state", "ember_inheritance", "persistent_effects",
                         "main_cast", "extra_npcs", "antagonist", "player_input"):
        pattern = f'"{section_name}"\\s*:'
        m = re.search(pattern, raw)
        if not m:
            continue
        rest = raw[m.end():].lstrip()
        if not rest:
            continue
        opener = rest[0]
        if opener == '{':
            closer = '}'
        elif opener == '[':
            closer = ']'
        else:
            continue
        start = m.end() + (len(raw[m.end():]) - len(rest))
        depth = 0
        for i in range(start, len(raw)):
            if raw[i] == opener:
                depth += 1
            elif raw[i] == closer:
                depth -= 1
                if depth == 0:
                    block = raw[start:i + 1]
                    try:
                        result[section_name] = json.loads(block)
                    except json.JSONDecodeError:
                        pass
                    break
    return result


# ---------------------------------------------------------------------------
# Monster Stat Block Registry — real D&D 5e stats
# Each entry has a "keywords" list for flexible matching.
# If ANY keyword appears as a substring in the player action, it matches.
# ---------------------------------------------------------------------------

MONSTER_REGISTRY = {
    "phase_spider": {
        "name": "Phase Spider", "max_hp": 32, "ac": 13,
        "speed": 30, "base_speed": 30,
        "stats": {"str": 1, "dex": 2, "con": 1, "int": -2, "wis": 0, "cha": -2},
        "proficiency": 2, "attack_bonus": 4, "initiative_mod": 2,
        "stealth_mod": 6, "perception_mod": 0,
        "keywords": ["spider", "phase"],
        "abilities": [
            {
                "name": "Bite", "action_type": "action",
                "damage": "1d10+2", "damage_type": "piercing",
                "description": "Melee Weapon Attack: +4 to hit, reach 5 ft. "
                               "Hit: 1d10+2 piercing + 4d8 poison (target makes DC 11 CON save; "
                               "success = half poison damage; fail on save by 5+ = poisoned for 1 hr, "
                               "paralyzed while poisoned this way). If poison reduces to 0 HP, target "
                               "is stable but poisoned 1 hr and paralyzed.",
            },
            {
                "name": "Ethereal Jaunt", "action_type": "bonus_action",
                "description": "Shift to Ethereal Plane from Material, or back. "
                               "While ethereal: visible as faint shimmer, can see/hear Material "
                               "Plane (greyed, 60 ft). Cannot affect or be affected by anything on "
                               "the other plane.",
            },
        ],
        "tags": ["monstrosity", "spider"],
        "morale_threshold": 0.25,
        "notes": "CR 3 (700 XP). Darkvision 60 ft. Web sense. "
                 "Ethereal ambush: advantage on attack if enters from Ethereal Plane same turn.",
    },
}


def _lookup_monster(name_or_key: str) -> dict:
    """Look up a monster in the registry. Case-insensitive, partial match."""
    key = name_or_key.lower().replace(" ", "_")
    if key in MONSTER_REGISTRY:
        return MONSTER_REGISTRY[key]
    for k, v in MONSTER_REGISTRY.items():
        if key in k or key in v["name"].lower():
            return v
    return None


# ---------------------------------------------------------------------------
# PC Combatant builder — converts character_world_state.json into
# a load_combatant()-compatible dict
# ---------------------------------------------------------------------------

def _build_pc_combatant(full_data: dict, eng) -> dict:
    """Build a Combatant dict from character state. Feeds into load_combatant()."""
    ms = full_data.get("mechanical_state", {})
    scores = ms.get("ability_scores", {})

    stats = {}
    for stat in ("str", "dex", "con", "int", "wis", "cha"):
        s = scores.get(stat.upper(), {})
        if isinstance(s, dict):
            stats[stat] = s.get("mod", 0)
        else:
            stats[stat] = 0

    level = eng.level
    prof = 2 + (level - 1) // 4

    spell_slots = {}
    if eng.spell_slots:
        for k, v in eng.spell_slots.items():
            if isinstance(v, (list, tuple)):
                spell_slots[int(k)] = list(v)
            else:
                spell_slots[int(k)] = [v, v]

    abilities = []
    for feat in (ms.get("class_features", []) or []):
        if isinstance(feat, dict):
            mechanics = feat.get("mechanics", {})
            atype = "action"
            if "bonus" in feat.get("name", "").lower():
                atype = "bonus_action"
            abilities.append({
                "name": feat["name"],
                "action_type": atype,
                "description": feat.get("description", ""),
                "extra": {"mechanics": mechanics} if mechanics else {},
            })

    for spell in (ms.get("spells_known", []) or []):
        if isinstance(spell, dict):
            ct = spell.get("casting_time", "1 action").lower()
            if "bonus" in ct:
                atype = "bonus_action"
            elif "reaction" in ct:
                atype = "reaction"
            else:
                atype = "action"
            abilities.append({
                "name": spell["name"],
                "action_type": atype,
                "slot_level": spell.get("level", 1),
                "description": spell.get("effect", spell.get("description", "")),
            })

    ei = full_data.get("ember_inheritance", {})
    ember_abs = ei.get("abilities", {})
    for key, label in [("passive", "passive"), ("active", "active"), ("surge", "surge")]:
        ea = ember_abs.get(key, {})
        if ea and isinstance(ea, dict) and ea.get("name"):
            atype = "bonus_action" if key == "active" else "action"
            raw_charges = ea.get("uses_per_day", 0) if key != "passive" else 0
            # Parse int from strings like "3 (scales with level)"
            if isinstance(raw_charges, str):
                m = re.match(r'(\d+)', raw_charges)
                charges = int(m.group(1)) if m else 0
            else:
                charges = int(raw_charges) if raw_charges else 0
            abilities.append({
                "name": ea["name"],
                "action_type": atype if key != "passive" else "passive",
                "max_charges": charges,
                "charges": charges,
                "description": ea.get("mechanical_effect", ea.get("description", "")),
            })

    perks = []
    pe = full_data.get("persistent_effects", {})
    for eff in pe.get("on_pc", []):
        if isinstance(eff, dict):
            perks.append({
                "name": eff.get("effect_name", "?"),
                "condition": "always",
                "effect": "narrative",
                "value": 0,
                "description": eff.get("mechanical_effect", ""),
            })

    atk_mod = max(stats.get("str", 0), stats.get("dex", 0))

    return {
        "name": eng.char_name,
        "max_hp": eng.max_hp,
        "hp": eng.hp,
        "temp_hp": getattr(eng, "temp_hp", 0),
        "ac": getattr(eng, "ac", 10),
        "base_ac": getattr(eng, "ac", 10),
        "stats": stats,
        "proficiency": prof,
        "attack_bonus": atk_mod + prof,
        "speed": 30,
        "base_speed": 30,
        "initiative_mod": stats.get("dex", 0),
        "spell_slots": spell_slots,
        "spell_save_dc": 8 + prof + stats.get("cha", 0),
        "spell_attack": prof + stats.get("cha", 0),
        "concentration_save_mod": stats.get("con", 0),
        "abilities": abilities,
        "disposition": "friendly",
        "perks": perks,
    }


def _build_ally_combatants(scene_npcs: list) -> list:
    """Build simplified combatant dicts for scene allies."""
    allies = []
    for npc in scene_npcs:
        source = npc.get("source", "")
        name = npc.get("name", "?")
        combat_abs = npc.get("combat_abilities", [])

        if source.startswith("cross_campaign"):
            scores = npc.get("ability_scores", {})
            stats = {}
            for stat in ("str", "dex", "con", "int", "wis", "cha"):
                s = scores.get(stat.upper(), {})
                stats[stat] = s.get("mod", 0) if isinstance(s, dict) else 0
            level = npc.get("level", 5) if isinstance(npc.get("level"), int) else 5
            prof = 2 + (level - 1) // 4
            hp_str = str(npc.get("hp", "20/20"))
            if "/" in hp_str:
                parts = hp_str.split("/")
                try:
                    hp = int(parts[0])
                    max_hp = int(parts[1])
                except ValueError:
                    hp = max_hp = 20
            else:
                hp = max_hp = int(hp_str) if hp_str.isdigit() else 20
            ab_list = []
            for feat in npc.get("class_features", []):
                if isinstance(feat, dict):
                    ab_list.append({
                        "name": feat.get("name", "?"),
                        "action_type": "action",
                        "description": feat.get("mechanical_effect", ""),
                    })
            allies.append({
                "name": name, "max_hp": max_hp, "hp": hp,
                "ac": npc.get("ac", 14) if isinstance(npc.get("ac"), int) else 14,
                "stats": stats, "proficiency": prof,
                "attack_bonus": max(stats.get("str", 0), stats.get("dex", 0)) + prof,
                "speed": 30, "initiative_mod": stats.get("dex", 0),
                "abilities": ab_list, "disposition": "friendly",
            })
        elif combat_abs:
            ab_list = []
            for ca in combat_abs:
                if isinstance(ca, dict):
                    ab_list.append({
                        "name": ca.get("name", "?"),
                        "action_type": "action",
                        "description": ca.get("effect", ""),
                    })
            allies.append({
                "name": name, "max_hp": 25, "hp": 25, "ac": 14,
                "stats": {"str": 1, "dex": 1, "con": 1, "int": 0, "wis": 0, "cha": 0},
                "proficiency": 2, "attack_bonus": 4, "speed": 30,
                "initiative_mod": 1, "abilities": ab_list,
                "disposition": "friendly",
            })
    return allies


# ---------------------------------------------------------------------------
# Combat State Persistence — COMBAT_STATE.json
# ---------------------------------------------------------------------------

def _serialize_combatant(c: Combatant) -> dict:
    """Serialize a Combatant to a JSON-safe dict."""
    abilities = []
    for name, ab in c.abilities.items():
        abilities.append({
            "name": ab.name, "action_type": ab.action_type,
            "cost_type": ab.cost_type, "cost_amount": ab.cost_amount,
            "slot_level": ab.slot_level, "max_charges": ab.max_charges,
            "charges": ab.charges, "cooldown": ab.cooldown,
            "cooldown_remaining": ab.cooldown_remaining,
            "is_reaction": ab.is_reaction, "damage": ab.damage,
            "damage_type": ab.damage_type, "save_stat": ab.save_stat,
            "save_dc": ab.save_dc, "description": ab.description,
            "active": ab.active, "tags": ab.tags, "extra": ab.extra,
        })
    statuses = []
    for s in c.statuses:
        statuses.append({
            "name": s.name, "category": s.category, "duration": s.duration,
            "round_applied": s.round_applied, "source": s.source,
            "compound_clears": s.compound_clears,
        })
    return {
        "name": c.name, "max_hp": c.max_hp, "hp": c.hp, "temp_hp": c.temp_hp,
        "ac": c.ac, "base_ac": c.base_ac, "stats": c.stats,
        "proficiency": c.proficiency, "attack_bonus": c.attack_bonus,
        "flat_attack_bonus": c.flat_attack_bonus,
        "spell_attack": c.spell_attack, "spell_save_dc": c.spell_save_dc,
        "crit_range": c.crit_range, "speed": c.speed, "base_speed": c.base_speed,
        "initiative_mod": c.initiative_mod,
        "spell_slots": {str(k): list(v) for k, v in c.spell_slots.items()},
        "ki": c.ki, "ki_max": c.ki_max,
        "abilities": abilities, "buffs": dict(c.buffs),
        "statuses": statuses,
        "concentrating_on": c.concentrating_on,
        "concentration_save_mod": c.concentration_save_mod,
        "action_used": c.action_used, "bonus_action_used": c.bonus_action_used,
        "extra_action_used": c.extra_action_used,
        "reaction_used": c.reaction_used, "reaction_name": c.reaction_name,
        "movement_remaining": c.movement_remaining,
        "has_cunning_action": c.has_cunning_action,
        "has_extra_action": c.has_extra_action,
        "position": c.position, "elevation": c.elevation,
        "alive": c.alive, "conscious": c.conscious,
        "disposition": c.disposition, "perks": c.perks,
        "morale_threshold": c.morale_threshold, "has_fled": c.has_fled,
        "tags": c.tags, "notes": c.notes,
        "weapon_config": c.weapon_config, "weapon_configs": c.weapon_configs,
        "vulnerabilities": c.vulnerabilities, "immunities": c.immunities,
        "death_throes": c.death_throes,
        "legendary_actions": c.legendary_actions_max,
        "legendary_action_options": c.legendary_action_options,
        "legendary_resistances": c.legendary_resistances_max,
        "phases": c.phases, "current_phase": c.current_phase,
        "theme": c.theme,
    }


def _serialize_combat(combat: Combat) -> dict:
    fighters = {}
    for name, c in combat.fighters.items():
        fighters[name] = _serialize_combatant(c)
    return {
        "round": combat.round, "turn_idx": combat.turn_idx,
        "order": combat.order, "fighters": fighters,
        "log": combat.log[-50:], "active": combat.active,
        "zones": combat.zones,
    }


def _deserialize_combat(data: dict) -> Combat:
    combat = Combat()
    combat.round = data.get("round", 1)
    combat.turn_idx = data.get("turn_idx", -1)
    combat.order = [tuple(x) for x in data.get("order", [])]
    combat.active = data.get("active", True)
    combat.log = data.get("log", [])
    combat.zones = data.get("zones", [])

    for name, fdata in data.get("fighters", {}).items():
        saved_statuses = fdata.pop("statuses", [])
        saved_action_used = fdata.pop("action_used", False)
        saved_bonus_used = fdata.pop("bonus_action_used", False)
        saved_extra_used = fdata.pop("extra_action_used", False)
        saved_reaction_used = fdata.pop("reaction_used", False)
        saved_reaction_name = fdata.pop("reaction_name", "")
        saved_movement = fdata.pop("movement_remaining", 30)
        saved_alive = fdata.pop("alive", True)
        saved_conscious = fdata.pop("conscious", True)
        saved_current_phase = fdata.pop("current_phase", 0)

        c = load_combatant(fdata)
        c.action_used = saved_action_used
        c.bonus_action_used = saved_bonus_used
        c.extra_action_used = saved_extra_used
        c.reaction_used = saved_reaction_used
        c.reaction_name = saved_reaction_name
        c.movement_remaining = saved_movement
        c.alive = saved_alive
        c.conscious = saved_conscious
        c.current_phase = saved_current_phase

        for sd in saved_statuses:
            s = Status(
                name=sd["name"], category=sd.get("category", "condition"),
                duration=sd.get("duration", -1),
                round_applied=sd.get("round_applied", 0),
                source=sd.get("source", ""),
                compound_clears=sd.get("compound_clears", ""),
            )
            c.statuses.append(s)

        combat.fighters[name] = c
    return combat


def _get_combat_state_path(character: str) -> Path:
    state_file = resolve_state_file(character)
    return state_file.parent / "COMBAT_STATE.json"


def _load_combat_state(character: str) -> tuple:
    path = _get_combat_state_path(character)
    if not path.exists():
        return None, None
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw or raw == "{}":
            return None, None
        data = json.loads(raw)
        if not data.get("combat", {}).get("fighters"):
            return None, None
        combat = _deserialize_combat(data.get("combat", {}))
        meta = data.get("meta", {})
        return combat, meta
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"  WARNING: COMBAT STATE CORRUPT: {e}")
        return None, None


def _save_combat_state(combat: Combat, character: str, meta: dict = None):
    path = _get_combat_state_path(character)
    data = {
        "meta": meta or {},
        "combat": _serialize_combat(combat),
        "saved_at": __import__("datetime").datetime.utcnow().isoformat(),
    }
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    return path


def _clear_combat_state(character: str):
    path = _get_combat_state_path(character)
    if path.exists():
        try:
            path.unlink()
        except PermissionError:
            # Sandbox may block delete; truncate instead
            path.write_text("{}", encoding="utf-8")


# ---------------------------------------------------------------------------
# Combat section helpers
# ---------------------------------------------------------------------------

def _print_combat_dashboard(combat: Combat, whose_turn: str = ""):
    print(f"\n{'=' * 60}")
    print(f"ACTIVE COMBAT — ROUND {combat.round}")
    print(f"{'=' * 60}")

    print(f"\n  INITIATIVE ORDER:")
    for init, name in combat.order:
        f = combat.fighters[name]
        marker = " << CURRENT" if name == whose_turn else ""
        alive = "" if f.alive else " [DEAD]"
        print(f"    {init:>2}  {name}{alive}{marker}")

    print(f"\n  COMBATANT STATUS:")
    for _, name in combat.order:
        f = combat.fighters[name]
        if not f.alive:
            print(f"  [{name}] DEAD")
            continue
        print(f"  {f.status_line()}")
        print(f"    {f.action_economy_line()}")

    if combat.zones:
        print(f"\n  ACTIVE ZONES:")
        for z in combat.zones:
            rem = z.get('rounds_remaining', 'permanent')
            print(f"    {z['name']} — pos {z['position']}ft, r{z['radius']}ft, {rem}rd")

    if whose_turn:
        f = combat.fighters.get(whose_turn)
        if f:
            print(f"\n  >>> {whose_turn}'s TURN <<<")
            print(f"  {f.action_economy_line()}")
            avail = f.available_abilities()
            if avail:
                print(f"  Available abilities: {', '.join(avail.keys())}")

    print(f"{'=' * 60}")


def _find_target(combat: Combat, text: str, default_side: str = "enemy", pc_name: str = "") -> str:
    """Find best combat target from player text. Returns fighter name or ''."""
    text_lower = text.lower()
    alive = {n: f for n, f in combat.fighters.items() if f.alive}

    # Direct name match (case-insensitive)
    for name in alive:
        if name.lower() in text_lower:
            return name

    # Numbered target: "spider 1", "spider 2"
    for name in alive:
        words = name.lower().split()
        base = words[0] if words else ""
        if base and base in text_lower:
            return name

    # Fallback: first alive enemy (for attack) or ally (for heal)
    if default_side == "enemy":
        enemies = [n for n, f in alive.items() if f.disposition in ("hostile", "") and n != pc_name]
        return enemies[0] if enemies else ""
    else:
        allies = [n for n, f in alive.items() if n != pc_name]
        return allies[0] if allies else ""


def _classify_action(text: str, pc_abilities: list) -> dict:
    """Classify player combat text into action type + details."""
    t = text.lower()
    result = {"type": "unknown", "action_cost": "action", "ability": None,
              "target_hint": text, "raw": text}

    # Flee / disengage (check first — unambiguous)
    if any(kw in t for kw in ["flee", "run away", "disengage", "retreat"]):
        result["type"] = "disengage"
        result["action_cost"] = "action"
        return result

    # Match against known PC abilities (spells, class features, ember abilities)
    # Check BEFORE generic attack/end-turn so "chorus of one and end turn" matches ability
    for ab in pc_abilities:
        ab_name_lower = ab.get("name", "").lower()
        if ab_name_lower and (ab_name_lower in t or
                              all(w in t for w in ab_name_lower.split() if len(w) > 3)):
            result["type"] = "ability"
            result["ability"] = ab
            result["action_cost"] = ab.get("action_type", "action")
            return result

    # Generic attack keywords
    if any(kw in t for kw in ["attack", "kick", "hit", "strike", "punch",
                               "slash", "stab", "shoot", "tai chi", "melee"]):
        result["type"] = "attack"
        result["action_cost"] = "action"
        return result

    # Cast (generic)
    if any(kw in t for kw in ["cast", "spell"]):
        result["type"] = "cast"
        result["action_cost"] = "action"
        return result

    # End turn / pass — checked LAST so compound actions match first
    if any(kw in t for kw in ["end turn", "pass", "done", "skip"]):
        result["type"] = "end_turn"
        return result

    return result


def _process_pc_combat_turn(combat: Combat, pc_name: str, action_info: dict) -> dict:
    """Execute the PC's declared action through the Combat engine.
    Returns a dict of results for the DM to narrate."""
    pc = combat.get(pc_name)
    results = {"pc": pc_name, "actions_taken": [], "errors": [], "log_before": len(combat.log)}

    atype = action_info["type"]

    if atype == "end_turn":
        results["actions_taken"].append({"type": "end_turn", "detail": "Player ended turn"})
        return results

    if atype == "disengage":
        ok, msg = pc.use_action("Disengage")
        if ok:
            results["actions_taken"].append({"type": "disengage", "detail": "Disengage — no opportunity attacks this turn"})
        else:
            results["errors"].append(f"Cannot Disengage: {msg}")
        return results

    if atype == "attack":
        target = _find_target(combat, action_info["raw"], "enemy", pc_name)
        if not target:
            results["errors"].append("No valid target found for attack")
            return results

        ok, msg = pc.use_action(f"Attack {target}")
        if not ok:
            results["errors"].append(f"Cannot Attack: {msg}")
            return results

        atk_result = combat.attack(pc_name, target)
        action_record = {
            "type": "attack", "target": target,
            "roll": atk_result["nat"], "total": atk_result["total"],
            "target_ac": atk_result["tgt_ac"],
            "hit": atk_result["hits"], "crit": atk_result["crit"],
            "nat1": atk_result["nat1"],
        }

        if atk_result["hits"]:
            # Default melee: 1d6 + STR or DEX mod
            atk_stat = max(pc.stats.get("str", 0), pc.stats.get("dex", 0))
            dmg_val, dmg_info = combat.damage(target, "1d6", "bludgeoning",
                                               mod=atk_stat, crit=atk_result["crit"])
            combat.deal_damage(target, dmg_val)
            action_record["damage"] = dmg_val
            action_record["damage_type"] = "bludgeoning"
            tgt_f = combat.get(target)
            action_record["target_hp"] = f"{tgt_f.hp}/{tgt_f.max_hp}"
            action_record["target_alive"] = tgt_f.alive
            # Tai Chi: always prone on hit
            if "tai chi" in action_info["raw"].lower() or "kick" in action_info["raw"].lower():
                combat.add_status(target, "prone", duration=1)
                action_record["applied_status"] = "prone"
        else:
            action_record["damage"] = 0

        results["actions_taken"].append(action_record)
        return results

    if atype == "ability":
        ab = action_info["ability"]
        ab_name = ab.get("name", "?")
        cost = action_info["action_cost"]

        # Validate action economy
        if cost == "bonus_action":
            ok, msg = pc.use_bonus_action(ab_name)
        elif cost == "reaction":
            ok, msg = pc.use_reaction(ab_name) if hasattr(pc, 'use_reaction') else (False, "No reaction method")
        elif cost == "passive":
            ok, msg = True, "Passive — always active"
        else:
            ok, msg = pc.use_action(ab_name)

        if not ok:
            results["errors"].append(f"Cannot use {ab_name}: {msg}")
            return results

        action_record = {"type": "ability", "name": ab_name, "cost": cost}

        # Spell slot check
        slot_lvl = ab.get("slot_level", 0)
        if slot_lvl and pc.spell_slots:
            slot_key = slot_lvl
            if slot_key in pc.spell_slots:
                cur, mx = pc.spell_slots[slot_key]
                if cur <= 0:
                    results["errors"].append(f"No L{slot_lvl} spell slots remaining (0/{mx})")
                    # Undo action spend
                    if cost == "bonus_action":
                        pc.bonus_action_used = False
                    else:
                        pc.action_used = False
                    return results
                pc.spell_slots[slot_key] = [cur - 1, mx]
                action_record["slot_spent"] = f"L{slot_lvl}: {cur-1}/{mx}"

        # Charge check for ember abilities
        for a in pc.abilities.values():
            if a.name == ab_name and a.max_charges > 0:
                if a.charges <= 0:
                    results["errors"].append(f"{ab_name}: no charges remaining (0/{a.max_charges})")
                    if cost == "bonus_action":
                        pc.bonus_action_used = False
                    else:
                        pc.action_used = False
                    return results
                a.charges -= 1
                action_record["charges_remaining"] = f"{a.charges}/{a.max_charges}"

        # If ability targets an enemy (damage/debuff), find target and apply
        ab_desc = ab.get("description", "").lower()
        if any(kw in ab_desc for kw in ["damage", "attack", "save dc", "disadvantage",
                                          "frightened", "stunned"]):
            target = _find_target(combat, action_info["raw"], "enemy", pc_name)
            if target:
                action_record["target"] = target

        # If ability is a heal, note that
        if any(kw in ab_desc for kw in ["heal", "hp", "temp hp", "regenerat"]):
            target = _find_target(combat, action_info["raw"], "ally", pc_name)
            action_record["heal_target"] = target or pc_name

        # Concentration check
        if "concentration" in ab.get("description", "").lower():
            if pc.concentrating_on:
                action_record["broke_concentration"] = pc.concentrating_on
            pc.concentrating_on = ab_name
            action_record["concentrating"] = ab_name

        results["actions_taken"].append(action_record)
        return results

    # Unknown action — let DM interpret
    results["errors"].append(f"Could not parse combat action: '{action_info['raw']}'. "
                              "DM should interpret and use Combat API manually.")
    return results


def _process_npc_turns(combat: Combat, pc_name: str) -> list:
    """Process NPC turns between current position and the PC's turn.
    Returns list of turn summaries for DM to narrate."""
    npc_turns = []
    safety = 0
    while safety < len(combat.order) * 2:
        safety += 1
        if combat.turn_idx >= 0:
            current = combat.order[combat.turn_idx][1]
            if current == pc_name:
                break

        rnd, name = combat.next_turn()
        if name == pc_name:
            break

        fighter = combat.get(name)
        turn_summary = {"name": name, "round": rnd, "actions": []}

        if not fighter.alive:
            continue

        # NPC AI: simple attack logic for monsters
        if fighter.disposition in ("hostile", ""):
            # Find closest alive PC/ally to attack
            targets = [n for n, f in combat.fighters.items()
                       if f.alive and f.disposition == "friendly"]
            if not targets:
                targets = [n for n, f in combat.fighters.items()
                           if f.alive and n != name]
            if targets:
                import random
                tgt = random.choice(targets)
                ok, _ = fighter.use_action(f"Attack {tgt}")
                if ok:
                    atk_result = combat.attack(name, tgt)
                    action_record = {
                        "type": "attack", "target": tgt,
                        "roll": atk_result["nat"], "total": atk_result["total"],
                        "hit": atk_result["hits"], "crit": atk_result["crit"],
                    }
                    if atk_result["hits"]:
                        # Use first offensive ability's damage dice, or default
                        dmg_dice = "1d6"
                        dmg_mod = max(fighter.stats.get("str", 0), fighter.stats.get("dex", 0))
                        dmg_type = "piercing"
                        for ab in fighter.abilities.values():
                            if hasattr(ab, 'damage') and ab.damage:
                                dmg_dice = ab.damage
                                break
                            elif hasattr(ab, 'extra') and isinstance(ab.extra, dict):
                                if "damage" in ab.extra:
                                    dmg_dice = ab.extra["damage"]
                                    break

                        dmg_val, _ = combat.damage(tgt, dmg_dice, dmg_type,
                                                    mod=dmg_mod, crit=atk_result["crit"])
                        combat.deal_damage(tgt, dmg_val, dmg_type)
                        action_record["damage"] = dmg_val
                        action_record["damage_type"] = dmg_type
                        tgt_f = combat.get(tgt)
                        action_record["target_hp"] = f"{tgt_f.hp}/{tgt_f.max_hp}"
                        action_record["target_alive"] = tgt_f.alive

                        # Phase Spider: poison save on bite
                        if "spider" in name.lower() and atk_result["hits"]:
                            tgt_f = combat.get(tgt)
                            con_mod = tgt_f.stats.get("con", 0)
                            save_roll = d20() + con_mod
                            action_record["poison_save"] = save_roll
                            action_record["poison_dc"] = 11
                            if save_roll < 11:
                                poison_dmg, _ = combat.damage(tgt, "4d8", "poison")
                                if save_roll < 6:  # Fail by 5+
                                    combat.deal_damage(tgt, poison_dmg, "poison")
                                    combat.add_status(tgt, "poisoned", duration=600)
                                    combat.add_status(tgt, "paralyzed", duration=600,
                                                       compound_clears="poisoned")
                                    action_record["poison_full"] = poison_dmg
                                    action_record["poisoned_paralyzed"] = True
                                else:
                                    half_poison = poison_dmg // 2
                                    combat.deal_damage(tgt, half_poison, "poison")
                                    action_record["poison_half"] = half_poison
                                tgt_f = combat.get(tgt)
                                action_record["target_hp"] = f"{tgt_f.hp}/{tgt_f.max_hp}"
                                action_record["target_alive"] = tgt_f.alive
                            else:
                                action_record["poison_saved"] = True
                    else:
                        action_record["damage"] = 0

                    turn_summary["actions"].append(action_record)

        elif fighter.disposition == "friendly" and name != pc_name:
            # Allies attack a random alive enemy
            enemies = [n for n, f in combat.fighters.items()
                       if f.alive and f.disposition in ("hostile", "") and n != name]
            if enemies:
                import random
                tgt = random.choice(enemies)
                ok, _ = fighter.use_action(f"Attack {tgt}")
                if ok:
                    atk_result = combat.attack(name, tgt)
                    action_record = {
                        "type": "attack", "target": tgt,
                        "roll": atk_result["nat"], "total": atk_result["total"],
                        "hit": atk_result["hits"], "crit": atk_result["crit"],
                    }
                    if atk_result["hits"]:
                        atk_stat = max(fighter.stats.get("str", 0), fighter.stats.get("dex", 0))
                        dmg_val, _ = combat.damage(tgt, "1d8", "slashing",
                                                    mod=atk_stat, crit=atk_result["crit"])
                        combat.deal_damage(tgt, dmg_val)
                        action_record["damage"] = dmg_val
                        tgt_f = combat.get(tgt)
                        action_record["target_hp"] = f"{tgt_f.hp}/{tgt_f.max_hp}"
                        action_record["target_alive"] = tgt_f.alive
                    else:
                        action_record["damage"] = 0
                    turn_summary["actions"].append(action_record)

        if turn_summary["actions"]:
            npc_turns.append(turn_summary)

    return npc_turns


def _check_combat_end(combat: Combat, pc_name: str) -> str:
    """Check if combat should end. Returns reason string or ''."""
    enemies_alive = [n for n, f in combat.fighters.items()
                     if f.alive and f.disposition in ("hostile", "")]
    if not enemies_alive:
        return "ALL_ENEMIES_DEAD"
    pc = combat.fighters.get(pc_name)
    if pc and not pc.alive:
        # Biologically dead — fatality OR 2-round window expired without healing.
        return "PC_DOWN"
    if pc and getattr(pc, "dying", False):
        # In the 2-round healing window — DM/party should attempt heal.
        return "PC_DYING"
    allies = [n for n, f in combat.fighters.items()
              if f.alive and (f.disposition == "friendly" or n == pc_name)]
    if not allies:
        return "PARTY_WIPED"
    return ""


def _print_combat_action_results(results: dict):
    """Print the results of PC combat action processing."""
    pc = results["pc"]
    if results["errors"]:
        for e in results["errors"]:
            print(f"  !! COMBAT ERROR: {e}")

    for act in results["actions_taken"]:
        atype = act["type"]
        if atype == "end_turn":
            print(f"  {pc} ends turn.")
        elif atype == "disengage":
            print(f"  {pc} Disengages — safe from opportunity attacks.")
        elif atype == "attack":
            hit_str = "CRIT!" if act.get("crit") else ("HIT" if act["hit"] else "MISS")
            nat1_str = " (NAT 1!)" if act.get("nat1") else ""
            print(f"  {pc} attacks {act['target']}: "
                  f"d20({act['roll']})+{act['total']-act['roll']}={act['total']} "
                  f"vs AC {act['target_ac']} → {hit_str}{nat1_str}")
            if act["hit"]:
                print(f"    Damage: {act['damage']} {act.get('damage_type', 'bludgeoning')}"
                      f" → {act['target']} HP {act['target_hp']}")
                if act.get("applied_status"):
                    print(f"    Applied: {act['applied_status']}")
                if not act.get("target_alive"):
                    print(f"    >>> {act['target']} is DOWN! <<<")
        elif atype == "ability":
            print(f"  {pc} uses {act['name']} ({act['cost']})")
            if act.get("slot_spent"):
                print(f"    Spell slot spent: {act['slot_spent']}")
            if act.get("charges_remaining"):
                print(f"    Charges: {act['charges_remaining']}")
            if act.get("target"):
                print(f"    Target: {act['target']}")
            if act.get("heal_target"):
                print(f"    Heal target: {act['heal_target']}")
            if act.get("concentrating"):
                print(f"    Now concentrating on: {act['concentrating']}")
            if act.get("broke_concentration"):
                print(f"    !! Broke concentration on: {act['broke_concentration']}")


def _print_npc_turn_results(npc_turns: list):
    """Print NPC turn results for DM to narrate."""
    if not npc_turns:
        return
    print(f"\n  {'─' * 50}")
    print(f"  NPC TURNS (engine-resolved — DM narrate these):")
    print(f"  {'─' * 50}")
    for turn in npc_turns:
        name = turn["name"]
        for act in turn["actions"]:
            if act["type"] == "attack":
                hit_str = "CRIT!" if act.get("crit") else ("HIT" if act["hit"] else "MISS")
                print(f"  {name} → {act['target']}: "
                      f"d20({act['roll']})+{act['total']-act['roll']}={act['total']} "
                      f"→ {hit_str}")
                if act["hit"]:
                    print(f"    Damage: {act['damage']} {act.get('damage_type', '')} "
                          f"→ {act['target']} HP {act.get('target_hp', '?')}")
                    if act.get("poison_save") is not None:
                        dc = act.get("poison_dc", 11)
                        sv = act["poison_save"]
                        if act.get("poison_saved"):
                            print(f"    Poison: CON save {sv} vs DC {dc} → SAVED (no poison)")
                        elif act.get("poisoned_paralyzed"):
                            print(f"    Poison: CON save {sv} vs DC {dc} → FAIL BY 5+! "
                                  f"{act.get('poison_full', 0)} poison dmg → POISONED + PARALYZED")
                        elif act.get("poison_half") is not None:
                            print(f"    Poison: CON save {sv} vs DC {dc} → FAIL "
                                  f"→ {act['poison_half']} poison dmg (half)")
                        print(f"    → {act['target']} HP {act.get('target_hp', '?')}")
                    if not act.get("target_alive", True):
                        print(f"    >>> {act['target']} is DOWN! <<<")


def _init_combat(pc_data: dict, ally_data: list, monsters: list) -> Combat:
    combat = Combat()

    pc = load_combatant(pc_data)
    init_roll = d20() + pc.initiative_mod
    combat.add(pc, init_roll)

    for ad in ally_data:
        ally = load_combatant(ad)
        init_roll = d20() + ally.initiative_mod
        combat.add(ally, init_roll)

    for m in monsters:
        count = m.pop("_count", 1)
        base_name = m["name"]
        for i in range(count):
            md = dict(m)
            if count > 1:
                md["name"] = f"{base_name} {i + 1}"
            md.setdefault("disposition", "hostile")
            monster = load_combatant(md)
            monster.hp = monster.max_hp
            monster.disposition = "hostile"
            init_roll = d20() + monster.initiative_mod
            combat.add(monster, init_roll)

    combat.start()
    return combat


# ---------------------------------------------------------------------------
# State loader
# ---------------------------------------------------------------------------

def load_state_safe(state_file: Path):
    raw = state_file.read_text(encoding="utf-8")
    try:
        full_data = json.loads(raw)
        if "_story_engine_state" in full_data:
            eng = StoryEngine(data=full_data["_story_engine_state"])
            return eng, full_data, "full_parse"
        else:
            eng = StoryEngine(data=full_data)
            return eng, full_data, "flat_parse"
    except json.JSONDecodeError:
        pass
    se_data = _extract_story_engine_state(raw)
    if se_data is None:
        raise ValueError(f"Cannot parse state from {state_file}")
    eng = StoryEngine(data=se_data)
    partial = _extract_top_level_fields(raw)
    partial["_story_engine_state"] = se_data
    extra = _extract_full_sections(raw)
    partial.update(extra)
    return eng, partial, "truncation_fallback"


# ---------------------------------------------------------------------------
# Fallback brief builder
# ---------------------------------------------------------------------------

def _build_fallback_brief(eng) -> str:
    hr = int(eng.hour) if isinstance(eng.hour, (int, float)) else eng.hour
    lines = [
        f"# {eng.char_name} — live state (gamemode fallback brief)",
        "",
        "## Time and place",
        f"- **Day {eng.day},** hour {hr:02d}:00" if isinstance(hr, int) else f"- **Day {eng.day},** hour {hr}",
        f"- **Location:** {eng.location}",
        f"- **Weather:** {eng.weather}",
        "",
        "## PC — mechanical facts",
        f"- **{eng.char_name},** level {eng.level} — {getattr(eng, 'exp', 0):,} EXP",
        f"- **HP** {eng.hp}/{eng.max_hp}, **AC** {getattr(eng, 'ac', '?')}",
        f"- **Wealth:** {eng.gold} GP, {eng.silver} SP, {getattr(eng, 'copper', 0)} CP | **meals** {eng.meals}",
    ]
    if eng.spell_slots:
        sp = " ".join(f"L{k}:{v[0]}/{v[1]}" for k, v in sorted(eng.spell_slots.items()))
        lines.append(f"- **Spell slots:** {sp}")
    if eng.class_features:
        cf = ", ".join(f.get("name", str(f)) if isinstance(f, dict) else str(f)
                       for f in eng.class_features)
        lines.append(f"- **Class features:** {cf}")
    if eng.known_spells:
        sp_names = ", ".join(s.get("name", str(s)) if isinstance(s, dict) else str(s)
                             for s in eng.known_spells)
        lines.append(f"- **Spells known:** {sp_names}")
    if eng.quests:
        lines.append("")
        lines.append("## Objectives")
        for q in eng.quests:
            if isinstance(q, dict):
                lines.append(f"- [{q.get('priority','?')}] {q.get('name','?')} ({q.get('status','?')})")
    if eng.events:
        lines.append("")
        lines.append("## Scheduled events")
        for ev in eng.events:
            if isinstance(ev, dict):
                lines.append(f"- Day {ev.get('day','?')}: {ev.get('name','?')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# City Location Registry parser
# ---------------------------------------------------------------------------

def load_city_registry(location: str) -> dict:
    ttrpg_root = _find_ttrpg_root(SCRIPT_DIR)
    if not ttrpg_root:
        for candidate in [SCRIPT_DIR.parent.parent, SCRIPT_DIR.parent]:
            swc = candidate / "shared_world_continuity.md"
            if swc.exists():
                ttrpg_root = candidate
                break
    if not ttrpg_root:
        return {"error": "Cannot find TTRPG root"}
    swc = ttrpg_root / "shared_world_continuity.md"
    if not swc.exists():
        return {"error": f"shared_world_continuity.md not found in {ttrpg_root}"}
    text = swc.read_text(encoding="utf-8")
    registry_start = text.find("## City Location Registry")
    if registry_start == -1:
        return {"error": "No City Location Registry section found"}
    registry_text = text[registry_start:]
    city_pattern = re.compile(r'^### (.+?)(?:\n|$)', re.MULTILINE)
    cities = {}
    for m in city_pattern.finditer(registry_text):
        city_header = m.group(1).strip()
        city_name = city_header.split("(")[0].strip()
        start = m.end()
        next_city = city_pattern.search(registry_text, start)
        end = next_city.start() if next_city else len(registry_text)
        section = registry_text[start:end]
        locations = []
        for line in section.split("\n"):
            line = line.strip()
            if line.startswith("| **"):
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) >= 6:
                    loc_name = cells[0].replace("**", "").strip()
                    locations.append({
                        "name": loc_name, "type": cells[1].strip(),
                        "origin": cells[2].strip(), "owner": cells[3].strip(),
                        "status_25yr": cells[4].strip(),
                        "lore": cells[5].strip() if len(cells) > 5 else "",
                    })
        if locations:
            cities[city_name] = locations

    loc_lower = location.lower()
    def _strip_articles(s):
        for art in ("the ", "a ", "an "):
            if s.startswith(art):
                s = s[len(art):]
        return s

    matched_city = None
    for city_name in cities:
        if city_name.lower() in loc_lower or loc_lower in city_name.lower():
            matched_city = city_name
            break
    if not matched_city:
        loc_stripped = _strip_articles(loc_lower)
        for city_name, locs in cities.items():
            for loc in locs:
                nl = loc["name"].lower()
                ns = _strip_articles(nl)
                if nl in loc_lower or ns in loc_stripped or loc_lower in nl or loc_stripped in ns:
                    matched_city = city_name
                    break
            if matched_city:
                break
    if not matched_city:
        for city_name, locs in cities.items():
            for loc in locs:
                lore = loc.get("lore", "").lower()
                if loc_lower.split(",")[0].strip() in lore or loc_lower.split("—")[0].strip() in lore:
                    matched_city = city_name
                    break
            if matched_city:
                break
    if not matched_city:
        for city_name in cities:
            if city_name.lower() in loc_lower:
                matched_city = city_name
                break

    if matched_city:
        return {"city": matched_city, "locations": cities[matched_city],
                "location_count": len(cities[matched_city])}
    if not cities:
        return {"city": None, "locations": [],
                "note": f"City registry truncated. Location: '{location}'"}
    return {"city": None, "locations": [],
            "note": f"No city match for '{location}'."}


# ---------------------------------------------------------------------------
# Periodic-check sampler
# ---------------------------------------------------------------------------
# Most boot steps are AUDITS — they detect drift/breakage that only happens at
# chapter close, location change, etc. Running them every turn is wasted work
# and noisy output. This sampler runs each audit on a configured period and
# force-runs whenever the relevant inputs (chapter, location) change.
#
# Always-run: LOAD STATE [1], STATE SUMMARY [2], DEADLINES [7]. Time-sensitive.
# Sampled:    TRACKER DRIFT [3], CONTINUITY [4], CITY REGISTRY [5], NARRATOR [6].

GAMEMODE_CHECK_PERIODS = {
    "tracker_drift": 3,    # tracker only drifts at chapter close
    "continuity":    3,    # campaign data is stable mid-scene
    "city_registry": 3,    # location-keyed; force-runs on location change
    "narrator_style": 10,  # narrator style is set once per character
}


def _gamemode_meta_path(character: str) -> Path:
    """Per-character call-counter / cache file (gitignored, local-only)."""
    safe = "".join(c for c in character.lower() if c.isalnum() or c in "_-") or "default"
    return SCRIPT_DIR / f"_gamemode_meta_{safe}.json"


def _load_gamemode_meta(character: str) -> dict:
    p = _gamemode_meta_path(character)
    default = {"calls": 0, "last_chapter": None, "last_location": None,
               "last_check_run": {}}
    if not p.exists():
        return default
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # Backfill any missing keys.
        for k, v in default.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return default


def _save_gamemode_meta(character: str, meta: dict) -> None:
    try:
        _gamemode_meta_path(character).write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except Exception:
        # Best-effort; never break gamemode() because the meta cache failed.
        pass


def _should_run_check(check_name: str, meta: dict, *,
                     audit: bool = False,
                     force_on_change: dict = None) -> tuple:
    """Decide whether a sampled check should run this call.

    Returns (should_run: bool, reason: str). The reason is suitable for printing.
    Force conditions (always run):
      - audit=True (CLI --audit / passed in by caller)
      - first-ever run for this check
      - any force_on_change key whose value differs from meta[f"last_{key}"]

    Otherwise sample on the configured period in GAMEMODE_CHECK_PERIODS.
    """
    if audit:
        return True, "audit mode (forced)"

    last_run_map = meta.get("last_check_run", {})
    if check_name not in last_run_map:
        return True, "first run"

    period = GAMEMODE_CHECK_PERIODS.get(check_name, 1)
    calls_since = max(0, meta.get("calls", 0) - last_run_map[check_name])

    # Force-on-change escape valve.
    if force_on_change:
        for key, current_value in force_on_change.items():
            prev = meta.get(f"last_{key}")
            if prev is not None and prev != current_value:
                return True, f"{key} changed ({prev} → {current_value})"

    if calls_since >= period:
        return True, f"period elapsed ({calls_since}/{period})"

    next_in = period - calls_since
    return False, f"skipped (next in {next_in} call{'s' if next_in != 1 else ''})"


def _record_check_run(meta: dict, check_name: str) -> None:
    meta.setdefault("last_check_run", {})[check_name] = meta.get("calls", 0)


# ---------------------------------------------------------------------------
# Tracker drift checker
# ---------------------------------------------------------------------------
# WHY THIS EXISTS:
#   character_tracker.md is treated as the source of truth by sync_tracker_to_json().
#   sync direction is markdown -> JSON, so a stale tracker can silently CLOBBER a
#   current JSON. Gameplay updates JSON; the tracker has to be hand-updated at
#   chapter close. If we don't catch drift at session start, we may get to a
#   sync call that rolls everything back. This function compares the tracker
#   header (Active PC level / Current In-Game Date Day / Chapter / EXP) against
#   the engine's loaded state and reports any mismatch.

def check_tracker_drift(eng, full_data: dict, tracker_path: Path = None) -> dict:
    """Compare character_tracker.md header against JSON state.

    Returns a dict:
        {
          "checked": bool,
          "tracker_path": str,
          "tracker": {"level": int|None, "day": int|None, "chapter": int|None, "exp": int|None},
          "json":    {"level": int,      "day": int,      "chapter": int,      "exp": int},
          "drift":   [str, ...],   # human-readable mismatch lines
          "warnings": [str, ...],  # non-fatal issues (file missing, parse failures)
        }
    """
    if tracker_path is None:
        tracker_path = SCRIPT_DIR / "character_tracker.md"

    json_level   = getattr(eng, "level", 0)
    json_day     = getattr(eng, "day", 0)
    json_chapter = (full_data or {}).get("_chapter", 0) or 0
    json_exp     = getattr(eng, "exp", 0) or 0

    result = {
        "checked": False,
        "tracker_path": str(tracker_path),
        "tracker": {"level": None, "day": None, "chapter": None, "exp": None},
        "json":    {"level": json_level, "day": json_day,
                    "chapter": json_chapter, "exp": json_exp},
        "drift":   [],
        "warnings": [],
    }

    if not tracker_path.exists():
        result["warnings"].append(f"Tracker file not found: {tracker_path}")
        return result

    try:
        text = tracker_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        result["warnings"].append(f"Tracker read failed: {e}")
        return result

    # Only inspect the first ~50 lines (the header block). Don't be confused by
    # the words "Day" / "Chapter" / "Level" appearing later in chapter logs etc.
    head = "\n".join(text.splitlines()[:50])

    def _grab(pattern):
        m = re.search(pattern, head)
        return m.group(1).strip() if m else None

    # Parse header fields. Patterns are anchored to the header label ("Active PC",
    # "Current In-Game Date", "**Chapter:**", "**EXP:**") so chapter logs don't fool us.
    raw_level   = _grab(r"Active PC:[^\n]*?\(Level\s+(\d+)\)")
    raw_day     = _grab(r"Current In-Game Date:[^\n]*?\bDay\s+(\d+)")
    raw_chapter = _grab(r"\*\*Chapter:\*\*\s*(\d+)")
    raw_exp     = _grab(r"\*\*EXP:\*\*\s*([\d,]+)")

    try:
        result["tracker"]["level"]   = int(raw_level)   if raw_level   is not None else None
        result["tracker"]["day"]     = int(raw_day)     if raw_day     is not None else None
        result["tracker"]["chapter"] = int(raw_chapter) if raw_chapter is not None else None
        result["tracker"]["exp"]     = int(raw_exp.replace(",", "")) if raw_exp is not None else None
    except ValueError as e:
        result["warnings"].append(f"Tracker header parse: {e}")

    t = result["tracker"]

    if t["level"] is not None and t["level"] != json_level:
        result["drift"].append(
            f"LEVEL: tracker={t['level']}, json={json_level}"
        )
    if t["day"] is not None and t["day"] != json_day:
        gap = abs(t["day"] - json_day)
        result["drift"].append(
            f"DAY: tracker={t['day']}, json={json_day} (gap {gap} day{'s' if gap != 1 else ''})"
        )
    if t["chapter"] is not None and t["chapter"] != json_chapter:
        result["drift"].append(
            f"CHAPTER: tracker={t['chapter']}, json={json_chapter}"
        )
    if t["exp"] is not None and abs(t["exp"] - json_exp) > 1000:
        # Allow up to 1k EXP slack for in-scene unsaved drift; anything bigger is real drift.
        result["drift"].append(
            f"EXP: tracker={t['exp']:,}, json={json_exp:,} (delta {abs(t['exp']-json_exp):,})"
        )

    if t["level"] is None and t["day"] is None and t["chapter"] is None and t["exp"] is None:
        result["warnings"].append(
            "Could not parse any header fields from character_tracker.md — "
            "header format may have changed (expected: 'Active PC: ... (Level N)', "
            "'Current In-Game Date: ... Day N', '**Chapter:** N', '**EXP:** N,NNN')."
        )

    result["checked"] = True
    return result


# ---------------------------------------------------------------------------
# Deadline checker
# ---------------------------------------------------------------------------

def check_deadlines(eng, full_data: dict = None) -> list:
    alerts = []
    d = eng.day
    for ev in eng.events:
        # Skip events already marked DONE / COMPLETE / RESOLVED
        ev_status = str(ev.get("status", "")).upper()
        if ev_status in ("DONE", "COMPLETE", "RESOLVED", "CANCELLED", "SKIPPED"):
            continue
        ed = ev.get("day", 999); en = ev.get("name", "unnamed")
        if ed < d:   alerts.append({"name": en, "day": ed, "status": "OVERDUE"})
        elif ed == d: alerts.append({"name": en, "day": ed, "status": "DUE_TODAY"})
        elif ed == d+1: alerts.append({"name": en, "day": ed, "status": "TOMORROW"})
    for q in eng.quests:
        if q.get("status","").lower() in ("complete","done","resolved","failed"):
            continue
        qn = q.get("name","unnamed"); qd = q.get("due_day", q.get("deadline"))
        if qd is not None and isinstance(qd, (int, float)):
            if qd < d:   alerts.append({"name": qn, "day": int(qd), "status": "OVERDUE", "type": "quest"})
            elif qd == d: alerts.append({"name": qn, "day": int(qd), "status": "DUE_TODAY", "type": "quest"})
    seen = set(); unique = []
    for a in alerts:
        if a["name"] not in seen:
            seen.add(a["name"]); unique.append(a)
    return unique


# ---------------------------------------------------------------------------
# Character-goal alert scanner
# ---------------------------------------------------------------------------
# Scans _story_engine_state.character_goals[] (PC + NPC goals) and emits the
# alert tiers from DM_TURN_PROTOCOL § "Goal alert scan" (step 0 of every DM
# response). check_deadlines() handles calendar events / dated quests; this
# handles the broader Active Goals table where NPC behavior is keyed.
#
# Tier semantics:
#   FIRES_NOW    — due today AND due_time has arrived (or is within ~1 hr)
#   IMMINENT     — due today AND due_time within 4 hours
#   DUE_TODAY    — due today (no time, or time still hours out)
#   DUE_TOMORROW — due tomorrow
#   OVERDUE      — due_day already passed, status still active

def check_character_goals(eng, full_data: dict = None) -> list:
    """Return active goal alerts from _story_engine_state.character_goals.

    Each alert: {goal_id, character, due_day, due_time, status, summary, type='goal'}.
    Skips goals with no due_day, status != active, or due_day > current_day + 1.
    """
    alerts = []
    if not full_data:
        return alerts

    se = full_data.get("_story_engine_state", {}) or {}
    goals = se.get("character_goals", []) or []
    if not isinstance(goals, list):
        return alerts

    current_day  = getattr(eng, "day", 0) or 0
    current_hour = getattr(eng, "hour", 0)
    if not isinstance(current_hour, (int, float)):
        current_hour = 0

    for g in goals:
        if not isinstance(g, dict):
            continue
        if str(g.get("status", "")).lower() not in ("active", "in_progress", "in progress"):
            continue
        due_day_raw = g.get("due_day")
        if due_day_raw is None:
            continue  # ongoing / no deadline
        try:
            due_day = int(due_day_raw)
        except (TypeError, ValueError):
            continue

        # Parse due_time "HH:MM" → due_hour. Skip strings like "ongoing", "" etc.
        due_hour = None
        dt = g.get("due_time", "")
        if isinstance(dt, str) and ":" in dt:
            try:
                due_hour = int(dt.split(":")[0])
            except (ValueError, IndexError):
                pass

        gap = due_day - current_day
        if gap < 0:
            status = "OVERDUE"
        elif gap == 0:
            if due_hour is None:
                status = "DUE_TODAY"
            elif due_hour <= current_hour + 1:
                status = "FIRES_NOW"
            elif due_hour <= current_hour + 4:
                status = "IMMINENT"
            else:
                status = "DUE_TODAY"
        elif gap == 1:
            status = "DUE_TOMORROW"
        else:
            continue  # too far out — don't alert

        alerts.append({
            "goal_id":   g.get("goal_id") or g.get("name", "unnamed"),
            "character": g.get("character", "?"),
            "due_day":   due_day,
            "due_time":  dt or "",
            "status":    status,
            "summary":   (g.get("summary") or "")[:120],
            "type":      "goal",
            # mirror check_deadlines fields so dashboard renders both uniformly:
            "name":      f"{g.get('character', '?')}: {g.get('goal_id') or g.get('name', 'unnamed')}",
            "day":       due_day,
        })

    # Sort by tier severity then by day, so FIRES_NOW prints first.
    tier_order = {"FIRES_NOW": 0, "OVERDUE": 1, "IMMINENT": 2, "DUE_TODAY": 3, "DUE_TOMORROW": 4}
    alerts.sort(key=lambda a: (tier_order.get(a["status"], 9), a["day"]))
    return alerts


# ---------------------------------------------------------------------------
# Narrator style reader
# ---------------------------------------------------------------------------

def read_narrator_style(full_data: dict) -> str:
    pi = full_data.get("player_input", {})
    if not isinstance(pi, dict):
        return "Aleron Kong (irreverent, funny, mechanics-in-prose)"
    style = pi.get("narrator_style", "")
    if isinstance(style, dict):
        author = style.get("author", "")
        voice = style.get("voice", "")
        return f"{author} ({voice[:80]})" if author else voice[:100]
    return style if style else "Aleron Kong (irreverent, funny, mechanics-in-prose)"


# ---------------------------------------------------------------------------
# PC Abilities collector — reads EVERYTHING from the state file
# ---------------------------------------------------------------------------

def _collect_pc_abilities(full_data: dict) -> dict:
    ms = full_data.get("mechanical_state", {})
    ei = full_data.get("ember_inheritance", {})
    pe = full_data.get("persistent_effects", {})

    abilities = {
        "ability_scores": ms.get("ability_scores", {}),
        "saving_throws": ms.get("saving_throws", {}),
        "skills": ms.get("skills", {}),
        "ac_note": ms.get("AC_note", ""),
        "character_flaw": ms.get("character_flaw", ""),
        "halfling_luck": ms.get("halfling_luck", ""),
        "spells": [], "class_features": [],
        "ember_passive": {}, "ember_active": {}, "ember_surge": {},
        "persistent_effects": [],
    }

    for key in ("spells_known", "known_spells"):
        spells = ms.get(key, [])
        if spells:
            abilities["spells"] = spells
            break
    if not abilities["spells"]:
        se = full_data.get("_story_engine_state", {})
        for key in ("spells_known", "known_spells"):
            spells = se.get(key, [])
            if spells:
                abilities["spells"] = spells
                break

    cf = ms.get("class_features", [])
    if not cf:
        se = full_data.get("_story_engine_state", {})
        cf = se.get("class_features", [])
    abilities["class_features"] = cf

    ember_abs = ei.get("abilities", {})
    abilities["ember_passive"] = ember_abs.get("passive", {})
    abilities["ember_active"] = ember_abs.get("active", {})
    abilities["ember_surge"] = ember_abs.get("surge", {})
    abilities["ember_theme"] = ei.get("theme", "")
    abilities["ember_theme_desc"] = ei.get("theme_description", "")
    abilities["persistent_effects"] = pe.get("on_pc", [])
    return abilities


def _print_inventory(full_data: dict, pc_name: str) -> None:
    """Print equipped / key items / satchel / consumables in compact form.

    Reads from _story_engine_state.{equipped, key_items, satchel, consumables}.
    No-op if all four are empty. Slots into the dashboard between the deadlines
    block and PC ABILITIES so the player sees status info before capabilities.
    """
    se = full_data.get("_story_engine_state", {}) or {}
    equipped    = se.get("equipped", [])    or []
    key_items   = se.get("key_items", [])   or []
    satchel     = se.get("satchel", [])     or []
    consumables = se.get("consumables", {}) or {}

    if isinstance(consumables, dict):
        cons_items = list(consumables.items())
    elif isinstance(consumables, list):
        cons_items = [(str(x), "") for x in consumables]
    else:
        cons_items = []

    if not (equipped or key_items or satchel or cons_items):
        return

    print(f"\n{'─' * 60}")
    print(f"INVENTORY — {pc_name}")
    print(f"{'─' * 60}")
    if equipped:
        print(f"  Equipped:")
        for item in equipped:
            print(f"    • {str(item)[:110]}")
    if key_items:
        print(f"  Key items:")
        for item in key_items:
            print(f"    ⭐ {str(item)[:110]}")
    if satchel:
        print(f"  Satchel:")
        for item in satchel:
            print(f"    · {str(item)[:90]}")
    if cons_items:
        print(f"  Consumables:")
        for k, v in cons_items:
            line = f"{k}: {v}" if v else f"{k}"
            print(f"    ◇ {line[:90]}")


def _print_pc_abilities(abilities: dict, pc_name: str):
    print(f"\n{'=' * 60}")
    print(f"PC ABILITIES — {pc_name.upper()}'S CHARACTER SHEET")
    print(f"{'=' * 60}")

    scores = abilities.get("ability_scores", {})
    if scores:
        score_parts = []
        for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
            s = scores.get(stat, {})
            if isinstance(s, dict):
                final = s.get("final", s.get("base", "?"))
                mod = s.get("mod", "?")
                sign = f"+{mod}" if isinstance(mod, int) and mod >= 0 else str(mod)
                score_parts.append(f"{stat} {final}({sign})")
            else:
                score_parts.append(f"{stat} {s}")
        print(f"  Stats: {' | '.join(score_parts)}")

    saves = abilities.get("saving_throws", {})
    if saves:
        prof = saves.get("proficient", [])
        if prof:
            save_strs = []
            for s in prof:
                sv = saves.get(f"{s}_save", "")
                save_strs.append(f"{s} {sv}" if sv else s)
            print(f"  Saves (proficient): {', '.join(save_strs)}")
        flaw = saves.get("_flaw_note", "")
        if flaw:
            print(f"  !! FLAW: {flaw[:120]}")

    skills = abilities.get("skills", {})
    if skills:
        skill_parts = [f"{k} {v}" for k, v in skills.items() if not k.startswith("_")]
        if skill_parts:
            print(f"  Skills: {' | '.join(skill_parts)}")

    ac_note = abilities.get("ac_note", "")
    if ac_note:
        print(f"  AC: {ac_note[:200]}")
    flaw = abilities.get("character_flaw", "")
    if flaw:
        print(f"  Flaw: {flaw[:200]}")
    hl = abilities.get("halfling_luck", "")
    if hl:
        print(f"  Racial: {hl}")

    cf = abilities.get("class_features", [])
    if cf:
        print(f"\n  --- CLASS FEATURES ---")
        for feat in cf:
            if isinstance(feat, dict):
                name = feat.get("name", "?")
                desc = feat.get("description", "")
                mech = feat.get("mechanical_effect", "")
                mechanics = feat.get("mechanics", {})
                print(f"  [{name}]")
                if desc: print(f"    {desc[:250]}")
                if mech: print(f"    EFFECT: {mech[:250]}")
                if mechanics and isinstance(mechanics, dict):
                    for mk, mv in mechanics.items():
                        print(f"    {mk}: {str(mv)[:250]}")
            else:
                print(f"  [{feat}]")

    spells = abilities.get("spells", [])
    if spells:
        print(f"\n  --- SPELLS KNOWN ---")
        for spell in spells:
            if isinstance(spell, dict):
                name = spell.get("name", "?")
                level = spell.get("level", "?")
                casting = spell.get("casting_time", "")
                rng = spell.get("range", "")
                dur = spell.get("duration", "")
                print(f"  [L{level}] {name}")
                if casting: print(f"    Cast: {casting} | Range: {rng} | Duration: {dur}")
                for fk in ("description", "effect", "effect_during", "effect_on_completion", "failure", "limitation"):
                    fv = spell.get(fk, "")
                    if fv:
                        label = fk.upper().replace("EFFECT_", "").replace("_", " ")
                        print(f"    {label}: {fv[:250]}")
            else:
                print(f"  {spell}")

    ember_theme = abilities.get("ember_theme", "")
    if ember_theme:
        print(f"\n  --- EMBER INHERITANCE (theme: {ember_theme}) ---")
        desc = abilities.get("ember_theme_desc", "")
        if desc: print(f"    {desc[:250]}")

    for key, label in [("ember_passive", "PASSIVE"), ("ember_active", "ACTIVE"), ("ember_surge", "SURGE")]:
        ab = abilities.get(key, {})
        if ab and isinstance(ab, dict) and ab.get("name"):
            print(f"  [{label}] {ab['name']}")
            for fk in ("description", "mechanical_effect"):
                fv = ab.get(fk, "")
                if fv: print(f"    {fk.upper().replace('_',' ')}: {fv[:300]}")
            uses = ab.get("uses_per_day", "")
            if uses: print(f"    USES: {uses}")
            cost = ab.get("exhaustion_cost", "")
            if cost: print(f"    COST: {cost}")

    pe = abilities.get("persistent_effects", [])
    if pe:
        print(f"\n  --- ACTIVE EFFECTS & PERKS ---")
        for eff in pe:
            if isinstance(eff, dict):
                name = eff.get("effect_name", "?")
                mech = eff.get("mechanical_effect", "")
                etype = eff.get("type", "")
                print(f"  [{etype}] {name}")
                if mech: print(f"    EFFECT: {mech[:300]}")
            else:
                print(f"  {eff}")


# ---------------------------------------------------------------------------
# Scene NPC collector
# ---------------------------------------------------------------------------

def _collect_scene_npcs(full_data: dict, character: str, location: str) -> list:
    npcs = []
    for npc in full_data.get("main_cast", []):
        if isinstance(npc, dict):
            npcs.append({
                "name": npc.get("name", "?"), "role": npc.get("role", "?"),
                "alignment": npc.get("alignment", "?"),
                "location": npc.get("location", "?"),
                "want": npc.get("want", ""),
                "voice_hook": npc.get("voice_hook", ""),
                "combat_abilities": npc.get("combat_abilities", []),
                "source": "main_cast",
            })

    extras = full_data.get("extra_npcs", {})
    if isinstance(extras, dict):
        for npc in extras.get("npcs", []):
            if isinstance(npc, dict) and npc.get("status", "active") == "active":
                npcs.append({
                    "name": npc.get("name", "?"), "role": npc.get("job_excuse", ""),
                    "alignment": npc.get("alignment", "?"),
                    "tier": npc.get("tier", "extra"),
                    "relationship": npc.get("relationship", ""),
                    "combat_abilities": npc.get("combat_abilities", []),
                    "source": "extra_npcs",
                })

    ttrpg_root = _find_ttrpg_root(SCRIPT_DIR)
    if ttrpg_root:
        for candidate_dir in ttrpg_root.iterdir():
            if not candidate_dir.is_dir(): continue
            if candidate_dir.name.lower() == character.lower(): continue
            state_candidates = [
                candidate_dir / "Game init files" / "character_world_state.json",
                candidate_dir / "Game init files" / f"{candidate_dir.name.lower()}_state.json",
            ]
            for sf in state_candidates:
                if sf.exists():
                    try:
                        raw = sf.read_text(encoding="utf-8")
                        data = json.loads(raw)
                        se = data.get("_story_engine_state", data)
                        char_name = se.get("char_name", candidate_dir.name)
                        ms = data.get("mechanical_state", {})
                        npcs.append({
                            "name": char_name,
                            "role": f"Cross-campaign PC ({candidate_dir.name})",
                            "level": se.get("level", "?"),
                            "hp": f"{se.get('hp', '?')}/{se.get('max_hp', '?')}",
                            "ac": se.get("ac", "?"),
                            "ability_scores": ms.get("ability_scores", {}),
                            "class_features": ms.get("class_features", []) or se.get("class_features", []),
                            "spells": ms.get("spells_known", []) or se.get("known_spells", []),
                            "ember_abilities": data.get("ember_inheritance", {}).get("abilities", {}),
                            "source": f"cross_campaign:{candidate_dir.name}",
                        })
                    except (json.JSONDecodeError, OSError):
                        pass
                    break
    return npcs


def _print_scene_npcs(npcs: list):
    if not npcs: return
    print(f"\n{'=' * 60}")
    print("SCENE NPCs & ALLIES")
    print(f"{'=' * 60}")
    for npc in npcs:
        name = npc.get("name", "?")
        role = npc.get("role", "")
        source = npc.get("source", "")
        if source.startswith("cross_campaign"):
            print(f"\n  [{name}] Level {npc.get('level','?')} — {role}")
            print(f"    HP {npc.get('hp','?')} | AC {npc.get('ac','?')}")
            scores = npc.get("ability_scores", {})
            if scores:
                parts = []
                for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
                    s = scores.get(stat, {})
                    if isinstance(s, dict):
                        final = s.get("final", s.get("base", "?"))
                        mod = s.get("mod", "?")
                        sign = f"+{mod}" if isinstance(mod, int) and mod >= 0 else str(mod)
                        parts.append(f"{stat} {final}({sign})")
                if parts: print(f"    Stats: {' | '.join(parts)}")
            for feat in npc.get("class_features", []):
                if isinstance(feat, dict):
                    fn = feat.get("name", "?")
                    fm = feat.get("mechanical_effect", "")
                    print(f"    [{fn}]" + (f" — {fm[:150]}" if fm else ""))
        else:
            alignment = npc.get("alignment", "")
            print(f"\n  [{name}] {alignment} — {role}")
            for fk in ("location", "want", "voice_hook", "relationship"):
                fv = npc.get(fk, "")
                if fv: print(f"    {fk.title()}: {fv[:200]}")
            for c in npc.get("combat_abilities", []):
                if isinstance(c, dict):
                    print(f"    Combat: {c.get('name','?')} — {c.get('effect','')[:150]}")


# ---------------------------------------------------------------------------
# Enemy info collector
# ---------------------------------------------------------------------------

def _collect_enemy_info(full_data: dict) -> dict:
    pe = full_data.get("persistent_effects", {})
    ant = full_data.get("antagonist", {})
    return {
        "known_enemy_buffs": pe.get("known_enemy_buffs", []),
        "antagonist_name": ant.get("name", ""),
        "antagonist_alignment": ant.get("alignment", ""),
        "antagonist_want": ant.get("want", ""),
        "antagonist_abilities": ant.get("abilities", []),
        "antagonist_weakness": ant.get("weakness", ""),
    }


def _print_enemy_info(enemy_info: dict):
    buffs = enemy_info.get("known_enemy_buffs", [])
    ant_name = enemy_info.get("antagonist_name", "")
    if not buffs and not ant_name: return

    print(f"\n{'=' * 60}")
    print("KNOWN ENEMY ABILITIES")
    print(f"{'=' * 60}")
    if ant_name:
        print(f"  [ANTAGONIST] {ant_name} ({enemy_info.get('antagonist_alignment','')})")
        want = enemy_info.get("antagonist_want", "")
        if want: print(f"    Want: {want[:250]}")
        weakness = enemy_info.get("antagonist_weakness", "")
        if weakness: print(f"    Weakness: {weakness[:250]}")
        for ab in enemy_info.get("antagonist_abilities", []):
            if isinstance(ab, dict):
                print(f"    Ability: {ab.get('name','?')} — {ab.get('effect','')[:200]}")
    if buffs:
        print(f"\n  --- KNOWN ENEMY BUFFS ---")
        for b in buffs:
            if isinstance(b, dict):
                print(f"  [{b.get('enemy_name','?')}] {b.get('buff_name','?')}")
                print(f"    EFFECT: {b.get('effect','')[:250]}")


# ---------------------------------------------------------------------------
# GAMEMODE — main boot function
# ---------------------------------------------------------------------------

def gamemode(character: str = "kenji", player_action: str = "",
             audit: bool = False) -> dict:
    """Full DM boot sequence + combat engine. Returns structured report dict.

    Parameters
    ----------
    character : str
        Active character (kenji, cookie, ...).
    player_action : str
        Player input text for this turn (drives combat detection / scene routing).
    audit : bool
        If True, force-run every sampled check this turn (TRACKER DRIFT,
        CONTINUITY, CITY REGISTRY, NARRATOR STYLE) regardless of period.
        Use after suspected drift, after restoring from a backup, or as a
        scheduled deep-audit. Default False — sampled checks honor their
        configured period and force-run on chapter/location change.
    """
    state_file = resolve_state_file(character)
    _dm_turn.STATE_FILE = state_file

    # Per-character call counter + last-seen chapter/location for change detection.
    meta = _load_gamemode_meta(character)
    meta["calls"] = meta.get("calls", 0) + 1

    report = {
        "command": "gamemode", "character": character,
        "player_action": player_action, "status": "OK",
        "audit": audit, "call_number": meta["calls"],
        "errors": [], "warnings": [],
    }

    print("=" * 60)
    print(f"GAMEMODE — DM BOOT SEQUENCE  (call #{meta['calls']}{'  AUDIT' if audit else ''})")
    print("=" * 60)
    print(f"Character: {character}")
    print(f"State file: {state_file}")
    if not state_file.exists():
        report["status"] = "FATAL"
        report["errors"].append(f"State file not found: {state_file}")
        print(f"FATAL: State file not found: {state_file}")
        return report

    # == 1. LOAD STATE & WRITE BRIEF ==
    try:
        eng, full_data, load_method = load_state_safe(state_file)
        if load_method == "truncation_fallback":
            report["warnings"].append("State file truncated — used fallback parser")
            print(f"[1/7] LOAD — truncation fallback")
        else:
            print(f"[1/7] LOAD — {load_method}")
        try:
            brief_text = eng.ai_brief_markdown()
            out = SCRIPT_DIR / "AI_CONTEXT.md"
            out.write_text(brief_text, encoding="utf-8")
            report["brief"] = f"OK ({len(brief_text)} chars)"
            print(f"      BRIEF — wrote AI_CONTEXT.md ({len(brief_text)} chars)")
        except Exception as e:
            brief_text = _build_fallback_brief(eng)
            out = SCRIPT_DIR / "AI_CONTEXT.md"
            out.write_text(brief_text, encoding="utf-8")
            report["brief"] = f"FALLBACK ({len(brief_text)} chars)"
            report["warnings"].append(f"Fallback brief ({e})")
            print(f"      BRIEF — fallback ({len(brief_text)} chars)")
    except Exception as e:
        report["errors"].append(f"Load failed: {e}")
        print(f"[1/7] LOAD — FAILED: {e}")
        report["status"] = "DEGRADED"
        return report

    # == 2. STATE SUMMARY ==
    cal = day_to_calendar(eng.day)
    weekday = day_to_weekday(eng.day)
    hr = int(eng.hour) if isinstance(eng.hour, (int, float)) else eng.hour
    time_str = f"{hr:02d}:00" if isinstance(hr, int) else str(hr)
    state_summary = {
        "character": eng.char_name, "level": eng.level,
        "exp": getattr(eng, "exp", 0),
        "exp_to_next": getattr(eng, "exp_to_next_level", 0),
        "day": eng.day, "hour": hr,
        "calendar": f"{weekday}, {cal} 1247 AR",
        "location": eng.location, "weather": eng.weather,
        "hp": eng.hp, "max_hp": eng.max_hp,
        "ac": getattr(eng, "ac", 0),
        "gold": eng.gold, "silver": eng.silver,
        "copper": getattr(eng, "copper", 0),
        "spell_slots": {k: {"current": v[0], "max": v[1]}
                        for k, v in eng.spell_slots.items()} if eng.spell_slots else {},
        "charges": {k: {"current": v[0], "max": v[1]}
                    for k, v in eng.charges.items()} if eng.charges else {},
        "buffs": list(eng.buffs.keys()) if eng.buffs else [],
        "meals": eng.meals, "hours_since_meal": eng.hours_since_meal,
        "chapter": full_data.get("_chapter", 0),
        "chapter_status": full_data.get("_chapter_status", ""),
        "chapter_title": full_data.get("_chapter_title", ""),
    }
    report["state"] = state_summary
    print(f"[2/7] STATE — {eng.char_name} L{eng.level} | Day {eng.day} {time_str} | {eng.location}")

    # == 3. TRACKER DRIFT ==
    # Sampled — runs every Nth call and force-runs on chapter change (since the
    # tracker only goes stale at chapter close anyway).
    chapter_now = full_data.get("_chapter", 0) or 0
    should_run, reason = _should_run_check(
        "tracker_drift", meta, audit=audit,
        force_on_change={"chapter": chapter_now},
    )
    if should_run:
        try:
            drift_report = check_tracker_drift(eng, full_data, SCRIPT_DIR / "character_tracker.md")
            report["tracker_drift"] = drift_report
            if drift_report["drift"]:
                for d in drift_report["drift"]:
                    report["warnings"].append(f"TRACKER DRIFT: {d}")
                print(f"[3/7] TRACKER DRIFT — !!! {len(drift_report['drift'])} field(s) out of sync !!! ({reason})")
                for d in drift_report["drift"]:
                    print(f"      • {d}")
                print(f"      ⚠ Update character_tracker.md before chapter close, or sync_tracker_to_json()")
                print(f"      ⚠ will clobber the live JSON state with the stale tracker values.")
            elif drift_report["warnings"]:
                for w in drift_report["warnings"]:
                    report["warnings"].append(f"TRACKER DRIFT: {w}")
                print(f"[3/7] TRACKER DRIFT — could not verify ({len(drift_report['warnings'])} warning(s); {reason})")
                for w in drift_report["warnings"]:
                    print(f"      • {w}")
            else:
                print(f"[3/7] TRACKER DRIFT — clean ({reason})")
            _record_check_run(meta, "tracker_drift")
        except Exception as e:
            report["warnings"].append(f"Tracker drift check failed: {e}")
            print(f"[3/7] TRACKER DRIFT — FAILED: {e}")
    else:
        report["tracker_drift"] = {"checked": False, "reason": reason}
        print(f"[3/7] TRACKER DRIFT — {reason}")

    # == 4. CONTINUITY ENGINE ==
    # Sampled — runs every Nth call and force-runs on chapter change.
    should_run, reason = _should_run_check(
        "continuity", meta, audit=audit,
        force_on_change={"chapter": chapter_now},
    )
    if should_run:
        try:
            import continuity_engine as ce
            if load_method == "truncation_fallback" and full_data:
                load_msg = f"Loaded {character} via truncation fallback"
                ce._LOADED_CHARACTER = character.lower()
            else:
                load_msg = ce.load_campaign(character.lower())
            report["continuity_load"] = load_msg
            ce_state = {
                "hour": eng.hour, "day": eng.day, "location": eng.location,
                "hp": eng.hp, "max_hp": eng.max_hp, "exp": getattr(eng, "exp", 0),
                "meals": eng.meals, "hours_since_meal": eng.hours_since_meal,
                "weather": eng.weather, "npcs_in_scene": [], "threat_id": "",
                "aura_targets": [], "active_buffs": list(eng.buffs.keys()) if eng.buffs else [],
                "charges": {k: v[0] for k, v in eng.charges.items()} if eng.charges else {},
            }
            ce_report = ce.check_engine(ce_state)
            report["continuity_check"] = ce_report
            ic = ce_report.count("!!") + ce_report.count("MISSING") + ce_report.count("BROKEN")
            if ic > 0:
                report["warnings"].append(f"Continuity: {ic} issue(s)")
            print(f"[4/7] CONTINUITY — loaded {character}, {ic} issue(s) ({reason})")
            _record_check_run(meta, "continuity")
        except Exception as e:
            report["continuity_load"] = f"FAILED: {e}"
            report["continuity_check"] = ""
            report["warnings"].append(f"Continuity failed: {e}")
            print(f"[4/7] CONTINUITY — FAILED: {e}")
    else:
        report["continuity_load"] = "skipped"
        report["continuity_check"] = ""
        print(f"[4/7] CONTINUITY — {reason}")

    # == 5. CITY LOCATION REGISTRY ==
    # Sampled — force-runs on location change (where it's actually informative).
    should_run, reason = _should_run_check(
        "city_registry", meta, audit=audit,
        force_on_change={"location": eng.location},
    )
    if should_run:
        city_data = load_city_registry(eng.location)
        report["city_registry"] = city_data
        cn = city_data.get("city", "none")
        lc = city_data.get("location_count", 0)
        print(f"[5/7] CITY REGISTRY — {cn or 'no match'} ({lc} locations) ({reason})")
        _record_check_run(meta, "city_registry")
    else:
        report["city_registry"] = {"checked": False, "reason": reason}
        print(f"[5/7] CITY REGISTRY — {reason}")

    # == 6. NARRATOR STYLE ==
    # Sampled at low frequency — narrator style is set once per character.
    should_run, reason = _should_run_check(
        "narrator_style", meta, audit=audit,
        force_on_change={"chapter": chapter_now},
    )
    if should_run:
        narrator = read_narrator_style(full_data)
        report["narrator_style"] = narrator
        print(f"[6/7] NARRATOR — {str(narrator)[:60]} ({reason})")
        _record_check_run(meta, "narrator_style")
    else:
        report["narrator_style"] = "skipped"
        print(f"[6/7] NARRATOR — {reason}")

    # == 7. DEADLINES + GOAL ALERTS ==
    # Always-run; both feeds are time-sensitive. Deadlines = events + dated quests.
    # Goal alerts = character_goals[] (PC + NPC) per DM_TURN_PROTOCOL step 0.
    deadlines = check_deadlines(eng, full_data)
    goal_alerts = check_character_goals(eng, full_data)
    report["deadlines"] = deadlines
    report["goal_alerts"] = goal_alerts

    overdue = [d for d in deadlines if d["status"] == "OVERDUE"]
    due_today = [d for d in deadlines if d["status"] == "DUE_TODAY"]
    fires_now = [g for g in goal_alerts if g["status"] == "FIRES_NOW"]
    g_overdue = [g for g in goal_alerts if g["status"] == "OVERDUE"]
    g_imminent = [g for g in goal_alerts if g["status"] == "IMMINENT"]

    if overdue:
        report["warnings"].extend([f"OVERDUE: {d['name']} (Day {d['day']})" for d in overdue])
    if fires_now:
        report["warnings"].extend([f"GOAL FIRES NOW: {g['name']}" for g in fires_now])
    if g_overdue:
        report["warnings"].extend([f"GOAL OVERDUE: {g['name']} (Day {g['day']})" for g in g_overdue])

    print(f"[7/7] DEADLINES & GOALS — events: {len(overdue)} overdue / {len(due_today)} today / {len(deadlines)} total | "
          f"goals: {len(fires_now)} firing / {len(g_overdue)} overdue / {len(g_imminent)} imminent / {len(goal_alerts)} alerted")

    # == DASHBOARD ==
    print(f"\n{'=' * 60}")
    print("DASHBOARD")
    print(f"{'=' * 60}")

    def _slot_str(k, v):
        if isinstance(v, (list, tuple)): return f"L{k}: {v[0]}/{v[1]}"
        elif isinstance(v, dict): return f"L{k}: {v.get('current','?')}/{v.get('max','?')}"
        return f"L{k}: {v}"

    slots_str = " | ".join(_slot_str(k, v) for k, v in sorted(eng.spell_slots.items())) if eng.spell_slots else "none"
    charges_str = _build_charge_str(eng).replace("**", "") if eng.charges else "none"
    exp_total = getattr(eng, "exp", 0)
    _etn = getattr(eng, "exp_to_next_level", None); _etn_value = int(_etn()) if callable(_etn) else (int(_etn) if isinstance(_etn, (int,float)) else 0); exp_next = exp_total + _etn_value

    print(f"  {eng.char_name} — Day {eng.day} | {time_str} | {eng.location}")
    print(f"  HP {eng.hp}/{eng.max_hp} | AC {getattr(eng, 'ac', '?')} | Level {eng.level} ({exp_total:,}/{exp_next:,})")
    print(f"  GP {eng.gold} | SP {eng.silver} | CP {getattr(eng, 'copper', 0)}")
    print(f"  Slots: {slots_str}")
    if eng.charges: print(f"  Charges: {charges_str}")
    if eng.buffs: print(f"  Buffs: {', '.join(eng.buffs.keys())}")
    print(f"  Weather: {eng.weather}")
    print(f"  Meals: {eng.meals} | Hours since meal: {eng.hours_since_meal}")
    if deadlines:
        print(f"  Event Deadlines:")
        for dl in deadlines:
            print(f"    [{dl['status']}] {dl['name']} — Day {dl['day']}")
    if goal_alerts:
        print(f"  Goal Alerts:")
        for ga in goal_alerts:
            time_part = f" {ga['due_time']}" if ga.get("due_time") and ":" in str(ga.get("due_time")) else ""
            print(f"    [{ga['status']}] {ga['character']}: {ga['goal_id']} — Day {ga['day']}{time_part}")

    # == INVENTORY ==
    _print_inventory(full_data, eng.char_name)

    # == PC ABILITIES ==
    pc_abilities = _collect_pc_abilities(full_data)
    report["pc_abilities"] = pc_abilities
    _print_pc_abilities(pc_abilities, eng.char_name)

    # == SCENE NPCs & ALLIES ==
    scene_npcs = _collect_scene_npcs(full_data, character, eng.location)
    report["scene_npcs"] = scene_npcs
    _print_scene_npcs(scene_npcs)

    # == KNOWN ENEMY ABILITIES ==
    enemy_info = _collect_enemy_info(full_data)
    report["known_enemies"] = enemy_info
    _print_enemy_info(enemy_info)

    # == PLAYER ACTION + COMBAT ENGINE ==
    if player_action:
        print(f"\n{'=' * 60}")
        print(f"PLAYER ACTION: \"{player_action}\"")
        print(f"{'=' * 60}")

    combat, combat_meta = _load_combat_state(character)

    if combat and combat.active:
        # --- CONTINUING COMBAT ---
        pc_name = eng.char_name
        if 0 <= combat.turn_idx < len(combat.order):
            current_name = combat.order[combat.turn_idx][1]
        else:
            current_name = ""

        # If player submitted an action and it's NOT their turn, process NPC turns first
        if player_action and current_name != pc_name and current_name:
            print(f"\n  Current turn: {current_name} (not {pc_name})")
            print(f"  Auto-advancing NPC turns to reach {pc_name}...")
            npc_turns = _process_npc_turns(combat, pc_name)
            _print_npc_turn_results(npc_turns)

            end_reason = _check_combat_end(combat, pc_name)
            if end_reason:
                print(f"\n  {'=' * 40}")
                if end_reason == "ALL_ENEMIES_DEAD":
                    print(f"  >>> COMBAT OVER — ALL ENEMIES DEFEATED <<<")
                    _clear_combat_state(character)
                    combat = None
                elif end_reason == "PC_DOWN":
                    print(f"  >>> {pc_name} IS DEAD — biological death (fatality or 2-rd window expired) <<<")
                elif end_reason == "PC_DYING":
                    print(f"  >>> {pc_name} IS DYING — 2-round window open, party should heal NOW <<<")
                print(f"  {'=' * 40}")

        # If still in combat and it's PC's turn, prompt for player input
        if combat and combat.active:
            if 0 <= combat.turn_idx < len(combat.order):
                whose = combat.order[combat.turn_idx][1]
            else:
                whose = ""
            _print_combat_dashboard(combat, whose)

            if player_action and whose == pc_name:
                pc_abilities_list = []
                cf = pc_abilities.get("class_features", []) or []
                if isinstance(cf, list):
                    for ab in cf:
                        if isinstance(ab, dict):
                            pc_abilities_list.append({
                                "name": ab.get("name", ""),
                                "data": ab,
                            })
                action_info = _classify_action(player_action, pc_abilities_list)
                results = _process_pc_combat_turn(combat, pc_name, action_info)
                _print_combat_action_results(results)

                end_reason = _check_combat_end(combat, pc_name)
                if end_reason:
                    print(f"\n  {'=' * 40}")
                    if end_reason == "ALL_ENEMIES_DEAD":
                        print(f"  >>> COMBAT OVER — ALL ENEMIES DEFEATED <<<")
                        _clear_combat_state(character)
                        combat = None
                    elif end_reason == "PC_DOWN":
                        print(f"  >>> {pc_name} IS DEAD <<<")
                    elif end_reason == "PC_DYING":
                        print(f"  >>> {pc_name} IS DYING — 2-round window open <<<")
                    elif end_reason == "PARTY_WIPED":
                        print(f"  >>> PARTY WIPED <<<")
                    print(f"  {'=' * 40}")
                else:
                    rnd, next_name = combat.next_turn()
                    print(f"\n  Next turn: {next_name} (Round {combat.round})")
                    if next_name != pc_name:
                        npc_turns = _process_npc_turns(combat, pc_name)
                        _print_npc_turn_results(npc_turns)
                        end_reason = _check_combat_end(combat, pc_name)
                        if end_reason:
                            print(f"\n  {'=' * 40}")
                            if end_reason == "ALL_ENEMIES_DEAD":
                                print(f"  >>> COMBAT OVER — ALL ENEMIES DEFEATED <<<")
                                _clear_combat_state(character)
                                combat = None
                            elif end_reason == "PC_DOWN":
                                print(f"  >>> {pc_name} IS DEAD <<<")
                            elif end_reason == "PC_DYING":
                                print(f"  >>> {pc_name} IS DYING — 2-round window open <<<")
                            print(f"  {'=' * 40}")

                if combat:
                    _save_combat_state(combat, character)
                    report["combat"] = {
                        "active": combat.active, "round": combat.round,
                    }
        elif not combat:
            report["combat"] = {"active": False, "ended": True}

    elif player_action:
        # --- CHECK IF PLAYER ACTION IMPLIES COMBAT START ---
        action_lower = player_action.lower()
        combat_keywords = [
            "attack", "fight", "engage", "strike", "hit", "kill", "combat",
            "tai chi", "kick", "melee", "cast", "spell", "healing dance",
            "initiative", "battle", "charge",
        ]
        wants_combat = any(kw in action_lower for kw in combat_keywords)

        if wants_combat:
            print(f"\n{'=' * 60}")
            print("COMBAT INITIALIZATION")
            print(f"{'=' * 60}")

            pc_data = _build_pc_combatant(full_data, eng)
            print(f"  PC: {pc_data['name']} HP {pc_data['hp']}/{pc_data['max_hp']} "
                  f"AC {pc_data['ac']} | ATK +{pc_data['attack_bonus']} "
                  f"| Spell DC {pc_data['spell_save_dc']}")

            ally_data = _build_ally_combatants(scene_npcs)
            for ad in ally_data:
                print(f"  ALLY: {ad['name']} HP {ad.get('hp', ad['max_hp'])}/{ad['max_hp']} "
                      f"AC {ad['ac']} | ATK +{ad['attack_bonus']}")

            # Detect monsters by keyword substring
            monsters_to_add = []
            for mk, mv in MONSTER_REGISTRY.items():
                keywords = mv.get("keywords", [mk.replace("_", " ")])
                if any(kw in action_lower for kw in keywords):
                    count = 1
                    for word in action_lower.split():
                        if word.isdigit():
                            count = int(word)
                            break
                    if count == 1:
                        for kw in keywords:
                            if kw + "s" in action_lower or kw + "es" in action_lower:
                                count = 3
                                break
                    md = dict(mv)
                    md["_count"] = count
                    monsters_to_add.append(md)

            if not monsters_to_add:
                print(f"  !! No monsters auto-detected in action text.")
                print(f"  Available monsters: {', '.join(MONSTER_REGISTRY.keys())}")
                print(f"  DM: specify which monsters and how many.")
            else:
                for md in monsters_to_add:
                    ct = md.get("_count", 1)
                    print(f"  ENEMY: {md['name']} x{ct} — HP {md['max_hp']} AC {md['ac']} "
                          f"| ATK +{md['attack_bonus']}")

                combat = _init_combat(pc_data, ally_data, monsters_to_add)
                rnd, first_name = combat.next_turn()
                _print_combat_dashboard(combat, first_name)

                _save_combat_state(combat, character, meta={
                    "started_by": player_action, "pc": eng.char_name,
                })
                print(f"\n  [COMBAT STATE SAVED] -> COMBAT_STATE.json")

                report["combat"] = {
                    "active": True, "round": combat.round,
                    "current_turn": first_name,
                    "initiative_order": combat.order,
                    "fighters": {n: {"hp": f.hp, "max_hp": f.max_hp, "ac": f.ac, "alive": f.alive}
                                 for n, f in combat.fighters.items()},
                }

    # == CARDINAL RULES ==
    # Per DM_TURN_PROTOCOL: print at every boot so the rules are visible to the AI/DM.
    # RULES 1-6 from before; RULES 7-8 added Day 9 (no fabricated program output;
    # no process interruptions for mature content).
    print(f"\n{'=' * 60}")
    print("CARDINAL RULES (see dm_rules_tracking.md)")
    print(f"{'=' * 60}")
    print("""  1. NEVER write the PC's dialogue. STOP for player.
  2. NEVER auto-resolve combat. Round-by-round ONLY.
  3. STOP at every decision point. Present, don't decide.
  4. No fabricated exposition NPCs (RULE 4).
  5. 60% dialogue minimum in NPC scenes (RULE 5).
  6. Style tax — describe the cool moves with detail (RULE 6).
  7. NO fabricated program output. Engine-styled output only when bash actually
     ran the script. State summaries between turns are plain prose.
  8. NO process interruptions for mature content. Hold concerns once-and-done in
     the same response that offers a workable alternative AND writes the version.
     Forward momentum is the default.""")
    report["cardinal_rules"] = "PRINTED"

    # == SUMMARY ==
    print(f"{'=' * 60}")
    if report["errors"]:
        print(f"ERRORS: {len(report['errors'])}")
        for e in report["errors"]: print(f"  !! {e}")
    if report["warnings"]:
        print(f"WARNINGS: {len(report['warnings'])}")
        for w in report["warnings"]: print(f"  ! {w}")
    if not report["errors"] and not report["warnings"]:
        print("ALL SYSTEMS GREEN")
    print(f"{'=' * 60}")

    report_path = SCRIPT_DIR / "GAMEMODE_REPORT.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8"
    )
    print(f"\n[REPORT] Wrote GAMEMODE_REPORT.json")

    # Persist call counter + last seen chapter/location for next call's
    # change-detection. Updates last_chapter/last_location AFTER any change-driven
    # check has already fired this turn.
    meta["last_chapter"] = chapter_now
    meta["last_location"] = eng.location
    _save_gamemode_meta(character, meta)

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    argv = list(sys.argv[1:])
    character = "kenji"
    audit = False
    if "--character" in argv:
        idx = argv.index("--character")
        if idx + 1 < len(argv):
            character = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2:]
        else:
            print("ERROR: --character requires a name", file=sys.stderr)
            sys.exit(1)
    if "--audit" in argv:
        audit = True
        argv = [a for a in argv if a != "--audit"]
    player_action = " ".join(argv)
    result = gamemode(character=character, player_action=player_action, audit=audit)
    sys.exit(0 if result["status"] == "OK" else 1)