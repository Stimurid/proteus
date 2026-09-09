# UNRESOLVED / UNKNOWN / CONFLICT

- UNKNOWN (epistemic limit, T01): this process cannot internally prove the T01 chat was free of RUN-001 transcript contamination. Non-contamination is **externally witnessed**, not internally provable.
- UNKNOWN: whether a full Cursor OS process quit occurred. T02b Proteus `sessionStart` still carries frozen `cursor_pid` 40844 / `cursor_create_time_utc` `2026-09-09T22:51:16.147627+00:00`. A different Cursor.exe (pid 13224, create `2026-09-09T23:07:05Z`) hosted a `workspaceOpen` for `zarathustra-push`. Marker change is compatible with a process boundary, not a quit witness.
- PARTIAL (T02 hooks): original T02 post-cutoff rows were all `hook_event_name=unknown`. Do not upgrade T02 to PASS. T02b (argv identity) is PASS; see `T02b_RESULT.md`.
- UNKNOWN: root cause of missing `hook_event_name` on GUI stdin JSON on this Windows Cursor. T02b named fires had `stdin_byte_count` > 0 but `event_name_stdin=null`; identity came from argv. H1/H2/H3 in `T02_DIAGNOSIS.md` still open.
- UNKNOWN: Toolhelp `process_marker` picks the first ancestor whose image contains `cursor`; multiple Cursor.exe create times coexist in one tree. Not an OS-quit proof.
- UNKNOWN: Cursor Agent CLI `agent` / `agent acp` binary location on this machine — not on PATH.
- UNKNOWN: `CURSOR_TRANSCRIPT_PATH` was empty in the bootstrap shell; transcript capture not verified.
- CONFLICT: Gate 1 eval file lists some plugin Drive IDs that differ from `70_PLUGIN_SOURCE_MAP.md` / `71_PLUGIN_RECOVERY_LEDGER.md`. Local packet copies are used; Drive ID conflict not resolved.
- UNKNOWN: whether stop-hook follow-up will fire in a live IDE conversation versus only after a later agent stop boundary.
- UNKNOWN (T03 until boundary): whether IDE `/summarize` emits a live `preCompact` hook row on this Windows Cursor; zero `preCompact` events at T03 freeze. Do not treat a new chat as compaction.
