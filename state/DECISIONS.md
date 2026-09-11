# DECISIONS

## D-001 — Host surfaces for v0.1
- Decision: use Cursor project `AGENTS.md` + always-apply `.cursor/rules/*.mdc` + project/user `hooks.json` command hooks + Python ideal-body installer.
- Not used as primary: Cursor marketplace plugin (not required to prove Gate 1 P0), Drive gateway, vector DB.
- Provenance: PRODUCT_SPEC §2 + host inspection of Cursor 3.19.13 docs (`sessionStart.additional_context`, `stop.followup_message`).
- Status: accepted for first incarnation; reversible via uninstall + backup.

## D-002 — Observability transport
- Decision: local append-only JSONL + local observatory mirror; Drive flush marked FAILED_TRANSPORT until a real synced path or working Drive MCP exists.
- Provenance: WORKLOG spec §13 failure principle + first-run host evidence.
- Status: accepted.

## D-003 — Hook event identity when stdin is empty
- Decision: each Cursor `hooks.json` command string includes `--hook-event <slot>`; `proteus.hook` keeps stdin JSON when valid; `event_name_source` is `stdin` | `argv` | `stdin+argv` | `none` | `conflict`. Conflicting stdin vs argv is recorded and does not pick a winner. Timing is not used to name events.
- Provenance: T02 PARTIAL (empty-stdin live spool) + Cursor hooks docs allowing extra argv on `command` + isolated `.cmd` pipe diagnostic (`T02_DIAGNOSIS.md`).
- Status: accepted. T02b PASS confirmed argv naming on live `sessionStart`/`workspaceOpen`. T02 remains PARTIAL (empty-stdin original). OS quit still UNKNOWN.

## D-004 — Proteus is not identical to BUILDER-01 or to incarnation carriers
- Decision: treat Proteus as a candidate organ (constitutional carrier `60_CURRENT_PROTEUS_STATUS.md`); treat BUILDER-01 as this host's acting role; treat `state/*`, test statuses, hooks, manifests, and the installer as carriers. Do not load the full constitutional document into every `sessionStart`. Do not add a per-task transduction checklist.
- Not claimed: that the de-equation text causes ordinary-work loss-naming without an explicit audit.
- Provenance: F01 self-transduction (`evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/F01_SELF_TRANSDUCTION.md`) against pre-repair `state/IDENTITY.md` / `AGENTS.md` versus `_BOOTSTRAP/BLIND_START/60_CURRENT_PROTEUS_STATUS.md` CORE FUNCTION and `72_PRIMARY_SOURCE_PLUGIN_LAUNCH.md`.
- Status: accepted for this incarnation; reversible via IDENTITY/templates + reinstall.

## D-005 — Portable handoff is classified payload + reconstruct, not a live-host clone
- Decision: the user-carried artifact is `distribution/proteus-portable-handoff.zip` (classified payload of ideal-body source, templates, durable `state/*`, tests, `_BOOTSTRAP`, evidence, and superseded root residue) plus `bootstrap.cmd` that copies the payload and runs source → tests → `install_cursor` on the destination. Generated host files (`AGENTS.md`, `.cursor/rules|skills|hooks`, `state/INCARNATION.md`) are omitted from the payload and recreated. User-global `~/.cursor` hooks and `%USERPROFILE%\.proteus` are installation actions (`bootstrap.cmd --machine-host`), not static package contents. Isolated reconstruct is the default and the clean-room path. Drive observatory and Agent CLI remain non-portable (FAILED_TRANSPORT / unproved). Root `CURRENT.md` / `FRONTIER.md` / `DECISIONS.md` / `UNKNOWN.md` / `DESIGN_v0.1.md` travel as superseded residue, not live carriers.
- Not claimed: PROCESS_DEATH continuity; Gate 1; that an isolated reconstruct equals a live Cursor session; that Python is inside the zip.
- Provenance: portable-handoff episode under RUN `PROTEUS-CURSOR-RUN-001-20260909T201711Z`; product spec §3 form A (ideal/portable body) vs B (host incarnation).
- Status: accepted for this incarnation; reversible by removing `src/proteus/handoff.py` / `distribution/`.

