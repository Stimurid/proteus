"""Drive export automation for cross-host-critical claims (Phase 5.5.B).

Claim schema extension (optional):
    - ``cross_host_critical: bool``        — mark a claim as needing cloud carrier
    - ``drive_export_target: str``         — Google Drive folder id (fallback: config)

This module:
    1. Scans world entities for current claims flagged ``cross_host_critical``.
    2. Produces SHA-sealed carrier bundles via ``drive_carrier.export_entity_carrier_bundle``.
    3. Writes a per-entity ``PENDING_DRIVE_UPLOAD.json`` pointing at the bundle +
       target folder id so the drive-fetch upload wrapper can pick it up.

Upload transport is out of scope here (drive-fetch MCP is currently fetch-only;
upload wrapper is deferred). The ledger makes "what should be uploaded next" a
first-class artifact that is itself tracked in git (and therefore cross-host
visible on every pull).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .drive_carrier import export_entity_carrier_bundle
from .store import WorldStore

EXPORT_SCHEMA = "proteus.drive_export.v0.1"

DEFAULT_PENDING_DIR_NAME = "pending_drive_uploads"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def scan_pending_exports(*, world: WorldStore | None = None) -> list[dict[str, Any]]:
    """Return a list of {entity_id, claim_ids, drive_export_target} for all
    entities carrying at least one current ``cross_host_critical`` claim."""
    store = world or WorldStore()
    pending: list[dict[str, Any]] = []
    for eid in store.list_entity_ids():
        claims = store.list_claims(eid)
        hits = [c for c in claims if c.get("cross_host_critical") and c.get("status") != "superseded"]
        if not hits:
            continue
        # Entity-level target: use any first-seen non-empty target, else None.
        target = None
        for c in hits:
            t = c.get("drive_export_target")
            if t:
                target = t
                break
        pending.append(
            {
                "entity_id": eid,
                "claim_ids": [c["claim_id"] for c in hits],
                "drive_export_target": target,
            }
        )
    return pending


def export_entity_to_drive_folder(
    entity_id: str,
    *,
    folder_id: str | None,
    out_dir: Path | None = None,
    world: WorldStore | None = None,
) -> dict[str, Any]:
    """Produce the carrier bundle and a PENDING_DRIVE_UPLOAD manifest.

    Returns the manifest dict. Does NOT upload to Drive — see module docstring.
    """
    store = world or WorldStore()
    out_dir = Path(out_dir) if out_dir else (store.root / DEFAULT_PENDING_DIR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_now().replace(":", "").replace("-", "")[:15]  # 2026-10-08T18:30 -> 20261008T1830
    bundle_path = out_dir / f"{entity_id}.{stamp}.carrier.zip"
    meta = export_entity_carrier_bundle(entity_id, world=store, out_path=bundle_path)
    meta.pop("payload", None)
    manifest = {
        "schema": EXPORT_SCHEMA,
        "entity_id": entity_id,
        "bundle_path": str(bundle_path),
        "bundle_sha256": meta["sha256"],
        "bundle_bytes": meta["bytes"],
        "drive_export_target": folder_id,
        "generated_utc": utc_now(),
        "upload_status": "PENDING",
        "upload_transport_note": (
            "drive-fetch MCP currently exposes only download; upload wrapper to be "
            "added in a follow-up slice. For now a human/agent with Drive write "
            "capability can post this bundle to the target folder."
        ),
    }
    manifest_path = out_dir / f"{entity_id}.{stamp}.PENDING_DRIVE_UPLOAD.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def emit_pending_uploads_for_critical_claims(
    *,
    world: WorldStore | None = None,
    default_folder_id: str | None = None,
) -> dict[str, Any]:
    """Hook target: after rebuild_index, scan and produce manifests.

    Returns a run report. Safe to call repeatedly — each run stamps a fresh
    bundle, which the real uploader will deduplicate by sha256.
    """
    store = world or WorldStore()
    pending = scan_pending_exports(world=store)
    produced = []
    for p in pending:
        folder = p.get("drive_export_target") or default_folder_id
        m = export_entity_to_drive_folder(
            p["entity_id"], folder_id=folder, world=store
        )
        produced.append(m)
    return {
        "schema": EXPORT_SCHEMA,
        "scanned_utc": utc_now(),
        "pending_count": len(pending),
        "manifests": produced,
    }
