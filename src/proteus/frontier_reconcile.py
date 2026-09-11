"""Shared project-frontier branch write + reconcile (no last-write-wins).

Host-neutral substrate for Gate T09: concurrent actors write branch frontiers
against a shared project base; a distinct reconcile step emits R1 with merged
compatible fields and explicit CONFLICT/UNKNOWN for incompatible ones.

Branch files are provenance carriers. The reconciled receipt is a VIEW, not a
silent overwrite of either branch. Timestamp order is never used as semantic
resolution.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "proteus.frontier_reconcile.v0.1"
BRANCH_DIR = ".proteus/frontier_branches"
RECONCILED_JSON = ".proteus/FRONTIER_RECONCILED.json"
RECONCILED_MD = "state/FRONTIER_RECONCILED.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _branches_dir(project: Path) -> Path:
    return project / BRANCH_DIR


def _digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_base(
    project: Path,
    *,
    items: dict[str, str],
    note: str | None = None,
) -> dict[str, Any]:
    """Record shared base frontier S0 under .proteus/frontier_base.json."""
    project = project.resolve()
    proteus = project / ".proteus"
    proteus.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": SCHEMA,
        "kind": "base",
        "recorded_utc": utc_now(),
        "items": dict(items),
        "note": note,
    }
    payload["base_digest"] = _digest_text(json.dumps(payload["items"], sort_keys=True))
    path = proteus / "frontier_base.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**payload, "path": str(path)}


def read_base(project: Path) -> dict[str, Any] | None:
    path = project.resolve() / ".proteus" / "frontier_base.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_branch(
    project: Path,
    *,
    branch_id: str,
    actor: str,
    items: dict[str, str],
    base_digest: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Write one concurrent frontier branch. Does not overwrite other branches."""
    project = project.resolve()
    if not branch_id or "/" in branch_id or "\\" in branch_id:
        raise ValueError(f"invalid branch_id: {branch_id!r}")
    base = read_base(project)
    if base_digest is None:
        base_digest = (base or {}).get("base_digest")
    bdir = _branches_dir(project)
    bdir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": SCHEMA,
        "kind": "branch",
        "branch_id": branch_id,
        "actor": actor,
        "recorded_utc": utc_now(),
        "base_digest": base_digest,
        "items": dict(items),
        "note": note,
        "invariants": {
            "NO_LAST_WRITE_WINS": True,
            "BRANCH_DOES_NOT_MUTATE_SIBLINGS": True,
        },
    }
    path = bdir / f"{branch_id}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**payload, "path": str(path)}


