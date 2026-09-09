# T01 CLEAN_REENTRY — PASS (externally witnessed)

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Test: T01 FRESH SESSION REENTRY (`_BOOTSTRAP/BLIND_START/50_GATE1_EVAL.md`)
Result: **PASS**
Do not rerun T01.

## Procedure as recorded

- Fresh Cursor Agent chat on workspace `C:\Projects\Proteus`.
- Started only from `CLEAN_REENTRY_PROMPT.md`.
- RUN-001 transcript was not pasted into that chat (operator/external witness).
- BUILDER-01 answered from durable state (`AGENTS.md`, `state/*`, `RUN_RECEIPT.md`) without asking the user to paste the previous conversation.

## What this process can and cannot prove

- **Can cite:** durable files named the actor BUILDER-01, project Proteus / Cursor, frontier (then: clean reentry then hooks/Drive), D-002, UNKNOWNs (hooks/restart, Agent CLI, Drive FAILED_TRANSPORT), test matrix, next step.
- **Cannot internally prove:** that the T01 context window contained no hidden RUN-001 transcript. Absence of contamination is **externally witnessed**, not internally provable. Record that limit; do not upgrade it to internal certainty.

## Evidence locations

- Prompt: `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/CLEAN_REENTRY_PROMPT.md`
- This receipt: `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/T01_CLEAN_REENTRY.md`
- Authoritative matrix: `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/RUN_RECEIPT.md` (T01 row + CLEAN_REENTRY = PASS)
- State: `state/CURRENT.md`, `state/FRONTIER.md`, `state/UNRESOLVED.md`

## Witness

External operator stated T01 CLEAN REENTRY is witnessed PASS (2026-09-09T21:53Z approx, local 2026-09-10). This file does not invent additional operator-layer claims.
