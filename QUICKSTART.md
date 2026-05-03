# QUICKSTART — TTRPG Kingdom of Ankunyx

5-minute first-run guide. Goal: get you playing or continuing a campaign as fast as possible.

---

## 1. Install Python (one-time, ~2 min)

If you don't have Python 3.10+ already:

- **Windows:** download from https://python.org and check **"Add Python to PATH"** during install.
- **Mac:** `brew install python` or use the official installer.
- **Linux:** `sudo apt install python3 python3-pip` (or your distro equivalent).

Verify:
```bash
python --version    # or python3 --version
# Should print Python 3.10.x or higher
```

## 2. Clone the repo (~30 sec)

```bash
git clone https://github.com/charlesnmcdowell/ttrpg.git
cd ttrpg
```

## 3. Pick your path (~30 sec to choose)

### A. **Continue an existing campaign** (Cookie / Holly / Shen Sama / Kenji / Amaris)

```bash
cd Kenji/Game\ init\ files
python gamemode.py --character cookie       # starter-arc bard
python gamemode.py --character shen_sama    # dragon road-movie arc
python gamemode.py --character kenji        # kenji manifest → kenji_state.json
```

You'll see:
- Boot sequence with all 7 steps (LOAD STATE / TRACKER DRIFT / CONTINUITY / CITY REGISTRY / NARRATOR / DEADLINES & GOALS)
- Dashboard with HP, AC, level, XP, gold, spell slots, inventory, deadlines, goal alerts
- PC abilities + Ember inheritance + scene NPCs + cardinal rules
- Ends with `GAMEMODE_REPORT.json` written

### B. **Start a brand-new character**

```bash
cd Kenji/Game\ init\ files
python generate_starter_campaign.py
```

Interactive prompts:
- **Name** — your PC's first name (e.g., Kael, Tava, Mira)
- **Race** — Halfling / Human / Half-Orc / Elf / Dwarf / Eladrin / etc.
- **Class** — Fighter / Bard / Druid / etc. (or any made-up class concept)
- **Background** — 1–2 sentences on where they come from
- **Personal goal** — what they want
- **Region** — frontier / heartland / coastal / mountain / forest / desert / etc.

Output:
- `<YourCharName>/Game init files/character_world_state.json` — a full Levels 1–10 starter campaign with main cast, quest spine, antagonist arc, and Ember inheritance shaped to your character concept.
- `Kenji/Game init files/manifests/<yourcharname>.json` — central manifest so the new character is launchable via `--character <yourcharname>` from CLI, GUI, or .exe without any extra config inside the character folder.

Then start play:
```bash
python gamemode.py --character <yourcharname>
```

## 4. Make rolls during play (~5 sec each)

```bash
# Skill check, no advantage
python ttrpg_game_engine.py skill 9 --dc 18 --label "Persuasion"

# Skill check with advantage
python ttrpg_game_engine.py skill 7 --adv --dc 14 --label "Stealth"

# Skill check with disadvantage
python ttrpg_game_engine.py skill -2 --dis --dc 12 --label "WIS save vs alcohol"
```

The output is real bytes from a real run — paste them into your AI conversation, your VTT, or wherever.

## 5. Update state during play (~5 sec each)

```bash
# Tick the clock 1 hour
python _dm_turn.py --character cookie tick 1

# Spend gold
python _dm_turn.py --character cookie gold sub 12

# Use a spell slot
python _dm_turn.py --character cookie slot use 2

# Use an ability charge
python _dm_turn.py --character cookie charge use "Stunning Kicks"

# Take a long rest (restores HP, slots, daily abilities)
python _dm_turn.py --character cookie rest long

# Eat a meal (resets hunger timer)
python _dm_turn.py --character cookie eat
```

## 6. End a chapter (~2 min)

When the narrative reaches a natural break:

1. Write the chapter prose file: `<YourCharName>/Chapters/<charname>_chapter_NN.md`
2. Run the chapter-close protocol — see `Kenji/Game init files/DM_TURN_PROTOCOL.md` § "CHAPTER END". This updates JSON `_chapter`, `_chapter_status`, `_chapter_title`, appends to `_chapter_history`, and updates the tracker.
3. Re-run `gamemode.py` — should report `ALL SYSTEMS GREEN` (or surface drift you need to fix).

## Common issues

### "ModuleNotFoundError: No module named 'customtkinter'"
You're trying to run the GUI without installing the package. `pip install customtkinter`.

### "TRACKER DRIFT — !!! field(s) out of sync"
The tracker markdown header is out of step with the JSON state. Update the tracker's "Day", "Level", "EXP", or "Chapter" line to match the JSON.

### "OVERDUE: <something>"
Either:
- The event is real and you forgot it → resolve it in fiction
- The event is done and not marked → edit JSON, set `"status": "DONE"` on that event entry

### "JSON parse fail / unterminated string"
OneDrive sync footgun: bash sees a stale truncated copy of a file the editor just wrote. Wait 30 seconds for sync, retry. If persistent, force a save in your editor.

### "exp_to_next_level: unsupported operand"
Engine bug fixed in commits after this version. Pull latest from origin/main.

## Optional: GUI

```bash
pip install customtkinter
cd Kenji/Game\ init\ files
python kenji_gui.py --character cookie        # or: shen_sama, holly, amaris, kenji
```

Live state dashboard. Reads the same JSON the CLI does. The `--character` flag resolves a manifest under `Kenji/Game init files/manifests/`.

## Optional: Build a Windows .exe

Requires Windows + Python with `pyinstaller` and `customtkinter` installed.

**From `cmd.exe`:**
```cmd
cd "C:\Users\<you>\...\TTRPG\Kenji\Game init files"
build_exe.bat
```

**From PowerShell** (PowerShell does NOT auto-run scripts from the current directory — you must prefix with `.\`):
```powershell
cd "C:\Users\<you>\...\TTRPG\Kenji\Game init files"
.\build_exe.bat
```

Output: `Kenji\Game init files\dist\Kenji DM Tool.exe`. Single self-contained .exe.

Launch from PowerShell with the call operator:

```powershell
& ".\Kenji DM Tool.exe" --character cookie
```

If `--character` is omitted, the .exe defaults to the Kenji manifest. To debug a silent crash, build the debug variant via `build_exe_debug.bat` and run `Kenji DM Tool DEBUG.exe` — the console stays open behind the GUI and prints any traceback.

## How to play with an AI DM

1. Run `python gamemode.py --character <name>` at session start.
2. Paste the boot output to the AI (Claude, GPT, etc.).
3. The AI runs the DM role. Tell it what your PC does.
4. When the AI calls for a roll, run the skill-check command and paste real output back.
5. State changes go through `_dm_turn.py` commands or direct JSON edits.
6. At chapter close, run the chapter-close protocol.

Cardinal Rules in `Kenji/Game init files/dm_rules_tracking.md` — Rule 7 specifically: **the AI must paste real engine bytes, not fabricated output.** Rule 8: **the AI doesn't pause the game to negotiate mature content.**

---

That's the whole loop. Engine is pure stdlib so a fresh clone runs immediately. Existing campaigns (Cookie, Kenji, Amaris) are ready to load. New campaigns spin up via `generate_starter_campaign.py`.

For the full DM protocol, rules library, and architecture, see `Kenji/Game init files/DM_TURN_PROTOCOL.md` and `Kenji/Game init files/dm_rules_tracking.md`.
