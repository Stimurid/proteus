# PORTABLE_HANDOFF

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: portable bootstrap / handoff artifact
When: 2026-09-10

## Object

A single user-carried zip that reconstructs the currently useful Proteus development environment in a fresh directory without the origin chat, Google Drive, or Agent CLI.

## Form chosen (from inspection)

Zip + bootstrap, not a raw dump of the whole working tree:

- Payload = classified portable set (source, templates, `state/*` except generated `INCARNATION.md`, tests, `_BOOTSTRAP`, evidence, superseded root residue, `.cursor/commands`).
- Omitted generated host files that baked origin-machine Python / `%USERPROFILE%\.proteus` paths (`.cursor/hooks/proteus_hook.cmd`, `AGENTS.md`, `state/INCARNATION.md`).
- Bootstrap copies payload, then source → tests → `install_cursor`.
- Default reconstruct is **isolated** (`PROTEUS_HOME` + `PROTEUS_CURSOR_USER_DIR` under the destination tree). `--machine-host` is the destination installation action for live user hooks.

Zipping the entire repo including generated hooks would have shipped a hidden coupling to the origin machine. That is why the whole-repo zip is not the portable boundary.

## Artifact

- Path: `distribution/proteus-portable-handoff.zip` (gitignored build product; regenerate with `python -m proteus.handoff pack`)
- Wrapper inside zip: `proteus-handoff/READ_ME_FIRST.md`, `bootstrap.cmd`, `MANIFEST.json`, `payload/`
- SHA256 and file_count: see pack sidecar / this receipt after pack (filled below).

## Usage sequence (fresh Windows directory)

1. Copy `proteus-portable-handoff.zip` into an empty folder.
2. `tar -xf proteus-portable-handoff.zip`
3. `proteus-handoff\bootstrap.cmd` (isolated reconstruct into sibling `Proteus\`)
4. Optional live host install: `proteus-handoff\bootstrap.cmd --machine-host`
5. Open the reconstructed `Proteus` folder in Cursor. Give the agent `HANDOFF.md` or `AGENTS.md`. Do not paste the origin chat.

Python 3 on PATH is a destination host requirement.

## Clean-room test

Method: `python -m proteus.handoff cleanroom` and `python tests\test_portable_handoff.py`.

Preconditions: only the produced zip is copied into a temp directory outside this working tree. Reconstruct runs isolated so live `~/.cursor/hooks.json` must not change.

Results (this episode, before/with the source commit): see "Pack / clean-room results" below. Failures that were repaired in-tree:

- Generated `proteus_hook.cmd` on the origin tree contains origin-user Python and `%USERPROFILE%\.proteus\host\cursor\src`. Repair: omit generated hooks from payload; regenerate via installer; `cursor_user_dir()` honors `PROTEUS_CURSOR_USER_DIR`.
- Installer used `REPO_ROOT` from the *importing module* file path and baked it into `AGENTS.md`. Repair: templates and `{{SOURCE_ROOT}}` come from `--project`.
- Root `CURRENT.md` / `FRONTIER.md` looked live. Repair: SUPERSEDED banners (same residue treatment as F01 for `DECISIONS.md` / `UNKNOWN.md`).

## What reconstructs

- Ideal-body `src/proteus`, Cursor templates, tests
- Live `state/*` distinctions (including UNKNOWN / CONFLICT / T02 PARTIAL / Gate 1 NOT_YET)
- Superseded root dumps as residue
- Evidence needed for continuation and for `test_hook_event_identity.py` (T02 baseline)
- `_BOOTSTRAP/BLIND_START` provenance packet
- Generated `AGENTS.md` / `.cursor` incarnation on the destination
- Isolated `.proteus-runtime` and `.cursor-user-isolated` (created, not carried)

## What remains machine-local / non-portable

- Python 3 interpreter
- Live `~/.cursor` user hooks unless `--machine-host`
- `%USERPROFILE%\.proteus` machine_id, telemetry spool, observatory mirror
- Google Drive transport (FAILED_TRANSPORT)
- Cursor Agent CLI (unproved)
- Origin Cursor PID / process-quit witness (UNKNOWN)
- PROCESS_DEATH continuity (explicitly NOT_CLAIMED)

## Form-change (this packaging)

- Preserved: source, templates, durable state distinctions, evidence texts, test statuses.
- Transformed: location; generated incarnation (new install); installer SOURCE_ROOT binding.
- Lost: live process, origin machine_id, hook spool, any illusion that the new tree *is* the old session.
- Emerged: classified zip, isolated vs machine-host install, `HANDOFF.md` / `state/RECONSTRUCTION.md`.
- Residue: original workspace path inside `state/CURRENT.md` and historical evidence files.

## Gate / test statuses

Unchanged: T01 PASS; T02 PARTIAL; T02b PASS; T03 PASS; T11 PARTIAL; Gate 1 NOT_YET; PROCESS_DEATH UNKNOWN.
Added: portable-handoff clean-room PASS (this episode). Not a Gate 1 test.

## Pack / clean-room results

- Official pack command: `python -m proteus.handoff pack` → `distribution/proteus-portable-handoff.zip`
- Payload file_count: 126
- Inner wrapper: `proteus-handoff/READ_ME_FIRST.md`, `bootstrap.cmd`, `MANIFEST.json`, `payload/`
- Zip SHA256 is **not** stored in this packed evidence file (self-digest loop). After pack, read `distribution/proteus-portable-handoff.manifest.json` (gitignored sidecar) or recompute `Get-FileHash`.
- `python tests\test_smoke.py` PASS
- `python tests\test_hook_event_identity.py` PASS
- `python tests\test_portable_handoff.py` PASS (includes clean-room: zip-only copy into `%TEMP%\proteus-cleanroom-*`, isolated reconstruct, live `~/.cursor/hooks.json` unchanged)
- `python -m proteus.handoff cleanroom` PASS (`verify.pass: true`, `failed: []`, `live_user_hooks_unchanged: true`)
- Origin-machine hook cmd is not in the payload; reconstructed `AGENTS.md` Source root is the destination path; `state/CURRENT.md` still names `C:\Projects\Proteus` as provenance
- Isolated reconstruct did not require `C:\Projects\Proteus` to exist as an operational dependency

