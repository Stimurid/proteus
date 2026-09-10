# FRESH_WORKSPACE_LAUNCH

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: move execution boundary to prepared fresh workspace
When: 2026-09-10 (~15:22–15:27 local, UTC+3)
Statuses unchanged by this episode: T01/T02/T02b/T03/Gate 1 / PROCESS_DEATH_BOUNDARY / Drive / fresh-Agent execution of `FRESH_AGENT_TASK.md`

This episode is not a PASS on the future incarnation. Opening a window is not Agent execution.

## Target verified before launch

- Path exists: `C:\Projects\Proteus-FRESH-001\Proteus`
- Task file exists: `C:\Projects\Proteus-FRESH-001\Proteus\FRESH_AGENT_TASK.md`
- Destination is the prepared reconstruct (no origin `.git` copy); not mutated from origin to simulate relocation.

## Launch attempted

| Field | Value |
| --- | --- |
| Attempted | YES |
| Mechanism | `Start-Process` → `Cursor.exe -n C:\Projects\Proteus-FRESH-001\Proteus` |
| Executable | `C:\Users\Timur Shchukin\AppData\Local\Programs\cursor\Cursor.exe` (also on PATH as `cursor.cmd`) |
| Launch PID | 2064 |
| Before Cursor process count | 38 |
| After (~8s) | 41 |
| New PIDs observed | 2064, 6020, 21108 |

## Workspace / window activation verified

| Evidence | Result |
| --- | --- |
| `workspaceStorage` entry | YES — id `2933702524a15212fc18d5f35c2cdfd5`, `workspace.json` folder `file:///c%3A/Projects/Proteus-FRESH-001/Proteus`, LastWriteTime `2026-09-10T15:22:58+03:00` |
| Cursor project dir | YES — `%USERPROFILE%\.cursor\projects\c-Projects-Proteus-FRESH-001-Proteus` created `2026-09-10T15:23:15+03:00` (`canvases/`, `mcps/`) |
| Win32 command line | YES — PID 2064: `Cursor.exe -n C:\Projects\Proteus-FRESH-001\Proteus` |
| Distinct classic window title | NOT observed as a separate titled frame; visible Cursor UI title sampled as `Cursor Agents` (Glass/Agents host surface). Folder registration is still verified via storage + project dir. |

Verdict: **target workspace opened/activated automatically** (separate `-n` new-window launch; not `move_agent_to_root` on this conversation).

## Independent Agent instantiation

| Path tried | Result |
| --- | --- |
| `cursor-app-control.move_agent_to_root` | NOT USED — would keep this origin conversation as authority |
| `cursor-app-control.open_resource` | Cannot open an out-of-workspace folder as a new Cursor window; command/product-protocol URIs unsupported |
| IDE API to create a new Agent chat + inject prompt | UNAVAILABLE in this host tool surface |
| Cursor Agent CLI before this episode | Missing / unproved |
| Official Windows install `irm https://cursor.com/install?win32=true \| iex` | SUCCEEDED; binaries at `%LOCALAPPDATA%\cursor-agent\agent.cmd` and `cursor-agent.cmd` (CLI Version `2026.09.08-6caf4ff`) |
| `agent status` / `agent about` | **Not logged in**; no `CURSOR_API_KEY` in environment; no matching key name in `C:\projects\.cursor\secrets.env` |
| Non-interactive probe | `agent -p --trust --workspace C:\Projects\Proteus-FRESH-001\Proteus "<one-line instruction>"` → stderr: `Authentication required. Please run 'agent login' first, or set CURSOR_API_KEY environment variable.` (see `_agent_cli_probe.err.txt`) |
| `agent login` | Would require browser/device auth — expands human action beyond the intended single paste; not performed |

Verdict: **independent fresh Agent was NOT instantiated.**

CLI binary is now present (prior UNKNOWN/unproved location resolved to install path) but authentication is a separate host/UI boundary. Completing CLI login would add a browser/auth step and is not preferred over the already-open IDE workspace path.

## Exact remaining boundary

Single irreducible next human action:

> In the already-opened Cursor workspace rooted at `C:\Projects\Proteus-FRESH-001\Proteus`, create/select a new Agent chat and paste only: `Open and execute FRESH_AGENT_TASK.md. Treat this workspace's durable files as authority. Do not inspect or use C:\Projects\Proteus or any previous conversation.`

Not required of the human: folder opening, workspace navigation, shell commands, copying files, or setup.

## Not claimed

- Gate 1 upgrade
- Fresh-Agent execution PASS
- PROCESS_DEATH continuity
- That Agent CLI install equals authenticated headless control
- That Glass window-title absence disproves workspace activation (storage + project dir contradict that)
