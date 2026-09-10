# FRESH_INCARNATION_CLOSURE

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: origin-side closure of the fresh-incarnation / operating-brief experiment
When: 2026-09-10
Authority for this closure: preserved origin + fresh filesystem evidence only. Fresh Agent raw stdout is **not** rewritten.

## Evidence used (not altered)

| Side | Path |
| --- | --- |
| Fresh brief | `C:\Projects\Proteus-FRESH-001\Proteus\distribution\PROTEUS_OPERATING_BRIEF.md` |
| Fresh episode | `C:\Projects\Proteus-FRESH-001\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\OPERATING_BRIEF_EPISODE.md` |
| Origin CLI episode | `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/FRESH_AGENT_CLI_EPISODE.md` |
| Origin raw stdout | `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/FRESH_AGENT_CLI_STDOUT.txt` |
| Origin meta | `evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/FRESH_AGENT_CLI_META.json` |
| Prior prep / launch | `FRESH_WORKSPACE_PREP.md`, `FRESH_WORKSPACE_LAUNCH.md`, `PORTABLE_HANDOFF.md` |

## Established distinctions (do not collapse)

| Claim | Status | Basis |
| --- | --- | --- |
| Portable handoff clean-room reconstruction | **PASS** (prior packager episode) | `PORTABLE_HANDOFF.md`; zip-only temp reconstruct; not Gate 1 |
| Real fresh workspace reconstruction from distribution ZIP | **PASS** (prep) | `FRESH_WORKSPACE_PREP.md`; destination `C:\Projects\Proteus-FRESH-001\Proteus`; isolated; not a clone of origin `.git` |
| GUI open of that workspace | **PASS** (launch only) | `FRESH_WORKSPACE_LAUNCH.md`; `Cursor.exe -n`; workspaceStorage verified |
| Independent Cursor Agent CLI instantiation against that tree | **PASS** | `FRESH_AGENT_CLI_EPISODE.md` / `FRESH_AGENT_CLI_META.json`; PID 28588; no `--continue`/`--resume`; prompt-only |
| Completion of the operating-brief task (`FRESH_AGENT_TASK.md`) | **PASS** | exit 0; brief present (~2302 words); fresh `OPERATING_BRIEF_EPISODE.md`; raw completion report in `FRESH_AGENT_CLI_STDOUT.txt` |
| Controlled compression / accounting of transfer losses | **PASS** (within that episode’s own readback) | Fresh agent recorded survives / does-not-survive / weakened distinctions / resists compression in `OPERATING_BRIEF_EPISODE.md` and the brief itself |
| Process continuity (PROCESS_DEATH / same Cursor GUI process) | **NOT CLAIMED** | Reconstruction + CLI child ≠ origin GUI continuity; `RECONSTRUCTION.md` / D-005 / CLI episode “Not claimed” |
| Gate 1 | **NOT_YET** (unchanged) | No Gate upgrade from prep, launch, CLI spawn, or brief write |
| Spontaneous ordinary-work loss-naming / organ behavior under unprompted conditions | **NOT TESTED** | F01 OPEN / T11 PARTIAL remain; this episode tasked an explicit brief-writing job, not spontaneous interception |

## Provenance divergence: “Agent CLI unproved”

The fresh Agent’s final report (verbatim in `FRESH_AGENT_CLI_STDOUT.txt`) states status **Agent CLI unproved**.

That statement is **historically correct relative to the reconstructed tree’s carriers** at the moment of that session:

- The fresh workspace was reconstructed from a portable package whose durable `state/*` / evidence predated origin-side CLI proof.
- Origin later proved Agent CLI availability + auth + independent run (`FRESH_AGENT_CLI_EPISODE.md`; RESOLVED in origin `state/UNRESOLVED.md`).
- The fresh Agent did not receive origin conversation updates; its local UNRESOLVED/RUN_RECEIPT still said CLI unproved, and it correctly refused to invent a newer machine fact from outside its authority.

**Do not** edit the fresh stdout or fresh-side historical files to “correct” that line. Origin closure records the fork:

| Frame | Agent CLI claim |
| --- | --- |
| Fresh reconstructed carriers + fresh Agent report | unproved (as of packaged state) |
| Origin machine after CLI episode | proved for this host (install + auth reuse + successful `-p` run) |

## Not established by success of the overall experiment

- Gate 1 survival or PROCESS_DEATH_BOUNDARY
- Upgrade of T01 / T02 / T02b / T03 / T11
- That the operating brief is a constitution or replaces `state/*`
- That IDE Agent chats and CLI sessions are the same continuity
- That organ behavior appears without an explicit task (spontaneous loss-naming)

## Closure verdict

Fresh-incarnation experiment **closed** at origin: prep PASS, GUI launch demonstrated, independent CLI instantiation PASS, operating-brief task PASS, compression accounting recorded by the fresh Agent, process continuity NOT CLAIMED, Gate 1 unchanged, spontaneous organ behavior NOT TESTED. Divergence on “Agent CLI unproved” preserved as provenance, not normalized into the child’s raw result.
