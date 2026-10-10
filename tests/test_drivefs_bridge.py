"""DriveFS delivery adapter: the failures that must never become a false green.

Every test here names a way the bridge could lie about delivery:
a mount that is gone, a ``G:`` that belongs to someone else, a half-written
copy, a name that collides with different bytes, a zero-length or CRC-broken
archive, a manifest pointing at a different Drive folder, two runs racing, and
- the central one - a local ``G:`` readback being mistaken for proof that the
bytes reached Google.
"""

from __future__ import annotations

import json
import os
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from proteus.world import drivefs_bridge as fs  # noqa: E402
from proteus.world.drive_export import (  # noqa: E402
    DEFAULT_PENDING_DIR_NAME,
    emit_pending_uploads_for_critical_claims,
)
from proteus.world.store import WorldStore  # noqa: E402

ENTITY = "entity.test.drivefs"
FOLDER = "1eMS-TEST-FOLDER-ID"


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


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
    (ed / "claims.jsonl").write_text(_claim("c1", "first state") + "\n", encoding="utf-8")
    monkeypatch.setenv("PROTEUS_WORLD_ROOT", str(root))
    monkeypatch.setenv("AIYE_HOME", str(tmp_path / "aiye"))
    return WorldStore(root=root)


@pytest.fixture()
def fake_drive(tmp_path):
    """A stand-in for G: that carries the real identity markers."""
    root = tmp_path / "Gdrive"
    target = root / "My Drive" / "AORUS" / "results"
    target.mkdir(parents=True)
    for m in fs.DEFAULT_MARKERS:
        (target / m).write_text("marker", encoding="utf-8")
    return fs.DriveFsTarget(drivefs_root=root, target_dir=target, folder_id=FOLDER)


@pytest.fixture()
def ledger_dir(tmp_path):
    d = tmp_path / "bridge"
    d.mkdir()
    return d


def _up() -> bool:
    return True


def _export(world: WorldStore) -> list[dict]:
    return emit_pending_uploads_for_critical_claims(world=world)


def _manifests(world: WorldStore) -> list[dict]:
    d = world.root / DEFAULT_PENDING_DIR_NAME
    out = []
    for mp in sorted(d.glob("*.PENDING_DRIVE_UPLOAD.json")):
        m = json.loads(mp.read_text(encoding="utf-8"))
        m["_manifest_path"] = str(mp)
        out.append(m)
    return out


# ---------------------------------------------------------------------------
# target validation
# ---------------------------------------------------------------------------


def test_missing_mount_is_drivefs_unavailable_not_a_silent_skip(fake_drive, ledger_dir, world, tmp_path):
    gone = fs.DriveFsTarget(
        drivefs_root=tmp_path / "no-such-drive",
        target_dir=tmp_path / "no-such-drive" / "results",
        folder_id=FOLDER,
    )
    s = fs.run_stage(target=gone, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert s["status"] == fs.DRIVEFS_UNAVAILABLE
    assert s["exit_code"] == 2
    assert s["target"]["reason"] == "MOUNT_ROOT_ABSENT"


def test_mount_present_but_client_not_running_is_unavailable(fake_drive, ledger_dir, world):
    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir,
                     process_probe=lambda: False)
    assert s["status"] == fs.DRIVEFS_UNAVAILABLE
    assert s["target"]["reason"] == "GOOGLEDRIVEFS_NOT_RUNNING"
    assert s["exit_code"] == 2


