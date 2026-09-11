"""Host-neutral world-memory access contract.

Intended for Cursor/Codex/Claude/OpenClaw carriers without baking host UI into
the entity substrate. Implementations may wrap CLI or import this module.
"""

from __future__ import annotations

from typing import Any

from .archivarius import reconcile_entity, resolve_via_bridge
from .drive_carrier import (
    export_entity_carrier_bundle,
    import_entity_carrier_bundle,
    recover_entity_from_carrier,
)
from .route import MemoryScope, classify_and_route
from .store import Provenance, WorldStore, ensure_world_home


def resolve_entity(query: str, *, world: WorldStore | None = None) -> dict[str, Any]:
    store = world or WorldStore()
    return store.resolve(query)


def mount_entity(query: str, *, world: WorldStore | None = None) -> dict[str, Any]:
    """Resolve + Archivarius-compatible reconciliation surface."""
    return resolve_via_bridge(query, world=world)


def retrieve_facts(
    query: str,
    *,
    world: WorldStore | None = None,
    include_conflicts: bool = True,
    include_unknowns: bool = True,
) -> dict[str, Any]:
    mounted = resolve_entity(query, world=world)
    out = {
        "entity_id": mounted["entity_id"],
        "identity": mounted["identity"],
        "current_claims": mounted["current_claims"],
        "provenance_bearing": [
            {
                "claim_id": c["claim_id"],
                "text": c["text"],
                "topic": c.get("topic"),
                "status": c.get("status"),
                "provenance": c.get("provenance"),
            }
            for c in mounted["claims"]
            if c.get("provenance")
        ],
        "unresolved_md": mounted["unresolved_md"],
        "secret_refs": mounted["secret_refs"],
        "carriers": mounted["carriers"],
        "projects": mounted["projects"],
    }
    if include_conflicts:
        out["conflicts"] = mounted["conflicts"]
    if include_unknowns:
        out["unknowns"] = mounted["unknowns"]
    return out


def route_observation(
    *,
    scope: str | MemoryScope,
    text: str,
    observer: str,
    entity_query: str | None = None,
    entity_id: str | None = None,
    topic: str | None = None,
    status: str = "current",
    project: str | None = None,
    run_id: str | None = None,
    source: str | None = None,
    kind: str = "observation",
    confidence: str | None = None,
    secret_uri: str | None = None,
    secret_label: str | None = None,
    world: WorldStore | None = None,
) -> dict[str, Any]:
    return classify_and_route(
        scope=scope,
        text=text,
        provenance=Provenance(
            observer=observer,
            project=project,
            run_id=run_id,
            source=source,
            kind=kind,
            confidence=confidence,
        ),
        entity_query=entity_query,
        entity_id=entity_id,
        topic=topic,
        status=status,
        project_path=project,
        secret_uri=secret_uri,
        secret_label=secret_label,
        world=world,
    )


def resolve_secret_ref(secret_uri: str) -> str:
    """Explicit broker get. Never log the return value."""
    from ..secrets import get_secret

    return get_secret(secret_uri)


def describe_secret_ref(secret_uri: str) -> dict[str, Any]:
    from ..secrets import describe_secret

    return describe_secret(secret_uri)


CONTRACT = {
    "schema": "proteus.world.access.v0.1",
    "operations": [
        "resolve_entity",
        "mount_entity",
        "retrieve_facts",
        "route_observation",
        "resolve_secret_ref",
        "describe_secret_ref",
        "reconcile_entity",
        "export_entity_carrier_bundle",
        "import_entity_carrier_bundle",
        "recover_entity_from_carrier",
        "ensure_world_home",
    ],
    "note": "Host-neutral; carriers wrap this API without Cursor-specific assumptions.",
}
