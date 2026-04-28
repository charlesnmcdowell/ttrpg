# DM TURN PROTOCOL — NON-NEGOTIABLE

> **Every AI session that runs a TTRPG campaign MUST follow this protocol.**
> Read this file BEFORE your first DM response. No exceptions.
> This is the shared run plan for all campaigns (Kenji, Cookie, future characters).

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

Run these steps IN ORDER before writing any narrative:

### 1. Read campaign CLAUDE.md
- Find the character's `Game init files/CLAUDE.md`
- Follow all pointers to shared systems

### 2. Load character state
- Read `character_world_state.json` for the active character
- Note: chapter number, level, XP, day/hour, location, HP, currency, scheduled events, quests, persistent effects
- **Read `player_input.narrator_style`** — this sets your writing voice for the entire session. Match the named author's tone (see dm_rules_tracking.md § Character Creation step 9). If empty, default to Aleron Kong style.

### 3. Read DM rules
- Read `dm_rules_tracking.md` — at minimum the AVAILABLE SYSTEMS table and Scene skill preroll section
- If support class: read SUPPORT / NON-COMBAT CLASS — EXP RULES

### 4. Run engine brief
```bash
python ttrpg_game_engine.py brief          # prints AI context to stdout
# OR
python _dm_turn.py brief                   # writes AI_CONTEXT.md
```
- If the CLI isn't available, manually load `_story_engine_state` from the character's JSON and note all fields

### 5. Check continuity
```bash
python continuity_engine.py                # self-test with Kenji defaults
python continuity_engine.py cookie         # loads Cookie's campaign data
python continuity_engine.py <name>         # any character
```
- The engine loads campaign data from the character's state file via `load_campaign("name")`
- Review campaign threats, NPC registry, and any overdue goal alerts

### 6. Check goal deadlines
- Compare current engine `day` against all events and quest deadlines
- Flag anything due today or overdue

### 7. Print dashboard
```bash
python _dm_turn.py dashboard
```
- Or manually construct from `_story_engine_state` fields
- This is what the player sees — verify it matches reality

---

## EVERY DM RESPONSE — Mandatory Steps

### Before narrating:

1. **NEVER SPEAK FOR THE PC** — The DM never writes the player character's dialogue. Not in quotes. Not paraphrased. Not summarized. Not implied through narration.
   - If a scene requires the PC to say something, STOP and ask the player.
   - **Only exception:** when the player's prompt makes intent crystal clear AND the words carry zero narrative weight (e.g., player says "I order a room" → DM can write "You ask for a room"). But if the conversation involves negotiation, emotional stakes, promises, strategy, or relationships → STOP and let the player speak.
   - Even in multi-action prompts ("meet X, then do Y") — narrate NPC dialogue, describe the scene, and STOP for the player's words whenever the PC needs to respond to something meaningful. The player declared the goal, not the dialogue.
   - **Self-test:** Read your response before sending. Find every instance where the PC talks, argues, explains, or responds verbally. Delete all of them. Present the NPC's side and wait.

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
   - Support archetype domain roll: +25% of XP-to-next-level per successful roll
   - State EXP earned in the response

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
