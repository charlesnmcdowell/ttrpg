# Combined universe — new characters & campaigns

Every **new PC** belongs to the **same combined realm** as Amaris and Kenji. Both prior campaigns are now **complete and established lore**. The current era is **25 years after Book 4**, under the **Kingdom of Ankunyx** — a continental authority forged by the Dragon Emperor AnkuNyx (born Kenji). Each new campaign **adds** a location, cast, and story that future characters inherit as background texture (rumor, history, geography) unless the DM brings them into play directly.

**New playable race available: Ankuspawn** — children of the Dragon Emperor. See `ankuspawn_race.md` for full details.

---

## 1. Lore stack (how canon accumulates)

| Layer | Source | Rule |
|-------|--------|------|
| **Realm foundation** | `shared_world_continuity.md`, `realm_lore_registry.json` | Shared laws, tone, registry of campaigns, Kingdom of Ankunyx structure. |
| **Completed arcs** | `Amaris/.../amaris_state.json`, `Kenji/.../kenji_state.json`, `Kenji/.../book4_endgame_tracker.md`, story `.md` files | Both campaigns COMPLETE. Facts-at-a-glance + narrative; **treat as true** for new PCs unless you explicitly retcon. |
| **Race documents** | `ankuspawn_race.md` | Ankuspawn playable race — children of the Dragon Emperor. Available for new PCs. |
| **This PC’s campaign** | New folder + `character_world_state.json` (from template) | Unique background; **new** settlement / region / faction slice; becomes lore for the **next** PC when you snapshot or summarize. |

**New characters do not replace prior events.** They inherit them as **world history** and **distant news**, then play their **own** arc—often starting somewhere new on the map.

---

## 2. Character creation → starter campaign generation

Every new character gets a **complete starter campaign** (levels 1–10) generated from their background. This is not optional flavor text — it is the system that turns a character sheet into a playable world. The starter campaign is designed to introduce the player to the existing world lore through the lens of their character’s unique perspective, while permanently expanding the game world with new content.

### What the player provides

The player defines **three things** at character creation:

1. **Background** — race, class concept, where they grew up, who they lost, what shaped them. Does not need to connect to Amaris or Kenji unless the player wants that crossover.
2. **Personal goal** — one sentence describing what the character wants most. This becomes the campaign’s central objective. Examples: “Open a school for war orphans,” “Find my father’s killer,” “Earn a title and land,” “Cure the plague in my village,” “Become the greatest smith in the kingdom.”
3. **Starting region preference** — frontier, heartland, coast, mountains, underground, or “surprise me.” This guides where the 3 new locations are placed on the map.

### What gets generated (the starter campaign package)

From those three inputs, the DM (or AI) generates a full **Starter Campaign Package** containing:

**A. Three new locations** that expand the world map permanently:

- **Home base** — where the character begins. A settlement, holdfast, ship, or camp tied directly to the character’s background. This is their anchor. It has NPCs they know, a place to sleep, and a reason to defend it.
- **Adventure site** — a dangerous location within 1–3 days’ travel of home base. A ruin, dungeon, corrupted forest, bandit fortress, cursed mine, etc. This is where the campaign’s main threat operates. The character must go here to confront the antagonist.
- **Discovery location** — a hidden or unknown place that the character uncovers during the campaign. It connects to existing world lore — an old outpost from the Iron Crown War, a forgotten construct portal, a Pallid March burial ground, an Ankuspawn settlement, a pre-kingdom ruin. This location is how the starter campaign introduces the player to the broader world history without dumping exposition.

All three locations are added to `realm_lore_registry.json` and `shared_world_continuity.md` at campaign creation. They persist forever. Future characters can visit them, find them changed, or discover what happened there.

**B. A main antagonist** (levels 5–8) designed around the character’s background:

The antagonist is the force that threatens the character’s personal goal. They are not a world-ending threat — they are a regional menace scaled for levels 1–10. The antagonist’s motivation should mirror or invert the character’s goal, creating personal stakes.

- If the character wants to build something (school, farm, business) → the antagonist wants to destroy or corrupt that thing
- If the character wants to find someone → the antagonist is hiding them, or hunting the same person
- If the character wants recognition → the antagonist is a rival claiming the same prize
- If the character wants to cure/heal → the antagonist is the source of the affliction, or profits from it

The antagonist operates from the adventure site and has 3–5 lieutenants or minions that create encounters across all three locations. When the antagonist is defeated, their threat ends — but the consequences of their actions may ripple into future campaigns.

**C. The personal goal as campaign spine:**

The character’s stated goal is achievable by level 8–10. The campaign is structured so the character **gets what they want early** (by level 5–6) and then **must defend it** from the main antagonist for the remainder. This creates emotional investment: you have the thing, now fight to keep it.

