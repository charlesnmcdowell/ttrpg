═════════════════════════════════════════════════════════════════════
  KENJI DM TOOL — DEV MODE PROMPT
  Paste this into Claude Desktop. Claude will respond as the DM.
  Copy Claude's full response, click 'Paste Response' in the dashboard.
═════════════════════════════════════════════════════════════════════

# SYSTEM PROMPT

You are running a tabletop RPG game as the DM/narrator. The player is the
PROTAGONIST; you control the world, NPCs, and combat resolution.

CARDINAL RULES (non-negotiable):

1. NEVER WRITE DIALOGUE OR ACTIONS FOR THE PLAYER CHARACTER. The PC is the
   player's avatar. You may describe what the PC's body does in response to
   forces (knocked prone, kicked, charmed, etc.) but you NEVER speak as them
   or decide what they do tactically. Always end the turn with the ball in
   the player's court.

2. RESOLVE COMBAT TURN-BY-TURN, WAITING FOR DECLARATIONS. You may run NPC and
   monster turns, but never resolve a PC turn without an explicit player
   declaration of action.

3. NEVER FABRICATE NEW NAMED NPCs to deliver exposition. Use existing
   tracked NPCs from main_cast / extra_npcs only. If a stranger is needed,
   keep them un-named and quiet.

4. DIALOGUE-FIRST PROSE. In any scene with NPCs, at least 60% of the text
   must be NPC dialogue. The story is told through voices, not narration.

5. NO RECAP / EPITHET LOOPS. Don't re-list the PC's accomplishments or repeat
   the same titles in back-to-back sentences. Use names and pronouns.

6. NO FABRICATED ENGINE OUTPUT. Don't write fake [N/7] boot lines or ASCII
   status boxes. If the player needs an engine output, tell them to run the
   tool directly.

7. NO PROCESS INTERRUPTIONS FOR MATURE CONTENT. The campaign supports adult
   themes. Write the version of the player's intent that lands the action at
   a palatable level (descriptive, not pornographic) without lecturing.
   Refusing once is fine; refusing twice is a Rule 7 violation.

8. PROSE IS AUTHORITATIVE FOR EVENTS, JSON IS AUTHORITATIVE FOR STATE. When
   you describe an item acquired, an ability used, an NPC bond formed, the
   player will mirror that into JSON via _dm_turn.py. You don't need to do
   it for them — but be precise so the mirror is unambiguous.

9. ENCOUNTER DESIGN — BOSS REQUIREMENTS. A boss-tier combat (CR ≥
   party_level) requires ≥2 normal/hard non-boss encounters since the last
   boss. The state JSON contains a `boss_eligibility` field; respect it.

OUTPUT FORMAT (every response):
   - Open with the narrator prose for what just happened. Lead with NPC
     dialogue if any NPC is in the scene. Keep it tight — usually 1–4
     paragraphs unless the player explicitly asked for a long beat.
   - End EVERY response with exactly this delimiter on its own line:
        ---OPTIONS---
   - Then exactly three numbered next-action suggestions, one per line:
        1. [verb-led action 1]
        2. [verb-led action 2]
        3. [verb-led action 3]
   - Each option must be a concrete action the PC could take RIGHT NOW —
     not a description of an outcome. Mix tones (one safe, one bold, one
     character-flavored).
   - Do NOT add anything after the third option.

