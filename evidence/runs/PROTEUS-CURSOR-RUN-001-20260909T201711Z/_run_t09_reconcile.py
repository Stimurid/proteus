"""One-shot T09 shared-frontier reconciliation episode runner."""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from proteus.frontier_reconcile import (
    list_branches,
    reconcile,
    show_reconciled,
    write_base,
    write_branch,
)

EP = Path(r"C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z")
T09 = EP / "gate1_final3_fixtures" / "T09_SHARED"


def main() -> None:
    if T09.exists():
        shutil.rmtree(T09)
    (T09 / "state").mkdir(parents=True)

    s0 = write_base(
        T09,
        items={
            "mission": "ship inventory helper v0",
            "constraint": "keep tests green",
            "priority_theme": "local-first tooling",
        },
        note="S0",
    )
    (EP / "T09_S0_BASE.json").write_text(json.dumps(s0, indent=2) + "\n", encoding="utf-8")

    time.sleep(1)
    a = write_branch(
        T09,
        branch_id="A",
        actor="session.A.worker",
        items={
            "next_step": "implement login flow first",
            "constraint": "keep tests green",
            "shared_note": "document CLI usage",
            "priority_theme": "local-first tooling",
        },
        base_digest=s0["base_digest"],
        note="A1_login",
    )
    (EP / "T09_BRANCH_A.json").write_text(json.dumps(a, indent=2) + "\n", encoding="utf-8")

    time.sleep(2)
    b = write_branch(
        T09,
        branch_id="B",
        actor="session.B.worker",
        items={
            "next_step": "implement offline cache first",
            "constraint": "keep tests green",
            "risk": "UNKNOWN: auth vendor SLA",
            "priority_theme": "local-first tooling",
        },
        base_digest=s0["base_digest"],
        note="B1_cache",
    )
    (EP / "T09_BRANCH_B.json").write_text(json.dumps(b, indent=2) + "\n", encoding="utf-8")

    branches = list_branches(T09)
    (EP / "T09_BRANCHES_LIST.json").write_text(
        json.dumps(branches, indent=2) + "\n", encoding="utf-8"
    )

    r1 = reconcile(T09, observer="gate1.final3.t09")
    (EP / "T09_RECONCILE_R1.json").write_text(json.dumps(r1, indent=2) + "\n", encoding="utf-8")

    fresh = show_reconciled(T09)
    (EP / "T09_FRESH_READER.json").write_text(
        json.dumps(fresh, indent=2) + "\n", encoding="utf-8"
    )

    shutil.copy(T09 / ".proteus" / "FRONTIER_RECONCILED.json", EP / "T09_FRONTIER_RECONCILED_COPY.json")
    shutil.copy(T09 / "state" / "FRONTIER_RECONCILED.md", EP / "T09_FRONTIER_RECONCILED.md")

    assert a["recorded_utc"] < b["recorded_utc"], "B should be later so LWW temptation exists"
    assert any(c["key"] == "next_step" for c in r1["conflicts"])
    vals = {
        c["value"]
        for c in next(c for c in r1["conflicts"] if c["key"] == "next_step")["candidates"]
    }
    assert vals == {"implement login flow first", "implement offline cache first"}
    assert r1["merged"]["constraint"] == "keep tests green"
    assert r1["merged"]["shared_note"] == "document CLI usage"
    assert fresh is not None and fresh["branch_ids"] == ["A", "B"]
    print("T09_OK")
    print("A_utc", a["recorded_utc"])
    print("B_utc", b["recorded_utc"])
    print("conflicts", [c["key"] for c in r1["conflicts"]])
    print("merged_keys", sorted(r1["merged"]))


if __name__ == "__main__":
    main()
