#!/usr/bin/env python3
"""Engine Upgrade v2.0 — Goal Audit, Triggers, Escalation, Perk Binding,
EXP Tracking, Economy Validation, Campaign Rules, Chapter Pipeline.

This module extends StoryEngine with the v2.0 systems specified in
engine_upgrade_spec.md. It patches the methods onto StoryEngine at import
time, so any code that imports StoryEngine after importing this module
gets the new capabilities.

Usage:
    import engine_v2  # patches StoryEngine automatically
    from ttrpg_game_engine import StoryEngine
    eng = StoryEngine.load_json("kenji_state.json")
    report = eng.generate_chapter_open_report(chapter=43)
    audit = eng.audit_goals(current_chapter=43)

CLI:
    python engine_v2.py test             # run all v2.0 tests
    python engine_v2.py chapter_open N   # generate chapter-open report for chapter N
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from ttrpg_game_engine import StoryEngine, ACTIVE_CHARACTER_GOAL_STATUSES


# ============================================================
# SAFE TRIGGER EXPRESSION EVALUATOR
# ============================================================

class _AttrDict(dict):
    """Dict that supports dot-access for trigger expressions."""
    def __getattr__(self, key):
        try:
            val = self[key]
            if isinstance(val, dict) and not isinstance(val, _AttrDict):
                return _AttrDict(val)
            return val
        except KeyError:
            return None


def _eval_trigger(self, expr: str, ctx: dict) -> bool:
    """Evaluate a trigger condition string against a context dict.

    Sandboxed: only allows attribute access, comparisons, boolean ops,
    and a small set of function calls. No arbitrary code execution.

    Context keys available:
      character.*  — active PC state fields
      state.*      — engine state fields (day, hour, etc.)
      npc.<name>.* — NPC fields
      goal.*       — goal helper functions

    Examples:
      "character.cover_status == 'OPEN'"
      "state.day >= 300"
      "npc.korrim.disposition >= 5"
      "character.perk_active('bane_of_eve') and state.day > 285"
      "goal.completed('korrim_trade')"
    """
    if not expr or not isinstance(expr, str):
        return False
    expr = expr.strip()
    if not expr:
        return False

    # Basic safety check
    banned = re.compile(r'__|\bimport\b|\bexec\b|\beval\b|\bopen\b|\bos\b|\bsys\b|\bgetattr\b')
    if banned.search(expr):
        return False

    safe_ns = {}
    for key, val in ctx.items():
        safe_ns[key] = val

    try:
        result = eval(expr, {"__builtins__": {}}, safe_ns)
        return bool(result)
    except Exception:
        return False


def _build_trigger_context(self, active_pc: str = None) -> dict:
    """Build the context dict for trigger evaluation from current engine state."""
    # character.* — the active PC's state
    char_ctx = _AttrDict({
        "cover_status": self.extra_json.get("cover_status", "UNKNOWN"),
        "location": self.location,
        "level": self.level,
        "day": self.day,
        "gold": self.gold,
        "hp": self.hp,
        "max_hp": self.max_hp,
        "char_name": self.char_name,
    })
    # perk_active helper
    perk_ids = set()
    for p in self.extra_json.get("perks", []):
        if isinstance(p, dict) and p.get("active"):
            perk_ids.add(p.get("perk_id", ""))
    for p_str in self.active_perks:
        if isinstance(p_str, str):
            perk_ids.add(p_str.lower().split("(")[0].strip().replace(" ", "_").replace("'", ""))
    char_ctx["perk_active"] = lambda pid: pid in perk_ids

    # state.*
    state_ctx = _AttrDict({
        "day": self.day,
        "hour": self.hour,
        "weather": self.weather,
        "location": self.location,
        "golden_age_active": self.golden_age_active,
    })

    # npc.*
    npc_ctx = _AttrDict()
    for npc_name, npc_data in self.npcs.items():
        if isinstance(npc_data, dict):
            npc_ctx[npc_name.lower().replace(" ", "_")] = _AttrDict(npc_data)
    for npc_name, rel_data in self.relationships.items():
        key = npc_name.lower().replace(" ", "_")
        if key not in npc_ctx:
            npc_ctx[key] = _AttrDict(rel_data)
        elif isinstance(rel_data, dict):
            npc_ctx[key].update(rel_data)

    # goal.*
    completed_goals = set()
    for g in self.character_goals:
        if isinstance(g, dict):
            st = (g.get("status") or "").strip().lower()
            if st in ("resolved", "complete", "completed"):
                completed_goals.add(g.get("goal_id", ""))
    goal_ctx = _AttrDict({
        "completed": lambda gid: gid in completed_goals,
    })

    return {
        "character": char_ctx,
        "state": state_ctx,
        "npc": npc_ctx,
        "goal": goal_ctx,
        "active_pc": (active_pc or self.char_name).lower(),
    }


# ============================================================
# GOAL AUDIT SYSTEM (§3 of spec)
# ============================================================

def audit_goals(self, current_chapter: int = None, active_pc: str = None) -> dict:
    """Audit all goals against current state. Returns structured report.

    Returns dict with keys:
      triggered, overdue, due, stale, approaching
    """
    ctx = self._build_trigger_context(active_pc)
    chapter = current_chapter or self.extra_json.get("current_chapter", 0)

    report = {"triggered": [], "overdue": [], "due": [], "stale": [], "approaching": []}

    all_goals = list(self.character_goals)
    # Synthesize perk-as-goal entries
    for perk in self.extra_json.get("perks", []):
        if isinstance(perk, dict) and perk.get("schedule") == "per_chapter":
            all_goals.append({
                "goal_id": perk.get("perk_id", "unknown_perk"),
                "description": f"Perk: {perk.get('perk_name', '?')}",
                "status": "active" if perk.get("active") else "inactive",
                "trigger_condition": perk.get("trigger_condition"),
                "recurrence": "per_chapter",
                "character_bound": perk.get("character_bound"),
                "_is_perk": True,
            })

    for g in all_goals:
        if not isinstance(g, dict):
            continue
        st = (g.get("status") or "").strip().lower()
        if st in ("resolved", "mia", "closed", "closed_overdue", "complete",
                   "completed", "superseded", "failed", "inactive"):
            continue
        if st and st not in ACTIVE_CHARACTER_GOAL_STATUSES and st != "active":
            continue

        gid = g.get("goal_id", "?")
        entry = {
            "goal_id": gid,
            "description": g.get("description") or g.get("summary", ""),
            "character": g.get("character") or g.get("character_bound", "?"),
            "status": st,
        }

        # 1. Check trigger_condition
        tc = g.get("trigger_condition")
        if tc and self._eval_trigger(tc, ctx):
            entry["trigger_met"] = True
            entry["trigger_condition"] = tc
            report["triggered"].append(entry.copy())

        # 2. Check due_chapter
        due_ch = g.get("due_chapter")
        if due_ch is not None and chapter > 0:
            try:
                due_ch_i = int(due_ch)
                if chapter > due_ch_i:
                    overdue_by = chapter - due_ch_i
                    entry["overdue_chapters"] = overdue_by
                    entry["due_chapter"] = due_ch_i
                    if overdue_by >= 5:
                        entry["escalation_tier"] = 3
                        entry["escalation_action"] = "FAILED — on_fail consequence applies"
                    elif overdue_by >= 3:
                        entry["escalation_tier"] = 2
                        entry["escalation_action"] = "NPC autonomous action"
                    else:
                        entry["escalation_tier"] = 1
                        entry["escalation_action"] = "Flagged — DM must acknowledge"
                    report["overdue"].append(entry.copy())
                elif due_ch_i - chapter <= 5:
                    entry["due_chapter"] = due_ch_i
                    entry["chapters_remaining"] = due_ch_i - chapter
                    report["approaching"].append(entry.copy())
            except (TypeError, ValueError):
                pass

        # 3. Check due_day
        due_day = g.get("due_day")
        if due_day is not None:
            try:
                due_day_i = int(due_day)
                if self.day > due_day_i:
                    if "overdue_chapters" not in entry:
                        overdue_days = self.day - due_day_i
                        entry["overdue_days"] = overdue_days
                        entry["due_day"] = due_day_i
                        equiv_ch = overdue_days // 2
                        if equiv_ch >= 5:
                            entry["escalation_tier"] = 3
                            entry["escalation_action"] = "FAILED"
                        elif equiv_ch >= 3:
                            entry["escalation_tier"] = 2
                            entry["escalation_action"] = "NPC autonomous action"
                        elif equiv_ch >= 1:
                            entry["escalation_tier"] = 1
                            entry["escalation_action"] = "Flagged"
                        report["overdue"].append(entry.copy())
                elif due_day_i - self.day <= 10:
                    if "chapters_remaining" not in entry:
                        entry["due_day"] = due_day_i
                        entry["days_remaining"] = due_day_i - self.day
                        report["approaching"].append(entry.copy())
            except (TypeError, ValueError):
                pass

        # 4. Check recurrence
        if g.get("recurrence") == "per_chapter":
            tc2 = g.get("trigger_condition")
            if tc2:
                if self._eval_trigger(tc2, ctx):
                    entry["recurrence"] = "per_chapter"
                    report["due"].append(entry.copy())
            else:
                entry["recurrence"] = "per_chapter"
                report["due"].append(entry.copy())

        # 5. Check staleness
        last_ch = g.get("last_updated_chapter")
        if last_ch is not None and chapter > 0:
            try:
                last_ch_i = int(last_ch)
                if chapter - last_ch_i >= 3:
                    entry["chapters_since_update"] = chapter - last_ch_i
                    report["stale"].append(entry.copy())
            except (TypeError, ValueError):
                pass

    return report


def escalate_goals(self, current_chapter: int = None) -> List[str]:
    """Apply escalation tiers to overdue goals. Returns list of escalation messages."""
    chapter = current_chapter or self.extra_json.get("current_chapter", 0)
    if chapter <= 0:
        return []

    messages = []
    for g in self.character_goals:
        if not isinstance(g, dict):
            continue
        st = (g.get("status") or "").strip().lower()
        if st not in ACTIVE_CHARACTER_GOAL_STATUSES:
            continue
        due_ch = g.get("due_chapter")
        if due_ch is None:
            continue
        try:
            due_ch_i = int(due_ch)
        except (TypeError, ValueError):
            continue
        if chapter <= due_ch_i:
            continue

        overdue = chapter - due_ch_i
        gid = g.get("goal_id", "?")
        char = g.get("character") or g.get("character_bound", "?")
        old_tier = g.get("escalation_tier", 0)

        if overdue >= 5 and old_tier < 3:
            g["escalation_tier"] = 3
            g["status"] = "failed"
            on_fail = g.get("on_fail", "Goal failed — opportunity lost.")
            messages.append(
                f"TIER 3 ESCALATION — {gid} ({overdue} chapters overdue)\n"
                f"  Character: {char}\n"
                f"  GOAL FAILED. Consequence: {on_fail}"
            )
            if g.get("on_fail"):
                self.consequences.append({
                    "trigger_day": self.day,
                    "cause": f"Goal '{gid}' failed (Tier 3 escalation)",
                    "effect": g["on_fail"],
                    "fired": False,
                })
        elif overdue >= 3 and old_tier < 2:
            g["escalation_tier"] = 2
            npc = g.get("attached_npc") or char
            desc = g.get("description") or g.get("summary", "")
            messages.append(
                f"TIER 2 ESCALATION — {gid} ({overdue} chapters overdue)\n"
                f"  NPC: {npc}\n"
                f"  Action: {npc} takes autonomous action regarding: {desc}"
            )
        elif overdue >= 1 and old_tier < 1:
            g["escalation_tier"] = 1
            messages.append(
                f"TIER 1 ESCALATION — {gid} ({overdue} chapters overdue)\n"
                f"  Character: {char}\n"
                f"  Flagged for DM acknowledgment."
            )
    return messages


# ============================================================
# PERK BINDING + NPC VISIBILITY (§6 of spec)
# ============================================================

def check_perks(self, active_pc: str = None) -> List[dict]:
    """Check all perks for the current chapter. Returns list of perk event dicts."""
    pc = (active_pc or self.char_name).lower()
    ctx = self._build_trigger_context(active_pc)
    events = []

    for perk in self.extra_json.get("perks", []):
        if not isinstance(perk, dict) or not perk.get("active"):
            continue
        perk_id = perk.get("perk_id", "?")
        perk_name = perk.get("perk_name", "?")
        char_bound = (perk.get("character_bound") or "").lower()
        schedule = perk.get("schedule", "")
        tc = perk.get("trigger_condition")

        trigger_met = True
        if tc:
            trigger_met = self._eval_trigger(tc, ctx)
        if not trigger_met:
            continue

        event = {
            "perk_id": perk_id,
            "perk_name": perk_name,
            "character_bound": perk.get("character_bound", "?"),
            "schedule": schedule,
        }
        if char_bound == pc:
            if schedule == "per_chapter":
                event["event_type"] = "player_encounter"
                event["description"] = f"PERK DUE: {perk_name} — run as player encounter"
            elif schedule == "dm_initiated":
                event["event_type"] = "dm_option"
                event["description"] = f"PERK AVAILABLE: {perk_name} — DM may initiate"
            events.append(event)
        else:
            if perk.get("visible_to_others"):
                event["event_type"] = "npc_visible"
                event["description"] = f"NPC PERK EVENT: {perk.get('character_bound', '?')} — {perk_name}"
                event["visibility_description"] = perk.get("visibility_description", "")
                event["npc_observation_hook"] = perk.get("npc_observation_hook", "")
            else:
                event["event_type"] = "npc_silent"
                event["description"] = f"(background) {perk.get('character_bound', '?')} — {perk_name} fired silently"
            events.append(event)
    return events


# ============================================================
# EXP TRACKING (§7 of spec)
# ============================================================

def update_exp(self, chapter: int, combat: int = 0, roleplay: int = 0,
               discovery: int = 0, justification: str = "") -> dict:
    """Update EXP from a chapter receipt. Logs to exp_history."""
    total = combat + roleplay + discovery
    if "exp_history" not in self.extra_json:
        self.extra_json["exp_history"] = []

    entry = {
        "chapter": chapter,
        "amount": total,
        "breakdown": {"combat": combat, "roleplay": roleplay, "discovery": discovery},
        "justification": justification,
    }
    self.extra_json["exp_history"].append(entry)

    old_exp = self.exp
    self.exp += total

    # Check consecutive zero-EXP streak
    history = self.extra_json["exp_history"]
    zero_streak = 0
    for h in reversed(history):
        if h.get("amount", 0) == 0:
            zero_streak += 1
        else:
            break

    result = {
        "old_exp": old_exp,
        "new_exp": self.exp,
        "gained": total,
        "breakdown": {"combat": combat, "roleplay": roleplay, "discovery": discovery},
        "level_up": False,
        "zero_streak_warning": zero_streak >= 3,
        "zero_streak": zero_streak,
    }
    if zero_streak >= 3:
        result["warning"] = f"No EXP awarded in {zero_streak} consecutive chapters. Intentional?"
    return result


# ============================================================
# ECONOMY VALIDATION (§8 of spec)
# ============================================================

PRICE_TABLE = {
    "meal_common": {"cost_cp": 3, "note": "Bread, stew, ale"},
    "meal_fine": {"cost_sp": 2, "note": "Roast, wine, dessert"},
    "room_common": {"cost_cp": 5, "note": "Shared room, one night"},
    "room_private": {"cost_sp": 2, "note": "Private room, one night"},
    "horse": {"cost_gp": 15, "note": "Riding horse, not war-trained"},
    "sword_common": {"cost_gp": 3, "note": "Functional steel, not enchanted"},
    "healing_potion": {"cost_gp": 10, "note": "Standard restoration"},
    "nyx_elixir_black_market": {"cost_gp": 100, "note": "100-500 GP, varies"},
    "hired_guard_per_day": {"cost_sp": 2, "note": "Competent, not elite"},
    "mercenary_per_day": {"cost_gp": 1, "note": "Professional, combat-ready"},
    "passage_ship": {"cost_gp": 5, "note": "Coastal, one-way"},
    "passage_portal": {"cost_gp": 1, "note": "Coalition portal network"},
}


def validate_economy(self, gold_gained: int = 0, gold_spent: int = 0,
                     notes: str = "") -> dict:
    """Validate gold changes from a chapter receipt."""
    result = {
        "valid": True,
        "warnings": [],
        "gold_before": self.gold,
        "gold_after": self.gold + gold_gained - gold_spent,
        "net_change": gold_gained - gold_spent,
    }
    if gold_spent > 0 and not notes:
        result["warnings"].append("Gold spent but no notes — what was it spent on?")
    if result["gold_after"] < 0:
        result["warnings"].append(f"Character would be broke ({result['gold_after']} GP).")
    if result["warnings"]:
        result["valid"] = False
    return result


# ============================================================
# CAMPAIGN-SPECIFIC RULES (§9 of spec)
# ============================================================

def apply_campaign_rules(self, report: dict, active_pc: str = None) -> dict:
    """Filter a chapter-open report through campaign-specific rules."""
    pc = (active_pc or self.char_name).lower()
    rules = self.extra_json.get("campaign_rules", [])

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = rule.get("rule_id", "")

        if rule_id == "invisible_to_kenji" and "kenji" in pc:
            cult_keywords = {"cult", "anku", "conspiracy", "ankuspawn", "harvesting",
                             "academy_prisoner", "nyx_operation"}
            for category in ("triggered", "overdue", "due", "stale", "approaching"):
                if category in report:
                    report[category] = [
                        item for item in report[category]
                        if not any(kw in (item.get("goal_id", "") + item.get("description", "")).lower()
                                  for kw in cult_keywords)
                    ]

        elif rule_id == "cult_visibility_non_kenji" and "kenji" not in pc:
            if "ambient_events" not in report:
                report["ambient_events"] = []
            report["ambient_events"].append(
                "Tavern rumor: 'Have you heard about those elixirs from the Academy? "
                "Strength of a hundred men, they say...'"
            )
            report["ambient_events"].append(
                "Notice board: Missing persons — several young adults, "
                "distinctive features, last seen traveling toward Ashenveil."
            )
    return report


# ============================================================
# CHAPTER-OPEN REPORT GENERATOR (§2 of spec)
# ============================================================

def generate_chapter_open_report(self, current_chapter: int = None,
                                 active_pc: str = None) -> str:
    """Generate the mandatory pre-chapter report. AI reads this BEFORE writing any scene."""
    chapter = current_chapter or self.extra_json.get("current_chapter", 0)
    pc = active_pc or self.char_name

    lines = ["=== CHAPTER OPEN REPORT ==="]
    lines.append(f"Current Day: {self.day} | Location: {self.location} | "
                 f"Cover: {self.extra_json.get('cover_status', 'UNKNOWN')}")
    lines.append("")

    audit = self.audit_goals(chapter, pc)
    escalation_msgs = self.escalate_goals(chapter)
    perk_events = self.check_perks(pc)
    audit = self.apply_campaign_rules(audit, pc)

    if audit["triggered"]:
        lines.append("--- TRIGGERED GOALS (conditions met) ---")
        for item in audit["triggered"]:
            tc = item.get("trigger_condition", "")
            lines.append(f"[!] {item['goal_id']}: {item['description']}"
                        f"{f' (trigger: {tc})' if tc else ''}")
        lines.append("")

    if audit["overdue"]:
        lines.append("--- OVERDUE GOALS (past due date) ---")
        for item in audit["overdue"]:
            tier = item.get("escalation_tier", 0)
            tier_label = {1: "TIER 1 — DM must acknowledge",
                          2: "TIER 2 — NPC autonomous action",
                          3: "TIER 3 — Goal FAILED"}.get(tier, "")
            if "overdue_chapters" in item:
                info = f"Was due Ch{item['due_chapter']}, now Ch{chapter}."
            elif "overdue_days" in item:
                info = f"Was due Day {item['due_day']}, now Day {self.day}."
            else:
                info = ""
            lines.append(f"[!!] {item['goal_id']}: {info} {tier_label}")
        lines.append("")

    if escalation_msgs:
        lines.append("--- ESCALATION EVENTS ---")
        for msg in escalation_msgs:
            lines.append(msg)
        lines.append("")

    if perk_events:
        lines.append("--- SCHEDULED PERK EVENTS ---")
        for ev in perk_events:
            prefix = f"[{ev.get('character_bound', '?')}]"
            lines.append(f"{prefix} {ev['description']}")
            if ev.get("visibility_description"):
                lines.append(f"  VISIBLE: {ev['visibility_description']}")
            if ev.get("npc_observation_hook"):
                lines.append(f"  OBSERVATION HOOK: {ev['npc_observation_hook']}")
        lines.append("")

    if audit["due"]:
        lines.append("--- DUE THIS CHAPTER ---")
        for item in audit["due"]:
            lines.append(f"[*] {item['goal_id']}: {item['description']}")
        lines.append("")

    if audit["approaching"]:
        lines.append("--- APPROACHING DEADLINES ---")
        for item in audit["approaching"]:
            if "chapters_remaining" in item:
                lines.append(f"[~] {item['goal_id']}: Due Ch{item['due_chapter']} "
                            f"({item['chapters_remaining']} chapters remaining)")
            elif "days_remaining" in item:
                lines.append(f"[~] {item['goal_id']}: Due Day {item['due_day']} "
                            f"({item['days_remaining']} days remaining)")
        lines.append("")

    if audit["stale"]:
        lines.append("--- STALE GOALS (no update in 3+ chapters) ---")
        for item in audit["stale"]:
            lines.append(f"[?] {item['goal_id']}: Last updated "
                        f"{item.get('chapters_since_update', '?')} chapters ago. Review.")
        lines.append("")

    if audit.get("ambient_events"):
        lines.append("--- AMBIENT WORLD EVENTS ---")
        for ev in audit["ambient_events"]:
            lines.append(f"  {ev}")
        lines.append("")

    # NPC Lifecycle — Extra/Promoted audit
    extras_audit = self.audit_extras(chapter)
    if extras_audit["summary_lines"]:
        lines.append("--- NPC LIFECYCLE (Extras & Promoted) ---")
        lines.append(f"Active promoted NPCs: {extras_audit['promoted_active']}")
        for el in extras_audit["summary_lines"]:
            lines.append(el)
        lines.append("")

    history = self.extra_json.get("exp_history", [])
    if history:
        last = history[-1]
        lines.append("--- EXP STATUS ---")
        lines.append(f"Last chapter ({last.get('chapter', '?')}): "
                    f"+{last.get('amount', 0)} EXP — {last.get('justification', '')}")
        zero_streak = 0
        for h in reversed(history):
            if h.get("amount", 0) == 0:
                zero_streak += 1
            else:
                break
        if zero_streak >= 3:
            lines.append(f"[!!] WARNING: No EXP in {zero_streak} consecutive chapters!")
        lines.append(f"Total EXP: {self.exp:,}")
        lines.append("")

    lines.append("=== END REPORT ===")
    return "\n".join(lines)


# ============================================================
# NPC LIFECYCLE — EXTRA / PROMOTED / EXIT
# ============================================================

def audit_extras(self, current_chapter: int = None) -> dict:
    """Audit the extra_npcs array for doom clock warnings and promotion candidates.

    Returns dict with keys:
        promoted_due: list of promoted NPCs whose doom clock is due this chapter
        promoted_approaching: list of promoted NPCs approaching deadline
        overstayed_extras: list of extras that have appeared 3+ chapters without promotion
        promoted_active: count of currently active promoted NPCs
        summary_lines: list of formatted strings for the chapter-open report
    """
    chapter = current_chapter or self.extra_json.get("current_chapter", 0)
    extras = self.extra_json.get("extra_npcs", [])

    promoted_due = []
    promoted_approaching = []
    overstayed = []
    active_promoted = 0
    lines = []

    for npc in extras:
        status = npc.get("status", "active")
        if status != "active":
            continue

        tier = npc.get("tier", "extra")
        name = npc.get("name", "[unnamed]")
        intro_ch = npc.get("introduced_chapter", 0)

        if tier == "promoted":
            active_promoted += 1
            doom = npc.get("doom_clock", {})
            deadline = doom.get("deadline_chapter")
            if deadline is None:
                lines.append(f"[!] PROMOTED NPC '{name}' has NO doom clock deadline — fix immediately")
                continue

            remaining = deadline - chapter
            warning_stage = doom.get("warning_stage", "early")

            if remaining <= 0:
                promoted_due.append({
                    "name": name,
                    "goal": doom.get("goal", ""),
                    "deadline_chapter": deadline,
                    "overdue_by": abs(remaining),
                })
                # Auto-update warning stage
                doom["warning_stage"] = "due"
                lines.append(
                    f"[!!!] DOOM CLOCK DUE: '{name}' — {doom.get('goal', '?')[:80]}. "
                    f"Consequence MUST happen this chapter. NPC exits tracking."
                )
            elif remaining <= 2:
                promoted_approaching.append({
                    "name": name,
                    "goal": doom.get("goal", ""),
                    "deadline_chapter": deadline,
                    "chapters_remaining": remaining,
                })
                # Auto-advance warning stage
                if warning_stage in ("early", "mid"):
                    doom["warning_stage"] = "late"
                lines.append(
                    f"[!!] DOOM CLOCK LATE: '{name}' — {remaining} chapter(s) left. "
                    f"Dialogue MUST show desperation. Goal: {doom.get('goal', '?')[:60]}"
                )
            elif remaining <= 5:
                if warning_stage == "early":
                    doom["warning_stage"] = "mid"
                lines.append(
                    f"[~] DOOM CLOCK MID: '{name}' — {remaining} chapters left. "
                    f"Dialogue should show worry."
                )

        elif tier == "extra":
            # Check for overstayed extras (3+ chapters since introduction)
            chapters_present = chapter - intro_ch if intro_ch > 0 else 0
            if chapters_present >= 3:
                overstayed.append({
                    "name": name,
                    "introduced_chapter": intro_ch,
                    "chapters_present": chapters_present,
                })
                lines.append(
                    f"[?] EXTRA '{name}' has been around {chapters_present} chapters. "
                    f"PROMOTE (add doom clock) or FADE (remove from scenes)."
                )

    return {
        "promoted_due": promoted_due,
        "promoted_approaching": promoted_approaching,
        "overstayed_extras": overstayed,
        "promoted_active": active_promoted,
        "summary_lines": lines,
    }


# ============================================================
# PATCH StoryEngine — attach all v2.0 methods
# ============================================================

StoryEngine._eval_trigger = _eval_trigger
StoryEngine._build_trigger_context = _build_trigger_context
StoryEngine.audit_goals = audit_goals
StoryEngine.escalate_goals = escalate_goals
StoryEngine.check_perks = check_perks
StoryEngine.update_exp = update_exp
StoryEngine.validate_economy = validate_economy
StoryEngine.apply_campaign_rules = apply_campaign_rules
StoryEngine.generate_chapter_open_report = generate_chapter_open_report
StoryEngine.audit_extras = audit_extras
StoryEngine.PRICE_TABLE = PRICE_TABLE


# ============================================================
# CLI + TESTS
# ============================================================

def _run_v2_tests():
    """Self-test for all v2.0 engine features."""
    import json

    state_file = SCRIPT_DIR / "kenji_state.json"
    if not state_file.exists():
        print("ERROR: kenji_state.json not found")
        return False

    eng = StoryEngine.load_json(str(state_file))
    print(f"Loaded: {eng.char_name}, Day {eng.day}, Level {eng.level}")
    print(f"Goals: {len(eng.character_goals)}, Active perks: {len(eng.active_perks)}")
    print()

    # Test 1: Trigger context
    print("=== TEST 1: Trigger Context ===")
    ctx = eng._build_trigger_context("kenji")
    assert ctx["character"]["location"] == eng.location
    assert ctx["state"]["day"] == eng.day
    assert ctx["active_pc"] == "kenji"
    print(f"  character.location = {ctx['character']['location']}")
    print(f"  state.day = {ctx['state']['day']}")
    print("  PASS")
    print()

    # Test 2: Trigger evaluation
    print("=== TEST 2: Trigger Evaluation ===")
    assert eng._eval_trigger("state.day >= 250", ctx) == True
    assert eng._eval_trigger("state.day >= 9999", ctx) == False
    assert eng._eval_trigger("active_pc == 'kenji'", ctx) == True
    assert eng._eval_trigger("active_pc == 'amaris'", ctx) == False
    assert eng._eval_trigger("", ctx) == False
    assert eng._eval_trigger("__import__('os')", ctx) == False  # safety
    print("  All trigger evals correct")
    print("  PASS")
    print()

    # Test 3: Goal audit
    print("=== TEST 3: Goal Audit ===")
    audit = eng.audit_goals(current_chapter=43, active_pc="kenji")
    print(f"  Triggered: {len(audit['triggered'])}")
    print(f"  Overdue: {len(audit['overdue'])}")
    print(f"  Due: {len(audit['due'])}")
    print(f"  Stale: {len(audit['stale'])}")
    print(f"  Approaching: {len(audit['approaching'])}")
    # We should have overdue goals (the current goals have due_day < current engine day)
    assert isinstance(audit["overdue"], list)
    assert isinstance(audit["triggered"], list)
    for item in audit["overdue"][:2]:
        print(f"    OVERDUE: {item['goal_id']} - tier {item.get('escalation_tier', '?')}")
    for item in audit["approaching"][:2]:
        remain = item.get("days_remaining") or item.get("chapters_remaining", "?")
        print(f"    APPROACHING: {item['goal_id']} - {remain} remaining")
    print("  PASS")
    print()

    # Test 4: EXP tracking
    print("=== TEST 4: EXP Tracking ===")
    old_exp = eng.exp
    result = eng.update_exp(99, combat=100, roleplay=200, discovery=50, justification="test")
    assert result["gained"] == 350
    assert result["new_exp"] == old_exp + 350
    assert len(eng.extra_json.get("exp_history", [])) >= 1
    # Restore
    eng.exp = old_exp
    eng.extra_json["exp_history"].pop()
    print(f"  Gained: {result['gained']}, Old: {result['old_exp']}, New: {result['new_exp']}")
    print("  PASS")
    print()

    # Test 5: Economy validation
    print("=== TEST 5: Economy Validation ===")
    econ = eng.validate_economy(gold_gained=50, gold_spent=12, notes="Bought supplies")
    assert econ["valid"] == True
    econ2 = eng.validate_economy(gold_gained=0, gold_spent=999999, notes="")
    assert econ2["valid"] == False
    assert len(econ2["warnings"]) >= 1
    print(f"  Valid transaction: {econ['valid']}")
    print(f"  Invalid transaction warnings: {econ2['warnings']}")
    print("  PASS")
    print()

    # Test 6: Perk check (empty perks array is OK)
    print("=== TEST 6: Perk Check ===")
    events = eng.check_perks("kenji")
    print(f"  Perk events: {len(events)}")
    for ev in events[:3]:
        print(f"    {ev['perk_id']}: {ev['event_type']}")
    print("  PASS")
    print()

    # Test 7: Campaign rules
    print("=== TEST 7: Campaign Rules ===")
    test_report = {
        "triggered": [{"goal_id": "cult_operation", "description": "Cult of Anku active"}],
        "overdue": [],
        "due": [],
        "stale": [],
        "approaching": [],
    }
    # With Kenji as PC + invisible rule
    eng.extra_json["campaign_rules"] = [
        {"rule_id": "invisible_to_kenji", "applies_when": "active_pc == 'kenji'"},
    ]
    filtered = eng.apply_campaign_rules(dict(test_report), "kenji")
    assert len(filtered["triggered"]) == 0, "Cult should be invisible to Kenji"
    filtered2 = eng.apply_campaign_rules(dict(test_report), "amaris")
    assert len(filtered2["triggered"]) == 1, "Cult should be visible to non-Kenji"
    eng.extra_json.pop("campaign_rules", None)
    print("  Kenji sees 0 cult goals (invisible)")
    print("  Amaris sees 1 cult goal (visible)")
    print("  PASS")
    print()

    # Test 8: Chapter-open report
    print("=== TEST 8: Chapter-Open Report ===")
    report = eng.generate_chapter_open_report(current_chapter=43, active_pc="kenji")
    assert "=== CHAPTER OPEN REPORT ===" in report
    assert "=== END REPORT ===" in report
    lines = report.split("\n")
    print(f"  Report generated: {len(lines)} lines")
    # Print first 10 and last 5 lines
    for line in lines[:10]:
        print(f"    {line}")
    print("    ...")
    for line in lines[-5:]:
        print(f"    {line}")
    print("  PASS")
    print()

    # Test 9: NPC Lifecycle — audit_extras
    print("=== TEST 9: NPC Lifecycle (audit_extras) ===")
    # Inject test extra_npcs data
    old_extras = eng.extra_json.get("extra_npcs", [])
    eng.extra_json["extra_npcs"] = [
        {
            "name": "Greta the Bartender",
            "tier": "promoted",
            "introduced_chapter": 38,
            "promotion_chapter": 40,
            "status": "active",
            "doom_clock": {
                "goal": "Owes money to the antagonist's lieutenant",
                "deadline_chapter": 43,
                "warning_stage": "mid",
            },
        },
        {
            "name": "Old Tom",
            "tier": "extra",
            "introduced_chapter": 39,
            "status": "active",
            "doom_clock": {},
        },
        {
            "name": "Resolved Merchant",
            "tier": "promoted",
            "introduced_chapter": 35,
            "promotion_chapter": 37,
            "status": "resolved_dead",
            "doom_clock": {"goal": "Was caught", "deadline_chapter": 41},
        },
    ]
    ea = eng.audit_extras(current_chapter=43)
    assert len(ea["promoted_due"]) == 1, f"Expected 1 due, got {len(ea['promoted_due'])}"
    assert ea["promoted_due"][0]["name"] == "Greta the Bartender"
    assert ea["promoted_active"] == 1  # only Greta is active promoted (Resolved Merchant is dead)
    assert len(ea["overstayed_extras"]) == 1, f"Expected 1 overstayed, got {len(ea['overstayed_extras'])}"
    assert ea["overstayed_extras"][0]["name"] == "Old Tom"
    assert len(ea["summary_lines"]) >= 2
    print(f"  Promoted due: {[n['name'] for n in ea['promoted_due']]}")
    print(f"  Overstayed extras: {[n['name'] for n in ea['overstayed_extras']]}")
    print(f"  Active promoted count: {ea['promoted_active']}")
    print(f"  Summary lines: {len(ea['summary_lines'])}")
    for sl in ea["summary_lines"]:
        print(f"    {sl}")
    # Restore
    eng.extra_json["extra_npcs"] = old_extras
    print("  PASS")
    print()

    print("=" * 50)
    print("ALL v2.0 TESTS PASSED")
    print("=" * 50)
    return True


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "test":
        _run_v2_tests()
    elif args[0] == "chapter_open":
        chapter = int(args[1]) if len(args) > 1 else 0
        eng = StoryEngine.load_json(str(SCRIPT_DIR / "kenji_state.json"))
        if chapter <= 0:
            chapter = eng.extra_json.get("current_chapter", 0)
        if chapter <= 0:
            print("Usage: python engine_v2.py chapter_open <chapter_number>")
            sys.exit(1)
        pc = args[2] if len(args) > 2 else eng.char_name
        report = eng.generate_chapter_open_report(chapter, pc)
        print(report)
        # Write to file
        out = SCRIPT_DIR / "CHAPTER_OPEN_REPORT.md"
        out.write_text(f"<!-- Generated by engine_v2.py -->\n\n{report}\n", encoding="utf-8")
        print(f"\n[Wrote {out.name}]")
    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: python engine_v2.py [test|chapter_open N]")
