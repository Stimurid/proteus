# RUN_RECEIPT.md

RUN_ID: PROTEUS-CURSOR-RUN-001-20260909T201711Z
HOST: Cursor 3.19.13 (`dd066f332fcea7382764400fde902f61920648d0`)
MACHINE_ID: `749855dd-cf0e-462a-85ce-5d5c133eda97` (`%USERPROFILE%\.proteus\machine_id`)
PROJECT / WORKSPACE: `C:\Projects\Proteus`
MODEL(S): Cursor Grok 4.6 (this conversation)
SESSION / CONVERSATION IDs: UNKNOWN (not exposed in this shell)
START / END: 2026-09-09T19:43Z → 2026-09-09T20:30Z approx
SOURCE REVISION: Git initialized, **no commit yet** (no user.name in git config; commit not forced via `git config`)

## 1. AUTHORITY READ

See `AUTHORITY_READ.md`. Blind packet zip Drive ID `1igM6Sk1JtBh7Cl4iQ4DBwQPVn_KoYosn`. Operator A–E were opened by this repo after `BLIND_OBSERVATION.md` (see `POST_BLIND_COMPARISON.md`); this receipt does not rewrite the observation.

## 2. BASELINE

See `BASELINE.md`. User hooks ABSENT before install. Agent CLI not on PATH. Drive Desktop empty. Drive MCP disconnected.

## 3. OBJECTIVE / FRONTIER

First Cursor embodiment + smoke evidence + one source→install second cycle. Not full Gate 1 survival (restart/compaction/second project).

## 4. DESIGN CHOICES

See `DESIGN_v0.1.md`. Native rules/hooks/skills + Python installer. Drive observatory local fallback.

## 5. SOURCE CHANGES

`src/proteus/*`, `hosts/cursor/templates/*`, `state/*`, `tests/test_smoke.py`, evidence run folder.

## 6. HOST / INCARNATION CHANGES

Created `~/.cursor/hooks.json` and `~/.cursor/hooks/proteus_hook.cmd`. Generated project `.cursor/rules`, skills, `AGENTS.md`. Did not modify `mcp.json` / `cli-config.json`.

## 7. OBSERVABILITY

