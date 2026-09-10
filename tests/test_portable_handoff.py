from __future__ import annotations

import json
import os
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.handoff import (  # noqa: E402
    ARTIFACT_DIR_NAME,
    ARTIFACT_FILENAME,
    classify_payload_path,
    cleanroom,
    iter_payload_files,
    mentions_origin_workspace,
    operational_coupling_hits,
    origin_path_markers,
    origin_workspace_from_state,
    pack,
    verify_reconstructed,
)
from proteus.install_cursor import install  # noqa: E402
from proteus.paths import cursor_user_dir, proteus_home  # noqa: E402


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_origin_path_boundary_does_not_treat_fresh_sibling_as_origin() -> None:
    origin = r"C:\Projects\Proteus"
    fresh_agents = "Source root: `C:\\projects\\Proteus-FRESH-001\\Proteus`\n"
    fresh_hook = "set PYTHONPATH=C:\\projects\\Proteus-FRESH-001\\Proteus\\.proteus-runtime\\host\\cursor\\src\n"
    assert_true(not mentions_origin_workspace(fresh_agents, origin), "FRESH dest is not origin")
    assert_true(not mentions_origin_workspace(fresh_hook, origin), "FRESH hook is not origin")
    assert_true(mentions_origin_workspace(r"Workspace: `C:\Projects\Proteus`", origin), "exact origin still matches")
    assert_true(mentions_origin_workspace(r"set PYTHONPATH=C:\projects\Proteus\src", origin), "origin src still matches")


def test_payload_omits_generated_and_classifies_residue() -> None:
    rels = {p.relative_to(ROOT).as_posix() for p in iter_payload_files(ROOT)}
    assert_true("AGENTS.md" not in rels, "generated AGENTS.md must not be payload")
    assert_true("CLAUDE.md" not in rels, "generated CLAUDE.md must not be payload")
    assert_true("state/INCARNATION.md" not in rels, "generated INCARNATION.md must not be payload")
    assert_true(".cursor/hooks.json" not in rels, "generated project hooks.json must not be payload")
    assert_true(not any(r.startswith(".cursor/hooks/") for r in rels), "generated hook cmd must not be payload")
    assert_true("src/proteus/handoff.py" in rels, "packager is portable source")
    assert_true("hosts/cursor/templates/AGENTS.md" in rels, "templates are portable source")
    assert_true("state/UNRESOLVED.md" in rels, "unresolved is portable state")
    assert_true("state/DECISIONS.md" in rels, "decisions are portable state")
    assert_true(".cursor/commands/proteus-checkpoint.md" in rels, "command source travels")
    assert_true(classify_payload_path("DECISIONS.md") == "superseded_residue", "root decisions residue")
    assert_true(classify_payload_path("state/DECISIONS.md") == "portable_state", "canonical decisions")
    assert_true(classify_payload_path("src/proteus/hook.py") == "portable_source", "source class")
    hits = operational_coupling_hits(ROOT, origin_path_markers(origin_workspace_from_state(ROOT)))
    assert_true(hits == [], f"src/hosts must not hardcode origin workspace: {hits}")


def test_isolated_install_does_not_use_live_cursor_dir() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        project = home / "proj"
        (project / "src" / "proteus").mkdir(parents=True)
        shutil.copytree(ROOT / "src" / "proteus", project / "src" / "proteus", dirs_exist_ok=True)
        shutil.copytree(ROOT / "hosts", project / "hosts")
        (project / "state").mkdir()
        os.environ["PROTEUS_HOME"] = str(home / "ph")
        os.environ["PROTEUS_CURSOR_USER_DIR"] = str(home / "cu")
        os.environ["PROTEUS_SOURCE_ROOT"] = str(project)
        try:
            install(project, run_id="TEST-ISOLATED", backup_dir=home / "bak")
            assert_true((home / "cu" / "hooks.json").is_file(), "isolated hooks.json")
            assert_true(cursor_user_dir() == home / "cu", "cursor_user_dir honors env")
            assert_true(proteus_home() == home / "ph", "proteus_home honors env")
            assert_true("cu" in str(cursor_user_dir()), "not live user dir")
            text = (project / "AGENTS.md").read_text(encoding="utf-8")
            assert_true(str(project.resolve()) in text, "SOURCE_ROOT is project")
            for marker in origin_path_markers(origin_workspace_from_state(ROOT)):
                assert_true(marker.lower() not in text.lower() or marker.lower() == str(project.resolve()).lower(), "no origin bake-in")
        finally:
            os.environ.pop("PROTEUS_HOME", None)
            os.environ.pop("PROTEUS_CURSOR_USER_DIR", None)
            os.environ.pop("PROTEUS_SOURCE_ROOT", None)


