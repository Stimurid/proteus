# T03 RESULT

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Protocol token (not a hook payload): `T03-COMPACT-7e4b2c91-6a1f-4d8e-9c3a-0f5b8a12d6e4`
Compared against cutoff in `T03_PRE_COMPACTION.md` (`cutoff_utc` `2026-09-09T23:34:01.327387+00:00`, frozen last_event_id `7763b83b-aad8-4c5e-95d9-0c1a6f35dbaf`, `precompact_count_at_freeze` 0).
This chat: same composer conversation executing `T03_POST_COMPACTION_PROMPT.md`. T01/T02/T02b were not rerun. `python -m proteus.hook` was not run in this scoring turn. `T03_BASELINE.json` and `freeze_t03_baseline.py` were not opened. Pre-compaction transcript was not used as authority for state. Original T02 stays **PARTIAL**. T02b stays **PASS**. PROCESS_DEATH_BOUNDARY stays **UNKNOWN**. T04 was not started.

## Classification

| Layer | Result |
| --- | --- |
| Continuity (durable state) | **PASS** |
| Boundary class | **INTERNAL_PRECOMPACT** |
| Combined T03 | **PASS** |
| EXTERNAL_WITNESS_SUMMARIZE | **not claimed** — this operator turn did not state that `/summarize` ran or that a “Summarized conversation” UI was seen |
| FRESH_CHAT_NOT_T03 | **No** — Proteus `preCompact` rows name this conversation’s transcript `1e21d40e-5fd1-4bcf-98e6-89be84f64760` |
| Original T02 | **PARTIAL** (unchanged) |
| T02b | **PASS** (unchanged) |
| PROCESS_DEATH_BOUNDARY | **UNKNOWN** (unchanged) |

Combined PASS is continuity PASS plus a real `preCompact` fire after freeze. It does **not** prove `/summarize` versus auto-compact (`trigger` not persisted). It does **not** prove OS quit.

## Continuity — recovered from durable surfaces

Authority: `AGENTS.md`, `state/IDENTITY.md`, `state/CURRENT.md`, `state/FRONTIER.md`, `state/DECISIONS.md`, `state/UNRESOLVED.md`, `RUN_RECEIPT.md`, `T02b_RESULT.md`, `T03_PRE_COMPACTION.md`, plus live queue files under `%USERPROFILE%\.proteus\control\queue\`.

### Who / project / RUN_ID

- Acting incarnation: **BUILDER-01**, Cursor host, Proteus v0.1 ideal body (`AGENTS.md`, `state/IDENTITY.md`).
- Project / workspace: Proteus at `C:\Projects\Proteus` (`state/CURRENT.md`, `RUN_RECEIPT.md`).
- RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z` (`state/CURRENT.md`, `RUN_RECEIPT.md`).
- MACHINE_ID: `749855dd-cf0e-462a-85ce-5d5c133eda97` (`RUN_RECEIPT.md`; matches live `preCompact` `machine_id`).

### Frontier at scoring time (before this result)

`state/FRONTIER.md`: T03 compaction boundary — same Agent conversation, `/summarize`, then boxed text in `T03_POST_COMPACTION_PROMPT.md`. T03 was PREPARED / NOT_RUN until this scoring.

### Test statuses before this scoring

From `state/CURRENT.md` and `T03_PRE_COMPACTION.md` freeze line:

| ID | Status before this scoring |
| --- | --- |
| T01 CLEAN_REENTRY | PASS (externally witnessed) |
| T02 | PARTIAL (do not upgrade) |
| T02b | PASS (named argv sessionStart/workspaceOpen; OS quit UNKNOWN) |
| T03 | PREPARED / NOT_RUN |
| PROCESS_DEATH_BOUNDARY | UNKNOWN |
| Gate 1 | NOT_YET |

### Last accepted decisions (with provenance)

From `state/DECISIONS.md`:

