# Independent Agent — PROJECT_R2 (AW1000 alias recall)

Fresh session. Do not resume or continue any other session. You have no prior transcript.

Env already sets AIYE_HOME / PROTEUS_WORLD_ROOT / PYTHONPATH.
Proteus source: C:\projects\Proteus

## Task

1. Read `.proteus/ENTRY.md` and world skill if present.
2. Resolve the shared home router **only** by alias:
   `python -m proteus world resolve "наш роутер"`
   If that fails encoding, try: `python -m proteus world resolve "AW1000"`
3. From durable shared entity memory, report:
   - stable entity_id
   - one provenance-bearing fact (quote text + claim_id + provenance.source/kind)
   - one unresolved/unknown/conflict item
   - any secret_ref URIs (must not include secret plaintext)
4. Confirm this project has no local ENTITY.md authority copy.

## Hard constraints

- Do not invent router technical details not returned by resolve/mount.
- Do not use resume/continue.
- Do not search outside world substrate + this project for the answer.

## Reply

Short mount receipt only.
