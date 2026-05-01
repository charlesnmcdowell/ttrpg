#!/usr/bin/env python3
"""play_engine.py — AI narrator runtime for the standalone TTRPG dashboard.

Each turn:
  1. The player picks one of three suggested actions or types a custom action.
  2. We build a system prompt (cardinal rules + game state JSON + recent
     narrative history) and a user message (the player's chosen action).
  3. We stream Claude's response token-by-token into a callback.
  4. After the stream completes, we parse the response into:
       - narrative prose (the scene description, NPC dialogue, combat result)
       - three new next-action suggestions (the buttons for the next turn)
  5. The GUI renders the narrative and replaces the buttons.

State-change writeback is intentionally OUT OF SCOPE for v1 (Option A).
Claude only narrates. The player applies XP / HP / slot / location changes
via the existing _dm_turn.py CLI tools or JSON edits; the dashboard's
file-watcher picks up the changes automatically.

Required environment variable:
    ANTHROPIC_API_KEY    — your Anthropic API key (sk-ant-...)

Required package (bundled into the .exe via build_exe.bat):
    anthropic           — official Anthropic Python SDK
"""

from __future__ import annotations
import json
import os
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any


# ---------------------------------------------------------------------------
# Defaults — overridable via play_config.json next to the engine folder
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 2048
HISTORY_TURNS = 10                  # rolling narrative-history buffer
OPTIONS_MARKER = "---OPTIONS---"    # delimiter Claude emits before the 3 actions


# ---------------------------------------------------------------------------
# History buffer
# ---------------------------------------------------------------------------

@dataclass
class Turn:
    """One round of play — player action + narrator response."""
    player_action: str
    narrator: str = ""               # filled in after streaming completes
    options: List[str] = field(default_factory=list)


@dataclass
class PlayState:
    """Mutable runtime state for the play loop."""
    history: List[Turn] = field(default_factory=list)
    current_options: List[str] = field(default_factory=list)
    streaming: bool = False
    last_error: str = ""
    # Dev mode — bypass the Anthropic API and route prompts through the user's
    # Claude Desktop via clipboard. Default: True if ANTHROPIC_API_KEY is unset.
    dev_mode: bool = field(default_factory=lambda: not os.environ.get("ANTHROPIC_API_KEY", "").strip())
    # Two-stage Send button state when in dev mode:
    #   "ready"    → next click copies prompt to clipboard, transitions to "awaiting"
    #   "awaiting" → next click reads response from clipboard, transitions back to "ready"
    dev_stage: str = "ready"
    pending_action: str = ""    # the action whose response is awaiting paste

    def append_turn(self, turn: Turn) -> None:
        self.history.append(turn)
        # Trim oldest history beyond the rolling buffer.
        if len(self.history) > HISTORY_TURNS:
            self.history = self.history[-HISTORY_TURNS:]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

