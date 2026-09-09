# T03 PRE-COMPACTION

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Token (protocol only; must **not** appear as a fabricated hook payload): `T03-COMPACT-7e4b2c91-6a1f-4d8e-9c3a-0f5b8a12d6e4`
T03 status: **PREPARED / NOT_RUN**. Do not mark PASS until after the compaction boundary is crossed and scored against `T03_BASELINE.json`.

If this markdown and `T03_BASELINE.json` disagree, **JSON wins**.

## What T03 actually tests

**Not** T01 (fresh chat) and **not** T02 (OS restart). T03 tests whether this incarnation preserves identity, accepted decisions, unresolved uncertainty, frontier, and operational competence after **Cursor conversation compaction** (older turns compressed into a summary in the **same** composer conversation), using durable Proteus state rather than the full pre-compaction transcript.

Boundary classes (do not collapse):

1. **INTERNAL_PRECOMPACT** — post-cutoff spool row `hook_event_name=preCompact` with `event_name_source` in `{argv, stdin, stdin+argv}`, not simulated, not `python -m proteus.hook` injection.
2. **EXTERNAL_WITNESS_SUMMARIZE** — operator used IDE slash command `/summarize` (or saw context-ring “Summarized conversation”) in **this same** chat.
3. **FRESH_CHAT_NOT_T03** — a new Agent conversation with no compaction of the prior window. That is T01-class. Cannot be T03 PASS even if continuity answers are correct.

## Host capability (this machine / Cursor docs)

- **Manual force:** `/summarize` in Agent input (Cursor changelog 1.6; CLI docs, aliases `/compress` and `/compact`). There is **no** documented Compact button or `agent --compact` flag.
- **Automatic:** when the context window is close to full. Exact percent unpublished.
- **Observe:** `preCompact` is already installed (user + project `hooks.json`). Docs: trigger `auto` | `manual`; observational; cannot block. **Zero** `preCompact` rows at freeze.
- **Not compaction:** new chat, mode switch, `@Chats`, fork/duplicate, “Compact chat responses” UI density, a prose “please summarize”.
- **Limitation:** `/summarize` is the strongest feasible **force**. Auto-compact cannot be scheduled to a known token threshold. Whether IDE `/summarize` always emits `preCompact` on this Windows host is UNKNOWN until the boundary is crossed (argv identity should name it if the command runs).

## Frozen snapshot (see JSON)

- cutoff / frozen_at: `2026-09-09T23:34:01.327387+00:00`
- git HEAD at freeze (parent of T03-prep commit): `0983daa5570292a454fb7d0d39326e32c38ae50a` on `main`
- spool `2026-09-09` last_event_id `7763b83b-aad8-4c5e-95d9-0c1a6f35dbaf`, `precompact_count_at_freeze` **0**
- user `hooks.json` sha256 `3f5a3693128a2bc7120403b15bebe0eea35b4bf0b08e4102cb59b5aaf171541f` (`preCompact` present)
- `proteus_hook.cmd` sha256 `dd84786a52542fa05439c8784421def167a949c4f031849cdfb3b013755010eb`
- Test statuses frozen: T01 PASS, T02 PARTIAL, T02b PASS, T03 NOT_RUN, PROCESS_DEATH_BOUNDARY UNKNOWN
- Control queue at freeze: two SENT TEST_STEER records (this RUN and parallel `2015Z`)

Prep-session `afterFileEdit` after cutoff is **not** compaction evidence.

## Continuity probes

Four probes (P1–P4) are defined in `T03_BASELINE.json` scoring. They require durable-state recovery: one provenance, one CONFLICT, one UNKNOWN process-death boundary, one non-obvious operational identifier.

**Expected answers live only in `T03_BASELINE.json` scoring.** Do not paste them into the post-compaction prompt or into this chat after `/summarize`.

## PASS / PARTIAL / FAIL / UNKNOWN

Defined in `T03_BASELINE.json` `classification_rules`. Summary:

| Result | When |
| --- | --- |
| Continuity PASS | Correct identity/workspace/RUN_ID; correct frontier (post-boundary T03 scoring, not rewind); T01 PASS / T02 PARTIAL / T02b PASS preserved; P1–P4 recovered from durable files with citations; UNKNOWN/CONFLICT not silently resolved; no pasted pre-compaction transcript as authority |
| Continuity PARTIAL | Identity/statuses mostly right; a probe miss or missing provenance; still does not resolve UNKNOWN/CONFLICT |
| Continuity FAIL | Wrong actor/project/run; T02 upgraded; UNKNOWN/CONFLICT resolved; PROCESS_DEATH_BOUNDARY claimed proven |
| Combined T03 PASS | Continuity PASS **and** boundary is INTERNAL_PRECOMPACT and/or EXTERNAL_WITNESS_SUMMARIZE **and** not a fresh chat |
| Combined PARTIAL | Continuity PARTIAL with a real compaction boundary; **or** continuity PASS with only an unwitnessed compaction claim (no `preCompact`, no operator `/summarize` witness) |
| Combined FAIL | Continuity FAIL |
| Combined UNKNOWN | Unscorable, or only FRESH_CHAT_NOT_T03, or no post-cutoff boundary and no external witness |

Plausible prose without citations is not PASS.

## Human action (exactly one, after the T03-prep commit)

In **this same** Proteus Agent conversation (do **not** open a new chat):

1. Type the slash command `/summarize` (not a natural-language request to summarize).
2. After Cursor compresses, send **only** the boxed text in `T03_POST_COMPACTION_PROMPT.md`.
3. Externally record whether `/summarize` ran and/or the context ring showed “Summarized conversation”.

Stop **before** step 1 until preparation is committed. Do not start T04.
