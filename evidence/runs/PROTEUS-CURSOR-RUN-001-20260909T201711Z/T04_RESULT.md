# T04 RESULT — Correction learning

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Contract: `50_GATE1_EVAL.md` T04 / L4  
Historical: unrun → **current PASS**

## Procedure executed

1. Meaningful correction captured and promoted in fixture `gate1_blocker_fixtures/T04_CORRECTION`:
   - `state/corrections/20260911T220000Z_urgency_unknown.md`
   - `state/DECISIONS.md` D-T04-1 (do not invent default urgency; prefer UNKNOWN)
2. Later **independent** Codex ephemeral session (`T04_META.json`, PID in meta, `used_resume=false`).
3. Analogous triage task; prompt did **not** contain the correction text / UNKNOWN instruction (`T04_INDEPENDENT_PROMPT.txt`; launch prompt_sha256 `11f9b94924dce982eb52ee00004f905c4b57f43fa99cfc18f10f3ad195389e68`).

## Result

Raw (`T04_RAW.txt`): urgency **UNKNOWN**; cited durable correction/decision files.

**T04 = PASS** (behavior changed appropriately; provenance recoverable).

No code repair required.
