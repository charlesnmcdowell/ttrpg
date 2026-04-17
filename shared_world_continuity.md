# Shared world continuity — Amaris + Kenji

**Universe policy:** All **future PCs** use this same realm. Amaris and Kenji remain **fixed lore**; each new character adds their own region and story (see `universe_campaign_framework.md` and `realm_lore_registry.json`). Copy `templates/new_character_campaign.template.json` when you start a new hero.

Both campaigns take place in **the same realm**: one legal and magical order (Academy-trained mages, Mage Council oversight where institutions reach, necromancy broadly illegal, ley lines real but poorly understood in the countryside).

## Regions (same map, different stories)

| Region | Campaign anchor | Role in the world |
|--------|-----------------|-------------------|
| **Eastern frontier** | Amaris — Thornfield, Briarstone, **Greenveil** | Sparse villages, little institutional magic. Ley activity here is **local** (e.g. Greenveil / Crawling Dark). Resolved in Amaris’s epilogue; no requirement that anyone in Varenholm ever heard the village’s name. |
| **Heartland & west** | Kenji — **Varenholm**, **Duskfen**, **Bleakmoor**, **Sundered Gate** | Academy politics, guild economics, convergence-scale ley warfare, Council scrutiny. Books 1-2. |
| **Coalition territories** | Kenji — **Crestfall**, **Stormhaven**, **Ironholt**, **Thornwall**, **Thornkeep**, **Ashward Mines**, **Mordecai Ridge** | Post-Iron Crown War (Book 3). Coalition spans two continents. 13 portals, 1,088 constructs, 12,000 troops. These territories are managed by Kenji’s stewards while he is absent in Book 4. |
| **Allied independent** | Kenji — **Deepwood / Silvandris**, **Cinderpeak**, **Vyranth** | Allied but self-governing. Deepwood (elven, the Eldest). Cinderpeak (Zarek, mining). Vyranth (conquered, post-war provisional government). |
| **Eastern coast & border** | Kenji (Book 4) — **Ashenmere**, **Millhaven**, **Thornkeep** | Active campaign territory. Ashenmere is a major port city (Red Court infiltration). Millhaven is a garrison town on the Ashenveil border (also Amaris-adjacent). Thornkeep is the southern border fortress. |
| **Threat regions (Book 4)** | Kenji — **Kharn-Dural**, **The Ashenveil**, **The Sunderplains**, **Dragonspine Mountains** | Five existential threats. Kharn-Dural (dwarven undermountain, northwest). Ashenveil (undead marshlands, southeast). Sunderplains (orc steppe, west). Dragonspine (dragon territory, far north). Ashenmere (vampire infiltration, eastern coast). |

**Thornfield** sits far from Kenji’s corridor of portals and headlines — **weeks by road**, no gate in the village square, and news travels as rumor, late and distorted.

### Travel matrix (rough, for consistency)

Values are **by road / sensible route**, not portal hops. Adjust for weather or story; don’t contradict by placing two hubs “next door” if this says otherwise.

| From → To | Approx. time | Note |
|-----------|----------------|------|
| **Varenholm** ↔ **Duskfen** | 2–4 days | Heartland travel; frequented. |
| **Varenholm** ↔ **Crestfall** | 3–5 days | Eastern frontier road. Major garrison city. |
| **Crestfall** ↔ **Bleakmoor** edge | several days | Military / ley hazard depending on era. |
| **Varenholm** ↔ **Thornwall** (west) | 3–5 days | Military HQ. Western border. |
| **Thornwall** ↔ **Sunderplains** border | 1–2 days | Orc steppe begins. Open ground. |
| **Varenholm** ↔ **Stormhaven** (south) | 4–7 days | Naval territory. Coastal. |
| **Stormhaven** ↔ **Thornkeep** | 2–3 days | Southern border. Bridge fortress. |
| **Thornkeep** ↔ **Ashenveil** border | 1–2 days | Undead marshlands begin south. |
| **Thornkeep** ↔ **Millhaven** | ~1 day | Garrison towns on the same southern road. |
| **Thornkeep** ↔ **Ashenmere** | 2–4 days | Eastern coast port city. |
| **Millhaven** ↔ **Thornfield** | ~2 days | Amaris reference: garrison town north of Thornfield. |
| **Duskfen** ↔ **Thornfield** (east) | 1–2+ weeks | Frontier; fewer inns. |
| **Varenholm** ↔ **Thornfield** | 2–3+ weeks | Long haul; news arrives late. |
| **Varenholm** ↔ **Ironholt** (east) | ~1 week | Eastern anchor. Place of Power. |
| **Varenholm** ↔ **Deepwood / Silvandris** | ~1 week | Elven territory. Independent. Requires permission to enter. |
| **Varenholm** ↔ **Cinderpeak** | 1–2 weeks | Mountain territory. Mining. Remote. |
| **Varenholm** ↔ **Vyranth** (far east) | 2–3 weeks by road | Conquered empire. Post-war. Across the continent. |
| **Varenholm** ↔ **Kharn-Dural** (northwest) | 2–3 weeks | Dwarven undermountain. Mountain roads. |
| **Varenholm** ↔ **Dragonspine** (far north) | 3–4+ weeks | Ancient dragon territory. Treacherous mountain passes. |
| **New PC region** ↔ nearest listed hub | *define at creation* | Add to `realm_lore_registry.json` and this table when the place is canon. |

