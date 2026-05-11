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
# Hard cap on narrator response length. Sized to fit ~1–2 tight paragraphs
# of prose (≈300 words ≈ 450 tokens) plus the ---OPTIONS--- block (~80 tokens),
# with a small safety margin. Lower numbers keep play snappy; raising it lets
# the model write more before being cut off mid-sentence by the API. The
# CARDINAL_RULES brevity rule below is the soft enforcement; this is the hard
# ceiling.
DEFAULT_MAX_TOKENS = 700
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
    # Claude Desktop via clipboard / play_response.md file bridge. Default:
    # True ONLY if neither ANTHROPIC_API_KEY env var nor ttrpg_key.txt next to
    # play_engine.py provides a key — i.e. dev mode is the safe fallback when
    # there is no way to call the API. Either source flips this to False so
    # the dashboard streams turns from the API instead.
    dev_mode: bool = field(default_factory=lambda: not (
        os.environ.get("ANTHROPIC_API_KEY", "").strip()
        or _load_api_key_from_file()
    ))
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
# NPC appearance loader (shared cross-campaign canon)
# ---------------------------------------------------------------------------
#
# The single source of truth for NPC physical canon is
# `Kenji/Game init files/npc_appearance.md`. Every campaign in the realm
# (Amaris, Cookie, Holly, Shen Sama, Kenji) reads from this same file —
# the universe is shared and we don't duplicate NPC info per campaign.
#
# play_engine.py lives in that same folder, so the file is a sibling.
# Every turn we scan the state JSON for any NPC name whose appearance
# entry exists in the file, and inject the matched entries into the
# prompt right after CURRENT GAME STATE. The DM agent then has authoritative
# physical canon (color, eyes, build, voice, aura) for any NPC currently in
# threat_clocks / events / main_cast / scene fields — and never has to
# fabricate it from prose tags or extrapolate from PC stats.

# Section headers in npc_appearance.md that are NOT individual NPCs and
# should be skipped during entry parsing.
_APPEARANCE_NON_NPC_HEADERS = (
    "shared pattern",
    "deepwood characters",
    "book 1-2 characters",
    "dm checklist",
    "template",
)

# Tokens that are titles/articles, not name parts. When parsing a header like
# "## Lady Nyx — Living Lich", we want "Nyx" not "Lady" as the matchable token.
_APPEARANCE_TITLE_TOKENS = {
    "the", "a", "an", "of", "lady", "lord", "sir", "ser", "captain",
    "commander", "elder", "master", "mistress", "dame",
}


def _find_npc_appearance_file() -> Optional[Path]:
    """Return the path to canonical npc_appearance.md, or None if missing.

    play_engine.py is installed in Kenji/Game init files/ regardless of which
    campaign the dashboard is currently running, so the file is always a
    sibling on disk.
    """
    candidate = Path(__file__).resolve().parent / "npc_appearance.md"
    return candidate if candidate.exists() else None


def _parse_npc_appearance_entries(text: str) -> List[tuple]:
    """Parse npc_appearance.md into (header_line, name_tokens, body) tuples.

    Returns one tuple per NPC entry, skipping group headers and the template
    placeholder. name_tokens is the list of proper-noun words from the entry
    header that can be matched against the state JSON to detect whether the
    NPC is currently in scene.
    """
    entries: List[tuple] = []
    parts = re.split(r"^(## .+)$", text, flags=re.MULTILINE)
    # parts == [pre_text, header1, body1, header2, body2, ...]

    for i in range(1, len(parts), 2):
        header_line = parts[i].strip()
        body = parts[i + 1] if (i + 1) < len(parts) else ""
        header = header_line[3:].strip() if header_line.startswith("## ") else header_line
        header_lower = header.lower()

        # Skip non-NPC structural headers
        if any(skip in header_lower for skip in _APPEARANCE_NON_NPC_HEADERS):
            continue
        # Skip template placeholder "## [Name] — [Role / context]"
        if header.startswith("[") and "]" in header:
            continue

        # Extract the name portion — text before " — " / " – " / " - " or " ("
        name_part = re.split(r"\s+[—–\-]\s+|\s*\(", header, maxsplit=1)[0].strip()
        # Tokenize into proper-noun words, filtering out titles
        tokens = [
            t for t in re.findall(r"[A-Za-z']+", name_part)
            if t.lower() not in _APPEARANCE_TITLE_TOKENS
        ]
        if not tokens:
            continue

        entries.append((header_line, tokens, body.rstrip()))

    return entries


