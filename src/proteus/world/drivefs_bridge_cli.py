"""Command line entry point for the DriveFS delivery bridge.

Run as ``python -m proteus.world.drivefs_bridge_cli <command>``.

Exit codes are the scheduler contract:
    0  nothing to do, or everything the pass attempted succeeded
    1  at least one hard delivery failure
    2  the DriveFS target could not be validated (mount gone, wrong folder)
    3  usage / configuration error

The target is supplied as a UTF-8 JSON config and never as a command-line
literal, because ``powershell.exe`` 5.1 reads a BOM-less ``.ps1`` as ANSI and
mangles the Cyrillic folder name on the way through.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

if __package__ in (None, ""):  # pragma: no cover - direct-script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from proteus.world.drivefs_bridge import (
    TARGET_OK,
    DriveFsTarget,
    cloud_verify_queue,
    default_ledger_dir,
    import_cloud_presence,
    import_cloud_receipt,
    plan_stage,
    run_stage,
    scan_foreign_artifacts,
    validate_target,
    write_summary,
)
from proteus.world.store import WorldStore


def _emit(obj: object) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n")


def _refresh_summary(ledger_dir: Path, target, status: str) -> Path:
    """Regenerate the readable summary after anything that changes the ledger.

    The summary is derived; forgetting to rebuild it leaves a stale count on
    disk that reads as an authoritative claim about delivery.
    """
    return write_summary(
        ledger_dir,
        {
            "status": status,
            "exit_code": 0,
            "host": socket.gethostname(),
            "target": validate_target(target),
            "plan": plan_stage(WorldStore(), ledger_dir),
        },
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="drivefs-bridge", description=__doc__)
    ap.add_argument("--config", required=True, help="UTF-8 JSON target config")
    ap.add_argument("--ledger-dir", default=None, help="default: ~/.aiye/drivefs_bridge")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="validate the DriveFS target, write nothing")
    p_plan = sub.add_parser("plan", help="show what WOULD be staged (pure read)")
    p_plan.add_argument("--batch-cap", type=int, default=8)

    p_stage = sub.add_parser("stage", help="stage one bounded batch into DriveFS")
    p_stage.add_argument("--batch-cap", type=int, default=8)
    p_stage.add_argument("--max-bytes", type=int, default=64 * 1024 * 1024)
    p_stage.add_argument("--max-seconds", type=int, default=300)
    p_stage.add_argument("--dry-run", action="store_true")

    sub.add_parser("queue", help="records awaiting independent cloud verification")
    sub.add_parser("summary", help="regenerate the readable DRIVEFS_SUMMARY.md")

    p_imp = sub.add_parser("import-receipt", help="promote STAGED_LOCAL to CLOUD_VERIFIED")
    p_imp.add_argument("receipt", help="path to a proteus.drivefs_cloud_verification.v0.1 JSON")

    p_pres = sub.add_parser(
        "import-presence",
        help="record CLOUD_PRESENT (provider sees name+parent+length); does NOT verify bytes",
    )
    p_pres.add_argument("evidence", help="path to a proteus.drivefs_cloud_presence.v0.1 JSON")

    args = ap.parse_args(argv)
    ledger_dir = Path(args.ledger_dir) if args.ledger_dir else default_ledger_dir()

    try:
        target = DriveFsTarget.from_config(args.config)
    except (OSError, ValueError, KeyError) as exc:
        _emit({"status": "CONFIG_ERROR", "error": f"{type(exc).__name__}: {exc}"})
        return 3

    if args.cmd == "status":
        v = validate_target(target)
        v["foreign_artifacts"] = scan_foreign_artifacts(target, ledger_dir) if v["status"] == TARGET_OK else []
        v["cloud_verify_pending"] = len(cloud_verify_queue(ledger_dir))
        _emit(v)
        return 0 if v["status"] == TARGET_OK else 2

    if args.cmd == "plan":
        plan = plan_stage(WorldStore(), ledger_dir, batch_cap=args.batch_cap)
        plan["to_stage"] = [
            {k: m.get(k) for k in ("entity_id", "content_sha256", "bundle_sha256",
                                   "bundle_bytes", "generated_utc")}
            for m in plan["to_stage"]
        ]
        _emit(plan)
        return 0

    if args.cmd == "stage":
        s = run_stage(
            target=target,
            ledger_dir=ledger_dir,
            batch_cap=args.batch_cap,
            max_bytes=args.max_bytes,
            max_seconds=args.max_seconds,
            dry_run=args.dry_run,
        )
        _emit(s)
        return int(s.get("exit_code", 1))

    if args.cmd == "queue":
        q = cloud_verify_queue(ledger_dir)
        _emit({"pending": len(q), "records": q})
        return 0

    if args.cmd == "import-receipt":
        try:
            receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            _emit({"status": "RECEIPT_READ_ERROR", "error": str(exc)})
            return 3
        res = import_cloud_receipt(ledger_dir, receipt)
        _emit(res)
        _refresh_summary(ledger_dir, target, "CLOUD_RECEIPT_IMPORTED")
        return 0 if res["ok"] else 1

    if args.cmd == "import-presence":
        try:
            evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            _emit({"status": "EVIDENCE_READ_ERROR", "error": str(exc)})
            return 3
        items = evidence if isinstance(evidence, list) else [evidence]
        results = [import_cloud_presence(ledger_dir, e) for e in items]
        _emit({"imported": sum(1 for r in results if r["ok"]), "results": results})
        _refresh_summary(ledger_dir, target, "CLOUD_PRESENCE_IMPORTED")
        return 0 if all(r["ok"] for r in results) else 1

    if args.cmd == "summary":
        p = _refresh_summary(ledger_dir, target, "SUMMARY_REFRESHED")
        _emit({"summary_path": str(p)})
        return 0

    _emit({"status": "UNKNOWN_COMMAND", "cmd": args.cmd})
    return 3


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
