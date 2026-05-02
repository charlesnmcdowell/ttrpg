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
import json
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


# Cardinal Rule 11: Power Override Scaling.
# Character creation enforces a 72-point base-stat cap (sum of STR+DEX+CON+
# INT+WIS+CHA, before racial bonuses) and an L1 starting level. Any character
# created above either threshold is "power-override" and triggers auto-scaled
# threats + counter-strategy weighting + the honeymoon→escalation curve.
# See dm_rules_tracking.md § RULE 11 for the full obligation.
#
# Honeymoon is measured in IN-GAME HOURS (not days) so escalation kicks in
# within a single play session. Most sittings cover ~24 in-game hours, so
# the OP-feel window naturally ends about when the player wraps for the day.
POINT_BUY_CAP = 72
STANDARD_STARTING_LEVEL = 1
HONEYMOON_HOURS = 24                  # 0-24h = honeymoon, OP feel
FIRST_COUNTER_HOURS = 48              # 24-48h = first counter telegraphed
COMPOUND_ESCALATION_HOURS = 168       # 48-168h (~Day 7) = compound counters
                                       # 168+h = existential phase opens


def detect_power_override(state: Dict[str, Any]) -> Dict[str, Any]:
    """Detect whether a character exceeds the standard 72-point / L1 baseline,
    and if so, compute the override factor + escalation state.

    This function is idempotent — it can be re-run on a state file to refresh
    `honeymoon_days_remaining` based on the current in-game day.

    Returns a dict with:
        is_override:              bool — true if base_points > 72 OR level > 1
        override_factor:          float — (base_points / 72) × level (capped at 9999)
        base_points_total:        int — sum of base STR+DEX+CON+INT+WIS+CHA
        starting_level:           int — current level (used as level multiplier)
        cap_breach_points:        int — how many points over the 72-point cap
        cap_breach_levels:        int — how many levels above L1
        honeymoon_days_remaining: int — days until counter rotation begins
        honeymoon_active:         bool — true while the player feels OP
        weaknesses:               list — declared weaknesses from the state
        recommended_phase:        str — 'honeymoon' | 'first_counter' | 'compound_escalation'
    """
    ms = state.get("mechanical_state") or {}
    ab = ms.get("ability_scores") or {}

    # Sum standard six (skip LUCK and any other extra ability scores).
    standard_six = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
    base_points = 0
    for s in standard_six:
        blk = ab.get(s)
        if isinstance(blk, dict):
            base = blk.get("base", 10)
            if isinstance(base, (int, float)):
                base_points += int(base)

    level = int(ms.get("level", 1) or 1)

    cap_breach_points = max(0, base_points - POINT_BUY_CAP)
    cap_breach_levels = max(0, level - STANDARD_STARTING_LEVEL)
    is_override = cap_breach_points > 0 or cap_breach_levels > 0

    if is_override:
        stat_factor = max(1.0, base_points / POINT_BUY_CAP)
        level_factor = max(1, level)
        override_factor = round(min(9999.0, stat_factor * level_factor), 2)
    else:
        override_factor = 1.0

    # Honeymoon window: HONEYMOON_HOURS of in-game time from start (Day 1, h0).
    # Compressed to one in-game day so escalation begins within a single play
    # session — most sittings cover roughly 24 in-game hours.
    ses = state.get("_story_engine_state") or {}
    cur_day = int(ses.get("day", 1) or 1)
    cur_hour = int(float(ses.get("hour", 0) or 0))
    elapsed_hours = max(0, (cur_day - 1) * 24 + cur_hour)
    honeymoon_hours_remaining = max(0, HONEYMOON_HOURS - elapsed_hours) if is_override else 0
    honeymoon_active = is_override and honeymoon_hours_remaining > 0

    if not is_override:
        recommended_phase = "standard"
    elif honeymoon_active:
        recommended_phase = "honeymoon"
    elif elapsed_hours < FIRST_COUNTER_HOURS:
        recommended_phase = "first_counter"
    elif elapsed_hours < COMPOUND_ESCALATION_HOURS:
        recommended_phase = "compound_escalation"
    else:
        recommended_phase = "existential"

    # Pull declared weaknesses from common locations on the state.
    weaknesses: List[str] = []
    flaw = ms.get("character_flaw")
    if isinstance(flaw, str) and flaw.strip():
        weaknesses.append(f"character_flaw: {flaw[:200]}")
    persistent = state.get("persistent_effects") or {}
    for eff in (persistent.get("on_pc") or []):
        if isinstance(eff, dict) and eff.get("type") == "debuff":
            name = eff.get("effect_name") or "(unnamed debuff)"
            mech = eff.get("mechanical_effect") or ""
            weaknesses.append(f"environmental_debuff: {name} — {mech[:120]}")
    # Patron / ember suppression vectors are also valid counters.
    pg = state.get("patron_gift") or {}
    for vector in (pg.get("suppression_threats") or []):
        if isinstance(vector, dict):
            t = vector.get("type") or "(unnamed)"
            v = vector.get("vector") or ""
            weaknesses.append(f"patron_suppression: {t} — {v[:120]}")
    ei = state.get("ember_inheritance") or {}
    if ei.get("growth_stage"):
        # Ember-bearing characters are suppressible by Cult Ember-Shade ward.
        weaknesses.append("ember_suppression: Cult Ember-Shade ward (or equivalent) nullifies ember-tier abilities")

    return {
        "is_override": is_override,
        "override_factor": override_factor,
        "base_points_total": base_points,
        "starting_level": level,
        "cap_breach_points": cap_breach_points,
        "cap_breach_levels": cap_breach_levels,
        "honeymoon_hours_remaining": honeymoon_hours_remaining,
        "honeymoon_active": honeymoon_active,
        "elapsed_in_game_hours": elapsed_hours,
        "weaknesses": weaknesses,
        "recommended_phase": recommended_phase,
        "_canon_constants": {
            "point_buy_cap": POINT_BUY_CAP,
            "standard_starting_level": STANDARD_STARTING_LEVEL,
            "honeymoon_hours": HONEYMOON_HOURS,
            "first_counter_hours": FIRST_COUNTER_HOURS,
            "compound_escalation_hours": COMPOUND_ESCALATION_HOURS,
        },
    }


