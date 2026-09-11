"""World / entity memory vertical-slice tests."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.activate import activate  # noqa: E402
from proteus.world import (  # noqa: E402
    MemoryScope,
    WorldStore,
    classify_and_route,
    export_entity_carrier_bundle,
    import_entity_carrier_bundle,
    rebuild_index,
)
from proteus.world.store import (  # noqa: E402
    EntityAmbiguousError,
    EntityNotFoundError,
    Provenance,
    ensure_world_home,
)


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _iso(td: Path) -> WorldStore:
    os.environ["AIYE_HOME"] = str(td / "aiye")
    os.environ["PROTEUS_WORLD_ROOT"] = str(td / "aiye" / "world")
    os.environ["PROTEUS_HOME"] = str(td / "ph")
    os.environ["PROTEUS_SOURCE_ROOT"] = str(ROOT)
    ensure_world_home()
    return WorldStore()


def test_stable_identity_and_alias() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        ident = store.create_entity(
            "Fixture Router",
            entity_id="entity.router.fixture",
            aliases=["our router", "fixture-aw"],
        )
        assert_true(ident["entity_id"] == "entity.router.fixture", "id")
        m1 = store.resolve("entity.router.fixture")
        m2 = store.resolve("our router")
        m3 = store.resolve("Fixture Router")
        assert_true(m1["entity_id"] == m2["entity_id"] == m3["entity_id"], "alias same id")


def test_ambiguous_resolution() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        store.create_entity("Alpha Device", entity_id="entity.alpha", aliases=["shared-alias"])
        store.create_entity("Beta Device", entity_id="entity.beta", aliases=["shared-alias"])
        try:
            store.resolve("shared-alias")
            raise AssertionError("expected ambiguous")
        except EntityAmbiguousError as e:
            assert_true(len(e.candidates) == 2, "two candidates")


def test_two_projects_one_shared_fact() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        store = _iso(home)
        store.create_entity("Shared Widget", entity_id="entity.widget", aliases=["widget"])
        pa = home / "PROJECT_A"
        pb = home / "PROJECT_B"
        pa.mkdir()
        pb.mkdir()
        prov = Provenance(observer="test-a", project=str(pa), kind="observation", source="unit")
        classify_and_route(
            scope=MemoryScope.ENTITY,
            text="Widget firmware build is W-100.",
            provenance=prov,
            entity_id="entity.widget",
            topic="firmware_build",
            project_path=str(pa),
            world=store,
        )
        # project-only decision in A
        classify_and_route(
            scope=MemoryScope.PROJECT,
            text="PROJECT_A will not ship widget UI this sprint.",
            provenance=Provenance(observer="test-a", project=str(pa), kind="decision"),
            project_path=str(pa),
            topic="ship_ui",
            world=store,
        )
        store.link_project("entity.widget", str(pb), relation="reads")
        mounted = store.resolve("widget")
        texts = [c["text"] for c in mounted["current_claims"]]
        assert_true(any("W-100" in t for t in texts), "entity fact present")
        # project decision must not be in entity claims
        assert_true(not any("ship widget UI" in t for t in texts), "project decision not leaked")
        # B can resolve without local copy
        assert_true(not (pb / "ENTITY.md").exists(), "B has no copied entity file")
        assert_true(store.resolve("widget")["entity_id"] == "entity.widget", "B resolve")


def test_conflict_no_last_write_wins() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        store.create_entity("Conflict Box", entity_id="entity.box")
        p = Provenance(observer="t", kind="observation")
        c1 = store.write_claim("entity.box", "Color is blue.", p, topic="color", status="current")
        c2 = store.write_claim("entity.box", "Color is red.", p, topic="color", status="current")
        assert_true(c2["status"] == "conflict", "new is conflict")
        claims = store.list_claims("entity.box")
        by_id = {c["claim_id"]: c for c in claims}
        assert_true(by_id[c1["claim_id"]]["status"] == "conflict", "old also conflict")
        assert_true(c1["text"] != c2["text"], "both texts survive")
        unresolved = (store.entity_dir("entity.box") / "unresolved.md").read_text(encoding="utf-8")
        assert_true("CONFLICT" in unresolved, "conflict logged")


def test_unknown_retention() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        store.create_entity("Mystery", entity_id="entity.mystery")
        store.write_claim(
            "entity.mystery",
            "Owner of port 8443 is UNKNOWN.",
            Provenance(observer="t", kind="observation"),
            topic="port_8443",
            status="unknown",
        )
        m = store.mount("entity.mystery")
        assert_true(len(m["unknowns"]) == 1, "unknown claim")
        assert_true("UNKNOWN" in m["unresolved_md"], "unresolved md")


def test_secret_ref_no_plaintext() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        store.create_entity("Sec Device", entity_id="entity.sec")
        ref = store.add_secret_ref(
            "entity.sec",
            "secret://entity.sec.admin",
            label="admin credential",
            auth_method="keychain",
        )
        assert_true(ref["plaintext"] is None, "no plaintext")
        blob = json.dumps(store.mount("entity.sec"))
        assert_true("password" not in blob.lower() or "password" in "secret reference", "no pwd")
        assert_true("secret://entity.sec.admin" in blob, "uri present")


def test_index_rebuildable() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        store.create_entity("Idx One", entity_id="entity.idx1", aliases=["one"])
        idx = rebuild_index(world=store)
        assert_true("by_alias" in idx, "alias map")
        (store.index_dir / "by_alias.json").unlink()
        idx2 = rebuild_index(world=store)
        assert_true(idx2["by_alias"]["one"] == "entity.idx1", "rebuilt")


def test_carrier_export_import_no_lww() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        store = _iso(home)
        store.create_entity("Clouded", entity_id="entity.cloud")
        store.write_claim(
            "entity.cloud",
            "Local fact L1.",
            Provenance(observer="local", kind="observation"),
            topic="l1",
        )
        bundle = home / "carrier.zip"
        meta = export_entity_carrier_bundle("entity.cloud", world=store, out_path=bundle)
        meta.pop("payload", None)
        # mutate local after export
        store.write_claim(
            "entity.cloud",
            "Local-only after export.",
            Provenance(observer="local", kind="observation"),
            topic="l2",
        )
        report = import_entity_carrier_bundle(bundle, world=store, expect_entity_id="entity.cloud")
        assert_true(report["no_last_write_wins"] is True, "flag")
        assert_true("Local-only after export." in [c["text"] for c in store.list_claims("entity.cloud")], "local kept")
        assert_true(len(report["only_local"]) >= 1, "only_local detected")


def test_activation_includes_world_skill() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        os.environ["PROTEUS_HOME"] = str(home / "ph")
        os.environ["PROTEUS_CURSOR_USER_DIR"] = str(home / "cu")
        os.environ["PROTEUS_SOURCE_ROOT"] = str(ROOT)
        os.environ["AIYE_HOME"] = str(home / "aiye")
        target = home / "proj"
        target.mkdir()
        activate(target, dry_run=False, run_id="TEST-WORLD")
        skill = target / ".cursor" / "skills" / "proteus-world" / "SKILL.md"
        assert_true(skill.is_file(), "world skill installed")
        entry = (target / ".proteus" / "ENTRY.md").read_text(encoding="utf-8")
        assert_true("world resolve" in entry, "entry mentions world")


def test_idempotent_write_reread() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        store.create_entity("Idem", entity_id="entity.idem")
        p = Provenance(observer="t", kind="observation")
        c1 = store.write_claim("entity.idem", "Same fact.", p, topic="t1", status="current")
        c2 = store.write_claim("entity.idem", "Same fact.", p, topic="t1", status="current")
        assert_true(c1["claim_id"] == c2["claim_id"], "same claim returned")
        assert_true(c2.get("idempotent_reread") is True, "flag")
        assert_true(len(store.list_claims("entity.idem")) == 1, "single row")


def test_aw1000_alias_and_api() -> None:
    """Lightweight regression using episode world if present; else skip-like create."""
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        store.create_entity(
            "Arcadian AW1000 router",
            entity_id="entity.router.aw1000.home",
            aliases=["AW1000", "наш роутер", "Arcadyan AW1000"],
        )
        assert_true(store.resolve("наш роутер")["entity_id"] == "entity.router.aw1000.home", "cyrillic")
        assert_true(store.resolve("AW1000")["entity_id"] == "entity.router.aw1000.home", "aw")
        from proteus.world.api import retrieve_facts, CONTRACT

        facts = retrieve_facts("AW1000", world=store)
        assert_true(facts["entity_id"] == "entity.router.aw1000.home", "api")
        assert_true("resolve_entity" in CONTRACT["operations"], "contract")


def test_missing_entity() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = _iso(Path(td))
        try:
            store.resolve("no-such-entity")
            raise AssertionError("expected missing")
        except EntityNotFoundError:
            pass


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS", name)
    print("ALL_OK")
