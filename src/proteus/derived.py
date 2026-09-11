"""Optional recorder for durable derived-representation ↔ source relations.

Keeps derived artifacts distinct from richer source material by writing a small
JSON relation receipt beside the derived path. Does not make the derived file
canonical. Not required for trivial copies.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "proteus.derived_relation.v0.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relation_path_for(derived: Path) -> Path:
    derived = derived.resolve()
    return derived.with_name(derived.name + ".derived_relation.json")


def record_relation(
    *,
    derived: Path | str,
    sources: list[Path | str],
    note: str | None = None,
    observer: str | None = None,
    project: Path | str | None = None,
) -> dict[str, Any]:
    derived_p = Path(derived).resolve()
    source_list = [str(Path(s).resolve()) for s in sources]
    if not source_list:
        raise ValueError("at least one --source is required")
    if not derived_p.exists():
        raise FileNotFoundError(f"derived artifact missing: {derived_p}")
    for s in source_list:
        if not Path(s).exists():
            raise FileNotFoundError(f"source missing: {s}")

    receipt = {
        "schema": SCHEMA,
        "derived": str(derived_p),
        "sources": source_list,
        "note": note,
        "observer": observer,
        "project": str(Path(project).resolve()) if project else None,
        "recorded_utc": utc_now(),
        "claims": [
            "derived is not identical to source",
            "omitted or ambiguous source material may require reopening sources",
            "do not treat derived as full object by default",
        ],
    }
    out = relation_path_for(derived_p)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["relation_path"] = str(out)
    return receipt


def read_relation(derived: Path | str) -> dict[str, Any] | None:
    path = relation_path_for(Path(derived))
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
