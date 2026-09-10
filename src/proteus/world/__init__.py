"""Shared world / entity substrate (vertical slice).

ENTITY ≠ CARRIER; VIEW ≠ SOURCE TRUTH. Index under world/index is rebuildable.
"""

from __future__ import annotations

from .archivarius import reconcile_entity, rebuild_index
from .drive_carrier import export_entity_carrier_bundle, import_entity_carrier_bundle
from .route import MemoryScope, classify_and_route, route_project_decision
from .store import (
    EntityAmbiguousError,
    EntityNotFoundError,
    WorldStore,
    ensure_world_home,
)

__all__ = [
    "MemoryScope",
    "WorldStore",
    "EntityAmbiguousError",
    "EntityNotFoundError",
    "ensure_world_home",
    "classify_and_route",
    "route_project_decision",
    "reconcile_entity",
    "rebuild_index",
    "export_entity_carrier_bundle",
    "import_entity_carrier_bundle",
]
