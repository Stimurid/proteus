from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    return Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())


def proteus_home() -> Path:
    return Path(os.environ.get("PROTEUS_HOME") or (home() / ".proteus"))


def cursor_user_dir() -> Path:
    override = os.environ.get("PROTEUS_CURSOR_USER_DIR")
    if override:
        return Path(override)
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


def aiye_home() -> Path:
    """Subject-level Aiye home. Created only when world memory needs a local root.

    No pre-existing ``~/.aiye`` / Archivarius object-home was found on this host
    (2026-09-10). Override with ``AIYE_HOME``.
    """
    return Path(os.environ.get("AIYE_HOME") or (home() / ".aiye"))


def world_root() -> Path:
    """Entity substrate root. Override with ``PROTEUS_WORLD_ROOT``."""
    override = os.environ.get("PROTEUS_WORLD_ROOT")
    if override:
        return Path(override)
    return aiye_home() / "world"
