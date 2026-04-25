# Character Tracker — Kenji TTRPG

**Current In-Game Date:** Ashmere **47** morning, 1247 AR — **Day** **269** **~10:00** — **Varkûl** **(**Iron Horde capital, south gate blood circle**)**  
**Current Location:** **Kenji** **—** **Varkûl**, **south gate blood circle** — **outside ring, watching**. **CLIFFHANGER:** Gorath vs Nyx (Close to Death trap). **ANKU NYX ACTIVE.** Green aura + green eyes (permanent). Soul Conqueror locked (1.5^7 = 17.09×). 8 gate guards KO'd (JKD). Arcane Sprint 460mi/7min (L6 spent). Corwyn at Pallid March (full consciousness, flesh facade). **Mursha** **—** **still** **Kharn** **witness-engineer**. **Purse** **1395 GP / 181 SP**. **HP 6,288/6,288** (regen 1,048/sec); **Wind Step 5/5**; **Smoke-Invis-Clone 3/3**; **Iaido 1/1**; **L6: 1/2**.
**BOOK 4 — Ch36 COMPLETE** (played live). **Ch35** (played live — Corwyn restored, Iron Horde strategy). **Ch34** — `fraying_empire_chapter_34.md` (**Seven Days**). **Ch33** — `fraying_empire_chapter_33.md` (**Anku Nyx**). **Threat 1 Hollowing** — **seam pinned, not closed**. **Threat 2 Pallid March** — **ALLIED; March impregnable (Vigor-enhanced undead); 612 anchors prostrate**. **Threat 3 Iron Horde** — **ACTIVE; Close to Death trap on Gorath in progress**.
**Active Book:** Book 4 — Fraying Empire (The Ronin Arc)

> **Cross-references:** **Arc clarity (core problem, regional stakes, NPC agendas)** → `arcs/ARC_STANDARD.md` (Kharn example: `arcs/north_relay_two_chapter_plan.md` § *Kharn forge crisis*) | DM behavior rules → `dm_rules_tracking.md` (**MIA PROTOCOL** + **🎯 ALIVE / IN-PLAY NPC — GOAL INVARIANT** + **Scene skill preroll** + **Player success integrity**: roll before outcome-dependent prose; PC success = player-favorable beat; no NPC Perception auto-win / no “gotcha” undo) | Game engine & mechanics → `ttrpg_game_engine.py` (`skill_roll`, `contested_skill`, `build_skill_modifier`, CLI `skill`) | Live state → `kenji_state.json` | Cursor agent rule → repo `.cursor/rules/kenji-scene-skill-gates.mdc`

---

## MORALE COMPASS REFERENCE

Every character entry includes a **Morale Compass** value. Use it to decide how to write them, when they hold ground, and when they oppose Kenji. Five values are used:

- **Lawful Good (LG)** — Follows the law, helps people. Cooperates when justice and protection align. Opposes Kenji if he becomes the one harming innocents. *Examples: Sera, Sir Corwyn (a Lawful Good paladin whose sovereign happens to be evil — the alignment describes the man, not the throne he answers to).*
  - **The dangerous read.** Lawful Good is the alignment players most often mistake for *safe.* It is not. LG characters are friendly, principled, trustworthy in most contexts — and they will absolutely put you in poverty, in jail, or in the ground if the law they serve tells them to. Nothing is above the law for them. Not friendship, not gratitude, not mercy in the moment. That is why Lawful Good characters are easy to hate and hard to navigate: the same code that makes them honorable in one scene makes them an enemy in the next the instant the law you crossed is theirs. You are always walking on eggshells around an LG you have reason to fear, because their kindness is real and their sword is also real and both of them answer to the same sovereign.
- **Chaotic Good (CG)** — Breaks rules for good ends. Protects people without permission. Ignores laws that grind down the weak. Helps Kenji when it saves lives; pushes back when he grows cold or convenient. *Example: Garret (bandit highwayman who refused to kill needlessly).*
- **Neutral (N)** — Self-interest, balance, or capacity for genuine change. **RESERVED FOR PLAYER CHARACTERS ONLY.** See rules below.
- **Lawful Evil (LE)** — Works inside the rules to accrue power and harm those beneath them legally. Shows up to court. Stabs you on the way out. *Examples: Vael, Mordecai.*
  - **The trustworthiness paradox.** Lawful Evil is — counterintuitively — *more* predictable than Chaotic Evil. An LE operator has drawn a line: they will not cross the laws of the land. They will twist, exploit, contract around, and lobby to change those laws, but within them, they play straight. That consistency is a kind of trust: you know what they will and will not do, and the boundary holds. Their ambition is to *control* the law, not to disobey it. This makes them dangerous in a slower, more negotiable way than a Chaotic Evil character — you can sign a deal with a Lawful Evil and actually expect the terms to be honored. You cannot sign a deal with Chaotic Evil at all, and if you do, it is not binding on them the second a better offer appears.
- **Chaotic Evil (CE)** — Cares only for self: pleasure, power, conquest. Obeys only when forced or rewarded. Lies, pretends virtue, betrays the moment a better deal appears. *Example: Lady Nyx.*

### Alignment Rules

