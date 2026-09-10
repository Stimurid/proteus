# UNRESOLVED / UNKNOWN / CONFLICT

- UNKNOWN (epistemic limit, T01): this process cannot internally prove the T01 chat was free of RUN-001 transcript contamination. Non-contamination is **externally witnessed**, not internally provable.
- UNKNOWN: whether a full Cursor OS process quit occurred. T02b Proteus `sessionStart` still carries frozen `cursor_pid` 40844 / `cursor_create_time_utc` `2026-09-09T22:51:16.147627+00:00`. A different Cursor.exe (pid 13224, create `2026-09-09T23:07:05Z`) hosted a `workspaceOpen` for `zarathustra-push`. Marker change is compatible with a process boundary, not a quit witness. T03 Proteus `preCompact` rows still show pid 40844 / the same create time.
- PARTIAL (T02 hooks): original T02 post-cutoff rows were all `hook_event_name=unknown`. Do not upgrade T02 to PASS. T02b (argv identity) is PASS; see `T02b_RESULT.md`.
- UNKNOWN: root cause of missing `hook_event_name` on GUI stdin JSON on this Windows Cursor. T02b named fires and T03 `preCompact` rows had `stdin_byte_count` > 0 but `event_name_stdin=null`; identity came from argv. H1/H2/H3 in `T02_DIAGNOSIS.md` still open.
- UNKNOWN: Toolhelp `process_marker` picks the first ancestor whose image contains `cursor`; multiple Cursor.exe create times coexist in one tree. Not an OS-quit proof.
- UNKNOWN: Cursor Agent CLI `agent` / `agent acp` binary location on this machine — not on PATH.
- UNKNOWN: `CURSOR_TRANSCRIPT_PATH` was empty in the bootstrap shell; transcript capture not verified.
- CONFLICT: Gate 1 eval file lists some plugin Drive IDs that differ from `70_PLUGIN_SOURCE_MAP.md` / `71_PLUGIN_RECOVERY_LEDGER.md`. Local packet copies are used; Drive ID conflict not resolved.
- UNKNOWN: whether stop-hook follow-up will fire in a live IDE conversation versus only after a later agent stop boundary.
- UNKNOWN (T03 trigger): live Proteus `preCompact` fired after freeze (`T03_RESULT.md`), but persisted events have no `trigger` field (`auto` vs `manual` unknown). This scoring turn did not contain an operator statement that `/summarize` ran or that a “Summarized conversation” UI was seen. Do not invent EXTERNAL_WITNESS_SUMMARIZE.
- OPEN (F01): whether D-004 / widened anti-reduction causes Proteus to name its own formalization losses during ordinary work, rather than only when explicitly audited. Text in IDENTITY/rules does not prove that behavior.
- OPEN (F01): next organ evidence is ordinary-work loss-naming or a human-chosen foreign-body mount — not a new hook-identity test. T11 remains PARTIAL.
- SOURCE_GAP (F01): no local Proteus passport; no file named constitution; Generous primary `07_14_…txt`, `про парадигму.md`, AI Quest Contract PDF, and `01_PROTEUS_CORPUS_MANIFEST` are not in this workspace. Full ChatGPT «плагин» corpus remains UNKNOWN (`71_PLUGIN_RECOVERY_LEDGER.md`).
- RESIDUE (F01): root `DECISIONS.md` / `UNKNOWN.md` / `DESIGN_v0.1.md` stamped SUPERSEDED/historical; their D-numbers must not be read as `state/DECISIONS.md`. Duplicate always-apply `.cursor/rules/proteus.mdc` removed (was not in installer mapping).