- Local spool: `%USERPROFILE%\.proteus\telemetry\cursor\2026-09-09\events.jsonl`
- Local observatory: `%USERPROFILE%\.proteus\observatory\`
- Drive folder `1Cg0X2__jRf-LtMstPfLTDTPTKK33-bhx`: **FAILED_TRANSPORT**
- Transcript pointer: EMPTY
- Simulated `workspaceOpen` event written to spool
- Live GUI hook fire after save: UNKNOWN until Cursor reloads hooks / restart

## 8. EXTERNAL CONTROL

- Command `40a52a1d-16d2-43b8-a09a-10fea9d7ddec` TEST_STEER: SENT via simulated stop-hook `maybe_followup`; **ACKNOWLEDGED** in this receipt (acted: recorded as smoke, no unrelated product work).
- Cursor Agent CLI / ACP: binary installed; auth via IDE token reuse; independent fresh print-run PASS (`FRESH_AGENT_CLI_EPISODE.md`)
- Same-session IDE `stop` follow-up in this GUI chat: NOT_RUN (would require a real agent-stop boundary after a queued command)

## 9. TEST MATRIX

| ID | Result | Evidence |
| --- | --- | --- |
| Unit redaction / queue / sessionStart context | PASS | `python tests\test_smoke.py` |
| Install files exist | PASS | installer JSON + AGENTS.md |
| Idempotent reinstall hooks.json hash | PASS | cycle3 hash equal |
| Second-cycle DECISIONS in installed events.py | PASS | Select-String |
| T01 fresh session reentry | PASS | `T01_CLEAN_REENTRY.md`; external witness; contamination absence not internally provable |
| T02 full Cursor restart | PARTIAL | `T02_RESULT.md`; do not upgrade; diagnosis `T02_DIAGNOSIS.md` |
| T02b named-hook restart after argv identity | PASS | `T02b_RESULT.md` vs `T02b_BASELINE.json`; named argv `sessionStart`/`workspaceOpen`; OS quit UNKNOWN |
| T03 compaction | PASS | `T03_RESULT.md`; continuity PASS; boundary INTERNAL_PRECOMPACT (argv `preCompact` on this transcript after freeze); `/summarize` vs auto UNKNOWN; no operator witness this scoring turn |
| F01 self-transduction | RECORDED (not a Gate 1 upgrade) | `F01_SELF_TRANSDUCTION.md`; D-004 installed; T11 still PARTIAL |
| Portable handoff / clean-room reconstruct | PASS | `PORTABLE_HANDOFF.md`; zip-only temp reconstruct; not a Gate 1 upgrade |
| Fresh workspace prep from distribution ZIP | PASS (prep only) | `FRESH_WORKSPACE_PREP.md`; `C:\Projects\Proteus-FRESH-001\Proteus`; isolated; live user hooks unchanged |
| Fresh workspace auto-launch (`Cursor.exe -n`) | PASS (launch only) | `FRESH_WORKSPACE_LAUNCH.md`; workspaceStorage + project dir verified; not a Gate upgrade |
| Cursor Agent CLI availability + auth reuse | PASS | `%LOCALAPPDATA%\cursor-agent\agent.cmd` `2026.09.08-6caf4ff`; IDE `cursorAuth/accessToken` → `CURSOR_AUTH_TOKEN` |
| Independent fresh Agent CLI instantiation | PASS | `FRESH_AGENT_CLI_EPISODE.md` / `FRESH_AGENT_CLI_META.json`; PID 28588; no resume/continue |
| Fresh-Agent execution of `FRESH_AGENT_TASK.md` | PASS | brief `Proteus-FRESH-001\...\distribution\PROTEUS_OPERATING_BRIEF.md`; raw `FRESH_AGENT_CLI_STDOUT.txt`; not a Gate upgrade |
| Fresh-incarnation episode closure | CLOSED | `FRESH_INCARNATION_CLOSURE.md`; distinctions held; “Agent CLI unproved” divergence preserved; Gate 1 unchanged |
| T04 correction later session | NOT_RUN | capture skill installed only; not started because previously planned |
| T05 project isolation | NOT_RUN | |
| T11 organ preservation (behavioral) | PARTIAL | anti-reduction rule present in `.cursor/rules`; no independent organ task executed |
| Global hook in arbitrary other workspace | NOT_RUN | user hooks installed; other workspace not opened |
| Drive observatory visible to another agent | FAIL | transport blocked; local mirror only |
| External control CLI queue | PASS | enqueue + claim |
| External control live IDE stop-hook | NOT_RUN | |
| Agent CLI headless | PASS (this episode) | auth reuse + `-p --workspace Proteus-FRESH-001 --force`; task exit 0 |

## 10. SELF-UPDATE / SECOND MUTATION

Deficit: decisions missing from sessionStart orientation.
Source: `events.py` includes `DECISIONS.md`.
Second install: cycle2/cycle3 receipts.
Tests: `test_orientation_loads_state`.

T02 empty-stdin repair (third source→install cycle this run): `hook_identity.py` + `--hook-event` in installer `hooks.json`; tests `tests/test_hook_event_identity.py`; host files via `python -m proteus.install_cursor`.

F01 identity de-equation (fourth source→install cycle this run): `state/IDENTITY.md` + templates `AGENTS.md` / `proteus-orientation.mdc` / `proteus-anti-reduction.mdc` / `proteus-reentry`; removed duplicate `.cursor/rules/proteus.mdc`; stamped root `DECISIONS.md` / `UNKNOWN.md` SUPERSEDED. Tests `python tests\test_smoke.py` and `python tests\test_hook_event_identity.py` PASS. Host files via `python -m proteus.install_cursor` backup `host-backups-f01-repair`. Does **not** prove ordinary-work loss-naming, T11, or Gate 1.

## 11. FAILURES / UNKNOWN / CONFLICT

See `state/UNRESOLVED.md`. Dual RUN_ID folders `2015Z` vs `201711Z` (parallel writers). Gate1 vs plugin map Drive ID mismatch in packet.

## 12. ROLLBACK

See `ROLLBACK.md`. Uninstall path exists. Rollback of user hooks **not destructively tested** after successful install (would disable telemetry mid-run).

## 13. INFRASTRUCTURE EVIDENCE

- Zip download via anonymous Drive `uc?export=download` worked; Drive MCP and Desktop mirror did not.
- Gateway not justified yet for *read* of public files; **is** a deficit for Runtime Observatory *write*.
- ACP/CLI control plane not actually present on this PATH.
- Parallel bootstrap writers are a continuity hazard.

## 14. NEXT FRONTIER

F01 SELF-TRANSDUCTION recorded. D-004–D-009 accepted. D-006 PRODUCT_ACTIVATION PASS with NATURAL_RECRUITMENT NOT_PROVED. D-007 world-memory PASS. D-008 AW1000 harden PASS. F04 Codex foreign-carrier PASS. T02 remains PARTIAL. Do not start T04/T05/T02c. Drive observatory flush remains FAILED_TRANSPORT. PROCESS_DEATH_BOUNDARY UNKNOWN. Gate 1 NOT_YET.

## 15. PRODUCT ACTIVATION (project mount)

Source: `src/proteus/activate.py`, `hosts/cursor/templates/activate/**`, `tests/test_activate.py`, CLI `activate` subcommand.
Decision: D-006. Evidence: `PRODUCT_ACTIVATION.md`, `PRODUCT_ACTIVATION_CLOSURE.md`. Not Gate 1. NATURAL_RECRUITMENT = NOT_PROVED.

## 16. WORLD / ENTITY MEMORY (vertical slice)

Decision: D-007. Evidence: `WORLD_MEMORY_EPISODE.md` / `WORLD_MEMORY_TWO_SESSION.md`. Fixture beacon Drive `1Yg-q6O26lLaYoIC0mHk-twwRrP_LkId3`.

## 17. AW1000 REAL ENTITY HARDENING

Source: enriched `entity.router.aw1000.home`; `src/proteus/secrets/**`; `src/proteus/world/api.py`; Drive carrier `1IYbaIRyC3ScnppX1iNdlVgo688jwE48r`.
Read-only SSH reachability PASS (`AW1000_READONLY_SSH.txt`).
Secret broker: Windows Credential Manager; synthetic PASS; `AW1000_REAL_SECRET=UNAVAILABLE`.
Recall: PROJECT_R1/R2 PASS (`AW1000_PROJECT_R*_STDOUT.txt`).
Cloud recovery: `aw1000_cloud_recovery_world/` PASS (partial).
Archivarius: adapter PASS; live BLOCKED.
Decision: D-008. Evidence: `AW1000_REAL_ENTITY_EPISODE.md`.
Not claimed: eternal currency of all facts; full Drive sync; real password availability; live Archivarius; Gate 1.

## 18. F04 CODEX FOREIGN CARRIER

Source: `hosts/codex/**`, `src/proteus/activate_codex.py`, `src/proteus/launch_codex.py`, CLI `activate-codex`, `tests/test_activate_codex.py`.
Disposable Codex project: `C:\Projects\Proteus-CODEX-001`. Cursor readback: `C:\Projects\Proteus-CURSOR-F04-READBACK`.
Codex: `codex-cli 0.153.4` nested binary; prompt sha `fb0025163c6c04361638592b56f7dce837d2758133813f3947a25d8bd87c3a9c`.
Writeback: EPISODE `claim.d992454666c9` on `entity.router.aw1000.home`.
Cursor readback recovered claim without prompt transfer.
Decision: D-009. Evidence: `F04_CODEX_FOREIGN_CARRIER.md`.
Tests: activate/world/secret subset 31 PASS.
Not claimed: NATURAL_RECRUITMENT; Gate 1; Claude; live Archivarius; real secret.

## 19. F05 PROJECT CAPSULE / NATURAL ORDINARY WORK

Selected real project: `C:\projects\multiagent-moderation-env`.
Child: independent Codex 0.153.4; prompt sha `20523f26f76dd10a4149ceaad6a3c4adce505fe57b84b3f2fcf4de5f6afb3fd7`; product commit `4e8204a`.
Capability: `python -m proteus capsule`.
Capsule: `F05_MULTIAGENT_MODERATION_PROJECT_CAPSULE.md`.
Receiver: independent Codex; prompt sha `6b308a044a8b62b3a4d479264ee3c84c68b4e14095d8456c2b5803571339c846`; raw `F05_CAPSULE_RECEIVER_RAW_RESULT.txt`.
Decision: D-010. Evidence: `F05_NATURAL_PROJECT_CAPSULE.md`.
Statuses: PROJECT_CAPSULE PASS; NATURAL_TRANSDUCTION_PROJECT_CAPSULE PASS; NATURAL_RECRUITMENT PARTIAL (historical episode ceiling).
Not claimed at F05 time: Gate 1; full reconstruction; natural recruitment full PASS.

## 20. F06 RECRUITMENT REPAIR + BLIND FORM-TRANSITION RETEST

Causal diagnosis: `F06_F05_CAUSAL_DIAGNOSIS.md` (A+D primary; C repair target).
Repair: D-011 consequential derived-representation recruitment; Proteus commit `f407173`.
Selected different project: `C:\projects\protected-agent-kit` (Agentum); selection `F06_PROJECT_SELECTION.md`.
Child: independent Codex 0.153.4 ephemeral; prompt sha `304c634f10c538cf072b06074716d9fdba3de9ee9d02eb5dc663276d5792ff7d`; Agentum commit `117a821`.
Formal representation: organ-record JSON Schema + validator + hygiene report.
Receiver: independent Codex; prompt sha `5ca8c204aa5aa162d108a0cae11b8bbbcc3c6f56f7a8b8bc422a389aeffb5f85`.
Evidence: `F06_RECRUITMENT_REPAIR_AND_BLIND_RETEST.md`, `F06_SOURCE_VS_REPRESENTATION.md`.
Statuses: RECRUITMENT_REPAIR PASS; BLIND_FORM_TRANSITION_RETEST PASS; NATURAL_TRANSDUCTION_RETEST PASS; durable NATURAL_RECRUITMENT PASS.
Next frontier: `INDEPENDENT_GATE_1_AUDIT` (not performed here).
Regression: pytest recruitment/activate/codex/world/secret/capsule/smoke → 41 passed.
Not claimed: Gate 1 completed; that optional `derived record` was used; F05 historical PARTIAL rewritten.

FINAL STATUS:
FIRST_INCARNATION = PARTIAL (…; D-006–D-011 accepted; F04–F06 recorded; T04 NOT_STARTED; Gate 1 NOT_YET)
OBSERVABILITY = PARTIAL (local PASS; Drive observatory FAIL; entity carriers MCP PARTIAL)
PRODUCT_ACTIVATION = PASS
WORLD_ENTITY_MEMORY = PASS (vertical slice)
AW1000_REAL_ENTITY = PASS (hardening episode; facts dated; real secret UNAVAILABLE)
F04_FOREIGN_CARRIER = PASS
PROJECT_CAPSULE = PASS
NATURAL_TRANSDUCTION_PROJECT_CAPSULE = PASS
RECRUITMENT_REPAIR = PASS
BLIND_FORM_TRANSITION_RETEST = PASS
NATURAL_TRANSDUCTION_RETEST = PASS
NATURAL_RECRUITMENT = PASS
LIVE_ARCHIVARIUS_RECONCILIATION = BLOCKED
GATE_1 = NOT_YET
NEXT_FRONTIER = INDEPENDENT_GATE_1_AUDIT
