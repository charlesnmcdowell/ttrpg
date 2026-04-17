# Character Tracker — Kenji TTRPG

**Current In-Game Date:** Ashmere 26, 1247 AR (morning)
**Current Location:** Gap zone camp, off-road between crossroads and Ashenmere (south road)
**Active Book:** Book 4 — Fraying Empire (The Ronin Arc)

> **Cross-references:** DM behavior rules → `dm_rules_tracking.md` | Game engine & mechanics → `ttrpg_game_engine.py` | Live state → `kenji_state.json`

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
**Location:** Gap zone camp, off-road between crossroads and Ashenmere (south road). With Elda and Halden.
**Last Updated:** Ashmere 26

**Physical:** See npc_appearance.md (pending entry)
**Disposition:** N/A (protagonist)
**Morale Compass:** Neutral (Player Character — Hiro's call; shiftable as Kenji develops)

**Abilities (full ArchMagus kit — most are SUPPRESSED in Ronin mode):** Enhanced Arcane Edge, Haste, Stride (L4), Wind Step (70m), God Sight (120ft darkvision + crit targeting), Greater Invisibility, Clone (smoke bomb), Radiant Edge, Ward Mastery (L4), Living Ground (druid bond), Diagnostic Touch, Bond-Form Sight, Captain's Read, Siren-Elf attraction aura (Irresistible Presence DC 23 — biological attraction, NOT charm/dominate, target retains full sentience and free will), Portal Gateway, Lover's Vigor (transmitted via intimacy — +50% all stats, 5 days, eye-color shift)

### RONIN MODE — Active Loadout (Book 4)

**Why he's fighting this way:** Kenji is deliberately building a new combat persona — **The Ronin** — to throw off everyone hunting Kenji the ArchMagus / Champion of the Elves / Bane of Eve. The iaido-and-nodachi silhouette, the wuxia-style Wind Step, the troll-illusion smoke-bomb-clone combo, the trimmed spell list — none of it reads like the Wizard King's fighting style. Anyone searching for Kenji is looking for: ember aura, dual-blade Emberfrost, golden portals, Siren-Elf charm pressure, creation/entropy signature, battlefield flight. **The Ronin uses none of that.** Witnesses describe a masked swordsman with a black nodachi, a hakama, and a smoke-bomb trick. That description maps to hundreds of wandering blades across the continent. That's the point.

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
- Siren-Elf Charm Aura (DC 23) — activating it near NPCs creates witnesses who can later describe the aura and trigger Bane of Eve #2.
- Full-scale Lover's Vigor transmission to anyone whose eye-color shift will be publicly visible and traced back.

**Sensory toolkit (passive, no tell, always on):**

- Bond-Form Sight, Living Ground, Captain's Read, Steel Sight, Diagnostic Touch, God Sight — all invisible to observers, all safe to use at all times.

**Emergency-only (breaks cover, used only if the alternative is dying or exposure is already inevitable):**

- Recall (solo teleport to portal network) — visual tell is brief but complete disappearance.
- Frost Fang summon — Solveth speaks through it audibly; only draw if already committed to a fight with no survivors.
- Full Arcane/Ember arsenal — if the mask comes off, it comes off; fight as the ArchMagus.

**Important Gear:** Abyssal Shard Nodachi (red-black steel, 25% vaporize on hit), Windstrider boots, Threadwalker gloves, red-and-black hakama (+3 light armor, ward every 2 turns), Emberfang (creation sword — left behind/stored), Frost Fang (entropy sword — summonable, Solveth lives here), Bag of Holding, Iron Key (pulls SSW — 2-century binding, feeder ley-node, sealed terminator), Hollow Crown → Circuit Bracelet (Book 2 endgame), mask, ronin garb, enchanted underclothes

**Gold:** ~1,487 gp / 47 sp

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| iron_key_investigation | Ashmere 22 | Ashmere 45 (Still Night) | TBD | OPEN | Seal OPENED Ashmere 24 night at terminus (grid H-9). Key LEFT IN THE GROUND. Contents unexplored — Kenji walked away with Elda before looking. Death knight witnessed. Whatever is below the seal is now accessible. If Kenji doesn't go back, someone else will find it. | Unknown. The seal is open. The key is unrecovered. |
| iron_chest_contents | Ashmere 23 | N/A | N/A | RESOLVED | RETURNED to Sir Corwyn at terminus camp, Ashmere 24 night. Contents never opened. Kenji never looked inside. | Corwyn has his chest back. Relationship shifted to Conflicted. |
| apotheosis_level_40 | ongoing | Ashmere 45 (Still Night) | N/A | in_progress | 2,214,900 / 2,500,000 EXP. 285,100 to Level 40 (apotheosis cap). Five threats provide the content. Bane of Eve daily supplemental. The threats converge at Still Night. | Reaching L40 completes the apotheosis arc. Mechanical cap on advancement. |

---

## BRACKEN — Watch Captain, Millhaven Garrison

**Status:** alive
**Met:** yes (Ashmere 22 — Millhaven watch-hall, multiple interactions through Ashmere 24)
**Location:** Millhaven — watch-hall or home (doesn't know Kenji left)
**Last Updated:** Ashmere 24

**Physical:** See npc_appearance.md
**Disposition to Kenji:** Allied/Professional — aura exposed across debrief but NO intimacy. Professional trust developing. Personal filter not compromised.
**Morale Compass:** Lawful Good — watch captain to his bones. Upholds the law, protects the town, reads intent before swinging. Opposes Kenji if Kenji becomes the predator. Stands his ground on due process, the safety of Millhaven, and lies told to his face.

**Abilities:** Captain's Read (reads intent, rank, allegiance, lie-tells on sight), Bond-Form Sight (reads binding geometry, termination, feeder of any binding contract), 19 years watch-captain experience, Ashenmere-trained (clerk in form-room summer 1228), Coalition liaison authority

**Important Gear:** Watch brooch, seax (sword), half-plate over linen, bond-form connection to Kenji

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| ashenveil_situation | Ashmere 24 | Ashmere 32 | TBD | in_progress | Taryn's commission letter dispatched to Coalition Council. Border shift confirmed at caravan circle (15 miles north of official maps). Has not yet visited the grove or seen evidence of the Pallid March perimeter directly. Coalition response expected by Ashmere 32. | Coalition becomes aware of threat. Political/military response possible. Grove reconnaissance still pending. |

---

## TARYN — Fighter / Commissioned Scout

**Status:** alive
**Met:** yes (Ashmere 22 — Millhaven gate, multiple interactions through Ashmere 24)
**Location:** South road to Ashenmere City (departed Ashmere 24 evening or Ashmere 25 dawn, estimated arrival Ashmere 26-27)
**Last Updated:** Ashmere 24

**Physical:** See npc_appearance.md (pending entry). Late twenties, lean, dark hair, muscular. All scars healed by Kenji's creation energy (burn scar on wrist gone, scar across eyebrow gone, old ankle/shoulder injuries healed). Looks ~20 after healing.
**Disposition to Kenji:** Intimate (score 45) — knows the cold-hand tell, knows the clone wasn't real. Did not chase. Kept the career.
**Morale Compass:** Lawful Good — commissions scouts, reports up the Coalition chain, pays his debts. Opposes Kenji if Kenji undermines the Coalition or leaves civilians undefended. Stands ground on contract, rank, and the scout's code.

**Abilities:** Halberd combat (12 forms), Action Surge, Reaper's Chain (cascading multi-hit), Polearm Defense (free dodge), Victory Rush (full heal on kill), Grievous Wounds (mythril edge bleed 15% max HP/turn/stack). Level 9.

**Important Gear:** Holsk's custom thrum-alloy halberd (Featherfall / Truestrike / Bondseal runes), refitted mythril half-plate (dark steel / blue-silver sheen), Letter of Commission (Bracken's signature, Coalition Council auth, 475g paid + 5,000g pending)

**Vigor Status:** Received intimacy Ashmere 21 evening. Vigor active 5 days. Expires end of Ashmere 26. (NOTE: This expires TONIGHT at midnight if the current date is Ashmere 24 evening; adjust based on actual timeline — Vigor lasts exactly 5 days from Ashmere 21 evening, so it expires Ashmere 26 evening/night.)

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| deliver_commission_letter | Ashmere 24 | Ashmere 27 | Ashmere 30 | in_progress | Deliver Letter of Commission to Coalition Council at Ashenmere City. Claim 5,000g bounty and formalize scout role. Riding at Vigor pace while buff lasts. | Coalition Council processes commission. 5,000g released. Taryn formalized as commissioned scout. Coalition becomes aware of Millhaven Pallid March situation (the letter contains intel). Public_at reflects time for this to ripple back to Millhaven. |

**NOTES:** Vigor drops end of Ashmere 26 (expires Ashmere 27 morning). STR 24→16, DEX 21→14 when it falls. If still on the road after midnight Ashmere 26, she fights at baseline stats. Holsk's halberd may not fit at baseline strength. Holsk polearm pickup: Ashmere 28 (if in Ashenmere by then).

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
| support_key_investigation | Ashmere 24 | Ashmere 45 (Still Night) | TBD | in_progress | Support Kenji's investigation of the iron key pulling SSW. Provide entropy-domain knowledge as needed. | Key's nature and destination revealed. |

---

## LADY NYX — Living Lich / Warden-Queen (Pallid March)

**True name:** Lady Nyx. **She speaks this name aloud to exactly one person in the setting: Kenji — and only if Kenji's disposition to her reads neutral-or-higher at the moment they actually meet.** If he meets her hostile, afraid, or combat-forward, he gets "the Lych" like everyone else and the name stays locked. The reveal is conditional, not guaranteed. Before that reveal she has no name in the narrative — only aliases.

**Aliases (use these in prose until — and unless — the reveal):**
- **"their Lady" / "my Lady" / "our Lady"** — what her followers call her. Her followers are **undead enthralled thralls with no free will.** They do not know her name because they are not people anymore. "The Lady" is the only noun an enthralled mouth can shape toward her. Followers do NOT count as neutral+ disposition — they have no disposition, only command.
- **"the Lych"** — what her enemies call her. The Coalition. Ashenveil survivors. Thornkeep patrols. Old historians. The few who have seen her and lived. Derogatory. Afraid. **She is always in lich form to enemies.** No exceptions.
- **"— the Lady"** — her signature on border-proclamations and bound notices (see Chapter 5 caravan circle parchment). She signs as *the Lady* because the title is the same thing her followers call her, which is the same thing her enemies do not yet understand — that the undead signing the proclamation and the horror guarding the grove are the same authority. Public-facing signature. **Not "S."** — the abbreviation has been retired in-setting and in all notes.
- The true name "Lady Nyx" is a reveal beat gated behind Kenji's disposition. Save it.

**Status:** alive (ley-suspended, dormant)
**Met:** no — Kenji knows of her through intel and Solveth's identification. Never encountered directly. Name unknown to Kenji (see alias rules above).
**Location:** Weeping elm grove, 4 miles into woodland east of Millhaven
**Last Updated:** Ashmere 24

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

**Disposition to Kenji:** Unknown to Kenji — not yet encountered. Kenji has not yet met her in person. The grove visit that would establish her nature has not occurred. Kenji currently only knows her as "the Lych" (coalition/Bracken framing) and "the Lady" (the signature on the caravan circle parchment). He has not yet connected the two names.
**Morale Compass:** Chaotic Evil — the anchor of this alignment. Conquest, pleasure, and self are the only loyalties. Obeys only under compulsion. Lies, pretends tenderness, flips sides the instant a better throne is on offer. Will love Kenji as a pet and murder him the moment he stops being interesting.

**Abilities:** Ley-pool stasis (breathing every 11 seconds), senses and commands all 612 undead she anchors, high WIS (item-boosted), 1042 Warden-elect binding knowledge, grief-seam creation, form-switching (lich ↔ human, defaults to lich), necromantic dominion (the 612-column, the 32-mile perimeter, the territorial control), living mist grove defense (locks out intruders, grove becomes ordinary trees to unwelcome visitors)

**Important Gear:** Bronze ring (4 seams — 3 clean, 4th is grief-seam tied to Corban, parasitized by death-binder). The ring is her phylactery-equivalent — the puzzle. The iron key at Kenji's hip pulls toward something connected to her power structure (grid square H-9, 6 miles south of grove).

### Close to Death (Contagion Mechanic — CRITICAL)

Lady Nyx carries a condition called **"Close to Death."** It is a fantasy-venereal contagion tied to her Living Lich state — the alive-with-full-dominion-over-death edge that makes her what she is leaks across skin contact during intercourse.

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
| pallid_march_potential | 1042 AR | Ashmere 45 (Still Night) | TBD | active | The full Pallid March threat — Lady Nyx's lich-form ambition. The Pallid March launches at Still Night. Her advance columns are already testing borders. Even in suspension, the army she built operates on her timeline. Once freed, her nature determines whether she becomes a threat regardless of Kenji's choices (natural 5%/20 days conquest). Intimacy with Kenji accelerates this catastrophically. | Without Vigor: slow 5%/20-day expansion, manageable threat. With Vigor: 10%/cycle blitz, unstoppable army, capture-Kenji side plot triggers, kingdom-ending trajectory. |
| capture_kenji | N/A | N/A | N/A | dormant | ACTIVATES only after first Vigor buff expires. Lady Nyx hunts Kenji (sends minions or goes personally) to capture him alive and force re-buff. Repeats after every expiration. | If Kenji is captured: forced intimacy → new 5-day conquest cycle → 10% more kingdom falls. Escape or rescue required. Side plot escalates with each capture attempt. |

**THE TRAP:** She is the easiest woman in the story to bed — chaotic evil, zero inhibitions, upfront about what she wants, beautiful in human form. But each intimacy event (a) requires Kenji to *survive Close to Death* (1%/sec), (b) triggers a 10% kingdom conquest cycle if he does, and (c) eventually a capture-hunt side plot. The romance path IS the threat path AND the extinction path. Nobody omnisciently connects Kenji to the surge. The player chooses the destruction with full mechanical transparency. Kenji has not yet encountered her.

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
| find_kenji | Ashmere 11 | Ashmere 30 | N/A | in_progress | Searching for Kenji via Root Network (heartbeat through soil). He left Thornfield invisibly. She does not know where he went. 15 days of active druid searching. If she doesn't find him by Ashmere 30, she changes approach. | If she finds him: emotional confrontation. She was intimate, he vanished. |
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
| analyze_kenji_samples | Ashmere 18 | Ashmere 35 | TBD | in_progress | Scientific documentation of Kenji's biological enhancement mechanism. 10 pages with charts already written. Samples A and B in her possession. By Ashmere 35, Wynn's analysis reaches critical mass — she identifies the parallel between Kenji's enhancement and creation energy signatures. She starts asking "what IS he" instead of "what does he produce." | If this research reaches the wrong hands: Kenji's nature becomes known. If it reaches scholars: potential replication or exploitation. STORY-CHANGING if it leaves Thornfield. |
| find_kenji | Ashmere 18 | Ashmere 35 | N/A | in_progress | Knows the clone wasn't real. Furious then fascinated. Will write about it, then look for him. Analysis and search converge at the same deadline. | Confrontation or correspondence when she locates him. She has documentation that proves what he can do. |

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
| compare_notes_with_wynn | Ashmere 23 | Ashmere 30 | N/A | in_progress | Both Delia and Wynn lost vigor on Ashmere 23. Same village, ~150 people. Delia runs the only inn. Wynn visits for meals. Within 7 days one mentions feeling off to the other. By Ashmere 30 they've compared notes and realized the same man did the same thing to both of them. | Delia and Wynn connect the dots. Shared intel on Kenji's biological enhancement. Two witnesses, same village, same timeline. |

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
| taryn_polearm_pickup | Ashmere 21 | Ashmere 28 | N/A | active | Taryn's halberd fitted during vigor (STR 24, DEX 21). Pickup scheduled Ashmere 28. Vigor drops Ashmere 27 — Taryn shows up post-vigor (STR 16, DEX 14). The measurements are wrong. A runesmith who reads bodies by sight will see a different woman. He'll have questions. | Holsk notices the discrepancy. Asks questions. Data point toward Kenji's identity exposure (failure state). If Holsk connects the dots to enhancement magic, word reaches the guild network. |

---

## TEILEN — Sergeant, Millhaven Watch

**Status:** alive
**Met:** yes (Ashmere 22 — Millhaven watch-hall, multiple interactions)
**Location:** Millhaven watch-hall
**Last Updated:** Ashmere 24

**Physical:** Forties, short grey-brown hair, watch uniform (no brooch).
**Disposition to Kenji:** Neutral/Professional — filed him in one glance, focused on Bracken.
**Morale Compass:** Lawful Good — sergeant of the watch. Follows Bracken's chain, does the paperwork, keeps the peace. Opposes Kenji if Kenji breaks the watch's rules inside Millhaven's walls.

**Abilities:** Grid mapping, operational planning, compass/ruler work, military logistics. Half-elf. Off-books Pallid March expertise.

**Important Gear:** Compass, rulers, watch-hall map table access

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| coalition_response_prep | Ashmere 25 | Ashmere 32 | N/A | active | Bracken's reports on Ashenveil escalation going up the chain. Teilen preparing operational grid maps and garrison readiness assessments for potential coalition response. If response comes, Teilen coordinates Millhaven's contribution. | Coalition mobilization order routes through Teilen's desk. Quality of preparation determines Millhaven's response speed. |

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
| siphon_critical_mass | pre-campaign | Ashmere 45 (Still Night) | N/A | active | Parasitizing the 4th grief-seam of the Lych's bronze ring. Power accumulation accelerates as Still Night approaches (ley energy peaks at solstice). By Ashmere 45, the death-binder has siphoned enough to either break free of the ring dependency or challenge the Lych directly. If the Lych discovers the parasite before then, war between them — which destabilizes the Pallid March (success state for Kenji). If undiscovered, the death-binder becomes a second-front threat independent of the Lych (failure state). | Two possible outcomes: Lych discovers parasite (March fractures, opportunity for Kenji) or death-binder completes siphon (new independent threat). Either changes the board. |
| react_to_seal_opening | Ashmere 24 | Ashmere 30 | N/A | active | The terminus seal at H-9 was opened Ashmere 24 night. The death-binder's perimeter node registered the event. By Ashmere 30, the death-binder has investigated the opened seal and whatever is below it. If Kenji doesn't return first, the death-binder claims the contents. | Contents of the seal fall to whoever gets there first. The death-binder has proximity advantage. |

---

## HANDLER — Unnamed (death-binder's logistics/support)

**Status:** MIA
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

No active goals — identity and status unknown. **Investigation flag:** Who Corban was/is to the Lych determines whether he's leverage, a hostage, a ghost, or a piece of the death-binder's power feed. Solving the ring likely requires solving Corban first.

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
**Location:** Iron Key Terminus — grid H-9, edge of Lady Nyx's 32-mile perimeter. Last seen at stone ring camp with returned iron chest. Seal opened nearby. May report to Seravane.
**Last Updated:** Ashmere 25 (Chapter 6 end)

**Physical:** Black plate armor, polished. Greatsword called Oathbreaker — two signatures (holy + necrotic). The sword is in pain.
**Disposition to Kenji:** Conflicted. Initially hostile (chased clone Ashmere 23, called "THIEF"). After chest return (Ashmere 24): puzzled, wary, not aggressive. The thief came back, returned the stolen property, and walked away from an opened seal without looking inside. That's not thief behavior. The restraint — the *willingness to talk* — is a function of his partial sentience, not his orders. Orders say kill. Oath says protect. The ronin's behavior (returning stolen goods, protecting a civilian) maps to the Oath, not the enemy. Corwyn noticed. Does not know Kenji's identity.
**Morale Compass:** **Lawful Good.** Strictly speaking — not "Lawful Good with an asterisk," not "Lawful Good warped," just Lawful Good. He follows a lawful chain of command. He protects what he has been given to protect. He does not seek power for himself. He does not take pleasure in hurting anyone. He does not lie, cheat, or hunt the helpless. He confirms targets before striking and he keeps his word. That is the behavior of a Lawful Good character, and alignment describes behavior, not the morality of whoever sits on the throne he answers to. The queen he serves is Chaotic Evil. Corwyn is not. Two characters, two alignments. His Oath of Protection was redirected — who he protects changed — but the virtues that make him *him* are intact and operating on the same rules they did when he was alive. He is a good knight serving the wrong queen. That is the entire tragedy in one sentence, and it does not require the alignment label to carry a qualifier.

**Origin — The Seventy-Two Hour Death (CRITICAL — explains everything about him):**

Sir Corwyn was a Lawful Good paladin of the Oath of Protection. Before he fell, he was everything the Oath asked of him — a shield for the weak, an honest sword, a man whose word was a load-bearing beam of his life.

Lady Nyx seduced him. In Lady form. Bedded him with the intent of Close to Death running its standard course — 1% max-HP per second, dead in under two minutes, rise as thrall.

**His paladin Constitution refused to cooperate.** The Oath-bonded CON, the divine vigor of a protector at peak — it resisted the contagion directly. He didn't die in two minutes. He didn't die in an hour. He didn't die in a day.

**It took seventy-two hours of continuous connection.** She stayed with him the entire time, because the mechanic requires ongoing intercourse to deal damage — she couldn't leave and come back. For three full days she fed Close to Death into his body, and he held. His HP drained percentile by percentile while his Oath kept rebuilding the floor underneath him.

**When he finally died, he didn't fully enthrall.** The Close to Death completed the kill. The dominion-over-death rebound fired as it always does. But the Oath of Protection did not break — it *warped.* Where her other victims lost everything that made them people, Corwyn kept:

- **His paladin power.** Full suite. Lay on Hands, smite, aura, divine sense — all functional, all tied to the original Oath that was never formally broken. He can still cast as a paladin because he still *is* one, technically.
- **His sentience.** Partial. He knows who he was. He knows what he is now. He knows how he got here. Most thralls know nothing. Corwyn knows everything and remembers every hour of the seventy-two.
- **His Oath.** Not broken — warped. The Oath of Protection now reads: *protect the Lady, her grove, her domain.* But the original vector (protect the weak, protect the innocent, do not strike the defenseless) is still underneath it, unbroken because paladin oaths are not simple compliance contracts — they are identity. She could rewrite the target. She could not delete the shape.
- **His alignment.** Still Lawful Good. Strictly. The Close to Death killed his body, not his morality. He has not become cruel, he has not become grasping, he has not developed a taste for the things death knights usually develop a taste for. He serves a dark queen, but he serves her the way a good man serves — without relish, without ambition, without any of the pleasures of evil. The *law* he answers to is now hers. The *good* is the same good it was when he was alive. Alignment describes the character, not the throne; Corwyn stays Lawful Good the way Sera or Bracken do, and the sovereign he answers to is simply CE. Two characters, two alignments, both clean. That is exactly what makes him the most dangerous of her followers to her own cause — because he still has a conscience, and conscience is the one thing her other servants do not have to fight through.

This is the duality the story has been gesturing at: a creature of light and undeath in the same armor, neither fully. The necrotic runs up his sword from the pommel; the holy runs down from the edge. They meet in the middle of Oathbreaker and they are *still fighting each other.* The blade is in pain because the wielder is in pain.

**Abilities:** Death Knight, Level 26 — BUT retains functional paladin class features under the warped Oath. Lay on Hands still heals (he can heal *her grove's living defenders*, which is theologically incoherent and which he does not think about). Smite fires on command (necrotic-tinged). Divine Sense still works. Aura of Protection still extends. The Oath powers have been re-targeted, not removed. Combat: most dangerous single combatant in her army. Greatsword Oathbreaker (holy/necrotic dual-signature — sword is *in pain* because it is also carrying the duality). Retains personality, honor, memories. Hates what he's become but cannot act directly against the Lady without breaking the warped Oath, which he does not know he can survive.

**Important Gear:** Black plate armor, Oathbreaker (greatsword — holy origin, necrotic corruption, dual-signature, *in pain*). Iron chest was stolen from his camp by Kenji — he was guarding it because the Lady told him to, and his Oath requires him to recover it, which means he must chase Kenji, which means he must talk before he strikes, which means he is *here and not killing.*

**Personality:** Honorable. Tormented. The calmest voice in the Lady's army because he is the only follower who is still a *person* in there. If Kenji can break the warped Oath (not the original — the warp), Corwyn returns fully to who he was and becomes a catastrophic ally (paladin memories + death knight power + seventy-two hours of grudge against the Lady). If Kenji cannot break it, Corwyn remains the most dangerous and the most hesitant enemy Kenji will fight — the one who will pause before the killing stroke and ask a question first. The pause is the opening.

**Narrative function — why he hasn't rushed to kill Kenji:** Every prior encounter where Corwyn has talked instead of struck is because the Oath of Protection — the unbroken underneath one — is reading Kenji's intent (not yet a threat to the Lady directly) and running the old rules: *do not strike the uncommitted, confirm the target.* That is paladin doctrine, not death-knight doctrine. He is acting on the doctrine that was never deleted. The Lady's orders say kill the thief. The original Oath says confirm the threat. The original Oath moves his feet first.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| serve_the_lady | pre-campaign | DORMANT (tied to Pallid March clock) | N/A | dormant | Bound to Their Lady's service via the warped Oath of Protection (what he and the other bound undead call her). Leads assault columns. Patrols the Ashenveil. Currently hunting whatever stole the iron chest from his camp. His compliance is NOT total — the original unbroken Oath is still underneath, reading intent, hesitating on uncommitted targets. | If the warp is broken (not the Oath itself — the redirect): Corwyn returns fully to Lawful Good with full paladin class features AND death knight power AND seventy-two hours of grudge against the Lady. Catastrophic ally. If March launches before the warp breaks: he leads the vanguard, and the vanguard has a hesitation built into it that Kenji can exploit. |
| recover_iron_chest | Ashmere 23 | Ashmere 30 | N/A | in_progress | Kenji stole a warded iron chest from Corwyn's camp during the eastbound run. Corwyn chased the clone south. Doesn't know who took it or where they went. | If recovered: whatever was in the chest returns to the Lych's control. If not: Kenji has it (contents unknown — still in Bag of Holding). |
| report_to_seravane | Ashmere 25 | Ashmere 28 | N/A | in_progress | Death knight witnessed the seal opening and Kenji's departure at the terminus (Ashmere 24 night). Intel travels through the undead network in 2-3 days. Seravane knows by Ashmere 28. | The Lady's network learns the seal is open and a masked swordsman was present. Intel quality depends on what Corwyn observed and how he frames it. |

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

## CORPORAL JOSTIN — Scout, Thornkeep Garrison

**Status:** Active
**Met:** yes — Ashmere 25, south road patrol zone. Kenji found him on patrol, relayed Hale's briefing and Elda's missing son report. Jostin agreed to search the gap.
**Location:** South road patrol zone, Thornkeep garrison
**Last Updated:** Ashmere 25

**Physical:** Late twenties, lean, dark circles under his eyes. Scout's kit — light armor, short bow, journal in belt. Looks like he hasn't slept well in weeks.
**Disposition to Kenji:** Cautiously impressed. The masked ronin killed 4 wights and 2 skeleton warriors on his patrol route in one morning. Wants him to stick around.
**Morale Compass:** Lawful Good — Coalition scout, Renna Hale's best. Reports up the chain, takes the border seriously, believes in the line. Opposes Kenji if Kenji is a threat to the Coalition's intel integrity or the people behind the line.

**Abilities:** Level 10. Thornkeep garrison. Renna Hale's best scout. Watching the southern swamp border. Reports getting shorter and more frightened.

**Important Gear:** Scout gear, patrol equipment.

**Personality:** Professional. Increasingly terrified. Last report: "They're practicing formations."

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| border_watch | ongoing | Ashmere 45 (Still Night — March launches) | N/A | active | Monitoring undead activity on the southern Ashenveil border. Reports to Renna Hale. Intel quality degrading — the volume of what they're watching exceeds what two scouts can cover. Jostin is searching the gap TODAY (Ashmere 26). Report expected Ashmere 27. | If reports reach the right ears: Coalition awareness of Pallid March escalation. If suppressed: border collapse comes without warning. |

---

## COMMANDER RENNA HALE — Garrison Commander, Thornkeep

**Status:** Active
**Met:** yes — Ashmere 25, Thornkeep garrison hall. Kenji brought Elda in to report her missing son. Hale took the report, offered Jostin's patrol, noted she's short-staffed.
**Location:** Thornkeep garrison
**Last Updated:** Ashmere 25

**Physical:** Mid-forties, short-cropped dark hair going grey at the temples, scar from ear to jaw. Chainmail under coalition tabard. Weathered. Practical. Cold mug always in hand.
**Disposition to Kenji:** Curious, measuring. A masked ronin who killed 4 wights solo and brought a civilian to her door. She wants to know more. Asked his name — he didn't give it.
**Morale Compass:** Lawful Good — holds the bridge, holds the line, holds her people. Opposes Kenji if he threatens Thornkeep's stability or the border watch. Book 3 history: held Thornkeep through the war with 300 soldiers. Kenji came back for her. In person. Like he promised.

**Abilities:** Level 18 Fighter. Garrison commander. 300 soldiers under her command. Veteran of the Dominion war. Practical tactician, not flashy. The scar is from holding a bridge with twelve soldiers against a cavalry charge.

**Important Gear:** Practical steel (dented at the shoulder), garrison command authority.

**Personality:** Low voice. Unhurried. Efficient. Not unfriendly — just doesn't waste words. Pushes chairs with her boot. Reads people fast.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| border_defense | ongoing | Ashmere 45 (Still Night — March launches) | N/A | active | Defending the southern border with 14 soldiers covering 30 miles. Undead activity escalating. Reports going up chain. Coalition response expected by Ashmere 32 (7 days). If no response, Hale escalates independently. | If reinforced: Thornkeep holds. If ignored: border collapses when the March launches. |

---

## ELDA — Civilian, Traveler

**Status:** Active
**Met:** yes — Ashmere 24 night, Iron Key Terminus. Found at Sir Corwyn's camp, searching for her missing son. Kenji escorted her to Thornkeep. Son found Ashmere 25.
**Location:** Gap zone camp, off-road between crossroads and Ashenmere (with Kenji and Halden)
**Last Updated:** Ashmere 26

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
| return_home | Ashmere 25 | Ashmere 27 | N/A | active | Get herself and Halden safely home (presumably Ashenmere or wherever they were headed). Immediate — they need escort NOW. | Needs escort through the gap. Road is dead — no living traffic in 3+ days. |

---

## HALDEN — Civilian, Elda's Son

**Status:** Active
**Met:** yes — Ashmere 25, gap zone off-road. Found hiding in a lean-to between two fallen oaks. Had been there 3 days after fleeing undead on the south road.
**Location:** Gap zone camp, off-road (with Kenji and Elda)
**Last Updated:** Ashmere 26

**Physical:** Twenty-four. Sandy hair. Thin face. Earnest eyes. Not a strong face — a kind one. Looks exactly like his portrait.
**Disposition to Kenji:** Awe. A masked stranger appeared from nowhere, killed undead, and reunited him with his mother. Hero worship territory.
**Morale Compass:** Lawful Good — follows the road, follows the rules, does what his mother tells him. Not brave. Not a fighter. Just a decent young man who got caught in something bigger than him.

**Abilities:** None. Civilian. Commoner stat block.

**Important Gear:** Nothing (lost everything fleeing).

**Personality:** Earnest. Frightened. Cries when overwhelmed. Loves his mother. Not equipped for the world that's forming around him.

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| survive | Ashmere 25 | Ashmere 27 | N/A | active | Get home alive. Was traveling to meet his mother at the crossroads when undead appeared on the road. Hid for 3 days. Same escort deadline as Elda — they need to move NOW. | Needs escort. Cannot travel the gap alone — road is dead, undead active. |

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

**Personality:** Tired. Kind. Certain the treaty matters. Less certain every decade that it will hold. A thousand years of holding the line against his own blood. His first question to Kenji won't be about power — it'll be about the four women carrying his children and what that says about how he treats bonds.

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
**Status:** MIA | **Location:** Varenholm HQ | **Last Updated:** Book 2 end
**Disposition:** Allied/Intimate (Whisperstone ring bonded)
**Morale Compass:** Lawful Good — the canonical LG. Follows the law, helps people, tells the truth even when it costs her. Opposes Kenji if Kenji becomes the unjust hand.
**Gear:** Rapier of Arrest, Breach Shard, Whisperstone ring
**Goal:** Leading Darkblades squad, renovating HQ (900+ gold unallocated)

### Pip — Director of Holdings / Innkeeper / Spatial Mage
**Status:** MIA | **Location:** Duskfen (Broken Antler) | **Last Updated:** Book 2 end
**Disposition:** Intimate/Bonded (Whisperstone ring)
**Morale Compass:** Lawful Good — ledger-keeper, house-keeper, people-keeper. Runs three properties by taking care of the people inside them first.
**Gear:** Whisperstone ring, ledgers
**Goal:** Managing 3 properties (Broken Antler, Silver Draft, textile building). 400g operational budget.

### Garrett — Mercenary Leader / Advisor
**Status:** MIA | **Location:** Varenholm | **Last Updated:** Book 2 end
**Disposition:** Professional/Loyal
**Morale Compass:** Chaotic Good — the canonical CG. Ex-bandit highwayman who refused to kill needlessly. Breaks rules he disagrees with, protects people without asking permission.
**Goal:** Managing Darkblade guild operations, Council liaison

### Elara — Academy Chancellor
**Status:** MIA | **Location:** Varenholm Academy | **Last Updated:** Book 2 end
**Disposition:** Allied/Professional
**Morale Compass:** Lawful Good — Chancellor-class LG. Believes in institutions because institutions outlast any one person. Opposes Kenji if Kenji undermines the Academy's integrity.
**Goal:** Academy management, convergence seal support

### Aldwin — Artificer / Professor
**Status:** MIA | **Location:** Varenholm Academy | **Last Updated:** Book 2 end
**Disposition:** Allied/Mentor
**Morale Compass:** Lawful Good — teacher's morality. Passes the craft on, doesn't hoard it, corrects students gently and firmly. Opposes misuse of artifice.
**Goal:** Teaching, magical research

### Maren — Enchanter / Shopkeeper
**Status:** MIA | **Location:** Varenholm | **Last Updated:** Book 2 end
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
- **Renna Hale** — Lawful Good. Thornkeep garrison commander. **Now has full entry above (promoted from Distant — met Ashmere 25).**
- **Ryn** — Chaotic Good. Spell Thief / Scout. Book 1-2 Wardbreaker. Takes what the enemy won't miss, leaves what the party can't live without. Operates inside the law only when it's cheaper.
- **Finch** — Chaotic Good. Halfling Scout / Wardbreaker. Finds things interesting when he should find them terrifying. Loyal to the squad, not the rules.
- **Varn** — Lawful Good. Half-orc Fighter / Wardbreaker. Greatshield line. Single-sentence sincerity. Opposes Kenji if Kenji asks him to stand aside while civilians get hit.

---

## THE FOUR MOTHERS — MIA (arrivals triggered by Kenji's location becoming known)

Each of the four women carrying Kenji's children has a distinct arrival trigger and behavioral pattern. Arrival is not the same as knowing the father — several of them have chosen what Kenji will and won't be told. Morale compass tracked per arrival.

### Pip's Arrival (mother #1)
**Trigger:** Location known → immediate.
**Behavior:** Arrives with a ledger, a baby, and a list of things the empire needs. No drama, no ultimatum. Just: "Here are the facts. Here is the child. Here is what comes next."
**Morale Compass:** Lawful Good (see Pip entry above).

### Sera's Arrival (mother #2)
**Trigger:** Never — she won't come.
**Behavior:** Waits. Refuses to chase. **Kenji must come to her.** If he doesn't, she raises the child at the Darkblades HQ and lets him find out on his own schedule. She is not hiding; she is refusing to perform the reunion.
**Morale Compass:** Lawful Good (see Sera entry above).

### Senna's Arrival (mother #3)
**Trigger:** DM decides based on her pregnancy choice. If kept: she may not tell him. If she shows up, it's about the War College, not the baby.
**Behavior:** Professional. Deflective. Whatever she came for, the child isn't officially on the agenda.
**Morale Compass:** Chaotic Good — see Distant NPCs.

### Elara's Arrival (mother #4)
**Trigger:** DM decides based on her pregnancy choice. If kept: she has buried the paternity.
**Behavior:** Arrives as Chancellor with Academy business. The child is not mentioned.
**Morale Compass:** Lawful Good (see Elara entry above).

**Shared mechanic:** All four arrivals compete with the 5 campaign clocks for Kenji's time. Each one is a pull on the protagonist during a period when every day matters.

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

- **Season:** Late Ashmere (autumn deepening). Still Night (winter solstice) approaching — ~19 days away.
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
| pallid_march_border_shift | Ashmere 23 | ongoing | Ashmere 30 (Coalition awareness) | in_progress | Border has moved 15 miles north of official maps. Kenji discovered the shift at caravan circle (Ashmere 23-24). Taryn carrying the commission letter to Coalition Council. Coalition does NOT know yet. | When public: political shockwave. Garrison redeployment. Possible Coalition intervention. Fear in border towns. |
| thornfield_recovery | Ashmere 11 | ongoing | local knowledge only | in_progress | Greenveil corruption cleared. Ley lines clean. Village returning. Soil healing. | Thornfield becomes a viable settlement again. Amaris anchors it. Delia rebuilds community. |
| bane_of_eve_trigger | Ashmere 24 | undefined | N/A | pending | **Master trigger — starts all 5 campaign threat clocks simultaneously.** Kenji's identity or location becoming known to the wider world. Possible trigger events: (1) Ember use at scale (Mordecai detects, ripples to allies), (2) Aura overexposure / charm-affected NPC reports a siren-elf aura, (3) Taryn's commission letter reaching Coalition Council with "the ronin" references, (4) Amaris's Root Network reaches Millhaven's region, (5) Wynn publishes her research, (6) Vess's intelligence network traces the ronin back to him, (7) Senna/Elara/Pip actively search and succeed, (8) Lady Nyx identifies him if encountered and chooses to broadcast. **Any one of these pops the disguise.** | All 5 threat clocks begin counting. Four Mothers arrival triggers activate (Pip arrives, Sera waits, Senna/Elara DM-dependent). Vess gets a location to be angry at. Allies stop searching blindly and start converging. The ronin stops working as a cover. |
| coalition_response_to_border | Ashmere 30 | ~Ashmere 35-40 | Ashmere 30 (upon letter delivery + Council review) | pending | After Taryn delivers the commission letter and Coalition Council reads it: political shockwave. What do they *do* with the intel? Possible responses: (1) Redeploy garrisons toward Millhaven, (2) Send a fact-finding delegation (risky — they'd go to the grove), (3) Deny it / suppress it to avoid panic, (4) Brief Vess / Katya, (5) Internal vote on Coalition intervention. | Depends on response chosen. Garrison redeployment = allies near Millhaven. Delegation = possibly triggers Pallid March clock. Denial = intel gap persists. Briefing Vess = she demands to know where Kenji is (partial Bane of Eve). |

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
*(I) Minor tracker refinements flagged but not applied: "Source: Book 4 Chapters 1-8 prose" in line 1181 is stale (only Chapters 1–5 exist); Taryn's `Location:` field is forward-projected to the Ashenmere City road but prose ends with her still in the Millhaven street holding the commission letter; TEILEN entry is a DM-prepared NPC with no prose appearance yet. Left as-is pending direction — none are load-bearing.*
