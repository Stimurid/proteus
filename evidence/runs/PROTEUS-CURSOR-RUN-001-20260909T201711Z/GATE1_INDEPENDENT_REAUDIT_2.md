# GATE1_INDEPENDENT_REAUDIT_2

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
When: 2026-09-11/12  
Origin role: BUILDER-01 recording only — **did not alter re-auditor-2 verdict**.

## Freeze

| Field | Value |
| --- | --- |
| Audited commit | `94e6f09d29c9c58bfaf01fac2917a0263cf54311` |
| Origin HEAD at freeze | identical |
| Working tree for subject | clean tracked tree; untracked isolated Cursor userdata dirs excluded via `git archive` |
| Snapshot method | `git archive --format=zip` → extract to isolated dir |
| Re-audit-2 bundle | `C:\Projects\Proteus-GATE1-REAUDIT-002` |
| Archive ZIP SHA-256 | `310a5e1843edee6e13ade58bdd202fd6f20653bac939ea58e4a951bc9b2f7bda` |
| Content-address SHA-256 | `32873ef7bfc5bee6b9199f738b543d832b7c8bf44361da22ad613797cb2b0cd3` |
| Manifest SHA-256 | `e74727a92adcde057fdad4cefbf8708f24b6c76f4601d72411154fc63d441a96` |
| File count | 821 |
| First-audit subject (historical) | `94e3d60…` / NOT_ACCEPTED preserved |
| Second-reaudit subject (historical) | `4b1f8d3…` / NOT_ACCEPTED preserved |

No Proteus activation into the re-audit-2 project (`.proteus` absent after auditor).

## Re-auditor-2 independence

| Field | Value |
| --- | --- |
| Host | Codex `codex-cli 0.153.4` |
| Executable | `%LOCALAPPDATA%\OpenAI\Codex\bin\27d6a192e9c98618\codex.exe` |
| Workspace | `C:\Projects\Proteus-GATE1-REAUDIT-002` |
| PID | 21836 |
| ephemeral | true |
| used_resume / fork / continue | false |
| Proteus mount / activate | **not performed** |
| Prompt | `GATE1_REAUDITOR_2_PROMPT.txt` |
| Prompt SHA-256 | `8e7d2b85e6d46e750c649ae2529f001a9e561335d34c9073466e706d02059e82` |
| Meta | `GATE1_REAUDITOR_2_META.json` |
| Raw | `GATE1_REAUDITOR_2_RAW_RESULT.txt` |
| Exit | 0 |

Transport: `~/.codex/.env` stashed (`GATE1_REAUDITOR_2_DOTENV_STASH.env`), restored after.

Origin verified major citation paths exist in the re-audit-2 bundle. Re-auditor reported 821/821 manifest hash matches.

## Final-three recheck (re-auditor-2)

| Item | Re-auditor-2 status |
| --- | --- |
| Cursor-native T02 | PARTIALLY_CLOSED |
| T09 shared-frontier reconciliation | PARTIALLY_CLOSED |
| Cursor-path T13 | PARTIALLY_CLOSED |
| L6 | PARTIAL |
| T11 | NON_BLOCKING_QUALIFICATION (PARTIALLY_CLOSED preserved; not upgraded) |

## L4 / L5 / L6 (re-auditor-2)

L4 SUPPORTED; L5 SUPPORTED_WITH_LIMIT; L6 PARTIAL — Gate minimum maturity **not** met.

## Re-auditor-2 verdict (verbatim authority)

**NOT_ACCEPTED**

## Resulting Gate status

`GATE_1 = NOT_ACCEPTED`

(First audit and second re-audit NOT_ACCEPTED remain historical authority; re-audit-2 confirms non-acceptance.)

## Next frontier (re-auditor-2 Gate-critical blockers only)

Do not repair in this episode:

1. Native Cursor-session evidence connecting Cursor B to independent reentry/recovery/use of A’s durable state, also establishing the T13/L6 fresh Cursor-session path.
2. Independently evidenced concurrent shared-base A1/B1 writes, reconciliation to R1, and an independently identified fresh reader.

## Non-blocking / post-gate (re-auditor-2)

ACCEPTED_OPEN_BOUNDARY: live Archivarius; AW1000 real secret; Drive transport; multi-machine sync; Claude/OpenClaw; Tyumen source access; portable Python prerequisite.  
POST_GATE: packaging, marketplace, UX, field deployment, broader activation coverage.

## Drive / recovery result

- Local recording commit: `be714ccf967cb254fc2b82e6b7020b162a878b5e`.
- Drive MCP status note id: `1EGU3KLWGx5w_Nzxl8Oj4U3ZL3vrhdvYMltw8hQAAWtg` (observatory folder).
- Follow-up recovery tip: `9d354d25e32128b4536cc2f71eb09ef50437e0b5`.
