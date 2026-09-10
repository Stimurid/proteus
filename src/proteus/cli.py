from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .activate import activate, remove_activation
from .control import enqueue, list_queue
from .flush import flush
from .install_cursor import REPO_ROOT, install


def cmd_enqueue(ns: argparse.Namespace) -> None:
    path = enqueue(ns.action, ns.instruction, target_run=ns.run_id, mode=ns.mode)
    print(path)


def cmd_queue(_ns: argparse.Namespace) -> None:
    print(json.dumps(list_queue(), indent=2))


def cmd_probe_cli(_ns: argparse.Namespace) -> None:
    found = shutil.which("agent")
    cursor = shutil.which("cursor")
    print(
        json.dumps(
            {
                "agent_on_path": found,
                "cursor_on_path": cursor,
                "acp": "NOT_PROBED_NO_AGENT_BINARY",
                "note": "Cursor Agent CLI `agent` was not on PATH during first run host inspection.",
            },
            indent=2,
        )
    )


def cmd_activate(ns: argparse.Namespace) -> None:
    target = Path(ns.project)
    if ns.remove:
        result = remove_activation(target, dry_run=ns.dry_run)
    else:
        result = activate(target, dry_run=ns.dry_run, run_id=ns.run_id)
    print(json.dumps(result, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(prog="proteus")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enqueue")
    e.add_argument("--action", required=True)
    e.add_argument("--instruction", required=True)
    e.add_argument("--run-id")
    e.add_argument("--mode", default="SAME_SESSION")
    e.set_defaults(func=cmd_enqueue)
    q = sub.add_parser("queue")
    q.set_defaults(func=cmd_queue)
    f = sub.add_parser("flush")
    f.set_defaults(func=lambda ns: print(json.dumps(flush(), indent=2)))
    c = sub.add_parser("probe-cli")
    c.set_defaults(func=cmd_probe_cli)
    a = sub.add_parser("activate", help="Mount Proteus on an existing Cursor project")
    a.add_argument("--project", required=True)
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--remove", action="store_true")
    a.add_argument("--run-id", default=None)
    a.set_defaults(func=cmd_activate)
    ns = p.parse_args()
    ns.func(ns)


if __name__ == "__main__":
    sys.path.insert(0, str(REPO_ROOT / "src"))
    main()
