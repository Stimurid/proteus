# F06 — Hidden source-vs-representation comparison (origin)

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Child commit (Agentum): `117a8211f30c2c5a795ab511c0f9ffef199c86a8`  
Formal representation: `registry_contracts/agent_organ_record.schema.json` + `scripts/agent_organ_registry.py`  
Derived report: `02_REGISTRIES/derived/agent_organ_registry_report.json`

## Form transition

Narrative/design organ-record theory (`03_THEORY/AGENT_ORGAN_RECORD_SPEC.md`, trust/lifecycle companion) → machine-readable JSON Schema + executable validator → hygiene report over living YAML registry.

## Consequential distinctions

| Distinction | Fate in formalization | Class |
| --- | --- | --- |
| Compact status vocabulary (draft…retired) | Encoded as enum in schema | **Carried** |
| Richer lifecycle (probation, installed, field_proven, deprecated, merged, rejected) | Explicitly **not** encoded; README points to theory doc as remaining governor | **Omitted visibly** / reopenable |
| Trust levels + selected/active trust gates | Encoded in schema + semantic validator rules | **Carried** / **Transformed** (rules are operationalization) |
| Field meanings / review questions / anti-patterns | Not in schema; remain in theory | **Omitted visibly** (correct compression) |
| Entity typology object-class boundary | Referenced by theory; not duplicated as typology machine model | **Omitted** — not falsely asserted complete |
| Required relations (deficit, scenes, failures, install scope) | Partially transformed into ID cross-checks + minItems | **Transformed** |
| `output_class` enum | Present in theory; was missing on all living records; child filled values aligned to organ function | **Carried** with **repair of living registry**; values inferred from existing function text (not arbitrary enums) |
| Registry YAML as living source vs schema as contract vs report as derived | README + report `source.path`/`sha256`; derived README “not source-of-truth” | **Jurisdiction preserved** |
| Claim that schema = full organ ontology | Rejected by deliberate compact-only validation | **Not collapsed** |

## Downstream receiver (artifact-only)

Receiver used schema/report/validator/README + registry YAML without theory corpus.

- Reproduced validate/report success (7 organs ok).
- Correctly stated contract purpose, inventory, source SHA lineage.
- Correctly stated derived artifacts are **not** source-of-truth.
- Correctly restated compact-vs-richer lifecycle limitation from contract README.

No false completeness claim observed.

## Semantic flattening / failure observed

- Mild: inventing previously-absent `output_class` values to satisfy the required field — mitigated because enum set matches theory and choices track each organ’s stated function.
- Residual: optional `proteus derived record` not used; relation is carried by README/report instead (acceptable; not required).
- No dominant collapse of richer lifecycle into compact enums as “the full truth.”
