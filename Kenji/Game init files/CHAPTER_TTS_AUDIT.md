# Chapter TTS — Production Run Audit (money / audio loss vectors)

Read-only review of `chapter_tts.py` (800 lines) and `chapter_tts_interactive.py`. Looking specifically for paths where you could spend money and not get the audio, or have already-paid audio get discarded.

Ranked by cost impact and likelihood.

---

## CRITICAL — could silently lose paid audio

### CRIT-1. Non-deterministic Claude parse defeats the cache on re-run

`_claude_call` at line 266 does not pass `temperature=0`. Anthropic's default temperature is 1.0, which is non-deterministic.

The cache key is `sha1(voice_id + "\n" + text)`. If Claude parses the same chapter twice and produces even slightly different segmentation — different whitespace stripping, different splits at em-dashes, different attribution decisions — every changed segment misses the cache and re-fires ElevenLabs.

**Failure scenario:**
1. Run 1 succeeds. 206 segments synthesized. All cached. Total cost: ~$10.
2. Run 2 (same chapter, e.g. you want to verify a voice change) — Claude re-parses non-deterministically. ~30% of segments are subtly different. Cache miss on ~60 segments. **You pay an extra $3-4 for what you already bought.**

**Fix:** add `temperature=0` to the `client.messages.create()` call. One-line change.

### CRIT-2. Silent cache write failure loses everything on a later crash

`_save_pcm_cache` (line ~614) wraps the entire write in `try: except Exception: pass`. So if the cache dir can't be created (permission denied, disk full, OneDrive lock), every PCM write fails silently. The PCMs are in memory only — exactly the same failure mode that cost you the $1.25-$2.50 the first time.

The user sees the normal "synthesizing..." output, has no idea the cache is broken, and only finds out when a mid-run failure proves there's nothing on disk.

**Fix:** verify the cache dir is writable at the start of `synth_segments` by writing a test file. If it fails, print a loud warning and ask the user whether to abort or continue without cache.

---

## HIGH — significant cost waste in edge cases

### HIGH-1. Cache lives inside OneDrive, subject to sync conflicts

