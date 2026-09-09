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
