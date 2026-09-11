"""Tests for compact, source-grounded project handoff capsules."""

from __future__ import annotations

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


def main() -> None:
    test_capsule_contains_handoff_essentials_and_redacts()
    test_capsule_respects_global_bound_and_does_not_mutate_project()
    test_capsule_summarizes_cache_shaped_dirty_paths()
    print("test_capsule: PASS")


if __name__ == "__main__":
    main()
