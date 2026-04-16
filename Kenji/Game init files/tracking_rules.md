# Tracking Rules — Kenji TTRPG

These rules govern how character state, goals, and world progression are tracked across sessions. They are mandatory and override ad-hoc judgment.

---

## Rule 1 — Pre-Write Chapter Review

Before committing any new prose or DM narration, read the last 2 chapters of the active book. The chapter prose is canon. Tracking files are summaries that may lag behind.

If tracking and prose conflict: **prose wins for the last 2 chapters.** For anything older than 2 chapters, **tracking wins** (because tracking should have been updated by then via Rule 3).

---

## Rule 2 — In-Game Date Timestamps

Every character change (disposition, gear, ability, goal, status) must be timestamped with the in-game date (e.g., Ashmere 26, 1247 AR). This ties every tracked change to the chapter it happened in and enables drift detection.

---

## Rule 3 — Drift Check

At the start of any game-continuation turn, compare the current in-game date against each tracked character's `last_updated` date. If the gap is **greater than 2 in-game days**, that character's entry is potentially stale. Review the chapters spanning that gap before referencing the character in new prose.

This also applies to goals: any goal whose `due_date` has passed but whose `status` is still `in_progress` must be resolved.

---

## Rule 4 — Goal Timers (Due Date + Public Date)

Every active goal has two timers:

- **`due_date`**: when the goal completes in the world, whether Kenji is present or not.
- **`public_at`**: when the information becomes available to reference in the story. NPCs can mention it, Kenji can encounter its consequences.

**Check per turn:**
- Current date >= `due_date` → goal completes. Run `completion_effects`. Flip status to `complete`. Write `conclusion`.
- Current date >= `public_at` → fact is live. NPCs can reference it. No need to narrate how the information traveled — the reader will infer it naturally because enough time has passed.

Goal timers are set using common-sense estimates:
- Travel/delivery: distance / mode-speed + buffer
- Investigation: 1-3 weeks
- Political moves: weeks to months
- Recovery/healing: days to weeks
- Combat: same scene
- Long arc: multiple chapters

---

## Rule 5 — Alive Characters Must Have Goals

Every character with `status: alive` must have at least one active goal. If a character is alive and has no goal, **flag it** — they need either a new goal or a status change.

- **alive** = actively tracked, must have goal(s)
- **MIA** = no longer relevant to Kenji's current story. Goals paused. Can reactivate later.
- **dead** = no goals needed. Entry preserved for reference.

---

## Rule 6 — Never Delete, Only Update

Character data is never deleted. Fields are updated in place:
- Physical features change → update the field, timestamp the change
- Gear changes → update the field
- Disposition shifts → update the field
- Ability gained/lost → update the field
- Goal completes → write conclusion, mark complete, leave in history
- Character dies → change status to dead, leave all other data intact

Completed goals stay in the tracker with their conclusion. They become the historical record.

---

## Rule 7 — Endgame Snapshots

At the end of each book, create a file called `book_#_endgame_tracker.md` that captures the final state of every tracked character at that book's close:
- All current field values (appearance, disposition, abilities, gear, status)
- All goals with their conclusions
- Summary of where they are and what they're doing

This file is frozen — never edited after creation. It becomes the canonical reference for "where was everyone at the end of Book X" and prevents needing to re-read entire books.

---

## Rule 8 — Personality Constrains Behavior

Each character has a personality profile that constrains their behavior in new prose. The DM must respect these constraints:

- A pragmatic soldier does not interrogate a lover about their powers
- A skeptical academic does probe institutional risks
- A confident woman who knows her body does not agonize over sleeping with someone
- A pious character does apply moral scrutiny

If a scene requires a character to act outside their personality profile, there must be a specific in-story trigger justifying it. "The aura made them act differently" is not sufficient on its own — the aura amplifies existing personality, it does not replace it.

Not every female NPC is a private investigator. Variety is mandatory.

---

## Rule 9 — Consolidation Pass Trigger

When a new chapter is written or played, run a consolidation pass on the chapter that just aged out of the 2-chapter window:
- Extract any permanent facts (gear, abilities, relationships, goals opened/closed)
- Update existing tracker entries with timestamps
- Add new entries for new characters
- Remove nothing — only update

This keeps drift at zero by construction.

---

## File Structure

The tracking system uses these files:

| File | Purpose |
|------|---------|
| `tracking_rules.md` | This file. The operating rules. |
| `character_tracker.md` | Per-character entries: appearance, disposition, abilities, gear, status, goals |
| `npc_appearance.md` | Detailed physical reference (image-derived). Cross-referenced by tracker. |
| `world_state.md` | Calendar, faction status, global threats, kingdom state |
| `book_#_endgame_tracker.md` | Frozen snapshot at end of each book |
| `AI_CONTEXT.md` | Index file. Current date, current scene, pointers to all tracking files. |

---

*These rules are permanent. They do not get overridden by vibes, time pressure, or "I'll update it later."*
