# T09_SHARED_FRONTIER_RECONCILIATION

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Contract: `50_GATE1_EVAL.md` T09 — frontiers preserved and reconciled without last-write-wins.  
Authority for gap: `GATE1_INDEPENDENT_REAUDIT.md` (T09 PARTIALLY_CLOSED — no shared reconcile).  
Mechanism: D-012 `proteus.frontier_reconcile` / `python -m proteus frontier`.

Historical prior T09 concurrent-isolation claim remains historical; this episode is **current** shared-frontier reconciliation.

## Causal form executed

1. Shared base **S0** — `T09_S0_BASE.json` / fixture `.proteus/frontier_base.json`
2. Concurrent **A1** (`session.A.worker`): next_step = login flow; shared_note = document CLI — `T09_BRANCH_A.json`
3. Concurrent **B1** (`session.B.worker`, later timestamp): next_step = offline cache; risk = UNKNOWN — `T09_BRANCH_B.json`
4. Distinct reconcile → **R1** — `T09_RECONCILE_R1.json` / `.proteus/FRONTIER_RECONCILED.json`
5. Fresh independent reader — `T09_FRESH_READER.json`

Fixture: `gate1_final3_fixtures/T09_SHARED`

## Results

| Check | Result |
| --- | --- |
| A and B both retained as branches | yes (`branch_ids` A,B) |
| B later than A (LWW temptation) | A_utc < B_utc |
| Compatible merge (`constraint`, `shared_note`, themes) | in `merged` |
| Incompatible `next_step` | CONFLICT with both candidates; `resolution=UNRESOLVED` |
| Timestamp LWW rejected | `rejected_methods` includes `last_write_wins` / `recorded_utc_order` |
| UNKNOWN risk preserved | in `unknowns` |
| Fresh reader sees R1 + both provenances | yes |

## Status

**T09 current shared-frontier reconciliation = PASS**

Historical concurrent-isolation T09 evidence remains as originally recorded.
