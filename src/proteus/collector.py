"""Flush local telemetry cards. Drive transport is attempted only if a synced path exists."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from paths import observatory_local, proteus_home  # noqa: E402


def find_drive_observatory() -> Path | None:
    # Drive Desktop 'My Drive' on this machine was empty (2026-09-09). Do not invent a path.
    candidates = []
    home = Path.home()
    for name in ("My Drive", "Мой диск", "Google Drive"):
        p = home / name
        if p.exists():
            candidates.append(p)
    for c in candidates:
        hit = list(c.glob("**/00_ACTIVE_RUNS"))
        if hit:
            return hit[0].parent
    return None


def main():
    local = observatory_local()
    dest = find_drive_observatory()
    status = {
        "local": str(local),
        "drive_synced_path": str(dest) if dest else None,
        "transport": "DRIVE_SYNCED" if dest else "LOCAL_FALLBACK",
        "note": "Google Drive MCP was disconnected; Drive Desktop mirror had no files. Local observatory remains authoritative until transport is proven.",
    }
    if dest:
        src = local / "00_ACTIVE_RUNS"
        target = dest / "00_ACTIVE_RUNS"
        target.mkdir(parents=True, exist_ok=True)
        for f in src.glob("*.json"):
            shutil.copy2(f, target / f.name)
    status_path = proteus_home() / "runtime" / "collector-status.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
