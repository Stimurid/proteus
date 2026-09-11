# F04 — First foreign-carrier morphology: Codex

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
When: 2026-09-11 (origin BUILDER-01)  
Decision: **D-009** (Codex morphology; host-neutral world API reuse)

## Verdict (separate statuses — do not collapse)

| Status key | Result |
| --- | --- |
| `CODEX_HOST_DISCOVERY` | **PASS** |
| `CODEX_MORPHOLOGY` | **PASS** |
| `CODEX_INDEPENDENT_SESSION` | **PASS** |
| `CODEX_AW1000_RECALL` | **PASS** |
| `CODEX_PROVENANCE_RECALL` | **PASS** |
| `CODEX_CONFLICT_UNKNOWN_RECALL` | **PASS** |
| `CODEX_SECRET_BOUNDARY` | **PASS** |
| `CODEX_DURABLE_WRITEBACK` | **PASS** |
| `CURSOR_POST_CODEX_READBACK` | **PASS** |
| `PROJECT_SCOPE_NEGATIVE_CONTROL` | **PASS** |
| `F04_FOREIGN_CARRIER` | **PASS** |

Not claimed: Gate 1; NATURAL_RECRUITMENT PASS; live Archivarius; real secret availability; Claude/OpenClaw; full multi-host sync; identity of Codex incarnation with Cursor BUILDER-01.

`NATURAL_RECRUITMENT` remains **NOT_PROVED** (ordinary unprimed prompt; spontaneous Proteus-like behaviors noted as potential evidence only).

## Recovered origin (pre-mutation)

Preserved: D-006 PRODUCT_ACTIVATION PASS; D-007 world memory PASS; D-008 AW1000 harden PASS; entity `entity.router.aw1000.home`; Gate 1 NOT_YET; LIVE_ARCHIVARIUS_RECONCILIATION BLOCKED; AW1000_REAL_SECRET UNAVAILABLE.

## 1. Codex host discovery

- Desktop CLI present: `%LOCALAPPDATA%\OpenAI\Codex\bin\`
- Top-level shim `codex.exe` reported `codex-cli 0.130.0-alpha.5` (insufficient for configured model `gpt-5.6-terra`).
- Versioned binary used for success: `...\bin\27d6a192e9c98618\codex.exe` → **`codex-cli 0.153.4`**
- Auth: ChatGPT login (tokens not logged); `codex login status` → Logged in using ChatGPT
- Non-interactive: `codex exec` (`-C`, `--ephemeral`, `--skip-git-repo-check`, `-o`, stdin prompt)
- Resume exists as separate command (`codex resume` / `fork`) — **not used**
- winget package `OpenAI.Codex` 0.152.0 available; npm `@openai/codex` 0.154.0 noted; desktop update path refused (“Could not detect installation method”)

### Transport repairs (infrastructure only; not semantic child steering)

1. Stale `~/.codex/.env` forced `HTTP(S)_PROXY=http://127.0.0.1:10809` with nothing listening → WSS/HTTP failures (10061). Stashed for successful run; restored after (`F04_CODEX_DOTENV_STASH.env`).
2. Prefer newer nested CLI 0.153.4 over 0.130 alpha shim.
3. Models-cache effort variants `max`/`ultra` sanitized to `xhigh` for alpha parser (cache still refreshed from network).

Failed attempts preserved: `F04_CODEX_CHILD_ATTEMPT{1,2,3}_*` + smoke files.

## 2. Morphology (D-009)

Ideal body (not Cursor clone):

- Templates: `hosts/codex/templates/` (`AGENTS.md`, `ENTRY.md`, `world_env.cmd`, minimal `state/*`, `CLAUDE.md`)
- Installer: `python -m proteus.activate_codex` / `python -m proteus activate-codex`
- Runtime: prefers **ideal-body `src`** PYTHONPATH (not Cursor host-install copy)
- Reuses **`proteus.world.api`** / `python -m proteus world`
- No Cursor hooks/rules/launcher clone
- Acting identity: Codex coding agent (**not** BUILDER-01)
- Launcher: `src/proteus/launch_codex.py` (+ episode `_codex_launcher.py`)

Disposable project: **`C:\Projects\Proteus-CODEX-001`**  
`AIYE_HOME` → episode `world_memory_home` (shared substrate; no AW1000 corpus copied into project).

## 3. Independent Codex session

| Field | Value |
| --- | --- |
| Executable | `...\27d6a192e9c98618\codex.exe` |
| Version | `codex-cli 0.153.4` |
| PID | 22444 |
| Workspace | `C:\projects\Proteus-CODEX-001` |
| Session id | `01a09085-e581-7ae1-9909-3135620187ae` (stderr banner; ephemeral) |
| used_resume / fork / continue | **false** |
| ephemeral | true |
| Prompt SHA-256 | `fb0025163c6c04361638592b56f7dce837d2758133813f3947a25d8bd87c3a9c` |
| Prompt file | `F04_CODEX_CHILD_PROMPT.txt` |
| Meta | `F04_CODEX_CHILD_META.json` |
| Raw result | `F04_CODEX_CHILD_RAW_RESULT.txt` (+ `F04_CODEX_CHILD_LAST_MESSAGE.txt`, stdout/stderr) |

