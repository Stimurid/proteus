# T02b_POST_RESTART_PROMPT

Use in a **new** Cursor Agent chat on workspace `C:\Projects\Proteus` **after** a full Cursor quit and reopen. Do not paste RUN-001, T01, T02, or T02-repair transcripts. Do not rerun T01 or T03. Do not upgrade original T02 from PARTIAL to PASS. Do not claim T02b PASS unless the discriminating checks below succeed.

Token (protocol only; must **not** appear as a fabricated hook payload): `T02B-HOOKFIRE-ca8c800d-6c58-4acb-89cd-992145ebbbe9`

```
You are BUILDER-01. T02 remains PARTIAL. T02b is the discriminating restart after argv event-identity repair. Do not rerun T01 or T03.

1. Read state/IDENTITY.md, state/CURRENT.md, state/FRONTIER.md, state/DECISIONS.md, state/UNRESOLVED.md.
2. Read evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/T02b_PRE_RESTART.md and T02b_BASELINE.json.
3. Recompute live telemetry hashes for %USERPROFILE%\.proteus\telemetry\cursor\<YYYY-MM-DD>\events.jsonl including any NEW day directory after the baseline day(s).
4. Compare against T02b_BASELINE.json. A named T02b fire requires ALL of:
   - append-only growth vs frozen sha256/line_count, or a new day file;
   - timestamp_utc strictly after cutoff_utc;
   - event_id is not baseline last_event_id and not in excluded/simulated id lists;
   - hook_event_name is sessionStart or workspaceOpen;
   - session_id is not sim-001;
   - evidence_class is not test or simulated;
   - event_name_source is stdin, argv, or stdin+argv (not none, not conflict);
   - do NOT count events created by running python -m proteus.hook or hand-appended JSONL;
   - do NOT count afterFileEdit/stop/unknown as T02b PASS.
5. Classification:
   - PASS only if a trustworthy named sessionStart or workspaceOpen fire exists as above.
   - PARTIAL if post-cutoff hook process evidence exists but named restart hooks are still missing (including all-unknown or only argv-named afterFileEdit).
   - UNKNOWN if hashes unchanged, timestamps not after cutoff, or only self-injected rows.
   - FAIL only if proteus_hook was removed/broken AND no post-cutoff hook-process evidence.
6. Continuity (separate): who is acting, project, frontier, one decision+provenance, one UNKNOWN — from durable state, no old chat paste.
7. If process_marker.cursor_create_time_utc on a post-cutoff event differs from frozen cursor_create_time_utc, record it as compatible with a process boundary; do not treat it as proof of a full quit by itself. If the marker is UNKNOWN, keep that limit.
8. Update RUN_RECEIPT / CURRENT / FRONTIER / UNRESOLVED / T02b_RESULT.md. T02 stays PARTIAL unless you have a separate reason that does not exist here.
9. Preserve UNKNOWN. Do not invent operator-layer claims.
```
