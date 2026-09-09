# BASELINE

RUN_ID: PROTEUS-CURSOR-RUN-001-20260909T201711Z
OS: Windows 10 (build 26200)
Cursor: 3.19.13 (`dd066f332fcea7382764400fde902f61920648d0`) x64
Workspace before move: `C:\projects`
Workspace after move: `C:\Projects\Proteus` (same NTFS path, case-insensitive)
Git: initialized empty repo at first run; no remotes.

## Supported surfaces (DISCOVERED vs DOCS)

| Surface | Status |
| --- | --- |
| Project `.cursor/rules/*.mdc` | DOCS + create-rule skill; not previously present in this repo |
| `AGENTS.md` / `CLAUDE.md` | DOCS (Agent CLI reads them); used |
| User `~/.cursor/hooks.json` | DOCS; file ABSENT before install |
| Project `.cursor/hooks.json` | DOCS; used |
| `sessionStart.additional_context` | DOCS (fetched cursor.com/docs/hooks) |
| `stop.followup_message` + `loop_limit` | DOCS |
| Skills `.cursor/skills` | DISCOVERED user skills under `~/.cursor/skills-cursor`; project skills installed |
| MCP user `~/.cursor/mcp.json` | DISCOVERED (Dropbox only); **not modified** |
| `~/.cursor/cli-config.json` | DISCOVERED; **not modified** |
| Cursor Agent CLI `agent` | NOT FOUND on PATH |
| `agent acp` | NOT PROBED (no binary) |
| `CURSOR_TRANSCRIPT_PATH` | EMPTY in bootstrap shells |
| Google Drive Desktop `Мой диск` | EXISTS but empty (desktop.ini only) |
| Drive MCP | error / Not connected |
| `cursor` CLI | FOUND (`cursor.cmd`) |

## Unrelated settings boundary

Do not edit: `cli-config.json`, `mcp.json`, `argv.json`, VPN, Amnezia/Happ, other project repos.
