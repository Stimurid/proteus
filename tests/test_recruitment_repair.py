"""Tests for recruitment repair: constitutive install + derived relation recorder."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.activate import activate as activate_cursor  # noqa: E402
from proteus.activate_codex import activate as activate_codex  # noqa: E402
from proteus.derived import read_relation, record_relation  # noqa: E402


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


MARKER = "Consequential derived representations"


def test_anti_reduction_template_has_principle() -> None:
    text = (ROOT / "hosts" / "cursor" / "templates" / "rules" / "proteus-anti-reduction.mdc").read_text(
        encoding="utf-8"
    )
    assert_true(MARKER in text, "anti-reduction principle")
    assert_true("not a per-task audit checklist" in text or "not a per-task checklist" in text, "not checklist")
    assert_true("derived record" in text, "optional recorder mentioned")


def test_codex_and_cursor_activate_install_constitutive() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        os.environ["PROTEUS_SOURCE_ROOT"] = str(ROOT)
        os.environ["PROTEUS_HOME"] = str(home / "ph")
        os.environ["PROTEUS_CURSOR_USER_DIR"] = str(home / "cu")
        os.environ["AIYE_HOME"] = str(home / "aiye")

        cursor_proj = home / "cursor_proj"
        cursor_proj.mkdir()
        activate_cursor(cursor_proj, dry_run=False, run_id="TEST-D011")
        anti = (cursor_proj / ".cursor" / "rules" / "proteus-anti-reduction.mdc").read_text(encoding="utf-8")
        assert_true(MARKER in anti, "cursor anti-reduction installed")
        const = (cursor_proj / ".proteus" / "CONSTITUTIVE.md").read_text(encoding="utf-8")
        assert_true(MARKER in const, "cursor constitutive")
        entry = (cursor_proj / ".proteus" / "ENTRY.md").read_text(encoding="utf-8")
        assert_true("CONSTITUTIVE.md" in entry, "cursor entry points constitutive")

        codex_proj = home / "codex_proj"
        codex_proj.mkdir()
        # Pre-existing AGENTS must be preserved; constitutive still installed.
        (codex_proj / "AGENTS.md").write_text("# Foreign\nMARKER\n", encoding="utf-8")
        activate_codex(codex_proj, dry_run=False, run_id="TEST-D011", aiye_home=home / "aiye")
        assert_true((codex_proj / "AGENTS.md").read_text(encoding="utf-8").startswith("# Foreign"), "agents preserved")
        cconst = (codex_proj / ".proteus" / "CONSTITUTIVE.md").read_text(encoding="utf-8")
        assert_true(MARKER in cconst, "codex constitutive")
        centry = (codex_proj / ".proteus" / "ENTRY.md").read_text(encoding="utf-8")
        assert_true("CONSTITUTIVE.md" in centry, "codex entry points constitutive")


def test_derived_relation_recorder() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        src = home / "design.md"
        derived = home / "model.json"
        src.write_text("# design\nambiguous X vs Y\n", encoding="utf-8")
        derived.write_text('{"x": true}\n', encoding="utf-8")
        receipt = record_relation(
            derived=derived,
            sources=[src],
            note="test projection",
            observer="test",
            project=home,
        )
        assert_true(Path(receipt["relation_path"]).is_file(), "relation file")
        loaded = read_relation(derived)
        assert_true(loaded is not None and loaded["schema"].startswith("proteus.derived_relation"), "load")
        assert_true(str(src.resolve()) in loaded["sources"], "source listed")
        assert_true("derived is not identical to source" in loaded["claims"][0], "non-identity claim")


def main() -> None:
    test_anti_reduction_template_has_principle()
    test_codex_and_cursor_activate_install_constitutive()
    test_derived_relation_recorder()
    print("test_recruitment_repair: PASS")


if __name__ == "__main__":
    main()
