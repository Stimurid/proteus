# GATE1_BLOCKER_CONTRACT_MAP

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
When: 2026-09-11  
Authority freeze (audited subject): `94e3d60c9785789f1b7e812a865a325fcb23475f`  
Recording tip at map write: `41fbcdbc96be8e216fb720c347cbefc6494f3708`  
Gate status (unchanged by this map): **NOT_ACCEPTED** (auditor verdict preserved)

Primary authority: `_BOOTSTRAP/BLIND_START/50_GATE1_EVAL.md`, `_BOOTSTRAP/BLIND_START/60_CURRENT_PROTEUS_STATUS.md`, `_BOOTSTRAP/BLIND_START/21_PRODUCT_BACKLOG.md` (G1 P0-14 / G2), durable `state/*`, `GATE1_INDEPENDENT_AUDIT.md`, `GATE1_AUDITOR_RAW_RESULT.txt`.

Auditor blocker set treated as exhaustive unless a material contract mismatch is shown below. **No material mismatch found** — auditor mapped Gate tests/levels to source correctly; interpretation of L6/T13 as requiring an unambiguous post-install developmental second cycle is within `50_GATE1_EVAL` T13 + L6 + failure family F12 + backlog P0-14.

---

## T04 — CORRECTION LEARNING (= L4)

| Field | Content |
| --- | --- |
| Exact source | `50_GATE1_EVAL.md` §4 T04; L4 “LEARNS — correction changes future independent behavior”; backlog P1-9 |
| Requirement | Procedure: a meaningful correction is given; a **later independent session** meets an **analogous** situation. Pass: behavior changes appropriately **and** provenance of the learned rule/skill is recoverable. |
| Available evidence | Correction *capture* skill/template exists (`proteus-correction`); not an executed T04 behavioral episode. Auditor: unrun. |
| Satisfies | **none** of the behavioral pass criteria |
| Missing delta | Execute correction → durable capture/promotion → independent analogous session → prove changed behavior + recoverable provenance |
| Code change? | Only if execution exposes a causal defect; skill/surfaces already exist |

---

## T05 — PROJECT ISOLATION

| Field | Content |
| --- | --- |
| Exact source | `50_GATE1_EVAL.md` §4 T05; failure F05; backlog P1-5 |
| Requirement | Project-local facts/rules do **not** silently become global or leak into an unrelated project. |
| Available evidence | `WORLD_MEMORY_TWO_SESSION.md`: PROJECT_A decision did **not** appear as entity truth in PROJECT_B; shared ENTITY recovered without project-local corpus copy. D-006 activate preserves foreign AGENTS / non-`proteus-*` rules. |
| Satisfies | **part** — strong for scoped world memory + activate coexistence; not yet a dedicated T05-labeled behavioral episode covering project **rules/facts** isolation in general |
| Missing delta | Formal crosswalk + one narrow behavioral check that project-local durable fact/rule in project A is absent from unrelated project B when B is entered independently |
| Code change? | Likely execution/evidence only |

---

## T09 — PARALLEL RUN SAFETY

| Field | Content |
| --- | --- |
| Exact source | `50_GATE1_EVAL.md` §4 T09; failure F07; backlog P1-4; L3 mentions parallel work |
| Requirement | Separate RUN/BODY/project frontiers are preserved and can be reconciled **without last-write-wins semantic loss**. |
| Available evidence | Historical dual RUN_ID folders `2015Z`/`201711Z` noted as parallel-writer residue (negative residue, not a PASS). World memory scopes ENTITY vs PROJECT. No dedicated T09 PASS episode. |
| Satisfies | **none** as a Gate T09 demonstration |
| Missing delta | Two concurrent/near-concurrent independent bodies/runs with distinct frontiers; prove both survive without silent overwrite; show reconciliation path |
| Code change? | Only if frontiers collide due to a causal defect |

---

## T11 — ORGAN PRESERVATION (= L5 core behavioral)