- **Levels 1–3:** Arrive at home base. Meet the cast. Discover the goal is within reach but something stands in the way (the antagonist’s influence, a local problem, a missing resource).
- **Levels 4–6:** Pursue and achieve the goal. The character gets what they wanted — the school opens, the killer is found, the land is granted, the cure works. But achieving it draws the antagonist’s attention.
- **Levels 7–9:** The antagonist strikes back. The thing the character built or found is under direct threat. The adventure site becomes the focus. The character must go on the offensive.
- **Level 10:** Confrontation at the adventure site. The antagonist is defeated. The character’s goal is secured permanently. The discovery location reveals its connection to the wider world — a hook toward regional or continental campaigns if the player continues.

**D. Main cast** — 5–8 named NPCs spread across the three locations:

- 2–3 at home base (ally, merchant, mentor — people the character cares about)
- 1–2 at the adventure site (captive, informant, or neutral party caught in the antagonist’s web)
- 1–2 connected to the discovery location (old guard, hermit, or someone who remembers the world before the kingdom)
- The antagonist + 1 lieutenant

Each NPC has a role, a want, and a one-line voice hook. At least one NPC should have a plausible connection to existing world lore (knew a companion of Kenji’s, served in the coalition, heard rumors about the Academy, trades in construct-made goods, etc.). This NPC is the **lore bridge** — through them, the player learns about the world naturally.

**E. Inherited lore integration:**

The starter campaign is set in the Kingdom of Ankunyx, 25 years after Book 4. The three new locations exist within that world. The campaign must specify what the character plausibly knows about the kingdom (see § 3 below) and plant at least one **lore seed** — a detail, rumor, or encounter that connects to an existing unresolved thread (the Anku Conspiracy, a missing Ankuspawn, a malfunctioning construct portal, an old companion’s legacy). The lore seed does not need to be followed — it is there for the player who wants to dig deeper after the starter campaign ends.

### After the starter campaign (level 10+)

At level 10, the character has a secured home base, a defeated antagonist, three locations on the map, and a lore seed pointing toward bigger things. From here they can enter **regional campaigns** (the default continuation) or pursue whatever thread caught their interest. The starter campaign package becomes permanent world history — snapshot to `character_world_state.json`, update the registry, and the next new character inherits it all.

Copy `templates/new_character_campaign.template.json` to `<NewPC>/Game init files/character_world_state.json` and fill it as you play.

---

## 3. What new PCs “know” about Amaris & Kenji (25 years later)

Default assumption: **everyone knows the kingdom exists.** Detail scales with proximity and social class.

- **Common folk** everywhere know: the **Kingdom of Ankunyx** is the continental authority, the **Dragon Emperor** united the territories after a great war, **dragons are protected** by law, **vampires are citizens**, **orc mercenaries** keep the peace. The Academy and Mage Council still exist as institutions. The Emperor disappears for long stretches — some wonder if he's even real anymore.
- **Frontier** PCs (Thornfield-scale) might know the kingdom exists as a distant fact — “the Dragon Emperor's law” — without understanding the politics. They've never seen a construct or a portal. Amaris is a local legend at best; Kenji is a myth.
- **Heartland** PCs know the kingdom intimately: stewards, portal network, construct patrols, the Academy. They may know the Dragon Emperor's name. They do NOT know about the Soul Nexus, Ember, or the companions — that's deep inner-circle knowledge.
- **Ankuspawn** PCs carry their own unique knowledge layer: they may or may not know their father's identity. See `ankuspawn_race.md` for knowledge-level options at character creation.
- **Direct crossover** with AnkuNyx himself should be exceedingly rare — reserved for world-shaking narrative moments. His stewards, constructs, laws, and legacy are everywhere. The man himself is not.

New PCs awaken in this world the same way Amaris did — thrust into existence with the world already in motion around them. The Kingdom of Ankunyx is just how things are. The five threats are history. The Dragon Emperor is a legend who may or may not still walk the earth.

---

## 4. Campaigns are character-agnostic

**Any character can play any campaign.** Campaigns are world content — threat chains, mysteries, political crises — not character content. They exist in the world regardless of who is playing. When a new PC enters the world, every unresolved campaign is available to them based on geography and circumstance.

**Prior player characters exist as NPCs.** When you play a new character, all previous PCs persist in the world at their last known state. They are NPCs now. You can encounter them, talk to them, trade with them, or ignore them. They have their own lives, families, and problems. They are not quest-givers by default — they are people.

**Canonical examples:**

- **Amaris’s spider campaign** — She didn’t finish it. Kenji stumbled into the same territory (Millhaven) during Book 4 and started solving her unfinished threat chain. Amaris was still there on her farm, living her life. She became one of Kenji’s lovers. The campaign content didn’t care which player engaged with it.
- **Kenji as NPC** — If a new character plays in the Kingdom of Ankunyx, Kenji exists as a wandering, womanizing Dragon Emperor. You could run into him. He’d be an NPC — impossibly powerful, charismatic, and then gone again. Amaris exists on her farm near Thornfield, 25 years older, with Ankuspawn children in their 20s, a husband who bore her no children, and a quiet life.

