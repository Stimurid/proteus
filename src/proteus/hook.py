from __future__ import annotations

import json
import os
import sys
import time

from proteus.control import maybe_followup
from proteus.events import append_event, base_event, load_project_orientation, write_active_card
from proteus.hook_identity import resolve_event_identity
from proteus.process_marker import cursor_host_process_marker


def _read_payload() -> tuple[bytes, dict]:
    buf = getattr(sys.stdin, "buffer", sys.stdin)
    raw = buf.read()
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not raw:
        return b"", {}
    try:
        parsed = json.loads(raw.decode("utf-8"))
        if isinstance(parsed, dict):
            return raw, parsed
        return raw, {"_parse_error": True, "_bytes": len(raw), "_json_type": type(parsed).__name__}
    except Exception:
        return raw, {"_parse_error": True, "_bytes": len(raw)}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    raw, payload = _read_payload()
    identity = resolve_event_identity(payload, argv)
    hook = identity["hook_event_name"]
    extra = {
        "event_name_source": identity["event_name_source"],
        "event_name_stdin": identity["event_name_stdin"],
        "event_name_argv": identity["event_name_argv"],
        "stdin_byte_count": len(raw),
        "process_marker": cursor_host_process_marker(),
    }
    evidence_class = os.environ.get("PROTEUS_EVIDENCE_CLASS")
    if evidence_class:
        extra["evidence_class"] = evidence_class
    if identity["conflict"]:
        extra["event_name_conflict"] = True
        extra["event_name_conflict_detail"] = identity["conflict_detail"]
        extra["status"] = "CONFLICT"
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
