# Character Tracker — TTRPG Universe

**Active PCs:**
- **Cookie** — Halfling Ankuspawn Dancer (Level 10 — STARTER CAP) — Ch11 "From Kettlebrook" COMPLETE | Civic Auditorium recital arc closing
- **Holly** — Snow Elf escapee, Master Toymaker's former conscript (Level 297 — POWER-OVERRIDE FLAGGED) — Ch1 PENDING | Solandra Bay arrival, honeymoon hour 7/24
- **Shen Sama** — Ankuspawn True Dragon (Level 1, 24-yr-old half-Kenji+half-Vorathiel) — Ch2 in progress | Highford foothills, Dragon Form aftermath
- **Amaris** — Eastern frontier (Level 5 Sorcerer) — campaign COMPLETE epilogue | Briarstone Homestead, retired
- **Kenji** — The Dragon Emperor (Level 40 Apotheosis) — Book 4 Ch42 COMPLETE, Ch43 OPEN | Ashmere 69 dawn, Dragonspine peaks

**Cross-character continuity:** Cardinal Rule 14 governs cross-PC visibility. The launcher's `_cross_character_sync.py` runs on every boot to refresh each PC's `_world_cross_references` block. Each PC's full section below contains signature abilities, quirks, threat clocks, and cross-character relevance notes.

**Narrator Style (per-character defaults):** Cookie — Aleron Kong (irreverent, funny, mechanics-in-prose). Holly — fish-out-of-water comedy meets cozy-inventor with snow-elf vulnerability. Shen Sama — quiet-monster road movie. Amaris — eastern-frontier western. Kenji — high-fantasy political weight.

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

**Status:** alive | healthy | **EMBER_CAPPED** (no further Ember growth until story trigger)
**Level:** **10** — 131,768 / 130,000 EXP (cap reached). Mechanical progression cap. Ember Enhancement at maximum starter strength.
**Location:** Sunken Playhouse causeway, ~100 ft from proscenium pillar, marsh approach — Day 9, ~09:30. Six-person party halted; flute/drum/female-voice charm-resonant music ahead; Silka recognized the song. Senna's hold-fist up. Cookie's call pending.
**HP:** 60/60 | **AC:** 22 | **Proficiency:** +4 (L10 bump)
**Saves:** DEX +12, CHA +8, WIS −2 (prof +4)
**Skills:** Performance +10, Persuasion +10, Acrobatics +12, Deception +6 (prof +4 applied)
**Spells:** L1: 4/4, L2: 3/3 (long rest restored). Stunning Kicks 4/4, Healing Dance 4/4, Dispel 4/4, Planar Waltz 4/4, Dragon's Roar 4/4.
**Wealth:** 4 GP, 18 SP, 90 CP (Hazel split rounded up)
**Attunement (2/3):** Healer's Ring, Anklet of Unarmed Combat (silver-paste worn off — re-apply before next combat)
**Fame:** LOCAL SENSATION in Varenholm; Hazel volunteering to promote Cookie to upper-tier women's circuit; Calverton engagement declined Day 7 (Jareth lead burned)
**Last Updated:** Day 8 05:30 — L10 cap reached (Wererat fight Round 3 + Performance domain bonuses), long rest completed, BUZZED cleared, Ember frozen at current strength

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

### L9 Unlocks — Social / Behavioral Layer (Day 7 17:20)

These three perks bifurcate every Heartstring-touched humanoid by gender × disposition. They are the dominant social-mechanics layer from L9 forward — the DM must check them every scene that involves NPCs who have felt Heartstring.

- **Perk: The Great User (L9):**
  - **Female humanoid + felt Heartstring + disposition ≤ neutral** → antagonistic. Challenges Cookie to duels, betrays her in combat, actively tries to steal her friends and male admirers.
  - **Male humanoid + disposition ≥ neutral toward Cookie** → protective. Asks what she needs and buys it. **In combat, gains the option to intercept any attack aimed at Cookie — counts as an automatic critical hit on the intercepting NPC.**
- **Ember Enhancement: Fans Out of Control (L9, while Ember active):**
  - **Male humanoid + felt Heartstring + disposition < neutral** → stalker. Attempts kidnap or sleep-time impregnation.
  - **Female + felt Heartstring** → assassins. Show up to kill her.
  - **Male + disposition ≥ neutral + felt Heartstring** → secret guard network. Quietly watch over her location and pop up to fight when she's ambushed.
  - **Mechanical effect:** Cookie rolls for ambush even in safe locations during sleep, but always has at least one nearby protector who arrives to help fight.