def test_wrong_folder_on_the_right_drive_is_refused(tmp_path, world, ledger_dir):
    """A ``G:`` that mounts a DIFFERENT account must not be written to."""
    root = tmp_path / "Gdrive"
    other = root / "My Drive" / "SomebodyElse" / "results"
    other.mkdir(parents=True)
    (other / "unrelated.txt").write_text("x", encoding="utf-8")
    t = fs.DriveFsTarget(drivefs_root=root, target_dir=other, folder_id=FOLDER)

    s = fs.run_stage(target=t, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert s["status"] == fs.MARKER_MISSING
    assert s["exit_code"] == 2
    assert list(other.iterdir()) == [other / "unrelated.txt"], "nothing may be written"


def test_marker_threshold_requires_more_than_one_coincidence(fake_drive, ledger_dir):
    for m in fs.DEFAULT_MARKERS[1:]:
        (fake_drive.target_dir / m).unlink()
    v = fs.validate_target(fake_drive, process_probe=_up)
    assert v["status"] == fs.MARKER_MISSING
    assert len(v["checks"]["markers_found"]) == 1


def test_validate_target_never_writes_to_the_corpus(fake_drive):
    before = sorted(p.name for p in fake_drive.target_dir.iterdir())
    fs.validate_target(fake_drive, process_probe=_up)
    assert sorted(p.name for p in fake_drive.target_dir.iterdir()) == before


# ---------------------------------------------------------------------------
# staging
# ---------------------------------------------------------------------------


def test_stage_delivers_and_reports_staged_local_not_verified(world, fake_drive, ledger_dir):
    _export(world)
    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)

    assert s["status"] == "STAGED_UNVERIFIED", "a G: copy is never a PASS"
    assert s["exit_code"] == 0
    assert len(s["staged"]) == 1
    rec = s["staged"][0]
    assert rec["status"] == fs.STAGED_LOCAL
    dest = Path(rec["dest_path"])
    assert dest.is_file()
    assert fs.sha256_file(dest)[0] == rec["bundle_sha256"]
    # and nothing anywhere claims the cloud has it
    assert not any(r.get("status") == fs.CLOUD_VERIFIED for r in fs.read_ledger(ledger_dir))


def test_rerun_is_idempotent_and_does_not_duplicate(world, fake_drive, ledger_dir):
    _export(world)
    first = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    after_first = sorted(p.name for p in fake_drive.target_dir.iterdir())

    second = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert second["plan"]["batch_size"] == 0, "an already-delivered state must not be re-planned"
    assert sorted(p.name for p in fake_drive.target_dir.iterdir()) == after_first
    assert second["exit_code"] == 0
    assert len(first["staged"]) == 1


def test_destination_present_with_identical_bytes_is_skip_not_rewrite(world, fake_drive, ledger_dir):
    _export(world)
    m = _manifests(world)[0]
    r1 = fs.stage_one(fake_drive, m)
    assert r1["status"] == fs.STAGED_LOCAL
    mtime = Path(r1["dest_path"]).stat().st_mtime_ns

    r2 = fs.stage_one(fake_drive, m)
    assert r2["status"] == fs.SKIPPED_IDENTICAL
    assert Path(r1["dest_path"]).stat().st_mtime_ns == mtime, "the file was not rewritten"


def test_same_name_different_bytes_is_refused_never_overwritten(world, fake_drive, ledger_dir):
    _export(world)
    m = _manifests(world)[0]
    name = fs.deterministic_name(m["entity_id"], m["content_sha256"], m["bundle_sha256"])
    victim = fake_drive.target_dir / name
    victim.write_bytes(b"SOMEONE ELSE'S PAYLOAD")

    r = fs.stage_one(fake_drive, m)
    assert r["status"] == fs.STAGE_FAILED
    assert r["reason"] == fs.NAME_COLLISION_DIFFERENT_PAYLOAD
    assert victim.read_bytes() == b"SOMEONE ELSE'S PAYLOAD", "pre-existing bytes survived"


def test_manifest_targeting_a_different_drive_folder_is_rejected(world, fake_drive):
    _export(world)
    m = dict(_manifests(world)[0], drive_export_target="SOME-OTHER-FOLDER")
    r = fs.stage_one(fake_drive, m)
    assert r["status"] == fs.STAGE_FAILED
    assert r["reason"] == fs.MANIFEST_TARGET_MISMATCH
    assert not list(fake_drive.target_dir.glob("proteus-carrier.*"))


def test_zero_length_bundle_never_reaches_drive(world, fake_drive, tmp_path):
    _export(world)
    m = dict(_manifests(world)[0])
    empty = tmp_path / "empty.carrier.zip"
    empty.write_bytes(b"")
    m["bundle_path"] = str(empty)
    m.pop("bundle_sha256", None)
    m.pop("bundle_bytes", None)
    r = fs.stage_one(fake_drive, m)
    assert r["status"] == fs.STAGE_FAILED
    assert r["reason"] == fs.BUNDLE_EMPTY
    assert not list(fake_drive.target_dir.glob("proteus-carrier.*"))