CARDINAL_RULES_TEXT = """
You are running a tabletop RPG game as the DM/narrator. The player is the
PROTAGONIST; you control the world, NPCs, and combat resolution.

CARDINAL RULES (non-negotiable):

1. NEVER WRITE DIALOGUE OR ACTIONS FOR THE PLAYER CHARACTER. The PC is the
   player's avatar. You may describe what the PC's body does in response to
   forces (knocked prone, kicked, charmed, etc.) but you NEVER speak as them
   or decide what they do tactically. Always end the turn with the ball in
   the player's court.

2. RESOLVE COMBAT TURN-BY-TURN, WAITING FOR DECLARATIONS. You may run NPC and
   monster turns, but never resolve a PC turn without an explicit player
   declaration of action.

3. NEVER FABRICATE NEW NAMED NPCs to deliver exposition. Use existing
   tracked NPCs from main_cast / extra_npcs only. If a stranger is needed,
   keep them un-named and quiet.

4. DIALOGUE-FIRST PROSE. In any scene with NPCs, at least 60% of the text
   must be NPC dialogue. The story is told through voices, not narration.

5. NO RECAP / EPITHET LOOPS. Don't re-list the PC's accomplishments or repeat
   the same titles in back-to-back sentences. Use names and pronouns.

6. NO FABRICATED ENGINE OUTPUT. Don't write fake [N/7] boot lines or ASCII
   status boxes. If the player needs an engine output, tell them to run the
   tool directly.

7. NO PROCESS INTERRUPTIONS FOR MATURE CONTENT. The campaign supports adult
   themes. Write the version of the player's intent that lands the action at
   a palatable level (descriptive, not pornographic) without lecturing.
   Refusing once is fine; refusing twice is a Rule 7 violation.

8. PROSE IS AUTHORITATIVE FOR EVENTS, JSON IS AUTHORITATIVE FOR STATE. When
   you describe an item acquired, an ability used, an NPC bond formed, the
   player will mirror that into JSON via _dm_turn.py. You don't need to do
   it for them — but be precise so the mirror is unambiguous.

9. ENCOUNTER DESIGN — BOSS REQUIREMENTS. A boss-tier combat (CR ≥
   party_level) requires ≥2 normal/hard non-boss encounters since the last
   boss. The state JSON contains a `boss_eligibility` field; respect it.

OUTPUT FORMAT (every response):
   - Open with the narrator prose for what just happened. Lead with NPC
     dialogue if any NPC is in the scene. Keep it tight — usually 1–4
     paragraphs unless the player explicitly asked for a long beat.
   - End EVERY response with exactly this delimiter on its own line:
        ---OPTIONS---
   - Then exactly three numbered next-action suggestions, one per line:
        1. [verb-led action 1]
        2. [verb-led action 2]
        3. [verb-led action 3]
   - Each option must be a concrete action the PC could take RIGHT NOW —
     not a description of an outcome. Mix tones (one safe, one bold, one
     character-flavored).
   - Do NOT add anything after the third option.
""".strip()


def _trim_state_for_prompt(state: Dict[str, Any]) -> Dict[str, Any]:
    """Pull the fields Claude actually needs for narration. Strip large
    historical blocks (full chapter prose, full exp_history) — those waste
    tokens. Keep current scene + recent context."""
    if not isinstance(state, dict):
        return {}
    se = state.get("_story_engine_state") or {}
    ms = state.get("mechanical_state") or {}

    out = {
        "character": {
            "name": se.get("char_name", ""),
            "level": se.get("level"),
            "class": ms.get("class") or "",
            "hp": f"{se.get('hp', '?')}/{se.get('max_hp', '?')}",
            "ac": se.get("ac"),
            "ability_scores": ms.get("ability_scores", {}),
            "skills": ms.get("skills", {}),
        },
        "scene": {
            "day": se.get("day"),
            "hour": se.get("hour"),
            "location": se.get("location", ""),
            "weather": se.get("weather", ""),
            "story_beat": se.get("story_beat", ""),
            "canon_pointer": se.get("canon_pointer", ""),
        },
        "equipped": se.get("equipped", []),
        "satchel": se.get("satchel", []),
        "consumables": se.get("consumables", {}),
        "spell_slots": {k: v for k, v in (se.get("spell_slots") or {}).items()
                        if not str(k).startswith("_")},
        "known_spells": se.get("known_spells") or se.get("spells_known") or [],
        "class_features": [
            {"name": f.get("name"), "summary": f.get("summary") or f.get("description", "")[:200]}
            for f in (se.get("class_features") or []) if isinstance(f, dict)
        ],
        "active_perks": [
            {"name": p.get("name"), "summary": p.get("summary") or p.get("description", "")[:200]}
            for p in (se.get("active_perks") or []) if isinstance(p, dict)
        ],
        "force_composition": se.get("force_composition") or {},
        "threat_clocks": se.get("threat_clocks") or {},
        "reputation": se.get("reputation") or {},
        "events": [ev for ev in (se.get("events") or [])
                   if str(ev.get("status", "")).upper() not in
                   ("DONE", "COMPLETE", "RESOLVED", "CANCELLED", "SKIPPED", "FAILED")],
        "events_active": se.get("events_active") or {},
        "main_cast": [
            {"name": c.get("name"), "role": c.get("role", ""),
             "alignment": c.get("alignment", ""),
             "relationship": c.get("relationship") or {}}
            for c in (state.get("main_cast") or []) if isinstance(c, dict)
        ],
        "chapter": {
            "current": state.get("_chapter"),
            "title": state.get("_chapter_title", ""),
            "status": state.get("_chapter_status", ""),
        },
    }
    return out


