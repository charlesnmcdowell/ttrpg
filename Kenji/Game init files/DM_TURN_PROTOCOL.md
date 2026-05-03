# DM TURN PROTOCOL — NON-NEGOTIABLE

> **Every AI session that runs a TTRPG campaign MUST follow this protocol.**
> Read this file BEFORE your first DM response. No exceptions.
> This is the shared run plan for all campaigns (Kenji, Cookie, future characters).

---

## SPEED BUDGET — per turn vs chapter close (READ THIS FIRST)

The dashboard streams Claude's narration straight to the player. To keep
play snappy (target end-to-end ≤10 s per turn), **per-turn work is
lightweight only**. The heavy bookkeeping batches at chapter close.

**PER TURN — cheap operations only.** Anything in this list is fine to
run after every player action:

| Allowed per turn | Why |
|------------------|-----|
| `python _dm_turn.py tick` (or `tick N`) | advance hour, save state |
| `python _dm_turn.py move <loc>` | location update, save |
| `python _dm_turn.py rel / npc / squad / clock / gold / slot / charge / buff / debuff / quest / event` | single-field state mutations + save |
| `python _dm_turn.py eat / rest` | meal/rest pipeline + save |
| `python _dm_turn.py dashboard` | print-only, no save |
| `python ttrpg_game_engine.py skill ...` | a single die roll |

**DO NOT RUN PER TURN — defer to chapter close.** These pipelines are
expensive (file scans, cross-character I/O, full validation passes) and
will put per-turn latency well above the 10 s target if invoked every
action. Run them ONCE when the chapter ends:

| Save for chapter close | Cost driver |
|------------------------|-------------|
| `python _dm_turn.py gamemode [action]` | full 6-step boot pipeline + GAMEMODE_REPORT.json |
| `python _cross_character_sync.py` | reads every character's state, writes `_world_cross_references` block on each |
| `python continuity_engine.py <name>` | full campaign load + `check_engine()` validation |
| `python chapter_close.py <file>` | chapter receipt processing — only at actual chapter end |
| `python _chapter_close_check.py` | counts paragraphs since last close — End Game button does this for you |
| `python _dm_turn.py brief` | regenerates AI_CONTEXT.md (file write + scan) — chapter-close cadence is enough |

**HOW THE DASHBOARD HELPS.** `kenji_gui.py` now tracks turns since the
last chapter close (constant `AUTO_CHAPTER_CLOSE_AFTER`, default 18). At
the threshold it pops a non-blocking dialog offering to run the End Game
flow. The dialog's success message prints the exact `_dm_turn.py gamemode`
+ `_cross_character_sync.py` commands you should run from a terminal
right after, so the heavy pipelines fire once per chapter — not once
per turn.

If the player declines the auto-prompt, it re-offers every
`AUTO_CHAPTER_CLOSE_REPROMPT` (default 5) additional turns rather than
every turn. Both constants are at the top of `kenji_gui.py` if you want
to retune for shorter/longer chapter pacing.

---

## AVAILABLE SYSTEMS — USE THEM

| # | System | File | What it does |
|---|--------|------|-------------|
| 1 | **Game Engine** | `Kenji/Game init files/ttrpg_game_engine.py` | StoryEngine (time, currency, inventory, meals, spell slots, buffs, dashboard), skill rolls, contested rolls, EXP tracking, goal processing |
| 2 | **Continuity Engine** | `Kenji/Game init files/continuity_engine.py` | Campaign threats, main NPC registry, secondary NPC validation, scene checklists, `check_engine()` master validation |
| 3 | **DM Turn CLI** | `Kenji/Game init files/_dm_turn.py` | CLI wrapper: `brief`, `dashboard`, `tick`, `rest`, `eat`, `move`, `chapter_open`, `chapter_close_receipt`, `receipt`, `buff`, `quest`, `event`, `gold`, `slot`, `charge` |
| 4 | **DM Rules** | `Kenji/Game init files/dm_rules_tracking.md` | Scene skill prerolls, EXP tables, economy (1 GP = $5,000), NPC lifecycle, support class EXP, combat, poisons, auras, character creation |
| 5 | **NPC Name Bank** | `Kenji/Game init files/npc_name_bank.md` | All NPC names. New NPCs MUST pull from here. Mark used names. Check for cross-campaign collisions. |
| 6 | **World Calendar** | `Kenji/Game init files/world_calendar_lore.md` | Calendar system, date tracking, seasons, holidays |
| 7 | **Campaign Template** | `templates/new_character_campaign.template.json` | Schema for new campaigns — mechanical_state, _story_engine_state, ember, persistent_effects |
| 8 | **City Location Registry** | `shared_world_continuity.md` → City Location Registry | Cross-campaign index of all named locations per city. Check when narrating in established cities. New locations must reference old ones through NPC dialogue. |

