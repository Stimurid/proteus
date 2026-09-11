# GATE1_LAST_TWO_EVIDENCE_REQUIREMENTS

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Tip at map write: `e7b16755755a83a1e4502f2bd51e34122d9381c5`  
Gate: **NOT_ACCEPTED** (three independent verdicts preserved)  
Authority: `GATE1_INDEPENDENT_REAUDIT_2.md`, `GATE1_REAUDITOR_2_RAW_RESULT.txt`, `50_GATE1_EVAL.md` T02/T09/T13/L6

Do not reopen T04/T05/T11 or unrelated research lines.

---

## Blocker A — Cursor B–tied native session (T02 / T13 / L6)

### What prior evidence established
- Isolated Cursor A launch + kill with process tree death (`T02_CURSOR_NATIVE_*`, final-three episode).
- Fresh Cursor B launch with distinct PID against same isolated profile/workspace.
- Durable project state survived (inventory, PRE_BOUNDARY_MARKER, Proteus mount).
- A later **Cursor Agent CLI** session recovered Cycle1 work and extended it (`T13_L6_CURSOR_PATH_TWO_CYCLE.md`).
- Cycle2 prompt did not seed inventory/sizes; product extension was real.

### What re-auditor-2 specifically found missing
From raw §6 / §11 / §17:

> Cycle2 was a new Cursor Agent CLI invocation… evidence does not establish that the Agent CLI reentry was a session of, launched by, or otherwise causally tied to Cursor B. It is an external `cursor-agent` Node process.

> Mere temporal coexistence of Cursor B and Agent CLI does not prove Cursor-native session reentry.

> Minimum remaining: Native Cursor-session evidence connecting Cursor B to independent reentry/recovery/use of A’s durable state, also establishing the T13/L6 fresh Cursor-session path.

### Primary evidence that would close the gap
1. Cursor B process identity (PID/tree, user-data-dir, workspace) after A death.
2. An Agent chat/session **owned by / created through Cursor B** (not freestanding Agent CLI alone), with attribution via a defensible combination of: B window/process, B user-data-dir, B workspaceStorage / logs / conversation ID, timestamp correlation, UI evidence, and/or IPC ancestry.
3. New session: no resume/continue/thread reuse; ordinary RU reentry prompt only; prompt SHA-256 preserved.
4. Session recovers Cycle1 durable consequence and produces new durable work → closes T02 current + T13/L6 current in one causal chain.

Artifact: `T02_T13_CURSOR_B_NATIVE_SESSION.md`

---

## Blocker B — T09 primary concurrency + independent fresh reader

### What prior evidence established
- D-012 `proteus.frontier_reconcile` produces R1 with merge + CONFLICT + provenance; rejects LWW (`T09_SHARED_FRONTIER_RECONCILIATION.md`, unit tests).
- Re-auditor-2: “D-012 correctly produces an R1 receipt… rejects LWW.”

### What re-auditor-2 specifically found missing
From raw §6 / §11 / §17:

> primary evidence does not establish concurrent A1/B1 writes: branch receipts are sequentially timestamped and lack independent writer/session provenance. “Fresh reader” is a duplicate receipt with no independent reader identity.

> Minimum remaining: Independently evidenced concurrent shared-base A1/B1 writes, reconciliation to R1, and an independently identified fresh reader.

### Primary evidence that would close the gap
1. Shared S0 with recorded hash; two independent writer processes (distinct PIDs) both record S0 hash before write.
2. External barrier: both READY before release; neither consumes the other’s branch before write.
3. Post-barrier divergent A1/B1 (compatible + conflicting `next_step`); distinct write times OK if LWW still rejected.
4. Real `python -m proteus frontier reconcile` → R1 (not hand-built).
5. Third independent Reader C process/session: ordinary RU prompt only; recovers R1 + merge + conflict + both provenances; no A/B/reconciler transcript.

Artifact: `T09_PRIMARY_CONCURRENT_RECONCILIATION.md`

---

## Explicitly out of scope
T11 NON_BLOCKING_QUALIFICATION; T04/T05; world/AW1000/NR/Codex/secrets/Archivarius/packaging. No Gate re-audit in this episode.
