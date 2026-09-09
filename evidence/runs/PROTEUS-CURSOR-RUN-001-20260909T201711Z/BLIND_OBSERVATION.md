# BLIND_OBSERVATION.md

RUN_ID: PROTEUS-CURSOR-RUN-001-20260909T201711Z
Written before reading `99_POST_BLIND_UNLOCK.md` operator folder.
This file must not be rewritten after operator-layer disclosure.

## Unexpected relations, coincidences, tensions

The agent spec (BUILDER-01 as a subject that survives chats) and the product spec (Proteus as installable host infrastructure) are almost the same object described twice: one as “who acts”, one as “what is installed so that actor can exist”. I noticed this while implementing, but I am not treating it as a doctrine. It may be a coincidence of this packet’s structure.

Tension: AGENT_SPEC forbids reducing living process to architecture, while FIRST_RUN_PROMPT demands files, hooks, receipts, and a source→install loop. The working compromise in this run was to put *judgment* in markdown + LLM context and *only* make deterministic the parts that are actually event plumbing (JSONL, queue claim, redaction). That may still be too much machinery; it may also be the only way a host like Cursor can be observed.

Another tension: PRODUCT_SPEC wants Drive-visible observatory “without copying chat”, but the host could download a public zip and could not write Drive. So the first global organ is local-only. Observability and steering split across an unauthorized cloud boundary.

## Product properties that began to change this run’s own work

Once `state/CURRENT.md` and `FRONTIER.md` existed, I started treating them as the continuation pointer instead of the original user bootstrap message. The install path also forced a second cycle (DECISIONS.md into sessionStart) rather than a one-shot dump of host files.

## Agent properties that had to be materialized as product

Persistent orientation, checkpoint, UNKNOWN carrier, anti-reduction instruction, baseline/rollback, and a RUN_ID card are not “nice extras”: without them BUILDER-01 cannot survive a session boundary on this host. They landed as files + hooks because Cursor exposes those surfaces, not because they are the ontology of the agent.

## What seems accidental vs structural

Accidental: two overlapping RUN_ID timestamps (2015Z vs 201711Z) from parallel writes; empty Drive Desktop; Agent CLI advertised but not on PATH; `move_agent_to_root` failing with unknown agent while the shell already used `C:\Projects\Proteus`.

Structural: you cannot have a long-running agent in Cursor without some durable carrier outside the chat transcript; hooks are the only global, workspace-independent lever found; anti-reduction cannot be implemented as a parser without becoming the bug it names.

## Conclusions I do not yet have the right to make

- That Proteus “is” the agent, or that the product should collapse into BUILDER-01.
- That hooks+markdown are the correct long-term body versus plugin/MCP/daemon.
- That Drive gateway is or is not necessary beyond this machine’s transport failure.
- What the withheld operator documents will claim about the experiment.
