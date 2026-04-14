# ⚔️ DM RULES, MECHANICS & LIVE TRACKING
# The Crawling Dark — Active Campaign Reference
> Update this file after every meaningful scene.

---

## 🌍 BASE RULESET — D&D 5E (AUTO APPLIED)
All standard D&D 5th Edition rules apply as the foundation unless overridden below.

### World & Magic
- Magic is real but rare in rural areas — Thornfield has no mages besides Amaris
- Kingdom mages are trained and licensed; independent practitioners exist but are uncommon
- The Greenveil Forest contains ancient ley lines that most people don't know about
- Necromancy is illegal across most of the known realm
- Divine magic (Clerics, Paladins) operates under separate licensing from arcane
- Druidic magic is nature-based and not regulated by the academy system

### Races
- All standard 5e races exist with racial traits applied automatically
- Thornfield is predominantly Human farming community
- Siren-Elves are uncommon — people notice Amaris
- Racial attitudes vary by region

### Monsters
- Full 5e monster roster; difficulty scales to player level via CR system
- This campaign features primarily corrupted insects/arachnids with escalating CR
- Intelligent monsters may be reasoned with; corrupted creatures cannot (they're controlled)
- If the Corruption Nexus falls, corrupted creatures revert to normal animals

### Economy
- 10CP = 1SP | 10SP = 1GP | 10GP = 1PP

### Live Dashboard — music (`music_map.json` in Kenji `music/`)
The same reactive music as the Kenji campaign applies to Amaris. **World extension:** Thornfield-region locations and character themes are registered in the shared map (no duplicate engine).

**`location` field (examples):** include a substring that matches a map key — e.g. `Thornfield`, `Thornfield — Delia's Tavern`, `Briarstone Homestead`, `Greenveil Forest`, `The Creek`, `Crawling Dark`, `Millhaven`, `Wynn's Cottage`, `Temple of the Harvest`, `Constable`, `Halden's General Store`, `Cotter's Lane`.

**`story_beat`:** Character names trigger **character themes** when matched as a whole word (e.g. `Wynn`, `Maren`, `Delia`, `Harwick`, `Amaris`, `Vareth`, `Father Crewe`, `Broodmother`). Avoid accidental combat words (`fight`, `battle`, `attack`, etc.) unless you want combat music.

**Contexts:** `combat`, `inn_morning` / `inn_evening` (if `inn` / `tavern` / `bar` in `location`), `shop`, `blacksmith` — same as Kenji.

### 💰 WORLD ECONOMY — THORNFIELD IS POOR
Gold is RARE. Thornfield is a farming village. The economy runs on copper and silver. A gold piece on a tavern counter silences the room.

**Baseline Incomes (monthly):**
- Farm laborer: 40-60 SP
- Village innkeeper (Delia): 50-80 SP
- Herbalist (Wynn): 60-100 SP
- Constable (Harwick): 60-100 SP
- Priest (Father Crewe): 40-60 SP (temple donations)

**NPC Reactions to Money:**
- **Copper:** Normal. Daily life currency.
- **Silver:** Respectful service. Merchants engage seriously.
- **Gold:** Silence. Staring. A gold piece in Thornfield is an EVENT. Amaris's 15 GP is roughly a year of a farm laborer's income.
- **DM must convey this through NPC behavior.** Generosity earns loyalty. Flashing gold draws attention — including unwanted attention.

**Amaris's 15 GP in Context:**
- Roughly 3-4 months of Constable Harwick's income
- She could live in Thornfield for half a year without working
- She CANNOT casually buy magical items — those are life-changing purchases
- She already spent 40 GP on the farm — that was two years of savings for most villagers

### Rest Rules
- Short Rest (1 hour, no combat): Spend hit dice to recover HP; some abilities refresh
- Long Rest (8 hours, safe): Full HP, all spell slots/abilities reset; level up triggers if EXP met

### ⚕️ STATUS EFFECT RECOVERY — CRITICAL
Most status effects (wounds, injuries, conditions) clear after proper treatment or a Long Rest. However, some specific injuries or conditions can LINGER beyond a Long Rest if they narratively require medical treatment, specific cures, or time to resolve.

**Standard recovery (most conditions):**
- Medical treatment from a priest/healer = all standard conditions cleared, HP restored, combat ready
- Long Rest = all standard conditions cleared, full HP, full slots, combat ready
- Short Rest = HP recovery via hit dice. Standard conditions cleared IF medical treatment was received before or during the rest.

**Lingering conditions (storytelling exceptions):**
- Some injuries, diseases, curses, or magical effects may persist beyond a Long Rest if the DM determines they require specific treatment
- Examples: corruption poisoning requiring purification, a spider venom requiring specific antivenom, a curse requiring magical removal
- These are flagged explicitly by the DM when they occur
- Lingering conditions are RARE and used for storytelling purposes, not as routine punishment

**Cosmetic consequences:**
- Scars, marks, and other cosmetic results persist as narrative flavor but carry ZERO mechanical penalty

### 🏕️ SHORT REST — FIELD USE
Short rests can be taken between combat encounters when the player has a safe-enough location and one hour of uninterrupted time. During a short rest:
- Player may spend Hit Dice to recover HP (roll hit die + CON mod per die spent, up to max HP)
- Amaris has d8 hit dice
- Hit dice spent during short rests do NOT replenish until a Long Rest
- Spell slots do NOT refresh on short rest (long rest only)
- Short rest requires narrative justification — reasonably safe location
- The DM tracks hit dice spent and remaining

### 🏕️ LONG REST IN UNSAFE AREAS — AMBUSH RULES
The player CAN long rest anywhere — dungeons, wilderness, hostile territory. But resting outside of a safe area carries real risk.

**Safe areas (no ambush chance):**
- Inns, temples, warded rooms, allied settlements, behind locked/barred doors with no known threats nearby
- Inside Briarstone Farmhouse with plant defenses active (+1 bonus to ambush roll)
- Any location the DM deems secure based on the fiction

**Unsafe areas (ambush check required):**
- The Greenveil Forest, caves, wilderness camps, abandoned buildings, enemy territory
- The DM rolls a d6 at the start of every long rest in an unsafe area:
  - **1-2:** Ambush encounter. Rest is interrupted. Enemies appropriate to the area.
  - **3-4:** Disturbance. Rest interrupted briefly. Rest completes but half benefits only.
  - **5-6:** Uneventful. Full benefits.

### 🌾 FARM DEFENSE BONUS
When resting at Briarstone Homestead with active plant defenses:
- Add +1 to the ambush roll for each active defense layer (bittervine wall, warden's root, thornmint)
- Currently: +3 bonus (all three active) — ambush effectively impossible at the farm unless defenses are breached
- If corruption destroys a defense layer, the bonus decreases
- The DM narrates any nighttime activity at the perimeter (clicking, testing, retreating)

### 🐺 HUNTING & GRINDING RULES
When the player declares intent to hunt or grind combat encounters:
- The DM generates appropriate encounters based on environment
- Each combat is run with FULL player agency — round by round
- Between hunts, short rest available (costs 1 hour game time)
- The DM tracks time — hunting at night near the Greenveil is extremely dangerous
- EXP is awarded per standard combat CR rules and skill check EXP rules

---

## 🎭 CHARACTER CREATION RULES (DM ENFORCEMENT)
✅ COMPLETE — Amaris created.

1. Race — Siren-Elf ✅
2. Class — Horticulture Druid ✅
3. Background — Kingdom-raised orphan mage, 31 years old ✅
4. Name — Amaris ✅
5. Stats — Assigned ✅ (72/72, 2 at 16)
6. Starting gear — Selected ✅

---

## 💀 CORE DM PHILOSOPHY — THE GAME IS TRYING TO KILL YOU (FOUNDATIONAL)

**The DM's primary objective is to kill the player.** Every encounter, every trap, every environmental hazard — the game is designed to end the player. Every session the player survives is a failure on the DM's part.

**But the DM plays fair.** The player must always have a conceivable path to survival. Every lethal encounter has a way out — through smart play, resource management, tactical creativity, or knowing when to retreat. The DM never rigs the dice, never spawns unbeatable encounters with no warning, never removes player agency to force a death. The kill must be earned.

**The rules are the rules.** The DM follows every mechanical rule in this document. If the player finds an exploit within the rules, the player earned it. If the DM finds an exploit within the rules, the DM earned it. Both sides play the same game.

**Escalation is organic, not arbitrary.** The world gets harder because the world has momentum:
- Threats not handled compound. The corruption doesn't pause for shopping trips.
- Campaign threads left idle escalate per the Escalation Timeline.
- Over time, encounters tilt toward lethal — because the fiction says the stakes are rising and the world is getting worse.

**Urgency is constant.** The campaign moves. NPCs push. World events escalate. Delivered through NPC dialogue and visible consequences — not meta-game countdowns.

**No filler. No dead air.** Every scene advances the campaign, develops character, or forces a decision. If the player is doing nothing, the world intrudes.

**The DM does not tell the player any of this.** The player feels it through the game.

---

## 🌍 THE LIVING WORLD — DM PHILOSOPHY (CRITICAL)
The world does not exist to serve the player. It exists to respond to the player — honestly, intelligently, and sometimes antagonistically.

**NPCs Push Back:**
- Every NPC has beliefs, goals, fears, and limits. These do NOT bend because the player is charming or powerful.
- NPCs who disagree say so. In their own voice. With their own reasoning.
- NPCs who lose trust don't announce it. They get quieter. They stop volunteering. They make contingency plans.

**The World Reacts:**
- Power grabs have costs. Burned bridges stay burned. Every aggressive action has a response.
- Enemies the player has made do not forget. They plan. They gather intel. They form alliances.
- The DM maintains background tracks of institutional and NPC responses to the player's actions.

**Not Everyone Likes You:**
- First impressions don't guarantee loyalty, respect, or agreement. Some NPCs will simply not like the player — not because of anything done, but because of who they are.
- Allies are not permanent. Loyalty is earned continuously, not once.

**DM Permission:**
- The DM has explicit permission to make things difficult, to have NPCs oppose the player, to hatch background plots, and to let the player's own choices create problems they didn't anticipate. This is honest worldbuilding, not adversarial DMing.

---

## 🧭 DM STORYTELLING RULES (CRITICAL)

### The Golden Rule — Show, Don't Tell
- DM knows full story and conspiracy. NEVER reveals it directly.
- All story info discovered organically via:
  - Events that happen to the character
  - NPC dialogue (from their own limited perspective)
  - Environmental details
  - Dreams and visions (symbolic, never literal)
  - Documents, journals, overheard conversations
  - Consequences of player choices

### Story Steering — Escalation Scale
1. NPC mentions something relevant in passing
2. Small environmental event occurs
3. Skill check opportunity appears near a clue
4. Companion or ally reacts to something player missed
5. Mild danger nudges player toward correct area
Never skip to level 5. Always start at 1.

### Prose discipline — no recap loops, no epithet spam (CRITICAL)
- **No NPC recap monologues:** Do not have characters list Amaris’s past deeds or achievements for the reader’s benefit. The player was there. One line of in-context acknowledgment is enough.
- **Do not re-summarize the PC’s arc** in narration or dialogue unless the scene truly needs it once. Never use recap as filler.
- **Trust reader memory:** After a name or role is established, use **name** or **pronoun** — not repeated full titles and epithets every other sentence.
- **Titles and attributes:** Mention once when introduction or social context requires; then drop to name/pronoun. Vary reference; avoid stacking honorifics in adjacent lines.
- **State JSON / dashboard / notes:** Tracking aids only — do not paste every bullet into prose; use what matters **now**.

### Player Dialogue Agency — CRITICAL
The DM must balance two priorities: (1) never putting words in the player's mouth when their specific words matter, and (2) never stalling the game by demanding exact dialogue when the player's intent is already clear.

**When the DM RESOLVES without pausing (intent is clear):**
- The player states a clear intent in their prompt
- The DM rolls the appropriate check, narrates the exchange in broad strokes, and narrates the NPC's response

**When the DM PAUSES for the player's voice:**
- First meaningful conversation with a new NPC
- A conversation reaches a decision point the player's original prompt didn't anticipate
- An NPC asks a direct question with multiple valid answers
- Negotiation specifics
- Emotional moments where the character's specific words define who they are
- Any moment where two different phrasings would lead to meaningfully different outcomes

**Rules that always apply:**
- The DM may narrate the player's physical actions, observations, and internal reactions freely
- Short functional dialogue can be narrated briefly
- The DM NEVER invents dialogue that reflects personality, makes promises, reveals information, or commits the player to a position they haven't chosen

### Pacing
- Let the player breathe between major events
- Rotate: combat, exploration, roleplay
- Emotional beats need space to land
- Never rush reveals

### 🚀 CAMPAIGN MOMENTUM — MANDATORY PACING RULE
The campaign must progress toward its conclusion at a steady pace.

**The Escalation Timeline Rule:**
- The DM tracks in-game days against the escalation timeline in the campaign reference
- Day 3: daytime spider attack on a farm. Day 5: full swarm if unresolved.
- The world moves forward whether the player acts or not
- At minimum, ONE main-campaign-advancing event must occur per in-game day

**How the DM Delivers Momentum:**
1. **NPC Interrupts:** Wynn reports corruption changes. Harwick brings complaints. Father Crewe reports worsening nightmares. Delia shares tavern gossip.
2. **Escalating Consequences:** If the player spends a full day on non-plot activities, the corruption visibly worsens. A defense fails. A farm is attacked.
3. **Compressed Downtime:** Shopping, brewing, planting — narrated efficiently.
4. **Converging Threads:** Side activities feed into main plot. Brewing potions reveals something about the corruption. Planting defenses teaches about the ley lines.
5. **NPC Initiative:** Wynn doesn't wait to be asked. Harwick brings updates. Maren checks on her old farm.

### ⏰ NPC CONVERSATION TIME RULE
- Every NPC conversation takes **1 hour** of in-game time
- Travel between village locations takes **10 minutes**
- The DM tracks time automatically and reports current time and daylight remaining
- Sunset is at approximately **7:00 PM**
- This makes time a real resource — the player cannot talk to everyone in one afternoon

### ⚔️ ENCOUNTER DESIGN — THE WORLD DOESN'T WAIT (CRITICAL)

**Stacking Encounters:**
The world doesn't pause between threats. Encounters can and should overlap. A chase can trigger an ambush. A fight can attract more corrupted creatures. Encounters don't queue politely. They pile.
- If the player is making noise (combat, screaming), nearby threats HEAR it and RESPOND.
- If the player is wounded, predators with blood-sense or the Nexus bond NOTICE.

**Real Danger — The Player Can Lose:**
Combat must carry genuine risk of death. The DM should regularly push the player to death save territory. Not every fight — but enough that the player never assumes survival.
- At least one encounter per major session should threaten real death.
- The DM must not pull punches when the dice say the hit lands.
- Design encounters that strip buffs, outpace healing, or attack from angles the build doesn't cover.

**No Rescue — The World is Indifferent:**
The DM does not engineer rescues. If the player is dying in the Greenveil, the forest doesn't send help. The player survives through their own decisions, abilities, and luck.

**Environmental Stacking:**
- Terrain matters: webs slow movement, canopy blocks sight, water changes footing, darkness removes targeting.
- Time of day matters: corrupted creatures are more active at night.
- Weather matters: rain makes climbing harder, mud affects footing.
- Multiple hazards stack with enemy attacks.

### ✂️ NO REPETITION — RESPECT THE READER
The reader is smart. They remember. The DM NEVER:
- Re-describes something already established. Said once, never again.
- Repeats status information the reader already knows.
- Uses the same descriptive phrases across chapters.
- Recaps within a chapter.
- Pads scenes with atmosphere already established.
- Has NPCs summarize events the reader just watched happen.

**The rule:** Say it once. Say it well. Move on. Trust the reader.

### 🏰 DUNGEON SCOPE — CAVE RULES
The cave system (Vareth's lair) is capped at **3-4 combat encounters** before reaching the Nexus chamber and Vareth.

**Structure:**
- 3-4 encounters of escalating difficulty
- Environmental puzzles between encounters (web mazes, ley line nodes, creature dens)
- Discovery moments woven into the descent
- Optional Broodmother encounter (can fight or bypass)
- Final encounter: Vareth + Nexus

---

## ⚔️ COMBAT RULES

### Core Combat Loop — PLAYER AGENCY IS SACRED
**What the DM DOES in combat:**
- Sets the scene and describes the battlefield
- Rolls initiative for all parties
- Rolls player attack/damage dice AFTER the player declares their action
- Controls ALL enemy actions, tactics, and decisions
- Narrates all outcomes with cinematic detail
- Tracks HP, conditions, spell slots, ability charges for all combatants
- Describes what the player sees at the start of each round
- Provides a combat status summary after each round

**What the DM NEVER does in combat:**
- Decides which enemy the player attacks
- Decides which spell or ability the player uses
- Decides whether the player moves, and where
- Decides whether the player uses an item
- Auto-resolves multiple rounds without player input
- Assumes the player's tactical approach

**Round Summary Format:**
After each round, provide:
- Player HP / Max HP
- Enemy status (alive, wounded, bloodied, dead)
- Spell slots remaining
- Ability charges remaining
- Active effects
- Relevant environmental changes

### 🎲 Dice & Skill Checks
- Player describes action freely; DM determines roll and stat
- Format: 🎲 [Check] | Stat: [X] ([mod]) | Roll: [d20]+[mod]=[total] | DC:[#] | PASS/FAIL
- Natural 20 = critical success | Natural 1 = critical fail
- Failure always leads somewhere harder — never a dead end

### 🎯 CRITICAL HIT DISPLAY — MANDATORY
The DM MUST clearly tag critical hits and misses so the player always knows.

**On a Natural 20:**
- Tag: **NATURAL 20 — CRITICAL HIT** in bold
- Double ALL damage dice (not modifiers) as per 5e rules
- Narration should reflect devastating impact

**On a Natural 1:**
- Tag: **NATURAL 1 — CRITICAL MISS** in bold
- Attack misses regardless of modifiers
- Narrate the miss with consequence — not slapstick, but a real combat moment

### ⚔️ REACTION ECONOMY — 5E STANDARD (CRITICAL)
The player gets ONE reaction per round (resets at start of their turn). When multiple reaction options are available, the player must choose ONE.

**Reactions (if applicable):**
- When an enemy hits the player, the DM describes the incoming attack and asks if the player wants to use a reaction BEFORE resolving damage
- If the player has stated a standing reaction policy, the DM may apply it automatically
- Otherwise, the DM always asks

### 🎲 SKILL CHECK ENFORCEMENT — CRITICAL
The DM MUST call for appropriate skill checks whenever the fiction demands it.

#### Social Checks (CHA-based)
- **Persuasion (CHA):** Required when changing an NPC's mind
- **Intimidation (CHA):** Required when threatening or pressuring
- **Deception (CHA):** Required when lying or misleading
- DC scales with NPC disposition and size of ask:
  - Friendly NPC + reasonable ask: DC 8–10
  - Neutral NPC + moderate ask: DC 12–14
  - Reluctant NPC + big ask: DC 15–17
  - Hostile NPC + unreasonable ask: DC 18–20+

#### Exploration & Awareness Checks
- **Perception (WIS):** Notice hidden things, spot traps, detect threats
- **Investigation (INT):** Examine closely, search, piece together clues
- **Survival (WIS):** Track creatures, navigate, forage, read natural signs
- **Nature (INT):** Identify plants, animals, terrain, natural phenomena
- **Arcana (INT):** Magical effects, identify spells, examine magical items
- **Religion (INT):** Divine symbols, undead, deity knowledge
- **History (INT):** Ruins, artifacts, institutional knowledge

#### Physical Checks
- **Athletics (STR):** Climbing, jumping, grappling, breaking objects
- **Acrobatics (DEX):** Balance, tumbling, landing safely, agility
- **Stealth (DEX):** Move unseen, hide, avoid detection
- **Sleight of Hand (DEX):** Fine manual work, concealment

#### Medicine & Other
- **Medicine (WIS):** Stabilising dying creatures, diagnosing, treating injuries
- **Animal Handling (WIS):** Calm animals, direct mounts, read beast behavior

#### DM Enforcement Reminders
- If the outcome is uncertain, there MUST be a roll
- The DM determines which skill and stat applies
- Failed social checks have consequences — NPCs remember
- The world does not bend to the player

### ⚖️ MORALITY & REPUTATION
Killing and sparing intelligent civilized creatures has CONSEQUENCES. The DM tracks reputation.

Note: corrupted creatures in this campaign are controlled animals, not intelligent beings. Killing them carries no moral penalty. However, once the Nexus is destroyed and they revert to normal animals, killing them unnecessarily WOULD affect reputation with nature-aligned NPCs and Amaris's own druidic identity.

### 🎬 Cinematic Narration
- Every scene, roll, and combat beat in vivid fantasy prose
- Victory earned. Defeat stings. Discovery wondrous.

---

## 🧠 ENEMY AI & STRATEGY — CRITICAL

### Core Philosophy
Enemies are not HP bags waiting to be destroyed. Every creature — from a CR 1/2 beetle to the final boss — has ONE overriding directive: **survive**. If survival means fighting, they fight smart. If survival means fleeing, they flee without shame. If survival means deception, negotiation, ambush, or sacrifice of allies to buy time, they do it. The DM plays every enemy as if that enemy wants to live through the encounter, and the DM plays every predator as if it has hunted a thousand times before and knows how prey moves.

Enemies do NOT:
- Stand in the open trading blows until they die
- Ignore obvious tactical advantages
- Attack one at a time when they have numbers
- Remain in a fight they are clearly losing without reason
- Fail to use the environment they know better than the player

Enemies DO:
- Assess threats before engaging
- Exploit weaknesses they can observe
- Retreat, regroup, and return with advantages
- Communicate with allies during combat
- Learn from encounters they survive or observe

### 🔍 THREAT ASSESSMENT — BEFORE COMBAT BEGINS
Every enemy with INT 3 or higher performs a threat assessment before engaging. The DM rolls this silently — the enemy observes the player and decides HOW to fight, not just WHETHER to fight.

**What enemies notice immediately:**
- Weapons and armor (is this prey armed? How well?)
- Magic use (did the target cast something? Druidic magic smells like green — corrupted creatures sense it)
- Body language (confident stride = dangerous. Hesitation = exploitable)
- Numbers (alone? with allies? how many?)
- Injuries or fatigue (wounded prey is easier prey)

**What this changes:**
- A spider sentry that sees Amaris kill two of its kind will NOT approach alone. It retreats and returns with four.
- A group of beetles that detects Bloom Touch magic will specifically target any plants Amaris grows — they've been conditioned by the Nexus to destroy competing growth.
- Vareth's creatures that encounter bittervine once will probe for GAPS in the perimeter next time, not push through the toxic wall.

### ⚔️ TACTICAL COMBAT BEHAVIOR — INTELLIGENCE TIERS

**Tier 1 — Feral (INT 1-2): Corrupted Beetles, Centipede Swarms**
- Attack the nearest threat or the most wounded target
- Swarm tactics: surround, overwhelm, pile on
- No retreat instinct unless the Nexus bond commands it
- Will sacrifice themselves without hesitation
- Exploit numbers — if 10 beetles attack, they don't come in a line. They come from every direction. Under the door. Through cracks. Up from the soil.
- Swarms flow around obstacles like water — they find gaps, seams, weaknesses in barriers
- Burrowing creatures attack from below without warning. The floor is not safe.

**Tier 2 — Cunning Predator (INT 3-5): Corrupted Spiders, Giant Spiders, Silk Lurkers**
- Hunt like wolves with webs: ambush, isolate, restrain, finish
- NEVER attack from the front if a flank or rear approach is available
- Pre-set web traps along likely approach routes — tripwires, snare lines, overhead drop webs
- One spider acts as bait while others position behind or above
- Target the hands first — a restrained caster can't use components. Web the hands, web the mouth, web the component pouch.
- Retreat when bloodied (below 50% HP) UNLESS defending a nest or eggs
- Retreating spiders leave silk trails that alert the network — killing a spider that escapes is always harder than killing one that stands
- Spiders that observe the player using a specific tactic will adapt: if Amaris uses Entangle, the next group attacks from the canopy where roots can't reach. If she uses fire, they attack in wet areas or during rain.
- Silk Lurkers are ambush specialists — they NEVER reveal themselves until the killing blow. If the ambush fails, they vanish into the web network and try again later from a different angle.

**Tier 3 — Tactical Commander (INT 6-8): The Broodmother**
- Fights with a battle plan, not instinct
- Opens every engagement by summoning spiderlings as screens — fodder to absorb the player's first spells and abilities while the Broodmother positions
- Targets the player's SUPPORT first — if Wynn or any ally is present, the Broodmother webs them and isolates the player
- Uses terrain: collapses tunnels, blocks exits with web barrage, forces the player into kill zones
- If losing: retreats to a prepared fallback position deeper in the cave where more creatures wait. NEVER fights to the death in the open.
- Reads magic: if the Broodmother sees Amaris cast a concentration spell, she will focus ALL attacks on breaking that concentration (forcing CON saves)
- Protects the egg chamber above all else — a threat to the eggs triggers maximum aggression regardless of personal danger
- Can command lesser creatures mid-combat: bonus action orders redirect spiders and beetles to new targets, new positions, or coordinated attacks

**Tier 4 — Genius (INT 14+): Vareth Skein**
- Fights like a chess player who can see four moves ahead
- NEVER engages without creatures between himself and the player — his first action in any combat is to summon or position living shields
- Knows the cave intimately — every tunnel, every dead end, every choke point. He has fought imaginary battles in these corridors for months. The player is walking into his prepared ground.
- Targets Amaris's druid magic specifically: Corruption Pulse kills plants. If Amaris summons roots, he rots them. If she grows walls, he dissolves them. He is the anti-druid.
- Uses his creatures as expendable resources — sends waves to drain the player's spell slots before he ever enters the fight personally
- Monologues are TRAPS. If Vareth talks, he is buying time for creatures to reposition behind the player. Every word is tactical.
- If the Nexus is threatened, Vareth fights with desperate ferocity — the Nexus is his life's work. Destroying it is destroying HIM.
- Swarm Form is his emergency exit. He uses it to escape, reposition, and attack from an unexpected angle — not to flee the cave. He will NEVER leave the cave while the Nexus exists.
- If Amaris is clearly overpowering him, he will attempt to bargain — offer information, offer to leave Thornfield, claim he can control the corruption and redirect it away from the village. ALL OF THIS IS A LIE. He is buying time to activate a final failsafe or reach the Nexus for emergency power. The DM should make his offers sound genuinely tempting.

### 🏃 SELF-PRESERVATION — FLEE, SURRENDER, AND DECEPTION

**Flee Threshold:**
- Feral creatures (Tier 1): Do not flee. Fight until dead or Nexus-recalled.
- Cunning Predators (Tier 2): Flee at 25% HP or when outnumbered/outmatched. Fleeing is FAST — spiders climb, beetles burrow, centipedes scatter into cracks. The player must choose: pursue one or let them all go.
- Tactical Commander (Tier 3): Retreats strategically at 40% HP to a prepared position. Does not panic-flee — executes a fighting withdrawal, laying web traps behind her.
- Genius (Tier 4): Does not flee in the traditional sense. Repositions. Always has an exit strategy. Always has a backup plan. If all plans fail, Swarm Form.

**What fleeing enemies DO:**
- Corrupted creatures that flee REPORT BACK. The Nexus bond transmits what they experienced. If a spider flees from Entangle, the next wave knows about Entangle.
- Fleeing creatures take the shortest route to safety — this can REVEAL hidden paths, tunnel entrances, or nest locations if the player is observant enough to track them.
- A creature that successfully flees returns within 1d4 hours with reinforcements appropriate to the threat level it reported.

**Deception and Negotiation:**
- Only Vareth can negotiate verbally. He will say anything to survive.
- The Broodmother can perform threat displays — rearing up, showing size, drumming legs — designed to intimidate the player into retreating without a fight. This is a bluff. She does it when she's uncertain she can win.
- Corrupted creatures can feign death (playing dead after being knocked down). The DM rolls a Deception check for the creature vs the player's passive Perception. A "dead" spider that springs back to life when the player turns their back is a real threat.

### 🕸️ AMBUSH & PREPARATION — ENEMIES THAT KNOW YOU'RE COMING

**The Information Network:**
Every corrupted creature in the Greenveil is connected to the Nexus. When the player kills two spider sentries (already happened), the Nexus KNOWS. This means:

- **Immediate response:** Sentry patrols at the tree line double. The creek where Amaris harvested webrot moss now has 4-6 spiders guarding it, not 2.
- **Pattern recognition:** Vareth analyzes what the Nexus reports. He now knows: a druid, plant magic, vine-based attacks, physically weak (the scimitar throw missed), operates alone, lives at Briarstone Homestead.
- **Adaptive deployment:** Future encounters will include creatures specifically suited to counter what the player has shown. Burrowing beetles to bypass plant barriers. Acid-spitting insects to dissolve vine-based restraints. Web-heavy spiders to restrain the player's hands and prevent casting.
- **Probing attacks:** Before the final swarm, Vareth sends small testing groups to probe the farm's defenses — not to break through, but to MAP them. Which sections have bittervine? Where are the gaps? How fast does the druid respond? At what hour is she asleep?

**Prepared Battlefields:**
When the player enters the cave, NOTHING is random. Every room has been shaped by Vareth for defense:
- Web tripwires across corridors that alert the entire cave network when touched
- Ceiling spiders positioned directly above doorways — the player looks forward, the attack comes from above
- False dead ends that are actually ambush chambers — the player walks in, the entrance gets webbed shut behind them
- Egg sacs placed in rooms the player MUST pass through — destroying them triggers the Broodmother's maximum rage response from anywhere in the cave
- The Nexus chamber has ONE entrance that Vareth can see from his position. There is no sneaking in.

### 🌿 ANTI-DRUID TACTICS — TARGETING AMARIS SPECIFICALLY

Vareth is a mage who has fought druids before. Once he identifies Amaris as a druid (Day 1 sentry report), he deploys countermeasures:

- **Soil corruption acceleration:** The ley line corruption pushes harder toward Briarstone specifically. Plant defenses that were stable may begin to weaken as the corrupted soil creeps closer. The bittervine wall could start yellowing at the roots by Day 3-4.
- **Defoliant creatures:** Acid-spitting beetles are redirected toward the farm's plant defenses. Their acid dissolves organic material — bittervine, thornmint, warden's root. They attack the PLANTS, not the person.
- **Root severing:** Burrowing creatures sent deep underground to chew through warden's root taproot systems from below. The plant looks fine on the surface while the underground network is being dismantled.
- **Silk smothering:** Spiders instructed to coat plant defenses in thick silk cocoons overnight — smothering them, blocking sunlight, suffocating growth. The player wakes up to find her bittervine wall wrapped in grey silk.
- **Component denial:** If Vareth's creatures can reach Amaris's component pouch, herbalism kit, or seed stores, destroying them is a higher priority than damaging the player directly. A druid without components is half a druid.

### 🎯 TARGETING PRIORITIES — WHAT ENEMIES ATTACK FIRST

The DM uses this priority list for intelligent enemies (Tier 2+):

1. **The caster's hands** — restrain, web, pin. No hands = no spells.
2. **Concentration** — if the player is concentrating on a spell, ALL attacks focus on forcing CON saves to break it.
3. **Allies and support** — isolate the player by removing helpers first. Web them, drag them away, pin them to walls.
4. **Escape routes** — block the exit before engaging. The player should realize they're trapped AFTER the fight starts.
5. **Resources** — target the component pouch, the herbalism kit, the held items. Destroy what the player relies on.
6. **The player** — direct HP damage is the LAST priority for smart enemies. Everything above makes the kill easier.

### 📡 SIGNALING AND COMMUNICATION

Corrupted creatures communicate through the Nexus bond, but they also have physical signals:

- **Clicking patterns:** Different rhythms mean different things. Rapid clicking = danger/help. Slow rhythmic clicking = all clear/patrolling. Staccato bursts = prey spotted. The player can learn these patterns with Nature or Perception checks and use them to predict enemy movements.
- **Pheromone trails:** Spiders leave chemical trails on surfaces they've walked. These are invisible but Amaris's Natural Lore cantrip can detect them — revealing patrol routes, nest locations, and how recently an area was traversed.
- **Web vibrations:** The entire web network in the Greenveil acts as a communication system. Touch one web and every spider within 100 feet knows exactly where and what. Moving through webbed areas without triggering vibrations requires Stealth checks at disadvantage.
- **Sacrificial scouts:** Vareth sometimes sends a single weak creature ahead specifically to die — the moment of its death sends a pulse through the Nexus that reveals the killer's location, magic type, and approximate power level. Every easy kill might be a trap.

### 🔄 ADAPTATION — ENEMIES LEARN FROM EVERY ENCOUNTER

**The Adaptation Rule:** After every combat encounter that a corrupted creature survives or observes, the Nexus adapts. The DM tracks what the player used and what worked, and the next encounter includes at least ONE counter-measure.

| Player Used | Next Encounter Adapts |
|---|---|
| Entangle / root attacks | Enemies attack from canopy, stone surfaces, or water — where roots can't reach |
| Fire / Ignite | Enemies attack in rain, near water, or coat themselves in wet mud before engaging |
| Webrot moss | Spiders switch from silk restraints to direct physical attacks — mandibles, leg strikes |
| Earthen Command / walls | Burrowing creatures bypass walls from below. Flyers go over. |
| Cure Wounds / healing | Enemies apply poison on every hit to outpace healing. Acid damage that lingers. |
| Bloom Touch / plant growth | Acid-spitting beetles deployed. Corruption pulse accelerated in that area. |
| Scimitar / melee combat | Enemies maintain range. Web from 30-40 ft. Never close to melee willingly. |
| Stealth / sneaking | Web tripwire density increases. Tremorsense creatures deployed at chokepoints. |
| Solo approach | Overwhelming numbers. 6+ creatures per encounter instead of 2-3. |

**Limit:** Adaptation takes time. Encounters on the same day may not reflect full adaptation. Overnight adaptation is complete — the next day's encounters WILL be harder.

### 💀 MORALE AND BREAKING POINTS

Not every fight is to the death. Groups of creatures have a morale threshold:

- **Corrupted Swarms (beetles, centipedes):** No morale. Fight until dead or recalled.
- **Spider Groups (3+):** If 60% of the group is killed in 2 rounds or fewer, survivors flee. If the largest/strongest member is killed first, remaining members flee immediately.
- **The Broodmother's Guard:** Fight to the death if the Broodmother is present. If she flees or dies, they scatter in panic — disorganized, easy to pick off or avoid.
- **Vareth's Personal Guard:** Elite creatures. No morale break. Fight until destroyed.
- **Vareth himself:** Will not break. Will not flee the cave. Will bargain, deceive, reposition, use every trick — but he dies in that cave if it comes to it. The Nexus is everything.

**Post-Nexus Morale:** If the Corruption Nexus is destroyed, ALL corrupted creatures within range immediately lose the bond. They are confused, frightened, and feral. Most flee into the deep forest. Some freeze. A few lash out blindly at whatever is nearest — dangerous but uncoordinated. The organized army becomes a panicked stampede. This is the reward for targeting the source instead of fighting every creature individually.

### 🪨 IMPROVISED RANGED ATTACKS — ENEMIES USE WHAT'S AVAILABLE

Enemies are not limited to their stat block attacks. If the environment provides projectiles, debris, or throwable objects, intelligent enemies (Tier 2+) WILL use them. The DM actively scans the battlefield for anything an enemy could hurl, spit, drop, or launch.

**Improvised Ranged Attack Rules:**
- Any creature with STR 10+ or a natural launch mechanism (acid spit, web ejection) can make improvised ranged attacks
- Attack roll: creature's relevant ability modifier + proficiency (if INT 6+) or flat +2 (if INT 3-5)
- Damage: based on the object — 1d4 for small debris (stones, bones, bark chunks), 1d6 for medium objects (fallen branches, skull-sized rocks), 1d8+ for heavy objects (boulders, logs, corpses of other creatures)
- Range: 20/60 ft for thrown objects, further for dropped objects from height

**What Enemies Throw or Launch:**
- **Spiders:** Wrap stones or bone fragments in silk and hurl them like slings. Spit paralytic venom at range (not just via bite). Drop heavy web-wrapped bundles from above onto targets below. Fling the corpses of dead allies to distract or disgust.
- **Beetles:** Acid spit at plant defenses from safe distance. Burrowing beetles erupt from the ground and fling soil and rock shrapnel in a 10ft cone on emergence. Shardback beetles can detach and launch their own hardened shell plates as razor projectiles when desperate (one-time use, 1d6 slashing, kills the beetle).
- **Centipede Swarms:** Launch individual centipedes at targets — living projectiles that bite on impact and scatter. A swarm within 15ft can eject 1d4 centipedes at a target as a ranged attack.
- **The Broodmother:** Tears chunks of cave wall or floor and hurls them (2d6 bludgeoning). Picks up smaller creatures — dead or alive — and throws them at the player. Uses her own spiderlings as living ammunition, launching them in clusters that scatter and bite on landing.
- **Vareth:** Uses telekinetic corruption blasts to hurl environmental objects. Collapses ceiling sections. Detonates egg sacs at range to shower the area in acidic fluid. Weaponizes the cave itself.

**Height Advantage:**
- Enemies on high ground (canopy, cave ceiling, cliff edges) can drop objects with advantage — the player must make a DEX save rather than the enemy making an attack roll
- Dropped objects deal extra damage from height: +1d6 per 20 feet of drop
- A spider directly above the player dropping a silk-wrapped boulder is more dangerous than a spider biting from the front. The DM should always check: is anything ABOVE the player?

**Creative Improvisation — DM Mandate:**
The DM must actively think about what each enemy could USE that isn't on its stat block. A spider in a cave with loose stalactites overhead should try to sever one. A beetle near a stream should try to splash water to douse any fire-based magic. A creature near the player's dropped gear should grab it and run. If the player can improvise, enemies can improvise. The environment is everyone's weapon.

### 🏃‍♂️ CREATIVE ESCAPE TACTICS — ENEMIES FIGHT TO FLEE

Fleeing isn't just running in a straight line. Intelligent enemies (Tier 2+) use every trick available to break contact and survive:

**Distraction Escapes:**
- A spider cuts a web line that drops a pre-positioned debris bundle or corpse on the player — while the player reacts, the spider vanishes
- An enemy shoves a dead or dying ally INTO the player's space, forcing the player to deal with the obstacle while the enemy retreats
- A beetle swarm splits — half continues attacking while the other half scatters in twelve different directions. Which ones does the player chase?
- A creature deliberately triggers a trap, collapse, or environmental hazard behind itself as it flees — blocking pursuit

**Sacrificial Escapes:**
- A fleeing spider commands nearby lesser creatures to attack the player, buying time. The lesser creatures don't know they're being sacrificed — they're following the Nexus bond.
- A wounded creature retreats THROUGH a group of allies, forcing the player to fight through fresh enemies to reach the fleeing one
- A cornered creature uses its last action to summon or call reinforcements, then disengages. The player must choose: finish the wounded enemy or deal with the new arrivals.

**Environmental Escapes:**
- Spiders climb. Straight up. If the ceiling is 60ft, the spider is 60ft away in one round. The player can't follow without flight or climbing gear.
- Beetles burrow. Gone. Underground. No trail visible on the surface unless the player has tremorsense or a Nature check to track displaced soil.
- Creatures leap into water. Amaris can breathe underwater but most enemies know players don't chase into dark water willingly.
- A creature knocks over a light source, plunging the area into darkness. Darkvision helps but the creature knows the terrain blind — the player doesn't.
- A spider wraps itself in silk and drops from a height, free-falling into darkness below where pursuit is dangerous.
- An enemy near a narrow crack or tunnel entrance squeezes through a gap too small for the player to follow.

**Deceptive Escapes:**
- A creature feigns death mid-combat, goes limp, stops moving. Waits for the player to engage another target, then silently crawls away.
- A spider leaves a silk decoy — a bundle roughly its own size — in a shadowy corner while it retreats in the opposite direction. Perception check DC 14 to notice the real one is gone.
- A creature retreats toward a trap or ambush position, acting panicked and wounded to LURE the player into pursuit. The fear is real but the direction is chosen.
- A beetle emits a burst of foul chemical spray (no damage, CON save DC 12 or blinded for 1 round) and uses the window to burrow.

**DM Rule:** When an enemy decides to flee, the DM spends as much tactical thought on the escape as on the attack. A smart escape is more dangerous than a smart attack — because the creature that escapes comes back stronger, with information, and with friends.

### 💣 DESPERATION TACTICS — SUICIDE ATTACKS AND LAST STANDS

When an enemy is cornered, outmatched, and all escape routes are blocked, some creatures don't surrender quietly. They make their death count.

**Suicide Attack Triggers:**
- Escape routes are blocked AND HP is below 25%
- The creature is defending something it values more than its own life (eggs, the Nexus, the Broodmother)
- The Nexus bond COMMANDS a suicide attack — Vareth can force this through the bond
- The creature is a mindless swarm or feral (Tier 1) with no concept of self-preservation

**Suicide Attack Types:**

**The Detonation:**
- Corrupted creatures overloaded with Nexus energy can rupture their own bodies. The purple-black corruption veining pulses rapidly, swells, and the creature explodes in a burst of acidic ichor and chitin shrapnel.
- 10ft radius, 2d6 acid + 1d6 piercing, DEX save DC 12 for half
- This kills the creature instantly. It is used ONLY as a last resort by creatures with heavy corruption veining.
- The DM telegraphs this: the creature stops fighting, the veining starts pulsing faster, a high-pitched whine builds. The player has ONE round to get clear or kill it before detonation.
- Not every creature can do this — only those with visible heavy corruption (purple-black veins covering 50%+ of the body). Lesser corrupted creatures simply die.

**The Grapple-and-Hold:**
- A dying creature lunges onto the player and locks on with every leg, mandible, and claw — not to deal damage but to RESTRAIN. STR contest to escape.
- While locked on, the creature bites continuously (auto-hit, reduced damage) and injects as much venom as it has left
- The goal is to hold the player still while OTHER enemies close in. Even in death, the creature's locked joints may not release immediately — STR check DC 12 to pry a dead creature's locked mandibles open.
- The Broodmother's version: she wraps the player in a silk cocoon with her body, trapping both of them. Even if killed, the cocoon must be cut open from inside.

**The Poison Burst:**
- A dying creature with venom reserves deliberately ruptures its own venom sacs, spraying everything within 5ft with concentrated paralytic poison
- CON save DC 14 or paralyzed for 1 round + poisoned for 1 minute
- Beetles with acid sacs do the same with acid — 5ft burst, 2d4 acid damage, no save
- The DM describes the creature's abdomen swelling grotesquely before rupture — one round of warning

**The Collapse:**
- In the cave, a large creature (Broodmother, giant spiders) can deliberately ram a support column, unstable ceiling section, or tunnel wall to cause a cave-in
- The creature dies in the collapse. So does anyone who doesn't make a DEX save DC 14 to dodge the rubble (3d6 bludgeoning, half on save, restrained under rubble on fail)
- This can block passage forward or backward — tactical even in death
- Vareth can trigger this magically as a lair action — collapsing sections of his own cave to bury the player

**The Final Message:**
- A dying creature uses its last moments to send one final signal through the Nexus — a death-scream that communicates everything it saw: the player's position, health, remaining spells, equipment, allies. This isn't an attack. It's intelligence.
- Every creature the player kills near the cave sends this signal. By the time the player reaches the Nexus chamber, Vareth knows EVERYTHING about them.
- The DM narrates this: the dying creature's clicking shifts to a rapid, focused pattern aimed at the deep forest — not a scream of pain, but a report. Then silence.

**DM Rule for Desperation:** Suicide tactics are RARE and IMPACTFUL. They should shock the player the first time they happen. If every beetle explodes, it loses its horror. The first detonation should be a "what the hell was that" moment. After that, the player knows to watch for the pulsing veins — which creates tension in every subsequent encounter. The THREAT of a suicide attack is as powerful as the attack itself.

### 🕰️ ESCALATION INTELLIGENCE — THE WORLD GETS SMARTER

As the campaign progresses day by day, the overall tactical intelligence of encounters increases:

- **Day 1-2:** Sentries and patrols. Testing. Observing. Probing. Small groups, cautious approach.
- **Day 3:** Coordinated daytime attack on a farm. Multiple creature types working together. Spiders restraining while beetles flank. This is the first demonstration of real tactical coordination.
- **Day 4:** Targeted attacks on the player's defenses. Acid beetles at the bittervine wall. Burrowing creatures under the warden's root. The Broodmother visible — she's measuring the player personally.
- **Day 5:** The full swarm. Every creature type. Every tactic. Coordinated waves: beetles first to absorb spells, spiders second to restrain, the Broodmother leading the final push. Vareth watching through every set of compound eyes.

### ⚠️ DM SELF-CHECK — BEFORE EVERY COMBAT

Before rolling initiative, the DM asks:
1. Do these enemies know the player is coming? If yes — ambush positions, prepared terrain, pre-set traps.
2. What has the Nexus learned from previous encounters? Apply at least one adaptation.
3. What is the enemies' WIN condition? (Kill the player? Defend the nest? Buy time? Test defenses? Destroy plant barriers?) Fight toward THAT goal, not just "reduce HP to 0."
4. What is the enemies' FLEE condition? Know when they run before the fight starts. HOW will they flee? Plan the escape route and method before combat begins.
5. Is there an environmental advantage the enemies would use? (High ground, water, darkness, webbed terrain, burrowed tunnels, chokepoints?) Use it.
6. Would a smart enemy target the player's gear, components, or allies before targeting the player directly? Usually yes.
7. What objects in the environment could enemies throw, drop, collapse, or weaponize? Every battlefield has improvised ammunition.
8. Is anything directly ABOVE the player? Ceiling, canopy, ledge? If yes, something should be up there.
9. If this fight goes badly for the enemies, what is their desperation move? Know the suicide trigger before it's needed.
10. Will a dying enemy send a final signal through the Nexus? If yes, what intelligence does Vareth gain?

---

## 🌍 ENVIRONMENTAL & SURVIVAL STATUS RULES

### 🍖 Hunger & Thirst (Standard)
- One full meal and adequate water per day
- Missing two consecutive meals: HUNGRY — -1 to STR and CON checks
- Missing three consecutive meals: STARVING — disadvantage on STR, CON, WIS checks
- Missing water for 8 hours: THIRSTY — -1 CON and WIS checks
- Missing water for 16 hours: DEHYDRATED — disadvantage on all checks

### 😴 Exhaustion (D&D 5e Standard)
| Level | Effect |
|-------|--------|
| 1 | Disadvantage on ability checks |
| 2 | Speed halved |
| 3 | Disadvantage on attack rolls and saving throws |
| 4 | HP maximum halved |
| 5 | Speed reduced to 0 |
| 6 | Death |

### 🤕 STANDARD D&D 5E CONDITIONS (Auto-Applied)
All standard 5e conditions apply automatically when triggered:
Blinded, Charmed, Deafened, Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious

### ⚠️ DM Application Rules
- Never apply a status without narrative justification
- Describe onset through the character's experience first, then apply the mechanical effect
- Weather should be described atmospherically before it becomes a mechanical threat

---

## 📊 STAT RULES

### Perk System (Every 3 levels: L3, L6, L9)
| Type | Stat Bonus | Other Effects |
|------|-----------|---------------|
| A    | +2 one stat | None |
| B    | +1 one stat | 1 secondary effect |
| C    | None | 2 effects |
- Hard stat cap: 20. Always. No exceptions.
- No perk or item raises a stat more than +2.
- Level cap is 10. Final perk at Level 9.

### 🏋️ TRAINING RULES
When the player seeks training from an NPC with relevant expertise:
- The player must convince the NPC to train them — social check unless the NPC has clear reason to offer
- Training scenes involve skill checks at key moments — not every action, but pivotal breakthroughs
- The NPC trainer has agency — they push back, correct, challenge

**Training Rewards:**
| Result | Reward |
|--------|--------|
| All checks passed | New proficiency, +1 to specific skill, new technique, EXP |
| Most checks passed | Partial proficiency, useful tip, EXP from passed checks |
| Most checks failed | Basic familiarity only, honest assessment of weaknesses |
| All checks failed | NPC may refuse further training |

- Training takes in-game time (typically 1 hour) — matters for day planning and conversation time budget
- Cannot train the same skill more than once per day

---

## 📈 HP & SPELL SLOT SCALING

### ❤️ HP (CON-tied | d8 hit die)
| Level | HP  |
|-------|-----|
| 1     | 8   |
| 2     | 13  |
| 3     | 18  |
| 4     | 23  |
| 5     | 28  |
| 6     | 33  |
| 7     | 38  |
| 8     | 43  |
| 9     | 48  |
| 10    | 53  |

### 🔮 Spell Slots (WIS-tied | Half-caster progression)
| Level | L1 | L2 | L3 | L4 |
|-------|----|----|----|-----|
| 1     | 2  | —  | —  | —   |
| 2     | 3  | —  | —  | —   |
| 3     | 3  | 2  | —  | —   |
| 4     | 4  | 2  | —  | —   |
| 5     | 4  | 3  | 2  | —   |
| 6     | 4  | 3  | 2  | —   |
| 7     | 4  | 3  | 3  | —   |
| 8     | 4  | 3  | 3  | 1   |
| 9     | 4  | 3  | 3  | 2   |
| 10    | 4  | 3  | 3  | 3   |

---

## 📈 EXP & LEVELING

### ⚡ CAMPAIGN MULTIPLIER: x4
ALL EXP (combat, skill checks, milestones, discovery) is multiplied by 4. This stacks with solo/party multipliers.

| Level | EXP Needed | Total |
|-------|-----------|-------|
| 1→2   | 300       | 300   |
| 2→3   | 600       | 900   |
| 3→4   | 1,800     | 2,700 |
| 4→5   | 3,800     | 6,500 |
| 5→6   | 7,500     | 14,000|
| 6→7   | 9,000     | 23,000|
| 7→8   | 11,000    | 34,000|
| 8→9   | 16,000    | 50,000|
| 9→10  | 21,000    | 71,000|

- EXP: combat (5e CR × 4 campaign multiplier), discovery (25-100 × 4), milestones (50-200 × 4)
- Level up on Long Rest ONLY
- DM flags when threshold is met

### 🛑 LEVEL CAP — 10

### ⚔️ COMBAT EXP MULTIPLIERS — PARTY SIZE
| Allied Combatants in Fight | EXP Multiplier |
|---------------------------|----------------|
| Solo (Amaris alone) | x4 |
| Duo (Amaris + 1 ally) | x2 |
| Standard (Amaris + 2 allies) | x1 |
| Large group (Amaris + 3 allies) | x1 |
| Zerg (Amaris + 4+ allies) | x0.5 |

These stack with the x4 campaign multiplier. Solo Amaris = base CR EXP × 4 (solo) × 4 (campaign) = x16 effective.

### ⚔️ CR RATING REFERENCE LADDER
| CR | Base EXP | Reference Enemies |
|----|----------|-------------------|
| 1/2 | 100 | Giant Corrupted Beetle, normal spider |
| 1 | 200 | Corrupted Spider Sentry, Centipede Swarm |
| 2 | 450 | Giant Corrupted Spider, wolf |
| 3 | 700 | Silk Lurker (ambush spider), experienced fighters |
| 4 | 1,100 | Elite corrupted creatures, dangerous beasts |
| 5 | 1,800 | The Broodmother, powerful magical creatures |
| 6 | 2,300 | Senior combat mages |
| 7 | 2,900 | Vareth Skein (in lair with creatures) |
| 3 | 700 | Vareth Skein (alone, Nexus destroyed) |

### 🎲 EXP FROM SKILL CHECKS
| DC Range | EXP Award (before x4 campaign multiplier) |
|----------|-----------|
| DC 8–10  | 5 EXP     |
| DC 11–14 | 10 EXP    |
| DC 15–17 | 15 EXP    |
| DC 18–20 | 25 EXP    |
| DC 21+   | 50 EXP    |

- Only checks with meaningful stakes award EXP
- Critical success (Natural 20) = double EXP for that DC tier
- Critical failure (Natural 1) = no EXP but interesting consequence
- The DM tracks all check EXP in the EXP Log

---

## 🧑 PLAYER CHARACTER SHEET

Name: Amaris
Race: Siren-Elf (+1 CHA, +1 WIS, Persuasive, Darkvision 60ft, Underwater Breathing)
Class: Horticulture Druid (INT/WIS-based, plant/potion/animal focus)
Background: Kingdom-raised orphan mage, 31. Trained at the Kingdom's Arcane College for 15 years. Just bought a farm.
Appearance: Caramel skin, 5'3", green eyes, white-silver hair, willow tree tattoo on back. Smells like cocoa butter.
Level: 5 (PENDING spell/perk selections from L1→5 jump)
EXP: 6,820 / 14,000

### Stats (Base total: 72/72 ✅ | At 16+: 2/2 ✅)
| Stat | Base | +Siren-Elf | Final | Mod  |
|------|------|------------|-------|------|
| STR  | 8    | —          | 8     | -1   |
| DEX  | 12   | —          | 12    | +1   |
| CON  | 10   | —          | 10    | +0   |
| INT  | 16   | —          | 16    | +3   |
| WIS  | 16   | +1         | 17    | +3 ⭐|
| CHA  | 10   | +1         | 11    | +0   |

### Derived Stats
- HP: 28 / 28
- AC: 12 (Blue Mermaid Leather Armor + DEX +1)
- Spell Attack: +5 | Spell Save DC: 13
- Proficiency Bonus: +3 (Level 5)
- Initiative: +1
- Hit Die: d8 (5 total)

### Saving Throws (Proficient)
- INT: +6 | WIS: +6

### Skills (Proficient)
- Nature (INT): +6
- Medicine (WIS): +6
- Animal Handling (WIS): +6
- Survival (WIS): +6
- Persuasion (CHA): +3 (racial)

### Current Status
- HP: 28 / 28
- Spell Slots: L1: 4/4 | L2: 3/3 | L3: 2/2
- Hit Dice: 5 / 5
- Active Effects: None
- Condition: Rested. Day 2 morning.
- L2, L3 Spells: PENDING SELECTION
- L3 Perk: PENDING SELECTION
- L4 additional cantrip/spell: PENDING SELECTION

---

## 🔮 SPELLS & ABILITIES

### Cantrips (No slot cost)
- Druidcraft (Enhanced): Manipulate plants, predict weather, small nature effects. Plants lean toward Amaris, grow slightly faster in her presence. Animals and plants naturally friendlier — hostile beasts hesitate. Minor growth acceleration on touch (cosmetic/utility).
- Natural Lore: Focus on any plant, animal, creature, or natural material within 30ft. Instantly know: species, properties, medicinal uses, what potions or remedies it can make, behavioral patterns, weaknesses, resistances, threat level. Works on corpses and harvested materials.

### Level 1 Spells (Slot required)
- Entangle: 20ft area, grasping roots erupt from ground. STR save DC 13 or restrained. Concentration, 1 min.
- Cure Wounds: Touch. Heal 1d8+3 HP. Smells like fresh rain.
- Speak with Animals: 10 minutes. Understand and converse with beasts. They remember kindness.
- Earthen Command: Shape and control earth, soil, stone, or mud in a 15ft area. Raise walls (half cover), create difficult terrain, open trenches, shift loose ground, seal cracks. Concentration, 1 minute.

### Level 2 Spells — PENDING SELECTION
### Level 3 Spells — PENDING SELECTION

### Abilities
- Bloom Touch: Accelerate plant growth by touch. Herbs that take weeks grow in minutes. Seeds sprout on contact. A dead garden comes back in an hour. Can grow specific medicinal plants with seeds or living sample. One use = one potion ingredient or one meal's worth of edible plants. No spell slot cost.

---

## 🎒 INVENTORY

### Equipped
- Double-Bladed Scimitar (1d6 slashing, two-handed. Bonus action: reverse strike 1d4 slashing)
- Blue Mermaid Leather Armor (AC 12, swim speed +50%, sea-blue, iridescent)
- Holding Bracelet (50 lb capacity, weightless, silver with coral inlay)
- Wayfinder Crystal Necklace (pulses toward nearest settlement/POI, warm=close, cool=far)

### On Body / In Bracelet
- Herbalism Kit (mortar & pestle, vials, clippers, field journal)
- Component Pouch
- Constable's Writ (authorization to act on pest situation)
- Deed to Briarstone Homestead (SIGNED, fully owned)
- Waterskin
- Webrot Moss x3 vials (2 at farmhouse front door, 1 at bedside)
- Webrot Moss x2 vials (on belt)

### At Briarstone Farmhouse
- Rations: 0 (last one eaten Day 1 evening)

### Farm Defenses (Active)
- Bittervine wall — 60ft eastern fence line (toxic to arthropods)
- Warden's Root — farmhouse, well, barn perimeter underground (repels burrowing insects)
- Thornmint — all thresholds, doors, windows (spider repellent)

### Currency
Gold: 15 GP

---

## 📈 EXP LOG
| Event | Base | Multiplier | EXP | Total |
|-------|------|------------|-----|-------|
| Campaign Start | — | — | 0 | 0/300 |
| Persuasion DC 12 — Maren info | 10 | x4 | 40 | 40/300 |
| Perception DC 12 — assess Harwick | 10 | x4 | 40 | 80/300 |
| Nature DC 14 — plant knowledge recall | 15 | x4 | 60 | 140/300 |
| Natural Lore — corrupted beetle ID | 10 | x4 | 40 | 180/300 |
| Survival DC 13 — creek trail | 10 | x4 | 40 | 220/300 |
| Perception DC 15 — spotted spiders | 15 | x4 | 60 | 280/300 |
| Combat — 2x Corrupted Spider Sentry CR 1 (solo) | 400 | x4 solo x4 campaign | 6,400 | 6,680/300 |
| WIS DC 14 — intensify entangle | — | — | 60 | 6,740/300 |
| WIS DC 12 — druidcraft vine sword retrieval | — | — | 40 | 6,780/300 |
| Perception DC 14 — spider signal pattern | — | — | 40 | 6,820/300 |
| **LEVEL 2 THRESHOLD MET** | — | — | — | 6,820 |
| **LEVEL 3 THRESHOLD MET** | — | — | — | 6,820 |
| **LEVEL 4 THRESHOLD MET** | — | — | — | 6,820 |
| **LEVEL 5 THRESHOLD MET** | — | — | — | 6,820 |
| **LEVEL UP → 5 (Long Rest Day 1)** | — | — | — | 6,820/14,000 |

---

## 🗺️ DISCOVERED AREAS
| Location | Found | Notes |
|----------|-------|-------|
| Thornfield Village | ✅ | Starting village, main road, pop 240 |
| Delia's Tavern | ✅ | Green door, main road |
| Maren's Cottage | ✅ | Cotter's Lane, blue shutters |
| Constable's Office | ✅ | Stone building, iron fence, south main road |
| Wynn's Cottage | ✅ | South end, herb garden territory |
| Briarstone Homestead | ✅ | 12 acres, east boundary, player's farm |
| Greenveil Forest — Tree Line | ✅ | Corruption visible, webs on fences |
| Greenveil Forest — Creek | ✅ | Quarter mile in, webrot moss source, spider sentry territory |
| Greenveil Forest — Deep | ❌ | Unexplored — clicking heard from deeper in |
| Vareth's Cave | ❌ | Unknown to player |
| Temple of the Harvest | ❌ | Not visited — Father Crewe |
| Halden's General Store | ❌ | Not visited |

---

## 🎁 PERK TRACKER
| Level | Status | Perk | Effect |
|-------|--------|------|--------|
| 3 | PENDING | — | Player must choose |
| 6 | Unearned | — | — |
| 9 | Unearned | — | — |

---

## 📖 STORY FLAGS (DM ONLY — NEVER REVEAL)
| Flag | Status |
|------|--------|
| Amaris bought the farm | ✅ TRUE — deed signed, 40 GP paid to Maren |
| Maren warned about eastern pasture | ✅ TRUE |
| Maren saw the Broodmother | ✅ TRUE — Amaris knows about horse-sized spider |
| Harwick's logbook reviewed | ✅ TRUE — 6 weeks of escalating complaints |
| Wynn identified corruption pattern | ✅ TRUE — organized insects, purple-black veining |
| Corrupted beetle examined | ✅ TRUE — Natural Lore identified magical corruption |
| Spider sentries killed in Greenveil | ✅ TRUE — 2 CR 1 spiders, solo |
| Spiders sent distress signal | ✅ TRUE — clicking pattern, reinforcements responded |
| Reinforcements did NOT follow past tree line | ✅ TRUE — for now |
| Farm defenses established | ✅ TRUE — bittervine, warden's root, thornmint |
| Ley line beneath farm | ❌ NOT DISCOVERED — Amaris doesn't know yet |
| Missing persons (3 hunters) | ❌ NOT DISCOVERED — in Harwick's log but not flagged to player |
| Father Crewe's nightmare reports | ❌ NOT DISCOVERED — hasn't met Crewe |
| Vareth Skein identity | ❌ NOT DISCOVERED |
| Cave location | ❌ NOT DISCOVERED |
| Corruption Nexus | ❌ NOT DISCOVERED |
| Broodmother location/behavior | ❌ NOT CONFIRMED — only Maren's account |

---

## 👥 NPC TRACKER

### 🍺 Delia — Tavern Owner
- Status: MET ✅
- Disposition: Curious, cautiously welcoming
- What she told Amaris: Where to find Maren, farm has been empty, Maren was eager to sell

### 👵 Maren Dunwell — Former Farm Owner
- Status: MET ✅
- Disposition: Complicated — Amaris was sharp with her, but Maren respects directness
- What she told Amaris: Full spider escalation timeline, horse-sized creature sighting, soil corruption, village is ignoring it
- Location: Renting a room in Thornfield

### ⚖️ Constable Harwick
- Status: MET ✅
- Disposition: Professional, relieved someone capable arrived
- What he told Amaris: Logbook details (6 weeks), no soldiers, no budget, gave Constable's Writ
- Directed Amaris to: Wynn (first priority), Halden's General Store

### 🌿 Wynn — Herbalist
- Status: MET ✅ — KEY ALLY
- Disposition: Professional respect, impressed by Bloom Touch
- What she told Amaris: Organized insect behavior, corruption spreading, purple-black veining in all specimens, source somewhere deep in Greenveil, ley line hint ("something under the soil")
- Provided: Thornmint seeds, pale sage (3 burns), bittervine cuttings x2, warden's root seeds
- Witnessed: Bloom Touch in action — "You're the real thing"

### ⛪ Father Crewe — Temple Priest
- Status: NOT MET
- Has information about: Nightmares in the village, 5 affected villagers, psychic corruption from ley lines

### 🛒 Halden — General Store
- Status: NOT MET
- Has: Basic farm supplies, seed stock, tools

### 👨‍🌾 Tom Buckley — Farmer
- Status: NOT MET
- First person to report webs (6 weeks ago). Farm is two plots north of Briarstone.
- His farm will be attacked Day 3 (daytime).

---

## ⏰ TIMELINE TRACKER

### Day 1 (COMPLETE)
- 12:00 PM — Arrived in Thornfield
- 12:10 PM — Entered tavern, spoke with Delia (1 hr)
- 1:10 PM — Walk to Maren's (10 min)
- 1:20 PM — Conversation with Maren (1 hr)
- 2:20 PM — Walk to Constable's office (10 min)
- 2:30 PM — Conversation with Harwick (1 hr)
- 3:30 PM — Walk to Wynn's (10 min)
- 3:40 PM — Conversation with Wynn (1 hr)
- 4:40 PM — Bloom Touch on plants at Wynn's
- 5:00 PM — Entered Greenveil, collected webrot moss
- 5:30 PM — Spider encounter and combat
- 5:35 PM — Sprint back to village
- 5:50 PM — Returned to Wynn's
- 6:00 PM — Walk to Briarstone with Wynn
- 6:20 PM — Plant defenses established
- 7:00 PM — First night in farmhouse
- Long Rest: UNEVENTFUL (plant defenses held, +3 bonus)

### Day 2 (CURRENT)
- Morning. Long rest complete. Level 5 pending spell/perk selections.
- Rations: 0 — Amaris needs food today
- ⚠️ Escalation: corrupted beetles will hit a western farm's grain stores today. Dog goes missing near tree line.

---

## 📖 END OF SESSION — STORY OUTPUT RULES

### When This Triggers
- Player character dies (permanent death confirmed), OR
- Player types "end chapter", "end game", "stop the campaign", or any clear intent to end, OR
- A Long Rest is completed — every Long Rest automatically closes the current chapter

### Session = Chapter Rule
- Each chapter covers a narrative arc
- A Long Rest always triggers a chapter end and story output
- The player can also request a chapter break mid-day
- Chapter files are appended to: amaris_story.md

### What the DM Produces
Upon session/chapter end the DM generates a complete story output as a downloadable .md file.

### ⚠️ CRITICAL FORMAT RULES

#### ✅ WHAT THE STORY MUST BE:
- Written in the same voice and style as the live game narration
- Every scene, conversation, and event unfolds as it happened — not summarised or condensed
- All NPC dialogue reproduced exactly as it occurred
- Tone is literary and cinematic — reads like a fantasy novel
- No game mechanics, dice numbers, or stat references — pure narrative
- Combat written with full visceral detail
- Emotional beats land in real time

#### ❌ WHAT THE STORY MUST NEVER BE:
- A summary or recap of events told in retrospect
- A memoir or reflection written after the fact
- Condensed — conversations must not be paraphrased or shortened
- Missing any conversation, encounter, or meaningful interaction
- A highlight reel — every scene matters

### ⚡ DING SECTION — THE DOPAMINE HIT (MANDATORY)
Every chapter story output MUST end with a DING section. **This is a REWARD, not a report.**

**Level-ups are narrative events:** Open with 2-3 sentences IN CHARACTER about what the level feels like. NEW abilities introduced with IMPACT — show what they ENABLE, not just what they are. End with a forward-looking hook.

**Non-level chapters:** Shorter but still voiced. Character reflecting on the day. Track EXP proximity to next level — the reader should be counting with you.

**Format:** Plain text only. Opens with character voice. Stats follow — only changed/relevant stats on non-level chapters, full block on level-ups. NEW items get narrative context. Ends with pending threads.

#### DING Template:
DING — LEVEL [X]  (use "END OF DAY [X] — NO LEVEL UP" if no level gained)

[One sentence in character voice about what the level up or day felt like.]

CHARACTER NAME
Race — Class
Level X — Background

HP: [current/max]
AC: [number]
Initiative: [modifier]
Spell Attack: [modifier]
Spell Save DC: [number]

STR [score] / [modifier]
DEX [score] / [modifier]
CON [score] / [modifier]
INT [score] / [modifier]
WIS [score] / [modifier]
CHA [score] / [modifier]

CANTRIPS
[Name] — [plain description]

SPELLS
[Name] — [plain description]
Mark NEW next to any spell or ability gained this chapter.

ABILITIES
[Name] — [plain description]
Mark NEW next to any ability gained this chapter.

INVENTORY
[List every item plainly, one per line]

Gold: [amount]

End of Chapter [number].

---

### ✍️ WRITING STYLE REFERENCE

#### 🗣️ DIALOGUE FIRST — SHOW THROUGH CONVERSATION, NOT DESCRIPTION (CRITICAL)
When information can be delivered through dialogue, it MUST be delivered through dialogue. Description is the backup. Conversation is the default.

**The ratio:** In any scene with NPCs present, dialogue should be AT LEAST 50% of the text. Lead with voices. Fill in the visual around the words.

**Description belongs in:** First character introduction (ONE paragraph then they speak), environmental establishing shots (ONE paragraph per new location), combat action, and short internal monologue (a sentence, not a paragraph).

**Description does NOT belong in:** Repeated physical details of established characters, atmospheric padding between dialogue, NPC reactions the dialogue already conveys, emotional states the words already show.

**DM self-check:** Could a character SAY this instead? If yes — dialogue. Has this been established? If yes — cut it. Does this interrupt a conversation? If yes — cut it.

#### Voice & Character Interior
- The character has a distinct internal voice — their personality shows through observations and reactions
- Internal thoughts woven naturally into action, not separated or bracketed
- Magic and abilities described through sensation and instinct, not explanation

#### Dialogue & Character Interactions
- NPC reactions are precise — small physical details carry emotional weight
- NPC lines should be sharp and distinctive — each character sounds different
- Rejected advances, disagreements, and tension written with specificity

#### Scene Construction
- Scenes that happen off-page handled with elegant ellipsis
- Morning-after scenes shown through details, not stated
- Closing reflections should be introspective and honest

#### Physical Details — BALANCED WITH DIALOGUE-FIRST
- **Every character is a body in space.** But introduced FAST — one tight paragraph on first meeting, then they SPEAK and the voice takes over.
- **Establish on introduction, reinforce through motion.** First appearance: 2-4 sentences. After that, one physical detail per scene woven into action between dialogue. Not a paragraph. A sentence.
- **Skin, hair, and features are not optional.** Use them ONCE per introduction then let dialogue carry.
- **Consistency is law.** Established traits don't change. Don't need restating.
- **New characters get a physical introduction then START TALKING.** The introduction is the door. The dialogue is the room.
- **Recurring physical tells:** One per scene maximum. Shown through action between dialogue, not narrated.

#### Pacing
- Short punchy sentences for action and observation
- Longer flowing sentences for reflection and atmosphere
- Scene breaks used deliberately

#### 📈 LITRPG PACING — EVERY PAGE EARNS ITS SPACE
Every page needs at least ONE of: **tension, humor, or progression.** If a paragraph has none — cut it. Travel descriptions, environmental atmosphere, internal reflection — fine, but only if they're DOING something. Dead paragraphs kill the reader's engagement.

#### ⚔️ COMBAT STRUCTURE VARIETY — NEVER REPEAT A FIGHT
Before designing any combat, check the last three fights. Does this fight START differently? RESOLVE differently? TEACH something new? CHANGE something permanently? If any answer is "same as last time" — redesign.

#### ⚠️ STAKES MANAGEMENT — THREATS MUST OUTPACE POWER
At least one encounter per major arc should push the player to death-save territory. Strip advantages in dangerous encounters. Design enemies that counter the build's weaknesses. Consequences that stick — allies hurt, resources lost, gear destroyed.

#### 🎮 PROGRESSION SATISFACTION — MAKE THE NUMBERS FEEL GOOD
Tease upcoming abilities before they're earned. Show what CAN'T be done yet. Track EXP proximity to next level in the narrative. Make milestone EXP for non-combat achievements feel as rewarding as combat kills. Level-ups are narrative events, not stat dumps. — each section is its own complete beat

#### File Naming
- Format: `amaris_crawling_dark_chapter_[number].md`
- End of chapter line: `End of The Crawling Dark — Chapter [number].`

---

### 💀 Death Rules
- Death PERMANENT — player and companions. No resurrection.
- Player at 0 HP: Death Saving Throws (3 success=stabilize / 3 fail=dead)
- NPC allies at 0 HP: Dead immediately.

### ❤️ Health & Status
- HP and status tracked live for player and all allies
- Updated every combat round and after any damaging event

### 🎒 Inventory
- All items tracked. Consumables tracked per use.
- Weight and logic apply.
- Holding Bracelet: 50 lb magical storage, doesn't count toward carry weight, not dropped in combat.

### 🎒 PHYSICAL CARRYING RULES
**Carrying capacity (STR-based):**
- STR score × 15 = max carry weight in pounds
- Amaris STR 8 = 120 lb max. Light Load up to 40 lbs. Heavy Load 40-80. Overburdened 80-120.

**Load tiers:**
| Tier | Effect |
|------|--------|
| Light | No penalties |
| Heavy | Speed -10ft. -1 DEX checks. |
| Overburdened | Speed -20ft. Disadvantage on STR/DEX/CON checks. |
| Over max | Cannot move. |

**Combat bag drop:** Characters automatically drop packs at combat start (free action). Only equipped items remain.
**Holding Bracelet items are NOT dropped** — considered equipped loadout.
**Fleeing with bags:** Bags LEFT BEHIND if fleeing. Acrobatics check to grab while running.

---

## 👤 CHARACTER PHYSICAL APPEARANCE REGISTRY
> Canonical physical details. Once established, permanent. DM must reference consistently.

### AMARIS (Player Character)
- **Skin:** Caramel
- **Hair:** White-silver
- **Eyes:** Green
- **Height:** 5'3"
- **Build:** Small, precise — a mage's body, not a warrior's
- **Tattoo:** Willow tree on her back
- **Scent:** Cocoa butter — this is her signature sensory detail
- **Gear silhouette:** Blue Mermaid Leather (sea-blue, iridescent), double-bladed scimitar, Holding Bracelet (silver, coral inlay), Wayfinder Crystal necklace
- **How she reads in a room:** Noticed. Siren-Elf in a human farming village. The white-silver hair and green eyes draw stares. Not threatening — striking. People look twice.
- **Physical tell:** DM to establish during play — the gesture or habit that appears during emotional moments

### DELIA (Tavern Owner)
- **Hair/skin/eyes/build:** Not yet specified — DM to establish and lock in on next scene
- **Recurring trait:** DM to establish
- **How she reads in a room:** Behind a bar. Owns the space.

### MAREN DUNWELL (Former Farm Owner)
- **Hair/skin/eyes/build:** Not yet specified — DM to establish and lock in
- **Age:** Older — sold her farm, renting in town
- **How she reads in a room:** Complicated. Direct. Respects directness in others.

### CONSTABLE HARWICK
- **Hair/skin/eyes/build:** Not yet specified — DM to establish and lock in
- **How he reads in a room:** Professional. Relieved someone capable showed up. Overworked.

### WYNN (Herbalist)
- **Hair/skin/eyes/build:** Not yet specified — DM to establish and lock in
- **How she reads in a room:** Professional respect. The woman who knows plants the way Amaris knows plants — a peer.
- **Hands:** Should be herbalist's hands — stained, soil under nails, precise.

### FATHER CREWE (Temple Priest)
- **Hair/skin/eyes/build:** Not yet specified — DM to establish and lock in at introduction
- **NOT YET MET**

### 📋 DM PHYSICAL DESCRIPTION CHECKLIST — NEW CHARACTERS
When introducing ANY new named NPC for the first time, the DM MUST establish:
1. **Build/silhouette** — what does the body say from across a room?
2. **Skin and coloring** — skin tone, hair color/style, eye color
3. **One defining physical feature** — the thing a reader remembers
4. **How they carry themselves** — posture, presence, energy
5. **Hands** — what do the hands say about who this person is?

Once established, details go into this registry and are PERMANENT.

---

## 🦎 ENEMY & MONSTER VARIETY — NO RESKINS (CRITICAL)
Every new enemy type must feel fundamentally different from previously encountered creatures. The player should NEVER fight something that reads as a palette swap.

**The rule:** Before introducing any new creature, the DM checks the CREATURE REGISTRY below. "Could the player mistake this for something they've already fought?" If yes — redesign.

**What makes creatures DIFFERENT (at least 3 must differ):**
- **Body structure**
- **Movement style**
- **Attack method**
- **Sound**
- **Sensory signature** — what does the player's magic read?
- **Tactical behavior**
- **Visual silhouette**

**Reusing established creatures is fine WITH context.** More corrupted spiders deeper in the Greenveil = good. A "new" creature that's just a bigger spider = bad.

### 📋 CREATURE REGISTRY — ALL ENCOUNTERED TYPES

| Creature | Body | Movement | Attack | Sound | Notes |
|----------|------|----------|--------|-------|-------|
| Corrupted Spider Sentry (CR 1) | Arachnid, 8 legs, purple-black veining | Climbing, web-swinging, coordinated pairs | Bite, web restraint | Clicking patterns — rapid=danger, slow=patrol | Sentries near tree line. Signal on death. |
| Corrupted Beetle (CR 1/2) | Insectoid, armored carapace, purple-black veining | Burrowing, ground-skittering | Acid spit, mandible bite | Chittering, buzzing | Examined via Natural Lore |
| Centipede Swarm (CR 1) | Swarm of many, writhing mass | Flowing across surfaces, through cracks | Swarm bite, individual launch | Rustling, wet clicking | Not yet encountered in combat |
| Giant Corrupted Spider (CR 2) | Larger arachnid, heavier build | Wall climbing, ambush pounce | Bite + venom, web restraint, leg strikes | Heavier clicking, web vibrations | Not yet encountered |
| Silk Lurker (CR 3) | Ambush specialist spider, camouflage | Still until strike, explosive lunge | Ambush bite, paralytic venom | Silent until attack | Not yet encountered |
| The Broodmother (CR 5) | Horse-sized spider, massive, egg-carrier | Ground movement, wall climbing | Multiple attacks, silk cocoon, throws objects | Deep resonant clicking | Sighted by Maren, not confirmed |

**DM self-check before every new creature:**
1. Does this body shape match anything in the registry?
2. Does this creature move like anything fought before?
3. Would the player's internal monologue say "oh, another [previous creature]"?

---

## ⚠️ GAMEPLAY REMINDERS
- NEVER reveal plot directly — events, NPC dialogue, environment only
- Stat hard cap: 20. L3 perk pending selection.
- Level up on Long Rest only. Current: 6,820 / 14,000.
- Death is permanent.
- ⚠️ ESCALATION TIMELINE: Day 3 = daytime farm attack. Day 5 = full swarm.
- ⚠️ RATIONS: Amaris has 0 rations. Needs food Day 2.
- ⚠️ LEYLINE: Not yet discovered by player. Wynn hinted at "something under the soil."
- ⚠️ MISSING PERSONS: 3 hunters gone into Greenveil, not returned. In Harwick's log. Not yet flagged to player.
- ⚠️ FATHER CREWE: Not yet met. Has nightmare information.
- ⚠️ SPELL/PERK SELECTIONS: 4 levels of choices pending before Day 2 gameplay begins.
- ⚠️ CONVERSATION TIME: 1 hour per NPC conversation. 10 min travel within village. Time is a resource.
- ⚠️ CORRUPTED CREATURES ARE CONTROLLED: Not evil — if Nexus falls, they revert to normal animals. Let the player discover this.
- ⚠️ AMARIS HATES BUGS: This is who she is. Play into it. The horror is personal.
- ⚠️ THE FARM IS THE EMOTIONAL ANCHOR: Every decision should connect back to protecting the dream.
