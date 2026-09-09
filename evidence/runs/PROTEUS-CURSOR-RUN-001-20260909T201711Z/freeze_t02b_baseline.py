"""Read-only T02b baseline freeze. Does not invoke proteus.hook."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(r"C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z")
TOKEN = "T02B-HOOKFIRE-ca8c800d-6c58-4acb-89cd-992145ebbbe9"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(path: Path) -> dict:
    data = path.read_bytes()
    lines = [ln for ln in data.decode("utf-8").splitlines() if ln.strip()]
    events = []
    bad = 0
    for ln in lines:
        try:
            events.append(json.loads(ln))
        except Exception:
            bad += 1
    last = events[-1] if events else {}
    named = []
    cursor_times = []
    for ev in events:
        name = ev.get("hook_event_name")
        if name and name != "unknown":
            named.append(
                {
                    "event_id": ev.get("event_id"),
                    "hook_event_name": name,
                    "timestamp_utc": ev.get("timestamp_utc"),
                    "session_id": ev.get("session_id"),
                    "event_name_source": ev.get("event_name_source"),
                    "evidence_class": ev.get("evidence_class"),
                }
            )
        marker = ev.get("process_marker") or {}
        ctime = marker.get("cursor_create_time_utc")
        if ctime:
            cursor_times.append(ctime)
    return {
        "path": str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "line_count": len(lines),
        "parsed_events": len(events),
        "non_json_lines": bad,
        "last_event_id": last.get("event_id"),
        "last_timestamp_utc": last.get("timestamp_utc"),
        "last_hook_event_name": last.get("hook_event_name"),
        "last_event_name_source": last.get("event_name_source"),
        "named_events": named,
        "last_process_marker": last.get("process_marker"),
        "seen_cursor_create_time_utc": sorted(set(cursor_times)),
    }


def main() -> None:
    t02 = json.loads((RUN / "T02_BASELINE.json").read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    spool_root = Path(os.path.expandvars(r"%USERPROFILE%\.proteus\telemetry\cursor"))
    obs_root = Path(os.path.expandvars(r"%USERPROFILE%\.proteus\observatory\10_CURSOR"))
    hooks = Path(os.path.expandvars(r"%USERPROFILE%\.cursor\hooks.json"))
    cmd = Path(os.path.expandvars(r"%USERPROFILE%\.cursor\hooks\proteus_hook.cmd"))

    spool_days = []
    for day in sorted(p for p in spool_root.iterdir() if p.is_dir()):
        evp = day / "events.jsonl"
        if evp.exists():
            spool_days.append(analyze(evp))
    obs_days = []
    if obs_root.exists():
        for day in sorted(p for p in obs_root.iterdir() if p.is_dir()):
            evp = day / "events.jsonl"
            if evp.exists():
                obs_days.append(analyze(evp))

    cursor_create = None
    for day in spool_days:
        times = day.get("seen_cursor_create_time_utc") or []
        if times:
            cursor_create = times[-1]
        marker = day.get("last_process_marker") or {}
        if marker.get("cursor_create_time_utc"):
            cursor_create = marker.get("cursor_create_time_utc")

    baseline = {
        "token": TOKEN,
        "cutoff_utc": now,
        "frozen_at_utc": now,
        "note": (
            "Events at or before cutoff_utc / matching these hashes are PRE-T02b. "
            "Do not treat them as T02b named restart fire. Do not inject proteus.hook to fake PASS. "
            "Original T02 stays PARTIAL."
        ),
        "t02_status_must_remain": "PARTIAL",
        "expected_named_events": ["sessionStart", "workspaceOpen"],
        "expected_event_name_source": ["argv", "stdin", "stdin+argv"],
        "exclusion_rules": [
            "timestamp_utc <= cutoff_utc",
            "event_id == last_event_id",
            "ids in simulated_named_ids_must_not_count or excluded_event_ids",
            "session_id == sim-001",
            "evidence_class in {test, simulated}",
            "hook_event_name not in {sessionStart, workspaceOpen}",
            "event_name_source in {none, conflict} or event_name_conflict true",
            "rows created by python -m proteus.hook or hand-appended JSONL",
            "same-session afterFileEdit/stop after freeze (including git commit) is not T02b PASS",
        ],
        "simulated_named_ids_must_not_count": t02["simulated_named_ids_must_not_count"],
        "excluded_event_ids": [t02["spool_days"][0]["last_event_id"]],
        "user_hooks_json": {
            "path": str(hooks),
            "sha256": sha256(hooks),
            "bytes": hooks.stat().st_size,
            "exists": True,
            "contains_proteus_hook": b"proteus_hook" in hooks.read_bytes(),
            "commands_include_hook_event_argv": "--hook-event" in hooks.read_text(encoding="utf-8"),
        },
        "user_hook_cmd": {
            "path": str(cmd),
            "sha256": sha256(cmd),
            "exists": True,
            "forwards_argv": "%*" in cmd.read_text(encoding="utf-8", errors="replace"),
        },
        "spool_days": spool_days,
        "observatory_days": obs_days,
        "cursor_create_time_utc_at_freeze": cursor_create,
        "cursor_create_time_note": (
            "Best-effort Toolhelp marker from spool process_marker fields; UNKNOWN if null. "
            "A change after reopen is compatible with a process boundary, not proof of a full quit."
        ),
        "day_dirs_present": [p.name for p in sorted(spool_root.iterdir()) if p.is_dir()],
    }
    outp = RUN / "T02b_BASELINE.json"
    outp.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(json.dumps({"wrote": str(outp), "cutoff_utc": now, "spool": [
        {
            "lines": d["line_count"],
            "sha256": d["sha256"],
            "last_event_id": d["last_event_id"],
            "last_hook": d["last_hook_event_name"],
            "last_source": d["last_event_name_source"],
            "named": len(d["named_events"]),
        }
        for d in spool_days
    ], "hooks_sha256": baseline["user_hooks_json"]["sha256"], "cursor_create_time_utc_at_freeze": cursor_create}, indent=2))


if __name__ == "__main__":
    main()