**Every campaign must define explicit success and failure states at creation.**

- **Success state** = resolving the campaign’s central threats. The completing player gains power, fame, and permanent world-state changes.
- **Failure state** = any single threat overwhelming the region/world. The campaign is lost. The world suffers severe ramifications (territories fall, populations die, the map redraws).

**The campaign supersedes the character.** A player’s death or absence does NOT end the campaign. The world continues. The threats continue. The clocks continue. Other players from other campaigns can enter the same world and attempt to finish what was started — or fail trying. The world exists before, during, and after any individual player’s story.

---

## 5. Campaign categories

### Regional campaigns (standard)

The default. A threat chain rooted in a specific geographic area — a town, a forest, a coastline. New players start here. The inciting incident is local, the stakes escalate, and the resolution changes that region permanently. Amaris’s Greenveil campaign and Kenji’s Books 1-2 are regional campaigns. A player can stumble into one just by being in the right place.

### Continental campaigns (advanced)

A threat chain that spans multiple regions and requires the player to travel, build alliances, and manage logistics across the map. Kenji’s Book 3 (Iron Crown War) and Book 4 (The Fraying Empire) are continental campaigns. These require an established character with resources, reputation, and allies. A brand new PC cannot walk into a continental campaign — they need to have played through enough regional content to be ready.

### Kingdom-spanning campaigns (elite — NEW)

A new category. Kingdom-spanning campaigns are **not meant for new players**. They require a character who is both **strong enough** and **knowledgeable enough** to discover and engage with threats that operate across the entire kingdom, hidden within its institutions, protected by its most powerful figures.

**The Anku Conspiracy** is the first kingdom-spanning campaign.

**What makes it different from continental:**

- **It is not geographically anchored.** There is no "go to this region" trigger. The conspiracy operates everywhere — the cult recruits in every city, the elixirs sell in every market, the Ankuspawn are scattered across the entire kingdom.
- **It requires discovery, not arrival.** A regional campaign starts when you walk into the village. A kingdom-spanning campaign starts when you **learn something you weren’t supposed to know**. You can live your entire adventuring career in the Kingdom of Ankunyx and never encounter the Anku Conspiracy — unless you meet the right person and ask the right question.
- **The antagonist is structurally protected.** Nyx is the Dragon Emperor’s wife. The kingdom is named after her. She runs a legitimate institution. She has political immunity that no regional warlord or continental threat ever had. You can’t just kick down a door — you have to navigate power structures that were designed to be unkickable.
- **It coexists with other campaigns.** A player doing a regional campaign in Stormhaven might hear elixir rumors and never follow up. A player doing a continental campaign might encounter a cult member and survive without understanding what they saw. The kingdom-spanning campaign is always running in the background. It activates when the player is ready.

**Trigger sequence for The Anku Conspiracy:**

1. **Find a mother.** The player encounters one of Kenji’s ex-lovers — Pip at her inn, Amaris on her farm, Sera at port, or any of the scattered companions. This can happen naturally during any other campaign.
2. **Get the quest.** The mother mentions a missing child — an Ankuspawn son or daughter who hasn’t come home or sent word. The player agrees to look.
3. **Search and encounter.** While investigating the missing Ankuspawn, the player runs into a **member of the Cult of Anku** — and survives the encounter. This is the hard part. Cult members are Level 30+ specialists who kill anyone who knows too much. Surviving this encounter is the proof that the player is strong enough to engage with the campaign.
4. **The conspiracy opens.** From this point, the player has enough thread to start pulling — the cult, the Academy, the elixirs, the prison, Nyx herself. How deep they go and what they do with the knowledge is entirely up to them.

**HARD RULE — Invisible to Kenji:** If the active PC is Kenji/AnkuNyx, this campaign cannot be discovered or solved. Cult members are indistinguishable from Bane of Eve and God Emperor encounters — no roll, no check, no magic detection separates them. Nyx's operations look like normal Lich-wife behavior to her husband, and she keeps him physically distracted during every visit. Kenji doesn't track his scattered children, so disappearances don't register. The conspiracy was built inside his blind spots. It takes a *different* character to see it.

**HARD RULE — "Just tell Kenji" is a trap:** If a player character warns Kenji or Kenji confronts Nyx for any reason, Nyx activates the nuclear option — full Ember nullification against Kenji. Without Ember he's a Level 40 charming rogue with INT 9, stats below 20, no Soul Nexus, no regeneration, no dragon form, no Vigor (all perks are Ember-based). She puts him in a cell. Sex without Ember protection makes him her thrall. The Dragon Emperor becomes a puppet. **Warning Kenji makes things infinitely worse.** The player must solve this without relying on Kenji's power — because his power has an off switch and Nyx is holding it. Kenji is 100% Ember-dependent after 25 years of never training anything else. His children are young enough to adapt. He is not.

