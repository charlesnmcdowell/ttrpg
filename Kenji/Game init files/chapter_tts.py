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
CLAUDE_MAX_TOKENS = 8000  # one chapter can produce ~30-100 segments

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
   code fences. Start with [ and end with ].
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

Example input:
"You stay," Kenji said. He turned to the road. The dust rose. "I'll walk."

Example output:
[
  {"speaker": "Kenji", "text": "\\"You stay,\\""},
  {"speaker": "Narrator", "text": "Kenji said. He turned to the road. The dust rose."},
  {"speaker": "Kenji", "text": "\\"I'll walk.\\""}
]
"""


def parse_speakers_via_claude(chapter_text: str, api_key: str) -> List[Dict[str, str]]:
    """Send the chapter to Claude Haiku for speaker attribution.
    Returns a list of {speaker, text} dicts.
    Raises RuntimeError on API failure or invalid JSON response."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic SDK not installed. Run: pip install anthropic"
        )
    client = anthropic.Anthropic(api_key=api_key)
    try:
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=SPEAKER_PARSER_SYSTEM,
            messages=[{"role": "user", "content": chapter_text}],
        )
    except Exception as e:
        raise RuntimeError(f"Claude API call failed: {e}")
    text_parts = []
    for block in resp.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)
    raw = "".join(text_parts).strip()
    # Strip possible accidental code fences.
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```\s*$", "", raw)
    try:
        segments = json.loads(raw)
    except json.JSONDecodeError as e:
        # Save the raw output for debugging, then re-raise.
        dump = SCRIPT_DIR / "_chapter_tts_last_parse.txt"
        try:
            dump.write_text(raw, encoding="utf-8")
        except Exception:
            pass
        raise RuntimeError(
            f"Claude returned non-JSON. Saved to {dump}. Error: {e}"
        )
    if not isinstance(segments, list):
        raise RuntimeError("Claude response was not a JSON array.")
    cleaned: List[Dict[str, str]] = []
    for i, seg in enumerate(segments):
        if not isinstance(seg, dict):
            raise RuntimeError(f"Segment {i} is not an object: {seg!r}")
        speaker = str(seg.get("speaker", "")).strip()
        text = str(seg.get("text", "")).strip()
        if not speaker:
            speaker = "Narrator"
        if not text:
            continue  # skip empty segments
        cleaned.append({"speaker": speaker, "text": text})
    if not cleaned:
        raise RuntimeError("Parser returned zero valid segments.")
    return cleaned


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
              retries: int = 2) -> bytes:
    """POST one segment to ElevenLabs, return raw PCM bytes.
    Retries on transient HTTP errors. Raises RuntimeError on hard failure."""
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
            # Read the error body for the API's structured message
            try:
                body_msg = e.read().decode("utf-8", errors="replace")[:500]
                last_err += f"\n  body: {body_msg}"
            except Exception:
                pass
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(last_err)
        except Exception as e:
            last_err = str(e)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(last_err)
    raise RuntimeError(last_err or "fetch_pcm exhausted retries")


def synth_segments(
    segments: List[Dict[str, str]],
    voice_map: Dict[str, str],
    api_key: str,
) -> List[bytes]:
    """Call ElevenLabs once per segment in order, return list of PCM bytes."""
    pcms: List[bytes] = []
    for i, seg in enumerate(segments, start=1):
        speaker = seg["speaker"]
        text = seg["text"]
        voice_id = voice_map[speaker.lower()]
        preview = text[:60].replace("\n", " ")
        print(f"  [{i}/{len(segments)}] {speaker:<14} \"{preview}{'...' if len(text) > 60 else ''}\"")
        try:
            pcm = fetch_pcm(api_key, voice_id, text)
        except Exception as e:
            raise RuntimeError(f"Segment {i} ({speaker}) failed: {e}")
        pcms.append(pcm)
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

    # Step 2: parse via Claude
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

    # Step 6: synth + stitch + save
    print(f"[5/6] Synthesizing {len(segments)} segments via ElevenLabs...")
    t0 = time.time()
    try:
        pcms = synth_segments(segments, voice_map, elevenlabs_key)
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
    duration_s = total_pcm / (ELEVENLABS_PCM_RATE * 2)  # 16-bit mono
    print(f"      Wrote {nbytes / 1024 / 1024:.1f} MB "
          f"(~{duration_s / 60:.1f} min audio)")
    print()
    print(f"Done. Output: {output_path}")


if __name__ == "__main__":
    main()
