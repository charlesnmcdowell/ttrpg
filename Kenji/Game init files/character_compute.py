#!/usr/bin/env python3
"""character_compute.py — Pure functions for deriving character stats from
base + racial inputs.

WHY THIS EXISTS
---------------
Cardinal Rule 9: prose is authoritative for events; JSON is authoritative for
state. Within the JSON, MANY values are *derived* — ability mod from final
score, HP from CON mod, AC from DEX/WIS mods, skill bonuses from ability mod
+ prof, etc. When base or racial fields change (level-up, ember toggle, racial
heritage adjustment), every derived value goes stale. The dashboard reads
the stale values and the math drifts.

Without a single source of truth for the derivation, every character bug is
a Whack-a-Mole hunt. This module is that single source.

USAGE
-----
Programmatic:
    from character_compute import recompute_character_state
    state = json.load(open(state_path))
    report = recompute_character_state(state)
    print(report['changes'])
    json.dump(state, open(state_path, 'w'), indent=2)

CLI (via _dm_turn.py):
    python _dm_turn.py --character shen_sama recompute
        # Shows diff. Use --apply to write.
    python _dm_turn.py --character shen_sama recompute --apply
        # Applies changes to character_world_state.json

DESIGN GUARANTEES
-----------------
- IDEMPOTENT: running recompute twice returns the same state.
- MINIMAL TOUCH: only fields that need to change are touched.
- HUMAN-READABLE DIFF: every change is reported with old + new values.
- SAFE: never deletes user-authored fields; only updates known derived fields.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional


# Skill-to-ability mapping (5e standard).
SKILL_TO_ABILITY = {
    "Acrobatics":      "DEX",
    "Animal Handling": "WIS",
    "Arcana":          "INT",
    "Athletics":       "STR",
    "Deception":       "CHA",
    "History":         "INT",
    "Insight":         "WIS",
    "Intimidation":    "CHA",
    "Investigation":   "INT",
    "Medicine":        "WIS",
    "Nature":          "INT",
    "Perception":      "WIS",
    "Performance":     "CHA",
    "Persuasion":      "CHA",
    "Religion":        "INT",
    "Sleight of Hand": "DEX",
    "Stealth":         "DEX",
    "Survival":        "WIS",
    # Custom-class skills can be added here as they emerge.
    "Tai Chi":         "DEX",   # Cookie's Dancer combat-style
    "Dancing":         "CHA",   # Cookie's Dance Inspiration domain
    "Singing":         "CHA",   # Cookie's vocal performance
}

# Default hit-die sizes by class — used when no explicit hit_die in JSON.
CLASS_HIT_DIE = {
    "barbarian": 12, "fighter": 10, "paladin": 10, "ranger": 10,
    "monk":       8, "rogue":   8, "bard":    8, "cleric":  8,
    "druid":      8, "warlock": 8,
    "sorcerer":   6, "wizard":  6,
}


# True-dragon racial-bonus stat affinity per dragon color/type.
# Each chromatic/metallic dragon's heritage targets two ability scores that
# match its physical/magical archetype. The "+1 per year alive" true-dragon
# bonus only applies to those two stats; the others use base values.
#
# Reference cases in this universe:
#   - Shen Sama (Vorathiel's son) — BLACK dragon → STR + CON. Brute, melee,
#     dragonhide, breath as area weapon.
#   - Ignis (Kenji's daughter) — RED dragon → CHA + INT. Sorcerer self-label,
#     fire magic, charisma + intellect as caster pillars.
#
# Other entries are placeholders aligned to D&D archetype convention; refine
# as new true-dragon Ankuspawn appear in canon.
DRAGON_STAT_AFFINITY = {
    "black":   ["STR", "CON"],   # melee brute, hide
    "red":     ["CHA", "INT"],   # sorcerer-tier caster, fire magic
    "blue":    ["DEX", "WIS"],   # storm caster, lightning, foresight
    "green":   ["INT", "DEX"],   # cunning forest predator
    "white":   ["STR", "WIS"],   # blizzard hunter, instinctual
    "gold":    ["CHA", "WIS"],   # benevolent radiant caster
    "silver":  ["CHA", "STR"],   # paladin-tier valor
    "bronze":  ["INT", "STR"],   # storm-tactician
    "copper":  ["DEX", "INT"],   # trickster
    "brass":   ["CHA", "DEX"],   # bard-tier conversationalist
}


# Canon rule: when a true-dragon Ankuspawn's Ember is active, the per-year
# bonus is 10× the baseline. When Ember is nullified (Cult Ember-Shade ward,
# dispel, etc.), the bonus reverts to the baseline 1×. This constant lives
# here so the multiplier cannot drift from data corruption — the tool
# computes from EMBER_ACTIVE flag + this constant, not from a per-character
# multiplier field.
EMBER_ACTIVE_MULTIPLIER = 10
EMBER_INACTIVE_MULTIPLIER = 1
DRAGON_BASELINE_PER_YEAR = 1


def compute_dragon_racial_bonus(age_years: int, dragon_type: str,
                                  ember_active: bool = True) -> Dict[str, int]:
    """Return {stat_name: racial_bonus} for a true-dragon character.

    Rules (canonical, NOT per-character configurable):
        - When ember_active: per_year = DRAGON_BASELINE_PER_YEAR × EMBER_ACTIVE_MULTIPLIER
        - When ember inactive: per_year = DRAGON_BASELINE_PER_YEAR × 1 (baseline)
        - applies ONLY to the two stats in DRAGON_STAT_AFFINITY[dragon_type]
        - other stats receive 0
    """
    affinity = DRAGON_STAT_AFFINITY.get((dragon_type or "").lower(), [])
    multiplier = EMBER_ACTIVE_MULTIPLIER if ember_active else EMBER_INACTIVE_MULTIPLIER
    per_year = DRAGON_BASELINE_PER_YEAR * multiplier
    total = age_years * per_year if age_years > 0 else 0
    return {stat: (total if stat in affinity else 0)
            for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA")}


def apply_dragon_inheritance(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """If state has a dragon_inheritance block, write the resulting racial
    bonuses into mechanical_state.ability_scores. Returns a list of changes.

    Expected dragon_inheritance schema:
        {
          "is_true_dragon": true,
          "dragon_type": "black" | "red" | ...,
          "age_years": 24,
          "ember_active": true,
          "ember_multiplier": 10,
          "baseline_per_year": 1
        }
    """
    di = state.get("dragon_inheritance")
    if not isinstance(di, dict) or not di.get("is_true_dragon"):
        return []
    ms = state.get("mechanical_state") or {}
    ab = ms.get("ability_scores")
    if not isinstance(ab, dict):
        return []
    # ember_multiplier and baseline_per_year are deprecated — the tool now
    # uses EMBER_ACTIVE_MULTIPLIER (10) and DRAGON_BASELINE_PER_YEAR (1) as
    # canon constants. If those fields exist on the character data we just
    # log a warning so the user knows they're being ignored.
    if "ember_multiplier" in di or "baseline_per_year" in di:
        # Caller can read this from the changes report — it'll surface in
        # recompute reports as a 'warnings' entry via the wrapper.
        di["_deprecated_fields_ignored"] = (
            "ember_multiplier and baseline_per_year are no longer per-character "
            "configurable. The tool uses canon constants: ember-active = 10×, "
            "ember-nullified = 1×, baseline = +1/year."
        )
    bonuses = compute_dragon_racial_bonus(
        age_years=int(di.get("age_years", 0) or 0),
        dragon_type=di.get("dragon_type", ""),
        ember_active=bool(di.get("ember_active", True)),
    )
    changes = []
    for stat, new_racial in bonuses.items():
        block = ab.get(stat)
        if not isinstance(block, dict):
            continue
        old_racial = block.get("racial", 0)
        if old_racial != new_racial:
            changes.append({
                "field": f"ability_scores.{stat}.racial",
                "old": old_racial, "new": new_racial,
                "source": f"dragon_inheritance ({di.get('dragon_type')} dragon, age {di.get('age_years')})",
            })
            block["racial"] = new_racial
    return changes


def compute_mod(score: int) -> int:
    """5e ability score → modifier. Floor of (score - 10) / 2."""
    if not isinstance(score, (int, float)):
        return 0
    return (int(score) - 10) // 2


def recompute_ability_scores(ability_scores: Dict[str, Any]) -> List[Dict[str, Any]]:
    """For each ability, set final = base + racial, mod = compute_mod(final).

    Mutates the dict in place. Returns a list of {stat, old, new} change records.
    Skips entries where base/racial isn't present or isn't a number.
    """
    changes = []
    for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
        if stat not in ability_scores:
            continue
        block = ability_scores[stat]
        if not isinstance(block, dict):
            continue
        base = block.get("base", 10)
        racial = block.get("racial", 0)
        if not isinstance(base, (int, float)) or not isinstance(racial, (int, float)):
            continue
        new_final = int(base) + int(racial)
        new_mod = compute_mod(new_final)
        old_final = block.get("final")
        old_mod = block.get("mod")
        if old_final != new_final or old_mod != new_mod:
            changes.append({
                "stat": stat,
                "old": {"final": old_final, "mod": old_mod},
                "new": {"final": new_final, "mod": new_mod},
            })
            block["final"] = new_final
            block["mod"] = new_mod
    return changes


def compute_max_hp(level: int, hit_die: int, con_mod: int) -> int:
    """5e standard:
        L1: max hit die + CON mod
        L2+: per level, average hit die roll (rounded up) + CON mod
             = ((hit_die // 2) + 1) + CON mod per level

    Returns the total max HP at the given level. Negative results clamped to 1.
    """
    if level < 1:
        return 0
    if hit_die < 4:
        hit_die = 8   # safe fallback
    l1 = hit_die + con_mod
    avg_per_level = (hit_die // 2) + 1 + con_mod
    total = l1 + avg_per_level * (level - 1)
    return max(1, total)


def compute_monk_unarmored_ac(dex_mod: int, wis_mod: int) -> int:
    """Monk Unarmored Defense: 10 + DEX mod + WIS mod."""
    return 10 + dex_mod + wis_mod


def compute_barbarian_unarmored_ac(dex_mod: int, con_mod: int) -> int:
    """Barbarian Unarmored Defense: 10 + DEX mod + CON mod."""
    return 10 + dex_mod + con_mod


def compute_default_ac(dex_mod: int) -> int:
    """No-armor baseline: 10 + DEX mod."""
    return 10 + dex_mod


def detect_ac_formula(class_str: str) -> str:
    """Return one of: 'monk', 'barbarian', 'monk_barbarian', 'default'."""
    cs = (class_str or "").lower()
    has_monk = "monk" in cs
    has_barb = "barbarian" in cs
    if has_monk and has_barb:
        return "monk_barbarian"   # take the higher of the two
    if has_monk:
        return "monk"
    if has_barb:
        return "barbarian"
    return "default"


def compute_ac(ability_scores: Dict[str, Any], class_str: str,
               natural_armor_bonus: int = 0) -> int:
    """Pick the right unarmored-AC formula based on class.

    natural_armor_bonus: optional flat bonus from racial hide / dragon scale.
    For Monk/Barbarian, the unarmored formula already exceeds raw 10+armor in
    most cases, so the natural-armor bonus is added on TOP of the chosen formula.
    """
    if not isinstance(ability_scores, dict):
        return 10
    dex_mod = ability_scores.get("DEX", {}).get("mod", 0) or 0
    wis_mod = ability_scores.get("WIS", {}).get("mod", 0) or 0
    con_mod = ability_scores.get("CON", {}).get("mod", 0) or 0
    formula = detect_ac_formula(class_str)
    if formula == "monk_barbarian":
        ac = max(
            compute_monk_unarmored_ac(dex_mod, wis_mod),
            compute_barbarian_unarmored_ac(dex_mod, con_mod),
        )
    elif formula == "monk":
        ac = compute_monk_unarmored_ac(dex_mod, wis_mod)
    elif formula == "barbarian":
        ac = compute_barbarian_unarmored_ac(dex_mod, con_mod)
    else:
        ac = compute_default_ac(dex_mod)
    return ac + natural_armor_bonus


def compute_skill_bonus(skill_name: str, ability_scores: Dict[str, Any],
                         proficient: bool, prof_bonus: int) -> Optional[int]:
    """Skill bonus = ability mod + (prof_bonus if proficient else 0)."""
    ability = SKILL_TO_ABILITY.get(skill_name)
    if not ability:
        return None
    mod = (ability_scores.get(ability) or {}).get("mod", 0) or 0
    return mod + (prof_bonus if proficient else 0)


def compute_save_bonus(ability_name: str, ability_scores: Dict[str, Any],
                        proficient: bool, prof_bonus: int) -> int:
    """Saving throw bonus = ability mod + (prof_bonus if proficient else 0)."""
    mod = (ability_scores.get(ability_name) or {}).get("mod", 0) or 0
    return mod + (prof_bonus if proficient else 0)


def _hit_die_from_class(class_str: str, default: int = 8) -> int:
    """Pick the larger hit die when class is multiclass (Monk/Barbarian → d12)."""
    cs = (class_str or "").lower()
    sizes = [size for keyword, size in CLASS_HIT_DIE.items() if keyword in cs]
    return max(sizes) if sizes else default


def recompute_character_state(state: Dict[str, Any],
                                hit_die_override: Optional[int] = None,
                                natural_armor_bonus: int = 0) -> Dict[str, Any]:
    """Top-level: recompute everything from base + racial in a state dict.

    Mutates `state` in place. Returns a report of changes.
    """
    report: Dict[str, Any] = {"changes": [], "warnings": []}

    ms = state.get("mechanical_state")
    if not isinstance(ms, dict):
        report["warnings"].append("No mechanical_state block — nothing to recompute.")
        return report

    # 0. Auto-apply dragon inheritance: writes racial bonuses for true dragons
    #    based on dragon_type and age_years. Skipped silently for non-dragon PCs.
    di_changes = apply_dragon_inheritance(state)
    report["changes"].extend(di_changes)

    # 1. Recompute ability mods from base + racial.
    ab = ms.get("ability_scores")
    if isinstance(ab, dict):
        ab_changes = recompute_ability_scores(ab)
        for c in ab_changes:
            report["changes"].append({"field": f"ability_scores.{c['stat']}", **c})
    else:
        report["warnings"].append("ability_scores block missing or malformed.")
        return report

    # 2. Recompute HP from level + hit die + CON mod.
    level = ms.get("level", 1) or 1
    class_str = ms.get("class", "") or ""
    hit_die = hit_die_override or _hit_die_from_class(class_str, default=8)
    con_mod = (ab.get("CON") or {}).get("mod", 0) or 0
    new_hp_max = compute_max_hp(level, hit_die, con_mod)
    old_hp = ms.get("hp")
    if old_hp != new_hp_max:
        report["changes"].append({
            "field": "mechanical_state.hp", "old": old_hp, "new": new_hp_max,
        })
        ms["hp"] = new_hp_max
    # Mirror to _story_engine_state.max_hp (and clamp current hp if it now exceeds).
    ses = state.get("_story_engine_state")
    if isinstance(ses, dict):
        old_max = ses.get("max_hp")
        if old_max != new_hp_max:
            report["changes"].append({
                "field": "_story_engine_state.max_hp", "old": old_max, "new": new_hp_max,
            })
            ses["max_hp"] = new_hp_max
        cur = ses.get("hp", new_hp_max)
        if isinstance(cur, (int, float)) and cur > new_hp_max:
            report["changes"].append({
                "field": "_story_engine_state.hp",
                "old": cur, "new": new_hp_max,
                "note": "current HP clamped to new max",
            })
            ses["hp"] = new_hp_max

    # 3. Recompute AC from class + ability mods.
    new_ac = compute_ac(ab, class_str, natural_armor_bonus=natural_armor_bonus)
    old_ac = ms.get("AC")
    if old_ac != new_ac:
        report["changes"].append({
            "field": "mechanical_state.AC", "old": old_ac, "new": new_ac,
            "formula": detect_ac_formula(class_str),
        })
        ms["AC"] = new_ac
    if isinstance(ses, dict):
        old_ses_ac = ses.get("ac")
        if old_ses_ac != new_ac:
            report["changes"].append({
                "field": "_story_engine_state.ac", "old": old_ses_ac, "new": new_ac,
            })
            ses["ac"] = new_ac

    # 4. Recompute skill bonuses.
    skills = ms.get("skills", {})
    prof_bonus = ms.get("proficiency_bonus", 2) or 2
    if isinstance(skills, dict):
        for skill_name in list(skills.keys()):
            if skill_name.startswith("_"):
                continue
            ability = SKILL_TO_ABILITY.get(skill_name)
            if not ability:
                continue
            # Determine proficiency by parsing existing bonus string for "prof".
            old_value = skills[skill_name]
            proficient = "prof" in str(old_value).lower()
            bonus = compute_skill_bonus(skill_name, ab, proficient, prof_bonus)
            if bonus is None:
                continue
            sign = "+" if bonus >= 0 else ""
            ability_mod = (ab.get(ability) or {}).get("mod", 0) or 0
            ability_sign = "+" if ability_mod >= 0 else ""
            new_str = f"{sign}{bonus} ({ability} {ability_sign}{ability_mod}"
            if proficient:
                new_str += f", prof +{prof_bonus}"
            new_str += ")"
            if str(old_value) != new_str:
                report["changes"].append({
                    "field": f"skills.{skill_name}",
                    "old": old_value, "new": new_str,
                })
                skills[skill_name] = new_str

    # 5. Recompute saving throw bonuses.
    saves = ms.get("saving_throws", {})
    if isinstance(saves, dict):
        prof_list = saves.get("proficient", []) or []
        for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
            key = f"{stat}_save"
            proficient = stat in prof_list
            bonus = compute_save_bonus(stat, ab, proficient, prof_bonus)
            sign = "+" if bonus >= 0 else ""
            ability_mod = (ab.get(stat) or {}).get("mod", 0) or 0
            ability_sign = "+" if ability_mod >= 0 else ""
            new_str = f"{sign}{bonus} ({stat} {ability_sign}{ability_mod}"
            if proficient:
                new_str += f", prof +{prof_bonus}"
            new_str += ")"
            old_value = saves.get(key)
            if old_value is not None and str(old_value) != new_str:
                report["changes"].append({
                    "field": f"saving_throws.{key}",
                    "old": old_value, "new": new_str,
                })
                saves[key] = new_str

    return report


def format_report(report: Dict[str, Any]) -> str:
    """Pretty-print a recompute report for CLI / drift-check display."""
    lines = []
    if report.get("warnings"):
        lines.append("WARNINGS:")
        for w in report["warnings"]:
            lines.append(f"  - {w}")
    changes = report.get("changes", [])
    if not changes:
        lines.append("OK — no derived values changed. Character math is consistent.")
        return "\n".join(lines)
    lines.append(f"CHANGES ({len(changes)}):")
    for c in changes:
        field = c.get("field", "?")
        if "stat" in c:
            old = c["old"]
            new = c["new"]
            lines.append(f"  {field}:  final {old.get('final')} → {new.get('final')},  mod {old.get('mod')} → {new.get('mod')}")
        else:
            old = c.get("old")
            new = c.get("new")
            note = c.get("note", "")
            lines.append(f"  {field}:  {old} → {new}" + (f"  ({note})" if note else ""))
    return "\n".join(lines)


# CLI front-end (runnable standalone, also imported by _dm_turn.py)

def _cli():
    import argparse
    import json
    from pathlib import Path

    p = argparse.ArgumentParser(
        description="Recompute derived character stats from base + racial inputs."
    )
    p.add_argument("state_file", type=Path, help="Path to character_world_state.json")
    p.add_argument("--apply", action="store_true",
                    help="Write changes back to the file. Without this, prints diff only.")
    p.add_argument("--natural-armor", type=int, default=0,
                    help="Natural-armor bonus added on top of unarmored AC formula.")
    args = p.parse_args()

    if not args.state_file.exists():
        print(f"ERROR: {args.state_file} not found.")
        return 1
    raw = args.state_file.read_text(encoding="utf-8")
    state = json.loads(raw)
    report = recompute_character_state(state, natural_armor_bonus=args.natural_armor)
    print(format_report(report))
    if args.apply and report.get("changes"):
        args.state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
        print(f"\nApplied to {args.state_file}")
    elif report.get("changes"):
        print("\n(diff only — pass --apply to write changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
