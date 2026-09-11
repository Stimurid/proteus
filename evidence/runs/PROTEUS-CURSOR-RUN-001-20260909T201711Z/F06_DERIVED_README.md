# Derived registry outputs

These files are reproducible hygiene artifacts, not source-of-truth registry records.

Regenerate `agent_organ_registry_report.json` from the repository root:

```powershell
python scripts/agent_organ_registry.py validate
python scripts/agent_organ_registry.py report
```

The report is deterministic for a given source registry: it includes the source SHA-256 and does not include a generation timestamp.