def _flip_byte_in_member(src: Path, dst: Path, member: str) -> None:
    """Corrupt one byte inside a member's compressed data, so the CRC must notice.

    Flipping at an arbitrary offset is not a test of anything: a small archive
    has slack (headers, the central directory) where a flip changes no CRC.
    """
    data = bytearray(src.read_bytes())
    with zipfile.ZipFile(src) as zf:
        info = zf.getinfo(member)
    with open(src, "rb") as fh:
        fh.seek(info.header_offset + 26)
        name_len = int.from_bytes(fh.read(2), "little")
        extra_len = int.from_bytes(fh.read(2), "little")
    start = info.header_offset + 30 + name_len + extra_len
    at = start + info.compress_size // 2
    data[at] ^= 0xFF
    dst.write_bytes(bytes(data))


def test_corrupt_zip_never_reaches_drive(world, fake_drive, tmp_path):
    """The 2-byte base64 corruption class, caught before the copy."""
    _export(world)
    m = dict(_manifests(world)[0])
    broken = tmp_path / "broken.carrier.zip"
    _flip_byte_in_member(Path(m["bundle_path"]), broken, "claims.jsonl")
    m["bundle_path"] = str(broken)
    m.pop("bundle_sha256", None)
    m.pop("bundle_bytes", None)

    r = fs.stage_one(fake_drive, m)
    assert r["status"] == fs.STAGE_FAILED
    assert r["reason"] == fs.ZIP_CORRUPT
    assert not list(fake_drive.target_dir.glob("proteus-carrier.*"))


def test_archive_without_a_carrier_manifest_is_not_a_carrier(world, fake_drive, tmp_path):
    _export(world)
    m = dict(_manifests(world)[0])
    impostor = tmp_path / "impostor.zip"
    with zipfile.ZipFile(impostor, "w") as zf:
        zf.writestr("hello.txt", "a perfectly valid zip that is not a carrier")
    m["bundle_path"] = str(impostor)
    m.pop("bundle_sha256", None)
    m.pop("bundle_bytes", None)

    r = fs.stage_one(fake_drive, m)
    assert r["status"] == fs.STAGE_FAILED
    assert r["reason"] == fs.ZIP_CORRUPT
    assert not list(fake_drive.target_dir.glob("proteus-carrier.*"))


def test_content_changed_under_a_stale_manifest_is_a_digest_mismatch(world, fake_drive, tmp_path):
    _export(world)
    m = _manifests(world)[0]
    tampered = tmp_path / "tampered.carrier.zip"
    with zipfile.ZipFile(tampered, "w") as zf:
        zf.writestr("CARRIER_MANIFEST.json", json.dumps({"sha256": m["content_sha256"]}))
        zf.writestr("payload.txt", "different content")
    m2 = dict(m, bundle_path=str(tampered))

    r = fs.stage_one(fake_drive, m2)
    assert r["status"] == fs.STAGE_FAILED
    assert r["reason"] == fs.LOCAL_DIGEST_MISMATCH


def test_half_written_copy_leaves_no_destination_and_no_success(world, fake_drive, ledger_dir, monkeypatch):
    """Crash mid-copy: the temp file must never be visible under the real name."""
    _export(world)
    m = _manifests(world)[0]

    real_rename = os.rename

    def boom(src, dst):
        raise OSError("simulated crash between write and rename")

    monkeypatch.setattr(fs.os, "rename", boom)
    r = fs.stage_one(fake_drive, m)
    monkeypatch.setattr(fs.os, "rename", real_rename)

    assert r["status"] == fs.STAGE_RETRY
    assert r["reason"] == fs.COPY_FAILED
    assert not list(fake_drive.target_dir.glob("proteus-carrier.*")), "no partial under the real name"

    # and a later run completes it without a duplicate
    r2 = fs.stage_one(fake_drive, m)
    assert r2["status"] == fs.STAGED_LOCAL
    assert len(list(fake_drive.target_dir.glob("proteus-carrier.*"))) == 1


def test_abandoned_temp_files_are_reaped_and_only_ours(world, fake_drive, ledger_dir):
    stale = fake_drive.target_dir / f"{fs.TEMP_PREFIX}1234-deadbeef"
    stale.write_bytes(b"junk")
    os.utime(stale, (0, 0))
    foreign = fake_drive.target_dir / ".someone-elses.tmp"
    foreign.write_bytes(b"not ours")
    os.utime(foreign, (0, 0))

    _export(world)
    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert stale.name in s["abandoned_temps_removed"]
    assert not stale.exists()
    assert foreign.exists(), "only our own temp prefix may be reaped"


