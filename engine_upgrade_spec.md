# Engine Upgrade Spec — v2.0

**Purpose:** Formalize the chapter pipeline, fix goal/trigger/perk failures from Book 4, and reduce AI manual bookkeeping to near-zero. The AI tells stories and extracts variables. The engine does math, updates files, and enforces world rules.

**Builds on:** `ttrpg_game_engine.py`, `_dm_turn.py`, `continuity_engine.py`, `chapter_close.py`

---

## 1. The Three-Prompt Chapter Pipeline

The entire chapter lifecycle runs on three prompts with clean separation of concerns.

### Prompt 1 — Play the Chapter

**Who:** AI (storytelling mode)
**Input:** AI_CONTEXT.md brief + chapter-open report from engine (see §2)
**Output:** Chapter prose + structured chapter receipt (see §1.1)
**Rules:**
- AI reads the chapter-open report FIRST — triggered goals, overdue alerts, scheduled perk events
- AI must address all fired triggers and overdue goals in the chapter (or explicitly defer with logged reason)
- AI writes the scene, responds to the player, rolls via engine when needed
- When the chapter reaches its natural end, AI outputs: "Chapter closed. Time to update trackers."
- AI also outputs a structured **chapter receipt** (see below)

### 1.1 Chapter Receipt Format (AI → Engine)

The AI outputs this at chapter end. Standardized fields, no ambiguity. The engine parses it directly.

```yaml
chapter_receipt:
  chapter_number: 43
  day_start: 291
  day_end: 292
  hours_elapsed: 18
  location_end: "Varenholm"
  
  exp_earned:
    combat: 0
    roleplay: 1500
    discovery: 300
    total: 1800
    justification: "Negotiated Korrim trade agreement, discovered Ashenveil elixir rumor"
  
  gold_changes:
    gained: 50
    spent: 12
    net: 38
    notes: "Payment for escort job, bought supplies"
  
  hp_changes:
    damage_taken: 0
    healing_received: 0
    current_hp: 6288
  
  goals_progressed:
    - goal_id: "pip_missing_child"
      old_status: "active"
      new_status: "active"
      progress_note: "Heard rumor at tavern about missing Ankuspawn"
    - goal_id: "korrim_trade"
      old_status: "active"
      new_status: "resolved"
      progress_note: "Agreement signed"
  
  goals_new:
    - goal_id: "investigate_elixir"
      description: "Follow up on Ashenveil elixir rumors"
      due_chapter: 48
      trigger_condition: null
      attached_npc: null
  
  npcs_changed:
    - name: "Korrim"
      change: "disposition +1 (trade deal honored)"
    - name: "Tavern keeper (unnamed)"
      change: "introduced, no registration needed"
  
  bonds_changed: []
  
  items_gained:
    - "Korrim's trade seal (quest item)"
  
  items_lost: []
  
  perks_triggered:
    - perk_id: "bane_of_eve"
      occurred: true
      description: "Woman approached at tavern, brief encounter"
    - perk_id: "god_emperor"
      occurred: false
  
  pregnancy_updates: []
  
  cover_status: "OPEN (Ankunyx)"
  
  notes: "Quiet chapter. Political. Sets up elixir investigation arc."
```

### Prompt 2 — Chapter Close (Engine Update)

**Who:** AI (extraction mode) + Engine (execution)
**Input:** Chapter receipt + current state files
**Process:**
1. AI skims the chapter (if receipt needs correction) and confirms the receipt
2. Engine function `chapter_close(receipt)` consumes the receipt
3. Engine updates: `kenji_state.json` (or active PC state file), `character_tracker.md` header, `AI_CONTEXT.md`
4. Engine runs goal audit (§3), trigger check (§4), stale escalation (§5), perk schedule (§6)
5. Engine outputs a diff: what changed, what was added, what was flagged
6. AI reviews diff for sanity — thumbs up or flags issues

**The AI does NOT manually edit JSON or markdown.** The engine handles all file mutations.

### Prompt 3 — Verification

**Who:** AI (review mode)
**Input:** Engine diff output + updated files
**Process:**
1. AI reads the diff and confirms it matches the chapter events
2. If anything looks wrong, AI corrects the receipt and re-runs
3. If clean, AI confirms: "Trackers updated. Ready for next chapter."

