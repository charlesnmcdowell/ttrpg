#!/usr/bin/env python3
"""_cross_character_sync.py - Build a world snapshot from all character state
files and inject 'what the other PCs are doing' into each character's
_narrative_summary so each character sees the world as it actually stands
when loaded.

Cardinal Rule 14 (Cross-Character Continuity Update): when a chapter closes
in any campaign, this script should run to refresh every other character's
view of that PC. The character_tracker.md is the human-edited source of
truth, but the running state files (per-character JSON) are what the
dashboard actually reads. This sync keeps them in lockstep.

Usage:
    python _cross_character_sync.py          # sync all characters
    python _cross_character_sync.py --dry-run  # report, don't write
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _read_state(p: Path) -> Optional[Dict[str, Any]]:
    """Read a state JSON. Tolerates both modern (mechanical_state +
    _story_engine_state) and legacy (top-level fields) schemas."""
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_pc_summary(name: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a one-line snapshot of a PC's current state. Schema-agnostic.
    Returns: {name, level, location, day, hour, hp, status, last_action}.
    """
    # Modern schema (Cookie, Shen, Holly) keeps the runtime block under
    # _story_engine_state; legacy schema (Amaris, Kenji) keeps it at top level.
    ses = state.get("_story_engine_state") or state
    ms = state.get("mechanical_state") or state

    level = ms.get("level") or ses.get("level") or "?"
    day = ses.get("day", "?")
    hour = ses.get("hour", "?")
    hp = ses.get("hp", "?")
    max_hp = ses.get("max_hp", "?")
    location = (ses.get("location", "") or "").strip()
    canon = (ses.get("canon_pointer", "") or "").strip()
    beat = (ses.get("story_beat", "") or "").strip()
    chapter = state.get("_chapter") or ses.get("_chapter")
    chapter_status = state.get("_chapter_status") or ses.get("_chapter_status") or ""
    chapter_title = state.get("_chapter_title") or ses.get("_chapter_title") or ""

    # Determine status. Defaults to "active" but we mark COMPLETE campaigns
    # as such so other characters see "Amaris (campaign complete) at ..."
    canon_upper = canon.upper()
    if "COMPLETE" in canon_upper or chapter_status == "COMPLETE" and chapter and chapter > 10:
        active_status = "campaign-complete"
    elif chapter_status == "PENDING":
        active_status = "active (mid-chapter)"
    else:
        active_status = "active"

    # One-line summary other characters will see.
    summary = (
        f"{name} (L{level}, {active_status}) - "
        f"Day {day} hour {hour}, "
        f"{location[:80] or '(location unknown)'}"
    )
    if chapter:
        ch = f"Ch{chapter}"
        if chapter_title:
            ch += f" '{chapter_title[:40]}'"
        if chapter_status:
            ch += f" [{chapter_status}]"
        summary += f" - {ch}"
    if canon:
        summary += f" - {canon[:120]}"

    return {
        "name": name,
        "level": level,
        "location": location,
        "day": day,
        "hour": hour,
        "hp": f"{hp}/{max_hp}",
        "status": active_status,
        "chapter": chapter,
        "chapter_status": chapter_status,
        "summary": summary,
    }


