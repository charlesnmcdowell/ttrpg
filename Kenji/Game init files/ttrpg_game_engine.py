#!/usr/bin/env python3
"""TTRPG Game Engine — combat resolution plus world/story state (single module).

Combat: dice, Combatant, Combat, EXPTracker, load_combatant, etc.
Story: StoryEngine for kenji_state.json — time, economy, clocks, dashboards, AI brief.

**NPC / character goals:** Operational goals that the engine can **date-check** and **optionally auto-advance** live in `kenji_state.json` → **`character_goals`** (list of dicts). The engine **does not** parse `character_tracker.md` markdown tables (fragile); keep tracker as prose-of-record and mirror critical rows into `character_goals` for automation. See `StoryEngine.process_character_goals()` and DM rule **GOAL INVARIANT** in `dm_rules_tracking.md`. Arc prose remains human-edited; the engine can append **`consequences`** / **`world_events`** from goal `on_resolve` payloads when `auto_resolve` is true.

Cross-references:
  DM behavior rules & referee handbook → dm_rules_tracking.md
  Character abilities & narrative details → character_tracker.md
  Live game state → kenji_state.json
  Archived Book 1-3 lore & stat blocks → dm_rules_archive_books1_3.md

CLI:
  python ttrpg_game_engine.py brief [path/to/state.json]   # default: ./kenji_state.json
  python ttrpg_game_engine.py skill <total_modifier> [--adv|--dis] [--dc N] [--label NAME]
  python ttrpg_game_engine.py              # story tests, then combat tests
  python ttrpg_game_engine.py combat-only  # combat tests only

**Scene skill gate (5e):** When fiction depends on Stealth, Sleight of Hand, social skills,
or contested perception/insight, the referee **rolls first** via `skill_roll()` / `ability_check()` /
`contested_skill()` below — **do not** narrate success tiers or NPC omniscience until totals vs DC
(or contest) are known. On a **PC success**, the beat goes **player-favorable**; no unstated
Perception auto-win or “chair creak” undo. NPCs use passive or rolled checks—never auto-success.
See `dm_rules_tracking.md` → **Scene skill preroll** + **Player success integrity**.
"""

import random, json, math
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any

def d20(): return random.randint(1, 20)

# character_goals.status values the engine treats as "still ticking" for due / overdue logic
ACTIVE_CHARACTER_GOAL_STATUSES = frozenset(
    {"active", "in_progress", "open", "overdue", "active_dm"}
)

def roll_dice(notation):
    notation = notation.strip().lower()
    mod = 0
    if '+' in notation:
        parts = notation.split('+'); dice_part = parts[0].strip(); mod = int(parts[1].strip())
    elif '-' in notation:
        parts = notation.split('-'); dice_part = parts[0].strip(); mod = -int(parts[1].strip())
    else: dice_part = notation
    if 'd' in dice_part:
        n, sides = dice_part.split('d'); n = int(n) if n else 1; sides = int(sides)
        rolls = [random.randint(1, sides) for _ in range(n)]
    else: rolls = [int(dice_part)]
    return sum(rolls) + mod, rolls, mod


# ---------------------------------------------------------------------------
# 5e-style scene skill gates — roll before narrating outcome-dependent fiction
# ---------------------------------------------------------------------------
# PHB skill → ability (STR/DEX/CON/INT/WIS/CHA) for building modifiers from raw stats.
SKILL_ABILITY_MAP: Dict[str, str] = {
    "Athletics": "STR",
    "Acrobatics": "DEX",
    "Sleight of Hand": "DEX",
    "Stealth": "DEX",
    "Arcana": "INT",
    "History": "INT",
    "Investigation": "INT",
    "Nature": "INT",
    "Religion": "INT",
    "Animal Handling": "WIS",
    "Insight": "WIS",
    "Medicine": "WIS",
    "Perception": "WIS",
    "Survival": "WIS",
    "Deception": "CHA",
    "Intimidation": "CHA",
    "Performance": "CHA",
    "Persuasion": "CHA",
}

# When a scene tag touches these, the table/engine convention is: **resolve dice first**, then prose.
SCENE_PREROLL_SKILLS = frozenset(SKILL_ABILITY_MAP.keys())
SCENE_PREROLL_ABILITIES = frozenset({"STR", "DEX", "CON", "INT", "WIS", "CHA"})


def ability_modifier(score: int) -> int:
    """5e ability modifier from score 1..30 (typical)."""
    return (int(score) - 10) // 2


def proficiency_bonus(character_level: int) -> int:
    """5e proficiency bonus by character level (2 at 1-4, +1 per four levels)."""
    lv = max(1, min(30, int(character_level)))
    return 2 + (lv - 1) // 4


def roll_d20_advantage(advantage: bool = False, disadvantage: bool = False) -> Tuple[int, List[int]]:
    """Roll d20 with optional adv/dis. If both, RAW cancels to a single die."""
    a, b = d20(), d20()
    if advantage and disadvantage:
        return a, [a]
    if advantage:
        return max(a, b), [a, b]
    if disadvantage:
        return min(a, b), [a, b]
    return a, [a]


def skill_roll(
    modifier: int,
    *,
    advantage: bool = False,
    disadvantage: bool = False,
    dc: Optional[int] = None,
    label: str = "skill check",
) -> Dict[str, Any]:
    """
    One PHB-style d20 + modifier, optional adv/dis, optional DC.
    Use for Stealth, Sleight of Hand, Persuasion, etc. after you compute **modifier** from stats + prof.
    """
    nat, raw = roll_d20_advantage(advantage, disadvantage)
    total = nat + int(modifier)
    out: Dict[str, Any] = {
        "kind": "skill",
        "label": label,
        "d20": raw,
        "d20_used": nat,
        "modifier": int(modifier),
        "total": total,
    }
    if dc is not None:
        out["dc"] = int(dc)
        out["success"] = total >= int(dc)
        out["margin"] = total - int(dc)
    return out


def ability_check(
    modifier: int,
    *,
    advantage: bool = False,
    disadvantage: bool = False,
    dc: Optional[int] = None,
    label: str = "ability check",
) -> Dict[str, Any]:
    """STR / DEX / CON / INT / WIS / CHA check (raw ability mod + situational bonuses in *modifier*)."""
    nat, raw = roll_d20_advantage(advantage, disadvantage)
    total = nat + int(modifier)
    out: Dict[str, Any] = {
        "kind": "ability",
        "label": label,
        "d20": raw,
        "d20_used": nat,
        "modifier": int(modifier),
        "total": total,
    }
    if dc is not None:
        out["dc"] = int(dc)
        out["success"] = total >= int(dc)
        out["margin"] = total - int(dc)
    return out


def saving_throw(
    modifier: int,
    *,
    advantage: bool = False,
    disadvantage: bool = False,
    dc: Optional[int] = None,
    label: str = "save",
) -> Dict[str, Any]:
    """WIS save vs IP, CON concentration, etc. Same math as ability_check; label for logs."""
    return ability_check(modifier, advantage=advantage, disadvantage=disadvantage, dc=dc, label=label)


def contested_skill(
    left_modifier: int,
    right_modifier: int,
    *,
    left_name: str = "A",
    right_name: str = "B",
    left_advantage: bool = False,
    left_disadvantage: bool = False,
    right_advantage: bool = False,
    right_disadvantage: bool = False,
) -> Dict[str, Any]:
    """
    Two opposed d20+mod totals (Stealth vs passive Perception rolled active, Perception vs Stealth, etc.).
    Tie → defender wins is a common table rule; here ties are reported as 'tie' for DM to apply house rule.
    """
    l_nat, l_raw = roll_d20_advantage(left_advantage, left_disadvantage)
    r_nat, r_raw = roll_d20_advantage(right_advantage, right_disadvantage)
    left_total = l_nat + int(left_modifier)
    right_total = r_nat + int(right_modifier)
    if left_total > right_total:
        winner = left_name
    elif right_total > left_total:
        winner = right_name
    else:
        winner = "tie"
    return {
        "kind": "contest",
        "left_name": left_name,
        "right_name": right_name,
        "left": {"d20": l_raw, "d20_used": l_nat, "modifier": int(left_modifier), "total": left_total},
        "right": {"d20": r_raw, "d20_used": r_nat, "modifier": int(right_modifier), "total": right_total},
        "winner": winner,
        "margin": left_total - right_total,
    }


def build_skill_modifier(
    ability_scores: Dict[str, Any],
    skill_name: str,
    *,
    character_level: int,
    proficiency: bool = True,
    expertise: bool = False,
    extra_bonus: int = 0,
) -> Tuple[int, str]:
    """
    Compute d20 modifier for a named PHB skill from ability_scores keys STR..CHA (any case).
    Returns (modifier, formula note).
    """
    sk = skill_name.strip()
    ab = SKILL_ABILITY_MAP.get(sk)
    if not ab:
        raise ValueError(f"Unknown skill {skill_name!r}; use a PHB skill name (e.g. 'Stealth').")
    key = ab.upper()
    score = int(ability_scores.get(key) or ability_scores.get(ab) or 10)
    mod = ability_modifier(score)
    pb = proficiency_bonus(character_level)
    prof_part = 0
    if proficiency:
        prof_part = pb * (2 if expertise else 1)
    total = mod + prof_part + int(extra_bonus)
    note = f"{sk} = {ab} ({score}) {mod:+d}"
    if proficiency:
        note += f" + prof {prof_part:+d} (pb {pb}, expertise={expertise})"
    if extra_bonus:
        note += f" + misc {extra_bonus:+d}"
    note += f" => **{total:+d}**"
    return total, note


@dataclass
class Status:
    name: str; category: str = "condition"; duration: int = -1
    source: str = ""; round_applied: int = 0; compound_clears: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    def tick(self):
        if self.duration > 0: self.duration -= 1
        return self.duration == 0

@dataclass
class Ability:
    name: str; action_type: str = "action"; cost_type: str = "none"
    cost_amount: int = 0; slot_level: int = 0; max_charges: int = 0; charges: int = 0
    cooldown: int = 0; cooldown_remaining: int = 0; last_used_round: int = -1
    is_reaction: bool = False; requires_two_weapons: bool = False; requires_melee: bool = False
    damage: str = ""; damage_type: str = ""; save_stat: str = ""; save_dc: int = 0
    description: str = ""; active: bool = True
    tags: List[str] = field(default_factory=list); extra: Dict[str, Any] = field(default_factory=dict)
    def is_available(self):
        if not self.active: return False
        if self.max_charges > 0 and self.charges <= 0: return False
        if self.cooldown_remaining > 0: return False
        return True
    def use(self, rnd):
        if self.max_charges > 0: self.charges -= 1
        if self.cooldown > 0: self.cooldown_remaining = self.cooldown; self.last_used_round = rnd
    def tick_cooldown(self):
        if self.cooldown_remaining > 0: self.cooldown_remaining -= 1

