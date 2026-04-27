#!/usr/bin/env python3
"""Starter Campaign Generator — generates a full levels 1–10 campaign package
for a new character in the Kingdom of Ankunyx.

Usage:
    python generate_starter_campaign.py                  # interactive mode
    python generate_starter_campaign.py --name "Kael" \
        --race "Half-Orc" --class "Barbarian" \
        --background "Orphan raised by Sunderplains orc mercenaries" \
        --goal "Build a fighting school in the frontier" \
        --region frontier                                # CLI mode

Reads:
    ../shared_world_continuity.md
    ../realm_lore_registry.json
    ../templates/new_character_campaign.template.json

Writes:
    ../<CharName>/Game init files/character_world_state.json
    Updates ../realm_lore_registry.json with 3 new locations
    Prints the campaign package to stdout

Requires an AI backend for generation. If no AI is available, creates
the folder structure with a prompted template ready for manual fill.
"""

import json
import os
import sys
import textwrap
from pathlib import Path
from datetime import datetime
from copy import deepcopy

# ---------------------------------------------------------------------------
# Paths — walk upward until we find realm_lore_registry.json (TTRPG root)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent               # Game init files/

def _find_ttrpg_root(start: Path) -> Path:
    """Walk up from start until we find realm_lore_registry.json."""
    cur = start
    for _ in range(10):
        if (cur / "realm_lore_registry.json").exists():
            return cur
        cur = cur.parent
    # Fallback: try common mount patterns
    for candidate in [start.parent.parent, start.parent]:
        if (candidate / "realm_lore_registry.json").exists():
            return candidate
    raise FileNotFoundError(
        f"Cannot find TTRPG root (realm_lore_registry.json) from {start}. "
        "Run from inside Game init files/ or set TTRPG_ROOT env var."
    )

TTRPG_DIR = Path(os.environ.get("TTRPG_ROOT", "")) if os.environ.get("TTRPG_ROOT") else _find_ttrpg_root(SCRIPT_DIR)
TEMPLATE_PATH = TTRPG_DIR / "templates" / "new_character_campaign.template.json"
REGISTRY_PATH = TTRPG_DIR / "realm_lore_registry.json"
CONTINUITY_PATH = TTRPG_DIR / "shared_world_continuity.md"

# ---------------------------------------------------------------------------
# Known world anchors (for geographic placement)
# ---------------------------------------------------------------------------
REGION_ANCHORS = {
    "heartland": {
        "near": ["Varenholm", "Duskfen", "Bleakmoor"],
        "vibe": "institutional, urban, kingdom infrastructure everywhere",
        "travel": "days to Varenholm",
        "crown_position": "inside kingdom — deep core",
    },
    "frontier": {
        "near": ["Thornfield", "Briarstone", "Millhaven", "Greenveil"],
        "vibe": "sparse, rural, Crown attention thin",
        "travel": "weeks to Varenholm by road",
        "crown_position": "border — kingdom law exists on paper, enforcement patchy",
    },
    "coast": {
        "near": ["Stormhaven", "Ashenmere"],
        "vibe": "port towns, maritime trade, naval presence",
        "travel": "1-2 weeks to Varenholm by ship or road",
        "crown_position": "inside kingdom — trade hub",
    },
    "mountains": {
        "near": ["Dragonspine", "Kharn-Dural", "Cinderpeak"],
        "vibe": "mining, dwarven influence, dragon territory nearby",
        "travel": "2-3 weeks to Varenholm, mountain passes",
        "crown_position": "border — dwarven/dragon jurisdiction overlaps",
    },
    "underground": {
        "near": ["Kharn-Dural", "Ashward Mines", "Cinderpeak"],
        "vibe": "tunnels, dwarven architecture, deep resources",
        "travel": "variable — underground express or weeks overland",
        "crown_position": "inside kingdom — dwarven territorial autonomy",
    },
}

