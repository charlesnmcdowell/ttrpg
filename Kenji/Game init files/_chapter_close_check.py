#!/usr/bin/env python3
"""_chapter_close_check.py — Decide whether the in-progress chapter has
enough activity to warrant closing, and close it if so.

Called by the launcher before swapping characters. Threshold: ≥5 "paragraphs
of activity" since the last chapter close. A "paragraph" is counted as:

    - 1 new encounter_log entry after the last _chapter_history entry's day
    - 1 fired event with day >= last-chapter-close day
    - 1 threat_clock that advanced past 0 since last close

If activity ≥ 5, we:
    - Set _chapter_status = "COMPLETE" and bump _chapter to the next number
    - Append a minimal _chapter_history entry with rolling stats
    - Reset _chapter_status of the new (next) chapter to "PENDING"

If activity < 5, we just leave the chapter open and exit silently.

Usage:
    python _chapter_close_check.py <path_to_character_world_state.json>
    python _chapter_close_check.py <path> --force        # close regardless
    python _chapter_close_check.py <path> --threshold 3  # custom threshold
    python _chapter_close_check.py <path> --dry-run      # report, don't write
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _last_close_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return the snapshot recorded at the last chapter close, or a zero-baseline
    if none exists. Schema:
        {
          "encounter_log_count": int,
          "events_fired_names": [str, ...],
          "clock_progress": {clock_name: int, ...},
          "closed_at_day": int,
          "closed_at_hour": int,
        }
    """
    history = state.get("_chapter_history") or []
    if not isinstance(history, list) or not history:
        return {
            "encounter_log_count": 0,
            "events_fired_names": [],
            "clock_progress": {},
            "closed_at_day": 0,
            "closed_at_hour": 0,
        }
    last = history[-1] if isinstance(history[-1], dict) else {}
    snap = last.get("_close_snapshot") or {}
    # Backward-compat fallbacks: parse timing string for the LAST 'Day N' (the
    # close day, not the open day) when no explicit snapshot is present.
    if "closed_at_day" not in snap:
        import re
        timing = str(last.get("timing", ""))
        days = re.findall(r"Day\s+(\d+)", timing)
        snap.setdefault("closed_at_day", int(days[-1]) if days else 0)
        snap.setdefault("closed_at_hour", 23)   # treat the close as end-of-day
    snap.setdefault("encounter_log_count", 0)
    snap.setdefault("events_fired_names", [])
    snap.setdefault("clock_progress", {})
    return snap


def _count_activity(state: Dict[str, Any],
                     baseline: Dict[str, Any]) -> Dict[str, Any]:
    """Count NEW activity since the baseline snapshot. Returns a dict with
    breakdown + total. Counts:
        - encounter_log entries with index >= baseline['encounter_log_count']
          OR (legacy fallback) day-and-hour AFTER baseline's closed_at_*
        - fired events whose name is NOT in baseline['events_fired_names']
        - threat clocks whose progress increased above the baseline value
    """
    ses = state.get("_story_engine_state") or {}
    encounters = 0
    events = 0
    clocks_advanced = 0
    fatalities = 0

    enc_log = ses.get("encounter_log") or []
    base_enc_count = int(baseline.get("encounter_log_count", 0) or 0)
    base_close_day = int(baseline.get("closed_at_day", 0) or 0)
    base_close_hour = int(baseline.get("closed_at_hour", 0) or 0)

    for idx, enc in enumerate(enc_log):
        if not isinstance(enc, dict):
            continue
        # Primary path: index-based count (new entries since the last close
        # are exactly those after the recorded count).
        is_new_by_index = idx >= base_enc_count
        # Fallback path: if no snapshot was recorded (legacy data), use
        # day-and-hour ordering vs the last close moment.
        d = int(enc.get("day", 0) or 0)
        h = int(float(enc.get("hour", 0) or 0))
        is_new_by_time = (d > base_close_day) or (d == base_close_day and h > base_close_hour)
        is_new = is_new_by_index if base_enc_count > 0 else is_new_by_time
        # Also respect explicit chapter tags if present (most authoritative).
        enc_chapter = enc.get("_chapter")
        if isinstance(enc_chapter, int):
            cur_ch = int(state.get("_chapter") or 1)
            is_new = (enc_chapter >= cur_ch)
        if is_new:
            encounters += 1
            fats = enc.get("fatalities") or []
            if isinstance(fats, list):
                fatalities += len(fats)

    base_event_names = set(baseline.get("events_fired_names") or [])
    for ev in (ses.get("events") or []):
        if not isinstance(ev, dict):
            continue
        if (ev.get("status") or "").upper() != "FIRED":
            continue
        name = ev.get("name") or ""
        if name and name not in base_event_names:
            events += 1

    base_clocks = baseline.get("clock_progress") or {}
    for name, clock in (ses.get("threat_clocks") or {}).items():
        if not isinstance(clock, dict):
            continue
        prog = int(clock.get("progress", 0) or 0)
        prev = int(base_clocks.get(name, 0) or 0)
        if prog > prev:
            clocks_advanced += 1

    total = encounters + events + clocks_advanced
    return {
        "encounters": encounters,
        "events_fired": events,
        "clocks_advanced": clocks_advanced,
        "fatalities": fatalities,
        "total_paragraphs": total,
        "_baseline": baseline,
    }