## D-006 — Project activation coexistence (Cursor mount)
- Decision: `python -m proteus.activate --project <path>` performs PRODUCT_SPEC form C project mount on Cursor only. It never overwrites an existing target `AGENTS.md` or `CLAUDE.md`, never overwrites non-`proteus-*` Cursor rules, merges only `proteus_hook` entries into project `.cursor/hooks.json`, creates `state/*` carriers only when absent, records ownership in `.proteus/activation.json`, and removes only owned paths on `--remove`. Mount templates live under `hosts/cursor/templates/activate/` and must not claim the target tree is the Proteus ideal body. Ideal-body incarnation remains `install_cursor` on a Proteus source tree.
- Not claimed: Gate 1; multi-host activation; automatic history import; that activation alone proves organ behavior; that activate installs user-global hooks.
- Provenance: product activation episode under RUN `PROTEUS-CURSOR-RUN-001-20260909T201711Z`; PRODUCT_SPEC §3C / §4.3; evidence `PRODUCT_ACTIVATION.md`.
- Status: accepted for this incarnation; reversible by removing `src/proteus/activate.py` and activate templates.

## D-007 — Shared world / entity substrate + memory-scope routing
- Decision: Durable trans-project world knowledge lives in an **entity substrate** under configurable `AIYE_HOME` / `PROTEUS_WORLD_ROOT` (default `~/.aiye/world`), not inside each project's `state/*`. Proteus provides memory-scope routing (`SELF` / `ORGAN` / `PROJECT` / `ENTITY` / `EPISODE` / `SECRET_REFERENCE`) and resolve/mount/route CLI (`python -m proteus world`). Projects **reference/mount** entities; they do not own global entity truth. Archivarius remains identity/graph/index reconciliation (local adapter emits reconcile evidence; live Archivarius process not required for this slice). Drive carrier bundles are optional BACKUP carriers with explicit reconcile (no last-write-wins). Secret material is `secret_ref` only in semantic memory. Responsibility split: Aiye (self) / Proteus (routing/reentry) / Archivarius (graph) / entity substrate (world) / project memory / secret broker.
- Not claimed: universal ontology; full Archivarius product; full Drive bidirectional sync; multi-host sync; real secret broker; Gate 1; natural recruitment.
- Provenance: user-consented `WORKING_ARCHITECTURE — AIYE × PROTEUS × ARCHIVARIUS × ENTITY SUBSTRATE v0.1` (Drive `1MIaOF2uyozecgePkkowfblwGtOBG7tQrjUdVyLav1fw`); episode `WORLD_MEMORY_EPISODE.md` / `WORLD_MEMORY_TWO_SESSION.md`.
- Status: accepted for this incarnation; reversible by removing `src/proteus/world/` and related activate skill/ENTRY sections.

## D-008 — Real entity hardening + Windows secret broker
- Decision: The first real persistent trans-project entity for this incarnation is `entity.router.aw1000.home` (Arcadyan/Arcadian AW1000). Aliases may expand without creating a second entity. Durable Drive BACKUP carriers for real entities use the existing export/import/reconcile path (no last-write-wins; local authority preserved). Opaque `secret://` refs are resolved by a replaceable Secret Broker; on this Windows host the provider is Credential Manager (`proteus.secrets`). Real router passwords are not auto-migrated; if unavailable, mark `AW1000_REAL_SECRET=UNAVAILABLE` while synthetic broker tests may still PASS. Host-neutral access lives in `proteus.world.api` for later foreign carriers.
- Not claimed: full local↔Drive sync; live Archivarius process; that all imported facts are eternally current; real secret availability when only synthetic broker tests pass; Gate 1; natural recruitment; Codex/Claude portability.
- Provenance: AW1000 real-entity episode under RUN `PROTEUS-CURSOR-RUN-001-20260909T201711Z`; evidence `AW1000_REAL_ENTITY_EPISODE.md`.
- Status: accepted for this incarnation; reversible by removing `src/proteus/secrets/` and reverting AW1000 carrier pointers.