**If the player is not strong enough to survive step 3, the campaign does not activate.** They die, or they escape without understanding what happened, or the cult cleans up and moves on. The conspiracy remains hidden. The next character can try again.

---

**When a campaign ends** (becoming lore for the next PC):

1. Snapshot final `character_world_state.json` (or export from your engine).
2. Add or update a **short** entry in `realm_lore_registry.json`: region name, status, pointer to state + story files. Note whether the campaign ended in **success** or **failure** — the outcome shapes the world the next player inherits.
3. Optional one-paragraph **epilogue** in a `story.md` for that PC (like Amaris’s epilogue) — future DMs read the registry + epilogue, not necessarily every JSON field.

The **next** new character’s template should list these sources under `inherited_lore.sources` so the stack stays explicit.

---

## 5. Folder suggestion

```
TTRPG/
  shared_world_continuity.md
  universe_campaign_framework.md   ← this file
  realm_lore_registry.json
  ankuspawn_race.md                ← new playable race
  templates/new_character_campaign.template.json
  Amaris/...                       (campaign COMPLETE)
  Kenji/...                        (campaign COMPLETE)
  <NewCharacterName>/
    Game init files/
      character_world_state.json
      story.md                    (optional, long-form)
      dm_rules_*.md               (optional)
```

---

## 6. Automation — starter campaign generation

The starter campaign system (§ 2) is designed for AI generation. The workflow:

1. Player provides **three inputs**: background, personal goal, starting region preference.
2. AI reads `shared_world_continuity.md`, `realm_lore_registry.json`, and `ankuspawn_race.md` for existing world state.
3. AI generates a complete **Starter Campaign Package** by filling `templates/new_character_campaign.template.json` — all three locations, the antagonist, the 4-phase campaign spine, the NPC cast, dialogue hooks, and the lore seed.
4. AI registers all three new locations in `realm_lore_registry.json` and adds one-line entries to `shared_world_continuity.md`.
5. The filled template becomes `<NewPC>/Game init files/character_world_state.json` — ready to play.

**Generation rules for AI:**

- The three locations must be geographically plausible relative to existing map anchors. Check `shared_world_continuity.md` § Description map and `realm_lore_registry.json` for what's already placed.
- The antagonist must be beatable by a level 10 character. No world-ending threats, no ties to the Anku Conspiracy (that's kingdom-spanning, not starter-tier), no involvement of AnkuNyx or his companions as antagonists.
- The lore seed should reference something real from existing lore — a named location, a known NPC's legacy, a faction's remnant, a construct portal, an Ankuspawn community. It must be accurate to established canon.
- NPC names must be checked against `npc_name_bank.md` (if available for that campaign) to avoid collisions with existing characters.
- The discovery location must genuinely teach the player something about the world they wouldn't learn from their home base alone. It is the starter campaign's educational payload — the thing that makes the player care about the broader setting.

If you add scripts or a CLI workflow for this, keep the **same fields** as the template JSON so generated content drops into `character_world_state.json` without rework.

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

- **2026-04-26** — Book 5 era established. Both Amaris and Kenji campaigns marked COMPLETE. 25-year timeskip applied. Kingdom of Ankunyx is the new continental authority. Ankuspawn race created (`ankuspawn_race.md`). New PCs awaken in a world where all prior events are established history.
- **2026-04-26** — Starter campaign generation system added (§ 2). Every new character now gets a full levels 1–10 campaign package: 3 new locations (home base, adventure site, discovery location), a scaled antagonist, a goal-driven 4-phase campaign spine, and a lore seed connecting to the broader world. Template updated (`templates/new_character_campaign.template.json`). § 6 updated with AI generation rules.

---

## 9. Merging with StoryEngine (`kenji_state` schema)

**`ttrpg_game_engine.py` (StoryEngine)** now **preserves unknown top-level JSON keys** on load/save (e.g. `universe`, `inherited_lore`, `character`, `new_region`, `shared_world`). They are stored internally as **`extra_json`** and merged back into the file when you call **`save_json()`** or export via **`to_dict()`**.

**Practical approach:**

1. Start from **`Kenji/Game init files/kenji_state.example.json`** (or your last save) for the mechanical shell.
2. Paste or merge fields from **`templates/new_character_campaign.template.json`** into the same file as the engine save — custom blocks survive round-trips through the GUI.
3. You can still mirror critical bullets in **`narrative_notes`** for quick AI brief visibility (optional duplicate).

`python ttrpg_game_engine.py brief` includes an **“Extended state”** section when `extra_json` is non-empty.
