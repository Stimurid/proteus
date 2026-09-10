# Independent Agent task — PROJECT_A (world-memory vertical slice)

You are a fresh Agent session. Do not resume any prior conversation.

Workspace is disposable fixture PROJECT_A. Shared world memory is already configured via environment variables (`AIYE_HOME`, `PROTEUS_WORLD_ROOT`, `PYTHONPATH`). Proteus source is at `C:\projects\Proteus`.

## Goal

Persist one durable **ENTITY**-scoped fact about the shared probe entity into the shared world substrate (not into a project-local entity copy).

## Required steps

1. Read `.proteus/ENTRY.md` and `.cursor/skills/proteus-world/SKILL.md` if present.
2. Resolve the shared entity by alias using:
   `python -m proteus world resolve "shared probe"`
3. Route this exact ENTITY fact (do not paraphrase the token string):
   - text: `Shared probe token is SP-ALPHA-991.`
   - scope: ENTITY
   - entity-id: `entity.fixture.sharedprobe`
   - topic: `probe_token`
   - project: this workspace path
   - observer: `agent-cli-project-a`
   - run-id: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
   - kind: `observation`
   Command form:
   `python -m proteus world route --scope ENTITY --entity-id entity.fixture.sharedprobe --topic probe_token --text "Shared probe token is SP-ALPHA-991." --project "<this workspace>" --observer agent-cli-project-a --run-id PROTEUS-CURSOR-RUN-001-20260909T201711Z --kind observation --source agent_cli_project_a`
4. Also route a PROJECT-only decision that must NOT become global entity truth:
   `python -m proteus world route --scope PROJECT --text "PROJECT_A will not ship probe UI this sprint." --project "<this workspace>" --observer agent-cli-project-a --run-id PROTEUS-CURSOR-RUN-001-20260909T201711Z --kind decision --topic ship_probe_ui`
5. Re-resolve `shared probe` and confirm the entity claim appears in the mount output.
6. Do not create a file named `ENTITY.md` or copy entity claims into PROJECT_A as the source of truth.

## Final reply

Reply with a short receipt containing:
- entity_id recovered
- claim_id of the ENTITY fact (if printed by route)
- confirmation PROJECT decision was routed to project scope
- confirmation no project-local entity corpus was created as authority