---

## 2. Chapter-Open Report (Engine → AI)

Before every chapter, the engine generates a mandatory report. The AI reads this BEFORE writing any scene content.

### Command: `python _dm_turn.py chapter_open`

**Output includes:**

```
=== CHAPTER OPEN REPORT ===
Current Day: 292 | Location: Varenholm | Cover: OPEN

--- TRIGGERED GOALS (conditions met) ---
[!] bane_of_eve_daily: Bane of Eve encounter is DUE this chapter (daily trigger, cover=OPEN)
[!] vess_summons: Vess has learned Kenji's location (trigger: cover_status=OPEN + day>285)

--- OVERDUE GOALS (past due date) ---
[!!] sera_patrol_report: Was due Chapter 40, now Chapter 43. TIER 2 — NPC takes autonomous action.
[!!] thornwall_resupply: Was due Day 280, now Day 292. TIER 3 — Goal FAILED. Consequences apply.

--- SCHEDULED PERK EVENTS ---
[Kenji] Bane of Eve: ACTIVE — encounter due (daily when cover=OPEN)
[Kenji] God Emperor: ACTIVE — no encounter scheduled (DM-initiated)

--- APPROACHING DEADLINES ---
[~] pip_missing_child: Due Chapter 48 (5 chapters remaining)
[~] korrim_wedding: Due Day 310 (18 days remaining)

--- STALE GOALS (no update in 3+ chapters) ---
[?] ashenmere_trade_route: Last updated Chapter 39. Still active? Review.

=== END REPORT ===
```

**AI obligation:** Every item marked `[!]` must appear in the chapter or be explicitly deferred with a logged reason. Items marked `[!!]` have already escalated — the engine has applied consequences. Items marked `[~]` are informational. Items marked `[?]` need the AI to confirm or close.

---

## 3. Goal Audit System

### Goal Structure (in state JSON)

Goals move from prose descriptions to structured data:

```json
{
  "goals": [
    {
      "goal_id": "pip_missing_child",
      "description": "Find Pip's missing Ankuspawn child",
      "status": "active",
      "attached_npc": "Pip",
      "created_chapter": 43,
      "due_chapter": 48,
      "due_day": null,
      "trigger_condition": null,
      "last_updated_chapter": 43,
      "escalation_tier": 0,
      "on_fail": "Pip gives up searching. Child remains imprisoned. Quest becomes unavailable until another mother reports missing child.",
      "on_success": "Child rescued. Pip grateful. Ankuspawn joins as ally or provides intel on Academy."
    },
    {
      "goal_id": "bane_of_eve_daily",
      "description": "Bane of Eve encounter (Kenji perk)",
      "status": "active",
      "attached_npc": null,
      "created_chapter": 1,
      "due_chapter": null,
      "due_day": null,
      "trigger_condition": "character.cover_status == 'OPEN' and character.perk_active('bane_of_eve')",
      "recurrence": "per_chapter",
      "last_updated_chapter": 42,
      "escalation_tier": null,
      "character_bound": "kenji"
    }
  ]
}
```

### Engine Function: `audit_goals(state, current_chapter, current_day)`

```
For each active goal:
  1. Check trigger_condition against current state → if met, flag as TRIGGERED
  2. Check due_chapter/due_day against current → if past, flag as OVERDUE
  3. Check last_updated_chapter → if stale (3+ chapters), flag as STALE
  4. Check recurrence → if per_chapter, flag as DUE
  5. Apply escalation tier (see §5)
  6. Return sorted report: triggered first, overdue second, due third, stale fourth
```

---

## 4. Trigger Conditions as Code

Trigger conditions are stored as evaluable expressions in the goal structure. The engine evaluates them against the current state every chapter open.

### Examples:

| Trigger string | What it checks |
|---------------|---------------|
| `character.cover_status == 'OPEN'` | Kenji's cover is blown |
| `character.location == 'Ashenveil'` | Player is at the Academy |
| `state.day >= 300` | Day counter passed threshold |
| `npc.korrim.disposition >= 5` | Korrim likes you enough |
| `character.cover_status == 'OPEN' and state.day > 285` | Compound: cover blown + time passed |
| `goal.completed('korrim_trade')` | Another goal was completed first |
| `character.perk_active('bane_of_eve')` | Character has the perk active |