# Cardinal Rule 12: Low-Stat Quirks.
# Any base ability score below 10 in STR/DEX/CON/INT/WIS/CHA auto-generates
# an engine-canonical quirk that the DM must enforce at the table. The
# 72-point cap means balanced characters almost always have at least one
# low stat; this rule turns the trade-off into mechanical reality.
LOW_STAT_THRESHOLD = 10

LOW_STAT_QUIRK_TEMPLATES = {
    "STR": {
        "name": "Weak",
        "effect": (
            "Cannot pull off raw physical feats — heavy lifting, hard hits, "
            "long jumps, breaking-down doors. Disadvantage on STR athletics. "
            "Easy to knock prone (DC against grapples and shoves drops by 2). "
            "The world says no when they try to brute-force a problem."
        ),
    },
    "DEX": {
        "name": "Clumsy",
        "effect": (
            "Always falling, knocking things over, running into walls. "
            "Disadvantage on DEX saves. -1 AC against opportunity attacks. "
            "Narrator describes small clumsiness in movement-heavy scenes "
            "(knocked-over chair, spilled drink, grazed elbow). Stealth is "
            "functionally impossible without help."
        ),
    },
    "CON": {
        "name": "Squishy",
        "effect": (
            "Dies fast — HP scales as if CON 8 even if base is lower. "
            "Disadvantage on CON saves vs disease, poison, exhaustion. "
            "Affected disproportionately by alcohol, drugs, harm — half a "
            "normal dose is a full effect. Catches diseases on contact "
            "exposure rolls instead of penetration-exposure."
        ),
    },
    "INT": {
        "name": "Slow",
        "effect": (
            "Cannot read complex text (basic literacy only — signs, names, "
            "single-page notes; books/scrolls/contracts beyond a certain "
            "length require a roll or a translator). Plans often fail or go "
            "sideways — DM rolls d20+INT_mod when the player declares a "
            "multi-step plan; on a fail, one step in the plan goes wrong in "
            "a way the character should have foreseen. Knowledge skills "
            "(Arcana, History, Investigation, Religion) at disadvantage "
            "without proficiency."
        ),
    },
    "WIS": {
        "name": "Indulgent",
        "effect": (
            "Has to roll WIS saves to resist temptations the character "
            "doesn't intend. Minimum trigger list: alcohol/drugs (DC 12 to "
            "refuse a drink offered), unnecessary spending (DC 12 to walk "
            "past a shiny purchase), buying too much food (DC 12 at any "
            "market stall), other unwise decisions (DC 12-18 by strength). "
            "Failed save = the character does the unwise thing. Player's "
            "intent is OVERRIDDEN by the WIS quirk on a failed roll."
        ),
    },
    "CHA": {
        "name": "Off-Putting",
        "effect": (
            "Civilized authorities default to suspicion or hostility. "
            "Persuasion DC raised by +5 in any settlement on first contact. "
            "Strangers do not warm without intermediary or demonstration. "
            "Reaction rolls trend toward wary or hostile."
        ),
    },
}


