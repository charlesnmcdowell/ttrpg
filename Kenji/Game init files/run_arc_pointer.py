#!/usr/bin/env python3
"""
Resolve kenji_state.json -> active_arc.relative_path (markdown under this folder).
Prints KENJI_ARC_POINTER_RUN_RECEIPT so you can prove the tool ran (paste into AI session).

Usage (from this directory):
  python run_arc_pointer.py
  python run_arc_pointer.py --peek 40
  python run_arc_pointer.py --state "C:/path/to/kenji_state.json"
  python run_arc_pointer.py --stamp --no-log   # one proof line, no logs/ file (fast paste for AI)
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


def _utf8_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def file_sha256_16(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_state(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_arc_path(state: dict) -> tuple[Path | None, dict | None, list[str]]:
    """Return (absolute arc path, active_arc dict from state, error strings)."""
    aa = state.get("active_arc")
    errs: list[str] = []
    if aa is None:
        return None, None, ["Missing top-level key active_arc in kenji_state.json."]
    if isinstance(aa, str):
        meta: dict = {"relative_path": aa, "slug": "", "title": ""}
        rel = aa.strip()
    elif isinstance(aa, dict):
        meta = aa
        rel = (aa.get("relative_path") or aa.get("path") or "").strip()
    else:
        return None, None, ["active_arc must be an object {relative_path, ...} or a string path."]

    if not rel:
        return None, meta, ["active_arc.relative_path (or .path) is empty."]

    arc = (_ROOT / rel).resolve()
    try:
        arc.relative_to(_ROOT)
    except ValueError:
        return None, meta, [f"Arc path must stay under Game init files: {arc}"]

    if not arc.is_file():
        return None, meta, [f"Arc file not found: {arc}"]

    return arc, meta, errs


def first_markdown_title(text: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("#").strip() or "(empty heading)"
    return "(no heading in arc file)"


def build_success_receipt(
    *,
    run_id: str,
    state_path: Path,
    state_sha: str,
    arc_path: Path,
    arc_sha: str,
    meta: dict,
    arc_title_line: str,
    arc_bytes: int,
    log_file: Path,
) -> str:
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    slug = meta.get("slug", "") or "(none)"
    title = meta.get("title", "") or "(none)"
    rel = meta.get("relative_path") or meta.get("path") or ""

    lines = [
        "",
        "#" * 78,
        "#  KENJI_ARC_POINTER_RUN_RECEIPT  (machine output — not LLM-authored)",
        "#" * 78,
        f"RUN_ID:           {run_id}",
        f"TOOL:             run_arc_pointer.py",
        f"EXECUTED_AT_UTC:  {utc}",
        f"STATE_FILE:       {state_path.resolve()}",
        f"STATE_FILE_SHA:   {state_sha}  (first 16 hex of SHA-256)",
        f"ACTIVE_ARC_REL:   {rel}",
        f"ACTIVE_ARC_SLUG:  {slug}",
        f"ACTIVE_ARC_TITLE: {title}",
        f"RESOLVED_PATH:    {arc_path.resolve()}",
        f"ARC_FILE_SHA:     {arc_sha}  (first 16 hex of SHA-256)",
        f"ARC_BYTES:        {arc_bytes}",
        f"ARC_FIRST_TITLE:  {arc_title_line}",
        "",
        f"SESSION_LOG:      {log_file.resolve()}",
        "#" * 78,
        "Paste RUN_ID + ARC_FILE_SHA + STATE_FILE_SHA into your AI session to prove this resolver ran.",
        "The AI did not run this script unless this block appears in tool/log output.",
        "#" * 78,
        "",
    ]
    return "\n".join(lines)


def build_stamp_line_success(
    *,
    run_id: str,
    utc: str,
    state_sha: str,
    arc_sha: str,
    meta: dict,
) -> str:
    """Single-line machine stamp (ASCII). Proof fields match the full receipt."""
    slug = meta.get("slug", "") or "(none)"
    rel = (meta.get("relative_path") or meta.get("path") or "").strip() or "(none)"
    return (
        "KENJI_ARC_POINTER_STAMP "
        f"RUN_ID={run_id} "
        f"EXECUTED_AT_UTC={utc} "
        f"STATE_FILE_SHA={state_sha} "
        f"ARC_FILE_SHA={arc_sha} "
        f"ACTIVE_ARC_SLUG={slug} "
        f"ACTIVE_ARC_REL={rel}"
    )


def build_stamp_line_failure(*, run_id: str, utc: str, state_sha: str | None, err: str) -> str:
    sha = state_sha or "NONE"
    err_one = err.replace("\n", " ").strip()[:200]
    return (
        "KENJI_ARC_POINTER_STAMP_FAIL "
        f"RUN_ID={run_id} EXECUTED_AT_UTC={utc} STATE_FILE_SHA={sha} ERR={err_one}"
    )


def build_failure_receipt(
    *,
    run_id: str,
    state_path: Path,
    state_sha: str | None,
    fail_lines: list[str],
    log_file: Path,
) -> str:
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    detail = "\n".join(f"  {x}" for x in fail_lines) if fail_lines else "  (none)"
    sha_line = (
        f"STATE_FILE_SHA:   {state_sha}  (first 16 hex of SHA-256)"
        if state_sha
        else "STATE_FILE_SHA:   (state file missing or unreadable)"
    )
    lines = [
        "",
        "#" * 78,
        "#  KENJI_ARC_POINTER_FAILURE_RECEIPT  (machine output — not LLM-authored)",
        "#" * 78,
        f"RUN_ID:           {run_id}",
        f"TOOL:             run_arc_pointer.py",
        f"EXECUTED_AT_UTC:  {utc}",
        f"STATE_FILE:       {state_path.resolve()}",
        sha_line,
        "",
        "--- FAILURE ---",
        detail,
        "",
        f"SESSION_LOG:      {log_file.resolve()}",
        "#" * 78,
        "Fix kenji_state.active_arc or the arc path, then re-run.",
        "#" * 78,
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    _utf8_stdio()
    ap = argparse.ArgumentParser(description="Resolve active_arc from kenji_state.json")
    ap.add_argument(
        "--state",
        type=Path,
        default=_ROOT / "kenji_state.json",
        help="Path to kenji_state.json",
    )
    ap.add_argument(
        "--peek",
        type=int,
        default=0,
        metavar="N",
        help="After receipt, print first N lines of the arc file (default 0)",
    )
    ap.add_argument("--no-log", action="store_true", help="Do not write logs/arc_session_*.txt")
    ap.add_argument(
        "--stamp",
        action="store_true",
        help="Print one ASCII proof line (RUN_ID + SHAs + slug) instead of the full receipt banner",
    )
    args = ap.parse_args()

    log_dir = _ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    run_id = str(uuid.uuid4())
    log_file = log_dir / (
        f"arc_session_{run_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
    )

    state_path = args.state
    out_parts: list[str] = []

    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not state_path.is_file():
        fail_lines = [f"State file not found: {state_path}"]
        r = build_failure_receipt(
            run_id=run_id,
            state_path=state_path,
            state_sha=None,
            fail_lines=fail_lines,
            log_file=log_file,
        )
        if args.stamp:
            print(build_stamp_line_failure(run_id=run_id, utc=utc, state_sha=None, err=fail_lines[0]))
        else:
            print(r)
        if not args.no_log:
            log_file.write_text(r, encoding="utf-8")
            if not args.stamp:
                print(f"Wrote: {log_file}")
        return 1

    try:
        state = load_state(state_path)
    except json.JSONDecodeError as e:
        fail_lines = [f"Invalid JSON in state file: {e}"]
        r = build_failure_receipt(
            run_id=run_id,
            state_path=state_path,
            state_sha=None,
            fail_lines=fail_lines,
            log_file=log_file,
        )
        if args.stamp:
            print(build_stamp_line_failure(run_id=run_id, utc=utc, state_sha=None, err=fail_lines[0]))
        else:
            print(r)
        if not args.no_log:
            log_file.write_text(r, encoding="utf-8")
            if not args.stamp:
                print(f"Wrote: {log_file}")
        return 1

    state_sha = file_sha256_16(state_path)
    arc_resolved, meta, errs = resolve_arc_path(state)
    if errs or arc_resolved is None:
        r = build_failure_receipt(
            run_id=run_id,
            state_path=state_path,
            state_sha=state_sha,
            fail_lines=errs,
            log_file=log_file,
        )
        if args.stamp:
            print(
                build_stamp_line_failure(
                    run_id=run_id, utc=utc, state_sha=state_sha, err=errs[0] if errs else "resolve failed"
                )
            )
        else:
            print(r)
        out_parts.append(r)
        if not args.no_log:
            log_file.write_text("".join(out_parts), encoding="utf-8")
            if not args.stamp:
                print(f"Wrote: {log_file}")
        return 1

    arc_text = arc_resolved.read_text(encoding="utf-8", errors="replace")
    arc_sha = file_sha256_16(arc_resolved)
    title_line = first_markdown_title(arc_text)
    receipt = build_success_receipt(
        run_id=run_id,
        state_path=state_path,
        state_sha=state_sha,
        arc_path=arc_resolved,
        arc_sha=arc_sha,
        meta=meta or {},
        arc_title_line=title_line,
        arc_bytes=len(arc_text.encode("utf-8")),
        log_file=log_file,
    )
    if args.stamp:
        print(
            build_stamp_line_success(
                run_id=run_id,
                utc=utc,
                state_sha=state_sha,
                arc_sha=arc_sha,
                meta=meta or {},
            )
        )
    else:
        print(receipt)
    out_parts.append(receipt)

    if args.peek > 0 and not args.stamp:
        peek_lines = arc_text.splitlines()[: args.peek]
        peek_block = "\n".join(peek_lines) + ("\n" if peek_lines else "")
        hdr = f"\n--- ARC PEEK (first {args.peek} lines) ---\n"
        print(hdr + peek_block)
        out_parts.append(hdr + peek_block)
    elif args.peek > 0 and args.stamp:
        print("run_arc_pointer.py: --peek ignored when using --stamp", file=sys.stderr)

    if not args.no_log:
        log_file.write_text("".join(out_parts), encoding="utf-8")
        if not args.stamp:
            print(f"Wrote: {log_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