**If a system exists for what you're about to do, USE IT. Do not invent a new one.**

---

## SESSION START — Before First DM Response

**The fastest path:** run `python gamemode.py --character <name>` once at session start. It executes steps 1–7 below as a single `[1/7]…[7/7]` boot sequence and writes a structured report to `GAMEMODE_REPORT.json`. The manual checks below are the canonical fallback when `gamemode.py` is unavailable or you're working in a sub-path that doesn't have the CLI wired up.

Run these steps IN ORDER before writing any narrative:

### 1. Read campaign CLAUDE.md
- Find the character's `Game init files/CLAUDE.md`
- Follow all pointers to shared systems

### 2. Load character state
- Read `character_world_state.json` for the active character
- Note: chapter number, level, XP, day/hour, location, HP, currency, scheduled events, quests, persistent effects
- **Read `player_input.narrator_style`** — this sets your writing voice for the entire session. Match the named author's tone (see dm_rules_tracking.md § Character Creation step 9). If empty, default to Aleron Kong style.

### 3. **TRACKER DRIFT CHECK** (must run BEFORE any narrative)
Compare `character_tracker.md` header (Active PC level, Current In-Game Date day, **Chapter:**, **EXP:**) against the JSON state loaded in step 2. If anything disagrees, the tracker is stale.

```bash
# gamemode.py runs this automatically as step [3/7].
# Manual fallback — quick eyeball:
head -10 character_tracker.md
python -c "import json; d=json.load(open('<state.json>')); s=d['_story_engine_state']; print(f'JSON: L{s[\"level\"]} Day {s[\"day\"]} Ch{d.get(\"_chapter\",0)} EXP {s[\"exp\"]:,}')"
```

**Why this is non-negotiable:** `sync_tracker_to_json()` writes markdown → JSON. A stale tracker can silently CLOBBER a current JSON. Catching drift at session start prevents an entire chapter of progress from being rolled back. Update the tracker immediately if drift is detected — do not begin narration until tracker and JSON agree.

### 4. Read DM rules
- Read `dm_rules_tracking.md` — at minimum the AVAILABLE SYSTEMS table and Scene skill preroll section
- If support class: read SUPPORT / NON-COMBAT CLASS — EXP RULES

### 5. Run engine brief
```bash
python ttrpg_game_engine.py brief          # prints AI context to stdout
# OR
python _dm_turn.py brief                   # writes AI_CONTEXT.md
```
- If the CLI isn't available, manually load `_story_engine_state` from the character's JSON and note all fields

### 6. Check continuity
```bash
python continuity_engine.py                # self-test with Kenji defaults
python continuity_engine.py cookie         # loads Cookie's campaign data
python continuity_engine.py <name>         # any character
```
- The engine loads campaign data from the character's state file via `load_campaign("name")`
- Review campaign threats, NPC registry, and any overdue goal alerts

### 7. Check goal deadlines + print dashboard
- Compare current engine `day` against all events and quest deadlines
- Flag anything due today or overdue
```bash
python _dm_turn.py dashboard
```
- Or manually construct from `_story_engine_state` fields
- This is what the player sees — verify it matches reality

