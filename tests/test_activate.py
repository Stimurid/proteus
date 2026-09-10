"""Fixture campaign for Proteus Cursor project activation (mount)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.activate import activate, inspect_target, remove_activation  # noqa: E402


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _env_isolated(td: Path) -> None:
    os.environ["PROTEUS_HOME"] = str(td / "ph")
    os.environ["PROTEUS_CURSOR_USER_DIR"] = str(td / "cu")
    os.environ["PROTEUS_SOURCE_ROOT"] = str(ROOT)


def _tree_files(root: Path) -> set[str]:
    out: set[str] = set()
    for p in root.rglob("*"):
        if p.is_file():
            out.add(p.relative_to(root).as_posix())
    return out


def test_empty_target_activate() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "empty_proj"
        target.mkdir()
        dry = activate(target, dry_run=True, run_id="TEST-ACT")
        assert_true(dry["mode"] == "dry_run", "dry mode")
        assert_true(any(a["action"] == "would_create" for a in dry["actions"]), "would create")
        assert_true(not (target / ".proteus").exists(), "dry-run writes nothing")

        result = activate(target, dry_run=False, run_id="TEST-ACT")
        assert_true(result["mode"] == "activate", "activated")
        assert_true((target / ".proteus" / "activation.json").is_file(), "manifest")
        assert_true((target / ".proteus" / "ENTRY.md").is_file(), "entry")
        assert_true((target / "AGENTS.md").is_file(), "agents created")
        assert_true((target / "state" / "IDENTITY.md").is_file(), "state identity")
        assert_true((target / ".cursor" / "rules" / "proteus-orientation.mdc").is_file(), "rule")
        assert_true((target / ".cursor" / "hooks" / "proteus_hook.cmd").is_file(), "hook cmd")
        assert_true((target / ".cursor" / "hooks.json").is_file(), "hooks json")
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        assert_true("BUILDER-01" not in agents or "not automatically BUILDER-01" in agents or "project mount" in agents.lower() or "Proteus project mount" in agents, "mount-oriented agents")
        assert_true("{{" not in agents, "placeholders rendered")
        entry = (target / ".proteus" / "ENTRY.md").read_text(encoding="utf-8")
        assert_true("Open this folder" in entry or "Open / continue" in entry, "entry instructions")
        man = json.loads((target / ".proteus" / "activation.json").read_text(encoding="utf-8"))
        assert_true("AGENTS.md" in man["owned_paths"], "owns created AGENTS")
        assert_true("Gate 1" in man["not_claimed"][0] or any("Gate 1" in x for x in man["not_claimed"]), "no Gate 1 claim")


def test_existing_agents_preserved() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "with_agents"
        target.mkdir()
        original = "# My Project Agents\n\nDo not clobber me.\nMARKER_FOREIGN_AGENTS\n"
        (target / "AGENTS.md").write_text(original, encoding="utf-8")
        result = activate(target, dry_run=False, run_id="TEST-ACT")
        assert_true((target / "AGENTS.md").read_text(encoding="utf-8") == original, "AGENTS preserved")
        assert_true("AGENTS.md" in result["preserved_paths"], "noted preserved")
        man = json.loads((target / ".proteus" / "activation.json").read_text(encoding="utf-8"))
        assert_true("AGENTS.md" not in man["owned_paths"], "does not own foreign AGENTS")
        assert_true((target / ".cursor" / "rules" / "proteus-orientation.mdc").is_file(), "rules still installed")


def test_existing_cursor_rules_preserved() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "with_rules"
        target.mkdir()
        rules = target / ".cursor" / "rules"
        rules.mkdir(parents=True)
        foreign = rules / "my-project.mdc"
        foreign.write_text("# foreign rule\nMARKER_FOREIGN_RULE\n", encoding="utf-8")
        (target / ".cursor" / "hooks.json").write_text(
            json.dumps({"version": 1, "hooks": {"stop": [{"command": "echo foreign", "timeout": 5}]}}),
            encoding="utf-8",
        )
        activate(target, dry_run=False, run_id="TEST-ACT")
        assert_true(foreign.read_text(encoding="utf-8").startswith("# foreign rule"), "foreign rule kept")
        hooks = json.loads((target / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
        stop = hooks["hooks"]["stop"]
        assert_true(any("echo foreign" in str(h) for h in stop), "foreign stop hook kept")
        assert_true(any("proteus_hook" in str(h) for h in stop), "proteus stop merged")
        assert_true((rules / "proteus-orientation.mdc").is_file(), "proteus rule added")
        assert_true(not (rules / "proteus-orientation.mdc").read_text(encoding="utf-8").startswith("# foreign"), "did not overwrite foreign")


def test_rerun_idempotent() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "rerun"
        target.mkdir()
        first = activate(target, dry_run=False, run_id="TEST-ACT")
        man1 = json.loads((target / ".proteus" / "activation.json").read_text(encoding="utf-8"))
        agents1 = (target / "AGENTS.md").read_text(encoding="utf-8")
        (target / "AGENTS.md").write_text(agents1 + "\nLOCAL_EDIT\n", encoding="utf-8")
        second = activate(target, dry_run=False, run_id="TEST-ACT")
        man2 = json.loads((target / ".proteus" / "activation.json").read_text(encoding="utf-8"))
        assert_true(man1["activation_id"] == man2["activation_id"], "stable activation id")
        assert_true("LOCAL_EDIT" in (target / "AGENTS.md").read_text(encoding="utf-8"), "does not clobber post-activate AGENTS edit")
        assert_true((target / ".cursor" / "rules" / "proteus-orientation.mdc").is_file(), "rules refreshed/kept")
        assert_true(any(a["action"] == "skip_exists" for a in second["actions"]), "skips preserved")
        assert_true(first["activation_id"] == second["activation_id"], "same id returned")


def test_remove_after_activation() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "remove_me"
        target.mkdir()
        (target / "README.md").write_text("keep me\n", encoding="utf-8")
        foreign_agents = "# foreign\nKEEP_AGENTS\n"
        (target / "AGENTS.md").write_text(foreign_agents, encoding="utf-8")
        rules = target / ".cursor" / "rules"
        rules.mkdir(parents=True)
        (rules / "other.mdc").write_text("other\n", encoding="utf-8")
        (target / ".cursor" / "hooks.json").write_text(
            json.dumps({"version": 1, "hooks": {"stop": [{"command": "echo foreign"}]}}),
            encoding="utf-8",
        )
        activate(target, dry_run=False, run_id="TEST-ACT")
        assert_true((target / ".proteus" / "activation.json").is_file(), "activated")
        dry_rm = remove_activation(target, dry_run=True)
        assert_true(dry_rm["mode"] == "dry_run_remove", "dry remove")
        assert_true((target / ".proteus" / "activation.json").is_file(), "dry remove keeps files")

        remove_activation(target, dry_run=False)
        assert_true(not (target / ".proteus" / "activation.json").exists(), "manifest gone")
        assert_true(not (target / ".cursor" / "rules" / "proteus-orientation.mdc").exists(), "proteus rule gone")
        assert_true((rules / "other.mdc").is_file(), "foreign rule remains")
        assert_true((target / "AGENTS.md").read_text(encoding="utf-8") == foreign_agents, "foreign AGENTS remains")
        assert_true((target / "README.md").read_text(encoding="utf-8") == "keep me\n", "unrelated remains")
        hooks = json.loads((target / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
        assert_true(any("echo foreign" in str(h) for h in hooks["hooks"]["stop"]), "foreign hook remains")
        assert_true(not any("proteus_hook" in str(h) for h in hooks["hooks"].get("stop", [])), "proteus hook stripped")


def test_remove_refuses_without_manifest() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "no_manifest"
        target.mkdir()
        (target / "AGENTS.md").write_text("x\n", encoding="utf-8")
        try:
            remove_activation(target, dry_run=False)
            raise AssertionError("expected FileNotFoundError")
        except FileNotFoundError:
            pass
        assert_true((target / "AGENTS.md").is_file(), "untouched")


def test_missing_target_fails_visibly() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        missing = home / "nope"
        try:
            activate(missing, dry_run=True)
            raise AssertionError("expected FileNotFoundError")
        except FileNotFoundError:
            pass


def test_inspect_reports_preexisting() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        target = home / "insp"
        target.mkdir()
        (target / "AGENTS.md").write_text("a\n", encoding="utf-8")
        report = inspect_target(target)
        assert_true(report.pre_existing["AGENTS.md"] is True, "sees AGENTS")
        assert_true(report.already_activated is False, "not activated")


def test_hooks_json_utf8_bom() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "bom_hooks"
        target.mkdir()
        hooks_dir = target / ".cursor"
        hooks_dir.mkdir(parents=True)
        payload = json.dumps({"version": 1, "hooks": {"stop": [{"command": "echo foreign"}]}})
        # Windows PowerShell Set-Content -Encoding utf8 writes BOM
        (hooks_dir / "hooks.json").write_bytes(b"\xef\xbb\xbf" + payload.encode("utf-8"))
        result = activate(target, dry_run=False, run_id="TEST-ACT")
        assert_true(result["mode"] == "activate", "activated despite BOM")
        assert_true((target / ".proteus" / "activation.json").is_file(), "manifest written")
        hooks = json.loads((hooks_dir / "hooks.json").read_text(encoding="utf-8"))
        assert_true(any("echo foreign" in str(h) for h in hooks["hooks"]["stop"]), "foreign kept")
        assert_true(any("proteus_hook" in str(h) for h in hooks["hooks"]["stop"]), "proteus merged")


def test_invalid_hooks_json_fails_before_writes() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        _env_isolated(home)
        target = home / "bad_hooks"
        target.mkdir()
        hooks_dir = target / ".cursor"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "hooks.json").write_text("{not-json", encoding="utf-8")
        try:
            activate(target, dry_run=False, run_id="TEST-ACT")
            raise AssertionError("expected RuntimeError")
        except RuntimeError as exc:
            assert_true("hooks.json" in str(exc), "mentions hooks")
        assert_true(not (target / ".proteus").exists(), "no partial .proteus")
        assert_true(not (target / "AGENTS.md").exists(), "no partial AGENTS")


def main() -> None:
    test_empty_target_activate()
    test_existing_agents_preserved()
    test_existing_cursor_rules_preserved()
    test_rerun_idempotent()
    test_remove_after_activation()
    test_remove_refuses_without_manifest()
    test_missing_target_fails_visibly()
    test_inspect_reports_preexisting()
    test_hooks_json_utf8_bom()
    test_invalid_hooks_json_fails_before_writes()
    print("PASS all activation fixture tests")


if __name__ == "__main__":
    main()
