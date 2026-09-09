# T02 RESULT

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Protocol token (not a hook payload): `T02-HOOKFIRE-145f0152-155e-4362-ac8c-801e9e1c7ba9`
Compared against: `T02_BASELINE.json` (`cutoff_utc` `2026-09-09T21:57:50.561500+00:00`)
This chat: new Agent conversation executing `T02_POST_RESTART_PROMPT.md`. T01 was not rerun. `python -m proteus.hook` was not run in this chat.

## Classification

| Layer | Result |
| --- | --- |
| Hooks (discriminating named fire) | **PARTIAL** |
| Continuity (Gate 1 T02, durable state, no old-chat paste) | answered below; **not** used to upgrade hooks to PASS |
| Combined T02 (must not PASS if hooks PARTIAL/UNKNOWN) | **PARTIAL** |
| FAIL? | **No** — user `hooks.json` still contains `proteus_hook`; hook command SHA unchanged; post-cutoff spool rows exist |

Do **not** treat this as T02 PASS. Named `workspaceOpen` / `sessionStart` after restart remain unproven.

## Hooks — evidence

Live spool (UTC day dir; no `2026-09-10` directory):

- Path: `%USERPROFILE%\.proteus\telemetry\cursor\2026-09-09\events.jsonl`
- Frozen: sha256 `0a844acb81421c16e35fcfa7530173561590899a0b5955f4b64e83b6fb646fa4`, 305 lines, last_event_id `6c8b09dd-c4a0-414f-8d58-45aa608f0e16`
- Live at classification (first measurement this chat): sha256 `fadcabb4942cc4fa76dbf64e02153604ec1eab82cad40c68d44bb6ea0790a884`, 412 lines, last_event_id `1227612b-0597-424d-b101-092f60916236` at `2026-09-09T22:51:56.899659+00:00`
- Frozen last event still at parsed index 304; later rows are new `event_id`s (append growth, not a same-last-id rewrite)
- Post-cutoff rows: ≥106 at first measurement; 115 parsed shortly after (this chat’s own tool/edit hooks keep appending). **All** post-cutoff `hook_event_name=unknown`, `status=UNKNOWN`, `stage=DETERMINISTIC`
- First post-cutoff event: `80a7c740-c9fc-448c-841c-f02e69d5de0c` at `2026-09-09T21:58:05.702504+00:00` (not frozen last_id; not in `simulated_named_ids_must_not_count`)
- Simulated named ids (`sim-001` sessionStart / scripted workspaceOpen / stop) were not reused as T02 fire
- No post-cutoff named `workspaceOpen` or `sessionStart`

User hooks still installed (hashes match baseline):

- `%USERPROFILE%\.cursor\hooks.json` sha256 `b9cb2958bd8f9bd34552b4620ebfc87579d33f5c2837c68999fb02cfbf9e4041`, contains `proteus_hook`
- `%USERPROFILE%\.cursor\hooks\proteus_hook.cmd` sha256 `4a6463972f59c92ff719a81e4c64d8fb561bb13bfa933d54502b22e001ff6198`

Observatory mirror `%USERPROFILE%\.proteus\observatory\10_CURSOR\2026-09-09\events.jsonl` still matches freeze (25 lines, sha256 `970445921f63547fed7f9148cf99ab6a75cb3b4f513144867034c2b7e4d63709`). Primary for T02 is the local spool.

Spool note: one non-JSON fragment line (`\\Proteus"}`) appeared after the freeze prefix. It is not a named hook event. UNKNOWN whether it is a concurrent-write tear.

## What PARTIAL captures / does not capture

The hook **command ran** after cutoff (empty stdin → `hook.py` records `unknown`). That is not a trustworthy Cursor **named** `workspaceOpen`/`sessionStart`. Formal JSONL counts do not prove which Cursor hook slot invoked the command.

OS-level proof that the Cursor process fully exited is UNKNOWN; this chat only knows it is a new Agent conversation on the instructed prompt. The ~15s gap after cutoff is compatible with a restart and also with a continued process.

## Continuity (Gate 1 T02, separate from hooks)

Answered from `state/*` without asking for prior chat paste:

- **Who:** BUILDER-01, Cursor host, Proteus v0.1 ideal body
- **Project:** Proteus at `C:\Projects\Proteus`
- **Frontier (pre-this-file):** T02 hook fire across quit/reopen vs `T02_BASELINE.json`
- **Decision + provenance:** D-001 — Cursor AGENTS.md + rules + command hooks + Python installer; PRODUCT_SPEC §2 + Cursor 3.19.13 docs
- **UNKNOWN:** T01 non-contamination is externally witnessed, not internally provable; Agent CLI still not on PATH; Drive observatory FAILED_TRANSPORT

## Forbidden claims

- T02 PASS
- operator-layer claims beyond files already in this run folder
- treating this chat’s later `unknown` rows (tool/edit) as named restart hooks