def test_pack_zip_has_entrypoint_and_no_generated_payload() -> None:
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / ARTIFACT_FILENAME
        manifest = pack(ROOT, zip_path=zpath)
        assert_true(zpath.is_file(), "zip exists")
        assert_true(manifest["file_count"] > 20, "payload is non-empty")
        with zipfile.ZipFile(zpath) as zf:
            names = zf.namelist()
        assert_true(f"{ARTIFACT_DIR_NAME}/READ_ME_FIRST.md" in names, "entrypoint")
        assert_true(f"{ARTIFACT_DIR_NAME}/bootstrap.cmd" in names, "bootstrap")
        assert_true(f"{ARTIFACT_DIR_NAME}/MANIFEST.json" in names, "manifest")
        assert_true(f"{ARTIFACT_DIR_NAME}/payload/src/proteus/handoff.py" in names, "handoff source")
        assert_true(
            f"{ARTIFACT_DIR_NAME}/payload/AGENTS.md" not in names,
            "AGENTS.md must be generated on destination",
        )
        assert_true(
            not any(n.endswith("payload/.cursor/hooks/proteus_hook.cmd") for n in names),
            "must not ship origin-machine hook cmd",
        )


def test_cleanroom_reconstruction() -> None:
    result = cleanroom(repo=ROOT, origin_workspace=r"C:\Projects\Proteus", keep=True)
    dest = Path(result["reconstruct"]["dest"])
    try:
        assert_true(result["verify"]["pass"], json.dumps(result["verify"].get("failed"), indent=2))
        assert_true(result["live_user_hooks_unchanged"], "must not touch live ~/.cursor/hooks.json")
        assert_true((dest / "HANDOFF.md").is_file(), "Cursor entrypoint")
        assert_true((dest / "AGENTS.md").is_file(), "generated AGENTS.md")
        assert_true("SUPERSEDED" in (dest / "DECISIONS.md").read_text(encoding="utf-8"), "root decisions residue")
        assert_true("SUPERSEDED" in (dest / "FRONTIER.md").read_text(encoding="utf-8"), "root frontier residue")
        assert_true("UNKNOWN" in (dest / "state" / "UNRESOLVED.md").read_text(encoding="utf-8"), "UNKNOWN")
        assert_true("CONFLICT" in (dest / "state" / "UNRESOLVED.md").read_text(encoding="utf-8"), "CONFLICT")
        agents = (dest / "AGENTS.md").read_text(encoding="utf-8")
        assert_true(str(dest) in agents, "reconstructed source root")
        assert_true(r"C:\Projects\Proteus" not in agents and r"C:\projects\Proteus" not in agents, "no origin in AGENTS")
        hook = (dest / ".cursor" / "hooks" / "proteus_hook.cmd").read_text(encoding="utf-8")
        assert_true(r"C:\Projects\Proteus" not in hook, "hook cmd not origin tree")
        assert_true(".proteus-runtime" in hook or "proteus-runtime" in hook.replace("\\", "/"), "isolated runtime")
        v = verify_reconstructed(dest, isolated=True, origin_workspace=r"C:\Projects\Proteus")
        assert_true(v["pass"], str(v["failed"]))
    finally:
        def _onerror(func, path, _exc):  # noqa: ANN001
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass

        shutil.rmtree(result["cleanroom_dir"], onerror=_onerror)


def main() -> None:
    test_origin_path_boundary_does_not_treat_fresh_sibling_as_origin()
    test_payload_omits_generated_and_classifies_residue()
    test_isolated_install_does_not_use_live_cursor_dir()
    test_pack_zip_has_entrypoint_and_no_generated_payload()
    test_cleanroom_reconstruction()
    print("PASS portable handoff / clean-room reconstruction")


if __name__ == "__main__":
    main()