def sync_all(ttrpg_root: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Discover all character state files via manifests, build a world
    snapshot, write a `_world_cross_references` block (and append to
    `_narrative_summary` if the schema is legacy-flat) into each state file.

    Returns a report dict.
    """
    manifests_dir = ttrpg_root / "Kenji" / "Game init files" / "manifests"
    manifest_files = list(manifests_dir.glob("*.json"))
    chars: List[Dict[str, Any]] = []   # [{id, name, state_path, state}]

    # Pass 1: load all states.
    for mp in manifest_files:
        try:
            mf = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            continue
        sf_rel = mf.get("state_file") or ""
        state_path = ttrpg_root / sf_rel
        if not state_path.exists():
            continue
        state = _read_state(state_path)
        if state is None:
            continue
        char_id = mp.stem
        # Determine display name from state.
        ses = state.get("_story_engine_state") or state
        display_name = (ses.get("char_name") or
                          state.get("player_input", {}).get("name") or
                          char_id.replace("_", " ").title())
        chars.append({
            "id": char_id,
            "name": display_name,
            "state_path": state_path,
            "state": state,
        })

    # Pass 2: build world snapshot.
    snapshot = {
        c["name"]: _extract_pc_summary(c["name"], c["state"])
        for c in chars
    }

    # Pass 3: write _world_cross_references into each character's state.
    # Bug #8 fix: only write when content actually changed (compare new
    # other_characters block vs existing). Avoids OneDrive sync storms.
    # Bug #9 fix: stopped stitching into _narrative_summary. The dashboard
    # reads _world_cross_references directly now via _refresh_narrative_tab.
    # Bug #14 fix: previous hand-written narrative content is never
    # silently overwritten by sync.
    report: Dict[str, Any] = {"updated": [], "skipped_unchanged": [], "snapshot": snapshot}
    for c in chars:
        state = c["state"]
        my_name = c["name"]
        others = {n: s for n, s in snapshot.items() if n != my_name}

        new_cross_refs = {
            "_rule": (
                "Auto-built by _cross_character_sync.py — this is what's "
                "currently happening with the OTHER PCs in the world. The "
                "loaded character may encounter them as NPCs, hear about "
                "them in tavern gossip, or be affected by their actions. "
                "Synced at the timestamp below; re-run sync after any "
                "chapter close in any campaign to refresh. The dashboard "
                "Narrative tab reads this block directly; sync NEVER "
                "modifies _narrative_summary so hand-written content is "
                "always safe."
            ),
            "synced_at": datetime.now().isoformat(timespec="seconds"),
            "other_characters": others,
        }

        # Bug #8 fix: skip the file write entirely if other_characters is
        # byte-identical to what's already on disk. Prevents OneDrive
        # write-storm when nothing actually changed.
        existing = state.get("_world_cross_references") or {}
        existing_others = existing.get("other_characters") or {}
        if existing_others == others:
            report["skipped_unchanged"].append({
                "character": my_name,
                "other_characters_count": len(others),
            })
            continue

        state["_world_cross_references"] = new_cross_refs

        # Bug #9 fix: previously this stitched a paragraph into
        # _narrative_summary. That risked overwriting hand-written content.
        # Now we ONLY update _world_cross_references. The dashboard renders
        # it via _refresh_narrative_tab as a separate "ELSEWHERE" section.
        # Note: legacy .exe builds (pre-fix) won't see this section; user
        # needs to rebuild for the new Narrative tab layout to surface it.

        if not dry_run:
            c["state_path"].write_text(
                json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8")
        report["updated"].append({
            "character": my_name,
            "state_path": str(c["state_path"]),
            "other_characters_count": len(others),
        })

    return report


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ttrpg-root", type=Path,
                    default=Path(__file__).resolve().parent.parent.parent,
                    help="Root of the TTRPG folder (contains Kenji/, Cookie/, etc.)")
    p.add_argument("--dry-run", action="store_true",
                    help="Print what would be written, don't write.")
    args = p.parse_args()

    print(f"[cross-character-sync] root: {args.ttrpg_root}")
    report = sync_all(args.ttrpg_root, dry_run=args.dry_run)

    print(f"[cross-character-sync] world snapshot:")
    for n, s in report["snapshot"].items():
        print(f"  - {s['summary'][:200]}")
    print()
    print(f"[cross-character-sync] updated {len(report['updated'])} character(s):")
    for u in report["updated"]:
        print(f"  - {u['character']}: +{u['other_characters_count']} cross-refs"
              f"{' (DRY RUN)' if args.dry_run else ''}")
    skipped = report.get("skipped_unchanged", [])
    if skipped:
        print(f"[cross-character-sync] skipped {len(skipped)} unchanged "
              f"(no write — saves OneDrive sync churn):")
        for u in skipped:
            print(f"  - {u['character']}: cross-refs already current")


if __name__ == "__main__":
    main()
