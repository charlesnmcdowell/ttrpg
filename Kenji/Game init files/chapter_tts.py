#!/usr/bin/env python3
"""chapter_tts.py — convert a chapter markdown file into an audiobook WAV.

Pipeline:
  1. Read the chapter .md file.
  2. Send it to Claude (Haiku) for speaker attribution. Returns a JSON list
     of {speaker, text} segments. Unattributed prose goes to "Narrator".
  3. Validate every speaker has a voice ID in tts_config.json. If any are
     missing, print the full list of missing names and abort BEFORE firing
     the (expensive) ElevenLabs API.
  4. Show a cost preview: char count, segment count, ElevenLabs $ estimate.
     Prompt the user (y/n) before burning credits.
  5. Fetch PCM from ElevenLabs per segment.
  6. Stitch into one WAV via tts_stitcher (120ms silence between speakers).
  7. Write to Kenji/voice_audio/<chapter_basename>.wav.

Usage:
    python chapter_tts.py path/to/chapter.md
    python chapter_tts.py path/to/chapter.md --yes       # skip confirm
    python chapter_tts.py path/to/chapter.md --dry-run   # parse + validate only
    python chapter_tts.py path/to/chapter.md --out custom_name.wav

The voice ID registry is the existing tts_config.json. The lookup is
case-insensitive. Keys starting with "_" are documentation, not slots.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- Constants ---------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent  # .../Kenji/Game init files
KENJI_DIR = SCRIPT_DIR.parent                  # .../Kenji
VOICE_AUDIO_DIR = KENJI_DIR / "voice_audio"
TTS_CONFIG = SCRIPT_DIR / "tts_config.json"

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_MAX_TOKENS = 16000      # per-chunk output budget (Haiku 4.5 supports more)
CHUNK_MAX_CHARS  = 5000        # split chapters into chunks this size before
                                # parsing. Empirically, ~5k chars of prose
                                # produces well under 16k tokens of segmented
                                # JSON, leaving headroom for verbatim text +
                                # JSON syntax overhead. Lower this if you
                                # still hit "Unterminated string" parse errors.

ELEVENLABS_MODEL = "eleven_multilingual_v2"
ELEVENLABS_PCM_RATE = 22050
ELEVENLABS_MIN_PCM_BYTES = 2048

# Pricing reference — pre-set so the user sees a real estimate. ElevenLabs
# bills per-character at tier-dependent rates. We show a range covering the
# common tiers (Starter $5/mo, Pro $22/mo, Scale $99/mo).
# Source: elevenlabs.io/pricing (verify if billing changes).
COST_PER_1K_CHARS_LOW = 0.15   # ~ Scale tier
COST_PER_1K_CHARS_HIGH = 0.30  # ~ Starter tier


# --- API key + config loaders ------------------------------------------------

def load_anthropic_key() -> str:
    """Mirror play_engine's key lookup: env var, then ttrpg_key.txt."""
    env = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env:
        return env
    key_file = SCRIPT_DIR / "ttrpg_key.txt"
    if key_file.exists():
        try:
            return key_file.read_text(encoding="utf-8").strip()
        except Exception:
            return ""
    return ""


def load_elevenlabs_key(config: Dict) -> str:
    """Mirror the dashboard's 3-layer ElevenLabs key resolution
    (kenji_gui._tts_load_config). First hit wins:

      1. key.txt next to this script (or one dir up, or the bundle dir).
         First non-empty, non-comment line is the key.
      2. tts_config.json -> api_key field.
      3. ELEVENLABS_API_KEY environment variable.

    This is the same key the dashboard's Speak buttons use, so the user
    only sets it in one place."""
    # Layer 1: key.txt — search the same dirs the dashboard searches.
    search_dirs = [SCRIPT_DIR, SCRIPT_DIR.parent]
    seen = set()
    for d in search_dirs:
        try:
            rd = d.resolve()
        except Exception:
            continue
        if rd in seen:
            continue
        seen.add(rd)
        key_path = rd / "key.txt"
        if not key_path.exists():
            continue
        try:
            for line in key_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
        except Exception:
            continue
    # Layer 2: tts_config.json api_key field.
    cfg_key = (config.get("api_key") or "").strip()
    if cfg_key:
        return cfg_key
    # Layer 3: env var.
    return os.environ.get("ELEVENLABS_API_KEY", "").strip()


