# Shared world continuity — Amaris + Kenji

**Universe policy:** All **future PCs** use this same realm. Amaris and Kenji remain **fixed lore**; each new character adds their own region and story (see `universe_campaign_framework.md` and `realm_lore_registry.json`). Copy `templates/new_character_campaign.template.json` when you start a new hero.

Both campaigns take place in **the same realm**: one legal and magical order (Academy-trained mages, Mage Council oversight where institutions reach, necromancy broadly illegal, ley lines real but poorly understood in the countryside).

## Regions (same map, different stories)

| Region | Campaign anchor | Role in the world |
|--------|-----------------|-------------------|
| **Eastern frontier** | Amaris — Thornfield, Briarstone, **Greenveil** | Sparse villages, little institutional magic. Ley activity here is **local** (e.g. Greenveil / Crawling Dark). Resolved in Amaris’s epilogue; no requirement that anyone in Varenholm ever heard the village’s name. |
| **Heartland & west** | Kenji — **Varenholm**, **Duskfen**, **Bleakmoor**, **Sundered Gate** | Academy politics, guild economics, convergence-scale ley warfare, Council scrutiny. These events **exist** everywhere in principle, but **distance and class divide** keep them from touching a frontier farm. |

**Thornfield** sits far from Kenji’s corridor of portals and headlines — **weeks by road**, no gate in the village square, and news travels as rumor, late and distorted.

### Travel matrix (rough, for consistency)

Values are **by road / sensible route**, not portal hops. Adjust for weather or story; don’t contradict by placing two hubs “next door” if this says otherwise.

| From → To | Approx. time | Note |
|-----------|----------------|------|
| **Varenholm** ↔ **Duskfen** | 2–4 days | Heartland travel; frequented. |
| **Duskfen** ↔ **Thornfield** (east) | 1–2+ weeks | Frontier; fewer inns. |
| **Varenholm** ↔ **Thornfield** | 2–3+ weeks | Long haul; news arrives late. |
| **Varenholm** / **Duskfen** ↔ **Bleakmoor** edge | several days–week | Military / ley hazard depending on era. |
| **Thornfield** ↔ **Millhaven** (north) | ~2 days | Amaris reference: garrison town north of Thornfield. |
| **New PC region** ↔ nearest listed hub | *define at creation* | Add to `realm_lore_registry.json` and this table when the place is canon. |

Portals (Kenji arc) **shorten** travel for those with access; most people and most new PCs **do not** use them.

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
- **Millhaven** — **north** of Thornfield — **small** **garrison** **town** (two days’ ride from Thornfield in Amaris continuity).
- **Briarstone** / **Greenveil** — **Thornfield’s** **eastern** **edge**; **Greenveil** **forest** **east** of the **fields**.

**New regions:** When you add a location, give **two** **lines**: where it lies **relative to the world’s “middle”** (girdle / heartland), and where it lies **relative to the Crown realm** (inside the kingdom, on a border, or beyond usual law). Add the place name to **`realm_lore_registry.json`** and, if you like, a **single sentence** under this section.

### In-world calendar (optional)

| Concept | Default |
|---------|--------|
| **Era / year** | Unnamed until you need a date in dialogue. Optional: set `calendar` in `realm_lore_registry.json`. |
| **Per-campaign `day`** | Each `*_state.json` uses its **own** day counter (see below). |
| **Crossover scenes** | If two PCs meet, pick a **story day** and **season** ad hoc, then note it in `shared_world_continuity.md` Changelog or the registry `supersedes_note`. |

Seasons are normal four-season temperate unless you define otherwise in a regional write-up.

## What “same world” means at the table

- **Kenji’s current events** (Bleakmoor, ArchMagus stakes, constructs, property empire, Mordecai) are **happening** while Amaris could be drinking tea on her porch — she is simply **not in the blast radius** unless you move her geographically into that plot.
- **Amaris’s outcome** (Greenveil corruption ended, Briarstone secure, stranger in the forest) does **not** require Kenji’s plot to pause or change. The eastern incident can remain a local mystery with **no paperwork in Crestfall** if you prefer.
- **Crossover is optional**: cameos, shared NPCs, or “the stranger” identities are **not assumed** by this document. Add them only when you want them.
- **Rumors vs. live saves:** Kenji’s **current** arc is tracked in **`kenji_state.json`**; Amaris’s file does **not** auto-update when Kenji’s does. Same-world **truth** for what is really happening in the heartland = Kenji’s state + fiction. What **Amaris hears** = your choice: usually **vague, late, or garbled** rumor unless you narrate a specific channel (travel, letter, scrying, etc.). No requirement that she mirror Kenji’s latest mechanical snapshot.

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
