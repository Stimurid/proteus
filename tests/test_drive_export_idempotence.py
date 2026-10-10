"""Issue #3 / P2-E: the Drive exporter must be idempotent on semantic content.

Before this change ``rebuild_index`` emitted a fresh carrier bundle on EVERY
15-minute sync, forever, with no consumer. Measured on the live world on
2026-10-10: 209 bundles + 209 manifests = 3.7 MB, all upload_status=PENDING,
for only 125 distinct content states - and the newest state had been
republished 48 times unchanged across 12 hours.

The exporter justified this in its own docstring ("the real uploader will
deduplicate by sha256"). That uploader did not exist, and the sha it named -
the zip digest - could never have deduplicated anything, because the zip
embeds ``exported_utc`` and is therefore byte-unique on every run.

These tests pin the repaired contract:
  * an unchanged cycle produces NO new payload
  * a changed claim DOES produce a new payload
  * suppression never deletes history
  * a missing payload is re-emitted (crash/GC resumption)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from proteus.world.drive_carrier import (  # noqa: E402
    entity_content_sha256,
    export_entity_carrier_bundle,
)
from proteus.world.drive_export import (  # noqa: E402
    DEFAULT_PENDING_DIR_NAME,
    emit_pending_uploads_for_critical_claims,
)
from proteus.world.store import WorldStore  # noqa: E402

ENTITY = "entity.test.exporter"
FOLDER = "test-folder-id"


def _claim(cid: str, body: str) -> str:
    return json.dumps(
        {
            "claim_id": cid,
            "subject": ENTITY,
            "body": body,
            "status": "current",
            "cross_host_critical": True,
            "drive_export_target": FOLDER,
        }
    )


@pytest.fixture()
def world(tmp_path, monkeypatch):
    """An isolated world. PROTEUS_WORLD_ROOT is bound so nothing can reach the
    real ~/.aiye/world (that escape is exactly what Issue #1 round 3 fixed)."""
    root = tmp_path / "world"
    (root / "entities" / ENTITY).mkdir(parents=True)
    (root / "index").mkdir(parents=True)
    monkeypatch.setenv("PROTEUS_WORLD_ROOT", str(root))
    ed = root / "entities" / ENTITY
    (ed / "identity.json").write_text(
        json.dumps({"entity_id": ENTITY, "name": "exporter test"}), encoding="utf-8"
    )
    (ed / "claims.jsonl").write_text(_claim("claim.one", "first") + "\n", encoding="utf-8")
    return WorldStore(root=root) if _accepts_root() else WorldStore()


def _accepts_root() -> bool:
    import inspect

    return "root" in inspect.signature(WorldStore.__init__).parameters


def _bundles(store: WorldStore) -> list[Path]:
    d = store.root / DEFAULT_PENDING_DIR_NAME
    return sorted(d.glob("*.carrier.zip")) if d.is_dir() else []


def _manifests(store: WorldStore) -> list[Path]:
    d = store.root / DEFAULT_PENDING_DIR_NAME
    return sorted(d.glob("*.PENDING_DRIVE_UPLOAD.json")) if d.is_dir() else []


def test_content_hash_is_stable_but_zip_hash_is_not(world, tmp_path):
    """The stated reason the old dedup could never work."""
    a = export_entity_carrier_bundle(ENTITY, world=world, out_path=tmp_path / "a.zip")
    b = export_entity_carrier_bundle(ENTITY, world=world, out_path=tmp_path / "b.zip")
    assert a["content_sha256"] == b["content_sha256"], "content digest must be stable"
    assert a["sha256"] != b["sha256"], (
        "zip digest is expected to differ across exports (exported_utc); if this "
        "ever starts matching, the dedup key choice should be revisited"
    )
    assert a["content_sha256"] == entity_content_sha256(ENTITY, world=world)


def test_first_cycle_emits(world):
    r = emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    assert r["pending_count"] == 1
    assert r["emitted_count"] == 1
    assert r["skipped_count"] == 0
    assert len(_bundles(world)) == 1
    assert len(_manifests(world)) == 1
    m = json.loads(_manifests(world)[0].read_text(encoding="utf-8"))
    assert m["content_sha256"] == entity_content_sha256(ENTITY, world=world)
    assert m["upload_status"] == "PENDING"


def test_noop_cycle_creates_no_new_payload(world):
    """THE regression: 48 identical bundles in 12 hours must become 1."""
    emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    before_b = [p.name for p in _bundles(world)]
    before_m = [p.name for p in _manifests(world)]

    for _ in range(5):  # five unchanged "15-minute cycles"
        r = emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
        assert r["emitted_count"] == 0
        assert r["skipped_count"] == 1
        assert r["skipped"][0]["reason"] == "UNCHANGED_SINCE_LAST_EXPORT"

    assert [p.name for p in _bundles(world)] == before_b, "no new bundle may appear"
    assert [p.name for p in _manifests(world)] == before_m, "no new manifest may appear"


def test_changed_claim_emits_a_new_payload(world):
    emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    first_sha = entity_content_sha256(ENTITY, world=world)

    cf = world.root / "entities" / ENTITY / "claims.jsonl"
    with cf.open("a", encoding="utf-8") as fh:  # append-only, as the ledger requires
        fh.write(_claim("claim.two", "second") + "\n")

    assert entity_content_sha256(ENTITY, world=world) != first_sha
    r = emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    assert r["emitted_count"] == 1, "a real semantic change must still be exported"
    assert r["skipped_count"] == 0
    assert len(_bundles(world)) == 2


def test_suppression_never_deletes_history(world):
    emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    cf = world.root / "entities" / ENTITY / "claims.jsonl"
    with cf.open("a", encoding="utf-8") as fh:
        fh.write(_claim("claim.two", "second") + "\n")
    emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    for _ in range(3):
        emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)

    # Both historical event snapshots survive; backpressure is suppression only.
    assert len(_bundles(world)) == 2
    assert len(_manifests(world)) == 2


def test_missing_bundle_is_reemitted(world):
    """Crash / external cleanup between emit and consumption must self-heal."""
    emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    os.remove(_bundles(world)[0])
    r = emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    assert r["emitted_count"] == 1, "payload gone -> must re-emit, not silently skip"


def test_force_overrides_suppression(world):
    emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    r = emit_pending_uploads_for_critical_claims(
        world=world, default_folder_id=FOLDER, force=True
    )
    assert r["emitted_count"] == 1
    assert len(_bundles(world)) == 2


def test_non_critical_entity_is_never_exported(world):
    cf = world.root / "entities" / ENTITY / "claims.jsonl"
    cf.write_text(
        json.dumps({"claim_id": "claim.plain", "subject": ENTITY, "status": "current"})
        + "\n",
        encoding="utf-8",
    )
    r = emit_pending_uploads_for_critical_claims(world=world, default_folder_id=FOLDER)
    assert r["pending_count"] == 0
    assert r["emitted_count"] == 0
    assert _bundles(world) == []
