from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .paths import cursor_user_dir, host_install_dir, proteus_home


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = REPO_ROOT / "hosts" / "cursor" / "templates"
PYTHON = sys.executable

USER_HOOK_TIMEOUTS = {
    "workspaceOpen": 15,
    "sessionStart": 15,
    "sessionEnd": 15,
    "preCompact": 15,
    "stop": 15,
    "afterFileEdit": 10,
    "postToolUseFailure": 10,
}


def hook_command(event_name: str, *, project: bool = False) -> str:
    prefix = ".cursor\\hooks\\proteus_hook.cmd" if project else "hooks\\proteus_hook.cmd"
    return f"{prefix} --hook-event {event_name}"


def user_hook_entries() -> dict:
    entries: dict = {}
    for name, timeout in USER_HOOK_TIMEOUTS.items():
        item = {"command": hook_command(name), "timeout": timeout}
        if name == "stop":
            item["loop_limit"] = 2
        entries[name] = [item]
    return entries


def proteus_hook_cmd_text(*, python: str, pythonpath: str) -> str:
    return "\r\n".join(
        [
            "@echo off",
            "set PYTHONIOENCODING=utf-8",
            f"set PYTHONPATH={pythonpath}",
            f'"{python}" -m proteus.hook %*',
            "",
        ]
    )


def _sha(path: Path) -> str:
    if not path.exists():
        return "ABSENT"
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def snapshot_host(backup_dir: Path) -> dict:
    backup_dir.mkdir(parents=True, exist_ok=True)
    targets = {
        "user_hooks_json": cursor_user_dir() / "hooks.json",
        "user_hooks_dir": cursor_user_dir() / "hooks",
    }
    record = {"at": datetime.now(timezone.utc).isoformat(), "files": {}}
    for name, path in targets.items():
        rec = {"path": str(path), "exists": path.exists(), "sha256_16": _sha(path) if path.is_file() else None}
        dest = backup_dir / name
        if path.is_file():
            shutil.copy2(path, dest)
        elif path.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(path, dest)
        record["files"][name] = rec
    (backup_dir / "SNAPSHOT.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def install(project_root: Path, *, run_id: str, backup_dir: Path) -> dict:
    project_root = project_root.resolve()
    snap = snapshot_host(backup_dir)
    installed = []

    # copy hook runtime
    hook_src = REPO_ROOT / "src" / "proteus"
    hook_dst = host_install_dir() / "src" / "proteus"
    if hook_dst.exists():
        shutil.rmtree(hook_dst)
    shutil.copytree(hook_src, hook_dst)
    installed.append(str(hook_dst))

    cmd = host_install_dir() / "proteus_hook.cmd"
    _write(
        cmd,
        proteus_hook_cmd_text(python=PYTHON, pythonpath=str(host_install_dir() / "src")),
    )
    installed.append(str(cmd))

    user_hook_cmd = cursor_user_dir() / "hooks" / "proteus_hook.cmd"
    user_hook_cmd.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cmd, user_hook_cmd)
    installed.append(str(user_hook_cmd))

    hooks_json = {"version": 1, "hooks": user_hook_entries()}
    existing = cursor_user_dir() / "hooks.json"
    if existing.exists():
        try:
            prev = json.loads(existing.read_text(encoding="utf-8"))
        except Exception:
            prev = {"version": 1, "hooks": {}}
        merged = prev if isinstance(prev, dict) else {"version": 1, "hooks": {}}
        hooks_map = merged.setdefault("hooks", {})
        for k, v in hooks_json["hooks"].items():
            current = hooks_map.get(k) or []
            current = [h for h in current if "proteus_hook" not in str(h)]
            current.extend(v)
            hooks_map[k] = current
        merged["version"] = merged.get("version") or 1
        payload = merged
    else:
        payload = hooks_json
    _write(existing, json.dumps(payload, indent=2))
    installed.append(str(existing))

    # project incarnation from templates
    mapping = {
        "AGENTS.md": project_root / "AGENTS.md",
        "CLAUDE.md": project_root / "CLAUDE.md",
        "rules/proteus-orientation.mdc": project_root / ".cursor" / "rules" / "proteus-orientation.mdc",
        "rules/proteus-anti-reduction.mdc": project_root / ".cursor" / "rules" / "proteus-anti-reduction.mdc",
        "rules/proteus-mutation.mdc": project_root / ".cursor" / "rules" / "proteus-mutation.mdc",
        "skills/proteus-checkpoint/SKILL.md": project_root / ".cursor" / "skills" / "proteus-checkpoint" / "SKILL.md",
        "skills/proteus-correction/SKILL.md": project_root / ".cursor" / "skills" / "proteus-correction" / "SKILL.md",
        "skills/proteus-reentry/SKILL.md": project_root / ".cursor" / "skills" / "proteus-reentry" / "SKILL.md",
        "hooks.json": project_root / ".cursor" / "hooks.json",
    }
    for rel, dest in mapping.items():
        src = TEMPLATES / rel
        text = src.read_text(encoding="utf-8")
        text = text.replace("{{RUN_ID}}", run_id)
        text = text.replace("{{SOURCE_ROOT}}", str(REPO_ROOT))
        _write(dest, text)
        installed.append(str(dest))

    project_hook = project_root / ".cursor" / "hooks" / "proteus_hook.cmd"
    _write(
        project_hook,
        proteus_hook_cmd_text(python=PYTHON, pythonpath=str(host_install_dir() / "src")),
    )
    installed.append(str(project_hook))

    marker = project_root / "state" / "INCARNATION.md"
    _write(
        marker,
        (
            f"# Proteus Cursor incarnation\n\n"
            f"- RUN_ID: `{run_id}`\n"
            f"- installed_at: `{datetime.now(timezone.utc).isoformat()}`\n"
            f"- source_root: `{REPO_ROOT}`\n"
            f"- host: Cursor\n"
            f"- generated_from: `hosts/cursor/templates` + `src/proteus/install_cursor.py`\n"
            f"- backup: `{backup_dir}`\n"
        ),
    )
    installed.append(str(marker))

    receipt = {
        "receipt_id": f"INSTALL-{run_id}",
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_root": str(REPO_ROOT),
        "project_root": str(project_root),
        "python": PYTHON,
        "files_installed": installed,
        "snapshot": snap,
        "unrelated_settings_policy": "only merged proteus_hook entries into ~/.cursor/hooks.json; did not rewrite cli-config.json or mcp.json",
    }
    rec_path = proteus_home() / "receipts" / f"{run_id}.json"
    rec_path.parent.mkdir(parents=True, exist_ok=True)
    rec_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt


def uninstall_user_hooks() -> None:
    existing = cursor_user_dir() / "hooks.json"
    if not existing.exists():
        return
    data = json.loads(existing.read_text(encoding="utf-8"))
    hooks = data.get("hooks") or {}
    for k, lst in list(hooks.items()):
        hooks[k] = [h for h in lst if "proteus_hook" not in str(h)]
        if not hooks[k]:
            del hooks[k]
    existing.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project", default=str(REPO_ROOT))
    p.add_argument("--run-id", required=True)
    p.add_argument("--backup-dir", required=True)
    p.add_argument("--uninstall", action="store_true")
    args = p.parse_args()
    if args.uninstall:
        uninstall_user_hooks()
        print("uninstalled user proteus hooks")
        return
    rec = install(Path(args.project), run_id=args.run_id, backup_dir=Path(args.backup_dir))
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
