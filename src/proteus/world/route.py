"""Proteus memory-scope routing — decide where durable knowledge belongs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..paths import proteus_home, world_root
from .scopes import MemoryScope
from .store import Provenance, WorldStore, ensure_world_home


def _organ_ledger() -> Path:
    d = proteus_home() / "memory" / "organ"
    d.mkdir(parents=True, exist_ok=True)
    return d / "claims.jsonl"


def _self_ledger() -> Path:
    d = proteus_home() / "memory" / "self"
    d.mkdir(parents=True, exist_ok=True)
    return d / "claims.jsonl"


def _append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def classify_and_route(
    *,
    scope: MemoryScope | str,
    text: str,
    provenance: Provenance,
    entity_query: str | None = None,
    entity_id: str | None = None,
    topic: str | None = None,
    status: str = "current",
    project_path: str | None = None,
    secret_uri: str | None = None,
    secret_label: str | None = None,
    world: WorldStore | None = None,
) -> dict[str, Any]:
    """Route a durable observation to the correct substrate.

    Returns a receipt describing where the knowledge was written.
    Does not invent a universal merge law for PROJECT carriers beyond append.
    """
    ensure_world_home()
    scope_e = MemoryScope.parse(scope) if isinstance(scope, str) else scope
    store = world or WorldStore()
    receipt: dict[str, Any] = {
        "scope": scope_e.value,
        "text": text,
        "routed_utc": provenance.observed_at,
    }

    if scope_e is MemoryScope.ENTITY:
        if not entity_id and not entity_query:
            raise ValueError("ENTITY scope requires entity_id or entity_query")
        if entity_id:
            eid = entity_id
        else:
            mounted = store.resolve(entity_query or "")
            eid = mounted["entity_id"]
        claim = store.write_claim(
            eid,
            text,
            provenance,
            topic=topic,
            status=status,
            scope=MemoryScope.ENTITY,
        )
        if project_path:
            store.link_project(eid, project_path)
        receipt.update({"entity_id": eid, "claim": claim, "destination": str(store.entity_dir(eid))})
        return receipt

    if scope_e is MemoryScope.SECRET_REFERENCE:
        if not entity_id and not entity_query:
            raise ValueError("SECRET_REFERENCE requires an entity to attach the ref")
        if not secret_uri:
            raise ValueError("SECRET_REFERENCE requires secret_uri (secret://...)")
        eid = entity_id or store.resolve(entity_query or "")["entity_id"]
        ref = store.add_secret_ref(
            eid,
            secret_uri,
            label=secret_label or text,
            scope="entity",
        )
        # Also record episodic pointer without plaintext
        claim = store.write_claim(
            eid,
            f"Secret reference recorded: {secret_uri} ({secret_label or text})",
            provenance,
            topic=topic or f"secret_ref:{secret_uri}",
            status="current",
            scope=MemoryScope.SECRET_REFERENCE,
        )
        receipt.update({"entity_id": eid, "secret_ref": ref, "claim": claim})
        return receipt

    if scope_e is MemoryScope.PROJECT:
        if not project_path:
            raise ValueError("PROJECT scope requires project_path")
        return route_project_decision(project_path, text, provenance, topic=topic)

    if scope_e is MemoryScope.ORGAN:
        obj = {
            "scope": scope_e.value,
            "text": text,
            "topic": topic,
            "status": status,
            "provenance": provenance.to_dict(),
        }
        _append_jsonl(_organ_ledger(), obj)
        receipt["destination"] = str(_organ_ledger())
        receipt["claim"] = obj
        return receipt

    if scope_e is MemoryScope.SELF:
        obj = {
            "scope": scope_e.value,
            "text": text,
            "topic": topic,
            "status": status,
            "provenance": provenance.to_dict(),
        }
        _append_jsonl(_self_ledger(), obj)
        receipt["destination"] = str(_self_ledger())
        receipt["claim"] = obj
        return receipt

    if scope_e is MemoryScope.EPISODE:
        # Episode evidence attaches to entity if provided, else organ ledger
        if entity_id or entity_query:
            eid = entity_id or store.resolve(entity_query or "")["entity_id"]
            claim = store.write_claim(
                eid,
                text,
                provenance,
                topic=topic,
                status=status,
                scope=MemoryScope.EPISODE,
            )
            receipt.update({"entity_id": eid, "claim": claim})
            return receipt
        obj = {
            "scope": scope_e.value,
            "text": text,
            "topic": topic,
            "status": status,
            "provenance": provenance.to_dict(),
        }
        path = proteus_home() / "memory" / "episodes" / "claims.jsonl"
        _append_jsonl(path, obj)
        receipt["destination"] = str(path)
        receipt["claim"] = obj
        return receipt

    raise ValueError(f"Unhandled scope: {scope_e}")


def route_project_decision(
    project_path: str,
    text: str,
    provenance: Provenance,
    *,
    topic: str | None = None,
) -> dict[str, Any]:
    """Append a project-scoped decision; does not write to entity substrate."""
    root = Path(project_path)
    if not root.is_dir():
        raise FileNotFoundError(f"Project path missing: {project_path}")
    decisions = root / "state" / "DECISIONS.md"
    decisions.parent.mkdir(parents=True, exist_ok=True)
    if not decisions.exists():
        decisions.write_text("# DECISIONS\n\n", encoding="utf-8")
    stamp = provenance.observed_at
    block = (
        f"\n## Project decision ({stamp})\n"
        f"- {text}\n"
        f"- topic: {topic or '(none)'}\n"
        f"- provenance: {provenance.kind} / {provenance.observer}\n"
        f"- scope: PROJECT (not ENTITY)\n"
    )
    with decisions.open("a", encoding="utf-8") as f:
        f.write(block)
    # Also structured append for tests
    ledger = root / ".proteus" / "project_memory.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    obj = {
        "scope": MemoryScope.PROJECT.value,
        "text": text,
        "topic": topic,
        "provenance": provenance.to_dict(),
    }
    _append_jsonl(ledger, obj)
    return {
        "scope": MemoryScope.PROJECT.value,
        "destination": str(decisions),
        "structured": str(ledger),
        "claim": obj,
        "note": "Project-scoped; must not appear as global entity truth",
        "world_root": str(world_root()),
    }
