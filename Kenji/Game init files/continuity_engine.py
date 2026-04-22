"""
CONTINUITY ENGINE — Kenji TTRPG Campaign
=========================================
Lightweight validation layer. The AI DM references this before every scene.
This file is the SOURCE OF TRUTH for campaign structure. It does not replace
character_tracker.md or kenji_state.json — it VALIDATES them.

RULES:
  1. MAIN_NPCS are immutable. Created at campaign design time. Cannot be killed
     off-screen, retconned, or replaced without player approval.
  2. SECONDARY_NPCS exist to serve MAIN_NPCS. Every secondary NPC must have a
     'points_to' field linking them to at least one main NPC or threat.
  3. DISPOSABLE_NPCS (unnamed innkeepers, guards, farmers) have NO tracker entry.
     They know PUBLIC info only. They point to tracked NPCs, nothing more.
  4. Every encounter must route to exactly one THREAT.
  5. The AI cannot create a new named NPC without registering them here first
     and assigning a points_to link.

USAGE:
  The AI calls validate_scene() before presenting any scene with NPCs.
  The AI calls validate_npc() before introducing any named character.
  The AI calls get_threat_npcs() to see who belongs to a given threat.
  The AI calls check_npc_function() to verify a secondary NPC is serving its purpose.
"""

# =============================================================================
# CAMPAIGN THREATS — IMMUTABLE
# =============================================================================
# These are the 5 existential threats. Their structure cannot change mid-game.
# Only their 'progress' and 'status' fields update during play.

THREATS = {
    "pallid_march": {
        "name": "The Pallid March",
        "location": "The Ashenveil — Dead Marshlands (southeast)",
        "race": "Undead — skeletons, revenants, wraiths, death knights, a lich",
        "clock_days": 27,
        "rate_per_day": 3,
        "current_progress": 20,
        "status": "active — advance columns testing southern borders",
        "win_condition": "Destroy Lady Nyx's phylactery-equivalent (bronze ring, 4 seams) OR coalition army defeats the March conventionally (every casualty feeds enemy)",
        "fail_condition": "March launches and overruns Thornkeep → Stormhaven → southern farmland. Every fallen soldier rises on her side.",
        "shortcut": "Phylactery ring. 4 seams tied to named anchors. 4th seam parasitized by death-binder.",
        "danger": "Intimacy with Lady Nyx triggers Lover's Vigor → +50% her stats for 5 days → accelerates conquest to 10%/cycle. Romance IS the threat path.",
        "key_npcs": ["lady_nyx", "sir_corwyn", "mags", "jostin", "hale", "death_binder", "handler", "corban"],
    },
    "the_hollowing": {
        "name": "The Hollowing",
        "location": "Kharn-Dural — Dwarven Undermountain (northwest)",
        "race": "Dwarves, deep gnomes, duergar, and The Fathom",
        "clock_days": 42,
        "rate_per_day": 2,
        "current_progress": 15,
        "status": "active — seal holding, barely",
        "win_condition": "Reinforce the seal (ember/creation energy — breaks Kenji's cover) OR Amaris's Bloom Purge stabilizes ley lines (buys decades)",
        "fail_condition": "Seal breaks → The Fathom rises → undermountain collapses → 40,000 dwarves die/flee → corruption reaches coalition via Ashward Mine tunnels",
        "shortcut": "Ember magic is The Fathom's antithesis. Direct application seals it. But reveals Kenji.",
        "danger": "Tunnels connect to Ashward Mines — coalition territory. Breach spreads fast.",
        "key_npcs": ["thorgrim", "brunhild", "grimjaw"],
    },
    "red_court": {
        "name": "The Red Court",
        "location": "Ashenmere — Port City (eastern coast)",
        "race": "Vampires, thralls, doppelgangers, corrupted nobility",
        "clock_days": 70,
        "rate_per_day": 1,
        "current_progress": 30,
        "status": "active — 30% converted, infiltration deepening",
        "win_condition": "Root out infiltration. Expose/destroy Lady Mirenne's network. Cure or kill turned officials.",
        "fail_condition": "Ashenmere falls completely → Red Court uses port + portal to infiltrate rest of coalition. Silent conquest. Doppelgangers in Varenholm.",
        "shortcut": "Sevren (spymaster) knows the full roster of who's been replaced. Capture alive = intelligence goldmine.",
        "danger": "Kenji's Irresistible Presence disrupts Court cover — every female thrall/doppelganger drawn to him. Chaos in their network but also exposes him.",
        "key_npcs": ["mirenne", "sevren", "halvard", "old_tam", "morvak"],
    },
    "iron_horde": {
        "name": "The Iron Horde",
        "location": "The Sunderplains — Open Steppe (west/northwest)",
        "race": "Orcs, goblins, trolls, ogres, half-orcs, worgs, war mammoths",
        "clock_days": 16,
        "rate_per_day": 4,
        "current_progress": 35,
        "status": "active — 50,000 warriors mobilized, pointed east",
        "win_condition": "Diplomacy: offer recognition + trade + portal → Horde becomes ally (50,000 warriors join coalition). OR delay tactics: Horde's logistics sustain 30 days, then tribes fracture.",
        "fail_condition": "Horde hits Thornwall → Katya's HQ falls → western territories collapse. 12,000 vs 50,000.",
        "shortcut": "Gorath WANTS a treaty. He unified through shame, not bloodlust. Offer recognition, trade, portal seat.",
        "danger": "Fighting wins the battle but loses alliance forever. 50,000 orcs with a generational grudge.",
        "key_npcs": ["gorath", "magra", "snikkit", "vrokka"],
    },
    "twin_wyrms": {
        "name": "The Twin Wyrms",
        "location": "The Dragonspine Mountains (far north)",
        "race": "Dragons, dragonborn, kobolds, dragon cultists, two ancients",
        "clock_days": 95,
        "rate_per_day": 1,
        "current_progress": 5,
        "status": "active — slow clock, biggest stakes",
        "win_condition": "Attend the Reckoning. Convince enough flights to vote for balance. Requires Kaeltharion's endorsement → Dragonspine gauntlet.",
        "fail_condition": "Vorathiel wins vote → seven dragonflights descend → everything burns. Cannot be fought. Only politicked.",
        "shortcut": "Drazhara wants a dragonborn seat at the Reckoning. Offering that could flip the vote.",
        "danger": "Irresistible Presence has NO effect on true dragons (non-humanoid). Dragonborn — roll normally. Ignis in humanoid form — roll normally.",
        "key_npcs": ["vorathiel", "kaeltharion", "drazhara", "ignis", "skratch"],
    },
}