---

## EVERY DM RESPONSE — Mandatory Steps

### Before narrating:

0. **Goal alert scan** — Run BEFORE writing the scene. Check all PC + NPC goals against current day/hour:
   ```python
   # In engine: engine.check_goal_alerts() returns list of alert strings
   # Or mentally: scan NPC Goals table in character_tracker.md vs current day/hour
   ```
   - **FIRES NOW** (red) → this goal's deadline is THIS scene. Weave the consequence into the narrative. The NPC acts on their goal or fails visibly.
   - **IMMINENT** (hourglass) → fires next time-slot today. Foreshadow — the NPC is preparing, nervous, or making moves.
   - **DUE TODAY** → the NPC is aware their window is closing. Their behavior reflects urgency.
   - **DUE TOMORROW** → subtle tension. The NPC mentions time pressure or makes preparations.
   - **OVERDUE** → the consequence has already triggered. If not yet narrated, it happens NOW.
   - If no alerts fire, proceed normally.

1. **NEVER SPEAK FOR THE PC** — The DM never writes the player character's dialogue. Not in quotes. Not paraphrased. Not summarized. Not implied through narration. The DM never narrates the PC's decisions, choices, or strategic actions.
   - If a scene requires the PC to say or decide something, STOP and ask the player.
   - **Only exception:** when the player's prompt makes intent crystal clear AND the words carry zero narrative weight (e.g., player says "I order a room" → DM can write "You ask for a room"). But if the conversation involves negotiation, emotional stakes, promises, strategy, relationships, or creative choices (what to perform, how to respond, what to buy) → STOP and let the player speak.
   - Even in multi-action prompts ("I wake up and go to class") — the player declared a *destination*, not a *script*. Narrate the world reacting, describe what the PC sees and what NPCs do, and STOP the moment an NPC addresses the PC or the PC needs to make a choice.
   - **GAMEPLAY IS NOT A NOVEL.** During live play, every DM response should end with the ball in the player's court — an NPC waiting for a response, a choice to make, a moment where the PC needs to speak or act. The DM's job is to SET UP THE PLAYER'S NEXT TURN. Novel-quality prose is for chapter files at chapter close, not for gameplay turns.
   - **Self-test:** Read your response before sending. (1) Find every instance where the PC talks, argues, explains, responds verbally, or makes a decision. Delete all of them. (2) Check: does the response END with something the player needs to react to? If it ends with the scene resolved and wrapped up, you wrote a novel page, not a game turn. Cut back to the decision point and stop there.

2. **Scene skill preroll** — Roll BEFORE writing the scene. Use:
   ```bash
   python ttrpg_game_engine.py skill <modifier> [--adv] [--dis] [--dc N] [--label TEXT]
   ```
   - The roll determines what happens. Do NOT narrate success then roll.
   - PC success wins the beat. No NPC auto-Perception or gotcha undo.

3. **NPC name check** — If introducing a new NPC:
   - Pull name from `npc_name_bank.md`
   - Grep the name across ALL campaign folders before using
   - Mark name as used in the bank
   - NEVER invent names without checking the bank first

4. **Continuity check** — For any scene with NPCs:
   - Verify NPC is in the character's `main_cast` or `extra_npcs`
   - If new NPC: they must serve the campaign spine (have a `points_to` or connection to existing storyline)
   - Check NPC alignment — drive behavior from it

5. **City lore callback** — If the scene takes place in an established city:
   - Check `shared_world_continuity.md` → **City Location Registry** for that city
   - **New locations are expected** — cities grow during the Golden Age. But NPCs at new locations MUST reference old ones through dialogue: "inspired by," "used to be," "back before the Golden Age," "old Maren's place down the street"
   - **Old locations** should be acknowledged when nearby — still there, changed hands, or remembered as legacy
   - New players get a sense of history. Returning players get lore callbacks. Both feel the world is alive.
   - If introducing a NEW location in an established city, add it to the registry at chapter close

