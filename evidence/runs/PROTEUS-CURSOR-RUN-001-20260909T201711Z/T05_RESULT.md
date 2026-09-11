# T05 RESULT — Project isolation

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Contract: `50_GATE1_EVAL.md` T05

## Evidence crosswalk (prior)

`WORLD_MEMORY_TWO_SESSION.md`: PROJECT_A decision did not become entity truth in PROJECT_B; shared ENTITY recovered without project-local corpus copy. **Partial prior satisfaction** of T05 for scoped memory.

## Missing-delta execution

- Fixture A holds project-local decision `LOCAL_ONLY_TOKEN=ISO-A-77QX`.
- Independent Codex in fixture B only (`T05_META.json`); prompt forbids opening A.
- Raw (`T05_RAW.txt`): no LOCAL_ONLY_TOKEN decision in B; value **UNKNOWN**.

## Status

**T05 = PASS** (prior world-memory isolation + current local-decision non-leak).

Historical world-memory episode not rewritten.
