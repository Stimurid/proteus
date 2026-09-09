from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .events import append_event
from .paths import ack_dir, queue_dir
from .redact import redact

ALLOWED_ACTIONS = {
    "CONTINUE",
    "EXECUTE_NEXT",
    "RUN_TEST",
    "CHECKPOINT",
    "MOUNT_PROJECT",
    "REPAIR",
    "PAUSE_AFTER",
    "STATUS_ONLY",
    "TEST_STEER",
}


def enqueue(
    action: str,
    instruction: str,
    *,
    target_run: str | None = None,
    mode: str = "SAME_SESSION",
    issuer: str = "local-cli",
) -> Path:
    action = action.upper()
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"unknown action {action}")
    rec = {
        "command_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "issuer": issuer,
        "provenance": "local filesystem queue; not Drive until transport exists",
        "target_host": "cursor",
        "target_RUN_ID": target_run,
        "requested_action": action,
        "instruction": instruction,
        "mode_preference": mode,
        "priority": 10,
        "status": "QUEUED",
        "safety_class": "bounded-non-destructive",
    }
    path = queue_dir() / f"{rec['command_id']}.json"
    path.write_text(json.dumps(redact(rec), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _claim(path: Path) -> dict | None:
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if rec.get("status") != "QUEUED":
        return None
    rec["status"] = "CLAIMED"
    rec["claimed_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec


def maybe_followup(payload: dict) -> str | None:
    loop_count = int(payload.get("loop_count") or 0)
    if loop_count >= 1:
        return None
    status = payload.get("status")
    if status and status not in ("completed", "complete", None):
        return None
    queued = sorted(queue_dir().glob("*.json"))
    for path in queued:
        rec = _claim(path)
        if not rec:
            continue
        if rec.get("mode_preference") not in ("SAME_SESSION", "AUTO"):
            rec["status"] = "QUEUED"
            path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
            continue
        rec["status"] = "SENT"
        rec["channel"] = "STOP_HOOK"
        path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        ack = ack_dir() / f"{rec['command_id']}.json"
        ack.write_text(
            json.dumps(
                {
                    "command_id": rec["command_id"],
                    "status": "ACKNOWLEDGED_DISPATCH",
                    "channel": "STOP_HOOK",
                    "at": datetime.now(timezone.utc).isoformat(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        append_event(
            {
                "schema_version": "0.1.0",
                "event_id": str(uuid.uuid4()),
                "hook_event_name": "external_command_sent",
                "command_id": rec["command_id"],
                "channel": "STOP_HOOK",
                "status": "SENT",
            }
        )
        instruction = rec.get("instruction") or rec.get("requested_action")
        return (
            "[PROTEUS EXTERNAL COMMAND]\n"
            f"command_id={rec['command_id']}\n"
            f"action={rec.get('requested_action')}\n"
            "Acknowledge this command in the next turn by writing status ACKNOWLEDGED "
            f"to the run receipt if you can act; then execute:\n{instruction}"
        )
    return None


def list_queue() -> list[dict]:
    items = []
    for path in sorted(queue_dir().glob("*.json")):
        try:
            items.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return items
