# archivarius-mcp (SKELETON — Phase 5.6)

Live Archivarius bridge, to be exposed to MCP clients (Claude Code, OpenClaw
agent, Cursor+Kilo, Codex) as the "world identity authority" organ promised in
`WORKING_ARCHITECTURE §2` but never materialised as a runtime.

**Status 2026-10-08**: core skeleton only. Pure-Python core lives in
`src/proteus/world/archivarius_bridge.py`. The MCP server wrapper (same shape as
`proteus-mcp` and `drive-fetch` under `aorus-ecosystem/services/`) will be
scaffolded next and should land in
`C:\projects\aorus-ecosystem\services\archivarius-mcp\`.

## Design decisions (locked)

- Archivarius is **not** a semantic monarch. It is a reconciliation organ.
- Backing store: Proteus local world substrate (`~/.aiye/world/entities/`).
- No parallel entity database. The graph is **derived** from Proteus on every
  call. Caching is a VIEW, never SOURCE_TRUTH.
- No last-write-wins merge for cross-host duplicates. Automated merge is
  deferred until the policy is explicit (plan Gap L).

## Tools

| Tool | Status | Core function |
|---|---|---|
| `archivarius_graph(entity_id)` | implemented in core | relations + carriers + current claim topics |
| `archivarius_reconcile(entity_a, entity_b)` | surfaces UNRESOLVED only (deferred merge) | detect overlap, flag for operator |
| `archivarius_claims_current(topic)` | implemented in core | cross-entity current-claim lookup by topic |

## Open work (next slice)

- MCP server (`server.py`) mirroring `proteus-mcp` structure.
- Wire into OpenClaw Gateway and Claude Code hooks.
- Decide + document merge policy for `archivarius_reconcile`.
- Add `after_rebuild_index` hook integration — recompute a cached graph digest.
- Integrate with `hestia-formation-resolver` consumer path (plan §6 acceptance 3).

## Reality clock

Core + tests: 1 day. MCP wrapper: 0.5 day. Merge policy spec: 0.5 day. HESTIA
link + round-trip verification: 1 day. Total ~3 days from this skeleton.
