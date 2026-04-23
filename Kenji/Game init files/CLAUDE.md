# Instructions for AI assistants (Kenji — Game init files)

This folder holds live campaign tooling and trackers. Read **`tracking_rules.md`** before editing tracked prose or state.

---

## Machine receipts — NON-NEGOTIABLE

The following markers mean **output produced by a real Python process on the player’s machine**, not LLM prose:

- **`KENJI_ARC_POINTER_RUN_RECEIPT`** / **`KENJI_ARC_POINTER_FAILURE_RECEIPT`** — from `run_arc_pointer.py`
- **`KENJI_ARC_POINTER_STAMP`** / **`KENJI_ARC_POINTER_STAMP_FAIL`** — one-line proof from `run_arc_pointer.py --stamp` (same `RUN_ID` + `STATE_FILE_SHA` + `ARC_FILE_SHA` contract as the full receipt)
- **`KENJI_SCENE_GRAPH_RUN_RECEIPT`** / **`KENJI_SCENE_GRAPH_FAILURE_RECEIPT`** — from `scene_graph_prototype/run_scene_graph.py`

A genuine receipt includes fields such as **`RUN_ID`**, **`STATE_FILE_SHA`**, **`ARC_FILE_SHA`**, **`SCENES_FILE_SHA`**, **`EXECUTED_AT_UTC`**, etc. Those values are **observable** only after a script run (stdout or a file under `logs/`).

### Rules

1. **Do not fabricate receipts.** Never invent or type a `RUN_ID`, any `*_FILE_SHA`, or a full receipt banner to “be helpful,” simulate success, or show an example **unless** the user explicitly asked for a **hypothetical** block and you label every line as **example-only, not proof** (and you still must not mimic a real `RUN_ID` format in a way that could be mistaken for a run).
2. **If a receipt is required**, run the tool in the **integrated terminal** from the correct working directory and **copy only the actual stdout** (or the contents of the log file the script wrote). If terminal execution is unavailable or denied, **say that** and tell the user exactly which command to run; do not substitute fake output.
3. **If the user pasted a receipt**, you may interpret it (arc slug, hashes, flags). You must not “refresh” or “re-run” it by generating a new receipt in chat.
4. **Reading** `logs/*.txt` or `scene_graph_prototype/logs/*.txt` to quote an existing receipt is allowed **only** when those files exist and you actually read them via the editor tools — still do not invent new IDs.

### Commands (reference)

From **`Game init files/`** (this directory):

```bash
python run_arc_pointer.py
python run_arc_pointer.py --peek 40
python run_arc_pointer.py --stamp --no-log
python _dm_turn.py receipt
```

From **`Game init files/scene_graph_prototype/`**:

```bash
python run_scene_graph.py --dry-run --skip-ai
```

---

## Engine brief

- `python ttrpg_game_engine.py brief` — prints AI brief to stdout (loads `./kenji_state.json` by default).
- `python _dm_turn.py brief` — writes **`AI_CONTEXT.md`** to disk from the same brief source.

`kenji_state.json` is gitignored; **`active_arc`** and other extra keys live there and round-trip through `StoryEngine` / `_dm_turn.py`.