@dataclass
class Combatant:
    name: str; max_hp: int; hp: int = 0; temp_hp: int = 0; ac: int = 10; base_ac: int = 10
    stats: Dict[str, int] = field(default_factory=lambda: {"str":0,"dex":0,"con":0,"int":0,"wis":0,"cha":0})
    proficiency: int = 0; attack_bonus: int = 0; flat_attack_bonus: int = 0
    spell_attack: int = 0; spell_save_dc: int = 0; crit_range: int = 20
    speed: int = 30; base_speed: int = 30; initiative_mod: int = 0
    spell_slots: Dict[int, List[int]] = field(default_factory=dict)
    ki: int = 0; ki_max: int = 0
    abilities: Dict[str, Ability] = field(default_factory=dict)
    statuses: List[Status] = field(default_factory=list)
    resistances: Dict[str, Dict[str, float]] = field(default_factory=dict)
    has_progressive_resistance: bool = False
    regen_percent: float = 0.0; heal_or_purge: bool = False; heal_used: bool = False
    reaction_used: bool = False; reaction_name: str = ""
    action_used: bool = False; bonus_action_used: bool = False; extra_action_used: bool = False
    movement_remaining: int = 0  # set to speed at start of turn
    has_cunning_action: bool = False  # rogue: Disengage/Dash as bonus action
    has_extra_action: bool = False  # Stride: one weapon attack extra
    slow_per_stack: int = 10
    encounter_scaling: Dict[str, float] = field(default_factory=dict); encounters: int = 0
    flying: bool = False; flight_speed: int = 0
    conscious: bool = True; alive: bool = True
    buffs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Thrown weapon system (Giant's Throw)
    thrown_damage_mult: float = 1.0   # 1.5 with Giant's Throw
    thrown_range_mult: int = 1        # 3 with Giant's Throw
    thrown_range_bonus: int = 0       # +60 with God Sight
    counter_throw_available: bool = False  # Giant's Throw grants this
    counter_throw_cooldown: int = 0        # 0 = available, >0 = on cooldown
    counter_throw_cooldown_max: int = 2    # 2 rounds between uses
    
    # Concentration tracking (Haste, etc.)
    concentrating_on: str = ""         # "" = nothing, "Haste" = tracking
    concentration_save_mod: int = 0    # CON mod for concentration saves
    
    # Frost Fang healing
    frost_fang_heal_pct: float = 0.0   # 0.50 = 50% of damage heals. 0 = no Frost Fang.
    
    # Weapon configuration tracking
    # "emberfrost" = combined double-blade. AC uses base_ac (no cross-guard). No Twin Fang. No Cage.
    #   Attacks/round: Action 1 + Haste 2 + Stride 1 = 4 (each does both blade dmg)
    #   Cyclone available. Horizon Arc available.
    # "separated" = two blades. AC uses base_ac + 4 (cross-guard). Twin Fang. Cage counters.
    #   Attacks/round: Twin Fang 2 + Haste 2 + Stride 1 = 5
    #   No Cyclone. No Horizon Arc.
    # "single" = one weapon. AC uses base_ac + 2.
    # "" = no weapon config tracking (default for non-Kenji combatants)
    weapon_config: str = ""
    weapon_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Example: {"emberfrost": {"ac": 18, "max_attacks": 4, "abilities": ["Cyclone","Horizon Arc"]},
    #           "separated": {"ac": 22, "max_attacks": 5, "abilities": ["Twin Fang","Enhanced Cage","Cross-Guard"]}}
    
    # Perception / Stealth
    perception_mod: int = 0       # WIS mod + proficiency (if proficient)
    perception_adv: bool = False  # God Sight grants advantage
    stealth_mod: int = 0          # DEX mod + proficiency (if proficient)
    stealth_adv: bool = False     # Glass Skin, cloak, etc.
    
    # Perks — loaded from data, checked by engine
    perks: List[Dict[str, Any]] = field(default_factory=list)
    disposition: str = "neutral"
    
    # Death Throes — triggered when HP hits 0
    # {"type": "detonation", "radius": 15, "damage": "4d8", "dtype": "fire", "save_stat": "dex", "save_dc": 15}
    # {"type": "spawn", "spawns": [{"name": "Mite", "count": 3, "data": {...}}]}
    # {"type": "signal", "description": "reinforcements in 1d4 rounds"}
    # {"type": "void_collapse", "radius": 15, "duration": 3, "description": "anti-magic zone"}
    # {"type": "resurrection_seed", "rounds": 3, "hp_pct": 0.50, "prevented_by": ["radiant", "fire"]}
    death_throes: Dict[str, Any] = field(default_factory=dict)
    
    # Legendary Actions — boss only. Actions taken between player turns.
    legendary_actions_max: int = 0       # 0 = none, 3 = standard boss
    legendary_actions_remaining: int = 0
    legendary_action_options: List[Dict[str, Any]] = field(default_factory=list)
    # [{"name": "Strike", "cost": 1, "description": "One melee attack"},
    #  {"name": "Move", "cost": 1, "description": "Move up to speed without provoking OA"},
    #  {"name": "Ability", "cost": 2, "description": "Use a specific ability"}]
    
    # Legendary Resistances — auto-pass failed saves
    legendary_resistances_max: int = 0
    legendary_resistances_remaining: int = 0
    
    # Lair Actions — environment attacks on initiative 20 (boss only)
    lair_actions: List[Dict[str, Any]] = field(default_factory=list)
    # [{"name": "Gravity Surge", "save_stat": "str", "save_dc": 16, "effect": "pulled 15ft toward gate"}]
    
    # Phase Transitions — boss transforms at HP thresholds
    # [{"trigger_hp_pct": 0.50, "new_ac": 19, "new_abilities": [...], "description": "Phase 2: Unleashed"}]
    phases: List[Dict[str, Any]] = field(default_factory=list)
    current_phase: int = 0
    
    # Army Squad — simplified mass combat unit
    is_squad: bool = False
    squad_size: int = 0          # number of individuals in this squad
    individual_hp: int = 0       # HP per individual (for AOE kill calc)
    
    # Theme — one word, all abilities orbit this
    theme: str = ""  # "dissolution", "gravity", "reflection", "void", etc.
    
    # Vulnerability / Immunity (flat, not progressive)
    # vulnerability: {"radiant": 2.0, "fire": 2.0}  = takes double
    # immunity: {"poison": True, "charm": True}  = takes zero / auto-pass
    vulnerabilities: Dict[str, float] = field(default_factory=dict)  # dtype: multiplier (2.0 = double)
    immunities: List[str] = field(default_factory=list)  # ["poison", "charm", "fear", "necrotic"]
    
    # Position tracking (simple)
    position: int = 0           # linear position in feet from reference point (0)
    elevation: int = 0          # feet above ground. 0 = ground. Negative = below.
    
    # Morale
    morale_threshold: float = 0.0   # 0 = fights to death. 0.25 = flees at 25% HP
    has_fled: bool = False
    
    tags: List[str] = field(default_factory=list); notes: str = ""
    
    def set_weapon_config(self, config: str):
        """Switch weapon configuration. Updates AC and available attacks."""
        if config in self.weapon_configs:
            self.weapon_config = config
            cfg = self.weapon_configs[config]
            self.ac = cfg.get("ac", self.base_ac)
        elif config == "":
            self.weapon_config = ""
            self.ac = self.base_ac
    
    def get_max_attacks(self) -> int:
        """Get max attacks this round based on config + buffs."""
        if self.weapon_config and self.weapon_config in self.weapon_configs:
            return self.weapon_configs[self.weapon_config].get("max_attacks", 1)
        return 1
    
    def config_allows(self, ability_name: str) -> bool:
        """Check if current weapon config allows a specific ability."""
        if not self.weapon_config or self.weapon_config not in self.weapon_configs:
            return True  # no config tracking = everything allowed
        cfg = self.weapon_configs[self.weapon_config]
        allowed = cfg.get("abilities", [])
        blocked = cfg.get("blocked", [])
        if blocked and ability_name in blocked: return False
        if allowed and ability_name not in allowed: return True  # abilities list is extras, not restrictions
        return True

    def slow_stacks(self): return sum(1 for s in self.statuses if s.category == "slow")
    def effective_speed(self): return max(0, self.base_speed - self.slow_stacks() * self.slow_per_stack)
    def has_status(self, name): return any(s.name == name for s in self.statuses)
    
    def add_status(self, status):
        self.statuses.append(status)
        if status.name == "unconscious": self.conscious = False

    def remove_status(self, name, one_only=True):
        for i, s in enumerate(self.statuses):
            if s.name == name:
                removed = self.statuses.pop(i)
                if removed.compound_clears: self.remove_status(removed.compound_clears, True)
                if name == "unconscious": self.conscious = True
                return removed
        return None

    def purge_one(self):
        for n in ["bittershade","somnus","unconscious","stunned","charmed","frozen_limb","blinded","poisoned","slow_stack","prone"]:
            if self.has_status(n): return self.remove_status(n)
        return None

    def take_damage(self, amount, dtype="physical"):
        if self.has_progressive_resistance and dtype in self.resistances:
            self.resistances[dtype]["exposures"] += 1
        absorbed = min(self.temp_hp, amount); self.temp_hp -= absorbed
        self.hp = max(0, self.hp - (amount - absorbed))
        
        # Check phase transitions
        if self.phases and self.hp > 0:
            for i, phase in enumerate(self.phases):
                already_triggered = i < self.current_phase
                if already_triggered: continue
                threshold = int(self.max_hp * phase.get("trigger_hp_pct", 0))
                if self.hp <= threshold and i >= self.current_phase:
                    self.current_phase = i + 1  # move to next phase (1-indexed for "phases triggered")
                    if "new_ac" in phase: self.ac = phase["new_ac"]
                    if "new_speed" in phase: self.speed = phase["new_speed"]; self.base_speed = phase["new_speed"]
                    self._phase_triggered = phase
                    break
        
        # Check death
        if self.hp <= 0:
            self.alive = False; self.conscious = False
            self._death_throes_triggered = bool(self.death_throes)
        
        return amount

    def use_legendary_action(self, cost: int = 1) -> bool:
        if self.legendary_actions_remaining >= cost:
            self.legendary_actions_remaining -= cost; return True
        return False
    
    def use_legendary_resistance(self) -> bool:
        if self.legendary_resistances_remaining > 0:
            self.legendary_resistances_remaining -= 1; return True
        return False
    
    def reset_legendary_actions(self):
        """Called at start of this creature's turn."""
        self.legendary_actions_remaining = self.legendary_actions_max
    
    def squad_take_aoe(self, damage_per_individual: int) -> int:
        """For army squads: AOE kills individuals based on damage vs individual HP. Returns kills."""
        if not self.is_squad: return 0
        kills = min(self.squad_size, damage_per_individual // max(1, self.individual_hp))
        self.squad_size -= kills
        self.hp = self.squad_size * self.individual_hp
        if self.squad_size <= 0: self.alive = False; self.conscious = False
        return kills

    def heal_hp(self, amount): self.hp = min(self.max_hp, self.hp + amount)
    def add_temp_hp(self, amount): self.temp_hp = max(self.temp_hp, amount)
    
    def get_resist_mult(self, dtype):
        if not self.has_progressive_resistance or dtype not in self.resistances: return 1.0
        r = self.resistances[dtype]; return max(0.0, 1.0 - r["exposures"] * r["rate"])

    def apply_resist(self, damage, dtype): return max(0, int(damage * self.get_resist_mult(dtype)))
    
    def apply_vulnerability(self, damage, dtype):
        """Apply vulnerability multiplier. Stacks AFTER resistance."""
        if dtype in self.vulnerabilities:
            return int(damage * self.vulnerabilities[dtype])
        return damage
    
    def is_immune(self, dtype_or_condition):
        """Check immunity to damage type or condition."""
        return dtype_or_condition in self.immunities
    
    def apply_all_modifiers(self, damage, dtype):
        """Apply resistance → then vulnerability. Returns final damage."""
        if self.is_immune(dtype): return 0
        d = self.apply_resist(damage, dtype)
        d = self.apply_vulnerability(d, dtype)
        return d
    
    def check_morale(self) -> bool:
        """Returns True if creature wants to flee. Checks HP vs threshold."""
        if self.morale_threshold <= 0: return False
        return self.hp <= (self.max_hp * self.morale_threshold) and not self.has_fled
    def spend_slot(self, level):
        if level in self.spell_slots and self.spell_slots[level][0] > 0:
            self.spell_slots[level][0] -= 1; return True
        return False
    def spend_ki(self, amount):
        if self.ki >= amount: self.ki -= amount; return True
        return False

    def start_turn(self, rnd):
        self.heal_used = False; self.reaction_used = False; self.reaction_name = ""
        self.action_used = False; self.bonus_action_used = False; self.extra_action_used = False
        self.movement_remaining = self.effective_speed()
        for a in self.abilities.values(): a.tick_cooldown()
        if self.counter_throw_cooldown > 0: self.counter_throw_cooldown -= 1
        self.tick_buffs()
        self.reset_legendary_actions()
        # Reset per-turn flags
        if not hasattr(self, '_phase_triggered'): self._phase_triggered = {}
        if not hasattr(self, '_death_throes_triggered'): self._death_throes_triggered = False
        self._phase_triggered = {}
        expired = [s for s in self.statuses if s.tick()]
        for s in expired:
            self.statuses.remove(s)
            if s.name == "unconscious": self.conscious = True
    
    def use_action(self, desc=""):
        if self.action_used: return False, "ACTION ALREADY USED"
        self.action_used = True; return True, desc
    
    def use_bonus_action(self, desc=""):
        if self.bonus_action_used: return False, "BONUS ACTION ALREADY USED"
        self.bonus_action_used = True; return True, desc
    
    def use_extra_action(self, desc=""):
        if not self.has_extra_action: return False, "NO EXTRA ACTION AVAILABLE"
        if self.extra_action_used: return False, "EXTRA ACTION ALREADY USED"
        self.extra_action_used = True; return True, desc
    
    def can_disengage_bonus(self):
        return self.has_cunning_action and not self.bonus_action_used
    
    def action_economy_line(self):
        parts = []
        parts.append(f"Action:{'USED' if self.action_used else 'OPEN'}")
        parts.append(f"Bonus:{'USED' if self.bonus_action_used else 'OPEN'}")
        if self.has_extra_action: parts.append(f"Extra:{'USED' if self.extra_action_used else 'OPEN'}")
        parts.append(f"Reaction:{'USED('+self.reaction_name+')' if self.reaction_used else 'OPEN'}")
        parts.append(f"Move:{self.movement_remaining}ft")
        return " | ".join(parts)

    def use_reaction(self, name): self.reaction_used = True; self.reaction_name = name
    def available_abilities(self): return {n: a for n, a in self.abilities.items() if a.is_available()}

    def add_buff(self, name, duration=-1, effects=""):
        self.buffs[name] = {"duration": duration, "effects": effects}
    
    def remove_buff(self, name):
        return self.buffs.pop(name, None)
    
    def tick_buffs(self):
        expired = []
        for name, b in self.buffs.items():
            dur_key = "duration_hrs" if "duration_hrs" in b else "duration"
            if dur_key in b and b[dur_key] > 0:
                b[dur_key] -= 1
                if b[dur_key] == 0: expired.append(name)
        for name in expired: del self.buffs[name]
        return expired

    def status_line(self):
        p = [f"{self.name}:", f"HP {self.hp}/{self.max_hp}" + (f"+{self.temp_hp}t" if self.temp_hp else ""),
             f"AC {self.ac}", f"Spd {self.effective_speed()}"]
        # Weapon config
        if self.weapon_config:
            max_atk = self.get_max_attacks()
            p.append(f"[{self.weapon_config.upper()} {max_atk}atk]")
        if self.ki_max: p.append(f"Ki {self.ki}/{self.ki_max}")
        if self.spell_slots: p.append(" ".join(f"L{k}:{v[0]}/{v[1]}" for k,v in sorted(self.spell_slots.items())))
        ch = [f"{n}:{a.charges}/{a.max_charges}" for n,a in self.abilities.items() if a.max_charges > 0]
        cd = [f"{n}:CD{a.cooldown_remaining}" for n,a in self.abilities.items() if a.cooldown_remaining > 0]
        if ch: p.append(" ".join(ch))
        if cd: p.append(" ".join(cd))
        # Active buffs
        if self.buffs:
            bf = [f"{n}({b.get('duration_hrs', b.get('duration', '?'))}hr)" if b.get('duration_hrs', b.get('duration', -1)) > 0 else n for n, b in self.buffs.items()]
            p.append(f"BUFFS[{', '.join(bf)}]")
        # Concentration
        if self.concentrating_on:
            p.append(f"CONC:{self.concentrating_on}")
        # Thrown weapon
        if self.thrown_damage_mult > 1.0:
            ct_str = f"CT:{'READY' if self.counter_throw_cooldown == 0 and self.counter_throw_available else f'CD{self.counter_throw_cooldown}'}"
            base_range = 30  # Cyclone base
            total_range = (base_range + self.thrown_range_bonus) * self.thrown_range_mult
            p.append(f"Thrown:x{self.thrown_damage_mult} {total_range}ft {ct_str}")
        # Frost Fang healing
        if self.frost_fang_heal_pct > 0:
            p.append(f"FrostHeal:{int(self.frost_fang_heal_pct*100)}%")
        # Statuses
        st = [s.name for s in self.statuses if s.category != "slow"]
        sl = self.slow_stacks()
        if sl: st.append(f"slow x{sl}")
        if st: p.append(f"[{', '.join(st)}]")
        if self.has_progressive_resistance:
            rs = [f"{d}:{int(r['exposures']*r['rate']*100)}%" for d,r in self.resistances.items() if r["exposures"]>0]
            if rs: p.append(f"Resist({', '.join(rs)})")
        # Flat vulnerabilities
        if self.vulnerabilities:
            vs = [f"{d}x{v}" for d,v in self.vulnerabilities.items()]
            p.append(f"VULN({', '.join(vs)})")
        # Immunities (compact)
        if self.immunities:
            p.append(f"IMMUNE({','.join(self.immunities[:4])}{'...' if len(self.immunities)>4 else ''})")
        # Legendary
        if self.legendary_actions_max > 0:
            p.append(f"LA:{self.legendary_actions_remaining}/{self.legendary_actions_max}")
        if self.legendary_resistances_max > 0:
            p.append(f"LR:{self.legendary_resistances_remaining}/{self.legendary_resistances_max}")
        # Phase
        if self.phases:
            p.append(f"Phase:{self.current_phase}/{len(self.phases)}")
        # Theme
        if self.theme:
            p.append(f"[{self.theme}]")
        # Squad
        if self.is_squad:
            p.append(f"Squad:{self.squad_size}")
        # Perks (compact)
        if self.perks:
            pnames = [pk.get("name","?") for pk in self.perks if pk.get("effect") not in ("aura","custom")]
            if pnames:
                p.append(f"PERKS[{', '.join(pnames[:3])}{'...' if len(pnames)>3 else ''}]")
        # Morale
        if self.morale_threshold > 0 and self.check_morale():
            p.append("⚠️FLEEING")
        return " | ".join(p)

def load_ability(data):
    return Ability(name=data.get("name","?"), action_type=data.get("action_type","action"),
        cost_type=data.get("cost_type","none"), cost_amount=data.get("cost_amount",0),
        slot_level=data.get("slot_level",0), max_charges=data.get("max_charges",0),
        charges=data.get("charges", data.get("max_charges",0)),
        cooldown=data.get("cooldown",0), cooldown_remaining=data.get("cooldown_remaining",0),
        is_reaction=data.get("is_reaction",False), requires_two_weapons=data.get("requires_two_weapons",False),
        requires_melee=data.get("requires_melee",False), damage=data.get("damage",""),
        damage_type=data.get("damage_type",""), save_stat=data.get("save_stat",""),
        save_dc=data.get("save_dc",0), description=data.get("description",""),
        active=data.get("active",True), tags=data.get("tags",[]), extra=data.get("extra",{}))

def load_combatant(data):
    c = Combatant(name=data.get("name","?"), max_hp=data.get("max_hp",10),
        hp=data.get("hp", data.get("max_hp",10)), temp_hp=data.get("temp_hp",0),
        ac=data.get("ac",10), base_ac=data.get("base_ac", data.get("ac",10)),
        stats=data.get("stats",{"str":0,"dex":0,"con":0,"int":0,"wis":0,"cha":0}),
        proficiency=data.get("proficiency",2), attack_bonus=data.get("attack_bonus",0),
        flat_attack_bonus=data.get("flat_attack_bonus",0), spell_attack=data.get("spell_attack",0),
        spell_save_dc=data.get("spell_save_dc",0), crit_range=data.get("crit_range",20),
        speed=data.get("speed",30), base_speed=data.get("base_speed",data.get("speed",30)),
        initiative_mod=data.get("initiative_mod",0),
        spell_slots={int(k):v for k,v in data.get("spell_slots",{}).items()},
        ki=data.get("ki",0), ki_max=data.get("ki_max",0),
        has_progressive_resistance=data.get("has_progressive_resistance",False),
        regen_percent=data.get("regen_percent",0.0), heal_or_purge=data.get("heal_or_purge",False),
        slow_per_stack=data.get("slow_per_stack",10),
        encounter_scaling=data.get("encounter_scaling",{}), encounters=data.get("encounters",0),
        flying=data.get("flying",False), flight_speed=data.get("flight_speed",0),
        has_cunning_action=data.get("has_cunning_action",False),
        has_extra_action=data.get("has_extra_action",False),
        thrown_damage_mult=data.get("thrown_damage_mult",1.0),
        thrown_range_mult=data.get("thrown_range_mult",1),
        thrown_range_bonus=data.get("thrown_range_bonus",0),
        counter_throw_available=data.get("counter_throw_available",False),
        counter_throw_cooldown=data.get("counter_throw_cooldown",0),
        counter_throw_cooldown_max=data.get("counter_throw_cooldown_max",2),
        concentrating_on=data.get("concentrating_on",""),
        concentration_save_mod=data.get("concentration_save_mod",0),
        frost_fang_heal_pct=data.get("frost_fang_heal_pct",0.0),
        weapon_config=data.get("weapon_config",""),
        weapon_configs=data.get("weapon_configs",{}),
        perception_mod=data.get("perception_mod",0),
        perception_adv=data.get("perception_adv",False),
        stealth_mod=data.get("stealth_mod",0),
        stealth_adv=data.get("stealth_adv",False),
        perks=data.get("perks",[]),
        disposition=data.get("disposition","neutral"),
        death_throes=data.get("death_throes",{}),
        legendary_actions_max=data.get("legendary_actions",0),
        legendary_actions_remaining=data.get("legendary_actions",0),
        legendary_action_options=data.get("legendary_action_options",[]),
        legendary_resistances_max=data.get("legendary_resistances",0),
        legendary_resistances_remaining=data.get("legendary_resistances",0),
        lair_actions=data.get("lair_actions",[]),
        phases=data.get("phases",[]),
        is_squad=data.get("is_squad",False),
        squad_size=data.get("squad_size",0),
        individual_hp=data.get("individual_hp",0),
        theme=data.get("theme",""),
        vulnerabilities=data.get("vulnerabilities",{}),
        immunities=data.get("immunities",[]),
        position=data.get("position",0),
        elevation=data.get("elevation",0),
        morale_threshold=data.get("morale_threshold",0.0),
        tags=data.get("tags",[]), notes=data.get("notes",""))
    # Apply initial weapon config AC
    if c.weapon_config and c.weapon_config in c.weapon_configs:
        c.ac = c.weapon_configs[c.weapon_config].get("ac", c.base_ac)
    for dtype, rdata in data.get("resistances",{}).items():
        if isinstance(rdata, dict): c.resistances[dtype] = {"exposures":rdata.get("exposures",0),"rate":rdata.get("rate",0.1)}
        else: c.resistances[dtype] = {"exposures":0,"rate":float(rdata)}
    for adata in data.get("abilities",[]):
        ab = load_ability(adata); c.abilities[ab.name] = ab
    for bname, bdata in data.get("buffs", {}).items():
        if isinstance(bdata, dict): c.buffs[bname] = bdata
        else: c.buffs[bname] = {"duration": -1, "effects": str(bdata)}
    return c


def load_perks_from_persistent_effects(persistent_effects: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert character_world_state persistent_effects → Combatant.perks format.

    Maps persistent_effects entries (type: perk, ember_enhancement, ember_combat_passive, etc.)
    into the perk dicts that Combat.check_perks() understands:
      {"name": str, "condition": str, "effect": str, "value": float, "source_type": str}

    Also converts monster special abilities and NPC buffs (Nyx Elixirs, Ankuspawn embers)
    when stored as persistent_effects.
    """
    perks = []
    on_pc = persistent_effects.get("on_pc", [])
    on_pc_from_npcs = persistent_effects.get("on_pc_from_npcs", [])

    for entry in on_pc + on_pc_from_npcs:
        etype = entry.get("type", "")
        ename = entry.get("effect_name", "")
        mech = entry.get("mechanical_effect", "")

        # Ember Enhancement — healing/buff 10x multiplier
        if etype == "ember_enhancement" and "10x" in mech.lower():
            # Healing multiplier
            if "healing" in mech.lower():
                perks.append({
                    "name": ename, "condition": "ember_active",
                    "effect": "heal_mult", "value": 10.0,
                    "source_type": etype,
                })
            # Buff multiplier (Protector's Surge, Chorus of One, etc.)
            if "buff" in mech.lower():
                perks.append({
                    "name": ename, "condition": "ember_active",
                    "effect": "buff_mult", "value": 10.0,
                    "source_type": etype,
                })

        # Ember combat passive — Pretty Privilege attack bonus, magnetism, etc.
        elif etype == "ember_combat_passive":
            # Combat Magnetism: enemies target Cookie (narrative, not a modifier — skip)
            pass

        # Perk — gold multiplier, etc. (narrative perks, not combat modifiers)
        elif etype == "perk":
            # Pretty Privilege gold is narrative; skip for combat perks
            pass

        # Aura — Heartstring, enemy auras, etc.
        elif etype == "aura":
            perks.append({
                "name": ename, "condition": "always",
                "effect": "aura", "value": 0,
                "aura_data": {
                    "range_ft": 30,
                    "save_stat": "wis", "save_dc": 12,
                    "description": mech,
                },
                "source_type": etype,
            })

        # Generic status-granting effects (Nyx Elixirs, monster abilities)
        elif etype in ("nyx_elixir", "monster_ability", "ankuspawn_ember"):
            perks.append({
                "name": ename, "condition": "always",
                "effect": "custom", "value": 0,
                "mechanical_effect": mech,
                "source_type": etype,
            })

    return perks


def load_monster_perks(abilities_data: List[Dict], tags: List[str] = None) -> List[Dict[str, Any]]:
    """Convert monster special abilities into perks format.

    Phase Spiders get 'ethereal_jaunt' perk. Nyx-enhanced monsters get elixir perks.
    Called during monster combatant creation.
    """
    perks = []
    tags = tags or []

    for ab in abilities_data:
        aname = ab.get("name", "").lower()
        # Ethereal Jaunt — tracked as a perk so the engine knows this combatant CAN go ethereal
        if "ethereal" in aname and "jaunt" in aname:
            perks.append({
                "name": "Ethereal Jaunt", "condition": "always",
                "effect": "can_ethereal", "value": 1,
                "source_type": "monster_ability",
            })

    # Nyx-enhanced tag
    if "nyx_enhanced" in tags:
        perks.append({
            "name": "Nyx Elixir", "condition": "always",
            "effect": "attack_bonus", "value": 2,
            "source_type": "nyx_elixir",
        })

    return perks


class Combat:
    def __init__(self):
        self.fighters: Dict[str, Combatant] = {}; self.order = []; self.round = 0
        self.turn_idx = -1; self.log = []; self.active = False
        self.zones: List[Dict[str, Any]] = []  # terrain zones, hazards, anti-magic areas

    def add(self, c, initiative): self.fighters[c.name] = c; self.order.append((initiative, c.name)); self.order.sort(key=lambda x:-x[0])
    def start(self): self.round = 1; self.turn_idx = -1; self.active = True; self._log(f"Combat start: {', '.join(f'{n}({i})' for i,n in self.order)}")
    def get(self, name): return self.fighters[name]

    def ambush_check(self, detector: str, sneaker: str) -> dict:
        """Roll Perception vs Stealth. Accounts for advantage on either side.
        Returns {'detected': bool, 'perception_roll': int, 'stealth_roll': int, 'surprise': bool}
        If surprise: sneaker gets auto-crit on first attack, detector loses first turn."""
        d = self.fighters[detector]
        s = self.fighters[sneaker]
        
        # Perception roll (advantage if God Sight etc.)
        r1, r2 = d20(), d20()
        p_nat = max(r1, r2) if d.perception_adv else min(r1, r2) if False else r1
        if d.perception_adv:
            p_nat = max(r1, r2)
            self._log(f"  {detector} Perception (ADV): {r1}, {r2} → {p_nat}+{d.perception_mod}={p_nat+d.perception_mod}")
        else:
            p_nat = r1
            self._log(f"  {detector} Perception: {p_nat}+{d.perception_mod}={p_nat+d.perception_mod}")
        p_total = p_nat + d.perception_mod
        
        # Stealth roll (advantage if Glass Skin etc.)
        r1, r2 = d20(), d20()
        if s.stealth_adv:
            s_nat = max(r1, r2)
            self._log(f"  {sneaker} Stealth (ADV): {r1}, {r2} → {s_nat}+{s.stealth_mod}={s_nat+s.stealth_mod}")
        else:
            s_nat = r1
            self._log(f"  {sneaker} Stealth: {s_nat}+{s.stealth_mod}={s_nat+s.stealth_mod}")
        s_total = s_nat + s.stealth_mod
        
        detected = p_total >= s_total
        surprise = not detected
        
        if detected:
            self._log(f"  ✓ {detector} SPOTS {sneaker}! No surprise. ({p_total} vs {s_total})")
        else:
            self._log(f"  ✗ {sneaker} HIDDEN! Surprise round. Auto-crit on first attack. ({s_total} vs {p_total})")
        
        return {
            "detected": detected,
            "surprise": surprise,
            "perception_roll": p_total,
            "stealth_roll": s_total,
        }
    
    def check_weapon_config(self, name: str, action: str) -> Tuple[bool, str]:
        """Validate an action against current weapon config. Returns (allowed, reason)."""
        c = self.fighters[name]
        if not c.weapon_config: return True, ""
        cfg = c.weapon_configs.get(c.weapon_config, {})
        blocked = cfg.get("blocked", [])
        if action in blocked:
            self._log(f"  ⚠️ {action} BLOCKED — {c.weapon_config} config does not allow {action}")
            return False, f"{action} not available in {c.weapon_config} config"
        return True, ""

    DISPOSITION_RANK = {"hostile":0,"reluctant":1,"neutral":2,"friendly":3,"close":4,"intimate":5}

    def check_perks(self, name: str, target: str = "") -> dict:
        """Check which perks are active for a fighter. Returns active bonuses.

        Returned dict keys:
          attack_bonus  — flat bonus to attack rolls
          heal_mult     — multiplier for healing received/given (Ember Enhancement 10x)
          buff_mult     — multiplier for buff spell potency (Ember Enhancement 10x)
          crit_range_mod — lowers crit threshold (e.g. 1 → crits on 19-20)
          can_ethereal  — True if combatant has Ethereal Jaunt or similar
          active_perks  — list of perk names that are currently active
        """
        c = self.fighters[name]
        t = self.fighters.get(target)
        result = {
            "attack_bonus": 0, "heal_mult": 1.0, "buff_mult": 1.0,
            "crit_range_mod": 0, "can_ethereal": False, "active_perks": [],
        }

        # Find allies (other fighters on same side — disposition friendly+)
        allies = [f for fname, f in self.fighters.items()
                  if fname != name and f.alive and self.DISPOSITION_RANK.get(f.disposition, 0) >= 3]
        any_observers = [f for fname, f in self.fighters.items()
                        if fname != name and f.alive and self.DISPOSITION_RANK.get(f.disposition, 0) >= 0]

        # Check ember suppression (nullification fields, Ember Shade wards)
        ember_suppressed = c.has_status("ember_suppressed") or c.has_status("ember_nullified")

        for perk in c.perks:
            cond = perk.get("condition", "always")
            active = False

            if cond == "always": active = True
            elif cond == "ember_active": active = not ember_suppressed
            elif cond == "friendly_observer": active = len(allies) > 0
            elif cond == "any_observer": active = len(any_observers) > 0
            elif cond == "target_charmed": active = t and t.has_status("charmed")

            if active:
                effect = perk.get("effect", "")
                val = perk.get("value", 0)
                result["active_perks"].append(perk["name"])

                if effect == "attack_bonus": result["attack_bonus"] += val
                elif effect == "heal_mult": result["heal_mult"] *= val
                elif effect == "buff_mult": result["buff_mult"] *= val
                elif effect == "crit_range_mod": result["crit_range_mod"] += val
                elif effect == "can_ethereal": result["can_ethereal"] = True

        return result
    
    def next_turn(self):
        # Skip dead combatants
        attempts = 0
        while attempts < len(self.order) * 2:
            self.turn_idx += 1
            if self.turn_idx >= len(self.order):
                self.turn_idx = 0; self.round += 1
                self.tick_zones()  # Zones tick at start of each new round
            name = self.order[self.turn_idx][1]
            if self.fighters[name].alive: break
            attempts += 1
        self.fighters[name].start_turn(self.round)
        self._log(f"--- R{self.round} {name}'s turn ---"); return self.round, name

    def can_be_targeted(self, tgt: str, atk: str = "", ranged: bool = False) -> Tuple[bool, str]:
        """Check if target can be attacked. Enforces ethereal, invisible, etc.
        Returns (targetable, reason). If not targetable, attack should auto-fail."""
        t = self.fighters[tgt]
        # Ethereal — on a different plane, cannot be targeted by material attacks
        if t.has_status("ethereal"):
            return False, f"{tgt} is ETHEREAL — on the Ethereal Plane, untargetable"
        # Dead
        if not t.alive:
            return False, f"{tgt} is DEAD"
        return True, ""

    def _status_adv_dis(self, atk: str, tgt: str, ranged: bool = False, range_ft: int = 5) -> Tuple[bool, bool, List[str]]:
        """Compute advantage/disadvantage from status effects on attacker and target.
        Returns (adv, dis, reasons[]) to be combined with caller-supplied adv/dis."""
        a, t = self.fighters[atk], self.fighters[tgt]
        adv_reasons = []; dis_reasons = []
        dist = self.distance_between(atk, tgt) if a.position != t.position else 5

        # --- ATTACKER statuses ---
        if a.has_status("blinded"):
            dis_reasons.append("attacker blinded")
        if a.has_status("frightened"):
            dis_reasons.append("attacker frightened")
        if a.has_status("restrained"):
            dis_reasons.append("attacker restrained")
        if a.has_status("poisoned"):
            dis_reasons.append("attacker poisoned")
        if a.has_status("invisible"):
            adv_reasons.append("attacker invisible")

        # --- TARGET statuses ---
        if t.has_status("blinded"):
            adv_reasons.append("target blinded")
        if t.has_status("restrained"):
            adv_reasons.append("target restrained")
        if t.has_status("prone"):
            if ranged or dist > 5:
                dis_reasons.append("target prone (ranged)")
            else:
                adv_reasons.append("target prone (melee)")
        if t.has_status("invisible"):
            dis_reasons.append("target invisible")
        if t.has_status("stunned"):
            adv_reasons.append("target stunned")
        if t.has_status("paralyzed"):
            adv_reasons.append("target paralyzed")
        if t.has_status("unconscious"):
            adv_reasons.append("target unconscious")

        has_adv = len(adv_reasons) > 0
        has_dis = len(dis_reasons) > 0
        reasons = adv_reasons + dis_reasons
        return has_adv, has_dis, reasons

    def attack(self, atk, tgt, bonus=0, adv=False, dis=False, auto_crit=False, ranged=False, range_ft=5):
        a, t = self.fighters[atk], self.fighters[tgt]

        # --- STATUS GATE: can target be attacked? ---
        targetable, reason = self.can_be_targeted(tgt, atk, ranged)
        if not targetable:
            self._log(f"{atk} → {tgt}: BLOCKED — {reason}")
            return {"nat":0,"total":0,"bonus":0,"crit":False,"nat1":False,"hits":False,
                    "tgt_ac":t.ac,"perks":{},"blocked":True,"block_reason":reason}

        # Range check (warn, don't block — DM may override)
        dist = self.distance_between(atk, tgt) if a.position != t.position else 5
        if ranged and dist > range_ft:
            self._log(f"  ⚠️ RANGE WARNING: {atk} is {dist}ft from {tgt}, weapon range {range_ft}ft")
        elif not ranged and dist > 5:
            self._log(f"  ⚠️ RANGE WARNING: {atk} is {dist}ft from {tgt} (melee = 5ft)")

        # --- STATUS ADV/DIS: prone, blinded, restrained, etc. ---
        status_adv, status_dis, status_reasons = self._status_adv_dis(atk, tgt, ranged, range_ft)
        final_adv = adv or status_adv
        final_dis = dis or status_dis
        # RAW: if both adv AND dis from any source, they cancel to flat
        if final_adv and final_dis:
            final_adv = False; final_dis = False

        perks = self.check_perks(atk, tgt)
        perk_atk = perks["attack_bonus"]
        perk_crit = perks["crit_range_mod"]
        tb = a.attack_bonus + a.flat_attack_bonus + bonus + perk_atk
        effective_crit = a.crit_range - perk_crit  # lower = crits on more numbers
        nat = max(d20(),d20()) if final_adv else (min(d20(),d20()) if final_dis else d20())
        total = nat + tb; ic = auto_crit or nat >= effective_crit
        # Auto-crit: stunned, unconscious, paralyzed (within 5ft)
        if t.has_status("stunned") or t.has_status("unconscious"): ic = True
        if t.has_status("paralyzed") and dist <= 5: ic = True
        hits = ic or (nat != 1 and total >= t.ac)
        tag = "CRIT!" if ic else ("HIT" if hits else "MISS")
        perk_note = f" [+{perk_atk}PoF]" if perk_atk > 0 else ""
        crit_note = f" [crit {effective_crit}-20]" if perk_crit > 0 else ""
        status_note = f" [{', '.join(status_reasons)}]" if status_reasons else ""
        adv_tag = " ADV" if final_adv else (" DIS" if final_dis else "")
        self._log(f"{atk} → {tgt}: nat {nat}+{tb}={total} vs AC {t.ac} → {tag}{adv_tag}{perk_note}{crit_note}{status_note}")
        return {"nat":nat,"total":total,"bonus":tb,"crit":ic,"nat1":nat==1,"hits":hits,
                "tgt_ac":t.ac,"perks":perks,"blocked":False,"status_reasons":status_reasons}

    def damage(self, tgt, dice, dtype, mod=0, crit=False, extra_dice="", flat=0):
        t = self.fighters[tgt]
        if t.is_immune(dtype):
            self._log(f"  DMG({dtype}): IMMUNE — 0 damage"); return 0, {"raw":0,"final":0,"dtype":dtype,"crit":crit,"resist_pct":100}
        total, rolls, bm = roll_dice(dice); total += mod
        if crit:
            cr, _, _ = roll_dice(dice); total += cr - bm
        if extra_dice:
            e, _, em = roll_dice(extra_dice)
            if crit: ce, _, _ = roll_dice(extra_dice); e += ce - em
            total += e
        total += flat; raw = total
        final = t.apply_all_modifiers(total, dtype)
        rp = int((1 - t.get_resist_mult(dtype)) * 100)
        vuln = t.vulnerabilities.get(dtype, 1.0)
        vuln_str = f", x{vuln} vuln" if vuln > 1.0 else ""
        self._log(f"  DMG({dtype}): {raw} → {final}" + (f" ({rp}% resist{vuln_str})" if rp or vuln > 1.0 else ""))
        return final, {"raw":raw,"final":final,"dtype":dtype,"crit":crit,"resist_pct":rp,"vuln":vuln}

    def deal_damage(self, tgt, amount, dtype="physical"):
        t = self.fighters[tgt]
        was_alive = t.alive
        t.take_damage(amount, dtype)
        self._log(f"  {tgt} takes {amount} → HP {t.hp}/{t.max_hp}" + (f"+{t.temp_hp}t" if t.temp_hp else ""))
        
        # Phase transition
        if hasattr(t, '_phase_triggered') and t._phase_triggered:
            phase = t._phase_triggered
            self._log(f"  ⚡ PHASE TRANSITION: {phase.get('description', 'Phase ' + str(t.current_phase))}")
            self._log(f"    New AC: {t.ac}")
        
        # Death throes — PROCESS effects, not just log
        death_throes_result = None
        if was_alive and not t.alive and t.death_throes:
            dt = t.death_throes
            death_throes_result = {"type": dt.get("type"), "source": tgt}
            self._log(f"  💀 DEATH THROES: {dt.get('type')} — {dt.get('description', '')}")
            
            if dt.get("type") == "detonation":
                radius = dt.get("radius", 15)
                dmg_dice = dt.get("damage", "3d8")
                det_dtype = dt.get("dtype", "force")
                save_dc = dt.get("save_dc", 15)
                save_stat = dt.get("save_stat", "dex")
                self._log(f"    💥 DETONATION: {radius}ft, {dmg_dice} {det_dtype}, {save_stat.upper()} DC {save_dc}")
                dmg_total, _, _ = roll_dice(dmg_dice)
                # Hit everyone in radius
                for fname, f in self.fighters.items():
                    if fname == tgt or not f.alive: continue
                    dist = abs(f.position - t.position)
                    if dist <= radius:
                        sv = self.save(fname, save_stat, save_dc)
                        actual = dmg_total // 2 if sv["success"] else dmg_total
                        f.take_damage(actual, det_dtype)
                        self._log(f"    {fname}: {actual} {det_dtype} ({'half' if sv['success'] else 'full'}) → HP {f.hp}/{f.max_hp}")
                death_throes_result["damage"] = dmg_total
                
            elif dt.get("type") == "void_collapse":
                radius = dt.get("radius", 15)
                duration = dt.get("duration", 3)
                self.add_zone("Void Collapse", t.position, radius, duration, effect="suppress_buffs")
                death_throes_result["zone"] = True
                
            elif dt.get("type") == "spawn":
                spawns = dt.get("spawns", [])
                spawn_data = []
                for sp in spawns:
                    for i in range(sp.get("count", 1)):
                        name = f"{sp['name']} {i+1}"
                        if "data" in sp:
                            data = {**sp["data"], "name": name, "position": t.position}
                            spawn_data.append(data)
                            self._log(f"    SPAWN: {name}")
                if spawn_data:
                    self.add_reinforcements(spawn_data, f"{tgt} death spawns")
                death_throes_result["spawned"] = len(spawn_data)
                
            elif dt.get("type") == "signal":
                self._log(f"    🚨 SIGNAL SENT: {dt.get('description', 'Reinforcements incoming')}")
                death_throes_result["signal"] = True
                
            elif dt.get("type") == "chain_death":
                chain_dmg_dice = dt.get("damage", "3d8")
                chain_dtype = dt.get("chain_dtype", "necrotic")
                chain_radius = dt.get("radius", 15)
                max_jumps = dt.get("jumps", 3)
                chain_dmg, _, _ = roll_dice(chain_dmg_dice)
                self._log(f"    ⚡ CHAIN DEATH: {chain_dmg} {chain_dtype}, up to {max_jumps} jumps")
                last_pos = t.position
                hit_names = {tgt}
                for jump in range(max_jumps):
                    nearest = None; nearest_dist = 999
                    for fname, f in self.fighters.items():
                        if fname in hit_names or not f.alive: continue
                        dist = abs(f.position - last_pos)
                        if dist <= chain_radius and dist < nearest_dist:
                            nearest = fname; nearest_dist = dist
                    if nearest:
                        nf = self.fighters[nearest]
                        nf.take_damage(chain_dmg, chain_dtype)
                        hit_names.add(nearest)
                        last_pos = nf.position
                        self._log(f"    Chain → {nearest}: {chain_dmg} {chain_dtype} → HP {nf.hp}/{nf.max_hp}")
                    else: break
                
            elif dt.get("type") == "resurrection_seed":
                rounds = dt.get("rounds", 3)
                prevented = dt.get("prevented_by", ["radiant", "fire"])
                self._log(f"    ☠️ RESURRECTION SEED: Reforms in {rounds}rd unless destroyed by {prevented}")
                death_throes_result["res_rounds"] = rounds
                death_throes_result["prevented_by"] = prevented
                
            elif dt.get("type") == "terrain_hazard":
                radius = dt.get("radius", 10)
                duration = dt.get("duration", 3)
                zone_name = dt.get("zone_name", f"{tgt} remains")
                self.add_zone(zone_name, t.position, radius, duration, 
                            damage=dt.get("damage","1d6"), dtype=dt.get("dtype","acid"), save_dc=dt.get("save_dc",13))
                
            elif dt.get("type") == "buff_allies":
                buff_name = dt.get("buff_name", "Death Rage")
                buff_dur = dt.get("buff_duration", 3)
                for fname, f in self.fighters.items():
                    if fname == tgt or not f.alive: continue
                    if f.disposition in ("hostile", "cold") or f.disposition == t.disposition:
                        continue  # only buff same-side
                    # Buff allies of the dead creature (enemies of the player)
                    # Simple: buff any non-player fighter
                    if fname not in ["Kenji"]:  # crude but works
                        f.add_buff(buff_name, duration=buff_dur, effects=dt.get("effects", "+2 atk, +10 temp HP"))
                        self._log(f"    {fname} gains [{buff_name}] for {buff_dur}rd")
        
        return {"alive": t.alive, "death_throes": death_throes_result}

    def thrown_attack(self, atk, tgt, dice, dtype, mod=0, crit=False, extra_dice="",
                      vuln_mult=1, bonus_flat=0):
        """Roll thrown weapon damage with Giant's Throw multiplier auto-applied."""
        a = self.fighters[atk]
        base_dmg, details = self.damage(tgt, dice, dtype, mod=mod, crit=crit, extra_dice=extra_dice, flat=bonus_flat)
        
        # Apply vulnerability multiplier (e.g. fire x2 vs abyssal)
        if vuln_mult > 1:
            base_dmg = int(base_dmg * vuln_mult)
        
        # Apply thrown multiplier (Giant's Throw)
        if a.thrown_damage_mult > 1.0:
            pre = base_dmg
            base_dmg = int(base_dmg * a.thrown_damage_mult)
            self._log(f"  Thrown x{a.thrown_damage_mult}: {pre} → {base_dmg}")
        
        return base_dmg, details

    def frost_fang_hit(self, atk, tgt, total_damage):
        """Apply Frost Fang healing after a hit. Auto-heals or adds temp HP. Adds slow stack. Checks perks.
        NOTE: total_damage should already have per-component vulnerability applied by the DM.
        Use emberfrost_damage() to calculate component damage properly."""
        a = self.fighters[atk]
        t = self.fighters[tgt]
        perks = self.check_perks(atk)
        
        # Check slow immunity
        slow_immune = t.is_immune("slow")
        
        # Apply damage (death throes handled by take_damage → deal_damage path if needed)
        was_alive = t.alive
        t.take_damage(total_damage, "emberfrost")
        self._log(f"  {tgt} takes {total_damage} → HP {t.hp}/{t.max_hp}" + (f"+{t.temp_hp}t" if t.temp_hp else ""))
        
        # Phase check
        if hasattr(t, '_phase_triggered') and t._phase_triggered:
            self._log(f"  ⚡ PHASE TRANSITION: {t._phase_triggered.get('description', '')}")
        
        # Death throes check
        if was_alive and not t.alive and t.death_throes:
            self._log(f"  💀 DEATH THROES: {t.death_throes.get('type')} — {t.death_throes.get('description','')}")
        
        # Slow stack (if not immune)
        if not slow_immune:
            t.add_status(Status(name="slow_stack", category="slow", source="Frost Fang", round_applied=self.round))
            self._log(f"  {tgt} slow +1 (total: {t.slow_stacks()}, speed: {t.effective_speed()})")
        else:
            self._log(f"  {tgt} immune to slow")
        
        # Frost Fang healing with perk multiplier (Attention Whore)
        heal = 0
        if a.frost_fang_heal_pct > 0:
            heal = int(total_damage * a.frost_fang_heal_pct * perks["heal_mult"])
            perk_note = f" [x{perks['heal_mult']} AW]" if perks["heal_mult"] > 1.0 else ""
            if a.hp < a.max_hp:
                actual_heal = min(heal, a.max_hp - a.hp)
                a.heal_hp(actual_heal)
                overflow = heal - actual_heal
                if overflow > 0:
                    a.add_temp_hp(min(overflow, a.max_hp))
                self._log(f"  FrostHeal: {heal}{perk_note} → HP {a.hp}/{a.max_hp}+{a.temp_hp}t")
            else:
                a.add_temp_hp(min(heal, a.max_hp))
                self._log(f"  FrostHeal: {heal}{perk_note} → overflow → {a.temp_hp}t")
        
        return {"damage": total_damage, "healing": heal, "slow_stacks": t.slow_stacks(), "alive": t.alive}
    
    def emberfrost_damage(self, tgt, crit=False, thrown_mult=1.0):
        """Calculate Emberfrost damage per component with per-type vulnerability.
        Returns (total, breakdown_dict). DM passes total to frost_fang_hit."""
        t = self.fighters[tgt]
        # Slash
        slash, _, _ = roll_dice("1d8+2")
        if crit: s2, _, _ = roll_dice("1d8"); slash += s2
        slash = t.apply_all_modifiers(slash, "slashing")
        # Fire
        fire, _, _ = roll_dice("1d6")
        if crit: f2, _, _ = roll_dice("1d6"); fire += f2
        fire = t.apply_all_modifiers(fire, "fire")
        # Cold
        cold, _, _ = roll_dice("1d8+5")
        if crit: c2, _, _ = roll_dice("1d8"); cold += c2
        cold = t.apply_all_modifiers(cold, "cold")
        # Necrotic (10% max HP)
        necrotic = int(t.max_hp * 0.10)
        necrotic = t.apply_all_modifiers(necrotic, "necrotic")
        
        base = slash + fire + cold + necrotic
        total = int(base * thrown_mult) if thrown_mult > 1.0 else base
        
        breakdown = {"slash": slash, "fire": fire, "cold": cold, "necrotic": necrotic,
                     "base": base, "total": total, "thrown_mult": thrown_mult, "crit": crit}
        self._log(f"  Emberfrost: s{slash}+f{fire}+c{cold}+n{necrotic}={base}" +
                  (f" x{thrown_mult}={total}" if thrown_mult > 1.0 else ""))
        return total, breakdown
    
    # ---- UTILITY METHODS ----
    
    def remove_all_buffs(self, name: str) -> List[str]:
        """Strip ALL buffs from a combatant (anti-magic pulse). Returns removed buff names."""
        c = self.fighters[name]
        removed = list(c.buffs.keys())
        c.buffs.clear()
        if c.concentrating_on:
            removed.append(f"CONC:{c.concentrating_on}")
            c.concentrating_on = ""
        if removed:
            self._log(f"  🚫 {name}: ALL BUFFS STRIPPED — {', '.join(removed)}")
        return removed
    
    def inflict(self, tgt: str, condition: str, duration: int = -1, source: str = ""):
        """Shorthand to inflict a common condition. Checks immunity first."""
        t = self.fighters[tgt]
        if t.is_immune(condition):
            self._log(f"  {tgt} IMMUNE to [{condition}]")
            return False
        cat = "condition"
        if condition in ("slow_stack",): cat = "slow"
        s = Status(name=condition, category=cat, duration=duration, round_applied=self.round, source=source)
        t.add_status(s)
        self._log(f"  {tgt} → [{condition}]{f' ({duration}rd)' if duration > 0 else ''}{f' from {source}' if source else ''}")
        # Side effects
        if condition == "stunned": t.action_used = True; t.bonus_action_used = True
        if condition == "unconscious": t.conscious = False
        if condition == "prone": pass  # melee adv, ranged disadv, costs half movement to stand
        if condition == "grappled": t.movement_remaining = 0
        return True

    def concentration_check(self, name, damage_taken):
        """Roll concentration save. DC = max(10, damage/2). Returns True if held."""
        c = self.fighters[name]
        if not c.concentrating_on:
            return True  # not concentrating, no check needed
        dc = max(10, damage_taken // 2)
        nat = d20()
        total = nat + c.concentration_save_mod
        success = total >= dc
        self._log(f"  CONCENTRATION ({c.concentrating_on}): nat {nat}+{c.concentration_save_mod}={total} vs DC {dc} → {'HOLDS' if success else 'BROKEN!'}")
        if not success:
            spell = c.concentrating_on
            c.concentrating_on = ""
            self._log(f"  ⚠️ {spell} DROPPED!")
        return success

    def counter_throw_check(self, atk, tgt, missed=True):
        """Check if counter throw is available and fire it if so. Returns result dict or None."""
        a = self.fighters[atk]
        if not missed: return None
        if not a.counter_throw_available: return None
        if a.counter_throw_cooldown > 0:
            self._log(f"  Counter Throw: on cooldown ({a.counter_throw_cooldown}rd remaining)")
            return None
        if a.reaction_used:
            self._log(f"  Counter Throw: reaction already used ({a.reaction_name})")
            return None
        
        self._log(f"  ⚡ COUNTER THROW FIRES!")
        a.use_reaction("Counter Throw")
        a.counter_throw_cooldown = a.counter_throw_cooldown_max
        
        result = self.attack(atk, tgt)
        return result

    def heal(self, name, amount, source: str = "", healer: str = ""):
        """Heal a combatant. Applies perk multipliers (e.g. Ember Enhancement 10x).

        Args:
            name: combatant being healed
            amount: base heal amount BEFORE perk multipliers
            source: label for the heal source (e.g. "Healing Dance")
            healer: name of the combatant casting the heal (for perk lookup).
                    If empty, checks the target's own perks (self-heal).
        Returns:
            dict with base, multiplier, final, and overflow info.
        """
        c = self.fighters[name]
        # Look up heal_mult from the HEALER's perks (the caster's Ember Enhancement)
        perk_owner = healer if healer and healer in self.fighters else name
        perks = self.check_perks(perk_owner)
        mult = perks.get("heal_mult", 1.0)
        final = int(amount * mult)
        actual = min(final, c.max_hp - c.hp)
        overflow = final - actual
        c.heal_hp(actual)
        src_tag = f" ({source})" if source else ""
        mult_tag = f" [x{mult} Ember]" if mult > 1.0 else ""
        overflow_tag = f" (overflow {overflow})" if overflow > 0 else ""
        self._log(f"  {name} heals {amount}→{final}{mult_tag}{src_tag} → HP {c.hp}/{c.max_hp}{overflow_tag}")
        return {"base": amount, "mult": mult, "final": final, "actual": actual, "overflow": overflow}

    def add_temp(self, name, amount, source: str = "", granter: str = ""):
        """Add temp HP. Applies buff_mult from granter's perks (Ember Enhancement 10x for Chorus of One, etc.)."""
        c = self.fighters[name]
        perk_owner = granter if granter and granter in self.fighters else name
        perks = self.check_perks(perk_owner)
        mult = perks.get("buff_mult", 1.0)
        final = int(amount * mult) if mult > 1.0 else amount
        c.add_temp_hp(final)
        mult_tag = f" [x{mult} Ember]" if mult > 1.0 else ""
        src_tag = f" ({source})" if source else ""
        self._log(f"  {name} +{final}t{mult_tag}{src_tag} → {c.temp_hp}t")

    def process_auras(self, name: str) -> List[Dict[str, Any]]:
        """Process start-of-turn aura effects from ALL combatants that affect 'name'.

        Called at start of a combatant's turn. Checks every fighter for aura perks
        and applies saves/effects to the active combatant if in range.
        Returns list of aura results for the DM script to narrate.
        """
        target = self.fighters[name]
        results = []
        for fname, f in self.fighters.items():
            if fname == name or not f.alive: continue
            for perk in f.perks:
                if perk.get("effect") != "aura": continue
                aura = perk.get("aura_data", {})
                arange = aura.get("range_ft", 30)
                dist = abs(target.position - f.position) if target.position != f.position else 5
                if dist > arange: continue

                # Aura affects this combatant
                save_stat = aura.get("save_stat", "")
                save_dc = aura.get("save_dc", 0)
                result = {"aura_name": perk["name"], "source": fname, "target": name}
                if save_stat and save_dc:
                    sv = self.save(name, save_stat, save_dc)
                    result["save"] = sv
                    result["affected"] = not sv["success"]
                else:
                    result["affected"] = True  # no save = auto-apply
                results.append(result)
                if result["affected"]:
                    self._log(f"  AURA: {perk['name']} ({fname}) → {name} AFFECTED")
                else:
                    self._log(f"  AURA: {perk['name']} ({fname}) → {name} RESISTED")
        return results

    def add_status(self, tgt, name, category="condition", duration=-1, compound_clears="", source=""):
        s = Status(name=name, category=category, duration=duration, round_applied=self.round, compound_clears=compound_clears, source=source)
        self.fighters[tgt].add_status(s); self._log(f"  {tgt} gains [{name}]")

    def save(self, name, stat, dc, adv=False, dis=False, auto_fail=False):
        c = self.fighters[name]; mod = c.stats.get(stat, 0)
        if auto_fail or c.has_status("stunned"):
            # Check legendary resistance before auto-fail
            if c.legendary_resistances_remaining > 0:
                c.use_legendary_resistance()
                self._log(f"  {name} {stat.upper()} DC {dc}: Would AUTO-FAIL → ⚡LEGENDARY RESISTANCE ({c.legendary_resistances_remaining} left)")
                return {"nat":0,"total":0,"dc":dc,"success":True,"legendary":True}
            self._log(f"  {name} {stat.upper()} DC {dc}: AUTO-FAIL"); return {"nat":0,"total":0,"dc":dc,"success":False}
        nat = max(d20(),d20()) if adv else (min(d20(),d20()) if dis else d20())
        total = nat + mod; ok = total >= dc
        # Legendary resistance on fail
        if not ok and c.legendary_resistances_remaining > 0:
            c.use_legendary_resistance()
            self._log(f"  {name} {stat.upper()}: nat {nat}+{mod}={total} vs DC {dc} → FAIL → ⚡LEGENDARY RESISTANCE ({c.legendary_resistances_remaining} left)")
            return {"nat":nat,"total":total,"dc":dc,"success":True,"legendary":True}
        self._log(f"  {name} {stat.upper()}: nat {nat}+{mod}={total} vs DC {dc} → {'PASS' if ok else 'FAIL'}")
        return {"nat":nat,"total":total,"dc":dc,"success":ok}

    def state(self):
        lines = [f"╔══ ROUND {self.round} ══╗"]
        for _, n in self.order:
            f = self.fighters[n]
            lines.append(f"  {f.status_line()}")
            lines.append(f"    {f.action_economy_line()}")
        lines.append(f"╚{'═'*30}╝"); return "\n".join(lines)

    def move_away(self, mover: str, from_who: str, distance: int) -> dict:
        """Handle movement away from an enemy. Checks for OA if no disengage."""
        m = self.fighters[mover]
        threat = self.fighters[from_who]
        result = {"oa_triggered": False, "oa_result": None, "moved": True}
        
        # Check if mover disengaged this turn
        disengage = m.has_status("disengaged")
        
        if not disengage and not threat.reaction_used:
            # Opportunity attack triggered
            self._log(f"  {mover} moves without Disengage — {from_who} gets Opportunity Attack!")
            result["oa_triggered"] = True
        
        m.movement_remaining = max(0, m.movement_remaining - distance)
        return result
    
    def disengage(self, name: str) -> Tuple[bool, str]:
        """Attempt to Disengage. Costs ACTION unless has Cunning Action (bonus)."""
        c = self.fighters[name]
        if c.has_cunning_action:
            ok, msg = c.use_bonus_action("Disengage (Cunning Action)")
            if ok:
                c.add_status(Status(name="disengaged", category="condition", duration=1))
                self._log(f"  {name} Disengages (bonus action — Cunning Action)")
                return True, "Disengaged (bonus)"
            return False, msg
        else:
            ok, msg = c.use_action("Disengage")
            if ok:
                c.add_status(Status(name="disengaged", category="condition", duration=1))
                self._log(f"  {name} Disengages (action)")
                return True, "Disengaged (action)"
            return False, f"Cannot Disengage — {msg}"

    def recent_log(self, n=15): return "\n".join(self.log[-n:])
    def _log(self, msg): self.log.append(f"R{self.round}: {msg}")
    
    # ---- LAIR ACTIONS (Initiative 20) ----
    
    def process_lair_action(self, boss_name: str) -> Optional[Dict]:
        """Process lair action for a boss. Called at initiative 20 each round. Returns action details."""
        boss = self.fighters.get(boss_name)
        if not boss or not boss.lair_actions or not boss.alive: return None
        # Cycle through lair actions round-robin
        action = boss.lair_actions[(self.round - 1) % len(boss.lair_actions)]
        self._log(f"  🏰 LAIR ACTION: {action['name']} — {action.get('effect', '')}")
        return action
    
    # ---- LEGENDARY ACTIONS (Between player turns) ----
    
    def process_legendary_action(self, boss_name: str, action_name: str, cost: int = 1) -> bool:
        """Boss uses a legendary action between another creature's turns."""
        boss = self.fighters.get(boss_name)
        if not boss or not boss.alive: return False
        if not boss.use_legendary_action(cost):
            self._log(f"  {boss_name}: Not enough legendary actions ({boss.legendary_actions_remaining}/{boss.legendary_actions_max})")
            return False
        self._log(f"  ⚡ LEGENDARY ACTION ({boss.legendary_actions_remaining}/{boss.legendary_actions_max}): {action_name}")
        return True
    
    # ---- REINFORCEMENT WAVES ----
    
    def add_reinforcements(self, combatants: List, description: str = "Reinforcements arrive!"):
        """Add new combatants mid-fight. They act next round."""
        self._log(f"  🚨 {description}")
        for c_data in combatants:
            if isinstance(c_data, dict):
                c = load_combatant(c_data)
            else:
                c = c_data
            init_roll = d20() + c.initiative_mod
            self.fighters[c.name] = c
            self.order.append((init_roll, c.name))
            self._log(f"    + {c.name} (init {init_roll}) — HP {c.hp}/{c.max_hp}")
        self.order.sort(key=lambda x: -x[0])
    
    # ---- TERRAIN & ZONES ----
    # Zone examples:
    # {"name": "Acid Pool", "position": 30, "radius": 15, "damage": "2d6", "dtype": "acid",
    #   "save_stat": "dex", "save_dc": 14, "duration": 5, "rounds_remaining": 5}
    # {"name": "Anti-Magic", "position": 50, "radius": 15, "effect": "suppress_buffs", "duration": 3}
    # {"name": "Difficult Terrain", "position": 0, "radius": 100, "effect": "half_speed"}
    
    def add_zone(self, name: str, position: int, radius: int, duration: int = -1, **kwargs):
        """Add a terrain zone. Duration -1 = permanent."""
        zone = {"name": name, "position": position, "radius": radius, 
                "duration": duration, "rounds_remaining": duration, **kwargs}
        self.zones.append(zone)
        self._log(f"  🌍 ZONE: {name} at {position}ft, {radius}ft radius" + 
                  (f", {duration}rd" if duration > 0 else " (permanent)"))
        return zone
    
    def tick_zones(self):
        """Tick zone durations. Called at start of each round."""
        expired = []
        for z in self.zones:
            if z["rounds_remaining"] > 0:
                z["rounds_remaining"] -= 1
                if z["rounds_remaining"] == 0: expired.append(z)
        for z in expired:
            self.zones.remove(z)
            self._log(f"  🌍 ZONE EXPIRED: {z['name']}")
        return expired
    
    def check_zones(self, name: str) -> List[Dict]:
        """Check which zones affect a combatant at their position."""
        c = self.fighters[name]
        active = []
        for z in self.zones:
            if abs(c.position - z["position"]) <= z["radius"]:
                active.append(z)
        return active
    
    # ---- POSITION TRACKING ----
    
    def set_position(self, name: str, position: int, elevation: int = 0):
        c = self.fighters[name]
        c.position = position; c.elevation = elevation
        self._log(f"  {name} → position {position}ft, elevation {elevation}ft")
    
    def distance_between(self, name1: str, name2: str) -> int:
        """Get distance between two combatants (simple linear + elevation)."""
        c1, c2 = self.fighters[name1], self.fighters[name2]
        horiz = abs(c1.position - c2.position)
        vert = abs(c1.elevation - c2.elevation)
        return int((horiz**2 + vert**2)**0.5)  # pythagorean
    
    def in_range(self, attacker: str, target: str, range_ft: int) -> bool:
        return self.distance_between(attacker, target) <= range_ft
    
    # ---- MORALE CHECK ----
    
    def check_morale(self, name: str) -> bool:
        """Check if a creature wants to flee. Returns True if fleeing."""
        c = self.fighters[name]
        if c.check_morale():
            self._log(f"  🏃 {name} MORALE BREAK — attempts to flee!")
            return True
        return False
    
    # ---- ENHANCED STATE DISPLAY ----
    
    def battlefield(self) -> str:
        """Show full battlefield state including positions and zones."""
        lines = [f"╔══ ROUND {self.round} — BATTLEFIELD ══╗"]
        # Combatants by position
        by_pos = sorted([(f.position, f.elevation, n, f) for n, f in self.fighters.items() if f.alive], key=lambda x: x[0])
        for pos, elev, name, f in by_pos:
            elev_str = f" ↑{elev}ft" if elev > 0 else (f" ↓{abs(elev)}ft" if elev < 0 else "")
            lines.append(f"  [{pos}ft{elev_str}] {f.status_line()}")
        # Dead
        dead = [n for n, f in self.fighters.items() if not f.alive]
        if dead: lines.append(f"  DEAD: {', '.join(dead)}")
        # Zones
        if self.zones:
            lines.append(f"  ── ZONES ──")
            for z in self.zones:
                dur = f"{z['rounds_remaining']}rd" if z['rounds_remaining'] > 0 else "permanent"
                lines.append(f"  🌍 {z['name']} @ {z['position']}ft ({z['radius']}ft radius) [{dur}]")
        lines.append(f"╚{'═'*35}╝")
        return "\n".join(lines)

# ============================================================
# EXP SYSTEM
# ============================================================

CR_EXP = {
    0: 10, 0.125: 25, 0.25: 50, 0.5: 100,
    1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
    6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900,
    11: 7200, 12: 8400, 13: 10000, 14: 11500, 15: 13000,
    16: 15000, 17: 18000, 18: 20000, 19: 22000, 20: 25000,
    21: 33000, 22: 41000, 23: 50000, 24: 62000, 25: 75000,
}

LEVEL_THRESHOLDS = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
    6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
    11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
    16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
}

PARTY_MULTIPLIER = {
    0: 4.0,   # solo
    1: 2.0,   # duo
    2: 1.0,   # standard (player + 2)
    3: 1.0,   # large
}  # 4+ allies = 0.5

SKILL_CHECK_EXP = {
    (8, 10): 5, (11, 14): 10, (15, 17): 15, (18, 20): 25, (21, 99): 50,
}

class EXPTracker:
    def __init__(self, current_exp: int = 0, current_level: int = 1):
        self.exp = current_exp
        self.level = current_level
        self.combat_log: List[Dict[str, Any]] = []
        self.pending_exp: int = 0

    def get_level_for_exp(self, exp: int) -> int:
        lvl = 1
        for level, threshold in sorted(LEVEL_THRESHOLDS.items()):
            if exp >= threshold: lvl = level
        return lvl

    def exp_to_next(self) -> int:
        next_lvl = self.level + 1
        if next_lvl in LEVEL_THRESHOLDS:
            return LEVEL_THRESHOLDS[next_lvl] - self.exp
        return 0

    def award_combat(self, cr: float, allies: int = 0, description: str = "") -> int:
        """Award EXP for a combat encounter. allies = number of allied combatants (0 = solo)."""
        base = CR_EXP.get(cr, 0)
        if allies >= 4:
            mult = 0.5
        else:
            mult = PARTY_MULTIPLIER.get(allies, 1.0)
        awarded = int(base * mult)
        self.pending_exp += awarded
        entry = {"type": "combat", "cr": cr, "base": base, "mult": mult, "allies": allies,
                 "awarded": awarded, "desc": description}
        self.combat_log.append(entry)
        return awarded

    def award_check(self, dc: int, description: str = "") -> int:
        """Award EXP for a successful skill check."""
        awarded = 0
        for (lo, hi), exp in SKILL_CHECK_EXP.items():
            if lo <= dc <= hi:
                awarded = exp; break
        self.pending_exp += awarded
        self.combat_log.append({"type": "check", "dc": dc, "awarded": awarded, "desc": description})
        return awarded

    def award_milestone(self, exp: int, description: str = "") -> int:
        """Award milestone/discovery EXP."""
        self.pending_exp += exp
        self.combat_log.append({"type": "milestone", "awarded": exp, "desc": description})
        return exp

    def commit(self) -> dict:
        """Commit pending EXP. Returns level-up info."""
        old_exp = self.exp
        old_level = self.level
        self.exp += self.pending_exp
        new_level = self.get_level_for_exp(self.exp)
        levels_gained = new_level - old_level
        result = {
            "old_exp": old_exp, "new_exp": self.exp, "gained": self.pending_exp,
            "old_level": old_level, "new_level": new_level, "levels_gained": levels_gained,
            "next_threshold": LEVEL_THRESHOLDS.get(new_level + 1, 0),
            "exp_to_next": LEVEL_THRESHOLDS.get(new_level + 1, 0) - self.exp,
        }
        self.level = new_level
        self.pending_exp = 0
        return result

    def end_combat_summary(self) -> str:
        """Print full EXP summary for the session."""
        lines = ["╔══ EXP SUMMARY ══╗"]
        total = 0
        for entry in self.combat_log:
            if entry["type"] == "combat":
                lines.append(f"  ⚔️ {entry.get('desc','Combat')} — CR {entry['cr']} × {entry['mult']}x = {entry['awarded']:,} EXP")
            elif entry["type"] == "check":
                lines.append(f"  🎲 {entry.get('desc','Check')} — DC {entry['dc']} = {entry['awarded']} EXP")
            elif entry["type"] == "milestone":
                lines.append(f"  ⭐ {entry.get('desc','Milestone')} = {entry['awarded']:,} EXP")
            total += entry["awarded"]
        lines.append(f"  ─────────────────")
        lines.append(f"  Total pending: {total:,}")
        lines.append(f"  Current EXP: {self.exp:,}")
        lines.append(f"  After commit: {self.exp + self.pending_exp:,}")
        projected = self.get_level_for_exp(self.exp + self.pending_exp)
        if projected > self.level:
            lines.append(f"  🔺 LEVEL UP: {self.level} → {projected} (Long Rest required)")
        lines.append(f"  EXP to Level {projected + 1}: {LEVEL_THRESHOLDS.get(projected + 1, 0) - (self.exp + self.pending_exp):,}")
        lines.append(f"╚{'═'*20}╝")
        return "\n".join(lines)

# ============================================================
# REFERENCE CONSTANTS — Mechanics formerly in dm_rules_tracking.md
# The DM referee guide (dm_rules_tracking.md) now points here for numbers.
# ============================================================

# --- EXP TABLE (cumulative thresholds) ---
EXP_TABLE = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
    9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
    15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
    21: 450000, 22: 550000, 23: 675000, 24: 825000, 25: 1000000,
    26: 1200000, 27: 1400000, 28: 1650000, 29: 1900000, 30: 2200000,
    31: 2400000, 32: 2600000, 33: 2800000, 34: 3000000, 35: 2500000,  # 35 is Kenji's cap area
}

# --- CR → EXP REFERENCE ---
CR_EXP = {
    0: 10, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450, 3: 700, 4: 1100,
    5: 1800, 6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900, 11: 7200,
    12: 8400, 13: 10000, 14: 11500, 15: 13000, 16: 15000, 17: 18000,
    18: 20000, 19: 22000, 20: 25000, 21: 33000, 22: 41000, 23: 50000,
    24: 62000, 25: 75000, 26: 90000, 27: 105000, 28: 120000, 29: 135000,
    30: 155000,
}

# --- COMBAT EXP MULTIPLIERS (party size) ---
EXP_MULTIPLIERS = {
    "solo": 4.0,        # Kenji alone
    "duo": 2.0,         # Kenji + 1 companion
    "small_party": 1.5, # Kenji + 2-3
    "full_party": 1.0,  # 4+ members
}

# --- EXHAUSTION LEVELS (D&D 5e standard) ---
EXHAUSTION = {
    1: "Disadvantage on ability checks",
    2: "Speed halved",
    3: "Disadvantage on attack rolls and saving throws",
    4: "Hit point maximum halved",
    5: "Speed reduced to 0",
    6: "Death",
}

# --- STANDARD D&D CONDITIONS ---
CONDITIONS = {
    "blinded": "Can't see. Auto-fail sight checks. Attacks have disadvantage, attacks against have advantage.",
    "charmed": "Can't attack charmer. Charmer has advantage on social checks.",
    "deafened": "Can't hear. Auto-fail hearing checks.",
    "frightened": "Disadvantage on checks/attacks while source visible. Can't willingly move closer.",
    "grappled": "Speed 0. Ends if grappler incapacitated or effect removes.",
    "incapacitated": "Can't take actions or reactions.",
    "invisible": "Impossible to see without magic. Attacks have advantage, attacks against have disadvantage.",
    "paralyzed": "Incapacitated. Can't move or speak. Auto-fail STR/DEX saves. Attacks have advantage. Melee hits are auto-crits.",
    "petrified": "Transformed to stone. Weight x10. Incapacitated. Resistant to all damage. Immune to poison/disease.",
    "poisoned": "Disadvantage on attack rolls and ability checks.",
    "prone": "Disadvantage on attacks. Attacks from within 5ft have advantage, beyond have disadvantage. Costs half speed to stand.",
    "restrained": "Speed 0. Attacks have disadvantage. Attacks against have advantage. Disadvantage on DEX saves.",
    "stunned": "Incapacitated. Can't move. Speak only falteringly. Auto-fail STR/DEX saves. Attacks against have advantage.",
    "unconscious": "Incapacitated. Can't move or speak. Unaware. Drop what held. Fall prone. Auto-fail STR/DEX. Attacks have advantage. Melee auto-crit.",
}

# --- ENCOUNTER ROLL TABLE (dangerous territory) ---
# d6 per hour of travel, d6 per 3 hours of rest
# Kenji's cover (Greater Invis, Wind Step, Windstrider, Living Ground) bumps 1-2 → near miss
ENCOUNTER_TABLE_TRAVEL = {
    1: "encounter",   2: "encounter",
    3: "no_encounter", 4: "no_encounter",
    5: "no_encounter", 6: "no_encounter",
}
ENCOUNTER_TABLE_TRAVEL_COVER = {
    1: "encounter",
    2: "no_encounter", 3: "no_encounter",
    4: "no_encounter", 5: "no_encounter", 6: "no_encounter",
}
ENCOUNTER_TABLE_REST = ENCOUNTER_TABLE_TRAVEL  # same odds, different frequency
ENCOUNTER_TABLE_REST_COVER = ENCOUNTER_TABLE_TRAVEL_COVER

# --- AMBUSH TABLE ---
# After encounter fires, roll d6 for ambush.
# 1-2: enemy ambush (free turn), 3-4: neutral (no surprise), 5-6: player ambush (free turn)
# Kenji cover shifts result +1 (enemy→neutral, neutral→player)
AMBUSH_TABLE = {
    1: "enemy_ambush", 2: "enemy_ambush",
    3: "neutral",      4: "neutral",
    5: "player_ambush", 6: "player_ambush",
}

# --- WIND STEP TRAVEL TIERS ---
WIND_STEP_TIERS = {
    "base":    {"mph": 25, "description": "Standard chained Wind Step. Silent, agile, wuxia."},
    "stealth": {"mph": 40, "description": "Clone runs road as decoy, Kenji ghost-steps parallel. Can be seen/stopped."},
    "sprint":  {"mph": 80, "description": "All-out kung fu montage. Kicking off obstacles, air-walking, sky-glide. Flashy."},
    "burst":   {"mph": 200, "description": "Maximum airborne glide phase of sprint. Fastest without ember/Arcane Stride."},
}

# --- FALL DAMAGE ---
def fall_damage(feet: int) -> str:
    """D&D 5e fall damage: 1d6 per 10 feet, max 20d6."""
    dice = min(feet // 10, 20)
    if dice <= 0: return "No damage"
    total, rolls, _ = roll_dice(f"{dice}d6")
    return f"{dice}d6 = {total} bludgeoning (rolls: {rolls})"

# --- PERK REFERENCE (Kenji's earned perks by level) ---
PERK_TABLE = {
    3:  "Speedster (Type C): Arcane Stride Enhanced (12hr, 1 slot, extra action). Fast Metabolism (hunger 4hr, healing doubled).",
    6:  "God Sight: 120ft darkvision, crit range 18-20, +60 thrown range, advantage Perception.",
    9:  "Giant's Throw: 1.5x thrown dmg, 3x range, Counter Throw reaction.",
    12: "Bonded Lovers: +1 STR/CON per intimate partner. Soul Nexus: all partner abilities passive.",
    15: "Irresistible Presence: DC 23 Siren-Elf aura (procreative urge, NOT charm/dominate), always on. Lover's Vigor + 5-day IP immunity when semen reaches vagina (Book 3: elf sister + hair) — see kenji_tracking_OBSOLETE.md.",
    18: "Sorcerer's Hegemony: 48 constructs/day, delegated command.",
}

# --- CARRYING / ENCUMBRANCE ---
def carrying_capacity(strength: int) -> dict:
    """D&D 5e carrying rules with Kenji's STR."""
    return {
        "carry": strength * 15,
        "push_drag_lift": strength * 30,
        "encumbered": strength * 5,       # -10 speed
        "heavily_encumbered": strength * 10,  # -20 speed, disadvantage STR/DEX/CON
    }

# ============================================================
# ============================================================
# WORLD STATE
# ============================================================

class StoryEngine:
    def __init__(self, data: dict = None):
        d = data or {}
        
        # TIME — Hour-based tracking. 1 interaction = 1 hour.
        self.day = d.get("day", 1)
        self.hour = d.get("hour", 6)  # 0-23. Dawn=6, Morning=8, Midday=12, Afternoon=14, Evening=18, Night=21
        self.hours_since_meal = d.get("hours_since_meal", 0)  # Fast Metabolism: eat every 4
        self.meal_interval = 4  # hours between meals before penalty
        
        # LOCATION
        self.location = d.get("location", "Unknown")
        self.weather = d.get("weather", "Clear")
        
        # CHARACTER
        self.char_name = d.get("char_name", "Kenji")
        self.level = d.get("level", 1)
        self.exp = d.get("exp", 0)
        self.hp = d.get("hp", 0)
        self.max_hp = d.get("max_hp", 0)
        self.temp_hp = d.get("temp_hp", 0)
        self.ac = d.get("ac", 10)
        self.spell_slots = d.get("spell_slots", {})  # {"1": [cur, max], ...}
        self.gold = d.get("gold", 0)
        self.silver = d.get("silver", 0)
        self.copper = d.get("copper", 0)
        self.meals = d.get("meals", 0)
        
        
        # INVENTORY
        self.equipped = d.get("equipped", [])       # ["Emberfang", "Frost Fang", ...]
        self.satchel = d.get("satchel", [])         # ["41 meals", "Garrett's envelope"]
        self.consumables = d.get("consumables", {})  # {"Somnus doses": 0, "Bittershade": 0}
        self.key_items = d.get("key_items", [])     # ["Circuit Bracelet", "Hollow Crown (in satchel)"]
        
        # BUFFS
        self.buffs = d.get("buffs", {})  # {"God Sight": {"duration": "46hr", "effects": "crit 18-20"}}
        
        # STATUS
        self.statuses = d.get("statuses", [])  # ["healthy", "well-fed", "rested"]
        
        # CHARGES
        self.charges = d.get("charges", {})  # {"Blade Ward": [3,3], "Ember Lance": [5,5]}
        
        # PORTALS
        self.portals = d.get("portals", {})  # {"Varenholm": "active", ...}
        self.portal_max = d.get("portal_max", 8)
        
        # SCHEDULE / EVENTS
        self.events = d.get("events", [])  
        # [{"name": "Tournament", "day": 21, "type": "deadline", "priority": "HIGH"}]
        
        # QUEST OBJECTIVES
        self.quests = d.get("quests", [])
        # [{"name": "Bleakmoor source", "status": "active", "priority": "HIGH", "notes": ""}]
        
        # SQUADS
        self.squads = d.get("squads", {})
        # {"Darkblades": {"captain": "Sera", "status": "deployed", "location": "Eastern highway", "mission": "sweep"}}
        
        # ASSETS / INCOME — each asset has daily_gp and daily_sp for auto-deposit
        # "status": "active" = deposits daily. "frozen"/"pending" = no deposits.
        # Golden Age doubles all income — applied in process_income()
        self.assets = d.get("assets", [])
        # [{"name": "Highway Contract", "daily_gp": 2, "daily_sp": 66, "status": "active", "display": "80 GP/month"},
        #  {"name": "Guild Stipend", "daily_gp": 0, "daily_sp": 100, "status": "active", "display": "100-300 SP/delivery"},
        #  {"name": "Mine Ore", "daily_gp": 0, "daily_sp": 27, "status": "frozen", "display": "~8 GP/month"}]
        self.golden_age_active = d.get("golden_age_active", True)  # doubles all income
        
        # NPCs
        self.npcs = d.get("npcs", {})
        # {"Sera": {"location": "Eastern highway", "activity": "Darkblades sweep", "disposition": "deep trust"}}
        
        # WEATHER PROFILES PER LOCATION
        self.weather_profiles = d.get("weather_profiles", {
            "Varenholm": ["Clear", "Overcast", "Light rain", "Cold wind"],
            "Duskfen": ["Misty", "Humid", "Drizzle", "Fog"],
            "Bleakmoor": ["Grey overcast", "Dead air", "Cold", "Ash wind"],
            "Thornwall": ["Dry", "Windy", "Clear", "Dust"],
            "Crestfall": ["Cold", "Clear", "Frost", "Bitter wind"],
            # Book 4 locations
            "Thornfield": ["Overcast", "Light rain", "Clearing mist", "Cool wind", "Pale sun"],
            "Greymere": ["Grey overcast", "Drizzle", "Cold fog", "Damp wind"],
            "Millhaven": ["Overcast", "Light rain", "Cold wind", "Clear morning", "Frost at dawn"],
            "Thornkeep": ["Overcast", "Hard frost predawn", "Cold wind off the crown", "Clear cold", "Sleet"],
            "Bronzebarrow": ["Forge haze", "Hard frost predawn", "Cold clear", "Relay wind off the crown road", "Overcast", "Thin smoke and yard dust"],
            "Western cut": ["Trail mist", "Cold dusk", "Stars through cloud breaks", "Ridge wind", "Frost on deadfall"],
        })
        
        # HEARTS & MINDS — Squad EXP tracking
        self.hm_log = d.get("hm_log", [])
        self.hm_total_today = d.get("hm_total_today", 0)
        
        # NOBLE'S INTEREST — Gold compound tracking
        self.noble_interest_active = d.get("noble_interest_active", True)
        self.gold_yesterday = d.get("gold_yesterday", 0)
        
        # PERKS — active/inactive status for display
        self.active_perks = d.get("active_perks", [])
        
        # WEAPON CONFIG — for display
        self.weapon_config = d.get("weapon_config", "")
        self.weapon_config_detail = d.get("weapon_config_detail", "")
        
        # ============================================================
        # LIVING WORLD SYSTEMS
        # ============================================================
        
        # THREAT CLOCKS — Things progressing whether player acts or not
        # Progress 0-100. Rate = % per day. At 100, the threat fires.
        self.threat_clocks = d.get("threat_clocks", {})
        # {"Sundered Gate": {"progress": 35, "rate": 8, "trigger": "Gate opens. Mordecai wins.",
        #     "description": "Mordecai's gate opening ritual", "accelerated": True},
        #  "Council Investigation": {"progress": 20, "rate": 5, "trigger": "Formal audit. Assets frozen.",
        #     "description": "Council building case against ArchMagus"}}
        
        # NPC AGENDAS — What NPCs want, tracked with progress
        self.npc_agendas = d.get("npc_agendas", {})
        # {"Senna": {"goal": "Prove she can beat Kenji", "progress": 20, "deadline_day": 29,
        #     "actions": ["Training daily", "Studying his tactics"], "blocked_by": ""},
        #  "Garrett": {"goal": "Win mine hearing", "progress": 60, "deadline_day": 21,
        #     "actions": ["Gathering witnesses", "Building legal case"], "blocked_by": "Missing ore samples"}}
        
        # ORGANIZATION PLOTS — Factions with their own timelines
        self.org_plots = d.get("org_plots", {})
        # {"Council": {"plot": "Restrict ArchMagus authority", "progress": 25, "rate": 3,
        #     "next_move": "Subpoena guild records", "next_move_day": 22,
        #     "description": "Political pressure campaign against Kenji's expanding power"},
        #  "Mordecai's Backer": {"plot": "Open the Sundered Gate", "progress": 50, "rate": 8,
        #     "next_move": "Send construct reinforcements", "next_move_day": 19}}
        
        # WORLD EVENTS QUEUE — Things that happen on specific days regardless of player
        self.world_events = d.get("world_events", [])
        # [{"day": 19, "hour": 12, "event": "Darkblades reach Thornwall", "effect": "Sera reports in person",
        #     "fired": False},
        #  {"day": 20, "hour": 18, "event": "Tournament registration closes", "effect": "No more entries",
        #     "fired": False}]
        
        # CONSEQUENCE QUEUE — Delayed effects of player actions
        self.consequences = d.get("consequences", [])
        # [{"trigger_day": 20, "cause": "Charmed Thessaly in Academy corridor",
        #     "effect": "Elara hears. Summons Kenji for a conversation.", "fired": False},
        #  {"trigger_day": 22, "cause": "Giant portal built at Bleakmoor crater",
        #     "effect": "Thornwall patrol reports 'new abyssal gate' sighting. Military response.", "fired": False}]
        
        # REPUTATION — What the world knows about Kenji
        self.reputation = d.get("reputation", {})
        # {"Academy": {"level": "ArchMagus", "opinion": "respected/feared", "knows": ["portal network", "ember power", "killed Solveth's prison"]},
        #  "Thornwall Military": {"level": "known combatant", "opinion": "wary", "knows": ["portals appearing", "Bleakmoor activity"]},
        #  "Criminal Networks": {"level": "high-value target", "opinion": "interested", "knows": ["carries wealth", "travels with satchel"]}}
        
        # RELATIONSHIP TRACKER — Numeric disposition with history
        self.relationships = d.get("relationships", {})
        
        # CONSTRUCT ARMY — Sorcerer's Hegemony (Level 18 perk)
        # Per-portal tracking: {"Varenholm": {"squads": 3, "warrior": 3, "healer": 3, "mage": 3, "ranger": 3, "destroyed": 2}}
        self.construct_army = d.get("construct_army", {})
        # Population fear per location: 0=none, 1=unsettling, 2=fear, 3=panic, 4=crisis
        self.construct_fear = d.get("construct_fear", {})
        self.hegemony_active = d.get("hegemony_active", False)  # True once Level 18 perk earned
        
        # EVENT PROGRESSION TRACKER — Tournaments, Dungeons, Sieges, etc.
        # Flexible multi-stage event system. Each event has stages (rounds/floors/waves).
        # Tracks combatants, results, brackets, loot, and progression.
        # Usage:
        #   start_event("Tournament", "tournament", {...})
        #   log_bout(event_name, bout_num, fighter_a, fighter_b, winner, rounds, details)
        #   advance_stage(event_name)
        #   end_event(event_name)
        self.events_active = d.get("events_active", {})
        # Example tournament:
        # {"Tournament": {
        #     "type": "tournament",       # tournament | dungeon | siege | custom
        #     "stage": 1,                 # current round/floor/wave
        #     "max_stages": 3,            # total rounds/floors
        #     "status": "active",         # active | complete | failed
        #     "combatants": {"Kenji": {"hp": 93, "max_hp": 93, "status": "active", "wins": 1},
        #                    "Sera": {"hp": 65, "max_hp": 65, "status": "active", "wins": 1}},
        #     "bracket": [                # ordered list of bouts
        #         {"bout": 1, "stage": 1, "a": "Kenji", "b": "Greave", "winner": "Kenji", "rounds": 4, "details": "Never stood up"},
        #     ],
        #     "loot": [],                 # dungeon loot collected
        #     "notes": "",
        # }}
        # {"Senna": {"score": -15, "tier": "cold", "history": [
        #     {"day": 17, "change": -30, "reason": "Portal-dumped 60 miles"},
        #     {"day": 18, "change": +15, "reason": "Professional combat cooperation"}]},
        #  "Thessaly": {"score": -5, "tier": "reluctant", "history": [
        #     {"day": 17, "change": -20, "reason": "Charmed in public"},
        #     {"day": 18, "change": +15, "reason": "Saved from Glass Stalker"}]}}
        
        # AI / NARRATIVE BRIDGE — short text for LLM sessions (see ai_brief_markdown())
        self.canon_pointer = d.get("canon_pointer", "")
        self.story_beat = d.get("story_beat", "")
        self.narrative_notes = d.get("narrative_notes", [])
        # CHARACTER GOALS — machine-readable rows for deadline / overdue / optional auto_resolve
        # Schema per item: character, goal_id, status (active|in_progress|open|overdue|resolved|mia|closed_overdue),
        # due_day (engine day), public_day (optional), summary, arc_file (optional doc pointer),
        # kenji_hook (effect on Kenji — queued text), auto_resolve (bool),
        # replacement (optional dict — new goal row), on_resolve (optional {append_consequence: {...}}).
        self.character_goals: List[dict] = list(d.get("character_goals", []))
        
        # CHARACTER SHEET — optional blocks for dashboard / brief (D&D-style; empty = omit in UI)
        self.ability_scores = d.get("ability_scores", {})  # {"STR": 14, "DEX": 16, ...}
        self.skills = d.get("skills", {})  # {"Perception": "+5", "Athletics": "+7", ...}
        self.known_spells = d.get("known_spells", [])  # ["Shield", "Fireball", ...]
        self.class_features = d.get("class_features", [])  # ["Metamagic", "Font of Magic", ...]
        
        # SAVE INTEGRITY — OneDrive sync protection
        self._save_version = d.get("_save_version", 0)
        self._saved_at = d.get("_saved_at", "")
        self._construct_total_expected = d.get("_construct_total_expected", -1)

        # PASSTHROUGH — any other top-level JSON keys (e.g. universe, inherited_lore, shared_world
        # from templates/new_character_campaign) round-trip on save_json(). _comment is stripped in load_json.
        self._known_top_level_keys = frozenset({
            "day", "hour", "hours_since_meal", "location", "weather", "char_name", "level", "exp",
            "hp", "max_hp", "temp_hp", "ac", "spell_slots", "gold", "silver", "copper", "meals",
            "equipped", "satchel", "consumables", "key_items", "buffs", "statuses", "charges",
            "portals", "portal_max", "events", "quests", "squads", "assets", "npcs",
            "golden_age_active", "hm_log", "hm_total_today", "noble_interest_active", "gold_yesterday",
            "active_perks", "weapon_config", "weapon_config_detail", "weather_profiles",
            "threat_clocks", "npc_agendas", "org_plots", "world_events", "consequences",
            "reputation", "relationships", "construct_army", "construct_fear", "hegemony_active",
            "events_active", "canon_pointer", "story_beat", "narrative_notes", "character_goals",
            "ability_scores", "skills", "known_spells", "class_features",
            "_save_version", "_saved_at", "_construct_total_expected",
        })
        self.extra_json: dict = {}
        for k, v in d.items():
            if k not in self._known_top_level_keys:
                self.extra_json[k] = v
    
    # ---- TIME ----
    
    def time_of_day(self) -> str:
        if self.hour < 6: return "Night"
        elif self.hour < 8: return "Dawn"
        elif self.hour < 12: return "Morning"
        elif self.hour < 14: return "Midday"
        elif self.hour < 18: return "Afternoon"
        elif self.hour < 21: return "Evening"
        else: return "Night"

    def clock_display(self) -> str:
        """Format self.hour as HH:MM (supports fractional hours, e.g. recon timestamps)."""
        hf = float(self.hour) % 24.0
        if hf < 0:
            hf += 24.0
        h = int(hf)
        m = int(round((hf - h) * 60.0)) % 60
        return f"{h:02d}:{m:02d}"

    def _advance_time(self, hours: int = 1) -> List[str]:
        """Single source of truth for time, buff expiry, meal counter, and day rollover.
        Returns list of alerts (expired buffs, new-day processing)."""
        alerts = []
        self.hour += hours
        self.hours_since_meal += hours
        expired = []
        for name in list(self.buffs.keys()):
            b = self.buffs[name]
            dur = b.get("duration_hrs", -1)
            if dur > 0:
                b["duration_hrs"] = dur - hours
                if b["duration_hrs"] <= 0:
                    del self.buffs[name]
                    expired.append(name)
        for name in expired:
            alerts.append(f"⏰ Buff expired: {name}")
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
            day_results = self.process_new_day()
            alerts.extend(day_results)
        return alerts
    
    def advance_day(self):
        """Jump to next morning (Long Rest). Restores resources + runs daily pipeline."""
        self.day += 1
        self.hour = 6
        self.hours_since_meal = 0
        self.restore_all_slots()
        self.restore_all_charges()
        self.buffs.clear()
        return self.process_new_day()
    
    def hours_until(self, target_day: int, target_hour: int = 6) -> int:
        """Hours until a target day+hour."""
        target_total = target_day * 24 + target_hour
        current_total = self.day * 24 + self.hour
        return max(0, target_total - current_total)
    
    def meal_status(self) -> str:
        if self.hours_since_meal >= 8: return "!! STARVING (-disadv STR/CON/WIS, no short rest HP)"
        elif self.hours_since_meal >= 6: return "!! HUNGRY (-1 STR/CON)"
        elif self.hours_since_meal >= 3: return f"{4 - self.hours_since_meal}hr until hungry"
        else: return "Fed"
    
    # ---- UPDATES ----
    
    def set_location(self, loc: str, weather: str = None):
        self.location = loc
        if weather:
            self.weather = weather
        elif loc in self.weather_profiles:
            import random
            self.weather = random.choice(self.weather_profiles[loc])
    
    def add_buff(self, name: str, duration_hrs: int, effects: str):
        self.buffs[name] = {"duration_hrs": duration_hrs, "effects": effects}
    
    def add_event(self, name: str, day: int, etype: str = "deadline", priority: str = "MEDIUM", notes: str = ""):
        self.events.append({"name": name, "day": day, "type": etype, "priority": priority, "notes": notes})
    
    def complete_event(self, name: str):
        self.events = [e for e in self.events if e["name"] != name]
    
    def update_squad(self, name: str, status: str = None, location: str = None, mission: str = None):
        if name in self.squads:
            if status: self.squads[name]["status"] = status
            if location: self.squads[name]["location"] = location
            if mission: self.squads[name]["mission"] = mission
    
    def update_npc(self, name: str, location: str = None, activity: str = None, disposition: str = None):
        if name not in self.npcs:
            self.npcs[name] = {"location": "", "activity": "", "disposition": ""}
        if location: self.npcs[name]["location"] = location
        if activity: self.npcs[name]["activity"] = activity
        if disposition: self.npcs[name]["disposition"] = disposition
    
    def spend_gold(self, gp: int = 0, sp: int = 0, cp: int = 0):
        self.copper -= cp
        if self.copper < 0:
            borrow = abs(self.copper)
            self.silver -= (borrow // 100) + 1
            self.copper = 100 - (borrow % 100)
        self.silver -= sp
        if self.silver < 0:
            borrow = abs(self.silver)
            self.gold -= (borrow // 100) + 1
            self.silver = 100 - (borrow % 100)
        self.gold -= gp
    
    def eat_meal(self, from_satchel: bool = True):
        if from_satchel and self.meals > 0:
            self.meals -= 1
        self.hours_since_meal = 0
    
    def spend_slot(self, level: str, count: int = 1) -> bool:
        """Spend spell slot(s). Returns True if successful."""
        if level not in self.spell_slots:
            return False
        cur, mx = self.spell_slots[level]
        if cur < count:
            return False
        self.spell_slots[level][0] = cur - count
        return True
    
    def restore_slot(self, level: str, count: int = 1):
        """Restore spell slot(s), capped at max."""
        if level not in self.spell_slots:
            return
        cur, mx = self.spell_slots[level]
        self.spell_slots[level][0] = min(mx, cur + count)
    
    def restore_all_slots(self):
        """Refill all spell slots to max (long rest)."""
        for level in self.spell_slots:
            self.spell_slots[level][0] = self.spell_slots[level][1]
    
    def spend_charge(self, name: str, count: int = 1) -> bool:
        """Spend charge(s). Returns True if successful."""
        if name not in self.charges:
            return False
        cur, mx = self.charges[name]
        if cur < count:
            return False
        self.charges[name][0] = cur - count
        return True
    
    def restore_charge(self, name: str, count: int = 1):
        """Restore charge(s), capped at max."""
        if name not in self.charges:
            return
        cur, mx = self.charges[name]
        self.charges[name][0] = min(mx, cur + count)
    
    def restore_all_charges(self):
        """Refill all charges to max (long rest)."""
        for name in self.charges:
            self.charges[name][0] = self.charges[name][1]
    
    def remove_buff(self, name: str) -> bool:
        """Remove a buff by name. Returns True if found and removed."""
        if name in self.buffs:
            del self.buffs[name]
            return True
        return False
    
    def tick_interaction(self) -> List[str]:
        """THE ONE METHOD TO CALL EVERY INTERACTION. Advances 1 hour, checks everything.
        Returns list of alerts the DM must narrate."""
        alerts = self._advance_time(1)
        
        meal_alert = self.check_meal()
        if meal_alert: alerts.append(meal_alert)
        
        for event in self.world_events:
            if not isinstance(event, dict):
                continue
            if "day" not in event:
                continue
            if not event.get("fired") and event["day"] == self.day and event.get("hour", 0) <= self.hour:
                event["fired"] = True
                alerts.append(f"🌍 EVENT: {event['event']} — {event.get('effect', '')}")
        
        for con in self.consequences:
            if not con.get("fired") and con["trigger_day"] <= self.day:
                con["fired"] = True
                alerts.append(f"⏰ CONSEQUENCE: {con['cause']} → {con['effect']}")
        
        return alerts
    
    def check_expired_buffs(self) -> List[str]:
        """Check and remove expired buffs. Returns list of expired buff names."""
        expired = []
        to_remove = []
        for name, b in self.buffs.items():
            dur_key = "duration_hrs" if "duration_hrs" in b else "duration"
            if dur_key in b and b[dur_key] > 0:
                b[dur_key] -= 1
                if b[dur_key] <= 0:
                    to_remove.append(name)
                    expired.append(name)
        for name in to_remove:
            del self.buffs[name]
        return expired
    
    def check_meal(self) -> Optional[str]:
        """Check meal status. Returns alert string if hungry/penalty."""
        if self.hours_since_meal >= self.meal_interval + 2:
            return f"HUNGER PENALTY ACTIVE — {self.hours_since_meal}hr since last meal. -1 to all checks."
        elif self.hours_since_meal >= self.meal_interval:
            return f"EAT NOW — {self.hours_since_meal}hr since last meal."
        return None
    
    def estimate_squad_hm(self, squad_name: str, kills_per_day: int = 2, avg_cr: int = 5) -> int:
        """Estimate daily Hearts & Minds EXP for a deployed squad. Auto-logs."""
        base_exp = CR_EXP.get(avg_cr, 1800)
        # Squad kills use duo multiplier (x2) since they work together
        daily_exp = kills_per_day * base_exp * 2
        self.log_hm_exp(squad_name, f"Est. {kills_per_day} kills CR{avg_cr}/day", daily_exp)
        return daily_exp
    
    def to_dict(self) -> dict:
        """Serialize entire state to dict. Use for save/load between sessions.
        Merges extra_json last so combined-universe / template keys round-trip."""
        core = {
            "_save_version": self._save_version,
            "_saved_at": self._saved_at,
            "_construct_total_expected": self._construct_total_expected,
            "day": self.day, "hour": self.hour, "hours_since_meal": self.hours_since_meal,
            "location": self.location, "weather": self.weather,
            "char_name": self.char_name, "level": self.level, "exp": self.exp,
            "hp": self.hp, "max_hp": self.max_hp, "temp_hp": self.temp_hp, "ac": self.ac,
            "spell_slots": self.spell_slots,
            "gold": self.gold, "silver": self.silver, "copper": self.copper, "meals": self.meals,
            "equipped": self.equipped, "satchel": self.satchel,
            "consumables": self.consumables, "key_items": self.key_items,
            "buffs": self.buffs, "statuses": self.statuses,
            "charges": self.charges,
            "portals": self.portals, "portal_max": self.portal_max,
            "events": self.events, "quests": self.quests,
            "squads": self.squads, "assets": self.assets, "npcs": self.npcs,
            "golden_age_active": self.golden_age_active,
            "hm_log": self.hm_log, "hm_total_today": self.hm_total_today,
            "noble_interest_active": self.noble_interest_active,
            "gold_yesterday": self.gold_yesterday,
            "active_perks": self.active_perks,
            "weapon_config": self.weapon_config, "weapon_config_detail": self.weapon_config_detail,
            "threat_clocks": self.threat_clocks, "npc_agendas": self.npc_agendas,
            "org_plots": self.org_plots, "world_events": self.world_events,
            "consequences": self.consequences, "reputation": self.reputation,
            "relationships": self.relationships,
            "construct_army": self.construct_army,
            "construct_fear": self.construct_fear,
            "hegemony_active": self.hegemony_active,
            "events_active": self.events_active,
            "canon_pointer": self.canon_pointer,
            "story_beat": self.story_beat,
            "narrative_notes": self.narrative_notes,
            "character_goals": self.character_goals,
            "ability_scores": self.ability_scores,
            "skills": self.skills,
            "known_spells": self.known_spells,
            "class_features": self.class_features,
        }
        if self.extra_json:
            merged = {**core, **self.extra_json}
            return merged
        return core
    
    def log_hm_exp(self, squad: str, desc: str, exp: int):
        self.hm_log.append({"squad": squad, "desc": desc, "exp": exp})
        self.hm_total_today += exp; self.exp += exp
    
    def apply_noble_interest(self):
        self.gold_yesterday = self.gold + (self.silver / 100)
        self.gold = int(self.gold * 1.5)
        overflow_sp = int(self.silver * 0.5)
        self.silver += overflow_sp
        while self.silver >= 100: self.silver -= 100; self.gold += 1
    
    def projected_gold(self) -> float:
        return (self.gold + (self.silver / 100)) * 1.5
    
    # ============================================================
    # LIVING WORLD PROCESSING
    # ============================================================
    
    def process_income(self) -> List[str]:
        """Process daily income from all active assets. Golden Age doubles everything. Called by process_new_day."""
        results = []
        total_gp = 0; total_sp = 0
        mult = 2 if self.golden_age_active else 1
        
        for asset in self.assets:
            if asset.get("status", "active") != "active": continue
            dgp = asset.get("daily_gp", 0) * mult
            dsp = asset.get("daily_sp", 0) * mult
            if dgp > 0 or dsp > 0:
                total_gp += dgp; total_sp += dsp
                ga_note = " (2x Golden Age)" if mult > 1 else ""
                results.append(f"  💰 {asset['name']}: +{dgp} GP {dsp} SP{ga_note}")
        
        # Convert overflow SP to GP
        total_gp += total_sp // 100
        total_sp = total_sp % 100
        
        if total_gp > 0 or total_sp > 0:
            self.gold += total_gp; self.silver += total_sp
            while self.silver >= 100: self.silver -= 100; self.gold += 1
            results.insert(0, f"💰 DAILY INCOME: +{total_gp} GP {total_sp} SP deposited")
        
        return results
    
    def process_character_goals(self) -> List[str]:
        """Check `character_goals` against engine `day`. Emits DM alerts; optionally closes a goal
        and appends `replacement` / `consequences` when `auto_resolve` is true on the goal row.
        Does **not** edit `character_tracker.md` or arc markdown — DM mirrors fallout there."""
        out: List[str] = []
        for g in self.character_goals:
            if not isinstance(g, dict):
                continue
            st = (g.get("status") or "").strip().lower()
            if st in ("resolved", "mia", "closed", "closed_overdue", "complete", "completed", "superseded"):
                continue
            if st and st not in ACTIVE_CHARACTER_GOAL_STATUSES:
                continue
            char = g.get("character", "?")
            gid = g.get("goal_id", "?")
            due = g.get("due_day")
            if due is None:
                continue
            try:
                due_i = int(due)
            except (TypeError, ValueError):
                continue
            pub = g.get("public_day")
            if pub is not None:
                try:
                    pub_i = int(pub)
                except (TypeError, ValueError):
                    pub_i = None
                if pub_i is not None and self.day >= pub_i and not g.get("_public_window_announced"):
                    g["_public_window_announced"] = True
                    summ = g.get("summary", "")
                    out.append(f"📣 PUBLIC WINDOW: **{char}** `{gid}` — day {pub_i}+ — {summ}")
            if self.day == due_i - 1:
                out.append(f"⏳ GOAL DUE NEXT DAWN: **{char}** `{gid}` (deadline engine day {due_i})")
            if self.day < due_i:
                continue
            if self.day == due_i and not g.get("_due_announced"):
                g["_due_announced"] = True
                out.append(f"🎯 GOAL DEADLINE: **{char}** `{gid}` — {g.get('summary', '')}")
            elif self.day > due_i and not g.get("_overdue_announced"):
                g["_overdue_announced"] = True
                hook = g.get("kenji_hook", "")
                hook_txt = f" Kenji hook: {hook}" if hook else ""
                out.append(
                    f"⚠️ GOAL OVERDUE: **{char}** `{gid}` (was due engine day {due_i}).{hook_txt}"
                )
            if g.get("auto_resolve") and self.day >= due_i and not g.get("_resolved_by_engine"):
                g["_resolved_by_engine"] = True
                g["status"] = (g.get("resolved_status") or "resolved").strip().lower()
                repl = g.get("replacement")
                if isinstance(repl, dict):
                    repl = dict(repl)
                    repl.setdefault("status", "active")
                    self.character_goals.append(repl)
                    out.append(
                        f"🎯 ENGINE CLOSED **{char}** `{gid}` → replacement `{repl.get('goal_id', '?')}`"
                    )
                or_append = g.get("on_resolve") or {}
                cons = or_append.get("append_consequence")
                if isinstance(cons, dict):
                    cons = dict(cons)
                    cons.setdefault("fired", False)
                    cons.setdefault("trigger_day", self.day)
                    self.consequences.append(cons)
                    c0 = str(cons.get("cause", ""))[:100]
                    out.append(f"  ⏰ Consequence queued: {c0}")
                arc_c = g.get("arc_commit")
                if arc_c:
                    af = g.get("arc_file", "active arc")
                    out.append(f"  📜 DM: paste into `{af}` — {arc_c}")
        return out

    def process_new_day(self):
        """Called at dawn each day. Advances ALL world systems."""
        results = []
        
        # Asset Income (deposits BEFORE Noble's Interest so it compounds)
        income_results = self.process_income()
        results.extend(income_results)
        
        # Noble's Interest (compounds AFTER income deposited)
        if self.noble_interest_active:
            old = self.gold + (self.silver / 100)
            self.apply_noble_interest()
            new = self.gold + (self.silver / 100)
            results.append(f"💰 Noble's Interest: {old:.1f} GP → {new:.1f} GP")
        
        # Threat clocks advance
        for name, clock in self.threat_clocks.items():
            clock["progress"] = min(100, clock["progress"] + clock["rate"])
            if clock["progress"] >= 100:
                results.append(f"🚨 THREAT CLOCK FIRED: {name} — {clock['trigger']}")
            elif clock["progress"] >= 75:
                results.append(f"⚠️ Threat clock critical: {name} ({clock['progress']}%) — {clock['description']}")
            elif clock["progress"] >= 50:
                results.append(f"📊 Threat clock: {name} ({clock['progress']}%)")
        
        # NPC agendas advance
        for npc, agenda in self.npc_agendas.items():
            if agenda.get("deadline_day") and self.day >= agenda["deadline_day"]:
                results.append(f"📋 {npc} agenda deadline: {agenda['goal']}")
        
        # Character goals (machine-readable; see kenji_state.json character_goals)
        cg_results = self.process_character_goals()
        results.extend(cg_results)
        
        # Org plots advance
        for org, plot in self.org_plots.items():
            plot["progress"] = min(100, plot["progress"] + plot.get("rate", 0))
            if plot.get("next_move_day") == self.day:
                results.append(f"🏛️ {org} MOVES: {plot['next_move']}")
            if plot["progress"] >= 100:
                results.append(f"🚨 ORG PLOT FIRES: {org} — {plot['plot']}")
        
        # World events and consequences are handled by tick_interaction()
        # with proper hour checks — not duplicated here.
        
        # Construct Army spawning (Sorcerer's Hegemony)
        if self.hegemony_active:
            construct_results = self.spawn_constructs()
            if construct_results:
                results.append(f"🤖 CONSTRUCT SPAWN: +{len([p for p,s in self.portals.items() if s=='active'])} squads ({self.total_constructs()} total)")
                results.extend(construct_results)
                # Fear consequences
                for portal, fear in self.construct_fear.items():
                    if fear >= 3:
                        results.append(f"  ⚠️ {portal}: PANIC LEVEL {fear} — population demanding action")
        
        # H&M daily reset
        self.hm_total_today = 0
        self.hm_log = []
        
        return results
    
    def advance_threat(self, name: str, amount: int):
        """Manually advance a threat clock (e.g., player action accelerated/decelerated it)."""
        if name in self.threat_clocks:
            self.threat_clocks[name]["progress"] = min(100, max(0, self.threat_clocks[name]["progress"] + amount))
    
    def update_relationship(self, npc: str, change: int, reason: str):
        """Update an NPC relationship score with history."""
        if npc not in self.relationships:
            self.relationships[npc] = {"score": 0, "tier": "neutral", "history": []}
        r = self.relationships[npc]
        r["score"] += change
        r["history"].append({"day": self.day, "change": change, "reason": reason})
        # Update tier based on score
        s = r["score"]
        if s <= -30: r["tier"] = "hostile"
        elif s <= -10: r["tier"] = "cold"
        elif s <= 10: r["tier"] = "neutral"
        elif s <= 30: r["tier"] = "friendly"
        elif s <= 50: r["tier"] = "close"
        else: r["tier"] = "intimate"
    
    # ---- TRAVEL & ENCOUNTER MECHANICS (formerly in dm_rules_tracking.md) ----

    def encounter_roll(self, mode: str = "travel", kenji_cover: bool = True) -> dict:
        """Roll for encounter in dangerous territory. Binary: encounter or no encounter.
        mode: 'travel' (d6/hr) or 'rest' (d6/3hr).
        kenji_cover: if True, only a roll of 1 triggers encounter (instead of 1-2).
        Returns: {'roll': int, 'result': str, 'description': str}
        If encounter fires, also rolls ambush check (d6).
        See dm_rules_tracking.md § BINARY ENCOUNTER SYSTEM.
        """
        roll = random.randint(1, 6)
        if mode == "travel":
            table = ENCOUNTER_TABLE_TRAVEL_COVER if kenji_cover else ENCOUNTER_TABLE_TRAVEL
        else:
            table = ENCOUNTER_TABLE_REST_COVER if kenji_cover else ENCOUNTER_TABLE_REST
        result = table[roll]

        out = {"roll": roll, "result": result}

        if result == "encounter":
            # Roll ambush check
            ambush = self.ambush_roll(kenji_cover)
            out["ambush"] = ambush
            cover_note = " (cover active, threshold=1)" if kenji_cover else " (no cover, threshold=1-2)"
            out["description"] = (
                f"d6={roll} → ENCOUNTER{cover_note}. "
                f"Ambush: {ambush['description']}. DM generates threat appropriate to region."
            )
        else:
            out["description"] = f"d6={roll} → no encounter. Travel continues."
        return out

    def ambush_roll(self, kenji_cover: bool = True) -> dict:
        """Roll d6 for ambush when an encounter fires.
        1-2: enemy ambush (free turn), 3-4: neutral, 5-6: player ambush (free turn).
        kenji_cover shifts result +1 (enemy→neutral, neutral→player).
        See dm_rules_tracking.md § AMBUSH CHECK.
        """
        roll = random.randint(1, 6)
        raw_result = AMBUSH_TABLE[roll]
        result = raw_result
        if kenji_cover:
            if raw_result == "enemy_ambush":
                result = "neutral"
            elif raw_result == "neutral":
                result = "player_ambush"
            # player_ambush stays player_ambush

        descriptions = {
            "enemy_ambush": f"d6={roll} → ENEMY AMBUSH. Enemies get a free turn before initiative.",
            "neutral": f"d6={roll} → NEUTRAL. No surprise. Roll initiative normally.",
            "player_ambush": f"d6={roll} → PLAYER AMBUSH. Kenji gets a free turn before initiative.",
        }
        return {"roll": roll, "raw": raw_result, "result": result, "description": descriptions[result]}

    def travel_time(self, miles: float, tier: str = "base") -> dict:
        """Calculate travel time at a given Wind Step tier.
        Returns hours, encounter roll count, and description.
        See WIND_STEP_TIERS for tier definitions.
        """
        speed = WIND_STEP_TIERS.get(tier, WIND_STEP_TIERS["base"])["mph"]
        hours = miles / speed
        encounter_rolls = max(1, int(hours))  # minimum 1 roll
        if hours < 1:
            encounter_rolls = 1  # always at least 1 check
        return {
            "miles": miles, "speed_mph": speed, "tier": tier,
            "hours": round(hours, 2), "encounter_rolls": encounter_rolls,
            "description": f"{miles}mi at {speed}mph ({tier}) = {hours:.1f}hr → {encounter_rolls} encounter roll(s)"
        }

    def travel_leg(self, miles: float, tier: str = "base", kenji_cover: bool = True) -> dict:
        """Execute a full travel leg: calculate time, roll binary encounters, check hunger.
        Binary system: encounter or no encounter. No near-miss stops.
        If encounter fires → includes ambush roll. Travel pauses for DM narration.
        If no encounters → travel completes, DM narrates arrival at objective.
        See dm_rules_tracking.md § BINARY ENCOUNTER SYSTEM.
        """
        calc = self.travel_time(miles, tier)
        hours = max(1, int(calc["hours"]))
        results = {
            "calc": calc, "hours_elapsed": 0, "encounters": [],
            "alerts": [], "meals_consumed": 0, "arrived": False
        }

        for hr in range(hours):
            # Advance 1 hour
            time_alerts = self._advance_time(1)
            results["alerts"].extend(time_alerts)
            results["hours_elapsed"] += 1

            # Check hunger — Travel Hunger Protocol
            meal_alert = self.check_meal()
            if meal_alert:
                results["alerts"].append(meal_alert)

            # Auto-eat at STARVING (8+ hrs) if player hasn't acted — per dm_rules protocol
            if self.hours_since_meal >= 8 and self.meals > 0:
                self.eat_meal(from_satchel=True)
                results["meals_consumed"] += 1
                results["alerts"].append(
                    f"🍖 AUTO-EAT (STARVING): Kenji ate from satchel mid-stride. "
                    f"Meals remaining: {self.meals}. Timer reset."
                )

            # Binary encounter roll
            enc = self.encounter_roll("travel", kenji_cover)
            enc["hour"] = hr + 1
            results["encounters"].append(enc)

            # If encounter fires, stop travel — DM narrates encounter
            if enc["result"] == "encounter":
                results["alerts"].append(
                    f"⚔️ ENCOUNTER at hour {hr+1}! "
                    f"Ambush: {enc['ambush']['result']}. Travel paused. DM narrates."
                )
                break
        else:
            # No encounter across all hours — player arrives at objective
            results["arrived"] = True
            results["alerts"].append(
                f"✅ ARRIVED. {hours} hour(s) traveled, no encounters. DM narrates arrival at objective."
            )

        return results

    def rest_check(self, hours: int = 8, kenji_cover: bool = True) -> dict:
        """Roll binary encounter checks during rest in dangerous territory.
        d6 every 3 hours. Encounter or no encounter. If encounter → ambush roll.
        No watch = enemy ambush is automatic (no ambush roll needed).
        See dm_rules_tracking.md § REST ENCOUNTER ROLLS.
        """
        rolls_needed = max(1, hours // 3)
        results = {"hours": hours, "encounters": [], "alerts": [], "rest_complete": True}
        for i in range(rolls_needed):
            enc = self.encounter_roll("rest", kenji_cover)
            enc["rest_hour"] = (i + 1) * 3
            results["encounters"].append(enc)
            if enc["result"] == "encounter":
                results["rest_complete"] = False
                results["alerts"].append(
                    f"⚔️ REST INTERRUPTED at hour {(i+1)*3}! "
                    f"Ambush: {enc['ambush']['result']}."
                )
                break
        if results["rest_complete"]:
            results["alerts"].append(f"✅ Rest complete. {hours} hours, no interruptions.")
        return results

    # ---- EXHAUSTION TRACKING ----

    def get_exhaustion(self) -> int:
        """Get current exhaustion level from statuses."""
        for s in self.statuses:
            if isinstance(s, str) and s.startswith("exhaustion_"):
                try: return int(s.split("_")[1])
                except: pass
        return 0

    def set_exhaustion(self, level: int) -> str:
        """Set exhaustion level (0-6). 0 = clear. 6 = death.
        Effects per level defined in EXHAUSTION constant.
        Causes: missed long rests, forced marching, extreme conditions, swimming in armor.
        """
        # Remove old exhaustion status
        self.statuses = [s for s in self.statuses if not (isinstance(s, str) and s.startswith("exhaustion_"))]
        if level > 0:
            self.statuses.append(f"exhaustion_{level}")
            effect = EXHAUSTION.get(level, "Unknown")
            return f"⚠️ EXHAUSTION LEVEL {level}: {effect}"
        return "Exhaustion cleared."

    def add_exhaustion(self, levels: int = 1) -> str:
        """Add exhaustion levels (stacking). Returns alert string."""
        current = self.get_exhaustion()
        new_level = min(6, current + levels)
        return self.set_exhaustion(new_level)

    def remove_exhaustion(self, levels: int = 1) -> str:
        """Remove exhaustion levels (long rest removes 1). Returns alert string."""
        current = self.get_exhaustion()
        new_level = max(0, current - levels)
        return self.set_exhaustion(new_level)

    def add_consequence(self, trigger_day: int, cause: str, effect: str):
        self.consequences.append({"trigger_day": trigger_day, "cause": cause, "effect": effect, "fired": False})
    
    def add_world_event(self, day: int, hour: int, event: str, effect: str):
        self.world_events.append({"day": day, "hour": hour, "event": event, "effect": effect, "fired": False})
    
    def add_threat_clock(self, name: str, progress: int, rate: int, trigger: str, description: str):
        self.threat_clocks[name] = {"progress": progress, "rate": rate, "trigger": trigger, "description": description}
    
    # ---- CONSTRUCT ARMY (Sorcerer's Hegemony) ----
    
    def spawn_constructs(self) -> List[str]:
        """Spawn 1 squad (4 constructs) at each active portal. Called by process_new_day."""
        if not self.hegemony_active: return []
        results = []
        active_portals = [n for n, s in self.portals.items() if s == "active"]
        for portal in active_portals:
            if portal not in self.construct_army:
                self.construct_army[portal] = {"squads": 0, "warrior": 0, "healer": 0, "mage": 0, "ranger": 0, "destroyed": 0}
            army = self.construct_army[portal]
            self._normalize_army(army)
            army["squads"] += 1
            army["warrior"] += 1; army["healer"] += 1; army["mage"] += 1; army["ranger"] += 1
            total = army["warrior"] + army["healer"] + army["mage"] + army["ranger"]
            results.append(f"  🤖 {portal}: +1 squad (total: {army['squads']} squads, {total} constructs)")
        # Update fear levels
        self.update_construct_fear()
        return results
    
    def update_construct_fear(self):
        """Recalculate population fear per portal location based on construct count."""
        for portal, army in self.construct_army.items():
            squads = army.get("squads", 0)
            if squads <= 0: self.construct_fear[portal] = 0
            elif squads <= 2: self.construct_fear[portal] = 1  # unsettling
            elif squads <= 5: self.construct_fear[portal] = 2  # fear
            elif squads <= 10: self.construct_fear[portal] = 3  # panic
            else: self.construct_fear[portal] = 4  # crisis
    
    def _normalize_army(self, army: dict):
        """Ensure all construct type keys exist in an army dict."""
        for k in ("squads", "warrior", "healer", "mage", "ranger", "destroyed"):
            army.setdefault(k, 0)
    
    def teleport_constructs(self, from_portal: str, to_portal: str, count: int, unit_type: str = "all") -> str:
        """Move constructs between portals or to Kenji's location."""
        if from_portal not in self.construct_army: return "No constructs at source."
        army = self.construct_army[from_portal]
        self._normalize_army(army)
        if to_portal not in self.construct_army:
            self.construct_army[to_portal] = {"squads": 0, "warrior": 0, "healer": 0, "mage": 0, "ranger": 0, "destroyed": 0}
        dest = self.construct_army[to_portal]
        self._normalize_army(dest)
        
        if unit_type == "all":
            squads_to_move = min(count, army["squads"])
            for utype in ["warrior", "healer", "mage", "ranger"]:
                army[utype] -= squads_to_move
                dest[utype] += squads_to_move
            army["squads"] -= squads_to_move
            dest["squads"] += squads_to_move
            actually_moved = squads_to_move
            label = "squads"
        else:
            actually_moved = min(count, army.get(unit_type, 0))
            army[unit_type] -= actually_moved
            dest[unit_type] += actually_moved
            army["squads"] = min(army["warrior"], army["healer"], army["mage"], army["ranger"])
            dest["squads"] = min(dest["warrior"], dest["healer"], dest["mage"], dest["ranger"])
            label = unit_type
        
        self.update_construct_fear()
        return f"Moved {actually_moved} {label} from {from_portal} to {to_portal}"
    
    def destroy_constructs(self, portal: str, count: int):
        """Record construct losses at a portal, distributed evenly across roles."""
        if portal not in self.construct_army: return
        army = self.construct_army[portal]
        self._normalize_army(army)
        remaining = count
        roles = ["warrior", "healer", "mage", "ranger"]
        while remaining > 0:
            removed_this_pass = 0
            for utype in roles:
                if remaining <= 0:
                    break
                if army[utype] > 0:
                    army[utype] -= 1
                    army["destroyed"] += 1
                    remaining -= 1
                    removed_this_pass += 1
            if removed_this_pass == 0:
                break
        army["squads"] = min(army["warrior"], army["healer"], army["mage"], army["ranger"])
        self.update_construct_fear()
    
    def total_constructs(self) -> int:
        """Get total construct count across all portals."""
        keys = ("warrior", "healer", "mage", "ranger")
        return sum(
            sum(a.get(k, 0) for k in keys)
            for a in self.construct_army.values()
        )
    
    # ---- EVENT PROGRESSION (Tournaments, Dungeons, Sieges) ----
    
    def start_event(self, name: str, etype: str, max_stages: int, combatants: dict = None, notes: str = "") -> str:
        """Start a tracked event. etype: tournament, dungeon, siege, custom."""
        self.events_active[name] = {
            "type": etype, "stage": 1, "max_stages": max_stages,
            "status": "active", "combatants": combatants or {},
            "bracket": [], "loot": [], "notes": notes,
        }
        return f"Event started: {name} ({etype}, {max_stages} stages)"
    
    def add_combatant(self, event: str, name: str, hp: int, max_hp: int, status: str = "active", **extra):
        """Add a combatant/party to an event."""
        if event not in self.events_active: return
        self.events_active[event]["combatants"][name] = {
            "hp": hp, "max_hp": max_hp, "status": status, "wins": 0, "losses": 0, **extra
        }
    
    def log_bout(self, event: str, bout: int, a: str, b: str, winner: str, rounds: int, 
                 hp_a: int = 0, hp_b: int = 0, details: str = ""):
        """Log a bout/encounter result."""
        if event not in self.events_active: return
        ev = self.events_active[event]
        ev["bracket"].append({
            "bout": bout, "stage": ev["stage"], "a": a, "b": b,
            "winner": winner, "rounds": rounds, "hp_a": hp_a, "hp_b": hp_b,
            "details": details,
        })
        # Update combatant records
        if winner in ev["combatants"]:
            ev["combatants"][winner]["wins"] += 1
            ev["combatants"][winner]["hp"] = hp_a if winner == a else hp_b
        loser = b if winner == a else a
        if loser in ev["combatants"]:
            ev["combatants"][loser]["losses"] += 1
            ev["combatants"][loser]["status"] = "eliminated"
            ev["combatants"][loser]["hp"] = 0
    
    def log_room(self, event: str, room: int, encounter: str = "", loot: str = "", status: str = "cleared"):
        """Log a dungeon room/area. For dungeon-type events."""
        if event not in self.events_active: return
        self.events_active[event]["bracket"].append({
            "room": room, "stage": self.events_active[event]["stage"],
            "encounter": encounter, "loot": loot, "status": status,
        })
        if loot:
            self.events_active[event]["loot"].append(loot)
    
    def advance_stage(self, event: str) -> str:
        """Advance to next stage (round/floor). Heals tournament combatants."""
        if event not in self.events_active: return "Event not found"
        ev = self.events_active[event]
        ev["stage"] += 1
        # Tournament: heal all active combatants between rounds
        if ev["type"] == "tournament":
            for name, c in ev["combatants"].items():
                if c["status"] == "active":
                    c["hp"] = c["max_hp"]
        if ev["stage"] > ev["max_stages"]:
            ev["status"] = "complete"
            return f"{event}: COMPLETE"
        return f"{event}: Stage {ev['stage']}/{ev['max_stages']}"
    
    def end_event(self, event: str, result: str = "complete"):
        """End an event."""
        if event not in self.events_active: return
        self.events_active[event]["status"] = result
    
    def event_dashboard(self, event: str) -> str:
        """Generate display for an event's current state."""
        if event not in self.events_active: return "Event not found"
        ev = self.events_active[event]
        w = 58
        lines = []
        lines.append(f"╔{'═'*w}╗")
        title = f" {event.upper()} — Stage {ev['stage']}/{ev['max_stages']} ({ev['status'].upper()}) "
        lines.append(f"║{title:^{w}}║")
        lines.append(f"╠{'═'*w}╣")
        
        if ev["type"] == "tournament":
            # Show active combatants
            active = {n: c for n, c in ev["combatants"].items() if c["status"] == "active"}
            eliminated = {n: c for n, c in ev["combatants"].items() if c["status"] == "eliminated"}
            
            if active:
                lines.append(f"║ {'ACTIVE FIGHTERS':<{w}}║")
                for name, c in active.items():
                    fline = f"  ⚔️ {name}: {c['hp']}/{c['max_hp']} | W:{c['wins']} L:{c['losses']}"
                    lines.append(f"║ {fline:<{w}}║")
            
            if eliminated:
                lines.append(f"╠{'─'*w}╣")
                lines.append(f"║ {'ELIMINATED':<{w}}║")
                for name, c in eliminated.items():
                    fline = f"  ✗ {name} (W:{c['wins']} L:{c['losses']})"
                    lines.append(f"║ {fline:<{w}}║")
            
            # Show current stage bouts
            stage_bouts = [b for b in ev["bracket"] if b.get("stage") == ev["stage"]]
            prev_bouts = [b for b in ev["bracket"] if b.get("stage") < ev["stage"]]
            
            if prev_bouts:
                lines.append(f"╠{'─'*w}╣")
                lines.append(f"║ {'PREVIOUS ROUNDS':<{w}}║")
                for b in prev_bouts:
                    bline = f"  R{b['stage']} B{b['bout']}: {b['winner']} def. {b['b'] if b['winner']==b['a'] else b['a']} ({b['rounds']}rds)"
                    lines.append(f"║ {bline:<{w}}║")
            
            if stage_bouts:
                lines.append(f"╠{'─'*w}╣")
                lines.append(f"║ {'ROUND ' + str(ev['stage']) + ' RESULTS':<{w}}║")
                for b in stage_bouts:
                    bline = f"  B{b['bout']}: {b['winner']} def. {b['b'] if b['winner']==b['a'] else b['a']} ({b['rounds']}rds)"
                    if b.get("details"):
                        bline += f" — {b['details'][:25]}"
                    lines.append(f"║ {bline:<{w}}║")
        
        elif ev["type"] == "dungeon":
            # Show rooms cleared
            rooms = [b for b in ev["bracket"] if "room" in b]
            stage_rooms = [r for r in rooms if r.get("stage") == ev["stage"]]
            lines.append(f"║ {'FLOOR ' + str(ev['stage']):<{w}}║")
            for r in stage_rooms:
                status_icon = "✅" if r["status"] == "cleared" else "⚠️" if r["status"] == "partial" else "❌"
                rline = f"  {status_icon} Room {r['room']}: {r['encounter'][:30]}"
                lines.append(f"║ {rline:<{w}}║")
            if ev["loot"]:
                lines.append(f"╠{'─'*w}╣")
                lines.append(f"║ {'LOOT COLLECTED':<{w}}║")
                for item in ev["loot"]:
                    lines.append(f"║   ⭐ {item:<{w-4}}║")
        
        lines.append(f"╚{'═'*w}╝")
        return "\n".join(lines)
    
    # ---- v2.0 methods live in engine_v2.py (monkey-patched at import) ----
    # See: audit_goals, escalate_goals, check_perks, update_exp,
    #      validate_economy, apply_campaign_rules, generate_chapter_open_report
    # Usage: import engine_v2  # patches StoryEngine automatically

    # (v2.0 inline code removed — now in engine_v2.py)
    # Placeholder to prevent re-insertion:
    _v2_methods_in_engine_v2_py = True

    # ---- DASHBOARD ----


    def dashboard(self) -> str:
        lines = []
        w = 60
        lines.append(f"╔{'═'*w}╗")
        time_str = f"Day {self.day}, {self.clock_display()} — {self.time_of_day()}"
        lines.append(f"║ {self.char_name} — Level {self.level} — {time_str:<37}║")
        lines.append(f"║ {self.location} — {self.weather:<46}║")
        lines.append(f"║ {self.meal_status():<59}║")
        lines.append(f"╠{'═'*w}╣")
        
        # HP / AC / Slots
        hp_str = f"HP: {self.hp}/{self.max_hp}" + (f"+{self.temp_hp}t" if self.temp_hp else "")
        slots_str = " ".join(f"L{k}:{v[0]}/{v[1]}" for k, v in sorted(self.spell_slots.items(), key=lambda x: int(x[0])))
        lines.append(f"║ {hp_str} | AC {self.ac} | {slots_str:<30}║")
        
        # Currency / Meals
        cur = f"Gold: {self.gold} GP, {self.silver} SP, {self.copper} CP | Meals: {self.meals}"
        lines.append(f"║ {cur:<{w}}║")
        
        # Charges
        if self.charges:
            ch_str = " | ".join(f"{n}:{v[0]}/{v[1]}" for n, v in self.charges.items())
            lines.append(f"║ {ch_str:<{w}}║")
        
        # Buffs
        if self.buffs:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'ACTIVE BUFFS':<{w}}║")
            for name, b in self.buffs.items():
                dur = b.get("duration_hrs", -1)
                dur_str = f"{dur}hr" if dur > 0 else "permanent" if dur == -1 else b.get("duration", "?")
                bline = f"  {name} ({dur_str}) — {b.get('effects', '')}"
                lines.append(f"║ {bline:<{w}}║")
        
        # Status
        if self.statuses:
            lines.append(f"║ Status: {', '.join(self.statuses):<{w-8}}║")
        
        # Portals
        lines.append(f"╠{'─'*w}╣")
        active = [n for n, s in self.portals.items() if s == "active"]
        lines.append(f"║ {'PORTALS ' + str(len(active)) + '/' + str(self.portal_max):<{w}}║")
        if active:
            lines.append(f"║   {', '.join(active):<{w-2}}║")
        
        # Schedule
        if self.events:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'SCHEDULE':<{w}}║")
            for e in sorted(self.events, key=lambda x: x["day"]):
                hrs = self.hours_until(e["day"])
                days_away = hrs // 24
                urgency = "⚠️" if hrs <= 24 else "📅"
                if hrs == 0:
                    time_str = "NOW"
                elif hrs < 24:
                    time_str = f"{hrs}hr away"
                else:
                    time_str = f"{days_away}d {hrs % 24}hr away"
                etype = e.get('priority') or e.get('type', '?')
                ename = e.get('name') or e.get('summary', '')[:60]
                eline = f"  {urgency} [{etype}] {ename} — Day {e['day']} ({time_str})"
                enotes = e.get("notes") or (e.get("summary", '') if 'name' in e else '')
                if enotes and enotes != ename:
                    eline += f" — {enotes[:80]}"
                lines.append(f"║ {eline:<{w}}║")
        
        # Quests
        if self.quests:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'OBJECTIVES':<{w}}║")
            for q in self.quests:
                icon = "🔴" if q["priority"] == "HIGH" else ("🟡" if q["priority"] == "MEDIUM" else "🔵")
                qline = f"  {icon} {q['name']} [{q['status']}]"
                if q.get("notes"):
                    qline += f" — {q['notes']}"
                lines.append(f"║ {qline:<{w}}║")
        
        # Squads
        if self.squads:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'SQUADS':<{w}}║")
            for name, s in self.squads.items():
                icon = "⚔️" if s["status"] == "deployed" else "🏠"
                sline = f"  {icon} {name} ({s['captain']}) — {s['status']} @ {s['location']}"
                if s.get("mission"):
                    sline += f" — {s['mission']}"
                lines.append(f"║ {sline:<{w}}║")
        
        # Assets
        if self.assets:
            lines.append(f"╠{'─'*w}╣")
            ga = " (2x Golden Age)" if self.golden_age_active else ""
            lines.append(f"║ {'ASSETS & INCOME' + ga:<{w}}║")
            mult = 2 if self.golden_age_active else 1
            total_daily_gp = 0; total_daily_sp = 0
            for a in self.assets:
                icon = "💰" if a.get("status") == "active" else "❄️"
                # Show daily rate if available, otherwise show display string
                if "daily_gp" in a or "daily_sp" in a:
                    dgp = a.get("daily_gp", 0) * mult
                    dsp = a.get("daily_sp", 0) * mult
                    if a.get("status") == "active":
                        total_daily_gp += dgp; total_daily_sp += dsp
                    rate = f"+{dgp}gp {dsp}sp/day" if a.get("status") == "active" else "frozen"
                    disp = a.get("display", a["name"])
                    aline = f"  {icon} {a['name']}: {rate} ({disp})"
                else:
                    aline = f"  {icon} {a['name']} — {a.get('income', '?')} [{a.get('status', '?')}]"
                lines.append(f"║ {aline:<{w}}║")
            # Total daily
            total_daily_gp += total_daily_sp // 100; total_daily_sp = total_daily_sp % 100
            if total_daily_gp > 0 or total_daily_sp > 0:
                lines.append(f"║   📊 Total daily income: +{total_daily_gp} GP {total_daily_sp} SP{' '*(w-38-len(str(total_daily_gp))-len(str(total_daily_sp)))}║")
        
        # Key NPCs
        if self.npcs:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'KEY NPCs':<{w}}║")
            for name, n in self.npcs.items():
                nline = f"  {name}: {n['location']}"
                if n.get("activity"):
                    nline += f" — {n['activity']}"
                lines.append(f"║ {nline:<{w}}║")
        
        # INVENTORY — Full tracking
        lines.append(f"╠{'─'*w}╣")
        lines.append(f"║ {'INVENTORY':<{w}}║")
        if self.equipped:
            lines.append(f"║ {'  Equipped:':<{w}}║")
            eq_str = ", ".join(self.equipped)
            while len(eq_str) > w - 4:
                cut = eq_str[:w-4].rfind(",")
                if cut == -1: cut = w - 4
                lines.append(f"║   {eq_str[:cut+1]:<{w-2}}║")
                eq_str = eq_str[cut+1:].strip()
            if eq_str:
                lines.append(f"║   {eq_str:<{w-2}}║")
        if self.satchel:
            lines.append(f"║ {'  Satchel:':<{w}}║")
            for item in self.satchel:
                lines.append(f"║     {item:<{w-4}}║")
        if self.consumables:
            cons = " | ".join(f"{n}: {v}" for n, v in self.consumables.items())
            lines.append(f"║   Consumables: {cons:<{w-15}}║")
        if self.key_items:
            lines.append(f"║ {'  Key Items:':<{w}}║")
            for item in self.key_items:
                lines.append(f"║     ⭐ {item:<{w-6}}║")
        
        # Hearts & Minds EXP
        if self.hm_log or self.hm_total_today > 0:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'HEARTS & MINDS (Squad EXP)':<{w}}║")
            for entry in self.hm_log:
                hline = f"  ⚔️ {entry['squad']}: {entry['desc']} — {entry['exp']:,} EXP"
                lines.append(f"║ {hline:<{w}}║")
            lines.append(f"║   Total H&M today: {self.hm_total_today:,} EXP{' '*(w-28-len(str(self.hm_total_today)))}║")
        
        # Noble's Interest / Economy
        if self.noble_interest_active:
            lines.append(f"╠{'─'*w}╣")
            total_gp = self.gold + (self.silver / 100)
            projected = self.projected_gold()
            lines.append(f"║ {'WIZARD KING ECONOMY':<{w}}║")
            lines.append(f"║   Noble's Interest: {total_gp:.1f} GP today → {projected:.1f} GP tomorrow (+50%){' '*(max(0,w-60))}║")
            lines.append(f"║   Golden Age: All income x2 under leadership{' '*(w-47)}║")
        
        # Threat Clocks
        if self.threat_clocks:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'⏰ THREAT CLOCKS':<{w}}║")
            for name, clock in sorted(self.threat_clocks.items(), key=lambda x: -x[1]["progress"]):
                pct = clock["progress"]
                bar_len = 20
                filled = int(bar_len * pct / 100)
                bar = "█" * filled + "░" * (bar_len - filled)
                icon = "🚨" if pct >= 75 else ("⚠️" if pct >= 50 else "📊")
                cline = f"  {icon} {name}: [{bar}] {pct}% (+{clock['rate']}%/day)"
                lines.append(f"║ {cline:<{w}}║")
                if pct >= 75:
                    lines.append(f"║     → {clock['trigger']:<{w-6}}║")
        
        # Key Relationships (only show non-neutral)
        active_rels = {n: r for n, r in self.relationships.items() if r["score"] != 0}
        if active_rels:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'💬 KEY RELATIONSHIPS':<{w}}║")
            for name, r in sorted(active_rels.items(), key=lambda x: x[1]["score"]):
                score = r["score"]
                tier = r["tier"]
                icon = "❤️" if score > 20 else ("🟢" if score > 0 else ("🟡" if score == 0 else ("🔴" if score > -20 else "💀")))
                recent = r["history"][-1] if r["history"] else None
                recent_str = f" (last: {recent['reason']})" if recent else ""
                rline = f"  {icon} {name}: {tier} ({score:+d}){recent_str}"
                lines.append(f"║ {rline:<{w}}║")
        
        # Pending Consequences (unfired only)
        pending = [c for c in self.consequences if not c.get("fired")]
        if pending:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'⏳ PENDING CONSEQUENCES':<{w}}║")
            for con in sorted(pending, key=lambda x: x["trigger_day"]):
                days = con["trigger_day"] - self.day
                cline = f"  Day {con['trigger_day']} ({days}d): {con['cause'][:40]}"
                lines.append(f"║ {cline:<{w}}║")
        
        # Org Plots (show active ones)
        active_orgs = {n: p for n, p in self.org_plots.items() if p["progress"] < 100}
        if active_orgs:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'🏛️ FACTION PLOTS':<{w}}║")
            for org, plot in active_orgs.items():
                pct = plot["progress"]
                icon = "🚨" if pct >= 75 else "📊"
                oline = f"  {icon} {org}: {plot['plot'][:35]} ({pct}%)"
                lines.append(f"║ {oline:<{w}}║")
                if plot.get("next_move_day"):
                    days = plot["next_move_day"] - self.day
                    if days <= 2:
                        lines.append(f"║     → Next: {plot['next_move'][:35]} (Day {plot['next_move_day']}){' '*(max(0,w-55))}║")
        
        # NPC Agendas (compact — only show those with deadlines soon or high progress)
        urgent_agendas = {n: a for n, a in self.npc_agendas.items() 
                         if (a.get("deadline_day") and a["deadline_day"] - self.day <= 5) or a.get("progress", 0) >= 50}
        if urgent_agendas:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'📋 NPC AGENDAS (urgent)':<{w}}║")
            for npc, agenda in urgent_agendas.items():
                deadline = f"Day {agenda['deadline_day']}" if agenda.get("deadline_day") else "ongoing"
                aline = f"  {npc}: {agenda['goal'][:35]} ({agenda.get('progress',0)}%, {deadline})"
                lines.append(f"║ {aline:<{w}}║")
        
        # String entries = lore notes (e.g. Amaris combined-universe); scheduled dicts = timed events
        lore_world_notes = [e for e in self.world_events if isinstance(e, str) and e.strip()]
        if lore_world_notes:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'🌍 WORLD / LORE NOTES':<{w}}║")
            for note in lore_world_notes:
                chunk = note[: w - 4]
                lines.append(f"║   {chunk:<{w - 4}}║")
                if len(note) > w - 4:
                    rest = note[w - 4 :]
                    while rest:
                        lines.append(f"║   {rest[: w - 4]:<{w - 4}}║")
                        rest = rest[w - 4 :]

        # Upcoming World Events (unfired, within 3 days) — dict entries only
        upcoming = [
            e for e in self.world_events
            if isinstance(e, dict) and "day" in e
            and not e.get("fired") and e["day"] - self.day <= 3
        ]
        if upcoming:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'🌍 UPCOMING WORLD EVENTS':<{w}}║")
            for event in sorted(upcoming, key=lambda x: x["day"]):
                days = event["day"] - self.day
                eline = f"  Day {event['day']} ({days}d): {event['event'][:40]}"
                lines.append(f"║ {eline:<{w}}║")
        
        # Reputation (compact)
        if self.reputation:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'📢 REPUTATION':<{w}}║")
            for faction, rep in self.reputation.items():
                rline = f"  {faction}: {rep.get('opinion', '?')} ({rep.get('level', '?')})"
                lines.append(f"║ {rline:<{w}}║")
        
        # Construct Army (Sorcerer's Hegemony)
        if self.hegemony_active and self.construct_army:
            lines.append(f"╠{'─'*w}╣")
            total = self.total_constructs()
            lines.append(f"║ {'🤖 CONSTRUCT ARMY (' + str(total) + ' total)':<{w}}║")
            fear_labels = {0: "", 1: "👁️ unsettling", 2: "😰 fear", 3: "🚨 PANIC", 4: "💀 CRISIS"}
            for portal, army in self.construct_army.items():
                n_war, n_heal, n_mag, n_rng = (
                    army.get("warrior", 0),
                    army.get("healer", 0),
                    army.get("mage", 0),
                    army.get("ranger", 0),
                )
                count = n_war + n_heal + n_mag + n_rng
                squads = army.get("squads", 0)
                if count <= 0 and squads <= 0:
                    continue
                fear = self.construct_fear.get(portal, 0)
                fear_str = f" [{fear_labels.get(fear, '')}]" if fear > 0 else ""
                if count > 0:
                    cline = f"  {portal}: {squads}sq ({count}) W:{n_war} H:{n_heal} M:{n_mag} R:{n_rng}{fear_str}"
                else:
                    cline = f"  {portal}: {squads} squads (per-portal snapshot){fear_str}"
                lines.append(f"║ {cline:<{w}}║")
                if army.get("destroyed", 0) > 0:
                    lines.append(f"║     Destroyed: {army['destroyed']:<{w-16}}║")
        
        # Active Events (Tournament, Dungeon, etc.)
        for ename, ev in self.events_active.items():
            if ev["status"] != "active": continue
            lines.append(f"╠{'─'*w}╣")
            etitle = f"🏆 {ename.upper()} — Round {ev['stage']}/{ev['max_stages']}"
            lines.append(f"║ {etitle:<{w}}║")
            active_fighters = {n: c for n, c in ev["combatants"].items() if c["status"] == "active"}
            for name, c in active_fighters.items():
                fline = f"  ⚔️ {name}: {c['hp']}/{c['max_hp']} W:{c['wins']}"
                lines.append(f"║ {fline:<{w}}║")
            # Show latest stage results
            stage_bouts = [b for b in ev["bracket"] if b.get("stage") == ev["stage"]]
            if stage_bouts:
                for b in stage_bouts:
                    loser = b["b"] if b["winner"] == b["a"] else b["a"]
                    bline = f"  {b['bout']}: {b['winner']} def. {loser} ({b['rounds']}rds)"
                    lines.append(f"║ {bline:<{w}}║")
                fought = set()
                for b in stage_bouts:
                    fought.add(b["a"])
                    fought.add(b["b"])
                unfought = [n for n in active_fighters if n not in fought]
                if len(unfought) >= 2:
                    lines.append(f"║ {'  ⏳ UPCOMING:':<{w}}║")
                    for i in range(0, len(unfought) - 1, 2):
                        uline = f"    {unfought[i]} vs {unfought[i + 1]}"
                        lines.append(f"║ {uline:<{w}}║")

        # Abilities / Skills / Spells (character sheet)
        sheet_any = self.ability_scores or self.skills or self.known_spells or self.class_features
        if sheet_any:
            lines.append(f"╠{'─'*w}╣")
            lines.append(f"║ {'📋 ABILITIES / SKILLS / SPELLS':<{w}}║")
            if self.ability_scores:
                order = ('STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA')
                parts = []
                for k in order:
                    if k in self.ability_scores:
                        parts.append(f"{k} {self.ability_scores[k]}")
                for k in sorted(self.ability_scores.keys()):
                    if k not in order:
                        parts.append(f"{k} {self.ability_scores[k]}")
                ab = "  " + "  ".join(parts)
                for i in range(0, len(ab), w - 2):
                    seg = ab[i:i + w - 2]
                    lines.append(f"║ {seg:<{w}}║")
            if self.skills:
                lines.append(f"║ {'  Skills:':<{w}}║")
                for sk, mod in sorted(self.skills.items()):
                    sline = f"    {sk} {mod}"
                    lines.append(f"║ {sline[:w]:<{w}}║")
            if self.known_spells:
                lines.append(f"║ {'  Spells known:':<{w}}║")
                for sp in self.known_spells:
                    sline = f"    • {sp}"
                    lines.append(f"║ {sline[:w]:<{w}}║")
            if self.class_features:
                lines.append(f"║ {'  Class / passive features:':<{w}}║")
                for feat in self.class_features:
                    fline = f"    • {feat}"
                    lines.append(f"║ {fline[:w]:<{w}}║")

        # Perks
        lines.append(f"╠{'─'*w}╣")
        if self.active_perks:
            perk_str = ", ".join(self.active_perks)
            lines.append(f"║ PERKS: {perk_str:<{w-7}}║")
        else:
            lines.append(f"║ PERKS: None active (no friendly observer){' '*(w-42)}║")

        # Weapon Config
        if self.weapon_config:
            lines.append(f"║ CONFIG: {self.weapon_config.upper()} — {self.weapon_config_detail:<{w-11-len(self.weapon_config)}}║")

        # Exhaustion
        exh = self.get_exhaustion()
        if exh > 0:
            lines.append(f"╠{'─'*w}╣")
            exh_effect = EXHAUSTION.get(exh, '')
            lines.append(f"║ {'⚠️ EXHAUSTION LEVEL ' + str(exh) + ': ' + exh_effect:<{w}}║")

        # Cardinal Rules
        lines.append(f"╠{'─'*w}╣")
        lines.append(f"║ {'🚨 CARDINAL RULES (see dm_rules_tracking.md)':<{w}}║")
        lines.append(f"║   1. NEVER write Kenji's dialogue. STOP for player.{' '*(w-52)}║")
        lines.append(f"║   2. NEVER auto-resolve combat. Round-by-round ONLY.{' '*(w-53)}║")
        lines.append(f"║   3. STOP at every decision point. Present, don't decide.{' '*(w-58)}║")
        lines.append(f"║   4. No fabricated exposition NPCs (RULE 4).{' '*(w-46)}║")
        lines.append(f"║   5. 60% dialogue minimum. Ronin style tax (RULE 6).{' '*(w-53)}║")
        lines.append(f"║   6. 1hr/beat travel. Flag hunger at 4hr. Auto-eat 8hr.{' '*(w-55)}║")

        lines.append(f"╚{'═'*w}╝")
        return "\n".join(lines)

    def scene_prompt(self, scene_type="arrival", npcs_present=None):
        """Generate a DM scene prompt with player agency reminders.
        scene_type: arrival, combat, social, rest, travel, shopping
        npcs_present: list of NPC names in the scene
        """
        npcs = npcs_present or []
        lines = []
        lines.append(f"┌── SCENE: {scene_type.upper()} ──┐")
        lines.append(f"│ Location: {self.location}")
        lines.append(f"│ Time: Day {self.day}, {self.clock_display()} — {self.time_of_day()}")
        lines.append(f"│ NPCs present: {', '.join(npcs)}")
        lines.append("│")
        lines.append("│ DM WRITES:")
        lines.append("│   ✅ NPC dialogue (what THEY say)")
        lines.append("│   ✅ Environment (what player SEES, HEARS, SMELLS)")
        lines.append("│   ✅ NPC actions and reactions")
        lines.append("│   ✅ Consequences of player's stated actions")
        lines.append("│ DM NEVER WRITES:")
        lines.append("│   ❌ Player dialogue (what Kenji SAYS)")
        lines.append("│   ❌ Player decisions (what Kenji CHOOSES to do)")
        lines.append("│   ❌ Player emotional reactions narrated as fact")
        lines.append("│   ❌ Player walking somewhere unprompted")
        lines.append("│ SCENE FLOW:")
        if scene_type == "arrival":
            lines.append("│   1. Describe the location (one paragraph)")
            lines.append("│   2. NPCs react to player arriving")
            lines.append("│   3. First NPC speaks")
            lines.append("│   4. STOP — wait for player to respond")
        elif scene_type == "social":
            lines.append("│   1. NPC initiates or continues conversation")
            lines.append("│   2. STOP after NPC's line — let player respond")
            lines.append("│   3. Never run both sides of a conversation")
        elif scene_type == "rest":
            lines.append("│   1. Describe comfort (food, bath, bed) via NPC dialogue")
            lines.append("│   2. NPCs comment on the relief — they're people too")
            lines.append("│   3. STOP before Long Rest — ask player if anything before sleep")
        elif scene_type == "travel":
            lines.append("│   1. Set the road scene")
            lines.append("│   2. Encounter check or NPC conversation")
            lines.append("│   3. STOP for player decisions at each beat")
        elif scene_type == "shopping":
            lines.append("│   1. Describe the shop/vendor")
            lines.append("│   2. Merchant speaks first")
            lines.append("│   3. STOP — player decides what to buy/ask")
        elif scene_type == "combat":
            lines.append("│   1. Set the encounter (enemies, terrain)")
            lines.append("│   2. Roll initiative")
            lines.append("│   3. Present round — STOP for player action")
        lines.append("│ REMEMBER: Set scene, NPCs react, STOP.")
        lines.append(f"└{'────────────────────────────────────────'}┘")
        return "\n".join(lines)

    @classmethod
    def load_json(cls, path):
        """Load state from JSON. Supports both flat (kenji_state.json) and nested
        (character_world_state.json with _story_engine_state) formats."""
        import json
        from pathlib import Path
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            data.pop("_comment", None)
            # character_world_state.json nests engine state under _story_engine_state
            if "_story_engine_state" in data:
                engine_data = data["_story_engine_state"]
                engine_data.pop("_comment", None)
                engine_data.pop("_rule", None)
                data = engine_data
        eng = cls(data)
        print(f"[load] v{eng._save_version} saved {eng._saved_at or 'never'}")
        return eng

    def save_json(self, path):
        """Persist full state to JSON. Atomic write + verify to survive OneDrive sync."""
        import json, os
        from pathlib import Path
        from datetime import datetime
        self._save_version += 1
        self._saved_at = datetime.now().isoformat(timespec="seconds")
        if self.hegemony_active and self.construct_army:
            self._construct_total_expected = self.total_constructs()
        data = self.to_dict()
        tmp = Path(path).with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)
        # Verify
        check = json.loads(Path(path).read_text(encoding="utf-8"))
        if check.get("_save_version") != self._save_version:
            raise RuntimeError(
                f"SAVE VERIFY FAILED: wrote v{self._save_version}"
                f", read back v{check.get('_save_version')}"
                " — OneDrive likely overwrote the file"
            )

    def validate(self):
        """Check state consistency. Returns list of warnings (empty = clean)."""
        warnings = []
        # Construct army vs portals
        portal_names = set(self.portals.keys())
        army_names = set(self.construct_army.keys())
        orphan_armies = army_names - portal_names
        missing_armies = {n for n in portal_names if self.portals[n] == "active"} - army_names
        if orphan_armies:
            warnings.append(f"construct_army has entries not in portals: {orphan_armies}")
        if missing_armies:
            warnings.append(f"Active portals missing from construct_army: {missing_armies}")
        if self.hegemony_active:
            for portal, army in self.construct_army.items():
                for k in ("warrior", "healer", "mage", "ranger"):
                    if k not in army:
                        warnings.append(f"construct_army['{portal}'] missing key '{k}'")
        # Currency / HP
        if self.gold < 0:
            warnings.append(f"Gold is negative: {self.gold}")
        if self.meals < 0:
            warnings.append(f"Meals is negative: {self.meals}")
        if self.hp > self.max_hp:
            warnings.append(f"HP ({self.hp}) exceeds max HP ({self.max_hp})")
        if self.hp < 0:
            warnings.append(f"HP is negative: {self.hp}")
        # Threat clocks
        for name, clock in self.threat_clocks.items():
            for req in ("progress", "rate", "trigger", "description"):
                if req not in clock:
                    warnings.append(f"threat_clock['{name}'] missing key '{req}'")
        # Character goals
        for i, g in enumerate(self.character_goals):
            if not isinstance(g, dict):
                warnings.append(f"character_goals[{i}] is not an object")
                continue
            st = g.get("status", "").strip().lower()
            if st not in ACTIVE_CHARACTER_GOAL_STATUSES:
                continue
            due = g.get("due_day", None)
            if due is not None:
                try:
                    di = int(due)
                except (TypeError, ValueError):
                    warnings.append(f"character_goals[{i}] `{g.get('goal_id', '?')}` has non-int due_day")
                    continue
                if self.day > di:
                    warnings.append(
                        f"character_goals OVERDUE: {g.get('character', '?')}"
                        f" `{g.get('goal_id', '?')}` (engine day {self.day} > due_day {di})"
                    )
        # Construct total drift
        if self._construct_total_expected is not None:
            actual = self.total_constructs()
            if actual != self._construct_total_expected:
                warnings.append(
                    f"Construct total drifted: expected {self._construct_total_expected}"
                    f", actual {actual} (Δ{actual - self._construct_total_expected})"
                )
        return warnings

    def ai_brief_markdown(self):
        """Compact markdown for LLM-assisted DMing. Uses engine variables + narrative_notes.
        Does not replace the novels — use for facts-at-a-glance and dynamic continuity."""
        lines = []
        lines.append(f"# {self.char_name} — live state (StoryEngine / ttrpg_game_engine)")
        lines.append("")
        lines.append("Use these **numbers and facts** for the current session. For prose style, voice, and "
                      "secrets the party does not know, still follow `Kenji_story_book1.md` / `Kenji_story_book2.md` and `dm_rules_tracking.md` (spoiler sections).")
        lines.append(f"**Canon pointer:** {self.canon_pointer}")

        # Active arc
        aa = self.extra_json.get("active_arc")
        if isinstance(aa, dict):
            lines.append("")
            lines.append("## Active story arc (from kenji_state.json)")
            rel = aa.get("relative_path") or aa.get("path")
            slug = aa.get("slug")
            title = aa.get("title")
            if slug or title:
                lines.append(f"- **Slug:** {slug} | **Title:** {title}")
            if rel:
                lines.append(f"- **Arc file (relative to Game init files):** `{rel}`")
            else:
                lines.append(f"- **Arc path:** `{aa.get('path')}`")
            lines.append("- **Resolver:** run `python run_arc_pointer.py` from this folder for **KENJI_ARC_POINTER_RUN_RECEIPT** (machine proof) and optional `--peek N`.")

        # Where we left off
        if self.story_beat and str(self.story_beat).strip():
            lines.append("")
            lines.append("## Where we left off")
            lines.append(self.story_beat)

        # Time and place
        lines.append("")
        lines.append("## Time and place")
        hr = int(float(self.hour)) if self.hour else 0
        lines.append(f"- **Day {self.day},** hour {hr:02d}:00 — {self.time_of_day()}")
        lines.append(f"- **Location:** {self.location}")
        lines.append(f"- **Weather:** {self.weather}")

        # PC mechanical facts
        lines.append("")
        lines.append("## PC — mechanical facts")
        hp_str = f"{self.hp}/{self.max_hp}"
        if self.temp_hp:
            hp_str += f" (+{self.temp_hp} temp)"
        lines.append(f"- **{self.char_name},** level {self.level} — {self.exp:,} EXP")
        lines.append(f"- **HP** {hp_str}, **AC** {self.ac}")
        # Spell slots
        slot_parts = []
        for k, v in sorted(self.spell_slots.items(), key=lambda x: int(x[0])):
            slot_parts.append(f"L{k}:{v[0]}/{v[1]}")
        if slot_parts:
            lines.append(f"- **Spell slots:** {' '.join(slot_parts)}")
        lines.append(f"- **Wealth:** {self.gold} GP, {self.silver} SP, {self.copper} CP | **meals** {self.meals}")
        if self.weapon_config:
            lines.append(f"- **Weapon layout:** {self.weapon_config.upper()} — {self.weapon_config_detail}")
        else:
            lines.append(f"- **Weapon layout:** see `dm_rules_tracking.md` (Combat library section)")
        if self.active_perks:
            lines.append(f"- **Active perks:** {', '.join(self.active_perks)}")

        # Abilities / skills / spells
        if self.ability_scores or self.skills or self.known_spells or self.class_features:
            lines.append("")
            lines.append("## Abilities, skills, spells (sheet)")
            if self.ability_scores:
                order = ('STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA')
                row = []
                for k in order:
                    if k in self.ability_scores:
                        row.append(f" **{k}** {self.ability_scores[k]}")
                for k in sorted(self.ability_scores.keys()):
                    if k not in order:
                        row.append(f" **{k}** {self.ability_scores[k]}")
                lines.append(f"- **Ability scores:** {' · '.join(row)}")
            if self.skills:
                sk_parts = [f"{sk} {mod}" for sk, mod in sorted(self.skills.items())]
                lines.append(f"- **Skills:** {'; '.join(sk_parts)}")
            if self.known_spells:
                sp_names = [s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in self.known_spells]
                lines.append(f"- **Spells known:** {', '.join(sp_names)}")
            if self.class_features:
                cf_names = [f.get("name", str(f)) if isinstance(f, dict) else str(f) for f in self.class_features]
                lines.append(f"- **Class features:** {', '.join(cf_names)}")

        # Buffs
        if self.buffs:
            lines.append("")
            lines.append("## Buffs")
            for name, b in self.buffs.items():
                dur = b.get("duration_hrs") or b.get("duration", "?")
                eff = b.get("effects", "")
                lines.append(f"- **{name}** ({dur}): {eff}")

        # Charges
        if self.charges:
            lines.append("")
            lines.append("## Charges")
            for name, v in self.charges.items():
                lines.append(f"- {name}: {v[0]}/{v[1]}")

        # Portals
        lines.append("")
        lines.append("## Portals")
        active = [n for n, s in self.portals.items() if s == "active"]
        lines.append(f"{len(active)}/{self.portal_max} active: {', '.join(active)}")

        # Squads
        if self.squads:
            lines.append("")
            lines.append("## Squads")
            for name, s in self.squads.items():
                sline = f"- **{name}** ({s['captain']}) — {s['status']} @ {s['location']}"
                if s.get("mission"):
                    sline += f" — {s['mission']}"
                lines.append(sline)

        # Objectives
        if self.quests:
            lines.append("")
            lines.append("## Objectives")
            for q in self.quests:
                qline = f"- [{q['priority']}] {q['name']} ({q['status']})"
                if q.get("notes"):
                    qline += f" — {q['notes']}"
                lines.append(qline)

        # Threat clocks
        if self.threat_clocks:
            lines.append("")
            lines.append("## Threat clocks")
            for name, clock in self.threat_clocks.items():
                lines.append(f"- **{name}:** {clock['progress']}% (+{clock['rate']}%/day) — {clock.get('description', '')}")
                if clock["progress"] >= 50:
                    lines.append(f"  - Trigger: {clock['trigger']}")

        # Character goals
        if self.character_goals:
            lines.append("")
            lines.append("## Character goals (engine)")
            lines.append("Rows from `kenji_state.json` → `character_goals` (not parsed from `character_tracker.md`). "
                         "`process_new_day` / dawn pipeline runs `process_character_goals()` — set `auto_resolve` only when a row should mutate without DM hand-edit.")
            for g in self.character_goals:
                if not isinstance(g, dict):
                    continue
                char = g.get("character", "")
                gid = g.get("goal_id", "?")
                st = g.get("status", "")
                due = g.get("due_day", "—")
                pub = g.get("public_day", "—")
                auto = "auto" if g.get("auto_resolve") else "manual"
                summ = g.get("summary", "") or ""
                if len(summ) > 120:
                    summ = summ[:117] + "..."
                lines.append(f"- **{char}** `{gid}` — **{st}** | due_day **{due}** | public_day **{pub}** | {auto}")
                if summ:
                    lines.append(f"  - {summ}")
                hook = g.get("kenji_hook")
                if hook:
                    lines.append(f"  - Kenji impact: {hook}")

        # NPC positions
        if self.npcs:
            lines.append("")
            lines.append("## NPC positions (snapshot)")
            for name, n in self.npcs.items():
                nline = f"- **{name}:** {n['location']}"
                if n.get("activity"):
                    nline += f" — {n['activity']}"
                if n.get("disposition"):
                    nline += f" ({n['disposition']})"
                lines.append(nline)

        # Relationships
        rels = {n: r for n, r in self.relationships.items() if r["score"] != 0}
        if rels:
            lines.append("")
            lines.append("## Relationships (tracked)")
            for name, r in sorted(rels.items(), key=lambda x: x[1]["score"]):
                lines.append(f"- **{name}:** {r['tier']} ({r['score']:+d})")

        return "\n".join(str(x) for x in lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    if not args:
        # Default: run story tests, then combat tests
        eng = StoryEngine.load_json("kenji_state.json")
        print(eng.dashboard())
        warnings = eng.validate()
        if warnings:
            print("\n⚠️  Validation warnings:")
            for w in warnings:
                print(f"  - {w}")
        else:
            print("\n✅ State validation clean.")

    elif args[0] == "brief":
        path = args[1] if len(args) > 1 else "kenji_state.json"
        eng = StoryEngine.load_json(path)
        print(eng.ai_brief_markdown())

    elif args[0] == "skill":
        import argparse
        parser = argparse.ArgumentParser(prog="ttrpg_game_engine.py skill")
        parser.add_argument("modifier", type=int)
        parser.add_argument("--adv", action="store_true")
        parser.add_argument("--dis", action="store_true")
        parser.add_argument("--dc", type=int, default=None)
        parser.add_argument("--label", type=str, default="Skill check")
        parsed = parser.parse_args(args[1:])
        result = skill_roll(
            parsed.modifier,
            advantage=parsed.adv,
            disadvantage=parsed.dis,
            dc=parsed.dc,
            label=parsed.label,
        )
        print(json.dumps(result, indent=2))

    elif args[0] == "combat-only":
        print("Combat-only tests — see Combat class.")

    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: python ttrpg_game_engine.py [brief|skill|combat-only]")