def load_voice_config() -> Dict:
    """Load tts_config.json. Returns the raw dict (not just character_voices)."""
    if not TTS_CONFIG.exists():
        raise FileNotFoundError(f"tts_config.json missing at {TTS_CONFIG}")
    with open(TTS_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def voice_id_for(speaker: str, config: Dict) -> Optional[str]:
    """Case-insensitive lookup in character_voices. Skips _doc keys.
    Returns the voice ID string, or None if not mapped / mapped to empty."""
    slots = config.get("character_voices", {})
    target = speaker.strip().lower()
    for key, value in slots.items():
        if key.startswith("_"):
            continue
        if key.strip().lower() == target:
            return value.strip() if isinstance(value, str) and value.strip() else None
    return None


# --- Chapter loader ---------------------------------------------------------

def load_chapter(path: Path) -> str:
    """Read the chapter md file as a single string."""
    if not path.is_file():
        raise FileNotFoundError(f"Chapter file not found: {path}")
    return path.read_text(encoding="utf-8")


# --- Claude-driven speaker parser -------------------------------------------

SPEAKER_PARSER_SYSTEM = """You are a dialogue attribution parser for an audiobook generator.

You receive a chapter of prose. You return ONLY a JSON array of segments.
Each segment is an object with exactly two keys:
  "speaker": the name of who is speaking. Use the exact display name of the
             character (e.g. "Kenji", "Sera"). If the prose is narration
             (description, action beats, internal thoughts, anything outside
             a dialogue attribution), use "Narrator". If a line of dialogue
             has no attribution and the speaker is ambiguous, also use
             "Narrator" so the quote is read by the narrator voice.
  "text":    the verbatim prose for that segment, with markdown formatting
             stripped (no #, *, _, --- dividers, no blockquote >). Quotes
             around dialogue MUST be preserved. Italics that indicate
             internal thought stay as plain text without underscores.

Rules:
1. Output ONLY the JSON array. No preamble, no commentary, no markdown
   code fences. Start with [ and end with ]. NEVER explain or describe the
   input - just return the JSON, even if the input is unusual.
2. Segments concatenate in the same order as the original prose.
3. Group consecutive sentences by the same speaker into ONE segment.
4. When dialogue is attributed mid-sentence (e.g. "Yes," she said, "I will."),
   produce one dialogue segment, then a narrator segment for the attribution,
   then another dialogue segment. The attribution itself is narrator prose.
5. Em-dashes that introduce dialogue (— "Yes,") or attribution beats
   (Kenji nodded. — "Fine.") split segments the same way.
6. Strip chapter titles and section dividers entirely. Skip "---" and
   "End of Chapter X" markers.
7. Keep proper nouns capitalized. Do not paraphrase, summarize, or modernize
   the prose. Verbatim text only.
8. If the input contains NO dialogue at all (pure narration, action
   description, or a single internal monologue), return the ENTIRE input
   as one Narrator segment. Do NOT refuse or explain - just wrap it.
9. LitRPG stat blocks, level-up notifications, status windows, attribute
   tables, spell lists, and inventory dumps ARE valid narrator content.
   Return them as Narrator segments verbatim. Examples that count as
   narration: "DING - LEVEL 4", "HP: 27 / AC: 15", "Cantrips: Arcane Edge",
   "Inventory updated", "+1 STR". Read them as the narrator would in an
   audiobook - just include the text.
10. If you genuinely cannot determine what to do with the input, return:
    [{"speaker": "Narrator", "text": "<entire input verbatim>"}]
    Do NOT return an explanation, a refusal, or commentary outside the JSON.

Example input 1:
"You stay," Kenji said. He turned to the road. The dust rose. "I'll walk."

Example output 1:
[
  {"speaker": "Kenji", "text": "\\"You stay,\\""},
  {"speaker": "Narrator", "text": "Kenji said. He turned to the road. The dust rose."},
  {"speaker": "Kenji", "text": "\\"I'll walk.\\""}
]

Example input 2 (stat block - NO dialogue):
DING - LEVEL 4
KENJI
HP: 27
AC: 15
STR 15 / +2

Example output 2:
[
  {"speaker": "Narrator", "text": "DING - LEVEL 4. KENJI. HP: 27. AC: 15. STR 15, plus 2."}
]
"""


def chunk_chapter(text: str, max_chars: int = CHUNK_MAX_CHARS) -> List[str]:
    """Split chapter prose into chunks of at most max_chars, on paragraph
    boundaries (blank lines). Each chunk is sent to Claude separately so we
    never blow past max_tokens for one response.

    Splits on `\\n\\s*\\n` (one or more blank lines). If a single paragraph
    exceeds max_chars on its own, it's emitted as its own chunk (Claude will
    handle it; the prompt is robust to long single paragraphs).
    """
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: List[str] = []
    current: List[str] = []
    current_size = 0
    for p in paragraphs:
        p_size = len(p)
        # Account for the "\n\n" joiner we'll insert
        joiner_size = 2 if current else 0
        if current and current_size + joiner_size + p_size > max_chars:
            chunks.append("\n\n".join(current))
            current = [p]
            current_size = p_size
        else:
            current.append(p)
            current_size += joiner_size + p_size
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _atomic_dump(path: Path, text: str) -> None:
    """Write `text` to `path` atomically. Uses a tmp file in the same dir
    plus os.replace, which sidesteps OneDrive's mid-write truncation."""
    try:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        # Best-effort fallback to direct write
        try:
            path.write_text(text, encoding="utf-8")
        except Exception:
            pass


def _claude_call(client, content: str):
    """Single Claude messages.create call with the standard system prompt.

    temperature=0 is critical: it makes the parser deterministic across runs.
    With the default temperature (1.0), the same chapter could parse into
    slightly different segments each time, and since the PCM cache is keyed
    by sha1(voice_id + text), any drift in segmentation produces cache
    misses and re-fires ElevenLabs for audio you already paid for."""
    return client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        temperature=0,
        system=SPEAKER_PARSER_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )


