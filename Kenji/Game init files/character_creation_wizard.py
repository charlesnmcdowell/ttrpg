#!/usr/bin/env python3
"""character_creation_wizard.py — 9-step Character Creation Wizard for the
Kenji DM Tool dashboard.

Walks the player through the canonical character creation process from
dm_rules_tracking.md § Character Creation Rules:

  1. Race            — fixed list + Custom (player describes)
  2. Class           — fixed list + Custom (player describes)
  3. Gender          — Male / Female / Non-binary / Custom
  4. Background      — free-text, player writes their own
  5. Name            — text input + AI-Suggest button (5 names)
  6. Appearance      — 7 fields (height/build, hair, eyes, skin,
                       distinguishing marks, style vibe, reference image path)
  7. Stats           — point-buy, total ≤ 72, no stat below 1
  8. Starting gear   — class-appropriate options
  9. Narrator style  — 7 LitRPG author voices

Each step has its own screen with Back / Next buttons. AI Suggest buttons
appear on relevant steps (Class, Background, Name, Appearance) and use the
Claude API when ANTHROPIC_API_KEY (or ttrpg_key.txt) is available; gracefully
disabled with a tooltip when no key is configured.

On finalize (step 9 Next button = "Create Character"), the pipeline runs
on a background thread (UI stays responsive):
  1. Up-front validation: name non-empty, no Windows-illegal chars, no
     existing folder/manifest collision (refuse to overwrite).
  2. In-process call to generate_starter_campaign.generate_campaign_scaffold
     (no subprocess - works in bundled .exe). Appearance, narrator_style
     (as the {author/series/voice} dict the template expects), and
     ability_scores all go into player_input under canonical keys.
  3. character_compute.recompute_character_state - derives HP / AC / saves
     from chosen stats and mirrors them into _story_engine_state.
  4. Starting gear merged into _story_engine_state.equipped (canonical
     inventory key - same one the play engine reads).
  5. Manifest written to dist/manifests/ override path (so bundled .exe
     picks up the new character without a rebuild).
  6. Voice slot added to tts_config.json (case-insensitive duplicate check).
  7. Success dialog -> user closes wizard -> re-launches dashboard from
     desktop shortcut and picks the new character from the picker.

See WIZARD_PHASE_2D_AUDIT.md for the full audit + fix history.
"""
from __future__ import annotations
import json
import os
import sys
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import customtkinter as ctk
from tkinter import messagebox

# Match the dashboard's color theme (kenji_gui.py constants)
BG_DARK   = "#1a1a2e"
BG_PANEL  = "#16213e"
BG_CARD   = "#0f3460"
GOLD      = "#c9a959"
GOLD_DIM  = "#8a7340"
TEXT      = "#e8e0d4"
TEXT_DIM  = "#9e9585"
RED       = "#c0392b"
GREEN     = "#27ae60"

FONT_HEADER = ("Segoe UI", 22, "bold")
FONT_STEP   = ("Segoe UI", 14, "bold")
FONT_LABEL  = ("Segoe UI", 12, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 10)


# === Fixed option catalogues (per Q2 answer: fixed list + Custom override) ===

RACES = [
    "Human", "Elf", "Half-Elf", "Dwarf", "Halfling", "Half-Orc",
    "Tiefling", "Gnome", "Dragonborn", "Ankuspawn", "Custom",
]

CLASSES = [
    "Fighter", "Barbarian", "Monk", "Paladin", "Ranger", "Rogue",
    "Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard", "Custom",
]

GENDERS = ["Male", "Female", "Non-binary", "Custom"]

REGIONS = ["Frontier", "Heartland", "Coast", "Mountains", "Underground", "Surface"]

# Per dm_rules_tracking.md § Character Creation #9 — narrator-style options
NARRATOR_STYLES = {
    "Aleron Kong (The Land)":
        "Irreverent, funny, detailed mechanics woven into prose, pop culture nods, "
        "narrator has personality and attitude. Father of American LitRPG voice.",
    "Travis Bagwell (Awaken Online)":
        "Dark, psychological, morally grey. Consequence-driven narration. "
        "Combat is visceral. The world pushes back hard.",
    "Luke Chmilenko (Ascend Online)":
        "Adventure-forward, party dynamics, exploration and wonder. "
        "World-building is lush. The narrator loves the setting.",
    "Dakota Krout (Divine Dungeon / Completionist)":
        "Whimsical, system-heavy, dry humor. Progression is the dopamine hit. "
        "The narrator geeks out over numbers and edge cases.",
    "Andrew Rowe (Arcane Ascension)":
        "Academic, analytical, mystery-driven. Hard magic systems explained cleanly. "
        "The narrator is a scholar who happens to tell stories.",
    "Shirtaloon (He Who Fights with Monsters)":
        "Witty banter, escalating stakes, strong party dynamics. The narrator is "
        "funny but knows when to get serious. Australian-flavored irreverence.",
    "Custom / Blend":
        "Player describes the tone they want. DM matches it.",
}

# Class → starting gear catalog (5e standard, simplified)
STARTING_GEAR = {
    "Fighter":   ["Chain mail", "Longsword + shield", "Crossbow + 20 bolts", "Explorer's pack", "10 GP"],
    "Barbarian": ["Greataxe", "Two handaxes", "Explorer's pack", "Four javelins", "10 GP"],
    "Monk":      ["Quarterstaff", "10 darts", "Dungeoneer's pack", "Plain robes", "5 GP"],
    "Paladin":   ["Chain mail", "Longsword + shield", "Holy symbol", "Priest's pack", "10 GP"],
    "Ranger":    ["Studded leather", "Two shortswords", "Longbow + 20 arrows", "Explorer's pack", "10 GP"],
    "Rogue":     ["Leather armor", "Shortsword + dagger", "Thieves' tools", "Burglar's pack", "10 GP"],
    "Wizard":    ["Spellbook", "Quarterstaff", "Component pouch", "Scholar's pack", "Robes", "10 GP"],
    "Sorcerer":  ["Light crossbow + 20 bolts", "Two daggers", "Component pouch", "Dungeoneer's pack", "10 GP"],
    "Warlock":   ["Light crossbow + 20 bolts", "Simple weapon", "Component pouch", "Scholar's pack", "10 GP"],
    "Cleric":    ["Mace", "Scale mail + shield", "Light crossbow + 20 bolts", "Holy symbol", "Priest's pack", "10 GP"],
    "Druid":     ["Wooden shield", "Scimitar", "Leather armor", "Druidic focus", "Explorer's pack", "10 GP"],
    "Bard":      ["Rapier", "Diplomat's pack", "Lute", "Leather armor", "Dagger", "10 GP"],
    "Custom":    ["Player + DM negotiate at table"],
}


# === API key detection (mirrors play_engine.py logic) ===

def _has_api_key() -> bool:
    """Check ANTHROPIC_API_KEY env var or ttrpg_key.txt next to this file."""
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        return True
    key_file = Path(__file__).resolve().parent / "ttrpg_key.txt"
    if key_file.exists():
        try:
            return bool(key_file.read_text(encoding="utf-8").strip())
        except Exception:
            return False
    return False


