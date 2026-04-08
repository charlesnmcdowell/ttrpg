# ⚔️ COMBAT LIBRARY — Engine-Ready Definitions
# Copy dict → paste into load_combatant() → fight.
# Add new entries as encountered. Update after level-ups/scaling.

---

## KENJI — Level 12 Blade Channeler
```python
KENJI = {
    "name": "Kenji",
    "max_hp": 93, "ac": 22, "base_ac": 18,
    "stats": {"str": 3, "dex": 3, "con": 1, "int": -1, "wis": 0, "cha": 5},
    "proficiency": 5, "attack_bonus": 10, "flat_attack_bonus": 0,  # NO hardcoded PoF — perks handle it
    "spell_attack": 10, "spell_save_dc": 18, "crit_range": 18,
    "speed": 90, "base_speed": 90, "initiative_mod": 3,
    "spell_slots": {"1": [5,5], "2": [3,3], "3": [3,3], "4": [3,3], "5": [3,3], "6": [1,1]},
    "frost_fang_heal_pct": 0.50,
    "thrown_damage_mult": 1.5, "thrown_range_mult": 3, "thrown_range_bonus": 60,
    "counter_throw_available": True, "counter_throw_cooldown_max": 2,
    "concentration_save_mod": 1,
    # Weapon configs — SET weapon_config at load time based on current state
    "weapon_config": "separated",  # DEFAULT: separated blades. Change to "emberfrost" when combined.
    "weapon_configs": {
        "emberfrost": {"ac": 18, "max_attacks": 4,
            "blocked": ["Twin Fang", "Enhanced Cage", "Cross-Guard"]},
        "separated": {"ac": 22, "max_attacks": 5,
            "blocked": ["Cyclone", "Horizon Arc"]},
    },
    # Perception — God Sight grants advantage
    "perception_mod": 5, "perception_adv": True,
    "perks": [
        {"name": "Power of Friendship", "effect": "attack_bonus", "value": 2, "condition": "friendly_observer"},
        {"name": "Attention Whore", "effect": "heal_mult", "value": 1.5, "condition": "friendly_observer"},
        {"name": "Emotional Damage", "effect": "crit_range_mod", "value": 3, "condition": "target_charmed"},
    ],
    "notes": "AC22=cross-guard(two weapons). AC18=base. Frost Fang heals 50% total dmg per hit. Fast Metabolism doubles all healing. Emberfang: 1d8+2 slash + 1d6 fire + ignite. Frost Fang: 1d8+5 cold + 10%maxHP necrotic + slow-10ft. Enhanced Edge: +1d4 force.",
    "abilities": [
        {"name": "Blade Ward", "action_type": "reaction", "is_reaction": True,
         "cost_type": "charge", "max_charges": 3, "charges": 3,
         "description": "Halve physical portion of one hit."},
        {"name": "Enhanced Cage", "action_type": "reaction", "is_reaction": True,
         "cost_type": "charge", "max_charges": 3, "charges": 3,
         "requires_melee": True, "requires_two_weapons": True,
         "description": "Counter on enemy MELEE miss. 1/enemy turn max."},
        {"name": "Ember Lance", "action_type": "action",
         "cost_type": "charge", "max_charges": 5, "charges": 5,
         "damage": "2d8", "damage_type": "radiant",
         "description": "60ft. Heals allies. Burns abyssal (2x). Damages entropy."},
        {"name": "Ignite", "action_type": "free",
         "cost_type": "charge", "max_charges": 3, "charges": 3,
         "damage": "2d6", "damage_type": "fire",
         "description": "Melee only. +2d6 fire + burn 1d6/rd."},
        {"name": "Thunder Strike", "action_type": "on_hit",
         "cost_type": "spell_slot", "slot_level": 1, "save_stat": "con", "save_dc": 15,
         "description": "On HIT expend slot. L1:2d6 prone. L2:3d6+10ft. L3:4d6+20ft. L4:5d6+30ft+stun. Misses cost nothing."},
        {"name": "Enhanced Arcane Edge", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 1,
         "description": "1min. L1=1wep, L2=2wep. +1d4 force/hit. Kills trigger Arcane Momentum."},
        {"name": "Arcane Stride", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 1,
         "description": "12hr. L1=60, L2=90, L3=120, L4=150, L5=180ft. Extra action: 1 weapon attack."},
        {"name": "Duality Aspect", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 3,
         "description": "1hr. Flight 4x speed. 60ft AOE: Entropy 1d6 necrotic or Creation 1d6 heal. No extra action."},
        {"name": "Ward Mastery", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 3,
         "description": "1hr. Halve nonmagical physical. Element: L3=-4, L4=-7, L5=-10 per hit."},
        {"name": "Charm Creature", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 1,
         "save_stat": "wis", "save_dc": 18,
         "description": "WIS save DISADVANTAGE. L1=1hr L2=4hr L3=8hr L4=24hr. Charmed=crit range 15-20."},
        {"name": "Haste", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 4,
         "description": "6hr. CONCENTRATION (CON save on damage, DC 10 or half dmg). +2 extra attacks/round. +30ft move. Stacks with everything. Fail concentration = gone.",
         "extra": {"extra_attacks": 2, "move_bonus": 30, "concentration": True, "max_attacks_with_stride_twin": 5}},
        {"name": "Giant's Throw", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 6,
         "description": "24hr. 3x throw range. +50% thrown damage. Counter Throw reaction: throw on enemy miss, 2rd cooldown. Stacks with everything.",
         "extra": {"range_mult": 3, "damage_mult": 1.5, "counter_throw_cooldown": 2}},
    ],
}
```