def _close_chapter(state: Dict[str, Any], activity: Dict[str, Any]) -> str:
    """Append a chapter_history entry, mark COMPLETE, bump chapter number.
    Returns a human-readable summary string."""
    cur_chapter = state.get("_chapter") or state.get("_story_engine_state", {}).get("_chapter", 1)
    cur_title = state.get("_chapter_title") or state.get("_story_engine_state", {}).get("_chapter_title", "")
    if not isinstance(cur_chapter, int):
        try:
            cur_chapter = int(cur_chapter)
        except Exception:
            cur_chapter = 1

    ses = state.get("_story_engine_state") or {}
    cur_day = int(ses.get("day", 1) or 1)
    cur_hour = int(float(ses.get("hour", 0) or 0))

    # Build a minimal history entry from observable state.
    fat_names: List[str] = []
    for enc in (ses.get("encounter_log") or []):
        if not isinstance(enc, dict):
            continue
        for fat in (enc.get("fatalities") or []):
            if isinstance(fat, dict) and fat.get("name"):
                fat_names.append(fat["name"])

    fired_events: List[str] = []
    for ev in (ses.get("events") or []):
        if not isinstance(ev, dict):
            continue
        if (ev.get("status") or "").upper() == "FIRED" and ev.get("name"):
            fired_events.append(ev["name"])

    summary_lines = [
        f"Chapter {cur_chapter} closed by launcher chapter-close check on Day {cur_day} hour {cur_hour}.",
        f"Activity since open: {activity['encounters']} combat encounter(s), {activity['events_fired']} event(s) fired, {activity['clocks_advanced']} threat-clock(s) advanced, {activity['fatalities']} fatality/-ies.",
    ]
    if fat_names:
        summary_lines.append("Fatalities: " + "; ".join(fat_names[:6]))
    if fired_events:
        summary_lines.append("Events fired: " + "; ".join(fired_events[:6]))
    summary = " | ".join(summary_lines)

    # Snapshot the state at close time so the next chapter-close check can
    # compute deltas instead of absolutes (this is THE fix for the "all
    # events in memory" bug — the next pass will only count NEW activity).
    close_snapshot = {
        "encounter_log_count": len(ses.get("encounter_log") or []),
        "events_fired_names": [
            ev.get("name") for ev in (ses.get("events") or [])
            if isinstance(ev, dict)
            and (ev.get("status") or "").upper() == "FIRED"
            and ev.get("name")
        ],
        "clock_progress": {
            name: int((c or {}).get("progress", 0) or 0)
            for name, c in (ses.get("threat_clocks") or {}).items()
            if isinstance(c, dict)
        },
        "closed_at_day": cur_day,
        "closed_at_hour": cur_hour,
    }

    # Tag any UN-tagged encounter_log entries with this chapter number, so
    # future filtering by `_chapter` is authoritative.
    for enc in (ses.get("encounter_log") or []):
        if isinstance(enc, dict) and "_chapter" not in enc:
            enc["_chapter"] = cur_chapter

    history = state.get("_chapter_history") or []
    history.append({
        "chapter": cur_chapter,
        "title": cur_title or f"Chapter {cur_chapter}",
        "timing": f"Through Day {cur_day} hour {cur_hour}",
        "summary": summary,
        "auto_closed_by": "_chapter_close_check.py",
        "auto_closed_at": datetime.now().isoformat(timespec="seconds"),
        "activity_metrics": activity,
        "_close_snapshot": close_snapshot,
    })
    state["_chapter_history"] = history

    # Mark complete and bump.
    state["_chapter_status"] = "COMPLETE"
    if "_story_engine_state" in state:
        state["_story_engine_state"]["_chapter_status"] = "COMPLETE"

    # Open the next chapter as PENDING.
    next_chapter = cur_chapter + 1
    state["_chapter"] = next_chapter
    state["_chapter_status"] = "PENDING"
    state["_chapter_title"] = f"[OPEN — Day {cur_day} hour {cur_hour}]"
    if "_story_engine_state" in state:
        ses = state["_story_engine_state"]
        ses["_chapter"] = next_chapter
        ses["_chapter_status"] = "PENDING"
        ses["_chapter_title"] = f"[OPEN — Day {cur_day} hour {cur_hour}]"

    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("state_file", type=Path,
                    help="Path to character_world_state.json")
    p.add_argument("--threshold", type=int, default=5,
                    help="Activity threshold (default: 5 paragraphs)")
    p.add_argument("--force", action="store_true",
                    help="Close chapter regardless of threshold")
    p.add_argument("--dry-run", action="store_true",
                    help="Report decision, don't write")
    args = p.parse_args()

    if not args.state_file.exists():
        print(f"[chapter-close] state file not found: {args.state_file}")
        return 1

    raw = args.state_file.read_text(encoding="utf-8")
    state = json.loads(raw)

    cur_status = (state.get("_chapter_status") or "").upper()
    if cur_status == "COMPLETE":
        print(f"[chapter-close] chapter already COMPLETE — nothing to close.")
        return 0

    baseline = _last_close_snapshot(state)
    activity = _count_activity(state, baseline)

    print(f"[chapter-close] activity since last close "
          f"(Day {baseline.get('closed_at_day')} hour {baseline.get('closed_at_hour')}, "
          f"snapshot enc_count={baseline.get('encounter_log_count')}): "
          f"{activity['encounters']} new encounters, "
          f"{activity['events_fired']} new events fired, "
          f"{activity['clocks_advanced']} clocks advanced, "
          f"{activity['fatalities']} fatalities. "
          f"Total: {activity['total_paragraphs']} paragraphs (threshold: {args.threshold}).")

    should_close = args.force or activity["total_paragraphs"] >= args.threshold

    if not should_close:
        print(f"[chapter-close] below threshold — leaving chapter open.")
        return 0

    summary = _close_chapter(state, activity)
    print(f"[chapter-close] {summary}")

    if args.dry_run:
        print(f"[chapter-close] DRY RUN — not writing.")
        return 0

    args.state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
    print(f"[chapter-close] applied to {args.state_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
