# Proteus entry — this project

Proteus is **mounted** on this Cursor project. This is a project mount, not a claim that this tree is the Proteus ideal body, and not Gate 1 acceptance of the whole product.

## Open / continue work

1. Open this folder as the Cursor workspace.
2. Start a new Agent chat (do not paste an old conversation).
3. Read, in order: `state/IDENTITY.md`, `state/CURRENT.md`, `state/FRONTIER.md`, `state/DECISIONS.md`, `state/UNRESOLVED.md`.
4. Follow `.cursor/rules/proteus-*.mdc` (always-apply) for mount orientation.
5. If this project already had its own `AGENTS.md` / rules before activation, those were **preserved**. Prefer project conventions there; Proteus carriers add reentry/checkpoint/anti-reduction surfaces.

## Shared world / entity memory

If the machine has a Proteus world substrate (`AIYE_HOME` / `PROTEUS_WORLD_ROOT`, default `~/.aiye/world`):

```
python -m proteus world resolve "<entity name or id>"
python -m proteus world mount "<entity name or id>"
python -m proteus world route --scope ENTITY --entity "<name>" --text "..." --project .
```

Do **not** copy entity knowledge into this project as local truth. Project decisions stay in `state/` / `.proteus/project_memory.jsonl`. ENTITY facts live in the shared substrate.

## Consequential derived representations

Read `.proteus/CONSTITUTIVE.md`. When a durable artifact will stand in for richer source in later action, keep it distinct from that source and retain reopenability. Optional: `python -m proteus derived record ...`.

## What Proteus owns here

See `.proteus/activation.json` (`owned_paths`). Only those paths are safe to reverse with:

```
python -m proteus.activate --project . --remove
```

(from a machine where the `proteus` package is importable; typically `PYTHONPATH=<proteus-src>`).

## Activation provenance

- activation_id: `PROTEUS-CURSOR-RUN-001-20260909T201711Z-ACT-20260911T194343Z`
- activated_at: `2026-09-11T19:43:43.189406+00:00`
- proteus_source: `C:\projects\Proteus`
- target: `C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\gate1_blocker_fixtures\T09_BODY_R2`
- host: Cursor
