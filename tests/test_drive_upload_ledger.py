"""Issue #3 / P2-D: durable, idempotent, verify-before-commit upload ledger.

The properties pinned here are the ones the field failure actually demanded:
no duplicate upload on rerun, a crash between write and proof is recoverable,
a corrupted or permission-denied remote NEVER reports PASS, originals are
preserved, and with no authorised transport the answer is an explicit
AUTH_REQUIRED rather than a pretend success.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from proteus.world.drive_export import (  # noqa: E402
    DEFAULT_PENDING_DIR_NAME,
    emit_pending_uploads_for_critical_claims,
)
from proteus.world.drive_upload_ledger import (  # noqa: E402
    AUTH_REQUIRED,
    FAILED,
    UPLOADED,
    VERIFIED,
    MockTransport,
    append_record,
    is_verified,
    ledger_path,
    plan_uploads,
    read_records,
    run_uploads,
    state_by_content,
)
from proteus.world.store import WorldStore  # noqa: E402

ENTITY = "entity.test.uploader"
FOLDER = "folder-xyz"


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
    root = tmp_path / "world"
    ed = root / "entities" / ENTITY
    ed.mkdir(parents=True)
    (root / "index").mkdir(parents=True)
    monkeypatch.setenv("PROTEUS_WORLD_ROOT", str(root))
    (ed / "identity.json").write_text(
        json.dumps({"entity_id": ENTITY, "name": "uploader test"}), encoding="utf-8"
    )
    (ed / "claims.jsonl").write_text(_claim("c1", "first") + "\n", encoding="utf-8")
    store = WorldStore(root=root)
    emit_pending_uploads_for_critical_claims(world=store, default_folder_id=FOLDER)
    return store


def _bundles(store):
    d = store.root / DEFAULT_PENDING_DIR_NAME
    return sorted(d.glob("*.carrier.zip"))


def test_no_transport_reports_auth_required_not_success(world):
    r = run_uploads(world, transport=None, dry_run=False)
    assert r["transport"]["status"] == AUTH_REQUIRED
    assert r["mode"] == "NO_TRANSPORT"
    assert r["verified"] == []
    assert r["uploaded"] == []
    assert r["eligible"] == 1, "it must still be able to say WHAT is outstanding"
    assert r["transport"]["one_user_action"]


def test_dry_run_changes_nothing(world):
    t = MockTransport()
    r = run_uploads(world, transport=t, dry_run=True)
    assert r["mode"] == "DRY_RUN"
    assert t.uploads == 0
    assert read_records(world) == []
    assert not ledger_path(world).exists()


def test_execute_uploads_then_verifies(world):
    t = MockTransport()
    r = run_uploads(world, transport=t, dry_run=False)
    assert len(r["verified"]) == 1
    assert r["failed"] == []
    recs = read_records(world)
    assert [x["status"] for x in recs] == [UPLOADED, VERIFIED], (
        "UPLOADED must be durable BEFORE the proof, so a crash is recoverable"
    )
    cs = recs[0]["content_sha256"]
    assert is_verified(world, cs)
    assert _bundles(world), "original payload must be preserved after verification"


def test_rerun_does_not_upload_twice(world):
    t = MockTransport()
    run_uploads(world, transport=t, dry_run=False)
    assert t.uploads == 1
    for _ in range(3):
        r = run_uploads(world, transport=t, dry_run=False)
        assert r["to_upload"] == []
        assert any(s["reason"] == "ALREADY_VERIFIED" for s in r["skipped"])
    assert t.uploads == 1, "idempotent: a rerun must never duplicate a verified object"


def test_crash_between_upload_and_receipt_resumes_without_duplicate(world):
    """Simulate the crash directly: a durable UPLOADED with no VERIFIED."""
    t = MockTransport()
    plan = plan_uploads(world)
    m = plan["to_upload"][0]
    rid = t.upload(Path(m["bundle_path"]), Path(m["bundle_path"]).name, FOLDER)
    append_record(
        world,
        {
            "entity_id": m["entity_id"],
            "content_sha256": m["content_sha256"],
            "bundle_path": m["bundle_path"],
            "drive_file_id": rid,
            "status": UPLOADED,
            "attempt": 1,
        },
    )
    assert t.uploads == 1

    r = run_uploads(world, transport=t, dry_run=False)
    assert t.uploads == 1, "resume must verify the existing object, not re-upload"
    assert len(r["verified"]) == 1
    assert r["verified"][0]["resumed"] is True
    assert is_verified(world, m["content_sha256"])


def test_corrupted_remote_is_never_reported_as_pass(world):
    t = MockTransport(corrupt=True)
    r = run_uploads(world, transport=t, dry_run=False)
    assert r["verified"] == []
    assert len(r["failed"]) == 1
    last = state_by_content(world)[r["failed"][0]["content_sha256"]]
    assert last["status"] == FAILED
    assert last["error"] == "REMOTE_READBACK_MISMATCH"
    assert not is_verified(world, r["failed"][0]["content_sha256"])


def test_permission_denied_does_not_report_pass_and_backs_off(world):
    t = MockTransport(fail_times=1)
    r = run_uploads(world, transport=t, dry_run=False)
    assert r["verified"] == []
    assert len(r["failed"]) == 1
    rec = read_records(world)[-1]
    assert rec["status"] in ("RETRY", FAILED)
    assert rec["backoff_seconds"] >= 2
    assert "simulated transport failure" in rec["error"]

    # outage ends -> next run succeeds, nothing lost
    r2 = run_uploads(world, transport=t, dry_run=False)
    assert len(r2["verified"]) == 1


def test_backlog_collapses_to_distinct_states_and_respects_batch_cap(world):
    """209 bundles for 125 states must plan 125 uploads, not 209 - and never
    by deleting anything."""
    store = world
    cf = store.root / "entities" / ENTITY / "claims.jsonl"
    for i in range(4):
        with cf.open("a", encoding="utf-8") as fh:
            fh.write(_claim(f"c{i + 2}", f"body {i}") + "\n")
        emit_pending_uploads_for_critical_claims(world=store, default_folder_id=FOLDER)
        # re-emit twice with NO change: must not create new states
        emit_pending_uploads_for_critical_claims(world=store, default_folder_id=FOLDER)
        emit_pending_uploads_for_critical_claims(world=store, default_folder_id=FOLDER)

    plan = plan_uploads(store, batch_cap=2)
    assert plan["distinct_content_states"] == 5, plan
    assert plan["eligible"] == 5
    assert len(plan["to_upload"]) == 2, "batch cap must bound a single run"
    assert plan["deferred_by_cap"] == 3
    assert len(_bundles(store)) == 5, "no historical snapshot may be deleted"


def test_missing_bundle_is_reported_not_silently_passed(world):
    for b in _bundles(world):
        b.unlink()
    plan = plan_uploads(world)
    assert plan["to_upload"] == []
    assert any(s["reason"] == "BUNDLE_MISSING" for s in plan["skipped"])


def test_torn_final_ledger_line_does_not_destroy_history(world):
    t = MockTransport()
    run_uploads(world, transport=t, dry_run=False)
    with ledger_path(world).open("a", encoding="utf-8") as fh:
        fh.write('{"status": "UPLOAD')  # simulated crash mid-append
    recs = read_records(world)
    assert len(recs) == 2
    assert recs[-1]["status"] == VERIFIED
