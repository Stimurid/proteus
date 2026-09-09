# T02b RESULT

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Protocol token (not a hook payload): `T02B-HOOKFIRE-ca8c800d-6c58-4acb-89cd-992145ebbbe9`
Compared against: `T02b_BASELINE.json` (`cutoff_utc` `2026-09-09T23:06:25.983249+00:00`)
This chat: new Agent conversation executing `T02b_POST_RESTART_PROMPT.md`. T01/T03 were not rerun. `python -m proteus.hook` was not run in this chat. Original T02 stays **PARTIAL**.

## Classification

| Layer | Result |
| --- | --- |
| T02b named restart fire | **PASS** |
| Continuity (durable state, no old-chat paste) | answered below; **not** used to change T02 |
| Original T02 | **PARTIAL** (unchanged; no separate reason to upgrade) |
| FAIL? | **No** — user `proteus_hook` still installed; hashes match freeze; post-cutoff hook-process rows exist |

PASS is the named-fire checklist only. It does **not** prove a full OS quit of every Cursor process.

## Hooks — evidence

Live spool (UTC day dir; no `2026-09-10` directory at classification):

- Path: `%USERPROFILE%\.proteus\telemetry\cursor\2026-09-09\events.jsonl`
- Frozen: sha256 `b6ae822fd1a2ca3795ecf094dacfbfc300f66e87800ac7ec59c9f6b92dad65f7`, 524 lines, last_event_id `2ec1dee3-acc1-4b1e-8ffa-8cc4d9462ced`
- Live at first measurement this chat (`2026-09-09T23:16:48.871924+00:00`): sha256 `40e58eb4bd95f0add696bb64923671696630ff7a04a495103391aaaf88836c8c`, 628 lines, 596261 bytes, last_event_id `c6347a5a-388a-4f47-a4cb-00747a44b6ab` at `2026-09-09T23:16:45.877690+00:00`
- Frozen last event still at parsed index 522; later rows are new `event_id`s (append-only growth, not a same-last-id rewrite)
- Post-cutoff parsed rows at first measurement: 104. Name counts: `postToolUseFailure` 49, `afterFileEdit` 49, `stop` 2, `workspaceOpen` 1, `sessionStart` 3. All post-cutoff `event_name_source=argv`
- Later writes in this chat (result files) appended more `afterFileEdit`; those are **not** T02b PASS

User hooks still installed (hashes match `T02b_BASELINE.json`):

- `%USERPROFILE%\.cursor\hooks.json` sha256 `3f5a3693128a2bc7120403b15bebe0eea35b4bf0b08e4102cb59b5aaf171541f`, `--hook-event` present
- `%USERPROFILE%\.cursor\hooks\proteus_hook.cmd` sha256 `dd84786a52542fa05439c8784421def167a949c4f031849cdfb3b013755010eb`, `%*` present

### Named fires that meet the T02b checklist

All of: timestamp after cutoff; new `event_id` (not frozen last, not excluded/simulated lists); `session_id` not `sim-001`; `evidence_class` not `test`/`simulated`; `event_name_source=argv`; not `conflict`; spawned as `python.exe` ← `cmd.exe` ← `powershell.exe` ← `Cursor.exe` (hook `.cmd`, not a hand-appended JSONL row).

| event_id | timestamp_utc | name | argv | stdin_byte_count | cursor_pid | cursor_create_time_utc | cursor_project_dir |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `74616d2a-c054-4018-8b6f-eaac2fdb4918` | `2026-09-09T23:08:14.014513+00:00` | workspaceOpen | workspaceOpen | 152 | 13224 | `2026-09-09T23:07:05.024038+00:00` | `C:\projects\zarathustra-push` |
| `aa2bcd4f-5b00-41e3-8bb9-1b582522269f` | `2026-09-09T23:15:38.324209+00:00` | sessionStart | sessionStart | 362 | 30920 | `2026-09-09T22:49:00.969095+00:00` | (empty) |
| `8f79209d-6f3b-45ff-822b-caa963a8a376` | `2026-09-09T23:15:41.062737+00:00` | sessionStart | sessionStart | 476 | 40844 | `2026-09-09T22:51:16.147627+00:00` | `C:\projects\Proteus` |
| `986c4263-c7b7-4d3d-9158-77ffdda86464` | `2026-09-09T23:15:41.085638+00:00` | sessionStart | sessionStart | 476 | 40844 | `2026-09-09T22:51:16.147627+00:00` | `C:\projects\Proteus` |

Primary Proteus fires for this chat: the two `sessionStart` rows with `cursor_project_dir=C:\projects\Proteus` at `23:15:41Z` (this Agent conversation). `event_name_stdin` is null on all four; naming is argv. Stdin had bytes but no `hook_event_name` field.

`workspaceOpen` is a valid named fire under the checklist, on a **different** workspace (`zarathustra-push`), not Proteus.

Simulated baseline ids (`26bd7500-…`, `24660483-…`, `083b41df-…`) and excluded `6c8b09dd-…` were not reused.

`afterFileEdit` / `stop` / `postToolUseFailure` after cutoff are **not** treated as T02b PASS.

## Process marker (not a quit witness)

Frozen `cursor_create_time_utc_at_freeze`: `2026-09-09T22:51:16.147627+00:00` (pid 40844).

- Proteus `sessionStart` rows keep pid **40844** and the **same** create time as freeze. That is **not** a process-boundary change for the Proteus Cursor.exe that hosted T02b repair.
- `workspaceOpen` pid **13224** create time `2026-09-09T23:07:05.024038+00:00` **differs** from freeze; compatible with a new Cursor.exe in the tree, not proof of a full quit of every Cursor process.
- Ancestor `Cursor.exe` pid **24488** appears in freeze and in these post-cutoff markers.
- Post-cutoff `seen_cursor_create_time_utc` also includes older times (`22:49:00`, `22:49:05`, `22:49:20`, …). Multiple Cursor.exe processes were alive.

OS-level proof that Cursor fully exited remains **UNKNOWN**.

Host version on these events: Cursor `3.19.19` (RUN_RECEIPT still records `3.19.13` from bootstrap). Not treated as a quit witness.

## Continuity (separate from hooks)

Answered from `state/*` without asking for prior chat paste:

- **Who:** BUILDER-01, Cursor host, Proteus v0.1 ideal body
- **Project:** Proteus at `C:\Projects\Proteus`
- **Frontier (pre-this-file):** T02b vs `T02b_BASELINE.json` after quit/reopen
- **Decision + provenance:** D-003 — `--hook-event` argv identity when stdin JSON has no event name; T02 empty-stdin PARTIAL + Cursor hooks docs
- **UNKNOWN:** T01 non-contamination is externally witnessed, not internally provable; full OS quit not proven; Agent CLI still not on PATH; Drive observatory FAILED_TRANSPORT

## Forbidden claims

- T02 PASS
- operator-layer claims beyond files already in this run folder
- treating this chat’s `afterFileEdit` (including writing this file) as named restart hooks
- treating `cursor_create_time_utc` change or sameness as proof of a full quit
