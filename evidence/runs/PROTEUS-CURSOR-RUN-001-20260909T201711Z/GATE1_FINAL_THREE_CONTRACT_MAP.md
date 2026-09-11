# GATE1_FINAL_THREE_CONTRACT_MAP

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
When: 2026-09-11/12  
Tip at map write: `f90926eaf6b424f539444e738a7208f0499c276a`  
Gate status (unchanged): **NOT_ACCEPTED**  
Authority: `50_GATE1_EVAL.md`; `60_CURRENT_PROTEUS_STATUS.md`; `GATE1_INDEPENDENT_AUDIT.md`; `GATE1_INDEPENDENT_REAUDIT.md`; `GATE1_REAUDITOR_RAW_RESULT.txt`

Do **not** reopen T04/T05 or unrelated research lines.

T11 inherited from re-audit: PARTIALLY_CLOSED / not in minimum remaining blocker set — touch only if a required closure causally depends on it (not expected here).

---

## 1. Cursor-native T02

| Field | Content |
| --- | --- |
| Exact contract | `50_GATE1_EVAL.md` T02 FULL RESTART: “Pass: same continuity after closing/reopening Cursor.” Failure F02 restart amnesia. |
| Re-auditor rejection | Isolated Cursor kill + **Codex** successor “CONTRADICTED” vs Cursor close/reopen. Process death of Cursor was real; native successor path missing. |
| Causal property now required | Cursor process A → durable pre-state → actual Cursor termination → confirmed dead → **new Cursor process B** → **Cursor-native** reentry (not Codex) → recover/use pre-death durable state without resume/continue. |
| Reusable evidence | `PROCESS_DEATH_RESULT.md` / PRE/POST JSON: isolated `--user-data-dir` kill method; origin IDE preserved. |
| Missing alone | Fresh Cursor B launch + Cursor-native (Agent) reentry proving continuity after reopen. |

---

## 2. T09 shared-frontier reconciliation

| Field | Content |
| --- | --- |
| Exact contract | `50_GATE1_EVAL.md` T09: “separate RUN/BODY/project frontiers are preserved and can be reconciled without last-write-wins semantic loss.” Failure F07. |
| Re-auditor rejection | Concurrent isolated bodies retained markers but **never contended for or reconciled a shared frontier**; no-LWW reconciliation untested. Isolated workspaces made overwrite impossible by construction. |
| Causal property now required | Shared base S0 → concurrent A1 & B1 on **shared** frontier substrate → distinct reconciliation → R1 with both provenance; merge compatible; CONFLICT/UNKNOWN for incompatible; fresh reader sees R1 not last writer only. |
| Reusable evidence | Prior T09 concurrent isolation (negative control that separate bodies don’t clobber); world `write_claim` no-LWW conflict marking as donor pattern — **not** itself a frontier reconcile PASS. |
| Missing alone | Shared-frontier branch writes + reconcile operation emitting R1 + fresh-reader proof. |

---

## 3. Cursor-path T13 / L6

| Field | Content |
| --- | --- |
| Exact contract | T13: after installation, bounded evidence-driven Proteus product improvement while **using newly installed continuity/checkpoint/install-update**; tests/rollback intact. L6: “installed capabilities safely participate in a subsequent product-development change.” F12 second-cycle failure. |
| Re-auditor rejection | Cycles were Codex-led on Cursor fixture; prompt directed continuity/checkpoint steps; attribution to installed Cursor capabilities ambiguous. |
| Causal property now required | Activate via supported Cursor path → Cycle1 ordinary Cursor-agent task (**no** cycle/L6/token coaching) → hard Cursor process boundary → Cycle2 new Cursor process + new Cursor agent with ordinary continuation (RU prompt as specified) reconstructing Cycle1 durables and producing new work. |
| Reusable evidence | Activate mechanism; prior process-death method; prior T13 structure as negative lesson (do not repeat prompt-directed Codex cycles). |
| Missing alone | Cursor-agent Cycle1 + Cursor reopen + Cursor-agent Cycle2 with causal dependency and no prompt-seeded memory. |

---

## Combination note

T02 native reopen and T13 Cycle1→boundary→Cycle2 **may share** one physical Cursor death/reopen if evidence independently demonstrates both properties. T09 remains separate.