**DM NOTES — Kenji combat modifiers:**
- Cross-Guard (+4 AC) requires two weapons. Emberfrost = one weapon = no cross-guard.
- Power of Friendship (+2 attack) requires friendly observer. Remove if solo.
- Frost Fang heal = 25% of total damage × 2 (Metabolism) = 50%. Overflow → temp HP (cap = max HP).
- Emberfang: 1d8+2 slash + 1d6 fire. Passive Ignite CON DC 15 or burn 1d6/rd.
- Emberfrost combined: both blade damages per hit. No cross-guard/cage. Cyclone 30ft returning. Horizon Arc 30ft AOE 1/combat.
- Somnus Knife: 0 doses remaining. Bittershade: 0 doses remaining.
- **Spell Save DC now 18 (proficiency +5 at Level 15).**
- **Haste max attack economy: Twin Fang 2 + Stride 1 + Haste 2 = 5 attacks/round. Concentration is the price.**
- **Giant's Throw + God Sight: thrown range 240/360ft. Counter Throw = free ranged attack on enemy miss (2rd CD).**
- **Full buff stack (pre-combat at ley line): God Sight + Stride + Haste + Edge + Frost Fang + Giant's Throw = all legal simultaneously. Haste requires concentration tracking.**
- **Cyclone IS a thrown weapon. Giant's Throw applies: range (30+60 God Sight) × 3 = 270ft. Damage × 1.5. Counter Throw works with Cyclone.**

---