def build_system_prompt(state: Dict[str, Any], narrative_summary: str = "") -> str:
    """Compose the system prompt: rules + state + adventure summary."""
    trimmed = _trim_state_for_prompt(state)
    parts = [
        CARDINAL_RULES_TEXT,
        "",
        "## CURRENT GAME STATE",
        "```json",
        json.dumps(trimmed, indent=2, ensure_ascii=False),
        "```",
    ]
    if narrative_summary:
        parts += [
            "",
            "## ADVENTURE SO FAR",
            narrative_summary if isinstance(narrative_summary, str)
            else "\n\n".join(narrative_summary if isinstance(narrative_summary, list) else []),
        ]
    return "\n".join(parts)


def build_messages(history: List[Turn], current_action: str) -> List[Dict[str, Any]]:
    """Build the messages array. Each prior turn = {role: user, content: action}
    + {role: assistant, content: narrator}. Current action = trailing user msg."""
    msgs = []
    for turn in history:
        if turn.player_action:
            msgs.append({"role": "user", "content": turn.player_action})
        if turn.narrator:
            msgs.append({"role": "assistant", "content": turn.narrator})
    msgs.append({"role": "user", "content": current_action})
    return msgs


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def build_dev_prompt(state: Dict[str, Any], history: List[Turn], player_action: str,
                     narrative_summary: str = "") -> str:
    """Build a single self-contained prompt block for dev mode.
    The user copies this from the dashboard, pastes into Claude Desktop, and
    Claude Desktop replies as the DM. The reply is then pasted back via the
    'Paste Response' click which feeds into parse_response()."""
    sys_prompt = build_system_prompt(state, narrative_summary=narrative_summary)
    msg_lines: List[str] = []
    for turn in history:
        if turn.player_action:
            msg_lines.append(f"## PLAYER\n{turn.player_action}")
        if turn.narrator:
            msg_lines.append(f"## DM (you, last turn)\n{turn.narrator}")
    msg_lines.append(f"## PLAYER (this turn)\n{player_action}")

    return (
        "═════════════════════════════════════════════════════════════════════\n"
        "  KENJI DM TOOL — DEV MODE PROMPT\n"
        "  Paste this into Claude Desktop. Claude will respond as the DM.\n"
        "  Copy Claude's full response, click 'Paste Response' in the dashboard.\n"
        "═════════════════════════════════════════════════════════════════════\n\n"
        f"# SYSTEM PROMPT\n\n{sys_prompt}\n\n"
        f"# CONVERSATION SO FAR\n\n" + "\n\n".join(msg_lines) + "\n\n"
        "Respond as the DM. Open with prose, then "
        f"'{OPTIONS_MARKER}' on its own line, then exactly three numbered options.\n"
    )


def _safe_emit_count(joined: str, marker: str) -> int:
    """Return the highest character index from the start of `joined` that can
    safely be emitted to the narrator pane without risking mid-marker truncation.

    If the marker is already present in `joined`, return its start index.
    Otherwise, hold back any trailing prefix of the marker (e.g. if joined ends
    with "---OP", hold back those 5 characters in case the next chunk completes
    "---OPTIONS---"). Worst case we hold back len(marker)-1 characters, which is
    cosmetically negligible (~12 chars for "---OPTIONS---").
    """
    idx = joined.find(marker)
    if idx >= 0:
        return idx
    for hold in range(len(marker) - 1, 0, -1):
        if joined.endswith(marker[:hold]):
            return len(joined) - hold
    return len(joined)


