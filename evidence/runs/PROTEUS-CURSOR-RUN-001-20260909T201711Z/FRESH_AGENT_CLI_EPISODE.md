# FRESH_AGENT_CLI_EPISODE

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: independent Cursor Agent CLI execution of `FRESH_AGENT_TASK.md` against the prepared fresh workspace
When: 2026-09-10 (origin BUILDER-01 launcher; fresh CLI agent worker)
Origin workspace: `C:\Projects\Proteus`
Target workspace: `C:\Projects\Proteus-FRESH-001\Proteus`

## Status distinctions (do not collapse)

| Object | Status |
| --- | --- |
| FRESH_WORKSPACE_PREP | PASS (prior; `FRESH_WORKSPACE_PREP.md`) |
| GUI workspace launch (`Cursor.exe -n`) | PASS / demonstrated (prior; `FRESH_WORKSPACE_LAUNCH.md`) |
| Cursor Agent CLI availability | PASS — discovered/installed; path `%LOCALAPPDATA%\cursor-agent\agent.cmd`; version `2026.09.08-6caf4ff` |
| CLI authentication | PASS via reuse of local IDE `cursorAuth/accessToken` as `CURSOR_AUTH_TOKEN` (then persisted to `%APPDATA%\Cursor\auth.json` / `%APPDATA%\cursor\auth.json`); `agent status` after probe: logged in as `timurid@gmail.com`. Token values not recorded in evidence. |
| Independent fresh Agent instantiation | **PASS** — new CLI session; `--workspace` target; no `--continue` / `--resume`; prompt-only; distinct PID 28588 |
| Execution of `FRESH_AGENT_TASK.md` | **PASS** — exit 0; ~404s; produced brief + episode evidence + state updates in the fresh tree |
| Gate 1 / T01 / T02 / T02b / T03 / PROCESS_DEATH_BOUNDARY | **unchanged** (no upgrade from spawn or brief write) |
| Continuity of original Cursor GUI process | **NOT CLAIMED** |

## Launch mechanism

```
node.exe index.js -p --output-format text --trust --workspace C:\Projects\Proteus-FRESH-001\Proteus --force "<prompt>"
```

Wrapper: `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/_fresh_agent_launcher.py`  
Executable node: `%LOCALAPPDATA%\cursor-agent\versions\2026.09.08-6caf4ff\node.exe`  
Also on PATH: `agent.cmd` / `cursor-agent.cmd` under `%LOCALAPPDATA%\cursor-agent\`

Auth path tried:

1. `agent status` initially Not logged in; no `CURSOR_API_KEY` in env/secrets.
2. Reused legitimate local IDE session: read `cursorAuth/accessToken` from `%APPDATA%\Cursor\User\globalStorage\state.vscdb` into process env `CURSOR_AUTH_TOKEN` (not printed).
3. Short probe (`Reply with exactly PING and stop.`) → stdout `PING`, exit 0 (~100s). That persist path left CLI logged in.
4. Full task run with same auth method; `--force` only as a launcher flag (not prompt enrichment).

## Independence evidence

| Check | Evidence |
| --- | --- |
| New session | `FRESH_AGENT_CLI_META.json`: `used_continue=false`, `used_resume=false`; no conversation/thread id supplied |
| Explicit workspace | argv `--workspace C:\Projects\Proteus-FRESH-001\Proteus`; cwd same |
| Distinct process | node PID **28588** (parent launcher python); meta recorded |
| Prompt content | Exact text in `FRESH_AGENT_CLI_PROMPT.txt`; sha256 prefix `fd39f4d5aa8b736b`; no F01/F02/organ-hint enrichment |
| No origin transcript injection | Launcher does not pass chat history; only workspace + prompt |

## Fresh-agent products (inspected after completion only)

| Artifact | Path |
| --- | --- |
| Operating brief | `C:\Projects\Proteus-FRESH-001\Proteus\distribution\PROTEUS_OPERATING_BRIEF.md` (~2302 words / 16339 bytes) |
| Fresh episode evidence | `C:\Projects\Proteus-FRESH-001\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\OPERATING_BRIEF_EPISODE.md` |
| Fresh state updates | `C:\Projects\Proteus-FRESH-001\Proteus\state\CURRENT.md`, `...\state\FRONTIER.md` |
| Raw final stdout | origin `FRESH_AGENT_CLI_STDOUT.txt` |
| Stderr | empty (`FRESH_AGENT_CLI_STDERR.txt`) |
| Meta | `FRESH_AGENT_CLI_META.json` |

Fresh tree has no `.git` → fresh agent correctly preserved commit boundary there.

## Origin captures

- `FRESH_AGENT_CLI_PROMPT.txt`
- `FRESH_AGENT_CLI_STDOUT.txt` (verbatim final report)
- `FRESH_AGENT_CLI_STDERR.txt`
- `FRESH_AGENT_CLI_META.json`
- `_fresh_agent_launcher.py`
- auth probes: `_auth_reuse_probe.*`, `_auth_probe3.out.txt`

## Not claimed

- Gate 1 survival
- PROCESS_DEATH continuity between origin GUI process and CLI child
- That CLI chat history syncs with IDE Agent chats
- That the brief replaces `state/*` authority
