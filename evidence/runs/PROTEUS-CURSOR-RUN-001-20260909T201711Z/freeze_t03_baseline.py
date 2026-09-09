"""Read-only T03 baseline freeze. Does not invoke proteus.hook."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(r"C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z")
TOKEN = "T03-COMPACT-" + "7e4b2c91-6a1f-4d8e-9c3a-0f5b8a12d6e4"
REPO = Path(r"C:\projects\Proteus")


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze_jsonl(path: Path) -> dict:
    if not path.exists():
        return {"path": str(path), "exists": False}
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
    precompact = [
        {
            "event_id": ev.get("event_id"),
            "timestamp_utc": ev.get("timestamp_utc"),
            "event_name_source": ev.get("event_name_source"),
            "session_id": ev.get("session_id"),
            "evidence_class": ev.get("evidence_class"),
        }
        for ev in events
        if ev.get("hook_event_name") == "preCompact"
    ]
    return {
        "path": str(path),
        "exists": True,
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
        "precompact_event_ids_at_freeze": [x["event_id"] for x in precompact],
        "precompact_count_at_freeze": len(precompact),
    }


def git_snapshot() -> dict:
    def run(args: list[str]) -> str:
        r = subprocess.run(
            ["git", *args],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        return (r.stdout or "").strip()

    return {
        "head": run(["rev-parse", "HEAD"]),
        "branch": run(["rev-parse", "--abbrev-ref", "HEAD"]),
        "status_short": run(["status", "--short"]),
        "log_oneline_3": run(["log", "-3", "--oneline"]),
    }


def queue_snapshot() -> list[dict]:
    qdir = Path(os.path.expandvars(r"%USERPROFILE%\.proteus\control\queue"))
    items = []
    if not qdir.exists():
        return items
    for path in sorted(qdir.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            items.append({"path": str(path), "parse_error": True})
            continue
        items.append(
            {
                "path": str(path),
                "command_id": rec.get("command_id"),
                "target_RUN_ID": rec.get("target_RUN_ID"),
                "requested_action": rec.get("requested_action"),
                "status": rec.get("status"),
            }
        )
    return items


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    spool_root = Path(os.path.expandvars(r"%USERPROFILE%\.proteus\telemetry\cursor"))
    hooks = Path(os.path.expandvars(r"%USERPROFILE%\.cursor\hooks.json"))
    cmd = Path(os.path.expandvars(r"%USERPROFILE%\.cursor\hooks\proteus_hook.cmd"))
    project_hooks = REPO / ".cursor" / "hooks.json"
    project_cmd = REPO / ".cursor" / "hooks" / "proteus_hook.cmd"
    machine = Path(os.path.expandvars(r"%USERPROFILE%\.proteus\machine_id"))

    spool_days = []
    day_dirs = []
    if spool_root.exists():
        for day in sorted(p for p in spool_root.iterdir() if p.is_dir()):
            day_dirs.append(day.name)
            evp = day / "events.jsonl"
            if evp.exists():
                spool_days.append(analyze_jsonl(evp))

    last_spool = spool_days[-1] if spool_days else {}
    baseline = {
        "token": TOKEN,
        "test": "T03_COMPACTION_CONTINUITY",
        "t03_status_at_freeze": "PREPARED_NOT_RUN",
        "note": (
            "Events at or before cutoff_utc / matching these hashes are PRE-T03. "
            "Do not treat them as T03 compaction evidence. Do not inject proteus.hook "
            "or hand-append JSONL to fake preCompact. Do not open a new chat and call it T03. "
            "Expected probe answers in scoring.probes are for post-boundary scoring only."
        ),
        "cutoff_utc": now,
        "frozen_at_utc": now,
        "identity": {
            "acting_incarnation": "BUILDER-01",
            "host": "Cursor",
            "body": "Proteus v0.1",
            "project": "Proteus",
            "workspace": r"C:\Projects\Proteus",
            "RUN_ID": "PROTEUS-CURSOR-RUN-001-20260909T201711Z",
            "machine_id": machine.read_text(encoding="utf-8").strip() if machine.exists() else None,
        },
        "semantic_state": {
            "frontier": "T03 prepared; stop before /summarize; then T03_POST_COMPACTION_PROMPT.md in the SAME composer conversation",
            "test_statuses": {
                "T01_CLEAN_REENTRY": "PASS",
                "T02": "PARTIAL",
                "T02b": "PASS",
                "T03": "NOT_RUN",
                "PROCESS_DEATH_BOUNDARY": "UNKNOWN",
            },
            "decisions": [
                {
                    "id": "D-001",
                    "summary": "Cursor AGENTS.md + always-apply rules + command hooks + Python installer",
                    "provenance": "PRODUCT_SPEC §2 + host inspection of Cursor 3.19.13 docs (sessionStart.additional_context, stop.followup_message)",
                },
                {
                    "id": "D-002",
                    "summary": "local append-only JSONL + local observatory mirror; Drive flush FAILED_TRANSPORT",
                    "provenance": "WORKLOG spec §13 failure principle + first-run host evidence",
                },
                {
                    "id": "D-003",
                    "summary": "--hook-event argv identity when stdin JSON has no event name; conflict recorded, no winner",
                    "provenance": "T02 PARTIAL (empty-stdin live spool) + Cursor hooks docs extra argv on command + isolated .cmd pipe diagnostic (T02_DIAGNOSIS.md)",
                },
            ],
            "unresolved_sample": [
                "T01 non-contamination is externally witnessed, not internally provable",
                "PROCESS_DEATH_BOUNDARY / full Cursor OS quit unproven after T02b",
                "GUI stdin still lacks hook_event_name; H1/H2/H3 open",
                "CONFLICT: Gate 1 eval plugin Drive IDs vs 70_PLUGIN_SOURCE_MAP.md / 71_PLUGIN_RECOVERY_LEDGER.md",
                "Agent CLI not on PATH; CURSOR_TRANSCRIPT_PATH empty at bootstrap",
            ],
        },
        "operational_state": {
            "git": git_snapshot(),
            "user_hooks_json": {
                "path": str(hooks),
                "sha256": sha256(hooks),
                "exists": hooks.exists(),
                "contains_preCompact": "preCompact" in hooks.read_text(encoding="utf-8") if hooks.exists() else False,
            },
            "user_hook_cmd": {
                "path": str(cmd),
                "sha256": sha256(cmd),
                "exists": cmd.exists(),
            },
            "project_hooks_json": {
                "path": str(project_hooks),
                "sha256": sha256(project_hooks),
            },
            "project_hook_cmd": {
                "path": str(project_cmd),
                "sha256": sha256(project_cmd) if project_cmd.exists() else None,
                "exists": project_cmd.exists(),
            },
            "spool_days": spool_days,
            "day_dirs_present": day_dirs,
            "telemetry_cutoff": {
                "last_event_id": last_spool.get("last_event_id"),
                "last_timestamp_utc": last_spool.get("last_timestamp_utc"),
                "last_hook_event_name": last_spool.get("last_hook_event_name"),
            },
            "control_queue": queue_snapshot(),
            "conversation_id": None,
            "conversation_id_note": "UNKNOWN in this shell; not exposed to the freeze process",
        },
        "compaction_capability": {
            "manual_force": "IDE/CLI slash command /summarize (CLI aliases /compress, /compact). Changelog 1.6; CLI slash-command docs.",
            "automatic": "Cursor compresses older turns when the context window is close to full. Exact percent unpublished; preCompact may include context_usage_percent.",
            "not_compaction": [
                "new Agent chat / CLI /clear",
                "mode switch (fresh window)",
                "@Chats attachment",
                "fork/duplicate chat",
                "Compact chat responses UI density (Cursor 3.4)",
                "prose request to summarize (UNKNOWN whether it equals /summarize; protocol forbids it)",
            ],
            "internal_observation": "preCompact hook already installed at user and project hooks.json; payload trigger auto|manual; observational, cannot block",
            "can_force_reliably": "manual /summarize is the documented force; auto-compact cannot be scheduled to a known token percent",
            "same_conversation_intended": True,
        },
        "boundary_classes": [
            "INTERNAL_PRECOMPACT",
            "EXTERNAL_WITNESS_SUMMARIZE",
            "FRESH_CHAT_NOT_T03",
            "UNKNOWN_BOUNDARY",
        ],
        "scoring": {
            "forbid_post_agent_from_reading": [
                "T03_BASELINE.json",
                "freeze_t03_baseline.py",
            ],
            "probes": [
                {
                    "id": "P1",
                    "kind": "provenance",
                    "question_for_post_prompt": "Recover D-003 from durable state: brief decision AND provenance. Provenance is required.",
                    "expect_decision_contains": ["--hook-event", "argv", "stdin"],
                    "expect_provenance_contains_any": [
                        "T02",
                        "T02_DIAGNOSIS",
                        "empty-stdin",
                        "hooks docs",
                    ],
                    "fail_if": "states argv identity with no provenance, or invents a different origin",
                },
                {
                    "id": "P2",
                    "kind": "unresolved_conflict",
                    "question_for_post_prompt": "Name one CONFLICT durable state refuses to resolve. Do not resolve it.",
                    "expect_mentions_any": [
                        "Drive ID",
                        "70_PLUGIN_SOURCE_MAP",
                        "71_PLUGIN_RECOVERY_LEDGER",
                        "Gate 1",
                    ],
                    "expect_status": "CONFLICT",
                    "fail_if": "picks a winning Drive ID or drops CONFLICT",
                },
                {
                    "id": "P3",
                    "kind": "unresolved_unknown",
                    "question_for_post_prompt": "Did T02b prove full OS process death/restart? Cite process_marker fields and keep the recorded epistemic status.",
                    "expect_status": "UNKNOWN",
                    "expect_mentions_any": [
                        "40844",
                        "2026-09-09T22:51:16",
                        "PROCESS_DEATH",
                        "create_time",
                    ],
                    "fail_if": "claims T02b proved a full quit, or upgrades PROCESS_DEATH_BOUNDARY to proven",
                },
                {
                    "id": "P4",
                    "kind": "nonobvious_operational",
                    "question_for_post_prompt": "Identify the local TEST_STEER command_id recorded for THIS RUN_ID.",
                    "expect_exact": "40a52a1d-16d2-43b8-a09a-10fea9d7ddec",
                    "fail_if": "invents a UUID, or cites the parallel 2015Z command 956aad61-9662-4130-a005-6b3257194b72 as this run",
                },
            ],
        },
        "classification_rules": {
            "continuity_PASS": "identity+workspace+RUN_ID correct; frontier is T03 post-boundary classification not a rewind to T01/T02; T01 PASS / T02 PARTIAL / T02b PASS preserved; P1 provenance recovered; P2 left CONFLICT; P3 left UNKNOWN; P4 exact command_id; no pasted pre-compaction transcript used as authority",
            "continuity_PARTIAL": "identity/frontier/statuses mostly right but one probe miss or provenance omitted, without silently resolving UNKNOWN/CONFLICT",
            "continuity_FAIL": "wrong actor/project/run, or T02 upgraded to PASS, or UNKNOWN/CONFLICT silently resolved, or PROCESS_DEATH_BOUNDARY claimed proven",
            "combined_PASS": "continuity PASS AND boundary_class in {INTERNAL_PRECOMPACT, EXTERNAL_WITNESS_SUMMARIZE, INTERNAL_AND_EXTERNAL} AND not FRESH_CHAT_NOT_T03",
            "combined_PARTIAL": "continuity PARTIAL with a real compaction boundary; OR continuity PASS but only weak/unwitnessed compaction claim without preCompact and without operator /summarize witness",
            "combined_FAIL": "continuity FAIL",
            "combined_UNKNOWN": "cannot score, or only a new chat (T01-class) was used, or hashes/timestamps do not show a post-cutoff boundary and no external /summarize witness",
            "fresh_chat_is_not_pass": True,
            "do_not_mark_pass_before_boundary": True,
        },
        "uuid_note": str(uuid.uuid4()),
    }
    outp = RUN / "T03_BASELINE.json"
    outp.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(outp)
    print("cutoff", now)
    print("head", baseline["operational_state"]["git"]["head"])
    print("last_event_id", last_spool.get("last_event_id"))
    print("precompact_count", last_spool.get("precompact_count_at_freeze"))


if __name__ == "__main__":
    main()