# Lore seeds that connect to existing unresolved threads
LORE_SEEDS = [
    {
        "thread": "Anku Conspiracy — missing Ankuspawn",
        "seed": "A young person in the area vanished recently. Locals say they had strange golden eyes. An older woman at the inn sighs and says 'another one' when asked.",
        "connects_to": "Cult of Anku kidnapping Ankuspawn",
    },
    {
        "thread": "Construct portal network — forgotten node",
        "seed": "An ancient stone archway in the ruins hums faintly at dawn. A dwarf trader mentions the old portal network 'had more nodes than the maps show.'",
        "connects_to": "Pre-kingdom portal infrastructure",
    },
    {
        "thread": "Vigor anomaly — unregistered bonded",
        "seed": "A local healer notices the discovery location has plants growing at unnatural speed. 'The soil remembers someone powerful,' she says. Traces of Vigor energy from a forgotten encounter.",
        "connects_to": "Kenji's wandering and untracked Vigor residue",
    },
    {
        "thread": "Iron Crown War remnant",
        "seed": "Old weapon caches from the Iron Crown War surface in the discovery location. Among them, a sealed letter bearing the sigil of a commander long dead — but the orders inside reference a contingency that was never activated.",
        "connects_to": "Unfinished Iron Crown War threads",
    },
    {
        "thread": "Dragon treaty — edge case",
        "seed": "A young dragon has been spotted near the adventure site — too small to be a flight elder, too bold to be following treaty rules. Is it lost, rebellious, or sent?",
        "connects_to": "Dragon treaty enforcement and Dragonspine politics",
    },
    {
        "thread": "Orc mercenary dispute",
        "seed": "A Sunderplains orc patrol refuses to enter the area around the adventure site. Their captain says only: 'The old contract doesn't cover that ground. Ask the Emperor why.'",
        "connects_to": "Orc mercenary corps jurisdiction and kingdom gaps",
    },
    {
        "thread": "Elixir trade — consumer end",
        "seed": "A wealthy merchant in the area is visibly younger than they should be. They credit 'a tonic from the Academy.' The price was a small fortune and a promise not to ask what's in it.",
        "connects_to": "Nyx's elixir distribution network",
    },
    {
        "thread": "Pip's missing child",
        "seed": "A traveler at the home base inn mentions meeting a kind innkeeper up north whose child went missing. 'Sad story. Gold eyes, that kid had. Went east and never wrote back.'",
        "connects_to": "Pip's frozen goal — direct on-ramp to Anku Conspiracy",
    },
]

# Antagonist archetypes scaled for levels 5-8
ANTAGONIST_ARCHETYPES = [
    {
        "type": "Bandit Lord",
        "level": 7,
        "class": "Fighter/Rogue",
        "style": "Controls the roads, extorts travelers, threatens commerce",
        "goal_conflict": "destroy | obstruct",
    },
    {
        "type": "Corrupt Official",
        "level": 6,
        "class": "Enchanter/Noble",
        "style": "Uses legal authority to squeeze the region, bribery and intimidation",
        "goal_conflict": "corrupt | exploit",
    },
    {
        "type": "Cult Leader",
        "level": 8,
        "class": "Warlock/Cleric",
        "style": "Small local cult, dark rituals, disappearances — NOT connected to Anku Conspiracy",
        "goal_conflict": "corrupt | destroy",
    },
    {
        "type": "Rival Adventurer",
        "level": 7,
        "class": "Mirror of PC class",
        "style": "Wants the same prize, willing to cheat and kill for it",
        "goal_conflict": "rival",
    },
    {
        "type": "Beast Master",
        "level": 6,
        "class": "Ranger/Druid (corrupted)",
        "style": "Controls dangerous creatures, terrorizes the area",
        "goal_conflict": "destroy | obstruct",
    },
    {
        "type": "Warlord Remnant",
        "level": 8,
        "class": "Warlord/Fighter",
        "style": "Pre-kingdom holdout who never accepted Ankunyx rule, gathering a militia",
        "goal_conflict": "destroy | rival",
    },
    {
        "type": "Smuggler Baron",
        "level": 6,
        "class": "Rogue/Merchant",
        "style": "Black market operation, poisons the local economy",
        "goal_conflict": "exploit | corrupt",
    },
    {
        "type": "Undead Commander",
        "level": 7,
        "class": "Death Knight / Necromancer",
        "style": "Pre-treaty undead threat that slipped through the cracks when Nyx consolidated",
        "goal_conflict": "destroy",
    },
]


# ---------------------------------------------------------------------------
# Ember Inheritance — algorithmic generation for Ankuspawn characters
# See ankuspawn_race.md § Ember Inheritance for full rules.
# ---------------------------------------------------------------------------

