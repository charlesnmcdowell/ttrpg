# Combined universe — new characters & campaigns

Every **new PC** belongs to the **same combined realm** as Amaris and Kenji. Prior campaigns are **established lore**; each new campaign **adds** a location, cast, and story that future characters inherit as background texture (rumor, history, geography) unless the DM brings them into play directly.

---

## 1. Lore stack (how canon accumulates)

| Layer | Source | Rule |
|-------|--------|------|
| **Realm foundation** | `shared_world_continuity.md`, `realm_lore_registry.json` | Shared laws, tone, and registry of campaigns. |
| **Completed / active arcs** | `Amaris/.../amaris_state.json`, `Kenji/.../kenji_state.json`, story `.md` files | Facts-at-a-glance + narrative; **treat as true** for new PCs unless you explicitly retcon. |
| **This PC’s campaign** | New folder + `character_world_state.json` (from template) | Unique background; **new** settlement / region / faction slice; becomes lore for the **next** PC when you snapshot or summarize. |

**New characters do not replace prior events.** They inherit them as **world history** and **distant news**, then play their **own** arc—often starting somewhere new on the map.

---

## 2. Character creation → what gets generated

When you create a new character, **define or generate** (yourself, AI, or a tool later):

1. **Personal background** — ties, wounds, goals; must not require being the Chosen One of Amaris’s or Kenji’s plot unless you want that crossover.
2. **A new anchor on the map** — named place (village, quarter, monastery, ship route, etc.) with **terrain, tone, and distance** from known regions (e.g. weeks from Varenholm, or “eastern frontier past Thornfield”). Prefer a **word map**: two lines in **`new_region`** — **from_worlds_middle** (vs “girdle” / heartland) and **from_crown_realm** (vs the largest kingdom); see **`shared_world_continuity.md`** § *Description map (words)*.
3. **Main cast** — 3–8 named NPCs with roles (ally, foil, merchant, priest, rival) and **one-line voices**.
4. **Quest spine** — inciting incident → midpoint twist → crisis → resolution; enough for dialogue and scene prompts.
5. **Dialogue & scene hooks** — short lines or bullet beats for intros, rumors, and confrontations (can live in the state file or a sidecar `campaign_dialogue.md`).

Copy `templates/new_character_campaign.template.json` to  
`<NewPC>/Game init files/character_world_state.json` and fill it as you play.

---

## 3. What new PCs “know” about Amaris & Kenji

Default assumption: **not much detail** unless their background justifies it.

- **Common folk** in a new region might know: big cities have an **Academy**, nobles and **Council** exist, **war in the west** or “trouble on the moors” as vague rumor—tune to taste using `kenji_state.json` / story files.
- **Frontier** PCs might know **Thornfield**-scale gossip: forests, ley strangeness, “a village east had a bad season”—without naming Amaris.
- **Direct crossover** is optional: use `inherited_lore.player_knowledge` in the template to lock what **this** PC has heard.

Distance and slow news are your friends; the combined universe stays consistent without forcing every PC into every plotline.

---

## 4. When a campaign ends (becoming lore for the next PC)

1. Snapshot final `character_world_state.json` (or export from your engine).
2. Add or update a **short** entry in `realm_lore_registry.json`: region name, status, pointer to state + story files.
3. Optional one-paragraph **epilogue** in a `story.md` for that PC (like Amaris’s epilogue)—future DMs read the registry + epilogue, not necessarily every JSON field.

The **next** new character’s template should list these sources under `inherited_lore.sources` so the stack stays explicit.

---

## 5. Folder suggestion

```
TTRPG/
  shared_world_continuity.md
  universe_campaign_framework.md   ← this file
  realm_lore_registry.json
  templates/new_character_campaign.template.json
  Amaris/...
  Kenji/...
  <NewCharacterName>/
    Game init files/
      character_world_state.json
      story.md                    (optional, long-form)
      dm_rules_*.md               (optional)
```

---

## 6. Automation later

If you add scripts or an LLM workflow for “roll a new region,” keep the **same fields** as the template JSON so generated content drops into `character_world_state.json` without rework.

---

## 7. Player-facing vs DM-only

- **Players** of a new PC should get **background, local region, and local NPCs** — not a dump of `kenji_state.json` or unpublished twists. Default: distant events are **rumors** (“trouble on the west moors,” “the Academy’s been odd”) unless `inherited_lore.player_knowledge` says something specific.
- **DM / solo prep** may use full `*_state.json`, novels, and `dm_rules` — treat as **spoilers** until revealed in play.
- **Solo play:** You are both DM and player; still use `player_knowledge` so “what the character could plausibly believe” stays clear.

---

## 8. Retcons (when prior canon must change)

1. **Prefer not to** — add new facts that fit (e.g. “another village east of Thornfield”) before erasing old ones.
2. If you must change something: **edit the relevant story `.md` and/or state JSON**, then add a short **`supersedes_note`** on the **registry entry** in `realm_lore_registry.json` (or a dated bullet in this file under **Changelog** below).
3. **Update `shared_world_continuity.md`** if the change is realm-wide (law, geography, a major faction).

### Changelog

_(Add dated one-line entries here when you retcon something major.)_

---

## 9. Merging with StoryEngine (`kenji_state` schema)

**`ttrpg_game_engine.py` (StoryEngine)** now **preserves unknown top-level JSON keys** on load/save (e.g. `universe`, `inherited_lore`, `character`, `new_region`, `shared_world`). They are stored internally as **`extra_json`** and merged back into the file when you call **`save_json()`** or export via **`to_dict()`**.

**Practical approach:**

1. Start from **`Kenji/Game init files/kenji_state.example.json`** (or your last save) for the mechanical shell.
2. Paste or merge fields from **`templates/new_character_campaign.template.json`** into the same file as the engine save — custom blocks survive round-trips through the GUI.
3. You can still mirror critical bullets in **`narrative_notes`** for quick AI brief visibility (optional duplicate).

`python ttrpg_game_engine.py brief` includes an **“Extended state”** section when `extra_json` is non-empty.
