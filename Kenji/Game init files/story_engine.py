#!/usr/bin/env python3
"""
TTRPG Story Engine — World State Tracker
Tracks everything the DM needs between combat: inventory, buffs, quests, squads, NPCs, economy, time.
DM updates state as play progresses, engine outputs formatted dashboard.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

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
        
        # ASSETS / INCOME
        self.assets = d.get("assets", [])
        # [{"name": "Mine", "income": "~8 GP/month", "status": "frozen — hearing pending"}]
        
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
        # {"Senna": {"score": -15, "tier": "cold", "history": [
        #     {"day": 17, "change": -30, "reason": "Portal-dumped 60 miles"},
        #     {"day": 18, "change": +15, "reason": "Professional combat cooperation"}]},
        #  "Thessaly": {"score": -5, "tier": "reluctant", "history": [
        #     {"day": 17, "change": -20, "reason": "Charmed in public"},
        #     {"day": 18, "change": +15, "reason": "Saved from Glass Stalker"}]}}
    
    # ---- TIME ----
    
    def time_of_day(self) -> str:
        if self.hour < 6: return "Night"
        elif self.hour < 8: return "Dawn"
        elif self.hour < 12: return "Morning"
        elif self.hour < 14: return "Midday"
        elif self.hour < 18: return "Afternoon"
        elif self.hour < 21: return "Evening"
        else: return "Night"
    
    def tick(self, hours: int = 1):
        """Advance time by N hours. Called after every player interaction in story mode."""
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
        """Jump to next morning (Long Rest)."""
        self.day += 1
        self.hour = 6
        self.hours_since_meal = 0
    
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
    
    def add_buff(self, name: str, duration: str, effects: str):
        self.buffs[name] = {"duration": duration, "effects": effects}
    
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
        from combat_engine import CR_EXP
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
            "hm_log": self.hm_log, "hm_total_today": self.hm_total_today,
            "noble_interest_active": self.noble_interest_active,
            "active_perks": self.active_perks,
            "weapon_config": self.weapon_config, "weapon_config_detail": self.weapon_config_detail,
            "threat_clocks": self.threat_clocks, "npc_agendas": self.npc_agendas,
            "org_plots": self.org_plots, "world_events": self.world_events,
            "consequences": self.consequences, "reputation": self.reputation,
            "relationships": self.relationships,
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
    
    def process_new_day(self):
        """Called at dawn each day. Advances ALL world systems."""
        results = []
        
        # Noble's Interest
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
        
        # World events check
        for event in self.world_events:
            if not event.get("fired") and event["day"] == self.day:
                event["fired"] = True
                results.append(f"🌍 WORLD EVENT: {event['event']} — {event.get('effect', '')}")
        
        # Consequences check
        for con in self.consequences:
            if not con.get("fired") and con["trigger_day"] <= self.day:
                con["fired"] = True
                results.append(f"⏰ CONSEQUENCE: {con['cause']} → {con['effect']}")
        
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
            lines.append(f"║ {'ASSETS & INCOME':<{w}}║")
            for a in self.assets:
                icon = "💰" if a["status"] == "active" else "❄️"
                aline = f"  {icon} {a['name']} — {a['income']} [{a['status']}]"
                lines.append(f"║ {aline:<{w}}║")
        
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
        lines.append(f"║ {'⚠️ DM RULES':<{w}}║")
        lines.append(f"║   Set scene → STOP → wait for player input.{' '*(w-45)}║")
        lines.append(f"║   1 interaction = 1 hour. Run dashboard EVERY response.{' '*(w-55)}║")
        lines.append(f"║   NPC AUTONOMY: Check motives before compliance.{' '*(w-50)}║")
        lines.append(f"║   CHA check if request conflicts with NPC personality.{' '*(w-55)}║")
        
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
        lines.append(f"│ Time: Day {self.day}, {self.time}")
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



# ============================================================
# VALIDATION — Run with: python3 story_engine.py
# ============================================================

if __name__ == "__main__":
    print("=== STORY ENGINE VALIDATION ===")
    tests_passed = 0; tests_total = 0
    
    def check(name, condition):
        global tests_passed, tests_total
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