EMBER_THEMES = {
    "resonance": {
        "keywords": ["bard", "dancer", "performer", "singer", "musician", "charm",
                      "fame", "inspire", "entertain", "song", "voice", "dance",
                      "charisma", "audience", "stage", "troupe", "troubadour"],
        "enhances": "Voice, sound, emotional projection, crowd control, performance magic",
        "nyx_extract": "Emotional resonance essence",
        "nyx_product": "Charm elixirs, mass suggestion potions, crowd-control compounds",
    },
    "aegis": {
        "keywords": ["paladin", "guardian", "protector", "shield", "defend", "save",
                      "shelter", "ward", "guard", "sentinel", "bastion", "bulwark",
                      "escort", "bodyguard", "fortify"],
        "enhances": "Defensive auras, damage absorption, warding, threat interception",
        "nyx_extract": "Protective aura fragments",
        "nyx_product": "Invulnerability serums, damage-immune coatings, ward stones",
    },
    "edge": {
        "keywords": ["fighter", "warrior", "blade", "weapon", "combat", "martial",
                      "conquer", "strength", "soldier", "mercenary", "gladiator",
                      "berserker", "barbarian", "ronin", "samurai", "knight", "sword"],
        "enhances": "Weapon mastery, combat instinct, physical augmentation, battle sense",
        "nyx_extract": "Combat instinct essence",
        "nyx_product": "Weapon mastery potions, battle-rage serums, reflex enhancers",
    },
    "veil": {
        "keywords": ["rogue", "assassin", "thief", "stealth", "shadow", "spy",
                      "escape", "survive", "scout", "infiltrate", "sneak", "pickpocket",
                      "burglar", "phantom", "ghost"],
        "enhances": "Invisibility, misdirection, sensory suppression, evasion",
        "nyx_extract": "Sensory-void particles",
        "nyx_product": "Invisibility elixirs, memory-wipe compounds, detection-proof coatings",
    },
    "crucible": {
        "keywords": ["smith", "crafter", "builder", "forge", "construct", "create",
                      "make", "engineer", "artificer", "inventor", "tinker", "artisan",
                      "blacksmith", "jeweler", "architect"],
        "enhances": "Material shaping, enchanting through touch, structural reinforcement",
        "nyx_extract": "Material-bonding essence",
        "nyx_product": "Enchanting catalysts, indestructible alloy treatments, golem-core fuel",
    },
    "verdance": {
        "keywords": ["druid", "ranger", "nature", "beast", "wild", "hunt", "track",
                      "grow", "animal", "forest", "herbalist", "shaman", "warden",
                      "beastmaster", "farm"],
        "enhances": "Plant/animal communion, accelerated healing, environmental sense",
        "nyx_extract": "Life-force concentrate",
        "nyx_product": "Resurrection reagents, fertility elixirs, aging reversal",
    },
    "lumen": {
        "keywords": ["cleric", "priest", "healer", "cure", "purify", "holy", "faith",
                      "restore", "temple", "divine", "sacred", "monk", "acolyte",
                      "chaplain", "missionary"],
        "enhances": "Radiant energy, purification, anti-undead, wound closure",
        "nyx_extract": "Radiant essence",
        "nyx_product": "Anti-undead weapons, purification reagents, divine-channel fuel",
    },
    "tempest": {
        "keywords": ["sorcerer", "wizard", "mage", "arcane", "power", "destroy",
                      "elemental", "chaos", "warlock", "conjurer", "evoker",
                      "pyromancer", "cryomancer", "lightning", "fire", "ice", "storm"],
        "enhances": "Raw elemental force, energy manipulation, magical amplification",
        "nyx_extract": "Raw magical condensate",
        "nyx_product": "Spell amplifiers, mana batteries, elemental weapon coatings",
    },
    "nexus": {
        "keywords": ["diplomat", "leader", "commander", "unite", "alliance", "kingdom",
                      "rule", "noble", "general", "captain", "warden", "governor",
                      "chieftain", "marshal", "strategist"],
        "enhances": "Emotional bonds, loyalty auras, group empowerment, morale",
        "nyx_extract": "Loyalty-bond extract",
        "nyx_product": "Domination elixirs, unbreakable oath seals, army-morale compounds",
    },
}


