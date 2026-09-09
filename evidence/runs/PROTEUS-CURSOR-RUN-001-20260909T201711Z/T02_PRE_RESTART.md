# T02 PRE-RESTART

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Token: `T02-HOOKFIRE-145f0152-155e-4362-ac8c-801e9e1c7ba9`
T02 status: **NOT_RUN** — do not claim PASS until after a real Cursor quit/reopen.

Machine-readable twin: `T02_BASELINE.json` (re-frozen at the end of this preparation; if this markdown and the JSON disagree, **JSON wins**).

## What T02 must prove

User-level Cursor hooks (`%USERPROFILE%\.cursor\hooks.json` → `hooks\proteus_hook.cmd`) still exist and **actually execute after a full Cursor process restart**, writing new telemetry that cannot be confused with pre-restart rows (including simulated `sessionStart`/`workspaceOpen` from RUN-001 and `unknown` rows from this T01/T02-prep session).

Gate 1 T02 also wants continuity after reopen; that is answered from durable state in the post-restart chat. Continuity alone is **not** hook-fire evidence.

## Discriminating rule (old telemetry cannot count)

A row counts as a **new hook firing** only if **all** hold:

1. It appears in `%USERPROFILE%\.proteus\telemetry\cursor\<day>\events.jsonl` (new day files after `2026-09-09` are allowed and expected if the local date rolled).
2. `timestamp_utc` is **strictly after** `cutoff_utc` in `T02_BASELINE.json`.
3. `event_id` is not the frozen `last_event_id`, and is not in `simulated_named_ids_must_not_count`.
4. The spool is append-only growth vs frozen `sha256`/`line_count` (or a new day file). Hash change without a newer timestamp is UNKNOWN, not PASS.
5. The row was **not** created by this agent running `python -m proteus.hook` or appending JSONL by hand.

Observatory mirror (`%USERPROFILE%\.proteus\observatory\10_CURSOR\`) is secondary. Primary is the local spool. Drive flush remains FAILED_TRANSPORT and is not T02.

## Classification

| Result | Required evidence |
| --- | --- |
| **PASS** (hooks) | ≥1 post-cutoff spool event with `hook_event_name` `workspaceOpen` or `sessionStart`, and `session_id` not `sim-001` |
| **PARTIAL** | post-cutoff spool events exist, but all are `hook_event_name=unknown` (binary ran; Cursor did not name the event) |
| **UNKNOWN** | no trustworthy new rows (unchanged hashes, timestamps ≤ cutoff, or only self-injected rows) |
| **FAIL** | positive evidence Proteus user hooks are gone/broken **and** no post-cutoff hook-process evidence |

Preserve UNKNOWN if Cursor gives no trustworthy hook evidence.

## Pre-restart snapshot (see JSON if stale)

Frozen fields are in `T02_BASELINE.json`. At last freeze before commit they included:

- spool `2026-09-09` `events.jsonl` — authoritative counts/hashes in `T02_BASELINE.json` (prep session already appended `unknown` rows; they are pre-restart)
- **no** `2026-09-10` spool file at freeze time
- named spool events only: two `external_command_sent`, simulated `sessionStart` `sim-001`, simulated `workspaceOpen`, one `stop` — **none of these may count as T02**
- user `hooks.json` contains `proteus_hook`

## Forbidden before the restart

- Do not inject hook events to green T02.
- Do not treat current-session `unknown` rows as restart survival.
- Do not rerun T01.

## Human action

Fully **quit Cursor** (exit the process). Reopen workspace `C:\Projects\Proteus`. Start a **new** Agent chat using only `T02_POST_RESTART_PROMPT.md`.