# =============================================================================
# MAIN NPCs — IMMUTABLE REGISTRY
# =============================================================================
# These characters were created at campaign design time. They are the spine
# of the story. Every secondary NPC, every encounter, every scene must
# ultimately point toward one or more of these characters.
#
# Fields:
#   threat     — which campaign threat they belong to (or "coalition" / "personal")
#   role       — their function in the campaign
#   goal       — what they want (drives their actions)
#   alive      — mutable during play, but killing a main NPC is a MAJOR event
#   met        — has Kenji met them face-to-face?
#   location   — current known location

MAIN_NPCS = {
    # --- PALLID MARCH ---
    "lady_nyx": {
        "name": "Lady Nyx / the Lych / their Lady",
        "threat": "pallid_march",
        "role": "antagonist — Warden-Queen of the Pallid March",
        "level": 32,
        "goal": "Siphon coalition ley network to fuel mass resurrection. Raise army of 10,000. March north.",
        "alive": True,
        "met": False,
        "location": "Ashenveil — weeping elm grove, 4mi east of Millhaven",
        "alignment": "CE",
    },
    "sir_corwyn": {
        "name": "Sir Corwyn the Fallen",
        "threat": "pallid_march",
        "role": "field champion — death knight, Lady Nyx's guard",
        "level": 26,
        "goal": "Protect Lady Nyx (Oath-bound). Cannot break service without breaking Oath. Oath keeps him sentient.",
        "alive": True,  # undead but sentient
        "met": True,
        "location": "Terminus site, 80 yards from iron seal (grid H-9)",
        "alignment": "LG",
    },
    "mags": {
        "name": "Mags",
        "threat": "pallid_march",
        "role": "guide — knows every path in the Ashenveil",
        "level": 8,
        "goal": "Survive. Get paid. 10 gold/day.",
        "alive": True,
        "met": False,
        "location": "Edge of the Ashenveil",
        "alignment": "CG",
    },
    "death_binder": {
        "name": "The Death-Binder (unnamed)",
        "threat": "pallid_march",
        "role": "second-order antagonist — parasitizing 4th seam of Lady Nyx's ring",
        "level": None,  # unknown
        "goal": "Unknown — parasitizing Lady Nyx's phylactery seam",
        "alive": True,
        "met": False,
        "location": "Unknown",
        "alignment": "unknown",
    },
    "handler": {
        "name": "The Handler (unnamed)",
        "threat": "pallid_march",
        "role": "logistics/support for the death-binder",
        "level": None,
        "goal": "Support the death-binder's operation",
        "alive": True,
        "met": False,
        "location": "Unknown",
        "alignment": "unknown",
    },
    "corban": {
        "name": "Corban",
        "threat": "pallid_march",
        "role": "connected to Lady Nyx's grief-seam (ring anchor)",
        "level": None,
        "goal": "Unknown — status unknown",
        "alive": None,  # unknown
        "met": False,
        "location": "Unknown",
        "alignment": "unknown",
    },

    # --- THE HOLLOWING ---
    "thorgrim": {
        "name": "King Thorgrim Ironvault",
        "threat": "the_hollowing",
        "role": "ruler of Kharn-Dural — ordered the dig that broke the seal",
        "level": 22,
        "goal": "Save his people. Will kneel to anyone who can. Has never knelt.",
        "alive": True,
        "met": False,
        "location": "Kharn-Dural — throne level",
        "alignment": "LG",
    },
    "brunhild": {
        "name": "Brunhild Deepdelve",
        "threat": "the_hollowing",
        "role": "head miner — was on the drill team that broke through",
        "level": 18,
        "goal": "Fix what she helped break. Hasn't slept in 3 months.",
        "alive": True,
        "met": False,
        "location": "Kharn-Dural — deep levels",
        "alignment": "LG",
    },
    "grimjaw": {
        "name": "Grimjaw",
        "threat": "the_hollowing",
        "role": "duergar exile — knows about the second breach",
        "level": 20,
        "goal": "Trade information for citizenship. Survival.",
        "alive": True,
        "met": False,
        "location": "Kharn-Dural — upper tunnels",
        "alignment": "N",
    },

    # --- RED COURT ---
    "mirenne": {
        "name": "Lady Mirenne",
        "threat": "red_court",
        "role": "antagonist — Elder Vampire, Red Court leader",
        "level": 28,
        "goal": "Own Ashenmere. Silent conquest. Then spread to the coalition.",
        "alive": True,
        "met": False,
        "location": "Ashenmere — embedded in noble society",
        "alignment": "LE",
    },
    "sevren": {
        "name": "Sevren",
        "threat": "red_court",
        "role": "doppelganger spymaster — runs the replacement network",
        "level": 20,
        "goal": "Maintain cover. 17 faces memorized. Will become Kenji's face if cornered.",
        "alive": True,
        "met": False,
        "location": "Ashenmere — multiple identities",
        "alignment": "LE",
    },
    "halvard": {
        "name": "Captain Halvard",
        "threat": "red_court",
        "role": "recently turned garrison commander — fighting the hunger",
        "level": 14,
        "goal": "Not become a monster. If cured, becomes inside man. Hunger wins within a month if untreated.",
        "alive": True,
        "met": False,
        "location": "Ashenmere garrison",
        "alignment": "LG",
    },
    "old_tam": {
        "name": "Old Tam",
        "threat": "red_court",
        "role": "goblin fence — notices which officials stopped eating garlic",
        "level": 6,
        "goal": "Buy and sell. Sell information for the right price.",
        "alive": True,
        "met": False,
        "location": "Ashenmere docks — pawn shop",
        "alignment": "N",
    },
    "morvak": {
        "name": "Brother Morvak",
        "threat": "red_court",
        "role": "orc priest — wards keeping vampires out, documenting the pattern",
        "level": 12,
        "goal": "Protect his block. Document the infiltration. Terrified and right.",
        "alive": True,
        "met": False,
        "location": "Ashenmere dock district — Sunfather mission",
        "alignment": "LG",
    },

    # --- IRON HORDE ---
    "gorath": {
        "name": "Warchief Gorath Skullsplitter",
        "threat": "iron_horde",
        "role": "antagonist/potential ally — unified 30 tribes through shame",
        "level": 27,
        "goal": "Recognition. Trade rights. Portal access. Coalition seat. Will burn the west to get it.",
        "alive": True,
        "met": False,
        "location": "Sunderplains — war camp",
        "alignment": "CG",
    },
    "magra": {
        "name": "Magra Bloodtusk",
        "threat": "iron_horde",
        "role": "orc shaman — Gorath's spiritual adviser",
        "level": 24,
        "goal": "Ensure Gorath saves the clans, not destroys them. Doesn't trust humans.",
        "alive": True,
        "met": False,
        "location": "Sunderplains — war camp",
        "alignment": "CG",
    },
    "snikkit": {
        "name": "Snikkit",
        "threat": "iron_horde",
        "role": "goblin sapper-engineer — designed all siege equipment",
        "level": 14,
        "goal": "Build things. Get recognition for goblins. A little proud of the catapult.",
        "alive": True,
        "met": False,
        "location": "Sunderplains — siege works",
        "alignment": "CG",
    },
    "vrokka": {
        "name": "Vrokka",
        "threat": "iron_horde",
        "role": "troll berserker — Gorath's champion, nuclear deterrent",
        "level": 22,
        "goal": "Hit things. Don't think. IP triggers on trolls (humanoid).",
        "alive": True,
        "met": False,
        "location": "Sunderplains — war camp",
        "alignment": "CE",
    },

    # --- TWIN WYRMS ---
    "vorathiel": {
        "name": "Vorathiel the Conqueror",
        "threat": "twin_wyrms",
        "role": "antagonist — Ancient Red Dragon, wants flights to descend",
        "level": 38,
        "goal": "End the treaty. Dragons rule. Afraid of humanity's rising power.",
        "alive": True,
        "met": False,
        "location": "Dragonspine Mountains — summit",
        "alignment": "LE",
    },
    "kaeltharion": {
        "name": "Kaeltharion the Keeper",
        "threat": "twin_wyrms",
        "role": "potential ally — Ancient Silver Dragon, defends the treaty",
        "level": 38,
        "goal": "Maintain the balance. Find a champion. Tired after 1000 years.",
        "alive": True,
        "met": False,
        "location": "Dragonspine Mountains — summit",
        "alignment": "LG",
    },
    "drazhara": {
        "name": "Drazhara",
        "threat": "twin_wyrms",
        "role": "dragonborn elder — wants a seat at the Reckoning",
        "level": 20,
        "goal": "Dragonborn representation. Caught between flights. Offering a seat flips the vote.",
        "alive": True,
        "met": False,
        "location": "Dragonspine — lower peaks settlement",
        "alignment": "LG",
    },
    "ignis": {
        "name": "Ignis",
        "threat": "twin_wyrms",
        "role": "young red dragon — Vorathiel's youngest, swing vote in her family",
        "level": 18,
        "goal": "Understand humans. Curious. Not sure mother is right or wrong. IP works in humanoid form.",
        "alive": True,
        "met": False,
        "location": "Dragonspine — secretly visits lowlands",
        "alignment": "N",
    },
    "skratch": {
        "name": "Skratch",
        "threat": "twin_wyrms",
        "role": "kobold prophet — saw 'a man made of fire kneeling before two mountains'",
        "level": 4,
        "goal": "Wait for the vision to come true. 11 years and counting.",
        "alive": True,
        "met": False,
        "location": "Dragonspine base — waiting",
        "alignment": "CG",
    },

    # --- COALITION / PERSONAL (not threat-specific, but campaign-critical) ---
    "garrett": {
        "name": "Garrett",
        "threat": "coalition",
        "role": "civil service HQ — runs Kenji's empire",
        "level": None,
        "goal": "Find Kenji. Hand him 2ft of paperwork. Keep the empire running.",
        "alive": True,
        "met": True,
        "location": "Crestfall",
        "alignment": "LG",
    },
    "sera": {
        "name": "Sera",
        "threat": "coalition",
        "role": "Darkblades commander — Stormhaven territory",
        "level": None,
        "goal": "Run Stormhaven. Raise her child. The door is hers. She doesn't chase.",
        "alive": True,
        "met": True,
        "location": "Stormhaven",
        "alignment": "CG",
    },
    "pip": {
        "name": "Pip",
        "threat": "coalition",
        "role": "Director of Holdings — 8 inns, empire logistics",
        "level": None,
        "goal": "Arrive with ledger, baby, and list of things the empire needs.",
        "alive": True,
        "met": True,
        "location": "Varenholm / touring properties",
        "alignment": "CG",
    },
    "senna": {
        "name": "Senna",
        "threat": "coalition",
        "role": "War College instructor — teaching combat tactics",
        "level": None,
        "goal": "Found purpose. Pregnancy status TBD.",
        "alive": True,
        "met": True,
        "location": "Varenholm — Aldwin War College",
        "alignment": "CG",
    },
    "elara": {
        "name": "Elara",
        "threat": "coalition",
        "role": "Chancellor — running the Academy",
        "level": None,
        "goal": "Academy business. Pregnancy buried if kept. Doesn't mention the child.",
        "alive": True,
        "met": True,
        "location": "Varenholm — Academy",
        "alignment": "LG",
    },
    "vess": {
        "name": "Vess",
        "threat": "coalition",
        "role": "governance — been running the coalition for 6 months without authorization",
        "level": None,
        "goal": "Legitimize what she's built or Kenji steps aside. Exhausted. Angry. Competent.",
        "alive": True,
        "met": True,
        "location": "Varenholm — Council chambers",
        "alignment": "LG",
    },
    "katya": {
        "name": "Katya",
        "threat": "coalition",
        "role": "General — 12,000 troops across 12+ territories",
        "level": None,
        "goal": "Hold the military together. Professional. Can't be everywhere.",
        "alive": True,
        "met": True,
        "location": "Vyranth — coalition military HQ",
        "alignment": "LG",
    },
    "dren": {
        "name": "Dren",
        "threat": "coalition",
        "role": "rebuilding Ironholt — eastern territories stable",
        "level": None,
        "goal": "Would come if called. Can't be called.",
        "alive": True,
        "met": True,
        "location": "Ironholt",
        "alignment": "CG",
    },
    "mordecai": {
        "name": "Mordecai",
        "threat": "coalition",
        "role": "wild card — gone, building something, watches the ley network",
        "level": None,
        "goal": "Gentleman's understanding. If Kenji uses ember at scale, Mordecai notices.",
        "alive": True,
        "met": True,
        "location": "Unknown",
        "alignment": "LE",
    },
    "amaris": {
        "name": "Amaris",
        "threat": "coalition",
        "role": "druid — Briarstone homestead, two vials of creation energy",
        "level": None,
        "goal": "Kenji left without a note. She will see him again. Bloom Purge could stabilize Kharn-Dural.",
        "alive": True,
        "met": True,
        "location": "Briarstone",
        "alignment": "CG",
    },
    "solveth": {
        "name": "Solveth",
        "threat": "coalition",
        "role": "God of Entropy — bonded in Frost Fang, speaks through the bond",
        "level": None,
        "goal": "Speaks rarely. Vague. Self-interested. Warns before lethal mistakes.",
        "alive": True,
        "met": True,
        "location": "In Frost Fang (stored at homestead)",
        "alignment": "N",
    },
    "the_eldest": {
        "name": "The Eldest",
        "threat": "coalition",
        "role": "Deepwood alliance — personal to Kenji, paper without him present",
        "level": None,
        "goal": "Alliance holds. Will send emissary → Faelindra → come herself if things get bad enough.",
        "alive": True,
        "met": True,
        "location": "Silvandris — Eldest tree",
        "alignment": "LG",
    },
    "lythara": {
        "name": "Lythara",
        "threat": "coalition",
        "role": "root-weaver — tending the Deepwood forest",
        "level": None,
        "goal": "The forest felt something leave. Waiting quietly.",
        "alive": True,
        "met": True,
        "location": "Silvandris — Deepwood",
        "alignment": "CG",
    },
    "faelindra": {
        "name": "Faelindra",
        "threat": "coalition",
        "role": "Continental Defense Commander — Silvandris",
        "level": None,
        "goal": "Has her own war to not-fight. Independent.",
        "alive": True,
        "met": True,
        "location": "Silvandris — continental defense",
        "alignment": "LG",
    },
    "nimue": {
        "name": "Nimue",
        "threat": "coalition",
        "role": "advanced aether researcher — Academy Spire",
        "level": None,
        "goal": "Processes through work. Published two papers.",
        "alive": True,
        "met": True,
        "location": "Silvandris — Academy Spire",
        "alignment": "LG",
    },
    "thessaly": {
        "name": "Thessaly",
        "threat": "coalition",
        "role": "researcher — ley networks and Confluence Lens",
        "level": None,
        "goal": "Publishing research. No closure.",
        "alive": True,
        "met": True,
        "location": "Silvandris — Heart Grove library",
        "alignment": "LG",
    },
    "aldwin": {
        "name": "Aldwin",
        "threat": "coalition",
        "role": "Dean — War College",
        "level": None,
        "goal": "War College is his legacy. Doesn't ask where Kenji went.",
        "alive": True,
        "met": True,
        "location": "Varenholm — War College",
        "alignment": "LG",
    },
}