def generate_ember_inheritance(class_concept: str, personal_goal: str,
                                name: str, race: str) -> dict | None:
    """Generate an Ember inheritance block for an Ankuspawn character.

    Returns None for non-Ankuspawn characters.
    The algorithm:
      1. Combine class_concept + personal_goal into a keyword pool
      2. Score each theme by keyword matches
      3. Pick the highest-scoring theme (ties broken by goal keywords > class keywords)
      4. Generate 3 abilities (passive, active, surge) as scaffolds
      5. Assign Nyx harvest priority based on theme rarity + female bonus

    The specific ability NAMES and DESCRIPTIONS are scaffolds for DM/AI creative fill.
    """
    # Only Ankuspawn get Ember
    race_lower = race.lower()
    if "ankuspawn" not in race_lower and "anku" not in race_lower:
        return None

    # Build keyword pool — goal words weighted 2x (goal = who they WANT to be)
    class_words = set(class_concept.lower().replace("/", " ").replace("-", " ").split())
    goal_words = set(personal_goal.lower().replace("/", " ").replace("-", " ").split())
    combined = class_words | goal_words

    # Score each theme
    scores = {}
    for theme_name, theme_data in EMBER_THEMES.items():
        kws = set(theme_data["keywords"])
        class_hits = len(class_words & kws)
        goal_hits = len(goal_words & kws)
        # Goal keywords count double — the goal is who they want to BE
        scores[theme_name] = class_hits + (goal_hits * 2)

    # Pick best theme (ties: use name hash for deterministic pick)
    max_score = max(scores.values())
    candidates = [t for t, s in scores.items() if s == max_score]
    if len(candidates) > 1:
        pick_idx = hash(name + race) % len(candidates)
        chosen_theme = sorted(candidates)[pick_idx % len(candidates)]
    else:
        chosen_theme = candidates[0]

    theme_data = EMBER_THEMES[chosen_theme]

    # Determine Nyx target priority
    # Female Ankuspawn are always higher priority (more potent extracts)
    # Some themes are rarer/more valuable
    high_value_themes = {"verdance", "resonance", "nexus", "tempest"}
    is_female = any(w in race_lower or w in class_concept.lower()
                    for w in ["female", "woman", "girl", "she", "her"])
    # For priority, also check if DM marked gender in player_input (handled at call site)
    if chosen_theme in high_value_themes:
        priority = "critical" if is_female else "high"
    else:
        priority = "high" if is_female else "medium"

    return {
        "_rule": "Ankuspawn only. Generated from class_concept + personal_goal. "
                 "Player does NOT choose. Theme-locked — refuses off-theme use. "
                 "See ankuspawn_race.md § Ember Inheritance.",
        "theme": chosen_theme,
        "theme_description": (
            f"[DM FILL: One sentence — why '{chosen_theme}' fits {name}. "
            f"This Ember enhances: {theme_data['enhances']}]"
        ),
        "abilities": {
            "passive": {
                "name": f"[{chosen_theme.upper()} PASSIVE — always active]",
                "description": f"[DM FILL: Low-level {chosen_theme} enhancement that colors everything {name} does]",
                "mechanical_effect": "[DM FILL: Game terms]",
            },
            "active": {
                "name": f"[{chosen_theme.upper()} ACTIVE — conscious activation]",
                "description": f"[DM FILL: Moderate {chosen_theme} ability, multiple uses per day]",
                "mechanical_effect": "[DM FILL: Game terms]",
                "uses_per_day": "3 (scales with level)",
            },
            "surge": {
                "name": f"[{chosen_theme.upper()} SURGE — emergency, 1/long rest]",
                "description": f"[DM FILL: Major {chosen_theme} burst — a flash of Kenji's power, burns to channel]",
                "mechanical_effect": "[DM FILL: Game terms]",
                "exhaustion_cost": "1 level of exhaustion after use",
            },
        },
        "theme_lock": [
            f"This Ember ONLY enhances: {theme_data['enhances']}.",
            f"[DM FILL: List 3-5 specific things {name} might try that the Ember REFUSES to do]",
        ],
        "growth_stage": "unreliable",
        "nyx_harvest_value": {
            "extract_type": theme_data["nyx_extract"],
            "elixir_product": theme_data["nyx_product"],
            "target_priority": priority,
        },
    }


