# Character Tracker — TTRPG Universe

**Active PC:** Cookie — Halfling Ankuspawn Dancer (Level 7)
**Current In-Game Date:** Fieldday, 5 Bright Turn 1247 AR — **Day 5 night, long rest to Day 6**
**Campaign:** Cookie — starter campaign (levels 1–10)
**Chapter:** 5 COMPLETE | Chapter 6 pending
**EXP:** 66,798 / 71,275 (4,477 to go)
**Narrator Style:** Aleron Kong (irreverent, funny, mechanics-in-prose)

> **Cross-references:** DM behavior rules → `dm_rules_tracking.md` (**Scene skill preroll** + **Player success integrity** + **WORLD ECONOMY REFERENCE**) | DM Turn Protocol → `DM_TURN_PROTOCOL.md` (session start, every response, chapter end) | Game engine → `ttrpg_game_engine.py` (`skill_roll`, `contested_skill`, CLI) | Live state → `Cookie/Game init files/character_world_state.json` | Name bank → `npc_name_bank.md` | World lore → `shared_world_continuity.md` | City locations → `shared_world_continuity.md` → City Location Registry

---

## MORALE COMPASS REFERENCE

Every character entry includes a **Morale Compass** value. Use it to decide how to write them, when they hold ground, and when they oppose the PC. Five values are used:

- **Lawful Good (LG)** — Follows the law, helps people. Cooperates when justice and protection align. Opposes the PC if they become the one harming innocents.
- **Chaotic Good (CG)** — Breaks rules for good ends. Protects people without permission. Ignores laws that grind down the weak.
- **Neutral (N)** — Self-interest, balance, or capacity for genuine change. **RESERVED FOR PLAYER CHARACTERS ONLY.**
- **Lawful Evil (LE)** — Works inside the rules to accrue power and harm those beneath them legally.
- **Chaotic Evil (CE)** — Cares only for self: pleasure, power, conquest. Obeys only when forced or rewarded.

### Alignment Rules

