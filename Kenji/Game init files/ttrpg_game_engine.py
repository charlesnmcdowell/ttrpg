#!/usr/bin/env python3
"""TTRPG Game Engine — combat resolution plus world/story state (single module).

Combat: dice, Combatant, Combat, EXPTracker, load_combatant, etc.
Story: StoryEngine for kenji_state.json — time, economy, clocks, dashboards, AI brief.

CLI:
  python ttrpg_game_engine.py brief [optional/path/to/state.json]
  python ttrpg_game_engine.py              # story tests, then combat tests
  python ttrpg_game_engine.py combat-only  # combat tests only
"""

import random, json, math
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any

def d20(): return random.randint(1, 20)

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
        """Check which perks are active for a fighter. Returns active bonuses."""
        c = self.fighters[name]
        t = self.fighters.get(target)
        result = {"attack_bonus": 0, "heal_mult": 1.0, "crit_range_mod": 0, "active_perks": []}
        
        # Find allies (other fighters on same side — disposition friendly+)
        allies = [f for fname, f in self.fighters.items() 
                  if fname != name and f.alive and self.DISPOSITION_RANK.get(f.disposition, 0) >= 3]
        any_observers = [f for fname, f in self.fighters.items()
                        if fname != name and f.alive and self.DISPOSITION_RANK.get(f.disposition, 0) >= 0]
        
        for perk in c.perks:
            cond = perk.get("condition", "always")
            active = False
            
            if cond == "always": active = True
            elif cond == "friendly_observer": active = len(allies) > 0
            elif cond == "any_observer": active = len(any_observers) > 0
            elif cond == "target_charmed": active = t and t.has_status("charmed")
            
            if active:
                effect = perk.get("effect", "")
                val = perk.get("value", 0)
                result["active_perks"].append(perk["name"])
                
                if effect == "attack_bonus": result["attack_bonus"] += val
                elif effect == "heal_mult": result["heal_mult"] *= val
                elif effect == "crit_range_mod": result["crit_range_mod"] += val
        
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

    def attack(self, atk, tgt, bonus=0, adv=False, dis=False, auto_crit=False, ranged=False, range_ft=5):
        a, t = self.fighters[atk], self.fighters[tgt]
        # Range check (warn, don't block — DM may override)
        dist = self.distance_between(atk, tgt) if a.position != t.position else 5
        if ranged and dist > range_ft:
            self._log(f"  ⚠️ RANGE WARNING: {atk} is {dist}ft from {tgt}, weapon range {range_ft}ft")
        elif not ranged and dist > 5:
            self._log(f"  ⚠️ RANGE WARNING: {atk} is {dist}ft from {tgt} (melee = 5ft)")
        perks = self.check_perks(atk, tgt)
        perk_atk = perks["attack_bonus"]
        perk_crit = perks["crit_range_mod"]
        tb = a.attack_bonus + a.flat_attack_bonus + bonus + perk_atk
        effective_crit = a.crit_range - perk_crit  # lower = crits on more numbers
        nat = max(d20(),d20()) if adv else (min(d20(),d20()) if dis else d20())
        total = nat + tb; ic = auto_crit or nat >= effective_crit
        if t.has_status("stunned") or t.has_status("unconscious"): ic = True
        hits = ic or (nat != 1 and total >= t.ac)
        tag = "CRIT!" if ic else ("HIT" if hits else "MISS")
        perk_note = f" [+{perk_atk}PoF]" if perk_atk > 0 else ""
        crit_note = f" [crit {effective_crit}-20]" if perk_crit > 0 else ""
        self._log(f"{atk} → {tgt}: nat {nat}+{tb}={total} vs AC {t.ac} → {tag}{perk_note}{crit_note}")
        return {"nat":nat,"total":total,"bonus":tb,"crit":ic,"nat1":nat==1,"hits":hits,"tgt_ac":t.ac,"perks":perks}

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

    def heal(self, name, amount):
        c = self.fighters[name]; c.heal_hp(amount); self._log(f"  {name} heals {amount} → HP {c.hp}/{c.max_hp}")

    def add_temp(self, name, amount):
        c = self.fighters[name]; c.add_temp_hp(amount); self._log(f"  {name} +{amount}t → {c.temp_hp}t")

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
    
    # ---- TIME ----
    
    def time_of_day(self) -> str:
        if self.hour < 6: return "Night"
        elif self.hour < 8: return "Dawn"
        elif self.hour < 12: return "Morning"
        elif self.hour < 14: return "Midday"
        elif self.hour < 18: return "Afternoon"
        elif self.hour < 21: return "Evening"
        else: return "Night"
    
    def _advance_time(self, hours: int = 1):
        """Internal: advance time + expire buffs. Use tick_interaction() for the full pipeline."""
        self.hour += hours
        self.hours_since_meal += hours
        # Tick buff durations
        for name in list(self.buffs.keys()):
            b = self.buffs[name]
            dur = b.get("duration_hrs", -1)
            if dur > 0:
                b["duration_hrs"] = dur - hours
                if b["duration_hrs"] <= 0:
                    del self.buffs[name]
        # Day rollover
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
    
    def advance_day(self):
        """Jump to next morning (Long Rest). Runs the full daily pipeline."""
        self.day += 1
        self.hour = 6
        self.hours_since_meal = 0
        return self.process_new_day()
    
    def hours_until(self, target_day: int, target_hour: int = 6) -> int:
        """Hours until a target day+hour."""
        target_total = target_day * 24 + target_hour
        current_total = self.day * 24 + self.hour
        return max(0, target_total - current_total)
    
    def meal_status(self) -> str:
        if self.hours_since_meal >= 8: return "⚠️ STARVING (-disadv STR/CON/WIS, no short rest HP)"
        elif self.hours_since_meal >= 6: return "⚠️ HUNGRY (-1 STR/CON)"
        elif self.hours_since_meal >= 3: return f"🍖 {4 - self.hours_since_meal}hr until hungry"
        else: return "🍖 Fed"
    
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
    
    def remove_buff(self, name: str):
        self.buffs.pop(name, None)
    
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
    
    def tick_interaction(self) -> List[str]:
        """THE ONE METHOD TO CALL EVERY INTERACTION. Advances 1 hour, checks everything.
        Returns list of alerts the DM must narrate."""
        alerts = []
        
        # Advance 1 hour
        self.hour += 1
        if self.hour >= 24:
            self.hour = 0; self.day += 1
            day_results = self.process_new_day()
            alerts.extend(day_results)
        
        # Meal tracking
        self.hours_since_meal += 1
        meal_alert = self.check_meal()
        if meal_alert: alerts.append(meal_alert)
        
        # Buff expiry
        expired = self.check_expired_buffs()
        for name in expired:
            alerts.append(f"⏰ Buff expired: {name}")
        
        # Check world events this hour
        for event in self.world_events:
            if not event.get("fired") and event["day"] == self.day and event.get("hour", 0) <= self.hour:
                event["fired"] = True
                alerts.append(f"🌍 EVENT: {event['event']} — {event.get('effect', '')}")
        
        # Check consequences
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
            return f"🍖 HUNGER PENALTY ACTIVE — {self.hours_since_meal}hr since last meal. -1 to all checks."
        elif self.hours_since_meal >= self.meal_interval:
            return f"🍖 EAT NOW — {self.hours_since_meal}hr since last meal."
        return None
    
    def estimate_squad_hm(self, squad_name: str, kills_per_day: int = 2, avg_cr: int = 5) -> int:
        """Estimate daily Hearts & Minds EXP for a deployed squad. Auto-logs."""
        base_exp = CR_EXP.get(avg_cr, 1800)
        # Squad kills use duo multiplier (x2) since they work together
        daily_exp = kills_per_day * base_exp * 2
        self.log_hm_exp(squad_name, f"Est. {kills_per_day} kills CR{avg_cr}/day", daily_exp)
        return daily_exp
    
    def to_dict(self) -> dict:
        """Serialize entire state to dict. Use for save/load between sessions."""
        return {
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
        }
    
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
        self._normalize_army(self.construct_army[to_portal])
        
        if unit_type == "all":
            squads_to_move = min(count, army["squads"])
            for utype in ["warrior", "healer", "mage", "ranger"]:
                moved = squads_to_move
                army[utype] -= moved
                self.construct_army[to_portal][utype] += moved
            army["squads"] -= squads_to_move
            self.construct_army[to_portal]["squads"] += squads_to_move
        else:
            moved = min(count, army.get(unit_type, 0))
            army[unit_type] -= moved
            self.construct_army[to_portal][unit_type] += moved
        
        self.update_construct_fear()
        return f"Moved {count} {'squads' if unit_type == 'all' else unit_type} from {from_portal} to {to_portal}"
    
    def destroy_constructs(self, portal: str, count: int):
        """Record construct losses at a portal."""
        if portal not in self.construct_army: return
        army = self.construct_army[portal]
        self._normalize_army(army)
        per_type = max(1, count // 4)
        for utype in ["warrior", "healer", "mage", "ranger"]:
            lost = min(per_type, army[utype])
            army[utype] -= lost
            army["destroyed"] += lost
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
    
    # ---- DASHBOARD ----
    
    def dashboard(self) -> str:
        lines = []
        w = 60
        lines.append(f"╔{'═'*w}╗")
        time_str = f"Day {self.day}, Hour {self.hour:02d}:00 — {self.time_of_day()}"
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
                eline = f"  {urgency} [{e['priority']}] {e['name']} — Day {e['day']} ({time_str})"
                if e.get("notes"):
                    eline += f" — {e['notes']}"
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
        
        # Upcoming World Events (unfired, within 3 days)
        upcoming = [e for e in self.world_events if not e.get("fired") and e["day"] - self.day <= 3]
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
                    loser = b['b'] if b['winner'] == b['a'] else b['a']
                    bline = f"  ✅ B{b['bout']}: {b['winner']} def. {loser} ({b['rounds']}rds)"
                    lines.append(f"║ {bline:<{w}}║")
            # Show upcoming bouts (active vs active, not yet fought this stage)
            fought = set()
            for b in stage_bouts:
                fought.add(b['a']); fought.add(b['b'])
            unfought = [n for n in active_fighters if n not in fought]
            if len(unfought) >= 2:
                lines.append(f"║ {'  ⏳ UPCOMING:':<{w}}║")
                for i in range(0, len(unfought)-1, 2):
                    uline = f"    {unfought[i]} vs {unfought[i+1]}"
                    lines.append(f"║ {uline:<{w}}║")
        
        # Active Perks
        lines.append(f"╠{'─'*w}╣")
        if self.active_perks:
            perk_str = ", ".join(self.active_perks)
            lines.append(f"║ PERKS: {perk_str:<{w-7}}║")
        else:
            lines.append(f"║ PERKS: None active (no friendly observer){' '*(w-42)}║")
        
        # Weapon Config
        if self.weapon_config:
            lines.append(f"║ CONFIG: {self.weapon_config.upper()} — {self.weapon_config_detail:<{w-11-len(self.weapon_config)}}║")
        
        # DM RULES REMINDER — always present
        lines.append(f"╠{'─'*w}╣")
        lines.append(f"║ {'🚨 CARDINAL RULES':<{w}}║")
        lines.append(f"║   1. NEVER write Kenji's dialogue. STOP for player.{' '*(w-52)}║")
        lines.append(f"║   2. NEVER auto-resolve combat. Round-by-round ONLY.{' '*(w-53)}║")
        lines.append(f"║   3. STOP at every decision point. Present, don't decide.{' '*(w-58)}║")
        lines.append(f"║   4. 1 interaction = 1 hour. Dashboard EVERY response.{' '*(w-55)}║")
        lines.append(f"║   5. NPC AUTONOMY: Check motives before compliance.{' '*(w-52)}║")
        
        lines.append(f"╚{'═'*w}╝")
        return "\n".join(lines)
    
    def scene_prompt(self, scene_type: str = "arrival", npcs_present: List[str] = None) -> str:
        """Generate a DM scene prompt with player agency reminders.
        scene_type: arrival, combat, social, rest, travel, shopping
        npcs_present: list of NPC names in the scene
        """
        npcs = npcs_present or []
        lines = []
        lines.append(f"┌── SCENE: {scene_type.upper()} ──┐")
        lines.append(f"│ Location: {self.location}")
        lines.append(f"│ Time: Day {self.day}, {self.hour:02d}:00 — {self.time_of_day()}")
        if npcs:
            lines.append(f"│ NPCs present: {', '.join(npcs)}")
        
        lines.append(f"│")
        lines.append(f"│ DM WRITES:")
        lines.append(f"│   ✅ NPC dialogue (what THEY say)")
        lines.append(f"│   ✅ Environment (what player SEES, HEARS, SMELLS)")
        lines.append(f"│   ✅ NPC actions and reactions")
        lines.append(f"│   ✅ Consequences of player's stated actions")
        lines.append(f"│")
        lines.append(f"│ DM NEVER WRITES:")
        lines.append(f"│   ❌ Player dialogue (what Kenji SAYS)")
        lines.append(f"│   ❌ Player decisions (what Kenji CHOOSES to do)")
        lines.append(f"│   ❌ Player emotional reactions narrated as fact")
        lines.append(f"│   ❌ Player walking somewhere unprompted")
        lines.append(f"│")
        lines.append(f"│ SCENE FLOW:")
        
        if scene_type == "arrival":
            lines.append(f"│   1. Describe the location (one paragraph)")
            lines.append(f"│   2. NPCs react to player arriving")
            lines.append(f"│   3. First NPC speaks")
            lines.append(f"│   4. STOP — wait for player to respond")
        elif scene_type == "social":
            lines.append(f"│   1. NPC initiates or continues conversation")
            lines.append(f"│   2. STOP after NPC's line — let player respond")
            lines.append(f"│   3. Never run both sides of a conversation")
        elif scene_type == "rest":
            lines.append(f"│   1. Describe comfort (food, bath, bed) via NPC dialogue")
            lines.append(f"│   2. NPCs comment on the relief — they're people too")
            lines.append(f"│   3. STOP before Long Rest — ask player if anything before sleep")
        elif scene_type == "travel":
            lines.append(f"│   1. Set the road scene")
            lines.append(f"│   2. Encounter check or NPC conversation")
            lines.append(f"│   3. STOP for player decisions at each beat")
        elif scene_type == "shopping":
            lines.append(f"│   1. Describe the shop/vendor")
            lines.append(f"│   2. Merchant speaks first")
            lines.append(f"│   3. STOP — player decides what to buy/ask")
        elif scene_type == "combat":
            lines.append(f"│   1. Set the encounter (enemies, terrain)")
            lines.append(f"│   2. Roll initiative")
            lines.append(f"│   3. Present round — STOP for player action")
        
        lines.append(f"│")
        lines.append(f"│ REMEMBER: Set scene, NPCs react, STOP.")
        lines.append(f"└{'─'*40}┘")
        return "\n".join(lines)

    # ---- AI CONTEXT (compact — paste into chat; novels remain source of voice/tone) ----

    @classmethod
    def load_json(cls, path: str) -> "StoryEngine":
        """Load state from JSON (e.g. kenji_state.json). Strips optional _comment key."""
        import json
        from pathlib import Path
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            data.pop("_comment", None)
        return cls(data)

    def save_json(self, path: str) -> None:
        """Persist full state to JSON (same keys as to_dict())."""
        import json
        from pathlib import Path
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def validate(self) -> List[str]:
        """Check state consistency. Returns list of warnings (empty = clean)."""
        warnings = []
        portal_names = set(self.portals.keys())
        army_names = set(self.construct_army.keys())
        orphan_armies = army_names - portal_names
        if orphan_armies:
            warnings.append(f"construct_army has entries not in portals: {orphan_armies}")
        missing_armies = {p for p, s in self.portals.items() if s == "active"} - army_names
        if missing_armies and self.hegemony_active:
            warnings.append(f"Active portals missing from construct_army: {missing_armies}")
        for portal, army in self.construct_army.items():
            for k in ("squads", "warrior", "healer", "mage", "ranger", "destroyed"):
                if k not in army:
                    warnings.append(f"construct_army[{portal}] missing key '{k}'")
        if self.gold < 0:
            warnings.append(f"Gold is negative: {self.gold}")
        if self.meals < 0:
            warnings.append(f"Meals is negative: {self.meals}")
        if self.hp > self.max_hp:
            warnings.append(f"HP ({self.hp}) exceeds max HP ({self.max_hp})")
        if self.hp < 0:
            warnings.append(f"HP is negative: {self.hp}")
        for name, clock in self.threat_clocks.items():
            for req in ("progress", "rate", "trigger"):
                if req not in clock:
                    warnings.append(f"threat_clock[{name}] missing key '{req}'")
        return warnings

    def ai_brief_markdown(self) -> str:
        """Compact markdown for LLM-assisted DMing. Uses engine variables + narrative_notes.
        Does not replace the novels — use for facts-at-a-glance and dynamic continuity."""
        lines: List[str] = []
        lines.append("# Kenji — live state (StoryEngine / ttrpg_game_engine)")
        lines.append("")
        lines.append(
            "Use these **numbers and facts** for the current session. For prose style, voice, and "
        )
        lines.append(
            "secrets the party does not know, still follow `Kenji_story_book1.md` / `Kenji_story_book2.md` and `dm_rules_tracking.md` (spoiler sections)."
        )
        lines.append("")
        if self.canon_pointer:
            lines.append(f"**Canon pointer:** {self.canon_pointer}")
            lines.append("")
        if self.story_beat.strip():
            lines.append("## Where we left off")
            lines.append("")
            lines.append(self.story_beat.strip())
            lines.append("")
        lines.append("## Time and place")
        lines.append("")
        lines.append(
            f"- **Day {self.day},** hour {self.hour:02d}:00 — {self.time_of_day()}"
        )
        lines.append(f"- **Location:** {self.location}")
        lines.append(f"- **Weather:** {self.weather}")
        lines.append("")
        lines.append("## PC — mechanical facts")
        lines.append("")
        hp_str = f"{self.hp}/{self.max_hp}"
        if self.temp_hp:
            hp_str += f" (+{self.temp_hp} temp)"
        lines.append(
            f"- **{self.char_name},** level {self.level} — {self.exp:,} EXP"
        )
        lines.append(f"- **HP** {hp_str}, **AC** {self.ac}")
        if self.spell_slots:
            slot_parts = []
            for k, v in sorted(self.spell_slots.items(), key=lambda x: int(x[0])):
                slot_parts.append(f"L{k}:{v[0]}/{v[1]}")
            lines.append("- **Spell slots:** " + " ".join(slot_parts))
        lines.append(
            f"- **Wealth:** {self.gold} GP, {self.silver} SP, {self.copper} CP | **meals** {self.meals}"
        )
        if self.weapon_config:
            lines.append(
                f"- **Weapon layout:** {self.weapon_config.upper()} — {self.weapon_config_detail or 'see `dm_rules_tracking.md` (Combat library section)'}"
            )
        if self.active_perks:
            lines.append("- **Active perks:** " + ", ".join(self.active_perks))
        lines.append("")
        if self.buffs:
            lines.append("## Buffs")
            lines.append("")
            for name, b in self.buffs.items():
                dur = b.get("duration_hrs", b.get("duration", "?"))
                eff = b.get("effects", "")
                lines.append(f"- **{name}** ({dur}): {eff}")
            lines.append("")
        if self.charges:
            lines.append("## Charges")
            lines.append("")
            for n, v in self.charges.items():
                lines.append(f"- {n}: {v[0]}/{v[1]}")
            lines.append("")
        active = [n for n, s in self.portals.items() if s == "active"]
        if active:
            lines.append("## Portals")
            lines.append("")
            lines.append(
                f"- {len(active)}/{self.portal_max} active: {', '.join(active)}"
            )
            lines.append("")
        if self.squads:
            lines.append("## Squads")
            lines.append("")
            for name, s in self.squads.items():
                lines.append(
                    f"- **{name}** ({s.get('captain', '?')}): {s.get('status')} @ {s.get('location')} — {s.get('mission', '')}"
                )
            lines.append("")
        if self.quests:
            lines.append("## Objectives")
            lines.append("")
            for q in self.quests:
                lines.append(
                    f"- [{q.get('priority', '?')}] {q['name']} ({q.get('status', '')}) — {q.get('notes', '')}"
                )
            lines.append("")
        if self.threat_clocks:
            lines.append("## Threat clocks")
            lines.append("")
            for name, clock in sorted(
                self.threat_clocks.items(), key=lambda x: -x[1].get("progress", 0)
            ):
                lines.append(
                    f"- **{name}:** {clock.get('progress', 0)}% (+{clock.get('rate', 0)}%/day) — {clock.get('description', '')}"
                )
                if clock.get("progress", 0) >= 50:
                    lines.append(f"  - Trigger: {clock.get('trigger', '')}")
            lines.append("")
        if self.npcs:
            lines.append("## NPC positions (snapshot)")
            lines.append("")
            for name, n in self.npcs.items():
                lines.append(
                    f"- **{name}:** {n.get('location', '')} — {n.get('activity', '')} ({n.get('disposition', '')})"
                )
            lines.append("")
        rels = {n: r for n, r in self.relationships.items() if r.get("score", 0) != 0}
        if rels:
            lines.append("## Relationships (tracked)")
            lines.append("")
            for name, r in sorted(rels.items(), key=lambda x: x[1].get("score", 0)):
                lines.append(
                    f"- **{name}:** {r.get('tier', '?')} ({r.get('score', 0):+d})"
                )
            lines.append("")
        if self.hegemony_active and self.construct_army:
            lines.append("## Construct army")
            lines.append("")
            lines.append(f"- **Total constructs (approx):** {self.total_constructs()}")
            for portal, army in self.construct_army.items():
                ct = (
                    army.get("warrior", 0)
                    + army.get("healer", 0)
                    + army.get("mage", 0)
                    + army.get("ranger", 0)
                )
                if ct <= 0:
                    continue
                fear = self.construct_fear.get(portal, 0)
                lines.append(
                    f"- {portal}: {army.get('squads', 0)} squads, fear level {fear}"
                )
            lines.append("")
        pending = [c for c in self.consequences if not c.get("fired")]
        if pending:
            lines.append("## Pending consequences")
            lines.append("")
            for con in sorted(pending, key=lambda x: x.get("trigger_day", 0)):
                lines.append(
                    f"- Day {con.get('trigger_day')}: {con.get('cause', '')} -> {con.get('effect', '')}"
                )
            lines.append("")
        if self.narrative_notes:
            lines.append("## Narrative notes (edit in kenji_state.json)")
            lines.append("")
            for note in self.narrative_notes:
                lines.append(f"- {note}")
            lines.append("")
        lines.append("---")
        lines.append(
            "*Update by editing `kenji_state.json`, then `python ttrpg_game_engine.py brief`, or call `save_json()` after play.*"
        )
        return "\n".join(lines)


# ============================================================
# CLI — brief + self-tests
# ============================================================

def _run_combat_tests() -> None:
    tests_passed = 0; tests_total = 0

    def check(name, condition):
        nonlocal tests_passed, tests_total
        tests_total += 1
        if condition: tests_passed += 1; print(f"  ✅ {name}")
        else: print(f"  ❌ {name}")

    # 1. Basic load
    k = load_combatant({"name":"K","max_hp":93,"ac":18,"attack_bonus":10,"crit_range":18,
        "perks":[{"name":"PoF","effect":"attack_bonus","value":2,"condition":"friendly_observer"}],
        "weapon_config":"emberfrost","weapon_configs":{"emberfrost":{"ac":18,"max_attacks":4,"blocked":["Twin Fang"]}},
        "frost_fang_heal_pct":0.50,"perception_mod":5,"perception_adv":True})
    check("Load combatant", k.name == "K" and k.max_hp == 93)
    check("Weapon config AC", k.ac == 18)
    check("Max attacks from config", k.get_max_attacks() == 4)

    # 2. Vulnerability & immunity
    e = load_combatant({"name":"E","max_hp":100,"ac":15,
        "vulnerabilities":{"radiant":2.0},"immunities":["charm","poison"]})
    check("Vulnerability x2", e.apply_all_modifiers(20, "radiant") == 40)
    check("No vulnerability", e.apply_all_modifiers(20, "fire") == 20)
    check("Immunity blocks damage", e.apply_all_modifiers(20, "poison") == 0)
    check("Condition immunity", e.is_immune("charm") == True)

    # 3. Legendary resistance
    boss = load_combatant({"name":"B","max_hp":300,"ac":19,"legendary_resistances":3,
        "legendary_actions":3,"stats":{"str":4,"dex":2,"con":4,"int":5,"wis":4,"cha":2}})
    c = Combat(); c.add(boss,15); c.add(k,10); c.start()
    sv = c.save("B","dex",25)  # Impossible DC — should use legendary resistance
    check("Legendary resistance auto-triggers", sv["success"] == True)
    check("LR decremented", boss.legendary_resistances_remaining == 2)

    # 4. Phase transition
    phased = load_combatant({"name":"P","max_hp":200,"ac":16,
        "phases":[{"trigger_hp_pct":0.50,"new_ac":20,"description":"Phase 2"}]})
    phased.take_damage(110, "force")
    check("Phase triggered at 50%", phased.current_phase == 1 and phased.ac == 20)

    # 5. Death throes detection
    doomed = load_combatant({"name":"D","max_hp":50,"ac":12,
        "death_throes":{"type":"detonation","radius":15,"damage":"3d8","dtype":"fire","save_dc":14,"save_stat":"dex"}})
    doomed._death_throes_triggered = False
    doomed.take_damage(999, "force")
    check("Death throes flagged", doomed._death_throes_triggered == True)

    # 6. Squad AOE
    squad = load_combatant({"name":"S","max_hp":200,"ac":12,"is_squad":True,"squad_size":20,"individual_hp":10})
    kills = squad.squad_take_aoe(35)
    check("Squad AOE kills correct", kills == 3 and squad.squad_size == 17)

    # 7. Morale
    runner = load_combatant({"name":"R","max_hp":100,"ac":14,"morale_threshold":0.25})
    runner.hp = 20
    check("Morale break at threshold", runner.check_morale() == True)
    runner.hp = 30
    check("Morale holds above threshold", runner.check_morale() == False)

    # 8. Next turn skips dead
    c2 = Combat()
    alive = load_combatant({"name":"Alive","max_hp":50,"ac":12})
    dead = load_combatant({"name":"Dead","max_hp":50,"ac":12})
    dead.hp = 0; dead.alive = False
    c2.add(dead, 20); c2.add(alive, 10); c2.start()
    rnd, name = c2.next_turn()
    check("Skips dead combatant", name == "Alive")

    # 9. Zones
    c3 = Combat()
    c3.add(load_combatant({"name":"Z","max_hp":50,"ac":12,"position":30}), 10)
    c3.start()
    c3.add_zone("Acid", 25, 15, duration=2)
    zones = c3.check_zones("Z")
    check("Zone detection", len(zones) == 1 and zones[0]["name"] == "Acid")

    # 10. Inflict with immunity check
    c4 = Combat()
    immune = load_combatant({"name":"I","max_hp":50,"ac":12,"immunities":["stunned"]})
    c4.add(immune, 10); c4.start()
    result = c4.inflict("I", "stunned")
    check("Inflict blocked by immunity", result == False)
    result = c4.inflict("I", "prone")
    check("Inflict succeeds when not immune", result == True)

    print(f"\n{'='*40}")
    print(f"RESULT: {tests_passed}/{tests_total} tests passed")
    if tests_passed == tests_total:
        print("ALL SYSTEMS OPERATIONAL ✅")
    else:
        print(f"⚠️ {tests_total - tests_passed} FAILURES")


def _run_story_tests() -> None:
    print("=== STORY ENGINE VALIDATION ===")
    tests_passed = 0; tests_total = 0

    def check(name, condition):
        nonlocal tests_passed, tests_total
        tests_total += 1
        if condition: tests_passed += 1; print(f"  ✅ {name}")
        else: print(f"  ❌ {name}")

    e = StoryEngine({"day": 18, "hour": 20, "hours_since_meal": 3, "meals": 41,
        "char_name": "Kenji", "level": 15, "exp": 257235,
        "hp": 93, "max_hp": 93, "ac": 18, "gold": 8, "silver": 83,
        "buffs": {"God Sight": {"duration_hrs": 26}, "Haste": {"duration_hrs": 1}},
        "portals": {"Varenholm": "active", "Thornwall": "active"}, "portal_max": 8,
        "events": [{"name": "Tournament", "day": 21, "priority": "HIGH"}],
        "quests": [{"name": "Gate", "status": "active", "priority": "HIGH"}],
        "threat_clocks": {"Gate": {"progress": 40, "rate": 8, "trigger": "Gate opens", "description": "test"}},
        "relationships": {"Senna": {"score": -25, "tier": "cold", "history": []}},
        "world_events": [{"day": 19, "hour": 8, "event": "Reinforcements", "effect": "20 sentinels", "fired": False}],
        "consequences": [{"trigger_day": 20, "cause": "Portal built", "effect": "Patrol sent", "fired": False}],
        "org_plots": {"Council": {"plot": "Restrict ArchMagus", "progress": 25, "rate": 5, "next_move": "Subpoena", "next_move_day": 22}},
        "npc_agendas": {"Garrett": {"goal": "Win hearing", "progress": 60, "deadline_day": 21}},
        "reputation": {"Academy": {"level": "ArchMagus", "opinion": "respected"}},
        "noble_interest_active": True,
    })

    # 1. Basic load
    check("Load engine", e.char_name == "Kenji" and e.day == 18)
    check("Time of day", e.time_of_day() == "Evening")
    check("Hours until event", e.hours_until(21) > 0)

    # 2. Meal check
    meal = e.check_meal()
    # 3hr is within 4hr interval, no warning yet. Test at 4hr:
    e.hours_since_meal = 4
    meal = e.check_meal()
    check("Meal warning fires at 4hr", meal is not None and "EAT" in meal)

    # 3. Buff expiry
    expired = e.check_expired_buffs()
    check("Haste expires (1hr → 0)", "Haste" in expired)
    check("God Sight survives (26→25)", "God Sight" not in expired and "God Sight" in e.buffs)

    # 4. Relationship
    e.update_relationship("Senna", 10, "Cooperated")
    check("Relationship score updated", e.relationships["Senna"]["score"] == -15)
    e.update_relationship("Senna", 30, "Saved squad")
    check("Tier advances to friendly", e.relationships["Senna"]["tier"] == "friendly")

    # 5. Threat clock
    e.advance_threat("Gate", 20)
    check("Threat advanced", e.threat_clocks["Gate"]["progress"] == 60)

    # 6. Noble's Interest
    check("Projected gold > current", e.projected_gold() > e.gold)

    # 7. Consequence
    e.add_consequence(19, "Test", "Effect")
    check("Consequence added", len(e.consequences) == 2)

    # 8. process_new_day
    e.day = 19; e.hour = 6
    results = e.process_new_day()
    check("process_new_day runs", len(results) > 0)
    check("Threat clock advanced by rate", e.threat_clocks["Gate"]["progress"] > 60)

    # 9. Serialization
    state = e.to_dict()
    check("to_dict works", isinstance(state, dict) and state["char_name"] == "Kenji")
    e2 = StoryEngine(state)
    check("Round-trip load", e2.day == e.day and e2.exp == e.exp)

    # 10. tick_interaction
    e3 = StoryEngine({"day": 18, "hour": 23, "hours_since_meal": 0, "meals": 10,
        "buffs": {"Test": {"duration_hrs": 1}},
        "world_events": [{"day": 19, "hour": 0, "event": "Dawn", "effect": "test", "fired": False}]})
    alerts = e3.tick_interaction()
    check("tick advances hour + day rollover", e3.hour == 0 and e3.day == 19)
    check("tick fires world events", any("Dawn" in a for a in alerts))
    check("tick expires buffs", "Test" not in e3.buffs)

    # 11. Dashboard
    dash = e.dashboard()
    check("Dashboard generates", len(dash) > 200)
    check("Dashboard has threat clocks", "THREAT" in dash)
    check("Dashboard has relationships", "RELATIONSHIP" in dash)
    check("Dashboard has faction plots", "FACTION" in dash)
    check("Dashboard has reputation", "REPUTATION" in dash)

    print(f"\n{'='*40}")
    print(f"RESULT: {tests_passed}/{tests_total} tests passed")
    if tests_passed == tests_total:
        print("ALL SYSTEMS OPERATIONAL ✅")
    else:
        print(f"⚠️ {tests_total - tests_passed} FAILURES")


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "brief":
        from pathlib import Path
        root = Path(__file__).resolve().parent
        state_path = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "kenji_state.json"
        if not state_path.is_file():
            print(
                f"Missing {state_path}. Copy kenji_state.example.json to kenji_state.json first.",
                file=sys.stderr,
            )
            sys.exit(1)
        eng = StoryEngine.load_json(str(state_path))
        text = eng.ai_brief_markdown()
        out_file = state_path.with_name("AI_CONTEXT.md")
        out_file.write_text(text, encoding="utf-8")
        print(text)
        print(f"\n[Wrote {out_file}]", file=sys.stderr)
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "combat-only":
        _run_combat_tests()
        raise SystemExit(0)

    _run_story_tests()
    print()
    _run_combat_tests()