def _quirk_severity(base: int) -> str:
    """Map a base ability score below 10 to a severity tier."""
    if base >= 9:
        return "mild"
    if base >= 7:
        return "moderate"
    if base >= 4:
        return "severe"
    return "crippling"


def detect_low_stat_quirks(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scan ability_scores for any BASE value below LOW_STAT_THRESHOLD and
    return a list of quirk dicts. BASE-ONLY by design — items/abilities/spells
    that temporarily lower a stat do NOT generate quirks; the cure for those
    is to dispel/destroy/neutralize the source (Cardinal Rule 12 SCOPE clause).

    Each quirk has stat, base, severity, name, effect, and a _rule_ref pointer
    back to dm_rules_tracking.md § RULE 12.
    """
    ms = state.get("mechanical_state") or {}
    ab = ms.get("ability_scores") or {}
    quirks: List[Dict[str, Any]] = []
    for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
        blk = ab.get(stat)
        if not isinstance(blk, dict):
            continue
        base = blk.get("base")
        if not isinstance(base, (int, float)):
            continue
        base = int(base)
        if base >= LOW_STAT_THRESHOLD:
            continue
        tmpl = LOW_STAT_QUIRK_TEMPLATES.get(stat) or {}
        quirks.append({
            "stat": stat,
            "base_value": base,
            "severity": _quirk_severity(base),
            "name": tmpl.get("name", "Quirk"),
            "effect": tmpl.get("effect", ""),
            "_rule_ref": "dm_rules_tracking.md § RULE 12",
        })
    return quirks


# Cardinal Rule 13: High-Stat Justification.
# Any base ability score above 20 must be justified by a class feature,
# racial trait, patron gift, or equipped item. If unjustified, a contextual
# quirk that drops the stat under 20 in defined circumstances is required.
HIGH_STAT_THRESHOLD = 20

# Searchable text keys per stat — for the heuristic justification scan.
HIGH_STAT_KEYWORDS = {
    "STR": ["str", "strength", "athletic", "carrying", "lift"],
    "DEX": ["dex", "dexterity", "agility", "reflex", "acrobat"],
    "CON": ["con", "constitution", "stamina", "endurance", "hardy"],
    "INT": ["int", "intelligence", "intellect", "lore", "scholar"],
    "WIS": ["wis", "wisdom", "perception", "insight", "instinct"],
    "CHA": ["cha", "charisma", "presence", "persuad", "performance"],
}


def _high_stat_severity(base: int) -> str:
    if base <= 24:
        return "mild"
    if base <= 30:
        return "moderate"
    if base <= 50:
        return "severe"
    return "crippling"


def _scan_for_stat_justification(state: Dict[str, Any], stat: str) -> List[str]:
    """Return a list of sources where this stat is referenced as justified
    (class features, perks, racial traits, equipped, dragon inheritance,
    patron gift). Empty list = unjustified.
    """
    keywords = HIGH_STAT_KEYWORDS.get(stat, [stat.lower()])
    sources: List[str] = []
    ms = state.get("mechanical_state") or {}
    ses = state.get("_story_engine_state") or {}

    def _check(blob: Any, label: str) -> None:
        text = json.dumps(blob, ensure_ascii=False).lower() if blob is not None else ""
        if any(k in text for k in keywords):
            sources.append(label)

    # Direct affinity blocks: dragon affinity stat list is authoritative.
    di = state.get("dragon_inheritance") or {}
    if isinstance(di, dict) and di.get("is_true_dragon"):
        affinity = [s.upper() for s in (di.get("stat_affinity") or [])]
        if stat in affinity:
            sources.append(f"dragon_inheritance (affinity {di.get('dragon_type')})")

    # Other blocks scanned by keyword.
    for key, lab in [
        ("active_perks", "active_perks"),
        ("class_features", "class_features"),
        ("equipped", "equipped"),
    ]:
        for blob in (ses.get(key) or []):
            _check(blob, f"_story_engine_state.{lab}")
            if sources and sources[-1].startswith("_story_engine_state"):
                break
    _check(state.get("racial_traits"), "racial_traits")
    _check(state.get("patron_gift"), "patron_gift")
    _check(state.get("ember_inheritance"), "ember_inheritance")
    return sources


def detect_high_stat_quirks(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scan ability_scores for BASE values above HIGH_STAT_THRESHOLD. BASE-ONLY
    by design — items/abilities/spells that temporarily raise a stat do NOT
    generate quirks; the counter for those is to deplete/dispel/destroy/remove
    the buff source (Cardinal Rule 13 SCOPE clause). Example: base STR 16 with
    a +8 STR gauntlet (final STR 24) generates ZERO quirks — knocking the
    gauntlet off / dispelling the magic IS the counter.

    For each base stat above 20, determine whether it's justified by an
    existing class feature, racial trait, patron gift, or equipped item. If
    unjustified, emit a quirk record marking the stat as needing a contextual
    debuff that drops the stat under 20 in defined circumstances.
    """
    ms = state.get("mechanical_state") or {}
    ab = ms.get("ability_scores") or {}
    high: List[Dict[str, Any]] = []
    for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
        blk = ab.get(stat)
        if not isinstance(blk, dict):
            continue
        base = blk.get("base")
        if not isinstance(base, (int, float)):
            continue
        base = int(base)
        if base <= HIGH_STAT_THRESHOLD:
            continue
        sources = _scan_for_stat_justification(state, stat)
        record = {
            "stat": stat,
            "base_value": base,
            "severity": _high_stat_severity(base),
            "justified": bool(sources),
            "justification_sources": sources,
            "_rule_ref": "dm_rules_tracking.md § RULE 13",
        }
        if not sources:
            record["needs_quirk"] = True
            record["suggested_quirk_template"] = (
                f"{stat} {base} is unjustified by any class feature, racial trait, "
                f"or item. Author a contextual quirk that drops {stat} under 20 in "
                f"a lore-grounded circumstance (environment, terrain, social context, "
                f"item-dependence, etc.) and write it into "
                f"mechanical_state.high_stat_quirks.active[i].quirk_text."
            )
        high.append(record)
    return high


def apply_high_stat_quirks(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect high-stat quirks and write them into mechanical_state.high_stat_quirks.
    Idempotent. Returns change records. Preserves existing `quirk_text` fields
    if present (so author-written quirks survive recompute)."""
    new_records = detect_high_stat_quirks(state)
    ms = state.get("mechanical_state")
    if not isinstance(ms, dict):
        return []
    old_block = ms.get("high_stat_quirks") or {}
    old_records = old_block.get("active") or []

    # Preserve existing author-written `quirk_text` for matching stats.
    existing_text = {r.get("stat"): r.get("quirk_text")
                      for r in old_records
                      if isinstance(r, dict) and r.get("quirk_text")}
    for r in new_records:
        prior = existing_text.get(r["stat"])
        if prior:
            r["quirk_text"] = prior
            r["needs_quirk"] = False

    new_block = {
        "_rule": (
            "Auto-detected by character_compute.detect_high_stat_quirks(). "
            "Cardinal Rule 13 — any base score > 20 must be justified by a "
            "class feature, racial trait, patron gift, or item. Unjustified "
            "high stats need a contextual quirk that drops them under 20 in "
            "defined circumstances. See dm_rules_tracking.md § RULE 13."
        ),
        "active": new_records,
        "count": len(new_records),
        "needs_quirk_count": sum(1 for r in new_records if r.get("needs_quirk")),
    }
    if old_block != new_block:
        ms["high_stat_quirks"] = new_block
        return [{
            "field": "mechanical_state.high_stat_quirks",
            "old": f"{(old_block or {}).get('count', '?')} high stats" if old_block else "(none)",
            "new": f"{len(new_records)} high stats, {new_block['needs_quirk_count']} need quirk(s)",
        }]
    return []


def apply_low_stat_quirks(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect low-stat quirks and write them into mechanical_state.low_stat_quirks.
    Idempotent. Returns change records."""
    quirks = detect_low_stat_quirks(state)
    ms = state.get("mechanical_state")
    if not isinstance(ms, dict):
        return []
    old = ms.get("low_stat_quirks")
    new_block = {
        "_rule": (
            "Auto-detected by character_compute.detect_low_stat_quirks(). "
            "Cardinal Rule 12 — any base score < 10 generates a mandatory quirk "
            "the DM must enforce at the table. See dm_rules_tracking.md § RULE 12."
        ),
        "active": quirks,
        "count": len(quirks),
    }
    if old != new_block:
        ms["low_stat_quirks"] = new_block
        return [{
            "field": "mechanical_state.low_stat_quirks",
            "old": "(none)" if not old else f"{(old or {}).get('count', '?')} quirk(s)",
            "new": f"{len(quirks)} quirk(s): " + ", ".join(
                f"{q['stat']} {q['base_value']} ({q['severity']})" for q in quirks
            ) if quirks else "no quirks (all stats >= 10)",
        }]
    return []


def apply_power_override(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run detect_power_override() and write the result into
    mechanical_state.power_override. Idempotent. Returns change records.
    """
    info = detect_power_override(state)
    ms = state.get("mechanical_state")
    if not isinstance(ms, dict):
        return []
    old = ms.get("power_override")
    new_block = {
        "_rule": (
            "Auto-detected by character_compute.detect_power_override(). "
            "Triggers Rule 11 threat-tier scaling, counter-strategy weighting, "
            "and the honeymoon→escalation curve. See dm_rules_tracking.md § RULE 11."
        ),
        **info,
    }
    if old != new_block:
        ms["power_override"] = new_block
        return [{
            "field": "mechanical_state.power_override",
            "old": old, "new": "{is_override=%s, factor=%s, phase=%s, hours_left=%s}" % (
                info["is_override"], info["override_factor"],
                info["recommended_phase"], info["honeymoon_hours_remaining"],
            ),
        }]
    return []


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

    # 0b. Power-override detection (Cardinal Rule 11). Writes the
    #     `power_override` block into mechanical_state with the override
    #     factor, honeymoon-days-remaining, and recommended escalation phase.
    #     Idempotent — safe to re-run every recompute.
    po_changes = apply_power_override(state)
    report["changes"].extend(po_changes)

    # 0c. Low-stat quirks detection (Cardinal Rule 12). Any base ability
    #     score below 10 generates a mandatory engine-canonical quirk the
    #     DM must enforce at the table.
    lsq_changes = apply_low_stat_quirks(state)
    report["changes"].extend(lsq_changes)

    # 0d. High-stat quirks detection (Cardinal Rule 13). Any base ability
    #     score above 20 must be justified by a class feature, racial trait,
    #     patron gift, or item. If unjustified, a contextual quirk dropping
    #     the stat under 20 is required.
    hsq_changes = apply_high_stat_quirks(state)
    report["changes"].extend(hsq_changes)

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
