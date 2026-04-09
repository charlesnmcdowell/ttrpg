# Kenji TTRPG — Game init files

## Story continuity (read this first)

**Anyone assisting with this campaign—including AI—should read the fiction in order before answering questions, planning scenes, or applying mechanics:**

1. **`Kenji_story_book1.md`** — Book one (*The Gilt Conspiracy* arc through the Hollow Crown / cycle restoration).
2. **`Kenji_story_book2.md`** — Book two to date (*The Descent* → *The Sundered Gate*; tournament, Bleakmoor, ongoing plot).

Without that context, answers will miss character history, relationships, what the world has already seen, and what is still secret in the DM material.

**Cursor / AI:** The repo includes **`.cursor/rules/kenji-ttrpg.mdc`** (parent `Kenji` folder) so assistants are nudged to read the novels first. Open the **`Kenji`** folder in Cursor for that rule to apply.

### Story engine + AI (short context)

You cannot paste 500k words of novels into every chat. Use this loop:

1. **`kenji_state.json`** — Single source of truth for **mechanical and world variables** (time, place, HP, slots, gold, portals, squads, threat clocks, relationships, constructs). Edit after each session (or incrementally during play).
2. **Narrative bridge fields** in the same JSON:
   - **`canon_pointer`** — Where the prose left off (e.g. “Book 2, Chapter 13 end”).
   - **`story_beat`** — 2–4 sentences: what just happened and what is about to happen.
   - **`narrative_notes`** — Bullet strings for anything else the AI must remember (e.g. “Senna is charm-immune”).
3. **Export a pasteable brief:** From the `Game init files` folder run:
   ```bash
   python ttrpg_game_engine.py brief
   ```
   (Uses `kenji_state.json` by default.) Or: `python ttrpg_game_engine.py brief kenji_state.example.json`
4. **Output:** Prints markdown to stdout and writes **`AI_CONTEXT.md`** next to the state file. Paste **`AI_CONTEXT.md`** (or the terminal output) at the **start of an AI DM session** so the model has accurate numbers without rereading the whole saga.
5. **Novels remain canonical** for voice, revealed plot, and tone; the engine state must not contradict them—if it does, fix the JSON.

---

## Run order (humans and tools)

| Step | What | Purpose |
|------|------|---------|
| 1 | **`dm_rules_tracking.md`** | **Single DM volume:** mechanics, rests, EXP, worldbuilding tone, DM-secret references (books 1–2), combat JSON definitions, Book 2 checkpoints / tracking (including auto-extracted blocks). |
| 2 | `kenji_state.example.json` | Copy to `kenji_state.json`, edit each session. Load: `StoryEngine.load_json("kenji_state.json")` or `save_json()` after changes. |
| 3 | **`ttrpg_game_engine.py`** | **`python ttrpg_game_engine.py brief`** — generates **`AI_CONTEXT.md`** + stdout. **`dashboard()`** between scenes. Self-tests: `python ttrpg_game_engine.py` (story + combat) or `python ttrpg_game_engine.py combat-only`. |
| 4 | `SESSION_TEMPLATE.md` | Duplicate per session for notes (optional). |

**Python:** See `requirements.txt` (stdlib only). On Windows, if validation prints fail on emoji, set `PYTHONIOENCODING=utf-8` or use a UTF-8 terminal.

---

## Save file convention

| File | Role |
|------|------|
| `kenji_state.example.json` | Checked-in **template** aligned with end of `Kenji_story_book2.md` (post-tournament snapshot). Includes `canon_pointer`, `story_beat`, `narrative_notes`. |
| `kenji_state.json` | **Your live save** (copy from example; add to `.gitignore` if you use git). Not created by default—create when you start tracking digitally. |
| `AI_CONTEXT.md` | **Generated** by `python ttrpg_game_engine.py brief` — paste into AI chats; optional gitignore. |

---

## File roles (quick)

| File | Role |
|------|------|
| `Kenji_story_book1.md` / `Kenji_story_book2.md` | Canon story so far (player-facing prose). |
| `dm_rules_tracking.md` | All DM rules, tracking norms, worldbuilding, spoilers, combat definitions, Book 2 stat snapshots. |
| `_strip_dm_notes.py` | Maintenance: moves DING blocks from `Kenji_story_book2.md` into the Book 2 section of `dm_rules_tracking.md`. |