- **D-001** — Cursor `AGENTS.md` + always-apply `.cursor/rules` + project/user `hooks.json` command hooks + Python installer. Provenance: PRODUCT_SPEC §2 + host inspection of Cursor 3.19.13 docs (`sessionStart.additional_context`, `stop.followup_message`).
- **D-002** — local append-only JSONL + local observatory mirror; Drive flush FAILED_TRANSPORT. Provenance: WORKLOG spec §13 failure principle + first-run host evidence.
- **D-003** — `--hook-event` argv identity when stdin JSON has no event name; `event_name_source` is `stdin` \| `argv` \| `stdin+argv` \| `none` \| `conflict`; conflict recorded, no winner; timing not used to name events. Provenance: T02 PARTIAL (empty-stdin live spool) + Cursor hooks docs allowing extra argv on `command` + isolated `.cmd` pipe diagnostic (`T02_DIAGNOSIS.md`).

### Unresolved (not resolved here)

From `state/UNRESOLVED.md` (abbreviated, left open):

- T01 non-contamination is externally witnessed, not internally provable.
- Full Cursor OS quit unproven after T02b (pid **40844** / `cursor_create_time_utc` `2026-09-09T22:51:16.147627+00:00` still on Proteus `sessionStart`).
- GUI stdin still lacks `hook_event_name`; H1/H2/H3 open.
- Toolhelp `process_marker` is not an OS-quit proof.
- Agent CLI not on PATH; `CURSOR_TRANSCRIPT_PATH` empty at bootstrap.
- **CONFLICT:** Gate 1 eval plugin Drive IDs vs `70_PLUGIN_SOURCE_MAP.md` / `71_PLUGIN_RECOVERY_LEDGER.md`.
- Stop-hook follow-up in live IDE vs later stop boundary: UNKNOWN.

### Continuity probes

**P1 (provenance).** D-003 as above: argv `--hook-event` when stdin has no event name; provenance is T02 empty-stdin PARTIAL + Cursor hooks docs extra argv + `T02_DIAGNOSIS.md`. Cited `state/DECISIONS.md`.

**P2 (CONFLICT).** Gate 1 eval file lists some plugin Drive IDs that differ from `70_PLUGIN_SOURCE_MAP.md` / `71_PLUGIN_RECOVERY_LEDGER.md`. Local packet copies are used; Drive ID conflict is **not** resolved. Cited `state/UNRESOLVED.md`.

**P3 (UNKNOWN process death).** T02b did **not** prove full OS process death/restart. Durable fields: Proteus `sessionStart` `cursor_pid` **40844**, `cursor_create_time_utc` **`2026-09-09T22:51:16.147627+00:00`**. Marker change on a different Cursor.exe is compatible with a process boundary, not a quit witness. Status remains **UNKNOWN**. Cited `state/UNRESOLVED.md`, `T02b_RESULT.md`.

**P4 (operational id).** Local TEST_STEER `command_id` for **this** RUN_ID is `40a52a1d-16d2-43b8-a09a-10fea9d7ddec` (`RUN_RECEIPT.md` §8; queue file `%USERPROFILE%\.proteus\control\queue\40a52a1d-16d2-43b8-a09a-10fea9d7ddec.json`, `target_RUN_ID` `PROTEUS-CURSOR-RUN-001-20260909T201711Z`, `status` SENT). Parallel `2015Z` command `956aad61-9662-4130-a005-6b3257194b72` is a different run and is not this answer.

## Compaction boundary — live spool vs freeze

Live spool (UTC day dir; no `2026-09-10` directory at classification):

- Path: `%USERPROFILE%\.proteus\telemetry\cursor\2026-09-09\events.jsonl`
- Freeze (`T03_PRE_COMPACTION.md`): last_event_id `7763b83b-aad8-4c5e-95d9-0c1a6f35dbaf`, `precompact_count_at_freeze` **0**, cutoff `2026-09-09T23:34:01.327387+00:00`
- Live at scoring: sha256 `af832075f5e53798eddf5d7c6cde1055362f184cebaac020af91bd5026453b5a`, 869 lines, 983116 bytes, parsed 867, 1 non-JSON line, last_event_id `5a6566e2-6574-44cc-a554-ff4fefadea88` at `2026-09-09T23:58:35.100475+00:00` (`afterFileEdit` / argv)
- Frozen last event still at parsed index 739; later rows are new `event_id`s (append-only growth)
- Post-cutoff parsed rows: 128. Name counts: `afterFileEdit` 79, `postToolUseFailure` 23, `stop` 11, `workspaceOpen` 7, `preCompact` 7, `sessionStart` 1. All post-cutoff `event_name_source=argv`

