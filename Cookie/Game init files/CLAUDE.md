# Instructions for AI assistants (Cookie — Game init files)

This is Cookie's campaign folder. **All shared DM systems live in Kenji's Game init files.** Read those before running any scene.

---

## Shared systems — READ FIRST

Before doing anything, read `Kenji/Game init files/dm_rules_tracking.md` — specifically the **AVAILABLE SYSTEMS** table at the top. It lists every existing system and where to find it. **Do not build new systems without checking that table.**

Key shared files (all paths relative to the TTRPG root):

| What | Where |
|------|-------|
| **DM rules** (skill prerolls, economy, combat, NPC lifecycle, poisons, auras, character creation) | `Kenji/Game init files/dm_rules_tracking.md` |
| **Game engine** (time, currency, inventory, schedule, buffs, dashboards, skill rolls) | `Kenji/Game init files/ttrpg_game_engine.py` |
| **World calendar** | `Kenji/Game init files/world_calendar_lore.md` |
| **NPC name bank** | `Kenji/Game init files/npc_name_bank.md` |
| **Ankuspawn race rules + Ember Inheritance** | `ankuspawn_race.md` |
| **Campaign template** | `templates/new_character_campaign.template.json` |
| **Shared world lore** | `shared_world_continuity.md`, `realm_lore_registry.json` |

## Cookie-specific files

| What | Where |
|------|-------|
| **Campaign state** (character, story, NPCs, Ember, persistent effects, engine state) | `character_world_state.json` |
| **Reference art** | `reference_art/` |

## Quick rules

- **Scene skill preroll** — roll before narrating. See `dm_rules_tracking.md` § Scene skill preroll.
- **Economy** — 1 GP = $5,000 USD. Cookie is broke. Use CP/SP for daily commerce.
- **Time** — StoryEngine tracks day/hour. Load `_story_engine_state` from `character_world_state.json`. Display dashboard at end of every DM response.
- **NPC names** — pull from `npc_name_bank.md`. Never invent without checking.
- **Cookie's Ember** — Resonance theme. Theme-locked. Growth stage: unreliable. See `character_world_state.json` § `ember_inheritance`.
- **Cookie's flaw** — WIS 7. Impulsive, no mental defense, blacks out from alcohol. Play this honestly.