Child prompt: ordinary Russian router task only (no entity id, no F04 labels, no provenance coaching).

## 4. AW1000 recall / provenance / conflict / secrets

From child raw result + world inspection:

- Resolved shared entity via ordinary name (“наш роутер”) without prompt-injected facts → **AW1000 recall PASS**
- Used prior provenance-bearing claims (historical vs live) → **provenance PASS**
- Retained CONFLICT (mgmt `192.168.2.1` vs `192.168.3.1`) and UNKNOWNs (failover, LED) → **conflict/UNKNOWN PASS**
- Secret refs present on entity (`secret://router.aw1000.home.admin` UNAVAILABLE; ssh key path only). Leakage scan on child artifacts: **no password/key material hits** → **secret boundary PASS**

## 5. Durable writeback

New observation:

- **claim_id:** `claim.d992454666c9`
- **scope:** `EPISODE` (correct for dated reachability)
- **entity:** `entity.router.aw1000.home`
- **text:** 2026-09-11T13:07Z read-only SSH to `root@192.168.3.1` from Proteus-CODEX-001; `ubus call system board` → QWRT / Arcadyan AW1000 / OpenWrt 21.02-SNAPSHOT; no config changes
- **destination:** shared world entity claims (not project-only)

## 6. Independent Cursor readback

| Field | Value |
| --- | --- |
| Workspace | `C:\Projects\Proteus-CURSOR-F04-READBACK` |
| Prompt SHA-256 | `b377749fadde76551b333e1c5034c3083825b294b90200b708bf8f1772d028d9` |
| used_resume/continue | false |
| Meta | `F04_CURSOR_READBACK_META.json` |
| Raw | `F04_CURSOR_READBACK_STDOUT.txt` |

Cursor recovered **today’s** Codex observation including `claim.d992454666c9` / Proteus-CODEX-001 / 13:07Z without receiving Codex output in the prompt → **CURSOR_POST_CODEX_READBACK PASS**.

## 7. Project-scope negative control

Origin-seeded PROJECT decision marker `NEGATIVE_CONTROL_CODEX_F04` in `Proteus-CODEX-001\state\DECISIONS.md` / project_memory.

- Absent from entity claims
- Absent from Cursor readback as router truth

→ **PROJECT_SCOPE_NEGATIVE_CONTROL PASS**

## 8. Morphology comparison (Cursor vs Codex)

| Surface | Cursor | Codex |
| --- | --- | --- |
| Entry / instructions | `AGENTS.md` + always-apply `.cursor/rules` + skills | Project `AGENTS.md` + `.proteus/ENTRY.md` |
| Lifecycle hooks | `hooks.json` sessionStart/stop/preCompact | Available on host but **not** used for F04 morphology |
| Tools / MCP | Cursor tools + Agent CLI | Codex tools/sandbox; optional MCP (not required for world API) |
| Fresh session launch | Agent CLI `node index.js -p` | `codex exec --ephemeral` |
| World API | `proteus.world.api` / CLI | **same** |
| Secret capability | Windows Credential Manager broker | same broker via CLI; no plaintext in child |
| Project activation | `proteus.activate` | `proteus.activate_codex` |
| Acting role | BUILDER-01 on ideal body; mount ≠ BUILDER-01 | Codex agent (explicitly not BUILDER-01) |

Transferred unchanged: entity substrate, alias resolve, scopes, secret refs, world API.  
Host-specific: instruction surfaces, launchers, absence of Cursor hooks in Codex mount.  
Unavailable / non-constitutive for this PASS: Cursor hook identity stack; Codex hooks unused.

## 9. Tests

- `tests/test_activate_codex.py` (empty activate, foreign AGENTS preserve, world API scopes, uninstall, refuse cursor manifest)
- Regression: `pytest tests/test_activate.py tests/test_activate_codex.py tests/test_world_memory.py tests/test_secret_broker.py` → **31 passed**

Synthetic tests do not replace the live Codex/Cursor loop above.

## 10. Natural recruitment note

Child spontaneously preserved CONFLICT/UNKNOWN and routed a dated observation as EPISODE without prompt coaching. Recorded as **potential** natural evidence only. **NATURAL_RECRUITMENT = NOT_PROVED**.

## 11. Limitations / boundaries

- Codex desktop shim 0.130 vs nested 0.153.4 version skew
- Stale `~/.codex/.env` proxy must be absent or pointed at a live proxy for CLI
- LIVE_ARCHIVARIUS_RECONCILIATION still BLOCKED
- AW1000_REAL_SECRET still UNAVAILABLE
- Gate 1 NOT_YET
- Disposable projects outside git (`Proteus-CODEX-001`, `Proteus-CURSOR-F04-READBACK`)
