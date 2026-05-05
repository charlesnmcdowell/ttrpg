#!/usr/bin/env python3
"""tts_voice_designer.py — lazy voice generation via the ElevenLabs Voice
Design API.

Workflow:
  1. The dashboard hits a new NPC (or a tracked NPC with no sticky voice).
  2. The resolver looks up the matching pool bucket. If the bucket has <
     BUCKET_CAP voices already in it, the dashboard calls
     `design_and_save_voice()` here to generate ONE new voice.
  3. Voice Design API returns 3 previews. We auto-pick #1, then call the
     /v1/text-to-voice/{generated_voice_id} endpoint to commit it to the
     user's voice library — that returns the final voice_id we'll use forever.
  4. Caller saves the new voice_id to tts_voice_pool.json (so subsequent
     NPCs in the same bucket either reuse it or trigger another generation
     until the cap is hit).

Cost surface:
  - Voice Design itself only charges for preview-text characters (~200 chars
    per generation = trivial cost). The voice slot itself is free below the
    tier cap (Pro = 160 slots, more than enough for 18-voice pool).
  - We deliberately do NOT generate previews the user reviews/picks from —
    we just take #1. Adds zero round-trips, zero per-NPC friction. If the
    voice is bad, the user can delete the entry from npc_voices.json + the
    pool config and the next encounter will re-design.

This module is HTTP only — no Tk, no caching, no playback. The caller is
responsible for cost confirmation, pool persistence, and retry on failure.
"""

from __future__ import annotations
import base64
import json
import re
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# Hard ceiling: stop generating once each (race, gender) bucket has this many
# voices. After the cap, the resolver reuses an existing bucket voice via the
# stable-pick hash. Default 3 matches the original pool design (3 humanoid +
# 3 orcish + 3 elfish per gender = 18 voices total).
BUCKET_CAP = 3

# A short generic line the API uses to render the 3 preview clips. We never
# play this — we just need ElevenLabs to accept the design call. Keep short
# to keep the per-character preview charge near zero (~30 chars).
DEFAULT_PREVIEW_TEXT = "Hold steady. Something approaches from the south."

# Description templates per (race, gender) bucket. The Voice Design API
# accepts free-form English; these are intentionally evocative + specific
# enough to bias the generator toward a recognizable archetype, not generic
# defaults. The {age_phrase} and {accent_phrase} slots are filled in when
# the NPC metadata supplies that info.
_RACE_BUCKET_DESCRIPTIONS = {
    ("humanoid", "male"):
        "An adult male with a clear, grounded human voice. {age_phrase} "
        "{accent_phrase} Conversational, confident, with steady breath. "
        "Suitable for shopkeepers, guards, fellow travelers — the kind of "
        "person you meet on the road and might trust or might not.",
    ("humanoid", "female"):
        "An adult female with a warm, resonant human voice. {age_phrase} "
        "{accent_phrase} Conversational, expressive, slight rasp on the low "
        "register. Suitable for innkeepers, scouts, allies — present, alert, "
        "human.",
    ("orcish", "male"):
        "An adult male with a deep, gravelly voice — half-orc or rough "
        "frontier stock. {age_phrase} Mountain accent, chest-resonance, "
        "consonants slightly clipped. Suitable for warriors, smiths, "
        "wardens — physical presence in every word.",
    ("orcish", "female"):
        "An adult female with a low, rough-edged voice — half-orc or "
        "ankuspawn lineage. {age_phrase} Mountain or steppe accent, "
        "controlled power, words land with weight. Suitable for hunters, "
        "shamans, soldiers — never delicate, always deliberate.",
    ("elfish", "male"):
        "An adult male with a lighter, melodic voice — elven or fey lineage. "
        "{age_phrase} {accent_phrase} Slight breath behind every word, "
        "vowels held a beat longer than human speech. Suitable for scholars, "
        "rangers, courtiers — old patience in a younger-sounding voice.",
    ("elfish", "female"):
        "An adult female with a soft, sylvan voice — elf or half-elf. "
        "{age_phrase} {accent_phrase} Cool clarity, faint lilt, low-register "
        "calm. Suitable for diplomats, healers, mages — quiet authority.",
}