1. **Only player-made characters are Neutral.** This covers Cookie (Hiro's character), Kenji (completed), Amaris (completed), and any future PCs. Every other NPC has a clear fixed alignment.
2. **Only Neutral characters can be persuaded to shift alignment.** NPCs do not shift — their alignment is who they are.
3. **When they oppose the PC:** They hold ground when the situation directly threatens their core compass value.

---

## COOKIE — Halfling Ankuspawn Dancer

**Status:** alive
**Level:** 7 — 66,798 / 71,275 EXP (4,477 to next)
**Location:** Cookie's room, Varenholm inn — Day 5 night. Ch5 COMPLETE, long rest to Day 6.
**HP:** 45/45 | **AC:** 22 | **Proficiency:** +3
**Saves:** DEX +11, CHA +7, WIS −2
**Skills:** Performance +9, Persuasion +9, Acrobatics +11, Deception +6
**Spells:** L1: 4/4, L2: 3/3
**Wealth:** 3 GP, 0 SP, 95 CP + bridge quest payout pending
**Attunement (2/3):** Healer's Ring, Anklet of Unarmed Combat
**Fame:** LOCAL SENSATION in Varenholm
**Last Updated:** Day 5 — Ch5 close (Four Seasons of Love, Starling show)

**Physical:** 4'10", athletic dancer's build — curvy but toned. Rich dark chocolate brown skin. Bright blue hair in twin tails. Gold-flecked eyes (Ankuspawn trait). Faint golden scroll-like markings on shoulders and torso (Ember traces — she thinks they're birthmarks). Pointed ears (halfling, slightly elongated from Ankuspawn blood). Small gold hoop earrings. Always barefoot or in light dance shoes. Reference: `Cookie/Game init files/reference_art/cookie_ref_1-4.png`
**Fashion Quirk — The Firebird Look:** Cookie is an obsessive Ignis fangirl. Ignis (fire dragon in human form) normalized wearing barely-there outfits in public — loose wraps, open corsets, sheer fabrics, lingerie-as-outerwear — because dragons don't understand human clothing modesty. Ignis made it fashion. Cookie dresses in this style daily: sexy, flowing, almost-lingerie dancer outfits in reds, golds, deep blues. Changes outfit every day — fashion IS performance. DM randomizes daily. Currently owns: indigo fitted dress (advantage on social checks), daily Firebird wardrobe, and 4 luxury performance outfits (Gilded Thread, pickup Day 4).
**Disposition:** N/A (protagonist)
**Morale Compass:** Neutral (Player Character — Hiro's call)

### Ember — Resonance Theme (unreliable stage)

Cookie's Ember shaped itself around her lifelong love of dance and music. It amplifies voice, sound, emotional projection, and performance magic. Theme-locked: CANNOT enhance physical combat, stealth, object manipulation, or mind-reading. See `character_world_state.json` → `ember_inheritance` for full rules.

- **Heartstring (passive, always on):** +2 all CHA checks when speaking/performing. Listeners within 30 ft: WIS DC 12 or emotional state shifted toward Cookie's current emotion. Cannot be turned off. Female NPCs with enchantment experience can be *aware* of it without being *swayed*.
- **Chorus of One (active, 5/day — scaled at L6):** Bonus action, 60 ft. Bolster (3 allies: 1d8+CHA temp HP + adv next save) or Disorient (3 enemies: CON DC 13, disadv attacks + −10 ft move, 1 round).
- **The Golden Note (surge):** 120 ft AOE. All allies: heal 3d10+CHA, cure fear/charm, adv all rolls 1 round. All enemies: WIS DC 15 or frightened 1 min (fail by 5+ = stunned 1 round). Cost: 1 exhaustion + 1 hr voiceless + Heartstring suppressed until short rest.

### Perks & Persistent Effects

- **Pretty Privilege (L4 perk):** 10× gold from male humanoid employers. Does NOT apply to female NPCs.
- **Ember Enhancement (L4):** All buff/heal spells and emotion transfers 10× more effective.
- **Combat Magnetism:** Male humanoid enemies = capture over kill (last target). Female humanoid enemies = jealousy (first target).
- **Dance Inspiration:** +d12 on Performance checks when dancing (not singing/speaking only).
- **Ankuspawn Beauty (racial, passive):** Supernatural beauty. Narrative flavor — not a combat aura, no saves. Men notice, stare, do favors.
- **Halfling Luck:** Reroll natural 1s on attacks, checks, and saves. Use the new roll.

### Equipment — Attuned Items

- **Healer's Ring** (Ring, Attunement) — When Cookie heals a target, she gains temp HP equal to the target's max HP until end of combat. Drawback: enemies targeting the healed ally redirect aggro to Cookie for 1 turn. Purchased from enchanter for 40 GP (Day 4).
- **Anklet of Unarmed Combat** (Wondrous Item, Attunement) — +4 DEX (mod 3→7). Kicks count as weapons: 6d8+DEX damage. DEX-based attack and damage rolls. Purchased from enchanter for 40 GP (Day 4, bundled with Healer's Ring).

### Combat — Dancer's Tai Chi

DEX-based martial art created during Ch2 bandit camp raid. High risk, high reward. Enhanced by Anklet of Unarmed Combat.
- **Kick:** 1 per round. +9 to hit (DEX 7 + prof 3 − 1). **6d8+7 bludgeoning** (Anklet). Kicks count as weapons. Always causes PRONE on hit.
- **Start of turn:** Performance roll (d20 + d12 + mod, dancing). DC 12. Success: allies gain 1 free attack. Fail: Cookie falls prone, loses turn.
- **End of turn:** Performance roll (d20 + d12 + mod, dancing). DC 12. Success: 75% dodge until next turn. Fail: Cookie falls prone.
- **Ember Prone Effect (humanoid enemies only):** Female enemies → Ridicule bonus (mock instead of kill). Male enemies → Lust bonus (STR save vs spell DC or spend turn grappling).

### Spells Known

- **Protector's Surge (L1):** +4 all ability scores, 1 creature, 6 hrs, no concentration. Only in genuinely unsafe situations.
- **Healing Dance (L2):** 3-round concentration dance. 25% max HP/round AOE. Completion: 100% heal + 10% regen/round for 1 hr.

### Active Goals

| goal_id | opened | due_date | status | description |
|---------|--------|----------|--------|-------------|
| become_famous_bard | Day 1 | ongoing | ACTIVE | Become a famous bard like Ignis. LOCAL SENSATION in Varenholm after 5 days. Starling show (Four Seasons of Love) — standing ovation, 200+ crowd. 3 return show slots offered. Torren booking patron inquiries. Isolde earring deal validated. |
| academy_term | Day 1 | Day 4 08:00 | COMPLETE | First class with Professor Ashworth. Dragon's Fire performance (22 vs DC 14). Fieldwork bounty assigned. |
| amphitheatre_spiders | Day 4 | Day 4 | COMPLETE | Burnt Amphitheatre spider infestation cleared. 3 Phase Spiders killed (all FATALITY by Fenella). 525 XP, 99 GP earned (50 spider parts + 49 quest bonus), 40 GP spent at enchanter. |
| outfit_pickup | Day 1 | Day 4 | COMPLETE | 4 luxury performance outfits picked up from The Gilded Thread. 5 total in wardrobe. |
| earring_pickup | Day 3 | Day 5 AM | COMPLETE | Custom enchanted earrings (+2 CHA, adv Persuasion & Performance) picked up from Isolde. Worn at Starling — advertising deal fulfilled. Equipped permanently. |
| starling_show | Day 1 | Day 5 EVE | COMPLETE | Four Seasons of Love — 4 songs, 4 outfits, all successful. Standing ovation from 200+. Leveled twice (5->7). 3 return slots offered. LOCAL SENSATION fame achieved. |
| academy_day6 | Day 4 | Day 6 08:00 | ACTIVE | Second class with Professor Ashworth. |
| starling_return_shows | Day 5 | Day 6+ | ACTIVE | Book 3 return show slots offered by Starling management. |
| torren_patron_inquiries | Day 5 | Day 6+ | ACTIVE | Torren locked 3 patron inquiries after Starling show (private shows, sponsorships). Follow up needed. |

### NPC Goals

| goal_id | character | opened | due_date | status | description | consequence_if_missed |
|---------|-----------|--------|----------|--------|-------------|----------------------|
| torren_starling_promo | Torren | Day 2 | Day 5 EVE | COMPLETE | Filled Starling show. 200+ audience. Locked 3 patron inquiries post-show. Now booking return shows. | N/A — succeeded. |
| isolde_earring_roi | Isolde | Day 3 | Day 7 | COMPLETE | Watched from back corner of Starling show. Earring deal validated — 200+ saw Cookie wearing her work. Relationship warm. | N/A — succeeded. |
| silka_report_cookie | Silka | Day 4 | Day 8 | ACTIVE | Report Cookie's abilities to Lyssa. Conflicted — Heartstring bond growing. | If reports: Lyssa Phase 2 activates. If delays: Lyssa sends Rook to pressure Silka. |
| ashworth_assess_cookie | Ashworth | Day 4 | Day 10 | ACTIVE | Determine what Cookie is. Saw visible magic through dance, Heartstring shifting 9/15 students. | If concludes "touched": private conversation + advanced mentorship. If inconclusive: harder fieldwork to provoke data. |
| lyssa_phase2_trigger | Lyssa Vane | Day 1 | Day 10 | ACTIVE | Identify and neutralize emerging performers. Silka's report accelerates timeline. | Starling success → Phase 2 (practice room trashed, threatening note). Quiet → slower escalation. |
| fern_beauty_line | Fern | Day 2 | Day 14 | ACTIVE | Build Torren's beauty department. First real week of customers. | Success: independence + income + roots. Fail: doubts the move, considers going home. |
| daisy_letter | Daisy | Day 1 | Day 7 | ACTIVE | Waiting for Cookie's first letter home. Growing anxious. | No letter by Day 7: sends Tomas to Varenholm to check. Letter arrives: relieved, replies with silverleaf tea reminder. |

### Chapter Log

- **Ch1** "First Night in Varenholm" (Day 1): Arrived, enrolled Academy, V.E.A. stamp, bought outfits, met Torren at Gilt Lily (failed WIS by 9). 3,375 XP. Level 1→2.
- **Ch2** "The Indigo Hustle" (Day 2): Maeven fitting, Torren seduction, Fern hired, guild rally, bandit camp raid (Tai Chi debut, 6 combat Performance rolls). 20,000 XP. Level 2→4.
- **Ch3** "Golden Returns" (Day 3): Survey Stones quest with party. Castor caught, Edric paid 6 GP (Pretty Privilege). Earring deal at Pale Lantern with Isolde. 6,000 XP. Level 4→5.
- **Ch4** "The Bat Dance" (Day 4): First Academy class — Dragon's Fire dance (22 vs DC 14, Heartstring shifted 9/15 students). Picked up outfits. Chose Academy fieldwork bounty over combat quests. Joined Team Two (Silka, Ivor, Fenella). Invented echolocation tap-dance at Burnt Amphitheatre (Performance 38, max d12) — mapped underchambers without entering. Detected phase spiders. Combat: 3 Phase Spiders at Burnt Amphitheatre, all FATALITY by Fenella. Healing Dance completed (100% regen buff active ~1 hr post-combat). Earned 99 GP (50 spider parts + 49 quest bonus). Purchased Healer's Ring + Anklet of Unarmed Combat from enchanter (40 GP). DEX 3→7, AC 18→22, kick now 6d8+7. 6,673 XP. Level 5.
- **Ch5** "The Four Seasons of Love" (Day 5): Updated guild registration (Dancer — support/tank/healer/buffer). Bridge troll quest with Davan, Aveline, Jessamine — solved non-lethally via Performance nat 20 (40 total) + Heartstring + Ember Enhancement, ogre now hands out pamphlets. Leveled to 6 (bridge domain bonus). Evening: Starling show — Four Seasons of Love (4 songs, 4 outfits, 4 emotions: grief/longing/lust/true love), all Performance checks successful with domain bonuses. Standing ovation, 200+ crowd. Leveled to 7 during Song 3. Starling comped food/drink, offered 3 return show slots. Torren locked 3 patron inquiries. Isolde watched from back — earring deal validated. LOCAL SENSATION fame in Varenholm. Long rest. 30,750 XP. Level 5→7.

---

## COOKIE'S MAIN CAST

### Daisy — Cookie's Mother
**Status:** alive | **Location:** Kettlebrook (The Wren's Rest) | **Morale Compass:** NG
**Disposition:** Loving but disapproving. Terrified of what Cookie is.
**Voice:** Clipped sentences when angry, long rambling when worried. Calls Cookie "little bean" when she forgets to be mad.
**DM Secret:** Met Kenji once, 22 years ago. Never learned his real name. Knows Cookie's father was "someone important." Cannot have more children (Mother's Curse). Blames herself.

### Tomas Wren — Innkeeper / Mentor
**Status:** alive | **Location:** Kettlebrook (The Wren's Rest) | **Morale Compass:** LN
**Disposition:** Dry, understated pride.
**Voice:** "That's nice, dear. Now mop the landing." Eyes crinkle when Cookie dances.
**DM Secret:** Former coalition army vet. Saw Varenholm during the founding. Has seen gold eyes before — on a traveler, years ago — said nothing.

### Fern — Best Friend / Roommate
**Status:** alive | **Location:** Millward Chandlery, Varenholm (sharing room with Cookie) | **Morale Compass:** CG
**Disposition:** Ride-or-die. Currently hired at Torren's beauty supply department.
**Voice:** Talks too fast, laughs too loud. "Wait wait wait — you're telling me that guy just GAVE you flowers? For dancing?"
**Campaign Role:** Gets charmed by Lyssa Vane in Phase 3 — the emotional core of the campaign.

### Professor Cadence Ashworth — Academy Mentor
**Status:** alive | **Location:** Varenholm Academy | **Morale Compass:** LG
**Disposition:** Professional fascination. Has never seen a student produce visible magic through dance alone.
**Voice:** Measured, precise. "Again. Slower. Watch where the light starts — it's not in your hands, it's in your spine."
**DM Secret:** Suspects Cookie is "touched by something." Will revise when Cookie's abilities develop.

### Lyssa Vane — Antagonist
**Status:** alive | **Location:** The Sunken Playhouse (2 days from Kettlebrook) | **Morale Compass:** NE
**Disposition:** Unknown to Cookie (not yet encountered).
**Voice:** Silky, warm, complimentary — until the mask drops. "You're so talented, darling. It would be such a shame if something happened to that voice."
**Abilities:** College of Glamour (corrupted). 15 ft charm aura — WIS DC 15 or charmed 1 min. Controls the regional performance circuit through blackmail, sabotage, and charm magic.
**Lieutenants:** Rook (CE enforcer, roaming), Silka (TN charmed spy at Academy — **secretly Ankuspawn**, Cookie's half-sister, Ember: Veil suppressed by Lyssa's silver chain amulet), Eira (NE recruiter near discovery location).
**DM Secret:** Contacted 2 years ago by anonymous patron (Cult of Anku recruiter). Paid 5 SP/month to report performers with "unusual golden eyes or supernatural charm." Thinks it's a noble with a fetish.

---

## COOKIE'S EXTRA NPCs

| Name | Alignment | Ch | Role | Status | Key Notes |
|------|-----------|-----|------|--------|-----------|
| **Torren** | TN | 1 | Textile merchant / promoter | active | Completely smitten. Failed WIS by 9. Seduced Ch2. Now promoting Cookie's Starling show. Hired Fern at 10× salary. Will do anything Cookie asks. |
| **Gilt Lily barkeep** | TN | 1 | Inn barkeep | MIA | Stocky woman, cropped hair. Gave Cookie intel on Torren. No ongoing story thread. |
| **Maeven** | TN | 2 | Tailor, Chandler's Row | MIA | Fitted Cookie's indigo dress. Professional. Returns if Cookie commissions again. |
| **Gruff** | LN | 2 | Adventurer's Guild clerk | MIA | Handles quest postings. Returns if Cookie visits guild. |
| **Dorith** | NG | 2 | Adventurer healer | MIA | Party member (bandit camp, survey stones). No contact since Ch3. |
| **Dalla** | TN | 2 | Adventurer fighter | MIA | Party member. No contact since Ch3. |
| **Silas** | CN | 2 | Adventurer rogue | MIA | Party member. No contact since Ch3. |
| **Marta** | NG | 2 | Adventurer ranger | MIA | Party member. Tracked cart ruts to Castor's farm. No contact since Ch3. |
| **Garron** | TN | 2 | Adventurer crossbowman | MIA | Party member. Originally "Fen." No contact since Ch3. |
| **Alderman Edric Tosse** | LN | 3 | City official | MIA | Quest complete. Returns only if civic matters arise. |
| **Castor** | TN | 3 | Turnip farmer | MIA | Serving 30 days labor. Returns Day 34 if story needs him. |
| **Isolde** | TN | 3 | Enchantress, The Pale Lantern | active | Apprenticed under Maren Holt (Gilt Lens). Female — immune to Pretty Privilege. Aware of Heartstring but not swayed (enchantment experience). Struck advertising deal: 85 GP earrings for 4 GP + Starling promotion. Watched Ch5 show from back corner — deal validated. |
| **Davan** | TN | 5 | Adventurer, greatsword fighter | MIA | Human male. Joined bridge troll quest party. No ongoing story thread. |
| **Aveline** | TN | 5 | Adventurer, archer/scout | MIA | Human female. Joined bridge troll quest party. No ongoing story thread. |
| **Jessamine** | NG | 5 | Adventurer, druid | MIA | Human female. Joined bridge troll quest party. No ongoing story thread. |
| **Silka** | TN (charmed, was NG) | 4 | Academy student / Lyssa's spy / **SECRET ANKUSPAWN** | active | Cookie's half-sister (NEITHER KNOWS). Ember: Veil (concealment/illusion) — ALL abilities SUPPRESSED by Lyssa's silver chain amulet. Grey eyes (gold suppressed), scroll marks hidden under conservative clothes. Sang perfect elven lullaby in Ashworth's class. Failed Heartstring WIS save — blushed when Cookie called her beautiful. On Team Two for Burnt Amphitheatre assignment. **REVEAL: save for high-danger mission, several chapters out.** |
| **Ivor** | TN | 4 | Academy student, lute player | active | Team Two. Lanky, sandy-haired, nervous. 3 cantrips: Light, Mending, Minor Illusion. Mother was a guild circuit bard — Lyssa Vane "made it difficult." Supported echolocation dance with Minor Illusion visualization. |
| **Fenella** | TN | 4 | Academy student, shortbow | active | Team Two. Stocky, freckled, practical. Father is gamekeeper outside Duskfen. Field medicine, tracking. Here for Warden credential, not performance. Mapped while others performed. |

---

### SILKA EMBER SPEC — Veil (concealment/illusion)
**Stage:** SUPPRESSED (silver chain amulet). Would be Unreliable if freed.
**Reveal timing:** High-danger mission, several chapters out. Chain comes off in life-or-death choice — Lyssa's mission vs Cookie's life.

**Tier 1 — Fade (passive, always-on when unsuppressed):**
+2 Stealth/Deception. 30 ft radius. WIS DC 14 to notice her when she doesn't want attention. WIS DC 12 or memories of her become vague afterward. Cannot suppress.

**Tier 2 — Phantom Echo (active, 3/day):**
Bonus action, 60 ft. **Duplicate:** illusory copy of self or 1 other person, INT DC 13 to see through, 1 min. **Cloak:** extend Fade to 3 allies, 30 ft, 1 min.

**Tier 3 — The Vanishing (surge):**
120 ft AOE. Allies: TRUE invisibility 1 min (sight + sound). Enemies: INT DC 15 or confused (forget everything, 1 min). **Cost:** 1 exhaustion + hyper-visible 1 hr (glowing, impossible to miss) + Fade suppressed until short rest.

**Sibling Resonance (both Embers unsuppressed, 30 ft):**
Cookie's Heartstring DCs +2, Silka's Fade DCs +2. Both feel unexplainable warmth. Unmistakable to trained magic users (Ashworth, Isolde) — proves shared bloodline.

---

## KINGDOM-ERA NOTABLE FIGURES (25 years post-Book 4)

These are former campaign NPCs now part of the world's living texture. Cookie may encounter them, hear about them, or be affected by their presence. Full lore in `shared_world_continuity.md`.

### AnkuNyx / Kenji — The Dragon Emperor (NPC — completed PC)
**Status:** alive | **Level:** 40 (Apotheosis) | **Morale Compass:** Neutral (former PC)
**Location:** Unknown — disappears for months or years. Most often in the Deepwood with the three elf sisters.
**What Cookie knows:** The Dragon Emperor exists. Everyone knows. He unified the continent. He's a legend more than a man. Cookie does NOT know he is her father.
**DM Secret:** Cookie's biological father via Bane of Eve encounter with Daisy 22 years ago. Full mechanical state in `kenji_state.json`. All 5 existential threats resolved. Kingdom of Ankunyx declared. 25 bonded lovers in the Soul Nexus.
**Relevance to Cookie:** Father (unknown). Source of her Ankuspawn heritage. Source of Ember. Will not appear in Cookie's campaign unless world-shaking moment demands it — Cookie's story is hers, not his.

### Vess — Head of the Coalition Council
**Status:** alive | **Location:** Varenholm (coalition HQ) | **Morale Compass:** LG
**What Cookie knows:** Public figure — the coalition's top administrator. Known for competence and iron will. Wedding rumors with Korrim the dwarf thane are tavern gossip.
**DM Secret:** Bore Ankuspawn with Kenji. Subject to Mother's Curse. Quietly seeking Nyx's fertility elixirs — doesn't know what they're made from. If she discovers the truth, she's the most dangerous person who could crack Nyx's operation open.

### Mirenne — Coalition Council Member (Vampire)
**Status:** alive (undead) | **Location:** Varenholm | **Morale Compass:** LE
**What Cookie knows:** Vess's shadow. Less visible, widely feared. Vampires are legal citizens under kingdom law.

### Pip — Innkeeper
**Status:** alive | **Location:** Heartland inn (likely near Varenholm/Duskfen) | **Morale Compass:** LG
**What Cookie knows:** A well-known innkeeper, if Cookie's traveled enough. Common folk might mention her.
**DM Secret:** Former companion of the Dragon Emperor. Bore Ankuspawn. One of her children has gone missing (captured by Nyx — Cult of Anku on-ramp for any PC who visits her inn).

### Sera — Captain of the Darkblades
**Status:** alive | **Location:** Stormhaven port | **Morale Compass:** LG
**What Cookie knows:** The Darkblades are a legitimate maritime security force. Sera commands respect on the docks.

### Ignis — "The Firebird" (Elder Fire Dragon / Bard)
**Status:** alive | **Location:** Traveling performer — kingdom-wide | **Morale Compass:** CG
**What Cookie knows:** COOKIE'S IDOL. The most famous bard alive. Fire dragon who mastered multiple instruments. Concerts feature real dragonfire fireworks. Cookie's entire dream is to be like Ignis.
**DM Secret:** Bonded to AnkuNyx. Cookie and Ignis share a father. If they ever meet, the resonance between their Ember sparks would be unmistakable. Ignis might be the first person to tell Cookie the truth.

### Maren Holt — Enchanter (Retired)
**Status:** alive (retired ~15 years) | **Location:** Varenholm | **Morale Compass:** LG
**What Cookie knows:** The famous enchanter of pre-Golden Age Varenholm. Isolde apprenticed under her. Grandson now runs The Gilt Lens (minor repairs/lenses).
**Relevance:** Lore callback — Isolde references her mentor when discussing the earring commission.

### Nyx — The Lich Queen / Head of the Ashenveil Academy (HIDDEN ANTAGONIST)
**Status:** alive (mostly — cured of full vampirism) | **Location:** The Ashenveil Academy | **Morale Compass:** CE
**What Cookie knows:** The Dragon Emperor's wife. Respected, feared, untouchable. Runs a prestigious magic academy in the southeast. Beyond that — nothing.
**DM Secret:** Founded the Cult of Anku. Captures and harvests mature Ankuspawn for powerful elixirs. Cookie is a "critical" priority target (female Ankuspawn + Resonance theme = highest-value for charm research). Lyssa Vane's anonymous patron is a Cult recruiter. The elixirs are the breadcrumb trail. Full lore in `shared_world_continuity.md`.
**Relevance to Cookie:** Lyssa's patron → Cult of Anku → Nyx is the chain. Defeating Lyssa in Phase 4 reveals the patron's identity. This is Cookie's on-ramp to the kingdom-spanning Nyx conspiracy.

### The Eldest — Sovereign of the Deepwood
**Status:** alive | **Location:** Deepwood / Silvandris | **Morale Compass:** LG
**What Cookie knows:** Nothing — the Deepwood is closed to outsiders.

### The Ousaki — Guardians of the Forest (3 half-elf Ankuspawn)
**Status:** alive | **Location:** Deepwood / Silvandris | **Morale Compass:** varies
**What Cookie knows:** Nothing.
**DM Secret:** Kenji's children with the three elf sisters. Young adults (18-25). Secretly ambitious — feel the Deepwood is too small. If any leaves the forest, Nyx's Cult detects them immediately. Highest-value targets the cult has ever identified.

---

## CAMPAIGN THREATS

### Lyssa Vane — Regional Antagonist (Levels 5–8)

**Status:** active — not yet encountered by Cookie
**Threat Level:** Scaled for levels 5-8. Regional menace, not world-ending.
**Phase 1** (L1-3): Cookie's first booked performance gets cancelled. "Someone told me not to book new acts without clearance." First hint of Lyssa's network. *(Not yet triggered — Cookie bypassed this by going through Torren and the Starling directly.)*
**Phase 2** (L4-6): Cookie becomes known. Lyssa notices. Practice room trashed. Note: "The heartland has enough bards." *(Cookie is now L7 — LOCAL SENSATION fame after Starling show. Phase 2 triggers imminent.)*
**Phase 3** (L7-9): Escalation. Fern charmed and turned. Cookie discovers the Sunken Playhouse and the Resonance Chamber. Young bronze dragon recognizes her Ember. *(Cookie entering this level range now.)*
**Phase 4** (L10): Final confrontation at the Sunken Playhouse. Performance duel — bard vs. bard. Fern freed. Lyssa's ledger reveals the anonymous patron → Cult of Anku thread opens.

### Cult of Anku — Background Threat (kingdom-spanning)

**Status:** background — becomes active post-Lyssa
**What Cookie knows:** Nothing.
**Mechanics:** Level 30+ CE women, Ember nullification gear, one warning before lethal response. Cookie's Ember abilities go dark against their wards. Full rules in `shared_world_continuity.md` and `dm_rules_tracking.md`.
**Connection:** Lyssa's anonymous patron is a Cult recruiter. Defeating Lyssa reveals the patron's identity. Cookie is on Nyx's target list as a "critical" priority.

---

## THE WORLD — Kingdom of Ankunyx (25 years post-Book 4)

**Era:** Golden Age under the Dragon Emperor. Continental authority, decentralized governance. All former threats resolved.

**Kingdom-wide laws:** Dragons protected (capital offense to hunt). Vampires are citizens. Orcs are licensed mercenaries. Dwarves dominate smithing and enchantment markets. Necromancy illegal except under license.

**Varenholm (Cookie's city):** Heartland capital. Largest scholarly city. Academy expanded to include bard school. Arts scene thriving — The Starling, The Gilt Lily, The Gilded Thread, Maeven's, The Pale Lantern all post-Golden Age establishments. Check City Location Registry in `shared_world_continuity.md` when narrating.

**Season:** Early Bright Turn (spring). 6-day weeks: Rootday, Forgeday, Windday, Fieldday, Crownday, Stillday.

**Elixir rumors (DM-only hook):** Whispers about impossibly powerful potions — strength ×100, unlimited spell slots, immunity to physical damage. "Where do they come from?" leads to Nyx. Too powerful to ignore. Everyone's talking about them.

---

## FLAGGED ISSUES

1. **Silka (Lyssa's spy) at the Academy — ANKUSPAWN** — Silka is Cookie's half-sister (neither knows). Both are Ankuspawn — daughters of the Dragon Emperor. Silka's Ember (Veil: concealment/illusion) is suppressed by Lyssa's silver chain amulet, which also hides her gold eyes and scroll markings. She dresses conservatively to cover any remaining marks. Lyssa KNOWS Silka is Ankuspawn and is deliberately keeping her suppressed and controlled. Cookie's Heartstring creates Ember resonance when near Silka — a faint warmth neither girl can explain. If other students discover two Ankuspawn topping first-year class, resentment will be immediate: "cheating bastards with daddy's Embers." Timeline: Silka will report Cookie to Lyssa, accelerating the antagonist — but her growing emotional bond with Cookie (Heartstring + sisterly Ember resonance) will eventually force a loyalties crisis.
2. **Cult of Anku target list** — Cookie is a "critical" priority target. Female Ankuspawn + Resonance theme = highest-value combination for Nyx's charm research. The cult doesn't know about Cookie yet, but Lyssa's reports about "gold-eyed performers" feed the recruiter who feeds the cult.
3. **Fern's future** — Fern gets charmed by Lyssa in Phase 3. Cookie's best friend becomes a weapon against her. This is the campaign's emotional core.
4. **Daisy doesn't know** — Cookie's mother has no idea Cookie is in danger. If the cult comes for Cookie, Daisy has no defenses and no understanding of what her daughter is.
5. **Ignis encounter** — Cookie's idol. If they meet, the Ember resonance would be unmistakable. Ignis might tell Cookie the truth about her heritage. This is a world-changing personal moment.
6. **Torren as liability** — Completely under Cookie's influence. If Lyssa targets Cookie's support network, Torren is easy leverage. Male, charmed, wealthy, no combat ability.
7. **Starling performance (Day 5) — COMPLETE** — Four Seasons of Love, standing ovation, 200+ crowd, LOCAL SENSATION fame. Torren locked 3 patron inquiries. Isolde validated. 3 return show slots offered. High visibility = Silka's report triggers faster — Lyssa Phase 2 acceleration imminent.
8. **Ankuspawn prejudice arc** — When classmates eventually connect Cookie + Silka's talent to their Ankuspawn heritage, resentment erupts: "Dragon Emperor's bastards born with Embers — the rest of us never had a chance." This is not entirely unfair. The prejudice is real, the advantage is real, and Cookie will have to decide whether she earned her talent or inherited it. Social pressure will push other students to exclude, sabotage, or petition against them. Ashworth's reaction is key — does she protect them or hold them to a higher standard?
9. **Silka's loyalty crisis (SAVE — high-danger chapter)** — The chain comes off in a life-or-death moment. Silka must choose: Lyssa (who "saved" her but is actually imprisoning her) or Cookie (who she's supposed to betray but who is her sister). The Ember resonance activates. Both girls' powers amplify. Anyone with magical training recognizes shared bloodline. This is the campaign's second major emotional beat (after Fern's charming in Phase 3).

---

## KENJI CAMPAIGN ARCHIVE REFERENCE

Kenji's completed campaign data lives in:
- `kenji_state.json` — full mechanical state (Level 40, Book 4 complete)
- `book4_endgame_tracker.md` — endgame threat resolution
- `Kenji_story_book1.md` through `Kenji_story_book4.md` — narrative chapters
- `npc_appearance.md` — visual descriptions of Kenji-era NPCs
- `iron_crown_war_campaign.md` — Book 3 campaign reference
- `fraying_empire_campaign.md` — Book 4 campaign reference

These files are read-only references for lore callbacks. Do not update them for Cookie's campaign.
