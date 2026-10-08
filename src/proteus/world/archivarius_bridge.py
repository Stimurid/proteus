"""Live Archivarius bridge skeleton (Phase 5.6).

Status: SKELETON. Not a live Archivarius runtime. This module provides the
in-process adapters that will be exposed through ``archivarius-mcp`` once that
MCP service is wired up (plan §6, phase 5.6).

Three tools from plan §6:

1. ``archivarius_graph(entity_id)``
      Relations + carriers + current claims as a derived graph. Rebuilt from
      the local Proteus store each call.

2. ``archivarius_reconcile(entity_a, entity_b)``
      Merge policy stub for cross-host-created duplicate entities (plan Gap L).
      Current behaviour: refuse to merge, surface the duplicate as an UNRESOLVED
      row for operator review. Automated merge is deferred until the policy is
      explicit and the operator has approved the merge heuristics.

3. ``archivarius_claims_current(topic)``
      Resolver "which claim is current on this topic across all entities".

The MCP wrapper layer is intentionally not shipped here — it belongs in
``C:\\projects\\aorus-ecosystem\\services\\archivarius-mcp\\`` so OpenClaw and
other MCP clients can mount it. This module is the pure-Python core they will
call into.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .store import WorldStore

ARCHIVARIUS_SCHEMA = "proteus.archivarius_bridge.v0.2"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def archivarius_graph(entity_id: str, *, world: WorldStore | None = None) -> dict[str, Any]:
    """Return a derived graph view: identity, carriers, current claims, relations."""
    store = world or WorldStore()
    mounted = store.mount(entity_id)
    identity = mounted["identity"]
    carriers = mounted["carriers"]["carriers"]
    current = mounted["current_claims"]
    conflicts = mounted["conflicts"]
    relations = identity.get("relations") or []
    return {
        "schema": ARCHIVARIUS_SCHEMA,
        "generated_utc": utc_now(),
        "entity_id": entity_id,
        "identity": identity,
        "carriers": carriers,
        "relations": relations,
        "current_claim_ids": [c["claim_id"] for c in current],
        "conflict_claim_ids": [c["claim_id"] for c in conflicts],
        "current_claim_topics": sorted({c.get("topic") for c in current if c.get("topic")}),
        "note": "derived graph; VIEW_NE_SOURCE_TRUTH",
    }


def archivarius_reconcile(
    entity_a: str, entity_b: str, *, world: WorldStore | None = None
) -> dict[str, Any]:
    """Stub: surface a potential cross-host duplicate without automated merge.

    Returns an UNRESOLVED row describing both entities and the aliases that
    overlap. Automated merge requires an explicit policy (plan Gap L); until
    that policy is written, the correct action is operator review.
    """
    store = world or WorldStore()
    a = store.mount(entity_a)
    b = store.mount(entity_b)
    a_aliases = {str(x).lower() for x in [a["identity"].get("display_name"), *a["identity"].get("aliases", [])] if x}
    b_aliases = {str(x).lower() for x in [b["identity"].get("display_name"), *b["identity"].get("aliases", [])] if x}
    overlap = sorted(a_aliases & b_aliases)
    return {
        "schema": ARCHIVARIUS_SCHEMA,
        "generated_utc": utc_now(),
        "status": "UNRESOLVED",
        "entity_a": entity_a,
        "entity_b": entity_b,
        "shared_aliases": overlap,
        "a_current_claim_count": len(a["current_claims"]),
        "b_current_claim_count": len(b["current_claims"]),
        "merge_policy": "DEFERRED",
        "note": (
            "Automated merge not performed. Operator must choose authority entity "
            "and record a `conflicts_with` chain pointing the deprecated entity at "
            "the retained one. See plan §6 Phase 5.6 and Gap L."
        ),
    }


def archivarius_claims_current(topic: str, *, world: WorldStore | None = None) -> dict[str, Any]:
    """Return all current claims across all entities carrying the given topic."""
    store = world or WorldStore()
    hits = []
    for eid in store.list_entity_ids():
        for c in store.list_claims(eid):
            if c.get("topic") == topic and c.get("status") == "current":
                hits.append({"entity_id": eid, "claim": c})
    return {
        "schema": ARCHIVARIUS_SCHEMA,
        "generated_utc": utc_now(),
        "topic": topic,
        "hit_count": len(hits),
        "hits": hits,
    }
