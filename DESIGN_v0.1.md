# DESIGN v0.1 — first Cursor incarnation

**Historical first-pass design dump.** A parallel write exists at `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/DESIGN_v0.1.md`. Neither file is Proteus itself. Accepted host-surface decisions live in `state/DECISIONS.md`.

Status: implementation choice (class E), tested against host inspection on 2026-09-09.

## Chosen surfaces (discovered vs documented)

Discovered on this machine:

- Cursor `3.19.13` (`dd066f332fcea7382764400fde902f61920648d0`), OS Windows 10, machine `timlenovo`.
- User config dir `%USERPROFILE%\.cursor\` with `cli-config.json`, `mcp.json`, `argv.json`. **No pre-existing `hooks.json`.**
- Project rules/skills/commands/hooks: standard `.cursor/` layout (used).
- `AGENTS.md` / `CLAUDE.md` supported per product docs; both present.
- MCP: user `mcp.json` currently lists Dropbox URL server; Google Drive MCP in this agent session was **error / not connected**.
- `cursor` CLI advertises `agent` subcommand. Standalone `agent` binary: **absent**. `cursor agent --help` does not print Agent CLI flags. ACP: **not demonstrated**.
- Transcripts: `CURSOR_TRANSCRIPT_PATH` not observed in this session. Pointer field is logged when hook payload provides it.

Documented (not all verified in behavior):

- User hooks `~/.cursor/hooks.json`; events including `workspaceOpen`, `sessionStart`, `stop` + `followup_message`.
- Windows stdout capture for stop hooks has a known failure class — recorded as UNKNOWN.

## Why these

- Persistent orientation: `AGENTS.md` + alwaysApply rule + `sessionStart.additional_context` (best-effort; fire-and-forget).
- Durable project state: `CURRENT.md` / `FRONTIER.md` / `UNKNOWN.md` / `DECISIONS.md` (files, not a vector DB).
- Checkpoint: `src/proteus/checkpoint.py` + skill/command.
- Telemetry: global user hooks writing `%USERPROFILE%\.proteus\telemetry\` and `%USERPROFILE%\.proteus\observatory\`.
- External control: stop-hook claim of local queue + `src/proteus/control.py` CLI ack. ACP/CLI-agent deferred with explicit blocker.
- Source→install: `src/proteus/install.py` copies hook tree and merges only Proteus entries in user `hooks.json`.

## Deferred (open)

- Drive API gateway / MCP Drive flush.
- Always-on ACP controller.
- User-level Cursor Settings rules via `cursor_dialog` (list returned empty; existing user rules in this chat may live elsewhere — do not overwrite).
- Plugin packaging.
- Vector memory, multi-host.

## Alternatives remaining open

- Plugin vs repo+hooks: repo chosen for inspectability and rollback.
- Prompt-based hooks vs command hooks: command hooks chosen (cloud-agent compatible for project `.cursor/hooks.json`).
