# Scene graph prototype (mile 15.5)

This folder is a **minimal working prototype** for the architecture we discussed:

- **Stone:** fixed narration + scene order + next pointers live in `scenes_mile155.json`.
- **AI voice only:** marked `ai_slots` — the model is only asked to fill those strings.
- **Validation:** slot text is checked against `canon_allowlist.json` (forbidden substrings like `Seravane`, wrong partner numbers) plus a light **name check** via `continuity_engine.validate_npc()` for capitalized words.
- **Existing work:** imports **`continuity_engine.py`** (parent folder) for registry checks and **`kenji_state.json`** (optional alignment warnings).

It does **not** replace `dm_rules_tracking.md`, `character_tracker.md`, or `npc_appearance.md` — it **consumes** them conceptually via `canon_allowlist.json` snippets and the continuity registry.

---

## Files

| File | Role |
|------|------|
| `scenes_mile155.json` | Scene graph: narration, `next`, `ai_slots` with prompts + validation rules |
| `canon_allowlist.json` | Facts + speaker one-liners + forbidden strings for this arc |
| `run_scene_graph.py` | CLI runner: prints fixed text, collects AI lines, validates, logs |
| `logs/` | Session transcripts (gitignored content optional) |

---

## Run

From **`Kenji/Game init files/scene_graph_prototype/`**:

```bash
python run_scene_graph.py --dry-run
```

Prints all **fixed** narration; no AI slots executed.

```bash
python run_scene_graph.py --skip-ai
```

Runs the graph but fills slots with `[AI SKIPPED — placeholder]` (good for CI / smoke test).

```bash
python run_scene_graph.py
```

Interactive: for each AI slot, the script prints **canon inject** + instructions, then you paste dialogue and end with a line containing only **`END`**.

If validation fails, fix and retry, or type **`ABORT`** to keep the text anyway (testing only).

```bash
python run_scene_graph.py --no-state-check
```

Skips **alignment warnings** (day/location vs prototype). The run receipt still loads `../kenji_state.json` when present for the **KENJI SNAPSHOT** block.

---

## Run receipt (proof the tool actually ran)

**Successful** runs end with **`KENJI_SCENE_GRAPH_RUN_RECEIPT`**. If the continuity pre-check fails or the graph references a missing scene id, you get **`KENJI_SCENE_GRAPH_FAILURE_RECEIPT`** instead (`RESULT: FAILED`, `FAIL_CODE`, partial `SCENES_VISITED`). That still has a unique **`RUN_ID`** and **`SCENES_FILE_SHA`** so you can prove the tool ran, even when the session did not finish.

The success receipt includes:

- **`RUN_ID`** — random UUID (new each run)
- **`SCENES_FILE_SHA`** — first 16 hex chars of SHA-256 of `scenes_mile155.json` (changes if you edit the graph)
- **`EXECUTED_AT_UTC`**, **`CLI_FLAGS`**, **`SCENES_VISITED`**, **`END_SCENE`**
- **`KENJI SNAPSHOT`** — fields read from `kenji_state.json` when the file exists
- **`HOW TO CONTINUE`** — labeled choices from `run_receipt.continuation_choices` in the JSON

The same block is appended to the session log under `logs/`.

**When you play through an AI**, paste that receipt (or the log path + `RUN_ID`) into the session. Narration alone is not proof the runner executed; an LLM can improvise prose. It cannot invent a matching **`RUN_ID`** + **`SCENES_FILE_SHA`** without you copying tool output.

---

## What this proves

1. **Story advance is deterministic** — the JSON `next` chain, not the LLM.
2. **AI is scoped** — only the strings in `ai_slots`.
3. **Hallucination is bounded** — forbidden tokens and registry name warnings catch common drift before the next scene.
4. **Your repo already had half the stack** — `continuity_engine` + `kenji_state.json` plug in naturally.

---

## Next steps (not in this prototype)

- Export **`character_tracker` / `npc_appearance`** to JSON automatically instead of hand-maintaining `canon_allowlist.json`.
- Richer validator (embeddings, LLM judge) for “only paraphrases canon.”
- Branching from real **flags** in `kenji_state.json` (not just linear `next`).
- GUI hook from `kenji_gui.py` or `ttrpg_game_engine.py`.

---

*Prototype only — safe to delete or replace without affecting the main tracking system.*