## SENNA — The Ashen Fist (Azarinth Healer)
```python
SENNA = {
    "name": "Senna",
    "max_hp": 198, "ac": 13,  # post-encounter 1 scaling: 180 × 1.10
    "stats": {"str": 3, "dex": 1, "con": 1, "int": 4, "wis": -1, "cha": -1},
    "proficiency": 5, "attack_bonus": 8,
    "speed": 60, "base_speed": 60, "initiative_mod": 1,
    "ki": 25, "ki_max": 25,
    "has_progressive_resistance": True,
    "resistances": {
        "necrotic": {"exposures": 8, "rate": 0.10},
        "cold": {"exposures": 4, "rate": 0.10},
        "fire": {"exposures": 0, "rate": 0.10},
        "lightning": {"exposures": 0, "rate": 0.10},
        "acid": {"exposures": 0, "rate": 0.10},
        "thunder": {"exposures": 0, "rate": 0.10},
        "poison": {"exposures": 1, "rate": 0.25},
        "mental": {"exposures": 1, "rate": 0.50},
    },
    "regen_percent": 0.50,
    "heal_or_purge": True,
    "encounter_scaling": {"hp": 0.10, "dmg": 0.05},
    "encounters": 1,
    "tags": ["hot-headed", "competitive", "loves-food", "holds-grudges"],
    "notes": "Regen 50% maxHP/turn OR purge 1 status. NOT both. Ki Intrusion: 2d8+3 bludgeon + 3d8 force per strike (1 Ki each). 2 strikes/action. Easy to hit (AC 13). Hard to kill (regen). One-shot kills are the threat. Resistances carry over between encounters within 24hrs. 'I'll Come Back Stronger': if she loses+retreats, 72hr later returns 2x HP 2x damage.",
    "abilities": [
        {"name": "Ki Intrusion", "action_type": "action",
         "cost_type": "ki", "cost_amount": 1,
         "damage": "2d8+3", "damage_type": "bludgeoning",
         "description": "Unarmed. +3d8 force (bypasses armor). 1 Ki/strike. 2 strikes/action.",
         "extra": {"force_dice": "3d8", "attacks_per_action": 2}},
        {"name": "Blink Step", "action_type": "reaction", "is_reaction": True,
         "cooldown": 2,
         "description": "20ft teleport. Dodge one attack. Through objects (not magic barriers). 2rd CD after use."},
        {"name": "Ash Wings", "action_type": "bonus_action",
         "cost_type": "ki", "cost_amount": 2,
         "description": "Flight 60ft. 1 Ki/rd to maintain."},
        {"name": "Ash Shield", "action_type": "reaction", "is_reaction": True,
         "cost_type": "ki", "cost_amount": 2,
         "description": "+4 AC vs one attack OR +2 AC vs all attacks until next turn."},
        {"name": "Ash Cloud", "action_type": "action",
         "cost_type": "ki", "cost_amount": 3,
         "save_stat": "con", "save_dc": 16,
         "description": "15ft radius blind. 1 round."},
    ],
}
```

**DM NOTES — Senna combat behavior:**
1. Opens aggressive. Charges biggest threat. Ki Intrusion immediately.
2. Takes hits (AC 13). Regen handles sustained damage.
3. Blink Step to dodge the ONE scary attack per 3 rounds (crits, Thunder Strike).
4. Ash Wings if enemy has no ranged. Dive-bomb.
5. Ash Cloud to blind clusters, then punches blind targets.
6. MORE aggressive as fight continues (INT 18 adapting).
7. Retreats if she'll die. Comes back stronger in 72hrs.
8. Each encounter adds +10% HP, +5% damage permanently. Track encounters.

**SCALING TRACKER:**
- Encounters: 1 (Kenji spar). HP: 180→198. Dmg: +5%.
- Resistances carried: necrotic 80%, cold 40%, poison 25%, mental 50%.
- Next encounter: HP becomes 217 (198×1.10). Dmg: +10%.

---

## THESSALY — Wardbreakers Arcanist
```python
THESSALY = {
    "name": "Thessaly",
    "max_hp": 47, "ac": 14,
    "stats": {"str": -1, "dex": 1, "con": 0, "int": 4, "wis": 2, "cha": -1},
    "proficiency": 4, "attack_bonus": 7,
    "spell_attack": 7, "spell_save_dc": 15,
    "speed": 30, "base_speed": 30, "initiative_mod": 2,
    "spell_slots": {"1": [4,4], "2": [3,3], "3": [2,2]},
    "disposition": "hostile",  # UPDATE AT LOAD TIME based on story state
    "notes": "Glass cannon. 9yr Academy grad. Crystal-focus staff. Hostile disposition toward Kenji. Ward specialist. Will NOT fight dirty — Academy rules. Forfeits if outmatched rather than risk injury. Book is her shield.",
    "abilities": [
        {"name": "Arcane Bolt", "action_type": "action",
         "damage": "1d10+4", "damage_type": "force",
         "description": "3 bolts per action. Spell attack +7 each. 1d10+4 force per bolt.",
         "extra": {"bolts": 3}},
        {"name": "Crystal Beam", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 2,
         "damage": "4d8", "damage_type": "force",
         "save_stat": "dex", "save_dc": 15,
         "description": "Focused beam. DEX DC 15. Full on fail, half on save."},
        {"name": "Ward Barrier", "action_type": "reaction", "is_reaction": True,
         "cost_type": "spell_slot", "slot_level": 1,
         "description": "Reduce incoming damage by 1d10+4."},
        {"name": "Force Wall", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 2,
         "description": "10ft transparent barrier. Blocks movement and projectiles. 1 min."},
        {"name": "Dispel", "action_type": "action",
         "cost_type": "spell_slot", "slot_level": 3,
         "description": "Remove one magical effect. Can target buffs on enemies or debuffs on allies."},
        {"name": "Arcane Shield", "action_type": "reaction", "is_reaction": True,
         "description": "+3 AC vs one attack. No slot cost. 1/round.",
         "extra": {"ac_bonus": 3}},
    ],
}
```