def _extract_raw_text(resp) -> str:
    parts = []
    for block in resp.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    raw = "".join(parts).strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```\s*$", "", raw)
    return raw


def _parse_one_chunk(chunk_text: str, api_key: str,
                      chunk_label: str = "",
                      allow_narrator_fallback: bool = True) -> List[Dict[str, str]]:
    """Send one chunk to Claude. Returns its segments. Raises RuntimeError
    on API failure or invalid JSON (after one retry).

    Auto-retries ONCE with a reinforcement prompt if Claude's first
    response is not valid JSON (handles cases where Claude explains a
    stat block instead of wrapping it). If the retry also fails AND
    allow_narrator_fallback is True, falls back to treating the whole
    chunk as one Narrator segment (no exception)."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic SDK not installed. Run: pip install anthropic"
        )
    client = anthropic.Anthropic(api_key=api_key)

    # Attempt 1: standard call
    try:
        resp = _claude_call(client, chunk_text)
    except Exception as e:
        raise RuntimeError(f"Claude API call failed{chunk_label}: {e}")
    stop_reason = getattr(resp, "stop_reason", None)
    raw = _extract_raw_text(resp)
    segments = None
    first_error = None
    try:
        segments = json.loads(raw)
    except json.JSONDecodeError as e:
        first_error = e

    # Attempt 2: retry with explicit reinforcement if first attempt failed
    if segments is None:
        retry_msg = (
            "The previous response was not valid JSON. Please retry. Even "
            "if the input has no dialogue, no characters, or looks like a "
            "stat block / system message / level-up screen, you MUST "
            "return a JSON array. The simplest valid response for any "
            "input is:\n"
            "[{\"speaker\": \"Narrator\", \"text\": \"<verbatim input>\"}]\n\n"
            "Input to parse:\n\n" + chunk_text
        )
        try:
            resp = _claude_call(client, retry_msg)
            stop_reason = getattr(resp, "stop_reason", None)
            raw = _extract_raw_text(resp)
            segments = json.loads(raw)
        except json.JSONDecodeError as e:
            # Persist the raw response so we can debug post-hoc.
            dump = SCRIPT_DIR / "_chapter_tts_last_parse.txt"
            _atomic_dump(dump, raw)
            if allow_narrator_fallback:
                print(f"      WARNING: Claude refused JSON twice{chunk_label} - "
                      f"falling back to single Narrator segment for this chunk.")
                print(f"      (Raw response saved to {dump})")
                return [{"speaker": "Narrator", "text": chunk_text.strip()}]
            hint = ""
            if stop_reason == "max_tokens":
                hint = ("\n  (stop_reason=max_tokens - chunk too large. "
                        "Try lowering CHUNK_MAX_CHARS in chapter_tts.py.)")
            raise RuntimeError(
                f"Claude returned non-JSON{chunk_label} (after retry). "
                f"Saved to {dump}. Error: {e}{hint}"
            )
        except Exception as e:
            raise RuntimeError(f"Claude API retry failed{chunk_label}: {e}")

    if not isinstance(segments, list):
        if allow_narrator_fallback:
            print(f"      WARNING: Claude response{chunk_label} not a list - "
                  f"falling back to single Narrator segment.")
            return [{"speaker": "Narrator", "text": chunk_text.strip()}]
        raise RuntimeError(f"Claude response{chunk_label} was not a JSON array.")
    cleaned: List[Dict[str, str]] = []
    for i, seg in enumerate(segments):
        if not isinstance(seg, dict):
            raise RuntimeError(f"Segment {i}{chunk_label} is not an object: {seg!r}")
        speaker = str(seg.get("speaker", "")).strip()
        text = str(seg.get("text", "")).strip()
        if not speaker:
            speaker = "Narrator"
        if not text:
            continue
        cleaned.append({"speaker": speaker, "text": text})
    return cleaned


def parse_speakers_via_claude(chapter_text: str, api_key: str) -> List[Dict[str, str]]:
    """Send the chapter to Claude Haiku for speaker attribution.

    Long chapters are split into chunks (CHUNK_MAX_CHARS each) at paragraph
    boundaries; each chunk is parsed separately and the segments are
    concatenated. This sidesteps the per-response max_tokens cap for
    chapters of ~30k+ chars.

    Returns a list of {speaker, text} dicts.
    Raises RuntimeError on API failure or invalid JSON response."""
    chunks = chunk_chapter(chapter_text, CHUNK_MAX_CHARS)
    print(f"      Splitting into {len(chunks)} chunk(s) "
          f"(<= {CHUNK_MAX_CHARS:,} chars each)")
    all_segments: List[Dict[str, str]] = []
    for i, chunk in enumerate(chunks, start=1):
        label = f" (chunk {i}/{len(chunks)})"
        print(f"      Parsing chunk {i}/{len(chunks)} ({len(chunk):,} chars)...")
        segs = _parse_one_chunk(chunk, api_key, chunk_label=label)
        all_segments.extend(segs)
    if not all_segments:
        raise RuntimeError("Parser returned zero valid segments.")
    return all_segments


# --- Validation -------------------------------------------------------------

def validate_voice_coverage(
    segments: List[Dict[str, str]], config: Dict
) -> Tuple[bool, List[str], Dict[str, str]]:
    """For each unique speaker in segments, check that tts_config.character_voices
    has a non-empty voice ID. Returns (ok, missing_speakers, voice_map).

    voice_map is a dict {speaker_lower: voice_id} for downstream use, populated
    only for the speakers that DID resolve (so segments using a missing speaker
    won't accidentally pick a wrong voice if you ignore the abort)."""
    unique_speakers = []
    seen = set()
    for seg in segments:
        s = seg["speaker"]
        sl = s.lower()
        if sl not in seen:
            seen.add(sl)
            unique_speakers.append(s)
    missing: List[str] = []
    voice_map: Dict[str, str] = {}
    for speaker in unique_speakers:
        vid = voice_id_for(speaker, config)
        if vid:
            voice_map[speaker.lower()] = vid
        else:
            missing.append(speaker)
    return (len(missing) == 0), missing, voice_map


# --- Cost preview -----------------------------------------------------------

def estimate_cost(segments: List[Dict[str, str]]) -> Dict:
    """Compute total character count + cost range.
    Returns {chars, segments, est_low, est_high}."""
    total_chars = sum(len(seg["text"]) for seg in segments)
    est_low = total_chars / 1000.0 * COST_PER_1K_CHARS_LOW
    est_high = total_chars / 1000.0 * COST_PER_1K_CHARS_HIGH
    return {
        "chars": total_chars,
        "segments": len(segments),
        "est_low": est_low,
        "est_high": est_high,
    }


def print_estimate(est: Dict, output_path: Path) -> None:
    print()
    print("=== Audio Generation Preview ===")
    print(f"  Segments:       {est['segments']}")
    print(f"  Total chars:    {est['chars']:,}")
    print(f"  ElevenLabs $:   ${est['est_low']:.2f} (Scale) - ${est['est_high']:.2f} (Starter)")
    print(f"  Output file:    {output_path}")
    print(f"  Format:         WAV @ {ELEVENLABS_PCM_RATE} Hz mono 16-bit")
    print()


def confirm_with_user() -> bool:
    """Prompt y/n. Returns True if user typed something starting with 'y'."""
    try:
        ans = input("Proceed and burn credits? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return ans.startswith("y")


# --- ElevenLabs synth -------------------------------------------------------

def fetch_pcm(api_key: str, voice_id: str, text: str,
              retries: int = 4) -> bytes:
    """POST one segment to ElevenLabs, return raw PCM bytes.
    Retries on transient HTTP errors + connection drops (TCP resets are
    common from ElevenLabs under load). Exponential backoff between tries.
    Raises RuntimeError on hard failure."""
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
           f"/stream?output_format=pcm_{ELEVENLABS_PCM_RATE}")
    body = json.dumps({
        "text": text,
        "model_id": ELEVENLABS_MODEL,
    }).encode("utf-8")
    last_err = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("xi-api-key", api_key)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                pcm = resp.read()
            if not pcm or len(pcm) < ELEVENLABS_MIN_PCM_BYTES:
                raise RuntimeError(
                    f"ElevenLabs returned {len(pcm) if pcm else 0} bytes "
                    f"(below {ELEVENLABS_MIN_PCM_BYTES} threshold)"
                )
            return pcm
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.reason}"
            try:
                body_msg = e.read().decode("utf-8", errors="replace")[:500]
                last_err += f"\n  body: {body_msg}"
            except Exception:
                pass
            # 5xx + 429 = transient; 4xx = stop retrying (bad key / bad voice)
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                backoff = 2.0 * (2 ** attempt)  # 2, 4, 8, 16s
                print(f"    HTTP {e.code} - retrying in {backoff:.1f}s "
                      f"(attempt {attempt+1}/{retries+1})")
                time.sleep(backoff)
                continue
            raise RuntimeError(last_err)
        except Exception as e:
            # Connection reset, timeout, DNS hiccup, etc. — all transient.
            last_err = f"{type(e).__name__}: {e}"
            if attempt < retries:
                backoff = 2.0 * (2 ** attempt)  # 2, 4, 8, 16s
                print(f"    network error ({type(e).__name__}) - retrying in "
                      f"{backoff:.1f}s (attempt {attempt+1}/{retries+1})")
                time.sleep(backoff)
                continue
            raise RuntimeError(last_err)
    raise RuntimeError(last_err or "fetch_pcm exhausted retries")


# --- Per-segment PCM cache --------------------------------------------------

def _segment_cache_dir(chapter_path: Path) -> Path:
    """Return the dir where this chapter's per-segment PCM cache lives.
    Lives under voice_audio/_cache/<chapter_stem>/."""
    return VOICE_AUDIO_DIR / "_cache" / chapter_path.stem


def _segment_hash(voice_id: str, text: str) -> str:
    """Stable filename for a (voice_id, text) pair. Used as the cache key.
    Re-using the same text with the same voice gives the same filename, so
    re-runs of the same chapter reuse cached audio for free."""
    h = hashlib.sha1((voice_id + "\n" + text).encode("utf-8")).hexdigest()
    return h[:16]


def _save_pcm_cache(cache_dir: Path, voice_id: str, text: str, pcm: bytes) -> None:
    """Write PCM to the cache atomically. Best-effort - cache failures are
    non-fatal (we still have the bytes in memory for the current run)."""
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / (_segment_hash(voice_id, text) + ".pcm")
        tmp = cache_path.with_suffix(".pcm.tmp")
        tmp.write_bytes(pcm)
        os.replace(tmp, cache_path)
    except Exception:
        pass


def _load_pcm_cache(cache_dir: Path, voice_id: str, text: str) -> Optional[bytes]:
    """Return cached PCM if present and looks valid, else None."""
    cache_path = cache_dir / (_segment_hash(voice_id, text) + ".pcm")
    if not cache_path.is_file():
        return None
    try:
        size = cache_path.stat().st_size
        if size < ELEVENLABS_MIN_PCM_BYTES:
            return None
        return cache_path.read_bytes()
    except Exception:
        return None


def _verify_cache_writable(cache_dir: Path) -> Tuple[bool, str]:
    """Probe the cache dir at the start of synth_segments. Tries to write
    and immediately delete a tiny test file. Returns (ok, reason).

    Catches the silent-cache-failure mode that would otherwise lose every
    fetched PCM on a later crash. If the cache can't be written, we want
    the user to know BEFORE they confirm the cost preview."""
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"cannot create cache dir: {e}"
    probe = cache_dir / ".write_probe"
    try:
        probe.write_bytes(b"ok")
        # Read back to confirm we can also read what we wrote.
        if probe.read_bytes() != b"ok":
            return False, "wrote probe but read-back mismatched"
        probe.unlink()
    except Exception as e:
        return False, f"probe write/read failed: {e}"
    return True, ""


def synth_segments(
    segments: List[Dict[str, str]],
    voice_map: Dict[str, str],
    api_key: str,
    cache_dir: Optional[Path] = None,
) -> List[bytes]:
    """Call ElevenLabs once per segment in order, return list of PCM bytes.

    If cache_dir is provided, each PCM is cached to disk after fetch, and
    subsequent runs skip the API call when the cache file exists. This
    means a mid-chapter failure resumes from where it stopped instead of
    re-paying for already-fetched segments.

    Before starting, verifies the cache dir is actually writable. If not
    (permission denied, OneDrive lock, disk full), prints a loud warning
    and asks whether to proceed without cache - because proceeding without
    cache means any mid-run failure loses every PCM synthesized so far."""
    # Verify cache health BEFORE we burn a single credit (CRIT-2 fix).
    if cache_dir is not None:
        ok, reason = _verify_cache_writable(cache_dir)
        if not ok:
            print()
            print("=" * 70)
            print("  WARNING: PCM cache is NOT writable.")
            print("=" * 70)
            print(f"  Cache dir:  {cache_dir}")
            print(f"  Reason:     {reason}")
            print()
            print("  This means PCMs will live in memory ONLY. If anything")
            print("  fails mid-chapter (network drop, ElevenLabs hiccup),")
            print("  every segment synthesized so far is LOST and you'll")
            print("  pay for them again on the next run.")
            print()
            print("  This is exactly the failure mode that cost real money")
            print("  on the first Book 1 Ch 5 run. Strongly recommend you")
            print("  fix the cache dir before continuing.")
            print()
            try:
                ans = input("  Proceed WITHOUT cache anyway? (y/N): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                ans = ""
            if not ans.startswith("y"):
                raise RuntimeError(
                    "User aborted at unwritable-cache warning. "
                    "No ElevenLabs credits spent."
                )
            # User chose to proceed unprotected. Disable cache for this run.
            print("  Continuing without cache. Be aware of the risk.")
            cache_dir = None

    pcms: List[bytes] = []
    cache_hits = 0
    api_calls = 0
    for i, seg in enumerate(segments, start=1):
        speaker = seg["speaker"]
        text = seg["text"]
        voice_id = voice_map[speaker.lower()]
        preview = text[:60].replace("\n", " ")
        # Try cache first
        if cache_dir is not None:
            cached = _load_pcm_cache(cache_dir, voice_id, text)
            if cached is not None:
                cache_hits += 1
                print(f"  [{i}/{len(segments)}] {speaker:<14} "
                      f"\"{preview}{'...' if len(text) > 60 else ''}\"  (cached)")
                pcms.append(cached)
                continue
        print(f"  [{i}/{len(segments)}] {speaker:<14} "
              f"\"{preview}{'...' if len(text) > 60 else ''}\"")
        try:
            pcm = fetch_pcm(api_key, voice_id, text)
        except Exception as e:
            partial = (f"  ({i-1} segments succeeded, {cache_hits} from cache, "
                       f"{api_calls} fresh. Re-run this chapter to resume "
                       f"from this point - the cached audio is preserved.)")
            raise RuntimeError(f"Segment {i} ({speaker}) failed: {e}\n{partial}")
        api_calls += 1
        pcms.append(pcm)
        if cache_dir is not None:
            _save_pcm_cache(cache_dir, voice_id, text, pcm)
    if cache_dir is not None and cache_hits:
        print(f"      ({cache_hits}/{len(segments)} segments reused from cache, "
              f"{api_calls} fresh API calls)")
    return pcms


# --- Stitch + write ---------------------------------------------------------

def stitch_and_save(pcms: List[bytes], output_path: Path) -> int:
    """Use tts_stitcher to wrap PCM into a single WAV.
    Returns the number of bytes written."""
    # Import lazily so a missing module doesn't break --dry-run.
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        import tts_stitcher
    except ImportError as e:
        raise RuntimeError(f"tts_stitcher module missing: {e}")
    wav = tts_stitcher.stitch_pcm_to_wav(
        pcms,
        rate_hz=ELEVENLABS_PCM_RATE,
        inter_segment_silence_ms=120,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(wav)
    return len(wav)


# --- Main pipeline ----------------------------------------------------------

def derive_output_path(chapter_path: Path,
                        explicit: Optional[str]) -> Path:
    if explicit:
        # Allow absolute or relative-to-voice_audio.
        p = Path(explicit)
        if not p.is_absolute():
            p = VOICE_AUDIO_DIR / p
        if p.suffix.lower() != ".wav":
            p = p.with_suffix(".wav")
        return p
    return VOICE_AUDIO_DIR / (chapter_path.stem + ".wav")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a chapter markdown file to an audiobook WAV "
                    "using Claude for speaker attribution + ElevenLabs for "
                    "voice synthesis.",
    )
    parser.add_argument("chapter", type=str,
                        help="Path to the chapter .md file")
    parser.add_argument("--out", type=str, default=None,
                        help="Output WAV path (default: voice_audio/<chapter_stem>.wav)")
    parser.add_argument("--yes", action="store_true",
                        help="Skip the cost-confirmation prompt")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse + validate + estimate cost, but do NOT "
                             "fire ElevenLabs and do NOT write output")
    parser.add_argument("--save-segments", type=str, default=None,
                        help="Also save the parsed segments to this JSON path "
                             "(useful for inspecting the parser output)")
    parser.add_argument("--load-segments", type=str, default=None,
                        help="Skip Claude parsing; load pre-parsed segments "
                             "from this JSON path. Used by the interactive "
                             "launcher to avoid double-billing Claude after "
                             "the user resolves missing voice IDs.")
    args = parser.parse_args()

    chapter_path = Path(args.chapter)
    output_path = derive_output_path(chapter_path, args.out)

    # Load API keys first (fail fast).
    anthropic_key = load_anthropic_key()
    if not anthropic_key:
        print("ERROR: No ANTHROPIC_API_KEY env var and no ttrpg_key.txt next "
              "to this script. Cannot call Claude for speaker parsing.",
              file=sys.stderr)
        sys.exit(2)

    # Step 1: load chapter
    print(f"[1/6] Loading chapter: {chapter_path}")
    try:
        chapter_text = load_chapter(chapter_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"      {len(chapter_text):,} chars in source")

    # Step 2: parse via Claude — OR load pre-parsed segments if the
    # interactive launcher already handled the parse step.
    if args.load_segments:
        print(f"[2/6] Loading cached segments from {args.load_segments}...")
        try:
            with open(args.load_segments, "r", encoding="utf-8") as f:
                segments = json.load(f)
            if not isinstance(segments, list):
                raise RuntimeError("Cached segments file is not a JSON array.")
        except Exception as e:
            print(f"ERROR loading cached segments: {e}", file=sys.stderr)
            sys.exit(3)
        print(f"      {len(segments)} segments loaded (Claude skipped)")
    else:
        print(f"[2/6] Parsing speakers via {CLAUDE_MODEL}...")
        try:
            segments = parse_speakers_via_claude(chapter_text, anthropic_key)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(3)
        print(f"      {len(segments)} segments parsed")

    if args.save_segments:
        Path(args.save_segments).write_text(
            json.dumps(segments, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"      Segments saved to {args.save_segments}")

    # Step 3: load voice config + validate coverage
    print(f"[3/6] Validating voice ID coverage...")
    try:
        config = load_voice_config()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(4)
    ok, missing, voice_map = validate_voice_coverage(segments, config)
    print(f"      {len(voice_map)} speakers mapped")
    if not ok:
        print()
        print("=== MISSING VOICE IDs ===")
        print(f"  The following speakers are not mapped in tts_config.json:")
        for name in missing:
            print(f"    - {name}")
        print()
        print(f"  Edit:  {TTS_CONFIG}")
        print(f"  Add each speaker to the 'character_voices' block with their")
        print(f"  ElevenLabs voice ID (find IDs at https://elevenlabs.io/app/voice-library).")
        print()
        print("Aborting before any ElevenLabs credits are spent.")
        sys.exit(5)

    # Step 4: cost preview + confirm
    est = estimate_cost(segments)
    print_estimate(est, output_path)
    if args.dry_run:
        print("[--dry-run] Stopping here. No audio generated.")
        sys.exit(0)
    if not args.yes:
        if not confirm_with_user():
            print("User declined. Exiting without burning credits.")
            sys.exit(0)

    # Step 5: ElevenLabs API key (same 3-layer resolution as the dashboard)
    elevenlabs_key = load_elevenlabs_key(config)
    if not elevenlabs_key:
        print("ERROR: No ElevenLabs API key found. The tool checks (in order):",
              file=sys.stderr)
        print(f"  1. key.txt in {SCRIPT_DIR} (or one dir up)", file=sys.stderr)
        print("  2. 'api_key' field in tts_config.json", file=sys.stderr)
        print("  3. ELEVENLABS_API_KEY environment variable", file=sys.stderr)
        print("\nThe dashboard reads from the same locations - so whichever you "
              "use for the Speak buttons also works here.", file=sys.stderr)
        sys.exit(6)

    # Step 6: synth + stitch + save (with per-segment cache for resume-on-failure)
    cache_dir = _segment_cache_dir(chapter_path)
    print(f"[5/6] Synthesizing {len(segments)} segments via ElevenLabs...")
    print(f"      Cache: {cache_dir}")
    t0 = time.time()
    try:
        pcms = synth_segments(segments, voice_map, elevenlabs_key, cache_dir=cache_dir)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(7)
    elapsed = time.time() - t0
    print(f"      Synth complete in {elapsed:.1f}s")

    print(f"[6/6] Stitching + saving to {output_path}...")
    try:
        nbytes = stitch_and_save(pcms, output_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(8)
    total_pcm = sum(len(p) for p in pcms)
    duration_s = total_pcm / (ELEVENLABS_PCM_RATE * 2)
    print(f"      Wrote {nbytes / 1024 / 1024:.1f} MB "
          f"(~{duration_s / 60:.1f} min audio)")
    print()
    print(f"Done. Output: {output_path}")
    print(f"      Cache kept at {cache_dir} - re-running this chapter")
    print(f"      will reuse cached audio at zero cost. Delete to force re-synth.")


if __name__ == "__main__":
    main()
