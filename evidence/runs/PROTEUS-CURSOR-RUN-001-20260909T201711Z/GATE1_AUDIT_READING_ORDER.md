# Gate 1 audit reading order (bundle-local paths)

## Authority / constitution
- `_BOOTSTRAP/BLIND_START/50_GATE1_EVAL.md` — Gate 1 eval + tests + acceptance levels
- `_BOOTSTRAP/BLIND_START/60_CURRENT_PROTEUS_STATUS.md` — status/function/boundaries/acceptance v0.1
- `_BOOTSTRAP/BLIND_START/11_AGENT_CAPABILITY_BACKLOG.md`
- `_BOOTSTRAP/BLIND_START/21_PRODUCT_BACKLOG.md`
- `state/IDENTITY.md`, `state/CURRENT.md`, `state/FRONTIER.md`, `state/DECISIONS.md`, `state/UNRESOLVED.md`
- `OPEN_BOUNDARIES_FOR_AUDIT.md`
- `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/WORKING_ARCHITECTURE_AIYE_PROTEUS_ARCHIVARIUS_ENTITY_v0.1.md` (if present)
- `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/RUN_RECEIPT.md`

## Core evidence
See episode MDs and raw outputs under `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/` (T01–T03, F01, portable handoff, fresh incarnation, product activation, world memory, AW1000, F04–F06).

## Implementation surfaces
`src/proteus/`, `hosts/cursor/`, `hosts/codex/`, `tests/`

## Constraint
Do not use the live origin tree outside this audit directory. Do not install/activate Proteus. Do not patch code or rewrite evidence.
