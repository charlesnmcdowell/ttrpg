"""
trigger_engine.py — structured-trigger lookup and dispatch.

WHY THIS EXISTS:
The campaign's perks and Ember enhancements were previously encoded as English
prose inside `mechanical_state.class_features[].mechanical_effect` strings.
Programs cannot act on prose; the DM had to remember every trigger and apply
it manually. That dependency failed (e.g., DDR-Ember charm during Dispel Dance
went unrolled because the AI didn't re-read the prose at action-time).

The fix: every game-mechanical trigger lives as STRUCTURED DATA in
`mechanical_state.triggers[]`. Programs match on `fires_on` event names and
`condition` constraints. The DM (or the engine) calls into this module with
an action context, gets back a list of triggers that should fire, and rolls
the dice deterministically.

The class_features prose remains for narrative flavor, but is no longer the
source of truth for mechanics.

USAGE:
    from trigger_engine import get_active_triggers, fire_trigger
    triggers = get_active_triggers(state, fires_on="round_tick_during_cast",
                                    context={"caster_action_class": "dance_ability",
                                             "caster_action_state": "casting",
                                             "ember_active": True})
    for t in triggers:
        result = fire_trigger(t, scene_context={"enemies_in_range_30": [...]})
        # result tells the DM what was rolled and what to apply

This module deliberately performs ZERO narrative interpretation. Output is
structured: dice rolls, target IDs, applied statuses, save DCs. Narrative
prose is for the DM/AI layer to wrap around the result, never to substitute
for it.
"""

from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Schema check — ensures triggers list is in expected shape
# ---------------------------------------------------------------------------

REQUIRED_TRIGGER_FIELDS = {"id", "name", "source", "fires_on",
                           "condition", "effect", "active_at_levels"}


def validate_trigger(t: dict) -> list:
    """Return a list of validation errors (empty list = valid)."""
    errors = []
    missing = REQUIRED_TRIGGER_FIELDS - set(t.keys())
    if missing:
        errors.append(f"trigger {t.get('id', '<?>')} missing fields: {sorted(missing)}")
    if not isinstance(t.get("active_at_levels"), list):
        errors.append(f"trigger {t.get('id')}: active_at_levels must be a list")
    if not isinstance(t.get("condition"), dict):
        errors.append(f"trigger {t.get('id')}: condition must be a dict")
    if not isinstance(t.get("effect"), dict):
        errors.append(f"trigger {t.get('id')}: effect must be a dict")
    return errors


def load_triggers(state_file: Path) -> list:
    """Load and validate all triggers from a character_world_state.json file."""
    data = json.loads(Path(state_file).read_text(encoding="utf-8"))
    triggers = data.get("mechanical_state", {}).get("triggers", [])
    if not isinstance(triggers, list):
        return []
    valid = []
    for t in triggers:
        errs = validate_trigger(t)
        if errs:
            print(f"[trigger_engine] schema warnings: {errs}")
            continue
        valid.append(t)
    return valid


# ---------------------------------------------------------------------------
# Lookup — match triggers against a fires_on event + context
# ---------------------------------------------------------------------------

def _condition_matches(condition: dict, context: dict) -> bool:
    """Return True if every key in `condition` matches the corresponding
    value in `context`. Missing keys in context fail the match (strict)."""
    for k, expected in condition.items():
        if k not in context:
            return False
        actual = context[k]
        if expected != actual:
            return False
    return True


def get_active_triggers(state_file: Path, fires_on: str, context: dict,
                        character_level: int = None) -> list:
    """Return the list of triggers from `state_file` that match the given
    fires_on event and context dictionary.

    Triggers are filtered by:
      1. fires_on event name exact match
      2. character_level within active_at_levels (or character_level None = pass)
      3. all condition keys present in context with matching values
    """
    triggers = load_triggers(state_file)
    matching = []
    for t in triggers:
        if t.get("fires_on") != fires_on:
            continue
        if character_level is not None:
            levels = t.get("active_at_levels", [])
            if character_level not in levels:
                continue
        if not _condition_matches(t.get("condition", {}), context):
            continue
        matching.append(t)
    return matching


# ---------------------------------------------------------------------------
# Dispatch — execute a trigger's effect against scene context
# ---------------------------------------------------------------------------

def _roll(roll_spec: dict) -> int:
    """Roll a die per the spec. Spec keys: die ('d20', 'd100', etc.)."""
    die = roll_spec.get("die", "d20")
    sides = int(die.lstrip("d"))
    return random.randint(1, sides)


