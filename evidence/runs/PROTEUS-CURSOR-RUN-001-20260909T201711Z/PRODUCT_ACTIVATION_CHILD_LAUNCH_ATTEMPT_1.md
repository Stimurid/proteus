# PRODUCT_ACTIVATION_CHILD_LAUNCH_ATTEMPT_1

When: 2026-09-10T16:27:56Z
Result: **FAIL (launcher)** — child Agent not started.
Cause: PowerShell `Get-Content` raced / failed to read `PRODUCT_ACTIVATION_CHILD_PROMPT.txt` at launch; multiline `--prompt` argv then missing → `_fresh_agent_launcher.py: error: argument --prompt: expected one argument`.
Repair: launcher gains `--prompt-file`; attempt 2 uses prompt file only (no semantic prompt change).