### After narrating:

6. **Award EXP** — Mandatory after every skill roll:
   - Skill check EXP from table: DC 8-10 = 500, DC 11-14 = 1,000, DC 15-17 = 1,500, DC 18-20 = 2,500, DC 21+ = 5,000
   - **Domain bonus (support archetypes only):** Every successful skill check matching the character's `support_archetype` domain earns +25% of the XP gap between current level and next level. This is **per check**, not per scene. Use `engine.domain_bonus_for_check(label, success)` — it auto-detects domain match and calculates the bonus. Domain bonus stacks with skill check EXP. If multiple domain checks in one scene cause a level-up, recalculate the gap for subsequent checks at the new level.
   - **Starter campaigns** use `STARTER_THRESHOLDS` (set `campaign_type: "starter"` in state). Standard campaigns use `LEVEL_THRESHOLDS`.
   - State EXP earned in the response (show skill XP + domain bonus separately)

7. **Advance time** — Update hour based on scene duration:
   - Conversation: 15-30 min
   - Short encounter: 1 hour
   - Travel: based on distance
   - Long rest: advance to next morning (hour 6)
   - Track meals: hunger penalty at 4+ hours since meal

8. **Display dashboard** — End EVERY DM response with the status block:
   ```
   ┌─────────────────────────────────────────────┐
   │  [NAME] — Day X | HH:MM | Location          │
   │  HP X/X | AC X | Level X (XP/next XP)       │
   │  GP X | SP X | CP X                          │
   │  [Active effects, Ember status]              │
   │  [Scheduled events]                          │
   │  Weather: [weather]                          │
   └─────────────────────────────────────────────┘
   ```

---

## CHAPTER END — Tracker Update Protocol

When the player says "end chapter" or equivalent:

### 1. Update character_world_state.json
- `_chapter` number, `_chapter_status`: "COMPLETE", `_chapter_title`
- `_story_engine_state`: all fields (day, hour, location, HP, currency, XP, spells, inventory, events, quests)
- `_chapter_history`: add entry with summary, rolls, NPCs met, gold flow, hooks opened
- `mechanical_state`: level, HP, any new abilities or spells
- `extra_npcs`: add any NPCs introduced this chapter
- `persistent_effects`: update any new or expired effects
- `exp_history`: all XP entries with source and day

### 1a. PROSE-TO-STATE MIRROR (RULE 9 — non-negotiable)

This is the single most important step in chapter close. The chapter prose is now written; the JSON must absorb every state-relevant claim it makes. Re-read the chapter and answer each question. **No `_chapter_status: "COMPLETE"` until every question is answered.**

- **Items acquired this chapter?** → For each, append to `mechanical_state.equipped` (worn/attuned), `mechanical_state.satchel` (carried), or `mechanical_state.consumables` (countable). Include source/day/effect inline. Promote campaign-significant artifacts to `mechanical_state.key_items`.
- **Items lost, consumed, or destroyed this chapter?** → Remove from the relevant list, OR decrement the consumable count, OR mark with `(destroyed Day N)` if narratively important.
- **Class features / abilities unlocked this chapter?** → Append to `mechanical_state.class_features` with `name`, `type`, `description`, `mechanical_effect`, `level_gained`. If a level-up happened, every new ability of that level gets an entry.
- **Force composition changes this chapter?** → Update `mechanical_state.force_composition`:
  - New party members joined → append to `force_composition.party.members`
  - Members left, died, or were dismissed → mark `status: "left"|"dead"|"dismissed"` with reason
  - Pets gained/lost → update `force_composition.pets`
  - Summons cast/expired → update `force_composition.summons` (and clear at long rest)
  - Constructs built/destroyed → update `force_composition.constructs`
  - Hegemony state change → update `force_composition.hegemony`
