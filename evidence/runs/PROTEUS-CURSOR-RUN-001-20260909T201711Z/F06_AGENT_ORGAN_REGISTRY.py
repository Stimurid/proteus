#!/usr/bin/env python3
"""Validate Agentum AgentOrgan records and emit deterministic registry hygiene data."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "02_REGISTRIES" / "AGENT_ORGAN_REGISTRY.yaml"
DEFAULT_SCHEMA = ROOT / "registry_contracts" / "agent_organ_record.schema.json"
DEFAULT_DEFICITS = ROOT / "02_REGISTRIES" / "DEFICIT_REGISTRY.yaml"
DEFAULT_FAILURES = ROOT / "02_REGISTRIES" / "FAILURE_MODE_REGISTRY.yaml"
DEFAULT_REPORT = ROOT / "02_REGISTRIES" / "derived" / "agent_organ_registry_report.json"
CONTRACT_VERSION = "1.0.0"
ID_RE = re.compile(r"^(?:ORGAN|DEFICIT|FAILURE)-[0-9]{3,}$")
TRUST_RANK = {"theory_only": 0, "scene_tested": 1, "install_tested": 2, "field_validated": 3}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        value = yaml.safe_load(source)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping at document root")
    return value


def load_schema(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def known_ids(path: Path, collection: str) -> set[str]:
    records = load_yaml(path).get(collection, [])
    return {record["id"] for record in records if isinstance(record, dict) and isinstance(record.get("id"), str)}


def schema_errors(value: Any, rule: dict[str, Any], definitions: dict[str, Any], path: str = "root") -> list[str]:
    """Validate the JSON-Schema subset used by this checked-in contract.

    Keeping this small interpreter here avoids a second, undeclared validator runtime
    while making the schema—not a parallel Python field list—the shape authority.
    """
    if "$ref" in rule:
        reference = rule["$ref"]
        if not reference.startswith("#/$defs/"):
            return [f"schema {path}: unsupported reference {reference}"]
        return schema_errors(value, definitions[reference.rsplit("/", 1)[1]], definitions, path)
    errors: list[str] = []
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"schema {path}: {value!r} is not one of {rule['enum']}")
    expected = rule.get("type")
    type_matches = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
    }
    if expected and not type_matches.get(expected, False):
        return errors + [f"schema {path}: expected {expected}"]
    if isinstance(value, str):
        if len(value) < rule.get("minLength", 0):
            errors.append(f"schema {path}: string is shorter than {rule['minLength']}")
        if "pattern" in rule and not re.match(rule["pattern"], value):
            errors.append(f"schema {path}: {value!r} does not match {rule['pattern']}")
    if isinstance(value, list):
        if len(value) < rule.get("minItems", 0):
            errors.append(f"schema {path}: requires at least {rule['minItems']} item(s)")
        if "items" in rule:
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, rule["items"], definitions, f"{path}/{index}"))
    if isinstance(value, dict):
        properties = rule.get("properties", {})
        for required in rule.get("required", []):
            if required not in value:
                errors.append(f"schema {path}: missing required property {required}")
        if rule.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"schema {path}: unknown property {key}")
        for key, child_rule in properties.items():
            if key in value:
                errors.extend(schema_errors(value[key], child_rule, definitions, f"{path}/{key}"))
    return errors


def validate(data: dict[str, Any], schema: dict[str, Any], deficit_ids: set[str], failure_ids: set[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(schema_errors(data, schema, schema.get("$defs", {})))

    organs = data.get("organs", [])
    if not isinstance(organs, list):
        return errors, warnings
    organ_ids = [record.get("id") for record in organs if isinstance(record, dict)]
    duplicates = sorted({item for item, count in Counter(organ_ids).items() if isinstance(item, str) and count > 1})
    for organ_id in duplicates:
        errors.append(f"duplicate organ id: {organ_id}")

    known_organs = {item for item in organ_ids if isinstance(item, str)}
    for index, organ in enumerate(organs):
        if not isinstance(organ, dict):
            continue
        label = organ.get("id", f"organs[{index}]")
        for field, candidates, known, noun in (
            ("deficit_origin", organ.get("deficit_origin", []), deficit_ids, "deficit"),
            ("failure_modes", organ.get("failure_modes", []), failure_ids, "failure mode"),
            ("parent_organs", organ.get("parent_organs", []), known_organs, "parent organ"),
            ("child_organs", organ.get("child_organs", []), known_organs, "child organ"),
        ):
            if not isinstance(candidates, list):
                continue
            for candidate in candidates:
                if isinstance(candidate, str) and ID_RE.match(candidate) and candidate not in known:
                    errors.append(f"{label}: {field} references unknown {noun} {candidate}")
        status, trust = organ.get("status"), organ.get("trust_level")
        if status in {"selected", "active"} and trust not in {"scene_tested", "install_tested", "field_validated"}:
            errors.append(f"{label}: {status} requires at least scene_tested trust")
        if status == "active" and trust not in {"install_tested", "field_validated"}:
            errors.append(f"{label}: active requires install_tested or field_validated trust")
        if status == "quarantined" and organ.get("quarantine_status") == "none":
            errors.append(f"{label}: quarantined status requires bounded or strict quarantine_status")
        if trust == "legacy_only" and status not in {"retired", "quarantined"}:
            warnings.append(f"{label}: legacy_only trust is normally retired or quarantined")
        parents, children = organ.get("parent_organs", []), organ.get("child_organs", [])
        if isinstance(parents, list) and label in parents:
            errors.append(f"{label}: cannot be its own parent")
        if isinstance(children, list) and label in children:
            errors.append(f"{label}: cannot be its own child")
    return errors, warnings


def build_report(data: dict[str, Any], registry_path: Path, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    organs = data.get("organs", [])
    inventory = [
        {"id": organ["id"], "name": organ["name"], "status": organ["status"], "trust_level": organ["trust_level"], "quarantine_status": organ["quarantine_status"], "output_class": organ["output_class"]}
        for organ in organs if isinstance(organ, dict) and all(key in organ for key in ("id", "name", "status", "trust_level", "quarantine_status", "output_class"))
    ]
    source_hash = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    return {
        "contract": {"name": "Agentum AgentOrgan Record", "version": CONTRACT_VERSION, "schema": "registry_contracts/agent_organ_record.schema.json"},
        "source": {"path": "02_REGISTRIES/AGENT_ORGAN_REGISTRY.yaml", "sha256": source_hash},
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "organ_count": len(inventory),
            "by_status": dict(sorted(Counter(item["status"] for item in inventory).items())),
            "by_trust_level": dict(sorted(Counter(item["trust_level"] for item in inventory).items())),
            "by_status_and_trust": {
                status: dict(sorted(Counter(item["trust_level"] for item in inventory if item["status"] == status).items()))
                for status in sorted({item["status"] for item in inventory})
            },
        },
        "inventory": sorted(inventory, key=lambda item: item["id"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "report"):
        subparser = subcommands.add_parser(command)
        subparser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
        subparser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
        subparser.add_argument("--deficits", type=Path, default=DEFAULT_DEFICITS)
        subparser.add_argument("--failures", type=Path, default=DEFAULT_FAILURES)
        if command == "report":
            subparser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    try:
        data = load_yaml(args.registry)
        errors, warnings = validate(data, load_schema(args.schema), known_ids(args.deficits, "deficits"), known_ids(args.failures, "failures"))
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exception:
        print(f"agent-organ-registry: {exception}", file=sys.stderr)
        return 2
    if args.command == "report":
        report = build_report(data, args.registry, errors, warnings)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"report={args.output.relative_to(ROOT)}")
    else:
        print(f"organs={len(data.get('organs', []))}")
    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    print("agent_organ_registry=ok" if not errors else "agent_organ_registry=invalid")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
