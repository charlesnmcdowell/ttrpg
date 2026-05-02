#!/usr/bin/env python3
"""Live Dashboard — campaign-agnostic TTRPG state viewer with reactive music.

Each campaign folder contains campaign_manifest.json (paths to save file, music, shared engine).
Run:
  python kenji_gui.py
  python kenji_gui.py --campaign "C:\\path\\to\\Amaris\\Game init files"
  python kenji_gui.py --manifest "C:\\path\\to\\campaign_manifest.json"

Environment: TTRPG_CAMPAIGN_DIR may point at a campaign folder (same as --campaign).
"""

import sys, io, os, json, random, argparse, re
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type, Any

import customtkinter as ctk

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# PyInstaller-aware path resolution.
# - When running as a PyInstaller .exe, __file__ resolves to the temp extraction
#   directory (sys._MEIPASS) which contains bundled read-only assets. The user's
#   STATE FILES live next to the .exe, not inside the bundle.
# - When running as a normal Python script, both directories are the same.
if getattr(sys, "frozen", False):
    # Frozen .exe (PyInstaller)
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)).resolve()
    SCRIPT_DIR = Path(sys.executable).resolve().parent
else:
    # Regular Python script run
    BUNDLE_DIR = Path(__file__).resolve().parent
    SCRIPT_DIR = Path(__file__).resolve().parent

# Defaults when campaign_manifest.json is missing (legacy Kenji layout).
# Note: state_file resolves relative to SCRIPT_DIR (next to the .exe at runtime,
# or next to kenji_gui.py when run as a script), NOT inside the bundle.
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
        "--character", "-C",
        type=str,
        default=None,
        help="Character name (looks up manifests/<name>.json in the engine folder). "
             "Recommended: '--character cookie', '--character kenji', '--character amaris'.",
    )
    p.add_argument(
        "--campaign", "-c",
        type=str,
        default=None,
        help="(Legacy) Path to campaign folder containing campaign_manifest.json.",
    )
    p.add_argument(
        "--manifest", "-m",
        type=str,
        default=None,
        help="(Legacy) Path directly to a campaign_manifest.json file.",
    )
    return p.parse_args(argv)


def _find_ttrpg_root(start: Path) -> Optional[Path]:
    """Walk up from `start` until we find realm_lore_registry.json (TTRPG repo root)."""
    cur = start.resolve()
    for _ in range(10):
        if (cur / "realm_lore_registry.json").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _manifest_search_dirs() -> list:
    """Where to look for manifests, in priority order.

    1. SCRIPT_DIR/manifests/   — user-overridable (next to kenji_gui.py or .exe)
    2. BUNDLE_DIR/manifests/   — bundled fallback (sys._MEIPASS in frozen mode)

    Same dir twice when running as a script — that's fine, the second is a no-op.
    """
    dirs = [SCRIPT_DIR / "manifests"]
    bundled = BUNDLE_DIR / "manifests"
    if bundled.resolve() != (SCRIPT_DIR / "manifests").resolve():
        dirs.append(bundled)
    return dirs


def _find_manifest(filename: str) -> Optional[Path]:
    """Return the first existing manifests/<filename> across search dirs."""
    for d in _manifest_search_dirs():
        candidate = d / filename
        if candidate.exists():
            return candidate
    return None


def _list_available_characters() -> list:
    """All character names with a manifest, across search dirs (de-duped, sorted)."""
    seen = set()
    for d in _manifest_search_dirs():
        if d.exists():
            for p in d.glob("*.json"):
                seen.add(p.stem)
    return sorted(seen)


def _load_campaign_config(argv: Optional[list] = None) -> CampaignConfig:
    args = _parse_cli(argv if argv is not None else sys.argv[1:])
    env_dir = os.environ.get("TTRPG_CAMPAIGN_DIR", "").strip()
    env_char = os.environ.get("TTRPG_CHARACTER", "").strip()

    # Resolution priority (new architecture: all manifests live in Kenji/Game init files/manifests/):
    # 1. --character <name>     → look up manifests/<name>.json inside SCRIPT_DIR (or its frozen-mode equivalent)
    # 2. --manifest <path>      → use that file directly (legacy)
    # 3. --campaign <path>      → look for <path>/campaign_manifest.json (legacy)
    # 4. env TTRPG_CHARACTER    → same as --character
    # 5. env TTRPG_CAMPAIGN_DIR → same as --campaign
    # 6. default                → manifests/kenji.json
    character = args.character or env_char or None

    manifest_path: Optional[Path] = None
    legacy_root: Optional[Path] = None

    if character:
        # New architecture: manifests live in SCRIPT_DIR/manifests/ (user-overridable)
        # OR BUNDLE_DIR/manifests/ (bundled into the .exe at build time).
        manifest_path = _find_manifest(f"{character.lower()}.json")
        if manifest_path is None:
            searched = "\n    ".join(str(d / f"{character.lower()}.json") for d in _manifest_search_dirs())
            raise SystemExit(
                f"Missing manifest for character '{character}'.\n"
                f"  Searched:\n    {searched}\n"
                f"  Available characters: {_list_available_characters()}\n"
                f"  Run generate_starter_campaign.py to create a new character."
            )
    elif args.manifest:
        manifest_path = Path(args.manifest).resolve()
        legacy_root = manifest_path.parent
    elif args.campaign:
        legacy_root = Path(args.campaign).resolve()
        manifest_path = legacy_root / "campaign_manifest.json"
    elif env_dir:
        legacy_root = Path(env_dir).resolve()
        manifest_path = legacy_root / "campaign_manifest.json"
    else:
        # Default to Kenji — same dual-dir search.
        manifest_path = _find_manifest("kenji.json")
        if manifest_path is None:
            # Fallback to legacy default (kenji_state.json next to script)
            data = dict(_DEFAULT_MANIFEST)
            data["__resolution_root__"] = "legacy_script_dir"
            return _build_config(data, SCRIPT_DIR)

    if not manifest_path.exists():
        raise SystemExit(
            f"Missing {manifest_path}.\n"
            f"For a new character, run generate_starter_campaign.py.\n"
            f"For legacy single-folder campaigns, place campaign_manifest.json in the campaign folder."
        )

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Invalid JSON in {manifest_path}: {e}") from e
    raw.pop("_comment", None)
    data = {**_DEFAULT_MANIFEST, **raw}

    # Path-resolution mode:
    # - If the manifest lives in ANY central manifests/ dir (SCRIPT_DIR or BUNDLE_DIR)
    #   → paths are TTRPG-root-relative
    # - Else (legacy: manifest in a campaign folder) → paths are manifest-folder-relative
    central_dirs = {d.resolve() for d in _manifest_search_dirs()}
    is_central_manifest = manifest_path.parent.resolve() in central_dirs
    if is_central_manifest:
        # Walk up from SCRIPT_DIR (where the .exe lives) — never from BUNDLE_DIR
        # which is a temp extraction folder with no TTRPG context above it.
        ttrpg_root = _find_ttrpg_root(SCRIPT_DIR)
        if ttrpg_root is None:
            raise SystemExit(
                f"Cannot find TTRPG root (no realm_lore_registry.json found upward from {SCRIPT_DIR}).\n"
                f"Place the .exe inside or beside the TTRPG repo so it can find shared lore files."
            )
        resolution_root = ttrpg_root
    else:
        resolution_root = legacy_root or manifest_path.parent

    return _build_config(data, resolution_root)


