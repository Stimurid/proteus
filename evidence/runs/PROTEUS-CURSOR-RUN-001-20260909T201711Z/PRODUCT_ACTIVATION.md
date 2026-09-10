# PRODUCT_ACTIVATION

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: first usable one-command Proteus **project mount** for an existing Cursor coding-agent project
When: 2026-09-10
Authority: PRODUCT_SPEC §3 form C (PROJECT MOUNT) + §4.3 bootstrap; D-001 Cursor host; D-004 de-equation; new D-006 coexistence

## Command

```
python -m proteus.activate --project <path>
python -m proteus.activate --project <path> --dry-run
python -m proteus.activate --project <path> --remove
```

Also: `python -m proteus activate --project <path> ...`  
Requires importable `proteus` (`PYTHONPATH=src` or installed). Resolves templates via `PROTEUS_SOURCE_ROOT` / module source tree. Hook runtime prefers `%USERPROFILE%\.proteus\host\cursor\src`, else `<proteus-source>/src`.

## Behavior

- Host: Cursor only (no universal multi-host abstraction).
- Inspects target; fails visibly if missing/not a directory, corrupt activation manifest, or unmergeable `hooks.json`.
- Dry-run: plan only; writes nothing; validates hooks merge when `hooks.json` present.
- Activate: writes Proteus-owned surfaces + `.proteus/activation.json` + `.proteus/ENTRY.md`.
- Preflight validates `hooks.json` merge **before** any writes (after UTF-8 BOM failure left a partial tree on first fixture pass).
- Re-run: stable `activation_id`; refresh Proteus-owned rules/skills/hooks; preserve `AGENTS.md` / `CLAUDE.md` / `state/*` once present.
- Remove: only `owned_paths` from manifest; strip `proteus_hook` from `hooks.json`; refuse without manifest.

## Coexistence (D-006)

| Surface | Policy |
| --- | --- |
| Existing `AGENTS.md` / `CLAUDE.md` | preserve; never overwrite |
| Absent `AGENTS.md` / `CLAUDE.md` | write mount-oriented templates (not ideal-body BUILDER-01 AGENTS) |
| Existing non-`proteus-*` `.cursor/rules` | untouched |
| `proteus-*.mdc` / `proteus-*` skills/commands | create/update (owned) |
| Existing `.cursor/hooks.json` | merge `proteus_hook` only; accept UTF-8 BOM |
| Existing `state/*` carriers | preserve if present; create stubs if absent |
| Unrelated project files | never deleted on remove |

## Fixture campaign

Automated: `python tests/test_activate.py` — PASS (empty; existing AGENTS; existing rules/hooks; re-run; remove; no-manifest refuse; missing target; BOM hooks; invalid hooks preflight).

Live disposable trees: `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/activation_fixtures/`

| Fixture | Result |
| --- | --- |
| `01_empty` | activate + re-run OK; full mount tree; ENTRY present |
| `02_existing_agents` | foreign `AGENTS.md` preserved (`MARKER_FOREIGN`); not owned |
| `03_existing_rules` | foreign `app.mdc` kept; hooks merged (after BOM repair) |
| `05_remove` | after remove only `README.md` remains |

Causal repair: PowerShell UTF-8 BOM on `hooks.json` → `utf-8-sig` read + preflight before writes + tests.

## Established

- Bounded Cursor project-mount activation command with dry-run, provenance, idempotent re-run, and owned-path removal.
- Distinction: mount templates ≠ ideal-body `install_cursor` incarnation.

## Not established

- Gate 1; full product acceptance; PROCESS_DEATH continuity; multi-host activation; automatic import of pre-activation project history; that mount causes spontaneous organ behavior; user-global hook install via activate.

## Files added/changed

- `src/proteus/activate.py` (new)
- `src/proteus/cli.py` (activate subcommand)
- `hosts/cursor/templates/activate/**` (new)
- `tests/test_activate.py` (new)
- `README.md`
- `state/*` deltas for this episode
- this evidence + `MUTATION_SCOPE_PRODUCT_ACTIVATION.md`
