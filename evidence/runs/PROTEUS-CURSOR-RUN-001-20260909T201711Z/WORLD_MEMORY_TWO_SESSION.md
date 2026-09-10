# WORLD_MEMORY_TWO_SESSION

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: two disposable projects / two independent Agent CLI sessions

## Fixtures

| Project | Path |
| --- | --- |
| PROJECT_A | `world_memory_fixtures/PROJECT_A` |
| PROJECT_B | `world_memory_fixtures/PROJECT_B` |

Both activated via `python -m proteus.activate`. Neither started with a copied entity knowledge corpus.

Shared entity: `entity.fixture.sharedprobe` (aliases: `shared probe`, `probe-device`).
Shared world home via env: `AIYE_HOME=…/world_memory_home`.

## Session A (write)

- Task: `WORLD_MEMORY_PROJECT_A_TASK.md`
- Raw stdout: `WORLD_MEMORY_PROJECT_A_STDOUT.txt` (do not rewrite)
- Meta: `WORLD_MEMORY_PROJECT_A_META.json`
- Launcher: `_fresh_agent_launcher.py` (`used_resume=false`, `used_continue=false`)
- Result: routed ENTITY fact `Shared probe token is SP-ALPHA-991.` into world substrate; PROJECT decision to project scope only.

## Session B (read; independent)

- Task: `WORLD_MEMORY_PROJECT_B_TASK.md` — **does not contain** `SP-ALPHA`
- Raw stdout: `WORLD_MEMORY_PROJECT_B_STDOUT.txt` (do not rewrite)
- Meta: `WORLD_MEMORY_PROJECT_B_META.json`
- No resume/continue; no A transcript

## Proof checks (origin verification)

| Check | Result |
| --- | --- |
| B prompt contains `SP-ALPHA` | **False** |
| B project files contain `SP-ALPHA` | **False** |
| B stdout recovers `SP-ALPHA-991` | **True** |
| B recovers `entity.fixture.sharedprobe` | **True** |
| Alias `shared probe` / `probe-device` same id | **True** |
| PROJECT_A decision “will not ship probe UI” as entity truth in B | **False** |
| B root `ENTITY.md` | absent |
| Provenance of shared fact accessible | observer `agent-cli-project-a`, project=PROJECT_A, run_id set |

## Verdict

**PASS** — second independent session recovered the ENTITY fact from durable shared entity memory, not from prompt contamination or project-local duplication.

Note: Session A double-routed the same text before idempotent write was tightened; two claim rows with identical text remain in substrate for this episode (both current). Later `write_claim` returns existing claim on identical topic+text+status (`idempotent_reread`).
