# Registry contracts

This directory contains executable, machine-readable contracts for Agentum registry surfaces. It preserves the source registries as YAML and does not turn theory or the research archive into runtime payload.

`agent_organ_record.schema.json` encodes the record shape from `03_THEORY/AGENT_ORGAN_RECORD_SPEC.md`; `scripts/agent_organ_registry.py` adds the checks JSON Schema cannot express cleanly: known relation IDs, duplicate IDs, lifecycle/trust compatibility, and self-lineage prevention.

The current contract deliberately validates only the compact registry lifecycle (`draft`, `candidate`, `selected`, `active`, `quarantined`, `retired`). The richer lifecycle remains governed by `03_THEORY/AGENTUM_ORGAN_TRUST_AND_LIFECYCLE.md` until the living registry adopts it.