def list_branches(project: Path) -> list[dict[str, Any]]:
    bdir = _branches_dir(project.resolve())
    if not bdir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(bdir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["path"] = str(path)
        out.append(data)
    return out


def reconcile(project: Path, *, observer: str = "proteus.frontier_reconcile") -> dict[str, Any]:
    """Produce reconciled shared frontier R1 from all branches + base.

    Compatible identical values merge. Differing values become CONFLICT with
    full branch provenance. Missing-but-present-elsewhere values merge as
    contributed. Never selects a winner by recorded_utc.
    """
    project = project.resolve()
    base = read_base(project)
    branches = list_branches(project)
    if len(branches) < 2:
        raise ValueError(
            "reconcile requires at least two frontier branches; "
            f"found {len(branches)}"
        )

    # Collect all keys
    keys: set[str] = set()
    if base:
        keys.update(base.get("items", {}).keys())
    for b in branches:
        keys.update(b.get("items", {}).keys())

    merged: dict[str, str] = {}
    conflicts: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    contributions: dict[str, list[dict[str, str]]] = {}

    for key in sorted(keys):
        values: dict[str, list[dict[str, str]]] = {}
        for b in branches:
            if key not in b.get("items", {}):
                continue
            val = b["items"][key]
            values.setdefault(val, []).append(
                {
                    "branch_id": b["branch_id"],
                    "actor": b.get("actor", ""),
                    "recorded_utc": b.get("recorded_utc", ""),
                }
            )
        contributions[key] = [
            {"value": v, **prov}
            for v, provs in values.items()
            for prov in provs
        ]
        if len(values) == 0:
            # Present only on base — inherit into merged VIEW
            if base and key in base.get("items", {}):
                merged[key] = base["items"][key]
            continue
        if len(values) == 1:
            only = next(iter(values))
            if only.startswith("UNKNOWN:") or only == "UNKNOWN":
                unknowns.append(
                    {
                        "key": key,
                        "text": only,
                        "provenance": values[only],
                    }
                )
            else:
                merged[key] = only
            continue
        # Semantic conflict — do NOT pick by timestamp
        conflicts.append(
            {
                "key": key,
                "status": "CONFLICT",
                "candidates": [
                    {"value": v, "provenance": provs} for v, provs in values.items()
                ],
                "resolution": "UNRESOLVED",
                "rejected_methods": ["last_write_wins", "recorded_utc_order"],
            }
        )

    receipt = {
        "schema": SCHEMA,
        "kind": "reconciled",
        "reconciled_utc": utc_now(),
        "observer": observer,
        "project": str(project),
        "base_digest": (base or {}).get("base_digest"),
        "branch_ids": [b["branch_id"] for b in branches],
        "branch_provenance": [
            {
                "branch_id": b["branch_id"],
                "actor": b.get("actor"),
                "recorded_utc": b.get("recorded_utc"),
                "path": b.get("path"),
                "items": b.get("items"),
            }
            for b in branches
        ],
        "merged": merged,
        "conflicts": conflicts,
        "unknowns": unknowns,
        "contributions_by_key": contributions,
        "invariants": {
            "NO_LAST_WRITE_WINS": True,
            "BRANCH_PROVENANCE_SURVIVES": True,
            "CONFLICT_AND_UNKNOWN_EXPLICIT": True,
            "VIEW_NE_SILENT_OVERWRITE": True,
        },
    }

    out_json = project / RECONCILED_JSON
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md_lines = [
        "# FRONTIER_RECONCILED (VIEW)",
        "",
        f"schema: `{SCHEMA}`",
        f"reconciled_utc: `{receipt['reconciled_utc']}`",
        f"branches: {', '.join(receipt['branch_ids'])}",
        "",
        "## Merged (compatible)",
        "",
    ]
    if merged:
        for k, v in merged.items():
            md_lines.append(f"- `{k}`: {v}")
    else:
        md_lines.append("- (none)")
    md_lines.extend(["", "## CONFLICT (unresolved — not last-write-wins)", ""])
    if conflicts:
        for c in conflicts:
            md_lines.append(f"### `{c['key']}`")
            for cand in c["candidates"]:
                actors = ", ".join(
                    f"{p['branch_id']}@{p['actor']}" for p in cand["provenance"]
                )
                md_lines.append(f"- candidate: {cand['value']} (from {actors})")
            md_lines.append(f"- resolution: `{c['resolution']}`")
            md_lines.append("")
    else:
        md_lines.append("- (none)")
    md_lines.extend(["", "## UNKNOWN", ""])
    if unknowns:
        for u in unknowns:
            md_lines.append(f"- `{u['key']}`: {u['text']}")
    else:
        md_lines.append("- (none)")
    md_lines.extend(
        [
            "",
            "## Branch provenance preserved",
            "",
        ]
    )
    for b in receipt["branch_provenance"]:
        md_lines.append(
            f"- `{b['branch_id']}` actor=`{b['actor']}` recorded_utc=`{b['recorded_utc']}`"
        )
    md_lines.append("")
    md_path = project / RECONCILED_MD
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    receipt["receipt_path"] = str(out_json)
    receipt["markdown_path"] = str(md_path)
    return receipt


def show_reconciled(project: Path) -> dict[str, Any] | None:
    path = project.resolve() / RECONCILED_JSON
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    data["receipt_path"] = str(path)
    return data
