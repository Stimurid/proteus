# FRESH_WORKSPACE_PREP

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: first real fresh Cursor incarnation *workspace preparation*
When: 2026-09-10
Status of future Agent execution: **PREPARED / NOT_RUN**

This episode is not a PASS on the future incarnation. Files were reconstructed; an independent Agent has not executed `FRESH_AGENT_TASK.md`.

## Distinctions (do not collapse)

| Object | Status |
| --- | --- |
| Portable-package clean-room (`python -m proteus.handoff cleanroom`) | PASS (prior episode `PORTABLE_HANDOFF.md`; reconfirmed PASS after path-boundary matcher repair) |
| Real fresh workspace preparation from the distribution ZIP | PASS (this episode) |
| Future fresh-Agent execution of `FRESH_AGENT_TASK.md` | **NOT_RUN** |
| T02 / T02b / T03 / PROCESS_DEATH_BOUNDARY / Gate 1 | unchanged |

## Artifact used (not a repo copy)

- Origin zip: `C:\projects\Proteus\distribution\proteus-portable-handoff.zip`
- SHA256: `42ED4BE19B73883BBB2085CCE35FEEAED0F87DD1265D1429FF3EA7DED3FF00DA`
- Manifest `source_revision`: `bb43659588a3f3a6928e8ec27bd41f52a4634443`
- Parent `C:\Projects\Proteus-FRESH-001` did not exist before this episode.
- Seed after copy, before extract: only `proteus-portable-handoff.zip` plus this episode's `_PREP_PROOF` notes (not origin source/state/`.cursor`/`.git`).
- Reconstruct path: `tar -xf` → `proteus-handoff\bootstrap.cmd` (default isolated; no `--machine-host`).
- Destination: `C:\Projects\Proteus-FRESH-001\Proteus`
- Destination `.git`: **absent** (payload excludes git history; not a clone of `C:\Projects\Proteus`).

## Reconstruction / verification

- Isolated install: `PROTEUS_HOME` = dest `.proteus-runtime`; `PROTEUS_CURSOR_USER_DIR` = dest `.cursor-user-isolated`.
- Live `%USERPROFILE%\.cursor\hooks.json` SHA256 unchanged: `3F5A3693128A2BC7120403B15BEBE0EEA35B4BF0B08E4102CB59B5AAF171541F`.
- Bootstrap-run tests: `tests/test_smoke.py` PASS; `tests/test_hook_event_identity.py` PASS.
- Re-run from dest tree: same two tests PASS.
- `verify_reconstructed` with path-boundary matcher: PASS (`failed: []`).
- Generated `AGENTS.md` Source root: `C:\projects\Proteus-FRESH-001\Proteus`.
- Project hook PYTHONPATH: dest `.proteus-runtime\host\cursor\src` (destination Python interpreter is a host requirement).
- `state/RECONSTRUCTION.md`: `process_death_continuity: NOT_CLAIMED`; Gate 1 not upgraded.
- `state/CURRENT.md` still names `C:\Projects\Proteus` as first-incarnation provenance.

## Origin-coupling

- No operational dependency on `C:\Projects\Proteus` in dest `src/` or `hosts/` (path-boundary match).
- Naive substring match falsely flagged `C:\projects\Proteus-FRESH-001\...` as the origin path. That is a checker defect, not a reconstruct defect. Origin repair: `mentions_origin_workspace` in `src/proteus/handoff.py` (does not change the already-transferred ZIP).
- Historical/provenance mentions of the origin path in dest `state/CURRENT.md` and `evidence/` remain residue.

## Fresh-agent task file

- Path: `C:\Projects\Proteus-FRESH-001\Proteus\FRESH_AGENT_TASK.md`
- Written by this origin episode. Not executed here.
- Independent Agent conversation: **not opened**. `move_agent_to_root` would keep this chat's context. Agent CLI remains unproved. `open_resource` cannot open a folder outside this workspace as a new Cursor window.

## Not claimed

- PROCESS_DEATH continuity
- Gate 1
- That reconstruction equals a live independent Agent session
- PASS on the future incarnation's work