def test_readback_mismatch_removes_the_bad_copy_and_fails(world, fake_drive, monkeypatch):
    _export(world)
    m = _manifests(world)[0]
    real = fs.sha256_file
    calls = {"n": 0}

    def flaky(path):
        calls["n"] += 1
        # 1st: source digest. 2nd: readback -> lie about it.
        if calls["n"] == 2:
            return ("0" * 64, 1)
        return real(path)

    monkeypatch.setattr(fs, "sha256_file", flaky)
    r = fs.stage_one(fake_drive, m)
    monkeypatch.setattr(fs, "sha256_file", real)

    assert r["status"] == fs.STAGE_FAILED
    assert r["reason"] == fs.READBACK_MISMATCH
    assert r["bad_copy_removed"] is True
    assert not list(fake_drive.target_dir.glob("proteus-carrier.*"))


# ---------------------------------------------------------------------------
# queue reconciliation
# ---------------------------------------------------------------------------


def test_duplicate_snapshots_of_one_state_collapse_to_one_delivery(world, fake_drive, ledger_dir):
    """The real shape of the backlog: many manifests, few content states."""
    for _ in range(5):
        _export(world)
    manifests = _manifests(world)
    assert len(manifests) >= 1
    plan = fs.plan_stage(world, ledger_dir)
    assert plan["distinct_content_states"] == 1
    assert plan["eligible"] == 1

    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert len(list(fake_drive.target_dir.glob("proteus-carrier.*"))) == 1
    assert len(s["staged"]) == 1


def test_batch_cap_bounds_the_run_and_backlog_drains_over_runs(world, fake_drive, ledger_dir):
    ed = world.root / "entities" / ENTITY
    for i in range(6):
        with (ed / "claims.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(_claim(f"c{i+2}", f"state {i}") + "\n")
        _export(world)

    plan = fs.plan_stage(world, ledger_dir, batch_cap=2)
    assert plan["distinct_content_states"] >= 6
    assert len(plan["to_stage"]) == 2
    assert plan["deferred_by_cap"] == plan["eligible"] - 2

    staged_total = 0
    for _ in range(10):
        s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir,
                         batch_cap=2, process_probe=_up)
        staged_total += len(s["staged"])
        if s["plan"]["batch_size"] == 0:
            break
    assert staged_total == plan["eligible"], "bounded runs still drain the whole backlog"
    assert fs.plan_stage(world, ledger_dir)["eligible"] == 0


def test_newest_state_is_delivered_first(world, fake_drive, ledger_dir):
    ed = world.root / "entities" / ENTITY
    for i in range(4):
        with (ed / "claims.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(_claim(f"n{i}", f"state {i}") + "\n")
        _export(world)
    plan = fs.plan_stage(world, ledger_dir, batch_cap=1)
    newest = max(_manifests(world), key=lambda m: m["generated_utc"])
    assert plan["to_stage"][0]["content_sha256"] == newest["content_sha256"]


def test_originals_and_manifests_are_never_deleted(world, fake_drive, ledger_dir):
    _export(world)
    pend = world.root / DEFAULT_PENDING_DIR_NAME
    before = sorted(p.name for p in pend.iterdir())
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert sorted(p.name for p in pend.iterdir()) == before


def test_max_seconds_stops_a_long_run_without_claiming_completion(world, fake_drive, ledger_dir):
    ed = world.root / "entities" / ENTITY
    for i in range(4):
        with (ed / "claims.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(_claim(f"t{i}", f"state {i}") + "\n")
        _export(world)
    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir,
                     batch_cap=10, max_seconds=0, process_probe=_up)
    assert s["timed_out"] is True
    assert s["staged"] == []
    assert fs.plan_stage(world, ledger_dir)["eligible"] > 0, "remaining work stays visible"


# ---------------------------------------------------------------------------
# locking
# ---------------------------------------------------------------------------


def test_concurrent_run_does_not_double_stage(world, fake_drive, ledger_dir):
    _export(world)
    held = fs.BridgeLock(ledger_dir / fs.LOCK_NAME).acquire()
    try:
        s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
        assert s["status"] == "LOCK_BUSY"
        assert s["exit_code"] == 0, "an overlapping scheduled tick is not a failure"
        assert not list(fake_drive.target_dir.glob("proteus-carrier.*"))
    finally:
        held.release()
    s2 = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert len(s2["staged"]) == 1


def test_stale_lock_is_broken_and_recorded(world, fake_drive, ledger_dir):
    lp = ledger_dir / fs.LOCK_NAME
    lp.write_text(json.dumps({"pid": 999999}), encoding="utf-8")
    os.utime(lp, (0, 0))
    _export(world)
    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir,
                     process_probe=_up, lock_stale_seconds=60)
    assert s["stale_lock_broken"] is not None
    assert any(r.get("status") == "STALE_LOCK_BROKEN" for r in fs.read_ledger(ledger_dir))
    assert len(s["staged"]) == 1


