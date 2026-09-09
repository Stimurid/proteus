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
- Cursor Agent CLI / ACP: NOT_RUN (binary missing)
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
| T02b named-hook restart after argv identity | NOT_RUN | prepared `T02b_PRE_RESTART.md` / `T02b_BASELINE.json`; wait physical quit |
| T03 compaction | NOT_RUN | |
| T04 correction later session | NOT_RUN | capture skill installed only |
| T05 project isolation | NOT_RUN | |
| T11 organ preservation (behavioral) | PARTIAL | anti-reduction rule present in `.cursor/rules`; no independent organ task executed |
| Global hook in arbitrary other workspace | NOT_RUN | user hooks installed; other workspace not opened |
| Drive observatory visible to another agent | FAIL | transport blocked; local mirror only |
| External control CLI queue | PASS | enqueue + claim |
| External control live IDE stop-hook | NOT_RUN | |
| Agent CLI headless | FAIL / blocked | `agent` not on PATH |

## 10. SELF-UPDATE / SECOND MUTATION

Deficit: decisions missing from sessionStart orientation.
Source: `events.py` includes `DECISIONS.md`.
Second install: cycle2/cycle3 receipts.
Tests: `test_orientation_loads_state`.

T02 empty-stdin repair (third source→install cycle this run): `hook_identity.py` + `--hook-event` in installer `hooks.json`; tests `tests/test_hook_event_identity.py`; host files via `python -m proteus.install_cursor`.

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

T02 remains PARTIAL. T02b: full Cursor quit/reopen, then new Agent chat with `T02b_POST_RESTART_PROMPT.md`. T03 not started. Drive observatory flush remains later (FAILED_TRANSPORT).

FINAL STATUS:
FIRST_INCARNATION = PARTIAL (installed + unit/install + T01; T02 hooks PARTIAL; T02b NOT_RUN)
OBSERVABILITY = PARTIAL (local PASS, Drive FAIL)
EXTERNAL_CONTROL = PARTIAL (queue PASS, live stop/CLI FAIL or NOT_RUN)
CLEAN_REENTRY = PASS (externally witnessed; see T01_CLEAN_REENTRY.md)
T02_HOOKS_RESTART = PARTIAL
T02B_NAMED_HOOK_RESTART = NOT_RUN
GATE_1 = NOT_YET
