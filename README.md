# TTRPG — combined universe

This folder holds **one shared fantasy realm** played across multiple characters and campaigns. Stories can stay in separate regions; **canon accumulates** so later heroes inherit earlier arcs as lore (rumor, history, geography—not always direct crossover).

## Universe docs (read order)

| Document | Purpose |
|----------|---------|
| **`shared_world_continuity.md`** | Realm rules, travel matrix, **word description map** (world’s “middle” + Crown realm), Amaris vs Kenji regions. |
| **`universe_campaign_framework.md`** | How **new PCs** inherit prior lore, add a **new location**, cast, quests, and dialogue at creation. |
| **`realm_lore_registry.json`** | Machine-readable index of campaigns—**extend** when you add or finish a hero. Optional **`calendar`** block for named era / notes. |
| **`templates/new_character_campaign.template.json`** | Copy to `<NewPC>/Game init files/character_world_state.json` for a new character. |

## Campaign folders

| Path | Character / notes |
|------|---------------------|
| **`Amaris/`** | Amaris — eastern frontier (Thornfield, Greenveil, Briarstone). Campaign complete; see `Game init files/amaris_state.json` and `amaris_story.md`. |
| **`Kenji/`** | Kenji — heartland / west (Varenholm, Duskfen, Bleakmoor, Sundered Gate). Live fiction + TTRPG engine lives under `Kenji/Game init files/`. |

Shared tooling (GUI, `ttrpg_game_engine.py`, music maps) is documented in **`Kenji/Game init files/README.md`**.

**Other campaigns (e.g. Amaris):** use a **`Game init files/campaign_manifest.json`** that sets `state_file`, `music_dir`, `music_map`, and **`engine_path`** → `Kenji/Game init files` so you do **not** duplicate the engine. See **`Amaris/Game init files/campaign_manifest.json`** as an example.

**Cursor:** Open **`TTRPG`** as the **workspace root** so **`.cursor/rules/ttrpg-universe.mdc`** applies — it nudges assistants to read the registry and continuity before inventing regions. If you only open **`Kenji/`**, use **`Kenji/.cursor/rules/kenji-ttrpg.mdc`** (novel canon) instead.

**Git / backup:** Optional **`.gitignore`** ignores generated `AI_CONTEXT.md` and `*.tmp`; uncomment lines there if you want to exclude live `*_state.json` from version control (OneDrive may still sync them).

## Starting a new character

1. Read **`universe_campaign_framework.md`**.
2. Copy **`templates/new_character_campaign.template.json`** into your new folder as `character_world_state.json` and fill it (background, **new region**, main cast, quest spine, dialogue).
3. List prior state files under `inherited_lore.sources`; set **`player_knowledge`** so rumors stay believable.
4. When the campaign is established or complete, add an entry to **`realm_lore_registry.json`**.

Day counters and HP in each `*_state.json` are **per campaign**, not one global calendar, unless you explicitly sync scenes.
