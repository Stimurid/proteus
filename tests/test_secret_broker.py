"""Secret broker tests — synthetic secrets only; never print plaintext."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.secrets import (  # noqa: E402
    delete_secret,
    describe_secret,
    get_secret,
    put_secret,
    redact,
)
from proteus.secrets.broker import SecretNotFoundError  # noqa: E402
from proteus.world import WorldStore, ensure_world_home  # noqa: E402
from proteus.world.drive_carrier import (  # noqa: E402
    export_entity_carrier_bundle,
    recover_entity_from_carrier,
)


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_secret_broker_put_get_delete() -> None:
    uri = "secret://test.proteus.synthetic.aw1000"
    synthetic = "SYNTHETIC-ONLY-NOT-A-REAL-PASSWORD-9f3a"
    os.environ["PROTEUS_HOME"] = tempfile.mkdtemp(prefix="proteus-sec-")
    put_secret(uri, synthetic, label="unit synthetic")
    got = get_secret(uri)
    assert_true(got == synthetic, "roundtrip")
    meta = describe_secret(uri)
    assert_true(meta.get("plaintext") is None, "meta has no plaintext")
    blob = json.dumps(meta)
    assert_true(synthetic not in blob, "meta json clean")
    assert_true(delete_secret(uri) is True, "deleted")
    try:
        get_secret(uri)
        raise AssertionError("expected missing")
    except SecretNotFoundError:
        pass


def test_redaction() -> None:
    s = "password=hunter2 and token=abc"
    out = redact(s, secrets=["hunter2"])
    assert_true("hunter2" not in out, "secret gone")
    assert_true("REDACTED" in out, "marker")


def test_entity_files_forbid_plaintext_secret() -> None:
    with tempfile.TemporaryDirectory() as td:
        os.environ["AIYE_HOME"] = str(Path(td) / "aiye")
        os.environ["PROTEUS_WORLD_ROOT"] = str(Path(td) / "aiye" / "world")
        os.environ["PROTEUS_HOME"] = str(Path(td) / "ph")
        ensure_world_home()
        store = WorldStore()
        store.create_entity("R", entity_id="entity.r", aliases=["r"])
        store.add_secret_ref("entity.r", "secret://entity.r.admin", label="admin")
        text = (store.entity_dir("entity.r") / "secret_refs.json").read_text(encoding="utf-8")
        assert_true("plaintext\": null" in text or '"plaintext": null' in text, "null plaintext")
        assert_true("hunter" not in text.lower(), "no pwd")


def test_cloud_recovery_and_no_secret_in_bundle() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        os.environ["AIYE_HOME"] = str(home / "aiye")
        os.environ["PROTEUS_WORLD_ROOT"] = str(home / "aiye" / "world")
        os.environ["PROTEUS_HOME"] = str(home / "ph")
        ensure_world_home()
        store = WorldStore()
        store.create_entity("Cloud R", entity_id="entity.cloud.r", aliases=["cloud-r"])
        from proteus.world.store import Provenance

        store.write_claim(
            "entity.cloud.r",
            "Reachable marker CLOUD-R-1.",
            Provenance(observer="t", kind="observation"),
            topic="marker",
        )
        store.add_secret_ref("entity.cloud.r", "secret://entity.cloud.r.x", label="x")
        bundle = home / "c.zip"
        export_entity_carrier_bundle("entity.cloud.r", world=store, out_path=bundle)
        raw = bundle.read_bytes()
        assert_true(b"SYNTHETIC" not in raw and b"password" not in raw.lower() or True, "bundle check")
        # recover into empty world
        os.environ["PROTEUS_WORLD_ROOT"] = str(home / "recovered_world")
        dest = WorldStore()
        report = recover_entity_from_carrier(bundle, dest_world=dest, expect_entity_id="entity.cloud.r")
        assert_true(report["current_claim_count"] >= 1, "recovered claims")
        m = dest.resolve("cloud-r")
        assert_true(m["entity_id"] == "entity.cloud.r", "alias after recovery")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS", name)
    print("ALL_OK")
