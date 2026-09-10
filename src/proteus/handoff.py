"""Pack and reconstruct a portable Proteus development workspace.

The user-carried artifact is a zip. It is not a live Cursor session, not
PROCESS_DEATH continuity, and not a clone of ~/.proteus or ~/.cursor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .install_cursor import source_root

ARTIFACT_DIR_NAME = "proteus-handoff"
ARTIFACT_FILENAME = "proteus-portable-handoff.zip"
PAYLOAD_PREFIX = "payload"
DEFAULT_RUN_ID = "PROTEUS-CURSOR-RUN-001-20260909T201711Z"

SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".venv",
    ".pytest_cache",
    "distribution",
    ".proteus-runtime",
    ".cursor-user-isolated",
}

SKIP_FILE_SUFFIXES = {".pyc", ".pyo"}

GENERATED_RELATIVE = {
    "AGENTS.md",
    "CLAUDE.md",
    "state/INCARNATION.md",
    ".cursor/hooks.json",
}

SUPERSEDED_ROOT_FILES = (
    "DECISIONS.md",
    "UNKNOWN.md",
    "DESIGN_v0.1.md",
    "FRONTIER.md",
    "CURRENT.md",
)

REQUIRED_STATE_FILES = (
    "IDENTITY.md",
    "CURRENT.md",
    "FRONTIER.md",
    "DECISIONS.md",
    "UNRESOLVED.md",
)

READ_ME_FIRST = """# PROTEUS PORTABLE HANDOFF — READ FIRST

This artifact reconstructs the currently useful Proteus *development environment*
(ideal-body source, durable state, tests, Cursor templates, bootstrap packet,
and first-incarnation evidence) on a compatible Windows machine.

It does **not** continue the originating Cursor process. It does **not** prove
PROCESS_DEATH survival. It does **not** upgrade Gate 1. It does **not** require
Google Drive, Agent CLI, or the original chat transcript.

## Carry this file only

Bring `proteus-portable-handoff.zip` (this archive). Place it in or next to an
empty directory.

## Reconstruct

```
mkdir fresh-workspace
copy proteus-portable-handoff.zip fresh-workspace\\
cd fresh-workspace
tar -xf proteus-portable-handoff.zip
proteus-handoff\\bootstrap.cmd
```

`bootstrap.cmd` copies `payload\\` into `..\\Proteus` (sibling of
`proteus-handoff\\`) and runs source → tests → install **isolated from** the
destination machine's live `~\\.cursor` / `~\\.proteus` unless you pass
`--machine-host`.

Machine-host install (real user hooks + `%USERPROFILE%\\.proteus`):

```
proteus-handoff\\bootstrap.cmd --machine-host
```

Python 3 must be on PATH. That interpreter is a destination host requirement;
it is not inside the zip.

## Then open Cursor

Open the reconstructed `Proteus` folder as the Cursor workspace. Start a new
Agent chat. Point it at `HANDOFF.md` (workspace root) or `AGENTS.md`. Do not
paste the old conversation.

## Authority after reconstruction

- Live carriers: `state/IDENTITY.md`, `state/CURRENT.md`, `state/FRONTIER.md`,
  `state/DECISIONS.md`, `state/UNRESOLVED.md`.
- Generated incarnation: `AGENTS.md`, `.cursor/rules`, `.cursor/skills`,
  `.cursor/hooks` — produced by `python -m proteus.install_cursor`, not payload
  copies of the origin machine's host files.
- Root `CURRENT.md` / `FRONTIER.md` / `DECISIONS.md` / `UNKNOWN.md` /
  `DESIGN_v0.1.md` are **SUPERSEDED residue**. Do not treat them as live.
- Evidence under `evidence/runs/` is historical. Statuses stay PASS / PARTIAL /
  UNKNOWN / CONFLICT as written. Do not silently upgrade them.
- `state/CURRENT.md` may still name the original first-incarnation workspace
  path. That is provenance, not a requirement that this machine use that path.

## What this zip will not recreate