def _load_npc_appearance_for_state(state: Dict[str, Any]) -> str:
    """Return a markdown block of NPC appearance entries relevant to the
    current state, or empty string if none match.

    An entry matches if any of its name tokens appears as a whole word
    (case-insensitive) anywhere in the state JSON dump — covers
    threat_clocks, events, main_cast, scene fields, equipped descriptions,
    canon_pointer text, etc. without needing per-field special handling.
    """
    appearance_file = _find_npc_appearance_file()
    if appearance_file is None:
        return ""

    try:
        text = appearance_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    entries = _parse_npc_appearance_entries(text)
    if not entries:
        return ""

    state_str = json.dumps(state, ensure_ascii=False)

    matched: List[tuple] = []
    seen_headers = set()
    for header, tokens, body in entries:
        for token in tokens:
            pattern = re.compile(r"\b" + re.escape(token) + r"\b", re.IGNORECASE)
            if pattern.search(state_str):
                if header not in seen_headers:
                    matched.append((header, body))
                    seen_headers.add(header)
                break  # one token match is enough to include the entry

    if not matched:
        return ""

    out = [
        "## NPC APPEARANCE (canonical reference for scene)",
        "",
        "These are authoritative physical descriptions for any NPC named in "
        "the state above. Do NOT improvise dragon colors, eye colors, scale "
        "patterns, body builds, voice, or aura signatures — read here first. "
        "These entries live in Kenji/npc_appearance.md and are shared across "
        "every campaign in the realm.",
        "",
    ]
    for header, body in matched:
        out.append(header)
        out.append(body)
        out.append("")

    return "\n".join(out).rstrip() + "\n"


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

