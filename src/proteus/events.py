from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import SCHEMA_VERSION, HOST
from .paths import active_runs_path, machine_id_path, observatory_local, spool_path
from .redact import redact


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def day_stamp(dt: datetime | None = None) -> str:
    return (dt or utc_now()).strftime("%Y-%m-%d")


def machine_id() -> str:
    p = machine_id_path()
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    p.parent.mkdir(parents=True, exist_ok=True)
    mid = str(uuid.uuid4())
    p.write_text(mid, encoding="utf-8")
    return mid


def append_event(event: dict[str, Any]) -> Path:
    event = redact(event)
    dt = utc_now()
    path = spool_path(day_stamp(dt))
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def write_active_card(card: dict[str, Any]) -> None:
    card = redact(card)
    path = active_runs_path()
    path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    dest = observatory_local() / "00_ACTIVE_RUNS" / "current.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")


def base_event(hook_name: str, payload: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    dt = utc_now()
    local = datetime.now().astimezone()
    ev = {
        "schema_version": SCHEMA_VERSION,
        "event_id": str(uuid.uuid4()),
        "timestamp_utc": dt.isoformat(),
        "timestamp_local": local.isoformat(),
        "host": HOST,
        "machine_id": machine_id(),
        "cursor_version": os.environ.get("CURSOR_VERSION") or payload.get("cursor_version"),
        "workspace_roots": payload.get("workspace_roots") or payload.get("roots"),
        "project_id": payload.get("project_id"),
        "RUN_ID": os.environ.get("PROTEUS_RUN_ID") or payload.get("generation_id") or payload.get("session_id"),
        "conversation_id": payload.get("conversation_id") or payload.get("session_id"),
        "session_id": payload.get("session_id"),
        "generation_id": payload.get("generation_id"),
        "model": payload.get("model"),
        "hook_event_name": hook_name,
        "stage": "DETERMINISTIC",
        "status": payload.get("status") or hook_name.upper(),
        "transcript_path": os.environ.get("CURSOR_TRANSCRIPT_PATH") or payload.get("transcript_path"),
        "cwd": os.getcwd(),
        "cursor_project_dir": os.environ.get("CURSOR_PROJECT_DIR"),
    }
    if extra:
        ev.update(extra)
    return ev


def load_project_orientation(root: Path | None) -> str:
    if root is None:
        env = os.environ.get("CURSOR_PROJECT_DIR")
        root = Path(env) if env else Path.cwd()
    state = root / "state"
    chunks = []
    for name in ("IDENTITY.md", "CURRENT.md", "FRONTIER.md", "UNRESOLVED.md", "DECISIONS.md"):
        p = state / name
        if p.exists():
            text = p.read_text(encoding="utf-8")[:2500]
            chunks.append(f"## {name}\n{text}")
    if not chunks:
        return ""
    return (
        "PROTEUS durable project orientation (loaded by host hook; not a complete memory dump).\n\n"
        + "\n\n".join(chunks)
    )