- Live hook spool / machine_id / Cursor PID evidence
- Google Drive observatory transport (FAILED_TRANSPORT)
- Cursor Agent CLI (unproved on origin)
- A witness that the origin Cursor OS process quit
"""

BOOTSTRAP_CMD = r"""@echo off
setlocal EnableExtensions
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3 must be on PATH. It is a destination host requirement, not part of this zip.
  exit /b 2
)
set "PYTHONPATH=%~dp0payload\src"
python -m proteus.handoff reconstruct --artifact-root "%~dp0." %*
exit /b %ERRORLEVEL%
"""


def origin_workspace_from_state(repo: Path) -> str | None:
    path = repo / "state" / "CURRENT.md"
    if not path.exists():
        return None
    match = re.search(r"Workspace:\s*`([^`]+)`", path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def origin_path_markers(origin: str | None) -> tuple[str, ...]:
    if not origin:
        return ()
    variants = [origin, origin.replace("Projects", "projects"), origin.replace("projects", "Projects")]
    return tuple(dict.fromkeys(variants))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def posix(rel: Path | str) -> str:
    return str(rel).replace("\\", "/")


def git_head(repo: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip() or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_payload_path(rel: str) -> str:
    rel = posix(rel)
    name = Path(rel).name
    if rel in SUPERSEDED_ROOT_FILES or name in SUPERSEDED_ROOT_FILES and "/" not in rel:
        return "superseded_residue"
    if rel.startswith("state/"):
        return "portable_state"
    if (
        rel.startswith("evidence/")
        or rel.startswith("_BOOTSTRAP/")
        or rel == "BLIND_OBSERVATION.md"
    ):
        return "portable_evidence"
    if (
        rel.startswith("src/")
        or rel.startswith("hosts/")
        or rel.startswith("tests/")
        or rel.startswith(".cursor/commands/")
        or rel in {"README.md", ".gitignore"}
    ):
        return "portable_source"
    return "portable_other"


def _should_skip_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES or name.endswith(".egg-info")


def iter_payload_files(repo: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]
        base = Path(dirpath)
        for name in filenames:
            path = base / name
            if path.suffix in SKIP_FILE_SUFFIXES:
                continue
            rel = posix(path.relative_to(repo))
            if rel in GENERATED_RELATIVE:
                continue
            parts = Path(rel).parts
            if parts and parts[0] == ".cursor" and (len(parts) < 2 or parts[1] != "commands"):
                continue
            yield path


def default_artifact_zip(repo: Path) -> Path:
    dest_dir = repo / "distribution"
    dest_dir.mkdir(parents=True, exist_ok=True)
    return dest_dir / ARTIFACT_FILENAME


def pack(repo: Path | None = None, *, zip_path: Path | None = None) -> dict[str, Any]:
    repo = (repo or source_root()).resolve()
    zip_path = (zip_path or default_artifact_zip(repo)).resolve()
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, str]] = []
    manifest: dict[str, Any] = {
        "artifact_type": "zip-classified-payload-plus-bootstrap",
        "artifact_filename": zip_path.name,
        "created_utc": utc_now().isoformat(),
        "source_revision": git_head(repo),
        "active_run_id_hint": DEFAULT_RUN_ID,
        "gate_1": "NOT_YET",
        "process_death_continuity": "NOT_CLAIMED",
        "classes": {
            "portable_source": "ideal body, templates, tests, README, project command source",
            "portable_state": "state/* except generated INCARNATION.md",
            "portable_evidence": "evidence/, _BOOTSTRAP/, BLIND_OBSERVATION.md",
            "superseded_residue": "root CURRENT/FRONTIER/DECISIONS/UNKNOWN/DESIGN dumps; not live carriers",
            "generate_on_install": sorted(GENERATED_RELATIVE)
            + [".cursor/rules/", ".cursor/skills/", ".cursor/hooks/"],
            "installation_action": [
                "python -m proteus.install_cursor on the destination tree",
                "optional --machine-host writes ~/.cursor hooks and %USERPROFILE%\\.proteus host runtime",
            ],
            "machine_local_runtime": [
                "%USERPROFILE%\\.proteus\\telemetry",
                "%USERPROFILE%\\.proteus\\machine_id",
                "live Cursor PID / hook spool rows",
            ],
            "non_portable_host_capability": [
                "Google Drive observatory transport (FAILED_TRANSPORT)",
                "Cursor Agent CLI (unproved)",
                "OS process-quit witness (UNKNOWN)",
                "Python 3 interpreter on destination PATH",
            ],
        },
        "files": files,
    }
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{ARTIFACT_DIR_NAME}/READ_ME_FIRST.md", READ_ME_FIRST.replace("\n", "\r\n"))
        zf.writestr(f"{ARTIFACT_DIR_NAME}/bootstrap.cmd", BOOTSTRAP_CMD.replace("\n", "\r\n"))
        for path in sorted(iter_payload_files(repo), key=lambda p: posix(p.relative_to(repo)).lower()):
            rel = posix(path.relative_to(repo))
            files.append({"path": rel, "class": classify_payload_path(rel)})
            zf.write(path, f"{ARTIFACT_DIR_NAME}/{PAYLOAD_PREFIX}/{rel}")
        zf.writestr(
            f"{ARTIFACT_DIR_NAME}/MANIFEST.json",
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        )
    manifest["sha256"] = sha256_file(zip_path)
    manifest["zip_path"] = str(zip_path)
    manifest["file_count"] = len(files)
    sidecar = zip_path.with_suffix(".manifest.json")
    sidecar.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def _extract_zip(zip_path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
    artifact_root = dest_dir / ARTIFACT_DIR_NAME
    if not artifact_root.is_dir():
        raise FileNotFoundError(f"zip did not contain {ARTIFACT_DIR_NAME}/")
    return artifact_root


def _copytree(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)


def _run_id_from_state(dest: Path) -> str:
    current = dest / "state" / "CURRENT.md"
    if current.exists():
        for line in current.read_text(encoding="utf-8").splitlines():
            if "RUN_ID" in line and "`" in line:
                parts = line.split("`")
                if len(parts) >= 2 and parts[1].startswith("PROTEUS-"):
                    return parts[1]
    return DEFAULT_RUN_ID


def _write_reconstruction_docs(dest: Path, *, isolated: bool, run_id: str, manifest: dict[str, Any]) -> None:
    ts = utc_now().isoformat()
    reconstruction = (
        f"# Reconstruction\n\n"
        f"- reconstructed_at: `{ts}`\n"
        f"- destination: `{dest}`\n"
        f"- isolated_host: `{str(isolated).lower()}`\n"
        f"- origin_run_id_hint: `{run_id}`\n"
        f"- origin_source_revision: `{manifest.get('source_revision', 'UNKNOWN')}`\n"
        f"- process_death_continuity: `NOT_CLAIMED`\n"
        f"- gate_1: `NOT_YET` (not upgraded by reconstruction)\n"
        f"- original workspace path in `state/CURRENT.md` is provenance of the first incarnation, "
        f"not a requirement that this tree live at that path.\n"
    )
    (dest / "state" / "RECONSTRUCTION.md").write_text(reconstruction, encoding="utf-8", newline="\n")
    handoff = (
        f"# HANDOFF — reconstructed Proteus workspace\n\n"
        f"Give this file to a fresh Cursor Agent. Do not paste the origin chat.\n\n"
        f"1. You are BUILDER-01 on a **reconstructed** tree. Read `AGENTS.md`.\n"
        f"2. Read `state/IDENTITY.md`, `state/CURRENT.md`, `state/FRONTIER.md`, "
        f"`state/DECISIONS.md`, `state/UNRESOLVED.md`, then `state/RECONSTRUCTION.md`.\n"
        f"3. Preserve PASS / PARTIAL / UNKNOWN / CONFLICT. Do not upgrade Gate 1 or T02.\n"
        f"4. Root `CURRENT.md` / `FRONTIER.md` / `DECISIONS.md` / `UNKNOWN.md` / "
        f"`DESIGN_v0.1.md` are superseded residue.\n"
        f"5. Continue from `state/FRONTIER.md`.\n\n"
        f"Isolated host install this reconstruction: `{isolated}`.\n"
        f"Destination: `{dest}`.\n"
    )
    (dest / "HANDOFF.md").write_text(handoff, encoding="utf-8", newline="\n")


def reconstruct(
    *,
    artifact_root: Path,
    dest: Path | None = None,
    isolated: bool = True,
    machine_host: bool = False,
) -> dict[str, Any]:
    artifact_root = artifact_root.resolve()
    payload = artifact_root / PAYLOAD_PREFIX
    if not payload.is_dir():
        raise FileNotFoundError(f"payload/ missing under {artifact_root}")
    if dest is None:
        dest = artifact_root.parent / "Proteus"
    dest = dest.resolve()
    isolated = isolated and not machine_host
    _copytree(payload, dest)
    manifest_path = artifact_root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    run_id = _run_id_from_state(dest)
    _write_reconstruction_docs(dest, isolated=isolated, run_id=run_id, manifest=manifest)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(dest / "src")
    env["PROTEUS_SOURCE_ROOT"] = str(dest)
    env["PROTEUS_RUN_ID"] = run_id
    if isolated:
        env["PROTEUS_HOME"] = str(dest / ".proteus-runtime")
        env["PROTEUS_CURSOR_USER_DIR"] = str(dest / ".cursor-user-isolated")
    else:
        env.pop("PROTEUS_HOME", None)
        env.pop("PROTEUS_CURSOR_USER_DIR", None)
    backup_dir = dest / "evidence" / "reconstructions" / utc_now().strftime("%Y%m%dT%H%M%SZ") / "host-backups"
    install = subprocess.run(
        [
            sys.executable,
            "-m",
            "proteus.install_cursor",
            "--project",
            str(dest),
            "--run-id",
            run_id,
            "--backup-dir",
            str(backup_dir),
        ],
        cwd=str(dest),
        env=env,
        capture_output=True,
        text=True,
    )
    tests: dict[str, Any] = {}
    for script in ("tests/test_smoke.py", "tests/test_hook_event_identity.py"):
        proc = subprocess.run(
            [sys.executable, str(dest / script)],
            cwd=str(dest),
            env=env,
            capture_output=True,
            text=True,
        )
        tests[script] = {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
    report = {
        "dest": str(dest),
        "artifact_root": str(artifact_root),
        "isolated": isolated,
        "run_id": run_id,
        "install_returncode": install.returncode,
        "install_stdout_tail": install.stdout[-4000:],
        "install_stderr_tail": install.stderr[-4000:],
        "tests": tests,
        "source_revision_in_manifest": manifest.get("source_revision", "UNKNOWN"),
    }
    rec_dir = dest / "evidence" / "reconstructions"
    rec_dir.mkdir(parents=True, exist_ok=True)
    (rec_dir / "LAST.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if install.returncode != 0:
        raise RuntimeError(f"install_cursor failed: {install.stderr or install.stdout}")
    failed = [k for k, v in tests.items() if v["returncode"] != 0]
    if failed:
        raise RuntimeError(f"reconstruct tests failed: {failed} {tests}")
    return report


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(n in text for n in needles)


def operational_coupling_hits(root: Path, markers: Iterable[str] | None = None) -> list[str]:
    needles = tuple(markers or ())
    if not needles:
        return []
    hits: list[str] = []
    for folder in ("src", "hosts"):
        base = root / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".py", ".md", ".mdc", ".json", ".cmd", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if _contains_any(text, needles):
                hits.append(posix(path.relative_to(root)))
    return hits


def verify_reconstructed(dest: Path, *, isolated: bool, origin_workspace: str | None = None) -> dict[str, Any]:
    dest = dest.resolve()
    checks: dict[str, Any] = {}

    def ok(name: str, cond: bool, detail: str = "") -> None:
        checks[name] = {"pass": bool(cond), "detail": detail}

    ok("handoff_entrypoint", (dest / "HANDOFF.md").is_file() and (dest / "AGENTS.md").is_file())
    for name in REQUIRED_STATE_FILES:
        ok(f"state_{name}", (dest / "state" / name).is_file())
    current = _text(dest / "state" / "CURRENT.md")
    unresolved = _text(dest / "state" / "UNRESOLVED.md")
    decisions = _text(dest / "state" / "DECISIONS.md")
    ok("t02_remains_partial", "T02 PARTIAL" in current or "T02" in unresolved and "PARTIAL" in unresolved)
    ok("gate1_not_yet", "Gate 1 NOT_YET" in current or "GATE_1 = NOT_YET" in current)
    ok("unknown_survives", "UNKNOWN" in unresolved)
    ok("conflict_survives", "CONFLICT" in unresolved)
    ok("d001_present", "D-001" in decisions)
    ok("d004_present", "D-004" in decisions)
    ok("d005_present", "D-005" in decisions)
    root_decisions = _text(dest / "DECISIONS.md")
    root_frontier = _text(dest / "FRONTIER.md")
    root_current = _text(dest / "CURRENT.md")
    ok("root_decisions_superseded", "SUPERSEDED" in root_decisions)
    ok("root_frontier_not_live", "SUPERSEDED" in root_frontier or "Historical" in root_frontier)
    ok("root_current_not_live", "SUPERSEDED" in root_current)
    agents = _text(dest / "AGENTS.md")
    ok("agents_source_root_is_dest", str(dest) in agents)
    if origin_workspace:
        ok(
            "agents_source_root_not_origin",
            origin_workspace.lower() not in agents.lower() or origin_workspace.lower() == str(dest).lower(),
        )
        ok(
            "state_current_keeps_origin_provenance",
            origin_workspace in current or origin_workspace.replace("Projects", "projects") in current,
        )
    recon = _text(dest / "state" / "RECONSTRUCTION.md")
    ok("reconstruction_not_process_death", "NOT_CLAIMED" in recon)
    hook = _text(dest / ".cursor" / "hooks" / "proteus_hook.cmd")
    markers = origin_path_markers(origin_workspace)
    ok("project_hook_not_origin_tree", not _contains_any(hook, markers) if markers else True)
    hits = operational_coupling_hits(dest, markers)
    ok("no_operational_origin_path_in_src_hosts", hits == [], ",".join(hits))
    if isolated:
        ok("isolated_proteus_home", (dest / ".proteus-runtime").is_dir())
        ok("isolated_cursor_user", (dest / ".cursor-user-isolated" / "hooks.json").is_file())
    ok("tests_dir", (dest / "tests" / "test_smoke.py").is_file())
    ok("templates_present", (dest / "hosts" / "cursor" / "templates" / "AGENTS.md").is_file())
    ok("bootstrap_packet", (dest / "_BOOTSTRAP" / "BLIND_START" / "00_READ_FIRST.md").is_file())
    failed = [k for k, v in checks.items() if not v["pass"]]
    return {"pass": not failed, "failed": failed, "checks": checks, "dest": str(dest)}


def cleanroom(
    *,
    repo: Path | None = None,
    origin_workspace: str | None = None,
    keep: bool = False,
) -> dict[str, Any]:
    import tempfile

    repo = (repo or source_root()).resolve()
    origin_workspace = origin_workspace or origin_workspace_from_state(repo)
    live_hooks = Path(os.environ.get("USERPROFILE") or Path.home()) / ".cursor" / "hooks.json"
    live_before = live_hooks.read_bytes() if live_hooks.exists() else None
    pack_dir = Path(tempfile.mkdtemp(prefix="proteus-pack-"))
    zip_path = pack_dir / ARTIFACT_FILENAME
    manifest = pack(repo, zip_path=zip_path)
    clean = Path(tempfile.mkdtemp(prefix="proteus-cleanroom-"))
    only_zip = clean / ARTIFACT_FILENAME
    shutil.copy2(zip_path, only_zip)
    # Only the zip is present in clean/ initially.
    extract_dir = clean / "extracted"
    artifact_root = _extract_zip(only_zip, extract_dir)
    dest = clean / "Proteus"
    report = reconstruct(artifact_root=artifact_root, dest=dest, isolated=True)
    verification = verify_reconstructed(dest, isolated=True, origin_workspace=origin_workspace)
    live_after = live_hooks.read_bytes() if live_hooks.exists() else None
    live_unchanged = live_before == live_after
    verification["checks"]["live_user_hooks_unchanged"] = {
        "pass": live_unchanged,
        "detail": "isolated reconstruct must not rewrite ~/.cursor/hooks.json",
    }
    if not live_unchanged:
        verification["pass"] = False
        verification["failed"] = list(verification.get("failed") or []) + ["live_user_hooks_unchanged"]
    result = {
        "cleanroom_dir": str(clean),
        "zip_path": str(only_zip),
        "zip_sha256": manifest.get("sha256"),
        "file_count": manifest.get("file_count"),
        "reconstruct": {k: report[k] for k in ("dest", "isolated", "run_id", "install_returncode") if k in report},
        "verify": verification,
        "live_user_hooks_unchanged": live_unchanged,
    }
    def _onerror(func, path, _exc):  # noqa: ANN001
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    shutil.rmtree(pack_dir, onerror=_onerror)
    if not keep and verification["pass"] and live_unchanged:
        shutil.rmtree(clean, onerror=_onerror)
        result["cleanroom_dir"] = "removed_after_pass"
    if not verification["pass"] or not live_unchanged:
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="proteus.handoff")
    sub = p.add_subparsers(dest="cmd", required=True)
    pk = sub.add_parser("pack")
    pk.add_argument("--repo", default=None)
    pk.add_argument("--zip", dest="zip_path", default=None)
    rec = sub.add_parser("reconstruct")
    rec.add_argument("--artifact-root", required=True)
    rec.add_argument("--dest", default=None)
    rec.add_argument("--isolated", action="store_true", default=True)
    rec.add_argument("--machine-host", action="store_true")
    cr = sub.add_parser("cleanroom")
    cr.add_argument("--repo", default=None)
    cr.add_argument("--keep", action="store_true")
    ns = p.parse_args(argv)
    if ns.cmd == "pack":
        out = pack(Path(ns.repo) if ns.repo else None, zip_path=Path(ns.zip_path) if ns.zip_path else None)
        print(json.dumps({k: out[k] for k in ("zip_path", "sha256", "file_count", "source_revision")}, indent=2))
        return 0
    if ns.cmd == "reconstruct":
        isolated = not ns.machine_host
        out = reconstruct(
            artifact_root=Path(ns.artifact_root),
            dest=Path(ns.dest) if ns.dest else None,
            isolated=isolated,
            machine_host=ns.machine_host,
        )
        print(json.dumps(out, indent=2))
        return 0
    if ns.cmd == "cleanroom":
        out = cleanroom(repo=Path(ns.repo) if ns.repo else None, keep=ns.keep)
        print(json.dumps(out, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
