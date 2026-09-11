"""Activate Proteus as a Codex project mount (foreign-carrier morphology).

This is not Cursor activation (`proteus.activate`) and not ideal-body
`install_cursor`. Codex-native surfaces only: AGENTS.md, .proteus/*, minimal
state carriers, world_env.cmd. No Cursor hooks/rules/launcher clone.

Reuses host-neutral `proteus.world.api` / `python -m proteus world` against
the shared entity substrate (AIYE_HOME).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .install_cursor import source_root

HOST = "codex"
ACTIVATION_DIR = ".proteus"
ACTIVATION_MANIFEST = "activation.json"
ENTRY_FILE = "ENTRY.md"
SCHEMA = "proteus.codex_activation.v0.1"


def resolve_codex_pythonpath(proteus_source: Path) -> Path:
    """Prefer ideal-body src — Codex must not depend on Cursor host-install copy."""
    src = proteus_source / "src"
    if (src / "proteus").is_dir():
        return src
    return resolve_runtime_pythonpath(proteus_source)

ActionKind = Literal[
    "create",
    "update",
    "skip_exists",
    "remove",
    "would_create",
    "would_update",
    "would_skip",
    "would_remove",
]


@dataclass
class PlannedAction:
    rel: str
    kind: ActionKind
    reason: str


@dataclass
class InspectReport:
    target: Path
    exists: bool
    is_dir: bool
    pre_existing: dict[str, bool] = field(default_factory=dict)
    already_activated: bool = False
    activation_id: str | None = None
    issues: list[str] = field(default_factory=list)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def resolve_proteus_source() -> Path:
    root = source_root()
    templates = root / "hosts" / "codex" / "templates"
    if templates.is_dir():
        return root
    raise FileNotFoundError(
        "Cannot locate Proteus Codex templates. Set PROTEUS_SOURCE_ROOT to a "
        "Proteus ideal-body tree containing hosts/codex/templates/."
    )


def templates_root(proteus_source: Path) -> Path:
    path = proteus_source / "hosts" / "codex" / "templates"
    if not path.is_dir():
        raise FileNotFoundError(f"Codex templates missing: {path}")
    return path


def default_aiye_home() -> Path:
    env = os.environ.get("AIYE_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".aiye").resolve()


def inspect_target(target: Path) -> InspectReport:
    report = InspectReport(
        target=target,
        exists=target.exists(),
        is_dir=target.is_dir() if target.exists() else False,
    )
    if not report.exists:
        report.issues.append(f"target does not exist: {target}")
        return report
    if not report.is_dir:
        report.issues.append(f"target is not a directory: {target}")
        return report
    keys = {
        "AGENTS.md": target / "AGENTS.md",
        "CLAUDE.md": target / "CLAUDE.md",
        "state": target / "state",
        ".proteus/activation.json": target / ACTIVATION_DIR / ACTIVATION_MANIFEST,
    }
    for k, p in keys.items():
        report.pre_existing[k] = p.exists()
    manifest = target / ACTIVATION_DIR / ACTIVATION_MANIFEST
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            report.already_activated = True
            report.activation_id = data.get("activation_id")
            if data.get("host") not in (None, HOST):
                report.issues.append(
                    f"activation.json host={data.get('host')!r} is not Codex; "
                    "refuse to overwrite a non-Codex mount with activate_codex"
                )
        except json.JSONDecodeError:
            report.issues.append(f"corrupt activation manifest: {manifest}")
    return report


def _render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for k, v in mapping.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def owned_file_plan() -> list[tuple[str, str]]:
    """(relative dest, template relative path under hosts/codex/templates)."""
    return [
        (f"{ACTIVATION_DIR}/{ENTRY_FILE}", "ENTRY.md"),
        (f"{ACTIVATION_DIR}/CONSTITUTIVE.md", "CONSTITUTIVE.md"),
        (f"{ACTIVATION_DIR}/world_env.cmd", "world_env.cmd"),
        ("state/IDENTITY.md", "state/IDENTITY.md"),
        ("state/CURRENT.md", "state/CURRENT.md"),
        ("state/FRONTIER.md", "state/FRONTIER.md"),
        ("state/DECISIONS.md", "state/DECISIONS.md"),
        ("state/UNRESOLVED.md", "state/UNRESOLVED.md"),
        ("AGENTS.md", "AGENTS.md"),
        ("CLAUDE.md", "CLAUDE.md"),
        (f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}", "__manifest__"),
    ]


PRESERVE_IF_EXISTS = {
    "AGENTS.md",
    "CLAUDE.md",
    "state/IDENTITY.md",
    "state/CURRENT.md",
    "state/FRONTIER.md",
    "state/DECISIONS.md",
    "state/UNRESOLVED.md",
}

REFRESHABLE = {
    f"{ACTIVATION_DIR}/{ENTRY_FILE}",
    f"{ACTIVATION_DIR}/CONSTITUTIVE.md",
    f"{ACTIVATION_DIR}/world_env.cmd",
    f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}",
}


def plan_activate(target: Path) -> list[PlannedAction]:
    actions: list[PlannedAction] = []
    for rel, _key in owned_file_plan():
        dest = target / rel
        if rel in PRESERVE_IF_EXISTS and dest.exists():
            actions.append(
                PlannedAction(rel, "skip_exists", "preserve pre-existing or previously written carrier")
            )
            continue
        if dest.exists() and rel in REFRESHABLE:
            actions.append(PlannedAction(rel, "update", "refresh Proteus-owned Codex surface"))
        elif dest.exists():
            actions.append(PlannedAction(rel, "skip_exists", "exists and not refreshable under policy"))
        else:
            actions.append(PlannedAction(rel, "create", "Proteus-owned Codex path absent"))
    return actions


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def activate(
    target: Path,
    *,
    dry_run: bool = False,
    run_id: str | None = None,
    activation_id: str | None = None,
    aiye_home: Path | None = None,
) -> dict[str, Any]:
    target = target.resolve()
    report = inspect_target(target)
    if report.issues and not report.exists:
        raise FileNotFoundError("; ".join(report.issues))
    if report.issues and not report.is_dir:
        raise NotADirectoryError("; ".join(report.issues))
    if report.issues:
        raise RuntimeError("; ".join(report.issues))

    proteus_source = resolve_proteus_source()
    pythonpath = resolve_codex_pythonpath(proteus_source)
    troot = templates_root(proteus_source)
    home = (aiye_home or default_aiye_home()).resolve()
    world_root = home / "world"

    act_id = activation_id or f"ACT-CODEX-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    if run_id:
        act_id = f"{run_id}-{act_id}" if not act_id.startswith(run_id) else act_id
    activated_at = utc_now()
    mapping = {
        "ACTIVATION_ID": act_id,
        "ACTIVATED_AT": activated_at,
        "PROTEUS_SOURCE": str(proteus_source),
        "TARGET_ROOT": str(target),
        "PROJECT_NAME": target.name,
        "RUN_ID": run_id or act_id,
        "AIYE_HOME": str(home),
        "PROTEUS_WORLD_ROOT": str(world_root),
        "PYTHONPATH": str(pythonpath),
    }

    planned = plan_activate(target)
    if dry_run:
        dry_actions = []
        for a in planned:
            if a.kind == "create":
                kind: ActionKind = "would_create"
            elif a.kind == "update":
                kind = "would_update"
            else:
                kind = "would_skip"
            dry_actions.append({"path": a.rel, "action": kind, "reason": a.reason})
        return {
            "schema": SCHEMA,
            "mode": "dry_run",
            "host": HOST,
            "target": str(target),
            "proteus_source": str(proteus_source),
            "runtime_pythonpath": str(pythonpath),
            "aiye_home": str(home),
            "proteus_world_root": str(world_root),
            "inspect": {
                "pre_existing": report.pre_existing,
                "already_activated": report.already_activated,
                "activation_id": report.activation_id,
            },
            "actions": dry_actions,
            "policy": {
                "AGENTS.md": "create_if_absent_else_preserve",
                "CLAUDE.md": "create_if_absent_else_preserve",
                "state/*": "create_if_absent_else_preserve",
                "cursor_hooks_rules": "not_installed",
            },
            "not_claimed": [
                "Gate 1",
                "Cursor morphology parity",
                "NATURAL_RECRUITMENT",
                "live Archivarius reconciliation",
            ],
        }

    prior_owned: set[str] = set()
    manifest_path = target / ACTIVATION_DIR / ACTIVATION_MANIFEST
    if manifest_path.is_file():
        try:
            prior = json.loads(manifest_path.read_text(encoding="utf-8"))
            prior_owned = set(prior.get("owned_paths") or [])
            if prior.get("activation_id"):
                act_id = prior["activation_id"]
                mapping["ACTIVATION_ID"] = act_id
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"cannot re-activate: corrupt {manifest_path}: {exc}") from exc

    performed: list[dict[str, str]] = []
    owned: list[str] = []
    content_hashes: dict[str, str] = {}
    preserve_notes: list[str] = []

    for rel, tmpl in owned_file_plan():
        dest = target / rel
        if rel == f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}":
            continue
        action = next(a for a in planned if a.rel == rel)
        if action.kind == "skip_exists":
            preserve_notes.append(rel)
            if rel in prior_owned:
                owned.append(rel)
            continue
        text = _render((troot / tmpl).read_text(encoding="utf-8"), mapping)
        _write(dest, text)
        owned.append(rel)
        content_hashes[rel] = _sha16(text.encode("utf-8"))
        performed.append({"path": rel, "action": action.kind, "reason": action.reason})

    # Seed empty project memory log if absent (project-scope routing target).
    pmem_rel = f"{ACTIVATION_DIR}/project_memory.jsonl"
    pmem = target / pmem_rel
    if not pmem.exists():
        pmem.write_text("", encoding="utf-8")
        owned.append(pmem_rel)
        performed.append(
            {"path": pmem_rel, "action": "create", "reason": "project-scope memory log"}
        )

    owned.append(f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}")
    manifest = {
        "schema": SCHEMA,
        "host": HOST,
        "activation_id": act_id,
        "activated_at": activated_at,
        "proteus_source": str(proteus_source),
        "runtime_pythonpath": str(pythonpath),
        "target": str(target),
        "run_id": run_id,
        "aiye_home": str(home),
        "proteus_world_root": str(world_root),
        "owned_paths": sorted(set(owned)),
        "content_hashes": content_hashes,
        "morphology": {
            "instruction_surface": "AGENTS.md",
            "entry": f"{ACTIVATION_DIR}/{ENTRY_FILE}",
            "world_env": f"{ACTIVATION_DIR}/world_env.cmd",
            "world_api": "proteus.world.api",
            "world_cli": "python -m proteus world",
            "cursor_hooks": False,
            "cursor_rules": False,
            "acting_role": "Codex coding agent (not BUILDER-01)",
        },
        "not_claimed": [
            "Gate 1",
            "identity with Cursor BUILDER-01 incarnation",
            "NATURAL_RECRUITMENT PASS",
            "LIVE_ARCHIVARIUS_RECONCILIATION",
            "real secret availability",
            "multi-host full sync",
        ],
    }
    man_text = json.dumps(manifest, indent=2) + "\n"
    man_existed = manifest_path.is_file()
    _write(manifest_path, man_text)
    content_hashes[f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}"] = _sha16(man_text.encode("utf-8"))
    performed.append(
        {
            "path": f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}",
            "action": "update" if man_existed else "create",
            "reason": "write Codex activation manifest",
        }
    )

    return {
        "schema": SCHEMA,
        "mode": "activate",
        "host": HOST,
        "target": str(target),
        "activation_id": act_id,
        "proteus_source": str(proteus_source),
        "runtime_pythonpath": str(pythonpath),
        "aiye_home": str(home),
        "proteus_world_root": str(world_root),
        "actions": performed,
        "owned_paths": manifest["owned_paths"],
        "preserved_paths": preserve_notes,
        "entry": f"{ACTIVATION_DIR}/{ENTRY_FILE}",
        "not_claimed": manifest["not_claimed"],
    }


def remove_activation(target: Path, *, dry_run: bool = False) -> dict[str, Any]:
    target = target.resolve()
    manifest_path = target / ACTIVATION_DIR / ACTIVATION_MANIFEST
    if not manifest_path.is_file():
        raise FileNotFoundError(f"no Codex activation manifest at {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("host") not in (None, HOST):
        raise RuntimeError(
            f"refuse to remove non-Codex activation (host={data.get('host')!r})"
        )
    owned = list(data.get("owned_paths") or [])
    actions: list[dict[str, str]] = []
    for rel in sorted(owned, reverse=True):
        path = target / rel
        if dry_run:
            actions.append({"path": rel, "action": "would_remove"})
            continue
        if path.is_file():
            path.unlink()
            actions.append({"path": rel, "action": "remove"})
        elif path.is_dir():
            # only remove empty dirs later
            actions.append({"path": rel, "action": "skip_dir"})
    if not dry_run:
        # Remove empty .proteus / state if emptied
        for drel in (ACTIVATION_DIR, "state"):
            d = target / drel
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
                actions.append({"path": drel, "action": "remove_empty_dir"})
    return {
        "schema": SCHEMA,
        "mode": "dry_run_remove" if dry_run else "remove",
        "host": HOST,
        "target": str(target),
        "actions": actions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Activate Proteus Codex project mount")
    parser.add_argument("--project", required=True, help="target project directory")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-id", default=None)
    parser.add_argument(
        "--aiye-home",
        default=None,
        help="AIYE_HOME / world substrate parent (default: env or ~/.aiye)",
    )
    ns = parser.parse_args(argv)
    target = Path(ns.project)
    if ns.remove:
        result = remove_activation(target, dry_run=ns.dry_run)
    else:
        aiye = Path(ns.aiye_home).expanduser() if ns.aiye_home else None
        result = activate(
            target,
            dry_run=ns.dry_run,
            run_id=ns.run_id,
            aiye_home=aiye,
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