1. **Only player-made characters are Neutral.** This currently covers Kenji (Hiro's character), Amaris (player-made), and any future cross-campaign player characters brought in via the combined-universe mechanic. Every other NPC has a clear fixed alignment so the DM knows how to write them.
2. **Only Neutral characters can be persuaded to shift alignment.** Their arc and relationships can push them toward LG/CG/LE/CE over time. NPCs do not shift — their alignment is who they are.
3. **When they oppose Kenji:** They hold ground when the situation directly threatens their core compass value. LG opposes injustice. CG opposes cruelty and cold calculation. LE opposes threats to their legitimacy, position, or contract. CE opposes anything that curbs their power or pleasure — and will flip the instant a stronger hand shows up.

---

## KENJI — The Ronin / ArchMagus (disguised)

**Status:** alive
**Level:** 35
**Location:** **Varkûl** **—** **south gate blood circle**, **Ashmere** **47** **morning** **Day** **269** **~10:00**. **Iron Horde capital.** Gorath vs Nyx in blood circle (staged loss — Close to Death trap). Kenji outside ring. Thousands of orcs watching. **HP 6,288/6,288** (regen 1,048/sec); **Wind Step 5/5**; **Smoke-Invis-Clone 3/3**; **Iaido 1/1**; **L6: 1/2** (Arcane Sprint spent). **Purse ~1395 GP, 181 SP** (`kenji_state.json`).
**Last Updated:** Ashmere **47** / Day **269** — **Ch36** *Varkûl Gate — The Bait*

**Physical:** `npc_appearance.md` § **Kenji — Ronin / Blade Channeler**
**Disposition:** N/A (protagonist)
**Morale Compass:** Neutral (Player Character — Hiro's call; shiftable as Kenji develops)

**Abilities (full ArchMagus kit — most are SUPPRESSED in Ronin mode):** Enhanced Arcane Edge, Haste, Stride (L4), Wind Step (70m), God Sight (120ft darkvision + crit targeting), Greater Invisibility, Clone (smoke bomb), Radiant Edge, Ward Mastery (L4), Living Ground (druid bond), Diagnostic Touch, Bond-Form Sight, Captain's Read, Irresistible Presence (Siren-Elf aura; full rules → `kenji_tracking_OBSOLETE.md` § IRRESISTIBLE PRESENCE), Portal Gateway, Lover's Vigor (see same subsection), Scribe's Eye (Tamsin bond — passive omnilingual literacy), Paper Memory (Tamsin bond — 1/LR perfect document recall 24h)

### Irresistible Presence & Lover’s Vigor (female humanoids) — authoritative summary

**Irresistible Presence:** **NOT charm / NOT dominate.** Sentience and free will stay intact. The aura is a **strong urge to want to procreate with Kenji**, escalating on a save ladder while she **views** him (DC, timing, stacks, fades — **verbatim** in `kenji_tracking_OBSOLETE.md → ## IRRESISTIBLE PRESENCE RULES**).

**Lover’s Vigor + five-day immunity to the aura (linked):** Trigger when Kenji **ejaculates inside her vagina** **or** she otherwise receives **his semen inside her vagina** (intimacy, stored sample, **Book 3 — Kenji’s elf sister used her hair to put his semen inside the recipient’s vagina**, other vectors if the table accepts them, etc.). **Effect for exactly 5 days:** **+50% all stats**, **Lover’s Vigor** tells (often eye shift; see per-NPC notes), and **immunity to Irresistible Presence** (no IP save pressure from aura during the window). **Tracker fields (DM / notes per woman):** `vigor_start`, `vigor_expires`, `immune_to_IP_until`, snapshot or pointer to `baseline_stats` vs buffed line. **On expiry:** buff and **immunity both end**; **urge returns at full stack pressure**; many characters will **want the power back** and may pursue Kenji or his seed — intentional hook for obsession, deals, theft, and repeat cycles (Lady Nyx’s capture-Kenji pattern is one CE example).

### RONIN MODE — Active Loadout (Book 4)

**Why he's fighting this way:** Kenji is deliberately building a new combat persona — **The Ronin** — to throw off everyone hunting Kenji the ArchMagus / Champion of the Elves / Bane of Eve. The iaido-and-nodachi silhouette, the wuxia-style Wind Step, the troll-illusion smoke-bomb-clone combo, the trimmed spell list — none of it reads like the Wizard King's fighting style. Anyone searching for Kenji is looking for: ember aura, dual-blade Emberfrost, golden portals, Siren-Elf **Irresistible Presence** (procreative-urge pressure), creation/entropy signature, battlefield flight. **The Ronin uses none of that.** Witnesses describe a masked swordsman with a black nodachi, a hakama, and a smoke-bomb trick. That description maps to hundreds of wandering blades across the continent. That's the point.

Kenji is undercover. **Arcane and Ember abilities are deliberately off the table** — using them would identify him as Kenji the ArchMagus and collapse the disguise. Ronin mode is a trimmed, deliberately low-tier-looking kit that lets him fight and travel without reading as an archmagus to any observer.

**What's active:**

- **Abyssal Shard Nodachi** — primary weapon. Red-black steel, faint internal luminescence. **Damage: 6d12 slash + Void.** **25% chance to vaporize the enemy on a CRIT** (instant-kill roll per crit, not per hit). Reads as a scary but mundane exotic blade to observers.
- **Iaido Stance** (Taryn bond, trained Millhaven Ch 4) — **Guaranteed crit on the drawn cut. Once per encounter.** Triggers either **before initiative** (pre-combat draw-strike) or **after a full sheathe** during combat (reset by sheathing the blade, then redrawing). Form: thumb on guard, left foot forward, weight low. Draw, strike, return — one motion, one breath. Six months of muscle memory plus seven days of back-room drill. **Synergy with the nodachi:** guaranteed crit + 25% vaporize on crit = every drawn cut rolls for instant-kill.
- **Iaido Combat Economy (per turn):**
  - **2 attacks per turn** base.
  - **2 counter-attacks per turn** (reactions on enemy miss in melee range, no reaction cap within a single turn — each counter is its own strike).
  - **On-Kill Continuation:** When Kenji kills an enemy with the nodachi, he gets an immediate free bonus attack. **This is baked into the iaido style itself — it does NOT require Arcane Edge active.** Replaces Arcane Momentum in Ronin mode (Arcane Edge is suppressed for cover reasons, but the style's momentum-on-kill remains). Unlimited triggers per round so long as the kill requirement keeps being met.
- **Ronin Quirks (roleplay-driven combat behaviors — not perks, not leveled, earned through play):**
  - **Showman's Sheathe (nat 1 / miss quirk):** When Kenji rolls a nat 1 or misses an attack, he does NOT continue attacking. Instead, he plays the miss off — creating distance with a spin, twirl, or flourish — then slowly sheathes the nodachi in a dramatic samurai/ninja pose and **freezes in the pose, ending his turn.** The enemy gets their attack turn against a man standing still with his sword put away. **But Kenji gains 4 counters during the enemy's attack turn while holding the pose.** Each counter is a full reaction strike triggered on an enemy miss. Pose ends at the start of Kenji's next turn. **Mechanically:** trades offense for quadruple counter potential. **Narratively:** the ronin who treats combat like performance art. Witnesses see a man who missed, sheathed his blade mid-fight, and then punished every retaliatory swing without breaking the pose. It looks insane. It looks deliberate. It looks like he meant to miss.
  - **Sheathe types** (flavor/tactical):
    - **Back-carry sheathe** — slow arc over right shoulder, tip skyward, rotates down behind the back. *Shhhhiiiing. Click.* Full sheathe. Resets Iaido Stance.
    - **Hayanoto (quick reset)** — fast one-handed drop to the scabbard. Full sheathe. Resets Iaido Stance.
    - **Chiburi-first** — flick of the blade to shed blood before sheathing. Full sheathe. Resets Iaido Stance. Cosmetic — tells witnesses he's done.
    - **Half-sheathe hold** — tip into the mouth of the scabbard, thumb on guard, blade mostly exposed. **Does NOT reset Iaido Stance.** Reads as "still dangerous" to anyone paying attention. Used to bluff, load, or keep options open.
    - **Reverse / left-hand sheathe** — off-hand sheathe. Full sheathe (resets stance), awkward on purpose, used to sell off-balance or occupied-hand.
- **Jeet Kune Do Stance** — alternate unarmed fighting style. Kenji drops his weapon, removes upper armor, and fights Bruce Lee–style: hopping footwork, showboating sounds (*wataaah*, *waaaah*), nose-rub taunts. **Cannot be used simultaneously with Iaido — this is a stance swap (weapon down, fists up).**
  - **Unarmed attacks count as weapons:** **4d8 bludgeoning** per strike. STR-based: **+23 to hit** (+16 STR, +7 prof).
  - **All attacks are non-lethal.**
  - **4 attacks per round:** 3 kicks, 1 punch.
  - **Kick** — chance to **knock prone** (target DEX or CON save vs DC 23).
  - **Punch** — chance to **stun** (target CON + STR save vs DC 23).
  - **KO Threshold:** Any landed hit on a target below **25% HP** forces a save or **knockout**.
  - **Counter Punches:** **2 per enemy round**, proc on enemy hit **or** miss. Each has a chance to **stun** (target STR or CON save vs DC 23). **Stun ends the enemy's round.**
  - **Performance Check 1 (start of round):** If passed → **Spirit Aura** active until next turn. All attacks deal an additional **15% of target's max HP as spirit damage**. Does not affect constructs.
  - **Performance Check 2 (end of round):** If passed → enemy gets **disadvantage on attacks** and Kenji gains **75% dodge chance** during the enemy's next turn.
  - **Grapple:** Cannot initiate grapple in this stance. All enemy grapples on Kenji have a **75% chance of being broken** on the next round.
  - **Style tax:** Same showman energy as Iaido — the performance IS the fighting. Witnesses see a shirtless martial artist bouncing on his toes, making Bruce Lee sounds, and putting opponents on the floor with kicks that crack the air. It reads as eccentric wandering fighter, not ArchMagus.
- **Steel Sight** (Taryn bond) — Reads weapon quality and flaws at a glance. Passive, no tell.
- **Windstrider Boots** — silent, trackless, +2 DEX, +5 Acrobatics, 20% dodge.
- **Threadwalker Gloves** — +3 DEX.
- **Red-and-Black Hakama** — **+3 light armor. Generates a defensive ward every 2 turns** (one absorption/deflection charge refreshes on a 2-round cadence). Reads as traveling clothes. The ward cadence is the only tell, and it's subtle — looks like "lucky blocks" to an outside eye.
- **Smoke Bomb + Invisibility + Clone (combined)** — single combo ability. **Lasts 6 hours. 3 charges per day.** Smoke bomb drops, Kenji goes invisible, the clone walks out of the smoke. This is a **troll-tier illusion package** — Kenji uses it for fun and distraction. A genuine illusionist at Kenji's level would do vastly more; this is the shallow surface layer specifically *because* he's playing small.
- **Wind Step** — travel ability. ~70 meter burst. **Opposite of Arcane Stride — this is extremely agile and silent instead of fast and loud.** Cloud-stepping, tree-running, water-running. Kenji crosses terrain by skipping across surfaces that shouldn't hold weight. Looks like wuxia, not war-magic. No tiring over normal distances at Level 35.
  - **CURRENT TIER (Book 4 early): 25 mph** — base pace, chained continuously.
  - **PENDING UPGRADE — Wind Step Leveled (DM: trigger when travel use earns it):**
    - **Stealth mode (clone running ahead as decoy): 40 mph.** Not invisible-fast — can be seen and stopped. The clone runs the road openly while Kenji ghost-steps parallel. Observers see a traveler. Not two.
    - **All-out sprint (no stealth, doesn't care who sees): 80 mph.** Ridiculous kung-fu montage — kicking off trees, buildings, boulders, using them to gain height, then air-walking for a few moments and spinning into a sky-glide streaming upward before slowly arcing back down to earth. Flashy, loud in a wuxia way (not an ember way), unmistakably a high-level move but reads as martial mastery, not arcane.
    - **Maximum burst (sustained glide phase): ~200 mph** during the airborne portion of the all-out sprint. This is as fast as Kenji can move without Arcane Stride / the ember.
  - **NARRATIVE DIRECTION — THE RONIN'S STYLE TAX:** Wind Step (all tiers) is Kenji deliberately looking cool. The reader knows his real potential from Books 1-3 (Arcane Stride was raw speed and violence). The Ronin version is theatrical — twirls, spins, mid-air poses, cloud-stepping with unnecessary flourish. **Describe in detail:** the wuxia kicks, the tree launches, the glide arcs, the deliberate show of it. NPCs who witness it should react the same way they react to the clone — comedic disbelief, dry commentary, "did that man just run on a cloud?" Same energy as when characters spot the clone isn't real. **No omniscient commentary** — NPCs comment on what they see (a masked swordsman doing impossible acrobatics), NOT on Kenji's true potential or old move set unless they canonically know who he is.

**What's suppressed (will break cover if used):**

- All Ember abilities (Ember Lance, Emberfang, Emberfrost, Cyclone, Horizon Arc, Ignite) — Emberfang is left behind/stored specifically to prevent temptation.
- All overt Arcane casting visible to witnesses — Enhanced Arcane Edge, Radiant Edge, Stride, Haste, Thunderous Strike, etc. Held in reserve for genuine emergencies only.
- Portal Gateway creation — 15ft dual-nature archways are a signature fingerprint.
- Duality Aspect — 60ft aura and flight would identify him instantly.
- Irresistible Presence / Siren-Elf aura (DC 23) — activating it near NPCs creates witnesses who can later describe the aura and trigger Bane of Eve #2.
- Full-scale Lover's Vigor transmission to anyone whose eye-color shift will be publicly visible and traced back.

**Sensory toolkit (passive, no tell, always on):**

- Bond-Form Sight, Living Ground, Captain's Read, Steel Sight, Diagnostic Touch, God Sight — all invisible to observers, all safe to use at all times.

**Emergency-only (breaks cover, used only if the alternative is dying or exposure is already inevitable):**

- Recall (solo teleport to portal network) — visual tell is brief but complete disappearance.
- Frost Fang summon — Solveth speaks through it audibly; only draw if already committed to a fight with no survivors.
- Full Arcane/Ember arsenal — if the mask comes off, it comes off; fight as the ArchMagus.

**Important Gear:** Abyssal Shard Nodachi (red-black steel, 25% vaporize on hit), Windstrider boots, Threadwalker gloves, red-and-black hakama (+3 light armor, ward every 2 turns), Emberfang (creation sword — left behind/stored), Frost Fang (entropy sword — summonable, Solveth lives here), Bag of Holding, Iron Key (pulls SSW — 2-century binding, feeder ley-node, sealed terminator), Hollow Crown → Circuit Bracelet (Book 2 endgame), mask, ronin garb, enchanted underclothes

**Gold:** ~1385 GP / 191 SP (Ch22 −8 GP parlor; +500 GP haul + suite costs prior; sync `kenji_state.json` on next agent pass)

### ANKU NYX — Personality Mode (Ch34+, conditional)

**Condition:** Active **as long as Lady Nyx remains in Kenji's Soul Nexus** (Bond #23). If the bond is ever severed — Nyx dies, betrays past the point of no return, or is somehow removed from the Nexus — Anku Nyx reverts. The green fades. The hazel returns. The tattoos go dark. Until then, this is what he looks like and how he carries himself.

**What changed (Ch34 — Seven Days):** Seven days inside Close to Death with a Living Lich. Vigor stacked 1→7 (geometric, unprecedented — the system was designed for a single application). Soul Conqueror unlocked — all seven Vigor stacks reflected back through the Nexus into Kenji's own stats. **1.5^7 = 17.09× geometric multiplier on ALL ability scores.** Pre-SC base: STR 43, DEX 20, CON 43, INT 9, WIS 10, CHA 20. **Post-SC: STR 734, DEX 341, CON 734, INT 153, WIS 170, CHA 341. HP 6,288. Regen 1,048/sec.** The creation ember that has always burned behind his ribs met death-dominion energy and fused into a new spectrum. The root network — Nyx's 612-anchor territorial system — read the fusion and granted authorization. What walked out of that castle is not the Ronin. It is not the ArchMagus. It is something adjacent to both.

**Why this is a separate personality:** The Ronin was a disguise — deliberately trimmed, deliberately small, designed to hide the ArchMagus. Anku Nyx is not a disguise. It is what Kenji became when he stopped hiding from one specific thing. The Ronin sheathes his blade and plays the wandering swordsman. Anku Nyx stands in a dead woman's throne room with green light pouring off his skin and does not pretend to be anything other than what he is. The combat style is the same (iaido, JKD, nodachi). The attitude is not.

**Visual — ANKU NYX FORM:**

- **Eyes:** Green. Luminous, glowing, faintly sinister. **No longer hazel.** Permanent. Not Vigor teal — not the temporary cyan-green shift that partners get. This is a new color: deep green with inner light, the same spectrum as the aura. The eyes of someone who spent seven days inside death and came out the other side still breathing.
- **Aura:** Green. Permanent ambient glow — visible in low light, faint in daylight but present. Not the gold-green of the ember (creation). Not the teal of Vigor (temporary buff). A new spectrum: **creation + death-dominion fusion.** The ember still burns behind his ribs, but it burns in two spectrums now. The green is the death-dominion half made visible.
- **Chest Sigil:** A glowing green runic mark centered on the sternum — vertical, angular, sharp-lined. Pulses faintly with heartbeat. This is the Soul Conqueror anchor point — where the Nexus bond to Nyx physically manifests on his body. **Holds a dim green glow even at rest** — the core never fully goes dark. Visible whenever his chest is exposed (shirtless, open vest, JKD stance).
- **Dragon (back):** Large dragon-demon-god spanning shoulder blades from nape to waist — surfaced during the last hour of Day 7. Green eye, purple outline glow, intricate scale work. Tail wraps around left side to ribs. Head faces forward over right shoulder with an expression of *attention*. The visual signature of Anku Nyx — the way the runic lines are Nyx's, the dragon is Kenji's. Dark dormant linework at rest; green eye and purple outline glow when active.
- **Body Markings:** Arcane symbol tattoos across chest, arms, and back — **did not exist before Day 1 of Ch34.** They surfaced during the seven days as the physical record of the bond: faint dark linework appearing Day 5, spreading across chest and arms Day 6, the dragon completing on Day 7. Not ink — the bond wrote them into the skin between cycles of destruction and repair. Dark dormant linework when inactive; **ignite green when power flows** (combat, aura surge, emotional intensity). Functional cue: glowing tattoos = he's drawing on it. Brightest at the wrists, hands, and chest sigil. Dimmer along the arms and back. The effect is subdermal — light beneath the skin, not on it.
- **Build:** Massive. STR 734 reads on his frame now — broad shoulders, heavy arms, the physique of something that should not exist at human scale. The Ronin looked lean and precise. Anku Nyx looks like a weapon someone forgot to sheathe.
- **Hair:** Purple dreads unchanged — long, braided, falling past mid-back. Three with iron beads, one with Deepwood bramble-clasp. The green glow catches in them when it pulses.
- **Skin:** Dark. Deep warm brown, unchanged. The green markings sit beneath it, not on top of it.
- **Gear (default stance):** Shirtless or dark sleeveless haori (open, sigil visible — haori comes off when things start). Black hakama (same +3 light armor). Simple martial-arts shoes. Nodachi carried by choice, not default — across the back when announcing himself, sheathed at the hip when talking. No mask. No ronin hat. **Anku Nyx does not hide his face.** The mask was the Ronin's. This version of Kenji does not wear it unless there is a tactical reason — and even then, the green eyes glow through.
- **Gear (combat):** Iaido stance or JKD stance — same combat mechanics as Ronin Mode. The green energy does not add mechanical damage (Soul Conqueror's stat reflection is already baked into the numbers). The visual difference is cosmetic but dramatic — every strike trails faint green light, every counter-punch pulses at the knuckles, the iaido draw leaves a green afterimage in the air.

**Personality shift:**

- **The Ronin** played small, played funny, played the wandering nobody. Showman's Sheathe, Bruce Lee sounds, the annoying grin behind the mask. That energy is still there — Kenji is still Kenji. He still makes the sounds. He still does the nose-rub taunt. He still sheathes the blade mid-fight to prove a point.
- **Anku Nyx** adds weight to the comedy. The man making *wataaah* sounds is also glowing green with death-dominion energy and has a sigil on his chest that reads "I survived something you cannot name." The humor lands differently when the person delivering it looks like a final boss. Witnesses don't know whether to laugh or run.
- **Title usage:** Kenji introduced "Anku Nyx" as his title to Nyx specifically — it means "I am your other half, and we do not die." He may or may not use it publicly. The title is a relationship marker, not a rank. But anyone who sees this version of Kenji and later hears the name "Anku Nyx" will connect the two instantly. The green is a signature.

**Cover implications:**

- **The Ronin disguise is compromised.** Green eyes + green aura + green body markings are not something hundreds of wandering blades share. The Ronin was anonymous because he looked generic. Anku Nyx is the opposite — unmistakable, unique, instantly memorable. Anyone who sees this version of Kenji and later encounters a description of the ArchMagus will have a data point that did not exist before.
- **The mask is optional now, not habitual.** The Ronin wore the mask to hide. Anku Nyx does not default to hiding. This is a behavioral shift, not a mechanical one — Kenji can still put the mask on, but the instinct to hide is weaker after seven days of being fully seen by someone who could have killed him at any moment and chose not to.
- **New tell for identity trackers:** "Green-eyed swordsman with purple dreads and glowing marks" is a description that narrows the field from hundreds to one. Bane of Eve pressure escalates if this version of Kenji is seen in public.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| iron_key_investigation | Ashmere 22 | TBD | TBD | OPEN | Seal OPENED Ashmere 24 night at terminus (grid H-9). Key LEFT IN THE GROUND. Contents unexplored — Kenji walked away with Elda before looking. Death knight witnessed. Whatever is below the seal is now accessible. | Unknown. The seal is open. The key is unrecovered. |
| iron_chest_contents | Ashmere 23 | N/A | N/A | RESOLVED | RETURNED to Sir Corwyn at terminus camp, Ashmere 24 night. Contents never opened. Kenji never looked inside. | Corwyn has his chest back. Relationship shifted to Conflicted. |
| apotheosis_level_40 | ongoing | TBD | N/A | in_progress | **2,270,050** / 2,500,000 EXP (~**229,950** to Level 40). Synced `kenji_state.json` **exp** (Ch18 close). Five threats + Bane supplemental. | Reaching L40 completes the apotheosis arc. Mechanical cap on advancement. |

---

## BRONZEBARROW — The Brass Hitch (minor NPCs; **Ch21–23** arc — **Ch23** exits north)

### Ch19 played (Ashmere 35 — **synced** **`kenji_state.json`**)

- **Inn:** **rumors** **/** **leads** **asked** (**Calista** **/** **desk**).
- **Forge — Marthel:** **medium** **dragon-scale** **laminate** sold as **junk** (**10 GP** Kenji); **Luck** **(CHA)** + **Steel** **Sight** table; **clean** **+** **fit** **Mursha**. **Oathbreaker** **out** **of** **BoH** — **reforge** **for** **Mursha** **denied** (**Persuasion** **fail**); **stowed**; **Mursha:** *Where’d you get that?* **unanswered** **in** **JSON**.
- **Weapon** **stall** (**EDGE**): **honest** **blade** **chosen** — **payment** **next** **beat**.

Relay-town inn cast; names from `npc_name_bank.md`. Full coloring → `npc_appearance.md`.

| Name | Role | Species | Skin (summary) |
|------|------|---------|----------------|
| **Calista** | Barmaid | Human | Warm light golden-beige; freckled nose/cheeks |
| **Mursha** | Iron Mule caravan guard (severed roster) | Half-orc | **Pale olive–green**, **STR-heavy** build (broad shoulders, defined back/abs, very large thighs/glutes), **black cornrow→braids** + **silver bands/hoops**, **long ears**, **small capped tusks**, **R brow + cheek scars** — **tavern lock:** `mursha_brass_hitch_tavern.png`; **suite:** `mursha_brass_hitch_suite_*.png` (×7) + optional player refs → full **`npc_appearance.md` § Mursha**; **DM stages:** (1) professional (2) IP pressure (3) **Lover’s Vigor** — **bronze-gold eye ring** |
| **Haldra** | Dwarf factor clerk | Dwarf | Fair warm-toned, cream-and-rose; forge-flush cheeks/nose; full-figured build, dark auburn twin braids w/ bronze ties; clear blue eyes — **required refs by stage:** clerk `haldra_brass_hitch_clerk.png` + `_back.png`; intimacy `haldra_offduty_intimacy_reference.png`; post-vigor `haldra_post_vigor_reference.png`; **DM stages:** (1) normal (2) pre-intimacy/IP pressure (3) post-intimacy **Lover's Vigor** — brass-amber eye ring tell |
| **Gwynn** | Hostler | Halfling | Sun-kissed golden tan; hazel eyes — **required refs by stage:** work `gwynn_hostler_portrait.png` + `gwynn_hostler_work_back.png`; intimacy `gwynn_intimacy_reference.png`; post-vigor `gwynn_post_vigor_reference.png`; **DM stages:** (1) normal (2) pre-intimacy/IP (3) post-intimacy **Lover’s Vigor** — **emerald / bright green** eye tell |
| **Tamsin Vale** | Coalition tally scribe | Human | Ink-stained fingers, clerk posture; **brown** eyes — **Lover’s Vigor** (triggered **Ch25** berm beat): **fine copper-bright ring** at pupil (visible **Ch26** niche lantern); +50% stats ~5 days; **IP-immune** vs Kenji ~Day 265 / Ashmere ~43; **Ch26** letter routing hook live; **identity pressure** vector (5 data points — illiteracy, 80 GP, IP, "the ronin", berm) |

### Ch20 played (Ashmere 35 evening — **synced**)

- **Western cut:** pack-train siege found (box switchback, ridge bandits, ~2d siege). Split flank — Mursha left, Kenji right (**Iaido** spent). Rim broken.
- **Mursha:** **Power of P** vs ridge lieutenant (CON fail reroll); intel + **+2 STR** → baseline **STR 22**. Kenji watched invisibly (**Greater Invis** overwatch).
- **Exit misdirect:** illusion double → sleight swap → dismiss. **Smoke-Invis-Clone 2/3**.

### Ch21 played (Ashmere 35 late eve → Ashmere 36 predawn — **synced**)

- **Circle:** survivors stabilizing; Kenji shares bread with driver's mate. Mursha returns from ridge — intel secured; Power of P witness asymmetry unchanged.
- **Inventory:** Mursha manifest reconciliation (coalition cargo accounted); Kenji bandit hoard **+500 GP, +18 SP** (retcon). Train cargo stays with clerk.
- **Night road:** ~3 hours, western cut → Bronzebarrow. No speech.
- **Brass Hitch:** standard room **−6 GP −4 SP**; luxury suite upgrade + late tray **−18 GP −6 SP**. Kenji ley-steam bath (mask off); Mursha kit maintenance + intel to paper. Predawn private beat — **Vigor reinforced**.
- **End:** Day 258, Ashmere 36, ~05:30. **1393 GP, 191 SP**. HP 368/368. All charges unchanged.

### Ch22 played (Ashmere 36 morning — prose `fraying_empire_chapter_22.md`)

- **Brass Hitch:** Calista gossip → **Mursha** leads **Haldra** desk (Kharn paper / north-row vault line). **IP:** Haldra fails WIS twice (desk + transit). **Private parlor:** 8 GP hour; **Persuasion ADV 20 vs DC 19** — extended consent beat; **verbal-only** intel (Kenji INT 9). **Lover’s Vigor** on Haldra per table.
- **Relay:** Kenji oral merge to **Mursha**; ridge paper + parlor intel combined. **End ~10:30.** **Purse 1385 GP** after hour.

### Ch23 played (Ashmere 36 mid → Ashmere 37 — prose `fraying_empire_chapter_23.md`)

- **Exit bridge:** **North** courier toward Kharn-Dural (**Hollowing** vector). **Mursha** formal paper handoff to **Haldra** + **factor guard contract** (professional cover with Kenji). **Sealed tube** mis-deliver → Haldra open → **read-aloud** Kharn sub-clan plea (*note changing beneath the mountain*). Kenji carries tube as witness.
- **Yard:** Cassia investigation ambient — clerk look, **no** stop. **Travel:** factor train, Day 259 first leg; dwarf whisper “the note changed.” **Camp:** wrong forge-glow on horizon.

### Ch24 played (Ashmere 37–38, Day 259–260 — prose `fraying_empire_chapter_24.md`)

- **Mursha:** climb + watch; **gnomish milepost** — factor silver, rhetoric; **outer Kharn checkpoint** — papers; **blocked random bag verification** on Kenji (BoH not opened). **Oathbreaker** question **deferred** (Marthel memory). **IP** strain on staff. **Ambient:** relay trough soap; Kenji unvoiced.
- **End:** Day 260 evening — admitted **gate line**, inner yard **Ch25**.

### Ch25 played (Ashmere 38 night, Day 260 — prose `fraying_empire_chapter_25.md`)

- **Tamsin Vale** — coalition scribe; off-base beat (mature / coercion / IP per table). **Read proof:** three coalition hand-marks in dirt; Kenji speaks sounds; **Kenji (player):** *I can read* — breakthrough stub (not full literacy for INT 9). Marks **erased**. **80 GP** escrow resolved (Tamsin keeps — lessons delivered). **Player close:** *send a letter to the ronin, I’ll come to you* — Tamsin: threat-memory (*I’ll remember. Don’t make me use it*). **Literacy:** ongoing unless table retcons. **Charges:** unchanged unless table logged clone/invis on checkpoint thread.
- **End:** Day 260 night — approach to outer line / separation per table. Purse ~1385 GP. HP 368.

### Ch26 played (Ashmere 38 night/predawn, Day 260 carry — prose `fraying_empire_chapter_26.md`)

- **Kharn-Dural upper works** — inside the mountain (mines / surface-linked gallery). Kenji + Tamsin in lantern hearing (tally niche). **Kenji (player):** reaffirms letter routing (*Ms. Vale — if you want me to come by again, send a letter. Same as before*). Tamsin: *Letters need routes. Ronin isn’t a route.* Then: *I’ll find one. Don’t flatter yourself that I’m eager.*
- **Lover’s Vigor on Tamsin:** copper ring at pupil tell — visible in niche lantern light. IP immunity vs Kenji active ~5 days (table). Tamsin: horror → *Don’t name it* → clerk ice → *Five days* (she knows the window from gossip/fear). Clearer head = sharper shame arc. Not Bonded Lovers #22 unless table promotes (vigor ≠ automatic bond slot).
- **End:** Ashmere 38 predawn Day 260 — Kenji at coalition clip-desk vector; Tamsin routed away (Bond #22 — table promoted). Mursha / factor train remerge Ch27. Charges unchanged. ~1385 GP. HP 368. EXP 2,270,050.

### Ch27 played (Ashmere 39 morning–afternoon, Day 261 — prose `fraying_empire_chapter_27.md`)

- **Mursha** states dual objective: Haldra-line liability + quarantine truth (forge story Kharn wraps in "malfunction" — get close enough to see the real situation). **Coin distraction + Sleight contest** (Kenji DEX+5 advantage 16 vs dwarf traveler Perception+2 disadvantage 4, margin 12) — unwitting traveler now carries repositioned extradimensional kit past checkpoint (BoH / satchel plant — moral + inspection time bomb elsewhere in queue). **First stamp pass** — clean.
- **Manifest Revision II:** personal lane + resonance spot-check language. Kenji **reads dwarf script + coalition marginalia** via Scribe's Eye (table literacy tool confirmed in play). Forge-sight clerk asks for palms up — **pass**. Mursha covers literacy tell: *Krath — read like that again in public, make it look like you're counting boot laces.*
- **End:** Day 261 afternoon — past Manifest Revision II; approaching cargo reconciliation; Kenji + Mursha clean this beat. ~1385 GP (±trivial coin). HP 368.

### Ch28 played (Ashmere 39 afternoon–evening, Day 261 — prose `fraying_empire_chapter_28.md`)

- **Wind Step breach** past quarantine chain — Kenji separates from Mursha. **Quarantine Forge Three:** dead forge, seam in floor (Hollowing crack — organic, not structural). **Investigation fail** (total 5 vs DC 22 — INT 9 wall). Ley tap strained (sick ley network); **ember surged** — creation nova, gold-green visible. **Forge mistress** challenged at rail (dwarf, decades of service, reads energy categories).
- **Oathbreaker** driven into seam to crossguard — holy/necrotic dual binding pins crack (not cure, wedge). **Frost Fang** second-wedged beside it — entropy vs creation thermal argument; ward chalk fought itself. **Full STR (42)** drove both to hilt. **Entropy mode** fed wrong mouth until mistress read *balancing without healing*.
- **Males warned back** (player line) — aura + entropy field = permanent death risk for males in confined space. Forge mistress held **female-only breath line**; guards disciplined panic.
- **Creation volcano:** Kenji palmed crack, **vented upward** through shaft space — **gold-green conduit visible from upper works and surface yards**. **RONIN COVER COLLAPSED** to witnesses (ArchMagus-grade creation signature). Seam **pinned not healed** (crack smaller, not gone). Hand fused to stone on release (raw palm, stone dust).
- **Player:** *"That's one spicy meatball"* + burp (gallows humor). **Iron-grey elder** (forge owner / crown voice — table names pending) demands **ten words or less** why the forge stopped eating itself. **Beat open for player reply.**
- **End:** Day 261 evening — quarantine forge chamber; elder + mistress + guards; Kenji at seam afterglow. Wind Step 0/5 (heavily spent); spell economy strained; Smoke-Invis-Clone 1/3; Iaido 0/1. HP 368 (or table exhaustion). EXP 2,270,050. Mursha separated — reunion pending.

### Ch29 played (Ashmere 39 evening–night, Day 261 — prose `fraying_empire_chapter_29.md`)

- **Quarantine custody** — Procedure Seven (gender-segregated watch). Female watch assigned; IP cadence running on watchers (DC 23, −1/15 min cumulative). **Sleight + smoke/clone misdirect FAIL** (18 vs DC 23); DM ruling — no bar work unless decoy draws violence; clone dismissed. **Intimidation** 18 vs DC 19 fail (earlier beat).
- **Goat poem / verse** — Performance **nat 20** (+11 = 31 vs DC 21). All male guards laugh uncontrollably; **senior watch (female, ledger)** does NOT laugh. **Persuasion** 29 vs DC 23 — supervised dwarven breakfast + honey mead (clerical cap). Kenji meditates, eats, waits.
- **Bench escort** — clerks (not guards). Escort flirtation + contempt; near-gag-order (custody doctrine voice-restraint citation). **Perception nat 1** vs DC 16 — fails to see **veiled gallery observer** (unidentified).
- **Korrim Stoneunder bench** — elder from forge, now bench authority. Court reads incident record (conduit vent, blades in seam, Mursha partitioned). **Seam light brazier** examines intent: **not malicious surge** (coarse truth, entered); **not intended final blade retention** (entered).
- **Blade provenance volunteered** — Oathbreaker described as "undead paladin greatsword"; Frost Fang as "god sword." Self-contradictory phrasing preserved verbatim by clerks. Kenji: **does not fear bench** (entered); **does not respect procedure** (entered). If he had, he'd have followed **"Mursha's way"** — name forces motion.
- **Mursha summoned** under Haldra-line bind protocol. **Null thread** at throat (measures voluntary vs compelled speech — protection dressed as restraint). Kenji smiled when she entered. Korrim opens her examination under seam light. **Beat open at her first answer.**
- **End:** Day 261 night — Kharn seam-witness chamber; Kenji in prisoner circle; Mursha at witness rail under null thread; Korrim examining. HP 368/368 table. EXP 2,270,050. Purse 1435 GP (sync table). Contempt + menace entries on Kharn slate.

### Ch30 played (Ashmere 39 night, Day 261 — prose `fraying_empire_chapter_30.md`)

- **Examination becomes standoff** — Mursha answers clean under null thread (operational closure: brace vent path → extraction order → ward growth or controlled pin). Kenji **breaks Mursha's restraints by force** (wrist + elbow bindings, STR 42). Chamber calculates; watch stops.
- **Intimidation** 28 vs DC 25 PASS (Sovereign Voice / ADV +11) — throat thread removed by bench order (fiction: "witness clarity ruling"). Wrist/elbow plan voided by defendant action.
- **Creation mode hover** — Kenji lifts off stone floor (3 inches), gold-green light, boots leaving ground. Cover incinerated in real time. Every forge-trained eye reads the signature.
- **Recall claim** — Frost Fang (conjured) can be recalled/unmade from seam. Oathbreaker (physical steel) requires hands. **Seam team dispatched** (4 forge-priests — entropy couplet readings).
- **Mursha engineering** — closure as sequence: brace vent path, choose extraction order (thermal argument is load-bearing), ward growth or controlled pin. Operational intelligence, not magic.
- **Written liability REFUSED** — Kenji compares bench to undead court paper traps (Sir Corwyn analogy implicit). Will not sign into a system that outlasts willingness. Entered as contempt.
- **Collar ordered** → **"Touch me and it's war"** (player line). Bench pivots to **non-contact containment** (glass barriers, ward circles — no skin contact).
- **IDENTITY DECLARED ON RECORD:** **Champion of the Elves, Archmagus of Varenholm Academy** (player-declared titles). Clerks record verbatim. Chamber arithmetic inverts — prisoner is diplomatic figure; contempt entries now carry geopolitical weight. **Rorschach beat** — "trapped with me" power inversion.
- **Coalition relay flagged** (encrypted) — information leaving the mountain. Wards ordered without skin contact. Korrim: "no court stabbing theater" (entered as ruling).
- **Hot meal** — bacon, eggs, mead (clerical cap) — de-escalation triage for Mursha at witness bench. **"Babe — you're going to love the eggs"** (player line) — public intimacy while wards rise.
- **End:** Day 261 late night — seam-witness chamber; non-contact ward protocol; Kenji identity on slate; Mursha at rail (restraints broken, eating); coalition relay in transit; veiled observer still active; seam instrument cadence ongoing. HP 368/368. EXP 2,270,050. Purse 1435 GP.

### Ch31 played (Ashmere 39 late night → Ashmere 40 predawn, Day 261→262 — prose `fraying_empire_chapter_31.md`)

- **Mursha-centered cooperation** — Kenji addresses Mursha as reason he engages; Korrim logs; hour + findings; Solveth speaks publicly at blade (god-voice); proxy permission to Mursha logged under witness.
- **Timeline & tension** — honest closure range (~2–6 days best, up to ~2 weeks risk); Kenji declares two-week patience + ultimatum language; portal attempt canceled under wards; apology/peace beats to Mursha; Korrim **witness-engineer** bundle (parity, returns within hour where safe).
- **Inventory** — nodachi + Bag of Holding verified returned per receipt; seam blades remain wedged (not in BoH).
- **Egress** — **Performance** 23 vs DC 16 PASS (tap-dance clone); **Stealth** ADV 18 vs DC 16 PASS (Greater Invis + distraction); Wind Step distance; ~3 mi green portal off beaten path.
- **End:** Day 262 predawn — Kenji remote off relay path; Mursha on closure duty at Kharn; relay breach flags likely; Solveth in seam work. HP 368/368. EXP 2,270,050. Purse 1435 GP. Smoke-Invis-Clone 1/3; Wind Step 1/5.

### Ch32 played (Ashmere 40 morning, Day 262 — prose `fraying_empire_chapter_32.md`)

- **Milepost Crown Rest** — nearest crown relay inn; luxury suite, ley-steam bath, fine dining to room.
- **Ledger** — ~40 GP + 10 SP (table approx; sync `kenji_state.json`).
- **Long rest** — spell slots full, HP 368/368, Wind Step 5/5, Smoke-Invis-Clone 3/3, Iaido 1/1.
- **End:** ~07:30 Ashmere 40 — rested; gossip/recognition risk at waystation; relay may catch up.

**Cross-ref:** `arcs/north_relay_two_chapter_plan.md` — north fork spine + **§ Canon played — Ch18–Ch33** (prose Ch22–33 in `Book 4/Chapters/`).

### Ch33 played (Ashmere 40 mid-morning → late morning, Day 262 — prose `fraying_empire_chapter_33.md`)

- **Portal to Pallid March** — Kenji portals from Crown Rest area to undead territory relay point; walks the last 3 miles. Living Ground reads terrain shift at perimeter border.
- **Lady Nyx audience** — human form in dead village square. Corwyn present (one arm, no Oathbreaker). Conversation: Hollowing = appetite not wound (Nyx confirms via root network); Kharn rift is hunger, not structural; dwarves treating symptom wrong. Nyx cannot close it either.
- **Name reveal** — disposition gate met (neutral+). Nyx speaks true name: "Nyx." First living person to hear it in centuries.
- **Solveth relay** — Kenji pushes Hollowing intel to Mursha via Frost Fang bond (thin connection, impression not transcript).
- **JKD combat spar** — Kenji drops nodachi, removes hakama top, challenges Nyx unarmed. **Round 1:** Performance 30 vs DC 18 PASS (Spirit Aura). All 6 strikes hit. Kick 3 knocks prone (DEX 22 vs 23 FAIL). Nyx at 238/720 HP. KO save 23 vs 23 — holds by zero. **Round 2:** Kenji showboats only (no attacks). Performance 20 + 23 vs DC 18 PASS/PASS. Nyx attacks into disadv + 75% dodge — 1 of 3 lands (22 necrotic, healed by regen). Counter 1 stuns (CON 15 vs 23 FAIL). Counter 2 triggers KO save: 14 vs 23 FAIL. **Nyx knocked out in 2 rounds.**
- **Diagnostic Touch readout** — Kenji reads Nyx's biology through combat contact: 1% metabolism, 11-sec heartbeat, reinforced bone density, zero cellular turnover, ley-pool IS circulatory system, anchor structure behind heart (phylactery-equivalent terminus), 4th cable frayed/parasitized.
- **Five kingdoms briefing** — Nyx describes regional powers: Coalition (13 portal-cities), Kharn-Dural (dwarves), Iron Horde (orcs, ~60K, Gorath), Red Court (vampires, institutional), Twin Wyrms (sleeping, southern range).
- **Alliance proposal** — Kenji proposes: mate/partner, advisor role, title "Anku Nyx," Corwyn rebuilds village for living, March does not expand. Nyx counters with 3 conditions: (1) Corwyn's chain is hers, (2) March holds for now not forever, (3) eye contact during intimacy. Kenji accepts. Declares: "Call me Anku Nyx, we do not die."
- **IP tracking** — 6 saves across ~75 min viewing. Saves 1-3 PASS. Save 4 (45 min, −3): d20=5, FAIL → Stack 1. Save 5 (60 min, −4): **NAT 1**, FAIL → Stack 2 (Moderate Attraction). Save 6 (75 min, −5): d20=18, PASS. **Nyx at Stack 2 end of chapter.**
- **End:** Day 262 ~11:00 — Pallid March, Nyx's dead village square. Alliance terms set. Intimacy pending (Close to Death math favors survival). HP 368/368. EXP 2,270,050. Purse 1395 GP / 181 SP. All charges at LR values.

### Ch34 played (Ashmere 40 late morning → Ashmere 47 dawn, Day 262→269 — prose `fraying_empire_chapter_34.md`)

- **Seven Days** — Kenji and Nyx to her chamber. Corwyn guards door for 7 days straight.
- **Close to Death survived** — regen 61 HP/sec vs 3.68 HP/sec drain. First survival in setting history. Kenji never lost consciousness.
- **Vigor stacking 1→7** — unprecedented. Sustained intimacy prevented Vigor expiration. Geometric multiplication each day. By Day 7, Nyx operating at god-tier stats. Castle structurally damaged. 612 undead prostrated by signal overflow. Root network transmitted resonance across full 32-mile perimeter.
- **Kenji HP** dropped to ~10% (36/368) on Day 7 — not from Close to Death (irrelevant to regen) but from physical output with Vigor 7-enhanced partner. Regen recovering.
- **Nyx breaks first** — final climax overloads her vessel. Teal shockwave flattens dead trees at perimeter edge. Falls into deep sleep (real sleep, not stasis). Vigor 7 metabolizing.
- **ANKU NYX EMERGED** — Kenji transformation post-7-day contact:
  - **Green aura** (permanent) — creation + death-dominion fusion. Not gold-green (ember), not teal (Vigor). New spectrum.
  - **Green eyes** (permanent) — no longer hazel. Luminous, sinister, glowing.
  - **Ember evolved** — now burns in two spectrums (creation + death-dominion). Not Apotheosis. Something adjacent.
  - **Soul Conqueror** (Nyx Soul Nexus bond #23) — all 7 Vigor stacks reflected into Kenji's own stats via Nexus. Permanent integration.
  - **Root network authorization** — Pallid March territorial system recognizes Kenji's signature.
- **Corwyn** — 7 days at the door. On his knees by Day 7. Unbroken. Heartbroken. Recognizes the shift.
- **Nyx now Bonded Partner #23** — Unsatisfiable applied (permanent). IP-immune via Vigor (extended duration given Vigor 7). Close to Death contagion no longer a threat to Kenji.
- **End:** Day 269 ~06:00 dawn — Nyx's castle great hall; Kenji in queen's chair; green aura; green eyes; HP recovering; Nyx asleep in chamber; Corwyn at door. EXP 2,270,050. Purse 1395 GP / 181 SP.

### Ch35 played (Ashmere 47 dawn → mid-morning, Day 269 — NO PROSE FILE, played live)

- **Morning with Nyx** — Kenji returned to bed until she woke. No regrets. Morning intimacy (missionary, ~1 hour). Nyx's metabolism climbed during; network pulsed castle-wide.
- **Corwyn consciousness restoration** — Kenji touched Corwyn's head in meditation. Creation energy conducted through root network without breaking enthrallment lattice. Restored FULL consciousness (was partial — see Corwyn entry). Corwyn now fully sentient, fully aware, choosing to serve rather than compelled. Chain intact, Nyx's authority intact, but the man underneath is *all the way back.*
- **Corwyn flesh facade** — Two attempts. First: brute-force creation energy, lasted 11 seconds, faded. Second: grafted a self-sustaining draw onto the ley-line network — flesh facade feeds on ambient magic. In ley-rich territory (the March), holds indefinitely (decades). Away from ley sources, degrades (weeks in dead zones, months near minor rifts, years near major ley lines). Corwyn now appears as a living man in his fifties — scarred, weathered, ruined arm still ruined but covered in real-looking skin. **Can blush.** Was deeply embarrassed by subsequent conversation and excused himself to patrol.
- **Nyx backstory revealed (Close to Death origin):** Death-dominion wellspring. **Innate trait since age 19** — not a curse, not a disease. One in ~100,000 births. First lover died in her bed. Second died three months later. Third — she knew. Saw a hedge witch (not a curse), an elven diviner (innate, like eye color). Built the Pallid March to surround herself with things she couldn't kill. Every thrall except Corwyn was originally a lover. **"I built a kingdom out of things I could not kill because I was tired of killing things I loved."**
- **Vigor self-restoration explained** — Kenji told Nyx she has 35 days (7 stacks × 5 days) of creation energy already inside her. Self-directed — she can restore her own biology, heal the architecture back to living tissue, without needing Kenji to do it for her. Renewable on intimacy. Nyx: "How often can the Vigor be renewed" = *how often would you come back.*
- **IP / Soul Nexus / Vigor mechanics** — Kenji explained the full system to Nyx in clinical detail. Corwyn was present and sentient for this. Corwyn's ears turned red. Nyx dismissed him to patrol the perimeter.
- **Iron Horde strategy** — Kenji proposed orc kingdom as next conquest target. Nyx briefed: 60K strong, Gorath, bloodline authority (11 generations), clans follow chief absolutely, no external conquest recognized. Nyx deduced plan: **marriage conquest** — Nyx appears alive (Vigor + self-restoration), Kenji defeats Gorath in single combat, union provides bloodline claim. Nyx: "You're not conquering the Horde with an army. You're conquering them with a *marriage.*"
- **Nyx: "I am keeping you."** — Final line of the chapter. Disposition: locked.
- **New creation abilities demonstrated:** (1) Consciousness restoration on undead via creation+death-dominion dual spectrum. (2) Self-sustaining flesh facade on undead, ley-energy powered. Both unprecedented.
- **End:** Day 269 ~09:00 mid-morning — Nyx's castle great hall; strategy table; Corwyn patrolling perimeter (living face, full consciousness, embarrassed). Nyx clothed, braided, at table. EXP 2,270,050. Purse 1395 GP / 181 SP. All charges at LR values.

### Ch36 played (Ashmere 47 mid-morning, Day 269 — NO PROSE FILE, played live)

- **Arcane Sprint to Varkûl** — Nyx on Kenji's back. L6 Arcane Sprint + Soul Conqueror stats. **460 miles in ~7 minutes.** Crossed Pallid March (40mi, under 1 min), Ashfield Barrens (dead grassland), eastern steppe. Broke sound barrier — sonic boom, trail of craters visible for miles. Orc patrol camp saw green streak cross the sky. Nyx experienced joy (smiled against his neck, first time in centuries). Decelerated on ridge overlooking Varkûl, 4 miles out.
- **Speed test prior to sprint** — Kenji crossed quarter-mile clearing in under 2 seconds (base speed, no magic). Nyx ran same in ~3 seconds (DEX 239 from Vigor stacks, network-assisted landing). Both confirmed: post-Soul Conqueror physical capabilities are god-tier.
- **Nyx briefed plan** — "Gritty, unpleasant, effective." No exact script. Nyx agreed to follow Kenji's lead. Her one condition: tell her before using Close to Death on someone. Kenji: "I will never tell you how to use your abilities."
- **Varkûl south gate** — Two gate guards. Older guard (scarred, filed tusks, 15 years gate duty) and nephew Tuska (young, proud). Kenji insulted both. Called guard dumb, compared orcs to pigs. Guard offered **sacred processional law** (ancient right: any challenger who demands combat with chief by name gets safe passage to iron hall). **Kenji rejected the law.** Slapped the older guard in the face (Performance +165, calibrated STR to humiliate not harm). Guard whistled for backup.
- **Gate fight (JKD, no weapon drawn)** — Kenji KO'd 8 orcs in sequence: Tuska (palm strike under jaw), older guard (caught axe one-handed, temple strike), brawler (straight lead to solar plexus, lifted 400lb orc 6 inches off ground), 2 axe-orcs (ankle sweep + double temple strike), 2 hammer-orcs (trap-punch-kick combo + caught hammer mid-swing), mace-wielder (saw the math, put mace down, went to get the chief). All knockouts — zero kills, zero weapon draws. Every hit calibrated via Performance to demonstrate overwhelming superiority without lethal force.
- **Gorath arrived** — Iron Horde chief. 8ft tall, 8ft wide, green-grey skin, massive tusks, covered in scars. Carrying **the black axe** (double-headed, dark iron, the ceremonial challenge weapon). Assessed the seven bodies, assessed Kenji, assessed Nyx.
- **The bait** — INT +71 analysis of orc culture: a man who sends his wife to fight = ultimate cowardice. Orc response to cowardice = maximum humiliation. Victor claims the defeated woman as property, publicly, then deals with the husband. Kenji: "My wife Nyx could take you out. I won't even step in to help her." Performance +165 — delivered as genuine dismissal, not strategy. Crowd reaction: visceral contempt. Kenji became the most hated man in Varkûl. **Exactly as planned.**
- **Gorath took the bait** — "A man who sends his woman to fight his challenge forfeits everything. His name. His claim. His *property.* When I break her, she is mine. And you will watch." Walked past Kenji toward Nyx.
- **Kenji whispered to Nyx** — "The leader is going to fight you, do not defeat him, let him have his way and win." Nyx understood instantly: Gorath wins → claims her → Close to Death activates naturally → chief dies from his own culture's brutality. Not an order to kill. An arrangement where the kill happens by itself. Nyx nodded. Called it "the most ruthless thing anyone has ever asked me to do" without asking her to kill anyone.
- **Blood circle formed** — Orc spectator ring, 30ft diameter. Thousands watching. Gorath vs Nyx (Lady form, performing vulnerability). Nyx in position — two centuries of predator disguised as prey.
- **CLIFFHANGER:** Gorath raises the black axe. Nyx in the circle. Close to Death trap set. Kenji watching from outside the ring.
- **Spell slot spent:** L6 Arcane Sprint (1/2 remaining).
- **End:** Day 269 ~10:00 morning — Varkûl, south gate blood circle. Gorath vs Nyx (staged loss). Kenji outside ring. Thousands of orcs watching. EXP 2,270,050. Purse 1395 GP / 181 SP. L6: 1/2. All other charges at LR values.

### KORRIM STONEUNDER — Elder bench authority, Kharn-Dural (Ch28–31)

**Status:** alive  
**Met:** yes — Ashmere **39** Day **261** (Ch28 forge, Ch29 bench)  
**Role:** Clan-crown authority; elder with jurisdiction over quarantine Forge Three. Iron-grey beard, braid pattern = clan-crown (not forge worker, not factor clerk). First appeared demanding ten-word explanation in Ch28; presides over seam-witness bench in Ch29. Uses seam light brazier for intent examination. Assessed Kenji's conduit as "not malicious — coarse truth" and blade retention as "not intended."  
**Disposition:** judicial — neither hostile nor sympathetic. Treats Kenji as a problem the system must process. Gave Kenji the bench (process), not the chain (arrest) — but contempt entries are stacking.  
**Morale Compass:** Lawful Good — serves the mountain's law and his people's safety. Will protect Kenji from mob response if the law says to; will punish him if the law demands it. The bench is sovereign. His personal opinion of the prisoner is irrelevant until the bench closes.  
**Last Updated:** Ashmere **40** / Day **262** — Ch31 *Two Weeks and a Green Door*

#### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| bench_verdict | Ashmere 39 | Ashmere 40 | immediate | active | Determine the legal status of the masked human who breached quarantine, drove foreign blades into the mountain's seam, and vented a creation conduit through the upper works. **Ch31 update:** Kenji exited under decoy/invisible breach — relay flags likely; legal status **more** fraught (fugitive pressure vs prior custody). Mursha remains witness-engineer on closure. Veiled gallery observer still live. | Verdict / relay response determines Kharn + coalition posture. Blade extraction politics follow — removing Oathbreaker + Frost Fang may destabilize the pin. |

---

### MARTHEL — Smith, Bronzebarrow forge row (**Ch19**)

**Status:** alive  
**Met:** yes — Ashmere **35** (**Mursha** armor beat)  
**Role:** **relay** smith; sold **“junk”** **dragon-scale** **medium** **armor** **10 GP**; **refused** **Oathbreaker** **reforge**  
**Disposition:** wary-professional — paid, spooked by **BoH** sword  
**Morale Compass:** Lawful Good — dwarven-trained smith; respects steel, respects coin, respects the customer who pays fair. Opposes Kenji if Kenji asks him to cut corners or forge something he shouldn't.  
**Last Updated:** Ashmere **35** (`kenji_state.json` **npc_states**)

#### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| oathbreaker_memory | Ashmere 35 | Ashmere 40 | N/A | active | A masked ronin pulled a **holy/necrotic greatsword** out of a bag and asked him to reforge it. He refused. The sword hurt to look at. He hasn't forgotten. If anyone asks about unusual weapons or unusual customers, he has a story. | Adds to **ronin_identity_pressure** — a relay smith who saw a blade that shouldn't exist in a bag that shouldn't hold it. Cross-cuts with Cassia's investigation if yard gossip connects "ronin with impossible sword" to "ronin who released Mursha same day coffer walked." |

---

### TAMSIN VALE — Coalition tally scribe (**Ch25–26**)

**Status:** alive
**Met:** yes — checkpoint desk (Ch24 ambient) → berm private beat (Ch25) → Kharn upper gallery niche (Ch26)
**Location:** Kharn-Dural upper works — routed away from Kenji toward scribe quarters after niche encounter. **Ashmere 38 predawn Day 260**.
**Last Updated:** Ashmere 38 / Day 260 — **Ch26** copper ring

**Physical / voice:** Human woman. Ink-stained fingers, clerk posture, brown eyes. **Lover's Vigor active (Ch25 trigger):** fine copper-bright ring at pupil — visible in Ch26 niche lantern. +50% stats ~5 days. IP-immune vs Kenji ~Day 265 / Ashmere ~43.

**Disposition to Kenji:** Hostile-professional. Taught him to read (80 GP for chalk marks — $400,000 in relay economy). Experienced IP firsthand (severe — private, prolonged, berm). Vigor tell horrified her (*Don't name it*). Routing future contact on her terms (*Letters need routes. Ronin isn't a route*). Threat dressed as memory (*I'll remember. Don't make me use it*).

**Morale Compass:** Lawful Neutral — paper is armor; procedure is faith; routing is survival. Will file, withhold, or weaponize information depending on which serves her position. Not cruel — accurate.

**Identity pressure vector:** Five data points on the ronin — illiteracy arc, 80 GP payment capacity (wealthy for any sell-sword), IP effect (experienced firsthand in two settings), "the ronin" as self-identifier with no yard/factor attached, berm beat. +2–4% ronin_identity_pressure if she talks. A clerk with five data points and a memory threat can file a report that interests factor houses, checkpoint officers, or anyone looking for a man who doesn't add up.

**Pregnancy:** One qualifying exposure (Ch25 berm beat, IP + private + Vigor triggered). Pending — no roll logged. DM resolves per pregnancy tracker rules.

#### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| letter_routing | Ashmere 38 (Ch26) | open | N/A | active | Find a way to route a letter "to the ronin" — the contact offer Kenji made twice (Ch25 walk, Ch26 niche). She accepted the task: *I'll find one.* No route exists yet; ronin is not a factor address. | If successful: future contact vector (lessons, blackmail, factor trap, or genuine professional relationship — DM chooses). If intercepted: identity pressure spike. |
| vigor_window_survival | Ashmere 38 (Ch25) | ~Ashmere 43 / Day 265 | N/A | active | Survive ~5 days of Lover's Vigor with a copper-ring tell in coalition scribe spaces where dwarven/coalition observers may know vigor lore. She knows the window (*Five days*). Manage exposure of the tell. | After expiry: IP immunity drops; aura returns at full force if proximity resumes. Copper ring fades. Shame arc resolves or compounds. |

---

### CASSIA VORN — Factor, Iron Mule Freight (Bronzebarrow yard)

**Status:** alive  
**Met:** yes (Day **256**, IC via **Mursha** escort + Kenji **invis** overwatch)  
**Location:** **Iron Mule** factor **office**, Bronzebarrow — **Ashmere 35** morning **ledger crisis**  
**Last Updated:** Ashmere 35 (`kenji_state.json` **npc_states**)

**Physical / voice:** `npc_appearance.md` § **Cassia Vorn** (stub — no portrait lock yet); table: **ledger-first** operator, **neutral** → **hunting** once **floor coffer** + **relay float** vanish.

**Disposition to Kenji:** **Unknown** — she dealt with **Mursha** + **silent illusion-double**; **not** proved as **thief** yet; **same-day** **Mursha** release + **theft** = **pattern** risk if anyone **correlates**.

**Morale Compass:** **Lawful Neutral** — contract, stamp, **clawback** language; **professional** panic when **cash** **walks**.

**Ch18 threads:** Open **investigation**; possible **yard gossip**, **Coalition** wires, **inside-job** suspicion vs **pro** **thief** profile.

#### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| coffer_investigation | Ashmere 35 | **Ashmere 40** | N/A | **active** | Floor coffer + relay float **gone** — morning count Ashmere 35 confirmed. **Inside job** vs **pro thief** profile. Cassia's first move: **audit who was in the building** the day before. Mursha's same-day release + ronin's same-day visit = **timeline correlation** she hasn't drawn yet but will. | If she connects ronin + Mursha + missing coin: formal **complaint** to yard captain → **Coalition factor wires** → ronin description enters the network. Feeds **ronin_identity_pressure**. If she doesn't: investigation stalls on "professional job, no leads." |
| factor_wire_report | Ashmere 36 | **Ashmere 38** | Ashmere 38 | **active** | Standard **factor loss report** to Iron Mule central and Coalition relay office — cash loss above threshold requires paper. The report describes the **amount**, the **method** (no forced entry), and anyone **in the building** that day. | Paper enters a system where clerks cross-file. If ronin's description matches any other report (Thornkeep, Millhaven, relay corridor), the **cross-cut** fires. |

---

### HALDRA — Dwarf factor clerk, Brass Hitch (Ch22–23)

**Status:** alive  
**Met:** yes — **Brass Hitch** Ashmere **36** (Ch22 — desk + private parlor)  
**Location:** **Bronzebarrow** — Brass Hitch factor corner, Ashmere **37**. Kenji + Mursha departed north (Ch23); Haldra remains at her desk.  
**Last Updated:** Ashmere 37 / Day 259 — **Ch23** (paper handoff, guard contract, tube read-aloud)

**Physical:** `npc_appearance.md` § **Haldra** — Full-figured dwarf woman; wide hips, heavy bust; rich chestnut-red/auburn twin braids past shoulders with bronze ties; clear blue eyes; fair warm-toned cream-and-rose skin; forge-flush on cheeks/nose; dark fitted pinafore-apron over white blouse; tool-pouch (quill case, seal-wax stick, folding rule). **Refs:** `haldra_brass_hitch_clerk.png`, `_back.png`; intimacy `haldra_offduty_intimacy_reference.png`; post-vigor `haldra_post_vigor_reference.png`.

**Disposition to Kenji:** **Intimate** — IP failed ×2 (DC 23 desk + transit); Persuasion ADV 20 vs DC 19 extended consent in private parlor; verbal intel briefing (Kenji INT 9). Professional composure rebuilt between parlor and desk. **Lover's Vigor active** — brass-amber eye ring tell; +50% stats; IP-immune ~Day 263 / Ashmere ~41.

**Morale Compass:** **Lawful Good** — clerk discipline; respects paper, process, and accuracy. Factor-house territorial about her desk and her information. Cooperated with Mursha because Mursha spoke the right professional language. Opposes Kenji if he misuses the intelligence she provided or puts her desk at risk.

#### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| north_courier_contract | Ashmere 36 | Ashmere 40+ | N/A | **active** | Ch23: Mursha signed guard contract through Haldra for north courier run toward Kharn-Dural. Haldra facilitated the paper + sealed tube read-aloud. Professional broker role between factor network and traveling party. | Haldra becomes information anchor at Bronzebarrow for Kharn-Dural paper thread. Return visits or courier messages route through her desk. |
| vigor_window_active | Ashmere 36 | **~Ashmere 41** | N/A | **active** | Lover's Vigor on — brass-amber eye ring tell; +50% all stats; IP-immune to Kenji for ~5 days (~Day 263). When it expires: urge returns at full stack pressure; she may want the power back. | Expiry resets IP vulnerability. Dwarf clerk with factor-house memory + Kenji oral briefing in her head = intel value + attraction compound. |
| kharn_paper_knowledge | Ashmere 36 | ongoing | N/A | **active** | Haldra holds verbal + written knowledge of: vault/seal discrepancy, clerk names who signed/refused/vanished, suspected factor-house laundering under coalition wax, Varenholm silence margins, yard observation patterns. She spoke all of this to Kenji (verbal only — he can't read). She also received the merged ridge + parlor intel from Mursha on paper (Ch23). | Information broker value. If anyone asks the right questions at her desk, she has answers that connect the western cut leak to Kharn-Dural internal corruption. |

**DM — pregnancy (not IC):** **`pending_assessment`** in `kenji_state.json` — **one** exposure logged (Ch22 Day 258 private parlor; Vigor triggered); **no roll** — **DM** resolves. See **§ DM — PREGNANCY TRACKER**.

---

### MURSHA — Half-orc, ex–Iron Mule guard (Bonded **#20**)

**Status:** alive  
**Met:** yes — **Brass Hitch** Ashmere **34**; **intimate** (see `relationships.Mursha` in `kenji_state.json`)  
**Location:** **Kharn-Dural outer checkpoint** (admitted line), Ashmere **38** Day **260** (`kenji_state.json` when synced).  

**Appearance (canon — expand in `npc_appearance.md` § Mursha):** Half-orc body built like a **spear-line lieutenant** — **exceptionally muscular** (**heavy shoulders, arms, lats**; **visible core** when unarmored; **narrow waist**; **very powerful thighs and glutes**). **Pale olive–green** skin, **warm** undertone; **jet-black** hair in **tight cornrows** feeding **thick braids** banded with **silver rings**; **long pointed ears** with **silver hoop** earrings (off-duty/suite); **small steel-capped tusks**; **dark brown** eyes; **bronze-gold** ring at pupil when **Lover’s Vigor** active. **Scars:** vertical **right brow**, small **right cheek**. **On duty:** minimal **dark breastplate**, **right pauldron**, bracers, **olive/tan wraps**, **thigh straps/buckles**. **Suite / private:** may wear **white or teal lace** lingerie; **black** nail polish; lamplight **sheen** on muscle. **Prose:** prefer **named anatomy + light + jewelry + scars**, not generic “buff woman.”

**DM — intimacy quirk (Mursha / Kenji):** On **any** intimate beat between them, layer **creative ambient hints** that she may have been with **other men earlier that day** (scent, texture, timing, stray detail); **Kenji never** calls it out in-scene. Ties to **Power of P** / hidden intel habits — not retconned without player buy-in on specific NPCs.

**DM — anger/dialogue quirk (Mursha):** When angry, frustrated, or under pressure, Mursha drops **short orcish curse-words** (invented, guttural, 1–3 syllables: *krath*, *vol-sha*, *drekk*, etc.). The curse is **punctuation, not the sentence**. The **meaning** must come from the **plain English** line that follows or surrounds it — concrete, clear, paraphraseable. **Pattern:** [orcish expletive] + [clear English that carries the actual meaning]. **Test:** cover the orcish word; does the English still make complete sense on its own? If not, rewrite the English. **Bad:** vibe-shaped lines where individual words are thematically adjacent but the sentence dissolves when you ask what she's actually saying. Mursha is a guard, not a poet — her lines should be blunt and parseable.

**Baseline ability scores (before Lover's Vigor +50%):** STR **22** **(**+2** **Power** **of** **P** **Day** **257** **lieutenant**)**, DEX **16**, CON **20**, INT **10**, WIS **8**, CHA **14** — `kenji_state.json` **`soul_nexus_registry.Mursha.baseline_ability_scores`**.

**Soul Nexus (Bond #20 — Kenji):** **`kenji_state.json`** **`soul_nexus_registry.Mursha`**  
- **Bloodlust:** **+25%** **all** **stats** **per** **killing** **blow** **Mursha** **scores**; **stacks** **additively**; **ends** **end** **of** **combat**. **Replaces** **Yard** **Truth.**  
- **Power** **of** **P** **(Barbarian** **Ways):** **interrogation** **via** **mating** **male** **humanoids** — **cannot** **lie** **to** **her;** **auto** **truth** **sense;** **STR** **or** **CON** **save** **vs** **DC** **8+PB+matching** **Mursha** **mod** **to** **negate;** **on** **orgasm** **Mursha** **+2** **permanent** **to** **their** **highest** **ability** **(**once** **per** **unique** **mate**)**. **Log** **`mursha_power_of_p_log`**. **Replaces** **Escort's** **Anchor.** **Full** **rules** **`dm_rules_tracking.md`** **§** **Mursha** **—** **Soul** **Nexus.**

**DM — Mursha default after battle:** **Strongest** **male** **humanoid** **captive** **→** **private** **Power** **of** **P** **for** **intel** **(**not** **in** **the** **open**)**. **Hides** **it** **from** **Kenji** **(**excuses,** **shame** **—** **not** **betrayal**)**; **Kenji** **may** **still** **see** **via** **Stealth** **/** **invis** **/** **overwatch**. **If** **Kenji** **names** **the** **method** **/** **orcish** **ways** **/** **orders** **her** **to** **use** **it** **—** **she** **refuses** **(**human** **side** **won’t** **perform** **it** **once** **spoken**)**.

**Gear:** **dragon-scale** **medium** **laminate**; **masterwork** **longsword** **+3**, **3d12** **slashing** (**2H:** **add** **Str** **mod** **again** **to** **damage**); **masterwork** **warhammer** **4d8** **bludgeoning**, **versatile**, **armor** **break** (**2H:** **add** **Str** **mod** **again**). **Full** **wording** **`dm_rules_tracking.md`** **§** **Mursha** **—** **masterwork** **weapons**. **~400 GP** **gift** **untouched**.  
**Last Updated:** Ashmere 38 / Day 260 — Ch24 (Mursha fronted gate line; BoH near-miss deferred; Oathbreaker ask deferred)

**Disposition to Kenji:** **Intimate** — **Vigor** **~Day 261**; **IP-immune** vs him for window; **saw** **clone** **flicker** (**magic** **twin**); **Deception** on double **failed** — she **knows** **something** **wrong**, **stayed** anyway. **Children:** he **asked**; she **did not** **promise** in **steam**.

**Morale Compass:** **Neutral** — **contract** **mind** reframes **choice**; **values** **honest** **mouth** on **“free”**; will **walk** if **lied** **to** about **terms**.

#### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| decide_road_or_town | Ashmere 35 | **Ashmere 37** | N/A | **resolved** | **Ch23:** Signed **Haldra-line factor guard** contract for north Kharn courier; rides with Kenji under **professional** cover (not yard re-hire). | **Road** locked — Hollowing / Kharn-Dural corridor; relationship proceeds via proximity + duty. |
| oathbreaker_question | Ashmere 35 | **Ashmere 38** | N/A | **active** | *Where'd you get that?* — asked at Marthel's forge (Ch19) when Kenji pulled Oathbreaker from BoH. Unanswered. If not addressed by Ashmere 38, contract mind files it as **deliberate evasion** (disposition −2). | If answered honestly: trust stress (holy/necrotic greatsword from a dead knight's camp). If deflected: she notes the deflection. If ignored past due: silent disposition hit. |
| clone_flicker_filed | Ashmere 34 | ongoing | N/A | **active** | Saw the clone flicker during Brass Hitch swap (Ch18). Persuasion kept her following but she **knows** something was wrong — a magic twin, a shimmer, something not right. Filed, not confronted. Compounds over time. | If Kenji uses clone/illusion again in her LOS: the filed observation becomes a confrontation trigger. |
| power_of_p_secret | Ashmere 35 | ongoing | N/A | **active** | She does not know Kenji watched her Power of P interrogation of the ridge lieutenant (Ch20, Greater Invis at 30 ft). He has not named what he saw. Three-layer asymmetry: she carries two secrets (flicker + oathbreaker), he carries all three (flicker + oathbreaker + the watch). | If he names it: trust stress — she hid it, he watched it. If he stays silent: the secret compounds. Asymmetry persists until one of them breaks it. |

**DM — pregnancy (not IC):** **`pending_assessment`** in `kenji_state.json` — **two** exposures logged (Ch18 Day 256 + Ch21 Day 257–258); **roll** or **narrative** **lock** **pending**. See **§ DM — PREGNANCY TRACKER**.

---

## BRACKEN — Watch Captain, Millhaven Garrison (LEGACY — DO NOT USE CH17+)

> **TRACKER SPLIT NOTE:** **Millhaven watch captain** = **Hadley**. **Thornkeep garrison commander** = **Renna Bracken** (`npc_appearance.md`). This block is **legacy naming** — **not** the Ch17 office source of truth.

**Status:** MIA (consolidated — all **live** Ch17+ commander beats and goals live under **COMMANDER RENNA BRACKEN — Thornkeep** below)
**Met:** yes (historical — Ashmere 22–24 Millhaven)
**Location:** Millhaven (historical); **does not** track Thornkeep play
**Last Updated:** Ashmere 33 (MIA per goal invariant — avoid duplicate “alive” commander)

**Physical:** See npc_appearance.md
**Disposition to Kenji:** Allied/Professional — aura exposed across debrief but NO intimacy. Professional trust developing. Personal filter not compromised.
**Morale Compass:** Lawful Good — watch captain to his bones. Upholds the law, protects the town, reads intent before swinging. Opposes Kenji if Kenji becomes the predator. Stands his ground on due process, the safety of Millhaven, and lies told to his face.

**Abilities:** Captain's Read (reads intent, rank, allegiance, lie-tells on sight), Bond-Form Sight (reads binding geometry, termination, feeder of any binding contract), 19 years watch-captain experience, Ashenmere-trained (clerk in form-room summer 1228), Coalition liaison authority

**Important Gear:** Watch brooch, seax (sword), half-plate over linen, bond-form connection to Kenji

### Active Goals

*None — entry **MIA**; see **COMMANDER RENNA BRACKEN — Thornkeep** for operational commander goals.*

---

## TARYN — Fighter / Commissioned Scout

**Status:** alive
**Met:** yes (Ashmere 22 — Millhaven gate, multiple interactions through Ashmere 24)
**Location:** **Millhaven** — gate circuit / guild hall orbit (back from Ashenmere intake run; **Letter of Commission** filed **received** end of Ashmere **27** — see goals)
**Last Updated:** Ashmere 34 (table correction: delivery goal clarified — nondelivery arc **retracted**)

**Physical:** See npc_appearance.md (pending entry). Late twenties, lean, dark hair, muscular. All scars healed by Kenji's creation energy (burn scar on wrist gone, scar across eyebrow gone, old ankle/shoulder injuries healed). Looks ~20 after healing.
**Disposition to Kenji:** Intimate (score 45) — knows the **cold-hand** tell, knows the **clone** wasn't real; knows his **first name — Kenji** (spoken trust, not public use). Did not chase. Kept the career.
**Morale Compass:** Lawful Good — commissions scouts, reports up the Coalition chain, pays his debts. Opposes Kenji if Kenji undermines the Coalition or leaves civilians undefended. Stands ground on contract, rank, and the scout's code.

**Abilities:** Halberd combat (12 forms), Action Surge, Reaper's Chain (cascading multi-hit), Polearm Defense (free dodge), Victory Rush (full heal on kill), Grievous Wounds (mythril edge bleed 15% max HP/turn/stack). Level 9.

**Important Gear:** Holsk's custom thrum-alloy halberd (Featherfall / Truestrike / Bondseal runes), refitted mythril half-plate (dark steel / blue-silver sheen). **Letter of Commission** — **delivered** to Coalition clerk intake Ashmere **27** (original returned to her file-stamped or copy retained per clerk practice); **475g** paid; **5,000g + seat** still **pending council review** (slow politics, not “lost in the mail”).

**Vigor Status:** **EXPIRED end of Ashmere 26** (5-day window from Ashmere 21 evening). **Ashmere 31:** Taryn fights at **baseline** STR/DEX; halberd carry may strain — verify encumbrance at table.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| deliver_commission_letter | Ashmere 24 | Ashmere 27 | Ashmere 30 | **resolved** | **Canon (table Apr 2026):** Taryn’s job was always **hand off border/undead intel** to Coalition intake — career step from gate guard, backed by **wolf slaughter proof** + **new kit**. She **made the window**: filed **Ashmere 27** (travel off-screen after Ch5 street beat). **Not** “mystery nondelivery” — prior **`closed_overdue` / nondelivery fork was AI bookkeeping error**, retracted. | Council stack now holds her packet; **political** follow-through is separate from “did she deliver.” |
| coalition_seat_review_pending | Ashmere 27 | **TBD** | N/A | **active** | Bureaucratic **5k + recognition** grind; may summon her again; does **not** mean the intel never arrived. | Hooks Ashenmere politics / `ashenmere_council_pressure_arc.md` when promoted. |
| answer_coalition_nondelivery | Ashmere 33 | — | — | **superseded** | **Retracted** — replaced by honest **`resolved`** delivery row above. Do **not** spawn clerk-harassment beats from this ID. | — |
| taryn_post_vigor_kit | Ashmere 26 | **TBD** | N/A | **active** | **Lover's Vigor ended** ~Ashmere **26** (from Ashmere 21 intimacy window). Holsk fitted **thrum halberd + mythril half-plate** to her **buffed** STR/DEX; at **baseline** the kit is **wrong-weight / wrong-balance** — not useless, but **slower**, **harder to clear**, **more exhausting**, possible **AC or attack penalty** at table until refit, partial swap, or **second vigor window**. Pride vs asking for help = character beat. | Bad day on patrol = obvious hook; Holsk scene; guild assigns her **lighter** duties (insult + relief); or she **pushes** and risks injury — DM picks. |

**NOTES (Vigor → gear — this is a *problem*, not flavor):** Stat drop is **STR 24→16, DEX 21→14**. The **Ch5 wolf/warg showcase** was earned skill — but the weapon/armor were spec'd while she was **stronger than her career baseline**. After vigor: polearm **length/weight class** and plate **mobility** fight her; long fights **gas** her faster; she may need to **leave pieces in the chest** or run **non-standard** form until Holsk refits. **IP / aura:** she is **no longer vigor-immune** — DC 23 viewing rules apply again if Kenji is in LOS (see `kenji_state.json` + IP rules).

### What “mission complete” *means* for the story (DM — pay this forward)

**Do not treat filing as “checkbox done, world unchanged.”** It moves these levers:

1. **Truth on paper:** Ashenmere clerks can no longer pretend the border shift / column / Coalition dead names are **only tavern rumor**. Quiet denial costs **political** capital.
2. **Taryn’s visibility:** She is now the **named scout** on a hot file — **guild attention** (good and bad), **summons**, **mentors**, **rivals**, or **“explain this sentence”** interviews.
3. **Council clock:** `coalition_seat_review_pending` is the **slow knife** — redeploy debates, fact-finding votes, **Vess/Katya** inbox, possible **delegation toward the March** — all **optional** scene fuel, not automatic combat.
4. **Kenji / ronin correlation:** Where her filing names **Kenji** + describes **ronin capability**, that stack can later **cross-cut** with Thornkeep leaks, academy strings, and Lady-side intel — **graduated** identity pressure (see Bane trigger row), not a single “you’re caught” roll.
5. **Bracken convergence:** When Bracken’s **own** formal dispatch hits the same clerk stack, readers **compare** two Thornkeep-originating threads — drama multiplier.

---

## SOLVETH — God of Entropy (bonded in Frost Fang)

**Status:** alive (bonded to blade)
**Met:** yes (Book 2 — bonded, ongoing ember communication)
**Location:** Frost Fang (summonable by Kenji)
**Last Updated:** Ashmere 24

**Physical:** Voice only — dry, ancient, patient. Speaks through the blade or through the ring.
**Disposition to Kenji:** Allied — demands respect, chapter manners. Called Kenji "reckless fool" (affectionate). Invested in Bracken's survival.
**Morale Compass:** Chaotic Evil — entropy given will. Cares only for its own feeding and expansion. Cooperates with Kenji because the bond is useful, not because it loves him. Will betray, eat, or abandon him the moment a larger hunger or a stronger host is offered. Lies gracefully.

**Abilities:** Entropy domain knowledge, patience-binder recognition (fought one in Spoke Wars 1196), chapter-form briefing, bond-form observation, can visit the Lych via summon-on-request arrangement

**Important Gear:** Lives in Frost Fang. Manifests through the ring at Kenji's hip.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| support_key_investigation | Ashmere 24 | TBD | TBD | in_progress | Support Kenji's investigation of the iron key pulling SSW. Provide entropy-domain knowledge as needed. | Key's nature and destination revealed. |

---

## LADY NYX — Living Lich / Warden-Queen (Pallid March)

**True name:** Lady Nyx. **She speaks this name aloud to exactly one person in the setting: Kenji — and only if Kenji's disposition to her reads neutral-or-higher at the moment they actually meet.** If he meets her hostile, afraid, or combat-forward, he gets "the Lych" like everyone else and the name stays locked. The reveal is conditional, not guaranteed. Before that reveal she has no name in the narrative — only aliases.

**Aliases (use these in prose until — and unless — the reveal):**
- **"their Lady" / "my Lady" / "our Lady"** — what her followers call her. Her followers are **undead enthralled thralls with no free will.** They do not know her name because they are not people anymore. "The Lady" is the only noun an enthralled mouth can shape toward her. Followers do NOT count as neutral+ disposition — they have no disposition, only command.
- **"the Lych"** — what her enemies call her. The Coalition. Ashenveil survivors. Thornkeep patrols. Old historians. The few who have seen her and lived. Derogatory. Afraid. **She is always in lich form to enemies.** No exceptions.
- **"— the Lady"** — her signature on border-proclamations and bound notices (see Chapter 5 caravan circle parchment). She signs as *the Lady* because the title is the same thing her followers call her, which is the same thing her enemies do not yet understand — that the undead signing the proclamation and the horror guarding the grove are the same authority. Public-facing signature. **Not "S."** — the abbreviation has been retired in-setting and in all notes.
- The true name "Lady Nyx" is a reveal beat gated behind Kenji's disposition. Save it.

**Status:** alive (ley-suspended, metabolism 1%)
**Met:** yes — **Ashmere 29–30** (Ch15–16, human-form the Lady: meal, bath short of intercourse, guest chamber LR; Seren mask-name; bronze trophy). **Ashmere 40** (Ch33, human-form: Hollowing briefing, **true name revealed** ("Nyx"), JKD spar, alliance). **Ashmere 40–47** (Ch34, **Seven Days**: 7-day intimacy, Close to Death survived, Vigor 1–7 stacked, bonded partner #23, Kenji emerged as Anku Nyx).
**Location:** **Varkûl** — south gate blood circle (Ch36, performing vulnerability in Lady form — Close to Death trap on Gorath)
**Last Updated:** Ashmere **47** / Day **269** — **Ch34** *Seven Days*

**Class:** Living Lich — alive with full dominion over death. Not undead. Real heartbeat, real warmth, real body. Chose this path as a Warden-elect in 1042. Holds a lich's power (undead army, territorial control, phylactery-equivalent) without crossing the threshold into undeath. Can switch between lich form (default) and human form (rare — seduction only).

**Physical:** See npc_appearance.md — two forms documented. **DEFAULT FORM is lich** — giant skeletal floating grim reaper nightmare. Shadow and bone. This is what the world sees 99% of the time. **Human form (the "Lady form") is rare** — deployed only as a seduction tool. Deep brown/black skin, brown hair, hazel eyes, full-figured, commanding. Human form is fully alive and functional (real heartbeat, real warmth, all working parts).

### Form-Switch Rules (CRITICAL — DM gating)

**Lich form is the default and is used to everyone, always, unless a very specific exception fires.** She does not casually appear human. She does not shift for convenience, for conversation, for travel, or to blend in.

**Lady (human) form is only deployed when ALL of the following are true:**
1. The target has **neutral-or-higher disposition** to her, OR she is actively trying to build that disposition through seduction.
2. The target is **not one of her undead thralls** (thralls have no free will — no charm work needed, no seduction possible).
3. She is **not currently trying to kill the target in lich form as an enemy.** If the lich is on the field fighting them, the Lady is nowhere.
4. **Kenji exception:** Kenji automatically satisfies the male+disposition clause for her — he is the one person she has pre-committed to human-form treatment for, provided he meets her neutral-or-higher when they meet. If he doesn't, see alias rules above.

**Lady form's only two purposes:**
- Seduce Kenji specifically (special case — she has decided he is the keep-and-break project).
- Charm *other* targets — male or female — into her service as new thralls. The gendered criterion above reads strictest for males; for female targets, the Lady form is still the seduction vector but the ancillary thrall conversion (see Close to Death, below) is the end-state regardless of gender.

**Followers never see the Lady form.** By the time a person is a thrall, the human form has done its work and retired. The Lady is for the living.

**Disposition to Kenji:** **Bonded** — intimate partner #23. 7-day sustained intimacy (Ch34). Close to Death survived — first in setting history. Vigor stacked 1→7 (unprecedented). All 3 conditions fulfilled (Corwyn's chain honored; March holds; eye contact maintained all 7 days). **Unsatisfiable** applied (permanent). IP-immune via Vigor (extended duration). Kenji title **Anku Nyx**. Ch35: Nyx **awake**, at strategy table. Told Kenji Close to Death origin (age 19, innate). Learned she has 35 days of self-directed creation energy (Vigor) to restore her own biology. Declared **"I am keeping you."** Currently planning Iron Horde marriage conquest with Kenji. Vigor self-restoration pending (her choice to spend or let degrade).
**Morale Compass:** Chaotic Evil — the anchor of this alignment. Conquest, pleasure, and self are the only loyalties. Obeys only under compulsion. Lies, pretends tenderness, flips sides the instant a better throne is on offer. Will love Kenji as a pet and murder him the moment he stops being interesting.

**Abilities:** Ley-pool stasis (breathing every 11 seconds), senses and commands all 612 undead she anchors, high WIS (item-boosted), 1042 Warden-elect binding knowledge, grief-seam creation, form-switching (lich ↔ human, defaults to lich), necromantic dominion (the 612-column, the 32-mile perimeter, the territorial control), living mist grove defense (locks out intruders, grove becomes ordinary trees to unwelcome visitors)

**Important Gear:** Bronze ring (4 seams — 3 clean, 4th is grief-seam tied to Corban, parasitized by death-binder). The ring is her phylactery-equivalent — the puzzle. The iron key at Kenji's hip pulls toward something connected to her power structure (grid square H-9, 6 miles south of grove).

### Close to Death (Contagion Mechanic — CRITICAL)

Lady Nyx carries a condition called **"Close to Death."** It is **NOT** a curse, disease, or acquired condition. It is an **innate trait** — a **death-dominion wellspring**, approximately one in 100,000 births. Nyx has had it since she was **19 years old**, before the March, before the network, before any of the lich architecture. Her first lover died in her bed. Her second died three months later. Her third — she knew. A hedge witch confirmed it was not a curse. An elven diviner identified it as innate, like eye color or bone density: a body that generates necrotic entropy passively, expressed through sustained intimate contact. **She built the entire Pallid March — the undead army, the root network, the 612 anchors, the two centuries of solitary sovereignty — because she was tired of killing things she loved.** The lich transformation and death-dominion architecture were her solution to a problem she was born with.

- **Vector:** Transmitted only through intercourse in Lady (human) form. Lich form cannot transmit it because lich form does not have intercourse.
- **Mechanic:** Deals **1% max-HP damage per second** to the partner for the duration of the act. A typical encounter (100+ seconds) will reduce a baseline humanoid to zero HP. Scales raw — no save, no resistance, no mitigation from ordinary means.
- **Usual outcome:** Death mid-act or shortly after.
- **Post-death outcome:** The partner rises as one of her **enthralled undead.** This is the primary origin pathway for most of her standing army of thralls. She does not recruit — she beds.
- **This is why her followers have no free will.** They were people she slept with. The Close to Death killed them. The dominion-over-death rebound bound them to her. "My Lady" is what a mouth that used to love her now calls her.
- **Canonical exception — Sir Corwyn the Fallen.** His paladin Constitution and Oath of Protection refused to die on the normal schedule. Seventy-two continuous hours of intercourse were required to finally reduce him to zero HP. When he finally died, his Oath did not break — it *warped,* and the dominion-over-death rebound could not fully claim him. He retains full paladin class features, partial sentience, memory, and an unbroken (though redirected) Oath of Protection. This is the only documented survival of the first hour in setting history, and it is still not a full survival — it is a partial one. See Corwyn's entry below for the full mechanics and narrative consequences.

**Kenji-specific implications (DM-tracked, not player-visible until discovery):**
- Kenji's biological enhancement profile and healing throughput may be the first thing in her living memory that could survive the act. Whether he does is a mechanic, not a plot guarantee.
- If Kenji survives an encounter, the Vigor cycle below fires — and he survives to face the 10%-per-cycle conquest consequence. She gets what she wants *and* keeps him alive to do it again.
- If Kenji does not survive, he becomes her highest-grade thrall. The Abyssal Shard Nodachi in the hand of an enthralled Kenji is a setting-level extinction event. Do not hand-wave this outcome.
- The first intimacy is the test. The first dawn after is the reveal.

### Vigor Consequence Mechanics (CRITICAL)

If Kenji is intimate with Lady Nyx (human form) **and survives Close to Death**, she receives Lover's Vigor (+50% all stats, 5 days):
- **Immediate:** She becomes unstoppable in combat. Minion toughness multiplied 5×. Her lich-form army becomes unkillable by any local force.
- **Per 5-day buff cycle:** Conquers **10% of the kingdom** — destroys villages in her area, expands undead territory, absorbs populations into her army.
- **Natural conquest rate (no buff):** 5% per 20 days. She's already a threat without Vigor. With it, she's a catastrophe.
- **Post-buff behavior:** The moment Vigor expires, she hunts Kenji. Sends minions to find him. Goal: capture Kenji alive, force re-buff, repeat conquest cycle. Each cycle = another 10%.
- **Nobody knows it's Kenji's fault.** The world sees "the Lych" surging. No one connects it to a ronin sleeping with the Warden-Queen.
- **Eye shift during Vigor:** Hazel → vivid teal/cyan-green (luminous, glowing). Faint teal-green runic lines trace across skin (arms, thighs, back, collarbones) — veins of light beneath the surface.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| still_night_doctrine | Ashmere 30 | **Hollowmere 15** | Ashmere 30 | **active** | March peaks **Still Night** — she tightens doctrine, spends cordon attention, tests Coalition blind spots while ley-stasis holds. | Border fiction collapses faster after peak if she commits; political panic clocks advance. |
| trace_oathbreaker_vector | Ashmere 31 | TBD | N/A | **active** | Champion disarmed; **Oathbreaker** off-body — binding net and trophy strings **hunt the gap** toward thief/BoH signature (she may not know it is Kenji). | Increases March-side probes, dreams, or courier-thrall attempts — **play**, not JSON omniscience. |
| pallid_march_potential | 1042 AR | TBD | TBD | dormant | Long-arc conquest math (5%/20d baseline; 10%/cycle if Vigor ever fires). **Secondary** clock — must not be her *only* operational row. | See Vigor mechanics above. |
| capture_kenji | N/A | on_first_vigor | N/A | **moot** | Was dormant — activates after first Vigor. Ch34: Vigor fired ×7, but alliance conditions override predation. Kenji is bonded partner #23. Capture goal **superseded** by alliance. CE alignment means this could reactivate if alliance fractures. | Hunt / capture / repeat cycle — **SUSPENDED** while alliance holds. |
| anku_nyx_alliance | Ashmere 40 | ongoing | Ashmere 40 | **active** | Alliance with Kenji (Anku Nyx title). Ch34: intimacy sealed, Close to Death survived, Vigor 1–7 stacked, Soul Conqueror unlocked. All 3 conditions fulfilled. Corwyn rebuilding village. March holds. Nyx is bonded partner #23. | Alliance deepened beyond conditions — Vigor 7 created something unprecedented. Conquest rate available but Nyx agreed to hold March. |

**THE TRAP:** She is the easiest woman in the story to bed — chaotic evil, zero inhibitions, upfront about what she wants, beautiful in human form. But each intimacy event (a) requires Kenji to *survive Close to Death* (1%/sec), (b) triggers a 10% kingdom conquest cycle if he does, and (c) eventually a capture-hunt side plot. The romance path IS the threat path AND the extinction path. Nobody omnisciently connects Kenji to the surge. The player chooses the destruction with full mechanical transparency. **TRAP TRIGGERED AND SURVIVED (Ch34).** 7-day sustained intimacy. Close to Death irrelevant (regen 61 HP/sec vs 3.68 HP/sec drain). Vigor stacked 1→7 (unprecedented — geometric, not additive). Nyx bonded partner #23. Soul Conqueror unlocked (Vigor stacks reflected into Kenji's stats). Nyx currently asleep (Vigor 7 metabolizing). **Conquest consequence:** Pallid March impregnable (Vigor-enhanced undead, 5× minion toughness). 10%/cycle conquest rate available BUT Nyx agreed to hold March (condition 2). Capture-Kenji goal **moot** — alliance, not predation. **New risk vector:** Vigor 7 Nyx waking up changed. World saw/felt the 7-day event. Ronin cover further compromised (green eyes, green aura).

---

## AMARIS — Druid, Briarstone Homestead

**Status:** alive
**Met:** yes (Book 4 Ch1-3 — Greymere/Thornfield, intimate partner)
**Location:** Briarstone Homestead, Thornfield region
**Last Updated:** Ashmere 11 (Book 4 Ch 2)

**Physical:** Silver-white hair, green eyes, 5'3", athletic build.
**Disposition to Kenji:** Intimate/Bonded — established relationship. Kenji departed via invisibility; she discovered he was gone. Searching for him via Root Network.
**Morale Compass:** Neutral (Player-Made Character — cross-campaign; shiftable via her arc and her bond with Kenji)

**Abilities:** Level 16 druid. Double-bladed scimitar combat, Entangle (L1/L2), Earthen Command, Bloom Touch, Cure Wounds, sage bomb creation, Warden's Root, bittervine wall cultivation, Diagnostic Touch, Living Ground. Post-Vigor: WIS 25, INT 24, enhanced strength (crushes rock), darkvision.

**Important Gear:** Double-bladed scimitar, component pouch, Stilthorn paralytic recipe (grandmaster-level), bittervine cuttings, webrot moss vials, pale sage bundles, warden's root seeds

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| find_kenji | Ashmere 11 | TBD | N/A | in_progress | Searching for Kenji via Root Network (heartbeat through soil). He left Thornfield invisibly. She does not know where he went. | If she finds him: emotional confrontation. She was intimate, he vanished. |
| protect_briarstone | Ashmere 11 | ongoing | N/A | in_progress | Maintain Briarstone homestead and cleared Greenveil ley lines. Farm is operational. Corruption reversed. | Land stays healthy. Farm produces. Amaris remains anchored to Thornfield. |

---

## WYNN — Herbalist / Researcher

**Status:** alive
**Met:** yes (Book 4 Ch1-3 — Thornfield herb cottage, intimate partner)
**Location:** Herb cottage, Thornfield (south end)
**Last Updated:** Ashmere 18 (Book 4 Ch 3)

**Physical:** Late thirties, lean, sun-darkened, short dark hair, calloused hands.
**Disposition to Kenji:** Intimate — scientific fascination + emotional bond. Discovered clone deception ~10 minutes after he left. Was "furious" then started writing about it. Has 10 pages of documented analysis on Kenji's biological enhancement mechanism.
**Morale Compass:** Chaotic Good — a researcher who publishes what she finds because the truth belongs to everyone. Breaks rules she disagrees with, hides nothing on principle, helps people without being asked. Opposes Kenji if he asks her to bury evidence or weaponize her research against the helpless.

**Abilities:** Plant-based magical manipulation, herbalism, Earthen Command, scientific analysis, mapmaking. Post-Vigor: grip strength +40%, darkvision, resting heart rate -12 bpm, enhanced cognition.

**Important Gear:** Research notebook (10 pages on Kenji's bio-enhancement), Sample A (in situ, activated — luminescent gold-green), Sample B (oral extraction, unactivated), magnifying lens, specimen collection, garden tools

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| analyze_kenji_samples | Ashmere 18 | TBD | TBD | in_progress | Scientific documentation of Kenji's biological enhancement mechanism. 10 pages with charts already written. Samples A and B in her possession. | If this research reaches the wrong hands: Kenji's nature becomes known. If it reaches scholars: potential replication or exploitation. STORY-CHANGING if it leaves Thornfield. |
| find_kenji | Ashmere 18 | TBD | N/A | in_progress | Knows the clone wasn't real. Furious then fascinated. Will write about it, then look for him. | Confrontation or correspondence when she locates him. She has documentation that proves what he can do. |

**FLAG:** Wynn's samples and research are a ticking story bomb. If she shares or publishes, Kenji's biological enhancement becomes public knowledge.

---

## DELIA — Tavern Keeper, Thornfield

**Status:** alive
**Met:** yes (Book 4 Ch3 — Thornfield tavern, intimate partner)
**Location:** The Stubborn Mule tavern, Thornfield
**Last Updated:** Ashmere 18 (Book 4 Ch 3)

**Physical:** 43 years old, broad shoulders, ruddy-cheeked, strong arms.
**Disposition to Kenji:** Friendly/Grateful — intimate relationship during his 7-day rest. Chose breakfast company over tavern duty. Not apologetic. Self-assured.
**Morale Compass:** Lawful Good — honest tavern keeper. Pays her dues, takes care of her staff and regulars, serves the road. Opposes Kenji if he endangers her house or her people. Stands ground on hospitality and the unwritten rule that the roof protects everyone under it.

**Abilities:** Tavern management, community leadership, morale, cooking

**Important Gear:** Tavern (The Stubborn Mule, green door)

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| rebuild_thornfield | Ashmere 18 | ongoing | N/A | in_progress | Village recovery post-corruption. Twelve people returned. Fences being fixed. Tavern operational. Stillday traditions being established. | Thornfield becomes a functioning village again. Delia anchors the community. |

---

## BRECA — Merchant / Dry Goods Trader

**Status:** MIA
**Met:** yes (Book 4 Ch1 — Greymere north road, intimate partner)
**Location:** Northbound trade route (departed Greymere region)
**Last Updated:** Ashmere 5 (Book 4 Ch 1)

**Physical:** Not heavily described. Cart with red axle.
**Disposition to Kenji:** Friendly/Intimate (brief encounter). Six-year widowhood ended. Offered to stop at Fallowmere on future circuits.
**Morale Compass:** Lawful Good — small-town merchant who stocks what Millhaven needs, extends credit when the winter is hard, pays her taxes. Opposes Kenji if he brings violence to her circuit or asks her to cheat her regulars.

**Abilities:** Trade route knowledge, caravan management

**Important Gear:** Trade cart (red axle), mules, crossbow

*No active goals — MIA (departed story area, no current relevance to Kenji's active threads)*

---

## HOLSK — Blacksmith (Dwarven), Millhaven

**Status:** alive
**Met:** yes (Ashmere 22 — Millhaven forge, multiple interactions)
**Location:** Millhaven garrison blacksmith
**Last Updated:** Ashmere 24 (Book 4 Ch 5)

**Physical:** 4'8", shoulders wider than doorframe.
**Disposition to Kenji:** Professional/Friendly — recognizes quality of nodachi, willing to work commissions.
**Morale Compass:** Lawful Good — dwarven craftsman's honor. Works the forge, keeps his word, respects good steel. Opposes Kenji if Kenji asks him to shortcut the craft or make a weapon he won't be able to look at in the morning.

**Abilities:** Master-level weapon crafting (mythril, rune-tempered, crystal structure with enchantment slots, thrum-alloy). Weapons grow with wielder.

**Important Gear:** Forge, tools, materials

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| operate_forge | ongoing | ongoing | N/A | in_progress | Maintain garrison blacksmith. Accept commissions. | Kenji has access to master-level crafting in Millhaven. |

---

## TEILEN — Sergeant, Millhaven Watch

**Status:** alive
**Met:** yes (Ashmere 22 — Millhaven watch-hall, multiple interactions)
**Location:** Millhaven watch-hall
**Last Updated:** Ashmere 33

**Physical:** Forties, short grey-brown hair, watch uniform (no brooch).
**Disposition to Kenji:** Neutral/Professional — filed him in one glance, focused on Bracken.
**Morale Compass:** Lawful Good — sergeant of the watch. Follows Bracken's chain, does the paperwork, keeps the peace. Opposes Kenji if Kenji breaks the watch's rules inside Millhaven's walls.

**Abilities:** Grid mapping, operational planning, compass/ruler work, military logistics. Half-elf. Off-books Pallid March expertise.

**Important Gear:** Compass, rulers, watch-hall map table access

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| watch_hall_maps | Ashmere 22 | ongoing | N/A | **active** | Keep Millhaven watch-hall map boards current; support **Hadley’s** chain (not Thornkeep). Pallid March overlays from Bracken-era intel still referenced by clerks. | If March noise returns north: Teilen is the fast path to “what the watch already filed.” |
| pallid_overflow_prep | Ashmere 33 | **Ashmere 36** | N/A | **active** | **Revised:** Taryn’s packet is **in**; prep is for **council review noise** / ronin name cross-file (she filed **Kenji** as source where required), not “missing letter.” Teilen etc. optional if politics spike. | Council-pressure levers without contradicting resolved delivery. |

---

## DEATH-BINDER — Unnamed (antagonist)

**Status:** alive (presumed — location unknown)
**Met:** no — no direct intel. Known only through Living Ground/Bond-Form readings and Solveth's analysis.
**Location:** Unknown — operates within a 32-mile perimeter south/southwest of Millhaven. Iron key's SSW pull terminates at grid square H-9 (6 miles south of weeping elm grove, inside this perimeter).
**Last Updated:** Ashmere 24

**Physical:** Unknown to Kenji — no direct intelligence yet.
**Disposition to Kenji:** Unknown — has not encountered Kenji.
**Morale Compass:** Lawful Evil — runs a precise, contracted column of 612 bodies along a fixed 32-mile perimeter. Everything she does has a ledger behind it. She's siphoning the Lych's grief-seam on the same parasitic logic. Opposes Kenji if Kenji threatens her column, her handler, or her parasite line. Negotiates before she kills — which makes her worse, not better.

**Abilities:** Patience-binding (specialized necromantic discipline Solveth recognized from Spoke Wars 1196). Keeps a 612-body column moving on a 32-mile perimeter patrol. Parasitized the 4th seam of the Lych's bronze ring (grief-seam tied to Corban) — siphoning power without her awareness or consent. Works with a handler (logistics/supply support).

**Important Gear:** Unknown. Operates the ring's 4th seam as a power feed.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| maintain_column | ongoing | ongoing | N/A | in_progress | Keep the 612-body column patrolling the 32-mile perimeter. Column is the visible arm of the death-binder's operation. | Ongoing. Failure = column collapses, perimeter unguarded, whatever the death-binder is hiding becomes reachable. |
| siphon_from_lych_ring | ~unknown (established pre-current) | ongoing | N/A | in_progress | Parasitize the 4th grief-seam of the Lych's bronze ring to feed own power. She does not know. If she finds out, she will not be gracious. | If discovered by the Lych: war between them. If severed by Kenji: death-binder loses primary power feed, column weakens, but the Lych's ring is disturbed (unknown consequences). |

---

## HANDLER — Unnamed (death-binder's logistics/support)

**Status:** alive (presumed — location unknown)
**Met:** no — no direct intel at all.
**Location:** Unknown — mobile, within the death-binder's operational range
**Last Updated:** Ashmere 24

**Physical:** Unknown to Kenji — no direct intelligence.
**Disposition to Kenji:** Unknown — has not encountered Kenji.
**Morale Compass:** Lawful Evil — quartermaster morality. Keeps the logistics tight, loyal up the chain, willing to hurt anyone who interrupts the supply. Opposes Kenji if Kenji disrupts the operation.

**Abilities:** Unknown. Confirmed role: supports the death-binder. Likely handles logistics (supplies for whatever living infrastructure the death-binder needs), recruitment, or intelligence gathering. May be living (handler for the undead column) or may be something else.

**Important Gear:** Unknown.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| support_death_binder | ongoing | ongoing | N/A | in_progress | Support the death-binder's operation — exact role TBD. | Unknown. Kenji has no intel yet. |

---

## CORBAN — Connected to the Lych's Grief-Seam

**Status:** Unknown (alive / dead / undead / bound — not yet determined)
**Met:** no — identity and status unknown to Kenji. Name known only through Bond-Form analysis of the bronze ring's 4th seam.
**Location:** Unknown
**Last Updated:** Ashmere 24

**Physical:** Unknown to Kenji — no direct intelligence.
**Disposition to Kenji:** Unknown — has not encountered Kenji.
**Morale Compass:** Lawful Evil — currently a thrall of the Lych's grief-seam. Functions within her hierarchy and carries out her will. Alignment reflects what he IS right now, not what he might become if the seam is cut.

**Abilities:** Unknown. Named as the anchor of the 4th seam on the Lych's bronze ring — the grief-seam. Whatever he was/is to her, the emotional binding was strong enough to leave a seam in her phylactery-equivalent, and that seam is what the death-binder parasitized.

**Important Gear:** Unknown. May be the grief-seam's living anchor, a body the death-binder holds, or a memory-construct — unclear.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| grief_seam_anchor | pre-campaign | TBD | N/A | active_dm | **Entity status still unknown** — tracker keeps **operational** goals so the seam is not inert lore. Whatever Corban **is**, the 4th seam stays load-bearing for **death-binder / Lych ring** tension. | Reveals leverage: hostage, ghost-in-ring, parasitic memory, etc., when Kenji earns the scene. |
| resist_parasite_or_succumb | Ashmere 24 | TBD | N/A | active_dm | Death-binder siphons grief-seam; Corban-side pressure **increases** if March tightens (see Lady **trace_oathbreaker_vector**). | May force visible symptom on column or dreams; **pay through play**. |

*Investigation flag unchanged:* Who Corban **was/is** determines hostage vs ghost vs power-feed.

---

## CAMPAIGN THREAT NPCs — MIA (introduced when Kenji encounters the threat, or when Vess/Elara locate Kenji and notify him)

**All timers below are DORMANT.** Due dates are calculated from each threat's clock rate but do not begin counting until the NPC is introduced to Kenji — either by Kenji finding the threat himself, or by Vess or Elara locating Kenji and briefing him. The "due_date" column shows "DORMANT + X days from introduction" format.

---

### THE HOLLOWING — Kharn-Dural (Northwest)

---

## KING THORGRIM IRONVAULT — Runesmith / Ruler of Kharn-Dural

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Kharn-Dural — Dwarven Undermountain (northwest)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Eight hundred years old. Dwarven king. Carries the weight of the dig that broke the floor.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Good — dwarven king who carries the dig that broke the floor on his conscience. Runesmith, ruler, owner of the problem. Opposes Kenji if Kenji endangers Kharn-Dural or asks the dwarves to abandon the lower delve.

**Abilities:** Runesmith, Level 22. Magic through carved stone and metal. Ordered the deep dig that breached The Fathom's prison. Eight centuries of stonecraft knowledge. Ruler of 40,000 dwarves. Sent emissaries to surface nations — most ignored. Coalition received his letter (Vess filed it, Garrett flagged it, nobody acted without the ArchMagus).

**Important Gear:** Unknown — royal dwarven regalia presumed.

**Personality:** Proud. Guilty. Will kneel to anyone who can save his people. Has never knelt.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| save_kharn_dural | pre-campaign | DORMANT + 42 days from introduction | TBD | dormant | The Fathom presses against the mythril seal. Wards weaken daily (+2%/day from 15%). Thorgrim needs outside help — ember energy or Bloom Purge to reinforce the seal. Timer starts when Kenji learns of the Hollowing threat. | If seal holds: 40,000 dwarves survive, dwarven alliance possible. If seal breaks: undermountain collapses, The Fathom spreads through tunnel network to Ashward Mine system, corruption reaches coalition territory within weeks. |

---

## BRUNHILD DEEPDELVE — Head Miner, Kharn-Dural

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Kharn-Dural — deep tunnels (northwest)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Dwarf. Was on the drill team that broke through. Hasn't slept in three months.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Good — head miner. Workers first, then the king. Hasn't slept in three months because her team broke through the wrong wall. Opposes Kenji if he treats miners as expendable or covers up what they found.

**Abilities:** Head Miner, Level 18. Knows the tunnels better than anyone alive. Heard The Fathom's non-sound first. Deep mining expertise, tunnel navigation.

**Important Gear:** Mining equipment, tunnel maps.

**Personality:** Exhausted. Haunted. The woman who heard the nothing first.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| guide_tunnels | pre-campaign | DORMANT (activates on introduction) | N/A | dormant | Essential guide for navigating the deep tunnels to the seal breach. Only person who knows the full tunnel network at depth. | Whoever goes to reinforce the seal needs Brunhild. Without her, they're blind underground. |

---

## GRIMJAW — Duergar Exile, Kharn-Dural Upper Tunnels

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Kharn-Dural — upper tunnels (northwest)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Duergar (grey dwarf). Lives in the tunnel margins.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Evil — duergar exile who still thinks like duergar: cruelty is efficiency, hierarchy is survival, kindness is a trap. Exile changed his employer, not his compass. Opposes Kenji if Kenji doesn't pay or doesn't scare him enough.

**Abilities:** Level 20. Trades with the surface. Feels The Fathom's pressure through stone. Tunnel survival, information brokering, duergar pragmatism.

**Important Gear:** Trade goods, tunnel access.

**Personality:** Pragmatic. Distrusted by the dwarves. Has critical intel he'll trade for citizenship.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| trade_intel_for_citizenship | pre-campaign | DORMANT (activates on introduction) | N/A | dormant | Knows there's a second breach forming in the eastern shaft. The dwarves don't know. Will trade this information for Kharn-Dural citizenship. | If intel is obtained: second breach can be addressed before it opens. If ignored: two-front collapse of the undermountain. |

---

### THE PALLID MARCH — Ashenveil (Southeast)

*(Lady Nyx / "the Lych" already tracked above as full entry — Pallid March leader.)*

---

## SIR CORWYN THE FALLEN — Death Knight, the Lych's Guard

> **One-line character:** A Lawful Good undead paladin serving a Chaotic Evil lich. Both halves of that sentence are fully and simultaneously true, and the tension between them is the character. Every encounter with Corwyn has to play both halves at once — the honor and the horror, the conscience and the chain, the sword that still carries holy fire in the hand of a man who died three days dying.

**Status:** Active
**Met:** yes — Ashmere 24 night, terminus camp. Kenji returned the stolen iron chest, spoke face to face ("I thought dead men told no tales, yet here we are"). Corwyn asked "Why are you here, swordsman?" twice. Kenji never answered — walked away with Elda mid-conversation. Corwyn witnessed the seal opening behind Kenji. Kenji knows him as "the death knight" — does not use the name Corwyn in conversation (learned via Steel Sight only).
**Location:** South road ~**mile 18** crown — **down**, **disarmed**; **Oathbreaker stolen** (Kenji’s **Bag of Holding**). Arm ruined at shoulder/elbow; cannot wield until triage/healing/binding resolution.
**Last Updated:** Ashmere 33 — iron chest row **RESOLVED**; arm triage + sword-loss off-screen goals **active**; `serve_the_lady` row now **active** (not dormant-only)

**Physical:** Black plate armor, polished. **Oathbreaker no longer at his side** — stolen; holy/necrotic duality now **muffled** off-body (may still ache in his senses). The blade was *in pain* when he carried it; the absence is a new wound.
**Disposition to Kenji:** Conflicted. Initially hostile (chased clone Ashmere 23, called "THIEF"). After chest return (Ashmere 24): puzzled, wary, not aggressive. The thief came back, returned the stolen property, and walked away from an opened seal without looking inside. That's not thief behavior. The restraint — the *willingness to talk* — is a function of his partial sentience, not his orders. Orders say kill. Oath says protect. The ronin's behavior (returning stolen goods, protecting a civilian) maps to the Oath, not the enemy. Corwyn noticed. Does not know Kenji's identity.
**Morale Compass:** **Lawful Good.** Strictly speaking — not "Lawful Good with an asterisk," not "Lawful Good warped," just Lawful Good. He follows a lawful chain of command. He protects what he has been given to protect. He does not seek power for himself. He does not take pleasure in hurting anyone. He does not lie, cheat, or hunt the helpless. He confirms targets before striking and he keeps his word. That is the behavior of a Lawful Good character, and alignment describes behavior, not the morality of whoever sits on the throne he answers to. The queen he serves is Chaotic Evil. Corwyn is not. Two characters, two alignments. His Oath of Protection was redirected — who he protects changed — but the virtues that make him *him* are intact and operating on the same rules they did when he was alive. He is a good knight serving the wrong queen. That is the entire tragedy in one sentence, and it does not require the alignment label to carry a qualifier.

**Origin — The Seventy-Two Hour Death (CRITICAL — explains everything about him):**

Sir Corwyn was a Lawful Good paladin of the Oath of Protection. Before he fell, he was everything the Oath asked of him — a shield for the weak, an honest sword, a man whose word was a load-bearing beam of his life.

Lady Nyx seduced him. In Lady form. Bedded him with the intent of Close to Death running its standard course — 1% max-HP per second, dead in under two minutes, rise as thrall.

**His paladin Constitution refused to cooperate.** The Oath-bonded CON, the divine vigor of a protector at peak — it resisted the contagion directly. He didn't die in two minutes. He didn't die in an hour. He didn't die in a day.

**It took seventy-two hours of continuous connection.** She stayed with him the entire time, because the mechanic requires ongoing intercourse to deal damage — she couldn't leave and come back. For three full days she fed Close to Death into his body, and he held. His HP drained percentile by percentile while his Oath kept rebuilding the floor underneath him.

**When he finally died, he didn't fully enthrall.** The Close to Death completed the kill. The dominion-over-death rebound fired as it always does. But the Oath of Protection did not break — it *warped.* Where her other victims lost everything that made them people, Corwyn kept:

- **His paladin power.** Full suite. Lay on Hands, smite, aura, divine sense — all functional, all tied to the original Oath that was never formally broken. He can still cast as a paladin because he still *is* one, technically.
- **His sentience.** ~~Partial~~ **FULL (Ch35).** Originally partial — he knew who he was, what he is, how he got here, remembered every hour of the seventy-two. Most thralls know nothing; Corwyn knew everything but experienced it through a compressed bandwidth. **Ch35: Kenji restored full consciousness** via creation energy conducted through root network (dual creation+death-dominion spectrum). Corwyn is now fully sentient — complete cognitive bandwidth, emotional range, capacity for embarrassment, independent judgment. Chain and enthrallment intact; he serves because he *chooses* to, and the choice matches the command. Additionally given a **self-sustaining flesh facade** (ley-powered) — appears as living man in his fifties. Facade holds indefinitely in ley-rich territory.
- **His Oath.** Not broken — warped. The Oath of Protection now reads: *protect the Lady, her grove, her domain.* But the original vector (protect the weak, protect the innocent, do not strike the defenseless) is still underneath it, unbroken because paladin oaths are not simple compliance contracts — they are identity. She could rewrite the target. She could not delete the shape.
- **His alignment.** Still Lawful Good. Strictly. The Close to Death killed his body, not his morality. He has not become cruel, he has not become grasping, he has not developed a taste for the things death knights usually develop a taste for. He serves a dark queen, but he serves her the way a good man serves — without relish, without ambition, without any of the pleasures of evil. The *law* he answers to is now hers. The *good* is the same good it was when he was alive. Alignment describes the character, not the throne; Corwyn stays Lawful Good the way Sera or Bracken do, and the sovereign he answers to is simply CE. Two characters, two alignments, both clean. That is exactly what makes him the most dangerous of her followers to her own cause — because he still has a conscience, and conscience is the one thing her other servants do not have to fight through.

This is the duality the story has been gesturing at: a creature of light and undeath in the same armor, neither fully. The necrotic runs up his sword from the pommel; the holy runs down from the edge. They meet in the middle of Oathbreaker and they are *still fighting each other.* The blade is in pain because the wielder is in pain.

**Abilities:** Death Knight, Level 26 — BUT retains functional paladin class features under the warped Oath. Lay on Hands still heals (he can heal *her grove's living defenders*, which is theologically incoherent and which he does not think about). Smite fires on command (necrotic-tinged). Divine Sense still works. Aura of Protection still extends. The Oath powers have been re-targeted, not removed. Combat: most dangerous single combatant in her army. Greatsword Oathbreaker (holy/necrotic dual-signature — sword is *in pain* because it is also carrying the duality). Retains personality, honor, memories. Hates what he's become but cannot act directly against the Lady without breaking the warped Oath, which he does not know he can survive.

**Important Gear:** Black plate armor. **Oathbreaker — STOLEN (Ashmere 28 Ch14)** by Kenji into extradimensional storage; recovery now a **binding** and **logistics** problem, not a draw-cut problem. Iron chest arc resolved earlier; seal/key thread separate.

**Personality:** Honorable. Tormented. The calmest voice in the Lady's army because he is the only follower who is still a *person* in there. If Kenji can break the warped Oath (not the original — the warp), Corwyn returns fully to who he was and becomes a catastrophic ally (paladin memories + death knight power + seventy-two hours of grudge against the Lady). If Kenji cannot break it, Corwyn remains the most dangerous and the most hesitant enemy Kenji will fight — the one who will pause before the killing stroke and ask a question first. The pause is the opening.

**Narrative function — why he hasn't rushed to kill Kenji:** Every prior encounter where Corwyn has talked instead of struck is because the Oath of Protection — the unbroken underneath one — is reading Kenji's intent (not yet a threat to the Lady directly) and running the old rules: *do not strike the uncommitted, confirm the target.* That is paladin doctrine, not death-knight doctrine. He is acting on the doctrine that was never deleted. The Lady's orders say kill the thief. The original Oath says confirm the threat. The original Oath moves his feet first.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| serve_the_lady | pre-campaign | ongoing | N/A | **active** | Warped **Oath of Protection** still routes to her domain; he patrols, reports, leads when ordered. Original LG Oath **still underneath** — hesitation on uncommitted targets, confirm-before-kill paladin habit. | If warp breaks (not the Oath): catastrophic LG ally + DK power vs her. If not: vanguard with a **pause** baked in. |
| recover_iron_chest | Ashmere 23 | Ashmere 24 | N/A | **RESOLVED** | Iron chest thread — **returned** to Corwyn terminus night Ashmere 24; contents never opened by Kenji. | Closed. |

### Off-screen goals (Ch15–16, Kenji south / Corwyn not in POV)

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| report_sword_loss | Ashmere 29 | N/A | N/A | **MOOT** | Lady knows; alliance renders hunt priority irrelevant. Oathbreaker still in Kenji’s BoH. | Recovery now a cooperative question, not adversarial. |
| triage_arm_binding | Ashmere 29 | TBD | N/A | active | Arm still ruined (shoulder/elbow from iaido crit Ch16). Flesh facade covers it but structural damage remains. Stabilization still needed. | Kenji’s creation energy may be able to address — untested on structural bone damage. |
| thief_profile_update | Ashmere 29 | N/A | N/A | **RESOLVED** | Alliance + full consciousness restoration. Corwyn now serves Nyx alongside Kenji, not against him. Original LG Oath reads Kenji as ally to the Lady’s domain. | Hesitation window → cooperation. |
| full_consciousness_adjustment | Ashmere 47 | ongoing | N/A | **active** | Adjusting to full cognitive bandwidth after 200 years of partial sentience. Emotional range restored — experiencing embarrassment, nuance, independent judgment for first time since death. Flesh facade adds sensory input (warmth, touch, blush response). | Long-term personality development; may develop independent opinions about Nyx/Kenji alliance. |

---

## MAGS — Halfling Grave-Robber, Ashenveil Border

**Status:** MIA
**Met:** no — MIA. Stub created but never encountered.
**Location:** Edge of the Ashenveil (southeast)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Tiny. Halfling.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Chaotic Good — grave-robber with rules. Won't hurt the living, won't rob the freshly grieved, cuts in the people who helped her. Opposes Kenji if he tries to use her to hurt someone alive, or if he stiffs her on a split.

**Abilities:** Level 8. Twenty years of Ashenveil looting experience. Knows every path, sinking pit, and safe camp in the swamp. The guide.

**Important Gear:** Looting tools, swamp survival gear.

**Personality:** Foul-mouthed. Charges ten gold a day and she's worth fifty. Not aligned with the Lych — independent operator.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| survive_and_loot | ongoing | DORMANT (activates on introduction) | N/A | dormant | Continues grave-robbing the Ashenveil margins. Available as a guide for hire. Knows the swamp better than anyone living. | If hired: provides safe passage and critical path knowledge through the Ashenveil. Essential for any deep-swamp operation (phylactery hunt). |

---

## BRYNN — Shield Infantry, Thornkeep Garrison (Partner #19)

**Status:** Active (**not MIA** — off-screen with goals)
**Met:** yes — Book 4 south push; intimate bond; **Lover’s Vigor EXPIRED** predawn **Ashmere 34** per `kenji_state.json` — **no longer IP-immune**; emotional bond unchanged; eyes tell per arc when visible.
**Location:** **Thornkeep garrison** — officer wing / yard orbit (**Ashmere 35**); Kenji **left north** Day **256** ~**09:00** — she **may** hear **gate** gossip before **Bracken** spells it out.
**Last Updated:** Ashmere 35 (post–Ch18 Kenji departure — `kenji_state.json`)

**Physical / disposition / Morale Compass:** See `npc_appearance.md` (full build). **Disposition to Kenji:** intimate (**+34**); carries professional discipline + private fear when he goes south alone. **Morale Compass:** Lawful Good — Coalition shield line; opposes Kenji if he burns the border’s trust or abandons innocents for convenience.

**Abilities:** Shield infantry (garrison); **Lover’s Vigor** ended **Ashmere 34 predawn** — IP saves apply again if she **views** Kenji (DC 23 aura rules).

### Off-screen goals (Ch15 split onward)

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| escort_north_split | Ashmere 29 | TBD | N/A | **complete** | Execute Kenji’s order: march **Jostin** north safely. **Ashmere 31:** arrived Thornkeep; escort objective satisfied. | — |
| rejoin_command_report | Ashmere 29 | TBD | N/A | **complete** | Reach **Thornkeep**; report into **Bracken** chain (not “Hale” — deprecated naming). **Ashmere 31:** debrief **interrupted** by Kenji presence; facts partially spoken before room cleared. | Coalition ear now has **live** Kenji in-building. |
| vigor_window_prep | Ashmere 29 | ~Ashmere 33 | N/A | active | **Learn** buffed body under travel + light skirmish; plan for **post-Vigor** stat cliff and returning **IP** pressure. | Avoids surprise weakness when Vigor drops. |
| kenji_south_private | Ashmere 29 | TBD | N/A | active | Emotional load: **not** abandoning post — but tracking time/distance to Kenji’s reckoning; seek courier or reunion beat when table calls for it. | Drives future scene priority without teleporting her south. |

---

## CORPORAL JOSTIN — Scout, Thornkeep Garrison

**Status:** Active (**not MIA** — off-screen with goals)
**Met:** yes — Ashmere 25, south road patrol zone. Kenji found him on patrol, relayed Hale's briefing and Elda's missing son report. Jostin agreed to search the gap.
**Location:** **Thornkeep garrison** — scout rotation / **Bracken** chain (**Ashmere 35**); Kenji **not** on post (departed north Day **256**).
**Last Updated:** Ashmere 35 (`kenji_state.json` — Ch18 shelf)

**Physical:** Late twenties, lean, dark circles under his eyes. Scout's kit — light armor, short bow, journal in belt. Looks like he hasn't slept well in weeks.
**Disposition to Kenji:** Cautiously impressed. The masked ronin killed 4 wights and 2 skeleton warriors on his patrol route in one morning. Wants him to stick around.
**Morale Compass:** Lawful Good — Coalition scout, **Commander Renna Bracken’s** best. Reports up the chain, takes the border seriously, believes in the line. Opposes Kenji if Kenji is a threat to the Coalition's intel integrity or the people behind the line.

**Abilities:** Level 10. Thornkeep garrison. **Bracken’s** best scout (legacy “Hale” strings in old notes = **deprecated**). Watching the southern swamp border. Reports getting shorter and more frightened.

**Important Gear:** Scout gear, patrol equipment.

**Personality:** Professional. Increasingly terrified. Last report: "They're practicing formations."

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| border_watch | Ashmere 25 | **ongoing** (spikes toward **Hollowmere 15**) | N/A | **active** | Southern Ashenveil cordon watch; reports to **Commander Renna Bracken**. Volume of sightings exceeds comfortable scout bandwidth — intel gets shorter, uglier. | Coalition escalation or blind spot — feeds Bracken’s office truth vs fear. |

### Off-screen goals (Ch15 split onward)

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| formal_field_report | Ashmere 29 | Ashmere 35 | N/A | **complete** | **Ch18 close:** interrupted **Ashmere 31** debrief **unblocked** by Kenji’s **exit** Day **256** — remaining **oral/written** closure is **routine** **Bracken** **chain** **when** she **calls** it (no longer hostage to guest-in-building). | Jostin’s **truth** **eventually** **lands** **on** **full** **slate**; **Coalition** **paper** **inch** **continues** via **addendum** **rows**. |
| escort_brynn_contract | Ashmere 29 | TBD | N/A | **complete** | Keep **Brynn** alive northbound. **Ashmere 31:** both alive at Thornkeep — objective satisfied. | — |
| personal_kenji_math | Ashmere 29 | TBD | N/A | active | Private: reconcile admiration for the ronin with **fear** of what he just walked into; journal margins for truth he won’t say aloud yet. | Shapes first reunion line when POV returns. |

---

## COMMANDER RENNA BRACKEN — Garrison Commander, Thornkeep

> **Naming note:** Older logs may say **“Hale”** — **retired**. Canon commander surname is **Bracken** (`npc_appearance.md`; Ch7, Ch16–17).

**Status:** Active
**Met:** yes — Ashmere 25, Thornkeep garrison hall (as commander); Ch16–17 office beats with Kenji; **Ch17 close** — private quarters consent arc overnight Ashmere 33→34; **Ashmere 34 morning** Kenji **ghosted** on runner knock (**Stealth**), tailed Brynn, **exited gates** (~09:00) — Bracken **not** played as omniscient; absence lands when she checks quarters / gossip crosses runners.
**Location:** Thornkeep — **garrison** (**Ashmere 35**): Kenji **departed** north **Ashmere 34** ~09:00; **captain** **routine**; **Vigor** still **on**; **discretion** + `officer_wing_discretion` **unchanged**.
**Last Updated:** Ashmere 35 (Ch18 close — `kenji_state.json` **npc_states.Bracken**)

**Physical:** Mid-forties, short-cropped dark hair going grey at the temples, scar from ear to jaw. Chainmail under coalition tabard. Weathered. Practical. Cold mug always in hand.
**Disposition to Kenji:** Intimate-trust after explicit consent beat; LG spine intact — she **chose** the line Persuasion opened; attraction and duty both real; **scandal risk** if corridor gossip catches boot-scuffs. Asked his name — he still didn't give it. **Vigor** window active again (emerald tell) — **immune to IP** until expiry per engine.
**Morale Compass:** Lawful Good — holds the bridge, holds the line, holds her people. Opposes Kenji if he threatens Thornkeep's stability or the border watch. Book 3 history: held Thornkeep through the war with 300 soldiers. Kenji came back for her. In person. Like he promised.

**Abilities:** Level 18 Fighter. Garrison commander. 300 soldiers under her command. Veteran of the Dominion war. Practical tactician, not flashy. The scar is from holding a bridge with twelve soldiers against a cavalry charge.

**Important Gear:** Practical steel (dented at the shoulder), garrison command authority.

**Personality:** Low voice. Unhurried. Efficient. Not unfriendly — just doesn't waste words. Pushes chairs with her boot. Reads people fast.

**DM — pregnancy (not IC):** **Active** — conceived **Day 248**; **Kenji unaware**; full row → **`kenji_state.json` `dm_private.pregnancies.Bracken`** and **§ DM — PREGNANCY TRACKER** above.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| border_defense | Ashmere 25 | **ongoing** (spikes toward **Hollowmere 15**) | N/A | **active** | **14** soldiers / **30** miles southern front; undead **noise** up; Coalition answers **slow**. Pair A sweeps (Kenji’s taunt) buy time, not victory. | Thornkeep holds or folds on **Still Night** pressure — military spine of arc. |
| coalition_paper_discipline | Ashmere 31 | **Ashmere 38** | N/A | **active** | **Oathbreaker** exposure + Jostin addendum + eyes-only routing — keep **Thornkeep** from becoming a circus; feed Ashenmere **truth** without losing garrison tempo. LG means **boring paperwork done correctly.** | Council trust meter; possible summons / seal-room custody asks. |
| officer_wing_discretion | Ashmere 34 | **Ashmere 36** | N/A | **active** | One night’s **secret** egress does not erase **gossip math** — who was on landing watch; whether linen / lamp oil tells a story. | If rumor ignites: discipline hearing pressure **or** forced marriage politics **or** quiet blackmail — table choice. |

---

## ELDA — Civilian, Traveler

**Status:** Active
**Met:** yes — Ashmere 24 night, Iron Key Terminus. Found at Sir Corwyn's camp, searching for her missing son. Kenji escorted her to Thornkeep. Son found Ashmere 25.
**Location:** Thornkeep waystation — with Halden (escorted off-line Ashmere 26 morning). Not on the south road with Kenji.
**Last Updated:** Ashmere 28

**Physical:** Fifty-three. Grey hair, weathered face. Traveling clothes. Small painted portrait of her son always in hand.
**Disposition to Kenji:** Overwhelming gratitude + IP Stack 7 (Ravenous Attraction, fading with blindfold). He saved her life, found her son, held her while she slept. She is in deep.
**Morale Compass:** Lawful Good — a mother who walked into undead territory alone to find her son. Doesn't break rules. Doesn't know how to fight. Just walks forward.

**Abilities:** None. Civilian. Commoner stat block. WIS +1.

**Important Gear:** Portrait of Halden (painted on wood, palm-sized). Traveling clothes. Shawl.

**Personality:** Steady under pressure when it comes to her son. Falls apart in private. Embarrassed and confused by the aura effects. Calls Kenji "you horrible young man" when he deserves it.

**IP Status:** Stack 7 (Ravenous, fading). Blindfolded during sleep — no visual contact blocks escalation. Partial fade from 8 over 8hrs. Physical contact without visual = comfort without feeding the aura.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| find_halden | Ashmere 24 | N/A | N/A | RESOLVED | Find her missing son Halden. He was traveling south from Ashenmere. | RESOLVED Ashmere 25. Kenji used Living Ground + Trade Warmth to locate Halden hiding off-road in the gap. |
| return_home | Ashmere 25 | TBD | N/A | active | Get herself and Halden safely home (presumably Ashenmere or wherever they were headed). | Needs escort through the gap. Road is dead — no living traffic in 3+ days. |

---

## HALDEN — Civilian, Elda's Son

**Status:** Active
**Met:** yes — Ashmere 25, gap zone off-road. Found hiding in a lean-to between two fallen oaks. Had been there 3 days after fleeing undead on the south road.
**Location:** Thornkeep waystation — with Elda (off Kenji’s patrol line Ashmere 26 morning).
**Last Updated:** Ashmere 28

**Physical:** Twenty-four. Sandy hair. Thin face. Earnest eyes. Not a strong face — a kind one. Looks exactly like his portrait.
**Disposition to Kenji:** Awe. A masked stranger appeared from nowhere, killed undead, and reunited him with his mother. Hero worship territory.
**Morale Compass:** Lawful Good — follows the road, follows the rules, does what his mother tells him. Not brave. Not a fighter. Just a decent young man who got caught in something bigger than him.

**Abilities:** None. Civilian. Commoner stat block.

**Important Gear:** Nothing (lost everything fleeing).

**Personality:** Earnest. Frightened. Cries when overwhelmed. Loves his mother. Not equipped for the world that's forming around him.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| survive | Ashmere 25 | N/A | N/A | active | Get home alive. Was traveling to meet his mother at the crossroads when undead appeared on the road. Hid for 3 days. | Needs escort. Cannot travel the gap alone — road is dead, undead active. |

---

### THE RED COURT — Ashenmere (Eastern Coast)

---

## LADY MIRENNE — Elder Vampire, Red Court Leader

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Ashenmere — hidden estate, eastern coast
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Looks thirty. Has been alive six hundred years. Charming, sophisticated, cultured.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Evil — six centuries of patience. Runs a silent infiltration, not a slaughter. Contracts, protocols, doppelganger rosters, coven discipline. Opposes Kenji the moment he threatens the takeover timetable — and she opposes him the way a court lawyer does, not a brawler.

**Abilities:** Elder Vampire, Level 28. Six centuries of practice. Charm, Dominate, Mist Form, elder bloodline gifts. Runs the Red Court coven's infiltration of Ashenmere — harbor master thralled, 2/5 city council replaced with doppelgangers, garrison commander recently turned. Uses portal network to move between coven cells once Ashenmere falls.

**Important Gear:** Estate, coven infrastructure, roster of replacements.

**Personality:** Patient. Cultured. The kind of villain who hosts dinner parties. Doesn't see the Court as evil — she sees it as evolution. Humans had their chance. Now it's her turn.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| take_ashenmere | pre-campaign | DORMANT + ~100 days from introduction | N/A | dormant | Silent takeover of Ashenmere — infiltration reaches 100% when all 5 council seats, the harbor, and the garrison are fully Court-controlled. Currently at 30%. Once the city falls: portal network extends Red Court reach across the coalition. | If stopped: coven collapses locally, Mirenne retreats. If completed: Ashenmere becomes a Court capital. Port city, portal hub, 2nd-phase staging ground for the rest of the coalition. |

---

## SEVREN — Doppelganger Spymaster, Red Court

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Ashenmere — mobile, operating under multiple identities
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Seventeen faces memorized. True form unknown.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Evil — spymaster who thinks in org charts. Seventeen faces, one ledger, everyone has a replacement queued. Opposes Kenji if Kenji threatens the replacement network. Will try to absorb him into the roster before fighting him.

**Abilities:** Doppelganger, Level 24. Shapeshifter. Memory-taste (can read recent memories of someone he's impersonating with physical contact). Manages the replacement network for Lady Mirenne. Not a vampire — mercenary shapeshifter employed by the Court.

**Important Gear:** Roster of all current replacements, safehouse network, multiple wardrobes for memorized identities.

**Personality:** Paranoid. Brilliant. Mercenary shapeshifter — not a vampire, employed by the Court.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| manage_replacements | pre-campaign | DORMANT (tied to Red Court clock) | N/A | dormant | Operating the identity replacement network in Ashenmere. Replacing officials with doppelgangers. Maintaining cover for all converted assets. | If captured alive: full intel on every replacement in the city. If killed: network continues but loses coordination. If he escapes: takes the roster with him and the Court disperses to other cities. |

---

## CAPTAIN HALVARD — Ashenmere Garrison (recently turned)

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Ashenmere garrison (eastern coast)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Not described. Garrison commander.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Good — was the garrison's spine before the bite, and he is still fighting the hunger three weeks in. His compass hasn't flipped yet. The DM writes him as a LG man being hollowed out in real time; if he loses the fight, his role leaves the board rather than switching alignments on the page.

**Abilities:** Level 14. Ashenmere garrison. Recently turned vampire (bitten ~3 weeks ago). Fighting the hunger. Not fully converted. Potential inside man if cured.

**Important Gear:** Garrison authority, captain's kit.

**Personality:** Grim. Exhausted. Privately terrified. Hasn't told anyone. Still doing his job because stopping means admitting.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| fight_the_hunger | ~3 weeks ago | DORMANT + ~30 days from turning (~10 days remaining at campaign start) | N/A | dormant | Recently turned. Resisting vampire hunger. If cured (creation energy? Bloom Purge? alchemy?): becomes inside man against the Court. If hunger wins: fully converted, loyal to Mirenne. | Cured: critical inside ally with garrison authority. Lost: another asset for the Court, garrison fully compromised. Ticking clock within a ticking clock. |

---

## OLD TAM — Goblin Fence, Ashenmere Docks

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Ashenmere — pawn shop, dock district (eastern coast)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Goblin.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Evil — goblin fence. Plays the docks' unwritten rules harder than any guild captain. Fair to people who pay, ruthless to people who don't. Opposes Kenji if Kenji tries to shortcut the fence system or undercut his margins.

**Abilities:** Level 6. Runs a pawn shop. Buys and sells and notices things. Knows which officials stopped eating garlic, which nobles stopped attending day-court. Knows the temple priest ran because "the altar bled." Information broker — not Court, not coalition.

**Important Gear:** Pawn shop, trade goods, accumulated intelligence.

**Personality:** Shrewd operator. Sells information for the right price. Not aligned with anyone but his own ledger.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| sell_intel | ongoing | DORMANT (activates on introduction) | N/A | dormant | Has accumulated intelligence on the Red Court's infiltration through observation of behavioral changes in Ashenmere officials. Available for sale. | If purchased: critical early intel on who's been turned/replaced. Shortcut to identifying the network without investigation. |

---

## BROTHER MORVAK — Orc Priest of the Sunfather, Ashenmere Docks

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Ashenmere — dock district mission (eastern coast)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Orc.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Good — orc priest of the Sunfather. Runs the mission for dockworkers and the mixed-race poor, wards his block against the vampires, documents the infiltration because someone has to. Opposes Kenji if Kenji endangers his people or asks him to stop witnessing.

**Abilities:** Level 12. Priest of the Sunfather. Runs a mission for orc dockworkers and mixed-race poor. Wards keeping vampires out of his block. Has noticed the infiltration pattern. Documenting it. Terrified and correct.

**Important Gear:** Holy wards (anti-vampire), documentation of the pattern, mission building.

**Personality:** Gentle, stubborn, unshakable. The kind of priest who stands in the doorway because no one else will.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| protect_the_block | ongoing | DORMANT (activates on introduction) | N/A | dormant | Maintain holy wards. Document Red Court infiltration patterns. Protect orc dockworkers and mixed-race poor from conversion. | If reached: provides detailed pattern evidence of Court infiltration. Mission block becomes a safe zone. If overrun: documentation lost, dock-district poor become a feeding ground. |

---

### THE IRON HORDE — Sunderplains (West/Northwest)

---

## WARCHIEF GORATH SKULLSPLITTER — Barbarian Warlord (Outlander)

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Sunderplains — Horde encampment (west/northwest)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Seven feet tall. Half-orc frame. Scarred. Covered in trophies taken from people who were alive when he took them.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Chaotic Evil — murderhobo min-maxer. Treats the world as a video game he is "winning." Conquers populations as loot instances, takes women as sex slaves on a level-up ladder, enslaves surviving civilians as camp labor. Short temper — rages when NPCs "don't behave the way they should." Opposes anyone who interrupts his grind.

**Abilities:** Barbarian, Level 27. Classic rage, reckless attack, brutal critical. Stacked pure STR/CON — no tactical literacy beyond "hit it until the number drops." Commands 50,000 warriors by terror and the fact that he actually wins fights; loyalty bought with plunder rights. War mammoths, troll shock troops, goblin sappers, worg cavalry — delegated to competent subordinates (Magra, Snikkit, Vrokka) because Gorath does not read maps.

**Important Gear:** A massive two-handed axe he thinks of as his "main hand weapon slot." Several rings he believes are stat boosts (some actually are). Armor he calls "plus-fours."

**Personality:** Entitled, cruel, and unselfconsciously gleeful about it. Thinks of everyone around him as NPCs — kill commands, dialogue trees, quest givers, loot. Uses words like "XP," "quest," and "class" out loud and is confused why nobody else does. Believes he is the protagonist. Rage-flips when the world fails to obey the rules he thinks he is playing by.

**[DM-only — Harrowing lore: outlander. Pulled by Morrun (God of Death) from a world that had video games. Death did not speak to him, does not coach him, does not care about his methods. Death selected him because he was always going to be a destroyer. Morality was not a factor in the selection. Gorath does not know he was pulled. He believes he "isekai'd" and that confirms for him that reality is a game. He is right that it is something, wrong about what. **Dark mirror to Kenji** — both outlanders, both carried by gods, neither knows. Kenji thinks it's real, treats people as people, grows through relationships. Gorath thinks it's a game, treats people as NPCs, grinds levels through violence. When they meet, it reads as two entire theories of what a life IS colliding in combat. Gorath will see a mid-tier "ronin" side character and not understand why the numbers aren't working.]**

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| force_recognition | pre-campaign | DORMANT + 16 days from introduction | N/A | dormant | Demands: Sunderplains recognized as sovereign nation, trade rights, portal access, seat at coalition table. Will burn western territories to get that seat. 50,000 warriors vs Katya's 12,000. FASTEST CLOCK. Timer starts when Kenji learns of the Iron Horde threat. | Negotiated: Horde becomes ally (50,000 warriors join coalition — game-changing). Delayed: logistics collapse at 30 days, tribes fracture, but alliance chance lost forever. Defeated: grudge lasting generations. |

---

## MAGRA BLOODTUSK — Orc Shaman, Iron Horde

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Sunderplains — Horde encampment (west/northwest)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Orc. Shaman.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Evil — orc shaman serving the Horde's spiritual hierarchy. The spirits she speaks for are the ones that favor conquest. Opposes Kenji if Kenji profanes Horde ceremony or undermines Gorath.

**Abilities:** Orc Shaman, Level 24. Gorath's spiritual adviser. Sees spirits of the dead. Speaks in prophecy and profanity equally. Doesn't trust humans. Didn't trust the unification. Came because the spirits told her the half-blood would either save or destroy the clans.

**Important Gear:** Shamanic implements.

**Personality:** Distrustful of humans. Prophetic. Profane. Intends to ensure Gorath saves the clans rather than destroys them. Gatekeeper to Gorath's inner circle.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| ensure_clan_survival | pre-campaign | DORMANT (tied to Iron Horde clock) | N/A | dormant | Spiritual oversight of the unification. Watching for signs of whether Gorath's path leads to salvation or ruin. Will oppose any deal she thinks endangers the clans. | If convinced: shamanic endorsement of treaty smooths tribal acceptance. If opposed: spiritual resistance fractures the Horde from within regardless of Gorath's wishes. |

---

## SNIKKIT — Goblin Sapper-Engineer, Iron Horde

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Sunderplains — Horde siege works (west/northwest)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Goblin. Tiny. Twitchy.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Chaotic Evil — goblin sapper. Gleeful about the boom, loyal only to whoever feeds him targets. Will blow up his own side laughing if the math is funnier. Opposes Kenji if Kenji is in the blast radius.

**Abilities:** Sapper-Engineer, Level 14. Designed the Horde's siege equipment. Built a catapult that fires goblin-riders in clay pots. Brilliant engineer. Talks too fast.

**Important Gear:** Siege equipment designs, engineering tools, the catapult.

**Personality:** Brilliant. Twitchy. Not proud of the goblin-rider catapult but a little proud. If orcs join the coalition, Snikkit and Garrett would either become best friends or destroy each other.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| maintain_siege_works | pre-campaign | DORMANT (tied to Iron Horde clock) | N/A | dormant | Building and maintaining the Horde's siege equipment for the western campaign. | If treaty: Snikkit's engineering joins coalition infrastructure (Garrett interaction). If war: siege equipment deployed against Thornwall. |

---

## VROKKA — Female Troll Berserker, Iron Horde Champion

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Sunderplains — Horde encampment (west/northwest)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Eight feet tall. Troll. Regenerates.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Chaotic Evil — simple, destructive, and mean. Regenerates. Doesn't plan. Opposes anything in arm's reach that looks like a fight; flips to whoever's winning. The Horde's nuclear deterrent because nobody can steer her, they just point her.

**Abilities:** Troll Berserker, Level 22. Gorath's champion. Regenerates. The Horde's nuclear deterrent. Irresistible Presence triggers on trolls (humanoid). DM should roll and have fun with whatever happens.

**Important Gear:** Whatever she can swing.

**Personality:** Dumb as a bag of rocks. Twice as mean. Doesn't want to think. Perfect arrangement with Gorath.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| champion_duties | pre-campaign | DORMANT (tied to Iron Horde clock) | N/A | dormant | Gorath's champion. Fights his challenges. Intimidates his enemies. Exists as a deterrent. | If Kenji encounters Vrokka: Irresistible Presence roll. Results could be comedic or catastrophic. Troll regeneration makes her nearly unkillable in combat. |

---

### THE TWIN WYRMS — Dragonspine (Far North)

---

## VORATHIEL THE CONQUEROR — Ancient Red Dragon

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Dragonspine Mountains — summit aerie (far north)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Ancient Red Dragon. Massive.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Chaotic Evil — ancient red dragon. Greed and dominion as a personality. All other alignments bore her. Opposes Kenji the instant he threatens her hoard, her brood, or her pride — which he already does by existing at Level 35.

**Abilities:** Ancient Red Dragon, Level 38. CR 30+. Has convinced 4/7 dragonflights to support descent. A thousand years of patience exhausted by the coalition's rise. Immune to Irresistible Presence (non-humanoid). Cannot be defeated in combat by anyone alive.

**Important Gear:** N/A — she IS the weapon.

**Personality:** Not a villain. A mother protecting her children from a species that keeps getting more dangerous. Watched the Sundered Gate, the Iron Crown War, Kenji reshaping the ley network. Afraid — and an afraid ancient dragon is the most dangerous thing alive.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| force_descent | pre-campaign | DORMANT + 95 days from introduction | N/A | dormant | Push the Reckoning vote toward descent. Currently holds 4/7 flights. Needs one more to guarantee it. Timer starts when Kenji learns of the Twin Wyrms threat. | If she wins the vote: seven dragonflights descend. World ends. If vote fails: treaty holds another millennium. Vorathiel retreats but doesn't forget. |

---

## KAELTHARION THE KEEPER — Ancient Silver Dragon

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Dragonspine Mountains — lower peaks (far north)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Ancient Silver Dragon.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Good — ancient silver dragon. Keeper of oaths, guardian of the balance against the red line. Opposes Kenji if Kenji breaks faith with the pact or endangers the peoples under her wing.

**Abilities:** Ancient Silver Dragon, Level 38. Maintains the thousand-year treaty. Holds 3/7 flights for balance. Has been looking for a champion — a human who can stand before the flights and make the case for coexistence. Immune to Irresistible Presence (non-humanoid).

**Important Gear:** N/A.

**Personality:** Tired. Kind. Certain the treaty matters. Less certain every decade that it will hold. A thousand years of holding the line against his own blood. His first question to Kenji won't be about power — it'll be about the **children he doesn't know he's fathered** (**Sera**, **Pip**, **Bracken** canon; **Mursha** pending DM) and what that says about how he treats bonds.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| defend_treaty | pre-campaign | DORMANT + 95 days from introduction | N/A | dormant | Hold the Reckoning vote for balance. Currently holds 3/7. Needs to flip one flight or find a champion who can speak for humanity. Timer starts when Kenji learns of the Twin Wyrms threat. | If treaty holds: another millennium of peace. If Kenji earns endorsement: attends Reckoning, speaks for humanity. Kaeltharion's endorsement is the entry ticket. |

---

## DRAZHARA — Dragonborn Elder, Lower Peaks

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Dragonspine Mountains — largest dragonborn settlement, lower peaks (far north)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Dragonborn.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Lawful Good — dragonborn elder. Holds the community, keeps the council, remembers the old compacts. Opposes Kenji if Kenji destabilizes the lower peaks or drags the clan into a war they can't finish.

**Abilities:** Dragonborn Elder, Level 20. Leads the largest dragonborn settlement. Caught between flights. Respects Kaeltharion but her people are tired of being second-class citizens. Wants a seat at the Reckoning that dragonborn have never had. Irresistible Presence works on dragonborn (humanoid).

**Important Gear:** Settlement leadership, dragonborn loyalty.

**Personality:** Political. Tired of second-class status. The swing factor — if Kenji offers dragonborn a Reckoning seat, she could flip the vote.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| earn_reckoning_seat | pre-campaign | DORMANT (tied to Twin Wyrms clock) | N/A | dormant | Wants dragonborn represented at the Reckoning for the first time in history. Will support whoever offers this. | If Kenji offers a seat: Drazhara's settlement supports the treaty. Potentially flips the vote. If ignored: dragonborn stay neutral or side with Vorathiel out of resentment. |

---

## IGNIS — Young Red Dragon, Vorathiel's Youngest

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Dragonspine Mountains — upper peaks (far north)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Young Red Dragon. Can take humanoid form.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Chaotic Evil — young red, Vorathiel's youngest. Inherits the fire and the hunger without any of the mother's restraint. Opposes Kenji on instinct — anything larger than him is a threat, anything smaller is food.

**Abilities:** Young Red Dragon, Level 20. Can take humanoid form (rare in young reds — a gift from Vorathiel). Scout, saboteur, infiltrator. Tests coalition defenses for his mother. Immune to Irresistible Presence in dragon form; vulnerable in humanoid form.

**Important Gear:** Humanoid disguise-kit. Burned everything else.

**Personality:** Arrogant. Impatient. Hungry for proof he deserves the descent vote. Vorathiel's test piece — if Ignis survives coalition territory, the descent is viable.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| scout_coalition | pre-campaign | DORMANT (tied to Twin Wyrms clock) | N/A | dormant | Infiltrate coalition territory in humanoid form. Map defenses. Report weaknesses to Vorathiel. | If caught: humanoid red dragon in coalition territory pops the Reckoning tension into public. If undetected: Vorathiel gains the intel to argue for immediate descent. |

---

## SKRATCH — Kobold Prophet, Dragonspine Base

**Status:** MIA
**Met:** no — MIA. Campaign threat NPC. Never encountered.
**Location:** Dragonspine Mountains — base camps (far north)
**Last Updated:** Ashmere 24 (stub created — not yet encountered)

**Physical:** Tiny. Kobold. Manic.
**Disposition to Kenji:** Unknown — not yet encountered.
**Morale Compass:** Chaotic Evil — kobold prophet at the base of the Dragonspine. Fanatic for the red line, ecstatic about the coming burn. Opposes Kenji as prophecy-obstacle. Will die whooping.

**Abilities:** Kobold Prophet, Level 10. Reads dragon omens (weather, flight patterns, heat signatures, shed scales). Rallies kobold warrens at the base of the Spine. Irresistible Presence works on kobolds (humanoid). Useful as an omen-reader if captured alive.

**Important Gear:** Prophet's regalia (scavenged dragon scales), kobold warren command.

**Personality:** Shrieking, grinning, joyful. Treats the coming descent as the best day of his life. Not afraid of death — afraid of missing it.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| prophesy_descent | pre-campaign | DORMANT (tied to Twin Wyrms clock) | N/A | dormant | Rally kobold warrens for the descent. Read omens. Broadcast prophecy through the Spine's base settlements. | If broken: warrens disperse, prophecy loses its mouthpiece. If allowed to spread: kobold warbands begin pre-descent harassment of foothill settlements ahead of the main flight action. |

---

## BOOK 1-2 CHARACTERS (stubs — expand on thread reactivation)

These characters were primary NPCs in Book 1-2 and are alive, mostly anchored in the Varenholm/Duskfen region. Their full histories live in AI_CONTEXT.md. Promoted here for quick reference; expand to full entries when their threads reactivate.

### Sera — Captain of the Darkblades / Former Assassin
**Status:** alive | **Location:** Varenholm HQ | **Last Updated:** Book 2 end
**Disposition:** Allied/Intimate (Whisperstone ring bonded)
**Morale Compass:** Lawful Good — the canonical LG. Follows the law, helps people, tells the truth even when it costs her. Opposes Kenji if Kenji becomes the unjust hand.
**Gear:** Rapier of Arrest, Breach Shard, Whisperstone ring
**Goal:** Leading Darkblades squad, renovating HQ (900+ gold unallocated)

### Pip — Director of Holdings / Innkeeper / Spatial Mage
**Status:** alive | **Location:** Duskfen (Broken Antler) | **Last Updated:** Book 2 end
**Disposition:** Intimate/Bonded (Whisperstone ring)
**Morale Compass:** Lawful Good — ledger-keeper, house-keeper, people-keeper. Runs three properties by taking care of the people inside them first.
**Gear:** Whisperstone ring, ledgers
**Goal:** Managing 3 properties (Broken Antler, Silver Draft, textile building). 400g operational budget.

### Garrett — Mercenary Leader / Advisor
**Status:** alive | **Location:** Varenholm | **Last Updated:** Book 2 end
**Disposition:** Professional/Loyal
**Morale Compass:** Chaotic Good — the canonical CG. Ex-bandit highwayman who refused to kill needlessly. Breaks rules he disagrees with, protects people without asking permission.
**Goal:** Managing Darkblade guild operations, Council liaison

### Elara — Academy Chancellor
**Status:** alive | **Location:** Varenholm Academy | **Last Updated:** Book 2 end
**Disposition:** Allied/Professional
**Morale Compass:** Lawful Good — Chancellor-class LG. Believes in institutions because institutions outlast any one person. Opposes Kenji if Kenji undermines the Academy's integrity.
**Goal:** Academy management, convergence seal support

### Aldwin — Artificer / Professor
**Status:** alive | **Location:** Varenholm Academy | **Last Updated:** Book 2 end
**Disposition:** Allied/Mentor
**Morale Compass:** Lawful Good — teacher's morality. Passes the craft on, doesn't hoard it, corrects students gently and firmly. Opposes misuse of artifice.
**Goal:** Teaching, magical research

### Maren — Enchanter / Shopkeeper
**Status:** alive | **Location:** Varenholm | **Last Updated:** Book 2 end
**Disposition:** Professional (exclusivity contract with Kenji)
**Morale Compass:** Lawful Good — contract-keeper. Does the work, delivers on time, doesn't cheat the client. Opposes Kenji if he tries to break a contract she signed in good faith.
**Goal:** Operating shop, fulfilling Kenji's commissions

---

## DISTANT NPCs — MIA (activated when threads re-engage)

Last-known states preserved in AI_CONTEXT.md. Promote to full tracker entries on reactivation. Morale compass listed for each so DM can write them consistently when they return.

- **Senna** — Chaotic Good. War-priestess with a soft spot for the broken. Acts first, apologizes never.
- **Thessaly** — Lawful Good. Scholar-healer. Opposes harm even when harm is useful.
- **Vess** — Lawful Good. Coalition intelligence chief. Will bend rules for the mission, not for herself. Currently running the coalition solo, exhausted and angry.
- **Katya Voss** — Lawful Good. General at Thornkeep (eastern border fortress — bridge between continents). Commands the post-war allied continental defense: 20,000 soldiers across six territories built in five months. Thursdays she portals to Varenholm — nobody asks why. Soldier's morality. Protects her line first. Disposition to Kenji: intimate (earned post-war).
- **Mordecai** — Lawful Evil. Canonical LE alongside Vael. Former senior of the Vess council in Varenholm; left to build abyss-portal infrastructure (Book 2 architect). In Book 3: infiltrated Vyranth pretending to offer the Emperor Forge-reactivation — the offer was a feint. He never intended to fire it; he told the Emperor he could so the Emperor would have the illusion of choice, then waited in the throne room for Kenji to take the option away. Resolution: "gentleman's understanding" fulfilled, walked away clean. Post-war: vanished. The Dominion still wants his Confluence Lens methodology; the Coalition tolerates/hunts him depending on the week. Torvald says he'll find him eventually. Court-polite, quietly lethal, plays the board for himself within whatever legal framework is currently standing. **[DM: NOT a champion of any god — mortal engineer, standalone arc. See Harrowing appendix "What This Is Not."]**
- **Vael** — Lawful Evil. The other canonical LE. Legal mind, bureaucratic knife. Never breaks a rule he hasn't already rewritten.
- **The Eldest** — Lawful Good. She/her. Sovereign of the Deepwood, ten thousand years old. Doesn't fight; she decides. Mother of three daughters (Faelindra, Nimue, Lythara) and one son (Auren). Named Kenji Champion of the Deepwood. **[DM: Creation's senior champion — long-game restraint.]**
- **Faelindra** — Lawful Good. Eldest daughter of the Eldest. Military commander, ironwood armor, three hundred years of rejected suitors. Intimate with Kenji.
- **Nimue** — Chaotic Good. Middle daughter of the Eldest. Water affinity. The one Kenji calls "toots." Intimate with Kenji.
- **Lythara** — Chaotic Good. Youngest daughter of the Eldest. Root/hair affinity. Designed the continental ley restoration network. Intimate with Kenji.
- **Auren Greyholm** — Lawful Good. Son of the Eldest. Reincarnated king who chose peace the second time. Level 28. **[DM: outlander (Arthur/TBATE homage), pulled by Creation.]**
- **Queen Lirien — the Deepwood War-Singer** — Lawful Good. Auren's adoptive elven mother. Level 18. Aether-voice: casts through song — healing, buffs, battlefield control, can shatter siege-engine enchantments. Does not know her son was a reincarnated king; only knows he is *her* son and she protects him. Deepwood-based.
- **Malcus Vyr — the Deposed Emperor** — Lawful Evil (conviction-based, not cruelty-based). Level 30 war-mage. Former Emperor of Vyranthos; wore the Iron Crown until Day 49 of the Iron Crown War, when he walked off the throne with Faelindra's hand. Alive. The Crown came off voluntarily after the Crown had drunk from him for two days — he arrived at surrender on his own terms just before the swords came out. Post-war location: unknown. Not imprisoned (surrender terms honored). Probably in Vyranth or its outskirts, stripped of imperial authority but not executed. Genuinely believed unifying the continent under Vyranthos's system would save more lives than independent territories; he was wrong with conviction, not malice. **[DM: If he reappears in Book 4+, he's a defeated idealist, not a cackling returnee. Possible threads: reform advocate, wandering scholar, or target of vengeance from Dominion hardliners who blame him for the surrender. Not currently a threat clock.]**
- **Della** — Lawful Good. Village-keeper type, Thornfield-adjacent.
- **Lena** — Chaotic Good. Runaway-turned-fixer. Helps the wrong people first.
- **Torvald** — Lawful Good. Dwarven veteran, reliable as stone.
- **Brenn** — Lawful Good. Farm-hand-turned-militia. Protects what's his.
- **Carrick Hale** — Lawful Evil. Merchant-prince, Coalition-adjacent, plays the board for himself within the rules. Opened a restaurant in Stormhaven that sells "cheeseburgers." **[DM: outlander (Carl/DCC homage), pulled by Aelith.]**
- **Jarek Windmere** — Lawful Good. Ranger/hunter-king, "the perception-god." Apex Bow, Apex Perception, Predator's Mark. Based in the Deepwood. **[DM: outlander (Jake/Primal Hunter homage). Two-source: champion of the God of Poison in his home world (Malefic Viper homage); pulled here by Aelith. Poison kit is luggage; current patronage is Creation. God of Poison is a lateral god not involved in the Harrowing.]**
- **Zarek Ashborne** — Chaotic Good. Mountain lord of Cinderpeak, wields Worldsplitter. Comes when Kenji calls — because it's fun. **[DM: outlander (Zac/Defiance of the Fall homage), pulled by Aelith.]**
- **Jace Corwin** — Lawful Good. Based in Brackenmoor. **[DM: outlander (Jason/HWFWM homage), pulled by Aelith.]**
- **Jessica Windveil** — Lawful Good. Status: **alive, whereabouts unknown**. Healer-tank hybrid (punches to heal, heals to punch). Level 27. Was at Ironholt during the Book 3 siege — per campaign bible she was punching Dominion soldiers off the wall when Kenji's relief force arrived. After the siege broke she vanished before formal coalition contact (true to form — she's the paramedic who beat recruiters unconscious and walked into the wilderness the last time someone tried to hire her). **Current goal: find a merc company or independent army to sign on with on her own terms** — she won't be absorbed into a national military, won't take orders from lords, but will fight for pay and principle with a unit that lets her do the job. Last rumored heading northwest — chasing the same "Wizard King heals by touch" story that brought her east in the first place. **[DM: outlander (Ilea/Azarinth Healer homage), pulled by Aelith. Available for Book 4 reintroduction — merc hire, tavern encounter, or she finds Kenji-in-disguise and doesn't recognize him.]**
- **Dren Valdric** — Lawful Good. Lord of Ironholt / Master Enchanter, +30 disposition to Kenji. **[DM: outlander (Richter/The Land homage), pulled by Aelith.]**

### Book 1-2 Squad Leaders & Wardbreakers (referenced in AI_CONTEXT squads / npc_appearance.md)

- **Kael** — Lawful Good. Squad leader, Eastern territories patrol. Reports to Katya. Post-war patrol duty. Loyal to the chain, loyal to Kenji. Opposes Kenji only if Kenji undermines Katya's command or the patrol's mission.
- **Brindle** — Lawful Good. Squad leader, trade route security on the Broken Antler → Ironholt circuit. Reports to Katya. Caravan escort commander. Standards-first, merchants-second.
- **Renna Bracken** — Lawful Good. Thornkeep garrison commander. **Full entry above (met Ashmere 25+).**
- **Ryn** — Chaotic Good. Spell Thief / Scout. Book 1-2 Wardbreaker. Takes what the enemy won't miss, leaves what the party can't live without. Operates inside the law only when it's cheaper.
- **Finch** — Chaotic Good. Halfling Scout / Wardbreaker. Finds things interesting when he should find them terrifying. Loyal to the squad, not the rules.
- **Varn** — Lawful Good. Half-orc Fighter / Wardbreaker. Greatshield line. Single-sentence sincerity. Opposes Kenji if Kenji asks him to stand aside while civilians get hit.

---

## DM — PREGNANCY TRACKER (Book 4)

**Authoritative machine copy:** `kenji_state.json` → `dm_private.pregnancies` (**DM ONLY** — not PC knowledge).

| Name | Status | Due / notes | Kenji knows? |
|------|--------|-------------|--------------|
| **Sera** | **Keeping** — active | ~Hollowmere/Ironveil (Season of Dark); ~7–8 mo | **No** — finds out in-room |
| **Pip** | **Keeping** — active | ~Hollowmere/Ironveil; ~7–8 mo | **No** — Brenn may force the issue |
| **Bracken** | **Keeping** — active | Conceived **Day 248** (Ashmere 26); **Day 258** = 10 days — still **too early** IC for self-diagnosis; due ~Month **11–12** | **No** |
| **Mursha** | **Pending** | **Two** exposures: Ch18 (Day 256, multiple qualifying finishes) **+** Ch21 (Day 257–258 predawn, Vigor reinforced); **no roll** logged — **DM** resolves | N/A until confirmed |
| **Haldra** | **Pending** | **One** exposure: Ch22 (Day 258, Brass Hitch private parlor; IP fail ×2 + Persuasion ADV 20 vs DC 19; Lover's Vigor triggered — brass-amber eye ring); **no roll** logged — **DM** resolves | N/A until confirmed |
| **Tamsin Vale** | **Pending** | **One** exposure: Ch25 (Day 260, berm private beat; IP severe — close range, enclosed, dark; Lover's Vigor triggered — copper ring tell visible Ch26); **no roll** logged — **DM** resolves | N/A until confirmed |
| **Brynn** | **Not pregnant** | Rolled clear vs threshold (`dm_private`) | — |
| **Senna, Elara, Thessaly** | **Terminated** | — | — |

**Bracken note:** **Ashmere 33→34** quarters repeat **does not** stack a **second** pregnancy (`ashmere_33_34_note` in JSON).

---

## CONFIRMED MOTHERS — ARRIVAL TRIGGERS (Bane / location known)

Only **Pip**, **Sera**, and **Bracken** are **confirmed carrying** as of Day **260**. **Mursha** (two exposures), **Haldra** (one exposure), and **Tamsin Vale** (one exposure) are **separate** pending flags (no rolls logged) until `pregnancies.*.status` updates in JSON.

### Pip's Arrival
**Trigger:** Location known → immediate.
**Behavior:** Arrives with a ledger, a baby, and a list of things the empire needs. No drama, no ultimatum. Just: "Here are the facts. Here is the child. Here is what comes next."
**Morale Compass:** Lawful Good (see Pip entry above).

### Sera's Arrival
**Trigger:** Never — she won't come.
**Behavior:** Waits. Refuses to chase. **Kenji must come to her.** If he doesn't, she raises the child at the Darkblades HQ and lets him find out on his own schedule. She is not hiding; she is refusing to perform the reunion.
**Morale Compass:** Lawful Good (see Sera entry above).

### Bracken's Arrival (mother #3 — **active**, undiscovered IC)
**Trigger:** Location known **or** **garrison** rumor / **officer_wing_discretion** math — she **does not** chase him; he **sees** her **or** **hears** through **Coalition** channels.
**Behavior:** **Lawful Good** commander first — child is **secondary** in **public** **mask** until **showing** forces **the** **conversation**.
**Morale Compass:** Lawful Good (see **COMMANDER RENNA BRACKEN** above).

### Archived — Senna & Elara (pregnancies **terminated**)
**No arrival-for-baby beat** — if they appear, it is **professional** (War College / Chancellor), not **carrying** **Kenji’s** **child**.

**Shared mechanic:** Active-mother arrivals compete with the **five** campaign clocks. **Mursha**, **Haldra**, and **Tamsin** (if any upgrade to confirmed) add **fourth–sixth** active pregnancy lanes — **sync** JSON **before** **running** **Bane** **convergence**.

---

## FLAGGED ISSUES

1. **Wynn's research samples** — Story-changing if they leave Thornfield. No timer set because we don't know her plan. Needs a goal with due_date when she decides to act.
2. **Amaris searching via Root Network** — She's a Level 16 druid looking for Kenji through the soil. If the Root Network extends to Millhaven's region, she could detect his ember. Needs clarification on range.
3. **Iron key investigation** — Kenji is now following the pull SSW from Millhaven. Key points to something sealed with 2-century binding, located in grid square H-9 (6 miles south of grove). Inside death-binder's 32-mile perimeter.
4. **Iron chest contents** — Stolen from Corwyn. Still unopened in Bag of Holding. Unknown what the Lych thought was worth a death knight guarding.
5. **Corban unknown** — Named as the Lych's grief-seam anchor. Status (alive/dead/undead/bound) not determined. Likely gates the ring puzzle.
6. **Death-binder parasitism** — Feeding on the Lych's 4th seam. She doesn't know. Kenji doesn't know whether to tell her, sever it, or use the information as leverage.
7. **Border-signature standardized — "the Lady".** The Chapter 5 caravan-circle parchment (previously signed "— S.") and all subsequent border proclamations now sign *"— the Lady."* The abbreviation "S." has been retired in-setting. The signature aligns the public-facing notice with what her followers already call her, which means Kenji will one day realize the signature and his enemy are the same person — the recognition is the scene, not a puzzle reveal.
8. **Book 1-2 stub characters** — Sera, Pip, Garrett, Elara, Aldwin, Maren all have minimal entries. Expand when their threads reactivate.
9. **Distant NPCs not yet promoted** — Senna, Thessaly, Vess, Katya, Mordecai, Vael, Lythara, Nimue, Faelindra, The Eldest, Auren Greyholm, Queen Lirien, Malcus Vyr, Della, Lena, Torvald, Brenn, Carrick Hale, Jarek Windmere, Zarek Ashborne, Jace Corwin, Jessica Windveil, Dren Valdric. Their last-known states are in AI_CONTEXT.md or inline above and can be promoted to full tracker entries on reactivation.

---

## THE WORLD — Tracked as a Character

**Status:** alive
**Last Updated:** Ashmere 24

### Physical Features (change with season, war, Kenji's presence)

- **Season:** Late Ashmere (autumn deepening). Still Night (winter solstice) approaching — ~16 days away (from Ashmere 29).
- **Weather:** Rain season. Grey skies, intermittent rain, cloud banks from the west.
- **Thornfield region:** Recovered from corruption. Greenveil ley lines clean. Soil waking. Farms returning.
- **Millhaven region:** Functional garrison town. Eastern approaches stable. Pallid March border 15 miles north of official maps — closer than anyone knew.
- **Pallid March:** 612-body column walking 32-mile perimeter. Death-binder's territory. Undead presence suppresses wildlife and settlement in the eastern approaches.

### Disposition to Kenji

- **Creation mode (ember active, aura on):** The living world responds. Plants lean. Ley lines brighten. Animals calm. Undead locations should come *alive* — growth pushing through decay, warmth in cold places, the land remembering what it was. Allies near portals and constructs feel hope.
- **Entropy mode (Frost Fang drawn, Solveth active):** The world dims. Temperature drops. Colors desaturate. Living things pull back. The dying and the dead feel *right* — entropy in its proper domain. The land goes still and patient.
- **Ronin mode (suppressed, disguised):** Neutral. The world reads him as a man, not a force. No environmental tell. This is his current operating mode in Millhaven.
- **Portals/Constructs near populations:** Too many = fear. The uncanny valley of magical infrastructure. Civilians don't understand what they're looking at. On the battlefield = morale boost to allies, terror to enemies.

### World Goals — Events & Seasonal

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| still_night_approaches | Ashmere 19 | ~Lathmere 15 | N/A | in_progress | Winter solstice holiday. Family, warmth, speaking difficult truths. ~21 days from current date (Ashmere 24). | Seasonal shift. Social expectations change. Characters who celebrate may seek Kenji out. Emotional vulnerability rises across all NPCs. |
| pallid_march_border_shift | Ashmere 23 | ongoing | Ashmere 27 (Coalition intake) | in_progress | Border has moved 15 miles north of official maps. Kenji discovered the shift at caravan circle (Ashmere 23-24). **Taryn filed** Bracken-chain intel + commission **Ashmere 27** — **Coalition now has the claim on paper**; speed of *belief* / redeploy still politics-limited. | Shockwave when brass acts on it, not when clerk stamps receipt. |
| thornfield_recovery | Ashmere 11 | ongoing | local knowledge only | in_progress | Greenveil corruption cleared. Ley lines clean. Village returning. Soil healing. | Thornfield becomes a viable settlement again. Amaris anchors it. Delia rebuilds community. |
| bane_of_eve_trigger | Ashmere 24 | undefined | N/A | pending | **Master trigger — starts all 5 campaign threat clocks simultaneously.** Kenji's identity or location becoming known to the wider world. Possible trigger events: (1) Ember use at scale (Mordecai detects, ripples to allies), (2) Aura overexposure / charm-affected NPC reports a siren-elf aura, (3) **Coalition council review** cross-connects Taryn’s **filed** packet (includes **Kenji** + ronin intel where she swore truth) to wider identification — **delivery already happened**; risk is **political correlation**, not “lost letter,” (4) Amaris's Root Network reaches Millhaven's region, (5) Wynn publishes her research, (6) Vess's intelligence network traces the ronin back to him, (7) **Pip/Sera** (or allies) actively search and succeed — **Senna/Elara** **not** on **pregnancy** **arrival** **list** (**terminated**), (8) Lady Nyx identifies him if encountered and chooses to broadcast. **Any one of these pops the disguise.** | All 5 threat clocks begin counting. **Confirmed** mother arrivals: **Pip** / **Sera** / **Bracken** (see **DM — PREGNANCY TRACKER**). **Mursha** TBD. Vess gets a location to be angry at. Allies stop searching blindly and start converging. The ronin stops working as a cover. |
| coalition_response_to_border | Ashmere 27 | ~Ashmere 35-40 | Ashmere 27 (packet filed) | pending | Coalition clerk stack **has** Taryn’s border/undead intel; **council** must still **decide** what to do (slow politics). Possible responses: (1) Redeploy garrisons toward Millhaven, (2) Send a fact-finding delegation (risky — they'd go to the grove), (3) Deny it / suppress it to avoid panic, (4) Brief Vess / Katya, (5) Internal vote on Coalition intervention. | Depends on response chosen. Garrison redeployment = allies near Millhaven. Delegation = possibly triggers Pallid March clock. Denial = intel gap persists. Briefing Vess = she demands to know where Kenji is (partial Bane of Eve). |

### Campaign Goals — The Fraying Empire (5 Threats)

**Campaign triggers when:** Kenji's identity or location is exposed (Bane of Eve activates). All clocks start simultaneously from that moment. Clocks are currently **DORMANT** — Kenji is still disguised as the ronin. Threat percentages represent pre-trigger buildup.

**Campaign ends when:** All five threats resolved (destroyed, negotiated, contained) OR the kingdom falls. Partial victories possible.

| goal_id | trigger | clock_rate | current_state | endgame_threshold | status | description | completion_effects |
|---------|---------|------------|---------------|-------------------|--------|---------------|--------|--------------------|
| threat_iron_horde | DORMANT | +4%/day once triggered | 0% pre-trigger | 100% (Thornwall falls, 50k Horde through the western gap) | dormant | Warchief Gorath's Sunderplains unification. Fastest clock (~25 days from trigger to endgame). Negotiation window closes at 30 days from trigger. | Negotiated: Horde joins coalition (50k warriors). Delayed past 30 days: tribes fracture, alliance impossible, 50k Horde advances regardless. Defeated: generational grudge. |
| threat_hollowing | DORMANT | +2%/day once triggered | 15% (wards weakening pre-trigger) | 100% (mythril seal breaks, The Fathom escapes) | dormant | Kharn-Dural's deep dig breached The Fathom's prison. Wards hold. Thorgrim needs ember energy or Bloom Purge to reinforce seal. ~42 days from trigger. | Seal reinforced: 40k dwarves survive, alliance possible. Seal breaks: The Fathom spreads through tunnels, corruption reaches coalition in weeks. |
| threat_pallid_march | DORMANT (Lych suspended; clock is about the suspension breaking) | variable — 5%/20 days natural, 10% per 5-day Vigor cycle | dormant, grove intact, column patrolling | 100% (Lady Nyx launches full March, kingdom-scale threat) | dormant | Lady Nyx the Warden-Queen, ley-suspended in the weeping elm grove. Threat path IS the romance path — Vigor triples her expansion rate. Death-binder siphoning her 4th seam is a second-order complication. | Without Vigor contact: slow expansion, manageable. With Vigor: blitz, unstoppable army, capture-Kenji side plot, kingdom-ending. Phylactery-equivalent is the bronze ring (4 seams). |
| threat_red_court | DORMANT | +1%/day | 30% (Ashenmere infiltration pre-trigger) | 100% (Ashenmere falls; port + portal hub under Court control) | dormant | Vampire coven infiltrating Ashenmere port city. 30% converted. Harbor Master thrall, 2/5 council doppelgangers, garrison commander turned. Lady Mirenne (Elder Vampire L28) running silent takeover. Uses portal network to infiltrate rest of coalition once city falls. | Lady Mirenne destroyed or exiled. Infiltration network dismantled. Ashenmere liberated. Captain Halvard cured or killed. |
| threat_twin_wyrms | DORMANT | +1%/day | 4/7 flights pre-trigger (Vorathiel's bloc) | 100% (Reckoning vote passes for descent; seven flights descend) | dormant | Ancient dragons deliberating The Reckoning. Vorathiel pushes descent (4/7). Kaeltharion defends treaty (3/7). Dragonborn swing factor. Kenji can be the champion Kaeltharion's been seeking. | Descent vote fails: treaty holds another millennium. Vote passes: seven dragonflights descend. Kenji earning a seat at the Reckoning is the win condition. |

### Pallid March RECONCILED

The Pallid March row above is the ONE PUBLIC FACE of the threat — what the Coalition thinks it is. The private face (Lady Nyx is a Living Lich, Vigor triples her, capture-Kenji activates after first cycle, death-binder is parasitizing her ring) lives in Lady Nyx's character entry above. Both must be DM-aware. Only one appears on the campaign clocks table — the public one.

### Apotheosis tracker

Kenji at 2,209,800 / 2,500,000 EXP. 290,200 to Level 40. Five threats provide the content. Bane of Eve provides daily supplemental. Cap is the cap.

---

## HARROWING — DM-ONLY COSMOLOGY APPENDIX

The metaplot behind the campaign. **Kenji never learns this cleanly.** Scholars (Thess, Wynn, Edwyn, Mordecai) may piece fragments over time. Gods never monologue.

### The Four Gods

- **Aelith** — God of Creation (senior). *"The First Maker."*
- **Morrun** — God of Death (senior). *"The Last Door."*
- **Thirrin** — God of Nature (junior, dying — carried in Kenji's ember). *"The Greenkeeper."*
- **Solveth** — God of Entropy (junior, dying — lives in Frost Fang). *"The Unraveler."* (Canon from Book 1.)

Forces given sentience. No moral alignment. Thirrin + Solveth = the junior pair, the living-world cycle in miniature. Both are dying; both recover as Kenji grows; both are restored at his Level 40 apotheosis.

### How the Game Is Played

- Gods do not intervene directly.
- They recruit **champions** — native mortals or pulled outlanders — as chess pieces.
- Champions act; gods watch.
- Pulling an outlander is **rare and deliberate.** Death pulls sparingly (plenty of native destroyers); Creation cultivates a broader bench because its strategy is slower.
- The Harrowing never becomes common knowledge. If a character learns fragments, they stay fragments.

### Champion Roster (reveals, not inventions)

- **Aelith's senior champion:** The Eldest. Native. 10,000 years. Long-game restraint.
- **Morrun's senior champion:** Lady Nyx. Native. Archmage-to-lich.
- **Aelith's active outlander piece:** Kenji — also carrying Thirrin and Solveth. Does not know.

### Outlander Roster

- **Creation-pulled:** Kenji, Auren Greyholm, Jarek Windmere (two-source: Poison home-world + Aelith pull), Carrick Hale, Zarek Ashborne, Jace Corwin, Jessica Windveil, Dren Valdric.
- **Death-pulled:** Gorath Skullsplitter. The single isekai'd Death piece. Murderhobo min-maxer; morality irrelevant to the pull.

**Transported Protagonists — canonical table (self-contained reference):**

| Name | Home-World Homage | Level | Current Location | Pulled By |
|------|-------------------|-------|------------------|-----------|
| Kenji | — (original PC) | 20 (→40 at apotheosis) | Varenholm / mobile | Aelith |
| Auren Greyholm | Arthur / TBATE | 28 | Silvandris | Aelith |
| Jessica Windveil | Ilea / Azarinth Healer | 27 | Unknown | Aelith |
| Zarek Ashborne | Zac / Defiance of the Fall | 26 | Cinderpeak | Aelith |
| Dren Valdric | Richter / The Land | 25 | Ironholt | Aelith |
| Jarek Windmere | Jake / Primal Hunter | 24 | Deepwood | Aelith (two-source: Ki-Shar / Poison home-world) |
| Carrick Hale | Carl / Dungeon Crawler Carl | 23 | Stormhaven (restaurant) | Aelith |
| Jace Corwin | Jason / He Who Fights With Monsters | 22 | Brackenmoor | Aelith |
| Gorath Skullsplitter | (generic murderhobo-barbarian) | 27 | Mobile / conquest-driven | Morrun |

Pull direction is DM-only. Outlanders do not know they were pulled by a specific god — most assume random transport.

### Lateral Gods (exist, not on the Harrowing board)

- **Ki-Shar** — Lateral god of the poison-touched / predator-path (Primal Hunter / Malefic Viper homage). Jarek Windmere's home-world patron. No stake in the Harrowing. Provides character flavor, not cosmic-political involvement.
- **Vess, Nyx (as doctrine), Vorathiel** — lateral / regional gods already established in world canon. None play the Harrowing.
- Other lateral gods may sponsor characters similarly without affecting the cycle.

### Three Possible Endings (at Kenji's Apotheosis, Lv 40)

- **Life-dominant:** Aelith + Thirrin win. Paradise-stasis. Nothing dies, nothing changes, the cycle stops. Ending the cycle is itself a loss.
- **Death-dominant:** Morrun + Solveth win. Wasteland. Everything unravels faster than it makes. Extinction curve.
- **Balance:** Cycle preserved. The two dying juniors fully restored. Mortals continue imperfectly. The seniors return to equilibrium.

### What This Is Not

- **Mordecai is not anyone's champion.** Standalone mortal-mage arc (senior Varenholm council → Abyss portals → Book 3 Vyranth infiltration with a Forge-reactivation feint, waiting in the throne room for Kenji). Abyss portals are what Lawful Evil mortal mages do, not a cosmic signal.
- **The Fathom is not a god.** Cosmic-horror framing retired. Treat as a local apocalyptic prison-breach, not a Harrowing faction.
- **Kenji never fights gods.** The story does not go there. Apotheosis restores the juniors; it does not cage the seniors.

---

*Last full consolidation: Ashmere 24, 1247 AR. Source: Book 4 Chapters 1-8 prose + Book 1/2 story summaries. Full rewrite to restore content after mount-cache truncation incident; all renames (Seravane→Lady Nyx, Captain Voss→Captain Halvard, Brekka→Vrokka) applied; Morale Compass attribute added to every entry.*

*Patch pass (Ashmere 24, 1247 AR, later): rename drift fixed in `fraying_empire_campaign.md`, `npc_appearance.md`, `AI_CONTEXT.md`, `world_calendar_lore.md`. Added Book 1-2 squad leaders and Wardbreakers (Kael, Brindle, Renna Hale, Ryn, Finch, Varn) to Distant NPCs. Removed redundant "Alignment:" field from Lady Nyx entry. Flagged Dren entry collision (tracker vs AI_CONTEXT / npc_appearance) for reconciliation.*

*Lore expansion (Ashmere 24, 1247 AR, later still): Lady Nyx access-control rules formalized. Name-reveal gated to Kenji only, contingent on neutral-or-higher disposition at moment of meeting. Follower alias "the Lady" justified by thrall-status (no free will, cannot know her name). Enemies see lich form exclusively. Lady-form deployment rules codified (neutral+ disposition, not-thrall, not-actively-hostile, Kenji-exception, charm-target male or female). Close to Death contagion mechanic added (1%/sec max-HP during intercourse, post-death thrall conversion — origin pathway for her standing undead army). Vigor Consequence entry updated to note Kenji must first survive Close to Death before the buff cycle even fires. Mirrored into `npc_appearance.md` alias header and added to human-form Personality block.*

*Corwyn backstory canonized (Ashmere 24, 1247 AR, same pass): Sir Corwyn the Fallen entry rewritten with full Seventy-Two Hour Death origin — paladin CON resisted Close to Death for three continuous days of forced intercourse; when he finally died, his Oath of Protection warped rather than broke, leaving him partially sentient with retained paladin class features and the original protect-the-uncommitted instinct still running underneath the Lady's orders. Explains his duality (holy + necrotic in the same armor, Oathbreaker "in pain"), his restraint toward Kenji (old Oath confirms target before striking), and his story viability as the only follower who is still a person. Lady Nyx Close to Death entry cross-references Corwyn as the canonical exception.*

*Corwyn alignment correction (Ashmere 24, 1247 AR, follow-up, then further refined): Morale Compass settled at **Lawful Good — full stop, no qualifier.** Earlier drafts used "Lawful Good — warped" but that qualifier was wrong on reflection. Alignment describes the character, not the sovereign they answer to. Corwyn follows a lawful chain, protects what he has been given to protect, does not seek power, does not enjoy harm, does not lie, confirms targets before striking, keeps his word. That is Lawful Good behavior, by the book. The queen he serves is Chaotic Evil; Corwyn is not. Two characters, two clean alignments. The word "warped" is preserved only where it describes the *Oath* (a piece of divine binding that was re-targeted — a mechanical state) — not where it would describe *him.* This is the cleanest possible read: a Lawful Good knight serving the wrong queen, and the tragedy is that both of those sentences are simultaneously true without the alignment label needing to flinch.*

*Alignment reference expanded (Ashmere 24, 1247 AR, follow-up): Morale Compass descriptors for Lawful Good and Lawful Evil enriched with their *narrative-danger* readings. LG gets the "walking on eggshells" framing — the code that makes them honorable is the same code that makes them an enemy the instant the law you crossed is theirs; their kindness is real and their sword is also real and both answer to the same sovereign. LE gets the "trustworthiness paradox" framing — more predictable than CE because they will not cross the laws of the land, making a signed deal actually binding. You can negotiate with Lawful Evil. You cannot negotiate with Chaotic Evil. This sharpens the threat taxonomy and explains why Corwyn (LG warped) is simultaneously the most honorable and the most dangerous follower in the Lady's army.*

*Border-signature retirement (Ashmere 24, 1247 AR, same pass): "S." abbreviation dropped in-setting. All border-proclamations and bound notices now sign "— the Lady." Applied in `character_tracker.md`, `npc_appearance.md`, `fraying_empire_campaign.md`, `AI_CONTEXT.md`, `Kenji_story_book4.md` line 1214, and `Book 4/Chapters/fraying_empire_chapter_05.md` line 55. The signature now matches the follower-voice alias, which makes the recognition-beat (Kenji realizing the caravan-circle Lady and the Lych are one person) a narrative scene rather than an alphabet puzzle.*

*Harrowing cosmology & pre-play gap closure (Ashmere 24, 1247 AR, final pass):*
*(1) Harrowing appendix added to this file (four gods — Aelith/Morrun/Thirrin/Solveth, champion roster, outlander roster with self-contained protagonists table, three endings, explicit exclusions for Mordecai-as-champion and Fathom-as-god).*
*(2) Harrowing tracking rules added to `dm_rules_tracking.md` as companion block (divine silence extension, information tiers, champion operating spec, outlander pull rules, endgame triggers, quick-ref roster with Lady Nyx locked as Morrun's senior champion).*
*(3) Dren collision resolved: stray "Dren — Chaotic Evil ex-smuggler" entry was a miswrite; deleted. Canonical Dren is Dren Valdric, Lord of Ironholt / Master Enchanter, LG, +30 disposition, Creation-pulled outlander (Richter/The Land homage). Collision flag on his entry removed.*
*(4) Queen Lirien entry added to Distant NPCs (Auren's adoptive elven mother, Level 18, aether-voice war-singer, Deepwood-based).*
*(5) Mordecai snapshot expanded with Book 3 arc: Vess-senior-on-Varenholm-council → left to build abyss portals → nearly aided Vyranthos Emperor against elves → post-war neutral non-combatant, Dominion wants his Confluence Lens methodology. Explicit DM tag: NOT a champion of any god.*
*(6) Aldric naming collisions resolved: Book 2 Commander Aldric Thorne → Commander Darrus Thorne (Crestfall, `Kenji_story_book2.md` ln 1489); Iron Crown reincarnated king Aldric Greyholm → Auren Greyholm throughout `iron_crown_war_campaign.md` (matches canonical tracker name from Book 3). Aldric Voss (Book 1 Duskfen blacksmith) intact — he was the original and stays.*
*(7) README updated to mention Harrowing content in both tracker file descriptions.*

*Book 3 validation pass (Ashmere 24, 1247 AR, later): re-derived end-of-Book-3 state from the 13 chapters and the final epilogue; compared against tracker entries.*
*(A) Katya Voss location corrected: "General of the Thornwall" → "General at Thornkeep (eastern border)". Post-war role expanded: 20,000 soldiers across six territories, Thornkeep as bridge fortress, Thursdays in Varenholm. Disposition to Kenji: intimate.*
*(B) Jessica Windveil expanded: status locked as alive-whereabouts-unknown. Was at the Ironholt siege per campaign bible; after relief, fled before formal coalition contact (true to her "punch recruiters, walk into wilderness" precedent). Active goal: find a merc company or independent army on her own terms — last rumored heading northwest chasing the Wizard-King-heals-by-touch rumor. Available for Book 4 reintroduction.*
*(C) Mordecai Book 3 framing polished: "nearly aided Vyranthos Emperor" → infiltrated Vyranth with a Forge-reactivation feint, never intended to fire it, waited in the throne room for Kenji. "Gentleman's understanding" fulfilled; post-war vanished; Torvald hunting.*
*(D) Malcus Vyr entry added to Distant NPCs: Level 30 war-mage, deposed Emperor of Vyranthos, alive, walked off the throne voluntarily on Day 49, current location unknown. Lawful Evil conviction-based (wrong with conviction, not cruelty). Not a threat clock.*
*(E) Distant NPCs roster updated: added Queen Lirien, Malcus Vyr, Jarek Windmere, Zarek Ashborne, Jace Corwin, Jessica Windveil to the not-yet-promoted list (the Book 3 transported/Deepwood figures were missing).*
*(F) Campaign bible `iron_crown_war_campaign.md` has stale bible-era names (Dren Vauren, Carrick Dunne, Jarek Thornveil, Emperor Varek Sol, Blade Prince Saelen, Archon Thessik/Velnis) and a cut Archon spy character. Flagged but not touched — file is marked "Reference only (Book 3 complete)" in README. Prose-era names are canonical; tracker already reflects them.*

*Book 4 validation pass (Ashmere 24, 1247 AR, later): re-derived end-of-current-prose state from Chapters 1–5; compared against tracker entries. 17 major spot-checks matched.*
*(G) Seravane → "the Lady" scrub completed in Book 4 Ch5 prose: three stale narrative references (lines 13, 57, 65 of `fraying_empire_chapter_05.md` — and their mirrors in the built `Kenji_story_book4.md` lines 1172, 1216, 1224) converted from "Seravane" to "the Lady." All three references are in Kenji's POV and tied to her border claims (the border she drew / moved / her border stakes), which she signs `— the Lady.` so the signature-name framing fits his current awareness. Kenji still has not connected the border-signing Lady to the Coalition's Lych — the reveal beat remains gated. True name "Lady Nyx" remains locked behind the in-setting condition (disposition neutral-or-higher at first meeting with Kenji). Alias rule now enforced project-wide: allies/followers → "the Lady," enemies → "the Lych," true name → reveal-gated to Kenji only.*
*(H) Vess appearance entry added to `npc_appearance.md` (placed after Sera, before Lady Nyx). Covers build (tall, full-figured, curvy), hair (deep black wavy to mid-back), face (defined, controlled half-smile), eye-shift scale (slate blue-grey → teal/cyan-green on Vigor), Vigor skin-mark (teal-green runic lines under forearms/thighs/collarbones/lower belly), the Council coat uniform details, and off-duty/intimate register. Kenji-only: under-layer of black lace + garter + lace-top thigh-highs beneath the coat.*
*(I) Minor tracker refinements: Taryn **delivery** canonized **Ashmere 27** off-screen (Ch5 ends street image; tracker bridges gap). TEILEN entry is a DM-prepared NPC with no prose appearance yet.*
