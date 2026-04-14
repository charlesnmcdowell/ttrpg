# Amaris — The Crawling Dark

Campaign **complete** (eastern frontier: Thornfield, Greenveil, Briarstone). This folder is part of the **combined TTRPG universe** with Kenji and future PCs.

## Universe & lore (read first)

Parent folder hub: **`../README.md`** — combined realm, lore registry, new-character template.

| Doc | Purpose |
|-----|---------|
| `../shared_world_continuity.md` | How this region relates to Varenholm / Bleakmoor (distance, news). |
| `../universe_campaign_framework.md` | New PCs inherit prior arcs as lore; player vs DM knowledge. |
| `../realm_lore_registry.json` | Registry entry for Amaris + other campaigns. |

## This campaign — Game init files

| File | Role |
|------|------|
| **`Game init files/amaris_state.json`** | Post-campaign snapshot (mechanical + narrative bridge). |
| **`Game init files/amaris_story.md`** | Canon prose / epilogue. |
| **`Game init files/dm_rules_amaris_campaign.md`** | DM rules, economy, mechanics. |
| **`Game init files/dm_reference_crawling_dark.md`** | Reference (older timelines may be alternate vs epilogue — check story file for canon). |
| **`Game init files/campaign_manifest.json`** | Points shared **music** + **engine** at the Kenji install (see `../Kenji/Game init files/README.md`). |

**Live dashboard:** `Game init files/run_live_dashboard.bat` (or `python kenji_gui.py` with manifest path per Kenji README).

## Adding a new hero

Do **not** overwrite Amaris files. Start a **new folder** under `TTRPG/`, copy `../templates/new_character_campaign.template.json`, and add a row to `../realm_lore_registry.json` when ready.