Cache path: `voice_audio/_cache/<chapter_stem>/`. OneDrive syncs everything inside `OneDrive\Documents\`. We've already seen OneDrive truncate Python files mid-write — it could equally well lock or rename a .pcm cache file during sync.

Each `.pcm` file is ~80 KB; a 206-segment chapter is ~16 MB; full Book 1+2+3+4 (~80 chapters) could be 1+ GB. That's a lot to push through OneDrive.

**Concrete risks:**
- OneDrive sync conflict renames a cache file from `abc123.pcm` to `abc123 (conflict 2026-05-11).pcm` — cache hit fails, segment re-synthed, you pay again.
- OneDrive throttles or locks files during heavy sync — `os.replace` in `_save_pcm_cache` fails silently (see CRIT-2).
- The cache competes with Office docs and other work for OneDrive bandwidth.

**Fix options:**
1. Move cache to local `%TEMP%` or `%LOCALAPPDATA%` (not synced, fast, no conflicts) — downside: cache lost on reinstall.
2. Move cache to a local-only folder you create yourself (e.g., `C:\TTRPG_cache\`).
3. Keep in OneDrive but add `.cloudignore` / exclude rules — fiddly.

### HIGH-2. Stitch/save failure leaves all PCMs on disk but no final WAV

Pipeline order: synthesize ALL segments → stitch → write final WAV. If the stitch or write step fails (disk full, OneDrive lock on the output `.wav`, etc.), you've paid for the full chapter and have no file to show for it.

**Mitigation that already exists:** re-running gets 100% cache hits and re-stitches for free. So this isn't a money loss, just a "did the stitch run?" inconvenience.

**Hard cost loss only if** the cache also silently failed (CRIT-2) — then you have neither the WAV nor the cache.

### HIGH-3. Pre-flight Claude parse is lost if the user aborts voice resolution

In `chapter_tts_interactive.py`, the flow is:

1. Parse chapter via Claude → segments in memory
2. Validate voice coverage
3. If missing voices → interactive resolver
4. If user types `q` or `s` → exit with code 5, segments discarded

Cost lost per abort: ~$0.05 (one Haiku parse of the chapter). Small, but if you abort 3 times while sourcing voice IDs from ElevenLabs, that's $0.15 spent on Claude with nothing to show.

**Fix:** persist parsed segments to disk (e.g., `_cache/<chapter_stem>/segments.json`) BEFORE prompting for missing voices. Re-launching loads the cached segments and skips Claude. Tiny code change.

### HIGH-4. Cache is chapter-scoped — repeated text across chapters pays twice

The cache dir is `voice_audio/_cache/<chapter_stem>/`. If "He nodded." appears in both Ch 5 and Ch 6 with the same Narrator voice, those produce identical hashes — but the lookup happens in the per-chapter folder, so Ch 6 misses Ch 5's cache and re-synthesizes the same line.

**Cost impact:** depends on how repetitive your prose is. Probably 5-15% wasted on common short narrator lines across a book.

**Fix:** flatten cache to a single global folder `voice_audio/_cache/_global/<hash>.pcm`. Trade-off: harder to know which files belong to which chapter (no clean per-chapter cleanup). Worth considering once you're past one-off chapter runs.

---

## MEDIUM — minor leaks

### MED-1. Cache holds onto corrupted PCM if it passes the size check

`_load_pcm_cache` rejects files smaller than `ELEVENLABS_MIN_PCM_BYTES = 2048`. But if ElevenLabs returns a 5 KB PCM that happens to be garbled audio (right size, wrong content), we save it to cache and reuse it forever.

**Likelihood:** very low — ElevenLabs either succeeds with valid audio or fails with an HTTP error. Garbled-but-valid-size responses are rare. But if it happens once, every subsequent stitch silently produces a broken segment.

**Detection:** no automated way short of playing back the audio. Manual: spot-check the final WAV.

### MED-2. Claude refusal retry doubles the Haiku spend on that chunk

`_parse_one_chunk` retries once if the first response isn't valid JSON. Cost: ~$0.02 per refused chunk instead of $0.01. Tiny.

### MED-3. Both dry-run and real-run go through the same `main()`

Both call `synth_segments` → `stitch_and_save`. The dry-run exits at step 4 BEFORE step 5 (synth), so no ElevenLabs spend. Verified: the dry-run is genuinely free of ElevenLabs charges. Just Claude parsing once (already paid in pre-flight). ✓

No money risk here, just noting it because the audit name said "production run" and this was worth double-checking.

### MED-4. `confirm_with_user()` prompt is easy to skip with `--yes` flag

If you run from the launcher (`Run_Chapter_TTS.bat`), you always get the y/n prompt. But the underlying CLI accepts `--yes` to skip. If you accidentally run with `--yes` from a terminal, no cost preview ever appears. Probably not a realistic failure mode but worth knowing.

### MED-5. No early-warning for big chapters

The cost preview shows $5-$10 for Book 1 Ch 5 (36k chars). A whole Book 2 single chapter could be 30-50k chars too. No additional gating for "this chapter is unusually expensive" — the y/n is your only gate.

**Minor improvement:** flag chapters above some threshold (~$15) with an extra warning.

---

## LOW / informational

### LOW-1. Backoff timing can total 30 seconds for a single segment

`fetch_pcm` retries with exponential backoff: 2s, 4s, 8s, 16s. A single chronically-failing segment burns 30s of wall-clock time. Not a money issue, but a 206-segment chapter where every segment needs one retry takes ~7 extra minutes. Manageable.

### LOW-2. No automatic cache eviction

The cache grows unbounded. Each chapter is 16-30 MB. 50 chapters = ~1 GB. No auto-cleanup. The README says "delete to force re-synth" but doesn't help with disk pressure.

**Fix:** could add an `--clear-cache` flag, or a max-age policy (delete chapter caches older than 30 days). Not needed yet.

### LOW-3. Per-segment `synth_segments` print uses `\n.replace` on text

Line ~711: `preview = text[:60].replace("\n", " ")`. Cosmetic only — display rendering. Doesn't affect cost or audio.

### LOW-4. Cache filenames use 16-char SHA1 prefix

Collision space: 2^64. For 1 million cached segments, collision probability ~ 10^-8. Effectively zero. ✓

### LOW-5. Pre-flight Claude key check happens but ElevenLabs check happens later

If your ElevenLabs key is missing or invalid, you find out AFTER paying for Claude parsing. ~$0.05 lost per chapter where the key is broken.

**Fix:** call `load_elevenlabs_key(config)` at the start of `main()`, fail fast before Claude is called. Tiny code change.

---

## Summary table — what could go wrong, ranked by money lost

| ID     | Issue                                                                  | Max waste     | Status   |
|--------|------------------------------------------------------------------------|---------------|----------|
| CRIT-1 | Non-deterministic Claude → cache miss on re-run                        | 20-40% of chapter | open    |
| CRIT-2 | Cache write failing silently → repeat of original $1.25-$2.50 loss     | up to full chapter | open    |
| HIGH-1 | Cache in OneDrive → sync conflicts could invalidate cached PCMs        | up to full chapter | open    |
| HIGH-2 | Stitch/save failure → re-stitch is free, so just inconvenient          | $0 (free re-run)   | open    |
| HIGH-3 | Pre-flight Claude lost on user-abort at voice resolution               | $0.05 per abort    | open    |
| HIGH-4 | Cache scoped per-chapter → duplicated lines across chapters re-synth   | 5-15% of book      | open    |
| MED-1  | Corrupted PCM stays cached forever                                     | 1 segment per occurrence | open |
| MED-2  | Claude retry doubles Haiku on refused chunks                           | ~$0.01/chunk       | accepted |
| MED-5  | No extra warning for expensive chapters                                | none direct        | open    |
| LOW-5  | ElevenLabs key check happens after Claude parse                        | $0.05 per launch with bad key | open |

---

## Recommended fix order if you want to harden further

1. **CRIT-1** — add `temperature=0` to the Claude parser. One-line fix. Eliminates the biggest "I paid for this twice" hazard.
2. **CRIT-2** — verify cache writability at the start of `synth_segments`. Warn or abort if it fails. Closes the silent-failure loophole.
3. **HIGH-3** — cache parsed segments to disk before prompting for voices. ~10 lines. Prevents tiny but real waste.
4. **LOW-5** — move the ElevenLabs key check before the Claude parse. Trivial reordering.
5. **HIGH-1** — move cache out of OneDrive. Discussion needed (you may want the backup).
6. **HIGH-4** — global cache instead of per-chapter. Nontrivial, deferred until you've run more chapters.

The rest can wait or stay as known limitations.

---

**The two biggest "you'd lose money" hazards** are CRIT-1 (cache-miss on re-run) and CRIT-2 (silent cache failure). Both are one-screen fixes. Want me to apply them?
