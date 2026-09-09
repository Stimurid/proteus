"""Discriminating rules for T02 / T02b named restart fires.

Timing of unknown rows is not a named Cursor hook. Simulated baseline ids never count.
"""

from __future__ import annotations

from typing import Any, Mapping

NAMED_RESTART_HOOKS = frozenset({"sessionStart", "workspaceOpen"})


def counts_as_named_restart_fire(event: Mapping[str, Any], baseline: Mapping[str, Any]) -> bool:
    reason = named_restart_fire_reason(event, baseline)
    return reason is None


def named_restart_fire_reason(event: Mapping[str, Any], baseline: Mapping[str, Any]) -> str | None:
    cutoff = baseline.get("cutoff_utc") or ""
    ts = event.get("timestamp_utc") or ""
    if not ts or not (ts > cutoff):
        return "timestamp_not_after_cutoff"
    eid = event.get("event_id")
    last_id = None
    spool_days = baseline.get("spool_days") or []
    if spool_days:
        last_id = spool_days[0].get("last_event_id")
    if eid and eid == last_id:
        return "baseline_last_event_id"
    banned = set(baseline.get("simulated_named_ids_must_not_count") or [])
    banned.update(baseline.get("excluded_event_ids") or [])
    if eid in banned:
        return "excluded_simulated_or_named_id"
    if event.get("session_id") == "sim-001":
        return "sim_001_session"
    if event.get("evidence_class") in {"test", "simulated"}:
        return "test_or_simulated_evidence_class"
    name = event.get("hook_event_name")
    if name not in NAMED_RESTART_HOOKS:
        return "not_named_workspaceOpen_or_sessionStart"
    source = event.get("event_name_source")
    if source == "conflict":
        return "identity_conflict"
    if event.get("event_name_conflict"):
        return "identity_conflict"
    return None