**DM NOTES — Thessaly combat behavior:**
1. Stays at range. Always. 30ft+ if possible.
2. Opens with Arcane Bolt x3. Tests defenses.
3. If bolts can't penetrate AC, switches to Crystal Beam (save-based, ignores AC).
4. Force Wall to create distance if enemy closes.
5. Ward Barrier reaction on big incoming hits.
6. Dispel if enemy has visible buffs she can identify (Arcana INT +8).
7. Will NOT take a beating. Forfeits before she drops below 50% HP in a spar.
8. In real combat (not spar): much more vicious. Uses terrain, combo spells, targets weaknesses.

---

## 📦 FUTURE ENTRIES — Add as encountered
Template for new entries:
```python
NEW_COMBATANT = {
    "name": "",
    "max_hp": 0, "ac": 0,
    "stats": {"str": 0, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 0},
    "proficiency": 0, "attack_bonus": 0,
    "speed": 30, "initiative_mod": 0,
    # Optional:
    # "spell_slots": {"1": [0,0]},
    # "ki": 0, "ki_max": 0,
    # "has_progressive_resistance": False,
    # "resistances": {"fire": {"exposures": 0, "rate": 0.10}},
    # "regen_percent": 0.0, "heal_or_purge": False,
    "abilities": [],
}
```

### PENDING — To be added on encounter:
- Finch (Wardbreakers scout, halfling rogue)
- Varn (Wardbreakers fighter, half-orc greatshield)
- Sera (Darkblades captain, combat mage)
- Dren Valdric (Lord of Ironholt, CR 17/19)
- Kex (Psi Drake familiar, CR 8)
- Mordecai Corven (Gatekeeper, CR 18)
- Greave (Iron Coliseum Champion, CR 15)
- Tournament opponents (CR 5-12 ladder)
- Ironholt soldiers and inner circle

---

## 🔴 ENCOUNTERED — Bleakmoor Abyssal Creatures

### Glass Sentinel — CR 7
```python
GLASS_SENTINEL = {
    "name": "Glass Sentinel", "max_hp": 95, "ac": 16,
    "stats": {"str": 3, "dex": 1, "con": 3, "int": -2, "wis": 0, "cha": -3},
    "proficiency": 3, "attack_bonus": 7, "speed": 30, "initiative_mod": 1,
    "notes": "Abyssal construct. Immune charm/fear/poison. Necrotic RESIST. Radiant VULNERABLE (fire x2). Patrols relay nodes.",
    "abilities": [
        {"name": "Glass Strike", "damage": "2d8+3", "damage_type": "slashing",
         "description": "Melee. +1d6 acid (dissolution). Two attacks per action."},
        {"name": "Dissolution Pulse", "cost_type": "charge", "max_charges": 1, "charges": 1,
         "save_stat": "con", "save_dc": 15, "damage": "3d8", "damage_type": "acid",
         "description": "15ft radius. CON DC 15. Recharge 5-6."},
    ],
}
```

