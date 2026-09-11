# T09 RESULT — Parallel run safety

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Contract: `50_GATE1_EVAL.md` T09

## Execution

Two concurrent Codex ephemeral sessions on distinct bodies:

| Body | Workspace | Meta | Frontier marker preserved |
| --- | --- | --- | --- |
| R1 | `gate1_blocker_fixtures/T09_BODY_R1` | `T09_R1_META.json` | `alpha-frontier-marker-R1-ONLY` |
| R2 | `gate1_blocker_fixtures/T09_BODY_R2` | `T09_R2_META.json` | `beta-frontier-marker-R2-ONLY` |

Overlapping wall-clock runs (R1 started ~2s before R2). Each wrote `evidence/local_run_note.md` for its own body.

## Anti-LWW checks

- R1 frontier still contains alpha marker; not polluted by beta.
- R2 frontier still contains beta marker; not polluted by alpha.
- Separate project state roots — no shared FRONTIER file.

**T09 = PASS**

Historical dual-RUN_ID residue note unchanged (negative residue, not this PASS).
