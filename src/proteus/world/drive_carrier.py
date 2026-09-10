"""Cloud/Drive carrier interface for entity substrate.

Local semantic files remain source of truth for this slice. Drive payloads are
carriers with provider IDs — not a replacement ontology.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from .store import WorldStore

CARRIER_SCHEMA = "proteus.drive_entity_carrier.v0.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def export_entity_carrier_bundle(
    entity_id: str,
    *,
    world: WorldStore | None = None,
    out_path: Path | None = None,
) -> dict[str, Any]:
    """Pack local entity carrier files into a zip bytes/path for cloud upload."""
    store = world or WorldStore()
    ed = store.entity_dir(entity_id)
    if not ed.is_dir():
        raise FileNotFoundError(entity_id)
    files = {}
    for p in ed.rglob("*"):
        if p.is_file():
            rel = p.relative_to(ed).as_posix()
            files[rel] = p.read_bytes()
    manifest = {
        "schema": CARRIER_SCHEMA,
        "entity_id": entity_id,
        "exported_utc": utc_now(),
        "files": sorted(files.keys()),
        "sha256": hashlib.sha256(
            b"".join(files[k] for k in sorted(files.keys()))
        ).hexdigest(),
        "note": "Carrier bundle; ENTITY ≠ this zip",
    }
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("CARRIER_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
        for rel, data in files.items():
            zf.writestr(rel, data)
    payload = buf.getvalue()
    meta = {
        "schema": CARRIER_SCHEMA,
        "entity_id": entity_id,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "manifest": manifest,
        "transport": "bundle_ready",
    }
    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(payload)
        meta["path"] = str(out_path)
    meta["payload"] = payload  # caller may upload; tests should pop before JSON dump
    return meta


def import_entity_carrier_bundle(
    bundle_path: Path,
    *,
    world: WorldStore | None = None,
    expect_entity_id: str | None = None,
) -> dict[str, Any]:
    """Readback a carrier zip into a staging dir and compare to local authority.

    Does NOT last-write-wins overwrite local claims. Returns reconciliation report.
    """
    store = world or WorldStore()
    bundle_path = Path(bundle_path)
    with zipfile.ZipFile(bundle_path, "r") as zf:
        manifest = json.loads(zf.read("CARRIER_MANIFEST.json").decode("utf-8"))
        eid = manifest["entity_id"]
        if expect_entity_id and expect_entity_id != eid:
            raise ValueError(f"Entity id mismatch: {expect_entity_id} vs {eid}")
        staged = store.root / "_drive_staging" / eid
        if staged.exists():
            for p in staged.rglob("*"):
                if p.is_file():
                    p.unlink()
        staged.mkdir(parents=True, exist_ok=True)
        for name in zf.namelist():
            if name == "CARRIER_MANIFEST.json":
                continue
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(name))
    local = store.mount(eid)
    staged_claims = []
    sc = staged / "claims.jsonl"
    if sc.is_file():
        for line in sc.read_text(encoding="utf-8").splitlines():
            if line.strip():
                staged_claims.append(json.loads(line))
    local_ids = {c["claim_id"] for c in local["claims"]}
    staged_ids = {c["claim_id"] for c in staged_claims}
    report = {
        "schema": CARRIER_SCHEMA,
        "reconciled_utc": utc_now(),
        "entity_id": eid,
        "provider_bundle": str(bundle_path),
        "local_claim_ids": sorted(local_ids),
        "cloud_claim_ids": sorted(staged_ids),
        "only_local": sorted(local_ids - staged_ids),
        "only_cloud": sorted(staged_ids - local_ids),
        "shared": sorted(local_ids & staged_ids),
        "no_last_write_wins": True,
        "local_authority_preserved": True,
        "staged_path": str(staged),
        "manifest": manifest,
    }
    # Record Drive carrier pointer if provider id supplied via sidecar
    sidecar = bundle_path.with_suffix(bundle_path.suffix + ".provider.json")
    if sidecar.is_file():
        prov = json.loads(sidecar.read_text(encoding="utf-8-sig"))
        store.add_carrier(
            eid,
            {
                "role": "BACKUP",
                "kind": "google_drive",
                "provider_id": prov.get("file_id"),
                "title": prov.get("title"),
                "authority": "cloud_carrier",
                "currentness": "synced_snapshot",
                "recorded_utc": utc_now(),
            },
        )
        report["provider"] = prov
    recon_path = store.entity_dir(eid) / "DRIVE_RECONCILE.json"
    recon_path.write_text(json.dumps({k: v for k, v in report.items()}, indent=2) + "\n", encoding="utf-8")
    report["receipt_path"] = str(recon_path)
    return report
