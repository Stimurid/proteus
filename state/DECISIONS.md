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
