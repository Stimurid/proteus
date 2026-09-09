# T02 DIAGNOSIS — empty stdin

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
T02 status remains **PARTIAL**. This file does not upgrade T02.

## Facts

1. After T02 cutoff, `%USERPROFILE%\.proteus\telemetry\cursor\2026-09-09\events.jsonl` grew append-only with new `event_id` / `timestamp_utc`. Every live post-cutoff row had `hook_event_name=unknown` and null `conversation_id` / `workspace_roots` / `session_id` (empty payload, not merely a missing name field).
2. Installed user hooks (`%USERPROFILE%\.cursor\hooks.json`) registered the **same** `hooks\proteus_hook.cmd` under `workspaceOpen`, `sessionStart`, `sessionEnd`, `preCompact`, `stop`, `afterFileEdit`, `postToolUseFailure`. Cursor already knew the slot at registration; Proteus discarded that knowledge.
3. Launcher `%USERPROFILE%\.cursor\hooks\proteus_hook.cmd` was `@echo off` + env + `python -m proteus.hook` with **no argv** and no stdin fallback.
4. Isolated diagnostic (`PROTEUS_HOME` temp, not live spool): `cmd /c proteus_hook.cmd` with empty stdin → `unknown`. The same `.cmd` with JSON piped to stdin → `sessionStart` and `additional_context`. So the batch file **can** forward stdin when a pipe exists.
5. Cursor docs (https://cursor.com/docs/hooks.md): command hooks receive JSON on stdin including `hook_event_name`; `command` is a shell string; documented example includes extra argv (`bun run .cursor/hooks/track-stop.ts --stop`). Docs are silent on empty stdin and Windows `cmd.exe`.
6. Simulated named rows (`sim-001` sessionStart, scripted workspaceOpen) remain pre-cutoff and must not count.

## Hypotheses (not used as names)

- **H1:** This Cursor 3.19.13 Windows GUI spawn does not attach/write hook stdin for user-level `.cmd` hooks. Compatible with fact 1 + fact 4.
- **H2:** Stdin is written but lost in a spawn path we did not reproduce (not `cmd /c` + pipe). UNKNOWN.
- **H3:** A race (process reads stdin before Cursor writes). UNKNOWN; not tested against the GUI.

Do not infer `sessionStart` / `workspaceOpen` / `stop` from timestamps.

## Repair hypothesis (tested in unit/smoke, not by live `python -m proteus.hook`)

Registration already has the slot name. Put `--hook-event <name>` in each `command` string (documented argv convention). Parse stdin when valid; if argv and trusted stdin disagree, record CONFLICT and keep `hook_event_name=unknown`. Missing both → UNKNOWN.

## Process-boundary marker

Hook records a best-effort Windows Toolhelp ancestor whose image name contains `cursor`, plus create time. Python’s parent is often short-lived `cmd.exe`. A later change in `process_marker.cursor_create_time_utc` is compatible with a host restart and is **not** an independent OS-quit witness. If the walker cannot name Cursor, leave UNKNOWN.
