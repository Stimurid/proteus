"""Archivarius-compatible bridge (adapter, not a clone of Archivarius).

Preserves: ENTITY≠CARRIER, VIEW≠SOURCE TRUTH, rebuildable index, CONFLICT/UNKNOWN.
Live Archivarius process invocation is not claimed when unavailable.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .store import WorldStore

BRIDGE_SCHEMA = "proteus.archivarius_bridge.v0.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def reconcile_entity(entity_id: str, *, world: WorldStore | None = None) -> dict[str, Any]:
    """Produce reconciliation evidence for one entity + rebuild generated VIEW."""
    store = world or WorldStore()
    mounted = store.mount(entity_id)
    index = store.rebuild_index()
    receipt = {
        "schema": BRIDGE_SCHEMA,
        "reconciled_utc": utc_now(),
        "entity_id": entity_id,
        "identity": mounted["identity"],
        "carriers": mounted["carriers"]["carriers"],
        "current_claim_count": len(mounted["current_claims"]),
        "conflict_count": len(mounted["conflicts"]),
        "unknown_count": len(mounted["unknowns"]),
        "project_links": mounted["projects"].get("projects", []),
        "index_digest16": (
            json.loads((store.index_dir / "INDEX_RECEIPT.json").read_text(encoding="utf-8")).get(
                "digest16"
            )
        ),
        "invariants": {
            "ENTITY_NE_CARRIER": True,
            "VIEW_NE_SOURCE_TRUTH": True,
            "NO_LAST_WRITE_WINS": True,
            "UNKNOWN_AND_CONFLICT_SURVIVE": True,
        },
        "runtime_boundary": (
            "No live Archivarius process invoked; this adapter emits "
            "Archivarius-compatible reconciliation evidence against the local entity substrate."
        ),
        "alias_collisions_in_view": index.get("alias_collisions", []),
    }
    out = store.entity_dir(entity_id) / "ARCHIVARIUS_RECONCILE.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(out)
    return receipt


def rebuild_index(
    *,
    world: WorldStore | None = None,
    emit_drive_uploads: bool = True,
    drive_default_folder: str | None = None,
) -> dict[str, Any]:
    """Rebuild the alias/entity VIEW; optionally also emit pending Drive uploads
    for any claim flagged ``cross_host_critical`` (Phase 5.5.B hook)."""
    store = world or WorldStore()
    payload = store.rebuild_index()
    if emit_drive_uploads:
        # Import here to avoid any circular-import risk at module load.
        from .drive_export import emit_pending_uploads_for_critical_claims

        try:
            report = emit_pending_uploads_for_critical_claims(
                world=store, default_folder_id=drive_default_folder
            )
            if report.get("pending_count"):
                payload["drive_export_report"] = report
        except Exception as exc:  # noqa: BLE001  — surfaced in receipt, not fatal
            payload["drive_export_error"] = f"{type(exc).__name__}: {exc}"
    return payload


def resolve_via_bridge(query: str, *, world: WorldStore | None = None) -> dict[str, Any]:
    """resolve entity → identity → carriers/authority/conflicts → mount material."""
    store = world or WorldStore()
    mounted = store.resolve(query)
    recon = reconcile_entity(mounted["entity_id"], world=store)
    return {
        "schema": BRIDGE_SCHEMA,
        "query": query,
        "mount": mounted,
        "reconciliation": recon,
    }