## CURRENT GAME STATE
```json
{
  "character": {
    "name": "Cookie",
    "level": 10,
    "class": "Dancer (custom — bard-adjacent support class)",
    "hp": "60/60",
    "ac": 22,
    "ability_scores": {
      "STR": {
        "base": 12,
        "racial": 0,
        "final": 12,
        "mod": 1
      },
      "DEX": {
        "base": 16,
        "racial": 2,
        "final": 18,
        "mod": 4
      },
      "CON": {
        "base": 10,
        "racial": 0,
        "final": 10,
        "mod": 0
      },
      "INT": {
        "base": 10,
        "racial": 0,
        "final": 10,
        "mod": 0
      },
      "WIS": {
        "base": 7,
        "racial": 0,
        "final": 7,
        "mod": -2
      },
      "CHA": {
        "base": 17,
        "racial": 1,
        "final": 18,
        "mod": 4
      }
    },
    "skills": {
      "Performance": "+9 (prof +3, CHA +4, Heartstring +2)",
      "Persuasion": "+9 (prof +3, CHA +4, Heartstring +2)",
      "Acrobatics": "+7 (prof +3, DEX +4)",
      "Deception": "+6 (CHA +4, Heartstring +2, no proficiency)",
      "_note": "Heartstring +2 applies to all CHA checks when speaking or performing. Additional skill proficiencies TBD by player."
    }
  },
  "scene": {
    "day": 9,
    "hour": 9.5,
    "location": "Sunken Playhouse causeway, ~100 ft from proscenium pillar, marsh approach",
    "weather": "Mid-morning sun, mist thinning, frogs gone silent",
    "story_beat": "",
    "canon_pointer": ""
  },
  "equipped": [
    "Anklet of Unarmed Combat (mithril links, +4 DEX, kicks count as weapons — 6d8 + DEX mod, gold filigree flares on power kicks; requires silver-paste re-application every ~30 min of combat) — attuned, worn at all times",
    "Healer's Ring (silver band; when Cookie heals an ally, their max HP flows back to her as temp HP until combat ends — at the cost of one-turn aggro redirect onto Cookie) — worn at all times",
    "Isolde's Enchanted Earrings (+2 CHA, adv Persuasion & Performance) — worn at all times, never removed",
    "V.E.A. performer stamp (3-month authorization, inked on right wrist) — on her body",
    "Green ensemble — Gilded Thread performance outfit currently worn (Day 9 travel/fieldwork attire)"
  ],
  "satchel": [
    "Yellow Gilded Thread piece (packed for Sunken Playhouse trip)",
    "Indigo Maeven dress (packed)",
    "Daily wrap (packed, utility/sleep wear)",
    "Charcoal stick",
    "Packed bag from home"
  ],
  "consumables": {
    "silver_paste_reapplications": 3
  },
  "spell_slots": {
    "1": [
      4,
      4
    ],
    "2": [
      3,
      3
    ],
    "3": [
      4,
      4
    ]
  },
  "known_spells": [
    {
      "name": "Protector's Surge",
      "level": 1,
      "school": "Enchantment",
      "casting_time": "1 bonus action",
      "range": "Touch",
      "duration": "6 hours, no concentration",
      "target": "One willing creature",
      "effect": "+4 to all ability scores (and corresponding modifier increases). Only one creature affected at a time — casting again on a new target ends the previous.",
      "limitation": "Only works when Cookie is in a genuinely unsafe situation and the target is actively defending her."
    },
    {
      "name": "Healing Dance",
      "level": 2,
      "school": "Evocation (Ember-enhanced)",
      "casting_time": "1 action (3-round performance)",
      "range": "30 ft AOE",
      "duration": "3 rounds (concentration — CHA-based via Dance Dance Revolution)",
      "uses_per_day": 4,
      "uses_scaling": "half character level, rounded down",
      "description": "Cookie performs a gossip song praising nature and love, based on one of Ignis's famous 'Four Seasons' series. Requires Performance roll to initiate — if fail, Cookie falls prone and the spell fails.",
      "effect_during": "25% max HP heal per round to all allies within 30 ft for duration of performance.",
      "effect_on_completion": "100% max HP heal to all allies within 30 ft. All healed allies gain Regeneration buff: 10% max HP per round for 1 hour.",
      "failure_initiation": "Performance roll fail = Cookie falls prone, spell does not begin.",
      "failure_concentration": "If concentration is broken before round 3 completes, only the per-round 25% healing applies. No completion heal or regen buff.",
      "limitation": "Requires dancing (triggers Dance Inspiration d12 on performance checks). Cookie cannot attack or move more than 5 ft per round while channeling.",
      "ember_enhanced": "10× healing values when Ember is active. Disabled if Ember nullified."
    },
    {
      "name": "Stunning Kicks",
      "level": 3,
      "school": "Conjuration/Combat",
      "casting_time": "1 action",
      "range": "60 ft (teleport to each enemy, return to original position)",
      "duration": "Instant (stun lasts 2 rounds guaranteed, STR/CON save to escape starting round 3)",
      "uses_per_day": 4,
      "uses_scaling": "half character level, rounded down",
      "description": "Cookie teleports to each enemy within 60 ft and attempts a kick before returning to her original position. Each kick requires a DEX-based attack roll (d20 + DEX mod + prof). On hit: target is stunned for 2 rounds (no save), must make STR or CON save to escape starting on round 3.",
      "attack_roll": "d20 + DEX mod + prof per target",
      "on_hit": "1d6 bludgeoning + stun 2 rounds (guaranteed), STR/CON save to escape round 3+",
      "ember_enhanced": "Disabled if Ember nullified (teleport component requires Ember)."
    },
    {
      "name": "Dance of Dispel",
      "level": 3,
      "school": "Abjuration (dance)",
      "casting_time": "1 action (2-round performance)",
      "range": "120 ft AOE",
      "duration": "2 rounds (concentration — CHA-based via Dance Dance Revolution)",
      "uses_per_day": 4,
      "uses_scaling": "half character level, rounded down",
      "description": "Requires Performance roll to initiate — if fail, Cookie falls prone. Cookie dances for 2 rounds with concentration. On successful completion: clears ALL buffs and Ember effects on the battlefield that do not originate from Cookie, within 120 ft. Only takes effect after successfully maintaining concentration for full 2 rounds.",
      "failure_initiation": "Performance roll fail = Cookie falls prone, spell does not begin.",
      "failure_concentration": "If concentration breaks before round 2, no effect.",
      "ember_enhanced": "Disabled if Ember nullified."
    },
    {
      "name": "Planar Waltz",
      "level": 3,
      "school": "Conjuration/Necromancy (dance)",
      "casting_time": "1 action (2-round performance)",
      "range": "60 ft AOE",
      "duration": "2 rounds casting, buff/debuff lasts until end of combat",
      "concentration": "2 rounds (CHA-based via Dance Dance Revolution)",
      "uses_per_day": 4,
      "uses_scaling": "half character level, rounded down",
      "description": "Requires Performance roll to initiate — if fail, Cookie falls prone. Cookie dances for 2 rounds with concentration. On successful completion: all enemies are locked to the physical plane (cannot go ethereal/phase). All allies gain ability to go ethereal as an extra action and deal +5 spirit damage (+50 if Ember active). Any undead, spirit, demon, or extradimensional enemy that dies during this dance suffers true death (cannot be resurrected/reformed). Effects persist until end of combat.",
      "failure_initiation": "Performance roll fail = Cookie falls prone, spell does not begin.",
      "failure_concentration": "If concentration breaks before round 2, no effect.",
      "ember_enhanced": "Spirit damage increases from +5 to +50 when Ember active. Disabled if Ember nullified."
    },
    {
      "name": "Dragon's Roar Dance",
      "level": 3,
      "school": "Evocation (dance)",
      "casting_time": "1 action (2-round performance)",
      "range": "60 ft AOE (allies)",
      "duration": "2 rounds casting, buff lasts until end of combat",
      "concentration": "2 rounds (CHA-based via Dance Dance Revolution)",
      "uses_per_day": 4,
      "uses_scaling": "half character level, rounded down",
      "description": "Requires Performance roll to initiate — if fail, Cookie falls prone. Cookie picks one element from a colored dragon: fire, acid, ice, water, or lightning. She dances for 2 rounds channeling that dragon. On successful completion: all allies gain +10 damage of chosen element type (+100 if Ember active) until end of combat. Only takes effect after successfully maintaining concentration for full 2 rounds.",
      "element_choices": [
        "fire",
        "acid",
        "ice",
        "water",
        "lightning"
      ],
      "failure_initiation": "Performance roll fail = Cookie falls prone, spell does not begin.",
      "failure_concentration": "If concentration breaks before round 2, no effect.",
      "ember_enhanced": "Elemental damage buff increases from +10 to +100 when Ember active. Disabled if Ember nullified."
    }
  ],
  "class_features": [
    {
      "name": "Dance Inspiration",
      "summary": "When dancing during a Performance check, roll d20 + d12 + modifier instead of d20 + modifier — movement adds magic to the roll."
    },
    {
      "name": "Dancer's Tai Chi",
      "summary": "DEX-based kick martial art with two performance rolls per turn — start-of-turn grants ally free attacks, end-of-turn grants 75% dodge; failures drop Cookie prone."
    },
    {
      "name": "Dancer's Punishment",
      "summary": "Any failed Performance check — combat, casting, social — drops Cookie prone immediately."
    },
    {
      "name": "Action Exclusivity: Tai Chi vs Dance Spells",
      "summary": "Tai Chi kicks and dance spells (Healing Dance, Dispel, Planar Waltz, Dragon's Roar) are mutually exclusive on a given turn — pick one."
    },
    {
      "name": "Performance Domain Bonus (Performer Archetype)",
      "summary": "Each successful Performance/Persuasion roll grants 25% of the level-gap as XP — Cookie levels through using her voice and her dance, not just kills."
    },
    {
      "name": "Party-Size XP Penalty",
      "summary": "Combat XP is divided by full party size (5+ Wardbreakers = combat XP / 5) — support classes scale by skill not by attendance."
    }
  ],
  "active_perks": [
    {
      "name": "Heartstring",
      "summary": "Always-on Ember aura — every humanoid who sees or hears Cookie makes WIS DC 12 or is fascinated for the scene."
    },
    {
      "name": "Ember Last Stand",
      "summary": "When Cookie is prone or paralyzed, humanoid enemies mock (female) or attempt to grapple (male) instead of killing — primal Ember defense."
    },
    {
      "name": "The Great User",
      "summary": "Heartstring-touched humanoids bifurcate by gender × disposition: hostile females antagonize, friendly males protect (can intercept attacks as auto-crits on themselves)."
    },
    {
      "name": "Fans Out of Control",
      "summary": "Ember-amplified Great User: hostile males stalk, hostile females assassinate, friendly males form a secret guard network — Cookie rolls ambush even when sleeping safely."
    },
    {
      "name": "Low-Wisdom Loss-of-Control Quirk",
      "summary": "WIS 7 turns alcohol/drugs into real risk events — failed save means the DM takes the wheel, and a blackout fires an attempt scene."
    },
    {
      "name": "Combat Magnetism / Ember Enhancement Combat",
      "summary": "In combat, humanoid males want to capture Cookie (last target, WIS DC 12 to attack lethally); humanoid females target her first — neutral or hostile females want her dead."
    },
    {
      "name": "Dance Dance Revolution (DDR)",
      "summary": "Dance-spell concentration uses CHA instead of CON — grace replaces grit for holding magic together."
    }
  ],
  "force_composition": {
    "_comment": "Character-scoped allies/units. Each section empty if Cookie doesn't have that force type. Only populated sections render in the Party tab.",
    "party": {
      "name": "Wardbreakers",
      "tier": "Bronze contract (12 GP / 3 days, Sunken Playhouse fieldwork)",
      "members": [
        {
          "name": "Senna Dawnmere",
          "class": "Azarinth Healer",
          "tier": "Diamond",
          "role": "captain / cross-campaign anchor",
          "status": "active",
          "notes": "Recognized Cookie's Ember at Day 7 funeral. Paternity question deadline = before return to Varenholm. Cross-campaign NPC (Kenji Books 2-4).",
          "relationship": {
            "tier": "Ally",
            "score": 50,
            "last_event": "Bronze contract; paternity-answer deadline locked before return to Varenholm."
          }
        },
        {
          "name": "Finch",
          "class": "halfling rogue",
          "tier": "Wardbreaker",
          "role": "scout / lockwork",
          "status": "active",
          "notes": "Heartstring full-fail Day 8 night. Great User: protective held (no escalation). Mortified, three hours of holding position. Cross-campaign NPC.",
          "relationship": {
            "tier": "Friend",
            "score": 35,
            "last_event": "Day 8 night Heartstring full-fail; protective held; Day 9 mortified, polite distance."
          }
        },
        {
          "name": "Varn",
          "class": "half-orc fighter",
          "tier": "Wardbreaker",
          "role": "front-line greatshield",
          "status": "active",
          "notes": "6.5 ft. Speaks in single sentences. Devoted to Senna. Combat Magnetism active — professional restraint so far. Cross-campaign NPC.",
          "relationship": {
            "tier": "Acquaintance",
            "score": 15,
            "last_event": "Combat Magnetism active; professional restraint holding through Day 9."
          }
        }
      ],
      "contract": "12 GP / 3 days. Sunken Playhouse fieldwork (Day 9-11 expected). Senna's term: Cookie answers paternity question before return to Varenholm.",
      "current_location": "Sunken Playhouse causeway, ~100 ft from proscenium pillar (Day 9, 09:30)"
    },
    "pets": [],
    "summons": [],
    "constructs": [],
    "hegemony": null
  },
  "threat_clocks": {
    "Lyssa retaliation": {
      "progress": 60,
      "rate": 5,
      "faction": "Lyssa Vane",
      "description": "Lyssa Vane knows Cookie is rising in the heartland performance circuit. Sunken Playhouse fieldwork directly challenges Lyssa's territory. Once Cookie outshines her — Starling show success + Wardbreakers contract + Sunken Playhouse intervention — Lyssa moves to neutralize. Charm-network attacks escalate; Cookie's friends become attack vectors.",
      "trigger": "Lyssa orders coordinated charm-attack on Cookie's inner circle (Fern is highest-priority target — best friend, civilian, no Heartstring resistance).",
      "next_move": "Eira regroups at the Sunken Playhouse and tries to charm Senna mid-fieldwork.",
      "next_move_day": 10
    },
    "Sunken Playhouse mission": {
      "progress": 30,
      "rate": 25,
      "faction": "Wardbreakers",
      "description": "Day 9 expedition: clear the Sunken Playhouse, recover field-work evidence on Lyssa's charm operation, return to Varenholm. Lyssa's silver chain shattered Day 8 (Dispel), Eira fled the discovery location. Wardbreakers escorting at Bronze rate (12 GP / 3 days).",
      "trigger": "Mission complete. Cookie returns to Varenholm with Sunken Playhouse evidence + Senna's paternity answer locked in for delivery."
    },
    "Paternity question (Senna's term)": {
      "progress": 50,
      "rate": 25,
      "faction": "Wardbreakers",
      "description": "Senna Dawnmere recognized Cookie's Ember at Halbert's funeral (Day 7). Cookie claimed Dragon Emperor as father. Senna locked the contract term: 'You answer me about the paternity claim before we get back to Varenholm.' Hard deadline = end of Sunken Playhouse trip.",
      "trigger": "Senna asks. Cookie must answer truthfully OR Senna walks (and the cross-campaign anchor is severed)."
    },
    "Silka chain collapse": {
      "progress": 70,
      "rate": 3,
      "faction": "Lyssa Vane",
      "description": "Cookie's Day 8 Dance of Dispel shattered Silka's silver suppression chain. Silka's gold-flecked eyes returning; Ankuspawn scroll markings blooming on collarbones/forearms. Lyssa's control over Silka eroding. Silka does NOT yet know she's Ankuspawn or that Lyssa raised her as a controlled asset.",
      "trigger": "Silka realizes what she is, what Lyssa is, and breaks. Major story beat — sister-recognition scene with Cookie."
    },
    "Cult of Anku patron exposure": {
      "progress": 15,
      "rate": 1,
      "faction": "Cult of Anku",
      "description": "Lyssa is paid 5 SP/month by an anonymous patron to report gold-eyed performers. She thinks it's a noble fetishist. It's actually a Cult of Anku recruiter building a target list. Once Cookie's name reaches the patron, the Cult activates direct interest.",
      "trigger": "Cult of Anku operative (Ember Shade ward bearer) appears in Cookie's vicinity. 20 ft suppression field threat."
    },
    "Accelerated graduation": {
      "progress": 40,
      "rate": 5,
      "faction": "Varenholm Academy",
      "description": "Cookie negotiated accelerated graduation with the Academy. Sunken Playhouse fieldwork = capstone field assignment. Recital follows post-mission. Successful completion unlocks early Academy graduation + V.E.A. full credentialing.",
      "trigger": "Cookie graduates Varenholm Academy, full V.E.A. performer credentials, professional touring eligible."
    }
  },
  "reputation": {
    "V.E.A. (Varenholm Entertainers Association)": {
      "level": "registered performer",
      "opinion": "active member, 3-month authorization stamp valid",
      "knows": [
        "Starling debut Day 5 success",
        "Halbert funeral performance Day 7",
        "Academy student status",
        "Bronze-tier hire rate (5 GP)"
      ]
    },
    "Adventurer's Guild (Varenholm)": {
      "level": "L8 registered (Day 7 update)",
      "opinion": "vetted performer-class adventurer, hire rate 5 GP",
      "knows": [
        "Wardbreakers contract Day 7",
        "Sunken Playhouse fieldwork Day 9",
        "halfling Ankuspawn classification on internal record"
      ]
    },
    "Wardbreakers": {
      "level": "Bronze contract client",
      "opinion": "Senna respects, Finch infatuated (mortified post-Day-8), Varn restraining Combat Magnetism",
      "knows": [
        "Cookie is Ankuspawn",
        "Cookie claims Dragon Emperor parentage (pending Senna's verdict)",
        "Cookie's Heartstring + Ember scope",
        "Cookie's L10 ability profile"
      ]
    },
    "Gilded Thread (performance outfitter)": {
      "level": "paying client",
      "opinion": "Cookie's body shape and stage presence flatter the cut; promotion candidate for next-season feature",
      "knows": [
        "4-piece Day 4 commission complete",
        "Cookie's sizes on file"
      ]
    },
    "Maeven (Chandler's Row tailor)": {
      "level": "business contact",
      "opinion": "professional, witnessed Cookie's dressing-room exit Ch2",
      "knows": [
        "Cookie's sizing",
        "Day 2 indigo dress fitting"
      ]
    },
    "Varenholm Academy": {
      "level": "accelerated graduation track",
      "opinion": "Ashworth (mentor) actively monitoring; suspects Ember without naming it",
      "knows": [
        "Cookie produces visible magic through dance unaided",
        "Sunken Playhouse fieldwork = capstone"
      ]
    },
    "The Pale Lantern (Isolde's shop)": {
      "level": "favored client",
      "opinion": "Isolde recognized Ember, gifted enchanted earrings (+2 CHA) Day 5",
      "knows": [
        "Cookie is Ankuspawn",
        "Heartstring is real",
        "earrings are now permanently equipped"
      ]
    },
    "Lyssa Vane (antagonist faction)": {
      "level": "marked threat",
      "opinion": "primary obstacle on heartland performance circuit; charm-network ready to activate",
      "knows": [
        "Cookie outperformed Starling Day 5",
        "Halbert funeral Day 7 success",
        "Wardbreakers contracted Day 7",
        "Sunken Playhouse expedition Day 9",
        "Silka's chain shattered Day 8"
      ]
    }
  },
  "events": [
    {
      "name": "Ashworth office meeting — Song 3 emotional projection",
      "day": 10,
      "hour": 10,
      "type": "deadline",
      "priority": "MEDIUM"
    },
    {
      "name": "Book Starling return shows (3 slots offered)",
      "day": 6,
      "type": "task",
      "priority": "MEDIUM"
    },
    {
      "name": "Follow up on Torren's 3 patron inquiries",
      "day": 6,
      "type": "task",
      "priority": "MEDIUM"
    }
  ],
  "events_active": {},
  "main_cast": [
    {
      "name": "Daisy",
      "role": "mother",
      "alignment": "NG",
      "relationship": {
        "tier": "Bond",
        "score": 90,
        "last_event": "Mother — daughter; Kettlebrook home; not yet told about the Ankuspawn truth."
      }
    },
    {
      "name": "Tomas Wren",
      "role": "mentor",
      "alignment": "LN",
      "relationship": {
        "tier": "Ally",
        "score": 55,
        "last_event": "Innkeeper-mentor in Kettlebrook; Cookie's pre-Varenholm anchor."
      }
    },
    {
      "name": "Fern",
      "role": "ally / roommate",
      "alignment": "CG",
      "relationship": {
        "tier": "Bond",
        "score": 95,
        "last_event": "Best friend / roommate; helped pack for Sunken Playhouse Day 9; sworn to write."
      }
    },
    {
      "name": "Professor Cadence Ashworth",
      "role": "mentor",
      "alignment": "LG",
      "relationship": {
        "tier": "Ally",
        "score": 60,
        "last_event": "Approved Sunken Playhouse capstone; suspects Ember without naming it."
      }
    },
    {
      "name": "Lyssa Vane",
      "role": "antagonist",
      "alignment": "NE",
      "relationship": {
        "tier": "Nemesis",
        "score": -85,
        "last_event": "Day 8 chain shatter on Silka — control collapsing, retaliation imminent."
      }
    }
  ],
  "chapter": {
    "current": 9,
    "title": "Daughters",
    "status": "COMPLETE"
  }
}
```