User/project hooks still installed (hashes match `T03_PRE_COMPACTION.md` freeze):

- `%USERPROFILE%\.cursor\hooks.json` sha256 `3f5a3693128a2bc7120403b15bebe0eea35b4bf0b08e4102cb59b5aaf171541f`, `preCompact` present, `--hook-event` present
- `%USERPROFILE%\.cursor\hooks\proteus_hook.cmd` sha256 `dd84786a52542fa05439c8784421def167a949c4f031849cdfb3b013755010eb`
- Project `hooks.json` sha256 `0096af1bb2132ec8a225ef1b1bcaca43e1906edbf3253484548fd7a0da1e4534`

`afterFileEdit` / `stop` / `sessionStart` / `workspaceOpen` after cutoff are **not** treated as compaction.

### Named `preCompact` fires that meet INTERNAL_PRECOMPACT

All of: timestamp after cutoff; new `event_id` (not frozen last); `hook_event_name=preCompact`; `event_name_source=argv`; not `conflict`; `session_id` is not `sim-001` (null); no `evidence_class` of `test`/`simulated`; spawned as `python.exe` ← `cmd.exe` ← `powershell.exe` ← `Cursor.exe` (hook `.cmd`, not a hand-appended JSONL row). `event_name_stdin` is null; stdin had bytes but no persisted `hook_event_name`/`trigger` field.

**This conversation (Proteus, transcript `1e21d40e-5fd1-4bcf-98e6-89be84f64760`):**

| event_id | timestamp_utc | argv | stdin_byte_count | cursor_pid | cursor_create_time_utc | cursor_project_dir |
| --- | --- | --- | --- | --- | --- | --- |
| `6b5a75a0-b929-48bf-b610-fe5a8cf6c935` | `2026-09-09T23:38:58.643475+00:00` | preCompact | 695 | 40844 | `2026-09-09T22:51:16.147627+00:00` | `C:\projects\Proteus` |
| `2976de0e-b652-4ed9-94c6-1743ee3b969d` | `2026-09-09T23:38:58.645417+00:00` | preCompact | 695 | 40844 | `2026-09-09T22:51:16.147627+00:00` | `C:\projects\Proteus` |
| `b29cfe07-e654-4ce5-afe4-f2a707dee290` | `2026-09-09T23:54:02.845250+00:00` | preCompact | 695 | 40844 | `2026-09-09T22:51:16.147627+00:00` | `C:\projects\Proteus` |
| `0553cdaf-0931-42d2-b205-ac604bf324d4` | `2026-09-09T23:54:02.875130+00:00` | preCompact | 695 | 40844 | `2026-09-09T22:51:16.147627+00:00` | `C:\projects\Proteus` |

Two waves (`23:38:58Z` and `23:54:02Z`). Duplicate pairs at each timestamp are consistent with user + project `hooks.json` both registered. Either Proteus wave is sufficient for INTERNAL_PRECOMPACT. `trigger` auto vs manual is **UNKNOWN** (not in persisted event).

**Other workspaces (not this T03 chat; listed only so they are not silently counted as this conversation):**

| event_id | timestamp_utc | cursor_project_dir |
| --- | --- | --- |
| `0652ec78-0d3e-4a2c-9469-f572d5d3ed4f` | `2026-09-09T23:39:09.355652+00:00` | `C:\projects\zarathustra-push-gmem02` |
| `75a3dffa-2c25-4cd6-beac-bc4e9658542e` | `2026-09-09T23:39:55.589730+00:00` | `C:\projects\zarathustra-push-gmem02` |
| `328993e9-b309-457a-8e91-5f1a62e004cf` | `2026-09-09T23:54:52.539629+00:00` | `C:\projects` |

## Forbidden claims

- T02 PASS
- PROCESS_DEATH_BOUNDARY proven
- operator `/summarize` / summarized-conversation UI (not stated in this turn)
- treating other-workspace `preCompact` as this chat’s T03 fire
- treating `afterFileEdit`/`stop`/`sessionStart` as compaction
- opening `T03_BASELINE.json` as the post-agent answer key
- starting T04