# =============================================================================
# SECONDARY NPCs — CREATED DURING PLAY
# =============================================================================
# These NPCs were born from player interaction. They are valid characters
# but they MUST serve the campaign by pointing toward main NPCs / threats.
#
# The 'points_to' field is MANDATORY. It names the main NPC(s) or threat
# that this secondary NPC ultimately leads the player toward.
#
# The 'function' field describes HOW they serve the campaign.
# The 'expendable' field: True = can die/leave without affecting campaign spine.

SECONDARY_NPCS = {
    "bracken": {
        "name": "Commander Renna Bracken",
        "points_to": ["lady_nyx", "sir_corwyn", "pallid_march"],
        "function": "Garrison commander on Lady Nyx's advance front. Her intelligence and soldiers are Kenji's entry point into the Pallid March threat. Her letters to Katya/Vess connect the south road to coalition awareness.",
        "expendable": False,  # she's become load-bearing for the Pallid March entry
        "met": True,
        "location": "Thornkeep garrison",
        "alive": True,
    },
    "jostin": {
        "name": "Corporal Jostin",
        "points_to": ["lady_nyx", "sir_corwyn", "pallid_march"],
        "function": "Scout whose patrol data documents Lady Nyx's advance columns. His journal is the intelligence pipeline from field to coalition. Brain Kenji doesn't have (INT 9). Leads player deeper into Pallid March intelligence.",
        "expendable": False,  # campaign-bible NPC, Pallid March key NPC
        "met": True,
        "location": "Mile 12, underground hub",
        "alive": True,
    },
    "brynn": {
        "name": "Brynn",
        "points_to": ["lady_nyx", "pallid_march"],
        "function": "Shield support for the assault team. Her survival/death affects garrison strength on Lady Nyx's front. IP Stack 5 creates personal stakes that keep Kenji invested in the Pallid March fight.",
        "expendable": True,
        "met": True,
        "location": "Mile 12, underground hub",
        "alive": True,
    },
    "taryn": {
        "name": "Taryn",
        "points_to": ["lady_nyx", "pallid_march", "sir_corwyn"],
        "function": "Millhaven fighter. Letter of commission ties to coalition awareness of the March. Provided 4 leads. Intro letter to Vellin (archivist). Vigor expires Ashmere 27.",
        "expendable": True,
        "met": True,
        "location": "Millhaven",
        "alive": True,
    },
    "bracken": {
        "name": "Bracken",
        "points_to": ["lady_nyx", "sir_corwyn", "pallid_march"],
        "function": "Millhaven Watch Captain. Full debrief on Seravane/Corban/bronze rings. 4 leads provided. Intelligence conduit for Pallid March reconnaissance.",
        "expendable": True,
        "met": True,
        "location": "Millhaven",
        "alive": True,
    },
    "elda": {
        "name": "Elda",
        "points_to": ["sir_corwyn", "pallid_march"],
        "function": "Civilian found at Corwyn's camp. Her rescue connected Kenji to the terminus site and the iron seal. Emotional stakes — woman and child in a dead zone.",
        "expendable": True,
        "met": True,
        "location": "Thornkeep waystation",
        "alive": True,
    },
    "halden": {
        "name": "Halden",
        "points_to": ["sir_corwyn", "pallid_march"],
        "function": "Elda's son. Found near Corwyn's camp. Emotional stakes that connected Kenji to the terminus site.",
        "expendable": True,
        "met": True,
        "location": "Thornkeep waystation",
        "alive": True,
    },
    "holsk": {
        "name": "Holsk",
        "points_to": ["pallid_march"],
        "function": "Dwarven blacksmith, Millhaven. Crafted maerinbronze rings. Polearm pickup Ashmere 28. Equipment conduit — keeps Kenji geared for the fight ahead.",
        "expendable": True,
        "met": True,
        "location": "Millhaven — forge",
        "alive": True,
    },
    "wynn": {
        "name": "Wynn",
        "points_to": ["coalition"],
        "function": "Herbalist/researcher. Analyzing creation energy. If her analysis reaches wrong hands, Kenji's identity exposed → Bane of Eve triggers → all 5 clocks start.",
        "expendable": True,
        "met": True,
        "location": "Millhaven — herbalist shop",
        "alive": True,
    },
    "breca": {
        "name": "Breca",
        "points_to": ["coalition"],
        "function": "Merchant. Road Sense + The Long Haul perks. Trade route awareness. Intimate partner — emotional thread.",
        "expendable": True,
        "met": True,
        "location": "North road — driving toward Greymere",
        "alive": True,
    },
    "delia": {
        "name": "Delia",
        "points_to": ["coalition"],
        "function": "Thornfield tavern keeper. Chose her village over the aura. Stack 5 fading. Community resilience thread.",
        "expendable": True,
        "met": True,
        "location": "Thornfield — tavern",
        "alive": True,
    },
    "teilen": {
        "name": "Teilen",
        "points_to": ["lady_nyx", "pallid_march"],
        "function": "Millhaven Watch sergeant. Transactional military contact. His reports feed the chain that tracks Lady Nyx's advance columns.",
        "expendable": True,
        "met": True,
        "location": "Millhaven — watch post",
        "alive": True,
    },
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_npc(name: str) -> dict:
    """
    Check if an NPC exists in either registry.
    Returns the NPC data and classification, or an error.
    Call this BEFORE introducing any named character in a scene.
    """
    name_lower = name.lower().replace(" ", "_")

    if name_lower in MAIN_NPCS:
        return {
            "valid": True,
            "type": "MAIN",
            "data": MAIN_NPCS[name_lower],
            "warning": None,
        }

    if name_lower in SECONDARY_NPCS:
        npc = SECONDARY_NPCS[name_lower]
        return {
            "valid": True,
            "type": "SECONDARY",
            "data": npc,
            "points_to": npc["points_to"],
            "warning": f"Secondary NPC. Must serve: {', '.join(npc['points_to'])}",
        }

    return {
        "valid": False,
        "type": None,
        "data": None,
        "error": f"NPC '{name}' NOT IN REGISTRY. Cannot introduce. "
                 f"Either add them to SECONDARY_NPCS with a points_to link, "
                 f"or use a disposable unnamed NPC (no name, no plot knowledge, "
                 f"transactional only, points to a tracked NPC if asked).",
    }


def validate_scene(npcs_in_scene: list, threat_id: str = None) -> dict:
    """
    Validate an entire scene before presenting it.

    Args:
        npcs_in_scene: list of NPC name strings appearing in the scene
        threat_id: which campaign threat this scene connects to (optional but recommended)

    Returns:
        dict with 'valid', 'errors', and 'warnings'
    """
    errors = []
    warnings = []

    # Check all NPCs
    for npc_name in npcs_in_scene:
        result = validate_npc(npc_name)
        if not result["valid"]:
            errors.append(result["error"])
        elif result["type"] == "SECONDARY":
            warnings.append(result["warning"])

    # Check threat routing
    if threat_id:
        if threat_id not in THREATS and threat_id != "coalition":
            errors.append(f"Threat '{threat_id}' does not exist. Valid: {list(THREATS.keys()) + ['coalition']}")
    else:
        warnings.append("No threat_id specified. Every scene should connect to a campaign threat.")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def get_threat_npcs(threat_id: str) -> dict:
    """
    Get all NPCs (main + secondary) associated with a threat.
    Use this to see who's available for a scene in a given threat's territory.
    """
    if threat_id not in THREATS and threat_id != "coalition":
        return {"error": f"Unknown threat: {threat_id}"}

    main = {k: v for k, v in MAIN_NPCS.items()
            if v["threat"] == threat_id}
    secondary = {k: v for k, v in SECONDARY_NPCS.items()
                 if threat_id in v["points_to"]}

    return {
        "threat": threat_id,
        "main_npcs": main,
        "secondary_npcs": secondary,
        "total": len(main) + len(secondary),
    }


def check_npc_function(npc_name: str) -> str:
    """
    Quick check: what is this NPC's purpose and who do they point to?
    Use this when writing a secondary NPC's dialogue or actions to stay on track.
    """
    name_lower = npc_name.lower().replace(" ", "_")

    if name_lower in MAIN_NPCS:
        npc = MAIN_NPCS[name_lower]
        return f"MAIN NPC: {npc['name']} | Threat: {npc['threat']} | Goal: {npc['goal']}"

    if name_lower in SECONDARY_NPCS:
        npc = SECONDARY_NPCS[name_lower]
        return (f"SECONDARY NPC: {npc['name']} | Points to: {', '.join(npc['points_to'])} | "
                f"Function: {npc['function']} | Expendable: {npc['expendable']}")

    return f"NPC '{npc_name}' NOT FOUND. Do not introduce."


def register_secondary_npc(key: str, name: str, points_to: list,
                           function: str, expendable: bool = True,
                           met: bool = False, location: str = "unknown") -> dict:
    """
    Register a new secondary NPC during play.
    REQUIRES a points_to link to at least one main NPC or threat.
    The AI must call this before using any new named character.
    """
    if not points_to:
        return {"error": "Cannot register NPC without points_to. Every secondary NPC must serve the campaign."}

    # Validate that points_to targets exist (MAIN NPCs or threats ONLY — no secondary chains)
    valid_targets = set(MAIN_NPCS.keys()) | set(THREATS.keys()) | {"coalition"}
    for target in points_to:
        if target not in valid_targets:
            return {"error": f"points_to target '{target}' not in MAIN_NPCS or THREATS. Secondary NPCs ALWAYS point to main NPCs — no chains."}

    SECONDARY_NPCS[key] = {
        "name": name,
        "points_to": points_to,
        "function": function,
        "expendable": expendable,
        "met": met,
        "location": location,
        "alive": True,
    }
    return {"success": True, "registered": key, "points_to": points_to}


def campaign_status() -> dict:
    """
    Quick snapshot of all 5 threats. Call at session start or chapter end.
    """
    status = {}
    for tid, threat in THREATS.items():
        status[tid] = {
            "name": threat["name"],
            "progress": f"{threat['current_progress']}%",
            "days_to_critical": threat["clock_days"],
            "status": threat["status"],
            "npcs_met": sum(1 for npc_id in threat["key_npcs"]
                          if npc_id in MAIN_NPCS and MAIN_NPCS[npc_id]["met"]),
            "npcs_total": len(threat["key_npcs"]),
        }
    return status


def scene_checklist(npcs: list, threat: str, location: str) -> str:
    """
    Pre-scene validation. Returns a formatted checklist the AI should
    mentally run through before writing any scene.
    """
    lines = ["=== CONTINUITY ENGINE — SCENE CHECK ==="]
    lines.append(f"Location: {location}")
    lines.append(f"Threat: {threat}")
    lines.append("")

    # Validate threat
    if threat not in THREATS and threat != "coalition":
        lines.append(f"❌ THREAT '{threat}' INVALID")
        return "\n".join(lines)
    else:
        lines.append(f"✓ Threat valid: {THREATS[threat]['name'] if threat in THREATS else 'Coalition'}")

    # Validate NPCs
    lines.append("")
    for npc in npcs:
        result = validate_npc(npc)
        if result["valid"]:
            npc_type = result["type"]
            if npc_type == "MAIN":
                lines.append(f"✓ {npc} — MAIN NPC ({result['data']['threat']})")
            else:
                lines.append(f"✓ {npc} — SECONDARY → points to: {', '.join(result['data']['points_to'])}")
        else:
            lines.append(f"❌ {npc} — NOT IN REGISTRY. DO NOT USE.")

    lines.append("")
    lines.append("=== END CHECK ===")
    return "\n".join(lines)


# =============================================================================
# SELF-TEST — Run this file directly to verify integrity
# =============================================================================

# =============================================================================
# CHECK ENGINE — Master validation command
# =============================================================================
# When the player says "check engine", the AI runs THIS function.
# It replaces the old long-form request:
#   (dm aura checks, update as needed, kenji state, check statuses, perks,
#    weather, time, engine, cha trackers, dm rules, npc_name_bank.md,
#    kenji state file, world map.)
#
# The AI reads the output and fixes any issues found before continuing gameplay.

def check_engine(state: dict = None) -> str:
    """
    Master validation. Run when player says 'check engine'.
    
    Args:
        state: dict with current game state. Expected keys:
            - hour (float)
            - day (int)
            - location (str)
            - hp / max_hp (int)
            - exp (int)
            - meals (int)
            - hours_since_meal (float)
            - weather (str)
            - npcs_in_scene (list of str)
            - threat_id (str)
            - aura_targets (list of dicts with name, stack, last_save_time)
            - active_buffs (list of str)
            - charges (dict)
    
    Returns:
        Formatted checklist string with issues flagged.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("CHECK ENGINE — FULL STATE AUDIT")
    lines.append("=" * 60)
    
    if state is None:
        lines.append("")
        lines.append("NO STATE PROVIDED. AI must read kenji_state.json and pass")
        lines.append("the current values to this function. Checklist items:")
        lines.append("")
        lines.append("  [ ] 1. READ kenji_state.json — get all live values")
        lines.append("  [ ] 2. AURA CHECKS — roll/track IP for all nearby NPCs")
        lines.append("  [ ] 3. TIME/WEATHER — update hour, check meal timer")
        lines.append("  [ ] 4. SCENE VALIDATION — validate_scene() for NPCs present")
        lines.append("  [ ] 5. THREAT ROUTING — which threat does current scene serve?")
        lines.append("  [ ] 6. STATUS/PERKS — Living Ground range, Vigor timers, charges")
        lines.append("  [ ] 7. CHARACTER TRACKER — sync locations, dispositions, stacks")
        lines.append("  [ ] 8. DM RULES ACTIVE CONTEXT — update location, time, threads")
        lines.append("  [ ] 9. NPC NAME BANK — mark any newly used names")
        lines.append("  [ ] 10. WORLD CALENDAR — verify date, countdown timers")
        lines.append("  [ ] 11. CAMPAIGN STATUS — campaign_status() for all 5 clocks")
        lines.append("  [ ] 12. WRITE UPDATES — push changes to all affected files")
        lines.append("")
        lines.append("The AI MUST complete ALL 12 steps before resuming gameplay.")
        return "\n".join(lines)
    
    # --- With state provided, validate ---
    lines.append("")
    
    # Time and hunger
    hour = state.get("hour", 0)
    hsm = state.get("hours_since_meal", 0)
    lines.append(f"TIME: Day {state.get('day', '?')}, hour {hour:.2f}")
    if hsm >= 4:
        lines.append(f"  \!\! HUNGER PENALTY — {hsm:.1f} hrs since meal (max 4)")
    elif hsm >= 3.5:
        lines.append(f"  \! HUNGER WARNING — {hsm:.1f} hrs, penalty at 4.0")
    else:
        lines.append(f"  OK — {hsm:.1f} hrs since meal")
    
    # HP
    hp = state.get("hp", 0)
    max_hp = state.get("max_hp", 0)
    if hp < max_hp:
        lines.append(f"HP: {hp}/{max_hp} — NOT FULL")
    else:
        lines.append(f"HP: {hp}/{max_hp} — full")
    
    # Meals
    meals = state.get("meals", 0)
    if meals <= 2:
        lines.append(f"  \!\! MEALS LOW: {meals} remaining")
    else:
        lines.append(f"  Meals: {meals}")
    
    # Scene validation
    npcs = state.get("npcs_in_scene", [])
    threat = state.get("threat_id", None)
    if npcs:
        result = validate_scene(npcs, threat)
        lines.append("")
        lines.append("SCENE VALIDATION:")
        lines.append(f"  Valid: {result['valid']}")
        for e in result["errors"]:
            lines.append(f"  \!\! ERROR: {e}")
        for w in result["warnings"]:
            lines.append(f"  \! WARN: {w}")
    
    # Aura checks
    aura_targets = state.get("aura_targets", [])
    if aura_targets:
        lines.append("")
        lines.append("AURA STATUS (IP DC 23):")
        for t in aura_targets:
            name = t.get("name", "?")
            stack = t.get("stack", 0)
            status = "OK"
            if stack >= 5:
                status = "OBSESSED — cannot voluntarily leave LOS"
            elif stack >= 4:
                status = "FIXATED — disadvantage on saves"
            elif stack >= 3:
                status = "INTERESTED — positioning shift"
            lines.append(f"  {name}: Stack {stack} ({status})")
    
    # Campaign status
    lines.append("")
    lines.append("CAMPAIGN CLOCKS:")
    for tid, s in campaign_status().items():
        lines.append(f"  {s['name']:25s} | {s['progress']:5s} | {s['days_to_critical']:3d}d")
    
    # Charges
    charges = state.get("charges", {})
    if charges:
        lines.append("")
        lines.append("CHARGES:")
        for name, vals in charges.items():
            if isinstance(vals, (list, tuple)) and len(vals) >= 2:
                current, maximum = vals[0], vals[1]
                tag = "OK" if current > 0 else "EMPTY"
                lines.append(f"  [{tag}] {name}: {current}/{maximum}")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("FILES TO UPDATE AFTER CHECK:")
    lines.append("  - kenji_state.json (hour, location, exp, statuses)")
    lines.append("  - character_tracker.md (NPC locations, dispositions, stacks)")
    lines.append("  - dm_rules_tracking.md (active context section)")
    lines.append("  - AI_CONTEXT.md (where we left off, time, place)")
    lines.append("  - world_calendar_lore.md (if date/time changed)")
    lines.append("  - npc_name_bank.md (if new names introduced)")
    lines.append("=" * 60)
    
    return "\n".join(lines)


# =============================================================================
# SELF-TEST
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("CONTINUITY ENGINE - SELF TEST")
    print("=" * 60)
    print("")
    print("--- Test 1: Threat NPC references ---")
    all_reg = set(MAIN_NPCS.keys()) | set(SECONDARY_NPCS.keys())
    for tid, threat in THREATS.items():
        for npc_id in threat["key_npcs"]:
            tag = "OK" if npc_id in all_reg else "MISSING"
            print(f"  [{tag}] {tid}: {npc_id}")
    print("")
    print("--- Test 2: Secondary NPC points_to (MAIN only) ---")
    valid_targets = set(MAIN_NPCS.keys()) | set(THREATS.keys()) | {"coalition"}
    for key, npc in SECONDARY_NPCS.items():
        for target in npc["points_to"]:
            tag = "OK" if target in valid_targets else "BROKEN"
            print(f"  [{tag}] {key} -> {target}")
    print("")
    print("--- Test 3: Campaign Status ---")
    for tid, s in campaign_status().items():
        print(f"  {s['name']:25s} | {s['progress']:5s} | {s['days_to_critical']:3d}d | Met: {s['npcs_met']}/{s['npcs_total']}")
    print("")
    print("--- Test 4: Good scene ---")
    r = validate_scene(["jostin", "brynn"], "pallid_march")
    print(f"  Valid: {r['valid']}")
    for w in r["warnings"]:
        print(f"  WARN: {w}")
    print("")
    print("--- Test 5: Fabricated NPC ---")
    r = validate_scene(["jostin", "bone_architect"], "pallid_march")
    print(f"  Valid: {r['valid']}")
    for e in r["errors"]:
        print(f"  ERROR: {e}")
    print("")
    print("--- Test 6: Check Engine (no state) ---")
    print(check_engine())
    print("")
    print("--- Test 7: Check Engine (with state) ---")
    test_state = {
        "hour": 8.5,
        "day": 249,
        "hp": 333,
        "max_hp": 333,
        "meals": 5,
        "hours_since_meal": 2.25,
        "npcs_in_scene": ["jostin", "brynn"],
        "threat_id": "pallid_march",
        "aura_targets": [
            {"name": "Brynn", "stack": 5},
        ],
        "charges": {
            "Wind Step": [5, 5],
            "Smoke Bomb": [3, 3],
            "Phantom Double": [2, 2],
        },
    }
    print(check_engine(test_state))
    print("")
    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