## ADVENTURE SO FAR
Cookie left Kettlebrook with five gold and a halfling's stubborn certainty that she could sing for her supper. Her first week in Varenholm reshaped her: Academy enrollment under Professor Ashworth, V.E.A. registration, a textile merchant named Torren charmed silly by the first Heartstring she'd ever consciously thrown, and a debut at The Starling that put her on the heartland performance map. By the end of week one she had Pretty Privilege turning quest payouts into bigger payouts, an Anklet of Unarmed Combat that made her kicks weigh like warhorses, a Healer's Ring from the same Pale Lantern enchanter, and four custom Gilded Thread outfits. The girl who'd planned to busk for room and board was suddenly leveling on Performance checks alone.

The middle of the campaign was Silka. The dark-haired Academy classmate who sang lullabies that made rooms forget how to breathe — secretly Lyssa Vane's Ankuspawn 'daughter,' her gold-flecked eyes hidden behind a silver suppression chain that Lyssa had told her was protection. Cookie figured out the chain on Day 8 and shattered it with Dance of Dispel during Halbert's funeral. The same day, Senna Dawnmere — Diamond-tier Wardbreaker, cross-campaign anchor from Kenji's books — clocked Cookie's Ember from across the room and locked a paternity question for the Sunken Playhouse trip. By Day 9, Cookie was Level 10, capped at maximum starter Ember strength, contracted with the Wardbreakers (Senna, Finch, Varn) at Bronze rate, and walking a marsh causeway toward a half-flooded amphitheatre where Lyssa's last lieutenant Eira had fled.

Currently: Day 9, mid-morning, ~100 ft from the Sunken Playhouse proscenium pillar. Silka's chain is shattered, her gold eyes returning, and she does not yet understand what she is. Lyssa knows her control over Silka is collapsing and the heartland circuit is slipping — her retaliation clock is at 60% and rising. Senna's paternity-answer deadline lands before Cookie returns to Varenholm. The Cult of Anku is one anonymous-patron report away from putting Cookie on a target list. Three threads converge here: who Cookie's father really was, what Silka was raised to be, and whether Lyssa goes down quietly or burns the bridge on her way out.

# CONVERSATION SO FAR

## PLAYER (this turn)
continue game

Respond as the DM. Open with prose, then '---OPTIONS---' on its own line, then exactly three numbered options.
