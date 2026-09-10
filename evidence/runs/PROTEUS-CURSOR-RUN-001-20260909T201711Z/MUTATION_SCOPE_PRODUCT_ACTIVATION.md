# MUTATION_SCOPE — product activation (project mount)

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: one-command Proteus activation path for an existing Cursor coding-agent project

## In scope

- `src/proteus/activate.py` — activate / dry-run / remove for Cursor project mount
- `src/proteus/cli.py` — `activate` subcommand
- `hosts/cursor/templates/activate/**` — mount-oriented templates (not ideal-body AGENTS)
- `tests/test_activate.py` — disposable fixture campaign
- `README.md` — user-facing activate command
- Durable state / decisions / frontier / evidence for this episode only
- Disposable trees under `evidence/runs/.../activation_fixtures/`

## Out of scope

- Gate 1 claims; organ-behavior tests; T04/T05/T02c
- Multi-host adapters (Claude Code, Codex, …)
- Rewriting constitutional / `_BOOTSTRAP` materials
- Changing `install_cursor` ideal-body incarnation semantics
- Silent overwrite of foreign `AGENTS.md` / non-`proteus-*` rules
- User-global `~/.cursor` mutation as part of project activate (project-local mount only)
- Repacking `distribution/proteus-portable-handoff.zip` (source lands in next pack)

## Intended behavioral effect

A developer can run one command against an existing project path and obtain a usable Proteus-mounted Cursor environment with inspect/dry-run, provenance, and bounded removal — without manually copying a file collection and without destroying unrelated project material.
