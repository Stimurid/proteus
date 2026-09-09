# DESIGN_v0.1.md

RUN_ID: PROTEUS-CURSOR-RUN-001-20260909T201711Z
Status: implementation choice (class E), tested where possible.

## Chosen surfaces

1. **Persistent orientation** — always-apply `.cursor/rules` + `AGENTS.md` + `sessionStart.additional_context` from `state/*.md`.
2. **Durable current-run/project carrier** — `state/` markdown files (IDENTITY/CURRENT/FRONTIER/DECISIONS/UNRESOLVED).
3. **Source→install** — `src/proteus/install_cursor.py` copies templates into project + user hooks.
4. **Global telemetry** — user `~/.cursor/hooks.json` command hook writing JSONL under `%USERPROFILE%\.proteus\telemetry`.
5. **External control P0** — local JSON command queue + `stop` `followup_message`; CLI wrapper `python -m proteus.cli enqueue`.
6. **Anti-reduction** — dedicated always-apply rule quoting the 14 Aug 2026 constraint without turning it into a state machine.

## Deferred (open alternatives)

- Cursor plugin marketplace package
- ACP persistent controller (`agent acp` binary missing)
- Drive Runtime Observatory upload (no working Drive transport)
- Vector memory / MCP memory organ
- Prompt-type hooks (command hooks chosen for deterministic telemetry)

## Why not plugin-first

Host inspection found native rules/hooks/skills sufficient for a reversible first embodiment. A plugin remains a FUTURE_OPTION until native surfaces fail a Gate test.
