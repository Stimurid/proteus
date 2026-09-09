# INSTALL_RECEIPT

- receipt ID: INSTALL-PROTEUS-CURSOR-RUN-001-20260909T201711Z
- RUN_ID: PROTEUS-CURSOR-RUN-001-20260909T201711Z
- timestamp: 2026-09-09T20:27:08Z (last cycle)
- source: `C:\Projects\Proteus` (`hosts/cursor/templates` + `src/proteus/install_cursor.py`)
- host: Cursor 3.19.13
- python: `C:\Users\Timur Shchukin\AppData\Local\Programs\Python\Python313\python.exe`

## Host files created (none of these existed as Proteus hooks before this run)

- `%USERPROFILE%\.cursor\hooks.json` (created; previously ABSENT)
- `%USERPROFILE%\.cursor\hooks\proteus_hook.cmd`
- `%USERPROFILE%\.proteus\host\cursor\**`

## Project files generated from templates

See installer JSON under `%USERPROFILE%\.proteus\receipts\PROTEUS-CURSOR-RUN-001-20260909T201711Z.json`.

## Unrelated settings

`~/.cursor/mcp.json` still only `Dropbox MCP`. `cli-config.json` not rewritten.

## Rollback

`evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/ROLLBACK.md`
Backups: `host-backups`, `host-backups-cycle2`, `host-backups-cycle3`

## Second cycle

Deficit: sessionStart orientation omitted `DECISIONS.md` (provenance of accepted decisions).
Source change: `src/proteus/events.py` load list.
Reinstall copied package to `~/.proteus/host/cursor/src/proteus`.
Verify: unit test `decision-marker`; Select-String on installed `events.py`.
Idempotent third install: `hooks.json` SHA256 unchanged.
