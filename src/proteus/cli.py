from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .activate import activate, remove_activation
from .activate_codex import activate as activate_codex
from .activate_codex import remove_activation as remove_codex_activation
from .control import enqueue, list_queue
from .flush import flush
from .install_cursor import REPO_ROOT, install
from .world import (
    MemoryScope,
    WorldStore,
    classify_and_route,
    ensure_world_home,
    export_entity_carrier_bundle,
    import_entity_carrier_bundle,
    rebuild_index,
    reconcile_entity,
    recover_entity_from_carrier,
)
from .world.archivarius import resolve_via_bridge
from .world.store import Provenance
from .secrets import delete_secret, describe_secret, put_secret, redact
from .secrets.broker import SecretNotFoundError, get_secret
from .capsule import DEFAULT_MAX_CHARS, build_capsule


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


def cmd_activate_codex(ns: argparse.Namespace) -> None:
    target = Path(ns.project)
    if ns.remove:
        result = remove_codex_activation(target, dry_run=ns.dry_run)
    else:
        aiye = Path(ns.aiye_home).expanduser() if ns.aiye_home else None
        result = activate_codex(
            target,
            dry_run=ns.dry_run,
            run_id=ns.run_id,
            aiye_home=aiye,
        )
    print(json.dumps(result, indent=2))


def cmd_capsule(ns: argparse.Namespace) -> None:
    result = build_capsule(
        Path(ns.project), Path(ns.out), max_chars=ns.max_chars
    )
    print(
        json.dumps(
            {
                "project": str(result.project),
                "output": str(result.output),
                "chars": result.chars,
                "included_documents": list(result.included_documents),
            },
            indent=2,
        )
    )


