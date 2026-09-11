# Proteus entry — Codex project mount

Proteus is **mounted** on this **Codex** project for shared world/entity memory. This is not a claim that this tree is the Proteus ideal body, not a Cursor BUILDER-01 incarnation, and not Gate 1 acceptance of the whole product.

## Open / continue work

1. Open this folder as the Codex working directory (`codex -C <path>` / project root).
2. Start a **new** Codex session (do not `codex resume` / `fork` an unrelated session for continuity of foreign work).
3. Read, in order when present: `state/IDENTITY.md`, `state/CURRENT.md`, `state/FRONTIER.md`, `state/DECISIONS.md`, `state/UNRESOLVED.md`.
4. Follow project `AGENTS.md` for mount orientation (Codex-native instruction surface).
5. If this project already had its own `AGENTS.md` before activation, that file was **preserved**; prefer those conventions for project-specific work. Proteus carriers still live under `.proteus/` and optional owned `AGENTS.md` only when created by activation.

## Shared world / entity memory

Environment for this mount (also written to `.proteus/world_env.cmd`):

- `AIYE_HOME={{AIYE_HOME}}`
- `PROTEUS_WORLD_ROOT={{PROTEUS_WORLD_ROOT}}`
- `PYTHONPATH={{PYTHONPATH}}`
- `PROTEUS_SOURCE_ROOT={{PROTEUS_SOURCE}}`

Load with:

```
call .proteus\world_env.cmd
```

Then:

```
python -m proteus world resolve "<entity name or alias>"
python -m proteus world mount "<entity name or alias>"
python -m proteus world route --scope ENTITY --entity "<name>" --text "..." --project .
python -m proteus world route --scope PROJECT --project . --text "<project-only>"
```

Host-neutral module: `proteus.world.api`.

Do **not** copy entity knowledge into this project as local truth. Project decisions stay in `state/` / `.proteus/project_memory.jsonl`. ENTITY facts live in the shared substrate.

Secrets: opaque `secret://` refs only. Never print plaintext secrets.

## What Proteus owns here

See `.proteus/activation.json` (`owned_paths`). Reverse with:

```
python -m proteus.activate_codex --project . --remove
```

(from a machine where the `proteus` package is importable; typically `PYTHONPATH=<proteus-src>`).

## Activation provenance

- activation_id: `{{ACTIVATION_ID}}`
- activated_at: `{{ACTIVATED_AT}}`
- proteus_source: `{{PROTEUS_SOURCE}}`
- target: `{{TARGET_ROOT}}`
- host: Codex
- aiye_home: `{{AIYE_HOME}}`