def build_voice_description(race_bucket: str, gender: str,
                              npc_meta: Optional[Dict] = None) -> str:
    """Compose an ElevenLabs Voice Design prompt from bucket + NPC metadata.

    Args:
        race_bucket: 'humanoid' | 'orcish' | 'elfish'
        gender:      'male' | 'female'
        npc_meta:    optional {race, gender, age, role, accent, personality}
                     dict — fills in the {age_phrase} / {accent_phrase} slots.
                     Missing keys produce empty fillers.

    Returns: a free-form English description suitable for the API.
    """
    base = _RACE_BUCKET_DESCRIPTIONS.get(
        (race_bucket, gender),
        "An adult voice. Clear, conversational, mid-register. "
        "{age_phrase} {accent_phrase}"
    )
    meta = npc_meta or {}
    age = (meta.get("age") or "").strip().lower()
    accent = (meta.get("accent") or "").strip()
    age_phrase = ""
    if age:
        if any(t in age for t in ("young", "teen", "twenty", "20s")):
            age_phrase = "Voice reads early-twenties — fresh, less weathered."
        elif any(t in age for t in ("old", "elder", "sixty", "seventy", "60", "70", "80")):
            age_phrase = "Voice reads older — gravel in the lower register, breath used judiciously."
        elif any(t in age for t in ("middle", "forty", "fifty", "40", "50")):
            age_phrase = "Voice reads middle-aged — settled, lived-in."
    accent_phrase = f"Speaks with a {accent} accent." if accent else ""
    return base.format(age_phrase=age_phrase, accent_phrase=accent_phrase).strip()


@dataclass
class DesignResult:
    """What design_and_save_voice returns on success."""
    voice_id: str          # final library voice_id, ready for TTS
    description_used: str  # the prompt we sent (logged for debugging)
    cost_chars: int        # preview text length (rough credit estimate)


