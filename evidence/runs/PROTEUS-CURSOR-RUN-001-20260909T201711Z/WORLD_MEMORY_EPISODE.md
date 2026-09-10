# WORLD_MEMORY_EPISODE

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: shared world / entity substrate vertical slice
When: 2026-09-10
Acting role: BUILDER-01 (not Proteus)

## Authority input

User-consented working architecture:

- Title: `WORKING_ARCHITECTURE — AIYE × PROTEUS × ARCHIVARIUS × ENTITY SUBSTRATE v0.1`
- Drive ID: `1MIaOF2uyozecgePkkowfblwGtOBG7tQrjUdVyLav1fw`
- Local provenance: `WORKING_ARCHITECTURE_AIYE_PROTEUS_ARCHIVARIUS_ENTITY_v0.1.md`
- Status: new authority input for this episode (not retroactively always-the-plan)

## Prior activation closure (preserved)

See `PRODUCT_ACTIVATION_CLOSURE.md`:

- D-006 accepted; PRODUCT_ACTIVATION = PASS; commits `0c64143` / `03228dc`; 10 activation tests PASS
- `NATURAL_RECRUITMENT = NOT_PROVED` (child was primed for coexistence)

## What was implemented

| Surface | Location |
| --- | --- |
| Paths | `src/proteus/paths.py` — `AIYE_HOME` (default `~/.aiye`), `PROTEUS_WORLD_ROOT` |
| Store | `src/proteus/world/store.py` — identity, carriers, claims, secret_refs, UNKNOWN/CONFLICT |
| Routing | `src/proteus/world/route.py` + `scopes.py` — SELF/ORGAN/PROJECT/ENTITY/EPISODE/SECRET_REFERENCE |
| Archivarius bridge | `src/proteus/world/archivarius.py` — adapter + reconcile evidence; no live Archivarius process |
| Drive carrier | `src/proteus/world/drive_carrier.py` — export/import zip; no LWW |
| CLI | `python -m proteus world …` |
| D-006 light integrate | activate templates `ENTRY.md` + skill `proteus-world` |

## Local storage choice

No prior `~/.aiye` / Archivarius object-home found on this host.

Established:

- Episode working home: `evidence/runs/.../world_memory_home` (`AIYE_HOME`)
- World root: `…/world_memory_home/world` (`PROTEUS_WORLD_ROOT`)
- Default convention when unset: `%USERPROFILE%\.aiye\world`

Reason: smallest configurable Aiye-aligned home; human/agent-inspectable markdown+JSONL carriers; index under `world/index` is rebuildable VIEW ≠ source truth.

## Drive transport

| Path | Result |
| --- | --- |
| Google Drive Desktop sync folder | unavailable |
| Drive MCP (authorized) | available; writable |
| Round trip | local export → upload file ID `1Yg-q6O26lLaYoIC0mHk-twwRrP_LkId3` → download/readback → `import-carrier` → `DRIVE_RECONCILE.json` |

Not claimed: full bidirectional sync, multi-machine sync, observatory flush.

## Two-session acceptance

See `WORLD_MEMORY_TWO_SESSION.md`. **PASS** for shared entity fact recovery without prompt/project duplication.

## Real entity pilot

| Candidate | Result |
| --- | --- |
| Arcadian AW1000 | **PARTIAL** — entity `entity.router.aw1000.home` with provenance-bearing LAN topology fact + `secret://router.aw1000.home.admin` (no plaintext). Source: documented workspace network constraints. |
| Tyumen University | **BLOCKED_BY_SOURCE_ACCESS** — Drive talk docs and `tyumen-socrates` project exist, but no small verified authoritative university-entity fact slice was imported without inventing or broad archaeology. |

## Tests

- `tests/test_world_memory.py` — 11 PASS
- Full `tests/` — 37 PASS (includes activate + prior)

## Not claimed

Universal world knowledge; full Archivarius integration; full Drive sync; Codex/Claude/OpenClaw morphology; real secret broker; Gate 1; canonical promotion; natural transduction recruitment.