def _build_config(data: dict, resolution_root: Path) -> CampaignConfig:
    """Build a CampaignConfig by resolving manifest paths against `resolution_root`."""
    def _resolve(p: str) -> Path:
        path = Path(p)
        if path.is_absolute():
            return path.resolve()
        return (resolution_root / path).resolve()

    eng = data.get("engine_path", ".")
    engine_dir = _resolve(eng) if eng not in (None, ".", "") else resolution_root

    return CampaignConfig(
        root=resolution_root,
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

COMBAT_KEYWORDS = {"combat", "battle", "fight", "attack", "engaging", "ambush", "assault", "skirmish", "fray"}
# Keep this list TIGHT — these only matter when combat is also detected.
# Specific boss names (Lyssa, Broodmother) are intentional; generic words
# ("phase", "climax") are too noisy and dropped. Use events_active[].boss=true
# for the authoritative boss flag.
BOSS_KEYWORDS   = {"boss", "boss fight", "final encounter", "showdown",
                   "lyssa vane", "broodmother"}
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

        # Apply persisted text-scale BEFORE building widgets so the initial
        # render uses the correct size. The label updates after _build_header.
        self._current_scale = self._load_scale()
        try:
            ctk.set_widget_scaling(self._current_scale)
        except Exception:
            pass

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

        # Sync the scale label to the loaded value (the label was created in _build_header).
        if hasattr(self, "lbl_scale"):
            self.lbl_scale.configure(text=f"{int(self._current_scale * 100)}%")

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
                try:
                    self._music_map_mtime = os.path.getmtime(mp)
                except Exception:
                    self._music_map_mtime = 0.0
            except Exception:
                pass
        else:
            self._music_map_mtime = 0.0

    @staticmethod
    def _theme_tracks(value):
        """Normalize a character_themes value to a list of track filenames.
        Backwards-compat: legacy entries are flat lists; new entries are dicts
        with a 'tracks' field (and optional 'fire_on_skills')."""
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            t = value.get("tracks")
            return t if isinstance(t, list) else []
        return []

    @staticmethod
    def _theme_fire_on_skills(value):
        """Return the list of skill keywords that should fire this theme."""
        if isinstance(value, dict):
            s = value.get("fire_on_skills") or []
            return [str(x).lower() for x in s if isinstance(x, str)]
        return []

    def _resolve_track(self, location=None, context=None, character=None):
        """Pick a candidate track from the music_map for the given signal.
        Resolution order: context → character → location.
        Location matching: exact key first, then per-comma-segment fuzzy match
        against any map key (so "Sunken Playhouse causeway, ~100 ft from
        proscenium pillar" matches "Sunken Playhouse" by first segment)."""
        mm = self._music_map
        candidates = []
        if context and context in mm.get("contexts", {}):
            candidates = mm["contexts"][context]
        elif character and character in mm.get("character_themes", {}):
            candidates = self._theme_tracks(mm["character_themes"][character])
        elif location:
            is_night = self.engine and (self.engine.hour >= 21 or self.engine.hour < 6)
            mm_locations = mm.get("locations", {})
            loc_data = mm_locations.get(location)
            if not loc_data:
                # Split on commas/em-dashes to try sub-segments first.
                # Cookie's location is e.g. "Sunken Playhouse causeway, ~100 ft from proscenium pillar, marsh approach".
                # We want "Sunken Playhouse" (first segment) to match before any later substring search.
                segments = [s.strip() for s in re.split(r"[,—–]", location) if s.strip()]
                # Score each map key by how well it matches any segment.
                # Prefer earlier-segment matches and longer-key matches (more specific).
                best = None
                best_score = -1
                for key in mm_locations:
                    key_lower = key.lower()
                    for seg_idx, seg in enumerate(segments):
                        seg_lower = seg.lower()
                        if key_lower in seg_lower or seg_lower in key_lower:
                            # Score: first-segment match beats later, longer key beats shorter.
                            score = (10 if seg_idx == 0 else 5) + len(key_lower)
                            if score > best_score:
                                best_score = score
                                best = key
                if best:
                    loc_data = mm_locations[best]
            if loc_data:
                time_key = "night" if is_night and "night" in loc_data else "day"
                candidates = loc_data.get(time_key, loc_data.get("day", []))
        if not candidates:
            return None
        full = self.config.music_dir / random.choice(candidates)
        return str(full) if full.exists() else None

    # ------------------------------------------------------------------
    def _is_in_combat(self) -> bool:
        """True if engine indicates an active combat encounter — checks
        events_active dict (engine-canonical) plus story_beat keyword fallback."""
        e = self.engine
        if not e:
            return False
        # Source 1: events_active engine field — combat encounters get tagged here.
        for ev in (getattr(e, "events_active", None) or {}).values():
            if not isinstance(ev, dict):
                continue
            if str(ev.get("type", "")).lower() in ("combat", "battle", "encounter"):
                if str(ev.get("status", "")).lower() in ("active", "running", "in progress", "ongoing"):
                    return True
        # Source 2: story_beat keyword fallback.
        beat = (getattr(e, "story_beat", "") or "").lower()
        return any(kw in beat for kw in COMBAT_KEYWORDS)

    def _is_boss_combat(self) -> bool:
        """True if the active combat is a boss encounter — checks events_active
        for an explicit `boss=true` flag, then falls back to story_beat keywords."""
        e = self.engine
        if not e:
            return False
        for ev in (getattr(e, "events_active", None) or {}).values():
            if not isinstance(ev, dict):
                continue
            if ev.get("boss") is True or str(ev.get("kind", "")).lower() == "boss":
                return True
        beat = (getattr(e, "story_beat", "") or "").lower()
        return any(kw in beat for kw in BOSS_KEYWORDS)

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
        """Reactive music selection. Priority:
          1. Boss combat → boss_combat context (Origin of the Last Name)
          2. Regular combat → combat context (Smile in the Fire)
          3. Character theme (if scene is dominated by a tracked character)
          4. Inn / shop / blacksmith context detection
          5. Location-based ambient (random pick on every change)

        Triggers on either location change OR story_beat change OR
        events_active change. Same-input return-early prevents spam."""
        if not self._music_enabled or not self.engine:
            return

        e = self.engine
        loc = e.location or ""
        loc_lower = loc.lower()
        beat = (e.story_beat or "").lower()

        # Build a combined fingerprint so any of (location, beat, active events)
        # changing triggers a re-resolve. Without active-events in the fingerprint,
        # combat starting/ending wouldn't trigger a music change.
        events_fp = repr(sorted((getattr(e, "events_active", None) or {}).keys()))
        cur_fp = (loc, e.story_beat, events_fp)
        last_fp = getattr(self, "_last_music_fp", None)
        self._last_music_fp = cur_fp
        self._last_location = loc
        self._last_story_beat = e.story_beat
        if last_fp == cur_fp:
            return

        # ---- 1/2. Combat (boss takes priority) ----
        # Boss music ONLY plays during active combat — a story_beat that mentions
        # Lyssa in passing must not trigger boss music outside a fight.
        if self._is_in_combat():
            if self._is_boss_combat():
                track = self._resolve_track(context="boss_combat")
                if track:
                    self._play_music(track)
                    return
                # Fallback to regular combat if boss_combat context missing/empty.
            track = self._resolve_track(context="combat")
            if track:
                self._play_music(track)
                return

        # ---- 3. Character themes ----
        # Three sub-rules in priority order:
        #   3a. PC's OWN theme fires when story_beat mentions a configured
        #       skill (e.g. Cookie's theme fires on "persuasion"). This is
        #       the dedicated mechanism for "intense moment, focus on PC".
        #   3b. OTHER character's theme fires when their name is in story_beat
        #       (NPC scene, cross-campaign appearance).
        #   3c. PC's own NAME is intentionally NOT auto-matched — it would
        #       hijack every scene, since the PC's name is in story_beat
        #       almost constantly.
        char_themes = self._music_map.get("character_themes", {})
        pc_name = (getattr(e, "char_name", "") or "").lower()

        # 3a. PC's theme via skill match
        if pc_name and pc_name in {k.lower() for k in char_themes.keys()}:
            # Find the canonical key (case-preserving lookup)
            pc_key = next((k for k in char_themes if k.lower() == pc_name), None)
            if pc_key:
                fire_skills = self._theme_fire_on_skills(char_themes[pc_key])
                if any(skill in beat for skill in fire_skills):
                    track = self._resolve_track(character=pc_key)
                    if track:
                        self._play_music(track)
                        return

        # 3b. Other character's theme via name-in-beat match
        for char_name in char_themes:
            if char_name.lower() == pc_name:
                continue
            if char_name.lower() in beat:
                track = self._resolve_track(character=char_name)
                if track:
                    self._play_music(track)
                    return

        # ---- 4. Inn / shop / blacksmith ----
        if any(kw in loc_lower for kw in INN_KEYWORDS):
            ctx = "inn_evening" if e.hour >= 18 else "inn_morning"
            track = self._resolve_track(context=ctx)
            if track:
                self._play_music(track)
                return

        if any(kw in loc_lower for kw in SHOP_KEYWORDS):
            track = self._resolve_track(context="shop")
            if track:
                self._play_music(track)
                return

        if any(kw in loc_lower for kw in SMITH_KEYWORDS):
            track = self._resolve_track(context="blacksmith")
            if track:
                self._play_music(track)
                return

        # ---- 5. Location-based ambient (random pick from map) ----
        track = self._resolve_track(location=loc)
        if track:
            self._play_music(track)
            return

        # ---- 6. Ambient fallback — random character theme ----
        # When no location-key matches, fall back to a random character theme
        # from anywhere in the map. Themes are well-produced pieces in this
        # world's sound palette; sprinkling them in keeps silence at bay and
        # adds variety. Skip the PC's own theme so it stays reserved.
        all_themes = []
        for char_name, value in (self._music_map.get("character_themes") or {}).items():
            if char_name.lower() == pc_name:
                continue
            all_themes.extend(self._theme_tracks(value))
        if all_themes:
            pick = random.choice(all_themes)
            full = self.config.music_dir / pick
            if full.exists():
                self._play_music(str(full))

    # ------------------------------------------------------------------
    # File watcher — polls kenji_state.json for changes
    # ------------------------------------------------------------------
    def _poll_state(self):
        try:
            # Hot-reload music_map if it changed on disk
            try:
                mp = self.config.music_map
                if mp.exists():
                    mm_mtime = os.path.getmtime(mp)
                    if mm_mtime != getattr(self, "_music_map_mtime", 0.0):
                        self._load_music_map()
                        # Force re-resolve on next _react_music call
                        self._last_location = ""
                        self._last_story_beat = ""
                        self._react_music()
            except Exception:
                pass

            mtime = os.path.getmtime(self.config.state_file)
            if mtime != self._last_mtime:
                self._last_mtime = mtime
                self._load_engine()
                self.refresh_all()
                self._react_music()
                self._refresh_now_playing()

            # Play-mode response-file watcher.
            # When dev mode is active and we're awaiting a response, watch
            # play_response.md next to the state file. If its mtime advances,
            # read it and apply as if it had been pasted from clipboard.
            self._play_check_response_file()
        except Exception:
            pass
        self.after(2000, self._poll_state)

    def _play_check_response_file(self) -> None:
        """Polled from _poll_state. Reads play_response.md if it has been
        modified since we started awaiting; applies it as the response."""
        if not getattr(self, "play_state", None):
            return
        if not self.play_state.dev_mode or self.play_state.dev_stage != "awaiting":
            return
        path = getattr(self, "_play_response_path", None)
        if path is None or not path.exists():
            return
        try:
            mtime = path.stat().st_mtime
        except Exception:
            return
        if mtime <= getattr(self, "_play_response_mtime", 0.0):
            return
        # File has been modified since we began awaiting — read and apply.
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception as e:
            self._play_append_narrator(f"[error: could not read play_response.md — {e}]\n")
            return
        if not text:
            return
        self._play_response_mtime = mtime
        self._play_apply_response(text, source="play_response.md")

    # ------------------------------------------------------------------
    # Engine loader
    # ------------------------------------------------------------------
    def _load_engine(self):
        # Pre-check: if the state file genuinely isn't on disk, show a helpful
        # error instead of a Python traceback. This is the "user double-clicked
        # the .exe but didn't put a campaign next to it" path.
        if not Path(self.config.state_file).exists():
            try:
                from tkinter import messagebox
                messagebox.showerror(
                    "Campaign state file not found",
                    f"Could not find the campaign state file:\n\n"
                    f"  {self.config.state_file}\n\n"
                    f"To fix:\n"
                    f"  1. Place a character_world_state.json (or kenji_state.json) "
                    f"in a 'Game init files' folder next to this .exe\n"
                    f"  2. Or run from command line with --campaign \"<path-to-campaign-folder>\"\n"
                    f"  3. Or run generate_starter_campaign.py to create a new character first\n\n"
                    f"See QUICKSTART.md in the repo for the full setup guide."
                )
            except Exception:
                # tkinter messagebox not available — fall back to print-and-die
                print(f"FATAL: state file not found: {self.config.state_file}", file=sys.stderr)
            sys.exit(2)
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

        # Text-size controls. Three small buttons: A-, %, A+. Customtkinter's
        # set_widget_scaling() rescales every CTk widget at once. Scale is
        # persisted next to the .exe so it survives restarts.
        ctk.CTkButton(hdr, text="A+", width=28, height=28, fg_color=BG_CARD,
                       hover_color=GOLD_DIM, text_color=GOLD, font=FONT_SMALL,
                       command=lambda: self._adjust_scale(+0.1)
                       ).pack(side="right", padx=2)
        self.lbl_scale = ctk.CTkLabel(hdr, text="100%", font=FONT_SMALL,
                                       text_color=TEXT_DIM, width=42)
        self.lbl_scale.pack(side="right", padx=2)
        ctk.CTkButton(hdr, text="A-", width=28, height=28, fg_color=BG_CARD,
                       hover_color=GOLD_DIM, text_color=GOLD, font=FONT_SMALL,
                       command=lambda: self._adjust_scale(-0.1)
                       ).pack(side="right", padx=2)
        ctk.CTkButton(hdr, text="■", width=28, height=28, fg_color=BG_CARD,
                       hover_color=RED, text_color=TEXT, font=FONT_SMALL,
                       command=self._stop_music).pack(side="right", padx=2)
        self.lbl_now_playing = ctk.CTkLabel(hdr, text="", font=FONT_SMALL, text_color=TEXT_DIM)
        self.lbl_now_playing.pack(side="right", padx=8)

    # ------------------------------------------------------------------
    # Text-scale persistence
    # ------------------------------------------------------------------
    @property
    def _scale_path(self) -> Path:
        """Settings file path — sits next to the .exe / kenji_gui.py."""
        return SCRIPT_DIR / ".dashboard_scale"

    def _load_scale(self) -> float:
        """Return saved scale or 1.0. Clamped to [0.7, 1.6]."""
        try:
            txt = self._scale_path.read_text(encoding="utf-8").strip()
            v = float(txt)
            return max(0.7, min(1.6, v))
        except Exception:
            return 1.0

    def _save_scale(self, scale: float) -> None:
        try:
            self._scale_path.write_text(f"{scale:.2f}\n", encoding="utf-8")
        except Exception:
            pass   # not fatal — scale just won't persist

    def _apply_scale(self, scale: float) -> None:
        """Apply a scale factor to all CTk widgets via the global scaling
        manager. Updates the % indicator label."""
        scale = max(0.7, min(1.6, round(scale, 2)))
        self._current_scale = scale
        try:
            ctk.set_widget_scaling(scale)
        except Exception:
            pass
        if hasattr(self, "lbl_scale"):
            self.lbl_scale.configure(text=f"{int(scale * 100)}%")

    def _adjust_scale(self, delta: float) -> None:
        """Increment / decrement the scale and persist."""
        cur = getattr(self, "_current_scale", 1.0)
        new = max(0.7, min(1.6, round(cur + delta, 2)))
        self._apply_scale(new)
        self._save_scale(new)

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
        """Lean character panel: HP/AC/SpellSlots/Currency/Meals — the at-a-glance
        vitals only. Detailed sheet info (conditions, ability scores, skills,
        spells, class features, perks) lives in the Status tab on the right."""
        left = ctk.CTkScrollableFrame(parent, fg_color=BG_PANEL, width=240, corner_radius=8,
                                       label_text="CHARACTER", label_font=FONT_LABEL,
                                       label_fg_color=BG_CARD, label_text_color=GOLD)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 4))

        # HP bar
        hp_frame = ctk.CTkFrame(left, fg_color="transparent")
        hp_frame.pack(fill="x", padx=4, pady=(4, 2))
        ctk.CTkLabel(hp_frame, text="HP", font=FONT_LABEL, text_color=GOLD).pack(anchor="w")
        self.hp_bar = ctk.CTkProgressBar(hp_frame, height=18, corner_radius=4)
        self.hp_bar.pack(fill="x", pady=2)
        self.lbl_hp = ctk.CTkLabel(hp_frame, text="", font=FONT_BODY, text_color=TEXT)
        self.lbl_hp.pack(anchor="w")

        # AC
        self.lbl_ac = ctk.CTkLabel(left, text="", font=FONT_LABEL, text_color=TEXT)
        self.lbl_ac.pack(anchor="w", padx=8, pady=(2, 6))

        # Spell slots — gated. Built always, but the header label and slot frame
        # both pack_forget() at refresh if the engine has no slots (non-caster class).
        self.slot_header = ctk.CTkLabel(left, text="SPELL SLOTS", font=FONT_LABEL, text_color=GOLD)
        self.slot_header.pack(anchor="w", padx=8, pady=(6, 2))
        self.slot_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.slot_frame.pack(fill="x", padx=4)

        # Currency + Meals
        ctk.CTkLabel(left, text="CURRENCY", font=FONT_LABEL, text_color=GOLD).pack(anchor="w", padx=8, pady=(10, 2))
        self.lbl_currency = ctk.CTkLabel(left, text="", font=FONT_BODY, text_color=TEXT, justify="left")
        self.lbl_currency.pack(anchor="w", padx=12)
        self.lbl_meals = ctk.CTkLabel(left, text="", font=FONT_BODY, text_color=TEXT)
        self.lbl_meals.pack(anchor="w", padx=12, pady=(2, 4))
        self.lbl_meal_status = ctk.CTkLabel(left, text="", font=FONT_SMALL, text_color=TEXT_DIM)
        self.lbl_meal_status.pack(anchor="w", padx=12, pady=(0, 6))

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

        for name in ("Play", "Status", "Inventory", "World", "Party", "Schedule", "Narrative"):
            tab = self.tabs.add(name)
            if name == "Play":
                # The Play tab gets a custom layout: narrator output (scrolling
                # textbox) + 3 option buttons + custom input row.
                self._build_play_tab(tab)
            else:
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
        # e.hour can be a float (half-hour granularity), so render h:mm.
        _h = float(e.hour)
        _hh = int(_h)
        _mm = int(round((_h - _hh) * 60))
        if _mm == 60:
            _hh += 1
            _mm = 0
        self.lbl_time.configure(text=f"Day {e.day}  {_hh:02d}:{_mm:02d} — {e.time_of_day()}")
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

        # ---- Spell Slots ----
        # Gate the section: only display if the class actually uses slots.
        # We treat any non-empty spell_slots dict (with at least one slot defined)
        # as "this is a spell-slot caster". Non-casters (Fighters, Monks without
        # ki, etc.) have empty spell_slots and the entire section hides.
        # Filter out meta keys (anything starting with "_" like "_comment")
        # before iterating; those aren't actual spell levels.
        slots_dict_raw = getattr(e, "spell_slots", None) or {}
        slots_dict = {k: v for k, v in slots_dict_raw.items() if not str(k).startswith("_")}
        has_slots = any(
            (isinstance(v, (list, tuple)) and len(v) >= 2 and v[1] > 0)
            or (isinstance(v, dict) and v.get("max", 0) > 0)
            or (isinstance(v, (int, float)) and v > 0)
            for v in slots_dict.values()
        )

        for w in self.slot_frame.winfo_children():
            w.destroy()

        if has_slots:
            self.slot_header.pack(anchor="w", padx=8, pady=(6, 2))
            self.slot_frame.pack(fill="x", padx=4)

            def _slot_level_int(k):
                try:
                    return int(k)
                except (ValueError, TypeError):
                    return 999

            for level in sorted(slots_dict.keys(), key=_slot_level_int):
                v = slots_dict[level]
                # Coerce slot value to (cur, mx) tuple regardless of input shape.
                if isinstance(v, (list, tuple)) and len(v) >= 2:
                    cur, mx = int(v[0]), int(v[1])
                elif isinstance(v, dict):
                    cur = int(v.get("current", v.get("cur", 0)))
                    mx = int(v.get("max", 0))
                else:
                    cur = int(v) if isinstance(v, (int, float)) else 0
                    mx = cur
                if mx <= 0:
                    continue
                row = ctk.CTkFrame(self.slot_frame, fg_color="transparent")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=f"L{level}", width=30, font=FONT_SMALL, text_color=TEXT).pack(side="left")
                ctk.CTkLabel(row, text=f"{cur}/{mx}", width=45, font=FONT_BODY, text_color=TEXT).pack(side="left", padx=4)
                bar = ctk.CTkProgressBar(row, width=100, height=10, corner_radius=3)
                bar.set(cur / max(mx, 1))
                bar.configure(progress_color=BLUE)
                bar.pack(side="left", padx=4)
        else:
            # Non-caster — hide the whole section.
            self.slot_header.pack_forget()
            self.slot_frame.pack_forget()

        self.lbl_currency.configure(text=f"{e.gold} GP  |  {e.silver} SP  |  {e.copper} CP")
        self.lbl_meals.configure(text=f"Meals: {e.meals}")
        self.lbl_meal_status.configure(text=e.meal_status())

        self._refresh_status_tab()
        self._refresh_inventory_tab()
        self._refresh_world_tab()
        self._refresh_party_tab()
        self._refresh_schedule_tab()
        self._refresh_narrative_tab()
        self._refresh_now_playing()
        self._apply_window_title_from_engine()

    # ------------------------------------------------------------------
    # Tab refresh helpers
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Play tab — AI narrator runtime
    # ------------------------------------------------------------------
    def _build_play_tab(self, tab):
        """Custom layout for the Play tab. Narrator output dominates the top;
        bottom strip has three option buttons + a custom-input row + Send."""
        # Narrator output — scrollable text box, takes most of the tab.
        self.play_narrator = ctk.CTkTextbox(
            tab, fg_color=BG_CARD, text_color=TEXT,
            font=FONT_BODY, wrap="word", state="disabled",
        )
        self.play_narrator.pack(fill="both", expand=True, padx=4, pady=(4, 2))

        # Bottom interaction bar
        bar = ctk.CTkFrame(tab, fg_color=BG_PANEL, corner_radius=6)
        bar.pack(fill="x", padx=4, pady=(2, 4))

        # Three suggested-action options as click-able frame+label widgets.
        # Using CTkButton would truncate long option text — CTkLabel inside a
        # bound frame supports `wraplength` so multi-line options render fully.
        self.play_option_btns = []
        for i in range(3):
            row = ctk.CTkFrame(bar, fg_color=BG_CARD, corner_radius=4)
            row.pack(fill="x", padx=6, pady=2)
            label = ctk.CTkLabel(
                row, text=f"Option {i+1}",
                font=FONT_BODY, text_color=TEXT_DIM,
                wraplength=700, justify="left", anchor="w",
                cursor="arrow",   # default cursor when disabled
            )
            label.pack(fill="x", padx=10, pady=8)

            # Dynamic wrap — resize wraplength to match the row's rendered
            # width so labels reflow if the window grows or shrinks.
            def _on_resize(ev, lab=label):
                w = max(200, ev.width - 28)
                lab.configure(wraplength=w)
            row.bind("<Configure>", _on_resize)

            # Track each option's interactive state — disabled by default until
            # _play_set_options populates real text.
            opt_state = {"frame": row, "label": label, "idx": i, "enabled": False}
            self.play_option_btns.append(opt_state)

            def _on_click(_ev=None, idx=i):
                if not self.play_option_btns[idx]["enabled"]:
                    return
                self._play_send_option(idx)
            def _on_enter(_ev=None, idx=i):
                if self.play_option_btns[idx]["enabled"]:
                    self.play_option_btns[idx]["frame"].configure(fg_color=GOLD_DIM)
            def _on_leave(_ev=None, idx=i):
                if self.play_option_btns[idx]["enabled"]:
                    self.play_option_btns[idx]["frame"].configure(fg_color=BG_CARD)

            row.bind("<Button-1>", _on_click)
            label.bind("<Button-1>", _on_click)
            row.bind("<Enter>", _on_enter)
            label.bind("<Enter>", _on_enter)
            row.bind("<Leave>", _on_leave)
            label.bind("<Leave>", _on_leave)

        # Custom-input row (Entry + Send)
        custom_row = ctk.CTkFrame(bar, fg_color="transparent")
        custom_row.pack(fill="x", padx=6, pady=(4, 2))
        self.play_input = ctk.CTkEntry(
            custom_row, placeholder_text="Or type your own action and press Enter…",
            fg_color=BG_CARD, text_color=TEXT, font=FONT_BODY,
        )
        self.play_input.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.play_input.bind("<Return>", lambda ev: self._play_send_custom())
        self.play_send_btn = ctk.CTkButton(
            custom_row, text="Send", width=140, fg_color=GOLD_DIM, hover_color=GOLD,
            text_color=BG_DARK, font=FONT_LABEL,
            command=self._play_send_custom,
        )
        self.play_send_btn.pack(side="right")

        # Initial state: PlayState lives on the dashboard for the session.
        # Lazy-imported here so the rest of the GUI works without anthropic SDK.
        from play_engine import PlayState
        self.play_state = PlayState()

        # Dev-mode toggle row — bypass the API and route through Claude Desktop.
        # Default-on if ANTHROPIC_API_KEY is unset (so the user isn't surprised
        # by a key-required error on first Send).
        toggle_row = ctk.CTkFrame(bar, fg_color="transparent")
        toggle_row.pack(fill="x", padx=6, pady=(0, 6))
        self.play_devmode_var = tk.BooleanVar(value=self.play_state.dev_mode)
        self.play_devmode_chk = ctk.CTkCheckBox(
            toggle_row,
            text="Dev mode (use Claude Desktop via clipboard — no API cost)",
            variable=self.play_devmode_var,
            font=FONT_SMALL, text_color=TEXT_DIM,
            command=self._play_toggle_dev_mode,
        )
        self.play_devmode_chk.pack(side="left", padx=2)

        # Sync the Send button label to the initial mode/stage.
        self._play_update_send_button()

        if self.play_state.dev_mode:
            welcome = (
                "Welcome to the Play tab — DEV MODE.\n\n"
                "No ANTHROPIC_API_KEY detected (or you toggled dev mode on), so "
                "the dashboard routes turns through your Claude Desktop instead "
                "of the API.\n\n"
                "WORKFLOW each turn:\n"
                "  1. Type an action below (or click a suggestion when populated) "
                "and press Enter.\n"
                "  2. Click 'Copy Prompt → Clipboard'. Paste it into Claude Desktop.\n"
                "  3. Claude Desktop responds as the DM.\n"
                "  4. Select Claude's full response, copy it.\n"
                "  5. Click '← Paste Response from Clipboard'. Narrative renders, "
                "buttons populate."
            )
        else:
            welcome = (
                "Welcome to the Play tab.\n\n"
                "Type your first action below and press Enter. Three suggested "
                "next-actions will appear after the narrator responds.\n\n"
                "Tip: enable 'Dev mode' below to bypass the API and route turns "
                "through your Claude Desktop via clipboard."
            )
        self._play_set_narrator(welcome)

    def _play_toggle_dev_mode(self):
        """Sync the toggle into PlayState and refresh the Send button label."""
        self.play_state.dev_mode = bool(self.play_devmode_var.get())
        # Reset the dev-stage so a stale "awaiting" doesn't carry across modes.
        self.play_state.dev_stage = "ready"
        self.play_state.pending_action = ""
        self._play_update_send_button()

    def _play_update_send_button(self):
        """Refresh Send button label based on mode + stage."""
        if not getattr(self, "play_send_btn", None):
            return
        if self.play_state.dev_mode:
            if self.play_state.dev_stage == "awaiting":
                self.play_send_btn.configure(text="← Paste Response")
            else:
                self.play_send_btn.configure(text="Copy Prompt →")
        else:
            self.play_send_btn.configure(text="Send")

    def _play_set_narrator(self, text: str) -> None:
        """Replace narrator pane contents."""
        tb = self.play_narrator
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")
        tb.see("end")

    def _play_append_narrator(self, text: str) -> None:
        """Append (used for streaming tokens)."""
        tb = self.play_narrator
        tb.configure(state="normal")
        tb.insert("end", text)
        tb.configure(state="disabled")
        tb.see("end")

    def _play_set_options(self, options: list) -> None:
        """Repopulate the three option widgets — frame+label rather than buttons,
        so multi-line option text wraps cleanly."""
        for i, opt in enumerate(self.play_option_btns):
            label = opt["label"]
            frame = opt["frame"]
            if i < len(options) and options[i]:
                label.configure(text=f"{i+1}. {options[i]}", text_color=TEXT, cursor="hand2")
                frame.configure(fg_color=BG_CARD, cursor="hand2")
                opt["enabled"] = True
            else:
                label.configure(text=f"Option {i+1}", text_color=TEXT_DIM, cursor="arrow")
                frame.configure(fg_color=BG_CARD, cursor="arrow")
                opt["enabled"] = False

    def _play_set_busy(self, busy: bool) -> None:
        """Disable inputs while a turn is streaming."""
        state = "disabled" if busy else "normal"
        if busy:
            # Disable all option rows during streaming — clicks ignored.
            for opt in self.play_option_btns:
                opt["enabled"] = False
                opt["frame"].configure(fg_color=BG_CARD, cursor="arrow")
                opt["label"].configure(text_color=TEXT_DIM, cursor="arrow")
        # else: option rows are re-enabled by _play_set_options after the
        # response is parsed; we don't touch them here on the way out.
        self.play_input.configure(state=state)
        self.play_send_btn.configure(state=state)

    def _play_dev_paste_response(self) -> None:
        """Read response from clipboard, hand off to _play_apply_response."""
        try:
            response_text = self.clipboard_get()
        except Exception as e:
            self._play_append_narrator(
                f"[error: could not read clipboard — {e}]\n"
                "Make sure the response is copied (Ctrl+C) before clicking.\n"
            )
            return
        if not response_text or not response_text.strip():
            self._play_append_narrator(
                "[clipboard is empty — copy the response and try again]\n"
            )
            return
        self._play_apply_response(response_text, source="clipboard")

    def _play_apply_response(self, response_text: str, source: str = "?") -> None:
        """Parse a response (from clipboard OR play_response.md) and render
        narrative + options. Resets dev-stage to 'ready'. Idempotent — safe
        to call from the file-watcher.

        After applying, clears play_response.md so the same response cannot
        be re-applied if the file mtime ticks again. Empty file = idle state."""
        from play_engine import parse_response, Turn
        parsed = parse_response(response_text)
        narrative = parsed.get("narrative", "").strip()
        options = parsed.get("options", []) or []

        if narrative:
            self._play_append_narrator(narrative + "\n\n")
        else:
            self._play_append_narrator(
                f"[no narrative parsed from {source} — make sure the full "
                f"response is present, including the '---OPTIONS---' line]\n\n"
            )

        new_turn = Turn(
            player_action=self.play_state.pending_action,
            narrator=narrative or response_text,
            options=options,
        )
        self.play_state.append_turn(new_turn)
        self.play_state.current_options = options
        self.play_state.pending_action = ""
        self.play_state.dev_stage = "ready"

        self._play_set_options(options)
        self._play_update_send_button()
        self.play_input.focus_set()

        # Clear play_response.md so it can't be re-applied next poll cycle.
        # The empty file represents the idle state between turns.
        path = getattr(self, "_play_response_path", None)
        if path is not None:
            try:
                path.write_text("", encoding="utf-8")
                self._play_response_mtime = path.stat().st_mtime
            except Exception:
                pass

    def _play_send_option(self, idx: int) -> None:
        """Player clicked one of the three suggestion buttons."""
        # In dev mode, if we're awaiting a response paste, the button click
        # means "paste the response" — not "send a new option". Catch that.
        if self.play_state.dev_mode and self.play_state.dev_stage == "awaiting":
            self._play_dev_paste_response()
            return
        opts = self.play_state.current_options
        if idx < 0 or idx >= len(opts):
            return
        self._play_send_text(opts[idx])

    def _play_send_custom(self) -> None:
        """Send button / Enter key. In API mode: stream a turn. In dev mode:
        either copy the prompt to clipboard (stage='ready') or read the
        response from clipboard (stage='awaiting')."""
        if self.play_state.dev_mode and self.play_state.dev_stage == "awaiting":
            self._play_dev_paste_response()
            return

        text = self.play_input.get().strip()
        if not text:
            return
        self.play_input.delete(0, "end")
        self._play_send_text(text)

    def _play_send_text(self, action_text: str) -> None:
        """Common path: marshal a player action into a turn.
        Branches between API streaming (live) and dev-mode clipboard (manual)."""
        # Echo the player's action above the upcoming narrator response.
        sep = "\n\n" if self.play_narrator.get("1.0", "end").strip() else ""
        self._play_append_narrator(f"{sep}> {action_text}\n\n")

        # Re-load the latest state from disk so any out-of-band edits
        # (_dm_turn.py commands, manual JSON edits) are reflected.
        try:
            full_state = json.loads(self.config.state_file.read_text(encoding="utf-8"))
        except Exception as e:
            self._play_append_narrator(f"\n[error: could not read state file — {e}]\n")
            return

        # Adventure summary for the prompt — prefer hand-written, fall back
        # to top-level _narrative_summary already loaded onto the engine.
        narrative_summary = ""
        if hasattr(self, "engine") and self.engine is not None:
            ns = getattr(self.engine, "_narrative_summary", "")
            if isinstance(ns, list):
                narrative_summary = "\n\n".join(ns)
            elif isinstance(ns, str):
                narrative_summary = ns

        # ---- Dev mode: build prompt, write to file (and clipboard), await response ----
        # Two channels for the response:
        #   1. Clipboard (manual paste workflow — Claude Desktop)
        #   2. File `play_response.md` next to the state file (file bridge —
        #      auto-detected and applied when modified). The file channel lets
        #      an external assistant write the response directly with no
        #      copy/paste step. The clipboard channel still works.
        if self.play_state.dev_mode:
            from play_engine import build_dev_prompt
            prompt_text = build_dev_prompt(
                state=full_state,
                history=self.play_state.history,
                player_action=action_text,
                narrative_summary=narrative_summary,
            )

            # Write the prompt to a file so an external editor (Claude Code, vim,
            # or another assistant) can read it without clipboard.
            prompt_path = self.config.state_file.parent / "play_prompt.md"
            try:
                prompt_path.write_text(prompt_text, encoding="utf-8")
            except Exception as e:
                self._play_append_narrator(f"[warning: could not write prompt file — {e}]\n")

            # Also push to the clipboard for the manual paste-into-Claude-Desktop
            # workflow. Either channel can deliver the response.
            try:
                self.clipboard_clear()
                self.clipboard_append(prompt_text)
                self.update()
            except Exception:
                pass   # file channel still works even if clipboard fails

            # Initialize the response-file watcher mtime baseline so we don't
            # re-read a stale response file from a previous turn.
            response_path = self.config.state_file.parent / "play_response.md"
            self._play_response_path = response_path
            try:
                self._play_response_mtime = (
                    response_path.stat().st_mtime if response_path.exists() else 0.0
                )
            except Exception:
                self._play_response_mtime = 0.0

            self.play_state.pending_action = action_text
            self.play_state.dev_stage = "awaiting"
            self._play_update_send_button()

            self._play_append_narrator(
                f"[Prompt written to play_prompt.md and clipboard "
                f"({len(prompt_text):,} chars). Awaiting response — either "
                f"paste from clipboard, or write to play_response.md and the "
                f"dashboard will auto-apply.]\n\n"
            )
            return

        # ---- API mode: stream a turn live ----
        # Disable inputs while streaming.
        self._play_set_busy(True)
        self.play_state.streaming = True

        from play_engine import stream_turn, Turn
        new_turn = Turn(player_action=action_text)

        # Streaming-thread callbacks marshalled onto the Tk main loop.
        def on_token(tok: str):
            self.after(0, lambda: self._play_append_narrator(tok))
            new_turn.narrator += tok

        def on_complete(parsed: dict):
            def apply():
                # Re-enable buttons / input and populate new options.
                new_turn.narrator = parsed.get("narrative", new_turn.narrator)
                new_turn.options = parsed.get("options", []) or []
                self.play_state.current_options = new_turn.options
                self.play_state.append_turn(new_turn)
                self.play_state.streaming = False
                self._play_set_options(new_turn.options)
                self._play_set_busy(False)
                self.play_input.focus_set()
            self.after(0, apply)

        def on_error(msg: str):
            def apply():
                self._play_append_narrator(f"\n[error]\n{msg}\n")
                self.play_state.streaming = False
                self.play_state.last_error = msg
                self._play_set_busy(False)
            self.after(0, apply)

        stream_turn(
            state=full_state,
            history=self.play_state.history,
            player_action=action_text,
            on_token=on_token,
            on_complete=on_complete,
            on_error=on_error,
            narrative_summary=narrative_summary,
        )

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
        """No-op shim. The detailed character-sheet sections (conditions, ability
        scores, skills, spells, class features, perks) moved off the left panel
        into the Status tab on the right. Kept as a method for any external
        callers that still invoke it; intentionally does nothing now."""
        return

    def _refresh_status_tab(self):
        e = self.engine
        lines = []

        # ---- STATUS (CONDITIONS) ----
        # Only real conditions/buffs go here. Filter out narrative flags
        # ("healthy", "EMBER_CAPPED" — story-state, not gameplay). KEEP real
        # combat statuses like POISONED, PARALYZED, EMBER_NULLIFIED, etc.
        _NARRATIVE_NOISE = {"healthy", "fine", "ok", "okay", "normal"}
        # Explicit denylist — narrative-only flags that look like statuses but
        # aren't gameplay-actionable. Add new ones here as they're identified.
        _NARRATIVE_FLAGS = {"EMBER_CAPPED", "STORY_LOCKED", "CAMPAIGN_PAUSED"}
        real_conditions = []
        for s in (e.statuses or []):
            if not isinstance(s, str):
                continue
            head = s.split("—")[0].strip()
            if head.lower() in _NARRATIVE_NOISE:
                continue
            if head.upper() in _NARRATIVE_FLAGS:
                continue
            real_conditions.append(s)

        lines.append("═══ STATUS (CONDITIONS) ═══")
        if real_conditions or e.buffs:
            for c in real_conditions:
                # Show only the short head before any em-dash explanation.
                short = c.split("—")[0].strip()
                lines.append(f"  • {short}")
            for name, b in (e.buffs or {}).items():
                dur = b.get("duration_hrs", b.get("duration", "?"))
                fx = b.get("effects", "")
                tail = f" — {fx}" if fx else ""
                lines.append(f"  • {name}  ({dur}hr){tail}")
        else:
            lines.append("  No active conditions.")

        # ---- ABILITY SCORES ----
        lines += ["", "═══ ABILITY SCORES ═══"]
        scores = getattr(e, "ability_scores", None) or {}
        if scores:
            order = ("STR", "DEX", "CON", "INT", "WIS", "CHA")

            def _fmt_score(v):
                if isinstance(v, dict):
                    final = v.get("final", v.get("base", "?"))
                    mod = v.get("mod")
                    if mod is None or final == "?":
                        return f"{final}"
                    sign = "+" if (isinstance(mod, (int, float)) and mod >= 0) else ""
                    return f"{final}  ({sign}{mod})"
                return f"{v}"

            for k in order:
                if k in scores:
                    lines.append(f"  {k}  {_fmt_score(scores[k])}")
            for k in sorted(scores.keys()):
                if k not in order:
                    lines.append(f"  {k}  {_fmt_score(scores[k])}")
        else:
            lines.append("  (not configured)")

        # ---- SKILLS ----
        lines += ["", "═══ SKILLS ═══"]
        skills = getattr(e, "skills", None) or {}
        if skills:
            for sk in sorted(k for k in skills.keys() if not k.startswith("_")):
                lines.append(f"  {sk}: {skills[sk]}")
        else:
            lines.append("  (none)")

        # ---- SPELLS (with charges inline) ----
        lines += ["", "═══ SPELLS ═══"]
        known = getattr(e, "known_spells", None) or []
        # Build a charge-lookup for inline display.
        charge_map = {}
        for cname, pair in (getattr(e, "charges", {}) or {}).items():
            try:
                cur, mx = pair[0], pair[1]
                charge_map[cname.lower()] = f"{cur}/{mx}"
            except Exception:
                pass
        # Filter meta keys (e.g. "_comment") before iterating slot levels.
        _slots_raw = getattr(e, "spell_slots", None) or {}
        slots = {k: v for k, v in _slots_raw.items() if not str(k).startswith("_")}
        def _fmt_slot(v):
            """Render a spell-slot entry — handles [cur, max], {current, max}, or int."""
            if isinstance(v, list) and len(v) >= 2:
                return f"{v[0]}/{v[1]}"
            if isinstance(v, dict):
                cur = v.get("current", v.get("cur", "?"))
                mx = v.get("max", "?")
                return f"{cur}/{mx}"
            return str(v)

        if known:
            for sp in known:
                # sp may be a string OR a dict {name, level, charges_key, notes}.
                # Spell-slot-based casting is the standard: each cast consumes one
                # slot of its level. Per-spell uses_per_day is treated as authoring
                # note only and not rendered (see spell_slots widget for daily caps).
                if isinstance(sp, dict):
                    name = sp.get("name", "?")
                    lvl = sp.get("level")
                    notes = sp.get("notes", "")
                    ck = sp.get("charges_key") or name
                    line = f"  • {name}"
                    if lvl is not None:
                        line += f"  (L{lvl})"
                    # Charges still render IF a class has explicit non-slot charges
                    # tracked (e.g., a future class using per-ability uses).
                    if ck.lower() in charge_map:
                        line += f"  [{charge_map[ck.lower()]} uses]"
                    if notes:
                        line += f" — {notes}"
                    lines.append(line)
                else:
                    name = str(sp)
                    line = f"  • {name}"
                    matched = next((v for k, v in charge_map.items() if k in name.lower() or name.lower() in k), None)
                    if matched:
                        line += f"  [{matched} uses]"
                    lines.append(line)
        else:
            lines.append("  (none)")
        if slots:
            def _level_int(k):
                """Coerce slot-level key to int for numeric sort. Cookie's keys are
                strings ('1', '2'); future characters might use ints. Either way
                we want L2 < L10, not lexical 'L10' < 'L2'."""
                try:
                    return int(k)
                except (ValueError, TypeError):
                    return 999
            slot_pairs = []
            for lvl, v in sorted(slots.items(), key=lambda x: _level_int(x[0])):
                rendered = _fmt_slot(v)
                if rendered and rendered != "0/0":
                    slot_pairs.append(f"L{lvl}: {rendered}")
            if slot_pairs:
                lines.append(f"  Slots — {'  '.join(slot_pairs)}")

        # ---- CLASS FEATURES (Dancer-specific only, 1-sentence summary) ----
        # Filter to actual class features by `type`. Ember/perk/quirk entries
        # render under PERKS instead.
        _CLASS_TYPES = {"class", "combat_style", "class_rule", "support_archetype"}
        cf_list = getattr(e, "class_features", None) or []
        class_only = [f for f in cf_list if isinstance(f, dict) and (f.get("type") or "").lower() in _CLASS_TYPES]
        perk_from_cf = [f for f in cf_list if isinstance(f, dict) and (f.get("type") or "").lower() not in _CLASS_TYPES]

        def _summarize(feat: dict) -> str:
            """Return a 1-sentence summary for the feature."""
            if feat.get("summary"):
                return feat["summary"]
            # Fall back to first sentence of description.
            desc = feat.get("description", "") or feat.get("mechanical_effect", "") or ""
            # Split on sentence terminators; first non-empty piece.
            for piece in re.split(r"(?<=[.!?])\s+", desc):
                piece = piece.strip()
                if len(piece) >= 8:
                    return piece if piece.endswith((".", "!", "?")) else piece + "."
            return desc[:120] + ("…" if len(desc) > 120 else "")

        lines += ["", "═══ CLASS FEATURES ═══"]
        if class_only:
            for feat in class_only:
                name = feat.get("name", "?")
                summary = _summarize(feat)
                lines.append(f"  • {name} — {summary}")
        else:
            # Strings (legacy free-form) get rendered as-is.
            string_features = [f for f in cf_list if isinstance(f, str)]
            if string_features:
                for f in string_features:
                    lines.append(f"  • {f}")
            else:
                lines.append("  (none)")

        # ---- PERKS (ACTIVE) ----
        lines += ["", "═══ PERKS (ACTIVE) ═══"]
        rendered_any = False
        for feat in perk_from_cf:
            name = feat.get("name", "?")
            summary = _summarize(feat)
            lines.append(f"  • {name} — {summary}")
            rendered_any = True
        for p in (e.active_perks or []):
            if isinstance(p, dict):
                name = p.get("name", "?")
                # Use _summarize so the `summary` field is honored, falling back
                # to first sentence of effect/description/mechanical_effect.
                # _summarize reads `summary` then `description` then `mechanical_effect`.
                # Provide a temporary feat-shaped dict that aliases `effect` into description.
                feat_shape = dict(p)
                if "description" not in feat_shape and "effect" in feat_shape:
                    feat_shape["description"] = feat_shape["effect"]
                summary = _summarize(feat_shape)
                tail = f" — {summary}" if summary else ""
                lines.append(f"  • {name}{tail}")
            else:
                lines.append(f"  • {p}")
            rendered_any = True
        if not rendered_any:
            lines.append("  (none)")

        # ---- MEAL & EXP ----
        lines += ["", "═══ MEAL & EXP ═══"]
        lines.append(f"  Hours since meal: {e.hours_since_meal}")
        lines.append(f"  {e.meal_status()}")
        # EXP as current/threshold for next level (no thematic cap — synthesized
        # thresholds extend past the table-defined levels).
        try:
            thresholds = e.get_thresholds()
            next_threshold = thresholds.get(e.level + 1)
            if next_threshold:
                remaining = max(0, next_threshold - e.exp)
                lines.append(f"  EXP: {e.exp:,} / {next_threshold:,}  ({remaining:,} to L{e.level + 1})")
            else:
                lines.append(f"  EXP: {e.exp:,}  (no next-level threshold defined)")
        except Exception:
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
        key_npcs = e.get_key_npcs() if hasattr(e, "get_key_npcs") else []
        if key_npcs:
            for npc in key_npcs:
                name = npc.get("name", "?")
                role = npc.get("role", "")
                loc = npc.get("location", "")
                tier = npc.get("_tier", "")
                marker = "★" if tier == "main" else "•"
                desc = " · ".join(x for x in (role, loc) if x)
                lines.append(f"  {marker} {name:18s}  {desc}")
        else:
            lines.append("  (none)")
        lines += ["", "═══ RELATIONSHIPS ═══"]
        rels = e.get_relationships_view() if hasattr(e, "get_relationships_view") else []
        if rels:
            for r in rels[:10]:   # top 10 by abs(score)
                name = r["name"]
                score = r["score"]
                tier = r["tier"]
                last = r.get("last_event", "")
                # Sign-prefix score; show tier; trim last-event to keep line tight
                short = (last[:60] + "…") if last and len(last) > 60 else last
                lines.append(f"  {name:18s}  {score:+d}  ({tier})  {short}")
        else:
            lines.append("  (none)")
        lines += ["", "═══ REPUTATION ═══"]
        if e.reputation:
            for faction, info in e.reputation.items():
                lines.append(f"  {faction}: {info.get('level', '?')} — {info.get('opinion', '?')}")
        else:
            lines.append("  (none)")
        self._set_tb("world", "\n".join(lines))

    def _refresh_party_tab(self):
        """Universal force-composition tab: party, pets, summons, constructs, hegemony.
        Renders only sections the character actually has — no Kenji-specific defaults
        for characters who'll never have a Sorcerer's Hegemony."""
        e = self.engine
        lines = []

        if not e.has_any_force():
            lines.append("  No party, pets, summons, or constructs.")
            lines.append("")
            lines.append("  Allies acquired through play (party contracts, animal companions,")
            lines.append("  spell summons, or built constructs) will appear here.")
            self._set_tb("party", "\n".join(lines))
            return

        # ---- PARTY ----
        party = e.get_party()
        members = party.get("members", []) if party else []
        if members:
            header = "═══ PARTY"
            if party.get("name"):
                header += f" — {party['name']}"
            if party.get("tier"):
                header += f" ({party['tier']})"
            header += " ═══"
            lines.append(header)
            for m in members:
                name = m.get("name", "?")
                role = m.get("role", "")
                cls = m.get("class", "")
                tier = m.get("tier", "")
                status = m.get("status", "active")
                desc_parts = [p for p in (cls, role, tier) if p]
                desc = " · ".join(desc_parts) if desc_parts else ""
                marker = "●" if status == "active" else "○"
                lines.append(f"  {marker} {name:18s}  {desc}")
                if status and status != "active":
                    lines.append(f"    └ status: {status}")
            if party.get("contract"):
                lines.append(f"  Contract: {party['contract']}")
            lines.append("")

        # ---- PETS ----
        pets = e.get_pets()
        if pets:
            lines.append("═══ PETS / COMPANIONS ═══")
            for p in pets:
                name = p.get("name", "?")
                species = p.get("species", "")
                role = p.get("role", "")
                status = p.get("status", "active")
                marker = "●" if status == "active" else "○"
                desc = " · ".join(x for x in (species, role) if x)
                lines.append(f"  {marker} {name:18s}  {desc}")
            lines.append("")

        # ---- SUMMONS ----
        summons = e.get_summons()
        if summons:
            lines.append("═══ ACTIVE SUMMONS ═══")
            for s in summons:
                name = s.get("name", "?")
                src = s.get("source_spell", "")
                dur = s.get("duration", "")
                status = s.get("status", "active")
                marker = "●" if status == "active" else "○"
                desc = " · ".join(x for x in (src, f"dur: {dur}" if dur else "") if x)
                lines.append(f"  {marker} {name:18s}  {desc}")
            lines.append("")

        # ---- FORCE-COMPOSITION CONSTRUCTS (per-character, distinct from hegemony) ----
        force_constructs = e.get_force_constructs()
        if force_constructs:
            lines.append("═══ CONSTRUCTS ═══")
            for c in force_constructs:
                name = c.get("name", "?")
                ctype = c.get("type", "")
                count = c.get("count", 1)
                loc = c.get("location", "")
                status = c.get("status", "active")
                marker = "●" if status == "active" else "○"
                desc = " · ".join(x for x in (ctype, f"x{count}" if count != 1 else "", f"@ {loc}" if loc else "") if x)
                lines.append(f"  {marker} {name:18s}  {desc}")
            lines.append("")

        # ---- HEGEMONY (Kenji-specific empire-scale rollup) ----
        heg = e.get_hegemony()
        if heg and heg.get("active"):
            lines.append("═══ SORCERER'S HEGEMONY ═══")
            lines.append(f"  Total constructs: {e.total_constructs()}")
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
            lines.append("  ── PORTALS ──")
            active = sum(1 for s in e.portals.values() if s == "active")
            lines.append(f"  {active}/{e.portal_max} active")
            for name, status in sorted(e.portals.items()):
                lines.append(f"  {'●' if status == 'active' else '○'} {name}: {status}")
            if e.squads:
                lines += ["", "  ── SQUADS ──"]
                for name, info in sorted(e.squads.items()):
                    icon = "⚔" if info.get("status") == "deployed" else "⌂"
                    lines.append(f"  {icon} {name} (Cpt: {info.get('captain', '?')})")
                    lines.append(f"    {info.get('status', '?')} @ {info.get('location', '?')}")
                    if info.get("mission"):
                        lines.append(f"    Mission: {info['mission']}")
            if e.assets:
                lines += ["", "  ── ASSETS & INCOME ──"]
                if e.golden_age_active:
                    lines.append("  ★ GOLDEN AGE ACTIVE (2x income)")
                for a in e.assets:
                    icon = "✓" if a.get("status") == "active" else "✗"
                    lines.append(f"  {icon} {a.get('name', '?')}: {a.get('display', '')} [{a.get('status', '?')}]")

        self._set_tb("party", "\n".join(lines))

    def _refresh_schedule_tab(self):
        """Schedule = upcoming/active items only. Completed/done/resolved/cancelled
        entries are filtered out — they live in chapter history, not here."""
        e = self.engine
        lines = []
        _DONE_STATUSES = {"DONE", "COMPLETE", "COMPLETED", "RESOLVED", "CANCELLED",
                          "CANCELED", "SKIPPED", "FAILED", "CLOSED"}

        def _is_done(item):
            return str(item.get("status", "")).upper() in _DONE_STATUSES

        # ---- EVENTS (active/upcoming only) ----
        active_events = [ev for ev in (e.events or []) if not _is_done(ev)]
        lines.append("═══ EVENTS ═══")
        if active_events:
            for ev in sorted(active_events, key=lambda x: x.get("day", 999)):
                day = ev.get("day", "?")
                name = ev.get("name", "?")
                pri = ev.get("priority", "MED")
                delta = e.hours_until(day) if isinstance(day, int) else 0
                when = "NOW" if delta <= 0 else (f"{delta}hr" if delta < 24 else f"{delta//24}d {delta%24}hr")
                lines.append(f"  [{pri}] {name} — Day {day} ({when})")
                if ev.get("notes"):
                    lines.append(f"         {ev['notes']}")
        else:
            lines.append("  No upcoming events.")

        # ---- QUESTS (active only) ----
        active_quests = [q for q in (e.quests or []) if not _is_done(q)]
        lines += ["", "═══ QUESTS ═══"]
        if active_quests:
            for q in active_quests:
                lines.append(f"  [{q.get('priority', 'MED')}] {q.get('name', '?')}  [{q.get('status', '?')}]")
                if q.get("notes"):
                    lines.append(f"         {q['notes']}")
        else:
            lines.append("  No active quests.")

        # ---- PENDING CONSEQUENCES (derived: clocks at >=75%) ----
        cons = e.get_active_consequences(warn_threshold=75) if hasattr(e, "get_active_consequences") else []
        lines += ["", "═══ PENDING CONSEQUENCES ═══"]
        if cons:
            for c in cons:
                kind = c.get("kind", "?")
                name = c.get("name", "?")
                prog = c.get("progress")
                marker = "🔥" if kind == "FIRED" else ("⚠" if kind == "IMMINENT" else "•")
                head = f"  {marker} [{kind}] {name}"
                if prog is not None:
                    head += f"  ({prog}%)"
                lines.append(head)
                trig = c.get("trigger", "")
                if trig:
                    lines.append(f"     → {trig}")
        else:
            lines.append("  None pending. (Clocks below 75% live in the World tab.)")

        # ---- FACTION PLOTS (derived: threat_clocks tagged with `faction`) ----
        lines += ["", "═══ FACTION PLOTS ═══"]
        faction_groups = e.get_faction_plots() if hasattr(e, "get_faction_plots") else {}
        # Add legacy org_plots (in-progress) so old data still renders
        for org, p in (e.org_plots or {}).items():
            if isinstance(p, dict) and p.get("progress", 0) < 100 and not _is_done(p):
                entries = faction_groups.setdefault(org, [])
                entries.append({
                    "name": p.get("plot", org),
                    "progress": p.get("progress", 0),
                    "rate": p.get("rate", 0),
                    "description": p.get("description", ""),
                    "next_move": p.get("next_move", ""),
                    "next_move_day": p.get("next_move_day"),
                })
        if faction_groups:
            for faction, plots in sorted(faction_groups.items()):
                lines.append(f"  {faction}")
                for p in sorted(plots, key=lambda x: -x.get("progress", 0)):
                    lines.append(f"    • {p['name']}  ({p['progress']}%, {p.get('rate', 0)}/day)")
                    if p.get("next_move"):
                        d = p.get("next_move_day")
                        nm_tail = f" (Day {d})" if d else ""
                        lines.append(f"        Next: {p['next_move']}{nm_tail}")
        else:
            lines.append("  No active faction plots. (Tag threat_clocks with `faction:` to populate.)")

        # ---- BOSS READINESS (Rule 10) ----
        if hasattr(e, "boss_eligibility"):
            try:
                elig = e.boss_eligibility()
                lines += ["", "═══ BOSS READINESS ═══"]
                marker = "✓" if elig.get("eligible") else "✗"
                lines.append(f"  {marker} {elig.get('reason', '')}")
                last_boss = elig.get("last_boss")
                if last_boss and isinstance(last_boss, dict):
                    bn = last_boss.get("description") or "(unnamed boss)"
                    bd = last_boss.get("day", "?")
                    lines.append(f"     Last boss: {bn[:80]}  (Day {bd})")
            except Exception:
                pass

        # ---- CHARACTER GOALS (open only, optional) ----
        goals = getattr(e, "character_goals", None) or []
        active_goals = [g for g in goals if isinstance(g, dict) and not _is_done(g)]
        if active_goals:
            lines += ["", "═══ CHARACTER GOALS ═══"]
            for g in active_goals:
                gname = g.get("name") or g.get("goal_id") or "?"
                gdesc = g.get("description") or g.get("notes") or ""
                gprog = g.get("progress")
                line = f"  • {gname}"
                if gprog is not None:
                    line += f"  ({gprog}%)"
                if gdesc:
                    short = gdesc.split(".")[0]
                    if len(short) > 100:
                        short = short[:97] + "…"
                    line += f" — {short}"
                lines.append(line)

        self._set_tb("schedule", "\n".join(lines))

    def _refresh_narrative_tab(self):
        """Adventure recap — 3 paragraphs max, sourced from _narrative_summary
        if hand-written, else auto-condensed from _chapter_history. Quick read,
        not a chapter-by-chapter log (that's what _chapter_history is for)."""
        e = self.engine
        lines = []

        # Header — current chapter pointer.
        ch_num = getattr(e, "_chapter_num", None)
        ch_title = getattr(e, "_chapter_title", "") or ""
        ch_status = getattr(e, "_chapter_status", "") or ""
        if ch_num is not None:
            header = f"Chapter {ch_num}"
            if ch_title:
                header += f" — {ch_title}"
            if ch_status:
                header += f"  [{ch_status}]"
            lines.append(f"  {header}")
            lines.append("")

        # Source 1: hand-written narrative summary (preferred — author has
        # already condensed and edited it). Stored as either a single string
        # or a list of paragraph strings.
        summary = getattr(e, "_narrative_summary", "") or ""

        if summary:
            paragraphs = summary if isinstance(summary, list) else [summary]
            # Cap at 3 paragraphs
            paragraphs = [p.strip() for p in paragraphs if p and isinstance(p, str)][:3]
            for i, para in enumerate(paragraphs):
                lines.append(para)
                if i < len(paragraphs) - 1:
                    lines.append("")
        else:
            # Source 2: auto-condense from _chapter_history.
            history = getattr(e, "_chapter_history", None) or []
            if not history:
                lines.append("  No chapter history yet. The adventure summary will")
                lines.append("  appear here once chapters have been written and closed.")
            else:
                # Group chapters into 3 buckets: opening (1/3), middle (1/3), recent (1/3).
                n = len(history)
                if n <= 3:
                    buckets = [[ch] for ch in history]
                else:
                    third = max(1, n // 3)
                    buckets = [
                        history[:third],
                        history[third:2*third],
                        history[2*third:],
                    ]

                paragraph_labels = ["Opening:", "Middle arc:", "Recent:"]
                for label, bucket in zip(paragraph_labels, buckets):
                    if not bucket:
                        continue
                    # Compose a paragraph from the chapter summaries in this bucket.
                    pieces = []
                    for ch in bucket:
                        if not isinstance(ch, dict):
                            continue
                        ch_n = ch.get("chapter", "?")
                        ch_t = ch.get("title", "")
                        ch_s = ch.get("summary", "")
                        # Take only the first sentence of each summary to keep paragraphs short.
                        first = ch_s.split(". ")[0].strip() if ch_s else ""
                        if first and not first.endswith("."):
                            first += "."
                        head = f"Ch{ch_n}"
                        if ch_t:
                            head += f" '{ch_t}'"
                        pieces.append(f"{head}: {first}")
                    if pieces:
                        lines.append(f"  {label}")
                        lines.append("  " + " ".join(pieces))
                        lines.append("")

        self._set_tb("narrative", "\n".join(lines))


# Backward-compatible name for scripts that imported KenjiDashboard
KenjiDashboard = LiveDashboard


def _show_fatal_error(title: str, message: str) -> None:
    """Surface a fatal startup error visibly even under --noconsole.

    Under PyInstaller --noconsole, any uncaught exception or SystemExit
    silently kills the process — the user sees nothing. This puts the
    message in a Tk dialog so failures are debuggable without a console.
    """
    # Always print to stderr too (visible under --console / DEBUG build).
    try:
        print(f"FATAL: {title}\n{message}", file=sys.stderr)
    except Exception:
        pass
    # Best-effort GUI dialog.
    try:
        import tkinter as _tk
        from tkinter import messagebox as _mb
        _root = _tk.Tk()
        _root.withdraw()
        _mb.showerror(title, message)
        _root.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        cfg = _load_campaign_config()
        app = LiveDashboard(cfg)
        app.mainloop()
    except SystemExit as e:
        # SystemExit raised from _load_campaign_config carries the user-facing message.
        msg = str(e) if str(e) else "Unknown startup error."
        _show_fatal_error("Kenji DM Tool — startup error", msg)
        sys.exit(1)
    except Exception:
        import traceback as _tb
        tb = _tb.format_exc()
        _show_fatal_error("Kenji DM Tool — unhandled exception", tb)
        sys.exit(2)
