# Character Tracker — [CAMPAIGN NAME] TTRPG

<!-- HEADER — Update these fields at the start of each session -->
**Current In-Game Date:** [date and time]
**Current Location:** [region or settlement — specific location]
**Active Book:** [Book # — Book Name]

---

<!-- 
TRACKING OVERVIEW:
This template follows the mandatory rules in tracking_rules.md. Every character entry must:
1. Have a clear status (alive, MIA, or dead)
2. Include timestamp (last_updated) on every significant change
3. Contain at least one active goal if status is "alive"
4. Track disposition toward the protagonist (the player character)
5. Record all gear, abilities, and important mechanics

This file is a living document. Characters are NEVER deleted — only updated or marked MIA/dead.
See tracking_rules.md for operating rules and file structure documentation.
-->

---

## [PROTAGONIST NAME] — [Class/Title] / [Optional Subclass/Epithet]

<!-- 
PC SECTION:
This is the player character. Track level, location, inventory, gold, and active goals.
Disposition for the PC is always N/A since they are the narrative anchor.
Reference npc_appearance.md for detailed physical description if needed.
-->

**Status:** alive
**Level:** [#]
**Location:** [region — specific location]
**Last Updated:** [date]

**Physical:** See npc_appearance.md (or local description)
**Disposition:** N/A (protagonist)

**Abilities:** [Ability 1, Ability 2, Ability 3, ...]

**Important Gear:** [Item 1, Item 2, Item 3, ...]

**Gold:** [amount in copper/silver/gold]

### Active Goals

<!-- 
GOAL TABLE STRUCTURE:
- goal_id: unique kebab-case identifier for the goal
- opened: date goal was added to the tracker
- due_date: when the goal completes in the world (whether PC is present or not)
- public_at: when information about goal becomes available for NPCs to reference
- status: in_progress, complete, dormant, or failed
- description: what needs to happen
- completion_effects: what changes when this goal resolves

See tracking_rules.md Rule 4 for timer guidance and common-sense due date estimates.
-->

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| [goal_id_1] | [date] | [date] | [date] | in_progress | [What needs to happen?] | [What changes when complete?] |
| [goal_id_2] | [date] | [date] | [date] | in_progress | [What needs to happen?] | [What changes when complete?] |

---

## [ALLY NPC NAME] — [Class/Title]

<!-- 
NPC SECTION — ALLY EXAMPLE:
Track all NPCs the PC interacts with significantly. Include allies and antagonists.
Disposition shows the NPC's view of the PC (not the PC's view of them).
Last_updated timestamps every significant change (disposition shift, gear acquisition, goal opened, etc.)
-->

**Status:** alive
**Location:** [region — specific location]
**Last Updated:** [date]

**Physical:** [Brief description or reference to npc_appearance.md]
**Disposition to [PC Name]:** [How they feel/view the PC. Include relevant mechanical state if intimate/bonded.]

**Abilities:** [Ability 1, Ability 2, Ability 3, ...]

**Important Gear:** [Item 1, Item 2, ...]

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| [goal_id_1] | [date] | [date] | [date] | in_progress | [What does this NPC need to do?] | [What changes when complete?] |

**NOTES:** [Any mechanical rules, personal quirks, or hooks relevant to this character.]

---

## [ANTAGONIST NPC NAME] — [Class/Title]

<!-- 
NPC SECTION — ANTAGONIST EXAMPLE:
Antagonists get the same tracking structure as allies. Include their goals, abilities, and disposition.
Remember: disposition is their view of the PC, not the player's moral judgment of them.
-->

**Status:** alive (or presumed — if location unknown)
**Location:** [region or "unknown" if not currently locatable]
**Last Updated:** [date]

**Physical:** [Brief description]
**Disposition to [PC Name]:** [How they regard the PC. Hostile? Curious? Indifferent?]

**Abilities:** [Ability 1, Ability 2, Ability 3, ...]

**Important Gear:** [Item 1, Item 2, ...]

### Active Goals

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| [goal_id_1] | [date] | [date] | [date] | in_progress | [What does this antagonist want?] | [What happens if they succeed?] |

**NOTES:** [Mechanical hooks, behavioral patterns, or strategic intelligence about this character.]

---

## BOOK STUBS — Previous Campaign Characters

<!-- 
STUBS SECTION:
When a campaign ends (Book 1 complete, Book 2 starts, etc.), preserve characters from the previous book
in a condensed format. Include just enough data to reactivate them later without needing to re-read old sessions.
Status changes to MIA and goals pause until the thread reactivates.

Format: Minimal line for each character. Use book_#_endgame_tracker.md as the full reference.
-->

### [Previous Book Name] Characters (status: mostly MIA)

- **[Name] — [Class/Title]** | Status: [alive/dead] | Last Updated: [book end date] | Notes: [one-line summary of current situation]
- **[Name] — [Class/Title]** | Status: [alive/dead] | Last Updated: [book end date] | Notes: [one-line summary of current situation]

---

## FLAGGED ISSUES

<!-- 
FLAGGED ISSUES:
Use this section to mark story-critical uncertainties or timer concerns that need DM attention.
Examples:
- A character's research/plan may have unintended consequences
- A clock's rate or trigger condition is unclear
- An NPC's psychological state may shift unexpectedly
- A goal's due_date may conflict with another goal
- A piece of gear or ability has unresolved mechanics

Review this section before each session. Resolve or clarify before prose continues.
Do NOT leave items flagged without a plan for resolution.
-->

- [Issue 1: brief description of what's uncertain]
- [Issue 2: brief description of what's uncertain]

---

---

## THE WORLD — Tracked as a Character

<!-- 
THE WORLD SECTION:
The campaign setting is tracked as a character. This captures the world's "mood," the passage of seasons,
political/environmental shifts, and how the world reacts to the PC's presence and actions.

Use this to ground descriptions in current world state and avoid anachronisms or forgotten context.
Update Physical Features, Disposition, and World Goals regularly.
-->

**Status:** alive
**Last Updated:** [date]

### Physical Features

<!-- 
PHYSICAL FEATURES:
The world's tangible state. What characters see and experience.
Update this section as seasons change, wars progress, cities recover/decline, etc.
-->

- **Season:** [season name] [progress indicator — e.g., "early," "deepening," "approaching end"]
- **Weather:** [current conditions]
- **[Region 1]:** [current state — settlement, military situation, environmental condition, etc.]
- **[Region 2]:** [current state]
- **[Key Location/Faction]:** [current state]

### Disposition to [PC Name]

<!-- 
DISPOSITION TO PC:
How the world responds to the PC's presence. Does the land flourish under their power?
Does undeath feel at home when they're near? This is mechanically tied to the PC's class/powers.

Different "modes" (creation, entropy, disguised) produce different world reactions.
Use this section to explain what NPCs observe about the PC's effect on reality.
-->

[Explain the world's reaction to the PC. How does the PC's nature/actions influence the physical and political landscape? What do NPCs intuit about the PC's presence?]

### World Goals — Events & Seasonal Changes

<!-- 
WORLD GOALS:
Major recurring events, seasonal transitions, faction movements, political shifts.
These are not the PC's goals — these are things that happen in the world regardless of the PC's involvement.
Track them separately so they can be triggered at the right time.
-->

| goal_id | opened | due_date | public_at | status | description | completion_effects |
|---------|--------|----------|-----------|--------|-------------|--------------------|
| [event_id_1] | [date] | [date] | [date] | in_progress | [What's happening in the world?] | [How does this change the setting?] |
| [event_id_2] | [date] | [date] | [date] | in_progress | [What's happening in the world?] | [How does this change the setting?] |

### Campaign Goals — Overarching Threats/Conflicts

<!-- 
CAMPAIGN GOALS (Optional):
Some campaigns track overarching threats as "campaign clocks" — existential risks or major story arcs
that progress independently of the PC's actions but can be influenced by them.

Clock mechanics:
- clock_start: when the threat began escalating (may be dormant/hidden)
- rate: percentage progress per in-game day/week/season
- current_%: where the clock stands now
- critical_at: the percentage where the threat becomes irreversible or reaches crescendo
- status: dormant (hidden/not yet triggered), active (clock running), or resolved

Use this if your campaign has multiple parallel threats competing for resolution.
Otherwise, omit this table and track major plot arcs as NPC goals instead.
-->

| goal_id | clock_start | rate | current_% | critical_at | status | description | completion_condition |
|---------|-------------|------|-----------|-------------|--------|-------------|---------------------|
| [threat_1] | [date or "dormant"] | [rate] | [%] | [%] | [status] | [What is the threat?] | [How is it resolved?] |
| [threat_2] | [date or "dormant"] | [rate] | [%] | [%] | [status] | [What is the threat?] | [How is it resolved?] |

---

---

## CONSOLIDATION NOTES

<!-- 
CONSOLIDATION:
This footer tracks when the tracker was last updated and from what source material.
Update this at the end of each session or chapter consolidation pass.
Use format: "Date. Source: [session #/chapter name/prose range]"
-->

*Last full consolidation: [date], [Book/Campaign name]. Source: [Chapter/Session reference].*
