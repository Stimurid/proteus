"""Activate Proteus as a Cursor project mount on an existing coding-agent project.

This is PRODUCT_SPEC form C (project mount) + §4.3 bootstrap — not ideal-body
incarnation (`install_cursor`) and not Gate 1 acceptance of the whole product.

Coexistence (D-006): never overwrite pre-existing AGENTS.md / CLAUDE.md /
non-proteus Cursor rules / pre-existing state carriers. Only Proteus-owned
paths listed in `.proteus/activation.json` are written on activate and removed
on --remove.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .install_cursor import hook_command, proteus_hook_cmd_text, source_root, templates_dir
from .paths import host_install_dir

HOST = "cursor"
ACTIVATION_DIR = ".proteus"
ACTIVATION_MANIFEST = "activation.json"
ENTRY_FILE = "ENTRY.md"
SCHEMA = "proteus.activation.v0.1"

ActionKind = Literal["create", "update", "skip_exists", "merge", "remove", "would_create", "would_update", "would_merge", "would_remove", "would_skip"]


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
    """Prefer explicit env, then module source tree, fail if templates missing."""
    root = source_root()
    activate_templates = root / "hosts" / "cursor" / "templates" / "activate"
    if activate_templates.is_dir():
        return root
    raise FileNotFoundError(
        "Cannot locate Proteus activate templates. Set PROTEUS_SOURCE_ROOT to a "
        "Proteus ideal-body tree (or portable reconstruct) containing "
        "hosts/cursor/templates/activate/."
    )


def resolve_runtime_pythonpath(proteus_source: Path) -> Path:
    """Prefer machine host install copy; else ideal-body src. Fail visibly."""
    host_src = host_install_dir() / "src"
    if (host_src / "proteus").is_dir():
        return host_src
    src = proteus_source / "src"
    if (src / "proteus").is_dir():
        return src
    raise FileNotFoundError(
        "Cannot resolve Proteus Python runtime (proteus package). "
        "Run `python -m proteus.install_cursor` once on a Proteus tree, "
        "or ensure PROTEUS_SOURCE_ROOT/src/proteus exists."
    )


def activate_templates_root(proteus_source: Path) -> Path:
    path = proteus_source / "hosts" / "cursor" / "templates" / "activate"
    if not path.is_dir():
        raise FileNotFoundError(f"Activate templates missing: {path}")
    return path


def shared_templates_root(proteus_source: Path) -> Path:
    return templates_dir(proteus_source)


def inspect_target(target: Path) -> InspectReport:
    report = InspectReport(target=target, exists=target.exists(), is_dir=target.is_dir() if target.exists() else False)
    if not report.exists:
        report.issues.append(f"target does not exist: {target}")
        return report
    if not report.is_dir:
        report.issues.append(f"target is not a directory: {target}")
        return report
    keys = {
        "AGENTS.md": target / "AGENTS.md",
        "CLAUDE.md": target / "CLAUDE.md",
        ".cursor/rules": target / ".cursor" / "rules",
        ".cursor/hooks.json": target / ".cursor" / "hooks.json",
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
        except json.JSONDecodeError:
            report.issues.append(f"corrupt activation manifest: {manifest}")
    return report


def _render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for k, v in mapping.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def _read_template(path: Path, mapping: dict[str, str]) -> str:
    return _render(path.read_text(encoding="utf-8"), mapping)


def owned_file_plan() -> list[tuple[str, str]]:
    """(relative dest, template key). template key: activate:<rel> or shared:<rel>."""
    return [
        (f"{ACTIVATION_DIR}/{ENTRY_FILE}", "activate:ENTRY.md"),
        ("state/IDENTITY.md", "activate:state/IDENTITY.md"),
        ("state/CURRENT.md", "activate:state/CURRENT.md"),
        ("state/FRONTIER.md", "activate:state/FRONTIER.md"),
        ("state/DECISIONS.md", "activate:state/DECISIONS.md"),
        ("state/UNRESOLVED.md", "activate:state/UNRESOLVED.md"),
        ("AGENTS.md", "activate:AGENTS.md"),
        ("CLAUDE.md", "activate:CLAUDE.md"),
        (".cursor/rules/proteus-orientation.mdc", "activate:rules/proteus-orientation.mdc"),
        (".cursor/rules/proteus-mutation.mdc", "activate:rules/proteus-mutation.mdc"),
        (".cursor/rules/proteus-anti-reduction.mdc", "shared:rules/proteus-anti-reduction.mdc"),
        (".cursor/skills/proteus-checkpoint/SKILL.md", "shared:skills/proteus-checkpoint/SKILL.md"),
        (".cursor/skills/proteus-correction/SKILL.md", "shared:skills/proteus-correction/SKILL.md"),
        (".cursor/skills/proteus-reentry/SKILL.md", "shared:skills/proteus-reentry/SKILL.md"),
        (".cursor/skills/proteus-world/SKILL.md", "activate:skills/proteus-world/SKILL.md"),
        (".cursor/commands/proteus-checkpoint.md", "shared:commands/proteus-checkpoint.md"),
        (".cursor/hooks/proteus_hook.cmd", "runtime:hook_cmd"),
        (".cursor/hooks.json", "runtime:hooks_json"),
        (f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}", "runtime:manifest"),
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

# On re-run, Proteus-owned generated surfaces may be refreshed.
REFRESHABLE = {
    f"{ACTIVATION_DIR}/{ENTRY_FILE}",
    ".cursor/rules/proteus-orientation.mdc",
    ".cursor/rules/proteus-mutation.mdc",
    ".cursor/rules/proteus-anti-reduction.mdc",
    ".cursor/skills/proteus-checkpoint/SKILL.md",
    ".cursor/skills/proteus-correction/SKILL.md",
    ".cursor/skills/proteus-reentry/SKILL.md",
    ".cursor/skills/proteus-world/SKILL.md",
    ".cursor/commands/proteus-checkpoint.md",
    ".cursor/hooks/proteus_hook.cmd",
    ".cursor/hooks.json",
    f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}",
}


def _load_template_text(
    key: str,
    *,
    activate_root: Path,
    shared_root: Path,
    mapping: dict[str, str],
    pythonpath: Path,
) -> str | None:
    if key.startswith("activate:"):
        rel = key.split(":", 1)[1]
        return _read_template(activate_root / rel, mapping)
    if key.startswith("shared:"):
        rel = key.split(":", 1)[1]
        return _read_template(shared_root / rel, mapping)
    if key == "runtime:hook_cmd":
        return proteus_hook_cmd_text(python=sys.executable, pythonpath=str(pythonpath))
    if key == "runtime:hooks_json":
        return None  # merged specially
    if key == "runtime:manifest":
        return None
    raise ValueError(f"unknown template key: {key}")


def project_hooks_payload() -> dict[str, Any]:
    return {
        "version": 1,
        "hooks": {
            "sessionStart": [{"command": hook_command("sessionStart", project=True), "timeout": 15}],
            "stop": [{"command": hook_command("stop", project=True), "timeout": 15, "loop_limit": 2}],
            "preCompact": [{"command": hook_command("preCompact", project=True), "timeout": 15}],
        },
    }


def read_text_utf8(path: Path) -> str:
    """Read text accepting UTF-8 with or without BOM (Windows editors often write BOM)."""
    return path.read_text(encoding="utf-8-sig")


def merge_project_hooks(existing_text: str | None) -> str:
    proteus = project_hooks_payload()
    if not existing_text:
        return json.dumps(proteus, indent=2) + "\n"
    try:
        prev = json.loads(existing_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"cannot merge hooks.json: invalid JSON ({exc})") from exc
    if not isinstance(prev, dict):
        raise ValueError("cannot merge hooks.json: root must be an object")
    hooks_map = prev.setdefault("hooks", {})
    if not isinstance(hooks_map, dict):
        raise ValueError("cannot merge hooks.json: hooks must be an object")
    for name, entries in proteus["hooks"].items():
        current = hooks_map.get(name) or []
        if not isinstance(current, list):
            raise ValueError(f"cannot merge hooks.json: hooks.{name} must be a list")
        current = [h for h in current if "proteus_hook" not in str(h)]
        current.extend(entries)
        hooks_map[name] = current
    prev["version"] = prev.get("version") or 1
    return json.dumps(prev, indent=2) + "\n"


def strip_proteus_hooks(existing_text: str) -> str | None:
    """Return updated JSON text, or None if hooks object becomes empty of all events."""
    data = json.loads(existing_text)
    hooks = data.get("hooks") or {}
    for k, lst in list(hooks.items()):
        hooks[k] = [h for h in lst if "proteus_hook" not in str(h)]
        if not hooks[k]:
            del hooks[k]
    data["hooks"] = hooks
    if not hooks and set(data.keys()) <= {"version", "hooks"}:
        # File was only Proteus — remove entirely
        return None
    return json.dumps(data, indent=2) + "\n"


def plan_activate(target: Path) -> list[PlannedAction]:
    actions: list[PlannedAction] = []
    for rel, _key in owned_file_plan():
        dest = target / rel
        if rel == ".cursor/hooks.json":
            if dest.exists():
                actions.append(PlannedAction(rel, "merge", "merge proteus_hook entries; preserve others"))
            else:
                actions.append(PlannedAction(rel, "create", "write proteus project hooks.json"))
            continue
        if rel in PRESERVE_IF_EXISTS and dest.exists():
            # Re-run: if we own it (listed in prior manifest), allow refresh only for non-preserve?
            # Preserve policy is absolute for these paths once foreign or first-written content exists.
            actions.append(PlannedAction(rel, "skip_exists", "preserve pre-existing or previously written carrier"))
            continue
        if dest.exists() and rel in REFRESHABLE:
            actions.append(PlannedAction(rel, "update", "refresh Proteus-owned surface"))
        elif dest.exists():
            actions.append(PlannedAction(rel, "skip_exists", "exists and not refreshable under policy"))
        else:
            actions.append(PlannedAction(rel, "create", "Proteus-owned path absent"))
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
    pythonpath = resolve_runtime_pythonpath(proteus_source)
    activate_root = activate_templates_root(proteus_source)
    shared_root = shared_templates_root(proteus_source)

    # Preflight: validate hooks merge before any writes (avoid partial trees).
    hooks_path = target / ".cursor" / "hooks.json"
    hooks_existing: str | None = None
    if hooks_path.is_file():
        hooks_existing = read_text_utf8(hooks_path)
        try:
            merge_project_hooks(hooks_existing)
        except ValueError as exc:
            raise RuntimeError(str(exc)) from exc

    act_id = activation_id or f"ACT-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    if run_id:
        act_id = f"{run_id}-{act_id}" if not act_id.startswith(run_id) else act_id
    activated_at = utc_now()
    project_name = target.name
    mapping = {
        "ACTIVATION_ID": act_id,
        "ACTIVATED_AT": activated_at,
        "PROTEUS_SOURCE": str(proteus_source),
        "TARGET_ROOT": str(target),
        "PROJECT_NAME": project_name,
        "RUN_ID": run_id or act_id,
        "SOURCE_ROOT": str(proteus_source),
    }

    planned = plan_activate(target)
    if dry_run:
        dry_actions = []
        for a in planned:
            kind: ActionKind
            if a.kind == "create":
                kind = "would_create"
            elif a.kind == "update":
                kind = "would_update"
            elif a.kind == "merge":
                kind = "would_merge"
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
            "inspect": {
                "pre_existing": report.pre_existing,
                "already_activated": report.already_activated,
                "activation_id": report.activation_id,
            },
            "actions": dry_actions,
            "entry": f"{ACTIVATION_DIR}/{ENTRY_FILE}",
            "policy": {
                "AGENTS.md": "create_if_absent_else_preserve",
                "CLAUDE.md": "create_if_absent_else_preserve",
                "state/*": "create_if_absent_else_preserve",
                ".cursor/rules": "only proteus-*.mdc",
                "hooks.json": "merge proteus_hook only",
            },
        }

    prior_owned: set[str] = set()
    manifest_path = target / ACTIVATION_DIR / ACTIVATION_MANIFEST
    if manifest_path.is_file():
        try:
            prior = json.loads(manifest_path.read_text(encoding="utf-8"))
            prior_owned = set(prior.get("owned_paths") or [])
            # Keep stable activation_id on re-run
            if prior.get("activation_id"):
                act_id = prior["activation_id"]
                mapping["ACTIVATION_ID"] = act_id
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"cannot re-activate: corrupt {manifest_path}: {exc}") from exc

    performed: list[dict[str, str]] = []
    owned: list[str] = []
    content_hashes: dict[str, str] = {}
    preserve_notes: list[str] = []

    for rel, key in owned_file_plan():
        dest = target / rel
        if rel == f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}":
            continue  # written at end
        if rel == ".cursor/hooks.json":
            existing = hooks_existing if dest.exists() else None
            try:
                text = merge_project_hooks(existing)
            except ValueError as exc:
                raise RuntimeError(str(exc)) from exc
            action = "merge" if existing is not None else "create"
            _write(dest, text)
            owned.append(rel)
            content_hashes[rel] = _sha16(text.encode("utf-8"))
            performed.append({"path": rel, "action": action, "reason": "proteus_hook merge"})
            continue

        if rel in PRESERVE_IF_EXISTS and dest.exists():
            preserve_notes.append(rel)
            performed.append({"path": rel, "action": "skip_exists", "reason": "preserve existing"})
            # If we created it on a prior activate, keep ownership
            if rel in prior_owned:
                owned.append(rel)
                content_hashes[rel] = _sha16(dest.read_bytes())
            continue

        text = _load_template_text(
            key,
            activate_root=activate_root,
            shared_root=shared_root,
            mapping=mapping,
            pythonpath=pythonpath,
        )
        assert text is not None
        action = "update" if dest.exists() else "create"
        _write(dest, text)
        owned.append(rel)
        content_hashes[rel] = _sha16(text.encode("utf-8"))
        performed.append({"path": rel, "action": action, "reason": "Proteus-owned"})

    # Always own entry + manifest
    if f"{ACTIVATION_DIR}/{ENTRY_FILE}" not in owned:
        # should have been written; ensure
        pass

    receipt = {
        "schema": SCHEMA,
        "activation_id": act_id,
        "host": HOST,
        "activated_at": activated_at,
        "updated_at": activated_at,
        "target_root": str(target),
        "proteus_source": str(proteus_source),
        "runtime_pythonpath": str(pythonpath),
        "python": sys.executable,
        "run_id": run_id,
        "owned_paths": sorted(set(owned) | {f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}", f"{ACTIVATION_DIR}/{ENTRY_FILE}"}),
        "content_sha256_16": content_hashes,
        "preserved_paths": preserve_notes,
        "policy": {
            "AGENTS.md": "create_if_absent_else_preserve",
            "CLAUDE.md": "create_if_absent_else_preserve",
            "state/*": "create_if_absent_else_preserve",
            ".cursor/rules": "only proteus-*.mdc owned",
            "hooks.json": "merge proteus_hook only",
            "removal": "only owned_paths from this manifest",
        },
        "actions": performed,
        "entry": f"{ACTIVATION_DIR}/{ENTRY_FILE}",
        "not_claimed": [
            "Gate 1",
            "full Proteus product acceptance",
            "PROCESS_DEATH continuity",
            "universal multi-host activation",
        ],
    }
    # Ensure ENTRY is owned even if somehow skipped
    entry_rel = f"{ACTIVATION_DIR}/{ENTRY_FILE}"
    if entry_rel not in receipt["owned_paths"]:
        receipt["owned_paths"].append(entry_rel)
        receipt["owned_paths"] = sorted(set(receipt["owned_paths"]))

    manifest_body = json.dumps(receipt, indent=2) + "\n"
    _write(manifest_path, manifest_body)
    receipt["content_sha256_16"][f"{ACTIVATION_DIR}/{ACTIVATION_MANIFEST}"] = _sha16(manifest_body.encode("utf-8"))
    # rewrite with hash of manifest included
    manifest_body = json.dumps(receipt, indent=2) + "\n"
    _write(manifest_path, manifest_body)

    return {
        "schema": SCHEMA,
        "mode": "activate",
        "activation_id": act_id,
        "target": str(target),
        "entry": str(target / ACTIVATION_DIR / ENTRY_FILE),
        "manifest": str(manifest_path),
        "actions": performed,
        "preserved_paths": preserve_notes,
        "owned_paths": receipt["owned_paths"],
        "proteus_source": str(proteus_source),
        "runtime_pythonpath": str(pythonpath),
    }


def remove_activation(target: Path, *, dry_run: bool = False) -> dict[str, Any]:
    target = target.resolve()
    manifest_path = target / ACTIVATION_DIR / ACTIVATION_MANIFEST
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"No Proteus activation manifest at {manifest_path}. "
            "Refusing to remove arbitrary project files."
        )
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"corrupt activation manifest: {exc}") from exc
    owned = list(data.get("owned_paths") or [])
    if not owned:
        raise RuntimeError("activation manifest has empty owned_paths; refusing remove")

    actions: list[dict[str, str]] = []
    # Remove files deepest-first; handle hooks.json specially
    for rel in sorted(owned, key=lambda r: r.count("/"), reverse=True):
        path = target / rel
        if rel == ".cursor/hooks.json" and path.is_file():
            text = read_text_utf8(path)
            try:
                updated = strip_proteus_hooks(text)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"cannot strip hooks.json: {exc}") from exc
            if dry_run:
                actions.append({"path": rel, "action": "would_merge" if updated else "would_remove", "reason": "strip proteus_hook"})
            elif updated is None:
                path.unlink()
                actions.append({"path": rel, "action": "remove", "reason": "hooks.json was proteus-only"})
            else:
                _write(path, updated)
                actions.append({"path": rel, "action": "merge", "reason": "stripped proteus_hook; preserved others"})
            continue
        if not path.exists():
            actions.append({"path": rel, "action": "skip_exists", "reason": "already absent"})
            continue
        if dry_run:
            actions.append({"path": rel, "action": "would_remove", "reason": "owned by activation"})
            continue
        if path.is_file():
            path.unlink()
            actions.append({"path": rel, "action": "remove", "reason": "owned by activation"})
        else:
            actions.append({"path": rel, "action": "skip_exists", "reason": "not a file; left in place"})

    if not dry_run:
        # Clean empty Proteus-created directories (best-effort)
        for rel in (
            ".cursor/hooks",
            ".cursor/commands",
            ".cursor/skills/proteus-checkpoint",
            ".cursor/skills/proteus-correction",
            ".cursor/skills/proteus-reentry",
            ".cursor/skills/proteus-world",
            ".cursor/skills",
            ".cursor/rules",
            ".cursor",
            "state",
            ACTIVATION_DIR,
        ):
            d = target / rel
            if d.is_dir():
                try:
                    next(d.iterdir())
                except StopIteration:
                    d.rmdir()

    return {
        "schema": SCHEMA,
        "mode": "dry_run_remove" if dry_run else "remove",
        "target": str(target),
        "activation_id": data.get("activation_id"),
        "actions": actions,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="proteus.activate",
        description="Activate or remove a Proteus Cursor project mount on an existing project.",
    )
    p.add_argument("--project", required=True, help="Target project directory")
    p.add_argument("--dry-run", action="store_true", help="Inspect and plan; write nothing")
    p.add_argument("--remove", action="store_true", help="Remove Proteus-owned mount material only")
    p.add_argument("--run-id", default=None, help="Optional run id for provenance")
    p.add_argument("--json", action="store_true", help="Print result as JSON only")
    args = p.parse_args(argv)

    target = Path(args.project)
    try:
        if args.remove:
            result = remove_activation(target, dry_run=args.dry_run)
        else:
            result = activate(target, dry_run=args.dry_run, run_id=args.run_id)
    except (FileNotFoundError, NotADirectoryError, RuntimeError, ValueError) as exc:
        err = {"ok": False, "error": str(exc)}
        print(json.dumps(err, indent=2), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
        if not args.remove and not args.dry_run:
            entry = result.get("entry")
            if entry:
                print(f"\nEntry instructions: {entry}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
