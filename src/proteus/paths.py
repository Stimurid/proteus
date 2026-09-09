from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    return Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())


def proteus_home() -> Path:
    return Path(os.environ.get("PROTEUS_HOME") or (home() / ".proteus"))


def cursor_user_dir() -> Path:
    return home() / ".cursor"


def telemetry_day_dir(day: str) -> Path:
    d = proteus_home() / "telemetry" / "cursor" / day
    d.mkdir(parents=True, exist_ok=True)
    return d


def spool_path(day: str) -> Path:
    return telemetry_day_dir(day) / "events.jsonl"


def observatory_local() -> Path:
    d = proteus_home() / "observatory"
    d.mkdir(parents=True, exist_ok=True)
    return d


def queue_dir() -> Path:
    d = proteus_home() / "control" / "queue"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ack_dir() -> Path:
    d = proteus_home() / "control" / "ack"
    d.mkdir(parents=True, exist_ok=True)
    return d


def active_runs_path() -> Path:
    p = proteus_home() / "runs"
    p.mkdir(parents=True, exist_ok=True)
    return p / "active.json"


def machine_id_path() -> Path:
    return proteus_home() / "machine_id"


def host_install_dir() -> Path:
    d = proteus_home() / "host" / "cursor"
    d.mkdir(parents=True, exist_ok=True)
    return d
