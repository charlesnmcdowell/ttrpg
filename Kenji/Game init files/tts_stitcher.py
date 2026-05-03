#!/usr/bin/env python3
"""tts_stitcher.py — stitch per-segment PCM bytes into a single playable WAV.

ElevenLabs returns raw PCM at 22050 Hz mono 16-bit when you ask for
output_format=pcm_22050. Stitching is just byte concatenation since every
segment has the same sample format. We add a tiny inter-segment gap (~120ms
of silence) to avoid jarring voice transitions.

This module knows nothing about HTTP or Tk — pass it the PCM bytes you
already fetched from ElevenLabs (one bytes object per segment, in order)
and it returns a complete WAV file as bytes, ready to write to disk + play.
"""

from __future__ import annotations
import io
import wave
from typing import List, Optional


# Match the existing dashboard's TTS_PCM_RATE constant. Don't import from
# kenji_gui to keep this module pure — if the dashboard changes the rate it
# also has to update here.
DEFAULT_PCM_RATE = 22050
SAMPLE_WIDTH_BYTES = 2  # 16-bit mono PCM
INTER_SEGMENT_SILENCE_MS = 120  # gap between voice transitions for clarity


def _silence_bytes(ms: int, rate_hz: int = DEFAULT_PCM_RATE) -> bytes:
    """Return raw PCM bytes for `ms` milliseconds of silence at `rate_hz`."""
    n_samples = int(rate_hz * ms / 1000)
    return b"\x00\x00" * n_samples


def stitch_pcm_to_wav(
    pcm_segments: List[bytes],
    *,
    rate_hz: int = DEFAULT_PCM_RATE,
    inter_segment_silence_ms: int = INTER_SEGMENT_SILENCE_MS,
) -> bytes:
    """Concatenate per-segment PCM and wrap in a WAV header.

    Args:
        pcm_segments: list of raw PCM byte blobs (one per Segment), in order.
                      Empty segments are skipped silently. Mismatched sample
                      formats will produce garbage output — caller's job to
                      ensure all segments came from the same TTS output_format.
        rate_hz: PCM sample rate. Must match what was requested from the API.
        inter_segment_silence_ms: silence inserted between segments. Set to 0
                                   to concat with no gap (rougher transitions).

    Returns:
        A complete WAV file as bytes. Caller writes it to disk + plays.
    """
    valid_segments = [s for s in pcm_segments if s]
    if not valid_segments:
        return b""

    silence = _silence_bytes(inter_segment_silence_ms, rate_hz) if inter_segment_silence_ms > 0 else b""
    parts: List[bytes] = []
    for i, seg in enumerate(valid_segments):
        parts.append(seg)
        if i < len(valid_segments) - 1 and silence:
            parts.append(silence)
    full_pcm = b"".join(parts)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(SAMPLE_WIDTH_BYTES)
        wf.setframerate(rate_hz)
        wf.writeframes(full_pcm)
    return buf.getvalue()


def estimate_duration_seconds(
    pcm_segments: List[bytes],
    *,
    rate_hz: int = DEFAULT_PCM_RATE,
    inter_segment_silence_ms: int = INTER_SEGMENT_SILENCE_MS,
) -> float:
    """Compute total play duration in seconds (PCM bytes / sample width / rate
    + silence gaps). Used by the dashboard to set the TTS-playing-until window
    so reactive music doesn't cut off mid-sentence."""
    valid = [s for s in pcm_segments if s]
    if not valid:
        return 0.0
    total_pcm_bytes = sum(len(s) for s in valid)
    pcm_seconds = total_pcm_bytes / (SAMPLE_WIDTH_BYTES * rate_hz)
    silence_seconds = (max(0, len(valid) - 1) * inter_segment_silence_ms) / 1000.0
    return pcm_seconds + silence_seconds


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _test_runner():
    failures = []

    # 1. Empty input → empty output
    if stitch_pcm_to_wav([]) != b"":
        failures.append("empty input should return empty bytes")

    # 2. Single non-empty segment → valid WAV
    one_sec_pcm = b"\x00\x01" * DEFAULT_PCM_RATE  # 1s of low-amplitude tone
    wav = stitch_pcm_to_wav([one_sec_pcm])
    if not (wav.startswith(b"RIFF") and b"WAVEfmt " in wav[:50]):
        failures.append("single-segment WAV header malformed")

    # 3. Multi-segment WAV: roundtrip via wave module to verify framerate + length
    seg = b"\x00\x01" * (DEFAULT_PCM_RATE // 2)  # 0.5 s each
    wav = stitch_pcm_to_wav([seg, seg, seg],
                             inter_segment_silence_ms=120)
    with wave.open(io.BytesIO(wav), "rb") as wf:
        if wf.getframerate() != DEFAULT_PCM_RATE:
            failures.append(f"framerate mismatch: {wf.getframerate()}")
        if wf.getnchannels() != 1:
            failures.append(f"channel count mismatch: {wf.getnchannels()}")
        n_frames = wf.getnframes()
        # Expected: 3 × 0.5s + 2 × 120ms = 1.74s = 1.74 × 22050 = ~38367 frames
        expected = int(3 * 0.5 * DEFAULT_PCM_RATE + 2 * 0.120 * DEFAULT_PCM_RATE)
        if abs(n_frames - expected) > 50:  # allow tiny rounding
            failures.append(f"frame count off: got {n_frames} expected ~{expected}")

    # 4. Empty segments mixed in — should be skipped silently
    wav2 = stitch_pcm_to_wav([b"", seg, b"", seg, b""],
                              inter_segment_silence_ms=0)
    with wave.open(io.BytesIO(wav2), "rb") as wf:
        n = wf.getnframes()
        # 2 segments × 0.5s, no silence
        expected = int(2 * 0.5 * DEFAULT_PCM_RATE)
        if abs(n - expected) > 50:
            failures.append(f"empty-skip: got {n} expected ~{expected}")

    # 5. Duration estimator matches actual WAV length
    dur = estimate_duration_seconds([seg, seg, seg], inter_segment_silence_ms=120)
    actual = n_frames / DEFAULT_PCM_RATE if 'n_frames' in dir() else 0
    if abs(dur - 1.74) > 0.05:
        failures.append(f"duration estimate off: {dur}s vs ~1.74s")

    if failures:
        print(f"FAIL: {len(failures)} test(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"OK: all stitcher tests passed (5 cases)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_test_runner())
