# GATE1_INDEPENDENT_REAUDIT

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
When: 2026-09-11  
Origin role: BUILDER-01 recording only — **did not alter re-auditor verdict**.

## Freeze

| Field | Value |
| --- | --- |
| Audited commit | `4b1f8d39a6731a994dc67c66aa8f5c059bda78d8` |
| Origin HEAD at freeze | identical |
| Working tree for subject | clean (untracked isolated Cursor userdata dirs excluded) |
| Snapshot method | `git archive --format=zip` → Expand-Archive |
| Re-audit bundle | `C:\Projects\Proteus-GATE1-REAUDIT-001` |
| Archive ZIP SHA-256 | `49a52f5aecf942e2a124cf7a1b9a443ac907f9e3aa2826b4460dba52ccce2007` |
| Content-address SHA-256 | `2c29815b27e4637d0af973e2ea0f2b635c4af00eba378f64c3e803b5357a558f` |
| Manifest SHA-256 | `5bbc27cd28e63131cfb6c7875bd7040dd88ffe3e1d8d72603a8214e373d7785a` |
| First-audit subject (historical) | `94e3d60c9785789f1b7e812a865a325fcb23475f` / verdict NOT_ACCEPTED preserved |

No Proteus activation into the re-audit project (`.proteus` absent after auditor).

## Re-auditor independence

| Field | Value |
| --- | --- |
| Host | Codex `codex-cli 0.153.4` |
| Executable | `%LOCALAPPDATA%\OpenAI\Codex\bin\27d6a192e9c98618\codex.exe` |
| Workspace | `C:\Projects\Proteus-GATE1-REAUDIT-001` |
| PID | 5896 |
| ephemeral | true |
| used_resume / fork / continue | false |
| Proteus mount / activate | **not performed** |
| Prompt | `GATE1_REAUDITOR_PROMPT.txt` |
| Prompt SHA-256 | `9f1001bb6b8c706c3f2a3caf45a61c0e10397686651600b9c76694d63ce44121` |
| Meta | `GATE1_REAUDITOR_META.json` |
| Raw | `GATE1_REAUDITOR_RAW_RESULT.txt` |
| Exit | 0 |

Transport: `~/.codex/.env` stashed (`GATE1_REAUDITOR_DOTENV_STASH.env`), restored after.

Origin verified major citation paths exist in the re-audit bundle. Re-auditor reported independent recalculation of 734 manifest hashes with 0 mismatches.

## First-audit blocker closure (re-auditor)

| Blocker | Re-auditor status |
| --- | --- |
| T04 | CLOSED |
| T05 | CLOSED |
| T11 | PARTIALLY_CLOSED |
| T09 | PARTIALLY_CLOSED |
| T02 / PROCESS_DEATH | CONTRADICTED (vs Cursor close/reopen contract) |
| L6 / T13 | PARTIALLY_CLOSED |

## L4 / L5 / L6 (re-auditor)

L4 SUPPORTED; L5 SUPPORTED_WITH_LIMIT; L6 PARTIAL — Gate minimum maturity **not** met.

## Re-auditor verdict (verbatim authority)

**NOT_ACCEPTED**

## Resulting Gate status

`GATE_1 = NOT_ACCEPTED`

(First audit NOT_ACCEPTED remains historical authority; re-audit confirms non-acceptance.)

## Next frontier (re-auditor Gate-critical blockers only)

Do not repair in this episode:

1. T02 with actual Cursor close/reopen and independent Cursor reentry from durable carriers.
2. T09 reconciliation of independently changed frontiers without last-write-wins semantic loss.
3. T13/L6 on the installed Cursor path, with later-cycle continuity attributable to installed capabilities rather than prompt-specified fixture steps.

## Non-blocking / post-gate (re-auditor)

ACCEPTED_OPEN_BOUNDARY: real secret unavailable; live Archivarius blocked; multi-machine reconciliation; Claude/OpenClaw; Drive observatory transport.  
POST_GATE: packaging, marketplace/product UX, broader activation coverage.
