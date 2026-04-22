#!/usr/bin/env python3
"""
Scene graph prototype runner — mile 15.5 shield wall.

The app owns scene order and fixed narration. AI only fills ai_slots.
This script validates slot output against canon_allowlist + continuity_engine.

Usage:
  python run_scene_graph.py
  python run_scene_graph.py --dry-run          # print fixed text only, no slots
  python run_scene_graph.py --skip-ai          # use [AI SKIPPED] placeholders
  python run_scene_graph.py --no-state-check   # do not warn if kenji_state mismatch

On failure (continuity pre-check or missing scene id), the tool prints KENJI_SCENE_GRAPH_FAILURE_RECEIPT
and writes logs/session_*.txt with the same machine block.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# continuity_engine lives in parent "Game init files" folder
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import continuity_engine as ce  # noqa: E402


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_state(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return load_json(path)
    except json.JSONDecodeError as e:
        print(f"[STATE] Invalid JSON in {path}: {e}")
        return None


def check_state_alignment(
    state: dict | None, hint: dict, state_path: Path | None = None
) -> list[str]:
    """Return warning strings if state file doesn't match prototype expectations."""
    if state is None:
        if state_path and state_path.is_file():
            return ["kenji_state.json exists but is invalid JSON — skipping alignment check."]
        return ["kenji_state.json not found — skipping alignment check."]
    warnings = []
    min_day = hint.get("min_day")
    if min_day is not None and state.get("day", 0) < min_day:
        warnings.append(
            f"State day={state.get('day')} is below prototype min_day={min_day}."
        )
    sub = hint.get("location_substring", "")
    loc = (state.get("location") or "").lower()
    if sub and sub.lower() not in loc:
        warnings.append(
            f"State location may not match prototype (expected '{sub}' in location string)."
        )
    return warnings