def cmd_world(ns: argparse.Namespace) -> None:
    ensure_world_home()
    store = WorldStore()
    if ns.world_cmd == "ensure-home":
        print(json.dumps(ensure_world_home(), indent=2))
        return
    if ns.world_cmd == "create":
        print(
            json.dumps(
                store.create_entity(
                    ns.name,
                    entity_id=ns.entity_id,
                    aliases=ns.alias or [],
                ),
                indent=2,
            )
        )
        return
    if ns.world_cmd == "resolve":
        print(json.dumps(store.resolve(ns.query), indent=2, ensure_ascii=False))
        return
    if ns.world_cmd == "mount":
        print(json.dumps(resolve_via_bridge(ns.query), indent=2, ensure_ascii=False))
        return
    if ns.world_cmd == "route":
        prov = Provenance(
            observer=ns.observer or "proteus.cli",
            project=ns.project,
            run_id=ns.run_id,
            source=ns.source,
            kind=ns.kind,
            confidence=ns.confidence,
        )
        result = classify_and_route(
            scope=MemoryScope.parse(ns.scope),
            text=ns.text,
            provenance=prov,
            entity_query=ns.entity,
            entity_id=ns.entity_id,
            topic=ns.topic,
            status=ns.status,
            project_path=ns.project,
            secret_uri=ns.secret_uri,
            secret_label=ns.secret_label,
            world=store,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    if ns.world_cmd == "reconcile":
        print(json.dumps(reconcile_entity(ns.entity_id, world=store), indent=2))
        return
    if ns.world_cmd == "rebuild-index":
        print(json.dumps(rebuild_index(world=store), indent=2))
        return
    if ns.world_cmd == "export-carrier":
        meta = export_entity_carrier_bundle(
            ns.entity_id, world=store, out_path=Path(ns.out)
        )
        meta.pop("payload", None)
        print(json.dumps(meta, indent=2))
        return
    if ns.world_cmd == "import-carrier":
        print(
            json.dumps(
                import_entity_carrier_bundle(
                    Path(ns.path), world=store, expect_entity_id=ns.entity_id
                ),
                indent=2,
            )
        )
        return
    if ns.world_cmd == "recover-carrier":
        dest = WorldStore(root=Path(ns.dest_world)) if ns.dest_world else WorldStore()
        print(
            json.dumps(
                recover_entity_from_carrier(
                    Path(ns.path), dest_world=dest, expect_entity_id=ns.entity_id
                ),
                indent=2,
            )
        )
        return
    if ns.world_cmd == "add-alias":
        print(
            json.dumps(
                store.add_aliases(ns.entity_id, ns.alias or []),
                indent=2,
                ensure_ascii=False,
            )
        )
        return
    raise SystemExit(f"Unknown world command: {ns.world_cmd}")


def cmd_secret(ns: argparse.Namespace) -> None:
    if ns.secret_cmd == "put":
        # plaintext only via env or file — never echoed back
        if ns.from_env:
            import os

            plaintext = os.environ.get(ns.from_env)
            if not plaintext:
                raise SystemExit(f"env {ns.from_env} empty/missing")
        elif ns.from_file:
            plaintext = Path(ns.from_file).read_text(encoding="utf-8").rstrip("\n")
        else:
            raise SystemExit("provide --from-env or --from-file")
        meta = put_secret(ns.uri, plaintext, label=ns.label)
        print(json.dumps(meta, indent=2))
        return
    if ns.secret_cmd == "describe":
        print(json.dumps(describe_secret(ns.uri), indent=2))
        return
    if ns.secret_cmd == "get":
        # Explicit dangerous path: writes only to --out file, never stdout
        if not ns.out:
            raise SystemExit("secret get requires --out path (never prints value)")
        try:
            value = get_secret(ns.uri)
        except SecretNotFoundError as e:
            raise SystemExit(str(e)) from e
        Path(ns.out).write_text(value, encoding="utf-8")
        print(json.dumps({"ok": True, "uri": ns.uri, "out": ns.out, "bytes": len(value.encode("utf-8"))}))
        return
    if ns.secret_cmd == "delete":
        print(json.dumps({"deleted": delete_secret(ns.uri), "uri": ns.uri}))
        return
    raise SystemExit(f"Unknown secret command: {ns.secret_cmd}")


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

    ac = sub.add_parser(
        "activate-codex",
        help="Mount Proteus world-memory morphology on a Codex project (foreign carrier)",
    )
    ac.add_argument("--project", required=True)
    ac.add_argument("--dry-run", action="store_true")
    ac.add_argument("--remove", action="store_true")
    ac.add_argument("--run-id", default=None)
    ac.add_argument("--aiye-home", default=None)
    ac.set_defaults(func=cmd_activate_codex)

    cap = sub.add_parser(
        "capsule",
        help="Create a compact, source-grounded Markdown handoff capsule without mutating the project",
    )
    cap.add_argument("--project", required=True, help="existing coding project to inspect")
    cap.add_argument("--out", required=True, help="Markdown capsule path (normally outside the target project)")
    cap.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    cap.set_defaults(func=cmd_capsule)

    w = sub.add_parser("world", help="Shared world / entity memory")
    wsub = w.add_subparsers(dest="world_cmd", required=True)
    wh = wsub.add_parser("ensure-home")
    wh.set_defaults(func=cmd_world)
    wc = wsub.add_parser("create")
    wc.add_argument("--name", required=True)
    wc.add_argument("--entity-id")
    wc.add_argument("--alias", action="append", default=[])
    wc.set_defaults(func=cmd_world)
    wr = wsub.add_parser("resolve")
    wr.add_argument("query")
    wr.set_defaults(func=cmd_world)
    wm = wsub.add_parser("mount")
    wm.add_argument("query")
    wm.set_defaults(func=cmd_world)
    wrt = wsub.add_parser("route")
    wrt.add_argument("--scope", required=True)
    wrt.add_argument("--text", required=True)
    wrt.add_argument("--entity")
    wrt.add_argument("--entity-id")
    wrt.add_argument("--topic")
    wrt.add_argument("--status", default="current")
    wrt.add_argument("--project")
    wrt.add_argument("--observer")
    wrt.add_argument("--run-id")
    wrt.add_argument("--source")
    wrt.add_argument("--kind", default="observation")
    wrt.add_argument("--confidence")
    wrt.add_argument("--secret-uri")
    wrt.add_argument("--secret-label")
    wrt.set_defaults(func=cmd_world)
    wrec = wsub.add_parser("reconcile")
    wrec.add_argument("--entity-id", required=True)
    wrec.set_defaults(func=cmd_world)
    wri = wsub.add_parser("rebuild-index")
    wri.set_defaults(func=cmd_world)
    wex = wsub.add_parser("export-carrier")
    wex.add_argument("--entity-id", required=True)
    wex.add_argument("--out", required=True)
    wex.set_defaults(func=cmd_world)
    wim = wsub.add_parser("import-carrier")
    wim.add_argument("--path", required=True)
    wim.add_argument("--entity-id")
    wim.set_defaults(func=cmd_world)
    wrecov = wsub.add_parser("recover-carrier")
    wrecov.add_argument("--path", required=True)
    wrecov.add_argument("--dest-world", required=True)
    wrecov.add_argument("--entity-id")
    wrecov.set_defaults(func=cmd_world)
    wal = wsub.add_parser("add-alias")
    wal.add_argument("--entity-id", required=True)
    wal.add_argument("--alias", action="append", default=[])
    wal.set_defaults(func=cmd_world)

    s = sub.add_parser("secret", help="Protected secret broker (no plaintext in stdout for put)")
    ssub = s.add_subparsers(dest="secret_cmd", required=True)
    sp = ssub.add_parser("put")
    sp.add_argument("--uri", required=True)
    sp.add_argument("--label")
    sp.add_argument("--from-env")
    sp.add_argument("--from-file")
    sp.set_defaults(func=cmd_secret)
    sd = ssub.add_parser("describe")
    sd.add_argument("--uri", required=True)
    sd.set_defaults(func=cmd_secret)
    sg = ssub.add_parser("get")
    sg.add_argument("--uri", required=True)
    sg.add_argument("--out", required=True)
    sg.set_defaults(func=cmd_secret)
    sdel = ssub.add_parser("delete")
    sdel.add_argument("--uri", required=True)
    sdel.set_defaults(func=cmd_secret)

    ns = p.parse_args()
    ns.func(ns)


if __name__ == "__main__":
    sys.path.insert(0, str(REPO_ROOT / "src"))
    main()
