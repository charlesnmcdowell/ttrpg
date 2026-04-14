#!/usr/bin/env python3
"""Live Dashboard — campaign-agnostic TTRPG state viewer with reactive music.

Each campaign folder contains campaign_manifest.json (paths to save file, music, shared engine).
Run:
  python kenji_gui.py
  python kenji_gui.py --campaign "C:\\path\\to\\Amaris\\Game init files"
  python kenji_gui.py --manifest "C:\\path\\to\\campaign_manifest.json"

Environment: TTRPG_CAMPAIGN_DIR may point at a campaign folder (same as --campaign).
"""

import sys, io, os, json, random, argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type, Any

import customtkinter as ctk

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

SCRIPT_DIR = Path(__file__).resolve().parent

# Defaults when campaign_manifest.json is missing (legacy Kenji layout)
_DEFAULT_MANIFEST = {
    "campaign_id": "kenji",
    "window_title_template": "{char_name} — Live Dashboard",
    "state_file": "kenji_state.json",
    "music_dir": "../music",
    "music_map": "../music/music_map.json",
    "engine_path": ".",
}


@dataclass
class CampaignConfig:
    """Resolved paths for one campaign (one 'save slot')."""
    root: Path
    campaign_id: str
    state_file: Path
    music_dir: Path
    music_map: Path
    engine_dir: Path
    window_title_template: str


def _parse_cli(argv: Optional[list]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="TTRPG Live Dashboard (multi-campaign)")
    p.add_argument(
        "--campaign", "-c",
        type=str,
        default=None,
        help="Path to campaign folder (must contain campaign_manifest.json)",
    )
    p.add_argument(
        "--manifest", "-m",
        type=str,
        default=None,
        help="Path directly to campaign_manifest.json",
    )
    return p.parse_args(argv)


def _load_campaign_config(argv: Optional[list] = None) -> CampaignConfig:
    args = _parse_cli(argv if argv is not None else sys.argv[1:])
    env_dir = os.environ.get("TTRPG_CAMPAIGN_DIR", "").strip()

    if args.manifest:
        manifest_path = Path(args.manifest).resolve()
        root = manifest_path.parent
    elif args.campaign:
        root = Path(args.campaign).resolve()
        manifest_path = root / "campaign_manifest.json"
    elif env_dir:
        root = Path(env_dir).resolve()
        manifest_path = root / "campaign_manifest.json"
    else:
        root = SCRIPT_DIR
        manifest_path = root / "campaign_manifest.json"

    if manifest_path.exists():
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise SystemExit(f"Invalid JSON in {manifest_path}: {e}") from e
        raw.pop("_comment", None)
        data = {**_DEFAULT_MANIFEST, **raw}
    else:
        data = dict(_DEFAULT_MANIFEST)
        if root != SCRIPT_DIR:
            raise SystemExit(
                f"Missing {manifest_path}. Create campaign_manifest.json in the campaign folder."
            )

    def _resolve(p: str) -> Path:
        path = Path(p)
        if path.is_absolute():
            return path.resolve()
        return (root / path).resolve()

    eng = data.get("engine_path", ".")
    engine_dir = _resolve(eng) if eng not in (None, ".", "") else root

    return CampaignConfig(
        root=root,
        campaign_id=str(data.get("campaign_id", "campaign")),
        state_file=_resolve(data["state_file"]),
        music_dir=_resolve(data["music_dir"]),
        music_map=_resolve(data["music_map"]),
        engine_dir=engine_dir,
        window_title_template=str(data.get("window_title_template", _DEFAULT_MANIFEST["window_title_template"])),
    )


def _import_story_engine(engine_dir: Path) -> Type[Any]:
    """Import StoryEngine from the shared engine folder (no duplicate engine per campaign)."""
    ed = str(engine_dir.resolve())
    if ed not in sys.path:
        sys.path.insert(0, ed)
    from ttrpg_game_engine import StoryEngine  # noqa: E402 — path set at runtime
    return StoryEngine

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
BG_DARK      = "#1a1a2e"
BG_PANEL     = "#16213e"
BG_CARD      = "#0f3460"
GOLD         = "#c9a959"
GOLD_DIM     = "#8a7340"
TEXT         = "#e8e0d4"
TEXT_DIM     = "#9e9585"
RED          = "#c0392b"
BLUE         = "#2980b9"
HP_LOW       = "#e74c3c"
HP_MID       = "#f39c12"
HP_HIGH      = "#2ecc71"
FONT_HEADER  = ("Segoe UI", 18, "bold")
FONT_TITLE   = ("Segoe UI", 14, "bold")
FONT_LABEL   = ("Segoe UI", 12, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 10)
FONT_MONO    = ("Consolas", 10)

