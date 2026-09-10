# CHECKPOINT

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
When: portable handoff artifact + clean-room reconstruct (new episode; same jurisdiction)

## Done

- Recovered durable state from repository files; did not use prior chat as authority.
- Determined portable boundary by inspection: classified payload + bootstrap, not a whole-tree zip of generated host files.
- Implemented `python -m proteus.handoff pack|reconstruct|cleanroom`. Isolated host dirs via `PROTEUS_CURSOR_USER_DIR`. Installer binds templates/`{{SOURCE_ROOT}}` to `--project`.
- Stamped root `CURRENT.md` / `FRONTIER.md` SUPERSEDED. D-005 accepted.
- Clean-room: zip-only copy into a temp directory outside the working tree; reconstruct; tests PASS; live user hooks unchanged.
- Did not start T04/T05/T02c. Did not upgrade Gate 1, T02, or PROCESS_DEATH.

## Changed

`src/proteus/handoff.py`, `paths.py`, `install_cursor.py`, `checkpoint.py`; templates (AGENTS reentry step 6, commands); `tests/test_portable_handoff.py`; `distribution/README.md`; `README.md`; `.gitignore`; `state/*`; root CURRENT/FRONTIER banners; this evidence; installer cycle `host-backups-portable-handoff`.

## Decisions

D-005 — classified zip + reconstruct; generated host files recreated; isolated default; Drive/CLI non-portable.

## Unresolved

Prior UNKNOWNs preserved. New: destination Python required; machine_id/spool/PID not transferred; reconstruction ≠ PROCESS_DEATH.

## Next frontier

Handoff object closed. Carry the zip to a fresh workspace if a new machine is needed. Organ next remains ordinary-work loss-naming or a human-chosen foreign-body mount.

## Git / tests

`python tests\test_smoke.py` PASS; `python tests\test_hook_event_identity.py` PASS; `python tests\test_portable_handoff.py` PASS; `python -m proteus.handoff cleanroom` PASS. Installer cycle `host-backups-portable-handoff` at `2026-09-10T11:34:33Z`.