- **Quirk: Low-Wisdom Loss-of-Control (L9):**
  - When alcohol or drugs are offered, Cookie must make a WIS save (DC varies by potency) to refuse.
  - On a failed save, the player loses control of Cookie for the duration.
  - If Cookie is drugged or blacked out from alcohol → an attempt scene fires:
    - Female aggressor → assassination attempt
    - Male aggressor → impregnation attempt
  - **Great User intervention:** any nearby Heartstring-touched friendly male humanoid can attempt to thwart the attempt.
  - If thwart fails → Cookie is treated as prone → **Ember prone effect**: female attackers gain ridicule bonus (mock instead of finishing); male attackers gain lust bonus (must succeed STR save vs Cookie's CHA-based DC to be stopped from succeeding).
  - **Tracking implication:** every "drink offered" scene is now a real WIS save, not flavor. DM must roll, not narrate around.

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
| become_famous_bard | Day 1 | ongoing | ACTIVE | Become a famous bard like Ignis. LOCAL SENSATION in Varenholm after 7 days. Starling show (Four Seasons of Love) — standing ovation, 200+ crowd. 3 return show slots offered. Torren booking patron inquiries. Isolde earring deal validated. Term 1 closed; Term 2 fieldwork (Halbert funeral) complete; accelerated graduation negotiated. |
| academy_term | Day 1 | Day 4 08:00 | COMPLETE | First class with Professor Ashworth. Dragon's Fire performance (22 vs DC 14). Fieldwork bounty assigned. |
| amphitheatre_spiders | Day 4 | Day 4 | COMPLETE | Burnt Amphitheatre spider infestation cleared. 3 Phase Spiders killed (all FATALITY by Fenella). 525 XP, 99 GP earned (50 spider parts + 49 quest bonus), 40 GP spent at enchanter. |
| outfit_pickup | Day 1 | Day 4 | COMPLETE | 4 luxury performance outfits picked up from The Gilded Thread. 5 total in wardrobe. |
| earring_pickup | Day 3 | Day 5 AM | COMPLETE | Custom enchanted earrings (+2 CHA, adv Persuasion & Performance) picked up from Isolde. Worn at Starling — advertising deal fulfilled. Equipped permanently. |
| starling_show | Day 1 | Day 5 EVE | COMPLETE | Four Seasons of Love — 4 songs, 4 outfits, all successful. Standing ovation from 200+. Leveled twice (5->7). 3 return slots offered. LOCAL SENSATION fame achieved. |
| bridge_troll | Day 5 | Day 5 | COMPLETE | Bridge troll quest with Davan, Aveline, Jessamine. Solved non-lethally via Performance nat 20 (40) + Heartstring + Ember Enhancement. Ogre now distributes pamphlets. Domain bonus pushed Cookie L5→L6. |
| academy_day6 | Day 4 | Day 6 08:00 | COMPLETE | Second class — Performance 32 vs DC 16 (success +16). Accelerated graduation negotiated (3 Persuasion checks, final nat 20 vs DC 22). Term 1 closed via Starling. Term 2 fieldwork: Halbert's funeral assigned. |
| funeral_fieldwork | Day 6 | Day 7 noon | COMPLETE | Term 2 fieldwork — Halbert's funeral. Visited widow Maret (Day 6), gathered personal details. Vocal Performance at the procession (23 vs DC 14, success +9). 7,250 XP. Need to report to Ashworth. |
| accelerated_graduation | Day 6 | Day 10 | ACTIVE | Negotiated with Ashworth Day 6. Halbert fieldwork complete; report at Day 10 office meeting. |
| starling_return_shows | Day 5 | Day 8+ | ACTIVE | 3 return show slots offered by Starling. Unbooked. |
| torren_patron_inquiries | Day 5 | Day 8+ | ACTIVE | Torren locked 3 patron inquiries after Starling. Unactioned. |
| guild_hire_posting | Day 7 | ongoing | ACTIVE | Updated registration L8 Dancer (support — healer/buffer/tank). Listed for hire at 5 GP/quest. Selwyn + Beldra of Greyrush iron crew approached Day 7 17:00 with a 2-day flooded-mill escort/pacification offer at posted rate. |
| wardbreaker_encounter | Day 7 16:00 | Day 7 ongoing | ACTIVE | The Wardbreakers (Senna, Finch, Varn, Thessaly) — Diamond-tier Vanguard Hall, cross-campaign from Kenji Books 2-4 — entered the guild while Cookie was at the counter. Senna recognized Cookie's Ember (25 yrs around AnkuNyx). Cookie sat next to Finch, flirted, then dropped: "You one of the ladies that bang my dad?" Senna replied "Once. A long time ago. Before he knew what he was. Finch is a grown man. Bang who you like, halfling. — But I want to hear you say it again. Slow. Who did you just call your father." Cookie deflected with public Ankuspawn admission + pivot to support-for-hire posting. Senna let her walk; Wardbreakers watching. |
| ankuspawn_public_outing | Day 7 17:00 | ongoing | ACTIVE | Cookie publicly identified herself as Ankuspawn in a full guild hall. Heard by full bar; one set of ears in the contracts alcove (scholar-robed, ledger-keeping) responded — believed to be a Cult of Anku informant. No immediate consequence; trail opens. |

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
- **Ch6** "Gold in the Morning" (Day 6): Ashworth's second Academy class — Performance 32 vs DC 16 (success +16). Accelerated graduation negotiated via 3 Persuasion checks (final nat 20 vs DC 22). Term 1 closed (Starling accepted as recital). Term 2 fieldwork: Halbert's funeral assigned. Visited widow Maret to gather personal details for the eulogy song. 21,500 XP. Level 7→8.
- **Ch7** "Daddy's Girl" (Day 7 afternoon): Halbert's funeral procession — vocal Performance 23 vs DC 14 (no dance — funeral context), 7,250 XP. Updated guild registration to L8 Dancer, hire rate 5 GP/quest. The Wardbreakers (Senna Dawnmere, Finch, Varn, Thessaly — Diamond-tier Vanguard Hall, cross-campaign from Kenji Books 2-4) entered the guild while Cookie was at the counter. Senna recognized Cookie's Ember from 25 years around AnkuNyx. Cookie sat next to Finch, flirted, then dropped: "You one of the ladies that bang my dad?" — implying AnkuNyx is her father. Chapter ends on cliffhanger: Senna's response pending.
- **Ch8** "Six Gold and a Stew" (Day 7 evening — Day 8 dawn): Senna replied "Once. A long time ago. Before he knew what he was. — But I want to hear you say it again. Slow." Cookie sighed, publicly outed herself as Ankuspawn to the entire guild, pivoted to support-for-hire (Persuasion DC 18 ADV 28 → 2,500 XP; Persuasion DC 15 ADV 25 → 1,500 XP). Cult-of-Anku scrivener filed her name, sealed grey-wax courier. Honey mead WIS save FAIL by 4 → BUZZED. Selwyn + Beldra declined cleanly (Hen & Hammer hook). Investigation DC 13 → 1,500 XP. Jareth's Calverton lead declined silently. Brass Whistle (Falconer/Tova/Mograth) joined for The Gilded Thread cellar wererat job — 4-way split, 1.5 GP each. **8 wererats cleared in 30 seconds.** Stunning Kicks teleport (8/8 hits, all stunned 2 rounds). Falconer 2 nat-20 crits Round 1. Round 3 Cookie kicked F1 → **first FATALITY** (bludgeoning paste, indigo silk shroud); kicked M1 → **second FATALITY** (paste-gore, brick crater). R2 fled, Falconer arrow + fall + Mograth coup-de-grace. Ankuspawn lycanthropy-immunity confirmed. 4 Performance domain successes = 30,000 XP + 720 combat. **LEVEL 8→10 (starter cap reached). EMBER ENHANCEMENT AT GROWTH CEILING.** Hazel paid 6 GP + lifetime 10% retail discount + voluntary upper-tier promotion. Walked home, Fern's stew, slept 21:00. Ambush check NAT 20 — quiet night. Long rest completed. Day 8 dawn 05:30. Total Ch8 XP: 36,220.
- **Ch9** "Daughters" (Day 8 morning — Day 9 mid-morning): Class with Ashworth — Performance 28 vs DC 14 longing-projection success, Heartstring landed cohort-wide, Silka rocked. Term 2 Halbert closed satisfactory. **Final fieldwork assigned: Sunken Playhouse 2-day expedition + Civic Auditorium recital** (Council attends, Vess attends, Ashenmere Bardic Master invited). Cookie accepted, signed parchment. Caught Silka in corridor, invited her on the trip — Silka accepted (under Lyssa's standing instruction + un-named sister-resonance pull). Hired the Wardbreakers at Senna's Bronze rate gift — 12 GP for 3 days + paternity-question term locked (deadline = before return). Prep: bursar 15 GP, Gilded Thread NEW green outfit (6.3 SP after Hazel discount), Pale Lantern (Isolde threw in dried Ember-reactive herb 'for the ruin'), General store, home/Fern. South gate noon, six-person party (Cookie + Silka + Senna + Finch + Varn + Thessaly). Marshmouth Inn arrival sunset. Senna deferred paternity question to trip. **Cookie's WIS-7 stunt at 00:15:** lingerie, pressed against Finch in his bedroll, milk-flask prank at 00:25 (Performance 19 vs DC 18 by 1 — sold as halfling clown-pose). Senna walked over at 00:30, read it correctly, laid heat on Finch, sent Cookie back to her own bedroll. Finch wears the heat through this expedition. Silka's sister-resonance pain compounded silently. Ambush NAT 20 = quiet night. Long rest completed. Day 9 dawn breakfast in heavy silence. Marsh approach. ~09:30 Thessaly's crystal lit continuous gold; proscenium peak visible 200 yards south. Cookie picked **west causeway approach** (fast, expected). Silver-paste reapplied. 100 ft in around a stone pillar — **flute/drum/woman's voice charm-resonant music**, Silka knew the song (didn't say so), Thessaly's crystal red-shot ("College of Glamour signature, target-locked"). Frogs gone silent. **Chapter cliffhanger — first defensive layer of the Sunken Playhouse engaged.** XP at L10 cap; tracking deferred until campaign promoted to standard.

---

## HOLLY — Snow Elf escapee, Master Toymaker's former conscript

**Status:** alive | healthy | **freedom-run Day 1** (escaped North Pole workshop ~3 weeks ago, just walked off the cargo cog *Witherhold* in Solandra Bay this morning)
**Level:** 297 (Legendary Artificer — Master Toymaker subclass) | **POWER-OVERRIDE FLAGGED** (factor 1398.38×, currently in honeymoon phase, ~17h remaining)
**Location:** Solandra Bay — Pier Three, dawn, mango vendor stall (Mama Po) on the dock
**HP:** 3864/3864 | **AC:** 30 | **Proficiency:** +12
**Stats (base):** STR 31, DEX 44, CON 27, INT 99, WIS 78, CHA 60, **LUCK 100** (snow-elf 7th ability — +45 to all d20 rolls)
**Saves:** STR +55, DEX +62, CON +65, INT +101, WIS +79, CHA +70 (Luck +45 added to all)
**Skills:** Arcana +101, Investigation +101, History +101, Perception +91, Sleight of Hand +74, Insight +79, Persuasion +70, Performance +70
**Spells:** Artificer extended slots (1st-9th, scaled to L297). Spell save DC 64. Spell attack +56.
**Wealth:** 0 GP cash | ~250,000 GP equivalent in raw materials in unlimited pouch (mithril, adamantine, dragon-bone, snowflake-quartz). Liquidating any sizable amount draws Council customs attention.
**Attunement:** Toymaker's Workshop Apron (mithril-thread inner lining, +3 AC, never gets dirty) | Cyan snowflake pendant (snowflake-quartz, low-light glows, cold-damage focus) | Three uninstalled construct cores (palm-sized, in pouch, dormant — stolen on the way out)
**Fame:** Unknown — first day in any city. Snow elf is a rarity on the southern coast. Will build fast given CHA 60 + Luck +45.
**Last Updated:** Day 1 hour 7 — Mama Po introduction, fixed wobbly stool with Sudden Insight, identified rigged fishmonger scale.

**Physical:** Petite snow elf — short white hair, pale blue eyes, pointed ears, palm-sized snowflake markings tattooed across right shoulder/back/right thigh (the Master Toymaker workshop's quiet brand — unique pattern per conscript).
**Wears:** Red workshop dress (sleeveless, cinched), black wool santa-style hat with white fur trim and a luminous-cyan snowflake pendant dangling from the tip, black leather satchel cross-strap, no shoes.
**Demeanor:** Carefree-curious. Will stop mid-sentence to take apart a mango. Wide-eyed attentiveness of someone who has read about humans for centuries and is now meeting them for the first time.
**Morale Compass:** Neutral (Player Character — Hiro's call)

### Signature Abilities — Power of Creation (patron-gifted by the Master Toymaker)

- **Sudden Insight (passive, always on):** Free-action visual examination of any machine. Treats any non-divine, non-eldritch device as if she had spent weeks studying it. Combat: identify construct vulnerabilities + off-switches. Social: read rigged scales, picked locks, missing badges. Exploration: any door/vault/trap is read on sight.
- **Workshop Mode (Craft Anything, active, unlimited use):** Action to begin. 10 min (lockpick, music box) → 6 hr (CR-5 toy soldier construct). Materials from pouch. Constructs scale to her INT mod (44). Theme-locked: cannot craft assassination devices, charm-machines, necromancy.
- **Endless Possibilities Surge (active, 10 Luck per use, regen 1/hr):** Bonus action narrative-reroll. Spend 10 Luck to rewrite a single ambient detail in her favor — coincidences, fortuitous arrivals, lucky finds. Cannot resurrect, damage, or override sentient choice.
- **Unlimited Inventory Pouch:** Free-action pull-from-pouch. Bag of holding++. Cannot store living creatures, food, or sentient constructs.

### Quirks (Rule 12 + Rule 13 active)

- **High-stat quirks (Rule 13, all 6 stats above 20, all unjustified by class buff):** STR 31 "All hands, no leverage" (drops to 19 on full-body braced effort). DEX 44 "Unfamiliar terrain" (drops to 19 on cobblestones/sand/wet/tile). CON 27 "Snow-elf biology vs heat" (drops to 19 above 75°F, to 14 above 85°F). INT 99 "Library catalog, no muscle memory" (drops to 19 on real-world social/practical applications). WIS 78 "Carefree-curious distractibility" (drops to 19 when something interesting catches her eye). CHA 60 "Charm without technique" (drops to 19 on first-meeting interactions).

### Threat Clocks

- **Master Toymaker's awareness (rate +5/hour pre-discovery, +15/hour after):** Master discovers absence by Pole-time hour 8. Reaches 100 around Day 7-8 — Master arrival window opens (existential threat).
- **Frostmaster pursuit (CR 8 lieutenant, dispatched Day 1 hour 24):** Arrives Day 2 hour 18. The "pest" in the Cobalt Fountains Quarter is the early telegraph.
- **Council customs flagging (rate +4/hour):** Harbor Master Tezo cross-references the Witherhold manifest. Summons by Day 2 morning.

### Chapter Pointer

- **Ch1** "[OPEN — Day 1 dawn, Solandra Bay]" PENDING — Mama Po introduction, stool fix, rigged-scale read. Three options on the board.

---

## SHEN SAMA — Ankuspawn True Dragon (Vorathiel + Kenji's son)

**Status:** alive | healthy | **first Ankuspawn True Dragon ever recorded** | base 72 / L1 (meets cap), CHA 4 quirk active
**Level:** 1 (Legendary Hero — Monk/Barbarian — Ankuspawn True Dragon) | **EMBER ACTIVE** (10× racial multiplier on STR + CON via dragon affinity)
**Location:** Foothill pine forest, ~16 miles south of Dragonspine pass, Highford's south road. **In dragon form** as of Day 3 hour 14 — Marshal B fatality just executed, dragon-form charge expended (0/1, 24h CD).
**HP:** 137/137 (Ember active) | **AC:** 135 (Barbarian Unarmored Defense: 10 + DEX 0 + CON 125) | **Proficiency:** +2
**Stats (base):** STR 18, DEX 10, CON 20, INT 10, WIS 10, **CHA 4** (Rule 12 quirk active — "Off-Putting" + manual "Charisma Flaw (Mountain-Raised Monster)")
**Stats (Ember-active, dragon-affinity bonus +240 to STR + CON only):** STR 258 (+124), DEX 10 (0), CON 260 (+125), INT 10 (0), WIS 10 (0), CHA 4 (-3, dragon bonus does NOT apply to CHA)
**Saves:** STR +126 (prof), CON +127 (prof), DEX/INT/WIS +0/+0/+0, **CHA -3** (primary vulnerability)
**Skills:** Athletics +126 (prof), Intimidation +2 (CHA -3 + Dragon Presence +5), Survival +2, Acrobatics +2, Perception +2
**Wealth:** 0 GP, 0 SP, 0 CP — left Vorathiel's ledge with nothing but monk pants and the tattoo on his chest.
**Fame:** **CONFIRMED DRAGON-TIER HOSTILE** across Highford county and the southern foothill belt. Council Mage-Hunter writ accelerated to Lord-level by Day 4 afternoon.
**Last Updated:** Day 3 hour 14 — Dragon Form bite-pluck on Marshal B (FATALITY HP -124, body destroyed). Vorathiel pursuit clock 6 → 60. Cult of Anku 25 → 60.

**Physical:** Looks 24 years old, fully developed adult human form. Black dragon-tattoo across chest + left arm — pulses with green-fire when Ember active; identifies him as Vorathiel-line dragon to anyone who knows the markings.
**Wears:** Monk-style trousers (rough-spun, mountain-grade — all he owns). Bare feet (calluses count as natural sole armor on rough terrain).
**Demeanor:** Quiet. Watches before he speaks. Twenty-four years on a Dragonspine ledge means he reads humans like a child reads picture books — concept-by-concept, no fluency.
**Morale Compass:** Neutral (Player Character — Hiro's call)

### Signature Abilities — Body Enhancement + Damage Reflection (Ember inheritance)

- **Green-Fire Reflection Aura (passive, Ember active):** Melee attackers take 50% of damage dealt back as green dragon-fire. Doubles to 100% when raging.
- **Body Enhancement (passive, Ember active):** STR/CON saves auto-pass non-magical. Unarmed/claw damage doubles. +2 AC from green-fire shield.
- **Body Enhancement Surge (active, 4/day):** Bonus action 1-min burst. Claw damage doubles AGAIN. STR/DEX/CON saves auto-pass even magical. +2 AC stacks.
- **Dragon Claws:** Free-action retract/extend, both hands independent. Damage Nd8 + STR per strike (L1: 1d8+124 = 125-132 per claw).
- **Green-Fire Breath (4/day):** 30-ft cone, 2d6 fire, DEX DC 13 save half. Scales with level.
- **Dragon Form Transformation (1/day, 24h CD):** Action to transform into adult black dragon. Flight (1000 ft/round at L1). Unlimited breath. 4× HP. Civilizations log him as monster permanently. **Currently spent — earliest re-use Day 4 hour 14.**
- **Rage (Barbarian, 2/day at L1):** +2 STR-melee damage, B/P/S resistance, Reflection doubles to 100%.

### Quirks

- **Charisma Flaw + Rule 12 "Off-Putting" (CHA 4, severe):** Civilized authorities default to suspicion or hostility. Persuasion DC raised by +5 in any settlement on first contact. Persuasion DC 18 to avoid attack-on-sight first entry to any town — with CHA -3 his max possible roll is 17. Cannot pass without external help.

### Threat Clocks

- **Vorathiel's pursuit (60%, +20/hour):** Earliest physical intercept Day 4 dawn. Cannot be defeated at L1.
- **Civilization first-contact (FIRED — DRAGON-TIER HOSTILE, 100%):** Sergeant + courier (Calden) eyewitness to transformation; Marshal B fatality; farmstead bells.
- **Cult of Anku (60%, +8/day):** First Ember-Shade ward-bearer dispatched from Stormhaven, ETA Day 6.

### Chapter Pointer

- **Ch1** "Stand Down" COMPLETE — patrol intercept, Marshal A fatality under post-stand-down truce-break.
- **Ch2** in progress (Day 3 hour 14) — Marshal B pursuit-kill via Dragon Form. Three paths queued: climb-and-fly to Varenholm / land-and-walk south / burn the chimney farmstead.

### Cross-Character

- **Father:** Kenji (NPC entry below) — never met. Kenji not informed of Shen's birth.
- **Mother:** Vorathiel (Dragon God Queen, Dragonspine peaks) — raised him; now hunting him.
- **Half-sister:** Ignis (NPC entry below) — never met, knows by reputation only. Model he's chasing.
- **Half-sister:** Cookie — does NOT yet know she exists. Major story beat if Shen reaches Varenholm.

---

## AMARIS — Eastern frontier (campaign complete, epilogue)

**Status:** alive | retired | **campaign closed** (Eastern Frontier — Thornfield/Greenveil/Briarstone arc resolved)
**Level:** 5 (Sorcerer)
**Location:** Briarstone Homestead — porch (Day 8 hour 9, clear weather)
**HP:** 28/28 | **AC:** 12 | **Proficiency:** +3
**Last Updated:** Day 8 hour 9 — campaign epilogue; Vareth/Nexus arc resolved off-camera, no civilian casualties.

**Demeanor:** Settled, post-adventure. Local hero in the eastern frontier; kingdom-wide identity is "Mysterious hero — details contradictory in village gossip." Doesn't seek fame.
**Morale Compass:** Neutral (former PC — completed)

### Signature Abilities (recorded for cross-campaign NPC use)

- Sorcerer kit, eastern-frontier flavored. Spell slots 1st-3rd available. Specific spell list lives in `amaris_state.json` and `amaris_story.md`.
- Local familiarity with Greenveil + Briarstone — knows back roads, local merchants, safe houses.

### Cross-Character Relevance

- If Holly travels east from Solandra (~3 weeks) she could hear of "the mysterious hero." Amaris herself avoids attention; word-of-mouth rumors are her public face.
- If any other PC needs an eastern-frontier safe house, Briarstone Homestead is canonically a refuge — Amaris will host but won't fight.

---

## KENJI — The Dragon Emperor (campaign ongoing — Book 4 Ch43 OPEN)

**Status:** alive | **APOTHEOSIS** | **Book 4 Ch42 COMPLETE, Ch43 OPEN**
**Level:** 40 (post-Iron Crown War, post-Fraying Empire)
**Location:** Ashmere 69 dawn — Dragonspine peaks, granite shelf near Ignis mating ground (off beaten path) — Day 291 hour 6
**Morale Compass:** Neutral (former PC — Hiro's character, currently dormant)

### Signature Style + Reputation

- Unified the continent. Kingdom of Ankunyx declared. All 5 existential threats resolved.
- 25 bonded lovers in the Soul Nexus.
- Disappears for months or years at a time. Most often in the Deepwood with the three elf sisters — currently on the Dragonspine peaks near Ignis's mating ground.
- **Public face:** Legend more than a man. Wedding rumors, succession rumors, dragon-flight sightings.
- **Combat signature:** Dragon-tier melee, soulbound weapons, full battlefield-shaping kit. At L40 Apotheosis, effectively unkillable by mortal means.

### DM Secrets (cross-character continuity)

- **Cookie's biological father** (Bane of Eve encounter with Daisy 22 years ago). Cookie does NOT know.
- **Shen Sama's father** (egg-child from Kenji's pregnancy with Vorathiel). Has never met Shen.
- **Ignis's father** (red dragon daughter — separate from Vorathiel). Ignis is "The Firebird," Cookie's idol.
- **The Ousaki — three half-elf Ankuspawn with the elf sisters in the Deepwood.** Young adults (18-25). Cult of Anku highest-value targets if they ever leave the forest.

### Chapter Pointer

- **Book 4 Ch42** "The Weld" COMPLETE (`fraying_empire_chapter_42.md`).
- **Book 4 Ch43** OPEN — Ashmere 69, Day 291 dawn.

### Cross-Character Relevance

- **Cookie:** Background presence. Tavern gossip. Will not appear in Cookie's campaign unless world-shaking. If ever met: paternity reveal.
- **Shen:** Father (unknown). If Shen reaches Varenholm or the Hearthstead, Kenji's tracker may register the Ankuspawn. Likely route: Cookie meets Ignis → Ignis recognizes another Ankuspawn → trail to Shen → Kenji investigates.
- **Holly:** Background lore (Iron Crown War 25 years ago). Holly knows the legend from books. Won't cross paths unless Holly's escape brings her into the heartland.
- **Amaris:** Kenji's eastern-frontier reputation is post-war canon. Amaris would recognize the name without having met him.

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
| **Halbert** | (deceased) | 6/7 | Funeral subject (Term 2 fieldwork) | dead | Local figure. Funeral procession Day 7. Cookie performed vocal eulogy (Performance 23 vs DC 14). Personal details gathered from widow Maret. |
| **Maret** | NG | 6 | Halbert's widow | MIA | Visited Day 6 to gather personal details for the funeral song. Provided memories Cookie wove into the eulogy. Returns if Halbert's death threads back into civic story. |
| **Senna Dawnmere** | CG | 7 | **Wardbreaker** — Diamond-tier (cross-campaign, Kenji Books 2-4) | active | Former Wardbreakers leader. Fighter / Azarinth Healer. Late 40s, looks mid-20s (Azarinth regen halts aging). Slept with AnkuNyx once "before he knew what he was." Recognized Cookie's Ember instantly. INT 18, LOW WIS (Heartstring DC 12 — failed save Ch7), LOW CHA. Currently letting Cookie play out the room without intercepting. Watching how she lands. |
| **Finch** | CN | 7 | **Wardbreaker** — halfling rogue (cross-campaign) | active | Sandy-brown hair, throwing knives. Jokes-as-deflection. Cookie sat next to him and flirted — failed CHA contest (17 vs 18) means his usual halfling-rogue patter cracked. No clean comeback. Has not put his beer down since. |
| **Varn** | LN | 7 | **Wardbreaker** — half-orc fighter (cross-campaign) | active | Greatshield, devoted to Senna, speaks in single sentences. MALE → Combat Magnetism affects him. WIS 10 vs DC 12 — restraint slipping but not broken. Watching, not advancing. |
| **Thessaly** | LN | 7 | **Wardbreaker** — human arcanist (cross-campaign) | active | Crystal-focus arcanist. Sarcastic, formal-magic snob. Crystal pulsed three times reading Cookie's Ember — Arcana 13 vs 15, knows it's *something* but cannot yet classify. Watching Senna for cues. |
| **Selwyn** | LG | 8 | Greyrush iron crew leader, ranger | active | Late twenties, longbow, leathers patched at the elbows. Approached Cookie at the corner table Day 7 17:00. Iron-tier crew (4 heads) banged up from a Sunwell granary breach contract. Has a 2-day follow-up: flooded mill east of town, escort + pacification, "one wight rumor we're discounting." Hat off, businesslike. Ears went pink at 30 ft of Heartstring. |
| **Beldra** | LN | 8 | Greyrush crew, dwarf fighter | active | Mid-40s, axe at hip, left forearm bandaged. Carried the contract sleeve. Female, immune to Heartstring sway via standards. Wants the deal closed in six minutes. Offered axe-edge regrind as side-payment. |
| **Scholar-robed scrivener** | (unknown) | 8 | Contracts-alcove informant | active | NO NAME — caught the word "Ankuspawn" at the threshold of comprehension (eavesdrop DC 12 hit by 0). Wrote four small letters in the margin of an otherwise empty ledger page, blew the ink, closed the book, and went back to writing. Did not look up. **Suspected Cult of Anku informant.** Filed; no immediate action. |
| **Jareth** | LN | 8 | Guild runner, Varenholm noble salon circuit | active | Mid-30s, charcoal cutaway coat, hair silvering at temples. Approached Cookie at the contract board (Pretty-Privilege crowd assist DC 12, rolled 20). Offered the Calverton engagement-party lead — 12 GP + tips, 18:30–20:30 Day 7, school-compatible curfew. Felt Heartstring (voice went a quarter-step higher). **Great User: protective.** **CALVERTON LEAD DECLINED Day 7 — Cookie skipped, Jareth's hook burned for that night.** Books out of the noble district; future leads still possible. |
| **Falconer** | LG | 8 | Brass Whistle ranger / urban tracker | active | Human, mid-30s, longbow, silver-tipped broadheads. Heartstring-touched (voice rose, ears pinked). **Great User: protective** active. Two NAT 20 crit kills on R3 + R4 in the wererat fight Round 1. Books at the guild board mornings. Offered to walk Cookie home (Cookie declined). Posts under "Brass Whistle." |
| **Tova** | LN | 8 | Brass Whistle dwarf fighter | active | Mid-60s, axe + shield, iron-grey braid. Standards-immune to Heartstring sway (like Beldra). Crit on M2 in Round 1; missed all swings Round 3 (took it personally). Honest broker on splits. Confirmed F2 + R1 with axe-pommel post-combat. |
| **Mograth** | LN | 8 | Brass Whistle orc brawler | active | Mid-30s, silver-shod cudgel, anti-grapple specialist. **Great User: protective** active. Killed M1 (Round 1) and M2 (Round 2), confirmed R2 with cudgel-tap post-combat. Two-word vocabulary in combat. |
| **Hazel** | NG | 8 | Halfling proprietress, The Gilded Thread | active | Mid-50s, silvered curls, more pearls than three nobles. Heartstring-touched, friendly disposition (no Great User antagonism). Pulled out of contract: 6 GP plus permanent 10% Gilded Thread retail discount + free first-fitting on any future commission. Volunteered to promote Cookie to Lady Calverton's tier of upper-class women — said names will be on Torren's books by Day 8 lunch. Force-multiplier for the bardic career on her own initiative. |

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
**Phase 1** (L1-3): Cookie's first booked performance gets cancelled. "Someone told me not to book new acts without clearance." First hint of Lyssa's network. *(Skipped — Cookie bypassed this by going through Torren and the Starling directly.)*
**Phase 2** (L4-6): Cookie becomes known. Lyssa notices. Practice room trashed. Note: "The heartland has enough bards." *(Triggers due via Silka's pending report — Day 8 deadline. Cookie now L8, deep in the Phase 3 band; Phase 2 should fire ASAP if it's going to fire as written.)*
**Phase 3** (L7-9): Escalation. Fern charmed and turned. Cookie discovers the Sunken Playhouse and the Resonance Chamber. Young bronze dragon recognizes her Ember. *(Cookie is L8 — IN THIS BAND. Public Ankuspawn admission Day 7 17:00 + Cult-of-Anku scrivener notation = the antagonist supply chain just got direct evidence.)*
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