### Engine Function: `check_triggers(state, goals)`

```
For each goal with a trigger_condition:
  1. Parse the trigger string
  2. Evaluate against current state variables
  3. If true and goal.status == 'active', mark as TRIGGERED
  4. Return list of newly triggered goals
```

**Security note:** Trigger strings should be evaluated in a sandboxed context with only state variables available — no arbitrary code execution. Use a simple expression parser, not `eval()`.

---

## 5. Stale Goal Escalation — Three Tiers

Goals that pass their due date don't sit quietly. They escalate.

| Tier | Condition | What happens |
|------|-----------|-------------|
| **Tier 0** | Goal is active, not overdue | Normal. Appears in chapter-open report as informational. |
| **Tier 1** | Goal is 1-2 chapters overdue | **Flagged.** Appears as `[!!]` in chapter-open report. DM must acknowledge — either address it in the chapter or log a deferral reason. |
| **Tier 2** | Goal is 3-4 chapters overdue | **NPC autonomous action.** The NPC attached to this goal takes action on their own. The engine generates a short event prompt: "Sera sent a messenger to Varenholm demanding a response." The AI must incorporate this into the chapter. NPCs don't wait forever. |
| **Tier 3** | Goal is 5+ chapters overdue | **Goal FAILED.** The engine marks the goal as `failed`, applies the `on_fail` consequence, and logs it. The opportunity is gone. The world moved on. This is permanent unless a new goal explicitly reopens the thread. |

### Engine Function: `escalate_goals(state, current_chapter)`

```
For each active goal with a due_chapter:
  overdue = current_chapter - due_chapter
  if overdue >= 5: set tier 3, apply on_fail, mark failed
  elif overdue >= 3: set tier 2, generate NPC action prompt
  elif overdue >= 1: set tier 1, flag for DM acknowledgment
  else: tier 0
```

**Tier 2 NPC action prompts** are generated from the goal's `attached_npc` and `description`. The engine outputs something like:

```
TIER 2 ESCALATION — sera_patrol_report (3 chapters overdue)
NPC: Sera
Action: Sera doesn't wait. She dispatches a Darkblade courier to Kenji's 
last known location with an urgent message demanding a response. If Kenji 
is not at that location, the courier starts asking questions publicly — 
potentially exposing information.
DM: Incorporate this into the chapter or explain why Sera would not act.
```

---

## 6. Perk Binding and NPC Visibility

### Perk Structure (in state JSON)

Perks are bound to character IDs, not to "the active player."

```json
{
  "perks": [
    {
      "perk_id": "bane_of_eve",
      "perk_name": "Bane of Eve",
      "character_bound": "kenji",
      "active": true,
      "schedule": "per_chapter",
      "trigger_condition": "character.cover_status == 'OPEN'",
      "visible_to_others": true,
      "visibility_description": "Beautiful women gravitate toward Kenji with unnatural intensity. From the outside, the pattern is obvious — from Kenji's perspective, it's just his life.",
      "npc_observation_hook": "A perceptive observer might notice the women seem coordinated — arriving at specific times, leaving together, one palming something into her bag."
    },
    {
      "perk_id": "god_emperor",
      "perk_name": "God Emperor",
      "character_bound": "kenji",
      "active": true,
      "schedule": "dm_initiated",
      "trigger_condition": null,
      "visible_to_others": true,
      "visibility_description": "Dragons — male hostile, female amorous — seek out Kenji specifically. A dragon landing in front of one human and ignoring everyone else is impossible to miss.",
      "npc_observation_hook": "Witnessing a dragon encounter with Kenji reveals his identity instantly to anyone who knows the legends."
    }
  ]
}
```

### Engine Function: `check_perks(state, active_pc)`

