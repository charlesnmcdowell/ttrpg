# SESSION MEMORY — AI Persistent Notes

**Purpose:** This file is updated by the AI throughout each session to preserve context that would be lost during chat compaction. Read this file at the start of every session and after any compaction event.

**Last updated:** 2026-04-30, Ch8 opening + tracker drift fix + domain-bonus rule clarified

---

## ACTIVE STATE

- **Current character:** Cookie
- **Current chapter:** Ch8 IN PROGRESS (Day 7 afternoon — Wardbreaker confrontation aftermath, Ankuspawn public admission, hire offer at the table)
- **Day / hour:** Day 7 / ~17:00 (saved state still pinned at 16:25 — 35 min unsaved drift)
- **Level:** 8
- **XP:** 95,548 / 100,000 saved; **99,548 narrated mid-Ch8** (+4,000 unsaved from two Persuasion successes — 452 to L9)
- **HP:** 50/50
- **Fame:** LOCAL SENSATION in Varenholm
- **Gold:** 3 GP | 8 SP | 90 CP (mead at corner table on the house — Pretty Privilege)
- **Location:** Adventurer's Guild, Varenholm — corner table, mead in hand
- **Next events:** Academy next class (Day 8, 08:00), Ashworth meeting (Day 10, 10:00), Starling return shows (unbooked), Torren's patron inquiries (pending)
- **Active goals:** become_famous_bard (ongoing), guild_hire_posting (5 GP/quest), wardbreaker_encounter (Senna let her walk after "say it again, slow" — Cookie deflected with public Ankuspawn admission), ankuspawn_public_outing (Cult-of-Anku scrivener noted four letters in his ledger), Selwyn+Beldra hire offer pending response
- **Key open beats (Ch8):**
  1. Selwyn (ranger, Greyrush iron crew) is asking yes/no on a 5 GP, 2-day flooded-mill escort/pacification. Beldra (dwarf, bandaged) wants this closed in six minutes.
  2. Senna is across the room watching how Cookie lands the hire conversation — INT 18, took the dodge cleanly, did not intervene. Wardbreakers still in the hall.
  3. Cookie has mead at her lips, has not yet sipped. WIS 7 + alcohol = blackout window opens with the first swallow.
  4. Scrivener / Cult-of-Anku informant filed an entry. No immediate consequence; trail opened.

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
10. **TRACKER DRIFT IS SILENT.** `character_tracker.md` does not auto-update from gameplay. The `sync_tracker_to_json()` direction is markdown → JSON, so an out-of-date tracker can clobber a current JSON. After every chapter close, manually update the tracker header (Active PC level, in-game date, chapter pointer, EXP) AND the Chapter Log AND any new EXTRA NPCs. As of 2026-04-30 the tracker was 3 chapters and 2 levels behind reality before this fix.
