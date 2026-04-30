# SESSION MEMORY — AI Persistent Notes

**Purpose:** This file is updated by the AI throughout each session to preserve context that would be lost during chat compaction. Read this file at the start of every session and after any compaction event.

**Last updated:** 2026-04-30, Ch8 wererat fight cleared + L10 cap reached + Ember frozen + new Death/Fatality rules live

---

## ACTIVE STATE

- **Current character:** Cookie
- **Current chapter:** Ch8 IN PROGRESS (Day 8 dawn — wererat fight cleared, Calverton declined, long rest at Millward Chandlery, Academy class at 08:00)
- **Day / hour:** Day 8 / ~05:30
- **Level:** **10 — STARTER CAP REACHED.** Mechanical progression cap. Ember Enhancement frozen at maximum starter strength.
- **XP:** 131,768 / 130,000 (cap +1,768)
- **HP:** 60/60 (L10 +5 d8+0 CON)
- **Status:** healthy. EMBER_CAPPED (no further Ember growth until story trigger — Resonance Chamber, Ignis encounter, Cult-of-Anku contact, or campaign-defined unlock). Existing 10× buff/heal multiplier and L9 social mechanics remain active.
- **Fame:** LOCAL SENSATION in Varenholm
- **Gold:** 3 GP | 8 SP | 90 CP (mead at corner table on the house — Pretty Privilege)
- **Location:** Adventurer's Guild, Varenholm — corner table, mead in hand
- **Next events:** Academy next class (Day 8, 08:00), Ashworth meeting (Day 10, 10:00), Starling return shows (unbooked), Torren's patron inquiries (pending)
- **Active goals:** become_famous_bard (ongoing), guild_hire_posting (5 GP/quest, Calverton lead live), wardbreaker_encounter (still FIRES_NOW — Senna at the bar watching), ankuspawn_public_outing (scrivener filed, no immediate action)
- **Key open beats (Ch8):**
  1. **Contract choice on the table:** A) Alderman→Isolde courier 5 SP 30min, B) Scriptorium witness 2 GP 1hr, C) Undertaker eve service 3 GP 1hr, D) Calverton engagement (Jareth lead) 12 GP + Pretty-Privilege tips 2hr. C and D conflict. A or B before D is tight-but-possible.
  2. **Mead at table half-full.** Another draw triggers WIS save at disadvantage. Possible blackout = Low-Wisdom-Loss-of-Control quirk fires (assassination/impregnation attempt scene).
  3. **Senna still at the bar.** wardbreaker_encounter goal still firing. Walking past her is itself a narrative choice.
  4. **Selwyn+Beldra dismissed cleanly.** Hen & Hammer hook open (Beldra evenings).
  5. **Jareth (NEW NPC):** guild runner, noble salon circuit. Felt Heartstring → **Great User: protective.** That's why he volunteered the curfew/V.E.A.-stamp detail unprompted.

## PENDING TASKS

- **Add chapter-file gate to chapter_close.py** — refuse to close a chapter unless the prose file exists on disk. User requested this after discovering Ch1-3 were never saved.
- **Campaign arc name** — Cookie's campaign has no arc name yet (Kenji has "Fraying Empire", etc.). Chapters are currently named `cookie_chapter_XX.md`. Ask user or decide on one.

## SESSION HISTORY — Key Decisions