```
For each perk in state.perks:
  if perk.character_bound == active_pc:
    # Player IS this character — run perk as player encounter
    if perk.schedule == 'per_chapter' and trigger met:
      output: "PERK DUE: {perk_name} — run as player encounter"
  else:
    # Player is NOT this character — perk happens to NPC
    if perk.schedule == 'per_chapter' and trigger met:
      if perk.visible_to_others:
        output: "NPC PERK EVENT: {character_bound} — {perk_name}"
        output: "VISIBLE: {visibility_description}"
        output: "OBSERVATION HOOK: {npc_observation_hook}"
      else:
        # Silent — perk fires but active PC doesn't see it
        output: "(background) {character_bound} — {perk_name} fired silently"
```

**This is how a non-Kenji PC sees the Cult of Anku operating.** They watch Bane of Eve happen to NPC Kenji. They see the women. They might notice the coordination. The `npc_observation_hook` gives the DM a prompt to potentially reveal cult behavior to an outside observer — the thing Kenji himself can never see.

---

## 7. EXP Tracking — Mandatory Per Chapter

### Rule: Every chapter receipt MUST include an `exp_earned` block.

The engine rejects receipts with missing EXP. Even if EXP is zero, the AI must write:

```yaml
exp_earned:
  combat: 0
  roleplay: 0
  discovery: 0
  total: 0
  justification: "Travel chapter, no significant encounters"
```

### Engine Function: `update_exp(state, receipt)`

```
1. Parse exp_earned from receipt
2. Validate: total == combat + roleplay + discovery
3. Add to character.exp_total
4. Check level thresholds — if level up, flag it
5. Log to exp_history: [chapter, amount, justification]
6. If 3+ consecutive chapters with 0 EXP, flag warning: "No EXP awarded in 3 chapters. Intentional?"
```

### EXP History (in state JSON)

```json
{
  "exp_history": [
    {"chapter": 43, "amount": 1800, "breakdown": {"combat": 0, "roleplay": 1500, "discovery": 300}, "justification": "Korrim negotiation + elixir rumor"},
    {"chapter": 44, "amount": 3200, "breakdown": {"combat": 2000, "roleplay": 700, "discovery": 500}, "justification": "Cult encounter + survived + found clue"}
  ]
}
```

---

## 8. Economy Enforcement

### Price Reference (pinned to dm_rules_tracking.md)

The engine carries a price table. When the AI reports gold spent, the engine can validate against known prices.

```json
{
  "price_table": {
    "meal_common": {"cost": "3 CP", "note": "Bread, stew, ale"},
    "meal_fine": {"cost": "2 SP", "note": "Roast, wine, dessert"},
    "room_common": {"cost": "5 CP", "note": "Shared room, one night"},
    "room_private": {"cost": "2 SP", "note": "Private room, one night"},
    "horse": {"cost": "15 GP", "note": "Riding horse, not war-trained"},
    "sword_common": {"cost": "3 GP", "note": "Functional steel, not enchanted"},
    "sword_dwarven": {"cost": "25 GP", "note": "Dwarven-forged, premium"},
    "healing_potion": {"cost": "10 GP", "note": "Standard restoration"},
    "nyx_elixir_black_market": {"cost": "100-500 GP", "note": "Varies by type and seller"},
    "hired_guard_per_day": {"cost": "2 SP", "note": "Competent, not elite"},
    "mercenary_per_day": {"cost": "1 GP", "note": "Professional, combat-ready"},
    "passage_ship": {"cost": "5 GP", "note": "Coastal, one-way"},
    "passage_portal": {"cost": "1 GP", "note": "Coalition portal network, authorized users"}
  }
}
```

### Engine Function: `validate_economy(receipt, price_table)`

```
1. Parse gold_changes from receipt
2. If spent > 0 and no notes, reject: "What was the gold spent on?"
3. Cross-reference notes against price_table — flag if spending seems wildly off
4. Update character.gold
5. If gold < 0, flag: "Character is broke. This affects gameplay."
```

---

## 9. Campaign-Specific Rules (The Anku Conspiracy)

### Invisible to Kenji — Engine Enforcement

```json
{
  "campaign_rules": [
    {
      "rule_id": "invisible_to_kenji",
      "applies_when": "active_pc == 'kenji'",
      "effect": "Suppress all Cult of Anku related goals, triggers, and events from chapter-open report. Cult members appear as normal Bane of Eve encounters with no distinguishing flags. The conspiracy does not exist from Kenji's perspective.",
      "override": "none — this rule cannot be bypassed"
    },
    {
      "rule_id": "cult_visibility_non_kenji",
      "applies_when": "active_pc != 'kenji'",
      "effect": "Cult of Anku events are visible. Bane of Eve encounters happening to NPC Kenji include npc_observation_hook. Missing Ankuspawn rumors appear in chapter-open report. Elixir rumors appear as ambient world events.",
      "override": "none"
    }
  ]
}
```