def load_template() -> dict:
    """Load the campaign template."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_registry() -> dict:
    """Load the realm lore registry."""
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_existing_locations(registry: dict) -> set:
    """Extract all known location names from the registry."""
    locations = set()
    kingdom = registry.get("kingdom", {})
    for t in kingdom.get("territories", []):
        # Extract location names from territory strings
        for part in t.split("(")[0].split(","):
            locations.add(part.strip())
    # Also check campaigns for established regions
    for campaign in registry.get("campaigns", []):
        for region in campaign.get("regions_established", []):
            locations.add(region)
    return locations


def interactive_input() -> dict:
    """Gather character inputs interactively."""
    print("=" * 60)
    print("  STARTER CAMPAIGN GENERATOR")
    print("  Kingdom of Ankunyx — 25 years post-Book 4")
    print("=" * 60)
    print()

    name = input("Character name: ").strip()
    race = input("Race (human, elf, half-orc, dwarf, ankuspawn, etc.): ").strip()
    class_concept = input("Class concept (e.g. 'barbarian berserker', 'hedge wizard'): ").strip()

    print()
    print("Background — where they grew up, who they lost, what shaped them:")
    background = input("> ").strip()

    print()
    print("Personal goal — one sentence, what the character wants MOST:")
    print("  (This becomes the campaign's central objective)")
    goal = input("> ").strip()

    print()
    print("Starting region preference:")
    for key, info in REGION_ANCHORS.items():
        print(f"  {key:12s} — near {', '.join(info['near'][:3])}; {info['vibe'][:50]}")
    region = input("Choice [frontier]: ").strip().lower() or "frontier"

    return {
        "name": name,
        "race": race,
        "class_concept": class_concept,
        "background": background,
        "personal_goal": goal,
        "starting_region_preference": region,
    }


def generate_campaign_scaffold(player_input: dict) -> dict:
    """Generate a starter campaign scaffold from player inputs.

    This creates the structural framework with placeholder content.
    An AI session or manual DM work fills in the creative details.
    """
    template = load_template()
    registry = load_registry()
    existing = get_existing_locations(registry)

    name = player_input["name"]
    region_pref = player_input.get("starting_region_preference", "frontier")
    region_info = REGION_ANCHORS.get(region_pref, REGION_ANCHORS["frontier"])
    goal = player_input["personal_goal"]
    background = player_input["background"]

    # Pick a lore seed (rotate based on character name hash)
    seed_idx = hash(name) % len(LORE_SEEDS)
    lore_seed = LORE_SEEDS[seed_idx]

    # Pick an antagonist archetype
    ant_idx = hash(name + goal) % len(ANTAGONIST_ARCHETYPES)
    antagonist = ANTAGONIST_ARCHETYPES[ant_idx]

    # Fill the template
    campaign = deepcopy(template)

    # Player input
    campaign["player_input"] = player_input
    campaign["_saved_at"] = datetime.now().isoformat(timespec="seconds")

    # Inherited lore
    campaign["inherited_lore"]["lore_seed"] = (
        f"[{lore_seed['thread']}] {lore_seed['seed']} "
        f"(Connects to: {lore_seed['connects_to']})"
    )

    # Locations — scaffolded with region info, ready for creative fill
    campaign["locations"]["home_base"].update({
        "name": f"[NAME — {name}'s home base]",
        "from_worlds_middle": region_info["vibe"],
        "from_crown_realm": region_info["crown_position"],
        "nearest_named_anchor": region_info["near"][0],
        "travel_time_to_major_hub": region_info["travel"],
        "connection_to_character": f"Tied to {name}'s background: {background[:100]}",
        "registry_entry": f"[One sentence — {name}'s starting settlement near {region_info['near'][0]}]",
    })

    campaign["locations"]["adventure_site"].update({
        "name": f"[NAME — dangerous site near {region_info['near'][0]}]",
        "distance_from_home_base": "1-3 days travel",
        "why_dangerous": f"Base of operations for {antagonist['type']} ({antagonist['class']}). "
                         f"Threatens {name}'s goal: {goal[:80]}",
        "registry_entry": f"[One sentence — {antagonist['type']}'s lair near {region_info['near'][0]}]",
    })

    campaign["locations"]["discovery_location"].update({
        "name": f"[NAME — hidden/forgotten site in {region_pref} region]",
        "connection_to_existing_lore": lore_seed["connects_to"],
        "what_the_player_learns_here": lore_seed["seed"],
        "registry_entry": f"[One sentence — discovery site, connects to {lore_seed['thread']}]",
    })

    # Antagonist
    campaign["antagonist"].update({
        "name": f"[NAME — {antagonist['type']}]",
        "level_range": f"{antagonist['level']-1}–{antagonist['level']+1}",
        "race_and_class": antagonist["class"],
        "motivation": f"[Fill: why this {antagonist['type']} specifically conflicts with '{goal}']",
        "relationship_to_goal": antagonist["goal_conflict"],
        "defeat_consequences": f"[Fill: what changes in the {region_pref} region when the {antagonist['type']} falls]",
        "lieutenants": [
            {"name": "[Lieutenant 1]", "role": f"{antagonist['type']}'s enforcer", "location": "adventure_site"},
            {"name": "[Lieutenant 2]", "role": "Spy/informant in home base", "location": "home_base"},
            {"name": "[Lieutenant 3]", "role": "Guard at discovery location", "location": "discovery_location"},
        ],
    })

    # Campaign spine
    campaign["campaign_spine"]["phase_1_arrival"]["key_scenes"] = [
        f"{name} arrives at home base. Meets 2-3 friendly NPCs.",
        f"Learns that {goal} is possible but something blocks it.",
        f"First encounter with the {antagonist['type']}'s influence (not the villain directly).",
    ]
    campaign["campaign_spine"]["phase_2_achievement"]["key_scenes"] = [
        f"{name} achieves the goal: {goal}",
        f"Celebration or quiet victory — then the {antagonist['type']} notices.",
        "First direct threat to what was just built.",
    ]
    campaign["campaign_spine"]["phase_3_defense"]["key_scenes"] = [
        f"The {antagonist['type']} attacks what {name} built/found.",
        f"Allies are tested. One NPC may betray or be captured.",
        "Discovery location found — reveals connection to broader world.",
    ]
    campaign["campaign_spine"]["phase_4_confrontation"]["key_scenes"] = [
        f"Assault on the adventure site to end the {antagonist['type']} permanently.",
        f"{name}'s goal is secured. Home base is safe.",
        f"Lore seed payoff: {lore_seed['thread']} — hook for continuation.",
    ]

    # Main cast scaffold
    campaign["main_cast"] = [
        {
            "name": "[Ally 1 — home base]",
            "role": "ally",
            "location": "home_base",
            "want": f"Wants to help {name} achieve their goal",
            "voice_hook": "[Speech pattern]",
            "lore_connection": "",
        },
        {
            "name": "[Mentor — home base]",
            "role": "mentor",
            "location": "home_base",
            "want": "Peace and quiet after a long life",
            "voice_hook": "[Speech pattern]",
            "lore_connection": f"[Optional: served in the coalition, knew someone from {region_info['near'][0]}]",
        },
        {
            "name": "[Merchant — home base]",
            "role": "merchant",
            "location": "home_base",
            "want": "Profit, but fair about it",
            "voice_hook": "[Speech pattern]",
            "lore_connection": "",
        },
        {
            "name": "[Lore Bridge NPC]",
            "role": "lore_bridge",
            "location": "discovery_location",
            "want": "Someone to understand what this place was",
            "voice_hook": "[Speech pattern]",
            "lore_connection": f"Connects to {lore_seed['connects_to']}. This NPC teaches the player about the broader world.",
        },
        {
            "name": f"[{antagonist['type']}]",
            "role": "antagonist",
            "location": "adventure_site",
            "want": f"[Fill: what the {antagonist['type']} wants that conflicts with {name}'s goal]",
            "voice_hook": "[Speech pattern]",
            "lore_connection": "",
        },
    ]

    # Dialogue
    campaign["dialogue"] = {
        "intro_scene": f"{name} arrives at [home base]. [First NPC] greets them. The settlement is [describe]. The mood is [describe].",
        "rumor_mill_examples": [
            f"'Watch the road to [adventure site]. People have gone missing.'",
            f"'{antagonist['type']} has been getting bolder. Used to stay in the [terrain].'",
            f"'There's an old [ruin/cave/structure] east of here nobody goes near. Bad air, they say.'",
        ],
        "antagonist_confrontation_line": f"[{antagonist['type']}'s threatening speech when they first confront {name}]",
        "discovery_reveal_moment": f"The moment {name} realizes this place connects to something bigger: {lore_seed['thread']}",
        "peaceful_outro_hint": f"With the {antagonist['type']} gone, [home base] thrives. {name}'s goal — {goal} — stands. But the lore seed lingers...",
    }

    # Ember Inheritance (Ankuspawn only)
    race = player_input.get("race", "")
    class_concept = player_input.get("class_concept", "")
    ember = generate_ember_inheritance(class_concept, goal, name, race)
    if ember:
        # Override gender-based priority if gender is explicitly set
        gender = player_input.get("gender", "").lower()
        if gender in ("female", "f", "woman"):
            high_value = {"verdance", "resonance", "nexus", "tempest"}
            ember["nyx_harvest_value"]["target_priority"] = (
                "critical" if ember["theme"] in high_value else "high"
            )
        campaign["ember_inheritance"] = ember
    else:
        campaign["ember_inheritance"] = None

    # Success / failure states
    campaign["success_state"] = (
        f"{name}'s goal ({goal}) is permanently secured. The {antagonist['type']} is defeated. "
        f"All three locations are safe and added to the world map. "
        f"The lore seed ({lore_seed['thread']}) is revealed but unresolved — hook for continuation."
    )
    campaign["failure_state"] = (
        f"The {antagonist['type']} destroys or corrupts what {name} built. "
        f"The home base suffers — NPCs displaced, resources lost. "
        f"The region degrades. Future characters inherit a damaged area."
    )

    return campaign


def create_campaign_folder(name: str, campaign: dict) -> Path:
    """Create the campaign folder structure and write the state file."""
    # Sanitize name for folder
    folder_name = name.strip().replace(" ", "_")
    campaign_dir = TTRPG_DIR / folder_name / "Game init files"
    campaign_dir.mkdir(parents=True, exist_ok=True)

    state_file = campaign_dir / "character_world_state.json"
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(campaign, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return state_file


def register_locations(campaign: dict) -> int:
    """Add the 3 new locations to realm_lore_registry.json.
    Returns count of locations added."""
    registry = load_registry()

    # Ensure 'starter_campaign_locations' list exists
    if "starter_campaign_locations" not in registry:
        registry["starter_campaign_locations"] = []

    char_name = campaign["player_input"]["name"]
    locations = campaign.get("locations", {})
    added = 0

    for loc_type in ("home_base", "adventure_site", "discovery_location"):
        loc = locations.get(loc_type, {})
        if not loc:
            continue
        entry = {
            "name": loc.get("name", f"[Unnamed {loc_type}]"),
            "type": loc_type,
            "character": char_name,
            "registry_entry": loc.get("registry_entry", ""),
            "from_crown_realm": loc.get("from_crown_realm", ""),
            "added_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
        }
        registry["starter_campaign_locations"].append(entry)
        added += 1

    # Write back
    tmp = REGISTRY_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(REGISTRY_PATH)

    return added


def print_campaign_summary(campaign: dict):
    """Print a readable summary of the generated campaign."""
    pi = campaign["player_input"]
    locs = campaign["locations"]
    ant = campaign["antagonist"]
    spine = campaign["campaign_spine"]
    seed = campaign["inherited_lore"]["lore_seed"]

    print()
    print("=" * 60)
    print(f"  STARTER CAMPAIGN: {pi['name']}")
    print(f"  {pi['race']} {pi['class_concept']}")
    print("=" * 60)

    print(f"\n  PERSONAL GOAL: {pi['personal_goal']}")
    print(f"  BACKGROUND: {pi['background']}")
    print(f"  REGION: {pi['starting_region_preference']}")

    print(f"\n--- THREE NEW LOCATIONS ---")
    for loc_type, label in [("home_base", "HOME BASE"), ("adventure_site", "ADVENTURE SITE"), ("discovery_location", "DISCOVERY LOCATION")]:
        loc = locs.get(loc_type, {})
        print(f"\n  [{label}]")
        print(f"    Name: {loc.get('name', '?')}")
        if loc.get("nearest_named_anchor"):
            print(f"    Near: {loc['nearest_named_anchor']}")
        if loc.get("why_dangerous"):
            print(f"    Danger: {loc['why_dangerous'][:100]}")
        if loc.get("connection_to_existing_lore"):
            print(f"    Lore: {loc['connection_to_existing_lore']}")

    print(f"\n--- ANTAGONIST ---")
    print(f"    Name: {ant.get('name', '?')}")
    print(f"    Level: {ant.get('level_range', '?')}")
    print(f"    Class: {ant.get('race_and_class', '?')}")
    print(f"    Conflict: {ant.get('relationship_to_goal', '?')}")
    print(f"    Lieutenants: {len(ant.get('lieutenants', []))}")

    print(f"\n--- CAMPAIGN SPINE (Levels 1–10) ---")
    for phase_key, phase in spine.items():
        if phase_key.startswith("_"):
            continue
        if isinstance(phase, dict):
            label = phase_key.replace("phase_", "Phase ").replace("_", " ").title()
            print(f"\n  {label} (Levels {phase.get('levels', '?')})")
            print(f"    {phase.get('summary', '')[:120]}")
            for scene in phase.get("key_scenes", [])[:2]:
                print(f"      - {scene[:100]}")

    print(f"\n--- LORE SEED ---")
    print(f"    {seed[:200]}")

    print(f"\n--- SUCCESS STATE ---")
    print(f"    {campaign.get('success_state', '')[:200]}")

    print(f"\n--- FAILURE STATE ---")
    print(f"    {campaign.get('failure_state', '')[:200]}")

    # Ember Inheritance (Ankuspawn only)
    ember = campaign.get("ember_inheritance")
    if ember:
        print(f"\n--- EMBER INHERITANCE (Ankuspawn) ---")
        print(f"    Theme: {ember['theme'].upper()}")
        print(f"    Enhances: {EMBER_THEMES[ember['theme']]['enhances']}")
        print(f"    Growth: {ember.get('growth_stage', 'unreliable')}")
        nyx = ember.get("nyx_harvest_value", {})
        print(f"    Nyx Priority: {nyx.get('target_priority', '?').upper()}")
        print(f"    Extract: {nyx.get('extract_type', '?')}")
        print(f"    Product: {nyx.get('elixir_product', '?')}")
        for lock in ember.get("theme_lock", []):
            print(f"    LOCK: {lock[:120]}")

    print()
    print("=" * 60)
    print("  [NAME] fields need creative fill — run an AI session or")
    print("  edit character_world_state.json manually to finalize.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate a starter campaign (levels 1-10) for a new character.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Every new character adds 3 locations to the world map.
            See universe_campaign_framework.md § 2 for the full system.
        """),
    )
    parser.add_argument("--name", type=str, help="Character name")
    parser.add_argument("--race", type=str, help="Race")
    parser.add_argument("--class", dest="class_concept", type=str, help="Class concept")
    parser.add_argument("--background", type=str, help="Background story")
    parser.add_argument("--goal", type=str, help="Personal goal (one sentence)")
    parser.add_argument("--region", type=str, default="frontier",
                        choices=list(REGION_ANCHORS.keys()),
                        help="Starting region preference")
    parser.add_argument("--no-register", action="store_true",
                        help="Don't update realm_lore_registry.json")
    parser.add_argument("--no-folder", action="store_true",
                        help="Don't create the campaign folder (print only)")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of summary")

    args = parser.parse_args()

    # Interactive or CLI
    if args.name:
        player_input = {
            "name": args.name,
            "race": args.race or "",
            "class_concept": args.class_concept or "",
            "background": args.background or "",
            "personal_goal": args.goal or "",
            "starting_region_preference": args.region,
        }
    else:
        player_input = interactive_input()

    if not player_input["name"]:
        print("ERROR: Character name is required.")
        sys.exit(1)

    # Generate
    campaign = generate_campaign_scaffold(player_input)

    # Output
    if args.json:
        print(json.dumps(campaign, indent=2, ensure_ascii=False))
    else:
        print_campaign_summary(campaign)

    # Create folder
    if not args.no_folder:
        state_file = create_campaign_folder(player_input["name"], campaign)
        print(f"\n  Campaign file: {state_file}")

    # Register locations
    if not args.no_register:
        count = register_locations(campaign)
        print(f"  Registered {count} new locations in realm_lore_registry.json")

    print(f"\n  Next: fill [NAME] fields, then play!")


if __name__ == "__main__":
    main()
