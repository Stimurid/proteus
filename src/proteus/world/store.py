from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..paths import aiye_home, world_root
from .scopes import MemoryScope

SCHEMA = "proteus.entity.v0.1"
INDEX_SCHEMA = "proteus.world.index.v0.1"


class EntityNotFoundError(LookupError):
    pass


class EntityAmbiguousError(LookupError):
    def __init__(self, query: str, candidates: list[str]):
        self.query = query
        self.candidates = candidates
        super().__init__(f"Ambiguous entity resolution for {query!r}: {candidates}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", ".", text.strip().lower()).strip(".")
    return s or "unnamed"


def ensure_world_home() -> dict[str, Any]:
    """Create smallest configurable Aiye world root if missing; return layout note."""
    home = aiye_home()
    world = world_root()
    entities = world / "entities"
    index = world / "index"
    created = []
    for d in (home, world, entities, index):
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d))
    readme = home / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Aiye home\n\n"
            "Established by Proteus world-memory vertical slice because no prior "
            "`~/.aiye` / Archivarius object-home existed on this host.\n\n"
            "- Override with `AIYE_HOME`.\n"
            "- Entity substrate: `world/` (or `PROTEUS_WORLD_ROOT`).\n"
            "- ENTITY ≠ CARRIER; generated `world/index` is a rebuildable VIEW.\n",
            encoding="utf-8",
        )
        created.append(str(readme))
    cfg = world / "config.json"
    if not cfg.exists():
        cfg.write_text(
            json.dumps(
                {
                    "schema": SCHEMA,
                    "aiye_home": str(home),
                    "world_root": str(world),
                    "created_utc": utc_now(),
                    "why": (
                        "No existing Aiye/Archivarius local world root found; "
                        "smallest configurable home for entity substrate."
                    ),
                    "invariants": [
                        "ENTITY_NE_CARRIER",
                        "VIEW_NE_SOURCE_TRUTH",
                        "NO_LAST_WRITE_WINS",
                        "UNKNOWN_AND_CONFLICT_SURVIVE",
                        "MANIFEST_IS_ADDRESS_NOT_ONTOLOGY",
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        created.append(str(cfg))
    return {"aiye_home": str(home), "world_root": str(world), "created": created}


@dataclass
class Provenance:
    observer: str
    project: str | None = None
    run_id: str | None = None
    session: str | None = None
    observed_at: str = field(default_factory=utc_now)
    source: str | None = None
    kind: str = "observation"  # observation|user_assertion|inference|decision|imported_reference
    confidence: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class WorldStore:
    def __init__(self, root: Path | None = None):
        ensure_world_home()
        self.root = Path(root) if root else world_root()
        self.entities_dir = self.root / "entities"
        self.index_dir = self.root / "index"
        self.entities_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def entity_dir(self, entity_id: str) -> Path:
        return self.entities_dir / entity_id

    def list_entity_ids(self) -> list[str]:
        if not self.entities_dir.is_dir():
            return []
        return sorted(p.name for p in self.entities_dir.iterdir() if p.is_dir())

    def create_entity(
        self,
        display_name: str,
        *,
        entity_id: str | None = None,
        aliases: list[str] | None = None,
        relations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        eid = entity_id or f"entity.{_slug(display_name)}"
        path = self.entity_dir(eid)
        if path.exists():
            raise FileExistsError(f"Entity already exists: {eid}")
        path.mkdir(parents=True)
        identity = {
            "schema": SCHEMA,
            "entity_id": eid,
            "display_name": display_name,
            "aliases": list(aliases or []),
            "relations": list(relations or []),
            "created_utc": utc_now(),
            "note": "identity card is address/catalog, not ontology of the living object",
        }
        carriers = {
            "schema": SCHEMA,
            "entity_id": eid,
            "carriers": [
                {
                    "role": "HOME",
                    "kind": "local_fs",
                    "path": str(path),
                    "authority": "local_semantic",
                    "currentness": "active",
                }
            ],
        }
        (path / "identity.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
        (path / "carriers.json").write_text(json.dumps(carriers, indent=2) + "\n", encoding="utf-8")
        (path / "claims.jsonl").write_text("", encoding="utf-8")
        (path / "projects.json").write_text(
            json.dumps({"schema": SCHEMA, "entity_id": eid, "projects": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        (path / "secret_refs.json").write_text(
            json.dumps({"schema": SCHEMA, "entity_id": eid, "secret_refs": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        (path / "unresolved.md").write_text(
            f"# Unresolved — {display_name}\n\n"
            "UNKNOWN and CONFLICT survive here. Do not collapse by last-write-wins.\n",
            encoding="utf-8",
        )
        (path / "ENTITY.md").write_text(
            f"# {display_name}\n\n"
            f"- entity_id: `{eid}`\n"
            f"- aliases: {', '.join(aliases or []) or '(none)'}\n\n"
            "## Current facts\n\n"
            "_No durable entity facts yet._\n\n"
            "## Notes\n\n"
            "Rich prose may live here; structured claims live in `claims.jsonl`.\n",
            encoding="utf-8",
        )
        self.rebuild_index()
        return identity

    def add_aliases(self, entity_id: str, aliases: list[str]) -> dict[str, Any]:
        ident = self._load_identity(entity_id)
        existing = list(ident.get("aliases") or [])
        for a in aliases:
            a = a.strip()
            if a and a not in existing and a.lower() != str(ident.get("display_name", "")).lower():
                existing.append(a)
        ident["aliases"] = existing
        ident["aliases_updated_utc"] = utc_now()
        path = self.entity_dir(entity_id) / "identity.json"
        path.write_text(json.dumps(ident, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        # keep ENTITY.md alias line loosely in sync
        md_path = self.entity_dir(entity_id) / "ENTITY.md"
        if md_path.is_file():
            body = md_path.read_text(encoding="utf-8")
            lines = body.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("- aliases:"):
                    lines[i] = f"- aliases: {', '.join(existing) or '(none)'}"
                    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    break
        self.rebuild_index()
        return ident

    def append_unresolved(self, entity_id: str, line: str) -> None:
        self._append_unresolved(entity_id, line)

    def _load_identity(self, entity_id: str) -> dict[str, Any]:
        path = self.entity_dir(entity_id) / "identity.json"
        if not path.is_file():
            raise EntityNotFoundError(entity_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def resolve(self, query: str) -> dict[str, Any]:
        q = query.strip()
        if not q:
            raise EntityNotFoundError("(empty)")
        ids = self.list_entity_ids()
        if q in ids:
            return self.mount(q)
        matches: list[str] = []
        ql = q.lower()
        for eid in ids:
            ident = self._load_identity(eid)
            names = [ident.get("display_name", ""), eid, *ident.get("aliases", [])]
            if any(ql == str(n).lower() for n in names if n):
                matches.append(eid)
            elif any(ql in str(n).lower() for n in names if n):
                matches.append(eid)
        # unique preserve order
        seen: set[str] = set()
        uniq = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                uniq.append(m)
        if not uniq:
            raise EntityNotFoundError(q)
        if len(uniq) > 1:
            # exact alias preferred over substring
            exact = []
            for eid in uniq:
                ident = self._load_identity(eid)
                names = [ident.get("display_name", ""), eid, *ident.get("aliases", [])]
                if any(ql == str(n).lower() for n in names if n):
                    exact.append(eid)
            if len(exact) == 1:
                return self.mount(exact[0])
            if len(exact) > 1:
                raise EntityAmbiguousError(q, exact)
            raise EntityAmbiguousError(q, uniq)
        return self.mount(uniq[0])

    def mount(self, entity_id: str) -> dict[str, Any]:
        path = self.entity_dir(entity_id)
        if not path.is_dir():
            raise EntityNotFoundError(entity_id)
        identity = self._load_identity(entity_id)
        carriers = json.loads((path / "carriers.json").read_text(encoding="utf-8"))
        projects = json.loads((path / "projects.json").read_text(encoding="utf-8"))
        secrets = json.loads((path / "secret_refs.json").read_text(encoding="utf-8"))
        claims = self.list_claims(entity_id)
        unresolved = (path / "unresolved.md").read_text(encoding="utf-8")
        entity_md = (path / "ENTITY.md").read_text(encoding="utf-8")
        return {
            "schema": SCHEMA,
            "entity_id": entity_id,
            "identity": identity,
            "carriers": carriers,
            "projects": projects,
            "secret_refs": secrets,
            "claims": claims,
            "current_claims": [c for c in claims if c.get("status") == "current"],
            "conflicts": [c for c in claims if c.get("status") == "conflict"],
            "unknowns": [c for c in claims if c.get("status") == "unknown"],
            "unresolved_md": unresolved,
            "entity_md": entity_md,
            "local_path": str(path),
            "note": "VIEW/index separate; this mount reads carrier source truth",
        }

    def list_claims(self, entity_id: str) -> list[dict[str, Any]]:
        path = self.entity_dir(entity_id) / "claims.jsonl"
        if not path.is_file():
            return []
        out = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

    def link_project(self, entity_id: str, project_path: str, relation: str = "uses") -> dict[str, Any]:
        path = self.entity_dir(entity_id) / "projects.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        entry = {
            "project_path": str(Path(project_path).resolve()),
            "relation": relation,
            "linked_utc": utc_now(),
        }
        existing = [p for p in data.get("projects", []) if p.get("project_path") == entry["project_path"]]
        if not existing:
            data.setdefault("projects", []).append(entry)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return data

    def add_secret_ref(
        self,
        entity_id: str,
        secret_uri: str,
        *,
        label: str,
        auth_method: str | None = None,
        scope: str | None = None,
    ) -> dict[str, Any]:
        if secret_uri.startswith("secret://") is False:
            raise ValueError("secret_ref must use secret:// URI; plaintext secrets forbidden")
        path = self.entity_dir(entity_id) / "secret_refs.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for existing in data.get("secret_refs", []):
            if existing.get("secret_uri") == secret_uri:
                # update metadata only; never store plaintext
                existing["label"] = label
                if auth_method is not None:
                    existing["auth_method"] = auth_method
                if scope is not None:
                    existing["scope"] = scope
                existing["plaintext"] = None
                existing["updated_utc"] = utc_now()
                path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                return existing
        ref = {
            "secret_uri": secret_uri,
            "label": label,
            "auth_method": auth_method,
            "scope": scope,
            "recorded_utc": utc_now(),
            "plaintext": None,
            "note": "semantic reference only; Secret Broker resolves capability",
        }
        data.setdefault("secret_refs", []).append(ref)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return ref

    def add_carrier(self, entity_id: str, carrier: dict[str, Any]) -> dict[str, Any]:
        path = self.entity_dir(entity_id) / "carriers.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        carriers = data.setdefault("carriers", [])
        pid = carrier.get("provider_id")
        if pid:
            for existing in carriers:
                if existing.get("provider_id") == pid and existing.get("kind") == carrier.get("kind"):
                    existing.update(carrier)
                    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                    return data
        carriers.append(carrier)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return data

    def write_claim(
        self,
        entity_id: str,
        text: str,
        provenance: Provenance,
        *,
        topic: str | None = None,
        status: str = "current",
        conflicts_with: list[str] | None = None,
        scope: MemoryScope = MemoryScope.ENTITY,
        cross_host_critical: bool = False,
        drive_export_target: str | None = None,
    ) -> dict[str, Any]:
        if scope not in (MemoryScope.ENTITY, MemoryScope.EPISODE, MemoryScope.SECRET_REFERENCE):
            raise ValueError(
                f"Entity substrate accepts ENTITY/EPISODE/SECRET_REFERENCE claims; got {scope}"
            )
        if status not in ("current", "conflict", "unknown", "superseded", "historical"):
            raise ValueError(f"Invalid claim status: {status}")
        claims_path = self.entity_dir(entity_id) / "claims.jsonl"
        existing = self.list_claims(entity_id)
        # Idempotent re-write: identical topic+text+status already present → return existing
        if topic is not None:
            for old in existing:
                if (
                    old.get("topic") == topic
                    and old.get("text") == text
                    and old.get("status") == status
                ):
                    return {**old, "idempotent_reread": True}
        claim_id = f"claim.{uuid.uuid4().hex[:12]}"
        conflict_ids: list[str] = list(conflicts_with or [])

        # No last-write-wins: same topic with differing current text → CONFLICT both
        if topic and status == "current":
            for old in existing:
                if (
                    old.get("topic") == topic
                    and old.get("status") == "current"
                    and old.get("text") != text
                ):
                    conflict_ids.append(old["claim_id"])
                    self._rewrite_claim_status(entity_id, old["claim_id"], "conflict")
                    status = "conflict"
                    self._append_unresolved(
                        entity_id,
                        f"CONFLICT on topic `{topic}`: existing `{old['claim_id']}` vs new `{claim_id}`",
                    )

        claim = {
            "claim_id": claim_id,
            "entity_id": entity_id,
            "scope": scope.value,
            "topic": topic,
            "text": text,
            "status": status,
            "conflicts_with": conflict_ids,
            "provenance": provenance.to_dict(),
            "recorded_utc": utc_now(),
        }
        if cross_host_critical:
            claim["cross_host_critical"] = True
            if drive_export_target:
                claim["drive_export_target"] = drive_export_target
        with claims_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(claim, ensure_ascii=False) + "\n")

        if status == "current":
            self._append_entity_md_fact(entity_id, text, claim_id, provenance)
        elif status == "unknown":
            self._append_unresolved(entity_id, f"UNKNOWN: {text} ({claim_id})")
        return claim

    def _rewrite_claim_status(self, entity_id: str, claim_id: str, status: str) -> None:
        path = self.entity_dir(entity_id) / "claims.jsonl"
        lines = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("claim_id") == claim_id:
                obj["status"] = status
                obj["status_changed_utc"] = utc_now()
            lines.append(json.dumps(obj, ensure_ascii=False))
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    def _append_unresolved(self, entity_id: str, line: str) -> None:
        path = self.entity_dir(entity_id) / "unresolved.md"
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n- {utc_now()}: {line}\n")

    def _append_entity_md_fact(
        self, entity_id: str, text: str, claim_id: str, provenance: Provenance
    ) -> None:
        path = self.entity_dir(entity_id) / "ENTITY.md"
        body = path.read_text(encoding="utf-8")
        marker = "## Current facts\n"
        entry = (
            f"\n- {text}  \n"
            f"  - claim_id: `{claim_id}`  \n"
            f"  - provenance: {provenance.kind} / {provenance.observer}"
            f"{(' / ' + provenance.source) if provenance.source else ''}  \n"
        )
        if "_No durable entity facts yet._" in body:
            body = body.replace("_No durable entity facts yet._\n", entry)
        elif marker in body:
            body = body.replace(marker, marker + entry, 1)
        else:
            body += "\n## Current facts\n" + entry
        path.write_text(body, encoding="utf-8")

    def rebuild_index(self) -> dict[str, Any]:
        by_alias: dict[str, str] = {}
        entities: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        for eid in self.list_entity_ids():
            ident = self._load_identity(eid)
            entities.append(
                {
                    "entity_id": eid,
                    "display_name": ident.get("display_name"),
                    "aliases": ident.get("aliases", []),
                }
            )
            for name in [eid, ident.get("display_name"), *ident.get("aliases", [])]:
                if name:
                    key = str(name).lower()
                    # index is VIEW; collisions recorded, not silently overwritten as identity
                    if key in by_alias and by_alias[key] != eid:
                        conflicts.append({"alias": key, "entities": [by_alias[key], eid]})
                    else:
                        by_alias[key] = eid
        payload = {
            "schema": INDEX_SCHEMA,
            "rebuilt_utc": utc_now(),
            "view_note": "rebuildable VIEW; not source truth",
            "entities": entities,
            "by_alias": by_alias,
            "alias_collisions": conflicts,
        }
        (self.index_dir / "entities.json").write_text(
            json.dumps({"schema": INDEX_SCHEMA, "entities": entities, "rebuilt_utc": payload["rebuilt_utc"]}, indent=2)
            + "\n",
            encoding="utf-8",
        )
        (self.index_dir / "by_alias.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
        (self.index_dir / "INDEX_RECEIPT.json").write_text(
            json.dumps(
                {
                    "schema": INDEX_SCHEMA,
                    "rebuilt_utc": payload["rebuilt_utc"],
                    "entity_count": len(entities),
                    "digest16": digest,
                    "view_ne_source_truth": True,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return payload
