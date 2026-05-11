# chapter_tts.py — Chapter-to-Audiobook Generator

Converts a single chapter markdown file into one stitched WAV audiobook by parsing speakers with Claude and synthesizing each segment via ElevenLabs.

## Quick start (recommended)

Double-click **`Run_Chapter_TTS.bat`** in this folder. A console window opens and asks for the chapter path.

In Windows Explorer, hold **Shift + right-click** the chapter `.md` file and choose **"Copy as path"**. Right-click into the launcher window to paste. Press Enter.

The launcher will:
1. Offer to do a free dry-run first (recommended — parses + validates voice IDs without firing ElevenLabs).
2. If the dry-run succeeds, ask if you want to run for real (this is when you'd burn ElevenLabs credits).
3. Pause at the end so you can read the result before the window closes.

If Python isn't installed, the launcher tells you where to get it. If the `anthropic` package is missing, it offers to `pip install` it for you.

## Manual / scripted usage

```
cd "C:\Users\charl\OneDrive\Documents\TTRPG\Kenji\Game init files"

# Dry-run first to verify all speakers have voice IDs (free, no API credits)
python chapter_tts.py "..\Book 4\Chapters\fraying_empire_chapter_04.md" --dry-run

# Real run (will prompt y/n before burning credits)
python chapter_tts.py "..\Book 4\Chapters\fraying_empire_chapter_04.md"

# Skip the y/n prompt
python chapter_tts.py "..\Book 4\Chapters\fraying_empire_chapter_04.md" --yes

# Save the parser output for inspection
python chapter_tts.py "...chapter.md" --dry-run --save-segments segs.json

# Custom output filename
python chapter_tts.py "...chapter.md" --out millhaven.wav
```

Output lands in `C:\Users\charl\OneDrive\Documents\TTRPG\Kenji\voice_audio\<chapter_stem>.wav`.

## Pipeline (6 stages, with strict cost gating)

1. **Load chapter** — read the .md file. Reports source character count.
2. **Parse via Claude Haiku** — send the chapter to `claude-haiku-4-5-20251001` with a strict JSON-output system prompt. Returns a list of `{speaker, text}` segments. Unattributed prose goes to `"Narrator"`. Attribution beats ("she said") become Narrator segments between dialogue segments.
3. **Validate voice coverage** — for every unique speaker, look up their slot in `tts_config.json → character_voices` (case-insensitive). If any speaker has no slot or has an empty string slot, print the full list of missing names and **abort before any ElevenLabs call**. No credits spent.
4. **Cost preview** — print segment count, total character count, and an ElevenLabs cost range (Scale tier ~$0.15/1k chars to Starter tier ~$0.30/1k chars). Prompt `y/n` unless `--yes` was passed.
5. **Synthesize** — for each segment, POST to `https://api.elevenlabs.io/v1/text-to-speech/<voice_id>/stream?output_format=pcm_22050`. Retries on 429/500/502/503/504 with backoff. PCM bytes collected in order.
6. **Stitch + save** — call the existing `tts_stitcher.stitch_pcm_to_wav()` with 120ms inter-segment silence and write to `voice_audio/<chapter_stem>.wav`.

## Voice ID registry

Lives in `tts_config.json` (the same file the dashboard already uses). Add a speaker by editing the `character_voices` block:

```json
"character_voices": {
  "Narrator": "SBeVjlAyPCwBVd6RVxhx",
  "Kenji":    "SBeVjlAyPCwBVd6RVxhx",
  "Sera":     "w6TF991FL9W1ZVbaJZfK",
  "Ryn":      "V8MrPOnARtlsjrlxEsE7",
  "Edwyn":    "qRlggZwkZ89qLUe4wsqh",
  "YourNewNPC": "<voice_id_from_elevenlabs_library>"
}
```

Keys starting with `_` are documentation and ignored by the lookup. Empty string values count as "no voice ID" and trigger the missing-speaker abort.

## What the abort looks like

If you run a chapter with NPCs that don't have voice IDs yet:

```
[3/6] Validating voice ID coverage...
      2 speakers mapped

=== MISSING VOICE IDs ===
  The following speakers are not mapped in tts_config.json:
    - Vorathiel
    - Hadley
    - Otten

  Edit:  C:\...\Kenji\Game init files\tts_config.json
  Add each speaker to the 'character_voices' block with their
  ElevenLabs voice ID (find IDs at https://elevenlabs.io/app/voice-library).

Aborting before any ElevenLabs credits are spent.
```

Exit code `5`. The Anthropic call for parsing still happened (~$0.01 cost), but no ElevenLabs credits.

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Success (or dry-run / user declined) |
| 2    | Bad input — file missing, no Anthropic key |
| 3    | Claude parse failed (network, invalid JSON) |
| 4    | tts_config.json missing or malformed |
| 5    | Missing voice IDs — see the printed list |
| 6    | No ElevenLabs API key |
| 7    | ElevenLabs synth failed mid-run |
| 8    | Stitch / write failed |

## Cost reference

ElevenLabs character pricing (verify at elevenlabs.io/pricing):
- Scale tier: ~$0.15 per 1k chars
- Pro tier:   ~$0.18 per 1k chars
- Starter:    ~$0.30 per 1k chars

A typical Book 4 chapter (15-30k chars) runs ~$2.25-$9.00 depending on tier. Worth gating with the y/n prompt.

The Claude parsing step costs ~$0.001-$0.01 per chapter (Haiku is cheap). Runs even on `--dry-run`.

## Dependencies

- `anthropic` (Python SDK): `pip install anthropic`
- `tts_stitcher.py` (already in this folder — no install needed)
- Internet access to `api.anthropic.com` and `api.elevenlabs.io`

## Limitations

- Single chapter at a time (by design — predictable cost gating).
- No MP3 output (WAV only; you can convert with ffmpeg afterward).
- Parser may mis-attribute very ambiguous dialogue. Use `--dry-run --save-segments segs.json` to inspect before firing.
- No voice ID overrides per chapter — the dashboard's tts_config is the single source of truth.

## Files touched

- `tts_config.json` — voice ID registry (extended with Narrator/Sera/Ryn/Edwyn, Kenji slot populated)
- `chapter_tts.py` — the tool itself
- `tts_stitcher.py` — reused as-is for PCM-to-WAV stitching
- `voice_audio/` — output directory (auto-created if missing)