def fire_trigger(trigger: dict, scene_context: dict) -> dict:
    """Execute a trigger's effect against the given scene context.

    Returns a structured result dict reporting what was rolled and what
    statuses/effects should be applied. The DM/engine uses this result to
    update game state — this function does NOT mutate state directly.

    For per_target_roll effects, scene_context must provide a list of
    candidate targets matching the target_filter; a roll is made per target
    and the result includes a list of {target_id, roll, passed, effect}.
    """
    effect = trigger.get("effect", {})
    kind = effect.get("kind")
    result = {
        "trigger_id": trigger["id"],
        "trigger_name": trigger.get("name"),
        "kind": kind,
        "rolls": [],
        "applied": [],
    }

    if kind == "override_save_stat":
        result["use_stat"] = effect.get("use_stat")
        result["narrative"] = (
            f"Concentration save uses {effect.get('use_stat')} instead of CON."
        )
        return result

    if kind == "per_target_roll":
        target_filter = effect.get("target_filter", {})
        targets = scene_context.get("candidate_targets", [])
        # Filter targets by the filter spec (caller is expected to have
        # pre-filtered, but we double-check humanoid/in_range_ft if present).
        filtered = []
        for tgt in targets:
            if "humanoid" in target_filter and target_filter["humanoid"]:
                if not tgt.get("humanoid", False):
                    continue
            if "in_range_ft" in target_filter:
                if tgt.get("range_ft", 999) > target_filter["in_range_ft"]:
                    continue
            if "side" in target_filter:
                if tgt.get("side") != target_filter["side"]:
                    continue
            filtered.append(tgt)
        roll_spec = effect.get("roll", {})
        threshold = roll_spec.get("threshold", 0)
        op = roll_spec.get("operator", "<=")
        for tgt in filtered:
            r = _roll(roll_spec)
            if op == "<=":
                passed = r <= threshold
            elif op == ">=":
                passed = r >= threshold
            elif op == "<":
                passed = r < threshold
            elif op == ">":
                passed = r > threshold
            else:
                passed = r == threshold
            applied = effect.get("on_pass", {}) if passed else effect.get("on_fail", {})
            result["rolls"].append({
                "target_id": tgt.get("id"),
                "target_label": tgt.get("label"),
                "roll": r,
                "threshold": threshold,
                "operator": op,
                "passed": passed,
                "applied": applied,
            })
        return result

    if kind == "compound":
        sub_effects = effect.get("effects", [])
        result["sub_effects"] = []
        for sub in sub_effects:
            sub_trigger = dict(trigger)
            sub_trigger["effect"] = sub
            sub_result = fire_trigger(sub_trigger, scene_context)
            result["sub_effects"].append(sub_result)
        return result

    if kind == "constrain_action":
        # Behavior modifier — engine returns the constraint set; the DM applies
        # it to the enemy's action selection logic.
        result["constraint"] = effect
        result["narrative"] = (
            "Behavior constraint set on humanoid enemy actions per gender + disposition rules."
        )
        return result

    # Unknown effect kind — return the raw effect for the DM to interpret.
    result["raw_effect"] = effect
    result["narrative"] = "Unknown effect kind; raw structure returned for DM interpretation."
    return result


# ---------------------------------------------------------------------------
# CLI for smoke testing
# ---------------------------------------------------------------------------

def _cli_demo(state_file_path: str, character_level: int = 10) -> None:
    """Demo: list triggers that would fire during a dance ability cast."""
    state_file = Path(state_file_path)
    print("=" * 64)
    print(f"trigger_engine smoke test — {state_file.name} (level {character_level})")
    print("=" * 64)

    # Test 1: round_tick_during_cast for a dance ability
    triggers = get_active_triggers(
        state_file,
        fires_on="round_tick_during_cast",
        context={
            "caster_action_class": "dance_ability",
            "caster_action_state": "casting",
            "ember_active": True,
        },
        character_level=character_level,
    )
    print(f"\nMatching triggers for 'round_tick_during_cast' (dance, casting, ember on):")
    for t in triggers:
        print(f"  - {t['id']}: {t['name']}")

    # Test 2: fire one of them (simulate the DDR Ember charm) against 2 enemies
    if triggers:
        t = next((x for x in triggers
                  if x["id"] == "ddr_ember_charm_during_dance_cast"), None)
        if t:
            print(f"\nFiring trigger: {t['id']}")
            scene = {
                "candidate_targets": [
                    {"id": "performer_thrall", "label": "Charmed performer (past pillar)",
                     "humanoid": True, "side": "enemy", "range_ft": 25},
                    {"id": "eira_hidden",      "label": "Eira (recruiter, hidden)",
                     "humanoid": True, "side": "enemy", "range_ft": 28},
                ]
            }
            result = fire_trigger(t, scene)
            print(f"  rolls fired: {len(result['rolls'])}")
            for r in result["rolls"]:
                outcome = "CHARMED -> targets allies" if r["passed"] else "RESISTED"
                print(f"    target={r['target_label']:<48s} roll={r['roll']:>3d} "
                      f"(<= {r['threshold']}) → {outcome}")

    # Test 3: concentration save during dance ability
    triggers = get_active_triggers(
        state_file,
        fires_on="concentration_save",
        context={"caster_action_class": "dance_ability"},
        character_level=character_level,
    )
    print(f"\nMatching triggers for 'concentration_save' (dance ability):")
    for t in triggers:
        print(f"  - {t['id']}: {t['name']}")
        result = fire_trigger(t, {})
        print(f"    -> {result.get('narrative')}")


if __name__ == "__main__":
    import sys
    state_file = sys.argv[1] if len(sys.argv) > 1 else (
        "/sessions/kind-awesome-heisenberg/mnt/TTRPG/Cookie/Game init files/character_world_state.json"
    )
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    _cli_demo(state_file, level)