def _api_post(url: str, api_key: str, body: dict, timeout: int = 60
               ) -> Tuple[Optional[dict], Optional[str]]:
    """POST JSON to ElevenLabs, return (parsed_json_or_None, error_str_or_None).
    Never raises — caller decides how to surface the error."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
    )
    req.add_header("xi-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            err = str(e)
        return None, f"HTTP {e.code}: {err}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    try:
        return json.loads(raw.decode("utf-8")), None
    except Exception as e:
        return None, f"JSON parse: {e} (first 200 bytes: {raw[:200]!r})"


def design_and_save_voice(
    api_key: str,
    description: str,
    npc_name: str,
    *,
    preview_text: str = DEFAULT_PREVIEW_TEXT,
) -> Tuple[Optional[DesignResult], Optional[str]]:
    """Two-step Voice Design call: design (get 3 previews) → save preview #1
    to the user's library. Returns (DesignResult, None) on success or
    (None, error_message) on failure. Never raises.

    The npc_name is used as the saved voice's display name in the user's
    ElevenLabs library so they can identify it later (e.g. delete it if they
    don't like the result and want re-generation on next encounter).
    """
    # Step 1: design — returns 3 previews, each with a generated_voice_id.
    design_body = {
        "voice_description": description,
        "text": preview_text,
        # auto_generate_text=True would let ElevenLabs pick the preview text
        # for us, but using our own keeps the cost predictable + auditable.
        "auto_generate_text": False,
    }
    design_resp, err = _api_post(
        "https://api.elevenlabs.io/v1/text-to-voice/design",
        api_key, design_body,
    )
    if err:
        return None, f"design step: {err}"
    previews = (design_resp or {}).get("previews") or []
    if not previews:
        return None, f"design step: no previews returned (response keys: {list((design_resp or {}).keys())})"
    # Pick #1 deterministically. If the user wants control, they can edit
    # the saved voice_id out of npc_voices.json + pool to force a re-design.
    chosen = previews[0]
    generated_voice_id = chosen.get("generated_voice_id")
    if not generated_voice_id:
        return None, "design step: preview missing generated_voice_id"

    # Step 2: save preview to user's library — returns final voice_id.
    # Display name uses the NPC name so the library entry is identifiable.
    safe_name = re.sub(r"[^\w\- ]", "", npc_name)[:60].strip() or "Unnamed NPC"
    save_body = {
        "voice_name": f"TTRPG: {safe_name}",
        "voice_description": description,
        "generated_voice_id": generated_voice_id,
    }
    save_resp, err = _api_post(
        "https://api.elevenlabs.io/v1/text-to-voice",
        api_key, save_body,
    )
    if err:
        return None, f"save step: {err}"
    final_voice_id = (save_resp or {}).get("voice_id")
    if not final_voice_id:
        return None, f"save step: response missing voice_id (keys: {list((save_resp or {}).keys())})"

    return DesignResult(
        voice_id=final_voice_id,
        description_used=description,
        cost_chars=len(preview_text),
    ), None


# ---------------------------------------------------------------------------
# Self-tests — exercise the description builder + the API call shape against
# a stubbed HTTP layer so we don't burn real ElevenLabs credits to validate.
# ---------------------------------------------------------------------------

def _test_runner():
    failures = []

    # 1. Description builder produces non-empty text for every bucket.
    for race in ("humanoid", "orcish", "elfish"):
        for gender in ("male", "female"):
            d = build_voice_description(race, gender)
            if len(d) < 50:
                failures.append(f"description too short for {race}.{gender}: {d!r}")
            if "{age_phrase}" in d or "{accent_phrase}" in d:
                failures.append(f"unfilled template slots in {race}.{gender}: {d!r}")

    # 2. Description picks up age + accent metadata.
    d = build_voice_description("humanoid", "female",
                                  {"age": "elderly", "accent": "northern"})
    if "older" not in d.lower() or "northern" not in d.lower():
        failures.append(f"age/accent not threaded: {d!r}")

    # 3. Stub the HTTP layer and verify both API steps fire in order with
    #    the correct payload shape.
    api_log = []
    fake_design_resp = {
        "previews": [
            {"generated_voice_id": "gen_abc123", "audio_base_64": "..."},
            {"generated_voice_id": "gen_def456", "audio_base_64": "..."},
            {"generated_voice_id": "gen_ghi789", "audio_base_64": "..."},
        ],
    }
    fake_save_resp = {"voice_id": "FINAL_VOICE_xyz"}

    def fake_urlopen(req, timeout=None):
        url = req.full_url
        body = json.loads(req.data.decode("utf-8"))
        api_log.append({"url": url, "body": body})
        # Return the appropriate stubbed response based on URL.
        if url.endswith("/design"):
            payload = json.dumps(fake_design_resp).encode("utf-8")
        else:
            payload = json.dumps(fake_save_resp).encode("utf-8")
        class FakeResp:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def read(self): return payload
        return FakeResp()

    real_urlopen = urllib.request.urlopen
    urllib.request.urlopen = fake_urlopen
    try:
        result, err = design_and_save_voice(
            api_key="fake-key",
            description="A halfling woman, gruff voice.",
            npc_name="Maren Ashby",
        )
    finally:
        urllib.request.urlopen = real_urlopen

    if err:
        failures.append(f"unexpected error: {err}")
    if not result or result.voice_id != "FINAL_VOICE_xyz":
        failures.append(f"wrong voice_id: {result}")
    if len(api_log) != 2:
        failures.append(f"expected 2 API calls, got {len(api_log)}")
    elif not api_log[0]["url"].endswith("/design"):
        failures.append(f"first call not /design: {api_log[0]['url']}")
    elif api_log[1]["body"].get("generated_voice_id") != "gen_abc123":
        failures.append(f"save step didn't pick preview #1: {api_log[1]['body']}")
    elif "TTRPG: Maren Ashby" not in api_log[1]["body"].get("voice_name", ""):
        failures.append(f"save name missing NPC: {api_log[1]['body'].get('voice_name')}")

    # 4. Error handling: stub a failure and verify we return (None, error).
    def failing_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized",
                                       {}, None)
    urllib.request.urlopen = failing_urlopen
    try:
        result, err = design_and_save_voice("bad-key", "desc", "Test")
    finally:
        urllib.request.urlopen = real_urlopen
    if result is not None or err is None or "401" not in err:
        failures.append(f"expected 401 error, got result={result} err={err!r}")

    if failures:
        print(f"FAIL: {len(failures)} test(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"OK: all designer tests passed (4 cases, 14 sub-checks)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_test_runner())
