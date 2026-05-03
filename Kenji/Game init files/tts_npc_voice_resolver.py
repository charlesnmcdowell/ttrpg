#!/usr/bin/env python3
"""tts_npc_voice_resolver.py — given a parsed Segment + campaign metadata,
return the ElevenLabs voice ID for that segment.

Resolution priority (first hit wins):
  1. Narrator (no speaker)              → narrator_voice_id
  2. Player character (PC name match)   → tts_config.character_voices[pc_name]
  3. Tracked NPC with sticky assignment → npc_voices.json[npc_name]
  4. Tracked NPC, fresh assignment      → pick from pool[(race, gender)],
                                          save to npc_voices.json so future
                                          appearances are sticky
  5. Anonymous descriptor / fallback    → pool[("humanoid", gender_or_male)],
                                          NOT saved (no name to pin to)
  6. Total miss                         → narrator_voice_id (safe fallback)

Pool buckets are pre-populated 0–3 voice IDs each (see tts_voice_pool.json).
Empty buckets fall through to narrator silently — system works the moment
even one bucket has voices in it.

This module is pure logic + tiny file I/O. No HTTP, no Tk, no anthropic.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class VoiceAssignment:
    """Result of resolving one Segment to a voice."""
    voice_id: str
    source: str              # "narrator" | "pc" | "npc-sticky" | "npc-fresh" | "anon-pool" | "fallback"
    bucket: Optional[str] = None  # e.g. "humanoid.male" if pool was used


def _race_to_bucket(race: Optional[str]) -> str:
    """Map an NPC race string to one of the three pool buckets. Anything not
    recognized → humanoid (the catch-all bucket)."""
    if not race:
        return "humanoid"
    r = race.lower()
    if any(t in r for t in ("orc", "ankuspawn", "goblin", "hobgoblin",
                            "ogre", "troll", "half-orc")):
        return "orcish"
    if any(t in r for t in ("elf", "fey", "fae", "sylvan", "drow",
                            "half-elf", "halfelf")):
        return "elfish"
    return "humanoid"


def _stable_pick(name: str, choices: List[str]) -> str:
    """Deterministic pick from a non-empty list, keyed by the NPC name. Same
    name always picks the same voice from the same pool — important so the
    sticky behavior is consistent even if the persistence file is wiped."""
    if not choices:
        return ""
    h = int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:8], 16)
    return choices[h % len(choices)]


def _load_npc_voices(path: Path) -> Dict[str, str]:
    """Load the per-character npc_voices.json sticky map. Returns {} on any
    failure (missing file, unreadable, empty)."""
    try:
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {k: v for k, v in data.items()
                if isinstance(k, str) and isinstance(v, str)
                and not k.startswith("_") and v}
    except Exception:
        return {}


def _save_npc_voices(path: Path, mapping: Dict[str, str]) -> None:
    """Write the sticky map. Best-effort — silently swallows errors so a
    write fail (e.g. read-only mount) never blocks playback."""
    try:
        out = {
            "_doc": ("Per-character sticky NPC → ElevenLabs voice ID map. "
                     "Auto-populated by tts_npc_voice_resolver. Edit by hand "
                     "to override an auto-pick. Delete a key to force re-"
                     "assignment on next encounter."),
        }
        out.update({k: v for k, v in sorted(mapping.items()) if v})
        path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    except Exception:
        pass


def resolve_voice(
    speaker: Optional[str],
    gender_hint: Optional[str],
    *,
    narrator_voice_id: str,
    pc_name: Optional[str],
    pc_voice_id: Optional[str],
    pool: Dict,
    npc_voices_path: Optional[Path] = None,
    npc_metadata: Optional[Dict[str, Dict]] = None,
) -> VoiceAssignment:
    """Resolve one Segment to a voice. See module docstring for priority rules.

    Args:
        speaker:         Segment.speaker (NPC name or None for narrator)
        gender_hint:     Segment.gender_hint ("male"/"female"/None)
        narrator_voice_id: top-level voice from tts_config.json
        pc_name, pc_voice_id: active PC name + their assigned voice (may be None)
        pool:            parsed tts_voice_pool.json (with humanoid/orcish/elfish keys)
        npc_voices_path: per-character sticky map; reads + writes here
        npc_metadata:    {"npc name": {"race": "...", "gender": "..."}, ...}
                         from the engine's main_cast / extra_npcs roster.
                         Used to pick the right pool bucket for tracked NPCs.
    """
    # 1. Narrator — ONLY when there is NO speaker AND NO gender hint.
    #    A None speaker with a gender hint set means the parser found an
    #    anonymous descriptor or pronoun (e.g. 'the woman', 'she') — that
    #    must route to the NPC pool, never to the narrator voice.
    if speaker is None and gender_hint is None:
        return VoiceAssignment(voice_id=narrator_voice_id, source="narrator")

    # 2. Player character — exact name match (case-insensitive)
    if (speaker is not None and pc_name and pc_voice_id
            and speaker.lower().strip() == pc_name.lower().strip()):
        return VoiceAssignment(voice_id=pc_voice_id, source="pc")

    # speaker_key is the canonical name we'll use for sticky lookup,
    # roster matching, and stable-pick hashing. None speaker (anon
    # dialogue with gender hint) gets a synthetic key so the hash is
    # stable across appearances of the same descriptor.
    speaker_key = speaker.strip() if speaker else f"anon-{gender_hint or 'unknown'}"

    # 3. Sticky NPC assignment from npc_voices.json (only for named speakers)
    sticky = _load_npc_voices(npc_voices_path) if (npc_voices_path and speaker) else {}
    for key, vid in sticky.items():
        if key.lower() == speaker_key.lower():
            return VoiceAssignment(voice_id=vid, source="npc-sticky")

    # 4. Look up race + gender from tracked metadata
    meta = (npc_metadata or {}).get(speaker_key)
    if meta is None:
        # Try case-insensitive match on roster
        for k in (npc_metadata or {}).keys():
            if k.lower() == speaker_key.lower():
                meta = npc_metadata[k]
                break
    race = (meta or {}).get("race", "") if meta else ""
    gender = (meta or {}).get("gender", "") if meta else ""
    bucket_race = _race_to_bucket(race)
    bucket_gender = (gender or gender_hint or "male").lower()
    if bucket_gender not in ("male", "female"):
        bucket_gender = "male"
    bucket_key = f"{bucket_race}.{bucket_gender}"
    bucket = pool.get(bucket_race, {}).get(bucket_gender, [])
    bucket_voices = [v for v in bucket if v]

    # Tracked NPC with usable bucket → pin and persist
    if meta and bucket_voices:
        chosen = _stable_pick(speaker_key, bucket_voices)
        if chosen and npc_voices_path is not None:
            sticky[speaker_key] = chosen
            _save_npc_voices(npc_voices_path, sticky)
        return VoiceAssignment(voice_id=chosen, source="npc-fresh", bucket=bucket_key)

    # 5. Anonymous descriptor → pool pick, NOT persisted
    if bucket_voices:
        chosen = _stable_pick(speaker_key or f"anon-{bucket_key}", bucket_voices)
        return VoiceAssignment(voice_id=chosen, source="anon-pool", bucket=bucket_key)

    # 6. Pool empty for this bucket → fall back to narrator
    return VoiceAssignment(voice_id=narrator_voice_id, source="fallback",
                            bucket=bucket_key)


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _test_runner():
    pool_filled = {
        "humanoid": {"male": ["VH_M_1", "VH_M_2", "VH_M_3"],
                     "female": ["VH_F_1", "VH_F_2", "VH_F_3"]},
        "orcish":   {"male": ["VO_M_1", "VO_M_2", "VO_M_3"],
                     "female": ["VO_F_1", "VO_F_2", "VO_F_3"]},
        "elfish":   {"male": ["VE_M_1"], "female": []},
    }
    pool_empty = {"humanoid": {"male": [], "female": []},
                  "orcish":   {"male": [], "female": []},
                  "elfish":   {"male": [], "female": []}}

    NARR = "NARRATOR_ID"
    PC = "PC_VOICE_ID"

    cases = []

    # 1. None speaker → narrator
    cases.append(("narrator",
        resolve_voice(None, None, narrator_voice_id=NARR,
                      pc_name="Shen Sama", pc_voice_id=PC,
                      pool=pool_filled),
        ("narrator", NARR)))

    # 2. PC name match → PC voice
    cases.append(("pc",
        resolve_voice("Shen Sama", None, narrator_voice_id=NARR,
                      pc_name="Shen Sama", pc_voice_id=PC,
                      pool=pool_filled),
        ("pc", PC)))

    # 3. Tracked NPC with race + gender → npc-fresh from correct bucket
    npc_meta = {"Sera": {"race": "Human", "gender": "female"}}
    a = resolve_voice("Sera", None, narrator_voice_id=NARR,
                      pc_name="Shen Sama", pc_voice_id=PC,
                      pool=pool_filled, npc_metadata=npc_meta,
                      npc_voices_path=None)
    cases.append(("npc-fresh humanoid.female",
        a,
        ("npc-fresh", a.voice_id)))  # voice_id is deterministic — content-test it
    assert a.voice_id in pool_filled["humanoid"]["female"], f"wrong bucket: {a}"
    assert a.bucket == "humanoid.female", f"wrong bucket label: {a}"

    # 4. Tracked orc NPC → orcish bucket
    npc_meta2 = {"Garruk": {"race": "Half-Orc", "gender": "male"}}
    a2 = resolve_voice("Garruk", None, narrator_voice_id=NARR,
                       pc_name=None, pc_voice_id=None,
                       pool=pool_filled, npc_metadata=npc_meta2)
    assert a2.voice_id in pool_filled["orcish"]["male"], f"wrong bucket: {a2}"
    cases.append(("npc-fresh orcish.male", a2, ("npc-fresh", a2.voice_id)))

    # 5. Anonymous descriptor → anon-pool, not saved
    a3 = resolve_voice("the woman", "female", narrator_voice_id=NARR,
                       pc_name=None, pc_voice_id=None, pool=pool_filled)
    assert a3.source == "anon-pool" and a3.voice_id in pool_filled["humanoid"]["female"]
    cases.append(("anon-pool female", a3, ("anon-pool", a3.voice_id)))

    # 6. Pool empty → fallback narrator
    a4 = resolve_voice("Sera", None, narrator_voice_id=NARR,
                       pc_name=None, pc_voice_id=None,
                       pool=pool_empty, npc_metadata=npc_meta)
    cases.append(("fallback empty pool", a4, ("fallback", NARR)))

    # 7. Sticky map honored
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"Sera": "STICKY_VOICE_FOR_SERA"}, f)
        sticky_path = Path(f.name)
    try:
        a5 = resolve_voice("Sera", None, narrator_voice_id=NARR,
                           pc_name=None, pc_voice_id=None,
                           pool=pool_filled, npc_metadata=npc_meta,
                           npc_voices_path=sticky_path)
        cases.append(("npc-sticky", a5, ("npc-sticky", "STICKY_VOICE_FOR_SERA")))
    finally:
        sticky_path.unlink(missing_ok=True)

    # 9. Bug E regression — orphan dialogue (speaker=None, gender=male)
    #    must route to humanoid.male pool, NEVER to narrator.
    a_orphan = resolve_voice(None, "male", narrator_voice_id=NARR,
                              pc_name=None, pc_voice_id=None,
                              pool=pool_filled)
    assert a_orphan.source == "anon-pool", f"orphan went to {a_orphan.source}"
    assert a_orphan.voice_id in pool_filled["humanoid"]["male"], a_orphan
    cases.append(("orphan dialogue → pool", a_orphan,
                  ("anon-pool", a_orphan.voice_id)))

    # 10. Bug E regression — None speaker AND None gender → narrator
    a_narr = resolve_voice(None, None, narrator_voice_id=NARR,
                            pc_name=None, pc_voice_id=None,
                            pool=pool_filled)
    cases.append(("true narrator", a_narr, ("narrator", NARR)))

    # 8. Determinism — same name always picks same voice from same pool
    a6a = resolve_voice("Garruk", None, narrator_voice_id=NARR,
                        pc_name=None, pc_voice_id=None,
                        pool=pool_filled, npc_metadata=npc_meta2)
    a6b = resolve_voice("Garruk", None, narrator_voice_id=NARR,
                        pc_name=None, pc_voice_id=None,
                        pool=pool_filled, npc_metadata=npc_meta2)
    assert a6a.voice_id == a6b.voice_id, "non-deterministic pick"
    cases.append(("deterministic", a6a, ("npc-fresh", a6a.voice_id)))

    failures = []
    for name, got, expect in cases:
        if (got.source, got.voice_id) != expect:
            failures.append((name, expect, got))
    if failures:
        print(f"FAIL: {len(failures)}/{len(cases)} test(s)")
        for name, expect, got in failures:
            print(f"  {name}: expected={expect} got=({got.source!r}, {got.voice_id!r})")
        return 1
    print(f"OK: all {len(cases)} resolver test(s) passed")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_test_runner())
