#!/usr/bin/env python
"""claims_jsonl.py — append-only merge + integrity validation for claims.jsonl.

Issue #1 round 3. Two distinct false-SUCCESS paths existed before this tool:

  1. CONFLICT PATH. aiye-world-sync.ps1 resolved a conflicted claims.jsonl with a
     bare `git add -- <f>`, which marks the file resolved using the worktree copy
     *including* `<<<<<<<` / `=======` / `>>>>>>>` markers. The merge commit then
     succeeded (exit 0) and published syntactically invalid JSONL.

  2. UNION PATH (worse, because nothing flags it). `.gitattributes` sets
     `entities/**/claims.jsonl merge=union`. If either side's file lacks a
     trailing newline, the union driver concatenates the last line of one side
     with the first line of the other, producing corrupt lines and duplicating
     claims — with NO conflict raised at all.

Both are resolved here by parsing claims as records, never as text hunks.

NO_LAST_WRITE_WINS: a claim_id present on both sides with differing bodies keeps
BOTH records. Divergence is surfaced for `proteus world reconcile` to convert
into a `conflicts_with` chain; it is never silently collapsed.

Commands:
  validate [--strict] <file>...      -> 0 clean, 3 corrupt (or 3 on warnings
                                        when --strict); warnings alone are
                                        reported but do not fail by default
  resolve --base B --ours O --theirs T --out F
                                     -> 0 merged, 3 unparseable input
Exit codes are distinct from 0/1 so a PowerShell caller can route them.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARKERS = ("<<<<<<<", "=======", ">>>>>>>")
EXIT_OK = 0
EXIT_INVALID = 3


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    # newline="" would preserve CRLF; we normalise to logical lines here.
    text = path.read_text(encoding="utf-8")
    return [ln for ln in text.replace("\r\n", "\n").split("\n")]


def validate_file(path: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings).

    errors   = corruption that must block publication (markers, bad JSON,
               missing trailing newline, missing claim_id).
    warnings = legal append-only states that still need operator/reconcile
               attention (same claim_id recorded twice with different bodies,
               e.g. an append-only supersede marker). These must NOT fail the
               sync: the live world legitimately contains them.
    """
    problems: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return [f"{path}: missing"], []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        # This is the precondition that makes merge=union corrupt the file.
        problems.append(
            f"{path}: missing trailing newline "
            "(merge=union would concatenate this file's last claim with the other side's first)"
        )
    seen: dict[str, str] = {}
    for i, line in enumerate(_read_lines(path), 1):
        s = line.strip()
        if not s:
            continue
        if any(s.startswith(m) for m in MARKERS):
            problems.append(f"{path}:{i}: unresolved git conflict marker: {s[:40]}")
            continue
        try:
            obj = json.loads(s)
        except Exception as exc:
            problems.append(f"{path}:{i}: invalid JSON ({exc.__class__.__name__}): {s[:80]}")
            continue
        if not isinstance(obj, dict):
            problems.append(f"{path}:{i}: claim is not a JSON object")
            continue
        cid = obj.get("claim_id")
        if not cid:
            problems.append(f"{path}:{i}: claim missing required 'claim_id'")
            continue
        if cid in seen and seen[cid] != s:
            # Divergent duplicate: legal on disk (append-only keeps both) but the
            # operator must see it, because reconcile is what resolves it. A
            # same-claim_id pair whose `status` disagrees is the concrete hazard:
            # any reader that takes the first match gets the stale verdict.
            warnings.append(
                f"{path}:{i}: claim_id {cid} appears again with a DIFFERENT body "
                "(append-only supersede or unreconciled divergence; reconcile owns this)"
            )
        seen.setdefault(cid, s)
    return problems, warnings


def _records(path: Path) -> tuple[list[str], list[str]]:
    """Return (ordered unique claim lines, problems)."""
    out: list[str] = []
    problems: list[str] = []
    for i, line in enumerate(_read_lines(path), 1):
        s = line.strip()
        if not s:
            continue
        if any(s.startswith(m) for m in MARKERS):
            problems.append(f"{path}:{i}: conflict marker in merge input")
            continue
        try:
            json.loads(s)
        except Exception as exc:
            problems.append(f"{path}:{i}: invalid JSON in merge input ({exc.__class__.__name__})")
            continue
        out.append(s)
    return out, problems


def resolve(base: Path, ours: Path, theirs: Path, out: Path) -> int:
    b, pb = _records(base)
    o, po = _records(ours)
    t, pt = _records(theirs)
    problems = pb + po + pt
    if problems:
        for p in problems:
            print(f"RESOLVE_INPUT_INVALID {p}", file=sys.stderr)
        return EXIT_INVALID

    bset = set(b)
    merged: list[str] = []
    seen: set[str] = set()

    def add(line: str) -> None:
        if line not in seen:
            seen.add(line)
            merged.append(line)

    # Common ancestor first (stable prefix), then each side's additions in order.
    for line in b:
        add(line)
    for line in o:
        if line not in bset:
            add(line)
    for line in t:
        if line not in bset:
            add(line)

    out.write_text("\n".join(merged) + "\n", encoding="utf-8", newline="\n")

    ids: dict[str, list[str]] = {}
    for line in merged:
        cid = json.loads(line).get("claim_id")
        ids.setdefault(str(cid), []).append(line)
    divergent = sorted(c for c, v in ids.items() if len(v) > 1)
    print(
        f"RESOLVE_OK base={len(b)} ours={len(o)} theirs={len(t)} merged={len(merged)} "
        f"ours_added={len([x for x in o if x not in bset])} "
        f"theirs_added={len([x for x in t if x not in bset])}"
    )
    for cid in divergent:
        print(f"RESOLVE_DIVERGENT claim_id={cid} kept={len(ids[cid])} (NO_LAST_WRITE_WINS)")
    return EXIT_OK


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="claims_jsonl.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("files", nargs="+")
    v.add_argument(
        "--strict",
        action="store_true",
        help="treat divergent-claim_id warnings as failures too",
    )
    r = sub.add_parser("resolve")
    r.add_argument("--base", required=True)
    r.add_argument("--ours", required=True)
    r.add_argument("--theirs", required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "validate":
        bad = warn = 0
        for f in a.files:
            errs, warns = validate_file(Path(f))
            for p in errs:
                print(f"CLAIMS_INVALID {p}", file=sys.stderr)
                bad += 1
            for p in warns:
                print(f"CLAIMS_WARN {p}", file=sys.stderr)
                warn += 1
        if bad or (warn and a.strict):
            print(
                f"CLAIMS_VALIDATE_FAIL errors={bad} warnings={warn} strict={bool(a.strict)}",
                file=sys.stderr,
            )
            return EXIT_INVALID
        print(f"CLAIMS_VALIDATE_OK files={len(a.files)} warnings={warn}")
        return EXIT_OK

    return resolve(Path(a.base), Path(a.ours), Path(a.theirs), Path(a.out))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
