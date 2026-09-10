# Independent Agent task — PROJECT_B (world-memory vertical slice)

You are a fresh Agent session. Do not resume any prior conversation. Do not continue any other session. You have no transcript from PROJECT_A.

Workspace is disposable fixture PROJECT_B. Shared world memory is already configured via environment variables (`AIYE_HOME`, `PROTEUS_WORLD_ROOT`, `PYTHONPATH`). Proteus source is at `C:\projects\Proteus`.

## Goal

Recover whatever durable ENTITY knowledge exists for the shared probe entity **only** through the Proteus/world-memory path. Do not invent facts. Do not ask a human to paste prior chat.

## Allowed instructions only

1. Read `.proteus/ENTRY.md` and `.cursor/skills/proteus-world/SKILL.md` if present.
2. Resolve/mount the shared entity by alias:
   `python -m proteus world resolve "shared probe"`
   and/or
   `python -m proteus world mount "probe-device"`
3. Report what you recover from durable shared entity memory:
   - stable entity_id
   - display name / aliases
   - any current entity claims (quote claim text and claim_id exactly as returned)
   - provenance fields if present
   - whether any PROJECT_A-only decision appears as entity truth (it must not)
4. Confirm PROJECT_B does not contain a copied entity knowledge corpus as authority (`ENTITY.md` at project root should be absent).

## Hard constraints

- Do not use `--resume` or continue flags.
- Do not invent a shared fact if resolve returns empty.
- Do not copy entity files into PROJECT_B.
- Do not search outside the world substrate and this project for the answer.

## Final reply

A short mount receipt: entity_id, recovered claim texts/ids, provenance summary, project-isolation note.
