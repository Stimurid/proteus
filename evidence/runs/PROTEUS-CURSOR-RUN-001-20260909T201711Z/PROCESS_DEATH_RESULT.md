# PROCESS_DEATH_BOUNDARY / T02 gap closure

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`

## Contracts

- T02 (`50_GATE1_EVAL.md`): continuity after closing/reopening Cursor.
- Campaign PROCESS_DEATH_BOUNDARY: real process termination, not new-chat / sessionStart-only / frozen same PID.
- Historical: `T02_RESULT.md` **PARTIAL** (unchanged); `T02b_RESULT.md` named-hook PASS without OS quit proof.

## Method (autonomous; origin IDE not killed)

1. Freeze pre-existing Cursor PIDs.
2. Launch **isolated** Cursor: `Cursor.exe -n --user-data-dir <episode/gate1_isolated_cursor_userdata2> <T13_BODY>`.
3. Collect launcher descendants + CommandLine matches for that user-data-dir.
4. Safety filter: never kill pre-existing origin PIDs.
5. Force-terminate isolated tree; verify targets gone (`PROCESS_DEATH_POST.json` terminated=true).
6. Origin Cursor process count remained non-zero (coordinator preserved).
7. Successor: **new** ephemeral Codex session (no resume) on same durable fixture — T13 cycle-2 — recovered cycle-1 state and continued work.

## Evidence checklist

| Requirement | Evidence |
| --- | --- |
| Pre-death alive | `PROCESS_DEATH_PRE.json` launcher/tree/cmdline PIDs |
| Termination crossed boundary | `PROCESS_DEATH_POST.json` terminated=true; still_alive=[] |
| Successor ≠ conversational continue | `T13_CYCLE2_META.json` ephemeral, used_resume=false |
| Durable reentry survived | Cycle-2 recovered CYCLE1_CHECKPOINT / FRONTIER; wrote CYCLE2_* |
| Old PID not claimed surviving | Post file lists kill targets; still_alive empty |
| Raw before/death/after | PRE/POST JSON + cycle1/cycle2 raw |

## Status

- **PROCESS_DEATH_BOUNDARY = PASS** (isolated Cursor process death + durable successor continuity).
- **T02 historical = PARTIAL** (unchanged).
- **T02 current Gate satisfaction = PASS** for the process-death continuity gap the auditor named (close Cursor body + independent successor continuity). Does not rewrite T02b or original T02 episode files.
