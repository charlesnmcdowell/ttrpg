#!/usr/bin/env python3
"""tts_speaker_parser.py — segment narrator prose into [(speaker, gender_hint, text), ...]
for the multi-voice TTS pipeline.

Design goals:
  - Pure function, no I/O, no side effects — easy to unit-test with `python -m
    pytest -k speaker_parser` (or just run this file: it self-tests at __main__).
  - Heuristic, not perfect. Mis-attributions route to a wrong voice but never
    crash. Fallback to "narrator" (no speaker) is always safe.
  - Knows nothing about voice IDs, the Anthropic API, or ElevenLabs. It only
    answers: "given this prose and this NPC roster, who is speaking what?"

The dashboard wires the output to tts_npc_voice_resolver to pick a voice ID
per segment, then to tts_stitcher to concatenate per-segment audio.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple


# Detect a quoted dialogue segment. Allow either curly or straight quotes
# (Anthropic responses sometimes use ASCII " and sometimes typographic " ").
# DOTALL so dialogue spanning a paragraph break still counts as one segment.
_DIALOGUE_RE = re.compile(
    r'(?P<dlg>[“"][^“”"]+[”"])',
    re.DOTALL,
)

# Attribution patterns that ride next to a dialogue chunk:
#   "line," X said.            → group "name" = X
#   X said, "line"             → group "name" = X (when this regex is run before the dialogue)
#   "line," the taller one snapped.  → no name; descriptor stored as gender_hint source
#
# We capture an attribution that comes IMMEDIATELY after a closing quote,
# allowing a comma + speech verb. Matching on first/last name only — multi-
# word names ("Sera Lightfoot") are still single-token tagged because the
# resolver matches on substring. Order of speech verbs influences gender:
# the gendered-pronoun fallback ("he said" / "she said") is its own pattern.
# Words that look like a name (capitalized at sentence start) but are
# actually pronouns — must be rejected by every name regex via a post-
# match check, NOT carried into the resolver as a literal speaker.
_PRONOUN_BLOCKLIST = {
    "he", "she", "they", "it", "him", "her", "them",
    "his", "hers", "its", "theirs",
}

# Post-attribution name pattern. NOT IGNORECASE — names are properly
# capitalized in narrator prose. The verb half stays case-sensitive too
# (Anthropic emits lowercase speech verbs reliably).
_AFTER_QUOTE_NAME_RE = re.compile(
    r'^[\s,—\-]*(?P<name>[A-Z][a-zA-Z\'\-]+)\s+(?P<verb>'
    r'said|asked|whispered|muttered|growled|snapped|barked|sighed|laughed|'
    r'replied|answered|called|shouted|hissed|murmured|continued|added|'
    r'declared|remarked|countered|insisted|admitted|explained|warned'
    r')\b',
)
# Pronoun attribution: any 'he/she/they' immediately after a closing quote
# is treated as the speaker. Don't require a speech verb — 'He shook his
# head' attributes the prior dialogue just as well as 'He said'.
_AFTER_QUOTE_PRONOUN_RE = re.compile(
    r'^[\s,—\-]*(?P<pronoun>he|she|they)\b',
    re.IGNORECASE,
)
# Descriptor attribution. Matches:
#   'The woman folded her arms.'           → role='woman' (gendered)
#   'The taller one, certain.'             → 'one' fallback (gender unknown)
#   'The older man scoffed.'               → adj='older' role='man'
#   'The shorter snaps back.'              → bare adjective with no role noun
# The role list determines gender hint via _ROLE_GENDER below; 'one' and bare
# adjectives produce no gender hint and the resolver defaults to humanoid.male.
_AFTER_QUOTE_DESCRIPTOR_RE = re.compile(
    r'^[\s,—\-]*[Tt]he\s+(?P<adj>\w+\s+)?(?P<role>'
    r'man|woman|girl|boy|guard|priest|priestess|merchant|farmer|shepherd|'
    r'innkeeper|sergeant|marshal|knight|ranger|wizard|witch|hunter|smith|'
    r'monk|nun|elder|king|queen|prince|princess|lord|lady|barbarian|'
    r'sorcerer|sorceress|stranger|figure|rider|soldier|captain|child|'
    r'one|other|first|second|third|taller|shorter|older|younger|larger|'
    r'smaller|bigger|smallest|tallest|shortest|oldest|youngest'
    r')\b',
    re.IGNORECASE,
)


@dataclass
class Segment:
    """One chunk of audio in the stitched output. `speaker` is the NPC name
    (matched against the campaign roster) OR None for narrator/unattributed.
    `gender_hint` is best-effort from descriptors / pronouns; resolver can use
    it to pick from the male/female bucket when speaker is unmatched."""
    text: str
    speaker: Optional[str] = None
    gender_hint: Optional[str] = None  # "male" | "female" | None
    is_dialogue: bool = False           # True if this came out of a quoted block


# Role → typical gender (used when descriptor is gender-neutral, e.g. "the guard").
# Conservative: only assign gender for unambiguous role nouns. Gender-neutral
# roles return None and the resolver falls back to "humanoid.male" by default.
_ROLE_GENDER = {
    "woman": "female", "girl": "female", "priestess": "female", "witch": "female",
    "queen": "female", "princess": "female", "lady": "female", "nun": "female",
    "sorceress": "female",
    "man": "male", "boy": "male", "priest": "male", "king": "male",
    "prince": "male", "lord": "male", "monk": "male", "sorcerer": "male",
}


def _gender_from_pronoun(pronoun: str) -> Optional[str]:
    p = pronoun.lower().strip()
    if p == "he":
        return "male"
    if p == "she":
        return "female"
    return None


def _match_attribution(post_text: str, roster: Set[str]
                       ) -> Tuple[Optional[str], Optional[str]]:
    """Inspect the prose immediately after a closing quote and return
    (speaker_name_or_None, gender_hint_or_None)."""
    m = _AFTER_QUOTE_NAME_RE.match(post_text)
    if m:
        name_raw = m.group("name").strip()
        # Reject pronouns that happen to start sentences ("She said" → 
        # 'She' is NOT a name). Pronouns flow through _AFTER_QUOTE_PRONOUN_RE
        # below for proper gender-only attribution.
        if name_raw.lower() in _PRONOUN_BLOCKLIST:
            m = None
    if m:
        name_raw = m.group("name").strip()
        # Match against the roster case-insensitively, longest match wins.
        name_lower = name_raw.lower()
        for r in sorted(roster, key=len, reverse=True):
            r_lower = r.lower().strip()
            if r_lower and (r_lower == name_lower
                            or r_lower.split()[0] == name_lower
                            or name_lower in r_lower.split()):
                return r, None
        # Capitalized word but not in roster — return as best-guess speaker
        # so the resolver can decide whether to add to roster on the fly.
        return name_raw, None
    m = _AFTER_QUOTE_DESCRIPTOR_RE.match(post_text)
    if m:
        role = m.group("role").lower()
        # Gendered roles (woman, priestess, queen, etc.) return their
        # explicit gender. Gender-neutral descriptors ("one", "shorter",
        # "taller", "figure") fall back to "male" so the resolver still
        # picks an NPC voice from the humanoid.male pool — far better
        # than routing the line to the narrator voice (which would make
        # every unknown-descriptor character sound like the DM).
        return None, _ROLE_GENDER.get(role, "male")
    m = _AFTER_QUOTE_PRONOUN_RE.match(post_text)
    if m:
        return None, _gender_from_pronoun(m.group("pronoun"))
    return None, None


def _last_roster_mention(window: str, roster: Set[str]) -> Optional[str]:
    """Find the most-recent roster name in the given text window. Used
    for pronoun antecedent resolution: when prose says 'Sera moved...
    "line," she whispered.', we attribute the pronoun-tagged dialogue
    to Sera by looking backward at the preceding narration.

    Returns the matched canonical roster name, or None if no match."""
    if not roster:
        return None
    # Find the LAST occurrence of any roster name in the window.
    last_pos = -1
    last_match = None
    lower_window = window.lower()
    for r in roster:
        # Try the full name and then the first token (so 'Maren Ashby'
        # matches just 'Maren').
        for variant in (r, r.split()[0] if r.split() else r):
            v_lower = variant.lower()
            # Word-boundary check by surrounding the search.
            idx = lower_window.rfind(v_lower)
            if idx > last_pos:
                # Make sure it's a whole word (not 'serape' matching 'sera').
                left_ok = idx == 0 or not lower_window[idx-1].isalnum()
                right_idx = idx + len(v_lower)
                right_ok = right_idx >= len(lower_window) or not lower_window[right_idx].isalnum()
                if left_ok and right_ok:
                    last_pos = idx
                    last_match = r
    return last_match


def parse_prose(prose: str, roster: Optional[Set[str]] = None) -> List[Segment]:
    """Split `prose` into ordered Segments. Connective tissue between dialogue
    chunks is emitted as narrator (speaker=None, is_dialogue=False); each
    quoted dialogue chunk is emitted as a separate segment with speaker /
    gender_hint inferred from the prose immediately following it.

    `roster` is the set of NPC names (case-insensitive) currently tracked in
    the campaign — used to match "Sera said" against the engine's main_cast.
    """
    if roster is None:
        roster = set()
    segments: List[Segment] = []
    cursor = 0
    for m in _DIALOGUE_RE.finditer(prose):
        # Narrator chunk before this dialogue
        pre = prose[cursor:m.start()]
        if pre.strip():
            segments.append(Segment(text=pre, speaker=None, is_dialogue=False))
        # Dialogue chunk itself (strip outer quotes for cleaner TTS, keep punctuation)
        dlg = m.group("dlg")
        # Look at the prose immediately AFTER the dialogue for attribution
        post_window = prose[m.end():m.end() + 80]
        speaker, gender_hint = _match_attribution(post_window, roster)
        # When post-attribution didn't yield a name, look backward for
        # the most-recent roster mention — the dialogue probably belongs
        # to whoever was just mentioned. Fires for both pronoun-attributed
        # ('she whispered' → look back for Sera) AND orphan dialogue
        # ('Garruk grunted. "Smells wrong here."' → attribute to Garruk).
        if speaker is None and roster:
            antecedent_window = prose[max(0, m.start() - 200):m.start()]
            antecedent = _last_roster_mention(antecedent_window, roster)
            if antecedent:
                speaker = antecedent
        # If attribution failed AFTER, look BEFORE for pre-attribution
        # ("Sera said, 'line'") — scan back ~80 chars for a name + verb pattern,
        # OR a pronoun + verb pattern ("She said, 'line'") for gender-only
        # attribution.
        if speaker is None and gender_hint is None:
            pre_window = prose[max(0, m.start() - 80):m.start()]
            tail = pre_window.rstrip()
            # Pre-attribution PRONOUN check first (cheap, no roster lookup):
            #   "...She said," → gender_hint='female'
            pre_pron = re.search(
                r'\b(?P<pronoun>she|he|they)\s+(?:said|asked|whispered|'
                r'muttered|growled|snapped|barked|replied|answered|called|'
                r'hissed|murmured)[\s,]*$',
                tail, re.IGNORECASE,
            )
            if pre_pron:
                gender_hint = _gender_from_pronoun(pre_pron.group("pronoun"))
            # Reverse heuristic: "Sera asked," → name comes before the verb.
            # Case-sensitive on the name (capital first letter) — without
            # this constraint, IGNORECASE would let pronouns 'she/he/they'
            # match as a 'name'. The verb half stays case-insensitive.
            rev = re.search(
                r'(?P<name>[A-Z][a-zA-Z\'\-]+)\s+(?:said|asked|whispered|muttered|'
                r'growled|snapped|barked|replied|answered|called|hissed|murmured)'
                r'[\s,]*$',
                tail,
            )
            if rev:
                name_raw = rev.group("name").strip()
                # Same pronoun guard as post-attribution — "She said,
                # 'line'" must not capture 'She' as a name.
                if name_raw.lower() in _PRONOUN_BLOCKLIST:
                    rev = None
            if rev:
                name_raw = rev.group("name").strip()
                name_lower = name_raw.lower()
                for r in sorted(roster, key=len, reverse=True):
                    r_lower = r.lower().strip()
                    if r_lower and (r_lower == name_lower
                                    or r_lower.split()[0] == name_lower):
                        speaker = r
                        break
                else:
                    speaker = name_raw
        # Orphan-dialogue safety net: if NO attribution was found at all
        # (no name, no descriptor, no pronoun, no antecedent), force a
        # 'male' gender hint so the resolver routes the line to the
        # humanoid.male pool instead of the narrator voice. The DM should
        # NEVER voice a quoted line — bare dialogue is always SOMEONE
        # talking, even if we don't know who. The pool resolver picks a
        # voice deterministically from the text hash so different orphan
        # lines get different voices (giving the scene a sense of multiple
        # speakers even when attribution is absent).
        if speaker is None and gender_hint is None:
            gender_hint = "male"
        segments.append(Segment(text=dlg, speaker=speaker,
                                 gender_hint=gender_hint, is_dialogue=True))
        cursor = m.end()
    # Trailing narrator tail (often the last attribution + scene-set after the
    # final dialogue, or pure prose if no dialogue at all)
    tail = prose[cursor:]
    if tail.strip():
        segments.append(Segment(text=tail, speaker=None, is_dialogue=False))
    return segments


# ---------------------------------------------------------------------------
# Self-tests — run `python tts_speaker_parser.py` to validate.
# ---------------------------------------------------------------------------

def _test_runner():
    cases = []

    # 1. Pure narrator, no dialogue
    cases.append(("Pure narrator",
                  "Wind moved through the pines. Shen kept walking south.",
                  set(),
                  [(None, False, None)]))

    # 2. Single named NPC, post-attribution
    cases.append(("Named NPC — post-attribution",
                  '"Stop right there." Sera said, hand on her sword.',
                  {"Sera"},
                  [("Sera", True, None), (None, False, None)]))

    # 3. Single named NPC, pre-attribution
    cases.append(("Named NPC — pre-attribution",
                  'Sera said, "Stop right there."',
                  {"Sera"},
                  [(None, False, None), ("Sera", True, None)]))

    # 4. Anonymous descriptor with implicit gender
    cases.append(("Anonymous descriptor — woman",
                  '"You\'ll regret that." The woman folded her arms.',
                  set(),
                  [(None, True, "female"), (None, False, None)]))

    # 5. Pronoun fallback
    cases.append(("Pronoun fallback — he",
                  '"That\'s bone-pattern." He shook his head.',
                  set(),
                  [(None, True, "male"), (None, False, None)]))

    # 6. Mixed dialogue: two named speakers + narrator
    cases.append(("Mixed: two named speakers",
                  '"Where to?" Sera asked. The wind shifted. "North." Edwyn replied softly.',
                  {"Sera", "Edwyn"},
                  [("Sera", True, None), (None, False, None),
                   ("Edwyn", True, None), (None, False, None)]))

    # 8. Bug A regression — "she" must NOT be captured as a name when
    #    the pre-attribution regex sees "she said" before the quote.
    cases.append(("Bug A: pronoun NOT mistaken for name (pre-attribution)",
                  'She said, "Stay back."',
                  set(),
                  [(None, False, None), (None, True, "female")]))

    # 9. Bug B regression — descriptor "the taller one" must attribute
    #    even though "one" wasn't in the original role list.
    cases.append(("Bug B: descriptor 'the taller one' → defaults to male",
                  '"Three rings." The taller one, certain.',
                  set(),
                  [(None, True, "male"), (None, False, None)]))

    # 10. Bug B regression — "the shorter" with no role noun.
    cases.append(("Bug B: bare adjective 'the shorter' → defaults to male",
                  '"You are wrong." The shorter snapped back.',
                  set(),
                  [(None, True, "male"), (None, False, None)]))

    # 11. Bug C regression — pronoun antecedent. 'Sera moved... "line"
    #     she whispered.' → dialogue attributed to Sera.
    cases.append(("Bug C: pronoun antecedent finds Sera",
                  'Sera moved beside Shen. "Stay low," she whispered.',
                  {"Sera"},
                  [(None, False, None), ("Sera", True, "female"), (None, False, None)]))

    # 13. Antecedent-pickup for orphan dialogue: 'Garruk grunted from
    #     the rocks. "Smells wrong here."' → dialogue attributed to
    #     Garruk via the antecedent search (no pronoun, no descriptor,
    #     just a recent named mention).
    cases.append(("antecedent finds Garruk for orphan dialogue",
                  'Garruk grunted from the rocks. "Smells wrong here."',
                  {"Garruk"},
                  [(None, False, None), ("Garruk", True, None)]))

    # 12. Bug D regression — orphan dialogue with NO attribution must
    #     route to the pool (gender hint set), NEVER to narrator voice.
    cases.append(("Bug D: orphan dialogue → pool, never narrator",
                  '"Smells wrong here."',
                  set(),
                  [(None, True, "male")]))

    # 7. Roster matching — first-name only
    cases.append(("Roster match — first-name",
                  '"Bring it back," Maren said.',
                  {"Maren Ashby"},
                  [("Maren Ashby", True, None), (None, False, None)]))

    failures = []
    for name, prose, roster, expect in cases:
        got = parse_prose(prose, roster)
        # Compare just (speaker, is_dialogue, gender_hint) for each segment
        got_simple = [(s.speaker, s.is_dialogue, s.gender_hint) for s in got]
        if got_simple != expect:
            failures.append((name, expect, got_simple, got))
    if failures:
        print(f"FAIL: {len(failures)}/{len(cases)} test(s)")
        for name, expect, got, segs in failures:
            print(f"\n  case: {name}")
            print(f"    expected: {expect}")
            print(f"    got:      {got}")
            for s in segs:
                print(f"    seg: speaker={s.speaker!r} gender={s.gender_hint!r} "
                      f"is_dlg={s.is_dialogue} text={s.text[:50]!r}")
        return 1
    print(f"OK: all {len(cases)} test(s) passed")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_test_runner())
