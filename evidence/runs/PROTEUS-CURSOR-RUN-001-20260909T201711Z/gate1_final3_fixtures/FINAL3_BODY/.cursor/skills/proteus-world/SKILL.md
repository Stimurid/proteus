---
name: proteus-world
description: Resolve or mount a shared world entity and route durable knowledge by memory scope.
---

# Shared world memory

Use when a fact concerns a **trans-project entity** (router, university, person, service, device) rather than only this project's decisions.

## Resolve / mount

```
python -m proteus world resolve "<name|alias|id>"
python -m proteus world mount "<name|alias|id>"
```

Mount returns identity, carriers, current claims, conflicts/UNKNOWN, secret refs (no plaintext), and project links.

## Route new durable knowledge

Scopes: `SELF` | `ORGAN` | `PROJECT` | `ENTITY` | `EPISODE` | `SECRET_REFERENCE`

```
python -m proteus world route --scope ENTITY --entity "<name>" --text "<fact>" --project .
python -m proteus world route --scope PROJECT --project . --text "<project-only decision>"
```

Do not store plaintext secrets. Use `--scope SECRET_REFERENCE --secret-uri secret://...`.

ENTITY ≠ CARRIER. Generated indexes are rebuildable VIEWs. UNKNOWN and CONFLICT survive; no last-write-wins.