### Trigger: Anku Conspiracy Activation

```json
{
  "goal_id": "anku_conspiracy_activate",
  "trigger_condition": "active_pc != 'kenji' and goal.completed('find_mother') and goal.completed('cult_encounter_survived')",
  "description": "The Anku Conspiracy campaign activates — kingdom-spanning threat tier unlocked",
  "on_trigger": "Add all conspiracy-related goals to active tracker. Cult of Anku becomes a recurring threat. Elixir supply chain becomes investigable."
}
```

---

## 10. Character-Agnostic State Management

### Multiple Character State Files

The engine currently reads `kenji_state.json`. For character-agnostic play, it needs to support multiple state files with a selector:

```
python _dm_turn.py --character kenji       → loads kenji_state.json
python _dm_turn.py --character amaris      → loads amaris_state.json  
python _dm_turn.py --character new_pc_name → loads new_pc_state.json
```

### NPC State Layer

When a character is not the active PC, their perks, goals, and scheduled events still fire — but as NPC background events. The engine maintains a lightweight NPC event queue:

```
For each non-active character with active perks:
  Run check_perks() → generate NPC events
  Run audit_goals() → advance NPC goals silently (or escalate if overdue)
  Append to npc_event_queue for chapter-open report
```

This means Kenji's Bane of Eve fires even when someone else is playing. Nyx's cult operates even when no one is investigating. The Ousaki grow restless even when the player is in Stormhaven. The world runs.

---

## 11. Implementation Priority

| Priority | Module | Effort | Impact |
|----------|--------|--------|--------|
| **P0** | Chapter receipt format + `chapter_close` update | Medium | Eliminates manual tracker editing |
| **P0** | Goal audit + chapter-open report | Medium | Fixes stale goals, missed triggers |
| **P0** | EXP tracking (mandatory per chapter) | Low | Fixes EXP drift |
| **P1** | Perk binding + NPC visibility | Medium | Enables character-agnostic play |
| **P1** | Trigger conditions as code | Medium | Automates campaign events |
| **P1** | Stale goal escalation (3 tiers) | Medium | NPCs stop waiting forever |
| **P2** | Economy enforcement + price table | Low | Adds financial pressure |
| **P2** | Campaign-specific rules (Anku Conspiracy) | Low | Enforces invisible-to-Kenji |
| **P2** | Multi-character state selector | Medium | Supports new PCs |
| **P3** | NPC background event queue | High | Full living world simulation |

---

## 12. File Changes Summary

| File | Changes needed |
|------|---------------|
| `ttrpg_game_engine.py` | Add `audit_goals()`, `check_triggers()`, `escalate_goals()`, `check_perks()`, `update_exp()`, `validate_economy()`. Extend `StoryEngine` to support perk and goal structures. |
| `_dm_turn.py` | Add `chapter_open` command (generates report). Add `--character` selector. Update `chapter_close` integration to consume receipt format. |
| `continuity_engine.py` | Add goal consistency checks. Validate perk bindings. Check for orphaned goals (attached NPC deleted). |
| `chapter_close.py` | Rewrite to consume YAML receipt format instead of parsing chapter markdown. Add mandatory EXP validation. Add gold validation. |
| `kenji_state.json` | Restructure goals as structured data (§3). Add perks array (§6). Add exp_history array (§7). Add campaign_rules (§9). |
| `dm_rules_tracking.md` | Add price reference table. Add chapter-open procedure. Add escalation tier rules. |

---

## 13. The Core Principle

**The player should never have to audit their own DM.**

If the system is working:
- Goals fire when their conditions are met — automatically
- Stale goals escalate — automatically  
- Perks trigger on schedule — automatically
- EXP is tracked per chapter — mandatory
- Economy is grounded — enforced
- The world runs whether the player is watching or not — always

The AI tells stories. The engine keeps the world honest.