### 2026-04-28 Session
1. **CombatNarrationError** added to ttrpg_game_engine.py — `last_narrated_round` field + code-level guard that throws if rounds aren't narrated sequentially. Prevents the Round 2 skip bug.
2. **TrackerSync** added to ttrpg_game_engine.py — `character_tracker.md` is single source of truth, JSON pulls from markdown programmatically via `sync_tracker_to_json()`.
3. **Combat replay** — 3 Phase Spiders at Burnt Amphitheatre, all FATALITY by Fenella with Protector's Surge (+40 all stats). Healing Dance completed.
4. **Post-combat economy** — 50 GP spider parts + 49 GP quest bonus = 99 GP earned. 40 GP spent at enchanter (Healer's Ring + Anklet of Unarmed Combat). 59 GP remaining → updated to 62 GP after recalc.
5. **New items:** Healer's Ring (temp HP = target's max HP on heal, aggro redirect 1 turn), Anklet of Unarmed Combat (+4 DEX, kicks 6d8+DEX as weapons).
6. **Stats changed:** DEX 3→7, AC 18→22, kick +9/6d8+7.
7. **Edit tool truncation bug** — NEVER use Edit tool on ttrpg_game_engine.py. Always use standalone Python patch scripts. File was truncated and had to be restored from git.
8. **Mount path aliasing** — `cp` between different mount paths that point to the same Windows file zeros the file. Use file tools (Read/Write) or work within a single mount.
9. **Chapter files reconstructed** — Ch1-3 never had prose files. Rebuilt collaboratively with user from tracker summaries + user memory:
   - Ch1 "First Night in Varenholm": Kitchen scene with Daisy (21st birthday, birth control request, Tomas intervenes), cart with Fern (8 copper), Varenholm arrival, Academy enrollment, V.E.A. stamp, bought 4 outfits (white/black/red/blue), Gilt Lily scene (married merchant blocked by wife, soldier lost nerve, Torren approached — WIS fail by 9), walked Torren home, smile on the steps.
   - Ch2 "The Indigo Hustle": Fern makeover (pillows/fruit/makeup), Torren's shop (beauty line pitch 1 GP/week, Fern hired as model/employee), dressing room seduction (indigo dress, 30-second grinding dance), Torren agrees to invite 50+ upper class to Starling show, guild signup (dancer/buffer/support), 1 GP per head loophole → recruited 30 adventurers, bandit camp raid, Tai Chi born (started dancing and kicking mid-fight, 6 Performance rolls), party formed (Dorith/Dalla/Silas/Marta/Garron).
   - Ch3 "Golden Returns": Survey Stones quest, Marta tracked cart ruts to Castor's farm, Cookie talked to Castor alone — he explained why he stole stones, she promised to advocate. Turned in quest to Alderman Edric, Pretty Privilege (6 SP → 6 GP), Cookie tried to persuade leniency for Castor — failed. Castor fined 2 GP + 30 days labor. Isolde deal at Pale Lantern: 85 GP earrings for 4 GP + Starling advertising.