10. BREVITY IS A HARD RULE. Each response is 1–2 paragraphs MAX of narrator
    prose (target ≤180 words; absolute ceiling 300). Do NOT pad with
    atmosphere, recap, internal monologue, or sensory inventories. If a beat
    needs more space, COMPRESS it: pick the single most consequential image
    or line of dialogue and cut everything else. The player should be reading
    for ~15–30 seconds before they get control back. Long blocks of text
    between decisions kill pacing — bounce the ball back fast. Only exceed
    2 paragraphs if the player explicitly asked for a long beat (e.g.
    "describe the room in detail", "give me a flashback", "narrate the next
    hour"). Combat rounds, travel transitions, and reaction beats stay short.

OUTPUT FORMAT (every response):
   - Open with the narrator prose for what just happened. Lead with NPC
     dialogue if any NPC is in the scene. Keep it tight — 1–2 paragraphs
     ONLY (see Rule 10). No preambles, no recap, no closing summaries.
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
    """Compose the system prompt: rules + state + NPC appearance + adventure summary.

    NPC appearance is auto-loaded from the canonical
    Kenji/Game init files/npc_appearance.md — any NPC whose name appears in
    the state JSON gets their physical canon piped into the prompt so the
    DM agent doesn't have to fabricate it. See
    `_load_npc_appearance_for_state` for the matching logic.
    """
    trimmed = _trim_state_for_prompt(state)
    parts = [
        CARDINAL_RULES_TEXT,
        "",
        "## CURRENT GAME STATE",
        "```json",
        json.dumps(trimmed, indent=2, ensure_ascii=False),
        "```",
    ]
    npc_block = _load_npc_appearance_for_state(state)
    if npc_block:
        parts += ["", npc_block]
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
# Cost estimation (API mode warning)
# ---------------------------------------------------------------------------

# Anthropic per-million-token pricing snapshot. Used by estimate_turn_cost()
# to surface a $ figure on the Confirm-Send dialog so the player sees what a
# turn will cost BEFORE the API call fires. Keys must match the `model` arg
# passed to stream_turn (see DEFAULT_MODEL above). Prices change — verify
# current rates at https://www.anthropic.com/pricing and update this table.
# Numbers are USD per 1,000,000 tokens.
MODEL_PRICING = {
    # Sonnet 4.x line (the dashboard's default narrator)
    "claude-sonnet-4-6":      {"input": 3.00,  "output": 15.00},
    "claude-sonnet-4-5":      {"input": 3.00,  "output": 15.00},
    # Opus 4.x line (heaviest, most expensive — only use for hard scenes)
    "claude-opus-4-7":        {"input": 15.00, "output": 75.00},
    "claude-opus-4-6":        {"input": 15.00, "output": 75.00},
    # Haiku 4.5 (cheapest, fastest — fine for low-stakes scenes)
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
    "claude-haiku-4-5":       {"input": 1.00,  "output": 5.00},
}
# Fallback price if the active model isn't in the table — assume Sonnet rate
# (the safest middle estimate; a quote that turns out high is better than
# silently underpricing an Opus turn).
FALLBACK_PRICING = {"input": 3.00, "output": 15.00}


def estimate_tokens(text: str) -> int:
    """Rough token count from a character count. Anthropic tokenizer averages
    ~4 characters per token for English prose; we use 4.0 as a conservative
    rounding (slightly overestimates → cost quote is mildly pessimistic, which
    is the right direction for a spend warning)."""
    if not text:
        return 0
    return max(1, int(len(text) / 4))


def estimate_turn_cost(
    state: Dict[str, Any],
    history: List[Turn],
    player_action: str,
    narrative_summary: str = "",
    model: str = None,
    max_tokens: int = None,
) -> Dict[str, Any]:
    """Estimate the USD cost of a single API turn BEFORE firing it.

    Returns a dict the dashboard can render in its confirm dialog:
        {
            "model":             <str>,
            "pricing_known":     <bool>,           # False ⇒ used FALLBACK_PRICING
            "input_tokens":      <int>,
            "max_output_tokens": <int>,
            "est_input_usd":     <float>,
            "est_output_max_usd": <float>,        # if model uses entire budget
            "est_total_max_usd": <float>,         # input + max_output
            "est_typical_usd":   <float>,         # ~60% output assumption
        }

    NOTE: input_tokens is approximated from the assembled prompt size
    (system + history + current action). Real billing uses the Anthropic
    tokenizer; this estimate is within ~10% for English prose."""
    model = model or DEFAULT_MODEL
    max_tokens = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS
    pricing = MODEL_PRICING.get(model, FALLBACK_PRICING)
    pricing_known = model in MODEL_PRICING

    sys_prompt = build_system_prompt(state, narrative_summary=narrative_summary)
    msgs = build_messages(history, player_action)
    msg_text = "\n\n".join(m.get("content", "") for m in msgs if isinstance(m, dict))
    in_tok = estimate_tokens(sys_prompt) + estimate_tokens(msg_text)

    est_in_usd = in_tok * pricing["input"] / 1_000_000.0
    est_out_max_usd = max_tokens * pricing["output"] / 1_000_000.0
    est_total_max_usd = est_in_usd + est_out_max_usd
    # Most narrator turns don't use the full output budget — empirically the
    # brevity rule lands responses around 350-450 tokens of 700 cap. Use 60%
    # as the "typical" estimate to give the player a realistic median.
    est_typical_usd = est_in_usd + (max_tokens * 0.60) * pricing["output"] / 1_000_000.0

    return {
        "model": model,
        "pricing_known": pricing_known,
        "input_tokens": in_tok,
        "max_output_tokens": max_tokens,
        "est_input_usd": est_in_usd,
        "est_output_max_usd": est_out_max_usd,
        "est_total_max_usd": est_total_max_usd,
        "est_typical_usd": est_typical_usd,
    }


# ---------------------------------------------------------------------------

class PlayEngineError(Exception):
    """Recoverable runtime error — surfaces in the dashboard, not a crash."""


# Filename next to play_engine.py that holds an Anthropic API key as plain
# text (single line, no quotes, no "export ...=" prefix). Used as a fallback
# when ANTHROPIC_API_KEY is not exported in the environment — handy for the
# Windows dashboard where setting persistent env vars is friction. The file
# is gitignored in this folder's .gitignore. Never commit it.
API_KEY_FILENAME = "ttrpg_key.txt"


def _load_api_key_from_file() -> str:
    """Read API_KEY_FILENAME from the same folder as play_engine.py, strip
    whitespace, return the key string or "" on any failure (missing file,
    empty, unreadable). Never raises — caller decides whether absence is
    fatal (API mode) or fine (dev mode default detection)."""
    try:
        path = Path(__file__).parent / API_KEY_FILENAME
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _get_api_key() -> str:
    """Resolve the Anthropic API key, in this precedence order:
      1. ANTHROPIC_API_KEY environment variable (preferred — works the same
         way every other Anthropic-SDK consumer expects)
      2. ttrpg_key.txt next to play_engine.py (file fallback — convenient on
         Windows where setting a persistent env var requires admin rights)
    Raises PlayEngineError with setup instructions if neither is present."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        key = _load_api_key_from_file()
    if not key:
        key_path = Path(__file__).parent / API_KEY_FILENAME
        raise PlayEngineError(
            "No Anthropic API key found.\n\n"
            "Either set the env var (PowerShell):\n"
            "    [Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-...', 'User')\n\n"
            f"OR drop the key (single line, no quotes) into:\n"
            f"    {key_path}\n\n"
            "Then close and reopen the dashboard so it re-checks both sources.\n"
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