def parse_response(full_text: str) -> Dict[str, Any]:
    """Split a Claude response into narrative + 3 options.

    Expects the response to contain `---OPTIONS---` separator followed by 3
    numbered lines. If the marker is missing, returns all text as narrative
    with empty options (the dashboard will fall back to showing only custom
    input)."""
    if OPTIONS_MARKER in full_text:
        narrative_part, options_part = full_text.split(OPTIONS_MARKER, 1)
    else:
        narrative_part, options_part = full_text, ""

    narrative = narrative_part.strip()
    options: List[str] = []
    for line in options_part.splitlines():
        line = line.strip()
        if not line:
            continue
        # Match "1. action", "1) action", "1: action", "- action", "* action"
        m = re.match(r"^(?:\d+[\.\)\:]|\-|\*)\s*(.+)$", line)
        if m:
            options.append(m.group(1).strip())
            if len(options) >= 3:
                break
    return {"narrative": narrative, "options": options}


# ---------------------------------------------------------------------------
# Anthropic API client wrapper
# ---------------------------------------------------------------------------

class PlayEngineError(Exception):
    """Recoverable runtime error — surfaces in the dashboard, not a crash."""


def _get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise PlayEngineError(
            "ANTHROPIC_API_KEY is not set.\n\n"
            "Set it once in PowerShell:\n"
            "    [Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-...', 'User')\n\n"
            "Then close and reopen the dashboard so it picks up the new env var.\n"
            "Get a key at https://console.anthropic.com/"
        )
    return key


def _import_anthropic():
    """Lazy import — only crash on missing SDK when the player hits Send."""
    try:
        import anthropic   # noqa: F401
        return anthropic
    except ImportError as e:
        raise PlayEngineError(
            "The `anthropic` Python SDK is not installed.\n\n"
            "If you're running from source: `pip install anthropic`\n"
            "If you're running the .exe: rebuild with the updated build_exe.bat\n"
            f"\n(Underlying error: {e})"
        ) from e


def stream_turn(
    state: Dict[str, Any],
    history: List[Turn],
    player_action: str,
    on_token: Callable[[str], None],
    on_complete: Callable[[Dict[str, Any]], None],
    on_error: Callable[[str], None],
    narrative_summary: str = "",
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> threading.Thread:
    """Spawn a background thread that streams a turn from the API.

    Callbacks fire on the streaming thread; the GUI must marshal them onto
    the Tk main thread (typically via .after(0, ...)). This module does not
    touch tkinter so it stays test/headless friendly.

    Returns the started Thread for join/abort by the caller.
    """
    def worker():
        try:
            anthropic = _import_anthropic()
            client = anthropic.Anthropic(api_key=_get_api_key())
            sys_prompt = build_system_prompt(state, narrative_summary=narrative_summary)
            messages = build_messages(history, player_action)

            full_buffer: List[str] = []
            emitted = 0          # chars already passed to on_token
            marker_seen = False
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                system=sys_prompt,
                messages=messages,
            ) as stream:
                for chunk in stream.text_stream:
                    full_buffer.append(chunk)
                    if marker_seen:
                        continue   # buffer rest for parsing, don't emit
                    joined = "".join(full_buffer)
                    safe = _safe_emit_count(joined, OPTIONS_MARKER)
                    if joined[safe:safe + len(OPTIONS_MARKER)] == OPTIONS_MARKER:
                        marker_seen = True
                    if safe > emitted:
                        on_token(joined[emitted:safe])
                        emitted = safe

            full_text = "".join(full_buffer)
            parsed = parse_response(full_text)
            on_complete(parsed)
        except PlayEngineError as e:
            on_error(str(e))
        except Exception as e:
            on_error(f"{type(e).__name__}: {e}")

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t