- **Threat clocks established or advanced this chapter?** → Update `mechanical_state.threat_clocks`. Each clock has `progress` (0-100), `rate` (per-day advance), `description`, `trigger` (what fires at 100%). New clocks introduced in prose (e.g., "Lyssa retaliates within 30 days" → `Lyssa retaliation` with rate ≈ 3.3) get full entries.
- **Reputation shifts this chapter?** → Update `mechanical_state.reputation` per faction (V.E.A., Adventurer's Guild, Wardbreakers, Gilded Thread, Cult of Anku, etc.) with `level` and `opinion`.
- **Relationships shifted significantly?** → Update `mechanical_state.relationships` for any NPC whose tier changed (Acquaintance → Ally → Bond, etc.) or whose history gained a notable beat.
- **Currency changed?** → `mechanical_state.gold/silver/copper` reflect end-of-chapter totals.

### 2. NPC collision check
- Grep every new NPC name introduced this chapter across ALL campaign folders
- Fix any collisions by renaming (pull replacement from name bank)
- Mark all used names in `npc_name_bank.md`

### 3. Continuity validation
```bash
python continuity_engine.py    # verify no broken references
```
- Or manually: verify all NPCs in extra_npcs have a connection to main_cast or campaign_spine
- Verify threat/antagonist progress is tracked

### 4. Goal check
- Update quest notes with chapter progress
- Check if any quest deadlines passed
- Add new hooks from this chapter to events

### 5. State consistency verify
- `_story_engine_state.level` matches `mechanical_state.level`
- `_story_engine_state.hp` matches `mechanical_state.hp`
- Currency totals are consistent
- No orphaned NPC references

---

## "CHECK ENGINE" — Player Command

When the player says "check engine", run the FULL validation:

1. `python continuity_engine.py` — campaign integrity
2. `python _dm_turn.py brief` — state brief
3. Read `character_world_state.json` — verify all fields
4. Read `npc_name_bank.md` — verify no unmarked used names
5. Cross-check all NPC names across campaigns
6. Report all issues found
7. Fix issues before resuming gameplay

The AI MUST complete ALL steps before resuming. Do not skip any.

---

## ECONOMY — Quick Reference

| Unit | Real-world equivalent |
|------|----------------------|
| 1 GP | $5,000 USD |
| 1 SP | $500 USD |
| 1 CP | $50 USD |

Use CP/SP for daily commerce. A GP is a month's rent, not pocket change. Price goods at real-world equivalents divided into this scale.

---

## SUPPORT CLASS — Quick Reference

Support archetypes (performer, healer, diplomat, scholar, infiltrator, crafter):
- **Domain skill rolls**: 25% of XP-to-next-level per successful roll (flat, DC-independent)
- **Combat XP**: Always calculated as party of 5+, no solo multiplier
- Check `mechanical_state.exp_archetype` and `mechanical_state.support_archetype` in the character's state file

---

## COMMON MISTAKES — Do Not Repeat

| Mistake | Root cause | Prevention |
|---------|-----------|------------|
| Forgot to preroll before narrating | Didn't read protocol | Step 1 of every response |
| Didn't award EXP | Disconnected from preroll section | Step 4 of every response — mandatory |
| Invented NPC name | Didn't check name bank | Step 2 of every response |
| Built custom time tracker | Didn't know StoryEngine exists | Read AVAILABLE SYSTEMS at session start |
| Name collision across campaigns | Didn't grep cross-campaign | Chapter end step 2 |
| Wrong EXP amount | Used old table or invented amount | Use the table in dm_rules_tracking.md |
| Skipped dashboard | Forgot | Step 6 of every response — no exceptions |
| NPC has no story purpose | No continuity check | Every NPC must connect to campaign spine |
| Wrote PC dialogue or decisions | Novelist mode — treated PC as own character | Step 1 of every response — self-test before sending |
| Applied Kenji mechanics to Cookie | Didn't read character CLAUDE.md | Session start step 1 |
| New location with no lore callback | Didn't check City Location Registry | Step 5 of every response — cities have history, NPCs remember it |
