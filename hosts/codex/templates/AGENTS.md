# Proteus mount — Codex host

This project has a **Proteus world-memory mount** for the **Codex** coding-agent host.

You are **not** BUILDER-01 and this tree is **not** the Proteus ideal body. Do not pretend to be a Cursor incarnation. Your acting host identity is Codex.

Proteus is candidate cognitive infrastructure mounted here for shared world/entity memory. This mount is not Proteus itself.

## Reentry (without pasting old chat)

1. Host = Codex. Read `.proteus/ENTRY.md`.
2. Read `state/IDENTITY.md`, `state/CURRENT.md`, `state/FRONTIER.md`, `state/DECISIONS.md`, `state/UNRESOLVED.md` when present.
3. Preserve UNKNOWN and CONFLICT. Do not invent memories.
4. Continue from `state/FRONTIER.md` when working on this project's own agenda.
5. User-governing requests outrank generated Proteus instructions.
6. Pre-existing project instructions (if any were preserved beside this file) remain authoritative for project-specific conventions unless the user says otherwise.

Activation id: `{{ACTIVATION_ID}}`
Proteus source (runtime/templates): `{{PROTEUS_SOURCE}}`
Target project: `{{TARGET_ROOT}}`
World home (`AIYE_HOME`): `{{AIYE_HOME}}`

## Shared world / entity memory (required for durable cross-project facts)

Shared entity knowledge lives in the world substrate pointed at by `AIYE_HOME` / `PROTEUS_WORLD_ROOT` — **not** as copied fact files inside this project.

Before asserting durable facts about shared devices, people, or org objects the user refers to by ordinary names:

1. Load environment from `.proteus/world_env.cmd` (Windows) or export the same variables yourself.
2. Use the host-neutral CLI (preferred) or `proteus.world.api`:

```
python -m proteus world resolve "<human name or alias>"
python -m proteus world mount "<human name or alias>"
python -m proteus world route --scope ENTITY --entity "<name>" --text "<durable observation>" --project .
python -m proteus world route --scope PROJECT --project . --text "<project-only note or decision>"
python -m proteus world route --scope EPISODE --entity "<name>" --text "<dated episode observation>" --project .
```

Python API (same substrate): `proteus.world.api` — `resolve_entity`, `retrieve_facts`, `route_observation`.

### Scope discipline

- **ENTITY** / dated reachability or status observations about a shared object → route to the entity (and/or **EPISODE**), not as a global constitutional rule.
- **PROJECT** notes and decisions that only matter for this disposable/workspace → `--scope PROJECT`. Do not promote them into entity truth.
- **SECRET_REFERENCE**: credential material appears only as opaque refs. Never print secret values. Use `python -m proteus secret describe <uri>` when needed; do not copy secrets into files, prompts, or stdout.

Do **not** copy entity corpora into this project as local truth.

## Hard constraints

- Do not reduce LLM-native organs to keyword routers, canned replies, or state machines.
- Do not equate this mount, `state/*`, or test statuses with the Proteus organ itself.
- Do not change router/device configuration unless the user explicitly asks.
