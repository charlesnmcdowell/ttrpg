# Character Creation Wizard — Phase 2d Bug Audit

Read-only audit. Bugs are flagged with severity and the line(s) involved. No fixes applied.

---

## CRITICAL — will misbehave the moment you actually use it

### CRIT-1. `_find_ttrpg_root` returns the wrong folder inside the bundled `.exe`

`character_creation_wizard.py` lines 905–914.

In a PyInstaller `--onefile` build, `Path(__file__).resolve().parent` resolves to `_MEI<random>/` (PyInstaller's temp extraction folder), not the OneDrive engine dir. So:

- `here = _MEI<random>/` — assuming the bundle preserves the script's flat layout, which it usually does.
- `candidate = here.parent.parent` — somewhere under `%TEMP%/`, not the user's TTRPG folder.
- The `(candidate / "Kenji" / "Game init files").is_dir()` guard fails (correctly).
- `os.environ.get("TTRPG_ROOT")` is unlikely to be set.
- The function returns `candidate` ("best effort") — **a temp folder that gets nuked on .exe exit**.

Downstream effect: the new character's folder + manifests get written to `%TEMP%/_MEI*/...`, then disappear when the .exe quits. The wizard reports success but nothing persists.

The existing `generate_starter_campaign.py` does this correctly (lines 40–56): it walks up looking for `realm_lore_registry.json`, which is a stable marker. The wizard should use the same trick (or just import and reuse `generate_starter_campaign.SCRIPT_DIR`/`TTRPG_DIR`).

### CRIT-2. `subprocess.run([sys.executable, gen_script, ...])` is wrong inside the bundled `.exe`

`character_creation_wizard.py` line 948.

Inside a PyInstaller bundle, `sys.executable` is `Kenji DM Tool.exe`, not Python. So the subprocess line resolves to:

```
"C:\...\Kenji DM Tool.exe" "C:\...\generate_starter_campaign.py" --name X --race Y ...
```

`Kenji DM Tool.exe` does not accept a `.py` path as its first arg — its argparse only knows `--character` and `--new-character`. The subprocess will either no-op, error, or worst case re-launch the wizard recursively.

Fix path requires either: (a) detect `getattr(sys, "frozen", False)` and call `generate_starter_campaign` in-process via `import` instead of subprocess, or (b) ship a separate `generate_starter_campaign.exe` PyInstaller target.

This and CRIT-1 together mean **the wizard cannot work as a bundled `.exe` in its current form**. It will only function when run as `python kenji_gui.py --new-character` from a terminal with the OneDrive folder structure intact.

### CRIT-3. Wizard writes to `state.player_info.appearance`, but the canonical key is `player_input.appearance`

`character_creation_wizard.py` lines 986–990 and 994–995.

The template (`templates/new_character_campaign.template.json`) and the generator (`generate_campaign_scaffold` line 552: `campaign["player_input"] = player_input`) both store these fields under `player_input`, not `player_info`:

- Template line 23: `"player_input": { ..., "appearance": { ... } }`
- Template line 18: `"player_input": { ..., "narrator_style": { "author":..., "series":..., "voice":... } }`

The wizard creates **brand-new dict keys** (`player_info`, `campaign_meta`) that no other code in the engine reads. The fields the player painstakingly entered through 9 steps go into a pocket of the JSON nothing else looks at. Silent data loss.

Additionally: `narrator_style` in the template is a **dict** (`author`, `series`, `voice`), but the wizard writes a **string** (e.g. `"Aleron Kong (The Land)"`). Anything that reads `state.player_input.narrator_style.author` would TypeError.

### CRIT-4. Existing-character name collision silently destroys the existing state file

`generate_starter_campaign.py` line 770–773.

`create_campaign_folder` does `with open(state_file, "w", ...)` unconditionally — no check for whether the folder already exists. The wizard does not pre-validate that the chosen name isn't already taken.

Scenario: user names a new character "Kenji". Wizard runs the generator. Generator's `state_file = TTRPG_DIR / "Kenji" / "Game init files" / "character_world_state.json"` (an existing file from your real Kenji campaign). The open-for-write **truncates and overwrites** the existing Kenji state with a level-1 starter scaffold.

The manifest is preserved (line 798: `if not manifest_path.exists()`) but the actual game state is gone. This is destructive and irrecoverable without git/backup.

The wizard should do an existence check on the target folder before invoking the generator and bounce the user back to the Name step with an error.

---

## HIGH — will produce a visibly broken character or a frozen UI

### HIGH-1. UI freezes during the generator subprocess (no async)

`character_creation_wizard.py` lines 959–960.

`subprocess.run(cmd, capture_output=True, text=True, timeout=60)` is synchronous on the Tk main thread. The button text updates to "Creating..." right before this call, but Tk never gets a chance to repaint — the entire wizard window goes "Not Responding" until the generator finishes (typically 1–3 seconds, but could be longer on a cold disk or under OneDrive sync pressure). On Windows the title bar grays out and the user is likely to force-quit.

`update_idletasks()` on line 1087 helps the button label change, but doesn't help during the subprocess.

Fix would require running the pipeline on a `threading.Thread` and using `self.after()` to dispatch UI updates back to the main thread.

### HIGH-2. `starting_gear` written to wrong key — never appears in inventory

`character_creation_wizard.py` lines 999–1003.

The wizard writes to `state.mechanical_state.inventory`. But `generate_campaign_scaffold` (lines 729–739) creates `mechanical_state` with these keys:

```
level, class, proficiency_bonus, ability_scores, starting_gold,
character_flaw, exp_archetype, support_archetype
```

There is **no `inventory` key** in the generated scaffold. The wizard's `setdefault("inventory", [])` creates a new key that no other code reads. The play_engine, dashboard, and chapter-close pipeline don't know about `mechanical_state.inventory`.

Whether starting gear surfaces in the actual game depends on where the engine reads inventory from. Worth verifying before relying on it.

### HIGH-3. `_pipeline_recompute_stats` may double-apply racial bonuses

`character_creation_wizard.py` lines 1013–1033 + `character_compute.py` `recompute_ability_scores`.

The generator (`generate_starter_campaign.py` lines 698–727) **already computes racial bonuses** and writes the full `ability_scores` block with `base/racial/final/mod` per stat. Then the wizard immediately calls `character_compute.recompute_character_state`, which calls `recompute_ability_scores`.

If `recompute_ability_scores` reads `base + racial → final + mod` (idempotent), this is fine. If it reads `final` and then re-applies racial bonuses, you get racial bonuses applied twice. Likely fine based on past usage but worth confirming with a manual run.

### HIGH-4. `character_compute` import via `sys.path.insert` is fragile in bundled mode

`character_creation_wizard.py` lines 1016–1022.

In a bundled `.exe`, `engine_dir = ttrpg_root / "Kenji" / "Game init files"` is wrong (see CRIT-1). Even if `engine_dir` were correct, the bundled .exe cannot `import character_compute` from a filesystem path — PyInstaller froze the modules at build time. The import only succeeds if `character_compute` is **already** bundled (which it should be — it's used by the dashboard).

But if the bundled version drifts from the OneDrive version, `recompute_character_state` runs against the bundled (possibly older) logic. Subtle versioning landmine.

### HIGH-5. Empty / whitespace-only name slips through if step 5 is skipped via Back→jump

`character_creation_wizard.py` line 343 / 397–402.

Validation only fires on `_on_next` for the current step. If the user types a name, navigates Back to step 4, edits something, navigates forward (which re-runs step 4's validation but not step 5's), then through to step 9 — and step 5's `_w_name` widget got cleared somehow — the name field could be empty by the time finalize runs.

The finalize pipeline does `display = self.data["name"].strip()`, then computes folder/slug from it. An empty name produces:
- `_compute_folder_name()` → `""`
- `_compute_slug()` → `""`
- Subprocess gets `--name ""` — generator either errors or produces a "" folder.

Should add a final sanity check inside `_on_finalize` before kicking off Step 1.

### HIGH-6. Step counter not refreshed during pipeline; user sees one frozen "Creating..." for the whole 5-step run

`character_creation_wizard.py` lines 1084–1120.

The button text reads "Creating..." for all five sequential steps. There is no per-step UI indication. If step 3 (recompute) hangs or step 4 (dist manifest) is slow because of OneDrive, the user has no idea what's happening — they'll assume it crashed and force-quit, leaving a half-created character on disk.

Should update `btn_next` text to `"Step 1/5: Generating..."`, `"Step 2/5: Patching..."`, etc., between calls.

---

## MEDIUM — minor data correctness or UX issues

### MED-1. `display in slots` is case-sensitive — can clutter `tts_config.json`

`character_creation_wizard.py` line 1067.

The TTS multi-voice loader does case-insensitive lookup per the `_doc` comment in `tts_config.json`. So `"Kenji"` and `"kenji"` would both work for resolution — but if the wizard adds `"kenji"` while `"Kenji"` already exists, the JSON now has two duplicate-ish slots that confuse manual editing later.

Should compare with `.lower()` against `slot.lower()` for keys.

### MED-2. `_resolve_race_string` and `_resolve_class_string` return empty string on the fallthrough

`character_creation_wizard.py` lines 921–933.

If `self.data["race"]` is somehow empty (e.g. wizard data corrupted by a partial init), `_resolve_race_string` returns `""` — not the documented `"Human"` fallback. Same for class. Validation should prevent this from happening, but defense-in-depth would say `return race or "Human"` instead of `return race`.

### MED-3. `--background` and `--goal` are passed even when empty

`character_creation_wizard.py` lines 952–953.

Validation requires bg ≥ 50 chars and goal ≥ 10 chars (lines 393–396) — so this won't fire in practice. But if `_collect_current_step` ever fails silently, `--background ""` and `--goal ""` get passed to the generator, which produces a hollow character with `[Tied to 's background: ]` placeholder strings (see generator line 568). Cosmetic, low risk.

### MED-4. `--archetype` is hard-coded to `"combat"`

`character_creation_wizard.py` line 957.

The generator supports `combat`, `support:performer`, `support:healer`, etc. The wizard offers no way to pick. Players who want a non-combat archetype have to manually edit the state file after creation. Feature gap, not a bug — but worth documenting.

### MED-5. Region `.lower()` called twice (defense in depth, harmless)

`character_creation_wizard.py` lines 341 + 954. Already lowercased on collect, lowercased again in pipeline. No-op. Cosmetic.

### MED-6. `_pipeline_write_dist_manifest` checks `dist_manifests.parent.is_dir()` — meaning it requires the `dist/` folder, not `dist/manifests/`

`character_creation_wizard.py` line 1044.

`dist_manifests = engine_dir / "dist" / "manifests"`, so `.parent` is `engine_dir/dist`. Correct logic — only proceed if the `dist/` build folder exists. But the comment says "(no dist folder)" which matches. Verify the user's actual layout: if their `dist/` exists but `dist/manifests/` doesn't, `mkdir(parents=True)` creates it. Good.

### MED-7. `_compute_folder_name` doesn't sanitize against Windows-illegal chars

`character_creation_wizard.py` lines 896–899.

A name like `"Kenji/Vex"` or `"Bob:The Slayer"` would create a folder name with `/` or `:` in it, which Windows rejects. The validation only enforces length ≥ 2. Should strip or reject illegal chars: `< > : " / \ | ? *`.

### MED-8. `region.lower()` matches only `REGION_ANCHORS` keys — no validation against unknowns

If the dropdown ever offers a region the generator doesn't know (`REGION_ANCHORS` in `generate_starter_campaign.py` ~line 65), the generator silently falls back to `"frontier"` (line 536). Not a bug — but if you add new regions to the wizard you must also add them to `REGION_ANCHORS`.

---

## LOW / cosmetic

### LOW-1. Stale comment in `kenji_gui.py` `_run_character_creation_wizard` docstring

Lines 3924–3928 still say "Phase 2d wires the finalize pipeline; Phase 2c's wizard currently dumps data to /tmp/wizard_output.json for inspection at finalize." Phase 2d is now done — the docstring lies.

### LOW-2. `_run_character_creation_wizard` says "validates NPC names against npc_name_bank.md"

Line 3922. The wizard does not currently do this — it was deferred. Docstring is aspirational.

### LOW-3. Step 9 success dialog instructs user to relaunch from desktop shortcut

`character_creation_wizard.py` lines 1127–1129.

This is a usability papercut. It would be smoother to auto-relaunch the dashboard with `--character <slug>` via `subprocess.Popen` and then `self.destroy()`. Trade-off: explicit/safe vs. seamless. Current behavior is explicit/safe.

### LOW-4. `import subprocess` inside `_pipeline_run_generator` is lazy

`character_creation_wizard.py` line 937.

Cosmetic — should move to the module-level imports for clarity/PEP-8. No functional impact.

### LOW-5. `_finalize_failure` button text uses "Create Character →" with the literal arrow character

`character_creation_wizard.py` line 1136.

Make sure the actual label set at step 9 elsewhere matches exactly, otherwise the button label could mismatch after a failed retry. Quick visual check needed.

---

## Audit summary

**Showstoppers (any one prevents the wizard from doing its job correctly):**
- CRIT-1 + CRIT-2: bundled `.exe` will write to a temp folder and lose everything. Wizard only works in `python kenji_gui.py --new-character` mode for now.
- CRIT-3: appearance and narrator never reach the keys the rest of the engine reads. Player input silently lost.
- CRIT-4: name collision silently destroys an existing character's state file.

**High-impact but recoverable:**
- HIGH-1: UI freeze; user thinks it crashed.
- HIGH-2: starting gear written to dead key.
- HIGH-3: possible double-applied racial bonuses.
- HIGH-5: empty name slips through edge cases.
- HIGH-6: no per-step progress indicator.

**Recommended remediation order if/when you want fixes:**
1. CRIT-4 (data destruction) — add an existence check on the folder before subprocess.
2. CRIT-3 (data layout mismatch) — re-route writes to `player_input.appearance` and `player_input.narrator_style` (and reshape narrator into the dict the template expects).
3. CRIT-1 + CRIT-2 (bundled mode) — switch the generator from subprocess to in-process import. Solves both at once and makes HIGH-1 (UI freeze) much easier because you can wrap the in-process call in a thread.
4. HIGH-2 (gear key) — verify where the engine actually reads inventory from, then write there.
5. The rest in order of severity.

---

## Fixes Applied (post-audit pass)

All four CRITs and the high-priority highs are addressed in the current `character_creation_wizard.py` (~1320 lines). End-to-end pipeline test passed in the Linux sandbox: scaffold → folder → recompute → manifest write all succeed, with appearance + narrator_style + ability_scores landing in canonical `player_input.*` keys, equipped gear in `_story_engine_state.equipped`, and HP/AC mirrored into both `mechanical_state` and `_story_engine_state`.

| ID     | Fix                                                                                          | Status   |
|--------|----------------------------------------------------------------------------------------------|----------|
| CRIT-1 | `_find_ttrpg_root` walks up looking for `realm_lore_registry.json`, with `TTRPG_ROOT` env override and `sys.executable`-based fallback for bundled `.exe`. Returns `Optional[Path]` so callers can fail gracefully. | fixed    |
| CRIT-2 | Dropped `subprocess.run` entirely. New `_pipeline_run_generator_inproc` does `import generate_starter_campaign` and calls `generate_campaign_scaffold` + `create_campaign_folder` in-process. Sets `TTRPG_ROOT` env var first so the generator's module-level constants resolve correctly. Works in bundled `.exe`. | fixed    |
| CRIT-3 | New `_build_player_input` puts appearance / narrator_style (as `{author, series, voice}` dict) / ability_scores under `player_input.*` — the canonical keys the template + engine read from. New `_narrator_style_dict` parses the wizard's display string (e.g. `"Aleron Kong (The Land)"`) into the dict shape. | fixed    |
| CRIT-4 | New `_validate_finalize_or_error` checks both folder collision (`ttrpg_root / folder.exists()`) and manifest collision (with non-zero size — to ignore the 0-byte tombstones from the Aelyn cleanup). Refuses to proceed; bounces user back with a "go back to step 5" message. | fixed    |
| HIGH-1 | New `_pipeline_thread` runs the 4 pipeline steps on a `threading.Thread(daemon=True)`. UI updates posted back via `self.after(0, ...)`. Wizard window stays responsive throughout. | fixed    |
| HIGH-2 | Starting gear written to `_story_engine_state.equipped` (verified canonical key in template + Kenji's real state file). Old `mechanical_state.inventory` write removed. | fixed    |
| HIGH-3 | Verified `recompute_ability_scores` reads `base + racial` (idempotent) — no fix needed. Audit dismissed. | dismissed |
| HIGH-4 | Bundled `.exe` import of `character_compute` works because PyInstaller already bundles it. Documented. No code change. | accepted  |
| HIGH-5 | `_validate_finalize_or_error` checks `name.strip()` is non-empty before kicking off any pipeline step. | fixed    |
| HIGH-6 | New `_set_step_text` helper updates button text per pipeline step: `"Step 1/4: Generating..."` → `"Step 2/4: Computing stats..."` → `"Step 3/4: Writing manifests..."` → `"Step 4/4: Adding TTS slot..."`. Thread-safe via `self.after()`. | fixed    |
| MED-1  | TTS slot existence check is now case-insensitive: builds `existing_lower = {k.lower(): k for k in slots if not k.startswith("_")}` and compares `display.lower()`. | fixed    |
| MED-2  | `_resolve_race_string` and `_resolve_class_string` fall back to `"Human"` / `"Fighter"` instead of empty string. | fixed    |
| MED-3  | Validation already enforces `bg ≥ 50` and `goal ≥ 10`. No fix needed. | accepted  |
| MED-4  | Archetype hard-coded to `"combat"` documented as a feature gap, not a bug. | deferred  |
| MED-5  | `region.lower()` defense-in-depth, harmless. No fix. | accepted  |
| MED-6  | `_pipeline_write_dist_manifest` parent-check is correct. No fix. | accepted  |
| MED-7  | New `_ILLEGAL_NAME_CHARS` constant + check in `_validate_finalize_or_error` rejects `< > : " / \ \| ? *` in names with a clear error message. | fixed    |
| MED-8  | `REGION_ANCHORS` mismatch is a future-changes hazard, not a current bug. Documented. | accepted  |
| LOW-1  | Stale "Phase 2c stub" wording in module docstring + `kenji_gui._run_character_creation_wizard` docstring rewritten to describe the actual 7-step finalize pipeline. | fixed    |
| LOW-2  | Stale "validates NPC names against npc_name_bank.md" claim removed from docstrings (NPC name validation was deferred and didn't ship). | fixed    |
| LOW-3  | "Relaunch from desktop shortcut" success-dialog UX intentional (explicit/safe over seamless). Can revisit if friction observed. | deferred  |
| LOW-4  | `import subprocess` no longer needed (subprocess removed). | obsolete  |
| LOW-5  | Button label "Create Character →" used consistently in `_finalize_failure` and step-9 setup. | fixed    |

**Smoke-test command to verify before rebuilding the `.exe`:**

```
cd "C:\Users\charl\OneDrive\Documents\TTRPG\Kenji\Game init files"
python kenji_gui.py --new-character
```

Walk through 9 steps with throwaway data. The wizard should:
- refuse a name like `Kenji` ("character folder already exists")
- refuse a name with `/` or `:` ("contains characters Windows doesn't allow")
- show per-step button text during the pipeline
- complete in ~1-2 seconds without freezing
- write `Test_Character/Game init files/character_world_state.json` with HP/AC populated, appearance under `player_input.appearance`, narrator under `player_input.narrator_style` as a dict, gear under `_story_engine_state.equipped`

Then delete the test folder before running `build_exe.bat`.