**Portals** (Kenji arc) shorten travel to **near-instant** for those with access (13 portals across coalition territories). Most people and most new PCs **do not** use them. Portal locations: Varenholm, Crestfall, Stormhaven, Ironholt, Thornwall, Thornkeep, Ashward Mines, Mordecai Ridge, and others.

### Description map (words)

*Primary reference: no drawn map required. This is how travelers, priests, and merchants **talk** about place — belief and habit, not a survey grid.*

#### 1. The “middle of the world” (what people think it is)

Almost no one means the **geometric center of the planet**. They mean one of two things, depending on who is speaking:

- **The girdle of the world** — sailors and old stories describe a **temperate belt** of sea and cropland between **cold north** and **hot south** as *the middle lands*: where most mortals live, farm, and trade. The **Crown heartland** (the river country that holds **Varenholm** and the **Academy**) sits **in** that belt, **inland** from the western trade routes.
- **The heart of the realm** — day-to-day, “**middle**” means **toward the Crown** and **toward Varenholm**: where **law**, **guild charters**, and **licensed mages** are normal. “**Out** toward the frontier” means **away** from that center — **east** into wilder country, or **toward** the **Bleakmoor** border.

Use whichever phrasing fits the NPC. Scholars may nod at the girdle; a farmer says “toward the Academy” or “back toward the Crown roads.”

#### 2. The biggest kingdom in the area (anchor for everything else)

In the territory these campaigns use, the **largest** **unified** **power** is the **Crown realm** — the **old kingdom** whose **law** the **Mage Council** and **Academy** ultimately answer to (titles and capital name can stay vague in dialogue until you name them). **Varenholm** is **not** the whole kingdom; it is a **major** **city** **inside** the kingdom’s **fertile** **heartland**.

From **that** kingdom’s **core** (Crown / heartland / Varenholm cluster), describe other places like this:

- **Varenholm** — **in** the **green** **heartland**, **deep** **inside** the kingdom; **northwest** of **Duskfen** on the usual road net.
- **Duskfen** — still **inside** the realm, on the **forested** **edge** of the heartland — **east** of Varenholm, **before** the land turns **grim**.
- **Crestfall** — a **large** **garrison** **city** on the kingdom’s **eastern** **frontier**, **toward** the **Bleakmoor**; **between** safe farmland and the **moor**. (Larger than Varenholm in **military** **presence**, not necessarily in **scholarship**.)
- **Bleakmoor** and the **Sundered Gate** — **east** of Crestfall, **outside** the **comfortable** **heartland**: **dead** **ground**, **ley** **wounds**, **military** **and** **arcane** **crisis** country.
- **Thornfield** (Amaris) — **far** **east** of the heartland, on the **eastern** **frontier** where **Crown** **attention** is **thin**; **weeks** from Varenholm by **ordinary** **road**.
- **Stormhaven** — **south** of the heartland, on the **coast**; **naval** **territory**, **harbor** **city**. Sera’s Darkblades patrol. Major trade port.
- **Thornwall** — **west** of the heartland; **military** **headquarters**, **army** **staging** **ground**. Katya’s 12,000 troops. First target if the Sunderplains orcs march east.
- **Thornkeep** — **southern** **border** **fortress**; the **bridge** between coalition and frontier. Renna Hale’s garrison. First target if the Pallid March launches north.
- **Ironholt** — **east** of the heartland; **eastern** **anchor** of the coalition. Dren’s Place of Power. Kex patrols the skies.
- **Ashward Mines** — **east** of Crestfall; **revenue** **source**, quarterly audits. Mining territory.
- **Mordecai Ridge** — former **Confluence** **Lens** **site**; now a **portal** **hub** under Vess’s administration.
- **Deepwood / Silvandris** — **elven** **territory**, **independent** **allied**. The Eldest rules. Faelindra commands defense. Permission required to enter. The Heart Grove is the seat of power.
- **Cinderpeak** — **mountain** **territory**, **far** from the heartland. Zarek Ashborne. Mining. Allied independent.
- **Vyranth** — **far** **east**, **across** the **continent**. Conquered empire (Iron Crown War). Post-war provisional government. Resentment simmering. Fragile.
- **Ashenmere** — **eastern** **coast** **port** **city**. Major trade hub. Currently being infiltrated by the Red Court (vampire coven). 30% converted at Book 4 start.
- **Millhaven** — **south** of Thornkeep, **north** of Thornfield — **garrison** **town** on the Ashenveil border. Amaris-adjacent territory. Kenji is operating here in Book 4 under alias.
- **Briarstone** / **Greenveil** — **Thornfield’s** **eastern** **edge**; **Greenveil** **forest** **east** of the **fields**.
- **Kharn-Dural** — **northwest**, deep **mountain** territory. Dwarven undermountain, 40,000 dwarves, two miles deep. The Fathom sealed beneath. Beyond usual Crown law.
- **The Ashenveil** — **southeast**, **dead** **marshlands**. Undead territory. The Lych’s domain. Perpetually grey. The Pallid March stages here.
- **The Sunderplains** — **west** / **northwest**, open **steppe** beyond Thornwall. Orc territory. 30+ tribes unified under Warchief Gorath. Beyond Crown law entirely.
- **Dragonspine Mountains** — **far** **north**. Ancient dragon territory. Off-limits for a thousand years by treaty. Seven dragonflights. The Reckoning vote decides whether dragons descend.

