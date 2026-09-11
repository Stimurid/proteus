"""Tests for shared frontier reconcile (T09 substrate)."""

from __future__ import annotations

import json
from pathlib import Path

from proteus.frontier_reconcile import (
    list_branches,
    reconcile,
    show_reconciled,
    write_base,
    write_branch,
)


def test_reconcile_merges_compatible_and_keeps_conflict(tmp_path: Path) -> None:
    project = tmp_path / "body"
    project.mkdir()
    (project / "state").mkdir()

    base = write_base(
        project,
        items={
            "mission": "ship inventory helper",
            "constraint": "keep tests green",
        },
        note="S0",
    )
    assert base["base_digest"]

    # A writes later timestamp intentionally — must NOT win conflicts by time
    a = write_branch(
        project,
        branch_id="A",
        actor="session.A",
        items={
            "next_step": "implement login flow",
            "constraint": "keep tests green",
            "shared_note": "document CLI usage",
        },
        base_digest=base["base_digest"],
    )
    b = write_branch(
        project,
        branch_id="B",
        actor="session.B",
        items={
            "next_step": "implement offline cache",
            "constraint": "keep tests green",
            "risk": "UNKNOWN: auth vendor SLA",
        },
        base_digest=base["base_digest"],
    )
    assert a["recorded_utc"] != "" and b["recorded_utc"] != ""
    assert len(list_branches(project)) == 2

    r1 = reconcile(project, observer="test")
    assert set(r1["branch_ids"]) == {"A", "B"}
    assert r1["merged"]["constraint"] == "keep tests green"
    assert r1["merged"]["shared_note"] == "document CLI usage"
    assert any(c["key"] == "next_step" for c in r1["conflicts"])
    conflict = next(c for c in r1["conflicts"] if c["key"] == "next_step")
    values = {c["value"] for c in conflict["candidates"]}
    assert values == {"implement login flow", "implement offline cache"}
    assert conflict["resolution"] == "UNRESOLVED"
    assert "last_write_wins" in conflict["rejected_methods"]
    assert any(u["key"] == "risk" for u in r1["unknowns"])

    # Fresh independent reader
    shown = show_reconciled(project)
    assert shown is not None
    assert shown["merged"] == r1["merged"]
    assert len(shown["branch_provenance"]) == 2
    md = (project / "state" / "FRONTIER_RECONCILED.md").read_text(encoding="utf-8")
    assert "implement login flow" in md
    assert "implement offline cache" in md
    assert "CONFLICT" in md
    assert "last-write-wins" in md.lower() or "NO_LAST_WRITE_WINS" in json.dumps(shown)


def test_reconcile_requires_two_branches(tmp_path: Path) -> None:
    project = tmp_path / "solo"
    project.mkdir()
    write_base(project, items={"next_step": "alone"})
    write_branch(project, branch_id="A", actor="a", items={"next_step": "alone"})
    try:
        reconcile(project)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "two frontier branches" in str(e)
