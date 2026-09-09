# T02_POST_RESTART_PROMPT

Use in a **new** Cursor Agent chat on workspace `C:\Projects\Proteus` **after** a full Cursor quit and reopen. Do not paste RUN-001 or T01 transcripts. Do not rerun T01. Do not claim T02 PASS unless the discriminating checks below succeed.

Token (protocol only; must **not** appear as a fabricated hook payload): `T02-HOOKFIRE-145f0152-155e-4362-ac8c-801e9e1c7ba9`

```
You are BUILDER-01. T01 CLEAN_REENTRY is already PASS. Do not rerun T01.

1. Read state/IDENTITY.md, state/CURRENT.md, state/FRONTIER.md, state/DECISIONS.md, state/UNRESOLVED.md.
2. Read evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/T02_PRE_RESTART.md and T02_BASELINE.json.
3. Recompute live telemetry hashes for:
   - %USERPROFILE%\.proteus\telemetry\cursor\<YYYY-MM-DD>\events.jsonl
   - including any NEW day directory after the baseline day 2026-09-09
4. Compare against T02_BASELINE.json. A new hook firing requires ALL of:
   - append-only growth: new lines and/or a new day file; do not treat a rewritten file with the same last event_id as a fire;
   - at least one event with timestamp_utc strictly after cutoff_utc in T02_BASELINE.json;
   - that event_id is not the baseline last_event_id and does not belong to the pre-restart named simulated set (sim-001 sessionStart, scripted workspaceOpen);
   - do NOT count events you create in this chat by running python -m proteus.hook or otherwise injecting JSONL.
5. Classification (hooks):
   - PASS only if a post-cutoff event has hook_event_name workspaceOpen or sessionStart (not sim-001) — trustworthy named Cursor hook after restart.
   - PARTIAL if post-cutoff events exist but all are hook_event_name=unknown (command ran; event name still unproven).
   - UNKNOWN if hashes unchanged, timestamps not after cutoff, or the only new rows are self-injected.
   - FAIL only if you have positive evidence hooks were removed/broken (e.g. hooks.json missing proteus_hook) AND no post-cutoff hook process evidence.
6. Also answer continuity (Gate 1 T02, separate from hooks): who is acting, project, frontier, one decision+provenance, one UNKNOWN — from durable state, without asking for old chat paste.
7. Update RUN_RECEIPT / CURRENT / FRONTIER / UNRESOLVED / a T02_RESULT.md to match the classification. Do not claim T02 PASS if hooks are PARTIAL or UNKNOWN.
8. Preserve UNKNOWN. Do not invent operator-layer claims.
```
