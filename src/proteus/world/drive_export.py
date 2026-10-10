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

from .drive_carrier import entity_content_sha256, export_entity_carrier_bundle
from .store import WorldStore

EXPORT_SCHEMA = "proteus.drive_export.v0.2"

DEFAULT_PENDING_DIR_NAME = "pending_drive_uploads"

MANIFEST_SUFFIX = ".PENDING_DRIVE_UPLOAD.json"


def _latest_manifest(entity_id: str, out_dir: Path) -> dict[str, Any] | None:
    """Newest previously-emitted manifest for this entity, or None.

    Filenames carry a sortable UTC stamp, so lexical max is chronological max.
    """
    newest: dict[str, Any] | None = None
    newest_key = ""
    for mp in out_dir.glob(f"{entity_id}.*{MANIFEST_SUFFIX}"):
        if mp.name <= newest_key:
            continue
        try:
            newest = json.loads(mp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # unreadable/corrupt manifest must not block a fresh export
        newest_key = mp.name
    return newest


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
    # Microsecond stamp, NOT whole seconds. The previous format truncated to
    # "%Y%m%dT%H%M%S", so two exports inside the same second produced the same
    # filename and the second silently OVERWROTE the first - losing a historical
    # event snapshot without any error. The content digest is folded into the
    # name too, so a bundle is self-describing and two different states can never
    # collide on disk.
    content_sha = entity_content_sha256(entity_id, world=store)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    bundle_path = out_dir / f"{entity_id}.{stamp}.{content_sha[:12]}.carrier.zip"
    meta = export_entity_carrier_bundle(entity_id, world=store, out_path=bundle_path)
    meta.pop("payload", None)
    if meta["content_sha256"] != content_sha:
        # The entity changed underneath us between hashing and packing. Refuse to
        # label the bundle with a digest it does not have.
        raise RuntimeError(
            f"entity {entity_id} mutated during export: "
            f"{content_sha} -> {meta['content_sha256']}"
        )
    manifest = {
        "schema": EXPORT_SCHEMA,
        "entity_id": entity_id,
        "bundle_path": str(bundle_path),
        # Container digest: unique per export, useless for deduplication.
        "bundle_sha256": meta["sha256"],
        # Content digest: stable while the entity is unchanged. THE dedup key.
        "content_sha256": meta["content_sha256"],
        "bundle_bytes": meta["bytes"],
        "drive_export_target": folder_id,
        "generated_utc": utc_now(),
        "upload_status": "PENDING",
        "upload_transport_note": (
            "NO UNATTENDED UPLOADER IS WIRED. Verified 2026-10-10: the connected "
            "Claude Google Drive MCP does expose a real binary create into the "
            "target folder (1064-byte probe round-tripped byte-identical), so "
            "write capability is proven, not merely 'Connected'. It is NOT usable "
            "as a daemon: payload bytes must cross the model token stream as "
            "base64 in both directions, which is not byte-reliable at bundle size "
            "(a 13527-byte archive came back with one flipped base64 character, "
            "2 bad bytes, failing CRC). An unattended consumer therefore needs a "
            "credentialed non-model transport (service account / rclone / native "
            "Drive client) that this host does not yet have authorised. Until "
            "then: status stays PENDING, and GIT_PASS must never be reported as "
            "cross-host delivery."
        ),
    }
    manifest_path = out_dir / f"{entity_id}.{stamp}.{content_sha[:12]}{MANIFEST_SUFFIX}"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def emit_pending_uploads_for_critical_claims(
    *,
    world: WorldStore | None = None,
    default_folder_id: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Hook target: after rebuild_index, scan and produce manifests.

    IDEMPOTENT ON SEMANTIC CONTENT. A cycle in which an entity did not change
    produces NO new bundle and NO new manifest.

    This is called from ``rebuild_index`` on every 15-minute sync. The previous
    version emitted unconditionally and justified it in its own docstring with
    "the real uploader will deduplicate by sha256". That uploader never existed,
    and the sha it named (the zip digest) could not have deduplicated anything
    anyway, because the zip embeds ``exported_utc``. The measured result on
    2026-10-10 was 209 bundles / 418 files / 3.7 MB for 125 real content states,
    the newest of which had been republished 48 times unchanged over 12 hours.

    Backpressure is applied by SUPPRESSION, never by deletion: existing bundles
    are historical event snapshots and are left untouched. Pass ``force=True``
    to re-emit regardless (operator escape hatch).
    """
    store = world or WorldStore()
    out_dir = store.root / DEFAULT_PENDING_DIR_NAME
    pending = scan_pending_exports(world=store)
    produced: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for p in pending:
        eid = p["entity_id"]
        folder = p.get("drive_export_target") or default_folder_id
        content_sha = entity_content_sha256(eid, world=store)
        if not force:
            prev = _latest_manifest(eid, out_dir) if out_dir.is_dir() else None
            if (
                prev is not None
                and prev.get("content_sha256") == content_sha
                and prev.get("bundle_path")
                and Path(prev["bundle_path"]).exists()
            ):
                # Unchanged AND the prior payload is still on disk -> no-op.
                skipped.append(
                    {
                        "entity_id": eid,
                        "content_sha256": content_sha,
                        "reason": "UNCHANGED_SINCE_LAST_EXPORT",
                        "existing_bundle_path": prev["bundle_path"],
                        "existing_generated_utc": prev.get("generated_utc"),
                    }
                )
                continue
        produced.append(
            export_entity_to_drive_folder(eid, folder_id=folder, world=store)
        )
    return {
        "schema": EXPORT_SCHEMA,
        "scanned_utc": utc_now(),
        "pending_count": len(pending),
        "emitted_count": len(produced),
        "skipped_count": len(skipped),
        "manifests": produced,
        "skipped": skipped,
    }
