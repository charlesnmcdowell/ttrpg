#!/usr/bin/env python3
"""TTRPG Combat Engine v2 — Generic, Data-Driven. Load ANY character/monster from a dict."""

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
# VALIDATION — Run with: python3 combat_engine.py
# ============================================================
if __name__ == "__main__":
    print("=== COMBAT ENGINE VALIDATION ===")
    tests_passed = 0; tests_total = 0
    
    def check(name, condition):
        global tests_passed, tests_total
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