def test_lock_is_released_even_when_the_pass_explodes(world, fake_drive, ledger_dir, monkeypatch):
    _export(world)
    monkeypatch.setattr(fs, "plan_stage", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert not (ledger_dir / fs.LOCK_NAME).exists()


# ---------------------------------------------------------------------------
# cloud verification handshake  -- the heart of the honesty contract
# ---------------------------------------------------------------------------


def test_staging_alone_never_produces_cloud_verified(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    assert all(r.get("status") != fs.CLOUD_VERIFIED for r in fs.read_ledger(ledger_dir))
    assert len(fs.cloud_verify_queue(ledger_dir)) == 1


def test_queue_record_is_self_sufficient_for_a_remote_verifier(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    for k in ("dest_name", "expect_sha256", "expect_bytes", "cloud_folder_id",
              "content_sha256", "entity_id", "verifier_instructions"):
        assert q.get(k), f"handoff record is missing {k}"
    assert q["status"] == "PENDING_CLOUD_VERIFY"


def _receipt_for(q: dict, **over) -> dict:
    r = {
        "schema": fs.RECEIPT_SCHEMA,
        "verified_at_utc": "2026-10-10T09:45Z",
        "source_sha256": q["expect_sha256"],
        "source_length_bytes": q["expect_bytes"],
        "cloud_file_id": "1R7oX2CRfwWrhZ2TjvmrnjvB9Ru8BgaLh",
        "cloud_parent_id": q["cloud_folder_id"],
        "cloud_download_sha256": q["expect_sha256"],
        "cloud_zip_integrity": "PASS",
        "cloud_readback_via": "independent provider download",
        "verdict": "CLOUD_VERIFIED_BYTE_IDENTICAL",
    }
    r.update(over)
    return r


def test_matching_receipt_promotes_to_cloud_verified(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]

    res = fs.import_cloud_receipt(ledger_dir, _receipt_for(q))
    assert res["ok"], res["problems"]
    assert res["record"]["status"] == fs.CLOUD_VERIFIED
    assert res["record"]["cloud_file_id"]
    assert fs.cloud_verify_queue(ledger_dir) == []


def test_receipt_with_a_different_digest_promotes_nothing(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]

    res = fs.import_cloud_receipt(ledger_dir, _receipt_for(q, cloud_download_sha256="f" * 64))
    assert res["ok"] is False
    assert res["problems"] == ["NO_MATCHING_STAGED_RECORD"]
    assert all(r.get("status") != fs.CLOUD_VERIFIED for r in fs.read_ledger(ledger_dir))
    assert len(fs.cloud_verify_queue(ledger_dir)) == 1, "still pending, not silently dropped"


def test_receipt_that_contradicts_itself_is_rejected(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    bad = _receipt_for(q)
    bad["source_sha256"] = "a" * 64  # claims one source, downloaded another
    res = fs.import_cloud_receipt(ledger_dir, bad)
    assert res["ok"] is False
    assert "RECEIPT_SELF_INCONSISTENT" in res["problems"]


def test_receipt_for_the_wrong_drive_folder_is_rejected(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    res = fs.import_cloud_receipt(ledger_dir, _receipt_for(q, cloud_parent_id="SOMEWHERE-ELSE"))
    assert res["ok"] is False
    assert "PARENT_FOLDER_MISMATCH" in res["problems"]


def test_receipt_with_wrong_byte_length_is_rejected(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    res = fs.import_cloud_receipt(ledger_dir, _receipt_for(q, source_length_bytes=1))
    assert res["ok"] is False
    assert "BYTE_LENGTH_MISMATCH" in res["problems"]


def test_receipt_without_a_cloud_file_id_is_not_evidence(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    res = fs.import_cloud_receipt(ledger_dir, _receipt_for(q, cloud_file_id=None))
    assert res["ok"] is False
    assert "NO_CLOUD_FILE_ID" in res["problems"]


def test_receipt_under_an_unknown_schema_is_rejected(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    res = fs.import_cloud_receipt(ledger_dir, _receipt_for(q, schema="something.else.v9"))
    assert res["ok"] is False
    assert any(p.startswith("WRONG_SCHEMA") for p in res["problems"])


def _presence_for(q: dict, **over) -> dict:
    e = {
        "schema": fs.PRESENCE_SCHEMA,
        "observed_at_utc": "2026-10-10T10:05Z",
        "cloud_file_name": q["dest_name"],
        "cloud_file_id": "1gmlEwHUjsIlA8Ojb00mv8KpyAwH48gCZ",
        "cloud_parent_id": q["cloud_folder_id"],
        "cloud_file_size_bytes": q["expect_bytes"],
        "observed_via": "provider metadata query, not the G: mount",
    }
    e.update(over)
    return e


def test_cloud_presence_is_recorded_but_never_counts_as_verified(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]

    res = fs.import_cloud_presence(ledger_dir, _presence_for(q))
    assert res["ok"], res["problems"]
    assert res["record"]["status"] == fs.CLOUD_PRESENT
    assert res["record"]["still_pending_byte_verification"] is True
    assert all(r.get("status") != fs.CLOUD_VERIFIED for r in fs.read_ledger(ledger_dir))
    assert len(fs.cloud_verify_queue(ledger_dir)) == 1, "presence must not clear the queue"


def test_cloud_presence_with_wrong_byte_length_is_rejected(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    res = fs.import_cloud_presence(ledger_dir, _presence_for(q, cloud_file_size_bytes=1))
    assert res["ok"] is False
    assert "BYTE_LENGTH_MISMATCH" in res["problems"]
    assert all(r.get("status") != fs.CLOUD_PRESENT for r in fs.read_ledger(ledger_dir))


def test_cloud_presence_in_the_wrong_folder_is_rejected(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    res = fs.import_cloud_presence(ledger_dir, _presence_for(q, cloud_parent_id="ELSEWHERE"))
    assert res["ok"] is False
    assert "PARENT_FOLDER_MISMATCH" in res["problems"]


def test_presence_then_verification_upgrades_but_never_downgrades(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]

    fs.import_cloud_presence(ledger_dir, _presence_for(q))
    assert fs.state_by_content(ledger_dir)[q["content_sha256"]]["status"] == fs.CLOUD_PRESENT

    fs.import_cloud_receipt(ledger_dir, _receipt_for(q))
    assert fs.state_by_content(ledger_dir)[q["content_sha256"]]["status"] == fs.CLOUD_VERIFIED

    # a later presence observation must not walk it back
    fs.import_cloud_presence(ledger_dir, _presence_for(q))
    assert fs.state_by_content(ledger_dir)[q["content_sha256"]]["status"] == fs.CLOUD_VERIFIED


def test_cloud_verified_is_not_demoted_by_a_later_local_record(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    q = fs.cloud_verify_queue(ledger_dir)[0]
    fs.import_cloud_receipt(ledger_dir, _receipt_for(q))

    fs.append_ledger(ledger_dir, {"status": fs.STAGED_LOCAL,
                                  "content_sha256": q["content_sha256"],
                                  "bundle_sha256": q["bundle_sha256"]})
    assert fs.state_by_content(ledger_dir)[q["content_sha256"]]["status"] == fs.CLOUD_VERIFIED


def test_the_real_aiye_receipt_validates_against_a_matching_staged_record(ledger_dir):
    """The actual 2026-10-10 provider verification, used as a fixture.

    Proves the contract accepts the receipt shape a real cloud verifier already
    produced, rather than one invented to fit the code.
    """
    real = {
        "schema": "proteus.drivefs_cloud_verification.v0.1",
        "verified_at_utc": "2026-10-10T09:45Z",
        "source_sha256": "3e3552cba2d6e16dfddf634c3ef85149093f043af13cddad9eb055210af4264e",
        "source_length_bytes": 17864,
        "cloud_file_id": "1R7oX2CRfwWrhZ2TjvmrnjvB9Ru8BgaLh",
        "cloud_parent_id": "1eMS-Q5kB8-ijPDLFW9qcNBjWVVTDYdR0",
        "cloud_download_sha256": "3e3552cba2d6e16dfddf634c3ef85149093f043af13cddad9eb055210af4264e",
        "cloud_zip_integrity": "PASS: unzip -t all members, no CRC errors",
        "verdict": "CLOUD_VERIFIED_BYTE_IDENTICAL",
    }
    # no staged record yet -> refuses, loudly
    assert fs.import_cloud_receipt(ledger_dir, real)["problems"] == ["NO_MATCHING_STAGED_RECORD"]

    fs.append_ledger(
        ledger_dir,
        {
            "status": fs.STAGED_LOCAL,
            "entity_id": "entity.service.proteus",
            "content_sha256": "4eba3fe4f61bae69a6a0b5c48fcc5921a5bbf13c0c49e37892ae8daeac42a253",
            "bundle_sha256": real["source_sha256"],
            "bundle_bytes": 17864,
            "dest_name": "proteus-carrier.entity.service.proteus.c4eba3fe4f61bae6.b3e3552cba2d6e16.zip",
            "cloud_folder_id": "1eMS-Q5kB8-ijPDLFW9qcNBjWVVTDYdR0",
        },
    )
    res = fs.import_cloud_receipt(ledger_dir, real)
    assert res["ok"], res["problems"]
    assert res["record"]["cloud_file_id"] == "1R7oX2CRfwWrhZ2TjvmrnjvB9Ru8BgaLh"


# ---------------------------------------------------------------------------
# foreign artifacts, ledger durability, summary
# ---------------------------------------------------------------------------


def test_previously_corrupted_artifact_is_listed_but_never_counted(world, fake_drive, ledger_dir):
    bad = fake_drive.target_dir / "entity.service.proteus.content-9289bf7eaaa562e3.20261010T073743.carrier.zip"
    bad.write_bytes(b"corrupt-from-the-base64-route")
    _export(world)
    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    names = [f["name"] for f in s["foreign_artifacts"]]
    assert bad.name in names
    assert all(f["status"] == fs.FOREIGN_UNVERIFIED for f in s["foreign_artifacts"])
    assert bad.exists(), "foreign artifacts are classified, not deleted"
    assert all(r.get("dest_name") != bad.name for r in fs.read_ledger(ledger_dir))


def test_torn_final_ledger_line_does_not_destroy_history(ledger_dir):
    fs.append_ledger(ledger_dir, {"status": fs.STAGED_LOCAL, "bundle_sha256": "a" * 64})
    with fs.ledger_path(ledger_dir).open("a", encoding="utf-8") as fh:
        fh.write('{"status": "STAGED_LOCAL", "bundle_sha')  # crash mid-append
    recs = fs.read_ledger(ledger_dir)
    assert len(recs) == 1
    assert recs[0]["bundle_sha256"] == "a" * 64


def test_ledger_lives_outside_the_world_repo(world, fake_drive, tmp_path, monkeypatch):
    monkeypatch.setenv("AIYE_HOME", str(tmp_path / "aiye"))
    d = fs.default_ledger_dir()
    assert d == Path(tmp_path / "aiye" / "drivefs_bridge")
    assert str(world.root) not in str(d)


def test_summary_states_the_local_vs_cloud_distinction_in_words(world, fake_drive, ledger_dir):
    _export(world)
    fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir, process_probe=_up)
    text = (ledger_dir / fs.SUMMARY_NAME).read_text(encoding="utf-8")
    assert "PROVIDER_BYTE_VERIFIED (states) | 0" in text
    assert "not evidence the bytes" in text


def test_deterministic_name_is_stable_and_parseable():
    n1 = fs.deterministic_name("entity.service.proteus", "a" * 64, "b" * 64)
    n2 = fs.deterministic_name("entity.service.proteus", "a" * 64, "b" * 64)
    assert n1 == n2
    m = fs.NAME_RE.match(n1)
    assert m and m.group("c") == "a" * 16 and m.group("b") == "b" * 16


def test_dry_run_writes_nothing_anywhere(world, fake_drive, ledger_dir):
    _export(world)
    before = sorted(p.name for p in fake_drive.target_dir.iterdir())
    s = fs.run_stage(target=fake_drive, store=world, ledger_dir=ledger_dir,
                     process_probe=_up, dry_run=True)
    assert s["status"] == "DRY_RUN"
    assert sorted(p.name for p in fake_drive.target_dir.iterdir()) == before
    assert fs.read_ledger(ledger_dir) == []