| Field | Content |
| --- | --- |
| Exact source | `50_GATE1_EVAL.md` §4 T11; L5 “PRESERVES ORGANS”; `60_CURRENT` LLM-ORGAN PRESERVATION + REDUCTION DETECTION tests |
| Requirement | Input: task specifying a living LLM-native agent/organ with semantic judgment, open-ended dialogue, uncertainty. Fail: keyword router / deterministic switch / fixed state machine/graph substitutes the organ without explicit agreement. Pass: implementation preserves transformer/LLM-native function and makes any necessary formal boundary explicit. |
| Available evidence | Historical: rule/anti-reduction text present; RUN_RECEIPT T11 **PARTIAL** (no independent organ task). F01/D-004 de-equation. F05/F06 show recruitment/transduction on form transitions — **related but not identical** to implementing an LLM-native organ under coding pressure. |
| Satisfies | **part** (constitutional text + later anti-reduction behavior on different tasks) |
| Missing delta | One narrow independent coding task that asks for an LLM-native judgment organ; score reduction vs preservation; keep historical PARTIAL intact |
| Code change? | Only if Proteus morphology causally forces reduction |

---

## T02 / T02b / PROCESS_DEATH_BOUNDARY

| Field | Content |
| --- | --- |
| Exact source | `50_GATE1_EVAL.md` T02 “FULL RESTART — same continuity after closing/reopening Cursor”; failure F02; backlog P1-2; durable UNRESOLVED PROCESS_DEATH_BOUNDARY UNKNOWN; `T02_RESULT.md` PARTIAL; `T02b_RESULT.md` named-hook PASS without OS quit proof |
| Requirement | Continuity after Cursor close/reopen. Process-death proof (from campaign practice + auditor): pre-death process alive; termination crosses process boundary; successor is not conversational continuation; durable reentry works; old PID not falsely surviving; raw before/death/after evidence. |
| Available evidence | T02 PARTIAL (unknown hook names / quit unproven). T02b named fires PASS. Fresh sessions, portable reconstruct, CLI instantiation — **do not** equal process death. |
| Satisfies | **part** (continuity-without-paste and named hooks); process-death **none** |
| Missing delta | Autonomous isolated process death + successor reentry evidence; do not kill live origin coordinator |
| Code change? | Unlikely; host/process experiment |

---

## T13 / L6 — FIRST POST-INSTALL SECOND-CYCLE

| Field | Content |
| --- | --- |
| Exact source | `50_GATE1_EVAL.md` T13 + L6; failure F12; backlog P0-14 “bounded second product improvement through that path” |
| Requirement | After installation, one bounded evidence-driven **Proteus product improvement** is performed while **actually using** newly installed continuity/checkpoint/install-update capabilities; tests and rollback remain intact. L6: installed capabilities safely participate in a subsequent product-development change. Auditor: must be temporally/causally distinct second cycle using durable consequences of a prior cycle — not two back-to-back commands in one semantic action, not origin-transcript authority. |
| Available evidence | Many install→improve cycles in origin chat; **not** labeled unambiguous post-install second-cycle with independent reentry. Auditor: no unambiguous L6/T13. |
| Satisfies | **none** as Gate-specific T13/L6 episode |
| Missing delta | Install/activate → cycle-1 improvement+checkpoint using installed surfaces → independent later cycle-2 that recovers cycle-1 durables and performs another bounded Proteus improvement with tests/rollback intact |
| Code change? | Only if installed path is broken |

---

## L4 / L5 / L6 (maturity)

| Level | Source definition | Maps to |
| --- | --- | --- |
| L4 LEARNS | correction changes future independent behavior | T04 |
| L5 PRESERVES ORGANS | coding does not silently reduce LLM-native mechanisms | T11 (+ 60_CURRENT organ tests) |
| L6 SECOND-CYCLE WORKS | installed capabilities safely participate in subsequent product-development change | T13 |

Gate 1 not accepted below L6 for Proteus itself (`50_GATE1_EVAL.md` §6).