### Gate Warden — CR 11
```python
GATE_WARDEN = {
    "name": "Gate Warden", "max_hp": 175, "ac": 17,
    "stats": {"str": 4, "dex": 1, "con": 4, "int": 2, "wis": 3, "cha": -3},
    "proficiency": 4, "attack_bonus": 9, "speed": 0, "initiative_mod": 1,
    "notes": "Seated at gate base. Void-shaped. Immune charm/fear/poison. Necrotic RESIST. Radiant VULNERABLE. Does not move until gate threatened.",
    "abilities": [
        {"name": "Void Grasp", "damage": "3d10+4", "damage_type": "force",
         "description": "30ft range. Pulls target 15ft toward gate. Two grasps per action."},
        {"name": "Gate Pulse", "cost_type": "charge", "max_charges": 2, "charges": 2,
         "save_stat": "con", "save_dc": 17, "damage": "4d10", "damage_type": "necrotic",
         "description": "30ft cone from gate. CON DC 17. Last resort."},
        {"name": "Dissolution Field", "action_type": "passive",
         "description": "15ft radius around gate. 1d8 acid at start of creatures' turns."},
    ],
}
```

### Void Weaver — CR 9
```python
VOID_WEAVER = {
    "name": "Void Weaver", "max_hp": 85, "ac": 15,
    "stats": {"str": -1, "dex": 2, "con": 1, "int": 3, "wis": 2, "cha": -2},
    "proficiency": 4, "attack_bonus": 7, "spell_attack": 7,
    "speed": 30, "initiative_mod": 2,
    "notes": "COUNTER-KENJI DESIGN: Phase dodges melee, Unravel strips buffs, multi-hit forces concentration, Web denies Stride. Immune charm/fear/poison.",
    "abilities": [
        {"name": "Void Bolt", "damage": "2d8+4", "damage_type": "force",
         "description": "60ft. 2 bolts/action. Each forces concentration check.", "extra": {"bolts": 2}},
        {"name": "Unravel", "save_stat": "int", "save_dc": 16,
         "description": "30ft. INT DC 16. FAIL: strip one active buff."},
        {"name": "Phase Shift", "action_type": "reaction", "is_reaction": True, "cooldown": 1,
         "description": "Teleport 15ft. Dodge one melee attack. 1rd CD."},
        {"name": "Dissolution Web", "action_type": "bonus_action", "cost_type": "charge", "max_charges": 2, "charges": 2,
         "description": "15ft square difficult terrain + 1d6 acid/turn. 3 rounds."},
    ],
}
```

### Glass Stalker — CR 10
```python
GLASS_STALKER = {
    "name": "Glass Stalker", "max_hp": 110, "ac": 17,
    "stats": {"str": 4, "dex": 4, "con": 2, "int": 1, "wis": 2, "cha": -3},
    "proficiency": 4, "attack_bonus": 9, "speed": 40, "initiative_mod": 4,
    "stealth_mod": 8, "stealth_adv": True,
    "notes": "COUNTER-AOE DESIGN: Invisible ceiling ambush. Grabs squishies as shields. Anti-caster assassin. Immune charm/fear/poison. Radiant breaks invisibility. Use ambush_check() before combat.",
    "abilities": [
        {"name": "Impale", "damage": "3d8+4", "damage_type": "piercing",
         "description": "Melee. From stealth = auto-crit. Grapple on hit.",
         "extra": {"grapple_on_hit": True, "auto_crit_from_stealth": True}},
        {"name": "Glass Skin", "action_type": "passive",
         "description": "Invisible while stationary. ADV stealth. Radiant breaks for 1 round."},
        {"name": "Drag", "action_type": "bonus_action",
         "description": "Grappled target dragged 15ft. STR contest."},
        {"name": "Shatter Burst", "action_type": "reaction", "is_reaction": True,
         "cost_type": "charge", "max_charges": 1, "charges": 1,
         "save_stat": "con", "save_dc": 16, "damage": "3d6", "damage_type": "piercing",
         "description": "When hit: explodes 10ft. CON DC 16. Reforms next turn."},
    ],
}
```
**DM NOTES — Glass Stalker behavior:**
1. Always targets the squishiest party member first. NOT Kenji.
2. Uses grappled target as cover against ranged attacks (+5 AC effective).
3. Drags grappled target up walls/ceilings to deny melee reach.
4. Shatter Burst is a reaction — punishes the first hit, damages nearby allies.
5. After Shatter Burst, reforms invisible next round if not hit by radiant.
6. **ALWAYS run ambush_check() before this encounter. God Sight advantage applies.**
