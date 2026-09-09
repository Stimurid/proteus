# DECISIONS

## D-001 — Host surfaces for v0.1
- Decision: use Cursor project `AGENTS.md` + always-apply `.cursor/rules/*.mdc` + project/user `hooks.json` command hooks + Python ideal-body installer.
- Not used as primary: Cursor marketplace plugin (not required to prove Gate 1 P0), Drive gateway, vector DB.
- Provenance: PRODUCT_SPEC §2 + host inspection of Cursor 3.19.13 docs (`sessionStart.additional_context`, `stop.followup_message`).
- Status: accepted for first incarnation; reversible via uninstall + backup.

## D-002 — Observability transport
- Decision: local append-only JSONL + local observatory mirror; Drive flush marked FAILED_TRANSPORT until a real synced path or working Drive MCP exists.
- Provenance: WORKLOG spec §13 failure principle + first-run host evidence.
- Status: accepted.

## D-003 — Hook event identity when stdin is empty
- Decision: each Cursor `hooks.json` command string includes `--hook-event <slot>`; `proteus.hook` keeps stdin JSON when valid; `event_name_source` is `stdin` | `argv` | `stdin+argv` | `none` | `conflict`. Conflicting stdin vs argv is recorded and does not pick a winner. Timing is not used to name events.
- Provenance: T02 PARTIAL (empty-stdin live spool) + Cursor hooks docs allowing extra argv on `command` + isolated `.cmd` pipe diagnostic (`T02_DIAGNOSIS.md`).
- Status: accepted. T02b PASS confirmed argv naming on live `sessionStart`/`workspaceOpen`. T02 remains PARTIAL (empty-stdin original). OS quit still UNKNOWN.
