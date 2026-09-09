from __future__ import annotations

import json
import sys
import time

from proteus.control import maybe_followup
from proteus.events import append_event, base_event, load_project_orientation, write_active_card


def _read_payload() -> dict:
    buf = getattr(sys.stdin, "buffer", sys.stdin)
    raw = buf.read()
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {"_parse_error": True, "_bytes": len(raw)}


def main() -> int:
    payload = _read_payload()
    hook = (
        payload.get("hook_event_name")
        or payload.get("event_name")
        or payload.get("hook")
        or "unknown"
    )
    extra = {}
    if hook in ("afterFileEdit", "afterShellExecution", "postToolUse"):
        extra["tool"] = payload.get("tool_name") or payload.get("tool")
        extra["file_path"] = payload.get("file_path") or payload.get("path")
    ev = base_event(hook, payload, extra)
    append_event(ev)
    write_active_card(
        {
            "host": "cursor",
            "workspace": ev.get("workspace_roots") or ev.get("cursor_project_dir") or ev.get("cwd"),
            "RUN_ID": ev.get("RUN_ID"),
            "conversation_id": ev.get("conversation_id"),
            "model": ev.get("model"),
            "last_event": ev.get("event_id"),
            "last_hook": hook,
            "status": ev.get("status"),
            "semantic_stage": {
                "value": "UNKNOWN",
                "note": "semantic analyzer not run this event; deterministic status only",
            },
            "transcript_path": ev.get("transcript_path"),
            "observatory_sync": "local_only",
        }
    )
    out: dict = {}
    if hook == "sessionStart":
        ctx = load_project_orientation(None)
        if ctx:
            out["additional_context"] = ctx
        out["env"] = {"PROTEUS_HOOKS": "1"}
    if hook == "stop":
        msg = maybe_followup(payload)
        if msg:
            out["followup_message"] = msg
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    sys.stdout.flush()
    time.sleep(0.08)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        sys.stdout.write("{}")
        sys.stdout.flush()
        time.sleep(0.08)
        raise SystemExit(0)
