"""Tests for compact, source-grounded project handoff capsules."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.capsule import build_capsule  # noqa: E402


def run(project: Path, *args: str) -> None:
    subprocess.run(args, cwd=project, check=True, capture_output=True, text=True)


def test_capsule_contains_handoff_essentials_and_redacts() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        project = root / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# Rules\nRead docs/law.md first.\n", encoding="utf-8")
        (project / "README.md").write_text("# Example\nA practical application.\n", encoding="utf-8")
        (project / "PROJECT_INTENT_AND_CURRENT_STATE.md").write_text(
            "# Current\nThe active focus is migration safety.\nAPI_KEY=should_not_escape\n",
            encoding="utf-8",
        )
        (project / "ROADMAP_NEXT_STEPS.md").write_text(
            "# Next\nRun the targeted migration smoke before a broad suite.\n",
            encoding="utf-8",
        )
        (project / "package.json").write_text('{"name":"example"}\n', encoding="utf-8")
        (project / "changed.py").write_text("before\n", encoding="utf-8")
        run(project, "git", "init")
        run(project, "git", "config", "user.email", "test@example.invalid")
        run(project, "git", "config", "user.name", "Capsule Test")
        run(project, "git", "add", ".")
        run(project, "git", "commit", "-m", "initial")
        (project / "changed.py").write_text("after\n", encoding="utf-8")
        (project / "untracked.txt").write_text("local work\n", encoding="utf-8")

        out = root / "capsule.md"
        result = build_capsule(project, out, max_chars=12_000)
        text = out.read_text(encoding="utf-8")
        assert result.output == out.resolve()
        assert result.chars == len(text)
        assert "Read docs/law.md first" in text
        assert "active focus is migration safety" in text
        assert "targeted migration smoke" in text
        assert "Working tree: dirty (2 status entries; untracked directories summarized)" in text
        assert "Changed-path triage: 2 non-cache-shaped paths" in text
        assert "changed.py" in text and "untracked.txt" in text
        assert "should_not_escape" not in text
        assert "<REDACTED>" in text
        assert "What to inspect before changing code" in text


def test_capsule_respects_global_bound_and_does_not_mutate_project() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        project = root / "project"
        project.mkdir()
        original = "# Readme\n" + ("useful context\n" * 2_000)
        (project / "README.md").write_text(original, encoding="utf-8")
        out = root / "capsule.md"
        result = build_capsule(project, out, max_chars=4_500)
        assert result.chars <= 4_500
        assert (project / "README.md").read_text(encoding="utf-8") == original
        assert "Generated context, not a source of truth" in out.read_text(encoding="utf-8")


def test_capsule_summarizes_cache_shaped_dirty_paths() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        project = root / "project"
        cache = project / "SAS" / ".edge-render-x" / "Default" / "Cache"
        cache.mkdir(parents=True)
        (project / "README.md").write_text("# Example\n", encoding="utf-8")
        (project / "useful.txt").write_text("keep me\n", encoding="utf-8")
        cache_file = cache / "blob"
        cache_file.write_text("generated\n", encoding="utf-8")
        run(project, "git", "init")
        run(project, "git", "config", "user.email", "test@example.invalid")
        run(project, "git", "config", "user.name", "Capsule Test")
        run(project, "git", "add", ".")
        run(project, "git", "commit", "-m", "initial")
        (project / "useful.txt").write_text("changed\n", encoding="utf-8")
        cache_file.write_text("changed cache\n", encoding="utf-8")
        out = root / "capsule.md"
        build_capsule(project, out)
        text = out.read_text(encoding="utf-8")
        assert "1 non-cache-shaped paths; 1 browser/cache-shaped paths" in text
        assert "useful.txt" in text
        assert "Browser/cache-shaped paths are summarized" in text



def test_capsule_preserves_mounted_frontier_and_redacts_mcp_values() -> None:
    """Proteus mount + state, with names-only MCP inventory and no secrets."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        project = root / "hydra"
        (project / ".proteus").mkdir(parents=True)
        (project / "state").mkdir()
        (project / "docs").mkdir()
        (project / ".proteus" / "ENTRY.md").write_text(
            "Actual Cursor project mount entry; resolve Proteus locally.\n",
            encoding="utf-8",
        )
        (project / "state" / "CURRENT.md").write_text(
            "Current workline: HYDRA continuity check.\n", encoding="utf-8"
        )
        (project / "state" / "FRONTIER.md").write_text(
            "Next: verify B receives current project state.\n", encoding="utf-8"
        )
        (project / "state" / "UNRESOLVED.md").write_text(
            "Unresolved: B did not prove full read.\n", encoding="utf-8"
        )
        (project / "docs" / "CURRENT.md").write_text(
            "Project-local operational snapshot.\n", encoding="utf-8"
        )
        (project / ".mcp.json").write_text(
            json.dumps({"mcpServers": {
                "proteus": {"command": "DO_NOT_DISCLOSE_THIS_COMMAND",
                            "env": {"TOKEN": "MCP_SECRET_CANARY"}},
                "aiye-executor": {"url": "https://private.invalid/secret-path"}
            }}),
            encoding="utf-8",
        )
        result = build_capsule(project, root / "capsule.md", max_chars=16_000)
        body = result.output.read_text(encoding="utf-8")
        assert "Actual Cursor project mount entry" in body
        assert "Current workline: HYDRA continuity check" in body
        assert "Next: verify B receives current project state" in body
        assert "Unresolved: B did not prove full read" in body
        assert "Project-local operational snapshot" in body
        assert "`proteus`" in body and "`aiye-executor`" in body
        assert "configuration only; runtime unverified" in body
        assert "MCP_SECRET_CANARY" not in body
        assert "DO_NOT_DISCLOSE_THIS_COMMAND" not in body
        assert "private.invalid" not in body
        assert "state/FRONTIER.md" in result.included_documents
        assert ".proteus/ENTRY.md" in result.included_documents


def test_capsule_explicitly_marks_host_mcp_unknown() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        project = root / "project"
        project.mkdir()
        (project / "README.md").write_text("# Project\n", encoding="utf-8")
        out = root / "capsule.md"
        build_capsule(project, out)
        body = out.read_text(encoding="utf-8")
        assert "host-level tools and current availability remain UNKNOWN" in body


def main() -> None:
    test_capsule_contains_handoff_essentials_and_redacts()
    test_capsule_respects_global_bound_and_does_not_mutate_project()
    test_capsule_summarizes_cache_shaped_dirty_paths()
    test_capsule_preserves_mounted_frontier_and_redacts_mcp_values()
    test_capsule_explicitly_marks_host_mcp_unknown()
    print("test_capsule: PASS")


if __name__ == "__main__":
    main()