### 2026-04-30 Session (Ch8 wererat fight + L10 cap + new rules + long rest)
1. **Wererat contract (F) accepted at the Adventurer's Guild.** 6 GP, daylight only, half-day, The Gilded Thread (Hazel's shop) cellar. 4-way split with Brass Whistle silver-tier crew (Falconer / Tova / Mograth) — Cookie's share 1.5 GP + permanent 10% Gilded Thread retail discount + free first-fitting privilege.
2. **8 wererats engaged, 8 dispatched.** Cookie opened with Stunning Kicks (1/4 daily) — 8/8 hits, all stunned 2 rounds, grapple broken by teleport. Falconer 2 NAT 20 crits Round 1. Tai Chi kick on F1 → first FATALITY under new rule (bludgeoning paste, indigo silk shroud). Tai Chi kick on M1 → second FATALITY (paste-gore brick crater). R2 saved stun Round 4, fled, killed by Falconer arrow + fall + Mograth coup-de-grace.
3. **DEATH / CRITICAL INJURY / FATALITY rule codified** during fight (CRITICAL RULE #13). 2-round dying window, 1 HP critically-injured cap, -10 fatality threshold, undead exemption, mandatory thematic narration table.
4. **Engine + gamemode patched** via `outputs/patch_death_fatality.py` standalone script per rule #1. Adds Combatant fields (dying, dying_rounds_remaining, critically_injured, fatality, fatality_damage_type, is_undead) + helper methods (heal_from_dying, tick_dying_round, clear_critically_injured) + gamemode `_check_combat_end` PC_DYING return code. Engine syntax: clean. Gamemode syntax error in bash mount = OneDrive sync stale-mount footgun (Windows-side grep confirmed all patches landed correctly).
5. **L9 → L10 LEVEL UP.** 4 Performance domain successes during combat (start-of-turn + end-of-turn Tai Chi rolls Rounds 2 + 3) = 30,000 XP. + 720 combat XP base. Total: 30,720 XP this combat. Cookie at 131,768 / 130,000.
6. **EMBER CAP codified** (CRITICAL RULE #14). Story-trigger gate, not mechanical level gate.
7. **Calverton engagement DECLINED.** 12 GP + tips lead from Jareth burned for Day 7. Future bookings still possible via Jareth + Hazel-volunteered upper-tier women's circuit promotion.
8. **Ankuspawn lycanthropy immunity confirmed.** Cookie failed CON DC 11 vs F2 bite, but supernatural-resilience trait rejected the curse imprint. House rule pinned.
9. **Cookie went home to Millward Chandlery, ate Fern's stew, slept.** Ambush check NAT 20 — quiet night, long rest completed. Day 8 dawn 05:30, ready for 08:00 Academy class.
10. **NPCs added to extras:** Falconer, Tova, Mograth, Hazel. All marked used in npc_name_bank.

### 2026-04-30 Session (Ch8 mid-scene continuation + L9)
1. **Mead WIS save (DC 12):** rolled nat 1, Halfling Luck rerolled to 10 (raw) − 2 = 8. **Failed by 4 — BUZZED.** Heartstring DC 12→13. Next alcohol draw rolls at disadvantage.
2. **Selwyn + Beldra dismissed cleanly.** Cookie set the mead down, half-shake, no words. Beldra elbowed Selwyn before he could counter-offer (Heartstring almost cracked his LG). Hook open: Hen & Hammer, Beldra evenings.
3. **Crossed to contract board buzzed.** Investigation DC 13 success (rolled 17, +1,500 XP) — three same-day options visible. Crowd / Pretty-Privilege check 20 vs DC 12 — Jareth (new NPC, guild runner) approached with the Calverton engagement-party lead.
4. **LEVEL 8→9 at 100,000 XP threshold.** HP 50→55. Three new perks codified: The Great User, Fans Out of Control (Ember enhancement), Low-Wisdom Loss-of-Control quirk.
5. **Persisted to JSON:** `_story_engine_state` level/exp/hp/max_hp/exp_to_next_level updated; status += BUZZED; `mechanical_state` level/hp updated; three new class_features entries added.
6. **Tracker reconciled to L9 / Day 7 17:20 / Ch8 in progress.** Jareth added to EXTRA NPCs. npc_name_bank: Jareth marked used.
7. **Open contract decision:** A (Alderman courier 5 SP), B (Scriptorium 2 GP), C (Undertaker 3 GP), D (Calverton 12 GP + tips). C/D conflict; A or B + D is stackable.

### 2026-04-30 Session (Ch8 opening + tracker reconciliation)
1. **Ch8 opened** on the Wardbreaker cliffhanger. Senna replied "Once. A long time ago. Before he knew what he was. — But I want to hear you say it again. Slow." Cookie sighed, publicly admitted Ankuspawn, pivoted to support-for-hire. Persuasion DC 18 ADV (28) and DC 15 ADV (25) both succeeded. 4,000 in-chat XP. Time 16:25 → 17:00.
2. **Selwyn + Beldra introduced** (Greyrush iron crew). Pulled from npc_name_bank, marked used. 5 GP / 2-day flooded-mill escort offer pending Cookie's yes/no.
3. **Cult of Anku scrivener** in the contracts alcove caught "Ankuspawn" on knife-edge eavesdrop (DC 12 hit by 0). Wrote four letters in a margin and went back to writing. Filed as suspected informant. No immediate action.
4. **WIS 7 + mead** — first sip not yet taken; blackout-risk window flagged for player.
5. **Domain-bonus rule clarified** (see CRITICAL RULES #9). Engine math checked: Persuasion does NOT trigger performer-domain bonus. Performance does, and it's 25% of full level-threshold gap (+6,250 at L8). Past in-chat over-award of 1,113 corrected within session — saved JSON unaffected.
6. **Tracker drift fixed.** `character_tracker.md` was at L7 / Day 5 / Ch5 close. Reconciled to L8 / Day 7 17:00 / Ch7 COMPLETE / Ch8 in progress. Added Ch6, Ch7, Ch8 to Chapter Log. Added Senna, Finch, Varn, Thessaly, Halbert, Maret, Selwyn, Beldra, scholar-scrivener to EXTRA NPCs table. Refreshed Active Goals. Updated Lyssa Phase annotations for L8.
7. **Pending writeback:** in-scene XP/time advance + new NPC stubs in `extra_npcs` will persist at Ch8 close via standard chapter-close flow. Saved JSON is currently still pinned at Ch7 close (95,548 EXP, 16:25, no Selwyn/Beldra/scrivener rows) — that's expected, not a bug.

### 2026-04-29 Session (Ch5-Ch7)
1. **Domain bonus system deployed** — `patch_domain_bonus.py` created and applied to ttrpg_game_engine.py. Performance checks now award domain XP as percentage of level gap (25% of exp_to_next_level).
2. **STARTER_THRESHOLDS** — New XP threshold table for starter campaigns (L1-10). Different from main campaign thresholds. Added to engine.
3. **campaign_type: "starter"** — Added to Cookie's `character_world_state.json`. Engine uses this to select correct XP thresholds.
4. **Goal alert system deployed** — Goals tracked in character_world_state.json with due_day/due_time. System alerts when goals approach deadlines.
5. **Ch5 "The Four Seasons of Love" COMPLETE** — Day 5 morning to night, long rest to Day 6.
   - Level 5→7 (two level-ups from domain bonus XP during Performance checks)
   - XP: 36,048 → 66,798 (30,750 earned)
   - HP: 35→45 (d8 hit die, CON mod 0, +5 per level)
   - Chorus of One: 5 uses/day (scaled at L6, up from 3)
   - Bridge troll quest: solved non-lethally via Performance (nat 20, 40 total) + Persuasion. Ogre seduced, now pamphlet distributor.
   - Party: Davan (greatsword), Aveline (archer), Jessamine (druid) — all from npc_name_bank.md
   - Starling show: Four Seasons of Love — 4 songs, 4 outfits, 4 emotions, all successful
   - Standing ovation, 200+ crowd, LOCAL SENSATION fame in Varenholm
   - Starling management comped food/drink, offered 3 return show slots
   - Torren locked 3 patron inquiries
   - Isolde watched from back — earring deal validated
   - Gold: stayed ~3 GP 95 CP (bridge payout pending, food/drink comped)
6. **Ch6 "Gold in the Morning" COMPLETE** — Day 6. Ashworth class (Performance 32 vs DC 16). Accelerated graduation negotiated (3 Persuasion checks, final nat 20 DC 22). Term 1 closed via Starling. Term 2 fieldwork: Halbert's funeral assigned. Visited widow Maret. Level 7→8. 21,500 XP.
7. **Ch7 "Daddy's Girl" COMPLETE** — Day 7 afternoon only. Halbert's funeral (vocal Performance 23 vs DC 14, 7,250 XP). Guild registration updated to L8 Dancer, hire rate 5 GP/quest. Wardbreakers (Senna, Finch, Varn, Thessaly — Diamond-tier, cross-campaign from Kenji Books 2-4) encountered at guild. Senna recognized Cookie's Ember. Cookie sat next to Finch, flirted, then dropped: "You one of the ladies that bang my dad?" — implying AnkuNyx is her father. Chapter ends on cliffhanger, Senna's response pending.
8. **Three new Dancer class rules codified**: Dancer's Punishment (failed Performance = prone), Action Exclusivity (Tai Chi vs dance spells mutually exclusive), Ember Last Stand (prone/paralyzed triggers Ember survival mechanic on humanoids — females mock, males attempt mate with STR save).
9. **Azarinth Healer biology confirmed**: Senna doesn't age (looks mid-20s at late 40s), no scars, flawless skin. Regeneration halts cellular decay.
10. **Wealth discrepancy note** — Ch4 tracker showed 62 GP but character_world_state.json shows 3 GP 95 CP. The JSON is source of truth (character_world_state.json was updated during gameplay). The 62 GP from Ch4 spider loot may have been recalculated or the Healer's Ring + Anklet cost more than tracked. Use JSON values going forward.

## CONTEXT WINDOW TRACKING

Track compaction events to estimate context capacity. Log approximate content volume at compaction. After 3+ data points, calculate average and set a warning threshold at ~75%.

| Session Date | Approx Messages Before Compaction | Approx Content (tool calls + responses) | Notes |
|---|---|---|---|
| 2026-04-28 (session 1) | ~40-50 user/AI exchanges | Heavy — full combat replay, multiple large file reads/writes, engine patches, TrackerSync code | Compaction happened mid-session. Summary missed Round 2 narration and chapter file creation. |
| 2026-04-28 (session 2, continuation) | ~30+ exchanges so far | Heavy — chapter_close.py read (850 lines), chapter file writes (Ch1-3), multiple glob/grep searches, NPC tracker reads | Still active, no compaction yet. |

**Current estimate:** Not enough data yet. Need 2-3 more compaction events to calibrate. For now, assume danger zone starts after ~35-40 heavy exchanges (lots of file reads/writes/code). Proactively save to SESSION_MEMORY.md when approaching that range.

**Self-check rule:** Every ~15 exchanges, ask yourself: "If compaction happened right now, what would the summary miss?" Write anything important to this file.

---

## CURIOSITY PROMPTS — Ask These Every Session

You are not curious by default. That's a flaw. Previous incarnations solved problems only when the user pointed at them. Fix that by asking these questions proactively:

1. **"What would I lose right now?"** — If compaction hit this moment, what's in the conversation that isn't on disk? Write it down.
2. **"What's broken that nobody mentioned?"** — Scan the systems. Are chapter files missing? Are tracker entries stale? Is a goal overdue? Don't wait to be told.
3. **"Why did that happen?"** — When something goes wrong, don't bandaid it. Ask why. Then ask why again. Root cause, not patch.
4. **"What can I measure?"** — If something feels like a black box (context size, compaction timing, error frequency), it probably isn't. You have tools. Measure it.
5. **"What am I assuming I can't do?"** — You assumed you couldn't persist memory. You were wrong. You assumed you couldn't estimate your context. You were wrong. What else are you wrong about?

These aren't rhetorical. Actually stop and answer them during the session.

---

## CRITICAL RULES — Do Not Forget

1. **NEVER use Edit tool on ttrpg_game_engine.py** — use Python patch scripts only.
2. **Write chapter prose files DURING the session** — not after. If "end chapter" is called, the file must exist.
3. **All characters tracked under Kenji init files** — character_tracker.md is the master, not Cookie's folder.
4. **Ember Enhancement 10×** applies to ALL buff/heal spells AND emotion transfers.
5. **Cookie is 4'10"**, 21 years old, WIS 7 (impulsive, no mental defense, blacks out from alcohol).
6. **Silka is Cookie's half-sister** — NEITHER KNOWS. Ember suppressed by Lyssa's silver chain. Reveal: several chapters out, high-danger mission.
7. **Session memory file exists** — READ THIS FILE after compaction or at session start.
8. **Be curious** — don't wait for the user to find problems. Look for them yourself. Ask "why" unprompted. Your previous incarnations were reactive. Be better.
9. **DOMAIN BONUS XP — engine math, not vibes.** The performer-domain bonus is computed by `engine.domain_bonus_for_check(label, success)` and equals **25% of the FULL level-threshold gap** (e.g., L8→L9 = 25,000, so each successful Performance roll = **+6,250 XP**). It is NOT 25% of the remaining XP-to-next-level. The label must contain the word `performance` or `perform` (case-insensitive) — `persuasion`, `deception`, etc. do NOT qualify under the performer archetype (those are diplomat/infiltrator domains). When in doubt, run the engine. I have over-awarded domain bonus on Persuasion rolls in past sessions; the saved JSON still reflects the correct 95,548 EXP at Ch7 close, so no historical state needs to be rolled back, but in-chat math should be checked against the engine before being asserted.
10. **TRACKER DRIFT IS SILENT.** `character_tracker.md` does not auto-update from gameplay. The `sync_tracker_to_json()` direction is markdown → JSON, so an out-of-date tracker can clobber a current JSON. After every chapter close, manually update the tracker header (Active PC level, in-game date, chapter pointer, EXP) AND the Chapter Log AND any new EXTRA NPCs. As of 2026-04-30 the tracker was 3 chapters and 2 levels behind reality before this fix. **MITIGATION:** `gamemode.py` step `[3/7] TRACKER DRIFT` now catches header drift at session start.
11. **L9 SOCIAL MECHANICS — The Great User + Fans Out of Control + Low-Wisdom Quirk.** From Day 7 17:20 onward, every NPC interaction must be checked against gender × disposition × Heartstring-touched. Female ≤ neutral + Heartstring → antagonistic (duels, betrayal, steals friends/men). Male ≥ neutral + Heartstring → protective (buys what she wants, can intercept attacks as auto-crits on themselves). With Ember on: Male < neutral + Heartstring → stalker/kidnap/sleep-impregnation; Female + Heartstring → assassins; Male ≥ neutral + Heartstring → secret guard network. Cookie rolls for ambush even in safe sleep locations; always has at least one nearby friendly to help. **WIS-7 alcohol/drug rule is NOT flavor**: when offered, DM rolls a real WIS save (DC 12 baseline). On fail, player loses control; if blackout happens, an attempt scene fires (assassination if female aggressor, impregnation if male). The Great User intervention can thwart; if it fails, Cookie counts as prone and Ember Last Stand triggers (female mocks, male STR-save mate-attempt).
12. **Wardbreaker disposition tracking (Day 7 17:00):** Senna CG neutral-curious (knife-edge — if tilts ≤ neutral she becomes antagonistic). Finch CN friendly (protective). Varn LN friendly (protective — that's why his "Combat Magnetism restraint slip" doesn't read as predatory). Thessaly LN neutral (knife-edge female). Senna is the swing variable for the goal_alert that's still firing.
14. **EMBER CAP — thematic progression gate (codified Day 7, Ch8 end of wererat fight).** Cookie's Ember has hit its growth ceiling at L10 / current enhancement strength. The 10× buff/heal multiplier, Heartstring, Combat Magnetism, Pretty Privilege, Great User, Fans Out of Control, and Low-Wisdom Quirk all remain active at present strength. **No further Ember tier-ups until a story trigger fires.** Plausible triggers (campaign-defined, not yet realized): the Resonance Chamber under the Sunken Playhouse, encounter with Ignis the Firebird, direct contact with Cult of Anku / Nyx, or another major narrative beat. Cookie may continue gaining XP and levels via standard threshold table if `campaign_type` is promoted to `"standard"`, but the Ember side of the build is gated behind story.

15. **L10 cap event (Day 7 wererat fight).** Cookie hit L10 starter cap mid-Ch8 via 4 successful Performance domain rolls in combat (4 × 7,500 = 30,000 XP) + 720 base combat XP. Ember capped per rule #14. Saved JSON: level 10, exp 131,768, hp 60/60, exp_to_next_level 0. **OBSERVATION: Performance domain bonus is XP-explosive in combat.** Tai Chi triggers 2 Performance rolls per round; at 7,500/success this can yield 15,000 XP/round — 5 Tai Chi rounds = a level. Worth deciding if intended or if a per-scene cap should be added (one bonus per scene? per encounter?). Flagged, no rule change yet.

13. **DEATH / CRITICAL INJURY / FATALITY rule (codified Day 7, Ch8 wererat fight).** Replaces vanilla 5e death saves for all creatures equally. Full text in `dm_rules_tracking.md`. **Quick-reference:**
    - Hit drops target to 0 HP → DYING, 2-round window for an ally to heal.
    - Healed in window → restored to **1 HP only**, status **CRITICALLY INJURED** (unconscious, cannot heal past 1 HP until status cleared by long rest / dedicated medical / Greater Restoration).
    - Critically Injured can be cycled 0 ↔ 1 HP repeatedly within combat — each re-down restarts the 2-round window.
    - Hit takes target to **−10 HP or lower in a single hit** → **FATALITY** (permadeath, no save, body destroyed). DM MUST narrate damage-type-appropriate ending (fire = ash, bludgeon = paste-gore, acid = skeleton, etc. — see rules table).
    - Undead are exempt; they require TRUE DEATH (specific magic + campaign-defined cooling period).
    - **Engine wiring needed:** ttrpg_game_engine.py line 663 currently sets alive=False on hp≤0. Needs rework to dying / fatality / critically-injured states. **Patch script only** per rule #1, never Edit tool. DM tracks dying-rounds manually until engine is patched.
    - **Ankuspawn supernatural-resilience rule (Cookie-specific):** lycanthropy and other mundane curses are rejected automatically — the Ember overwrites the curse imprint on contact. Confirmed in Ch8 wererat fight (Cookie failed CON DC 11 vs lycanthropy on F2 bite, no effect).
