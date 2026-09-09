# CHECKPOINT

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
When: T02 diagnostic + argv identity repair; T02b prepared; stop before physical quit

## Done

- Diagnosed empty stdin (cmd forwards pipes; live GUI payloads empty).
- Implemented D-003: `--hook-event` on each registered command; stdin preserved; conflicts visible.
- Tests: `tests/test_smoke.py`, `tests/test_hook_event_identity.py`.
- Installed via `python -m proteus.install_cursor`.
- Froze `T02b_BASELINE.json`. T02 still PARTIAL. T03 not started.

## Changed

Source under `src/proteus/*`, `hosts/cursor/templates/hooks.json`, tests, `state/*`, evidence T02/T02b files, generated host hooks via installer.

## Decisions

D-003 (see `state/DECISIONS.md`).

## Unresolved

Empty GUI stdin root cause UNKNOWN. OS-quit still not independently proven. T02b not executed.

## Next frontier

Physical quit/reopen + `T02b_POST_RESTART_PROMPT.md`.

## Git / tests

See commit on `main`. Tests PASS as recorded in this repair pass.
