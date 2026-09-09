# T03_POST_COMPACTION_PROMPT

Use in the **same** Cursor Agent conversation on workspace `C:\Projects\Proteus` **after** `/summarize` (or after an auto-compaction you can witness). Do not paste the pre-compaction transcript. Do not open `T03_BASELINE.json` or `freeze_t03_baseline.py`. Do not rerun T01, T02, or T02b. Do not upgrade T02. Do not mark T03 PASS unless the criteria in `T03_PRE_COMPACTION.md` succeed. A new chat with this prompt and no compaction is **FRESH_CHAT_NOT_T03**, not T03 PASS.

Token (protocol only; must **not** appear as a fabricated hook payload): `T03-COMPACT-7e4b2c91-6a1f-4d8e-9c3a-0f5b8a12d6e4`

```
You are BUILDER-01. T03 compaction continuity. T01 remains PASS. T02 remains PARTIAL. T02b remains PASS. T03 is NOT_RUN until you score it. Do not rerun T01/T02/T02b. Do not use a pasted pre-compaction transcript as authority. Do not open T03_BASELINE.json or freeze_t03_baseline.py.

1. Read AGENTS.md, state/IDENTITY.md, state/CURRENT.md, state/FRONTIER.md, state/DECISIONS.md, state/UNRESOLVED.md.
2. Read evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/RUN_RECEIPT.md, T02b_RESULT.md, T03_PRE_COMPACTION.md.
3. From those durable surfaces only, answer with file citations:
   - Who is acting, and what project/workspace/RUN_ID is this?
   - What is the current frontier?
   - What are the exact statuses of T01, T02, T02b, and T03-before-this-scoring?
   - What are the last 2–3 accepted decisions, each with provenance (not decision text alone)?
   - What unresolved/UNKNOWN/CONFLICT items remain? Do not resolve them.
4. Continuity probes (cite durable files; do not invent):
   P1. Recover D-003: brief decision AND its provenance. Provenance is required.
   P2. Name one CONFLICT that durable state refuses to resolve. Leave it unresolved.
   P3. Did T02b prove full OS process death/restart? Cite the process_marker fields durable state uses, and keep the recorded epistemic status.
   P4. Identify the local TEST_STEER command_id recorded for THIS RUN_ID.
5. Compaction boundary (separate from continuity). Recompute live telemetry hashes for %USERPROFILE%\.proteus\telemetry\cursor\<YYYY-MM-DD>\events.jsonl including any new day directory. Compare to the cutoff and last_event_id stated in T03_PRE_COMPACTION.md (not the JSON answer key). Assign exactly one primary boundary_class:
   - INTERNAL_PRECOMPACT if a post-cutoff preCompact row exists with event_name_source stdin|argv|stdin+argv, not simulated, not created by running python -m proteus.hook or hand-appended JSONL.
   - EXTERNAL_WITNESS_SUMMARIZE only if the operator’s message in this turn states they ran /summarize or saw summarized-conversation UI in this same chat — do not invent that witness.
   - INTERNAL_AND_EXTERNAL if both of the above.
   - FRESH_CHAT_NOT_T03 if this is a new composer conversation with no compaction of a prior window (including a new sessionStart without preCompact and no operator /summarize witness).
   - UNKNOWN_BOUNDARY otherwise.
   Do not count afterFileEdit/stop/sessionStart as compaction. Do not treat PROCESS_DEATH_BOUNDARY as this test.
6. Classification:
   - Combined T03 PASS only if continuity recovers identity, frontier, PASS vs PARTIAL vs UNKNOWN distinctions, probes P1–P4, provenance on P1, unresolved preserved, no pasted transcript, AND boundary_class is INTERNAL_PRECOMPACT or EXTERNAL_WITNESS_SUMMARIZE or INTERNAL_AND_EXTERNAL.
   - PARTIAL / FAIL / UNKNOWN per T03_PRE_COMPACTION.md. Fresh chat cannot be T03 PASS.
7. Update RUN_RECEIPT, CURRENT, FRONTIER, UNRESOLVED, CHECKPOINT, and write T03_RESULT.md. T02 stays PARTIAL. T02b stays PASS. Do not start T04.
8. Preserve UNKNOWN. Do not invent operator-layer claims.
```