**New regions:** When you add a location, give **two** **lines**: where it lies **relative to the world’s “middle”** (girdle / heartland), and where it lies **relative to the Crown realm** (inside the kingdom, on a border, or beyond usual law). Add the place name to **`realm_lore_registry.json`** and, if you like, a **single sentence** under this section.

### In-world calendar (optional)

| Concept | Default |
|---------|--------|
| **Era / year** | Unnamed until you need a date in dialogue. Optional: set `calendar` in `realm_lore_registry.json`. |
| **Per-campaign `day`** | Each `*_state.json` uses its **own** day counter (see below). |
| **Crossover scenes** | If two PCs meet, pick a **story day** and **season** ad hoc, then note it in `shared_world_continuity.md` Changelog or the registry `supersedes_note`. |

Seasons are normal four-season temperate unless you define otherwise in a regional write-up.

## Campaign supersedes character

**The campaign is bigger than any single player.** A player’s death or absence does NOT end a campaign — it ends that player’s participation. The world continues. The threats continue. The clocks continue. Other players can enter the same world and attempt to finish what was started. A failed campaign has severe world ramifications (territories fall, populations die, the political map redraws). A successful campaign rewards the completing player with power, fame, and permanent world-state changes.

**Canonical example:** In Book 4, Kenji is operating in Millhaven — Amaris’s campaign territory. The seal, the dead road, the undead activity — that’s her threat chain, her content. She’s absent. Kenji walked in and started solving her problems. This is a player doing another player’s campaign in their absence. The world doesn’t wait for the “right” player to show up. Whoever is there, plays.

**Every campaign must have defined success and failure states.** Success = resolving the campaign’s central threats. Failure = any single threat overwhelming the world. These states persist regardless of which player is active.

## What “same world” means at the table

- **Kenji’s current events** (coalition governance, five converging threats, continental defense) are **happening** while Amaris could be drinking tea on her porch — she is simply **not in the blast radius** unless you move her geographically into that plot.
- **Amaris’s outcome** (Greenveil corruption ended, Briarstone secure, stranger in the forest) does **not** require Kenji’s plot to pause or change. The eastern incident can remain a local mystery with **no paperwork in Crestfall** if you prefer.
- **Crossover is real and happening**: Kenji is currently in Amaris’s region (Millhaven) in Book 4, operating under alias. This is not a forced crossover — it’s geographic proximity. The world is consistent; if a player walks into another player’s territory, they encounter what’s there.
- **Rumors vs. live saves:** Kenji’s **current** arc is tracked in **`kenji_state.json`**; Amaris’s file does **not** auto-update when Kenji’s does. Same-world **truth** for what is really happening = Kenji’s state + fiction. What **Amaris hears** = your choice: usually **vague, late, or garbled** rumor unless you narrate a specific channel (travel, letter, scrying, etc.). No requirement that she mirror Kenji’s latest mechanical snapshot.

## Day counters

`kenji_state.json` **Day** and `amaris_state.json` **day** are **campaign-local** counters, not a single shared calendar. Treat them as **the same era** without 1:1 day alignment unless you explicitly sync a scene.

## Files

| File | Purpose |
|------|---------|
| `universe_campaign_framework.md` | How new characters inherit lore and add locations + quests. |
| `realm_lore_registry.json` | Index of every campaign in the combined universe (extend per new PC). |
| `templates/new_character_campaign.template.json` | Blank `character_world_state` for a new hero. |
| `Kenji/Game init files/kenji_state.json` | Live Kenji state; narrative notes may reference this continuity. |
| `Amaris/Game init files/amaris_state.json` | Post–Amaris arc snapshot; `shared_world` block points here. |

Update this file when a **realm-wide** fact changes (e.g. Council law, a named kingdom border) so all campaigns stay consistent.
