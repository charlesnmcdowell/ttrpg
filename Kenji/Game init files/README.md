# Kenji TTRPG — Game init files

## How the game works

This campaign uses a **rules-based tracking system** to maintain continuity across sessions. The chapter prose is the canon. The tracking files are downstream artifacts that get updated after play — never the other way around.

### The core loop

1. **Before writing prose:** Read `tracking_rules.md`, then read the last 2 chapters of the active book, then read `character_tracker.md` for any NPC you're about to write.
2. **During play:** Write prose. Stop at decision points. Never speak for Kenji. Never auto-resolve combat.
3. **After play:** Update `character_tracker.md` (timestamps on every change), update `AI_CONTEXT.md` header fields, append prose to the chapter file.

### The tracking system (source of truth)

| File | Purpose | When to read |
|------|---------|--------------|
| `tracking_rules.md` | **READ FIRST every session.** 9 mandatory rules: pre-write review, timestamps, drift checks, goal timers, personality constraints, alive-must-have-goals, never delete, endgame snapshots, consolidation. | Start of every session |
| `character_tracker.md` | Source of truth for all characters >2 chapters old. Status, location, disposition, abilities, gear, goals with due dates and public_at timers. The World is also tracked here. Campaign threats with clock percentages. | Before writing any NPC |
| `npc_appearance.md` | Physical reference derived from image uploads. Includes Vigor eye-shift mechanics. DM checklist for new character introductions. | When describing any NPC physically |
| `book_1_endgame_tracker.md` | Frozen snapshot — all characters at Book 1 end (Day 13, Level 9). | Reference only |
| `book_2_endgame_tracker.md` | Frozen snapshot — all characters at Book 2 end (Day 24, Level 20). | Reference only |
| `character_tracker_example.md` | **Template** for new campaigns using this tracking system. | When starting a new campaign |

### DM rules and mechanics

| File | Purpose | When to read |
|------|---------|--------------|
| `dm_rules_tracking.md` | Cardinal rules (never speak for Kenji, never auto-resolve combat, stop at decision points, dialogue-first narrative), combat mechanics, enemy tactics, creature registry, encounter design, worldbuilding tone, environmental rules, NPC combat stat blocks. Historical DM secrets for Books 1-2 (archived). | Before running combat or encounters |
| `world_calendar_lore.md` | Calendar system, holidays, seasonal cycle, month names. | When referencing dates or seasons |
| `fraying_empire_campaign.md` | Book 4 campaign bible — 5 threats, clock management, key NPCs per threat. | When writing campaign-level content |
| `iron_crown_war_campaign.md` | Book 3 campaign bible. | Reference only (Book 3 complete) |

### Story files

| File | Purpose |
|------|---------|
| `Kenji_story_book1.md` | Book 1 — *The Gilt Conspiracy* (condensed summary) |
| `Kenji_story_book2.md` | Book 2 — *The Expedition* through *The Sundered Gate* (full manuscript) |
| `Kenji_story_book4.md` | Book 4 — *Fraying Empire / The Ronin* (combined manuscript through latest chapter) |
| `Book 4/Chapters/` | Per-chapter edit surface for Book 4 |

### AI context (short-context sessions)

| File | Purpose |
|------|---------|
| `AI_CONTEXT.md` | Generated state brief. Contains: tracking system file index, pre-write checklist, canon pointer, mechanical stats, relationships, extended state (DM-private data, Vigor tracking, Soul Nexus registry, equipment, narrative notes). Paste at start of AI sessions for context. |

The AI_CONTEXT file is large but most of it is stable reference (stats, relationships, narrative notes). The header section (tracking file index, pre-write checklist, canon pointer, time/place) is the part that changes each session.

### Session workflow

| Step | What to do |
|------|-----------|
| 1 | Read `tracking_rules.md` (if not loaded this session) |
| 2 | Read last 2 chapters of active book (prose = canon for recent events) |
| 3 | Read `character_tracker.md` for any NPC you're about to write |
| 4 | Check goal timers — any `due_date` past current date → resolve before writing |
| 5 | Check drift — any character `last_updated` >2 days behind → re-read source chapters |
| 6 | Play the session |
| 7 | Update `character_tracker.md` (timestamps on every change) |
| 8 | Update `AI_CONTEXT.md` header (canon pointer, time/place, where we left off) |
| 9 | Copy `SESSION_TEMPLATE.md` for session notes (optional) |

---

## Combined universe (parent folder)

This campaign is **one arc in a shared realm** with the Amaris campaign and any future PCs. Realm-wide policy, lore registry, and new-character templates live one level up:

- `../../README.md` — hub for `TTRPG/` (universe docs, folder map, how to start a new hero)
- `../../shared_world_continuity.md` — how regions relate; Amaris vs Kenji distance and news
- `../../universe_campaign_framework.md` — inheriting lore; adding a new location + quest spine
- `../../realm_lore_registry.json` — index of campaigns
- `../../templates/new_character_campaign.template.json` — blank state for new heroes

---

## Optional tools (legacy / dashboard)

These files support the Python GUI dashboard and game engine. They are **not required** for the tracking system but remain available for live dashboard use.

| File | Purpose |
|------|---------|
| `kenji_state.json` | Live save file for the Python engine/GUI. Updated independently of the tracking system. |
| `ttrpg_game_engine.py` | Story engine — `python ttrpg_game_engine.py brief` generates AI_CONTEXT.md from the JSON. |
| `kenji_gui.py` | Live dashboard GUI. Loads any campaign via `campaign_manifest.json`. |
| `campaign_manifest.json` | Campaign root config for the GUI (state file, music, engine path). |
| `_dm_turn.py` | DM turn processing script. |
| `_strip_dm_notes.py` | Moves DING blocks from story files into dm_rules_tracking.md. |
| `requirements.txt` | Python dependencies (stdlib only). |
| `build_exe.bat` | Windows build script for GUI executable. |

### Running the dashboard

**Default (Kenji):** `python kenji_gui.py` from this folder.
**Other campaign:** `python kenji_gui.py --campaign "C:\path\to\Campaign\Game init files"` or set `TTRPG_CAMPAIGN_DIR`.

---

## Obsolete files

| File | Status |
|------|--------|
| `kenji_tracking_OBSOLETE.md` | Old-style character tracking. Superseded by `character_tracker.md`. Kept for historical reference. |
| `Kenji_story_book1_legacy_full_manuscript.md` | Full Book 1 manuscript (legacy). Condensed version is `Kenji_story_book1.md`. |

---

*Last updated: Ashmere 24, 1247 AR (Book 4, Chapter 5 end).*
