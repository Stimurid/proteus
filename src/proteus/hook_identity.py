"""Resolve hook event identity from stdin payload and registration argv.

This is an interface for evidence, not a living organ: it names the Cursor
hook slot when the host tells us, and records UNKNOWN/CONFLICT when it does not.
It does not infer sessionStart/workspaceOpen/stop from timing.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

ARGV_FLAG = "--hook-event"
SOURCE_STDIN = "stdin"
SOURCE_ARGV = "argv"
SOURCE_BOTH = "stdin+argv"
SOURCE_NONE = "none"
SOURCE_CONFLICT = "conflict"
UNNAMED = "unknown"


def parse_hook_event_argv(argv: Sequence[str]) -> str | None:
    found: str | None = None
    i = 0
    while i < len(argv):
        a = argv[i]
        value: str | None = None
        if a == ARGV_FLAG and i + 1 < len(argv):
            value = argv[i + 1]
            i += 2
        elif a.startswith(ARGV_FLAG + "="):
            value = a.split("=", 1)[1]
            i += 1
        else:
            i += 1
            continue
        value = (value or "").strip()
        if not value:
            continue
        if found is not None and found != value:
            return None
        found = value
    return found


def stdin_event_name(payload: Mapping[str, Any]) -> str | None:
    if payload.get("_parse_error"):
        return None
    for key in ("hook_event_name", "event_name", "hook"):
        raw = payload.get(key)
        if not isinstance(raw, str):
            continue
        name = raw.strip()
        if not name or name.lower() == UNNAMED:
            continue
        return name
    return None


def resolve_event_identity(payload: Mapping[str, Any], argv: Sequence[str]) -> dict[str, Any]:
    stdin_name = stdin_event_name(payload)
    argv_name = parse_hook_event_argv(argv)
    out: dict[str, Any] = {
        "hook_event_name": UNNAMED,
        "event_name_source": SOURCE_NONE,
        "event_name_stdin": stdin_name,
        "event_name_argv": argv_name,
        "conflict": False,
        "conflict_detail": None,
    }
    if stdin_name and argv_name and stdin_name != argv_name:
        out["event_name_source"] = SOURCE_CONFLICT
        out["conflict"] = True
        out["conflict_detail"] = {
            "stdin": stdin_name,
            "argv": argv_name,
            "note": "registration argv and trusted stdin disagree; neither name is chosen",
        }
        return out
    if stdin_name and argv_name:
        out["hook_event_name"] = stdin_name
        out["event_name_source"] = SOURCE_BOTH
        return out
    if stdin_name:
        out["hook_event_name"] = stdin_name
        out["event_name_source"] = SOURCE_STDIN
        return out
    if argv_name:
        out["hook_event_name"] = argv_name
        out["event_name_source"] = SOURCE_ARGV
        return out
    return out