COMBAT_KEYWORDS = {"combat", "battle", "fight", "attack", "engaging", "ambush", "assault"}
INN_KEYWORDS    = {"inn", "tavern", "hearth", "bar", "pub"}
SHOP_KEYWORDS   = {"shop", "market", "merchant", "vendor", "store"}
SMITH_KEYWORDS  = {"smith", "forge", "anvil", "blacksmith"}


class LiveDashboard(ctk.CTk):
    """Campaign-agnostic dashboard; paths come from CampaignConfig / campaign_manifest.json."""

    def __init__(self, config: CampaignConfig):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.config = config
        self._StoryEngine = _import_story_engine(config.engine_dir)

        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG_DARK)

        self.engine = None
        self._load_engine()
        self._apply_window_title_from_engine()
        self._load_music_map()

        self._current_track = None
        self._music_playing = False
        self._music_enabled = True

        self._last_mtime = 0.0
        self._last_location = ""
        self._last_story_beat = ""

        self._build_header()
        self._build_body()

        self.refresh_all()
        self._react_music()
        self._poll_state()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Music system
    # ------------------------------------------------------------------
    def _load_music_map(self):
        self._music_map = {"locations": {}, "contexts": {}, "character_themes": {}}
        mp = self.config.music_map
        if mp.exists():
            try:
                raw = json.loads(mp.read_text(encoding="utf-8"))
                raw.pop("_comment", None)
                self._music_map = raw
            except Exception:
                pass

    def _resolve_track(self, location=None, context=None, character=None):
        mm = self._music_map
        candidates = []
        if context and context in mm.get("contexts", {}):
            candidates = mm["contexts"][context]
        elif character and character in mm.get("character_themes", {}):
            candidates = mm["character_themes"][character]
        elif location:
            is_night = self.engine and (self.engine.hour >= 21 or self.engine.hour < 6)
            loc_data = mm.get("locations", {}).get(location)
            if not loc_data:
                for key in mm.get("locations", {}):
                    if key.lower() in location.lower() or location.lower() in key.lower():
                        loc_data = mm["locations"][key]
                        break
            if loc_data:
                time_key = "night" if is_night and "night" in loc_data else "day"
                candidates = loc_data.get(time_key, loc_data.get("day", []))
        if not candidates:
            return None
        full = self.config.music_dir / random.choice(candidates)
        return str(full) if full.exists() else None

    def _play_music(self, track_path):
        if not HAS_WINSOUND or not track_path:
            return
        if track_path == self._current_track and self._music_playing:
            return
        self._stop_music()
        self._current_track = track_path
        self._music_playing = True
        try:
            winsound.PlaySound(track_path,
                               winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        except Exception:
            self._music_playing = False

    def _stop_music(self):
        self._music_playing = False
        self._current_track = None
        if HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_ASYNC)
            except Exception:
                pass

    def _on_close(self):
        self._stop_music()
        self.destroy()

    # ------------------------------------------------------------------
    # Reactive music — auto-selects track based on state changes
    # ------------------------------------------------------------------
    def _react_music(self):
        if not self._music_enabled or not self.engine:
            return

        e = self.engine
        loc = e.location.lower()
        beat = (e.story_beat or "").lower()

        location_changed = (e.location != self._last_location)
        beat_changed = (e.story_beat != self._last_story_beat)

        self._last_location = e.location
        self._last_story_beat = e.story_beat

        if not location_changed and not beat_changed:
            return

        if beat_changed and any(kw in beat for kw in COMBAT_KEYWORDS):
            track = self._resolve_track(context="combat")
            if track:
                self._play_music(track)
                return

        char_themes = self._music_map.get("character_themes", {})
        if beat_changed:
            for char_name in char_themes:
                if char_name.lower() in beat:
                    track = self._resolve_track(character=char_name)
                    if track:
                        self._play_music(track)
                        return

        if any(kw in loc for kw in INN_KEYWORDS):
            ctx = "inn_evening" if e.hour >= 18 else "inn_morning"
            track = self._resolve_track(context=ctx)
            if track:
                self._play_music(track)
                return

        if any(kw in loc for kw in SHOP_KEYWORDS):
            track = self._resolve_track(context="shop")
            if track:
                self._play_music(track)
                return

        if any(kw in loc for kw in SMITH_KEYWORDS):
            track = self._resolve_track(context="blacksmith")
            if track:
                self._play_music(track)
                return

        track = self._resolve_track(location=e.location)
        if track:
            self._play_music(track)

    # ------------------------------------------------------------------
    # File watcher — polls kenji_state.json for changes
    # ------------------------------------------------------------------
    def _poll_state(self):
        try:
            mtime = os.path.getmtime(self.config.state_file)
            if mtime != self._last_mtime:
                self._last_mtime = mtime
                self._load_engine()
                self.refresh_all()
                self._react_music()
                self._refresh_now_playing()
        except Exception:
            pass
        self.after(2000, self._poll_state)

    # ------------------------------------------------------------------
    # Engine loader
    # ------------------------------------------------------------------
    def _load_engine(self):
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            self.engine = self._StoryEngine.load_json(str(self.config.state_file))
        finally:
            sys.stdout = old_stdout
        try:
            self._last_mtime = os.path.getmtime(self.config.state_file)
        except Exception:
            pass

    def _apply_window_title_from_engine(self):
        char = "…"
        if self.engine and getattr(self.engine, "char_name", None):
            char = self.engine.char_name
        tpl = self.config.window_title_template
        try:
            self.title(tpl.format(char_name=char))
        except Exception:
            self.title(tpl.replace("{char_name}", char))

    # ------------------------------------------------------------------
    # Header bar
    # ------------------------------------------------------------------
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        self.lbl_name = ctk.CTkLabel(hdr, text="", font=FONT_HEADER, text_color=GOLD)
        self.lbl_name.pack(side="left", padx=16)

        self.lbl_time = ctk.CTkLabel(hdr, text="", font=FONT_TITLE, text_color=TEXT)
        self.lbl_time.pack(side="left", padx=16)

        self.lbl_location = ctk.CTkLabel(hdr, text="", font=FONT_BODY, text_color=TEXT_DIM)
        self.lbl_location.pack(side="left", padx=16)

        self.lbl_version = ctk.CTkLabel(hdr, text="", font=FONT_SMALL, text_color=TEXT_DIM)
        self.lbl_version.pack(side="right", padx=16)

        self.btn_music_toggle = ctk.CTkButton(hdr, text="♫ ON", width=55, height=28,
                                               fg_color=BG_CARD, hover_color=GOLD_DIM,
                                               text_color=GOLD, font=FONT_SMALL,
                                               command=self._on_music_toggle)
        self.btn_music_toggle.pack(side="right", padx=4)
        ctk.CTkButton(hdr, text="■", width=28, height=28, fg_color=BG_CARD,
                       hover_color=RED, text_color=TEXT, font=FONT_SMALL,
                       command=self._stop_music).pack(side="right", padx=2)
        self.lbl_now_playing = ctk.CTkLabel(hdr, text="", font=FONT_SMALL, text_color=TEXT_DIM)
        self.lbl_now_playing.pack(side="right", padx=8)

    def _on_music_toggle(self):
        self._music_enabled = not self._music_enabled
        if self._music_enabled:
            self.btn_music_toggle.configure(text="♫ ON")
            self._react_music()
        else:
            self.btn_music_toggle.configure(text="♫ OFF")
            self._stop_music()
        self._refresh_now_playing()

    def _refresh_now_playing(self):
        if self._current_track and self._music_playing:
            name = Path(self._current_track).stem
            if len(name) > 30:
                name = name[:28] + "..."
            self.lbl_now_playing.configure(text=f"♫ {name}")
        else:
            self.lbl_now_playing.configure(text="")

    # ------------------------------------------------------------------
    # Body: 2-column layout
    # ------------------------------------------------------------------
    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        body.pack(fill="both", expand=True, padx=4, pady=4)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_center_panel(body)

    # ------------------------------------------------------------------
    # LEFT PANEL — character card (read-only)
    # ------------------------------------------------------------------
    def _build_left_panel(self, parent):
        left = ctk.CTkScrollableFrame(parent, fg_color=BG_PANEL, width=280, corner_radius=8,
                                       label_text="CHARACTER", label_font=FONT_LABEL,
                                       label_fg_color=BG_CARD, label_text_color=GOLD)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 4))

        hp_frame = ctk.CTkFrame(left, fg_color="transparent")
        hp_frame.pack(fill="x", padx=4, pady=(4, 2))
        ctk.CTkLabel(hp_frame, text="HP", font=FONT_LABEL, text_color=GOLD).pack(anchor="w")
        self.hp_bar = ctk.CTkProgressBar(hp_frame, height=18, corner_radius=4)
        self.hp_bar.pack(fill="x", pady=2)
        self.lbl_hp = ctk.CTkLabel(hp_frame, text="", font=FONT_BODY, text_color=TEXT)
        self.lbl_hp.pack(anchor="w")

        self.lbl_ac = ctk.CTkLabel(left, text="", font=FONT_LABEL, text_color=TEXT)
        self.lbl_ac.pack(anchor="w", padx=8, pady=(2, 6))

        ctk.CTkLabel(left, text="SPELL SLOTS", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.slot_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.slot_frame.pack(fill="x", padx=4)

        ctk.CTkLabel(left, text="CHARGES", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(10, 2))
        self.charge_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.charge_frame.pack(fill="x", padx=4)

        ctk.CTkLabel(left, text="CURRENCY", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(10, 2))
        self.lbl_currency = ctk.CTkLabel(left, text="", font=FONT_BODY, text_color=TEXT, justify="left")
        self.lbl_currency.pack(anchor="w", padx=12)
        self.lbl_meals = ctk.CTkLabel(left, text="", font=FONT_BODY, text_color=TEXT)
        self.lbl_meals.pack(anchor="w", padx=12, pady=(2, 6))

        ctk.CTkLabel(left, text="WEAPON", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.lbl_weapon = ctk.CTkLabel(left, text="", font=FONT_SMALL, text_color=TEXT_DIM,
                                        wraplength=250, justify="left")
        self.lbl_weapon.pack(anchor="w", padx=12, pady=(0, 6))

        self.lbl_meal_status = ctk.CTkLabel(left, text="", font=FONT_BODY, text_color=TEXT)
        self.lbl_meal_status.pack(anchor="w", padx=8, pady=(2, 4))

        ctk.CTkLabel(left, text="CONDITIONS", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.lbl_conditions = ctk.CTkLabel(left, text="", font=FONT_SMALL, text_color=TEXT_DIM,
                                          wraplength=250, justify="left")
        self.lbl_conditions.pack(anchor="w", padx=12, pady=(0, 4))

        ctk.CTkLabel(left, text="ABILITY SCORES", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.sheet_ability_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.sheet_ability_frame.pack(fill="x", padx=4)

        ctk.CTkLabel(left, text="SKILLS", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.sheet_skills_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.sheet_skills_frame.pack(fill="x", padx=4)

        ctk.CTkLabel(left, text="SPELLS (KNOWN)", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.sheet_spells_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.sheet_spells_frame.pack(fill="x", padx=4)

        ctk.CTkLabel(left, text="CLASS FEATURES", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.sheet_features_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.sheet_features_frame.pack(fill="x", padx=4)

        ctk.CTkLabel(left, text="PERKS", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(6, 2))
        self.sheet_perks_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.sheet_perks_frame.pack(fill="x", padx=4)

    # ------------------------------------------------------------------
    # CENTER PANEL — tabbed content
    # ------------------------------------------------------------------
    def _build_center_panel(self, parent):
        center = ctk.CTkFrame(parent, fg_color=BG_DARK, corner_radius=0)
        center.grid(row=0, column=1, sticky="nsew")

        self.tabs = ctk.CTkTabview(center, fg_color=BG_PANEL, segmented_button_fg_color=BG_CARD,
                                    segmented_button_selected_color=GOLD_DIM,
                                    segmented_button_unselected_color=BG_CARD,
                                    text_color=TEXT, corner_radius=8)
        self.tabs.pack(fill="both", expand=True)

        for name in ("Status", "Inventory", "World", "Army", "Schedule", "Narrative"):
            tab = self.tabs.add(name)
            tb = ctk.CTkTextbox(tab, fg_color=BG_CARD, text_color=TEXT,
                                font=FONT_MONO, wrap="word", state="disabled")
            tb.pack(fill="both", expand=True, padx=4, pady=4)
            setattr(self, f"_tb_{name.lower()}", tb)

    # ------------------------------------------------------------------
    # REFRESH all panels
    # ------------------------------------------------------------------
    def refresh_all(self):
        e = self.engine
        if not e:
            return

        self.lbl_name.configure(text=f"{e.char_name}  Lv{e.level}")
        self.lbl_time.configure(text=f"Day {e.day}  {e.hour:02d}:00 — {e.time_of_day()}")
        self.lbl_location.configure(text=f"{e.location} — {e.weather}")
        ver = f"v{e._save_version}"
        if e._saved_at:
            ver += f"  ({e._saved_at})"
        self.lbl_version.configure(text=ver)

        hp_frac = e.hp / max(e.max_hp, 1)
        self.hp_bar.set(hp_frac)
        if hp_frac > 0.6:
            self.hp_bar.configure(progress_color=HP_HIGH)
        elif hp_frac > 0.3:
            self.hp_bar.configure(progress_color=HP_MID)
        else:
            self.hp_bar.configure(progress_color=HP_LOW)
        hp_text = f"{e.hp}/{e.max_hp}"
        if e.temp_hp:
            hp_text += f" (+{e.temp_hp} temp)"
        self.lbl_hp.configure(text=hp_text)
        self.lbl_ac.configure(text=f"AC  {e.ac}")

        for w in self.slot_frame.winfo_children():
            w.destroy()
        for level in sorted(e.spell_slots.keys(), key=lambda x: int(x)):
            cur, mx = e.spell_slots[level]
            row = ctk.CTkFrame(self.slot_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"L{level}", width=30, font=FONT_SMALL, text_color=TEXT).pack(side="left")
            ctk.CTkLabel(row, text=f"{cur}/{mx}", width=45, font=FONT_BODY, text_color=TEXT).pack(side="left", padx=4)
            bar = ctk.CTkProgressBar(row, width=100, height=10, corner_radius=3)
            bar.set(cur / max(mx, 1))
            bar.configure(progress_color=BLUE)
            bar.pack(side="left", padx=4)

        for w in self.charge_frame.winfo_children():
            w.destroy()
        for name in sorted(e.charges.keys()):
            cur, mx = e.charges[name]
            row = ctk.CTkFrame(self.charge_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=name, width=90, font=FONT_SMALL, text_color=TEXT, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=f"{cur}/{mx}", width=45, font=FONT_BODY, text_color=TEXT).pack(side="left", padx=4)

        self.lbl_currency.configure(text=f"{e.gold} GP  |  {e.silver} SP  |  {e.copper} CP")
        self.lbl_meals.configure(text=f"Meals: {e.meals}")
        self.lbl_meal_status.configure(text=e.meal_status())
        self.lbl_weapon.configure(text=f"{e.weapon_config}\n{e.weapon_config_detail}" if e.weapon_config else "—")
        self._refresh_character_sheet(e)

        self._refresh_status_tab()
        self._refresh_inventory_tab()
        self._refresh_world_tab()
        self._refresh_army_tab()
        self._refresh_schedule_tab()
        self._refresh_narrative_tab()
        self._refresh_now_playing()
        self._apply_window_title_from_engine()

    # ------------------------------------------------------------------
    # Tab refresh helpers
    # ------------------------------------------------------------------
    def _set_tb(self, name, text):
        tb = getattr(self, f"_tb_{name}")
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")

    def _clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _refresh_character_sheet(self, e):
        """Left column: conditions, ability scores, skills, spells, class features, perks."""
        if hasattr(self, "lbl_conditions"):
            self.lbl_conditions.configure(
                text=", ".join(e.statuses) if e.statuses else "—"
            )
        self._clear_frame(self.sheet_ability_frame)
        order = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
        ab = getattr(e, "ability_scores", None) or {}
        if ab:
            row = ctk.CTkFrame(self.sheet_ability_frame, fg_color="transparent")
            row.pack(fill="x")
            for k in order:
                if k in ab:
                    ctk.CTkLabel(
                        row,
                        text=f"{k}\n{ab[k]}",
                        width=38,
                        font=FONT_SMALL,
                        text_color=TEXT,
                    ).pack(side="left", padx=1)
            extra = [k for k in sorted(ab.keys()) if k not in order]
            for k in extra:
                ctk.CTkLabel(
                    self.sheet_ability_frame,
                    text=f"{k}  {ab[k]}",
                    font=FONT_SMALL,
                    text_color=TEXT_DIM,
                    anchor="w",
                ).pack(fill="x", padx=2)
        else:
            ctk.CTkLabel(
                self.sheet_ability_frame,
                text="—",
                font=FONT_SMALL,
                text_color=TEXT_DIM,
            ).pack(anchor="w")

        self._clear_frame(self.sheet_skills_frame)
        skills = getattr(e, "skills", None) or {}
        if skills:
            for sk, mod in sorted(skills.items()):
                ctk.CTkLabel(
                    self.sheet_skills_frame,
                    text=f"{sk}  {mod}",
                    font=FONT_SMALL,
                    text_color=TEXT,
                    anchor="w",
                ).pack(fill="x", padx=4)
        else:
            ctk.CTkLabel(
                self.sheet_skills_frame,
                text="—",
                font=FONT_SMALL,
                text_color=TEXT_DIM,
            ).pack(anchor="w")

        self._clear_frame(self.sheet_spells_frame)
        spells = getattr(e, "known_spells", None) or []
        if spells:
            for sp in spells:
                ctk.CTkLabel(
                    self.sheet_spells_frame,
                    text=f"• {sp}",
                    font=FONT_SMALL,
                    text_color=TEXT,
                    anchor="w",
                ).pack(fill="x", padx=4)
        else:
            ctk.CTkLabel(
                self.sheet_spells_frame,
                text="—",
                font=FONT_SMALL,
                text_color=TEXT_DIM,
            ).pack(anchor="w")

        self._clear_frame(self.sheet_features_frame)
        feats = getattr(e, "class_features", None) or []
        if feats:
            for feat in feats:
                ctk.CTkLabel(
                    self.sheet_features_frame,
                    text=f"• {feat}",
                    font=FONT_SMALL,
                    text_color=TEXT,
                    anchor="w",
                ).pack(fill="x", padx=4)
        else:
            ctk.CTkLabel(
                self.sheet_features_frame,
                text="—",
                font=FONT_SMALL,
                text_color=TEXT_DIM,
            ).pack(anchor="w")

        self._clear_frame(self.sheet_perks_frame)
        if e.active_perks:
            for p in e.active_perks:
                txt = f"{p.get('name', '?')} — {p.get('effect', '')}" if isinstance(p, dict) else str(p)
                ctk.CTkLabel(
                    self.sheet_perks_frame,
                    text=f"• {txt}",
                    font=FONT_SMALL,
                    text_color=GOLD,
                    anchor="w",
                    wraplength=250,
                    justify="left",
                ).pack(fill="x", padx=4)
        else:
            ctk.CTkLabel(
                self.sheet_perks_frame,
                text="—",
                font=FONT_SMALL,
                text_color=TEXT_DIM,
            ).pack(anchor="w")

    def _refresh_status_tab(self):
        e = self.engine
        lines = ["═══ STATUS (CONDITIONS) ═══"]
        lines.append(f"  {', '.join(e.statuses) if e.statuses else '(none)'}")

        lines += ["", "═══ ABILITY SCORES ═══"]
        if getattr(e, "ability_scores", None):
            order = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
            for k in order:
                if k in e.ability_scores:
                    lines.append(f"  {k}: {e.ability_scores[k]}")
            for k in sorted(e.ability_scores.keys()):
                if k not in order:
                    lines.append(f"  {k}: {e.ability_scores[k]}")
        else:
            lines.append("  (none — add ability_scores to state JSON)")

        lines += ["", "═══ SKILLS ═══"]
        if getattr(e, "skills", None):
            for sk, mod in sorted(e.skills.items()):
                lines.append(f"  {sk}: {mod}")
        else:
            lines.append("  (none — add skills to state JSON)")

        lines += ["", "═══ SPELLS (KNOWN) ═══"]
        if getattr(e, "known_spells", None):
            for sp in e.known_spells:
                lines.append(f"  • {sp}")
        else:
            lines.append("  (none — add known_spells to state JSON)")

        lines += ["", "═══ CLASS FEATURES ═══"]
        if getattr(e, "class_features", None):
            for feat in e.class_features:
                lines.append(f"  • {feat}")
        else:
            lines.append("  (none — add class_features to state JSON)")

        lines += ["", "═══ PERKS (ACTIVE) ═══"]
        if e.active_perks:
            for p in e.active_perks:
                if isinstance(p, dict):
                    lines.append(f"  {p.get('name', '?')} — {p.get('effect', '')}")
                else:
                    lines.append(f"  {p}")
        else:
            lines.append("  (none)")

        lines += ["", "═══ CHARGES (LIMITED USES) ═══"]
        if e.charges:
            for name, pair in sorted(e.charges.items()):
                lines.append(f"  {name}: {pair[0]}/{pair[1]}")
        else:
            lines.append("  (none)")

        lines += ["", "═══ ACTIVE BUFFS ═══"]
        if e.buffs:
            for name, b in e.buffs.items():
                dur = b.get("duration_hrs", b.get("duration", "?"))
                fx = b.get("effects", "")
                lines.append(f"  {name}  ({dur}hr)  — {fx}")
        else:
            lines.append("  (none)")

        lines += ["", "═══ MEAL & EXP ═══"]
        lines.append(f"  Hours since meal: {e.hours_since_meal}")
        lines.append(f"  {e.meal_status()}")
        lines.append(f"  EXP: {e.exp:,}")
        self._set_tb("status", "\n".join(lines))

    def _refresh_inventory_tab(self):
        e = self.engine
        lines = ["═══ EQUIPPED ═══"]
        for item in e.equipped:
            lines.append(f"  • {item}")
        lines += ["", "═══ SATCHEL ═══"]
        for item in e.satchel:
            lines.append(f"  • {item}")
        lines += ["", "═══ CONSUMABLES ═══"]
        if e.consumables:
            for name, count in e.consumables.items():
                lines.append(f"  {name}: {count}")
        else:
            lines.append("  (none)")
        lines += ["", "═══ KEY ITEMS ═══"]
        for item in e.key_items:
            lines.append(f"  ★ {item}")
        self._set_tb("inventory", "\n".join(lines))

    def _refresh_world_tab(self):
        e = self.engine
        lines = ["═══ THREAT CLOCKS ═══"]
        if e.threat_clocks:
            for name, c in sorted(e.threat_clocks.items(), key=lambda x: -x[1].get("progress", 0)):
                prog = c.get("progress", 0)
                rate = c.get("rate", 0)
                filled = int(prog / 100 * 20)
                bar = "█" * filled + "░" * (20 - filled)
                lines.append(f"  {name}")
                lines.append(f"    [{bar}] {prog}%  ({rate}/day)")
                desc = c.get("description", "")
                if desc:
                    lines.append(f"    {desc}")
                if prog >= 75:
                    lines.append(f"    ⚠️ TRIGGER: {c.get('trigger', '')}")
                lines.append("")
        else:
            lines.append("  (none)")
        lines.append("═══ KEY NPCs ═══")
        if e.npcs:
            for name, info in sorted(e.npcs.items()):
                loc = info.get("location", "?")
                act = info.get("activity", "")
                lines.append(f"  {name:15s}  {loc}")
                if act:
                    lines.append(f"  {'':15s}  └ {act}")
        else:
            lines.append("  (none)")
        lines += ["", "═══ RELATIONSHIPS ═══"]
        if e.relationships:
            for npc, r in sorted(e.relationships.items(), key=lambda x: -abs(x[1].get("score", 0))):
                score = r.get("score", 0)
                tier = r.get("tier", "?")
                hist = r.get("history", [])
                last = hist[-1]["reason"] if hist else ""
                lines.append(f"  {npc:15s}  {score:+d}  ({tier})  {last}")
        else:
            lines.append("  (none)")
        lines += ["", "═══ REPUTATION ═══"]
        if e.reputation:
            for faction, info in e.reputation.items():
                lines.append(f"  {faction}: {info.get('level', '?')} — {info.get('opinion', '?')}")
        else:
            lines.append("  (none)")
        self._set_tb("world", "\n".join(lines))

    def _refresh_army_tab(self):
        e = self.engine
        lines = []
        if not e.hegemony_active:
            lines.append("  Sorcerer's Hegemony not yet active.")
            self._set_tb("army", "\n".join(lines))
            return
        lines.append("═══ CONSTRUCT ARMY ═══")
        lines.append(f"  Total: {e.total_constructs()} constructs")
        lines.append("")
        for portal, army in sorted(e.construct_army.items()):
            w, h, m, r = army.get("warrior", 0), army.get("healer", 0), army.get("mage", 0), army.get("ranger", 0)
            sq, dest = army.get("squads", 0), army.get("destroyed", 0)
            lines.append(f"  {portal}: {w+h+m+r} active ({sq} squads)")
            lines.append(f"    W:{w}  H:{h}  M:{m}  R:{r}  (lost:{dest})")
            fear = e.construct_fear.get(portal, 0)
            fear_labels = {0: "none", 1: "unsettling", 2: "fear", 3: "panic", 4: "crisis"}
            lines.append(f"    Fear: {fear_labels.get(fear, fear)}")
            lines.append("")
        lines.append("═══ PORTALS ═══")
        active = sum(1 for s in e.portals.values() if s == "active")
        lines.append(f"  {active}/{e.portal_max} active")
        for name, status in sorted(e.portals.items()):
            lines.append(f"  {'●' if status == 'active' else '○'} {name}: {status}")
        lines += ["", "═══ SQUADS ═══"]
        if e.squads:
            for name, info in sorted(e.squads.items()):
                icon = "⚔️" if info.get("status") == "deployed" else "🏠"
                lines.append(f"  {icon} {name} (Cpt: {info.get('captain', '?')})")
                lines.append(f"    {info.get('status', '?')} @ {info.get('location', '?')}")
                if info.get("mission"):
                    lines.append(f"    Mission: {info['mission']}")
                lines.append("")
        else:
            lines.append("  (none)")
        lines += ["", "═══ ASSETS & INCOME ═══"]
        if e.golden_age_active:
            lines.append("  ★ GOLDEN AGE ACTIVE (2x income)")
        if e.assets:
            for a in e.assets:
                icon = "✓" if a.get("status") == "active" else "✗"
                lines.append(f"  {icon} {a.get('name', '?')}: {a.get('display', '')} [{a.get('status', '?')}]")
        else:
            lines.append("  (none)")
        self._set_tb("army", "\n".join(lines))

    def _refresh_schedule_tab(self):
        e = self.engine
        lines = ["═══ EVENTS ═══"]
        if e.events:
            for ev in sorted(e.events, key=lambda x: x.get("day", 999)):
                day, name, pri = ev.get("day", "?"), ev.get("name", "?"), ev.get("priority", "MED")
                delta = e.hours_until(day) if isinstance(day, int) else 0
                when = "NOW" if delta <= 0 else (f"{delta}hr" if delta < 24 else f"{delta//24}d {delta%24}hr")
                lines.append(f"  [{pri}] {name} — Day {day} ({when})")
                if ev.get("notes"):
                    lines.append(f"         {ev['notes']}")
        else:
            lines.append("  (none)")
        lines += ["", "═══ QUESTS ═══"]
        if e.quests:
            for q in e.quests:
                lines.append(f"  [{q.get('priority', 'MED')}] {q.get('name', '?')}  [{q.get('status', '?')}]")
                if q.get("notes"):
                    lines.append(f"         {q['notes']}")
        else:
            lines.append("  (none)")
        lines += ["", "═══ PENDING CONSEQUENCES ═══"]
        unfired = [c for c in e.consequences if not c.get("fired")]
        if unfired:
            for c in sorted(unfired, key=lambda x: x.get("trigger_day", 999)):
                lines.append(f"  Day {c.get('trigger_day', '?')}: {c.get('cause', '?')}")
                lines.append(f"    → {c.get('effect', '?')}")
        else:
            lines.append("  (none pending)")
        lines += ["", "═══ FACTION PLOTS ═══"]
        if e.org_plots:
            for org, p in e.org_plots.items():
                if p.get("progress", 0) >= 100:
                    continue
                lines.append(f"  {org}: {p.get('plot', '?')} ({p.get('progress', 0)}%)")
                if p.get("next_move"):
                    lines.append(f"    Next: {p['next_move']} (Day {p.get('next_move_day', '?')})")
        else:
            lines.append("  (none)")
        self._set_tb("schedule", "\n".join(lines))

    def _refresh_narrative_tab(self):
        e = self.engine
        lines = ["═══ STORY BEAT ═══", f"  {e.story_beat or '(none)'}"]
        lines += ["", "═══ CANON POINTER ═══", f"  {e.canon_pointer or '(none)'}"]
        lines += ["", "═══ NARRATIVE NOTES ═══"]
        if e.narrative_notes:
            for note in e.narrative_notes:
                lines.append(f"  • {note}")
        else:
            lines.append("  (none)")
        if e.events_active:
            lines += ["", "═══ ACTIVE EVENTS ═══"]
            for name, ev in e.events_active.items():
                lines.append(f"  {name} ({ev.get('type', '?')}) — Stage {ev.get('stage', '?')}/{ev.get('max_stages', '?')} [{ev.get('status', '?')}]")
                for c_name, c_info in ev.get("combatants", {}).items():
                    lines.append(f"    {c_name}: {c_info.get('status', '?')}  W:{c_info.get('wins', 0)}")
                for bout in ev.get("bracket", []):
                    lines.append(f"    Bout {bout.get('bout', '?')}: {bout.get('a', '?')} vs {bout.get('b', '?')} → {bout.get('winner', '?')} ({bout.get('rounds', '?')}r)")
                lines.append("")
        self._set_tb("narrative", "\n".join(lines))


# Backward-compatible name for scripts that imported KenjiDashboard
KenjiDashboard = LiveDashboard


if __name__ == "__main__":
    cfg = _load_campaign_config()
    app = LiveDashboard(cfg)
    app.mainloop()
