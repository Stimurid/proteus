"""Tests for Proteus Codex project activation (foreign-carrier morphology)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.activate_codex import activate, inspect_target, remove_activation  # noqa: E402
from proteus.world.api import resolve_entity, route_observation  # noqa: E402
from proteus.world.store import WorldStore, ensure_world_home  # noqa: E402


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _env_isolated(td: Path) -> None:
    os.environ["PROTEUS_HOME"] = str(td / "ph")
    os.environ["PROTEUS_CURSOR_USER_DIR"] = str(td / "cu")
    os.environ["PROTEUS_SOURCE_ROOT"] = str(ROOT)
    os.environ["AIYE_HOME"] = str(td / "aiye")


def test_codex_empty_activate() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "codex_proj"
        target.mkdir()
        dry = activate(target, dry_run=True, run_id="TEST-CODEX", aiye_home=home / "aiye")
        assert_true(dry["mode"] == "dry_run", "dry mode")
        assert_true(dry["host"] == "codex", "host codex")
        assert_true(dry["policy"]["cursor_hooks_rules"] == "not_installed", "no cursor clone")
        assert_true(not (target / ".proteus").exists(), "dry-run writes nothing")

        result = activate(target, dry_run=False, run_id="TEST-CODEX", aiye_home=home / "aiye")
        assert_true(result["mode"] == "activate", "activated")
        assert_true((target / ".proteus" / "activation.json").is_file(), "manifest")
        assert_true((target / ".proteus" / "ENTRY.md").is_file(), "entry")
        assert_true((target / ".proteus" / "world_env.cmd").is_file(), "world env")
        assert_true((target / "AGENTS.md").is_file(), "agents")
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        assert_true("BUILDER-01" in agents and "not" in agents.lower(), "rejects BUILDER-01 role")
        assert_true("Codex" in agents, "codex host named")
        assert_true("python -m proteus world resolve" in agents, "world cli")
        assert_true("{{" not in agents, "placeholders rendered")
        assert_true(not (target / ".cursor").exists(), "no .cursor tree")
        man = json.loads((target / ".proteus" / "activation.json").read_text(encoding="utf-8"))
        assert_true(man["host"] == "codex", "manifest host")
        assert_true(man["morphology"]["cursor_hooks"] is False, "no hooks claim")
        env_cmd = (target / ".proteus" / "world_env.cmd").read_text(encoding="utf-8")
        expected = str((home / "aiye").resolve())
        assert_true(
            expected in env_cmd or expected.replace("\\", "/") in env_cmd.replace("\\", "/"),
            f"aiye in env; expected={expected!r} env={env_cmd!r}",
        )


def test_codex_existing_agents_preserved() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "with_agents"
        target.mkdir()
        original = "# Foreign Codex Agents\nMARKER_FOREIGN_CODEX\n"
        (target / "AGENTS.md").write_text(original, encoding="utf-8")
        result = activate(target, dry_run=False, run_id="TEST-CODEX", aiye_home=home / "aiye")
        assert_true((target / "AGENTS.md").read_text(encoding="utf-8") == original, "AGENTS preserved")
        assert_true("AGENTS.md" in result["preserved_paths"], "noted preserved")
        assert_true((target / ".proteus" / "ENTRY.md").is_file(), "entry still installed")
        man = json.loads((target / ".proteus" / "activation.json").read_text(encoding="utf-8"))
        assert_true("AGENTS.md" not in man["owned_paths"], "does not own foreign AGENTS")


def test_codex_world_api_alias_and_scopes() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        ensure_world_home()
        store = WorldStore()
        eid = f"entity.fixture.codex.{home.name}"
        store.create_entity(
            "Fixture Router",
            entity_id=eid,
            aliases=[f"our fixture router {home.name}", f"наш фикстурный роутер {home.name}"],
        )
        resolved = resolve_entity(f"our fixture router {home.name}", world=store)
        assert_true(resolved["entity_id"] == eid, "alias resolve")
        proj_path = home / "proj"
        proj_path.mkdir()
        ent = route_observation(
            scope="ENTITY",
            text="Codex morphology test entity observation",
            observer="test_codex",
            entity_query=eid,
            project=str(proj_path),
            world=store,
        )
        assert_true(ent.get("scope") == "ENTITY", f"entity route {ent}")
        proj = route_observation(
            scope="PROJECT",
            text="Codex-only project note NEGATIVE_CONTROL_MARKER_XYZ",
            observer="test_codex",
            project=str(proj_path),
            world=store,
        )
        assert_true(proj.get("scope") == "PROJECT", f"project route {proj}")
        # Project note must not appear as entity claim text
        claims_text = " ".join(c.get("text", "") for c in store.resolve(eid)["claims"])
        assert_true("NEGATIVE_CONTROL_MARKER_XYZ" not in claims_text, "project note not entity truth")


def test_codex_uninstall() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "rm_proj"
        target.mkdir()
        activate(target, dry_run=False, run_id="TEST-CODEX", aiye_home=home / "aiye")
        assert_true((target / ".proteus" / "activation.json").is_file(), "before remove")
        remove_activation(target, dry_run=False)
        assert_true(not (target / ".proteus" / "activation.json").exists(), "manifest gone")
        assert_true(not (target / "AGENTS.md").exists(), "owned agents removed")


def test_codex_refuse_cursor_manifest() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "cursorish"
        target.mkdir()
        (target / ".proteus").mkdir()
        (target / ".proteus" / "activation.json").write_text(
            json.dumps({"host": "cursor", "activation_id": "x", "owned_paths": []}),
            encoding="utf-8",
        )
        try:
            activate(target, dry_run=False, aiye_home=home / "aiye")
            raise AssertionError("should refuse cursor host")
        except RuntimeError as exc:
            assert_true("not Codex" in str(exc) or "cursor" in str(exc).lower(), str(exc))


def main() -> None:
    test_codex_empty_activate()
    test_codex_existing_agents_preserved()
    test_codex_world_api_alias_and_scopes()
    test_codex_uninstall()
    test_codex_refuse_cursor_manifest()
    print("test_activate_codex: PASS")


if __name__ == "__main__":
    main()