def _get_api_key() -> str:
    """Return the API key from env or ttrpg_key.txt, or empty string."""
    env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        return env_key
    key_file = Path(__file__).resolve().parent / "ttrpg_key.txt"
    if key_file.exists():
        try:
            return key_file.read_text(encoding="utf-8").strip()
        except Exception:
            return ""
    return ""


def _ai_suggest(prompt: str, on_complete: Callable[[str], None],
                on_error: Callable[[str], None]) -> None:
    """Fire a quick Claude request in a background thread, deliver the text
    via on_complete callback. Used by Suggest buttons throughout the wizard.
    Single-shot, no streaming."""
    def worker():
        try:
            import anthropic  # type: ignore
            client = anthropic.Anthropic(api_key=_get_api_key())
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",  # fast cheap model for suggestions
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(block.text for block in resp.content if hasattr(block, "text"))
            on_complete(text.strip())
        except Exception as e:
            on_error(f"{type(e).__name__}: {e}")
    threading.Thread(target=worker, daemon=True).start()


# === Wizard window ===

class CharacterCreationWizard(ctk.CTk):
    """9-step character creation flow. One screen per step. Back/Next nav.
    Validation gates each step. AI Suggest helpers where they fit the rules."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Kenji DM Tool — Character Creation")
        self.geometry("780x720")
        self.configure(fg_color=BG_DARK)

        # Accumulator for all collected data
        self.data: Dict = {
            "name": "",
            "gender": "",
            "race": "",
            "race_custom": "",  # populated only if race == "Custom"
            "class_concept": "",
            "class_custom": "",  # populated only if class == "Custom"
            "background": "",
            "personal_goal": "",
            "starting_region_preference": "frontier",
            "appearance": {
                "height_build": "",
                "hair": "",
                "eyes": "",
                "skin": "",
                "distinguishing_marks": "",
                "style_vibe": "",
                "reference_image": "",
            },
            "stats": {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10},
            "starting_gear": [],
            "narrator_style": "Aleron Kong (The Land)",
        }

        self.step_index = 0
        self.total_steps = 9
        self.has_api = _has_api_key()

        self._build_chrome()
        self._render_current_step()

    # ---- Chrome (header + nav buttons that persist across all steps) ----

    def _build_chrome(self):
        """Build the persistent header (title + step indicator) and footer
        (Back / Next buttons)."""
        # Header
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=80)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Character Creation", font=FONT_HEADER,
                     text_color=GOLD).pack(side="left", padx=24, pady=14)

        self.lbl_step = ctk.CTkLabel(header, text="", font=FONT_STEP,
                                      text_color=TEXT)
        self.lbl_step.pack(side="right", padx=24)

        if not self.has_api:
            ctk.CTkLabel(header,
                         text="⚠ No API key — Suggest buttons disabled",
                         font=FONT_SMALL, text_color=RED).pack(side="right", padx=12)

        # Footer (Back / Next + Cancel)
        footer = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=70)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        self.btn_cancel = ctk.CTkButton(footer, text="Cancel", width=100, height=38,
                                         fg_color=BG_CARD, hover_color=RED,
                                         font=FONT_LABEL, text_color=TEXT,
                                         command=self._on_cancel)
        self.btn_cancel.pack(side="left", padx=20, pady=14)

        self.btn_next = ctk.CTkButton(footer, text="Next →", width=140, height=38,
                                       fg_color=GOLD_DIM, hover_color=GOLD,
                                       font=FONT_LABEL, text_color=BG_DARK,
                                       command=self._on_next)
        self.btn_next.pack(side="right", padx=20, pady=14)

        self.btn_back = ctk.CTkButton(footer, text="← Back", width=100, height=38,
                                       fg_color=BG_CARD, hover_color=GOLD_DIM,
                                       font=FONT_LABEL, text_color=TEXT,
                                       command=self._on_back)
        self.btn_back.pack(side="right", padx=8, pady=14)

        # Body container — each step replaces the contents
        self.body = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.body.pack(side="top", fill="both", expand=True, padx=20, pady=10)

    def _clear_body(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    # ---- Navigation ----

    def _render_current_step(self):
        """Dispatch to the right step renderer + update header step counter +
        update Back/Next button labels."""
        renderers = [
            self._render_step_race,        # 1
            self._render_step_class,       # 2
            self._render_step_gender,      # 3
            self._render_step_background,  # 4
            self._render_step_name,        # 5
            self._render_step_appearance,  # 6
            self._render_step_stats,       # 7
            self._render_step_gear,        # 8
            self._render_step_narrator,    # 9
        ]
        self._clear_body()
        renderers[self.step_index]()
        self.lbl_step.configure(text=f"Step {self.step_index + 1} of {self.total_steps}")
        self.btn_back.configure(state="disabled" if self.step_index == 0 else "normal")
        if self.step_index == self.total_steps - 1:
            self.btn_next.configure(text="Create Character →", fg_color=GREEN)
        else:
            self.btn_next.configure(text="Next →", fg_color=GOLD_DIM)

    def _on_back(self):
        if self.step_index > 0:
            self._collect_current_step()
            self.step_index -= 1
            self._render_current_step()

    def _on_next(self):
        ok, msg = self._validate_current_step()
        if not ok:
            messagebox.showwarning("Cannot continue", msg, parent=self)
            return
        self._collect_current_step()
        if self.step_index == self.total_steps - 1:
            self._on_finalize()
        else:
            self.step_index += 1
            self._render_current_step()

    def _on_cancel(self):
        if messagebox.askyesno("Cancel character creation?",
                                "Discard everything and exit the wizard?", parent=self):
            self.destroy()

    def _collect_current_step(self):
        """Pull the current step's widget values back into self.data.
        Each step renderer wires its widgets to self._w_<step> attributes
        so this method can read them."""
        idx = self.step_index
        if idx == 0:
            self.data["race"] = self._w_race.get()
            if self.data["race"] == "Custom":
                self.data["race_custom"] = self._w_race_custom.get("0.0", "end").strip()
        elif idx == 1:
            self.data["class_concept"] = self._w_class.get()
            if self.data["class_concept"] == "Custom":
                self.data["class_custom"] = self._w_class_custom.get("0.0", "end").strip()
        elif idx == 2:
            g = self._w_gender.get()
            if g == "Custom":
                self.data["gender"] = self._w_gender_custom.get().strip()
            else:
                self.data["gender"] = g
        elif idx == 3:
            self.data["background"] = self._w_bg.get("0.0", "end").strip()
            self.data["personal_goal"] = self._w_goal.get("0.0", "end").strip()
            self.data["starting_region_preference"] = self._w_region.get().lower()
        elif idx == 4:
            self.data["name"] = self._w_name.get().strip()
        elif idx == 5:
            self.data["appearance"]["height_build"] = self._w_app["height_build"].get().strip()
            self.data["appearance"]["hair"] = self._w_app["hair"].get().strip()
            self.data["appearance"]["eyes"] = self._w_app["eyes"].get().strip()
            self.data["appearance"]["skin"] = self._w_app["skin"].get().strip()
            self.data["appearance"]["distinguishing_marks"] = self._w_app["distinguishing_marks"].get("0.0", "end").strip()
            self.data["appearance"]["style_vibe"] = self._w_app["style_vibe"].get("0.0", "end").strip()
            self.data["appearance"]["reference_image"] = self._w_app["reference_image"].get().strip()
        elif idx == 6:
            try:
                for k in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
                    self.data["stats"][k] = int(self._w_stats[k].get())
            except (ValueError, TypeError):
                pass
        elif idx == 7:
            self.data["starting_gear"] = [
                item for item, var in self._w_gear.items() if var.get()
            ]
        elif idx == 8:
            self.data["narrator_style"] = self._w_narrator.get()

    def _validate_current_step(self) -> Tuple[bool, str]:
        """Per-step validation. Returns (ok, error_message)."""
        idx = self.step_index
        if idx == 0:
            race = self._w_race.get()
            if not race:
                return False, "Pick a race."
            if race == "Custom":
                desc = self._w_race_custom.get("0.0", "end").strip()
                if len(desc) < 20:
                    return False, "Custom race needs at least a couple sentences describing how it functions and its physical features."
        elif idx == 1:
            cls = self._w_class.get()
            if not cls:
                return False, "Pick a class."
            if cls == "Custom":
                desc = self._w_class_custom.get("0.0", "end").strip()
                if len(desc) < 20:
                    return False, "Custom class needs at least a couple sentences describing its abilities and concept."
        elif idx == 2:
            g = self._w_gender.get()
            if not g:
                return False, "Pick a gender."
            if g == "Custom" and not self._w_gender_custom.get().strip():
                return False, "Custom gender needs a value."
        elif idx == 3:
            bg = self._w_bg.get("0.0", "end").strip()
            goal = self._w_goal.get("0.0", "end").strip()
            if len(bg) < 50:
                return False, "Background needs at least a couple sentences. Per house rule: the player writes their own background — the AI doesn't generate it for you. (Use Suggest only as a brainstorming spark.)"
            if len(goal) < 10:
                return False, "Personal goal needs at least one sentence — what does this character actually want?"
        elif idx == 4:
            name = self._w_name.get().strip()
            if not name:
                return False, "Enter a name (or click Suggest to generate options)."
            if len(name) < 2:
                return False, "Name needs at least 2 characters."
        elif idx == 5:
            for field, label in (("height_build", "Height/build"), ("hair", "Hair"),
                                  ("eyes", "Eyes"), ("skin", "Skin")):
                if not self._w_app[field].get().strip():
                    return False, f"{label} field is required."
        elif idx == 6:
            try:
                stats = {k: int(self._w_stats[k].get()) for k in ("STR","DEX","CON","INT","WIS","CHA")}
            except (ValueError, TypeError):
                return False, "Each stat must be a whole number."
            if any(v < 1 for v in stats.values()):
                return False, "No stat can be below 1."
            if any(v > 18 for v in stats.values()):
                return False, "Max base stat at creation is 18 (racial bonuses applied later)."
            total = sum(stats.values())
            if total > 72:
                return False, f"Total base stats must be ≤ 72. You have {total} (over by {total - 72})."
        elif idx == 7:
            pass  # gear is optional
        elif idx == 8:
            if not self._w_narrator.get():
                return False, "Pick a narrator style."
        return True, ""

    # ---- Step 1: Race ----

    def _render_step_race(self):
        ctk.CTkLabel(self.body, text="Race", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Pick a race. Custom lets you describe a homebrew lineage in your own words.",
                     font=FONT_BODY, text_color=TEXT_DIM).pack(anchor="w", pady=(0, 16))

        self._w_race = ctk.StringVar(value=self.data["race"] or "Human")
        grid = ctk.CTkFrame(self.body, fg_color="transparent")
        grid.pack(anchor="w", fill="x")
        for i, r in enumerate(RACES):
            ctk.CTkRadioButton(grid, text=r, variable=self._w_race, value=r,
                                font=FONT_BODY, text_color=TEXT,
                                fg_color=GOLD, command=self._toggle_race_custom).grid(
                row=i // 4, column=i % 4, sticky="w", padx=12, pady=6)

        # Custom textarea — visible only when Custom is picked
        self._w_race_custom_frame = ctk.CTkFrame(self.body, fg_color=BG_PANEL,
                                                   corner_radius=8)
        ctk.CTkLabel(self._w_race_custom_frame,
                     text="Describe your custom race — how it functions, physical features, anything that makes it distinctive:",
                     font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=12, pady=(8, 4))
        self._w_race_custom = ctk.CTkTextbox(self._w_race_custom_frame, height=140,
                                               fg_color=BG_CARD, text_color=TEXT,
                                               font=FONT_BODY)
        self._w_race_custom.pack(fill="x", padx=12, pady=(0, 10))
        if self.data.get("race_custom"):
            self._w_race_custom.insert("0.0", self.data["race_custom"])

        self._toggle_race_custom()

    def _toggle_race_custom(self):
        if self._w_race.get() == "Custom":
            self._w_race_custom_frame.pack(fill="x", pady=(20, 0))
        else:
            self._w_race_custom_frame.pack_forget()

    # ---- Step 2: Class ----

    def _render_step_class(self):
        ctk.CTkLabel(self.body, text="Class", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Pick a class. Custom lets you build a homebrew kit in your own words.",
                     font=FONT_BODY, text_color=TEXT_DIM).pack(anchor="w", pady=(0, 16))

        self._w_class = ctk.StringVar(value=self.data.get("class_concept") or "Fighter")
        grid = ctk.CTkFrame(self.body, fg_color="transparent")
        grid.pack(anchor="w", fill="x")
        for i, c in enumerate(CLASSES):
            ctk.CTkRadioButton(grid, text=c, variable=self._w_class, value=c,
                                font=FONT_BODY, text_color=TEXT,
                                fg_color=GOLD, command=self._toggle_class_custom).grid(
                row=i // 4, column=i % 4, sticky="w", padx=12, pady=6)

        self._w_class_custom_frame = ctk.CTkFrame(self.body, fg_color=BG_PANEL,
                                                    corner_radius=8)
        ctk.CTkLabel(self._w_class_custom_frame,
                     text="Describe your custom class — its abilities, concept, what makes it distinct:",
                     font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=12, pady=(8, 4))
        self._w_class_custom = ctk.CTkTextbox(self._w_class_custom_frame, height=140,
                                                fg_color=BG_CARD, text_color=TEXT,
                                                font=FONT_BODY)
        self._w_class_custom.pack(fill="x", padx=12, pady=(0, 10))
        if self.data.get("class_custom"):
            self._w_class_custom.insert("0.0", self.data["class_custom"])

        self._toggle_class_custom()

    def _toggle_class_custom(self):
        if self._w_class.get() == "Custom":
            self._w_class_custom_frame.pack(fill="x", pady=(20, 0))
        else:
            self._w_class_custom_frame.pack_forget()

    # ---- Step 3: Gender ----

    def _render_step_gender(self):
        ctk.CTkLabel(self.body, text="Gender", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Pick your character's gender. The DM uses this for all narration, pronouns, and NPC reactions.",
                     font=FONT_BODY, text_color=TEXT_DIM).pack(anchor="w", pady=(0, 16))

        current = self.data.get("gender", "Male")
        # Map a custom gender back to "Custom" radio selection
        radio_value = current if current in GENDERS else "Custom"
        custom_text = "" if current in GENDERS else current

        self._w_gender = ctk.StringVar(value=radio_value)
        grid = ctk.CTkFrame(self.body, fg_color="transparent")
        grid.pack(anchor="w")
        for i, g in enumerate(GENDERS):
            ctk.CTkRadioButton(grid, text=g, variable=self._w_gender, value=g,
                                font=FONT_BODY, text_color=TEXT,
                                fg_color=GOLD, command=self._toggle_gender_custom).grid(
                row=0, column=i, sticky="w", padx=16, pady=8)

        self._w_gender_custom_frame = ctk.CTkFrame(self.body, fg_color=BG_PANEL,
                                                     corner_radius=8)
        ctk.CTkLabel(self._w_gender_custom_frame, text="Custom gender:",
                     font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=12, pady=(8, 4))
        self._w_gender_custom = ctk.CTkEntry(self._w_gender_custom_frame,
                                               fg_color=BG_CARD, text_color=TEXT,
                                               font=FONT_BODY, height=36)
        self._w_gender_custom.pack(fill="x", padx=12, pady=(0, 10))
        if custom_text:
            self._w_gender_custom.insert(0, custom_text)

        self._toggle_gender_custom()

    def _toggle_gender_custom(self):
        if self._w_gender.get() == "Custom":
            self._w_gender_custom_frame.pack(fill="x", pady=(20, 0))
        else:
            self._w_gender_custom_frame.pack_forget()

    # ---- Step 4: Background ----

    def _render_step_background(self):
        ctk.CTkLabel(self.body, text="Background & Goal", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Write your character's background in your OWN words. The DM never generates this for you "
                          "— Suggest is only a brainstorming spark.",
                     font=FONT_BODY, text_color=TEXT_DIM, wraplength=720,
                     justify="left").pack(anchor="w", pady=(0, 12))

        # Region picker
        region_row = ctk.CTkFrame(self.body, fg_color="transparent")
        region_row.pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(region_row, text="Starting region:", font=FONT_LABEL,
                     text_color=GOLD).pack(side="left", padx=(0, 12))
        self._w_region = ctk.CTkComboBox(region_row, values=REGIONS, width=180,
                                           font=FONT_BODY, fg_color=BG_CARD,
                                           text_color=TEXT, dropdown_fg_color=BG_PANEL,
                                           button_color=GOLD_DIM, button_hover_color=GOLD)
        self._w_region.pack(side="left")
        self._w_region.set(self.data.get("starting_region_preference", "frontier").capitalize())

        # Background textarea + Suggest button
        bg_label_row = ctk.CTkFrame(self.body, fg_color="transparent")
        bg_label_row.pack(anchor="w", fill="x", pady=(12, 4))
        ctk.CTkLabel(bg_label_row, text="Background (where they grew up, what shaped them, who they lost):",
                     font=FONT_LABEL, text_color=GOLD).pack(side="left")
        self._suggest_button(bg_label_row, "Suggest", self._suggest_background)

        self._w_bg = ctk.CTkTextbox(self.body, height=140, fg_color=BG_CARD,
                                      text_color=TEXT, font=FONT_BODY)
        self._w_bg.pack(fill="x", pady=(0, 12))
        if self.data.get("background"):
            self._w_bg.insert("0.0", self.data["background"])

        # Personal goal
        ctk.CTkLabel(self.body, text="Personal goal — what they actually want (one sentence):",
                     font=FONT_LABEL, text_color=GOLD).pack(anchor="w", pady=(8, 4))
        self._w_goal = ctk.CTkTextbox(self.body, height=70, fg_color=BG_CARD,
                                        text_color=TEXT, font=FONT_BODY)
        self._w_goal.pack(fill="x")
        if self.data.get("personal_goal"):
            self._w_goal.insert("0.0", self.data["personal_goal"])

    def _suggest_background(self):
        race = self.data.get("race") or self._w_race.get() if hasattr(self, "_w_race") else self.data.get("race")
        cls = self.data.get("class_concept")
        gender = self.data.get("gender")
        prompt = (f"Suggest a 2-paragraph evocative background for a {gender} {race} {cls} "
                  f"in a fantasy LitRPG world. Specific, grounded — give them a place they grew up, "
                  f"a person they lost or owe, something that shaped them. No clichés. "
                  f"This is brainstorming material — the player will rewrite it in their own voice.")
        self._show_suggest_loading(self._w_bg)
        _ai_suggest(prompt,
                     on_complete=lambda txt: self.after(0, lambda: self._fill_textbox(self._w_bg, txt)),
                     on_error=lambda err: self.after(0, lambda: self._suggest_error(self._w_bg, err)))

    # ---- Step 5: Name ----

    def _render_step_name(self):
        ctk.CTkLabel(self.body, text="Name", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Enter your character's name. Click Suggest to generate 5 options matching their race + class.",
                     font=FONT_BODY, text_color=TEXT_DIM).pack(anchor="w", pady=(0, 16))

        row = ctk.CTkFrame(self.body, fg_color="transparent")
        row.pack(anchor="w", fill="x")
        ctk.CTkLabel(row, text="Name:", font=FONT_LABEL, text_color=GOLD).pack(side="left", padx=(0, 12))
        self._w_name = ctk.CTkEntry(row, width=400, height=38, fg_color=BG_CARD,
                                      text_color=TEXT, font=FONT_BODY)
        self._w_name.pack(side="left", padx=(0, 12))
        if self.data.get("name"):
            self._w_name.insert(0, self.data["name"])
        self._suggest_button(row, "Suggest 5", self._suggest_names)

        # Suggestion display area
        ctk.CTkLabel(self.body, text="Suggestions appear below. Click any line to use it.",
                     font=FONT_SMALL, text_color=TEXT_DIM).pack(anchor="w", pady=(20, 4))
        self._w_name_suggestions = ctk.CTkTextbox(self.body, height=180, fg_color=BG_CARD,
                                                    text_color=TEXT, font=FONT_BODY)
        self._w_name_suggestions.pack(fill="x")
        # Click-to-fill behavior
        self._w_name_suggestions.bind("<Button-1>", self._click_name_suggestion)

    def _suggest_names(self):
        race = self.data.get("race")
        cls = self.data.get("class_concept")
        gender = self.data.get("gender")
        if self.data.get("race") == "Custom":
            race = f"Custom race ({self.data.get('race_custom', '')[:80]})"
        if self.data.get("class_concept") == "Custom":
            cls = f"Custom class ({self.data.get('class_custom', '')[:80]})"
        prompt = (f"Generate 5 name suggestions for a {gender} {race} {cls} in a fantasy world. "
                  f"Each on its own line. Format: 'Firstname Lastname — one-line vibe note'. "
                  f"Vary the styles — some names should feel ancient, some practical, some elegant. "
                  f"No bullet points, no numbering, just one name per line with the vibe note.")
        self._show_suggest_loading(self._w_name_suggestions)
        _ai_suggest(prompt,
                     on_complete=lambda txt: self.after(0, lambda: self._fill_textbox(self._w_name_suggestions, txt)),
                     on_error=lambda err: self.after(0, lambda: self._suggest_error(self._w_name_suggestions, err)))

    def _click_name_suggestion(self, event):
        try:
            idx = self._w_name_suggestions.index(f"@{event.x},{event.y}")
            line_idx = idx.split('.')[0]
            line = self._w_name_suggestions.get(f"{line_idx}.0", f"{line_idx}.end").strip()
            if line and not line.startswith("⏳") and not line.startswith("⚠"):
                # Take just the name part (before first " — " or " - ")
                for sep in (" — ", " – ", " - ", ":"):
                    if sep in line:
                        line = line.split(sep, 1)[0].strip()
                        break
                # Strip leading numbers/bullets if present
                line = line.lstrip("0123456789.•-* ").strip()
                self._w_name.delete(0, "end")
                self._w_name.insert(0, line)
        except Exception:
            pass

    # ---- Step 6: Appearance ----

    def _render_step_appearance(self):
        ctk.CTkLabel(self.body, text="Appearance", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        row = ctk.CTkFrame(self.body, fg_color="transparent")
        row.pack(anchor="w", fill="x")
        ctk.CTkLabel(row, text="Describe your character's physical look. Suggest fills all fields from race/class/gender.",
                     font=FONT_BODY, text_color=TEXT_DIM).pack(side="left")
        self._suggest_button(row, "Suggest", self._suggest_appearance)

        scroll = ctk.CTkScrollableFrame(self.body, fg_color="transparent",
                                          height=460)
        scroll.pack(fill="both", expand=True, pady=(12, 0))

        self._w_app: Dict[str, ctk.CTkBaseClass] = {}
        fields_one_line = [
            ("height_build", "Height & build", "tall, slender / short, stocky / etc."),
            ("hair", "Hair", "color, length, style"),
            ("eyes", "Eyes", "color (Ankuspawn: gold-flecked)"),
            ("skin", "Skin", "tone / texture"),
            ("reference_image", "Reference image (optional path)", "filename or full path to art reference"),
        ]
        for key, label, hint in fields_one_line:
            ctk.CTkLabel(scroll, text=label, font=FONT_LABEL,
                          text_color=GOLD).pack(anchor="w", pady=(8, 2))
            entry = ctk.CTkEntry(scroll, fg_color=BG_CARD, text_color=TEXT,
                                   font=FONT_BODY, height=34, placeholder_text=hint)
            entry.pack(fill="x", pady=(0, 4))
            if self.data["appearance"].get(key):
                entry.insert(0, self.data["appearance"][key])
            self._w_app[key] = entry

        # Multi-line fields
        for key, label, hint in [
            ("distinguishing_marks", "Distinguishing marks (optional)",
             "scars, tattoos, birthmarks, unusual features"),
            ("style_vibe", "Style / vibe (optional)",
             "how they dress, how they carry themselves"),
        ]:
            ctk.CTkLabel(scroll, text=label, font=FONT_LABEL,
                          text_color=GOLD).pack(anchor="w", pady=(8, 2))
            tb = ctk.CTkTextbox(scroll, height=80, fg_color=BG_CARD,
                                  text_color=TEXT, font=FONT_BODY)
            tb.pack(fill="x", pady=(0, 4))
            if self.data["appearance"].get(key):
                tb.insert("0.0", self.data["appearance"][key])
            self._w_app[key] = tb

    def _suggest_appearance(self):
        race = self.data.get("race")
        cls = self.data.get("class_concept")
        gender = self.data.get("gender")
        name = self.data.get("name")
        prompt = (f"Generate a physical appearance for {name} — a {gender} {race} {cls}. "
                  f"Output exactly 6 lines, each prefixed by the field name and a colon, in this order:\n"
                  f"Height & build: ...\n"
                  f"Hair: ...\n"
                  f"Eyes: ...\n"
                  f"Skin: ...\n"
                  f"Distinguishing marks: ...\n"
                  f"Style/vibe: ...\n"
                  f"Each value should be 1-2 sentences max. Coherent, grounded, specific.")

        def apply_suggestion(text: str):
            for line in text.splitlines():
                if ":" in line:
                    key_part, value = line.split(":", 1)
                    value = value.strip()
                    key_lower = key_part.strip().lower()
                    if "height" in key_lower or "build" in key_lower:
                        target = self._w_app["height_build"]
                    elif "hair" in key_lower:
                        target = self._w_app["hair"]
                    elif "eye" in key_lower:
                        target = self._w_app["eyes"]
                    elif "skin" in key_lower:
                        target = self._w_app["skin"]
                    elif "mark" in key_lower:
                        target = self._w_app["distinguishing_marks"]
                    elif "style" in key_lower or "vibe" in key_lower:
                        target = self._w_app["style_vibe"]
                    else:
                        continue
                    if isinstance(target, ctk.CTkEntry):
                        target.delete(0, "end")
                        target.insert(0, value)
                    elif isinstance(target, ctk.CTkTextbox):
                        target.delete("0.0", "end")
                        target.insert("0.0", value)

        _ai_suggest(prompt,
                     on_complete=lambda txt: self.after(0, lambda: apply_suggestion(txt)),
                     on_error=lambda err: self.after(0, lambda:
                         messagebox.showwarning("Suggest failed", err, parent=self)))

    # ---- Step 7: Stats ----

    def _render_step_stats(self):
        ctk.CTkLabel(self.body, text="Stats", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Assign your six base stats. Total ≤ 72. No stat below 1, max 18 at creation. "
                          "Racial bonuses applied later. Per house rule: the DM never suggests a spread.",
                     font=FONT_BODY, text_color=TEXT_DIM, wraplength=720,
                     justify="left").pack(anchor="w", pady=(0, 16))

        # Live total counter
        self._w_stats_total = ctk.CTkLabel(self.body, text="Total: 60 / 72",
                                             font=FONT_HEADER, text_color=GREEN)
        self._w_stats_total.pack(anchor="w", pady=(0, 16))

        grid = ctk.CTkFrame(self.body, fg_color=BG_PANEL, corner_radius=10)
        grid.pack(anchor="w", padx=4, pady=4)

        self._w_stats: Dict[str, ctk.CTkEntry] = {}
        for i, stat in enumerate(("STR", "DEX", "CON", "INT", "WIS", "CHA")):
            row = ctk.CTkFrame(grid, fg_color="transparent")
            row.grid(row=i // 3, column=i % 3, padx=18, pady=12)
            ctk.CTkLabel(row, text=stat, width=42, font=FONT_LABEL,
                          text_color=GOLD).pack(side="left")
            entry = ctk.CTkEntry(row, width=70, height=38, fg_color=BG_CARD,
                                   text_color=TEXT, font=FONT_LABEL,
                                   justify="center")
            entry.pack(side="left", padx=8)
            entry.insert(0, str(self.data["stats"].get(stat, 10)))
            entry.bind("<KeyRelease>", lambda e: self._update_stats_total())
            self._w_stats[stat] = entry

        self._update_stats_total()

        ctk.CTkLabel(self.body,
                     text="Standard array reference: 15, 14, 13, 12, 10, 8 (total 72).",
                     font=FONT_SMALL, text_color=TEXT_DIM).pack(anchor="w", pady=(20, 0))

    def _update_stats_total(self):
        try:
            total = sum(int(self._w_stats[k].get() or 0) for k in ("STR","DEX","CON","INT","WIS","CHA"))
        except (ValueError, TypeError):
            total = -1
        if total > 72:
            self._w_stats_total.configure(text=f"Total: {total} / 72  (over by {total - 72})", text_color=RED)
        elif total < 0:
            self._w_stats_total.configure(text="Total: ? / 72  (invalid number)", text_color=RED)
        else:
            self._w_stats_total.configure(text=f"Total: {total} / 72", text_color=GREEN if total <= 72 else RED)

    # ---- Step 8: Starting gear ----

    def _render_step_gear(self):
        ctk.CTkLabel(self.body, text="Starting gear", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Pick your starting equipment. Class-appropriate options shown.",
                     font=FONT_BODY, text_color=TEXT_DIM).pack(anchor="w", pady=(0, 16))

        cls = self.data.get("class_concept", "Fighter")
        gear_list = STARTING_GEAR.get(cls, STARTING_GEAR["Custom"])

        self._w_gear: Dict[str, ctk.BooleanVar] = {}
        for item in gear_list:
            var = ctk.BooleanVar(value=item in self.data.get("starting_gear", []) or not self.data.get("starting_gear"))
            ctk.CTkCheckBox(self.body, text=item, variable=var, font=FONT_BODY,
                              text_color=TEXT, fg_color=GOLD, hover_color=GOLD_DIM).pack(
                anchor="w", padx=16, pady=4)
            self._w_gear[item] = var

        ctk.CTkLabel(self.body,
                     text="You can adjust gear later via the dashboard's Inventory tab.",
                     font=FONT_SMALL, text_color=TEXT_DIM).pack(anchor="w", pady=(20, 0))

    # ---- Step 9: Narrator style ----

    def _render_step_narrator(self):
        ctk.CTkLabel(self.body, text="Narrator style", font=FONT_HEADER,
                     text_color=GOLD).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body,
                     text="Pick a LitRPG author voice — sets the tone of your campaign narration. "
                          "The DM reads this at session start and maintains the voice throughout.",
                     font=FONT_BODY, text_color=TEXT_DIM, wraplength=720,
                     justify="left").pack(anchor="w", pady=(0, 16))

        self._w_narrator = ctk.StringVar(value=self.data.get("narrator_style") or "Aleron Kong (The Land)")

        scroll = ctk.CTkScrollableFrame(self.body, fg_color="transparent",
                                          height=420)
        scroll.pack(fill="both", expand=True)

        for author, desc in NARRATOR_STYLES.items():
            row = ctk.CTkFrame(scroll, fg_color=BG_PANEL, corner_radius=8)
            row.pack(fill="x", pady=6, padx=4)
            ctk.CTkRadioButton(row, text=author, variable=self._w_narrator, value=author,
                                font=FONT_LABEL, text_color=GOLD,
                                fg_color=GOLD).pack(anchor="w", padx=14, pady=(10, 4))
            ctk.CTkLabel(row, text=desc, font=FONT_BODY, text_color=TEXT_DIM,
                          wraplength=700, justify="left").pack(anchor="w", padx=42, pady=(0, 10))

    # ---- Suggest button helpers ----

    def _suggest_button(self, parent, label: str, callback: Callable):
        """Helper to add a Suggest button next to a label/header.
        Disabled if no API key."""
        btn = ctk.CTkButton(parent, text=f"✨ {label}", width=110, height=30,
                              fg_color=BG_CARD, hover_color=GOLD_DIM,
                              font=FONT_SMALL, text_color=GOLD if self.has_api else TEXT_DIM,
                              command=callback if self.has_api else
                                      lambda: messagebox.showinfo(
                                          "API key required",
                                          "Set ANTHROPIC_API_KEY env var or add ttrpg_key.txt next to play_engine.py to enable Suggest buttons.",
                                          parent=self))
        btn.pack(side="right", padx=8)
        if not self.has_api:
            btn.configure(state="normal")  # keep clickable so user gets the helpful message

    def _show_suggest_loading(self, target):
        if isinstance(target, ctk.CTkTextbox):
            target.delete("0.0", "end")
            target.insert("0.0", "⏳ Generating suggestions...")

    def _fill_textbox(self, target: ctk.CTkTextbox, text: str):
        target.delete("0.0", "end")
        target.insert("0.0", text)

    def _suggest_error(self, target: ctk.CTkTextbox, err: str):
        target.delete("0.0", "end")
        target.insert("0.0", f"⚠ Suggest failed: {err}")

    # ---- Finalize (Phase 2d pipeline — audit fixes applied) ----
    #
    # Audit fixes from WIZARD_PHASE_2D_AUDIT.md:
    #   CRIT-1: _find_ttrpg_root walks up looking for realm_lore_registry.json
    #           (matches generate_starter_campaign's marker — works in bundled .exe)
    #   CRIT-2: dropped subprocess; imports generate_starter_campaign in-process
    #   CRIT-3: appearance + narrator_style + ability_scores written to
    #           player_input.* (the canonical keys read by template + engine)
    #   CRIT-4: folder collision check up front; bounce to Name step on hit
    #   HIGH-1: pipeline runs on a background thread; UI stays responsive
    #   HIGH-2: starting_gear written to _story_engine_state.equipped (canonical)
    #   HIGH-5: empty / whitespace name check up front
    #   HIGH-6: per-step button text (Step 1/4 / Step 2/4 / ...)
    #   MED-1:  tts slot dedup is case-insensitive
    #   MED-2:  _resolve_*_string fall back to defaults instead of empty
    #   MED-7:  Windows-illegal char sanitization at finalize entry

    _ILLEGAL_NAME_CHARS = '<>:"/\\|?*'

    def _compute_folder_name(self) -> str:
        """Folder under TTRPG/<Folder>/ — Title Case with underscores."""
        raw = self.data["name"].strip()
        return raw.replace(" ", "_")

    def _compute_slug(self) -> str:
        """Manifest id (lowercase, underscores) — matches generate_starter_campaign."""
        return self._compute_folder_name().lower()

    def _find_ttrpg_root(self) -> Optional[Path]:
        """Walk up from this module looking for realm_lore_registry.json — the
        canonical TTRPG root marker. Same trick as generate_starter_campaign.
        Works inside the bundled .exe (where __file__ is in _MEI<tmp>) only if
        TTRPG_ROOT env var is set, which the launcher should set. Otherwise
        we walk up the .exe's location."""
        env_root = os.environ.get("TTRPG_ROOT")
        if env_root:
            p = Path(env_root)
            if (p / "realm_lore_registry.json").exists():
                return p

        # Walk up from this module (works in dev mode and OneDrive paths).
        cur = Path(__file__).resolve().parent
        for _ in range(10):
            if (cur / "realm_lore_registry.json").exists():
                return cur
            cur = cur.parent

        # Walk up from sys.executable (works in bundled .exe — the .exe lives
        # somewhere under TTRPG/Kenji/Game init files/dist/ typically).
        try:
            exe_parent = Path(sys.executable).resolve().parent
            cur = exe_parent
            for _ in range(10):
                if (cur / "realm_lore_registry.json").exists():
                    return cur
                cur = cur.parent
        except Exception:
            pass

        return None

    def _resolve_race_string(self) -> str:
        race = self.data.get("race", "") or ""
        if race == "Custom":
            custom = (self.data.get("race_custom", "") or "").strip()
            return custom or "Human"
        return race or "Human"

    def _resolve_class_string(self) -> str:
        cls = self.data.get("class_concept", "") or ""
        if cls == "Custom":
            custom = (self.data.get("class_custom", "") or "").strip()
            return custom or "Fighter"
        return cls or "Fighter"

    def _narrator_style_dict(self) -> Dict[str, str]:
        """Reshape the wizard's narrator_style string into the dict shape the
        template + engine expect: {author, series, voice}.

        Wizard stores e.g. "Aleron Kong (The Land)". Split into author + series."""
        selection = (self.data.get("narrator_style", "") or "").strip()
        if "(" in selection and selection.endswith(")"):
            author, _, rest = selection.partition("(")
            author = author.strip()
            series = rest[:-1].strip()
        else:
            author = selection
            series = ""
        return {
            "author": author,
            "series": series,
            "voice": "Selected via Character Creation Wizard.",
        }

    def _build_player_input(self) -> Dict:
        """Build the player_input dict that goes into generate_campaign_scaffold.
        This puts every wizard field in the canonical key the template defines."""
        appearance = dict(self.data.get("appearance", {}) or {})
        # Drop empty-string values so the template's defaults aren't replaced
        # with "" (preserves placeholder hint text in unfilled fields).
        appearance = {k: v for k, v in appearance.items() if v}

        return {
            "name": self.data["name"].strip(),
            "gender": self.data.get("gender", "") or "Unspecified",
            "race": self._resolve_race_string(),
            "class_concept": self._resolve_class_string(),
            "background": self.data.get("background", "") or "",
            "personal_goal": self.data.get("personal_goal", "") or "",
            "starting_region_preference": (
                self.data.get("starting_region_preference") or "frontier"
            ).lower(),
            "appearance": appearance,
            "narrator_style": self._narrator_style_dict(),
            "ability_scores": dict(self.data.get("stats", {})),
            "exp_archetype": "combat",
            "support_archetype": "",
        }

    def _validate_finalize_or_error(
        self, ttrpg_root: Optional[Path]
    ) -> Optional[str]:
        """Run all up-front validations. Returns an error string to show to the
        user, or None if everything looks good to proceed."""
        if ttrpg_root is None:
            return ("Could not locate the TTRPG root folder (looking for "
                    "realm_lore_registry.json). Set TTRPG_ROOT env var or "
                    "launch from the standard layout.")

        display = (self.data.get("name", "") or "").strip()
        if not display:
            return ("Name is empty. Go back to step 5 and enter a name.")

        bad = [c for c in display if c in self._ILLEGAL_NAME_CHARS]
        if bad:
            return ("Name contains characters Windows doesn't allow in folder "
                    "names: " + " ".join(sorted(set(bad))) + "\n\n"
                    "Go back to step 5 and pick a name without these.")

        folder = self._compute_folder_name()
        target_dir = ttrpg_root / folder
        if target_dir.exists():
            return ("A character folder already exists at:\n  "
                    + str(target_dir) + "\n\n"
                    "Pick a different name to avoid overwriting an existing "
                    "character. Go back to step 5.")

        slug = self._compute_slug()
        engine_dir = ttrpg_root / "Kenji" / "Game init files"
        manifest_path = engine_dir / "manifests" / (slug + ".json")
        if manifest_path.exists() and manifest_path.stat().st_size > 0:
            return ("A character manifest already exists for slug '"
                    + slug + "':\n  " + str(manifest_path) + "\n\n"
                    "Pick a different name. Go back to step 5.")

        return None

    def _pipeline_run_generator_inproc(
        self, ttrpg_root: Path
    ) -> Tuple[bool, str]:
        """Phase 2d-1 (audit fix CRIT-2): in-process call to
        generate_starter_campaign — no subprocess, no sys.executable issues.

        Builds the full player_input dict (with appearance / narrator_style /
        ability_scores in their canonical keys), runs generate_campaign_scaffold,
        runs create_campaign_folder, then merges starting gear into the
        canonical _story_engine_state.equipped list.

        Returns (ok, state_path_or_error_msg)."""
        engine_dir = ttrpg_root / "Kenji" / "Game init files"
        if str(engine_dir) not in sys.path:
            sys.path.insert(0, str(engine_dir))

        # Set TTRPG_ROOT so the generator's module-level constants point at
        # the right place (it computes TTRPG_DIR at import time from this).
        os.environ["TTRPG_ROOT"] = str(ttrpg_root)

        try:
            import generate_starter_campaign as gen
        except Exception as e:
            return False, "Could not import generate_starter_campaign: " + str(e)

        player_input = self._build_player_input()

        try:
            campaign = gen.generate_campaign_scaffold(player_input)
        except Exception as e:
            return False, "generate_campaign_scaffold failed: " + str(e)

        try:
            state_path = gen.create_campaign_folder(player_input["name"], campaign)
        except Exception as e:
            return False, "create_campaign_folder failed: " + str(e)

        # Merge starting gear into the canonical inventory key (HIGH-2 fix).
        gear = self.data.get("starting_gear", []) or []
        if gear:
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                ses = state.setdefault("_story_engine_state", {})
                equipped = ses.setdefault("equipped", [])
                for item in gear:
                    if item and item not in equipped:
                        equipped.append(item)
                with open(state_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                    f.write("\n")
            except Exception as e:
                return False, "Could not write starting gear to state: " + str(e)

        # Register locations (best-effort, non-fatal).
        try:
            gen.register_locations(campaign)
        except Exception:
            pass

        return True, str(state_path)

    def _pipeline_recompute_stats(
        self, state_path: Path, ttrpg_root: Path
    ) -> Tuple[bool, str]:
        """Phase 2d-2: import character_compute and recompute HP / AC / saves.

        recompute_ability_scores reads base + racial (idempotent — confirmed in
        audit), so this is safe to run after the generator has already populated
        the ability_scores block."""
        engine_dir = ttrpg_root / "Kenji" / "Game init files"
        if str(engine_dir) not in sys.path:
            sys.path.insert(0, str(engine_dir))
        try:
            import character_compute
        except Exception as e:
            return False, "Could not import character_compute: " + str(e)

        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            character_compute.recompute_character_state(state)
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            return False, "Recompute failed: " + str(e)
        return True, ""

    def _pipeline_write_dist_manifest(
        self, ttrpg_root: Path
    ) -> Tuple[bool, str]:
        """Phase 2d-3: also write manifest into dist/manifests/ override path."""
        slug = self._compute_slug()
        engine_dir = ttrpg_root / "Kenji" / "Game init files"
        central = engine_dir / "manifests" / (slug + ".json")
        if not central.is_file():
            return False, "Central manifest missing: " + str(central)

        dist_manifests = engine_dir / "dist" / "manifests"
        if not dist_manifests.parent.is_dir():
            return True, "skipped (no dist folder)"
        dist_manifests.mkdir(parents=True, exist_ok=True)
        dist_path = dist_manifests / (slug + ".json")
        try:
            dist_path.write_bytes(central.read_bytes())
        except Exception as e:
            return False, "Could not write dist manifest: " + str(e)
        return True, str(dist_path)

    def _pipeline_add_tts_slot(
        self, ttrpg_root: Path
    ) -> Tuple[bool, str]:
        """Phase 2d-4: add a blank voice slot in tts_config.json.
        Case-insensitive duplicate check (audit MED-1 fix)."""
        cfg_path = ttrpg_root / "Kenji" / "Game init files" / "tts_config.json"
        if not cfg_path.is_file():
            return True, "skipped (tts_config.json missing)"
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            return False, "Could not read tts_config.json: " + str(e)

        slots = cfg.setdefault("character_voices", {})
        display = self.data["name"].strip()
        # Case-insensitive existence check, skipping doc keys (those start "_").
        existing_lower = {
            k.lower(): k for k in slots.keys() if not k.startswith("_")
        }
        if display.lower() in existing_lower:
            return True, ("slot already exists as '"
                          + existing_lower[display.lower()] + "'")
        slots[display] = ""
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            return False, "Could not write tts_config.json: " + str(e)
        return True, ""

    # ---- Threaded pipeline runner + UI updaters ----

    def _set_step_text(self, text: str) -> None:
        """Thread-safe button-text updater. Schedules the UI change on the
        Tk main thread via self.after()."""
        try:
            self.after(0, lambda: self.btn_next.configure(text=text))
        except Exception:
            pass

    def _on_finalize(self):
        """Phase 2d pipeline — runs all up-front validations, then kicks off
        the actual work on a background thread so the UI stays responsive."""
        ttrpg_root = self._find_ttrpg_root()
        err = self._validate_finalize_or_error(ttrpg_root)
        if err:
            messagebox.showerror("Cannot create character", err, parent=self)
            return

        # Disable nav buttons while the pipeline runs.
        self.btn_back.configure(state="disabled")
        self.btn_next.configure(state="disabled", text="Step 1/4: Generating...")
        self.btn_cancel.configure(state="disabled")
        self.update_idletasks()

        thread = threading.Thread(
            target=self._pipeline_thread,
            args=(ttrpg_root,),
            daemon=True,
        )
        thread.start()

    def _pipeline_thread(self, ttrpg_root: Path) -> None:
        """Background-thread runner. Posts UI updates back via self.after()."""
        try:
            steps_log: List[str] = []

            # Step 1: in-process generator (with appearance / narrator / gear
            # threaded into player_input directly — CRIT-3 + HIGH-2 fix).
            self._set_step_text("Step 1/4: Generating...")
            ok, info = self._pipeline_run_generator_inproc(ttrpg_root)
            if not ok:
                self.after(0, lambda i=info:
                           self._finalize_failure("Step 1/4 — Generator", i))
                return
            state_path = Path(info)
            steps_log.append("Step 1/4  Generator: state file written")

            # Step 2: recompute HP/AC/saves.
            self._set_step_text("Step 2/4: Computing stats...")
            ok, info = self._pipeline_recompute_stats(state_path, ttrpg_root)
            if not ok:
                self.after(0, lambda i=info:
                           self._finalize_failure("Step 2/4 — Recompute", i))
                return
            steps_log.append("Step 2/4  Recompute: HP / AC / saves derived")

            # Step 3: dist/manifests override.
            self._set_step_text("Step 3/4: Writing manifests...")
            ok, info = self._pipeline_write_dist_manifest(ttrpg_root)
            if not ok:
                self.after(0, lambda i=info:
                           self._finalize_failure("Step 3/4 — Dist manifest", i))
                return
            steps_log.append("Step 3/4  Dist manifest: " + (info or "ok"))

            # Step 4: tts slot.
            self._set_step_text("Step 4/4: Adding TTS slot...")
            ok, info = self._pipeline_add_tts_slot(ttrpg_root)
            if not ok:
                self.after(0, lambda i=info:
                           self._finalize_failure("Step 4/4 — TTS slot", i))
                return
            steps_log.append("Step 4/4  TTS slot: " + (info or "added"))

            # Success — bounce back to UI thread to show the dialog.
            log_copy = list(steps_log)
            self.after(0, lambda: self._finalize_success(log_copy))

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            err_msg = str(e) + "\n\n" + tb
            self.after(0, lambda: self._finalize_failure("Pipeline crash", err_msg))

    def _finalize_success(self, steps_log: List[str]) -> None:
        """Show the success dialog and close the wizard. Called on UI thread."""
        slug = self._compute_slug()
        display = self.data["name"].strip()
        body = "\n".join(steps_log)
        msg = ("Character created!\n\n"
               + display + "  (slug: " + slug + ")\n"
               + "Folder: " + self._compute_folder_name() + "/\n\n"
               + body + "\n\n"
               + "Click OK to close this wizard.\nThen launch the dashboard "
               + "again from the desktop shortcut and pick "
               + display + " from the picker.")
        messagebox.showinfo("Character created", msg, parent=self)
        self.destroy()

    def _finalize_failure(self, step_label: str, err: str) -> None:
        """Re-enable nav buttons and show the failure to the user."""
        self.btn_back.configure(state="normal")
        self.btn_next.configure(state="normal", text="Create Character →")
        self.btn_cancel.configure(state="normal")
        messagebox.showerror(
            "Character creation failed",
            step_label + " failed:\n\n" + err
            + "\n\nNothing was launched. You can adjust the wizard and try "
            "again, or Cancel and start over.",
            parent=self,
        )


def run() -> None:
    """Entry point — instantiate and run the wizard. Called by
    kenji_gui._run_character_creation_wizard()."""
    app = CharacterCreationWizard()
    app.mainloop()


if __name__ == "__main__":
    run()
