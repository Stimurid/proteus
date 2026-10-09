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
    """Produce reconciliation evidence for one entity + rebuild generated VIEW.

    IDEMPOTENCE CONTRACT (Stimurid/proteus#2): identical semantic input
    produces identical ARCHIVARIUS_RECONCILE.json on disk — no Git churn
    from observation timestamps. The volatile `reconciled_utc` is returned
    in the API response for live callers but written to the file only when
    the semantic payload (identity/carriers/counts/digest/collisions/invariants)
    actually changed. File mtime therefore reliably marks real world changes.
    """
    store = world or WorldStore()
    mounted = store.mount(entity_id)
    index = store.rebuild_index()
    reconciled_utc = utc_now()
    semantic_body = {
        "schema": BRIDGE_SCHEMA,
        "entity_id": entity_id,
        "identity": mounted["identity"],
        "carriers": mounted["carriers"]["carriers"],
        "current_claim_count": len(mounted["current_claims"]),
        "conflict_count": len(mounted["conflicts"]),
        "unknown_count": len(mounted["unknowns"]),
        "project_links": mounted["projects"].get("projects", []),
        "index_digest16": index.get("digest16"),
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
    existing_body: dict[str, Any] | None = None
    if out.exists():
        try:
            existing_full = json.loads(out.read_text(encoding="utf-8"))
            existing_body = {k: v for k, v in existing_full.items() if k != "reconciled_utc"}
        except Exception:
            existing_body = None

    semantic_changed = existing_body != semantic_body
    file_payload = {**semantic_body, "reconciled_utc": reconciled_utc}
    if semantic_changed:
        out.write_text(json.dumps(file_payload, indent=2) + "\n", encoding="utf-8")

    # Operational heartbeat (observed time + change decision) is persisted
    # outside Git-tracked entity files so monitoring survives without churn.
    try:
        hb_dir = store.index_dir / "reconcile_heartbeat"
        hb_dir.mkdir(parents=True, exist_ok=True)
        (hb_dir / f"{entity_id}.json").write_text(
            json.dumps(
                {
                    "entity_id": entity_id,
                    "last_checked_utc": reconciled_utc,
                    "semantic_changed": semantic_changed,
                    "digest16": index.get("digest16"),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except Exception:
        pass  # heartbeat is best-effort; must not fail reconcile

    receipt = {**file_payload, "receipt_path": str(out), "semantic_changed": semantic_changed}
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
