# T02b PRE-RESTART

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Token: `T02B-HOOKFIRE-ca8c800d-6c58-4acb-89cd-992145ebbbe9`
Original T02: **PARTIAL** (do not upgrade).
T02b status: **NOT_RUN** — do not claim PASS until after a real Cursor quit/reopen compared to `T02b_BASELINE.json`.

If this markdown and `T02b_BASELINE.json` disagree, **JSON wins**.

## What T02b must prove

User-level hooks still run after a full Cursor process restart **and** a post-cutoff spool row is a trustworthy named `sessionStart` or `workspaceOpen` with `event_name_source` in `{argv, stdin, stdin+argv}`, not `sim-001`, not test/simulated.

In-session `afterFileEdit` named via argv (already observed while writing this repair) is **not** T02b PASS.

## Frozen snapshot (see JSON)

- cutoff / frozen_at: `2026-09-09T23:06:25.983249+00:00`
- spool `2026-09-09` sha256 `b6ae822fd1a2ca3795ecf094dacfbfc300f66e87800ac7ec59c9f6b92dad65f7`, 524 lines, 432541 bytes, last_event_id `2ec1dee3-acc1-4b1e-8ffa-8cc4d9462ced`, last name `afterFileEdit` / source `argv`
- user `hooks.json` sha256 `3f5a3693128a2bc7120403b15bebe0eea35b4bf0b08e4102cb59b5aaf171541f` (`--hook-event` present)
- `proteus_hook.cmd` sha256 `dd84786a52542fa05439c8784421def167a949c4f031849cdfb3b013755010eb` (`%*` present)
- `cursor_create_time_utc_at_freeze`: `2026-09-09T22:51:16.147627+00:00` (best-effort; not a quit witness)
- expected named events: `sessionStart`, `workspaceOpen`

## Human action (exactly one)

Fully **quit Cursor** (exit the process). Reopen workspace `C:\Projects\Proteus`. Start a **new** Agent chat using only `T02b_POST_RESTART_PROMPT.md`.

Stop before that quit. Do not start T03.