def validate_slot_text(text: str, rules: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    text_lower = text.lower()
    for bad in rules.get("forbidden_substrings", []):
        if bad.lower() in text_lower:
            errors.append(f"Forbidden substring: {bad!r}")
    max_chars = rules.get("max_chars")
    if max_chars and len(text) > max_chars:
        errors.append(f"Too long: {len(text)} chars (max {max_chars})")
    # Optional: flag unknown Title-Case tokens (very noisy — off by default)
    return (len(errors) == 0, errors)


def validate_named_npcs_mentioned(text: str) -> list[str]:
    """
    Heuristic: find capitalized words; if they look like names, check continuity_engine.
    Ignores sentence-start words and common geography.
    """
    skip = {
        "The", "A", "An", "I", "We", "You", "He", "She", "They", "It", "And", "But",
        "South", "North", "East", "West", "Lady", "Sir", "Kenji", "Brynn", "Jostin",
        "Pallid", "March", "Thornkeep", "Millhaven", "Coalition",
    }
    warnings: list[str] = []
    for m in re.finditer(r"\b([A-Z][a-z]+)\b", text):
        word = m.group(1)
        if word in skip:
            continue
        r = ce.validate_npc(word)
        if not r["valid"]:
            warnings.append(f"Possible unknown name: {word!r} — {r.get('error', '')}")
    return warnings


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def format_kenji_snapshot(state: dict | None) -> str:
    if not state:
        return "  (kenji_state.json missing or unreadable — snapshot unavailable)\n"
    lines = [
        f"  day / hour: {state.get('day')} / {state.get('hour')}",
        f"  location: {state.get('location', '')[:200]}{'...' if len(str(state.get('location', ''))) > 200 else ''}",
        f"  level: {state.get('level')} | HP: {state.get('hp')}/{state.get('max_hp')} | AC: {state.get('ac')}",
        f"  wealth: {state.get('gold')} GP, {state.get('silver')} SP",
        f"  weather: {state.get('weather', '')[:120]}",
    ]
    st = state.get("statuses")
    if isinstance(st, list) and st:
        lines.append("  statuses (first 2):")
        for s in st[:2]:
            lines.append(f"    - {str(s)[:160]}")
    return "\n".join(lines) + "\n"


def build_run_receipt(
    *,
    run_id: str,
    scenes_path: Path,
    pack: dict,
    state: dict | None,
    visited: list[str],
    end_scene: str | None,
    dry_run: bool,
    skip_ai: bool,
    no_state_check: bool,
    log_file: Path,
) -> str:
    """Machine-generated block — hard for an LLM to fake without copying this output."""
    cid = pack.get("campaign_id", "unknown")
    sha = file_sha256(scenes_path)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path_str = str(scenes_path.resolve())
    chain = " -> ".join(visited) if visited else "(none)"
    choices = pack.get("run_receipt", {}).get("continuation_choices", [])
    choice_lines = []
    for c in choices:
        choice_lines.append(f"  [{c.get('id', '?')}] {c.get('label', '')}")

    lines = [
        "",
        "#" * 78,
        "#  KENJI_SCENE_GRAPH_RUN_RECEIPT  (machine output — not LLM-authored)",
        "#" * 78,
        f"RUN_ID:          {run_id}",
        f"SCENE_GRAPH:     {cid}",
        f"SCENES_FILE_SHA: {sha}  (first 16 hex of SHA-256 of {path_str})",
        f"EXECUTED_AT_UTC: {utc}",
        f"CLI_FLAGS:       dry_run={dry_run}  skip_ai={skip_ai}  no_state_check={no_state_check}",
        "",
        "--- KENJI SNAPSHOT (read from kenji_state.json when available) ---",
        format_kenji_snapshot(state).rstrip(),
        "",
        "--- GRAPH TRAVERSAL ---",
        f"SCENES_VISITED:  {chain}",
        f"END_SCENE:       {end_scene or '(graph incomplete)'}",
        "",
        "--- HOW TO CONTINUE (author picks one) ---",
        *(choice_lines or ["  (no continuation_choices in JSON)"]),
        "",
        f"SESSION_LOG:     {log_file.resolve()}",
        "#" * 78,
        "If your AI session cannot show RUN_ID + SCENES_FILE_SHA above, the tool did not run.",
        "#" * 78,
        "",
    ]
    return "\n".join(lines)


def build_failure_receipt(
    *,
    run_id: str,
    scenes_path: Path,
    pack: dict,
    state: dict | None,
    visited: list[str],
    reason_code: str,
    detail_lines: list[str],
    dry_run: bool,
    skip_ai: bool,
    no_state_check: bool,
    log_file: Path,
) -> str:
    """Emitted when the graph cannot complete — still machine-stamped for session notes."""
    cid = pack.get("campaign_id", "unknown")
    sha = file_sha256(scenes_path)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path_str = str(scenes_path.resolve())
    chain = " -> ".join(visited) if visited else "(none)"
    detail = "\n".join(f"  {line}" for line in detail_lines) if detail_lines else "  (none)"

    lines = [
        "",
        "#" * 78,
        "#  KENJI_SCENE_GRAPH_FAILURE_RECEIPT  (machine output — not LLM-authored)",
        "#" * 78,
        f"RUN_ID:          {run_id}",
        f"RESULT:          FAILED",
        f"FAIL_CODE:       {reason_code}",
        f"SCENE_GRAPH:     {cid}",
        f"SCENES_FILE_SHA: {sha}  (first 16 hex of SHA-256 of {path_str})",
        f"EXECUTED_AT_UTC: {utc}",
        f"CLI_FLAGS:       dry_run={dry_run}  skip_ai={skip_ai}  no_state_check={no_state_check}",
        "",
        "--- FAILURE DETAIL ---",
        detail,
        "",
        "--- KENJI SNAPSHOT (read from kenji_state.json when available) ---",
        format_kenji_snapshot(state).rstrip(),
        "",
        "--- GRAPH TRAVERSAL (partial) ---",
        f"SCENES_VISITED:  {chain}",
        "",
        f"SESSION_LOG:     {log_file.resolve()}",
        "#" * 78,
        "This run did not complete. Fix the issue and re-run.",
        "#" * 78,
        "",
    ]
    return "\n".join(lines)


def print_canon_inject(speaker_key: str, canon: dict) -> None:
    sp = canon.get("speakers", {}).get(speaker_key, {})
    facts = canon.get("facts_from_state_ashmere_28", {})
    print("\n--- CANON INJECT (paste into AI prompt) ---")
    print(f"Speaker: {speaker_key}")
    if sp:
        print(f"Physical: {sp.get('physical_one_liner', '')}")
        print(f"Voice: {sp.get('voice_note', '')}")
    try:
        print(ce.check_npc_function(speaker_key))
    except Exception as e:
        print(f"(registry check failed: {e})")
    print(f"Scene facts: {json.dumps(facts, indent=0)}")
    print("--- END CANON INJECT ---\n")


def run_flow(
    scenes_path: Path,
    canon_path: Path,
    state_path: Path,
    dry_run: bool,
    skip_ai: bool,
    check_state: bool,
) -> int:
    pack = load_json(scenes_path)
    canon = load_json(canon_path)
    state = load_state(state_path)
    if check_state:
        for w in check_state_alignment(state, pack.get("state_hint", {}), state_path):
            print(f"[STATE] {w}")
    else:
        print("[STATE] Alignment warnings skipped (--no-state-check); snapshot still from file if present.")

    log_path = Path(__file__).parent / "logs"
    log_path.mkdir(exist_ok=True)
    run_id = str(uuid.uuid4())
    log_file = log_path / (
        f"session_{run_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
    )

    threat = pack.get("campaign_id", "prototype")
    npcs_arc = pack.get("npcs_in_arc", [])
    scene_result = ce.validate_scene(npcs_arc, "pallid_march")
    print("=== CONTINUITY PRE-CHECK (ascii) ===")
    print(f"Location: South road ~mile 15.5 | Threat: pallid_march")
    for npc in npcs_arc:
        r = ce.validate_npc(npc)
        mark = "OK" if r["valid"] else "FAIL"
        print(f"  [{mark}] {npc}: {r.get('error') or r.get('type', 'ok')}")
    print("=== END ===")
    if not scene_result["valid"]:
        print("CONTINUITY ERRORS:", scene_result["errors"])
        errs = scene_result.get("errors") or []
        detail = [str(e) for e in errs] if isinstance(errs, list) else [str(errs)]
        freceipt = build_failure_receipt(
            run_id=run_id,
            scenes_path=scenes_path,
            pack=pack,
            state=state,
            visited=[],
            reason_code="CONTINUITY_PRECHECK",
            detail_lines=detail,
            dry_run=dry_run,
            skip_ai=skip_ai,
            no_state_check=not check_state,
            log_file=log_file,
        )
        print(freceipt)
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(freceipt)
        print(f"Failure log written: {log_file}")
        return 1
    for warn in scene_result.get("warnings", []):
        print(f"[WARN] {warn}")

    entry = pack["entry_scene"]
    scenes: dict = pack["scenes"]

    lines_out: list[str] = []
    visited: list[str] = []
    end_scene: str | None = None
    sid = entry
    while sid:
        visited.append(sid)
        sc = scenes.get(sid)
        if not sc:
            print(f"Missing scene: {sid}")
            freceipt = build_failure_receipt(
                run_id=run_id,
                scenes_path=scenes_path,
                pack=pack,
                state=state,
                visited=visited,
                reason_code="MISSING_SCENE",
                detail_lines=[
                    f"Scene id {sid!r} is not defined under pack['scenes'].",
                    "Check next pointers and scene keys in the JSON.",
                ],
                dry_run=dry_run,
                skip_ai=skip_ai,
                no_state_check=not check_state,
                log_file=log_file,
            )
            print(freceipt)
            lines_out.append(freceipt)
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("".join(lines_out))
            print(f"Session log written: {log_file}")
            return 1
        header = f"\n{'='*60}\n[{sid}] {sc.get('title', '')}\n{'='*60}\n"
        print(header)
        lines_out.append(header)
        narr = sc.get("narration", "")
        print(narr)
        lines_out.append(narr + "\n")

        for slot in sc.get("ai_slots", []):
            if dry_run:
                print(f"[DRY-RUN] Would request AI slot: {slot['id']}")
                continue
            print_canon_inject(slot["speaker"], canon)
            print("INSTRUCTIONS FOR AI:")
            print(slot.get("prompt", ""))
            print()
            if skip_ai:
                body = "[AI SKIPPED — placeholder]"
                ok, errs = True, []
            else:
                body = ""
                ok, errs = False, []
                while not ok:
                    print("Paste dialogue below. End with a line containing only END")
                    buf: list[str] = []
                    while True:
                        try:
                            line = input()
                        except EOFError:
                            line = "END"
                        if line.strip() == "END":
                            break
                        buf.append(line)
                    body = "\n".join(buf).strip()
                    ok, errs = validate_slot_text(body, slot.get("validation", {}))
                    npc_warns = validate_named_npcs_mentioned(body)
                    for w in npc_warns:
                        print(f"[NAME CHECK] {w}")
                    if not ok:
                        print("VALIDATION FAILED:")
                        for e in errs:
                            print(f"  - {e}")
                        again = input("Fix and retry, or type ABORT to keep text anyway: ").strip()
                        if again.upper() == "ABORT":
                            ok = True
                        else:
                            ok = False

            block = f"\n>>> AI_SLOT [{slot['id']} / {slot['speaker']}]:\n{body}\n"
            print(block)
            lines_out.append(block)

        nxt = sc.get("next")
        if nxt is None:
            print("\n[END OF GRAPH — next=null]")
            end_scene = sid
            break
        sid = nxt

    receipt = build_run_receipt(
        run_id=run_id,
        scenes_path=scenes_path,
        pack=pack,
        state=state,
        visited=visited,
        end_scene=end_scene or (visited[-1] if visited else None),
        dry_run=dry_run,
        skip_ai=skip_ai,
        no_state_check=not check_state,
        log_file=log_file,
    )
    print(receipt)
    lines_out.append(receipt)

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("".join(lines_out))
    print(f"Session log written: {log_file}")
    return 0


def main() -> int:
    # Windows consoles often default to cp1252; UTF-8 avoids mojibake on em dashes / arrows in JSON.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description="Scene graph prototype — mile 15.5")
    ap.add_argument("--dry-run", action="store_true", help="Print narration only")
    ap.add_argument("--skip-ai", action="store_true", help="Skip AI input with placeholders")
    ap.add_argument(
        "--no-state-check",
        action="store_true",
        help="Skip day/location alignment warnings; snapshot still loads from kenji_state.json if present",
    )
    ap.add_argument(
        "--scenes",
        type=Path,
        default=Path(__file__).parent / "scenes_mile155.json",
    )
    ap.add_argument(
        "--canon",
        type=Path,
        default=Path(__file__).parent / "canon_allowlist.json",
    )
    ap.add_argument(
        "--state",
        type=Path,
        default=Path(__file__).parent.parent / "kenji_state.json",
    )
    args = ap.parse_args()
    return run_flow(
        args.scenes,
        args.canon,
        args.state,
        dry_run=args.dry_run,
        skip_ai=args.skip_ai,
        check_state=not args.no_state_check,
    )


if __name__ == "__main__":
    raise SystemExit(main())
